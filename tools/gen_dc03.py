# -*- coding: utf-8 -*-
"""DC-03 X·Y 케이블 베어 자리 생성기 — v1.0.8 -> v1.0.9, 수정 1회차 --fix1 v1.0.9 -> v1.0.10 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_DC-03_select.md(DC-03-S, C3 고친 안)를 그린다.
python -B tools/gen_dc03.py -> tools/out/mech_DC-03/model/stage_*.json (MCP batch로 차례로 보냄), edit.json, edit_meta.json
좌표: 바늘점 원점 월드 mm, J_U4_X·J_U4_Y 0(REST)에서 그린다.
- 판금 SUS304(요구서 2-1): t2 R2 / t3 R3, K 0.44. 구멍은 판에 평행한 스케치 + 압출 자르기.
  XTROUGH·XMOV = contour flange(선은 바깥 면, 재료는 진행 방향 오른쪽 — N03 실측 규칙),
  YTRAY·YMOV = base flange + edge flange(밑/윗면 모서리 점 + flip, position inside / material_outside).
- 탭(M5 Ø4.2 깊이 12)은 그 바디를 만든 Box 바로 뒤로 마커를 돌려 넣는다(N03 방식): U2_BASE Box22, U4_X_BEAM Box30, U4_Y_CARR Box40.
- 볼트 CB5-12 실물 STEP 1개를 넣어 유닛 컴포넌트로 옮긴 뒤 occurrence.copy(translate).
- X 베어 임시 형상: 지시 '차지 상자'를 실제 차지 띠(안 줄 X -1230~464, 바깥 줄 X -521~464, 고리 쓸림 X -437.5~464)
  한 스케치로 밀어 한 바디로 — 지시의 바닥 볼트 자리(Y 1290, 줄 사이)가 상자 안에 드는 모순을 지시 기준(볼트는 베어를 피함)대로 푼다.
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC-03")
CB12 = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/CB5-12/CB5-12.stp"

XT, XM, YT, YM = "P_DC03_XTROUGH", "P_DC03_XMOV", "P_DC03_YTRAY", "P_DC03_YMOV"
XB, YB = "STEP대기_E4.56.10.150.0", "STEP대기_2400.05.075.0"

XT_BOLTS = [(-1150, 1290), (-800, 1290), (-500, 1290), (478, 1140), (478, 1290), (478, 1440)]   # (X, Y), 자리 Z -378
XM_BOLTS = [(-1030, -320), (-970, -320)]                                                       # (X, Z), 자리 Y 1003
YT_BOLTS = [(903, -325), (932, -325), (-903, -325), (-932, -325)]                               # (Y, Z), 자리 X -1052
YM_BOLTS = [(-325, -245), (-295, -245)]                                                        # (Y, Z), 자리 X -1028


def C(cmd, **p):
    return {"command": cmd, "params": p}


def plane(origin, xd, yd, name):
    return C("sketch.create", plane={"origin": origin, "x_dir": xd, "y_dir": yd}, name=name)


def cyl(r, h, base, axis, tg):
    return C("solid.cylinder", radius=r, height=h, base=base, axis=axis, operation="cut", targets=tg)


# ---------------- stage 1: 판금 4장 ----------------
def stage_sheet():
    st = [C("sheet.manage_rules", name="SUS304_t2", thickness="2", bend_radius="2", k_factor="0.44", active=True),
          C("sheet.manage_rules", name="SUS304_t3", thickness="3", bend_radius="3", k_factor="0.44", active=False)]
    # (1) X 홈통: 단면 YZ(법선 +X), X -1260 -> 490. 선 = 바깥 면, 재료 오른쪽
    st += [plane([-1260, 0, 0], [0, 1, 0], [0, 0, 1], "SK_DC03_XTROUGH"),
           C("sketch.line", points=[[1487, -298], [1487, -380], [1086, -380], [1086, -358]]),
           C("sketch.finish"),
           C("sheet.flange", type="contour", sketch="SK_DC03_XTROUGH", curves=["l1", "l2", "l3"], distance=1750,
             rule="SUS304_t2", body_name=XT)]
    # (3) X 움직이는 끝 U: 단면 YZ, X -1050 -> -950
    st += [plane([-1050, 0, 0], [0, 1, 0], [0, 0, 1], "SK_DC03_XMOV"),
           C("sketch.line", points=[[1101, -262], [1101, -348], [1000, -348], [1000, -295]]),
           C("sketch.finish"),
           C("sheet.flange", type="contour", sketch="SK_DC03_XMOV", curves=["l1", "l2", "l3"], distance=100,
             rule="SUS304_t3", body_name=XM)]
    # (4) Y 홈통: 바닥 Z -360 -> -358, 탭 두 개, +X 벽 릴리프 Y ±(885~890) X -1210~-1204
    st += [plane([0, 0, -360], [1, 0, 0], [0, 1, 0], "SK_DC03_YTRAY"),
           C("sketch.line", points=[[-1284, -945], [-1052, -945], [-1052, -890], [-1210, -890], [-1210, -885], [-1204, -885],
                                    [-1204, 885], [-1210, 885], [-1210, 890], [-1052, 890], [-1052, 945], [-1284, 945]], closed=True),
           C("sketch.finish"),
           C("sheet.flange", type="base", sketch="SK_DC03_YTRAY", body_name=YT, rule="SUS304_t2"),
           # 벽 2(안쪽): 밑면 모서리 점 + flip -> 위로, 높이 30(밑면 -360 -> -330)
           C("sheet.flange", type="edge", body=YT, edges=[[-1284, 0, -360], [-1204, 0, -360]], height=30, angle=90, flip=True),
           # 끝 웹 2·탭 끝 플랜지 2(재료 바깥): 웹 Y ±(945~947) 높이 30, 플랜지 X -1052~-1050 높이 60(-> Z -300)
           C("sheet.flange", type="edge", body=YT, position="material_outside", angle=90, flip=True, height=30,
             edges=[{"point": [-1170, 945, -360], "height": 30}, {"point": [-1170, -945, -360], "height": 30},
                    {"point": [-1052, 917.5, -360], "height": 60}, {"point": [-1052, -917.5, -360], "height": 60}])]
    # (6) Y 움직이는 끝: 팔 Z -173 -> -170(윗면 -170), 다리 X -1028~-1025 아래로 88, 보강 Y -283~-280 아래로 18(X -1205~-1025)
    st += [plane([0, 0, -173], [1, 0, 0], [0, 1, 0], "SK_DC03_YMOV"),
           # 베어 위(X < -1209) 팔은 Y -340~-287로 좁혀 보강 플랜지 모서리를 끊는다(릴리프 7 ≥ t+R 6).
           # 처음 그린 노치(-1205~-1209, 깊이 4)는 플랜지가 베어 위 모서리까지 이어져 베어 상자와 겹쳤다(2,953 mm³) -> 지우고 다시 그림
           C("sketch.line", points=[[-1277, -340], [-1025, -340], [-1025, -280], [-1209, -280], [-1209, -287], [-1277, -287]],
             closed=True),
           C("sketch.finish"),
           C("sheet.flange", type="base", sketch="SK_DC03_YMOV", body_name=YM, rule="SUS304_t3"),
           C("sheet.flange", type="edge", body=YM, edges=[{"point": [-1025, -310, -170], "height": 88},
                                                         {"point": [-1115, -280, -170], "height": 18}],
             height=88, angle=90, flip=True),
           C("sheet.manage_rules", name="SUS304_t2", active=True)]
    return st


# ---------------- stage 2: 판금 구멍 ----------------
def stage_holes():
    st = []
    # X 홈통 바닥 Ø5.5 ×6: 평면 Z -378 법선 -Z, (u, v) = (X, -Y)
    st += [plane([0, 0, -378], [1, 0, 0], [0, -1, 0], "SK_DC03_XTROUGH_H1")]
    st += [C("sketch.circle.center", center=[x, -y], radius=2.75) for (x, y) in XT_BOLTS]
    st += [C("sketch.finish"), C("solid.extrude", distance=2, operation="cut", targets=[XT])]
    # X 홈통 바깥 벽 케이블 창 X -590~-510, Z -370~-310: 평면 Y 1487 법선 -Y
    st += [plane([0, 1487, 0], [1, 0, 0], [0, 0, 1], "SK_DC03_XTROUGH_W"),
           C("sketch.rectangle.two_point", p0=[-590, -370], p1=[-510, -310]),
           C("sketch.finish"), C("solid.extrude", distance=2, operation="cut", targets=[XT])]
    # XMOV A면 Ø5.5 ×2: 평면 Y 1003 법선 -Y
    st += [plane([0, 1003, 0], [1, 0, 0], [0, 0, 1], "SK_DC03_XMOV_H")]
    st += [C("sketch.circle.center", center=[x, z], radius=2.75) for (x, z) in XM_BOLTS]
    st += [C("sketch.finish"), C("solid.extrude", distance=3, operation="cut", targets=[XM])]
    # YTRAY 끝 플랜지 Ø5.5 ×4: 평면 X -1052 법선 +X
    st += [plane([-1052, 0, 0], [0, 1, 0], [0, 0, 1], "SK_DC03_YTRAY_H")]
    st += [C("sketch.circle.center", center=[y, z], radius=2.75) for (y, z) in YT_BOLTS]
    st += [C("sketch.finish"), C("solid.extrude", distance=2, operation="cut", targets=[YT])]
    # YMOV 다리 Ø5.5 ×2: 평면 X -1028 법선 +X
    st += [plane([-1028, 0, 0], [0, 1, 0], [0, 0, 1], "SK_DC03_YMOV_H")]
    st += [C("sketch.circle.center", center=[y, z], radius=2.75) for (y, z) in YM_BOLTS]
    st += [C("sketch.finish"), C("solid.extrude", distance=3, operation="cut", targets=[YM])]
    return st


# ---------------- stage 3: 상대 부품 탭 M5 Ø4.2 깊이 12 ----------------
def stage_taps():
    st = [C("timeline.roll_to", feature="Box22"), plane([0, 0, -380], [1, 0, 0], [0, -1, 0], "SK_DC03_BASE_TAP")]
    st += [C("sketch.circle.center", center=[x, -y], radius=2.1) for (x, y) in XT_BOLTS]
    st += [C("sketch.finish"), C("solid.extrude", distance=12, operation="cut", targets=["U2_BASE"]),
           C("timeline.rollback", position="end"),
           C("timeline.roll_to", feature="Box30")]
    st += [cyl(2.1, 12, [x, 988, z], "Y", ["U4_X_BEAM"]) for (x, z) in XM_BOLTS]          # 보 +Y 끝면
    st += [cyl(2.1, 12, [-1050, y, z], "X", ["U4_X_BEAM"]) for (y, z) in YT_BOLTS]        # 보 -X 면 끝 통살
    st += [C("timeline.rollback", position="end"), C("timeline.roll_to", feature="Box40")]
    st += [cyl(2.1, 12, [-1025, y, z], "X", ["U4_Y_CARR"]) for (y, z) in YM_BOLTS]        # 대차 -X 면
    st += [C("timeline.rollback", position="end")]
    return st


# ---------------- stage 4: 케이블 베어 임시 형상(E-10) ----------------
def stage_bear():
    return [
        # X 베어 E4.56.10.150.0 눕힌 고리 차지 띠: Z -378 -> -250
        plane([0, 0, -378], [1, 0, 0], [0, 1, 0], "SK_DC03_XBEAR"),
        C("sketch.line", points=[[-1230, 1101], [464, 1101], [464, 1485], [-521, 1485], [-521, 1401], [-437.5, 1401],
                                 [-437.5, 1185], [-1230, 1185]], closed=True),
        C("sketch.finish"),
        C("solid.extrude", distance=128, operation="new", body_name=XB),
        # 바깥 아래 모서리 C2: 홈통 바깥 벽 굽힘 안쪽(R2)과 겹치던 0.86 mm² × 985 를 뺀다(REST 검사에서 찾음)
        C("solid.chamfer", edges=[[0, 1485, -378]], distance=2),
        # Y 베어 2400.05.075.0 세운 고리 차지 상자
        C("solid.box", length=64, width=1736, height=185, corner=[-1277, -806, -358], operation="new", body_name=YB),
    ]


# ---------------- stage 5: 재질·컴포넌트 ----------------
def stage_assign():
    return [
        C("material.create", name="PA", density_g_cm3=1.14, color="#3c3c3c"),
        C("material.assign", bodies=[XT, XM, YT, YM], material="SUS304"),
        C("material.assign", bodies=[XB, YB], material="PA"),
        C("component.move_bodies", bodies=[XT, XB], component="U4_FIX"),
        C("component.move_bodies", bodies=[XM, YT, YB], component="U4_X"),
        C("component.move_bodies", bodies=[YM], component="U4_Y"),
    ]


# ---------------- stage 6: 볼트 ----------------
ROWS = {"-Z": [[0, 0, 1], [0, 1, 0], [-1, 0, 0]], "-Y": [[0, 1, 0], [-1, 0, 0], [0, 0, 1]],
        "+X": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
AXES = {"-Z": [0, 0, -1], "-Y": [0, -1, 0], "+X": [1, 0, 0]}


def bmat(d, p):
    return [v for i in range(3) for v in (ROWS[d][i] + [round(p[i], 4)])]


def bolt_groups():
    return [
        ("CB5-12_DC03XT", "-Z", [(x, y, -378.0) for (x, y) in XT_BOLTS], "U4_FIX", "X 홈통 바닥 -> U2_BASE 탭(물림 10)", XT, "U2_BASE"),
        ("CB5-12_DC03XM", "-Y", [(x, 1003.0, z) for (x, z) in XM_BOLTS], "U4_X", "XMOV A면 -> 보 +Y 끝면 탭(물림 9)", XM, "U4_X_BEAM"),
        ("CB5-12_DC03YT", "+X", [(-1052.0, y, z) for (y, z) in YT_BOLTS], "U4_X", "YTRAY 끝 플랜지 -> 보 -X 면 탭(물림 10)", YT, "U4_X_BEAM"),
        ("CB5-12_DC03YM", "+X", [(-1028.0, y, z) for (y, z) in YM_BOLTS], "U4_Y", "YMOV 다리 -> 대차 -X 면 탭(물림 9)", YM, "U4_Y_CARR"),
    ]


def stage_bolts():
    st = []
    for nm, d, pts, par, desc, a, b in bolt_groups():
        p0 = pts[0]
        st += [C("file.insert_step", path=CB12, name=nm, matrix=bmat(d, p0)),
               C("body.rename", body="Cut-Extrude1", name=nm),
               C("material.assign", bodies=[nm], material="SCM435"),
               C("component.metadata.set", component=nm, part_number="CB5-12", bom_type="purchased",
                 description="MISUMI 육각 구멍붙이 볼트 CB5-12 — %s (DC-03)" % desc),
               C("occurrence.reparent", occurrence=nm + ":1", parent=par)]
        for p in pts[1:]:
            st.append(C("occurrence.copy", occurrence=nm + ":1", translate=[round(p[i] - p0[i], 4) for i in range(3)]))
    st.append(C("motion.play", study="REST", step=0, quiet=True))
    return st


# ---------------- 수정 1회차(v1.0.9 -> v1.0.10): YMOV 다리 ㄷ 보강 ----------------
# 검증 문제: 다리 Z -230~-170 받침 없는 띠(60x3, Z 90 mm3)가 오조작 손 100 N(팔 끝 X -1277)+1 g에서 SF 0.69.
# 고친 안 A: 다리 양 옆 Y -340~-337·-283~-280에 -X 15 옆판(X -1043~-1028, Z -230~), +Y 쪽은 다리 릴리프(Y -285.12~-280)를
# 메우고 보강 플랜지와 모서리 용접(릴리프 12 대신). 옆판 1은 팔 밑 Z -173까지, 옆판 2는 보강 플랜지 굽힘 밑 Z -176까지.
# 판금 edge flange는 가장자리 전체에만 서므로(부분 길이 불가) 용접 옆판을 extrude join으로 그린다(전개는 DC-03-D9).
def stage_fix1():
    Y2 = -285.12132034355966   # 다리 +Y 가장자리(corner relief 끝)
    return [
        plane([0, 0, -230], [1, 0, 0], [0, 1, 0], "SK_DC03_YMOV_SIDE1"),
        C("sketch.rectangle.two_point", p0=[-1043, -340], p1=[-1028, -337]),
        C("sketch.finish"),
        C("solid.extrude", distance=57, operation="join", targets=[YM]),
        plane([0, 0, -230], [1, 0, 0], [0, 1, 0], "SK_DC03_YMOV_SIDE2"),
        C("sketch.line", points=[[-1043, -283], [-1028, -283], [-1028, Y2], [-1025, Y2], [-1025, -280], [-1043, -280]], closed=True),
        C("sketch.finish"),
        C("solid.extrude", distance=54, operation="join", targets=[YM]),
        C("motion.play", study="REST", step=0, quiet=True),
    ]


STAGES = [("sheet", stage_sheet), ("holes", stage_holes), ("taps", stage_taps), ("bear", stage_bear),
          ("assign", stage_assign), ("bolts", stage_bolts)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    stages = list(STAGES)
    rig = os.path.join(OUT, "model", "rigid_ids.json")
    if os.path.exists(rig):
        ids = json.load(open(rig, encoding="utf-8"))
        stages.append(("rigid", lambda: [C("joint.rigid_group", occurrences=v) for v in ids.values()]
                       + [C("motion.play", study="REST", step=0, quiet=True)]))
    for i, (nm, f) in enumerate(stages, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.8.sc", "result": "3D_Modeling/FSAP_v1.0.9.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bl = []
    for nm, d, pts, par, desc, a, b in bolt_groups():
        for k, p in enumerate(pts, 1):
            bl.append({"name": "%s:%d" % (nm, k), "spec": "CB5-12", "pos": list(p), "axis": AXES[d], "unit": par,
                       "clamps": a, "tap": b})
    json.dump(bl, open(os.path.join(OUT, "model", "bolts_plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc), "bolts", len(bl))


def main_fix1():
    s = stage_fix1()
    json.dump(s, open(os.path.join(OUT, "model", "stage_8_fix1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(s, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.9.sc", "result": "3D_Modeling/FSAP_v1.0.10.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("stage_8_fix1", len(s))


if __name__ == "__main__":
    import sys
    if "--fix1" in sys.argv:
        main_fix1()      # v1.0.9 -> v1.0.10 (edit.json = 이 회차 명령만; v1.0.9 전체는 model/edit_v1.0.9.json)
    else:
        main()
