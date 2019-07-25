流化内容
==================

有时候你想要把数据内容一项一项发送给客户端，要比保存到内存中更好。
当你们生成这样的数据时，你如何把数据送回客户端而不在文件系统上产生往返操作呢？

答案就是使用生成器和直接响应对象。

基础用法
-----------

这是一个基础视图函数，用来生成一项一项的大量 CSV 数据。
技巧就是有一个封装函数，该函数使用一个生成器来产生数据，
并且稍后引入封装函数在把封装函数代入到一个响应对象中去::

    from flask import Response

    @app.route('/large.csv')
    def generate_large_csv():
        def generate():
            for row in iter_all_rows():
                yield ','.join(row) + '\n'
        return Response(generate(), mimetype='text/csv')

每个 ``yield`` 表达式都直接发送到浏览器。注意，
有的 WSGI 中间件也许会破坏数据流，所以在调试环境中
此处要小心，要使用侧写器和其它可以开启的工具。

来自模版的数据流
------------------------

在 Jinja2 模版引擎中也支持把模版翻译成一段一段。
这个功能没有被 Flask 直接曝光给用户，因为这不是
非常共性的技术，但你可以自己容易地实现它::

    from flask import Response

    def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        rv.enable_buffering(5)
        return rv

    @app.route('/my-large-page.html')
    def render_large_template():
        rows = iter_all_rows()
        return Response(stream_template('the_template.html', rows=rows))

这里的技巧是从网络应用上的 Jinja2 环境里获得模版对象，然后
调用 :meth:`~jinja2.Template.stream` 方法，而不是调用
:meth:`~jinja2.Template.render` 方法，这样用返回一个
数据流对象来代替一个字符串。由于我们搭桥在 Flask 翻译模版函数
和使用模版对象自身，所以我们要自己通过调用
:meth:`~flask.Flask.update_template_context` 方法来确保
更新翻译语境。模版稍后才评估成迭代的流化对象。由于每次你都执行
一次 `yield` 语句，服务器会把内容流向客户端，你可能想要在
模版中缓存几次，那么你可以使用 ``rv.enable_buffering(size)``
方法，其中的参数值 ``5`` 是一种正常的默认缓存值。

使用语境来流化
----------------------

.. versionadded:: 0.9

注意，当你流化数据时，请求语境在函数执行时已经消失。
Flask 0.9 提供了一个助手给你，它可以把请求语境保存
在生成器执行期间::

    from flask import stream_with_context, request, Response

    @app.route('/stream')
    def streamed_response():
        def generate():
            yield 'Hello '
            yield request.args['name']
            yield '!'
        return Response(stream_with_context(generate()))

没有 :func:`~flask.stream_with_context` 函数的话，你会得到一个
:class:`RuntimeError` 运行错误。
