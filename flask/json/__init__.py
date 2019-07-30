# -*- coding: utf-8 -*-
"""
flask.json
~~~~~~~~~~

:copyright: © 2010 by the Pallets team.
:license: BSD, see LICENSE for more details.
"""
import codecs
import io
import uuid
from datetime import date, datetime
from flask.globals import current_app, request
from flask._compat import text_type, PY2

from werkzeug.http import http_date
from jinja2 import Markup

# Use the same json implementation as itsdangerous on which we
# depend anyways.
from itsdangerous import json as _json


# Figure out if simplejson escapes slashes.  This behavior was changed
# from one version to another without reason.
_slash_escape = '\\/' not in _json.dumps('/')


__all__ = ['dump', 'dumps', 'load', 'loads', 'htmlsafe_dump',
           'htmlsafe_dumps', 'JSONDecoder', 'JSONEncoder',
           'jsonify']


def _wrap_reader_for_text(fp, encoding):
    if isinstance(fp.read(0), bytes):
        fp = io.TextIOWrapper(io.BufferedReader(fp), encoding)
    return fp


def _wrap_writer_for_text(fp, encoding):
    try:
        fp.write('')
    except TypeError:
        fp = io.TextIOWrapper(fp, encoding)
    return fp


class JSONEncoder(_json.JSONEncoder):
    """默认的 Flask JSON 编码器。该编码器通过支持 ``datetime`` 对象、
    ``UUID`` 和 ``Markup`` 对象扩展了默认的 simplejson 编码器。
    ``Markup`` 对象都是序列化成 RFC 822 日期时间字符串（这样与 HTTP
    的日期格式就一样了）。为了支持更多数据类型，覆写了 :meth:`default` 方法。
    """

    def default(self, o):
        """部署这个方法是以一个子类形式实现的，这样它为 ``o`` 返回一个可序列化对象，
        或者调用基础部署（会抛出一个 :exc:`TypeError` 例外类型）。

        例如，要支持任意迭代器，你可以把 default 部署成如下这样::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        if isinstance(o, datetime):
            return http_date(o.utctimetuple())
        if isinstance(o, date):
            return http_date(o.timetuple())
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, '__html__'):
            return text_type(o.__html__())
        return _json.JSONEncoder.default(self, o)


class JSONDecoder(_json.JSONDecoder):
    """默认的 JSON 解码器。没有改变默认的 simplejson 解码器行为。
    参考 :mod:`json` 模块文档了解更多信息。
    本解码器不仅给本模块的 `load` 函数使用，也给 :attr:`~flask.Request` 使用。
    """


def _dump_arg_defaults(kwargs):
    """把默认参数注射给 `dumps` 和 `dump` 函数."""
    if current_app:
        bp = current_app.blueprints.get(request.blueprint) if request else None
        kwargs.setdefault(
            'cls',
            bp.json_encoder if bp and bp.json_encoder
                else current_app.json_encoder
        )

        if not current_app.config['JSON_AS_ASCII']:
            kwargs.setdefault('ensure_ascii', False)

        kwargs.setdefault('sort_keys', current_app.config['JSON_SORT_KEYS'])
    else:
        kwargs.setdefault('sort_keys', True)
        kwargs.setdefault('cls', JSONEncoder)


def _load_arg_defaults(kwargs):
    """把默认参数注射给 `loads` 和 `load` 函数."""
    if current_app:
        bp = current_app.blueprints.get(request.blueprint) if request else None
        kwargs.setdefault(
            'cls',
            bp.json_decoder if bp and bp.json_decoder
                else current_app.json_decoder
        )
    else:
        kwargs.setdefault('cls', JSONDecoder)


def detect_encoding(data):
    """检测使用哪种 UTF 编码给已知的字节编码。

    最新的 JSON 标准 (:rfc:`8259`) 建议了只接受 UTF-8 这种类型。
    老旧的文档介绍允许使用 8、 16 或 32 类型。而 16 和 32 可以作为
    大字节序或小字节序。有的编辑器或库也许增加了一个 BOM 信息。

    :param data: 未知的 UTF 编码字节。
    :return: UTF 编码名
    """
    head = data[:4]

    if head[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'

    if b'\x00' not in head:
        return 'utf-8'

    if head in (codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE):
        return 'utf-32'

    if head[:2] in (codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE):
        return 'utf-16'

    if len(head) == 4:
        if head[:3] == b'\x00\x00\x00':
            return 'utf-32-be'

        if head[::2] == b'\x00\x00':
            return 'utf-16-be'

        if head[1:] == b'\x00\x00\x00':
            return 'utf-32-le'

        if head[1::2] == b'\x00\x00':
            return 'utf-16-le'

    if len(head) == 2:
        return 'utf-16-be' if head.startswith(b'\x00') else 'utf-16-le'

    return 'utf-8'


def dumps(obj, **kwargs):
    """把 ``obj`` 序列化成一个 JSON 格式的 ``str`` 。
    如果在堆栈上有一个网络应用的话，
    使用网络应用的配置编码器 (:attr:`~flask.Flask.json_encoder`) 。

    本函数可以返回 ``unicode`` 字符串或返回只有 ASCII 内容的字节字符串，
    默认情况自动强制成 unicode 字符串。这种默认行为是通过 ``JSON_AS_ASCII``
    配置变量来控制的，并且可以通过 simplejson 的 ``ensure_ascii`` 参数来覆写。
    """
    _dump_arg_defaults(kwargs)
    encoding = kwargs.pop('encoding', None)
    rv = _json.dumps(obj, **kwargs)
    if encoding is not None and isinstance(rv, text_type):
        rv = rv.encode(encoding)
    return rv


def dump(obj, fp, **kwargs):
    """类似 :func:`dumps` 函数，但写成了一个文件对象."""
    _dump_arg_defaults(kwargs)
    encoding = kwargs.pop('encoding', None)
    if encoding is not None:
        fp = _wrap_writer_for_text(fp, encoding)
    _json.dump(obj, fp, **kwargs)


def loads(s, **kwargs):
    """把一个字符串 ``s`` 加载成非序列化的 JSON 对象 。
    如果在堆栈上有一个网络应用的话，
    使用网络应用的配置解码器 (:attr:`~flask.Flask.json_decoder`) 。
    """
    _load_arg_defaults(kwargs)
    if isinstance(s, bytes):
        encoding = kwargs.pop('encoding', None)
        if encoding is None:
            encoding = detect_encoding(s)
        s = s.decode(encoding)
    return _json.loads(s, **kwargs)


def load(fp, **kwargs):
    """类似 :func:`loads` 函数，但从一个文件对象来读取内容."""
    _load_arg_defaults(kwargs)
    if not PY2:
        fp = _wrap_reader_for_text(fp, kwargs.pop('encoding', None) or 'utf-8')
    return _json.load(fp, **kwargs)


def htmlsafe_dumps(obj, **kwargs):
    """工作起来完全像 :func:`dumps` 函数，
    但对于用在 ``<script>`` 脚本标签中是安全的。
    本函数接收同样的参数后返回一个 JSON 字符串。
    注意这个函数可以用在模版中，通过 ``|tojson`` 过滤器
    也可以把结果标记成安全。如果用在 ``<script>`` 标签外的话，
    由于本函数转义某些字符的原理也是安全的。

    如下字符都会转义成字符串：

    -   ``<``
    -   ``>``
    -   ``&``
    -   ``'``

    这让在 HTML 中嵌入任何一个这种字符字符串都会变的安全，
    但要注意使用双引号属性时的例外情况。在这种情况下，单引号
    属性或者 HTML 转义时都是额外注意。

    .. versionchanged:: 0.10
       本函数返回的值现在一直会为 HTML 用法实现安全保护，
       即使用在 `script` 标签外或用在 XHTML 中也是安全的。
       当在 HTML 属性中都是双引号时，这种规则就不成立了。
       如果你使用 ``|tojson`` 过滤器的话，
       那就要一直用单引号来写 HTML 属性。
       换一种用法是 ``|tojson|forceescape`` 强制转义。
    """
    rv = dumps(obj, **kwargs) \
        .replace(u'<', u'\\u003c') \
        .replace(u'>', u'\\u003e') \
        .replace(u'&', u'\\u0026') \
        .replace(u"'", u'\\u0027')
    if not _slash_escape:
        rv = rv.replace('\\/', '/')
    return rv


def htmlsafe_dump(obj, fp, **kwargs):
    """类似 :func:`htmlsafe_dumps` 函数，但写成了一个晚间对象."""
    fp.write(text_type(htmlsafe_dumps(obj, **kwargs)))


def jsonify(*args, **kwargs):
    """本函数打包了 :func:`dumps` 函数是为了增强一下更容易使用。
    本函数把 JSON 结果变成一个 :class:`~flask.Response` 对象，
    该类实例对象含有 :mimetype:`application/json` 媒体类型。
    为了方便起见，本函数也把多参数转换成一个列表或者
    把多关键字参数转换成一个字典。意思就是 ``jsonify(1,2,3)`` 和
    ``jsonify([1,2,3])`` 都会序列化成 ``[1,2,3]`` 。

    为了明确， JSON 序列化行为与 :func:`dumps` 函数有如下不同之处：

    1. 单个参数：直接代入到 :func:`dumps` 函数中。
    2. 多参数：转换成列表后再代入 :func:`dumps` 函数中。
    3. 多关键字参数：转换成字典后再代入 :func:`dumps` 函数中。
    4. 同时使用 args 和 kwargs 参数时：没有定义行为并会抛出一个例外类型。

    示例用法::

        from flask import jsonify

        @app.route('/_get_current_user')
        def get_current_user():
            return jsonify(username=g.user.username,
                           email=g.user.email,
                           id=g.user.id)

    这种用法会发送一个 JSON 响应对象，就像浏览器中的::

        {
            "username": "admin",
            "email": "admin@localhost",
            "id": 42
        }


    .. versionchanged:: 0.11
       增加了支持序列化顶层阵列。
       否则在老旧的浏览器中会导致一项安全风险。
       查看 :ref:`json-security` 了解细节。

    如果 ``JSONIFY_PRETTYPRINT_REGULAR`` 配置项设置成 `True` 的话，
    或者 Flask 网络应用运行在调试模式中的话，
    本函数的响应对象会是良好格式输出。
    压缩的格式（非良好格式）当前意思就是在分隔符后没有缩进和没有空格。

    .. versionadded:: 0.2
    """

    indent = None
    separators = (',', ':')

    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
        indent = 2
        separators = (', ', ': ')

    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    return current_app.response_class(
        dumps(data, indent=indent, separators=separators) + '\n',
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )


def tojson_filter(obj, **kwargs):
    return Markup(htmlsafe_dumps(obj, **kwargs))
