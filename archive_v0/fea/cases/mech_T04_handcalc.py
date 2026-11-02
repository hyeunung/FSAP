# -*- coding: utf-8 -*-
"""T04 가장자리 센서 배치 — 노루발 P_T02_FOOT(주머니·슬릿·통로 추가) 강도·처짐 손계산 (해석부, 2026-10-31, 대상 v0.3.2).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음), numpy도 없음.
그래서 표준 라이브러리만으로 '단면 수치 적분 + 보 이론 + 프란틀 응력함수(유한차분) 비틀림'을 한다.

입력 형상: tools/out/mech_T04/stepout/P_T02_FOOT.step(세계 좌표, 대기 = 내림 + 10).
  - 바깥 형상·컷 평면은 STEP의 PLANE·CYLINDRICAL_SURFACE에서 읽어 검산(chk)한다.
  - 주머니·슬릿 4각형 꼭짓점은 STEP의 VERTEX_POINT(Z 23.05 / Z 21.05 / Z 31.05)에서 읽는다.
  - 화이버 통로는 STEP에서 B-spline 면 2장으로 나와 축을 바로 못 읽는다. 끝 캡 PLANE(법선 = 축 방향)과
    모델 보고서 2절 값(r 1.3, 시작 (−0.0652,−6.7363,27.05), 길이 16.9041)을 쓰고, 캡 법선과 축 방향이 같은지 검산한다.
  - 옛 형상(T02, v0.3.0~0.3.1)도 같은 스크립트로 풀어(컷 없음) 차이를 남긴다(E-18 '옛 모델도 같은 형상으로').

해석 모델(fea/models.json P_T02_FOOT, T02와 같음): 자루 윗면(내림 Z 45)에서 헤드 노루발대 Ø10에 물린 외팔.
바닥 판은 자루 앞면(Y −10)에서 나온 외팔. 하중: 누름 50 N(위로, 바닥 밑면 Y −4.5), 끌림 20 N(+X, 바닥 밑면),
오조작 417.5 N(위 노즈 가운데 Y 10, 내림 Z 8.775 → 대기 Z 18.775, X 또는 Y 방향), 자중 ×3 g.

단위 mm, N, MPa.  실행: python -B fea/cases/mech_T04_handcalc.py
결과: fea/results/mech_T04_handcalc.json, 로그 fea/results/mech_T04_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
STEP_NEW = os.path.join(ROOT, 'tools', 'out', 'mech_T04', 'stepout', 'P_T02_FOOT.step')
STEP_OLD = os.path.join(ROOT, 'tools', 'out', 'mech_T02', 'stepout', 'P_T02_FOOT.step')
T02_RES = os.path.join(ROOT, 'fea', 'results', 'mech_T02_handcalc.json')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T04_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T04_handcalc_log.txt')
g = 9.81
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


# ------------------------------------------------------------------ 재료·기준 (T02와 같음)
E_R, NU_R, ALLOW_R = 10000.0, 0.30, 65.0     # Rigid 10K(공개 데이터시트 기억값, 확인 못 함 — T02와 같음)
G_R = E_R / (2 * (1 + NU_R))
F_PRESS, F_DRAG = 50.0, 20.0                 # D-10 자리값
F_MIS = 835.0 * 0.5                          # D-05 × D-04 = 417.5 N
NG = 3.0
MASS_FOOT = 25.54                            # g, v0.3.2 모델 질량(모델 보고서 3-1)
SF_REQ, SF_REQ_MIS, SF_BREAK = 3.0, 2.0, 1.2  # M-09 기본값(요구서 6-1 비어 있음), 해석부 지시 1.2
KT_CORNER = 2.5                              # 날카로운 안쪽 모서리(T02와 같은 보수 자리값)
KT_HOLE = 3.0                                # 둥근 구멍 옆(무한판 구멍 Kt 3)
GAP_NEEDLE = 0.7                             # 바늘 r0.6 ↔ 노루발 구멍 r1.3(내림), T02 5절


# ================================================================== STEP 읽기
def step_entities(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ent = {}
    for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
        ent[int(m.group(1))] = m.group(2).replace('\n', '')
    return ent


def nums(s):
    return tuple(float(x) for x in re.search(r"\(([-\d.Ee+,\s]+)\)\)?\s*$", s).group(1).split(','))


def read_step(path):
    ent = step_entities(path)

    def pt(i):
        return tuple(float(x) for x in re.search(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", ent[i]).group(1).split(','))

    def dirn(i):
        return tuple(float(x) for x in re.search(r"DIRECTION\('[^']*',\(([^)]*)\)\)", ent[i]).group(1).split(','))

    def ax(i):
        a = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ent[i])
        return pt(int(a.group(1))), dirn(int(a.group(2)))
    verts, planes, cyls, nbs = [], [], [], 0
    for i, s in ent.items():
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
        m = re.match(r"ADVANCED_FACE\('[^']*',\([^)]*\),#(\d+)", s)
        if m:
            surf = ent[int(m.group(1))]
            pm = re.match(r"PLANE\('[^']*',#(\d+)\)", surf)
            cm = re.match(r"CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)", surf)
            if pm:
                loc, n = ax(int(pm.group(1)))
                planes.append(dict(loc=loc, normal=n))
            elif cm:
                loc, n = ax(int(cm.group(1)))
                cyls.append(dict(r=float(cm.group(2)), loc=loc, dir=n))
            elif 'B_SPLINE_SURFACE' in surf:
                nbs += 1
    return dict(verts=verts, planes=planes, cyls=cyls, n_bspline_faces=nbs)


checks = []


def chk(what, got, want, tol=0.02):
    ok = abs(got - want) <= tol
    checks.append(dict(what=what, step=round(got, 4), used=want, ok=ok))
    return got


S = read_step(STEP_NEW)
xs = [v[0] for v in S['verts']]; ys = [v[1] for v in S['verts']]; zs = [v[2] for v in S['verts']]
chk('bbox X min', min(xs), -9.0); chk('bbox X max', max(xs), 9.0, 0.01)
chk('bbox Y min', min(ys), -26.0); chk('bbox Y max', max(ys), 18.5)
chk('bbox Z min', min(zs), 16.5); chk('bbox Z max', max(zs), 55.0)
zpl = sorted(set(round(p['loc'][2], 3) for p in S['planes'] if abs(abs(p['normal'][2]) - 1) < 1e-6))
log('STEP Z 평면:', zpl, ' 면 수: 평면 %d, 원통 %d, B-spline %d' % (len(S['planes']), len(S['cyls']), S['n_bspline_faces']))
for zz in (16.5, 21.05, 23.05, 31.05, 55.0):
    chk('Z 평면 %.2f 있음' % zz, min(abs(z - zz) for z in zpl), 0.0, 0.005)
nose = [c for c in S['cyls'] if abs(c['r'] - 8.5) < 0.01][0]
hole = [c for c in S['cyls'] if abs(c['r'] - 1.3) < 0.01 and abs(c['dir'][2]) > 0.99][0]
chk('위 노즈 축 X', nose['loc'][0], 0.0); chk('위 노즈 축 Y', nose['loc'][1], 10.0)
chk('바늘 구멍 축 X', hole['loc'][0], 0.0); chk('바늘 구멍 축 Y', hole['loc'][1], 0.0)


def quad_from_verts(z0, near):
    """Z z0 높이의 VERTEX_POINT 중 near(지시 좌표) 각 점에 가장 가까운 STEP 점."""
    cand = [v for v in S['verts'] if abs(v[2] - z0) < 1e-3]
    out = []
    for p in near:
        q = min(cand, key=lambda v: (v[0] - p[0]) ** 2 + (v[1] - p[1]) ** 2)
        chk('꼭짓점 Z%.2f (%.3f,%.3f)' % (z0, p[0], p[1]), math.hypot(q[0] - p[0], q[1] - p[1]), 0.0, 0.01)
        out.append((q[0], q[1]))
    return out


POCKET = quad_from_verts(23.05, [(1.5139, -6.2493), (-5.3260, 3.6105), (-7.9141, 1.8149), (-1.0742, -8.0449)])
SLIT = quad_from_verts(21.05, [(0.6962, -6.2110), (-5.5736, 2.8271), (-6.3952, 2.2570), (-0.1254, -6.7811)])
# 통로: 끝 캡 평면(법선이 XY 대각)
cap = [p for p in S['planes'] if abs(p['normal'][2]) < 1e-6 and abs(abs(p['normal'][0]) - 0.57) < 0.01]
CH_DIR = (0.56999, -0.821652, 0.0); CH_O = (-0.0652, -6.7363, 27.05); CH_R = 1.3; CH_L = 16.9041
chk('통로 끝 캡 법선 X(축 방향)', cap[0]['normal'][0], CH_DIR[0], 0.001)
chk('통로 끝 캡 위치(축 거리 = 길이)', sum((cap[0]['loc'][k] - CH_O[k]) * CH_DIR[k] for k in range(3)), CH_L, 0.01)
fails = [c for c in checks if not c['ok']]
log('STEP 검산 %d개, 불일치 %d' % (len(checks), len(fails)))
for c in fails:
    log('  불일치:', c)


# ================================================================== 형상 판정(대기 세계 좌표)
def in_poly(x, y, P):
    ins = False
    n = len(P)
    for i in range(n):
        x1, y1 = P[i]; x2, y2 = P[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def solid(x, y, z, cuts=True):
    body = ((-9 <= x <= 9 and -10 <= y <= 18.5 and 21.05 <= z <= 31.05) or
            (-9 <= x <= 9 and -26 <= y <= -10 and 21.05 <= z <= 55.0) or
            (x * x + (y - 10) ** 2 <= 72.25 and 16.5 <= z <= 21.05))
    if not body:
        return False
    if x * x + y * y < 1.69 and z >= 16.5:          # 바늘 구멍 r1.3(옛 형상에도 있음)
        return False
    if not cuts:
        return True
    if 23.05 <= z <= 31.05 and in_poly(x, y, POCKET):
        return False
    if 21.05 <= z <= 23.05 and in_poly(x, y, SLIT):
        return False
    d = (x - CH_O[0], y - CH_O[1], z - CH_O[2])
    t = d[0] * CH_DIR[0] + d[1] * CH_DIR[1]
    if 0 <= t <= CH_L and (d[0] - t * CH_DIR[0]) ** 2 + (d[1] - t * CH_DIR[1]) ** 2 + d[2] ** 2 < CH_R ** 2:
        return False
    return True


# ================================================================== Y 단면(바닥 판) 수치 적분
H = 0.1        # 굽힘 격자
HT = 0.2       # 비틀림 격자


def section_y(y, cuts, mask=None):
    cells = []
    nx, nz = int(round(18 / H)), int(round((31.05 - 16.5) / H))
    for i in range(nx):
        x = -9 + (i + 0.5) * H
        for k in range(nz):
            z = 16.5 + (k + 0.5) * H
            if solid(x, y, z, cuts):
                cells.append((x, z, mask(x, y, z) if mask else 0))
    A = len(cells) * H * H
    xc = sum(c[0] for c in cells) / len(cells); zc = sum(c[1] for c in cells) / len(cells)
    Iuu = sum((c[0] - xc) ** 2 for c in cells) * H * H
    Iww = sum((c[1] - zc) ** 2 for c in cells) * H * H
    Iuw = sum((c[0] - xc) * (c[1] - zc) for c in cells) * H * H
    return dict(cells=cells, A=A, xc=xc, zc=zc, Iuu=Iuu, Iww=Iww, Iuw=Iuw)


def torsion_y(y, cuts, iters=4000, tol=1e-7, lump=True):
    """프란틀 응력함수 ∇²φ = −2 (Gθ = 1). 바깥 경계 φ = 0(셀 면, 거울 유령점).
    단면 안에 갇힌 구멍(화이버 통로가 단면을 꿰는 자리)은 lump=True면 한 마디 φ_h로 묶어 브레트 조건
    Σ(φ_이웃 − φ_h) + 2h²·N_구멍 = 0 을 푼다(다중연결 단면의 바른 조건). lump=False면 φ_h = 0(보수, 옛 1차 계산)."""
    nx, nz = int(round(18 / HT)), int(round((31.05 - 16.5) / HT))
    inside = [[solid(-9 + (i + 0.5) * HT, y, 16.5 + (k + 0.5) * HT, cuts) for k in range(nz)] for i in range(nx)]
    # 바깥과 이어진 빈 셀(격자 테두리에서 빈 셀로 퍼짐) → 나머지 빈 셀은 갇힌 구멍
    ext = [[False] * nz for _ in range(nx)]
    st = [(i, k) for i in range(nx) for k in (0, nz - 1) if not inside[i][k]] +          [(i, k) for k in range(nz) for i in (0, nx - 1) if not inside[i][k]]
    for (i, k) in st:
        ext[i][k] = True
    while st:
        i, k = st.pop()
        for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ii, kk = i + di, k + dk
            if 0 <= ii < nx and 0 <= kk < nz and not inside[ii][kk] and not ext[ii][kk]:
                ext[ii][kk] = True; st.append((ii, kk))
    hole = [[(not inside[i][k]) and (not ext[i][k]) for k in range(nz)] for i in range(nx)]
    n_hole = sum(sum(r) for r in hole)
    phi = [[0.0] * nz for _ in range(nx)]
    ph = 0.0
    w = 1.9
    h2 = HT * HT
    for it in range(iters):
        dmax = 0.0
        for i in range(nx):
            row = inside[i]
            for k in range(nz):
                if not row[k]:
                    continue
                s = 0.0; den = 4.0
                for ii, kk in ((i - 1, k), (i + 1, k), (i, k - 1), (i, k + 1)):
                    if 0 <= ii < nx and 0 <= kk < nz and inside[ii][kk]:
                        s += phi[ii][kk]
                    elif 0 <= ii < nx and 0 <= kk < nz and hole[ii][kk] and lump:
                        s += ph
                    elif 0 <= ii < nx and 0 <= kk < nz and hole[ii][kk]:
                        den += 1.0          # φ_h = 0, 셀 면에서
                    else:
                        den += 1.0          # 바깥: 거울 유령점
                new = (s + 2 * h2) / den
                d = new - phi[i][k]
                phi[i][k] += w * d
                if abs(d) > dmax:
                    dmax = abs(d)
        if lump and n_hole:
            sn, nf = 0.0, 0
            for i in range(nx):
                for k in range(nz):
                    if hole[i][k]:
                        for ii, kk in ((i - 1, k), (i + 1, k), (i, k - 1), (i, k + 1)):
                            if inside[ii][kk]:
                                sn += phi[ii][kk]; nf += 1
            newh = (sn + 2 * h2 * n_hole) / nf
            d = newh - ph; ph += d
            dmax = max(dmax, abs(d))
        if dmax < tol:
            break
    J = 2 * (sum(sum(r) for r in phi) + (ph * n_hole if lump else 0.0)) * h2
    gmax, gpos = 0.0, None
    for i in range(nx):
        for k in range(nz):
            if not inside[i][k]:
                continue
            for ii, kk in ((i - 1, k), (i + 1, k), (i, k - 1), (i, k + 1)):
                if 0 <= ii < nx and 0 <= kk < nz and inside[ii][kk]:
                    gr = abs(phi[i][k] - phi[ii][kk]) / HT
                elif 0 <= ii < nx and 0 <= kk < nz and hole[ii][kk] and lump:
                    gr = abs(phi[i][k] - ph) / HT
                else:
                    gr = phi[i][k] / (HT / 2)
                if gr > gmax:
                    gmax, gpos = gr, (round(-9 + (i + 0.5) * HT, 2), round(16.5 + (k + 0.5) * HT, 2))
    return dict(J=J, gmax=gmax, gpos=gpos, iters=it + 1, n_hole=n_hole)


# 비틀림 검증: 18 × 10 꽉 찬 직사각(바늘 구멍 없는 Y −5, 옛 형상)과 Roark β
def beta_rect(a, b):
    a, b = max(a, b), min(a, b); r = a / b
    tab = [(1.0, .141), (1.2, .166), (1.5, .196), (2.0, .229), (2.5, .249), (3.0, .263), (4.0, .281), (5.0, .291), (10.0, .312), (1e9, .333)]
    for (r0, b0), (r1, b1) in zip(tab, tab[1:]):
        if r <= r1:
            return (b0 + (b1 - b0) * (r - r0) / (r1 - r0)) * a * b ** 3


def alpha_rect(a, b):
    a, b = max(a, b), min(a, b); r = a / b
    tab = [(1.0, .208), (1.5, .231), (2.0, .246), (2.5, .258), (3.0, .267), (4.0, .282), (5.0, .291), (10.0, .312), (1e9, .333)]
    for (r0, a0), (r1, a1) in zip(tab, tab[1:]):
        if r <= r1:
            return a0 + (a1 - a0) * (r - r0) / (r1 - r0)


tv = torsion_y(-5.0, False)
J_roark = beta_rect(18, 10); tau_roark = 1.0 / (alpha_rect(18, 10) * 18 * 10 ** 2)   # T = 1
tau_fd = tv['gmax'] / tv['J']
log('비틀림 검증(18×10 꽉 찬): J FD %.1f / Roark %.1f (%.1f %%), τ/T FD %.5f / Roark %.5f (%.1f %%), 반복 %d'
    % (tv['J'], J_roark, 100 * (tv['J'] / J_roark - 1), tau_fd, tau_roark, 100 * (tau_fd / tau_roark - 1), tv['iters']))
TORSION_CHECK = dict(J_fd=round(tv['J'], 1), J_roark=round(J_roark, 1), tau_per_T_fd=round(tau_fd, 6), tau_per_T_roark=round(tau_roark, 6))


# ================================================================== 하중 경우 (대기 세계 좌표의 작용점)
W_SELF = MASS_FOOT / 1000 * g * NG
CASES = {
    # 이름: [(작용점, 힘 벡터)], 필요 SF
    'op':   ([((0.0, -4.5, 21.05), (0.0, 0.0, F_PRESS)), ((0.0, -4.5, 21.05), (F_DRAG, 0.0, 0.0))], SF_REQ),
    'misX': ([((0.0, 10.0, 18.775), (F_MIS, 0.0, 0.0))], SF_REQ_MIS),
    'misY': ([((0.0, 10.0, 18.775), (0.0, -F_MIS, 0.0))], SF_REQ_MIS),   # 매트가 노즈를 −Y(자루 쪽)로 미는 것 = 축 압축 + 굽힘
    'misY+': ([((0.0, 10.0, 18.775), (0.0, F_MIS, 0.0))], SF_REQ_MIS),
}


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def stress_y(sec, tor, y, loads):
    """Y 단면 응력: 앞쪽(y' > y) 하중의 합력 → 축력 N(Fy), 굽힘 Mx·Mz(비대칭 굽힘식), 비틀림 My, 직접 전단."""
    C = (sec['xc'], y, sec['zc'])
    F = [0.0, 0.0, 0.0]; M = [0.0, 0.0, 0.0]
    for P, Fv in loads:
        if P[1] <= y:
            continue
        r = (P[0] - C[0], P[1] - C[1], P[2] - C[2])
        m = cross(r, Fv)
        for k in range(3):
            F[k] += Fv[k]; M[k] += m[k]
    # 굽힘: σ = N/A + a u + b w,  Mx = −(a Iuw + b Iww), Mz = a Iuu + b Iuw
    Iuu, Iww, Iuw = sec['Iuu'], sec['Iww'], sec['Iuw']
    det = Iuu * Iww - Iuw * Iuw
    # 풀기: [Iuw Iww; Iuu Iuw][a b] = [−Mx, Mz]
    a = (-M[0] * Iuw - Mz_(M) * Iww) / (Iuw * Iuw - Iww * Iuu)
    b = (Iuw * Mz_(M) + M[0] * Iuu) / (Iuw * Iuw - Iww * Iuu)
    N = F[1]
    tau_t = abs(M[1]) * tor['gmax'] / tor['J'] if tor else 0.0
    tau_v = 1.5 * math.hypot(F[0], F[2]) / sec['A']
    smax, spos, snotch, snpos = 0.0, None, 0.0, None
    for (x, z, kt) in sec['cells']:
        s = abs(N / sec['A'] + a * (x - sec['xc']) + b * (z - sec['zc']))
        if s > smax:
            smax, spos = s, (round(x, 2), round(z, 2))
        if kt and s * kt > snotch:
            snotch, snpos = s * kt, (round(x, 2), round(z, 2), kt)
    vm = math.sqrt(smax ** 2 + 3 * (tau_t + tau_v) ** 2)
    vmn = math.sqrt(snotch ** 2 + 3 * (tau_t + tau_v) ** 2) if snotch else 0.0
    return dict(F=[round(v, 2) for v in F], M=[round(v, 1) for v in M], sigma_max=round(smax, 3), at=spos,
                tau_torsion=round(tau_t, 3), tau_shear=round(tau_v, 3), vm=round(vm, 3), vm_notch=round(vmn, 3), notch_at=snpos)


def Mz_(M):
    return M[2]


def cut_mask_new(x, y, z):
    """셀이 컷 경계 0.15 안이면 Kt: 주머니·슬릿 모서리 2.5, 통로 구멍 옆 3.0. 없으면 0."""
    h = 0.15
    if not (-8.5 <= y <= 4.0 and z >= 20.5):
        return 0
    for dx, dz in ((h, 0), (-h, 0), (0, h), (0, -h)):
        for dy in (0.0, h, -h):
            if not solid(x + dx, y + dy, z + dz, True) and solid(x + dx, y + dy, z + dz, False):
                # 어느 컷인가
                xx, yy, zz = x + dx, y + dy, z + dz
                d = (xx - CH_O[0], yy - CH_O[1], zz - CH_O[2])
                t = d[0] * CH_DIR[0] + d[1] * CH_DIR[1]
                if 0 <= t <= CH_L and (d[0] - t * CH_DIR[0]) ** 2 + (d[1] - t * CH_DIR[1]) ** 2 + d[2] ** 2 < CH_R ** 2:
                    return KT_HOLE
                return KT_CORNER
    return 0


def cut_mask_old(x, y, z):
    return 0


# 단면 위치: 뿌리 Y −10, 통로가 지나는 −10~−6.7, 주머니 −8.05~3.61, 노즈 앞까지
YS = [-10.0 + 0.0001] + [round(-10 + 0.5 * i, 2) for i in range(1, 39)]
rows = {'new': [], 'old': []}
for tag, cuts, mask in (('new', True, cut_mask_new), ('old', False, cut_mask_old)):
    for y in YS:
        sec = section_y(y, cuts, mask if cuts else None)
        tor = torsion_y(y, cuts, iters=3000, tol=1e-6)
        r = dict(y=round(y, 2), n_hole=tor['n_hole'], tau_at=tor['gpos'], A=round(sec['A'], 2), xc=round(sec['xc'], 3), zc=round(sec['zc'], 3),
                 Iuu=round(sec['Iuu'], 1), Iww=round(sec['Iww'], 1), Iuw=round(sec['Iuw'], 1), J=round(tor['J'], 1))
        for cname, (loads, need) in CASES.items():
            r[cname] = stress_y(sec, tor, y, loads)
        rows[tag].append(r)
    log('[%s] 단면 %d개 풀림' % (tag, len(YS)))


def worst(tag, cname, key):
    best = max(rows[tag], key=lambda r: r[cname][key])
    return best['y'], best[cname][key], best[cname]


R = {}
for cname, (loads, need) in CASES.items():
    for key in ('vm', 'vm_notch'):
        yn, vn, dn = worst('new', cname, key)
        yo, vo, do = worst('old', cname, key) if key == 'vm' else (None, 0.0, None)
        sf = ALLOW_R / vn if vn > 0 else float('inf')
        verdict = '동작(SF<1.2)' if sf < SF_BREAK else ('기준 미달(디테일)' if sf < need else '통과')
        R['%s_%s' % (cname, key)] = dict(case=cname, kind=('공칭' if key == 'vm' else '노치 Kt'), y=yn, vm=round(vn, 2),
                                         sf=round(sf, 2) if sf < 1e6 else 'inf', need=need, verdict=verdict, detail=dn,
                                         old_y=yo, old_vm=round(vo, 2) if vo else None,
                                         old_sf=(round(ALLOW_R / vo, 2) if vo else None))
        log('%-6s %-7s 최대 Y %6.2f  σvm %7.2f MPa  SF %6.2f (필요 %.0f) %s   | 옛 형상 %s'
            % (cname, '공칭' if key == 'vm' else 'Kt', yn, vn, sf, need, verdict,
               ('Y %.2f σvm %.2f SF %.2f' % (yo, vo, ALLOW_R / vo)) if vo else '-'))

# ================================================================== 처짐: 오조작 X에서 바늘 구멍(Y 0) X 이동 — 바닥 판 굽힘 몫의 차이
def plate_disp(tag, F, ycut=0.0):
    """Y −10(뿌리) ~ Y 0(구멍) 사이 판 면 안 굽힘(Z축) 몫: δ = ∫ F (10 − y)(0 − y) / (E Iuu) dy (단면 0.5 간격 사다리꼴)."""
    pts = [(r['y'], r['Iuu']) for r in rows[tag] if r['y'] <= ycut + 1e-9]
    s = 0.0
    for (y1, I1), (y2, I2) in zip(pts, pts[1:]):
        f1 = F * (10 - y1) * (ycut - y1) / (E_R * I1); f2 = F * (10 - y2) * (ycut - y2) / (E_R * I2)
        s += (f1 + f2) / 2 * (y2 - y1)
    return s


d_new = plate_disp('new', F_MIS); d_old = plate_disp('old', F_MIS)
t02 = json.load(open(T02_RES, encoding='utf-8'))
dh_t02 = t02['foot_hole_disp']['misX']['x']
dh_new = dh_t02 + (d_new - d_old)
log('바늘 구멍 X 이동(오조작 X): 판 굽힘 몫 옛 %.4f → 새 %.4f mm, T02 합계 %.3f → %.3f (틈 %.2f, 남음 %.3f)'
    % (d_old, d_new, dh_t02, dh_new, GAP_NEEDLE, GAP_NEEDLE - dh_new))
d_new_op = plate_disp('new', F_DRAG); d_old_op = plate_disp('old', F_DRAG)
dh_op = t02['foot_hole_disp']['op']['x'] + (d_new_op - d_old_op)

# ================================================================== 슬릿 둘레 바닥(두께 2) 국부 휨: 누름 50 N을 주머니 바닥 면적에 다 몰았을 때
ledge = (3.15 - 1.0) / 2       # 슬릿 옆 턱 폭(외팔)
p_all = F_PRESS / (12.0 * 3.15)
s_ledge = 3 * p_all * ledge ** 2 / 2.0 ** 2
log('슬릿 옆 바닥 턱(외팔 %.3f, t 2): 누름 50 N 전부를 주머니 면적에 몰아도 p %.2f MPa → σ %.2f MPa, SF %.0f'
    % (ledge, p_all, s_ledge, ALLOW_R / s_ledge))

# 얇은 벽: 주머니 ↔ 바늘 구멍, 주머니 ↔ 옆면(X −9)
def wall_runs(y, z):
    xs_ = [-9 + (j + 0.5) * 0.01 for j in range(1800)]
    out, cur = [], None
    for x in xs_:
        s = solid(x, y, z, True)
        if s and cur is None:
            cur = x
        if not s and cur is not None:
            out.append((cur, x)); cur = None
    if cur is not None:
        out.append((cur, 9.0))
    return out


walls = []
for i in range(0, 120):
    y = round(-8.0 + i * 0.1, 2)
    for (a, b) in wall_runs(y, 27.0):
        walls.append((round(b - a, 3), y, round(a, 2), round(b, 2)))
walls.sort()
thin = [w for w in walls if w[0] < 3.0][:6]
log('주머니 높이(Z 27) 얇은 살(폭, Y, X 구간):', thin)

# ================================================================== 결과 저장
over_note = '노루발 전체 지배 SF는 T02 자루(오조작 X 2.41)와 이번 바닥 값 중 작은 쪽 — 필요 2의 3배(6) 미만이라 과사양 아님'
res = dict(date='2026-10-31', target='3D_Modeling/FSAP_v0.3.2.sc', part='P_T02_FOOT',
           method='손계산(해석 못 함 — 환경 없음, D-16): 단면 수치 적분(격자 0.1) + 비대칭 굽힘 + 프란틀 FD 비틀림(격자 0.2), 교차 검증 없음',
           step_checks=len(checks), step_checks_fail=fails, torsion_check=TORSION_CHECK,
           loads=dict(F_PRESS=F_PRESS, F_DRAG=F_DRAG, F_MIS=F_MIS, W_SELF_3g=round(W_SELF, 3)),
           criteria=dict(SF_REQ=SF_REQ, SF_REQ_MIS=SF_REQ_MIS, SF_BREAK=SF_BREAK, KT_CORNER=KT_CORNER, KT_HOLE=KT_HOLE, allow=ALLOW_R),
           results=R,
           hole_disp=dict(misX_plate_old=round(d_old, 4), misX_plate_new=round(d_new, 4), misX_total_t02=round(dh_t02, 4),
                          misX_total_new=round(dh_new, 4), op_total_new=round(dh_op, 4), gap=GAP_NEEDLE),
           slit_ledge=dict(ledge=ledge, p=round(p_all, 3), sigma=round(s_ledge, 3), sf=round(ALLOW_R / s_ledge, 1)),
           thin_walls_z27=thin,
           unchanged_from_T02=dict(shank_top_misX_sf=2.41, inner_corner_misX_sf=2.57, nose_root_sf=13.88,
                                   note='자루(Z 31.05 이상)·위 노즈는 컷이 닿지 않아 T02 값 그대로(E-19)'),
           overspec=over_note,
           sections=rows)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
log('저장:', OUT)
