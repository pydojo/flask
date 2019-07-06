.. currentmodule:: flask

Flask 变更日志
===============


版本 1.1
-----------

未发布

-   :meth:`flask.RequestContext.copy` includes the current session
    object in the request context copy. This prevents ``session``
    pointing to an out-of-date object. (`#2935`_)
-   Using built-in RequestContext, unprintable Unicode characters in
    Host header will result in a HTTP 400 response and not HTTP 500 as
    previously. (`#2994`_)
-   :func:`send_file` supports :class:`~os.PathLike` objects as
    described in PEP 0519, to support :mod:`pathlib` in Python 3.
    (`#3059`_)
-   :func:`send_file` supports :class:`~io.BytesIO` partial content.
    (`#2957`_)

.. _#2935: https://github.com/pallets/flask/issues/2935
.. _#2957: https://github.com/pallets/flask/issues/2957
.. _#2994: https://github.com/pallets/flask/pull/2994
.. _#3059: https://github.com/pallets/flask/pull/3059


Version 1.0.3
-------------

Unreleased

-   :func:`send_file` encodes filenames as ASCII instead of Latin-1
    (ISO-8859-1). This fixes compatibility with Gunicorn, which is
    stricter about header encodings than PEP 3333. (`#2766`_)
-   Allow custom CLIs using ``FlaskGroup`` to set the debug flag without
    it always being overwritten based on environment variables.
    (`#2765`_)
-   ``flask --version`` outputs Werkzeug's version and simplifies the
    Python version. (`#2825`_)
-   :func:`send_file` handles an ``attachment_filename`` that is a
    native Python 2 string (bytes) with UTF-8 coded bytes. (`#2933`_)
-   A catch-all error handler registered for ``HTTPException`` will not
    handle ``RoutingException``, which is used internally during
    routing. This fixes the unexpected behavior that had been introduced
    in 1.0. (`#2986`_)

.. _#2766: https://github.com/pallets/flask/issues/2766
.. _#2765: https://github.com/pallets/flask/pull/2765
.. _#2825: https://github.com/pallets/flask/pull/2825
.. _#2933: https://github.com/pallets/flask/issues/2933
.. _#2986: https://github.com/pallets/flask/pull/2986


Version 1.0.2
-------------

Released on May 2nd 2018

-   Fix more backwards compatibility issues with merging slashes between
    a blueprint prefix and route. (`#2748`_)
-   Fix error with ``flask routes`` command when there are no routes.
    (`#2751`_)

.. _#2748: https://github.com/pallets/flask/pull/2748
.. _#2751: https://github.com/pallets/flask/issues/2751


Version 1.0.1
-------------

Released on April 29th 2018

-   Fix registering partials (with no ``__name__``) as view functions.
    (`#2730`_)
-   Don't treat lists returned from view functions the same as tuples.
    Only tuples are interpreted as response data. (`#2736`_)
-   Extra slashes between a blueprint's ``url_prefix`` and a route URL
    are merged. This fixes some backwards compatibility issues with the
    change in 1.0. (`#2731`_, `#2742`_)
-   Only trap ``BadRequestKeyError`` errors in debug mode, not all
    ``BadRequest`` errors. This allows ``abort(400)`` to continue
    working as expected. (`#2735`_)
-   The ``FLASK_SKIP_DOTENV`` environment variable can be set to ``1``
    to skip automatically loading dotenv files. (`#2722`_)

.. _#2722: https://github.com/pallets/flask/issues/2722
.. _#2730: https://github.com/pallets/flask/pull/2730
.. _#2731: https://github.com/pallets/flask/issues/2731
.. _#2735: https://github.com/pallets/flask/issues/2735
.. _#2736: https://github.com/pallets/flask/issues/2736
.. _#2742: https://github.com/pallets/flask/issues/2742


版本 1.0
-----------

发布于 April 26th 2018

-   **不再支持 Python 2.6 和 3.3 版本。** (`pallets/meta#24`_)
-   最新稳定版本所需要的依赖库最小版本号：
    Werkzeug >= 0.14, Jinja >= 2.10, itsdangerous >= 0.24, Click >= 5.1.
    (`#2586`_)
-   当一个 Flask 应用从命令行运行时，跳过 :meth:`app.run <Flask.run>` 方法。
    这样避免一些导致调试困惑的行为。
-   把 :data:`JSONIFY_PRETTYPRINT_REGULAR` 默认值变更为 ``False``
    函数 :func:`~json.jsonify` 默认返回一种紧凑格式，
    在调试模式中带有一种缩进格式。 (`#2193`_)
-   方法 :meth:`Flask.__init__ <Flask>` 接受 ``host_matching`` 参数，
    并且把参数设置在 :attr:`~Flask.url_map` 属性上。 (`#1559`_)
-   方法 :meth:`Flask.__init__ <Flask>` 接受 ``static_host`` 参数，
    并且当定义静态路线时把参数代入成 ``host`` 参数。 (`#1559`_)
-   函数 :func:`send_file` 在 ``attachment_filename`` 中支持 Unicode 编码。
    (`#2223`_)
-   把函数 :func:`url_for` 的 ``_scheme`` 参数代入到
    方法 :meth:`~Flask.handle_url_build_error` 中。 (`#2017`_)
-   方法 :meth:`~Flask.add_url_rule` 接受
    ``provide_automatic_options`` 参数来禁用增加 ``OPTIONS`` 方法。 (`#1489`_)
-   类 :class:`~views.MethodView` 的子类从基类继承方法处理器 (`#1936`_)
-   当在请求开始时打开会话，由应用错误处理器处理的请求会产生错误。 (`#2254`_)
-   蓝图获得 :attr:`~Blueprint.json_encoder` 和
    :attr:`~Blueprint.json_decoder` 属性来覆写应用的编码器和解码器。 (`#1898`_)
-   方法 :meth:`Flask.make_response` 对于坏的响应类型抛出 ``TypeError`` 例外，
    而不是 ``ValueError`` 例外。错误消息已经得到改善，描述为什么类型是非法的。
    (`#2256`_)
-   增加 ``routes`` 命令行命令来输出注册在应用上的路线。 (`#2259`_)
-   当会话 cookie 域是一个裸露主机名，或一个 IP 地址时显示警告。
    因为在有些浏览器中可能表现不正常，例如 Chrome 浏览器。 (`#2282`_)
-   允许 IP 地址完全作为会话 cookie 域。 (`#2282`_)
-   如果 ``SESSION_COOKIE_DOMAIN`` 通过 ``SERVER_NAME`` 检测到的话，
    说明 ``SESSION_COOKIE_DOMAIN`` 被设置了。 (`#2282`_)
-   从 ``FLASK_APP`` 调用 ``create_app`` 或 ``make_app`` 会自动检测
    无参数应用工厂。 (`#2297`_)
-   工厂函数都不需要一个 ``script_info`` 参数来与 ``flask`` 命令一起工作。
    如果工厂函数使用单一参数，或用了 ``script_info`` 参数的话，
    类 :class:`~cli.ScriptInfo` 对象会被代入。 (`#2319`_)
-   ``FLASK_APP`` 可以被设置到一个应用工厂上，如果需要可以带参数。
    例如： ``FLASK_APP=myproject.app:create_app('dev')``
    (`#2326`_)
-   ``FLASK_APP`` 可以指向没有安装的可编辑模式本地包，
    尽管 ``pip install -e`` 依然是好的包安装模式。
    (`#2414`_)
-   类 :class:`~views.View` 的属性
    :attr:`~views.View.provide_automatic_options` 被设置在
    :meth:`~views.View.as_view` 方法里，能被
    :meth:`~Flask.add_url_rule` 方法检测到。 (`#2316`_)
-   错误处理会尝试处理器注册 ``blueprint, code``,
    ``app, code``, ``blueprint, exception``, ``app, exception``
    (`#2314`_)
-   请求期间（和没有删除请求期间）如果会话被访问的话，
    ``Cookie`` 加入到响应的 ``Vary`` 头部。 (`#2288`_)
-   当建立基础 URL 时，使用 :meth:`~Flask.test_request_context` 方法接受
    ``subdomain`` 和 ``url_scheme`` 参数。
    (`#1621`_)
-   把 :data:`APPLICATION_ROOT` 默认设置成 ``'/'`` 值。当设置成 ``None`` 值时，
    隐含的默认值也是 ``'/'``
-   :data:`TRAP_BAD_REQUEST_ERRORS` is enabled by default in debug mode.
    ``BadRequestKeyError`` has a message with the bad key in debug mode
    instead of the generic bad request message. (`#2348`_)
-   Allow registering new tags with
    :class:`~json.tag.TaggedJSONSerializer` to support storing other
    types in the session cookie. (`#2352`_)
-   Only open the session if the request has not been pushed onto the
    context stack yet. This allows :func:`~stream_with_context`
    generators to access the same session that the containing view uses.
    (`#2354`_)
-   Add ``json`` keyword argument for the test client request methods.
    This will dump the given object as JSON and set the appropriate
    content type. (`#2358`_)
-   Extract JSON handling to a mixin applied to both the
    :class:`Request` and :class:`Response` classes. This adds the
    :meth:`~Response.is_json` and :meth:`~Response.get_json` methods to
    the response to make testing JSON response much easier. (`#2358`_)
-   Removed error handler caching because it caused unexpected results
    for some exception inheritance hierarchies. Register handlers
    explicitly for each exception if you want to avoid traversing the
    MRO. (`#2362`_)
-   Fix incorrect JSON encoding of aware, non-UTC datetimes. (`#2374`_)
-   Template auto reloading will honor debug mode even even if
    :attr:`~Flask.jinja_env` was already accessed. (`#2373`_)
-   The following old deprecated code was removed. (`#2385`_)

    -   ``flask.ext`` - import extensions directly by their name instead
        of through the ``flask.ext`` namespace. For example,
        ``import flask.ext.sqlalchemy`` becomes
        ``import flask_sqlalchemy``.
    -   ``Flask.init_jinja_globals`` - extend
        :meth:`Flask.create_jinja_environment` instead.
    -   ``Flask.error_handlers`` - tracked by
        :attr:`Flask.error_handler_spec`, use :meth:`Flask.errorhandler`
        to register handlers.
    -   ``Flask.request_globals_class`` - use
        :attr:`Flask.app_ctx_globals_class` instead.
    -   ``Flask.static_path`` - use :attr:`Flask.static_url_path`
        instead.
    -   ``Request.module`` - use :attr:`Request.blueprint` instead.

-   The :attr:`Request.json` property is no longer deprecated.
    (`#1421`_)
-   Support passing a :class:`~werkzeug.test.EnvironBuilder` or
    ``dict`` to :meth:`test_client.open <werkzeug.test.Client.open>`.
    (`#2412`_)
-   The ``flask`` command and :meth:`Flask.run` will load environment
    variables from ``.env`` and ``.flaskenv`` files if python-dotenv is
    installed. (`#2416`_)
-   When passing a full URL to the test client, the scheme in the URL is
    used instead of :data:`PREFERRED_URL_SCHEME`. (`#2430`_)
-   :attr:`Flask.logger` has been simplified. ``LOGGER_NAME`` and
    ``LOGGER_HANDLER_POLICY`` config was removed. The logger is always
    named ``flask.app``. The level is only set on first access, it
    doesn't check :attr:`Flask.debug` each time. Only one format is
    used, not different ones depending on :attr:`Flask.debug`. No
    handlers are removed, and a handler is only added if no handlers are
    already configured. (`#2436`_)
-   Blueprint view function names may not contain dots. (`#2450`_)
-   Fix a ``ValueError`` caused by invalid ``Range`` requests in some
    cases. (`#2526`_)
-   The development server uses threads by default. (`#2529`_)
-   Loading config files with ``silent=True`` will ignore
    :data:`~errno.ENOTDIR` errors. (`#2581`_)
-   Pass ``--cert`` and ``--key`` options to ``flask run`` to run the
    development server over HTTPS. (`#2606`_)
-   Added :data:`SESSION_COOKIE_SAMESITE` to control the ``SameSite``
    attribute on the session cookie. (`#2607`_)
-   Added :meth:`~flask.Flask.test_cli_runner` to create a Click runner
    that can invoke Flask CLI commands for testing. (`#2636`_)
-   Subdomain matching is disabled by default and setting
    :data:`SERVER_NAME` does not implicitly enable it. It can be enabled
    by passing ``subdomain_matching=True`` to the ``Flask`` constructor.
    (`#2635`_)
-   A single trailing slash is stripped from the blueprint
    ``url_prefix`` when it is registered with the app. (`#2629`_)
-   :meth:`Request.get_json` doesn't cache the
    result if parsing fails when ``silent`` is true. (`#2651`_)
-   :func:`Request.get_json` no longer accepts arbitrary encodings.
    Incoming JSON should be encoded using UTF-8 per :rfc:`8259`, but
    Flask will autodetect UTF-8, -16, or -32. (`#2691`_)
-   Added :data:`MAX_COOKIE_SIZE` and :attr:`Response.max_cookie_size`
    to control when Werkzeug warns about large cookies that browsers may
    ignore. (`#2693`_)
-   Updated documentation theme to make docs look better in small
    windows. (`#2709`_)
-   Rewrote the tutorial docs and example project to take a more
    structured approach to help new users avoid common pitfalls.
    (`#2676`_)

.. _pallets/meta#24: https://github.com/pallets/meta/issues/24
.. _#1421: https://github.com/pallets/flask/issues/1421
.. _#1489: https://github.com/pallets/flask/pull/1489
.. _#1559: https://github.com/pallets/flask/issues/1559
.. _#1621: https://github.com/pallets/flask/pull/1621
.. _#1898: https://github.com/pallets/flask/pull/1898
.. _#1936: https://github.com/pallets/flask/pull/1936
.. _#2017: https://github.com/pallets/flask/pull/2017
.. _#2193: https://github.com/pallets/flask/pull/2193
.. _#2223: https://github.com/pallets/flask/pull/2223
.. _#2254: https://github.com/pallets/flask/pull/2254
.. _#2256: https://github.com/pallets/flask/pull/2256
.. _#2259: https://github.com/pallets/flask/pull/2259
.. _#2282: https://github.com/pallets/flask/pull/2282
.. _#2288: https://github.com/pallets/flask/pull/2288
.. _#2297: https://github.com/pallets/flask/pull/2297
.. _#2314: https://github.com/pallets/flask/pull/2314
.. _#2316: https://github.com/pallets/flask/pull/2316
.. _#2319: https://github.com/pallets/flask/pull/2319
.. _#2326: https://github.com/pallets/flask/pull/2326
.. _#2348: https://github.com/pallets/flask/pull/2348
.. _#2352: https://github.com/pallets/flask/pull/2352
.. _#2354: https://github.com/pallets/flask/pull/2354
.. _#2358: https://github.com/pallets/flask/pull/2358
.. _#2362: https://github.com/pallets/flask/pull/2362
.. _#2374: https://github.com/pallets/flask/pull/2374
.. _#2373: https://github.com/pallets/flask/pull/2373
.. _#2385: https://github.com/pallets/flask/issues/2385
.. _#2412: https://github.com/pallets/flask/pull/2412
.. _#2414: https://github.com/pallets/flask/pull/2414
.. _#2416: https://github.com/pallets/flask/pull/2416
.. _#2430: https://github.com/pallets/flask/pull/2430
.. _#2436: https://github.com/pallets/flask/pull/2436
.. _#2450: https://github.com/pallets/flask/pull/2450
.. _#2526: https://github.com/pallets/flask/issues/2526
.. _#2529: https://github.com/pallets/flask/pull/2529
.. _#2586: https://github.com/pallets/flask/issues/2586
.. _#2581: https://github.com/pallets/flask/pull/2581
.. _#2606: https://github.com/pallets/flask/pull/2606
.. _#2607: https://github.com/pallets/flask/pull/2607
.. _#2636: https://github.com/pallets/flask/pull/2636
.. _#2635: https://github.com/pallets/flask/pull/2635
.. _#2629: https://github.com/pallets/flask/pull/2629
.. _#2651: https://github.com/pallets/flask/issues/2651
.. _#2676: https://github.com/pallets/flask/pull/2676
.. _#2691: https://github.com/pallets/flask/pull/2691
.. _#2693: https://github.com/pallets/flask/pull/2693
.. _#2709: https://github.com/pallets/flask/pull/2709


版本 0.12.4
--------------

发布于 April 29 2018

-   对 0.12.3 版本进行重新打包来修复包层次问题。 (`#2728`_)

.. _#2728: https://github.com/pallets/flask/issues/2728


版本 0.12.3
--------------

发布于 April 26th 2018

-   函数 :func:`Request.get_json` 不再接受任何一种编码。
    入口 JSON 应该每次使用 UTF-8 编码 :rfc:`8259`，
    但 Flask 会自动检测 UTF-8 UTF-16 或 UTF-32。(`#2692`_)
-   修复使用 ``python -m flask`` 时一个关于 Python 导入的警告。
    (`#2666`_)
-   修复某些情况中由于非法 ``Range`` 请求导致的一个 ``ValueError`` bug

.. _#2666: https://github.com/pallets/flask/issues/2666
.. _#2692: https://github.com/pallets/flask/issues/2692


版本 0.12.2
--------------

发布于 May 16 2017

- 修复Windows系统 `safe_join` 中的一个 bug

版本 0.12.1
--------------

Bug 修复，发布于 March 31th 2017

- 在已导入的应用模块中，当一项 ImportError 例外出现时，
  防止 `flask run` 显示一个 NoAppException 例外。
- 为 Python3 修复 ``app.config.from_pyfile`` 的编码行为。``#2118``
- 如果对于 ``app.run`` 作为默认值的话，使用 ``SERVER_NAME`` 配置项。
  ``#2109``, ``#2152``
- 调用 `ctx.auto_pop` 含带例外对象，而不是 `None`，在事件中是一个 `BaseException`
  就像一个请求处理器中抛出的 `KeyboardInterrupt` 一样。

版本 0.12
------------

发布于 December 21th 2016，代号 Punsch 潘趣酒

- 命令行命令现在有了 `--version` 选项。
- 对于类似文件的对象 Mimetype 猜测和 ETag 生成已经从 ``send_file`` 中移除，
  因为有如下问题 ``#104`` (`#1849`_)
- 在 ``send_file`` 中的 Mimetype 猜测现在明显失败，
  并且不回滚到 ``application/octet-stream`` (`#1988`_)
- 让 ``flask.safe_join`` 能够加入多个路径，就像 ``os.path.join`` 一样。
  (`#1730`_)
- 恢复一个行为变更，让开发服务器崩溃，而不是返回一项内部服务器错误。 (`#2006`_)
- 对于正常请求发送和错误处理器都会正确地引入响应处理器。
- 对于应用日志器，禁用默认日志器广播。
- 在 ``send_file`` 中增加范围请求支持。
- ``app.test_client`` 包含预置默认环境，现在可以直接设置默认环境，
  不再每次都用 ``client.get`` 来设置了。

.. _#1849: https://github.com/pallets/flask/pull/1849
.. _#1988: https://github.com/pallets/flask/pull/1988
.. _#1730: https://github.com/pallets/flask/pull/1730
.. _#2006: https://github.com/pallets/flask/pull/2006

版本 0.11.2
--------------

Bug 修复，未发布

- 修复了在 PyPy3 下运行时的崩溃。 (`#1814`_)

.. _#1814: https://github.com/pallets/flask/pull/1814

版本 0.11.1
--------------

Bug 修复，发布于 June 7th 2016

- 修复了一个 bug，该 bug 阻止来自工作中的 ``FLASK_APP=foobar/__init__.py``
  (`#1872`_)

.. _#1872: https://github.com/pallets/flask/pull/1872

版本 0.11
------------

发布于 May 29th 2016，代号 Absinthe 茴香酒

- 已加入顶层阵列序列化到 :func:`flask.jsonify` 函数的支持。这介绍了在老旧浏览器中的
  一项安全风险。查看 :ref:`json-security` 了解细节。
- 已加入 before_render_template 信号。
- 已把 `**kwargs` 多关键字参数加入到 :meth:`flask.Test.test_client` 方法中，
  为了支持把额外的关键字参数代入到 :attr:`flask.Flask.test_client_class` 
  属性构造器中。
- 已加入 ``SESSION_REFRESH_EACH_REQUEST`` 配置键，该键控制设置cookie行为。
  如果键值是 ``True`` 的话，每次请求一个永久会话会被刷新，并且获得生命周期的延续；
  如果键值是 ``False`` 的话，只在实际修改会话时才会修改永久会话。
  非永久绘画不会受到此项配置键的影响，并且关闭浏览器总会让非永久会话过期。
- 对于进入的数据来说，Flask 支持了自定义 JSON mimetypes 
- 已加入支持从一个视图函数返回的元组形式 ``(response, headers)``
- 已加入方法 :meth:`flask.Config.from_json`
- 已加入属性 :attr:`flask.Flask.config_class`
- 已加入方法 :meth:`flask.Config.get_namespace`
- debug 模式以外模版不再自动重新加载。自动加载模版功能可以用新的
  ``TEMPLATES_AUTO_RELOAD`` 配置键来设置。
- 针对 Python3.3 命名空间加载器的一个限制，加入了一种变通解决方案。
- 已加入使用 Python3.3 命名空间包时的明确根路径支持。
- 已加入 :command:`flask` 命令和 ``flask.cli`` 模块来启动本地调试服务器，
  通过鼠标点击 CLI 系统即可。这种更新要比老旧的 ``flask.run()`` 方法工作效率
  更快更可信赖，因为用了不同的设计并且也代替了 ``Flask-Script``
- 错误处理器在匹配具体的类别之前都先做检查，因此允许获得 HTTP 例外的子类类外，
  HTTP 例外都在 ``werkzeug.exceptions`` 中。这样的更新让一名扩展件作者可以
  选择 HTTP 错误作为默认例外结果，也可以用一种自定义错误处理捕获例外。
- 已加入方法 :meth:`flask.Config.from_mapping`
- Flask 日志现在是默认开启，即是禁用调试模式也有日志功能。日志格式现在是硬编码，
  但默认日志处理可以禁用，通过 ``LOGGER_HANDLER_POLICY`` 配置键设置。
- 删除不赞成的模块功能。
- 已加入 ``EXPLAIN_TEMPLATE_LOADING`` 配置键，当开启时会让 Flask 解释如何分配模版。
  这项配置在加载了错误的模版时帮助用户调试。
- 蓝图处理严格按照注册模版加载时的顺序进行。
- 已移植测试套件到 py.test
- 不赞成 ``request.json`` 用法，改为 ``request.get_json()`` 用法。
- 增加 "pretty" 和 "compressed" 分隔符定义到 jsonify() 方法里。
  减少 JSON 响应规模，当 JSONIFY_PRETTYPRINT_REGULAR=False 时默认移除分隔符后
  不需要的空白内容。
- JSON 响应现在都用一个新行字符来终止，因为方便 UNIX 文件已一个新行作为结束，
  并且一些客户端缺少这个新行字符无法获得良好的处理。查看
  https://github.com/pallets/flask/pull/1262 网址，内容都是原始中的一部分，
  原始内容网址是 https://github.com/kennethreitz/httpbin/issues/168
- 如果用户使用小写版本 ``options`` (issue ``#1288``)注册一个覆写规则的话，
  自动化提供的 ``OPTIONS`` 方法现在会正确地禁用。
- ``flask.json.jsonify`` 现在支持 ``datetime.date`` 类型 (`#1326`_)
- 不要把已捕获的例外信息泄露到语境管理器 teardown 处理器里。 (`#1393`_)
- 允许自定义 Jinja 环境子类。 (`#1422`_)
- 更新扩展件开发指导。

- ``flask.g`` 现在有了 ``pop()`` 和 ``setdefault`` 方法了。
- 默认为 ``flask.templating.render_template_string`` 打开自动化转义。
  (`#1515`_)
- 现在不赞成使用 ``flask.ext`` (`#1484`_)
- 如果文件名在服务器操作系统上非法的话，
  ``send_from_directory`` 现在抛出 BadRequest 例外 (`#1763`_)
- 已加入 ``JSONIFY_MIMETYPE`` 配置变量 (`#1728`_)
- 在 teardown 处理过程中出现的例外不再把坏应用保留在语境中。

.. _#1326: https://github.com/pallets/flask/pull/1326
.. _#1393: https://github.com/pallets/flask/pull/1393
.. _#1422: https://github.com/pallets/flask/pull/1422
.. _#1515: https://github.com/pallets/flask/pull/1515
.. _#1484: https://github.com/pallets/flask/pull/1484
.. _#1763: https://github.com/pallets/flask/pull/1763
.. _#1728: https://github.com/pallets/flask/pull/1728

版本 0.10.2
--------------

Bug 修复，发布日期待公布

- 已修复断裂的 `test_appcontext_signals()` 测试用例。
- 当 PEP 302 导入钩子使用时没有一个 `is_package()` 方法情况下，
  在 :func:`flask.helpers.find_package` 函数中使用一个有用的消息来解释
  为什么会产生一个 :exc:`AttributeError` 执行错误。
- 已修复一个问题，在把一个请求或者一个应用语境输入到 teardown 处理器之前，导致一些
  例外产生。
- 已修复一个问题，在测试客户端中当请求绝对 URL 地址时，使用查询参数会从请求中得到删除。
- 制作完 `@before_first_request` 到一个装饰器里作为以后使用。
- 已修复一个电子标签 bug，该 bug 发生在使用一个名字发送一个文件流时。
- 已修复 `send_from_directory` 不能正确地扩展到应用根路径上。
- 已变更逻辑，第一次请求处理器之前变成第一次处理之后翻转旗语。这会允许一些潜在的危险
  使用，但应该也是许可的。
- 已修复 Python 3 bug，当一个来自 `app.url_build_error_handlers` 的处理器会
  再次产生 `BuildError` 错误。

版本 0.10.1
--------------

Bug 修复，发布于 June 14th 2013

- 修复一个问题， ``|tojson`` 所在之处没有使用单引号会让过滤器在 HTML 属性里不正确
  地工作。现在使用在单引号属性中可以让过滤器正确工作了。这样做让与 angular.js 使用
  时更容易工作了。
- 已加入字节字符串的支持到会话系统中。否则为了令牌验证而把二进制数据放到会话里的共同
  情况中会破坏兼容性。
- 已修复一个问题，其中为同一个端点注册了两次同名方法会不正确地出发一个例外。

版本 0.10
------------

发布于 June 13th 2013，代号 Limoncello 柠檬酒

- 已变更默认 cookie 从 pickle 到 JSON 序列化格式，如果密钥泄露的话，
  达到限制一个追踪器能做什么。查看 :ref:`upgrading-to-010` 了解更多信息。
- 已加入 ``template_test`` 一些方法到已有的 ``template_filter`` 方法家族中。
- 已加入 ``template_global`` 一些方法到已有的 ``template_filter`` 方法家族中。
- 为 x-sendfile 设置内容长度头部信息。
- ``tojson`` 过滤器现在在 HTML5 语法分析器中不再转义脚本块语句了。
- 用在模版里的 ``tojson`` 现在默认为安全模式。这样做是因为转义表现存在差异。
- 如果你想要在一个已经使用的端点上注册一个新的函数，Flask 现在会产生一项错误。
- 已加入简单的 JSON 打包模块，并且也加入了时间对象的默认序列化。这样做允许更容易
  自定义如何通过 Flask 来处理 JSON 或者通过任何一个 Flask 扩展包也更容易处理了。
- 删除淘汰的内部 ``flask.session`` 模块别名。使用 ``flask.sessions`` 代替
  获得会话模块。这样就不会与 ``flask.session`` 会话代理混为一谈了。
- 许多模版现在可以不用请求语境进行翻译了。这种行为与 ``request``、 ``session``
  和 ``g`` 对象稍有不同，这三种对象不可以这样使用，以及蓝图语境处理器也不能这样调用。
- 配置对象现在可以用在模版中作为一个真正的全局范围对象，并且不用通过语境处理器，甚至
  默认导入到模版中。
- 已加入一个选项来生成非 ASCII 编码的 JSON 对象，这样应该在网络上减少字节传输。默认
  是关闭状态，为了与现有的库不产生困惑，而现有的库也许期望用 ``flask.json.dumps`` 
  来默认返回字节字符串。
- ``flask.g`` 现在存储在应用语境，而不是请求语境。
- ``flask.g`` 现在有了一个 ``get()`` 方法，为了不存在的元素不会出现错误。
- ``flask.g`` 现在可以与 ``in`` 操作符使用来查看定义了什么，并且
  此时是可迭代对象，以及会生成所有已存储的属性。
- ``flask.Flask.request_globals_class`` 已经更名为
  ``flask.Flask.app_ctx_globals_class`` 了，这个名字从 0.10 开始更合适。
- `request`、 `session` 和 `g` 现在也都增加成模版语境代理，这样在导入的模版中
  就可以使用了。有一点要非常小心，那就是在宏范围外的使用也许会产生缓存。
- 如果一个代理例外被代入的话，Flask 将不再介入错误处理器。
- 已加入一项在 localhost 中 chrome 浏览器的 cookies 解决方案，而不是与域名一起
  工作的解决方案。
- 已变更来自会话的 cookie 值默认腌制逻辑，这样会更好地与 Google Chrome 
  浏览器一起工作。
- 已加入 `message_flashed` 信号，可以简化闪存消息测试。
- 已加入请求语境副本支持，这样更好地与 greenlet 一起工作。
- 删除自定义 JSON HTTP 例外子类。如果你依赖这些子类的话，你可以自己写这些子类。
  使用这些子类不管怎么做到的，我们都是强烈不鼓励这样做，因为会导致接口溢出。
- Python 需求变更：目前为 Python 2.6 或 2.7 ，现在要为 Python 3.3 做准备了。
- 变更 teardown 系统如何呈现例外信息。此时在处理错误进程中半路介入处理一个例外的
  一些情况变得更加可靠。
- 请求语境保护在调试模式中现在保留例外信息，这样意味着 teardown 处理器都能够从成功
  情况里区分出错误来。
- 已加入 ``JSONIFY_PRETTYPRINT_REGULAR`` 配置变量。
- Flask 现在默认对 JSON 键进行排序，这样不会把 HTTP 缓存当成垃圾处理，因为
  不同的工作器之间存在不同的哈希种子。
- 已加入 `appcontext_pushed` 和 `appcontext_popped` 信号。
- 当在腌制默认端口上运行时，内置运行方法现在把 ``SERVER_NAME`` 放到账户中。
- 已加入 `flask.request.get_json()` 作为老旧的 `flask.request.json` 属性
  替换方法。

版本 0.9
-----------

发布于 July 1st 2012，代号 Campari 低度酒

- 函数 :func:`flask.Request.on_json_loading_failed` 现在默认返回一个 JSON 
  格式的响应结果。
- 函数 :func:`flask.url_for` 现在可以生成 HTML 链接锚点了。
- 函数 :func:`flask.url_for` 现在也可以准确地生成 URL 规则到一个给出的 HTTP 方法。
- 如果没有明确设置的话，日志现在只返回调试日志配置。
- 当终止请求时，不会在 WSGI 环境与请求对象之间注册一个回路依赖。这意味着响应返回给
  WSGI 服务器后 ``werkzeug.request`` 会是 ``None`` ，但在 CPython 上具有垃圾
  收集器优势会清理请求，除非用户自己建立回路依赖。
- 现在回调之后才存储会话，所以如果会话装载存储在会话中，你仍然可以在一个请求回调之后
  修改会话。
- 类 :class:`flask.Flask` 会避免导入已提供的导入名称，如果能够的话 (需要第一个参数)，
  有效的工具会以编程方式建立 Flask 实例。Flask 类会在系统上回到使用自定义模块钩子使用
  导入，例如，Google 应用引擎，或者当导入名称时在Python 2.7 以前版本位于一个压缩文档
  里时 (通常是一个 .egg 文件) 。
- 蓝图技术现在具有了一个装饰器来增加自定义模版过滤器应用方法 :meth:`flask.Blueprint.app_template_filter`
- Flask 和 Blueprint 类现在具有了一个非装饰器方法来增加自定义模版过滤器应用，分别是
  :meth:`flask.Flask.add_template_filter` 和
  :meth:`flask.Blueprint.add_app_template_filter`
- 函数 :func:`flask.get_flashed_messages` 现在允许在各自的块语句中翻译闪存消息类别，
  通过一个 ``category_filter`` 参数来实现。
- :meth:`flask.Flask.run` 方法现在接受参数 `host` 和 `port` 值为 ``None`` 时，
  使用默认值。这样对于调用 ``run`` 方法时允许使用配置值，例如：
  ``app.run(app.config.get('MYHOST'), app.config.get('MYPORT'))`` ，这样使用
  不管有没有提供一个配置文件都会有正确的表现。
- :meth:`flask.render_template` 方法现在即可以接受一种模版名的可迭代对象，也可以
  接受单个模版名。以前的话，只能接受单个模版名。在一个可迭代对象上，第一个找到的模版才
  会被翻译。
- 已加入 :meth:`flask.Flask.app_context` 方法，该方法工作类似请求语境，但只提供访问
  当前应用。这样也增加了对没有一个激活请求语境的 URL 生成支持。
- 视图函数现在可以返回一个元组了，其中第一个实例是 :class:`flask.Response` 类的实例。
  这样允许从一个视图函数返回 ``jsonify(error="error msg"), 400`` 结果。
- :class:`~flask.Flask` 类和 :class:`~flask.Blueprint` 类现在提供了一个
  :meth:`~flask.Flask.get_send_file_max_age` 方法钩子给子类来覆写来自 Flask 
  的静态文件服务行为，这要在 Flask 使用 :meth:`flask.Flask.send_static_file` 
  (默认静态文件处理器使用的) 方法和 :func:`~flask.helpers.send_file` 函数时有效。
  这个钩子要用一个文件名来提供，其中例如通过文件扩展允许改变缓存控制。对于 `send_file`
  默认最大时限和静态文件可以通过一个新的 ``SEND_FILE_MAX_AGE_DEFAULT`` 配置变量来
  设置，该配置变量用于 `get_send_file_max_age` 默认部署。
- 已修复一项会话部署使用外部存储时可能会打断闪存消息的会话部署假设。
- 变更了从函数返回元组值的行为。它们不再作为响应对象的参数，它们现在具有一种已经定义完的
  意义了。
- 已加入 :attr:`flask.Flask.request_globals_class` 属性来允许一个具体类用在每个
  请求实例 :data:`~flask.g` 数据建立上。
- 已加入 `required_methods` 属性给视图函数在注册上必须增加的方法。
- 已加入 :func:`flask.after_this_request` 函数。
- 已加入 :func:`flask.stream_with_context` 函数并且具备把语境多次推送的能力，不会
  产生意外表现。

版本 0.8.1
-------------

Bug 修复，发布于 July 1st 2012

- 已修复 Python 2.5 上使用无文档的 `flask.session` 模块无法正确工作的问题。以后不会
  这样用了，但曾经导致包管理器一些问题。

版本 0.8
-----------

发布于 September 29th 2011，代号 Rakija 蒸馏果酒

- 重构会话支持进入一个会话接口，这样部署的会话可以不用覆写 Flask 类就可以变更会话。
- 空会话 cookies 现在都自动地正确删除。
- 试图函数现在可以选择自动 OPTIONS 部署了。
- 现在可以获得 HTTP 例外与坏的请求错误，这样可以正常显示在回溯信息中。
- 在 Flask 调试模式中现在能检测一些共性问题，并且尽量提示给你。
- 如果一个试图函数在处理第一次请求之后出现，在 Flask 调试模式中现在会用一个判断错误
  来提示你。当用户忘记导入视图函数代码时，这会尽早给出反馈。
- 已加入在第一次请求开始时注册只触发一次的回调。 (:meth:`Flask.before_first_request`)
- 异常的 JSON 数据现在会出发一个坏的请求 HTTP 例外来代替 500 内部服务器错误值。这
  不会是一个向后兼容的变更。
- 许多应用程序现在不仅有一个资源与模块所在位置的根路径，也有一个实例路径。实例路径所
  设计的位置是用来丢掉那些在运行时修改的文件 (包括上传文件，等)。这是一个概念上只针对
  实例依赖和外部版本控制，所以这是一个完美的放置配置等文件的地方。对于更多信息请查看
  :ref:`instance-folders` 实例文件夹。
- 已加入 ``APPLICATION_ROOT`` 配置变量。
- 已部署 :meth:`~flask.testing.TestClient.session_transaction` 方法容易修改
  测试环境中的会话。
- 重构内部测试客户端。``APPLICATION_ROOT`` 配置变量与 ``SERVER_NAME`` 变量现在
  都正确的被测试客户端作为默认使用。
- 已加入 :attr:`flask.views.View.decorators` 属性来支持更简单的可插拔 (基于类的)
  试图函数的装饰器。
- 已修复一个测试客户端问题，如果使用了 ``with`` 语句不能触发 teardown 处理器的执行。
- 已加入对会话 cookie 参数的更好控制。
- 如果没有部署一个处理器的话，现在 HEAD 请求一个方法视图自动调度到 `get` 方法。
- 已部署虚拟模块 :mod:`flask.ext` 包来导入扩展包。
- 在例外上的语境保护现在是 Flask 自身的一个内部组件，并且不再属于测试客户端。这样做
  可以让内部逻辑变得整洁，以及减少单元测试中运行请求语境的可能性。

版本 0.7.3
-------------

Bug 修复，发布时间需要确定

- 修复 当引入蓝图或模块时，Jinja2 环境的 ``list_templates`` 方法
  无法返回正确名字的问题。

版本 0.7.2
-------------

Bug 修复，发布于 on July 6th 2011

- 修复一个 URL 处理器不能正确工作在蓝图上的问题。

版本 0.7.1
-------------

Bug修复，发布于 June 29th 2011

- 已加入缺少的特性，兼容 2.5 中 import 不会导致断裂。
- 修复一个蓝图技术无限重定向问题。

版本 0.7
-----------

发布于 June 28th 2011，代号 Grappa 白兰地

- 已加入 :meth:`~flask.Flask.make_default_options_response` 方法，
  该方法可以用于子类来警告 ``OPTIONS`` 响应的默认行为。
- 解绑本地现在会产生一个正确的 :exc:`RuntimeError` 运行错误来代替一个
  :exc:`AttributeError` 属性错误。
- 对于 :func:`flask.send_file` 函数淘汰了媒体类型的猜测和电子标签支持，
  因为猜猜是不可靠的。代入文件名或写你自己的电子标签后通过手动提供一个正确
  的媒体类型。
- 对于模块来说静态文件处理现在需要提供明确的静态文件夹名。以前自动检测是
  不可靠的，并且在 Google 的应用引擎上会产生问题。直到 1.0 老旧的表现
  依然会存在，但会有依赖警告。
- 修复一个运行在 jython 上的 Flask 问题。
- 已加入一个 ``PROPAGATE_EXCEPTIONS`` 配置变量，这个变量可以用来翻页
  例外传播设置，以前的例外传播设置只会连接到 ``DEBUG`` 上，而现在既可以
  连接到 ``DEBUG`` 模式上，也可以连接到 ``TESTING`` 测试模式上。
- Flask 不再内部依靠通过 `add_url_rule` 函数增加的规则，并且现在可以
  接受常规的 werkzeug 规则加入到 url 地图中。
- 已加入一个 `endpoint` 方法给 flask 应用对象，这样允许一个对象注册一个
  回调给任何一个带有一个装饰器的端点。
- 使用最后编辑日期给静态文件发送，这样代替了 0.6 中介绍的不正确发送日期。
- 已加入 `create_jinja_loader` 来覆写加载器建立的进程。
- 为 `config.from_pyfile` 部署一个沉默旗语。
- 已加入 `teardown_request` 装饰器，对那些应该运行在一个请求结束时考虑
  是否有一个例外发生。同样对于 `after_request` 的表现也有了变更。当一个
  例外产生时它现在不再执行了。查看 :ref:`upgrading-to-new-teardown-handling`
- 已部署 :func:`flask.has_request_context` 函数。
- 淘汰了 `init_jinja_globals` 方法。覆写 :meth:`~flask.Flask.create_jinja_environment` 
  方法来代替同样的功能。
- 已加入 :func:`flask.safe_join` 函数。
- 自动化 JSON 请求数据解压现在会查看媒体类型参数字符集。
- 如果在会话里没有消息的话，不会修改 :func:`flask.get_flashed_messages` 函数
  上的会话。
- `before_request` 处理器现在能够用错误来忽略请求。
- 不再支持定义用户例外处理器。在请求处理过程中你可以为某种可能发生的错误提供
  来自一个中心 hub 的自定义错误消息 (例如，对于数据库连接实例错误来说，远程
  资源超时错误，等等)。
- 蓝图技术可以提供蓝图具体的错误处理器。
- 已部署普通的 :ref:`views` 视图函数(基于类的视图函数)。

版本 0.6.1
-------------

Bug 修复，发布于 December 31st 2010

- 修复了一个默认 ``OPTIONS`` 响应没有曝露 ``Allow`` 头部中所有合法方法的 bug
- Jinja2 模版加载句法现在允许在一个模版加载路径里使用 "./" 写法。以前使用模块
  配置会有问题。
- 修复了一个为模块配置子域名会忽略静态文件夹的问题。
- 修复一个安全问题，问题是如果主机服务器是 Windows 操作系统的话客户端会下载任何文件，
  并且客户端使用反斜杠转义目录会导致文件暴露出来。

版本 0.6
-----------

发布于 July 27th 2010，代号 Whisky 威士忌

- 在请求函数之后就可以用逆序注册来调用这些请求函数。
- OPTIONS 现在是由 Flask 自动部署，除非应用明确增加 'OPTIONS'
  方法到 URL 规则中。在这种情况下 OPTIONS 处理不会自动介入。
- 对于模块来说如果没有静态文件夹的话，静态规则依然存在。这
  样做是为了 GAE，因为如果静态文件夹映射在 .yml 文件中的话，
  GAE会删除静态文件夹。
- :attr:`~flask.Flask.config` 属性现在可以用在模版中
  作为 `config` 内容。
- 语境处理器不再会覆写直接带入到翻译函数中的那些值了。
- 已加入限制入口请求数据含带新 ``MAX_CONTENT_LENGTH`` 
  配置值的能力。
- :meth:`flask.Module.add_url_rule` 方法的端点可选为
  与应用对象上同名函数保持一致了。
- 已加入一个 :func:`flask.make_response` 函数，它直接
  在视图函数中建立响应对象实例。
- 已加入基于信号灯的信号支持。这个特性当前是可选项，并且可
  能会由扩展与应用来使用。如果你想用这个特性的话，确保已经
  安装了 `blinker`_ 库。
- 重构了 URL 适配器建立的方法。这种重构处理现在完全可以用
  :meth:`~flask.Flask.create_url_adapter` 方法来自定
  义了。
- 模块现在可以注册一个子域名来代替一个 URL 前缀。这样做可以
  把一个完整的模块绑定到一个可配置的子域名上。

.. _blinker: https://pypi.org/project/blinker/

版本 0.5.2
-------------

Bug 修复，发布于 July 15th 2010

- 修复另一个从目录加载模版的问题，从而解决了什么时候模块用在哪里。
  modules were used.

版本 0.5.1
-------------

Bug 修复，发布于 July 6th 2010

- 修复一个模版加载目录的问题，从而解决了什么时候模块用在哪里。

版本 0.5
-----------

发布于 July 6th 2010，代号 Calvados 烈酒

- 修复了一个 bug 该 bug 是不能访问具体服务器名的子域名。服务器名现在可以
  用 ``SERVER_NAME`` 配置键来设置了。这个键名现在也用来设置会话 cookie
  跨子域名功能。
- 自动转义不再为所有模版处于激活状态。相反自动转义只为 ``.html``、 ``.htm``、
  ``.xml`` 和 ``.xhtml`` 而激活。在这些模版中自动转义的行为可以用
  ``autoescape`` 模版语言标签来改变。
- 内部重构完 Flask 代码。现在是由多个文件组成的了。
- :func:`flask.send_file` 函数此时发出许多电子标签后具备了内在的条件反射能力。
- (临时地) 删除了压缩应用程序的支持。这是一个几乎用不到的特性，并且产生一些
  令人困惑的表现。
- 已加入支持每个包模版和静态文件目录。
- 删除 `create_jinja_loader` 的支持，因为在 0.5 中不再使用是为了提升模块支持。
- 已加入一个助手函数来曝露任何一个目录中的文件。

版本 0.4
-----------

发布于 June 18th 2010，代号 Rakia 果酒

- 已加入一项能力，从模块注册应用范围错误处理器。
- :meth:`~flask.Flask.after_request` 方法处理器现在也都开始介入，
  如果请求因为一个列外而终止，然后一个错误处理页面就会出现。
- 测试客户端具有了保留一小段时间的请求语境能力。这项能力也可以用来触发
  为测试而无法删除请求堆栈的自定义请求。
- 由于 Python 标准库缓存日志，日志名现在可以配置成更好地支持单元测试。
- 已加入 ``TESTING`` 开关，它可以激活单元测试助手。
- 如果调试模式开启的话，日志现在可以切换到 ``DEBUG`` 调试模式。

版本 0.3.1
-------------

Bug 修复，发布于 May 28th 2010

- 修复了一个使用 :meth:`flask.Config.from_envvar` 方法报告时产生的一个错误。
- 删除了一些 flask 中未使用的代码。
- 本版本中不再含有开发残留文件 ( 对于主题来说的 .git 文件夹，建立文档时产生的 zip
  和 pdf 文件，以及一些 .pyc 文件)

版本 0.3
-----------

发布于 May 28th 2010，代号 Schnaps 白酒

- 已加入对闪存消息分类的支持。
- 现在应用程序配置了一个 :class:`logging.Handler` 类并且在没有开启
  调试模式时把那些请求处理例外错误记录在日志中。例如，这样可能实现接收
  到服务器错误方面的电子邮件通知。
- 已加入支持语境绑定，语境绑定不需要在终端里使用 ``with`` 语句。
- 现在请求语境可以用在 ``with`` 语句里了，这样做可以实现稍后推送请求语境，
  或者删除请求语境。
- 已加入支持许多配置。

版本 0.2
-----------

发布于 May 12th 2010，代号 Jägermeister 开胃酒

- 各种 bug 修复
- 集成了 JSON 支持
- 已加入 :func:`~flask.get_template_attribute` 助手函数。
- :meth:`~flask.Flask.add_url_rule` 该方法现在也可以注册
  一个视图函数了。
- 重构内部请求调度。
- 修复了使用 chrome 浏览器默认访问在 127.0.0.1 上的服务器问题。
- 已加入支持外部 URL 功能。
- 已加入 :func:`~flask.send_file` 函数的支持。
- 模块支持与内部请求处理重构成更好地支援可插拔应用程序。
- 在每个会话基础上现在可以把会话设置成永久的了。
- 在缺少密钥情况下有更好的错误报告内容。
- 已加入支持 Google Appengine 应用引擎。

版本 0.1
-----------

第一次公开预览发布。
