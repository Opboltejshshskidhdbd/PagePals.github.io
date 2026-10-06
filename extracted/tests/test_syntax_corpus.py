import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from luau_syntax import validate_source

def _corpus():
    for p in (os.path.join(ROOT, 'skills', 'roblox-luau-assistant', 'references', 'syntax-regression-corpus.json'),
              os.path.join(ROOT, 'references', 'syntax-regression-corpus.json')):
        if os.path.exists(p):
            return json.load(open(p, encoding='utf-8'))
    raise FileNotFoundError('syntax-regression-corpus.json')

def test_corpus_wrong_and_right():
    problems = []
    for c in _corpus()['cases']:
        w = validate_source(c['wrong']).to_dict(); r = validate_source(c['right']).to_dict()
        if c.get('expect_wrong', 'reject') == 'reject':
            if w['status'] != 'SYNTAX_FAILED': problems.append(f"{c['id']}: wrong snippet was accepted")
            elif c.get('expect_fragment') and c['expect_fragment'] not in w['diagnostics'][0]['message']:
                problems.append(f"{c['id']}: message {w['diagnostics'][0]['message']!r} lacks {c['expect_fragment']!r}")
        elif w['status'] != 'SYNTAX_VERIFIED':
            problems.append(f"{c['id']}: expected accept for wrong snippet")
        if r['status'] != 'SYNTAX_VERIFIED': problems.append(f"{c['id']}: right snippet rejected: {r['diagnostics'][:1]}")
    assert not problems, problems

def test_valid_only_snippets_are_accepted():
    bad = [n for n, s in _corpus()['valid_only'].items() if validate_source(s).to_dict()['status'] != 'SYNTAX_VERIFIED']
    assert not bad, bad
