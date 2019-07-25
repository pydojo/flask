单页网络应用
========================

Flask 可以用来服务单页网络应用 (SPA) ，
通过把你前端框架生成的静态文件放在你项目中的一个子文件夹里。
你也需要建立一个一下获得所有内容的端点，
该端点把所有请求都指向你的 SPA 路径。

下面的例子示范了如何用一个 API 服务一项 SPA 的代码::

    from flask import Flask, jsonify

    app = Flask(__name__, static_folder='app')


    @app.route("/heartbeat")
    def heartbeat():
        return jsonify({"status": "healthy"})


    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")
