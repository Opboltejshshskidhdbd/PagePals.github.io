#!/usr/bin/env python3
"""Luau syntax checker (pure Python, no dependencies).
Parses Luau source (statements, expressions, types, if-expressions, compound assignment,
interpolated strings, continue, type aliases) and reports the first syntax error with line:col.
Also flags a few compile-time errors: break/continue outside a loop, '...' outside a vararg function.
It is NOT a type checker and NOT a runtime test. Usage: python luau_syntax.py file.luau"""
import re, sys

KEYWORDS = {'and','break','do','else','elseif','end','false','for','function','if','in','local','nil',
            'not','or','repeat','return','then','true','until','while'}
OPS3 = ['...', '..=', '//=']
OPS2 = ['..', '==', '~=', '<=', '>=', '+=', '-=', '*=', '/=', '%=', '^=', '//', '->', '::']
OPS1 = set('+-*/%^#<>=(){}[];:,.&|?@')
COMPOUND = {'+=', '-=', '*=', '/=', '%=', '^=', '..=', '//='}
BLOCK_END = {'end', 'else', 'elseif', 'until'}

class LuauSyntaxError(Exception):
    def __init__(self, line, col, msg, hint=None):
        super().__init__(msg)
        self.line, self.col, self.msg, self.hint = line, col, msg, hint
    def __str__(self):
        return f'{self.line}:{self.col}: {self.msg}' + (f'  (hint: {self.hint})' if self.hint else '')

class Tok:
    __slots__ = ('type', 'value', 'line', 'col')
    def __init__(self, type_, value, line, col):
        self.type, self.value, self.line, self.col = type_, value, line, col
    def __repr__(self): return f'{self.type}:{self.value!r}@{self.line}'

# ------------------------------------------------------------------ lexer
def tokenize(src, line0=1):
    toks, i, n, line, ls = [], 0, len(src), line0, 0
    def err(msg, hint=None): raise LuauSyntaxError(line, i - ls + 1, msg, hint)
    while i < n:
        c = src[i]
        if c == '\n':
            line += 1; i += 1; ls = i; continue
        if c in ' \t\r\f\v':
            i += 1; continue
        # comments
        if src.startswith('--', i):
            m = re.match(r'--\[(=*)\[', src[i:])
            if m:
                close = ']' + m.group(1) + ']'
                j = src.find(close, i + len(m.group(0)))
                if j < 0: err('unfinished long comment')
                line += src.count('\n', i, j); 
                k = src.rfind('\n', i, j)
                if k >= 0: ls = k + 1
                i = j + len(close); continue
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        col = i - ls + 1
        # long string
        m = re.match(r'\[(=*)\[', src[i:])
        if m:
            close = ']' + m.group(1) + ']'
            j = src.find(close, i + len(m.group(0)))
            if j < 0: err('unfinished long string')
            toks.append(Tok('string', src[i:j + len(close)], line, col))
            line += src.count('\n', i, j)
            k = src.rfind('\n', i, j)
            if k >= 0: ls = k + 1
            i = j + len(close); continue
        # names / keywords
        if c.isalpha() or c == '_':
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] == '_'): j += 1
            w = src[i:j]
            toks.append(Tok('keyword' if w in KEYWORDS else 'name', w, line, col))
            i = j; continue
        # numbers
        if c.isdigit() or (c == '.' and i + 1 < n and src[i + 1].isdigit()):
            m = (re.match(r'0[xX][0-9a-fA-F_]+', src[i:]) or re.match(r'0[bB][01_]+', src[i:]) or
                 re.match(r'(?:\d[\d_]*\.?[\d_]*|\.\d[\d_]*)(?:[eE][+-]?\d+)?', src[i:]))
            j = i + len(m.group(0))
            if j < n and (src[j].isalpha() or src[j] == '_'):
                err('malformed number near ' + repr(src[i:j + 1]))
            toks.append(Tok('number', m.group(0), line, col)); i = j; continue
        # strings
        if c in '"\'':
            j = i + 1
            while True:
                if j >= n or src[j] == '\n':
                    err('unfinished string', 'close the quote, or use \\n / [[ ]] for multi-line text')
                if src[j] == '\\':
                    j += 2; continue
                if src[j] == c: break
                j += 1
            toks.append(Tok('string', src[i:j + 1], line, col)); i = j + 1; continue
        # interpolated strings
        if c == '`':
            j, parts = i + 1, []
            while True:
                if j >= n: err('unfinished interpolated string')
                if src[j] == '\\': j += 2; continue
                if src[j] == '`': break
                if src[j] == '{':
                    depth, k = 1, j + 1
                    while k < n and depth:
                        if src[k] == '{': depth += 1
                        elif src[k] == '}': depth -= 1
                        elif src[k] in '"\'':
                            q = src[k]; k += 1
                            while k < n and src[k] != q:
                                k += 2 if src[k] == '\\' else 1
                        k += 1
                    if depth: err('unfinished {expression} in interpolated string')
                    parts.append((src[j + 1:k - 1], line))
                    j = k; continue
                j += 1
            toks.append(Tok('istring', parts, line, col))
            line += src.count('\n', i, j)
            k = src.rfind('\n', i, j)
            if k >= 0: ls = k + 1
            i = j + 1; continue
        # operators
        if src[i:i + 3] in OPS3: toks.append(Tok('op', src[i:i + 3], line, col)); i += 3; continue
        if src[i:i + 2] in OPS2: toks.append(Tok('op', src[i:i + 2], line, col)); i += 2; continue
        if c in OPS1: toks.append(Tok('op', c, line, col)); i += 1; continue
        if c == '!':
            err("unexpected symbol '!'", "Luau uses '~=' for not-equal and 'not x' for negation, never '!='/'!'")
        if c == '$' or c == '\\':
            err(f'unexpected symbol {c!r}')
        err(f'unexpected symbol {c!r}')
    toks.append(Tok('eof', '<eof>', line, i - ls + 1))
    return toks

# ------------------------------------------------------------------ parser
class Parser:
    def __init__(self, toks):
        self.t, self.p = toks, 0
        self.warnings = []
        self.loop_depth = 0
        self.vararg = [True]   # main chunk accepts ...

    # --- helpers
    def peek(self, k=0): return self.t[min(self.p + k, len(self.t) - 1)]
    def next(self):
        tok = self.t[self.p]
        if tok.type != 'eof': self.p += 1
        return tok
    def is_(self, value, k=0):
        tok = self.peek(k); return tok.type in ('op', 'keyword') and tok.value == value
    def accept(self, value):
        if self.is_(value): return self.next()
        return None
    def fail(self, msg, tok=None, hint=None):
        tok = tok or self.peek()
        raise LuauSyntaxError(tok.line, tok.col, msg, hint)
    def near(self, tok=None):
        tok = tok or self.peek()
        return "near <eof>" if tok.type == 'eof' else f"near '{tok.value if tok.type != 'istring' else '`'}'"
    def expect(self, value, what=None, opener=None, hint=None):
        if self.is_(value): return self.next()
        tok = self.peek()
        ctx = f' {what}' if what else ''
        extra = f" (to close '{opener[0]}' opened at line {opener[1]})" if opener else ''
        if tok.type == 'eof' or (value == 'end' and tok.value in BLOCK_END):
            hint = hint or (f"count your blocks: every function/if/for/while/do needs its own 'end'" if value == 'end' else None)
        self.fail(f"expected '{value}'{ctx}{extra} {self.near(tok)}", tok, hint)
    def name(self, what='identifier'):
        tok = self.peek()
        if tok.type == 'name': return self.next()
        hint = None
        if tok.type == 'keyword': hint = f"'{tok.value}' is a reserved word and cannot be used as a name"
        self.fail(f'expected {what} {self.near(tok)}', tok, hint)

    # --- chunk / blocks
    def parse_chunk(self):
        self.parse_block()
        tok = self.peek()
        if tok.type != 'eof':
            if tok.value == 'end':
                self.fail("unexpected 'end' with no open block", tok, "there is one more 'end' than blocks: look for a stray 'end', or an 'else if' that should be 'elseif'")
            self.fail(f"unexpected '{tok.value}' {self.near(tok)}", tok)

    def at_block_end(self):
        tok = self.peek()
        return tok.type == 'eof' or (tok.type == 'keyword' and tok.value in BLOCK_END)

    def parse_block(self):
        while not self.at_block_end():
            if self.is_('return'):
                ret = self.next()
                if not self.at_block_end() and not self.is_(';'):
                    self.parse_exprlist()
                self.accept(';')
                if not self.at_block_end():
                    nxt = self.peek()
                    self.fail(f"'return' must be the last statement in its block, but code follows it {self.near(nxt)}", nxt,
                              f"'return' at line {ret.line} ends the block: move this code above the return, or wrap the return in 'do return end'")
                return
            self.parse_stat()
            self.accept(';')

    # --- statements
    def parse_stat(self):
        tok = self.peek()
        v = tok.value if tok.type == 'keyword' else None
        if v == 'if': return self.stat_if()
        if v == 'while':
            op = self.next(); self.parse_expr(); self.expect('do', 'after while condition')
            self.loop_depth += 1; self.parse_block(); self.loop_depth -= 1
            return self.expect('end', opener=('while', op.line))
        if v == 'do':
            op = self.next(); self.parse_block(); return self.expect('end', opener=('do', op.line))
        if v == 'for': return self.stat_for()
        if v == 'repeat':
            op = self.next(); self.loop_depth += 1; self.parse_block(); self.loop_depth -= 1
            self.expect('until', opener=('repeat', op.line)); return self.parse_expr()
        if v == 'function':
            op = self.next(); self.name('function name')
            while self.accept('.'): self.name('field name')
            if self.accept(':'): self.name('method name')
            return self.funcbody(op)
        if v == 'local':
            op = self.next()
            if self.is_('function'):
                fn = self.next(); self.name('function name'); return self.funcbody(fn)
            return self.stat_local()
        if v == 'break' or (tok.type == 'name' and tok.value == 'continue' and self.is_continue_stmt()):
            kw = self.next()
            if self.loop_depth == 0:
                self.fail(f"'{kw.value}' used outside of a loop", kw, "break/continue only work inside for/while/repeat")
            return
        if v == 'return': return self.fail("unexpected 'return'")
        if v in ('end', 'else', 'elseif', 'until', 'then', 'in'):
            self.fail(f"unexpected '{v}' {self.near(tok)}", tok)
        if tok.type == 'name' and tok.value == 'type' and self.peek(1).type == 'name' and (self.is_('=', 2) or self.is_('<', 2)):
            return self.stat_type_alias()
        if tok.type == 'name' and tok.value == 'export' and self.peek(1).type == 'name' and self.peek(1).value == 'type':
            self.next(); return self.stat_type_alias()
        if tok.type == 'name' and tok.value in ('var', 'let', 'const', 'def', 'fn', 'func', 'elif') and self.peek(1).type == 'name':
            self.fail(f"'{tok.value}' is not a Luau keyword", tok, {'elif': "use 'elseif'", 'var': "use 'local'", 'let': "use 'local'", 'const': "use 'local'", 'fn': "use 'function'", 'func': "use 'function'", 'def': "use 'function'"}.get(tok.value))
        return self.stat_expr()

    def is_continue_stmt(self):
        nxt = self.peek(1)
        if nxt.type == 'op' and nxt.value in ('=', '.', ':', '(', '[', ',', '{') or nxt.value in COMPOUND:
            return False
        return True

    def stat_if(self):
        op = self.next()
        self.parse_expr(); self.expect('then', 'after if condition')
        self.parse_block()
        while self.is_('elseif'):
            self.next(); self.parse_expr(); self.expect('then', 'after elseif condition'); self.parse_block()
        if self.is_('else'):
            e = self.next()
            if self.is_('if') and self.peek().line == e.line:
                self.warnings.append((e.line, e.col, "'else if' opens a NEW if that needs its own 'end'; use 'elseif'"))
            self.parse_block()
        self.expect('end', opener=('if', op.line))

    def stat_for(self):
        op = self.next()
        n1 = self.name('loop variable')
        if self.is_('='):
            self.next(); self.parse_expr(); self.expect(',', 'in numeric for'); self.parse_expr()
            if self.accept(','): self.parse_expr()
        else:
            if self.accept(':'): self.parse_type()
            while self.accept(','):
                self.name('loop variable')
                if self.accept(':'): self.parse_type()
            self.expect('in', "in generic for (use 'for k, v in pairs(t) do')")
            self.parse_exprlist()
        self.expect('do', 'after for header')
        self.loop_depth += 1; self.parse_block(); self.loop_depth -= 1
        self.expect('end', opener=('for', op.line))

    def stat_local(self):
        self.name('variable name')
        if self.accept(':'): self.parse_type()
        if self.is_('<') and self.peek(1).type == 'name' and self.is_('>', 2):
            self.next(); self.next(); self.next()
        while self.accept(','):
            self.name('variable name')
            if self.accept(':'): self.parse_type()
        if self.accept('='):
            self.parse_exprlist()

    def stat_type_alias(self):
        self.next()  # 'type'
        self.name('type name')
        if self.is_('<'): self.parse_generics()
        self.expect('=', 'in type alias')
        self.parse_type()

    def stat_expr(self):
        start = self.peek()
        kind = self.parse_suffixed()
        tok = self.peek()
        if self.is_('=') or self.is_(','):
            if kind != 'var':
                self.fail('cannot assign to this expression', start, 'only variables, fields and indexes can be assigned')
            while self.accept(','):
                if self.parse_suffixed() != 'var': self.fail('cannot assign to this expression', tok)
            self.expect('=')
            return self.parse_exprlist()
        if tok.type == 'op' and tok.value in COMPOUND:
            if kind != 'var': self.fail('cannot assign to this expression', start)
            self.next(); return self.parse_expr()
        if tok.type == 'op' and tok.value in ('+', '-', '*', '/') and self.peek(1).value == tok.value and tok.value in ('+',):
            self.fail(f"'{tok.value}{tok.value}' is not an operator in Luau", tok, "use 'x += 1' (there is no ++)")
        if kind != 'call':
            if tok.type == 'eof' or self.at_block_end() or True:
                self.fail(f"syntax error: this expression is not a statement {self.near(tok)}", start,
                          "a statement must be a call (f()), an assignment (x = 1 / x += 1), or a keyword statement; check for a missing '=' or an earlier unclosed bracket")

    # --- functions
    def parse_generics(self):
        self.expect('<')
        while True:
            self.name('generic name'); self.accept('...')
            if not self.accept(','): break
        self.expect('>')

    def funcbody(self, opener_tok):
        if self.is_('<'): self.parse_generics()
        self.expect('(', 'to start the parameter list')
        vararg = False
        if not self.is_(')'):
            while True:
                if self.accept('...'):
                    vararg = True
                    if self.accept(':'): self.parse_type()
                    break
                self.name('parameter name')
                if self.accept(':'): self.parse_type()
                if not self.accept(','): break
        self.expect(')', 'to close the parameter list')
        if self.accept(':'): self.parse_type(allow_pack=True)
        saved = self.loop_depth; self.loop_depth = 0; self.vararg.append(vararg)
        self.parse_block()
        self.vararg.pop(); self.loop_depth = saved
        self.expect('end', opener=('function', opener_tok.line))

    # --- expressions
    def parse_exprlist(self):
        self.parse_expr()
        while self.accept(','): self.parse_expr()

    BINPRI = {'or': (1, 1), 'and': (2, 2), '<': (3, 3), '>': (3, 3), '<=': (3, 3), '>=': (3, 3), '~=': (3, 3), '==': (3, 3),
              '..': (5, 4), '+': (6, 6), '-': (6, 6), '*': (7, 7), '/': (7, 7), '//': (7, 7), '%': (7, 7), '^': (10, 9)}
    UNARY_PRI = 8

    def parse_expr(self, limit=0):
        tok = self.peek()
        if (tok.type == 'keyword' and tok.value == 'not') or (tok.type == 'op' and tok.value in ('-', '#')):
            self.next(); self.parse_expr(self.UNARY_PRI)
        else:
            self.parse_simple()
        while True:
            op = self.peek()
            key = op.value if op.type in ('op', 'keyword') else None
            if key in ('&&', '||'): pass
            if op.type == 'op' and op.value in ('&', '|'):
                self.fail(f"'{op.value}' is not an expression operator in Luau", op,
                          "use 'and' / 'or' (the symbols & and | only appear in type annotations); bitwise ops live in the bit32 library")
            pri = self.BINPRI.get(key) if key else None
            if not pri or pri[0] <= limit: break
            self.next(); self.parse_expr(pri[1])
            if self.is_('?') :
                self.fail("'?' is not a ternary operator in Luau", self.peek(), "use 'if cond then a else b' as an expression, or 'cond and a or b'")

    def parse_simple(self):
        tok = self.peek()
        if tok.type in ('number', 'string'):
            self.next()
        elif tok.type == 'istring':
            self.next()
            for text, ln in tok.value:
                if not text.strip(): self.fail('empty {} in interpolated string', tok)
                sub = Parser(tokenize(text, ln)); sub.vararg = list(self.vararg)
                sub.parse_expr()
                if sub.peek().type != 'eof': self.fail('unexpected token in interpolated expression', tok)
        elif tok.type == 'keyword' and tok.value in ('nil', 'true', 'false'):
            self.next()
        elif tok.type == 'op' and tok.value == '...':
            self.next()
            if not self.vararg[-1]:
                self.fail("cannot use '...' outside of a vararg function", tok, "declare the function as function(...)")
        elif tok.type == 'op' and tok.value == '{':
            self.table()
        elif tok.type == 'keyword' and tok.value == 'function':
            self.next(); self.funcbody(tok)
        elif tok.type == 'keyword' and tok.value == 'if':
            self.if_expr()
        else:
            self.parse_suffixed()
        while self.accept('::'):
            self.parse_type()

    def if_expr(self):
        self.next(); self.parse_expr(); self.expect('then', 'in if-expression'); self.parse_expr()
        while self.is_('elseif'):
            self.next(); self.parse_expr(); self.expect('then', 'in if-expression'); self.parse_expr()
        if not self.is_('else'):
            self.fail(f"if-expression needs an 'else' branch {self.near()}", None, "an expression 'if a then b' without else is invalid; write 'if a then b else c'")
        self.next(); self.parse_expr()

    def parse_suffixed(self):
        tok = self.peek()
        if tok.type == 'name':
            self.next(); kind = 'var'
        elif self.is_('('):
            self.next(); self.parse_expr(); self.expect(')', 'to close the parenthesized expression'); kind = 'other'
        else:
            hint = None
            if tok.type == 'keyword' and tok.value in ('nil', 'true', 'false', 'function'): hint = None
            if tok.type == 'name' and tok.value in ('null', 'undefined'): hint = "use 'nil'"
            self.fail(f'unexpected symbol {self.near(tok)}' if tok.type != 'eof' else 'unexpected end of input, expected an expression', tok, hint)
        while True:
            tok = self.peek()
            if self.is_('.'):
                self.next(); self.name('field name after \'.\''); kind = 'var'
            elif self.is_('['):
                self.next(); self.parse_expr(); self.expect(']', 'to close the index'); kind = 'var'
            elif self.is_(':') :
                self.next(); self.name('method name after \':\'')
                if not (self.is_('(') or self.peek().type in ('string', 'istring') or self.is_('{')):
                    self.fail(f"expected call arguments after method name {self.near()}", None, "a method call needs parentheses: obj:Method()")
                self.call_args(); kind = 'call'
            elif self.is_('(') or tok.type in ('string', 'istring') or self.is_('{'):
                self.call_args(); kind = 'call'
            else:
                return kind

    def call_args(self):
        tok = self.peek()
        if tok.type in ('string', 'istring'):
            return self.parse_simple()
        if self.is_('{'): return self.table()
        op = self.expect('(')
        if not self.is_(')'):
            self.parse_exprlist()
        if not self.is_(')'):
            nxt = self.peek()
            self.fail(f"expected ')' to close the call opened at line {op.line} {self.near(nxt)}", nxt,
                      "missing ')' or ',' between arguments")
        self.next()

    def table(self):
        op = self.expect('{')
        while not self.is_('}'):
            if self.is_('['):
                self.next(); self.parse_expr(); self.expect(']'); self.expect('=', 'in table field')
                self.parse_expr()
            elif self.peek().type == 'name' and self.is_('=', 1):
                self.next(); self.next(); self.parse_expr()
            else:
                self.parse_expr()
            if self.accept(',') or self.accept(';'): continue
            if not self.is_('}'):
                nxt = self.peek()
                self.fail(f"expected ',' or '}}' in the table opened at line {op.line} {self.near(nxt)}", nxt,
                          "a comma is missing between table entries (or a bracket above is unclosed)")
        self.next()

    # --- types
    def parse_type(self, allow_pack=False):
        self.type_atom(allow_pack)
        while True:
            if self.accept('?'): continue
            if self.is_('|') or self.is_('&'):
                self.next(); self.type_atom(); continue
            break

    def type_list(self, close):
        while not self.is_(close):
            if self.peek().type == 'name' and self.is_(':', 1):
                self.next(); self.next()
            self.parse_type()
            if not self.accept(','): break
        self.expect(close)

    def type_atom(self, allow_pack=False):
        tok = self.peek()
        if tok.type in ('string', 'number') or (tok.type == 'keyword' and tok.value in ('nil', 'true', 'false')):
            self.next(); return
        if tok.type == 'op' and tok.value == '...':
            self.next(); self.parse_type(); return
        if tok.type == 'op' and tok.value == '{':
            self.next()
            while not self.is_('}'):
                if self.is_('['):
                    self.next(); self.parse_type(); self.expect(']'); self.expect(':'); self.parse_type()
                elif self.peek().type == 'name' and self.is_(':', 1):
                    self.next(); self.next(); self.parse_type()
                else:
                    self.parse_type()
                if not (self.accept(',') or self.accept(';')): break
            self.expect('}', 'to close the table type'); return
        if tok.type == 'op' and tok.value == '(':
            self.next(); count = 0
            while not self.is_(')'):
                if self.peek().type == 'name' and self.is_(':', 1): self.next(); self.next()
                self.parse_type(); count += 1
                if not self.accept(','): break
            self.expect(')')
            if self.accept('->'):
                self.parse_type(allow_pack=True)
            elif count != 1 and not allow_pack:
                self.fail('expected a single type or a function type', tok)
            return
        if tok.type == 'name':
            self.next()
            if tok.value == 'typeof' and self.is_('('):
                self.next(); self.parse_expr(); self.expect(')'); return
            while self.accept('.'): self.name('type name')
            if self.is_('<'):
                self.next(); self.type_list('>')
            self.accept('...')
            return
        self.fail(f'expected a type {self.near(tok)}', tok)

# ------------------------------------------------------------------ public API
def check(source):
    """Returns {'ok': bool, 'error': 'line:col: msg' | None, 'hint': str|None, 'warnings': [..]}"""
    try:
        toks = tokenize(source)
        p = Parser(toks)
        p.parse_chunk()
        return {'ok': True, 'error': None, 'hint': None, 'line': None,
                'warnings': [f'{l}:{c}: {m}' for l, c, m in p.warnings]}
    except LuauSyntaxError as e:
        return {'ok': False, 'error': f'{e.line}:{e.col}: {e.msg}', 'hint': e.hint, 'line': e.line, 'warnings': []}
    except RecursionError:
        return {'ok': False, 'error': '0:0: nesting too deep for this checker', 'hint': None, 'line': 0, 'warnings': []}

def main():
    src = open(sys.argv[1], encoding='utf-8').read() if len(sys.argv) > 1 else sys.stdin.read()
    r = check(src)
    for w in r['warnings']: print('warning', w)
    if r['ok']:
        print('SYNTAX OK (parsed fully; this is not a type check or a runtime test)')
        return 0
    print('SYNTAX ERROR', r['error'])
    if r['hint']: print('hint:', r['hint'])
    lines = src.split('\n')
    if r['line'] and 0 < r['line'] <= len(lines): print(f"  {r['line']:4d} | {lines[r['line'] - 1]}")
    return 1

if __name__ == '__main__':
    sys.exit(main())
