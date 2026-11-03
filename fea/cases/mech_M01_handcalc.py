# -*- coding: utf-8 -*-
"""M01 해석부 손계산 — P_M01_HANGER(SUS304 t8 L 판금) + P_M01_FOOT(S45C). FEA 환경 없음(D-16).
형상은 STEP(tools/out/mech_M01/stepout/*.step) 꼭짓점 bbox로 확인하고 모델링 보고서 2절 치수를 쓴다.
  매달기: 선반 X 0~400 · Y -90~120 · Z 560~568(t8), 세운 판 Y 112~120 · Z 560~650, 굽힘 R8(안쪽).
          선반 볼트 CB5-16 x6 (X 40/200/360, Y +-50) -> 헤드 윗면 탭, 세운 판 볼트 CB5-16 x4 (X 50/150/250/350, Z 620) -> U1_BEAM 앞면 Y 120.
  노루발: v1 N01과 같은 치수(발바닥 t2 Z 12~14, 대 O6 (-5,-3) Z 14~80, 노즈 밑면 Z 46).
하중(임시값):
  윗헤드 60 kg (D-107 M00 손계산용; D-108은 50 kg — 큰 쪽) x 3 g = 1,766 N (지시서 '자중 x3 g')
  봉제 끌림: 운전 30 N(노루발 마찰 상한 0.6 x 50 N), 오조작 100 N(D-79 전부) — 바늘점 Z 12에서 수평(Y가 가장 불리)
  노루발: 누름 50 N(운전)/150 N(오조작), v1 N01과 같은 모델
판정: M-09 운전 SF 3, 오조작 SF 2 (요구서 6-1 기본값). SUS304 항복 205, E 193 GPa / S45C 345, 205 GPa.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
out = {'step_bbox': {}}

# 0) STEP bbox
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
for n in ('P_M01_HANGER', 'P_M01_FOOT'):
    t = open(f'{ROOT}/tools/out/mech_M01/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = [[round(min(c), 2), round(max(c), 2)] for c in zip(*pts)]

# ---------------- 매달기 ----------------
E_S, RP_S = 193000.0, 205.0
t, b = 8.0, 400.0
I = b * t ** 3 / 12; Z = b * t ** 2 / 6
m_head = 60.0
W1 = m_head * G                     # 1 g
W3 = 3 * W1                         # 3 g
arm = 116.0                         # 헤드 무게중심 Y 0 -> 세운 판 가운데 Y 116 (굽힘 자리)
lev_drag = 560.0 - 12.0             # 끌림 작용점 Z 12 -> 선반 밑 Z 560
Kc = 1.30                           # 굽힘 R8 곡선보 안쪽 응력 계수(Roark, R중심/c = 12/4 = 3) — 기록용
H = {}
for case, f_drag, sfm in [('run', 30.0, 3.0), ('mis', 100.0, 2.0)]:
    M = W3 * arm + f_drag * lev_drag
    s = M / Z
    H[f'bend_root_{case}'] = {'M_Nmm': round(M), 'stress_MPa': round(s, 1), 'stress_curved_MPa': round(s * Kc, 1),
                              'sf': round(RP_S / s, 2), 'sf_curved': round(RP_S / (s * Kc), 2), 'sf_min': sfm,
                              'ok': RP_S / s >= sfm, 'near_10pct': sfm <= RP_S / s < 1.1 * sfm}
# 설계안 식 재현(50 kg x 2, 팔 112) — 옛 모델 대조
s_d = (50 * G * 2 * 112) / Z
H['design_basis_50kg_x2'] = {'stress_MPa': round(s_d, 1), 'sf': round(RP_S / s_d, 2)}

# 처짐·기울기: 선반 자유 구간(헤드 끝 Y 90 -> 굽힘 Y 104) + 세운 판(굽힘 Z 568 -> 볼트 줄 620, 모멘트 선형 감소)
EI = E_S * I
L_sh, L_up = 26.0, 52.0
c_rot = (L_sh + L_up / 2) / EI      # rad / (N·mm)
lev_needle = 560.0 - 12.0
for case, M in [('static_1g', W1 * arm), ('drag_run_30N', 30.0 * lev_drag), ('drag_mis_100N', 100.0 * lev_drag)]:
    th = M * c_rot
    H[f'tilt_{case}'] = {'M_Nmm': round(M), 'theta_mrad': round(th * 1e3, 3), 'needle_shift_mm': round(th * lev_needle, 3)}
# 흔들림 고유 진동수(X축 둘레 회전, 헤드 상자 Y 180 x Z 435, 무게중심 Y 0 · Z 342, 경첩 Y 116 · Z 564)
k_th = 1.0 / c_rot / 1000.0          # N·m/rad
r2 = (116e-3) ** 2 + ((564 - 342.5) * 1e-3) ** 2
J = m_head * ((0.180 ** 2 + 0.435 ** 2) / 12 + r2)
H['rock_freq'] = {'k_theta_Nm_rad': round(k_th), 'J_kgm2': round(J, 3), 'f_Hz': round(math.sqrt(k_th / J) / (2 * math.pi), 1),
                  'stitch_Hz_at_1500_3000spm': [25, 50]}

# 볼트 — 세운 판 x4 (보 앞면 탭), 바닥 모서리 Z 560 받침, 볼트 줄 Z 620 (팔 60)
B = {}
for case, f_drag, sfm in [('run', 30.0, 3.0), ('mis', 100.0, 2.0)]:
    M = W3 * arm + f_drag * lev_drag
    Tb = M / 60.0 / 4
    B[f'upright_{case}_le8_SS400'] = calc(d=5, le=8, load=round(Tb, 1), torque=7.0, bolt='12.9', base='SS400', sf_min=sfm)
    B[f'upright_{case}_le6_tube_t6'] = calc(d=5, le=6, load=round(Tb, 1), torque=7.0, bolt='12.9', base='SS400', sf_min=sfm)
    # 선반 x6 (헤드 윗면 탭, 주철 대신 SS400 근사): 무게 W3/6 + 끌림 모멘트 짝힘(헤드 끝 Y 90 받침, 줄 40·140)
    Md = f_drag * lev_drag
    Tm = Md / (3 * (140 + 40 ** 2 / 140))
    B[f'shelf_{case}_le8'] = calc(d=5, le=8, load=round(W3 / 6 + Tm, 1), torque=7.0, bolt='12.9', base='SS400', sf_min=sfm)
# 세운 판 볼트 전단(마찰): 예압 7 kN x 4 x mu 0.15 = 4.2 kN vs W3 + 끌림
B['upright_slip'] = {'friction_N': round(7000 * 4 * 0.15), 'shear_N': round(W3 + 100), 'sf': round(7000 * 4 * 0.15 / (W3 + 100), 2)}
B['upright_slip_5Nm'] = {'friction_N': round(5000 * 4 * 0.15), 'shear_N': round(W3 + 100), 'sf': round(5000 * 4 * 0.15 / (W3 + 100), 2)}
B['upright_le6_5Nm'] = calc(d=5, le=6, load=round((W3 * arm + 100 * lev_drag) / 240, 1), torque=5.0, bolt='12.9', base='SS400', sf_min=2.0)
out['hanger'] = H
out['bolts'] = B

# ---------------- 노루발 (v1 N01과 같은 모델, 틈만 v2 값) ----------------
E, RP = 205000.0, 345.0
w = 17.2e-3 * G * 3
L_tip = math.hypot(3 + 5, 6 + 3) - 3.0
F = {}
for k, c in {'sole_run_b6_Ltip': dict(t=2, b=6, load=50 + w, sf_min=3),
             'sole_mis_b6_Ltip': dict(t=2, b=6, load=150 + w, sf_min=2),
             'sole_run_bhalfper_Ltip': dict(t=2, b=round(math.pi * 3, 2), load=50 + w, sf_min=3),
             'sole_mis_bhalfper_Ltip': dict(t=2, b=round(math.pi * 3, 2), load=150 + w, sf_min=2),
             'fix_t3_mis_b6_Ltip': dict(t=3, b=6, load=150 + w, sf_min=2)}.items():
    F[k] = beam(length=round(L_tip, 2), e=E, sy=RP, **c)
d, lev = 6.0, 46.0 - 13.0
Ib = math.pi * d ** 4 / 64; Zb = math.pi * d ** 3 / 32
gap_min = 0.5                        # v2.0.2 노루발↔노즈 0.5, ↔바늘 0.7 (mech_M01_model.md 요약)
for k, f, sfm in [('bar_drag_run', 30.0, 3), ('bar_drag_mis', 100.0, 2)]:
    s = f * lev / Zb; dfl = f * lev ** 3 / (3 * E * Ib)
    F[k] = {'F_N': f, 'lever_mm': lev, 'stress_MPa': round(s, 1), 'sf': round(RP / s, 2), 'sf_min': sfm,
            'ok': RP / s >= sfm, 'near_10pct': sfm <= RP / s < 1.1 * sfm, 'deflection_mm': round(dfl, 3),
            'gap_min_mm': gap_min, 'motion_ok': dfl < gap_min}
F['bar_buckle_mis'] = {'Pcr_N': round(math.pi ** 2 * E * Ib / (2 * lev) ** 2), 'F_N': 150}
F['bar_buckle_mis']['sf'] = round(F['bar_buckle_mis']['Pcr_N'] / 150, 1)
out['foot'] = F

p = f'{ROOT}/fea/results/mech_M01_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bbox', out['step_bbox'])
for grp in ('hanger', 'foot'):
    for k, v in out[grp].items():
        print(grp, k, {kk: v[kk] for kk in ('stress_MPa', 'sf', 'sf_curved', 'deflection_mm', 'needle_shift_mm', 'f_Hz') if kk in v})
for k, v in B.items():
    print('bolt', k, v.get('sf_operating', ''), v.get('sf_tightening', ''), v.get('ok', v.get('sf')))
