.. _uploading-files:

上传文件
===============

是的，文件上传一直是一个好的旧问题。文件上传的基本思路实际上
是非常简单的。它基础工作就像下面所述：

1. 一个 HTML ``<form>`` 标签使用 ``enctype=multipart/form-data``
   标记后把 ``<input type=file>`` 标签放在表单标签里。
2. 网络应用访问文件是从请求对象上的 :attr:`~flask.request.files` 
   属性字典中获得上传的文件。
3. 使用文件的 :meth:`~werkzeug.datastructures.FileStorage.save` 方法
   来把上传的文件保存在文件系统上。

一种绅士般的介绍
---------------------

让我们用一个非常基础的网络应用作为开始，该网络应用上传一个文件到
一个具体的上传文件夹中，然后把这个文件显示给用户。
让我们来看看我们这个网络应用的集成后的代码::

    import os
    from flask import Flask, flash, request, redirect, url_for
    from werkzeug.utils import secure_filename

    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

第一步我们需要一些导入语句。大部分都是直接就明白的，
:func:`werkzeug.secure_filename` 函数稍后解释。
``UPLOAD_FOLDER`` 变量名指向了我们要存储上传文件到地方，
``ALLOWED_EXTENSIONS`` 变量名指向了许可的文件扩展名集合。

为什么我们要限制文件的扩展名呢？
你可能不想让你的用户上传任何东西，如果服务器是直接把数据发送给客户端的话，
确实应该限制一下。那样你可以确保用户都不能上传 HTML 文件，因为 HTML 文件
会导致 XSS 的许多问题（查看 :ref:`xss` 文档内容)。
同样确保不许可上传 ``.php`` 文件，如果服务器执行 php 文件的话，那么是谁
把 PHP 文件安装到服务器上的呢？是吧 :)

第二步，写一些函数来检查扩展名是否是合法的，然后上传文件，接着把用户重定向
到上传文件的 URL 地址上::

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

那么此时 :func:`~werkzeug.utils.secure_filename` 函数真正是做什么的呢？
现在的问题是有一个原则叫作 **永远不要相信人的输入** 。
对于一个上传文件的文件名来说也是成立的。所有提交的表单数据都可以被篡改，
并且文件名都是危险的内容。如果你了解文件的实质，就会认识到这一点。
在这里只需要记住：
在直接存储到文件系统上之前，总要使用函数来对一个文件名进行安全处理。

.. admonition:: 给专家提点建议

   那么你对 :func:`~werkzeug.utils.secure_filename` 函数所做的感兴趣吗？
   如果你不使用这个函数会导致什么问题呢？那么想象一下，某个人发送了如下
    `filename` 信息到你的网络应用::

      filename = "../../../../home/username/.bashrc"

   假设 ``../`` 的使用数量正好，你就会把这个文件加入到 ``UPLOAD_FOLDER`` 
   所指的目录中，这样用户就可能具备了修改不该修改的服务器文件系统上的文件。
   实现这个确实需要一些网络应用长什么样子的知识，但信任我，黑客们都是不急不躁的
   一群家伙 :)

   现在我们来看看这个安全化文件名函数是如何工作的：

   >>> secure_filename('../../../../home/username/.bashrc')
   'home_username_.bashrc'

现在最后一件没说的事情就是：上传文件的服务过程。
在 :func:`upload_file()` 函数中我们把用户
重定向到 ``url_for('uploaded_file', filename=filename)`` 地址上，
那就是 ``/uploads/filename`` 位置上。
那么我们所写的 :func:`uploaded_file` 函数要返回那个名字的文件。
作为 Flask 0.5 版本中，我们可以使用一个函数来为我们实现那个目标::

    from flask import send_from_directory

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)

另一个，我们可以把 `uploaded_file` 注册成 `build_only` 规则，然后使用
 :class:`~werkzeug.wsgi.SharedDataMiddleware` 类。这种方法用较旧的
 Flask 版本也有效::

    from werkzeug import SharedDataMiddleware
    app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                     build_only=True)
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/uploads':  app.config['UPLOAD_FOLDER']
    })

如果你现在运行网络应用，每件事应该如期而至。


改善上传
-----------------

.. versionadded:: 0.6

那么 Flask 是如何处理上传的呢？
如果上传文件都是小型文件的话，会存储在网络服务器的内存中，
否则存储在临时位置上 (与 :func:`tempfile.gettempdir` 返回结果一样)。
但你如何在一个上传终止后描述文件的最大规模呢？
默认情况下，Flask 会高兴地接受一个文件上传到没有内存限制的地方，
但你可以通过设置 ``MAX_CONTENT_LENGTH`` 配置键值来限制::

    from flask import Flask, Request

    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

上面这段代码会限制允许的最大装载量到 16 兆字节。
如果传输一个大于 16 MB 的文件，Flask 会抛出一个
:exc:`~werkzeug.exceptions.RequestEntityTooLarge` 例外。

.. admonition:: 连接重置问题

    当使用本地开发服务器时，你也许得到一个连接重置错误，
    而不是一个 413 响应代号。
    当用一个生产 WSGI 服务器运行网络应用时，你会得到
    正确的状态响应代号。

这个特性已经加入到 Flask 0.6 版本中，但在较旧的版本里也可以实现，
通过请求对象子类化。对于更多的信息咨询 Werkzeug 文件处理文档内容。


上传进度条
--------------------

许久以前许多开发者们都曾经有以许多小车皮形式读取进入的文件思路，
并且把上传进度存储在数据库中，这样能够在客户端上使用
JavaScript 来记录上传进度。长话短说：
客户端每隔5秒向服务器询问已经传输了多少数据。
你认识到这个讽刺了吗？客户端正在问它本来应该知道的事情，
为何多此一举呢！

一个更容易的解决方案
-----------------------

现在有许多更好的解决方案，而且工作起来更快更可信赖。
有许多 JavaScript 库，像 jQuery_ 就有表单插件容易
建立进度条功能。

对于现有的文件上传几乎在所有网络应用中都是使用共性的模式来处理上传任务，
我们也有一个 Flask 扩展件名叫 `Flask-Uploads`_ 部署了一种完全成熟的
上传机制，在扩展名中建立白名单和黑名单，以及更多功能。

.. _jQuery: https://jquery.com/
.. _Flask-Uploads: https://pythonhosted.org/Flask-Uploads/
