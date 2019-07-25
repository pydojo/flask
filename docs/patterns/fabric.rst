.. _fabric-deployment:

用 Fabric 部署全自动化
=========================

`Fabric`_ 对 Python 来说类似 Makefile 的一个工具，
但带有在一个远程服务器上执行命令的能力。与一个正确配置的
Python 包 (:ref:`larger-applications`) 和一个良好
的配置概念 (:ref:`config`) 组合起来，把 Flask 网络应用
部署到外部服务器上是非常容易的事情。

我们开始之前，我们要确保如下一份检查清单已经就绪：

-   Fabric 1.0 要安装在本地系统上。本教程假设安装了
    最新版本的 Fabric 库。
-   网络应用已经转换成一个包了，并且含有需要的一个
    :file:`setup.py` 文件 (:ref:`distribute-deployment`) 。
-   如下的示例中我们的远程服务器正在使用 `mod_wsgi` 模块。
    你当然可以使用自己喜欢的服务器，但对于这里但示例来说，
    我们选择了 Apache + `mod_wsgi` 组合，因为非常容易配置，
    并且具有一种直接的方式来重载网络应用，不需要超级用户权限。

建立第一个 Fabfile 文件
--------------------------

一个 fabfile 文件就是控制 Fabric 要执行什么。文件名是 :file:`fabfile.py`
并且要用 `fab` 命令来执行这个文件。文件中所有定义的函数都会视为
 `fab` 的子命令。它们都被执行在一个或多个主机上。
这些主机既可以定义在 fabfile 文件中，也可以定义在命令行中。
这里我们会把主机加入到 fabfile 文件里。

下面的第一个例子是基础，它具有上传当前源代码到服务器的能力，
并且安装到预先存在的虚拟环境中::

    from fabric.api import *

    # the user to use for the remote commands
    env.user = 'appuser'
    # the servers where the commands are executed
    env.hosts = ['server1.example.com', 'server2.example.com']

    def pack():
        # build the package
        local('python setup.py sdist --formats=gztar', capture=False)

    def deploy():
        # figure out the package name and version
        dist = local('python setup.py --fullname', capture=True).strip()
        filename = '%s.tar.gz' % dist

        # upload the package to the temporary folder on the server
        put('dist/%s' % filename, '/tmp/%s' % filename)

        # install the package in the application's virtualenv with pip
        run('/var/www/yourapplication/env/bin/pip install /tmp/%s' % filename)

        # remove the uploaded package
        run('rm -r /tmp/%s' % filename)

        # touch the .wsgi file to trigger a reload in mod_wsgi
        run('touch /var/www/yourapplication.wsgi')

运行 Fabfile 文件
-----------------------

现在你如何执行上面的 fabfile 文件呢？那就是使用 `fab` 命令。
要在远程服务器上部署当前版本的代码，你要使用如下命令::

    $ fab pack deploy

不管如何做到的，远程服务器上需要已经有
:file:`/var/www/yourapplication` 文件夹和
:file:`/var/www/yourapplication/env` 虚拟环境目录。
进一步说，我们没有建立配置，或者说在远程服务器上没有建立
 ``.wsgi`` 文件。那么我们如何把新的服务器绑定到基础设施上呢？

此时就依据我们想要配置的服务器数量了。
如果我们只有一个网络应用服务器的话（
这是大多数网络应用都会有的），在
fabfile 文件中建立一个命令，对这种情况来说是过分了。
但显然你可以这样做。在那种情况中你可能调用
`setup` 或 `bootstrap` 命令后把服务器名明确地
代入到命令行中::

    $ fab -H newserver.example.com bootstrap

要配置一个新的服务器，你应该大概完成如下步骤：

1.  在 :file:`/var/www` 目录中建立目录结构::

        $ mkdir /var/www/yourapplication
        $ cd /var/www/yourapplication
        $ virtualenv --distribute env

2.  上传一个新的 :file:`application.wsgi` 文件到远程服务器，
    和上传一个网络应用的配置文件 (eg: :file:`application.cfg`)

3.  建立一个新的 Apache 配置给 ``yourapplication`` 目录后激活配置。
    确保为 ``.wsgi`` 文件的变更激活守望功能，所以我们才可以碰一下
    这个文件就能够自动化重载网络应用了。
    (查看 :ref:`mod_wsgi-deployment` 参考内容了解更多信息)

那么现在的问题是，在哪里写 :file:`application.wsgi` 文件，以及
:file:`application.cfg` 文件来自什么地方？

WSGI 文件
-------------

对于 WSGI 文件来说要导入网络应用，并且也要设置一个环境变量，
这样网络应用才知道去哪里寻找配置。如下正是一个简短的示例::

    import os
    os.environ['YOURAPPLICATION_CONFIG'] = '/var/www/yourapplication/application.cfg'
    from yourapplication import app

作为网络应用自身然后要做的就是，初始化自己，就像下面代码一样
去寻找在环境变量中的配置::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_config')
    app.config.from_envvar('YOURAPPLICATION_CONFIG')

这种方式详细解释在 :ref:`config` 配置处理文档中。

配置文件
----------------------

此时如同上面所提醒的一样，网络应用会找到正确的配置文件，
通过查看 ``YOURAPPLICATION_CONFIG`` 环境变量即可。
所以我们要把配置文件放在一个地方，那就是网络应用能找到
的地方。许多配置文件在所有电脑上存在不同的形式，至此具有
一种不友好的质量属性，所以你常常不要对其进行版本化。

一种受欢迎的方法就是把许多配置文件针对不同的服务器存储在
一个单独的版本控制仓库里，然后在所有服务器上来检查它们。
那么针对一个服务器建立一个激活的软连接文件指向所期望的位置
 (例如， :file:`/var/www/yourapplication`)。

即便是这种方法，在我们此处的情况中，我们只期望一个或两个
服务器，然后我们手动提前上传它们。


第一步部署
----------------

现在我们可以开展第一步部署。我们已经设置了服务器，所以
服务器有了它们的虚拟环境和激活的 apache 配置文件。现在
我们可以打包网络应用后部署网络应用::

    $ fab pack deploy

Fabric 此时会连接到所有的服务器，然后运行写在 fabfile 文件
中的命令。首先会执行打包命令，这样我们就有了准备好的包，接着
会执行部署命令和上传源代码到所有服务器，在服务器上安装这个包。
要感谢 :file:`setup.py` 文件，我们会自动地拉取所需的库到
服务器上的虚拟环境中。

第二步部署
-------------

从第一步继续，这步可以实现许多工作让部署变得真正有趣：

-   建立一个 `bootstrap` 命令，该命令初始化所有新服务器。
    它可以初始化一个新的虚拟环境，正确地配置 apache 服务器，等等工作。
-   把许多配置文件放在一个单独的版本控制仓库中，然后建立激活的
    配置文件软连接连接到所在位置。
-   你也可以把你的网络应用代码放到一个仓库中，然后检查服务器上的最新版本，
    然后再安装。那样你也可以容易地退回到较旧的版本上。
-   在测试功能性时，使用钩子，那样你可以部署到一个外部服务器上，然后运行
    测试套件。

与 Fabric 一起工作是有趣的事情，并且你会注意到输入 ``fab deploy`` 命令
如同魔术一样，然后看到你的网络应用就自动化地部署到一个或多个远程服务器上。


.. _Fabric: https://www.fabfile.org/
