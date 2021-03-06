开门见山
===========

在你开始使用 Flask 之前先阅读本文档。
希望回答许多关于项目目的和项目目标方面的众多问题，
然后你会明白什么时候应该使用 Flask 框架，或什么时候不应该使用。

*微* 的真实含义是什么？
-----------------------

*微* 不意味着你的整个网络应用只适合放到单个 Python 文件里（尽管当然可以做到），
也不意味着 Flask 在功能性上有什么缺陷。
*微* 在微框架中的意思是 Flask 瞄准了让核心简单却是扩展性的。
Flask 不会为你做许多决定，例如要使用什么样的数据库。
Flask 所做的决定都是属于容易改变的性质，例如，使用什么模版引擎。
至于其它难于变化的都由你来决定，所以 Flask 可以是你所需要的，也可以什么都不是。

默认下，Flask 不包括一个数据库抽象层，表单验证或任何其它已经存在的做一件事的不同库。
相反，Flask 支持的所有扩展件增加诸如此类的功能到你的网络应用中，即使已经用 Flask 部署过也可以。
大量的扩展件提供了数据库集成功能，表单验证功能，上传文件功能，各种授权技术，以及多如牛毛的功能扩展件。
也许你觉得 Flask 就是“微小”，但 Flask 是为生产而准备的用在各种需求上的框架。

配置与惯例
-----------------------------

Flask 具有许多配置项值，经过明智地考虑后提供了默认值，并且启动时需要较少的惯例即可。
对于惯例来说，模版和静态文件都存储在网络应用的 Python 源代码树状结构子目录中，
目录名分别是 :file:`templates` 和 :file:`static` 文件夹。同时这也是可以改变的，
你常常不需要去变化它，尤其是启动之后。

带着 Flask 一起成长
-----------------------

一旦你拥有了 Flask 后，网络应用跑起来，你会在社区中发现各种各样的扩展件可用，
从而把你的项目集成到生产中去。Flask 核心团队审阅这些扩展件，并确保验收完的扩展件
不会在未来发布的版本中导致断裂情况。

因为你的代码会增长，所以你来作出适合你项目的设计决策，自由权给你。
Flask 会继续提供非常直接连接到 Python 已经提供的最好的层连机制。
你可以用 SQLAlchemy 部署高级模式，或者用其它数据库工具，把非关系型
数据库存储合适地部署在网络应用中，然后获得未知框架工具优势来建立 WSGI 应用，
建立 Python 网络接口。

Flask 包含了许多钩子来自定义其行为表现。需要你具备更多自定义能力，Flask 类是为子类化而建立的。
如果你们在自定义能力上感兴趣的话，查看 :ref:`becomingbig` 文档。
如果你对 Flask 的设计原则感到好奇的话，回顾 :ref:`design` 文档。

继续阅读 :ref:`installation` 文档， :ref:`quickstart` 文档，
或 :ref:`advanced_foreword` 文档。
