# -*- coding: utf-8 -*-
"""N04 해석부 2회차 손계산 — v1.0.14 수정 1회차로 바뀐 하중 부품 5파일(CYLBKT·SADDLE·STORE·PANEL·CHAIN_HEAD).
FEA 환경 없음(D-16). 형상은 tools/out/mech_N04/stepout/*.step의 바디별 점 bbox·고유 좌표로 확인한다(이 스크립트가 다시 읽음).
월드 mm, REST(J 0). 하중·기준은 1회차(mech_N04_handcalc.py 머리말)와 같다:
  손 운전 100 N / 오조작 300 N(작은 받침은 손바닥 100x100 0.01 / 0.03 MPa), 자중 x3 g / x1 g,
  CDJ2B16 추력 0.5 MPa 100.5 N / 0.7 MPa 140.7 N(요구서 2-4 미정 -> 0-6 공급 0.5 MPa), 사슬 6.5 kg 전부 보관 하나(보수),
  매트 끌림 30 / 100 N(D-79). 판정 M-09 운전 SF 3·오조작 SF 2, SF < 1.2 = 영구 변형(동작).
재질 항복(하한): SUS304 205, A6063-T5 110(JIS 하한), A5052 표피 175.
"""
import json, math, re, sys, os
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

G = 9.81
RP = {'SUS304': 205.0, 'A6063': 110.0, 'A5052': 175.0}
E = {'SUS304': 193000.0, 'A6063': 69000.0}
SFMIN = {'run': 3.0, 'mis': 2.0}
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SD = ROOT + '/tools/out/mech_N04/stepout'
out = {'_note': 'N04 해석 2회차 손계산(FEA 환경 없음 D-16). 단위 mm·N·MPa', 'bodies': {}, 'items': [], 'old_vs_new': {}}
F_CYL = {'run': math.pi / 4 * 16 ** 2 * 0.5, 'mis': math.pi / 4 * 16 ** 2 * 0.7}
GF = {'run': 3.0, 'mis': 1.0}
PALM = {'run': 0.01, 'mis': 0.03}
DRAG = {'run': 30.0, 'mis': 100.0}


def item(part, where, case, stress, mat, extra=None, shear=False):
    rp = RP[mat] / math.sqrt(3) if shear else RP[mat]
    sf = rp / stress if stress else float('inf')
    r = {'part': part, 'where': where, 'case': case, 'stress_MPa': round(stress, 2), 'mat': mat, 'shear': shear,
         'sf': round(sf, 2), 'sf_min': SFMIN[case], 'ok': sf >= SFMIN[case],
         'near_10pct': 0.9 * SFMIN[case] <= sf < 1.1 * SFMIN[case], 'oversize_3x': sf >= 3 * SFMIN[case], 'motion_break': sf < 1.2}
    if extra:
        r.update(extra)
    out['items'].append(r)
    return r


# ---- 0) STEP 바디별 bbox(MANIFOLD_SOLID_BREP 앞의 점 = 그 바디의 점, 원점 축 놓기 점은 뺌)
BS = chr(92)
X2 = re.compile(re.escape(BS + 'X2' + BS) + '([0-9A-F]+)' + re.escape(BS + 'X0' + BS))
for fn in ('P_N04_CYLBKT', 'P_N04_SADDLE', 'P_N04_STORE', 'P_N04_PANEL', 'P_N04_CHAIN_HEAD'):
    pts = []
    for line in open(SD + '/' + fn + '.step', encoding='latin-1'):
        m = re.search(r"CARTESIAN_POINT\('[^']*',\(([-\d.Ee+]+),([-\d.Ee+]+),([-\d.Ee+]+)\)\)", line)
        if m:
            v = tuple(float(x) for x in m.groups())
            if v != (0.0, 0.0, 0.0):
                pts.append(v)
        m = re.search(r"MANIFOLD_SOLID_BREP\('([^']*)'", line)
        if m:
            nm = X2.sub(lambda k: ''.join(chr(int(k.group(1)[i:i + 4], 16)) for i in range(0, len(k.group(1)), 4)), m.group(1))
            out['bodies'][nm] = {'file': fn, 'bbox': [[round(min(p[i] for p in pts), 2), round(max(p[i] for p in pts), 2)] for i in range(3)]}
            if len(pts) < 60:
                out['bodies'][nm]['uniq'] = [sorted(set(round(p[i], 1) for p in pts)) for i in range(3)]
            pts = []
B = out['bodies']
# 형상 확인(수정 1회차 보고서 2절 값과 같아야 계속)
assert B['P_N04_CYLBKT_P']['uniq'][1] == [1533.0, 1537.0, 1545.0] and B['P_N04_CYLBKT_P']['uniq'][2] == [-125.0, -44.0, -40.0]
assert B['P_N04_CYLBKT_A']['uniq'][0] == [-2010.0, -2008.0, -2000.0, -1950.0] and B['P_N04_CYLBKT_A']['uniq'][2] == [-192.0, -44.0, -40.0]
assert -950.0 in B['P_N04_SADDLE']['uniq'][0] and -850.0 in B['P_N04_SADDLE']['uniq'][0]
z_cyl_pn = sum(B['STEP대기_CDJ2B16-110_P']['bbox'][2]) / 2       # −112
z_cyl_a = sum(B['STEP대기_CDJ2B16-150_A']['bbox'][2]) / 2        # −180
out['axis_z'] = {'P/N': round(z_cyl_pn, 2), 'A': round(z_cyl_a, 2)}

# ---- 1) CYLBKT_P/_N: 세운 판 50×t4(Y 1533~1537) 뿌리 Z −44, 날개 Z −44~−40 · Y 1533~1545(바깥으로 8)
arm_pn = -44.0 - z_cyl_pn                                     # 68
for case in ('run', 'mis'):
    M = F_CYL[case] * arm_pn
    item('P_N04_CYLBKT_P/_N', '세운 판 뿌리 Z −44(50×t4, 팔 %.0f)' % arm_pn, case, M / (50 * 16 / 6), 'SUS304', {'M_Nmm': round(M)})
    # 날개 Y 1537 단면(50×t4)은 같은 M(받침 = 바깥 끝 1545 발꿈치, 인서트 = 날개 가운데 1541)
    item('P_N04_CYLBKT_P/_N', '날개 뿌리 Y 1537(50×t4, 같은 M)', case, M / (50 * 16 / 6), 'SUS304')
    out.setdefault('insert_pull_N', {})['CYLBKT_P/_N 날개 가운데 인서트(발꿈치 1545까지 4) ' + case] = round(M / 4.0)
    out['insert_pull_N']['CYLBKT_P/_N 안쪽 날개 안(뿌리 1533에서 12) ' + case] = round(M / 16.0)
out['cylbkt_pn_beam'] = beam(4.0, 50.0, arm_pn, load=F_CYL['run'], e=E['SUS304'], sy=RP['SUS304'], sf_min=3.0)

# ---- 2) CYLBKT_A: 통 블록 X −2008~−2000(t8) × Y ±20 × Z −192~−44 + 받침판 X −2010~−1950 × Z −44~−40(t4)
arm_a = -44.0 - z_cyl_a                                       # 136
cg = (-2000.0 + B['STEP대기_CDJ2B16-150_A']['bbox'][0][1]) / 2 - (-2004.0)   # 몸 무게 중심 ↔ 블록 가운데 X 94
m_cyl_a = 0.454
for case in ('run', 'mis'):
    M = F_CYL[case] * arm_a + m_cyl_a * GF[case] * G * cg
    # (옛 모델) 블록 뿌리 Z −44 고정
    r_old = item('P_N04_CYLBKT_A', '블록 뿌리 Z −44(40×t8, 팔 %.0f) — 옛 모델(뿌리 고정)' % arm_a, case, M / (40 * 64 / 6), 'SUS304', {'M_Nmm': round(M)})
    # (새 모델) 받침판이 판 밑면에 인서트로: 발꿈치 X −2010(눌림), 당김 줄 X −1955(끝에서 5) → 블록 +X 면 X −2000 판 단면 40×t4
    T = M / 55.0
    Mp = T * 45.0
    r_new = item('P_N04_CYLBKT_A', '받침판 X −2000 단면(40×t4) — 새 모델(발꿈치 −2010, 당김 줄 −1955)', case, Mp / (40 * 16 / 6), 'SUS304',
                 {'M_plate_Nmm': round(Mp), 'insert_pull_N': round(T)})
    # 고친 안: 받침판 t8(Z −48~−40) 또는 블록 양옆 리브
    item('P_N04_CYLBKT_A(받침판 t8 안)', '받침판 X −2000 단면(40×t8)', case, Mp / (40 * 64 / 6), 'SUS304')
    out['old_vs_new']['CYLBKT_A ' + case] = {'old_block_root_sf': r_old['sf'], 'new_plate_sf': r_new['sf']}
    out.setdefault('insert_pull_N', {})['CYLBKT_A 당김 줄 −1955 ' + case] = round(T)
# 멈춤 자리 밀림(운전): 블록 휨 + 받침판 회전 × 팔
I_blk = 40 * 8 ** 3 / 12.0
I_pl = 40 * 4 ** 3 / 12.0
Mr = F_CYL['run'] * arm_a + m_cyl_a * 3 * G * cg
d_blk = F_CYL['run'] * arm_a ** 3 / (3 * E['SUS304'] * I_blk)
th = (0.818 * Mr / 2) * 45.0 / (E['SUS304'] * I_pl)
out['cylbkt_a_stop_shift_run_mm'] = {'block_bend': round(d_blk, 3), 'plate_rotation': round(th * (arm_a + 4), 3),
                                     'total': round(d_blk + th * (arm_a + 4), 3),
                                     'plate_t8_total': round(d_blk + th / 8 * (arm_a + 8), 3)}

# ---- 3) STOP 로드(구매품 CDJ2B16 로드 Ø5, 참고 M-06) 좌굴: 끝이 사슬에 걸린 외팔 K 2
Ir = math.pi * 5 ** 4 / 64
for nm, Lf in (('CDJ2B16-110 로드(내밂 끝 자유 길이 약 123)', 123.0), ('CDJ2B16-150 로드(약 163)', 163.0)):
    Pcr = math.pi ** 2 * E['SUS304'] * Ir / (2 * Lf) ** 2
    out.setdefault('rod_buckling_ref', {})[nm] = {'Pcr_N': round(Pcr), 'sf_vs_mis_thrust': round(Pcr / F_CYL['mis'], 2)}
out['stop_pad_bearing_MPa'] = round(F_CYL['mis'] / (math.pi / 4 * 16 ** 2), 2)

# ---- 4) SADDLE: 다리 2(X −950~−850, t4, Y −470~−466/−334~−330, 높이 129) + 윗판 t2 Z −2~0(가운데 Ø126, 중심 (−900, −400))
cx, cy, r = -900.0, -400.0, 63.0


def flap(pres, x0, xe):
    F = M = A = 0.0
    n = 200
    for i in range(n):
        x = x0 + (xe - x0) * (i + 0.5) / n
        for j in range(n):
            y = -470 + 140.0 * (j + 0.5) / n
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                continue
            dA = ((xe - x0) / n) * (140.0 / n)
            A += dA; F += pres * dA; M += pres * dA * abs(xe - x)
    return A, F, M


b_root = 2 * (70 - math.sqrt(r * r - 50 ** 2))                 # X −950 단면 띠 폭 63.3
for case in ('run', 'mis'):
    A, F, M = flap(PALM[case], -966.0, -950.0)
    item('P_N04_SADDLE', '윗판 날개 뿌리 X −950(띠 폭 %.1f, t2, 외팔 16)' % b_root, case, M / (b_root * 4 / 6), 'SUS304',
         {'flap_area_mm2': round(A), 'F_N': round(F, 2)})
    # 다리 뿌리 면 밖(Y 끌림): 100×t4 ×2, 팔 129
    item('P_N04_SADDLE', '다리 뿌리 면 밖 굽힘(100×t4 ×2, 팔 129)', case, DRAG[case] * 129 / (2 * 100 * 16 / 6), 'SUS304')
    # 다리 압축 + 좌굴(외팔 K 2, I = 100·4³/12)
    P = 100.0 if case == 'run' else 300.0
    item('P_N04_SADDLE', '다리 압축(2 × 100×t4)', case, P / (2 * 400), 'SUS304')
Pcr_leg = math.pi ** 2 * E['SUS304'] * (100 * 4 ** 3 / 12) / (2 * 129.0) ** 2
out['saddle_leg_buckling'] = {'Pcr_N_per_leg': round(Pcr_leg), 'sf_vs_mis_300N': round(2 * Pcr_leg / 300.0, 1)}

# ---- 5) STORE: P/N 안쪽 폭 137(−968.5~−831.5), A 안쪽 109 · 길이 727.5. 바닥 t1.5 단순 받침, 턱 10 외팔, 옆벽 매달림
for nm, span, Lst in (('P_N04_STORE_P/_N', 137.0, 600.0), ('P_N04_STORE_A', 109.0, 727.5)):
    for case in ('run', 'mis'):
        w = 6.5 * GF[case] * G / Lst
        item(nm, '바닥판 가운데(폭 %g 단순, t1.5)' % span, case, (w / span) * span ** 2 / 8 / (1.5 ** 2 / 6), 'SUS304')
        item(nm, '턱 뿌리(외팔 10, t1.5)', case, (w / 2) * 10.0 / (1.5 ** 2 / 6), 'SUS304')
        item(nm, '옆벽 매달림 인장(2 × t1.5)', case, w / (2 * 1.5), 'SUS304')
# STORE_A 끝 따냄(X −1278~−1272.5, Z −172 아래): 옆벽이 Z −172~−40만 남는 5.5 길이 — 매달림 끝 구간이라 굽힘 없음, 기록만
out['store_a_notch'] = '옆벽 끝 5.5 mm 구간 높이 160 → 132. 매달림 인장만 받는 끝이라 응력 변화 없음'

# ---- 6) CHAIN_HEAD(A6063 t5): 홈 턱 위를 미끄러지며 매트 밑 작업면이 된다. 손바닥이 머리 위에
#   P/N: X −966~−834(132), 턱 X −966~−964·−836~−834에 얹힘 → 지지 간격 130, 폭 92.5
#   A:   Y ±54(108), 턱 ±51~±54 → 지지 간격 105, 폭 42 (손바닥 넓이 중 머리 위 42×100만)
for nm, L, b, mat in (('P_N04_CHAIN_P/N_HEAD', 130.0, 92.5, 'A6063'), ('P_N04_CHAIN_A_HEAD', 105.0, 42.0, 'A6063')):
    I = b * 5 ** 3 / 12.0
    for case in ('run', 'mis'):
        P = PALM[case] * min(b, 100.0) * 100.0
        M = P * L / 4 - P * 100.0 / 8                     # 가운데 길이 100 고른 하중, 단순 받침
        item(nm, '단순 받침 가운데(지지 %g, 폭 %g, t5)' % (L, b), case, M / (b * 25 / 6), mat, {'P_N': round(P, 1)})
        out.setdefault('head_deflect_mm', {})[nm + ' ' + case] = round(P * L ** 3 / (48 * E['A6063'] * I), 3)
    out.setdefault('head_lip_bearing_MPa', {})[nm] = round(300.0 / 2 / (2.0 * b if 'P/N' in nm else 3.0 * 42), 2)
# 오조작 300 N을 한 점으로(보수)
for nm, L, b in (('P_N04_CHAIN_P/N_HEAD', 130.0, 92.5), ('P_N04_CHAIN_A_HEAD', 105.0, 42.0)):
    item(nm + '(300 N 한 점 보수)', '단순 받침 가운데 집중', 'mis', 300.0 * L / 4 / (b * 25 / 6), 'A6063')

# ---- 7) PANEL: 바뀐 곳은 A 통로 X −1292.5~−1272.5에서 아래 턱 ±51 → ±55(턱 4 × 깊이 35 × 길이 20 뺌)뿐
out['panel_change'] = {'removed_lip_mm3': 2 * 4 * 35 * 20, 'section_width_loss_pct_at_X-1282': round(2 * 4 / 3105 * 100, 2),
                       'note': '판 전체(폭 3105) 단면 손실 0.26 %. 1회차 PANEL 값(±X 외팔 운전 18.3·오조작 10.2)에 변화 없음. 매다는 무게 증가(STORE_A 690→727.5, CYLBKT_A 452 g)는 0.1 kg 미만'}

json.dump(out, open(ROOT + '/fea/results/mech_N04_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
bad = [i for i in out['items'] if not i['ok']]
print('items', len(out['items']), 'not ok', len(bad), 'motion_break', sum(i['motion_break'] for i in out['items']))
for i in out['items']:
    flag = 'BREAK' if i['motion_break'] else ('NG' if not i['ok'] else ('OVER' if i['oversize_3x'] else 'ok'))
    print('%-5s %-26s %-4s %8.2f SF %6.2f  %s' % (flag, i['part'][:26], i['case'], i['stress_MPa'], i['sf'], i['where'][:46]))
for k in ('axis_z', 'insert_pull_N', 'cylbkt_a_stop_shift_run_mm', 'rod_buckling_ref', 'saddle_leg_buckling', 'head_deflect_mm', 'old_vs_new'):
    print(k, json.dumps(out[k], ensure_ascii=False))
print('pn_beam', out['cylbkt_pn_beam'].get('deflection_mm'), out['cylbkt_pn_beam'].get('sf'))
