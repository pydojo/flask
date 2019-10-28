# -*- coding: utf-8 -*-
"""
    flask.cli
    ~~~~~~~~~

    一个直接运行 Flask 网络应用的命令行程序。

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

import ast
import inspect
import os
import platform
import re
import ssl
import sys
import traceback
from functools import update_wrapper
from operator import attrgetter
from threading import Lock, Thread

import click
from werkzeug.utils import import_string

from . import __version__
from ._compat import getargspec, itervalues, reraise, text_type
from .globals import current_app
from .helpers import get_debug_flag, get_env, get_load_dotenv

try:
    import dotenv
except ImportError:
    dotenv = None


class NoAppException(click.UsageError):
    """如果无法发现一个网络应用或无法加载一个网络应用就抛出这个例外."""


def find_best_app(script_info, module):
    """根据一个模块实例尝试找到模块中最可能的网络应用，
    或者抛出一个例外。
    """
    from . import Flask

    # Search for the most common names first.
    for attr_name in ('app', 'application'):
        app = getattr(module, attr_name, None)

        if isinstance(app, Flask):
            return app

    # Otherwise find the only object that is a Flask instance.
    matches = [
        v for v in itervalues(module.__dict__) if isinstance(v, Flask)
    ]

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            'Detected multiple Flask applications in module "{module}". Use '
            '"FLASK_APP={module}:name" to specify the correct '
            'one.'.format(module=module.__name__)
        )

    # Search for app factory functions.
    for attr_name in ('create_app', 'make_app'):
        app_factory = getattr(module, attr_name, None)

        if inspect.isfunction(app_factory):
            try:
                app = call_factory(script_info, app_factory)

                if isinstance(app, Flask):
                    return app
            except TypeError:
                if not _called_with_wrong_args(app_factory):
                    raise
                raise NoAppException(
                    'Detected factory "{factory}" in module "{module}", but '
                    'could not call it without arguments. Use '
                    '"FLASK_APP=\'{module}:{factory}(args)\'" to specify '
                    'arguments.'.format(
                        factory=attr_name, module=module.__name__
                    )
                )

    raise NoAppException(
        'Failed to find Flask application or factory in module "{module}". '
        'Use "FLASK_APP={module}:name to specify one.'.format(
            module=module.__name__
        )
    )


def call_factory(script_info, app_factory, arguments=()):
    """获得一个网络应用工厂，一个 ``script_info`` 对象和
    可选的一个多个参数组成的元组形式。
    检查本函数所获得的参数中是否有 ``script_info`` 参数，
    然后调用 ``app_factory`` 参数值。
    """
    args_spec = getargspec(app_factory)
    arg_names = args_spec.args
    arg_defaults = args_spec.defaults

    if 'script_info' in arg_names:
        return app_factory(*arguments, script_info=script_info)
    elif arguments:
        return app_factory(*arguments)
    elif not arguments and len(arg_names) == 1 and arg_defaults is None:
        return app_factory(script_info)

    return app_factory()


def _called_with_wrong_args(factory):
    """检查调用一个函数是否抛出一个 ``TypeError`` 例外，
    因为调用失败或者工厂函数中某行代码抛出错误。

    :param factory: 要调用的工厂函数。
    :return: 如果调用失败返回 ``True`` 值。
    """
    tb = sys.exc_info()[2]

    try:
        while tb is not None:
            if tb.tb_frame.f_code is factory.__code__:
                # in the factory, it was called successfully
                return False

            tb = tb.tb_next

        # didn't reach the factory
        return True
    finally:
        del tb


def find_app_by_string(script_info, module, app_name):
    """检查给出的字符串是否是一个变量名，还是一个函数名。
    如果字符串是一个函数名的话，本函数检查具体的函数参数后，
    是否得到一个 ``script_info`` 参数，并且用合适的参数来调用函数。
    """
    from flask import Flask
    match = re.match(r'^ *([^ ()]+) *(?:\((.*?) *,? *\))? *$', app_name)

    if not match:
        raise NoAppException(
            '"{name}" is not a valid variable name or function '
            'expression.'.format(name=app_name)
        )

    name, args = match.groups()

    try:
        attr = getattr(module, name)
    except AttributeError as e:
        raise NoAppException(e.args[0])

    if inspect.isfunction(attr):
        if args:
            try:
                args = ast.literal_eval('({args},)'.format(args=args))
            except (ValueError, SyntaxError)as e:
                raise NoAppException(
                    'Could not parse the arguments in '
                    '"{app_name}".'.format(e=e, app_name=app_name)
                )
        else:
            args = ()

        try:
            app = call_factory(script_info, attr, args)
        except TypeError as e:
            if not _called_with_wrong_args(attr):
                raise

            raise NoAppException(
                '{e}\nThe factory "{app_name}" in module "{module}" could not '
                'be called with the specified arguments.'.format(
                    e=e, app_name=app_name, module=module.__name__
                )
            )
    else:
        app = attr

    if isinstance(app, Flask):
        return app

    raise NoAppException(
        'A valid Flask application was not obtained from '
        '"{module}:{app_name}".'.format(
            module=module.__name__, app_name=app_name
        )
    )


def prepare_import(path):
    """根据一个文件名来尝试计算 Python 路径，
    把文件名加入到搜索路径中后，返回期望的实际模块名。
    """
    path = os.path.realpath(path)

    fname, ext = os.path.splitext(path)
    if ext == '.py':
        path = fname

    if os.path.basename(path) == '__init__':
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, '__init__.py')):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return '.'.join(module_name[::-1])


def locate_app(script_info, module_name, app_name, raise_if_not_found=True):
    __traceback_hide__ = True

    try:
        __import__(module_name)
    except ImportError:
        # Reraise the ImportError if it occurred within the imported module.
        # Determine this by checking whether the trace has a depth > 1.
        if sys.exc_info()[-1].tb_next:
            raise NoAppException(
                'While importing "{name}", an ImportError was raised:'
                '\n\n{tb}'.format(name=module_name, tb=traceback.format_exc())
            )
        elif raise_if_not_found:
            raise NoAppException(
                'Could not import "{name}".'.format(name=module_name)
            )
        else:
            return

    module = sys.modules[module_name]

    if app_name is None:
        return find_best_app(script_info, module)
    else:
        return find_app_by_string(script_info, module, app_name)


def get_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    import werkzeug
    message = (
        'Python %(python)s\n'
        'Flask %(flask)s\n'
        'Werkzeug %(werkzeug)s'
    )
    click.echo(message % {
        'python': platform.python_version(),
        'flask': __version__,
        'werkzeug': werkzeug.__version__,
    }, color=ctx.color)
    ctx.exit()


version_option = click.Option(
    ['--version'],
    help='Show the flask version',
    expose_value=False,
    callback=get_version,
    is_flag=True,
    is_eager=True
)


class DispatchingApp(object):
    """调度给一个 Flask 网络应用的特殊应用，
    在后端线程中通过应用名来导入。如果发生一个错误的话，
    会记录下来，并且显示成 WSGI 处理中的部分内容，
    在 Werkzeug 调试器环境里意味着会显示在浏览器中。
    """

    def __init__(self, loader, use_eager_loading=False):
        self.loader = loader
        self._app = None
        self._lock = Lock()
        self._bg_loading_exc_info = None
        if use_eager_loading:
            self._load_unlocked()
        else:
            self._load_in_background()

    def _load_in_background(self):
        def _load_app():
            __traceback_hide__ = True
            with self._lock:
                try:
                    self._load_unlocked()
                except Exception:
                    self._bg_loading_exc_info = sys.exc_info()
        t = Thread(target=_load_app, args=())
        t.start()

    def _flush_bg_loading_exception(self):
        __traceback_hide__ = True
        exc_info = self._bg_loading_exc_info
        if exc_info is not None:
            self._bg_loading_exc_info = None
            reraise(*exc_info)

    def _load_unlocked(self):
        __traceback_hide__ = True
        self._app = rv = self.loader()
        self._bg_loading_exc_info = None
        return rv

    def __call__(self, environ, start_response):
        __traceback_hide__ = True
        if self._app is not None:
            return self._app(environ, start_response)
        self._flush_bg_loading_exception()
        with self._lock:
            if self._app is not None:
                rv = self._app
            else:
                rv = self._load_unlocked()
            return rv(environ, start_response)


class ScriptInfo(object):
    """用来处理 Flask 网络应用的辅助对象。
    常常不需要与本类进行互动，因为本类是在调度给 click 库时的内部用法。
    在 Flask 以后的版本中本类建立的对象最可能扮演一个更重要的角色。
    典型情况下，本类的对象是通过 :class:`FlaskGroup` 类自动建立的，
    但你也可以手动来建立后代入成 click 对象一样。
    """

    def __init__(self, app_import_path=None, create_app=None,
                 set_debug_flag=True):
        #: Optionally the import path for the Flask application.
        self.app_import_path = app_import_path or os.environ.get('FLASK_APP')
        #: Optionally a function that is passed the script info to create
        #: the instance of the application.
        self.create_app = create_app
        #: A dictionary with arbitrary data that can be associated with
        #: this script info.
        self.data = {}
        self.set_debug_flag = set_debug_flag
        self._loaded_app = None

    def load_app(self):
        """加载 Flask 网络应用（假如还没加载的话）后返回网络应用。
        多次调用本方法只会产生已加载的网络应用返回效果。
        """
        __traceback_hide__ = True

        if self._loaded_app is not None:
            return self._loaded_app

        app = None

        if self.create_app is not None:
            app = call_factory(self, self.create_app)
        else:
            if self.app_import_path:
                path, name = (re.split(r':(?![\\/])', self.app_import_path, 1) + [None])[:2]
                import_name = prepare_import(path)
                app = locate_app(self, import_name, name)
            else:
                for path in ('wsgi.py', 'app.py'):
                    import_name = prepare_import(path)
                    app = locate_app(self, import_name, None,
                                     raise_if_not_found=False)

                    if app:
                        break

        if not app:
            raise NoAppException(
                'Could not locate a Flask application. You did not provide '
                'the "FLASK_APP" environment variable, and a "wsgi.py" or '
                '"app.py" module was not found in the current directory.'
            )

        if self.set_debug_flag:
            # Update the app's debug flag through the descriptor so that
            # other values repopulate as well.
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app


pass_script_info = click.make_pass_decorator(ScriptInfo, ensure=True)


def with_appcontext(f):
    """打包一个回调函数，这样才能确保带有脚本的网络应用语境能够执行该函数。
    如果回调函数都直接注册到 ``app.cli`` 对象上的话，
    那么这些回调函数都默认使用本函数来进行打包，除非禁用本函数。
    """
    @click.pass_context
    def decorator(__ctx, *args, **kwargs):
        with __ctx.ensure_object(ScriptInfo).load_app().app_context():
            return __ctx.invoke(f, *args, **kwargs)
    return update_wrapper(decorator, f)


class AppGroup(click.Group):
    """本类工作起来就像正规的 click 库的 :class:`~click.Group` 类一样，
    但区别是本类改变了 :meth:`command` 方法装饰器的行为，
    所以才能够自动地把函数打包到 :func:`with_appcontext` 函数中。

    别与 :class:`FlaskGroup` 类搞混了。
    """

    def command(self, *args, **kwargs):
        """本方法与 :class:`click.Group` 类的同名方法工作完全一样，
        但本方法把回调函数打包到 :func:`with_appcontext` 函数中，
        除非通过代入 ``with_appcontext=False`` 参数值后禁用本方法。
        """
        wrap_for_ctx = kwargs.pop('with_appcontext', True)
        def decorator(f):
            if wrap_for_ctx:
                f = with_appcontext(f)
            return click.Group.command(self, *args, **kwargs)(f)
        return decorator

    def group(self, *args, **kwargs):
        """本方法与 :class:`click.Group` 类的同名方法工作完全一样，
        但本方法默认默认分组到 :class:`AppGroup` 类上。
        """
        kwargs.setdefault('cls', AppGroup)
        return click.Group.group(self, *args, **kwargs)


class FlaskGroup(AppGroup):
    """本类是 :class:`AppGroup` 类的特殊子类，
    支持从配置完的 Flask 网络应用中加载更多命令。
    正常情况，一名开发者不用与本类进行互动，
    但本类有一些非常高级的用法，针对本类的实例来说是有意义的。

    对于为什么有意义查看 :ref:`custom-scripts` 参考文档。

    :param add_default_commands: 如果这个参数值是 `True` 的话，
                                 默认运行加入的终端命令。
    :param add_version_option: 增加 ``--version`` 命令选项。
    :param create_app: 一种可选的回调功能，脚本信息代入后返回加载的网络应用。
    :param load_dotenv: 加载最近的 :file:`.env` 文件和 :file:`.flaskenv` 文件，
                        用来设置环境变量。也会把工作目录变成含有找到的第一个文件所在目录。
    :param set_debug_flag: 根据激活的环境设置网络应用的调试旗语。

    .. versionchanged:: 1.0
        如果安装了 python-dotenv 的话，会使用 python-dotenv 来加载
        来自 :file:`.env` 文件和 :file:`.flaskenv` 文件中的环境变量。
    """

    def __init__(self, add_default_commands=True, create_app=None,
                 add_version_option=True, load_dotenv=True,
                 set_debug_flag=True, **extra):
        params = list(extra.pop('params', None) or ())

        if add_version_option:
            params.append(version_option)

        AppGroup.__init__(self, params=params, **extra)
        self.create_app = create_app
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        if add_default_commands:
            self.add_command(run_command)
            self.add_command(shell_command)
            self.add_command(routes_command)

        self._loaded_plugin_commands = False

    def _load_plugin_commands(self):
        if self._loaded_plugin_commands:
            return
        try:
            import pkg_resources
        except ImportError:
            self._loaded_plugin_commands = True
            return

        for ep in pkg_resources.iter_entry_points('flask.commands'):
            self.add_command(ep.load(), ep.name)
        self._loaded_plugin_commands = True

    def get_command(self, ctx, name):
        self._load_plugin_commands()

        # We load built-in commands first as these should always be the
        # same no matter what the app does.  If the app does want to
        # override this it needs to make a custom instance of this group
        # and not attach the default commands.
        #
        # This also means that the script stays functional in case the
        # application completely fails.
        rv = AppGroup.get_command(self, ctx, name)
        if rv is not None:
            return rv

        info = ctx.ensure_object(ScriptInfo)
        try:
            rv = info.load_app().cli.get_command(ctx, name)
            if rv is not None:
                return rv
        except NoAppException:
            pass

    def list_commands(self, ctx):
        self._load_plugin_commands()

        # The commands available is the list of both the application (if
        # available) plus the builtin commands.
        rv = set(click.Group.list_commands(self, ctx))
        info = ctx.ensure_object(ScriptInfo)
        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except Exception:
            # Here we intentionally swallow all exceptions as we don't
            # want the help page to break if the app does not exist.
            # If someone attempts to use the command we try to create
            # the app again and this will give us the error.
            # However, we will not do so silently because that would confuse
            # users.
            traceback.print_exc()
        return sorted(rv)

    def main(self, *args, **kwargs):
        # Set a global flag that indicates that we were invoked from the
        # command line interface. This is detected by Flask.run to make the
        # call into a no-op. This is necessary to avoid ugly errors when the
        # script that is loaded here also attempts to start a server.
        os.environ['FLASK_RUN_FROM_CLI'] = 'true'

        if get_load_dotenv(self.load_dotenv):
            load_dotenv()

        obj = kwargs.get('obj')

        if obj is None:
            obj = ScriptInfo(create_app=self.create_app,
                             set_debug_flag=self.set_debug_flag)

        kwargs['obj'] = obj
        kwargs.setdefault('auto_envvar_prefix', 'FLASK')
        return super(FlaskGroup, self).main(*args, **kwargs)


def _path_is_ancestor(path, other):
    """得到 ``other`` 参数值后，去掉 ``path`` 参数值长度。
    然后加入到 ``path`` 参数值中。
    如果结果是原来的值的话， ``path`` 参数值就是``other`` 参数值的前身。
    """
    return os.path.join(path, other[len(path):].lstrip(os.sep)) == other


def load_dotenv(path=None):
    """加载 "dotenv" 文件达到提前设置环境变量的效果。

    如果已经设置了一个环境变量的话，不会覆写环境变量，
    所以列表中先找到的文件都优先于后找到的文件。

    把当前工作目录变成找到的第一个文件所在目录，
    文件都假设在项目目录顶层位置中，并且是导入
    本地包应该有的 Python 路径上。

    如果没有安装 `python-dotenv`_ 的话，本函数就没有效果。

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: 在本参数值位置上加载文件，而不是搜索路径。
    :return: 如果一个文件加载完毕，返回值是 ``True``

    .. versionadded:: 1.0
    """
    if dotenv is None:
        if path or os.path.isfile('.env') or os.path.isfile('.flaskenv'):
            click.secho(
                ' * Tip: There are .env or .flaskenv files present.'
                ' Do "pip install python-dotenv" to use them.',
                fg='yellow')
        return

    if path is not None:
        return dotenv.load_dotenv(path)

    new_dir = None

    for name in ('.env', '.flaskenv'):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path)

    if new_dir and os.getcwd() != new_dir:
        os.chdir(new_dir)

    return new_dir is not None  # at least one file was located and loaded


def show_server_banner(env, debug, app_import_path, eager_loading):
    """在服务器第一次运行时显示额外的启动消息，
    忽略重载器。
    """
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return

    if app_import_path is not None:
        message = ' * Serving Flask app "{0}"'.format(app_import_path)

        if not eager_loading:
            message += ' (lazy loading)'

        click.echo(message)

    click.echo(' * Environment: {0}'.format(env))

    if env == 'production':
        click.secho(
            '   WARNING: Do not use the development server in a production'
            ' environment.', fg='red')
        click.secho('   Use a production WSGI server instead.', dim=True)

    if debug is not None:
        click.echo(' * Debug mode: {0}'.format('on' if debug else 'off'))


class CertParamType(click.ParamType):
    """为 ``--cert`` 命令行选项增加的 Click 库支持。
    对一个 :class:`~ssl.SSLContext` 类对象来说，
    允许是一个存在的文件、或是字符串 ``'adhoc'``，
    又或是允许一项导入。
    """

    name = 'path'

    def __init__(self):
        self.path_type = click.Path(
            exists=True, dir_okay=False, resolve_path=True)

    def convert(self, value, param, ctx):
        try:
            return self.path_type(value, param, ctx)
        except click.BadParameter:
            value = click.STRING(value, param, ctx).lower()

            if value == 'adhoc':
                try:
                    import OpenSSL
                except ImportError:
                    raise click.BadParameter(
                        'Using ad-hoc certificates requires pyOpenSSL.',
                        ctx, param)

                return value

            obj = import_string(value, silent=True)

            if sys.version_info < (2, 7, 9):
                if obj:
                    return obj
            else:
                if isinstance(obj, ssl.SSLContext):
                    return obj

            raise


def _validate_key(ctx, param, value):
    """当 ``--cert`` 以一个文件方式使用时，
    必须描述一个 ``--key`` 命令行选项。
    如果需要的话，把 ``cert`` 参数描述成
    一个 ``(cert, key)`` 证书钥匙对儿形式。
    """
    cert = ctx.params.get('cert')
    is_adhoc = cert == 'adhoc'

    if sys.version_info < (2, 7, 9):
        is_context = cert and not isinstance(cert, (text_type, bytes))
    else:
        is_context = isinstance(cert, ssl.SSLContext)

    if value is not None:
        if is_adhoc:
            raise click.BadParameter(
                'When "--cert" is "adhoc", "--key" is not used.',
                ctx, param)

        if is_context:
            raise click.BadParameter(
                'When "--cert" is an SSLContext object, "--key is not used.',
                ctx, param)

        if not cert:
            raise click.BadParameter(
                '"--cert" must also be specified.',
                ctx, param)

        ctx.params['cert'] = cert, value

    else:
        if cert and not (is_adhoc or is_context):
            raise click.BadParameter(
                'Required when using "--cert".',
                ctx, param)

    return value


@click.command('run', short_help='Run a development server.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--cert', type=CertParamType(),
              help='Specify a certificate file to use HTTPS.')
@click.option('--key',
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              callback=_validate_key, expose_value=False,
              help='The key file to use when specifying a certificate.')
@click.option('--reload/--no-reload', default=None,
              help='Enable or disable the reloader. By default the reloader '
              'is active if debug is enabled.')
@click.option('--debugger/--no-debugger', default=None,
              help='Enable or disable the debugger. By default the debugger '
              'is active if debug is enabled.')
@click.option('--eager-loading/--lazy-loader', default=None,
              help='Enable or disable eager loading. By default eager '
              'loading is enabled if the reloader is disabled.')
@click.option('--with-threads/--without-threads', default=True,
              help='Enable or disable multithreading.')
@pass_script_info
def run_command(info, host, port, reload, debugger, eager_loading,
                with_threads, cert):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    debug = get_debug_flag()

    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    if eager_loading is None:
        eager_loading = not reload

    show_server_banner(get_env(), debug, info.app_import_path, eager_loading)
    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    from werkzeug.serving import run_simple
    run_simple(host, port, app, use_reloader=reload, use_debugger=debugger,
               threaded=with_threads, ssl_context=cert)


@click.command('shell', short_help='Run a shell in the app context.')
@with_appcontext
def shell_command():
    """Run an interactive Python shell in the context of a given
    Flask application.  The application will populate the default
    namespace of this shell according to it's configuration.

    This is useful for executing small snippets of management code
    without having to manually configure the application.
    """
    import code
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app
    banner = 'Python %s on %s\nApp: %s [%s]\nInstance: %s' % (
        sys.version,
        sys.platform,
        app.import_name,
        app.env,
        app.instance_path,
    )
    ctx = {}

    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup, 'r') as f:
            eval(compile(f.read(), startup, 'exec'), ctx)

    ctx.update(app.make_shell_context())

    code.interact(banner=banner, local=ctx)


@click.command('routes', short_help='Show the routes for the app.')
@click.option(
    '--sort', '-s',
    type=click.Choice(('endpoint', 'methods', 'rule', 'match')),
    default='endpoint',
    help=(
        'Method to sort routes by. "match" is the order that Flask will match '
        'routes when dispatching a request.'
    )
)
@click.option(
    '--all-methods',
    is_flag=True,
    help="Show HEAD and OPTIONS methods."
)
@with_appcontext
def routes_command(sort, all_methods):
    """Show all registered routes with endpoints and methods."""

    rules = list(current_app.url_map.iter_rules())
    if not rules:
        click.echo('No routes were registered.')
        return

    ignored_methods = set(() if all_methods else ('HEAD', 'OPTIONS'))

    if sort in ('endpoint', 'rule'):
        rules = sorted(rules, key=attrgetter(sort))
    elif sort == 'methods':
        rules = sorted(rules, key=lambda rule: sorted(rule.methods))

    rule_methods = [
        ', '.join(sorted(rule.methods - ignored_methods)) for rule in rules
    ]

    headers = ('Endpoint', 'Methods', 'Rule')
    widths = (
        max(len(rule.endpoint) for rule in rules),
        max(len(methods) for methods in rule_methods),
        max(len(rule.rule) for rule in rules),
    )
    widths = [max(len(h), w) for h, w in zip(headers, widths)]
    row = '{{0:<{0}}}  {{1:<{1}}}  {{2:<{2}}}'.format(*widths)

    click.echo(row.format(*headers).strip())
    click.echo(row.format(*('-' * width for width in widths)))

    for rule, methods in zip(rules, rule_methods):
        click.echo(row.format(rule.endpoint, methods, rule.rule).rstrip())


cli = FlaskGroup(help="""\
A general utility script for Flask applications.

Provides commands from Flask, extensions, and the application. Loads the
application defined in the FLASK_APP environment variable, or from a wsgi.py
file. Setting the FLASK_ENV environment variable to 'development' will enable
debug mode.

\b
  {prefix}{cmd} FLASK_APP=hello.py
  {prefix}{cmd} FLASK_ENV=development
  {prefix}flask run
""".format(
    cmd='export' if os.name == 'posix' else 'set',
    prefix='$ ' if os.name == 'posix' else '> '
))


def main(as_module=False):
    args = sys.argv[1:]

    if as_module:
        this_module = 'flask'

        if sys.version_info < (2, 7):
            this_module += '.cli'

        name = 'python -m ' + this_module

        # Python rewrites "python -m flask" to the path to the file in argv.
        # Restore the original command so that the reloader works.
        sys.argv = ['-m', this_module] + args
    else:
        name = None

    cli.main(args=args, prog_name=name)


if __name__ == '__main__':
    main(as_module=True)
