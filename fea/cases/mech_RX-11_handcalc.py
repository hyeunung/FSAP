# -*- coding: utf-8 -*-
"""RX-11 해석부 손계산(2026-11-13, v2.17.0). FEA 못 함 — 환경 없음(자료대기 D-16).
U5 먼 쪽 바퀴 밑 받침: X축 자유 롤러 2줄(STEP대기_RORLM20-6-L200 x14 + STEP대기_SFJ6-213 x14),
새들 P_RX11_SADDLE x8 · 클램프 P_RX11_CLAMP x8 · CB5-20_RX11 x8, 고친 판 P_M04_PANEL_W2·E2(긴 홈), 가로대 HFS8-4080-560_M04_NOTCH(통과 홈).
설계안 손계산(tools/out/mech_RX-11/design/rx11design.py)과 다른 점:
 - 새들은 귀 단면(14 x 6)만 보지 않고 볼트 예압이 만드는 3점 굽힘을 STEP 최소 단면(축 홈 포켓 자리 = 바닥 살 + 가운데 벽 2, 볼트 구멍·카운터보어 자리)으로 본다.
 - 가로대 통과 홈 단면은 STEP 끝면·홈 벽면의 윤곽을 적분해 I를 구한다(옛 모델은 I 하한 1.5e5 통짜).
 - 판 W2 레일 ±100 사이는 긴 홈으로 끊겨 '경간 160 판'이 아니라 '외팔 57 두 장'이다(모델 바꿈, 옛 모델 값도 남김).
단면은 STEP 글자 파싱 값으로 확인한다(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로").
실행: python -X utf8 -B fea/cases/mech_RX-11_handcalc.py
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEPD = ROOT + '/tools/out/mech_RX-11/stepout/'
g = 9.81
SF_OP, SF_MIS, SF_PERM = 3.0, 2.0, 1.2          # 요구서 6-1 '기본값 — M-09', 영구 변형 선 1.2(지시문)
SY = {'A5052': 195.0, 'SUS304': 205.0, 'A6063-T5': 145.0}
E_ST, E_SUS, E_AL, NU = 206000.0, 193000.0, 70000.0, 0.3
F_OP, F_MIS, F_HAND = 46.54, 130.0, 100.0        # 바퀴 누름(운전), 오설정 바닥, 손(오조작)
R = {'_설명': 'RX-11 해석부 손계산. 좌표 = 세계 좌표(mm), REST. 힘 N, 응력 MPa'}


# ---------- 0. STEP 형상 ----------
def step_ent(path):
    txt = re.sub(r"\s*\n\s*", "", open(path, encoding="latin-1").read())
    ent = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*?)\);", txt)}
    cplx = {m.group(1): m.group(2) for m in re.finditer(r"#(\d+)\s*=\s*\((BOUNDED_CURVE.*?)\);", txt)}
    return ent, cplx


def nums(s):
    m = re.search(r"\(([-0-9.Ee+,\s]+)\)", s)
    return tuple(float(v) for v in m.group(1).split(",")) if m else None


def step_geo(path):
    ent, _ = step_ent(path)
    pts = {k: nums(v[1]) for k, v in ent.items() if v[0] == "CARTESIAN_POINT"}
    dirs = {k: nums(v[1]) for k, v in ent.items() if v[0] == "DIRECTION"}
    V = [pts[re.findall(r"#(\d+)", v[1])[0]] for v in ent.values() if v[0] == "VERTEX_POINT"]
    bb = [[round(min(p[i] for p in V), 3), round(max(p[i] for p in V), 3)] for i in range(3)]
    cyl = set()
    for v in ent.values():
        if v[0] == "CYLINDRICAL_SURFACE":
            refs = re.findall(r"#(\d+)", v[1]); rad = float(v[1].split(",")[-1])
            ar = re.findall(r"#(\d+)", ent[refs[0]][1]); o = pts[ar[0]]; d = dirs[ar[1]]
            main = max(range(3), key=lambda i: abs(d[i]))
            cyl.add((round(rad, 3), 'XYZ'[main], tuple(round(o[i], 2) for i in range(3) if i != main)))
    return {'bbox': bb, 'n_vertex': len(V), 'solid': sum(1 for v in ent.values() if v[0] == 'MANIFOLD_SOLID_BREP'), 'cyl': sorted(cyl),
            'x': sorted({round(p[0], 2) for p in V}), 'y': sorted({round(p[1], 2) for p in V}), 'z': sorted({round(p[2], 2) for p in V})}


GEO = {n: step_geo(STEPD + n + '.step') for n in ('P_RX11_SADDLE', 'P_RX11_CLAMP', 'P_M04_PANEL_W2', 'P_M04_PANEL_E2', 'HFS8-4080-560_M04_NOTCH')}
gs, gc, gw, ge, gh = (GEO[n] for n in ('P_RX11_SADDLE', 'P_RX11_CLAMP', 'P_M04_PANEL_W2', 'P_M04_PANEL_E2', 'HFS8-4080-560_M04_NOTCH'))
# 손계산에 쓰는 치수가 STEP과 같은지 확인(다르면 멈춤)
assert gs['bbox'] == [[-1845.0, -1831.0], [-26.5, 26.5], [-16.0, -2.0]], gs['bbox']
assert gs['x'] == [-1845.0, -1841.88, -1840.25, -1839.0, -1837.0, -1835.75, -1834.12, -1831.0], gs['x']      # 포켓 깊이 6, 가운데 벽 2
assert [y for y in gs['y'] if y > 0] == [1.58, 2.73, 7.9, 14.1, 22.5, 26.5], gs['y']                           # 축 홈 Y 7.9~14.1, 몸통 22.5, 귀 26.5
assert gs['z'] == [-16.0, -9.9, -8.0, -2.0] and (3.1, 'X', (11.0, -9.9)) in gs['cyl'] and (4.75, 'Z', (-1838.0, -0.0)) in gs['cyl'] and (2.75, 'Z', (-1838.0, -0.0)) in gs['cyl']
assert gc['bbox'] == [[-1845.0, -1831.0], [-30.0, 30.0], [-31.0, -12.0]] and gc['z'] == [-31.0, -16.5, -12.0] and (2.1, 'Z', (-1838.0, -0.0)) in gc['cyl']
assert gw['bbox'] == [[-2175.0, -410.0], [-300.0, 300.0], [-12.0, -8.0]] and 23.0 in gw['y'] and -1847.0 in gw['x']
assert (18.0, 'Z', (-1850.0, 50.0)) in gw['cyl'] and (18.0, 'Z', (-750.0, 50.0)) in gw['cyl'] and (2.75, 'Z', (-600.0, 100.0)) in gw['cyl']
assert ge['bbox'] == [[-410.0, 975.0], [-300.0, 300.0], [-12.0, -8.0]] and -317.0 in ge['x'] and (18.0, 'Z', (-350.0, 50.0)) in ge['cyl'] and (2.75, 'Z', (-400.0, 50.0)) in ge['cyl']
assert gh['bbox'] == [[-420.0, -380.0], [-280.0, 280.0], [-92.0, -12.0]] and gh['y'] == [-280.0, -24.0, 24.0, 280.0] and -23.0 in gh['z']
R['step_geo'] = {k: {kk: (vv if kk != 'cyl' else len(vv)) for kk, vv in v.items() if kk in ('bbox', 'n_vertex', 'solid', 'cyl')} for k, v in GEO.items()}


# ---------- 1. 가로대 통과 홈 단면(STEP 윤곽 적분) ----------
def bspline_pts(body, pts, n=6):
    cp = [pts[r] for r in re.findall(r"#(\d+)", re.search(r"B_SPLINE_CURVE\((\d+),\(([^)]*)\)", body).group(2))]
    deg = int(re.search(r"B_SPLINE_CURVE\((\d+),", body).group(1))
    km = re.search(r"B_SPLINE_CURVE_WITH_KNOTS\(\(([^)]*)\),\(([^)]*)\)", body)
    mult = [int(v) for v in km.group(1).split(",")]; kv = [float(v) for v in km.group(2).split(",")]
    U = [k for k, m in zip(kv, mult) for _ in range(m)]
    wm = re.search(r"RATIONAL_B_SPLINE_CURVE\(\(([^)]*)\)\)", body)
    W = [float(v) for v in wm.group(1).split(",")] if wm else [1.0] * len(cp)

    def N(i, p, u):
        if p == 0:
            return 1.0 if (U[i] <= u < U[i + 1]) or (u == U[-1] and U[i] < u <= U[i + 1]) else 0.0
        a = (u - U[i]) / (U[i + p] - U[i]) * N(i, p - 1, u) if U[i + p] > U[i] else 0.0
        b = (U[i + p + 1] - u) / (U[i + p + 1] - U[i + 1]) * N(i + 1, p - 1, u) if U[i + p + 1] > U[i + 1] else 0.0
        return a + b
    out = []
    spans = sorted(set(kv)); us = []
    for a, b in zip(spans[:-1], spans[1:]):
        us += [a + (b - a) * j / n for j in range(n)]
    us.append(spans[-1])
    for u in us:
        ws = [N(i, deg, u) * W[i] for i in range(len(cp))]; s = sum(ws)
        out.append(tuple(sum(ws[i] * cp[i][c] for i in range(len(cp))) / s for c in range(3)))
    return out


def section_faces(path, yplane):
    """법선이 ±Y이고 Y = yplane인 평면 면들의 (x, z) 윤곽 → 넓이·1차·2차 모멘트(z 0 기준) 합."""
    ent, cplx = step_ent(path)
    pts = {k: nums(v[1]) for k, v in ent.items() if v[0] == "CARTESIAN_POINT"}
    dirs = {k: nums(v[1]) for k, v in ent.items() if v[0] == "DIRECTION"}
    vtx = {k: pts[re.findall(r"#(\d+)", v[1])[0]] for k, v in ent.items() if v[0] == "VERTEX_POINT"}
    A = S = I0 = Sx = 0.0; nf = 0
    for k, v in ent.items():
        if v[0] != "ADVANCED_FACE":
            continue
        refs = re.findall(r"#(\d+)", v[1]); surf = ent.get(refs[-1])
        if not surf or surf[0] != "PLANE":
            continue
        ax = re.findall(r"#(\d+)", ent[re.findall(r"#(\d+)", surf[1])[0]][1])
        o, nrm = pts[ax[0]], dirs[ax[1]]
        if abs(abs(nrm[1]) - 1) > 1e-6 or abs(o[1] - yplane) > 1e-6:
            continue
        nf += 1
        for b in refs[:-1]:
            outer = ent[b][0] == "FACE_OUTER_BOUND"
            loop = ent[re.findall(r"#(\d+)", ent[b][1])[0]]
            poly = []
            for oe in re.findall(r"#(\d+)", loop[1]):
                e = ent[oe][1]; ec = re.findall(r"#(\d+)", e)[0]; fwd = e.strip().endswith(".T.")
                er = re.findall(r"#(\d+)", ent[ec][1]); p1, p2 = vtx[er[0]], vtx[er[1]]
                if er[2] in cplx:
                    seg = bspline_pts(cplx[er[2]], pts)
                    if math.dist(seg[0], p1) > math.dist(seg[0], p2) or (er[0] == er[1] and not ent[ec][1].strip().endswith(".T.")):
                        seg = seg[::-1]
                else:
                    seg = [p1, p2]
                if not fwd:
                    seg = seg[::-1]
                poly += [(p[0], p[2]) for p in seg[:-1]]
            a = s = i0 = sx = 0.0
            for (x1, z1), (x2, z2) in zip(poly, poly[1:] + poly[:1]):
                c = x1 * z2 - x2 * z1
                a += c / 2; s += (z1 + z2) * c / 6; i0 += (z1 * z1 + z1 * z2 + z2 * z2) * c / 12; sx += (x1 + x2) * c / 6
            sg = (1 if a > 0 else -1) * (1 if outer else -1)
            A += sg * a; S += sg * s; I0 += sg * i0; Sx += sg * sx
    return {'faces': nf, 'A': A, 'S': S, 'I0': I0, 'Sx': Sx}


# SolidCraft 내보내기에는 FACE_OUTER_BOUND가 없고 FACE_BOUND뿐이다 → 면마다 넓이가 가장 큰 윤곽을 바깥으로 본다
def section_faces2(path, yplane):
    ent, cplx = step_ent(path)
    pts = {k: nums(v[1]) for k, v in ent.items() if v[0] == "CARTESIAN_POINT"}
    dirs = {k: nums(v[1]) for k, v in ent.items() if v[0] == "DIRECTION"}
    vtx = {k: pts[re.findall(r"#(\d+)", v[1])[0]] for k, v in ent.items() if v[0] == "VERTEX_POINT"}
    tot = [0.0, 0.0, 0.0]; nf = 0
    for k, v in ent.items():
        if v[0] != "ADVANCED_FACE":
            continue
        refs = re.findall(r"#(\d+)", v[1]); surf = ent.get(refs[-1])
        if not surf or surf[0] != "PLANE":
            continue
        ax = re.findall(r"#(\d+)", ent[re.findall(r"#(\d+)", surf[1])[0]][1])
        o, nrm = pts[ax[0]], dirs[ax[1]]
        if abs(abs(nrm[1]) - 1) > 1e-6 or abs(o[1] - yplane) > 1e-6:
            continue
        nf += 1; loops = []
        for b in refs[:-1]:
            loop = ent[re.findall(r"#(\d+)", ent[b][1])[0]]
            poly = []
            for oe in re.findall(r"#(\d+)", loop[1]):
                e = ent[oe][1]; ec = re.findall(r"#(\d+)", e)[0]; fwd = e.strip().endswith(".T.")
                er = re.findall(r"#(\d+)", ent[ec][1]); p1, p2 = vtx[er[0]], vtx[er[1]]
                if er[2] in cplx:
                    seg = bspline_pts(cplx[er[2]], pts)
                    if math.dist(seg[0], p1) > math.dist(seg[0], p2):
                        seg = seg[::-1]
                else:
                    seg = [p1, p2]
                if not fwd:
                    seg = seg[::-1]
                poly += [(p[0], p[2]) for p in seg[:-1]]
            a = s = i0 = 0.0
            for (x1, z1), (x2, z2) in zip(poly, poly[1:] + poly[:1]):
                c = x1 * z2 - x2 * z1
                a += c / 2; s += (z1 + z2) * c / 6; i0 += (z1 * z1 + z1 * z2 + z2 * z2) * c / 12
            sg = 1 if a > 0 else -1
            loops.append((sg * a, sg * s, sg * i0))
        loops.sort(reverse=True)
        for j, (a, s, i0) in enumerate(loops):
            f = 1 if j == 0 else -1
            tot[0] += f * a; tot[1] += f * s; tot[2] += f * i0
    return {'faces': nf, 'A': tot[0], 'S': tot[1], 'I0': tot[2]}


pH = STEPD + 'HFS8-4080-560_M04_NOTCH.step'
full = section_faces2(pH, -280.0)            # 끝면 = 온 단면
cut = section_faces2(pH, 24.0)               # 통과 홈 벽면 = 잘려 나간 단면(Z -23 위)
zf = full['S'] / full['A']; If = full['I0'] - full['A'] * zf ** 2
An = full['A'] - cut['A']; zn = (full['S'] - cut['S']) / An; In = (full['I0'] - cut['I0']) - An * zn ** 2
V_STEP = 624561.05 - 9713.0                  # 모델링 보고 부피(온 것 624,561.05, 홈 -9,713)
sec = {'온 단면': {'faces': full['faces'], 'A_mm2': round(full['A'], 1), 'z_c': round(zf, 2), 'I_mm4': round(If), 'Z_top_mm3': round(If / (-12 - zf)), 'Z_bot_mm3': round(If / (zf + 92))},
       '홈에서 잘린 단면(Z -23 위)': {'faces': cut['faces'], 'A_mm2': round(cut['A'], 1)},
       '홈 자리 남은 단면(Z -92 ~ -23)': {'A_mm2': round(An, 1), 'z_c': round(zn, 2), 'I_mm4': round(In), 'Z_top_mm3': round(In / (-23 - zn)), 'Z_bot_mm3': round(In / (zn + 92))},
       '_확인': {'A x 560 (mm3)': round(full['A'] * 560), '모델 부피(온 것)': 624561.05, '잘린 A x 48 (mm3)': round(cut['A'] * 48), '모델 홈 부피': 9713.0},
       '옛 모델 I 하한': 1.5e5}
assert abs(full['A'] * 560 - 624561.05) / 624561.05 < 0.01, full['A'] * 560
assert abs(cut['A'] * 48 - 9713.0) / 9713.0 < 0.02, cut['A'] * 48
R['가로대 단면(STEP 윤곽 적분)'] = sec

# ---------- 2. 롤러·베어링·축 ----------
D_R, DI_R, L_R, B_BRG = 20.0, 12.0, 200.0, 5.0          # RORLM20-6-L200: 외경 20, 스틸 파이프 안지름 12, 길이 200, B696ZZ 폭 5 (catalog.md)
SPAN = L_R - B_BRG                                      # 베어링 중심 사이 195
I_R = math.pi / 64 * (D_R ** 4 - DI_R ** 4)
C0R, CR = 670.0, 1730.0                                 # 696ZZ NSK 치수표 값(임시, D-200)
ARM_SH = B_BRG / 2 + 1.0 + 5.5 / 2                      # 베어링 중심 → 새들 홈 받침 가운데: 2.5 + 틈 1.0 + 물림 5.5 / 2 = 6.25 (설계 5.75)
Z_SH = math.pi * 6 ** 3 / 32; I_SH = math.pi * 6 ** 4 / 64
E_star = 1 / ((1 - 0.3 ** 2) / E_ST + (1 - 0.33 ** 2) / E_AL)
R_eff = 1 / (1 / 3.0 - 1 / 3.1)                         # 축 R3 ↔ 홈 R3.1 (오목)
rl = {}
for tag, F, sfm in (('운전 46.54 N', F_OP, SF_OP), ('오설정 130 N', F_MIS, SF_MIS)):
    d_r = F * SPAN ** 3 / (48 * E_ST * I_R)             # 롤러 하나가 다 받고 가운데(불리)
    s_r = F * SPAN / 4 / (I_R / (D_R / 2))
    w = F / 5.5; p0 = math.sqrt(w * E_star / (math.pi * R_eff))
    rl[tag] = {'롤러 처짐 mm(한 줄이 다 받음, 가운데)': round(d_r, 4), '두 줄 반씩이면 mm': round(d_r / 2, 4), '기준 mm': 0.1, 'ok': d_r <= 0.1,
               '롤러 굽힘 MPa': round(s_r, 2),
               '696ZZ 정적 SF(한 베어링이 다 받음)': round(C0R / F, 2), '696ZZ 정적 SF(C0r 절반 335 N이어도)': round(C0R / 2 / F, 2), 'SF 기준': sfm, 'brg_ok': C0R / F >= sfm,
               '과사양 선(기준 x3)': 3 * sfm, '과사양': C0R / F >= 3 * sfm,
               '축 굽힘 MPa(팔 6.25)': round(F * ARM_SH / Z_SH, 1), '축 처짐 mm': round(F * ARM_SH ** 3 / (3 * E_ST * I_SH), 5),
               '축-홈 투영 면압 MPa': round(F / (6 * 5.5), 2), '축-홈 Hertz p0 MPa': round(p0, 1), 'Hertz SF(항복 시작 1.67 x 195)': round(1.67 * SY['A5052'] / p0, 2)}
rl['L10(46.54 N, Cr 1730 임시) 10^6 회전'] = round((CR / F_OP) ** 3)
rl['_단면'] = {'I_roller_mm4': round(I_R, 1), '베어링 중심 사이': SPAN, 'ARM_SH': ARM_SH}
R['롤러·베어링·축'] = rl

# ---------- 3. 새들·클램프(볼트 예압이 만드는 3점 굽힘) ----------
TX = 14.0                                                # X 두께(STEP -1845 ~ -1831)


def sec_T(parts):
    """parts = [(폭 X, z0, z1)] → A, 도심, I, 위·아래 끝 거리"""
    A = sum(b * (z1 - z0) for b, z0, z1 in parts); zc = sum(b * (z1 - z0) * (z0 + z1) / 2 for b, z0, z1 in parts) / A
    I = sum(b * (z1 - z0) ** 3 / 12 + b * (z1 - z0) * ((z0 + z1) / 2 - zc) ** 2 for b, z0, z1 in parts)
    zt, zb = max(p[2] for p in parts), min(p[1] for p in parts)
    # 소성 단면 계수(넓이 이등분 선)
    lo, hi = zb, zt
    for _ in range(60):
        mid = (lo + hi) / 2
        a_lo = sum(b * max(0.0, min(z1, mid) - z0) for b, z0, z1 in parts)
        lo, hi = (mid, hi) if a_lo < A / 2 else (lo, mid)
    zp = (lo + hi) / 2; Zp = 0.0
    for b, z0, z1 in parts:
        for a0, a1 in ((z0, min(z1, zp)), (max(z0, zp), z1)):
            if a1 > a0:
                Zp += b * (a1 - a0) * abs((a0 + a1) / 2 - zp)
    return {'A': A, 'zc': zc, 'I': I, 'c_top': zt - zc, 'c_bot': zc - zb, 'Zp': Zp}


def saddle_sec(y):
    y = abs(y)
    if y < 2.75:      # 볼트 구멍 Ø5.5 + 카운터보어 Ø9.5(바닥 Z -8)
        return sec_T([(TX - 5.5, -16.0, -8.0), (TX - 9.5, -8.0, -2.0)])
    if y < 4.75:      # 카운터보어만(현 폭)
        ch = 2 * math.sqrt(4.75 ** 2 - y ** 2); h = 2 * math.sqrt(max(0.0, 2.75 ** 2 - y ** 2)) if y < 2.75 else 0.0
        return sec_T([(TX - h, -16.0, -8.0), (TX - ch, -8.0, -2.0)])
    if 7.9 < y < 14.1:   # 축 홈 포켓: 바닥 = R 3.1 호(중심 Z -9.9), 가운데 벽 2
        zfl = -9.9 - math.sqrt(3.1 ** 2 - (y - 11.0) ** 2)
        return sec_T([(TX, -16.0, zfl), (2.0, zfl, -2.0)])
    if y <= 22.5:
        return sec_T([(TX, -16.0, -2.0)])
    return sec_T([(TX, -8.0, -2.0)])     # 귀


def saddle(P, y_r):
    """볼트 축력 P(가운데, 머리 좌면 평균 반지름 3.5의 고리), 귀 반력 자리 y_r. 굽힘 응력과 축 자리(Y 11) 내려앉음."""
    Rr = P / 2; y_h = 2 * 3.5 / math.pi                 # 고리 하중을 양쪽 두 점으로(도심)
    def M(y):
        y = abs(y)
        return Rr * (y_r - y) - (Rr * (y_h - y) if y < y_h else 0.0)
    rows = {}
    for nm, y in (('Y 0 (구멍 + 카운터보어)', 0.0), ('Y 4.0 (카운터보어 현)', 4.0), ('Y 7.9+ (포켓 안쪽 끝)', 7.9001), ('Y 11 (포켓 가장 깊은 곳)', 11.0), ('Y 14.1- (포켓 바깥 끝)', 14.0999), ('Y 22.5+ (귀 뿌리 14 x 6)', 22.5001)):
        s = saddle_sec(y); m = M(y)
        st, sb = m * s['c_top'] / s['I'], m * s['c_bot'] / s['I']
        rows[nm] = {'M_Nmm': round(m), 'I_mm4': round(s['I'], 1), 'σ_위(압축) MPa': round(st, 1), 'σ_밑(인장) MPa': round(sb, 1),
                    'SF_탄성(195)': round(SY['A5052'] / max(st, sb), 2) if max(st, sb) > 0 else None, 'SF_소성 붕괴(Mp)': round(SY['A5052'] * s['Zp'] / m, 2) if m > 0 else None}
    # 처짐: 귀 받침(y_r) 기준 Y 방향 적분(굽힘 + 전단 k 1.2), 대칭 → 가운데 기울기 0
    n = 4000; dy = y_r / n; th = 0.0; w = 0.0; w11 = None; G = E_AL / 2.6
    ys = [(i + 0.5) * dy for i in range(n)]
    slope = []
    for y in ys:                                         # 가운데(기울기 0)에서 바깥으로 기울기 적분
        s = saddle_sec(y); th += M(y) / (E_AL * s['I']) * dy
        slope.append(th + 1.2 * Rr / (G * s['A']) * (1 if y > y_h else y / y_h))
    w_c = sum(slope) * dy                                # 받침 대비 가운데 내려앉음
    w_11 = sum(sl for y, sl in zip(ys, slope) if y > 11.0) * dy
    return rows, w_c, w_11


def clamp(P, y_r):
    m = P / 2 * y_r; Z = (TX - 5.0) * 14.5 ** 2 / 6       # 가운데 단면: M5 나사 구멍 뺀 9 x 14.5 (Z -31 ~ -16.5)
    return m, m / Z


sd = {'_단면(STEP)': {'Y 11 포켓': {k: round(v, 2) for k, v in saddle_sec(11.0).items()}, 'Y 7.9+ 포켓 끝': {k: round(v, 2) for k, v in saddle_sec(7.9001).items()},
                     'Y 0': {k: round(v, 2) for k, v in saddle_sec(0.0).items()}, '온 단면 14 x 14': {k: round(v, 2) for k, v in saddle_sec(18.0).items()}}}
HEAD_A = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)             # CB5 머리 Ø8.5, 구멍 Ø5.5
EAR_A = 3.5 * TX                                         # 귀 받침 |Y| 23 ~ 26.5
MU_HOLD = 0.15                                           # A5052 ↔ SUS304 마른 면(낮은 쪽, 임시)
F_X_OP = 0.5 * (F_OP + 0.36 * 2)                         # 매트가 X로 미끄러질 때 롤러 2개가 받는 X 힘 상한(μ 0.5) → 새들 하나가 다 받음(불리)
for T in (3.0, 1.0, 0.78, 0.6, 0.42):   # 3.0 = 설계 지정, 0.6 = 권고(DC2-05 누름판과 같은 값), 0.78·0.42 = 0.6 ± 30 % 흩어짐
    P = T * 1000 / (0.2 * 5)
    out = {'예압 N': P}
    for nm, yr in (('반력 귀 받침 가운데 Y 24.75(불리)', 24.75), ('반력 판 홈 가장자리 쪽 Y 23.5(유리)', 23.5)):
        rows, w_c, w_11 = saddle(P, yr)
        worst = min(v['SF_탄성(195)'] for v in rows.values() if v['SF_탄성(195)'])
        out['새들 ' + nm] = {'단면별': rows, '최저 SF_탄성': worst, '최저 SF_소성 붕괴': min(v['SF_소성 붕괴(Mp)'] for v in rows.values() if v['SF_소성 붕괴(Mp)']),
                            '가운데 내려앉음 mm': round(w_c, 4), '축 자리(Y 11) 내려앉음 mm': round(w_11, 4)}
    mc, sc = clamp(P, 26.75); mc2, sc2 = clamp(P, 23.5)
    out['클램프 가운데 굽힘 MPa(기둥 가운데 26.75 / 안쪽 끝 23.5)'] = [round(sc, 1), round(sc2, 1)]
    out['클램프 SF(195)'] = [round(SY['A5052'] / sc, 2), round(SY['A5052'] / sc2, 2)]
    out['머리 좌면 MPa'] = round(P / HEAD_A, 1); out['귀 면압 MPa'] = round(P / 2 / EAR_A, 1)
    out['볼트(handcalc.calc, 물림 11.5, A5052 탭)'] = calc(5, 11.5, 0.0, torque=T, bolt='12.9', base='A5052', dw=8.5, dh=5.5, sf_min=SF_OP)
    out['X 미끄럼 버팀 N(귀 2면만 μ 0.15)'] = round(MU_HOLD * P, 1)
    out['X 미끄럼 SF(운전 %.1f N) / (손 100 N)' % F_X_OP] = [round(MU_HOLD * P / F_X_OP, 2), round(MU_HOLD * P / F_HAND, 2)]
    out['X 미끄럼 SF — 귀 + 클램프 기둥 두 쪽(볼트 구멍 틈 0.25 뒤), 운전 / 손 100 N'] = [round(2 * MU_HOLD * P / F_X_OP, 2), round(2 * MU_HOLD * P / F_HAND, 2)]
    sd['조임 %.2f N·m' % T] = out
R['새들·클램프(볼트 예압)'] = sd
# 바퀴 누름만(예압 없이) 새들이 받는 값 — 작음
rows_op, wc_op, w11_op = saddle(F_MIS, 24.75)
R['새들 — 바퀴 누름 130 N만'] = {'최대 σ MPa': round(max(max(v['σ_위(압축) MPa'], v['σ_밑(인장) MPa']) for v in rows_op.values()), 2), '축 자리 내려앉음 mm': round(w11_op, 5)}

# ---------- 4. 판 W2 긴 홈 살(외팔 57) · E2 끝 새들 ----------
T_P = 4.0; D_PL = E_SUS * T_P ** 3 / (12 * (1 - NU ** 2))
A_TIP = 80.0 - 24.75                                    # 레일 안쪽 면 Y 80 → 귀 받침 가운데 24.75
LIG = 32.0 - 23.0                                       # 홈 가장자리 23 ↔ 볼 구멍 Ø36(Y 50) 가장자리 32 = 9
pw = {'_형상(STEP)': {'홈 |Y|': 23.0, '레일 HFS8-4080-1755 Y': [80, 120], '접시 M5 Y ±100 X 피치 300': True, '볼 구멍 Ø36 Y ±50 X 피치 100': True, '살(홈 ↔ 볼 구멍)': LIG,
                    '새들 X': [-1838, -1622, -1406, -1190, -974, -758, -542], '볼 구멍 줄에 선 새들(X 차 ≤ 12)': [-1838, -758, -542]}}
for tag, F, sfm in (('운전 46.54 N(바퀴가 새들 바로 위)', F_OP, SF_OP), ('오설정 130 N', F_MIS, SF_MIS)):
    P = F / 2
    I50 = 50.0 * T_P ** 3 / 12
    d_fix = P * A_TIP ** 3 / (3 * E_SUS * I50)                              # 유효 폭 50 외팔보(설계 모델)
    d_jar = 0.168 * P * A_TIP ** 2 / D_PL / 0.64                            # 무한 폭 외팔판 끝 점하중(Jaramillo) ÷ 구멍 뺀 살 비 0.64
    m_jar = 0.509 * P / 0.64                                                # 뿌리 단위 폭 모멘트 최대
    th_scr = P * A_TIP * 20.0 / (3 * E_SUS * I50)                           # 뿌리 회전: 접시 볼트 줄(Y 100)까지 뒤 경간 20, 폭 50
    th_far = P * A_TIP * 220.0 / (3 * E_SUS * (216 * 0.64 * T_P ** 3 / 12))  # 볼트가 안 잡는다고 볼 때: 먼 레일 Y 300까지 220, 폭 = 새들 피치 216 x 0.64
    d_lig_ss = P * 36.0 ** 3 / (48 * E_SUS * (LIG * T_P ** 3 / 12))          # 볼 구멍 줄에 선 새들: 살 9 x t4가 구멍 지름 36을 건넘(단순 ~ 고정)
    s_lig = P * 36.0 / 4 / (LIG * T_P ** 2 / 6)
    s_root = 6 * m_jar / T_P ** 2; s_root50 = P * A_TIP / (50.0 * T_P ** 2 / 6)
    pw[tag] = {'한쪽 살 몫 N': round(P, 2),
               '살 끝 처짐 mm — 뿌리 고정(외팔판 / 폭 50 보)': [round(d_jar, 4), round(d_fix, 4)],
               '뿌리 회전 몫 mm(볼트 줄이 잡음 / 안 잡음)': [round(th_scr * A_TIP, 4), round(th_far * A_TIP, 4)],
               '살 끝 처짐 범위 mm': [round(d_jar, 4), round(d_fix + th_far * A_TIP, 4)],
               '볼 구멍 줄 새들 — 살 9 덧처짐 mm(고정 ~ 단순)': [round(d_lig_ss / 4, 4), round(d_lig_ss, 4)],
               '뿌리 응력 MPa(외팔판 / 폭 50 보)': [round(s_root, 1), round(s_root50, 1)], 'SF(205)': round(SY['SUS304'] / max(s_root, s_root50), 2),
               '살 9 굽힘 MPa(단순)': round(s_lig, 1), 'SF_살(205)': round(SY['SUS304'] / s_lig, 2), 'SF 기준': sfm}
# 손 100 N이 홈 옆 볼(Y 50) 하나에: 새 모델(외팔판, 뿌리에서 30) vs 옛 모델(레일 사이 경간 160 긴 판, M04R 결과)
Fh = 100.0 + 0.125 * g
m_h = 0.509 * Fh; s_h = 6 * m_h / T_P ** 2
pw['손 100 N 홈 옆 볼 하나(오조작)'] = {'F': round(Fh, 1), '새 모델: 외팔판 뿌리 σ MPa(끝 하중 계수 0.509, 불리)': round(s_h, 1), 'SF': round(SY['SUS304'] / s_h, 2), 'SF 기준': SF_MIS,
                                 '처짐 mm(a 30 / a 57)': [round(0.168 * Fh * 30 ** 2 / D_PL, 4), round(0.168 * Fh * 57 ** 2 / D_PL, 4)],
                                 '옛 모델(경간 160 긴 판, mech_M04R_handcalc.json)': {'σ MPa': 13.95, 'SF': 14.69, '처짐 mm': 0.077}, '_차이': '홈으로 판이 끊겨 옛 모델은 이 형상에 맞지 않음. 응력 +39 %, SF는 기준 2의 5배'}
# E2 끝 새들(X -326): 가로대 CM1 +X 면(-380) → 귀(-326). 길에 볼 구멍(-350, ±50) → 살 9만 센다(불리). J_U5_X 1380에서 트레드 X -420: 롤러(-534~-334) 받침 -531.5·-336.5
share = (-420.0 - (-531.5)) / SPAN
pe = {'바퀴가 가장 가까울 때(J 1380) 이 새들 몫': round(share, 3)}
for tag, F, sfm in (('운전 46.54 N', F_OP * share, SF_OP), ('오설정 130 N', F_MIS * share, SF_MIS), ('손 100 N 새들 바로 위', F_HAND, SF_MIS)):
    P = F / 2; Lc = -326.0 - (-368.0)                    # 구멍 시작(-368)에서 귀 가운데까지 42, 살 9 x t4 외팔(불리 — 구멍 밖 판은 안 셈)
    Il = LIG * T_P ** 3 / 12
    pe[tag] = {'귀 하나 N': round(P, 2), '살 9 외팔 42 처짐 mm(상한)': round(P * Lc ** 3 / (3 * E_SUS * Il), 4), 'σ MPa(상한)': round(P * Lc / (LIG * T_P ** 2 / 6), 1),
               'SF(205)': round(SY['SUS304'] / (P * Lc / (LIG * T_P ** 2 / 6)), 2), 'SF 기준': sfm}
R['판 W2 긴 홈 살'] = pw; R['판 E2 끝 새들'] = pe

# ---------- 5. 가로대 CM1 통과 홈 ----------
# 하중: 옛 모델(mech_M04R_handcalc.py)과 같은 보수 하중 — E2 전부 + W2 1/4 질량 x3 g 등분포(847.6 - 100 N), 가운데 점하중은 손 100 → 오설정 130 N + RX-11 부품 x3 g
W_dist = 847.6 - 100.0
m_rx11 = 2 * 0.322 + 2 * 0.047 + 0.012 + 0.03 + 0.005   # 롤러 2 + 축 2 + 새들 + 클램프 + 볼트 (kg, 끝 새들 몫 불리)
Pc = F_MIS + m_rx11 * 3 * g
Lcm = 560.0
Mcm = W_dist * Lcm / 8 + Pc * Lcm / 4
cmr = {'W_등분포 N': round(W_dist, 1), 'P_가운데 N': round(Pc, 1), 'M_가운데 N·m': round(Mcm / 1000, 2)}
for nm, I, ct, cb in (('새 모델: STEP 홈 자리 남은 단면', In, -23 - zn, zn + 92), ('온 단면(STEP, 홈 없음)', If, -12 - zf, zf + 92), ('옛 모델: I 하한 1.5e5 · c 40 (통짜)', 1.5e5, 40.0, 40.0)):
    s = Mcm * max(ct, cb) / I
    cmr[nm] = {'I_mm4': round(I), 'σ MPa': round(s, 2), 'SF(145)': round(SY['A6063-T5'] / s, 2), 'SF 기준': SF_MIS}
dlt = 5 * W_dist * Lcm ** 3 / (384 * 69000 * In) + Pc * Lcm ** 3 / (48 * 69000 * In)
cmr['처짐 mm(남은 단면이 온 길이라고 볼 때, 상한)'] = round(dlt, 4)
cmr['운전(자중 x3 g + 46.54 N)'] = {'σ MPa': round((W_dist * Lcm / 8 + (F_OP + m_rx11 * 3 * g) * Lcm / 4) * max(-23 - zn, zn + 92) / In, 2)}
cmr['운전(자중 x3 g + 46.54 N)']['SF(145)'] = round(SY['A6063-T5'] / cmr['운전(자중 x3 g + 46.54 N)']['σ MPa'], 2)
cmr['홈 벽 ↔ 판 E2 접시 볼트(X -400, Y ±50) T너트'] = '홈 |Y| ≤ 24 밖(26 떨어짐) — T홈 남음'
R['가로대 CM1 통과 홈'] = cmr

# ---------- 6. 받침 합 처짐(완료 판정 ④) ----------
tot = {}
for tag, F in (('운전 46.54 N', F_OP), ('오설정 130 N', F_MIS)):
    k = '운전 46.54 N(바퀴가 새들 바로 위)' if F == F_OP else '오설정 130 N'
    rr = rl[tag]['롤러 처짐 mm(한 줄이 다 받음, 가운데)']
    lo, hi = pw[k]['살 끝 처짐 범위 mm']
    tot[tag] = {'롤러(가운데) mm': rr, '판 살(새들 위) mm': [lo, hi], '축 mm': rl[tag]['축 처짐 mm'],
                '받침 합 mm(롤러 가운데 + 살 절반 ~ 새들 위 살 전부 + 볼 구멍 줄 덧처짐)': [round(rr + lo / 2, 4), round(hi + pw[k]['볼 구멍 줄 새들 — 살 9 덧처짐 mm(고정 ~ 단순)'][1] + rl[tag]['축 처짐 mm'], 4)]}
R['받침 합 처짐'] = tot

# ---------- 7. 회전 시간 키·SF(완료 판정 ⑤) — 띠 항 없이 ----------
MJ = json.load(open(ROOT + '/tools/machine.json', encoding='utf-8'))['_timing']
DJ = json.load(open(ROOT + '/tools/out/mech_RX-11/design/rx11design.json', encoding='utf-8'))['timing']
mu, F4, F5, d1, c_ball, c_w, f_row = 0.4, 40.0, 40.0, 0.100, 0.02, 0.05, 0.18
T_ex, I_d, T_f = 0.048, 0.0217, 0.096
m_roll = (math.pi / 4 * (D_R ** 2 - DI_R ** 2) * L_R + 2 * math.pi / 4 * (DI_R ** 2 - 6 ** 2) * B_BRG) * 7.85e-6
m_eq = 0.5 * m_roll * (0.010 ** 2 + 0.006 ** 2) / 0.010 ** 2
RC = [abs((a + a + 200) / 2000) for a in (-1830, -1614, -1398, -1182, -966, -750, -534)]
g1 = MJ['CYCLE_G1_바닥']['U4+U5']; assert '0.8 ×9' in g1 and '3° 0.6' in g1, g1
vk = MJ['CYCLE_V']; wk = MJ['CYCLE_W']
KEYS = [  # (설계 seg 이름 앞머리, 각, d2, machine.json 키, 매트가 덮는 가장 먼 롤러 |x| m)
    ('CYCLE_L 모서리', 90, 1.0, MJ['CYCLE_L_모서리']['U4+U5'], 2.13), ('CYCLE_G2 모서리', 90, 0.8, MJ['CYCLE_G2_모서리']['U4+U5'], 1.70),
    ('CYCLE_G1 출구', 9.5, 0.8, 1.2, 1.50), ('CYCLE_G1 바닥 12°', 12, 0.8, 0.8, 1.50), ('CYCLE_G1 바닥 3°', 3, 0.8, 0.6, 1.50),
    ('CYCLE_V 입구1', 75, 0.44, vk['입구1_U4+U5'], 1.50), ('CYCLE_V 꼭짓점 25°', 25, 0.44, vk['꼭짓점_U4+U5'][0], 1.39), ('CYCLE_V 꼭짓점 10°', 10, 0.44, vk['꼭짓점_U4+U5'][4], 1.39),
    ('CYCLE_V 입구2', 30, 0.44, vk['입구2_U4+U5'], 1.50),
    ('CYCLE_W 볼록 A·D', 90, 0.44, wk['볼록 모서리 A·D_U4+U5_90'], 1.66), ('CYCLE_W 볼록 B·C', 90, 0.44, wk['볼록 모서리 B·C_U4+U5_90'], 1.66),
    ('CYCLE_W 오목 입구', 90, 0.44, wk['오목 입구2·1_U4+U5_90'], 1.66), ('CYCLE_W 오목 안 모서리', 45, 0.44, wk['오목 안 모서리_U4+U5_45'], 1.66)]
tm = {'_가정': {'μ 바퀴–파일': mu, 'F4': F4, 'F5': F5, 'd1': d1, '볼 구름': c_ball, '바퀴 밑 롤러 구름(임시)': c_w, '바퀴 밖 롤러 저항 N': f_row, 'T_원판': T_ex, 'I_원판': I_d, 'T_노루발': T_f,
               '롤러 질량 kg': round(m_roll, 3), '둘레 환산 질량 kg': round(m_eq, 3), 'I_매트·볼 구름 Rg': '설계 rx11design.json segs(앞 과제 DC-02·VGR-01·DC-01·RX-12 값)'}}
sf_all = []
for nm, th_d, d2, key, Rfar in KEYS:
    s = next(x for x in DJ['segs'] if x['seg'].startswith(nm))
    th = math.radians(th_d); I = s['I_mat']; T_ball = s['T_ball']
    have = mu * (F4 * d1 + F5 * d2)
    T_row = 2 * f_row * sum(x for x in RC if x <= Rfar); T_row_all = 2 * f_row * sum(RC)
    Ie = I + I_d + 2 * m_eq * d2 ** 2
    def sf(cw, trow, t=key):
        return have / (T_ball + T_ex + T_f + cw * F5 * d2 + trow + Ie * 4 * th / t ** 2)
    old = have / (T_ball + T_ex + T_f + 0.30 * F5 * d2 + (I + I_d) * 4 * th / s['key_strip'] ** 2)
    row = {'키 s(machine.json)': key, 'have N·m': round(have, 3), 'SF': round(sf(c_w, T_row), 3), 'SF(롤러 구름 0.10)': round(sf(0.10, T_row), 3), 'SF(롤러 14개 다 매트 밑)': round(sf(c_w, T_row_all), 3),
           '설계 SF': s['SF_new'] if abs(s['key_new'] - key) < 1e-9 else None, '옛 띠 키 s · SF(μs 0.30)': [s['key_strip'], round(old, 3)], 'ok': sf(c_w, T_row) >= 1.0}
    tm[nm] = row
    if not nm.startswith('CYCLE_W'):
        sf_all.append((sf(c_w, T_row), nm))
tm['_최저 SF(L·G·V)'] = [round(min(sf_all)[0], 3), min(sf_all)[1]]
tm['_판정'] = all(v['ok'] for k, v in tm.items() if isinstance(v, dict) and 'ok' in v)
R['회전 시간 키·SF(띠 항 없음)'] = tm

json.dump(R, open(ROOT + '/fea/results/mech_RX-11_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 화면 요약(E-20, 15줄 안) ----------
s3 = sd['조임 3.00 N·m']; s06 = sd['조임 0.60 N·m']; s1 = sd['조임 1.00 N·m']; s078 = sd['조임 0.78 N·m']
ka, kb = '새들 반력 귀 받침 가운데 Y 24.75(불리)', '새들 반력 판 홈 가장자리 쪽 Y 23.5(유리)'
print('가로대 단면 A', sec['온 단면']['A_mm2'], 'I 온', sec['온 단면']['I_mm4'], '→ 홈 자리', sec['홈 자리 남은 단면(Z -92 ~ -23)']['I_mm4'], 'A', sec['홈 자리 남은 단면(Z -92 ~ -23)']['A_mm2'], '면', full['faces'], cut['faces'])
print('롤러 처짐', rl['운전 46.54 N']['롤러 처짐 mm(한 줄이 다 받음, 가운데)'], rl['오설정 130 N']['롤러 처짐 mm(한 줄이 다 받음, 가운데)'], '베어링 SF', rl['운전 46.54 N']['696ZZ 정적 SF(한 베어링이 다 받음)'], rl['오설정 130 N']['696ZZ 정적 SF(한 베어링이 다 받음)'])
print('축 굽힘', rl['운전 46.54 N']['축 굽힘 MPa(팔 6.25)'], rl['오설정 130 N']['축 굽힘 MPa(팔 6.25)'], 'Hertz', rl['운전 46.54 N']['축-홈 Hertz p0 MPa'], rl['오설정 130 N']['축-홈 Hertz p0 MPa'])
for T, o in (('3.0', s3), ('1.0', s1), ('0.78', s078), ('0.6', s06)):
    print('조임', T, '새들 SF 탄성', o[ka]['최저 SF_탄성'], '~', o[kb]['최저 SF_탄성'], '소성', o[ka]['최저 SF_소성 붕괴'], '축 자리 내려앉음', o[ka]['축 자리(Y 11) 내려앉음 mm'], '클램프 SF', o['클램프 SF(195)'], '좌면', o['머리 좌면 MPa'], '미끄럼 SF', o['X 미끄럼 SF(운전 %.1f N) / (손 100 N)' % F_X_OP])
print('새들 3.0 단면별', {k: (v['σ_위(압축) MPa'], v['σ_밑(인장) MPa']) for k, v in s3[ka]['단면별'].items()})
print('볼트 3.0', s3['볼트(handcalc.calc, 물림 11.5, A5052 탭)']['sf_tightening'], '0.6', s06['볼트(handcalc.calc, 물림 11.5, A5052 탭)']['sf_tightening'])
print('판 W2', {k: (v.get('살 끝 처짐 범위 mm'), v.get('SF(205)'), v.get('SF_살(205)')) for k, v in pw.items() if '살 끝 처짐 범위 mm' in v}, '손', pw['손 100 N 홈 옆 볼 하나(오조작)']['SF'])
print('판 E2', {k: (v['살 9 외팔 42 처짐 mm(상한)'], v['SF(205)']) for k, v in pe.items() if isinstance(v, dict)})
print('가로대', {k: (v['σ MPa'], v['SF(145)']) for k, v in cmr.items() if isinstance(v, dict) and 'σ MPa' in v}, '처짐', cmr['처짐 mm(남은 단면이 온 길이라고 볼 때, 상한)'])
print('받침 합', {k: v['받침 합 mm(롤러 가운데 + 살 절반 ~ 새들 위 살 전부 + 볼 구멍 줄 덧처짐)'] for k, v in tot.items()})
print('시간 키 SF', {k: (v['키 s(machine.json)'], v['SF'], v['SF(롤러 구름 0.10)'], v['SF(롤러 14개 다 매트 밑)']) for k, v in tm.items() if isinstance(v, dict) and 'SF' in v})
print('최저', tm['_최저 SF(L·G·V)'], '판정', tm['_판정'], '→ fea/results/mech_RX-11_handcalc.json')
