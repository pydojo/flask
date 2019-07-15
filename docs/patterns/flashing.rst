.. _message-flashing-pattern:

消息闪存
================

好的网络应用和用户接口都是有关反馈的事情。如果用户无法获得足够的反馈，
他们可能会恨恶那个网络应用不再使用。 Flask 提供了真正的直接方法
用闪存系统把反馈提供给用户。闪存系统基本上尽可能地在一个请求的结束时
记录一条消息，然后且只在下一个请求访问记录的上一条消息。
这常常与一个图层模版来实现。注意浏览器和一些网络服务器在 cookie 大小上
的强制限制。这种限制意味着闪存消息对于会话 cookie 太大的话，会导致
消息闪存默默地失败。

直接闪存
---------------

那么下面是一个完整的示例::

    from flask import Flask, flash, redirect, render_template, \
         request, url_for

    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['username'] != 'admin' or \
                    request.form['password'] != 'secret':
                error = 'Invalid credentials'
            else:
                flash('You were successfully logged in')
                return redirect(url_for('index'))
        return render_template('login.html', error=error)

然后下面是一个HTML语言和Jinja模版语言写的 :file:`layout.html` 模版文件，
该模版展示了魔法效果：

.. sourcecode:: html+jinja

   <!doctype html>
   <title>My Application</title>
   {% with messages = get_flashed_messages() %}
     {% if messages %}
       <ul class=flashes>
       {% for message in messages %}
         <li>{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}
   {% block body %}{% endblock %}

下面是一个 :file:`index.html` 模版文件，
该模版继承自 :file:`layout.html` 模版文件：

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Overview</h1>
     <p>Do you want to <a href="{{ url_for('login') }}">log in?</a>
   {% endblock %}

接下来的 :file:`login.html` 模版文件也继承自
 :file:`layout.html` 模版：

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Login</h1>
     {% if error %}
       <p class=error><strong>Error:</strong> {{ error }}
     {% endif %}
     <form method=post>
       <dl>
         <dt>Username:
         <dd><input type=text name=username value="{{
             request.form.username }}">
         <dt>Password:
         <dd><input type=password name=password>
       </dl>
       <p><input type=submit value=Login>
     </form>
   {% endblock %}

含有分类的闪存
------------------------

.. versionadded:: 0.3

当闪存一条消息时也可以提供分类。如果没有提供分类的话，默认分类是 ``'message'`` 。
另外可选的分类可以给用户提供更好的反馈。例如错误消息可以用红色背景来显示。

要使用不同的分类来闪存一条消息，只使用 :func:`~flask.flash` 函数的第二个参数即可 ::

    flash(u'Invalid password provided', 'error')

在模版中你就要告诉 :func:`~flask.get_flashed_messages` 函数也要返回分类信息。
此时模版中的循环语句就稍有不同了：

.. sourcecode:: html+jinja

   {% with messages = get_flashed_messages(with_categories=true) %}
     {% if messages %}
       <ul class=flashes>
       {% for category, message in messages %}
         <li class="{{ category }}">{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}

这就是一个如何翻译闪存消息的例子。有一种用法也可以增加标签给消息，
例如 ``<strong>Error:</strong>`` 。

过滤闪存消息
------------------------

.. versionadded:: 0.9

你可以有选择地把一个分类列表代入其中，这样就可以过滤
 :func:`~flask.get_flashed_messages` 函数的结果。
如果你希望把每个分类翻译到分块部分中这是有用的。

.. sourcecode:: html+jinja

    {% with errors = get_flashed_messages(category_filter=["error"]) %}
    {% if errors %}
    <div class="alert-message block-message error">
      <a class="close" href="#">×</a>
      <ul>
        {%- for msg in errors %}
        <li>{{ msg }}</li>
        {% endfor -%}
      </ul>
    </div>
    {% endif %}
    {% endwith %}
