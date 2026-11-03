# -*- coding: utf-8 -*-
"""M01 U3 헤드 개조 + 좁은 홈 묶음 생성기 — v2.0.1 -> v2.0.2 (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M01_design.md 지시서를 그린다.
python -B tools/gen_v2_m01.py -> tools/out/mech_M01/model/stage_*.json, tools/out/mech_M01/edit.json, edit_meta.json
좌표: 바늘점 원점, 테이블 면 Z 0, 이송 +Y. 노루발·바늘은 조인트 값 0(봉제 자세)의 세계 좌표로 그린다.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "out", "mech_M01")
P867 = "STEP대기_867-392342_"
CB16 = PRJ.replace("\\", "/") + "/purchased-step/CB5-16/CB5-16.stp"
HANGER, FOOT = "P_M01_HANGER", "P_M01_FOOT"
SHELF_B = [(x, y) for x in (40, 200, 360) for y in (-50, 50)]
PLATE_BX = (50, 150, 250, 350)
PLATE_BZ = 620


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0, "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, x, y, z0, z1, op, tg=None, name=None):
    p = {"radius": r, "height": z1 - z0, "base": [x, y, z0], "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


def stage_geom():
    s = [C("joint.drive", joint="J_U3_PRESSER", value=0, quiet=True),
         C("joint.drive", joint="J_U3_NEEDLE", value=0, quiet=True),
         # 1. 이름만 바꿈
         C("body.rename", body="U3_UPPER", name=P867 + "UPPER"),
         C("body.rename", body="U3_LOWER_POD", name=P867 + "LOWER"),
         # 3·4·6·8 옛 바디 지움(새로 그림)
         C("solid.remove", bodies=["U3_PRESSER_BOX", "U3_HANGER", "U7_BINDER", "U6_SHOE_SENSOR"])]
    # 1. UPPER 윗면 M5 탭 Ø4.2 깊이 12 (Z 548~560, 위로 1 더 자름)
    s += [cyl(2.1, x, y, 548, 561, "cut", [P867 + "UPPER"]) for (x, y) in SHELF_B]
    # 4. U1_BEAM 앞면 Y 120 M5 탭 Ø4.2 깊이 12 (Y 120~132, 앞으로 1 더)
    s += [C("solid.cylinder", radius=2.1, height=13, base=[x, 119, PLATE_BZ], axis="Y", operation="cut", targets=["U1_BEAM"])
          for x in PLATE_BX]
    # 2. 노즈
    s += [box(P867 + "NOSE", -11, 11, -10, 15, 46, 125),
          cyl(2.0, 0, 0, 45, 126, "cut", [P867 + "NOSE"]),
          cyl(3.5, -5, -3, 45, 126, "cut", [P867 + "NOSE"]),
          C("component.move_bodies", bodies=[P867 + "NOSE"], component="U3_HEAD")]
    # 3. 노루발: 발바닥 t2 한 윤곽 + 바늘 구멍 Ø3 + 노루발대 Ø6 Z 14~80
    s += [C("sketch.create", plane={"origin": [0, 0, 12], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_M01_FOOT"),
          C("sketch.line", points=[[-10, -8], [1, -8], [1, -3.5], [3.5, -3.5], [3.5, 3.5], [1, 3.5], [1, 6], [-10, 6]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M01_FOOT", distance=2, operation="new", body_name=FOOT),
          cyl(1.5, 0, 0, 11, 15, "cut", [FOOT]),
          cyl(3.0, -5, -3, 14, 80, "join", [FOOT]),
          C("material.create", name="S45C", density_g_cm3=7.85, color="#9aa0a6"),
          C("material.assign", bodies=[FOOT], material="S45C"),
          C("component.move_bodies", bodies=[FOOT], component="U3_PRESSER")]
    # 6. 바인더: 바깥 상자 X -11~40 Y -95~-9 Z 13~60에서 자름
    #    지시 3곳 + 노즈(Y -10~15, Z 46~125)와 겹치지 않게 끝 위(Z 22~60)의 Y -10.5~-9 띠(모델링부 보정, 보고서 2절)
    s += [box("U7_BINDER", -11, 40, -95, -9, 13, 60),
          box(None, 1, 41, -31, -8, 12, 22, "cut", ["U7_BINDER"]),
          box(None, -12, -10.5, -31, -8, 12, 22, "cut", ["U7_BINDER"]),
          box(None, -12, 41, -96, -30, 12, 22, "cut", ["U7_BINDER"]),
          box(None, -12, 41, -10.5, -8, 22, 61, "cut", ["U7_BINDER"]),
          C("component.move_bodies", bodies=["U7_BINDER"], component="U7_TAPE")]
    # 7. U7_PATH_V 바닥 12.5 -> 22
    s += [box(None, 29, 111, -136, -94, 11, 22, "cut", ["U7_PATH_V"])]
    # 8. 슈·센서: XZ 단면 다각형을 Y -100 -> -200 으로 밈(평면 법선 -Y)
    s += [C("sketch.create", plane={"origin": [0, -100, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_M01_SHOE"),
          C("sketch.line", points=[[-22, 12.5], [1, 12.5], [1, 30], [10, 30], [10, 90], [-22, 90]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M01_SHOE", distance=100, operation="new", body_name="U6_SHOE_SENSOR"),
          C("component.move_bodies", bodies=["U6_SHOE_SENSOR"], component="U6_SENSOR")]
    return s


def stage_sheet():
    s = [C("sheet.manage_rules", name="SUS304_t8", thickness="8", bend_radius="8", k_factor="0.44", active=True),
         C("sketch.create", plane={"origin": [0, 0, 560], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_M01_HANGER"),
         C("sketch.rectangle.two_point", p0=[0, -90], p1=[400, 120]),
         C("sketch.finish"),
         C("sheet.flange", type="base", sketch="SK_M01_HANGER", rule="SUS304_t8", body_name=HANGER),
         C("sheet.flange", type="edge", edges=[[200, 120, 568]], height=90, angle=90, body=HANGER)]
    return s


def stage_sheet_holes():
    s = [C("sketch.create", plane={"origin": [0, 0, 569], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_M01_HANGER_H1")]
    s += [C("sketch.slot.center_to_center", p0=[x - 2.75, y], p1=[x + 2.75, y], width=5.5) for (x, y) in SHELF_B]
    s += [C("sketch.finish"), C("solid.extrude", sketch="SK_M01_HANGER_H1", distance=10, direction="negative", operation="cut", targets=[HANGER])]
    s += [C("sketch.create", plane={"origin": [0, 111, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_M01_HANGER_H2")]
    s += [C("sketch.slot.center_to_center", p0=[x, PLATE_BZ - 2.75], p1=[x, PLATE_BZ + 2.75], width=5.5) for x in PLATE_BX]
    s += [C("sketch.finish"), C("solid.extrude", sketch="SK_M01_HANGER_H2", distance=10, direction="negative", operation="cut", targets=[HANGER])]
    s += [C("material.create", name="SUS304", density_g_cm3=7.93, color="#c8ccd0"),
          C("material.assign", bodies=[HANGER], material="SUS304"),
          C("component.move_bodies", bodies=[HANGER], component="U3_HEAD")]
    return s


def mat(d, x, y, z):
    """볼트 STEP 국소 +X(나사 방향) -> 월드 d, 머리 밑면 = (x, y, z)."""
    rows = {"-Z": [[0, 0, 1], [0, 1, 0], [-1, 0, 0]], "+Y": [[0, 0, 1], [1, 0, 0], [0, 1, 0]]}[d]
    t = [x, y, z]
    return [v for i in range(3) for v in (rows[i] + [t[i]])]


def bolt_list():
    b = []
    for i, (x, y) in enumerate(SHELF_B, 1):
        b.append(("CB5-16_M01_%d" % i, "-Z", x, y, 568))
    for j, x in enumerate(PLATE_BX, 7):
        b.append(("CB5-16_M01_%d" % j, "+Y", x, 112, PLATE_BZ))
    return b


def stage_bolts():
    s, occ, bodies = [], ["U3_HEAD:1"], []
    for (nm, d, x, y, z) in bolt_list():
        s += [C("file.insert_step", path=CB16, name=nm, matrix=mat(d, x, y, z)),
              C("body.rename", body="Cut-Extrude1", name=nm),
              C("component.metadata.set", component=nm, part_number="CB5-16", bom_type="purchased")]
        occ.append(nm + ":1")
        bodies.append(nm)
    s += [C("material.create", name="SCM435", density_g_cm3=7.85, color="#3a3a3a"),
          C("material.assign", bodies=bodies, material="SCM435"),
          C("joint.rigid_group", occurrences=occ)]
    return s


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints")]


STAGES = [("geom", stage_geom), ("sheet", stage_sheet), ("sheet_holes", stage_sheet_holes),
          ("bolts", stage_bolts), ("final", stage_final)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v2.0.1.sc", "result": "3D_Modeling/FSAP_v2.0.2.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("edit.json", len(allc))


if __name__ == "__main__":
    main()
