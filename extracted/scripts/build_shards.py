#!/usr/bin/env python3
"""Build domain shards (<=55 KB each) + manifest.json from a flat Alpaca dataset.
Usage: python scripts/build_shards.py dataset.json out_dir"""
import json, os, re, sys

DOMAINS = [
 ('networking', r'RemoteEvent|OnServerEvent|FireServer|FireClient|MessagingService|lag compens|reconcil|snapshot|buffer\.|rate limit|exploit|sanity'),
 ('datastore',  r'DataStore|ProcessReceipt|MemoryStore|TeleportService|OrderedDataStore|HttpService|session lock'),
 ('ai',         r'Pathfinding|A\*|boids|behavior tree|utility AI|steering|NPC|turret|patrol'),
 ('combat',     r'combo|parry|block|poise|stagger|hitbox|hitscan|ability module|weapon|dodge|knockback|ragdoll|status effect|TakeDamage'),
 ('ui',         r'ScreenGui|TextLabel|health bar|toast|typewriter|radar|ViewportFrame|dialogue|UIGradient|cooldown button|vignette|Frame'),
 ('camera',     r'camera|FOV|viewmodel|recoil|spectator|cinematic'),
 ('physics',    r'LinearVelocity|AlignPosition|constraint|Verlet|hover vehicle|raycast suspension|grapple|IKControl|AssemblyLinearVelocity|destructible'),
 ('easing',     r'easing function|ease(In|Out)'),
 ('vfx',        r'ParticleEmitter|Trail|Beam|shockwave|aura|explosion|lightning|dissolve|afterimage|Highlight|PointLight|VFX|effect'),
 ('architecture', r'Signal|Janitor|Promise|ECS|Store|Spring|FSM|EventBus|bootstrap|CollectionService|Pool|heap|spatial hash|Luau|task\.|metatable'),
]
def kind_of(r):
    if r['input']: return 'debug_fix'
    return 'code' if re.search(r'(?m)^\s*(local |function |return\b|for |if |while |repeat\b|--|end\b)', r['output']) else 'qa'
def context_of(s):
    srv = bool(re.search(r'ServerScriptService|OnServerEvent|DataStoreService|ProcessReceipt|-- SERVER|-- MANAGER|PlayerRemoving|BindToClose', s))
    cli = bool(re.search(r'LocalPlayer|UserInputService|RenderStepped|PreRender|BindToRenderStep|-- CLIENT|ScreenGui|CurrentCamera|OnClientEvent|ContextActionService', s))
    return 'multi_script' if srv and cli else 'client' if cli else 'server' if srv else 'shared_or_either'
def standalone(s):
    why = []
    if re.search(r'require\((script\.Parent|game\.ReplicatedStorage|game:GetService)', s): why.append('requires_sibling_module')
    if re.search(r'WaitForChild\(', s) and 'ReplicatedStorage' in s: why.append('needs_remotes_in_hierarchy')
    if re.search(r'YOUR_[A-Z_]+|REPLACE_WITH_[A-Z_]+|rbxassetid://0', s): why.append('asset_placeholder')
    if re.search(r'-- (SERVER|CLIENT|MANAGER|WORKER)', s): why.append('multiple_scripts_in_one_entry')
    return not why, why
def domain_of(r):
    for name, rx in DOMAINS:
        if re.search(rx, r['instruction'], re.I): return name
    for name, rx in DOMAINS:
        if re.search(rx, r['output'][:600], re.I): return name
    return 'misc'

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
data = json.load(open(src, encoding='utf-8'))
manifest, by_dom = [], {}
for i, r in enumerate(data):
    k = kind_of(r)
    ok, why = standalone(r['output']) if k != 'qa' else (False, ['not_code'])
    row = dict(r); row['id'] = f'rb-{i:04d}'
    manifest.append({'id': row['id'], 'index': i, 'domain': domain_of(r), 'kind': k,
                     'context': context_of(r['output']) if k != 'qa' else 'n/a',
                     'standalone_runnable': ok, 'not_standalone_reasons': why, 'instruction': r['instruction'][:110]})
    by_dom.setdefault(manifest[-1]['domain'], []).append(row)
files, LIMIT = [], 55_000
idx = {m['id']: m for m in manifest}
for dom, rows in sorted(by_dom.items()):
    chunk, size, n = [], 0, 1
    def flush():
        global chunk, size, n
        if not chunk: return
        fn = f'{dom}_{n:02d}.json'
        json.dump(chunk, open(os.path.join(out, fn), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        files.append({'file': fn, 'entries': len(chunk), 'bytes': os.path.getsize(os.path.join(out, fn))})
        for row in chunk: idx[row['id']]['shard'] = fn
        chunk, size, n = [], 0, n + 1
    for row in rows:
        s = len(json.dumps(row, ensure_ascii=False))
        if chunk and size + s > LIMIT: flush()
        chunk.append(row); size += s
    flush()
json.dump({'total': len(manifest), 'shards': files, 'entries': manifest}, open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('shards:', len(files), '| entries:', len(manifest), '| max shard bytes:', max(f['bytes'] for f in files))
