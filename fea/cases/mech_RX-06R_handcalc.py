# -*- coding: utf-8 -*-
"""RX-06R 해석부 손계산(2026-11-13, v2.15.0). FEA 못 함 — 환경 없음(D-16).
새·고친 하중 부품: P_RX06R_LOCK_BLADE_판금(SUS304 t2), P_RX06R_LOCK_CLAMP_레이저(SUS304 t3), P_RX06_CARRIAGE(A5052, 윗부분 자름).
볼트: CB5-16 x2(잠금), CB5-12 x4(날 고정). 구매품 몫: SSEB13 블록 4.
설계안 손계산(tools/out/mech_RX-06R/design/design_calc.py)과 다른 점:
 - 날은 누름 판과 웹 사이에 평평하게 물려 '끝 기울기 0'이다(설계안은 볼트 줄에서 자유롭게 도는 외팔보 L 75).
   -> Z자 판(다리·굽힘·선반·굽힘·플랜지)을 2D 뼈대로 풀었다(단위 폭, 판 강성 E/(1-nu^2)). 설계안 모델도 같은 형상으로 풀어 차이를 남긴다(E-18).
 - 날 고정 볼트 4개: X 힘이 볼트 줄에서 94 아래에 걸려 생기는 면내 모멘트를 더했다.
 - 날 복원력이 캐리지를 -Y로 당겨 블록에 실리는 힘을 뼈대 값으로 다시 셈했다.
단면은 STEP 글자 파싱 값으로 확인한다(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로").
실행: python -X utf8 -B fea/cases/mech_RX-06R_handcalc.py
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEPD = ROOT + '/tools/out/mech_RX-06R/stepout/'
g = 9.81
SF_OP, SF_MIS = 3.0, 2.0                       # 요구서 6-1 '기본값 — M-09'
SY = {'A5052': 195.0, 'SUS304': 205.0}
E_SUS, NU = 193000.0, 0.29
R = {'_설명': 'RX-06R 해석부 손계산. 좌표 = 측정 좌표계(월드), REST J_U4_X 0. 뼈대는 Y-Z 평면, 회전은 +X 둘레'}


# ---------- 0. STEP 형상 ----------
def step_geo(path):
    txt = re.sub(r"\s*\n\s*", "", open(path, encoding="latin-1").read())
    ent = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*?)\);", txt)}

    def nums(s):
        m = re.search(r"\(([-0-9.Ee+,\s]+)\)", s)
        return tuple(float(v) for v in m.group(1).split(",")) if m else None
    pts = {k: nums(v[1]) for k, v in ent.items() if v[0] == "CARTESIAN_POINT"}
    dirs = {k: nums(v[1]) for k, v in ent.items() if v[0] == "DIRECTION"}
    V = []
    for k, v in ent.items():
        if v[0] == "VERTEX_POINT":
            r = re.findall(r"#(\d+)", v[1])
            if r and r[0] in pts:
                V.append(pts[r[0]])
    bb = [[round(min(p[i] for p in V), 3), round(max(p[i] for p in V), 3)] for i in range(3)]
    cyl = set()
    for k, v in ent.items():
        if v[0] == "CYLINDRICAL_SURFACE":
            refs = re.findall(r"#(\d+)", v[1]); rad = float(v[1].split(",")[-1])
            ar = re.findall(r"#(\d+)", ent[refs[0]][1])
            o = pts.get(ar[0]); d = dirs.get(ar[1])
            main = max(range(3), key=lambda i: abs(d[i]))
            cyl.add((round(rad, 3), 'XYZ'[main], tuple(round(o[i], 2) for i in range(3) if i != main)))
    return {'bbox': bb, 'n_vertex': len(V), 'solid': sum(1 for v in ent.values() if v[0] == 'MANIFOLD_SOLID_BREP'),
            'cylinders(r, 축, 축에 수직 자리)': sorted(cyl),
            'x': sorted({round(p[0], 2) for p in V}), 'y': sorted({round(p[1], 2) for p in V}), 'z': sorted({round(p[2], 2) for p in V})}


GEO = {n: step_geo(STEPD + n + '.step') for n in ('P_RX06R_LOCK_BLADE', 'P_RX06R_LOCK_CLAMP', 'P_RX06_CARRIAGE')}
R['step_geo'] = GEO
gb, gc, gk = GEO['P_RX06R_LOCK_BLADE'], GEO['P_RX06R_LOCK_CLAMP'], GEO['P_RX06_CARRIAGE']
# 손계산에 쓰는 치수가 STEP과 같은지 확인(다르면 멈춤)
assert gb['bbox'] == [[-335.0, -122.0], [92.5, 120.0], [457.0, 577.0]], gb['bbox']
assert gb['y'] == [92.5, 94.5, 96.5, 116.0, 118.0, 120.0] and 541.0 in gb['z'] and 547.0 in gb['z']
assert gc['bbox'] == [[-237.5, -127.5], [89.3, 92.3], [458.0, 478.0]], gc['bbox']
assert gk['bbox'] == [[-240.0, -125.0], [45.0, 107.0], [250.0, 482.0]] and 95.0 in gk['y'], gk['bbox']
t_bl = 2.0                                     # 날 두께(Y 92.5~94.5, 118~120 / Z 543~545)
W_BL = 213.0                                   # 날 X 길이
W_PL, H_PL, T_PL = 110.0, 20.0, 3.0            # 누름 판
Z_CLAMP_TOP = 478.0                            # 누름 판 윗끝 = 날이 평평하게 물리는 끝
GAP_NOM, GAP_MAX = 0.5, 0.8                    # 날 뒷면 Y 94.5 ↔ 웹 앞면 Y 95, 굽힘 너머 공차 ±0.3(M-04)


# ---------- 1. 날: 2D 뼈대(단위 폭 1 mm) ----------
def solve(A, b):
    n = len(b); M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / piv
            if f:
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))) / M[r][r]
    return x


def blade_nodes():
    """중립선(Y, Z). 굽힘 안쪽 R2 → 중립선 R3. 'arc' 표시는 곡선보 계수용."""
    P = [(93.5, Z_CLAMP_TOP, 'leg')]
    n = 9
    for i in range(1, n + 1):
        P.append((93.5, Z_CLAMP_TOP + (541.0 - Z_CLAMP_TOP) * i / n, 'leg'))
    for i in range(1, 9):                      # 굽힘 1: 중심 (96.5, 541)
        a = math.pi - (math.pi / 2) * i / 8
        P.append((96.5 + 3 * math.cos(a), 541.0 + 3 * math.sin(a), 'arc1'))
    for i in range(1, 5):                      # 선반 Z 544
        P.append((96.5 + 19.5 * i / 4, 544.0, 'shelf'))
    for i in range(1, 9):                      # 굽힘 2: 중심 (116, 547)
        a = -math.pi / 2 + (math.pi / 2) * i / 8
        P.append((116.0 + 3 * math.cos(a), 547.0 + 3 * math.sin(a), 'arc2'))
    for z in (550.5, 554.0, 557.75, 562.0):    # 플랜지(볼트 머리 Ø8.5 아랫끝 557.75, 볼트 줄 562)
        P.append((119.0, z, 'flange'))
    return P


def frame(delta, E, a_uz_fixed=True, fix_from_z=557.75, beam_contact=False, t=t_bl, fz_A=0.0):
    P = blade_nodes(); nn = len(P); nd = 3 * nn
    K = [[0.0] * nd for _ in range(nd)]
    EA, EI = E * t, E * t ** 3 / 12.0
    els = []
    for i in range(nn - 1):
        y1, z1, _ = P[i]; y2, z2, tag = P[i + 1]
        L = math.hypot(y2 - y1, z2 - z1); c, s = (y2 - y1) / L, (z2 - z1) / L
        kl = [[EA / L, 0, 0, -EA / L, 0, 0],
              [0, 12 * EI / L ** 3, 6 * EI / L ** 2, 0, -12 * EI / L ** 3, 6 * EI / L ** 2],
              [0, 6 * EI / L ** 2, 4 * EI / L, 0, -6 * EI / L ** 2, 2 * EI / L],
              [-EA / L, 0, 0, EA / L, 0, 0],
              [0, -12 * EI / L ** 3, -6 * EI / L ** 2, 0, 12 * EI / L ** 3, -6 * EI / L ** 2],
              [0, 6 * EI / L ** 2, 2 * EI / L, 0, -6 * EI / L ** 2, 4 * EI / L]]
        T = [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
             [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]]
        kT = [[sum(kl[a][m] * T[m][b] for m in range(6)) for b in range(6)] for a in range(6)]
        kg = [[sum(T[m][a] * kT[m][b] for m in range(6)) for b in range(6)] for a in range(6)]
        dof = [3 * i, 3 * i + 1, 3 * i + 2, 3 * i + 3, 3 * i + 4, 3 * i + 5]
        for a in range(6):
            for b in range(6):
                K[dof[a]][dof[b]] += kg[a][b]
        els.append((dof, kT, tag if tag.startswith('arc') or P[i][2].startswith('arc') else tag, L))
    pres = {0: delta, 2: 0.0}
    if a_uz_fixed:
        pres[1] = 0.0
    for i, (y, z, tag) in enumerate(P):
        if tag == 'flange' and z >= fix_from_z - 1e-9:
            pres[3 * i] = 0.0; pres[3 * i + 1] = 0.0; pres[3 * i + 2] = 0.0
    i_c = next(i for i, p in enumerate(P) if abs(p[0] - 119.0) < 1e-9 and abs(p[1] - 547.0) < 1e-9)
    if beam_contact:
        pres[3 * i_c] = 0.0
    free = [d for d in range(nd) if d not in pres]
    A = [[K[r][c] for c in free] for r in free]
    b = [(fz_A if r == 1 else 0.0) - sum(K[r][c] * v for c, v in pres.items()) for r in free]
    xs = solve(A, b)
    u = [0.0] * nd
    for d, v in pres.items():
        u[d] = v
    for d, v in zip(free, xs):
        u[d] = v
    Rct = {d: sum(K[d][c] * u[c] for c in range(nd)) for d in pres}
    out = {'sigma': {}, 'M': {}}
    for dof, kT, tag, L in els:
        f = [sum(kT[a][b] * u[dof[b]] for b in range(6)) for a in range(6)]
        for (m_, n_) in ((f[2], f[0]), (f[5], f[3])):
            ki = 1.285 if tag.startswith('arc') else 1.0      # 곡선보 안쪽 섬유(R 3, c 1 사각 단면)
            sg = ki * 6 * abs(m_) / t ** 2 + abs(n_) / t
            if sg > out['sigma'].get(tag, 0):
                out['sigma'][tag] = sg; out['M'][tag] = abs(m_)
    mA = [sum(els[0][1][a][b] * u[els[0][0][b]] for b in range(6)) for a in range(6)][2]
    out.update({'RA_y': Rct[0], 'RA_z': Rct.get(1, 0.0), 'RA_M': Rct[2], 'M_clamp_edge': abs(mA), 'sigma_clamp_edge': 6 * abs(mA) / t ** 2,
                'uy_flange_547': u[3 * i_c], 'R_beam_contact_y': Rct.get(3 * i_c) if beam_contact else None,
                'sigma_max': max(max(out['sigma'].values()), 6 * abs(mA) / t ** 2)})
    return out


E_pl = E_SUS / (1 - NU ** 2)                    # 폭 110~213 ≫ 길이 63: 판 강성
# 조이는 동안 Z 묶임은 마찰까지만: 틈이 닫히는 순간 볼트 힘 = 닫는 힘이라 Z 마찰 <= mu x 닫는 힘(mu 0.15)
_v1 = frame(1.0, E=E_pl); _v2 = frame(1.0, E=E_pl, a_uz_fixed=False); _u = frame(0.0, E=E_pl, a_uz_fixed=False, fz_A=1.0)
_s = 1.0 if _v1['RA_z'] >= 0 else -1.0
FZ_MU = _s * 0.15 * _v2['RA_y'] / (1 - _s * 0.15 * _u['RA_y'])
Z_RATIO_V1 = abs(_v1['RA_z']) / _v1['RA_y']                  # Z로 묶는 데 드는 힘 / 닫는 힘
variants = {
    'V1_상한(물림 끝 기울기 0·Z 묶임, 플랜지는 볼트 머리 밑에서 고정, 판 강성)': dict(E=E_pl),
    'V1b_같음 + 플랜지 아랫끝이 보 면에 닿음': dict(E=E_pl, beam_contact=True),
    'V2_물림 끝 Z 자유(조이는 동안 날이 Z로 미끄러짐)': dict(E=E_pl, a_uz_fixed=False),
    'V3_보 강성 E(판 효과 없음)': dict(E=E_SUS),
    'V2m_기준(물림 끝 기울기 0, Z는 마찰 한계 mu 0.15 x 닫는 힘까지만 묶임)': dict(E=E_pl, a_uz_fixed=False, fz_A=FZ_MU),
}
bl = {}
for name, kw in variants.items():
    f1 = frame(1.0, **kw)
    bl[name] = {'k_N_per_mm_per_mmwidth': round(f1['RA_y'], 3), 'M_clamp_edge_Nmm_per_mm': round(f1['M_clamp_edge'], 1),
                'sigma_per_mm_gap_MPa': {k: round(v, 1) for k, v in f1['sigma'].items()},
                'sigma_clamp_edge_per_mm_gap_MPa': round(f1['sigma_clamp_edge'], 1), 'sigma_max_per_mm_gap_MPa': round(f1['sigma_max'], 1),
                'uy_flange_547_per_mm_gap': round(f1['uy_flange_547'], 5),
                'R_beam_contact_per_mm': None if f1['R_beam_contact_y'] is None else round(f1['R_beam_contact_y'], 3),
                'RA_M_Nmm_per_mm': round(f1['RA_M'], 1), 'RA_z_N_per_mm': round(f1['RA_z'], 3)}
    for gap in (GAP_NOM, GAP_MAX):
        s = f1['sigma_max'] * gap
        bl[name]['gap_%.1f' % gap] = {'sigma_MPa': round(s, 1), 'SF_yield205': round(SY['SUS304'] / s, 2),
                                      'F_close_N(w 110)': round(f1['RA_y'] * gap * W_PL, 1), 'F_close_N(w 213)': round(f1['RA_y'] * gap * W_BL, 1)}
# 닫힌 식 대조(양쪽 고정·나란히 이동, L 63): sigma = 3Et*d/L^2
bl['check_guided_L63(handcalc.py beam, 뿌리 강체)'] = beam(t=t_bl, b=1.0, length=63.0, deflect=GAP_NOM, e=E_pl, sy=SY['SUS304'], end='guided', sf_min=SF_OP)
# 옛 모델(설계안): 뿌리(Z 543) 고정, 볼트 줄(Z 468)에서 자유롭게 도는 외팔보 L 75, 보 강성 E
old = {}
for gap in (GAP_NOM, GAP_MAX):
    o = beam(t=t_bl, b=W_BL, length=75.0, deflect=gap, e=E_SUS, sy=SY['SUS304'], end='cantilever', sf_min=SF_OP)
    old['gap_%.1f' % gap] = {'sigma_MPa': o['stress_MPa'], 'SF': o['sf'], 'F_close_N': o['force_N'], 'k_N_mm': o['stiffness_N_mm']}
bl['old_model_설계안(외팔보 L75, 볼트 줄 핀)'] = old
UPP = 'V1_상한(물림 끝 기울기 0·Z 묶임, 플랜지는 볼트 머리 밑에서 고정, 판 강성)'
GOV = 'V2m_기준(물림 끝 기울기 0, Z는 마찰 한계 mu 0.15 x 닫는 힘까지만 묶임)'
fu = frame(1.0, E=E_pl)
fg = frame(1.0, E=E_pl, a_uz_fixed=False, fz_A=FZ_MU)
bl['governing'] = GOV
bl['Z_restraint_ratio_V1(RA_z/RA_y)'] = round(Z_RATIO_V1, 2)
bl['RA_M_sign_V1(받침이 날에 주는 모멘트, +X 둘레, N·mm/mm/mm)'] = round(_v1['RA_M'], 1)
bl['criteria'] = {'운전(조임은 평소 작업)': SF_OP, '영구 변형 한계(동작 문제 기준)': 1.2}
bl['fix_whatif(같은 뼈대, 두께·틈만 바꿈)'] = {}
for tt, gp in ((2.0, 0.27), (2.0, 0.2), (1.5, 0.5), (1.2, 0.5), (1.0, 0.5), (1.0, 0.8), (1.0, 0.3), (1.0, 0.6)):
    _a = frame(1.0, E=E_pl, a_uz_fixed=False, t=tt); _b = frame(0.0, E=E_pl, a_uz_fixed=False, fz_A=1.0, t=tt)
    fw = frame(1.0, E=E_pl, a_uz_fixed=False, fz_A=_s * 0.15 * _a['RA_y'] / (1 - _s * 0.15 * _b['RA_y']), t=tt)
    bl['fix_whatif(같은 뼈대, 두께·틈만 바꿈)']['t%.1f_gap%.2f' % (tt, gp)] = {
        'sigma_MPa': round(fw['sigma_max'] * gp, 1), 'SF': round(SY['SUS304'] / (fw['sigma_max'] * gp), 2), 'F_close_N(w 213)': round(fw['RA_y'] * gp * W_BL, 1)}
R['blade_frame'] = bl
kq = fg['RA_y']                                 # N/mm² (단위 폭·단위 틈)


# ---------- 2. 누름 판: 탄성 받침 위 보(X 방향, 볼트 2점 받침) ----------
def plate_bef(delta, kq, n=44):
    """판 X 0~110(월드 -237.5~-127.5), 볼트 x 12.5·97.5. w = 판이 웹에서 멀어지는 쪽 처짐. 날 반력 q = kq(delta - w)."""
    dx = W_PL / n; EI = E_SUS * H_PL * T_PL ** 3 / 12.0
    nd = 2 * (n + 1)
    sup = {int(round(12.5 / dx)), int(round(97.5 / dx))}
    contact = set()
    for _ in range(12):
        K = [[0.0] * nd for _ in range(nd)]; F = [0.0] * nd
        ke = [[12 * EI / dx ** 3, 6 * EI / dx ** 2, -12 * EI / dx ** 3, 6 * EI / dx ** 2],
              [6 * EI / dx ** 2, 4 * EI / dx, -6 * EI / dx ** 2, 2 * EI / dx],
              [-12 * EI / dx ** 3, -6 * EI / dx ** 2, 12 * EI / dx ** 3, -6 * EI / dx ** 2],
              [6 * EI / dx ** 2, 2 * EI / dx, -6 * EI / dx ** 2, 4 * EI / dx]]
        for e in range(n):
            dof = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
            for a in range(4):
                for b in range(4):
                    K[dof[a]][dof[b]] += ke[a][b]
        trib = [dx / 2 if i in (0, n) else dx for i in range(n + 1)]
        for i in range(n + 1):
            K[2 * i][2 * i] += kq * trib[i]; F[2 * i] += kq * delta * trib[i]
        fixed = {2 * i for i in sup | contact}
        free = [d for d in range(nd) if d not in fixed]
        xs = solve([[K[r][c] for c in free] for r in free], [F[r] for r in free])
        u = [0.0] * nd
        for d, v in zip(free, xs):
            u[d] = v
        neg = {i for i in range(n + 1) if u[2 * i] < -1e-9 and i not in sup}
        # 닿은 마디의 반력: 웹(날을 사이에 두고)은 판을 밀기만 한다(+w 쪽). 당기는 마디는 푼다
        pull = {i for i in contact if sum(K[2 * i][c] * u[c] for c in range(nd)) - F[2 * i] < -1e-9}
        if not (neg - contact) and not pull:
            break
        contact = (contact | neg) - pull
    w = [u[2 * i] for i in range(n + 1)]
    q = [kq * (delta - w[i]) for i in range(n + 1)]
    Ftot = sum(q[i] * trib[i] for i in range(n + 1))
    # 굽힘 모멘트(요소 끝)
    Mmax, xm = 0.0, 0.0
    for e in range(n):
        ue = [u[2 * e], u[2 * e + 1], u[2 * e + 2], u[2 * e + 3]]
        m1 = sum(ke[1][b] * ue[b] for b in range(4)); m2 = sum(ke[3][b] * ue[b] for b in range(4))
        for m_, x_ in ((abs(m1), e * dx), (abs(m2), (e + 1) * dx)):
            if m_ > Mmax:
                Mmax, xm = m_, x_
    i_mid = n // 2
    Rb = {i: sum(K[2 * i][c] * u[c] for c in range(nd)) - F[2 * i] for i in sup}
    at_bolt = abs(xm - 12.5) < dx / 2 or abs(xm - 97.5) < dx / 2
    Zs = (H_PL - 5.5) * T_PL ** 2 / 6.0 if at_bolt else H_PL * T_PL ** 2 / 6.0
    return {'w_mid_mm': round(w[i_mid], 3), 'w_end_mm': [round(w[0], 3), round(w[n], 3)], 'closed_mid_ratio': round((delta - w[i_mid]) / delta, 2),
            'F_blade_on_plate_N': round(Ftot, 1), 'F_rigid_plate_N': round(kq * delta * W_PL, 1), 'contact_nodes': len(contact),
            'M_max_Nmm': round(Mmax, 0), 'x_Mmax_mm': xm, 'Z_mm3': round(Zs, 2), 'sigma_MPa': round(Mmax / Zs, 1), 'SF_yield205': round(SY['SUS304'] / (Mmax / Zs), 2),
            'bolt_extra_pull_N_each': [round(-v, 1) for v in Rb.values()]}


R['clamp_plate'] = {'model': '보 20 x t3(I 45 mm^4), 볼트 2점 받침(x 12.5·97.5), 날 복원력 = Winkler 받침 kq(delta - w). 판 비틀림(선하중이 볼트 줄에서 10 위)은 넣지 않음',
                    'kq_N_per_mm2': round(kq, 3),
                    'gap_0.5': plate_bef(GAP_NOM, kq), 'gap_0.8': plate_bef(GAP_MAX, kq)}
# 가장 불리한 닫는 힘(누름 판이 강체·날 전체 폭이 닫힘) / 판 휨 반영(판 폭 110만)
F_UB = {g_: fu['RA_y'] * g_ * W_BL for g_ in (GAP_NOM, GAP_MAX)}      # 상한(V1)
F_GV = {g_: kq * g_ * W_BL for g_ in (GAP_NOM, GAP_MAX)}              # 기준(V2m), 강체 판·날 전체 폭
F_PL = {g_: R['clamp_plate']['gap_%.1f' % g_]['F_blade_on_plate_N'] for g_ in (GAP_NOM, GAP_MAX)}
M_UB = {g_: fu['RA_M'] * g_ * W_BL for g_ in (GAP_NOM, GAP_MAX)}     # 물림 끝 모멘트(받침이 날에 주는 값, +X 둘레)
M_GV = {g_: fg['RA_M'] * g_ * W_BL for g_ in (GAP_NOM, GAP_MAX)}
R['blade_force'] = {'F_close_upper_N(V1 상한, 강체 판·폭 213)': {str(k): round(v, 1) for k, v in F_UB.items()},
                    'F_close_governing_N(V2m, 강체 판·폭 213)': {str(k): round(v, 1) for k, v in F_GV.items()},
                    'M_clamp_governing_Nmm': {str(k): round(v, 0) for k, v in M_GV.items()},
                    'F_close_plate_flex_N(판 휨·폭 110)': {str(k): v for k, v in F_PL.items()},
                    'F_close_design_N(설계안 외팔보)': {'0.5': old['gap_0.5']['F_close_N'], '0.8': old['gap_0.8']['F_close_N']},
                    'M_clamp_upper_Nmm': {str(k): round(v, 0) for k, v in M_UB.items()}}


# ---------- 3. 잠금 미끄럼 ----------
T_LOCK, K_T, MU = 3.0, 0.2, 0.15               # catalog.md 임시 계수
Fv = T_LOCK * 1000.0 / (K_T * 5.0)             # 3,000 N/개
m_hung = 13.54 - 1.379 + 1.028 + 0.051 + 0.009  # 측정 1-3 13.54 kg - 옛 캐리지 + 새 캐리지(서명 1.028) + 누름 판 + 볼트 2
X_cases = {
    '운전 X(바퀴 축 방향 마찰 0.4 x 71.5)': (28.6, SF_OP),
    '오조작 X(0.5 x 134.9)': (67.5, SF_MIS),
    '손 오조작 X 100 N(D-79)': (100.0, SF_MIS),
    '완료 판정 ③: 스토퍼 받침 반력 204.3 N을 통째로 X로(운전)': (204.3, SF_OP),
    '보수: 받침 반력 오조작 553.1 N을 X로': (553.1, SF_MIS),
    '참고: 자중 x3 g를 X로(운반 충격, %.2f kg)' % m_hung: (round(m_hung * 3 * g, 1), SF_MIS),
}
slip = {'preload_N_each': Fv, 'mu': MU, 'K': K_T, 'm_hung_kg': round(m_hung, 2)}
for label, Fb in (('면 2(누름 판–날, 날–웹), 날 복원력 0.8 틈 상한 %.0f N 뺌' % F_UB[GAP_MAX], F_UB[GAP_MAX]),
                  ('면 2, 기준 틈 0.5 상한 %.0f N 뺌' % F_UB[GAP_NOM], F_UB[GAP_NOM])):
    hold = MU * (2 * 2 * Fv - Fb)              # 누름 판–날 N1 = 2Fv, 날–웹 N2 = 2Fv - F_blade
    slip[label] = {'hold_N': round(hold, 1), 'cases': {k: {'load_N': v[0], 'SF': round(hold / v[0], 2), 'need': v[1], 'ok': hold / v[0] >= v[1]} for k, v in X_cases.items()}}
hold1 = MU * (2 * Fv - F_UB[GAP_MAX])
slip['민감도: 면 1만(날–웹), 0.8 틈'] = {'hold_N': round(hold1, 1), 'cases': {k: {'load_N': v[0], 'SF': round(hold1 / v[0], 2), 'need': v[1], 'ok': hold1 / v[0] >= v[1]} for k, v in X_cases.items()}}
slip['min_torque_Nm_for_SF3_vs_204(면 2, 0.8 틈)'] = round((3 * 204.3 / MU + F_UB[GAP_MAX]) / 4 * K_T * 5.0 / 1000.0, 2)
R['lock_slip'] = slip
HOLD = slip['면 2(누름 판–날, 날–웹), 날 복원력 0.8 틈 상한 %.0f N 뺌' % F_UB[GAP_MAX]]['hold_N']


# ---------- 4. 볼트 ----------
# 잠금 볼트 CB5-16: 캐리지 웹 A5052 탭 물림 10.3, 외력 = 날 복원력 몫(상한) — 좌면은 누름 판 SUS304
R['lock_bolt_CB5-16'] = {
    'thread(A5052 탭)': calc(d=5, le=10.3, load=round(F_UB[GAP_MAX] / 2, 1), torque=T_LOCK, base='A5052', dw=8.5, dh=5.5),
    'seat(SUS304 누름 판)': calc(d=5, le=10.3, load=round(F_UB[GAP_MAX] / 2, 1), torque=T_LOCK, base='SUS304', dw=8.5, dh=5.5)['sf_tightening'],
    'shear_if_slip(나사 골 Ø4.13, 553.1/2 N)': round(0.6 * 1100 * 14.2 / (553.1 / 2), 1)}
# 날 고정 볼트 CB5-12 x4: 보 앞벽 t8 강 탭 물림 8, 4 N·m
T_BL = 4.0; Fv_bl = T_BL * 1000.0 / (K_T * 5.0)
bx = [-315.0, -255.0, -195.0, -135.0]; xc = sum(bx) / 4
arm_z = 562.0 - 468.0                           # 볼트 줄 Z 562 ↔ 잠금 줄 Z 468
sum_r2 = sum((x - xc) ** 2 for x in bx)
mount = {'preload_N_each': Fv_bl, 'friction_N_each(면 1, mu 0.15)': MU * Fv_bl, 'arm_z_mm': arm_z, 'cases': {}}
for label, (Fx, need) in X_cases.items():
    worst = 0.0
    for J in (0.0, 47.5, 95.0):                 # 잠금 중심 X = -182.5 - J
        xl = -182.5 - J
        Mi = Fx * arm_z                         # 면내(Y 둘레) 모멘트: X 힘 x Z 팔. 힘 방향이 X라 X 자리는 모멘트에 안 들어감
        for x in bx:
            fz = Mi * (x - xc) / sum_r2; fx = Fx / 4
            worst = max(worst, math.hypot(fx, fz))
    mount['cases'][label] = {'Fx_N': Fx, 'bolt_resultant_N': round(worst, 1), 'direct_only_N': round(Fx / 4, 1),
                             'SF_slip': round(MU * Fv_bl / worst, 2), 'need': need, 'ok': MU * Fv_bl / worst >= need}
# 볼트 인장: 날을 닫는 힘의 반력(뼈대 고정단) — 플랜지 지렛대(볼트 줄 ↔ 플랜지 윗끝 15)
f8 = frame(GAP_MAX, E=E_pl)
P_ = blade_nodes(); i_fix = next(i for i, p in enumerate(P_) if p[2] == 'flange' and abs(p[1] - 557.75) < 1e-9)
# 닫는 힘의 Y 반력은 플랜지를 보 면에 누르는 쪽(볼트 인장 아님). 고정단 모멘트만 지렛대(볼트 줄 ↔ 플랜지 끝 15)로 볼트를 당긴다
M_fl = max(fg['M']['flange'], fu['M']['flange']) * GAP_MAX * W_BL
mount['M_flange_fixed_Nmm(0.8 틈, V1·V2m 큰 쪽)'] = round(M_fl, 0)
mount['pull_from_blade_N_each(0.8 틈 상한)'] = round(M_fl / 15.0 / 4, 1)
mount['thread(강 SS400 탭 t8)'] = calc(d=5, le=8.0, load=mount['pull_from_blade_N_each(0.8 틈 상한)'], torque=T_BL, base='SS400', dw=8.5, dh=5.5)
mount['slip_SF_553_at_3Nm_whatif(검도 D3 제안 값)'] = round(MU * 3000.0 / mount['cases']['보수: 받침 반력 오조작 553.1 N을 X로']['bolt_resultant_N'], 2)
mount['thread_3Nm_whatif'] = calc(d=5, le=8.0, load=mount['pull_from_blade_N_each(0.8 틈 상한)'], torque=3.0, base='SS400', dw=8.5, dh=5.5)['sf_tightening']
mount['seat(SUS304 날 플랜지)'] = calc(d=5, le=8.0, load=1.0, torque=T_BL, base='SUS304', dw=8.5, dh=5.5)['sf_tightening']['조임 좌면']
R['mount_bolt_CB5-12'] = mount

# 날 면내(X 힘이 물린 자리에서 플랜지까지)
slot_low, slot_up = 465.25 - 457.0, 478.0 - 470.75      # 긴 구멍 아래 띠 8.25, 위(누름 판 범위 안) 7.25 — STEP z 좌표
Fx_m = 553.1
R['blade_inplane'] = {
    'slot_strip_heights_mm(STEP)': [slot_low, slot_up],
    'lower_strip_tension_MPa(553.1 N의 절반이 아래 띠 한쪽으로)': round(Fx_m / 2 / (slot_low * t_bl), 1),
    'leg_shear_MPa(553.1 / 213 x 2)': round(Fx_m / (W_BL * t_bl), 2),
    'leg_inplane_bend_MPa(팔 66, 폭 213)': round(Fx_m * 66.0 / (t_bl * W_BL ** 2 / 6.0), 2),
    'SF_min': round(SY['SUS304'] / (Fx_m / 2 / (slot_low * t_bl)), 1)}


# ---------- 5. 레일 블록 (잠금이 X를 받음, 날 복원력 더함) ----------
m_bundle, cg_bundle = 13.54 - 1.379, (-215.6, 33.6, 156.6)   # 캐리지 뺀 묶음(RX-08 스토퍼 포함). CG는 RX-06 값 그대로(Y가 레일에서 가장 먼 쪽 = 불리)
m_car, cg_car = 1.028, (-182.5, 95.5, 346.5)                 # 서명 질량, 웹(115x12x220)+발(115x62x12) 형상 중심
m_lock, cg_lock = 0.060, (-182.5, 91.0, 468.0)               # 누름 판 + 볼트 2
P0 = (-182.5, 112.0, 353.0); dX, dZ = 77.0 / 2, 174.0 / 2
blocks = [(sx * dX, sz * dZ) for sx in (-1, 1) for sz in (-1, 1)]
wheel = (-100.0, 0.0, 10.0)
lock_pt = (-182.5, 93.5, 468.0)                              # 날 중립면 Y 93.5, 볼트 줄 Z 468
clamp_edge = (-182.5, 93.5, Z_CLAMP_TOP)
N_op, N_mis = 71.5, 134.9                                    # 바퀴 누름: 0.2 MPa(IR1000 상한)·0.5 MPa 전부, 매트 두께 16 — 측정 6절(mech_M02R_fea.md). RX-06은 옛 식 56.4·121.5
C0_prov, C0_cat = 2000.0, 6000.0                             # 보수 임시 / catalog.md '이전 표 값'(미확인)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def blockloads(forces, couples=()):
    Fx = sum(f[0] for _, f in forces)
    forces = forces + [(lock_pt, (-Fx, 0.0, 0.0))]           # X는 잠금이 받는다
    F = [sum(f[i] for _, f in forces) for i in range(3)]
    M = [0.0, 0.0, 0.0]
    for p, f in forces:
        r = tuple((p[i] - P0[i]) / 1000.0 for i in range(3)); c = cross(r, f)
        M = [M[i] + c[i] for i in range(3)]
    for c in couples:
        M = [M[i] + c[i] for i in range(3)]
    sx2, sz2 = 4 * (dX / 1000) ** 2, 4 * (dZ / 1000) ** 2
    out = []
    for bx_, bz_ in blocks:
        bxm, bzm = bx_ / 1000, bz_ / 1000
        Fy = -(F[1] / 4) + (M[0] * bzm / sz2) - (M[2] * bxm / sx2)
        Fz = -(F[2] / 4) + (M[1] * bxm / sx2)
        out.append({'blk': (round(P0[0] + bx_, 1), round(P0[2] + bz_, 1)), 'Fy': round(Fy, 1), 'Fz': round(Fz, 1), 'P': round(abs(Fy) + abs(Fz), 1)})
    return {'F_N': [round(v, 1) for v in F], 'M_Nm': [round(v, 2) for v in M], 'blocks': out, 'P_max_N': max(b['P'] for b in out)}


def grav(k):
    return [(cg_bundle, (0, 0, -k * m_bundle * g)), (cg_car, (0, 0, -k * m_car * g)), (cg_lock, (0, 0, -k * m_lock * g))]


def blade_on_car(Fc, Mc):
    """날이 캐리지에 주는 힘: 받침 반력의 반대. 힘 -Y(레일에서 떼는 쪽) @ 물림 끝, 모멘트 -RA_M(+X 둘레)."""
    return [(clamp_edge, (0.0, -Fc, 0.0))], [(-Mc / 1000.0, 0.0, 0.0)]


cases = {
    'A_들기_3g': grav(3),
    'B_운전_누름_3g(N 덜어 줌 무시)': grav(3) + [(wheel, (0.4 * N_op, 18.0, 0))],
    'C_운전_누름_3g(N 반영)': grav(3) + [(wheel, (0.4 * N_op, 18.0, N_op))],
    'D_오조작_공급압_전부_3g(N 무시)': grav(3) + [(wheel, (0.5 * N_mis, 0.5 * N_mis, 0))],
}
rail = {}
blade_sets = {'날 힘 없음(잠금 풂)': (0.0, 0.0),
              '설계안 값(외팔보 0.8: %.0f N)' % old['gap_0.8']['F_close_N']: (old['gap_0.8']['F_close_N'], 0.0),
              '판 휨 반영 0.5(%.0f N)' % F_PL[GAP_NOM]: (F_PL[GAP_NOM], fg['RA_M'] * GAP_NOM * W_PL * R['clamp_plate']['gap_0.5']['F_blade_on_plate_N'] / R['clamp_plate']['gap_0.5']['F_rigid_plate_N']),
              '기준 0.5(V2m·폭 213: %.0f N)' % F_GV[GAP_NOM]: (F_GV[GAP_NOM], M_GV[GAP_NOM]),
              '기준 0.8(V2m·폭 213: %.0f N)' % F_GV[GAP_MAX]: (F_GV[GAP_MAX], M_GV[GAP_MAX]),
              '상한 0.5(V1·폭 213: %.0f N)' % F_UB[GAP_NOM]: (F_UB[GAP_NOM], M_UB[GAP_NOM]),
              '상한 0.8(V1·폭 213: %.0f N)' % F_UB[GAP_MAX]: (F_UB[GAP_MAX], M_UB[GAP_MAX])}
for bn, (Fc, Mc) in blade_sets.items():
    rail[bn] = {}
    for k, fs in cases.items():
        ef, ec = blade_on_car(Fc, Mc) if Fc else ([], [])
        r = blockloads(fs + ef, ec)
        need = SF_MIS if k.startswith('D') else SF_OP
        rail[bn][k] = {'P_max_N': r['P_max_N'], 'SF_C0_2kN(보수 임시)': round(C0_prov / r['P_max_N'], 2), 'SF_C0_6kN(카탈로그 표 미확인)': round(C0_cat / r['P_max_N'], 2),
                       'need': need, 'blocks': r['blocks'], 'F_N': r['F_N'], 'M_Nm': r['M_Nm']}
R['rail_blocks'] = rail
R['rail_note'] = {'N_op_N(0.2 MPa)': round(N_op, 1), 'N_mis_N(0.5 MPa)': round(N_mis, 1), 'm_bundle_kg': round(m_bundle, 3), 'm_car_kg': m_car,
                  'RX-06(v2.11.0) P_max_N': {'A': 239.9, 'B': 349.2, 'C': 347.2, 'D': 549.9}, 'sign': 'Fy + = 블록이 캐리지를 레일 쪽으로 당김(블록은 들리는 쪽 하중)'}


# ---------- 6. 캐리지 ----------
Zroot = 115 * 12 ** 2 / 6.0                                  # 웹·발 뿌리 115 x 12 (STEP y 95~107, x -240~-125)
car = {}
for k, fs in cases.items():
    pr = (0, 95.0, 256.0); Mx = 0.0
    for p, f in fs:
        if p in (cg_bundle, wheel):
            r = ((p[0] - pr[0]) / 1000, (p[1] - pr[1]) / 1000, (p[2] - pr[2]) / 1000); Mx += cross(r, f)[0]
    s = abs(Mx) * 1e3 / Zroot; need = SF_MIS if k.startswith('D') else SF_OP
    car[k] = {'Mx_root_Nm': round(abs(Mx), 2), 'sigma_MPa': round(s, 2), 'SF': round(SY['A5052'] / s, 1), 'need': need}
# 웹 윗부분(위 블록 윗끝 Z 453.5 위): 날 복원력 + 물림 모멘트, 탭 구멍 Ø4.2 x2 뺀 단면
Znet = (115 - 2 * 4.2) * 12 ** 2 / 6.0
Mtop = F_UB[GAP_MAX] * (Z_CLAMP_TOP - 453.5) + abs(M_UB[GAP_MAX])
car['웹 윗부분(Z 453.5~482) 날 힘 상한 0.8'] = {'M_Nmm': round(Mtop, 0), 'Z_net_mm3': round(Znet, 1), 'sigma_MPa': round(Mtop / Znet, 2), 'SF': round(SY['A5052'] / (Mtop / Znet), 1), 'need': SF_OP}
car['탭 구멍 가장자리 살(Z 468 ↔ 윗끝 482, Ø4.2)'] = {'edge_mm': 482.0 - 468.0 - 2.1, 'need_M03(mm)': 2.5}
car['과사양 메모(M-09)'] = '뿌리 SF %.1f(오조작) — 필요 2의 3배 이상. 두께 12 -> 8이면 응력 x2.25(SF %.1f). 레일 블록 자리·탭 물림 10.3이 두께를 정하므로 디테일링에서 판단' % (
    car['D_오조작_공급압_전부_3g(N 무시)']['SF'], car['D_오조작_공급압_전부_3g(N 무시)']['SF'] / 2.25)
R['carriage'] = car
MOD = json.load(open(ROOT + '/tools/out/mech_RX-06/model/handcalc_rx06.json', encoding='utf-8'))
k_up = max(v['Mx_root_Nm'] for k, v in car.items() if 'Mx_root_Nm' in v) / MOD['rail_screw']['carriage']['M_root_Nm']
R['foot_bolts_M5'] = calc(d=5, le=4, load=round(MOD['foot_bolts']['F_max_N'] * k_up, 1), base='SUS304')
R['foot_bolts_M5']['scale_from_model'] = round(k_up, 2)


# ---------- 7. 판정 모음 ----------
gv = bl[GOV]
S = []
def add(item, sf, need, kind='', note=''):
    S.append({'item': item, 'SF': sf, 'need': need, 'ok': sf >= need, 'kind_if_ng': kind, 'note': note})
sl = slip['면 2(누름 판–날, 날–웹), 날 복원력 0.8 틈 상한 %.0f N 뺌' % F_UB[GAP_MAX]]['cases']
for k, v in sl.items():
    add('잠금 미끄럼 ' + k, v['SF'], v['need'])
add('잠금 볼트 조임 볼트 응력', R['lock_bolt_CB5-16']['thread(A5052 탭)']['sf_tightening']['조임 볼트 응력'], 1.0)
add('잠금 볼트 조임 암나사 전단(A5052)', R['lock_bolt_CB5-16']['thread(A5052 탭)']['sf_tightening']['조임 암나사 전단'], 1.0)
add('잠금 볼트 좌면(SUS304 누름 판)', R['lock_bolt_CB5-16']['seat(SUS304 누름 판)']['조임 좌면'], 1.0)
add('잠금 볼트 분리(예압/날 복원력 몫)', R['lock_bolt_CB5-16']['thread(A5052 탭)']['sf_operating']['분리(예압/외력)'], SF_OP)
for k, v in mount['cases'].items():
    add('날 고정 볼트 미끄럼(면내 모멘트 포함) ' + k, v['SF_slip'], v['need'])
add('날 고정 볼트 조임 암나사 전단(강 t8, 4 N·m)', mount['thread(강 SS400 탭 t8)']['sf_tightening']['조임 암나사 전단'], 1.0)
add('날 굽힘 기준 V2m(조임 강제 변위, 틈 0.5)', gv['gap_0.5']['SF_yield205'], SF_OP, '디테일', '영구 변형 한계 1.2 이상. 상한 V1 SF %.2f, 설계안 모델 3.98' % bl[UPP]['gap_0.5']['SF_yield205'])
add('날 굽힘 기준 V2m(틈 0.8 공차 끝)', gv['gap_0.8']['SF_yield205'], SF_OP, '디테일', '영구 변형 한계 1.2 이상. 상한 V1 SF %.2f(겉면 항복 근처, 변위 제어), 설계안 모델 2.49' % bl[UPP]['gap_0.8']['SF_yield205'])
add('날 굽힘 상한 V1(틈 0.5) — 참고', bl[UPP]['gap_0.5']['SF_yield205'], 1.2, '동작', '영구 변형 한계와 비교')
add('누름 판 굽힘(판 휨 반영, 틈 0.5)', R['clamp_plate']['gap_0.5']['SF_yield205'], SF_OP, '디테일')
add('누름 판 굽힘(판 휨 반영, 틈 0.8)', R['clamp_plate']['gap_0.8']['SF_yield205'], SF_OP, '디테일')
add('날 면내(553.1 N)', R['blade_inplane']['SF_min'], SF_MIS)
for bn in rail:
    if bn.startswith('상한') or bn.startswith('설계안') or bn.startswith('판 휨'):
        continue                                 # 상한·비교 값은 rail_blocks에만 남김
    for k, v in rail[bn].items():
        if k.startswith('B') or k.startswith('D'):
            add('블록 %s / %s (C0 2 kN 보수)' % (bn, k[:1]), v['SF_C0_2kN(보수 임시)'], v['need'], '디테일', 'C0 6 kN이면 SF %.2f' % v['SF_C0_6kN(카탈로그 표 미확인)'])
for k, v in car.items():
    if isinstance(v, dict) and 'SF' in v:
        add('캐리지 ' + k, v['SF'], v['need'])
add('발 볼트 M5 암나사 전단', R['foot_bolts_M5']['sf_operating']['암나사 전단'], SF_OP)
R['summary'] = S
json.dump(R, open(ROOT + '/fea/results/mech_RX-06R_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 화면 요약(E-20)
print('날 뼈대 kq %.3f N/mm2, 기준 모델 sigma/mm %.1f MPa, 자리 %s, 물림 끝 %.1f' % (kq, fg['sigma_max'], {k: round(v, 1) for k, v in fg['sigma'].items()}, fg['sigma_clamp_edge']))
for n in bl:
    if n.startswith('V'):
        print(' ', n[:34], '0.5:', bl[n]['gap_0.5'], '0.8:', bl[n]['gap_0.8']['sigma_MPa'], bl[n]['gap_0.8']['SF_yield205'], 'uy547', bl[n]['uy_flange_547_per_mm_gap'], 'Rc', bl[n]['R_beam_contact_per_mm'])
print('Z 묶는 힘/닫는 힘(V1)', round(Z_RATIO_V1, 2), 'RA_M', round(_v1['RA_M'], 1), 'whatif', bl['fix_whatif(같은 뼈대, 두께·틈만 바꿈)'])
print('옛 모델', old)
print('누름 판', {k: (v['w_mid_mm'], v['F_blade_on_plate_N'], v['F_rigid_plate_N'], v['sigma_MPa'], v['SF_yield205'], v['x_Mmax_mm']) for k, v in R['clamp_plate'].items() if k.startswith('gap')})
ng = [s for s in S if not s['ok']]
print('판정 %d개, 미달 %d개' % (len(S), len(ng)))
for s in ng:
    print('  NG', s['item'], s['SF'], '/', s['need'], s['kind_if_ng'], s['note'])
print('잠금 유지력', HOLD, '| 블록 P', {bn[:12]: {k[:1]: v['P_max_N'] for k, v in rail[bn].items()} for bn in rail})
