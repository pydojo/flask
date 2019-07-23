.. _templates:

模版化
=========

Flask 把 Jinja2 作为模版引擎。你们显然可以自由地使用一个不同的模版引擎，
但你们依然会安装 Jinja2 来运行 Flask 自身程序。此项需求是需要开启丰富
扩展件的条件。一个扩展件可以依据 Jinja2 来呈现。

本文档部分是只对 Jinja2 如何集成到 Flask 上的一次非常快速的介绍。
如果你想了解模版引擎自身句法的信息，回顾官方 `Jinja2 模版文档
 <http://jinja.pocoo.org/docs/templates>`_ 了解更多信息。

安装 Jinja
-----------

除了自定义以外， Jinja2 是由 Flask 进行配置，如同下面一样：

-   为所有以 ``.html`` 结尾的模版开启自动化转义，当使用
    :func:`~flask.templating.render_template` 函数的时候，
    也支持以 ``.htm``, ``.xml`` 和 ``.xhtml`` 结尾的模版。
-   当使用 :func:`~flask.templating.render_template_string` 
    函数的时候，为所有字符串开启自动化转义。
-   使用 ``{% autoescape %}`` 标签让一个模版具有对输入/输出内容
    进行自动化转义的能力。
-   Flask 把两个全局函数和助手函数插入到 Jinja2 语境中，
    另外默认呈现那些函数值。

标准语境
----------------

如下全局变量都是默认用在 Jinja2 模版中：

.. data:: config
   :noindex:

   当前的配置对象 (:data:`flask.config`)

   .. versionadded:: 0.6

   .. versionchanged:: 0.10
      现在这个全局变量会一直可用，甚至在导入的模版中也是一样。

.. data:: request
   :noindex:

   当前的请求对象 (:class:`flask.request`)。如果模版没有用一个激活的请求语境
   进行翻译的话，这个全局变量是不可用的。

.. data:: session
   :noindex:

   当前的会话对象 (:class:`flask.session`)。如果模版没有用一个激活的请求语境
   进行翻译的话，这个全局变量是不可用的。

.. data:: g
   :noindex:

   为全局变量而绑定了请求的对象 (:data:`flask.g`)。如果模版没有用一个激活的请求语境
   进行翻译的话，这个全局变量是不可用的。

.. function:: url_for
   :noindex:

   该 :func:`flask.url_for` 函数。

.. function:: get_flashed_messages
   :noindex:

   该 :func:`flask.get_flashed_messages` 函数。

.. admonition:: Jinja 语境行为

   这里的变量都是加入到变量语境中，这些变量都不是全局变量。
   不同之处在于这些变量默认不会显示在导入的模版语境中。
   这样做一部分是考虑性能，一部分是要保持明确使用的理念。

   那么对你来说这意味着什么呢？如果你由一个宏命令要导入的话，
   要访问请求对象你有2种可能：

   1.   你明确地把请求对象代入到宏命令中作为参数，或者代入
        你感兴趣的请求对象属性。
   2.   你要用语境来导入宏命令。

   用语境导入看起来像下面这样使用：

   .. sourcecode:: jinja

      {% from '_helpers.html' import my_macro with context %}

标准过滤器
----------------

这些过滤器都是在 Jinja2 中可以使用的，另外过滤器都是由 Jinja2 自身提供的：

.. function:: tojson
   :noindex:

   这个函数把给出的对象转换成 JSON 表现形式。如果你尝试生成 JavaScript 脚本的话，
   该函数是非常有帮助的。

   .. sourcecode:: html+jinja

       <script type=text/javascript>
           doSomethingWith({{ user.username|tojson }});
       </script>

   在 HTML 属性中采用 *单引号* 包裹处理， `|tojson` 的输出结果才是安全的用法：

   .. sourcecode:: html+jinja

       <button onclick='doSomethingWith({{ user.username|tojson }})'>
           Click me
       </button>

   注意在 Flask 0.10 版本以前，如果在 ``script`` 标签中使用 ``|tojson`` 输出
   结果的话，确保使用 ``|safe`` 来禁用转义。
   在 Flask 0.10 以后和上面的示例代码中，已经自动禁用转义了。

控制自动转义
------------------------

自动转义是为你自动化转义特殊字符的概念。特殊字符在 HTML 中（或在 XML 和 XHTML 里）
都是 ``&``, ``>``, ``<``, ``"`` 和 ``'`` 这些字符。因为这些字符在文档里自身带有
具体的意思，如果你想要把这些特殊字符用做文本内容的话，你就要用名叫实体的形式来替换它们。
不这样做的话，在文本中就显示不了这些文字形式，只会让用户感到失望，同时也会导致安全问题。
（查看 :ref:`xss` 参考文档）

有时候不管如何做到的，你会需要在模版中禁用自动转义。如果你想要在页面上显示 HTML 代码
作为内容的话，这就是一种情况。那么例如如果这些 HTML 代码来自一个生成安全 HTML 代码的
系统，就像 markdown 这种 HTML 转换器一样，那就需要禁用自动转义了。

这里有3个方法来实现：

-   在 Python 代码里，把 HTML 字符串打包在一个 :class:`~flask.Markup` 类对象中，
    然后再代入到模版里。这是通用中建议的方法。
-   在模版中，使用 ``|safe`` 过滤器来明确地把一个字符串标记成安全的 HTML 内容，即
     (``{{ myvariable|safe }}``)
-   临时完全禁用自动转义系统。

要在模版中禁用自动转义系统，你可以使用 ``{% autoescape %}`` 块语句：

.. sourcecode:: html+jinja

    {% autoescape false %}
        <p>autoescaping is disabled here
        <p>{{ will_not_be_escaped }}
    {% endautoescape %}

不管什么时候你这样做，请非常小心在这个块语句里你使用的变量。

.. _registering-filters:

注册过滤器
-------------------

如果你想要注册你自己的过滤器到 Jinja2 中的话，你有2种方法来实现。
你既可以手动把过滤器放到网络应用的
:attr:`~flask.Flask.jinja_env` 属性里，也可以使用
:meth:`~flask.Flask.template_filter` 方法装饰器。

下面的2个例子都是相同的工作在反向操作一个对象上::

    @app.template_filter('reverse')
    def reverse_filter(s):
        return s[::-1]

    def reverse_filter(s):
        return s[::-1]
    app.jinja_env.filters['reverse'] = reverse_filter

在装饰器用法中，如果你想要使用函数名作为过滤器名的话，参数是可选项。
一旦完成注册的话，你可以在你的模版中使用你自己的过滤器了，用法与
Jinja2 的内置过滤器用法一样，例如，如果你有一个 Python 列表在
语境中叫做 `mylist` 的话，那么用起来就是::

    {% for x in mylist | reverse %}
    {% endfor %}


语境处理器
------------------

要把新的变量自动注射到一个模版的语境中，语境处理器会出现在 Flask 中。
语境处理器的运行要在模版被翻译之前，这样才有能力把新变量注射到模版语境中。
一个语境处理器就是一个函数，该函数要返回一个字典。
字典键和值都稍后与模版语境内容合并在一起，对于网络应用中的所有模版来说::

    @app.context_processor
    def inject_user():
        return dict(user=g.user)

上面这个语境处理器在模版中建立了一个名叫 `user` 的变量，变量值是 `g.user` 。
这个例子不是非常有意思，因为 `g` 在模版中会一直可用，但此处的例子让我们认识了
语境处理器是如何工作的。

变量的值是不受限制的；一个语境处理器也可以用来建立函数作为值给模版使用（因为
Python 允许代入函数）::

    @app.context_processor
    def utility_processor():
        def format_price(amount, currency=u'€'):
            return u'{0:.2f}{1}'.format(amount, currency)
        return dict(format_price=format_price)

上面这个语境处理器让所有模版可以使用建立的 `format_price` 函数::

    {{ format_price(0.33) }}

你也可以把 `format_price` 函数建立成一个模版过滤器（查看
:ref:`registering-filters` 参考内容），但这里示范的是
如何把函数代入到一个语境处理器中。
