# -*- coding: utf-8 -*-
"""
    flask.app
    ~~~~~~~~~

    本模块部署了中心 WSGI 网络应用对象。

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys
import warnings
from datetime import timedelta
from functools import update_wrapper
from itertools import chain
from threading import Lock

from werkzeug.datastructures import Headers, ImmutableDict
from werkzeug.exceptions import BadRequest, BadRequestKeyError, HTTPException, \
    InternalServerError, MethodNotAllowed, default_exceptions
from werkzeug.routing import BuildError, Map, RequestRedirect, \
    RoutingException, Rule

from . import cli, json
from ._compat import integer_types, reraise, string_types, text_type
from .config import Config, ConfigAttribute
from .ctx import AppContext, RequestContext, _AppCtxGlobals
from .globals import _request_ctx_stack, g, request, session
from .helpers import (
    _PackageBoundObject,
    _endpoint_from_view_func, find_package, get_env, get_debug_flag,
    get_flashed_messages, locked_cached_property, url_for, get_load_dotenv
)
from .logging import create_logger
from .sessions import SecureCookieSessionInterface
from .signals import appcontext_tearing_down, got_request_exception, \
    request_finished, request_started, request_tearing_down
from .templating import DispatchingJinjaLoader, Environment, \
    _default_template_ctx_processor
from .wrappers import Request, Response

# a singleton sentinel value for parameter defaults
_sentinel = object()


def _make_timedelta(value):
    if not isinstance(value, timedelta):
        return timedelta(seconds=value)
    return value


def setupmethod(f):
    """打包一个方法，这样如果第一个请求已经处理完的话，
    该方法依然可以在调试模式中执行一项检查操作。
    """
    def wrapper_func(self, *args, **kwargs):
        if self.debug and self._got_first_request:
            raise AssertionError('A setup function was called after the '
                'first request was handled.  This usually indicates a bug '
                'in the application where a module was not imported '
                'and decorators or other functionality was called too late.\n'
                'To fix this make sure to import all your view modules, '
                'database models and everything related at a central place '
                'before the application starts serving requests.')
        return f(self, *args, **kwargs)
    return update_wrapper(wrapper_func, f)


class Flask(_PackageBoundObject):
    """本类实例对象就是部署了一个 WSGI 网络应用，
    并且扮演了中心对象。本类要由模块名或网络应用包来导入。
    一旦本类实例建立完，本类实例会扮演一个中心注册，为视图函数、
    URL 规则、模版配置，以及更多对象提供注册接口。

    包名就是用来解决来自包内的资源，或文件夹里的资源问题，
    包含在其中的模块依据包参数是否解决一个实际 python 包问题
    （一个含有 :file:`__init__.py` 文件的目录），
    或者是否解决一个标准模块（就如一个 ``.py`` 文件一样）。

    对于更多关于资源加载问题，查看 :func:`open_resource` 函数。

    常常你建立一个 :class:`Flask` 类实例是在你的主模块中，
    或者在包的 :file:`__init__.py` 文件里，就像下面一样::

        from flask import Flask
        app = Flask(__name__)

    .. admonition:: 关于第一个参数

        第一个参数的想法是要让 Flask 知道你的网络应用属于谁。
        Flask 有了这个思想后，这个名字就是用来找到文件系统上的资源的关键点。
        这个名字也可以让 Flask 扩展件使用，从而改善调试信息和更多地方。

        所以第一参数使用的是什么是很重要的一件事。
        如果你正在使用一个模块来建立本类的实例的话，
        第一个参数要一直是 `__name__` 值才是正确的。
        不管如何做到的，如果你正在使用一个包的话，
        常常推荐使用硬编码你的包名来。

        例如，如果你的网络应用定义在
        :file:`yourapplication/app.py` 文件里的话，
        你建立时应该有如下两个版本之一::

            app = Flask('yourapplication')
            app = Flask(__name__.split('.')[0])

        为什么要这样定义？即便只使用 `__name__` 网络应用也能工作，
        感谢资源是如何进行查询的。不管如何做到的，单用一个 dunder name
        会让调试更痛苦。某些 Flask 扩展件可以根据你的网络应用导入名做出
        许多假设。例如， Flask-SQLAlchemy 扩展件会在调试模式中
        查询你网络应用代码触发的一句 SQL 查询语句。
        如果导入名没有设置正确的话，会丢失调试信息。
        （例如，只会找到 `yourapplication.app` 中的 SQL 查询信息，
        但找不到 `yourapplication.views.frontend` 信息。)

    .. versionadded:: 0.7
       增加 `static_url_path`、 `static_folder` 和 `template_folder`
       这3个参数。

    .. versionadded:: 0.8
       增加 `instance_path` 和 `instance_relative_config` 
       这2个参数。

    .. versionadded:: 0.11
       增加 `root_path` 这1个参数。

    .. versionadded:: 1.0
       增加 ``host_matching`` 和 ``static_host`` 这2个参数。

    .. versionadded:: 1.0
       增加 ``subdomain_matching`` 这1个参数。
       此版本中子域名匹配需要手动开启。设置
       :data:`SERVER_NAME` 配置项不隐含开启子域名匹配功能。

    :param import_name: 网络应用包的名字
    :param static_url_path: 可以用来为网络上的静态文件描述一个不同的路径。
                            默认指向 `static_folder` 文件夹的名字。
    :param static_folder: 含有静态文件的文件夹应该由 `static_url_path`
                          参数值提供。默认指向网络应用根路径里的
                           ``'static'`` 文件夹。
    :param static_host: 当增加静态路由时使用的主机。默认值是 `None`。
                        当使用 ``host_matching=True`` 时需要用
                         ``static_folder`` 来配置参数值。
    :param host_matching: 设置 ``url_map.host_matching`` 属性。
                          默认参数值是 `False`。
    :param subdomain_matching: 当匹配路由时考虑与 :data:`SERVER_NAME`
                               相关的子域名。默认参数值是 `False`。
    :param template_folder: 含有模版的文件夹应该由网络应用使用。
                            默认值是网络应用根路径里的 ``'templates'`` 文件夹。
    :param instance_path: 对网络应用来说实例路径的一种可选方案。
                          默认值是包或模块同级路径里的 ``'instance'`` 文件夹，
                          假设为实例路径。
    :param instance_relative_config: 如果设置成 ``True`` 值的话，加载配置时
                                     相关文件都假设为实例路径里的文件，
                                     而不是网络应用根路径中的文件。
    :param root_path: Flask 默认会自动计算网络应用根路径。
                      在某些情况下无法实现（如果包是一种 Python 3 命名空间包的话，
                      就无法实现自动计算网络应用根路径），并且需要手动定义根路径。
    """

    #: The class that is used for request objects.  See :class:`~flask.Request`
    #: for more information.
    request_class = Request

    #: The class that is used for response objects.  See
    #: :class:`~flask.Response` for more information.
    response_class = Response

    #: The class that is used for the Jinja environment.
    #:
    #: .. versionadded:: 0.11
    jinja_environment = Environment

    #: The class that is used for the :data:`~flask.g` instance.
    #:
    #: Example use cases for a custom class:
    #:
    #: 1. Store arbitrary attributes on flask.g.
    #: 2. Add a property for lazy per-request database connectors.
    #: 3. Return None instead of AttributeError on unexpected attributes.
    #: 4. Raise exception if an unexpected attr is set, a "controlled" flask.g.
    #:
    #: In Flask 0.9 this property was called `request_globals_class` but it
    #: was changed in 0.10 to :attr:`app_ctx_globals_class` because the
    #: flask.g object is now application context scoped.
    #:
    #: .. versionadded:: 0.10
    app_ctx_globals_class = _AppCtxGlobals

    #: The class that is used for the ``config`` attribute of this app.
    #: Defaults to :class:`~flask.Config`.
    #:
    #: Example use cases for a custom class:
    #:
    #: 1. Default values for certain config options.
    #: 2. Access to config values through attributes in addition to keys.
    #:
    #: .. versionadded:: 0.11
    config_class = Config

    #: The testing flag.  Set this to ``True`` to enable the test mode of
    #: Flask extensions (and in the future probably also Flask itself).
    #: For example this might activate test helpers that have an
    #: additional runtime cost which should not be enabled by default.
    #:
    #: If this is enabled and PROPAGATE_EXCEPTIONS is not changed from the
    #: default it's implicitly enabled.
    #:
    #: This attribute can also be configured from the config with the
    #: ``TESTING`` configuration key.  Defaults to ``False``.
    testing = ConfigAttribute('TESTING')

    #: If a secret key is set, cryptographic components can use this to
    #: sign cookies and other things. Set this to a complex random value
    #: when you want to use the secure cookie for instance.
    #:
    #: This attribute can also be configured from the config with the
    #: :data:`SECRET_KEY` configuration key. Defaults to ``None``.
    secret_key = ConfigAttribute('SECRET_KEY')

    #: The secure cookie uses this for the name of the session cookie.
    #:
    #: This attribute can also be configured from the config with the
    #: ``SESSION_COOKIE_NAME`` configuration key.  Defaults to ``'session'``
    session_cookie_name = ConfigAttribute('SESSION_COOKIE_NAME')

    #: A :class:`~datetime.timedelta` which is used to set the expiration
    #: date of a permanent session.  The default is 31 days which makes a
    #: permanent session survive for roughly one month.
    #:
    #: This attribute can also be configured from the config with the
    #: ``PERMANENT_SESSION_LIFETIME`` configuration key.  Defaults to
    #: ``timedelta(days=31)``
    permanent_session_lifetime = ConfigAttribute('PERMANENT_SESSION_LIFETIME',
        get_converter=_make_timedelta)

    #: A :class:`~datetime.timedelta` which is used as default cache_timeout
    #: for the :func:`send_file` functions. The default is 12 hours.
    #:
    #: This attribute can also be configured from the config with the
    #: ``SEND_FILE_MAX_AGE_DEFAULT`` configuration key. This configuration
    #: variable can also be set with an integer value used as seconds.
    #: Defaults to ``timedelta(hours=12)``
    send_file_max_age_default = ConfigAttribute('SEND_FILE_MAX_AGE_DEFAULT',
        get_converter=_make_timedelta)

    #: Enable this if you want to use the X-Sendfile feature.  Keep in
    #: mind that the server has to support this.  This only affects files
    #: sent with the :func:`send_file` method.
    #:
    #: .. versionadded:: 0.2
    #:
    #: This attribute can also be configured from the config with the
    #: ``USE_X_SENDFILE`` configuration key.  Defaults to ``False``.
    use_x_sendfile = ConfigAttribute('USE_X_SENDFILE')

    #: The JSON encoder class to use.  Defaults to :class:`~flask.json.JSONEncoder`.
    #:
    #: .. versionadded:: 0.10
    json_encoder = json.JSONEncoder

    #: The JSON decoder class to use.  Defaults to :class:`~flask.json.JSONDecoder`.
    #:
    #: .. versionadded:: 0.10
    json_decoder = json.JSONDecoder

    #: Options that are passed directly to the Jinja2 environment.
    jinja_options = ImmutableDict(
        extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_']
    )

    #: Default configuration parameters.
    default_config = ImmutableDict({
        'ENV':                                  None,
        'DEBUG':                                None,
        'TESTING':                              False,
        'PROPAGATE_EXCEPTIONS':                 None,
        'PRESERVE_CONTEXT_ON_EXCEPTION':        None,
        'SECRET_KEY':                           None,
        'PERMANENT_SESSION_LIFETIME':           timedelta(days=31),
        'USE_X_SENDFILE':                       False,
        'SERVER_NAME':                          None,
        'APPLICATION_ROOT':                     '/',
        'SESSION_COOKIE_NAME':                  'session',
        'SESSION_COOKIE_DOMAIN':                None,
        'SESSION_COOKIE_PATH':                  None,
        'SESSION_COOKIE_HTTPONLY':              True,
        'SESSION_COOKIE_SECURE':                False,
        'SESSION_COOKIE_SAMESITE':              None,
        'SESSION_REFRESH_EACH_REQUEST':         True,
        'MAX_CONTENT_LENGTH':                   None,
        'SEND_FILE_MAX_AGE_DEFAULT':            timedelta(hours=12),
        'TRAP_BAD_REQUEST_ERRORS':              None,
        'TRAP_HTTP_EXCEPTIONS':                 False,
        'EXPLAIN_TEMPLATE_LOADING':             False,
        'PREFERRED_URL_SCHEME':                 'http',
        'JSON_AS_ASCII':                        True,
        'JSON_SORT_KEYS':                       True,
        'JSONIFY_PRETTYPRINT_REGULAR':          False,
        'JSONIFY_MIMETYPE':                     'application/json',
        'TEMPLATES_AUTO_RELOAD':                None,
        'MAX_COOKIE_SIZE': 4093,
    })

    #: The rule object to use for URL rules created.  This is used by
    #: :meth:`add_url_rule`.  Defaults to :class:`werkzeug.routing.Rule`.
    #:
    #: .. versionadded:: 0.7
    url_rule_class = Rule

    #: the test client that is used with when `test_client` is used.
    #:
    #: .. versionadded:: 0.7
    test_client_class = None

    #: The :class:`~click.testing.CliRunner` subclass, by default
    #: :class:`~flask.testing.FlaskCliRunner` that is used by
    #: :meth:`test_cli_runner`. Its ``__init__`` method should take a
    #: Flask app object as the first argument.
    #:
    #: .. versionadded:: 1.0
    test_cli_runner_class = None

    #: the session interface to use.  By default an instance of
    #: :class:`~flask.sessions.SecureCookieSessionInterface` is used here.
    #:
    #: .. versionadded:: 0.8
    session_interface = SecureCookieSessionInterface()

    # TODO remove the next three attrs when Sphinx :inherited-members: works
    # https://github.com/sphinx-doc/sphinx/issues/741

    #: The name of the package or module that this app belongs to. Do not
    #: change this once it is set by the constructor.
    import_name = None

    #: Location of the template files to be added to the template lookup.
    #: ``None`` if templates should not be added.
    template_folder = None

    #: Absolute path to the package on the filesystem. Used to look up
    #: resources contained in the package.
    root_path = None

    def __init__(
        self,
        import_name,
        static_url_path=None,
        static_folder='static',
        static_host=None,
        host_matching=False,
        subdomain_matching=False,
        template_folder='templates',
        instance_path=None,
        instance_relative_config=False,
        root_path=None
    ):
        _PackageBoundObject.__init__(
            self,
            import_name,
            template_folder=template_folder,
            root_path=root_path
        )

        if static_url_path is not None:
            self.static_url_path = static_url_path

        if static_folder is not None:
            self.static_folder = static_folder

        if instance_path is None:
            instance_path = self.auto_find_instance_path()
        elif not os.path.isabs(instance_path):
            raise ValueError(
                'If an instance path is provided it must be absolute.'
                ' A relative path was given instead.'
            )

        #: Holds the path to the instance folder.
        #:
        #: .. versionadded:: 0.8
        self.instance_path = instance_path

        #: The configuration dictionary as :class:`Config`.  This behaves
        #: exactly like a regular dictionary but supports additional methods
        #: to load a config from files.
        self.config = self.make_config(instance_relative_config)

        #: A dictionary of all view functions registered.  The keys will
        #: be function names which are also used to generate URLs and
        #: the values are the function objects themselves.
        #: To register a view function, use the :meth:`route` decorator.
        self.view_functions = {}

        #: A dictionary of all registered error handlers.  The key is ``None``
        #: for error handlers active on the application, otherwise the key is
        #: the name of the blueprint.  Each key points to another dictionary
        #: where the key is the status code of the http exception.  The
        #: special key ``None`` points to a list of tuples where the first item
        #: is the class for the instance check and the second the error handler
        #: function.
        #:
        #: To register an error handler, use the :meth:`errorhandler`
        #: decorator.
        self.error_handler_spec = {}

        #: A list of functions that are called when :meth:`url_for` raises a
        #: :exc:`~werkzeug.routing.BuildError`.  Each function registered here
        #: is called with `error`, `endpoint` and `values`.  If a function
        #: returns ``None`` or raises a :exc:`BuildError` the next function is
        #: tried.
        #:
        #: .. versionadded:: 0.9
        self.url_build_error_handlers = []

        #: A dictionary with lists of functions that will be called at the
        #: beginning of each request. The key of the dictionary is the name of
        #: the blueprint this function is active for, or ``None`` for all
        #: requests. To register a function, use the :meth:`before_request`
        #: decorator.
        self.before_request_funcs = {}

        #: A list of functions that will be called at the beginning of the
        #: first request to this instance. To register a function, use the
        #: :meth:`before_first_request` decorator.
        #:
        #: .. versionadded:: 0.8
        self.before_first_request_funcs = []

        #: A dictionary with lists of functions that should be called after
        #: each request.  The key of the dictionary is the name of the blueprint
        #: this function is active for, ``None`` for all requests.  This can for
        #: example be used to close database connections. To register a function
        #: here, use the :meth:`after_request` decorator.
        self.after_request_funcs = {}

        #: A dictionary with lists of functions that are called after
        #: each request, even if an exception has occurred. The key of the
        #: dictionary is the name of the blueprint this function is active for,
        #: ``None`` for all requests. These functions are not allowed to modify
        #: the request, and their return values are ignored. If an exception
        #: occurred while processing the request, it gets passed to each
        #: teardown_request function. To register a function here, use the
        #: :meth:`teardown_request` decorator.
        #:
        #: .. versionadded:: 0.7
        self.teardown_request_funcs = {}

        #: A list of functions that are called when the application context
        #: is destroyed.  Since the application context is also torn down
        #: if the request ends this is the place to store code that disconnects
        #: from databases.
        #:
        #: .. versionadded:: 0.9
        self.teardown_appcontext_funcs = []

        #: A dictionary with lists of functions that are called before the
        #: :attr:`before_request_funcs` functions. The key of the dictionary is
        #: the name of the blueprint this function is active for, or ``None``
        #: for all requests. To register a function, use
        #: :meth:`url_value_preprocessor`.
        #:
        #: .. versionadded:: 0.7
        self.url_value_preprocessors = {}

        #: A dictionary with lists of functions that can be used as URL value
        #: preprocessors.  The key ``None`` here is used for application wide
        #: callbacks, otherwise the key is the name of the blueprint.
        #: Each of these functions has the chance to modify the dictionary
        #: of URL values before they are used as the keyword arguments of the
        #: view function.  For each function registered this one should also
        #: provide a :meth:`url_defaults` function that adds the parameters
        #: automatically again that were removed that way.
        #:
        #: .. versionadded:: 0.7
        self.url_default_functions = {}

        #: A dictionary with list of functions that are called without argument
        #: to populate the template context.  The key of the dictionary is the
        #: name of the blueprint this function is active for, ``None`` for all
        #: requests.  Each returns a dictionary that the template context is
        #: updated with.  To register a function here, use the
        #: :meth:`context_processor` decorator.
        self.template_context_processors = {
            None: [_default_template_ctx_processor]
        }

        #: A list of shell context processor functions that should be run
        #: when a shell context is created.
        #:
        #: .. versionadded:: 0.11
        self.shell_context_processors = []

        #: all the attached blueprints in a dictionary by name.  Blueprints
        #: can be attached multiple times so this dictionary does not tell
        #: you how often they got attached.
        #:
        #: .. versionadded:: 0.7
        self.blueprints = {}
        self._blueprint_order = []

        #: a place where extensions can store application specific state.  For
        #: example this is where an extension could store database engines and
        #: similar things.  For backwards compatibility extensions should register
        #: themselves like this::
        #:
        #:      if not hasattr(app, 'extensions'):
        #:          app.extensions = {}
        #:      app.extensions['extensionname'] = SomeObject()
        #:
        #: The key must match the name of the extension module. For example in
        #: case of a "Flask-Foo" extension in `flask_foo`, the key would be
        #: ``'foo'``.
        #:
        #: .. versionadded:: 0.7
        self.extensions = {}

        #: The :class:`~werkzeug.routing.Map` for this instance.  You can use
        #: this to change the routing converters after the class was created
        #: but before any routes are connected.  Example::
        #:
        #:    from werkzeug.routing import BaseConverter
        #:
        #:    class ListConverter(BaseConverter):
        #:        def to_python(self, value):
        #:            return value.split(',')
        #:        def to_url(self, values):
        #:            return ','.join(super(ListConverter, self).to_url(value)
        #:                            for value in values)
        #:
        #:    app = Flask(__name__)
        #:    app.url_map.converters['list'] = ListConverter
        self.url_map = Map()

        self.url_map.host_matching = host_matching
        self.subdomain_matching = subdomain_matching

        # tracks internally if the application already handled at least one
        # request.
        self._got_first_request = False
        self._before_request_lock = Lock()

        # Add a static route using the provided static_url_path, static_host,
        # and static_folder if there is a configured static_folder.
        # Note we do this without checking if static_folder exists.
        # For one, it might be created while the server is running (e.g. during
        # development). Also, Google App Engine stores static files somewhere
        if self.has_static_folder:
            assert bool(static_host) == host_matching, 'Invalid static_host/host_matching combination'
            self.add_url_rule(
                self.static_url_path + '/<path:filename>',
                endpoint='static',
                host=static_host,
                view_func=self.send_static_file
            )

        #: The click command line context for this application.  Commands
        #: registered here show up in the :command:`flask` command once the
        #: application has been discovered.  The default commands are
        #: provided by Flask itself and can be overridden.
        #:
        #: This is an instance of a :class:`click.Group` object.
        self.cli = cli.AppGroup(self.name)

    @locked_cached_property
    def name(self):
        """网络应用的名字。这个名字常常是导入的名字，
        名字会不同，如果导入的名字是 dunder main 的话，
        这个名字就是运行文件的名字。当 Flask 需要网络应用的名字时，
        这个名字与显示的名字是一样的。这个名字可以被设置，而且
        可以被覆写来改变名字值。

        .. versionadded:: 0.8
        """
        if self.import_name == '__main__':
            fn = getattr(sys.modules['__main__'], '__file__', None)
            if fn is None:
                return '__main__'
            return os.path.splitext(os.path.basename(fn))[0]
        return self.import_name

    @property
    def propagate_exceptions(self):
        """返回 ``PROPAGATE_EXCEPTIONS`` 配置项的值，
        如果设置就有值，否则返回的是明知的默认值。

        .. versionadded:: 0.7
        """
        rv = self.config['PROPAGATE_EXCEPTIONS']
        if rv is not None:
            return rv
        return self.testing or self.debug

    @property
    def preserve_context_on_exception(self):
        """返回 ``PRESERVE_CONTEXT_ON_EXCEPTION`` 配置项值，
        如果设置就有值，否则返回的是明知的默认值。

        .. versionadded:: 0.7
        """
        rv = self.config['PRESERVE_CONTEXT_ON_EXCEPTION']
        if rv is not None:
            return rv
        return self.debug

    @locked_cached_property
    def logger(self):
        """是 ``'flask.app'`` 日志器，是一个标准的 Python
        :class:`~logging.Logger` 类。

        在调试模式中，日志器的 :attr:`~logging.Logger.level` 属性会由
         :data:`~logging.DEBUG` 代理对象来设置。

        如果没有配置处理器的话，会增加一个默认处理器。
        查看 :ref:`logging` 文档内容了解更多信息。

        .. versionchanged:: 1.0
            简化了行为。日志器总是叫做 ``flask.app`` 。
            日志级别只在配置时进行设置，它不会每次检查 ``app.debug`` 信息。
            只使用一种格式，与 ``app.debug`` 的格式没有分别。
            不会删除多个处理器，如果没有配置多个处理器的话，只增加一个处理器。

        .. versionadded:: 0.3
        """
        return create_logger(self)

    @locked_cached_property
    def jinja_env(self):
        """用来加载模版的 Jinja2 环境."""
        return self.create_jinja_environment()

    @property
    def got_first_request(self):
        """如果网络应用开始处理第一个请求，这个属性要设置成 ``True``

        .. versionadded:: 0.8
        """
        return self._got_first_request

    def make_config(self, instance_relative=False):
        """由 Flask 构造器用来建立配置属性。
        需要把 `instance_relative` 参数代入到 Flask 构造器里
        （名字叫做 `instance_relative_config`）并且要指明是否
        配置应该与实例路径关联起来，或者指明网络应用的根路径。

        .. versionadded:: 0.8
        """
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        defaults = dict(self.default_config)
        defaults['ENV'] = get_env()
        defaults['DEBUG'] = get_debug_flag()
        return self.config_class(root_path, defaults)

    def auto_find_instance_path(self):
        """如果没有把实例路径提供给网络应用类的构造器，
        尝试分配默认的实例路径。它基本上会计算到名叫
        ``instance`` 文件夹的路径，这个文件夹与
        dunder main 文件或包目录在一个路径里。

        .. versionadded:: 0.8
        """
        prefix, package_path = find_package(self.import_name)
        if prefix is None:
            return os.path.join(package_path, 'instance')
        return os.path.join(prefix, 'var', self.name + '-instance')

    def open_instance_resource(self, resource, mode='rb'):
        """从网络应用实例文件夹打开一个资源 (:attr:`instance_path`)。
        否则用 :meth:`open_resource` 方法来打开资源。
        实例资源也可以用写模式打开。

        :param resource: 资源名字。要访问子文件夹中的资源使用斜杠做分隔符。
        :param mode: 打开资源文件的模式，默认值是 'rb' 模式。
        """
        return open(os.path.join(self.instance_path, resource), mode)

    def _get_templates_auto_reload(self):
        """当模版内容改变后重载模版。
        由 :meth:`create_jinja_environment` 方法使用。

        这个类属性可以用 :data:`TEMPLATES_AUTO_RELOAD` 配置项进行配置。
        如果没有设置配置项，会在调试模式中开启此项配置。

        .. versionadded:: 1.0
            已增加此项属性，但根据已有的配置和行为才有效。
        """
        rv = self.config['TEMPLATES_AUTO_RELOAD']
        return rv if rv is not None else self.debug

    def _set_templates_auto_reload(self, value):
        self.config['TEMPLATES_AUTO_RELOAD'] = value

    templates_auto_reload = property(
        _get_templates_auto_reload, _set_templates_auto_reload
    )
    del _get_templates_auto_reload, _set_templates_auto_reload

    def create_jinja_environment(self):
        """根据 :attr:`jinja_options` 属性和
        :meth:`select_jinja_autoescape` 方法来建立 Jinja2 环境。
        从 07 版本开始，实例化后本方法也增加 Jinja2 全局对象和过滤器。
        覆写本方法来自定义行为。

        .. versionadded:: 0.5
        .. versionchanged:: 0.11
           ``Environment.auto_reload`` 的设置根据
           ``TEMPLATES_AUTO_RELOAD`` 配置项值来决定。
        """
        options = dict(self.jinja_options)

        if 'autoescape' not in options:
            options['autoescape'] = self.select_jinja_autoescape

        if 'auto_reload' not in options:
            options['auto_reload'] = self.templates_auto_reload

        rv = self.jinja_environment(self, **options)
        rv.globals.update(
            url_for=url_for,
            get_flashed_messages=get_flashed_messages,
            config=self.config,
            # request, session and g are normally added with the
            # context processor for efficiency reasons but for imported
            # templates we also want the proxies in there.
            request=request,
            session=session,
            g=g
        )
        rv.filters['tojson'] = json.tojson_filter
        return rv

    def create_global_jinja_loader(self):
        """建立 Jinja2 环境加载器。只可以用来覆写加载器，
        并且其它都不会变。不鼓励覆写本方法。
        相反应该覆写 :meth:`jinja_loader` 方法。

        全局加载器负责网络应用加载器和各个蓝图之间的调度。

        .. versionadded:: 0.7
        """
        return DispatchingJinjaLoader(self)

    def select_jinja_autoescape(self, filename):
        """如果自动转义根据模版名激活的话，返回 ``True`` 值。
        如果没提供模版名的话，也返回 `True` 值。

        .. versionadded:: 0.5
        """
        if filename is None:
            return True
        return filename.endswith(('.html', '.htm', '.xml', '.xhtml'))

    def update_template_context(self, context):
        """用一些共性使用的变量来更新模版语境。
        本方法会把请求、会话、配置和 g 对象注射到模版语境中，
        与模版语境处理器要注射的内容一样。注意 Flask 0.6 版本，
        如果一个语境处理器决定返回相同的键值的话，
        语境中原来的值不会被覆写。

        :param context: 语境是一个字典，更新字典都是原位增加额外变量。
        """
        funcs = self.template_context_processors[None]
        reqctx = _request_ctx_stack.top
        if reqctx is not None:
            bp = reqctx.request.blueprint
            if bp is not None and bp in self.template_context_processors:
                funcs = chain(funcs, self.template_context_processors[bp])
        orig_ctx = context.copy()
        for func in funcs:
            context.update(func())
        # make sure the original values win.  This makes it possible to
        # easier add new variables in context processors without breaking
        # existing views.
        context.update(orig_ctx)

    def make_shell_context(self):
        """为网络应用的一个交互式终端返回终端语境。
        本方法运行所有注册完的终端语境处理器。

        .. versionadded:: 0.11
        """
        rv = {'app': self, 'g': g}
        for processor in self.shell_context_processors:
            rv.update(processor())
        return rv

    #: What environment the app is running in. Flask and extensions may
    #: enable behaviors based on the environment, such as enabling debug
    #: mode. This maps to the :data:`ENV` config key. This is set by the
    #: :envvar:`FLASK_ENV` environment variable and may not behave as
    #: expected if set in code.
    #:
    #: **Do not enable development when deploying in production.**
    #:
    #: Default: ``'production'``
    env = ConfigAttribute('ENV')

    def _get_debug(self):
        return self.config['DEBUG']

    def _set_debug(self, value):
        self.config['DEBUG'] = value
        self.jinja_env.auto_reload = self.templates_auto_reload

    #: Whether debug mode is enabled. When using ``flask run`` to start
    #: the development server, an interactive debugger will be shown for
    #: unhandled exceptions, and the server will be reloaded when code
    #: changes. This maps to the :data:`DEBUG` config key. This is
    #: enabled when :attr:`env` is ``'development'`` and is overridden
    #: by the ``FLASK_DEBUG`` environment variable. It may not behave as
    #: expected if set in code.
    #:
    #: **Do not enable debug mode when deploying in production.**
    #:
    #: Default: ``True`` if :attr:`env` is ``'development'``, or
    #: ``False`` otherwise.
    debug = property(_get_debug, _set_debug)
    del _get_debug, _set_debug

    def run(self, host=None, port=None, debug=None,
            load_dotenv=True, **options):
        """在一个本地开发服务器上运行网络应用。

        在生产设置中不要使用 ``run()`` 方法。它不是为了一个生产服务器
        满足安全和性能需求的方法。
        相反对于 WSGI 服务器建议查看 :ref:`deployment` 文档内容。

        如果设置了 :attr:`debug` 属性的话，
        服务器会自动重载代码上的变更，并且在
        有一个例外发生时呈现一个调试器。

        如果你想要让网络应用运行在调试模式中的话，
        还想禁用交互式调试器上的代码执行功能，
        你可以代入 ``use_evalex=False`` 参数。
        这样会让调试器的回溯屏幕保持激活状态，
        但禁用了代码执行功能。

        在含有自动加载的开发模式中不建议使用本方法，
        因为会败坏支持功能。相反你应该使用 :command:`flask` 
        命令行脚本中的 ``run`` 命令来获得支持功能。

        .. admonition:: 记在心里

           Flask 会压制任何一个含有普通错误页面的服务器错误，
           除非是在调试模式中不会压制错误消息。
           正如只开启交互式调试器而没有代码重载时，
           你不得不要使用 :meth:`run` 方法时带上
            ``debug=True`` 和 ``use_reloader=False`` 这2个参数。
           不在调试模式时把 ``use_debugger`` 设置成 ``True`` 不会
           捕获任何一个例外类型，因为非调试模式中不会有捕获例外行为。

        :param host: 要监听的主机名。参数值设置成 ``'0.0.0.0'`` 时
                     会有一个外部也可以访问的主机。
                     默认值是 ``'127.0.0.1'`` 或者在 ``SERVER_NAME`` 配置项中来设置。
        :param port: 网络服务器的端口。默认值是 ``5000`` 或者设置在
                      ``SERVER_NAME`` 配置项中。
        :param debug: 开启或禁用调试模式。查看 :attr:`debug` 属性。
        :param load_dotenv: 加载最近的 :file:`.env` 文件和
                             :file:`.flaskenv` 文件来设置环境变量。
                            也会把工作目录变更到含有第一个文件的目录上去。
        :param options: 更多选项都是直接根据 Werkzeug 服务器来决定。
                        查看 :func:`werkzeug.serving.run_simple` 函数了解更多信息。

        .. versionchanged:: 1.0
            如果安装完 python-dotenv 的话，会用它来加载
             :file:`.env` 文件和 :file:`.flaskenv` 文件里的环境变量。

            如果设置 :envvar:`FLASK_ENV` 和 :envvar:`FLASK_DEBUG`
            这2个环境变量的话，会覆写 :attr:`env` 和 :attr:`debug` 这2个属性。

            默认开启线程模式。

        .. versionchanged:: 0.10
            默认端口是从 ``SERVER_NAME`` 环境变量中获得。
        """
        # Change this into a no-op if the server is invoked from the
        # command line. Have a look at cli.py for more information.
        if os.environ.get('FLASK_RUN_FROM_CLI') == 'true':
            from .debughelpers import explain_ignored_app_run
            explain_ignored_app_run()
            return

        if get_load_dotenv(load_dotenv):
            cli.load_dotenv()

            # if set, let env vars override previous values
            if 'FLASK_ENV' in os.environ:
                self.env = get_env()
                self.debug = get_debug_flag()
            elif 'FLASK_DEBUG' in os.environ:
                self.debug = get_debug_flag()

        # debug passed to method overrides all other sources
        if debug is not None:
            self.debug = bool(debug)

        _host = '127.0.0.1'
        _port = 5000
        server_name = self.config.get('SERVER_NAME')
        sn_host, sn_port = None, None

        if server_name:
            sn_host, _, sn_port = server_name.partition(':')

        host = host or sn_host or _host
        port = int(port or sn_port or _port)

        options.setdefault('use_reloader', self.debug)
        options.setdefault('use_debugger', self.debug)
        options.setdefault('threaded', True)

        cli.show_server_banner(self.env, self.debug, self.name, False)

        from werkzeug.serving import run_simple

        try:
            run_simple(host, port, self, **options)
        finally:
            # reset the first request information if the development server
            # reset normally.  This makes it possible to restart the server
            # without reloader and that stuff from an interactive shell.
            self._got_first_request = False

    def test_client(self, use_cookies=True, **kwargs):
        """为网络应用建立一个单元测试客户端。
        对于单元测试的信息回顾 :ref:`testing` 文档内容。

        注意，如果你正在测试网络应用代码中的评估或例外时，
        你必须设置 ``app.testing = True`` 配置项，
        这样才会把例外类型传播到单元测试客户端里去。
        否则，例外类型会被网络应用处理（在单元测试客户端中就看不到例外类型了）
        并且只会把一个 AssertionError 或其它例外类型解释为
        一个 500 状态代号给单元测试客户端。
        查看 :attr:`testing` 属性。例如::

            app.testing = True
            client = app.test_client()

        单元测试客户端可以用在一个 ``with`` 语句块中来
        确保自动关闭语境。如果你想要访问语境中的本地对象
        来测试的话，这就是有用的方法::

            with app.test_client() as c:
                rv = c.get('/?vodka=42')
                assert request.args['vodka'] == '42'

        另外，你可以代入可选的关键字参数，
        这些关键字参数会稍后会代入到网络应用的
         :attr:`test_client_class` 属性构造器中。
        例如::

            from flask.testing import FlaskClient

            class CustomClient(FlaskClient):
                def __init__(self, *args, **kwargs):
                    self._authentication = kwargs.pop("authentication")
                    super(CustomClient,self).__init__( *args, **kwargs)

            app.test_client_class = CustomClient
            client = app.test_client(authentication='Basic ....')

        查看 :class:`~flask.testing.FlaskClient` 了解更多信息。

        .. versionchanged:: 0.4
           为客户端增加 ``with`` 语句块用法。

        .. versionadded:: 0.7
           增加 `use_cookies` 参数同时有能力覆写
           由 :attr:`test_client_class` 属性使用的客户端。

        .. versionchanged:: 0.11
           增加 `**kwargs` 参数来支持代入额外关键字参数
           到 :attr:`test_client_class` 属性构造器中。
        """
        cls = self.test_client_class
        if cls is None:
            from flask.testing import FlaskClient as cls
        return cls(self, self.response_class, use_cookies=use_cookies, **kwargs)

    def test_cli_runner(self, **kwargs):
        """为单元测试命令行命令建立一个命令行运行器。
        查看 :ref:`testing-cli` 文档内容。

        返回一个 :attr:`test_cli_runner_class` 属性的实例，
        默认通过 :class:`~flask.testing.FlaskCliRunner` 来返回。
        Flask 网络应用实例对象作为第一参数。

        .. versionadded:: 1.0
        """
        cls = self.test_cli_runner_class

        if cls is None:
            from flask.testing import FlaskCliRunner as cls

        return cls(self, **kwargs)

    def open_session(self, request):
        """建立或打开一个新会话。
        默认部署会存储一个签过名的 cookie 中的所有会话数据。
        本方法需要设置 :attr:`secret_key` 属性值。
        相反覆写本方法我们建议去覆写 :class:`session_interface` 类。

        .. deprecated: 1.0
            在 Flask 1.1 版本中会删除本方法。
            而是使用 ``session_interface.open_session`` 来代替。

        :param request: 参数值是 :attr:`request_class` 属性的一个实例。
        """

        warnings.warn(DeprecationWarning(
            '"open_session" is deprecated and will be removed in 1.1. Use'
            ' "session_interface.open_session" instead.'
        ))
        return self.session_interface.open_session(self, request)

    def save_session(self, session, response):
        """如果需要更新的话，保存会话。
        默认部署会检查 :meth:`open_session` 方法。
        相反覆写本方法我们建议去覆写 :class:`session_interface` 类。

        .. deprecated: 1.0
            在 Flask 1.1 版本中会删除本方法。
            而是使用 ``session_interface.save_session`` 来代替。

        :param session: 要保存的会话（一个
                        :class:`~werkzeug.contrib.securecookie.SecureCookie`
                        类对象）
        :param response: 参数值是 :attr:`response_class` 属性的一个实例。
        """

        warnings.warn(DeprecationWarning(
            '"save_session" is deprecated and will be removed in 1.1. Use'
            ' "session_interface.save_session" instead.'
        ))
        return self.session_interface.save_session(self, session, response)

    def make_null_session(self):
        """建立一个丢失会话的新实例。
        覆写本方法我们建议去覆写 :class:`session_interface` 类。

        .. deprecated: 1.0
            在 Flask 1.1 版本中会删除本方法。
            而是使用 ``session_interface.make_null_session`` 来代替。

        .. versionadded:: 0.7
        """

        warnings.warn(DeprecationWarning(
            '"make_null_session" is deprecated and will be removed in 1.1. Use'
            ' "session_interface.make_null_session" instead.'
        ))
        return self.session_interface.make_null_session(self)

    @setupmethod
    def register_blueprint(self, blueprint, **options):
        """在网络应用上注册一个 :class:`~flask.Blueprint` 类。
        代入到本方法中的关键字参数都会覆写蓝图上的默认设置。

        调用蓝图的 :meth:`~flask.Blueprint.register` 方法是在
        把蓝图记录在网络应用的 :attr:`blueprints` 属性之后的事情。

        :param blueprint: 要注册的蓝图。
        :param url_prefix: 本参数值会作为蓝图路由前缀。
        :param subdomain: 本参数值是蓝图路由要匹配的子域名。
        :param url_defaults: 蓝图路由会为视图函数参数使用本参数值。
        :param options: 额外的关键字参数都代入到
                        :class:`~flask.blueprints.BlueprintSetupState` 中。
                        这些参数可以在 :meth:`~flask.Blueprint.record` 方法
                        回调中访问。

        .. versionadded:: 0.7
        """
        first_registration = False

        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, (
                'A name collision occurred between blueprints %r and %r. Both'
                ' share the same name "%s". Blueprints that are created on the'
                ' fly need unique names.' % (
                    blueprint, self.blueprints[blueprint.name], blueprint.name
                )
            )
        else:
            self.blueprints[blueprint.name] = blueprint
            self._blueprint_order.append(blueprint)
            first_registration = True

        blueprint.register(self, options, first_registration)

    def iter_blueprints(self):
        """按照蓝图注册的顺序迭代所有的蓝图。

        .. versionadded:: 0.11
        """
        return iter(self._blueprint_order)

    @setupmethod
    def add_url_rule(self, rule, endpoint=None, view_func=None,
                     provide_automatic_options=None, **options):
        """连接一个 URL 规则。工作起来完全像 :meth:`route` 方法装饰器一样。
        如果提供了一个 `view_func` 参数值的话，会带着端点来进行注册。

        装饰器基础示例::

            @app.route('/')
            def index():
                pass

        等效于如下本方法的使用::

            def index():
                pass
            app.add_url_rule('/', 'index', index)

        如果没提供 `view_func` 参数的话，
        你会需要连接端点到一个视图函数上，用法如下::

            app.view_functions['index'] = index

        内部上来说 :meth:`route` 方法引入了 :meth:`add_url_rule` 方法，
        所以如果你想要自定义行为的话，通过子类化时你只可以改变本方法。

        更多信息参考 :ref:`url-route-registrations` 文档内容。

        .. versionchanged:: 0.2
           增加了 `view_func` 参数。

        .. versionchanged:: 0.6
           自动增加 ``OPTIONS`` 成方法。

        :param rule: 字符串形式的 URL 规则。
        :param endpoint: 注册完的 URL 规则端点。Flask 自身把
                         视图函数的名字假设成端点。
        :param view_func: 当对提供的端点服务一个请求时要调用的视图函数。
        :param provide_automatic_options: 控制是否自动把 ``OPTIONS`` 增加成方法。
                                          增加规则前通过设置
                                          ``view_func.provide_automatic_options = False``
                                          来控制本参数。
        :param options: 本参数都是根据
                        :class:`~werkzeug.routing.Rule` 类对象直接使用。
                        一项 Werkzeug 变更正在处理这些方法。
                        本参数形成的方法是一种列表形式，这种规则应该限制在
                        （``GET``, ``POST`` 等 HTTP 方法上。）
                        默认情况，一条规则只为 ``GET`` 方法执行监听任务
                        （并且隐含 ``HEAD`` ）。
                        从 Flask 0.6 版本开始， ``OPTIONS`` 是隐含地
                        增加上后由标准请求处理来进行处理。
        """
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        options['endpoint'] = endpoint
        methods = options.pop('methods', None)

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only ``GET`` as default.
        if methods is None:
            methods = getattr(view_func, 'methods', None) or ('GET',)
        if isinstance(methods, string_types):
            raise TypeError('Allowed methods have to be iterables of strings, '
                            'for example: @app.route(..., methods=["POST"])')
        methods = set(item.upper() for item in methods)

        # Methods that should always be added
        required_methods = set(getattr(view_func, 'required_methods', ()))

        # starting with Flask 0.8 the view_func object can disable and
        # force-enable the automatic options handling.
        if provide_automatic_options is None:
            provide_automatic_options = getattr(view_func,
                'provide_automatic_options', None)

        if provide_automatic_options is None:
            if 'OPTIONS' not in methods:
                provide_automatic_options = True
                required_methods.add('OPTIONS')
            else:
                provide_automatic_options = False

        # Add the required methods now.
        methods |= required_methods

        rule = self.url_rule_class(rule, methods=methods, **options)
        rule.provide_automatic_options = provide_automatic_options

        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func

    def route(self, rule, **options):
        """根据一条 URL 规则来注册一个视图函数的装饰器。
        本方法与 :meth:`add_url_rule` 方法工作效果是一样的，
        却只是为了装饰器用法::

            @app.route('/')
            def index():
                return 'Hello World'

        对于更多信息参考 :ref:`url-route-registrations` 文档内容。

        :param rule: 字符串形式的 URL 规则。
        :param endpoint: 已注册的 URL 规则的端点。Flask 自身把视图函数名字
                         假设成端点。
        :param options: 关键字参数根据
                        :class:`~werkzeug.routing.Rule` 类直接使用。
                        一项 Werkzeug 变更正在处理这些方法。
                        本参数形成的方法是一种列表形式，这种规则应该限制在
                        （``GET``, ``POST`` 等 HTTP 方法上。）
                        默认情况，一条规则只为 ``GET`` 方法执行监听任务
                        （并且隐含 ``HEAD`` ）。
                        从 Flask 0.6 版本开始， ``OPTIONS`` 是隐含地
                        增加上后由标准请求处理来进行处理。
        """
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    @setupmethod
    def endpoint(self, endpoint):
        """把一个函数注册成一个端点的装饰器。
        示例::

            @app.endpoint('example.endpoint')
            def example():
                return "example"

        :param endpoint: 端点名字
        """
        def decorator(f):
            self.view_functions[endpoint] = f
            return f
        return decorator

    @staticmethod
    def _get_exc_class_and_code(exc_class_or_code):
        """确保我们只把例外类型注册成处理器键."""
        if isinstance(exc_class_or_code, integer_types):
            exc_class = default_exceptions[exc_class_or_code]
        else:
            exc_class = exc_class_or_code

        assert issubclass(exc_class, Exception)

        if issubclass(exc_class, HTTPException):
            return exc_class, exc_class.code
        else:
            return exc_class, None

    @setupmethod
    def errorhandler(self, code_or_exception):
        """把一个函数注册到处理代号错误或处理例外类型错误上。

        根据一个错误代号注册一个函数的装饰器。
        示例::

            @app.errorhandler(404)
            def page_not_found(error):
                return 'This page does not exist', 404

        你也可以用任意例外类型来注册处理器::

            @app.errorhandler(DatabaseError)
            def special_exception_handler(error):
                return 'Database connection failed', 500

        .. versionadded:: 0.7
            对于网络应用普遍错误处理器来说，
            使用 :meth:`register_error_handler` 方法，
            而不要直接修改 :attr:`error_handler_spec` 属性。

        .. versionadded:: 0.7
           此时一种也可以注册自定义例外类型的装饰器，
           自定义例外类型不需要是
           :class:`~werkzeug.exceptions.HTTPException` 类
           的一个子类。

        :param code_or_exception: 参数值可以是HTTP 响应代号整数类型，
                                  或是任意一个例外类型。
        """
        def decorator(f):
            self._register_error_handler(None, code_or_exception, f)
            return f
        return decorator

    @setupmethod
    def register_error_handler(self, code_or_exception, f):
        """另外一种把函数固定到 :meth:`errorhandler` 方法装饰器上的方法，
        本方法是一种更直接的用法，不需要装饰器用法。

        .. versionadded:: 0.7
        """
        self._register_error_handler(None, code_or_exception, f)

    @setupmethod
    def _register_error_handler(self, key, code_or_exception, f):
        """
        :type key: 类型是 `None` 或 `str` 。
        :type code_or_exception: 类型是 `int` 或或一个类外类型。
        :type f: 类型是一个函数。
        """
        if isinstance(code_or_exception, HTTPException):  # old broken behavior
            raise ValueError(
                'Tried to register a handler for an exception instance {0!r}.'
                ' Handlers can only be registered for exception classes or'
                ' HTTP error codes.'.format(code_or_exception)
            )

        try:
            exc_class, code = self._get_exc_class_and_code(code_or_exception)
        except KeyError:
            raise KeyError(
                "'{0}' is not a recognized HTTP error code. Use a subclass of"
                " HTTPException with that code instead.".format(code_or_exception)
            )

        handlers = self.error_handler_spec.setdefault(key, {}).setdefault(code, {})
        handlers[exc_class] = f

    @setupmethod
    def template_filter(self, name=None):
        """一个用来注册自定义模版过滤器的装饰器。
        你可以描述一个过滤器名字，否则会使用函数名。
        示例::

          @app.template_filter()
          def reverse(s):
              return s[::-1]

        :param name: 可选参数值是过滤器的名字，否则使用函数的名字作为过滤器名。
        """
        def decorator(f):
            self.add_template_filter(f, name=name)
            return f
        return decorator

    @setupmethod
    def add_template_filter(self, f, name=None):
        """注册一个自定义模版过滤器。工作完全像
        :meth:`template_filter` 方法装饰器一样。

        :param name: 可选参数值是过滤器的名字，否则使用函数的名字作为过滤器名。
        """
        self.jinja_env.filters[name or f.__name__] = f

    @setupmethod
    def template_test(self, name=None):
        """一个用来注册自定义模版测试的装饰器。
        你可以描述一个名字给测试，否则会使用函数名。
        示例::

          @app.template_test()
          def is_prime(n):
              if n == 2:
                  return True
              for i in range(2, int(math.ceil(math.sqrt(n))) + 1):
                  if n % i == 0:
                      return False
              return True

        .. versionadded:: 0.10

        :param name: 可选参数值是测试的名字，否则会使用函数名作为测试名。
        """
        def decorator(f):
            self.add_template_test(f, name=name)
            return f
        return decorator

    @setupmethod
    def add_template_test(self, f, name=None):
        """注册一个自定义模版测试。工作起来完全像
        :meth:`template_test` 方法装饰器一样。

        .. versionadded:: 0.10

        :param name: 可选参数值是测试的名字，否则会使用函数名作为测试名。
        """
        self.jinja_env.tests[name or f.__name__] = f

    @setupmethod
    def template_global(self, name=None):
        """一个用来注册一个自定义模版全局函数的装饰器。
        你可以描述一个名字给全局函数，否则会使用函数名。
        示例::

            @app.template_global()
            def double(n):
                return 2 * n

        .. versionadded:: 0.10

        :param name: 可选参数是全局函数的名字，否则会使用函数名作为全局函数名。
        """
        def decorator(f):
            self.add_template_global(f, name=name)
            return f
        return decorator

    @setupmethod
    def add_template_global(self, f, name=None):
        """注册一个自定义模版全局函数。工作起来像
        :meth:`template_global` 方法装饰器一样。

        .. versionadded:: 0.10

        :param name: 可选参数是全局函数的名字，否则会使用函数名作为全局函数名。
        """
        self.jinja_env.globals[name or f.__name__] = f

    @setupmethod
    def before_request(self, f):
        """在每个请求之前注册一个要运行的函数。

        例如，本方法可以用来打开一个数据库连接，
        或者用来加载会话中登录的用户。

        被调用的函数是无参函数。如果被调用的函数返回了一个非空值的话，
        返回值处理成视图函数返回的值，然后停止下一步的请求处理。
        """
        self.before_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def before_first_request(self, f):
        """在第一个请求到达本网络应用实例之前，
        注册一个要运行的函数。

        被调用的函数是无参函数，并且忽略其返回的值。

        .. versionadded:: 0.8
        """
        self.before_first_request_funcs.append(f)
        return f

    @setupmethod
    def after_request(self, f):
        """每个请求之后注册一个要运行的函数。

        你的函数必须得到一个参数、
        一个 :attr:`response_class` 属性的实例，
        以及返回一个新响应对象或返回相同的响应对象
        （查看 :meth:`process_response` 方法）。

        作为 Flask 0.7 版本，这个函数也许不会在
        一个已发生的未处理的例外类型情况下，在请求结束时被执行。
        """
        self.after_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def teardown_request(self, f):
        """在每个请求结束时注册一个要运行的函数，
        不在乎是否有一个例外类型。
        当请求语境删除完的时候，这些函数都会被执行，
        即使没有真正执行一个请求也会被执行。

        示例::

            ctx = app.test_request_context()
            ctx.push()
            ...
            ctx.pop()

        当上面示例中的 ``ctx.pop()`` 执行完毕时，
        本方法注册的函数都会只在请求语境从激活的语境堆栈中删除之前被调用。
        如果你们在单元测试中正使用这种构造的话，就与此有关了。

        通用中本方法注册的函数必须要包含所需的每一步代码，
        这样才能避免这些函数不会失败。
        如果这些函数中确实要执行的代码会失败的话，
        那么就要使用 `try/except` 语句结构来包裹着要执行的代码，
        并且记录发生的错误。

        当一个被注册的函数因一个例外类型而调用时，
        例外类型会代入成一个错误对象。

        被注册的函数返回值都会被忽略掉。

        .. admonition:: 注意调试模式

           在调试模式中 Flask 不会在一个例外上触发本方法的一个请求。
           相反，会保留它处于活跃状态，所以交互式调试器依然可以访问被注册的函数。
           这种行为可以通过 ``PRESERVE_CONTEXT_ON_EXCEPTION`` 配置变量来控制。
        """
        self.teardown_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def teardown_appcontext(self, f):
        """当网络应用语境结束时，注册一个要调用的函数。
        当请求语境被删除时，这些被注册的函数也都典型被调用。

        示例::

            ctx = app.app_context()
            ctx.push()
            ...
            ctx.pop()

        当上面示例中的 ``ctx.pop()`` 执行完时，
        被注册的函数只在网络应用语境从激活的语境堆栈中被删除之前被调用。
        如果你们在单元测试中正使用这种构造的话，就与此有关了。

        因为一个请求语境典型也管理着一个网络应用语境，
        当你删除一个请求语境时，网络语境也会被调用。

        当一个被注册函数因一个未处理的例外被调用时，
        例外会代入成一个错误对象。
        如果注册了一个 :meth:`errorhandler` 方法的话，
        错误处理器会处理例外，并且被注册函数不会接收例外。

        被注册函数返回的值都会被忽略。

        .. versionadded:: 0.9
        """
        self.teardown_appcontext_funcs.append(f)
        return f

    @setupmethod
    def context_processor(self, f):
        """注册一个模版语境处理器函数."""
        self.template_context_processors[None].append(f)
        return f

    @setupmethod
    def shell_context_processor(self, f):
        """注册一个终端语境处理器函数。

        .. versionadded:: 0.11
        """
        self.shell_context_processors.append(f)
        return f

    @setupmethod
    def url_value_preprocessor(self, f):
        """为网络应用里的所有视图函数注册一个 URL 值处理器函数。
        这些被注册函数会在 :meth:`before_request` 方法注册的
        函数之前被调用。

        被注册的函数可以修改从匹配的 URL 捕获的值，
        修改捕获的值都是在这些值代入视图函数之前进行修改。
        例如，被注册的函数可以用来删除一个共性的语言代码值，
        然后把删除的值存储在 ``g`` 对象里，
        这要比把删除的值代入到每个视图函数中要好。

        被注册的函数代入成端点名和值字典中。
        被注册的函数返回值被忽略。
        """
        self.url_value_preprocessors.setdefault(None, []).append(f)
        return f

    @setupmethod
    def url_defaults(self, f):
        """为网络应用的所有视图函数针对 URL 规则使用的回调函数。
        带着端点和值被调用，而且应该更新代入的值。
        """
        self.url_default_functions.setdefault(None, []).append(f)
        return f

    def _find_error_handler(self, e):
        """返回一个为一种例外类型注册完的错误处理器，顺序是：
        一个具体代号的蓝图处理器，
        一个具体代号的网络应用处理器，
        一种例外类型的蓝图处理器，
        一种例外类型的网络应用处理器，
        如果没有一个合适的处理器就返回 ``None`` 值。
        """
        exc_class, code = self._get_exc_class_and_code(type(e))

        for name, c in (
            (request.blueprint, code), (None, code),
            (request.blueprint, None), (None, None)
        ):
            handler_map = self.error_handler_spec.setdefault(name, {}).get(c)

            if not handler_map:
                continue

            for cls in exc_class.__mro__:
                handler = handler_map.get(cls)

                if handler is not None:
                    return handler

    def handle_http_exception(self, e):
        """处理一个 HTTP 例外。默认情况下本方法会引入
        注册的错误处理器后回滚把例外返回成响应对象。

        .. versionchanged:: 1.0.3
            ``RoutingException`` 例外内部用于类似路由中的斜杠重定向行动，
            本例外不代入到错误处理器中。

        .. versionchanged:: 1.0
            HTTP 例外都通过代号 *和* MRO 来查询，
            所以 ``HTTPExcpetion`` 例外子类可以
            用一个捕获所有基类例外的处理器来处理。

        .. versionadded:: 0.3
        """
        # Proxy exceptions don't have error codes.  We want to always return
        # those unchanged as errors
        if e.code is None:
            return e

        # RoutingExceptions are used internally to trigger routing
        # actions, such as slash redirects raising RequestRedirect. They
        # are not raised or handled in user code.
        if isinstance(e, RoutingException):
            return e

        handler = self._find_error_handler(e)
        if handler is None:
            return e
        return handler(e)

    def trap_http_exception(self, e):
        """检查一个 HTTP 例外是否应该被捕获。
        如果 ``TRAP_BAD_REQUEST_ERRORS`` 设置成 ``True`` 的话，
        默认情况下，除了一个败坏的请求键错误，
        本方法会为所有例外返回 ``False`` 值。
        如果 ``TRAP_HTTP_EXCEPTIONS`` 设置成 ``True`` 的话，
        本方法也会返回 ``True`` 值。

        对一个视图函数抛出的所有 HTTP 例外来说都会调用本方法。
        如果对任何一个例外错误处理器来说，
        本方法返回 ``True`` 的话，该例外不会被调用，
        在堆栈中会显示成常规例外。
        对于调试隐含地抛出 HTTP 例外来说是有帮助的。

        .. versionchanged:: 1.0
            在调试模式中败坏的请求错误默认不会被捕获。

        .. versionadded:: 0.8
        """
        if self.config['TRAP_HTTP_EXCEPTIONS']:
            return True

        trap_bad_request = self.config['TRAP_BAD_REQUEST_ERRORS']

        # if unset, trap key errors in debug mode
        if (
            trap_bad_request is None and self.debug
            and isinstance(e, BadRequestKeyError)
        ):
            return True

        if trap_bad_request:
            return isinstance(e, BadRequest)

        return False

    def handle_user_exception(self, e):
        """不管什么时候一个应该被处理的例外出现时，
        都会调用本方法。一个具体情况是
        :class:`~werkzeug.exceptions.HTTPException` 类，
        这种例外是直接给 :meth:`handle_http_exception` 方法的。
        本方法即返回一个响应值，也二次抛出含有相同堆栈的例外。

        .. versionchanged:: 1.0
            来自请求数据抛出的键错误，在调试模式中可能
            ``form`` 显示败坏的键要比显示一个普通败坏请求消息要好。

        .. versionadded:: 0.7
        """
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e
        # ensure not to trash sys.exc_info() at that point in case someone
        # wants the traceback preserved in handle_http_exception.  Of course
        # we cannot prevent users from trashing it themselves in a custom
        # trap_http_exception method so that's their fault then.

        if isinstance(e, BadRequestKeyError):
            if self.debug or self.config["TRAP_BAD_REQUEST_ERRORS"]:
                # Werkzeug < 0.15 doesn't add the KeyError to the 400
                # message, add it in manually.
                description = e.get_description()

                if e.args[0] not in description:
                    e.description = "KeyError: '{}'".format(*e.args)
            else:
                # Werkzeug >= 0.15 does add it, remove it in production
                e.args = ()

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        handler = self._find_error_handler(e)

        if handler is None:
            reraise(exc_type, exc_value, tb)
        return handler(e)

    def handle_exception(self, e):
        """当一个例外出现而没捕获到，默认例外处理介入。
        在调试模式中例外会立即二次抛出，
        否则例外被记录下来后对一个 500 内部服务器错误使用处理器。
        如果没有这样的处理器的话，显示一个默认 500 内部服务器错误消息。

        .. versionadded:: 0.3
        """
        exc_type, exc_value, tb = sys.exc_info()
        got_request_exception.send(self, exception=e)

        if self.propagate_exceptions:
            # if we want to repropagate the exception, we can attempt to
            # raise it with the whole traceback in case we can do that
            # (the function was actually called from the except part)
            # otherwise, we just raise the error again
            if exc_value is e:
                reraise(exc_type, exc_value, tb)
            else:
                raise e

        self.log_exception((exc_type, exc_value, tb))
        handler = self._find_error_handler(InternalServerError())
        if handler is None:
            return InternalServerError()
        return self.finalize_request(handler(e), from_error_handler=True)

    def log_exception(self, exc_info):
        """记录一个例外。如果调试被禁用并且正好在处理器被调用之前，
        本方法会由 :meth:`handle_exception` 方法来调用。
        默认部署会在 :attr:`logger` 属性上把例外记录成错误。

        .. versionadded:: 0.8
        """
        self.logger.error('Exception on %s [%s]' % (
            request.path,
            request.method
        ), exc_info=exc_info)

    def raise_routing_exception(self, request):
        """在路由期间被记录的例外都要用这个方法进行二次抛出。
        调试期间对于非 ``GET``、 ``HEAD`` 或 ``OPTIONS``
        请求方法我们不二次抛出重定向请求，
        反而我们抛出一个不同的错误来帮助调试。

        :internal:
        """
        if not self.debug \
           or not isinstance(request.routing_exception, RequestRedirect) \
           or request.method in ('GET', 'HEAD', 'OPTIONS'):
            raise request.routing_exception

        from .debughelpers import FormDataRoutingRedirect
        raise FormDataRoutingRedirect(request)

    def dispatch_request(self):
        """实现请求调用。匹配 URL 和 返回视图函数返回值，
        或者返回错误处理器返回值。本方法不能返回一个响应对象。
        要把返回值转换成一个正确的响应对象，
        那就调用 :func:`make_response` 方法。

        .. versionchanged:: 0.7
           本方法不再做例外处理了，这类代码已经移到
           :meth:`full_dispatch_request` 新方法中去了。
        """
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule = req.url_rule
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if getattr(rule, 'provide_automatic_options', False) \
           and req.method == 'OPTIONS':
            return self.make_default_options_response()
        # otherwise dispatch to the handler for that endpoint
        return self.view_functions[rule.endpoint](**req.view_args)

    def full_dispatch_request(self):
        """调度请求并且在请求顶层执行
        请求预处理和后置处理，也会捕获 HTTP 例外以及错误处理。

        .. versionadded:: 0.7
        """
        self.try_trigger_before_first_request_functions()
        try:
            request_started.send(self)
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        return self.finalize_request(rv)

    def finalize_request(self, rv, from_error_handler=False):
        """根据一个视图函数的返回值，
        本函数通过把返回值转换成一个响应来终止请求，并且
        引入后置处理函数。本方法即可以为正常请求调度，
        也可以为错误处理器而使用。

        因为这就意味着，本方法也许被调用成一种失败的结果，
        一种具体的安全模式使用 `from_error_handler`
        旗语来进行开启后是可用的。
        如果开启安全模式的话，响应处理中的失败
        会被记录下来，否则会忽略失败。

        :internal:
        """
        response = self.make_response(rv)
        try:
            response = self.process_response(response)
            request_finished.send(self, response=response)
        except Exception:
            if not from_error_handler:
                raise
            self.logger.exception('Request finalizing failed with an '
                                  'error while handling an error')
        return response

    def try_trigger_before_first_request_functions(self):
        """在每个请求之前调用本方法，
        并且会确保本方法触发 :attr:`before_first_request_funcs` 属性，
        而且每个网络应用实例只触发一次（常常意味着进程）。

        :internal:
        """
        if self._got_first_request:
            return
        with self._before_request_lock:
            if self._got_first_request:
                return
            for func in self.before_first_request_funcs:
                func()
            self._got_first_request = True

    def make_default_options_response(self):
        """本方法的调用是要建立默认 ``OPTIONS`` 响应。
        这可以通过子类化来改变，因为子类化可以改变
        ``OPTIONS`` 响应的默认行为。

        .. versionadded:: 0.7
        """
        adapter = _request_ctx_stack.top.url_adapter
        if hasattr(adapter, 'allowed_methods'):
            methods = adapter.allowed_methods()
        else:
            # fallback for Werkzeug < 0.7
            methods = []
            try:
                adapter.match(method='--')
            except MethodNotAllowed as e:
                methods = e.valid_methods
            except HTTPException as e:
                pass
        rv = self.response_class()
        rv.allow.update(methods)
        return rv

    def should_ignore_error(self, error):
        """这个方法的调用是要弄清楚是否应该忽略一个错误，
        而错误都是属于释放系统所担心的。
        如果本方法返回 ``True`` 的话，
        那么释放处理器就得不到错误了。

        .. versionadded:: 0.10
        """
        return False

    def make_response(self, rv):
        """把一个视图函数的返回值转换成一个 :attr:`response_class` 属性的实例。

        :param rv: 视图函数的返回值。视图函数必须返回一个响应。
                   不允许返回 ``None`` 或
                   不允许视图函数结束时没有返回值。
                   对于 ``view_rv`` 来说允许返回如下类型：

                   ``str`` (``unicode`` in Python 2)
                   返回的响应对象主体要用字符串编码成 UTF-8 类型。

                   ``bytes`` (``str`` in Python 2)
                   返回的响应对象主体是字节类型。

                   ``tuple``
                   可以是 ``(body, status, headers)``、 ``(body, status)`` 或
                   ``(body, headers)`` 形式，其中 ``body`` 是这里允许的任何一种
                   其它类型， ``status`` 是一个字符串或一个整数，以及 ``headers`` 是
                   一个字典或一个 ``(key, value)`` 键值对儿元组列表形式。
                   如果 ``body`` 是一个 :attr:`response_class` 属性的实例的话，
                   ``status`` 覆写现有的值后 ``headers`` 都被展开。

                   :attr:`response_class`
                   被返回的对象无变化。

                   其它的 :class:`~werkzeug.wrappers.Response`
                   对象强制成 :attr:`response_class` 属性。

                   :func:`callable`
                   函数被调用成一个 WSGI 网络应用。
                   结果用来建立一个响应对象。

        .. versionchanged:: 0.9
           对响应对象来说前面一个元组被解释成多参数。
        """

        status = headers = None

        # unpack tuple returns
        if isinstance(rv, tuple):
            len_rv = len(rv)

            # a 3-tuple is unpacked directly
            if len_rv == 3:
                rv, status, headers = rv
            # decide if a 2-tuple has status or headers
            elif len_rv == 2:
                if isinstance(rv[1], (Headers, dict, tuple, list)):
                    rv, headers = rv
                else:
                    rv, status = rv
            # other sized tuples are not allowed
            else:
                raise TypeError(
                    'The view function did not return a valid response tuple.'
                    ' The tuple must have the form (body, status, headers),'
                    ' (body, status), or (body, headers).'
                )

        # the body must not be None
        if rv is None:
            raise TypeError(
                'The view function did not return a valid response. The'
                ' function either returned None or ended without a return'
                ' statement.'
            )

        # make sure the body is an instance of the response class
        if not isinstance(rv, self.response_class):
            if isinstance(rv, (text_type, bytes, bytearray)):
                # let the response class set the status and headers instead of
                # waiting to do it manually, so that the class can handle any
                # special logic
                rv = self.response_class(rv, status=status, headers=headers)
                status = headers = None
            else:
                # evaluate a WSGI callable, or coerce a different response
                # class to the correct type
                try:
                    rv = self.response_class.force_type(rv, request.environ)
                except TypeError as e:
                    new_error = TypeError(
                        '{e}\nThe view function did not return a valid'
                        ' response. The return type must be a string, tuple,'
                        ' Response instance, or WSGI callable, but it was a'
                        ' {rv.__class__.__name__}.'.format(e=e, rv=rv)
                    )
                    reraise(TypeError, new_error, sys.exc_info()[2])

        # prefer the status if it was provided
        if status is not None:
            if isinstance(status, (text_type, bytes, bytearray)):
                rv.status = status
            else:
                rv.status_code = status

        # extend existing headers with provided headers
        if headers:
            rv.headers.extend(headers)

        return rv

    def create_url_adapter(self, request):
        """为给出的请求建立一个 URL 适配器。
        建立 URL 适配器的所在位置根本没有配置请求语境，
        所以要明确地代入请求。

        .. versionadded:: 0.6

        .. versionchanged:: 0.9
           当 URL 适配器是为网络应用语境建立时，
           现在没有一个请求对象也可以调用本方法。

        .. versionchanged:: 1.0
            :data:`SERVER_NAME` 不再隐含开启子域名匹配。
            相反要使用 :attr:`subdomain_matching` 来代替本方法。
        """
        if request is not None:
            # If subdomain matching is disabled (the default), use the
            # default subdomain in all cases. This should be the default
            # in Werkzeug but it currently does not have that feature.
            subdomain = ((self.url_map.default_subdomain or None)
                         if not self.subdomain_matching else None)
            return self.url_map.bind_to_environ(
                request.environ,
                server_name=self.config['SERVER_NAME'],
                subdomain=subdomain)
        # We need at the very least the server name to be set for this
        # to work.
        if self.config['SERVER_NAME'] is not None:
            return self.url_map.bind(
                self.config['SERVER_NAME'],
                script_name=self.config['APPLICATION_ROOT'],
                url_scheme=self.config['PREFERRED_URL_SCHEME'])

    def inject_url_defaults(self, endpoint, values):
        """根据提供的端点直接把 URL 默认值注射到
        代入的值参数字典中。本方法内部使用并且
        在 URL 建立时自动调用本方法。

        .. versionadded:: 0.7
        """
        funcs = self.url_default_functions.get(None, ())
        if '.' in endpoint:
            bp = endpoint.rsplit('.', 1)[0]
            funcs = chain(funcs, self.url_default_functions.get(bp, ()))
        for func in funcs:
            func(endpoint, values)

    def handle_url_build_error(self, error, endpoint, values):
        """在 :meth:`url_for` 方法上处理
        :class:`~werkzeug.routing.BuildError` 类。
        """
        exc_type, exc_value, tb = sys.exc_info()
        for handler in self.url_build_error_handlers:
            try:
                rv = handler(error, endpoint, values)
                if rv is not None:
                    return rv
            except BuildError as e:
                # make error available outside except block (py3)
                error = e

        # At this point we want to reraise the exception.  If the error is
        # still the same one we can reraise it with the original traceback,
        # otherwise we raise it from here.
        if error is exc_value:
            reraise(exc_type, exc_value, tb)
        raise error

    def preprocess_request(self):
        """在请求被调度之前调用本方法。
        调用使用网络应用和当前蓝图注册的
        :attr:`url_value_preprocessors` 属性（如果有任何一个的话）。
        然后调用使用网络应用和蓝图注册的
        :attr:`before_request_funcs` 属性。

        如果任何一个 :meth:`before_request` 处理器返回一个非空值的话，
        返回值都处理成视图函数返回的值，并且
        终止下一步请求处理。
        """

        bp = _request_ctx_stack.top.request.blueprint

        funcs = self.url_value_preprocessors.get(None, ())
        if bp is not None and bp in self.url_value_preprocessors:
            funcs = chain(funcs, self.url_value_preprocessors[bp])
        for func in funcs:
            func(request.endpoint, request.view_args)

        funcs = self.before_request_funcs.get(None, ())
        if bp is not None and bp in self.before_request_funcs:
            funcs = chain(funcs, self.before_request_funcs[bp])
        for func in funcs:
            rv = func()
            if rv is not None:
                return rv

    def process_response(self, response):
        """可以被覆写，是为了响应对象发送到 WSGI 服务器之前
        来修改响应对象。默认情况下，本方法会调用所有
        :meth:`after_request` 方法装饰的函数。

        .. versionchanged:: 0.5
           对于请求执行之后来说， Flask 0.5 版本注册的函数
           都按照注册时的逆序来调用。

        :param response: 参数值是一个 :attr:`response_class` 属性对象。
        :return: 返回一个新响应对象，或返回同一个响应对象，
                 返回的对象都是一个 :attr:`response_class` 属性的实例。
        """
        ctx = _request_ctx_stack.top
        bp = ctx.request.blueprint
        funcs = ctx._after_request_functions
        if bp is not None and bp in self.after_request_funcs:
            funcs = chain(funcs, reversed(self.after_request_funcs[bp]))
        if None in self.after_request_funcs:
            funcs = chain(funcs, reversed(self.after_request_funcs[None]))
        for handler in funcs:
            response = handler(response)
        if not self.session_interface.is_null_session(ctx.session):
            self.session_interface.save_session(self, ctx.session, response)
        return response

    def do_teardown_request(self, exc=_sentinel):
        """请求被调度之后调用本方法，并且
        返回响应，正好都是在请求语境被删除之前完成。

        本方法调用了所有用
        :meth:`teardown_request` 方法装饰的函数，以及调用
        使用 :meth:`Blueprint.teardown_request` 方法装饰的函数。
        如果一个蓝图处理了请求的话，最终，
        :data:`request_tearing_down` 信号被发送出去。

        本方法会被
        :meth:`RequestContext.pop() <flask.ctx.RequestContext.pop>` 方法调用，
        在单元测试期间也许会被推迟到维护访问资源。

        :param exc: 参数值是调度请求时抛出的一个未处理的例外。
                    如果不代入参数值的话，
                    从当前例外信息中来检测。
                    代入到每个释放函数中。

        .. versionchanged:: 0.9
            增加了 ``exc`` 参数。
        """
        if exc is _sentinel:
            exc = sys.exc_info()[1]
        funcs = reversed(self.teardown_request_funcs.get(None, ()))
        bp = _request_ctx_stack.top.request.blueprint
        if bp is not None and bp in self.teardown_request_funcs:
            funcs = chain(funcs, reversed(self.teardown_request_funcs[bp]))
        for func in funcs:
            func(exc)
        request_tearing_down.send(self, exc=exc)

    def do_teardown_appcontext(self, exc=_sentinel):
        """正好在网络应用语境被删除之前调用本方法。

        当处理一个请求时，网络应用语境是在请求语境之后被删除的。
        查看 :meth:`do_teardown_request` 方法。

        本方法调用所有使用
        :meth:`teardown_appcontext` 装饰的函数。然后
        :data:`appcontext_tearing_down` 信号被发送出去。

        本方法被
        :meth:`AppContext.pop() <flask.ctx.AppContext.pop>` 方法调用。

        .. versionadded:: 0.9
        """
        if exc is _sentinel:
            exc = sys.exc_info()[1]
        for func in reversed(self.teardown_appcontext_funcs):
            func(exc)
        appcontext_tearing_down.send(self, exc=exc)

    def app_context(self):
        """建立一个 :class:`~flask.ctx.AppContext` 类。
        使用一个 ``with`` 语句块来推送语境，
        那么在本网络应用上建立一个 :data:`current_app` 数据点。

        当处理一个请求时，以及当运行一个命令行命令时，
        一个网络应用语境是自动被
        :meth:`RequestContext.push() <flask.ctx.RequestContext.push>`
        方法推送出去的。
        除此以外，当处理一个请求时，使用本方法手动建立一个语境。

        示例::

            with app.app_context():
                init_db()

        查看 :doc:`/appcontext` 文档内容。

        .. versionadded:: 0.9
        """
        return AppContext(self)

    def request_context(self, environ):
        """建立一个 :class:`~flask.ctx.RequestContext` 类代表一个
        WSGI 环境。使用一个 ``with`` 语句块来推送语境，
        这样会在这个请求上建立一个 :data:`request` 数据点。

        查看 :doc:`/reqcontext` 文档内容。

        典型来说你不应该在你自己的代码中调用本方法。
        当处理一个请求时，一个请求语境是由
        :meth:`wsgi_app` 方法自动推送出去的。
        使用 :meth:`test_request_context` 方法来
        建立一个环境和语境，而不是用本方法。

        :param environ: 参数值是一个 WSGI 环境。
        """
        return RequestContext(self, environ)

    def test_request_context(self, *args, **kwargs):
        """为一个 WSGI 环境建立一个
        :class:`~flask.ctx.RequestContext` 类，
        其中 WSGI 环境是从给出的值来建立的。
        在单元测试期间，本方法最有用，
        其中你也许想要运行一个函数，该函数使用请求数据，
        而不用调度一个完整的请求。

        查看 :doc:`/reqcontext` 文档内容。

        使用一个 ``with`` 语句块来推送语境，
        这样会在请求上为已建立的环境建立
        :data:`request` 数据点 ::

            with test_request_context(...):
                generate_report()

        当使用终端时，手动推送和删除语境来避免缩进也许更容易 ::

            ctx = app.test_request_context(...)
            ctx.push()
            ...
            ctx.pop()

        获得的参数与 Werkzeug 的
        :class:`~werkzeug.test.EnvironBuilder` 类是一样的，
        使用一些来自网络应用默认参数。
        查看 Werkzeug 文档内容了解更多可用的参数信息。
        Flask 描述的行为罗列在下面。

        :param path: 被请求的 URL 路径。
        :param base_url: 网络应用被服务的基础 URL 地址，与
                         ``path`` 参数值有关。
                         如果没提供参数值的话，参数值从
                         :data:`PREFERRED_URL_SCHEME`、
                         ``subdomain``、
                         :data:`SERVER_NAME` 和
                         :data:`APPLICATION_ROOT` 建立。
        :param subdomain: 追加到 :data:`SERVER_NAME` 中的子域名。
        :param url_scheme: 代替 :data:`PREFERRED_URL_SCHEME`
                           要使用的计划。
        :param data: 请求主体，即可以是一个字符串，也可以是一个
                     键值对儿形成的字典。
        :param json: 如果提供参数值的话，就是序列化的 JSON 对象，
                     并且代入成 ``data`` 参数值。同样
                     ``content_type`` 默认成 ``application/json``
        :param args: 其它代入到
                     :class:`~werkzeug.test.EnvironBuilder` 类中的
                     位置参数。
        :param kwargs: 其它代入到
                       :class:`~werkzeug.test.EnvironBuilder` 类中的
                       关键字参数。
        """
        from flask.testing import make_test_environ_builder

        builder = make_test_environ_builder(self, *args, **kwargs)

        try:
            return self.request_context(builder.get_environ())
        finally:
            builder.close()

    def wsgi_app(self, environ, start_response):
        """真正的 WSGI 网络应用。本方法不会部署在
        :meth:`__call__` 方法中，因此应用中间件
        可以不失去指向网络应用对象。
        不要这样做::

            app = MyMiddleware(app)

        如下做法是更好的思想::

            app.wsgi_app = MyMiddleware(app.wsgi_app)

        然后你依然具有原来的网络应用对象，并且
        可以继续在网络应用对象上调用众多方法。

        .. versionchanged:: 0.7
            对于请求和网络应用语境来说，
            释放事件都会被调用，
            即使出现了一个未处理的错误。
            根据调用期间出现的一个错误，
            其它事件也许不会被调用。
            查看 :ref:`callbacks-and-errors` 文档内容。

        :param environ: 一个 WSGI 环境。
        :param start_response: 一个可调用的接收给启动响应的
                               一个状态代号，
                               一个头部列表，和一个可选例外语境。
        """
        ctx = self.request_context(environ)
        error = None
        try:
            try:
                ctx.push()
                response = self.full_dispatch_request()
            except Exception as e:
                error = e
                response = self.handle_exception(e)
            except:
                error = sys.exc_info()[1]
                raise
            return response(environ, start_response)
        finally:
            if self.should_ignore_error(error):
                error = None
            ctx.auto_pop(error)

    def __call__(self, environ, start_response):
        """WSGI 服务器把 Flask 网络应用对象调用成
        WSGI 网络应用。本方法会调用 :meth:`wsgi_app` 方法，
        这样就可以打包到应用中的中间件里去了。"""
        return self.wsgi_app(environ, start_response)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.name,
        )
