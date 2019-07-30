# -*- coding: utf-8 -*-
"""
    flask.__main__
    ~~~~~~~~~~~~~~

    对于命令行中 flask.run 的一个别名形式。

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

if __name__ == '__main__':
    from .cli import main
    main(as_module=True)
