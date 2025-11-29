import sys
import re
import json

constants = {}

TOKEN_RE = re.compile(
    r'@"[^"]*"|'                     # строка
    r'-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|'  # число
    r'\(|\)|->|\$|;|'               # символы
    r'[_a-z]+|'                     # имя
    r'\S'                           # недопустимый символ
)

def tokenize(text: str):
    tokens = []
    for match in TOKEN_RE.finditer(text):
        tok = match.group()
        if tok.startswith('@'):
            tokens.append(('string', tok[2:-1]))
        elif tok == '(':
            tokens.append(('array_start', tok))
        elif tok == ')':
            tokens.append(('array_end', tok))
        elif tok == '->':
            tokens.append(('arrow', tok))
        elif tok == ';':
            tokens.append(('semicolon', tok))
        elif tok == '$':
            tokens.append(('dollar', tok))
        elif re.fullmatch(r'-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?', tok):
            if '.' in tok or 'e' in tok.lower():
                tokens.append(('number', float(tok)))
            else:
                tokens.append(('number', int(tok)))
        elif re.fullmatch(r'[_a-z]+', tok):
            tokens.append(('name', tok))
        else:
            raise SyntaxError(f"Недопустимый символ: '{tok}' в позиции {match.start()}")
    return tokens

def parse_array(tokens, i):
    arr = []
    i += 1  # пропустить '('
    while i < len(tokens) and tokens[i][0] != 'array_end':
        val, i = parse_value(tokens, i)
        arr.append(val)
    if i >= len(tokens):
        raise SyntaxError("Незакрытый массив: отсутствует закрывающая скобка ')'")
    return arr, i + 1  # пропустить ')'

def evaluate_postfix(expr_tokens):
    stack = []
    for typ, val in expr_tokens:
        if typ in ('number', 'name'):
            if typ == 'name':
                if val not in constants:
                    raise NameError(f"Неопределённая константа: '{val}'")
                val = constants[val]
            stack.append(val)
        elif val == '+':
            stack.append(stack.pop(-2) + stack.pop())
        elif val == '-':
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif val == '*':
            stack.append(stack.pop(-2) * stack.pop())
        elif val == 'mod()':
            b = stack.pop()
            a = stack.pop()
            stack.append(a % b)
        elif val == 'print()':
            if stack:
                print(f"[print()] {stack[-1]}", file=sys.stderr)
        else:
            raise SyntaxError(f"Неизвестный оператор или функция: '{val}'")
    if len(stack) != 1:
        raise ValueError("Некорректное выражение: результат не определён однозначно")
    return stack[0]

def parse_value(tokens, i):
    typ, val = tokens[i]
    if typ == 'number' or typ == 'string':
        return val, i + 1
    elif typ == 'array_start':
        return parse_array(tokens, i)
    elif typ == 'dollar':
        i += 1
        expr = []
        while i < len(tokens) and tokens[i][0] != 'dollar':
            expr.append(tokens[i])
            i += 1
        if i >= len(tokens):
            raise SyntaxError("Незакрытое выражение: отсутствует завершающий символ '$'")
        result = evaluate_postfix(expr)
        return result, i + 1
    else:
        raise SyntaxError(f"Неожиданный токен в позиции значения: '{val}'")

def main():
    global constants
    text = sys.stdin.read()
    if not text.strip():
        json.dump({}, sys.stdout, ensure_ascii=False, indent=2)
        return

    try:
        tokens = tokenize(text)
        constants = {}
        i = 0
        while i < len(tokens):
            val, i = parse_value(tokens, i)
            if i < len(tokens) and tokens[i][0] == 'arrow':
                i += 1
                if i >= len(tokens) or tokens[i][0] != 'name':
                    raise SyntaxError("Ожидалось имя после '->'")
                name = tokens[i][1]
                i += 1
                if i >= len(tokens) or tokens[i][0] != 'semicolon':
                    raise SyntaxError("Ожидалась точка с запятой ';' после имени")
                i += 1
                constants[name] = val
            else:
                raise SyntaxError("В корне разрешены только конструкции вида: значение -> имя;")
        json.dump(constants, sys.stdout, ensure_ascii=False, indent=2)
    except (SyntaxError, NameError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()