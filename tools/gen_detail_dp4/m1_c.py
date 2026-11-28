import json, re, sys, fx
from fx import ex, tool, C
Cs = json.load(open('comps0.json', encoding='utf-8'))
BY = {c['id']: c for c in Cs}
for c in Cs:
    if c['id'] in (32, 97892, 97890, 1) or re.search(r'RXDC03_(RISER|GUIDE|T2|CLAMP)|RXDCC1_RISER|CB5-16', c['name']):
        if c['name'].startswith('CB5-16') and not re.search('M07_NY|M01_1$', c['name']): continue
        print(c['id'], c['name'], 'parent', c.get('parent'), 'bodies', c.get('bodies')[:3] if len(c.get('bodies', [])) < 6 else len(c['bodies']), 'occ', [(o['id'], o.get('name'), [[round(v, 4) for v in r] for r in (o.get('transform') or [])]) for o in c.get('occurrences', [])][:1])
r = fx.call('ti2', {'commands': [C('timeline.inspect', feature=n) for n in ('RXDC03_CONN_ENC', 'RXDC03_CONN_PWR', 'RXDC03_COIL')], 'rollback': False, 'verbose': True})
for x in r['data']['results']: print(json.dumps(x.get('definition', x), ensure_ascii=False)[:300])
m = fx.meas(['STEP대기_HG-KR23_CONN_ENC', 'STEP대기_HG-KR23_CONN_PWR', 'STEP대기_HG-KR23_LEAD_ENC', 'STEP대기_HG-KR23_LEAD_PWR', 'STEP대기_HG-KR23_LEAD_LOOP', 'P_RX19_SWING_밀링', 'P_RX08_STOP_BLOCK_밀링',
    'STEP대기_MR-PWS1CBL5M-A2-H', 'STEP대기_MR-J3ENCBL5M-A2-H', 'STEP대기_MR-J3ENCBL5M-A2-H_LOOP', 'STEP대기_MR-PWS1CBL5M-A2-H_LOOP', 'STEP대기_MR-J3ENCBL5M-A2-H_FIX', 'STEP대기_MR-PWS1CBL5M-A2-H_FIX', 'P_M07_BEAM', 'CB5-16_M07_NY'])
for k, v in m.items(): print(k, v if isinstance(v, str) else (v['bbox'], v['volume'], v['material']))
rays = []
for (x, y) in ((-288, 90), (-278, 90), (-265.25, 79), (-284, 75), (-286, 75), (-296, 75), (-280.5, 78.25)):
    rays.append({'origin': [x, y, 300], 'dir': [0, 0, -1]})
    rays.append({'origin': [x, y, 200], 'dir': [0, 0, 1]})
d = ex('pick_blk', 'view.pick', rays=rays, all=True)['data']
for ry, h in zip(rays, d.get('hits', d.get('results', d)) if isinstance(d, dict) else d):
    hs = h if isinstance(h, list) else (h.get('hits') if isinstance(h, dict) and 'hits' in h else [h])
    print(ry['origin'], ry['dir'][2], [(x.get('body'), round(x['point'][2], 3)) for x in hs if x][:8])
j = ex('jl0', 'joint.list', exclude_rigid_groups=True)['data']
print({k: (v if not isinstance(v, list) else len(v)) for k, v in j.items()})
for jt in j['joints']:
    if re.search('U4_X|U4_PRESS|U5_X', jt.get('name', '')): print(json.dumps(jt, ensure_ascii=False)[:400])
