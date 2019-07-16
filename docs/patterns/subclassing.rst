Flask 子类
=================

对于 :class:`~flask.Flask` 类来说是为子类而设计的。

例如，你也许想要覆写请求参数都是如何处理的，以此来保护参数的顺序::

    from flask import Flask, Request
    from werkzeug.datastructures import ImmutableOrderedMultiDict
    class MyRequest(Request):
        """Request subclass to override request parameter storage"""
        parameter_storage_class = ImmutableOrderedMultiDict
    class MyFlask(Flask):
        """Flask subclass using the custom request class"""
        request_class = MyRequest

对于覆写或参数化 Flask 内部功能来说，这里的示例是推荐的实现方法。
