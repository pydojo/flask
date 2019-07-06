.. _installation:

安装 Flask
============

Python 版本
--------------

我们建议使用最新的 Python3 版本。Flask 支持大于 Python3.4 的版本，
以及支持 Python2.7 和 PyPy 版本。

依赖情况
------------

当安装 Flask 的过程中如下依赖库都会自动安装。

* `Werkzeug`_ 部署 WSGI 的库，在应用于服务器之间提供标准的 Python 接口。
* `Jinja`_ 是一个模版语言库，把应用服务翻译到页面上。
* `MarkupSafe`_ 伴随着 Jinja 一起安装的安全库。它在翻译模版过程中
  转义那些不被信赖的输入，来避免注射攻击。
* `ItsDangerous`_ 安全标记数据来确保数据的诚实性。它保护着 Flask 的会话cookie
* `Click`_ 是一个写命令行程序的框架。它提供着 ``flask`` 命令以及允许增加自定义管理命令。

.. _Werkzeug: http://werkzeug.pocoo.org/
.. _Jinja: http://jinja.pocoo.org/
.. _MarkupSafe: https://pypi.org/project/MarkupSafe/
.. _ItsDangerous: https://pythonhosted.org/itsdangerous/
.. _Click: http://click.pocoo.org/

可选的依赖情况
~~~~~~~~~~~~~~~~~~~~~

如下依赖库不会自动安装。手动安装后 Flask 会检测并使用它们。

* `Blinker`_ 针对 :ref:`signals` 提供支持。
* `SimpleJSON`_ 是一个快速 JSON 部署库，它兼容 Python 的 ``json`` 标准库。
  如果安装的话更适合对 JSON 的操作。
* `python-dotenv`_ 当运行 ``flask`` 命令时开启 :ref:`dotenv` 支持。
* `Watchdog`_ 针对开发服务器提供更快速、更有效的重载性能。

.. _Blinker: https://pythonhosted.org/blinker/
.. _SimpleJSON: https://simplejson.readthedocs.io/
.. _python-dotenv: https://github.com/theskumar/python-dotenv#readme
.. _watchdog: https://pythonhosted.org/watchdog/

虚拟环境
--------------------

使用一个虚拟环境来管理项目的这些依赖库，既可以用在开发中，也可以用在生产中。

一个虚拟环境到底解决什么问题？
你有许多 Python 项目时，很可能要与不同的 Python 库版本一起工作。
Python 库越新的版本对于一个项目来说可能会导致在其它项目中使用时无效。

虚拟环境都是独立的 Python 库安装环境，针对每个项目所安装的库版本都可以不一样。
那么为每个项目所安装的库版本因为在不同的虚拟环境中，彼此互不影响。
同时也不会影响在系统范围中所安装的 Python 库版本。

Python3 的标准虚拟环境库是 :mod:`venv` 模块，它可以建立众多虚拟环境。
如果你所使用的 Python 版本是比较新的3系，你可以继续看下一部分内容。

如果你使用的是 Python2 淘汰的遗产版本，先参考 :ref:`install-install-virtualenv` 内容。

.. _install-create-env:

建立一个虚拟环境
~~~~~~~~~~~~~~~~~~~~~

建立一个项目目录后，进入项目目录建立虚拟环境第二个 :file:`venv` 是虚拟环境目录名：

.. code-block:: sh

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv venv

在 Windows 上建立虚拟环境：

.. code-block:: bat

    $ py -3 -m venv venv

由于你正在使用 Python2 所安装的 virtualenv 要使用如下命令来建立虚拟环境：

.. code-block:: sh

    $ python2 -m virtualenv venv

在 Windows 上建立虚拟环境：

.. code-block:: bat

    > \Python27\Scripts\virtualenv.exe venv

.. _install-activate-env:

激活虚拟环境
~~~~~~~~~~~~~~~~~~~~~~~~

在项目上开始工作之前，激活对应的虚拟环境：

.. code-block:: sh

    $ . venv/bin/activate

在 Windows 上激活虚拟环境：

.. code-block:: bat

    > venv\Scripts\activate

命令行提示符最左边会显示激活虚拟环境的提示符。

安装 Flask
-------------

在激活虚拟环境后，使用如下命令安装 Flask：

.. code-block:: sh

    $ pip install Flask

Flask 安装完。可以阅读 :doc:`/quickstart` 文档，或者查看
 :doc:`Documentation Overview </index>` 文档。

活在边缘中的方式
~~~~~~~~~~~~~~~~~~

如果你想用还未发布的最新 Flask 代码的话，需要从主干安装或更新 Flask 代码：

.. code-block:: sh

    $ pip install -U https://github.com/pallets/flask/archive/master.tar.gz

.. _install-install-virtualenv:

安装 virtualenv
------------------

如果你正在使用 Python2 的话，venv 标准库无法使用。而是要安装 `virtualenv`_ 第三方库。

在 Linux 系统上 virtualenv 是由软件包管理器提供：

.. code-block:: sh

    # Debian, Ubuntu
    $ sudo apt-get install python-virtualenv

    # CentOS, Fedora
    $ sudo yum install python-virtualenv

    # Arch
    $ sudo pacman -S python-virtualenv

如果在 Mac OS X 或 Windows 系统上，下载 `get-pip.py`_ 后，安装：

.. code-block:: sh

    $ sudo python2 Downloads/get-pip.py
    $ sudo python2 -m pip install virtualenv

在 Windows 系统上，要以管理员身份来安装：

.. code-block:: bat

    > \Python27\python.exe Downloads\get-pip.py
    > \Python27\python.exe -m pip install virtualenv

此时你可以回看并参考 :ref:`install-create-env` 文档。

.. _virtualenv: https://virtualenv.pypa.io/
.. _get-pip.py: https://bootstrap.pypa.io/get-pip.py
