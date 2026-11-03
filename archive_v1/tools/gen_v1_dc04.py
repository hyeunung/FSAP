# -*- coding: utf-8 -*-
"""DC-04 정비 면·카세트 인출 안내 생성기 — v1.0.4 -> v1.0.5 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_DC-04_select.md(DC-04-C3 고친 안)를 그린다.
python -B tools/gen_v1_dc04.py -> tools/out/mech_DC-04/edit.json, edit_meta.json, model/stage_*.json
좌표: 바늘점 원점 mm, 작업면 Z 0, REST(J_U4_X·Y 0, J_U8_PULL 0)에서 그린다.
판금은 판금 기능(sheet.*)으로: 걸이 SUS304 t3 R3, 캐리어 SUS304 t4 R4, K 0.44.
3D 원통 자르기는 판금에서 거부되므로 구멍은 판에 평행한 스케치 + 압출 자르기로 낸다.
N01이 U8_CASSETTE_BOX를 컴포넌트에 넣은 뒤 자른 Box44·Box45(월드 고정 자르기)는 카세트가 움직이면 형상이 바뀌어
지우고, N00의 원래 피처 Box28(gen_v1_n00.py 48행)을 X -11~11로 고친다(DC-05와 같은 방법).
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC-04")
STEP_CB = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/CB5-12/CB5-12.stp"
RAIL, BLOCK, PLG = "STEP대기_SSEB13-560_RAIL", "STEP대기_SSEB13-560_BLOCK", "STEP대기_IXP-M8"
UPPER = "STEP대기_867-392342_UPPER"
BOLT_X = (-10, 240, 480)


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0, "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def sheet_stage():
    return [
        C("sheet.manage_rules", name="SUS304_t3", thickness="3", bend_radius="3", k_factor="0.44", active=True),
        # (1) 걸이: 다리 평면(Y -72 -> -75) 바탕 + 앞 혀(X -24~-10, Z 64~92) + 끝 혀(X 520~534, Z 64~92)
        C("sketch.create", plane={"origin": [0, -72, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_DC04_HANGER"),
        C("sketch.line", points=[[-24, 64], [-10, 64], [-10, 92], [520, 92], [520, 64], [534, 64], [534, 92],
                                 [522, 92], [522, 125], [-24, 125]], closed=True),
        C("sketch.finish"),
        C("sheet.flange", type="base", sketch="SK_DC04_HANGER", body_name="P_DC04_HANGER", rule="SUS304_t3"),
        C("sheet.flange", type="edge", body="P_DC04_HANGER", edges=[{"point": [250, -72, 125], "height": 18}],
          height=18, angle=90, flip=True),      # 플랜지 Y -90~-72, Z 122~125
        C("sheet.flange", type="edge", body="P_DC04_HANGER", edges=[{"point": [-24, -75, 80], "height": 49}],
          height=49, angle=90, flip=True),      # 앞 탭 X -24~-21, Y -75~-26
        C("sheet.flange", type="edge", body="P_DC04_HANGER", edges=[{"point": [534, -75, 78], "height": 26}],
          height=26, angle=90, flip=True),      # 끝 탭 X 531~534, Y -75~-49, Z 64~92
        C("sketch.create", plane={"origin": [0, 0, 125], "x_dir": [1, 0, 0], "y_dir": [0, -1, 0]}, name="SK_DC04_HANGER_H1"),
    ] + [C("sketch.circle.center", center=[x, 84], radius=2.75) for x in BOLT_X] + [
        C("sketch.finish"),
        C("solid.extrude", distance=3, operation="cut", targets=["P_DC04_HANGER"]),      # Ø5.5 ×3
        C("sketch.create", plane={"origin": [-24, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_DC04_HANGER_H2"),
        C("sketch.circle.center", center=[-36, 78], radius=4),
        C("sketch.finish"),
        C("solid.extrude", distance=3, operation="cut", targets=["P_DC04_HANGER"]),      # 플런저 M8
        # (6) 캐리어 t4: 판 + -X 러그(전 높이), Ø6H7, 테이프 창
        C("sheet.manage_rules", name="SUS304_t4", thickness="4", bend_radius="4", k_factor="0.44", active=True),
        C("sketch.create", plane={"origin": [0, -48, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_DC04_CARRIER"),
        C("sketch.line", points=[[-20, 64], [20, 64], [20, 124], [-12, 124], [-12, 92], [-20, 92]], closed=True),
        C("sketch.rectangle.two_point", p0=[-10, 70], p1=[10, 85]),
        C("sketch.finish"),
        C("sheet.flange", type="base", sketch="SK_DC04_CARRIER", body_name="P_DC04_CARRIER", rule="SUS304_t4"),
        C("sheet.flange", type="edge", body="P_DC04_CARRIER", edges=[{"point": [-20, -52, 78], "height": 22}],
          height=22, angle=90, flip=True),
        C("sketch.create", plane={"origin": [-20, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_DC04_CARRIER_H1"),
        C("sketch.circle.center", center=[-36, 78], radius=3),
        C("sketch.finish"),
        C("solid.extrude", distance=4, operation="cut", targets=["P_DC04_CARRIER"]),
        C("sketch.create", plane={"origin": [0, -48, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_DC04_CARRIER_WIN"),
        C("sketch.rectangle.two_point", p0=[-10, 70], p1=[10, 85]),
        C("sketch.finish"),
        C("solid.extrude", distance=4, operation="cut", targets=["P_DC04_CARRIER"]),
        C("sheet.manage_rules", name="SUS304_t3", active=True),
    ]


def solid_stage():
    st = [
        box(RAIL, -20, 540, -72, -64, 99.5, 112.5),            # (2) 레일 임시 외형
        box(BLOCK, -20, 20, -64, -52, 92.5, 119.5),             # (5) 블록 임시 외형
        C("solid.cylinder", radius=6, height=40, base=[-64, -36, 78], axis="X", operation="new", body_name=PLG),
        C("solid.cylinder", radius=4, height=3, base=[-24, -36, 78], axis="X", operation="join", targets=[PLG]),
        C("solid.cylinder", radius=3, height=5, base=[-21, -36, 78], axis="X", operation="join", targets=[PLG]),
    ]
    st += [C("solid.cylinder", radius=2.1, height=12, base=[x, -84, 125], operation="cut", targets=[UPPER]) for x in BOLT_X]
    st.append(box(None, 500, 985, 60, 700, -910, -370, "cut", ["U2_BASE"]))   # A. 정비 포켓
    for i, x in enumerate(BOLT_X, 1):
        st.append(C("file.insert_step", path=STEP_CB, name="CB5-12_%d" % i, matrix=[0, 0, -1, x, 0, 1, 0, -84, 1, 0, 0, 122]))
    st += [C("body.rename", body="Cut-Extrude1", name="CB5-12_1"),
           C("body.rename", body="Cut-Extrude1 (2)", name="CB5-12_2"),
           C("body.rename", body="Cut-Extrude1 (3)", name="CB5-12_3")]
    return st


def assy_stage():
    rest = {"J_U4_X": 0, "J_U4_Y": 0, "J_U3_ROT": 0, "J_U1_PRESSER": 20, "J_U1_NEEDLE": 0, "J_U8_PULL": 0}
    maint = dict(rest, J_U4_X=-200)
    mk = [{"joint": j, "points": [[0, v], [21, v]]} for j, v in maint.items() if j != "J_U8_PULL"]
    mk.append({"joint": "J_U8_PULL", "points": [[0, 0], [21, 511]]})
    return [
        C("material.create", name="SUS304", density_g_cm3=7.93, color="#b8bcc2"),
        C("material.create", name="SCM435", density_g_cm3=7.85, color="#3a3d42"),
        C("material.assign", bodies=["P_DC04_HANGER", "P_DC04_CARRIER"], material="SUS304"),
        C("material.assign", bodies=["CB5-12_1", "CB5-12_2", "CB5-12_3"], material="SCM435"),
        C("component.create", name="U8_GUIDE", parent="root", activate=False),
        C("component.move_bodies", bodies=["P_DC04_HANGER", RAIL, PLG], component="U8_GUIDE"),
        C("component.move_bodies", bodies=[BLOCK, "P_DC04_CARRIER"], component="U8_CASSETTE"),
        C("joint.rigid_group", occurrences=["REF_GROUND:1", "U8_GUIDE:1", "CB5-12_1:1", "CB5-12_2:1", "CB5-12_3:1"]),
        C("joint.delete", joint="Rigid Group 2:108"),            # U8_CASSETTE 고정을 풀고 조인트로(M-07)
        C("joint.create", type="slider", name="J_U8_PULL", flip=True, limits=[[0, 511]], quiet=True,
          a={"occurrence": "U8_GUIDE", "point": [0, -50, 100], "z": [1, 0, 0]},
          b={"occurrence": "U8_CASSETTE", "point": [0, -50, 100], "z": [1, 0, 0]}),
        # N01 월드 고정 자르기 정리(카세트가 움직이면 형상이 바뀜)
        C("timeline.delete", features=["Box44", "Box45"]),
        C("timeline.edit", feature="Box28", set={"corner": [-11, -45, 13], "length": "22"}),
        C("motion.study", study="REST", steps=1, keys=[{"joint": j, "points": [[0, v], [1, v]]} for j, v in rest.items()]),
        C("motion.study", name="MAINT", steps=21, keys=mk),
        C("motion.play", study="REST", step=0, quiet=True),
    ]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    stages = [sheet_stage(), solid_stage(), assy_stage()]
    allc = []
    for i, s in enumerate(stages, 1):
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d.json" % i), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d" % i, len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.4.sc", "result": "3D_Modeling/FSAP_v1.0.5.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc))


if __name__ == "__main__":
    main()
