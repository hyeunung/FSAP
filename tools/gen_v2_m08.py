# -*- coding: utf-8 -*-
"""M08 U8 공압·안전 자리 생성기 — 기준 3D_Modeling/FSAP_v2.4.0.sc -> 3D_Modeling/FSAP_v2.5.0.sc (모델링부 2026-11-05)
설계안 docs/reports/mechanism/mech_M08_design.md 6장(6-1은 mech_M08_design1.md 5절로 갈음). 보고서 mech_M08_model.md.
python -X utf8 -B tools/gen_v2_m08.py          -> tools/out/mech_M08/model/stage_*.json, tools/out/mech_M08/edit.json, lists.json
python -X utf8 -B tools/gen_v2_m08.py machine  -> tools/machine.json U8_PNEU 고침
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm. U8은 고정(새 조인트 0). 새 부품은 모두 U8_PNEU 아래(다관 커넥터 플러그 반쪽만 U7_CASSETTE 아래).
관(TU0604·TU0805)은 직선 원통 + 모서리 구로 그린 임시 관이다(굽힘 R은 디테일, 유연 거동은 요구서 7절).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cz, cy, cx, mat_assign  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUTT = os.path.join(ROOT, "out", "mech_M08")
OUT = os.path.join(OUTT, "model")
STEP = PRJ + "/purchased-step/"
U8 = "U8_PNEU"
CST = "U7_CASSETTE"
OLD = ["U8_REG", "U8_LC_L", "U8_LC_R", "U8_LAMP", "U8_HMI"]


def r4(v):
    return round(float(v), 4)


def add(a, b, k=1.0):
    return tuple(r4(a[i] + k * b[i]) for i in range(3))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mrow(lx, ly, lz, t):
    return [round(v, 6) for i in range(3) for v in (lx[i], ly[i], lz[i], t[i])]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (0, 1, 0)


def tag(v):
    return "".join(("P" if c > 0 else "N") + "XYZ"[i] for i, c in enumerate(v) if c)


def copy(occ, d):
    return C("occurrence.copy", occurrence=occ, in_place=True, translate=[r4(v) for v in d])


ADDED = []      # 새 컴포넌트(occurrence :1) — 리지드 묶음·목록
RIGID = []      # U8_PNEU와 리지드로 묶을 occurrence


def insert_group(path, comp, cols, places, src_body, pn, desc=None, mat=None, offset=None, parent=U8):
    p0 = places[0]
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=mrow(*cols, p0)),
         C("body.rename", body=src_body, name=comp)]
    if offset is not None:
        s.append(C("solid.offset_face", faces=offset[0], distance=r4(offset[1]), body=comp))
    md = {"component": comp, "part_number": pn, "bom_type": "purchased"}
    if desc:
        md["description"] = desc
    s.append(C("component.metadata.set", **md))
    if mat:
        s.append(mat_assign([comp], mat))
    s.append(C("occurrence.reparent", occurrence=comp + ":1", parent=parent))
    s += [copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    ADDED.append(comp)
    RIGID.extend(["%s:%d" % (comp, i + 1) for i in range(len(places))])
    return s


def tmp_comp(comp, body_cmds, bodies, pn, desc, mat="Default", copies=(), parent=U8):
    """STEP대기 임시 형상 컴포넌트: 그린 바디를 새 컴포넌트로 옮기고, copies(세계 이동)만큼 복사."""
    s = [C("component.create", name=comp, parent=parent, activate=False)]
    s += body_cmds
    s += [mat_assign(bodies, mat), C("component.move_bodies", bodies=bodies, component=comp),
          C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc)]
    s += [copy(comp + ":1", d) for d in copies]
    ADDED.append(comp)
    return s


def made(body_cmds, bodies, mat):
    return body_cmds + [mat_assign(bodies, mat), C("component.move_bodies", bodies=bodies, component=U8)]


def prism(name, pts, z0, z1, op="new", tg=None):
    """XY 다각형을 Z z0~z1로 밀어 한 바디로."""
    sk = "SK_" + name
    p = {"sketch": sk, "distance": r4(z1 - z0), "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return [C("sketch.create", plane={"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk),
            C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
            C("sketch.finish"), C("solid.extrude", **p)]


def prism_yz(name, pts, x0, x1):
    """YZ 다각형((Y, Z))을 X x0~x1로."""
    sk = "SK_" + name
    return [C("sketch.create", plane={"origin": [x0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name=sk),
            C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
            C("sketch.finish"), C("solid.extrude", sketch=sk, distance=r4(x1 - x0), operation="new", body_name=name)]


def hole(body, p, d, length, r=2.75):
    """p에서 d 방향으로 length만큼 원통 자르기(판 관통 구멍)."""
    base = add(p, d, -0.5)
    return C("solid.cylinder", radius=r, height=r4(length + 1.0), base=list(base), axis=list(d), operation="cut", targets=[body])


def tube(name, pts, r, R):
    """3D 스케치(직선 + 굽힘 호)를 따라 solid.pipe. 굽힘 반지름은 R(SMC 최소 굽힘 반지름 TU0604 15 / TU0805 20)이고,
    짧은 구간에서는 양쪽 구간 길이의 반까지로 줄인다(BENDS에 기록). 처음 안의 원통 + 구 join은 구 결합이 실패했다(앱 실측)."""
    import math
    n = len(pts)
    d = [[pts[i + 1][k] - pts[i][k] for k in range(3)] for i in range(n - 1)]
    L = [math.sqrt(sum(v * v for v in x)) for x in d]
    u = [[v / L[i] for v in d[i]] for i in range(n - 1)]
    rc = [0.0] * n
    for i in range(1, n - 1):
        lim_a = L[i - 1] if i - 1 == 0 else L[i - 1] / 2
        lim_b = L[i] if i == n - 2 else L[i] / 2
        rc[i] = min(R, lim_a, lim_b)
        BENDS.append((name, i, round(rc[i], 2), R))
    sk = "SK_" + name
    s = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    wires = 0
    for i in range(n - 1):
        a0 = [pts[i][k] + rc[i] * u[i][k] for k in range(3)]
        b0 = [pts[i + 1][k] - rc[i + 1] * u[i][k] for k in range(3)]
        if sum((b0[k] - a0[k]) ** 2 for k in range(3)) > 1e-6:
            s.append(C("sketch.line3d", points=[[r4(v) for v in a0], [r4(v) for v in b0]]))
            wires += 1
        if i < n - 2 and rc[i + 1] > 0:
            P, q = pts[i + 1], rc[i + 1]
            st = [P[k] - q * u[i][k] for k in range(3)]
            en = [P[k] + q * u[i + 1][k] for k in range(3)]
            c = [P[k] - q * u[i][k] + q * u[i + 1][k] for k in range(3)]
            m = [(st[k] - c[k]) + (en[k] - c[k]) for k in range(3)]
            mn = math.sqrt(sum(v * v for v in m))
            th = [c[k] + q * m[k] / mn for k in range(3)]
            s.append(C("sketch.arc3d", start=[r4(v) for v in st], through=[r4(v) for v in th], end=[r4(v) for v in en]))
            wires += 1
    s += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (j + 1) for j in range(wires)], diameter=2 * r, operation="new", body_name=name)]
    return s


BENDS = []


# ====================================================================== 좌표
REG_X = {"N": 700.0, "F": 800.0, "S": 900.0}
RY = 95.1                          # 레귤레이터 손잡이·포트 중심 Y
ZP = 511.0                         # 포트·게이지 중심 Z
ST = [1044.5 + 5.25 + 10.5 * k for k in range(6)]   # 밸브 스테이션 1~6 가운데 X
ZA, ZB = 340.0, 360.0              # A·B 포트 Z
A0 = lambda x: (x, 36.5, 325.5)    # A 포트 피팅 관 끝(출구 -Z)
B0 = lambda x: (x, 36.5, 374.5)    # B 포트 피팅 관 끝(출구 +Z)


# ====================================================================== 1. 준비·지움
def stage_prep():
    return [C("motion.play", study="REST", step=0, quiet=True), C("solid.remove", bodies=OLD)]


# ====================================================================== 2. 레귤레이터
def stage_reg():
    s = []
    for k, x in REG_X.items():
        nm = "STEP대기_IR1000-01BG_M08_" + k
        bk = nm + "_BRKT"
        body = [box(nm, x - 12.5, x + 12.5, 72.6, 117.6, 475, 547),
                cz(14.0, x, RY, 547, 565, "join", [nm]),
                cy(13.0, x, ZP, 47.6, 72.6, "join", [nm]),
                box(bk, x - 25, x + 25, 117.6, 119.9, 475, 535)]
        body += [hole(bk, (x - 17, 117.6, 490), (0, 1, 0), 2.3), hole(bk, (x + 17, 117.6, 520), (0, 1, 0), 2.3)]
        s += tmp_comp(nm, body, [nm, bk], "IR1000-01BG",
                      "SMC IR1000-01BG precision regulator with gauge and bracket (placeholder, catalog outline, M08)")
    # 이음 KQ2L08-01AS: 몸 옆 Rc1/8(Z 511)에서 꼬다리 10 + 엘보 Ø13.5, 관 출구 -Z(바닥 Z 455)
    for side, sg in (("PX", 1), ("NX", -1)):
        nm = "STEP대기_KQ2L08-01AS_M08_" + side
        x = REG_X["N"]
        # 꼬다리 12.5(몸 옆 x±12.5 -> x±25)가 엘보(중심 x±29.25, r 6.75, 안쪽 끝 x±22.5)에 2.5 겹쳐 한 덩어리.
        # (처음 안은 꼬다리 10이라 엘보와 접하기만 해 두 덩어리가 됐고, 그 바디에 다리를 join하자 앱·CLI 모두 끝나지 않았다)
        sx = x + 12.5 if sg > 0 else x - 25.0
        ex = x + sg * 29.25
        body = [cx(5.0, RY, ZP, sx, sx + 12.5, "new", None, nm), cz(6.75, ex, RY, 455, 517.75, "join", [nm])]
        s += tmp_comp(nm, body, [nm], "KQ2L08-01AS", "SMC KQ2L08-01AS elbow R1/8-8 (placeholder, M08)",
                      copies=[(100, 0, 0), (200, 0, 0)])
    return s


# ====================================================================== 3. 밸브
def stage_valve():
    s = []
    nm = "STEP대기_SS5Y3-20-06_M08"
    pts = [(1027, 50), (1044.5, 50), (1044.5, 80), (1107.5, 80), (1107.5, 50), (1123, 50), (1123, 120), (1027, 120)]
    body = prism(nm, pts, 330, 370)
    # CB4-20 자리: 끝 블록 Ø8 자리파기(Y 50~105) + Ø4.5 관통(105~120)
    for x in (1035.75, 1115.25):
        body += [C("solid.cylinder", radius=4.0, height=55.5, base=[x, 49.5, 350], axis=[0, 1, 0], operation="cut", targets=[nm]),
                 C("solid.cylinder", radius=2.25, height=16, base=[x, 104.5, 350], axis=[0, 1, 0], operation="cut", targets=[nm])]
    s += tmp_comp(nm, body, [nm], "SS5Y3-20-06", "SMC SS5Y3-20-06 manifold base 6 stations (placeholder, M08)")
    vn = "STEP대기_SY3120-5LZD-M5_M08"
    x0 = ST[0]
    vb = [box(vn, x0 - 5.25, x0 + 5.25, 50, 80, 330, 370)]
    vb += [C("solid.cylinder", radius=2.6, height=3.5, base=[x0, 50, z], axis=[0, 1, 0], operation="cut", targets=[vn]) for z in (ZA, ZB)]
    s += tmp_comp(vn, vb, [vn], "SY3120-5LZD-M5", "SMC SY3120-5LZD-M5 5-port solenoid valve (placeholder, M08)",
                  copies=[(10.5 * k, 0, 0) for k in range(1, 6)])
    bn = "STEP대기_CB4-20_M08"
    bb = [cy(3.5, 1035.75, 350, 101, 105, "new", None, bn), cy(2.0, 1035.75, 350, 105, 125, "join", [bn])]
    s += tmp_comp(bn, bb, [bn], "CB4-20", "Misumi CB4-20 socket head cap screw (placeholder)", mat="SCM435",
                  copies=[(1115.25 - 1035.75, 0, 0)])
    # 피팅 KQ2L06-M5A(실물 STEP): 로컬 X = 출구, 로컬 Y = 포트 바깥 법선, 원점 = 포트 면
    ny = (0, -1, 0)
    lx = (0, 0, -1)
    s += insert_group("KQ2L06-M5A/KQ2L06-M5A.stp", "KQ2L06-M5A_M08_NZ", (lx, ny, cross(lx, ny)),
                      [(x, 50.0, ZA) for x in ST], "KQ2L06-M5A", "KQ2L06-M5A", mat="Default")
    lx = (0, 0, 1)
    s += insert_group("KQ2L06-M5A/KQ2L06-M5A.stp", "KQ2L06-M5A_M08_PZ", (lx, ny, cross(lx, ny)),
                      [(ST[i], 50.0, ZB) for i in (0, 1, 3, 4, 5)], "KQ2L06-M5A", "KQ2L06-M5A", mat="Default")
    return s


# ====================================================================== 4. 커튼·기둥·캡
COL_COLS = ((0, 0, 1), (0, 1, 0), (-1, 0, 0))    # 4080 로컬 X(길이) -> +Z, 80 -> Y, 40 -> X
COLS = {"FL": ("HFS8-4080-2370_M08_FL", 2370, (-2280.0, -1600.0, -840.0)),
        "FR": ("HFS8-4080-1900_M08_FR", 1900, (380.0, -1600.0, -370.0)),
        "R": ("HFS8-4080-1900_M08_R", 1900, (-2320.0, 80.0, -370.0))}


def stage_curtain():
    s = []
    LC = {"1E": (-2260, -2230, -1630, -1600), "1R": (330, 360, -1630, -1600),
          "2E": (-2330, -2300, -1555, -1525), "2R": (-2330, -2300, 10, 40)}
    for k, (x0, x1, y0, y1) in LC.items():
        nm = "STEP대기_F3SG-4RA1520-14_M08_" + k
        s += tmp_comp(nm, [box(nm, x0, x1, y0, y1, -30, 1530)], [nm], "F3SG-4RA1520-14",
                      "Omron F3SG-4RA1520-14 safety light curtain %s (placeholder 30x30, protective height 1520, M08)"
                      % ("emitter" if k.endswith("E") else "receiver"))
    for key, (comp, L, o) in COLS.items():
        off = (["%s:face:0" % comp], L - 1900) if L != 1900 else None
        s += insert_group("HFS8-4080-1900/HFS8-4080-1900.stp", comp, COL_COLS, [o], "Boss-Extrude1",
                          "HFS8-4080-%d" % L, "Misumi HFS8-4080-1900 STEP%s (M08 light curtain column)" %
                          (", end face offset to L%d" % L if L != 1900 else ""), "Aluminum", off)
    top = [(o[0], o[1], o[2] + L) for _, L, o in COLS.values()]
    bot = [o for _, _, o in COLS.values()]
    s += insert_group("HFC8-4080-B/HFC8-4080-B.stp", "HFC8-4080-B_M08_T", ((0, 1, 0), (-1, 0, 0), (0, 0, 1)), top,
                      "Fillet2", "HFC8-4080-B", mat="Default")
    s += insert_group("HFC8-4080-B/HFC8-4080-B.stp", "HFC8-4080-B_M08_B", ((0, 1, 0), (1, 0, 0), (0, 0, -1)), bot,
                      "Fillet2", "HFC8-4080-B", mat="Default")
    return s


# ---------------------------------------------------------------- 체결(볼트 머리 밑 점, 축) / 너트(점, 면 바깥 법선, 홈 방향)
def fasteners():
    B, N = [], []
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    NX_, NY_, NZ_ = (-1, 0, 0), (0, -1, 0), (0, 0, -1)
    for x in REG_X.values():
        B += [("CB5-12", (x - 17, 117.6, 490.0), Y, "REG"), ("CB5-12", (x + 17, 117.6, 520.0), Y, "REG")]
    for y in (-1580.0, -1500.0):          # 이음판: 기둥 홈 Y -1580, 다리 홈 Y -1500
        for z in (-700.0, -440.0):
            B.append(("CB5-12", (-2306.0, y, z), X, "FL_JOINT"))
            N.append(((-2297.5, y, z), NX_, Z))
    for zs in ((-310.0, -270.0), (-72.0, -32.0)):   # 앞오른 L: 기둥 -X 면 / 가로대·레일 -Y 면
        for z in zs:
            B.append(("CB5-12", (356.0, -1580.0, z), X, "FR_L"))
            N.append(((362.5, -1580.0, z), NX_, Z))
            B.append(("CB5-12", (315.0, -1524.0, z), Y, "FR_L"))
            N.append(((315.0, -1517.5, z), NY_, X))
    for h in (100.0, 1400.0):             # 옆 투광 L
        B.append(("CB5-12", (-2303.0, -1580.0, h), X, "LC2F"))
        N.append(((-2297.5, -1580.0, h), NX_, Z))
        B.append(("CB5-12", (-2315.0, -1558.0, h), Y, "LC2F"))
    for z in (-300.0, 150.0, 600.0):      # 뒤 기둥 L: NX 기둥 -Y 면 / 뒤 기둥 -X 면
        B.append(("CB5-16", (-2360.0, 114.0, z), Y, "R_L"))
        if z < 250:                       # Z 600은 보(P_M07_BEAM, Z 250~650) 앞면 M5 탭 — 너트 없음(80160 기둥은 Z 250까지)
            N.append(((-2360.0, 122.5, z), NY_, Z))
        B.append(("CB5-16", (-2346.0, 100.0, z), X, "R_L"))
        N.append(((-2337.5, 100.0, z), NX_, Z))
    for x in (1170.0, 1210.0):            # HMI 받침판 -> PX 기둥 앞면
        for z in (350.0, 530.0):
            B.append(("CB5-16", (x, 110.0, z), Y, "HMI_MOUNT"))   # 보 앞면 M5 탭(보가 X 1230까지, 80160 기둥은 Z 250까지)
    B += [("CB5-16", (1185.0, 104.0, 510.0), Y, "HMI_L"), ("CB5-16", (1185.0, 104.0, 370.0), Y, "HMI_L"),
          ("CB5-16", (1185.0, 85.0, 486.0), NZ_, "HMI_L"), ("CB5-16", (1185.0, 85.0, 394.0), Z, "HMI_L")]
    N += [((1185.0, 85.0, 477.5), Z, Y), ((1185.0, 85.0, 402.5), NZ_, Y)]
    for z in (420.0, 460.0):              # 패널 받침 -> 팔 +X 면
        B.append(("CB5-12", (1207.0, -431.5, z), NX_, "HMI_PLATE"))
        N.append(((1202.5, -431.5, z), X, Y))
    return B, N


# ====================================================================== 5. 가공품(이음판·L·HMI 받침)
def stage_made():
    s = []
    nm = "P_M08_LC_JOINT_FL_WJ"
    pl = [box(nm, -2306, -2300, -1640, -1480, -800, -340)]
    pl += [hole(nm, (-2306, y, z), (1, 0, 0), 6) for y in (-1580, -1500) for z in (-700, -440)]
    s += made(pl, [nm], "A5052")
    sm = []
    for i, (z0, z1, zs) in enumerate(((-330, -250, (-310, -270)), (-88, -16, (-72, -32)))):
        nm = "P_M08_LC_BRKT_FR_SM_%d" % (i + 1)
        sm += prism(nm, [(356, -1595), (360, -1595), (360, -1520), (300, -1520), (300, -1524), (356, -1524)], z0, z1)
        sm += [hole(nm, (356, -1580, z), (1, 0, 0), 4) for z in zs] + [hole(nm, (315, -1524, z), (0, 1, 0), 4) for z in zs]
    for i, h in enumerate((100, 1400)):
        nm = "P_M08_LC2F_BRKT_SM_%d" % (i + 1)
        sm += prism(nm, [(-2303, -1620), (-2300, -1620), (-2300, -1555), (-2330, -1555), (-2330, -1558), (-2303, -1558)], h - 15, h + 15)
        sm += [hole(nm, (-2303, -1580, h), (1, 0, 0), 3), hole(nm, (-2315, -1558, h), (0, 1, 0), 3)]
    for i, z in enumerate((-300, 150, 600)):
        nm = "P_M08_LBRK_R%d_SM" % (i + 1)
        sm += prism(nm, [(-2380, 120), (-2340, 120), (-2340, 75), (-2346, 75), (-2346, 114), (-2380, 114)], z - 15, z + 15)
        sm += [hole(nm, (-2360, 114, z), (0, 1, 0), 6), hole(nm, (-2346, 100, z), (1, 0, 0), 6)]
    for nm, pts, zz in (("P_M08_LBRK_H1_SM", [(110, 480), (110, 525), (104, 525), (104, 486), (65, 486), (65, 480)], (510, 486)),
                        ("P_M08_LBRK_H2_SM", [(110, 400), (110, 355), (104, 355), (104, 394), (65, 394), (65, 400)], (370, 394))):
        sm += prism_yz(nm, pts, 1170, 1200)
        zt = 480 if "H1" in nm else 394
        sm += [hole(nm, (1185, 104, zz[0]), (0, 1, 0), 6), hole(nm, (1185, 85, zt), (0, 0, 1), 6)]
    nm = "P_M08_HMI_PLATE_SM"
    sm += prism(nm, [(1170, -465), (1442, -465), (1442, -463), (1170, -463)], 343, 557)
    sm += prism(nm + "_W", [(1205, -464), (1207, -464), (1207, -400), (1205, -400)], 400, 480, "join", [nm])
    sm += [hole(nm, (1207, -431.5, z), (-1, 0, 0), 2) for z in (420, 460)]
    smb = ["P_M08_LC_BRKT_FR_SM_1", "P_M08_LC_BRKT_FR_SM_2", "P_M08_LC2F_BRKT_SM_1", "P_M08_LC2F_BRKT_SM_2",
           "P_M08_LBRK_R1_SM", "P_M08_LBRK_R2_SM", "P_M08_LBRK_R3_SM", "P_M08_LBRK_H1_SM", "P_M08_LBRK_H2_SM", nm]
    s += made(sm, smb, "SUS304")
    nm = "P_M08_HMI_MOUNT_ML"
    hm = [box(nm, 1160, 1225, 110, 120, 340, 540)]
    hm += [hole(nm, (x, 110, z), (0, 1, 0), 10) for x in (1170, 1210) for z in (350, 530)]
    hm += [hole(nm, (1185, 110, z), (0, 1, 0), 10, 2.1) for z in (510, 370)]
    s += made(hm, [nm], "A5052")
    s += made([box("U8_HMI_PANEL", 1170, 1442, -522, -465, 343, 557)], ["U8_HMI_PANEL"], "Default")
    return s


# ====================================================================== 6. 경광등·HMI 팔·다관 커넥터
def stage_misc():
    s = []
    nm = "STEP대기_LR6-302WJBW-RYG_M08"
    s += tmp_comp(nm, [cz(30.0, 1190, 270, 650, 950, "new", None, nm)], [nm], "LR6-302WJBW-RYG",
                  "PATLITE LR6-302WJBW-RYG signal tower 3 tiers (placeholder D60 x 300, M08)")
    lx, ly = (0, -1, 0), (0, 0, 1)
    o = (1185.0, 110.0, 440.0)
    fp = [r4(o[i] + 580 * lx[i] + 6.3472 * ly[i] + 18.5178 * cross(lx, ly)[i]) for i in range(3)]
    s += insert_group("HFS8-4080-580/HFS8-4080-580.stp", "HFS8-4080-570_M08_HMI", (lx, ly, cross(lx, ly)), [o],
                      "Boss-Extrude1", "HFS8-4080-570", "Misumi HFS8-4080-580 STEP, end face offset to L570 (HMI arm)",
                      "Aluminum", ([fp], -10))
    nm = "STEP대기_KDM10-06_M08"
    s += tmp_comp(nm, [box(nm, 90, 140, -80, -40, 650.1, 675)], [nm], "KDM10-06",
                  "SMC KDM10-06 multi-connector, fixed half (placeholder, M08)")
    nm2 = nm + "_PLUG"
    s += tmp_comp(nm2, [box(nm2, 90, 140, -80, -40, 675, 697)], [nm2], "KDM10-06",
                  "SMC KDM10-06 multi-connector, plug half on cassette (placeholder, M08)", parent=CST)
    return s


# ====================================================================== 7. 볼트·너트
def stage_fast():
    B, N = fasteners()
    s = []
    g = {}
    for pn, p, d, _k in B:
        g.setdefault((pn, tuple(d)), []).append(p)
    for (pn, d), pl in g.items():
        cols = (d, perp(d), cross(d, perp(d)))
        s += insert_group("%s/%s.stp" % (pn, pn), "%s_M08_%s" % (pn, tag(d)), cols, pl, "Cut-Extrude1", pn, mat="SCM435")
    gn = {}
    for p, n, sd in N:
        gn.setdefault((tuple(sd), tuple(n)), []).append(p)
    for (sd, n), pl in gn.items():
        cols = (sd, n, cross(sd, n))
        s += insert_group("HNTT8-5/HNTT8-5.stp", "HNTT8-5_M08_%s_%s" % (tag(n), tag(sd)), cols, pl, "Tap1", "HNTT8-5", mat="Steel")
    return s, g, gn


# ====================================================================== 8. 관
def tubes():
    T = {}
    for i, (k, x) in enumerate(REG_X.items()):
        zi, zo = 305.0 + 10 * i, 340.0 + 10 * i
        xi, xo = x - 29.25, x + 29.25
        T["TU0805_M08_REG_IN_%d" % (i + 1)] = (4.0, [(xi, RY, 455), (xi, RY, zi), (xi, 56, zi), (1140, 56, zi)])
        T["TU0805_M08_REG_OUT_%d" % (i + 1)] = (4.0, [(xo, RY, 455), (xo, RY, zo), (xo, 110, zo), (1027, 110, zo)])
    X1, X2, X3 = ST[0], ST[1], ST[2]
    T["TU0604_M08_U4_A"] = (3.0, [A0(X1), (X1, 36.5, 270), (X1, 105, 270), (-165, 105, 270), (-165, 105, 330), (-165, 45, 330)])
    T["TU0604_M08_U4_B"] = (3.0, [B0(X1), (X1, 36.5, 385), (X1, 22, 385), (1020, 22, 385), (1020, 22, 278), (1020, 112, 278),
                                  (-175, 112, 278), (-175, 112, 320), (-175, 45, 320)])
    T["TU0604_M08_U6"] = (3.0, [A0(X3), (X3, 36.5, 262), (X3, 105, 262), (-347, 105, 262), (-347, 105, 158.65),
                                (-347, -130, 158.65), (-289.5, -130, 158.65)])
    T["TU0604_M08_U5_A"] = (3.0, [A0(X2), (X2, 36.5, 316), (X2, 14, 316), (1032, 14, 316), (1032, 14, 690), (1032, 190, 690), (-1242, 190, 690)])
    T["TU0604_M08_U5_B"] = (3.0, [B0(X2), (X2, 36.5, 400), (1040, 36.5, 400), (1040, 36.5, 680), (1040, 182, 680), (-1242, 182, 680)])
    lane = {3: 130.0, 4: 140.0, 5: 150.0}
    turnA = {3: 127.5, 4: 112.5, 5: 97.5}
    turnB = {3: 135.0, 4: 120.0, 5: 105.0}
    n = 0
    for st in (3, 4, 5):
        x = ST[st]
        n += 1
        T["TU0604_M08_U7_%d" % n] = (3.0, [A0(x), (x, 36.5, 318), (x, 14, 318), (x, 14, 670), (x, lane[st], 670),
                                           (turnA[st], lane[st], 670), (turnA[st], -40, 670)])
        n += 1
        T["TU0604_M08_U7_%d" % n] = (3.0, [B0(x), (x, 36.5, 660), (x, lane[st], 660), (turnB[st], lane[st], 660), (turnB[st], -40, 660)])
    return T


def stage_tubes(part):
    s = []
    T = tubes()
    names = [k for k in T if (k.startswith("TU0805") if part == 1 else not k.startswith("TU0805"))]
    for nm in names:
        r, pts = T[nm]
        pn = nm.split("_")[0]
        s += tmp_comp(nm, tube(nm, pts, r, 20.0 if r > 3.5 else 15.0), [nm], pn, "SMC %s polyurethane tube, cut to length (route M08)" % pn)
    return s


def stage_final():
    return [C("joint.rigid_group", occurrences=["U8_PNEU:1"] + [o for o in RIGID]),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M08 mechanism: U8 regulators IR1000 x3, SS5Y3 6-station valve, F3SG light curtains x2 pairs on HFS8 columns, LR6 lamp, HMI arm, tubes")]


def main():
    os.makedirs(OUT, exist_ok=True)
    sf, g, gn = stage_fast()
    stages = [("1_prep", stage_prep()), ("2_reg", stage_reg()), ("3_valve", stage_valve()), ("4_curtain", stage_curtain()),
              ("5_made", stage_made()), ("6_misc", stage_misc()), ("7_fast", sf), ("8_tube_reg", stage_tubes(1)),
              ("9_tube_valve", stage_tubes(2)), ("10_final", stage_final())]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st))
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.4.0.sc", "result": "3D_Modeling/FSAP_v2.5.0.sc", "generator": "tools/gen_v2_m08.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))
    B, N = fasteners()
    lists = {"added_components": ADDED, "rigid": RIGID,
             "bolts": {"%s_M08_%s" % (k[0], tag(k[1])): len(v) for k, v in g.items()},
             "nuts": {"HNTT8-5_M08_%s_%s" % (tag(k[1]), tag(k[0])): len(v) for k, v in gn.items()},
             "bolt_list": [{"spec": pn, "seat": list(p), "axis": list(d), "kind": k} for pn, p, d, k in B],
             "nut_list": [{"pos": list(p), "normal": list(n), "slot": list(sd)} for p, n, sd in N],
             "tubes": {k: {"r": v[0], "pts": v[1]} for k, v in tubes().items()}, "bends": BENDS, "commands": len(allc)}
    json.dump(lists, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(ADDED), "components", len(RIGID), "rigid", lists["bolts"], lists["nuts"])


def machine():
    m = json.load(open(os.path.join(ROOT, "machine.json"), encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.5.0.sc"
    m["units"]["U8_PNEU"] = {
        "parts": ["STEP대기_IR1000", "STEP대기_KQ2L08", "STEP대기_SS5Y3", "STEP대기_SY3120", "STEP대기_CB4-20_M08", "KQ2L06-M5A_M08",
                  "STEP대기_F3SG", "HFS8-4080-2370_M08", "HFS8-4080-1900_M08", "HFC8-4080-B_M08", "P_M08_", "U8_HMI_PANEL",
                  "STEP대기_LR6", "HFS8-4080-570_M08", "STEP대기_KDM10-06_M08", "CB5-12_M08", "CB5-16_M08", "HNTT8-5_M08",
                  "TU0604_M08", "TU0805_M08"],
        "moving": False,
        "_note": "고정(REF_GROUND 리지드). M08(v2.5.0): 레귤레이터 IR1000 ×3(STEP대기)+KQ2L08 ×6, 밸브 SS5Y3-20-06+SY3120 ×6(STEP대기)+KQ2L06-M5A ×11, "
                 "라이트 커튼 F3SG ×4(STEP대기) + 기둥 HFS8-4080 2370·1900·1900 + 캡 6, 이음판·판금 L, 경광등 LR6(STEP대기), HMI 받침판·팔 570·패널 받침·패널 자리, "
                 "다관 커넥터 KDM10-06 고정 반쪽(플러그 반쪽은 U7_CASSETTE), 관 TU0805 ×6·TU0604 ×11(임시 직선+구). 옛 상자 U8_REG·LC_L·LC_R·LAMP·HMI 지움. 새 조인트 0"}
    json.dump(m, open(os.path.join(ROOT, "machine.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json U8_PNEU updated")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "machine":
        machine()
    else:
        main()
