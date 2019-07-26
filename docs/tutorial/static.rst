静态文件
============

授权蓝图中的视图函数和模版都工作起来了，
但此时它们看起来还很是纯文本样式。
一些 `CSS`_ 语言可以增加样式给 HTML 中已建立的图层。
样式文件依然是一种 *静态* 文件，根一个模版一样。

Flask 自动增加一个 ``static`` 视图函数，该函数会得到
相关于 ``flaskr/static`` 子目录的路径并服务这个文件夹。
其中 ``base.html`` 模版里已经有了一个到 ``style.css`` 文件的链接：

.. code-block:: html+jinja

    {{ url_for('static', filename='style.css') }}

除了 CSS 外，其它类型的静态文件可以含有 JavaScript 函数，
或者一个图标图片。这些都要放在 ``flaskr/static`` 目录下，
然后用 ``url_for('static', filename='...')`` 来指向。

本部分教程内容不关注在如何写 CSS 文件，所以你可以把下面的
CSS 语言复制到 ``flaskr/static/style.css`` 文件里：

.. code-block:: css
    :caption: ``flaskr/static/style.css``

    html { font-family: sans-serif; background: #eee; padding: 1rem; }
    body { max-width: 960px; margin: 0 auto; background: white; }
    h1 { font-family: serif; color: #377ba8; margin: 1rem 0; }
    a { color: #377ba8; }
    hr { border: none; border-top: 1px solid lightgray; }
    nav { background: lightgray; display: flex; align-items: center; padding: 0 0.5rem; }
    nav h1 { flex: auto; margin: 0; }
    nav h1 a { text-decoration: none; padding: 0.25rem 0.5rem; }
    nav ul  { display: flex; list-style: none; margin: 0; padding: 0; }
    nav ul li a, nav ul li span, header .action { display: block; padding: 0.5rem; }
    .content { padding: 0 1rem 1rem; }
    .content > header { border-bottom: 1px solid lightgray; display: flex; align-items: flex-end; }
    .content > header h1 { flex: auto; margin: 1rem 0 0.25rem 0; }
    .flash { margin: 1em 0; padding: 1em; background: #cae6f6; border: 1px solid #377ba8; }
    .post > header { display: flex; align-items: flex-end; font-size: 0.85em; }
    .post > header > div:first-of-type { flex: auto; }
    .post > header h1 { font-size: 1.5em; margin-bottom: 0; }
    .post .about { color: slategray; font-style: italic; }
    .post .body { white-space: pre-line; }
    .content:last-child { margin-bottom: 0; }
    .content form { margin: 1em 0; display: flex; flex-direction: column; }
    .content label { font-weight: bold; margin-bottom: 0.5em; }
    .content input, .content textarea { margin-bottom: 1em; }
    .content textarea { min-height: 12em; resize: vertical; }
    input.danger { color: #cc2f2e; }
    input[type=submit] { align-self: start; min-width: 10em; }

你可以在 :gh:`example code <examples/tutorial/flaskr/static/style.css>`
中找到更松散的一种 CSS 样式内容。

现在刷新 http://127.0.0.1:5000/auth/login 地址后你就看到像下面截图一样的页面风格了。

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

你可以从 `Mozilla's documentation <CSS_>`_ 上阅读更多有关 CSS 的内容。
如果你改变了 CSS 文件内容，刷新网页就可以看到新样式效果。
如果没有显示新风格的话，尝试清空你的浏览器缓存再看看。

.. _CSS: https://developer.mozilla.org/docs/Web/CSS

继续阅读 :doc:`blog` 文档内容。
