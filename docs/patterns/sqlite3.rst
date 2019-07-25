.. _sqlite3:

用 Flask 使用 SQLite 3 数据库
====================================

在 Flask 中你可以容易地部署打开数据库连接需求，
并且当语境结束时关闭数据库连接 (常常是在请求结束时）。

你如何用 Flask 使用 SQLite 3 数据库呢？
下面是一个简单的示例::

    import sqlite3
    from flask import g

    DATABASE = '/path/to/database.db'

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

此时要使用数据库，网络应用必须有一个激活的网络应用语境（
如果有一个请求在线的话，网络应用语境要一直成立），或者
网络应用自身建立一个网络应用语境。那么在 ``get_db``
函数上才可以用来获得当前数据库连接。不管什么时候，
语境被销毁，数据库连接也会终止。

注意：如果你使用的是 Flask 0.9 或以前的老版本的话，
你需要使用 ``flask._app_ctx_stack.top`` ，而不是
把 ``g`` 用做 :data:`flask.g` 数据代理对象，
数据代理对象绑定到请求上，而不是绑定到网络应用语境上。

例如::

    @app.route('/')
    def index():
        cur = get_db().cursor()
        ...


.. 注意::

   请记住，释放请求和网络应用语境函数都一直被执行，
   即使一个请求之前处理器失败的话，或处理器从不执行的话，
   都会执行释放。由于这个机制我们在关闭数据库连接之前，
   还要确保此处有数据库。

根据需要连接数据库
---------------------

这种方法的优点（先使用再连接）是只有真的需要时才打开数据库连接。
如果你想要在一个请求语境之外使用这段代码的话，你可以在一个
Python 会话中来使用，通过手动打开网络应用语境::

    with app.app_context():
        # now you can use get_db()

.. _easy-querying:

查询容易
-------------

此时在每个请求处理函数中，你可以访问 `get_db()` 函数来获得
当前打开的数据库连接。要简化与 SQLite 数据库一起工作，一个
行工厂函数就是有用的。它把从数据库返回的每条结果转换成查询结果。
对于此时来说，要获得字典结果，而不是元组结果，那么就插入到我们
上面建立的 ``get_db`` 函数中::

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

这样就会让 sqlite3 模块为这个数据库连接返回字典结果，
字典都是更容易处理的。甚至更直接，我们反而可以把这个放在
 ``get_db`` 函数中::

    db.row_factory = sqlite3.Row

这种会使用 Row 对象的方法要比字典更好地返回查询结果。
这里会有许多 ``namedtuple`` 对象，所以我们可以通过
索引来访问，也可以通过键来访问。例如，假设我们有一个
 ``sqlite3.Row`` 对象名叫 ``r`` ，那么行有
 ``id``, ``FirstName``, ``LastName``, 和 ``MiddleInitial``::

    >>> # You can get values based on the row's name
    >>> r['FirstName']
    John
    >>> # Or, you can get them based on index
    >>> r[1]
    John
    # Row objects are also iterable:
    >>> for value in r:
    ...     print(value)
    1
    John
    Doe
    M

另外，提供一个查询函数是一种良好的思想，查询函数把
获得光标、执行查询，和取回结果三个操作组合在一起::

    def query_db(query, args=(), one=False):
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

这是一个上手的小函数，用一个行工厂组合起来，与数据库工作起来就令人更愉悦了，
这要比使用生食光标和数据库连接对象要好许多。

下面就是你如何使用这个查询函数::

    for user in query_db('select * from users'):
        print user['username'], 'has the id', user['user_id']

或者你只想要单个查询结果::

    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print 'No such user'
    else:
        print the_username, 'has the id', user['user_id']

要把变量部分代入到 SQL 语句中，在语境里使用一个问号，然后把参数代入成一个列表。
永远不要直接用字符串格式增加到 SQL 语句中，因为这样可以使得
 `SQL Injections <https://en.wikipedia.org/wiki/SQL_injection>`_ 
数据库注射攻击变成可能。

初始计划
---------------

关系型数据库需要计划，所以网络应用常常交付一个 `schema.sql` 文件来建立数据库。
提供一个函数来根据计划建立数据库是一种良好的思路。这样函数可以为你做如下工作::

    def init_db():
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

你可以稍后从 Python 会话中来建立这样的一个数据库：

>>> from yourapplication import init_db
>>> init_db()
