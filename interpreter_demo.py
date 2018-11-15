import re

number = re.compile(r'^\d+$')
operation = re.compile(r'\((?P<op>(?:\+|-|\*|/))\s+(?P<e1>(?:\(.*\)|\d+|\w))\s+(?P<e2>(?:\(.*\)|\d+|\w))\)$')
function = re.compile(r'^\(lambda \((?P<x>\w)\)\s+(?P<e>(?:\(.*\)|d+|\w))\)$')
bind = re.compile(r'^\(let\s+\(\[(?P<x>\w)\s+(?P<e1>(?:\(.*\)|\d+|\w))\]\)\s+(?P<e2>(?:\(.*\)|\d+|\w))\)$')
call= re.compile(r'^\((?P<e1>(?:\(.*\)|\w))\s+(?P<e2>(?:\(.*\)|\d+|\w))\)$')
variable = re.compile(r'^\w$')

def interpreter(exp):
    env = dict()
    return interp(exp, env)

def interp(exp, env):
    if number.match(exp):
        return int(exp)

    if variable.match(exp):
        v = env.get(exp)
        if not v:
            raise KeyError("变量未定义！")
        else:
            return v

    if operation.match(exp):
        res = operation.match(exp)
        v1 = interp(res.group('e1'), env)
        v2 = interp(res.group('e2'), env)
        op = res.group('op')
        if op == '+':
            return v1 + v2
        if op == '-':
            return v1 - v2
        if op == '*':
            return v1 * v2
        if op == '/':
            return v1 / v2

    if bind.match(exp):
        res = bind.match(exp)
        v1 = interp(res.group('e1'), env)
        env[res.group('x')] = v1
        return interp(res.group('e2'), env)

    if function.match(exp):
        closure = [function.match(exp), env.copy()]
        return closure

    if call.match(exp):
        res = call.match(exp)
        v1 = interp(res.group('e1'), env)
        v2 = interp(res.group('e2'), env)
        if isinstance(v1, list):
            env.update(v1[1])
            env[v1[0].group('x')] = v2
            return interp(v1[0].group('e'), env)

if __name__ == "__main__":
    print(interpreter('(+ 1 2)'))
    print(interpreter('(* 2 3)'))
    print(interpreter('(* 2 (+ 3 4))'))
    print(interpreter('(* (+ 1 2) (+ 3 4))'))
    print(interpreter('((lambda (x) (* 2 x)) 3)'))
    print(interpreter('(((lambda (y) (lambda (x) (+ (* 2 x) y))) 3) 1)'))
    print(interpreter('(let ([x 2]) (let ([f (lambda (y) (* x y))]) (f 3)))'))
    print(interpreter('(let ([x 2]) (let ([f (lambda (y) (* x y))]) (let ([x 4]) (f 3))))'))
