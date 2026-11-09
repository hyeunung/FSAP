# -*- coding: utf-8 -*-
"""FUNC-01 — U5 플로트(받침 스프링) + 접는 바인더 P_M05_BINDER + 바늘판 홈 + IR1000 F 지움 (v2.7.0 -> v2.8.0).
python -X utf8 -B tools/gen_v2_func01.py <stage> -> tools/out/mech_FUNC-01/model/stage_<stage>.json (한 줄 JSON 출력)

편집 자세: REST에서 J_U5_LIFT = 0 (U5_LIFT 로컬 = 세계 = REST - 30). U7은 J_U7_HGT 0·CST 0이라 카세트 좌표 = 세계.
지시서 좌표는 REST 기준 -> U5 Z는 30을 뺀다(zr()).
"""
import json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cz  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
STEP = PRJ + "/purchased-step/"
OUT = os.path.join(ROOT, "out", "mech_FUNC-01", "model")
K = 0.4663                                  # tan 25°
XS = -1847.0                                # 축 X
YS = (("N", -43.0), ("P", 43.0))


def zr(z):
    """REST Z -> 편집 자세 Z (J_U5_LIFT 0)."""
    return round(z - 30.0, 4)


def zc(y):
    return 41.5 - K * (y + 95.0)


def r4(v):
    return round(v, 4)


# ------------------------------------------------------------------ 0. 자세
def stage_pose():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("joint.drive", joint="J_U5_LIFT", value=0, quiet=True)]


# ------------------------------------------------------------------ A. IR1000 F(X 800) 묶음 지우기
def stage_ir_remove():
    return [C("selection.delete",
              occurrences=["IR1000-01BG_M08:2", "CB4-12_M08_REG:3", "CB4-12_M08_REG:4",
                           "KQ2L08-01AS_M08R_PX:2", "KQ2L08-01AS_M08R_NX:2"],
              components=["TU0805_M08T_REG_IN_2", "TU0805_M08T_REG_OUT_2"]),
            C("solid.remove", bodies=["TU0805_M08T_REG_IN_2", "TU0805_M08T_REG_OUT_2"])]   # 컴포넌트를 지우면 바디가 루트로 남음


# ------------------------------------------------------------------ B. U5 플로트 컴포넌트·재배치
FLOAT_BODIES = ["P_M03_LIFT_SIDE_N", "P_M03_LIFT_SIDE_P", "P_M03_FRONT", "P_M03_SNS_BRKT"]
FLOAT_OCCS = ["PGX62-H-10_M03W:1", "HG-KR23_M03W:1"] + ["CB5-16_M03_MOTW:%d" % i for i in range(1, 9)] + \
             ["CB5-16_M03_%d:1" % i for i in (9, 10, 11, 12)]
OLD_RIGID = [992] + list(range(95417, 95427)) + [95521, 95522, 95523, 95524]
OLD_BOLTS = ["CB5-12_M03_7", "CB5-12_M03_8", "CB5-12_M03_9", "CB5-12_M03_10"]   # 옆판 -> 승강판 (플로트로 갈라져 지움)


LIFT_OCCS = ["MGPM25-40Z(0)_ROD:1", "CB6-20_M03_LIFT:1", "CB6-20_M03_LIFT:2", "CB6-16_M03_LIFT:1", "CB6-16_M03_LIFT:2"]


def stage_float_comp():
    """옛 U5_LIFT(옆판·앞판·서보·감속기 등) = 새 U5_FLOAT. 승강판·MGP 끝판+봉·CB6 볼트만 새 컴포넌트로 옮겨 U5_LIFT로 이름을 바꾼다
    (재배치 수를 줄임: 큰 설계에서 selection.delete·reparent 한 번이 수 분)."""
    s = [C("joint.delete", joint=j) for j in OLD_RIGID]
    s += [C("selection.delete", components=OLD_BOLTS)]   # 이 컴포넌트들은 바디째 지워짐(측정 확인)
    s += [C("joint.delete", joint=8753),
          C("component.create", name="U5_LIFT_NEW", parent=0, activate=False),
          C("component.move_bodies", bodies=["P_M03_LIFT_TOP"], component="U5_LIFT_NEW")]
    s += [C("occurrence.reparent", occurrence=o, parent="U5_LIFT_NEW") for o in LIFT_OCCS]
    s += [C("joint.edit", joint="J_U5_LIFT", b={"occurrence": "U5_LIFT_NEW:1", "point": [-1800.0, 0.0, 70.0], "z": [0.0, 0.0, 1.0], "x": [0.0, 1.0, 0.0]}),
          C("component.rename", component="U5_LIFT", name="U5_FLOAT"),
          C("component.rename", component="U5_LIFT_NEW", name="U5_LIFT")]
    return s


def stage_float_joint():
    z0 = zr(164.0)
    return [C("joint.create", type="slider", name="J_U5_FLOAT", flip=True, limits=[[0.0, 20.0]], quiet=True,
              a={"occurrence": "U5_LIFT:1", "point": [XS, 0.0, z0], "z": [0.0, 0.0, 1.0], "x": [1.0, 0.0, 0.0]},
              b={"occurrence": "U5_FLOAT:1", "point": [XS, 0.0, z0], "z": [0.0, 0.0, 1.0], "x": [1.0, 0.0, 0.0]}),
            C("joint.rigid_group", occurrences=["U5_FLOAT:1", "E32-D36P1_2M_M03:1"] + FLOAT_OCCS),
            C("joint.rigid_group", occurrences=["U5_LIFT:1"] + LIFT_OCCS)]


# ------------------------------------------------------------------ C. 가공품 고치기
def stage_plates():
    s = [C("component.activate", component="U5_FLOAT")]
    for side, ys in YS:
        nm = "P_M03_LIFT_SIDE_" + side
        sg = 1 if ys > 0 else -1
        y_web0, y_web1 = (31.0, 37.0) if sg > 0 else (-37.0, -31.0)
        y_all0, y_all1 = (30.0, 56.0) if sg > 0 else (-56.0, -30.0)
        # 옛 위 플랜지·웹 윗부분 (REST Z 136 위) 깎음
        s.append(box(None, -1995.0, -1815.0, y_all0, y_all1, zr(136.0), zr(160.0), "cut", [nm]))
        # 새 위 플랜지 t6 (REST Z 130~136), 웹과 한 바디
        fy0, fy1 = (31.0, 55.0) if sg > 0 else (-55.0, -31.0)
        s.append(box(None, -1990.0, -1820.0, fy0, fy1, zr(130.0), zr(136.0), "join", [nm]))
        # 축 구멍 Ø16 H7 (플랜지)
        s.append(cz(8.0, XS, ys, zr(129.0), zr(137.0), "cut", [nm]))
        if sg > 0:
            # CB6-20 머리 비킴 Ø12 (u 20에서 머리 밑 Z 124)
            for xb in (-1959.0, -1881.0):
                s.append(cz(6.0, xb, 46.0, zr(129.0), zr(137.0), "cut", [nm]))
    # 축 받침 블록 P_F01_SHAFT_HLD_N/P (SUS304 밀링) REST Z 116~130, 축 Ø16 H7, 옆 M5 멈춤나사 Ø4.2
    for side, ys in YS:
        hn = "P_F01_SHAFT_HLD_" + side
        y0, y1 = (37.0, 55.0) if ys > 0 else (-55.0, -37.0)
        s.append(box(hn, -1861.0, -1833.0, y0, y1, zr(116.0), zr(130.0), "new"))
        s.append(cz(8.0, XS, ys, zr(115.0), zr(131.0), "cut", [hn]))
        ya, yb = (ys, 56.0) if ys > 0 else (-56.0, ys)
        s.append(cyl(2.1, [XS, ya, zr(123.0)], yb - ya, [0, 1, 0], "cut", [hn]))
        s.append(C("material.assign", bodies=[hn], material="SUS304"))
    # 앞판 윗면 Z 140 -> 134
    s.append(box(None, -1835.0, -1815.0, -35.0, 35.0, zr(134.0), zr(145.0), "cut", ["P_M03_FRONT"]))
    s.append(C("component.activate", component=0))
    return s


def stage_lifttop():
    t = "P_M03_LIFT_TOP"
    s = [C("component.activate", component="U5_LIFT"),
         box(None, -1995.0, -1876.0, -33.0, 33.0, zr(150.0), zr(170.0), "cut", [t]),          # 서보 창
         box(None, -1876.0, -1820.0, -70.0, -54.0, zr(156.0), zr(164.0), "join", [t])]         # -Y 넓힘
    for xb in (-1975.0, -1835.0):                                                              # 옛 CB5-12 탭 메움
        for yb in (-46.0, 46.0):
            s.append(cz(3.0, xb, yb, zr(156.0), zr(164.0), "join", [t]))
    for _, ys in YS:
        s.append(cz(8.25, XS, ys, zr(150.0), zr(170.0), "cut", [t]))                        # Ø16.5 관통
    s.append(C("component.activate", component=0))
    return s


# ------------------------------------------------------------------ D. 구매품·STEP대기
def m_z_up(t):
    """STEP 로컬 +X -> 세계 +Z, 로컬 +Y -> 세계 +X."""
    return [0.0, 1.0, 0.0, t[0], 0.0, 0.0, 1.0, t[1], 1.0, 0.0, 0.0, t[2]]


def stage_buy():
    s = []
    for side, ys in YS:
        s += [C("component.activate", component="U5_LIFT"),
              C("file.insert_step", path=STEP + "LHFR16/LHFR16.stp", name="LHFR16_F01_" + side,
                matrix=m_z_up((XS, ys, zr(164.0)))),
              C("component.activate", component="U5_FLOAT"),
              C("file.insert_step", path=STEP + "PSFJ16-150/PSFJ16-150.stp", name="PSFJ16-150_F01_" + side,
                matrix=m_z_up((XS, ys, zr(116.0))))]
    s.append(C("component.activate", component=0))
    return s


def stage_buy_names():
    s = []
    for raw, nm, pn, d in (("CBORE for Socket Head Cap Screw4", "LHFR16_F01_N", "LHFR16", "Misumi LHFR16 flange linear bushing, U5 float guide on lift plate (FUNC-01)"),
                           ("CBORE for Socket Head Cap Screw4 (2)", "LHFR16_F01_P", "LHFR16", "Misumi LHFR16 flange linear bushing, U5 float guide on lift plate (FUNC-01)"),
                           ("Chamfer1", "PSFJ16-150_F01_N", "PSFJ16-150", "Misumi PSFJ16-150 shaft, U5 float guide REST Z 116~266 (FUNC-01)"),
                           ("Chamfer1 (2)", "PSFJ16-150_F01_P", "PSFJ16-150", "Misumi PSFJ16-150 shaft, U5 float guide REST Z 116~266 (FUNC-01)")):
        s += [C("body.rename", body=raw, name=nm), C("material.assign", bodies=[nm], material="Steel"),
              C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased", description=d)]
    return s


def tube(name, x, y, r_out, r_in, z0, z1):
    return [cz(r_out, x, y, z0, z1, "new", name=name), cz(r_in, x, y, z0 - 1, z1 + 1, "cut", [name])]


def stage_wait():
    s = [C("component.activate", component="U5_FLOAT")]
    for side, ys in YS:
        s += tube("STEP대기_PSCS16_F01_HANG_" + side, XS, ys, 16.0, 8.0, zr(201.0), zr(213.0))
        s += tube("STEP대기_PSCS16_F01_TOP_" + side, XS, ys, 16.0, 8.0, zr(250.0), zr(262.0))
        s += tube("P_F01_SPRING_SEAT_" + side, XS, ys, 22.0, 8.25, zr(247.0), zr(250.0))
        s += [C("material.assign", bodies=["STEP대기_PSCS16_F01_HANG_" + side, "STEP대기_PSCS16_F01_TOP_" + side], material="S45C"),
              C("material.assign", bodies=["P_F01_SPRING_SEAT_" + side], material="SUS304")]
    s.append(C("component.activate", component="U5_LIFT"))
    for side, ys in YS:
        nm = "STEP대기_SPRING_d1.6_OD44_L132_" + side
        s += tube(nm, XS, ys, 22.0, 20.4, zr(172.0), zr(247.0))
        s.append(C("material.assign", bodies=[nm], material="Steel"))
    s.append(C("component.activate", component=0))
    return s


def stage_rigid():
    return [C("joint.rigid_group", occurrences=["U5_LIFT:1", "LHFR16_F01_N:1", "LHFR16_F01_P:1"]),
            C("joint.rigid_group", occurrences=["U5_FLOAT:1", "PSFJ16-150_F01_N:1", "PSFJ16-150_F01_P:1"])]


# ------------------------------------------------------------------ E. 바인더 P_M05_BINDER (카세트 좌표 = 세계)
B = "P_M05_BINDER"


def yz_poly(name, pts, x0, x1, op, tg=None):
    """YZ 평면(스케치 x = 세계 Y, y = 세계 Z) 다각형을 X x0 -> x1로 밈."""
    s = [C("sketch.create", plane="YZ", offset=x0),
         C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
         C("sketch.finish")]
    p = {"distance": r4(x1 - x0), "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    s.append(C("solid.extrude", **p))
    return s


def xy_poly(name, pts, z0, z1, op, tg=None):
    s = [C("sketch.create", plane="XY", offset=z0),
         C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
         C("sketch.finish")]
    p = {"distance": r4(z1 - z0), "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    s.append(C("solid.extrude", **p))
    return s


def slab(y0, y1, a, b):
    return [(y0, zc(y0) + a), (y1, zc(y1) + a), (y1, zc(y1) + b), (y0, zc(y0) + b)]


def layer(tag, y0, y1, a, b, x0, x1, plan):
    ts, tp = "TMP_F01_%s_S" % tag, "TMP_F01_%s_P" % tag
    s = yz_poly(ts, slab(y0, y1, a, b), x0, x1, "new")
    s += xy_poly(tp, plan, 0.0, 70.0, "new")
    s += [C("solid.combine", target=ts, tools=[tp], operation="intersect"),
          C("solid.combine", target=B, tools=[ts], operation="cut")]
    return s


def stage_binder_outer():
    s = [C("component.activate", component="U7_CASSETTE")]
    s += xy_poly(B, [(-11, -95), (45.5, -95), (45.5, -90.5), (40, -90.5), (40, -10.5), (-11, -10.5)], 22.0, 60.0, "new")
    s += [box(None, 40.0, 46.5, -96.0, -90.5, 21.0, 37.0, "cut", [B]),
          box(None, 40.0, 46.5, -96.0, -90.5, 47.0, 61.0, "cut", [B])]
    s += yz_poly(None, [(-9, 13), (-25.3, 13), (-44.6, 22), (-44.6, 23), (-10.5, 23), (-10.5, 22), (-9, 22)], -5.0, 8.0, "join", [B])
    s += [cz(2.1, 15.0, -80.0, 52.0, 61.0, "cut", [B]), cz(2.1, 15.0, -55.0, 52.0, 61.0, "cut", [B])]   # M5 탭 Ø4.2 깊이 8
    s.append(C("component.activate", component=0))
    return s


def stage_binder_inner():
    s = [C("component.activate", component="U7_CASSETTE")]
    s += layer("K1", -97, -62, -1.0, 1.0, 13.5, 44.5, [(13.5, -97), (46.5, -97), (13.5, -64)])
    s += layer("F1", -97, -62, -1.0, 4.2, 13.5, 44.5, [(46.5, -97), (48.5, -97), (15.5, -64), (13.5, -64)])
    s += layer("K2", -97, -62, 2.2, 4.2, -3.0, 44.5, [(46.5, -97), (13.5, -64), (-3, -64), (30, -97)])
    s += layer("F2", -97, -62, 2.2, 7.4, -5.0, 28.0, [(28, -97), (30, -97), (-3, -64), (-5, -64)])
    s += layer("K3", -97, -62, 5.4, 7.4, -3.0, 28.0, [(30, -97), (30, -62), (-5, -62)])
    # K4 윗날개 길: 경사 Y -64 ~ -25.3, 평평 Z 14.4~16.4 Y -25.3 ~ -8
    s += yz_poly(None, slab(-64.0, -25.3, 5.4, 7.4), -3.0, 8.0, "cut", [B])
    zf = r4(zc(-25.3) + 5.4)                       # 14.399: 경사 끝과 같은 높이
    s.append(box(None, -3.0, 8.0, -25.3, -8.0, zf, zf + 2.0, "cut", [B]))
    # K5 풀림: X 6.5~30, 아래로 열림
    s += yz_poly(None, [(-64, 10), (-64, zc(-64) + 7.4), (-25.3, zf + 2.0), (-8, zf + 2.0), (-8, 10)], 6.5, 30.0, "cut", [B])
    s += [C("material.assign", bodies=[B], material="PA12"), C("component.activate", component=0)]
    return s


def stage_binder_swap():
    return [C("solid.remove", bodies=["U7_BINDER"])]


def stage_lower():
    return [C("component.activate", component="U3_HEAD"),
            box(None, -4.0, 10.0, -45.0, 12.0, -1.4, 0.5, "cut", ["STEP대기_867-392342_LOWER"]),
            C("component.activate", component=0)]


# ------------------------------------------------------------------ F. 연구 키 바꾸기 (J_U5_LIFT 0/1/2 -> (-10, FLOAT 10/11/12))
def remap(points):
    lift, flt = [], []
    for st, v in points:
        if abs(v - 30.0) < 1e-6:
            lift.append([st, 30.0]); flt.append([st, 0.0])
        elif abs(v + 10.0) < 1e-6:
            lift.append([st, -10.0]); flt.append([st, 0.0])
        elif -0.001 <= v <= 2.001:
            lift.append([st, -10.0]); flt.append([st, round(10.0 + v, 4)])
        else:
            raise ValueError("unexpected J_U5_LIFT key %s" % v)
    return lift, flt


def stage_studies():
    d = json.load(open(os.path.join(ROOT, "out", "mech_FUNC-01", "motionlist_v270.json"), encoding="utf8"))
    s = []
    for st in d["studies"]:
        k = [x for x in st["keys"] if x["joint_name"] == "J_U5_LIFT"][0]
        lift, flt = remap(k["points"])
        keys = [{"joint": x["joint_name"], "index": x.get("index", 0), "points": x["points"]}
                for x in st["keys"] if x["joint_name"] != "J_U5_LIFT"]          # motion.study keys는 통째로 바뀐다 — 나머지 키를 그대로 다시 준다
        keys += [{"joint": "J_U5_LIFT", "points": lift}, {"joint": "J_U5_FLOAT", "points": flt}]
        s.append(C("motion.study", study=st["name"], steps=st["steps"], keys=keys))
    return s


def stage_save():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("component.rename", component=0, name="FSAP_v2.8.0")]


def dump(name, s):
    os.makedirs(OUT, exist_ok=True)
    json.dump(s, open(os.path.join(OUT, "stage_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return s


STAGES = ["pose", "ir_remove", "float_comp", "float_joint", "plates", "lifttop", "buy", "buy_names", "wait", "rigid",
          "binder_outer", "binder_inner", "binder_swap", "lower", "studies", "save"]

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "record":
        e = []
        for nm in STAGES:
            e += globals()["stage_" + nm]()
        d = os.path.dirname(OUT)
        json.dump(e, open(os.path.join(d, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        json.dump({"base": "3D_Modeling/FSAP_v2.7.0.sc", "result": "3D_Modeling/FSAP_v2.8.0.sc",
                   "generator": "tools/gen_v2_func01.py record (MCP batch, FUNC-01)"},
                  open(os.path.join(d, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("edit.json", len(e))
    else:
        print(json.dumps(dump(what, globals()["stage_" + what]()), ensure_ascii=False, separators=(",", ":")))
