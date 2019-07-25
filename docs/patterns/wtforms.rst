使用 WTForms 进行表单验证
============================

当你要与一个浏览器提交的表单数据一起工作时，
代码很快变得非常难于阅读。这里有一些库设计成
让这种处理更容易管理。其中一个就是 `WTForms`_ ，
它就是我们这里要介绍的。如果你发现自己处于大量
表单环境中的话，你也许想要试一下这个表单库。

当你与 WTForms 一起工作的时候，你先要把你的表单
定义成类。我建议把网络应用分解成许多模块
(:ref:`larger-applications`) 来做表单工作，
然后把许多表单增加成一个单独模块。

.. admonition:: 用一个扩展件就获得大部分 WTForms 功能

   扩展件 `Flask-WTF`_ 扩展了这种工作模式，并且增加了
   几个助手来完成表单工作，以及让 Flask 更加好玩了。
   你可以从 `PyPI
   <https://pypi.org/project/Flask-WTF/>`_ 上得到它。

.. _Flask-WTF: https://flask-wtf.readthedocs.io/en/stable/

表单
---------

对于一个典型的注册页面来说，如下是一个表单示例::

    from wtforms import Form, BooleanField, StringField, PasswordField, validators

    class RegistrationForm(Form):
        username = StringField('Username', [validators.Length(min=4, max=25)])
        email = StringField('Email Address', [validators.Length(min=6, max=35)])
        password = PasswordField('New Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
        confirm = PasswordField('Repeat Password')
        accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

在视图函数中使用表单
-------------------------

在视图函数中使用上面表单示例的用法如下::

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User(form.username.data, form.email.data,
                        form.password.data)
            db_session.add(user)
            flash('Thanks for registering')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

注意，我们此处的视图函数暗示了正在使用 SQLAlchemy 数据库
(:ref:`sqlalchemy-pattern`)，当然这不是一项需求。只是
为了适合代码的需要。

要记住的事情：

1. 如果数据提交是通过 HTTP 的 ``POST`` 方法，
   从请求 :attr:`~flask.request.form` 属性值来建立表单；
   如果数据提交是通过 ``GET`` 请求方法，
   从请求 :attr:`~flask.request.args` 属性值来建立表单。
2. 要验证表单提交的数据，调用 :func:`~wtforms.form.Form.validate`
   函数，如果数据通过验证，该方法会返回 ``True`` ，否则返回 ``False`` 值。
3. 要从表单逐个访问数据值，通过 `form.<NAME>.data` 来获得。

模版中的表单
------------------

现在来看看模版这边情况。当你把表单代入到模版中的时候，
你可以容易翻译它们。看看下面的模版例子就明白这有多容易了。
WTForms 库已经为我们实现了表单生成的一半工作。
要让表单工作更好一点，我们可以写一种宏命令，让宏来翻译
一个含有标签的区域，如果有任何错误就会列出错误信息。

下面的例子 :file:`_formhelpers.html` 模版文件就包含这样一个宏命令：

.. sourcecode:: html+jinja

    {% macro render_field(field) %}
      <dt>{{ field.label }}
      <dd>{{ field(**kwargs)|safe }}
      {% if field.errors %}
        <ul class=errors>
        {% for error in field.errors %}
          <li>{{ error }}</li>
        {% endfor %}
        </ul>
      {% endif %}
      </dd>
    {% endmacro %}

这个宏接收了一组关键字参数，这些关键字参数都直接来自
WTForm 库的 `field` 函数，它负责把区域翻译给我们。
关键字参数会插入成 HTML 属性。那么例如，你可以调用
 ``render_field(form.username, class='username')`` 
来给 `input` 标签增加一个 `class` 值。
注意， WTForms 库返回标准的 Python unicode 字符串，
所以我们要告诉 Jinja2 这个数据是已经使用 ``|safe`` 过滤器
转义过的 HTML 字符串。

下面的 :file:`register.html` 模版是针对我们使用的视图函数，
本模版从 :file:`_formhelpers.html` 模版中获得了宏命令优势：

.. sourcecode:: html+jinja

    {% from "_formhelpers.html" import render_field %}
    <form method=post>
      <dl>
        {{ render_field(form.username) }}
        {{ render_field(form.email) }}
        {{ render_field(form.password) }}
        {{ render_field(form.confirm) }}
        {{ render_field(form.accept_tos) }}
      </dl>
      <p><input type=submit value=Register>
    </form>

对于更多关于 WTForms 库的信息，回顾 `WTForms website`_ 官方站点。

.. _WTForms: https://wtforms.readthedocs.io/
.. _WTForms website: https://wtforms.readthedocs.io/
