.. _signals:

信号
=======

.. versionadded:: 0.6

从 Flask 0.6 版本开始使用，在 Flask 中有了集成信号的支持。
这项支持是由出色的 `blinker`_ 库提供的，并且如果不可用的话
会提供恩典式回调。

什么是信号？信号帮助你解耦合网络应用，当在核心框架中或者在其它
 Flask 扩展件里有动作发生时通过发送提醒来实现解耦合。
简言之，信号允许发布者在订阅者做了什么事情的时候发送提醒消息。

Flask 含有一组信号，以及其它扩展件也许提供了更多的信号。
同样要记住信号都是为了提醒订阅者而存在的，并且应该不鼓励
订阅者去修改数据。你会注意到这里出现的信号所做的就像内置装饰器一样
（例如， :data:`~flask.request_started` 信号数据非常像
 :meth:`~flask.Flask.before_request` 方法）。
不管如何做到的，它们在如何工作上面还是有些不同的。
核心 :meth:`~flask.Flask.before_request` 方法处理器，例如，
它是在一个具体顺序中被执行的，并且它能够通过返回一个响应来
提前忽略请求。在所有信号处理器对比中，都是在未定义的顺序来执行，
并且不能修改任何数据。

信号超越处理器来说，最大的优势是你可以安全地按秒来订阅信号。
例如对单元测试来说临时订阅都是有帮助的事情。
就是说你想要知道哪些模版翻译成一个请求部分：
信号允许你完全能够实现这种想法。

订阅信号
----------------------

要订阅一个信号，你可以使用一个信号的
:meth:`~blinker.base.Signal.connect` 方法。
第一个参数是信号发出时应该被调用的函数，
可选的第二个参数用来描述一个发送器。
要从一个信号取消订阅，你可以使用信号的
 :meth:`~blinker.base.Signal.disconnect` 方法。

对于所有核心 Flask 信号来说，发送器是发布信号的一个应用。
当你订阅一个信号时，确保也要提供一个发送器，除非你想监听
所有网络应用的信号。如果你正在开发一个扩展件的话，
监听所有信号特别真实。

例如，这里有一个帮助语境管理器可以用在一个单元测试中，
用来确定哪些模版被翻译了，以及什么变量代入到模版中::

    from flask import template_rendered
    from contextlib import contextmanager

    @contextmanager
    def captured_templates(app):
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

下面这种此时可以容易地与一个测试客户端进行配对::

    with captured_templates(app) as templates:
        rv = app.test_client().get('/')
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'
        assert len(context['items']) == 10

确保订阅要含有一项 ``**extra`` 关键字参数，
如果 Flask 介绍了新参数给信号的话，这样你的调用就不会失败。

所有翻译到代码中的模版都是通过网络应用 `app` 来发布，
在 ``with`` 块主体中此时会被记录在 `templates` 变量里。
不管什么时候一个模版被翻译，模版对象和语境都会被追加到变量里。

另外这里有一个方便的帮助器方法
(:meth:`~blinker.base.Signal.connected_to`) 
它允许你临时把一个函数在自身上订阅到含有一个语境管理器的信号上。
因为语境管理器的返回值不能被描述成那种方式，
你要把列表作为一项参数代入其中::

    from flask import template_rendered

    def captured_templates(app, recorded, **extra):
        def record(sender, template, context):
            recorded.append((template, context))
        return template_rendered.connected_to(record, app)

上面的例子稍后用起来会像下面一样::

    templates = []
    with captured_templates(app, templates, **extra):
        ...
        template, context = templates[0]

.. admonition:: Blinker API 变更

   该 :meth:`~blinker.base.Signal.connected_to` 方法是
   在 Blinker 1.1 版本中出现的。

建立信号
----------------

如果你想要在自己的网络应用中使用信号的话，
你可以直接使用blinker 库。最共同的用法是
以一种自定义 :class:`~blinker.base.Namespace` 类的方式来
命名信号。大多数时候都是如下这种推荐用法::

    from blinker import Namespace
    my_signals = Namespace()

现在你可以建立像下面一样的一个新信号::

    model_saved = my_signals.signal('model-saved')

这里信号的名字要保持唯一性，并且也要让调试变得简单。
你可以使用 :attr:`~blinker.base.NamedSignal.name` 属性来
访问信号名。

.. admonition:: 对于扩展件开发者来说

   如果你正在写一个 Flask 扩展件的话，并且你想要为没有安装
   blinker 提供恩典式降级支持的话，
   你可以通过使用
   :class:`flask.signals.Namespace` 类来实现。

.. _signals-sending:

发送信号
---------------

如果你想要发出一个信号的话，你可以通过调用
:meth:`~blinker.base.Signal.send` 方法来实现。
该方法接受一个发送器作为第一个参数，并且可选的关键字参数
对于信号订阅者来说都是直接调用的方式::

    class Model(object):
        ...

        def save(self):
            model_saved.send(self)

总要尝试选择一个良好的发送器。如果你有一个类是用来发送一个信号的话，
把 ``self`` 作为发送器代入其中。
如果你要从一个随机函数中发送一个信号的话，
你可以把 ``current_app._get_current_object()`` 作为发送器代入其中。

.. admonition:: 把代理对象作为发送器代入其中

   永远不要把 :data:`~flask.current_app` 代理数据作为发送器代入到一个信号里。
   相反要使用 ``current_app._get_current_object()`` 作为发送器。
   这么做的原因是 :data:`~flask.current_app` 代理数据是一个代理对象，
   并且不是真正的网络应用对象。


信号与 Flask 的请求语境
-----------------------------------

信号完全支持 :ref:`request-context` 参考文档中所描述的当接受信号时的操作。
本地语境变量在 :data:`~flask.request_started` 和
 :data:`~flask.request_finished` 之间持续可用，所以你可以根据
 :class:`flask.g` 类和其它所需要来使用信号。
注意描述在 :ref:`signals-sending` 参考内容中的限制，
以及 :data:`~flask.request_tearing_down` 信号中的限制。


基于信号订阅的装饰器
------------------------------------

使用 Blinker 1.1 你也可以容易地订阅信号，通过使用新的
:meth:`~blinker.base.NamedSignal.connect_via` 方法装饰来实现::

    from flask import template_rendered

    @template_rendered.connect_via(app)
    def when_template_rendered(sender, template, context, **extra):
        print 'Template %s is rendered with %s' % (template.name, context)

核心信号
------------

查看一下 :ref:`core-signals-list` 参考文档了解内置的信号列表。


.. _blinker: https://pypi.org/project/blinker/
