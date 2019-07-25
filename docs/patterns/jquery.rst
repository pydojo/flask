使用 jQuery 做 AJAX 工作
=============================

`jQuery`_ 是一个小型 JavaScript 库，
通用中共同用来简化与 DOM 和 JavaScript 一起工作。
通过在服务器和客户端之间交换 JSON 制作更动态的网络应用，
它是一个较好的工具。

JSON 自身是一个非常轻量级的传输格式，非常类似 Python 中的
 (数字、字符串、字典，和列表数据类型），看起来被广泛支持着，
并且非常容易进行语法分析。它变得受欢迎是几年前的事情了，而且
快速代替了网络应用中的 XML 数据传输格式。

.. _jQuery: https://jquery.com/

加载 jQuery
--------------

要使用 jQuery 的话，你要先下载它，然后把它放在你的网络应用静态文件夹中，
然后确保它被加载。理想的方式是你有一个图层模版，该模版给所有页面使用，该
模版只增加一个 HTML 脚本标签，放在 ``<body>`` 标签底部来加载 jQuery 即可：

.. sourcecode:: html

   <script type=text/javascript src="{{
     url_for('static', filename='jquery.js') }}"></script>

另外一个方法是使用 Google 的 `AJAX Libraries API
<https://developers.google.com/speed/libraries/devguide>`_ 来加载 jQuery 库：

.. sourcecode:: html

    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="{{
      url_for('static', filename='jquery.js') }}">\x3C/script>')</script>

在 AJAX 方式中你要把 jQuery 放在你的静态文件夹中作为一项回滚，
但它会先尝试从 Google 直接加载。这种用法的优势是你的站点会正确地
更快为用户加载，如果用户们曾经至少访问过具有相同 jQuery 版本的站点，
那么该版本就已经在浏览器的缓存中了。

我的站点在哪里？
--------------------

你知道你的网络应用在什么地方吗？
如果你正在开发中，答案就非常简单了：
网络应用位于本地服务器端口上，并且直接在服务器根路径上。
但如果你稍后决定把你的网络应用移动到不同的位置上后，又会是什么呢？
例如，移动到 ``http://example.com/myapp`` 位置上？
在服务器端这永远不是一个问题，因为我们正在使用
:func:`~flask.url_for` 函数，该函数可以回答这个问题，
但如果我们正在使用 jQuery 的话，我们不应该把路径硬编码给网络应用，
而是动态编码，所以我们如何才能做到这一点呢？

一个简单的方法会加入到一个 script 标签中，这样我们的页面设置了一个
全局变量作为网络应用根路径的前缀。就像下面代码一样：

.. sourcecode:: html+jinja

   <script type=text/javascript>
     $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
   </script>

其中 ``|safe`` 在 Flask 0.10 以前版本中是必须要有的，
这样 Jinja 不会转义含有 HTML 路由规则的 JSON 编码过的字符串。
常常这个过滤器都是需要的，但我们此时在一个 ``script`` 标签块中，
其中含有不同的规则。

.. admonition:: 给专家提点建议

   在 HTML ``script`` 标签中声明一个 ``CDATA`` 后，
   意味着不会对所有实体进行语法分析。直到 ``</script>``
   关标签中的每项内容都会作为脚本被处理。
   这也意味着在脚本标签中永远不能有任何一个 ``</`` 内容。
   过滤器 ``|tojson`` 在这里足以确保做对事情，并且为你
   转义反斜杠(例如，``{{ "</script>"|tojson|safe }}``
   会翻译成 ``"<\/script>"`` 这个结果)。

   在 Flask 0.10 中它会进一步用 unicode 转义字符来转义
   所有 HTML 标签。这对于 Flask 来说自动化把结果标记成安全
   的 HTML 内容变成可能。


JSON 视图函数
-------------------

现在让我们建立一个服务器端的函数，该函数接收2个数字 URL 参数，
该数字参数应该做加法后以一个 JSON 对象送回给网络应用。
这确实是一个有点可笑的例子，并且这是常常你在客户端来做的事情，
但这个简单的例子说明了你如何使用 jQuery 和 Flask 一起工作::

    from flask import Flask, jsonify, render_template, request
    app = Flask(__name__)

    @app.route('/_add_numbers')
    def add_numbers():
        a = request.args.get('a', 0, type=int)
        b = request.args.get('b', 0, type=int)
        return jsonify(result=a + b)

    @app.route('/')
    def index():
        return render_template('index.html')

如你所见，我也增加了一项 `index` 路由翻译一个模版。
这个模版会加载 jQuery 后有一个小的表单用来做加法，
并且有一个链接来触发服务器端的函数。

注意，我们正在使用 :meth:`~werkzeug.datastructures.MultiDict.get` 方法，
该方法永远不会失败。如果缺少一个键的话，返回一项默认值 (这里是 ``0``)。
更进一步来说，它可以把值转换成一个具体的类型 (就像这里的 `int` 一样)。
这里的代码非常上手，通过一个脚本就能够触发 (APIs，JavaScript 等等。)
因为你不需要描述错误来报告这种情况。

HTML 模版
--------------

你的 `index.html` 模版即要继承自 :file:`layout.html` 模版，
也就含有了加载的 jQuery 和 `$SCRIPT_ROOT` 变量设置内容，
也要写一遍需要的 HTML 代码给我们的小程序 (:file:`index.html`)。
注意，我们这里直接把脚本写在 HTML 模版中。
常常把脚本内容写一个单独的一个脚本文件里是更好的思路：

.. sourcecode:: html

    <script type=text/javascript>
      $(function() {
        $('a#calculate').bind('click', function() {
          $.getJSON($SCRIPT_ROOT + '/_add_numbers', {
            a: $('input[name="a"]').val(),
            b: $('input[name="b"]').val()
          }, function(data) {
            $("#result").text(data.result);
          });
          return false;
        });
      });
    </script>
    <h1>jQuery Example</h1>
    <p><input type=text size=5 name=a> +
       <input type=text size=5 name=b> =
       <span id=result>?</span>
    <p><a href=# id=calculate>calculate server side</a>

这里我不会介绍 jQuery 是如何工作的细节内容，只快速说明一下上的代码片段：

1. ``$(function() { ... })`` 描述的代码应该在浏览器完成加载
   页面的基础部分时只运行一次。
2. ``$('selector')`` 选择一个元素并让你操作这个元素。
3. ``element.bind('event', func)`` 描述了一个函数，该函数
   在用户点击这个元素时来运行。如果函数返回 `false` 值的话，
   默认行为不会出现 (在这里，就导航到 `#` URL地址上)。
4. ``$.getJSON(url, data, func)`` 发送一个 ``GET`` 请求到 `url` 后
   会发送 `data` 对象内容作为查询参数。一旦数据抵达后，
   它会用返回值作为参数来调用给出的函数。注意，我们可以使用
   这里的 `$SCRIPT_ROOT` 变量，它是我们前面设置好的。

检查 :gh:`example source <examples/javascript>` 内容是一个完整的
网络应用示范代码，同时使用了 ``XMLHttpRequest`` 和 ``fetch`` 做了同样的事情。
