.. currentmodule:: flask

.. _app-context:

网络应用语境
=======================

网络应用语境保存了一个请求期间、命令行、或其它活动过程中的应用层数据追踪信息。
这要比把网络应用代入到每个函数里要良好许多， :data:`current_app` 数据和
:data:`g` 数据代理都能代替访问到网络应用。

这类似于 :doc:`/reqcontext` 文档，该文档介绍了一个请求期间
保存请求层数据的追踪信息。当一个请求语境推送完时，一个相关的
网络应用语境也推送完成。

使用语境的目的
----------------------

对 :class:`Flask` 类建立的网络应用实例来说有许多属性，例如
:attr:`~Flask.config` 属性，这些属性都是访问视图函数内部时有用的，
并且访问命令行 :doc:`CLI commands </cli>` 文档内容也是有用的。
不管如何做到的，在你的项目中，在模块里导入 ``app`` 实例都会产生回路问题。
当使用 :doc:`app factory pattern </patterns/appfactories>` 文档介绍的技术，
或者使用 :doc:`blueprints </blueprints>` 文档介绍的复用技术写代码，
又或者使用 :doc:`extensions </extensions>` 文档介绍开发扩展件时，
根本都不会有一个 ``app`` 实例要导入。

Flask 解决这类问题使用了 *网络应用语境* 技术。这要比直接指向一个
 ``app`` 实例要良好，你使用 :data:`current_app` 数据代理，
就指向了网络应用处理的当前活动。

当处理一个请求时，Flask 自动化 *推送* 一个网络应用语境。
视图函数、错误处理器、和其它运行的函数，在一个请求期间会有
访问 :data:`current_app` 数据的权限。

用 :attr:`Flask.cli` 属性用做 ``@app.cli.command()`` 装饰器时，
当运行注册的命令行命令时，Flask 也会自动化推送一个 ``app`` 实例语境。


语境的生命周期
-----------------------

网络应用语境建立后根据需要来进行销毁。
当一个 Flask 网络应用开始处理一个请求时，
它推送了一个网络应用语境和一个 :doc:`request context </reqcontext>` 文档内容。
当请求结束时，先删除请求环境，再删除网络应用语境。
典型来说，一个网络应用语境会与一个请求有一样的生命周期。

查看 :doc:`/reqcontext` 文档来了解更多关于语境是如何工作的信息，
以及一个请求的完整生命周期细节。


手动推送一个语境
-----------------------

如果你尝试访问 :data:`current_app` 数据的话，或者访问任何使用数据代理的内容，
在一个网络应用语境之外访问你会得到这样的错误消息：

.. code-block:: pytb

    RuntimeError: Working outside of application context.

    这典型是指你想要使用能够与当前网络应用对象互动的功能。
    要解决这个运行时的错误问题，使用 app.app_context()
    配置一个网络应用语境即可。

如果你看到错误的同时配置了你的网络应用的话，
例如当初始化一个扩展件时，你可以手动推送一个语境，
因此你才有了直接访问 ``app`` 的权限。
使用 :meth:`~Flask.app_context` 方法要与
一个 ``with`` 语句组合使用，并且只有在块中运行
的代码才有权限访问 :data:`current_app` 数据代理。 ::

    def create_app():
        app = Flask(__name__)

        with app.app_context():
            init_db()

        return app

如果你代码中看到没有关联到配置网络应用的错误，
那最可能就是指你应该把代码移到一个视图函数里去，
或者移到一个命令行注册函数中去。


存储数据
------------

网络应用语境是在请求或命令行期间存储共同数据的良好位置。
Flask 提供了 :data:`g object <g>` 数据代理对象来解决
这种目的。它就是一个命名空间对象，
与一个网络应用语境的生命周期是一样的。

.. 注意::
    这个 ``g`` 名字代表了 "global" 全局的意思，但它也正指向了*一个语境中*
    的全局范围中的数据。在 ``g`` 对象上的数据在语境结束后就会消失，
    并且它不适合用来存储请求之间的数据。所以使用 :data:`session` 数据代理
    或者一个数据库来存储请求之间的数据。

对于 :data:`g` 数据代理的共同用法是管理一个请求之间的资源。

1.  ``get_X()`` 是建立一个不存在的资源 ``X`` ，把这个资源缓存成 ``g.X`` 对象。
2.  ``teardown_X()`` 关闭资源或释放掉已有的内存资源。它要注册成一个
     :meth:`~Flask.teardown_appcontext` 方法处理器。

例如，你可以使用如下模式来管理一个数据库连接::

    from flask import g

    def get_db():
        if 'db' not in g:
            g.db = connect_to_database()

        return g.db

    @app.teardown_appcontext
    def teardown_db():
        db = g.pop('db', None)

        if db is not None:
            db.close()

在一个请求期间，每次调用 ``get_db()`` 函数会返回相同的数据库连接，
然后它会在请求结束时自动关闭。

你可以使用 :class:`~werkzeug.local.LocalProxy` 类从
 ``get_db()`` 来建立一个新的本地语境::

    from werkzeug.local import LocalProxy
    db = LocalProxy(get_db)

访问 ``db`` 本地语境会内部地调用 ``get_db`` 函数，同样的方法用在
:data:`current_app` 数据代理上也是有效的。

扩展件数据代理
---------------

如果你正在写一个扩展件的话， :data:`g` 数据代理应该存储用户代码。
你也许要把内部数据存储在语境本身上，但要确保使用一个足够独到的名字。
当前语境要使用 :data:`_app_ctx_stack.top <_app_ctx_stack>` 
数据代理来访问。对于更多信息查看 :doc:`extensiondev` 文档内容。


事件与信号
------------------

在网络应用语境被删除时，网络应用会调用许多用
:meth:`~Flask.teardown_appcontext` 方法注册的函数。

如果 :data:`~signals.signals_available` 数据设置成 ``True`` 的话，
下面的信号都会被发送出去：
:data:`appcontext_pushed` 数据信号，
:data:`appcontext_tearing_down` 数据信号，和
:data:`appcontext_popped` 数据信号。
