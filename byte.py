#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# byte.py

from parser_ import Parser
from lexer import Lexer
from dis import dis


class VisitNode(object):
    def __init__(self, root):
        self.num = 0
        self.root = root
        self.bytecode = []

    def visit_file_input(self):
        for token in self.root.tokens:
            self.visit(token)
        return self.bytecode

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
        left = self.visit(node.left, True)
        right = self.visit(node.right, True)

        # 如果是=, 为赋值语句
        if node.op.value == '=':
            self.bytecode.append(['', right, '', left])
            return left

        # 二元操作，增加临时变量
        self.num += 1
        ret = 't' + str(self.num)
        # 如果是(), 为函数调用
        if node.op.value == '()':
            self.bytecode.append(['CALL', left, right, ret])
        if node.op.value == '-':
            self.bytecode.append(['-', left, right, ret])
        if node.op.value == '+':
            self.bytecode.append(['+', left, right, ret])
        if node.op.value == '*':
            self.bytecode.append(['*', left, right, ret])
        if node.op.value == '**':
            self.bytecode.append(['**', left, right, ret])
        if node.op.value == '/':
            self.bytecode.append(['/', left, right, ret])
        if node.op.value == '//':
            self.bytecode.append(['//', left, right, ret])
        if node.op.value == '%':
            self.bytecode.append(['%', left, right, ret])

        return ret

    def visit_UnaryOp(self, node):
        if node.op.value == '[]':
            return self.visit(node.token)
        pass

    def visit_ListObj(self, node):
        return [i for i in map(lambda x: self.visit(x), node.tokens)]

    def visit_Token(self, node, call=None):
        # 如果是str就直接返回
        # 函数名:可能被调用 或者 变量名
        # 返回数值
        if node.type in ('STR', 'ID', 'INT', 'FLOAT'):
            return node.value
        # 返回 True
        if node.type == 'TRUE':
            return True
        # 返回 False
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
        if len(res) == 1:
            return res[0]
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
    return VisitNode(root)

if __name__ == '__main__':
    # import ipdb
    res = main()
    print('操作符:操作数1:操作数2:返回地址')
    for code in res.visit_file_input():
        print(code)
    # ipdb.set_trace()
    # dot res.dot -T png -o out.png
