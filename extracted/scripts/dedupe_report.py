#!/usr/bin/env python3
"""Near-duplicate report for the dataset (token shingles after normalizing numbers/strings/colors).
Usage: python scripts/dedupe_report.py <shards_dir> [--threshold 0.85]
Writes dedupe_report.json. Report only: it never deletes entries."""
import json, os, re, sys
from collections import defaultdict

def normalize(code):
    code = re.sub(r'--\[\[.*?\]\]', ' ', code, flags=re.S)
    code = re.sub(r'--[^\n]*', ' ', code)
    code = re.sub(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"", ' STR ', code)
    code = re.sub(r'\b\d+(?:\.\d+)?\b', ' NUM ', code)
    toks = re.findall(r'[A-Za-z_][A-Za-z_0-9]*|[^\sA-Za-z_0-9]', code)
    out = []
    for t in toks:
        if re.fullmatch(r'(Fire|Ice|Lightning|Poison|Holy|Shadow|Wind|Earth|Water|Blood|Void|Plasma|Nature|Cosmic)\w*', t, re.I):
            t = 'ELEM'
        out.append(t.lower())
    return out

def shingles(tokens, n=6):
    return {' '.join(tokens[i:i + n]) for i in range(max(len(tokens) - n + 1, 1))}

def main():
    d = sys.argv[1]
    thr = float(sys.argv[sys.argv.index('--threshold') + 1]) if '--threshold' in sys.argv else 0.85
    man = json.load(open(os.path.join(d, 'manifest.json'), encoding='utf-8'))
    rows, cache = {}, {}
    for m in man['entries']:
        if m['kind'] == 'qa':
            continue
        shard = cache.setdefault(m['shard'], json.load(open(os.path.join(d, m['shard']), encoding='utf-8')))
        row = next(r for r in shard if r['id'] == m['id'])
        rows[m['id']] = (m, shingles(normalize(row['output'])))
    ids = list(rows)
    parent = {i: i for i in ids}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    pairs = 0
    for a in range(len(ids)):
        sa = rows[ids[a]][1]
        for b in range(a + 1, len(ids)):
            sb = rows[ids[b]][1]
            if not sa or not sb:
                continue
            inter = len(sa & sb)
            if inter / (len(sa) + len(sb) - inter) >= thr:
                pairs += 1
                parent[find(ids[a])] = find(ids[b])
    clusters = defaultdict(list)
    for i in ids:
        clusters[find(i)].append(i)
    big = [c for c in clusters.values() if len(c) > 1]
    in_clusters = sum(len(c) for c in big)
    unique = len(ids) - in_clusters + len(big)   # one representative per cluster
    report = {'threshold': thr, 'code_entries': len(ids), 'near_duplicate_pairs': pairs, 'clusters': len(big),
              'entries_in_clusters': in_clusters, 'effective_unique_entries': unique,
              'largest_clusters': sorted(({'size': len(c), 'example': rows[c[0]][0]['instruction'], 'ids': c[:6]} for c in big), key=lambda x: -x['size'])[:12]}
    json.dump(report, open('dedupe_report.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'largest_clusters'}, indent=1))
    for c in report['largest_clusters']:
        print(f"  cluster x{c['size']:3d}: {c['example'][:85]}")

if __name__ == '__main__':
    main()
