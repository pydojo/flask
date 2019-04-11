Flask
=====

Flask 是一个轻量级 `WSGI`_ 网络应用程序框架。使用 Flask 可以让你能够快速容易起步，
使用标量化能力建立多层化应用。起初 Flask 是一个简单地把 `Werkzeug`_
和 `Jinja`_ 打包在一起，后来逐渐成长为最受欢迎的 Python 网络应用框架之一。

Flask 提供了许多建议，但我们从不强迫定规使用一个依赖或一种项目层次。
程序的建造完全由开发者自己去选择，并且开发者们可以使用它们想用的任何一种库支持。
有许多扩展包来自社区，这样才让增加新功能更容易。


如何安装 Flask
----------

安装与更新都是使用 `pip`_:

.. code-block:: text

    pip install -U Flask


一个简单的例子
----------------

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello():
        return 'Hello, World!'

.. code-block:: text

    $ env FLASK_APP=hello.py flask run
     * Serving Flask app "hello"
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)


如何做贡献？
------------

对于指导搭建一个开发环境以及如何为 Flask 作出贡献，
请查看 `contributing guidelines`_

.. _contributing guidelines: https://github.com/pallets/flask/blob/master/CONTRIBUTING.rst


资助我们
------

调色板组织开发并支持 Flask 以及众多库的使用。
为了贡献者与用户社区的成长，可以多次资助我们的项目，
如果你有能力的话，何不为此做一份贡献呢。 `please
donate today`_.

.. _please donate today: https://psfmember.org/civicrm/contribute/transact?reset=1&id=20


众多参考链接
--------

* 站点 : https://www.palletsprojects.com/p/flask/
* 文档 : http://flask.pocoo.org/docs/
* 许可证 : `BSD <https://github.com/pallets/flask/blob/master/LICENSE>`_
* 发布 : https://pypi.org/project/Flask/
* 代码 : https://github.com/pallets/flask
* 问题跟进 : https://github.com/pallets/flask/issues
* 测试状态 :

  * Linux, Mac: https://travis-ci.org/pallets/flask
  * Windows: https://ci.appveyor.com/project/pallets/flask

* 测试覆盖率 : https://codecov.io/gh/pallets/flask

.. _WSGI: https://wsgi.readthedocs.io
.. _Werkzeug: https://www.palletsprojects.com/p/werkzeug/
.. _Jinja: https://www.palletsprojects.com/p/jinja/
.. _pip: https://pip.pypa.io/en/stable/quickstart/
