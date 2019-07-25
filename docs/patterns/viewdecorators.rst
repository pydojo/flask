视图装饰器
===============

Python 有一个真正有趣的特性，名叫函数装饰器。
对于网络应用来说这就允许实现一些真正的整洁编码。
因为在 Flask 中每个视图都是一个函数，而装饰器
可以用来把额外的功能注射到一个或多个函数中。
其中 :meth:`~flask.Flask.route` 方法装饰器
就是你可能用过的一个。对于部署你自己的装饰器来说，
有许多用例，例如，想象一下你有一个视图函数，它
应该只被人们用来登录用。如果一名用户访问了站点后，
却没有登录，那么就应该重定向到登录页面上。这是一个
良好的用例情况，那么用一个装饰器就是一个优秀的解决方案。

登录所需的装饰器
------------------------

那么我们来部署一个这样的装饰器吧。
一个装饰器就是一个函数，不过这个函数打包并替换另一个函数。
由于原始函数被替换了，你需要记住把原始函数的信息复制给新函数。
使用 :func:`functools.wraps` 函数来为你处理这种需求。

下面的例子假设登录页面叫作 ``'login'`` 并且当前用户已经
存储在 ``g.user`` 并且如果没有一个人登录的话就是 ``None`` 值。
定义一个装饰器的代码如下 ::

    from functools import wraps
    from flask import g, request, redirect, url_for

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

要使用装饰器，把它装饰给一个视图函数，放在最里面的位置上。
当应用下一个装饰器时，总要记住 :meth:`~flask.Flask.route` 方法
要作为最外面的装饰来使用。 ::

    @app.route('/secret_page')
    @login_required
    def secret_page():
        pass

.. 注意::
    对于登录页面来说，在一个 ``GET`` 请求之后，
    ``next`` 值会出现在 ``request.args`` 中。
    在登录表单发送 ``POST`` 请求时，你还要把它代入。
    你可以在 `input` 标签中用一个隐藏类型来实现，
    当用户登录时，然后从 ``request.form`` 取回它。 ::

        <input type="hidden" value="{{ request.args.get('next', '') }}"/>


缓存装饰器
-----------------

想象一下你有一个视图函数，要实现一种昂贵的计算任务，
并且你可能要缓存生成的结果一段时间。一个装饰器会是
这种情形的不错解决方案。我们正在假设你已经配置了一个
缓存，就像在 :ref:`caching-pattern` 文档中所说的一样。

下面是这个例子的缓存函数。它从一种具体的前缀（实际是一种格式化字符串）
和当前请求路径生成一个缓存钥匙。注意，我们正在使用一个函数先建立装饰器，
然后用来装饰视图函数。听起来有点坏坏的？不幸的是，这个函数有一点儿多层化，
但代码依然能够直接读懂。

装饰过的视图函数会像下面一样来工作：

1. 对于当前请求来说，根据当前路径来得到一个唯一的缓存钥匙。
2. 对于缓存钥匙来说会得到一个值。如果缓存返回某个内容，我们就会返回那个值。
3. 否则被调用的原始函数和返回值就存储在缓存中，根据提供的时限
   (默认是 5 分钟)。

代码如下::

    from functools import wraps
    from flask import request

    def cached(timeout=5 * 60, key='view/%s'):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = key % request.path
                rv = cache.get(cache_key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

注意，这里假设了一个可用的实例化 `cache` 对象，查看
:ref:`caching-pattern` 缓存模式文档内容了解更多信息。


模版化装饰器
--------------------

一种共同的模式被 TurboGears 这些家伙发明出来，那就是一种模版化装饰器。
这种装饰器的思路是你返回一个字典，字典值从视图函数代入到模版中，
然后模版被自动化翻译。使用这种方法，下面的3个例子所做的都是一件事::

    @app.route('/')
    def index():
        return render_template('index.html', value=42)

    @app.route('/')
    @templated('index.html')
    def index():
        return dict(value=42)

    @app.route('/')
    @templated()
    def index():
        return dict(value=42)

如你所见，如果没有提供模版名的话，它会使用带着句号的 URL 映射中的端点
转换成斜杠加上 ``'.html'`` 形式。否则就使用提供的模版名。
当装饰的函数返回时，返回的字典代入到翻译模版函数中。如果返回的是
``None`` 值的话，就假设成一个空字典；如果返回的不是字典的话，
我们就从无变化的函数来返回非字典值。这种方式你可以依然使用重定向函数，
或直接返回字符串。

如下就是模版装饰的代码::

    from functools import wraps
    from flask import request, render_template

    def templated(template=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                template_name = template
                if template_name is None:
                    template_name = request.endpoint \
                        .replace('.', '/') + '.html'
                ctx = f(*args, **kwargs)
                if ctx is None:
                    ctx = {}
                elif not isinstance(ctx, dict):
                    return ctx
                return render_template(template_name, **ctx)
            return decorated_function
        return decorator


端点装饰器
------------------

当你想要使用 werkzeug 路由系统来提供更灵活的性能时，
你需要把端点映射成定义在 :class:`~werkzeug.routing.Rule` 类中
提供给一个视图函数。这样才可能使用端点装饰器。例如::

    from flask import Flask
    from werkzeug.routing import Rule

    app = Flask(__name__)
    app.url_map.add(Rule('/', endpoint='index'))

    @app.endpoint('index')
    def my_index():
        return "Hello world"
