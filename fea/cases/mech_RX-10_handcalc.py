# -*- coding: utf-8 -*-
"""RX-10 해석부 손계산(2026-11-14, v2.17.2). FEA 못 함 — 환경 없음(D-16, numpy·gmsh 없음).
대상: P_M06_SHOE(바닥 Y 90 -> 130, 로드 구멍 Y -166), P_M06_PCYL_BRKT(Y -184.5~-122, 볼트 Y -177·-128), P_M06_CARR(인서트 자리 Y -177).
형상은 STEP(tools/out/mech_RX-10/stepout)에서 직접 읽는다(면·원통). 누름 띠 식·임시값은 tools/out/mech_U6S/model/u6s_calc_model.json 그대로.
자국 식은 fea/cases/mech_U6S_handcalc.py 1절(Winkler 강체 판)과 같다.
실행: python -X utf8 -B fea/cases/mech_RX-10_handcalc.py
"""
import json, math, re, sys, os
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEPDIR = ROOT + '/tools/out/mech_RX-10/stepout/'
M = json.load(open(ROOT + '/tools/out/mech_U6S/model/u6s_calc_model.json', encoding='utf-8'))
R = {'_설명': 'RX-10 해석부 손계산. 입력: STEP 3개(REST 자세) + u6s_calc_model.json + 모델링부 실측(면 2,266.599 mm2, 139.782 g)'}


# ---------- 0. STEP 읽기(면·원통) ----------
def read_step(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    data = txt.split('DATA;', 1)[1]
    ent = {}
    for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', data, re.S):
        body = m.group(2).replace('\n', '')
        mm = re.match(r'([A-Z0-9_]+)\s*\((.*)\)$', body)
        ent[int(m.group(1))] = (mm.group(1), mm.group(2)) if mm else ('COMPLEX', body)
    return ent


def refs(a):
    return [int(x) for x in re.findall(r'#(\d+)', a)]


def nums(a):
    return [float(x) for x in re.findall(r'[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?', a)]


def pt(ent, i):
    return tuple(nums(ent[i][1].split('(', 1)[1])[:3])


def placement(ent, i):
    r = refs(ent[i][1])
    return pt(ent, r[0]), (pt(ent, r[1]) if len(r) > 1 else (0.0, 0.0, 1.0))


def geom(path):
    ent = read_step(path)
    vs = [pt(ent, refs(a)[0]) for t, a in ent.values() if t == 'VERTEX_POINT']
    g = {'bbox_min': [round(min(v[i] for v in vs), 3) for i in range(3)], 'bbox_max': [round(max(v[i] for v in vs), 3) for i in range(3)],
         'cyl': [], 'planes': []}
    for t, a in ent.values():
        if t == 'CYLINDRICAL_SURFACE':
            o, d = placement(ent, refs(a)[0])
            g['cyl'].append({'r': round(nums(a.rsplit(',', 1)[1])[0], 4), 'o': [round(x, 3) for x in o], 'd': [round(x, 3) for x in d]})
    for t, a in ent.values():
        if t != 'ADVANCED_FACE':
            continue
        r = refs(a)
        st, sa = ent[r[-1]]
        if st != 'PLANE':
            continue
        o, d = placement(ent, refs(sa)[0])
        loops, ok = [], True
        for b in r[:-1]:
            lp = refs(ent[b][1])[0]
            poly, circ = [], 0.0
            for oe in refs(ent[lp][1]):
                ec = refs(ent[oe][1])[-1]
                flag = ent[oe][1].strip().endswith('.T.')
                er = refs(ent[ec][1])
                v1, v2 = pt(ent, refs(ent[er[0]][1])[0]), pt(ent, refs(ent[er[1]][1])[0])
                ct = ent[er[2]][0]
                if ct == 'CIRCLE' and er[0] == er[1]:
                    circ = math.pi * nums(ent[er[2]][1].rsplit(',', 1)[1])[0] ** 2
                elif ct != 'LINE':
                    ok = False
                poly.append(v1 if flag else v2)
            loops.append((ent[b][0], poly, circ))
        g['planes'].append({'o': o, 'n': d, 'loops': loops, 'straight': ok})
    return g


def poly_area_xy(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


G = {n: geom(STEPDIR + n + '.step') for n in ('P_M06_SHOE', 'P_M06_PCYL_BRKT', 'P_M06_CARR')}
S = G['P_M06_SHOE']
zmin = S['bbox_min'][2]
flat = None
for f in S['planes']:
    if abs(abs(f['n'][2]) - 1) < 1e-6 and abs(f['o'][2] - zmin) < 1e-3:
        ars = [poly_area_xy(l[1]) + l[2] for l in f['loops']]          # 이 STEP은 바깥·안 고리를 모두 FACE_BOUND로 쓴다 -> 가장 큰 고리가 바깥
        outer = f['loops'][ars.index(max(ars))][1]
        inner = sum(ars) - max(ars)
        flat = {'area': poly_area_xy(outer) - inner, 'x': [min(v[0] for v in outer), max(v[0] for v in outer)],
                'y': [min(v[1] for v in outer), max(v[1] for v in outer)], 'n_vertex': len(outer), 'straight': f['straight']}
rod_hole = [c for c in S['cyl'] if abs(c['r'] - 3.0) < 0.01 and abs(abs(c['d'][2]) - 1) < 1e-6]
slots = sorted({(c['o'][1], c['r']) for c in S['cyl'] if abs(c['r'] - 3.55) < 0.01})
wing = [f for f in S['planes'] if abs(abs(f['n'][2]) - 1) < 1e-6 and f['o'][2] > 50]
wing_x = [min(v[0] for f in wing for l in f['loops'] for v in l[1]), max(v[0] for f in wing for l in f['loops'] for v in l[1])]
wing_z = sorted({round(f['o'][2], 3) for f in wing})
wall_x = sorted({round(f['o'][0], 3) for f in S['planes'] if abs(abs(f['n'][0]) - 1) < 1e-6 and
                 max(v[2] for l in f['loops'] for v in l[1]) - min(v[2] for l in f['loops'] for v in l[1]) > 20})
B, C = G['P_M06_PCYL_BRKT'], G['P_M06_CARR']
brkt_holes = sorted({(c['r'], tuple(c['o']), tuple(abs(x) for x in c['d'])) for c in B['cyl']})
carr_ins = sorted({(c['r'], c['o'][1], c['o'][2]) for c in C['cyl'] if abs(c['r'] - 3.4) < 0.01 or abs(c['r'] - 2.6) < 0.01})
R['step'] = {
    'SHOE': {'bbox': [S['bbox_min'], S['bbox_max']], '바닥 평탄 면(법선 Z, Z=zmin)': {k: (round(v, 3) if isinstance(v, float) else v) for k, v in flat.items()},
             '로드 구멍 Ø6 축': [c['o'][:2] for c in rod_hole], '장공 원통 (Y, r)': slots, '윗날개 X': wing_x, '윗날개 면 Z': wing_z, '벽 면 X': wall_x},
    'PCYL_BRKT': {'bbox': [B['bbox_min'], B['bbox_max']], '원통 (r, 원점, 축)': brkt_holes},
    'CARR': {'bbox': [C['bbox_min'], C['bbox_max']], '인서트 자리 (r, Y, Z)': carr_ins},
}

# ---------- 공통 값 ----------
A_MEAS, MASS_G, MASS_OLD_G = 2266.599, 139.782, 92.883          # 모델링부 실측(mech_RX-10_model.md 2·3절)
A_step = flat['area']
Lf, bf = flat['y'][1] - flat['y'][0], flat['x'][1] - flat['x'][0]
yc, xc = sum(flat['y']) / 2, sum(flat['x']) / 2
ROD_X, ROD_Y = rod_hole[0]['o'][0], rod_hole[0]['o'][1]
L_ALL = S['bbox_max'][1] - S['bbox_min'][1]                      # 130
P_ALLOW, H, K_PILE = 30.0, 20.5, 0.05                            # kPa(D-165 임시), 바닥~칼라 팔, 파일 강성 N/mm3(D-145 0.02~0.05)
A_head, A_rod, f_seal = M['A_head_mm2'], M['A_rod_mm2'], M['friction_band_N']
MU_G = M['mu_g']
W = M['W_moving_N'] + (MASS_G - MASS_OLD_G) * 9.81 / 1000        # 1.470 N
SY, E = 205.0, 193000.0                                          # SUS304
SF_OP, SF_MIS, HAND = 3.0, 2.0, 100.0                            # 요구서 6-1(M-09 기본값), 손 힘 D-79
R['입력'] = {'닿는 면 mm2(모델 실측 / STEP 다각형)': [A_MEAS, round(A_step, 3)], '평탄 길이·폭': [round(Lf, 3), round(bf, 3)], '평탄 중심 (X, Y)': [round(xc, 3), round(yc, 3)],
           '로드 축 (X, Y)': [ROD_X, ROD_Y], '로드 편심 e_y·e_x mm': [round(ROD_Y - yc, 3), round(ROD_X - xc, 3)], '바닥 전체 길이 L': round(L_ALL, 3),
           'W_moving_N': round(W, 4), 'A_head·A_rod mm2': [A_head, A_rod], '패킹 마찰 띠 N': f_seal, 'mu_g': MU_G, 'p_allow_kPa': P_ALLOW, 'k_pile N/mm3': K_PILE}


def band(P, mu_s=0.4):
    kk = MU_G * mu_s
    Fh = (P * A_head + W + f_seal) / (1 - kk)
    Fl = P * A_head + W - f_seal - kk * Fh
    return Fl, Fh


def sf_formula(F, L=None, A=A_MEAS, mu=0.4):
    L = L or L_ALL
    return P_ALLOW / (F / A * 1e3 * (1 + 6 * mu * H / L))


# ---------- 1. 자국 ----------
F_need = 3 * 1.0 * 0.003 / 0.050 ** 3 * (L_ALL / 1000.0)         # 9.36 N (D-164 임시: EI 1.0, delta 3, a 50, b = 슈 길이)
mark = {'완료 판정 ① (같은 식, mu 0.4, L 130, 잰 면 2,266.599)': {}}
for tag, F in (('F_hi 21.59 N(과제 문구, 0.18 MPa 옛 띠)', M['F_hi_N']), ('F_hi @0.18 MPa 새 무게', band(0.18)[1]), ('F_hi @0.19 MPa(새 설정)', band(0.19)[1]),
               ('F_hi @0.20 MPa(레귤레이터 상한)', band(0.20)[1])):
    mark['완료 판정 ① (같은 식, mu 0.4, L 130, 잰 면 2,266.599)'][tag] = {
        'F_N': round(F, 2), 'p_avg_kPa': round(F / A_MEAS * 1e3, 2), 'SF(L 130)': round(sf_formula(F), 3),
        'SF(L = 평탄 길이 %.3f, 엄격)' % Lf: round(sf_formula(F, L=Lf), 3), 'SF(평균, 옛 모델)': round(P_ALLOW / (F / A_MEAS * 1e3), 3)}
# 옛 형상 같은 식(차이 남김)
mark['옛 형상 L 90 · 면 1,506.6 · F_hi 21.59 (U6S-D6)'] = round(P_ALLOW / (M['F_hi_N'] / 1506.6 * 1e3 * (1 + 6 * 0.4 * H / 90)), 3)


def winkler(F, ey, ex=0.0):
    """강체 사각 판(Lf x bf), 기울기 자유. 압력 중심이 (ex, ey)만큼 벗어남. 핵 밖(한 축)은 들뜸 삼각형."""
    ky, kx = 6 * abs(ey) / Lf, 6 * abs(ex) / bf
    if ky + kx <= 1.0:
        p = F / (Lf * bf) * (1 + ky + kx)
        lift = False
    elif kx < 1e-9:
        p = 2 * F / (3 * bf * (Lf / 2 - abs(ey)))
        lift = True
    else:
        p = F / (Lf * bf) * (1 + ky + kx)        # 두 축 핵 밖은 근사(작게 나옴) — 표시만
        lift = True
    return p * 1e3, lift


# (B) 로드 실제 자리 편심(Y) + (C) 가로(X) 편심: 로드 X 편심, 안내 마찰(벽 X), 무게 중심
X_WALL = sum(wall_x) / len(wall_x)                               # 벽 가운데 X(안내 마찰 작용선)
X_CG = (38.0 * xc + 9.4248 * (X_WALL + 1.3) + 59.0 * X_WALL + 9.4248 * (X_WALL + 1.3) + 32.0 * sum(wing_x) / 2) / 147.8496   # 끝면 단면 조각(측정부)
dist = {}
for P in (0.19, 0.20):
    for mu in (0.0, 0.2, 0.3, 0.4):
        kk = MU_G * mu
        Fh = (P * A_head + W + f_seal) / (1 - kk)
        F_rodline = P * A_head + f_seal                              # 로드 선(X ROD_X)
        f_guide = kk * Fh                                            # 벽 선
        ey = (ROD_Y - yc) - mu * H                                   # 끌림(+Y 이송)은 압력 중심을 -Y로
        ex = (F_rodline * (ROD_X - xc) + f_guide * (X_WALL - xc) + W * (X_CG - xc)) / Fh
        pB, liftB = winkler(Fh, ey)
        pC, liftC = winkler(Fh, ey, ex)
        tilt_y = (2 * Fh / (Lf * bf) * 6 * abs(ey) / Lf) / (K_PILE * Lf)       # rad (k 0.05)
        dist['P%.2f_mu%.1f' % (P, mu)] = {
            'F_N': round(Fh, 2), 'e_y_mm': round(ey, 2), 'e_x_mm': round(ex, 2), 'p_max_kPa(Y만)': round(pB, 2), 'SF(Y만)': round(P_ALLOW / pB, 3),
            'p_max_kPa(Y+X)': round(pC, 2), 'SF(Y+X)': round(P_ALLOW / pC, 3), 'SF(Y+X, 정지 한도 100 kPa)': round(100.0 / pC, 2), '들뜸': liftB or liftC,
            '필요 기울기 rad(k 0.05 / 0.02)': [round(tilt_y, 5), round(tilt_y * 2.5, 5)], '끌림': mu > 0}
mark['실제 분포(로드 자리 편심, 강체 판 기울기 자유)'] = dist
slide = [v for k, v in dist.items() if v['끌림']]
mark['실제 분포 최저(끌림 mu 0.2~0.4)'] = {'Y만 @0.19': min(v['SF(Y만)'] for k, v in dist.items() if v['끌림'] and k.startswith('P0.19')),
                                      'Y+X @0.19': min(v['SF(Y+X)'] for k, v in dist.items() if v['끌림'] and k.startswith('P0.19')),
                                      'Y+X @0.20': min(v['SF(Y+X)'] for k, v in dist.items() if v['끌림'] and k.startswith('P0.20'))}
# (D) 곡선 구간 가로 끌림: 가로 기울기는 칼라 축 틈 0.1(벽 2.0 / 축 2.1) / 턱 Ø12 로 막힘 -> 압력 기울기 상한
TH_X = 0.1 / 12.0
lat = {'가로 기울기 상한 rad': round(TH_X, 5)}
P = 0.19
Fh = band(P)[1]
for kp in (0.05, 0.02):
    dp = kp * TH_X * bf / 2 * 1e3                                    # 가장자리 압력 더하기 kPa
    row = {'가장자리 더하기 kPa': round(dp, 2)}
    for tag, ang in (('가로 0°(직선)', 0.0), ('45°(곡선 반경 ~ 슈 거리 175)', 45.0), ('90°(순수 가로)', 90.0)):
        ey = (ROD_Y - yc) - 0.4 * H * math.cos(math.radians(ang))
        Mx = 0.4 * Fh * math.sin(math.radians(ang)) * H               # 가로 끌림 모멘트
        M_stop = kp * TH_X * Lf * bf ** 3 / 12                        # 멈춤까지 기울이는 데 드는 모멘트
        add = dp if Mx >= M_stop else Fh / (Lf * bf) * 6 * (Mx / Fh) / bf * 1e3
        p = winkler(Fh, ey)[0] + add
        row[tag] = {'p_max_kPa': round(p, 2), 'SF': round(P_ALLOW / p, 3)}
    lat['k_pile %.2f' % kp] = row
mark['곡선 구간 가로 끌림(mu 0.4, 0.19 MPa, 상한 검토)'] = lat
R['mark'] = mark

# ---------- 2. 누름 띠·잡음 비·레귤레이터·들기 ----------
rows = []
for P in (0.18, 0.184, 0.19, 0.195, 0.20):
    Fl, Fh = band(P)
    rows.append({'P_MPa': P, 'F_lo_N': round(Fl, 2), 'F_hi_N': round(Fh, 2), '잡음 비': round(Fl / F_need, 3), '자국 SF(같은 식)': round(sf_formula(Fh), 3),
                 '자국 SF(L=평탄 길이)': round(sf_formula(Fh, L=Lf), 3), '직선 끌림 N(mu 0.4)': round(0.4 * Fh, 2)})
lo = next(p / 10000 for p in range(1500, 2101) if band(p / 10000)[0] / F_need >= 1.0)
hi = max(p / 10000 for p in range(1500, 2601) if sf_formula(band(p / 10000)[1]) >= 2.0)
hi_strict = max(p / 10000 for p in range(1500, 2601) if sf_formula(band(p / 10000)[1], L=Lf) >= 2.0)
F_lift = A_rod * 0.5
R['band'] = {'F_need_N(L 130, D-164 임시)': round(F_need, 3), '표': rows,
             '창 MPa': {'잡음 비 >= 1 최저': lo, '자국 SF >= 2 최고(같은 식)': hi, '자국 SF >= 2 최고(L=평탄 길이)': hi_strict, 'IR1000-01BG 상한': 0.2, '설정': 0.19,
                       '창 너비 kPa(0.20까지)': round((0.2 - lo) * 1000, 1), '설정에서 아래·위 여유 kPa': [round((0.19 - lo) * 1000, 1), 10.0]},
             '잡음 비 1.2(U6S 기준)가 되는 P': next((p / 10000 for p in range(1500, 2601) if band(p / 10000)[0] / F_need >= 1.2), None),
             '들기 0.5 MPa': {'F_lift_N': round(F_lift, 2), 'SF(W + 패킹)': round(F_lift / (W + f_seal), 2),
                           'SF(W + 패킹 + 안내 마찰)': round(F_lift / (W + f_seal + MU_G * 0.4 * band(0.19)[1]), 2), '옛 값': [M['lift_SF_vs_W_plus_f'], M['lift_SF_vs_W_plus_f_plus_fg']]},
             '직선 끌림/U4 견인(옛 0.54 @8.63 N)': round(0.54 * 0.4 * band(0.19)[1] / 8.63, 3)}

# ---------- 3. 강체 판·기울기 자유 가정 확인 ----------
I_sec = 2.0 * 29.5 ** 3 / 12 + 38.0 * 16.75 ** 2 + 32.0 * 16.75 ** 2          # 벽 + 바닥·윗날개 평행축(보수), mm4
q = band(0.20)[1] / Lf
a_long = max(ROD_Y - flat['y'][0], flat['y'][1] - ROD_Y)
d_beam = q * a_long ** 4 / (8 * E * I_sec)
p_avg = band(0.20)[1] / A_MEAS
b_cant = flat['x'][1] - X_WALL
d_plate = p_avg * b_cant ** 4 / (8 * E * 2.0 ** 3 / 12)
d_pile = p_avg / K_PILE
ROD_L_PRESS, ROD_PLAY = 69.3 - (57.7 - 4.9), 0.006                # 누름 자세 로드 내민 길이(몸 끝 Z 69.3 -> 윗너트 윗면), 부시 틈 rad(U6S)
H_T = 57.7 - 32.5                                                  # 윗너트 윗면 ~ 칼라 선 높이(REST)
tilt_need = max(v['필요 기울기 rad(k 0.05 / 0.02)'][1] for v in dist.values())
R['rigid_check'] = {'세로 보 처짐 mm(슈 단면 I %.0f mm4, 긴 쪽 %.1f)' % (I_sec, a_long): round(d_beam, 6), '바닥 판 가로 외팔 처짐 mm(팔 %.1f)' % b_cant: round(d_plate, 5),
                    '파일 눌림 mm(k 0.05)': round(d_pile, 3), '판정': '처짐 << 파일 눌림 -> 강체 판 가정 맞음',
                    '기울기 자유': {'필요 기울기 최대 rad(k 0.02)': tilt_need, '로드 끝 옆 이동 mm(칼라 선 위 %.1f)' % (H_T - 4.9): round(tilt_need * (H_T - 4.9), 3),
                               '틈 mm(칼라 ±0.05 + 부시 0.006 x %.1f)' % ROD_L_PRESS: round(0.05 + ROD_PLAY * ROD_L_PRESS, 3)}}

# ---------- 4. 바뀐 하중 부품 ----------
Kb = 1.3
t, Lb, bb = 3.0, 13.0, 28.0
edge_y = min(ROD_Y - B['bbox_min'][1], B['bbox_max'][1] - ROD_Y)
br = {'유효 폭 28(너트 + 45°) 반쪽 14 <= 축~판 끝 %.1f' % edge_y: edge_y >= 14}
for tag, F, sf in (('운전_들기_0.5MPa', F_lift + 3 * W, SF_OP), ('운전_누름_멈춤_0.20MPa', A_head * 0.20 + 3 * W, SF_OP),
                   ('오조작_레귤레이터우회_0.5MPa', A_head * 0.5 + 3 * W, SF_MIS), ('오조작_손100N', HAND + 3 * W, SF_MIS)):
    s = 6 * F * Lb / (bb * t * t) * Kb
    br[tag] = {'F_N': round(F, 2), 'sigma_MPa': round(s, 1), 'SF': round(SY / s, 2), 'criterion': sf}
R['PCYL_BRKT_plate'] = br
yb = sorted(c[1][1] for c in brkt_holes if abs(c[0] - 2.75) < 0.01)            # 벽 볼트 구멍 Y
zb = [c[1][2] for c in brkt_holes if abs(c[0] - 2.75) < 0.01][0]
x_wallface = B['bbox_min'][0]
arm_x = ROD_X - x_wallface
z_top, z_bot = B['bbox_max'][2], B['bbox_min'][2]
a1, a2 = ROD_Y - yb[0], yb[1] - ROD_Y
bolt = {'볼트 Y': yb, 'Z': zb, '축~가까운·먼 볼트': [round(a1, 2), round(a2, 2)], '벽면~축 팔 X': round(arm_x, 2)}
for tag, F, sf in (('운전_들기_0.5MPa', F_lift, SF_OP), ('오조작_손100N', HAND, SF_MIS), ('오조작_레귤레이터우회', A_head * 0.5, SF_MIS)):
    T_up, T_dn = F * arm_x / (z_top - zb), F * arm_x / (zb - z_bot)
    T = max(T_up, T_dn)                                                       # 가까운 볼트가 다 받는다고 봄(보수)
    V = F * a2 / (a1 + a2)
    c = calc(d=5, le=8, load=round(T, 1), torque=0, bolt='12.9', base='PET-CF', sf_min=sf)
    bolt[tag] = {'인장 합 N(위/아래 지렛대)': [round(T_up, 1), round(T_dn, 1)], '인서트 뽑힘 임시 1000 N SF': round(1000.0 / T, 2), '가까운 볼트 전단 N': round(V, 1),
                 '인서트 벽 받음 MPa(6.5 x 8)': round(V / 52.0, 2), 'PET-CF 받음 SF(60)': round(60.0 / (V / 52.0), 1),
                 'handcalc(나사산, PET-CF 직접 탭 가정·참고)': {k: c[k] for k in c if k.startswith('sf')}, 'criterion': sf}
Zw = 3.0 * (z_top - 80.3) ** 2 / 6
Mb = HAND * a1 * a2 / (a1 + a2)
bolt['벽 굽힘(볼트 사이 단순보, 손 100 N)'] = {'M_Nmm': round(Mb, 1), 'sigma_MPa': round(Mb / Zw, 1), 'SF': round(SY / (Mb / Zw), 1)}
ins_y = sorted({c[1] for c in carr_ins})
bolt['캐리지 인서트 자리 Y'] = ins_y
bolt['인서트 구멍 Ø6.8 ~ 캐리지 -Y 끝 살 mm'] = round((ins_y[0] - 3.4) - C['bbox_min'][1], 2)
bolt['브래킷 구멍 Ø5.5 ~ 판 -Y 끝 mm(M-04 1.5t = 4.5)'] = round((yb[0] - 2.75) - B['bbox_min'][1], 2)
R['PCYL_BRKT_bolt'] = bolt
# 슈 윗날개 탭(t2): 벽 안쪽 면 -> 로드 축
x_wall_in = max(wall_x)
Lt = ROD_X - x_wall_in
b_tab = 7.0 + 2 * Lt
edge_tab = min(ROD_Y - S['bbox_min'][1] - 10, -115.0 - ROD_Y)
tab = {'팔 mm(벽 안쪽 면 X %.1f -> 로드 X %.1f)' % (x_wall_in, ROD_X): round(Lt, 2), '유효 폭 mm': b_tab, '로드~날개 끝 mm': round(edge_tab, 1)}
for tag, F, sf in (('운전_들기_0.5MPa', F_lift, SF_OP), ('운전_누름_F_hi_0.20MPa', band(0.20)[1], SF_OP), ('오조작_레귤레이터우회', A_head * 0.5, SF_MIS), ('오조작_손100N', HAND, SF_MIS)):
    s = 6 * F * Lt / (b_tab * 4.0) * Kb
    tab[tag] = {'F_N': round(F, 2), 'sigma_MPa': round(s, 1), 'SF': round(SY / s, 2), 'criterion': sf}
R['SHOE_tab'] = tab

# ---------- 5. 오조작: 슈 끝을 손으로 누르거나 들 때(입술 모서리 점하중 100 N, models.json P_M06_SHOE load (b)) ----------
# 슈 안내 = 칼라 2개(같은 Z 32.5) + 세로 장공 -> 앞뒤 기울기(X축 둘레)는 장공 끝에 닿기 전까지 자유.
# 로드 Ø4(끝 나사 M4)는 너트 2개로 윗날개에 꽉 물림 -> 슈가 기울면 로드 끝이 각 theta, 옆 이동 h x theta 를 강제로 받는다.
D_ROD, D_ROOT = 4.0, 3.141                                         # CJ2B10 로드 Ø4, M4x0.7 골 지름
EI = E * math.pi * D_ROD ** 4 / 64
My_root, Mp_root = SY * math.pi * D_ROD ** 3 / 32, SY * D_ROD ** 3 / 6       # 부시 쪽(민 축)
My_tip, Mp_tip = SY * math.pi * D_ROOT ** 3 / 32, SY * D_ROOT ** 3 / 6       # 너트 쪽(나사 골)
AIR_HOLD = F_lift - W                                              # 들림 자세에서 로드를 붙드는 힘


def rod_resist(l, h):
    """내민 길이 l, 로드 끝이 칼라 선 위 h. 슈 기울기 theta가 로드에 강제하는 (각 theta, 옆 h*theta)에 대한 버팀 모멘트(칼라 선 둘레)."""
    c_root, c_tip = 6 * h / l ** 2 - 2 / l, 6 * h / l ** 2 - 4 / l             # M = EI*theta*c
    eith_y = min(My_root / abs(c_root), My_tip / abs(c_tip))
    th_y = eith_y / EI
    V_y = (abs(c_root) + abs(c_tip)) * eith_y / l
    M_y = abs(c_tip) * eith_y + V_y * h
    V_p = (Mp_root + Mp_tip) / l
    M_p = Mp_tip + V_p * h
    return {'내민 길이 l': round(l, 1), 'h': round(h, 1), '첫 항복 기울기 rad(틈 뺀 뒤)': round(th_y, 5), '첫 항복 버팀 N·mm': round(M_y), '첫 항복 옆힘 N': round(V_y),
            '소성 붕괴 버팀 N·mm': round(M_p), '붕괴 옆힘 N': round(V_p)}


def misuse(rod_y, tip_y, col_plus_y, state):
    l = 69.3 - 57.7 + (4.9 if state == '누름' else 0.0)
    h = H_T - (4.9 if state == '누름' else 0.0)
    rr = rod_resist(l, h)
    out = {'로드': rr}
    arm_up = rod_y - tip_y                                         # 끝 들기: 로드(후퇴 끝) 밑 칼라 선 둘레
    arm_dn = col_plus_y - tip_y                                    # 끝 누르기: +Y 칼라(장공 아래 끝 0.6 닿은 뒤) 둘레, 로드는 공기 힘만큼만 붙듦
    air = AIR_HOLD * (col_plus_y - rod_y) / arm_dn if state == '들림' else 0.0
    cases = [('끝 들기', arm_up, 0.0)] + ([('끝 누르기', arm_dn, air)] if state == '들림' else [])
    if state == '누름':
        out['끝 누르기'] = '매트가 받침(파일 기울기 강성 k b L^3/12 = %.0f N·mm/rad) — 따로 셈하지 않음' % (K_PILE * bf * Lf ** 3 / 12)
    for tag, arm, add in cases:
        Fy, Fp = rr['첫 항복 버팀 N·mm'] / arm + add, rr['소성 붕괴 버팀 N·mm'] / arm + add
        out[tag] = {'팔 mm': round(arm, 1), '첫 항복 손 힘 N': round(Fy, 1), '붕괴 손 힘 N': round(Fp, 1), 'SF 첫 항복(손 100 N)': round(Fy / HAND, 2),
                    'SF 붕괴(손 100 N)': round(Fp / HAND, 2)}
    return out


tipY = S['bbox_min'][1]
rodm = {'가정': 'SUS304 로드 205 MPa(SMC 재질 미확인), 부시를 고정단으로 봄(주변 강체 — 탄성 기울기는 작게, 붕괴 힘은 그대로), 붕괴 = 소성 힌지 2개(부시 쪽 Ø4, 너트 쪽 M4 골)',
        'My·Mp N·mm(Ø4 / M4 골)': [round(My_root), round(Mp_root), round(My_tip), round(Mp_tip)],
        '새 형상 v2.17.2(로드 Y %.0f, 끝 Y %.0f)' % (ROD_Y, tipY): {s: misuse(ROD_Y, tipY, -135.0, s) for s in ('들림', '누름')},
        '옛 형상 v2.17.1(로드 Y -152, 끝 Y -205)': {s: misuse(-152.0, -205.0, -135.0, s) for s in ('들림', '누름')}}
# 끝을 눌러 매트에 닿을 때까지의 기울기와 로드 끝 강제 옆 이동
th_mat = 7.0 / (-135.0 - flat['y'][0])
rodm['끝 누르기: 평탄 끝이 매트에 닿는 기울기 rad(들림 틈 7.0)'] = round(th_mat, 4)
rodm['그때 로드 끝 옆 이동 mm / 틈(칼라 0.05 + 부시 0.006 x 11.6)'] = [round(th_mat * H_T, 2), round(0.05 + 0.006 * 11.6, 3)]
rodm['끝 들기: -Y 칼라 장공 아래 끝(틈 0.6)에 닿는 기울기 rad'] = round(0.6 / (ROD_Y + 175.0), 4)
# 뜬 이음으로 고쳤을 때 끝 들기 멈춤 짝힘(로드 -166 <-> 칼라 -175, 팔 9)
arm_stop = ROD_Y + 175.0
F_col = HAND * (ROD_Y - tipY) / arm_stop
rodm['뜬 이음 뒤 끝 들기 100 N: 칼라·로드 축 힘 N(팔 %.0f)' % arm_stop] = {'칼라': round(F_col), '로드 축(후퇴 끝)': round(F_col + HAND),
                                                             '윗날개 탭 SF': round(tab['오조작_손100N']['SF'] * HAND / (F_col + HAND), 2)}
R['misuse_rod'] = rodm
# 들림 자세 매달린 무게 모멘트(로드 옆하중, M-06)
V_shoe = 147.8496 * 120.0
ycg = (V_shoe * -175.0 + 430.0 * -240.0 - 225.0 * -135.0 - 225.0 * -175.0 - 57.0 * ROD_Y) / (V_shoe + 430.0 - 507.0)
R['hang'] = {'슈 무게 중심 Y(단면 조각 어림)': round(ycg, 1), '로드에서 벗어남 mm': round(ROD_Y - ycg, 1), '모멘트 N·mm': round(MASS_G * 9.81e-3 * (ROD_Y - ycg), 1),
             '로드 끝 옆힘 어림 N(칼라 선 위 25.2)': round(MASS_G * 9.81e-3 * (ROD_Y - ycg) / H_T, 2), '옛 값 N·mm(무게 중심 -156.6, 로드 -152, 92.9 g)': round(92.883 * 9.81e-3 * 4.6, 1)}

os.makedirs(ROOT + '/fea/results', exist_ok=True)
json.dump(R, open(ROOT + '/fea/results/mech_RX-10_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
# ---------- 화면 요약(15줄 안) ----------
m1 = mark['완료 판정 ① (같은 식, mu 0.4, L 130, 잰 면 2,266.599)']
print('STEP 면', round(A_step, 3), '평탄', round(Lf, 3), round(bf, 3), '로드', ROD_X, ROD_Y, '편심', round(ROD_Y - yc, 3), round(ROD_X - xc, 3))
print('① 같은 식', {k[:14]: (v['SF(L 130)'], v['SF(L = 평탄 길이 %.3f, 엄격)' % Lf]) for k, v in m1.items()}, '옛', mark['옛 형상 L 90 · 면 1,506.6 · F_hi 21.59 (U6S-D6)'])
print('분포 최저', mark['실제 분포 최저(끌림 mu 0.2~0.4)'], '정지@0.19', dist['P0.19_mu0.0']['SF(Y+X)'], dist['P0.19_mu0.0']['SF(Y+X, 정지 한도 100 kPa)'])
print('가로 끌림', {k: {kk: vv['SF'] for kk, vv in v.items() if isinstance(vv, dict)} for k, v in lat.items() if isinstance(v, dict)})
print('띠', [(r['P_MPa'], r['F_lo_N'], r['F_hi_N'], r['잡음 비'], r['자국 SF(같은 식)']) for r in rows])
print('창', R['band']['창 MPa'], '들기', R['band']['들기 0.5 MPa'])
print('강체', R['rigid_check'])
print('브래킷 판', {k: v['SF'] for k, v in br.items() if isinstance(v, dict)})
print('볼트', {k: (v['인서트 뽑힘 임시 1000 N SF'], v['가까운 볼트 전단 N']) for k, v in bolt.items() if isinstance(v, dict) and '인서트 뽑힘 임시 1000 N SF' in v},
      '끝 살', bolt['인서트 구멍 Ø6.8 ~ 캐리지 -Y 끝 살 mm'], bolt['브래킷 구멍 Ø5.5 ~ 판 -Y 끝 mm(M-04 1.5t = 4.5)'], '벽', bolt['벽 굽힘(볼트 사이 단순보, 손 100 N)'])
print('탭', {k: (v['SF'] if isinstance(v, dict) else v) for k, v in tab.items()})
for k in ('새 형상 v2.17.2(로드 Y %.0f, 끝 Y %.0f)' % (ROD_Y, tipY), '옛 형상 v2.17.1(로드 Y -152, 끝 Y -205)'):
    print('오조작', k[:12], {s: {t: (v[t]['첫 항복 손 힘 N'], v[t]['붕괴 손 힘 N']) for t in ('끝 들기', '끝 누르기') if isinstance(v[t], dict)} for s, v in rodm[k].items()})
print('매달림', R['hang'])
