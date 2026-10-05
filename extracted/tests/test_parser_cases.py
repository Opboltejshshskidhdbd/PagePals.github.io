import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from luau_parser import check

VALID = {
 'basic': "local x = 1\nlocal function f(a, b)\n  return a + b\nend\nprint(f(1, 2))",
 'if_elseif': "if a then x = 1 elseif b then x = 2 else x = 3 end",
 'loops': "for i = 1, 10, 2 do continue end\nfor k, v in pairs(t) do print(k, v) end\nwhile true do break end\nrepeat local z = 1 until z == 1",
 'compound': "local n = 0\nn += 1\nn -= 2\nn *= 3\nn //= 2\ns ..= 'x'",
 'ifexpr': "local v = if a then 1 elseif b then 2 else 3",
 'types': "type P = {x: number, y: number?}\nexport type Cb<T...> = (T...) -> ()\nlocal function f<T>(a: T, ...: number): (T, string)\n  return a, 'x'\nend\nlocal m: {[string]: number} = {}\nlocal u = x :: number",
 'interp': "local s = `hello {name}, you have {#items + 1} items`",
 'strings': "local a = [[long\nstring]]\nlocal b = [==[ ]] ]==]\nlocal c = 'it\\'s'\n--[[ block\ncomment ]]\n--[=[ x ]=]",
 'tables': "local t = {1, 2, 3; a = 1, ['k'] = 2, f = function() end, {nested = true},}",
 'calls': "print 'hi'\nfoo{1,2}\nobj:Method 'x'\ngame:GetService('Players').PlayerAdded:Connect(function(p) end)",
 'varargs': "local function f(...) return select('#', ...) end\nlocal t = {...}",
 'numbers': "local a = 0xFF + 0b101 + 1e5 + 3.14 + .5 + 1_000_000",
 'return_in_do': "local function f()\n  do return end\n  print('x')\nend",
 'continue_ident': "local continue = 5\ncontinue = 6",
 'fn_identifier': "local function connect(fn)\n  fn(1)\nend",
 'attr_const': "local x <const> = 5",
}
INVALID = {
 'missing_end': ("local function f()\n  if x then\n    return 1\nend", 'expected'),
 'not_equal_bang': ("if a != b then end", "unexpected symbol '!'"),
 'else_if_missing_end': ("if a then\n x()\nelse if b then\n y()\nend", 'expected'),
 'missing_then': ("if a == 1\n  x()\nend", "expected 'then'"),
 'missing_do': ("for i = 1, 3\n  x()\nend", "expected 'do'"),
 'plusplus': ("local i = 0\ni++", None),
 'extra_end': ("local x = 1\nend", "unexpected 'end'"),
 'code_after_return': ("local function f()\n  return 1\n  print('x')\nend", "'return' must be the last"),
 'code_after_module_return': ("return M\nlocal x = 2", "'return' must be the last"),
 'table_missing_comma': ("local t = {\n  a = 1\n  b = 2\n}", "expected ',' or"),
 'and_symbols': ("if a && b then end", None),
 'unfinished_string': ("local s = 'abc\nprint(s)", 'unfinished string'),
 'js_declaration': ("let x = 1", "not a Luau keyword"),
 'braces_block': ("if a then { x() }", None),
 'ternary': ("local v = a ? 1 : 2", None),
 'assign_to_call': ("f() = 1", None),
 'break_outside': ("local function f()\n  break\nend", 'outside of a loop'),
 'vararg_outside': ("local function f()\n  return ...\nend", 'vararg'),
 'null_kw': ("local x = null\nx", None),
 'missing_paren': ("print('a'", None),
 'ifexpr_no_else': ("local v = if a then 1", "needs an 'else'"),
 'bare_expression': ("local x = 1\nx + 1", 'not a statement'),
 'c_comment': ("// comment\nlocal x = 1", None),
}

def test_parser_cases():
    problems = []
    for name, code in VALID.items():
        r = check(code)
        if not r['ok']: problems.append(f"FALSE REJECT {name}: {r['error']}")
    for name, (code, frag) in INVALID.items():
        r = check(code)
        if r['ok']: problems.append(f'FALSE ACCEPT {name}')
        elif frag and frag not in r['error']: problems.append(f"WRONG MESSAGE {name}: {r['error']}")
    assert not problems, problems
