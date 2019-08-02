# -*- coding: utf-8 -*-
"""
    flask.blueprints
    ~~~~~~~~~~~~~~~~

    蓝图在 Flask 0.7 版本以后都是部署更大型
    或更可插拔的网络应用推荐的方法。

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""
from functools import update_wrapper
from werkzeug.urls import url_join

from .helpers import _PackageBoundObject, _endpoint_from_view_func


class BlueprintSetupState(object):
    """为使用一个网络应用注册一张蓝图而临时保留对象。
    本类的一个实例就是通过
    :meth:`~flask.Blueprint.make_setup_state` 方法来建立的，
    并且稍后代入到所有注册回调函数中。
    """

    def __init__(self, blueprint, app, options, first_registration):
        #: a reference to the current application
        self.app = app

        #: a reference to the blueprint that created this setup state.
        self.blueprint = blueprint

        #: a dictionary with all options that were passed to the
        #: :meth:`~flask.Flask.register_blueprint` method.
        self.options = options

        #: as blueprints can be registered multiple times with the
        #: application and not everything wants to be registered
        #: multiple times on it, this attribute can be used to figure
        #: out if the blueprint was registered in the past already.
        self.first_registration = first_registration

        subdomain = self.options.get('subdomain')
        if subdomain is None:
            subdomain = self.blueprint.subdomain

        #: The subdomain that the blueprint should be active for, ``None``
        #: otherwise.
        self.subdomain = subdomain

        url_prefix = self.options.get('url_prefix')
        if url_prefix is None:
            url_prefix = self.blueprint.url_prefix
        #: The prefix that should be used for all URLs defined on the
        #: blueprint.
        self.url_prefix = url_prefix

        #: A dictionary with URL defaults that is added to each and every
        #: URL that was defined with the blueprint.
        self.url_defaults = dict(self.blueprint.url_values_defaults)
        self.url_defaults.update(self.options.get('url_defaults', ()))

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """把一个 URL 规则（以及可选的一个视图函数）注册到网络应用的一个辅助方法。
        端点是自动作为蓝图名字前缀的。
        """
        if self.url_prefix is not None:
            if rule:
                rule = '/'.join((
                    self.url_prefix.rstrip('/'), rule.lstrip('/')))
            else:
                rule = self.url_prefix
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, '%s.%s' % (self.blueprint.name, endpoint),
                              view_func, defaults=defaults, **options)


class Blueprint(_PackageBoundObject):
    """表示一张蓝图。
    一张蓝图就是一个用来记录使用
    :class:`~flask.blueprints.BlueprintSetupState` 类
    调用的函数的一个对象，
    稍后把这些函数或其它东西注册到主网络应用上。
    查看 :ref:`blueprints` 文档内容了解更多信息。

    .. versionadded:: 0.7
    """

    warn_on_modifications = False
    _got_registered_once = False

    #: Blueprint local JSON decoder class to use.
    #: Set to ``None`` to use the app's :class:`~flask.app.Flask.json_encoder`.
    json_encoder = None
    #: Blueprint local JSON decoder class to use.
    #: Set to ``None`` to use the app's :class:`~flask.app.Flask.json_decoder`.
    json_decoder = None

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

    def __init__(self, name, import_name, static_folder=None,
                 static_url_path=None, template_folder=None,
                 url_prefix=None, subdomain=None, url_defaults=None,
                 root_path=None):
        _PackageBoundObject.__init__(self, import_name, template_folder,
                                     root_path=root_path)
        self.name = name
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.deferred_functions = []
        if url_defaults is None:
            url_defaults = {}
        self.url_values_defaults = url_defaults

    def record(self, func):
        """当蓝图注册到网络应用时，注册一个被调用的函数。
        被调用的函数所含的状态与
        :meth:`make_setup_state` 方法
        所返回的参数是一样的。
        """
        if self._got_registered_once and self.warn_on_modifications:
            from warnings import warn
            warn(Warning('The blueprint was already registered once '
                         'but is getting modified now.  These changes '
                         'will not show up.'))
        self.deferred_functions.append(func)

    def record_once(self, func):
        """工作起来像 :meth:`record` 方法，
        但把函数打包到另一个函数中，这样确保函数只被调用一次。
        如果蓝图在网络应用上第二次注册的话，
        代入到函数不会被调用。
        """
        def wrapper(state):
            if state.first_registration:
                func(state)
        return self.record(update_wrapper(wrapper, func))

    def make_setup_state(self, app, options, first_registration=False):
        """建立一个 :meth:`~flask.blueprints.BlueprintSetupState`
        方法对象的实例，该对象稍后代入到注册的回调函数中。
        作为子类可以覆写本方法返回一个设置状态的子类。
        """
        return BlueprintSetupState(self, app, options, first_registration)

    def register(self, app, options, first_registration=False):
        """由 :meth:`Flask.register_blueprint` 方法调用注册
        所有已经用网络应用注册在蓝图上的视图函数和回调函数。
        建立一个 :class:`.BlueprintSetupState` 类后
        调用每个 :meth:`record` 方法回调该类。

        :param app: 注册本蓝图的网络应用。
        :param options: 直接来自 :meth:`~Flask.register_blueprint` 方法
                        的关键字参数。
        :param first_registration: 本蓝图是否是第一次注册在网络应用上。
        """
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_registration)

        if self.has_static_folder:
            state.add_url_rule(
                self.static_url_path + '/<path:filename>',
                view_func=self.send_static_file, endpoint='static'
            )

        for deferred in self.deferred_functions:
            deferred(state)

    def route(self, rule, **options):
        """像 :meth:`Flask.route` 方法一样但是给蓝图使用的。
        对于 :func:`url_for` 函数来说，
        端点是用蓝图的名字作前缀。
        """
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """像 :meth:`Flask.add_url_rule` 方法一样但是给蓝图使用的。
        对于 :func:`url_for` 函数来说，
        端点是用蓝图的名字作前缀。
        """
        if endpoint:
            assert '.' not in endpoint, "Blueprint endpoints should not contain dots"
        if view_func and hasattr(view_func, '__name__'):
            assert '.' not in view_func.__name__, "Blueprint view function name should not contain dots"
        self.record(lambda s:
            s.add_url_rule(rule, endpoint, view_func, **options))

    def endpoint(self, endpoint):
        """像 :meth:`Flask.endpoint` 方法一样但是给蓝图使用的。
        本方法中的端点不用蓝图名字作前缀，
        要明确地由本方法的用户来实现。
        如果端点的前缀含有一个 `.` 句号的话，
        会注册到当前蓝图上，否则就是一个网络应用的独立端点。
        """
        def decorator(f):
            def register_endpoint(state):
                state.app.view_functions[endpoint] = f
            self.record_once(register_endpoint)
            return f
        return decorator

    def app_template_filter(self, name=None):
        """注册一个自定义模版过滤器，可用在网络应用范围中。
        像 :meth:`Flask.template_filter` 方法一样但是给蓝图使用的。

        :param name: 可选的过滤器名字，否则使用函数的名字。
        """
        def decorator(f):
            self.add_app_template_filter(f, name=name)
            return f
        return decorator

    def add_app_template_filter(self, f, name=None):
        """注册一个自定义模版过滤器，可用在网络应用范围中。
        像 :meth:`Flask.add_template_filter` 方法一样但是给蓝图使用的。
        工作起来完全像 :meth:`app_template_filter` 方法装饰器一样。

        :param name: 可选的过滤器名字，否则使用函数的名字。
        """
        def register_template(state):
            state.app.jinja_env.filters[name or f.__name__] = f
        self.record_once(register_template)

    def app_template_test(self, name=None):
        """注册一个自定义模版测试，可用在网络应用范围中。
        像 :meth:`Flask.template_test` 方法一样但是给蓝图使用的。

        .. versionadded:: 0.10

        :param name: 可选的测试名字，否则使用函数的名字。
        """
        def decorator(f):
            self.add_app_template_test(f, name=name)
            return f
        return decorator

    def add_app_template_test(self, f, name=None):
        """注册一个自定义模版测试，可用在网络应用范围中。
        像 :meth:`Flask.add_template_test` 方法一样但是给蓝图使用的。
        工作起来完全像 :meth:`app_template_test` 方法装饰器一样。

        .. versionadded:: 0.10

        :param name: 可选的测试名字，否则使用函数的名字。
        """
        def register_template(state):
            state.app.jinja_env.tests[name or f.__name__] = f
        self.record_once(register_template)

    def app_template_global(self, name=None):
        """注册一个自定义模版全局对象，可用在网络应用范围中。
        像 :meth:`Flask.template_global` 方法一样但是给蓝图使用的。

        .. versionadded:: 0.10

        :param name: 可选的全局对象名，否则使用函数的名字。
        """
        def decorator(f):
            self.add_app_template_global(f, name=name)
            return f
        return decorator

    def add_app_template_global(self, f, name=None):
        """注册一个自定义模版全局对象，可用在网络应用范围中。
        像 :meth:`Flask.add_template_global` 方法一样但是给蓝图使用的。
        工作起来完全像 :meth:`app_template_global` 方法装饰器一样。

        .. versionadded:: 0.10

        :param name: 可选的全局对象名，否则使用函数的名字。
        """
        def register_template(state):
            state.app.jinja_env.globals[name or f.__name__] = f
        self.record_once(register_template)

    def before_request(self, f):
        """像 :meth:`Flask.before_request` 方法一样但是给蓝图使用的。
        这个函数只在由蓝图的一个函数处理的每个请求之前被执行。
        """
        self.record_once(lambda s: s.app.before_request_funcs
            .setdefault(self.name, []).append(f))
        return f

    def before_app_request(self, f):
        """像 :meth:`Flask.before_request` 方法一样。
        这样一个函数是在每个请求之前被执行，
        即使请求是蓝图以外的，这个函数也会被执行。
        """
        self.record_once(lambda s: s.app.before_request_funcs
            .setdefault(None, []).append(f))
        return f

    def before_app_first_request(self, f):
        """像 :meth:`Flask.before_first_request` 方法一样。
        这样的一个函数是在到达网络应用的第一个请求之前被执行。
        """
        self.record_once(lambda s: s.app.before_first_request_funcs.append(f))
        return f

    def after_request(self, f):
        """像 :meth:`Flask.after_request` 方法一样但是给蓝图使用的。
        这个函数只在由蓝图的一个函数处理的每个请求之后被执行。
        """
        self.record_once(lambda s: s.app.after_request_funcs
            .setdefault(self.name, []).append(f))
        return f

    def after_app_request(self, f):
        """像 :meth:`Flask.after_request` 方法一样但是给蓝图使用的。
        这样一个函数只在每个请求之后被执行，
        即使请求是蓝图以外的，这个函数也会被执行。
        """
        self.record_once(lambda s: s.app.after_request_funcs
            .setdefault(None, []).append(f))
        return f

    def teardown_request(self, f):
        """像 :meth:`Flask.teardown_request` 方法一样但是给蓝图使用的。
        这个函数只在由蓝图的一个函数处理的释放请求时被执行。
        释放请求函数都在请求语境被删除时被执行，
        甚至当没有实际请求执行时，释放请求函数也都被执行。
        """
        self.record_once(lambda s: s.app.teardown_request_funcs
            .setdefault(self.name, []).append(f))
        return f

    def teardown_app_request(self, f):
        """像 :meth:`Flask.teardown_request` 方法一样但是给蓝图使用的。
        这样一个函数是在释放每个请求时被执行，
        即使请求是蓝图以外的，这个函数也会被执行。
        """
        self.record_once(lambda s: s.app.teardown_request_funcs
            .setdefault(None, []).append(f))
        return f

    def context_processor(self, f):
        """像 :meth:`Flask.context_processor` 方法一样但是给蓝图使用的。
        这个函数只为蓝图处理的请求而执行。
        """
        self.record_once(lambda s: s.app.template_context_processors
            .setdefault(self.name, []).append(f))
        return f

    def app_context_processor(self, f):
        """像 :meth:`Flask.context_processor` 方法一样但是给蓝图使用的。
        这样一个函数为每个请求而执行，
        即使请求是蓝图以外的，这个函数也会被执行。
        """
        self.record_once(lambda s: s.app.template_context_processors
            .setdefault(None, []).append(f))
        return f

    def app_errorhandler(self, code):
        """像 :meth:`Flask.errorhandler` 方法一样但是给蓝图使用的。
        这个处理器是为所有请求而使用的，
        即使请求是蓝图以外的，也可以使用这个处理器。
        """
        def decorator(f):
            self.record_once(lambda s: s.app.errorhandler(code)(f))
            return f
        return decorator

    def url_value_preprocessor(self, f):
        """为本蓝图把一个函数注册成 URL 值处理器。
        在视图函数被调用之前调用处理器，
        并且可以修改提供的 URL 值。
        """
        self.record_once(lambda s: s.app.url_value_preprocessors
            .setdefault(self.name, []).append(f))
        return f

    def url_defaults(self, f):
        """为本蓝图针对 URL 默认值的回调函数。
        回调函数被调用时含有端点和值，
        并且应该更新代入的值。
        """
        self.record_once(lambda s: s.app.url_default_functions
            .setdefault(self.name, []).append(f))
        return f

    def app_url_value_preprocessor(self, f):
        """与 :meth:`url_value_preprocessor` 方法一样但是在蓝图范围中."""
        self.record_once(lambda s: s.app.url_value_preprocessors
            .setdefault(None, []).append(f))
        return f

    def app_url_defaults(self, f):
        """与 :meth:`url_defaults` 方法一样但是在蓝图范围中。."""
        self.record_once(lambda s: s.app.url_default_functions
            .setdefault(None, []).append(f))
        return f

    def errorhandler(self, code_or_exception):
        """只为本蓝图注册一个激活的错误处理器。
        要意识到路由不出现在本地到一个蓝图上，
        所以一个蓝图错误处理器常常不对 404 进行处理，
        除非 404 发生在一个视图函数内部。
        另一个具体情况就是 500 内部服务器错误，
        该错误总会从网络应用中来查找。

        否则工作起来就与 :class:`~flask.Flask` 类对象的
        :meth:`~flask.Flask.errorhandler` 方法装饰器一样了。
        """
        def decorator(f):
            self.record_once(lambda s: s.app._register_error_handler(
                self.name, code_or_exception, f))
            return f
        return decorator

    def register_error_handler(self, code_or_exception, f):
        """是 :meth:`errorhandler` 方法的非装饰器版本，
        类似 :class:`~flask.Flask` 类对象网络应用范围中
        函数的
        :meth:`~flask.Flask.register_error_handler` 方法，
        但是仅限提供给蓝图的错误处理器。

        .. versionadded:: 0.11
        """
        self.record_once(lambda s: s.app._register_error_handler(
            self.name, code_or_exception, f))
