.. _caching-pattern:

缓存
=======

当你的网络应用运行的慢时，把一些东西放到缓存中。
好吧，至少这样是提速的最简单方法。一个缓存到底做了什么？
比如说你有一个函数，它要花一些时间来完成一些计算，
但如果5分钟过去了，要想结果依然够好。那么思路就是
你真的要把计算结果放到一个缓存中保留一段时间。

Flask 自身不提供给你缓存技术，但 `Flask-Caching`_ 扩展件可以。
Flask-Caching 支持各种后端类型，并且它甚至可能让你开发自己但缓存后端。


.. _Flask-Caching: https://flask-caching.readthedocs.io/en/latest/
