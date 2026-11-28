"""DP-3 저장 전 검사 2: (1) 새 탭에 물린 그대로인 볼트 8개(REG 6 · 클램프 L_6 2)의 물림 (2) 관 빗 ±5° 돌림에서 턱이 보에 걸리는지(옮겨 보고 되돌림).
usage(작업 폴더에서): chk2.py"""
import json, sys, math, re, q


def C(command, **params):
    return {'command': command, 'params': params}


def ex(tag, command, params, timeout=470):
    u = q.call(tag, {'tool': 'execute', 'arguments': {'command': command, 'params': params}}, timeout=timeout)
    if u.get('isError') or isinstance(u['data'], str):
        print('FAIL', tag, str(u['data'])[:1200])
        sys.exit(2)
    return u['data']


M = {b['name']: b for b in q.unwrap('r_measall2.json')['data']['bodies']}
HEAD = lambda n: re.sub(r' \(.*', '', n)
out = {}
# (1) 그대로인 볼트 × 새 탭
reg = [n for n in M if HEAD(n) == 'CB4-12_M08_REG']
l6 = [n for n in M if HEAD(n) == 'CB5-16_M08_PY' and abs(M[n]['bbox']['min'][2] - 271.75) < 0.01 and M[n]['bbox']['min'][0] < -340]
lamp = [n for n in M if HEAD(n) == 'CB4-20_M08_LAMP']
d = ex('chk_tap', 'inspect.clearance', {'bodies': reg + l6 + lamp, 'against': ['P_M07_BEAM'], 'clearance': 0.5})
rows = []
for p in d['overlaps']:
    b = p['b'] if p['a'] == 'P_M07_BEAM' else p['a']
    ring = math.pi * (2.0 ** 2 - 1.65 ** 2) if 'CB4' in b else math.pi * (2.5 ** 2 - 2.1 ** 2)
    rows.append((b, round(p['volume_mm3'], 3), round(p['volume_mm3'] / ring, 2)))
    print('tap', b, round(p['volume_mm3'], 3), 'engage', round(p['volume_mm3'] / ring, 2))
out['tap_engage'] = rows
print('reg', len(reg), 'l6', len(l6), 'lamp', len(lamp), 'overlaps', len(d['overlaps']))
# (2) 턱 걸림: 볼트 축(X 가운데, Y 166) 둘레 ±5°
Cs = q.call('cl_chk', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']
BYN = {c['name']: c for c in Cs}
TEST = {'P_M08_TUBE_COMB_ML_5': 950, 'P_M08_TUBE_COMB_ML_7': 50, 'P_M08_TUBE_COMB_ML_8': -650, 'P_M08_TUBE_COMB_U5_2': -1245}
IDM = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
lip = {}
for n, xc in TEST.items():
    occ = BYN[n]['occurrences'][0]['id']
    res = {}
    for ang in (0, 5, -5):
        a = math.radians(ang)
        c, s = math.cos(a), math.sin(a)
        px = xc - (c * xc - s * 166)
        py = 166 - (s * xc + c * 166)
        mtx = [c, -s, 0, px, s, c, 0, py, 0, 0, 1, 0] if ang else IDM
        q.call('lip_mv', {'commands': [C('occurrence.move', occurrence=occ, space='local', to_matrix=mtx)], 'rollback': True, 'verbose': False})
        dd = ex('lip_if', 'inspect.interference', {'bodies': [n, 'P_M07_BEAM']})
        prs = dd.get('pairs') or dd.get('interferences') or dd.get('overlaps') or []
        vol = sum(p.get('volume_mm3', p.get('volume', 0)) for p in prs)
        box = prs[0].get('bbox') if prs else None
        res[ang] = dict(volume_mm3=round(vol, 4), bbox=box)
        print(n, ang, 'deg  comb x beam overlap', round(vol, 4), box and [round(v, 2) for v in box['min'] + box['max']])
    q.call('lip_mv', {'commands': [C('occurrence.move', occurrence=occ, space='local', to_matrix=IDM)], 'rollback': True, 'verbose': False})
    b = q.call('lip_m', {'tool': 'measure', 'arguments': {'body': n}})['data']['bodies'][0]
    back = [round(v, 3) for v in b['bbox']['min'] + b['bbox']['max']]
    ref = [round(v, 3) for v in M[n]['bbox']['min'] + M[n]['bbox']['max']]
    res['restored'] = back == ref
    print('   restored', back == ref, back)
    lip[n] = res
out['lip'] = lip
json.dump(out, open('chk2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
