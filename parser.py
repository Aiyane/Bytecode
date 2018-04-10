#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# pasrer.py
from lexer import *


class AST(object):
    pass


class SynError(Exception):
    pass


class UnaryOp(AST):
    def __init__(self, op, token):
        # 单个操作符
        self.op = op
        self.token = token


class BinOp(AST):
    def __init__(self, left, op, right):
        # 双目操作符
        self.op = op
        self.left = left
        self.right = right


class IfElse(AST):
    def __init__(self, left, req, right):
        self.left = left
        self.req = req
        self.right = right


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
        node = self.expr()
        while self.current_token.type in (COMP_OP, IN, NOT, IS):
            node = BinOp(node, self.comp_op(), self.expr())
        return node

    def not_test(self):
        # 'not' not_test | comparison
        if self.current_token.type == NOT:
            op = self.current_token
            self.eat(NOT)
            return UnaryOp(op, self.not_test())
        return self.comparison()

    def and_test(self):
        # not_test ('and' not_test)*
        node = self.not_test()
        while self.current_token.type == AND:
            op = self.current_token
            self.eat(AND)
            node = BinOp(node, op, self.not_test())
        return node

    def or_test(self):
        # and_test ('or' and_test)*
        node = self.and_test()
        while self.current_token.type == OR:
            op = self.current_token
            self.eat(OR)
            node = BinOp(node, op, self.and_test())
        return node

    def test(self):
        # or_test ['if' or_test 'else' test] | lambdef
        if self.current_token.type == LAMBDA:
            pass
        node = self.or_test()
        if self.current_token == IF:
            self.eat(IF)
            req = self.or_test()
            self.eat(ELSE)
            right = self.test()
            return IfElse(node, req, right)
        return node

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
        if self.current_token.type == DOT:
            self.eat(DOT)
            self.eat(DOT)
            self.eat(DOT)
            return Token('OMIT', '...')
        pass

    def arglist(self):
        pass

    def subscriptlist(self):
        pass

    def trailer(self):
        # '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
        if self.current_token.type == LB:
            lb = self.current_token
            self.eat(LB)
            token = self.arglist()
            self.eat(RB)
            return UnaryOp(lb, token)

        if self.current_token.type == LSB:
            lsb = self.current_token
            self.eat(LSB)
            token = self.subscriptlist()
            self.eat(RSB)
            return UnaryOp(lsb, token)

        dot = self.current_token
        self.eat(DOT)
        token = self.current_token
        self.eat(ID)
        return UnaryOp(dot, token)

    def atom_expr(self):
        # [AWAIT] atom trailer*
        _await = None
        if self.current_token.type == AWAIT:
            _await = self.current_token
            self.eat(AWAIT)

        node = self.atom()
        while self.current_token.type in (LB, LSB, DOT):
            right = self.trailer()
            node = BinOp(node, right.op, right)
        return UnaryOp(_await, node) if _await else node

    def power(self):
        # atom_expr ['**' factor]
        node = self.atom_expr()
        if self.current_token.type == POWER:
            op = self.current_token
            self.eat(POWER)
            node = BinOp(node, op, self.factor())
        return node

    def factor(self):
        # ('+'|'-'|'~') factor | power
        if self.current_token.type in (ADD, SUB, OPPO):
            op = self.current_token
            self.eat(op.type)
            token = self.factor()
            return UnaryOp(op, token)
        return self.power()

    def term(self):
        # factor (('*'|'@'|'/'|'%'|'//') factor)*
        node = self.factor()
        while self.current_token.type in (MUL, DEC, REAL_DIV, YU, DIV):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.factor())
        return node

    def arith_expr(self):
        # term (('+'|'-') term)*
        node = self.term()
        while self.current_token.type in (ADD, SUB):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.term())
        return node

    def shift_expr(self):
        # arith_expr (('<<'|'>>') arith_expr)*
        node = self.arith_expr()
        while self.current_token.type in (LL, RR):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.arith_expr())
        return node

    def and_expr(self):
        # shift_expr ('&' shift_expr)*
        node = self.shift_expr()
        while self.current_token.type == ET:
            op = self.current_token
            self.eat(ET)
            node = BinOp(node, op, self.shift_expr())
        return node

    def xor_expr(self):
        # and_expr ('^' and_expr)*
        node = self.and_expr()
        while self.current_token.type == DIF:
            op = self.current_token
            self.eat(DIF)
            node = BinOp(node, op, self.and_expr())
        return node

    def expr(self):
        # xor_expr ('|' xor_expr)*
        node = self.xor_expr()
        while self.current_token == SHU:
            op = self.current_token
            self.eat(SHU)
            node = BinOp(node, op, self.xor_expr())
        return node

    def star_expr(self):
        # '*' expr
        op = self.current_token
        self.eat(MUL)
        return UnaryOp(op, self.expr())

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

    def testlist_star_expr(self):
        # (test|star_expr) (',' (test|star_expr))* [',']
        if self.current_token.type == MUL:
            node = self.star_expr()
        else:
            node = self.test()
        if self.current_token.type == COMMA:
            tokens = []
            tokens.append(node)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                try:
                    if self.current_token.type == MUL:
                        tokens.append(self.star_expr())
                    else:
                        tokens.append(self.test())
                except SynError:
                    break
            return Token('testlist_star_expr', tokens) if len(tokens) > 1 else node
        return node

    def testlist(self):
        # test (',' test)* [',']
        node = self.test()
        if self.current_token.type == COMMA:
            tokens = []
            tokens.append(node)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                try:
                    tokens.append(self.test())
                except SynError:
                    break
            return Token('testlist', tokens) if len(tokens) > 1 else node
        return node

    def annassign(self):
        # ':' test ['=' test]
        pass

    def expr_stmt(self):
        # testlist_star_expr (annassign | augassign (yield_expr|testlist) |
        #  ('=' (yield_expr|testlist_star_expr))*)
        node = self.testlist_star_expr()

        if self.current_token.type == COLON:
            pass

        if self.current_token.type == AUGASSIGN:
            op = self.current_token
            self.eat(AUGASSIGN)
            if self.current_token.type == YIELD:
                pass
            return BinOp(node, op, self.testlist())

        while self.current_token.type == ASSIGN:
            op = self.current_token
            self.eat(ASSIGN)
            pass

        return node

    def small_stmt(self):
        #(expr_stmt | del_stmt | pass_stmt | flow_stmt |
        #  import_stmt | global_stmt | nonlocal_stmt | assert_stmt)
        cur_token = self.current_token
        if cur_token.value == 'del':
            pass
        if cur_token.type == PASS_STMT:
            pass
        if cur_token.type in (BREAK, CONTINUE, RET, YIELD, RAISE):
            pass
        if cur_token.type in (FROM, IMPORT):
            pass
        if cur_token.type == GLOBAL:
            pass
        if cur_token.type == NONLOCAL:
            pass
        if cur_token.type == ASSERT:
            pass
        return self.expr_stmt()

    def simple_stmt(self):
        # small_stmt (';' small_stmt)* [';'] NEWLINE
        tokens = []
        node = self.simple_stmt()
        tokens.append(node)
        while self.current_token.type == CEMI:
            self.eat(CEMI)
            tokens.append(self.small_stmt())
        self.eat(NEWLINE)
        return Token('simple_stmt', tokens) if len(tokens) > 1 else node

    def compound_stmt(self):
        # if_stmt | while_stmt | for_stmt | try_stmt
        # | with_stmt | funcdef | classdef | decorated | async_stmt
        pass

    def stmt(self):
        # simple_stmt | compound_stmt
        if self.current_token.type in (IF, WHILE, FOR, TRY, WITH, DEF, CLASS, DEC, ASYNC):
            pass
        return self.simple_stmt()

    def eval_input(self):
        # testlist NEWLINE* ENDMARKER
        pass

    def file_input(self):
        # (NEWLINE | stmt)* ENDMARKER
        tokens = []
        while True:
            if self.current_token.type == NEWLINE:
                tokens.append(self.current_token)
                self.eat(NEWLINE)
            else:
                tokens.append(self.stmt())
            if self.current_token.type == ENDMARKER:
                return Token('file_input', tokens)

    def single_input(self):
        # NEWLINE | simple_stmt | compound_stmt NEWLINE
        pass

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
