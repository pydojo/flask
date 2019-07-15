.. _quickstart:

快速开始
==========

是不是饥渴难耐了？本篇会给你一次 Flask 良好的指导。
假设你已经安装完 Flask 了，如果还没安装，回顾一下
:ref:`installation` 内容。


一个迷你应用
---------------------

一个迷你型的 Flask 应用看来就是下面这个样子::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

那么这段代码做了什么？

1. 首先我们导入了 :class:`~flask.Flask` 类。从而该类的一个实例会变成我们的 WSGI 应用。
2. 下一行我们建立了一个该类的实例。第一个参数值是应用模块或包的名字。
   如果你们只用做一个单一模块的话（如同此处的例子一样），
   你应该使用 ``__name__`` 这个变量名，因为依据模块启动的方式是应用方式或导入方式而不同。
   （``'__main__'`` 会与该变量做比较）。该变量名是需要的，这样 Flask 知道去哪里寻找模版、
   静态文件，等等资源。对于更多的相关信息看一下 :class:`~flask.Flask` 文档。
3. 当我们接下来使用 :meth:`~flask.Flask.route` 方法作为装饰器时，它告诉 Flask 应该
   用哪个 URL 地址来触发我们的视图函数。
4. 路由方法中给出的名字也会用来生成 URLs 地址提供给视图函数，
   然后返回的消息就是我们想要显示在用户浏览器中的内容。

把这段代码保存成 :file:`hello.py` 文件或其它名字的 Python 文件。
确保不要与 :file:`flask.py` 名字一样，因为这会导致与使用 Flask 产生冲突。

要运行应用，你既可以使用 :command:`flask` 命令方式，也可以使用 python 的 ``-m`` 带着 Flask 切换方式。
在你运行应用之前，你需要告诉终端，应用要与导出``FLASK_APP`` 环境变量一起工作::

    $ export FLASK_APP=hello.py
    $ flask run
     * Running on http://127.0.0.1:5000/

如果你们用 Windows 系统的话，环境变量句法要根据命令行解释器用法。
在命令行窗口中::

    C:\path\to\app>set FLASK_APP=hello.py

以及在 PowerShell 窗口中::

    PS C:\path\to\app> $env:FLASK_APP = "hello.py"

另外你可以使用 :command:`python -m flask`::

    $ export FLASK_APP=hello.py
    $ python -m flask run
     * Running on http://127.0.0.1:5000/

命令行启动方式加载了一种非常简单的内置服务器，好到足以用来测试开发使用，
但可能不是你想要用在生产中的方式。对于部署来说众多选项查看 :ref:`deployment` 文档。

现在回看一下 `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_ 地址，
你在浏览器中可以看到视图函数返回的内容出现在页面上了。

.. _public-server:

.. admonition:: 从外部看到服务器

   如果你运行服务器的话，你会注意到服务器只可以在自己的电脑上访问，
   网络中的其它电脑无法看到。采用这种默认配置是因为在调试模式中
   应用的一名使用者可以执行你电脑上的任意 Python 代码。

   如果你已经禁用了调试器的话，或者信任你网络中的其它用户的话，
   你可以让服务器变成公共可用模式，直接通过增加如下选项
   ``--host=0.0.0.0`` 到命令行中::

       $ flask run --host=0.0.0.0

   这就告诉了你的操作系统去监听所有公共 IPs 地址。


如果服务器没启动该怎么办
---------------------------------------

在使用 :command:`python -m flask` 命令失败时，或 :command:`flask` 命令不存在的话，
可能有许多原因导致。首先你需要查看错误消息。

老旧的 Flask 版本
````````````````````

比 0.11 版本还要旧的 Flask 曾使用不同方式启动应用。当时 :command:`flask` 命令还没有，
并且也没有 :command:`python -m flask` 命令方式。在此种情况中你有两个选择：
更新到最新的 Flask 版本，或者查看 :ref:`server` 文档了解运行一个服务器的另一种方法。

非法导入名
```````````````````

在 ``FLASK_APP`` 环境变量设置的模块名要在 :command:`flask run` 命令运行时被导入。
这种情况中，模块名设置不正确，你会得到一个错误。（或者如果调试开启的话，
当你导航到应用时也会提示错误。）它会告诉你要导入什么和为什么失败。

最共同的原因是拼写错误，或者因为你还没建立一个 ``app`` 对象。

.. _debug-mode:

调试模式
----------

（想要只记录错误日志和堆栈线索吗？查看 :ref:`application-errors` 文档。）

该 :command:`flask` 脚本是良好地启动一个本地开发服务器工具，但你不得不在每次变更你的代码时手动重启服务器。
手动不是非常良好的选择，并且 Flask 可以比手动更好。如果你开启调试支持的话，
服务器会在代码变更后重新加载，以及如果有什么问题也会提供有帮助的调试信息。

要开启全部开发特性（包括调试模式）你可以导出 ``FLASK_ENV`` 环境变量后
设置成 ``development`` 值，在运行服务器前执行此项操作::

    $ export FLASK_ENV=development
    $ flask run

（在 Windows 系统上你需要使用 ``set`` 命令代替 ``export`` 命令。）

该项操作效果如下：

1.  激活调试器，
2.  激活自动加载服务器，
3.  在 Flask 应用上开启调试模式。

你也可以通过环境变量来控制调试模式，通过导出 ``FLASK_DEBUG=1`` 环境变量。

更多的参数都解释在 :ref:`server` 文档中。

.. admonition:: 注意

   尽管交互式调试器不工作在叉子环境中（因为叉子版本几乎不用在生产服务器中），
   它依然允许任意代码的执行。这会造成主要的安全风险，并且因此**永远不要用在生产机器上**。

调试器执行中的截图：

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

在使用调试器中的更多信息可以在 `Werkzeug documentation`_ 文档中找到。

.. _Werkzeug documentation: http://werkzeug.pocoo.org/docs/debug/#using-the-debugger

还记得另一个调试器吗？查看 :ref:`working-with-debuggers` 参考内容。


路由
-------

现代网络应用使用有意义的 URLs 地址来帮助用户访问。用户们都更可能喜欢一个页面并回顾页面都是通过
容易记住的 URL 地址来访问，并且直接用网址来访问一个页面。

使用 :meth:`~flask.Flask.route` 方法装饰器把一个视图函数与一个 URL 地址绑定在一起。 ::

    @app.route('/')
    def index():
        return 'Index Page'

    @app.route('/hello')
    def hello():
        return 'Hello, World'

你可以做的更多！你可以把 URL 部分变成动态形式后伴随多个规则给一个视图函数。

变量规则
``````````````

你可以把变量部分加入到一个 URL 区域，通过使用 ``<variable_name>`` 来标记。
之后你的视图函数把 ``<variable_name>`` 接受成一个关键字参数。
另外，你可以使用一个转换器来描述参数的类型，就像 ``<converter:variable_name>`` 这种形式 ::

    @app.route('/user/<username>')
    def show_user_profile(username):
        # show the user profile for that user
        return 'User %s' % username

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        # show the post with the given id, the id is an integer
        return 'Post %d' % post_id

    @app.route('/path/<path:subpath>')
    def show_subpath(subpath):
        # show the subpath after /path/
        return 'Subpath %s' % subpath

转换器类型：

========== ==========================================
``string`` （默认）不用一个反斜杠接受任何文本内容
``int``    接受正整数
``float``  接受正浮点数值
``path``   类似 ``string`` 但也接受许多反斜杠
``uuid``   接受 UUID 字符串
========== ==========================================

唯一 URLs 地址 / 重定向行为
``````````````````````````````````

如下2条规则在使用一个反斜杠做结尾时是有区别的。 ::

    @app.route('/projects/')
    def projects():
        return 'The project page'

    @app.route('/about')
    def about():
        return 'The about page'

对于 ``projects`` 端点来说有一个反斜杠做结尾是权威的 URL 地址形式。
就像在一个文件系统中的文件夹表示一样。如果你访问网址不带反斜杠结尾的话，
Flask 会为你重定向到权威网址形式。

对于The canonical URL for the ``about`` 端点来说没有一个反斜杠作为网址也是权威的形式。
它类似一个文件的路径名。用有反斜杠结尾的方式访问它的话会产生一个 404  "Not Found" 错误代码。
这帮助让 URLs 成为这类资源的唯一网址形式，也帮助搜索引擎避免二次索引同一个页面。


.. _url-building:

URL 地址建立
````````````

要把一个 URL 地址建立给一个具体的视图函数，使用 :func:`~flask.url_for` 函数。
它把视图函数名接受成自己的第一个参数值，然后还有多关键字参数，每个参数都对应着 URL 规则
中一个变量部门。未知的变量部分都会追加到 URL 中作为查询参数。

为什么你想要建立 URLs 地址时使用 URL 逆向函数 :func:`~flask.url_for` 来代替
在你的模版中使用硬编码方式呢？

1. 逆向常常要比硬编码 URLs 地址更具描述性。
2. 你可以动态改变你的 URLs 地址，代替了每次手动改变硬编码 URLs 地址。
3. URL 地址建立中明确地处理具体字符的转义和 Unicode 数据。
4. 生成的路径都一直是绝对路径，这样避免了在浏览器中相对路径的意外行为。
5. 如果你的应用放在 URL 根地址以外的话，例如，
   是 ``/myapplication`` 地址，而不是 ``/`` 地址的话，
   :func:`~flask.url_for` 函数能为你正确地处理。

举例，这里我们使用了 :meth:`~flask.Flask.test_request_context` 方法来尝试
 :func:`~flask.url_for` 函数。那么 :meth:`~flask.Flask.test_request_context`
方法告诉 Flask 要表现成处理一个地址请求，甚至我们使用一个 Python 会话。
查看 :ref:`context-locals` 参考内容。

.. code-block:: python

    from flask import Flask, url_for

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'index'

    @app.route('/login')
    def login():
        return 'login'

    @app.route('/user/<username>')
    def profile(username):
        return '{}\'s profile'.format(username)

    with app.test_request_context():
        print(url_for('index'))
        print(url_for('login'))
        print(url_for('login', next='/'))
        print(url_for('profile', username='John Doe'))

.. code-block:: text

    /
    /login
    /login?next=/
    /user/John%20Doe


HTTP 方法
````````````

在访问 URLs 地址时，网络应用都使用不同的 HTTP 方法。与 Flask 工作时你自己应该熟悉这些方法。
默认情况，一个路由只回应 ``GET`` 方法请求。你可以使用  :meth:`~flask.Flask.route` 装饰器的
 ``methods`` 参数来处理不同的 HTTP 方法。
::

    from flask import request

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            return do_the_login()
        else:
            return show_the_login_form()

如果 ``GET`` 方法出现的话， Flask 自动增加支持 ``HEAD`` 方法后
根据 `HTTP RFC`_ 来处理 ``HEAD`` 请求。同样为你自动实施 ``OPTIONS`` 方法。

.. _HTTP RFC: https://www.ietf.org/rfc/rfc2068.txt

静态文件
------------

动态网络应用也需要静态文件。常常都是 CSS 和 JavaScript 文件。
理想情况你的网络服务器已配置好这些文件的服务，但在开发期间 Flask 也可以做到。
只是在你的包路径中建立一个名叫 :file:`static` 文件夹，或者在你的模块边上建立，
之后在应用上就可以使用 ``/static`` 了。

要为静态文件生成 URLs 地址，使用具体的 ``'static'`` 端点名::

    url_for('static', filename='style.css')

静态文件存储在文件系统中，如同 :file:`static/style.css` 一样。

翻译模版
-------------------

在 Python 内部生成 HTML 不是有趣的事情，并且实际上非常繁重的工作，
因为你不得不自己做 HTML 转义处理来保持应用的安全性。
由于 Flask 配置了 `Jinja2 <http://jinja.pocoo.org/>`_ 模版引擎
作为核心，可以为你自动完成此项工作。

要翻译一个模版，你可以使用 :func:`~flask.render_template` 函数。
你所要做的就是提供模版名称和你想要代入到模版引擎中的变量作为关键字参数。
如何翻译一个模版，这里有一个简单的例子::

    from flask import render_template

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('hello.html', name=name)

Flask 会在 :file:`templates` 目录中查找模版文件。所以如果你的应用是一个模块的话，
这个模版目录在同级路径下；如果应用是一个包的话，那么模版目录应该在你的包里：

**Case 1**: a module::

    /application.py
    /templates
        /hello.html

**Case 2**: a package::

    /application
        /__init__.py
        /templates
            /hello.html

对于模版来说你可以使用 Jinja2 模版的全部性能。回顾官方 `Jinja2 Template Documentation
<http://jinja.pocoo.org/docs/templates>`_ 文档了解更多信息。

如下是一个模版示例：

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Flask</title>
    {% if name %}
      <h1>Hello {{ name }}!</h1>
    {% else %}
      <h1>Hello, World!</h1>
    {% endif %}

在模版中你也可以访问 :class:`~flask.request` 类，
:class:`~flask.session` 类和 :class:`~flask.g` 类[#]_ 也可以访问对象函数
 :func:`~flask.get_flashed_messages`

如果使用了模版继承特性的话，模版变得特别有用。如果你想要知道模版继承是如何工作的，
回顾 :ref:`template-inheritance` 模式文档的内容。
基础的模版继承让每个页面上的某些元素分享给其它模版（例如 header, navigation 和 footer 这些元素）。

自动化转义开启后，那么如果 ``name`` 所含的HTML内容会自动地进行转义。
如果你信任一个变量的话，并且知道该变量是一种安全的HTML内容（例如变量来自一个把维基转换成HTML的模块）
你可以通过使用 :class:`~jinja2.Markup` 类来标记成安全内容，
或者在模版中通过使用 ``|safe`` 过滤器标记成安全内容。回顾 Jinja2 文档了解更多示例。

如下是 :class:`~jinja2.Markup` 类如何工作的基本介绍::

    >>> from flask import Markup
    >>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
    Markup(u'<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
    >>> Markup.escape('<blink>hacker</blink>')
    Markup(u'&lt;blink&gt;hacker&lt;/blink&gt;')
    >>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
    u'Marked up \xbb HTML'

.. versionchanged:: 0.5

   对于所有模版来说自动化转义不再默认开启。如下扩展名的模版会触发自动转义：
    ``.html``, ``.htm``, ``.xml``, ``.xhtml``  
   从一个字符串形式加载模版都默认禁用自动转义。

.. [#] 不知道 :class:`~flask.g` 对象是什么？它是根据自己的需要来存储信息的一个对象，
   查看该对象的文档介绍 (:class:`~flask.g`) 后参考 :ref:`sqlite3` 了解更多信息。


访问请求数据
----------------------

对于网路应用来说，一个客户端发送给服务器的数据响应是至关重要的。
在 Flask 中这类信息是由全局 :class:`~flask.request` 对象提供的。
如果你有一些使用 Python 的经验，你也许想知道这个对象如何变成全局对象，
并且想知道 Flask 如何管理这个对象，仍然是线程安全。回答这些问题的是本地语境：


.. _context-locals:

本地语境
``````````````

.. admonition:: 内部信息

   如果你想要理解本地语境是如何工作的，以及你如何部署本地语境来实现测试，
   阅读本部分内容，否则跳过即可。

在 Flask 中某些对象都是全局范围对象，但不是常用类型。
这些对象实际上都是代理了一些对象，被代理但对象都是本地具体的语境中但对象。
这里所说的，实际上非常容易理解。

想象一下处理线程的语境。一个请求进来后，网络服务器决定建立一个新的线程
（或者建立其它什么，依据对象处理并发系统的能力要比线程好）。
当 Flask 启动自身内部请求处理时，它会弄清楚当前线程是激活的语境，
然后把当前应用和 WSGI 环境绑定到那个语境上（线程上）。
它确实以一种智能的方式来运作，所以一个应用可以引入另一个应用且不存在中断影响。

那么这对你来说有什么意义呢？基本上你可以完全不考虑本地语境问题，
除非你正在进行单元测试这类工作。你会注意到代码根据一个请求对象，
会突然中断，因为此时没有请求对象。解决方案就是自己建立一个请求对象后
把请求对象绑定到本地语境上。对于单元测试时的最简单解决方案就是使用
 :meth:`~flask.Flask.test_request_context` 语境管理器方法。
语境管理器与 ``with`` 语句的组合使用会把一个测试请求绑定到本地语境中，
这样你可以与测试请求进行互动了。这里有一个示例::

    from flask import request

    with app.test_request_context('/hello', method='POST'):
        # now you can do something with the request until the
        # end of the with block, such as basic assertions:
        assert request.path == '/hello'
        assert request.method == 'POST'

另外一个可能就是把一个完整的 WSGI 环境代入到
:meth:`~flask.Flask.request_context` 方法中::

    from flask import request

    with app.request_context(environ):
        assert request.method == 'POST'

请求对象
``````````````````

请求对象文档内容在 API 文档部分中，并且我们不会在这里介绍细节（查看 :class:`~flask.Request` 文档）。
这里是最共同的操作概况介绍。首先你要从 ``flask`` 模块导入它::

    from flask import request

当前的请求方法是通过使用 :attr:`~flask.Request.method` 属性来使用的。
要从数据来访问（即数据以一个 ``POST`` 或 ``PUT`` 请求方法来进行传输）
你可以使用 :attr:`~flask.Request.form` 属性来实现。
前面提到的两个属性，如下是一个完整的例子::

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        error = None
        if request.method == 'POST':
            if valid_login(request.form['username'],
                           request.form['password']):
                return log_the_user_in(request.form['username'])
            else:
                error = 'Invalid username/password'
        # the code below is executed if the request method
        # was GET or the credentials were invalid
        return render_template('login.html', error=error)

如果在 ``form`` 属性中没有键存在的话会发生什么？在这种情况中，
一个具体的 :exc:`KeyError` 例外会抛出。你可以捕获成一个标准的
 :exc:`KeyError` 例外类型，但如果你不这样做的话，会用一个 HTTP 400
败坏的请求错误页面来代替例外显示出来。所以对于许多情形你不需要处理这种问题。

要访问 URL 网址中提交的参数 (``?key=value``) 你可以使用
:attr:`~flask.Request.args` 属性实现::

    searchword = request.args.get('key', '')

我们建议使用 `get` 访问 URL 网址中的参数，或者通过捕获 :exc:`KeyError` 例外的方法，
因为用户也许改变了 URL 网址并且呈现给用户一个 400 败坏请求页面不是很友好。

对于一个完整的请求方法列表和请求对象属性列表来说，回顾 :class:`~flask.Request` 文档内容。


上传文件
````````````

使用 Flask 你可以容易地处理上传文件。只需要别忘记在 HTML 表单上设置
 ``enctype="multipart/form-data"`` 属性即可，否则浏览器根本就不传输你的文件。

上传的所有文件都存储在内存中，或者存储在文件系统的临时目录里。
你可以访问这些文件，通过在请求对象上使用 :attr:`~flask.request.files` 属性来查找。
每个上传的文件都存储在那个字典中。它就像 Python 的标准 :class:`file` 类对象一样，
但它也有一个 :meth:`~werkzeug.datastructures.FileStorage.save` 方法，该方法
允许你把文件存储在服务器的文件系统上。如下是说明如何工作的一个简单例子::

    from flask import request

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/uploaded_file.txt')
        ...

如果你想知道在文件上传到你的网络应用之前，客户端如何命名文件的话，你可以访问
:attr:`~werkzeug.datastructures.FileStorage.filename` 属性来获得。
不管如何做到的，要记住这个属性值是可以被伪造的，所以永远不要相信该属性值。
如果你想要使用客户端的文件名来存储文件到服务器上的话，
通过 Werkzeug 提供的 :func:`~werkzeug.utils.secure_filename` 函数
来获得客户端上传的文件名::

    from flask import request
    from werkzeug.utils import secure_filename

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/' + secure_filename(f.filename))
        ...

对于一些更好的例子来说，查看 :ref:`uploading-files` 模式文档做参考。

Cookies
```````

要访问 cookies 的话，使用 :attr:`~flask.Request.cookies` 属性。
要设置 cookies 你可以使用响应对象的
 :attr:`~flask.Response.set_cookie` 属性方法。请求对象的
:attr:`~flask.Request.cookies` 属性是一个含有所有客户端传输过来的 cookies 字典。
如果你想要使用会话的话，不要直接使用 cookies 字典，而是使用 Flask 中的
:ref:`sessions` 参考对象，因为它为你在 cookies 上层增加了安全性。

读取 cookies::

    from flask import request

    @app.route('/')
    def index():
        username = request.cookies.get('username')
        # use cookies.get(key) instead of cookies[key] to not get a
        # KeyError if the cookie is missing.

存储 cookies::

    from flask import make_response

    @app.route('/')
    def index():
        resp = make_response(render_template(...))
        resp.set_cookie('username', 'the username')
        return resp

注意 cookies 都是设置在响应对象上的。所以你正常只需要让视图函数返回字符串即可，
Flask 会为你把字符串转换成响应对象。如果你想明确地实现响应对象的话，
你可以使用 :meth:`~flask.make_response` 方法函数后再修改响应对象。

有时候你也许想要在没有响应对象的位置上设置一个 cookie 的话，
通过使用 :ref:`deferred-callbacks` 模式也许能做到。

对于这种模式也要查看 :ref:`about-responses` 参考文档。

重定向和错误
--------------------

要把一个用户重定向到另一个端点上，使用 :func:`~flask.redirect` 函数；
要使用一个错误代号提前终止一个请求，使用 :func:`~flask.abort` 函数::

    from flask import abort, redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        abort(401)
        this_is_never_executed()

这个例子没有什么生产价值，因为一名用户会从主页位置重定向到一个无权访问的页面
（401 错误代号的意思是拒绝访问），但足够说明是如何工作的。

对于每个 HTTP 错误代号都是默认显示一个黑白页面。如果你想要自定义错误页面的话，
你可以使用 :meth:`~flask.Flask.errorhandler` 装饰器实现::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

注意 ``404`` 写在 :func:`~flask.render_template` 函数调用之后。
这是告诉 Flask 该页面的状态代号应该是 404 意思是无法找到访问的页面。
默认的 200 代号是假设一切都正常的意思。

查看 :ref:`error-handlers` 参考文档了解更多细节。

.. _about-responses:

关于响应
---------------

从一个视图函数返回的值是自动地为你转换成一个响应对象。如果返回值是一个字符串的话，
字符串会转化成一种字符串作为响应主体的响应对象，一个 ``200 OK`` 状态代号和
一个 :mimetype:`text/html` 互联网媒体类型。Flask 作用在转换过程
的逻辑，把值返回给响应对象，情况如下：

1.  如果返回的是正确类型的一个响应对象的话，它就是直接从视图函数返回的。
2.  如果是一个字符串的话，所建立的一个响应对象含有这个字符串数据和默认参数。
3.  如果返回的是一个元组的话，元组中的元素可以提供额外的信息。那么元组形式
    要是 ``(response, status, headers)`` 或 ``(response, headers)`` 
    其中一种。 ``status`` 值会覆写状态代号，并且 ``headers`` 可以是
    额外头部值的一种列表或字典形式。
4.  如果以上都不是的话，Flask 会假设返回值是一个合法的 WSGI 应用，
    并且把 WSGI 应用转换成一个响应对象。

如果你想在视图函数中控制响应对象结果的话，你可以使用 :func:`~flask.make_response` 函数。

想象一下你此时有一个像下面一样的视图函数::

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

你只需要把返回语句表达式部分用 :func:`~flask.make_response` 打包起来，
然后就得到一个响应对象可以修改它，接着返回修改后的响应对象::

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp

.. _sessions:

会话
--------

另外请求对象也有第二个对象名叫 :class:`~flask.session` 类，它让你存储
从一个请求到下一个请求用户的信息。这个类为你部署在 cookies 的顶层然后对
 cookies 进行加密签名。意思就是用户可以查看你的 cookie 内容却无法修改内容，
除非知道签名时使用的密钥。

要使用会话你就需要设置一个密钥。如下就是会话如何工作的示例::

    from flask import Flask, session, redirect, url_for, escape, request

    app = Flask(__name__)

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    @app.route('/')
    def index():
        if 'username' in session:
            return 'Logged in as %s' % escape(session['username'])
        return 'You are not logged in'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return '''
            <form method="post">
                <p><input type=text name=username>
                <p><input type=submit value=Login>
            </form>
        '''

    @app.route('/logout')
    def logout():
        # remove the username from the session if it's there
        session.pop('username', None)
        return redirect(url_for('index'))

这里要注意 :func:`~flask.escape` 函数，如果你没有使用模版引擎的话（如同本例中一样），
该函数会为你执行转义功能。

.. admonition:: 如何生成良好的密钥

    一个密钥应该尽可能是随机结果。你的操作系统有非常好的随机数据生成机制，
    依据一种加密的随机生成器来实现。使用如下命令可以快速为你生成一个随机值 
    :attr:`Flask.secret_key` 属性（或 :data:`SECRET_KEY` 数据）::

        $ python -c 'import os; print(os.urandom(16))'
        b'_5#y2L"F4Q8z\n\xec]/'

在基于 cookie 的会话上有一点要注意：Flask 会得到你放到会话对象中的值，然后把
值序列化到一个 cookie 中。如果你正在寻找一些值的时候，不要通过请求对象来存储，
cookies 都是启用的，并且你们都得不到一个清晰的错误消息，检查你的页面响应中的
 cookie 大小，与浏览器保存的大小进行比较。

另外对于默认客户端方的会话，如果你想要在服务器端来处理客户端会话，
有许多 Flask 扩展件支持这项任务。

消息闪存
----------------

好的网络应用和良好的用户接口都有关乎反馈的功能。如果用户得不到足够的反馈，
用户都会恨恶那些具有隐含性质的网络应用。Flask 提供了真正直接的方式把反馈
提供给用户，使用的就是闪存系统。闪存系统基本上在一个请求结束时，让记录一条消息
变成可能，并且在下一个请求（且只在下一个请求）上可以获得上一条消息。
这项技术常常与一个图层模版组合使用来曝光消息。

要闪存一条消息使用 :func:`~flask.flash` 函数，要得到消息你可以使用
 :func:`~flask.get_flashed_messages` 函数并且也可以用在模版中。
对于一个完整的示例查看 :ref:`message-flashing-pattern` 参考文档。

日志
-------

.. versionadded:: 0.3

有时候你也许身处一种情况中，你要处理的数据应该是正确的，但实际上却相反。
例如你也许有一些客户端代码，发送一个 HTTP 请求给服务器，但显然发送的数据被玷污了。
这也许是因为一名用户篡改了数据，或者客户端代码执行失败。大多数时候在这种情形里用
 ``400 Bad Request`` 作为回复是可以的，但有时候无法实现，并且客户端代码依然正在执行。

你也许想通过日志来记录那些腥臭的行为。这就是日志器登场的时候了。
从 Flask 0.3 开始，一个日志器预先配置完供你使用。

如下是一些日志调用的例子::

    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')

已经增加的 :attr:`~flask.Flask.logger` 属性是一项标准日志 :class:`~logging.Logger` 类，
所以回顾官方 `logging documentation <https://docs.python.org/library/logging.html>`_ 
文档了解更多信息。

再阅读 :ref:`application-errors` 参考文档也有益处。

在 WSGI 中间件里的钩子处理
---------------------------

如果你想要增加一个 WSGI 中间件到你的网络应用中，你可以打包内部的 WSGI 应用。
例如，如果你想使用 Werkzeug 包中的一个中间件的话，在 lighttpd 中围绕着 bugs 工作，
你可以像下面这样来实现::

    from werkzeug.contrib.fixers import LighttpdCGIRootFix
    app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)

使用 Flask 扩展件
----------------------

扩展件都是帮助你完成共性任务的包。例如， Flask-SQLAlchemy 提供了 SQLAlchemy 数据库支持，
它让 Flask 与数据库操作变得容易简单。

更多的 Flask 扩展件，查看 :ref:`extensions` 参考文档。

部署到一台网络服务器上
-------------------------

想把你的新 Flask 网络应用部署到网络服务器上吗？直接阅读 :ref:`deployment` 参考文档。
