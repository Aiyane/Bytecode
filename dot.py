#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# dot.py
from parser import Parser
from lexer import Lexer
try:
    import debug
except ImportError:
    pass


class VisitNode(object):
    def __init__(self, root):
        self.root = root
        self.content = ''
        self.num = 0

    def result(self):
        self.visit_file_input()
        return 'digraph astgraph {\n    node [shape=circle, fontsize=12, fontname="Courier", height=.1];\n    ranksep=.3;\n    edge [arrowsize=.5]\n' + self.content + '}'

    def visit_file_input(self):

        for token in self.root.tokens:
            if hasattr(token, 'type') and token.type == 'NEWLINE':
                continue
            if token:
                self.visit('Program', token)

    def visit_BinOp(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        root2 = ''.join(
            [node_token, ' [label="', str(node.op.value), ' BinOp"]'])
        self.content += ' ' * 4 + root2 + '\n'
        self.content += "    {} -> {}\n".format(root, node_token)
        if node.left is not None:
            self.visit(node_token, node.left)

        if node.right is not None:
            self.visit(node_token, node.right)

    def visit_UnaryOp(self, root0, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        root = ''.join(
            [node_token, ' [label="', str(node.op.value), ' UnaryOp"]'])
        self.content += ' ' * 4 + root + '\n'
        self.content += "    {} -> {}\n".format(root0, node_token)

        if node.token:
            self.visit(node_token, node.token)

    def visit_ListObj(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="List"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)
        for token in node.tokens:
            self.visit(node_token, token)

    def visit_Token(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="', str(node.value), '"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += "    {} -> {}\n".format(root, node_token)

    def visit_IfExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="IfExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)
        for item in node.tokens:
            self.visit(node_token, item)

    def visit_IfItem(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        if node.condition is not None:
            token = ''.join([node_token, ' [label="IfItem"]'])
            self.content += ' ' * 4 + token + '\n'
            self.content += '    {} -> {}\n'.format(root, node_token)
            self.visit(node_token, node.condition)
        else:
            token = ''.join([node_token, ' [label="Else"]'])
            self.content += ' ' * 4 + token + '\n'
            self.content += '    {} -> {}\n'.format(root, node_token)
        self.visit(node_token, node.stmt)

    def visit_WhileExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, '[label="WhileExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)

        self.visit(node_token, node.condition)
        self.visit(node_token, node.stmt)
        if node.other is not None:
            self.visit(node_token, node.other)

    def visit_ForExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, '[label="ForExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)

        self.visit(node_token, node.exprlist)
        self.visit(node_token, node.testlist)
        self.visit(node_token, node.stmt)
        if node.other:
            self.visit(node_token, node.other)

    def visit_ThreeOp(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="', node.op.value, ' ThreeOp"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += "    {} -> {}\n".format(root, node_token)

        if node.left is not None:
            self.visit(node_token, node.left)
        if node.middle is not None:
            self.visit(node_token, node.middle)
        if node.right is not None:
            self.visit(node_token, node.right)

    def visit_Args(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="Args"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)
        for token in node.args:
            self.visit(node_token, token)

    def visit_Arg(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        if node.default == 1:
            token = ''.join([node_token, ' [label="*', node.name.value, '"]'])
        elif node.default == 2:
            token = ''.join([node_token, ' [label="**', node.name.value, '"]'])
        else:
            token = ''.join([node_token, ' [label="', node.name.value, '"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}'.format(root, node_token)

        if not isinstance(node.default, int):
            self.visit(node_token, node.default)

    def visit_Class(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="Class ', node.name.value, '"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)
        if node.parents:
            self.visit(node_token, node.parents)
        self.visit(node_token, node.stmt)

    def visit_Func(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="Func ', node.name.value, '"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)

        self.visit(node_token, node.params)
        self.visit(node_token, node.stmt)
        if node.ret:
            self += 1
            node_token2 = ''.join(['node' + str(self.num)])
            token = ''.join([node_token2, ' [label="need ret"]'])
            self.content += ' ' * 4 + token + '\n'
            self.content += '    {} -> {}\n'.format(node_token, node_token2)
            self.visit(node_token2, node.ret)

    def visit_WithExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="WithExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)

        self.visit(node_token, node.token)
        self.visit(node_token, node.stmt)

    def visit_TryExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="TryExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)

        self.visit(node_token, node.condition)
        self.visit(node_token, node.stmt)

        if node.other:
            self.visit(node_token, node.other)
        else:
            self.num += 1
            self.content += ' '*4 + 'node' + str(self.num) + ' [label="None"]\n'
            self.content += '    {} -> node{}\n'.format(node_token, str(self.num))
        if node.fin:
            self.visit(node_token, node.fin)
        else:
            self.num += 1
            self.content += ' '*4 + 'node' + str(self.num) + ' [label="None"]\n'
            self.content += '    {} -> node{}\n'.format(node_token, str(self.num))

    def visit_ExceptExpr(self, root, node):
        self.num += 1
        node_token = ''.join(['node', str(self.num)])
        token = ''.join([node_token, ' [label="ExceptExpr"]'])
        self.content += ' ' * 4 + token + '\n'
        self.content += '    {} -> {}\n'.format(root, node_token)
        self.visit(node_token, node.condition)
        self.visit(node_token, node.value)

    def visit(self, root, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(root, node)

    def generic_visit(self, root, node):
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
    return res


if __name__ == '__main__':
    import ipdb
    res = main()
    ipdb.set_trace()
    # dot res.dot -T png -o out.png
