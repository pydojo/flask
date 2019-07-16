.. currentmodule:: flask

.. _request-context:

请求语境
===================

请求语境是在一个请求期间存储请求层数据追踪信息。这要比在一个请求期间把请求对象
代入到每个运行的函数中要好， :data:`request` 数据代理和 :data:`session` 
数据代理都可以用来代替访问请求数据。

这类似于 :doc:`/appcontext` 文档，该文档是保存每个请求中应用层数据追踪信息。
当一个请求语境推送完时，一个相关当网络应用语境也推送结束。


语境的目的
----------------------

当 :class:`Flask` 类网络应用实例处理一个请求的时候，实例根据接受自 WSGI 服务器的环境
建立了一个 :class:`Request` 类实例对象。因为一个 *worker* （依据服务器上的
线程、进程、或协程）在一个时间点上只处理一个请求，在处理请求期间请求数据视为全局范围。
Flask 使用术语 *本地语境* 来表示这种情况。

当处理一个请求时，Flask 自动地 *推送* 一个请求语境。视图函数、错误处理器，和其它
运行的函数，在一个请求期间具有访问 :data:`request` 数据代理的权限，该数据代理
为当前的请求指向请求对象。


语境的生命周期
-----------------------

当一个 Flask 网络应用开始处理一个请求时，它推送一个请求语境，请求语境也推送一个
 :doc:`/appcontext` 网络应用语境。当请求结束时，它会删除请求语境后再删除
网络应用语境。

语境对于每一个线程（或其它工作器类型）都是唯一的。
:data:`request` 数据代理不能代入到其它线程中去，
其它线程会有一个不同的语境堆栈，并且不会知道父线程所指向的请求。

本地语境都是用 Werkzeug 来部署。查看 :doc:`werkzeug:local` 文档内容
了解更多内部是如何工作的信息。


手动推送一个语境
-----------------------

如果你尝试访问 :data:`request` 数据代理的话，或者任何使用这个数据代理的对象，
那么你在一个请求语境之外这样做，你会得到如下的错误消息：

.. code-block:: pytb

    RuntimeError: Working outside of request context.

    这典型的意思就是你要使用一个激活的 HTTP 请求功能。
    咨询测试方面的文档内容了解更多如何避免这类问题的信息。

这种问题典型只发生在测试代码期望一个激活的请求情况中。
一个选项是要使用
:meth:`test client <Flask.test_client>` 方法来模拟一个完整的请求。
或者你可以与 ``with`` 语句组合使用
:meth:`~Flask.test_request_context` 方法，然后在块代码中运行的代码
会有访问 :data:`request` 数据代理的权限，生成你的测试数据。 ::

    def generate_report(year):
        format = request.args.get('format')
        ...

    with app.test_request_context(
            '/make_report/2017', data={'format': 'short'}):
        generate_report()

如果在你的代码中看到没有关联到测试的错误，
那最可能就是指你应该把代码移到一个视图函数里去。

对于如何在交互式 REPL 中使用请求语境的信息，查看 :doc:`/shell` 文档内容。


语境是如何工作的
---------------------

在 :meth:`Flask.wsgi_app` 方法被调用来处理每个请求时，它管理着请求期间的语境。
内部来说，请求语境和网络应用语境都是堆栈的工作方式，即
:data:`_request_ctx_stack` 数据代理和 :data:`_app_ctx_stack` 数据代理。
当语境都推送到堆栈上，依据语境的数据代理都可以使用，并且指向来自堆栈顶部语境的信息。

当请求开始时，一个 :class:`~ctx.RequestContext` 类就建立完成了，然后推送出去，
如果网络应用的一个语境还不是顶层语境的话，
这个类首先建立并推送一个 :class:`~ctx.AppContext` 类。
同时这些语境也会被推送， :data:`current_app`、 :data:`g`、
:data:`request` 和 :data:`session` 数据代理对最初处理请求的线程来说是可用的。

由于语境都是堆栈形式，在一个请求期间其它的语境也许被推送来改变数据代理。
同时这不是一种共性模式，它会用在高级网络应用中，例如，实现内部重定向或
把不同的网络应用串联在一起。

在请求被调度完，并且一个请求生成与发送结束之后，请求语境就被删除了，
然后再删除网络应用语境。在它们都被立即删除之前，
 :meth:`~Flask.teardown_request` 方法和
and :meth:`~Flask.teardown_appcontext` 方法都会被执行。
即使在调度期间一个未处理例外发生，这些方法也会被执行。


.. _callbacks-and-errors:

回调和错误
--------------------

Flask 在多个位置调度一个请求，会影响请求、响应，和错误是如何处理的。
在所有这些位置上语境都是要激活的。

一个 :class:`Blueprint` 类可以为这些具体的事件增加处理器到蓝图里。
如果蓝图的路由与请求的路由相匹配的话，一个蓝图的处理器才会运行。

#.  每个请求之前， :meth:`~Flask.before_request` 方法都要被调用。
    如果其中一个方法返回一个值的话，其它方法都会跳过不执行。
    返回值作为响应来对待，并且视图函数不会被调用。

#.  如果 :meth:`~Flask.before_request` 方法没有返回一个响应的话，
    匹配路由的视图函数才被调用，并且返回一个响应。

#.  视图函数的返回值转换成一个实际的响应对象，然后代入到
     :meth:`~Flask.after_request` 方法中。
    每次函数返回一个修改过的，或者新的响应对象。

#.  响应对象返回之后，语境才被删除，其中调用
     :meth:`~Flask.teardown_request` 方法和
    :meth:`~Flask.teardown_appcontext` 方法。
    即使一个未处理的例外以上任何一种情况下被抛出来，这两个方法也会被调用。

如果在 teardonw 方法之前抛出一个例外的话， Flask 尝试用一个
 :meth:`~Flask.errorhandler` 方法来匹配例外，处理例外和返回一个响应。
如果没有错误处理器的话，或者错误处理器自身抛出一个例外的话，
Flask 返回一个普通的 ``500 Internal Server Error`` 响应。
那些 teardown 方法也依然会被调用，并且跳过例外对象。

如果调试模式开启的话，未处理的例外都不转换成一个 ``500`` 响应，并且都要
广播给 WSGI 服务器。这样就允许开发服务器呈现交互式调试器时含有回溯信息。


Teardown 回调
~~~~~~~~~~~~~~~~~~

对于 teardown 回调来说都是独立于请求调度的，并且都是在语境被删除时被调用。
即使在调度期间有一个未处理例外的话，这类方法也都会被调用，并且对于手动推送
语境来说也都要被调用。这就意味着无法保证请求调度的任何一个其它部分会先运行。
确保写这些方法时用不依赖其它回调的方法，那么就不会失败了。

在测试期间，在请求结束之后推迟删除语境就变得有用了，
所以在测试函数中它们的数据可以被访问。使用 :meth:`~Flask.test_client` 方法
要与一个 ``with`` 语句组合使用来保护语境，直到退出 ``with`` 语句块代码层。

.. code-block:: python

    from flask import Flask, request

    app = Flask(__name__)

    @app.route('/')
    def hello():
        print('during view')
        return 'Hello, World!'

    @app.teardown_request
    def show_teardown(exception):
        print('after with block')

    with app.test_request_context():
        print('during with block')

    # teardown functions are called after the context with block exits

    with app.test_client() as client:
        client.get('/')
        # the contexts are not popped even though the request ended
        print(request.path)

    # the contexts are popped and teardown functions are called after
    # the client with block exists

信号
~~~~~~~

如果 :data:`~signals.signals_available` 数据设置成 ``True`` 的话，
下面这些信号就会被发送：

#.  :data:`request_started` 信号数据是在
    :meth:`~Flask.before_request` 方法调用之前发送。

#.  :data:`request_finished` 信号数据是在
    :meth:`~Flask.after_request` 方法调用之后发送。

#.  :data:`got_request_exception` 信号数据是在一个例外开始处理时，
    但在一个 :meth:`~Flask.errorhandler` 方法被查询之前或者
    被调用之前发送。

#.  :data:`request_tearing_down` 信号数据是在
    :meth:`~Flask.teardown_request` 方法被调用之后发送。


在错误上的语境保护
-----------------------------

在一个请求结束时，请求语境被删除并且所有与其相关的数据都被销毁。
在开发期间如果一个错误发生了，为了调试的目的推迟摧毁数据是有用的。

当开发服务器运行在开发模式时
（ ``FLASK_ENV`` 环境变量设置成 ``'development'``)，
错误和数据会被保护起来，并且显示在交互式调试器中。

这种行为表现可以用
:data:`PRESERVE_CONTEXT_ON_EXCEPTION` 配置数据来控制。
如上面描述一样，在开发环境中配置数据默认值是 ``True`` 。

在生产中不要开启 :data:`PRESERVE_CONTEXT_ON_EXCEPTION` 配置数据。
因为它会导致你的网络应用把例外泄露在内存中。


.. _notes-on-proxies:

在代理数据上的注意事项
---------------------------

Flask 提供的有些对象都是其它对象的代理对象。对于每个 *worker* 线程
来说都是相同的方式来访问代理对象，但指向唯一绑定到每个 *worker* 的
代理对象背后的情况描述在本段落。

大多数时候你不用担心代理的事情，但也有一些例外情况需要考虑，
那就是要好好地知道一下这个对象实际上是一个代理对象：

-   代理对象不能把自身类型假冒成实际对象类型。
    如果你想执行实例检查的话，你要做的就是在
    被代理的对象上进行类型检查。
-   如果具体对象的指向对象被导入的话，
    例如，发送信号 :ref:`signals` 文档中所描述的，
    或者把数据代入到后端线程中。

如果你需要访问被代理的对象，使用
:meth:`~werkzeug.local.LocalProxy._get_current_object` 方法::

    app = current_app._get_current_object()
    my_signal.send(app)
