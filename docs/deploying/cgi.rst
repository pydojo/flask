CGI
===

如果其它全部部署方法都无效的话， CGI 一定没问题。
CGI 是所有主要服务器都支持的一项功能，但常常具有一种次要理想性能。

这也可以让你在 Google's `App Engine`_ 上使用一个 Flask 网络应用，
其中 Google 执行类似一种 CGI 环境。

.. admonition:: 小心

   一定要确保任何一个 ``app.run()`` 调用放在你的应用文件
    ``if __name__ == '__main__':`` 习语块中，
   或者放到一个分开的文件里。只确保不被调用即可，因为总会启动一个本地
    WSGI 服务器，如果我们把网络应用部署到 CGI / app 引擎上的话，
   这不是我们想要的现象。

   使用 CGI，你也要确保你的代码不包含任何一个 ``print`` 语句。
   或者 ``sys.stdout`` 代码，因为它被覆写时有些内容无法写到 HTTP 响应中。

建立一个 `.cgi` 文件
----------------------

首先你需要建立一个 CGI 应用文件。此处我们叫它 :file:`yourapplication.cgi`::

    #!/usr/bin/python
    from wsgiref.handlers import CGIHandler
    from yourapplication import app

    CGIHandler().run(app)

服务器配置
------------

常常有两种方式来配置服务器。一种只是把
``.cgi`` 拷贝到 :file:`cgi-bin` 目录里（然后使用 `mod_rewrite` 或类似的工具重写 URL 地址），
另一种是直接让服务器指向 ``.cgi`` 文件。

在 Apache 服务器中，例如你可以把想如下一样指令放到配置文件中：

.. sourcecode:: apache

    ScriptAlias /app /path/to/the/application.cgi

在分享的网络主机上，尽管你也许没有访问 Apache 配置文件的权限。
在这种情况下，一个名叫 ``.htaccess`` 文件位于公共目录里，
这个正式你的网络应用想要使用的文件，同时可以有效的进行服务器配置，
但 ``ScriptAlias`` 这条指令就无效了，改为:

.. sourcecode:: apache

    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f # Don't interfere with static files
    RewriteRule ^(.*)$ /path/to/the/application.cgi/$1 [L]

更多信息咨询你的网络服务器文档内容。

.. _App Engine: https://developers.google.com/appengine/
