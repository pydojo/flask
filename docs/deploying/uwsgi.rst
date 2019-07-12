.. _deploying-uwsgi:

uWSGI
=====

uWSGI 是在像 `nginx`_、 `lighttpd`_、和 `cherokee`_ 这些服务器上的一种部署选择；
查看 :doc:`fastcgi` 文档和 :doc:`wsgi-standalone` 文档了解其它的选项内容。
要与 uWSGI 协议使用你的 WSGI 应用，你首先需要一个 uWSGI 服务器。
 uWSGI 既是一个协议，也是一个应用服务器；
作为应用服务器可以服务 uWSGI、 FastCGI、和 HTTP 三种协议。

最受欢迎的 uWSGI 服务器就是 `uwsgi`_ 了，我们会使用这个作为本次指导。
确保已经安装完再看如下内容。

.. admonition:: 小心

   一定要确保在你的网络应用中任何一个 ``app.run()`` 调用放在
    ``if __name__ == '__main__':`` 习语块内，或者移到单个文件里。
   只要确保不会被调用即可，否则总会启动一个本地 WSGI 服务器，
   如果我们把网络应用部署到 uWSGI 上的话，这不是我们想要的现象。

使用 uwsgi 启动你的网络应用
----------------------------

`uwsgi` 设计成在 python 模块中找到可调用的 WSGI 操作。

根据 myapp.py 中的一个 Flask 网络应用，使用如下命令：

.. sourcecode:: 命令行

    $ uwsgi -s /tmp/yourapplication.sock --manage-script-name --mount /yourapplication=myapp:app

该 ``--manage-script-name`` 选项会把 ``SCRIPT_NAME`` 的处理移送到 uwsgi 中去，
因为对于这样的处理 uwsgi 更聪明。一起使用的 ``--mount`` 选项指令会把向
 ``/yourapplication`` 发出的请求直接给了 ``myapp:app`` 。
如果你的网络应用在根路径上可以访问的话，你可以使用单个 ``/`` 斜杠代替 ``/yourapplication`` 内容。
 ``myapp`` 指向你的 Flask 网络应用文件名（不需要文件后缀名），
或者指向提供 ``app`` 的模块名。 ``app`` 在你的网络应用中是可调用的
（常常指的就是 ``app = Flask(__name__)`` 这行代码）。

如果你想在一个虚拟环境里部署你的 Flask 网络应用的话，
你也需要增加 ``--virtualenv /path/to/virtual/environment`` 选项到命令行中。
也许你也需要增加一项 ``--plugin python`` 或者 ``--plugin python3`` 到命令行中，
这要依据你的项目所使用的 python 版本了。

配置 nginx
-----------------

一个基础的 flask nginx 配置看起来如下一样::

    location = /yourapplication { rewrite ^ /yourapplication/; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
      include uwsgi_params;
      uwsgi_pass unix:/tmp/yourapplication.sock;
    }

这种配置把网络应用绑定到 ``/yourapplication`` 路径上。
如果你想在 URL 网址根路径中显示它，配置起来就更简单一点儿了::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/yourapplication.sock;
    }

.. _nginx: https://nginx.org/
.. _lighttpd: https://www.lighttpd.net/
.. _cherokee: http://cherokee-project.com/
.. _uwsgi: https://uwsgi-docs.readthedocs.io/
