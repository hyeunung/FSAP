# -*- coding: utf-8 -*-
"""T01 매트 잡기·회전 유닛 — 강도 손계산 2회차(해석부, 2026-10-30, 대상 v0.2.1).

1회차 케이스 mech_T01_handcalc.py를 복사해 v0.2.1 형상(링2 t5, 띠 Z -12~-7, 링2 샤프트·로드 윗끝 -12)으로 바꿨다.
계산 방법(곡선보 그릴리지·외팔·판 띠)은 1회차와 같다. 2회차에 더한 것: 링 곡선보 검증(Roark 3점 받침 원형 고리),
1회차 결과와 대조, 링2를 고친 뒤 처짐이 틈(간섭)에 주는 영향, 바뀐 링2 하중이 기존 부품(스파이더·허브·DG)에 주는 영향.

해석 못 함 — 환경 없음(자료대기 D-16): 이 컴퓨터에 엔진 해석 환경 engine/fea/.venv가 없다(설치하지 않음).
그래서 엔진 솔버(fea.py, gmsh TET10) 대신 표준 라이브러리만으로 손계산 + 링 곡선보(그릴리지) 수치 계산을 한다.

입력 형상: 모델링부가 내보낸 해석용 임시 STEP 15개(tools/out/mech_T01/stepout/P_T01_*.step).
면 선택·치수는 STEP 형상에서 읽는다(VERTEX_POINT 좌표 bbox, PLANE 면 위치·법선, 축 (0,-700) 기준 반경).
옛 케이스 좌표는 쓰지 않는다.

단위: mm, N, MPa, kg.  실행: python -B fea/cases/mech_T01_fea1_handcalc.py  → fea/results/mech_T01_fea1_handcalc.json
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T01', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T01_fea1_handcalc.json')
OUT_R1 = os.path.join(ROOT, 'fea', 'results', 'mech_T01_handcalc.json')   # 1회차 결과(대조용, 읽기만)
AX = (0.0, -700.0)          # 회전축(대기 자세 세계 좌표, 선정 3절)
g = 9.81
pi = math.pi

# ------------------------------------------------------------------ 재료 (E MPa, nu, 허용 기준 MPa, 밀도 kg/mm3, 출처)
MAT = {
    'SUS304':   (193000.0, 0.29, 205.0, 7.93e-6, '엔진 fea.py MAT(항복), 밀도 모델 재질'),
    'A5052':    (70300.0, 0.33, 175.0, 2.68e-6, '엔진 fea.py MAT(항복), 밀도 모델 재질'),
    'PET-CF':   (4000.0, 0.35, 20.0, 1.29e-6, '자리값: E 4 GPa(접목기 해석 케이스 G 값), 허용 20 MPa = 층간(Z) 강도 자리값. 데이터시트 확인 못 함'),
    'Rigid10K': (10000.0, 0.30, 65.0, 1.65e-6, '자리값: Formlabs Rigid 10K 후경화 인장강도 65 MPa·탄성 10 GPa(기억값, 데이터시트 확인 못 함). 취성이라 인장강도 기준'),
    'Steel':    (206000.0, 0.30, 345.0, 7.85e-6, '구매품 임시 형상(샤프트·로드) 참고용 S45C급'),
}

# ------------------------------------------------------------------ 하중 자리값 (자료대기 D-번호)
P_SUPPLY = 0.5      # MPa, 요구서 2-4 운전 압력 미정 → 0-6 기본 공급 0.5 MPa
BORE = 16.0         # CJ2B16
F_CYL = P_SUPPLY * pi * BORE ** 2 / 4      # 100.5 N (스프링 복귀력은 빼지 않음 = 보수)
T_DG_MAX = 50.0e3   # N·mm DGM200R 허용 토크(구상 2 출처, 카탈로그 미확인 D-17) = 막힘 때 최대
F_DRAG = 20.0       # N 바늘·노루발 끌림(D-10)
ALPHA = 5.0e-6      # rad/ms2 → 5 rad/s2 (단위 맞춤은 아래에서 SI로)
ACC = 2.0           # m/s2 이송(D-12)
RHO_A = 4.0e-6      # kg/mm2 매트 면밀도 4 kg/m2 (D-04)
MU = 0.5            # 매트 뒷면 마찰(D-04)
NG = 3.0            # 자중 × 3 g
SF_REQ, SF_REQ_MIS = 3.0, 2.0      # M-09 기본값(요구서 6-1 비어 있음)
SF_OVER = 3.0 * SF_REQ             # 필요치의 3배 이상 = 과사양 (M-09)
SF_BREAK = 1.2                     # 해석부 지시: SF < 1.2 = 부러짐·영구 변형(동작 문제)


# ================================================================== STEP 읽기
def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ent = {}
    for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
        ent[int(m.group(1))] = m.group(2).replace('\n', '')
    def pt(i):
        s = ent[i]
        nums = re.findall(r'\(([^()]*)\)\s*\)\s*$', s)
        v = re.search(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", s)
        return tuple(float(x) for x in v.group(1).split(','))
    def dirn(i):
        v = re.search(r"DIRECTION\('[^']*',\(([^)]*)\)\)", ent[i])
        return tuple(float(x) for x in v.group(1).split(','))
    verts = []
    for i, s in ent.items():
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
    planes = []
    for i, s in ent.items():
        m = re.match(r"PLANE\('[^']*',#(\d+)\)", s)
        if m:
            a = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ent[int(m.group(1))])
            loc = pt(int(a.group(1))); n = dirn(int(a.group(2)))
            planes.append(dict(loc=[round(c, 3) for c in loc], normal=[round(c, 3) for c in n]))
    cyls = []
    for i, s in ent.items():
        m = re.match(r"CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)", s)
        if m:
            cyls.append(float(m.group(2)))
    xs, ys, zs = zip(*verts)
    rr = [math.hypot(v[0] - AX[0], v[1] - AX[1]) for v in verts]
    zpl = sorted(set(round(p['loc'][2], 2) for p in planes if abs(abs(p['normal'][2]) - 1) < 1e-6))
    return dict(n_vert=len(verts), bbox=[[round(min(xs), 2), round(max(xs), 2)], [round(min(ys), 2), round(max(ys), 2)], [round(min(zs), 2), round(max(zs), 2)]],
                r_axis=[round(min(rr), 2), round(max(rr), 2)], z_planes=zpl, n_planes=len(planes), cyl_radii=sorted(set(round(c, 2) for c in cyls)),
                side_planes=[p for p in planes if abs(p['normal'][2]) < 1e-6])


geom = {}
for f in sorted(os.listdir(STEPDIR)):
    if f.endswith('.step'):
        geom[f[:-5]] = read_step(os.path.join(STEPDIR, f))
for k in geom:
    geom[k].pop('side_planes')          # 결과 파일에는 요약만

# 손계산에 쓰는 치수를 STEP에서 읽어 확인한다(허용 0.6 mm)
def chk(name, what, got, want, tol=0.6):
    ok = abs(got - want) <= tol
    checks.append(dict(part=name, what=what, step=got, used=want, ok=ok))
    return got
checks = []
strap_theta = {}
G = geom
chk('P_T01_DISC', 'R 바깥', G['P_T01_DISC']['r_axis'][1], 55.0)
chk('P_T01_DISC', 'Z 밑면', G['P_T01_DISC']['z_planes'][0], -12.5)
chk('P_T01_DISC', 'Z 윗면', G['P_T01_DISC']['z_planes'][-1], -0.5)
chk('P_T01_POST', 'R 안', G['P_T01_POST']['r_axis'][0], 20.0)
chk('P_T01_POST', 'R 바깥', G['P_T01_POST']['r_axis'][1], 30.0)
chk('P_T01_POST', 'Z 밑면', G['P_T01_POST']['z_planes'][0], -235.0)
chk('P_T01_POST', 'Z 윗면', G['P_T01_POST']['z_planes'][-1], -12.5)
chk('P_T01_HUB', 'R 안', G['P_T01_HUB']['r_axis'][0], 20.0)
chk('P_T01_HUB', 'R 바깥', G['P_T01_HUB']['r_axis'][1], 150.0)
chk('P_T01_HUB', 'Z 밑면', G['P_T01_HUB']['z_planes'][0], -241.0)
chk('P_T01_HUB', 'Z 윗면', G['P_T01_HUB']['z_planes'][-1], -235.0)
chk('P_T01_RING1', 'R 안', G['P_T01_RING1']['r_axis'][0], 75.0)
chk('P_T01_RING1', 'R 바깥', G['P_T01_RING1']['r_axis'][1], 300.0)
chk('P_T01_RING1', 't', G['P_T01_RING1']['z_planes'][-1] - G['P_T01_RING1']['z_planes'][0], 10.0)
chk('P_T01_RING2', 'R 안', G['P_T01_RING2']['r_axis'][0], 310.0)
chk('P_T01_RING2', 'R 바깥', G['P_T01_RING2']['r_axis'][1], 520.0)
T2 = 5.0                                   # v0.2.1 링2 두께(모델링부 T01-M07)
chk('P_T01_RING2', 't', G['P_T01_RING2']['z_planes'][-1] - G['P_T01_RING2']['z_planes'][0], T2)
chk('P_T01_RING2', 'Z 밑면', G['P_T01_RING2']['z_planes'][0], -7.0)
chk('P_T01_RING2', 'Z 윗면', G['P_T01_RING2']['z_planes'][-1], -2.0)
for i in range(1, 7):
    s = G['P_T01_RING2_STRAP_%d' % i]
    chk('P_T01_RING2_STRAP_%d' % i, 't', s['z_planes'][-1] - s['z_planes'][0], 5.0)
    chk('P_T01_RING2_STRAP_%d' % i, 'Z 밑면', s['z_planes'][0], -12.0)
    chk('P_T01_RING2_STRAP_%d' % i, 'Z 윗면(= 링2 밑면)', s['z_planes'][-1], -7.0)
    chk('P_T01_RING2_STRAP_%d' % i, 'r 안끝', s['r_axis'][0], 320.0, tol=1.0)     # 꼭짓점 반경(폭 40 모서리 → 320.6)
    chk('P_T01_RING2_STRAP_%d' % i, 'r 바깥끝', s['r_axis'][1], 515.0, tol=1.0)
    _bx = s['bbox']; _cx = (_bx[0][0] + _bx[0][1]) / 2 - AX[0]; _cy = (_bx[1][0] + _bx[1][1]) / 2 - AX[1]
    _th = math.degrees(math.atan2(_cy, _cx)) % 360
    checks.append(dict(part='P_T01_RING2_STRAP_%d' % i, what='각도 θ(bbox 중심)', step=round(_th, 2), used=None, ok=True))
    strap_theta[i] = _th
for i in range(1, 4):
    s = G['P_T01_SPIDER_%d' % i]
    chk('P_T01_SPIDER_%d' % i, 'Z 밑(다리)', s['z_planes'][0], -235.0)
    chk('P_T01_SPIDER_%d' % i, 'Z 위(웹)', s['z_planes'][-1], -85.0)
    chk('P_T01_SPIDER_%d' % i, '웹 밑면', [z for z in s['z_planes'] if -90 < z < -86][0], -88.0)
yb = G['P_T01_YPLATE']['bbox']
chk('P_T01_YPLATE', 'X 폭', yb[0][1] - yb[0][0], 400.0)
chk('P_T01_YPLATE', 'Y 폭', yb[1][1] - yb[1][0], 500.0)
chk('P_T01_YPLATE', 't', yb[2][1] - yb[2][0], 15.0)
sp1 = G['P_T01_SPIDER_1']['bbox']      # θ 90°: +Y 방향으로 뻗음 → 폭(접선)은 X, 길이는 Y
chk('P_T01_SPIDER_1', '폭(X)', sp1[0][1] - sp1[0][0], 60.0)
chk('P_T01_SPIDER_1', '안끝 r(Y)', sp1[1][0] - AX[1], 100.0)
chk('P_T01_SPIDER_1', '바깥끝 r(Y)', sp1[1][1] - AX[1], 490.0)

R = dict(method='손계산 + 링 곡선보 수치(표준 라이브러리). 엔진 솔버(fea.py) 못 씀 — 환경 없음(D-16)', step_geometry=geom, step_checks=checks, parts={})

# ================================================================== 질량 (모델 질량, E-09)
mass = dict(DISC=0.1882, POST=0.4508, HUB=3.3034, SPIDER=3.2395, RING1=7.1037, RING2=7.3373, STRAP=0.1045, YPLATE=8.040)
st = MAT['Steel'][3]
m_cyl = pi * 9 ** 2 * 130 * st                     # STEP대기_CJ2B16-60S 몸통 Ø18×130 (속 찬 임시 형상)
m_bush = (pi * 14 ** 2 * 37 + pi * 24 ** 2 * 5 - pi * 8.5 ** 2 * 42) * st
m_shaft = pi * 8 ** 2 * 150 * st                   # PSFJ16-150
m_rod1 = pi * 2.5 ** 2 * 74.5 * st; m_rod2 = pi * 2.5 ** 2 * 73 * st      # v0.2.1 로드 Z -85~-12
m_dg = (200 * 200 * 100 + 90 * 160 * 90) * st      # STEP대기_DGM200R-AZAC 임시 형상(속 찬 상자)
m_blk = 44 * 72 * 24 * st
mat_L = dict(a=600.0, m=RHO_A * 1200 * 1200)       # 큰 매트 1200×1200 (D-01 임시값)
mat_S = dict(m=RHO_A * 300 * 200)
R['mass_kg'] = dict(model=mass, cyl_placeholder=m_cyl, bush_placeholder=m_bush, shaft=m_shaft, dg_placeholder=m_dg, block=m_blk, mat_large=mat_L['m'], mat_small=mat_S['m'])


# ================================================================== 링 곡선보(그릴리지) 수치 모델
def lu(A):
    n = len(A); A = [row[:] for row in A]; piv = list(range(n))
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(A[i][k]))
        if p != k:
            A[k], A[p] = A[p], A[k]; piv[k], piv[p] = piv[p], piv[k]
        akk = A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / akk
            if f:
                A[i][k] = f
                Ai, Ak = A[i], A[k]
                for j in range(k + 1, n):
                    Ai[j] -= f * Ak[j]
    return A, piv


def lu_solve(LU, piv, b):
    n = len(LU); x = [b[piv[i]] for i in range(n)]
    for i in range(n):
        s = x[i]; Li = LU[i]
        for j in range(i):
            s -= Li[j] * x[j]
        x[i] = s
    for i in range(n - 1, -1, -1):
        s = x[i]; Ui = LU[i]
        for j in range(i + 1, n):
            s -= Ui[j] * x[j]
        x[i] = s / Ui[i]
    return x


def elem_k(p1, p2, EI, GJ):
    """그릴리지 요소(면외): 절점 자유도 [w, psiX, psiY]. 반환 (6x6 전역 K, 국부 변환, L)."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]; L = math.hypot(dx, dy); cx, cy = dx / L, dy / L
    kb = EI / L ** 3
    # 국부 [w, psi_x', psi_y'] (theta = dw/dx' = -psi_y')
    Kl = [[0.0] * 6 for _ in range(6)]
    B = [[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]]
    idx = [0, 2, 3, 5]; sgn = [1, -1, 1, -1]
    for a in range(4):
        for b in range(4):
            Kl[idx[a]][idx[b]] += kb * B[a][b] * sgn[a] * sgn[b]
    kt = GJ / L
    Kl[1][1] += kt; Kl[4][4] += kt; Kl[1][4] -= kt; Kl[4][1] -= kt
    T = [[0.0] * 6 for _ in range(6)]
    for n0 in (0, 3):
        T[n0][n0] = 1.0
        T[n0 + 1][n0 + 1] = cx; T[n0 + 1][n0 + 2] = cy
        T[n0 + 2][n0 + 1] = -cy; T[n0 + 2][n0 + 2] = cx
    # K = T^t Kl T
    KT = [[sum(Kl[i][k] * T[k][j] for k in range(6)) for j in range(6)] for i in range(6)]
    K = [[sum(T[k][i] * KT[k][j] for k in range(6)) for j in range(6)] for i in range(6)]
    return K, Kl, T, L


class Grid:
    def __init__(self, nodes, elems, EI, GJ):
        self.nodes = nodes; self.elems = elems; self.EI = EI; self.GJ = GJ
        n = 3 * len(nodes); self.n = n
        self.K = [[0.0] * n for _ in range(n)]
        self.data = []
        for (a, b) in elems:
            K, Kl, T, L = elem_k(nodes[a], nodes[b], EI, GJ)
            dofs = [3 * a, 3 * a + 1, 3 * a + 2, 3 * b, 3 * b + 1, 3 * b + 2]
            for i in range(6):
                for j in range(6):
                    self.K[dofs[i]][dofs[j]] += K[i][j]
            self.data.append((dofs, Kl, T, L))

    def support(self, node, kw=1e12, krot=0.0):
        self.K[3 * node][3 * node] += kw
        if krot:
            self.K[3 * node + 1][3 * node + 1] += krot; self.K[3 * node + 2][3 * node + 2] += krot

    def factor(self):
        self.LU, self.piv = lu(self.K)

    def solve(self, F):
        d = lu_solve(self.LU, self.piv, F)
        out = []
        for dofs, Kl, T, L in self.data:
            dg = [d[i] for i in dofs]
            dl = [sum(T[i][j] * dg[j] for j in range(6)) for i in range(6)]
            f = [sum(Kl[i][j] * dl[j] for j in range(6)) for i in range(6)]
            # 끝 굽힘 모멘트(국부 psi_y' 성분) · 비틀림(psi_x')
            out.append(dict(Mb=max(abs(f[2]), abs(f[5])), T=max(abs(f[1]), abs(f[4]))))
        return d, out


# --- 검증 1: 직선 단순보 등분포 → 5wL^4/384EI
def verify_straight():
    N = 40; Ltot = 1000.0; EI = 7.0e7; w = 0.1
    nodes = [(Ltot * i / N, 0.0) for i in range(N + 1)]
    elems = [(i, i + 1) for i in range(N)]
    gr = Grid(nodes, elems, EI, 1e9)
    gr.support(0); gr.support(N)
    gr.K[1][1] += 1e9; gr.K[3 * N + 1][3 * N + 1] += 1e9   # 비틀림 강체 모드 막음
    gr.factor()
    F = [0.0] * gr.n
    for i in range(N + 1):
        F[3 * i] = -w * Ltot / N * (0.5 if i in (0, N) else 1.0)
    d, out = gr.solve(F)
    num = -d[3 * (N // 2)]; th = 5 * w * Ltot ** 4 / (384 * EI)
    Mnum = max(o['Mb'] for o in out); Mth = w * Ltot ** 2 / 8
    return dict(defl_num=num, defl_theory=th, err_defl=num / th - 1, M_num=Mnum, M_theory=Mth, err_M=Mnum / Mth - 1)


# --- 검증 2: 외팔보 끝 하중 → PL^3/3EI (기울어진 방향 30°, 변환 확인)
def verify_cantilever():
    N = 20; Ltot = 500.0; EI = 5.0e7; P = 10.0; c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    nodes = [(Ltot * i / N * c, Ltot * i / N * s) for i in range(N + 1)]
    elems = [(i, i + 1) for i in range(N)]
    gr = Grid(nodes, elems, EI, 1e9)
    gr.support(0, krot=1e14)
    gr.factor()
    F = [0.0] * gr.n; F[3 * N] = -P
    d, out = gr.solve(F)
    num = -d[3 * N]; th = P * Ltot ** 3 / (3 * EI)
    return dict(defl_num=num, defl_theory=th, err=num / th - 1)


R['verify'] = dict(straight_ss=verify_straight(), cantilever_30deg=verify_cantilever())


def ring_model(r_n, b, t, E, nu, krot, N=72, w_nodes=None, e_contact=0.0):
    """w_nodes=None: 받침 3곳(θ 90·210·330)에서 w=0 + 회전 스프링. w_nodes=[i]: 실린더 힘 제어(막힘) — w=0은 걸린 점 i만, 받침 3곳은 회전 스프링만."""
    nodes = [(r_n * math.cos(2 * pi * i / N), r_n * math.sin(2 * pi * i / N)) for i in range(N)]
    elems = [(i, (i + 1) % N) for i in range(N)]
    I = b * t ** 3 / 12; J = b * t ** 3 / 3 * (1 - 0.63 * t / b); Gm = E / (2 * (1 + nu))
    gr = Grid(nodes, elems, E * I, Gm * J)
    sup = [round(N * a / 360) % N for a in (90, 210, 330)]
    if w_nodes is None:
        for s in sup:
            gr.support(s, krot=krot)
    else:
        for s in sup:
            gr.support(s, kw=0.0, krot=krot)
        for s in w_nodes:
            # 걸린 점은 노드 선에서 e_contact 바깥(링 바깥 끝): w_edge = w - psi_t*e = 0 을 벌칙으로
            th = 2 * pi * s / N; a = [1.0, e_contact * math.sin(th), -e_contact * math.cos(th)]
            for i in range(3):
                for j in range(3):
                    gr.K[3 * s + i][3 * s + j] += 1e12 * a[i] * a[j]
    gr.factor()
    gr.sup = sup; gr.N = N; gr.r_n = r_n; gr.Z = b * t ** 2 / 6; gr.Zt = b * t ** 2 / 3; gr.I = I; gr.J = J
    return gr


def ring_loads(gr, items):
    """items: (kind, ...)  모두 아래 방향 하중(N). kind 'unif'(W 총합, r_L), 'dens'(f(theta)→N/rad, r_L), 'point'(P, theta, r_L)."""
    N = gr.N; F = [0.0] * gr.n; dth = 2 * pi / N
    def add(i, W, rL):
        th = 2 * pi * i / N
        F[3 * i] -= W
        mt = (rL - gr.r_n) * W            # 접선축 모멘트(바깥이 내려가는 쪽 +)
        F[3 * i + 1] += mt * (-math.sin(th)); F[3 * i + 2] += mt * math.cos(th)
    for it in items:
        if it[0] == 'unif':
            for i in range(N):
                add(i, it[1] / N, it[2])
        elif it[0] == 'dens':
            for i in range(N):
                add(i, it[1](2 * pi * i / N) * dth, it[2])
        elif it[0] == 'point':
            i = round(it[2] / (2 * pi) * N) % N
            add(i, it[1], it[3])
    return F


def ring_result(gr, d, out, r_in, r_out):
    N = gr.N; wmax = 0.0; wedge = []; wabs = 0.0
    for i in range(N):
        th = 2 * pi * i / N
        w = d[3 * i]; pt = d[3 * i + 1] * (-math.sin(th)) + d[3 * i + 2] * math.cos(th)
        we = w - pt * (r_out - gr.r_n); wi = w + pt * (gr.r_n - r_in)
        wedge.append(we)
        wmax = min(wmax, we, wi, w); wabs = max(wabs, abs(we), abs(wi), abs(w))
    Mb = max(o['Mb'] for o in out); T = max(o['T'] for o in out)
    sig = Mb / gr.Z; tau = T / gr.Zt
    # 받침점 반력(수직)·회전 반력
    reac = []
    for s in gr.sup:
        reac.append(dict(node=s, Fz=-d[3 * s] * 1e12, Mrot=math.hypot(d[3 * s + 1], d[3 * s + 2]) * gr.krot if hasattr(gr, 'krot') else 0.0))
    return dict(w_min=wmax, w_absmax=wabs, sigma_b=sig, tau_t=tau, sigma_eq=math.sqrt(sig ** 2 + 3 * tau ** 2), Mb=Mb, T=T, reac=reac)


def square_overhang(beta, a, R0):
    """정사각 매트(반폭 a)를 beta만큼 돌렸을 때, 반경 R0 밖 면적의 각도 밀도(mm2/rad) 함수."""
    def f(th):
        p = th - beta
        rho = a / max(abs(math.cos(p)), abs(math.sin(p)))
        return max(0.0, (rho ** 2 - R0 ** 2) / 2)
    return f


# 샤프트(PSFJ16)가 부시(LHFR16) 안에서 링 기울기를 막는 회전 강성: 외팔 끝 모멘트 k = EI/L
L_SHAFT_FREE = {'RING1': -80.0 - (-10.5), 'RING2': -80.0 - (-12.0)}   # v0.2.1: 링2 샤프트 윗끝 -12      # 부시 플랜지 윗면 −80 ~ 링 밑(올림)
I_SH = pi * 16 ** 4 / 64
K_ROT = {k: MAT['Steel'][0] * I_SH / abs(v) for k, v in L_SHAFT_FREE.items()}
R['shaft_rot_stiffness_Nmm_per_rad'] = K_ROT


def ring_case(name, r_n, r_in, r_out, b, t, mat, m_ring, mat_band_kg_per_rad, r_band, overhang, P_jam):
    E, nu, sy, rho, _ = MAT[mat]
    res = {}
    for bc, kr in (('샤프트_고정(회전 스프링)', K_ROT[name]), ('핀(회전 자유, 상한)', 0.0)):
        gr = ring_model(r_n, b, t, E, nu, kr); gr.krot = kr
        worst = None
        for bdeg in range(0, 91, 5):
            beta = math.radians(bdeg)
            items = [('unif', m_ring * g, (r_in + r_out) / 2 if name == 'RING1' else 423.9)]
            if mat_band_kg_per_rad:
                items.append(('dens', (lambda th, v=mat_band_kg_per_rad: v * g), r_band))
            if overhang:
                fo = square_overhang(beta, mat_L['a'], r_out)
                items.append(('dens', (lambda th, f=fo: f(th) * RHO_A * g), r_out))
            F1 = ring_loads(gr, items)
            d, out = gr.solve(F1)
            r1 = ring_result(gr, d, out, r_in, r_out)
            r1['beta_deg'] = bdeg
            if worst is None or r1['sigma_eq'] > worst['sigma_eq']:
                worst = r1
        # 1 g 결과 → 3 g 응력, 1 g 처짐
        res[bc] = dict(beta_worst_deg=worst['beta_deg'], defl_1g_min_mm=worst['w_min'], sigma_eq_3g=NG * worst['sigma_eq'],
                       sigma_b_3g=NG * worst['sigma_b'], tau_3g=NG * worst['tau_t'], SF_3g=sy / (NG * worst['sigma_eq']),
                       reac_1g=worst['reac'], Mb_1g=worst['Mb'], T_1g=worst['T'])
        # 오조작: 실린더 막힘 — 링이 올라가다 한 점에 걸림, 실린더 3개 추력 전부가 그 점 반력(보수) + 1 g
        wj = None
        for adeg in range(90, 211, 5):
            Fj = ring_loads(gr, [('unif', m_ring * g, (r_in + r_out) / 2), ('point', P_jam, math.radians(adeg), r_out)])
            d, out = gr.solve(Fj)
            rj = ring_result(gr, d, out, r_in, r_out); rj['angle_deg'] = adeg
            if wj is None or rj['sigma_eq'] > wj['sigma_eq']:
                wj = rj
        res[bc]['jam_rigid_supports'] = dict(P=P_jam, angle_deg=wj['angle_deg'], sigma_eq=wj['sigma_eq'], SF=sy / wj['sigma_eq'], defl_mm=wj['w_min'])
        # 막힘(힘 제어, 실제에 가까움): 실린더 3개가 각 F_CYL로 밀고(받침 수직 자유), 걸린 점 하나가 w=0, 샤프트가 기울기를 막음
        if kr:
            wf = None
            for adeg in range(90, 211, 5):
                N = 72; ic = round(adeg / 360 * N) % N
                grj = ring_model(r_n, b, t, E, nu, kr, w_nodes=[ic], e_contact=r_out - r_n)
                Fj = ring_loads(grj, [('unif', m_ring * g, (r_in + r_out) / 2), ('point', -P_jam / 3, math.radians(90), r_n),
                                      ('point', -P_jam / 3, math.radians(210), r_n), ('point', -P_jam / 3, math.radians(330), r_n)])
                d, out = grj.solve(Fj)
                rj = ring_result(grj, d, out, r_in, r_out); rj['angle_deg'] = adeg
                if wf is None or rj['sigma_eq'] > wf['sigma_eq']:
                    wf = rj
            res[bc]['jam'] = dict(P_each_cyl=P_jam / 3, angle_deg=wf['angle_deg'], sigma_eq=wf['sigma_eq'], sigma_b=wf['sigma_b'], tau=wf['tau_t'], SF=sy / wf['sigma_eq'], defl_absmax_mm=wf['w_absmax'])
    return res


# ---- RING2: A5052 t5 R310~520, 받침 = 로드 r410(수직) + 샤프트 r460(기울기) θ 90·210·330
m_ring2_all = mass['RING2'] + 6 * mass['STRAP'] + 3 * (m_shaft + m_rod2)
band2 = (520 ** 2 - 310 ** 2) / 2 * RHO_A          # kg/rad, 링2 띠 위 매트(링2 윗면 −2: 매트가 1.5 처지면 닿음 → 무른 매트라 다 얹힌다고 봄, D-04)
ring2 = ring_case('RING2', 410.0, 310.0, 520.0, 210.0, T2, 'A5052', m_ring2_all, band2, 423.9, True, 3 * F_CYL)
# 링2 바깥 끝 반경 방향 판 굽힘(받침점 사이, 받침 없는 띠 부분): 매트 돌출 선하중이 R520 끝에 걸림, 판 t5 외팔 520−410
qmax = max(square_overhang(math.radians(b), 600.0, 520.0)(math.radians(th)) for b in (0,) for th in range(0, 91)) * RHO_A * g / 520.0   # N/mm (1 g, 모서리)
band_q = band2 * g / 1.0      # N/rad → 반경 방향 띠 하중은 r 따라 고르게: 단위 길이(호) 당 = RHO_A*g*(r) dr
Lc = 520.0 - 410.0
m_rad = qmax * Lc + RHO_A * g * (520 ** 3 / 3 - 410 ** 3 / 3 - 410 * (520 ** 2 - 410 ** 2) / 2) / 520.0 * 1.0  # N·mm/mm (근사)
m_rad += MAT['A5052'][3] * T2 * g * Lc ** 2 / 2
sig_rad = 6 * m_rad / T2 ** 2
D_pl = MAT['A5052'][0] * T2 ** 3 / 12 / (1 - 0.33 ** 2)
defl_rad = qmax * Lc ** 3 / (3 * D_pl) + (RHO_A * g + MAT['A5052'][3] * T2 * g) * Lc ** 4 / (8 * D_pl)
ring2['radial_plate'] = dict(q_edge_corner_1g=qmax, m_root_1g=m_rad, sigma_3g=NG * sig_rad, SF_3g=MAT['A5052'][2] / (NG * sig_rad), defl_edge_1g=defl_rad)
R['parts']['P_T01_RING2'] = ring2

# 링2 두께 안(고치는 방법 비교): t를 바꾸면 질량·관성도 바뀐다 → DG 토크(선정 5절 식) 다시
I_rot_base = 2.63; I_ring2_t3 = 0.81; I_mat = 1.38       # 선정 5절(링2 t3 포함 2.63)
def I_ring2(m):
    return m * (0.520 ** 2 + 0.310 ** 2) / 2              # 고리 관성 kg·m2
variants = {}
for tv in (3.0, 4.0, 5.0, 6.0):
    m_r2 = mass['RING2'] * tv / T2
    mall = m_r2 + 6 * mass['STRAP'] + 3 * (m_shaft + m_rod2)
    rv = ring_case('RING2', 410.0, 310.0, 520.0, 210.0, tv, 'A5052', mall, band2, 423.9, True, 3 * F_CYL)
    c = rv['샤프트_고정(회전 스프링)']
    I_rot = I_rot_base + (I_ring2(m_r2) - I_ring2_t3)
    T_need = (I_rot + I_mat) * 5.0 + F_DRAG * 0.836
    variants['t%d' % tv] = dict(mass_ring2=m_r2, SF_3g=c['SF_3g'], defl_1g=c['defl_1g_min_mm'], SF_jam=c['jam']['SF'], jam_defl=c['jam']['defl_absmax_mm'], SF_jam_rigid=c['jam_rigid_supports']['SF'],
                                rod_load_1g=max(r['Fz'] for r in c['reac_1g']), I_rot=I_rot, T_DG_need_Nm=T_need, T_DG_ratio=50.0 / T_need)
R['parts']['P_T01_RING2']['thickness_variants'] = variants

# ---- RING1: A5052 t10 R75~300, 받침 = 로드 r190 + 샤프트 r240. 진공은 매트+링 계에서 상쇄(선정 1-2) → 매트 무게만
m_ring1_all = mass['RING1'] + 3 * (m_shaft + m_rod1)
band1 = (300 ** 2 - 75 ** 2) / 2 * RHO_A
ring1 = ring_case('RING1', 190.0, 75.0, 300.0, 225.0, 10.0, 'A5052', m_ring1_all, band1, 210.0, False, 3 * F_CYL)
R['parts']['P_T01_RING1'] = ring1

# ---- RING2_STRAP: 받침 자리 띠(폭 40 t5)가 링2 접선축 모멘트를 샤프트로 넘김 + 띠 끝 외팔
st_b, st_t = 40.0, 5.0
Z_strap = st_b * st_t ** 2 / 6
Mrot_strap = max(r['Mrot'] for r in ring2['샤프트_고정(회전 스프링)']['reac_1g'])
Fz_strap = max(r['Fz'] for r in ring2['샤프트_고정(회전 스프링)']['reac_1g'])
M_strap_3g = NG * (Mrot_strap + Fz_strap * 0.0)
# 막힘: 링이 걸린 채 실린더 추력 100.5 N이 로드(r410)에서 띠를 밀고, 샤프트(r460)가 기울기를 막음 → 띠 r410~r460 굽힘 상한 F·50
M_strap_jam = F_CYL * 50.0
R['parts']['P_T01_RING2_STRAP_1~6'] = dict(Z=Z_strap, M_3g=M_strap_3g, sigma_3g=M_strap_3g / Z_strap, SF_3g=MAT['A5052'][2] / max(M_strap_3g / Z_strap, 1e-9),
                                           M_jam=M_strap_jam, sigma_jam=M_strap_jam / Z_strap, SF_jam=MAT['A5052'][2] / (M_strap_jam / Z_strap),
                                           note='띠 단면만(링2 판과 겹친 부분 무시 = 보수). 받침 아닌 띠 3개(θ 30·150·270)는 하중 길이 없음')

# ================================================================== SPIDER (SUS304 ㄷ t3, r100~490, 다리 −235~−88, 웹 −88~−85)
# 단면(STEP: 폭 60, 웹 밑 −88, 다리 밑 −235)
z0 = -235.0
web = (60.0 * 3.0, (-86.5) - z0, 60.0, 3.0)                # (A, z_c, b, h)
leg = (3.0 * 147.0, (-161.5) - z0, 3.0, 147.0)
A_sp = web[0] + 2 * leg[0]
zc = (web[0] * web[1] + 2 * leg[0] * leg[1]) / A_sp
I_sp = web[2] * web[3] ** 3 / 12 + web[0] * (web[1] - zc) ** 2 + 2 * (leg[2] * leg[3] ** 3 / 12 + leg[0] * (leg[1] - zc) ** 2)
Zb = I_sp / zc; Zt = I_sp / (150.0 - zc)
I_lat = 3.0 * 60 ** 3 / 12 + 2 * (147 * 3 ** 3 / 12 + leg[0] * 28.5 ** 2)
J_sp = (60 + 2 * 147) * 3.0 ** 3 / 3
r_root = 150.0                                           # 허브 바깥(다리가 허브 r100~150에 얹힘)
# 하중(1 g, N, 반경 mm): 링 받침 반력(링 모델, 샤프트 고정), 실린더·부시(임시 형상 질량), 스파이더 자중
reac1 = max(r['Fz'] for r in ring1['샤프트_고정(회전 스프링)']['reac_1g'])
reac2 = max(r['Fz'] for r in ring2['샤프트_고정(회전 스프링)']['reac_1g'])
mrot1 = max(r['Mrot'] for r in ring1['샤프트_고정(회전 스프링)']['reac_1g'])
mrot2 = max(r['Mrot'] for r in ring2['샤프트_고정(회전 스프링)']['reac_1g'])
loads_1g = [(reac1 + (m_cyl) * g, 190.0), (m_bush * g, 240.0), (reac2 + m_cyl * g, 410.0), (m_bush * g, 460.0)]
m_sp_out = mass['SPIDER'] * (490 - 150) / 390
loads_1g.append((m_sp_out * g, (150 + 490) / 2))
V_1g = sum(F for F, r in loads_1g)
M_1g = sum(F * (r - r_root) for F, r in loads_1g) + mrot1 + mrot2      # 샤프트 회전 반력을 같은 쪽으로(보수)
M_3g = NG * M_1g; V_3g = NG * V_1g
sig_sp = M_3g / Zb
# 막힘(오조작): 실린더 추력 100.5 N이 웹 r190·r410을 아래로 + 1 g
M_jam = F_CYL * ((190 - r_root) + (410 - r_root)) + M_1g
sig_sp_jam = M_jam / Zb
# 웹 국부: 실린더 로드 커버 너트(Ø19 구멍 둘레)가 웹(다리 사이 54)을 누름 — 양단 고정 띠(유효 폭 30)
Mw = max(F_CYL, NG * (reac2 + m_cyl * g)) * 54.0 / 8.0
sig_web = Mw / (30.0 * 3.0 ** 2 / 6)
# 회전 막힘 토크 50 N·m → 스파이더 3개, 접선 힘(최악: 전부 r240 샤프트) → 옆 굽힘
F_tan = T_DG_MAX / 3 / 240.0
sig_lat = F_tan * (240 - r_root) / (I_lat / 30.0)
# 끝 처짐(스파이더만, 1 g)
E_s = MAT['SUS304'][0]
defl_sp = sum(F * (r - r_root) ** 2 * (3 * (490 - r_root) - (r - r_root)) / (6 * E_s * I_sp) for F, r in loads_1g)
R['parts']['P_T01_SPIDER_1~3'] = dict(A=A_sp, zc_from_bottom=zc, I=I_sp, Z_bottom=Zb, I_lat=I_lat, J=J_sp,
                                     V_1g=V_1g, M_root_1g=M_1g, sigma_3g=sig_sp, SF_3g=MAT['SUS304'][2] / sig_sp,
                                     M_jam=M_jam, sigma_jam=sig_sp_jam, SF_jam=MAT['SUS304'][2] / sig_sp_jam,
                                     web_local_sigma=sig_web, SF_web=MAT['SUS304'][2] / sig_web,
                                     lateral_DGmax_sigma=sig_lat, SF_lat=MAT['SUS304'][2] / sig_lat, tip_defl_1g=defl_sp)

# ================================================================== HUB (SUS304 t6 R20~150, DG 테이블 위)
t_h = 6.0
def hub_case(r_s, V, M):
    F_out = V + M / 50.0; F_in = M / 50.0          # 다리 밑 r150(누름)·r100(들림 = 볼트 인장, 디테일)
    Mh = F_out * (150 - r_s) - F_in * max(0.0, 100 - r_s)
    b = min(60 + 2 * (150 - r_s), 2 * pi * r_s / 3)
    sig = Mh / (b * t_h ** 2 / 6)
    EI = MAT['SUS304'][0] * b * t_h ** 3 / 12
    L = 150 - r_s; a = max(0.0, 100 - r_s)
    d150 = (F_out * L ** 3 / 3 - F_in * a ** 2 * (3 * L - a) / 6) / EI
    sl = (F_out * L ** 2 / 2 - F_in * a ** 2 / 2) / EI
    return dict(r_support=r_s, F_out=F_out, F_in_bolt=F_in, M_hub=Mh, b_eff=b, sigma=sig, SF=MAT['SUS304'][2] / sig, defl_r150=d150, slope=sl)
hub = {}
for lab, rs in (('모델 임시 형상(DG 윗면 ±100, 받침 끝 r100)', 100.0), ('실제 출력 테이블이 Ø100이면(r50, D-17 미확인)', 50.0)):
    h3 = hub_case(rs, V_3g, M_3g)
    h1 = hub_case(rs, V_1g, M_1g)
    hj = hub_case(rs, V_1g + 2 * F_CYL, M_jam)
    # 허브 처짐 → 스파이더 강체 회전 → 링 받침점(r190·r410) 내려감(1 g)
    drop1 = h1['defl_r150'] + h1['slope'] * (190 - 150) + defl_sp * 0
    drop2 = h1['defl_r150'] + h1['slope'] * (410 - 150)
    hub[lab] = dict(normal_3g=h3, jam=hj, ring1_drop_1g=drop1, ring2_drop_1g=drop2, SF_3g=h3['SF'], SF_jam=hj['SF'])
R['parts']['P_T01_HUB'] = hub

# ================================================================== POST (PET-CF 관 Ø60/Ø40, 222.5, 위에 원판)
Lp = 235.0 - 12.5
Ip = pi * (60 ** 4 - 40 ** 4) / 64; Zp = Ip / 30; Jp = 2 * Ip
m_top = mass['DISC'] + mat_S['m']
F_lat = F_DRAG + m_top * ACC                              # 작은 매트: 끌림 + 이송 가속(원판만 잡음)
F_lat_mis = MU * 58e-3 * 9503                             # 오조작: 작은 매트가 부딪쳐 마찰 한계까지 미는 힘(58 kPa × 원판)
r_small = 168.9
T_post = F_DRAG * r_small + mat_S['m'] * (0.3 ** 2 + 0.2 ** 2) / 12 * 5.0 * 1e3   # N·mm
T_post_mis = MU * 58e-3 * 9503 * (2 / 3 * 55)            # 원판이 미끄러지기 전 최대 토크
sp_n = F_lat * Lp / Zp; sp_m = F_lat_mis * Lp / Zp
tau_n = T_post * 30 / Jp; tau_m = T_post_mis * 30 / Jp
eq_n = math.sqrt(sp_n ** 2 + 3 * tau_n ** 2) + NG * m_top * g / (pi * (30 ** 2 - 20 ** 2))
eq_m = math.sqrt(sp_m ** 2 + 3 * tau_m ** 2)
defl_p = F_lat * Lp ** 3 / (3 * MAT['PET-CF'][0] * Ip)
R['parts']['P_T01_POST'] = dict(I=Ip, Z=Zp, F_lat=F_lat, sigma_eq=eq_n, SF=MAT['PET-CF'][2] / eq_n, F_lat_mis=F_lat_mis, sigma_mis=eq_m, SF_mis=MAT['PET-CF'][2] / eq_m, top_defl=defl_p,
                                note='관 벽 10. 세워 출력하면 굽힘 응력이 층간(Z) 방향 → 층간 강도 자리값 20 MPa로 판정')

# ================================================================== DISC (Rigid 10K 원판 R55 t12, 기둥 R20~30 위)
# 진공: 매트+원판 계에서 대기압 상쇄(땅 접촉 = 홈 흡인), 원판 순하중은 무게뿐. 국부 굽힘은 진공 홈 상세(디테일)에서.
# 하중: 3 g 자중·작은 매트 무게를 R30~55 돌출에, 끌림 토크·옆힘은 기둥으로(면내 → 굽힘 작음)
w_d = NG * (mass['DISC'] + mat_S['m']) * g / (pi * (55 ** 2 - 30 ** 2))     # N/mm2 (보수: 전부 돌출부에)
m_disc = w_d * (55 - 30) ** 2 / 2 * (1 + 0.0)                                 # 단위 폭 외팔
sig_d = 6 * m_disc / 12 ** 2
# 진공 포트(밑면 가운데)가 원판을 기둥 쪽으로 당김: 58 kPa × Ø40 = 73 N → 기둥 윗끝 지지 R20~30이 받음(굽힘 거의 0)
R['parts']['P_T01_DISC'] = dict(sigma_3g=sig_d, SF_3g=MAT['Rigid10K'][2] / max(sig_d, 1e-9), port_pull_N=58e-3 * pi * 20 ** 2,
                                shear_mis=F_lat_mis / (pi * 60 * 12), note='취성 재료. 진공 홈·포트 상세가 생기면 홈 밑살에서 다시 본다')

# ================================================================== YPLATE (A5052 t15, 블록 4개 위, DG 임시 형상 얹힘)
m_on = m_dg + mass['DISC'] + mass['POST'] + mass['HUB'] + 3 * mass['SPIDER'] + 6 * m_cyl + 6 * m_bush + m_ring1_all + m_ring2_all + mat_L['m']
W3 = NG * m_on * g
L_diag = math.hypot(150 - 100, 860 - 800)              # DG 바닥 모서리(±100, −800/−600) → 블록 중심(±150, −860/−540)
M_y = W3 / 4 * L_diag
sig_y = M_y / (100.0 * 15 ** 2 / 6)
h_cg = 341.0                                           # 링 윗면(Z 0) ~ 판 윗면(−341)
F_hit = 2 * pi * 3.82e3 * 0.9 / 20.0                   # 400 W 서보 최대 토크 3.82 N·m, 리드 20, 효율 0.9 (형번 미정 D-17, 자리값)
M_hit = F_hit * h_cg
sig_y_hit = (M_hit / 200.0 / 2 * 60.0) / (200.0 * 15 ** 2 / 6) + sig_y / NG
R['parts']['P_T01_YPLATE'] = dict(m_on=m_on, W_3g=W3, L=L_diag, sigma_3g=sig_y, SF_3g=MAT['A5052'][2] / sig_y,
                                  F_hit=F_hit, M_hit=M_hit, sigma_hit=sig_y_hit, SF_hit=MAT['A5052'][2] / sig_y_hit,
                                  defl_1g=(W3 / NG / 4) * L_diag ** 3 / (3 * MAT['A5052'][0] * 100 * 15 ** 3 / 12))

# ================================================================== 구매품 참고(M-06 허용치 대조는 구매부, 여기서는 하중만)
m_rot_tot = mass['DISC'] + mass['POST'] + mass['HUB'] + 3 * mass['SPIDER'] + 6 * m_cyl + 6 * m_bush + m_ring1_all + m_ring2_all
R['purchased_loads'] = dict(
    DG_thrust_3g_N=NG * (m_rot_tot + mat_L['m']) * g,
    DG_moment_normal_Nm=(F_DRAG * 241 + (m_rot_tot + mat_L['m']) * ACC * 120) / 1e3,
    DG_moment_hit_mat_Nm=MU * 3.04e-3 * 274575 * 241 / 1e3,
    DG_moment_hit_servo_Nm=F_hit * 241 / 1e3,
    cyl_rod_load_ring1_3g_N=NG * reac1, cyl_rod_load_ring2_3g_N=NG * reac2, cyl_thrust_N=F_CYL,
    shaft_moment_ring2_3g_Nmm=NG * mrot2, shaft_sigma_ring2_3g=NG * mrot2 / (pi * 16 ** 3 / 32),
    shaft_moment_ring1_3g_Nmm=NG * mrot1)

R['loads'] = dict(P_supply_MPa=P_SUPPLY, F_cyl_N=F_CYL, T_DG_max_Nmm=T_DG_MAX, F_drag_N=F_DRAG, alpha_rad_s2=5.0, acc_m_s2=ACC, rhoA_kg_m2=4.0, mu=MU, n_g=NG,
                 SF_req=SF_REQ, SF_req_mis=SF_REQ_MIS, SF_overspec=SF_OVER, SF_break=SF_BREAK)
R['materials'] = {k: dict(E=v[0], nu=v[1], allow=v[2], rho_kg_mm3=v[3], src=v[4]) for k, v in MAT.items()}


# ================================================================== 2회차 추가 (v0.2.1)
# --- 검증 3: 원형 고리, 같은 간격 n=3 받침(핀), 중심선 등분포 w → Roark(고리 면외 하중):
#     받침 모멘트 M_s = w R^2 (1 - θ cot θ), 경간 가운데 M_m = w R^2 (θ / sin θ - 1), θ = π/n
#     (θ→0이면 양단 고정보 wL^2/12, wL^2/24로 가는 것을 확인한 식)
def verify_ring_roark():
    Rn, b, t, E, nu = 410.0, 210.0, T2, MAT['A5052'][0], 0.33
    gr = ring_model(Rn, b, t, E, nu, 0.0)
    w = 0.01                                      # N/mm
    F = ring_loads(gr, [('unif', w * 2 * pi * Rn, Rn)])
    d, out = gr.solve(F)
    th = pi / 3
    Ms = w * Rn ** 2 * (1 - th / math.tan(th)); Mm = w * Rn ** 2 * (th / math.sin(th) - 1)
    Mnum = max(o['Mb'] for o in out)
    # 경간 가운데(θ 150°, 받침 90·210 사이) 요소 끝 모멘트
    i_mid = round(150 / 360 * gr.N) % gr.N
    Mmid = out[i_mid]['Mb']
    return dict(M_support_theory=Ms, M_mid_theory=Mm, M_max_num=Mnum, M_mid_num=Mmid, err_support=Mnum / Ms - 1, err_mid=Mmid / Mm - 1,
                note='요소 끝 모멘트 최대 = 받침 모멘트, 경간 가운데 요소 끝 = 가운데 모멘트(요소 길이 36 → 끝점이 가운데에서 반 요소 벗어남)')
R['verify']['ring_3support_roark'] = verify_ring_roark()

# --- 검증 4(크기 가늠): 막힘 강체 상한을 곧은 보로 묶어 본다. 받침 사이 현 길이 L = 2·410·sin60,
#     가운데 점 하중 P(3개 추력) → 단순지지 PL/4(상한 쪽), 양단 고정 PL/8(하한 쪽). 편심(바깥 끝 110) 비틀림은 뺌.
L_ch = 2 * 410.0 * math.sin(pi / 3); Zr = 210.0 * T2 ** 2 / 6
R['verify']['ring2_jam_bracket'] = dict(L_chord=L_ch, sigma_ss=3 * F_CYL * L_ch / 4 / Zr, sigma_ff=3 * F_CYL * L_ch / 8 / Zr,
                                       sigma_grillage_rigid=ring2['샤프트_고정(회전 스프링)']['jam_rigid_supports']['sigma_eq'],
                                       note='그릴리지 값이 비틀림을 더해 단순지지 굽힘 근처인지 본다')

# --- 1회차 결과와 대조(1회차 두께 안 t5 예측 ↔ 2회차 실제 형상)
r1 = json.load(open(OUT_R1, encoding='utf-8')) if os.path.exists(OUT_R1) else None
c2 = ring2['샤프트_고정(회전 스프링)']
cmp = {}
if r1:
    v5 = r1['parts']['P_T01_RING2']['thickness_variants']['t5']
    c1 = r1['parts']['P_T01_RING2']['샤프트_고정(회전 스프링)']
    cmp['ring2_t5_pred_vs_now'] = dict(SF_3g=(v5['SF_3g'], c2['SF_3g']), defl_1g=(v5['defl_1g'], c2['defl_1g_min_mm']), SF_jam=(v5['SF_jam'], c2['jam']['SF']),
                                       SF_jam_rigid=(v5['SF_jam_rigid'], c2['jam_rigid_supports']['SF']), rod_load_1g=(v5['rod_load_1g'], max(r['Fz'] for r in c2['reac_1g'])),
                                       T_DG_need=(v5['T_DG_need_Nm'], variants['t5']['T_DG_need_Nm']))
    cmp['ring2_t3_round1'] = dict(SF_3g=c1['SF_3g'], defl_1g=c1['defl_1g_min_mm'], SF_jam=c1['jam']['SF'], SF_jam_rigid=c1['jam_rigid_supports']['SF'])
    o = r1['parts']
    ex = {
        'SPIDER SF_3g': (o['P_T01_SPIDER_1~3']['SF_3g'], R['parts']['P_T01_SPIDER_1~3']['SF_3g']),
        'SPIDER SF_jam': (o['P_T01_SPIDER_1~3']['SF_jam'], R['parts']['P_T01_SPIDER_1~3']['SF_jam']),
        'SPIDER SF_web': (o['P_T01_SPIDER_1~3']['SF_web'], R['parts']['P_T01_SPIDER_1~3']['SF_web']),
        'SPIDER M_root_1g': (o['P_T01_SPIDER_1~3']['M_root_1g'], R['parts']['P_T01_SPIDER_1~3']['M_root_1g']),
    }
    for lab in hub:
        ex['HUB SF_3g ' + lab] = (o['P_T01_HUB'][lab]['SF_3g'], hub[lab]['SF_3g'])
        ex['HUB SF_jam ' + lab] = (o['P_T01_HUB'][lab]['SF_jam'], hub[lab]['SF_jam'])
        ex['HUB ring2_drop_1g ' + lab] = (o['P_T01_HUB'][lab]['ring2_drop_1g'], hub[lab]['ring2_drop_1g'])
        ex['HUB F_in_bolt_3g ' + lab] = (o['P_T01_HUB'][lab]['normal_3g']['F_in_bolt'], hub[lab]['normal_3g']['F_in_bolt'])
    ex['YPLATE SF_3g'] = (o['P_T01_YPLATE']['SF_3g'], R['parts']['P_T01_YPLATE']['SF_3g'])
    ex['POST SF'] = (o['P_T01_POST']['SF'], R['parts']['P_T01_POST']['SF'])
    ex['RING1 SF_3g'] = (o['P_T01_RING1']['샤프트_고정(회전 스프링)']['SF_3g'], ring1['샤프트_고정(회전 스프링)']['SF_3g'])
    for k in ('DG_thrust_3g_N', 'DG_moment_normal_Nm', 'cyl_rod_load_ring2_3g_N', 'shaft_moment_ring2_3g_Nmm', 'shaft_sigma_ring2_3g'):
        ex['purchased ' + k] = (r1['purchased_loads'][k], R['purchased_loads'][k])
    cmp['existing_parts_round1_vs_now'] = ex
    cmp['strap_round1_vs_now'] = dict(SF_3g=(o['P_T01_RING2_STRAP_1~6']['SF_3g'], R['parts']['P_T01_RING2_STRAP_1~6']['SF_3g']),
                                      SF_jam=(o['P_T01_RING2_STRAP_1~6']['SF_jam'], R['parts']['P_T01_RING2_STRAP_1~6']['SF_jam']))
R['round1_compare'] = cmp

# --- 처짐과 틈(E-03 쪽 확인): 링2를 고친 뒤 처짐이 모델링부가 잰 틈을 먹는지
#     내린 자세(작은 매트 사이클)에는 큰 매트가 없다 → 링2 묶음 무게만. 받침 띠 밑 -72 ↔ 부시 플랜지 윗면 -80, 틈 8
gr_low = ring_model(410.0, 210.0, T2, MAT['A5052'][0], 0.33, K_ROT['RING2']); gr_low.krot = K_ROT['RING2']
d_low, o_low = gr_low.solve(ring_loads(gr_low, [('unif', m_ring2_all * g, 423.9)]))
rl = ring_result(gr_low, d_low, o_low, 310.0, 520.0)
def w_at(d, gr, th_deg, r):
    i = round(th_deg / 360 * gr.N) % gr.N; th = 2 * pi * i / gr.N
    w = d[3 * i]; pt = d[3 * i + 1] * (-math.sin(th)) + d[3 * i + 2] * math.cos(th)
    return w - pt * (r - gr.r_n)
strap_w = {}
for i, th in strap_theta.items():
    sup = min(abs(((th - a + 180) % 360) - 180) for a in (90, 210, 330)) < 5
    strap_w['STRAP_%d' % i] = dict(theta=round(th, 1), at_support=sup, w_1g_r320=w_at(d_low, gr_low, th, 320.0), w_1g_r515=w_at(d_low, gr_low, th, 515.0),
                                   w_3g_min=NG * min(w_at(d_low, gr_low, th, 320.0), w_at(d_low, gr_low, th, 515.0)))
sup_w = [v['w_3g_min'] for v in strap_w.values() if v['at_support']]
R['clearance'] = dict(lowered_ring_only=dict(w_min_1g=rl['w_min'], w_min_3g=NG * rl['w_min'], sigma_3g=NG * rl['sigma_eq'], SF_3g=MAT['A5052'][2] / (NG * rl['sigma_eq'])),
                      strap_deflection=strap_w, gap_strap_bushing_flange=8.0,
                      gap_left_3g=8.0 + (min(sup_w) if sup_w else 0.0),
                      raised_large_mat_w_min_1g=c2['defl_1g_min_mm'], raised_large_mat_w_min_3g=NG * c2['defl_1g_min_mm'],
                      note='처짐은 아래로(−). 받침 자리 띠는 로드·샤프트 바로 위라 처짐이 0에 가깝다. 올린 자세 링2 밑면 −7·띠 −12 아래 가장 가까운 것은 스파이더 웹 윗면 −85(틈 73)')

# --- 링2 로드(구매품 임시 형상 CJ2B16 Ø5) 좌굴 참고: 올린 자세 노출 길이 73, 고정-자유(K=2) 보수
I_rod = pi * 5.0 ** 4 / 64
Pcr = pi ** 2 * MAT['Steel'][0] * I_rod / (2 * 73.0) ** 2
R['rod2_buckling'] = dict(L=73.0, I=I_rod, Pcr_K2=Pcr, P_max=F_CYL, SF=Pcr / F_CYL,
                          note='구매품(M-06 허용치는 구매부). 실제 로드 지름·노출 길이는 STEP 수령 뒤(D-17)')
# --- 링2 올림 여유: 추력 100.5 N ↔ 로드 하중(1 g). 스프링 복귀력(단동 S형)은 카탈로그 확인 전(D-17)
rod1g = max(r['Fz'] for r in c2['reac_1g'])
R['ring2_lift_margin'] = dict(rod_load_1g=rod1g, thrust=F_CYL, ratio_no_spring=F_CYL / rod1g, spring_force_allowed_for_ratio_1p5=F_CYL - 1.5 * rod1g)
# --- 면압(STEP 반경으로 면적)
rd = G['P_T01_DISC']['r_axis'][1]; r1i, r1o = G['P_T01_RING1']['r_axis']; r2i, r2o = G['P_T01_RING2']['r_axis']
A_disc = pi * rd ** 2; A_r1 = pi * (r1o ** 2 - r1i ** 2); A_r2 = pi * (r2o ** 2 - r2i ** 2)
R['contact_pressure'] = dict(A_disc=A_disc, A_ring1=A_r1, A_ring2=A_r2, large_vac_kPa=3.04, large_force_N=3.04e-3 * (A_disc + A_r1),
                             ring2_self_kPa=(RHO_A * 1e6 * g) / 1e3, small_vac_kPa=(34, 58), small_force_N=(34e-3 * A_disc, 58e-3 * A_disc),
                             note='링2 윗면 높이·반경이 1회차와 같아 면압도 같다(파일 면 고체 접촉 0)')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

# 요약 출력
def p(*a):
    print(*a)
p('verify', json.dumps(R['verify'], ensure_ascii=False))
p('step checks fail:', [c for c in checks if not c['ok']])
for k, v in R['parts'].items():
    p('==', k)
    p(json.dumps(v, ensure_ascii=False, default=float)[:1500])
p('purchased', json.dumps(R['purchased_loads'], ensure_ascii=False))
