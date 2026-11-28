"""DP-3(보 탭 · 끝판 · 관 받침) 실행기 — 헤드리스 세션 41080. usage(작업 폴더 tools/out/detail/DP-3/m0 에서):
    python -X utf8 -B ../../../../gen_detail_dp3/build.py <stage>
단계마다 보낸 명령을 cmds_<stage>.json(편집 기록), 결과를 r_<tag>.json 에 남긴다."""
import json, sys, math, q

REC = []
def C(command, **params): return {'command': command, 'params': params}

def run(tag, cmds, verbose=False, rollback=True, rec=True):
    if rec: REC.extend(cmds)
    u = q.call(tag, {'commands': cmds, 'rollback': rollback, 'verbose': verbose})
    d = u.get('data')
    if u.get('isError') or isinstance(d, str) or not d or not d.get('ok'):
        print('FAIL', tag, (json.dumps(d, ensure_ascii=False) if not isinstance(d, str) else d)[:2500])
        json.dump(REC, open('cmds_FAILED_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
        sys.exit(2)
    print('ok', tag, len(cmds), 'cmds', '%.1f s' % u['s'])
    return d['results']

def meas(names, tag='meas'):
    out = {}
    for n in names:
        u = q.call(tag, {'tool': 'measure', 'arguments': {'body': n}})
        d = u['data']; b = [x for x in d['bodies'] if x['name'] == n]
        b = b[0] if b else d['bodies'][0]
        out[n] = dict(volume=round(b['volume_mm3'], 3), bbox=[round(v, 3) for v in b['bbox']['min'] + b['bbox']['max']], material=b.get('material'), mass=round(b.get('mass_g', 0), 3), shells=b.get('kernel', {}).get('shells'), faces=b.get('faces'))
    return out

BEAM = 'P_M07_BEAM'
def cyl(name, tgt, r, base, axis, h, op='cut'):
    return C('solid.cylinder', radius=r, height=h, base=base, axis=axis, operation=op, targets=[tgt], name=name)
def box(name, tgt, x0, x1, y0, y1, z0, z1, op='join'):
    return C('solid.box', corner=[x0, y0, z0], length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation=op, targets=[tgt], name=name)

# ---- 자리 ----
REG_X = [686, 714, 786, 814, 886, 914]; REG_Z = 527.8
CB4_NEW = [(1039.8, 343.0), (1039.8, 359.0)]
COMB_NEW_X = [250, 650, -350, -950]
HMI = [(1170, 350), (1170, 530), (1210, 350), (1210, 530)]
L6 = [(-362, 276), (-350, 276)]
LBRK = [(-2360, 600)]
CAP_X = {'NX': -2362.0, 'PX': 1332.0}   # 끝에서 18 (굽힘 끝선 6 + 2t+R 9 + 구멍 반지름 2.1 = 17.1 → 18)
CAP_Z = [350.0, 550.0]

def stage_A():
    """보: 탭 19 · 빈 탭 4 메움 · 끝판 2 + 속 막 1 떼기 · 덮개 볼트 구멍 8 / 이음판: 머리 구멍 4"""
    before = meas([BEAM, 'P_M07_SPLICE_NX', 'P_M07_SPLICE_PX'], 'A_before')
    json.dump(before, open('A_before.json', 'w'), indent=0)
    c = [C('component.activate', component='U1_FRAME')]
    for i, x in enumerate(REG_X): c.append(cyl('DP3_BEAM_TAP_M4_REG_%d' % (i + 1), BEAM, 1.65, [x, 119.9, REG_Z], [0, 1, 0], 8.2))
    for i, (x, z) in enumerate(CB4_NEW): c.append(cyl('DP3_BEAM_TAP_M4_SOL_%d' % (i + 1), BEAM, 1.65, [x, 119.9, z], [0, 1, 0], 8.2))
    for i, x in enumerate(COMB_NEW_X): c.append(cyl('DP3_BEAM_TAP_M5_COMB_%d' % (i + 1), BEAM, 2.1, [x, 166, 641.9], [0, 0, 1], 8.2))
    for i, (x, z) in enumerate(HMI): c.append(cyl('DP3_BEAM_TAP_M5_HMI_%d' % (i + 1), BEAM, 2.1, [x, 119.9, z], [0, 1, 0], 8.2))
    for i, (x, z) in enumerate(L6): c.append(cyl('DP3_BEAM_TAP_M5_CLAMP_L6_%d' % (i + 1), BEAM, 2.1, [x, 119.9, z], [0, 1, 0], 8.2))
    for i, (x, z) in enumerate(LBRK): c.append(cyl('DP3_BEAM_TAP_M5_LBRK_R3', BEAM, 2.1, [x, 119.9, z], [0, 1, 0], 8.2))
    r = run('A1_taps', c)
    m1 = meas([BEAM], 'A1_meas')
    c = [cyl('DP3_BEAM_FILL_NZ_1', BEAM, 2.4, [-255, 248, 250], [0, 0, 1], 8, 'join'),
         cyl('DP3_BEAM_FILL_NZ_2', BEAM, 2.4, [-225, 248, 250], [0, 0, 1], 8, 'join'),
         cyl('DP3_BEAM_FILL_NY_1', BEAM, 2.4, [-345, 120, 522], [0, 1, 0], 8, 'join'),
         cyl('DP3_BEAM_FILL_NY_2', BEAM, 2.4, [-345, 120, 534], [0, 1, 0], 8, 'join')]
    run('A2_fill', c)
    m2 = meas([BEAM], 'A2_meas')
    c = [box('DP3_BEAM_OLD_END_FILL', BEAM, 1221, 1231, 127, 313, 257, 643, 'join'),
         C('solid.extrude', sketch='SK_M07_BEAM_IN', distance=3732, direction='positive', operation='cut', targets=[BEAM], name='DP3_BEAM_ENDPLATE_CUT')]
    run('A3_endplate', c)
    m3 = meas([BEAM], 'A3_meas')
    c = []
    for e, x in CAP_X.items():
        for i, z in enumerate(CAP_Z):
            c.append(cyl('DP3_BEAM_CAP_HOLE_%s_F%d' % (e, i + 1), BEAM, 2.75, [x, 119.9, z], [0, 1, 0], 8.2))
            c.append(cyl('DP3_BEAM_CAP_HOLE_%s_B%d' % (e, i + 1), BEAM, 2.75, [x, 320.1, z], [0, -1, 0], 8.2))
            c.append(cyl('DP3_SPLICE_%s_HEAD_HOLE_%d' % (e, i + 1), 'P_M07_SPLICE_%s' % e, 5.0, [x, 319.9, z], [0, 1, 0], 6.2))
    c.append(C('component.activate', component='root'))
    run('A4_capholes', c)
    after = meas([BEAM, 'P_M07_SPLICE_NX', 'P_M07_SPLICE_PX'], 'A_after')
    json.dump(dict(before=before, taps=m1, fill=m2, endplate=m3, after=after), open('A_result.json', 'w'), indent=0)
    v0 = before[BEAM]['volume']
    exp_t = 11 * math.pi * 2.1 ** 2 * 8 + 8 * math.pi * 1.65 ** 2 * 8
    exp_f = 4 * math.pi * 2.1 ** 2 * 8
    ain = 184 * 384 - 4 * (16 - math.pi * 4)
    exp_e = ain * (8 + 7 + 1) - (16 - math.pi * 4) * 4 * 8
    exp_h = 8 * math.pi * 2.75 ** 2 * 8
    print('taps  d %.2f exp %.2f' % (v0 - m1[BEAM]['volume'], exp_t))
    print('fill  d %.2f exp %.2f' % (m2[BEAM]['volume'] - m1[BEAM]['volume'], exp_f))
    print('endpl d %.2f exp %.2f' % (m2[BEAM]['volume'] - m3[BEAM]['volume'], exp_e))
    print('holes d %.2f exp %.2f' % (m3[BEAM]['volume'] - after[BEAM]['volume'], exp_h))
    for s in ('NX', 'PX'):
        n = 'P_M07_SPLICE_' + s
        print(n, 'd %.2f exp %.2f' % (before[n]['volume'] - after[n]['volume'], 2 * math.pi * 25 * 6))
    print('beam bbox', after[BEAM]['bbox'])

if __name__ == '__main__':
    st = sys.argv[1]
    globals()['stage_' + st]()
    json.dump(REC, open('cmds_%s.json' % st, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
