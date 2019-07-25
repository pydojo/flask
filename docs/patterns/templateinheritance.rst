.. _template-inheritance:

模版继承
====================

Jinja 最有威力的部分就是模版继承系统。模版继承可以让你建立一个基础骨架模版，
骨架模版含有你的站点所有共同使用的元素，并且定义的 **块** 语句在子模版中可以覆写。

听起来复杂，但这是非常基础的功能。最容易理解的方法就是通过一个例子作为开始。


基础模版
-------------

这种模版我们会命名为 :file:`layout.html` 文件名，定义一个简单的 HTML 骨架文档，
你可以使用一个简单的双列排版页面。它的子模版负责填充内容块语句：

.. sourcecode:: html+jinja

    <!doctype html>
    <html>
      <head>
        {% block head %}
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <title>{% block title %}{% endblock %} - My Webpage</title>
        {% endblock %}
      </head>
      <body>
        <div id="content">{% block content %}{% endblock %}</div>
        <div id="footer">
          {% block footer %}
          &copy; Copyright 2010 by <a href="http://domain.invalid/">you</a>.
          {% endblock %}
        </div>
      </body>
    </html>

在这个模版里， ``{% block %}`` 定义的4歌块语句都是子模版可以填充的元素。
所有 `block` 语句就是告诉模版引擎一个子模版可以覆写的区域。

子模版
--------------

一个子模版也许看起来如下一样：

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Index{% endblock %}
    {% block head %}
      {{ super() }}
      <style type="text/css">
        .important { color: #336699; }
      </style>
    {% endblock %}
    {% block content %}
      <h1>Index</h1>
      <p class="important">
        Welcome on my awesome homepage.
    {% endblock %}

这里的 ``{% extends %}`` 语句是关键。
它告诉模版引擎本模版扩展自另一个模版。
当模版系统评估本模版时，首先做的就是分配父模版内容。
`extends` 语句必须放在本模版的第一行上。
要翻译定义在父模版中的块语句内容，
就是用 ``{{ super() }}`` 语句。
