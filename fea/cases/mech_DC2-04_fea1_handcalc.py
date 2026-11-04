# -*- coding: utf-8 -*-
"""DC2-04 수정 1회차 해석부 손계산 (v2.3.2).
새 하중 부품: P_DC204_PUSH_BLK(SUS304, X 8~48 Y -98~-90 Z 250~276) — 미는 볼트 M4 x2(X 14·42, 축 Y -94.1, 끝 Z 285 = 날개 A 아래 끝)
를 받아 CB5-12 x2(X 28, Z 257·269, 축 +Y)로 UPPER -Y 면에 붙는다. 바뀐 체결: CB5-12_M05_11·12(UPPER 물림 8 -> 7, 평 와셔 M5 추가).
하중 경로: HOLDER 아래 방향 Z 힘 + 면 안 비틀림(축 Y) -> 미는 볼트 끝(압축만) -> 블록 탭 -> 블록 볼트 마찰/자루 -> UPPER.
FEA 환경 없음(D-16) -> 손계산. 판정 요구서 6-1 비어 있음 -> M-09(운전 SF 3, 오조작 SF 2), SF < 1.2 만 '동작'.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SF_OP, SF_MIS = 3.0, 2.0
HAND = 100.0
W7 = 3 * 2.5 * G                 # U7 묶음 2.5 kg(보수) x 3 g = 73.6 N
FV = 4.5e3 / (0.2 * 5)           # CB5 4.5 N m -> 예압 4,500 N
MU = (0.15, 0.20)
T_op = 260.0                     # 봉제 반력 떼짐 몫(앞 회차 식, 장공 볼트 당김)
XS = (14.0, 42.0)                # 미는 볼트 X
XB = (18.0, 36.0)                # 장공 볼트 X
X_CG = 27.0                      # U7 묶음 무게중심 X(볼트 사이 가운데 가정)
XBLK, ZBLK = 28.0, (257.0, 269.0)  # 블록 볼트
Y_SCREW, Y_WING = (-94.1, (-94.0, -90.0))
SY = {'SUS304': 205.0, 'pG_SUS304': 400.0, 'set45H_y': 1100.0}


def verdict(sf, need):
    return '동작' if sf < 1.2 else ('디테일' if sf < need else '됨')


def step_bbox(path):
    pts = []
    for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", open(path, encoding='latin-1').read()):
        v = [float(x) for x in m.group(1).split(',')]
        if len(v) == 3: pts.append(v)
    return {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}


def seg_area(r, d):
    """원(반지름 r)에서 중심으로부터 d 떨어진 직선 바깥 쪽 활꼴 넓이(d<r)."""
    return r * r * math.acos(d / r) - d * math.sqrt(r * r - d * d)


def strip_in_circle(r, w):
    x = w / 2
    return 2 * (x * math.sqrt(r * r - x * x) + r * r * math.asin(x / r))


out = {'assume': {'W7_N': round(W7, 1), 'preload_N': FV, 'mu': MU, 'hand_N': HAND, 'X_CG': X_CG,
                  'screw_flat_point_dp': '2.5(JIS B 1177 M4 평끝 dp 최대) — 모델 STEP대기_ 는 끝 Ø4 그대로',
                  'block_bolt_torque': '4.5 N m(장공 볼트와 같은 값 가정, UPPER SS400 대용 D-10)'},
       'step_bbox': {'P_DC204_PUSH_BLK': step_bbox(f'{ROOT}/tools/out/mech_DC2-04/stepout/P_DC204_PUSH_BLK.step')}}
R = {}

# ---- 1) HOLDER 자유물체: 미는 볼트 하나가 받침점, 반대쪽은 장공 마찰(위 방향) ----
cases = {
    'operating_tape': (10 * (310 - 20), SF_OP, '테이프 장력 X 10 @ Z 20'),
    'misuse_hand_X_220': (HAND * (310 - 220), SF_MIS, '손 X 100 @ Z 220(M05 손 자리)'),
    'whatif_hand_X_12.5': (HAND * (310 - 12.5), SF_MIS, 'what-if 기록만: 손 X 100 @ 카세트 바닥'),
}
for name, (M, need, txt) in cases.items():
    worst = None
    for xs in XS:                                    # 받침이 되는 미는 볼트(양 방향 힘)
        other = XS[1] if xs == XS[0] else XS[0]
        # (a) 미는 볼트만으로(두 번째 볼트는 당기지 못함 -> 짝힘 반대쪽은 장공 마찰): 가장 큰 볼트 힘
        R_scr = W7 * abs(other - X_CG) / (other - xs if other > xs else xs - other) + M / abs(other - xs)
        # (b) 받침점 둘레 장공 마찰 모멘트 용량
        arms = [abs(xb - xs) for xb in XB]
        Mw = W7 * abs(X_CG - xs)                     # 자중 모멘트(불리하게 더함)
        cap = {mu: mu * (FV - T_op / 2) * sum(arms) for mu in MU}
        sf = {mu: round(cap[mu] / (M + Mw), 2) for mu in MU}
        cand = {'pivot_X': xs, 'screw_force_N': round(R_scr, 1), 'M_Nmm': round(M + Mw, 0), 'fric_arms': arms,
                'SF_pivot_mu0.15': sf[0.15], 'SF_pivot_mu0.2': sf[0.2]}
        if worst is None or cand['SF_pivot_mu0.15'] < worst['SF_pivot_mu0.15']:
            worst = cand
    worst['screw_force_N'] = round(max(W7 + M / abs(XS[1] - XS[0]), worst['screw_force_N']), 1)  # 보수: 자중 전부 + 짝힘
    worst.update({'load': txt, 'need': need, 'verdict_mu0.15': verdict(worst['SF_pivot_mu0.15'], need),
                  'verdict_mu0.2': verdict(worst['SF_pivot_mu0.2'], need), 'whatif': name.startswith('whatif')})
    R['holder_' + name] = worst

F = R['holder_misuse_hand_X_220']['screw_force_N']       # 판정 하중(오조작)
F_op = R['holder_operating_tape']['screw_force_N']

# ---- 2) 미는 볼트 M4 압축·끝 면압·편심 굽힘 ----
As4, d3 = 8.78, 3.141
r_dp = 2.5 / 2
d_off = Y_WING[0] - Y_SCREW                              # 축에서 날개 면까지 0.1
A_dp = seg_area(r_dp, d_off)                             # 평끝 Ø2.5 중 날개 위 넓이
A_full = seg_area(2.0, d_off)                            # 모델 끝 Ø4
# 맞닿음 중심 편심(활꼴 중심): 근사 4 r^3 sin^3 / (3(2θ - sin2θ)), θ = acos(d/r)
th = math.acos(d_off / r_dp)
e = 4 * r_dp ** 3 * math.sin(th) ** 3 / (3 * r_dp * r_dp * (2 * th - math.sin(2 * th)))
sig_c = F / As4
sig_b = F * e / (math.pi * d3 ** 3 / 32)
R['setscrew_M4'] = {'F_N': F, 'sigma_axial_MPa': round(sig_c, 1), 'ecc_mm': round(e, 2), 'sigma_bend_MPa': round(sig_b, 1),
                    'SF_yield': round(SY['set45H_y'] / (sig_c + sig_b), 2), 'need': SF_MIS,
                    'free_len_mm': '너트 위 5.8(h 0) ~ 1.8(h -4) — 세장비 무시',
                    'A_tip_dp2.5_mm2': round(A_dp, 2), 'A_tip_model_O4_mm2': round(A_full, 2),
                    'p_tip_MPa': round(F / A_dp, 0), 'SF_pG_wing_SUS304': round(SY['pG_SUS304'] * A_dp / F, 2),
                    'SF_yield_wing': round(SY['SUS304'] * A_dp / F, 2),
                    'p_tip_operating_MPa': round(F_op / A_dp, 0), 'SF_pG_operating': round(SY['pG_SUS304'] * A_dp / F_op, 2)}
R['setscrew_M4']['verdict'] = verdict(min(R['setscrew_M4']['SF_yield'], R['setscrew_M4']['SF_pG_wing_SUS304']), SF_MIS)
R['setscrew_M4']['note'] = ('축 Y -94.1이 날개(Y -94~-90) 바깥 끝에 있어 평끝 Ø2.5 중 1.15 mm 폭만 닿음. 면압 판정은 앞 회차와 같은 '
                            'p_G(SUS304 400) 기준. 항복 205 기준이면 SF %.2f — 국부 눌림(수 µm) 가능, 미는 볼트 축을 날개 가운데(Y -92) '
                            '쪽으로 옮기면 맞닿음 전폭' % R['setscrew_M4']['SF_yield_wing'])

# ---- 3) 블록 M4 탭(SUS304, 물림 블록 안 Z 260~276 = 16, h -4 최악 6+) ----
le_min = 276 - 266  # h +6: 볼트 아래 끝 266 -> 블록 안 10
A_th = math.pi * 3.242 * le_min * 0.75                   # 암나사 전단 넓이(D1 3.242 근사)
R['block_tap_M4'] = {'le_min_mm': le_min, 'A_shear_mm2': round(A_th, 1), 'tau_MPa': round(F / A_th, 1),
                     'SF': round(0.6 * SY['SUS304'] / (F / A_th), 1), 'need': SF_MIS}
R['block_tap_M4']['verdict'] = verdict(R['block_tap_M4']['SF'], SF_MIS)

# ---- 4) 블록 -> UPPER: CB5-12 x2 (X 28, Z 257·269, 간격 12), 면 안 힘 Z F + 면 안 비틀림 F x |14-28| ----
for xs in (XS[0],):
    Mz = F * abs(xs - XBLK)                                 # 축 Y 비틀림(대칭이라 하나만)
    r_b = (ZBLK[1] - ZBLK[0]) / 2
    Fx_each = Mz / (2 * r_b)                                 # 비틀림 -> 볼트마다 X 전단
    Fz_each = F / 2
    Fres = math.hypot(Fx_each, Fz_each)
    # 면 밖 당김: 미는 볼트 축 Y -94.1, 붙임면 Y -90 -> 팔 4.1, 블록 밑 Z 250 받침 -> 볼트 줄 거리 7·19
    My = F * 4.1
    Tmax = My * (ZBLK[1] - 250) / ((ZBLK[0] - 250) ** 2 + (ZBLK[1] - 250) ** 2)
    sf = {mu: round(mu * (FV - Tmax) / Fres, 2) for mu in MU}
    R['block_bolts_CB5-12_slip'] = {'Mz_Nmm': round(Mz, 0), 'Fx_each_N': round(Fx_each, 1), 'Fz_each_N': round(Fz_each, 1),
                                    'F_res_each_N': round(Fres, 1), 'T_ext_max_N': round(Tmax, 1),
                                    'SF_slip_mu0.15': sf[0.15], 'SF_slip_mu0.2': sf[0.2], 'need': SF_MIS,
                                    'verdict_mu0.15': verdict(sf[0.15], SF_MIS), 'verdict_mu0.2': verdict(sf[0.2], SF_MIS)}
    # 미끄러진 뒤: 자루 Ø5 가 Ø5.5 구멍 틈 0.25 만큼 돌고 자루 받침 -> 높이 바뀜
    rot = 0.25 / r_b
    R['block_bolts_CB5-12_slip']['after_slip'] = {
        'rot_rad': round(rot, 4), 'tip_dz_mm': round(rot * abs(xs - XBLK), 2),
        'shank_tau_MPa': round(Fres / (math.pi / 4 * 5 ** 2), 1),
        'note': '미끄러지면 블록이 축 Y로 돌아 자루가 구멍 벽에 닿을 때(틈 0.25) 멈춤 — 미는 볼트 끝 높이가 약 0.58 mm 바뀐 채 남음. 자루 전단은 낮음(부러짐 아님)'}
    R['block_bolts_CB5-12_bolt'] = calc(d=5, le=9.4, load=round(Fres + Tmax, 1), torque=4.5, bolt='12.9', base='SS400',
                                        dw=8.5, dh=5.5, sf_min=SF_MIS)

# ---- 5) 블록 몸(SUS304 40x8x26): 탭 뿌리 굽힘 — 미는 볼트 힘이 블록 밑 볼트 줄까지 X 14 팔 ----
#      단면: 블록 Y 8 x Z 26 판을 X 방향 외팔(볼트 X 28 -> 탭 X 14, 팔 14), 굽힘 축 Y: b=8? -> 판 두께 방향은 Z 26
R['block_body'] = beam(t=26.0, b=8.0, length=14.0, load=F, e=193000.0, sy=SY['SUS304'], end='cantilever', sf_min=SF_MIS)

# ---- 6) 바뀐 체결 CB5-12_M05_11·12: UPPER 물림 8 -> 7, 와셔 M5(Ø10) ----
# 앞 회차 가장 불리한 합 799 N(장공 마찰 몫 + 당김). 미는 볼트가 Z 몫을 받아도 보수로 그대로 씀.
A_wsh = math.pi * 5 ** 2 - strip_in_circle(5.0, 5.5)     # 와셔가 장공 위 판에 닿는 넓이
dh_eq = math.sqrt(10 ** 2 - 4 * A_wsh / math.pi)
R['slot_bolts_CB5-12_M05'] = calc(d=5, le=7, load=799.0, torque=4.5, bolt='12.9', base='SS400', dw=10.0, dh=round(dh_eq, 2), sf_min=SF_MIS)
R['slot_washer'] = {'A_washer_on_plate_mm2': round(A_wsh, 1), 'p_MPa': round(FV / A_wsh, 0),
                    'SF_pG_SUS304': round(SY['pG_SUS304'] * A_wsh / FV, 2), 'before_no_washer_SF': 1.20,
                    'washer_t1_bend': '와셔 t1이 장공 폭 5.5를 건너 받침 — 굽힘은 머리 좌면 Ø8.5와 장공 사이 1.5 띠라 낮음(기록)'}

out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-04_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    if isinstance(v, dict):
        print(k, {kk: vv for kk, vv in v.items() if not isinstance(vv, (dict, list)) or kk in ('worst', 'ok')})
