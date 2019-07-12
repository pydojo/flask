.. _deploying-wsgi-standalone:

独立 WSGI 容器
==========================

有许多受欢迎的服务器都是用 Python 写的，其中包含了 WSGI 应用和 HTTP 服务。
这些服务都是在运行时独立提供；你可以在你的网络服务器上把它们设置成代理服务器。
注意如果在运行时遇到问题的话，查看 :ref:`deploying-proxy-setups` 参考文档。

Gunicorn
--------

`Gunicorn`_ 'Green Unicorn' 环保独角兽是为 UNIX 提供的一个 WSGI HTTP 服务器。
它是一种前叉型工作模式，从 Ruby 独角兽项目中移植过来的。
它即支持 `eventlet`_ 也支持 `greenlet`_ 并发库。
运行一个 Flask 网络应用在这种服务器上是非常简单的::

    $ gunicorn myproject:app

`Gunicorn`_ 环保独角兽提供了许多命令行选项 -- 查看命令是 ``gunicorn -h``
例如，要运行一个 Flask 网络应用时使用 4 个工作器进程的命令行选项是
（ ``-w 4`` ），要绑定到本地服务器端口 4000 的选项是（ ``-b 127.0.0.1:4000`` ）::

    $ gunicorn -w 4 -b 127.0.0.1:4000 myproject:app

.. _Gunicorn: https://gunicorn.org/
.. _eventlet: https://eventlet.net/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/

uWSGI
--------

`uWSGI`_ 是用 C 语言写的一个快速网络应用服务器。
它的配置写起来要比环保独角兽更复杂。

运行 `uWSGI HTTP Router`_::

    $ uwsgi --http 127.0.0.1:5000 --module myproject:app

对于一个更优化完的配置，查看 :doc:`configuring uWSGI and NGINX <uwsgi>` 文档。

.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/
.. _uWSGI HTTP Router: https://uwsgi-docs.readthedocs.io/en/latest/HTTP.html#the-uwsgi-http-https-router

Gevent
-------

`Gevent`_ 是一个基于协程的 Python 网络库，它使用了 `greenlet`_ 
在 `libev`_ 事件循环顶层提供一种高层同步 API::

    from gevent.pywsgi import WSGIServer
    from yourapplication import app

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

.. _Gevent: http://www.gevent.org/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/
.. _libev: http://software.schmorp.de/pkg/libev.html

Twisted Web
-----------

`Twisted Web`_ 是使用 `Twisted`_ 移植的网络服务器，
它是一个成熟的、无阻碍事件驱动网络库。
微调网络库含有一项标准的 WSGI 容器，
该容器可以从命令行来进行控制，使用的是 ``twistd`` 工具::

    $ twistd web --wsgi myproject.app

这个示例会运行一个名叫 ``app`` 的 Flask 网络应用，
 ``myproject`` 是该网络应用所在的模块名。

微调网络支持许多旗语和选项，并且 ``twistd`` 工具也是这样工作的；
查看 ``twistd -h`` 帮助文档，以及查看 ``twistd web -h`` 帮助文档了解更多信息。
例如，要在前端运行一个微调网络服务器，
把 ``myproject`` 模块中的网络应用运行在 8080 端口上，命令是::

    $ twistd -n web --port tcp:8080 --wsgi myproject.app

.. _Twisted: https://twistedmatrix.com/
.. _Twisted Web: https://twistedmatrix.com/trac/wiki/TwistedWeb

.. _deploying-proxy-setups:

代理配置
------------

如果你在一个 HTTP 代理后面使用上面这些服务器中的一种来部署你的网络应用的话，
你会需要重写一点头部配置，这样网络应用才能工作。
在 WSGI 环境中常常导致问题的两项配置是 ``REMOTE_ADDR`` 和 ``HTTP_HOST`` 内容。
你可以配置 httpd 时代入这些头部信息，或者你可以在中间件里固化这些信息。
 Werkzeug 移植了一个固化器来解决一些共性的配置工作，
但你也许想写在自己的 WSGI 中间件里，给出具体的配置内容。

这是一个简单的 nginx 配置内容，它在本地服务器 8000 端口上代理了一个网络应用，
配置了合适的头部信息：

.. sourcecode:: nginx

    server {
        listen 80;

        server_name _;

        access_log  /var/log/nginx/access.log;
        error_log  /var/log/nginx/error.log;

        location / {
            proxy_pass         http://127.0.0.1:8000/;
            proxy_redirect     off;

            proxy_set_header   Host                 $host;
            proxy_set_header   X-Real-IP            $remote_addr;
            proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto    $scheme;
        }
    }

如果你的 httpd 没有提供这些头部信息的话，最共性的配置涉及了
从 ``X-Forwarded-Host`` 设置主机，
以及从 ``X-Forwarded-For`` 设置远程地址::

    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

.. admonition:: 信任头部信息

   要记住在一个没有代理配置的情况下使用一种中间件是一项安全问题，
   因为会盲目相信进入的头部信息，而头部信息也许被恶意客户端篡改了。

如果你想从另一个头部中重写头部信息的话，你也许想要使用一个固化器，就像下面这种::

    class CustomProxyFix(object):

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            host = environ.get('HTTP_X_FHOST', '')
            if host:
                environ['HTTP_HOST'] = host
            return self.app(environ, start_response)

    app.wsgi_app = CustomProxyFix(app.wsgi_app)
