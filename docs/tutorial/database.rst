.. currentmodule:: flask

定义和访问数据库
==============================

我们的网络应用会使用一个 `SQLite`_ 数据库来存储用户和发表内容。
Python 内置支持了 SQLite 数据库，就是用 :mod:`sqlite3` 标准库。

SQLite 数据库之所以方便，是因为它不需要配置一个数据库服务器，并且
是 Python 自带的内置数据库。不管如何做到的，如果并发请求中对数据库
进行写的操作，会按顺序来完成每个写操作，这会慢下来。小型网络应用
不在乎这种并发性能，一旦你的网络应用变大的话，你也许想要切换成另一种
不同的数据库。

本教程不会讨论有关数据库的细节问题。如果你不熟悉这个数据库的话，
查看 SQLite 文档了解 SQL 语言 `language`_ 即可。

.. _SQLite: https://sqlite.org/about.html
.. _language: https://sqlite.org/lang.html


连接到数据库
-----------------------

当我们与一个 SQLite 数据库一起工作的时候，
第一件事就是要建立一个数据库连接
（其它的数据库也都是一样）。 
任何一次数据库查询和操作都要使用数据库连接来执行，
数据库工作完成后数据库连接就关闭了。

在网络应用中，这种数据库连接典型地都与 HTTP 请求绑定在一起。
当处理一个 HTTP 请求时，在某个时间点上就建立了数据库连接，
然后在发送响应对象之前关闭数据库连接。

.. code-block:: python
    :caption: ``flaskr/db.py``

    import sqlite3

    import click
    from flask import current_app, g
    from flask.cli import with_appcontext


    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db


    def close_db(e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()

:data:`g` 是一个具体的代理对象，它对每个请求都保持唯一性。
它是用来存储请求期间许多函数要访问的数据用的。它存储了数据库
连接和复用数据库连接，而不是用来建立一个新的数据库连接的。
如果 ``get_db`` 在同一个请求中第二次被调用的话，确保数据库
连接是可用的。

:data:`current_app` 是另一个具体的代理对象，它指向了
 Flask 网络应用处理的请求。正是因为使用了一种网络应用工厂
模式，当写剩下的代码时就不需要一个网络应用实例对象了。
``get_db`` 函数会在网络应用已经建立完时调用，然后这个
函数开始处理一个请求，所以 :data:`current_app` 才可以被使用。
换句话说，没有网络应用被建立，就没有这个代理对象。

:func:`sqlite3.connect` 函数是建立一个指向
``DATABASE`` 配置键所描述的数据库文件的数据库连接。
这个数据库文件此时还不存在，
只有你稍后初始化数据库时才会建立这个数据库文件。

:class:`sqlite3.Row` 类是告诉数据库连接要返回像字典一样的
行数据。它允许根据名字来访问列数据。

``close_db`` 函数是通过检查 ``g.db`` 是否设置完，来检查
一个数据库连接是否建立完毕。如果数据库连接存在的话，该函数就
关闭数据库连接。有了这个函数后，你接下来要做的就是，
你要要把 ``close_db`` 函数告诉网络应用，
就是在网络应用工厂函数里写代码，这样在每个请求之后这个函数才被调用。


建立数据库表
-----------------

在 SQLite 数据库中，数据都是存储在 *数据库表* 里和 *列* 上。
在你存储数据和取回数据之前，这些都需要先建立完。
 Flaskr 项目会把用户存储在 ``user`` 数据库表中，
发表的内容会存储在 ``post`` 数据库表里。
用 SQL 语言来建立一个数据库文件，其中这两张表都是空数据库表：

.. code-block:: sql
    :caption: ``flaskr/schema.sql``

    DROP TABLE IF EXISTS user;
    DROP TABLE IF EXISTS post;

    CREATE TABLE user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    );

    CREATE TABLE post (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      author_id INTEGER NOT NULL,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      FOREIGN KEY (author_id) REFERENCES user (id)
    );

在 ``db.py`` 文件中增加一些 Python 函数，它们会运行这些 SQL 命令，
包含初始化数据库函数、增加命令行执行数据库初始化功能：

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_db():
        db = get_db()

        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """Clear the existing data and create new tables."""
        init_db()
        click.echo('Initialized the database.')

:meth:`open_resource() <Flask.open_resource>` 方法打开
 ``flaskr`` 包里的一个文件，它有用之处就是在后面部署网络应用时
你不需要知道位置所在就可以打开文件。 ``get_db`` 函数返回的是一个
数据库连接，用这个数据库连接来执行从 SQL 计划文件中读取的那些命令。

:func:`click.command` 函数是定义一个命令行命令， ``init-db``
这个名字就是在命令行中使用的，使用它时直接调用了  ``init_db`` 函数，
然后显示一个成功消息给你。你可以阅读 :ref:`cli` 参考内容来学习更多
关于写命令行命令的技术。


用网络应用来注册
-----------------------------

对于 ``close_db`` 和 ``init_db_command`` 两个函数来说，
要使用网络应用实例来进行注册；否则就无法被网络应用使用这两个函数。
不管如何做到的，由于你正在使用的是一个工厂函数，那么网络应用实例
在写这两个函数时是不可用的。所以我们要写一个函数来得到网络应用实例，
然后再做注册的事情。

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_app(app):
        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)

:meth:`app.teardown_appcontext() <Flask.teardown_appcontext>` 方法
告诉 Flask 要调用 `close_db` 函数，调用的时间点是返回响应对象之后清除时。

:meth:`app.cli.add_command() <click.Group.add_command>` 方法
把命令实际调用的 `init_db_command` 函数加入到命令行工具中，这样就可以
使用 ``flask`` 命令来调用 `init-db` 这个命令了。

在工厂函数中来导入和调用这个注册功能的 `init_app` 函数。
注意要把这段代码放在返回 `app` 之前，工厂函数尾部。

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import db
        db.init_app(app)

        return app


初始化数据库文件
----------------------------

好了，现在已经用 `app` 注册完 ``init-db`` 这个命令行命令了，
可以在终端里使用 ``flask`` 命令来调用，
就像前面见过的 ``run`` 命令用法一样。

.. 注意::

    如果你还在运行前面讲过的服务器，那么你可以终止服务器后再运行，
    或者你在一个新的终端里执行这个初始化数据库文件的命令。但是，
    如果你选择运行服务器时在新终端里执行这个命令的话，
    记住进入项目目录后激活虚拟环境，
    参考 :ref:`install-activate-env` 文档内容。
    同时也需要再设置一遍相同的 ``FLASK_APP`` 和 ``FLASK_ENV`` 
    环境变量后，再执行命令行命令。

运行 ``init-db`` 命令如下：

.. code-block:: none

    $ flask init-db
    Initialized the database.

现在你会看到在 ``instance`` 目录中的 ``flaskr.sqlite`` 文件出现在你的项目里了，
而且数据库初始化完毕后，该文件的大小不再是 *0* 了。

继续阅读 :doc:`views` 文档内容。
