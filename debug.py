#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""这是进行调试的程序"""

import sys


class ExceptionHook:
    instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            from IPython.core import ultratb
            self.instance = ultratb.FormattedTB(mode='Plain',
                                                color_scheme='Linux', call_pdb=1)
        return self.instance(*args, **kwargs)


sys.excepthook = ExceptionHook()
