#!/usr/bin/env python3
"""Rule lint for Roblox Luau snippets. Pure Python, no Luau tooling needed.
FAIL = violates a plugin rule. WARN = review. This is NOT a type checker or a runtime test."""
import re

def strip_comments_and_strings(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.S)
    out = []
    for line in code.split('\n'):
        out.append(re.sub(r'--.*$', '', re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "''", line)))
    return '\n'.join(out)

def strip_comments_only(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.S)
    return '\n'.join(re.sub(r'--.*$', '', line) for line in code.split('\n'))

def context_of(code):
    server = bool(re.search(r'ServerScriptService|OnServerEvent|DataStoreService|ProcessReceipt|PlayerRemoving|BindToClose', code))
    client = bool(re.search(r'LocalPlayer|UserInputService|PreRender|RenderStepped|BindToRenderStep|ScreenGui|CurrentCamera|OnClientEvent|ContextActionService', code))
    return server, client

RULES = [
  # (rule_id, severity, regex applied to comment-stripped code unless raw=True, message, raw)
  ('deprecated.wait',     'FAIL', r'(?<![\w.:])wait\(',                          'wait() is deprecated, use task.wait', False),
  ('deprecated.tick',     'FAIL', r'(?<![\w.:])tick\(\)',                        'tick() is deprecated, use os.clock / GetServerTimeNow', False),
  ('deprecated.spawn',    'FAIL', r'(?<![\w.:])(spawn|delay)\(',                 'spawn()/delay() deprecated, use task.spawn/task.delay', False),
  ('deprecated.bodymover','FAIL', r'\bBody(Velocity|Position|Gyro|Force|AngularVelocity)\b', 'legacy body mover, use constraints', False),
  ('deprecated.setprimary','FAIL', r'SetPrimaryPartCFrame',                       'use Model:PivotTo', False),
  ('deprecated.connect',  'FAIL', r':connect\(',                                 'lowercase :connect is deprecated', False),
  ('deprecated.velocity', 'FAIL', r'(?<!self)\.(Velocity|RotVelocity)\s*=',      'BasePart.Velocity is deprecated, use AssemblyLinearVelocity', False),
  ('style.instance_new_parent', 'FAIL', r"Instance\.new\(\s*''\s*,\s*[^)]+\)", 'Instance.new with parent arg: set Parent last', False),
  ('asset.zero_id',       'FAIL', r'rbxassetid://0\b',                           'unmarked placeholder asset id', True),
  ('stub.todo_here',      'FAIL', r'--[^\n]*\b(here)\b\s*$',                    'stub comment instead of implementation', True),
  ('stub.empty_function', 'FAIL', r'function\s*[\w.:]*\s*\([^)]*\)\s*(?:--[^\n]*\n\s*)*end', 'function with empty or comment-only body', True),
]

def lint(code, kind='code'):
    findings = []
    raw_lines = code.split('\n')
    clean = strip_comments_and_strings(code)
    for rid, sev, rx, msg, raw in RULES:
        target = code if raw else clean
        for m in re.finditer(rx, target, flags=re.M):
            line_no = target[:m.start()].count('\n') + 1
            # allow explicit documented placeholders, and prose mentions in comments handled by clean text
            line_text = raw_lines[line_no - 1] if line_no - 1 < len(raw_lines) else ''
            if rid == 'stub.empty_function' and line_text.lstrip().startswith('--'):
                continue
            findings.append({'rule': rid, 'severity': sev, 'line': line_no, 'message': msg, 'text': m.group(0).strip()[:90]})
    server, client = context_of(strip_comments_only(code))
    if client and not server and re.search(r'TakeDamage\(|\.Health\s*=', clean):
        findings.append({'rule': 'authority.client_damage', 'severity': 'FAIL', 'line': 0, 'message': 'damage applied in a client-only script', 'text': ''})
    client_nonrender = bool(re.search(r'LocalPlayer|UserInputService|ScreenGui|CurrentCamera|OnClientEvent|ContextActionService', strip_comments_only(code)))
    if server and not client_nonrender and re.search(r'RenderStepped|PreRender|BindToRenderStep', clean):
        findings.append({'rule': 'context.render_on_server', 'severity': 'FAIL', 'line': 0, 'message': 'render-step API in server code', 'text': ''})
    # connections with no stored handle (warning only; some are intentionally permanent)
    for m in re.finditer(r'^\s*(?:RunService|game:GetService\(\'RunService\'\))\.\w+:Connect\(', clean, flags=re.M):
        findings.append({'rule': 'lifecycle.unstored_connection', 'severity': 'WARN', 'line': clean[:m.start()].count('\n') + 1,
                         'message': 'frame connection without stored handle/cleanup path', 'text': m.group(0).strip()[:60]})
    return findings

if __name__ == '__main__':
    import sys, json
    code = open(sys.argv[1], encoding='utf-8').read() if len(sys.argv) > 1 else sys.stdin.read()
    res = lint(code)
    print(json.dumps(res, indent=2))
    sys.exit(1 if any(f['severity'] == 'FAIL' for f in res) else 0)
