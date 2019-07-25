.. _sqlalchemy-pattern:

Flask 中的 SQLAlchemy 数据库引擎
===================================

许多人都更喜欢 `SQLAlchemy`_ 作为数据库访问使用。在这种情况里都是
鼓励把你的 Flask 网络应用用作一个包，而不是一个模块，
并且把许多模块都分解成单个模块形式 (:ref:`larger-applications`)。
同时这不是需求，但却有很多的意义。

这里有4种共性方法来使用 SQLAlchemy 数据库引擎。
我会逐个以大纲形式列在下面：

Flask-SQLAlchemy 扩展件
--------------------------

因为 SQLAlchemy 是一种共性数据库抽象层，
还是一个对象关系映射器，作为映射器来说
需要一点儿配置工作，这里就有一个 Flask 扩展件
为你处理这些工作。如果你想要快速启动的话，
这就是建议使用的第一种方法。

你可以从 `PyPI <https://pypi.org/project/Flask-SQLAlchemy/>`_
下载 `Flask-SQLAlchemy`_ 扩展件。

.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/


描述方式
-----------

用 SQLAlchemy 描述方式是使用 SQLAlchemy 的最近一种方法。
这让你一次性定义数据库表和数据库模型，类似 Django 的工作方式。
另外下面的文本是我建议的官方 `declarative`_ 文档上展开的内容。

这里的 :file:`database.py` 模块是为你的网络应用作的一个示例::

    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()

    def init_db():
        # import all modules here that might define models so that
        # they will be registered properly on the metadata.  Otherwise
        # you will have to import them first before calling init_db()
        import yourapplication.models
        Base.metadata.create_all(bind=engine)

要定义你的模块，只通过上面的代码建立一个 `Base` 子类。
如果你好奇为什么我们不担心这里的线程呢？
 (像我们在 SQLite3 例子中所做的，用 :data:`~flask.g` 代理对象)：
那是因为 SQLAlchemy 为我们已经实现了，它使用
 :class:`~sqlalchemy.orm.scoped_session` 类做了那件事。

要用描述方式来使用 SQLAlchemy 与你的网络应用一起工作，
你只要把如下代码放到你的网络应用模块中即可。
Flask 会自动在请求结束时移除数据库会话，或者当网络应用
下线时自动关闭数据库会话::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

下面是一个示例模型 (例如把这段代码放到 :file:`models.py` 文件中。)::

    from sqlalchemy import Column, Integer, String
    from yourapplication.database import Base

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        email = Column(String(120), unique=True)

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return '<User %r>' % (self.name)

要建立数据库你可以使用 `init_db` 函数：

>>> from yourapplication.database import init_db
>>> init_db()

你可以插入条目到数据库中，像下面一样：

>>> from yourapplication.database import db_session
>>> from yourapplication.models import User
>>> u = User('admin', 'admin@localhost')
>>> db_session.add(u)
>>> db_session.commit()

查询也是直接的：

>>> User.query.all()
[<User u'admin'>]
>>> User.query.filter(User.name == 'admin').first()
<User u'admin'>

.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _declarative:
   https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/

手动对象关系映射
--------------------------------

对于上面的描述方式来说，手动对象关系映射有几个优点和几个缺点。
主要差异就是你分别定义数据库表和类，然后在映射到一起。
这更灵活，但要更多的敲打键盘。
通用中它工作像描述方式，所以也要确保把你的网络应用在一个包里分解成多个模块。

下面是为你的网络应用作的一个 :file:`database.py` 模块示例::

    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    def init_db():
        metadata.create_all(bind=engine)

与描述方式一样，你需要在每个请求之后或网络应用语境关闭之后关闭数据库会话。
把如下代码放到你的网络应用模块中::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

如下是一个数据库表和模型的示例 (把代码放到 :file:`models.py` 文件里)::

    from sqlalchemy import Table, Column, Integer, String
    from sqlalchemy.orm import mapper
    from yourapplication.database import metadata, db_session

    class User(object):
        query = db_session.query_property()

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return '<User %r>' % (self.name)

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), unique=True),
        Column('email', String(120), unique=True)
    )
    mapper(User, users)

查询和插入工作完全与上面的描述方式一样。


SQL 抽象层
---------------------

如果你只想要使用数据库系统 (和 SQL) 抽象层的话，
你基本上只需要数据库引擎即可::

    from sqlalchemy import create_engine, MetaData, Table

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData(bind=engine)

然后你可以在代码中描述数据库表，例如上面的例子，
或者自动化加载数据库表::

    from sqlalchemy import Table

    users = Table('users', metadata, autoload=True)

要插入数据你可以使用 `insert` 方法。我们不得不先得到一个数据库连接，
这样我们才可以使用一项数据库传输：

>>> con = engine.connect()
>>> con.execute(users.insert(), name='admin', email='admin@localhost')

SQLAlchemy 会自动为我们提交。

要查询你的数据库，你直接使用引擎，或使用一个数据库连接：

>>> users.select(users.c.id == 1).execute().first()
(1, u'admin', u'admin@localhost')

查询结果也都是像字典一样的元组：

>>> r = users.select(users.c.id == 1).execute().first()
>>> r['name']
u'admin'

你也可以把 SQL 语句字符串代入到
:meth:`~sqlalchemy.engine.base.Connection.execute` 方法里来查询：

>>> engine.execute('select * from users where id = :1', [1]).first()
(1, u'admin', u'admin@localhost')

对于 SQLAlchemy 的更多信息，回顾
`website <https://www.sqlalchemy.org/>`_ 官方站点。
