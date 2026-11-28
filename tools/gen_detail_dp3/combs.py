"""DP-3 관 빗 11개: 보 앞 윗모서리에 걸리는 턱(높이 3) + 재질 26품번 PET-CF. usage: combs.py lips | mats"""
import json, sys, q
def C(command, **params): return {'command': command, 'params': params}
def box(name, tgt, x0, x1, y0, y1, z0, z1):
    return C('solid.box', corner=[x0, y0, z0], length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation='join', targets=[tgt], name=name)
def run(tag, cmds):
    u = q.call(tag, {'commands': cmds, 'rollback': True, 'verbose': False}); d = u['data']
    if u.get('isError') or isinstance(d, str) or not d.get('ok'):
        print('FAIL', tag, json.dumps(d, ensure_ascii=False)[:2000]); sys.exit(2)
    print('ok', tag, len(cmds), '%.1f s' % u['s']); return d['results']
def meas(n):
    b = q.call('mm', {'tool': 'measure', 'arguments': {'body': n}})['data']['bodies']
    b = [x for x in b if x['name'] == n][0]
    return dict(volume=round(b['volume_mm3'], 3), bbox=[round(v, 3) for v in b['bbox']['min'] + b['bbox']['max']], material=b['material'], mass=round(b['mass_g'], 3), shells=b['kernel']['shells'])
# 이름: (X 가운데, 앞면 Y, 윗면 Z, 종류)
COMBS = {'P_M08_TUBE_COMB_ML_1': (250, 124, 697, 'A'), 'P_M08_TUBE_COMB_ML_2': (650, 124, 697, 'A'), 'P_M08_TUBE_COMB_ML_3': (-350, 124, 697, 'A'), 'P_M08_TUBE_COMB_ML_4': (-950, 124, 697, 'A'),
         'P_M08_TUBE_COMB_ML_5': (950, 124, 698, 'B'), 'P_M08_TUBE_COMB_ML_6': (450, 124, 698, 'B'), 'P_M08_TUBE_COMB_ML_9': (1000, 124, 698, 'B'),
         'P_M08_TUBE_COMB_ML_7': (50, 124, 718, 'C'),
         'P_M08_TUBE_COMB_ML_8': (-650, 158, 698, 'D'), 'P_M08_TUBE_COMB_U5_1': (-100, 158, 698, 'D'), 'P_M08_TUBE_COMB_U5_2': (-1245, 158, 697, 'E')}
YF, YL, ZL, ZB = 120.2, 123.8, 647.0, 650.1     # 턱 앞면 · 턱 안쪽면 · 턱 밑 · 빗 밑면
EXP = {'A': 16 * 3.8 * 46.9, 'B': 16 * 3.8 * 47.9, 'C': 16 * 3.8 * 67.9, 'D': 16 * 37.8 * 5, 'E': 16 * 37.8 * 5}
LIP = 16 * (YL - YF) * (ZB - ZL)
CLAMPS = ['P_M08_TUBE_CLAMP_F_%d' % i for i in range(1, 7)] + ['P_M08_TUBE_CLAMP_L_%d' % i for i in range(1, 7)] + ['P_M08_TUBE_CLAMP_SO_%d' % i for i in range(1, 4)]
if sys.argv[1] == 'lips':
    Cs = q.unwrap('r_complist.json')['data']['components']; BYN = {c['name']: c for c in Cs}
    rec = []; res = {}
    for n, (xc, yf, zt, k) in COMBS.items():
        b0 = meas(n)
        comp = n if n in BYN else 'U8_PNEU'
        cmds = [C('component.activate', component=comp)]
        if k in 'ABC':
            cmds.append(box('DP3_LIP_BASE_' + n[6:], n, xc - 8, xc + 8, YF, yf + 1, ZB, zt))      # 앞면을 Y 120.2 까지 한 면으로
        else:
            cmds.append(box('DP3_LIP_BASE_' + n[6:], n, xc - 8, xc + 8, YF, yf + 1, ZB, ZB + 5))  # 밑 받침 살 t5 를 보 앞 모서리까지
        cmds.append(box('DP3_LIP_' + n[6:], n, xc - 8, xc + 8, YF, YL, ZL, ZB + 0.9))               # 턱: 높이 3.1(빗 밑 650.1 -> 647)
        cmds.append(C('component.activate', component='root'))
        run('lip_' + n[6:], cmds); rec += cmds
        b1 = meas(n); d = b1['volume'] - b0['volume']; e = EXP[k] + LIP
        res[n] = dict(kind=k, before=b0, after=b1, dvol=round(d, 3), expected=round(e, 3))
        print(n, k, 'd %.2f exp %.2f' % (d, e), b1['bbox'], 'shells', b1['shells'])
    json.dump(rec, open('cmds_C.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(res, open('C_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
else:
    names = list(COMBS) + CLAMPS
    cmds = [C('material.assign', bodies=names, material='PET-CF')]
    run('mats', cmds)
    json.dump(cmds, open('cmds_E.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    res = {n: meas(n) for n in names}
    json.dump(res, open('E_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(names), set(v['material'] for v in res.values()), 'mass sum %.1f g' % sum(v['mass'] for v in res.values()))
