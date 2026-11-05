# -*- coding: utf-8 -*-
"""DC2-03 해석부 손계산 — 북 받이 판 P_DC203_TRAY(SUS304 t1.5 판금, v2.5.4) + CB5-12 x2 + HNTT8-5 x2.
형상(저장본 v2.5.4 측정, mech_DC2-03_model.md 2절): 바닥 X -38~378 · Y -276~-40 · Z -250~-248.5, 사방 테두리 위로(위 끝 Z -233.5,
판 밑면 기준 높이 16.5), 1.38 kg. 받침: 바닥틀 HFS8-4080 :6(X 340~380) 윗면 Z -250에 X 340~378이 얹힘, CB5-12 x2 at X 360 · Y -230/-110.
=> 외팔: 받침 모서리 X 340(뒤집힘 받침점) ~ 끝 X -38, 팔 378. 볼트 줄 X 360은 받침점에서 20(지렛대).
FEA 환경 없음(D-16) -> 손계산. 판정 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), SF < 1.2만 '동작'.
체결 임시값 D-54(HNTT8-5 + CB5 4 N·m -> 예압 4 kN, μ 0.15), 물림 7.5(M07K 표준 = 1.5d).
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SF_OP, SF_MIS = 3.0, 2.0
E, NU, SY = 193000.0, 0.3, 205.0       # SUS304
T = 1.5
X_TIP, X_PIV, X_BOLT, X_END = -38.0, 340.0, 360.0, 378.0
Y0, Y1 = -276.0, -40.0
W = Y1 - Y0                            # 236
H = 16.5                               # 테두리 높이(판 밑면 기준)
L = X_PIV - X_TIP                      # 378 외팔
LEV = X_BOLT - X_PIV                   # 20 지렛대
M_TRAY = 1.3808                        # kg (저장본)
HAND_MIS, HAND_REF = 100.0, 50.0       # 오조작 손(D-79 100 N 꼴) / 설계안 임시 50 N(참고)
BOB_M, BOB_H = 0.030, 208.5            # 북집+북 30 g 임시(D-108), 떨어지는 높이 Z -40 -> -248.5
PRELOAD = 4000.0


def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    return '됨'


def step_bbox(path):
    pts = []
    for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", open(path, encoding='latin-1').read()):
        v = [float(x) for x in m.group(1).split(',')]
        if len(v) == 3: pts.append(v)
    return {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}


def channel(bw, nflange):
    """바닥 bw x t + 세운 테두리 nflange 개(t x (H-t)). z = 판 밑면에서 위로. 반환 (A, zc, I, Zmin)."""
    parts = [(bw * T, T / 2, bw * T ** 3 / 12)] + [(T * (H - T), T + (H - T) / 2, T * (H - T) ** 3 / 12)] * nflange
    A = sum(p[0] for p in parts)
    zc = sum(p[0] * p[1] for p in parts) / A
    I = sum(p[2] + p[0] * (p[1] - zc) ** 2 for p in parts)
    c = max(zc, H - zc)
    return A, zc, I, I / c


out = {'assume': {'E': E, 'Sy': SY, 't': T, 'L_cant': L, 'lever_pivot_bolt': LEV, 'tray_kg': M_TRAY, 'g_factor': 3,
                  'hand_misuse_N': HAND_MIS, 'hand_ref_N': HAND_REF, 'bobbin_kg': BOB_M, 'drop_h_mm': BOB_H, 'preload_N': PRELOAD,
                  'src': '형상 = 저장본 v2.5.4 측정(mech_DC2-03_model.md), 손 100 N = M-09 오조작 꼴(D-82·D-38 미정), 북 30 g = D-108 임시, 예압 D-54'}}
out['step_bbox'] = step_bbox(f'{ROOT}/tools/out/mech_DC2-03/stepout/P_DC203_TRAY.step')

# 1. 단면
A_f, zc_f, I_f, Z_f = channel(W, 2)               # 전 폭 채널
BE = 30 * T                                       # 모서리 하중: 가까운 테두리 + 유효 바닥 30t(보수)
A_l, zc_l, I_l, Z_l = channel(BE, 1)
out['section'] = {'full_channel': {'A': round(A_f, 1), 'zc': round(zc_f, 2), 'I': round(I_f, 1), 'Z': round(Z_f, 1)},
                  'corner_L_30t': {'b_eff': BE, 'A': round(A_l, 1), 'zc': round(zc_l, 2), 'I': round(I_l, 1), 'Z': round(Z_l, 1)}}

w_self = M_TRAY * G * 3 / L                       # N/mm (3 g, 외팔 길이에 고르게 — 보수: 받침 위 몫도 팔에 둠)
M_self = w_self * L ** 2 / 2
d_self = w_self * L ** 4 / (8 * E * I_f)

cases = {}
# 2. 운전: 자중 x3 g + 북 떨어짐(끝에 떨어짐, 전 폭 채널 강성)
k_tip = 3 * E * I_f / L ** 3
E_drop = BOB_M * G * BOB_H                        # N·mm
m_eff_tip = M_TRAY * 33 / 140                     # 외팔 끝 유효 질량(Roark 충격 질량 보정)
eta_tip = BOB_M / (BOB_M + m_eff_tip)
F_drop = BOB_M * G + math.sqrt((BOB_M * G) ** 2 + 2 * E_drop * eta_tip * k_tip)
M_op = M_self + F_drop * L
s_op = M_op / Z_f
cases['운전: 자중x3g + 북 떨어짐(끝)'] = {'F_drop_eq_N': round(F_drop, 2), 'eta': round(eta_tip, 3), 'M_Nmm': round(M_op, 0), 'sigma': round(s_op, 2),
                                    'SF': round(SY / s_op, 2), 'need': SF_OP, 'tip_defl_mm': round(d_self + F_drop / k_tip, 3)}
# 2b. 북 떨어짐 판 국부(가장 넓은 칸 가운데 — 고정 둘레 원판 a = W/2, Roark 표 11.2 case 16, 접점 r0 2)
D = E * T ** 3 / (12 * (1 - NU ** 2))
a = W / 2
k_pl = 16 * math.pi * D / a ** 2
m_eff_pl = 0.2 * math.pi * a ** 2 * T * 7.93e-6      # 원판 가운데 유효 질량(판 질량 0.2배 어림)
eta_pl = BOB_M / (BOB_M + m_eff_pl)
F_pl = BOB_M * G + math.sqrt((BOB_M * G) ** 2 + 2 * E_drop * eta_pl * k_pl)
F_pl_nocorr = BOB_M * G + math.sqrt((BOB_M * G) ** 2 + 2 * E_drop * k_pl)
r0 = 2.0
r0p = math.sqrt(1.6 * r0 ** 2 + T ** 2) - 0.675 * T if r0 < 1.7 * T else r0
s_pl = 3 * F_pl * (1 + NU) / (2 * math.pi * T ** 2) * math.log(a / r0p) + 3 * F_pl / (2 * math.pi * T ** 2)
cases['운전: 북 떨어짐 판 국부(칸 가운데)'] = {'k_plate_N_per_mm': round(k_pl, 2), 'F_eq_N': round(F_pl, 2), 'sigma': round(s_pl, 1),
                                       'SF': round(SY / s_pl, 2), 'need': SF_OP, 'eta': round(eta_pl, 3), 'F_eq_no_mass_corr_N': round(F_pl_nocorr, 1), 'model': 'Roark 고정 둘레 원판 가운데 하중(r0 2, 판 두께 보정 r0\')'}

# 3. 오조작: 손 100 N 끝 — 가운데(전 폭) / 모서리(가까운 테두리 + 30t)
for name, F in (('오조작: 손 100 N 끝 가운데(전 폭 채널)', HAND_MIS), ('참고: 손 50 N 끝 가운데(설계안 값)', HAND_REF)):
    M = M_self + F * L
    s = M / Z_f
    cases[name] = {'M_Nmm': round(M, 0), 'sigma': round(s, 2), 'SF': round(SY / s, 2), 'need': SF_MIS,
                   'tip_defl_mm': round(d_self + F * L ** 3 / (3 * E * I_f), 3)}
M_c = M_self * (BE + T) / W + HAND_MIS * L        # 모서리 띠: 자중은 폭 몫만
s_c = M_c / Z_l
cases['오조작: 손 100 N 끝 모서리(테두리 + 30t, 보수)'] = {'M_Nmm': round(M_c, 0), 'sigma': round(s_c, 2), 'SF': round(SY / s_c, 2),
                                               'need': SF_MIS, 'tip_defl_mm': round(HAND_MIS * L ** 3 / (3 * E * I_l), 2),
                                               'note': '판 전체가 나눠 받으므로 실제는 가운데 값과 이 값 사이'}

# 4. 볼트: 받침점 X 340 둘레 모멘트를 볼트 줄(지렛대 20) 2개가 뺀다
M_root = M_self + HAND_MIS * L
T_bolt = M_root / LEV / 2
bolt = calc(d=5, le=7.5, load=T_bolt, torque=4.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS)
# 판 국부: 볼트 머리 둘레 뚫림 전단. 뿌리(X 340~360)는 점 볼트 2개라 테두리 몫이 판을 거쳐 볼트로 가야 한다(전단 지연).
# 손계산 범위: 낙관 = 전 폭 채널(위 cases), 비관 = 볼트 둘레 띠만(볼트 간격 120 + 양쪽 20 = 160 평판, 테두리 몫 없음).
tau_punch = T_bolt / (math.pi * 8.5 * T)
V_root = 2 * T_bolt
tau_web = V_root / (2 * (H - T) * T)
B_BAND = 120 + 2 * 20
s_band = M_root / (B_BAND * T ** 2 / 6)
plate_local = {'bolt_tension_each_N': round(T_bolt, 1), 'punch_tau': round(tau_punch, 1), 'SF_punch': round(0.58 * SY / tau_punch, 2),
               'root_shear_V_N': round(V_root, 0), 'web_tau': round(tau_web, 1), 'SF_web_shear': round(0.58 * SY / tau_web, 2),
               'band_b': B_BAND, 'band_sigma_pessimistic': round(s_band, 0), 'SF_band': round(SY / s_band, 2), 'need': SF_MIS,
               'note': '실제 뿌리 응력은 채널(낙관)과 띠(비관) 사이. 모서리 릴리프로 테두리끼리 이어지지 않아 판 안 전단 지연을 손계산으로 못 좁힘 -> FEA 대상(환경 없음 D-16)'}
seat = PRELOAD / (math.pi / 4 * (8.5 ** 2 - 5.5 ** 2))
slip = PRELOAD * 2 * 0.15 / (HAND_MIS * 0.5 + M_TRAY * G * 3)  # 옆 힘(손이 끌 때 μ 0.5 꼴) 대비 마찰
for k, v in cases.items():
    v['verdict'] = verdict(v['SF'], v['need'])
out['cases'] = cases
out['bolt_CB5-12_HNTT8-5'] = bolt
out['plate_local'] = plate_local
plate_local['verdict_punch'] = verdict(plate_local['SF_punch'], SF_MIS)
plate_local['verdict_band'] = verdict(plate_local['SF_band'], SF_MIS)
out['seat_pressure_MPa'] = {'p': round(seat, 1), 'pG_SUS304': 400, 'SF': round(400 / seat, 2)}
out['slip_SF'] = round(slip, 1)
out['thin_plate_ratio_t_over_L'] = round(T / L, 4)
out['beam_tool_check'] = beam(T, W, L, load=HAND_MIS, e=E, sy=SY, sf_min=SF_MIS)   # 테두리 없는 평판(하한 참고)

fix = {}
M_ss = HAND_MIS * L / 4 + M_TRAY * G * 3 * L / 8
fix['A: -X 끝 받침 추가(양끝 받침, 가운데 손 100 N)'] = {'sigma': round(M_ss / Z_f, 1), 'SF': round(SY * Z_f / M_ss, 2)}
T3 = 3.0
A3 = [(W * T3, T3 / 2, W * T3 ** 3 / 12)] + [(T3 * (H - T3), T3 + (H - T3) / 2, T3 * (H - T3) ** 3 / 12)] * 2
At = sum(q[0] for q in A3); z3 = sum(q[0] * q[1] for q in A3) / At; I3 = sum(q[2] + q[0] * (q[1] - z3) ** 2 for q in A3)
Z3 = I3 / max(z3, H - z3); M3 = M_self * 2 + HAND_MIS * L
fix['B: t3 외팔 그대로(테두리 16.5, 낙관 채널)'] = {'sigma': round(M3 / Z3, 1), 'SF': round(SY / (M3 / Z3), 2), 'note': '뿌리 전단 지연 그대로 — 권하지 않음'}
out['fix_options'] = fix
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-03_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in cases.items():
    print(k, '| sigma', v['sigma'], 'SF', v['SF'], '/', v['need'], v['verdict'], '| defl', v.get('tip_defl_mm'))
print('bolt', bolt['worst'], bolt['sf_operating'], bolt['sf_tightening'], 'ok', bolt['ok'])
print('plate_local', plate_local)
print('seat', out['seat_pressure_MPa'], 'slip', out['slip_SF'], 'bbox', out['step_bbox'])
print('fix', fix)
print('flat plate only', out['beam_tool_check'])
