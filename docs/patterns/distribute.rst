.. _distribute-deployment:

部署安装工具
=========================

`Setuptools`_, 是一个扩展库，共同用在分发 Python 库和扩展库。
它扩展了 distutils 标准库，标准库是随 Python 安装的一个模块，
也支持各种更多层化结构，这样让更大型的应用程序变得容易分发：

- **支持众多依赖关系**: 一个库或一个应用程序可以声明一份依据
  其它库的清单，这些其它库都会自动为你安装。
- **包注册**: setuptools 把你的包注册成 Python 安装形式。
  这就让从另一个包查询一个包提供的信息变成可能。这个系统最著名
  的特性就是允许一个包作为一个入口点，一个包声明一个入口点后，
  其它包可以用钩子进入该包扩展成其它的包。
- **安装管理器**: :command:`pip` 命令可以为你安装其它的库。

如果你安装的 Python 官网版本 (>=2.7.9) 或 (>=3.4) 的话，
在你的系统上已经有 pip 和 setuptools 了。否则你需要自己安装。

Flask 自身和所有你可以在 PyPI 上找到的库既可以用
setuptools 分发，也可以用 distutils 分发。

在这里我们假设你的网络应用名叫 :file:`yourapplication.py` 
并且你没有使用一个模块，而是要用 :ref:`package
<larger-applications>` 包的形式。如果你还没有把网络应用
转换成一个包的话，回顾 :ref:`larger-applications` 模式文档
看看如何实现应用变成包的方法。

使用 setuptools 的部署工作是进入更加多层化和更加自动化部署情景
的第一步。如果你想要全部自动化过程，
还要阅读 :ref:`fabric-deployment` 参考文档内容。

基础配置脚本
------------------

因为你已经安装 Flask 了，在你的系统上也有了可用的 setuptools 库。
Flask 也是依据 setuptools 库来分发的。

标准的免责声明应用在： :ref:`you better use a virtualenv
<virtualenv>` 参考文档中。

你的配置代码总要放在名叫 :file:`setup.py` 的一个文件中，
与你的网络应用在一个路径里。这个文件名是惯例，因为每个人都
会查看是否有这个文件，你最好不要改动这个名字。

对于一个 Flask 网络应用来说，
一个基础 :file:`setup.py` 文件代码如下一样::

    from setuptools import setup

    setup(
        name='Your Application',
        version='1.0',
        long_description=__doc__,
        packages=['yourapplication'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask']
    )

请记住，你要明确地描述子包列表。如果你想要 setuptools 库
自动查看这些包的话，你可以使用 ``find_packages`` 函数::

    from setuptools import setup, find_packages

    setup(
        ...
        packages=find_packages()
    )

该 ``setup`` 函数中的大部分参数都要自己来解释清楚，
``include_package_data`` 和 ``zip_safe`` 两项可以不用。
``include_package_data`` 参数告诉 setuptools 库要查找
一个 :file:`MANIFEST.in` 文件，并且安装里面描述的所有条目，
那些条目都匹配成包数据。我们会使用这个文件来分发静态文件和模版，
随着 Python 模块一起分发(查看 :ref:`distributing-resources` 内容)。
该 ``zip_safe`` 旗语参数可以用来开启建立或放置建立压缩档案。
通用中你可能不想让你的那些包都安装成压缩文件，因为有些工具不支持
压缩文档形式，并且给调试造成大量困难。


标签版本建立
--------------

在发布和开发版本建立之间这是有用的。增加一个
:file:`setup.cfg` 文件来配置这些选项内容。 ::

    [egg_info]
    tag_build = .dev
    tag_date = 1

    [aliases]
    release = egg_info -Db ''

运行 ``python setup.py sdist`` 命令会建立一个开发包，其中含有
".dev" 和当前日期内容增加到版本建立信息中：
 ``flaskr-1.0.dev20160314.tar.gz`` 。
运行 ``python setup.py release sdist`` 命令会建立一个发布包，
只含有版本号信息： ``flaskr-1.0.tar.gz`` 。


.. _distributing-resources:

分发资源
----------------------

如果你尝试安装你刚建立的包的话，你会注意到像
 :file:`static` 或 :file:`templates` 文件夹都没有安装。
原因就是 setuptools 还不知道哪些文件要为你增加到分发中。
那么你应该做什么呢？那就是建立一个 :file:`MANIFEST.in` 文件，
与你的 :file:`setup.py` 文件在一个路径下。把应该增加的资源文件
都列在这个分发资源文件里::

    recursive-include yourapplication/templates *
    recursive-include yourapplication/static *

别忘了，即使罗列在你的 :file:`MANIFEST.in` 文件中的资源，
它们也不会安装上，除非你在 ``setup`` 函数中把参数
`include_package_data` 设置成 ``True`` 才会真正的安装资源！


声明依赖关系
----------------------

依赖关系都要声明在 ``install_requires`` 参数中，以列表形式描述。
列表中的每一项都是一个应该从 PyPI 上安装的包名。
默认会一直安装最新的版本，但你也可以提供版本号的上下限。
如下就是一个示例::

    install_requires=[
        'Flask>=0.2',
        'SQLAlchemy>=0.6',
        'BrokenPackage>=0.7,<=1.0'
    ]

前面已经提醒过了，众多依赖包都要从 PyPI 来安装。如果你想要的一个
依赖包在 PyPI 上找不到，而且不属于一个不想分享的内部包情况的话，
你该怎么办呢？只需要提供一个类似 PyPI 的入口点并且提供另一个位置
链接让 setuptools 应该查询得到::

    dependency_links=['http://example.com/yourfiles']

确保包所在的页面有一个目录清单，并且页面上的链接都指向实际文件，
文件名都要正确，这就是与 setuptools 库如何发现所需文件一样。
如果你有一个内部公司服务器的话，提供含有这些依赖包的 URL 地址即可。


安装 / 开发
-----------------------

要安装你的网络应用（理想的环境就是在虚拟环境中）只要运行
:file:`setup.py` 脚本时使用 ``install`` 参数即可。
它就会把你的网络应用安装到虚拟环境的 site-packages 文件夹里，
并且也会下载并安装所有依赖包::

    $ python setup.py install

如果你们正在开发这个包的话，并且也想需要安装成开发版，
你可以使用 ``develop`` 参数来安装::

    $ python setup.py develop

开发版的安装优势是，安装一个连接到 site-packages 目录，
而不是把数据复制到这个目录中。你可以稍后继续工作在开发代码上，
而且每次代码变更后都不用再次使用 ``install`` 来安装了。


.. _pip: https://pypi.org/project/pip/
.. _Setuptools: https://pypi.org/project/setuptools/
