# -*- coding: utf-8 -*-
"""DC2-03 해석부 1회차(수정 1 뒤, v2.5.5) 손계산 — 북 받이 판 P_DC203_TRAY 양끝 받침 + 새 받침 HFS8-4080-300_DC203 + LBRKT 2 + 볼트.
형상(저장본 v2.5.5 측정, mech_DC2-03_model1.md 3절):
  받이 판 바닥 X -38~378 · Y -276~-40 · Z -250~-248.5, 테두리 높이 16.5, t1.5, 1.38 kg.
  받침 +X: 바닥틀 :6(X 340~380) 윗면, CB5-12 x2 at X 360 (Y -230/-110).
  받침 -X(새): HFS8-4080-300_DC203(X -38~2 · Y -280~20 · Z -330~-250) 윗면, CB5-12 x2 at X -18 (Y -230/-170).
  새 받침은 아래 레일 :3(Y +-20, 윗면 Z -330)에 얹히고 LBRKT 2개(Y -15~15, 볼트 줄 Y 0)로 묶임 -> 레일 -Y 모서리(Y -20)에서 외팔 256(끝 Y -276).
FEA 환경 없음(D-16) -> 손계산. 판정 요구서 6-1 = M-09(운전 SF 3, 오조작 SF 2), SF < 1.2만 '동작'.
임시값: 손 100 N(D-82·D-38), 북 30 g(D-108), CB5 예압 4 kN · mu 0.15(D-54).
HFS8-4080 단면 성질은 카탈로그 값 미확인 -> 하한 어림 I 1.0e5 mm^4(바깥 벽 t2 관 40x80 강축 3.9e5의 약 1/4), 재질 A6063-T5 항복 145(임시).
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SF_OP, SF_MIS = 3.0, 2.0
E, NU, SY = 193000.0, 0.3, 205.0       # SUS304
T, H = 1.5, 16.5
Y0, Y1 = -276.0, -40.0
W = Y1 - Y0                            # 236
L_EDGE = 340.0 - 2.0                   # 받침 모서리 사이 338
L_BOLT = 360.0 - (-18.0)               # 볼트 줄 사이 378 (보수: 이 값으로 단순 지지)
L = L_BOLT
M_TRAY = 1.3808
HAND = 100.0
BOB_M, BOB_H = 0.030, 208.5
PRELOAD, MU = 4000.0, 0.15
E_AL, SY_AL, I_AL = 70000.0, 145.0, 1.0e5
C_AL = 40.0


def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    return '됨'


def step_info(path):
    txt = open(path, encoding='latin-1').read()
    pts = []
    for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt):
        v = [float(x) for x in m.group(1).split(',')]
        if len(v) == 3: pts.append(v)
    circ = [float(m.group(1)) for m in re.finditer(r"CYLINDRICAL_SURFACE\('[^']*',#\d+,([0-9.Ee+-]+)\)", txt)]
    return {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)],
            'circle_r_2.75_count': sum(1 for r in circ if abs(r - 2.75) < 0.01)}


def channel(bw, nflange):
    parts = [(bw * T, T / 2, bw * T ** 3 / 12)] + [(T * (H - T), T + (H - T) / 2, T * (H - T) ** 3 / 12)] * nflange
    A = sum(p[0] for p in parts); zc = sum(p[0] * p[1] for p in parts) / A
    I = sum(p[2] + p[0] * (p[1] - zc) ** 2 for p in parts)
    return A, zc, I, I / max(zc, H - zc)


out = {'assume': {'E': E, 'Sy': SY, 't': T, 'span_bolt': L_BOLT, 'span_edge': L_EDGE, 'tray_kg': M_TRAY, 'hand_N': HAND,
                  'bobbin_kg': BOB_M, 'drop_h': BOB_H, 'preload': PRELOAD, 'mu': MU,
                  'HFS8-4080': {'E': E_AL, 'Sy': SY_AL, 'I_lower_bound': I_AL, 'c': C_AL, 'note': '카탈로그 미확인 하한 어림'},
                  'src': '형상 = v2.5.5 측정(mech_DC2-03_model1.md), 손 100 N D-82·D-38, 북 D-108, 예압 D-54'}}
out['step'] = step_info(f'{ROOT}/tools/out/mech_DC2-03/stepout/P_DC203_TRAY_fix1.step')

A_f, zc_f, I_f, Z_f = channel(W, 2)
BE = 30 * T
A_l, zc_l, I_l, Z_l = channel(BE, 1)
out['section'] = {'full': {'I': round(I_f, 1), 'Z': round(Z_f, 1)}, 'corner_L_30t': {'I': round(I_l, 1), 'Z': round(Z_l, 1)}}

wq = M_TRAY * G * 3 / L
M_self = wq * L ** 2 / 8
d_self = 5 * wq * L ** 4 / (384 * E * I_f)
cases = {}
# 운전: 자중 x3 g + 북 떨어짐(경간 가운데, 단순 지지)
k_mid = 48 * E * I_f / L ** 3
E_drop = BOB_M * G * BOB_H
m_eff = M_TRAY * 17 / 35
eta = BOB_M / (BOB_M + m_eff)
F_drop = BOB_M * G + math.sqrt((BOB_M * G) ** 2 + 2 * E_drop * eta * k_mid)
M_op = M_self + F_drop * L / 4
cases['운전: 자중x3g + 북 떨어짐(가운데, 단순 지지 378)'] = {'F_eq': round(F_drop, 2), 'eta': round(eta, 3), 'sigma': round(M_op / Z_f, 2),
    'SF': round(SY * Z_f / M_op, 2), 'need': SF_OP, 'defl': round(d_self + F_drop / k_mid, 3)}
# 운전: 판 국부(칸 가운데) — 칸 크기·두께 그대로라 지난 회차 식 그대로
D = E * T ** 3 / (12 * (1 - NU ** 2)); a = W / 2
k_pl = 16 * math.pi * D / a ** 2
m_pl = 0.2 * math.pi * a ** 2 * T * 7.93e-6
eta_pl = BOB_M / (BOB_M + m_pl)
F_pl = BOB_M * G + math.sqrt((BOB_M * G) ** 2 + 2 * E_drop * eta_pl * k_pl)
s_pl = 3 * F_pl * (1 + NU) / (2 * math.pi * T ** 2) * math.log(a / 2.0) + 3 * F_pl / (2 * math.pi * T ** 2)
cases['운전: 북 떨어짐 판 국부(칸 가운데, 지난 회차와 같음)'] = {'F_eq': round(F_pl, 2), 'sigma': round(s_pl, 1), 'SF': round(SY / s_pl, 2), 'need': SF_OP}
# 오조작: 손 100 N 가운데(전 폭) / 가운데 모서리(테두리 + 30t)
M_h = M_self + HAND * L / 4
cases['오조작: 손 100 N 가운데(전 폭 채널, 단순 지지 378)'] = {'sigma': round(M_h / Z_f, 2), 'SF': round(SY * Z_f / M_h, 2), 'need': SF_MIS,
    'defl': round(d_self + HAND * L ** 3 / (48 * E * I_f), 3)}
M_hc = M_self * (BE + T) / W + HAND * L / 4
cases['오조작: 손 100 N 가운데 모서리(테두리 + 30t, 보수)'] = {'sigma': round(M_hc / Z_l, 2), 'SF': round(SY * Z_l / M_hc, 2), 'need': SF_MIS,
    'defl': round(HAND * L ** 3 / (48 * E * I_l), 3)}
cases['참고: 받침 모서리 경간 338로 볼 때(손 100 N 가운데)'] = {'sigma': round((wq * L_EDGE ** 2 / 8 + HAND * L_EDGE / 4) / Z_f, 2),
    'SF': round(SY * Z_f / (wq * L_EDGE ** 2 / 8 + HAND * L_EDGE / 4), 2), 'need': SF_MIS}
# 받침 위 끝 내민 부분(-X 끝: 볼트 X -18 ~ 끝 X -38 = 20, 받침 위에 얹혀 있음 -> 내민 팔 0. +X: X 360~378 받침 위). 손이 끝을 눌러도 받침이 직접 받음.
# 받침 위 판 국부: 손 100 N이 받침 바로 위 -> 바닥이 형재에 눌림(압축), 볼트 인장 없음.

# 새 받침 HFS8-4080-300: 레일 :3 -Y 모서리 Y -20에서 끝 Y -276까지 외팔 256, 손 100 N 전부 끝(보수) + 받이 판 자중 몫
ARM = -20.0 - (-276.0)
F_sup = HAND + M_TRAY * G * 3 / 2
M_sup = F_sup * ARM
s_sup = M_sup * C_AL / I_AL
d_sup = F_sup * ARM ** 3 / (3 * E_AL * I_AL)
cases['오조작: 새 받침 HFS8-4080-300 외팔 256(손 100 N 끝, I 하한)'] = {'M_Nmm': round(M_sup, 0), 'sigma': round(s_sup, 2),
    'SF': round(SY_AL / s_sup, 2), 'need': SF_MIS, 'defl': round(d_sup, 3)}
# LBRKT 2: 뒤집힘 받침점 Y -20, 볼트 줄 Y 0 -> 들림 힘
LEV = 20.0
F_up = M_sup / LEV
F_br = F_up / 2
ARM_BR = 32.0 - (2.0 + 3.0)            # 세로 다리 중심(X 5) ~ 가로 다리 볼트(X 32) = 27 (보수, 모델링부 24)
Z_br = 30 * 6 ** 2 / 6
s_br = F_br * ARM_BR / Z_br
cases['오조작: LBRKT 가로 다리 굽힘(하나 몫)'] = {'F_each': round(F_br, 1), 'arm': ARM_BR, 'sigma': round(s_br, 1), 'SF': round(SY / s_br, 2), 'need': SF_MIS}
for v in cases.values():
    v['verdict'] = verdict(v['SF'], v['need'])
out['cases'] = cases

# 볼트
R_end = HAND / 2 + M_TRAY * G * 3 / 2               # 한 끝 반력(손 가운데) — 누르는 쪽이라 실제 볼트 인장 아님. 보수로 인장 취급
bolts = {}
bolts['CB5-12 + HNTT8-5 (받이 판 -X 끝, 하나)'] = calc(d=5, le=8.0, load=R_end / 2, torque=4.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS)
bolts['CB5-16 + HNTT8-5 (LBRKT 가로 다리 -> 레일 :3, 하나)'] = calc(d=5, le=7.5, load=F_br, torque=4.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS)
# LBRKT 세로 다리 볼트: 들림 힘이 전단(받침 옆면 홈, 힘은 홈 길이(Y)에 직각인 Z -> 미끄러지면 홈 벽·구멍 틈 0.25에서 볼트 지압)
slip_sf = PRELOAD * MU / F_br
tau_bolt = F_br / 14.2
bolts['CB5-16 세로 다리(전단)'] = {'F_shear': round(F_br, 1), 'slip_SF': round(slip_sf, 2), 'tau_bolt_MPa': round(tau_bolt, 1),
    'SF_shear_12.9': round(0.58 * 1080 / tau_bolt, 1),
    'note': '마찰만으로는 1 근처. 미끄러져도 구멍 틈(Ø5.5-Ø5 = 0.5) 안에서 볼트가 전단으로 받음. 받이 판 위치 변화 <= 0.25'}
out['bolts'] = bolts
out['beam_tool_flat_plate_ss_ref'] = beam(T, W, L / 2, load=HAND / 2, e=E, sy=SY, sf_min=SF_MIS)  # 테두리 없는 평판 반 경간 외팔(하한 참고)

# 지난 모델(외팔 378)과 차이
out['vs_prev_model'] = {'prev_cantilever_SF_hand100_mid': 1.10, 'now_ss_SF_hand100_mid': cases['오조작: 손 100 N 가운데(전 폭 채널, 단순 지지 378)']['SF']}
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-03_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('step', out['step'])
for k, v in cases.items():
    print(k, '| sigma', v['sigma'], 'SF', v['SF'], '/', v['need'], v['verdict'], '| defl', v.get('defl'))
for k, v in bolts.items():
    print(k, {kk: v[kk] for kk in v if kk in ('worst', 'ok', 'sf_operating', 'sf_tightening', 'slip_SF', 'SF_shear_12.9')})
