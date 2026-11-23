# RX-04 바늘 둘레 LED 조명 — 손계산(E-18, FEA 환경 없음 D-16)
# 대상: P_RX04_LED_BRKT_SHT(SUS304 t1.5 접은 판), CB4-12 x2(헤드 암 밑 탭), CB3-10 x2(램프)
# 형상: STEP 꼭짓점 bbox(아래에서 다시 잼) + 모델링 보고서 mech_RX-04_model.md 3-1절 단면 꼭짓점
import json, math, re, subprocess, sys

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine'
OUT = ROOT + '/fea/results/mech_RX-04_handcalc.json'
STEP = ROOT + '/tools/out/mech_RX-04/stepout/P_RX04_LED_BRKT_SHT.step'


def step_bbox(p):
    pat = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)")
    pts = [tuple(map(float, m.groups())) for m in pat.finditer(open(p, encoding='utf-8', errors='ignore').read())]
    if not pts:
        return None
    return {'n_pts': len(pts), 'min': [min(c[i] for c in pts) for i in range(3)], 'max': [max(c[i] for c in pts) for i in range(3)]}


def hc(args):
    r = subprocess.run([sys.executable, '-B', ENG + '/engine/tools/handcalc.py'] + args, capture_output=True, text=True, encoding='utf-8')
    try:
        return json.loads(r.stdout)
    except Exception:
        return {'raw': r.stdout, 'err': r.stderr}


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


res = {'bbox': step_bbox(STEP)}

# ---- 재질·기준(요구서 6-1 → M-09 기본값)
E, G, SY = 193000.0, 75000.0, 205.0         # SUS304 MPa
TAU_Y = SY / math.sqrt(3)
SF_RUN, SF_MIS = 3.0, 2.0
t = 1.5

# ---- 단면 꼭짓점(YZ, 모델링 보고서 3-1) — 굽힘 뿌리 = 플랜지–경사 판 꺾임
A2 = (-52.866, 125.0); B = (-52.0, 123.5)   # 꺾임 바깥·안
A3 = (-66.299, 101.733); A4 = (-55.474, 95.483); A5 = (-54.724, 96.782)
root = ((A2[0] + B[0]) / 2, (A2[1] + B[1]) / 2)
far = max([A3, A4, A5], key=lambda p: dist(p, root))
L_plate = dist(A2, A3)                        # 경사 판 길이 26.87
L_lip = dist(A3, A4)                          # 입술 12.5
lever_max = dist(far, root)                   # 뿌리에서 가장 먼 점(손 힘을 그 선에 수직으로)
b_plate = 100.0                               # 경사 판 X −15~85
bolt_X = (-20.0, 90.0); bolt_Y = -45.5
span = bolt_X[1] - bolt_X[0]                  # 110
pivot_Y = -38.0                               # 플랜지 +Y 끝(아래로 당기면 여기가 암 밑면을 누르는 받침)
Ymin = A3[0]                                  # 가장 바깥 −Y −66.3

# ---- 하중
m_lamp, m_brkt, m_cable = 0.040, 0.0651, 0.010   # kg (램프 40 g 임시 D-229, 브래킷 STEP 65.1 g, 케이블 매달린 몫 어림)
W3 = (m_lamp + m_brkt + m_cable) * 9.81 * 3     # 자중 x3 g
F_HAND = 20.0                                  # 오조작 손 부딪힘(설계안 가정 — 요구서·자료대기에 값 없음)
F_WHATIF = 100.0                               # 가정 검토: 다른 헤드 둘레 부품(RX-10 슈 등) 손 100 N
res['geom'] = {'L_plate': round(L_plate, 2), 'L_lip': round(L_lip, 2), 'lever_max': round(lever_max, 2), 'far_pt': far,
               'root': root, 'b_plate': b_plate, 'span_bolts': span}
res['loads'] = {'W3_N': round(W3, 3), 'F_hand_N': F_HAND, 'F_whatif_N': F_WHATIF}


def case(F, sf_req, label):
    r = {'F_N': F, 'sf_req': sf_req}
    M = F * lever_max
    # (1) 경사 판 뿌리 굽힘 — 판 폭 전체(가운데 하중) / 모서리 하중 유효 폭 = 레버(45° 퍼짐 한쪽, 보수)
    Zf = b_plate * t ** 2 / 6
    b_eff = min(b_plate, lever_max)
    Ze = b_eff * t ** 2 / 6
    r['root_full'] = {'M': round(M, 1), 'sigma': round(M / Zf, 1), 'SF': round(SY / (M / Zf), 2)}
    r['root_corner'] = {'b_eff': round(b_eff, 1), 'sigma': round(M / Ze, 1), 'SF': round(SY / (M / Ze), 2)}
    # (2) 볼트 사이 열린 단면(플랜지+경사 판+입술) 비틀림 — 가운데(X 35) 하중, 두 볼트가 반씩
    legs = [A2[0] - pivot_Y if False else abs(-38.0 - A2[0]), L_plate, L_lip]
    J = sum(l * t ** 3 / 3 for l in legs)
    Th = M / 2
    Lh = span / 2
    tau = Th * t / J
    theta = Th * Lh / (G * J)
    r['torsion'] = {'J_mm4': round(J, 1), 'T_half': round(Th, 1), 'tau': round(tau, 1), 'SF': round(TAU_Y / tau, 2),
                    'theta_rad': round(theta, 5), 'tip_move_mm': round(theta * lever_max, 3)}
    # (3) 플랜지 볼트 줄 굽힘 — 하중이 한 볼트 쪽 끝(X 85)에 있을 때, 볼트 줄 단면 유효 폭 = 머리 Ø7 + 2 x 꺾임–볼트 7.4 − 장공 4.5
    arm_bolt = abs(Ymin - bolt_Y)               # 아래 힘이 볼트 줄까지 가지는 수평 팔 20.8
    gap = abs(A2[0] - bolt_Y)                  # 7.37
    bw = 7.0 + 2 * gap - 4.5
    Mb = F * arm_bolt
    Zb = bw * t ** 2 / 6
    r['flange_boltline'] = {'arm': round(arm_bolt, 1), 'b_eff': round(bw, 1), 'M': round(Mb, 1), 'sigma': round(Mb / Zb, 1),
                            'SF': round(SY / (Mb / Zb), 2)}
    # (4) 볼트 당김(지렛대): 받침 Y −38, 볼트 팔 7.5, 힘 팔 |Ymin − pivot| — 한 볼트가 전부(보수)
    Fb = F * abs(Ymin - pivot_Y) / abs(bolt_Y - pivot_Y)
    r['bolt_pull_N'] = round(Fb, 1)
    r['bolt_M4'] = hc(['--d', '4', '--pitch', '0.7', '--le', '10.5', '--load', str(round(Fb, 1)), '--torque', '1.5', '--bolt', '12.9',
                       '--base', 'A5052', '--dw', '7.0', '--dh', '4.5', '--sf-min', str(sf_req)])
    # 램프 CB3-10 x2: 램프 질량만(손은 램프 몸이 판에 받침) — 운전에서만
    r['label'] = label
    return r


res['run_selfweight'] = case(W3, SF_RUN, '운전 자중 x3 g')
res['misuse_hand20'] = case(F_HAND, SF_MIS, '오조작 손 20 N(설계안 가정)')
res['whatif_hand100'] = case(F_WHATIF, SF_MIS, '가정 검토 손 100 N')

# ---- 볼트 머리 좌면(장공 4.5 x 10, 머리 Ø7) — 머리 원에서 폭 4.5 띠를 뺀 넓이
r_h = 3.5; w = 4.5
strip = 2 * (r_h ** 2 * math.asin(w / (2 * r_h)) + (w / 2) * math.sqrt(r_h ** 2 - (w / 2) ** 2))
A_seat = math.pi * r_h ** 2 - strip
Fv = 1500.0 / (0.2 * 4)                        # 1.5 N·m 예압
res['seat_CB4_on_slot'] = {'A_mm2': round(A_seat, 2), 'preload_N': Fv, 'p_MPa': round(Fv / A_seat, 1), 'pG_SUS304': 400,
                           'SF': round(400 / (Fv / A_seat), 2)}
# 1.0 N·m이면
res['seat_CB4_on_slot_1Nm'] = {'preload_N': 1000 / 0.8, 'p_MPa': round(1000 / 0.8 / A_seat, 1)}

# ---- 램프 M3 x2 (램프 탭, 임시 D-229 — 수지 몸이면 약함): 운전 자중 x3 g만
F_lamp = m_lamp * 9.81 * 3 / 2
res['lamp_M3_each_N'] = round(F_lamp, 3)

# ---- 고유 진동(헤드 3000 땀/분 = 50 Hz)
I_plate = b_plate * t ** 3 / 12                # mm⁴
k_bend = E * I_plate / L_plate * 1e-3          # N·m/rad (E MPa·mm⁴/mm = N·mm → /1000)
legs = [abs(-38.0 - A2[0]), L_plate, L_lip]
J = sum(l * t ** 3 / 3 for l in legs)
k_tor = 12 * G * J / span * 1e-3              # 고정–고정, 고르게 퍼진 비틀림의 평균 각 기준
k_ser = 1 / (1 / k_bend + 1 / k_tor)
r_g = 0.020                                     # 회전 반지름(꺾임선 → 램프 무게중심 약 14, 보수 20)
Jm = (m_lamp + m_brkt) * r_g ** 2
f1 = math.sqrt(k_ser / Jm) / (2 * math.pi)
f_bend_only = math.sqrt(k_bend / Jm) / (2 * math.pi)
res['vibration'] = {'k_bend_Nm_rad': round(k_bend, 1), 'k_tor_Nm_rad': round(k_tor, 1), 'k_series': round(k_ser, 1),
                    'J_kgm2': Jm, 'f1_Hz': round(f1, 0), 'f_bend_only_Hz': round(f_bend_only, 0), 'head_Hz': 50.0,
                    'ratio': round(f1 / 50.0, 2)}
# 자중 처짐(끝, 비틀림 + 굽힘)
th = W3 / 3 * lever_max * 1e-3 / k_ser
res['selfweight_tip_mm'] = round(th * lever_max, 4)

# 과사양 확인(운전 3배 = 9, 오조작 2배 = 6)
mis = res['misuse_hand20']
mins = min(mis['root_corner']['SF'], mis['torsion']['SF'], mis['flange_boltline']['SF'])
res['summary'] = {'misuse20_min_SF': mins, 'whatif100_min_SF': min(res['whatif_hand100']['root_corner']['SF'],
                  res['whatif_hand100']['torsion']['SF'], res['whatif_hand100']['flange_boltline']['SF']),
                  'run_min_SF': min(res['run_selfweight']['root_corner']['SF'], res['run_selfweight']['torsion']['SF'],
                                    res['run_selfweight']['flange_boltline']['SF'])}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
s = res['summary']
print('bbox', res['bbox'])
print('geom', res['geom'])
for k in ['run_selfweight', 'misuse_hand20', 'whatif_hand100']:
    c = res[k]
    print(k, 'root_full', c['root_full']['SF'], 'root_corner', c['root_corner']['SF'], 'tors', c['torsion']['SF'], c['torsion']['tip_move_mm'],
          'flange', c['flange_boltline']['SF'], 'boltN', c['bolt_pull_N'], 'boltM4', {x: c['bolt_M4'].get(x) for x in ('ok', 'sf_min_found', 'sf') if x in c['bolt_M4']})
print('seat', res['seat_CB4_on_slot'], 'vib', res['vibration'], 'tip', res['selfweight_tip_mm'])
