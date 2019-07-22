Pocoo 风格指导
==================

对于 Pocoo 风格指导来说就是所有 Pocoo 项目采用的一种风格，包括 Flask 项目。
这种风格指导时一种 Flask 补丁需求，并且也作为 Flask 扩展件的推荐风格。

通用中， Pocoo 风格指导紧密遵循着 :pep:`8` 标准，只含有很小的差异和扩展内容。

通用图层
--------------

缩进：
  4 个空格。不用 tabs 制表符。

最大单行长度：
  79 个字符，如果非要再长一点儿的话，最大为 84 个字符。
  尽量避免太多的嵌入层次代码，
  明智地使用 `break`、 `continue` 和 `return` 语句。

连续的长语句：
  要保持一个语句的连贯你可以使用反斜杠来保持下一行代码的对齐，
  要以最后一个句号或等号作为对齐点，又或用4个空格作为对齐点::

    this_is_a_very_long(function_call, 'with many parameters') \
        .that_returns_an_object_with_an_attribute

    MyModel.query.filter(MyModel.scalar > 120) \
                 .order_by(MyModel.name.desc()) \
                 .limit(10)

  如果一个语句含有圆括号对儿，或方括号对儿的话，以圆括号对儿为对齐点::

    this_is_a_very_long(function_call, 'with many parameters',
                        23, 42, 'and even more')

  对于列表或元组中含有许多项元素来说，要在开括号后立即换行来对齐::

    items = [
        'this is the first', 'set of items', 'with more items',
        'to come in this line', 'like this'
    ]

空行：
  顶层函数和类都要用2个空行来间隔，其它情况都是用1个空行来间隔。
  不要使用太多空行来分隔代码中的逻辑片段。例如::

    def hello(name):
        print 'Hello %s!' % name


    def goodbye(name):
        print 'See you %s.' % name


    class MyClass(object):
        """This is a simple docstring"""

        def __init__(self, name):
            self.name = name

        def get_annoying_name(self):
            return self.name.upper() + '!!!!111'

表达式和语句
--------------------------

通用空白符规则：
  - 对于不属于单词的一元操作符来说不需要使用空白符
    （例如， ``-``、 ``~`` 等等。）在圆括号内也是如此。
  - 空白符是放在二进制操作符之间用的。

  良好空白符用法::

    exp = -1.05
    value = (item_value / item_count) * offset / exp
    value = my_list[index]
    value = my_dict['key']

  败坏空白符用法::

    exp = - 1.05
    value = ( item_value / item_count ) * offset / exp
    value = (item_value/item_count)*offset/exp
    value=( item_value/item_count ) * offset/exp
    value = my_list[ index ]
    value = my_dict ['key']

比较对象放置问题：
  Never compare constant with variable, always variable with constant:

  良好的放置::

    if method == 'md5':
        pass

  败坏的放置::

    if 'md5' == method:
        pass

比较操作符：
  - 比较任意类型： ``==`` 和 ``!=``
  - 比较单体使用 ``is`` 和 ``is not`` （例如， ``foo is not None`` ）
  - 永远不要用 ``True`` 或 ``False`` 进行比较（例如，永远不要写这样的代码
     ``foo == False``，反而应该用 ``not foo`` 来实现布尔值比较操作）

不存在的成员检查：
  使用 ``foo not in bar`` 而不是使用 ``not foo in bar``

实例检查：
  使用 ``isinstance(a, C)`` 而不是用 ``type(A) is C`` ，通用中尽量
  避免实例检查，而是针对特性来做检查。


命名惯例
------------------

- 类的名字： ``CamelCase`` 驼峰体，保持首字母缩写的全大写形式
  （使用 ``HTTPWriter`` 而不要用 ``HttpWriter`` 这种写法）。
- 变量的名字： ``lowercase_with_underscores`` 全小写字母与下划线组合。
- 方法和函数的名字： ``lowercase_with_underscores`` 全小写字母与下划线组合。
- 常量的名字： ``UPPERCASE_WITH_UNDERSCORES`` 全大写与下划线组合。
- 提前编译的规则表达式： ``name_re``

受保护的成员名都要用一个下划线做前缀。
双下划线都是为类服务的。

在类名上使用关键字单词的话，要以下划线作为结束。
与内置函数名冲突都是允许的，但 **必须不能** 通过给变量名增加下划线来得到解决。
如果函数需要访问一个影子内置函数的话，要把内置函数名重新绑定到一个不同的名字来代替。

函数和方法的参数名：
  - 类方法参数名： ``cls`` 是第一参数名。
  - 实例方法参数名： ``self`` 是第一参数名。
  - 使用 lambda 表达式进行财产匿名操作，第一个参数名使用 ``x`` 来代替，
    就像 ``display_name = property(lambda x: x.real_name or x.username)``


文档字符串
-------------

文档字符串惯例：
  所有的文档字符串都要使用 reStructuredText 进行格式化，确保让 Sphinx 理解。
  依据文档字符串中的行数，它们都要进行不同地放置。
  如果只是一行文档字符串的话，关三引号要与开三引号在一行上，否则文本与开三引号在一行，
  关三引号自己单起一行。::

    def foo():
        """This is a simple docstring"""


    def bar():
        """This is a longer docstring with so much information in there
        that it spans three lines.  In this case the closing triple quote
        is on its own line.
        """

模块头部：
  模块头部由一个 utf-8 编码声明行作为开始（如果使用了非ASCII编码字符的话，
  但建议无论什么时候都要使用 utf-8 编码声明模块），后面紧接着一个标准的文档字符串::

    # -*- coding: utf-8 -*-
    """
        package.module
        ~~~~~~~~~~~~~~

        A brief description goes here.

        :copyright: (c) YEAR by AUTHOR.
        :license: LICENSE_NAME, see LICENSE_FILE for more details.
    """

  请记住，正确地版权和协议文件都是验收完的 Flask 扩展件的一项需求。


注释
---------

注释的规则都类似文档字符串。都要用 reStructuredText 进行格式化。
如果一个注释用在文档化一个属性时，要在井号（ ``#`` ）后紧跟着一个冒号::

    class User(object):
        #: the name of the user as unicode string
        name = Column(String)
        #: the sha1 hash of the password + inline salt
        pw_hash = Column(String)
