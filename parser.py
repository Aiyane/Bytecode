#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# pasrer.py
import operator

from lexer import *

BINARY_OPERATORS = {
    POWER: operator.pow,
    MUL: operator.mul,
    REAL_DIV: operator.floordiv,
    DIV: operator.truediv,
    YU: operator.mod,
    ADD: operator.add,
    SUB: operator.sub,
    LSB: operator.getitem,
    LL: operator.lshift,
    RR: operator.rshift,
    ET: operator.and_,
    DIF: operator.xor,
    SHU: operator.or_,
    NOT: operator.not_,
    IS: operator.is_,
    'is': operator.is_,
    'not': operator.not_,
    '<': operator.lt,
    '<=': operator.le,
    'is not': operator.is_not,
    '-': operator.neg,
    '+': operator.pos,
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '[]': operator.getitem,
    '~': operator.invert,
}


def real_str(token):
    if not isinstance(token, Token):
        raise TypeError("参数必须为token类!")
    head = token.value[0]
    for i, ch in enumerate(token.value):
        if ch != head:
            token.value = token.value[i:-i]
            return token


class AST(object):
    pass


class SynError(Exception):
    pass


class Func(AST):
    def __init__(self, name, params, stmt, ret):
        self.name = name
        self.params = params
        self.stmt = stmt
        self.ret = ret


class ForExpr(AST):
    def __init__(self, exprlist, testlist, stmt):
        self.exprlist = exprlist
        self.testlist = testlist
        self.stmt = stmt
        self.other = None


class WhileExpr(AST):
    def __init__(self, condition, stmt):
        self.condition = condition
        self.stmt = stmt
        self.other = None


class WithExpr(AST):
    def __init__(self, token, stmt):
        self.token = token
        self.stmt = stmt


class Class(AST):
    def __init__(self, name, parents, stmt):
        self.name = name
        self.parents = parents
        self.stmt = stmt


class IfExpr(AST):
    def __init__(self):
        self.tokens = []


class IfItem(AST):
    def __init__(self, condition, stmt):
        self.condition = condition
        self.stmt = stmt


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


class ThreeOp(AST):
    def __init__(self, op, left, middle, right):
        # 三目操作符
        self.op = op
        self.left = left
        self.middle = middle
        self.right = right


class Arg(AST):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default


class Args(AST):
    def __init__(self):
        self.args = []


class ListObj(AST):
    def __init__(self):
        self.tokens = []


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.STMTS = {
            # if_stmt | while_stmt | for_stmt | try_stmt
            # | with_stmt | funcdef | classdef | decorated | async_stmt
            IF: self.if_stmt,
            WHILE: self.while_stmt,
            FOR: self.for_stmt,
            TRY: self.try_stmt,
            WITH: self.with_stmt,
            DEF: self.funcdef,
            CLASS: self.classdef,
            DEC: self.decorated,
            ASYNC: self.async_stmt,
        }

    def error(self):
        raise SynError('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            print(self.current_token)
            self.error()

    def comparison(self):
        # expr (comp_op expr)*
        node = self.expr()
        while self.current_token.type in (COMP_OP, IN, NOT, IS):
            # node = BinOp(node, self.comp_op(), self.expr())
            op = self.comp_op()
            node2 = self.expr()
            if isinstance(node.value, (int, complex, float)) and isinstance(
                    node2.value, (int, complex, float)):
                node.value = BINARY_OPERATORS[op.value](node.value,
                                                        node2.value)
            # if op.type == COMP_OP:
            #     try:
            #         node.value = BINARY_OPERATORS[op.value](
            #             node.value, node2.value)
            #     except Exception:
            #         node = BinOp(node, op, node2)
            else:
                node = BinOp(node, op, node2)
        return node

    def not_test(self):
        # 'not' not_test | comparison
        if self.current_token.type == NOT:
            op = self.current_token
            self.eat(NOT)
            # return UnaryOp(op, self.not_test())
            node = self.not_test()
            try:
                node.value = BINARY_OPERATORS[NOT](node.value)
            except Exception:
                node = UnaryOp(op, node)
            return node
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
            root = IfExpr()
            self.eat(IF)
            req = self.or_test()
            root.tokens.append(IfItem(req, node))
            self.eat(ELSE)
            right = self.test()
            root.tokens.append(IfItem(None, right))
            return root
        return node

    def yield_arg(self):
        # 'from' test | testlist
        pass

    def yield_expr(self):
        # 'yield' [yield_arg]
        pass

    def testlist_comp(self):
        # (test|star_expr) ( comp_for | (',' (test|star_expr))* [','] )
        node = self.star_expr(
        ) if self.current_token.type == MUL else self.test()
        root = ListObj()
        if self.current_token.type in (ASYNC, FOR):
            pass

        root.tokens.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            try:
                root.tokens.append(self.star_expr() if self.current_token ==
                                   MUL else self.test())
            except SynError:
                break
        return root if len(root.tokens) > 1 else node

    def dictorsetmaker(self):
        pass

    def atom(self):
        # ('(' [yield_expr|testlist_comp] ')' |
        #    '[' [testlist_comp] ']' |
        #    '{' [dictorsetmaker] '}' |
        #    NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')
        if self.current_token.type in (INT, INUM, FLOAT, OINT, BINT, XINT, ID,
                                       NONE, TRUE, FALSE, STR, BSTR):
            token = self.current_token
            self.eat(token.type)
            if token.type == STR:
                return real_str(token)
            return token
        if self.current_token.type == DOT:
            self.eat(DOT)
            self.eat(DOT)
            self.eat(DOT)
            return Token('OMIT', '...')
        if self.current_token.type == LSB:
            op = self.current_token
            op.value = '[]'
            self.eat(LSB)
            token = self.testlist_comp()
            self.eat(RSB)
            return UnaryOp(op, token)
        if self.current_token == LB:
            op = self.current_token
            op.value = '()'
            self.eat(LB)
            token = self.yield_expr(
            ) if self.current_token.type == YIELD else self.testlist_comp()
            self.eat(RB)
            return UnaryOp(op, token)

        op = self.current_token
        self.eat(LCB)
        token = self.dictorsetmaker()
        self.eat(RCB)
        return UnaryOp(op, token)

    def return_stmt(self):
        # 'return' [testlist]
        op = self.current_token
        self.eat(RET)
        if self.current_token.type in (NEWLINE, DEDENT):
            return op
        else:
            return UnaryOp(op, self.testlist())

    def test_nocond(self):
        # or_test | lambdef_nocond
        if self.current_token.type == LAMBDA:
            pass
        return self.or_test()

    def comp_if(self):
        # 'if' test_nocond [comp_iter]
        self.eat(IF)
        root = IfItem(self.test_nocond(), 0)
        if self.current_token.type in (IF, FOR, ASYNC):
            res = ListObj()
            res.tokens.append(root)
            res.tokens.append(self.comp_iter())
            return res
        return root

    def comp_iter(self):
        # comp_for | comp_if
        if self.current_token.type == IF:
            return self.comp_if()
        return self.comp_for()

    def comp_for(self):
        # [ASYNC] 'for' exprlist 'in' or_test [comp_iter]
        async_expr = None
        if self.current_token.type == ASYNC:
            self.eat(ASYNC)
            async_expr = True
        self.eat(FOR)
        _exprlist = self.exprlist()
        self.eat(IN)
        _testlist = self.or_test()
        root = ForExpr(_exprlist, _testlist, 0)
        if self.current_token.type in (IF, FOR, ASYNC):
            res = ListObj()
            res.tokens.append(root)
            res.tokens.append(self.comp_iter())
            if async_expr:
                return UnaryOp(Token(ASYNC, ASYNC), res)
            return res
        if async_expr:
            return UnaryOp(Token(ASYNC, ASYNC), root)
        return root

    def argument(self):
        # ( test [comp_for] |
        #     test '=' test |
        #         '**' test |
        #          '*' test )
        if self.current_token.type == MUL:
            self.eat(MUL)
            return Arg(self.test(), 1)
        if self.current_token.type == POWER:
            self.eat(POWER)
            return Arg(self.test(), 2)
        name = self.test()
        if self.current_token.type == ASSIGN:
            self.eat(ASSIGN)
            return Arg(name, self.test())
        if self.current_token.type in (FOR, IF, ASYNC):
            comp = self.comp_for()
            return BinOp(name, Token(FOR, FOR), comp)
        return name

    def arglist(self):
        # argument (',' argument)*  [',']
        node = self.argument()
        root = Args()
        root.args.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            if self.current_token.type == RB:
                return root if len(root.args) > 1 else node
            root.args.append(self.argument())
        return root

    def subscriptlist(self):
        # subscript (',' subscript)* [',']
        node = self.subscript()
        root = ListObj()
        root.tokens.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            try:
                root.tokens.append(self.subscript())
            except SynError:
                break
        return root if len(root.tokens) > 1 else node

    def sliceop(self):
        # ':' [test]
        self.eat(COLON)
        return self.test()

    def subscript(self):
        # test | [test] ':' [test] [sliceop]
        test_head = (LAMBDA, NOT, ADD, SUB, OPPO, LB, LCB, LSB, AWAIT, INT,
                     INUM, FLOAT, OINT, BINT, XINT, ID, DOT, NONE, TRUE, FALSE,
                     STR, BSTR)
        node = None
        if self.current_token.type in test_head:
            node = self.test()

        if self.current_token.type == COLON:
            op = self.current_token
            self.eat(COLON)

            if self.current_token.type in test_head:
                middle = self.test()

                if self.current_token.type == COLON:
                    right = self.sliceop()
                    op = Token('slices', ':::')
                    if node:
                        return ThreeOp(op, node, middle, right)
                    return ThreeOp(op, None, middle, right)

                elif node:
                    return BinOp(node, op, middle)
                return BinOp(None, op, middle)

            elif self.current_token.type == COLON:
                right = self.sliceop()
                op = Token('slice', '::')
                if node:
                    return BinOp(node, op, right)
                return BinOp(None, op, right)

            elif node:
                return BinOp(node, op, None)
            return BinOp(None, op, None)

        elif node:
            return node
        self.error()

    def trailer(self):
        # '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
        if self.current_token.type == LB:
            lb = self.current_token
            lb.value = '()'
            self.eat(LB)
            token = self.arglist()
            self.eat(RB)
            return UnaryOp(lb, token)

        if self.current_token.type == LSB:
            lsb = self.current_token
            lsb.value = '[]'
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
            # if right.op.value == '[]':
            #     try:
            #         node.value = BINARY_OPERATORS['[]'](
            #             node.value, right.token.value)
            #     except Exception:
            #         node = BinOp(node, right.op, right)
            # else:
            node = BinOp(node, right.op, right.token)
        return UnaryOp(_await, node) if _await else node

    def power(self):
        # atom_expr ['**' factor]
        node = self.atom_expr()
        if self.current_token.type == POWER:
            op = self.current_token
            self.eat(POWER)
            # node = BinOp(node, op, self.factor())
            node2 = self.factor()
            try:
                node.value = BINARY_OPERATORS[POWER](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def factor(self):
        # ('+'|'-'|'~') factor | power
        if self.current_token.type in (ADD, SUB, OPPO):
            op = self.current_token
            self.eat(op.type)
            token = self.factor()
            # return UnaryOp(op, token)
            try:
                token.value = BINARY_OPERATORS[op.value](token.value)
            except Exception:
                token = UnaryOp(op, token)
            return token
        return self.power()

    def term(self):
        # factor (('*'|'@'|'/'|'%'|'//') factor)*
        node = self.factor()
        while self.current_token.type in (MUL, DEC, REAL_DIV, YU, DIV):
            op = self.current_token
            self.eat(op.type)
            # node = BinOp(node, op, self.factor())
            node2 = self.factor()
            try:
                node.value = BINARY_OPERATORS[op.type](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def arith_expr(self):
        # term (('+'|'-') term)*
        node = self.term()
        while self.current_token.type in (ADD, SUB):
            op = self.current_token
            self.eat(op.type)
            # node = BinOp(node, op, self.term())
            node2 = self.term()
            try:
                node.value = BINARY_OPERATORS[op.type](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def shift_expr(self):
        # arith_expr (('<<'|'>>') arith_expr)*
        node = self.arith_expr()
        while self.current_token.type in (LL, RR):
            op = self.current_token
            self.eat(op.type)
            # node = BinOp(node, op, self.arith_expr())
            node2 = self.arith_expr()
            try:
                node.value = BINARY_OPERATORS[op.type](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def and_expr(self):
        # shift_expr ('&' shift_expr)*
        node = self.shift_expr()
        while self.current_token.type == ET:
            op = self.current_token
            self.eat(ET)
            # node = BinOp(node, op, self.shift_expr())
            node2 = self.shift_expr()
            try:
                node.value = BINARY_OPERATORS[ET](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def xor_expr(self):
        # and_expr ('^' and_expr)*
        node = self.and_expr()
        while self.current_token.type == DIF:
            op = self.current_token
            self.eat(DIF)
            # node = BinOp(node, op, self.and_expr())
            node2 = self.and_expr()
            try:
                node.value = BINARY_OPERATORS[DIF](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
        return node

    def expr(self):
        # xor_expr ('|' xor_expr)*
        node = self.xor_expr()
        while self.current_token == SHU:
            op = self.current_token
            self.eat(SHU)
            # node = BinOp(node, op, self.xor_expr())
            node2 = self.xor_expr()
            try:
                node.value = BINARY_OPERATORS[SHU](node.value, node2.value)
            except Exception:
                node = BinOp(node, op, node2)
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
            return Token(IN, 'in')

        if self.current_token.type == NOT:
            _not = self.current_token
            self.eat(NOT)
            _in = self.current_token
            self.eat(IN)
            return Token('NOTIN', 'not in')

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
            root = ListObj()
            root.tokens.append(node)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                try:
                    if self.current_token.type == MUL:
                        root.tokens.append(self.star_expr())
                    else:
                        root.tokens.append(self.test())
                except SynError:
                    break
            return root if len(root.tokens) > 1 else node
        return node

    def testlist(self):
        # test (',' test)* [',']
        node = self.test()
        root = ListObj()
        root.tokens.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            try:
                root.tokens.append(self.test())
            except SynError:
                break
        return root if len(root.tokens) > 1 else node

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
            if self.current_token.type == YIELD:
                pass
            else:
                right = self.testlist_star_expr()
            node = BinOp(node, op, right)
            # node = BinOp(node, op, right.value)

        return node

    def flow_stmt(self):
        # break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
        if self.current_token.type == RET:
            return self.return_stmt()
        pass

    def small_stmt(self):
        # (expr_stmt | del_stmt | pass_stmt | flow_stmt |
        #  import_stmt | global_stmt | nonlocal_stmt | assert_stmt)
        cur_token = self.current_token
        if cur_token.value == 'del':
            pass
        if cur_token.type == PASS_STMT:
            pass
        if cur_token.type in (BREAK, CONTINUE, RET, YIELD, RAISE):
            return self.flow_stmt()
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
        root = ListObj()
        node = self.small_stmt()
        root.tokens.append(node)
        while self.current_token.type == CEMI:
            self.eat(CEMI)
            root.tokens.append(self.small_stmt())
        self.eat(NEWLINE)
        return root if len(root.tokens) > 1 else node

    def suite(self):
        # simple_stmt | NEWLINE INDENT stmt+ DEDENT
        if self.current_token.type in (NEWLINE, INDENT):
            self.eat(self.current_token.type)
            node = self.stmt()
            root = ListObj()
            root.tokens.append(node)
            while self.current_token.type not in (DEDENT, ENDMARKER):
                root.tokens.append(self.stmt())
            if self.current_token.type == DEDENT:
                self.eat(DEDENT)
            return root if len(root.tokens) > 1 else node

        return self.simple_stmt()

    def if_stmt(self):
        # 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
        root = IfExpr()
        self.eat(IF)
        condition = self.test()
        self.eat(COLON)
        stmt = self.suite()
        root.tokens.append(IfItem(condition, stmt))

        while self.current_token.type == ELIF:
            self.eat(ELIF)
            condition = self.test()
            self.eat(COLON)
            stmt = self.suite()
            root.tokens.append(IfItem(condition, stmt))
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            self.eat(COLON)
            stmt = self.suite()
            root.tokens.append(IfItem(None, stmt))
        return root

    def while_stmt(self):
        # 'while' test ':' suite ['else' ':' suite]
        self.eat(WHILE)
        condition = self.test()
        self.eat(COLON)
        stmt = self.suite()
        root = WhileExpr(condition, stmt)
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            self.eat(COLON)
            other = self.suite()
            for token in root.stmt.tokens:
                if type(token).__name__ == 'IfExpr':
                    root.other = other
                    break
        return root

    def exprlist(self):
        # (expr|star_expr) (',' (expr|star_expr))* [',']
        if self.current_token.type == MUL:
            node = self.star_expr()
        else:
            node = self.expr()
        root = ListObj()
        root.tokens.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            try:
                if self.current_token.type == MUL:
                    root.tokens.append(self.star_expr())
                else:
                    root.tokens.append(self.expr())
            except SynError:
                break
        return root if len(root.tokens) > 1 else node

    def for_stmt(self):
        # 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
        self.eat(FOR)
        _exprlist = self.exprlist()
        self.eat(IN)
        _testlist = self.testlist()
        self.eat(COLON)
        root = ForExpr(_exprlist, _testlist, self.suite())
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            self.eat(COLON)
            other = self.suite()
            for token in root.stmt.tokens:
                if type(token).__name__ == 'IfExpr':
                    root.other = other
                    break
        return root

    def tfpdef(self):
        # NAME [':' test]
        node = self.current_token
        self.eat(ID)
        if self.current_token == COLON:
            op = self.current_token
            self.eat(COLON)
            node = BinOp(node, op, self.test())
        return node

    def typedargslist(self):
        # '**' tfpdef [',']
        if self.current_token.type == POWER:
            self.eat(POWER)
            arg = Arg(self.tfpdef(), 2)
            if self.current_token.type == COMMA:
                self.eat(COMMA)
            return arg
        """
        '*' [tfpdef] (',' tfpdef ['=' test])*
        [
            ','['**' tfpdef [',']]
        ]
        """
        if self.current_token.type == MUL:
            self.eat(MUL)
            args = Args()
            if self.current_token.type == ID:
                arg = Arg(self.tfpdef(), 1)
                args.args.append(arg)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                if self.current_token.type == ID:
                    arg = self.tfpdef()
                    if self.current_token.type == ASSIGN:
                        self.eat(ASSIGN)
                        args.args.append(Arg(arg, self.test()))
                    else:
                        args.args.append(Arg(arg, 0))
                elif self.current_token.type == POWER:
                    args.args.append(self.typedargslist())
                    break
            if len(args.args) == 0:
                return Arg(Token(MUL, '*'))
            return args if len(args.args) > 1 else arg
        """
        tfpdef ['=' test] (',' tfpdef ['=' test])*
        [
            ','
            [
                '*' [tfpdef] (',' tfpdef ['=' test])*
                [
                    ','['**' tfpdef [',']]
                ]
            |
                '**' tfpdef [',']
            ]
        ]
        """
        arg = self.tfpdef()
        if self.current_token.type == ASSIGN:
            self.eat(ASSIGN)
            arg = Arg(arg, self.test())
        else:
            arg = Arg(arg, 0)

        args = Args()
        args.args.append(arg)
        if self.current_token.type == COMMA:
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                if self.current_token.type == ID:
                    arg = self.tfpdef()
                    if self.current_token.type == ASSIGN:
                        args.args.append(Arg(arg, self.test()))
                    else:
                        args.args.append(Arg(arg, 0))
                else:
                    arg = self.typedargslist()
                    if hasattr(arg, 'args'):
                        args.args.extend(arg.args)
                    else:
                        args.args.append(arg)
                    break
        return args if len(args.args) > 1 else arg

    def parameters(self):
        # '(' [typedargslist] ')'
        self.eat(LB)
        if self.current_token.type == RB:
            self.eat(RB)
            return Args()
        node = self.typedargslist()
        self.eat(RB)
        return node

    def funcdef(self):
        # 'def' NAME parameters ['->' test] ':' suite
        self.eat(DEF)
        name = self.current_token
        self.eat(ID)
        params = self.parameters()
        tp = None
        if self.current_token.type == OPIN:
            op = self.eat(OPIN)
            tp = self.test()
        self.eat(COLON)
        stmt = self.suite()
        return Func(name, params, stmt, tp)

    def classdef(self):
        # classdef: 'class' NAME ['(' [arglist] ')'] ':' suite
        self.eat(CLASS)
        name = self.current_token
        self.eat(ID)
        args = None
        if self.current_token.type == LB:
            self.eat(LB)
            args = self.arglist()
            self.eat(RB)
        self.eat(COLON)
        return Class(name, args, self.suite())

    def try_stmt(self):
        # ('try' ':' suite
        #  ((except_clause ':' suite)+
        #   ['else' ':' suite]
        #   ['finally' ':' suite] |
        #   'finally' ':' suite))
        if self.current_token.type == TRY:
            self.eat(TRY)
            self.eat(COLON)
            node = self.suite()
            if self.current_token.type == FINALLY:
                self.eat(FINALLY)
                self.eat(COLON)
                node = self.suite()
            if self.current_token.type == EXCEPT:
                self.eat(EXCEPT)
                self.eat(COLON)
                node = self.suite()
                if self.current_token.type == FINALLY:
                    self.eat(FINALLY)
                    self.eat(COLON)

        pass

    def with_item(self):
        # test ['as' expr]
        node = self.test()
        if self.current_token.type == AS:
            self.eat(AS)
            return BinOp(node, Token(AS, AS), self.expr())
        return node

    def with_stmt(self):
        # 'with' with_item (',' with_item)*  ':' suite
        self.eat(WITH)
        node = self.with_item()
        root = ListObj()
        root.tokens.append(node)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            root.tokens.append(self.with_item())
        self.eat(COLON)
        return WithExpr(root,
                        self.suite()) if len(root.tokens) > 1 else WithExpr(
                            node, self.suite())

    def decorated(self):
        pass

    def async_stmt(self):
        pass

    def compound_stmt(self):
        # if_stmt | while_stmt | for_stmt | try_stmt
        # | with_stmt | funcdef | classdef | decorated | async_stmt
        return self.STMTS[self.current_token.type]()

    def stmt(self):
        # simple_stmt | compound_stmt
        if self.current_token.type in (IF, WHILE, FOR, TRY, WITH, DEF, CLASS,
                                       DEC, ASYNC):
            return self.compound_stmt()
        return self.simple_stmt()

    def eval_input(self):
        # testlist NEWLINE* ENDMARKER
        pass

    def file_input(self):
        # (NEWLINE | stmt)* ENDMARKER
        root = ListObj()
        while True:
            if self.current_token.type == NEWLINE:
                root.tokens.append(self.current_token)
                self.eat(NEWLINE)
            else:
                root.tokens.append(self.stmt())
            if self.current_token.type == ENDMARKER:
                return root

    def single_input(self):
        # NEWLINE | simple_stmt | compound_stmt NEWLINE
        if self.current_token.type == NEWLINE:
            self.eat(NEWLINE)

        pass

    def parse(self):
        node = self.file_input()
        if self.current_token.type != ENDMARKER:
            self.error()

        return node


if __name__ == '__main__':
    with open(
            '/home/aiyane/code/python/Bytecode/test2.py', "r",
            encoding="utf8") as f:
        text = f.read()

    lex = Lexer(text)
    parser = Parser(lex)
    tree = parser.parse()
    print('end')
