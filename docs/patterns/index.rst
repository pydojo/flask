.. _patterns:

Flask 的众多模式
==================

某些事物都是共性的，在网络应用中足以有机会让你发现它们。
例如，大量的网络应用都使用关系型数据库和用户授权。
在这种情况中，在请求开始时它们都会打开一个数据库连接，
并且在用户当前登录完就获得信息。在请求结束时，数据库
连接会再次关闭。

这里有更多用户贡献了代码片段和许多模式 `Flask
Snippet Archives <http://flask.pocoo.org/snippets/>`_

.. toctree::
   :maxdepth: 2

   packages
   appfactories
   appdispatch
   apierrors
   urlprocessors
   distribute
   fabric
   sqlite3
   sqlalchemy
   fileuploads
   caching
   viewdecorators
   wtforms
   templateinheritance
   flashing
   jquery
   errorpages
   lazyloading
   mongoengine
   favicon
   streaming
   deferredcallbacks
   methodoverrides
   requestchecksum
   celery
   subclassing
   singlepageapplications
