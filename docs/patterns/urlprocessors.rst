使用 URL 处理器
====================

.. versionadded:: 0.7

Flask 0.7 版本介绍了 URL 处理器概念。
思路是你想在 URL 中拥有共同部分的资源分支，
但你不一直明确地想要提供。这种情况下，
你也许要有另一个语种的 URLs 分支，
但你不想在每个单独函数中都自己处理它。

当与蓝图组合时，URL 处理器都是特别有用的。
我们既可以处理网络应用描述的 URL 处理器，
也可以处理蓝图描述的 URL 处理器。

国际化网络应用 URLs 地址
----------------------------------

思考如下这样的一个网络应用::

    from flask import Flask, g

    app = Flask(__name__)

    @app.route('/<lang_code>/')
    def index(lang_code):
        g.lang_code = lang_code
        ...

    @app.route('/<lang_code>/about')
    def about(lang_code):
        g.lang_code = lang_code
        ...

这种含有大量重复代码的行为是一种败坏情形，因为在每个单独函数中
你被迫自己处理设置在 :data:`~flask.g` 代理对象上的语种代号。
当然，一个装饰器可以用来简化这种情况，但如果你想要一个函数接着
另一个函数生成许多 URLs 地址的话，你仍然被迫明确地提供语种代号，
这是多么令人厌烦的一件工作。

对于简化情况来说，使用的就是 :func:`~flask.Flask.url_defaults` 函数。
它们可以自动地为 :func:`~flask.url_for` 函数自动把值注射到一次调用中。
如下的代码检查了语种代号也不在 URL 值中，
并且端点还想要一个名叫 ``'lang_code'`` 的值::

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

URL 映射方法 :meth:`~werkzeug.routing.Map.is_endpoint_expecting` 可以
用来弄清楚这件事，如果它清楚提供一个语种代号给已知端点，那就有意义了。

该函数的反向查询都是
:meth:`~flask.Flask.url_value_preprocessor` 方法。
在请求匹配之后它们正好被执行，并且它们可以根据 URL 值来执行。
思路就是它们把值字典中的信息拉取过来后再放到其它地方::

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

这样的方式你就不用在每个函数中被迫把 `lang_code` 分配给
:data:`~flask.g` 代理对象了。你可以进一步改善这种方法，
通过写一个自己的装饰器，用语种代号作为 URLs 的前缀，但更
漂亮的解决方案就是使用一个蓝图技术。
一旦从值字典中删除 ``'lang_code'`` 后，
就不用直接提供给视图函数减少代码了::

    from flask import Flask, g

    app = Flask(__name__)

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

    @app.route('/<lang_code>/')
    def index():
        ...

    @app.route('/<lang_code>/about')
    def about():
        ...

国际化的蓝图 URLs 地址
--------------------------------

由于蓝图技术可以用一个共同的字符串自动给所有 URLs 地址增加前缀，
为每个函数自动化实现这种操作就是容易的事情了。
更进一步来说，蓝图技术可以有每个蓝图 URL 处理器，
这些蓝图地址处理器从 :meth:`~flask.Flask.url_defaults` 方法
中删除了整个大量逻辑，因为不再被迫用一个 ``'lang_code'`` 参数来
检查真正感兴趣的 URL 地址了::

    from flask import Blueprint, g

    bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

    @bp.url_defaults
    def add_language_code(endpoint, values):
        values.setdefault('lang_code', g.lang_code)

    @bp.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code')

    @bp.route('/')
    def index():
        ...

    @bp.route('/about')
    def about():
        ...
