"""수정 1회차 저장 전 검사: 새 볼트 × 주변 틈·겹침(REST), 탭 원통, 플랩 5점, 조인트. usage: python -X utf8 -B chk.py"""
import json, q, re
PRJ = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools'
S = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8'))['parts']
C = q.call('complist2', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']
c14 = [c for c in C if c['name'] == 'STEP대기_CB5-14_DP2'][0]; c16 = [c for c in C if c['name'] == 'CB5-16_DP2'][0]
print('CB5-14_DP2 occ', len(c14['occurrences']), [o['name'] for o in c14['occurrences']], '| CB5-16_DP2 occ', len(c16['occurrences']), ':15 left', [o['name'] for o in c16['occurrences'] if o['name'].endswith(':15')])
flap = [c for c in C if c['name'] == 'U2_FLAP'][0]; own = set(flap['bodies'])
inflap = lambda n: ('U2_FLAP:1/' in n) or (n in own)
NEW = 'STEP대기_CB5-14_DP2 (U2_TABLE:1/U2_FLAP:1/STEP대기_CB5-14_DP2:7)'
OLDKEY = 'U2_TABLE/CB5-16_DP2 (U2_TABLE:1/U2_FLAP:1/CB5-16_DP2:15)'
ob = S[OLDKEY]['bbox']
def near(bb, box, g): return all(bb[2*i] - g <= box[2*i+1] and box[2*i] - g <= bb[2*i+1] for i in range(3))
nb = [v['name'] for k, v in S.items() if k != OLDKEY and near(v['bbox'], ob, 2.0)]
print('neighbors(2 mm)', len(nb), nb)
out = {}
u = q.call('clr_rest', {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': [NEW], 'against': nb, 'clearance': 5.0}}}, timeout=460)
d = u['data']; assert not isinstance(d, str), d
out['rest'] = d
print('REST checked', d['pairs_checked'], 'pruned', d['pairs_pruned'], 'unchecked', len(d.get('unchecked', [])))
for o in d['overlaps']: print('  overlap', o['a'], '|', o['b'], round(o['volume_mm3'], 3))
for o in d.get('near', []): print('  near', json.dumps(o, ensure_ascii=False)[:260])
for body in ('P_RX12C1_FLAP_BAR_XP', NEW, 'P_RX12C1_FLAP_PL'):
    u = q.call('topo', {'tool': 'body_topology', 'arguments': {'body': body, 'faces': 'cylinders'}})
    cy = u['data']['cylinders']
    sel = [c for c in cy if abs(c['origin'][0] - 1092.5) < 13 and abs(c['origin'][1] + 330) < 8] if body != NEW else cy
    out['topo_' + body] = sel
    print(body, 'cyl', len(cy), '->', [(round(c['radius'], 3), [round(x, 3) for x in c['origin']], [round(x, 3) for x in c['axis']], [round(x, 3) for x in c['extent']]) for c in sel])
# 플랩 5점
box = [1040, 1165, -345, -315, -110, 10]
ag = [v['name'] for k, v in S.items() if k != OLDKEY and near(v['bbox'], box, 0.0) and not inflap(v['name'])]
print('flap against(non-flap in sweep box)', len(ag))
base = set(' | '.join(sorted((o['a'], o['b']))) for o in d['overlaps'])
out['flap'] = {}
for ang in (-22.5, -45.0, -67.5, -90.0):
    u = q.call('drive', {'tool': 'execute', 'arguments': {'command': 'joint.drive', 'params': {'joint': 'J_U2_FLAP', 'value': ang}}})
    if u.get('isError') or isinstance(u['data'], str): print('drive err', str(u['data'])[:300]); break
    u = q.call('clr_flap', {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': [NEW], 'against': ag + [n for n in nb if inflap(n)], 'clearance': 0.5}}}, timeout=460)
    e = u['data']; assert not isinstance(e, str), e
    newov = [(o['a'], o['b'], round(o['volume_mm3'], 3)) for o in e['overlaps'] if ' | '.join(sorted((o['a'], o['b']))) not in base]
    samev = [(re.sub(r' \(.*', '', o['b'] if o['a'] == NEW else o['a']), round(o['volume_mm3'], 3)) for o in e['overlaps']]
    out['flap'][ang] = dict(checked=e['pairs_checked'], pruned=e['pairs_pruned'], overlaps=samev, new=newov, near=[(x.get('a'), x.get('b'), x.get('distance_mm', x.get('distance'))) for x in e.get('near', [])], unchecked=len(e.get('unchecked', [])))
    print(ang, json.dumps(out['flap'][ang], ensure_ascii=False)[:500])
u = q.call('rest2', {'tool': 'execute', 'arguments': {'command': 'motion.play', 'params': {'study': 'REST', 'step': 0}}})
print('REST moved', u['data'].get('moved'), 'conflicts', u['data'].get('conflicts'))
u = q.call('props_rest', {'tool': 'execute', 'arguments': {'command': 'occurrence.properties', 'params': {'occurrence': 101168}}})
print('new bolt at REST bbox', u['data']['total']['bbox'])
out['rest_bbox_after'] = u['data']['total']['bbox']
j = q.call('jlist2', {'tool': 'execute', 'arguments': {'command': 'joint.list', 'params': {}}})['data']
out['joints'] = {k: len(v) for k, v in j.items() if isinstance(v, list)}
print('joints', out['joints'])
json.dump(out, open('pre_check.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
