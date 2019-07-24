.. _larger-applications:

更大的网络应用
===================

想象一个简单的 Flask 网络应用结构看起来如下一样::

    /yourapplication
        yourapplication.py
        /static
            style.css
        /templates
            layout.html
            index.html
            login.html
            ...

对于小型网络应用来说这是好的，对于更大型的网络应用来说，
好的思路就是使用一个包模式，而不是模块模式了。
在 :ref:`tutorial <tutorial>` 文档中介绍了包模式结构，
查看 :gh:`example code <examples/tutorial>` 示例代码。

简单的包
---------------

要把模块转换成一种更大的包模式，只要建立一个文件夹
:file:`yourapplication` 子目录后把上面所有内容
都移到子目录里。然后，把 :file:`yourapplication.py` 
模块名重命名为 :file:`__init__.py` 模块名。
（确保先删除所有 ``.pyc`` 文件，否则最可能出现的问题就是断裂）

最终你应该看到如下的结构内容::

    /yourapplication
        /yourapplication
            __init__.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

但是现在你该如何运行你的网络应用呢？幼稚地执行
 ``python yourapplication/__init__.py`` 不会有效。
就是说 Python 不想让包中的模块成为启动文件。
但这不是什么大问题，只需要增加一个新文件，
名叫 :file:`setup.py` 与 
:file:`yourapplication` 子目录在一个路径下，包含如下内容::

    from setuptools import setup

    setup(
        name='yourapplication',
        packages=['yourapplication'],
        include_package_data=True,
        install_requires=[
            'flask',
        ],
    )

为了运行网络应用，你需要导出一个环境变量来告诉 Flask 去哪里
找到网络应用实例::

    $ export FLASK_APP=yourapplication

如果你此时在终端里的位置在项目目录以外，那么确保提供完整的
网络应用路径。同样你可以打开开发模式特性，如同下面一样::

    $ export FLASK_ENV=development

为了安装和运行网络应用，你需要发布如下命令::

    $ pip install -e .
    $ flask run

从这两个命令中我们能得到什么呢？
此时我们把网络应用重新结构化成多个模块。
唯一的事情就是要记住下面的检查清单：

1. 对于 `Flask` 网络应用对象的建立要在
   :file:`__init__.py` 文件里。这样每个模块
   才能安全地导入网络应用，并且 `__name__` 变量
   会解决正确的包问题。
2. 所有视图函数（带有一个 :meth:`~flask.Flask.route`
   装饰器的函数）都要导入到 :file:`__init__.py` 文件里。
   不是导入对象本身，而是导入模块。导入视图模块要在
   **网络应用对象建立完成之后写导入语句**。

下面是一个 :file:`__init__.py` 文件的示例::

    from flask import Flask
    app = Flask(__name__)

    import yourapplication.views

那么在 :file:`views.py` 文件中该如何导入呢？如下一样::

    from yourapplication import app

    @app.route('/')
    def index():
        return 'Hello World!'

最后你的项目结构看起来如下一样::

    /yourapplication
        setup.py
        /yourapplication
            __init__.py
            views.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

.. admonition:: 导入语句的回路问题

   每个 Python 编程者都讨厌这个问题，我们也遇到一些这类问题：

   回路导入（是当2个模块彼此依赖时出现的非法问题。在这里的情况
    :file:`views.py` 文件依赖 :file:`__init__.py` 文件）。
   显然这是一种败坏的思想，通用中这样使用实际上没有问题。
   原因就是我们没有在 :file:`__init__.py` 文件里真正使用视图模块，
   并且只是确保模块被导入了，然后我们都是在文件底部做事情。

   使用这种方法依然有一些问题，如果你想使用装饰器的话，
   那就不能再这样用了。查看
   :ref:`becomingbig` 文档部分了解一些处理这种问题的灵感。


.. _working-with-modules:

与蓝图一起工作
-----------------------

如果你要做更大型的网络应用的话，建议就是分解成许多小组，
每组都用一张蓝图来部署。对于这个话题参考
:ref:`blueprints` 文档部分绅士般的描述吧。
