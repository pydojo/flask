.. _api:

API
===

.. module:: flask

本文档部分涵盖所有 Flask 的接口。
对于这些部分来说，都是 Flask 依据外部库的内容，
我们针对最重要的内容进行文档化工作，并且提供了权威文档的连接给你们。


网络应用对象
------------------

.. autoclass:: Flask
   :members:
   :inherited-members:


蓝图对象
-----------------

.. autoclass:: Blueprint
   :members:
   :inherited-members:

进入的请求数据
---------------------

.. autoclass:: Request
   :members:
   :inherited-members:

   .. attribute:: environ

      依据 WSGI 环境。

   .. attribute:: path
   .. attribute:: full_path
   .. attribute:: script_root
   .. attribute:: url
   .. attribute:: base_url
   .. attribute:: url_root

      提供了不同的方法来查看当前的 `IRI
      <https://tools.ietf.org/html/rfc3987>`_ 内容。
      想象一下你的网络应用正在监听如下网络应用根路径::

          http://www.example.com/myapplication

      并且一名用户对如下 URI 发送了一个请求::

          http://www.example.com/myapplication/%CF%80/page.html?x=y

      在这种情况中，上面提醒的属性值都要是如下内容：

      ============= ======================================================
      `path`        ``u'/π/page.html'``
      `full_path`   ``u'/π/page.html?x=y'``
      `script_root` ``u'/myapplication'``
      `base_url`    ``u'http://www.example.com/myapplication/π/page.html'``
      `url`         ``u'http://www.example.com/myapplication/π/page.html?x=y'``
      `url_root`    ``u'http://www.example.com/myapplication/'``
      ============= ======================================================


.. attribute:: request

   要访问进入的请求数据，你可以使用全局 `request` 对象。
   Flask 为你对进入的请求数据进行语法分析后，
   通过该全局对象给你访问进入的请求数据权限。
   如果你处于一种多线程环境中的话，对于激活的线程来说，
   Flask 在内部确保你一直获得正确的数据。

   这是一个代理。查看 :ref:`notes-on-proxies` 参考内容了解更多信息。

   请求对象是一个 :class:`~werkzeug.wrappers.Request` 子类的实例，
   并且提供了 Werkzeug 定义的所有属性。
   这里只展示最重要的一些属性概况。


响应对象
----------------

.. autoclass:: flask.Response
   :members: set_cookie, max_cookie_size, data, mimetype, is_json, get_json

   .. attribute:: headers

      一个 :class:`~werkzeug.datastructures.Headers` 类对象表示响应头部。

   .. attribute:: status

      含有一个响应状态的字符串。

   .. attribute:: status_code

      整数类型的响应状态。


会话
--------

如果你设置了 :attr:`Flask.secret_key` 属性
（或从 :data:`SECRET_KEY` 数据代理对象来配置），
那么你可以使用 Flask 网络应用中的会话。一个会话
是记住一个请求到另一个请求的信息用的。Flask 做到
这点是通过一个签名的 cookie 来实现的。用户可以看
会话的内容，但不能修改会话内容，除非他们知道密钥，
所以确保密钥内容设置成多层化的内容和无法猜到的值。

要访问当前会话，你可以使用 :class:`session` 类对象：

.. class:: session

   会话对象工作非常像一个普通的字典数据类型，唯一不同
   之处就是它保留了修改的追踪信息。

   这是一个代理。查看 :ref:`notes-on-proxies` 参考内容了解更多信息。

   下面的这些属性都是有趣的：

   .. attribute:: new

      如果会话是新的，属性值是 ``True`` ，否则属性值就是 ``False`` 。

   .. attribute:: modified

      如果会话对象检测到一项修改的话，属性值是 ``True`` 。
      劝告你在可变的数据类型上发生的修改不会自动选择，在这时
      你自己要明确地把属性值设置成 ``True`` 。如下是一个例子::

          # this change is not picked up because a mutable object (here
          # a list) is changed.
          session['objects'].append(42)
          # so mark it as modified yourself
          session.modified = True

   .. attribute:: permanent

      如果属性值设置成 ``True`` 的话，会话存活时间由
      :attr:`~flask.Flask.permanent_session_lifetime` 属性秒数值来决定，
      默认时间值是 31 天。
      如果此属性值设置成 ``False`` 的话（也是默认值），
      当用户关闭浏览器的时候会话也被删除。


会话接口
-----------------

.. versionadded:: 0.8

会话接口提供了替换 Flask 正在使用的会话部署的一个直接方法。

.. currentmodule:: flask.sessions

.. autoclass:: SessionInterface
   :members:

.. autoclass:: SecureCookieSessionInterface
   :members:

.. autoclass:: SecureCookieSession
   :members:

.. autoclass:: NullSession
   :members:

.. autoclass:: SessionMixin
   :members:

.. admonition:: 注意

   该 ``PERMANENT_SESSION_LIFETIME`` 配置键也可以是一个整数，
   从 Flask 0.8 开始可以这样配置。不管是你自己获得这个配置值，还是
   在网络应用上使用 :attr:`~flask.Flask.permanent_session_lifetime` 
   属性来配置，都会把配置值结果自动转换成一种整数类型。


测试客户端
--------------

.. currentmodule:: flask.testing

.. autoclass:: FlaskClient
   :members:


测试命令行运行器
--------------------

.. currentmodule:: flask.testing

.. autoclass:: FlaskCliRunner
    :members:


网络应用全局对象
-------------------

.. currentmodule:: flask

要分享数据，数据对于一个请求来说要是合法的，这个请求只来自一个函数要分享给另一个函数，
使用一个全局变量还不够好，因为在线程环境中会出现断裂情况。Flask 提供给你一个具体的
对象，这个对象确保对激活的请求来说是唯一的合法对象，并且该对象会针对每个请求返回不同
的值。在一个容器中：这个对象才能做正确的事情，就像它针对
:class:`request` 类和 :class:`session` 类所做的一样。

.. data:: g

    一个命名空间对象，它可以存储
    :doc:`application context </appcontext>` 文档所描述的数据。
    它是 :attr:`Flask.app_ctx_globals_class` 属性的一个实例，
    该属性是 :class:`ctx._AppCtxGlobals` 类的默认属性。

    在一个请求期间，这就是良好存储资源的地方。
    在测试期间，你可以使用 :ref:`faking-resources` 参考文档描述的模式
    来提前配置好这些资源。

    这是一个代理。查看 :ref:`notes-on-proxies` 参考内容了解更多信息。

    .. versionchanged:: 0.10
        该全局对象绑定到网络应用语境，而不是请求语境。

.. autoclass:: flask.ctx._AppCtxGlobals
    :members:


有用的函数和类
----------------------------

.. data:: current_app

    网络应用处理当前请求的一个代理。不需要导入网络应用就可以
    访问网络应用，或者如果网络应用无法导入的话，就像当使用
    网络应用工厂模式时，或者使用蓝图技术时，以及使用扩展件时。

    当 :doc:`application context </appcontext>` 文档
    所描述的语境推送完时，这个代理才可以使用。在请求期间和
    命令行命令期间，该代理会自动出现。它可以用
    :meth:`~flask.Flask.app_context` 方法手动控制。

    这是一个代理。查看 :ref:`notes-on-proxies` 参考内容了解更多信息。

.. autofunction:: has_request_context

.. autofunction:: copy_current_request_context

.. autofunction:: has_app_context

.. autofunction:: url_for

.. autofunction:: abort

.. autofunction:: redirect

.. autofunction:: make_response

.. autofunction:: after_this_request

.. autofunction:: send_file

.. autofunction:: send_from_directory

.. autofunction:: safe_join

.. autofunction:: escape

.. autoclass:: Markup
   :members: escape, unescape, striptags

消息闪存
----------------

.. autofunction:: flash

.. autofunction:: get_flashed_messages

JSON 支持
------------

.. module:: flask.json

Flask 使用 ``simplejson`` 来部署 JSON 支持。因为该模块即是标准库，
也是扩展件使用的模块，Flask 会先使用这个库，然后回滚到 Python 的标准
``json`` 库。在顶层上它会委托访问当前的网络应用 JSON 编码器和解码器，
这样自定义时更容易。

那么对于起始部分要这样做::

    try:
        import simplejson as json
    except ImportError:
        import json

你也可以只这样做::

    from flask import json

对于用法示例，阅读标准库中的 :mod:`json` 模块文档。如下扩展件都是
默认应用到 Python 标准库 json 模块上的：

1.  ``datetime`` 对象都是序列化成 :rfc:`822` 字符串形式。
2.  任何一个含有 ``__html__`` 方法的对象（像 :class:`~flask.Markup` 类一样），
    都会有一个这个方法，调用后返回的值都是序列化成字符串值。

这个 json 模块的 :func:`~htmlsafe_dumps` 函数也可以用做一个模版过滤器，
在 Jinja2 中叫做 ``|tojson`` 。注意，如果你要在  ``script``  标签中使用
``|tojson`` 过滤器输出结果的话，在 Flask 0.10 以前的版本中，你必须带着
``|safe`` 来禁用转义功能。在 Flask 0.10 以后的版本里，会自动包含安全过滤器
（但即便使用了 ``|safe`` 也是没有害处的）。

.. sourcecode:: html+jinja

    <script type=text/javascript>
        doSomethingWith({{ user.username|tojson|safe }});
    </script>

.. admonition:: 自动排序 JSON 键

    配置变量 ``JSON_SORT_KEYS`` (:ref:`config`) 可以设置成 false 来
    停用 Flask 自动排序 JSON 键。默认排序是开启的，并且是在网络应用语境之外
    来开启的。

    注意，当使用基于 HTTP 缓存的内容时，和使用 Python 的哈希随机特性时，
    禁用键排序能导致问题。

.. autofunction:: jsonify

.. autofunction:: dumps

.. autofunction:: dump

.. autofunction:: loads

.. autofunction:: load

.. autoclass:: JSONEncoder
   :members:

.. autoclass:: JSONDecoder
   :members:

.. automodule:: flask.json.tag

模版翻译
------------------

.. currentmodule:: flask

.. autofunction:: render_template

.. autofunction:: render_template_string

.. autofunction:: get_template_attribute

配置
-------------

.. autoclass:: Config
   :members:


流助手
--------------

.. autofunction:: stream_with_context

有用的内部
----------------

.. autoclass:: flask.ctx.RequestContext
   :members:

.. data:: _request_ctx_stack

    内部 :class:`~werkzeug.local.LocalStack` 类是保存
    :class:`~flask.ctx.RequestContext` 类实例的。典型
    :data:`request` 代理和 :data:`session` 代理对象应该
    被访问，而不是访问堆栈。在扩展件代码中访问堆栈也许是有用的。

    如下属性一直出现在堆栈的每一层上：

    `app`
      激活 Flask 网络应用。

    `url_adapter`
      该 URL 适配器（URL猫）是用来匹配请求用的。

    `request`
      当前请求对象。

    `session`
      激活的会话对象。

    `g`
      含有所有 :data:`flask.g` 代理对象属性的一个对象。

    `flashes`
      针对闪存消息的一个内部缓存。

    示例用法::

        from flask import _request_ctx_stack

        def get_session():
            ctx = _request_ctx_stack.top
            if ctx is not None:
                return ctx.session

.. autoclass:: flask.ctx.AppContext
   :members:

.. data:: _app_ctx_stack

    内部 :class:`~werkzeug.local.LocalStack` 类是保存
    :class:`~flask.ctx.AppContext` 类实例的。典型来说，
    :data:`current_app` 代理和 :data:`g` 代理对象应该
    被访问，而不是访问堆栈。扩展件可以访问堆栈上的内容，作为
    一个命名空间来存储堆栈中的数据。

    .. versionadded:: 0.9

.. autoclass:: flask.blueprints.BlueprintSetupState
   :members:

.. _core-signals-list:

信号
-------

.. versionadded:: 0.6

.. data:: signals.signals_available

   如果信号系统可用，设置成 ``True`` 值。这种情况只有在安装了
   `blinker`_ 库时才可以使用。

如下信号出现在 Flask 中：

.. data:: template_rendered

   当一个模版成果翻译完成时，这个信号被发送。该信号被引入时带着
   把模版实例用做 `template` 和把语境作为字典（名叫 `context`）。

   订阅者示例::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import template_rendered
        template_rendered.connect(log_template_renders, app)

.. data:: flask.before_render_template
   :noindex:

   翻译模版进程之前，这个信号被发送。该信号被引入时带着
   把模版实例用做 `template` 和把语境作为字典（名叫 `context`）。

   订阅者示例::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import before_render_template
        before_render_template.connect(log_template_renders, app)

.. data:: request_started

   当请求语境被设置时，这个信号被发送，而且是在任何一个请求处理发生之前被发送。
   因为请求语境已经绑定完成，订阅者可以使用标准的全局代理对象访问请求，例如用
   :class:`~flask.request` 代理对象。

   订阅者示例::

        def log_request(sender, **extra):
            sender.logger.debug('Request context is set up')

        from flask import request_started
        request_started.connect(log_request, app)

.. data:: request_finished

   在响应对象发送给客户端之前，这个信号被发送。
   信号被代入到响应中，
   响应对象以 `response` 名字被发送出去。

   订阅者示例::

        def log_response(sender, response, **extra):
            sender.logger.debug('Request context is about to close down.  '
                                'Response: %s', response)

        from flask import request_finished
        request_finished.connect(log_response, app)

.. data:: got_request_exception

   当一个例外在请求处理期间出现时，这个信号被发送。
   信号是在标准例外处理介入 *之前* 被发送的，并且
   即使在调试模式中没有例外处理发生也是这样。例外
   本身作为 `exception` 被传递给订阅者。

   订阅者示例::

        def log_exception(sender, exception, **extra):
            sender.logger.debug('Got exception during processing: %s', exception)

        from flask import got_request_exception
        got_request_exception.connect(log_exception, app)

.. data:: request_tearing_down

   当请求被释放时，这个信号被发送。
   即使一个例外产生，这个信号一直会被调用。
   当前监听这个信号的函数都在正规释放处理器之后被调用，
   而且这不是你可以依赖的东西。

   订阅者示例::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import request_tearing_down
        request_tearing_down.connect(close_db_connection, app)

   作为 Flask 0.9 版本，这个信号也要被代入一个 `exc` 关键字参数，
   如果有一个例外的话，关键字参数就有一个指向导致释放动作的例外。

.. data:: appcontext_tearing_down

   当网络应用语境被释放时，这个信号被发送。
   即使有一个例外发生，这个信号一直会被调用。
   当前监听这个信号的函数都在正规释放处理器之后被调用，
   而且这不是你可以依赖的东西。

   订阅者示例::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import appcontext_tearing_down
        appcontext_tearing_down.connect(close_db_connection, app)

   这个信号也要被代入一个 `exc` 关键字参数，
   如果有一个例外的话，关键字参数就有一个指向导致释放动作的例外。

.. data:: appcontext_pushed

   当一个网络应用语境被推送时，这个信号被发送。
   发送者就是网络应用。这对于单元测试来说常常是有用的，
   因为在信息中为了临时使用钩子。对于实例来说，它可以用来
   提早设置一个资源到 `g` 代理对象上。

   示例用法::

        from contextlib import contextmanager
        from flask import appcontext_pushed

        @contextmanager
        def user_set(app, user):
            def handler(sender, **kwargs):
                g.user = user
            with appcontext_pushed.connected_to(handler, app):
                yield

   并且在测试代码中用法如下::

        def test_user_me(self):
            with user_set(app, 'john'):
                c = app.test_client()
                resp = c.get('/users/me')
                assert resp.data == 'username=john'

   .. versionadded:: 0.10

.. data:: appcontext_popped

   当一个网络应用语境被删除时，这个信号被发送。
   发送者就是网络应用。
   这个信号常常与 :data:`appcontext_tearing_down` 信号放在一起。

   .. versionadded:: 0.10


.. data:: message_flashed

   当网络应用正在闪存一个消息时，这个信号被发送。
   消息作为 `message` 关键字参数被发送，并且
   消息类别作为 `category` 。

   订阅者示例::

        recorded = []
        def record(sender, message, category, **extra):
            recorded.append((message, category))

        from flask import message_flashed
        message_flashed.connect(record, app)

   .. versionadded:: 0.10

.. class:: signals.Namespace

   如果 blinker 库可用的话，是 :class:`blinker.base.Namespace` 类的别名。
   否则是建立假信号的替身类。这个类对 Flask 扩展件来说是可用的，因为扩展件想要
   提供与 Flask 自身相同的回滚系统。

   .. method:: signal(name, doc=None)

      如果 blinker 库可用的话，为这个别名类建立一个新信号，
      否则返回一个假信号，假信号有一个发送方法，该方法什么也不做，
      但对所有其它操作会带着一个 :exc:`RuntimeError` 例外失败，
      包括连接操作。


.. _blinker: https://pypi.org/project/blinker/

.. _class-based-views:

基于类的视图
-----------------

.. versionadded:: 0.7

.. currentmodule:: None

.. autoclass:: flask.views.View
   :members:

.. autoclass:: flask.views.MethodView
   :members:

.. _url-route-registrations:

URL路由注册
-----------------------

通用中对于路由系统来说有3个方法来定义路由规则：

1.  你可以使用 :meth:`flask.Flask.route` 方法装饰器。
2.  你可以使用 :meth:`flask.Flask.add_url_rule` 方法函数。
3.  你可以直接访问基于 Werkzeug 路由系统，该系统被曝光成
    :attr:`flask.Flask.url_map` 属性。

路由中的变量部分可以用尖括号来描述 (``/user/<username>``) 。
在 URL 中默认的一个变量部分接收任何一个字符串，不能带一个反斜杠，
不管如何做到的，一个不同的转换器也可以使用 ``<converter:name>`` 来描述。

许多变量部分都代入到视图函数中作为关键字参数。

下面的这些转换器都是可以使用的：

=========== ===============================================
`string`    accepts any text without a slash (the default)
`int`       accepts integers
`float`     like `int` but for floating point values
`path`      like the default but also accepts slashes
`any`       matches one of the items provided
`uuid`      accepts UUID strings
=========== ===============================================

自定义转换器可以使用 :attr:`flask.Flask.url_map` 属性来定义。

如下是一些示例::

    @app.route('/')
    def index():
        pass

    @app.route('/<username>')
    def show_user(username):
        pass

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        pass

一个重要的钶细节要记住，那就是 Flask 如何处理以反斜杠结尾的路由。
思路是保持每个 URL 都是唯一情况，所以要实行如下规则：

1. 如果一个规则以一个反斜杠结尾的话，并且用户发送请求时没有使用一个反斜杠的话，
   用户会自动被重定向到有一个反斜杠的页面地址上。
2. 如果一个规则没有以一个反斜杠结尾的话，并且用户发送请求时带有一个反斜杠的话，
   就会抛出一个 404 找不到页面的响应代号。

这是与网络服务器如何处理静态文件是一致的。这就让安全地使用相对链接目标变成可能。

为相同的视图函数你也可以定义多个路由规则。不管如何做到的，它们都要是唯一的。
也可以描述默认规则是哪条。这里的示例就是为一个 URL 地址定义接收一种
可选的页面路由规则::

    @app.route('/users/', defaults={'page': 1})
    @app.route('/users/page/<int:page>')
    def show_users(page):
        pass

这种定义描述了 ``/users/`` 会是第一个页面的 URL 地址，并且
``/users/page/N`` 会是第 ``N`` 个页面的 URL 地址。

如果一个 URL 地址含有一项默认值的话，规则会被重定向到含有一个 301 重定向代号
的更简单形式。例如上面的例子中， ``/users/page/1`` 会被重定向到 ``/users/`` 规则上。
如果你的路由处理 ``GET`` 和 ``POST`` 请求方法的话，
确保默认路由只处理 ``GET`` 请求方法，因为重定向不会保护表单数据。 ::

   @app.route('/region/', defaults={'id': 1})
   @app.route('/region/<id>', methods=['GET', 'POST'])
   def region(id):
      pass

如下这些参数都是 :meth:`~flask.Flask.route` 方法和
:meth:`~flask.Flask.add_url_rule` 方法接收的参数。
唯一不同的是含有路由参数的视图函数要用装饰器来定义，
取代了 `view_func` 参数。

=============== ==========================================================
`rule`          the URL rule as string
`endpoint`      the endpoint for the registered URL rule.  Flask itself
                assumes that the name of the view function is the name
                of the endpoint if not explicitly stated.
`view_func`     the function to call when serving a request to the
                provided endpoint.  If this is not provided one can
                specify the function later by storing it in the
                :attr:`~flask.Flask.view_functions` dictionary with the
                endpoint as key.
`defaults`      A dictionary with defaults for this rule.  See the
                example above for how defaults work.
`subdomain`     specifies the rule for the subdomain in case subdomain
                matching is in use.  If not specified the default
                subdomain is assumed.
`**options`     the options to be forwarded to the underlying
                :class:`~werkzeug.routing.Rule` object.  A change to
                Werkzeug is handling of method options.  methods is a list
                of methods this rule should be limited to (``GET``, ``POST``
                etc.).  By default a rule just listens for ``GET`` (and
                implicitly ``HEAD``).  Starting with Flask 0.6, ``OPTIONS`` is
                implicitly added and handled by the standard request
                handling.  They have to be specified as keyword arguments.
=============== ==========================================================

.. _view-func-options:

视图函数选项
---------------------

对于内部用法来说，视图函数都可以有一些属性附着后来自定义行为，
视图函数会正常地不具有控制权。
下面的这些属性可以选择地提供，既可以覆写一些默认行为到
:meth:`~flask.Flask.add_url_rule` 方法中或者覆写普通行为：

-   `__name__`: 一个函数的名字，默认用做端点。
    如果明确地提供了端点，这个值就被使用。
    另外这个值会是默认蓝图的名字前缀，不能在视图函数自身上进行自定义。

-   `methods`: 当 URL 规则增加时，如果方法都没有提供的话，
    如果一个 `methods` 属性存在的话，Flask 会看视图函数对象自身。
    如果函数实现了方法，那么就会把方法的信息拉取过来给这个属性值。

-   `provide_automatic_options`: 如果这个属性被设置的话，Flask 会
    即可以开启，也可以禁用 HTTP ``OPTIONS`` 响应的自动化部署。
    当与装饰器一起工作时这是有用的，因为装饰器想要在预先看到基础上
    自定义 ``OPTIONS`` 响应。

-   `required_methods`: 如果这个属性被设置的话，Flask 会在注册一个
    URL 路由规则时一直增加这些方法，即使在 ``route()`` 调用中方法都
    被覆写了也会增加这些方法。

完整的示例是::

    def index():
        if request.method == 'OPTIONS':
            # custom options handling here
            ...
        return 'Hello World!'
    index.provide_automatic_options = False
    index.methods = ['GET', 'OPTIONS']

    app.add_url_rule('/', index)

.. versionadded:: 0.8
   该 `provide_automatic_options` 功能已加入。

命令行接口
----------------------

.. currentmodule:: flask.cli

.. autoclass:: FlaskGroup
   :members:

.. autoclass:: AppGroup
   :members:

.. autoclass:: ScriptInfo
   :members:

.. autofunction:: load_dotenv

.. autofunction:: with_appcontext

.. autofunction:: pass_script_info

   Marks a function so that an instance of :class:`ScriptInfo` is passed
   as first argument to the click callback.

.. autodata:: run_command

.. autodata:: shell_command
