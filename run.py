#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File Name: run.py
# Created Time: Fri 04 May 2018 07:58:05 PM CST

from parser import Parser
from lexer import Lexer, Token, Args


class Run(object):
    def __init__(self, root):
        self.vars = dict()
        self.funcs = dict()
        self.root = root


    def visit_file_input(self):
        pass

    def visit_BinOp(self, node):
        if node.op.value == '=':
            if isinstance(node.left, Token) and isinstance(node.right, Token):
                self.vars[node.left.value] = node.right.value

        if node.op.value == '()':
            func = self.funcs(node.left.value)
            if func:
                pass
            else:
                func = getattr(__builtin__, node.left.value)
                if isinstance(node.right, Args):
                    params = map(self.visit_Toke, node.right.args)
                    return func(*params)
        pass

    def visit_UnaryOp(self, node):
        pass

    def visit_ListObj(self, node):
        pass

    def visit_Token(self, node):
        if node.type == 'STR':
            return node.value
        if node.type == 'ID':
            return self.vars[node.value]
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
        pass

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
    with open("test2.py", "r") as fin:
        text = fin.read()
    lex = Lexer(text)
    par = Parser(lex)
    root = par.parse()
    return root


if __name__ == "__main__":
    root = main()
    import ipdb; ipdb.set_trace()
