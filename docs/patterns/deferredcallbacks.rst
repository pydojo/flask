.. _deferred-callbacks:

延迟请求回调
==========================

Flask 设计原则之一就是响应对象都要被建立后，响应对象被代入到潜在的一条回调链中，
该条回调链可以修改响应对象或者替换响应对象。当一个请求处理开始时，还没有响应对象产生。
这个响应对象的建立既可以通过一个视图函数需求来决定，也可以通过系统中的某个组件来决定。

如果你想要在还没有响应对象时修改一个响应对象，那么会发生什么？
一个共性的示例就是使用一个 :meth:`~flask.Flask.before_request` 回调方法，
它想要在响应对象上设置一个 cookie 。

避免这种情况的一个方法，常常是可以做到的。此种情况你可以尝试把逻辑移到一个
 :meth:`~flask.Flask.after_request` 回调方法中取代提前设置 cookie 的动作。
不管如何做到的，有时候这种逻辑代码的移动会非常复杂，或者难于弄明白原因所在。

作为另一种解决方案，你可以使用 :func:`~flask.after_this_request` 函数来注册回调，
被注册的回调只会在当前请求之后进行执行。这种方法就是你延迟代码执行的用法，
可以用在网络应用中的任何地方，依据的就是当前请求。

在一个请求过程中的任何时间点上，我们可以注册一个函数在请求结束时进行调用。
例如你可以把用户的当前语言记在一个 cookie 里，
使用的就是一个 :meth:`~flask.Flask.before_request` 方法回调::

    from flask import request, after_this_request

    @app.before_request
    def detect_user_language():
        language = request.cookies.get('user_lang')

        if language is None:
            language = guess_language_from_request()

            # when the response exists, set a cookie with the language
            @after_this_request
            def remember_language(response):
                response.set_cookie('user_lang', language)
                return response

        g.language = language
