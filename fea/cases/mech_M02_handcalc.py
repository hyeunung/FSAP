# -*- coding: utf-8 -*-
"""M02 해석부 손계산 — U4 바늘 옆 바퀴(v2.1.0). FEA 환경 없음(D-16) -> 손계산만.
형상: tools/out/mech_M02/stepout/*.step 꼭짓점 bbox 확인 + tools/out/mech_M02/model/changed_parts.json(REST 자세 bbox·질량)
      + mech_M02_model.md 2절 치수 + tools/gen_v2_m02.py 볼트 좌표.
하중(지시서): 액추에이터 추력(CDM2C20 보어 Ø20, 공급 0.5 MPa D-111 — 요구서 2-4 미정), 작업 저항(바퀴 마찰 mu 0.5 D-93),
      자중 x3 g. 판정 M-09: 운전 SF 3, 오조작 SF 2(요구서 6-1 기본값).
  운전  : 레귤레이터를 누름 100 N에 맞춤(실린더 힘 F_c 계산값) + 자중 3 g, 바퀴 접선 = min(서보 토크 제한 3.5 N·m/r 0.06, mu 0.5 x F_w)
  오조작: 레귤레이터 잘못 -> 공급 0.5 MPa 전부(밀기 157.1 N) + 자중 3 g + 토크 제한 없음 -> 접선 = mu 0.5 x F_w(미끄럼 한도)
  what-if: mu 0.8(카펫 파일에 우레탄, 근거 없음) 오조작 — 기록만
좌표: 세계, J_U4_PRESS 0(누름) 자세. 피벗 (-300, Z 70), 바퀴 중심 (-100, 70), 접점 Z 10, 로드 핀 (-160, 122), 실린더 축 U0.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
out = {}

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
names = ['P_M02_BASE', 'P_M02_CYLBRKT', 'P_M02_ARM_SIDE_N', 'P_M02_ARM_SIDE_P', 'P_M02_FRONT', 'P_M02_ARM_TIE', 'P_M02_WHEEL',
         'P_M02_DISK', 'P_M02_DISK_SHAFT', 'P_M02_DISK_HSG', 'P_M02_DISK_BASE', 'P_M02_SNS_BRKT']
out['step_bbox'] = {}
for n in names:
    t = open(f'{ROOT}/tools/out/mech_M02/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = [[round(min(c), 2), round(max(c), 2)] for c in zip(*pts)]

# ---------- 1) 가동부 질량·무게중심 (REST 8.626° bbox 중심 -> 0 자세로 되돌림) ----------
parts = json.load(open(f'{ROOT}/tools/out/mech_M02/model/changed_parts.json', encoding='utf-8'))['parts']
PIV = (-300.0, 70.0)
TH_REST = math.radians(8.626)
def back(x, z):          # REST -> 0 자세 (축 -Y, + = 들림): 역회전
    dx, dz = x - PIV[0], z - PIV[1]
    c, s = math.cos(TH_REST), math.sin(TH_REST)
    return PIV[0] + dx * c + dz * s, PIV[1] - dx * s + dz * c
CAT = {'STEP대기_MHMF022L1U2M': 0.96, 'STEP대기_VRXF-PB-60-10': 1.10}   # 카탈로그 기억값(D-111). 임시 형상은 강철 상자라 무거움
mov = []
for k, v in parts.items():
    if v['component'] in ('U4_PRESS', 'U4_WHEEL') or v['name'].startswith(('CB5-16_M02_5', 'CB5-16_M02_6', 'CB5-16_M02_7', 'CB5-16_M02_8',
                                                                             'CB5-16_M02_9', 'CB5-16_M02_10', 'CB5-20', 'E32')):
        b = v['bbox']
        x, z = back((b[0] + b[1]) / 2, (b[4] + b[5]) / 2)
        mov.append((v['name'], v['mass'] / 1000.0, CAT.get(v['name'], v['mass'] / 1000.0), x, z))
def cg(idx):
    m = sum(p[idx] for p in mov)
    return m, sum(p[idx] * p[3] for p in mov) / m, sum(p[idx] * p[4] for p in mov) / m
m_cat, x_cat, z_cat = cg(2)
m_mod, x_mod, z_mod = cg(1)
m_cat += 0.03     # 센서 케이블·핀·부시 몫(임시)
out['moving'] = {'parts': [[p[0], round(p[2], 3), round(p[3], 1), round(p[4], 1)] for p in mov],
                 'catalog': {'m_kg': round(m_cat, 3), 'x_cg': round(x_cat, 1), 'z_cg': round(z_cat, 1), 'arm_from_pivot': round(x_cat - PIV[0], 1)},
                 'model_temp_shapes': {'m_kg': round(m_mod, 3), 'x_cg': round(x_mod, 1), 'arm_from_pivot': round(x_mod - PIV[0], 1)},
                 'design_basis': {'m_kg': 4.13, 'moment_Nm': 4.55}}

# ---------- 2) 실린더 크기 (완료 판정 ①) ----------
geom = json.load(open(f'{ROOT}/tools/out/mech_M02/model/geom.json', encoding='utf-8'))
u = geom['U0']; rp = geom['P0_rod_pin']
a_c = (rp[0] - PIV[0]) * u[2] - (rp[1] - PIV[1]) * u[0]        # 실린더 선 팔 (mm)
a_w = -100.0 - PIV[0]                                           # 바퀴 접점 팔 200
A_push = math.pi * 10 ** 2; A_pull = A_push - math.pi * 4 ** 2   # Ø20, 로드 Ø8
P_SUP, P_MIN = 0.5, 0.05                                        # 공급(D-111 임시), CM2 최저 사용 압력
CYL = {'arm_cyl_mm': round(a_c, 2), 'arm_wheel_mm': a_w, 'A_push_mm2': round(A_push, 1), 'A_pull_mm2': round(A_pull, 1),
       'F_push_0.5MPa_N': round(P_SUP * A_push, 1), 'F_pull_0.5MPa_N': round(P_SUP * A_pull, 1)}
for tag, m, xa in (('catalog', m_cat, x_cat - PIV[0]), ('model_temp', m_mod, x_mod - PIV[0])):
    Mw = m * G * xa                                              # N·mm, 무게 모멘트(누르는 쪽)
    r = {'weight_moment_Nm': round(Mw / 1000, 2), 'wheel_by_weight_N': round(Mw / a_w, 1)}
    for Fw in (30.0, 50.0, 100.0):
        Fc = (Fw * a_w - Mw) / a_c
        side = 'push' if Fc >= 0 else 'pull(균형)'
        p = abs(Fc) / (A_push if Fc >= 0 else A_pull)
        r[f'press_{int(Fw)}N'] = {'F_cyl_N': round(Fc, 1), 'side': side, 'p_MPa': round(p, 3), 'p_below_min_0.05': p < P_MIN,
                                  'sf_vs_supply': round(P_SUP / p, 2) if p else None}
    # 들기: 3 g 로 들어 올림(가속 포함) — 당김으로 무게 모멘트를 이김
    for gmul in (1, 3):
        Fl = gmul * Mw / a_c
        r[f'lift_{gmul}g'] = {'F_pull_N': round(Fl, 1), 'p_MPa': round(Fl / A_pull, 3), 'sf_vs_0.5MPa': round(P_SUP * A_pull / Fl, 2)}
    # 0.5 MPa 전부로 누를 때 바퀴 힘
    r['wheel_at_full_supply_1g_N'] = round((P_SUP * A_push * a_c + Mw) / a_w, 1)
    r['wheel_at_full_supply_3g_N'] = round((P_SUP * A_push * a_c + 3 * Mw) / a_w, 1)
    CYL[tag] = r
# 좌굴(로드 Ø8, 핀 사이 늘어난 길이 183.5 + 25)
I_rod = math.pi * 8 ** 4 / 64
L_pp = 183.5 + 25
CYL['buckling'] = {'P_euler_N': round(math.pi ** 2 * 205000 * I_rod / L_pp ** 2), 'sf': round(math.pi ** 2 * 205000 * I_rod / L_pp ** 2 / (P_SUP * A_push), 1)}
# 들림 끝 충돌 에너지(실린더 후퇴 끝이 멈춤): 레버 관성을 피스톤 쪽으로 환산
J_lev = sum(p[2] * ((p[3] - PIV[0]) ** 2 + (p[4] - PIV[1]) ** 2) for p in mov) * 1e-6 + 0.02   # kg·m² (+ 부품 자체 관성 몫 임시)
m_eq = J_lev / (a_c / 1000) ** 2
CYL['stroke_end'] = {'J_lever_kgm2': round(J_lev, 4), 'm_equiv_at_piston_kg': round(m_eq, 2),
                     'KE_J_at': {f'{v}mm/s': round(0.5 * m_eq * (v / 1000) ** 2, 3) for v in (100, 200, 300, 500)},
                     'note': 'CM2 Ø20 허용 운동 에너지는 카탈로그 확인 필요(기억값 약 0.27 J, 고무 쿠션) — 속도 제어로 맞춤'}
out['cylinder'] = CYL

# ---------- 3) 작은 매트 모서리 회전 토크 (완료 판정 ②, 0-8-5) ----------
rho_a = 6.0 / 1.44
a, b = 0.300, 0.200
m_s = rho_a * a * b
I_c = m_s * (a * a + b * b) / 3
# 모서리 중심 평균 거리(수치 적분)
n = 200; rs = 0.0
for i in range(n):
    for j in range(n):
        rs += math.hypot((i + 0.5) * a / n, (j + 0.5) * b / n)
r_mean = rs / n / n
mu_ball = 0.05
J_disk = 0.5 * 1.564 * 0.125 ** 2 + 0.5 * 0.274 * 0.010 ** 2      # 원판 + 축 (kg·m²)
r_d = 0.075                                                       # 원판 중심(-175) -> 바퀴 접점(-100)
d1 = 0.100
J_wheel = 0.5 * 0.635 * 0.06 ** 2                                 # 허브 + 트레드
J_rotor, ratio, eta = 0.14e-4, 10.0, 0.9
SM = {'m_kg': round(m_s, 3), 'I_corner_kgm2': round(I_c, 5), 'r_mean_m': round(r_mean, 4), 'J_disk_kgm2': round(J_disk, 5)}
for t in (0.5, 1.0):
    alpha = 4 * (math.pi / 2) / t ** 2                           # 삼각 속도 90°
    T_in = I_c * alpha
    T_f = mu_ball * m_s * G * r_mean
    F_mat = (T_in + T_f) / d1
    a_t = alpha * d1                                              # 바퀴 접점 접선 가속 m/s²
    F_disk = J_disk * (a_t / r_d) / r_d                           # 원판을 같이 돌리는 힘
    F_tot = F_mat + F_disk
    T_wheel_shaft = F_tot * 0.06 + J_wheel * a_t / 0.06 + J_rotor * ratio ** 2 * a_t / 0.06
    T_motor = T_wheel_shaft / ratio / eta
    r = {'alpha_rad_s2': round(alpha, 2), 'T_mat_inertia_Nm': round(T_in, 4), 'T_ball_Nm': round(T_f, 4),
         'F_wheel_mat_only_N': round(F_mat, 2), 'F_wheel_disk_N': round(F_disk, 2), 'F_wheel_total_N': round(F_tot, 2),
         'T_wheel_shaft_Nm': round(T_wheel_shaft, 3), 'T_motor_Nm': round(T_motor, 4), 'motor_rated_0.64_sf': round(0.64 / T_motor, 1)}
    for P in (30.0, 50.0, 100.0):
        r[f'slip_sf_press{int(P)}N_mu0.5'] = round(0.5 * P / F_tot, 2)
        r[f'slip_sf_press{int(P)}N_mat_only'] = round(0.5 * P / F_mat, 2)
    # 30 N 누름에서 슬립 SF 3이 되는 최소 회전 시간
    SM[f't{t}s'] = r
# 30 N 누름·SF 3 이 되는 시간(이분법)
def ftot(t):
    al = 4 * (math.pi / 2) / t ** 2
    return (I_c * al + mu_ball * m_s * G * r_mean) / d1 + J_disk * (al * d1 / r_d) / r_d
lo, hi = 0.2, 3.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (lo, mid) if 15.0 / ftot(mid) >= 3.0 else (mid, hi)
SM['t_min_for_sf3_at_30N_s'] = round(hi, 3)
out['small_mat_corner'] = SM

# ---------- 4) 하중 경우 ----------
Mw1 = m_cat * G * (x_cat - PIV[0])
CASES = {}
for case, Fc, gmul, mu, tlim, sfm in (('run', None, 3, 0.5, 3.5, 3.0), ('mis', P_SUP * A_push, 3, 0.5, None, 2.0),
                                      ('whatif_mu0.8', P_SUP * A_push, 3, 0.8, None, 2.0)):
    if Fc is None:
        Fc = (100.0 * a_w - Mw1) / a_c                            # 100 N 에 맞춘 레귤레이터
    Fw = (Fc * a_c + gmul * Mw1) / a_w
    Ft = mu * Fw if tlim is None else min(tlim / 0.06, mu * Fw)
    W = gmul * m_cat * G
    Rz = Fc + W - Fw                                              # 피벗이 레버를 위로 받치는 힘
    CASES[case] = {'F_cyl_N': round(Fc, 1), 'F_wheel_N': round(Fw, 1), 'F_tan_Y_N': round(Ft, 1), 'W_N': round(W, 1),
                   'R_pivot_z_N': round(Rz, 1), 'sf_min': sfm}
out['cases'] = CASES

E_S, RP_S, G_S = 193000.0, 205.0, 74000.0
E_C, RP_C = 205000.0, 345.0
E_A, RP_A = 70000.0, 195.0
S = {}
for case, c in CASES.items():
    Fw, Ft, Rz, Fc, sfm = c['F_wheel_N'], c['F_tan_Y_N'], c['R_pivot_z_N'], c['F_cyl_N'], c['sf_min']
    r = {}
    # --- 피벗 핀 Ø12 S45C: 받침 BASE 세운 다리 면 Y -52, 부시 Y -34(18)·+34(86), 간격 68
    Mx = Ft * (70 - 10)               # 접선 Y 힘 x 높이(접점 Z 10 -> 피벗 Z 70): X축 둘레
    Mz = Ft * a_w                     # 접선 Y 힘 x 팔 200: Z축 둘레
    M_pin = math.hypot(abs(Rz) * (18 + 86) / 2 + Mx * (86 - 18) / 68, Mz * (86 - 18) / 68)
    Zp = math.pi * 12 ** 3 / 32
    s = M_pin / Zp
    r['pivot_pin'] = {'M_root_Nmm': round(M_pin), 'stress_MPa': round(s, 1), 'sf': round(RP_C / s, 2), 'ok': RP_C / s >= sfm,
                      'near_10pct': sfm <= RP_C / s < 1.1 * sfm}
    # --- BASE 세운 다리 (X 45 x Y t8, 피벗 Z 70 -> 굽힘 Z 242, 172): 밖으로 굽힘(Y 힘 + 핀 모멘트 X축) + 비틀림(Z축)
    b_l, t_l, L_l = 45.0, 8.0, 172.0
    Zl = b_l * t_l ** 2 / 6
    M_out = Ft * (242 - 10) + abs(Rz) * 56     # Y 힘(접점에서) + 핀 Z 힘 x 핀 중간까지 팔(세운 다리 가운데 Y -56 -> 핀 하중 중심 Y 0)
    s_b = M_out / Zl
    alpha_t = 0.291                            # b/t 5.6
    tau = Mz / (alpha_t * b_l * t_l ** 2)
    s_eq = math.sqrt(s_b ** 2 + 3 * tau ** 2)
    r['base_upright'] = {'M_out_Nmm': round(M_out), 'sigma_MPa': round(s_b, 1), 'tau_MPa': round(tau, 1), 'sigma_eq_MPa': round(s_eq, 1),
                         'sf': round(RP_S / s_eq, 2), 'ok': RP_S / s_eq >= sfm, 'near_10pct': sfm <= RP_S / s_eq < 1.1 * sfm}
    # --- BASE 누운 다리: 보 앞면 Y 120에서 외팔, 실린더 반력 Y 0 (팔 120) 위로, 피벗 Y -56 (팔 176) 아래로 / X축 둘레 + Y축 비틀림
    M_root = abs(Fc * 120 - Rz * 176) + Ft * (246 - 10)
    Zh = (190 - 34) * 8 ** 2 / 6               # 실린더 장공 34 뺌
    T_y = Fc * abs(-162 - (-235)) + abs(Rz) * abs(-300 - (-235))
    tau_h = T_y / (0.32 * 190 * 8 ** 2)
    s_h = math.sqrt((M_root / Zh) ** 2 + 3 * tau_h ** 2)
    r['base_shelf'] = {'M_root_Nmm': round(M_root), 'T_y_Nmm': round(T_y), 'sigma_eq_MPa': round(s_h, 1), 'sf': round(RP_S / s_h, 2), 'ok': RP_S / s_h >= sfm}
    # --- CYLBRKT 귀 2장 (X 20 x t4, 구멍 Ø9): 밀기 반력 -> 귀 인장, 당김(들기 막힘 131.9) -> 압축·좌굴
    Ft_ear = Fc / 2
    s_ear = Ft_ear / ((20 - 9) * 4)
    tear = Ft_ear / (2 * (336 - 325.72 - 4.5) * 4)   # 핀 위 살(귀 끝 Z 336)
    P_cr = math.pi ** 2 * E_S * (20 * 4 ** 3 / 12) / (4 * (325.72 - 254) ** 2)
    r['cylbrkt_ears'] = {'tension_MPa': round(s_ear, 1), 'tearout_MPa': round(tear, 1), 'sf_tear(0.6Rp)': round(0.6 * RP_S / tear, 1),
                         'buckling_sf_pull_0.5MPa': round(P_cr / (P_SUP * A_pull / 2), 1)}
    # --- 옆판 2장 t6: 로드 핀 단면 X -160 (Z 40~117.5만, 구멍 위 살 무시) 굽힘 = 바퀴 힘 x 60
    Ms = Fw * 60 / 2
    Zs = 6 * 77.5 ** 2 / 6
    r['arm_side'] = {'M_each_Nmm': round(Ms), 'stress_MPa': round(Ms / Zs, 2), 'sf': round(RP_S / (Ms / Zs), 1),
                     'rod_pin_bearing_MPa': round(Fc / 2 / (9 * 6), 2), 'pivot_bush_axial_each_N': round(Mz / 68, 1)}
    # --- 앞판 t12: 옆판 사이 62 단순 지지, 바퀴 힘 + 서보·감속기 3 g, 단면 Z 높이 80 - 축 구멍 18
    P_f = Fw + 3 * 2.06 * G
    Mf = P_f * 62 / 4
    Zf = 12 * (80 - 18) ** 2 / 6
    r['front'] = {'M_Nmm': round(Mf), 'stress_MPa': round(Mf / Zf, 2), 'sf': round(RP_S / (Mf / Zf), 1)}
    # --- 원판 A5052 t12: 축 플랜지 r 25 에서 외팔, 하중 r 75 (팔 50), 유효 폭 100(보수)
    Md = Fw * 50
    s_d = 6 * Md / (100 * 12 ** 2)
    dd = Fw * 50 ** 3 / (3 * E_A * 100 * 12 ** 3 / 12)
    r['disk'] = {'stress_MPa': round(s_d, 1), 'sf': round(RP_A / s_d, 1), 'defl_mm': round(dd, 4)}
    # --- 원판 축 Ø20 S45C + 6004ZZ ×2 (중심 Z -30·-50, 간격 20): 누름 Fw at r 75, 마찰 0.5 Fw at Z 0
    Fh = 0.5 * Fw
    M_sh = math.hypot(Fw * 75, Fh * 30)
    s_sh = M_sh / (math.pi * 20 ** 3 / 32)
    R_up = math.hypot(Fw * 75 / 20, Fh * 50 / 20)
    P0 = max(R_up, 0.6 * R_up + 0.5 * Fw)
    r['disk_shaft'] = {'stress_MPa': round(s_sh, 1), 'sf': round(RP_C / s_sh, 1)}
    r['bearing_6004ZZ'] = {'R_upper_N': round(R_up), 'Fa_N': round(Fw), 'P0_N': round(P0), 'C0r_N': 5000, 'sf_static': round(5000 / P0, 1)}
    # --- 받침판 SUS304 t8 (볼트 X 스팬 220, 유효 폭 100 보수): 하우징 중앙 하중 + 모멘트
    Mb = Fw * 220 / 4 + M_sh / 2
    s_b2 = Mb / (100 * 8 ** 2 / 6)
    db = Fw * 220 ** 3 / (48 * E_S * 100 * 8 ** 3 / 12)
    r['disk_base'] = {'stress_MPa': round(s_b2, 1), 'sf': round(RP_S / s_b2, 1), 'defl_mm': round(db, 4)}
    # --- 바퀴 허브 A6061: 토크 전달(키 5x5 가정 — 체결 방식 미정 M02-X5)
    Tq = Ft * 0.06 * 1000
    r['wheel_hub_key_assumed'] = {'torque_Nmm': round(Tq), 'key_force_N': round(Tq / 8), 'key_bearing_MPa(A6061, h/2 2.5 x L 25)': round(Tq / 8 / (2.5 * 25), 1)}
    S[case] = r
out['strength'] = S

# ---------- 5) 센서 브래킷 t2 (얇은 판, beam 먼저) ----------
m_sns = 0.05   # 머리 + 케이블 몫(임시)
out['sns_brkt'] = {'beam_3g': beam(t=2.0, b=17.0, length=58.0, load=3 * m_sns * G, e=E_S, sy=RP_S, sf_min=3.0)}
k_s = out['sns_brkt']['beam_3g']['stiffness_N_mm'] * 1000
out['sns_brkt']['f_Hz'] = round(math.sqrt(k_s / m_sns) / (2 * math.pi), 1)

# ---------- 6) 바퀴 접선(Y) 강성·흔들림 — 운전 경우 ----------
c = CASES['run']; Ft = c['F_tan_Y_N']
EIp = E_C * math.pi * 12 ** 4 / 64
Mz = Ft * a_w
yaw_pin = 2765.0 * (Mz / 68) / EIp                  # 핀 두 부시 짝힘 처짐 차 / 68
J_leg = 0.291 * 45 * 8 ** 3
yaw_leg = Mz * 172 / (G_S * J_leg)                  # 세운 다리 비틀림
I_leg = 45 * 8 ** 3 / 12
EI_l = E_S * I_leg
M0 = Ft * 60
dy_leg = Ft * 172 ** 3 / (3 * EI_l) + M0 * 172 ** 2 / (2 * EI_l) + (Ft * 172 ** 2 / (2 * EI_l) + M0 * 172 / EI_l) * 60
dy = (yaw_pin + yaw_leg) * 200 + dy_leg
k_y = Ft / dy
J_yaw = sum(p[2] * ((p[3] - PIV[0]) ** 2) for p in mov) * 1e-6 + 0.01
k_th = Ft * a_w / 1000 / (yaw_pin + yaw_leg)      # N·m/rad
F_op = SM['t0.5s']['F_wheel_total_N']
out['wheel_lateral'] = {'F_tan_N': Ft, 'yaw_pin_rad': round(yaw_pin, 5), 'yaw_leg_rad': round(yaw_leg, 5), 'dy_leg_bend_mm': round(dy_leg, 3),
                        'dy_wheel_mm': round(dy, 3), 'k_y_N_mm': round(k_y, 1),
                        'dy_at_corner_force_mm': round(F_op / k_y, 3),
                        'yaw_k_Nm_rad': round(k_th), 'J_yaw_kgm2': round(J_yaw, 4),
                        'f_yaw_Hz': round(math.sqrt(k_th / J_yaw) / (2 * math.pi), 1), 'stitch_Hz_1500_3000spm': [25, 50],
                        'note': '부시 틈·볼트 미끄럼 제외(더 무름)'}

# ---------- 7) 볼트 (E-19 묶음별 가장 불리한 하나) ----------
B = {}
for case, cc in CASES.items():
    if case.startswith('whatif'):
        continue
    sfm = cc['sf_min']; Fw, Ft, Fc, Rz = cc['F_wheel_N'], cc['F_tan_Y_N'], cc['F_cyl_N'], cc['R_pivot_z_N']
    # G1 BASE -> U1_BEAM 4 (Y 140·180, X -310·-160): 받침 모서리 Y 120 둘레 X축 모멘트 + Y축 비틀림(X 짝 150)
    Mx_b = abs(Fc * 120 - Rz * 176) + Ft * (246 - 10)
    T1 = Mx_b * 60 / (2 * 20 ** 2 + 2 * 60 ** 2)
    T_y = Fc * 73 + abs(Rz) * 65
    T1 += T_y / 150 / 2
    B[f'G1_base_beam_{case}'] = {'load_N': round(T1, 1), 'le8_SS400_5Nm': calc(d=5, le=8, load=round(T1, 1), torque=5.0, base='SS400', sf_min=sfm),
                                 'le6_tube_5Nm': calc(d=5, le=6, load=round(T1, 1), torque=5.0, base='SS400', sf_min=sfm)}
    # G4 하우징 -> 받침판 4 (P.C.D 76, 플랜지 Ø90 모서리 받침): 매달린 하중 Fw/4 + 모멘트
    Mh = math.hypot(Fw * 75, 0.5 * Fw * 30)
    ys = [45 + 38 * math.cos(math.radians(a_)) for a_ in (0, 90, 180, 270)]
    T4 = Fw / 4 + Mh * max(ys) / sum(y * y for y in ys)
    B[f'G4_hsg_base_{case}'] = calc(d=5, le=8, load=round(T4, 1), torque=5.0, base='SUS304', sf_min=sfm)
    # G5 받침판 -> U2_PLATE 4 (X 스팬 220, Y 240): 매달린 하중 + 모멘트 (U2_PLATE 재질 미정 -> A5052)
    T5 = Fw / 4 + Mh / 220 / 2
    B[f'G5_dbase_plate_{case}'] = calc(d=5, le=8, load=round(T5, 1), torque=5.0, base='A5052', sf_min=sfm)
    # G6 원판 -> 축 플랜지 3 (r 18, 플랜지 r 25 모서리): 누름은 압축, 편심 모멘트로 들림 쪽 인장
    Md = Fw * 75
    T6 = Md * (25 + 18) / ((25 + 18) ** 2 + 2 * (25 - 9) ** 2)
    B[f'G6_disk_shaft_{case}'] = calc(d=5, le=9.5, load=round(T6, 1), torque=5.0, base='S45C', sf_min=sfm)
    # G8 실린더 브래킷 -> BASE CB5-12 2: 밀기 반력 위로 = 볼트 인장 Fc/2 + 지렛대 1.5
    B[f'G8_cylbrkt_base_{case}'] = calc(d=5, le=8, load=round(Fc / 2 * 1.5, 1), torque=5.0, base='SUS304', sf_min=sfm)
    # G2 옆판 -> 앞판 4 (Y 방향, 앞판 SUS304 탭 le 10): 축방향 = Z축 모멘트 짝(26 x Ft / 62 간격, X 짝)… 주로 전단 -> 미끄럼
    shear2 = math.hypot(Fw + 3 * 2.06 * G, Ft) / 4 + (Ft * 0.06 * 1000 + Ft * 60) / 30 / 2
    B[f'G2_side_front_{case}'] = {'shear_each_N': round(shear2, 1), 'slip_sf_5Nm_mu0.15': round(5000 * 0.15 / shear2, 1),
                                  'axial_check': calc(d=5, le=10, load=round(Ft * 26 / 62, 1) or 1.0, torque=5.0, base='SUS304', sf_min=sfm)}
    # G7 감속기 -> 앞판 CB5-20 4 (감속기 플랜지 탭 알루미늄 가정 le 8): 들린 상태 서보·감속기 3 g 외팔 + 바퀴 힘
    Mg = max(3 * 2.06 * G * 78, abs(Fw * 32 - 3 * 2.06 * G * 78))
    T7 = Mg / (2 * 49.5)
    B[f'G7_gear_front_{case}'] = calc(d=5, le=8, load=round(T7, 1), torque=5.0, base='A5052', sf_min=sfm)
# 조임 토크 7 N·m(M01과 같은 값)일 때 탭 암나사(가장 약한 A5052 le 8)
B['torque7_A5052_le8'] = calc(d=5, le=8, load=100.0, torque=7.0, base='A5052', sf_min=3.0)
B['torque7_A5052_le10_tie'] = calc(d=5, le=10, load=50.0, torque=7.0, base='A5052', sf_min=3.0)
out['bolts'] = B

# ---------- 8) 과사양(M-09: 필요 SF의 3배 이상) — note ----------
over = []
for k, v in S['run'].items():
    sf = v.get('sf')
    if isinstance(sf, (int, float)) and sf >= 9.0:
        over.append([k, sf])
out['overspec_run_sf_ge_9'] = over

json.dump(out, open(f'{ROOT}/fea/results/mech_M02_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 화면 요약
print('moving', out['moving']['catalog'], out['moving']['model_temp_shapes'])
print('cyl arm', CYL['arm_cyl_mm'], 'cat', {k: v for k, v in CYL['catalog'].items() if k.startswith(('press', 'lift', 'wheel'))})
print('cyl model_temp press100', CYL['model_temp']['press_100N'], 'press30', CYL['model_temp']['press_30N'], 'lift3g', CYL['model_temp']['lift_3g'])
print('buck', CYL['buckling'], 'end', CYL['stroke_end']['KE_J_at'], CYL['stroke_end']['m_equiv_at_piston_kg'])
print('corner 0.5', SM['t0.5s']); print('corner 1', SM['t1.0s']); print('tmin', SM['t_min_for_sf3_at_30N_s'])
print('cases', CASES)
for cs in S:
    print(cs, {k: (v.get('sf'), v.get('sf_static'), v.get('stress_MPa')) for k, v in S[cs].items()})
print('sns', out['sns_brkt']['beam_3g']['sf'], out['sns_brkt']['f_Hz'])
print('lat', out['wheel_lateral'])
for k, v in B.items():
    vv = v if 'worst' in v else (v.get('le8_SS400_5Nm') or v.get('axial_check') or v)
    print(k, v.get('load_N', v.get('shear_each_N', '')), vv.get('worst') if isinstance(vv, dict) else '', vv.get('ok') if isinstance(vv, dict) else '',
          vv.get('sf_operating') if isinstance(vv, dict) else '', vv.get('sf_tightening') if isinstance(vv, dict) else '', v.get('slip_sf_5Nm_mu0.15', ''))
print('step', out['step_bbox'])
print('over', over)
