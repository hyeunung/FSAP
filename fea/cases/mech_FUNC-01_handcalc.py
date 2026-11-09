# -*- coding: utf-8 -*-
"""FUNC-01 해석부 손계산 — U5 플로트(v2.8.0) 새 하중 부품. FEA 환경 없음(D-16) -> 손계산만.
대상: P_F01_SHAFT_HLD_N(/P 거울), P_M03_LIFT_SIDE_N/P, P_M03_LIFT_TOP + 하중 경로의 새 구매품(PSFJ16 축, LHFR16 부시,
      PSCS16 칼라, 새 체결 M4·M5).
형상: tools/out/mech_FUNC-01/stepout/*.step(bbox·원통면, 이 스크립트가 다시 읽음) + mech_FUNC-01_model.md 2-1 표(REST = LIFT 30, FLOAT 0).
좌표: REST 세계 mm. 플로트 틀(FLOAT 0) 기준 바퀴 접점 (-1800, 0, 40), 축 (-1847, +-43), 축 뿌리(옆판 플랜지 윗면) Z 136,
      부시 밑끝(승강판 윗면) Z 164(승강 틀, 플로트가 u 오르면 접점 40+u).
하중: 액추에이터 MGPM25 Ø25 공급 0.5 MPa(요구서 0-6, FUNC-01 수정 2), 작업 저항(바퀴 마찰 D-95, 서보 토크 제한),
      자중 x3 g. 판정 M-09: 운전 SF 3, 오조작 SF 2.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
out = {}
SY = {'SUS304': 205.0, 'S45C': 345.0}
SF_REQ = {'운전': 3.0, '오조작': 2.0}

# ---------- 0) STEP 형상 확인(bbox·원통면) ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
cyl = re.compile(r"#(\d+)\s*=\s*CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)")
out['step'] = {}
for n in ['P_F01_SHAFT_HLD_N', 'P_M03_LIFT_SIDE_N', 'P_M03_LIFT_SIDE_P', 'P_M03_LIFT_TOP']:
    t = open(f'{ROOT}/tools/out/mech_FUNC-01/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    pts = [p for p in pts if abs(p[0]) > 1.0]           # 원점 배치점(0,0,0) 뺌
    radii = sorted({round(float(m[2]), 2) for m in cyl.findall(t)})
    out['step'][n] = {'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)], 'cyl_radii': radii}

# ---------- 1) 무게·하중 경우 ----------
G = 9.81
W_f = 64.7                       # 플로트 CAD 무게 N (F01-M4, 계산 63.0보다 큰 쪽)
W_l = 80.9 + (64.7 - 63.0)       # 들 무게 N (수정 2 80.9 + CAD 차이)
A1, A2 = math.pi / 4 * 25 ** 2, math.pi / 4 * (25 ** 2 - 10 ** 2)
P = 0.5
F_push, F_pull = P * A1, P * A2  # 245.4, 206.2
E_CG = 30.0                      # 플로트 무게중심이 축 줄(X -1847)에서 -X로 30(가정, 서보·감속기 쪽; 부품 질량 어림 25 -> 올림. D-146 더함)
DX_W = 47.0                      # 바퀴 접점 X -1800 - 축 X -1847
YS = 43.0                        # 축 Y +-43, 간격 86
Z_C0, Z_ROOT, Z_B = 40.0, 136.0, 164.0
LB_EFF = 0.6 * 37.0              # LHFR16 몸 길이 37 중 모멘트 짝힘 팔(볼 회로 몫)
F_N_FLOAT = 48.8                 # 뜬 상태 최대 바퀴 힘(계산서 수정 2 이음매 u = t+2: F + f)
cases = {
    # 뜬 상태(u 0~20 사이, 팔이 가장 긴 u 0으로 보수): 수직은 스프링·무게·바퀴로 닫히고, 옆힘·모멘트는 축·부시
    '운전_뜸':   {'state': 'float', 'u': 0.0, 'N': F_N_FLOAT, 'Fy': 2.7 / 0.06, 'Fx': 45.0, 'Wdyn': 3 * W_f},
    # 위 기계 정지(u 20, 옆판 플랜지 윗면 = 승강판 밑면): 수직은 맞닿음, 옆힘은 보수로 모두 축·부시(맞닿음 마찰 0으로 봄)
    '운전_닿음': {'state': 'stop', 'u': 20.0, 'N': 100.0 + 2 * W_l, 'Fy': 2.7 / 0.06, 'Fx': 45.0, 'Wdyn': 0.0},
    '오조작Y':   {'state': 'stop', 'u': 20.0, 'N': F_push + 3 * W_l, 'Fy': 0.5 * (F_push + 3 * W_l), 'Fx': 0.0, 'Wdyn': 0.0},
    '오조작X':   {'state': 'stop', 'u': 20.0, 'N': F_push + 3 * W_l, 'Fy': 0.0, 'Fx': 0.5 * (F_push + 3 * W_l), 'Wdyn': 0.0},
    'whatif_mu0.8': {'state': 'stop', 'u': 20.0, 'N': F_push + 3 * W_l, 'Fy': 0.8 * (F_push + 3 * W_l), 'Fx': 0.0, 'Wdyn': 0.0},
}
def req(c): return SF_REQ['운전'] if c.startswith('운전') or c == '들기' else (SF_REQ['오조작'] if c.startswith('오조작') else None)
out['loads'] = {'W_float_N': W_f, 'W_lift_N': round(W_l, 1), 'push_0.5MPa': round(F_push, 1), 'pull_0.5MPa': round(F_pull, 1),
                'cases': {k: {kk: (round(v, 1) if isinstance(v, float) else v) for kk, v in c.items()} for k, c in cases.items()}}

def vm(s, t): return math.sqrt(s * s + 3 * t * t)
def sfv(sy, s): return round(sy / s, 2) if s > 1e-9 else 999.0

R = {}
for cn, c in cases.items():
    N, Fy, Fx, u = c['N'], c['Fy'], c['Fx'], c['u']
    zc = Z_C0 + u
    h_b = Z_B - zc              # 접점 -> 부시 밑끝
    h_r = Z_ROOT - Z_C0         # 접점 -> 축 뿌리(플로트 틀, u와 무관) 96
    vert = (N * DX_W + c['Wdyn'] * E_CG) if c['state'] == 'float' else 0.0   # 닿음이면 수직 모멘트는 맞닿음 면이 받음
    Mz = Fy * DX_W
    r = {}
    # ---- (a) 축 PSFJ16 x2: 부시 밑끝 굽힘(두 축 나눔) ----
    Mx_b, My_b = Fy * h_b, Fx * h_b + vert
    M_s = math.hypot(Mx_b, My_b) / 2
    Vx, Vy = Fx / 2 + Mz / (2 * YS), Fy / 2
    V_s = math.hypot(Vx, Vy)
    Zs = math.pi * 16 ** 3 / 32
    s_sh = M_s / Zs
    r['shaft'] = {'h_b': h_b, 'M_Nmm': round(M_s), 'V_N': round(V_s, 1), 'sigma': round(s_sh, 1), 'SF(S45C 345, 보수)': sfv(345, s_sh)}
    # ---- (b) LHFR16 부시: 반경 = 전단 + 모멘트 짝힘 ----
    F_bush = V_s + M_s / LB_EFF
    r['LHFR16'] = {'F_radial_N': round(F_bush, 1), 'C0_1180(기억값 D-146)/F': round(1180 / F_bush, 2)}
    # ---- (c) 축 받침 블록 + 옆판 플랜지(물림 20 = 플랜지 6 + 블록 14) ----
    Mx_r, My_r = Fy * h_r, Fx * h_r + vert
    M_r = math.hypot(Mx_r, My_r) / 2
    F_c = M_r / (2.0 / 3.0 * 20.0) + V_s / 2           # 물림 양끝 짝힘 + 전단 반
    p_brg = F_c / (16 * 7)                              # 끝 7 mm 몫 면압
    # 블록 바깥 띠(Y -55~-51, 두께 4, 높이 14)가 구멍 지름 16 사이에서 양끝 고정 보로 짝힘 끝 몫을 받는다(-Y로 밀 때)
    F_lig = F_c * 14.0 / 20.0
    s_lig = (F_lig * 16 / 8) / (14 * 4 ** 2 / 6)
    r['SHAFT_HLD'] = {'M_root_Nmm': round(M_r), 'F_couple_N': round(F_c, 1), 'p_bearing': round(p_brg, 1),
                      'sigma_ligament_t4': round(s_lig, 1), 'SF': sfv(205, max(s_lig, p_brg / 1.5))}
    # ---- (d) 옆판(L꼴 t6): 웨브 면 밖 굽힘(Mx 뿌리, 유효 폭 60) + 플랜지 뿌리(닿음 상태 N/2를 앞쪽 60 길이로) ----
    s_web = (Mx_r / 2) / (60 * 6 ** 2 / 6) + V_s / (60 * 6)
    if c['state'] == 'stop':
        w = (N / 2) / 60.0                                 # N/mm, 앞판 볼트 근처 60 길이로 몰림(보수)
        s_fl = (w * 18 / 2) / (6 ** 2 / 6)                 # 플랜지 폭 18 외팔, 끝 모아 반폭 9
    else:
        s_fl = 0.0
    r['LIFT_SIDE'] = {'sigma_web': round(s_web, 1), 'sigma_flange': round(s_fl, 1), 'SF': sfv(205, max(s_web, s_fl))}
    # ---- (e) 승강판 TOP t8 (U꼴: -Y 팔 Y -55~-33 X -1990~-1876 외팔 114, 다리 X -1876~-1820, +Y 팔 Y 33~78) ----
    if c['state'] == 'stop':
        q = N / 2                                         # -Y 쪽 플랜지 맞닿음 몫
        q_arm = q * 114.0 / 170.0                         # 팔 길이 몫
        bm = beam(t=8, b=22, length=114, load=q_arm / 2, e=193000, sy=205, sf_min=req(cn) or 2.0)   # 고른 분포 = 끝 하중 반
        s_arm = bm['stress_MPa']
        # 다리: -Y 몫 전부를 +Y 팔 뿌리(Y 33)까지 팔 77로 굽힘 + X 편심(팔 몫 무게중심 X -1933 -> 다리 가운데 -1848, 57)로 비틀림
        M_br = q * 77.0
        T_br = q_arm * 57.0
        s_br = M_br / (56 * 8 ** 2 / 6); t_br = T_br / (0.31 * 56 * 8 ** 2)
        # +Y 팔: 다리에서 MGP 끝판 접촉 끝(X -1893.5)까지 팔 45, -Y 몫 + +Y 몫 다리 근처 절반
        M_py = (q + q * 56.0 / 170.0) * 45.0
        s_py = M_py / (45 * 8 ** 2 / 6)
        s_top = max(s_arm, vm(s_br, t_br), s_py)
        r['LIFT_TOP'] = {'arm_beam': {'sigma': s_arm, 'defl_mm': bm['deflection_mm'], 'thin': bm['thin']},
                         'bridge_vm': round(vm(s_br, t_br), 1), 'arm_P': round(s_py, 1), 'SF': sfv(205, s_top)}
    else:
        # 뜬 상태: 부시 모멘트 M_s를 부시 플랜지(Ø48) 폭으로 판에 + 스프링 9.5 N
        s_top = M_s / (48 * 8 ** 2 / 6)
        r['LIFT_TOP'] = {'sigma_bush_moment': round(s_top, 1), 'SF': sfv(205, s_top)}
    # ---- (f) 새 체결(모델에 아직 없음, F01-D4·D5): LHFR16 플랜지 M4 x4(PCD 38, 판 t8 SUS304 탭), 블록 M5 x2(플랜지 t6 탭) ----
    F_m4 = M_s / 38.0 + V_s / 4 * 0.0                   # 짝힘 인장(전단은 마찰·끼움)
    F_m5 = M_r * (14.0 / 20.0) / 20.0                   # 블록 몫 모멘트 / 볼트 간격 20(보수 하나가 다)
    r['bolt_M4_LHFR'] = calc(d=4, le=8, load=max(F_m4, 1.0), bolt='12.9', base='SUS304', sf_min=req(cn) or 2.0)
    r['bolt_M5_HLD'] = calc(d=5, le=6, load=max(F_m5, 1.0), bolt='12.9', base='SUS304', sf_min=req(cn) or 2.0)
    R[cn] = r

# ---------- 들기(0.5 MPa 로드 쪽, 플로트 매달림 3 g) ----------
F_hang = 3 * W_f / 2                    # 칼라·축 하나 축 방향
lift = {'F_hang_per_shaft_N': round(F_hang, 1),
        'PSCS16_axial_hold(기억값 약 1000 N, D-146)/F': round(1000 / F_hang, 1),
        'M5_setscrew_hold(컵 끝 약 1000 N 기억값, D-146)/F': round(1000 / F_hang, 1),
        'shaft_tension_sigma': round(F_hang / (math.pi / 4 * 16 ** 2), 2)}
# 승강판: -Y 부시가 다리 쪽을 아래로 당김(F_hang) -> +Y 팔 뿌리까지 팔 86(축 -43 -> 33) / MGP 당김 206 N(멈춘 경우 전부)
s_lt = (F_hang * 86.0) / (56 * 8 ** 2 / 6)
s_mgp = (F_pull * 0.5 * 45.0) / (45 * 8 ** 2 / 6)
lift['LIFT_TOP_sigma'] = round(max(s_lt, s_mgp), 1); lift['LIFT_TOP_SF'] = sfv(205, max(s_lt, s_mgp))
lift['LHFR16_axial_bearing'] = '부시 몸이 칼라에 눌려 플랜지가 판을 누름(압축) — 볼트 인장 0'
R['들기'] = lift
out['results'] = R

# ---------- 옛 모델(models.json v2.1.2: 옆판 플랜지 CB5-12 x4로 TOP에 체결) 같은 하중으로 — 차이 기록용 ----
old = {}
for cn in ('운전_닿음', '오조작Y'):
    N, Fy = cases[cn]['N'], cases[cn]['Fy']
    V_n = N / 2 + Fy * (126 - 10) / 92.0
    s_ty = V_n * 84 / (100 * 8 ** 2 / 6) + 1.064 * N * 58.5 / (133 * 8 ** 2 / 6)
    V = N / 2 + Fy * (123 - 10) / 68.0
    s_side = max(V / (30 * 6) + (Fy / 2) * 25 / (60 * 6), V * 9 / (60 * 6))
    old[cn] = {'LIFT_TOP_SF_old_model': sfv(205, s_ty), 'LIFT_SIDE_SF_old_model': sfv(205, s_side),
               'note': '옛 모델의 경계(플랜지 볼트 CB5-12 x4, MGP 끝판 모서리 외팔)는 v2.8.0에 없음 — 볼트 지움·창 뚫음'}
out['old_model_same_loads'] = old

# ---------- 판정 ----------
summary = []
for cn, r in R.items():
    if cn == '들기':
        summary.append((cn, 'LIFT_TOP', r['LIFT_TOP_SF'], 3.0)); continue
    rq = req(cn)
    for part in ('shaft', 'LHFR16', 'SHAFT_HLD', 'LIFT_SIDE', 'LIFT_TOP'):
        v = r[part]
        sf = v.get('SF') or v.get('SF(S45C 345, 보수)') or v.get('C0_1180(기억값 D-146)/F')
        summary.append((cn, part, sf, rq))
    for b in ('bolt_M4_LHFR', 'bolt_M5_HLD'):
        summary.append((cn, b, min(r[b]['sf_operating'].values()), rq))
out['summary'] = [{'case': a, 'part': b, 'SF': c, 'req': d, 'ok': (d is None or c >= d), 'near(+10%)': (d is not None and d <= c < 1.1 * d)}
                  for a, b, c, d in summary]
json.dump(out, open(f'{ROOT}/fea/results/mech_FUNC-01_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
fails = [s for s in out['summary'] if not s['ok']]
print('cases', {k: (round(c['N']), round(c['Fy']), round(c['Fx'])) for k, c in cases.items()})
for cn in R:
    if cn == '들기': print('들기', R[cn]); continue
    r = R[cn]
    print(cn, 'shaft', r['shaft']['SF(S45C 345, 보수)'], 'bush', r['LHFR16']['C0_1180(기억값 D-146)/F'], 'HLD', r['SHAFT_HLD']['SF'],
          'SIDE', r['LIFT_SIDE']['SF'], 'TOP', r['LIFT_TOP']['SF'],
          'M4', min(r['bolt_M4_LHFR']['sf_operating'].values()), 'M5', min(r['bolt_M5_HLD']['sf_operating'].values()))
print('old', old)
print('fails', [(s['case'], s['part'], s['SF'], s['req']) for s in fails])
print('step', {k: (v['min'], v['max'], v['cyl_radii']) for k, v in out['step'].items()})
