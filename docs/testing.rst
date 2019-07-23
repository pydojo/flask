.. _testing:

测试 Flask 网络应用
==========================

   **有些事情未经测试就会破裂。**

这句引用的话不知是谁说的，而且并不是完全正确，更不属于真理。
未测试的网络应用只是在改善现有代码上会有困难，而且开发者们
不测试网络应用越来越多地呈现出一种妄想症。
如果一个网络应用完成了自动化测试，你可以安全地去做变更，
并且如果任何一个断裂出现都会立即知道。

Flask 提供了一种方法来测试你的网络应用，通过揭露 Werkzeug 测试
 :class:`~werkzeug.test.Client` 类和为你处理本地语境。
你可以稍后使用你喜欢的测试解决方案。

在本文档中我们会使用 `pytest`_ 单元测试库作为基础测试框架。
你可以用 ``pip`` 来安装它，就像下面这样::

    $ pip install pytest

.. _pytest:
   https://pytest.org

网络应用
---------------

首先，我们需要一个网络应用来做测试；
我们会使用来自 :ref:`tutorial` 教程中的网络应用作为示例。
如果你还没有那个网络应用的话，从 :gh:`the examples <examples/tutorial>`
来获得源代码。

测试骨架
--------------------

我们通过增加一个测试目录作为开始，要在网络应用根路径上增加测试目录。
然后，建立一个 Python 文件来存储我们的测试 (:file:`test_flaskr.py`)。
当我们的测试模块文件名是如下格式 ``test_*.py`` 的时候，
pytest 会自动发现测试模块。

接下来，我们建立一个 `pytest fixture`_ 固定设施名叫
:func:`client` 函数，它为测试对网络应用进行配置，以及
初始化一个新的数据库::

    import os
    import tempfile

    import pytest

    from flaskr import flaskr


    @pytest.fixture
    def client():
        db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        client = flaskr.app.test_client()

        with flaskr.app.app_context():
            flaskr.init_db()

        yield client

        os.close(db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

这个客户端固定设施会被每个独立测试来调用。它给了我们一个直接访问网络应用的接口，
其中我们可以触发到网络应用的测试请求。客户端固定设施也会为我们保留 cookies 的踪迹。

在配置过程中， ``TESTING`` 配置旗语要被激活。该旗语所做的就是在请求处理期间
禁用错误捕获，这样当执行对网络应用的测试请求时，你会得到更好的错误报告。

因为 SQLite3 是基于文件系统的数据库，我们可以容易使用 :mod:`tempfile` 模块来
建立一个临时数据库后初始化数据库。 :func:`~tempfile.mkstemp` 函数为我们做了
两件事：函数返回一个低层文件处理，和一个随机文件名。
随机文件名是我们用做数据库的名字。我们只要保存到 `db_fd` 变量中我们就可以使用
 :func:`os.close` 函数来关闭这个随机文件名文件。

要在测试后删除数据库，固定设施来关闭文件并从文件系统中删除该随机文件名文件。

如果我们现在运行测试套件的话，我们应该看到如下输出内容::

    $ pytest

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 0 items

    =========== no tests ran in 0.07 seconds ============

虽然没有运行任何实际的测试，但我们已经知道我们的 ``flaskr`` 网络应用
在句法上是合法的，否则导入时会伴随着一个例外中断测试运行器。

.. _pytest fixture:
   https://docs.pytest.org/en/latest/fixture.html

第一个测试
--------------

现在是时候启动网络应用的功能性测试了。
如果我们访问网络应用的根路径 (``/``) 的话，
让我们检查网络应用应该显示一句 "No entries here so far" 内容。
要实现这个测试，我们把一个新的测试函数增加到
 :file:`test_flaskr.py` 文件中，就像下面一样::

    def test_empty_db(client):
        """Start with a blank database."""

        rv = client.get('/')
        assert b'No entries here so far' in rv.data

注意我们的测试函数名都要以 `test_` 作为前缀；这样才允许
`pytest`_ 自动把一个函数是识别成测试用例来运行测试。

通过使用 ``client.get`` 我们可以发送一个 HTTP ``GET`` 请求给网络应用，
参数值是网络应用的路径。
返回值会是一个 :class:`~flask.Flask.response_class` 类对象。
我们现在可以使用 :attr:`~werkzeug.wrappers.BaseResponse.data` 属性来检查
来自网络应用的返回值（字符串内容）。在此处情况中，我们确保
``'No entries here so far'`` 是网络应用输出结果部分。

再次执行测试后你应该看到有一项测试用例通过测试了::

    $ pytest -v

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 1 items

    tests/test_flaskr.py::test_empty_db PASSED

    ============= 1 passed in 0.10 seconds ==============

登录和登出测试
------------------

我们的网络应用主要功能只是一个给管理员用户使用的，所以我们需要一种方法来
记录测试客户端进出网络应用。要实现这项测试，我们要雇佣一些请求发送给
登录和登出页面，还要带着所需要的表单数据（用户名和密码）。
并且由于登录和登出页面有重定向功能，我们要告诉测试客户端跟上重定向，
需要用到 `follow_redirects` 参数。

把如下2个函数增加到你的 :file:`test_flaskr.py` 文件中::

    def login(client, username, password):
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)


    def logout(client):
        return client.get('/logout', follow_redirects=True)

现在我们可以容易测试登录和登出效果，并且用非法证书让其出现失败现象。
增加新的测试函数::

    def test_login_logout(client):
        """Make sure login and logout works."""

        rv = login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
        assert b'You were logged in' in rv.data

        rv = logout(client)
        assert b'You were logged out' in rv.data

        rv = login(client, flaskr.app.config['USERNAME'] + 'x', flaskr.app.config['PASSWORD'])
        assert b'Invalid username' in rv.data

        rv = login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'] + 'x')
        assert b'Invalid password' in rv.data

测试增加消息功能
--------------------

我们也应该测试增加消息的效果。增加一个新的测试函数，如下一样::

    def test_messages(client):
        """Test that messages work."""

        login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
        rv = client.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

这里我们检查了 HTML 允许用在文本中，而不是用在标题里，
评估部分就是其应该有的行为。

运行测试现在应该给我们显示三项测试用例通过的报告结果::

    $ pytest -v

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 3 items

    tests/test_flaskr.py::test_empty_db PASSED
    tests/test_flaskr.py::test_login_logout PASSED
    tests/test_flaskr.py::test_messages PASSED

    ============= 3 passed in 0.23 seconds ==============


其它测试技巧
--------------------

除了上面展示的使用测试客户端方法，这里也有测试请求语境
:meth:`~flask.Flask.test_request_context` 方法，
它可以与 ``with`` 语句组合使用来临时激活一个请求语境。
使用这种方法你可以访问 :class:`~flask.request` 类、
:class:`~flask.g` 类和 :class:`~flask.session` 
类对象，就像在视图函数中使用一样。
下面是一个完整的示范此方法的示例::

    import flask

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        assert flask.request.path == '/'
        assert flask.request.args['name'] == 'Peter'

所有其它与语境绑定的对象都是一样的用法。

如果你想要用不同的配置来测试你的网络应用，
那显然这里的方法看起来就不是一种好的方法，
考虑切换成网络应用工厂模式（参考 :ref:`app-factories` 文档内容）。

注意，不管如何做到的，如果你正在使用一个测试请求语境的话，
:meth:`~flask.Flask.before_request` 方法和
:meth:`~flask.Flask.after_request` 方法都不会
自动被调用。不管如何做到的，当测试请求语境在 ``with`` 语句块里时，
:meth:`~flask.Flask.teardown_request` 方法都会执行。
如果你想要 :meth:`~flask.Flask.before_request` 方法也被调用，
你需要自己调用 :meth:`~flask.Flask.preprocess_request` 方法::

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        app.preprocess_request()
        ...

要打开数据库连接需要自己调用这个方法，或者依据你的网络应用是
如何设计的执行类似操作。

如果你想要调用 :meth:`~flask.Flask.after_request` 方法，你
需要调用 :meth:`~flask.Flask.process_response` 方法，其中
不管如何做到的，需要你把一个响应对象代入到方法次方法中::

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        resp = Response('...')
        resp = app.process_response(resp)
        ...

通用中这是没什么用，因为在那个点上你可以直接使用测试客户端开始测试。

.. _faking-resources:

仿造资源和语境
----------------------------

.. versionadded:: 0.10

一个非常共性的模式就是在网络应用语境上存储用户授权信息和数据库连接，
或者在 :attr:`flask.g` 对象上存储。
对于这个来说的通用模式是把其中的对象放在第一次使用的地方，
然后在一个 teardown 中来删除。
想象此时的情景，如下代码得到当前用户::

    def get_user():
        user = getattr(g, 'user', None)
        if user is None:
            user = fetch_current_user_from_database()
            g.user = user
        return user

对于一项测试来说，从外面来覆写这个用户是好的，
因为没有被迫去改变一些代码。这种方式可以使用
钩子来实现 :data:`flask.appcontext_pushed` 数据代理对象信号::

    from contextlib import contextmanager
    from flask import appcontext_pushed, g

    @contextmanager
    def user_set(app, user):
        def handler(sender, **kwargs):
            g.user = user
        with appcontext_pushed.connected_to(handler, app):
            yield

然后使用这个语境管理器对象::

    from flask import json, jsonify

    @app.route('/users/me')
    def users_me():
        return jsonify(username=g.user.username)

    with user_set(app, my_user):
        with app.test_client() as c:
            resp = c.get('/users/me')
            data = json.loads(resp.data)
            self.assert_equal(data['username'], my_user.username)


保留语境
--------------------------

.. versionadded:: 0.4

有时候触发一个正规的请求是有帮助的，但依然要保留语境稍长一点时间，
这样额外的反省就可以出现。从 Flask 0.4 开始这是可能的事情，
通过使用 :meth:`~flask.Flask.test_client` 方法与一个 ``with`` 语句组合使用::

    app = flask.Flask(__name__)

    with app.test_client() as c:
        rv = c.get('/?tequila=42')
        assert request.args['tequila'] == '42'

如果你曾经只使用 :meth:`~flask.Flask.test_client` 方法，
不带 ``with`` 语句的话， ``assert`` 语句会带着一个错误失败，
因为 `request` 不再可用了（因为你正在实际请求之外要使用请求）。


访问和修改会话
--------------------------------

.. versionadded:: 0.8

有时候从测试客户端访问或修改会话是非常有帮助的。
通用中有2个方法来做这件事。
如果你只想要确保一个会话具有某种键值对儿设置的话，
你可以只保留语境后访问 :data:`flask.session` 数据代理对象::

    with app.test_client() as c:
        rv = c.get('/')
        assert flask.session['foo'] == 42

不管如何做到的，这种方法是不能修改会话或在雇佣一个请求之前访问会话的。
从 Flask 0.8 开始，我们提供了一个名叫 *会话交易* 的概念，
它模拟了合适的调用在测试客户端语境中打开一个会话和修改一个会话。
在交易结束时会话存储了下来。这项工作是独立于后端使用的会话::

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['a_key'] = 'a value'

        # once this is reached the session was stored

注意，在这种情况中，你不得不使用 ``sess`` 对象来代替
:data:`flask.session` 数据代理对象。不管如何做到的，
替身对象会提供相同的接口。


测试 JSON APIs
-----------------

.. versionadded:: 1.0

Flask 很支持 JSON 并且对于建立 JSON APIs 来说都是采用此种数据结构。
使用 JSON 数据制作请求后检验响应中的 JSON 数据是非常方便的::

    from flask import request, jsonify

    @app.route('/api/auth')
    def auth():
        json_data = request.get_json()
        email = json_data['email']
        password = json_data['password']
        return jsonify(token=generate_token(email, password))

    with app.test_client() as c:
        rv = c.post('/api/auth', json={
            'email': 'flask@example.com', 'password': 'secret'
        })
        json_data = rv.get_json()
        assert verify_token(email, json_data['token'])

把 ``json`` 参数代入到测试客户端众多方法中，就把请求数据设置成
序列化后的 JSON 对象，并且把内容类型设置成 ``application/json`` 形式。
你可以在请求或响应对象上使用 ``get_json`` 方法来获得 JSON 数据。


.. _testing-cli:

测试命令行命令
--------------------

Click 含带着 `utilities for testing`_ 工具来测试你的命令行命令。
:class:`~click.testing.CliRunner` 类单独运行命令后捕获
:class:`~click.testing.Result` 对象中的输出结果。

Flask 提供了 :meth:`~flask.Flask.test_cli_runner` 方法来建立一个
:class:`~flask.testing.FlaskCliRunner` 类，该类把 Flask 网络应用
自动代入到命令行中。使用该类的 :meth:`~flask.testing.FlaskCliRunner.invoke`
方法来调用同样的命令，这些命令会在命令行中被调用::

    import click

    @app.cli.command('hello')
    @click.option('--name', default='World')
    def hello_command(name)
        click.echo(f'Hello, {name}!')

    def test_hello():
        runner = app.test_cli_runner()

        # invoke the command directly
        result = runner.invoke(hello_command, ['--name', 'Flask'])
        assert 'Hello, Flask' in result.output

        # or by name
        result = runner.invoke(args=['hello'])
        assert 'World' in result.output

上面的示例中，通过名字来引入命令是有用的，因为它验证正确注册到网络应用的命令。

如果你想要测试你的命令如何进行语法分析参数的话，
不需要运行命令，使用自身的 :meth:`~click.BaseCommand.make_context` 方法即可。
对于测试多层化验证规则和自定义类型来说这是有用的::

    def upper(ctx, param, value):
        if value is not None:
            return value.upper()

    @app.cli.command('hello')
    @click.option('--name', default='World', callback=upper)
    def hello_command(name)
        click.echo(f'Hello, {name}!')

    def test_hello_params():
        context = hello_command.make_context('hello', ['--name', 'flask'])
        assert context.params['name'] == 'FLASK'

.. _click: http://click.pocoo.org/
.. _utilities for testing: http://click.pocoo.org/testing
