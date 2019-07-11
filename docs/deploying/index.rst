.. _deployment:

部署选项
==================

轻量级意味着容易使用， **Flask 的内置服务器不适合生产环境** 因为标量性不是很好。
对于正确地在生产环境中运行 Flask 网络应用有一些选项都文档化在这里。

如果你想要把你的 Flask 网络应用部署到一台 WSGI 服务器上，相关文档不在这里，
查看服务器文档来了解如何使用一个 WSGI 应用。
只要记住你的 :class:`Flask` 类建立的实例应用对象实际上就是一个 WSGI 应用。


主机选择
--------------

- `Deploying Flask on Heroku <https://devcenter.heroku.com/articles/getting-started-with-python>`_
- `Deploying Flask on OpenShift <https://developers.openshift.com/en/python-flask.html>`_
- `Deploying Flask on Webfaction <http://flask.pocoo.org/snippets/65/>`_
- `Deploying Flask on Google App Engine <https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env>`_
- `Deploying Flask on AWS Elastic Beanstalk <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html>`_
- `Sharing your Localhost Server with Localtunnel <http://flask.pocoo.org/snippets/89/>`_
- `Deploying on Azure (IIS) <https://azure.microsoft.com/documentation/articles/web-sites-python-configure/>`_
- `Deploying on PythonAnywhere <https://help.pythonanywhere.com/pages/Flask/>`_

自服务主机选项
-------------------

.. toctree::
   :maxdepth: 2

   wsgi-standalone
   uwsgi
   mod_wsgi
   fastcgi
   cgi
