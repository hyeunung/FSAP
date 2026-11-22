# -*- coding: utf-8 -*-
"""RX-14 생성기 — U7 테이프 길을 테이블 면으로 (v2.18.0 -> v2.19.0, 설계안 mech_RX-14_design.md + design1.md)

python -X utf8 -B tools/gen_rx14.py
  출력: tools/out/mech_RX-14/model/stage_3_*.json … (MCP batch·CLI run이 받는 명령 배열)
좌표: 측정 좌표계 = 모델 좌표(바늘점 원점, 테이블 면 Z 0), mm.
걷기(타임라인 지우기·occurrence 지우기)는 model/del_ids.json · remove_set.json(ana3·ana4.py)로 따로 보낸다.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-14", "model")
STEP = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def plane(kind, off):
    """extrude 방향(+법선): XY -> +Z, YZ -> +X, ZX -> +Y. 스케치 좌표: XY (x,y) · YZ (y,z) · ZX (z,x)"""
    if kind == "XY":
        return {"origin": [0, 0, off], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}
    if kind == "YZ":
        return {"origin": [off, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}
    if kind == "ZX":
        return {"origin": [0, off, 0], "x_dir": [0, 0, 1], "y_dir": [1, 0, 0]}
    raise ValueError(kind)


def prism(sk, kind, off, pts, dist, op, body=None, targets=None, name=None):
    """닫힌 다각형 pts를 kind 평면(off)에 그려 +법선으로 dist 민다. ZX 평면의 pts는 (x,z)로 받아 (z,x)로 바꾼다."""
    if kind == "ZX":
        pts = [[p[1], p[0]] for p in pts]
    out = [C("sketch.create", plane=plane(kind, off), name=sk),
           C("sketch.line", points=[list(map(float, p)) for p in pts], closed=True),
           C("sketch.finish")]
    e = {"sketch": sk, "distance": dist, "operation": op, "name": name or sk.replace("SK_", "F_")}
    if body:
        e["body_name"] = body
    if targets:
        e["targets"] = targets
    out.append(C("solid.extrude", **e))
    return out


def cyl(r, h, base, axis, op, targets=None, body=None, name=None):
    p = {"radius": r, "height": h, "base": list(map(float, base)), "axis": axis, "operation": op}
    if targets:
        p["targets"] = targets
    if body:
        p["body_name"] = body
    if name:
        p["name"] = name
    return C("solid.cylinder", **p)


def box(corner, l, w, h, op, targets=None, body=None, name=None):
    p = {"corner": list(map(float, corner)), "length": l, "width": w, "height": h, "operation": op}
    if targets:
        p["targets"] = targets
    if body:
        p["body_name"] = body
    if name:
        p["name"] = name
    return C("solid.box", **p)


def comp(name, parent, pn=None, desc=None, bom=None):
    return [C("component.create", name=name, parent=parent)]


def meta(name, pn, desc, bom=None):
    p = {"component": name, "part_number": pn, "description": desc}
    if bom:
        p["bom_type"] = bom
    return [C("component.activate", component=0), C("component.metadata.set", **p)]


EARS = [200, 400, 600, 800, 960]
st = {}

# ---------------------------------------------------------------- 3a 남는 부품 추가 가공
a = []
a += [C("component.activate", component="U7_FIXED", occurrence="U7_FIXED:1"),
      box([0, -205, 280], 60, 105, 60, "cut", ["P_M05_HOLDER"], name="RX14_HOLDER_CUT"),
      C("component.activate", component=0)]
a += [C("component.activate", component="U2_TABLE", occurrence="U2_TABLE:1")]
for i, x in enumerate([64, 108]):
    a.append(cyl(3.25, 5, [x, 8, -12.5], "Z", "cut", ["P_M04_PANEL_E2"], name="RX14_PANEL_PIN_%d" % (i + 1)))
for i, x in enumerate([50, 86, 120]):
    a.append(cyl(2.75, 5, [x, 8, -12.5], "Z", "cut", ["P_M04_PANEL_E2"], name="RX14_PANEL_BOLT_%d" % (i + 1)))
a.append(box([49, 15, -12.5], 74, 34, 5, "cut", ["P_M04_PANEL_E2"], name="RX14_PANEL_WINDOW"))
for i, x in enumerate(EARS):
    a.append(cyl(2.1, 5, [x, 5, -12.5], "Z", "cut", ["P_M04_PANEL_E2"], name="RX14_PANEL_TAP_%d" % (i + 1)))
a += [C("component.activate", component=0), C("component.activate", component="U1_FRAME", occurrence="U1_FRAME:1")]
for i, z in enumerate([580, 620]):
    a.append(cyl(2.1, 12.1, [1127, 119.9, z], "Y", "cut", ["P_M07_BEAM"], name="RX14_BEAM_TAP_%d" % (i + 1)))
a += [C("component.activate", component=0)]
st["stage_3a_machining"] = a

# ---------------------------------------------------------------- 3b 유닛 컴포넌트
b = [C("component.create", name="U7_BASE", parent="root", activate=False),
     C("component.create", name="U7_KIT_STAGE", parent="root", activate=False),
     C("component.create", name="U7_KIT", parent="root", activate=False),
     C("component.create", name="U7_BINDER", parent="U7_KIT", activate=False),
     C("component.create", name="U3_BIND_DRV", parent="root", activate=False)]
st["stage_3b_units"] = b

# ---------------------------------------------------------------- 4a 카세트 판·덮개 (U7_KIT)
k = []
k += comp("P_RX14_KIT_PLATE", "U7_KIT")
# 평판: L자(X 46~64는 Y -60까지), 혀 자리(X 46~62, Y -37~-3)는 따냄
k += prism("SK_RX14_KIT_PLATE", "XY", -8,
           [[46, -60], [64, -60], [64, -43], [124, -43], [124, 15], [46, 15], [46, -3], [62, -3], [62, -37], [46, -37]],
           3, "new", body="P_RX14_KIT_PLATE", name="RX14_KIT_PLATE")
# 테이프 혀: X 62에서 굽혀 X 46 끝 윗면 Z -0.5 (15.7도)
k += prism("SK_RX14_KIT_TONGUE", "ZX", -37, [[62, -8], [62, -5], [46, -0.5], [46, -3.5]], 34, "join",
           targets=["P_RX14_KIT_PLATE"], name="RX14_KIT_TONGUE")
# 클램프 받이 귀: 목 Y 15~20(판 높이), 세운 살 Y 17~20, 귀 Y 20~40 · Z -20~-17 (받침 블록 포켓 벽 Y 16과 틈 1)
k += prism("SK_RX14_KIT_EAR", "YZ", 96, [[15, -5], [20, -5], [20, -17], [40, -17], [40, -20], [17, -20], [17, -8], [15, -8]], 20, "join",
           targets=["P_RX14_KIT_PLATE"], name="RX14_KIT_EAR")
k.append(cyl(3.0, 4, [64, 8, -8.5], "Z", "cut", ["P_RX14_KIT_PLATE"], name="RX14_KIT_PIN_HOLE"))
# 긴 구멍 6 x 8 (X로 긴 쪽): 원 둘 + 사각
k.append(cyl(3.0, 4, [107, 8, -8.5], "Z", "cut", ["P_RX14_KIT_PLATE"], name="RX14_KIT_SLOT_A"))
k.append(cyl(3.0, 4, [109, 8, -8.5], "Z", "cut", ["P_RX14_KIT_PLATE"], name="RX14_KIT_SLOT_B"))
k.append(box([107, 5, -8.5], 2, 6, 4, "cut", ["P_RX14_KIT_PLATE"], name="RX14_KIT_SLOT_C"))
for i, x in enumerate([50, 86, 120]):
    k.append(cyl(5.0, 4, [x, 8, -8.5], "Z", "cut", ["P_RX14_KIT_PLATE"], name="RX14_KIT_HEAD_%d" % (i + 1)))
k.append(C("material.assign", bodies=["P_RX14_KIT_PLATE"], material="SUS304"))
k += meta("P_RX14_KIT_PLATE", "P_RX14_KIT_PLATE",
          "RX-14 tool cassette base plate, SUS304 t3 sheet metal (laser + bend, provisional): tape tongue bent up 15.7 deg, "
          "clamp ear bent down, pin hole D6 H7 + slot 6x8, bolt head clearance D10 x3")
k += comp("P_RX14_KIT_COVER", "U7_KIT")
# 윗판(단면 X-Z): X 60~124 윗면 Z -1, X 44~60 경사, X 31~44 윗면 Z 2.5, 두께 1
k += prism("SK_RX14_KIT_COVER", "ZX", -37,
           [[124, -1], [60, -1], [44, 2.5], [31, 2.5], [31, 1.5], [44, 1.5], [60, -2], [124, -2]], 34, "new",
           body="P_RX14_KIT_COVER", name="RX14_KIT_COVER")
# 옆벽 + 발(X 64~124): 단면 Y-Z, 두 쪽
k += prism("SK_RX14_KIT_COVER_FOOT_A", "YZ", 64, [[-43, -5], [-36, -5], [-36, -2], [-37, -2], [-37, -4], [-43, -4]], 60, "join",
           targets=["P_RX14_KIT_COVER"], name="RX14_KIT_COVER_FOOT_A")
k += prism("SK_RX14_KIT_COVER_FOOT_B", "YZ", 64, [[3, -5], [-4, -5], [-4, -2], [-3, -2], [-3, -4], [3, -4]], 60, "join",
           targets=["P_RX14_KIT_COVER"], name="RX14_KIT_COVER_FOOT_B")
k.append(C("material.assign", bodies=["P_RX14_KIT_COVER"], material="SUS304"))
k += meta("P_RX14_KIT_COVER", "P_RX14_KIT_COVER",
          "RX-14 low tape cover on the cassette, SUS304 t1.0 sheet metal (provisional, D-212): top Z -1 (X 60-124), ramp, "
          "tongue top Z 2.5 over the needle plate (X 31-44), feet spot-welded to the plate x4")
st["stage_4a_kit"] = k

# ---------------------------------------------------------------- 4b 받침 블록 (U7_BASE)
s = []
s += comp("P_RX14_KIT_SEAT", "U7_BASE")
s.append(box([42, 0, -32], 84, 48, 20, "new", body="P_RX14_KIT_SEAT", name="RX14_SEAT"))
s.append(box([50, 16, -27], 72, 33, 16, "cut", ["P_RX14_KIT_SEAT"], name="RX14_SEAT_POCKET"))
for i, x in enumerate([50, 86, 120]):
    s.append(cyl(2.1, 10.1, [x, 8, -22], "Z", "cut", ["P_RX14_KIT_SEAT"], name="RX14_SEAT_TAP_%d" % (i + 1)))
for i, x in enumerate([64, 108]):
    s.append(cyl(3.0, 11.1, [x, 8, -23], "Z", "cut", ["P_RX14_KIT_SEAT"], name="RX14_SEAT_PIN_%d" % (i + 1)))
# 클램프 장착 M4 탭 4 (포켓 바닥 Z -27, 관통 5)
CL_B = [(54.5, 22.5), (54.5, 40.5), (80.5, 22.5), (80.5, 40.5)]
for i, (x, y) in enumerate(CL_B):
    s.append(cyl(1.65, 5.2, [x, y, -32.1], "Z", "cut", ["P_RX14_KIT_SEAT"], name="RX14_SEAT_M4_%d" % (i + 1)))
s.append(C("material.assign", bodies=["P_RX14_KIT_SEAT"], material="A5052"))
s += meta("P_RX14_KIT_SEAT", "P_RX14_KIT_SEAT",
          "RX-14 cassette seat block under panel E2, A5052 milling (provisional): 84 x 48 x 20, pocket for toggle clamp, "
          "M5 tap x3 depth 10, pin bore D6 x2 depth 11, M4 tap x4 (clamp, provisional pattern)")
st["stage_4b_seat"] = s

# ---------------------------------------------------------------- 4c 홈통·뚜껑 (U7_BASE)
t = []
t += comp("P_RX14_DUCT", "U7_BASE")
t += prism("SK_RX14_DUCT", "YZ", 125,
           [[-37, -6], [-3, -6], [-3, -2], [-4, -2], [-4, -5], [-36, -5], [-36, -2], [-37, -2]], 935, "new",
           body="P_RX14_DUCT", name="RX14_DUCT")
for i, x in enumerate(EARS):
    t += prism("SK_RX14_DUCT_EAR_%d" % (i + 1), "YZ", x - 8,
               [[-3, -5], [-2, -5], [-2, -7], [11, -7], [11, -8], [-3, -8]], 16, "join",
               targets=["P_RX14_DUCT"], name="RX14_DUCT_EAR_%d" % (i + 1))
    t.append(cyl(2.75, 1.4, [x, 5, -8.2], "Z", "cut", ["P_RX14_DUCT"], name="RX14_DUCT_HOLE_%d" % (i + 1)))
t.append(C("material.assign", bodies=["P_RX14_DUCT"], material="SUS304"))
t += meta("P_RX14_DUCT", "P_RX14_DUCT",
          "RX-14 fixed tape duct (U channel) in the valley between ball rows, SUS304 t1.0 sheet metal (provisional): "
          "X 125-1060, floor Z -6..-5, walls to Z -2, 5 ears joggled down to the panel, hole D5.5")
t += comp("P_RX14_DUCT_LID", "U7_BASE")
t.append(box([125, -37, -2], 935, 34, 1, "new", body="P_RX14_DUCT_LID", name="RX14_DUCT_LID"))
for i, x in enumerate(EARS):
    t += prism("SK_RX14_LID_EAR_%d" % (i + 1), "YZ", x - 8,
               [[-3, -1], [-1, -1], [-1, -6], [11, -6], [11, -7], [-2, -7], [-2, -2], [-3, -2]], 16, "join",
               targets=["P_RX14_DUCT_LID"], name="RX14_LID_EAR_%d" % (i + 1))
    t.append(cyl(2.75, 1.4, [x, 5, -7.2], "Z", "cut", ["P_RX14_DUCT_LID"], name="RX14_LID_HOLE_%d" % (i + 1)))
t.append(C("material.assign", bodies=["P_RX14_DUCT_LID"], material="SUS304"))
t += meta("P_RX14_DUCT_LID", "P_RX14_DUCT_LID",
          "RX-14 tape duct lid (low cover below the table surface, top Z -1), SUS304 t1.0 sheet metal (provisional, D-212): "
          "X 125-1060, 5 ears on the duct ears, hole D5.5")
st["stage_4c_duct"] = t

# ---------------------------------------------------------------- 4d 롤러 받침 R1·R2 (U7_BASE)
r = []
r += comp("P_RX14_R1_BRKT", "U7_BASE")
r += prism("SK_RX14_R1_BRKT", "XY", 560,
           [[1115, 120], [1161, 120], [1161, 1.5], [1115, 1.5], [1115, 7.5], [1155, 7.5], [1155, 114], [1115, 114]],
           151, "new", body="P_RX14_R1_BRKT", name="RX14_R1_BRKT")
r.append(box([1114.9, 113.9, 640], 40.1, 6.2, 71.1, "cut", ["P_RX14_R1_BRKT"], name="RX14_R1_BACK_TRIM"))
r.append(box([1114.9, 1.4, 559.9], 40.1, 6.2, 91.1, "cut", ["P_RX14_R1_BRKT"], name="RX14_R1_FRONT_TRIM"))
r.append(cyl(2.75, 6.2, [1137, 1.4, 681], "Y", "cut", ["P_RX14_R1_BRKT"], name="RX14_R1_PIN_HOLE"))
for i, z in enumerate([580, 620]):
    r.append(cyl(2.75, 6.2, [1127, 113.9, z], "Y", "cut", ["P_RX14_R1_BRKT"], name="RX14_R1_BOLT_%d" % (i + 1)))
r.append(C("material.assign", bodies=["P_RX14_R1_BRKT"], material="SUS304"))
r += meta("P_RX14_R1_BRKT", "P_RX14_R1_BRKT",
          "RX-14 guide roller R1 bracket on the beam front face, SUS304 t6 sheet metal U shape (provisional): "
          "back plate 46 x 80, arm 106.5 x 151, front plate 46 x 60, pin bolt hole D5.5, M5 clearance x2")
r += comp("P_RX14_R2_BRKT", "U7_BASE")
r += prism("SK_RX14_R2_BRKT", "YZ", 1113,
           [[1.5, -250], [51.5, -250], [51.5, -244], [7.5, -244], [7.5, 45], [1.5, 45]], 48, "new",
           body="P_RX14_R2_BRKT", name="RX14_R2_BRKT")
r.append(cyl(2.75, 6.2, [1137, 1.4, 15], "Y", "cut", ["P_RX14_R2_BRKT"], name="RX14_R2_PIN_HOLE"))
R2_B = [(1130, 20.0), (1130, 40.0)]
for i, (x, y) in enumerate(R2_B):
    r.append(cyl(2.75, 6.2, [x, y, -250.1], "Z", "cut", ["P_RX14_R2_BRKT"], name="RX14_R2_BOLT_%d" % (i + 1)))
r.append(C("material.assign", bodies=["P_RX14_R2_BRKT"], material="SUS304"))
r += meta("P_RX14_R2_BRKT", "P_RX14_R2_BRKT",
          "RX-14 guide roller R2 bracket on frame profile top (Z -250), SUS304 t6 sheet metal L shape (provisional): "
          "foot 48 x 50, upright 48 x 295, pin bolt hole D5.5, M5 clearance x2 (T-nut HNTT8-5)")
st["stage_4d_rollers"] = r

# ---------------------------------------------------------------- 4e 임시 형상 (클램프·바인더·차동 구동부·마개)
p = []
p += comp("STEP대기_MC01-5", "U7_BASE")
p.append(box([51, 19, -27], 33, 25, 3, "new", body="STEP대기_MC01-5", name="RX14_CLAMP_FLANGE"))
p += prism("SK_RX14_CLAMP_BODY", "XY", -24, [[59, 24], [76, 24], [76, 39], [59, 39]], 22, "join",
           targets=["STEP대기_MC01-5"], name="RX14_CLAMP_BODY")
for i, (x, y) in enumerate(CL_B):
    p.append(cyl(2.25, 3.2, [x, y, -27.1], "Z", "cut", ["STEP대기_MC01-5"], name="RX14_CLAMP_HOLE_%d" % (i + 1)))
p.append(C("material.assign", bodies=["STEP대기_MC01-5"], material="Steel"))
p.append(C("component.create", name="STEP대기_MC01-5_ARM", parent="STEP대기_MC01-5"))
p.append(box([88, 24, -17], 12, 12, 4, "new", body="STEP대기_MC01-5_ARM", name="RX14_CLAMP_ARM"))
p.append(C("material.assign", bodies=["STEP대기_MC01-5_ARM"], material="Steel"))
p += meta("STEP대기_MC01-5", "MC01-5",
          "placeholder (STEP pending): Misumi MC01-5 toggle clamp, holding force 196 N, arm opens 71 deg; provisional envelope "
          "within 70 x 25 x 25 (flange 33 x 25 x 3 + body 17 x 15 x 22 + arm), M4 x4 mounting pattern provisional", "purchased")
p += [C("component.metadata.set", component="STEP대기_MC01-5_ARM", part_number="MC01-5_ARM", bom_type="reference",
        description="placeholder: clamp arm of MC01-5 (moves with J_U7_CLAMP), presses the cassette ear top Z -17")]
# 바인더 (U7_BINDER 안)
p += [C("component.activate", component="U7_BINDER")]
p += prism("SK_RX14_BINDER_FLOOR", "XY", 0, [[8, -9.5], [12, -9.5], [12, -4], [30, -4], [30, -45], [8, -22]], 3, "new",
           body="STEP대기_BINDER_30_RX14", name="RX14_BINDER_FLOOR")
p += prism("SK_RX14_BINDER_JAW", "ZX", -22, [[8, 3], [12, 3], [12, 14], [-3, 14], [-3, 12.5], [8, 12.5]], 12.5, "join",
           targets=["STEP대기_BINDER_30_RX14"], name="RX14_BINDER_JAW")
p += prism("SK_RX14_BINDER_ARM", "XY", 0, [[30, -46], [62, -46], [62, -38], [30, -38]], 1.5, "join",
           targets=["STEP대기_BINDER_30_RX14"], name="RX14_BINDER_ARM")
p.append(C("material.assign", bodies=["STEP대기_BINDER_30_RX14"], material="Steel"))
p += [C("component.activate", component=0),
      C("component.metadata.set", component="U7_BINDER", part_number="867-392342-M_BINDER_30", bom_type="purchased",
        description="placeholder (D-211, no real dimensions): standard binder for 30 mm tape of Duerkopp Adler 867-392342-M, "
                    "proportions from R375X photos (benchmark da-6): floor triangle X 8-30, jaw wall X 8-12 with upper lip Z 12.5-14, arm to the differential drive")]
p += [C("component.activate", component="U3_BIND_DRV"),
      box([41, -46, -58], 3, 8, 57.8, "new", body="STEP대기_DIFF_BINDER_DRV_867", name="RX14_DIFF_DRV"),
      C("component.activate", component=0),
      C("component.metadata.set", component="U3_BIND_DRV", part_number="867-392342-M_DIFF_BINDER_DRV", bom_type="purchased",
        description="placeholder (D-211, no real dimensions): differential binder drive bar of 867-392342-M coming up between "
                    "needle plate and panel (X 41-44), moves with the feed (J_U3_BIND_DRV, stroke 12 provisional)")]
# 밸브 포트 마개 6
n = 2
for x in (1081.25, 1091.75, 1102.25):
    for z in (356.1, 345.9):
        nm = "STEP대기_M-5P_%d" % n
        p += [C("component.create", name=nm, parent="U8_PNEU"),
              cyl(4.0, 4, [x, 67.5, z], "Y", "new", body=nm, name="RX14_M5P_%d_HEAD" % n),
              cyl(2.5, 4, [x, 71.5, z], "Y", "join", targets=[nm], name="RX14_M5P_%d_THREAD" % n),
              C("component.activate", component=0),
              C("component.metadata.set", component=nm, part_number="M-5P", bom_type="purchased",
                description="placeholder (STEP pending): SMC M-5P plug for the unused M5 port of valve 4-6 (RX-15 will use them)")]
        n += 1
st["stage_4e_placeholders"] = p


# ---------------------------------------------------------------- 4f 테이프 모형 새 길 (U7_TAPE_LINE)
def tape_outline():
    """테이프 가운데 Y -20, 폭 30(Y -35~-5), 두께 1. X-Z 단면의 바깥선(롤러에 닿는 쪽의 반대 면)과 안쪽 선."""
    Rr, rc = 150.0, (670.0, 750.0)        # 롤
    r1, c1 = 19.0, (1137.0, 681.0)
    r2, c2 = 19.0, (1137.0, 15.0)
    T = 1.0
    # 롤 -> R1 윗쪽 바깥 접선 (두 원의 같은 쪽 접선)
    dx, dz = c1[0] - rc[0], c1[1] - rc[1]
    L = math.hypot(dx, dz)
    base = math.atan2(dz, dx)
    off = math.asin((Rr - r1) / L)
    nang = base + math.pi / 2 - off        # 접선의 바깥 법선 각(위쪽)
    nx, nz = math.cos(nang), math.sin(nang)
    inner = []   # 롤러·롤에 닿는 선(가운데 쪽)
    inner.append((rc[0] + Rr * nx, rc[1] + Rr * nz))
    # R1을 위로 감아 +X 쪽(각 0)까지
    a0 = nang
    for i in range(0, 9):
        ang = a0 + (0.0 - a0) * i / 8.0
        inner.append((c1[0] + r1 * math.cos(ang), c1[1] + r1 * math.sin(ang)))
    # 내려와 R2를 +X 쪽에서 아래(각 -90도)까지
    for i in range(0, 9):
        ang = 0.0 + (-math.pi / 2) * i / 8.0
        inner.append((c2[0] + r2 * math.cos(ang), c2[1] + r2 * math.sin(ang)))
    # 홈통·카세트 바닥 위 Z -4(테이프 윗면)로 X 62까지, 혀 경사, 바늘판 위 X 30까지
    inner += [(62.0, -4.0), (46.0, 0.5), (30.0, 0.5)]
    # 바깥선: 롤러 구간은 반지름 +T, 평평한 구간은 아래로 T
    outer = [(rc[0] + (Rr + T) * nx, rc[1] + (Rr + T) * nz)]
    for i in range(0, 9):
        ang = a0 + (0.0 - a0) * i / 8.0
        outer.append((c1[0] + (r1 + T) * math.cos(ang), c1[1] + (r1 + T) * math.sin(ang)))
    for i in range(0, 9):
        ang = 0.0 + (-math.pi / 2) * i / 8.0
        outer.append((c2[0] + (r2 + T) * math.cos(ang), c2[1] + (r2 + T) * math.sin(ang)))
    outer += [(62.2, -5.0), (46.2, -0.5), (30.0, -0.5)]
    # 바늘판 위(X 30~46)는 Z 0~1이어야 하므로 그 구간만 +0.5 올린다
    inner[-2:] = [(46.0, 1.0), (30.0, 1.0)]
    outer[-2:] = [(46.3, 0.0), (30.0, 0.0)]
    pts = inner + outer[::-1]
    return [[round(x, 4), round(z, 4)] for x, z in pts]


tp = [C("component.activate", component="U7_TAPE_LINE", occurrence="U7_TAPE_LINE:1")]
tp += prism("SK_TL_RX14_PATH", "ZX", -35, tape_outline(), 30, "new", body="TL_RX14_PATH", name="TL_RX14_PATH")
tp += [C("component.activate", component=0)]
st["stage_4f_tape"] = tp

for kname, v in st.items():
    json.dump(v, open(os.path.join(OUT, kname + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(kname, len(v))
json.dump({"EARS": EARS, "CL_B": CL_B, "R2_B": R2_B, "tape_outline": tape_outline()},
          open(os.path.join(OUT, "gen_consts.json"), "w", encoding="utf-8"))
