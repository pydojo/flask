.. currentmodule:: flask

蓝图与视图
====================

一个视图函数就是你要写的代码，要写成对所有抵达网络应用的请求作出响应的函数。
Flask 使用了许多模式来把进入的请求 URL 地址匹配到一个视图函数来处理 HTTP 请求。
视图函数返回的数据都会由 Flask 负责转换成一个出去的响应对象。
Flask 也可以在其它地方根据视图函数的名字和参数生成一个 URL 地址给视图函数。


建立一张蓝图
------------------

对于 :class:`Blueprint` 类来说，是一种组织代码的方法，它把与视图函数有关的代码
和视图函数无关的代码打包在一起。这要比直接注册视图函数和用网络应用直接注册其它代码
要更好，因为用一张视图就可以把不同的代码注册在一起。然后再用网络应用来注册蓝图，
注册蓝图是在工厂函数中当蓝图可用时进行的。

Flaskr 项目会有2张蓝图：
1. 其中一张蓝图包含那些授权有关的函数。
2. 另一张蓝图是包含博客发表内容有关的函数。
每张蓝图中的代码都分解到了各自的模块文件中。
因为博客需要知道关于授权的信息，所以你会先写授权那张蓝图。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    import functools

    from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
    )
    from werkzeug.security import check_password_hash, generate_password_hash

    from flaskr.db import get_db

    bp = Blueprint('auth', __name__, url_prefix='/auth')

这里第一个参数值是用 :class:`Blueprint` 类建立了一张名叫 ``'auth'`` 的蓝图。
像网络应用对象一样，蓝图需要知道自己定义在什么地方，所以把 ``__name__``
代入成第二个参数值。第三个参数 ``url_prefix`` 会把所有与这张蓝图有关的 URLs 地址
前面加上一个 ``'/auth'`` 前缀。

我们写完蓝图后，需要在工厂函数里导入蓝图并使用
:meth:`app.register_blueprint() <Flask.register_blueprint>` 方法
来把蓝图注册到网络应用实例上。下面的代码就是在工厂函数里需要为这张蓝图增加的代码。

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import auth
        app.register_blueprint(auth.bp)

        return app

用户授权蓝图会具有注册新用户、用户登录和用户登出的三个视图函数。


第一个用户注册视图函数
------------------------

当用户访问 ``/auth/register`` URL 地址时，名叫 ``register`` 的视图函数
会返回一个 `HTML`_ 表单给用户来填写。当用户们提交这张表单时，视图函数会验证
用户的输入，并且有错误的话会再次在表单页面上显示一个错误消息，或者没有错误就
建立一名新用户后重定向到登录页面。

.. _HTML: https://developer.mozilla.org/docs/Web/HTML

对于此时的你只需要在蓝图中写这个视图函数的代码即可。
下一个文档会介绍如何写模版来生成 HTML 表单。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/register', methods=('GET', 'POST'))
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(username)

            if error is None:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
                return redirect(url_for('auth.login'))

            flash(error)

        return render_template('auth/register.html')

这个 ``register`` 视图函数都做了什么呢？

#.  :meth:`@bp.route <Blueprint.route>` 方法把 URL ``/register`` 地址与
    这个 ``register`` 视图函数关联起来。当 Flask 接收到一个
     ``/auth/register`` 地址的请求时，网络应用就会调用 ``register`` 视图函数
    然后使用视图函数返回的值作为响应对象。

#.  如果用户提交表单的话，
    :attr:`request.method <Request.method>` 属性值就会是 ``'POST'`` 字符串。
    在这种情况下，就开始进入验证用户在表单中填写的数据环节。

#.  :attr:`request.form <Request.form>` 属性就是一种具体的
    :class:`dict` 字典数据类型，字典把表单提交的内容保存成键值对儿。
    表单中 `input` 标签的 ``username`` 和 ``password`` 属性作为键，
    用户填写的内容作为值。

#.  验证 ``username`` 和 ``password`` 都不是空值。

#.  验证 ``username`` 还没有被注册过是通过检查查询数据库返回的结果来确定的。
    :meth:`db.execute <sqlite3.Connection.execute>` 方法得到一个 SQL 
    查询语句，查询语句后面的一个 ``?`` 问号是占位符，会被任何一个用户输入内容
    代替，用户的输入放在一维元组中。数据库会照顾好转义用户输入值的事情，所以
    你们不用担心 *SQL 注射攻击* 漏洞。

    :meth:`~sqlite3.Cursor.fetchone` 方法是从查询结果中返回一行数据。
    如果查询不到符合查询语句的结果的话，返回的是一个 ``None`` 值。后面会用到
    :meth:`~sqlite3.Cursor.fetchall` 方法，它是把所有结果返回成一个列表。

#.  如果验证成功的话，就把新用户数据插入到数据库表中。
    为了安全起见，用户密码永远不要直接存储在数据库中。
    而是要使用
    :func:`~werkzeug.security.generate_password_hash` 函数把密码
    安全地进行哈希化处理，然后把哈希化过的用户密码存储在数据库中。
    因此这种修改数据的查询语句，需要调用
    :meth:`db.commit() <sqlite3.Connection.commit>` 方法来保存有变化的数据。

#.  存储完注册用户之后，都会重定向到登录页面上。
    :func:`url_for` 函数是为名叫 `login` 的视图函数生成一个 URL 地址。
    这种生成 URL 地址的方法要比直接写 URL 地址更好，因为 `url_for` 函数
    允许你稍后更改 URL 地址且不需要改变连接到地址的所有代码。
    :func:`redirect` 函数是生成一个该 URL 地址的重定向响应对象。

#.  如果验证失败的话，会把错误消息显示给填写表单的用户。
    :func:`flash` 函数是把错误消息闪存下来，当翻译模版时可以在模版中获得错误消息。

#.  当用户初次访问 ``auth/register`` 地址时，或者出现过验证错误消息的话，
    一个 HTML 注册表单页面应该继续显示给注册中的用户。
    :func:`render_template` 函数会把一个模版翻译成 HTML 页面，
    下一篇教学文档就会开始学习写模版。


登录视图函数
--------------

这个视图函数与上面 ``register`` 视图函数采用了相同的模式。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/login', methods=('GET', 'POST'))
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            flash(error)

        return render_template('auth/login.html')

登录视图函数与 ``register`` 视图函数有几处不同：

#.  先把查询结果存储在变量 `user` 中以备稍后使用。

#.  :func:`~werkzeug.security.check_password_hash` 函数把登录时填写的
    用户密码以存储时相同的方式哈希化后，进行安全性比较。如果匹配上的话，用户密码
    才是合法的。

#.  :data:`session` 数据代理对象就是一个 :class:`dict` 字典数据类型，
    它把请求中的数据存储下来。当验证成功时，变量 `user` 中的 ``id`` 值
    存储到一个新的会话中。临时数据存储在一个 *cookie* 里，这个 cookie
    会发送到浏览器，然后浏览器把含有随后的请求 cookie 在送回来。Flask
    的安全信号对数据做了 *标记* ，所以会话中的数据无法被篡改。

现在用户的 ``id`` 是存储在 :data:`session` 会话代理对象中，数据就可以
在随后的请求中使用。在每个请求开始的时候，如果一名用户已经登陆过了，那么
用户的信息应该被加载，并且让其它的视图函数可以使用。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.before_app_request
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

:meth:`bp.before_app_request() <Blueprint.before_app_request>` 方法
注册了一个函数，这个函数会在视图函数之前运行，不管发出哪个 URL 地址请求。
具体到 ``load_logged_in_user`` 函数就是检查一名用户的 `id` 如果存储在
:data:`session` 会话代理中，就从数据库里获得这名用户的数据，存储到
:data:`g.user <g>` 数据代理对象上，这个数据代理对象与请求共存亡。
如果会话代理中没有用户的 `id` 或者用户的 `id` 不存在的话，
``g.user`` 的值就会是 ``None`` 值。


登出视图函数
-------------

要想登出，你需要从 :data:`session` 会话代理中移除用户 `id` 数据。
那么 ``load_logged_in_user`` 函数就不在随后的请求中加载一名用户数据。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))


在其它视图函数上需要授权限制
-------------------------------------

建立、编辑和删除博客发表都会需要一名用户的授权，也就是需要用户登录来进行操作。
一个 *装饰器* 就可以用来检查每个视图函数是否具有授权限制。

.. code-block:: python
    :caption: ``flaskr/auth.py``

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            return view(**kwargs)

        return wrapped_view

这个装饰器函数返回一个新的 `view` 函数，新函数打包了代入的原始函数。
新函数检查的是如果一名用户已经登录了就返回原视图函数结果，
否则就重定向到登录页面。如果一名用户被原视图函数调用后加载了数据，那么
就正常继续。
在学习写博客视图函数时，我们会使用这个装饰器函数。

端点和 URLs 地址
------------------

对于 :func:`url_for` 函数根据一个视图函数名和其它参数生成的 URL 地址来说。
与视图名有关的地址名就叫做 *端点*，并且默认与视图函数名完全一样。

例如，已经加入的 ``hello()`` 视图函数，在网络应用工厂中就有一个
名叫 ``'hello'`` 的端点，并且连接到 ``url_for('hello')`` 生成的地址上。
如果我们再加一个参数，你后面会看到这种用法，那么就要用
``url_for('hello', who='World')`` 来生成地址了。

当使用一张蓝图时，蓝图的名字是放在视图函数名前面的，所以
对于 ``login`` 视图函数的端点名就是上面 ``'auth.login'`` 的写法，
因为你要把蓝图模块名 ``'auth'`` 作为前缀名。这是值得注意的地方！

继续阅读 :doc:`templates` 文档内容。
