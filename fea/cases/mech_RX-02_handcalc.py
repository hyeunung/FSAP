# RX-02 바늘 냉각 공기 노즐 — 손계산(E-18, FEA 환경 없음 D-16)
# 대상: P_RX02_NOZ_PIPE(SUS304 관 Ø4×0.5), P_RX02_NOZ_BLK_MILL(A5052 블록), CB5-20 ×2, M5 이음 탭
# 형상: 모델링 보고서 mech_RX-02_model.md 3-1절 + STEP 꼭짓점 bbox(아래에서 다시 잼)
import json, math, re, subprocess, sys, os

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine'
OUT = ROOT + '/fea/results/mech_RX-02_handcalc.json'


def step_bbox(p):
    xs, ys, zs = [], [], []
    pat = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)")
    with open(p, encoding='utf-8', errors='ignore') as f:
        for m in pat.finditer(f.read()):
            x, y, z = map(float, m.groups())
            xs.append(x); ys.append(y); zs.append(z)
    return {'n_pts': len(xs), 'min': [min(xs), min(ys), min(zs)], 'max': [max(xs), max(ys), max(zs)]} if xs else None


def hc(args):
    r = subprocess.run([sys.executable, '-B', ENG + '/engine/tools/handcalc.py'] + args, capture_output=True, text=True, encoding='utf-8')
    return json.loads(r.stdout)


res = {'bbox': {}}
for n in ['P_RX02_NOZ_BLK_MILL', 'P_RX02_NOZ_PIPE']:
    res['bbox'][n] = step_bbox(f'{ROOT}/tools/out/mech_RX-02/stepout/{n}.step')

# ---- 노즐 관 단면
D, d = 4.0, 3.0
A = math.pi * (D ** 2 - d ** 2) / 4          # 5.498 mm²
I = math.pi * (D ** 4 - d ** 4) / 64          # 8.590 mm⁴
Z = I / (D / 2)
E, SY, RHO = 193000.0, 205.0, 7.93e-9         # SUS304 MPa, MPa, t/mm³
root = (30.0, 30.0, 105.0)                    # 블록 밑면(관이 나오는 곳) — 모델 끼움 Z 105~109
bend = (30.0, 30.0, 62.5)
tip = (11.0, 11.0, 35.6)
u = (-0.5, -0.5, -math.sqrt(0.5))             # 분사 방향
r = [t - s for t, s in zip(tip, root)]
rl = math.sqrt(sum(c * c for c in r))
ru = sum(a * b for a, b in zip(r, u))
arm_jet = math.sqrt(max(rl ** 2 - ru ** 2, 0))
# 운전: 분사 반력 상한 — 공급압 0.5 MPa(요구서 2-4 운전 압력 상한 쪽)가 관 안 단면 전체에 걸린다고 봄(속도 조절 이음 무시, 보수)
P = 0.5
F_jet = P * math.pi * d ** 2 / 4              # 3.53 N
M_jet = F_jet * arm_jet
s_jet = M_jet / Z
hoop = P * d / (2 * 0.5)
# 자중 ×3 g
m_pipe = RHO * A * 84.1                       # t
F_g = m_pipe * 9810 * 3
M_g = F_g * math.hypot(r[0], r[1]) / 2        # 무게중심 팔 ≈ 수평 거리 절반(보수)
s_op = (M_jet + M_g) / Z
# 오조작: 끝을 손으로 옆으로 10 N(설계안 가정), 팔 = 뿌리–끝 전체 거리
F_hand = 10.0
M_hand = F_hand * rl
s_hand = M_hand / Z
F_hand_yield = SY * Z / rl                    # 굽기 시작하는 힘
F_hand_sf2 = F_hand_yield / 2
# 굽힘 R10: 바깥 섬유 변형률
R_bend = 10.0
eps_bend = (D / 2) / R_bend
t_out = 0.5 / (1 + eps_bend)
# 고유 진동(외팔, 펼친 길이: 블록 밖 길이)
L_out = 84.1 - 4.0
mpl = RHO * A
f1 = (1.875 ** 2 / (2 * math.pi)) * math.sqrt(E * I / (mpl * L_out ** 4))
f1_cons = (1.875 ** 2 / (2 * math.pi)) * math.sqrt(E * I / (mpl * 107.0 ** 4))
f_exc = 3000 / 60
# 끝 처짐(분사 반력, 직선 외팔 펼친 길이 근사)
defl_jet = F_jet * L_out ** 3 / (3 * E * I)
# 소켓 끼움 받침 압력(끼움 깊이 Le, 강체 소켓 선형 분포)
Le = 4.0
p_sock_jet = 6 * M_jet / (D * Le ** 2) + F_jet / (D * Le)
p_sock_hand = 6 * M_hand / (D * Le ** 2) + F_hand / (D * Le)
pG_A5052 = 210.0
# 굽은 관이 스스로 굽기 전에 블록 소켓이 먼저 눌리나(굽기 시작 힘에서)
p_sock_yield = 6 * F_hand_yield * rl / (D * Le ** 2) + F_hand_yield / (D * Le)

res['pipe'] = {
    'A_mm2': round(A, 3), 'I_mm4': round(I, 3), 'Z_mm3': round(Z, 3), 'L_centerline': 84.1, 'L_out_of_block': L_out,
    'root_tip_dist': round(rl, 2), 'arm_jet_mm': round(arm_jet, 2),
    'op': {'F_jet_N': round(F_jet, 3), 'M_jet_Nmm': round(M_jet, 1), 'F_selfweight3g_N': round(F_g, 4), 'M_g_Nmm': round(M_g, 3),
           'sigma_MPa': round(s_op, 2), 'sf': round(SY / s_op, 2), 'sf_req': 3, 'overspec_limit': 9,
           'hoop_MPa': round(hoop, 2), 'sf_hoop': round(SY / hoop, 1), 'tip_defl_mm': round(defl_jet, 4)},
    'misuse': {'F_N': F_hand, 'M_Nmm': round(M_hand, 1), 'sigma_MPa': round(s_hand, 1), 'sf': round(SY / s_hand, 2), 'sf_req': 2,
               'F_first_yield_N': round(F_hand_yield, 2), 'F_for_sf2_N': round(F_hand_sf2, 2)},
    'bend': {'R': R_bend, 'R_over_D': R_bend / D, 'outer_strain': round(eps_bend, 3), 'wall_outer_after_mm': round(t_out, 3), 'SUS304_elong_min': 0.40},
    'vib': {'f1_Hz_Lout': round(f1, 0), 'f1_Hz_L107': round(f1_cons, 0), 'excite_Hz': f_exc, 'ratio': round(f1 / f_exc, 1)},
    'socket': {'Le_mm': Le, 'p_jet_MPa': round(p_sock_jet, 2), 'sf_jet': round(pG_A5052 / p_sock_jet, 1),
               'p_hand10N_MPa': round(p_sock_hand, 1), 'sf_hand10N': round(pG_A5052 / p_sock_hand, 2),
               'p_at_pipe_yield_MPa': round(p_sock_yield, 1)},
}

# ---- 블록 · 볼트
# 관 당김(Ø6 우레탄 관 흔들림 ≤ 20 N, 설계안 가정) + 블록 36.5 g·관·이음 ×3 g, 지렛대: 하중이 엘보 관 축 X 57.5(볼트 줄 X 23에서 34.5)·Z 110(암 밑 Z 125에서 15)
F_tube = 20.0
m_blk = 0.0365 + 0.0037 + 0.010               # 블록 + 노즐 관 + 이음(임시 10 g)
F_w = m_blk * 9.81 * 3
# 가장 불리: 관 당김이 아래(−Z)로 X 57.5에서 → 볼트 두 개(X 23)가 당겨짐, 받침점 블록 −X 끝 X 16? 아님: 당김이 +X 쪽이면 받침점은 +X 모서리 X 44
# 당김 −Z at X 57.5: 블록 +X 모서리 X 44에 받침, 볼트 X 23까지 팔 21, 하중 팔 13.5 → 볼트 합 = F·13.5/21 + 직접
F_bolts = (F_tube + F_w) * (1 + 13.5 / 21.0)
F_per = F_bolts / 2
# 옆(Y) 당김 → 볼트 줄(Y 23·37 한 줄 X 23) 둘레 비틀림: 마찰로 받음
res['block'] = {'F_tube_N': F_tube, 'F_w3g_N': round(F_w, 3), 'F_bolt_each_N': round(F_per, 2)}
res['CB5-20_into_head'] = hc(['--d', '5', '--pitch', '0.8', '--le', '10', '--load', f'{F_per:.2f}', '--torque', '4.5', '--bolt', '12.9', '--base', 'A5052-H112', '--dw', '8.5', '--dh', '5.5'])
res['CB5-20_seat_on_block'] = hc(['--d', '5', '--pitch', '0.8', '--le', '10', '--load', f'{F_per:.2f}', '--torque', '4.5', '--bolt', '12.9', '--base', 'A5052', '--dw', '8.5', '--dh', '5.5'])
# 이음 M5 탭(블록, 깊이 6 → 물림 약 5): 황동 몸 근사 A2-70 Rp 450 대신 황동 Rp 250 → 'A2-70'은 볼트 쪽만 쓰므로 판정은 암나사 쪽
res['M5_fitting_tap'] = hc(['--d', '5', '--pitch', '0.8', '--le', '5', '--load', f'{F_tube:.1f}', '--torque', '1.5', '--bolt', 'A2-70', '--base', 'A5052', '--dw', '8.0', '--dh', '5.2'])
# 블록 몸 굽힘: 돌출 없는 28×28×20 상자, 볼트 줄–모서리 21 단면 28×(20−자리파기 10 → 살 10)
Mb = (F_tube + F_w) * 34.5
Zb = 28 * 10 ** 2 / 6
res['block']['sigma_MPa'] = round(Mb / Zb, 2)
res['block']['sf'] = round(195 / (Mb / Zb), 0)
# 포트 살: M5 탭 큰 지름 반경 2.5, 중심 Z 110 → 밑면 Z 105까지 2.5
res['block']['port_wall_min_mm'] = 2.5
res['block']['hoop_wall_sf'] = round(195 / (P * 5.0 / (2 * 2.5)), 0)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
p = res['pipe']
print('bbox', json.dumps(res['bbox']))
print('pipe op sf', p['op']['sf'], 'sigma', p['op']['sigma_MPa'], 'hoop sf', p['op']['sf_hoop'], 'defl', p['op']['tip_defl_mm'])
print('pipe misuse sf', p['misuse']['sf'], 'F_yield', p['misuse']['F_first_yield_N'], 'F_sf2', p['misuse']['F_for_sf2_N'])
print('bend', p['bend'])
print('vib', p['vib'])
print('socket', p['socket'])
print('block', res['block'])
for k in ['CB5-20_into_head', 'CB5-20_seat_on_block', 'M5_fitting_tap']:
    print(k, json.dumps({a: b for a, b in res[k].items() if a != 'inputs'}, ensure_ascii=False))
