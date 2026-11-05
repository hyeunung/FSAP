# -*- coding: utf-8 -*-
"""M07 U1 프레임 + 보 생성기 — 기준 3D_Modeling/FSAP_v2.3.2.sc -> 3D_Modeling/FSAP_v2.3.3.sc (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M07_design.md + 모델링 지시서. 보고서 docs/reports/mechanism/mech_M07_model.md.
python -X utf8 -B tools/gen_v2_m07.py          -> tools/out/mech_M07/model/stage_*.json, tools/out/mech_M07/edit.json, lists.json
python -X utf8 -B tools/gen_v2_m07.py machine  -> tools/machine.json U1_FRAME 고침
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm. U1은 고정(새 조인트 0). 모든 새 부품은 U1_FRAME 아래.
반복 구매품(형재 같은 길이, 캡, 브래킷, T너트, 볼트, STEP대기 레벨러)은 방향마다 한 컴포넌트를 두고
occurrence.copy(in_place, 세계 이동)로 놓는다(M04와 같은 길).
지시와 다른 곳: 다리 브래킷 16(지시 18) -> 브래킷 55(지시 57). 가운데 줄 끝 다리 2곳은 X 부재 끝과 같은 면이라 구석이 하나뿐.
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cz, cy, mat_assign  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUTT = os.path.join(ROOT, "out", "mech_M07")
OUT = os.path.join(OUTT, "model")
STEP = PRJ + "/purchased-step/"
U1 = "U1_FRAME"
BEAM_OLD, BEAM = "U1_BEAM", "P_M07_BEAM"
SEAT = {"NX": "P_M07_SEAT_NX", "PX": "P_M07_SEAT_PX"}
SPL = {"NX": "P_M07_SPLICE_NX", "PX": "P_M07_SPLICE_PX"}
COL = {"NX": "STEP대기_HFS8-80160-1482_M07_NX", "PX": "STEP대기_HFS8-80160-1482_M07_PX"}
COLCAP = {"NX": "STEP대기_HFC8-80160-B_M07_NX", "PX": "STEP대기_HFC8-80160-B_M07_PX"}
LEV = "STEP대기_LEVELER_M8_M07"


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


def plane(origin, xd, yd):
    return {"origin": list(origin), "x_dir": list(xd), "y_dir": list(yd)}


def XY(z):
    return plane((0, 0, z), (1, 0, 0), (0, 1, 0))


def XZ(y):
    return plane((0, y, 0), (1, 0, 0), (0, 0, 1))      # 법선 -Y, (u, v) = (X, Z)


def YZ(x):
    return plane((x, 0, 0), (0, 1, 0), (0, 0, 1))      # 법선 +X, (u, v) = (Y, Z)


def tag(v):
    return "".join(("P" if c > 0 else "N") + "XYZ"[i] for i, c in enumerate(v) if c)


def copy(occ, d):
    return C("occurrence.copy", occurrence=occ, in_place=True, translate=[r4(v) for v in d])


def insert_group(path, comp, cols, places, src_body, pn, desc=None, mat=None, offset=None):
    """첫 자리에 STEP을 넣고(세계 자리 행렬), 바디 이름·끝면 늘이기·메타·재질 뒤 U1_FRAME 아래로 옮기고 나머지는 세계 이동 복사."""
    p0 = places[0]
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=mrow(*cols, p0)),
         C("body.rename", body=src_body, name=comp)]
    if offset:
        # 끝면(로컬 X 1140) 위 점: STEP 실측 model.faces face 0 point (1140, 6.3472, 18.5178) — 이름(F<n>:face:0)은 문서마다 달라 점으로 집는다
        lx, ly, lz = cols
        fp = [r4(p0[i] + 1140 * lx[i] + 6.3472 * ly[i] + 18.5178 * lz[i]) for i in range(3)]
        s.append(C("solid.offset_face", faces=[fp], distance=r4(offset), body=comp))
    md = {"component": comp, "part_number": pn, "bom_type": "purchased"}
    if desc:
        md["description"] = desc
    s.append(C("component.metadata.set", **md))
    if mat:
        s.append(mat_assign([comp], mat))
    s.append(C("occurrence.reparent", occurrence=comp + ":1", parent=U1))
    s += [copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def tmp_comp(comp, body_cmds, places, pn, desc, mat):
    """STEP대기 임시 형상 컴포넌트: 첫 자리에 그려 U1_FRAME 아래 새 컴포넌트로 옮기고 나머지는 복사."""
    p0 = places[0]
    s = [C("component.create", name=comp, parent=U1, activate=False)]
    s += body_cmds(p0)
    s += [mat_assign([comp], mat), C("component.move_bodies", bodies=[comp], component=comp),
          C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc)]
    s += [copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def hole_cut(name, pl, centers, r, dist, body):
    s = [C("sketch.create", plane=pl, name=name)]
    s += [C("sketch.circle.center", center=[r4(a), r4(b)], radius=r) for a, b in centers]
    s.append(C("sketch.finish"))
    s.append(C("solid.extrude", sketch=name, distance=dist, operation="cut", targets=[body]))
    return s


# ====================================================================== A. 보
def stage_beam():
    s = []
    # 바깥: 큰 사각(Y 110~430, Z 240~660)과 둥근 사각(Y 120~320, Z 250~650, R12) 사이 띠를 잘라냄 = Y 320~420 띠 + 바깥 R12
    s += [C("sketch.create", plane=YZ(-2301), name="SK_M07_BEAM_OUT"),
          C("sketch.rectangle.two_point", p0=[110, 240], p1=[430, 660]),
          C("sketch.rectangle.rounded", p0=[120, 250], p1=[320, 650], radius=12),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M07_BEAM_OUT", distance=3452, operation="cut", targets=[BEAM_OLD],
            profiles=[{"point": [115, 450]}])]
    # 속: Y 128~312, Z 258~642, 안 R4, 양 끝 열림
    s += [C("sketch.create", plane=YZ(-2301), name="SK_M07_BEAM_IN"),
          C("sketch.rectangle.rounded", p0=[128, 258], p1=[312, 642], radius=4),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M07_BEAM_IN", distance=3452, operation="cut", targets=[BEAM_OLD])]
    # 새 M5 탭 Ø4.2 관통·공구 구멍 Ø10 — 큰 문서에서 원기둥 자르기 하나가 4~6 s라 면마다 스케치 한 번으로 자른다
    s += hole_cut("SK_M07_BEAM_HB", XY(249.9), [(x, y) for x in (-2265, -2225, 1075, 1115) for y in (160, 280)], 2.1, 8.2, BEAM_OLD)
    s += hole_cut("SK_M07_BEAM_HK", XZ(320.1), [(x, z) for x in (-2260, -2220, 1070, 1110) for z in (300, 600)], 2.1, 8.2, BEAM_OLD)
    s += hole_cut("SK_M07_BEAM_HT", XZ(128.1), [(-2244.75, 365.25), (-2244.75, 414.75), (-2195.25, 365.25), (-2195.25, 414.75)], 5.0, 8.2, BEAM_OLD)
    s += [C("body.rename", body=BEAM_OLD, name=BEAM), mat_assign([BEAM], "Steel")]
    return s


# ====================================================================== B. 기둥
def col_main(side):
    x0 = -2380.0 if side == "NX" else 1150.0
    x1 = x0 + 80
    nm = COL[side]
    z0, z1 = -841.0, 643.0
    # 단면(80 x 160, 8계열 T홈 자리, E-10 임시) 한 윤곽을 밀어 한 바디로. 160 면 홈: 입구 10 x 5.5, 속 18 x 5.5~12(T너트 17 들어감),
    # 80 면 홈: 입구 10 x 5.5, 속 18 x 5.5~10.5(모서리에서 두 속이 맞붙지 않게 0.5 띄움)
    pts = [(x0, 120.0)]
    for xc in (x0 + 20, x0 + 60):
        pts += [(xc - 5, 120), (xc - 5, 125.5), (xc - 9, 125.5), (xc - 9, 130.5), (xc + 9, 130.5), (xc + 9, 125.5), (xc + 5, 125.5), (xc + 5, 120)]
    pts.append((x1, 120.0))
    for y in (140, 180, 220, 260):
        pts += [(x1, y - 5), (x1 - 5.5, y - 5), (x1 - 5.5, y - 9), (x1 - 12, y - 9), (x1 - 12, y + 9), (x1 - 5.5, y + 9), (x1 - 5.5, y + 5), (x1, y + 5)]
    pts.append((x1, 280.0))
    for xc in (x0 + 60, x0 + 20):
        pts += [(xc + 5, 280), (xc + 5, 274.5), (xc + 9, 274.5), (xc + 9, 269.5), (xc - 9, 269.5), (xc - 9, 274.5), (xc - 5, 274.5), (xc - 5, 280)]
    pts.append((x0, 280.0))
    for y in (260, 220, 180, 140):
        pts += [(x0, y + 5), (x0 + 5.5, y + 5), (x0 + 5.5, y + 9), (x0 + 12, y + 9), (x0 + 12, y - 9), (x0 + 5.5, y - 9), (x0 + 5.5, y - 5), (x0, y - 5)]
    sk = "SK_M07_COL_" + side
    s = [C("sketch.create", plane=XY(-840), name=sk), C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
         C("sketch.finish"), C("solid.extrude", sketch=sk, distance=1482, operation="new", body_name=nm)]
    s.append(box(COLCAP[side], x0, x1, 120, 280, 642, 650))
    return s


AUX_COLS = ((0, 0, 1), (1, 0, 0), (0, 1, 0))       # 4080 로컬 X(길이) -> +Z, 로컬 Y(80) -> X, 로컬 Z(40) -> Y
AUX = [  # (컴포넌트, 길이, 밑 Z)
    ("HFS8-4080-1482_M07_NX", 1482, -840.0, (-2340.0, 300.0)),
    ("HFS8-4080-1482_M07_PX", 1482, -840.0, (1190.0, 300.0)),
]


def stage_columns():
    s = col_main("NX") + col_main("PX")
    s += [mat_assign([COL["NX"], COL["PX"]], "Aluminum"), mat_assign([COLCAP["NX"], COLCAP["PX"]], "Default"),
          C("component.move_bodies", bodies=[COL["NX"], COL["PX"], COLCAP["NX"], COLCAP["PX"]], component=U1)]
    for comp, L, z0, (x, y) in AUX:
        s += insert_group("HFS8-4080-1140/HFS8-4080-1140.stp", comp, AUX_COLS, [(x, y, z0)], "Boss-Extrude1",
                          "HFS8-4080-%d" % L, "Misumi HFS8-4080-1140 STEP, end face offset to L%d" % L, "Aluminum", L - 1140)
    return s


# ====================================================================== C. 보-기둥 이음
def stage_joints_plates():
    s = [C("sheet.manage_rules", name="SS400_t9", thickness="9", bend_radius="9", k_factor="0.44",
           relief_width="1", relief_depth="1.5", active=True)]
    for side in ("NX", "PX"):
        if side == "NX":
            hx0, hx1, ex, sx0, sx1 = -2300, -2200, -2300, -2380, -2200
            hh, vx, sh, sb = (-2265, -2225), (-2301, -2290), (-2360, -2320), (-2260, -2220)
        else:
            hx0, hx1, ex, sx0, sx1 = 1050, 1150, 1150, 1060, 1230
            hh, vx, sh, sb = (1075, 1115), (1140, 1151), (1170, 1210), (1070, 1110)
        nm = SEAT[side]
        s += [C("sketch.create", plane=XY(241), name="SK_M07_SEAT_" + side),
              C("sketch.line", points=[[hx0, 130], [hx1, 130], [hx1, 310], [hx0, 310]], closed=True),
              C("sketch.finish"),
              C("sheet.flange", type="base", sketch="SK_M07_SEAT_" + side, rule="SS400_t9", body_name=nm),
              C("sheet.flange", type="edge", edges=[[ex, 220, 241]], height=100, angle=90, body=nm)]
        # 판금 구멍은 스케치 평행 밀어 자르기로(solid.cylinder는 판금 전개를 못 지켜 거부됨)
        s += hole_cut("SK_M07_SEAT_%s_H" % side, XY(240), [(x, y) for x in hh for y in (160, 280)], 2.75, 11, nm)
        s += hole_cut("SK_M07_SEAT_%s_V" % side, YZ(vx[0]), [(y, z) for y in (140, 220, 300) for z in (175, 220)], 2.75, vx[1] - vx[0], nm)
        sp = SPL[side]
        s.append(box(sp, sx0, sx1, 320, 326, 260, 640))
        s += [cy(2.75, x, z, 319.9, 326.1, "cut", [sp]) for x in sb + sh for z in (300, 600)]
    s += [mat_assign([SEAT["NX"], SEAT["PX"], SPL["NX"], SPL["PX"]], "Steel"),
          C("component.move_bodies", bodies=[SEAT["NX"], SEAT["PX"], SPL["NX"], SPL["PX"]], component=U1)]
    return s


# ====================================================================== D. 받침틀
XM_COLS = ((1, 0, 0), (0, 0, 1), (0, -1, 0))       # X 부재: 길이 X, 80 -> Z, 40 -> Y
YM_COLS = ((0, 1, 0), (0, 0, 1), (1, 0, 0))        # Y 부재: 길이 Y, 80 -> Z, 40 -> X
LEG_COLS = AUX_COLS                                # 다리: 길이 Z, 80 -> X, 40 -> Y
YM_X = [-2280, -2135, -1535, -935, -440, 360, 565, 955, 1130]
LEG_X = [-2260, -440, 1110]
XMEM = [(-1500.0, -290.0), (1500.0, -290.0), (0.0, -370.0)]   # (Y 중심, Z 중심): XF, XB, XM


def stage_base():
    s = []
    s += insert_group("HFS8-4080-1140/HFS8-4080-1140.stp", "HFS8-4080-3450_M07", XM_COLS,
                      [(-2300.0, y, z) for y, z in XMEM], "Boss-Extrude1", "HFS8-4080-3450",
                      "Misumi HFS8-4080-1140 STEP, end face offset to L3450", "Aluminum", 3450 - 1140)
    s += insert_group("HFS8-4080-1140/HFS8-4080-1140.stp", "HFS8-4080-2960_M07", YM_COLS,
                      [(x, -1480.0, -290.0) for x in YM_X], "Boss-Extrude1", "HFS8-4080-2960",
                      "Misumi HFS8-4080-1140 STEP, end face offset to L2960", "Aluminum", 2960 - 1140)
    s += insert_group("HFS8-4080-1140/HFS8-4080-1140.stp", "HFS8-4080-510_M07", LEG_COLS,
                      [(x, y, -840.0) for x in LEG_X for y in (-1500.0, 1500.0)], "Boss-Extrude1", "HFS8-4080-510",
                      "Misumi HFS8-4080-1140 STEP, end face offset to L510", "Aluminum", 510 - 1140)
    s += insert_group("HFS8-4080-1140/HFS8-4080-1140.stp", "HFS8-4080-430_M07", LEG_COLS,
                      [(x, 0.0, -840.0) for x in LEG_X], "Boss-Extrude1", "HFS8-4080-430",
                      "Misumi HFS8-4080-1140 STEP, end face offset to L430", "Aluminum", 430 - 1140)
    return s


def cap_places():
    W = [(-2300.0, y, z) for y, z in XMEM]
    E = [(1150.0, y, z) for y, z in XMEM]
    T = [(-2340.0, 300.0, 642.0), (1190.0, 300.0, 642.0)]
    return {"W": (((0, 0, 1), (0, 1, 0), (-1, 0, 0)), W), "E": (((0, 0, 1), (0, -1, 0), (1, 0, 0)), E),
            "T": (((1, 0, 0), (0, 1, 0), (0, 0, 1)), T)}


def stage_caps():
    s = []
    for k, (cols, pl) in cap_places().items():
        comp = "HFC8-4080-B_M07_" + k
        s += insert_group("HFC8-4080-B/HFC8-4080-B.stp", comp, cols, pl, "Fillet2", "HFC8-4080-B", mat="Default")
    return s


def lev_places():
    pl = [(x, y, -900.0) for x in LEG_X for y in (-1500.0, 0.0, 1500.0)]
    pl += [(x, y, -900.0) for x in (-2340.0, 1190.0) for y in (160.0, 240.0, 300.0)]
    return pl


def stage_levelers():
    def lev(p):
        x, y = p[0], p[1]
        return [cz(20.0, x, y, -900.0, -890.0, "new", None, LEV), cz(4.0, x, y, -890.0, -840.0, "join", [LEV])]
    return tmp_comp(LEV, lev, lev_places(), "LEVELER-M8", "placeholder leveling foot M8 (pad 40x10, stud M8x50), Misumi ADJ series part number TBD", "Steel")


# ---------------------------------------------------------------- 브래킷·볼트·너트
def brackets():
    """(구석 점 o, n1 = 다리 A 붙는 면 바깥 법선, n2 = 다리 B 붙는 면 바깥 법선, 면1 홈 방향, 면2 홈 방향, 무리)."""
    B = []
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    NX_, NY_, NZ_ = (-1, 0, 0), (0, -1, 0), (0, 0, -1)
    # (1) Y 부재 끝 <-> 앞뒤 X 부재 안면(세로 구석, 홈 Z -270/-310)
    for xc in YM_X:
        sgn = -1 if xc == 1130 else 1
        zs = (-270.0, -310.0) if xc in (-2280, 1130) else (-270.0,)
        for yf, n1 in ((-1480.0, Y), (1480.0, NY_)):
            for zc in zs:
                B.append(((xc + 20 * sgn, yf, zc), n1, (sgn, 0, 0), X, Y, "YX"))
    # (2) Y 부재 <-> 가운데 X 부재 윗면(Y 0)
    for xc in YM_X:
        sgn = -1 if xc == 1130 else 1
        B.append(((xc + 20 * sgn, 0.0, -330.0), (sgn, 0, 0), Z, Y, X, "YM"))
    # (3) 다리 <-> 부재 밑면
    for xl in LEG_X:
        faces = {-2260: (1,), -440: (1, -1), 1110: (-1,)}[xl]
        for yl, zb in ((-1500.0, -330.0), (1500.0, -330.0), (0.0, -410.0)):
            for sd in faces:
                B.append(((xl + 40 * sd, yl, zb), NZ_, (sd, 0, 0), X, Z, "LEG"))
            if yl != 0.0 and xl in (-2260, 1110):
                xs = -2280.0 if xl == -2260 else 1130.0
                yf = -1480.0 if yl < 0 else 1480.0
                B.append(((xs, yf, -330.0), NZ_, (0, 1, 0) if yl < 0 else NY_, Y, Z, "LEGY"))
    # (4) 기둥 <-> 끝 Y 부재 윗면·밑면
    for xf, n2 in ((-2300.0, X), (1150.0, NX_)):
        for y in (180.0, 300.0):
            B.append(((xf, y, -250.0), Z, n2, Y, Z, "COL"))
        for y in (180.0, 260.0):
            B.append(((xf, y, -330.0), NZ_, n2, Y, Z, "COL"))
    return B


def fasteners():
    """브래킷·받침·이음판의 볼트(형번, 머리 밑 점, 축)·너트(점, 법선, 홈 방향)."""
    bolts, nuts, brk = [], [], []
    for o, n1, n2, s1, s2, kind in brackets():
        lz, ly = n1, n2
        lx = cross(ly, lz)
        brk.append((o, (lx, ly, lz), kind))
        p = add(o, n2, 20)           # 다리 A 구멍(면1 위)
        bolts.append(("CB5-12", add(p, n1, 9.0), tuple(-v for v in n1), "BRK-" + kind + "-A"))
        nuts.append((add(p, n1, -2.5), n1, s1))
        q = add(o, n1, 30)           # 다리 B 구멍(면2 위)
        bolts.append(("CB5-12", add(q, n2, 8.2), tuple(-v for v in n2), "BRK-" + kind + "-B"))
        nuts.append((add(q, n2, -2.5), n2, s2))
    for side in ("NX", "PX"):
        if side == "NX":
            hh, vf, vd, sb, sh = (-2265, -2225), -2291.0, (-1, 0, 0), (-2260, -2220), (-2360, -2320)
        else:
            hh, vf, vd, sb, sh = (1075, 1115), 1141.0, (1, 0, 0), (1070, 1110), (1170, 1210)
        for x in hh:
            for y in (160, 280):
                bolts.append(("CB5-20", (x, y, 241.0), (0, 0, 1), "SEAT-H-" + side))
        cf = vf + 9 * vd[0]          # 기둥 안쪽 면
        for y in (140, 220, 300):
            for z in (175, 220):
                bolts.append(("CB5-12", (vf, y, z), vd, "SEAT-V-" + side))
                nuts.append(((cf + 2.5 * vd[0], y, z), (-vd[0], 0, 0), (0, 0, 1)))
        for x in sb:
            for z in (300, 600):
                bolts.append(("CB5-16", (x, 326.0, z), (0, -1, 0), "SPL-B-" + side))
        for x in sh:
            for z in (300, 600):
                bolts.append(("CB5-12", (x, 326.0, z), (0, -1, 0), "SPL-C-" + side))
                nuts.append(((x, 317.5, z), (0, 1, 0), (0, 0, 1)))
    return bolts, nuts, brk


def stage_brackets():
    _, _, brk = fasteners()
    groups = {}
    for o, cols, kind in brk:
        groups.setdefault(cols, []).append(o)
    s = []
    for cols, pl in groups.items():
        comp = "HBLFSN8_M07_%s_%s" % (tag(cols[2]), tag(cols[1]))
        s += insert_group("HBLFSN8/HBLFSN8.stp", comp, cols, pl, "NONE", "HBLFSN8", mat="Aluminum")
    return s, groups


def stage_nuts():
    _, nuts, _ = fasteners()
    groups = {}
    for p, n, sd in nuts:
        cols = (tuple(sd), tuple(n), cross(sd, n))
        groups.setdefault(cols, []).append(p)
    s = []
    for cols, pl in groups.items():
        comp = "HNTT8-5_M07_%s_%s" % (tag(cols[1]), tag(cols[0]))
        s += insert_group("HNTT8-5/HNTT8-5.stp", comp, cols, pl, "Tap1", "HNTT8-5", mat="Steel")
    return s, groups


def stage_bolts():
    bolts, _, _ = fasteners()
    groups = {}
    for pn, p, d, _k in bolts:
        groups.setdefault((pn, tuple(d)), []).append(p)
    s = []
    for (pn, d), pl in groups.items():
        cols = (d, perp(d), cross(d, perp(d)))
        comp = "%s_M07_%s" % (pn, tag(d))
        s += insert_group("%s/%s.stp" % (pn, pn), comp, cols, pl, "Cut-Extrude1", pn, mat="SCM435")
    return s, groups


def stage_prep():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("solid.remove", bodies=["U1_COL_NX", "U1_COL_PX", "U1_BASE"])]


def stage_final(rigid):
    return [C("joint.rigid_group", occurrences=["U1_FRAME:1"] + rigid),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M07 mechanism: U1 frame - STKR400 400x200x8 beam, HFS8 columns, SS400 seat L and splice plates, HFS8-4080 base frame")]


def main():
    os.makedirs(OUT, exist_ok=True)
    sb, gb = stage_brackets()
    sn, gn = stage_nuts()
    so, go = stage_bolts()
    # STEP 안 리지드 묶음이 바닥에 안 이어지는 일(M04 HBLFSN8)을 막으려고 넣은 컴포넌트 :1을 U1_FRAME과 묶는다
    rigid = ["HBLFSN8_M07_%s_%s:1" % (tag(c[2]), tag(c[1])) for c in gb]
    stages = [("1_prep", stage_prep()), ("2_beam", stage_beam()), ("3_columns", stage_columns()),
              ("4_plates", stage_joints_plates()), ("5_base", stage_base()), ("6_caps", stage_caps()),
              ("7_levelers", stage_levelers()), ("8_brackets", sb), ("9_nuts", sn), ("10_bolts", so),
              ("11_final", stage_final(rigid))]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st))
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.3.2.sc", "result": "3D_Modeling/FSAP_v2.3.3.sc", "generator": "tools/gen_v2_m07.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))
    bolts, nuts, brk = fasteners()
    kinds = {}
    for o, cols, k in brk:
        kinds[k] = kinds.get(k, 0) + 1
    bk = {}
    for pn, p, d, k in bolts:
        bk[pn] = bk.get(pn, 0) + 1
    lists = {"brackets": len(brk), "bracket_kinds": kinds, "bracket_comps": {"HBLFSN8_M07_%s_%s" % (tag(c[2]), tag(c[1])): len(v) for c, v in gb.items()},
             "nuts": len(nuts), "nut_comps": {"HNTT8-5_M07_%s_%s" % (tag(c[1]), tag(c[0])): len(v) for c, v in gn.items()},
             "bolts": bk, "bolt_comps": {"%s_M07_%s" % (k[0], tag(k[1])): len(v) for k, v in go.items()},
             "levelers": len(lev_places()), "caps": {k: len(v[1]) for k, v in cap_places().items()},
             "bolt_list": [{"spec": pn, "seat": list(p), "axis": list(d), "kind": k} for pn, p, d, k in bolts],
             "nut_list": [{"pos": list(p), "normal": list(n), "slot": list(sd)} for p, n, sd in nuts],
             "bracket_list": [{"corner": list(o), "lz": list(c[2]), "ly": list(c[1]), "kind": k} for o, c, k in brk],
             "commands": len(allc)}
    json.dump(lists, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in lists.items() if not k.endswith("_list")}, ensure_ascii=False))


def machine():
    m = json.load(open(os.path.join(ROOT, "machine.json"), encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.3.3.sc"
    m["units"]["U1_FRAME"] = {
        "parts": ["P_M07_", "STEP대기_HFS8-80160", "STEP대기_HFC8-80160", "HFS8-4080-", "HFC8-4080-B_M07", "HBLFSN8_M07",
                  "HNTT8-5_M07", "CB5-12_M07", "CB5-16_M07", "CB5-20_M07", "STEP대기_LEVELER_M8_M07", "REF_"],
        "moving": False,
        "_note": "고정(접지). M07(v2.3.3): 보 P_M07_BEAM(STKR400 400x200x8, X -2300~1150·Y 120~320·Z 250~650), 기둥 80160(STEP대기)+4080 양쪽, "
                 "받침 L P_M07_SEAT_NX/PX(SS400 t9 판금)·뒤 이음판 P_M07_SPLICE_NX/PX(SS400 t6), 받침틀 HFS8-4080 X 3·Y 9·다리 9, 레벨링 풋 15(STEP대기), "
                 "HBLFSN8 55, CB5-12/16/20 + HNTT8-5. 옛 상자 U1_BEAM(고쳐 이름 바꿈)·U1_COL_NX·U1_COL_PX·U1_BASE 지움. 새 조인트 0"}
    json.dump(m, open(os.path.join(ROOT, "machine.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json U1_FRAME updated")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "k1":
        # 구동 후보 M07-K1(2026-11-05, 받침틀 브래킷 판금 L + CB5-16, 보고서 mech_M07-K1_model.md)은 tools/gen_v2_m07k1.py에 있다
        import gen_v2_m07k1
        gen_v2_m07k1.main()
    elif len(sys.argv) > 1 and sys.argv[1] == "machine":
        machine()
    else:
        main()
