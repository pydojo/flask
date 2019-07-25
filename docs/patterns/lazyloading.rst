按需加载视图
====================

Flask 常常使用装饰器。装饰器都是简单的，并且让你有一个
正确的 URL 地址指向所描述的被调用的函数。不管如何做到的，
这种方法也有一个缺点：
意味着所有你使用装饰器的代码都要提前导入，
否则 Flask 永远不会真正找到视图函数。

如果你的网络应用导入的快，那么就有一个问题。
也需要不得已在系统上来做导入，就像 Google 的网络应用引擎，
或其它系统一样。所以如果你突然注意到你的网络应用
大到不适合使用这种方法，你可以回滚到使用一种
中心化的 URL 映射上。

开启具有一种中心化的 URL 映射系统就是
:meth:`~flask.Flask.add_url_rule` 方法来实现。
代替使用装饰器，你要有一个配置所有 URLs 的文件。

转换成中心化的 URL 映射
---------------------------------

想象一下此时的网络应用看起来像下面一样::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        pass

    @app.route('/user/<username>')
    def user(username):
        pass

那么，使用中心化的方法你要有一个含有这些视图函数的文件
(:file:`views.py`) 但不使用任何一个装饰器::

    def index():
        pass

    def user(username):
        pass

然后再用一个文件来配置这个网络应用把这些函数映射到
对应的 URLs 地址上::

    from flask import Flask
    from yourapplication import views
    app = Flask(__name__)
    app.add_url_rule('/', view_func=views.index)
    app.add_url_rule('/user/<username>', view_func=views.user)

稍后加载
------------

我们做了这么多只是把视图函数和路由分离开来，但存储函数的模块依然要提前加载。
技巧就是要按照需求来实际加载视图函数。这个技巧可以用一个助手类来完成，
该类行为就像一个函数一样，但内部地导入先使用的真正函数::

    from werkzeug import import_string, cached_property

    class LazyView(object):

        def __init__(self, import_name):
            self.__module__, self.__name__ = import_name.rsplit('.', 1)
            self.import_name = import_name

        @cached_property
        def view(self):
            return import_string(self.import_name)

        def __call__(self, *args, **kwargs):
            return self.view(*args, **kwargs)

这里的重点是什么？那就是 `__module__` 和 `__name__` 都要正确地进行设置。
这是由 Flask 内部来使用的，从而弄清楚如何命名 URL 规则，
此时你自己不用提供一个规则名。

然后你可以定义你的中心化位置来把视图函数与路由组合起来，就像下面一样::

    from flask import Flask
    from yourapplication.helpers import LazyView
    app = Flask(__name__)
    app.add_url_rule('/',
                     view_func=LazyView('yourapplication.views.index'))
    app.add_url_rule('/user/<username>',
                     view_func=LazyView('yourapplication.views.user'))

你可以进一步优化这种方法，还要写一些代码到一个函数中，
让这个函数调用 :meth:`~flask.Flask.add_url_rule` 方法，
通过使用项目目录名和一个句号作为前缀，然后根据需要把
 `view_func` 打包进一个 `LazyView` 类中。  ::

    def url(import_name, url_rules=[], **options):
        view = LazyView('yourapplication.' + import_name)
        for url_rule in url_rules:
            app.add_url_rule(url_rule, view_func=view, **options)

    # add a single route to the index view
    url('views.index', ['/'])

    # add two routes to a single function endpoint
    url_rules = ['/user/','/user/<username>']
    url('views.user', url_rules)

这里要记住一件事，那就是在请求处理器之前和之后都要在一个文件中，
该文件要提前导入才能正确地工作在第一个请求上。
对于剩下的任何一个装饰器来说都要这样做。
