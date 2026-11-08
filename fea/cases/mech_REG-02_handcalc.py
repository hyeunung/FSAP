# -*- coding: utf-8 -*-
"""REG-02 해석부 손계산 (v2.6.6) — U6·U7 높이 조정 하나로 묶기(C-34).
새 하중 부품: P_REG02_HGT_PLATE(SUS304 t5, X -80~44 · Y -99~-93 · Z 157~330, BASE 쪽 1 mm 패드).
쌓임(Y): UPPER -Y 면(Y -90) | BASE 붙임면 t3 / HOLDER 날개 A t4 | (패드 1) 판 t5 | 볼트 머리(1·2 직접, 3·4 와셔 M5 t1).
볼트 CB5-16_REG02_1~4: X -70·-32 @ Z 180(BASE 장공 Z 174~184), X 18·36 @ Z 310(날개 장공 Z 304~314). UPPER 물림 7 / 6.
압입 스터드 FH4-M4 x4 + 너트: 높이 조정(장공 볼트 푼 때) 동안 BASE·HOLDER를 판에 붙들고, 판 + 두 묶음이 미는 볼트 M4 x2에 얹힘.
FEA 환경 없음(D-16) -> 손계산(엔진 handcalc import). 판정 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), SF < 1.2만 '동작'.
하중·임시값은 DC2-04(mech_DC2-04_handcalc.py, _fea1_handcalc.py)와 같다: U6 1.0 kg·U7 2.5 kg x3 g, 손 100 N, CJ2B16 막힘 100.5 N,
CB5 4.5 N·m -> 예압 4,500 N, mu 0.15(판정)/0.2(참고), UPPER 모재 SS400 대용(D-10).
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SF_OP, SF_MIS = 3.0, 2.0
HAND = 100.0
F16 = math.pi / 4 * 16 ** 2 * 0.5
FV = 4.5e3 / (0.2 * 5)
MU = (0.15, 0.20)
M6, M7, MPL = 1.0, 2.5, 0.28885 + 4 * (0.0015 + 0.00075)   # 판 288.85 g + 스터드·너트
BOLTS = [(-70.0, 180.0), (-32.0, 180.0), (18.0, 310.0), (36.0, 310.0)]
X6, X7, XPL = -51.0, 27.0, -18.0          # 무게중심 X: U6(J 원점), U7(J 원점), 판 bbox 가운데
SY_SUS, PG_SUS = 205.0, 400.0


def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '됨(과사양 note)'
    return '됨'


def step_info(path):
    txt = open(path, encoding='latin-1').read()
    pts = []
    for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt):
        v = [float(x) for x in m.group(1).split(',')]
        if len(v) == 3: pts.append(v)
    return {'n_pts': len(pts), 'n_solid': txt.count('MANIFOLD_SOLID_BREP'),
            'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}


def head_area_slot(dw, w=5.5):
    r, x = dw / 2, w / 2
    strip = 2 * (x * math.sqrt(r * r - x * x) + r * r * math.asin(x / r))
    return math.pi * r * r - strip


out = {'assume': {'preload_N': FV, 'mu': MU, 'hand_N': HAND, 'F16_N': round(F16, 1), 'g': 3,
                  'mass_kg': {'U6': M6, 'U7': M7, 'plate+studs+nuts': round(MPL, 3)},
                  'cg_X': {'U6': X6, 'U7': X7, 'plate': XPL},
                  'UPPER_base': 'SS400 대용(867 주물, D-10)', 'pG_SUS304': PG_SUS,
                  'model_choice': 'fea/models.json에 판 행 없음 -> 실제 조립 경계조건(4볼트 조임 + 장공, 마찰만)으로 새로 정함'},
       'step': step_info(f'{ROOT}/tools/out/mech_REG-02/stepout/P_REG02_HGT_PLATE.step')}
R = {}

# ---------- 1) 판 + 두 묶음 4볼트 무리(조여 있을 때) — 탄성 볼트 무리법, 맞닿는 면은 UPPER 면 하나만 셈(보수) ----------
xc = sum(b[0] for b in BOLTS) / 4
zc = sum(b[1] for b in BOLTS) / 4
J = sum((b[0] - xc) ** 2 + (b[1] - zc) ** 2 for b in BOLTS)
Wt = 3 * G * (M6 + M7 + MPL)
x_cg = (M6 * X6 + M7 * X7 + MPL * XPL) / (M6 + M7 + MPL)
R['group'] = {'centroid_XZ': [xc, zc], 'J_mm2': round(J, 0), 'W_3g_N': round(Wt, 1), 'cg_X': round(x_cg, 1)}


def group_case(tag, Fx, x_at, z_at, need, tension=0.0, note='', whatif=False):
    """면 안(XZ) 힘 Fx(+X) @ (x_at, z_at) + 자중 -Z @ x_cg. 볼트마다 직접 + 비틀림 몫 벡터합."""
    Fz = -Wt
    M = Fx * (zc - z_at) * (-1) + Fz * (x_cg - xc)    # 축 Y 모멘트(부호 일관, 크기만 씀)
    M = -Fx * (z_at - zc) + Fz * (x_cg - xc)
    worst = 0.0
    for bx, bz in BOLTS:
        dx, dz = bx - xc, bz - zc
        fx = Fx / 4 + (-M * dz) / J
        fz = Fz / 4 + (M * dx) / J
        worst = max(worst, math.hypot(fx, fz))
    d = {'Fx_N': Fx, 'at_XZ': [x_at, z_at], 'M_Nmm': round(abs(M), 0), 'F_bolt_max_N': round(worst, 1),
         'tension_ext_N': tension, 'need': need, 'load': note, 'whatif': whatif}
    for mu in MU:
        sf = mu * (FV - tension) / worst
        d[f'SF_slip_mu{mu}'] = round(sf, 2)
        d[f'verdict_mu{mu}'] = verdict(sf, need)
    R['group_' + tag] = d


group_case('op_U6_drag', 6.0, -51.0, 12.5, SF_OP, note='운전 X 6 N @ 슈 끝 Z 12.5(DC2-04 운전 값) + 자중 3 g')
group_case('op_U7_tape', 10.0, 27.0, 20.0, SF_OP, tension=260.0, note='테이프 장력 X 10 @ Z 20 + 자중 3 g, 떼짐 T 260 / 2(DC2-04 식)')
group_case('mis_U6_hand_X_shoe', HAND, -51.0, 12.5, SF_MIS, note='손 X 100 @ 슈 끝 Z 12.5 (DC2-04 BASE 홀로 SF 1.47 이던 경우)')
group_case('mis_U6_blocked_cyl', F16, -51.0, 136.0, SF_MIS, tension=101.9, note='CJ2B16 막힘 100.5 @ Z 136 + 자중, 당김 101.9(DC2-04)')
group_case('mis_U7_hand_X_220', HAND, 27.0, 220.0, SF_MIS, tension=130.0, note='손 X 100 @ Z 220(M05 손 자리) + 자중, 떼짐 T/2')
group_case('whatif_U7_hand_X_bottom', HAND, 27.0, 12.5, SF_MIS, tension=130.0, note='what-if 기록만: 손 X 100 @ 카세트 바닥 Z 12.5', whatif=True)

# ---------- 2) 묶음 하나만 미끄러지는 꼴(판은 다른 볼트 2개에 남음): 그 묶음은 UPPER 면 + 판(패드/날개) 면 두 면에서 미끄러져야 함 ----------
dc = json.load(open(f'{ROOT}/fea/results/mech_DC2-04_handcalc.json', encoding='utf-8'))['results']
dc1 = json.load(open(f'{ROOT}/fea/results/mech_DC2-04_fea1_handcalc.json', encoding='utf-8'))['results']
local = {}
for k in ('U6_BASE_slot_operating', 'U6_BASE_slot_misuse_blocked_cyl', 'U6_BASE_slot_misuse_hand_X_shoe', 'U6_BASE_slot_misuse_hand_Z',
          'U7_HOLDER_slot_operating', 'U7_HOLDER_slot_misuse_feed_blocked', 'U7_HOLDER_slot_misuse_hand_X_220', 'U7_HOLDER_slot_misuse_hand_Y_220'):
    v = dc[k]
    need = v['need']
    one = v['SF_slip_mu0.15']
    local[k] = {'DC2-04_one_face_SF_mu0.15': one, 'two_face_SF_mu0.15': round(2 * one, 2), 'need': need,
                'verdict_two_face': verdict(2 * one, need), 'verdict_if_pad_gap(one_face)': verdict(one, need)}
pv = dc1['holder_misuse_hand_X_220']
local['U7_pivot_on_push_screw_hand_X_220(DC2-04 fea1)'] = {'DC2-04_one_face_SF_mu0.15': pv['SF_pivot_mu0.15'],
    'two_face_SF_mu0.15': round(2 * pv['SF_pivot_mu0.15'], 2), 'need': SF_MIS, 'verdict_two_face': verdict(2 * pv['SF_pivot_mu0.15'], SF_MIS),
    'verdict_if_pad_gap(one_face)': verdict(pv['SF_pivot_mu0.15'], SF_MIS)}
R['local_one_bundle_slip'] = local
R['local_one_bundle_slip']['_note'] = ('BASE(또는 날개)가 판과 UPPER 사이에 끼어 같은 볼트 예압으로 두 면이 눌림. 판이 다른 묶음 볼트 2개에 남아 있으면 '
                                      '그 묶음은 두 면 모두 미끄러져야 함 -> 용량 2배. 패드 1 mm 가공 오차로 판이 그 묶음에 안 닿으면 한 면(DC2-04 값)')

# ---------- 3) 볼트 CB5-16_REG02: UPPER 물림 7(1·2) / 6(3·4) ----------
worst_T = 799.0   # DC2-04 fea1 장공 볼트 가장 불리한 합(보수 그대로)
A_wsh = math.pi * 5 ** 2 - (2 * (2.75 * math.sqrt(25 - 2.75 ** 2) + 25 * math.asin(2.75 / 5)))
R['bolt_1_2_le7_no_washer'] = calc(d=5, le=7, load=worst_T, torque=4.5, bolt='12.9', base='SS400', dw=8.5,
                                   dh=round(math.sqrt(8.5 ** 2 - 4 * head_area_slot(8.5) / math.pi), 2), sf_min=SF_MIS)
R['bolt_3_4_le6_washer'] = calc(d=5, le=6, load=worst_T, torque=4.5, bolt='12.9', base='SS400', dw=10.0,
                                dh=round(math.sqrt(100 - 4 * A_wsh / math.pi), 2), sf_min=SF_MIS)
R['bolt_whatif_CB5-20_le11'] = calc(d=5, le=11, load=worst_T, torque=4.5, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS)
R['bolt_whatif_le6_torque3.5'] = calc(d=5, le=6, load=worst_T, torque=3.5, bolt='12.9', base='SS400', dw=10.0,
                                      dh=round(math.sqrt(100 - 4 * A_wsh / math.pi), 2), sf_min=SF_MIS)

# ---------- 4) 머리 좌면(SUS304 판 장공 위) ----------
A1 = head_area_slot(8.5)
R['head_bearing'] = {'bolt_1_2_no_washer': {'A_mm2': round(A1, 1), 'p_MPa': round(FV / A1, 0), 'SF_pG': round(PG_SUS * A1 / FV, 2),
                                            'verdict': verdict(PG_SUS * A1 / FV, 1.2) if PG_SUS * A1 / FV >= 1.2 else '디테일(기준 1.2 근처)'},
                     'bolt_3_4_washer': {'A_mm2': round(A_wsh, 1), 'p_MPa': round(FV / A_wsh, 0), 'SF_pG': round(PG_SUS * A_wsh / FV, 2)}}

# ---------- 5) 판 몸 ----------
# (a) 조여 있을 때: 판은 볼트 4개 머리 사이에 눌려 면 안 하중은 마찰로 각 묶음이 UPPER로 바로 보냄 -> 판 몸 하중은 짐 넘김 몫뿐.
#     보수로 U6 손 X 100 전부가 판을 거쳐 U7 쪽 볼트로 간다고 보면: 판 가운데 띠(BASE 위 Z 195 ~ 날개 아래 Z 287, 폭 124) 면 안 굽힘.
b_pl, t_pl = 124.0, 5.0
Lmid = 287.0 - 195.0
M_in = HAND * (195.0 - 12.5) * 0.5 + HAND * Lmid * 0.5
Wz = t_pl * b_pl ** 2 / 6
R['plate_inplane_mid'] = {'M_Nmm': round(M_in, 0), 'W_mm3': round(Wz, 0), 'sigma_MPa': round(M_in / Wz, 2),
                          'SF': round(SY_SUS / (M_in / Wz), 0), 'verdict': verdict(SY_SUS / (M_in / Wz), SF_MIS),
                          'note': '보수: U6 손 X 100 의 짝힘 절반 + 전단 x 가운데 띠 길이 — 면 안 굽힘(폭 124 방향)'}
# (b) 높이 조정 중(볼트 풀림, 1 g 정적): U6 묶음 무게가 스터드 1·2 -> 판 -> 스터드 3·4 -> HOLDER -> 미는 볼트.
#     면 밖: U6 무게중심 Y 오프셋(BASE 면 Y -90 -> 슈·실린더 쪽 약 -150, 팔 60 가정) 모멘트를 판이 판 두께 방향으로 받음.
W6_1g = M6 * G
M_out = W6_1g * 60.0
R['plate_adjust_out_of_plane'] = beam(t=t_pl, b=b_pl, length=Lmid, load=round(M_out / Lmid * 2, 2), e=193000.0, sy=SY_SUS,
                                      end='cantilever', sf_min=SF_OP)
R['plate_adjust_out_of_plane']['_note'] = 'U6 1 kg @ 팔 60 의 짝힘을 가운데 띠 끝 힘으로 바꿔 외팔(보수, 판 폭 124 전부)'
R['plate_slot_edge'] = {'BASE_side_slot_top_to_edge': '판 아래 끝 Z 157, 장공 Z 171.25~186.75 -> 아래 살 14.25, 위로 판 계속',
                        'HOLDER_side': '장공 Z 301.25~316.75, 판 위 끝 Z 330 -> 살 13.25, 판 아래 끝 Z 287 -> 14.25', 'min_rib_vs_2.5': '됨'}

# ---------- 6) 스터드 FH4-M4 · 판 스터드 구멍(조정 중) ----------
As4 = 8.78
W_all_1g = (M6 + M7 + MPL) * G
R['studs_adjust'] = {'U6_side_2_studs_shear_N_each': round(W6_1g / 2, 1), 'tau_MPa': round(W6_1g / 2 / As4, 2),
                     'bearing_plate_t5_MPa': round(W6_1g / 2 / (4.0 * 5.0), 2),
                     'U7_side_2_studs_N_each(U6 몫 넘김)': round(W6_1g / 2, 1),
                     'push_screws_total_1g_N': round(W_all_1g, 1),
                     'push_screw_vs_DC2-04_fea1_F_N': dc1['setscrew_M4']['F_N'],
                     'verdict': '됨(과사양 note — 하중 수 N)',
                     'note': '스터드 압입 밀림 저항은 PEM 카탈로그 값(SUS 판 t3 최소 두께·구멍 Ø) 확인 필요 -> D-142. 하중 5 N 수준이라 결과에 영향 없음'}
R['studs_operating'] = {'note': '조여 있을 때 스터드 몫 거의 0(장공 볼트 마찰이 받음). 스터드 구멍 Ø4.5 - 스터드 Ø4 틈 0.25 -> 조여 있을 때 판·BASE 상대 미끄럼이 0.25 넘으면 스터드가 받음(전단 단면 2 x 8.78)',
                        'after_slip_cap_N': round(2 * As4 * 0.6 * 500, 0), 'stud_material': '400계 스테인리스 가정 인장 500 대용'}

out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_REG-02_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('step', out['step'])
for k, v in R.items():
    if k.startswith('group_'):
        print(k, v['F_bolt_max_N'], v['SF_slip_mu0.15'], v['verdict_mu0.15'], 'whatif' if v['whatif'] else '')
for k in ('bolt_1_2_le7_no_washer', 'bolt_3_4_le6_washer', 'bolt_whatif_CB5-20_le11', 'bolt_whatif_le6_torque3.5'):
    v = R[k]; print(k, v['worst'], v['sf_tightening'], v['ok'])
print('head', R['head_bearing'])
print('plate_inplane', R['plate_inplane_mid']['sigma_MPa'], R['plate_inplane_mid']['SF'])
print('plate_adjust', R['plate_adjust_out_of_plane']['stress_MPa'], R['plate_adjust_out_of_plane']['sf'], R['plate_adjust_out_of_plane']['deflection_mm'])
for k, v in R['local_one_bundle_slip'].items():
    if isinstance(v, dict): print(k, v['DC2-04_one_face_SF_mu0.15'], v['two_face_SF_mu0.15'], v['verdict_two_face'], v['verdict_if_pad_gap(one_face)'])
