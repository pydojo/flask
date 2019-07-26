.. currentmodule:: flask

模版
=========

你已经为你的网络应用写完了授权蓝图视图，
但是如果你运行服务器并访问任何一个 URLs 地址，
你都会看到一个
``jinja2.exceptions.TemplateNotFound`` 例外。
这是因为调用 :func:`render_template` 函数时，
你还没有写模版导致的。模版文件会存储在 ``flaskr`` 包目录
中的 ``templates`` 子目录里。

模版都是含有静态数据或为动态数据提供占位符的文件。
一个模版被翻译时用描述数据来生产出最终的文档页面。
Flask 就是使用 `Jinja`_ 模版库来翻译模版文件的。

在你的网络应用中，你会使用模版来翻译 `HTML`_ 页面，
这样就可以在浏览器中显示内容给用户了。在 Flask 中，
Jinja 被配置成 *自动转义* 任何一种数据，转义后的
数据翻译到 HTML 模版里。这就意味着，要翻译用户的
输入数据就变得安全了；输入的任何一个字符都可能把
HTML 内容弄乱，例如， ``<`` 和 ``>`` 就会 *转义*
成 *安全* 的数据值，正常显示在浏览器中，不会出现不想要的结果。

Jinja 模版语言外表和行为最像 Python 语言了。
在模版中静态数据句法区别就在于具体的分隔符，
Jinja 模版句法都是写在 ``{{`` 和 ``}}`` 里面，
形成一个表达式输出到最终文档页面里。
而 ``{%`` 和 ``%}`` 用在控制流语句上，像
``if`` 和 ``for`` 语句。与 Python 不同的地方，
还有块语句都是需要用开始和结束标签形成。这样做的好处
是因为静态文本在一个块语句中可能改变缩进数量。

.. _Jinja: http://jinja.pocoo.org/docs/templates/
.. _HTML: https://developer.mozilla.org/docs/Web/HTML


基础图层
---------------

在网络应用中的每个页面会有相同的基础图层包裹着不同的主体内容。
而不是在每个模版中写完整的 HTML 结构，每个模版会 *扩展* 一个
基础模版，然后覆写具体的部分。

.. code-block:: html+jinja
    :caption: ``flaskr/templates/base.html``

    <!doctype html>
    <title>{% block title %}{% endblock %} - Flaskr</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <nav>
      <h1>Flaskr</h1>
      <ul>
        {% if g.user %}
          <li><span>{{ g.user['username'] }}</span>
          <li><a href="{{ url_for('auth.logout') }}">Log Out</a>
        {% else %}
          <li><a href="{{ url_for('auth.register') }}">Register</a>
          <li><a href="{{ url_for('auth.login') }}">Log In</a>
        {% endif %}
      </ul>
    </nav>
    <section class="content">
      <header>
        {% block header %}{% endblock %}
      </header>
      {% for message in get_flashed_messages() %}
        <div class="flash">{{ message }}</div>
      {% endfor %}
      {% block content %}{% endblock %}
    </section>

模版中的 :data:`g` 数据代理对象是自动可用的。然后依据
如果 ``g.user`` 设置的话 (在 ``load_logged_in_user`` 函数中)，
那么用户名和一个登出链接都会显示在页面上，否则显示的是注册和登录链接。
模版中的 :func:`url_for` 也是自动可用的，并且用来生成到视图函数的
URLs 地址，而不是手动写这些地址，不需要硬编码。

在页面标题块语句之后，内容块语句之前，在模版里使用
:func:`get_flashed_messages` 函数，对其返回的
结果进行迭代循环处理，显示每条消息。在视图函数中你使用的
:func:`flash` 函数就是现实这些错误消息用的，并且
在模版中的代码就会把这些闪存消息显示在页面上了。

这里的基础模版里写了3个块语句，在其它模版中都会对其进行覆写：

#.  ``{% block title %}`` 会用来改变浏览器标签和窗口中标题内容。

#.  ``{% block header %}`` 类似标题块语句，但改变的是页面上的标题内容。

#.  ``{% block content %}`` 每个页面中的内容数据都会进入到内容块语句里，
    例如登录表单或一篇博客发表。

这个基础模版直接放在 ``templates`` 子目录中。其它的都不变，
对于一张蓝图的模版来说会放在与蓝图模块名一样的子目录中，模版名
与蓝图视图函数同名。


注册模版
-----------

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/register.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Register{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Register">
      </form>
    {% endblock %}

``{% extends 'base.html' %}`` 扩展块语句告诉 Jinja 引擎注册模版应该
替换基础模版中的块语句。所有翻译的内容必须出现在 ``{% block %}`` 语句中，
这样才可以覆写基础模版中的块语句。

一种有用的模式这里用到了，那就是把 ``{% block title %}`` 放到
``{% block header %}`` 里面。这种方式会设置标题块内容后，把它
的值输出到头部块语句里，这样才能够把相同内容都呈现在窗口和页面上，
不需要写两遍代码。

模版中 ``input`` 标签都适用了 ``required`` 属性做结尾。这就告诉浏览器
不要提交空数据表单，必须要填写数据才可以提交表单。如果用户正在使用一种老旧
的浏览器，那么就不会支持这种新属性功能，或者用户正在使用其它什么来代替浏览器
发送请求的话，你依然想要验证数据，那就还是在 Flask 视图函数中来部署。
在服务器端一直要做完全的验证，这是非常重要的一件事情，即使客户端也做同样的
验证工作也不能忽略。


登录模版
-----------

This is identical to the register template except for the title and
submit button.

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/login.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Log In{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Log In">
      </form>
    {% endblock %}


注册一名新用户
---------------

现在用户授权的模版都写完了，你可以注册一名新用户了。
确保服务器还在运行着 (如果没有的话，执行 ``flask run`` 终端命令)，
然后用浏览器访问 http://127.0.0.1:5000/auth/register 地址。

尝试下不填写表单直接点击注册按钮看看浏览器会现实一个什么样的错误消息？
尝试把输入标签中 ``required`` 属性去掉再点击注册看看会是什么样子？
在浏览器上反而会显示一个错误提示消息，页面会重新加载，错误提示消息来自
授权蓝图中视图函数，由于使用 :func:`flash` 才会在页面中显示错误提示消息。

都填写好用户名和用户密码后注册成功就重定向到登录页面了。
尝试输入一个不正确的用户名，或正确用户名错误密码来看看。
如果你登录页面得到一个错误消息的话，那就是因为我们此时
还没有 ``index`` 视图函数为你重定向。

继续阅读 :doc:`static` 文档内容。
