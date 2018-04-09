#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# pasrer.py
from lexer import *


class AST(object):
    pass


class SynError(Exception):
    pass


class Star_expr(AST):
    def __init__(self, mul, expr):
        self.mul = mul
        self.expr = expr
        self.type = 'star_expr'


class Expr(AST):
    def __init__(self, left, tokens):
        # 双目表达式
        self.left = left
        self.right = tokens
        self.op = tokens[0].value


class Factor(AST):
    def __init__(self, tokens):
        # 因子
        self.tokens = tokens


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self):
        raise SynError('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def comparison(self):
        # expr (comp_op expr)*
        pass

    def not_test(self):
        # 'not' not_test | comparison
        pass

    def and_test(self):
        # not_test ('and' not_test)*
        pass

    def or_test(self):
        # and_test ('or' and_test)*
        pass

    def test(self):
        # or_test ['if' or_test 'else' test] | lambdef
        pass

    def yield_arg(self):
        # 'from' test | testlist
        pass

    def yield_expr(self):
        # 'yield' [yield_arg]
        pass

    def atom(self):
        # ('(' [yield_expr|testlist_comp] ')' |
        #    '[' [testlist_comp] ']' |
        #    '{' [dictorsetmaker] '}' |
        #    NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')
        if self.current_token.type in (INT, INUM, FLOAT, OINT, BINT, XINT, ID, NONE, TRUE, FALSE, STR, BSTR):
            token = self.current_token
            self.eat(token.type)
            return token
        pass

    def trailer(self):
        # '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
        pass

    def atom_expr(self):
        # [AWAIT] atom trailer*
        _await = None
        if self.current_token.type == AWAIT:
            _await = self.current_token
            self.eat(AWAIT)

        node = self.atom()
        if self.current_token.type in (LB, LSB, DOT):
            tokens = []
            while self.current_token.type in (LB, LSB, DOT):
                tokens.append(self.trailer())
            node = Expr(node, tokens)
            return Factor([_await, node]) if _await else node
        return Factor([_await, node]) if _await else node

    def power(self):
        # atom_expr ['**' factor]
        node = self.atom_expr()
        tokens = []
        if self.current_token.type == POWER:
            tokens.append(self.current_token)
            self.eat(POWER)
            tokens.append(self.factor())
            return Expr(node, tokens)
        return node

    def factor(self):
        # ('+'|'-'|'~') factor | power
        tokens = []
        if self.current_token.type in (ADD, SUB, OPPO):
            tokens.append(self.current_token)
            self.eat(self.current_token.type)
            tokens.append(self.factor())
            return Factor(tokens)
        else:
            return self.power()

    def term(self):
        # factor (('*'|'@'|'/'|'%'|'//') factor)*
        node = self.factor()
        if self.current_token.type in (MUL, DEC, REAL_DIV, YU, DIV):
            tokens = []
            while self.current_token.type in (MUL, DEC, REAL_DIV, YU, DIV):
                tokens.append(self.current_token)
                self.eat(self.current_token.type)
                tokens.append(self.factor())
            return Expr(node, tokens)
        return node

    def arith_expr(self):
        # term (('+'|'-') term)*
        node = self.term()
        if self.current_token.type in (ADD, SUB):
            tokens = []
            while self.current_token.type in (ADD, SUB):
                tokens.append(self.current_token)
                self.eat(self.current_token.type)
                tokens.append(self.term())
            return Expr(node, tokens)
        return node

    def shift_expr(self):
        # arith_expr (('<<'|'>>') arith_expr)*
        node = self.arith_expr()
        if self.current_token.type in (LL, RR):
            tokens = []
            while self.current_token.type in (LL, RR):
                tokens.append(self.current_token)
                self.eat(self.current_token.type)
                tokens.append(self.arith_expr())
            return Expr(node, tokens)
        return node

    def and_expr(self):
        # shift_expr ('&' shift_expr)*
        node = self.shift_expr()
        if self.current_token.type == ET:
            tokens = []
            while self.current_token.type == ET:
                tokens.append(self.current_token)
                self.eat(ET)
                tokens.append(self.shift_expr())
            return Expr(node, tokens)
        return node

    def xor_expr(self):
        # and_expr ('^' and_expr)*
        node = self.and_expr()
        if self.current_token.type == DIF:
            tokens = []
            while self.current_token.type == DIF:
                tokens.append(self.current_token)
                self.eat(DIF)
                tokens.append(self.and_expr())
            return Expr(node, tokens)
        return node

    def expr(self):
        # xor_expr ('|' xor_expr)*
        node = self.xor_expr()
        if self.current_token == SHU:
            tokens = []
            while self.current_token == SHU:
                tokens.append(self.current_token)
                self.eat(SHU)
                tokens.append(self.xor_expr())
            return Expr(node, tokens)
        return node

    def star_expr(self):
        # '*' expr
        mul = self.current_token
        self.eat(MUL)
        expr = self.expr()
        return Star_expr(mul, expr)

    def comp_op(self):
        # '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
        # <> isn't actually a valid comparison operator in Python. It's here for the
        # sake of a __future__ import described in PEP 401 (which really works :-)
        # so, 我删了'<>'
        if self.current_token.type == COMP_OP:
            token = self.current_token
            self.eat(COMP_OP)
            return token

        if self.current_token.type == IN:
            token = self.current_token
            self.eat(IN)
            return Token(COMP_OP, 'in')

        if self.current_token.type == NOT:
            _not = self.current_token
            self.eat(NOT)
            _in = self.current_token
            self.eat(IN)
            return Token(COMP_OP, 'not in')

        _is = self.current_token
        self.eat(IS)
        if self.current_token.type == NOT:
            _not = self.current_token
            self.eat(NOT)
            return Token(COMP_OP, 'is not')
        return Token(COMP_OP, 'is')

    def augassign(self):
        # ('+=' | '-=' | '*=' | '@=' | '/=' | '%=' | '&=' | '|=' | '^=' |
        # '<<=' | '>>=' | '**=' | '//=')
        token = self.current_token
        self.eat(AUGASSIGN)
        return token

    def parse(self):
        pass


def main():
    with open('/home/aiyane/code/python/Bytecode/test.py', "r", encoding="utf8") as f:
        text = f.read()

    lex = Lexer(text)
    parser = Parser(lex)
    parser.parse()


if __name__ == '__main__':
    main()
