安全性考虑
=======================

网络应用常常面对各种安全问题，并且要想让每件事走在正轨上是非常困难的。
Flask 尽力为你解决其中较少的安全问题，但依然要你自己谨慎对待。

.. _xss:

跨站脚本攻击 (XSS)
--------------------------

跨站脚本是注射任意一个 HTML 的概念（并且使用了 JavaScript）到一个站点的内容中。
要想治愈这种类型到攻击，开发者们要正确地转义文本内容，这样不会包含任意 HTML 标签。
要想更多了解这方面的信息，查看维基百科中的文章：
`Cross-Site Scripting <https://en.wikipedia.org/wiki/Cross-site_scripting>`_

Flask 配置了 Jinja2 来自动转义所有值，除非你明确告诉引擎不转义。
自动转义的规则会把 XSS 问题全部排除在模版之外，但依然有几个地方需要你额外小心：

-   没有使用 Jinja2 来生成 HTML 模版内容。
-   在用户提交的数据上调用 :class:`~flask.Markup` 类。
-   从上传的文件中来发送 HTML 内容，永远不要这样做。使用
    ``Content-Disposition: attachment`` 头部来防止这类问题。
-   从上传的文件中来发送文本文件内容。有的浏览器正在使用内容类型猜测功能，
    根据前几个字节来猜测内容类型，所以一些用户会用诡计来让浏览器执行 HTML 内容。

另一件事是非常重要的，那就是没有引号包裹着的属性。同时 Jinja2 可以保护你远离 XSS 问题
就是通过转义 HTML 内容，这里有一件事是无法保护你的，那就是：通过属性注射的 XSS 攻击。
要计算这种攻击向量，一定要用单引号或双引号来包裹你的属性，即使是使用 Jinja 表达式时：

.. sourcecode:: html+jinja

    <input value="{{ value }}">

为什么需要引号来包裹属性值呢？因为如果你不这样做的话，一名攻击者可以轻易注射自定义
 JavaScript 处理器。例如，一名攻击者可以把如下 HTML+JavaScript 内容注射给你：

.. sourcecode:: html

    onmouseover=alert(document.cookie)

当用户把鼠标悬停在输入位置时， cookie 就会用来发出一个警告窗口给用户。
而不是把 cookie 显示给用户，一名邪恶的攻击者也许会执行任何其它 JavaScript 代码。
在组合上 CSS 注射时，攻击者也许可以让元素填充整个页面，所以用户只是移动鼠标到任何
一个地方就可以触发攻击代码。

这里有一种 XSS 问题，Jinja 引擎的转义功能无法保护这类攻击。
其中 ``a`` 标签的 ``href`` 属性可以包含一个 `javascript:` URI 地址，
如果没有正确地安全处理，在点击超链接时浏览器就会执行攻击代码。

.. sourcecode:: html

    <a href="{{ value }}">click here</a>
    <a href="javascript:alert('unsafe');">click here</a>

上面的这段模版代码就可以保护这种攻击，这就需要你设置 :ref:`security-csp` 响应头部。

跨站请求伪造攻击 (CSRF)
---------------------------------

另一个安全大问题就是 CSRF 攻击。这是一个非常多层化的话题，并且我不会在这里介绍细节，
只是从理论上来提醒你们如何防止此类攻击。

如果你的授权信息存储在 cookies 中的话，你就存在隐含的状态管理。
正在登录的状态是由一个 cookie 来控制的，并且 cookie 带着一个页面的请求被发送出去。
不幸的是，其中包含的请求是由第三方站点触发的。如果你忘记了，有的人也许能够欺骗你的
网络应用用户，使用社交关系来实现一些用户不知道的愚弄用户的事情。

就是说你有一个具体的 URL 地址，当你发送 ``POST`` 请求就会删除一个用户的侧写信息
（就是说 ``http://example.com/user/delete`` 这样的地址）。
如果一名攻击者此时建立了一个页面来发送一个 ``POST`` 请求给那个页面，带着一些
JavaScript 代码就可以欺骗某些用户来加载伪造的页面后，用户的侧写信息会被删除。

想象一下你们正在使用一款社交软件，社交软件的用户有上百万，而且有人会发送一张图片。
当用户点击图片的时候或收藏图片的时候就出发了刚才的那个页面请求，那么这些用户的信息
就都会被删除，同时用户还在欣赏着各种可爱的小猫图片却浑然不知。

那么你如何防止这种攻击呢？基本上对于每个修改服务器内容的请求，你既要使用一种一次性
令牌，也要把令牌存储在该会话的 cookie 中 **并且** 也要把一次性令牌带着表单数据
一起传输。服务器再次接收到数据之后，你接着比较两个令牌并确保令牌值是一样的。

为什么 Flask 不为你做这件事？因为防止这种攻击的理想位置都是发生在表单验证框架中，
Flask 核心没有表单框架。

.. _json-security:

JSON 安全问题
-------------

在 Flask 0.10 以前， :func:`~flask.jsonify` 函数不曾具有把顶层阵列序列化成 JSON 形式。
这是因为在顶层存在一项安全漏洞，那就是 ECMAScript 4

ECMAScript 5 关闭了这项漏洞，所以只有非主流浏览器依然存在这项漏洞。
所有浏览器都有一些其它严重的漏洞，查看如下开源内容了解细节
<https://github.com/pallets/flask/issues/248#issuecomment-59934857>`_ ，
所以 Flask 现在已经改变了 :func:`~flask.jsonify` 函数，此时可以支持序列化阵列功能了。

安全化头部
----------------

许多浏览器识别各种响应头部都是为了控制安全。我们建议在你的网络应用中为用户审阅如下每个头部信息。
在 `Flask-Talisman`_ 扩展件中可以用来为你管理 HTTPS 和安全化头部。

.. _Flask-Talisman: https://github.com/GoogleCloudPlatform/flask-talisman

HTTP 严谨传输安全 (HSTS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

告诉浏览器要把所有的 HTTP 请求都要转换成 HTTPS 进行传输，防止中间人攻击 (MITM) ::

    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security

.. _security-csp:

内容安全政策 (CSP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

告诉浏览器在哪里可以加载各种资源。这种头部应该不管什么时候都要使用，
而且需要一些工作来定义正确的政策给你的站点。一个非常严谨的政策会是::

    response.headers['Content-Security-Policy'] = "default-src 'self'"

- https://csp.withgoogle.com/docs/index.html
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy

未知内容类型选项
~~~~~~~~~~~~~~~~~~~~~~

强制浏览器遵循响应内容类型，而不是让浏览器来侦测响应内容类型。
因为浏览器侦测响应内容类型会导致滥用职权生成跨站攻击 (XSS) ::

    response.headers['X-Content-Type-Options'] = 'nosniff'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options

未知帧选项
~~~~~~~~~~~~~~~

防止外部站点把你的站点嵌入到一个 ``iframe`` 标签中。这就可以防止鼠标点击攻击，
因为发生在嵌入式中的鼠标点击会被翻译成看不见的鼠标点击动作，而实际上又点击了你的
页面上的元素内容。这就是鼠标点击劫持攻击 ::

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options

未知XSS保护
~~~~~~~~~~~~~~~~

浏览器会尝试防止 XSS 攻击的影响，通过不加载页面的方式实现。如果请求包含了一些像 JavaScript
的代码内容，并且响应包含了同样的数据的话，就需要对这种未知的XSS攻击进行保护 ::

    response.headers['X-XSS-Protection'] = '1; mode=block'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection


.. _security-cookie:

设置 Cookie 选项
~~~~~~~~~~~~~~~~~~

这些选项可以加入到一个 ``Set-Cookie`` 头部中来提升选项的安全性。
Flask 具有一些配置选项在会话 cookie 上进行这些设置。
它们也可以设置在其它 cookies 上。

- ``Secure`` 只限制 HTTPS 流量上的 cookies
- ``HttpOnly`` 保护使用 JavaScript 读取的 cookies 内容。
- ``SameSite`` 限制来自外部站点使用请求如何发送 cookies，
  可以设置成 ``'Lax'`` （推荐）或者设置成 ``'Strict'`` 。
  ``Lax`` 是防止来自外部站点使用 CSRF 证明请求来发送 cookies，
  例如外部站点提交的一个表单。
  ``Strict`` 防止使用所有外部请求来发送 cookies，包括如下正规链接。

::

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

    response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')

描述 ``Expires`` 或 ``Max-Age`` 选项，会在已知的时间后删除 cookie 内容，
或者当前时间加上一个时限后删除 cookie 内容。
如果这两个选项都没有设置的话，cookie 会在浏览器关闭后删除。 ::

    # cookie expires after 10 minutes
    response.set_cookie('snakes', '3', max_age=600)

对于会话 cookie 来说，如果 :attr:`session.permanent <flask.session.permanent>` 属性
设置了的话，那么 :data:`PERMANENT_SESSION_LIFETIME` 数据对象就用来设置过期时间。
Flask 的默认 cookie 部署验证加密签名不能小于这个时间值。
较低的值也许帮助减轻重复攻击，其中拦截过的 cookies 可以在稍晚的时间点被发送。 ::

    app.config.update(
        PERMANENT_SESSION_LIFETIME=600
    )

    @app.route('/login', methods=['POST'])
    def login():
        ...
        session.clear()
        session['user_id'] = user.id
        session.permanent = True
        ...

使用 :class:`itsdangerous.TimedSerializer` 类来签名和验证其它的 cookie 值
（或者任何一个需要安全签名的值）。

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie

.. _samesite_support: https://caniuse.com/#feat=same-site-cookie-attribute


HTTP 公匙锁定 (HPKP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

这个会告诉浏览器去授权服务器只使用描述的证书要是来防止 MITM (HTTP 安全传输）攻击。

.. 警告::
   当开启这项时要小心，因为如果你不正确地配置或升级你的公匙的话，它非常难于撤销。

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning
