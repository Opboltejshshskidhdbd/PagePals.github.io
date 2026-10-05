#!/usr/bin/env python3
"""Validate dataset entries. kind=code -> whole output; kind=debug_fix -> only the fixed code; kind=qa -> skipped.
Always runs rule lint. Runs luau-analyze only if installed (otherwise ANALYZER=TOOL_MISSING, never PASS).
Usage: python scripts/validate_dataset.py <shards_dir> [--analyzer "luau-lsp analyze"] [--types globalTypes.d.luau]"""
import json, os, re, shlex, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint_rules import lint
from luau_parser import check as syntax_check

def extract_code(row, kind):
    out = row['output']
    if kind == 'debug_fix':
        m = list(re.finditer(r'(?m)^(?:Fixed|Secure|Optimized)[^\n]*\n\n', out))
        return out[m[-1].end():] if m else out
    return out

def split_scripts(code):
    """Entries that hold several scripts (-- SERVER / -- CLIENT ...) are split so each is analyzed alone."""
    pieces = re.split(r'^--\s*(?:SERVER|CLIENT|MANAGER|WORKER)[^\n]*-*\s*$', code, flags=re.M)
    return [p for p in pieces if p.strip()] or [code]

def run_analyzer(binary, types, code):
    with tempfile.NamedTemporaryFile('w', suffix='.luau', delete=False, encoding='utf-8') as f:
        f.write(code); path = f.name
    cmd = shlex.split(binary)
    if types: cmd += ['--definitions=' + types]
    cmd += [path]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        out = (p.stdout + p.stderr).strip()
        errors = [l for l in out.split('\n') if 'TypeError' in l or 'SyntaxError' in l]
        return ('PASS' if p.returncode == 0 and not errors else 'FAIL'), errors[:5]
    except Exception as e:
        return 'ERROR', [str(e)]
    finally:
        os.unlink(path)

def main():
    shards_dir = sys.argv[1]
    analyzer = None; types = None
    if '--analyzer' in sys.argv: analyzer = sys.argv[sys.argv.index('--analyzer') + 1]
    if '--types' in sys.argv: types = sys.argv[sys.argv.index('--types') + 1]
    have_analyzer = bool(analyzer and shutil.which(shlex.split(analyzer)[0]))
    manifest = json.load(open(os.path.join(shards_dir, 'manifest.json'), encoding='utf-8'))
    shard_cache = {}
    report = {'analyzer': 'RAN' if have_analyzer else 'TOOL_MISSING', 'entries': [], 'summary': {}}
    counts = {'lint_pass': 0, 'lint_fail': 0, 'lint_warn_only': 0, 'skipped_qa': 0, 'analyzer_pass': 0, 'analyzer_fail': 0}
    for m in manifest['entries']:
        if m['kind'] == 'qa':
            counts['skipped_qa'] += 1
            report['entries'].append({'id': m['id'], 'status': 'SKIPPED_QA'}); continue
        shard = shard_cache.setdefault(m['shard'], json.load(open(os.path.join(shards_dir, m['shard']), encoding='utf-8')))
        row = next(r for r in shard if r['id'] == m['id'])
        code = extract_code(row, m['kind'])
        findings = []
        for piece in split_scripts(code):
            syn = syntax_check(piece)
            if not syn['ok']:
                findings.append({'rule': 'syntax.error', 'severity': 'FAIL', 'line': syn['line'], 'message': syn['error'], 'text': syn['hint'] or ''})
            findings += lint(piece)
        fails = [f for f in findings if f['severity'] == 'FAIL']
        warns = [f for f in findings if f['severity'] == 'WARN']
        status = 'LINT_FAIL' if fails else ('LINT_WARN' if warns else 'LINT_PASS')
        entry = {'id': m['id'], 'kind': m['kind'], 'domain': m['domain'], 'status': status, 'findings': findings}
        if have_analyzer and m['standalone_runnable']:
            results = [run_analyzer(analyzer, types, p) for p in split_scripts(code)]
            entry['analyzer'] = 'PASS' if all(r[0] == 'PASS' for r in results) else 'FAIL'
            entry['analyzer_errors'] = [e for r in results for e in r[1]]
            counts['analyzer_pass' if entry['analyzer'] == 'PASS' else 'analyzer_fail'] += 1
        else:
            entry['analyzer'] = 'TOOL_MISSING' if not have_analyzer else 'SKIPPED_NOT_STANDALONE'
        counts['lint_fail' if fails else ('lint_warn_only' if warns else 'lint_pass')] += 1
        report['entries'].append(entry)
    report['summary'] = counts
    json.dump(report, open('dataset_report.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps({'analyzer': report['analyzer'], **counts}, indent=1))
    return 1 if counts['lint_fail'] or counts['analyzer_fail'] else 0

if __name__ == '__main__':
    sys.exit(main())
