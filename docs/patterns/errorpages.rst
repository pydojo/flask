.. _errorpages:

自定义错误页面
==================

Flask 伴随着一个好用的 :func:`~flask.abort` 函数，它提前终止一个含有一个 HTTP 错误
代号的请求。它也会提供提供一个纯黑白错误页面给你，含带着一种基础描述，但外观一般。

依据错误代号，或多或少为用户提供实际所看到的一项错误。

共性的错误代号
------------------

下面这些错误代号都是常常显示给用户的，即使网络应用作出了正确的表现：

*404 Not Found*
    良好的老旧消息，意思是“小伙子，你输入的 URL 网址打错了。”
    所以对于访问互联网的新手来说这是一项共同犯的错，404 的意思就是：
    “该死，我在找的东西不在这里。”
    那么确保在一个 404 页面上给出点实际意思是非常良好的想法，
    至少要给一个返回主页的链接。

*403 Forbidden*
    如果你在你的网站上有一些访问控制的话，你要发送一个 403 代号给无权访问资源这种情况。
    所以确保用户不会糊涂，在他们尝试访问一个禁止访问的资源时给出实际的反馈表达。

*410 Gone*
    你知道 "404 Not Found" 还有一个兄弟，名叫 "410 Gone" 吗？
    很少有人去部署这项错误代号，意思是以前资源存在，但资源被删除了。
    所以要用 410 来代替 404 给出明确的反馈。
    如果你们没有从数据库中永久删除一些文档资源的话，只是给做了已删除的标记，
    那么就帮用户一把，要使用 410 代号来显示一个反馈消息，
    消息要表明用户们正在寻找的资源全部永久删除了。

*500 Internal Server Error*
    常常发生在编程中导致的错误，或者如果服务器超载了的话也会出现这个错误代号。
    有一个漂亮的页面提供出来是非常非常良好的思想，因为你的网络应用 *将要*
    产生失败，或者稍后会失败。（也要查看： :ref:`application-errors` 参考文档）。


错误处理器
--------------

一个错误处理器就是一个函数，该函数在一个错误类型被抛出的时候返回一个响应，
类似一个视图函数在一个请求 URL 匹配时返回一个响应一样。
它需要接受一个正在处理的错误实例，该实例最可能就是一个
:exc:`~werkzeug.exceptions.HTTPException` 例外实例。
一个错误处理器对于 "500 Internal Server Error" 错误情况会忽略不去捕获，
除非明确地指明 500 错误代号。

一个错误处理器是使用 :meth:`~flask.Flask.errorhandler` 方法装饰器来进行注册，
或者用 :meth:`~flask.Flask.register_error_handler` 方法进行注册。
一个处理器可以注册一个状态代号，像 404，或者为一个例外类来进行注册。

响应的状态代号不会被设置成处理器的代号。确保从一个处理器返回一个响应时，
提供合适的 HTTP 状态代号。

对于 "500 Internal Server Error" 来说，在运行调试模式时，
不会使用一个 500 处理器。相反，交互式调试器会使用并显示处理结果。

对于一个 "404 Page Not Found" 例外来说，如下是一个部署示例::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('404.html'), 404

当使用 :ref:`application factory pattern <app-factories>`
网络应用工厂模式时会部署成如下形式::

    from flask import Flask, render_template

    def page_not_found(e):
      return render_template('404.html'), 404

    def create_app(config_filename):
        app = Flask(__name__)
        app.register_error_handler(404, page_not_found)
        return app

在模版中部署的一个示例可能如下这样:

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Page Not Found{% endblock %}
    {% block body %}
      <h1>Page Not Found</h1>
      <p>What you were looking for is just not there.
      <p><a href="{{ url_for('index') }}">go somewhere nice</a>
    {% endblock %}
