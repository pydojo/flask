用 MongoEngine 做 MongoDB 数据库
========================================

使用一种文档数据库，就像 MongoDB 一样是共同使用的数据库，
代替关系型数据库的一种新型数据库。
本模式介绍如何使用 `MongoEngine`_ 工具，
它是一个文档数据库映射器库，集成了 MongoDB 数据库。

一台运行 MongoDB 数据库的服务器和
 `Flask-MongoEngine`_ 扩展件都是所需要的前提条件。 ::

    pip install flask-mongoengine

.. _MongoEngine: http://mongoengine.org
.. _Flask-MongoEngine: https://flask-mongoengine.readthedocs.io


配置
-------------

基础配置可以通过在 ``app.config`` 上
定义 ``MONGODB_SETTINGS`` 属性来实现，
然后建立一个 ``MongoEngine`` 实例即可。 ::

    from flask import Flask
    from flask_mongoengine import MongoEngine

    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        "db": "myapp",
    }
    db = MongoEngine(app)


映射文档数据库
-----------------

要声明一个模块来代表一个 Mongo 文档数据库，建立一个
继承自 ``Document`` 类的子类后声明每个区域即可。 ::

    import mongoengine as me

    class Movie(me.Document):
        title = me.StringField(required=True)
        year = me.IntField()
        rated = me.StringField()
        director = me.StringField()
        actors = me.ListField()

如果文档含有嵌入式区域的话，使用 ``EmbeddedDocument`` 类
来定义嵌入式文档区域，并且使用 ``EmbeddedDocumentField`` 类
在父文档上来声明嵌入区域。 ::

    class Imdb(me.EmbeddedDocument):
        imdb_id = me.StringField()
        rating = me.DecimalField()
        votes = me.IntField()

    class Movie(me.Document):
        ...
        imdb = me.EmbeddedDocumentField(Imdb)


建立数据
-------------

针对区域来实例化你的文档类要使用关键字参数。
你也可以在实例化之后把值分配给区域属性。
然后调用 ``doc.save()`` 就可以保存到数据库中了。 ::

    bttf = Movie(title="Back To The Future", year=1985)
    bttf.actors = [
        "Michael J. Fox",
        "Christopher Lloyd"
    ]
    bttf.imdb = Imdb(imdb_id="tt0088763", rating=8.5)
    bttf.save()


查询数据
------------

使用类的 ``objects`` 属性来建立查询。
一个关键字参数查询区域上的等价数据。 ::

    bttf = Movies.objects(title="Back To The Future").get_or_404()

查询操作可以通过使用一个双下划线把区域名串联起来。
 ``objects`` 和通过调用所返回的查询结果都是可迭代对象。 ::

    some_theron_movie = Movie.objects(actors__in=["Charlize Theron"]).first()

    for recents in Movie.objects(year__gte=2017):
        print(recents.title)


文档
-------------

使用 MongoEngine 有许多方法来定义和查询文档数据库。
更多信息查看官方文档 <MongoEngine_>`_ 。

Flask-MongoEngine 扩展件在 MongoEngine 顶层增加了许多帮助工具。
也要查看 `documentation <Flask-MongoEngine_>`_ 扩展件文档。
