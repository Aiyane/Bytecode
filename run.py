#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File Name: run.py
# Created Time: Fri 04 May 2018 07:58:05 PM CST

from parser import Parser, Args
from lexer import Lexer, Token


class Run(object):
    def __init__(self, root):
        self.vars = dict()
        self.funcs = dict()
        self.root = root

    def visit_file_input(self):
        for token in self.root.tokens:
            self.visit(token)

    def visit(self, node, call=None):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        if method_name == 'visit_Token':
            return visitor(node, call)
        return visitor(node)

    def generic_visit(self, node):
        # 抛出异常, 未知的Token
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_BinOp(self, node):
        # 如果是=, 为赋值语句
        if node.op.value == '=':
            self.vars[self.visit(node.left)] = self.visit(node.right, True)

        # 如果是(), 为函数调用
        if node.op.value == '()':
            name = self.visit(node.left)
            func = self.funcs.get(name)
            if not func:
                func = getattr(__builtins__, name)
            params = self.visit(node.right, True)
            return func(*params)

        if node.op.value == '-':
            return self.visit(node.left, True) - self.visit(node.right, True)
        if node.op.value == '+':
            return self.visit(node.left, True) + self.visit(node.right, True)
        if node.op.value == '*':
            return self.visit(node.left, True) * self.visit(node.right, True)
        if node.op.value == '**':
            return self.visit(node.left, True) ** self.visit(node.right, True)
        if node.op.value == '/':
            return self.visit(node.left, True) / self.visit(node.right, True)
        if node.op.value == '//':
            return self.visit(node.left, True) // self.visit(node.right, True)
        if node.op.value == '%':
            return self.visit(node.left, True) % self.visit(node.right, True)
        pass

    def visit_UnaryOp(self, node):
        if node.op.value == '[]':
            return self.visit(node.token)
        pass

    def visit_ListObj(self, node):
        return [i for i in map(lambda x: self.visit(x), node.tokens)]

    def visit_Token(self, node, call=None):
        # 如果是str就直接返回
        if node.type == 'STR':
            return node.value
        # 如果是ID, 在变量中查看, 或者返回其ID, 右值可能会被调用
        if node.type == 'ID':
            return self.vars[node.value] if call else node.value
        if node.type == 'INT':
            return node.value
        if node.type == 'FLOAT':
            return node.value
        if node.type == 'TRUE':
            return True
        if node.type == 'FALSE':
            return False
        pass

    def visit_IfExpr(self, node):
        pass

    def visit_IfItem(self, node):
        pass

    def visit_WhileExpr(self, node):
        pass

    def visit_ForExpr(self, node):
        pass

    def visit_ThreeOp(self, node):
        pass

    def visit_Args(self, node):
        # 有一个args参数, 这个参数的值是一个list
        # list内的元素再去访问, 这是右值, 需要调用
        res = []
        for tok in node.args:
            res.append(self.visit(tok, True))
        return res

    def visit_Arg(self, node):
        pass

    def visit_Class(self, node):
        pass

    def visit_Func(self, node):
        pass

    def visit_WithExpr(self, node):
        pass

    def visit_TryExpr(self, node):
        pass

    def visit_ExceptExpr(self, node):
        pass


def main():
    with open("test.py", "r") as fin:
        text = fin.read()
    lex = Lexer(text)
    par = Parser(lex)
    root = par.parse()
    return Run(root)


if __name__ == "__main__":
    root = main()
    # import ipdb
    # ipdb.set_trace()
    root.visit_file_input()
