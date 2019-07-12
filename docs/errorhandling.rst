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

When an exception is caught by Flask while handling a request, it is first
looked up by code. If no handler is registered for the code, it is looked up
by its class hierarchy; the most specific handler is chosen. If no handler is
registered, :class:`~werkzeug.exceptions.HTTPException` subclasses show a
generic message about their code, while other exceptions are converted to a
generic 500 Internal Server Error.

For example, if an instance of :exc:`ConnectionRefusedError` is raised, and a handler
is registered for :exc:`ConnectionError` and :exc:`ConnectionRefusedError`,
the more specific :exc:`ConnectionRefusedError` handler is called with the
exception instance to generate the response.

Handlers registered on the blueprint take precedence over those registered
globally on the application, assuming a blueprint is handling the request that
raises the exception. However, the blueprint cannot handle 404 routing errors
because the 404 occurs at the routing level before the blueprint can be
determined.

.. versionchanged:: 0.11

   Handlers are prioritized by specificity of the exception classes they are
   registered for instead of the order they are registered in.

Logging
-------

See :ref:`logging` for information on how to log exceptions, such as by
emailing them to admins.


Debugging Application Errors
============================

For production applications, configure your application with logging and
notifications as described in :ref:`application-errors`.  This section provides
pointers when debugging deployment configuration and digging deeper with a
full-featured Python debugger.


When in Doubt, Run Manually
---------------------------

Having problems getting your application configured for production?  If you
have shell access to your host, verify that you can run your application
manually from the shell in the deployment environment.  Be sure to run under
the same user account as the configured deployment to troubleshoot permission
issues.  You can use Flask's builtin development server with `debug=True` on
your production host, which is helpful in catching configuration issues, but
**be sure to do this temporarily in a controlled environment.** Do not run in
production with `debug=True`.


.. _working-with-debuggers:

Working with Debuggers
----------------------

To dig deeper, possibly to trace code execution, Flask provides a debugger out
of the box (see :ref:`debug-mode`).  If you would like to use another Python
debugger, note that debuggers interfere with each other.  You have to set some
options in order to use your favorite debugger:

* ``debug``        - whether to enable debug mode and catch exceptions
* ``use_debugger`` - whether to use the internal Flask debugger
* ``use_reloader`` - whether to reload and fork the process if modules were changed

``debug`` must be True (i.e., exceptions must be caught) in order for the other
two options to have any value.

If you're using Aptana/Eclipse for debugging you'll need to set both
``use_debugger`` and ``use_reloader`` to False.

A possible useful pattern for configuration is to set the following in your
config.yaml (change the block as appropriate for your application, of course)::

   FLASK:
       DEBUG: True
       DEBUG_WITH_APTANA: True

Then in your application's entry-point (main.py), you could have something like::

   if __name__ == "__main__":
       # To allow aptana to receive errors, set use_debugger=False
       app = create_app(config="config.yaml")

       use_debugger = app.debug and not(app.config.get('DEBUG_WITH_APTANA'))
       app.run(use_debugger=use_debugger, debug=app.debug,
               use_reloader=use_debugger, host='0.0.0.0')
