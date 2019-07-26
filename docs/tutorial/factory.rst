.. currentmodule:: flask

网络应用配置
=================

一个 Flask 网络应用就是一个 :class:`Flask` 类的实例。
与网络应用有关的每一件事，例如配置和 URLs 地址，
都会使用这个类来进行注册。

最直接的建立一个 Flask 网络应用方法就是在全局范围里
直接建立一个 :class:`Flask` 类实例，即在模块顶层上，
就像刚才的 "Hello, World!" 例子中所做的那样。
同时在某些情况中这是简单且有用的方法，但在项目长大时
会导致一些技巧性的问题。

代替全局范围中建立一个 :class:`Flask` 类实例，你会把
类实例建立在一个函数体中。这个函数就是众所周知的 *网络应用工厂* 模式。
任何一个配置、注册，和其它网络应用的配置都需要在函数体中来写，
最后要返回网络应用。


网络应用工厂
-----------------------

编码的时候到了！建立 ``flaskr`` 目录后在目录里增加一个
名叫 ``__init__.py`` 的文件。
这个 ``__init__.py`` 模块有双重责任：
1. 它会包含网络应用工厂。
2. 它告诉 Python 应该把 ``flaskr`` 目录视为一个包。

.. code-block:: none

    $ mkdir flaskr

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    import os

    from flask import Flask


    def create_app(test_config=None):
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

        if test_config is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile('config.py', silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)

        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # a simple page that says hello
        @app.route('/hello')
        def hello():
            return 'Hello, World!'

        return app

``create_app`` 函数就是网络应用工厂函数。
你会在本教程后面在工厂函数中增加许多内容，
此时它已经做了许多事情。

#.  ``app = Flask(__name__, instance_relative_config=True)`` 建立了
    :class:`Flask` 类实例 `app` 。

    *   ``__name__`` 变量作为第一个参数值，是当前dunder init 模块名。
        这样 `app` 就知道在什么地方配置一些路径，而且dunder name 就是
        告诉 `app` 这个信息的最佳人选。

    *   ``instance_relative_config=True`` 第二个参数是告诉 `app` 配置
        文件都在 :ref:`instance folder <instance-folders>` 目录里。
        这个实例目录放在 ``flaskr`` 包外面，并且可以保存本地数据，而这些
        本地数据不应该提交给版本控制系统，例如配置密钥和数据文件。

#.  :meth:`app.config.from_mapping() <Config.from_mapping>` 方法是
    设置 `app` 会使用的一些默认配置：

    *   :data:`SECRET_KEY` 密钥数据是被 Flask 和 Flask 扩展件使用，这样
        保证了数据安全。这里设置的 ``'dev'`` 只是为开发时提供了一个方便值，
        当部署网络应用时，例如你应该用 `os.urandom(64)` 生成一个64位随机密钥值。

    *   ``DATABASE`` 配置项是告诉 `app` SQLite 数据库文件会存储在什么地方。
        此处我们把数据库文件存储在
        :attr:`app.instance_path <Flask.instance_path>` 网络应用实例目录里，
        这个路径是 Flask 已经选好的。你会在下一篇文档中学习更多关于数据库内容。

#.  :meth:`app.config.from_pyfile() <Config.from_pyfile>` 方法覆写了
    默认配置，它会使用来自 ``config.py`` 配置文件中的内容来更新配置内容，
    如果这个配置文件在实例文件夹中的话就可以实现更新。例如，当部署的时候，
    可以把真正的 ``SECRET_KEY`` 密钥值写在这个配置文件里。

    *   ``test_config`` 参数也代入到工厂函数里，并且会用来替换实例配置。
        这是为了单元测试时使用的配置，你会在本教程后面来写单元测试时使用的
        配置，届时可以逐项修改开发配置值。

#.  :func:`os.makedirs` 函数是为了确保
    :attr:`app.instance_path <Flask.instance_path>` 实例目录存在。
    Flask 不会自动建立实例目录，但需要建立这样一个实例目录，因为你的项目会
    在实例目录中建立 SQLite 数据库文件。

#.  :meth:`@app.route() <Flask.route>` 方法是直接建立一个路由，所以你
    可以看到网络应用能够工作。它建立了一个连接，该链接就是在 URL ``/hello``
     地址和这个函数所返回的一个响应对象关联了起来，此处的响应对象就是一个字符串。


运行网络应用
-------------------

现在我们可以使用 ``flask`` 命令来运行网络应用。
在终端里要先告诉 Flask 在哪里找到网络应用，然后
再以开发模式来运行网络应用。记住，执行这些命令时，
你要在 ``flask-tutorial`` 目录中，而不是在
 ``flaskr`` 包路径下执行终端命令。

开发模式显示一个交互式调试器，不管什么时候一个页面
抛出例外时，调试器就会出现，并且不管你什么时候保存
改变网络应用代码后，服务器都会重启。
你可以不用管服务器的运行，只需要刷新一下浏览器页面
就可以，继续看下面的教程内容。

对于 Linux 和 Mac 操作系统来说：

.. code-block:: none

    $ export FLASK_APP=flaskr
    $ export FLASK_ENV=development
    $ flask run

对于 Windows 系统的 cmd 来说，使用 ``set`` 命令，而不是 ``export`` 命令：

.. code-block:: none

    > set FLASK_APP=flaskr
    > set FLASK_ENV=development
    > flask run

对于 Windows 系统的 PowerShell 来说，使用 ``$env:`` 而不是 ``set`` 命令：

.. code-block:: none

    > $env:FLASK_APP = "flaskr"
    > $env:FLASK_ENV = "development"
    > flask run

你会在终端里看到类似如下的输出结果：

.. code-block:: none

     * Serving Flask app "flaskr"
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 855-212-761

用浏览器访问 http://127.0.0.1:5000/hello 网址，你就可以看到页面上显示了
返回的字符串内容。恭喜你，你此时正在运行你的 Flask 网络应用呢！

继续阅读 :doc:`database` 文档内容。
