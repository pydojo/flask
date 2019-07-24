Celery 背景任务
=======================

如果你的网络应用有一种长时间运行的任务，例如处理上传的数据或发送邮件，
你不想在发送一个这样的请求期间一直盯着等待完成。那么就使用一个任务列队
来发送需要的数据给另一个进程，该进程会在背景中运行任务，同时请求立即返回。

Celery 是一个强力的任务列队库，可以用来直接背景化众多任务，也用在多层化
多阶段程序与计划上。本指导会为你展示如何使用 Flask 配置 Celery 库，
但需要你先阅读完 Celery 文档中的此篇指导内容：
`First Steps with Celery <https://celery.readthedocs.io/en/latest/getting-started/first-steps-with-celery.html>`_

安装
-------

Celery 是一个单独的 Python 包。使用 pip 从 PyPI 来安装::

    $ pip install celery

配置
---------

你需要的第一个东西就是一个 Celery 实例，它会叫做 celery 应用。
它就像 Flask 中 :class:`~flask.Flask` 对象一样提供服务，
只不过是为 Celery 而有。因此这个实例就是你在 Celery 中所做的
每一件事的入口点，例如建立任务和管理工作器，该实例必须能被其它
模块导入。

对于实例来说，你可以放在一个名叫 ``tasks`` 模块文件中。同时你可以
使用 Celery 时不需要用 Flask 进行任何二次配置，通过子类化任务就
变得有点不错哦，并且增加了对 Flask 网络应用语境的支持，以及用钩子
把 Flask 配置联系在一起。

如下就是正确地用 Flask 集成 Celery 的全部所需代码::

    from celery import Celery

    def make_celery(app):
        celery = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask
        return celery

这个函数建立了一个新的 Celery 对象，用网络应用配置属性作为消息代理
配置该对象，从 Flask 网络应用配置更新 Celery 应用配置，然后建立
一个任务子类，该子类把任务执行打包在一个网络应用语境中。

一个任务示例
---------------

让我们来写一个任务，该任务是做两个数字的加法，然后返回结果。
我们配置 Celery 的消息代理和后端是用了 Redis 库，
建立一个 ``celery`` 应用使用上面的函数，然后用这个应用定义任务。 ::

    from flask import Flask

    flask_app = Flask(__name__)
    flask_app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    celery = make_celery(flask_app)

    @celery.task()
    def add_together(a, b):
        return a + b

这个任务现在可以在背景里调用了::

    result = add_together.delay(23, 42)
    result.wait()  # 65

运行一个工作器
------------------

如果你已经进入并执行上面的代码，你会感到失望，
学会 ``.wait()`` 方法从来不返回实际内容。
那是因为你还需要运行一个 Celery 工作器来接收
并执行任务。 ::

    $ celery -A your_application.celery worker

这里的 ``your_application`` 指的是建立 ``celery``
对象代码所在的应用包或模块名。

执行完这个终端命令，工作器就运行起来了， ``wait`` 方法
一旦任务完成就返回结果。
