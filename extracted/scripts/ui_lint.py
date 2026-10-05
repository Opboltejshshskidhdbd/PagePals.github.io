#!/usr/bin/env python3
"""UI/asset/lifecycle lint for generated Roblox Luau. Pure Python.
Catches the defects seen in generated UIs: emoji used as icons or in logs (render as empty boxes),
fabricated or reused asset IDs, UI under the Roblox top bar, oversized panels, loading text left visible,
and unguarded :Init() calls. FAIL = must fix. WARN = review. Not a layout engine and not a runtime test.
Usage: python scripts/ui_lint.py file.luau [more files]   (exit code 1 when any FAIL)"""
import re, sys, os, json
from collections import Counter

PICTO = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u2190-\u21FF\u2300-\u23FF]')
STRING = re.compile(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"|`[^`\n]*`")

def strip_comments(code):
    code = re.sub(r'--\[(=*)\[.*?\]\1\]', '', code, flags=re.S)
    return '\n'.join(re.sub(r'--.*$', '', l) if "'" not in l and '"' not in l else strip_line_comment(l) for l in code.split('\n'))

def strip_line_comment(line):
    in_s = None; i = 0
    while i < len(line):
        c = line[i]
        if in_s:
            if c == '\\': i += 2; continue
            if c == in_s: in_s = None
        else:
            if c in '\'"`': in_s = c
            elif line.startswith('--', i): return line[:i]
        i += 1
    return line

def lint(code, filename='<source>'):
    out = []
    def add(rule, sev, msg, pos=None):
        out.append({'rule': rule, 'severity': sev, 'message': msg, 'line': (code[:pos].count('\n') + 1) if pos is not None else 0})
    src = strip_comments(code)
    manifest_like = bool(re.search(r'asset|icon|manifest', os.path.basename(filename), re.I))

    # --- emoji
    log_spans = []
    for m in re.finditer(r'\b(print|warn|error)\s*\(', src):
        depth, j = 1, m.end()
        while j < len(src) and depth:
            depth += {'(': 1, ')': -1}.get(src[j], 0); j += 1
        log_spans.append((m.start(), j))
        if PICTO.search(src[m.start():j]):
            add('emoji.in_log', 'FAIL', 'emoji/symbol in print/warn/error renders as an empty box in the output window; use ASCII', m.start())
    for m in STRING.finditer(src):
        if PICTO.search(m.group(0)) and not any(a <= m.start() < b for a, b in log_spans):
            add('emoji.in_ui_text', 'WARN', 'emoji/symbol in a string may render as an empty box; use IconProvider or a drawn badge', m.start())

    # --- asset ids
    ids = [(m.group(1), m.start()) for m in re.finditer(r'rbxassetid://(\d+)', src)]
    counts = Counter(i for i, _ in ids)
    for aid, n in counts.items():
        if n >= 3:
            add('asset.repeated_id', 'FAIL', f'asset id {aid} is used {n} times: one id for several items usually means it is fabricated or a copied placeholder', next(p for i, p in ids if i == aid))
    for aid, pos in ids:
        digits = set(aid)
        if len(aid) < 6 or len(digits) <= 3 or aid in ('123456789', '1234567890', '987654321'):
            add('asset.suspicious_id', 'FAIL', f'asset id {aid} looks fabricated (too short or too few distinct digits)', pos)
    if ids and not manifest_like:
        add('asset.id_outside_manifest', 'WARN', 'asset ids should live in an AssetManifest module, not inline in UI code', ids[0][1])

    # --- safe area / size
    if re.search(r'IgnoreGuiInset\s*=\s*true', src) and not re.search(r'ScreenInsets', src):
        m = re.search(r'IgnoreGuiInset\s*=\s*true', src)
        add('ui.topbar_overlap_risk', 'WARN', 'IgnoreGuiInset = true lets interactive UI sit under the Roblox top bar; use ScreenInsets = TopbarSafeInsets (verify in docs) unless this is a full-screen overlay', m.start())
    has_constraint = bool(re.search(r'UISizeConstraint|UIScale|UIAspectRatioConstraint', src))
    for m in re.finditer(r'Size\s*=\s*UDim2\.(?:fromScale\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)|new\(\s*([\d.]+)\s*,\s*0\s*,\s*([\d.]+)\s*,\s*0\s*\))', src):
        a = float(m.group(1) or m.group(3)); b = float(m.group(2) or m.group(4))
        if a >= 0.8 and b >= 0.8 and 'Frame' in src and not re.search(r'BackgroundTransparency\s*=\s*1', src[m.end():m.end() + 160] + src[max(0, m.start() - 160):m.start()]):
            add('ui.large_panel', 'WARN', f'panel covers {int(a * 100)}% x {int(b * 100)}% of the viewport at default size; compact default is at most 80% and about 62% width on desktop', m.start())
    if re.search(r"Instance\.new\(\s*'Frame'|Instance\.new\(\s*\"Frame\"", code) and not has_constraint:
        add('ui.no_size_constraint', 'WARN', 'no UISizeConstraint/UIScale: panel size will not adapt across phone/tablet/desktop')
    for m in re.finditer(r'TextSize\s*=\s*(\d+)', src):
        if int(m.group(1)) < 12:
            add('ui.small_text', 'WARN', f'TextSize {m.group(1)} is below the 12 minimum', m.start())

    # --- loading state
    lm = re.search(r"Text\s*=\s*['\"]Loading", src)
    if lm and not re.search(r'[Ll]oading\w*\.Visible\s*=\s*false|[Ll]oading\w*:Destroy\(\)|[Ll]oading\w*\.Enabled\s*=\s*false', src):
        add('ui.loading_never_hidden', 'WARN', 'a "Loading" element is created but never hidden or destroyed: it can stay on top of the content', lm.start())

    # --- lifecycle
    im = re.search(r'\b\w+:(Init|Start)\(', src)
    if im and not re.search(r'\.(Init|Start)\s+then|typeof\([^)]*\.(Init|Start)\)|type\([^)]*\.(Init|Start)\)|\.(Init|Start)\s*(==|~=)', src):
        add('lifecycle.unguarded_init', 'WARN', f"calling :{im.group(1)}() without checking the method exists causes \"attempt to call missing method '{im.group(1)}' of table\" for modules that do not define it", im.start())
    return out

def main():
    paths = sys.argv[1:]
    if not paths:
        print(__doc__); return 2
    bad = 0
    for p in paths:
        res = lint(open(p, encoding='utf-8', errors='replace').read(), p)
        for f in res:
            print(f"{p}:{f['line']}: {f['severity']} {f['rule']}: {f['message']}")
            bad += f['severity'] == 'FAIL'
        if not res: print(f'{p}: no UI lint findings (this is not a layout or runtime test)')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
