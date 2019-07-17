.. _blueprints:

使用蓝图技术模块化网络应用
====================================

.. currentmodule:: flask

.. versionadded:: 0.7

Flask 使用了一个 *蓝图* 概念为把网络应用制作成组件，然后在一个网络应用里或
横跨多个网络应用中支持共同模式的集成。蓝图技术可以极大的简化大型网络应用工作
如何进行，并且提供了一种中心意义给 Flask 扩展件来注册在网络应用上的操作。
一个 :class:`Blueprint` 类实例对象工作类似一个 :class:`Flask` 网络应用对象，
但蓝图对象实际上不是一个网络应用。蓝图对象更像是一张如何建造的 *图纸* 或者是
扩展了一个网络应用。

为什么要用蓝图技术？
-----------------------

在 Flask 中的蓝图技术都是用在如下情况中：

* 把一个网络应用分解成一套蓝图。对于更大型的网络应用来说这是理想的解决之道；
  一个项目可能实例化成一个网络应用对象，初始化了许多扩展包，然后注册成一种蓝图收集对象。
* 在一个网络应用上把一个蓝图注册在一个 URL 地址前缀 且/或 注册在子域名上。
  URL 前缀/子域名中的许多参数就变成了共性视图函数的参数（包含默认参数）
  在这个蓝图里可以横跨所有视图函数使用。
* 在一个网络应用上把一个蓝图多次注册在含有不同的 URL 地址规则。
* 通过蓝图技术提供模版过滤器、静态文件、模版文件，和其它工具。
  一个蓝图不能部署多个网络应用或多个视图函数。
* 针对这些情况中的任何一种初始化一个 Flask 扩展件时，在一个网络应用上注册一个蓝图。

在 Flask 中一个蓝图不是一个可插拔的应用，因为蓝图实际上不是一个网络应用。
蓝图是一套操作，这个操作集合可以被注册在一个网络应用上，甚至注册多次。
为什么不能有多个网络应用对象呢？你可以查看（ :ref:`app-dispatch` 网络应用调度文档），
但你的多个网络应用会有各种配置，并且会在 WSGI 层进行管理。

相反蓝图提供了在 Flask 层的分离技术，分享一个网络应用的配置，
然后在注册的时候根据需要可以改变一个网络应用对象。
蓝图技术的缺陷是一旦一个网络应用建立完你不能取消注册一个蓝图，
只有销毁整个网络应用对象后才能取消注册蓝图。

蓝图概念
-------------------------

蓝图的基础概念是蓝图把操作记录下来，当注册到一个网络应用时才执行操作。
当调度请求和生成一端到另一端的 URLs 地址时，Flask 用蓝图来把视图函数关联起来。

我的第一张图纸
------------------

如下是一个最基础的蓝图样式。在此情况中我们想要部署一个蓝图，
这个蓝图就是直接实现静态模版的翻译工作::

    from flask import Blueprint, render_template, abort
    from jinja2 import TemplateNotFound

    simple_page = Blueprint('simple_page', __name__,
                            template_folder='templates')

    @simple_page.route('/', defaults={'page': 'index'})
    @simple_page.route('/<page>')
    def show(page):
        try:
            return render_template('pages/%s.html' % page)
        except TemplateNotFound:
            abort(404)

当你把一个函数与 ``@simple_page.route`` 装饰器绑定在一起的时候，
蓝图会记录下把函数 ``show`` 注册在一个网络应用上的意图，
此时还没有进行注册，只是记录你想要注册，可以理解成填写注册信息，
当后面进行注册时才能完成注册。另外它会用蓝图的名字作为函数的前缀端点，
蓝图的名字是 :class:`Blueprint` 类构造器建立的实例被指向名（这里
也就是 ``simple_page`` 这个变量名）。蓝图的名字不会修改 URL 地址，
只是作为端点来使用。

注册蓝图
----------------------

那么你如何注册一个蓝图呢？像下面一样::

    from flask import Flask
    from yourapplication.simple_page import simple_page

    app = Flask(__name__)
    app.register_blueprint(simple_page)

如果你检查注册完的网络应用上的 URL 地址规则的话，你会发现如下内容::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/' (HEAD, OPTIONS, GET) -> simple_page.show>])

第一条显然是来自网络应用自身的静态文件地址。
第二条是 ``simple_page`` 蓝图的 `show` 函数地址。
最后如你所见，都使用了蓝图名做前缀并且用了一个句号 (``.``) 来分隔。

不管如何做到的，蓝图也可以被挂载到不同的位置上::

    app.register_blueprint(simple_page, url_prefix='/pages')

然后看一下生成的地址规则，足以确认了挂载功能::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/pages/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/pages/' (HEAD, OPTIONS, GET) -> simple_page.show>])

上面我们提到过蓝图可以注册多次，尽管不是每个蓝图可能会作出正确的响应。
实际上如果你挂载了多于一次，它要根据蓝图是如何部署的来做出响应。

蓝图资源
-------------------

蓝图也可以提供资源。有时候你也许只想要把一个蓝图作为提供资源来使用。

蓝图资源文件夹
`````````````````````````

可能对于正规的网络应用来说，蓝图都会被考虑成放在一个文件夹里。
在同一个文件夹中组织多张蓝图，并不需要这样做，而且正常来说是不建议这么做。

文件夹是根据 :class:`Blueprint` 类的第二个参数推理出来的，正常来说是
 `__name__` 值。这个参数描述了 Python 执行时逻辑判断是模块名还是包名，
那么判断结果会关联到蓝图上。如果指向了一个实际的 Python 包名的话，
那么包（就是文件系统上的一个目录）就是资源文件夹。
如果是一个模块名的话，包含模块的包会是资源文件夹。
你可以访问 :attr:`Blueprint.root_path` 属性来查看资源文件夹是什么::

    >>> simple_page.root_path
    '/Users/username/TestProject/yourapplication'

要从这个文件夹快速打开资源，你可以使用 :meth:`~Blueprint.open_resource` 方法::

    with simple_page.open_resource('static/style.css') as f:
        code = f.read()

静态文件
````````````

一个蓝图可以揭露含有静态文件的一个文件夹，
通过把文件系统上的文件夹路径提供给 ``static_folder`` 参数即可。
路径既可以是绝对路径，也可以是蓝图位置上的相对路径::

    admin = Blueprint('admin', __name__, static_folder='static')

路径的最右边部分默认揭露在网址中。这种表现可以用 ``static_url_path`` 参数来改变。
因为这里的文件夹名叫 ``static`` ，它会在蓝图的 ``url_prefix`` 加上
 ``/static`` 后可以被使用。如果蓝图有一个 ``/admin`` 前缀的话，
 静态 URL 地址会是 ``/admin/static`` 。

端点名就是 ``blueprint_name.static`` 。你可以用 :func:`url_for` 函数
来生成到这个端点的 URLs 网址，就像使用网络应用的静态文件夹一样::

    url_for('admin.static', filename='style.css')

不管如何做到的，如果蓝图没有一个 ``url_prefix`` 的话，就无法访问蓝图的静态文件夹了。
在此处情况中这是因为 URL 地址会变成 ``/static`` 了，而网络应用的 ``/static``
路由会获得优先权。不像模版文件夹，如果文件没有在网络应用静态文件夹中的话，
蓝图静态文件夹不会被搜索。

模版
`````````

如果你想要蓝图来揭露模版，你可以通过提供 `template_folder` 参数给
:class:`Blueprint` 构造器来实现::

    admin = Blueprint('admin', __name__, template_folder='templates')

对于静态文件来说，路径可以是绝对路径，或者是指向蓝图资源文件夹的相对路径。

模版文件夹加入到模版搜索路径中，却带着一个较低的优先级，就是说使用蓝图来指向模版会比
用实际的网络应用指向模版文件夹搜索顺序靠后。蓝图的方式你可以容易覆写在实际网络应用中
一个蓝图提供的模版。这也意味着如果你不想让一个蓝图模版被意外覆写的话，那就要确保没有
其它的蓝图或实际网络应用模版有一样的相对路径。当多张蓝图提供了同样的相对模版路径时，
第一个注册的蓝图是最先进行搜索的。


那么如果你在 ``yourapplication/admin`` 文件夹中有一张蓝图的话，并且你想要翻译
 ``'admin/index.html'`` 模版，以及你已经提供了 ``templates`` 作为一个
 `template_folder` 的话，你要建立一个像这样的文件：
:file:`yourapplication/admin/templates/admin/index.html` 才可以。
对于这里额外要建立的 ``admin`` 文件夹，原因就是要避免我们的模版被一个名叫
 ``index.html`` 的模版覆写，因为在实际网络应用中的模版文件夹里会出现同名模版。

重要的事情再说一遍：如果你有一个名叫 ``admin`` 的蓝图，且你想翻译一个名叫
 :file:`index.html` 的模版，这个模版描述给这个蓝图，最好的思路就是把你的
模版层次建立成如下这样::

    yourpackage/
        blueprints/
            admin/
                templates/
                    admin/
                        index.html
                __init__.py

然后当你要翻译模版时，使用 :file:`admin/index.html` 作为查询模版的名字。
如果你在加载正确的模版过程中遇到问题，开启 ``EXPLAIN_TEMPLATE_LOADING`` 配置变量，
它会指导 Flask 来输出在每次 ``render_template`` 调用模版时到达模版位置的步骤。

建立 URLs 地址
------------------

如果你想要从一个页面链接到另一个页面，你可以使用 :func:`url_for` 函数，
就像你正常使用它一样，只是你的 URL 端点前缀要带着蓝图名和一个句号 (``.``)::

    url_for('admin.index')

另外如果你位于一个蓝图的视图函数中，或者一个翻译过的模版位置里的话，
如果你想要链接到同一个蓝图的另一个端点上，
你可以使用相对重定向来实现，只带一个句号作为端点的前缀即可::

    url_for('.index')

这样会为实例链接到 ``admin.index`` 地址上，此处当前请求被调度到任何一个其它
`admin` 蓝图端点上。

错误处理
--------------

蓝图支持错误处理器装饰器用法，就像 :class:`Flask` 网络应用对象一样，
所以建立一个具体的蓝图自定义错误页面是容易的事情。

如下是一个 "404 Page Not Found" 例外处理示例::

    @simple_page.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/404.html')

大多数错误处理器都会直接有效；不管如何做到的，这里有一项警告，
对于 404 和 405 例外的处理要考虑好。这两个例外处理都只从一个
合适的 ``raise`` 语句被引入，或者在另一个蓝图的视图函数中调用
一个 ``abort`` 来引入这两个错误处理；它们两个不会被例如，
一个非法 URL 地址的访问而触发。这是因为蓝图不拥有某一个 URL 空间，
所以如果给出一个非法 URL 地址，网络应用实例不知道该运行那张蓝图的错误处理器。
如果你想要为这种 URL 前缀的错误执行不同的处理策略，它们两个就要
定义在网络应用层，使用 ``request`` 代理对象来实现::

    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex):
        if request.path.startswith('/api/'):
            return jsonify_error(ex)
        else:
            return ex

更多错误处理的信息查看 :ref:`errorpages` 参考文档。
