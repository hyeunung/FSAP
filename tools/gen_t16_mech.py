# T16(모델링부) 생성기: v0.8.6 -> v0.9.0 — X·Y 이송 배관·케이블 캐리어(분기·밸브 자리)
# 지시서: docs/reports/mechanism/mech_T16_select.md 5절. 좌표는 세계 대기(J_MAT_X 0, J_MAT_Y -700, 회전 0, 링 0), mm.
# MAT_Y 부품의 로컬 L 은 세계 Y = L - 700. 다르게 정한 곳은 docs/reports/mechanism/mech_T16_model.md 'DEV' 표.
# 쓰는 법: python -B tools/gen_t16_mech.py -> tools/out/mech_T16/model/stage_<a..h>.json (MCP batch 로 차례로 보냄)
#          edit.json = stage 를 이어 붙인 것(tools/out/mech_T16/edit.json)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T16', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
STAGES = {}
S = None
VER = "FSAP_v0.9.0"


def stage(n):
    global S
    S = STAGES.setdefault(n, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 4)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def M(lx, ly, t):
    lz = cross(lx, ly)
    return [lx[0], ly[0], lz[0], t[0], lx[1], ly[1], lz[1], t[1], lx[2], ly[2], lz[2], t[2]]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (1, 0, 0)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def zc(d, x, y, z0, z1, **k):           # Z 축 원통 z0~z1
    cyl(d, (x, y, min(z0, z1)), 'Z', abs(z1 - z0), **k)


def box(bb, name=None, op=None, targets=None):
    p = {"length": r6(bb[1] - bb[0]), "width": r6(bb[3] - bb[2]), "height": r6(bb[5] - bb[4]),
         "center": [r6((bb[0] + bb[1]) / 2), r6((bb[2] + bb[3]) / 2), r6((bb[4] + bb[5]) / 2)]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
        p["operation"] = "new"
    C("solid.box", p)


def comp(nm, par, pn, bom, desc):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})
    META.append({"component": nm, "part_number": pn, "bom_type": bom, "description": desc})


def meta_flush():
    for m in META:
        C("component.metadata.set", m)
    del META[:]


META = []
MAT = {}            # body -> material
STEELB = []         # 실물 STEP 볼트·너트
WAITB = []          # STEP대기 볼트·너트


def mat(bodies, m):
    for b in bodies:
        MAT[b] = m


def ins(step, name, mat_, rename, desc):
    C("file.insert_step", {"path": SP + step + '/' + step + '.stp', "name": name, "matrix": [r6(v) for v in mat_]})
    for old, new in rename.items():
        C("body.rename", {"body": old, "name": new})
    C("component.metadata.set", {"component": name, "part_number": step, "bom_type": "purchased", "description": desc})


def bolt(step, name, seat, d, desc):
    # CB STEP: 머리 X -k~0, 몸통 +X. seat = 머리 자리면 점, d = 넣는 방향
    ins(step, name, M(d, perp(d), seat), {"Cut-Extrude1": name}, desc)
    STEELB.append(name)


def tnut(name, at, n, s, desc):
    # HNTT: 윗면 로컬 Y=0, 길이 로컬 X(홈 방향). at = 형재 겉면의 구멍 중심, n = 겉면 바깥 법선
    o = [at[i] - 2.5 * n[i] for i in range(3)]
    ins("HNTT8-5", name, M(s, n, o), {"Tap1": name}, desc)
    STEELB.append(name)


def wait_cb4(name, seat, d, L):
    # E-10 임시 형상 CB4-L: 머리 Ø7 x 4 + 몸통 Ø4 x L (MISUMI CB 규격표 M4: dk 7, k 4)
    ax = 'X' if d[0] else ('Y' if d[1] else 'Z')
    i = {'X': 0, 'Y': 1, 'Z': 2}[ax]
    s = d[i]
    a = seat[i]
    o = [seat[j] for j in range(3) if j != i]

    def span(dd, a0, a1, **k):
        lo = min(a0, a1)
        base = list(o)
        base.insert(i, lo)
        cyl(dd, base, ax, abs(a1 - a0), **k)
    span(7, a - s * 4, a, name=name)
    span(4, a, a + s * L, op="join", targets=[name])
    WAITB.append(name)


def wait_nut(name, c, ax, a0, a1):
    # E-10 임시 형상 LBNR4: 바깥 Ø8(육각 7 대각 8.1 근사) x 3.2
    base = list(c)
    base.insert({'X': 0, 'Y': 1, 'Z': 2}[ax], min(a0, a1))
    cyl(8, base, ax, abs(a1 - a0), name=name)
    WAITB.append(name)


def sk_poly(name, plane, pts):
    C("sketch.create", {"plane": plane, "name": name})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})


PL_XZ = lambda y: {"origin": [0, y, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}     # 법선 -Y
PL_YZ = lambda x: {"origin": [x, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}     # 법선 +X
PL_XY = lambda z: {"origin": [0, 0, z], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}     # 법선 +Z
UPZ, DNZ, PX = (0, 0, 1), (0, 0, -1), (1, 0, 0)
YP = "P_T01_YPLATE"
L = lambda l: l - 700.0

# ---------------------------------------------------------------------------
# a: Y판 추가 가공 (Ø10 x2, M5 탭 x6, M4 탭 x2). DEV-1: TEEHOLD 탭 L119/196 -> L125/190(받침 끝 가장자리 1.25 -> 7.25)
stage('a')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "MAT_Y"})
for x, l in ((125, -81.4), (-125, 7)):
    zc(10, x, L(l), -371, -359, op="cut", targets=[YP])
TAP_M5 = [(-192, 84), (-180, 84), (-112, 62), (-112, 85), (0, 125), (0, 190)]
for x, l in TAP_M5:
    zc(4.2, x, L(l), -371, -359, op="cut", targets=[YP])
for x, l in ((-92, -121), (-92, -61)):
    zc(3.3, x, L(l), -371, -359, op="cut", targets=[YP])

# ---------------------------------------------------------------------------
# b: 밸브 매니폴드·밸브 4·이음 (STEP대기, MAT_Y)
stage('b')
MAN = "STEP대기_SS5Y3-20-04"
comp(MAN, "MAT_Y", "SS5Y3-20-04", "purchased",
     "SMC SY3000 바 매니폴드 4스테이션 SS5Y3-20-04 — STEP 대기 임시 외곽 50x68x20(X-117~-67, Y-825~-757, Z-390~-370), "
     "P 포트 Rc1/8 +Y 끝면, 배기 R -Y 끝면, CB4 구멍 x2 (카탈로그 외형 임시값, 자료대기) (T16 v0.9.0)")
box((-117, -67, L(-125), L(-57), -390, -370), MAN)
for x, y in ((-92, L(-121)), (-92, L(-61))):
    zc(4.5, x, y, -391, -369, op="cut", targets=[MAN])
cyl(8.7, (-92, L(-57) - 8, -380), 'Y', 8.01, op="cut", targets=[MAN])          # P 포트 Rc1/8 밑구멍
cyl(8.7, (-92, L(-125) - 0.01, -380), 'Y', 8, op="cut", targets=[MAN])         # 배기 R
mat([MAN], "Aluminum")
VALVES = {"V1": -107.75, "V2": -97.25, "V4": -86.75, "V3": -76.25}
VNAMES = []
for v, l in VALVES.items():
    nm = "STEP대기_SY3120-5LZ_%s" % v
    comp(nm, "MAT_Y", "SY3120-5LZ", "purchased",
         "SMC 5포트 솔레노이드 밸브 SY3120-5LZ(3포트로 씀) — STEP 대기 임시 외곽 40x10x48, 매니폴드 밑에 거꾸로 (%s, 스테이션 L %.2f) (T16 v0.9.0)" % (v, l))
    box((-112, -72, L(l) - 5, L(l) + 5, -438, -390), nm)
    VNAMES.append(nm)
mat(VNAMES, "Aluminum")
# A 포트 이음·B 포트 마개: 열을 X -102 / -82 로 엇갈려 이웃 스테이션(피치 10.5)과 겹치지 않게(DEV-2)
FIT = {"V1": ("KQ2H04-M5A", 10.4, -102), "V2": ("KQ2H04-M5A", 10.4, -82),
       "V4": ("KQ2H06-M5A", 12.8, -102), "V3": ("KQ2H06-M5A", 12.8, -82)}
FITS = []
for v, l in VALVES.items():
    pn, d, xa = FIT[v]
    nm = "STEP대기_%s_%s" % (pn, v)
    comp(nm, "MAT_Y", pn, "purchased",
         "SMC 원터치 이음 %s — STEP 대기 임시 외곽 Ø%.1f x 18(Z -456~-438), 밸브 %s A 포트 (카탈로그 외형 임시값) (T16 v0.9.0)" % (pn, d, v))
    zc(d, xa, L(l), -456, -438, name=nm)
    FITS.append(nm)
    xb = -82 if xa == -102 else -102
    nb = "STEP대기_M-5P_%s" % v
    comp(nb, "MAT_Y", "M-5P", "purchased",
         "SMC 마개 M-5P — STEP 대기 임시 외곽 Ø7 x 4(Z -442~-438), 밸브 %s B 포트 막음(3포트 사용) (T16 v0.9.0)" % v)
    zc(7, xb, L(l), -442, -438, name=nb)
    FITS.append(nb)
PF = "STEP대기_KQ2H06-01AS_P"
comp(PF, "MAT_Y", "KQ2H06-01AS", "purchased",
     "SMC 원터치 이음 KQ2H06-01AS(R1/8, 관 Ø6) — STEP 대기 임시 외곽 Ø12.8 x 18, 매니폴드 P 포트 +Y (Y -757~-739) (T16 v0.9.0)")
cyl(12.8, (-92, L(-57), -380), 'Y', 18, name=PF)
FITS.append(PF)
mat(FITS, "Brass")
C("component.activate", {"component": MAN})
for k, (x, y) in enumerate(((-92, L(-121)), (-92, L(-61))), 1):
    wait_cb4("STEP대기_CB4-30_T16_MAN_%d" % k, (x, y, -390), UPZ, 30)

# ---------------------------------------------------------------------------
# c: P_T16_TEEHOLD (PET-CF) + 분기 4 + CB5-12 x2
stage('c')
TH = "P_T16_TEEHOLD"
TH_DESC = ("PET-CF / FDM 3D 출력 / 분기 KQ2T04-00A x4 받침: 판 t4 X-25~25·Y-585~-500·Z-374~-370, 밑 홈 칸막이 3줄(X-25~-18, -6~6, 18~25, Z-380~-374) "
           "-> 홈 폭 12 x2(분기 몸통 Ø10), 가운데 칸막이 카운터보어 Ø9 + Ø5.5 x2 (0,-575)·(0,-510) CB5-12 (T16 v0.9.0)")
comp(TH, "MAT_Y", TH, "normal", TH_DESC)
sk_poly("SK_T16_TEEHOLD", PL_XZ(-500),
        [(-25, -370), (25, -370), (25, -380), (18, -380), (18, -374), (6, -374), (6, -380), (-6, -380),
         (-6, -374), (-18, -374), (-18, -380), (-25, -380)])
C("solid.extrude", {"sketch": "SK_T16_TEEHOLD", "profiles": "all", "distance": 85, "operation": "new", "body_name": TH})
TH_B = [(0, L(125)), (0, L(190))]
for x, y in TH_B:
    zc(9, x, y, -381, -374, op="cut", targets=[TH])
    zc(5.5, x, y, -375, -369, op="cut", targets=[TH])
mat([TH], "PET-CF")
TEES = []
k = 0
for x in (-12, 12):
    for (y0, y1) in ((-583, -547), (-538, -502)):
        k += 1
        nm = "STEP대기_KQ2T04-00A_%d" % k
        comp(nm, TH, "KQ2T04-00A", "purchased",
             "SMC 원터치 이음 유니언 티 KQ2T04-00A(관 Ø4) — STEP 대기 임시 외곽 몸통 Ø10 x 36(Y) + 가지 Ø10 아래로(Z -396), L36 x H20 (T16 v0.9.0)")
        cyl(10, (x, y0, -379), 'Y', y1 - y0, name=nm)
        zc(10, x, (y0 + y1) / 2, -396, -379, op="join", targets=[nm])
        TEES.append(nm)
mat(TEES, "Nylon")
C("component.activate", {"component": TH})
for k, (x, y) in enumerate(TH_B, 1):
    bolt("CB5-12", "CB5-12_T16_TH_%d" % k, (x, y, -374), UPZ,
         "MISUMI 육각 구멍붙이 볼트 M5x12 — P_T16_TEEHOLD 판 t4 밑에서 -> Y판 M5 관통 탭(물림 8) (T16 v0.9.0)")

# ---------------------------------------------------------------------------
# d: P_T16_YMEND (A5052 t6) + CB5-16 x2, P_T16_YCLIP (PET-CF) + CB5-12 x2
stage('d')
YM = "P_T16_YMEND"
YM_DESC = ("A5052 t6 / 레이저 평판 / Y 캐리어 이동단 받침 X-217~-176·Y-622~-568·Z-376~-370, 모서리 C0.5, Ø5.5 x2 (-192/-180,-616) CB5-16, "
           "M4 탭 관통 x2 (-205/-186,-595) 캐리어 끝 쇠 CB4-10 (T16 v0.9.0)")
comp(YM, "MAT_Y", YM, "normal", YM_DESC)
box((-217, -176, L(78), L(132), -376, -370), YM)
C("solid.chamfer", {"edges": [[-217, L(78), -373], [-176, L(78), -373], [-176, L(132), -373], [-217, L(132), -373]], "distance": 0.5})
YM_B = [(-192, L(84)), (-180, L(84))]
for x, y in YM_B:
    zc(5.5, x, y, -377, -369, op="cut", targets=[YM])
YM_T = [(-205, L(105)), (-186, L(105))]
for x, y in YM_T:
    zc(3.3, x, y, -377, -369, op="cut", targets=[YM])
mat([YM], "A5052")
for k, (x, y) in enumerate(YM_B, 1):
    bolt("CB5-16", "CB5-16_T16_YM_%d" % k, (x, y, -376), UPZ,
         "MISUMI 육각 구멍붙이 볼트 M5x16 — P_T16_YMEND t6 밑에서 -> Y판 M5 관통 탭(물림 10) (T16 v0.9.0)")
YC = "P_T16_YCLIP"
YC_DESC = ("PET-CF / FDM 3D 출력 / Y 쪽 케이블 클립 한 덩어리 X-176~-106·Y-648~-605·Z-379~-370, 케이블 홈 X-176~-118·Y-642~-612·Z-377.5~-370"
           "(위 열림, Y판이 덮개, 바닥 1.5), 바닥 구멍 X-128~-118, CB5-12 x2 (-112,-638/-615) 카운터보어 Ø10 깊이 6 (T16 v0.9.0)")
comp(YC, "MAT_Y", YC, "normal", YC_DESC)
box((-176, -106, L(52), L(95), -379, -370), YC)
box((-176.5, -118, L(58), L(88), -377.5, -369.5), op="cut", targets=[YC])
box((-128, -118, L(58), L(88), -379.5, -377), op="cut", targets=[YC])
C("solid.fillet", {"edges": [[-106, L(52), -374.5], [-106, L(95), -374.5]], "radius": 1})
YC_B = [(-112, L(62)), (-112, L(85))]
for x, y in YC_B:
    zc(10, x, y, -379.5, -373, op="cut", targets=[YC])
    zc(5.5, x, y, -374, -369, op="cut", targets=[YC])
mat([YC], "PET-CF")
for k, (x, y) in enumerate(YC_B, 1):
    bolt("CB5-12", "CB5-12_T16_YC_%d" % k, (x, y, -373), UPZ,
         "MISUMI 육각 구멍붙이 볼트 M5x12 — P_T16_YCLIP 카운터보어 바닥(살 3)에서 -> Y판 M5 관통 탭(물림 9) (T16 v0.9.0)")

# ---------------------------------------------------------------------------
# e: Y 캐리어 HSP0320-2BN 3분할 (STEP대기) + 끝 쇠 볼트
stage('e')
YCD = ("igus/MISUMI 케이블 캐리어 HSP0320-2BN(내폭 30, R50) — STEP 대기 임시 외곽 외폭 39 x 외높이 28, 피치 20, 31링크; "
       "대기 자세 3분할(_UPPER MAT_Y, _LOOP·_LOWER MAT_X) (카탈로그 외형 임시값, 자료대기) (T16 v0.9.0)")
YU, YL, YW = "STEP대기_HSP0320-2BN_UPPER", "STEP대기_HSP0320-2BN_LOOP", "STEP대기_HSP0320-2BN_LOWER"
comp(YU, "MAT_Y", "HSP0320-2BN", "purchased", YCD)
box((-215, -176, L(92), L(468.5), -404, -376), YU)
for x, y in YM_T:                                       # 이동단 끝 쇠: Ø4.5 + 머리 자리 Ø8(밑에서)
    zc(4.5, x, y, -380.01, -375.9, op="cut", targets=[YU])
    zc(8, x, y, -404.1, -380, op="cut", targets=[YU])
for k, (x, y) in enumerate(YM_T, 1):
    wait_cb4("STEP대기_CB4-10_T16_YM_%d" % k, (x, y, -380), UPZ, 10)
comp(YL, "MAT_X", "HSP0320-2BN", "reference", "HSP0320-2BN 고리 조각(같은 캐리어, BOM은 _UPPER 한 줄) " + YCD)
CYc, CZc = -231.5, -440.0
C("sketch.create", {"plane": PL_YZ(-215), "name": "SK_T16_YLOOP"})
C("sketch.line", {"points": [[CYc, CZc + 64], [CYc, CZc + 36]], "closed": False})
C("sketch.arc.three_point", {"start": [CYc, CZc + 36], "end": [CYc, CZc - 36], "through": [CYc + 36, CZc]})
C("sketch.line", {"points": [[CYc, CZc - 36], [CYc, CZc - 64]], "closed": False})
C("sketch.arc.three_point", {"start": [CYc, CZc - 64], "end": [CYc, CZc + 64], "through": [CYc + 64, CZc]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T16_YLOOP", "profiles": "all", "distance": 39, "operation": "new", "body_name": YL})
comp(YW, "MAT_X", "HSP0320-2BN", "reference", "HSP0320-2BN 고정 줄 조각(같은 캐리어, BOM은 _UPPER 한 줄) " + YCD)
box((-215, -176, -318, -231.5, -504, -476), YW)
YW_B = [(-205, -310), (-186, -310)]
for x, y in YW_B:                                        # 고정단 끝 쇠: Ø4.5 + 너트 자리 Ø9
    zc(4.5, x, y, -504.1, -500, op="cut", targets=[YW])
    zc(9, x, y, -500, -491.9, op="cut", targets=[YW])
mat([YU, YL, YW], "Nylon")

# ---------------------------------------------------------------------------
# f: P_T16_YTRAY (A5052 t2 판금, MAT_X) + CB5-12/HNTT8-5 x3 + CB4-12/LBNR4 x2
stage('f')
YT = "P_T16_YTRAY"
YT_DESC = ("A5052 t2 / 판금(굽힘 R2) / Y 캐리어 받침 홈통 Y-343~143: 바닥 X-219~-172·Z-506~-504, 세움 X-172~-170, 날개 X-170~-132·Z-480~-478(1300_L 밑면), "
           "바깥 턱 X-219~-217·Z-504~-494, 세움 노치 Y-342~-320·Z-502~-482, 날개 Ø5.5 x3 CB5-12 + HNTT8-5, 고정단 Ø4.5 x2 CB4-12 + LBNR4 (T16 v0.9.0)")
comp(YT, "MAT_X", YT, "normal", YT_DESC)
sk_poly("SK_T16_YTRAY", PL_XZ(143),
        [(-219, -506), (-170, -506), (-170, -480), (-132, -480), (-132, -478), (-172, -478), (-172, -504),
         (-217, -504), (-217, -494), (-219, -494)])
C("solid.extrude", {"sketch": "SK_T16_YTRAY", "profiles": "all", "distance": 486, "operation": "new", "body_name": YT})
C("solid.fillet", {"edges": [[-170, 0, -506], [-172, 0, -478], [-219, 0, -506]], "radius": 4})
C("solid.fillet", {"edges": [[-172, 0, -504], [-170, 0, -480], [-217, 0, -504]], "radius": 2})
box((-173, -169, -342, -320, -502, -482), op="cut", targets=[YT])
YT_W = [(-150, -290), (-150, -80), (-150, 120)]
for x, y in YT_W:
    zc(5.5, x, y, -481, -477, op="cut", targets=[YT])
for x, y in YW_B:
    zc(4.5, x, y, -507, -503, op="cut", targets=[YT])
mat([YT], "A5052")
for k, (x, y) in enumerate(YT_W, 1):
    bolt("CB5-12", "CB5-12_T16_YT_%d" % k, (x, y, -480), UPZ,
         "MISUMI 육각 구멍붙이 볼트 M5x12 — P_T16_YTRAY 날개 t2 밑에서 -> 1300_L 밑 홈 HNTT8-5 (T16 v0.9.0)")
    tnut("HNTT8-5_T16_YT_%d" % k, (x, y, -478), DNZ, (0, 1, 0),
         "MISUMI 후입 T너트 HNTT8-5 — 1300_L 밑 홈, P_T16_YTRAY 날개 (T16 v0.9.0)")
C("component.activate", {"component": YT})
for k, (x, y) in enumerate(YW_B, 1):
    wait_cb4("STEP대기_CB4-12_T16_YT_%d" % k, (x, y, -506), UPZ, 12)
    wait_nut("STEP대기_LBNR4_T16_YT_%d" % k, (x, y), 'Z', -500, -496.8)

# ---------------------------------------------------------------------------
# g: P_T16_XMEND (A5052 t3, MAT_X) + X 캐리어 _A + BASE 쪽 XGLIDE·_LOOP·_B
stage('g')
XM = "P_T16_XMEND"
XM_DESC = ("A5052 t3 / 판금 L(굽힘 R3) / X 캐리어 이동단 받침: 날개 X131~168·Y-286~-240·Z-481~-478(1300_R 밑면), 세움 X128~131·Z-594~-478, "
           "날개 Ø5.5 x2 CB5-12 + HNTT8-5, 세움 Ø4.5 x2 (Y-262, Z-588/-548) CB4-12 + LBNR4, 케이블 창 Y-276~-248·Z-578~-558 (T16 v0.9.0)")
comp(XM, "MAT_X", XM, "normal", XM_DESC)
sk_poly("SK_T16_XMEND", PL_XZ(-240), [(128, -594), (131, -594), (131, -481), (168, -481), (168, -478), (128, -478)])
C("solid.extrude", {"sketch": "SK_T16_XMEND", "profiles": "all", "distance": 46, "operation": "new", "body_name": XM})
C("solid.fillet", {"edges": [[128, -263, -478]], "radius": 6})
C("solid.fillet", {"edges": [[131, -263, -481]], "radius": 3})
box((127, 132, -276, -248, -578, -558), op="cut", targets=[XM])
XM_W = [(150, -275), (150, -251)]
for x, y in XM_W:
    zc(5.5, x, y, -482, -477, op="cut", targets=[XM])
XM_U = [(-262, -588), (-262, -548)]
for y, z in XM_U:
    cyl(4.5, (127, y, z), 'X', 5, op="cut", targets=[XM])
mat([XM], "A5052")
for k, (x, y) in enumerate(XM_W, 1):
    bolt("CB5-12", "CB5-12_T16_XM_%d" % k, (x, y, -481), UPZ,
         "MISUMI 육각 구멍붙이 볼트 M5x12 — P_T16_XMEND 날개 t3 밑에서 -> 1300_R 밑 홈 HNTT8-5 (T16 v0.9.0)")
    tnut("HNTT8-5_T16_XM_%d" % k, (x, y, -478), DNZ, (0, 1, 0),
         "MISUMI 후입 T너트 HNTT8-5 — 1300_R 밑 홈, P_T16_XMEND 날개 (T16 v0.9.0)")
XCD = ("igus/MISUMI 케이블 캐리어 HSP0350-2BN(임시 표기, 내폭 50, R75) — STEP 대기 임시 외곽 외폭 60 x 외높이 36, 43링크, 눕힘; "
       "대기 자세 3분할(_A MAT_X, _LOOP·_B BASE) (카탈로그 외형 임시값, 자료대기) (T16 v0.9.0)")
XA, XL, XB = "STEP대기_HSP0350-2BN_A", "STEP대기_HSP0350-2BN_LOOP", "STEP대기_HSP0350-2BN_B"
comp(XA, "MAT_X", "HSP0350-2BN", "purchased", XCD)
box((131, 443.2, -280, -244, -598, -538), XA)
for y, z in XM_U:
    cyl(4.5, (130.9, y, z), 'X', 4.1, op="cut", targets=[XA])
    cyl(9, (135, y, z), 'X', 8, op="cut", targets=[XA])
C("component.activate", {"component": XM})
for k, (y, z) in enumerate(XM_U, 1):
    wait_cb4("STEP대기_CB4-12_T16_XM_%d" % k, (128, y, z), PX, 12)
    wait_nut("STEP대기_LBNR4_T16_XM_%d" % k, (y, z), 'X', 135, 138.2)
# BASE
XG = "P_T16_XGLIDE"
XG_DESC = ("A5052 t2 / 판금(굽힘 R2) / X 캐리어 미끄럼 받침: 윗판 X-600~870·Y-292~-80·Z-600~-598(1140_XM·XP 윗면), 아래 날개 2 Y-292~-290/-82~-80·Z-635~-600·X-525~794, "
           "Ø5.5 x4 CB5-12 + HNTT8-5, 케이블 내림 Ø30 (100,-112), 고정단 Ø4.5 x2 CB4-12 + LBNR4 (T16 v0.9.0)")
comp(XG, "BASE", XG, "normal", XG_DESC)
sk_poly("SK_T16_XGLIDE", PL_YZ(-600),
        [(-292, -598), (-80, -598), (-80, -635), (-82, -635), (-82, -600), (-290, -600), (-290, -635), (-292, -635)])
C("solid.extrude", {"sketch": "SK_T16_XGLIDE", "profiles": "all", "distance": 1470, "operation": "new", "body_name": XG})
C("solid.fillet", {"edges": [[0, -292, -598], [0, -80, -598]], "radius": 4})
C("solid.fillet", {"edges": [[0, -290, -600], [0, -82, -600]], "radius": 2})
for xa, xb in ((-601, -525), (794, 871)):
    for ya, yb in ((-293, -287.9), (-84.1, -79)):
        box((xa, xb, ya, yb, -636, -600), op="cut", targets=[XG])
XG_B = [(-587, -250), (-587, -122), (856, -250), (856, -122)]
for x, y in XG_B:
    zc(5.5, x, y, -601, -597, op="cut", targets=[XG])
zc(30, 100, -112, -601, -597, op="cut", targets=[XG])
XG_F = [(141, -118), (141, -106)]
for x, y in XG_F:
    zc(4.5, x, y, -601, -597, op="cut", targets=[XG])
mat([XG], "A5052")
for k, (x, y) in enumerate(XG_B, 1):
    bolt("CB5-12", "CB5-12_T16_XG_%d" % k, (x, y, -598), DNZ,
         "MISUMI 육각 구멍붙이 볼트 M5x12 — P_T16_XGLIDE 윗판 t2 위에서 -> 1140 윗면 홈 HNTT8-5 (T16 v0.9.0)")
    tnut("HNTT8-5_T16_XG_%d" % k, (x, y, -600), UPZ, (0, 1, 0),
         "MISUMI 후입 T너트 HNTT8-5 — 1140_XM/XP 윗면 홈, P_T16_XGLIDE (T16 v0.9.0)")
comp(XL, "BASE", "HSP0350-2BN", "reference", "HSP0350-2BN 고리 조각(같은 캐리어, BOM은 _A 한 줄) " + XCD)
XCx, XCy = 443.2, -187.0
C("sketch.create", {"plane": PL_XY(-598), "name": "SK_T16_XLOOP"})
C("sketch.line", {"points": [[XCx, XCy + 93], [XCx, XCy + 57]], "closed": False})
C("sketch.arc.three_point", {"start": [XCx, XCy + 57], "end": [XCx, XCy - 57], "through": [XCx + 57, XCy]})
C("sketch.line", {"points": [[XCx, XCy - 57], [XCx, XCy - 93]], "closed": False})
C("sketch.arc.three_point", {"start": [XCx, XCy - 93], "end": [XCx, XCy + 93], "through": [XCx + 93, XCy]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T16_XLOOP", "profiles": "all", "distance": 60, "operation": "new", "body_name": XL})
comp(XB, "BASE", "HSP0350-2BN", "reference", "HSP0350-2BN 고정 줄 조각(같은 캐리어, BOM은 _A 한 줄) " + XCD)
box((131, 443.2, -130, -94, -598, -538), XB)
for x, y in XG_F:
    zc(4.5, x, y, -598.1, -594, op="cut", targets=[XB])
    zc(9, x, y, -594, -585.9, op="cut", targets=[XB])
mat([XA, XL, XB], "Nylon")
C("component.activate", {"component": XG})
for k, (x, y) in enumerate(XG_F, 1):
    wait_cb4("STEP대기_CB4-12_T16_XG_%d" % k, (x, y, -600), UPZ, 12)
    wait_nut("STEP대기_LBNR4_T16_XG_%d" % k, (x, y), 'Z', -594, -590.8)

# ---------------------------------------------------------------------------
# h: 이름·재질·대기
stage('h')
C("component.activate", {"component": "root"})
mat(STEELB + WAITB, "Steel")
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})
meta_flush()
C("component.rename", {"component": "root", "name": VER})
C("document.metadata.set", {"values": {"description": "T16 mechanism: X/Y cable carriers HSP0320/HSP0350 (STEP-wait), SY3120 valve manifold on MAT_Y, tee holder, Y/X carrier brackets, Y tray, X glide plate"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ---------------------------------------------------------------------------
# i: v0.9.0 -> v0.9.1 고침(DEV-7·DEV-8). MAT_Y 하위 컴포넌트에 넣은 실물 STEP 볼트 6개는 file.insert_step 의 matrix 가
#    컴포넌트 로컬로 읽혀 세계 Y -700 만큼 어긋났다(MAT_Y 원점 = 세계 Y -700 대기). 세계 +700 으로 옮긴다.
#    YMEND CB5-16_2 (-180,-616) 머리 Ø8.5 가 YCLIP X -176 면을 0.25 넘어 YCLIP 에 머리 자리 Ø10 (Z -379.5~-375.9)을 낸다.
stage('i')
for nm in ("CB5-12_T16_TH_1", "CB5-12_T16_TH_2", "CB5-16_T16_YM_1", "CB5-16_T16_YM_2", "CB5-12_T16_YC_1", "CB5-12_T16_YC_2"):
    C("occurrence.move", {"occurrence": nm + ":1", "space": "world", "translate": [0, 700, 0]})
C("component.activate", {"component": YC})
cyl(10, (-180, -616, -379.5), 'Z', 3.6, op="cut", targets=[YC])
C("component.activate", {"component": "root"})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.rename", {"component": "root", "name": "FSAP_v0.9.1"})
C("document.metadata.set", {"values": {"description": "T16 mechanism: X/Y cable carriers (STEP-wait), valve manifold on MAT_Y, tee holder, carrier brackets, Y tray, X glide; v0.9.1 fixes 6 MAT_Y bolt positions and YCLIP head relief"}})

MADE = {TH: TH_DESC, YM: YM_DESC, YC: YC_DESC, YT: YT_DESC, XM: XM_DESC, XG: XG_DESC,
        YP: "A5052 t10 / 추가: Ø10 x2 (125,-781.4)·(-125,-693), M5 탭 관통 x6, M4 탭 관통 x2"}
if __name__ == '__main__':
    allc = []
    for n in sorted(STAGES):
        json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        allc += STAGES[n]
        print(n, len(STAGES[n]))
    json.dump(allc, open(os.path.join(ROOT, 'tools', 'out', 'mech_T16', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    new_bodies = [b for b in MAT if b != YP]
    json.dump({"made": MADE, "bolts": STEELB, "wait_bolts": WAITB, "materials": MAT, "new_bodies": new_bodies,
               "changed": [YP] + new_bodies},
              open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allc), 'bodies', len(new_bodies))
