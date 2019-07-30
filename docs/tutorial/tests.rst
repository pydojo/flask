.. currentmodule:: flask

测试覆盖率
=============

为你的网络应用书写单元测试意义很大，让你能够检查你所写的代码是否如期而至。
Flask 提供了一个测试客户端，用来模拟发送请求到网络应用后返回响应对象数据。

你有责任尽可能多地去测试你的代码。当函数被调用的时候，函数中的代码才会运行，
并且可以进入代码分支中，例如，当条件表达式部分成立时才会运行 ``if`` 语句块。
你想要确保每个函数都经过测试，那就要覆盖每个分支中的所含数据。

这样才能够更接近 100% 的覆盖率，更让人舒服的是，你可以改变代码且不用担心行为
上的变化。不管如何做到的，100% 的覆盖率并不能保证你的网络应用没有 bugs 。
尤其是覆盖率测试不能够测试用户在浏览器中与网络应用是如何互动的。
尽管如此，在开发期间使用测试覆盖率就是一项重要的工具。

.. 注意::
    这个会在项目教程后面介绍到，但接下来在你的项目中你应该测试你的开发代码。

你要使用 `pytest`_ 和 `coverage`_ 来完成测试工作，并且测量你的代码。
这2个第三方库都要安装：

.. code-block:: none

    $ pip install pytest coverage

.. _pytest: https://pytest.readthedocs.io/
.. _coverage: https://coverage.readthedocs.io/


配置与固定设施
------------------

单元测试代码是放在 ``tests`` 目录中的。这个目录要与 ``flaskr`` 包在 *同级* 路径里，
而不要放到 ``flaskr`` 目录中。其中 ``tests/conftest.py`` 文件里包含了全部带有
*fixture* 的配置函数，固定设施函数都是每个测试用例要使用的。
测试用例都要放在以 ``test_`` 命名的 Python 模块中，
而且每个测试用例函数名也都要以 ``test_`` 作为前缀。

每个测试用例会建立一个新的、临时数据库文件后，生成一些单元测试中要用到的数据。
所以要写一个 SQL 文件来插入测试数据。

.. code-block:: sql
    :caption: ``tests/data.sql``

    INSERT INTO user (username, password)
    VALUES
      ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
      ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

    INSERT INTO post (title, body, author_id, created)
    VALUES
      ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

网络应用 ``app`` 固定设施会调用工厂函数后代入 ``test_config`` 来
配置网络应用和数据库，这都是单元测试用的配置，而不是本地开发配置。

.. code-block:: python
    :caption: ``tests/conftest.py``

    import os
    import tempfile

    import pytest
    from flaskr import create_app
    from flaskr.db import get_db, init_db

    with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
        _data_sql = f.read().decode('utf8')


    @pytest.fixture
    def app():
        db_fd, db_path = tempfile.mkstemp()

        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
        })

        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

        yield app

        os.close(db_fd)
        os.unlink(db_path)


    @pytest.fixture
    def client(app):
        return app.test_client()


    @pytest.fixture
    def runner(app):
        return app.test_cli_runner()

:func:`tempfile.mkstemp` 函数是建立并打开一个临时文件，
返回文件对象和文件路径。
配置项 ``DATABASE`` 路径值要经过覆写，这样才能指向这个临时文件路径，
从而不再指向 `instance` 实例文件夹了。
设置好临时路径后，数据库表都被建立并且测试数据也插入到数据库表中了。
一项测试完成后，关闭临时数据库再删除临时文件。

配置项 :data:`TESTING` 信号设置开启就告诉 Flask 此时建立的网络应用
运行在测试模式中。Flask 会改变一些内部行为让测试更加容易，并且其它扩展件
也可以使用旗语来让单元测试更容易。

固定设施函数 ``client`` 代入网络应用对象调用了
:meth:`app.test_client() <Flask.test_client>` 方法，
网络应用对象是由 ``app`` 固定设施建立的。单元测试会使用
客户端来制作 HTTP 请求到网络应用，所以不需要运行服务器了。

固定设施函数 ``runner`` 与 ``client`` 类似。
:meth:`app.test_cli_runner() <Flask.test_cli_runner>` 方法建立的
是一个运行器，这个运行器可以调用注册到网络应用的 Click 命令。

Pytest 使用的这些固定设施时，都是通过在测试用例函数中与固定设施名匹配的参数来实现。
例如，接下来你要写的 ``test_hello`` 测试用例函数会得到一个 ``client`` 参数。
Pytest 用 ``client`` 固定设施函数来与这个参数名来进行匹配，调用固定设施，
然后把固定设施返回的值代入到测试用例函数中。


测试工厂函数
-----------

对于工厂函数本身来说没有那么多的测试必要。大部分代码都会为每个测试用例而执行，
所以如果有什么失败的话，其它的测试用例也会注意到。

唯一可以改变的行为就是代入的测试配置。如果没有代入测试配置的话，
那么应该有一些默认的配置，否则配置就应该覆写配置项。

.. code-block:: python
    :caption: ``tests/test_factory.py``

    from flaskr import create_app


    def test_config():
        assert not create_app().testing
        assert create_app({'TESTING': True}).testing


    def test_hello(client):
        response = client.get('/hello')
        assert response.data == 'Hello, World!'.encode('utf-8')

你增加的 ``hello`` 路线在写工厂函数测试时使用本项目教程中一开始的那个例子。
那么请求后的返回值 "Hello, World!" 就在响应对象中，所以测试响应对象中的数据
是否与之匹配。


测试数据库
------------

在一个网络应用语境中， ``get_db`` 函数应该每次调用时返回相同的数据库连接。
语境结束后，应该关闭数据库连接。

.. code-block:: python
    :caption: ``tests/test_db.py``

    import sqlite3

    import pytest
    from flaskr.db import get_db


    def test_get_close_db(app):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        with pytest.raises(sqlite3.ProgrammingError) as e:
            db.execute('SELECT 1')

        assert 'closed' in str(e.value)

对于 ``init-db`` 命令来说应该调用的是 ``init_db`` 函数后输出一个消息。

.. code-block:: python
    :caption: ``tests/test_db.py``

    def test_init_db_command(runner, monkeypatch):
        class Recorder(object):
            called = False

        def fake_init_db():
            Recorder.called = True

        monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output
        assert Recorder.called

这种测试命令行命令的测试用例中使用了 Pytest 的 ``monkeypatch`` 固定设施来代替
``init_db`` 函数，使用了一种替身测试方法，含带被调用时的记录信息。
上面你写的 ``runner`` 固定设施是根据命令行中命令的名字来调用 ``init-db`` 命令的。


测试授权
--------------

对于大多数视图函数，需要一名已经登录的用户来进行单元测试。
在这种授权约束下的测试中，最简单的方法就是使用客户端固定设施
发出一个 ``POST`` 请求给 ``login`` 视图函数。
这要比每次都自己写发送请求更好，你可以写一个类让其方法来去做这些事，
然后使用一个固定设施把方法代入到客户端来进行每次的测试。

.. code-block:: python
    :caption: ``tests/conftest.py``

    class AuthActions(object):
        def __init__(self, client):
            self._client = client

        def login(self, username='test', password='test'):
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')


    @pytest.fixture
    def auth(client):
        return AuthActions(client)

使用 ``auth`` 固定设施，你可以在单元测试中调用 ``auth.login()`` 视图函数以
测试用户 ``test`` 进行登录操作，测试用户会插入到 ``app`` 固定设施中的测试数据中。

对于 ``register`` 视图函数来说，应该成功地在 ``GET`` 请求方法上翻译模版。
在 ``POST`` 请求方法上成功验证表单数据，然后成功地重定向到登录 URL 页面上，
然后用户的数据都应该存储在数据库中。非法数据出现时应该显示错误消息。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    import pytest
    from flask import g, session
    from flaskr.db import get_db


    def test_register(client, app):
        assert client.get('/auth/register').status_code == 200
        response = client.post(
            '/auth/register', data={'username': 'a', 'password': 'a'}
        )
        assert 'http://localhost/auth/login' == response.headers['Location']

        with app.app_context():
            assert get_db().execute(
                "select * from user where username = 'a'",
            ).fetchone() is not None


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', 'Username is required.'.encode('utf8')),
        ('a', '', 'Password is required.'.encode('utf8')),
        ('test', 'test', 'already registered'.encode('utf8')),
    ))
    def test_register_validate_input(client, username, password, message):
        response = client.post(
            '/auth/register',
            data={'username': username, 'password': password}
        )
        assert message in response.data

:meth:`client.get() <werkzeug.test.Client.get>` 方法制作了一个 ``GET`` 请求后
返回有 Flask 返回的一个 :class:`Response` 类实例对象。同样
:meth:`client.post() <werkzeug.test.Client.post>` 方法制作了一个 ``POST`` 请求后，
把 ``data`` 参数的字典数据转换成表单数据。

要测试成功翻译页面，直接制作一个请求后检查返回状态代号 ``200 OK`` 
:attr:`~Response.status_code` 属性值即可。如果翻译失败的话，
Flask 会返回一个 ``500 Internal Server Error`` 类型的代号。

:attr:`~Response.headers` 属性会有一个 ``Location`` 头部信息，这是在
登录地址的注册视图函数重定向到登录视图函数时含有的信息。

:attr:`~Response.data` 属性含有字节类型的响应主体内容。如果
你期望某个值翻译到页面上的话，检查是否存在在 ``data`` 属性中即可。
字节都必须与字节进行比较，所以要使用 `encode()` 字符串方法。
如果你想要比较 Unicode 文本内容的话，使用
:meth:`get_data(as_text=True) <werkzeug.wrappers.BaseResponse.get_data>` 方法
代替 ``data`` 属性。

``pytest.mark.parametrize`` 装饰器告诉 Pytest 要用不同的参数值来
运行同一个测试用例函数。这里用装饰器就是要测试不同的非法输入值和错误消息，
而且不用写三遍同样的代码了。

对于 ``login`` 视图函数的测试，与 ``register`` 视图函数都是非常相似的。
这要比在数据库中进行测试要好许多，
:data:`session` 数据代理对象应该在登录后设置 ``user_id`` 这一项。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_login(client, auth):
        assert client.get('/auth/login').status_code == 200
        response = auth.login()
        assert response.headers['Location'] == 'http://localhost/'

        with client:
            client.get('/')
            assert session['user_id'] == 1
            assert g.user['username'] == 'test'


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
    ))
    def test_login_validate_input(auth, username, password, message):
        response = auth.login(username, password)
        assert message in response.data

在一个 ``with`` 语句中使用 ``client`` 会允许访问语境中的变量，
例如， :data:`session` 数据代理对象是在响应返回之后可以访问的。
正常情况下，在一个请求之外访问 ``session`` 这个语境中的变量时，
会抛出一个例外错误类型。

测试登出 ``logout`` 视图函数正好与 ``login`` 视图函数相反。
:data:`session` 语境中的变量应该登出后不再含有 ``user_id`` 数据。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_logout(client, auth):
        auth.login()

        with client:
            auth.logout()
            assert 'user_id' not in session


测试博客蓝图
---------------

所有的博客蓝图视图函数都是使用前面 ``auth`` 用的固定设施。
调用 ``auth.login()`` 以及来自客户端的子序请求都是以
 ``test`` 用户登录的。

对于 ``index`` 视图函数来说应该显示关于发布的信息，
这个发布的内容是测试数据中加入的内容。当以作者身份登录时，
就应该有一个编辑发布内容的超链接。

在测试 ``index`` 视图函数时，你也可以测试更多的授权行为。
当没有登录时，每个页面上会显示登录和注册的超链接。
当登录时，就只有一个登出的超链接。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    import pytest
    from flaskr.db import get_db


    def test_index(client, auth):
        response = client.get('/')
        assert b"Log In" in response.data
        assert b"Register" in response.data

        auth.login()
        response = client.get('/')
        assert b'Log Out' in response.data
        assert b'test title' in response.data
        assert b'by test on 2018-01-01' in response.data
        assert b'test\nbody' in response.data
        assert b'href="/1/update"' in response.data

必须登录一名用户才能够访问 ``create``、 ``update`` 和
``delete`` 视图函数。而登录的用户必须是发布内容的作者时，
才能够访问 ``update`` 和 ``delete`` 视图函数，否则会
返回一个 ``403 Forbidden`` 状态代号。
如果一个 ``post`` 所含的已知 ``id`` 不存在的话，
那么 ``update`` 和 ``delete`` 视图函数应返回
 ``404 Not Found`` 状态代号。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
        '/1/delete',
    ))
    def test_login_required(client, path):
        response = client.post(path)
        assert response.headers['Location'] == 'http://localhost/auth/login'


    def test_author_required(app, client, auth):
        # change the post author to another user
        with app.app_context():
            db = get_db()
            db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
            db.commit()

        auth.login()
        # current user can't modify other user's post
        assert client.post('/1/update').status_code == 403
        assert client.post('/1/delete').status_code == 403
        # current user doesn't see edit link
        assert b'href="/1/update"' not in client.get('/').data


    @pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
    ))
    def test_exists_required(client, auth, path):
        auth.login()
        assert client.post(path).status_code == 404

对于 ``create`` 和 ``update`` 视图函数来说应该翻译并返回
一个 ``200 OK`` 状态代号给一个 ``GET`` HTTP 请求。当合法
数据以一个 ``POST`` 请求发送的时候， ``create`` 视图函数
应该插入新当发布数据到数据库中，然后 ``update`` 视图函数应该
修改已有的数据。使用非法数据时，这两个页面应该显示一个错误消息。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_create(client, auth, app):
        auth.login()
        assert client.get('/create').status_code == 200
        client.post('/create', data={'title': 'created', 'body': ''})

        with app.app_context():
            db = get_db()
            count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
            assert count == 2


    def test_update(client, auth, app):
        auth.login()
        assert client.get('/1/update').status_code == 200
        client.post('/1/update', data={'title': 'updated', 'body': ''})

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post['title'] == 'updated'


    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
    ))
    def test_create_update_validate(client, auth, path):
        auth.login()
        response = client.post(path, data={'title': '', 'body': ''})
        assert b'Title is required.' in response.data

对于 ``delete`` 视图函数应该重定向到主页 URL 地址上，
并且发布的内容应该从数据库中删除掉。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_delete(client, auth, app):
        auth.login()
        response = client.post('/1/delete')
        assert response.headers['Location'] == 'http://localhost/'

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post is None


跑测试
-----------------

一些额外的配置是不需要的，但要运行覆盖率的话需要一点配置。
覆盖率测试配置要增加到项目的 ``setup.cfg`` 文件中，
该配置文件要与 `tests` 目录在同一个路径下。

.. code-block:: none
    :caption: ``setup.cfg``

    [tool:pytest]
    testpaths = tests

    [coverage:run]
    branch = True
    source = flaskr

要运行这些测试，使用 ``pytest`` 命令即可。它会发现并运行
所有已经写过的测试用例函数。

.. code-block:: none

    $ pytest

    ========================= test session starts ==========================
    platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
    rootdir: /home/user/Projects/flask-tutorial, inifile: setup.cfg
    collected 23 items

    tests/test_auth.py ........                                      [ 34%]
    tests/test_blog.py ............                                  [ 86%]
    tests/test_db.py ..                                              [ 95%]
    tests/test_factory.py ..                                         [100%]

    ====================== 24 passed in 0.64 seconds =======================

如果有任何一个测试失败的话， pytest 会显示产生的错误信息。
你可以运行 ``pytest -v`` 命令来得到详细的测试报告内容。

要确保覆盖率的测试结果输出出来的话，使用 ``coverage`` 命令
来运行 pytest 运行器，而不是直接执行 `pytest` 命令。

.. code-block:: none

    $ coverage run -m pytest

这样运行的单元测试结果会由 `coverage` 收集到，
在终端里要显示覆盖率报告结果只需要运行如下命令即可：

.. code-block:: none

    $ coverage report

    Name                 Stmts   Miss Branch BrPart  Cover
    ------------------------------------------------------
    flaskr/__init__.py      21      0      2      0   100%
    flaskr/auth.py          54      0     22      0   100%
    flaskr/blog.py          54      0     16      0   100%
    flaskr/db.py            24      0      4      0   100%
    ------------------------------------------------------
    TOTAL                  153      0     44      0   100%

要生成一份 HTML 报告形式会让你看到每个文件中哪些行代码都经过了测试，
运行如下命令生产 HTML 报告内容：

.. code-block:: none

    $ coverage html

生成的报告保存在项目目录中的一个名叫 ``htmlcov`` 文件夹里。
在浏览器中打开 ``htmlcov/index.html`` 文件就可以看到完整报告了。

继续阅读 :doc:`deploy` 文档内容。
