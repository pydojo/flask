如何为 Flask 做贡献？
==========================

感谢想要为 Flask 做贡献的人们！

支援问题
-----------------

千万不要使用问题追踪来寻求支援。要想获得支援请用如下资源
解决你自己代码的问题：

* IRC 聊天通道 ``#pocoo`` 在 FreeNode 上。
* IRC 聊天通道 ``#python`` 在 FreeNode 上解决普通问题。
* 邮件列表 flask@python.org 是给那些长期讨论或大型问题而提供支持。
* 在 `Stack Overflow`_ 上询问或先使用 Google 来搜索答案：
  ``site:stackoverflow.com flask {search term, exception message, etc.}``

.. _Stack Overflow: https://stackoverflow.com/questions/tagged/flask?sort=linked

报告问题
----------------

- 说明你想要什么？
- 如果可能的话，包含一个小型完整可验证的例子 `minimal, complete, and verifiable example`_ 
  这样也会帮助我们识别问题到底是什么。同时这也会帮助检查问题不是因为你的代码造成的。
- 描述清楚实际发生了什么。如果有一个例外的话，把完整的回溯信息也提供出来。
- 列出你使用的 Python, Flask, 和 Werkzeug 版本号。如果可能的话，检查是否你遇到的问题
  是否已经在项目仓库中获得解决。

.. _minimal, complete, and verifiable example: https://stackoverflow.com/help/mcve

提交补丁
------------------

- 如果你的补丁可能解决了一个 bug 的话，要包含测试代码，并且要解释清楚是
  是在哪种回路 bug 下解决的。并确保没有你的补丁测试会失败。
- 尝试遵循 `PEP8`_ 也许你忽视了代码单行长度限制导致你的代码不适合人类阅读。

第一次配置
~~~~~~~~~~~~~~~~

- 下载并安装最新的 git 版本 `latest version of git`_.
- 使用你的用户名和电邮类配置 git `username`_ and `email`_::

        git config --global user.name 'your name'
        git config --global user.email 'your email'

- 确保你有一个 GitHub 账户 `GitHub account`_
- 使用叉子功能把 Flask 复制到你自己的 GitHub 账户仓库中，只需要点击叉子按钮即可 `Fork`_ 
- `Clone`_ 把你自己的 Flask 叉子版克隆到本地计算机上::

        git clone https://github.com/{username}/flask
        cd flask

- 增加主仓库作为一个远程仓库，以备后续更新使用::

        git remote add pallets https://github.com/pallets/flask
        git fetch pallets

- 建立一个虚拟环境 virtualenv::

        python3 -m venv env
        . env/bin/activate
        # or "env\Scripts\activate" on Windows

- 安装自己的叉子版 Flask 时采用可编辑模式，并带着开发依赖包::

        pip install -e ".[dev]"

.. _GitHub account: https://github.com/join
.. _latest version of git: https://git-scm.com/downloads
.. _username: https://help.github.com/articles/setting-your-username-in-git/
.. _email: https://help.github.com/articles/setting-your-email-in-git/
.. _Fork: https://github.com/pallets/flask/fork
.. _Clone: https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork

开始编码吧
~~~~~~~~~~~~

- 建立一个分支用来识别你工作中可能遇到的问题 (e.g.
  ``2287-dry-test-suite``)
- 使用你喜欢的文本编辑器，做一些变更提交 `committing as you go`_
- 尽量遵循 `PEP8`_ 否则你可能忽略单行长度限制导致代码无法适合人类阅读。
- 涉及任何你做出的变更都要包含一些测试，这样确保没有你的变更会导致测试失败。
  `Run the tests. <contributing-testsuite_>`_.
- 把你的提交推送到你自己的 GitHub 上然后 `create a pull request`_
- 恭喜你人生中第一次做出开源的贡献 🎉

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _PEP8: https://pep8.org/
.. _create a pull request: https://help.github.com/articles/creating-a-pull-request/

.. _contributing-testsuite:

运行测试
~~~~~~~~~~~~~~~~~

运行基本的测试集要使用::

    pytest

因为对于当前环境这是唯一运行测试用的。不管你工作在 Flask 的哪个相关部分中。
就在你提交获得请求时，Travis-CI 会运行完整的测试集。

完整的测试集要花很长时间去运行，因为要针对多个 Python 组合与依赖进行测试。
你需要有 Python 2.7, 3.4, 3.5 3.6, 以及 PyPy 2.7 安装在你的电脑上
来运行全部所需要的测试环境。然后再运行::

    tox

运行测试覆盖率
~~~~~~~~~~~~~~~~~~~~~

生成一份没有测试覆盖率的报告可以说明你要从哪里开始做贡献。
运行 ``pytest`` 时使用 ``coverage`` 可以在终端里生成一份报告和
交互式 HTML 文档::

    coverage run -m pytest
    coverage report
    coverage html
    # then open htmlcov/index.html

阅读更多覆盖率的使用内容 `coverage <https://coverage.readthedocs.io>`_

使用 ``tox`` 运行完整的测试集会把所有运行情况中的覆盖率报告合并成一份。


建立文档
~~~~~~~~~~~~~~~~~

在 ``docs`` 目录中建立文档要使用 Sphinx::

    cd docs
    make html

在你自己的浏览器中打开 ``_build/html/index.html`` 就可以看到文档内容。

阅读更多文档自动化内容 `Sphinx <https://www.sphinx-doc.org>`_


make 许多目标
~~~~~~~~~~~~

Flask 提供了一份 ``Makefile`` 文件，其中含有许多快捷方法。这些方法会确保
所有的依赖包都能安装上。

- ``make test`` 使用 ``pytest`` 运行基础的测试集
- ``make cov`` 使用 ``coverage`` 运行基础的测试集
- ``make test-all`` 使用 ``tox`` 运行完整的测试集
- ``make docs`` 建立 HTML 文档

警告：无缝隙文件模式
-------------------------------

这个仓库中含有许多零缝隙文件模式，零缝隙文件模式是在把这个
仓库推送到 git 服务器时会产生一个问题。修复这种问题是需要
不考虑结构化提交历时版本，所以我们建议忽略这些警告。如果推
送失败的话，并且你正在使用自己的 git 服务器，就像 GitLab
服务器，你可以在管理员面板中关闭仓库检查功能。

这些问题也会在克隆仓库时产生问题。如果你在 git 配置文件中
又如下设置内容的话 ::

    [fetch]
    fsckobjects = true

或 ::

    [receive]
    fsckObjects = true

克隆这个仓库就会失败。唯一的解决方案就是把上面两项设置成
false 值再克隆就不会失败了，并且克隆完毕后再设置回 true值。
