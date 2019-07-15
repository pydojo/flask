.. _extension-dev:

Flask 扩展件开发
===========================

Flask 是一个微框架，经常需要一些重复的步骤来获得一个第三方库。
因为这些步骤最常出现在支持多项目上，所以建立了 `Flask Extension Registry`_ 。

如果你想要建立你自己的 Flask 扩展件来补充空白，
扩展件开发指导会帮助你建立你的扩展件，并且告诉你用户所期望你的扩展件会有那些表现。

.. _Flask Extension Registry: http://flask.pocoo.org/extensions/

解刨一个扩展件
-----------------------

许多扩展件都是位于一个名叫 ``flask_something`` 名字的包里。
其中 "something" 部分是你自己扩展件作用的识别名。
例如，如果你打算增加一个名叫 `simplexml` 到 Flask 的话，
那么你要把你自己的扩展件包命名成 ``flask_simplexml`` 形式。

实际的扩展件名（适合人阅读，达到顾名思义的效果）不管如何做到的，
扩展件名要如同 "Flask-SimpleXML" 这种形式。一定要确保包含 
"Flask" 名字部分在扩展件名里，首字母一定要大写。
这样用户就可以在他们的  :file:`setup.py` 文件里，
把依赖关系注册到你的扩展件上。

然而扩展件自身看起来是什么样子呢？一个扩展件会确保与多个 Flask 网络应用实例一次性工作在一起。
这是一项需求，因为许多人会使用许多模式，像使用 :ref:`app-factories` 参考文档中的模式来
建立他们的网络应用，因此能够帮助单元测试和支持多种配置功能。
由于这项硬件需求，你的网络应用支持那种表现就是至关重要的了。

大多数重要的扩展件必须要使用一个 :file:`setup.py` 文件来进行传送，
并且必须注册在 PyPI 上。同时开发检查连接才有效，所以人们可以容易安装开发版
到他们的虚拟环境中，而不是要手动下载后再安装。

Flask 扩展件必须采用一种 BSD， MIT 或其它开明的协议，
这样才会罗列在 Flask 扩展件注册页面上。
记住 Flask 扩展件注册页面是一个温和之地，
并且许多开发出来的库如果行为符合需求都会坦率地进行审阅。

你好 Flask 扩展件
-----------------

那么我们开始建立一个 Flask 扩展件吧。我们此时要建立的扩展件会提供
非常基础的 SQLite3 数据库支持。

首先我们要建立如下目录结构::

    flask-sqlite3/
        flask_sqlite3.py
        LICENSE
        README

最重要的文件内容都在这里：

setup.py
````````

下一个文件就是必须要有的 :file:`setup.py` 文件，该文件是用来安装你的 Flask 扩展件。
如下的内容都是你可以有效与扩展件一起工作的内容::

    """
    Flask-SQLite3
    -------------

    This is the description for that library
    """
    from setuptools import setup


    setup(
        name='Flask-SQLite3',
        version='1.0',
        url='http://example.com/flask-sqlite3/',
        license='BSD',
        author='Your Name',
        author_email='your-email@example.com',
        description='Very short description',
        long_description=__doc__,
        py_modules=['flask_sqlite3'],
        # if you would be using a package instead use packages instead
        # of py_modules:
        # packages=['flask_sqlite3'],
        zip_safe=False,
        include_package_data=True,
        platforms='any',
        install_requires=[
            'Flask'
        ],
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )

这些代码有点多，但你真的可以只使用 复制/粘贴 现有的例子内容后调整一下即可。

flask_sqlite3.py
````````````````

此时这个文件就是你的扩展件代码要写的地方。那么这样的一个扩展件实际上应该看起来是什么样子呢？
继续阅读吧，这样你就可以获得内部见解了。

初始化扩展件
-----------------------

许多扩展件会需要某种初始化步骤。例如，思考一个应用当前正连接到 SQLite 数据库，
如同文档（:ref:`sqlite3`）所建议的一样。
那么扩展件如何知道应用对象的名字呢？

非常直接：你把应用代入到扩展件中去即可。

这里有两种初始化一个扩展件的建议方法：

初始化函数：

    如果你的扩展件名叫 `helloworld` 的话，你也许有一个名叫
     ``init_helloworld(app[, extra_args])`` 的函数，
    该函数为那个应用初始化扩展件。它可以放在处理器等等之前或之后。

初始化类：

    类工作起来最像初始化函数方法，但可以稍后使用来进一步改变表现。
    例如查看 `OAuth extension`_ 是如何工作的：
    当有一个 `OAuth` 对象时，它提供了一些帮助函数，像
     `OAuth.remote_app` 函数是建立指向一个使用了 OAuth 的远程应用。

使用什么依据的是你有什么。对于 SQLite 3 的扩展件来说，
我们会使用基于类的方法，因为会用一个对象提供给用户，
该对象处理打开和关闭数据库连接。

当涉及你的这个类时，重要的是让类容易在模块层实现复用。
这意味着对象自身必不能在任何一种情况下存储任何一个应用的具体状态，
并且必须在不同的应用之间进行分享。

扩展件代码
------------------

这里的 `flask_sqlite3.py` 内容可以复制/粘贴::

    import sqlite3
    from flask import current_app, _app_ctx_stack


    class SQLite3(object):
        def __init__(self, app=None):
            self.app = app
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            app.config.setdefault('SQLITE3_DATABASE', ':memory:')
            app.teardown_appcontext(self.teardown)

        def connect(self):
            return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

        def teardown(self, exception):
            ctx = _app_ctx_stack.top
            if hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db.close()

        @property
        def connection(self):
            ctx = _app_ctx_stack.top
            if ctx is not None:
                if not hasattr(ctx, 'sqlite3_db'):
                    ctx.sqlite3_db = self.connect()
                return ctx.sqlite3_db


那么这些代码到底做了什么：

1.  第一 ``__init__`` 初始化方法得到一个可选的 app 对象后，
    如果提供了参数值会调用 ``init_app`` 方法。
2.  第二 ``init_app`` 方法实现后 ``SQLite3`` 对象可以不需要一个 app 对象就
    完成实例化过程。这个方法支持了工厂模式来建立一个网络应用。
    那么 ``init_app`` 方法会对数据库进行配置，如果没有提供配置的话，
    默认配置到一个内存形式的数据库中。另外 ``init_app`` 方法里
    采用了 ``teardown`` 处理器。
3.  第三我们定义了一个 ``connect`` 方法，它是打开一个数据库连接。
4.  最后我们增加了一项 ``connection`` 财产对象，它首先访问打开的数据库连接，
    然后把数据库连接存储在语境中。这也是推荐的处理资源的方法：
    第一次使用资源时遵循按需取回资源。

    注意这里我们把我们的数据库连接固定到顶层应用环境，
    使用的是 ``_app_ctx_stack.top`` 来实现的。
    扩展件都应该使用顶层环境来存储扩展件自身含有足够多层化命名的信息。

那么为什么我们决定在这里使用基于类的方法呢？
因为使用我们的扩展件时，会像如下这样使用::

    from flask import Flask
    from flask_sqlite3 import SQLite3

    app = Flask(__name__)
    app.config.from_pyfile('the-config.cfg')
    db = SQLite3(app)

然后你才可以在视图函数中使用数据库，就像::

    @app.route('/')
    def show_all():
        cur = db.connection.cursor()
        cur.execute(...)

同样如果你在一个请求范围之外的话，
你可以通过推送一个 app 环境来使用数据库::

    with app.app_context():
        cur = db.connection.cursor()
        cur.execute(...)

在 ``with`` 语句块结束位置上， teardown 处理会自动执行。

另外， ``init_app`` 方法是用来支持工厂模式建立网络应用的::

    db = SQLite3()
    # Then later on.
    app = create_app('the-config.cfg')
    db.init_app(app)

记住支持这种工厂模式来建立的网络应用是许可 Flask 扩展件使用的一项需求（描述在下面）。

.. admonition:: 关注 ``init_app``

   如你所见， ``init_app`` 确实没有把 ``app`` 分配给 ``self`` 参数名。
   这样做是有意义的！基于类的 Flask 扩展件必须只能把网络应用存储在对象上，
   这发生在网络应用代入到构造器。这样就告诉了扩展件：
   我对使用多个网络应用不感兴趣。

   当扩展件需要发现当前网络应用时，扩展件的确不指向网络应用，
   扩展件必须使用 :data:`~flask.current_app` 环境数据分配
   或者改变 API，采用的方式是一种你明确地可以代入网络应用。


使用 _app_ctx_stack
--------------------

在上面的示例中，在每个请求之前，一个 ``sqlite3_db`` 变量要分配给
 ``_app_ctx_stack.top`` 。在一个视图函数中，这个变量是使用
 ``SQLite3`` 的 ``connection`` 财产项来访问的。在释放一个请求
的过程中， ``sqlite3_db`` 连接被关闭。通过使用这种模式，
对于请求期间，任何一种需求都可以访问 *相同的* sqlite3 数据库连接。


从其它方面学习
-----------------

本文档只涉及到最小程度的扩展件开发内容。如果你想要学习更多扩展件开发，
最好的思路就是在 `Flask Extension Registry`_ 上查看我们已有的扩展件。
如果你自己无法学会，这里也有 `mailinglist`_ 邮件列表和 `IRC channel`_ 公共聊天室
两个渠道来获得看起来不错的 APIs 开发思路。
尤其是如果你毫无思路的话，在你动手开发之前得到更多的认知是非常不错的想法。
这不仅在别人想从你的扩展件中得到什么，得到有用的反馈，
而且也避免了许多开发者单枪匹马地工作中产生的同样问题。 

记住：良好的 API 设计是困难的事情，所以把你的项目介绍在邮件列表上，
让其他开发者们给你帮助会对你的 API 设计更有益处。

对于 API 来说最好的 Flask 扩展件都是分享共同习语的扩展件。
并且如果早期合作时这是唯一有效的方式。

验收扩展件
-------------------

Flask 也有验收扩展件的项目管理概念。验收扩展件都是要作为 Flask 自身测试的一部分，
这样确保扩展件不会在新释放版本上出现断裂情况。
这些验收完的扩展件都会罗列在 `Flask Extension Registry`_ 上，并且给出合适的标记。
如果你想要自己的的扩展件获得验收通过的话，你要遵循如下验收标准：

0.  一个验收完的 Flask 扩展件需要一名运维人员。因为扩展件的作者步伐会超越项目的进展，
    作为项目来说应该找到一名新的运维人员，包括全部源代码过渡期主机和 PyPI 源代码访问。
    如果没有运维人员的话，那么就由 Flask 核心团队来控制。
1.  一个验收完的 Flask 扩展件必须确实提供一个包名或者一个模块名，命名规则是
     ``flask_extensionname`` 形式。
2.  一个验收完的 Flask 扩展件必须移交一套测试套件，既可以使用 ``make test``
    也可以使用 ``python setup.py test`` 进行测试。
    对于使用 ``make test`` 的测试套件来说，扩展件要确保所有测试使用的依赖包自动安装。
    如果使用 ``python setup.py test`` 的测试套件，测试依赖要描述在
     :file:`setup.py` 文件中。测试套件也要是分发包中的一部分。
3.  验收完的扩展件的 APIs 要经过如下特性的检查：

   -   一个验收完的扩展件要支持多个网络应用运行在同一个 Python 进程中。
   -   对于建立所有网络应用来说必须使用工厂模式。

4.  一个验收完的 Flask 扩展件协议必须是 BSD/MIT/WTFPL 三种协议之一。
5.  一个验收完的 Flask 扩展件命名计划官方名字形式必须是 *Flask-ExtensionName* 
    或者是 *ExtensionName-Flask* 二者之一。
6.  验收完的国战件必须在 :file:`setup.py` 文件中定义所有的依赖包，
    这些依赖包必须在 PyPI 上可用。
7.  文档必须采用 `Official Pallets Themes`_ 中的 ``flask`` 主题形式。
8.  在 setup.py 文件中的描述（以及 PyPI 上的描述）要连接到文档里去，
    网站（如果有一个的话）必须有一个自动连接到安装开发版本（ ``PackageName==dev``）的地址。
9.  对于在 setup 脚本中的 ``zip_safe`` 旗语必须设置成 ``False`` ，即使扩展件是安全压缩技术。
10. 一个扩展件此时必须要支持 Python 3.4 以上的版本，以及支持 Python 2.7 版本。


.. _OAuth extension: https://pythonhosted.org/Flask-OAuth/
.. _mailinglist: http://flask.pocoo.org/mailinglist/
.. _IRC channel: http://flask.pocoo.org/community/irc/
.. _Official Pallets Themes: https://pypi.org/project/pallets-sphinx-themes/
