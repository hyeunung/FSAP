"""DP-4 검도 수정 1회차(v2.31.3 읽기 세션 41085, 저장 안 함). usage: python -X utf8 -B v1_chk.py <단계...>
단계: doc flat topo pose xp c46 jl rest. 결과 tools/out/detail/DP-4/v1/v1.json"""
import sys, os, json, math
import fx, nb
fx.PORT = 41085
fx.WD = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/v1'
os.chdir(fx.WD)
from fx import ex, tool, C, clr, drive
T2 = 'P_RXDC03_T2_GUIDE_판금'; CL = 'P_RXDC03_BEAM_CLAMP_판금'; RB = 'P_RXDC03_RISER_BRKT_밀링'; LG = 'P_RXDC03_LEAD_GUIDE_3DP'
BR = ['CB5-16_RXDC03_RISER_1', 'CB5-16_RXDC03_RISER_2', 'CB5-16_RXDCC1_RISER_3']; BG = ['CB5-16_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_2']
BT = ['CB5-12_RXDC03_T2_1', 'CB5-12_RXDC03_T2_2']; BC = ['CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2']
S = [T2, CL, RB, LG] + BR + BG + BT + BC
OUT = {}
what = sys.argv[1:]


def against():
    sc = json.load(open('../../../scope.json', encoding='utf-8'))
    sg = json.load(open('../../../signatures.json', encoding='utf-8'))['parts']
    a = set()
    for k in sc['neighbors'] + sc['changed']:
        if k in sg: a.add(sg[k]['name'])
    boxes = [[-318.6 - 95, -258.0, 65.0, 97.0, 236.0, 487.0 + 31], [-310.6 - 95, -276.5, 66.0, 84.0, 198.0, 250.0], [-357, -333, 68, 129, 603.5, 644], [-318.6 - 95, -234, 30, 110, 70, 175]]
    a |= set(nb.neighbors(S, 6, boxes))
    return sorted(a - set(S))


if 'doc' in what:
    i = tool('insp', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
    fe = i['timeline']['features'] if isinstance(i['timeline'], dict) else i['timeline']
    bn = [b if isinstance(b, str) else b.get('name') for b in i.get('bodies', [])]
    OUT['doc'] = dict(name=i.get('name'), dirty=i.get('dirty'), features=len(fe), errors=[(f['name'], f['error']) for f in fe if f.get('error')], warnings=sum(1 for f in fe if f.get('warning')),
                      suppressed=[f['name'] for f in fe if f.get('suppressed')], rolled_back=sum(1 for f in fe if f.get('rolled_back')), bodies=len(bn),
                      lite=[b for b in bn if b.startswith('LITE_')], cb4=[b for b in bn if b.startswith('CB4')], old=[b for b in bn if b in ('P_RXDC03_RISER_BRKT_판금', 'P_RXDC03_LEAD_GUIDE_판금', 'CB4-12_RXDCC1_RISER_3') or (b.startswith('CB5-12_RXDC03_RISER') or b.startswith('CB5-12_RXDC03_GUIDE'))],
                      scope_present=[b for b in S if b in bn], prb=[b for b in bn if b.startswith('PRB') or b.startswith('PP_') or b.startswith('MIS_')])
    print(json.dumps({k: (v if k != 'cb4' else len(v)) for k, v in OUT['doc'].items()}, ensure_ascii=False))
    m = fx.meas(S + ['P_RX19_BLOCK_밀링', 'P_RX19_SWING_밀링'], 'm_s')
    OUT['meas'] = m
    for k, v in m.items(): print(k, v if isinstance(v, str) else (v['volume'], v['bbox'], v['material'], v['mass'], v['closed']))
if 'flat' in what:
    fl = {}
    for n in (T2, CL, RB, LG):
        d = ex('fp_%s' % n[8:12], 'sheet.flat_pattern', body=n)
        dd = d.get('data')
        if not isinstance(dd, dict) or d.get('isError'):
            fl[n] = str(dd)[:200]; print(n, 'flat ->', fl[n]); continue
        mb = ex('mb_%s' % n[8:12], 'sheet.measure_body', body=n)['data']
        fl[n] = dd; fl[n]['_measure_body'] = mb
        print(n, 'keys', list(dd.keys()))
        print(json.dumps({k: v for k, v in dd.items() if k not in ('outline', 'outline_loops', 'faces')}, ensure_ascii=False)[:2500])
        print('mb', json.dumps(mb, ensure_ascii=False)[:600])
    OUT['flat'] = fl
if 'topo' in what:
    tp = {}
    for n in (T2, CL, RB, LG):
        d = tool('tp_%s' % n[8:12], 'body_topology', body=n, faces='all')['data']
        tp[n] = d
        print(n, 'faces', len(d.get('faces', [])), 'edges', len(d.get('edges', [])))
    for n in ('P_RX19_BLOCK_밀링', 'P_RX19_SWING_밀링', 'P_M07_BEAM'):
        d = tool('tc_%s' % n[2:8], 'body_topology', body=n, faces='cylinders')['data']
        tp[n] = d
        print(n, 'cyl', len(d.get('cylinders', [])) if isinstance(d, dict) else str(d)[:200])
    json.dump(tp, open('topo.json', 'w', encoding='utf-8'), ensure_ascii=False)
AG = against()
OUT['against_n'] = len(AG)
P = {}
if 'pose' in what:
    print('against', len(AG))
    for v in (0, 23.75, 47.5, 71.25, 95):
        drive('J_U4_X', v)
        P['J_U4_X_%s' % v] = clr('u4x_%s' % str(v).replace('.', 'p'), S, AG, 2.0, 14)
    drive('J_U4_X', 0)
    for v in (-8.171, -1.2475, 5.676, 12.5995, 19.523):
        drive('J_U4_PRESS', v)
        P['J_U4_PRESS_%s' % v] = clr('press_%s' % str(v).replace('.', 'p').replace('-', 'm'), S, AG, 2.0, 14)
    drive('J_U4_PRESS', 19.523)
if 'xp' in what:
    drive('J_U4_X', 95)
    for v in (-8.171, 19.523):
        drive('J_U4_PRESS', v)
        P['X95_PRESS_%s' % v] = clr('xp_95_%s' % str(v).replace('.', 'p').replace('-', 'm'), S, AG, 2.0, 14)
    drive('J_U4_PRESS', 19.523); drive('J_U4_X', 0)
if 'c46' in what:
    drive('J_U4_X', 95); drive('J_U5_X', 1365)
    W = ['P_M03_WHEEL', 'P_M03_WHEEL_TREAD', 'CB5-12_M03_HUB', 'CB5-16_M03_HUB']
    sgn = {p['name'] for p in nb.parts()}
    W = [w for w in W if w in sgn] + sorted(n for n in sgn if n.startswith('CB5-16_M03_HUB (') or n.startswith('CB5-12_M03_HUB ('))
    L = [T2, RB, LG, 'STEP대기_HG-KR23_LEAD_LOOP', 'STEP대기_HG-KR23_LEAD_ENC', 'STEP대기_HG-KR23_LEAD_PWR', 'STEP대기_HG-KR23_CONN_ENC', 'STEP대기_HG-KR23_CONN_PWR'] + BG + BR + BT
    L = [x for x in L if x in sgn]
    print('wheel set', W)
    P['C46_95_1365'] = clr('c46', L, W, 15.0, 10)
    drive('J_U5_X', 0); drive('J_U4_X', 0)
if 'rest' in what:
    r = ex('rest', 'motion.play', study='REST', step=0)
    print('rest', json.dumps(r['data'], ensure_ascii=False)[:200])
    m = fx.meas([RB, LG, T2, CL] + BR[:1] + BG[:1], 'm_rest')
    OUT['rest_meas'] = m
    for k, v in m.items(): print(k, v['bbox'])
OUT['poses'] = P
if 'jl' in what:
    j = ex('jl', 'joint.list')['data']
    OUT['joints'] = dict(floating=j['floating'], conflicts=j['conflicts'], errors=j['errors'], n=len(j['joints']))
    print('joints', OUT['joints'])
old = json.load(open('v1.json', encoding='utf-8')) if os.path.exists('v1.json') else {}
for k, v in OUT.items():
    if k == 'poses': old.setdefault('poses', {}).update(v)
    else: old[k] = v
json.dump(old, open('v1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
