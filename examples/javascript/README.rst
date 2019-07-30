JavaScript Ajax 示例
=======================

示范如何发布表单数据后如何使用 JavaScript 处理一个 JSON 响应对象。
这就让制作请求时不用从页面上来实现导航。
示范中使用了 |XMLHttpRequest|_、 |fetch|_ 和 |jQuery.ajax|_ 内容。
查看 `Flask docs`_ 了解 jQuery 和 Ajax 内容。

.. |XMLHttpRequest| replace:: ``XMLHttpRequest``
.. _XMLHttpRequest: https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest

.. |fetch| replace:: ``fetch``
.. _fetch: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/fetch

.. |jQuery.ajax| replace:: ``jQuery.ajax``
.. _jQuery.ajax: https://api.jquery.com/jQuery.ajax/

.. _Flask docs: http://flask.pocoo.org/docs/patterns/jquery/


安装
-------

::

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -e .


运行
------

::

    $ export FLASK_APP=js_example
    $ flask run

Open http://127.0.0.1:5000 in a browser.


测试
------

::

    $ pip install -e '.[test]'
    $ coverage run -m pytest
    $ coverage report
