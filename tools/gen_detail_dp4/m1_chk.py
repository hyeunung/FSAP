"""수정 1회차 저장 전 검사(세션 41083): 타임라인 · 전개 · 자세별 틈 · C-46 한계 · 떠 있는 부품. 결과 chk1.json"""
import sys, os, json, time, fx, nb
from fx import ex, tool, C, clr, drive
T2 = 'P_RXDC03_T2_GUIDE_판금'; CL = 'P_RXDC03_BEAM_CLAMP_판금'; RB = 'P_RXDC03_RISER_BRKT_밀링'; LG = 'P_RXDC03_LEAD_GUIDE_3DP'
BR = ['CB5-16_RXDC03_RISER_1', 'CB5-16_RXDC03_RISER_2', 'CB5-16_RXDCC1_RISER_3']; BG = ['CB5-16_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_2']
BT = ['CB5-12_RXDC03_T2_1', 'CB5-12_RXDC03_T2_2']; BC = ['CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2']
OLDN = ['P_RXDC03_RISER_BRKT_판금', 'P_RXDC03_LEAD_GUIDE_판금', 'CB5-12_RXDC03_RISER_1', 'CB5-12_RXDC03_RISER_2', 'CB4-12_RXDCC1_RISER_3', 'CB5-12_RXDC03_GUIDE_1', 'CB5-12_RXDC03_GUIDE_2']
S = [T2, CL, RB, LG] + BR + BG + BT + BC
OUT = {}
what = sys.argv[1:] or ['tl', 'flat', 'pose', 'c46', 'jl']
if 'tl' in what:
    i = tool('insp_chk', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
    fe = i['timeline']['features'] if isinstance(i['timeline'], dict) else i['timeline']
    OUT['timeline'] = dict(features=len(fe), errors=[(f['name'], f['error']) for f in fe if f.get('error')], warnings=sum(1 for f in fe if f.get('warning')),
                           warn_new=[(f['name'], f['warning'][:80]) for f in fe if f.get('warning') and f['id'] > 101290], suppressed=[f['name'] for f in fe if f.get('suppressed')], bodies=len(i.get('bodies', [])), dirty=i.get('dirty'), name=i.get('name'))
    print('timeline', OUT['timeline'])
if 'flat' in what:
    fl = {}
    for n in (T2, CL):
        d = ex('fp_%s' % n[-6:], 'sheet.flat_pattern', body=n)['data']
        mb = ex('mb_%s' % n[-6:], 'sheet.measure_body', body=n)['data']
        if not isinstance(d, dict): print(n, 'FLAT ERR', str(d)[:300]); continue
        fl[n] = dict(flat_size=d.get('flat_size_mm'), rule=d.get('rule'), thickness=d.get('thickness'), bends=d.get('bends'), outline=d.get('outline') or d.get('outline_loops'),
                     holes=[c.get('circle') for c in d.get('cutout_shapes', [])], measure_body=mb if isinstance(mb, dict) else str(mb)[:300], keys=list(d.keys()))
        print(n, 'flat', d.get('flat_size_mm'), 'bends', json.dumps(d.get('bends'), ensure_ascii=False)[:500], 'holes', fl[n]['holes'], 'mb', json.dumps(mb, ensure_ascii=False)[:200])
    OUT['flat'] = fl
    for n in (RB, LG):
        d = ex('fp_x', 'sheet.flat_pattern', body=n)['data']
        print(n, 'flat ->', str(d)[:120])
boxes = [[-318.6 - 95, -258.0, 65.0, 97.0, 236.0, 487.0 + 31], [-310.6 - 95, -276.5, 66.0, 84.0, 198.0, 250.0], [-357, -333, 68, 129, 603.5, 644], [-318.6 - 95, -234, 30, 110, 70, 175]]
AG = sorted(set(nb.neighbors([T2, CL] + OLDN + BT + BC, 6, boxes)) - set(S) - set(OLDN))
OUT['against_n'] = len(AG)
P = {}
if 'pose' in what:
    print('against', len(AG))
    for v in (0, 23.75, 47.5, 71.25, 95):
        drive('J_U4_X', v)
        P['J_U4_X_%s' % v] = clr('u4x_%s' % str(v).replace('.', 'p'), S, AG, 1.0, 12)
    drive('J_U4_X', 0)
    for v in (-8.171, 5.676, 19.523):
        drive('J_U4_PRESS', v)
        P['J_U4_PRESS_%s' % v] = clr('press_%s' % str(v).replace('.', 'p').replace('-', 'm'), S, AG, 2.0, 12)
    drive('J_U4_PRESS', 19.523)
if 'c46' in what:
    drive('J_U4_X', 95); drive('J_U5_X', 1365)
    W = ['P_M03_WHEEL', 'P_M03_WHEEL_TREAD', 'CB5-16_M03_HUB']
    L = [T2, RB, LG, 'STEP대기_HG-KR23_LEAD_LOOP', 'STEP대기_HG-KR23_LEAD_ENC', 'STEP대기_HG-KR23_LEAD_PWR', 'STEP대기_HG-KR23_CONN_ENC', 'STEP대기_HG-KR23_CONN_PWR'] + BG + BR
    P['C46_95_1365'] = clr('c46', L, W, 15.0)
    drive('J_U5_X', 0); drive('J_U4_X', 0)
    r = ex('rest', 'motion.play', study='REST', step=0)
    print('rest', json.dumps(r['data'], ensure_ascii=False)[:160])
OUT['poses'] = P
if 'jl' in what:
    j = ex('jl2', 'joint.list')['data']
    OUT['joints'] = dict(floating=j['floating'], conflicts=j['conflicts'], errors=j['errors'], n=len(j['joints']))
    print('joints', OUT['joints'])
old = json.load(open('chk1.json', encoding='utf-8')) if os.path.exists('chk1.json') else {}
for k, v in OUT.items():
    if k == 'poses': old.setdefault('poses', {}).update(v)
    else: old[k] = v
json.dump(old, open('chk1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
