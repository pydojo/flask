.. _app-factories:

网络应用工厂模式
=====================

如果你已经正在对你的网络应用使用包和蓝图技术的话（:ref:`blueprints` 参考文档），
这里有一组真正良好的方法来进一步提升你的经验。
一个共同采用的模式就是，当蓝图导入后的时候建立网络应用对象。
但如果你把这个对象的建立移动到一个函数中去的话，你可以稍后建立这个应用的多个实例。

那么为什么你想要这样做呢？

1.  测试。你可以用不同的设置来测试每种情况，因为你可以建立许多网络应用的实例。
2.  多种实例。想象一下，你想要运行同一个网络应用的不同版本时。
    当然你需要有多种实例，在你的网络服务器里含有不同的配置，但如果你使用了工厂模式的话，
    你就可以对一个应用建立多种实例，运行在同一个应用进程中，这样就很上手了。

那么你如何实际地部署工厂模式呢？

基础工厂
---------------

在一个函数中配置网络应用的思路是如下这样::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

        from yourapplication.views.admin import admin
        from yourapplication.views.frontend import frontend
        app.register_blueprint(admin)
        app.register_blueprint(frontend)

        return app

工厂模式的缺点是在蓝图导入的时候你不能使用网络应用对象。
不管如何做到的，你要在一个请求中来使用网络应用对象。
你如何使用配置来访问网络应用呢？
使用 :data:`~flask.current_app` 数据::

    from flask import current_app, Blueprint, render_template
    admin = Blueprint('admin', __name__, url_prefix='/admin')

    @admin.route('/')
    def index():
        return render_template(current_app.config['INDEX_TEMPLATE'])

这就是我们以配置的方式来查询一个模版的名字。

工厂模式与扩展件
----------------------

最好就是建立你的扩展件和应用工厂，这样扩展件对象不会在初始化时就绑定到应用上。

使用 `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_ 作为一个例子，
如下这些行代码你不应该添加任何内容::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        db = SQLAlchemy(app)

但是在 model.py （或相同形式中）里::

    db = SQLAlchemy()

之后在你的 application.py (或相同形式中）里::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

就需要使用这种设计模式了，无应用具体的状态存储在扩展件对象上，
所以一个扩展件对象可以给多个应用使用。
关于扩展件的设计参考 :doc:`/extensiondev` 文档了解更多信息。

使用网络应用
------------------

要运行这样一种网络应用，你可以使用命令行 :command:`flask` 命令::

    $ export FLASK_APP=myapp
    $ flask run
    
Flask 会自动地在 ``myapp`` 中检测到工厂模式 (``create_app`` 或 ``make_app``)。
你也可以把参数代入到工厂函数里，想如下这样::

    $ export FLASK_APP="myapp:create_app('dev')"
    $ flask run
    
那么在 ``myapp`` 里的 ``create_app`` 工厂函数会带着字符串
 ``'dev'`` 作为参数值被调用。查看 :doc:`/cli` 文档了解更多细节。

工厂模式的改善
--------------------

工厂函数不是非常聪明，但你可以改善工厂函数。
下面的变更都是直接部署：

1.  对于单元测试来说，让工厂函数可以代入配置值，这样你就不用在文件系统上建立配置文件了。
2.  当网络应用被配置的时候，从一个蓝图来调用一个工厂函数，
    这样你就有了一个修改网络应用属性的地方（就像在请求处理器等等，之前/之后应用钩子一样）。
3.  如果需要的话，当建立网络应用的时候，把工厂函数加入到 WSGI 中间件里去。
