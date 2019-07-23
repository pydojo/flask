.. _views:

可插拔的视图
======================

.. versionadded:: 0.7

Flask 0.7 介绍了可插拔的视图，这个灵感来自 Django 的普通视图。
Django 的普通视图都是根据类来建立的，而不是函数。
主要目的是你可以替换部署中的一些部分，并且这种方法可以实现自定义可插拔视图。

基础原则
---------------

想象你有一个视图函数，该函数从数据库加载了一系列对象后
把这些对象翻译到一个模版中去::

    @app.route('/users/')
    def show_users(page):
        users = User.query.all()
        return render_template('users.html', users=users)

这就是简单且灵活的原则，但如果你想要把这个视图函数提供到一个普通模式中的话，
普通模式可以适应其它模型和模版，同时你也想要更具灵活性。
这就是需要可插拔基于类的视图该放置的地方。
第一步，要把这个函数转换到一个类的形式中，你要写成如下代码::


    from flask.views import View

    class ShowUsers(View):

        def dispatch_request(self):
            users = User.query.all()
            return render_template('users.html', objects=users)

    app.add_url_rule('/users/', view_func=ShowUsers.as_view('show_users'))

如你所见一样，你建立了一个 :class:`flask.views.View` 类的子类，然后部署
:meth:`~flask.views.View.dispatch_request` 方法时用原函数代码进行覆写。
那么后面我们还要把这个子类转换到一个真正的视图函数，通过使用
:meth:`~flask.views.View.as_view` 类方法来实现。
代入到该方法中的字符串是稍后会拥有的视图函数端点名。但这里的例子没有什么帮助，
所以让我们重构一下代码::


    from flask.views import View

    class ListView(View):

        def get_template_name(self):
            raise NotImplementedError()

        def render_template(self, context):
            return render_template(self.get_template_name(), **context)

        def dispatch_request(self):
            context = {'objects': self.get_objects()}
            return self.render_template(context)

    class UserView(ListView):

        def get_template_name(self):
            return 'users.html'

        def get_objects(self):
            return User.query.all()

当然对于一个小例子来说不是具有帮助，但作为解释基础原则来说足够好了。
当你有一个基于类的视图时，问题都来自 ``self`` 指向了什么。
这种工作方式就是不管什么时候，请求就被调度给一个建立完的新实例，
然后 :meth:`~flask.views.View.dispatch_request` 方法带着参数
被调用，参数都是来自 URL 规则中的内容。类自身就是用这些代入到
:meth:`~flask.views.View.as_view` 方法中的参数进行实例化的。
对于实例来说，你可以写一个像如下这个类::

    class RenderTemplateView(View):
        def __init__(self, template_name):
            self.template_name = template_name
        def dispatch_request(self):
            return render_template(self.template_name)

然后你可以把实例注册成如下这样::

    app.add_url_rule('/about', view_func=RenderTemplateView.as_view(
        'about_page', template_name='about.html'))

请求方法提醒
----------------

可插拔视图都是附着在网络应用上，就像一个正规的函数既可以使用
 :func:`~flask.Flask.route` 函数方式，也可以使用更好的
:meth:`~flask.Flask.add_url_rule` 方法。不管如何做到的，
那就意味着你要提供 HTTP 方法名给视图。为了把请求方法名信息移动
到类里，你可以提供一个 :attr:`~flask.views.View.methods` 
属性拥有这类信息::

    class MyView(View):
        methods = ['GET', 'POST']

        def dispatch_request(self):
            if request.method == 'POST':
                ...
            ...

    app.add_url_rule('/myview', view_func=MyView.as_view('myview'))

基于调度的方法
------------------------

对于 RESTful APIs 来说，为每个 HTTP 请求方法执行一个不同的函数特别有帮助。
使用 :class:`flask.views.MethodView` 类你可以容易实现。
每个 HTTP 请求方法映射到一个同名的函数上（只需要用小写字母即可）::

    from flask.views import MethodView

    class UserAPI(MethodView):

        def get(self):
            users = User.query.all()
            ...

        def post(self):
            user = User.from_form_data(request.form)
            ...

    app.add_url_rule('/users/', view_func=UserAPI.as_view('users'))

这种方式你也不用提供 :attr:`~flask.views.View.methods` 属性了。
它已经自动根据定义在类里的方法设置好了。

装饰器视图
----------------

由于视图类自身不是一个视图函数，而视图函数才能加入到路由系统中，
所以给类自身使用装饰器就没有意义。
相反你既可以手动装饰
:meth:`~flask.views.View.as_view` 方法返回的值::

    def user_required(f):
        """Checks whether user is logged in or raises error 401."""
        def decorator(*args, **kwargs):
            if not g.user:
                abort(401)
            return f(*args, **kwargs)
        return decorator

    view = user_required(UserAPI.as_view('users'))
    app.add_url_rule('/users/', view_func=view)

从 Flask 0.8 开始，也有另一种方式，那就是你可以描述一个装饰器列表，
这个装饰器列表是要写在类中来声明::

    class UserAPI(MethodView):
        decorators = [user_required]

由于隐含的 ``self`` 来自调用类时，显然你不能使用正规的视图函数装饰器
用法放在每个视图方法上，不管如何，你要记住这一点。

针对 APIs 的方法视图
-------------------------

网络 APIs 常常与 HTTP 动词紧密合作，所以部署一个这样的 API 根据
:class:`~flask.views.MethodView` 类实现就包含了大量意义。
那就是说，你要注意 API 所需要的不同 URL 规则，而这些规则都要有相同
的方法视图。对于实例来说，想象一下你正在揭露网络上的一个用户对象：

=============== =============== ======================================
URL             Method          Description
--------------- --------------- --------------------------------------
``/users/``     ``GET``         Gives a list of all users
``/users/``     ``POST``        Creates a new user
``/users/<id>`` ``GET``         Shows a single user
``/users/<id>`` ``PUT``         Updates a single user
``/users/<id>`` ``DELETE``      Deletes a single user
=============== =============== ======================================

那么你该如何使用 :class:`~flask.views.MethodView` 类来实现那件事呢？
技巧就是得到你提供给相同视图多个路由规则而获得的优势。

让我们假设此时的视图长如下这个样子::

    class UserAPI(MethodView):

        def get(self, user_id):
            if user_id is None:
                # return a list of users
                pass
            else:
                # expose a single user
                pass

        def post(self):
            # create a new user
            pass

        def delete(self, user_id):
            # delete a single user
            pass

        def put(self, user_id):
            # update a single user
            pass

那么我们如何用钩子做到把这个视图与路由系统连在一起呢？
通过增加2条规则后明确地提醒每个方法::

    user_view = UserAPI.as_view('user_api')
    app.add_url_rule('/users/', defaults={'user_id': None},
                     view_func=user_view, methods=['GET',])
    app.add_url_rule('/users/', view_func=user_view, methods=['POST',])
    app.add_url_rule('/users/<int:user_id>', view_func=user_view,
                     methods=['GET', 'PUT', 'DELETE'])

如果你有大量 APIs 看起来像你可以重构的那个的话，注册代码就是::

    def register_api(view, endpoint, url, pk='id', pk_type='int'):
        view_func = view.as_view(endpoint)
        app.add_url_rule(url, defaults={pk: None},
                         view_func=view_func, methods=['GET',])
        app.add_url_rule(url, view_func=view_func, methods=['POST',])
        app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                         methods=['GET', 'PUT', 'DELETE'])

    register_api(UserAPI, 'user_api', '/users/', pk='user_id')
