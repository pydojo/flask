项目层次
==============

建立一个项目目录后进入项目目录的命令是：

.. code-block:: none

    $ mkdir flask-tutorial
    $ cd flask-tutorial

然后按照 :doc:`installation instructions </installation>` 文档内容来
配置一个 Python 虚拟环境后为你的项目安装 Flask 框架。

从此时开始，本教程内容都是假设你工作在 ``flask-tutorial`` 目录上。
每个代码块的顶层文件名都会关联到这个目录上。

单个文件形式的网络应用
---------------------------

一个 Flask 网络应用可以简单放在单个文件中。

.. code-block:: python
    :caption: ``hello.py``

    from flask import Flask

    app = Flask(__name__)


    @app.route('/')
    def hello():
        return 'Hello, World!'

不管如何做到的，当一个项目变得更大时，
把所有代码放到一个文件里，会让人非常难受。
Python 的众多项目都使用 *包* 的概念来把
代码组织到多个模块中，这些模块可以在需求的
位置上再被导入，并且本教程也会这样做。

本项目目录会包含：

* ``flaskr/`` 目录，一个 Python 包，其中放你的网络应用代码和相关文件。
* ``tests/`` 目录，一个含有许多单元测试模块的目录。
* ``venv/`` 目录，一个 Python 虚拟环境目录，其中安装 Flask 和其它依赖包。
* 一些安装文件会告诉 Python 如何安装你的项目。
* 版本控制配置文件，例如， `git`_ 文件。你应该为你的所有项目都习惯使用某种
  版本控制系统，不管项目规模是小还是大。
* 任何以后你要增加的其它项目文件。

.. _git: https://git-scm.com/

最终，你的项目层次会看起来如下一样：

.. code-block:: none

    /home/user/Projects/flask-tutorial
    ├── flaskr/
    │   ├── __init__.py
    │   ├── db.py
    │   ├── schema.sql
    │   ├── auth.py
    │   ├── blog.py
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── auth/
    │   │   │   ├── login.html
    │   │   │   └── register.html
    │   │   └── blog/
    │   │       ├── create.html
    │   │       ├── index.html
    │   │       └── update.html
    │   └── static/
    │       └── style.css
    ├── tests/
    │   ├── conftest.py
    │   ├── data.sql
    │   ├── test_factory.py
    │   ├── test_db.py
    │   ├── test_auth.py
    │   └── test_blog.py
    ├── venv/
    ├── setup.py
    └── MANIFEST.in

如果你正在使用 `git` 版本控制系统，
如下生成的文件在运行你的项目时应该被忽略。
也许有其它文件也要忽略，这要根据你使用的文本编辑器来决定。
通用中，所忽略的文件都应该不是你写的文件。
使用 `git` 来忽略那些不是你写的文件：

.. code-block:: none
    :caption: ``.gitignore``

    venv/

    *.pyc
    __pycache__/

    instance/

    .pytest_cache/
    .coverage
    htmlcov/

    dist/
    build/
    *.egg-info/

继续阅读 :doc:`factory` 文档内容。
