#!/usr/bin/env python3
"""Usage: python search_dataset.py keyword [keyword ...] [--kind code|qa|debug_fix] [--max 5]
Returns at most N matching entries (never loads the whole dataset into context)."""
import json, sys, os
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
kind = None; mx = 5
if '--kind' in args: i = args.index('--kind'); kind = args[i+1]; del args[i:i+2]
if '--max' in args: i = args.index('--max'); mx = int(args[i+1]); del args[i:i+2]
words = [a.lower() for a in args]
man = json.load(open(os.path.join(here, 'manifest.json'), encoding='utf-8'))
hits = []
for m in man['entries']:
    if kind and m['kind'] != kind: continue
    score = sum(w in (m['instruction'] + ' ' + m['domain']).lower() for w in words)
    if score: hits.append((score, m))
hits.sort(key=lambda t: -t[0])
cache = {}
for _, m in hits[:mx]:
    shard = cache.setdefault(m['shard'], json.load(open(os.path.join(here, m['shard']), encoding='utf-8')))
    row = next(r for r in shard if r['id'] == m['id'])
    print('=' * 70); print(m['id'], m['domain'], m['kind'], m['context'], 'standalone' if m['standalone_runnable'] else 'NOT-standalone:' + ','.join(m['not_standalone_reasons']))
    print('Q:', row['instruction']); print(row['output'])
