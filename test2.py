#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# test2.py

num = 3 + 4 * 5
my_list = [6, 5, 4]
result = num * my_list[2]
a1 = 1
b2 = 2
a1, b2 = b2, a1

if num < 10:
    b = 12
elif num < 20:
    b = 22
else:
    b = 0
    c1 = b + num
while a1 < b2:
    a1 += 1
    b2 -= 1
else:
    c1 = 3
for i in my_list:
    if i > 5:
        a1 -= 1
    b2 += 1
else:
    c1 = a1 + b2
