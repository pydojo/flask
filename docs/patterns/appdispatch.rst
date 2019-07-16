.. _app-dispatch:

网络应用调度
=======================

网络应用调度是把多个 Flask 网络应用在 WSGI 层上组合在一起的过程。
你不仅只组合 Flask 网络应用，而且还可以把任何一种 WSGI 网络应用组合在一起。
如果你愿意的话，调度技术让你在同一个解释器中一个接着一个地运行
一个 Django 和 Flask 网络应用。调度之所以有用是根据网络应用内部是如何工作的。

来自 :ref:`module approach <larger-applications>` 参考文档的基础差异是
在调度中你正在运行同一个或不同的 Flask 网络应用，它们之间都是完全相互隔离的。
它们运行不同的配置以及都被调度到 WSGI 层上。


与本文档一起工作
--------------------------

众多技术中的每项技术，以及如下示例都要以一个 ``application`` 对象作为结果，
这样才可以与任何一种 WSGI 服务器一起运行。
对于生产来说，查看 :ref:`deployment` 部署文档内容。
对于开发来说， Werkzeug 库中的 :func:`werkzeug.serving.run_simple` 
函数给 development 环境变量提供了一个内置服务器::

    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, application, use_reloader=True)

注意 :func:`run_simple <werkzeug.serving.run_simple>` 这个函数，它不是
为了用在生产中的。生产中使用参考 :ref:`full-blown WSGI server <deployment>` 内容。

要使用交互式调试器，调试必须开启在网络应用和这个简单服务器上。
这里有一个 "hello world" 例子所带的调试和
:func:`run_simple <werkzeug.serving.run_simple>` 函数用法如下::

    from flask import Flask
    from werkzeug.serving import run_simple

    app = Flask(__name__)
    app.debug = True

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    if __name__ == '__main__':
        run_simple('localhost', 5000, app,
                   use_reloader=True, use_debugger=True, use_evalex=True)


把网络应用组合起来
----------------------

如果你有许多分离开来的许多网络应用的话，而且你还想让它们一个接着一个地工作在
相同的 Python 解释器进程中，那么你可以获得
:class:`werkzeug.wsgi.DispatcherMiddleware` 类的优势来实现。
这里的思路是每个 Flask 网络应用是一个合法的 WSGI 应用，并且它们都要
通过调度器中间件来进行组合，这样形成的一个更大型的网络应用才可以根据前缀顺序被调度。

例如，你可以有你的的主网络应用，运行在 ``/`` 路径上，
然后你的后端接口运行在 ``/backend`` 路径上::

    from werkzeug.wsgi import DispatcherMiddleware
    from frontend_app import application as frontend
    from backend_app import application as backend

    application = DispatcherMiddleware(frontend, {
        '/backend':     backend
    })


通过子域来调度
---------------------

有时候你也许想要使用同一个网络应用的多个实例，每个实例都有不同的配置。
假设网络应用建立在一个函数中，然后你可以调用那个函数来实例化，
这是非常容易部署的。为了开发你的网络应用来支持在函数中建立新的实例，
看一下 :ref:`app-factories` 工厂模式参考文档。

一个非常共性的例子会是每个子域名都建立一个网络应用。
对于你配置的实例来说，你的浏览器要为所有子域名调度全部到你的网络应用的请求，
并且你接下来使用子域名信息来建立具体用户的实例。
一旦你的服务器配置完监听所有子域名，那么你可以使用一个非常容易的 WSGI 应用
来实现动态网络应用的建立。

对于抽象来说完美的层次就是 WSGI 层。你写一个你自己的 WSGI 应用，
让它来查看进入的请求后，代表请求访问你的 Flask 网络应用。
如果网络应用不存在的话，就会动态地被建立并存储下来::

    from threading import Lock

    class SubdomainDispatcher(object):

        def __init__(self, domain, create_app):
            self.domain = domain
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, host):
            host = host.split(':')[0]
            assert host.endswith(self.domain), 'Configuration error'
            subdomain = host[:-len(self.domain)].rstrip('.')
            with self.lock:
                app = self.instances.get(subdomain)
                if app is None:
                    app = self.create_app(subdomain)
                    self.instances[subdomain] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(environ['HTTP_HOST'])
            return app(environ, start_response)


这种调度器稍厚可以使用成如下这种::

    from myapplication import create_app, get_user_for_subdomain
    from werkzeug.exceptions import NotFound

    def make_app(subdomain):
        user = get_user_for_subdomain(subdomain)
        if user is None:
            # if there is no user for that subdomain we still have
            # to return a WSGI application that handles that request.
            # We can then just return the NotFound() exception as
            # application which will render a default 404 page.
            # You might also redirect the user to the main page then
            return NotFound()

        # otherwise create the application for the specific user
        return create_app(user)

    application = SubdomainDispatcher('example.com', make_app)


通过路径来调度
----------------

在 URL 地址上通过一个路径来调度是非常相似的做法。
不是看 ``Host`` 头部来弄清楚子域名，而是直接看
请求路径到第一个斜杠::

    from threading import Lock
    from werkzeug.wsgi import pop_path_info, peek_path_info

    class PathDispatcher(object):

        def __init__(self, default_app, create_app):
            self.default_app = default_app
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, prefix):
            with self.lock:
                app = self.instances.get(prefix)
                if app is None:
                    app = self.create_app(prefix)
                    if app is not None:
                        self.instances[prefix] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(peek_path_info(environ))
            if app is not None:
                pop_path_info(environ)
            else:
                app = self.default_app
            return app(environ, start_response)

路径调度和子域调度最大的区别是，如果建造函数返回 ``None`` 的话，
路径调度回调了另一个网络应用::

    from myapplication import create_app, default_app, get_user_for_prefix

    def make_app(prefix):
        user = get_user_for_prefix(prefix)
        if user is not None:
            return create_app(user)

    application = PathDispatcher(default_app, make_app)
