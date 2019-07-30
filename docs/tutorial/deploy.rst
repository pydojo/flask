生产部署
====================

本部分教程假设你有一台服务器主机是你的网络应用部署对象。
如何建立分发文件并安装分发文件？本部分给你一个概况介绍，
但不会介绍用什么服务器或软件。你可以在你的开发电脑上
配置一个新的环境来尝试如下指令，但可能不该用在一台真正
的公共应用主机上。查看 :doc:`/deploying/index` 文档
了解不同的方法服务你的网络应用。


建立与安装
-----------------

当你想要把你的网络应用部署在其它服务器上，
你就要建立一个分发文件。当前对于 Python
来说标准是 *wheel* 格式，使用带有 ``.whl`` 
后缀的一种文件格式。确保先安装 wheel 库：

.. code-block:: none

    $ pip install wheel

用 Python 命令行工具运行 ``setup.py`` 时需要使用
 ``bdist_wheel`` 命令选项才会建立一个 wheel 格式
的分发版本文件。

.. code-block:: none

    $ python setup.py bdist_wheel

在项目目录中你会发现文件位于 ``dist/flaskr-1.0.0-py3-none-any.whl`` 路径上。
文件名就是网络应用名、版本号和一些文件可以安装的标签信息。

把这个文件拷贝到另一台设备上，参考
:ref:`set up a new virtualenv <install-create-env>` 内容，
然后用 ``pip`` 来安装这个文件。

.. code-block:: none

    $ pip install flaskr-1.0.0-py3-none-any.whl

Pip 会自动安装你的网络应用所需要的依赖库。

由于此时是一台与开发时使用的不同机器，
你还需要再运行 ``init-db`` 命令来
建立一个实例文件夹存放数据库。

.. code-block:: none

    $ export FLASK_APP=flaskr
    $ flask init-db

当 Flask 检测到网络应用已经安装完 (不要安装成可编辑模式)，
实例文件夹的名字与开发时使用的不同。你会发现变成
``venv/var/flaskr-instance`` 这个名字了。


配置密钥
------------------------

在本项目教程开始，你给过一个默认密钥 :data:`SECRET_KEY` 值。
这个值应该在生产中使用另一个随机字节密钥值。否则，攻击者会使用
公共的 ``'dev'`` 密钥值来修改会话 cookie 或者修改任何使用这个
密钥值的其它内容。

你可以使用如下命令来输出一个随机密钥：

.. code-block:: none

    $ python -c 'import os; print(os.urandom(16))'

    b'_5#y2L"F4Q8z\n\xec]/'

在实例文件夹中建立 ``config.py`` 文件，因为如果有这个文件的话，
工厂函数会从这个配置文件中来读取配置项值。把值复制给网络应用配置。

.. code-block:: python
    :caption: ``venv/var/flaskr-instance/config.py``

    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

你也可以在这个配置文件中设置其它需要的配置项，
对于 Flaskr 项目来说只需要 ``SECRET_KEY`` 配置项。


用生产服务器来运行网络应用
----------------------------

当运行在公共服务器环境中，
你应该不要使用开发时的内置服务器 (``flask run``) 了。
开发服务器是由 Werkzeug 为了开发方便而提供的，
这种开发服务器不是为特别效率、稳定或安全的生产而设计的。

相反生产环境中我们要使用一个 WSGI 服务器。例如，使用
 `Waitress`_ 服务器，首先在虚拟环境中安装它：

.. code-block:: none

    $ pip install waitress

你需要告诉 Waitress 关于你的网络应用相关信息，
而不是使用 ``FLASK_APP`` 像 ``flask run`` 命令那样。
你需要告诉生产服务器要导入和调用网络应用工厂函数来获得一个网络应用对象。

.. code-block:: none

    $ waitress-serve --call 'flaskr:create_app'

    Serving on http://0.0.0.0:8080

查看 :doc:`/deploying/index` 文档内容了解许多不同的服务你的网络应用方法。
Waitress 只是为本项目教程选用的一个示例，因为 Waitress 即支持 Windows系统，
也支持 Linux 系统。还有许多 WSGI 服务器作为你的项目部署选择。

.. _Waitress: https://docs.pylonsproject.org/projects/waitress/

继续阅读 :doc:`next` 文档内容。
