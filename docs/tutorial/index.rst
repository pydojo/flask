.. _tutorial:

教程
========

.. toctree::
    :caption: Contents:
    :maxdepth: 1

    layout
    factory
    database
    views
    templates
    static
    blog
    install
    tests
    deploy
    next

本教程会带着你走遍建立一个基础博客网络应用的全过程，我们叫它 Flaskr 。
支持多用户注册、登录、发表、编辑自己的内容、或删除自己的内容五项功能。
你会打包这个应用后安装到其它电脑上。

.. image:: flaskr_index.png
    :align: center
    :class: screenshot
    :alt: screenshot of index page

前提条件是你已经熟悉 Python 这个编程语言。
在 Python 语言官方教程文档中 `official tutorial`_ 
是你学习 Python 语言或复习 Python 语言最好的方式。

.. _official tutorial: https://docs.python.org/3/tutorial/

同时本教程设计的目的就是给出一个良好的起点，本教程不会涵盖所有的 Flask 特性。
要想对 Flask 来一次整体概览，查看 :ref:`quickstart` 文档后你就知道 Flask
可以做什么了，然后你可以深入其它文档来发现更多认知。
本教程只使用 Python 和 Flask 所提供的技术。在其它项目里，
你也许决定使用 :ref:`extensions` Flask 扩展件或其它 Python 库来让一些
任务变得更简单。

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

Flask 就是灵活，它不需要你使用任何一种特殊项目或特殊代码图层。
不管如何做到的，当第一次开启本教程时，就是用一个更加结构化的方法
来学习网络应用开发确实是有帮助的事情。
这也意味着本教程会需要一点缓慢的学习过程，但一旦完成本教程，
你可以避免许多共性的痛苦，而这些痛苦都是新开发者们都会遇到的，
而且本教程所建立的这个项目是容易继续扩展变大的。
一旦你与 Flask 相处变得更加舒服时，你可以走出本教程所使用的结构，
然后获得完整的 Flask 灵活性优势。

.. image:: flaskr_edit.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

:gh:`The tutorial project is available as an example in the Flask
repository <examples/tutorial>`，如果你想要把你写的本项目与最终本项目产品
做比较的话，可以从这个仓库获得产品代码。

继续阅读 :doc:`layout` 文档内容。
