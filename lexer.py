#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
# parse.py
# 终结符号
LB = 'LB'  # (
RB = 'RB'  # )
LCB = 'LCB'  # {
RCB = 'RCB'  # }
LSB = 'LSB'  # [
RSB = 'RSB'  # ]
ASSIGN = 'ASSIGN'  # =
COLON = 'COLON'  # :
CEMI = 'CEMI'  # ;
COMMA = 'COMMA'  # ,
DOT = 'DOT'  # .
ADD = 'ADD'  # +
SUB = 'SUB'  # -
MUL = 'MUL'  # *
ET = 'ET'  # &
SHU = 'SHU'  # |
OPPO = 'OPPO'  # ~
DIF = 'DIF'  # ^
OPIN = 'OPIN'  # ->
POWER = 'POWER'  # **
AUGASSIGN = 'AUGASSIGN'
DEC = 'DEC'  # @
DIV = 'DIV'  # //
REAL_DIV = 'REAL_DIV'  # /
YU = 'YU'  # %
COMP_OP = 'COMP_OP'
LL = 'LL'  # <<
RR = 'RR'  # >>
ES = 'ES'  # \
EOF = 'EOF'
INT = 'INT'
OINT = 'OINT'
BINT = 'BINT'
XINT = 'XINT'
FLOAT = 'FLOAT'
INUM = 'INUM'
ID = 'ID'
STR = 'STR'
BSTR = 'BSTR'
NEWLINE = 'NEWLINE'
INDENT = 'INDENT'
DEDENT = 'DEDENT'
ENDMARKER = 'ENDMARKER'
# 关键词
IS = 'IS'
CONTINUE = 'CONTINUE'
BREAK = 'BREAK'
WHILE = 'WHILE'
FOR = 'FOR'
RET = 'RET'
IF = 'IF'
ELIF = 'ELIF'
ELSE = 'ELSE'
DEF = 'DEF'
NOT = 'NOT'
OR = 'OR'
AND = 'AND'
TRUE = 'TRUE'
FALSE = 'FALSE'
NONE = 'NONE'
CLASS = 'CLASS'
FINALLY = 'FINALLY'
LAMBDA = 'LAMBDA'
TRY = 'TRY'
FROM = 'FROM'
NONLOCAL = 'NONLOCAL'
GLOBAL = 'GLOBAL'
WITH = 'WITH'
AS = 'AS'
YIELD = 'YIELD'
ASSERT = 'ASSERT'
IMPORT = 'IMPORT'
PASS_STMT = 'PASS_STMT'
EXCEPT = 'EXCEPT'
IN = 'IN'
RAISE = 'RAISE'
AWAIT = 'AWAIT'
ASYNC = 'ASYNC'


# 令牌类
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
    'is': Token(IS, 'IS'),
    'continue': Token(CONTINUE, 'CONTINUE'),
    'break': Token(BREAK, 'BREAK'),
    'while': Token(WHILE, 'WHILE'),
    'for': Token(FOR, 'FOR'),
    'return': Token(RET, 'RET'),
    'if': Token(IF, 'IF'),
    'elif': Token(ELIF, 'ELIF'),
    'else': Token(ELSE, 'ELSE'),
    'def': Token(DEF, 'DEF'),
    'not': Token(NOT, 'NOT'),
    'or': Token(OR, 'OR'),
    'and': Token(AND, 'AND'),
    'True': Token(TRUE, 'TRUE'),
    'False': Token(FALSE, 'FALSE'),
    'None': Token(NONE, 'NONE'),
    'class': Token(CLASS, 'CLASS'),
    'finally': Token(FINALLY, 'FINALLY'),
    'lambda': Token(LAMBDA, 'LAMBDA'),
    'try': Token(TRY, 'TRY'),
    'from': Token(FROM, 'FROM'),
    'nonlocal': Token(NONLOCAL, 'NONLOCAL'),
    'global': Token(GLOBAL, 'GLOBAL'),
    'with': Token(WITH, 'WITH'),
    'as': Token(AS, 'AS'),
    'yield': Token(YIELD, 'YIELD'),
    'assert': Token(ASSERT, 'ASSERT'),
    'import': Token(IMPORT, 'IMPORT'),
    'pass': Token(PASS_STMT, 'PASS_STMT'),
    'except': Token(EXCEPT, 'EXCEPT'),
    'in': Token(IN, 'IN'),
    'raise': Token(RAISE, 'RAISE'),
    'await': Token(AWAIT, 'AWAIT'),
    'async': Token(ASYNC, 'ASYNC'),
}

# 分割符号表
SIGOTABLE = {
    '(': Token(LB, '('),
    ')': Token(RB, ')'),
    '[': Token(LSB, '['),
    ']': Token(RSB, ']'),
    '{': Token(LCB, '{'),
    '}': Token(RCB, '}'),
    ',': Token(COMMA, ','),
    ':': Token(COLON, ':'),
    '.': Token(DOT, '.'),
    ';': Token(CEMI, ';'),
}


# 字符错误
class CharacterError(Exception):
    pass


class Lexer(object):
    def __init__(self, text):
        """
        text: 代码全文
        pos: 当前指针
        current_cur: 当前字符
        tab: 前一个缩进级别
        temp_token: 需要返回的令牌
        """
        self.text = ''.join([text, '\n'])
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.tab = 0
        self.temp_token = []

    def advance(self):
        """向前取一个字符, 当前字符向前移动"""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """向前取一个字符, 当前字符不变"""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def peekn(self, n):
        """向前取n个字符"""
        peek_pos = self.pos + n
        if 0 == n or peek_pos > len(self.text) - 1:
            return None
        return self.text[self.pos+1:peek_pos+1]

    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """跳过单行注释"""
        while self.current_char != '\n':
            self.advance()
        self.advance()

    def stringliteral(self):
        """[stringprefix](shortstring | longstring)"""

        result = ''

        # stringprefix 的 FIRST 集为 {"r", "u", "R", "U", "f", "F"}
        if self.current_char in ("r", "u", "R", "U", "f", "F"):
            result += self.stringprefix()

        # longstring 字符串以 """ 或 ''' 包裹的字符串。
        # shortstring 字符串以 ' 或 " 包裹的字符串。 
        if self.current_char in ("'", '"'):
            quote = self.current_char
            if self.peekn(2) in ("''", '""'):
                result += self.longstring(quote)
            else:
                result += self.shortstring(quote)
            return Token(STR, result)

        self.error()

    def stringprefix(self):
        """字符串前缀
        "r" | "u" | "R" | "U" | "f" | "F"
        | "fr" | "Fr" | "fR" | "FR" | "rf" | "rF" | "Rf" | "RF" 
        """
        if self.current_char in ("r", "u", "R", "U", "f", "F"):
            result = self.current_char

            if (result in ("f", "F") and self.peek() in ("R", "r") or
                    result in ("r", "R") and self.peek() in ("F", "f")):
                result += self.peek()
                self.advance()

            self.advance()
            return result

        self.error()

    def shortstring(self, quote):
        """字符串
        quote: 字符串包裹的字符，" 或 '
        "'" shortstringitem* "'" | '"' shortstringitem* '"'
        """
        result = ''
        if self.current_char == quote:
            result = quote
            self.advance()

            while True:
                if self.current_char is None:
                    self.error()

                if self.current_char == quote:
                    result += quote
                    self.advance()
                    break

                result += self.shortstringitem(quote)
            return result

        self.error()

    def longstring(self, quote):
        """字符串
        quote: 字符串包裹的字符，" (3个) 或 ' (3个)
        "'''" longstringitem* "'''" | '"""' longstringitem* '"""'
        """
        result = ''
        _loop_num = 3

        while _loop_num != 0 and self.current_char == quote:
            self.advance()
            _loop_num -= 1

        if _loop_num != 0:
            self.error()

        result = quote*3

        while True:
            if self.current_char is None:
                self.error()
            if self.current_char == quote and self.peekn(2) == quote*2:
                break
            result += self.longstringitem()

        self.advance()
        self.advance()
        self.advance()
        result += quote*3

        return result

    def shortstringitem(self, quote):
        """shortstringchar | stringescapeseq"""

        result = ''
        # stringescapeseq 的 FIRST 集为 '\'
        if self.current_char == '\\':
            result = self.stringescapeseq()
        elif self.current_char not in ('\n', quote):
            result = self.shortstringchar(quote)
        else:
            self.error()

        return result

    def longstringitem(self):
        """longstringchar | stringescapeseq"""

        result = ''
        # stringescapeseq 的 FIRST 集为 '\'
        if self.current_char == '\\':
            result = self.stringescapeseq()
        elif self.current_char:
            result = self.longstringchar()
        else:
            self.error()

        return result

    def shortstringchar(self, quote):
        """ <任意非"\" 换行 引号字符> """
        result = ''

        if self.current_char not in ('\\', '\n', quote):
            result = self.current_char
            self.advance()
            return result

        self.error()

    def longstringchar(self):
        """ <任意非"\"字符> """
        result = ''

        if self.current_char != '\\':
            result = self.current_char
            self.advance()
            return result

        self.error()

    def stringescapeseq(self):
        """ "\" <任意字符> """
        result = ''

        if self.current_char == '\\':
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            return result

        self.error()

    def bytesliteral(self):
        """bytesprefix(shortbytes | longbytes)"""

        result = ''
        # bytesprefix 的 FIRST 集为 {"b", "B", "r", "R"}
        if self.current_char in ("b", "B", "r", "R"):
            result += self.bytesprefix()
        else:
            self.error()

        if self.current_char in ("'", '"'):
            quote = self.current_char
            if self.peekn(2) in ("''", '""'):
                result += self.longbytes(quote)
            else:
                result += self.shortbytes(quote)
            return Token(BSTR, result)

        self.error()

    def bytesprefix(self):
        """二进制字符串前缀
        "b" | "B" | "br" | "Br" | "bR" | "BR" | "rb" | "rB" | "Rb" | "RB"
        """
        if self.current_char in ("b", "B", "r", "R"):
            result = self.current_char

            if result in ("r", "R") and self.peek() in ("B", "b") or self.peek() in ("r", "R"):
                result += self.peek()
                self.advance()

            self.advance()
            return result

        self.error()

    def shortbytes(self, quote):
        """ "'" shortbytesitem* "'" | '"' shortbytesitem* '"' """
        result = ''
        if self.current_char == quote:
            result += quote
            self.advance()

            while True:
                if self.current_char is None:
                    self.error()

                if self.current_char == quote:
                    result += quote
                    self.advance()
                    break

                result += self.shortbytesitem(quote)
            return result

        self.error()

    def longbytes(self, quote):
        """ "'''" longbytesitem* "'''" | '"""' longbytesitem* '"""' """
        result = ''
        _loop_num = 3

        while _loop_num != 0 and self.current_char == quote:
            self.advance()
            _loop_num -= 1

        if _loop_num != 0:
            self.error()

        result = quote*3

        while True:
            if self.current_char is None:
                self.error()
            if self.current_char == quote and self.peekn(2) == quote*2:
                break
            result += self.longbytesitem()

        self.advance()
        self.advance()
        self.advance()
        result += quote*3

        return result

    def shortbytesitem(self, quote):
        """ shortbyteschar | bytesescapeseq """
        result = ''

        if self.current_char == '\\':
            result = self.bytesescapeseq()
        elif self.current_char not in ('\n', quote):
            result = self.shortbyteschar(quote)
        else:
            self.error()

        return result

    def longbytesitem(self):
        """ longbyteschar | bytesescapeseq """
        result = ''

        if self.current_char == '\\':
            result = self.bytesescapeseq()
        elif self.current_char:
            result = self.longbyteschar()
        else:
            self.error()

        return result

    def shortbyteschar(self, quote):
        """ <任意非"\" 换行 引号字符> """
        result = ''

        if self.current_char not in ('\\', '\n', quote) and ord(self.current_char) < 128:
            result = self.current_char
            self.advance()
            return result

        self.error()

    def longbyteschar(self):
        """ <任意非"\"字符> """
        result = ''

        if self.current_char != '\\' and ord(self.current_char) < 128:
            result = self.current_char
            self.advance()
            return result

        self.error()

    def bytesescapeseq(self):
        """ "\" <任意ASCII字符> """
        result = ''

        if self.current_char == '\\' and ord(self.current_char) < 128:
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            return result

        self.error()

    def _id(self):
        """ 变量名 """
        cur_char = self.current_char
        next_char = self.peek()
        next_next_char = self.peekn(2)[1]

        if cur_char in ("b", "B") and next_char in ("'", '"'):
            return self.bytesliteral()

        if (cur_char in ("B", "b") and next_char in ("R", "r") or
                cur_char in ("R", "r") and next_char in ("B", "b")):
            if next_next_char in ('"', "'"):
                return self.bytesliteral()

        if cur_char in ("r", "R", "u", "U", "f", "F") and next_char in ("'", '"'):
            return self.stringliteral()

        if (cur_char in ("f", "F") and next_char in ("R", "r") or
                cur_char in ("R", "r") and next_char in ("F", "f")):
            if next_next_char in ("'", '"'):
                return self.stringliteral()

        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        return KEY_WORDS.get(result, Token(ID, result))

    def basedigit(self, items):
        """ 数字 """
        if self.current_char in items:
            result = self.current_char
            self.advance()
            return result

    def digit(self):
        # "0"..."9"
        return self.basedigit(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))

    def nonzerodigit(self):
        # "1"..."9"
        return self.basedigit(("1", "2", "3", "4", "5", "6", "7", "8", "9"))

    def bindigit(self):
        # "0" | "1"
        return self.basedigit(("0", "1"))

    def octdigit(self):
        # "0"..."7"
        return self.basedigit(("0", "1", "2", "3", "4", "5", "6", "7"))

    def hexdigit(self):
        # digit | "a"..."f" | "A"..."F"
        return self.basedigit(("0", "1", "2", "3", "4", "5", "6", "7", "8",
                               "9", "a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"))

    def baseinteger(self, head, digit_func):
        """ int 类型 """
        if self.current_char == '0' and self.peek() in head:
            result = self.current_char
            self.advance()
            result += self.current_char
            self.advance()

            has_error = True
            while True:
                if self.current_char == '_':
                    result += self.current_char
                    self.advance()

                temp_num = digit_func()
                if temp_num:
                    result += temp_num
                    has_error = False
                else:
                    break

            if has_error:
                self.error()

            return result

    def hexinteger(self):
        """ "0" ("x" | "X") (["_"] hexdigit)+ """
        return self.baseinteger(("x", "X"), self.hexdigit)

    def octinteger(self):
        """ "0" ("o" | "O") (["_"] octdigit)+ """
        return self.baseinteger(("o", "O"), self.octdigit)

    def bininteger(self):
        """ "0" ("b" | "B") (["_"] bindigit)+ """
        return self.baseinteger(("b", "B"), self.bindigit)

    def decinteger(self):
        """ nonzerodigit (["_"] digit)* | "0"+ (["_"] "0")* """
        result = ''

        if self.current_char == "0":
            while self.current_char == "0":
                result += "0"
                self.advance()

            while True:
                if self.current_char == '_':
                    result += '_'
                    self.advance()

                if self.current_char == "0":
                    result += "0"
                    self.advance()
                else:
                    break

            return result

        result = self.nonzerodigit()
        if result:
            has_error = False
            while True:
                if self.current_char == '_':
                    has_error = True
                    result += self.current_char
                    self.advance()

                temp_num = self.digit()
                if temp_num:
                    result += temp_num
                    has_error = False
                else:
                    break

            if has_error:
                self.error()

            return result

        self.error()

    def integer(self):
        """int类型 
        decinteger | bininteger | octinteger | hexinteger """
        if self.current_char.isdigit():
            if self.current_char == "0":
                if self.peek() in ("o", "O"):
                    return Token(OINT, int(self.octinteger(), 8))

                if self.peek() in ("b", "B"):
                    return Token(BINT, int(self.bininteger(), 2))

                if self.peek() in ("x", "X"):
                    return Token(XINT, int(self.hexinteger(), 16))

            return Token(INT, int(self.decinteger()))

        self.error()

    def digitpart(self):
        """ digit (["_"] digit)* """
        if self.current_char.isdigit():
            result = self.digit()

            while True:
                if self.current_char == '_':
                    result += '_'
                    self.advance()

                if self.current_char.isdigit():
                    result += self.digit()
                else:
                    break

            return result

        self.error()

    def fraction(self):
        """ "." digitpart """
        if self.current_char == ".":
            result = '.'
            self.advance()
            result += self.digitpart()
            return result

        self.error()

    def exponent(self):
        """ ("e" | "E") ["+" | "-"] digitpart """
        if self.current_char in ("e", "E"):
            result = self.current_char
            self.advance()

            if self.current_char in ("+", "-"):
                result += self.current_char
                self.advance()

            result += self.digitpart()
            return result

        self.error()

    def pointfloat(self):
        """ [digitpart] fraction | digitpart "." """
        result = ''
        if self.current_char.isdigit():
            result = self.digitpart()

            if self.current_char == '.':
                if self.peek().isdigit():
                    result += self.fraction()
                    return result

                result += '.'
                self.advance()
                return result
            self.error()

        if self.current_char == '.':
            return self.fraction()

        self.error()

    def exponentfloat(self):
        """ (digitpart | pointfloat) exponent """
        pos = self.pos
        try:
            result = self.pointfloat()
        except CharacterError:
            self.pos = pos
            self.current_char = self.text[self.pos]
            result = self.digitpart()

        result += self.exponent()
        return result

    def floatnumber(self):
        """ pointfloat | exponentfloat """
        pos = self.pos
        try:
            result = self.exponentfloat()
        except CharacterError:
            self.pos = pos
            self.current_char = self.text[self.pos]
            result = self.pointfloat()

        return result

    def imagnumber(self):
        """ (floatnumber | digitpart) ("j" | "J") """
        pos = self.pos
        try:
            result = self.floatnumber()
        except CharacterError:
            self.pos = pos
            self.current_char = self.text[pos]
            result = self.digitpart()

        if self.current_char in ("j", "J"):
            result += self.current_char
            self.advance()
            cur_char = self.current_char
            if cur_char.isalpha() or cur_char.isdigit():
                self.error()
            return result

        self.error()

    def number(self):
        """ 数字 """
        pos = self.pos
        try:
            return Token(INUM, complex(self.imagnumber()))
        except CharacterError:
            try:
                self.pos = pos
                self.current_char = self.text[self.pos]
                return Token(FLOAT, float(self.floatnumber()))
            except CharacterError:
                self.pos = pos
                self.current_char = self.text[self.pos]
                return self.integer()

    def other(self):
        """ 操作符 """
        if self.current_char == '>':
            if self.peekn(2) == ">=":
                self.advance()
                self.advance()
                self.advance()
                return Token(AUGASSIGN, ">>=")

            if self.peek() == '>':
                self.advance()
                self.advance()
                return Token(RR, ">>")

            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(COMP_OP, ">=")

            self.advance()
            return Token(COMP_OP, ">")

        if self.current_char == '<':
            if self.peekn(2) == "<=":
                self.advance()
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "<<=")

            if self.peek() == '<':
                self.advance()
                self.advance()
                return Token(LL, "<<")

            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(COMP_OP, "<=")

            self.advance()
            return Token(COMP_OP, "<")

        if self.current_char == '\\':
            self.advance()
            return Token(ES, "\\")

        if self.current_char == '~':
            self.advance()
            return Token(OPPO, '~')

        if self.current_char == '^':
            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "^=")
            self.advance()
            return Token(DIF, "^")

        if self.current_char == '!' and self.peek() == "=":
            self.advance()
            self.advance()
            return Token(COMP_OP, "!=")

        if self.current_char == "&":
            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "&=")
            self.advance()
            return Token(ET, '&')

        if self.current_char == '|':
            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "|=")
            self.advance()
            return Token(SHU, "|")

        if self.current_char == "@":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(AUGASSIGN, '@=')
            self.advance()
            return Token(DEC, "@")

        if self.current_char == "=":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(COMP_OP, "==")
            self.advance()
            return Token(ASSIGN, "=")

        if self.current_char == "%":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "%=")

            self.advance()
            return Token(YU, "%")

        if self.current_char == "+":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "+=")

            self.advance()
            return Token(ADD, "+")

        if self.current_char == "-":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "-=")

            if self.peek() == ">":
                self.advance()
                self.advance()
                return Token(OPIN, "->")

            self.advance()
            return Token(SUB, "-")

        if self.current_char == '*':
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "*=")

            if self.peek() == "*":
                self.advance()
                self.advance()
                return Token(POWER, "**")

            if self.peekn(2) == "*=":
                self.advance()
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "**=")

            self.advance()
            return Token(MUL, "*")

        if self.current_char == '/':
            if self.peek() == '=':
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "/=")

            if self.peekn(2) == '/=':
                self.advance()
                self.advance()
                self.advance()
                return Token(AUGASSIGN, "//=")

            if self.peek() == "/":
                self.advance()
                self.advance()
                return Token(DIV, "//")

            self.advance()
            return Token(REAL_DIV, "/")

    def error(self):
        raise CharacterError('Invalid character')

    def get_next_token(self):
        if self.temp_token:
            token = self.temp_token.pop(0)
            # token = self.temp_token
            # self.temp_token = None
            return token

        while self.current_char is not None:
            if self.current_char == '\n':
                self.advance()
                tab = 0
                while self.current_char is not None and self.current_char.isspace():
                    tab = tab + 1 if self.current_char != '\n' else 0
                    self.advance()
                if self.current_char == '#':
                    self.advance()
                    self.skip_comment()
                    if not self.current_char.isspace():
                        return Token(NEWLINE, tab)
                    continue
                if (tab - self.tab) // 4 > 0:
                    self.tab = tab
                    return Token(INDENT, INDENT)
                if (self.tab - tab) // 4 > 0:
                    while self.tab != tab:
                        self.tab -= 4
                        self.temp_token.append(Token(DEDENT, DEDENT))

                self.tab = tab
                return Token(NEWLINE, tab)

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == '_':
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '.':
                if self.peek().isdigit():
                    return self.number()

            if self.current_char in ('"', "'"):
                return self.stringliteral()

            token = SIGOTABLE.get(self.current_char)
            if token:
                self.advance()
                return token

            return self.other()

        return Token(ENDMARKER, 'ENDMARKER')


if __name__ == '__main__':
    with open('test2.py', "r", encoding="utf8") as f:
        text = f.read()

    lexer = Lexer(text)
    while True:
        token = lexer.get_next_token()
        print(token)
        if token.type == ENDMARKER:
            break
