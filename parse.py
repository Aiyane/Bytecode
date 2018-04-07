#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# parse.py
import re


# 终结符号
LB = 'LB'  # (
RB = 'RB'  # )
LCB = 'LCB'  # {
RCB = 'RCB'  # }
LSB = 'LSB'  # [
RSB = 'RSB'  # ]
ASSIGN = 'ASSIGN'  # =
COLON = 'COLON'  # :
COMMA = 'COMMA'  # ,
STR = 'STR'
INT = 'INT'
FLOAT = 'FLOAT'
ID = 'ID'
TAB = 'TAB'
END = 'END'
DEF = 'DEF'
IF = 'IF'
FOR = 'FOR'
IN = 'IN'
NOT = 'NOT'
AND = 'AND'
OR = 'OR'
ADD = 'ADD'  # +
SUB = 'SUB'  # -
MUL = 'MUL'  # *
DIV = 'DIV'  # //
REAL_DIV = 'REAL_DIV'  # /
TRUE = 'TRUE'
FALSE = 'FALSE'
GT = 'GT'  # >
GE = 'GE'  # >=
LT = 'LT'  # <
LE = 'LE'  # <=
EQ = 'EQ'  # ==
NE = 'NE'  # !=
IS = 'IS'
RET = 'RET'
ELIF = 'ELIF'
ELSE = 'ELSE'
WHILE = 'WHILE'
BREAK = 'BREAK'
CONTINUE = 'CONTINUE'
EOF = 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """
        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


# 关键字
KEY_WORDS = {
    'is': Token('IS', 'IS'),
    'continue': Token('CONTINUE', 'CONTINUE'),
    'break': Token('BREAK', 'BREAK'),
    'while': Token('WHILE', 'WHILE'),
    'for': Token('FOR', 'FOR'),
    'return': Token('RET', 'RET'),
    'if': Token('IF', 'IF'),
    'elif': Token('ELIF', 'ELIF'),
    'else': Token('ELSE', 'ELSE'),
    'def': Token('DEF', 'DEF'),
    'not': Token('NOT', 'NOT'),
    'or': Token('OR', 'OR'),
    'and': Token('AND', 'AND'),
    'True': Token('TRUE', 'TRUE'),
    'False': Token('FALSE', 'FALSE'),
}


class Lexer(object):
    def __init__(self, program):
        self.tab_level = 0
        self.program = program
        self.stack = []
        pass

    # 一行的分词
    def tokenize_line(self, line):
        cur_tab_level = self.count_tab_level(line)
        if cur_tab_level != self.tab_level:
            self.tab_level = cur_tab_level
            yield self.tab_level

        for m in re.finditer(r'\'\'\'|"""|".*?"|\'.*?\'|//?|[-+*()[\]{}:,;#]|[><=]=?|!=|[A-Za-z_]+\d*|\d+(?:\.\d*)?', line):
            tok = m.group(0)
            yield tok

    # 计算缩进级别
    def count_tab_level(self, line):
        tab_level = 0
        while line[tab_level*4:(tab_level+1)*4] == ' '*4:
            tab_level += 1
        return tab_level

    def _id(self, tok):
        token = KEY_WORDS.get(tok, Token(ID, tok))
        return token

    def number(self, tok):
        return Token(FLOAT, float(tok)) if '.' in tok else Token(INT, int(tok))

    def error(self):
        raise Exception('Invalid character')

    def tokenize(self):
        jump = False
        for line in self.program:
            for tok in self.tokenize_line(line):
                if isinstance(tok, int):
                    yield Token(TAB, tok)
                elif tok in ("'''", '"""'):
                    jump = not jump
                    break
                elif tok == "#" or jump:
                    break
                elif re.match(r'[A-Za-z_]+\d*', tok):
                    yield self._id(tok)
                elif re.match(r'\d+(?:\.\d*)?', tok):
                    yield self.number(tok)
                elif tok[0] in ('"', "'"):
                    yield Token(STR, tok)
                elif tok == ':':
                    yield Token(COLON, ':')
                elif tok == '=':
                    yield Token(ASSIGN, '=')
                elif tok == '==':
                    yield Token(EQ, '==')
                elif tok == '>':
                    yield Token(GT, '>')
                elif tok == '<':
                    yield Token(LT, '<')
                elif tok == '>=':
                    yield Token(GE, '>=')
                elif tok == '<=':
                    yield Token(LE, '<=')
                elif tok == '!=':
                    yield Token(NE, '!=')
                elif tok == '(':
                    yield Token(LB, '(')
                elif tok == ')':
                    yield Token(RB, ')')
                elif tok == '{':
                    yield Token(LCB, '{')
                elif tok == '}':
                    yield Token(RCB, '}')
                elif tok == '[':
                    yield Token(LSB, '[')
                elif tok == ']':
                    yield Token(RSB, ']')
                elif tok == '+':
                    yield Token(ADD, '+')
                elif tok == '-':
                    yield Token(SUB, '-')
                elif tok == '*':
                    yield Token(MUL, '*')
                elif tok == '/':
                    yield Token(REAL_DIV, '/')
                elif tok == '//':
                    yield Token(DIV, '//')
                elif tok == ',':
                    yield Token(COMMA, ',')
                elif tok == ';':
                    yield Token(END, ';')
                elif tok == ';':
                    continue
                else:
                    self.error()
            yield Token(END, None)
        yield Token(EOF, None)


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Block(AST):
    def __init__(self):
        self.tokens = []


class CallFunc(AST):
    def __init__(self, func, *attrs):
        self.token = func
        self.attrs = attrs


class Parser(object):
    def __init__(self, lexer):
        self.tokens = lexer.tokenize()
        self.cur_token = next(self.tokens)

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.cur_token.type == token_type:
            self.cur_token = next(self.tokens)
        else:
            self.error()

    def build_ld(self):
        # 列表解析, 字典解析
        pass

    def stmt(self):
        # 赋值语句或call_func
        var_name = Var(self.cur_token)
        self.eat(ID)
        if self.cur_token.type == ASSIGN:
            op = self.cur_token
            self.eat(ASSIGN)
            if self.cur_token.type in (ID, FLOAT, INT):
                left = self.factor()
                right = self.expr(left)
            elif self.cur_token.type in (LSB, LCB):
                right = self.build_ltd()
            else:
                self.error()
            node = Assign(var_name, op, right)
        elif self.cur_token.type == LB:
            node = self.call_func(var_name)
        else:
            self.error()
        return node

    def call_func(self, func_name):
        # 函数调用
        self.eat(LB)
        attrs = []
        while self.cur_token.type in (ID, INT, FLOAT):
            attrs.append(self.factor())
            if self.cur_token.type == COMMA:
                self.eat(COMMA)
        self.eat(RB)
        return CallFunc(func_name, attrs)

    def expr(self, left):
        # 表达式, 也可以是函数调用
        while True:
            if self.cur_token.type == END:
                self.eat(END)
                return left
            if self.cur_token.type == RB:
                return left
            if self.cur_token.type in (ADD, SUB):
                op = self.cur_token
                self.eat(op.type)
                right = self.term(self.factor())
                left = BinOp(left, op, right)
            elif self.cur_token.type in (MUL, DIV, REAL_DIV):
                left = self.term(left)
            elif self.cur_token.type == LB:
                node = self.call_func(left)
                return node
            else:
                self.error()
        return left

    def factor(self):
        # NUM或ID
        node = self.cur_token
        if node.type == ID:
            self.eat(ID)
            return Var(node)
        if node.type == INT:
            self.eat(INT)
            return Num(node)
        if node.type == FLOAT:
            self.eat(FLOAT)
            return Num(node)
        if node.type == LB:
            self.eat(LB)
            left = self.factor()
            node = self.expr(left)
            self.eat(RB)
            return node
        self.error()

    def term(self, left):
        # 乘除
        if self.cur_token.type in (ADD, SUB):
            return left
        if self.cur_token.type in (MUL, DIV, REAL_DIV):
            op = self.cur_token
            self.eat(op.type)
            right = self.factor()
            return BinOp(left, op, right)
        self.error()

    def frame(self):
        # 函数定义
        pass

    def block(self):
        node = Block()
        while True:
            if self.cur_token.type == EOF:
                break
            elif self.cur_token.type == ID:
                node.tokens.append(self.stmt())
            elif self.cur_token.type == IF:
                node.tokens.append(self.if_expr())
            elif self.cur_token.type == DEF:
                node.tokens.append(self.frame())
            else:
                self.error()
        return node

    def parse(self):
        node = self.block()
        return node


def main():
    with open('test.py', "r", encoding="utf8") as f:
        for token in Lexer(f).tokenize():
            print(token)


if __name__ == '__main__':
    main()
