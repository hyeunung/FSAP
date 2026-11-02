# -*- coding: utf-8 -*-
"""T02 봉제 헤드 묶음 홈 진입 — 강도·처짐 손계산 (해석부, 2026-10-30, 대상 v0.3.0).

해석 못 함 — 환경 없음(자료대기 D-16): 이 컴퓨터에 엔진 해석 환경 engine/fea/.venv가 없다(설치하지 않음).
엔진 솔버(fea.py, gmsh TET10) 대신 표준 라이브러리만으로 손계산(보·비틀림·원형 단면·외팔)을 한다.

입력 형상: 모델링부가 내보낸 해석용 임시 STEP 4개(tools/out/mech_T02/stepout/P_T02_*.step, 세계 좌표,
노루발은 대기 = 내림 + 10). 면 선택·치수는 STEP에서 읽는다(VERTEX_POINT bbox, PLANE 위치·법선,
CYLINDRICAL_SURFACE 반경·축). 옛 케이스 좌표는 쓰지 않는다.
STEP이 없는 것(헤드 임시 형상 STEP대기_SEWHEAD, 받침 형재 STEP대기_HFS8-*)은 모델링부 보고서
mech_T02_model.md 2절(다시 연 저장본 v0.3.0 값)의 자리·부피·질량을 쓴다.

단위: mm, N, MPa, g/kg 표기.  실행: python -B fea/cases/mech_T02_handcalc.py
결과: fea/results/mech_T02_handcalc.json, 로그 fea/results/mech_T02_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T02', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T02_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T02_handcalc_log.txt')
g = 9.81
pi = math.pi
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


# ------------------------------------------------------------------ 재료 (E MPa, nu, 허용 MPa, 출처)
MAT = {
    'Rigid10K': (10000.0, 0.30, 65.0, 'Formlabs Rigid 10K 후경화 인장강도 65 MPa·E 10 GPa(공개 데이터시트 기억값, 사본 없음 — 확인 못 함). 취성이라 인장강도 기준'),
    'S50C':     (205000.0, 0.29, 345.0, '자리값: 엔진 fea.py MAT S45C 항복 345 MPa를 보수로 씀(S50C 담금질 전 값보다 낮음)'),
    'SUS304':   (193000.0, 0.29, 205.0, '엔진 fea.py MAT'),
    'A6N01':    (69000.0, 0.33, 205.0, '엔진 fea.py MAT(MISUMI HFS 형재 A6N01SS-T5)'),
    'Steel':    (206000.0, 0.30, 345.0, '구매품 임시 형상(노루발대) 참고용'),
}

# ------------------------------------------------------------------ 하중 자리값 (자료대기 D-번호)
F_PRESS = 50.0      # N 노루발 누름(D-10, 구상 2 자리값)
F_DRAG = 20.0       # N 바늘·노루발 끌림, 봉제 방향 X(D-10, T01과 같은 값)
F_NEEDLE = 30.0     # N 바늘 관통(D-10, 구상 3 자리값) — 헤드 안 힘이지만 침판 위 매트를 누름
F_TAPE = 10.0       # N 테이프 장력(D-06, 구상 1·3 자리값)
F_MIS = 835.0 * 0.5  # N 오조작: 매트가 진공에서 미끄러지기 전 밀 수 있는 힘 835 N(D-05) × 마찰 0.5(D-04) = 417.5
NG = 3.0            # 자중 × 3 g
SF_REQ, SF_REQ_MIS = 3.0, 2.0      # M-09 기본값(요구서 6-1 비어 있음)
SF_BREAK = 1.2                     # 해석부 지시: SF < 1.2 = 부러짐·영구 변형(동작 문제)
P_SUPPLY = 0.5                     # MPa 요구서 2-4 미정 → 0-6 공급 0.5 MPa (T02에는 공압 실린더 없음)

# 모델 질량(g, mach_props.json·모델 보고서 2절, E-09 "질량 판정은 모델 질량을 그대로 쓴다")
MASS = {'STEP대기_SEWHEAD': 170368.2, 'P_T02_PLATE': 102.2, 'P_T02_BINDER': 51.2, 'P_T02_FOOT': 26.2,
        'STEP대기_SEWHEAD_PRESSERBAR': 95.5, 'STEP대기_SEWHEAD_NEEDLEBAR': 51.8, 'STEP대기_NEEDLE': 0.9,
        'P_T02_HEADPLATE': 2283.8}


# ================================================================== STEP 읽기
def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ent = {}
    for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
        ent[int(m.group(1))] = m.group(2).replace('\n', '')

    def pt(i):
        v = re.search(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", ent[i])
        return tuple(float(x) for x in v.group(1).split(','))

    def dirn(i):
        v = re.search(r"DIRECTION\('[^']*',\(([^)]*)\)\)", ent[i])
        return tuple(float(x) for x in v.group(1).split(','))

    def ax(i):
        a = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ent[i])
        return pt(int(a.group(1))), dirn(int(a.group(2)))

    verts, planes, cyls = [], [], []
    for i, s in ent.items():
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
        m = re.match(r"PLANE\('[^']*',#(\d+)\)", s)
        if m:
            loc, n = ax(int(m.group(1)))
            planes.append(dict(loc=[round(c, 3) for c in loc], normal=[round(c, 3) for c in n]))
        m = re.match(r"CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)", s)
        if m:
            loc, n = ax(int(m.group(1)))
            cyls.append(dict(r=round(float(m.group(2)), 3), axis_xy=[round(loc[0], 3), round(loc[1], 3)],
                             dir=[round(c, 3) for c in n]))
    xs, ys, zs = zip(*verts)

    def lv(k):
        return sorted(set(round(p['loc'][k], 2) for p in planes if abs(abs(p['normal'][k]) - 1) < 1e-6))
    return dict(n_vert=len(verts),
                bbox=[[round(min(xs), 3), round(max(xs), 3)], [round(min(ys), 3), round(max(ys), 3)], [round(min(zs), 3), round(max(zs), 3)]],
                x_planes=lv(0), y_planes=lv(1), z_planes=lv(2), cylinders=cyls)


G = {}
for f in sorted(os.listdir(STEPDIR)):
    if f.endswith('.step'):
        G[f[:-5]] = read_step(os.path.join(STEPDIR, f))

checks = []


def chk(part, what, got, want, tol=0.06):
    ok = abs(got - want) <= tol
    checks.append(dict(part=part, what=what, step=got, used=want, ok=ok))
    return got


def cyl(part, r):
    for c in G[part]['cylinders']:
        if abs(c['r'] - r) < 0.01:
            return c
    raise KeyError((part, r))


# --- 노루발 (STEP은 대기 = 내림 + 10)
F = G['P_T02_FOOT']
chk('P_T02_FOOT', 'X 폭 bbox', F['bbox'][0][1] - F['bbox'][0][0], 18.0)
chk('P_T02_FOOT', 'Y 뒷면(자루 뒤)', F['y_planes'][0], -26.0)
chk('P_T02_FOOT', 'Y 자루 앞면', F['y_planes'][1], -10.0)
chk('P_T02_FOOT', 'Y 바닥 앞끝', F['y_planes'][-1], 18.5)
chk('P_T02_FOOT', 'Z 노즈 밑면(대기)', F['z_planes'][0], 16.5)
chk('P_T02_FOOT', 'Z 바닥 밑면(대기)', F['z_planes'][1], 21.05)
chk('P_T02_FOOT', 'Z 바닥 윗면(대기)', F['z_planes'][2], 31.05)
chk('P_T02_FOOT', 'Z 자루 윗면(대기)', F['z_planes'][-1], 55.0)
nose_f = cyl('P_T02_FOOT', 8.5)
chk('P_T02_FOOT', '위 노즈 축 Y', nose_f['axis_xy'][1], 10.0)
hole_f = cyl('P_T02_FOOT', 1.3)
chk('P_T02_FOOT', '바늘 구멍 축 Y', hole_f['axis_xy'][1], 0.0)
DZ = -10.0                          # 대기 → 내림(J_PRESSER 0)
f_b = F['x_planes'][-1] - F['x_planes'][0]          # 18 (X)
f_shank_y = F['y_planes'][1] - F['y_planes'][0]     # 16 (Y)
z_nose_bot, z_bot_bot, z_bot_top, z_top = [F['z_planes'][i] + DZ for i in (0, 1, 2, -1)]
t_bot = z_bot_top - z_bot_bot                        # 10
z_nose_c = (z_nose_bot + z_bot_bot) / 2              # 노즈 노출 가운데(내림) 8.775
y_nose = nose_f['axis_xy'][1]; r_nose = nose_f['r']
y_shank_ax = (F['y_planes'][0] + F['y_planes'][1]) / 2   # −18 (노루발대 축과 같음)
y_shank_front = F['y_planes'][1]

# --- 침판
P = G['P_T02_PLATE']
chk('P_T02_PLATE', 'X 폭', P['bbox'][0][1] - P['bbox'][0][0], 80.0)
chk('P_T02_PLATE', 'Y 폭', P['bbox'][1][1] - P['bbox'][1][0], 50.0)
chk('P_T02_PLATE', 'Z 판 밑면', P['z_planes'][0], -4.05)
chk('P_T02_PLATE', 'Z 판 윗면', P['z_planes'][1], -1.05)
chk('P_T02_PLATE', 'Z 노즈 윗면', P['z_planes'][-1], 3.5)
nose_p = cyl('P_T02_PLATE', 8.5)
chk('P_T02_PLATE', '아래 노즈 축 Y', nose_p['axis_xy'][1], 10.0)
hole_p = cyl('P_T02_PLATE', 1.0)
chk('P_T02_PLATE', '바늘 구멍 축 Y', hole_p['axis_xy'][1], 0.0)
p_top, p_nose_top = P['z_planes'][1], P['z_planes'][-1]
p_nose_c = (p_top + p_nose_top) / 2

# --- 바인더
B = G['P_T02_BINDER']
chk('P_T02_BINDER', 'X', B['bbox'][0][0], -34.0); chk('P_T02_BINDER', 'X 끝', B['bbox'][0][1], -10.0)
chk('P_T02_BINDER', 'Y', B['bbox'][1][0], 2.0); chk('P_T02_BINDER', 'Y 끝', B['bbox'][1][1], 40.0)
chk('P_T02_BINDER', 'Z 밑면', B['z_planes'][0], 26.0); chk('P_T02_BINDER', 'Z 윗면(머리 밑면에 닿음)', B['z_planes'][-1], 60.0)
b_x = B['bbox'][0][1] - B['bbox'][0][0]; b_y = B['bbox'][1][1] - B['bbox'][1][0]; b_h = B['bbox'][2][1] - B['bbox'][2][0]

# --- 받침판
H = G['P_T02_HEADPLATE']
chk('P_T02_HEADPLATE', 'X', H['bbox'][0][0], -100.0); chk('P_T02_HEADPLATE', 'X 끝', H['bbox'][0][1], 100.0)
chk('P_T02_HEADPLATE', 'Y 앞', H['bbox'][1][0], 620.0); chk('P_T02_HEADPLATE', 'Y 뒤', H['bbox'][1][1], 860.0)
chk('P_T02_HEADPLATE', 'Z 밑면(형재 윗면)', H['z_planes'][0], -140.0); chk('P_T02_HEADPLATE', 'Z 윗면(헤드 기둥 밑면)', H['z_planes'][-1], -134.0)
h_t = H['z_planes'][-1] - H['z_planes'][0]
h_w = H['bbox'][0][1] - H['bbox'][0][0]
h_y0 = H['bbox'][1][0]

# 받침 형재 자리(모델 보고서 2절, STEP 없음): X ±(50~90) · Y 700~780 · Z −600~−140, 연결 Z −680~−600
POST = dict(x=(50.0, 90.0), y=(700.0, 780.0), z=(-600.0, -140.0))
POST_L = POST['z'][1] - POST['z'][0]          # 460
POST_XC = sum(POST['x']) / 2                  # 70
POST_YC = sum(POST['y']) / 2                  # 740
I_POST = 80.0e4      # mm4 HFS8-4080 강축(Y 80) — 카탈로그 확인 못 함(구상 2 자리값, D-27)
I_POST_WEAK = 20.0e4  # mm4 약축 자리값 = 강축 × (40/80)^2 (D-27)
GAP_BED_RING = 1.5   # 헤드 베드 밑면 −59 ↔ 링1 내림 윗면 −60.5 (선정 6-1)

# ================================================================== 헤드 질량·무게중심 (모델 보고서 2절 상자)
boxes = [  # (이름, x0,x1,y0,y1,z0,z1, 부호)
    ('베드', -50, 50, -30, 660, -59, -1.05, +1),
    ('기둥', -75, 75, 620, 860, -134, 250, +1),
    ('윗팔', -35, 35, 30, 630, 100, 180, +1),
    ('머리', -40, 40, -40, 40, 60, 200, +1),
    ('베드∩기둥', -50, 50, 620, 660, -59, -1.05, -1),
    ('윗팔∩기둥', -35, 35, 620, 630, 100, 180, -1),
    ('윗팔∩머리', -35, 35, 30, 40, 100, 180, -1),
    ('침판 홈', -40.1, 40.1, -25.1, 25.1, -4.05, -1.05, -1),
]
V = Sy = Sz = 0.0
for n, x0, x1, y0, y1, z0, z1, s in boxes:
    v = (x1 - x0) * (y1 - y0) * (z1 - z0) * s
    V += v; Sy += v * (y0 + y1) / 2; Sz += v * (z0 + z1) / 2
holes = [(1.5, 0, 0, -4.05, -1.05 - 0 + 0), (4.2, 0, 0, 60, 200), (5.2, 0, -18, 60, 200)]
# 훅 구멍 r1.5 Z −15~−4 중 베드 안 부분은 −15~−4.05(침판 홈 밑) → 길이 10.95
hole_list = [(1.5, 0.0, -9.525, 10.95), (4.2, 0.0, 130.0, 140.0), (5.2, -18.0, 130.0, 140.0)]
for r, yc, zc, L in hole_list:
    v = pi * r * r * L
    V -= v; Sy -= v * yc; Sz -= v * zc
V_CAD = 21702954.8
ycg_head = Sy / V; zcg_head = Sz / V
chk('STEP대기_SEWHEAD', '부피(상자 계산 / CAD)', V, V_CAD, tol=50.0)
# 묶음 전체 무게중심(작은 부품은 자리 중심, 노루발 대기 자세)
parts_cg = [('STEP대기_SEWHEAD', ycg_head), ('P_T02_PLATE', 0.0), ('P_T02_BINDER', 21.0), ('P_T02_FOOT', -6.0),
            ('STEP대기_SEWHEAD_PRESSERBAR', -18.0), ('STEP대기_SEWHEAD_NEEDLEBAR', 0.0), ('STEP대기_NEEDLE', 0.0)]
m_head = sum(MASS[k] for k, _ in parts_cg) / 1000.0          # kg
ycg = sum(MASS[k] * y for k, y in parts_cg) / (m_head * 1000.0)
W1 = m_head * g
log('헤드 묶음 질량 %.2f kg, 무게중심 Y %.1f (헤드 임시 형상만 Y %.1f, Z %.1f), 1 g %.1f N' % (m_head, ycg, ycg_head, zcg_head, W1))


# ================================================================== 도움 함수
def alpha_rect(a, b):
    """직사각 비틀림 τmax = T/(α a b²), a ≥ b"""
    a, b = max(a, b), min(a, b); r = a / b
    tab = [(1.0, .208), (1.2, .219), (1.5, .231), (2.0, .246), (2.5, .258), (3.0, .267), (4.0, .282), (5.0, .291), (10.0, .312), (1e9, .333)]
    for (r0, a0), (r1, a1) in zip(tab, tab[1:]):
        if r <= r1:
            return a0 + (a1 - a0) * (r - r0) / (r1 - r0), a, b
    return .333, a, b


def beta_rect(a, b):
    a, b = max(a, b), min(a, b); r = a / b
    tab = [(1.0, .141), (1.2, .166), (1.5, .196), (2.0, .229), (2.5, .249), (3.0, .263), (4.0, .281), (5.0, .291), (10.0, .312), (1e9, .333)]
    for (r0, b0), (r1, b1) in zip(tab, tab[1:]):
        if r <= r1:
            return (b0 + (b1 - b0) * (r - r0) / (r1 - r0)) * a * b ** 3
    return .333 * a * b ** 3


def tau_rect(T, a, b):
    al, A, Bb = alpha_rect(a, b)
    return T / (al * A * Bb * Bb)


def vm(s, t):
    return math.sqrt(s * s + 3 * t * t)


R = {}       # 결과
over = []    # 과사양 노트
det = []     # 디테일


def res(key, part, mat, case, sig, need, extra=None):
    allow = MAT[mat][2]
    sf = allow / sig if sig > 0 else float('inf')
    d = dict(part=part, mat=mat, case=case, sigma=round(sig, 3), sf=round(sf, 2) if sf < 1e6 else 'inf', need=need,
             verdict=('동작(SF<1.2)' if sf < SF_BREAK else ('기준 미달(디테일)' if sf < need else '통과')))
    if extra:
        d.update(extra)
    R[key] = d
    log('%-34s %-10s %-44s σ %8.3f MPa  SF %8.2f  필요 %.0f  %s' % (key, mat, case, sig, sf, need, d['verdict']))
    return sf


# ================================================================== 1. 노루발 P_T02_FOOT (Rigid 10K)
E_f = MAT['Rigid10K'][0]; G_f = E_f / (2 * (1 + MAT['Rigid10K'][1]))
w_self_f = MASS['P_T02_FOOT'] / 1000 * g * NG
L_sh = z_top - z_bot_top                    # 자루 길이 23.95(내림 Z 21.05~45)
Zs_x = f_shank_y * f_b ** 2 / 6             # X 힘 → 자루 굽힘(깊이 X 18) 864
Zs_y = f_b * f_shank_y ** 2 / 6             # Y 힘 → 깊이 Y 16, 768
A_sh = f_b * f_shank_y
# 1-1 운전: 누름 50 N(위로, 날개 하중 중심 Y −4.5) + 끌림 20 N(+X, 바닥 밑면 Z 11.05) + 자중 3 g
y_wing = -4.5
M_bot_press = F_PRESS * (y_wing - y_shank_front)          # 바닥 외팔(자루 앞면 Y −10에서)
s_bot_press = M_bot_press / (f_b * t_bot ** 2 / 6)
M_sh_drag = F_DRAG * (z_top - z_bot_bot)                  # 자루 윗면 물림 Z 45에서
T_sh_drag = F_DRAG * (y_wing - y_shank_ax)
M_sh_press = F_PRESS * (y_wing - y_shank_ax)             # 누름이 자루 축에서 Y로 떨어져 생기는 굽힘(X축)
s_sh_op = (F_PRESS + w_self_f) / A_sh + M_sh_drag / Zs_x + M_sh_press / Zs_y
t_sh_op = tau_rect(T_sh_drag, f_b, f_shank_y)
res('FOOT_op_shank', 'P_T02_FOOT', 'Rigid10K', '운전: 누름 50 + 끌림 20 N + 3 g, 자루 윗면(Z 45)', vm(s_sh_op, t_sh_op), SF_REQ)
res('FOOT_op_bottom', 'P_T02_FOOT', 'Rigid10K', '운전: 누름 50 N, 바닥 외팔 뿌리(Y −10)', s_bot_press, SF_REQ)
# 1-2 오조작 X: 418 N이 위 노즈 가운데(Y 10, Z 8.775)에 X 방향
M1 = F_MIS * (z_top - z_nose_c); T1 = F_MIS * (y_nose - y_shank_ax)
s1 = M1 / Zs_x; t1 = tau_rect(T1, f_b, f_shank_y)
sf_foot_mis = res('FOOT_misX_shank_top', 'P_T02_FOOT', 'Rigid10K', '오조작 X 418 N, 자루 윗면(Z 45) 굽힘+비틀림', vm(s1, t1), SF_REQ_MIS,
                  dict(M=round(M1), T=round(T1), sigma_b=round(s1, 2), tau=round(t1, 2)))
# 자루 밑(L자 안쪽 모서리 Z 21.05, Y −10): 굽힘 작고 비틀림 같음, 날카로운 안쪽 모서리 Kt 2.5(보수 자리값)
KT = 2.5
M1b = F_MIS * (z_bot_top - z_nose_c)
res('FOOT_misX_inner_corner', 'P_T02_FOOT', 'Rigid10K', '오조작 X, L자 안쪽 모서리(Z 21.05) Kt 2.5', vm(KT * M1b / Zs_x, t1), SF_REQ_MIS)
M1c = F_MIS * (y_nose - y_shank_front); T1c = F_MIS * ((z_bot_bot + z_bot_top) / 2 - z_nose_c)
res('FOOT_misX_bottom', 'P_T02_FOOT', 'Rigid10K', '오조작 X, 바닥 면 안 굽힘(Y −10) + 비틀림', vm(M1c / (t_bot * f_b ** 2 / 6), tau_rect(T1c, f_b, t_bot)), SF_REQ_MIS)
M1n = F_MIS * (z_bot_bot - z_nose_c); Zn = pi * r_nose ** 3 / 4; An = pi * r_nose ** 2
res('FOOT_misX_nose_root', 'P_T02_FOOT', 'Rigid10K', '오조작, 위 노즈 뿌리(Z 11.05) r8.5', vm(M1n / Zn, 4 / 3 * F_MIS / An), SF_REQ_MIS)
# 1-3 오조작 Y: 418 N이 노즈에 Y 방향(자루 축과 같은 X → 비틀림 없음)
M2 = F_MIS * (z_top - z_nose_c)
res('FOOT_misY_shank_top', 'P_T02_FOOT', 'Rigid10K', '오조작 Y 418 N, 자루 윗면(Z 45) 굽힘', M2 / Zs_y, SF_REQ_MIS)
M2b = F_MIS * ((z_bot_bot + z_bot_top) / 2 - z_nose_c)
res('FOOT_misY_bottom', 'P_T02_FOOT', 'Rigid10K', '오조작 Y, 바닥(Y −10) 축력 + 굽힘', F_MIS / (f_b * t_bot) + M2b / (f_b * t_bot ** 2 / 6), SF_REQ_MIS)

# 1-4 노루발 처짐 → 바늘 구멍 자리 이동(내림: 바늘 r0.6 ↔ 구멍 r1.3 틈 0.7)
def foot_hole_disp(Fx, Fy):
    e = z_bot_top - z_nose_c                       # 자루 밑에서 하중점까지 12.225
    dz_hole = z_bot_top - (z_bot_bot + z_bot_top) / 2   # 자루 밑 → 구멍(바닥 가운데) 5
    out = {}
    for comp, Fc, I in (('x', Fx, f_shank_y * f_b ** 3 / 12), ('y', Fy, f_b * f_shank_y ** 3 / 12)):
        d = Fc * L_sh ** 3 / (3 * E_f * I) + Fc * e * L_sh ** 2 / (2 * E_f * I)
        th = Fc * L_sh ** 2 / (2 * E_f * I) + Fc * e * L_sh / (E_f * I)
        out[comp] = d + th * dz_hole
    J = beta_rect(f_b, f_shank_y)
    phi = Fx * (y_nose - y_shank_ax) * L_sh / (G_f * J)
    out['x'] += phi * (0.0 - y_shank_ax)           # 구멍(Y 0)이 자루 축(Y −18)에서 18
    # 노루발대 Ø10 Steel, 헤드 머리 밑면(Z 60)에서 자루 윗면(Z 45)까지 15 외팔 + 비틀림
    Lb = 60.0 - z_top; Ib = pi * 10 ** 4 / 64; Jb = pi * 10 ** 4 / 32; Es = MAT['Steel'][0]; Gs = Es / 2.6
    arm = z_top - (z_bot_bot + z_bot_top) / 2
    for comp, Fc in (('x', Fx), ('y', Fy)):
        Mb = Fc * (z_top - z_nose_c)
        d = Fc * Lb ** 3 / (3 * Es * Ib) + Mb * Lb ** 2 / (2 * Es * Ib)
        th = Fc * Lb ** 2 / (2 * Es * Ib) + Mb * Lb / (Es * Ib)
        out[comp] += d + th * arm
    out['x'] += Fx * (y_nose - y_shank_ax) * Lb / (Gs * Jb) * 18.0
    return out


dh_op = foot_hole_disp(F_DRAG, 0.0)
dh_misx = foot_hole_disp(F_MIS, 0.0)
dh_misy = foot_hole_disp(0.0, F_MIS)
GAP_NEEDLE_FOOT = hole_f['r'] - 0.6
log('노루발 구멍 이동: 운전 끌림 %.4f, 오조작 X %.3f, 오조작 Y %.3f mm (틈 %.2f)' % (dh_op['x'], dh_misx['x'], dh_misy['y'], GAP_NEEDLE_FOOT))
over_foot = dict(part='P_T02_FOOT', governing='오조작 X SF %.2f (필요 2)' % sf_foot_mis, over=(sf_foot_mis >= 3 * SF_REQ_MIS))

# ================================================================== 2. 침판 P_T02_PLATE (S50C)
Zp = pi * nose_p['r'] ** 3 / 4; Ap = pi * nose_p['r'] ** 2
Mp_mis = F_MIS * (p_nose_c - p_top)
sf_plate_mis = res('PLATE_mis_nose_root', 'P_T02_PLATE', 'S50C', '오조작 418 N 아래 노즈 가운데, 뿌리(Z −1.05)', vm(Mp_mis / Zp, 4 / 3 * F_MIS / Ap), SF_REQ_MIS)
Mp_op = F_DRAG * (p_nose_c - p_top)
s_comp = (F_PRESS + F_NEEDLE) / Ap
res('PLATE_op_nose', 'P_T02_PLATE', 'S50C', '운전: 끌림 20 N + 누름 50 + 관통 30 N 압축', vm(Mp_op / Zp + s_comp, 4 / 3 * F_DRAG / Ap), SF_REQ)
bear_wall = F_MIS / ((P['z_planes'][1] - P['z_planes'][0]) * (P['bbox'][1][1] - P['bbox'][1][0]))
res('PLATE_mis_pocket_bearing', 'P_T02_PLATE', 'S50C', '오조작 418 N 헤드 홈 벽 지압(t3 × 50)', bear_wall, SF_REQ_MIS)
over.append(dict(part='P_T02_PLATE', sf=round(sf_plate_mis, 1), need=SF_REQ_MIS,
                 note='과사양(필요 2의 3배 이상). 크기는 홈 띠 빈 원(노즈 r8.5)과 헤드 침판 홈(t3)이 정해 줄일 두께가 없다. 재질 S50C는 바늘 타격·마모 때문(강도 아님) — 강도만 보면 SS400·SUS304로도 SF > 50. 가격 미확인'))

# ================================================================== 3. 바인더 P_T02_BINDER (Rigid 10K, 외형 상자)
Zb = b_y * b_x ** 2 / 6; Ab = b_x * b_y
w_self_b = MASS['P_T02_BINDER'] / 1000 * g * NG
Mb_op = F_TAPE * b_h
res('BINDER_op_root', 'P_T02_BINDER', 'Rigid10K', '운전: 테이프 장력 10 N 출구(Z 26) +X, 윗면 뿌리', Mb_op / Zb + w_self_b / Ab, SF_REQ)
Mb_mis = F_MIS * b_h
sf_bind_mis = res('BINDER_mis_root', 'P_T02_BINDER', 'Rigid10K', '오조작: 테이프 걸림 418 N 출구, 윗면 뿌리', vm(Mb_mis / Zb, 1.5 * F_MIS / Ab), SF_REQ_MIS)
# 고정(디테일링 CB5, 렌치 길 X −30~−14): X −30 볼트 인장, X −10 모서리 지렛점
T_bolt_binder = Mb_mis / (B['bbox'][0][1] - (-30.0))
Tb_op = Mb_op / (B['bbox'][0][1] - (-30.0))
log('바인더 고정 볼트(X −30 하나 가정) 인장: 운전 %.1f N, 오조작 %.0f N' % (Tb_op, T_bolt_binder))
over.append(dict(part='P_T02_BINDER', sf=round(sf_bind_mis, 1), need=SF_REQ_MIS,
                 note='외형 상자 값이라 과사양 판정 의미 없음: 속 테이프 통로(요구서 7, 구매 여부 U-T02-2)가 없다. 통로를 그리면 벽 두께로 다시 푼다. 줄일 두께 없음(크기는 테이프 길이 정함)'))

# ================================================================== 4. 받침판 P_T02_HEADPLATE (SUS304 t6) + 받침 형재
W3 = W1 * NG
lever_front = POST['y'][0] - ycg        # 지렛점(형재 앞면 Y 700)에서 무게중심까지
M_tip1 = W1 * lever_front; M_tip3 = W3 * lever_front
log('무게중심이 형재 앞면 Y 700보다 %.1f, 판 앞끝 Y 620보다 %.1f 앞(−Y)' % (lever_front, h_y0 - ycg))
# 4-1 모델대로(속 찬 기둥이 형재 위 겹친 자리 |X| 50~75 · Y 700~780에서 판을 누름)
ov_w = 75.0 - POST['x'][0]; ov_l = POST['y'][1] - POST['y'][0]
A_ov = 2 * ov_w * ov_l; S_ov = A_ov * ov_l / 6
M_c3 = W3 * (POST_YC - ycg)
s_comp_max = W3 / A_ov + M_c3 / S_ov
s_tens = W3 / A_ov - M_c3 / S_ov
res('HEADPLATE_asmodel_3g', 'P_T02_HEADPLATE', 'SUS304', '모델대로 3 g: 겹친 자리 지압(앞 끝 최대)', s_comp_max, SF_REQ,
    dict(rear_stress=round(s_tens, 2), note='뒤쪽이 인장(−) → 눌러 잡는 볼트 없이는 앞으로 넘어간다'))
# 눌러 잡는 힘(형재 앞면 Y 700 지렛점, 형재 뒤쪽 Y 770 볼트 가정)
y_bolt = 770.0
T_hold1 = M_tip1 / (y_bolt - POST['y'][0]); T_hold3 = M_tip3 / (y_bolt - POST['y'][0])
log('눌러 잡는 힘(형재 2개 합, 볼트 Y 770): 1 g %.0f N, 3 g %.0f N / 형재 하나 %.0f / %.0f N' % (T_hold1, T_hold3, T_hold1 / 2, T_hold3 / 2))
# 4-2 경계: 실제 헤드 밑면이 가장자리 발(앞 Y 625, 뒤 Y 855 볼트)이면 판이 형재 앞 75 mm 외팔로 받는다
y_ff, y_rf = 625.0, 855.0
R_ff1 = W1 * (y_rf - ycg) / (y_rf - y_ff); R_ff3 = R_ff1 * NG
Zh = h_w * h_t ** 2 / 6
Mo1 = R_ff1 * (POST['y'][0] - y_ff); Mo3 = Mo1 * NG
sf_hp_h1 = res('HEADPLATE_footed_1g', 'P_T02_HEADPLATE', 'SUS304', '경계(가장자리 발 헤드) 1 g, 판 앞 외팔 Y 700, b 200', Mo1 / Zh, SF_REQ)
sf_hp_h3 = res('HEADPLATE_footed_3g', 'P_T02_HEADPLATE', 'SUS304', '경계(가장자리 발 헤드) 3 g, 판 앞 외팔 Y 700, b 200', Mo3 / Zh, SF_REQ)
t_need = h_t * math.sqrt(SF_REQ / sf_hp_h3)
log('경계 경우 3 g에서 SF 3에 필요한 판 두께 %.1f mm' % t_need)

# 4-3 받침 형재(구매품 임시 형상, 참고): 기둥 굽힘·처짐, 비틀림(끌림) 흔들림
E_a = MAT['A6N01'][0]
M_post1 = M_c3 / NG / 2          # 형재 하나 1 g (형재 가운데 Y 740 기준)
M_post3 = M_c3 / 2
s_post3 = M_post3 * 40.0 / I_POST
res('POST_3g_ref', 'STEP대기_HFS8-4080-460_P1/P2', 'A6N01', '참고 3 g: 기둥 굽힘(I 80 cm4 자리값)', s_post3, SF_REQ)
th1 = M_post1 * POST_L / (E_a * I_POST)
d_top1 = M_post1 * POST_L ** 2 / (2 * E_a * I_POST)
sag_needle1 = th1 * (POST_YC - 0.0)
sag_bedtip1 = th1 * (POST_YC - (-30.0))
log('받침 1 g: 기울기 %.2e rad, 바늘점 내려감 %.3f, 베드 끝(Y −30) %.3f, 기둥 끝 수평 %.3f mm (베드–링1 틈 %.1f)' % (th1, sag_needle1, sag_bedtip1, d_top1, GAP_BED_RING))
# 끌림 20 N(+X, 바늘점 Z 0)이 받침에 비틀림: 두 기둥(X ±70)이 반대로 Y 굽힘
k_post = 3 * E_a * I_POST / POST_L ** 3
k_theta = 2 * k_post * POST_XC ** 2
arm_n = POST_YC - 0.0
k_needle = k_theta / arm_n ** 2
sway_op = F_DRAG / k_needle
sway_mis = F_MIS / k_needle
# 오조작 비틀림 짝힘 → 기둥 강축 굽힘
Fc_mis = F_MIS * arm_n / (2 * POST_XC)
s_post_mis = Fc_mis * POST_L * 40.0 / I_POST
res('POST_mis_torsion_ref', 'STEP대기_HFS8-4080-460_P1/P2', 'A6N01', '참고 오조작 418 N X: 비틀림 짝힘 굽힘', s_post_mis, SF_REQ_MIS)
log('받침 비틀림 강성(바늘점 X) %.1f N/mm → 끌림 20 N %.3f mm, 오조작 418 N %.1f mm' % (k_needle, sway_op, sway_mis))
# 받침 브래킷(기둥–연결 HBLFSN8, D-31)이 받는 모멘트
M_br1 = M_post1 / 1000; M_br3 = M_post3 / 1000

# ================================================================== 5. 처짐과 틈
gaps = [
    dict(where='바늘 r0.6 ↔ 노루발 구멍 r1.3(내림)', cad_gap=round(GAP_NEEDLE_FOOT, 2), load='운전 끌림 20 N', disp=round(dh_op['x'], 4), left=round(GAP_NEEDLE_FOOT - dh_op['x'], 3)),
    dict(where='〃', cad_gap=round(GAP_NEEDLE_FOOT, 2), load='오조작 X 418 N', disp=round(dh_misx['x'], 3), left=round(GAP_NEEDLE_FOOT - dh_misx['x'], 3)),
    dict(where='〃', cad_gap=round(GAP_NEEDLE_FOOT, 2), load='오조작 Y 418 N', disp=round(dh_misy['y'], 3), left=round(GAP_NEEDLE_FOOT - dh_misy['y'], 3)),
    dict(where='헤드 베드 밑면 −59 ↔ 링1 내림 윗면 −60.5(베드 끝 Y −30)', cad_gap=GAP_BED_RING, load='헤드 자중 1 g(받침 형재 굽힘만)', disp=round(sag_bedtip1, 3), left=round(GAP_BED_RING - sag_bedtip1, 3)),
    dict(where='〃', cad_gap=GAP_BED_RING, load='헤드 자중 3 g(강도용 계수, 실제 상태 아님)', disp=round(sag_bedtip1 * NG, 3), left=round(GAP_BED_RING - sag_bedtip1 * NG, 3)),
    dict(where='바늘점 봉제 방향(X) 흔들림 — 땀 위치(정밀 체인, 6-2 D-08)', cad_gap=None, load='운전 끌림 20 N', disp=round(sway_op, 3), left=None),
]
for gp in gaps:
    log('틈', gp)

out = dict(
    date='2026-10-30', target='3D_Modeling/FSAP_v0.3.0.sc', method='손계산(해석 못 함 — 환경 없음, D-16), 교차 검증 없음',
    step={k: v for k, v in G.items()}, step_checks=checks, step_checks_fail=sum(1 for c in checks if not c['ok']),
    head=dict(mass_kg=round(m_head, 3), ycg=round(ycg, 1), ycg_head_only=round(ycg_head, 1), zcg_head_only=round(zcg_head, 1), W1=round(W1, 1), W3=round(W3, 1),
              volume_boxes=round(V, 1), volume_cad=V_CAD),
    loads=dict(F_PRESS=F_PRESS, F_DRAG=F_DRAG, F_NEEDLE=F_NEEDLE, F_TAPE=F_TAPE, F_MIS=F_MIS, NG=NG, P_SUPPLY=P_SUPPLY,
               actuator='T02에 공압 실린더 없음(노루발 들기·누름은 헤드 안, D-10)'),
    criteria=dict(SF_REQ=SF_REQ, SF_REQ_MIS=SF_REQ_MIS, SF_BREAK=SF_BREAK, over=3.0),
    materials={k: dict(E=v[0], nu=v[1], allow=v[2], src=v[3]) for k, v in MAT.items()},
    results=R, overspec=over, foot_overspec=over_foot,
    foot_hole_disp=dict(op=dh_op, misX=dh_misx, misY=dh_misy),
    binder_bolt=dict(op=round(Tb_op, 1), mis=round(T_bolt_binder, 1)),
    stand=dict(lever_front=round(lever_front, 1), ahead_of_plate=round(h_y0 - ycg, 1), M_tip_1g_Nm=round(M_tip1 / 1000, 1), M_tip_3g_Nm=round(M_tip3 / 1000, 1),
               hold_down_total_1g=round(T_hold1), hold_down_total_3g=round(T_hold3), asmodel_rear_stress_3g=round(s_tens, 2),
               footed_R_front_1g=round(R_ff1), plate_t_need_footed_3g=round(t_need, 1),
               bracket_moment_per_post_1g_Nm=round(M_br1, 1), bracket_moment_per_post_3g_Nm=round(M_br3, 1),
               post_tilt_1g=th1, sag_needle_1g=round(sag_needle1, 3), sag_bedtip_1g=round(sag_bedtip1, 3), post_top_shift_1g=round(d_top1, 3),
               k_needle_X=round(k_needle, 2), sway_drag=round(sway_op, 3), sway_mis=round(sway_mis, 2), I_POST=I_POST),
    gaps=gaps,
)
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
log('STEP 확인 실패 %d / %d' % (out['step_checks_fail'], len(checks)))
log('저장', OUT)
