# -*- coding: utf-8 -*-
"""M03 해석부 손계산 — U5 먼 쪽 바퀴 대차(v2.1.2). FEA 환경 없음(D-16) -> 손계산만.
형상: tools/out/mech_M03/stepout/*.step 꼭짓점 bbox + tools/out/mech_M03/model/changed_parts.json(REST bbox·질량)
      + changed_bolts.json(볼트 자리·물림) + mech_M03_model.md 2절 치수. 좌표는 세계 mm, U5_LIFT·U5_WHEEL은 LIFT 0 좌표.
하중(지시서): 액추에이터 추력(MGPM25 Ø25, 공급 0.5 MPa D-111), 작업 저항(바퀴 마찰 mu 0.5 D-95), 자중 x3 g. 판정 M-09: 운전 SF 3, 오조작 SF 2.
  운전  : 누름을 100 N(D-92 상한)에 맞춤 + 자중 3 g 몫(+2W) / 접선 Y = 바퀴 서보 토크 제한 2.7 N·m / r 0.06 = 45 N / X 버팀 45 N 동시
  오조작: MGP 머리 쪽 0.5 MPa 전부(245.4 N) + 3W, 토크 제한 없음 -> 접선 = mu 0.5 x 접촉력(Y 또는 X 한쪽에 전부)
  what-if mu 0.8 — 기록만
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
out = {}
SY = {'SUS304': 205.0, 'A5052': 195.0, 'S45C': 345.0, 'A6061': 240.0, 'PET-CF': 60.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0, 'S45C': 205000.0}
SF_REQ = {'운전': 3.0, '오조작': 2.0}

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
names = ['P_M03_CAR_PLATE', 'P_M03_DRV_BRKT', 'P_M03_IDLER_BRKT', 'P_M03_IDLER_SHAFT', 'P_M03_LIFT_TOP', 'P_M03_LIFT_SIDE_N',
         'P_M03_LIFT_SIDE_P', 'P_M03_FRONT', 'P_M03_CHAIN_ARM', 'P_M03_BELT_CLAMP', 'P_M03_WHEEL', 'P_M03_SNS_BRKT']
out['step_bbox'] = {}
for n in names:
    t = open(f'{ROOT}/tools/out/mech_M03/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}

# ---------- 1) 질량 (임시 강철 상자 대신 카탈로그 기억값 D-111) ----------
parts = json.load(open(f'{ROOT}/tools/out/mech_M03/model/changed_parts.json', encoding='utf-8'))
parts = parts.get('parts', parts)
plist = list(parts.values()) if isinstance(parts, dict) else parts
CAT = {'STEP대기_VRXF-PB-60-10_U5W': 1.10, 'STEP대기_MHMF022L1U2M_U5W': 0.96,
       'STEP대기_VRXF-PB-60-10_U5X': 1.10, 'STEP대기_MHMF022L1U2M_U5X': 0.96,
       'STEP대기_MGPM25-40Z_BODY': 1.45, 'STEP대기_MGPM25-40Z_PLATE': 0.55}   # MGPM25-40 전체 약 2.0 kg(기억값, D-111 계열 임시)
def mass(comps):
    mm = mc = 0.0
    for v in plist:
        if v.get('component') in comps:
            m = v.get('mass', 0) / 1000.0
            mm += m; mc += CAT.get(v['name'], m)
    return mm, mc
m_lift_mod, m_lift = mass(('U5_LIFT', 'U5_WHEEL'))
m_car_mod, m_car_only = mass(('U5_CAR',))
m_lift += 0.05                            # 케이블·센서 몫(임시)
W = m_lift * G
m_car = m_car_only + m_lift               # X로 움직이는 전체
out['mass'] = {'lift_model_kg': round(m_lift_mod, 2), 'lift_catalog_kg': round(m_lift, 2), 'car_model_kg': round(m_car_mod + m_lift_mod, 2),
               'car_catalog_kg': round(m_car, 2), 'W_lift_N': round(W, 1),
               'note': 'MGP 몸·끝판·서보·감속기는 임시 강철 상자라 모델 질량이 큼(M03-X9). 카탈로그 기억값으로 바꿔 씀'}

# ---------- 2) 하중 경우 ----------
MU = 0.5
A1, A2 = math.pi / 4 * 25 ** 2, math.pi / 4 * (25 ** 2 - 10 ** 2)    # MGPM25 머리 491, 로드 412
P_SUP = 0.5
F_push, F_pull = P_SUP * A1, P_SUP * A2
cases = {
    '운전': {'N': 100.0 + 2 * W, 'Fy': 2.7 / 0.06, 'Fx': 45.0},
    '오조작Y': {'N': F_push + 3 * W, 'Fy': MU * (F_push + 3 * W), 'Fx': 0.0},
    '오조작X': {'N': F_push + 3 * W, 'Fy': 0.0, 'Fx': MU * (F_push + 3 * W)},
    'whatif_mu0.8': {'N': F_push + 3 * W, 'Fy': 0.8 * (F_push + 3 * W), 'Fx': 0.0},
}
def req(c): return SF_REQ['운전'] if c == '운전' else (SF_REQ['오조작'] if c.startswith('오조작') else None)
out['cases'] = {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in cases.items()}
out['cylinder'] = {'A1_mm2': round(A1), 'A2_mm2': round(A2), 'push_0.5MPa_N': round(F_push, 1), 'pull_0.5MPa_N': round(F_pull, 1),
                   'lift_1g_SF(pull/(W+마찰10))': round(F_pull / (W + 10), 2), 'lift_3g_SF': round(F_pull / (3 * W + 10), 2),
                   'push_for_100N_MPa(무게 빼고)': round(max(100 - W, 0) / A1, 3), 'weight_alone_N': round(W, 1)}

P0 = (-1800.0, 0.0, 10.0)        # 바퀴 접점 LIFT 0
PM10 = (-1800.0, 0.0, 0.0)       # LIFT -10(봉 가장 길게 나옴)
R = {}

def vm(s, t): return math.sqrt(s * s + 3 * t * t)
def sfv(sy, s): return round(sy / s, 2) if s > 1e-9 else 999.0

for cn, c in cases.items():
    N, Fy, Fx = c['N'], c['Fy'], c['Fx']
    r = {}
    # ---- (a) MGP 가이드봉 Ø16 x2 (구매품 몫, 몸 밑면 Z 179에서 외팔, LIFT -10) ----
    Cr = (-1940.0, 59.0, 179.0)
    rx, ry, rz = PM10[0] - Cr[0], PM10[1] - Cr[1], PM10[2] - Cr[2]       # 140, -59, -179
    Mx = abs(ry) * N + abs(rz) * Fy            # 부호를 더하는 쪽으로(보수)
    My = abs(rz) * Fx + abs(rx) * N
    Mz = abs(rx) * Fy + abs(ry) * Fx
    Mrod = math.hypot(Mx, My) / 2 + (Mz / 50.0) * 40.0                  # 두 봉 나눔 + 비틀림 짝힘 x 나온 길이 40
    s_rod = 32 * Mrod / (math.pi * 16 ** 3)
    r['MGP_rod'] = {'M_Nmm': round(Mrod), 'sigma': round(s_rod, 1), 'SF(S45C 345 가정)': sfv(345, s_rod),
                    'tip_lateral_N(끝판에서)': round(math.hypot(Fx, Fy), 1), 'moment_at_plate_Nm': round(math.hypot(Mx, My) / 1000, 1)}
    # ---- (b) LIFT_TOP t8 SUS304 — MGP 끝판 접촉면(X -1986.5~-1893.5, Y 38~80) 모서리에서 외팔 ----
    #   Y 방향: -Y 쪽 옆판 볼트 줄 Y -46까지 팔 84, 짝힘(Fy x 116 / 92)을 더함. X 방향: 앞 볼트 X -1835까지 팔 58.5, 레버 1.064
    V_n = N / 2 + Fy * (126 - 10) / 92.0
    s_ty = V_n * 84 / (100 * 8 ** 2 / 6)                                  # 유효 폭 100(볼트 2개 사이 일부)
    s_tx = 1.064 * N * 58.5 / (133 * 8 ** 2 / 6) + Fx * (134 - 10) / (133 * 8 ** 2 / 6) * 0.0
    r['LIFT_TOP'] = {'V_side_N': round(V_n, 1), 'sigma_y': round(s_ty, 1), 'sigma_x': round(s_tx, 1), 'sigma_sum': round(s_ty + s_tx, 1),
                     'SF': sfv(205, s_ty + s_tx)}
    # ---- (c) LIFT_SIDE t6 SUS304 L (양쪽 같음, E-19 한 장) ----
    V = N / 2 + Fy * (123 - 10) / 68.0                                    # 세로 몫 + Fy 짝힘
    s_in = V / (30 * 6)                                                    # 앞 볼트 근처 유효 폭 30 인장·전단
    M_out = (Fy / 2) * (120 - 70) / 2                                     # 문틀(앞판 강체) 고정-안내 기둥
    s_out = M_out / (60 * 6 ** 2 / 6)
    M_fl = V * 9                                                           # 플랜지 뿌리 Y 37 -> 볼트 Y 46
    s_fl = M_fl / (60 * 6 ** 2 / 6)
    s_side = max(s_in + s_out, s_fl)
    r['LIFT_SIDE'] = {'V_N': round(V, 1), 'sigma_inplane': round(s_in, 1), 'sigma_out_of_plane': round(s_out, 1), 'sigma_flange': round(s_fl, 1),
                      'SF': sfv(205, s_side)}
    # ---- (d) FRONT t12 SUS304 (옆판 사이 62, 바퀴 중심 X -1800 ↔ 앞판 가운데 X -1826 = 26) ----
    Mw = math.hypot(N, Fy) * 26
    s_fr = (Mw / 2) / (80 * 12 ** 2 / 6) + math.hypot(N, Fy) * 62 / 4 / (12 * 80 ** 2 / 6)
    r['FRONT'] = {'sigma': round(s_fr, 1), 'SF': sfv(205, s_fr)}
    # ---- (e) 감속기 출력축 반경 하중 (VRXF 허용 약 490 N, D-111 임시) ----
    Frad = math.hypot(N, Fy)
    r['VRXF_radial'] = {'F_N': round(Frad, 1), 'allow_N': 490, 'ratio_allow/F': round(490 / Frad, 2)}
    # ---- (f) 볼트: TOP -> MGP 끝판 CB6 x4 (접촉 모서리 받침점법) ----
    Mxp = N * 38 + Fy * (134 - 10)
    Myp = N * 93.5 + Fx * (134 - 10)
    T_top = Mxp * 35 / (2 * (24 ** 2 + 35 ** 2)) + Myp * 87.5 / (2 * (5.5 ** 2 + 87.5 ** 2))
    #      MGP 몸 -> 대차판 CB6 x4 (면 Y 80, 윗변 Z 276 받침, LIFT -10)
    Mxb = N * 80 + Fy * (276 - 0)
    Mzb = Fy * 93.5 + Fx * 80
    T_body = Mxb * 86 / (2 * (11 ** 2 + 86 ** 2)) + Mzb * 86.5 / (2 * (6.5 ** 2 + 86.5 ** 2))
    #      옆판 플랜지 CB5-12 -> TOP (누를 때는 압축, Fy 짝힘 쪽만 당김 / 들 때 3W 매달림)
    T_fl = max(1.064 * (Fy * 113 / 68.0 - N / 2) / 1.0, 1.064 * 3 * W / 2)
    T_fl = max(T_fl, 0.0)
    #      앞판 <-> 옆판 CB5-16 (전단 위주, 바퀴 편심 모멘트 N x 26 / 30 짝힘 -> X 전단)
    Q_fr = math.hypot(N / 4, N * 26 / 30 / 2)
    r['bolts'] = {'TOP_MGP_CB6_T_N': round(T_top, 1), 'BODY_PLATE_CB6_T_N': round(T_body, 1), 'SIDE_TOP_CB5_T_N': round(T_fl, 1),
                  'FRONT_SIDE_CB5_shear_N': round(Q_fr, 1)}
    # ---- (g) 대차판 A5052 t12 — LM 블록 밑변 Z 279 단면(폭 220) ----
    Mx_p = N * 86 + Fy * (279 - 0)
    My_p = Fx * (279 - 0)                      # 면 안 굽힘(깊이 220)
    s_pl = Mx_p / (220 * 12 ** 2 / 6) + My_p / (12 * 220 ** 2 / 6)
    r['CAR_PLATE'] = {'sigma': round(s_pl, 1), 'SF': sfv(195, s_pl)}
    # ---- (h) LM 블록 SV2RL28 (구매품, 허용치 임시 C0 15 kN·MR0 150 N·m 설계안) ----
    Cb = (-1930.0, 103.0, 300.0)
    bx, by, bz = PM10[0] - Cb[0], PM10[1] - Cb[1], PM10[2] - Cb[2]
    Wc = m_car_only * G * 3
    Mroll = (abs(by) * N + abs(bz) * Fy) / 1000.0
    Myaw = (abs(bz) * Fx + abs(bx) * N) / 1000.0
    Mpitch = (abs(bx) * Fy + abs(by) * Fx) / 1000.0
    Fblk = max(N / 2 + Wc / 2 + Myaw * 1000 / 140.0, Fy / 2 + Mpitch * 1000 / 140.0)
    r['LM_block'] = {'M_roll_Nm_per_block': round(Mroll / 2, 1), 'F_block_N': round(Fblk, 1),
                     'SF_C0_15kN': round(15000 / Fblk, 1), 'SF_MR0_150Nm': round(150 / (Mroll / 2), 1)}
    # ---- (i) 바퀴 A6061 키 5x5x25 (토크) ----
    T_w = (2.7 if cn == '운전' else MU * N * 0.06 if cn.startswith('오조작') else 0.8 * N * 0.06)
    Fk = T_w * 1000 / 8.0
    r['WHEEL_key'] = {'T_Nm': round(T_w, 2), 'tau_key': round(Fk / 125, 1), 'p_hub': round(Fk / 62.5, 1), 'SF_hub(A6061 240)': sfv(240, Fk / 62.5)}
    R[cn] = r
out['lift_unit'] = R

# ---------- 3) X 구동 고정부 (벨트) ----------
T0 = 150.0                                    # 설계안 M03-F6 초기 장력 150 N/가닥(임시)
Fe_op = 61.0                                  # 설계안 x_drive F_need
Tmax_mot = 0.64 * 3 * 10 * 0.9                # MHMF022 최대 1.91 N·m(정격 x3) x 1/10 x 효율 0.9 (D-111 임시)
Fe_mis = Tmax_mot / 0.04775
belt = {'운전': 2 * T0 if Fe_op < 2 * T0 else Fe_op + 0, '오조작': max(2 * T0, Fe_mis)}
out['belt'] = {'T0_N': T0, 'Fe_op_N': Fe_op, 'Fe_mis_N': round(Fe_mis, 1), 'shaft_load_N': {k: round(v, 1) for k, v in belt.items()},
               'T1_max_N': round(max(T0 + Fe_mis / 2, Fe_mis), 1)}
X = {}
for cn, Fb in belt.items():
    x = {}
    # 아이들러 축 S45C: 웨브 면 Y 94 안쪽 M10 골지름 8.16, 벨트 중심 Y 106.5
    M_sh = Fb * (106.5 - 94)
    s_sh = M_sh / (math.pi * 8.16 ** 3 / 32)
    M_sh2 = Fb * (106.5 - 97)
    s_sh2 = M_sh2 / (math.pi * 10 ** 3 / 32)
    x['IDLER_SHAFT'] = {'M_root': round(M_sh), 'sigma_root(M10 골)': round(s_sh, 1), 'sigma_seat(Ø10, Y97)': round(s_sh2, 1),
                        'SF': sfv(345, max(s_sh, s_sh2))}
    x['6200ZZ'] = {'per_bearing_N': round(Fb / 2, 1), 'SF_C0r_2.38kN': round(2380 / (Fb / 2), 1)}
    # 브래킷 웨브 t4 (XZ 평면): 벨트 X 힘은 면 안, 축 끝 모멘트 Fb x 12.5는 다리 사이 116 고정-고정 보에 가운데 모멘트 -> 최대 M/2
    M_web = Fb * 12.5 / 2
    s_web = M_web / (120 * 4 ** 2 / 6)
    # 구동 브래킷: 서보+감속기 2.06 kg x3 g, 무게중심 웨브에서 Y 80 외팔 -> 웨브 면 밖 모멘트
    Wm = 2.06 * G * 3
    s_web_d = (Wm * 80 / 2) / (120 * 4 ** 2 / 6) + (Fb * (106.5 - 88) / 2) / (120 * 4 ** 2 / 6)
    # 다리 t4 (XY 평면, 길이 26): 무게 Z 몫 반씩 고정-안내
    s_leg = (Wm / 2 * 26 / 2) / (120 * 4 ** 2 / 6)
    x['IDLER_BRKT'] = {'sigma_web': round(s_web, 1), 'SF': sfv(205, s_web)}
    x['DRV_BRKT'] = {'sigma_web': round(s_web_d, 1), 'sigma_leg': round(s_leg, 1), 'SF': sfv(205, max(s_web_d, s_leg))}
    # 브래킷 발 볼트 CB5-16 x4 -> U1_BEAM (SS400 가정)
    T_ft = (Wm * 112) * 144 / (2 * (8 ** 2 + 144 ** 2)) + (Fb * 13.5) * 95 / (2 * (25 + 95 ** 2))
    x['bolts'] = {'foot_T_N': round(T_ft, 1), 'foot_shear_N': round(math.hypot(Fb, Wm) / 4, 1)}
    # 벨트 클램프 PET-CF: 턱 외팔(Y 92 -> 벨트 가운데 106, 팔 14), 두 턱이 반씩. 인서트 면압 OD 6.5 x 8
    M_j = Fb / 2 * 14
    s_j = M_j / (30 * 14.35 ** 2 / 6)
    p_ins = (Fb / 4) / (6.5 * 8)
    x['BELT_CLAMP'] = {'F_N': round(Fb, 1), 'sigma_jaw': round(s_j, 1), 'p_insert': round(p_ins, 2), 'SF': sfv(60, max(s_j, p_ins))}
    X[cn] = x
out['x_drive'] = X

# ---------- 4) 체인 팔 SUS304 t3 Z자 ----------
#  가동 끝 Q (-1937.5, 236.5, 845). 세운 쪽 Y 80~83 · Z 423~848 (L 425, 폭 40), 누운 쪽 Y 83 -> Q 153.5
link_kg = 0.051 / 0.046            # 링크 1개 바디 합 약 51 g / 피치 46 (changed_parts L01: 20+15+8+8) -> 1.11 kg/m
cable_kg = 0.30                    # 케이블 임시(서보 동력·엔코더·센서), D-114 새
strand = 0.733                     # 위 가닥 자유 길이
m_end = (link_kg + cable_kg) * strand / 2 + 0.03     # 반을 끝이 받음 + 실물 끝 브래킷(플라스틱) 0.03
m_chain_move = (link_kg + cable_kg) * 1.012 / 2
a_op = 1.0
a_mis = Fe_mis / m_car
CH = {'m_end_kg': round(m_end, 3), 'a_mis_mps2': round(a_mis, 1)}
for cn, a in (('운전', a_op), ('오조작', a_mis)):
    Fz = m_end * G * 3
    Fx = m_chain_move * a + 5.0                       # 관성 + 루프 굽힘 저항 5 N(임시)
    b, t, L, arm = 40.0, 3.0, 425.0, 155.0
    Zw, Zs = b * t ** 2 / 6, t * b ** 2 / 6
    s_h = Fz * 153.5 / Zw + Fx * 153.5 / Zs           # 누운 쪽 뿌리
    s_v = Fz * arm / Zw + Fx * L / Zs                 # 세운 쪽 밑동 Z 423
    tau = Fx * arm / (b * t ** 2 / 3)
    sv = vm(s_v, tau)
    I = b * t ** 3 / 12
    M1 = m_end * G * arm
    sag = M1 * L / (E['SUS304'] * I) * arm + M1 * L ** 2 / (2 * E['SUS304'] * I) * 0 + m_end * G * 153.5 ** 3 / (3 * E['SUS304'] * I)
    top_y = M1 * L ** 2 / (2 * E['SUS304'] * I)
    theta = Fx * arm * L / (77000.0 * b * t ** 3 / 3)
    k_tor = (77000.0 * b * t ** 3 / 3) / L / arm ** 2          # 끝 X 방향 강성(비틀림만) N/mm
    f_n = math.sqrt(k_tor / m_end) / (2 * math.pi) * math.sqrt(1000)
    # t5 대안
    t5 = 5.0
    s_v5 = Fz * arm / (b * t5 ** 2 / 6) + Fx * L / (t5 * b ** 2 / 6)
    tau5 = Fx * arm / (b * t5 ** 2 / 3)
    CH[cn] = {'Fz_3g_N': round(Fz, 1), 'Fx_N': round(Fx, 1), 'sigma_horiz': round(s_h, 1), 'sigma_vert_base': round(s_v, 1), 'tau_torsion': round(tau, 1),
              'sigma_vm': round(sv, 1), 'SF': sfv(205, max(sv, s_h)), 'SF_t5': sfv(205, vm(s_v5, tau5)),
              'sag_end_1g_mm': round(sag, 2), 'top_shift_y_1g_mm': round(top_y, 2), 'twist_deg': round(math.degrees(theta), 2),
              'end_x_shift_mm': round(theta * arm, 1), 'f_torsion_Hz': round(f_n, 1)}
    CH[cn]['bolts_foot_T_N'] = round((Fz * arm + Fx * 0) / 20.0 / 2 + Fz / 2, 1)
out['chain_arm'] = CH

# ---------- 5) 센서 브래킷 t2 (M02와 같은 형상) ----------
out['SNS_BRKT'] = beam(t=2, b=15, length=58, load=0.05 * G * 3, e=193000, sy=205, sf_min=3.0)

# ---------- 6) 볼트 손계산 표 ----------
B = {}
for cn, sfm in (('운전', 3.0), ('오조작', 2.0)):
    key = '운전' if cn == '운전' else '오조작Y'
    bl = R[key]['bolts']
    keyx = '운전' if cn == '운전' else '오조작X'
    blx = R[keyx]['bolts']
    T_top = max(bl['TOP_MGP_CB6_T_N'], blx['TOP_MGP_CB6_T_N'])
    T_body = max(bl['BODY_PLATE_CB6_T_N'], blx['BODY_PLATE_CB6_T_N'])
    B[cn] = {
        'G1_TOP_MGP_CB6_le12_SS400': calc(d=6, le=12, load=round(T_top, 1), torque=8.0, base='SS400', sf_min=sfm),
        'G2_BODY_PLATE_CB6_le8_A5052': calc(d=6, le=8, load=round(T_body, 1), torque=6.0, base='A5052', sf_min=sfm),
        'G3_SIDE_TOP_CB5_le6_SUS304': calc(d=5, le=6, load=max(bl['SIDE_TOP_CB5_T_N'], 1.0), torque=5.0, base='SUS304', sf_min=sfm),
        'G4_BRKT_BEAM_CB5_le8_SS400': calc(d=5, le=8, load=max(X[cn]['bolts']['foot_T_N'], 1.0), torque=5.0, base='SS400', sf_min=sfm),
        'G5_CHAIN_ARM_CB5_le9_A5052': calc(d=5, le=9, load=max(CH[cn]['bolts_foot_T_N'], 1.0), torque=4.0, base='A5052', sf_min=sfm),
    }
    B[cn]['shear_note'] = {'FRONT_SIDE_CB5_N': R[key]['bolts']['FRONT_SIDE_CB5_shear_N'],
                           'FRONT_SIDE_CB5_SF(12.9 전단 0.6x1100x14.2)': round(0.6 * 1100 * 14.2 / R[key]['bolts']['FRONT_SIDE_CB5_shear_N'], 1)}
out['bolts'] = B

# ---------- 7) 완료 판정 ② — 120x120 모서리 회전 미끄럼 SF ----------
def corner(m, a, t, d2, Np, mu=0.5, ball_mu=0.0):
    I = m * (a * a + a * a) / 3.0
    al = 4 * (math.pi / 2) / t ** 2
    T = I * al + ball_mu * m * G * 0.765 * a     # 볼 구름 저항(모서리 기준 평균 거리 0.765a)
    F = T / d2
    return {'I': round(I, 2), 'alpha': round(al, 3), 'T_Nm': round(T, 2), 'F_N': round(F, 1), 'SF': round(mu * Np / F, 2),
            'N_req_SF1.5': round(1.5 * F / mu, 1), 't_min_SF1.5_at_N100': round(math.sqrt(4 * (math.pi / 2) * I / (mu * 100 / 1.5 * d2 - ball_mu * m * G * 0.765 * a)), 2)}
CT = {
    '1200_t1.0_d0.8_N100(0-8-5 약 45 N)': corner(6.0, 1.2, 1.0, 0.8, 100),
    '1200_t1.3_d0.8_N90(설계안 채택)': corner(6.0, 1.2, 1.3, 0.8, 90),
    '1200_t1.3_d0.8_N90_볼저항0.01(what-if)': corner(6.0, 1.2, 1.3, 0.8, 90, ball_mu=0.01),
    '1500_t1.75_d1.0_N90': corner(9.375, 1.5, 1.75, 1.0, 90),
    '1200_t1.0_d0.8_N136(MGP로 낼 수 있는 누름)': corner(6.0, 1.2, 1.0, 0.8, 136),
}
CT['wheel_torque_limit_check'] = {'F_at_1.3s_N': CT['1200_t1.3_d0.8_N90(설계안 채택)']['F_N'], 'limit_N(2.7/0.06)': 45.0}
CT['press_136N_MPa'] = round(max(136 - W, 0) / A1, 3)
out['corner_torque'] = CT

# ---------- 8) 완료 판정 ③ — 들린 자세 틈 ----------
out['lift_gap'] = {'model_gap_mat_mm': 30.0, 'model_gap_tape_mm': 29.0, 'source': 'mech_M03_model.md 4절(L 12, G2 630)',
                   'sag_lifted_mm': 0.0, 'note': '들린 자세는 실린더 후퇴 끝(끝판이 몸 밑면 Z 179에 닿음) 스토퍼라 매달림 처짐이 틈을 줄이지 않음. 봉은 축 방향만'}

json.dump(out, open(f'{ROOT}/fea/results/mech_M03_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 15줄 요약 ----------
print('mass lift', out['mass']['lift_catalog_kg'], 'car', out['mass']['car_catalog_kg'], 'W', out['mass']['W_lift_N'])
print('cases', out['cases'])
for cn in ('운전', '오조작Y', '오조작X'):
    r = R[cn]
    print(cn, 'rod', r['MGP_rod']['SF(S45C 345 가정)'], 'TOP', r['LIFT_TOP']['SF'], 'SIDE', r['LIFT_SIDE']['SF'], 'FRONT', r['FRONT']['SF'],
          'PLATE', r['CAR_PLATE']['SF'], 'VRXF', r['VRXF_radial']['ratio_allow/F'], 'LM C0', r['LM_block']['SF_C0_15kN'], 'MR0', r['LM_block']['SF_MR0_150Nm'],
          'key', r['WHEEL_key']['SF_hub(A6061 240)'])
for cn in ('운전', '오조작'):
    x = X[cn]
    print(cn, 'belt', belt[cn], 'shaft', x['IDLER_SHAFT']['SF'], '6200', x['6200ZZ']['SF_C0r_2.38kN'], 'IDL', x['IDLER_BRKT']['SF'], 'DRV', x['DRV_BRKT']['SF'],
          'CLAMP', x['BELT_CLAMP']['SF'], '| chain', CH[cn]['SF'], 't5', CH[cn]['SF_t5'], 'sag', CH[cn]['sag_end_1g_mm'], 'twist', CH[cn]['twist_deg'], 'f', CH[cn]['f_torsion_Hz'])
    print('  bolts', {k: (v['worst'], min(v['sf_operating'].values())) for k, v in B[cn].items() if k != 'shear_note'}, B[cn]['shear_note'])
print('SNS', out['SNS_BRKT']['sf'], out['SNS_BRKT']['deflection_mm'])
for k, v in CT.items():
    print(k, v)
print('cyl', out['cylinder'])
