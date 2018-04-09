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

# 测试字符串, 数字
r"hello"
u"hello"
R"hello"
U"hello"
# a = f"hello"
# a = F"hello"
# a = fr"hello"
# a = Fr"hello"
# a = fR"hello"
# a = FR"helo"
# a = rf"hello"
# a = rF"hello"
# a = Rf'hello'
# a = RF'hello'
b"hello"
B"""hello
hello"""
br'hello'
Br'hello'
bR'''hello
hello'''
'hello'
"hello"
"hello\b"
"""hello\r
hello"""
'''hello
hello'''
2147483647
7j
0o177
0b100110111
0xdeadbeef
# a = 100_000_000_000
# a = 0b_1110_0101
3.14
10.
.001
1e100
3.14e-10
0e0
# a = 3.14_15_93


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
