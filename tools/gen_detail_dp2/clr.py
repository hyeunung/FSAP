"""바뀐 바디 × 주변(bbox 2 mm) 틈·겹침. usage: clr.py <measure r_*.json> <sigdiff json> <tag> [chunk]"""
import json, sys, q, time
m = q.unwrap(sys.argv[1])['data']; sd = json.load(open(sys.argv[2], encoding='utf-8')); tag = sys.argv[3]; CH = int(sys.argv[4]) if len(sys.argv) > 4 else 40
B = {b['name']: b['bbox'] for b in m['bodies']}
chg = list(sd['added'].keys())
for k, v in sd['changed'].items():
    t = k.split('/', 1)[1]; chg.append(t if t in B else v['new']['name'])
assert all(c in B for c in chg)
def touch(a, b, g=2.0):
    return all(a['min'][i] - g <= b['max'][i] and b['min'][i] - g <= a['max'][i] for i in range(3))
cs = set(chg)
nb = {c: [n for n, bb in B.items() if n != c and touch(B[c], bb)] for c in chg}
json.dump(nb, open(tag + '_neighbors.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('changed', len(chg), 'neighbor pairs', sum(len(v) for v in nb.values()), 'distinct neighbors', len(set(n for v in nb.values() for n in v) - cs))
res = dict(overlaps=[], near=[], unchecked=[], pairs_checked=0, pairs_pruned=0, calls=[])
for i in range(0, len(chg), CH):
    part = chg[i:i + CH]
    ag = sorted(set(n for c in part for n in nb[c]) - set(part))
    t = time.time()
    u = q.call('%s_c%d' % (tag, i // CH), {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': part, 'against': ag, 'clearance': 1.0}}}, timeout=900)
    d = u['data']
    if isinstance(d, str): print('ERR', d[:500]); break
    for k in ('overlaps', 'near', 'unchecked'): res[k] += d.get(k, [])
    res['pairs_checked'] += d.get('pairs_checked', 0); res['pairs_pruned'] += d.get('pairs_pruned', 0)
    res['calls'].append(dict(i=i, bodies=len(part), against=len(ag), s=round(time.time() - t, 1), checked=d.get('pairs_checked'), pruned=d.get('pairs_pruned'), overlaps=len(d.get('overlaps', [])), near=len(d.get('near', []))))
    print(res['calls'][-1], flush=True)
    # 바뀐 것끼리(묶음 안)도 본다
    if len(part) > 1:
        pass
json.dump(res, open(tag + '_clearance.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('overlaps', len(res['overlaps']), 'near<1.0', len(res['near']), 'unchecked', len(res['unchecked']), 'checked', res['pairs_checked'], 'pruned', res['pairs_pruned'])
