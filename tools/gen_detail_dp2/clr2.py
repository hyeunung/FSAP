import json, sys, q, re, collections
tag = sys.argv[1]
m = q.unwrap(sys.argv[2])['data']
B = {b['name']: b['bbox'] for b in m['bodies']}
sd = json.load(open(tag + '_sigdiff.json', encoding='utf-8')); nb = json.load(open(tag + '_neighbors.json', encoding='utf-8'))
r = json.load(open(tag + '_clearance.json', encoding='utf-8'))
parts = [c for c in nb if c not in sd['added']]
ag = sorted(set(n for c in parts for n in nb[c]) - set(parts))
u = q.call(tag + '_cparts', {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': parts, 'against': ag, 'clearance': 1.0}}}, timeout=900)
d = u['data']; print('parts call', len(parts), len(ag), d.get('pairs_checked'), d.get('pairs_pruned'), len(d['overlaps']), len(d['near']), u['s'])
u2 = q.call(tag + '_cparts2', {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': parts, 'clearance': 1.0}}}, timeout=900) if False else None
ov = {}; nr = {}
for o in r['overlaps'] + d['overlaps']: ov[frozenset((o['a'], o['b']))] = o
for o in r['near'] + d['near']: nr[frozenset((o['a'], o['b']))] = o
unchecked = r['unchecked'] + d.get('unchecked', [])
# 새 볼트: 머리 끝·축(옛 bbox ↔ 새 bbox)
old = {}
for L in sum([json.load(open('log_%s.json' % s, encoding='utf-8')) for s in ('A', 'A2', 'B', 'C', 'C2', 'D', 'E')], []):
    pass
new = set(sd['added'])
def axis_tip(n):
    bb = B[n]; ext = [bb['max'][i] - bb['min'][i] for i in range(3)]
    i = max(range(3), key=lambda k: ext[k]); return i, ext[i]
h = lambda n: re.sub(r' \(.*', '', n)
thread_heads = ('HNTT8-5', 'P_RX12C1_FLAP_BAR', 'P_RX12C1_GS_ARM_BLK', 'P_M06_G1_PIN', 'P_M06_TOP_PIN', 'PGX62-H-10')
rows_o = collections.defaultdict(list); bad = []
for k, o in ov.items():
    a, b = tuple(k)
    if b in new and a not in new: a, b = b, a
    if a in new and b in new: bad.append(('bolt-bolt', a, b, o['volume_mm3'])); continue
    kind = 'thread' if (a in new and h(b).startswith(thread_heads)) or (h(a).startswith(thread_heads) and h(b).startswith('CB')) else ('countersink' if 'SFB5-16' in a and o['volume_mm3'] < 0.2 else 'OTHER')
    rows_o[(kind, h(a), h(b))].append(o['volume_mm3'])
    if kind == 'OTHER': bad.append(('overlap', a, b, o['volume_mm3']))
print('overlap pairs (dedup)', len(ov))
for k, v in sorted(rows_o.items()): print(' ', k, len(v), round(min(v), 2), round(max(v), 2))
rows_n = collections.defaultdict(list)
for k, o in nr.items():
    a, b = tuple(k)
    if b in new and a not in new: a, b = b, a
    rows_n[(h(a), h(b))].append((o['distance_mm'], o.get('from'), o.get('to')))
print('near pairs (dedup)', len(nr))
tipnear = []
for k, v in sorted(rows_n.items()):
    dmin = min(x[0] for x in v)
    if 0.01 < dmin < 1.0: print(' ', k, len(v), round(dmin, 3), 'from', [round(c, 2) for c in v[0][1]] if v[0][1] else None, 'to', [round(c, 2) for c in v[0][2]] if v[0][2] else None)
print('bad', bad, 'unchecked', len(unchecked))
json.dump(dict(overlaps={' | '.join(sorted(k)): o['volume_mm3'] for k, o in ov.items()}, near={' | '.join(sorted(k)): [o['distance_mm'], o.get('from'), o.get('to')] for k, o in nr.items()}, bad=bad, unchecked=unchecked,
               pairs_checked=r['pairs_checked'] + d.get('pairs_checked', 0), pairs_pruned=r['pairs_pruned'] + d.get('pairs_pruned', 0)), open(tag + '_clr_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
