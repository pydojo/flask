.. _application-errors:

网络应用错误
==================

.. versionadded:: 0.3

网络应用失败，服务器失败。在生产中立即或稍后你都会看到一个例外出现。
即使你的代码 100% 正确，你依然在任何时候都会看到各种例外现象。
为什么会这样？因为有任何其它情况会涉及失败。
这里有一些完美良好的代码所导致的服务器错误情形：

-   客户端提前终止了请求后网络应用依然读取进入的数据
-   数据库服务器超载后无法处理查询操作
-   一个文件系统空间占满了
-   一个硬盘坏了
-   一个后端服务器超载了
-   你使用了一个库中的编程错误
-   服务器网络连接到另一个系统失败了

并且这些都只是你可能面对的一小部分问题现象。那么我们如何处理这类问题呢？
如果你的网络应用运行在生产模式中，默认情况是 Flask 会显示一个非常简单的页面给你，
然后记录下例外提供给 :attr:`~flask.Flask.logger` 属性。

但你还有更多要做的，并且我们会介绍一些更好的配置来处理这些错误。

错误日志工具
-------------------

发送错误信息邮件，即使只对严重的错误发送邮件的话，
如果足够的用户都造成了错误邮件也会吞没你的视野，
并且通常都不会去查看日志文件。
这就是为什么我们要推荐使用 `Sentry <https://sentry.io/>`_ 
 来处理网络应用错误。它是一个可用的开源项目，位于
  `on GitHub <https://github.com/getsentry/sentry>`_ 可以找到。
并且也可以作为一个 `hosted version <https://sentry.io/signup/>`_ 来使用，
你可以免费尝试一下。 Sentry 为调试累计了重复的错误，捕获完整的堆栈追踪和本地变量，
并且根据新错误或频率阀值来给你发送邮件。

要使用 Sentry 你需要安装 `sentry-sdk` 客户端，使用 `flask` 外部依赖命令安装::

    $ pip install sentry-sdk[flask]

然后把它的代码增加到你的 Flask 网络应用中::

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    
    sentry_sdk.init('YOUR_DSN_HERE',integrations=[FlaskIntegration()])

其中 `YOUR_DSN_HERE` 这个值是要用你安装 Sentry 获得的 DSN 值来替换。

安装之后，导致内部服务器的错误都会自动地报告给 Sentry 后你可以接收到错误提醒。

继续阅读如下文档：

* Sentry 也支持捕获来自你的工作器列队（RQ，Celery）产生的错误，使用的是类似模式。
  查看 `Python SDK docs <https://docs.sentry.io/platforms/python/>`_ 文档
  了解更多信息。
* `Getting started with Sentry <https://docs.sentry.io/quickstart/?platform=python>`_
* `Flask-specific documentation <https://docs.sentry.io/platforms/python/flask/>`_.

.. _error-handlers:

错误处理器
--------------

当一个错误发生时，你也许想要显示自定义错误页面给用户。
通过注册错误处理器就可以实现。

一个错误处理器是一种正常的视图函数，它返回一个响应，而代替注册一个路由，
注册一个错误处理器是针对一个例外或一个 HTTP 状态代号，
它在尝试处理一个请求时会抛出这个 HTTP 状态代号。

注册
```````````

注册处理器通过装饰器句法使用 :meth:`~flask.Flask.errorhandler` 方法注册一个函数来实现。
或者无装饰器句法使用 :meth:`~flask.Flask.register_error_handler` 方法来稍后注册函数。
记住当返回响应时要设置 HTTP 错误代号。 ::

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    # or, without the decorator
    app.register_error_handler(400, handle_bad_request)

当注册处理器时，
:exc:`werkzeug.exceptions.HTTPException` 例外子类像
:exc:`~werkzeug.exceptions.BadRequest` 例外和其 HTTP 代号一样都是可互换的。
 (``BadRequest.code == 400``)

非标准 HTTP 代号不能通过代号来注册，因为 Werkzeug 不认识它们。
相反，定义一个 :class:`~werkzeug.exceptions.HTTPException` 的子类
包含合适的代号和注册器，以及抛出那个例外子类来实现。 ::

    class InsufficientStorage(werkzeug.exceptions.HTTPException):
        code = 507
        description = 'Not enough storage space.'

    app.register_error_handler(InsufficientStorage, handle_507)

    raise InsufficientStorage()

处理器可以为任何一种例外类别进行注册，不只是
 :exc:`~werkzeug.exceptions.HTTPException` 例外子类或 HTTP 状态代号。
处理器可以针对一个具体的类来进行注册，或者对一个父类的所有子类进行注册。

处理
````````

当 Flask 处理一个请求时，一个例外被其捕获的时候，Flask 会先查看代码。
如果代码中没有注册一个处理器的话， 通过例外的类垂直关系来查看例外；
会选择最具体的一个处理器。如果没有注册处理器的话，
 :class:`~werkzeug.exceptions.HTTPException` 例外子类显示关于代码
的一个普通消息，同时其它的例外都转换到一个普通的 500 内部服务器错误。

例如，如果抛出一个 :exc:`ConnectionRefusedError` 例外实例的话，
并且有一个处理器注册 :exc:`ConnectionError` 例外和
 :exc:`ConnectionRefusedError` 例外，
更具体的 :exc:`ConnectionRefusedError` 例外处理器
会带着例外实例被调用来生成其响应。

注册在蓝图上的处理器获得优先权，要比那些注册在全局范围上的网络应用先获得处理，
假设一个蓝图正在处理请求时，会先抛出例外。
不管如何做到的，蓝图不能处理 404 路由错误，因为在蓝图确定之前 404 发生在路由层。

.. versionchanged:: 0.11

   处理器优先权是通过例外类注册的具体顺序来计算，而不是根据处理器注册的顺序。

日志
-------

查看 :ref:`logging` 参考内容了解如何记录例外的，
例如天通过邮件发送给管理员。


调试网络应用错误
============================

对于生产中的网络应用来说，配置含有日志和提醒的网络应用，
描述在 :ref:`application-errors` 参考内容中。
本部分提供许多指导，作为调试开发配置和更深入了解完整特性的 Python 调试器。


不清楚的时候手动运行
---------------------------

对于生产环境你的网络应用是不是有许多问题？
如果你用终端访问你的主机的话，验证一下你
可以在部署环境中手动运行你的网络应用。
确保使用一样的部署配置和相同的用户权限来运行，这样可以解决权限许可问题。
你可以在生产主机上使用 Flask 的内置开发服务器包含 `debug=True` 配置，
这样在捕获配置问题中是有帮助的，
但 **一定要确保在一个控制的环境中临时性这样做。** 
不要在生产中带着 `debug=True` 运行网络应用。


.. _working-with-debuggers:

与调试器一起工作
----------------------

要更深入了解情况，可能要追踪代码的执行， Flask 提供了一种盒外调试器
（查看 :ref:`debug-mode` 参考内容）。如果你喜欢使用另一个 Python 调试器的话，
注意彼此之间的调试器接口。你需要设置一些选项才可以使用你喜欢的调试器：

* ``debug``        - 是否要开启调试模式并且捕获例外
* ``use_debugger`` - 是否要使用内部 Flask 调试器
* ``use_reloader`` - 如果模块保存了变更的话，是否要重载和叉起进程

``debug`` 必须设置成 True （例如，例外必须要被捕获）这样对于其它两个选项才会有任何一种值设置。

如果你正在使用 Aptana/Eclipse 文本编辑器做调试的话，你会需要把
 ``use_debugger`` 和 ``use_reloader`` 都设置成 False 值才可以。

对于配置来说一种可能有用的模式是在你的 `config.yaml` 文件中设置
（当然为你的网络应用更新合适的配置块内容）::

   FLASK:
       DEBUG: True
       DEBUG_WITH_APTANA: True

然后在你的网络应用的入口点（main.py），你可以增加如下这些内容::

   if __name__ == "__main__":
       # To allow aptana to receive errors, set use_debugger=False
       app = create_app(config="config.yaml")

       use_debugger = app.debug and not(app.config.get('DEBUG_WITH_APTANA'))
       app.run(use_debugger=use_debugger, debug=app.debug,
               use_reloader=use_debugger, host='0.0.0.0')
