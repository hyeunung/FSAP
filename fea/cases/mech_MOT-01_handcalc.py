# -*- coding: utf-8 -*-
"""MOT-01 해석부 손계산 (E-18: 새로 만들거나 옮긴 하중 부품·체결만).
해석 환경 없음(D-16) -> FEA 대신 손계산. 좌표는 v2.7.0 저장본 실측(tools/out/mech_MOT-01/measure_saved.json, REST 자세).
하중 경우는 mech_M02_handcalc.py·mech_M03_handcalc.py 와 같은 모델(fea/models.json)에 질량·토크만 바꿔 넣는다.
"""
import json, math, sys, os
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc as bolt

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
RP = {'SUS304': 205.0, 'S45C': 345.0, 'A6061': 240.0}
out = {}

def sf(rp, s):
    return round(rp / s, 2) if s > 0 else 999.0

# ---------- 0) 실측 질량 (STEP 속 꽉 찬 고체 -> 카탈로그보다 무겁다: 큰 쪽을 씀) ----------
M = json.load(open(f'{ROOT}/tools/out/mech_MOT-01/measure_saved.json', encoding='utf-8'))
B = {b['name']: b for b in M['bodies']}
def grp(prefix):
    bs = [b for n, b in B.items() if n.startswith(prefix)]
    m = sum(b['mass_g'] for b in bs) / 1000
    c = [sum(b['mass_g'] * b['center_of_mass'][i] for b in bs) / 1000 / m for i in range(3)]
    return m, c
m_mot2, c_mot2 = grp('HG-KR23_M02')
m_red2, c_red2 = grp('PGX62-H-10_M02')
m_motx, c_motx = grp('HG-KR23_M03X')
m_redx, c_redx = grp('PGX62-H-10_M03X')
m_mot3, c_mot3 = grp('HG-KR43_U3')
out['mass'] = {'HG-KR23_model_kg': round(m_mot2, 3), 'HG-KR23_catalog_kg': 0.96, 'PGX62-H-10_model_kg': round(m_red2, 3),
               'HG-KR43_model_kg': round(m_mot3, 3), 'HG-KR43_catalog_kg': 1.4,
               'note': 'STEP 바디는 속이 찬 Steel이라 카탈로그보다 무겁다(HG-KR23 2.01 vs 0.96). 하중은 모델 질량(큰 쪽)으로 셈'}

# ---------- 1) U4(M02) 누름 팔 하중 경우: 옛 모델 + 서보·감속기 질량 차이 ----------
PIV = (-300.0, 70.0); a_w, a_c = 200.0, 140.0
th = math.radians(8.626)              # REST -> 0 자세(누름) 되돌림
def arm0(c):
    dx, dz = c[0] - PIV[0], c[2] - PIV[1]
    return dx * math.cos(th) + dz * math.sin(th)
m_old_cat, x_old = 4.632, -181.5      # mech_M02_handcalc.json moving.catalog
Mw_old = m_old_cat * G * (x_old - PIV[0])
# 옛 임시: MHMF022 0.96 kg @ -234.2, VRXF 1.1 kg @ -154 (카탈로그 몫)
dM = (m_mot2 * arm0(c_mot2) + m_red2 * arm0(c_red2)) - (0.96 * (-234.2 - PIV[0]) + 1.1 * (-154.0 - PIV[0]))
dm = m_mot2 + m_red2 - (0.96 + 1.1)
m_new = m_old_cat + dm
Mw1 = Mw_old + dM * G
A_push = math.pi * 20 ** 2 / 4
CASES = {}
for case, Fc, mu, tlim, sfm in (('run', None, 0.5, 3.5, 3.0), ('mis', 0.5 * A_push, 0.5, None, 2.0), ('whatif_mu0.8', 0.5 * A_push, 0.8, None, 2.0)):
    if Fc is None:
        Fc = (100.0 * a_w - Mw1) / a_c
    Fw = (Fc * a_c + 3 * Mw1) / a_w
    Ft = mu * Fw if tlim is None else min(tlim / 0.06, mu * Fw)
    W = 3 * m_new * G
    Rz = Fc + W - Fw
    CASES[case] = {'F_cyl_N': round(Fc, 1), 'F_wheel_N': round(Fw, 1), 'F_tan_Y_N': round(Ft, 1), 'W_N': round(W, 1), 'R_pivot_z_N': round(Rz, 1), 'sf_min': sfm}
out['U4_moving'] = {'arm_motor_mm': round(arm0(c_mot2), 1), 'arm_reducer_mm': round(arm0(c_red2), 1), 'dm_kg': round(dm, 3),
                    'dM_kgmm': round(dM, 1), 'm_new_kg': round(m_new, 3)}
out['U4_cases'] = CASES

S = {}
for cn, c in CASES.items():
    Fw, Ft, Rz, Fc, sfm = c['F_wheel_N'], c['F_tan_Y_N'], c['R_pivot_z_N'], c['F_cyl_N'], c['sf_min']
    r = {}
    # --- P_M02_PIVOT_PIN Ø12 S45C (새 가공품): 머리 Y -65~-60 이 BASE 다리 바깥면, 다리 Y -60~-52 구멍에 끼움 -> 뿌리 Y -52
    # MPFZ12-10 부시: N Y -40~-30(가운데 -35), P Y 30~40(가운데 35) -> 뿌리에서 17, 87, 간격 70
    a1, a2 = 17.0, 87.0; sp = a2 - a1
    Mx = Ft * (70 - 10); Mz = Ft * a_w
    M_root = math.hypot(abs(Rz) * (a1 + a2) / 2 + Mx * (a2 - a1) / sp, Mz * (a2 - a1) / sp)
    Zp = math.pi * 12 ** 3 / 32
    s = M_root / Zp
    # 끝 M5 탭(Y 30.2~40.2, Ø4.2 구멍) 단면: P 부시 가운데 Y 35 바깥은 하중 없음 -> 탭 시작 Y 30.2 에서 P 부시 몫 x 4.8
    F2 = abs(Rz) / 2 + math.hypot(Mx, Mz) / sp
    M_tap = F2 * 4.8
    Zt = math.pi * (12 ** 4 - 5 ** 4) / (32 * 12)
    tau_pin = (abs(Rz) / 2 + math.hypot(Mx, Mz) / sp) / (math.pi * 12 ** 2 / 4)
    r['P_M02_PIVOT_PIN'] = {'M_root_Nmm': round(M_root), 'sigma_root_MPa': round(s, 1), 'sf_root': sf(RP['S45C'], s),
                            'M_tap_Nmm': round(M_tap), 'sigma_tap_MPa': round(M_tap / Zt, 1), 'sf_tap': sf(RP['S45C'], M_tap / Zt),
                            'bush_force_max_N': round(F2, 1), 'bush_p_MPa': round(F2 / (12 * 10), 2),
                            'ok': RP['S45C'] / s >= sfm, 'near_10pct': sfm <= RP['S45C'] / s < 1.1 * sfm}
    # 핀 축 방향: 접선 Y 힘 +Y 이면 P 부시 플랜지 -> 와셔 -> CB5-12(핀 끝 탭) -> 핀 인장 -> 머리가 다리 바깥면에 받힘(CB4-12 무하중)
    r['pivot_axial_end_bolt_N'] = round(Ft, 1)
    # --- P_M02_ARM_SIDE_N (고침): 로드 핀 단면 X -160 이 안면 홈(X -214~-134, Z 40~104, 깊이 2) 안 -> Z 40~104 는 t4, 104~117.5 는 t6
    segs = [(40.0, 104.0, 4.0), (104.0, 117.5, 6.0)]
    A = sum((z2 - z1) * t for z1, z2, t in segs)
    zc = sum((z2 - z1) * t * (z1 + z2) / 2 for z1, z2, t in segs) / A
    I = sum(t * (z2 - z1) ** 3 / 12 + (z2 - z1) * t * ((z1 + z2) / 2 - zc) ** 2 for z1, z2, t in segs)
    Zs = I / max(zc - 40.0, 117.5 - zc)
    Ms = Fw * 60 / 2
    # 피벗 구멍 Ø18 (옛 Ø16): 판 끝 X -325.3, 피벗 X -300 -> 살 25.3 - 9 = 16.3, t6
    Fb_side = F2
    tear = Fb_side / (2 * 16.3 * 6)
    r['P_M02_ARM_SIDE_N'] = {'groove_Z_mm3': round(Zs, 1), 'M_each_Nmm': round(Ms), 'sigma_MPa': round(Ms / Zs, 2), 'sf': sf(RP['SUS304'], Ms / Zs),
                             'pivot_hole_bearing_MPa': round(Fb_side / (18 * 6), 2), 'pivot_tearout_MPa': round(tear, 2),
                             'sf_tear(0.6Rp)': sf(0.6 * RP['SUS304'], tear)}
    # --- BASE 세운 다리(하중이 바뀐 이웃, 옛 식 그대로): 기록용
    Zl = 45 * 8 ** 2 / 6
    M_out = Ft * (242 - 10) + abs(Rz) * 56
    tau = Mz / (0.291 * 45 * 8 ** 2)
    s_eq = math.sqrt((M_out / Zl) ** 2 + 3 * tau ** 2)
    r['P_M02_BASE_upright(이웃)'] = {'sigma_eq_MPa': round(s_eq, 1), 'sf': sf(RP['SUS304'], s_eq), 'ok': RP['SUS304'] / s_eq >= sfm}
    S[cn] = r
out['U4_strength'] = S

# ---------- 2) U5X(M03) 구동 브래킷 P_M03_DRV_BRKT (SUS304, 웨브 Y 82~90 t8, Ø50 H8 관통) ----------
# 벨트 축 하중: 운전 300 N(초기 장력 150 x 2), 오조작 = HG-KR23 최대 2.2 N·m x 10 x 0.9 / r 47.75
r_p = 47.75
belt = {'운전': 300.0, '오조작': 2.2 * 10 * 0.9 / (r_p / 1000)}
mx = m_motx + m_redx
cgy = (m_motx * c_motx[1] + m_redx * c_redx[1]) / mx
arm_w = 82.0 - cgy                      # 웨브 바깥면 Y 82 에서 -Y 로 외팔
y_pul = 104.0                           # 풀리 = 키 Y 94~114 가운데
Wm = 3 * mx * G
Zw = (120 - 50) * 8 ** 2 / 6           # Ø50 구멍 지나는 단면
X = {}
for cn, Fb in belt.items():
    x = {}
    # 다리 사이 116 고정-고정 보, 가운데 모멘트 -> 최대 M/2 (옛 M03 식, 단면만 새것)
    s_web = (Wm * arm_w / 2 + Fb * (y_pul - 86) / 2) / Zw
    s_web_kt = 2.4 * s_web             # 구멍 가장자리 응력 집중(판 굽힘, d/w 0.42) -> 피로·기록용
    s_leg = (Wm / 2 * 26 / 2) / (120 * 4 ** 2 / 6)
    x['P_M03_DRV_BRKT'] = {'sigma_web_net_MPa': round(s_web, 1), 'sf': sf(RP['SUS304'], max(s_web, s_leg)),
                           'sigma_web_hole_Kt2.4_MPa': round(s_web_kt, 1), 'sf_with_Kt': sf(RP['SUS304'], s_web_kt), 'sigma_leg_MPa': round(s_leg, 1)}
    # 감속기 -> 웨브 M5 관통 탭 x4 (PCD 70, 물림 8): 무게·벨트 모멘트 -> 인장, 벨트·무게·토크 -> 전단(마찰)
    Mo = Wm * (82 - cgy) + Fb * (y_pul - 82)
    T_bolt = Mo / (2 * 49.5) * 1.0
    T_out = 2.2 * 10 if cn == '오조작' else 0.64 * 10
    V_bolt = (math.hypot(Fb, Wm)) / 4 + T_out * 1000 / (4 * 35)
    x['reducer_bolt'] = {'T_each_N': round(T_bolt, 1), 'V_each_N': round(V_bolt, 1),
                         'slip_sf(5kN x mu0.15 / V)': round(5000 * 0.15 / V_bolt, 2)}
    # 아이들러 축 (고침: Y 90~115, Ø10 + 칼라 Ø14 Y 94~97, 양 끝 M5 탭 DP10·DP12 -> 속 빔)
    Mi = Fb * (106.5 - 97)
    Zi = math.pi * (10 ** 4 - 5 ** 4) / (32 * 10)     # 탭 큰지름 Ø5 빼고
    x['P_M03_IDLER_SHAFT(이웃, 고침)'] = {'M_Nmm': round(Mi), 'sigma_MPa': round(Mi / Zi, 1), 'sf': sf(RP['S45C'], Mi / Zi),
                                         '6200ZZ_each_N': round(Fb / 2, 1), 'sf_C0r_2.38kN': round(2380 / (Fb / 2), 1)}
    x['PGX62_radial'] = {'F_N': round(Fb, 1), 'allow_N': 1120, 'ratio': round(1120 / Fb, 2)}
    X[cn] = x
out['U5X'] = {'belt_N': {k: round(v, 1) for k, v in belt.items()}, 'm_kg': round(mx, 3), 'cg_y': round(cgy, 1), 'arm_from_web_mm': round(arm_w, 1),
              'W_3g_N': round(Wm, 1), 'cases': X}

# ---------- 3) U3 아랫축 브래킷 P_U3_LDRV_BRKT (A6061, 새 가공품) ----------
# 판(플랜지 X 418~430 t12) - 옆벽 2(Y ±45~±53 t8, X 418~545, Z -140~-50) - 바닥판(X 537~545 t8)이 HFS8-4080 에 CB5-16 x4 + HNTT8-5
# 바닥판 볼트 Y ±38, Z -112/-152. 모터 HG-KR43 + 커플링 SCXW46(임시 0.19 kg) + 브래킷 자중, 3 g. 최대 토크 4.5 N·m(정지 반력)
m3 = m_mot3 + B['STEP대기_SCXW46-14-15']['mass_g'] / 1000
x3 = (m_mot3 * c_mot3[0] + B['STEP대기_SCXW46-14-15']['mass_g'] / 1000 * 389.5) / m3
mb = B['P_U3_LDRV_BRKT']['mass_g'] / 1000; xb = B['P_U3_LDRV_BRKT']['center_of_mass'][0]
W3 = 3 * m3 * G; Wb = 3 * mb * G
L_m = 537 - x3; L_b = 537 - xb
T3 = 4.5e3
r3 = {}
for cn, sfm, Fext in (('운전', 3.0, 0.0), ('오조작', 2.0, 100.0)):   # 오조작: 정비 중 모터 끝(X 400)에 100 N 아래로(M-09 기본값 가정)
    Mb = W3 * L_m + Wb * L_b + Fext * (537 - 400)
    Zwall = 2 * 8 * 90 ** 2 / 6
    s_bend = Mb / Zwall
    Fw = T3 / 98.0                                   # 비틀림 -> 옆벽 2장 반대 Z 힘(간격 98)
    s_tor = Fw * (537 - 430) / (8 * 90 ** 2 / 6)
    s_wall = s_bend + s_tor
    # 바닥판 볼트: 무게 모멘트(Y축) -> 인장, 받침 = 바닥판 아래 끝 Z -172
    zb = [-112 + 172, -152 + 172]
    T_max = Mb * zb[0] / (2 * sum(z ** 2 for z in zb))
    rg = math.hypot(38, 20)
    V = math.hypot((W3 + Wb + Fext) / 4, T3 / (4 * rg))
    # 바닥판 t8 굽힘: 옆벽 사이 띠, 볼트 인장을 판 굽힘으로(팔 = 볼트 Y 38 -> 옆벽 Y 45 : 7)
    s_plate = (T_max * 7) / (30 * 8 ** 2 / 6)
    r3[cn] = {'M_root_Nmm': round(Mb), 'sigma_wall_MPa': round(s_wall, 2), 'sf_wall': sf(RP['A6061'], s_wall),
              'sigma_base_plate_MPa': round(s_plate, 2), 'sf_plate': sf(RP['A6061'], s_plate),
              'bolt_T_max_N': round(T_max, 1), 'bolt_V_N': round(V, 1), 'sf_min': sfm}
out['U3'] = {'m_motor_coupling_kg': round(m3, 3), 'x_cg': round(x3, 1), 'm_brkt_kg': round(mb, 3), 'cases': r3}

# ---------- 4) 새 체결 (handcalc, 볼트 하나 몫 가장 불리) ----------
Bt = {}
mis = CASES['mis']; wi = CASES['whatif_mu0.8']
Bt['U5X 감속기->DRV_BRKT 웨브 M5 관통탭 물림8 SUS304'] = bolt(5, 8, max(X['오조작']['reducer_bolt']['T_each_N'], X['오조작']['reducer_bolt']['V_each_N']), 5.0, '12.9', 'SUS304', 8.5, 5.5, sf_min=2.0)
# U4 감속기 -> P_M02_FRONT 관통탭 물림8: 바퀴 힘 + 3g 무게, 토크 HG-KR23 최대 x10
V4 = math.hypot(mis['F_wheel_N'], 3 * (m_mot2 + m_red2) * G) / 4 + 22.0e3 / (4 * 35)
Bt['U4 감속기->FRONT M5 관통탭 물림8 SUS304'] = bolt(5, 8, V4, 5.0, '12.9', 'SUS304', 8.5, 5.5, sf_min=2.0)
Bt['U3 모터->브래킷 판 M5 탭 물림9 A6061'] = bolt(5, 9, max(r3['오조작']['bolt_V_N'], 50.0), 5.0, '12.9', 'A6061-T6', 8.5, 5.5, sf_min=2.0)
Bt['U3 브래킷->4080 CB5-16 + HNTT8-5 물림5(강 너트)'] = bolt(5, 5, max(r3['오조작']['bolt_T_max_N'], r3['오조작']['bolt_V_N']), 5.0, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)
Bt['U3 브래킷->4080 CB5-20 바꿈안 물림9'] = bolt(5, 9, max(r3['오조작']['bolt_T_max_N'], r3['오조작']['bolt_V_N']), 5.0, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)
Bt['피벗 끝 CB5-12 -> 핀 S45C 물림9 (축 방향 접선힘, what-if μ0.8)'] = bolt(5, 9, wi['F_tan_Y_N'], 5.0, '12.9', 'S45C', 8.5, 5.5, sf_min=2.0)
Bt['피벗 머리 CB4-12 x2 -> BASE 다리 SUS304 물림7 (부시 마찰 토크)'] = bolt(4, 7, 0.2 * 2 * CASES['mis']['F_wheel_N'] * 6 / (2 * 9), 3.0, '12.9', 'SUS304', 7.0, 4.5, sf_min=2.0)
Bt['아이들러 축 끝 CB5-12/SFB5-12 -> S45C 물림9'] = bolt(5, 9, X['오조작']['P_M03_IDLER_SHAFT(이웃, 고침)']['6200ZZ_each_N'] * 0.2, 5.0, '12.9', 'S45C', 8.5, 5.5, sf_min=2.0)
Bt['허브 끝 CB5-12 -> 감속기 축 끝 M5 물림8.5 S45C'] = bolt(5, 8.5, 0.5 * mis['F_wheel_N'], 5.0, '12.9', 'S45C', 8.5, 5.5, sf_min=2.0)
out['bolts'] = Bt

# 키: PGX 출력축 Ø16 키 5x5(키 X -123.5~-103), 허브 구멍 X -119~-96 -> 맞물림 16. 오조작 출력 HG-KR23 최대 2.2 x 10 = 22 N·m
T_k = 22.0e3; Lk = 16.0
p_h = T_k / 8 / (2.5 * Lk)
out['key_PGX_out'] = {'T_Nmm': T_k, 'L_mm': Lk, 'tau_MPa': round(T_k / 8 / (5 * Lk), 1), 'p_hub_MPa': round(p_h, 1),
                      'sf_hub_p(A6061 240)': sf(RP['A6061'], p_h), 'reducer_rated_40Nm_ratio': round(40 / 22, 2)}

os.makedirs(f'{ROOT}/fea/results', exist_ok=True)
json.dump(out, open(f'{ROOT}/fea/results/mech_MOT-01_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 15줄 요약
print('mass', out['mass']['HG-KR23_model_kg'], out['mass']['PGX62-H-10_model_kg'], out['mass']['HG-KR43_model_kg'], 'U4', out['U4_moving'])
print('cases', {k: (v['F_wheel_N'], v['F_tan_Y_N'], v['R_pivot_z_N']) for k, v in CASES.items()})
for cn in S:
    print(cn, 'pin', S[cn]['P_M02_PIVOT_PIN']['sf_root'], S[cn]['P_M02_PIVOT_PIN']['sf_tap'], 'arm', S[cn]['P_M02_ARM_SIDE_N']['sf'], S[cn]['P_M02_ARM_SIDE_N']['sf_tear(0.6Rp)'], 'base', S[cn]['P_M02_BASE_upright(이웃)']['sf'])
for cn in X:
    print('U5X', cn, X[cn]['P_M03_DRV_BRKT'], 'idl', X[cn]['P_M03_IDLER_SHAFT(이웃, 고침)']['sf'], 'rad', X[cn]['PGX62_radial']['ratio'], X[cn]['reducer_bolt'])
for cn in r3:
    print('U3', cn, r3[cn])
for k, v in Bt.items():
    print('bolt', k, v['worst'], v['ok'], v['engage_ratio'], min(v['sf_operating'].values()))
print('key', out['key_PGX_out'])
