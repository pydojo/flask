# -*- coding: utf-8 -*-
"""
标签过的 JSON
~~~~~~~~~~~~~~~~~

针对非标准 JSON 类型缺少序列化的一种坚实表现形式。
:class:`~flask.sessions.SecureCookieSessionInterface` 类使用本模块
序列化会话数据，但也可以用在其它地方。本模块可以扩展成支持其它类型。

.. autoclass:: TaggedJSONSerializer
    :members:

.. autoclass:: JSONTag
    :members:

让我们来看一个示例，该示例增加了 :class:`~collections.OrderedDict` 支持。
在 Python 或 JSON 中，字典都是无序的数据类型，所以处理字典我们会把词条转换成
 ``[key, value]`` 键值对列表形式。
子类化 :class:`JSONTag` 类后会给子类一个新键 ``' od'`` 来识别类型。
会话序列化器先处理字典，所以在最前面插入一个新的标签，因为
``OrderedDict`` 必须要在处理 ``dict`` 字典之前先处理完。 ::

    from flask.json.tag import JSONTag

    class TagOrderedDict(JSONTag):
        __slots__ = ('serializer',)
        key = ' od'

        def check(self, value):
            return isinstance(value, OrderedDict)

        def to_json(self, value):
            return [[k, self.serializer.tag(v)] for k, v in iteritems(value)]

        def to_python(self, value):
            return OrderedDict(value)

    app.session_interface.serializer.register(TagOrderedDict, index=0)

:copyright: © 2010 by the Pallets team.
:license: BSD, see LICENSE for more details.
"""

from base64 import b64decode, b64encode
from datetime import datetime
from uuid import UUID

from jinja2 import Markup
from werkzeug.http import http_date, parse_date

from flask._compat import iteritems, text_type
from flask.json import dumps, loads


class JSONTag(object):
    """为定义类型的基类标签给 :class:`TaggedJSONSerializer` 类."""

    __slots__ = ('serializer',)

    #: The tag to mark the serialized object with. If ``None``, this tag is
    #: only used as an intermediate step during tagging.
    key = None

    def __init__(self, serializer):
        """根据序列化器建立一个标签器."""
        self.serializer = serializer

    def check(self, value):
        """检查给出的值是否应该由本标签类进行标记."""
        raise NotImplementedError

    def to_json(self, value):
        """把 Python 对象转换成一个合法的 JSON 类型对象，
        标签会稍后增加。"""
        raise NotImplementedError

    def to_python(self, value):
        """把 JSON 形式转换回正确的类型，
        标签也会被移除。"""
        raise NotImplementedError

    def tag(self, value):
        """把值转换成一个合法的 JSON 类型后，
        把标签结构增加到结果上。"""
        return {self.key: self.to_json(value)}


class TagDict(JSONTag):
    """对一维字典进行标签化，只有键与注册的标签进行匹配。

    内部，字典键带有两个下划线 `__` 作为后缀，
    并且在解序列化时会移除这个后缀。
    """

    __slots__ = ()
    key = ' di'

    def check(self, value):
        return (
            isinstance(value, dict)
            and len(value) == 1
            and next(iter(value)) in self.serializer.tags
        )

    def to_json(self, value):
        key = next(iter(value))
        return {key + '__': self.serializer.tag(value[key])}

    def to_python(self, value):
        key = next(iter(value))
        return {key[:-2]: value[key]}


class PassDict(JSONTag):
    __slots__ = ()

    def check(self, value):
        return isinstance(value, dict)

    def to_json(self, value):
        # JSON objects may only have string keys, so don't bother tagging the
        # key here.
        return dict((k, self.serializer.tag(v)) for k, v in iteritems(value))

    tag = to_json


class TagTuple(JSONTag):
    __slots__ = ()
    key = ' t'

    def check(self, value):
        return isinstance(value, tuple)

    def to_json(self, value):
        return [self.serializer.tag(item) for item in value]

    def to_python(self, value):
        return tuple(value)


class PassList(JSONTag):
    __slots__ = ()

    def check(self, value):
        return isinstance(value, list)

    def to_json(self, value):
        return [self.serializer.tag(item) for item in value]

    tag = to_json


class TagBytes(JSONTag):
    __slots__ = ()
    key = ' b'

    def check(self, value):
        return isinstance(value, bytes)

    def to_json(self, value):
        return b64encode(value).decode('ascii')

    def to_python(self, value):
        return b64decode(value)


class TagMarkup(JSONTag):
    """序列化任何与 :class:`~flask.Markup` 类 API 相匹配的对象，
    查看那个方法结果使用 ``__html__`` 方法。
    总会解序列化成一个 :class:`~flask.Markup` 类实例。"""

    __slots__ = ()
    key = ' m'

    def check(self, value):
        return callable(getattr(value, '__html__', None))

    def to_json(self, value):
        return text_type(value.__html__())

    def to_python(self, value):
        return Markup(value)


class TagUUID(JSONTag):
    __slots__ = ()
    key = ' u'

    def check(self, value):
        return isinstance(value, UUID)

    def to_json(self, value):
        return value.hex

    def to_python(self, value):
        return UUID(value)


class TagDateTime(JSONTag):
    __slots__ = ()
    key = ' d'

    def check(self, value):
        return isinstance(value, datetime)

    def to_json(self, value):
        return http_date(value)

    def to_python(self, value):
        return parse_date(value)


class TaggedJSONSerializer(object):
    """使用一个标签系统的序列化器，它坚固地呈现那些不是 JSON 类型的对象。
    作为中间序列化器代入到 :class:`itsdangerous.Serializer` 类中。

    支持的额外类型如下：

    * :class:`dict`
    * :class:`tuple`
    * :class:`bytes`
    * :class:`~flask.Markup`
    * :class:`~uuid.UUID`
    * :class:`~datetime.datetime`
    """

    __slots__ = ('tags', 'order')

    #: Tag classes to bind when creating the serializer. Other tags can be
    #: added later using :meth:`~register`.
    default_tags = [
        TagDict, PassDict, TagTuple, PassList, TagBytes, TagMarkup, TagUUID,
        TagDateTime,
    ]

    def __init__(self):
        self.tags = {}
        self.order = []

        for cls in self.default_tags:
            self.register(cls)

    def register(self, tag_class, force=False, index=None):
        """使用本序列化器注册一个新标签。

        :param tag_class: 要注册的标签类。会被本序列化器类实例进行实例化。
        :param force: 覆写一个已有的标签。如果参数值是 `False`  (默认值)，
            会抛出一个 :exc:`KeyError` 例外类型。
        :param index: 索引插入到标签顺序中的新标签。
            当新标签是已有的标签时，这个参数是有用的。
            如果参数值是 ``None`` (默认值) 的话，
            新标签会插入到标签顺序的尾部。

        :raise KeyError: 如果新标签是已注册过的，
            并且 ``force`` 参数值是 `False` 的话，抛出这个例外。
        """
        tag = tag_class(self)
        key = tag.key

        if key is not None:
            if not force and key in self.tags:
                raise KeyError("Tag '{0}' is already registered.".format(key))

            self.tags[key] = tag

        if index is None:
            self.order.append(tag)
        else:
            self.order.insert(index, tag)

    def tag(self, value):
        """如果需要的话，本方法把一个值转换成一个标签过的表现形式."""
        for tag in self.order:
            if tag.check(value):
                return tag.tag(value)

        return value

    def untag(self, value):
        """把一个标签过的形式转换回原来的类型."""
        if len(value) != 1:
            return value

        key = next(iter(value))

        if key not in self.tags:
            return value

        return self.tags[key].to_python(value[key])

    def dumps(self, value):
        """标签化一个值后转化成一个坚固的 JSON 字符串."""
        return dumps(self.tag(value), separators=(',', ':'))

    def loads(self, value):
        """从一个 JSON 字符串加载数据后解序列化任何一个标签过的对象."""
        return loads(value, object_hook=self.untag)
