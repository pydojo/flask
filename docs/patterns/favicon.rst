增加一个图标
================

一个图标就是浏览器用来为标签和书签来显示的一个图标。
这有助于区分你的网站并让你的站点有了唯一的品牌。

一个共性的问题就是如何给一个 Flask 网络应用增加一个图标。
当然首先你得有一个图标文件。它应该是 16 × 16 像素大小，
并且文件格式是 ICO 类型。这虽然不是一项需求，但所有浏览器都支持的标准。
把图标文件放在你的静态目录中，保存成 :file:`favicon.ico` 文件名。

此时你用浏览器访问你的站点就有了图标显示出来了，正确的方式是要在你的
HTML 页面中增加一个 link 标签。那么示例如下：

.. sourcecode:: html+jinja

    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

对于大多数浏览器就是这样部署，不管如何做到的，有些老旧浏览器不支持这种标准。
有的老旧标准服务这种图标文件时，要在网站的根路径下放置文件。
如果你的网络应用没有挂载到域名的根路径上，你既可以配置网络服务器提供
位于根路径上的图标文件服务，或者可以不这样做。不管如何做到的，如果你的网络应用
就是需要根路径的话，你可以直接用一个重定向到图标文件::

    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))

如果你想要保存额外的重定向请求的话，你也可以写一个视图函数，
使用 :func:`~flask.send_from_directory` 函数来实现::

    import os
    from flask import send_from_directory

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

我们可以不明确媒体类型参数，然后它会去猜，但我们描述了，这是为了避免没必要的猜测，
这样会一直保持相同的图标类型。

上面的这种部署会通过你的网络应用来服务图标文件，并且如果可能的话，用网络服务器来配置图标服务更好；
参考网络服务器的文档内容。

也要查看
----------

* 维基百科 `Favicon <https://en.wikipedia.org/wiki/Favicon>`_ 关于图标的文章。
