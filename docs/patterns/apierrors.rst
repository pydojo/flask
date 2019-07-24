部署 API 例外
===========================

在 Flask 顶层部署 RESTful APIs 是非常共同的做法。开发者们首要做的事情之一就是
实现那些内置例外，对于 APIs 来说例外都是表达不足的，并且 :mimetype:`text/html`
的内容类型对于 API 用户们来说，发出的信息不是非常有用。

比使用 ``abort`` 给非法 API 用法发出信号错误更好的解决方案就是部署你自己的例外类型，
然后为自定义例外类型安装一个错误处理器，生成用户期望的错误信息格式。

简单的例外类
----------------------

基本思路是介绍一个新的例外，获得一种让人能读懂的消息，
错误的状态代号和一些可选的装载信息，提供更适合理解错误的语境。

如下是一个简单的示例::

    from flask import jsonify

    class InvalidUsage(Exception):
        status_code = 400

        def __init__(self, message, status_code=None, payload=None):
            Exception.__init__(self)
            self.message = message
            if status_code is not None:
                self.status_code = status_code
            self.payload = payload

        def to_dict(self):
            rv = dict(self.payload or ())
            rv['message'] = self.message
            return rv

一个视图现在可以抛出含有一个错误消息的例外。另外，一些额外
装载信息可以通过 `payload` 参数提供成一个字典数据类型。

注册一个错误处理器
----------------------------

现在视图可以抛出错误，但会立即造成一个内部服务器错误。
原因就是此时还没有为这个视图错误类注册处理器。
不管如何做到的，增加处理器是容易的事情::

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

视图用法
--------------

下面就是如何使用一个视图错误类功能::

    @app.route('/foo')
    def get_foo():
        raise InvalidUsage('This view is gone', status_code=410)
