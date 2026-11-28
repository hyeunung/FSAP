"""DP-4 저장 전 검사(세션 41082). 작업 폴더 tools/out/detail/DP-4/m0 에서:
python -X utf8 -B ../../../../gen_detail_dp4/chk.py
재질(TUBE_BRKT_U6 -> PET-CF) · 바뀐 바디 측정 · 전개 · 자세별 틈 · C-46 한계 · 떠 있는 부품 · 타임라인."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q, nb
from q import C

T2 = 'P_RXDC03_T2_GUIDE_판금'; CL = 'P_RXDC03_BEAM_CLAMP_판금'; U6 = 'P_M08_TUBE_BRKT_U6'
B1 = 'CB5-12_RXDC03_CLAMP_1'; B2 = 'CB5-12_RXDC03_CLAMP_2'
RS = 'P_RXDC03_RISER_BRKT_판금'; LG = 'P_RXDC03_LEAD_GUIDE_판금'
OUT = {}

# 1 재질
u = q.ex('mat_u6', 'material.assign', bodies=[U6], material='PET-CF')
print('material', json.dumps(u, ensure_ascii=False)[:200])
meas = {}
for n in (T2, CL, U6, B1, B2):
    m = q.tool('mf_%s' % n[-6:], 'measure', body=n)['data']
    b = m['bodies'][0]
    meas[n] = {k: b.get(k) for k in ('volume_mm3', 'mass_g', 'material', 'bbox', 'faces', 'closed', 'center_of_mass')}
    print(n, round(b['volume_mm3'], 3), b.get('mass_g'), b.get('material'), [round(x, 3) for x in b['bbox']['min'] + b['bbox']['max']])
OUT['measure'] = meas

# 2 전개
fl = {}
for n in (T2, CL):
    d = q.ex('fp_%s' % n[-6:], 'sheet.flat_pattern', body=n)['data']
    mb = q.ex('mb_%s' % n[-6:], 'sheet.measure_body', body=n)['data']
    fl[n] = dict(flat_size=d.get('flat_size_mm'), rule=d.get('rule'), thickness=d.get('thickness'), bends=d.get('bends'),
                 holes=[c.get('circle') for c in d.get('cutout_shapes', [])], measure_body=mb if isinstance(mb, dict) else str(mb)[:300])
    print(n, 'flat', d.get('flat_size_mm'), 'bends', len(d.get('bends', [])), 'holes', len(d.get('cutout_shapes', [])), 'mb', json.dumps(mb, ensure_ascii=False)[:200])
OUT['flat'] = fl

# 3 자세별 틈
S = [T2, CL, B1, B2]
boxes = [[-310.6 - 95, -280.0, 66.0, 84.0, 212.0, 236.0]]
AG = sorted(set(nb.neighbors(S, 6, boxes)) - set(S))
print('against', len(AG))
def clr(tag, bodies, against, c=1.0):
    d = q.ex('c_' + tag, 'inspect.clearance', bodies=bodies, against=against, clearance=c)['data']
    if not isinstance(d, dict):
        print(tag, 'ERR', str(d)[:300]); return None
    ok = d['pairs_checked'] + d['pairs_pruned'] > 0
    ov = [(p['a'], p['b'], round(p.get('volume_mm3', 0), 3)) for p in d.get('overlaps', [])]
    nr = sorted([(round(p['distance_mm'], 3), p['a'], p['b']) for p in d.get('near', []) if p['distance_mm'] > 1e-6])
    print(tag, 'measured', ok, 'trunc', d['truncated'], 'unchecked', len(d['unchecked']), 'overlaps', ov, 'near>0', nr[:6])
    return dict(measured=ok, truncated=d['truncated'], unchecked=d['unchecked'], overlaps=ov, near=nr, touching=[(p['a'], p['b']) for p in d.get('near', []) if p['distance_mm'] <= 1e-6])
P = {}
P['REST'] = clr('rest', S, AG)
for v in (0, 23.75, 47.5, 71.25, 95):
    r = q.ex('drv', 'joint.drive', joint='J_U4_X', value=v, quiet=True)
    P['J_U4_X_%s' % v] = clr('u4x_%s' % str(v).replace('.', 'p'), S, AG)
q.ex('drv', 'joint.drive', joint='J_U4_X', value=0, quiet=True)
for v in (-8.171, 5.676, 19.523):
    r = q.ex('drv', 'joint.drive', joint='J_U4_PRESS', value=v, quiet=True)
    P['J_U4_PRESS_%s' % v] = clr('press_%s' % str(v).replace('.', 'p').replace('-', 'm'), S, AG)
q.ex('drv', 'joint.drive', joint='J_U4_PRESS', value=19.523, quiet=True)
# C-46 한계: J_U4_X 95, J_U5_X 1365 에서 U5 바퀴 틈
q.ex('drv', 'joint.drive', joint='J_U4_X', value=95, quiet=True)
q.ex('drv', 'joint.drive', joint='J_U5_X', value=1365, quiet=True)
W = ['P_M03_WHEEL', 'P_M03_WHEEL_TREAD', 'CB5-12_M03_HUB']
L = [T2, RS, LG, 'STEP대기_HG-KR23_LEAD_LOOP', 'STEP대기_HG-KR23_LEAD_ENC', 'STEP대기_HG-KR23_LEAD_PWR', 'STEP대기_HG-KR23_CONN_ENC', 'STEP대기_HG-KR23_CONN_PWR']
P['C46_95_1365'] = clr('c46', L, W, 15.0)
q.ex('drv', 'joint.drive', joint='J_U5_X', value=0, quiet=True)
q.ex('drv', 'joint.drive', joint='J_U4_X', value=0, quiet=True)
r = q.ex('rest', 'motion.play', study='REST', step=0)
print('rest', json.dumps(r, ensure_ascii=False)[:200])
OUT['poses'] = P

# 4 조인트 · 타임라인
j = q.ex('jl2', 'joint.list')['data']
OUT['joints'] = dict(floating=j['floating'], conflicts=j['conflicts'], errors=j['errors'], n=len(j['joints']))
print('joints', OUT['joints'])
i = q.tool('insp_chk', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
fe = i['timeline']['features'] if isinstance(i['timeline'], dict) else i['timeline']
OUT['timeline'] = dict(features=len(fe), errors=sum(1 for f in fe if f.get('error')), warnings=sum(1 for f in fe if f.get('warning')), suppressed=[f['name'] for f in fe if f.get('suppressed')], bodies=len(i.get('bodies', [])), dirty=i.get('dirty'), name=i.get('name'))
print('timeline', OUT['timeline'])
json.dump(OUT, open('chk.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
