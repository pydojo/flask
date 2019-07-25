增加 HTTP 方法覆写
============================

有的 HTTP 代理不支持任意 HTTP 方法，或者不支持更新的 HTTP 方法
 (例如， PATCH 这个 HTTP 方法)。在这种情况下，要代理 HTTP 方法，
可能要通过另一种完全违背协议的 HTTP 方法来实现了。

这种方法是通过让客户端来实现一个 HTTP POST 请求方法，并且设置
 ``X-HTTP-Method-Override`` 头部信息以及设置值给要使用的
 HTTP 方法 (例如， ``PATCH``)。

用一个 HTTP 中间件就容易实现::

    class HTTPMethodOverrideMiddleware(object):
        allowed_methods = frozenset([
            'GET',
            'HEAD',
            'POST',
            'DELETE',
            'PUT',
            'PATCH',
            'OPTIONS'
        ])
        bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
            if method in self.allowed_methods:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
            if method in self.bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
            return self.app(environ, start_response)

要用 Flask 来做这件事，所需要的全部代码就是如下几行::

    from flask import Flask

    app = Flask(__name__)
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
