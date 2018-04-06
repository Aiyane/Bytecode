#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# test.py


def hello(a, b):
    # 还不支持
    # a += 1
    # b -= 1
    a = a + 1
    b = b - 1
    return a+b


a = 10
b = 5
c = a - b

print(hello(a, c))
