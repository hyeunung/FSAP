# -*- coding: utf-8 -*-
"""RX-10-F1 해석부 손계산(2026-11-23, v2.22.2 — 로드–윗날개 뜬 이음 + 브래킷 멈춤 턱). FEA 못 함 — 환경 없음(D-16).
형상: tools/out/mech_RX-10/stepout/P_M06_SHOE.step · P_M06_PCYL_BRKT.step(REST = 들림 자세)에서 직접 읽음.
옛 모델(꽉 물린 이음) 한도·가정은 fea/cases/mech_RX-10_handcalc.py 5절 그대로(SUS304 205 MPa D-210, 손 100 N D-79, 부시 틈 0.006 rad).
실행: python -X utf8 -B fea/cases/mech_RX-10_F1_handcalc.py  ->  fea/results/mech_RX-10_F1_handcalc.json
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEPDIR = ROOT + '/tools/out/mech_RX-10/stepout/'
R = {'_설명': 'RX-10-F1 해석부 손계산(v2.22.2). 입력: 임시 STEP 2개(REST) + 서명 bbox(tools/out/signatures.json) + 옛 해석 한도'}


# ---------- 0. STEP 읽기 ----------
def read_step(path):
    data = open(path, encoding='utf-8', errors='ignore').read().split('DATA;', 1)[1]
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


def geom(path):
    ent = read_step(path)
    vs = [pt(ent, refs(a)[0]) for t, a in ent.values() if t == 'VERTEX_POINT']
    g = {'bbox': [[round(min(v[i] for v in vs), 3) for i in range(3)], [round(max(v[i] for v in vs), 3) for i in range(3)]], 'cyl': [], 'planes': []}
    for t, a in ent.values():
        if t == 'CYLINDRICAL_SURFACE':
            r = refs(ent[refs(a)[0]][1])
            g['cyl'].append((round(nums(a.rsplit(',', 1)[1])[0], 3), tuple(round(x, 3) for x in pt(ent, r[0])), tuple(round(abs(x), 3) for x in pt(ent, r[1]))))
        if t == 'ADVANCED_FACE':
            r = refs(a)
            if ent[r[-1]][0] != 'PLANE':
                continue
            pr = refs(ent[refs(ent[r[-1]][1])[0]][1])
            o, n = pt(ent, pr[0]), pt(ent, pr[1])
            p = []
            for b in r[:-1]:
                for oe in refs(ent[refs(ent[b][1])[0]][1]):
                    er = refs(ent[refs(ent[oe][1])[-1]][1])
                    p += [pt(ent, refs(ent[er[0]][1])[0]), pt(ent, refs(ent[er[1]][1])[0])]
            g['planes'].append((o, n, p))
    return g


S, B = geom(STEPDIR + 'P_M06_SHOE.step'), geom(STEPDIR + 'P_M06_PCYL_BRKT.step')
rodslot = sorted({c[1][:2] for c in S['cyl'] if abs(c[0] - 2.5) < 0.01 and c[2][2] > 0.99})
wallslot = sorted({(c[1][1], c[1][2]) for c in S['cyl'] if abs(c[0] - 3.55) < 0.01})
wing = [f for f in S['planes'] if abs(abs(f[1][2]) - 1) < 1e-6 and f[0][2] > 50]
wing_xy = [[min(v[i] for f in wing for v in f[2]), max(v[i] for f in wing for v in f[2])] for i in (0, 1)]
flat = [f for f in S['planes'] if abs(abs(f[1][2]) - 1) < 1e-6 and abs(f[0][2] - S['bbox'][0][2]) < 1e-3]
flat_y = [min(v[1] for f in flat for v in f[2]), max(v[1] for f in flat for v in f[2])]
zb = B['bbox'][0][2]
lug = [f for f in B['planes'] if abs(abs(f[1][2]) - 1) < 1e-6 and abs(f[0][2] - zb) < 1e-3]
lug_x = [min(v[0] for f in lug for v in f[2]), max(v[0] for f in lug for v in f[2])]
lug_y = [min(v[1] for f in lug for v in f[2]), max(v[1] for f in lug for v in f[2])]
R['step'] = {'SHOE bbox': S['bbox'], '로드 장공 원통 R2.5 축 (X, Y)': rodslot, '벽 장공 원통 R3.55 (Y, Z)': wallslot, '윗날개 X·Y': wing_xy,
             '윗날개 윗면 Z': max(f[0][2] for f in wing), '바닥 평탄 Y': [round(v, 3) for v in flat_y],
             'BRKT bbox': B['bbox'], '멈춤 턱 밑면 Z': zb, '멈춤 턱 밑면 X·Y': [lug_x, lug_y],
             'BRKT 원통 (r, 원점, 축)': sorted(set(B['cyl']))}

# ---------- 공통 값 ----------
HAND, SY, E, KB = 100.0, 205.0, 193000.0, 1.3                       # D-79, SUS304(D-210 임시), 굽힘 계수(옛 해석과 같음)
Y_TIP, Y_FLAT, Y_ROD, Y_CN, Y_CP, Y_FRONT = S['bbox'][0][1], flat_y[0], -166.0, -175.0, -135.0, flat_y[1]
Y_STOP = lug_y[0]                                                    # 멈춤 턱 -Y 모서리(먼저 닿는 선)
Z_COL, R_COL, R_SLOT = 32.5, 3.5, 3.55
zs = sorted({z for _, z in wallslot})
G_UP = (Z_COL - zs[0]) + (R_SLOT - R_COL)                           # 들림 자세에서 슈가 칼라에 대해 더 오를 수 있는 양(장공 아래 끝)
G_DN = (zs[-1] - Z_COL) + (R_SLOT - R_COL)                          # 내려갈 수 있는 양(장공 윗끝)
G_STOP = zb - max(f[0][2] for f in wing)                            # 멈춤 턱 ↔ 윗날개 윗면
G_NUT, NUT_AC, NUT_AF, T_WING = 0.6, 8.082, 7.0, 2.0                 # 윗 너트 축 틈(검도 실측), NTJ-010C 맞모·맞변, 윗날개 t
SLOT_Y = min(Y_ROD - 2.0 - (rodslot[0][1] - 2.5), (rodslot[-1][1] + 2.5) - (Y_ROD + 2.0))   # 로드 Ø4 ↔ 장공 끝
W = 0.139615 * 9.80665
Y_CG = -177.1
F_LIFT, F_LIFT_MAX, F_HI = 32.99, 37.4, 23.8                         # 들기 붙듦 0.5 MPa(마찰 없이 / 패킹 마찰 띠 포함), 누름 띠 위 끝 0.20 MPa
D_ROD, D_ROOT = 4.0, 3.141
My4, Mp4 = SY * math.pi * D_ROD ** 3 / 32, SY * D_ROD ** 3 / 6
MyT, MpT = SY * math.pi * D_ROOT ** 3 / 32, SY * D_ROOT ** 3 / 6
L0, H_T, BUSH = 69.3 - 57.7, 57.7 - 32.5, 0.006                      # 들림 내민 길이, 윗 너트 윗면 ~ 칼라 선, 부시 틈 rad(임시)
Z_SHOE, Z_MAT, Z_SEAM, Z_BALL, Z_PANEL = S['bbox'][0][2], 10.0, 12.1, 0.0, -8.0   # 서명 bbox: 매트 윗면 10 · 이음매 12 · 볼 윗점 0 · 판넬 -8
R['입력'] = {'G_UP(칼라 장공 아래 끝)': round(G_UP, 3), 'G_DN(윗끝)': round(G_DN, 3), 'G_STOP': round(G_STOP, 3), 'G_NUT': G_NUT, '장공 Y 틈 ±': round(SLOT_Y, 3),
           'Y_TIP·FLAT·ROD·STOP·FRONT': [Y_TIP, round(Y_FLAT, 3), Y_ROD, Y_STOP, Y_FRONT], 'W N': round(W, 3),
           '로드 My·Mp(Ø4 / M4 골) N·mm': [round(My4), round(Mp4), round(MyT), round(MpT)], '슈 밑 Z(들림)': Z_SHOE,
           '슈 밑에 있는 것 Z(서명)': {'매트 윗면': Z_MAT, '이음매·테이프 윗면': Z_SEAM, '볼 윗점': Z_BALL, '판넬': Z_PANEL}}


def gap_need(th, w=NUT_AC):
    """기운 윗날개(t 2)가 너트 두 면 사이에 끼지 않으려면 필요한 축 틈"""
    return w * math.tan(th) + T_WING * (1 / math.cos(th) - 1)


def bind_angle(g, w=NUT_AC):
    lo, hi = 0.0, 0.6
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gap_need(mid, w) < g else (lo, mid)
    return lo


def float_rod(F, l, th, mu):
    """뜬 이음(끼기 전): 로드 굽힘 = 축 힘 x 너트 면 편심(맞모 반, 상한) + 옆힘(마찰 원뿔 tan(th + atan mu)) x 내민 길이"""
    m = F * NUT_AC / 2 + F * math.tan(th + math.atan(mu)) * l
    return {'로드 굽힘 N·mm': round(m, 1), 'SF 첫 항복(M4 골)': round(MyT / m, 2), 'SF 붕괴': round(MpT / m, 2)}


def wedged(l, h, arm, hold_m):
    """끼인 뒤(너트 두 면이 윗날개를 물음) 손 붕괴 힘: (i) 순수 짝힘 + 너트 면 마찰 옆힘 (ii) 옛 꽉 물린 이음(소성 힌지 2개)"""
    n = MpT / NUT_AC
    m1 = MpT + 0.2 * n * h
    vp = (Mp4 + MpT) / l
    m2 = MpT + vp * h
    y1 = MyT + 0.2 * (MyT / NUT_AC) * h
    return {'내민 길이·h': [round(l, 1), round(h, 1)], '첫 항복 손 힘 N(짝힘)': round((y1 + hold_m) / arm, 1),
            '붕괴 손 힘 N (i) 짝힘 / (ii) 꽉 물림': [round((m1 + hold_m) / arm, 1), round((m2 + hold_m) / arm, 1)],
            'SF 붕괴(손 100 N) (i) / (ii)': [round((m1 + hold_m) / arm / HAND, 2), round((m2 + hold_m) / arm / HAND, 2)],
            '끼인 너트가 윗날개에 주는 힘 N(로드 붕괴 때)': round(n + F_LIFT_MAX, 0)}


TH_B = bind_angle(G_NUT)
R['끼는 기울기 rad(너트 축 틈 0.6)'] = {'맞모 8.082가 Y 방향': round(TH_B, 4), '맞변 7.0이 Y 방향': round(bind_angle(G_NUT, NUT_AF), 4),
                              '장공 Y 틈이 다 차는 기울기(h 25.2)': round(SLOT_Y / H_T, 4)}
C = {}
# ---------- A. 들림 · 끝 들기 ----------
thA = G_STOP / (Y_ROD - Y_STOP)
FA = (HAND * (Y_STOP - Y_TIP) + W * (Y_CG - Y_STOP)) / (Y_ROD - Y_STOP)
SA = HAND + FA - W
C['A 들림·끝 들기'] = {'받는 것': '멈춤 턱(로드 아래 너트 둘레로 기울어 틈 %.2f)' % G_STOP, '기울기 rad': round(thA, 4), '로드 축 힘 = 탭 힘 N': round(FA, 1),
                 '멈춤 턱 힘 N': round(SA, 1), '탭 힘 ÷ 136': round(FA / 136, 2), '-Y 칼라 오름 / 틈': [round(thA * (Y_ROD - Y_CN), 3), round(G_UP, 2)],
                 '너트 축 틈 필요 / 있음': [round(gap_need(thA), 3), G_NUT], '로드 옆 이동 / 장공 틈': [round(H_T * thA, 2), round(SLOT_Y, 2)],
                 'mu 0.2': float_rod(FA, L0, thA, 0.2), 'mu 0.4': float_rod(FA, L0, thA, 0.4),
                 '들기 붙듦 ÷ 로드 축 힘(마찰 없이 / 패킹 마찰 포함)': [round(F_LIFT / FA, 2), round(F_LIFT_MAX / FA, 2)]}
# ---------- B. 들림 · 끝 누르기: +Y 칼라(장공 아래 끝) 둘레, 로드는 들기 붙듦만큼만 버팀 -> 평탄 끝이 밑에 닿을 때까지 기움 ----------
ARM_F, ARM_T = Y_CP - Y_FLAT, Y_CP - Y_TIP
TH_KIN = (G_UP + G_DN) / (Y_CP - Y_CN)                               # 밑에 아무것도 없을 때: -Y 칼라 장공 윗끝
for tag, ztop in (('B1 매트 있음(이음매 윗면 Z 12.1)', Z_SEAM), ('B2 매트 있음(매트 윗면 Z 10)', Z_MAT), ('B3 매트 없음(볼 윗점 Z 0)', Z_BALL), ('B4 매트 없음(볼 사이 — 칼라 장공 끝)', None)):
    th = TH_KIN if ztop is None else min(TH_KIN, (Z_SHOE - ztop + G_UP) / ARM_F)
    ext = (Y_CP - Y_ROD) * min(th, TH_B) - G_UP
    d = {'기울기 rad': round(th, 4), '로드 축 힘 = 탭 힘 N(들기 붙듦 상한)': F_LIFT_MAX, '너트 축 틈 필요(맞모 / 맞변) / 있음': [round(gap_need(th), 3), round(gap_need(th, NUT_AF), 3), G_NUT],
         '로드 옆 이동 / 장공 틈': [round(H_T * th, 2), round(SLOT_Y, 2)]}
    if gap_need(th) <= G_NUT:
        d['판정'] = '안 낌'
        d.update(float_rod(F_LIFT_MAX, L0 + (Y_CP - Y_ROD) * th - G_UP, th, 0.2))
    else:
        forced = th - TH_B - BUSH
        d['끼인 뒤 로드에 강제되는 각 rad(부시 틈 0.006 뺌)'] = round(forced, 4)
        if forced <= 0:
            d['판정'] = '맞모 방향이면 %.3f rad 낌 — 부시 틈(임시 0.006) 안이라 굽힘 없음(여유 없음)' % (th - TH_B)
            d.update(float_rod(F_LIFT_MAX, L0 + ext, TH_B, 0.2))
        else:
            d['판정'] = '낌 -> 로드 굽음(첫 항복 각 0.0003 rad의 %.0f배)' % (forced / 0.0003)
            d['끼인 뒤'] = wedged(L0 + ext, H_T - ext, ARM_T, F_LIFT_MAX * (Y_CP - Y_ROD) - W * (Y_CP - Y_CG))
    C[tag] = d
# ---------- C. 누름 · 끝 들기: 바닥 +Y 끝(매트) 둘레, 멈춤 턱 ----------
for tag, dz in (('C1 누름(-0.4)·끝 들기', 4.9), ('C2 누름(매트 윗면 -2.5)·끝 들기', 7.0)):
    th = (G_STOP + dz) / (Y_FRONT - Y_STOP)
    Sc = (HAND * (Y_FRONT - Y_TIP) - F_HI * (Y_FRONT - Y_ROD) - W * (Y_FRONT - Y_CG)) / (Y_FRONT - Y_STOP)
    C[tag] = {'기울기 rad': round(th, 4), '-Y 칼라가 먼저 닿는 기울기 rad': round((G_UP + dz) / (Y_FRONT - Y_CN), 4), '멈춤 턱 힘 N': round(Sc, 1),
              '로드 축 힘 = 탭 힘 N': F_HI, '너트 축 틈 필요 / 있음': [round(gap_need(th), 3), G_NUT], '로드 옆 이동 / 장공 틈': [round((H_T - dz) * th, 2), round(SLOT_Y, 2)],
              **float_rod(F_HI, L0 + dz + G_NUT, th, 0.2)}
# ---------- D·E. 매트 없이 -5.0까지 누른 채(운전 사이클 밖 — 기록) ----------
thD = (G_STOP + G_DN) / (Y_CP - Y_STOP)
C['D 누름 -5.0(매트 없음)·끝 들기'] = {'기울기 rad': round(thD, 4), '너트 축 틈 필요 / 있음': [round(gap_need(thD), 3), G_NUT],
    '끼인 뒤': wedged(L0 + G_DN + G_NUT, H_T - G_DN, ARM_T, F_HI * (Y_CP - Y_ROD) + W * (Y_CP - Y_CG))}
thE = min(TH_KIN, (Z_SHOE - G_DN - Z_BALL) / (Y_CN - Y_FLAT))
C['E 누름 -5.0(매트 없음)·끝 누르기'] = {'기울기 rad(볼 윗점)': round(thE, 4), '너트 축 틈 필요 / 있음': [round(gap_need(thE), 3), G_NUT],
    '끼인 뒤': wedged(L0 + G_DN, H_T - G_DN, Y_CN - Y_TIP, 0.0)}
R['경우'] = C

# ---------- 고친 뒤(what-if, 실형상 경계조건): 너트 축 틈 g2, 장공 +Y 틈 s2 ----------
G2, S2 = 2.2, 7.0
ext = (Y_CP - Y_ROD) * TH_KIN - G_UP
R['고친 뒤 what-if'] = {'가장 큰 기울기 rad(칼라 장공 끝 = 기구 한도)': round(TH_KIN, 4), '너트 축 틈 필요(맞모) / 제안': [round(gap_need(TH_KIN), 3), G2],
    '로드 옆 이동(윗날개가 -Y로) / 제안 +Y 틈': [round(H_T * TH_KIN, 2), S2], '끝 들기 쪽(-Y 틈 그대로 %.1f) 가장 큰 옆 이동(C2·D)' % SLOT_Y: [C['C2 누름(매트 윗면 -2.5)·끝 들기']['로드 옆 이동 / 장공 틈'][0], round((H_T - G_DN) * thD, 2)],
    '로드 굽힘(축 37.4 N, 내민 길이 %.1f)' % (L0 + ext): float_rod(F_LIFT_MAX, L0 + ext, TH_KIN, 0.2),
    '로드 내밈 합 mm(누름 -5.0 + 틈) / 행정': [round(G_DN + G2, 2), 15.0], '끼는 기울기 rad(틈 %.1f)' % G2: round(bind_angle(G2), 4),
    '아래 너트 밑 Z(누름 -5.0, 로드가 틈만큼 더 나옴) / 칼라 볼트 머리 윗 Z(어림 32.5 + 4.25)': [round(49.3 - G_DN - G2, 2), 36.75],
    '칼라 2개가 받는 짝힘 N(끝 누르기 100 N, 팔 110 / 40)': round(HAND * ARM_T / (Y_CP - Y_CN)), '슈 +Y 밑 모서리 Y 이동(E32까지 3.606)': round(15.5 * math.sin(TH_KIN) - 20 * (1 - math.cos(TH_KIN)), 2)}

# ---------- 새 하중 길: 멈춤 턱 -> 혀 -> 벽 + 판 L 단면 -> 벽 볼트 -> 인서트 / 슈 윗날개 ----------
Sx = max(SA, max(C[k]['멈춤 턱 힘 N'] for k in C if k.startswith('C')))
t, w = 3.0, lug_x[1] - lug_x[0]
Y_WALL_END = -216.5
sig_t = 6 * Sx * (Y_WALL_END - Y_STOP) / (w * t * t)
A1, z1, A2, z2 = 3 * 19.7, 9.85, 19 * 3, 1.5
zc = (A1 * z1 + A2 * z2) / (A1 + A2)
I = 3 * 19.7 ** 3 / 12 + A1 * (z1 - zc) ** 2 + 19 * 27 / 12 + A2 * (z2 - zc) ** 2 - (3 * 5.5 ** 3 / 12 + 3 * 5.5 * (11.7 - zc) ** 2)
sig_L = Sx * (-177.0 - Y_STOP) * (19.7 - zc) / I
J = (19.7 + 19.0) * t ** 3 / 3
x_mid = (lug_x[0] + lug_x[1]) / 2
Tq = Sx * (x_mid + 80.5)
tau = Tq * t / J
vm = math.sqrt((KB * sig_L) ** 2 + 3 * tau ** 2)
d_tw = Tq * (-177.0 - Y_WALL_END) / (79000 * J) * (x_mid + 80.5)
d_b = Sx * (-177.0 - Y_STOP) ** 3 / (3 * E * I) + Sx * (Y_WALL_END - Y_STOP) ** 3 / (3 * E * w * 27 / 12)
V1 = Sx * (-128.0 - Y_STOP) / 49.0
T1 = Sx * (x_mid + 82.0) / 8.0
c = calc(d=5, le=8, load=round(T1, 1), torque=0, bolt='12.9', base='PET-CF', sf_min=2.0)
wingc = {}
for tag, xc in (('턱 벽 쪽 끝 X %.1f(손이 입술 벽 쪽)' % lug_x[0], lug_x[0]), ('손이 입술 가운데(X -68.5) — 합력 자리', (HAND * -68.5 + FA * -68.0) / (HAND + FA)), ('윗날개 바깥 끝 X %.1f(손이 입술 바깥 모서리)' % wing_xy[0][1], wing_xy[0][1])):
    a = xc + 80.0
    b = (Y_STOP - wing_xy[1][0]) + a
    s = 6 * Sx * a / (b * T_WING ** 2)
    wingc[tag] = {'팔·유효 폭': [round(a, 2), round(b, 2)], 'σ MPa': round(s, 1), 'SF(굽힘 계수 1.3)': round(SY / (KB * s), 2)}
R['새 하중 길'] = {'가장 큰 멈춤 힘 N': round(Sx, 1), '턱 밑면 압축 MPa': round(Sx / (w * t), 2),
    '혀(%.1f x t3) 뿌리 굽힘 MPa / SF' % w: [round(sig_t, 1), round(SY / (KB * sig_t), 2)],
    'L 단면(벽 + 판, 구멍 뺌) I mm4 · 볼트 Y -177 자리 굽힘 MPa · 비틀림 τ MPa · 합성 SF': [round(I), round(sig_L, 1), round(tau, 1), round(SY / vm, 2)],
    '턱 처짐 mm(굽힘 + 비틀림) / 턱 틈과 칼라·너트 틈 차이': [round(d_b + d_tw, 3), round(min(G_UP, G_NUT) - G_STOP, 2)],
    '가까운 벽 볼트 Z 전단 N / PET-CF 받음 SF(옛 77.6 N -> 40.2 비례)': [round(V1), round(40.2 * 77.6 / V1, 1)],
    '벽 볼트 인장 N(가까운 볼트가 다 받음, 팔 8) / 인서트 뽑힘 SF(임시 1,000 N)': [round(T1), round(1000 / T1, 2)],
    'handcalc(나사산, PET-CF 직접 탭 가정·참고)': {k: c[k] for k in c if k.startswith('sf')},
    '슈 윗날개(t2) 턱에 눌림 — 닿는 자리별': wingc,
    '윗날개 탭(로드 힘) SF = 2.72 x 100 / 힘': {'A': round(272 / FA, 2), 'B': round(272 / F_LIFT_MAX, 2), 'C': round(272 / F_HI, 2)},
    '너트 ↔ 장공 옆 살(맞변 7 - 폭 5, X 틈 ±0.5) 받음 MPa(37.4 N, 한쪽 0.5 x 7 + 1.5 x 7)': round(F_LIFT_MAX / 14.0, 1)}
dW = (139.615 - 139.782) / 1000 * 9.80665
R['그대로인 값'] = {'슈 질량 g': 139.615, '무게 변화 N': round(dW, 4), '잡음 비': round((9.85 + dW) / 9.36, 3), '자국 SF': round(2.285 * 21.59 / (21.59 + dW), 3), '들기 SF': 5.34}
json.dump(R, open(ROOT + '/fea/results/mech_RX-10_F1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
for k in ('step', '입력', '끼는 기울기 rad(너트 축 틈 0.6)'):
    print(k, json.dumps(R[k], ensure_ascii=False))
for k, v in C.items():
    print(k, json.dumps(v, ensure_ascii=False))
for k in ('고친 뒤 what-if', '새 하중 길', '그대로인 값'):
    print(k, json.dumps(R[k], ensure_ascii=False))
