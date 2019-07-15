.. _logging:

日志
=======

Flask 使用了标准的 Python :mod:`logging` 模块。所有与 Flask 相关的消息
都记录在 ``'flask'`` 日志器命名空间里。
:meth:`Flask.logger <flask.Flask.logger>` 方法返回日志器名字
 ``'flask.app'`` 后可以用来记录你的网络应用消息。 ::

    @app.route('/login', methods=['POST'])
    def login():
        user = get_user(request.form['username'])

        if user.check_password(request.form['password']):
            login_user(user)
            app.logger.info('%s logged in successfully', user.username)
            return redirect(url_for('index'))
        else:
            app.logger.info('%s failed to log in', user.username)
            abort(401)


基础配置
-------------------

当你想要为你的项目配置日志时，你应该在程序启动时尽可能实现完。
如果在日志配置完之前访问了 :meth:`app.logger <flask.Flask.logger>` 方法，
它会增加一个默认处理器。如果可能的话，在建立网络应用对象之前就完成配置日志工作。

本示例使用了 :func:`~logging.config.dictConfig` 函数来建立一个日志配置，
类似 Flask 的默认配置，不包括所有的日志记录项::

    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)


默认配置
`````````````````````

如果你自己不做配置日志的话， Flask 会自动把一个
:class:`~logging.StreamHandler` 类增加到 :meth:`app.logger <flask.Flask.logger>`
 方法上。在请求期间，它会写到由 WSGI 服务器所描述的 ``environ['wsgi.errors']`` 流里去
 （它常常是 :data:`sys.stderr` 数据流）。)
 在请求以外，它会记录到 :data:`sys.stderr` 数据流中。


移除默认的处理器
````````````````````````````

如果你在访问 :meth:`app.logger <flask.Flask.logger>` 方法之后配置日志的话，
那么需要移除默认的处理器，你可以导入后移除它::

    from flask.logging import default_handler

    app.logger.removeHandler(default_handler)


用邮件发送错误信息给管理员
------------------------------

当为生产在一台远程服务器上运行网络应用时，你可能无法经常看到日志消息。
也许 WSGI 服务器会把日志消息发送到一个文件中去，
然后如果一名用户告诉你有什么错误时，你只可以检查那个日志文件。

要想主动发现并修复 bugs 的话，你可以配置一个
 :class:`logging.handlers.SMTPHandler` 类在
错误和更高级别的日志记录完时发送邮件。 ::

    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost='127.0.0.1',
        fromaddr='server-error@example.com',
        toaddrs=['admin@example.com'],
        subject='Application Error'
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if not app.debug:
        app.logger.addHandler(mail_handler)

发送邮件需要你有一个 SMTP 服务器配置在相同服务器上。
查看 Python 文档了解关于配置处理器的更多信息。


注射请求信息
-----------------------------

关于请求的更多信息，例如 IP 地址，也许帮助调试一些错误。
你可以建立一个 :class:`logging.Formatter` 类的子类来
注射你自己的区域，这样你自己的区域可以用在消息中。
你可以自定义 Flask 默认处理器的格式化器，
定义在上面的邮件处理器，或者任何其它一个处理器。::

    from flask import request
    from flask.logging import default_handler

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    default_handler.setFormatter(formatter)
    mail_handler.setFormatter(formatter)


其它库
---------------

其它的库也许用来扩展日志功能，并且你也想要看到来自那些日志的相关消息。
最简单的方法就是增加处理器到根日志器，而不是只增加到网络应用日志器中。 ::

    from flask.logging import default_handler

    root = logging.getLogger()
    root.addHandler(default_handler)
    root.addHandler(mail_handler)

根据你的项目，分别配置每个你在意的日志器也许更有用，
而不是只配置根日志器 ::

    for logger in (
        app.logger,
        logging.getLogger('sqlalchemy'),
        logging.getLogger('other_package'),
    ):
        logger.addHandler(default_handler)
        logger.addHandler(mail_handler)


Werkzeug
````````

Werkzeug 把基础的请求/响应信息记录到 ``'werkzeug'`` 日志器。
如果根日志器没有处理器配置的话， Werkzeug 会增加一个
 :class:`~logging.StreamHandler` 类处理器。


Flask 扩展
````````````````

根据情况来定，一个扩展也许选择记录日志到
 :meth:`app.logger <flask.Flask.logger>` 方法上，或者记录到自己命名的日志器上。
咨询每个扩展的文档了解细节。
