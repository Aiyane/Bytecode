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
DIV = 'DIV'  # //
REAL_DIV = 'REAL_DIV'  # /
YU = 'YU'  # %
ADDE = 'ADDE'  # +=
SUBE = 'SUBE'  # -=
MULE = 'MULE'  # *=
DIVE = 'DIVE'  # //=
REAL_DIVE = 'REAL_DIVE'  # /=
YUE = 'YUE'  # %=
GT = 'GT'  # >
GE = 'GE'  # >=
LT = 'LT'  # <
LE = 'LE'  # <=
EQ = 'EQ'  # ==
NE = 'NE'  # !=
EOF = 'EOF'
INT = 'INT'
OINT = 'OINT'
BINT = 'BINT'
XINT = 'XINT'
FLOAT = 'FLOAT'
ID = 'ID'
STR = 'STR'
BSTR = 'BSTR'
TAB = 'TAB'
NEWLINE = 'NEWLINE'
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
PASS = 'PASS'
EXCEPT = 'EXCEPT'
IN = 'IN'
RAISE = 'RAISE'


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
    'pass': Token(PASS, 'PASS'),
    'except': Token(EXCEPT, 'EXCEPT'),
    'in': Token(IN, 'IN'),
    'raise': Token(RAISE, 'RAISE'),
}


class CharacterError(Exception):
    pass


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.tab_level = 0
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        # 向前取一个字符, 当前字符向前移动
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        # 向前取一个字符, 当前字符不变
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def peekn(self, n):
        # 向前取n个字符
        peek_pos = self.pos + n
        if 0 == n or peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[self.pos+1:peek_pos+1]

    def skip_whitespace(self):
        # 跳过空白字符
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        # 跳过单行注释
        while self.current_char != '\n':
            self.advance()
        self.advance()

    def count_tab_level(self, line):
        # 计算缩进级别
        tab_level = 0
        while line[tab_level*4:(tab_level+1)*4] == ' '*4:
            tab_level += 1
        return tab_level

    def stringliteral(self):
        # [stringprefix](shortstring | longstring)

        result = ''

        if self.current_char in ("r", "u", "R", "U", "f", "F"):
            result += self.stringprefix()

        if self.current_char in ("'", '"'):
            quote = self.current_char
            if self.peekn(2) in ("''", '""'):
                result += self.longstring(quote)
            else:
                result += self.shortstring(quote)
            return Token(STR, result)

        self.error()

    def stringprefix(self):
        # "r" | "u" | "R" | "U" | "f" | "F"
        # | "fr" | "Fr" | "fR" | "FR" | "rf" | "rF" | "Rf" | "RF"
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
        # "'" shortstringitem* "'" | '"' shortstringitem* '"'
        result = ''
        if self.current_char == quote:
            result = quote
            self.advance()

            while True:
                if self.current_char == None:
                    self.error()

                if self.current_char == quote:
                    result += quote
                    self.advance()
                    break

                result += self.shortstringitem(quote)
            return result

        self.error()

    def longstring(self, quote):
        # '''" longstringitem* "'''" | '"""' longstringitem* '"""'
        result = ''
        _loop_num = 3

        while _loop_num != 0 and self.current_char == quote:
            self.advance()
            _loop_num -= 1

        if _loop_num != 0:
            self.error()

        result = quote*3

        while True:
            if self.current_char == None:
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
        # shortstringchar | stringescapeseq

        result = ''

        if self.current_char == '\\':
            result = self.stringescapeseq()
        elif self.current_char not in ('\n', quote):
            result = self.shortstringchar(quote)
        else:
            self.error()

        return result

    def longstringitem(self):
        # longstringchar | stringescapeseq

        result = ''

        if self.current_char == '\\':
            result = self.stringescapeseq()
        elif self.current_char:
            result = self.longstringchar()
        else:
            self.error()

        return result

    def shortstringchar(self, quote):
        # <任意非"\" 换行 引号字符>
        result = ''

        if self.current_char not in ('\\', '\n', quote):
            result = self.current_char
            self.advance()
            return result

        self.error()

    def longstringchar(self):
        # <任意非"\"字符>
        result = ''

        if self.current_char != '\\':
            result = self.current_char
            self.advance()
            return result

        self.error()

    def stringescapeseq(self):
        # "\" <任意字符>
        result = ''

        if self.current_char == '\\':
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            return result

        self.error()

    def bytesliteral(self):
        # bytesprefix(shortbytes | longbytes)

        result = ''
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
        # "b" | "B" | "br" | "Br" | "bR" | "BR" | "rb" | "rB" | "Rb" | "RB"
        if self.current_char in ("b", "B", "r", "R"):
            result = self.current_char

            if result in ("r", "R") and self.peek() in ("B", "b") or self.peek() in ("r", "R"):
                result += self.peek()
                self.advance()

            self.advance()
            return result

        self.error()

    def shortbytes(self, quote):
        # "'" shortbytesitem* "'" | '"' shortbytesitem* '"'
        result = ''
        if self.current_char == quote:
            result += quote
            self.advance()

            while True:
                if self.current_char == None:
                    self.error()

                if self.current_char == quote:
                    result += quote
                    self.advance()
                    break

                result += self.shortbytesitem(quote)
            return result

        self.error()

    def longbytes(self, quote):
        # "'''" longbytesitem* "'''" | '"""' longbytesitem* '"""'
        result = ''
        _loop_num = 3

        while _loop_num != 0 and self.current_char == quote:
            self.advance()
            _loop_num -= 1

        if _loop_num != 0:
            self.error()

        result = quote*3

        while True:
            if self.current_char == None:
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
        # shortbyteschar | bytesescapeseq
        result = ''

        if self.current_char == '\\':
            result = self.bytesescapeseq()
        elif self.current_char not in ('\n', quote):
            result = self.shortbyteschar(quote)
        else:
            self.error()

        return result

    def longbytesitem(self):
        # longbyteschar | bytesescapeseq
        result = ''

        if self.current_char == '\\':
            result = self.bytesescapeseq()
        elif self.current_char:
            result = self.longbyteschar()
        else:
            self.error()

        return result

    def shortbyteschar(self, quote):
        # <任意非"\" 换行 引号字符>
        result = ''

        if self.current_char not in ('\\', '\n', quote) and ord(self.current_char) < 128:
            result = self.current_char
            self.advance()
            return result

        self.error()

    def longbyteschar(self):
        # <任意非"\"字符>
        result = ''

        if self.current_char != '\\' and ord(self.current_char) < 128:
            result = self.current_char
            self.advance()
            return result

        self.error()

    def bytesescapeseq(self):
        # "\" <任意ASCII字符>
        result = ''

        if self.current_char == '\\' and ord(self.current_char) < 128:
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            return result

        self.error()

    def _id(self):
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
        while self.current_char is not None and cur_char.isalnum() or cur_char == '_':
            result += self.current_char
            self.advance()

        return KEY_WORDS.get(result, Token(ID, result))

    def basedigit(self, items):
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
        # "0" ("x" | "X") (["_"] hexdigit)+
        return self.baseinteger(("x", "X"), self.hexdigit)

    def octinteger(self):
        # "0" ("o" | "O") (["_"] octdigit)+
        return self.baseinteger(("o", "O"), self.octdigit)

    def bininteger(self):
        # "0" ("b" | "B") (["_"] bindigit)+
        return self.baseinteger(("b", "B"), self.bindigit)

    def decinteger(self):
        # nonzerodigit (["_"] digit)* | "0"+ (["_"] "0")*
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
        # decinteger | bininteger | octinteger | hexinteger
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
        # digit (["_"] digit)*
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
        # "." digitpart
        if self.current_char == ".":
            result = '.'
            self.advance()
            result += self.digitpart()
            return result

        self.error()

    def exponent(self):
        # ("e" | "E") ["+" | "-"] digitpart
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
        # [digitpart] fraction | digitpart "."
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
        # (digitpart | pointfloat) exponent
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
        # pointfloat | exponentfloat
        pos = self.pos
        try:
            result = self.exponentfloat()
        except CharacterError:
            self.pos = pos
            self.current_char = self.text[self.pos]
            result = self.pointfloat()

        return result

    def imagnumber(self):
        # (floatnumber | digitpart) ("j" | "J")
        try:
            result = self.floatnumber()
        except CharacterError:
            result = self.digitpart()

        if self.current_char in ("j", "J"):
            result += self.current_char
            self.advance()
            return result

        self.error()

    def number(self):
        pos = self.pos
        try:
            return Token(FLOAT, float(self.floatnumber()))
        except CharacterError:
            self.pos = pos
            self.current_char = self.text[self.pos]
            return self.integer()

    def error(self):
        raise CharacterError('Invalid character')

    def get_next_token(self):
        while self.current_char is not None:

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

            if self.current_char == "(":
                return Token(LB, "(")

            if self.current_char == ")":
                return Token(RB, ")")

            if self.current_char == "[":
                return Token(LSB, "[")

            if self.current_char == "]":
                return Token(RSB, "]")

            if self.current_char == "{":
                return Token(LCB, "{")

            if self.current_char == "}":
                return Token(RCB, "}")

            if self.current_char == ",":
                return Token(COMMA, ",")

            if self.current_char == ":":
                return Token(COLON, ":")

            if self.current_char == ".":
                return Token(DOT, ".")

            if self.current_char == ";":
                return Token(CEMI, ";")

# Operators
# +       -       *       **      /       //      %      @
# <<      >>      &       |       ^       ~
# <       >       <=      >=      ==      !=

# Delimiters
# (       )       [       ]       {       }
# ,       :       .       ;       @       =       ->
# +=      -=      *=      /=      //=     %=      @=
# &=      |=      ^=      >>=     <<=     **=

# special
# '       "       #       \

# error
# $       ?       `


def main():
    # with open('test.py', "r", encoding="utf8") as f:
    #     for token in Lexer(f).tokenize():
    #         print(token)
    test = """
r\"hello\"
u\"hello\"
R\"hello\"
U\"hello\"
f\"hello\"
F\"hello\"
fr\"hello\"
Fr\"hello\"
fR\"hello\"
FR\"helo\"
rf\"hello\"
rF\"hello\"
Rf'hello'
RF'hello'
b\"hello\"
B\"\"\"hello
hello\"\"\"
br'hello'
Br'hello'
bR'''hello
hello'''
'hello'
"hello"
"hello\b"
\"\"\"hello\r
hello\"\"\"
'''hello
hello'''
2147483647
0o177    
0b100110111
0xdeadbeef
100_000_000_000
0b_1110_0101
3.14
10.
.001
1e100
3.14e-10
0e0
3.14_15_93
"""
    lexer = Lexer(test)
    while True:
        token = lexer.get_next_token()
        if token is None:
            break
        print(token)


if __name__ == '__main__':
    main()
