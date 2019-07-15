.. _extensions:

扩展件
==========

扩展件都是一些额外的包，这些包给一个 Flask 网络应用增添了功能性。
例如，一个扩展也许增加了发送电子邮件的功能，或者增加了一项连接数据库的功能。
有的扩展件增加完全新的框架来帮助建立某种类型的网络应用，就像一个 RESTful API 。


寻找扩展件
------------------

Flask 扩展件常常命名为 "Flask-Foo" 或者 "Foo-Flask" 的形式。
许多扩展件都罗列在 `Extension Registry`_ 扩展件注册页面，
这样可以由扩展件开发者们更新扩展件。你也可以从 PyPI 搜索带有
 `Framework :: Flask <pypi_>`_ 标签的包。


使用扩展件
----------------

咨询每个扩展件的文档，对于安装、配置和使用指导都有介绍。
通用中，在初始化过程中会从 :attr:`app.config <flask.Flask.config>` 拽取
扩展件自身的配置，然后把扩展件的配置代入到一个网络应用实例中去。
例如，一个名叫 "Flask-Foo" 的扩展件用起来像下面一样::

    from flask_foo import Foo

    foo = Foo()

    app = Flask(__name__)
    app.config.update(
        FOO_BAR='baz',
        FOO_SPAM='eggs',
    )

    foo.init_app(app)


建造扩展件
-------------------

在 `Extension Registry`_ 中包含了许多 Flask 扩展件的同时，
你也许找不到一个你需要的扩展件。如果发生了这种情况，你可以建立
你自己的扩展件。阅读 :ref:`extension-dev` 扩展件开发文档来
开发你自己的 Flask 扩展件。


.. _Extension Registry: http://flask.pocoo.org/extensions/
.. _pypi: https://pypi.org/search/?c=Framework+%3A%3A+Flask
