让项目变成可安装的应用
============================

让你的项目变成可安装的应用，这个意义在于你可以建立一个 *分发版本* 文件，
而且安装到其它的环境中，就像安装 Flask 框架到你的项目虚拟环境里一样。
这样让部署你的项目与安装其它第三方库一样简单了，所以你要使用所有标准
的 Python 工具来管理项目的所有事情。

安装过程中也会伴随其它好处，这些好处不是本教程所能学到的，
也不是一个 Python 新手用眼睛能观察出来的，好处如下：

*   目前来说，Python 和 Flask 都会把 ``flaskr`` 看成一个包，
    并且知道如何使用这个项目包，因为你正在把项目目录作为当前工作目录来运行。
    安装就意味着你可以不管在什么路径上都可以导入本项目。

*   你可以管理你的项目依赖库，就像其它包所做的一样，所以
    使用 ``pip install yourproject.whl`` 就可以安装依赖库。

*   许多单元测试工具可以把你的测试环境从开发环境中隔离出来。

.. 注意::
    单元测试会在本项目教程后面介绍到，但在接下来的项目教程中
    你应该一直启动着开发服务器。


描述项目
--------------------

对于 ``setup.py`` 文件来说，就是描述你的项目和属于项目的所有文件用的。

.. code-block:: python
    :caption: ``setup.py``

    from setuptools import find_packages, setup

    setup(
        name='flaskr',
        version='1.0.0',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'flask',
        ],
    )


``packages`` 参数是告诉 Python 要包含哪些包目录（以及目录中包含哪些 Python 文件）。
``find_packages()`` 参数值是个函数，它可以自动找到这些目录，所以你不用描述目录是哪些。
要包含其它文件，例如静态和模版目录，就要使用 ``include_package_data`` 参数。
Python 需要另一个文件，名叫 ``MANIFEST.in`` ，它是告诉 Python 项目所含的其它数据有哪些。

.. code-block:: none
    :caption: ``MANIFEST.in``

    include flaskr/schema.sql
    graft flaskr/static
    graft flaskr/templates
    global-exclude *.pyc

这四行告诉 Python 要复制 ``static`` 和 ``templates`` 目录中的内容，
以及复制 ``schema.sql`` 文件，但不复制所有二进制字节代码文件。

查看 `official packaging guide`_ 官方打包指导文档了解打包时使用的
其它文件和选项解释。

.. _official packaging guide: https://packaging.python.org/tutorials/distributing-packages/


安装项目
-------------------

在虚拟环境中使用 ``pip`` 来安装你的项目。

.. code-block:: none

    $ pip install -e .

这种安装命令用法告诉 pip 找到当前目录下 ``setup.py`` 文件后
安装成名叫 *可编辑模式* 或 *开发* 模式。
可编辑模式意味着与改变本地代码一样，如果你改变了项目的元数据，
例如项目的依赖包有变化，那么你只需要重新安装即可。

现在你可以使用 ``pip list`` 查看当前你的项目已经安装到虚拟环境里了。

.. code-block:: none

    $ pip list

    Package        Version   Location
    -------------- --------- ----------------------------------
    click          6.7
    Flask          1.0
    flaskr         1.0.0     /home/user/Projects/flask-tutorial
    itsdangerous   0.24
    Jinja2         2.10
    MarkupSafe     1.0
    pip            9.0.3
    setuptools     39.0.1
    Werkzeug       0.14.1
    wheel          0.30.0

现在要运行你的项目不需要任何变更。
``FLASK_APP`` 已经设置成 ``flaskr`` 并且 ``flask run`` 命令依然会运行
网络应用，但你可以在任何位置调用这个命令了，
不必在 ``flask-tutorial`` 目录下来运行。

继续阅读 :doc:`tests` 文档内容。
