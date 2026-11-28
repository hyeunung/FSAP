"""세션(또는 저장본 측정 결과)의 전수 측정 ↔ signatures.json: 바뀐·새·없어진 바디. usage: sigdiff.py <measure result r_*.json | eval json> <out prefix>"""
import json, sys, q, re
src = sys.argv[1]; pre = sys.argv[2]
try:
    m = q.unwrap(src)['data']
except Exception:
    m = json.load(open(src, encoding='utf-8'))
    if 'results' in m: m = m['results'][-1]
S = json.load(open('../../../signatures.json', encoding='utf-8')); P = S['parts']
r3 = lambda x: round(x, 3)
M = {}
for b in m['bodies']:
    assert b['name'] not in M, b['name']
    M[b['name']] = b
def tail(k, v):
    t = k.split('/', 1)[1] if '/' in k else k
    if t in M: return t
    i = k.find(v['name'])
    return k[i:] if i >= 0 and k[i:] in M else None
used = {}; removed = []; changed = {}; same = 0
for k, v in P.items():
    n = tail(k, v)
    if n is None: removed.append(k); continue
    used[n] = k; b = M[n]
    bb = [r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])]
    w = dict(v); w['bbox'] = bb; w['volume'] = r3(b['volume_mm3']) if b.get('volume_mm3') is not None else v.get('volume'); w['mass'] = r3(b['mass_g']) if b.get('mass_g') is not None else v.get('mass'); w['material'] = b.get('material') or v.get('material')
    db = max(abs(a - c) for a, c in zip(v['bbox'], bb)); dv = abs((v.get('volume') or 0) - (w.get('volume') or 0))
    if db > 0.05 or dv > max(1e-4 * abs(v.get('volume') or 0), 0.01) or v.get('material') != w.get('material'):
        changed[k] = dict(old=v, new=w)
    else: same += 1
added = {n: M[n] for n in M if n not in used}
print('sig', len(P), 'measured', len(M), 'same', same, 'changed', len(changed), 'removed', len(removed), 'added', len(added))
json.dump(dict(changed=changed, removed=removed, added={n: dict(bbox=[r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])], volume=r3(b['volume_mm3']), mass=r3(b['mass_g']), material=b['material'], closed=b['closed']) for n, b in added.items()}), open(pre + '_sigdiff.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
import collections
print('changed:', [k for k in changed][:12])
print('removed heads:', collections.Counter(re.sub(r' \(.*', '', k) for k in removed))
print('added heads:', collections.Counter(re.sub(r' \(.*', '', n) for n in added))
print('added materials', collections.Counter(b['material'] for b in added.values()), 'open', [n for n, b in added.items() if not b['closed']])
