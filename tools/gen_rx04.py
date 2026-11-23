# -*- coding: utf-8 -*-
"""RX-04 바늘 둘레 LED 조명 — 명령 생성기 (v2.24.0 -> v2.25.0).

좌표: 측정 좌표계 = 월드(바늘점 원점, 테이블 면 Z 0, mm).
설계안: docs/reports/mechanism/mech_RX-04_design.md
출력: tools/out/mech_RX-04/model/stage_*.json, tools/out/mech_RX-04/edit.json
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_RX-04", "model")
os.makedirs(OUT, exist_ok=True)
STEP = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def r4(v):
    return round(v, 4)


S3 = math.sqrt(3) / 2
D = (-0.5, -S3)          # 판 방향 d (Y, Z)
N = (S3, -0.5)           # 빛 면 법선 n (Y, Z)
B = (-52.0, 123.5)       # 굽힘선 안쪽


def P(s, t):
    return (B[0] + s * D[0] + t * N[0], B[1] + s * D[1] + t * N[1])


def yz_poly(name, body, pts, x0, x1, op, tg=None):
    s = [C("sketch.create", plane="YZ", offset=x0, name="SK_" + name),
         C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
         C("sketch.finish")]
    p = {"distance": r4(x1 - x0), "operation": op, "name": name}
    if op == "new":
        p["body_name"] = body
    else:
        p["targets"] = tg
    s.append(C("solid.extrude", **p))
    return s


def cyl(name, r, base, axis, h, op, tg=None, body=None):
    p = {"radius": r, "height": r4(h), "base": [r4(v) for v in base], "axis": [r4(v) for v in axis],
         "operation": op, "name": name}
    if tg:
        p["targets"] = tg
    if body:
        p["body_name"] = body
    return C("solid.cylinder", **p)


def box(name, body, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"corner": [x0, y0, z0], "length": r4(x1 - x0), "width": r4(y1 - y0), "height": r4(z1 - z0),
         "operation": op, "name": name}
    if op == "new":
        p["body_name"] = body
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def comp(body, parent, part, bom, desc, mat):
    return [C("material.assign", bodies=[body], material=mat),
            C("component.create", name=body, parent=parent, activate=False),
            C("component.move_bodies", bodies=[body], component=body),
            C("component.metadata.set", component=body, part_number=part, bom_type=bom, description=desc)]


BR = "P_RX04_LED_BRKT_SHT"
LED = "STEP대기_LEDBAR_L100"
CBL = "CBL_RX04_LED"
GRP = "U3_LED"

# ---------------------------------------------------------------- 단면 점
YZ_A2 = 125.0  # 바깥 꼭짓점: 판 뒷면(t -1.5) 선과 Z 125
_bk = P(0, -1.5)
_s = (_bk[1] - 125.0) / S3                    # Z: bk_z - 0.866 s = 125
A2 = (_bk[0] + _s * D[0], 125.0)
A3 = P(26, -1.5)
A4 = P(26, 11)
A5 = P(24.5, 11)
A6 = P(24.5, 0)
FL_X = (-28.0, 98.0)      # 플랜지 X (지시 -25~95 -> 장공 끝 살 3: 2절)
PL_X = (-15.0, 85.0)      # 경사 판 · 입술 · 램프 X

# ---------------------------------------------------------------- stage 1 브래킷
s1 = [C("component.activate", component="root"),
      C("component.create", name=GRP, parent="U3_HEAD", activate=False),
      C("component.metadata.set", component=GRP, bom_type="phantom",
        description="RX-04 needle area LED light group (bent SUS304 bracket + LED bar + 3 cable clips + cable + bolts) under head arm front")]
# 플랜지(Y A2 ~ -38, Z 123.5~125)
s1 += yz_poly("RX04_BRKT_FLANGE", BR, [(A2[0], 123.5), (-38, 123.5), (-38, 125), (A2[0], 125)], FL_X[0], FL_X[1], "new")
# 굽힘 + 경사 판 + 입술(+n 11, s 24.5~26) — 플랜지와 굽힘 삼각만 겹침
s1 += yz_poly("RX04_BRKT_PLATE", BR, [A2, A3, A4, A5, A6, B], PL_X[0], PL_X[1], "join", [BR])
# 플랜지 장공 4.5 × 10(X) — 중심 (-20, -45.5) · (90, -45.5)
s1 += [C("sketch.create", plane="XY", offset=123.4, name="SK_RX04_BRKT_SLOT"),
       C("sketch.slot.center_to_center", p0=[-22.75, -45.5], p1=[-17.25, -45.5], width=4.5),
       C("sketch.slot.center_to_center", p0=[87.25, -45.5], p1=[92.75, -45.5], width=4.5),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_RX04_BRKT_SLOT", distance=1.7, operation="cut", targets=[BR], name="RX04_BRKT_SLOT")]
# 경사 판 Ø3.4 ×2 (X -5 · 75, s 12.5), 법선 방향
for x in (-5, 75):
    b0 = P(12.5, -1.6)
    s1.append(cyl("RX04_BRKT_H_%d" % x, 1.7, [x, b0[0], b0[1]], [0, N[0], N[1]], 1.7, "cut", [BR]))
s1 += comp(BR, GRP, BR, "normal",
           "LED bar bracket, SUS304 sheet t1.5 (laser + 2 bends, inner R1.5 detail): flange X -28~98 on head arm underside Z 125 "
           "with 2 slots 4.5x10 (CB4-12), plate 120 deg down toward -Y (light normal (0,0.866,-0.5)), 26 long, lip 11 (+n) "
           "as glare shield; 2x D3.4 for CB3-10 into LED bar (RX-04)", "SUS304")

# ---------------------------------------------------------------- stage 2 LED 바 임시 형상
L = [P(5, 0), P(20, 0), P(20, 10), P(5, 10)]
s2 = [C("component.activate", component="root")]
s2 += yz_poly("RX04_LED_BODY", LED, L, PL_X[0], PL_X[1], "new")
for x in (-5, 75):
    b0 = P(12.5, -0.1)
    s2.append(cyl("RX04_LED_TAP_%d" % x, 1.25, [x, b0[0], b0[1]], [0, N[0], N[1]], 9.1, "cut", [LED]))
s2 += comp(LED, GRP, "LEDBAR-L100", "purchased",
           "STEP wait (E-10/E-12, D-229), dimensions temporary: Misumi small LED bar light L100 (part no. TBD), "
           "DC24V white diffuse, box 100 x 15 x 10, light face = +n face (normal (0,0.866,-0.5)), 2x M3 tap depth 9 in base "
           "X -5/75 (temp), cable OD4 (CBL_RX04_LED) from -X end (RX-04)", "Default")
fc = P(12.5, 10)
s2.append(C("appearance.assign", bodies=[LED], color="#f4f4f0"))

# ---------------------------------------------------------------- stage 3 케이블 클립 ×3 + 케이블
CLIPS = [("P_RX04_CBL_CLIP_PRT_1", "Z", -18.0), ("P_RX04_CBL_CLIP_PRT_2", "Z", 60.0), ("P_RX04_CBL_CLIP_PRT_3", "Y", 165.0)]
CX, CR, CRI, HX = -22.0, 3.6, 2.1, -15.0
s3 = [C("component.activate", component="root")]
for nm, kind, c in CLIPS:
    if kind == "Z":   # 암 밑면, 케이블 축 Y(Z 121)
        s3 += [box(nm + "_BASE", nm, -25.5, -12.0, c - 5, c + 5, 122, 125),
               cyl(nm + "_RING", CR, [CX, c - 5, 121], [0, 1, 0], 10, "join", [nm]),
               cyl(nm + "_GROOVE", CRI, [CX, c - 5.1, 121], [0, 1, 0], 10.2, "cut", [nm]),
               cyl(nm + "_HOLE", 1.7, [HX, c, 121.9], [0, 0, 1], 3.2, "cut", [nm])]
    else:             # 암 뒷면 Y 90, 케이블 축 Z(Y 95)
        s3 += [box(nm + "_BASE", nm, -25.5, -12.0, 90, 93, c - 5, c + 5),
               cyl(nm + "_RING", CR, [CX, 95, c - 5], [0, 0, 1], 10, "join", [nm]),
               cyl(nm + "_GROOVE", CRI, [CX, 95, c - 5.1], [0, 0, 1], 10.2, "cut", [nm]),
               cyl(nm + "_HOLE", 1.7, [HX, 89.9, c], [0, 1, 0], 3.2, "cut", [nm])]
    s3 += comp(nm, GRP, "P_RX04_CBL_CLIP_PRT", "normal",
               "Cable saddle clip, PA12 3D print: base 13.5 x 10 x 3 + ring OD7.2 around cable D4.2 + D3.4 hole for CB3-10 "
               "into head arm M3 tap (RX-04)", "PA12")

# 케이블 길: (-15,-55,112) -> R5 -> (-22,-50,112) -> (-22,-41,112) -> S R10 x2 (Z +9) -> (-22,-24.30,121)
#           -> (-22,87,121) -> R8 -> (-22,95,129) -> (-22,95,200)
th = math.acos(0.55)
sy, sh = 10 * math.sin(th), 10 * math.sin(th / 2)
q1 = (-41 + sy, 116.5)
q2 = (-41 + 2 * sy, 121.0)
pts = [
    ("l", (-15, -55, 112), (-17, -55, 112)),
    ("a", (-17, -55, 112), (-17 - 5 * math.cos(math.pi / 4), -50 - 5 * math.sin(math.pi / 4), 112), (-22, -50, 112)),
    ("l", (-22, -50, 112), (-22, -41, 112)),
    ("a", (-22, -41, 112), (-22, -41 + sh, 122 - 10 * math.cos(th / 2)), (-22, q1[0], q1[1])),
    ("a", (-22, q1[0], q1[1]), (-22, q2[0] - sh, 111 + 10 * math.cos(th / 2)), (-22, q2[0], q2[1])),
    ("l", (-22, q2[0], q2[1]), (-22, 87, 121)),
    ("a", (-22, 87, 121), (-22, 87 + 8 * math.sin(math.pi / 4), 129 - 8 * math.cos(math.pi / 4)), (-22, 95, 129)),
    ("l", (-22, 95, 129), (-22, 95, 200)),
]
s3 += [C("sketch.create", plane="XY", name="SK_CBL_RX04_LED"), C("sketch.options", sketch_3d=True)]
for e in pts:
    if e[0] == "l":
        s3.append(C("sketch.line3d", points=[[r4(v) for v in e[1]], [r4(v) for v in e[2]]]))
    else:
        s3.append(C("sketch.arc3d", start=[r4(v) for v in e[1]], through=[r4(v) for v in e[2]], end=[r4(v) for v in e[3]]))
s3 += [C("sketch.finish"),
       C("solid.pipe", path_sketch="SK_CBL_RX04_LED", path=["w%d" % (i + 1) for i in range(len(pts))], diameter=4.0,
         operation="new", body_name=CBL, name="PIPE_CBL_RX04_LED")]
s3 += comp(CBL, GRP, "LEDBAR-L100", "reference",
           "LED bar cable OD4 (temp, D-229), body only - counted in LEDBAR-L100 purchased row: LED -X end -> under bracket "
           "flange Z 112 -> S up to Z 121 under arm (clips 1, 2) -> behind arm Y 95 up to Z 200 (clip 3) -> beam / electrics U-09 (RX-04)",
           "Default")
s3.append(C("appearance.assign", bodies=[CBL], color="#202020"))

# ---------------------------------------------------------------- stage 4 헤드 암 탭(이력 끝)
s4 = [C("component.activate", component="U3_HEAD")]
for x in (-20, 90):
    s4.append(cyl("RX04_ARM_M4_TAP_%d" % x, 1.65, [x, -45.5, 124.9], [0, 0, 1], 12.1, "cut", ["STEP대기_867-392342_UPPER"]))
for nm, kind, c in CLIPS:
    if kind == "Z":
        s4.append(cyl("RX04_ARM_M3_TAP_Y%d" % int(c), 1.25, [HX, c, 124.9], [0, 0, 1], 10.1, "cut", ["STEP대기_867-392342_UPPER"]))
    else:
        s4.append(cyl("RX04_ARM_M3_TAP_Z%d" % int(c), 1.25, [HX, 90.1, c], [0, -1, 0], 10.1, "cut", ["STEP대기_867-392342_UPPER"]))
s4.append(C("component.activate", component="root"))

# ---------------------------------------------------------------- stage 5 볼트(실물 STEP)
def bolt(name, spec, R, t, desc):
    # R: 열 = 로컬 x(볼트 축, 좌면 0 -> 끝), 로컬 y, 로컬 z 의 월드 방향
    m = [R[0][0], R[1][0], R[2][0], t[0], R[0][1], R[1][1], R[2][1], t[1], R[0][2], R[1][2], R[2][2], t[2]]
    m = [round(v, 12) for v in m]   # r4로 자르면 강체가 아니라고 거부됨(|RᵀR − I| 4.4e-5)
    return [C("file.insert_step", path=STEP + "%s/%s.stp" % (spec, spec), name=name, matrix=m),
            C("body.rename", body="Cut-Extrude1", name=name),
            C("component.metadata.set", component=name, part_number=spec, bom_type="purchased", description=desc),
            C("material.assign", bodies=[name], material="SCM435"),
            C("occurrence.reparent", occurrence=name + ":1", parent=GRP)]


UPZ = ((0, 0, 1), (0, 1, 0), (-1, 0, 0))
ALN = ((0, N[0], N[1]), (1, 0, 0), (0, D[0], D[1]))
MY = ((0, -1, 0), (1, 0, 0), (0, 0, 1))
BOLTS = [("CB4-12_RX04_1", "CB4-12", UPZ, (-20, -45.5, 123.5), "Misumi CB4-12 STEP, RX-04 LED bracket flange slot -> head arm M4 tap (from below)"),
         ("CB4-12_RX04_2", "CB4-12", UPZ, (90, -45.5, 123.5), "Misumi CB4-12 STEP, RX-04 LED bracket flange slot -> head arm M4 tap (from below)")]
for i, x in enumerate((-5, 75)):
    p = P(12.5, -1.5)
    BOLTS.append(("CB3-10_RX04_L%d" % (i + 1), "CB3-10", ALN, (x, p[0], p[1]),
                  "Misumi CB3-10 STEP, RX-04 bracket plate -> LED bar M3 tap (from plate back, +n)"))
for i, (nm, kind, c) in enumerate(CLIPS):
    if kind == "Z":
        BOLTS.append(("CB3-10_RX04_C%d" % (i + 1), "CB3-10", UPZ, (HX, c, 122), "Misumi CB3-10 STEP, RX-04 cable clip -> head arm underside M3 tap"))
    else:
        BOLTS.append(("CB3-10_RX04_C%d" % (i + 1), "CB3-10", MY, (HX, 93, c), "Misumi CB3-10 STEP, RX-04 cable clip -> head arm back M3 tap (-Y)"))
s5 = [C("component.activate", component="root")]
for b in BOLTS:
    s5 += bolt(b[0], b[1], b[2], b[3], b[4])

# ---------------------------------------------------------------- stage 6 리지드
s6 = [C("joint.rigid_group", occurrences=["U3_HEAD:1", GRP + ":1"] + [b[0] + ":1" for b in BOLTS])]

stages = [("1_bracket", s1), ("2_led", s2), ("3_clips_cable", s3), ("4_arm_taps", s4), ("5_bolts", s5), ("6_rigid", s6)]
allc = []
for nm, s in stages:
    json.dump(s, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    allc += s
json.dump(allc, open(os.path.join(ROOT, "out", "mech_RX-04", "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# 기대값
def area(poly):
    a = 0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


fl = (-38 - A2[0]) * 1.5
pl = area([A2, A3, A4, A5, A6, B])
tri = area([B, A2, (A2[0], 123.5)])
v_br = fl * (FL_X[1] - FL_X[0]) + (pl - tri) * (PL_X[1] - PL_X[0])
slot = 2 * (4.5 * 5.5 + math.pi * 2.25 ** 2) * 1.5
v_br -= slot + 2 * math.pi * 1.7 ** 2 * 1.5
v_led = 15 * 10 * 100 - 2 * math.pi * 1.25 ** 2 * 9
print("A2", A2, "A3", A3, "A4", A4, "A5", A5, "A6", A6)
print("bracket vol %.1f  led vol %.1f" % (v_br, v_led))
print("lamp corners", [tuple(round(v, 2) for v in p) for p in L], "face center", fc)
print("cmds", len(allc), [(n, len(s)) for n, s in stages])
