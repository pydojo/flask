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

To redirect a user to another endpoint, use the :func:`~flask.redirect`
function; to abort a request early with an error code, use the
:func:`~flask.abort` function::

    from flask import abort, redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        abort(401)
        this_is_never_executed()

This is a rather pointless example because a user will be redirected from
the index to a page they cannot access (401 means access denied) but it
shows how that works.

By default a black and white error page is shown for each error code.  If
you want to customize the error page, you can use the
:meth:`~flask.Flask.errorhandler` decorator::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

Note the ``404`` after the :func:`~flask.render_template` call.  This
tells Flask that the status code of that page should be 404 which means
not found.  By default 200 is assumed which translates to: all went well.

See :ref:`error-handlers` for more details.

.. _about-responses:

About Responses
---------------

The return value from a view function is automatically converted into a
response object for you.  If the return value is a string it's converted
into a response object with the string as response body, a ``200 OK``
status code and a :mimetype:`text/html` mimetype.  The logic that Flask applies to
converting return values into response objects is as follows:

1.  If a response object of the correct type is returned it's directly
    returned from the view.
2.  If it's a string, a response object is created with that data and the
    default parameters.
3.  If a tuple is returned the items in the tuple can provide extra
    information.  Such tuples have to be in the form ``(response, status,
    headers)`` or ``(response, headers)`` where at least one item has
    to be in the tuple.  The ``status`` value will override the status code
    and ``headers`` can be a list or dictionary of additional header values.
4.  If none of that works, Flask will assume the return value is a
    valid WSGI application and convert that into a response object.

If you want to get hold of the resulting response object inside the view
you can use the :func:`~flask.make_response` function.

Imagine you have a view like this::

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

You just need to wrap the return expression with
:func:`~flask.make_response` and get the response object to modify it, then
return it::

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp

.. _sessions:

Sessions
--------

In addition to the request object there is also a second object called
:class:`~flask.session` which allows you to store information specific to a
user from one request to the next.  This is implemented on top of cookies
for you and signs the cookies cryptographically.  What this means is that
the user could look at the contents of your cookie but not modify it,
unless they know the secret key used for signing.

In order to use sessions you have to set a secret key.  Here is how
sessions work::

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

The :func:`~flask.escape` mentioned here does escaping for you if you are
not using the template engine (as in this example).

.. admonition:: How to generate good secret keys

    A secret key should be as random as possible. Your operating system has
    ways to generate pretty random data based on a cryptographic random
    generator. Use the following command to quickly generate a value for
    :attr:`Flask.secret_key` (or :data:`SECRET_KEY`)::

        $ python -c 'import os; print(os.urandom(16))'
        b'_5#y2L"F4Q8z\n\xec]/'

A note on cookie-based sessions: Flask will take the values you put into the
session object and serialize them into a cookie.  If you are finding some
values do not persist across requests, cookies are indeed enabled, and you are
not getting a clear error message, check the size of the cookie in your page
responses compared to the size supported by web browsers.

Besides the default client-side based sessions, if you want to handle
sessions on the server-side instead, there are several
Flask extensions that support this.

Message Flashing
----------------

Good applications and user interfaces are all about feedback.  If the user
does not get enough feedback they will probably end up hating the
application.  Flask provides a really simple way to give feedback to a
user with the flashing system.  The flashing system basically makes it
possible to record a message at the end of a request and access it on the next
(and only the next) request.  This is usually combined with a layout
template to expose the message.

To flash a message use the :func:`~flask.flash` method, to get hold of the
messages you can use :func:`~flask.get_flashed_messages` which is also
available in the templates.  Check out the :ref:`message-flashing-pattern`
for a full example.

Logging
-------

.. versionadded:: 0.3

Sometimes you might be in a situation where you deal with data that
should be correct, but actually is not.  For example you may have some client-side
code that sends an HTTP request to the server but it's obviously
malformed.  This might be caused by a user tampering with the data, or the
client code failing.  Most of the time it's okay to reply with ``400 Bad
Request`` in that situation, but sometimes that won't do and the code has
to continue working.

You may still want to log that something fishy happened.  This is where
loggers come in handy.  As of Flask 0.3 a logger is preconfigured for you
to use.

Here are some example log calls::

    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')

The attached :attr:`~flask.Flask.logger` is a standard logging
:class:`~logging.Logger`, so head over to the official `logging
documentation <https://docs.python.org/library/logging.html>`_ for more
information.

Read more on :ref:`application-errors`.

Hooking in WSGI Middlewares
---------------------------

If you want to add a WSGI middleware to your application you can wrap the
internal WSGI application.  For example if you want to use one of the
middlewares from the Werkzeug package to work around bugs in lighttpd, you
can do it like this::

    from werkzeug.contrib.fixers import LighttpdCGIRootFix
    app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)

Using Flask Extensions
----------------------

Extensions are packages that help you accomplish common tasks. For
example, Flask-SQLAlchemy provides SQLAlchemy support that makes it simple
and easy to use with Flask.

For more on Flask extensions, have a look at :ref:`extensions`.

Deploying to a Web Server
-------------------------

Ready to deploy your new Flask app? Go to :ref:`deployment`.
