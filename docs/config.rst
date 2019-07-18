.. _config:

配置处理
======================

网络应用需要某种配置类型。有许多不同的配置你也许想要根据网络应用环境来改变，
像切换调试模式、设置密钥，和其它这类环境描述配置。

方法就是 Flask 常常设计成启动网络应用时需要配置才可用。
你可以在代码中硬编码配置，对于许多小型网络应用来说还不坏，
但这里有一些更好的方法。

如何独立加载你的配置文件，这里有一个配置对象可用，它保存了被加载的配置值：
:class:`~flask.Flask` 对象的 :attr:`~flask.Flask.config` 属性。
这个属性就是用来放置 Flask 自身某些配置值的地方，并且也可以放置扩展件的配置值。
而且这个属性也可以放置你自己的配置值。


基础配置
--------------------

这个 :attr:`~flask.Flask.config` 属性实际上是一个字典的子类，
并且可以像任何一个字典数据一样支持修改操作::

    app = Flask(__name__)
    app.config['TESTING'] = True

某些配置值也都是直接提供给 :attr:`~flask.Flask` 对象，
所以你可以直接读写它们::

    app.testing = True

要一次性更新多个键，你可以使用 :meth:`dict.update` 字典方法::

    app.config.update(
        TESTING=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
    )


环境与调试特性
------------------------------

对于 :data:`ENV` 和 :data:`DEBUG` 配置值来说都是特殊的，
因为如果值的改变是在网络应用已经完成配置之后，它们两个可能表现不一样。
为了可靠地设置环境和调试模式， Flask 使用了环境变量。

环境变量是用来指明 Flask、扩展件，和其它程序的，就像 Sentry 在
Flask 所运行的语境一样。使用 :envvar:`FLASK_ENV` 环境变量来控制运行语境，
并且默认值是 ``production`` 。

把 :envvar:`FLASK_ENV` 环境变量设置成 ``development`` 会开启调试模式。
``flask run`` 命令会在调试模式中默认使用交互式调试器和重载器。
要从环境中分开控制调试模式，使用 :envvar:`FLASK_DEBUG` 旗语环境变量。

.. versionchanged:: 1.0
    已加入 :envvar:`FLASK_ENV` 环境变量来分别控制开发环境和调试模式。
    开发环境开启调试模式。

要把 Flask 切换到开发环境和开启调试模式，把 :envvar:`FLASK_ENV` 设置成::

    $ export FLASK_ENV=development
    $ flask run

(在 Windows 系统上，使用 ``set`` 命令而不是 ``export`` 命令。)

上面的环境变量描述用法是推荐的方式。同时把 :data:`ENV` 和 :data:`DEBUG` 
设置在你的配置文件中也是可能的，或者设置在代码中，非常不鼓励你这样做。
因为它们无法通过 ``flask`` 命令提前读取，并且有的系统或扩展件已经根据
前面推荐的配置方法把值配置好了。


内置配置值
----------------------------

下面的配置值都是 Flask 内部使用的：

.. py:data:: ENV

    网络应用运行在什么环境中。Flask 和 扩展件根据环境也许开启各种行为表现，
    例如开启调试模式。 :attr:`~flask.Flask.env` 属性映射到这种配置的键上。
    通过 :envvar:`FLASK_ENV` 环境变量这种设置方法与在代码中设置也许有不同的表现。

    **当部署在生成环境中不要开启开发环境。**

    默认值是： ``'production'``

    .. versionadded:: 1.0

.. py:data:: DEBUG

    是否开启调试模式。当使用 ``flask run`` 命令来启动开发服务器时，
    一个交互式调试器会为无法处理的例外显示信息，而且当代码变更保存后会
    重新加载服务器。 :attr:`~flask.Flask.debug` 属性映射到这个配置键上。
    当 :data:`ENV` 配置成 ``'development'`` 时调试模式就开启了，
    然后通过 ``FLASK_DEBUG`` 环境变量来覆写属性值。如果在代码中配置也许有不同的表现。

    **当部署在生成环境中不要开启调试模式。**

    默认值是：如果 :data:`ENV` 是 ``'development'`` 的话，值是 ``True`` ，
    否则是 ``False``

.. py:data:: TESTING

    开启测试模式。例外都会被广播，这要比通过网络应用错误处理器来处理好。
    扩展件也可能改变其行为表现，对于测试来说就更容易了。
    你应该在你自己的测试中来开启。

    默认值是： ``False``

.. py:data:: PROPAGATE_EXCEPTIONS

    例外都会被二次抛出，这要比通过网络应用错误处理器来处理好。
    如果不配置这项配置值的话，如果开启 ``TESTING`` 或 ``DEBUG`` 的话，
    值会隐含为 ``True``

    默认值是： ``None``

.. py:data:: PRESERVE_CONTEXT_ON_EXCEPTION

    当一项例外发生时不删除请求语境。如果没有设置的话，开启 ``DEBUG`` 时它的值
    是 ``True`` 。这允许调试器在错误上反省请求数据，并且正常应该不需要直接进行设置。

    默认值是： ``None``

.. py:data:: TRAP_HTTP_EXCEPTIONS

    对于一个 ``HTTPException`` 例外类型来说没有一个处理器的话，
    会二次抛出被交互式调试器来处理，而不是返回成一个简答的错误响应。

    默认值是： ``False``

.. py:data:: TRAP_BAD_REQUEST_ERRORS

    尝试访问一个像 ``args`` 和 ``form`` 请求字典中没有的键时，
    会返回一个 400 败坏的请求错误页面。开启这项配置会把错误处理成
    一个未处理的例外，所以你会得到交互式调试器处理结果。这就是一个
    ``TRAP_HTTP_EXCEPTIONS`` 的更具体版本。如果没有设置此项，
    在调试模式中会被开启。

    默认值是： ``None``

.. py:data:: SECRET_KEY

    一个密钥会用来安全地发送给会话 cookie 信号，然后可以被例外或你的网络应用
    用来给其它任何安全相关的需求使用。它应该是一个长字节随机字符串，而且也接受
    unicode 编码。例如，把如下输出结果拷贝到你的配置项中::

        $ python -c 'import os; print(os.urandom(16))'
        b'_5#y2L"F4Q8z\n\xec]/'

    **当发布问题或提交代码时不要暴露密钥内容。**

    默认值是： ``None``

.. py:data:: SESSION_COOKIE_NAME

    会话 cookie 的名字。值可以变成你已经有相同名字的一个 cookie。

    默认值是： ``'session'``

.. py:data:: SESSION_COOKIE_DOMAIN

    会是合法的会话 cookie 域名匹配规则。如果没有设置此项，
    cookie 对于 :data:`SERVER_NAME` 的所有子域名会是合法的。
    如果值是 ``False`` 的话，cookie 的域名不会被设置。

    默认值是： ``None``

.. py:data:: SESSION_COOKIE_PATH

    会是合法的会话 cookie 路径。如果没设置此项，会根据 ``APPLICATION_ROOT`` 或
     ``/`` 来判断 cookie 是合法的。

    默认值是： ``None``

.. py:data:: SESSION_COOKIE_HTTPONLY

    浏览器不会允许 JavaScript 访问标记成 "HTTP only" 的 cookies 来实现安全部署。

    默认值是： ``True``

.. py:data:: SESSION_COOKIE_SECURE

    如果 cookie 标记了 "secure" 的话，浏览器只发送建立在 HTTPS 上的含有请求的 cookies。
    网络应用必须是部署在 HTTPS 上此项才有效。

    默认值是： ``False``

.. py:data:: SESSION_COOKIE_SAMESITE

    限制含有来自外部站点请求的 cookies 是如何被发送的。
    可以设置成 ``'Lax'`` （推荐值）或者设置成 ``'Strict'`` 。
    查看 :ref:`security-cookie` 参考文档。

    默认值是： ``None``

    .. versionadded:: 1.0

.. py:data:: PERMANENT_SESSION_LIFETIME

    如果 ``session.permanent`` 值是 ``True`` 的话，
    cookies 的过期时间会在未来设置成此项秒数值。既可以使用
    一个 :class:`datetime.timedelta` 值，也可以使用一个 ``int`` 值。

    Flask 的默认 cookie 部署验证加密签名不能大于此项配置值。

    默认值是： ``timedelta(days=31)`` (``2678400`` seconds)

.. py:data:: SESSION_REFRESH_EACH_REQUEST

    当 ``session.permanent`` 值是 ``True`` 的时候，控制 cookie 是否带着
    每个响应被发送出去。每次发送 cookie 的时候（默认）更依赖所保存的会话过期值，
    但使用更多带宽。无永久会话不会被此项影响。

    默认值是： ``True``

.. py:data:: USE_X_SENDFILE

    当服务文件时，设置 ``X-Sendfile`` 头部项配置，而不是设置含有 Flask 的服务数据。
    一些网络服务器，例如 Apache，认识此项配置并且服务数据更有效率。
    此项只在使用这种网络服务器时才有效。

    默认值是： ``False``

.. py:data:: SEND_FILE_MAX_AGE_DEFAULT

    当服务文件时，设置缓存控制最大时间给此项配置秒数值。
    既可以是一个 :class:`datetime.timedelta` 值，
    也可以是一个 ``int`` 值。在每个文件基础上来覆写这个值，
    在网络应用上或蓝图上使用 :meth:`~flask.Flask.get_send_file_max_age` 方法。

    默认值是： ``timedelta(hours=12)`` (``43200`` seconds)

.. py:data:: SERVER_NAME

    告诉网络应用要绑定到的主机地址和端口信息。
    对于子域名路由匹配支持是所需要的配置项。

    如何设置的话，如果 :data:`SESSION_COOKIE_DOMAIN` 没设置，
    会用做会话 cookie 域名。现代的网络浏览器不会允许为没有一个句号
    的域名设置 cookies 。要使用一个本地域名，把任何一个应该路由到
    网络应用的名字增加到 ``hosts`` 文件中，例如 ::

        127.0.0.1 localhost.dev

    如何设置的话， ``url_for`` 函数可以生成只含有一个网络应用语境的
    外部 URLs 网址，而不是生成一个请求语境。

    默认值是： ``None``

.. py:data:: APPLICATION_ROOT

    告诉网络应用挂载在网络服务器的什么路径上，
    也就是网络应用的 / 根路径代表了服务器上的那个路径。

    如果 ``SESSION_COOKIE_PATH`` 没有设置的话，会用给会话 cookie 路径。

    默认值是： ``'/'``

.. py:data:: PREFERRED_URL_SCHEME

    当没有在一个请求语境中的时候，使用此项计划来生成外部 URLs 地址。

    默认值是： ``'http'``

.. py:data:: MAX_CONTENT_LENGTH

    来自进入请求数据的字节读取不会超过此项配置值。
    如果没有设置此项并且请求没有描述一个 ``CONTENT_LENGTH`` 值的话，
    为了安全没有数据会被读取。

    默认值是： ``None``

.. py:data:: JSON_AS_ASCII

    把对象序列化成 ASCII 编码过的 JSON 对象。如果此项被禁用的话，
    JSON 对象会被返回成一个 unicode 字符串，或者通过 ``jsonify``
    编码成 ``UTF-8`` 内容。当在模版中把 JSON 翻译到 JavaScript 时
    此项设置涉及安全，并且应该典型保留开启状态。

    默认值是： ``True``

.. py:data:: JSON_SORT_KEYS

    根据字母来排序 JSON 对象的键。此项对于缓存来说是有用的，
    因为它确保了数据是序列化的，不在乎 Python 的哈希种子值是什么。
    同时此项设置也不是推荐使用的，因为你可以禁用此项配置来提升缓存成本上的性能。

    默认值是： ``True``

.. py:data:: JSONIFY_PRETTYPRINT_REGULAR

    ``jsonify`` 响应结果会含有新行、空格，和缩进字符，对于人类阅读来说更容易。
    在调试模式中总是开启的。

    默认值是： ``False``

.. py:data:: JSONIFY_MIMETYPE

    ``jsonify`` 响应的媒体类型。

    默认值是： ``'application/json'``

.. py:data:: TEMPLATES_AUTO_RELOAD

    当模版变更保存后重载模版。如果没设置此项，
    在调试模式中会被开启。

    默认值是： ``None``

.. py:data:: EXPLAIN_TEMPLATE_LOADING

    记录调试信息追踪一个模版文件是如何被加载的。
    这对于弄清楚为什么一个模版没被加载是有用的，
    或者弄清楚加载了错误的文件。

    默认值是： ``False``

.. py:data:: MAX_COOKIE_SIZE

    如果 cookie 头部比此项字节配置值还大的话，发出警告。
    默认字节大小是 ``4093`` 。
    比这大的 cookies 也许会被浏览器默不作声的忽略。
    设置成 ``0`` 是禁用警告。

.. versionadded:: 0.4
   ``LOGGER_NAME``

.. versionadded:: 0.5
   ``SERVER_NAME``

.. versionadded:: 0.6
   ``MAX_CONTENT_LENGTH``

.. versionadded:: 0.7
   ``PROPAGATE_EXCEPTIONS``, ``PRESERVE_CONTEXT_ON_EXCEPTION``

.. versionadded:: 0.8
   ``TRAP_BAD_REQUEST_ERRORS``, ``TRAP_HTTP_EXCEPTIONS``,
   ``APPLICATION_ROOT``, ``SESSION_COOKIE_DOMAIN``,
   ``SESSION_COOKIE_PATH``, ``SESSION_COOKIE_HTTPONLY``,
   ``SESSION_COOKIE_SECURE``

.. versionadded:: 0.9
   ``PREFERRED_URL_SCHEME``

.. versionadded:: 0.10
   ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``, ``JSONIFY_PRETTYPRINT_REGULAR``

.. versionadded:: 0.11
   ``SESSION_REFRESH_EACH_REQUEST``, ``TEMPLATES_AUTO_RELOAD``,
   ``LOGGER_HANDLER_POLICY``, ``EXPLAIN_TEMPLATE_LOADING``

.. versionchanged:: 1.0
    ``LOGGER_NAME`` and ``LOGGER_HANDLER_POLICY`` 被移除。
    查看 :ref:`logging` 参考文档了解关于此配置项的信息。

    已加入 :data:`ENV` 配置项来反映 :envvar:`FLASK_ENV` 环境变量。

    已加入 :data:`SESSION_COOKIE_SAMESITE` 配置项来控制
    会话 cookie 的 ``SameSite`` 选项。

    已加入 :data:`MAX_COOKIE_SIZE` 配置项来控制来自 Werkzeug 的一项警告。


从文件进行配置
----------------------

如果你存储在分开的一个文件中，配置就变得更加有用了，
单独的配置文件理想位置是在网络应用包之外。
这让通过各种打包工具来打包和分发你的网络应用变成可能
（:ref:`distribute-deployment` 参考文档）以及
以后再修改配置文件都变成可能了。

所以一个共同的模式就是如下形式::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

首先从 `yourapplication.default_settings` 模块加载配置，
然后用 :envvar:`YOURAPPLICATION_SETTINGS` 环境变量指向的配置文件来覆写配置项的值。
在启动网络服务器之前，这个环境变量可以在 Linux 或 OS X 系统上的 export 命令来设置::

    $ export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
    $ python run-app.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader...

在 Windows 系统上使用 `set` 内置命令来设置环境变量::

    > set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg

配置文件自身都要是真正的 Python 文件。
只有全大写的变量名的值才会稍后存储到配置对象中去。
所以确保使用全大写字母来写变量名作为配置的键名。

如下是一个配置文件内容的示例::

    # Example configuration
    DEBUG = False
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

确保要非常早的加载配置，这样当启动时扩展件才有能力访问配置。
在配置对象上也有其它的一些方法来从单独的文件加载配置。
对于一个完整的参考，阅读 :class:`~flask.Config` 类对象的文档。

从环境变量进行配置
--------------------------------------

另外就是使用环境变量来指向配置文件，你也许发现要从环境中直接控制你的配置项的值
是有用的（或者是需要的）。

在启动网络服务器之前，环境变量可以在 Linux 或 OS X 系统上用 `export` 命令来设置::

    $ export SECRET_KEY='5f352379324c22463451387a0aec5d2f'
    $ export DEBUG=False
    $ python run-app.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader...

在 Windows 系统上使用内置命令 `set` 来设置::

    > set SECRET_KEY='5f352379324c22463451387a0aec5d2f'
    > set DEBUG=False

同时这种实现方式是直接生效，重要的是记住环境变量值都是字符串，
它们都不是自动地解序成 Python 类型。

如下是在一个配置文件中使用环境变量来写配置的示例::

    # Example configuration
    import os

    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", default=False)
    if ENVIRONMENT_DEBUG.lower() in ("f", "false"):
        ENVIRONMENT_DEBUG = False

    DEBUG = ENVIRONMENT_DEBUG
    SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")


注意任何一个字符串值会解释成一个布尔 ``True`` 值，在 Python 中除了空字符串，
这点要注意一个环境变量要明确地设置成 ``False`` 值，不能用空字符串来代替。

确保最早来加载配置，所以当启动时扩展件才有能力访问配置。
在配置对象上也有其它的一些方法来从单独的文件加载配置。
对于一个完整的参考，阅读 :class:`~flask.Config` 类对象的文档。

配置的最好实行法
----------------------------

前面所提到的独立配置文件方法的缺点就是让测试变得有点困难。
对于这种问题通常没有一个 100% 的解决方案，但这里有两件事
你可以记住来提升经验:

1.  把你的网络应用建立在一个函数里，然后用在函数上注册蓝图的技术。
    这样你可以用不同的配置文件来建立你的网络应用多种实例，
    其中一种配置方案就是为单元测试提供的，这就容易多了。
    你可以使用这种方案来根据需要来代入配置。

2.  不要写导入时需要的配置代码。如果你限制了你自己只请求访问配置的话，
    你可以稍后根据需要重新配置对象。

.. _config-dev-prod:

开发与生产
------------------------

大多数网络应用需要更多的配置文件。这也是对生产服务器来说应该至少要采用分离配置思路，
而且一种配置使用在开发期间的。最容易的处理这种方法就是使用一个总会被加载的默认配置，
以及版本控制部分，和一个单独的配置文件根据需要来覆写配置项，如同上面示例所提示的::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

然后你就增加一个单独的 :file:`config.py` 配置文件后使用 `export` 来
``YOURAPPLICATION_SETTINGS=/path/to/config.py`` 设置配置文件路径，
就这样全都实现了。不管如何做到的，这里也有另外的可选方法。例如你可以使用导入或子类来实现。

在 Django 世界中非常受欢迎的就是在配置文件中实现明确地导入方式，
通过增加 ``from yourapplication.default_settings import *`` 语句在文件的顶部，
然后手动覆写那些变更配置项。你也可以检查一项环境变量，例如 ``YOURAPPLICATION_MODE`` 
后设置成 `production` 或 `development` 等等操作，然后根据这个导入不同的硬编码配置文件。

一种有趣的模式就是也会使用类和继承机制来写配置::

    class Config(object):
        DEBUG = False
        TESTING = False
        DATABASE_URI = 'sqlite:///:memory:'

    class ProductionConfig(Config):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(Config):
        DEBUG = True

    class TestingConfig(Config):
        TESTING = True

要启用这种配置，你只要把类调用到 :meth:`~flask.Config.from_object` 方法中::

    app.config.from_object('configmodule.ProductionConfig')

注意 :meth:`~flask.Config.from_object` 方法不实例化类对象。
如果你需要实例化类，例如访问一个财产项一样，那么你必须在调用
:meth:`~flask.Config.from_object` 方法之前来实现::

    from configmodule import ProductionConfig
    app.config.from_object(ProductionConfig())

    # Alternatively, import via string:
    from werkzeug.utils import import_string
    cfg = import_string('configmodule.ProductionConfig')()
    app.config.from_object(cfg)

实例化配置对象允许你在你的配置类内部使用 ``@property`` 财产装饰器::

    class Config(object):
        """Base config, uses staging database server."""
        DEBUG = False
        TESTING = False
        DB_SERVER = '192.168.1.56'

        @property
        def DATABASE_URI(self):         # Note: all caps
            return 'mysql://user@{}/foo'.format(self.DB_SERVER)

    class ProductionConfig(Config):
        """Uses production database server."""
        DB_SERVER = '192.168.19.32'

    class DevelopmentConfig(Config):
        DB_SERVER = 'localhost'
        DEBUG = True

    class TestingConfig(Config):
        DB_SERVER = 'localhost'
        DEBUG = True
        DATABASE_URI = 'sqlite:///:memory:'

这里有许多不同的方法，并且是根据你想要如何管理你的配置文件来决定。
不管如何做到的，如下是一份良好的建议清单：

-   保留一份版本控制中的默认配置文件。用此默认配置文件来生产新的配置，
    或者在覆写配置项值之前导入到你自己的配置文件中。
-   使用一个环境变量来切换配置文件。这种方法可以在 Python 解释器之外来实现，
    并且让开发和部署非常容易，因为你可以快速地、容易地切换不同的配置文件，
    还不触碰任何代码。如果你常常工作在不同的项目上，你甚至建立你自己的脚本来
    激活一个虚拟环境后为你导出开发版的配置文件。
-   在生产中使用一个像 `fabric`_ 一样的工具来分开推送代码和配置到生产服务器上。
    对于如何实现的一些细节，回顾 :ref:`fabric-deployment` 模式参考内容。

.. _fabric: https://www.fabfile.org/


.. _instance-folders:

实例文件夹
----------------

.. versionadded:: 0.8

Flask 0.8 介绍了实例文件夹。让 Flask 很长一段时间可以直接指向相对于网络应用目录
的路径变成可能（通过 :attr:`Flask.root_path` 属性来实现）。
这也曾是许多开发者如何加载存储在网络应用边上的配置。不幸的是，不管如何做到的，
这种技术只在如果网络应用不是放在包中才工作良好，在非包网络应用情况中根路径指向包内容。

在 Flask 0.8 中有一个新的属性被介绍到：
:attr:`Flask.instance_path` 属性。它指明了一个新的概念，名叫实例文件夹。
实例文件夹被设计成不在版本控制之下，并且要具体部署。实例文件夹是放置运行时的变化
或者配置文件的最好地方。

你既可以在建立 Flask 网络应用时明确地提供实例文件夹的路径，
也可以让 Flask 自动检测实例文件夹。对于明确地配置来说，使用
`instance_path` 参数::

    app = Flask(__name__, instance_path='/path/to/instance/folder')

请记住提供这个路径的时候 *必须* 是绝对路径。

如果 `instance_path` 参数没使用的话，会默认使用如下位置:

-   无安装的模块结构::

        /myapp.py
        /instance

-   无安装的包结构::

        /myapp
            /__init__.py
        /instance

-   安装的模块或包结构::

        $PREFIX/lib/python2.X/site-packages/myapp
        $PREFIX/var/myapp-instance

    ``$PREFIX`` 是 Python 安装的前缀。这可以是
    ``/usr`` 或你的虚拟环境中的安装路径。你可以输出
    ``sys.prefix`` 的值来查看要设置的前缀内容是什么。

由于配置对象提供了配置文件的加载，配置文件来自相对的文件名，
如果我们想要通过相对于实例路径的文件名来加载变更就变成可能了，
在配置文件中的相对路径的行为可以在“相对于网络应用根路径（默认）”
与“相对于实例文件夹”之间切换，相对于实例文件夹的切换通过把
`instance_relative_config` 参数代入到网络应用构造器中来实现::

    app = Flask(__name__, instance_relative_config=True)

如下是一个完整的示例，如何配置 Flask 从一个模块来提前加载配置，
然后从一个实例文件夹中的一个配置文件来覆写配置::

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)

到实例文件夹的路径可以通过 :attr:`Flask.instance_path` 属性找到。
Flask 也提供了一个快捷方法来打开实例文件夹中的一个配置文件，使用的就是
 :meth:`Flask.open_instance_resource` 方法。

这两种用法示例如下::

    filename = os.path.join(app.instance_path, 'application.cfg')
    with open(filename) as f:
        config = f.read()

    # or via open_instance_resource:
    with app.open_instance_resource('application.cfg') as f:
        config = f.read()
