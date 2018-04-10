#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# test.py


b1 = [1, 2, 3, 4, 5]
a1 = 10


class Test(object):
    def __init__(self, name):
        self.name = name

    def haha(self):
        print(self.name)


def say(a1, b1):

    if a1 >= 10:
        print("hello", a1)
    for i in b1:
        print(i)


def hello(a, b):
    """
    hello
    """
    a += 1
    b -= 1
    say(a1, b1)
    a = a + 1
    b = b - 1
    return a+b


a = 10
b = 5.5
c = a - b

print(hello(a, c))
