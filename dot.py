#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# dot.py
from parser import Parser
from lexer import Lexer
from functools import partial


class VisitNode(object):
    def __init__(self, root):
        self.root = root
        self.content = ''
        self.num = 0

    def result(self):
        self.visit_file_input()
        return 'digraph G {\n    node [shape=circle, fontsize=12, fontname="Courier", height=.1];\n    ranksep=.3;\n    edge [arrowsize=.5]\n' + self.content + '}'

    def visit_file_input(self):

        for token in self.root.tokens:
            if hasattr(token, 'type') and token.type == 'NEWLINE':
                continue
            if token:
                self.visit('root', token)

    def visit_BinOp(self, root, node):
        self.num += 1
        root2 = ''.join(['"', str(node.op.value), "_", str(self.num), '"'])

        self.content += "    {} -> {}\n".format(root, root2)
        if node.left:
            self.visit(root2, node.left)

        if node.right:
            self.visit(root2, node.right)

    def visit_UnaryOp(self, root0, node):
        self.num += 1
        root = ''.join(['"', str(node.op.value), "_", str(self.num), '"'])
        self.content += "    {} -> {}\n".format(root0, root)

        if node.token:
            self.visit(root, node.token)

    def visit_ListObj(self, root, node):
        for token in node.tokens:
            self.visit(root, token)

    def visit_Token(self, root, node):
        if hasattr(node, 'value'):
            self.num += 1
            token = ''.join(['"', str(node.value), '_', str(self.num), '"'])
            self.content += "    {} -> {}\n".format(root, token)
        else:
            self.visit(token, node)

    def visit(self, root, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(root, node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


def main():
    with open('/home/aiyane/code/python/Bytecode/test2.py', "r", encoding="utf8") as f:
        text = f.read()

    lex = Lexer(text)
    parser = Parser(lex)
    root = parser.parse()
    res = VisitNode(root).result()

    with open('res.dot', 'w', encoding="utf8") as f:
        f.write(res)
    # dot res.dot -T png -o out.png


if __name__ == '__main__':
    main()
