#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# test.py


# 暂不支持类
# class Test(object):
#     def __init__(self, name, pwd):
#         self.name = name
#         self.pwd = pwd

#     def say(self):
#         print("Hello", self.name)
b1 = [1, 2, 3, 4, 5]
a1 = 10


def say(a1, b1):

    if a1 >= 10:
        print("hello", a1)
    for i in b1:
        print(i)


def hello(a, b):
    """
    还不支持
    a += 1
    b -= 1
    """
    say(a1, b1)
    a = a + 1
    b = b - 1
    return a+b


a = 10
b = 5.5
c = a - b

print(hello(a, c))
