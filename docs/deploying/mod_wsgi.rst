.. _mod_wsgi-deployment:

mod_wsgi Apache
=================

如果你们正在使用 `Apache`_ 网络服务器的话，考虑使用 `mod_wsgi`_ 时。

.. admonition:: 小心

   一定要确保在你的网络应用中任何一个 ``app.run()`` 调用放在
    ``if __name__ == '__main__':`` 习语块内，或者移到单个文件里。
   只要确保不会被调用即可，否则总会启动一个本地 WSGI 服务器，
   如果我们把网络应用部署到 mod_wsgi 上的话，这不是我们想要的现象。

.. _Apache: https://httpd.apache.org/

安装 `mod_wsgi`
---------------------

如果你还没安装 `mod_wsgi` 的话，你即可使用包管理器来按照，也可以自己编译源文件来按照。
mod_wsgi `installation instructions`_ 含有在 UNIX 系统上的源文件安装介绍。

如果正在使用 Ubuntu/Debian Linux系统的话，你可以使用 apt-get 包管理器安装并激活：

.. sourcecode:: 命令行

    $ apt-get install libapache2-mod-wsgi

如果你正在使用基于 yum 分发版本的 Linux 系统的话（例如，Fedora、 OpenSUSE，等等）
你可以运行如下命令来安装：

.. sourcecode:: 命令行

    $ yum install mod_wsgi

在 FreeBSD Linux 系统上安装 `mod_wsgi` 是通过编译 `www/mod_wsgi` 移植包或通过
使用 pkg_add 来安装：

.. sourcecode:: 命令行

    $ pkg install ap22-mod_wsgi2

如果你正在使用 pkgsrc 的话，你可以通过编译 `www/ap2-wsgi` 包来安装 `mod_wsgi` 

在 apache 重载后，如果你遇到 segfaulting 子进程问题，你可以忽略它们。
只需要重启服务器即可。


建立一个 `.wsgi` 文件
-----------------------

要运行你的网络应用，你需要一个 :file:`yourapplication.wsgi` 文件。这个文件包含的
代码是在启动时 `mod_wsgi` 执行后获得网络应用对象。在这个文件中名叫
 `application` 的那个对象就是后面被用做应用。

对于大多数应用来说，下面的文件代码足够了::

    from yourapplication import app as application

如果在 Flask 网络应用中 :file:`__init__.py` 文件里使用了一种工厂函数方式的话，那么就要导入这个函数::

    from yourapplication import create_app
    application = create_app()

对于应用建立来说，如果你没有使用一种工厂函数方式的话，而是使用了单体模式实例，
那么你可以直接导入成 `application` 即可。

把 wsgi 文件存储在可以再次找到的地方（例如： :file:`/var/www/yourapplication` 路径），
然后确保 `yourapplication` 和所有用到的库都位于 python 加载路径上。
如果你不想安装到系统中，考虑使用一种 `virtual python`_ 虚拟环境实例即可。
记住实际上你也要把你的网络应用安装到虚拟环境里。
另外在导入应用之前，也可以有另外一种选择，只是把路径补充在 ``.wsgi`` 文件中::

    import sys
    sys.path.insert(0, '/path/to/the/application')

配置 Apache
------------------

你所要做的最后一件事情就是为你的网络应用建立一份 Apache 配置文件。
在此示例中，我们正在告诉 `mod_wsgi` 为了安全起见在不同的用户下执行网络应用：

.. sourcecode:: apache

    <VirtualHost *>
        ServerName example.com

        WSGIDaemonProcess yourapplication user=user1 group=group1 threads=5
        WSGIScriptAlias / /var/www/yourapplication/yourapplication.wsgi

        <Directory /var/www/yourapplication>
            WSGIProcessGroup yourapplication
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

注意： WSGIDaemonProcess 在 Windows 系统中没有部署，而且 Apache 在 Windows 系统上会拒绝运行
上面这种配置。在 Windows 系统上，使用如下配置内容：

.. sourcecode:: apache

	<VirtualHost *>
		ServerName example.com
		WSGIScriptAlias / C:\yourdir\yourapp.wsgi
		<Directory C:\yourdir>
			Order deny,allow
			Allow from all
		</Directory>
	</VirtualHost>

注意：对于 `Apache 2.4`_ 来说在访问控制配置文件上有了一些变更。

.. _Apache 2.4: https://httpd.apache.org/docs/trunk/upgrading.html

尤其是在目录许可的句法上与 httpd 2.2 不一样了：

.. sourcecode:: apache2.2

    Order allow,deny
    Allow from all

对于 httpd 2.4 的目录访问权限句法是

.. sourcecode:: apache2.4

    Require all granted


对于更多信息咨询 `mod_wsgi documentation`_ 文档内容。

.. _mod_wsgi: https://github.com/GrahamDumpleton/mod_wsgi
.. _installation instructions: https://modwsgi.readthedocs.io/en/develop/installation.html
.. _virtual python: https://pypi.org/project/virtualenv/
.. _mod_wsgi documentation: https://modwsgi.readthedocs.io/en/develop/index.html

遇到的麻烦
---------------

如果你的网络应用不能运行的话，遵循如下这些知道来解决麻烦：

**问题：** 网络应用不运行，错误日志显示 SystemExit ignored
    说明在你的网络应用文件中调用的那句 ``app.run()`` 代码没有放在
     ``if __name__ == '__main__':`` 习语块中。既可以移除
    那句 :meth:`~flask.Flask.run` 调用后放到单个
     :file:`run.py` 文件里，也可以放到习语块里。

**问题：** 网络应用给出许可错误
    可能是由于你的网络应用运行在没有权限的用户上。
    确保网络应用所在的目录具有所需正确的特权集合后
    网络应用运行在正确的用户账户上
    （ ``user`` 和 ``group`` 参数都会影响 `WSGIDaemonProcess` 指令的执行）

**问题：** 网络应用挂掉时含有一项错误显示在终端里
    记住 mod_wsgi 不允许使用 :data:`sys.stdout` 系统标准输出数据做任何事情，
    而且用 :data:`sys.stderr` 系统标准错误数据也不行。你可以禁用这类用法，
    在配置文件中设置 `WSGIRestrictStdout` 指令为 ``off`` 来开启保护：

    .. sourcecode:: apache

        WSGIRestrictStdout Off

    另外一种选择是，你也可以在 .wsgi 文件里用不同的数据流替换标准输出::

        import sys
        sys.stdout = sys.stderr

**问题：** 访问资源时给出了 IO 错误
    你的网络应用可能是一个单独连接到 site-packages 文件夹的软连接 .py 文件。
    要知道这样是无法工作的，相反你既可以把文件夹放到 python 路径文件所在的位置，
    也可以把你的网络应用转换成一个 python 包。

    对于这种问题的原因就是那些无安装的包形式造成的，模块文件名用做分配资源时识别的名字，
    并且对于软连接来说，选择了一个错误的文件名。

支持自动重载
-------------------------------

要帮助部署工具一个忙，你可以激活自动重载支持。
不管什么时候 ``.wsgi`` 文件变更了，
 `mod_wsgi` 都会为我们重载所有守护进程。

对于这个只增加如下指令到你的 `Directory` 配置部门：

.. sourcecode:: apache

   WSGIScriptReloading On

与虚拟环境一起工作
---------------------------------

虚拟环境具有的优势是，从来不安装所需的依赖包到系统中，
这样你就有了更良好的控制在什么地方使用什么资源。
如果你想要与 mod_wsgi 一起使用虚拟环境的话，
你要稍微修改一下你的 ``.wsgi`` 文件。

在你的 ``.wsgi`` 文件顶部增加如下代码::

    activate_this = '/path/to/env/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

对于 Python3 来说在你的 ``.wsgi`` 文件顶部增加如下代码::

    activate_this = '/path/to/env/bin/activate_this.py'
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

这就配置了加载路径，依据虚拟环境的设置来定。
记住虚拟环境中的这个文件路径必须是绝对路径。
