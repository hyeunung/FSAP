# -*- coding: utf-8 -*-
"""M02R 해석부 손계산(4회차, 2026-11-13, v2.14.0). FEA 못 함 — 환경 없음(자료대기 D-16).
대상(새 하중 부품 STEP 6): P_M02S_SPRING_TAB_1·_2(SUS304), P_M02_ARM_SIDE_N·_P(SUS304), P_M02_ARM_TIE(A5052), P_M02_BASE(SUS304).
바뀐 것: 탭 날개 24 -> 33·볼트 s±7 -> s±12, base M5 탭 4개 자리, 옆판 P에 그네 볼트 M5 탭 2개가 처음 생김(전에는 빗나가 없었음), 옆판·TIE 옛 구멍 메움.
단면은 가정하지 않고 STEP 글자 파싱(fea/results/mech_M02R_stepgeo.json)과 생성기 좌표로 쓴다(E-18).
좌표: 측정 좌표계. 팔·그네는 θ0(J_U4_PRESS 0) 자세 = U4_PRESS 컴포넌트 좌표(STEP은 REST 13.006° -> 축 X (Y 120, Z 140) 둘레로 되돌림).
하중: 운전 = 자중 x3 g(들림) / IR1000 상한 0.2 MPa 누름 + 마찰 μ0.4, 오조작 = 공급 0.5 MPa 전부 + μ0.5. 판정 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2).
실행: python -X utf8 -B fea/cases/mech_M02R_swing_handcalc.py
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = json.load(open(ROOT + '/fea/results/mech_M02R_stepgeo.json', encoding='utf-8'))
SW = json.load(open(ROOT + '/tools/out/mech_M02R/model5/swing5.json', encoding='utf-8'))
SWM = json.load(open(ROOT + '/tools/out/mech_M02R/model5/swing5_mass.json', encoding='utf-8'))
H6 = json.load(open(ROOT + '/tools/out/mech_M02R/handcalc6.json', encoding='utf-8'))
SF_OP, SF_MIS = 3.0, 2.0
SY = {'SUS304': 205.0, 'A5052': 195.0}
E_SUS = 193000.0
R = {'_설명': 'M02R 4회차 해석부 손계산(v2.14.0). FEA 못 함 — 환경 없음(D-16). 단위 mm·N·MPa'}
YP, ZP = 120.0, 140.0                      # 그네 축 X


def sfrec(name, s_op, s_mis, mat, note=''):
    a, b = SY[mat] / s_op, SY[mat] / s_mis
    R[name] = {'sigma_op_MPa': round(s_op, 2), 'sigma_mis_MPa': round(s_mis, 2), 'SF_op': round(a, 2), 'SF_mis': round(b, 2),
               'ok': a >= SF_OP and b >= SF_MIS, 'yield_ok': min(a, b) >= 1.2, 'near_limit': (SF_OP <= a < 1.1 * SF_OP) or (SF_MIS <= b < 1.1 * SF_MIS),
               'overspec': a >= 3 * SF_OP and b >= 3 * SF_MIS, 'material': mat, 'note': note}


# ================= 1. 스프링 힘(기하로 정해짐) =================
K, L0 = SW['k_each'], 45.0
F_INIT = SWM['init_tension_each_new']      # 15.51 N (D-189 임시)
TOP, BOT0 = (50.0, 234.0), (50.0, 156.0)   # 탭 다리 구멍 / 그네 귀 구멍(θ0)


def rot(p, deg):                           # + = 바퀴 내려감
    a = math.radians(deg); y, z = p[0] - YP, p[1] - ZP
    return (YP + y * math.cos(a) - z * math.sin(a), ZP + y * math.sin(a) + z * math.cos(a))


spring = {}
for nm, jp in (('내림 끝 J -4.11', -4.11), ('옛 내림 끝 J -3.349', -3.349), ('두께 6 J -0.96', -0.96), ('θ0', 0.0), ('두께 16 J 3.751', 3.751), ('들림 J 13.006', 13.006)):
    b = rot(BOT0, -jp)                     # J + = 들림 -> 바퀴 내려감은 -J
    L = math.hypot(TOP[0] - b[0], TOP[1] - b[1])
    f = F_INIT + K * (L - L0)
    spring[nm] = {'len': round(L, 2), 'F_each_N': round(f, 2), 'dir_from_Z_deg': round(math.degrees(math.atan2(abs(TOP[0] - b[0]), TOP[1] - b[1])), 2)}
F_S = spring['내림 끝 J -4.11']['F_each_N']
ang_max = max(v['dir_from_Z_deg'] for v in spring.values())
W_TAB = (22.73 + 21.04) / 1000 * 9.80665   # 탭 + 스프링 위 반쪽(서명 표)
F_TAB = F_S + 3 * W_TAB                    # 운전 = 오조작(스프링 힘은 실린더 행정 끝 기하로 막힘, 공압으로 더 늘지 않음)
R['spring'] = {'k': K, 'init_each': F_INIT, 'states': spring, 'F_max_each_N': F_S, 'tab_self_3g_N': round(3 * W_TAB, 2), 'F_tab_N': round(F_TAB, 2),
               'model_report_value': H6['tab_bending']['F_spring_N'],
               'note': '모델링부 30.38 N은 옛 내림 끝 -3.349° 값. 지금 J_U4_PRESS 하한 -4.11°에서 다시 셈. 초장력·k는 임시(D-189)'}

# ================= 2. 스프링 탭(STEP) =================
t = G['P_M02S_SPRING_TAB_1']
bx, by, bz = t['bbox']
holes = [c for c in t['cylinders'] if abs(c['r'] - 2.75) < 0.01]
hook = [c for c in t['cylinders'] if abs(c['r'] - 2.25) < 0.01][0]
xs = sorted(h['origin'][0] for h in holes)
span = xs[1] - xs[0]
T_PL = bz[1] - 238.0                       # 날개 Z 238~242
B_PL = by[1] - by[0]
leg_x = (-297.0, -293.0); leg_y = (44.0, 56.0); leg_z = (228.0, 238.0)   # STEP 고유 좌표 x·y·z
assert -297.0 in t['x'] and -293.0 in t['x'] and 44.0 in t['y'] and 56.0 in t['y'] and 238.0 in t['z']
lig_x = min(xs[0] - 2.75 - bx[0], bx[1] - xs[1] - 2.75)
lig_y = min(holes[0]['origin'][1] - 2.75 - by[0], by[1] - holes[0]['origin'][1] - 2.75)
head_in = min(xs[0] - 4.25 - bx[0], bx[1] - xs[1] - 4.25)
R['tab_geom'] = {'plate_X': bx, 'plate_Y': by, 't': T_PL, 'bolt_hole_X': xs, 'bolt_span': span, 'hook_hole': hook['origin'], 'leg_X': leg_x, 'leg_Y': leg_y, 'leg_Z': leg_z,
                 'ligament_X_mm': round(lig_x, 3), 'ligament_Y_mm': round(lig_y, 3), 'head_d8.5_inside_mm': round(head_in, 3), 'solid': t['solid'], 'closed_shell': t['closed_shell']}
# 2-1 날개 굽힘: 볼트 사이 단순 지지, 가운데(다리) 하중 -> 반쪽 외팔보(길이 span/2, 하중 F/2)로 같은 값
R['tab_plate_beam'] = beam(t=T_PL, b=B_PL, length=span / 2, load=F_TAB / 2, e=E_SUS, sy=SY['SUS304'], sf_min=SF_OP)
s_pl = R['tab_plate_beam']['stress_MPa']
KT = 3.0                                    # 다리 뿌리 안쪽 모서리(R 없음 가정)·구멍 가장자리 응력 집중 보수값
sfrec('tab_plate_bending', s_pl, s_pl, 'SUS304', f'경간 {span:.0f}(볼트 X {xs}), 단면 {B_PL:.0f} x {T_PL:.0f}. 다리 뿌리 Kt {KT:.0f}를 곱해도 {s_pl * KT:.1f} MPa(SF {205 / (s_pl * KT):.1f})')
# 2-2 다리 고리 구멍: 순 단면 인장·찢김
w_leg, t_leg = leg_y[1] - leg_y[0], leg_x[1] - leg_x[0]
A_net = (w_leg - 4.5) * t_leg
e_low = hook['origin'][2] - 2.25 - leg_z[0]
A_tear = 2 * e_low * t_leg
sfrec('tab_leg_net_tension', F_TAB / A_net * KT, F_TAB / A_net * KT, 'SUS304', f'다리 {w_leg:.0f} x {t_leg:.0f}, 구멍 Ø4.5 -> 순 단면 {A_net:.0f} mm², Kt {KT:.0f} 포함')
R['tab_leg_tearout'] = {'tau_MPa': round(F_TAB / A_tear, 2), 'allow_0.577Rp': round(0.577 * 205, 1), 'SF': round(0.577 * 205 / (F_TAB / A_tear), 1), 'e_below_hole_mm': e_low, 'A_mm2': A_tear}
# 2-3 다리 뿌리: 스프링이 기운 만큼(최대 기울기) Y 성분 굽힘 + 인장
Fy_leg = F_TAB * math.sin(math.radians(ang_max))
M_leg = Fy_leg * (leg_z[1] - hook['origin'][2])
s_leg = F_TAB / (w_leg * t_leg) + M_leg / (t_leg * w_leg ** 2 / 6)
sfrec('tab_leg_root', s_leg * KT, s_leg * KT, 'SUS304', f'스프링 기울기 최대 {ang_max:.1f}° -> Y 성분 {Fy_leg:.2f} N, 팔 {leg_z[1] - hook["origin"][2]:.0f}, Kt {KT:.0f} 포함')
# 2-4 탭이 버티는 힘(오조작 SF 2 기준) ÷ 스프링 최대 힘
cap = min(SY['SUS304'] / SF_MIS * (B_PL * T_PL ** 2 / 6) / (span / 4), SY['SUS304'] / SF_MIS * A_net / KT, 0.577 * SY['SUS304'] / SF_MIS * A_tear)
R['tab_capacity'] = {'F_cap_SF2_N': round(cap, 0), 'ratio_to_spring_max': round(cap / F_S, 1), 'note': '손으로 스프링을 더 당기는 식의 오조작도 스프링 최대 힘의 이 배수까지 SF 2'}
# 2-5 탭 볼트 CB5-12 x2 (머리 아래, 탭 t4 통과, base t8 M5 탭 물림 8)
LE_TAB = 12.0 - T_PL
F_BT = F_TAB / 2
R['tab_bolt_M5_op'] = calc(d=5, le=LE_TAB, load=round(F_BT, 2), base='SUS304', dw=8.5, dh=5.5, sf_min=SF_OP)
R['tab_bolt_M5_mis'] = calc(d=5, le=LE_TAB, load=round(F_BT, 2), base='SUS304', dw=8.5, dh=5.5, sf_min=SF_MIS)
strip8 = 0.6 * 205 * math.pi * 5 * LE_TAB * 0.75 * 0.5
R['tab_bolt_torque'] = {'thread_strip_N': round(strip8, 0), 'T_limit_Nm(SF1)': round(0.2 * 5 * strip8 / 1000, 2),
                        'at_7Nm(D-108 일반값)': calc(d=5, le=LE_TAB, load=round(F_BT, 2), torque=7.0, base='SUS304', dw=8.5, dh=5.5)['sf_tightening'],
                        'at_4Nm': calc(d=5, le=LE_TAB, load=round(F_BT, 2), torque=4.0, base='SUS304', dw=8.5, dh=5.5)['sf_tightening'],
                        'note': 'SUS304 t8 탭에 12.9 볼트 일반 토크 7 N·m는 손계산식으로 암나사 전단 < 1. 4 N·m 지정이면 >= 1.4'}
# 2-6 가장자리 살 1.75(M-03 기본 2.5 미달)의 강도 뜻: 볼트는 인장만, 머리 좌면 Ø8.5가 날개 안
ab = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
R['tab_edge_ligament'] = {'ligament_X_mm': round(lig_x, 2), 'M-03_default': 2.5, 'seat_area_mm2': round(ab, 1), 'seat_p_at_4kN_MPa': round(4000 / ab, 0), 'pG_SUS304': 400,
                          'shear_on_bolt_Y_N': round(Fy_leg / 2, 2), 'bearing_Y_MPa': round(Fy_leg / 2 / (5 * T_PL), 3),
                          'note': '찢김 방향(X) 하중 0, Y 성분은 볼트당 1 N 안쪽이고 Y 쪽 살은 7.25. 강도로는 문제 없음 — 규칙(M-03) 예외는 따로 판정'}

# ================= 3. P_M02_BASE: M5 탭 4개 자리 =================
bc = [c for c in G['P_M02_BASE']['cylinders'] if c['axis'] and abs(abs(c['axis'][2]) - 1) < 1e-3]
new = [(-307.0, 50.0), (-283.0, 50.0), (-197.0, 50.0), (-173.0, 50.0)]
old = [(-302.0, 50.0), (-288.0, 50.0), (-192.0, 50.0), (-178.0, 50.0)]
found = [p for p in new if any(abs(c['origin'][0] - p[0]) < 0.05 and abs(c['origin'][1] - p[1]) < 0.05 and abs(c['r'] - 2.1) < 0.01 for c in bc)]
gone = [p for p in old if not any(abs(c['origin'][0] - p[0]) < 0.05 and abs(c['origin'][1] - p[1]) < 0.05 for c in bc)]
near = {}
for p in new:
    best = None
    for c in bc:
        o = c['origin']
        if (abs(o[0] - p[0]) < 0.05 and abs(o[1] - p[1]) < 0.05) or c['r'] > 10:   # r > 10은 바퀴 각도 조절 원호 장공의 옆면(중심 (-100, 0))
            continue
        d = math.hypot(o[0] - p[0], o[1] - p[1])
        lig = d - c['r'] - 2.5               # M5 골 아닌 바깥 지름 기준
        if best is None or lig < best[0]:
            best = (round(lig, 2), [o[0], o[1]], c['r'])
    near[str(p)] = {'ligament_to_nearest_hole_mm': best[0], 'hole': best[1], 'r': best[2]}
bb = G['P_M02_BASE']['bbox']
line50 = sorted({c['origin'][0] for c in bc if abs(c['origin'][1] - 50.0) < 0.05})
assert -175.5 in G['P_M02_BASE']['x'] and -157.0 in G['P_M02_BASE']['x'] and 66.0 in G['P_M02_BASE']['y'] and 84.0 in G['P_M02_BASE']['y']   # 관 장공(RX-08)
R['base_taps'] = {'new_taps_found': found, 'old_taps_gone': gone, 'nearest': near, 'edge_X_mm': round(min(p[0] for p in new) - 2.5 - bb[0][0], 2),
                  'tap(-173,50)_to_tube_slot_Y66_mm': 66.0 - 50.0 - 2.5,
                  'holes_on_Y50_line_X': line50, 'net_section_Y50': f'구멍 {len(line50)}개 — 옛 자리와 개수·지름 같음(자리만 ∓5) -> Y 50 줄 순 단면 변화 0',
                  'solid': G['P_M02_BASE']['solid'], 'thread_strip_SF_op': R['tab_bolt_M5_op']['sf_operating']['암나사 전단']}
# base 판정은 고정·하중·단면이 그대로라 지난 수치를 다시 쓰고 판정만 다시 낸다(E-17)
rx8 = json.load(open(ROOT + '/fea/results/mech_RX-08_handcalc.json', encoding='utf-8'))
R['base_rejudge'] = {'RX-08 base_tap_strip': {k: rx8['base_tap_strip'][k] for k in ('sigma_op_MPa', 'sigma_mis_MPa', 'SF_op', 'SF_mis')},
                     'ok': rx8['base_tap_strip']['SF_op'] >= SF_OP and rx8['base_tap_strip']['SF_mis'] >= SF_MIS,
                     'tab_local': '탭 2개가 base 밑면을 내리당김 합 %.1f N(탭당) — 캐리지 발 볼트 (-232,50)·(-215,50)·(-150,50) 사이 t8 판, 굽힘 응력 < 1 MPa' % F_TAB,
                     'dist_new_tap_to_RX08_tap': round(math.hypot(-173 + 146, 50 - 69), 1)}

# ================= 4. 그네 세운 판 <-> 옆판 P 이음(볼트 3개, 옆판 P M5 탭 2개가 이번에 생김) =================
BOLT = {'B1 CB5-16_M02S_1': (-300.0, 100.0), 'B2 CB5-20_M02S_1': (-265.0, 111.0), 'B3 CB5-16_M02S_2': (-166.0, 120.0)}
sp = {(c['r'], c['origin'][0]) for c in G['P_M02_ARM_SIDE_P']['cylinders']}
assert (2.1, -300.0) in sp and (2.1, -166.0) in sp and (2.75, -265.0) in sp, sp      # 탭 r 2.1 x2, 통과 Ø5.5(TIE로)
YJ = 37.0                                   # 이음 면(옆판 P 바깥면 = 그네 세운 판 Y 37~45 안면)
SWX, SWZ = (-320.0, -161.0), (92.0, 141.0)  # 그네 세운 판(생성기 stage_4_swing.json: X -320 +159, Z 92~141)
W = 56.5                                    # 매달린 묶음(그네 빼고) N, swing5 전제(측정)
CG = (-191.0, -0.4, 74.4)                   # θ0 무게중심(측정 REST CG를 되돌린 값, mech_M02R_design.md 2절)
WH = (-100.0, -4.32, 18.0)                  # 바퀴 접지(두께 16: Y -4.32, 밑 Z 18)
s16 = SW['states']['thick16']
N_OP = s16['N_at_0.2']                      # IR1000 상한 0.2 MPa (요구서 2-4 운전 압력 미정 -> 조정기 상한)
N_MIS = max(v['N_free_p0'] + v['N_per_MPa'] * 0.5 for k, v in SW['states'].items() if 'lift' not in k)   # 공급 0.5 MPa 전부
sn = math.sin(math.radians(13.006)); cs = math.cos(math.radians(13.006))


def cases():
    out = {}
    for sg in (+1, -1):                     # 들림 자세: 몸통 좌표에서 중력이 13° 기움
        out[f'운전A 들림 3g (기움 {sg:+d})'] = ('op', [((0.0, sg * 3 * W * sn, -3 * W * cs), CG)])
    for nm, kind, N, mu in (('운전B 누름 0.2 MPa μ0.4', 'op', N_OP, 0.4), ('오조작 0.5 MPa μ0.5', 'mis', N_MIS, 0.5)):
        for ax in ('Y', 'X'):
            for sg in (+1, -1):
                fr = (0.0, sg * mu * N, N) if ax == 'Y' else (sg * mu * N, 0.0, N)
                out[f'{nm} 마찰 {ax}{sg:+d}'] = (kind, [(fr, WH), ((0.0, 0.0, -W), CG)])
    return out


def joint(loads):
    xc = sum(p[0] for p in BOLT.values()) / 3; zc = sum(p[1] for p in BOLT.values()) / 3
    sr2 = sum((p[0] - xc) ** 2 + (p[1] - zc) ** 2 for p in BOLT.values())
    Fx = sum(f[0] for f, _ in loads); Fz = sum(f[2] for f, _ in loads)
    tq = sum((p[2] - zc) * f[0] - (p[0] - xc) * f[2] for f, p in loads)
    shear = {k: math.hypot(Fx / 3 + tq / sr2 * (p[1] - zc), Fz / 3 - tq / sr2 * (p[0] - xc)) for k, p in BOLT.items()}
    ten = {k: 0.0 for k in BOLT}
    # X축 둘레 벌어짐: 밑 발꿈치 Z 92(위가 벌어짐) / 위 발꿈치(주 띠 윗변 107·귀 126·132, 보수로 볼트별 가까운 윗변)
    def mx(zh):
        return sum((p[1] - YJ) * f[2] - (p[2] - zh) * f[1] for f, p in loads)
    m = mx(SWZ[0])
    if m > 0:
        d = {k: p[1] - SWZ[0] for k, p in BOLT.items()}
    else:
        top = {'B1 CB5-16_M02S_1': 107.0, 'B2 CB5-20_M02S_1': 126.0, 'B3 CB5-16_M02S_2': 132.0}
        d = {k: top[k] - p[1] for k, p in BOLT.items()}
        m = -mx(107.0)                      # 가장 낮은 윗변 기준 모멘트(팔이 길어 큰 쪽)
    s2 = sum(v * v for v in d.values())
    for k in ten:
        ten[k] += max(m, 0.0) * d[k] / s2
    # Z축 둘레 벌어짐: 발꿈치 X -161(그네 +X 끝) 또는 X -320
    def mz(xh):
        return sum((p[0] - xh) * f[1] - (p[1] - YJ) * f[0] for f, p in loads)
    m1 = mz(SWX[1])
    if m1 > 0:
        d = {k: SWX[1] - p[0] for k, p in BOLT.items()}; m2 = m1
    else:
        d = {k: p[0] - SWX[0] for k, p in BOLT.items()}; m2 = -mz(SWX[0])
    s2 = sum(v * v for v in d.values())
    for k in ten:
        ten[k] += max(m2, 0.0) * d[k] / s2
    return shear, ten, {'Mx_bottom_heel': round(mx(SWZ[0]), 0), 'Mz_heel_-161': round(m1, 0), 'torque_Y': round(tq, 0)}


jt = {}; worst = {'op': {'T': 0, 'V': 0}, 'mis': {'T': 0, 'V': 0}}
wt = {'op': {k: 0.0 for k in BOLT}, 'mis': {k: 0.0 for k in BOLT}}
for nm, (kind, loads) in cases().items():
    sh, tn, mm = joint(loads)
    jt[nm] = {'shear_N': {k: round(v, 1) for k, v in sh.items()}, 'tension_N': {k: round(v, 1) for k, v in tn.items()}, **mm}
    worst[kind]['T'] = max(worst[kind]['T'], max(tn.values())); worst[kind]['V'] = max(worst[kind]['V'], max(sh.values()))
    for k in BOLT:
        wt[kind][k] = max(wt[kind][k], tn[k])
R['joint_cases'] = jt
R['joint_load'] = {'W_N': W, 'CG': CG, 'wheel': WH, 'N_op_0.2MPa': N_OP, 'N_mis_0.5MPa': round(N_MIS, 1),
                   'T_max_N': {k: round(v['T'], 1) for k, v in worst.items()}, 'V_max_N': {k: round(v['V'], 1) for k, v in worst.items()},
                   '_note': '인장 = X축 벌어짐 + Z축 벌어짐을 더함(둘 다 Y 직접 힘을 포함해 조금 겹쳐 셈 = 보수). 전단은 예압 마찰을 안 믿고 볼트가 받는 것으로'}
LE_SW = 6.0                                 # CB5-16: 그네 판 8 + 옆판 t6 탭(1.2d). CB5-20: 8 + 6 통과 + TIE 탭 6
for kind, sfm in (('op', SF_OP), ('mis', SF_MIS)):
    R[f'joint_bolt_sideP_tap_{kind}'] = calc(d=5, le=LE_SW, load=round(max(wt[kind]['B1 CB5-16_M02S_1'], wt[kind]['B3 CB5-16_M02S_2']), 1), base='SUS304', dw=8.5, dh=5.5, sf_min=sfm)
A_SH = 14.2
R['joint_bolt_shear'] = {k: {'V_N': round(worst[k]['V'], 1), 'tau_MPa': round(worst[k]['V'] / A_SH, 1), 'SF_0.6Rp_12.9': round(0.6 * 1100 * A_SH / worst[k]['V'], 1),
                             'bearing_sideP_t6_MPa': round(worst[k]['V'] / (5 * 6), 1), 'bearing_swing_A5052_t8_MPa': round(worst[k]['V'] / (5 * 8), 1),
                             'SF_bearing_min': round(min(205 / (worst[k]['V'] / 30), 195 / (worst[k]['V'] / 40)), 1)} for k in ('op', 'mis')}
strip6s, strip6a = 0.6 * 205 * math.pi * 5 * LE_SW * 0.375, 0.6 * 195 * math.pi * 5 * LE_SW * 0.375
R['joint_bolt_torque'] = {'strip_SUS304_le6_N': round(strip6s, 0), 'strip_A5052_le6_N': round(strip6a, 0), 'T_limit_Nm(SF1)': round(0.2 * 5 * min(strip6s, strip6a) / 1000, 2),
                          'at_7Nm': calc(d=5, le=LE_SW, load=round(worst['mis']['T'], 1), torque=7.0, base='SUS304', dw=8.5, dh=5.5, sf_min=SF_MIS)['sf_tightening'],
                          'at_3Nm_SUS304': calc(d=5, le=LE_SW, load=round(worst['mis']['T'], 1), torque=3.0, base='SUS304', dw=8.5, dh=5.5, sf_min=SF_MIS),
                          'at_3Nm_A5052': calc(d=5, le=LE_SW, load=round(worst['mis']['T'], 1), torque=3.0, base='A5052', dw=8.5, dh=5.5, sf_min=SF_MIS),
                          'slip_3Nm_mu0.15': {'grip_N': 3 * 3000 * 0.15, 'V_sum_mis_N': round(3 * worst['mis']['V'], 1), 'SF': round(3 * 3000 * 0.15 / (3 * worst['mis']['V']), 2)},
                          'note': '물림 6 mm = 1.2d(< 1.5d M-01, 검도 M02R-D5)라 일반 토크 7 N·m는 암나사 전단 < 1. 3 N·m 지정이면 조임 SF >= 1.38, 분리 SF 충분'}

# ================= 5. 옆판 P: 새 탭 가장자리 살 + 앞판 쪽 하중이 그네 끝(X -161)을 넘어 들어오는 단면 =================
R['sideP_geom'] = {'t': 6.0, 'pocket_t': 4.0, 'pocket_X': [-214.0, -134.0], 'outline_Z': [40.0, 107.0], 'ears': {'X -280~-250': 126.0, 'X -175~-145': 132.0},
                   'tap_edge': {'B1 (-300,100)': {'to_top_Z107_mm': 107.0 - 100.0 - 2.5, 'to_end_X-320_mm': 20.0 - 2.5},
                                'B3 (-166,120)': {'to_ear_side_X-175_mm': 9.0 - 2.5, 'to_ear_top_Z132_mm': 12.0 - 2.5}},
                   'filled': '옛 부시 구멍 r 9 (-300,70)·옛 핀 구멍 r 4.5 (-160,122) 없음(STEP 원통 면에 없음)', 'solid': G['P_M02_ARM_SIDE_P']['solid']}
XC, HC, TC = -147.0, 67.0, 4.0              # 자른 면 X -147(앞판 볼트 X -126 과 그네 끝 X -161 사이), Z 40~107, 안면 홈 t4(Z 101~107 t6·귀는 안 셈 = 보수)
ZC = 73.5; YM = 34.0
beta = (1 - 0.63 * TC / HC) / 3
sec = {}
for nm, (kind, loads) in cases().items():
    Fx = sum(f[0] for f, _ in loads); Fy = sum(f[1] for f, _ in loads); Fz = sum(f[2] for f, _ in loads)
    Tx = sum((p[1] - YM) * f[2] - (p[2] - ZC) * f[1] for f, p in loads)
    Mz = sum((p[0] - XC) * f[1] for f, p in loads)
    My = sum((p[0] - XC) * f[2] - (p[2] - ZC) * f[0] for f, p in loads)
    s = abs(Mz) / (HC * TC ** 2 / 6) + abs(My) / (TC * HC ** 2 / 6) + abs(Fx) / (HC * TC)
    tau = abs(Tx) / (beta * HC * TC ** 2) + 1.5 * math.hypot(Fz, Fy) / (HC * TC)
    vm = math.sqrt(s * s + 3 * tau * tau)
    sec[nm] = {'kind': kind, 'Tx': round(Tx, 0), 'Mz': round(Mz, 0), 'My': round(My, 0), 'sigma': round(s, 1), 'tau': round(tau, 1), 'vm': round(vm, 1)}
vop = max(v['vm'] for v in sec.values() if v['kind'] == 'op'); vmis = max(v['vm'] for v in sec.values() if v['kind'] == 'mis')
R['sideP_section_cases'] = sec
sfrec('sideP_section_X-147', vop, vmis, 'SUS304',
      '상한 가정: 앞판(X -126 볼트 2)으로 들어온 힘 전부가 옆판 P 한 장으로 그네까지 감(옆판 N·TIE 몫 0), 무게도 전부 앞쪽에 있다고 봄. 단면 67 x 4(안면 홈), 비틀림 얇은 직사각 식. 실제 이음·모서리 응력 집중은 FEA 없이는 못 봄(D-16)')

# ================= 6. 옆판 N·TIE(다른 쪽 상한: 세로 힘의 절반이 옆판 N -> TIE -> B2로 감) =================
Fz_op = max(3 * W, N_OP); Fz_mis = N_MIS
tie = {}
for kind, Fz, sfm in (('op', Fz_op, SF_OP), ('mis', Fz_mis, SF_MIS)):
    Fn = Fz / 2
    M = Fn * 62.0                             # TIE 길이(Y -31~31)
    s_t = M / (20.0 * 20.0 ** 2 / 6)          # TIE 단면 20 x 20(STEP: X -275~-255, Z 101~121), 축선 탭 Ø4.2는 중립축이라 뺌 없음
    t_b2 = M / 10.0 + wt[kind]['B2 CB5-20_M02S_1']    # 끝면 20 x 20 가운데 볼트 하나: 지레 팔 10
    tie[kind] = {'F_N_side_N': round(Fn, 1), 'M_Nmm': round(M, 0), 'sigma_TIE_MPa': round(s_t, 2), 'SF_TIE': round(195 / s_t, 1), 'B2_tension_N': round(t_b2, 1),
                 'B2_calc': calc(d=5, le=LE_SW, load=round(t_b2, 1), base='A5052', dw=8.5, dh=5.5, sf_min=sfm)}
    # 옆판 N: 앞판 볼트(X -126)에서 TIE(X -265)까지 139, 면내 굽힘. 단면 67 x 4(안면 홈)
    s_n = Fn * 139.0 / (4.0 * 67.0 ** 2 / 6)
    tie[kind]['sideN_inplane_MPa'] = round(s_n, 2); tie[kind]['SF_sideN'] = round(205 / s_n, 1)
R['tie_sideN_bound'] = tie
R['sideN_geom'] = {'filled': '옛 부시 구멍 r 9·옛 핀 구멍 r 4.5 없음 -> 순 단면이 늘기만 함', 'solid': G['P_M02_ARM_SIDE_N']['solid'], 'tie_solid': G['P_M02_ARM_TIE']['solid']}

# ================= 7. 완료 판정 ⑤ 그네 값 다시 셈(모델링부 handcalc6.json 대조) =================
sr = H6['swing_recheck']
dM = 0.0
for k, b in sr['bodies'].items():
    dM += b['mass_g'][1] * (YP - b['y_theta0'][1]) - b['mass_g'][0] * (YP - b['y_theta0'][0])
dN = dM / 1000 * 9.80665 / 120.0
ev = SW['eval_p_set']
rot_sf = {}
for th, v in ev.items():
    n0 = v['N_land']; rot_sf[th] = [round(SW['SF0'] * (100 - abs(v['dY'])) / 100 * n0 / 40, 4), round(SW['SF0'] * (100 - abs(v['dY'])) / 100 * (n0 + dN) / 40, 4)]
mark16 = [round(51.6 / ev['16']['N_nom'], 4), round(51.6 / (ev['16']['N_nom'] + dN), 4)]
R['swing_recheck'] = {'dM_gmm': round(dM, 1), 'dM_model_report': sr['dM_total_gmm'], 'dN_N': round(dN, 4), 'dN_pct_of_N_free': round(dN / SW['N_free_theta0'] * 100, 3),
                      'rot_SF_before_after': rot_sf, 'mark_SF_16_before_after': mark16, 'press_SF': sr['press_SF'], 'lift_SF_min': sr['lift_SF_min'],
                      'spring_anchor': {'tab_hook_hole(STEP)': hook['origin'], 'design': [TOP[0], TOP[1]], 'len_theta0': spring['θ0']['len']},
                      'unchanged': all(abs(a - b) < 0.001 for a, b in rot_sf.values()) and abs(mark16[0] - mark16[1]) < 0.001,
                      'note': '옆판 구멍 메움·탭으로 질량이 준 만큼(-1.76 g)과 무게중심 이동. 표기 자리(소수 셋째)에서 변화 없음. 회전·자국 SF 1.01대의 좁은 여유는 전부터 있는 디테일 M02R-D2(D-188·D-189)'}

# ================= 8. 요약 =================
rows = {k: v for k, v in R.items() if isinstance(v, dict) and 'SF_op' in v}
R['summary'] = {'min_SF_op': min((v['SF_op'], k) for k, v in rows.items()), 'min_SF_mis': min((v['SF_mis'], k) for k, v in rows.items()),
                'all_ok': all(v['ok'] for v in rows.values()), 'near_limit': [k for k, v in rows.items() if v['near_limit']], 'overspec': [k for k, v in rows.items() if v['overspec']],
                'bolt_ok_strength': {k: {'sf': v['sf_operating'], 'engage': v['engage_ratio'], 'ok': v['ok'], 'needs_fea': v['needs_fea']} for k, v in R.items() if isinstance(v, dict) and 'sf_operating' in v},
                'fea': '해석 못 함 — 환경 없음(자료대기 D-16)'}
json.dump(R, open(ROOT + '/fea/results/mech_M02R_swing_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('spring F_max', F_S, 'tab load', round(F_TAB, 2), '| N_op', N_OP, 'N_mis', round(N_MIS, 1))
for k, v in rows.items():
    print(f"{k:24s} op {v['sigma_op_MPa']:7.2f} mis {v['sigma_mis_MPa']:7.2f} SF {v['SF_op']:6.2f}/{v['SF_mis']:6.2f} {'ok' if v['ok'] else 'NG'}{' near' if v['near_limit'] else ''}")
print('tab tearout', R['tab_leg_tearout']['SF'], 'cap x', R['tab_capacity']['ratio_to_spring_max'], 'lig', R['tab_geom']['ligament_X_mm'], R['tab_geom']['ligament_Y_mm'])
print('tab bolt', R['tab_bolt_M5_op']['sf_operating'], R['tab_bolt_M5_op']['ok'], 'torque', R['tab_bolt_torque']['T_limit_Nm(SF1)'])
print('base', R['base_taps']['new_taps_found'], 'gone', R['base_taps']['old_taps_gone'], [v['ligament_to_nearest_hole_mm'] for v in R['base_taps']['nearest'].values()])
print('joint T', R['joint_load']['T_max_N'], 'V', R['joint_load']['V_max_N'])
print('joint tap op', R['joint_bolt_sideP_tap_op']['sf_operating'], 'mis', R['joint_bolt_sideP_tap_mis']['sf_operating'], 'Tlim', R['joint_bolt_torque']['T_limit_Nm(SF1)'], 'slip', R['joint_bolt_torque']['slip_3Nm_mu0.15']['SF'])
print('tie', {k: (v['SF_TIE'], v['B2_tension_N'], v['B2_calc']['sf_operating'], v['SF_sideN']) for k, v in tie.items()})
print('swing', R['swing_recheck']['dM_gmm'], R['swing_recheck']['dN_N'], R['swing_recheck']['rot_SF_before_after'], mark16, R['swing_recheck']['unchanged'])
print('summary', R['summary']['min_SF_op'], R['summary']['min_SF_mis'], R['summary']['all_ok'], R['summary']['near_limit'])
