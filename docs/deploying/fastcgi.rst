.. _deploying-fastcgi:

FastCGI
=======

FastCGI 是像 `nginx`_、 `lighttpd`_、和 `cherokee`_ 服务器上的一种配置选项；
查看 :doc:`uwsgi` 文档和 :doc:`wsgi-standalone` 文档了解其它选项。
上面中的任何一种服务器要使用你的 WSGI 应用都先需要一个 FastCGI 服务器才可以。
最受欢迎的一个就是 `flup`_ ，我们会使用此项作为指导。确保已经安装上后在看下面内容。

.. admonition:: 小心

   一定要确保在你的网络应用中任何一个 ``app.run()`` 调用放在
    ``if __name__ == '__main__':`` 习语块内，或者移到单个文件里。
   只要确保不会被调用即可，因为总会启动一个本地 WSGI 服务器，
   如果我们把网络应用部署到 FastCGI 上的话，这不是我们想要的现象。

建立一个 `.fcgi` 文件
-----------------------

首先你需要建立 FastCGI 服务器文件。此处我们叫它 `yourapplication.fcgi`::

    #!/usr/bin/python
    from flup.server.fcgi import WSGIServer
    from yourapplication import app

    if __name__ == '__main__':
        WSGIServer(app).run()

这就足以让 Apache 工作起来了。不管如何做到的， nginx 和老版本的 lighttpd 都
需要一个插槽来明确地代入到与 FastCGI 服务器通信中。
这样你需要把路径代入到插槽中 :class:`~flup.server.fcgi.WSGIServer`::

    WSGIServer(application, bindAddress='/path/to/fcgi.sock').run()

路径必须要与你定义在服务器配置中的路径完全一样。

把 :file:`yourapplication.fcgi` 文件保存在你可以再次找到的地方。
保存位置要在 :file:`/var/www/yourapplication` 文件路径里，或者类似的其它位置。

确保把文件设置成可执行权限，这样服务器才可以执行它：

.. sourcecode:: 增加执行权限

    $ chmod +x /var/www/yourapplication/yourapplication.fcgi

配置 Apache
------------------

上面的例子对于一个基本的 Apache 部署来说已经足够好了，
但你的 `.fcgi` 文件会显示在你的网络应用 URL 网址中。例如，
``example.com/yourapplication.fcgi/news/`` 这种现象。
这里也有几个方法来配置你的网络应用，这样 `.fcgi` 文件就不会显示在网址中了。
一种完美的方法就是使用 ScriptAlias 和 SetHandler 配置指令来把请求指向到
 FastCGI 服务器。如下的示例使用了 FastCgiServer 来启动应用的 5 个实例，
这样会处理所有进入的请求::

    LoadModule fastcgi_module /usr/lib64/httpd/modules/mod_fastcgi.so

    FastCgiServer /var/www/html/yourapplication/app.fcgi -idle-timeout 300 -processes 5

    <VirtualHost *>
        ServerName webapp1.mydomain.com
        DocumentRoot /var/www/html/yourapplication

        AddHandler fastcgi-script fcgi
        ScriptAlias / /var/www/html/yourapplication/app.fcgi/

        <Location />
            SetHandler fastcgi-script
        </Location>
    </VirtualHost>

这些进程会由 Apache 管理着。如果你正在使用一个单独的 FastCGI 服务器的话，
你可以使用 FastCgiExternalServer 指令代替 FastCgiServer 指令。
但要注意下面的路径部分不是实际路径，它是直接用做一个识别符，指向另一个指令，
就像 AliasMatch 一样::

    FastCgiServer /var/www/html/yourapplication -host 127.0.0.1:3000

如果你无法配置 ScriptAlias 指令的话，例如在一台分享网络主机上，你可以使用
WSGI 中间件从 URL 网址中来移除 yourapplication.fcgi 文件名。设置 .htaccess 文件::

    <IfModule mod_fcgid.c>
       AddHandler fcgid-script .fcgi
       <Files ~ (\.fcgi)>
           SetHandler fcgid-script
           Options +FollowSymLinks +ExecCGI
       </Files>
    </IfModule>

    <IfModule mod_rewrite.c>
       Options +FollowSymlinks
       RewriteEngine On
       RewriteBase /
       RewriteCond %{REQUEST_FILENAME} !-f
       RewriteRule ^(.*)$ yourapplication.fcgi/$1 [QSA,L]
    </IfModule>

设置 yourapplication.fcgi 文件::

    #!/usr/bin/python
    #: optional path to your local python site-packages folder
    import sys
    sys.path.insert(0, '<your_local_path>/lib/python<your_python_version>/site-packages')

    from flup.server.fcgi import WSGIServer
    from yourapplication import app

    class ScriptNameStripper(object):
       def __init__(self, app):
           self.app = app

       def __call__(self, environ, start_response):
           environ['SCRIPT_NAME'] = ''
           return self.app(environ, start_response)

    app = ScriptNameStripper(app)

    if __name__ == '__main__':
        WSGIServer(app).run()

配置 lighttpd
--------------------

对于 lighttpd 服务器的一项基础 FastCGI 配置看起来像下面内容::

    fastcgi.server = ("/yourapplication.fcgi" =>
        ((
            "socket" => "/tmp/yourapplication-fcgi.sock",
            "bin-path" => "/var/www/yourapplication/yourapplication.fcgi",
            "check-local" => "disable",
            "max-procs" => 1
        ))
    )

    alias.url = (
        "/static/" => "/path/to/your/static/"
    )

    url.rewrite-once = (
        "^(/static($|/.*))$" => "$1",
        "^(/.*)$" => "/yourapplication.fcgi$1"
    )

记住开启 FastCGI、 alias 和 rewrite 模块。这种配置把网络应用绑定到
 ``/yourapplication`` 上了。如果你想要网络应用工作在 URL 根路径上的话，
你就要用 :class:`~werkzeug.contrib.fixers.LighttpdCGIRootFix` 中间件
来处理一个 lighttpd bug 了。

如果你正在把网络应用挂载到 URL 根路径上的话，只确保应用它即可。
对于更多信息也要稍微查看一下 `FastCGI and Python
<https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_ModFastCGI>`_ 
文档内容（注意这里就不需要明确地把一个插槽代入到 run() 中了）。

配置 nginx
-----------------

在 nginx 上安装 FastCGI 应用有点不一样，因为默认不直接提供 FastCGI 参数。

一个基础的 Flask FastCGI 配置，对于 nginx 来说看起来像下面这样::

    location = /yourapplication { rewrite ^ /yourapplication/ last; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
        fastcgi_split_path_info ^(/yourapplication)(.*)$;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param SCRIPT_NAME $fastcgi_script_name;
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

这种配置是把应用绑定到 ``/yourapplication`` 上。
如果你想要在 URL 根路径上有这项内容的话，就更容易一点儿了，
因为你不需要知道如何计算 ``PATH_INFO`` 和 ``SCRIPT_NAME``::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

运行 FastCGI 进程
-------------------------

由于 nginx 和其它服务器不加载 FastCGI 应用，你还要自己来实现。
 `Supervisor can manage FastCGI processes.
<http://supervisord.org/configuration.html#fcgi-program-x-section-settings>`_
 文档介绍了另一种 FastCGI 进程管理器，或写一个脚本在引导时来运行你的 `.fcgi` 文件。
例如使用一个系统 ``init.d`` 脚本。对于一种临时解决方案来说，你可以在 GNU screen里一直
运行 ``.fcgi`` 脚本。查看 ``man screen`` 了解细节，而且注意这是一种手动解决方案，
意味着系统重启后就无效了::

    $ screen
    $ /var/www/yourapplication/yourapplication.fcgi

调试
---------

FastCGI 部署在大多数网络服务器上都是难于吊饰的。常常只有服务器日志能够告诉你
一些头部早期结束信息行。要调试应用唯一的事情就是给你一些为什么应用断裂的信息，
这样你可以手动切换到正确的用户和手动执行应用。

这个实例假设你的应用名叫 `application.fcgi` 并且你的网络服务器用户是 `www-data`::

    $ su www-data
    $ cd /var/www/yourapplication
    $ python application.fcgi
    Traceback (most recent call last):
      File "yourapplication.fcgi", line 4, in <module>
    ImportError: No module named yourapplication

此时的情况错误看起来表明 "yourapplication" 没有在 python 路径上。
共性的问题都是：

-   使用了相对路径。无法根据当前工作目录来调用。
-   代码依据的环境变量没有通过网络服务器进行设置。
-   使用了不同版本的 python 解释器。

.. _nginx: https://nginx.org/
.. _lighttpd: https://www.lighttpd.net/
.. _cherokee: http://cherokee-project.com/
.. _flup: https://pypi.org/project/flup/
