.. currentmodule:: flask

博客蓝图
==============

你会使用授权蓝图同样的技术来学习如何写博客蓝图。
博客应该列出所有的发表内容，并在登录后才许可用户
建立发表内容，然后允许登录中的用户发表一篇内容，
或者删除一篇自己发表的内容。

因为你部署的每个视图函数，一直运行开发模式服务器。
当你保持变更后的代码，尝试刷新浏览器即可测试效果。

第二张蓝图
-------------

定义蓝图模块后注册在网络应用工厂函数里。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for
    )
    from werkzeug.exceptions import abort

    from flaskr.auth import login_required
    from flaskr.db import get_db

    bp = Blueprint('blog', __name__)

在工厂函数中导入并注册博客蓝图，使用的依然是
:meth:`app.register_blueprint() <Flask.register_blueprint>` 方法。
把如下代码依然放在返回网络应用实例之前。

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import blog
        app.register_blueprint(blog.bp)
        app.add_url_rule('/', endpoint='index')

        return app


与授权蓝图不同，博客蓝图没有设置一个 ``url_prefix`` 参数。
所以 ``index`` 视图函数会放在 ``/`` URL 根路径上，而
``create`` 视图函数放在 ``/create`` 路径上，诸如此类。
博客是 Flaskr 项目的主要特性，所以把博客页面作为主页是有意义的。

不管如何做到的，对于 `endpoint` 端点参数指向的 ``index`` 视图函数
定义在 ``blog.index`` 模块中。一些授权视图函数指向一个纯端点
``index`` 即可。
:meth:`app.add_url_rule() <Flask.add_url_rule>` 方法会用
``/`` URL 地址把端点名 ``'index'`` 关联起来，所以这2种
``url_for('index')`` 或 ``url_for('blog.index')`` 用法都有效，
生成的 ``/`` URL 地址都是同一个地址。

在另一种网络应用里，你也许给博客蓝图增加一个 ``url_prefix`` 参数，
然后在网络应用工厂中单独定义一个 ``index`` 视图函数，
就像 ``hello`` 视图函数那种做法。那么 ``index`` 和
``blog.index`` 端点生成的 URLs 就不是同一个地址了。


index 视图函数
---------------

`index` 视图函数会用来显示所有的发表内容，按照最新发布来排序。
一个 ``JOIN`` 语句会用到，所以来自 ``user`` 数据库表的授权信息
要作为结果来使用。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/')
    def index():
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('blog/index.html', posts=posts)

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/index.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Posts{% endblock %}</h1>
      {% if g.user %}
        <a class="action" href="{{ url_for('blog.create') }}">New</a>
      {% endif %}
    {% endblock %}

    {% block content %}
      {% for post in posts %}
        <article class="post">
          <header>
            <div>
              <h1>{{ post['title'] }}</h1>
              <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
            </div>
            {% if g.user['id'] == post['author_id'] %}
              <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
            {% endif %}
          </header>
          <p class="body">{{ post['body'] }}</p>
        </article>
        {% if not loop.last %}
          <hr>
        {% endif %}
      {% endfor %}
    {% endblock %}

当一名用户登录后，模版中的 ``header`` 块语句增加一个到 ``create`` 视图函数的超链接。
当登录的用户是这一篇发表内容的作者的话，才会看到一个 "Edit" 超链接连接到
 ``update`` 视图函数来修改更新发表内容。模版中的 ``loop.last`` 是一个具体的变量，
它是在 `Jinja for loops`_ 内部可以直接使用的。每篇发表的内容后会显示一行来分隔下一篇内容，
但最后一篇没有这一分隔行。

.. _Jinja for loops: http://jinja.pocoo.org/docs/templates/#for


create 视图函数
---------------------

对于 ``create`` 视图函数来说，工作起来与授权蓝图中的 ``register`` 视图函数一样。
既显示表单内容，也要验证发表的数据，然后把发表的内容存储在数据库中，或者显示一个错误提示。

对于授权蓝图中所写的 ``login_required`` 装饰器也会用在博客蓝图中视图函数上。
一名用户必须登录后才可以看到对应的视图函数呈现的内容，否则都会重定向到登录页面上。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/create', methods=('GET', 'POST'))
    @login_required
    def create():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/create.html')

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/create.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}New Post{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title" value="{{ request.form['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
    {% endblock %}


update 视图函数
---------------------

对于 ``update`` 和 ``delete`` 这两个视图函数来说都会根据
``id`` 来获得一篇 ``post`` 内容，然后检查作者与登录用户是否匹配。
要避免重复代码，你可以写一个获得 ``post`` 内容的函数后在每个视图
中来调用这个函数。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    def get_post(id, check_author=True):
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()

        if post is None:
            abort(404, "Post id {0} doesn't exist.".format(id))

        if check_author and post['author_id'] != g.user['id']:
            abort(403)

        return post

:func:`abort` 函数会抛出一个具体的列外，这个例外会返回一个 HTTP 状态代号。
该函数第二个参数可以作为要显示的错误消息内容，否则会使用默认的消息内容。
代号 ``404`` 意味着 “找不到你要的内容”，而 ``403`` 代号意味着
“禁止查看你要找的内容”。（代号 ``401`` 意味着 “你没有权限查看你要找的内容”，
但你不用返回状态代号，而是重定向到登录页面即可。）

函数中定义的 ``check_author`` 参数是作为函数获得一篇 ``post`` 内容时，
是否需要进行作者检查功能的开关。如果你写了一个视图函数用来在一个页面上显示
单个发布内容的话，这个参数就有用了，因为不涉及修改发布内容，所以不用在乎用户
是否与作者相匹配。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/update', methods=('GET', 'POST'))
    @login_required
    def update(id):
        post = get_post(id)

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/update.html', post=post)

对于 ``update`` 视图函数来说，与前面所写的视图函数都不一样，
调用它时需要一个参数 ``id`` 。这样才能对应上路由地址中的 ``<int:id>`` 变量。
一个真正的 URL 地址看起来会像 ``/1/update`` 这种形式。
Flask 会捕获 ``1`` 这个变量来确保是一个 :class:`int` 整数数据类型，
然后把这个值作为 ``id`` 参数值代入到视图函数中。如果你不描述 ``int:`` 的话，
而只用 ``<id>`` 的话，那么 Flask 捕获的值就会是字符串数据类型了。
要生成一个 URL 地址给更新页面， :func:`url_for` 函数需要用到这个 ``id`` 参数值，
所以要代入其中 ``url_for('blog.update', id=post['id'])`` ，这也是为什么
在上面的 ``index.html`` 模版文件中会出现这种写法。

对于 ``create`` 和 ``update`` 视图函数来说看起来非常相似。
主要区别在于 ``update`` 视图函数使用了一个 ``post`` 对象和
一个 ``UPDATE`` 查询语句，而不是使用 ``INSERT`` SQL 语句。
使用了一些聪明的重构技术，你可以使用一个视图函数和一个模版就完成
两件事，但针对教程来说更聪明的做法就是把它们分开实现。

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/update.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Edit "{{ post['title'] }}"{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title"
          value="{{ request.form['title'] or post['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
      <hr>
      <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
        <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
      </form>
    {% endblock %}

更新模版有2个表单。第一个表单用来把编辑完的数据发布到当前页面 (``/<id>/update``) 上。
第二个表单只含有一个按钮功能，并且描述了一个 ``action`` 属性，这个属性是用来发布到
删除视图函数上的一个动作。按钮使用某个 JavaScript 脚本来显示一个确认对话框，确保
提交删除指令之前进行确认。

模版中的 ``{{ request.form['title'] or post['title'] }}`` 这种书写模式是
用来选择什么样的数据显示在表单中。当表单还没有提交时，原来的 ``post`` 数据会显示，
如果非法表单数据被提交的话，你又想显示篡改内容，这样用户才可以修复错误，所以就要使用
``request.form`` 获得的数据来显示。 :data:`request` 数据对象是另一个在
模版中自动可以使用的代理对象。


delete 视图函数
-------------------

对于 `delete` 视图函数来说不需要自己的模版，删除按钮是 ``update.html`` 模版的一部分，
并且其表单数据发布到 ``/<id>/delete`` URL 地址上。因此不需要删除模版，删除视图函数
只会处理 HTTP 的 ``POST`` 请求方法，然后重定向到 ``index`` 视图函数上去。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/delete', methods=('POST',))
    @login_required
    def delete(id):
        get_post(id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('blog.index'))

恭喜，你到此写完成了你的网络应用！
花点时间在浏览器上与网络应用玩一会儿吧。
不管如何做到的，对于这个项目来说还有更多要做的。

继续阅读 :doc:`install` 文档内容。
