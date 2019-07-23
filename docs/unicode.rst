Flask 中的 Unicode
=======================

Flask 像 Jinja2 和 Werkzeug 一样，当涉及到文本时全部基于 Unicode 编码。
不只这些库，与网络有关的主要 Python 库都是这样处理文本的。
如果你不知道什么是 Unicode 编码的话，你应该正确阅读如下文章
`The Absolute Minimum Every Software Developer
Absolutely, Positively Must Know About Unicode and Character Sets
<https://www.joelonsoftware.com/articles/Unicode.html>`_.  
本文档部分只是尽力涵盖非常基础的内容，所以你会拥有一次愉快的 Unicode 体验。

自动化转换
--------------------

Flask 很少去假设你的网络应用是否使用 Unicode 编码
（ 当然你可以改变字符集），因为 Unicode 是基础编码并且
减少你的许多痛苦：

-   在你的站点上对文本编码都采用 UTF-8 字符集。
-   除了 ASCII 字符外，内部会一直使用 Unicode 对文本进行逐字编码。
-   不管什么时候，你在用一个协议来建立通信时编码和解码过程都会出现，
    因为需要使用字节传输。

那么这些对你来说意味着什么？

HTTP 就是建立在字节基础之上的。不只协议是这样，服务器上的系统也是这样解释文档的
（所以叫做 URIs 或叫做 URLs）。不管如何做到的，HTML常常是在 HTTP 顶层进行传输，
支持大量各种字符集，并且都被使用着，传输的字符都在一个 HTTP 头部信息中。
如果你要发送 Unicode 出去，那就要用 UTF-8 进行编码，Flask 就是这样认识的，
别把事情搞成多层化，否则受痛苦的是你自己。 Flask 会做编码处理后为你设置合适的头部信息。

如果你使用 SQLAlchemy 或一个类似的 ORM 系统帮助与数据库通信，同样是这样。
有的数据库含带一种协议，如果你没编码成 Unicode 的话，该协议会为你编码再传输，
所以 SQLAlchemy 或你的其它 ORM 系统应该负责这件编码事情。

黄金法则
---------------

那么最棒的法则是：如果你们不处理二进制数据的话，那就与 Unicode 一起工作。
在 Python 2.x 中与 Unicode 一起工作意味着什么？

-   你们要一直只使用 ASCII 字符（基本上，数字、一些不含变音的拉丁字母或没有额外
    部分的具体字符），你可以使用正规的逐字字符串形式 (``'Hello World'``)。
-   如果在一个字符串中你需要任何一个非 ASCII 字符的话，你都要把字符串标记成
    Unicode 字符串形式，通过用一个小写字母 `u` 作为字符串前缀。
    (就像 ``u'Hänsel und Gretel'`` 这样)
-   如果在 Python 文件中你们正在使用非Unicode 字符的话，你们要告诉 Python 你
    采用的什么字符集编码 Python 文件。再次重申，我建议使用 UTF-8 来做这件事。
    要告诉解释器你的编码你可以把 ``# -*- coding: utf-8 -*-`` 放在 Python 源文件
    的第一行或第二行上。
-   Jinja 被配置成解码那些使用 UTF-8 的模版文件。所以确保告诉你的文本编辑器保存
    文件时也要采用 UTF-8 编码。

自己实现编码和解码
------------------------------

如果你们与一个文件系统或一些没有真正基于 Unicode 编码的事物通信时，
在与 Unicode 接口一起工作时你不得不要确保你的解码正确。所以例如，
如果你想要加载文件系统上的一个文件后，嵌入到一个 Jinja2 模版中的话，
你会在把读取的内容解码时使用与加载的文件所用的一样编码字符集。此处一个
老问题就是文本文件不描述它们所采用的编码字符集。所以帮自己一下，一定要
约束你自己采用 UTF-8 来写文本文件。

在 Python 2.x 中，要加载这样一种含有 Unicode 的文件，你可以使用内置字符串
:meth:`str.decode` 方法::

    def read_file(filename, charset='utf-8'):
        with open(filename, 'r') as f:
            return f.read().decode(charset)

要把 Unicode 内容解码成具体字符集，例如 UTF-8 一样，在 Python 2.x 中
可以使用 :meth:`unicode.encode` 方法::

    def write_file(filename, contents, charset='utf-8'):
        with open(filename, 'w') as f:
            f.write(contents.encode(charset))

在 Python 3.7 开始字符串只有 ``encode`` 方法，只有字节有 ``decode`` 方法。

配置文本编辑器
-------------------

大多数文本编辑器都是默认保存成 UTF-8 字符集，如果你的文本编辑器不是这样的话，改变它。
这里有一些共同的方式来设置你的文本编辑器存储成 UTF-8 字符集：

-   Vim: 把 ``set enc=utf-8`` 放到你的 ``.vimrc`` 文件中。

-   Emacs: 既可以使用一种编码 cookie 方式，也可以使用把配置放到
    你的 ``.emacs`` 文件里的方式::

        (prefer-coding-system 'utf-8)
        (setq default-buffer-file-coding-system 'utf-8)

-   Notepad++:

    1. Go to *Settings -> Preferences ...*
    2. Select the "New Document/Default Directory" tab
    3. Select "UTF-8 without BOM" as encoding

    同时建议使用 Unix 新行格式，你可以在相同的面板中选择该项，但这不是一项需求。
