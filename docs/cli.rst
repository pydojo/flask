.. currentmodule:: flask

.. _cli:

命令行接口
======================

在你的虚拟环境中安装 Flask 过程中安装了 ``flask`` 脚本，
这是一个 `Click`_ 命令行接口。
用来在终端里执行程序，这个脚本给了许多访问内置、扩展，和定义完的网络应用命令。
它的 ``--help`` 命令行选项会给你更多关于其它命令和选项的信息。

.. _Click: http://click.pocoo.org/


发现网络应用
---------------------

此 ``flask`` 命令是由 Flask 安装的，而不是由你的网络应用来安装；
那么就必须告诉 ``flask`` 命令到哪里可以找到你的网络应用，
这样才能在终端里启动网络应用。
其 ``FLASK_APP`` 环境变量是用来描述如何加载网络应用的。

Unix Bash (Linux, Mac, etc.)::

    $ export FLASK_APP=hello
    $ flask run

Windows CMD::

    > set FLASK_APP=hello
    > flask run

Windows PowerShell::

    > $env:FLASK_APP = "hello"
    > flask run

同时 ``FLASK_APP`` 支持许多各种选项来描述你的网络应用，大多数用起来都是简单直接。
下面是一些典型的值描述：

（什么都不描述）
    当 :file:`wsgi.py` 导入后，自动地检测一个网络应用（ ``app`` ）。
    这样提供了一种容易的方法带着许多额外的参数从一个工厂函数建立一个网络应用。

``FLASK_APP=hello``
    导入名字后，自动地检测一个网络应用（ ``app`` ）或工厂函数（ ``create_app`` ）。

``FLASK_APP`` 环境变量
----------------------------

``FLASK_APP`` 环境变量有三个部分：
一个可选路径，是设置当前工作目录，一个 Python文件或句号导入部分，
和一个可选的应用实例或工厂函数变量名。
如果名字是一个工厂函数的名字，那么就可以在圆括号对儿中代入参数。
如下例子示范了这些部分的用法：

``FLASK_APP=src/hello``
    设置当前工作目录为 ``src`` 后导入 ``hello`` 。

``FLASK_APP=hello.web``
    设置导入路径 ``hello.web`` 。

``FLASK_APP=hello:app2``
    设置导入 ``hello`` 中 ``app2`` Flask 实例作为网络应用。

``FLASK_APP="hello:create_app('dev')"``
    设置 ``hello`` 中的 ``create_app`` 工厂函数调用时带着字符串 ``'dev'`` 作为参数值。

如果 ``FLASK_APP`` 环境变量没有进行设置的话， ``flask`` 命令会寻找名叫
 :file:`wsgi.py` 的文件，或者寻找名叫 :file:`app.py` 的文件，
然后尝试检测一个网络应用实例或一个工厂函数。

在导入的内容里， ``flask`` 命令会查找名叫 ``app`` 或 ``application`` 的网络应用实例，
或者再查找任何一个网络应用实例。如果找不到一个实例的话，命令会去查找一个能够返回一个实例的名叫
 ``create_app`` 或 ``make_app`` 的工厂函数。

当调用一个网络应用工厂函数时，如果工厂函数得到一个名叫 ``script_info`` 的参数，
那么 :class:`~cli.ScriptInfo` 类的实例会代入成一个关键字参数。
如果网络应用工厂函数只得到一个参数并且工厂函数名后没有圆括号对儿的话，
 :class:`~cli.ScriptInfo` 类的实例会代入成一个位置参数。
如果圆括号对儿在工厂函数名后的话，其中的内容会由 Python 逐字分析后
作为参数代入到工厂函数中。这就意味着必须使用字符串。


运行开发服务器
--------------------------

用 :func:`run <cli.run_command>` 这个函数命令启动开发服务器。
大多数情况中它代替了 :meth:`Flask.run` 方法。 ::

    $ flask run
     * Serving Flask app "hello"
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

.. 警告:: 不要在生产环境中来使用这个命令。
    只用在开发期间来启动开发服务器。开发服务器是为了开发方便，
    没有为特殊安全、稳定或效率进行设计。
    查看 :ref:`deployment` 参考文档了解生产中如何开启服务器。


打开一个REPL
------------

要揭露你的网络应用中的数据，你可以用 :func:`shell <cli.shell_command>` 函数命令
启动一个 Python 的互动环境。一个网络应用的环境也会被激活，
然后 app 实例会导入到这种 REPL 里。 ::

    $ flask shell
    Python 3.6.2 (default, Jul 20 2017, 03:52:27)
    [GCC 7.1.1 20170630] on linux
    App: example
    Instance: /home/user/Projects/hello/instance
    >>>

使用 :meth:`~Flask.shell_context_processor` 方法来增加其它自动导入项。


环境
------------

.. versionadded:: 1.0

环境中的 Flask 网络应用运行是通过 :envvar:`FLASK_ENV` 环境变量来设置的。
如果没有设置的话，环境变量默认为 ``production`` 生产环境。
其它可以识别的环境变量值是 ``development`` 开发环境。
Flask 和扩展件根据环境来选择开启哪些行为表现。

如果环境变量设置成 ``development`` 开发的话，命令行 ``flask`` 命令会开启调试模式，
并且 ``flask run`` 会开启交互式调试器和重载器。

::

    $ FLASK_ENV=development flask run
     * Serving Flask app "hello"
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with inotify reloader
     * Debugger is active!
     * Debugger PIN: 223-456-919


调试模式
----------

当 :envvar:`FLASK_ENV` 环境变量值是 ``development`` 的时候才会开启调试模式，
如果你想要分开控制调试模式的话，使用 :envvar:`FLASK_DEBUG` 环境变量。
值为 ``1`` 是开启调试模式，值为 ``0`` 禁用调试模式。


.. _dotenv:

来自 dotenv 的环境变量
---------------------------------

比起每次打开新的终端来设置 ``FLASK_APP`` 环境变量，你可以使用
 Flask 的 dotenv 支持来自动化设置环境变量。

如果 `python-dotenv`_ 安装完毕的话，运行 ``flask`` 命令会设置定义在
 :file:`.env` 和 :file:`.flaskenv` 文件中的环境变量。
这种方式可以用来避免每次的手动设置 ``FLASK_APP`` 环境变量，
而且这种配置文件的设置用起来与有些开发服务工作原理是类似的。

把许多需要在命令行中设置的变量配置在 :file:`.env` 文件中，
都会被配置到 :file:`.flaskenv` 文件里去。
那么 :file:`.flaskenv` 文件应该用做公共变量，
例如 ``FLASK_APP`` 环境变量，同时 :file:`.env` 文件
不应该提交到你的仓库中，所以可以用来设置私有变量。

扫描目录都是从你调用 ``flask`` 命令所在的目录向上扫描来分配文件。
当前工作目录会被设置成文件所在位置，并假设成项目顶层目录。

只有通过 ``flask`` 命令或调用 :meth:`~Flask.run` 方法才能加载文件。
如果在生产环境中你想要加载这些文件的话，
你应该手动调用 :func:`~cli.load_dotenv` 函数。

.. _python-dotenv: https://github.com/theskumar/python-dotenv#readme


设置命令选项
~~~~~~~~~~~~~~~~~~~~~~~

Click 被配置成从环境变量加载命令行选项默认值。
这些变量使用了 ``FLASK_COMMAND_OPTION`` 模式。
例如，要设置 ``run`` 命令的端口的话，而不是使用
 ``flask run --port 8000`` 来运行网络应用，就是：

.. code-block:: none

    $ export FLASK_RUN_PORT=8000
    $ flask run
     * Running on http://127.0.0.1:8000/

这些命令选项可以增加到 ``.flaskenv`` 文件中去，
就像 ``FLASK_APP`` 控制默认命令选项一样。


禁用 dotenv
~~~~~~~~~~~~~~

如果 ``flask`` 命令检测到 dotenv 文件但没有安装 python-dotenv 的话，
命令行 ``flask`` 命令会显示一个消息。

.. code-block:: none

    $ flask run
     * Tip: There are .env files present. Do "pip install python-dotenv" to use them.

你可以告诉 Flask 不加载 dotenv 文件，即使安装了 python-dotenv 后设置了
 ``FLASK_SKIP_DOTENV`` 环境变量。
如果你想要手动加载它们的话这是有用的，或者如果你正使用一个项目运行器加载它们的话，
这也是有用的。记住环境变量必须在网络应用加载之前设置好，或者没有如期配置好之前。

.. code-block:: none

    $ export FLASK_SKIP_DOTENV=1
    $ flask run


来自 virtualenv 的环境变量
-------------------------------------

如果你不想安装 dotenv 支持的话，你依然可以通过把环境变量增加到
virtualenv :file:`activate` 虚拟环境激活脚本中来设置环境变量。
激活虚拟环境时会设置 Flask 的环境变量。

Unix Bash, :file:`venv/bin/activate`::

    $ export FLASK_APP=hello

Windows CMD, :file:`venv\\Scripts\\activate.bat`::

    > set FLASK_APP=hello

最好是使用 dotenv 支持来配置环境变量，因为 :file:`.flaskenv` 可以
提交到仓库中，如此一来不管什么时候检查项目时都会实现自动化工作。


自定义命令
---------------

部署 ``flask`` 命令使用的是 `Click`_ 模块。
查看项目文档了解书写命令的完整信息。

这里的例子是增加 ``create_user`` 命令，它可以接受 ``name`` 参数。 ::

    import click
    from flask import Flask

    app = Flask(__name__)

    @app.cli.command()
    @click.argument('name')
    def create_user(name):
        ...

::

    $ flask create_user admin

下面的例子是增加相同的命令，但用法是 ``user create`` 形式，
使用命令组中的一个命令方式。如果你想要对多个相关的命令进行组织的话，
这是有用的技术 ::

    import click
    from flask import Flask
    from flask.cli import AppGroup

    app = Flask(__name__)
    user_cli = AppGroup('user')

    @user_cli.command('create')
    @click.argument('name')
    def create_user(name):
        ...

    app.cli.add_command(user_cli)

::

    $ flask user create demo

查看 :ref:`testing-cli` 参考文档可以对如何测试你的自定义命令有一种概况认识。


网络应用语境
~~~~~~~~~~~~~~~~~~~

使用 Flask 网络应用的 :attr:`~Flask.cli` 属性
 :meth:`~cli.AppGroup.command` 方法装饰器增加的命令会带着一个推送的网络应用语境来执行，
所以你的命令和扩展件可以访问网络应用，以及访问网络应用的配置。
如果你使用 Click 模块的  :func:`~click.command` 函数装饰器建立一个命令，
而不是使用 Flask 装饰器来建立命令的话，你可以使用
 :func:`~cli.with_appcontext` 函数来获得一样的表现。 ::

    import click
    from flask.cli import with_appcontext

    @click.command()
    @with_appcontext
    def do_work():
        ...

    app.cli.add_command(do_work)

如果你确定一个命令不需要语境的话，你可以禁用语境::

    @app.cli.command(with_appcontext=False)
    def do_work():
        ...


插件
-------

Flask 会自动加载描述在 ``flask.commands`` `entry point`_ 入口中的命令。
这对于扩展件来说是有用的，因为扩展件安装完时想要增加命令。
入口点都描述在 :file:`setup.py` 文件里::

    from setuptools import setup

    setup(
        name='flask-my-extension',
        ...,
        entry_points={
            'flask.commands': [
                'my-command=flask_my_extension.commands:cli'
            ],
        },
    )


.. _entry point: https://packaging.python.org/tutorials/distributing-packages/#entry-points

在 :file:`flask_my_extension/commands.py` 文件里你可以导出一个 Click 模块对象::

    import click

    @click.command()
    def cli():
        ...

一旦在与你的 Flask 项目相同的虚拟环境中安装完那样的包，
你可以运行 ``flask my-command`` 来使用命令。


.. _custom-scripts:

自定义脚本
--------------

当你正在使用网络应用工厂模式时，定义你自己的 Click 脚本也许更方便。
而不是使用 ``FLASK_APP`` 环境变量后让 Flask 加载你的网络应用，
你可以建立你自己的 Click 对象后导出成一个 `console script`_ 控制台脚本入口点。

建立一个 :class:`~cli.FlaskGroup` 类的实例后代入到工厂函数里::

    import click
    from flask import Flask
    from flask.cli import FlaskGroup

    def create_app():
        app = Flask('wiki')
        # other setup
        return app

    @click.group(cls=FlaskGroup, create_app=create_app)
    def cli():
        """Management script for the Wiki application."""

在 :file:`setup.py` 文件中定义入口点::

    from setuptools import setup

    setup(
        name='flask-my-extension',
        ...,
        entry_points={
            'console_scripts': [
                'wiki=wiki:cli'
            ],
        },
    )

在虚拟环境中以可编辑模式来安装网络应用，并且自定义脚本是可用的。
注意你不需要设置 ``FLASK_APP`` 环境变量了 ::

    $ pip install -e .
    $ wiki run

.. admonition:: 自定义脚本中的错误

    当使用一个自定义脚本的时候，如果你在模块层代码中介绍了一项错误的话，
    重载器会失败，因为重载器不再加载入口点。

    那么 ``flask`` 命令，要从你的代码中分离出来，
    这样就没这种问题了，并且大多数案例中都推荐这样解决。

.. _console script: https://packaging.python.org/tutorials/distributing-packages/#console-scripts


PyCharm 集成
-------------------

PyCharm 2018.1 以前的版本都没有集成 Flask CLI 特性。
我们要做点微调工作来让 CLI 特性工作起来顺畅。
这些指导应该类似你使用的其它任何一个 IDE 集成环境。

在 PyCharm 中， 使用你的项目打开，点击菜单栏上的 *Run* 运行按钮后进入
 *Edit Configurations* 编辑配置。与下面的截图类似：

.. image:: _static/pycharm-runconfig.png
    :align: center
    :class: screenshot
    :alt: screenshot of pycharm's run configuration settings

这里有几个选项要改变一下，一旦我们完成一个命令的配置后，
我们可以轻易地复制整个配置后只做单项微调就完成另一个命令的配置，
包括任何一个你自己部署的自定义命令。

点击 + (*Add New Configuration*) 加号按钮后选择 *Python* 选项。
给配置起一个良好的名字，例如 "Run Flask Server" 达到顾名思义的效果。
对于 ``flask run`` 命令来说，勾选 "Single instance only" 选项，
因为你同一个时间不能运行多于一次的服务器。

从下拉菜单 (**A**) 选择 *Module name* 后输入 ``flask`` 内容。

参数 *Parameters* 区域 (**B**) 设置成要执行的命令行命令
(可以带任意数量的参数)。在这里的例子中我们使用 ``run`` 这个命令，
它会运行开发服务器。

如果你正在使用 :ref:`dotenv` 参考文档的话，你可以跳过这里，进入下一步骤。
我们需要增加一个环境变量 (**C**) 来识别我们的网络应用。
单击浏览按钮后在左边增加一个 ``FLASK_APP`` 入口后，
在右边增加 Python 导入的入口或文件 ( 例如 ``hello`` )。

下一步我们需要设置工作目录 (**D**) 就是我们网络应用所在的文件夹。

如果你在虚拟环境里把你的项目安装成一个包的话，
你不要勾选 *PYTHONPATH* 选项 (**E**)。
这会与你稍后如何部署的网络应用更准确地匹配上。

单击 *Apply* 来保持配置，或点击 *OK* 来保存，然后关闭窗口。
在 PyCharm 主窗口选择配置后点击 play 按钮来运行服务器。

至此我们在 PyCharm 中有了一个配置运行 ``flask run`` 的命令，
我们可以复制这个配置后在 *Script* 参数改变不同的命令行命令，
例如， ``flask shell`` 命令即可。
