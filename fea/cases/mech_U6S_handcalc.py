# -*- coding: utf-8 -*-
"""U6S 해석부 손계산(2026-11-11, v2.9.0). FEA 못 함 — 환경 없음(D-16).
새 하중 부품: P_M06_PCYL_BRKT(SUS304 t3), P_M06_SHOE(고침, 윗날개 탭), P_M06_SLIDE_COLLAR_1·2(SUS304).
누름 힘 띠·잡음·회전은 모델링부 u6s_calc_model.json 값을 다시 읽어 쓰고, 자국은 Winkler 강체 판 압력 기울기를 더한다.
실행: python -X utf8 -B fea/cases/mech_U6S_handcalc.py
"""
import json, math, re, sys, os
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
M = json.load(open(ROOT + '/tools/out/mech_U6S/model/u6s_calc_model.json', encoding='utf-8'))
R = {'_설명': 'U6S 해석부 손계산, 입력 u6s_calc_model.json(모델링부) + STEP bbox', 'step_bbox': {}}

# ---------- 0. STEP bbox(CARTESIAN_POINT 모두) ----------
for n in ['P_M06_PCYL_BRKT', 'P_M06_SHOE', 'P_M06_SLIDE_COLLAR']:
    txt = open(ROOT + f'/tools/out/mech_U6S/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(float(v) for v in m.split(',')) for m in re.findall(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt)]
    pts = [p for p in pts if len(p) == 3 and p != (0.0, 0.0, 0.0)]
    if pts:
        R['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(p[i] for p in pts), 2) for i in range(3)],
                             'max': [round(max(p[i] for p in pts), 2) for i in range(3)]}

SY = {'SUS304': 205.0}
SF_OP, SF_MIS = 3.0, 2.0          # 요구서 6-1(M-09 기본값)
HAND = 100.0                      # 오조작 손 힘(D-79)
A_head, A_rod = M['A_head_mm2'], M['A_rod_mm2']
P_sup = 0.5                       # 요구서 2-4 운전 압력
F_lift = A_rod * P_sup            # 32.99 N
F_push_fail = A_head * P_sup      # 레귤레이터 고장(우회) 39.3 N
F_hi, F_lo, F_abs = M['F_hi_N'], M['F_lo_N'], M['F_abs_max_N']
W = M['W_moving_N']

# ---------- 1. 자국: Winkler 강체 판 + 끌림 모멘트 압력 기울기 ----------
A_c = F_hi / (M['p_hi_kPa'] * 1e-3)        # 유효 닿는 넓이 mm2 (1,507)
L = 90.0                                    # 끌림 방향(Y) 바닥 길이
b = A_c / L
h = 20.5                                    # 바닥 Z ~12 -> 칼라 Z 32.5
P_ALLOW = 30.0                              # kPa, D-165 미끄럼 임시
mark = {}
for mu in (0.2, 0.3, 0.4):
    e = mu * h
    k = 1 + 6 * e / L
    for tag, F in (('F_hi', F_hi), ('F_nom', M['F_nom_N']), ('regmax', F_abs)):
        p_avg = F / A_c * 1e3
        p_max = p_avg * k
        mark[f'mu{mu}_{tag}'] = {'e_mm': round(e, 2), 'peak_factor': round(k, 3), 'p_avg_kPa': round(p_avg, 2),
                                 'p_max_kPa': round(p_max, 2), 'SF_avg': round(P_ALLOW / p_avg, 2), 'SF_peak': round(P_ALLOW / p_max, 2)}
R['mark_winkler_tilt'] = mark
# 기준 2 맞추려면: 길이 L' 또는 폭 b'
need = P_ALLOW / 2.0 * 1e-3                 # N/mm2
k4 = 1 + 6 * 0.4 * h / L
b_need = F_hi * k4 / (need * L)
aa = need * b / F_hi                        # (1/L)(1+6eh/L) <= aa
e4 = 0.4 * h
L_need = (1 + math.sqrt(1 + 4 * aa * 6 * e4)) / (2 * aa)
mu_need = None
for i in range(400, 0, -1):
    mu = i / 1000
    if F_hi / A_c * 1e3 * (1 + 6 * mu * h / L) <= P_ALLOW / 2:
        mu_need = mu
        break
R['mark_fix'] = {'b_eff_now_mm': round(b, 1), 'b_eff_need_mm(L 90, mu 0.4)': round(b_need, 1),
                 'L_need_mm(b now, mu 0.4)': round(L_need, 1), 'mu_need(형상 그대로)': mu_need,
                 'h_need_mm(형상 그대로, mu 0.4)': round(((P_ALLOW / 2) / (F_hi / A_c * 1e3) - 1) * L / 6 / 0.4, 2)}

# ---------- 2. 잡음·회전(모델링부 값 재확인) ----------
R['grip'] = {'F_lo_N': F_lo, 'need_N': M['F_need_design_N'], 'ratio': round(F_lo / M['F_need_design_N'], 3), 'criterion': 1.2}
R['rotation'] = M['rotation']
R['rotation_min_SF_lifted'] = min(s['SF_with_shoe_lifted'] for s in M['rotation'])
R['rotation_min_SF_if_pressed'] = min(s['SF_if_pressed_Flo_mu0.3'] for s in M['rotation'])

# ---------- 3. 브래킷 P_M06_PCYL_BRKT (SUS304 t3, 외팔 13, 유효 폭 28) ----------
t, Lb, bb = 3.0, 13.0, 28.0
Kb = 1.3   # 굽힘 R 모서리 계수(보수)
br = {}
for tag, F, sf in (('운전_들기_0.5MPa', F_lift + 3 * W, SF_OP), ('운전_누름_멈춤_0.18MPa', A_head * 0.18 + 3 * W, SF_OP),
                   ('오조작_레귤레이터우회_0.5MPa', F_push_fail + 3 * W, SF_MIS), ('오조작_손100N', HAND + 3 * W, SF_MIS)):
    s = 6 * F * Lb / (bb * t * t) * Kb
    br[tag] = {'F_N': round(F, 2), 'sigma_MPa': round(s, 1), 'SF': round(SY['SUS304'] / s, 2), 'criterion': sf}
R['PCYL_BRKT_plate'] = br
# t2로 줄였을 때(과사양 note)
s2 = 6 * (HAND + 3 * W) * Lb / (bb * 4.0) * Kb
R['PCYL_BRKT_t2_note'] = {'sigma_MPa': round(s2, 1), 'SF': round(205 / s2, 2)}
# 브래킷 볼트 CB5-12 x2 -> MBIS5 인서트(PET-CF 다리). 지렛대: 위로 힘 -> 받침 벽 윗끝 Z94, 볼트 Z86 팔 8; 아래로 -> 받침 Z74.3 팔 11.7
Mrot = HAND * (-8 - (-22))
T_up = Mrot / (94 - 86) / 2
T_dn = Mrot / (86 - 74.3) / 2
Tb = max(T_up, T_dn) + HAND / 2 * 0  # 전단 50 N/볼트는 마찰(인서트 예압 ≤ 1000 N x 0.15 = 150 N)로
R['PCYL_BRKT_bolt'] = {'T_up_per_bolt_N': round(T_up, 1), 'T_dn_per_bolt_N': round(T_dn, 1), 'shear_per_bolt_N': HAND / 2,
                       'insert_pullout_N(임시, M06 해석과 같음)': 1000.0, 'SF_pullout': round(1000.0 / max(T_up, T_dn), 1),
                       'calc_PETCF_thread': calc(d=5, le=8, load=round(max(T_up, T_dn), 1), torque=0, bolt='12.9', base='PET-CF', sf_min=SF_MIS)}

# ---------- 4. 슈 윗날개 탭(SUS304 t2, 벽 X-19 -> 로드 X-8 팔 11) ----------
tt, Lt = 2.0, 11.0
b_tab = 7.0 + 2 * Lt   # 너트 맞변 7 + 45° 퍼짐
tab = {}
for tag, F, sf in (('운전_들기_0.5MPa', F_lift, SF_OP), ('운전_누름_F_abs', F_abs, SF_OP), ('오조작_레귤레이터우회', F_push_fail, SF_MIS),
                   ('오조작_손100N', HAND, SF_MIS)):
    s = 6 * F * Lt / (b_tab * tt * tt) * Kb
    tab[tag] = {'F_N': round(F, 2), 'b_eff_mm': b_tab, 'sigma_MPa': round(s, 1), 'SF': round(205 / s, 2), 'criterion': sf}
R['SHOE_tab'] = tab
R['SHOE_tab_beam_check'] = beam(t=2.0, b=b_tab, length=Lt, load=HAND, e=193000, sy=205, sf_min=SF_MIS)
# 슈 바닥 판: 압력 22 kPa 수준 — 응력 무시할 크기
# ---------- 5. 칼라 P_M06_SLIDE_COLLAR (축 Ø7/Ø5.5 x 2.1, 턱 Ø12 x 1.5) ----------
A_sh = math.pi / 4 * (7.0 ** 2 - 5.5 ** 2)
col = {'A_shaft_annulus_mm2': round(A_sh, 2)}
for tq in (1.0, 1.2, 2.0, 3.0, 4.5):
    Fv = tq * 1000 / (0.2 * 5)
    s = Fv / A_sh
    col[f'preload_{tq}Nm'] = {'Fv_N': round(Fv), 'sigma_MPa': round(s, 1), 'SF': round(205 / s, 2)}
# 장공 끝 멈춤(-5.0): 누름 0.18 MPa 14.1 N + 손 100 N 오조작 -> 칼라 2개
for tag, F in (('운전_아래끝_0.18MPa', A_head * 0.18 + W), ('오조작_손100N', HAND)):
    q = F / 2
    col[tag] = {'per_collar_N': round(q, 1), 'bearing_shoe_t2_MPa': round(q / (7.0 * 2.0), 2),
                'shear_shaft_MPa': round(q / A_sh, 2)}
# 옆힘(끌림) mu0.4 F_hi
Fd = 0.4 * F_hi
col['drag_side'] = {'F_drag_N': round(Fd, 2), 'per_collar_N': round(Fd / 2, 2), 'bearing_MPa': round(Fd / 2 / 14.0, 2)}
# 턱 Ø12 x 1.5 굽힘(볼트 머리 Ø8.5 받침 -> 축 Ø7 링 판, 머리 지름이 축보다 커서 굽힘 팔 거의 0)
col['flange_note'] = '볼트 머리 Ø8.5가 축 Ø7보다 커서 예압은 턱을 거치지 않고 바로 축으로 감 -> 턱 굽힘 없음'
R['SLIDE_COLLAR'] = col

# ---------- 6. 칼라 볼트(옮긴 CB5-12_M06_3·_4) ----------
R['COLLAR_bolt'] = {'load_per_bolt_N(손100N 전단)': HAND / 2, 'insert_pullout_N(임시)': 1000.0,
                    'note': '예압으로 칼라 고정, 외력은 전단 50 N뿐(인서트 예압 1,000 N x mu 0.15 = 150 N 마찰 > 50)',
                    'SF_slip': round(1000 * 0.15 / (HAND / 2), 2)}

os.makedirs(ROOT + '/fea/results', exist_ok=True)
json.dump(R, open(ROOT + '/fea/results/mech_U6S_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bbox', json.dumps(R['step_bbox'], ensure_ascii=False))
for k in ('mu0.2_F_hi', 'mu0.3_F_hi', 'mu0.4_F_hi', 'mu0.3_F_nom', 'mu0.4_regmax'):
    print(k, mark[k])
print('fix', R['mark_fix'])
print('grip', R['grip'], 'rotSF', R['rotation_min_SF_lifted'], R['rotation_min_SF_if_pressed'])
print('brkt', {k: v['SF'] for k, v in br.items()}, 't2', R['PCYL_BRKT_t2_note'])
print('brkt bolt', R['PCYL_BRKT_bolt']['SF_pullout'], R['PCYL_BRKT_bolt']['calc_PETCF_thread']['sf_operating'])
print('tab', {k: v['SF'] for k, v in tab.items()}, R['SHOE_tab_beam_check'].get('needs_fea'))
print('collar', {k: v for k, v in col.items() if k.startswith('preload')})
print('collar load', col['오조작_손100N'], col['drag_side'])
