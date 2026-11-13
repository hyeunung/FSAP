# -*- coding: utf-8 -*-
"""RX-06R U4 X축 볼나사·손잡이 빼기 생성기 (v2.14.0 -> v2.15.0).

같은 형상을 다시 만들 수 있게 남기는 명령 생성기다(실행 규칙 3).
  python -B tools/gen_v2_rx06r.py
가 tools/out/mech_RX-06R/model/stage_*.json, mini_*.json 과
tools/out/mech_RX-06R/edit.json, edit_meta.json 을 다시 쓴다.

앱(MCP)에서 stage_0 -> save{path} -> stage_1 ... stage_9 -> save{path} 순서로 실행했다.
작은 볼트 설계(mini_*.json)는 CLI 로 만든다:
  solidcraft-cli run mini_<이름>.json --save d_<이름>.sc

좌표: 월드, REST(J_U4_X 0, J_U4_PRESS 13.006, J_U4_STOP 0).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-06R")
STAGE = os.path.join(OUT, "model")
STEP = os.path.join(os.path.dirname(HERE), "purchased-step").replace("\\", "/")
OUTP = STAGE.replace("\\", "/")
BASE = "3D_Modeling/FSAP_v2.14.0.sc"
RESULT = "3D_Modeling/FSAP_v2.15.0.sc"
DOC_NAME = "FSAP_v2.15.0"
DESC = "RX-06R mechanism: U4 X axis ball screw+handle removed, rail+block+bolt lock blade (C-46)"


def C(command, **params):
    return {"command": command, "params": params}


def cyl(r, h, base, axis, targets, name):
    return C("solid.cylinder", radius=r, height=h, base=base, axis=axis, operation="cut",
             targets=targets, name=name)


# ---- 작은 볼트 설계: STEP 로컬 +x(나사 끝) -> 월드 +Y, 원점 = 머리 밑면
R_X_TO_Y = [0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
LOCK = [("CB5-16_RX06R_LOCK_1", [-225, 89.3, 468]), ("CB5-16_RX06R_LOCK_2", [-140, 89.3, 468])]
BLADE_X = [-315, -255, -195, -135]
BLADE_B = [("CB5-12_RX06R_BLADE_%d" % (i + 1), [x, 118, 562]) for i, x in enumerate(BLADE_X)]
MINIS = {}
for name, _ in LOCK:
    MINIS[name] = [C("file.insert_step", path=STEP + "/CB5-16/CB5-16.stp", name="CB5-16", matrix=R_X_TO_Y),
                   C("body.rename", body="Cut-Extrude1", name=name)]
for name, _ in BLADE_B:
    MINIS[name] = [C("file.insert_step", path=STEP + "/CB5-12/CB5-12.stp", name="CB5-12", matrix=R_X_TO_Y),
                   C("body.rename", body="Cut-Extrude1", name=name)]

# ---- 0) 새 번호 문서: 이름·설명 (그 뒤 save {path})
stage_0 = [C("component.rename", component=0, name=DOC_NAME),
           C("document.metadata.set", key="description", value=DESC)]

# ---- 1) 조인트·링크·너트 볼트 occurrence
stage_1 = [C("joint.delete", link=35),                     # J_U4_X -> J_U4_XSCREW 18 deg/mm
           C("joint.delete", joint=98014),                 # J_U4_XSCREW
           C("joint.delete", joint=97992), C("joint.delete", joint=97993),   # BSW20, BUN20
           C("joint.delete", joint=97999),                 # 너트
           C("joint.delete", joint=98012),                 # 손잡이
           # CB6-20_M03_CAR:5~:8 (리지드 98000~98003 은 같이 지워진다)
           C("selection.delete", occurrences=[97906, 97981, 97982, 97983])]

# ---- 2) 피처: 나사 부품 7바디·축·손잡이·스페이서 F·S, 캐리지 너트 귀·구멍 5, 레일(Remove86·그린 상자)
stage_2 = [C("timeline.delete", features=[97905, 97915, 97916, 97917, 97918, 97919, 97920, 97921, 97922,
                                          97942, 97943, 97946, 97947,
                                          97928, 97929, 97930, 97931, 97932, 97933,
                                          97923, 97925, 97924])]
# ---- 3) 빈 컴포넌트 5
stage_3 = [C("component.delete", component=c) for c in
           ["BSW20_RX06", "BUN20_RX06", "BSS2020-1100_RX06_NUT", "BSS2020-1100_RX06", "STEP대기_HANDLE_D50"]]

# ---- 4) 캐리지 웹 윗끝 565 -> 482 (스케치 점 2개)
stage_4 = [C("sketch.edit", sketch=97926),
           C("sketch.move_point", point="l2.end", to=[107, 482]),
           C("sketch.move_point", point="l3.end", to=[95, 482]),
           C("sketch.finish")]

# ---- 5) 레일: STEP 원본(Chamfer2)을 X -115 에서 자르고 RAIL 컴포넌트 두 배치에
stage_5 = [C("component.activate", component="RAIL_SSEB13-570", occurrence="RAIL_SSEB13-570:1"),
           C("solid.box", corner=[-115, 130, 280], length=400, width=40, height=40, operation="cut",
             targets=["Chamfer2"], name="RX06R_RAIL_CUT_220"),
           C("component.activate", component=0),
           C("body.rename", body="Chamfer2", name="SSEB13-220_RX06_RAIL"),
           C("component.move_bodies", bodies=["SSEB13-220_RX06_RAIL"], component="RAIL_SSEB13-570",
             component_path=[97895, 97897])]

# ---- 6) U4_XCAR 안: 캐리지 M5 탭 2, 누름 판
CAR = "P_RX06_CARRIAGE"
CLAMP = "P_RX06R_LOCK_CLAMP_레이저"
stage_6 = [C("component.activate", component="U4_XCAR", occurrence="U4_XCAR:1"),
           cyl(2.1, 12.2, [-225, 94.9, 468], [0, 1, 0], [CAR], "RX06R_CAR_TAP_1"),
           cyl(2.1, 12.2, [-140, 94.9, 468], [0, 1, 0], [CAR], "RX06R_CAR_TAP_2"),
           C("solid.box", corner=[-237.5, 89.3, 458], length=110, width=3, height=20, operation="new",
             body_name=CLAMP, name="RX06R_LOCK_CLAMP"),
           cyl(2.75, 3.2, [-225, 89.2, 468], [0, 1, 0], [CLAMP], "RX06R_CLAMP_HOLE_1"),
           cyl(2.75, 3.2, [-140, 89.2, 468], [0, 1, 0], [CLAMP], "RX06R_CLAMP_HOLE_2"),
           C("material.assign", bodies=[CLAMP], material="SUS304"),
           C("component.activate", component=0)]

# ---- 7) 보 앞벽 M5 탭 4 (Ø4.2, Y 119~130 = 벽 t8 관통 + 2)
# 이력 끝에서 보를 자르면 느리거나 실패한다(보 = R12 필렛 + 구멍 110여 면):
#   U1_FRAME 활성 + 바닥 Y 119.9 원통 cut -> "boolean Cut: no result"(115 s),
#   끝에서 스케치 원 4 + extrude cut -> 실패(273 s), 4공구 solid.combine -> 278 s,
#   바닥을 면(Y 120)에 둔 원통 cut 4번 -> 통과하지만 하나 55~65 s 이고 joint.drive 마다 다시 계산된다(+270 s).
# 그래서 LITE(v2.8.10)가 보 탭을 모아 둔 앞쪽 스케치 Sketch15(96774, Box16 바로 뒤, 평면 Y 119·x = 월드 Z·y = 월드 X,
# Extrude143 = profiles all·cut 11·targets P_M07_BEAM)에 원 4개를 더한다. restore_marker null = 그 스케치로 내렸다가
# Finish 때 끝으로 올림(전체 재계산 한 번).
stage_7 = [C("sketch.edit", sketch=96774, restore_marker=None)]
stage_7 += [C("sketch.circle.center", center=[562, x], radius=2.1) for x in BLADE_X]
stage_7 += [C("sketch.finish")]

# ---- 8) U4_XAXIS 안: 잠금 날(판금 기능, t2 R2, Z자)
BL = "P_RX06R_LOCK_BLADE_판금"
stage_8 = [C("component.activate", component="U4_XAXIS", occurrence="U4_XAXIS:1"),
           C("sheet.manage_rules", name="SUS304_t2_R2", thickness="2", bend_radius="2", active=True),
           C("sketch.create", plane={"origin": [-335, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]},
             name="SK_RX06R_LOCK_BLADE"),
           # 판의 한쪽 면: 플랜지 뒷면(Y 120) - 선반 밑면(Z 543) - 다리 뒷면(Y 94.5)
           C("sketch.line", points=[[120, 577], [120, 543], [94.5, 543], [94.5, 457]]),
           C("sketch.finish"),
           C("sheet.flange", type="contour", sketch="SK_RX06R_LOCK_BLADE", curves=["l1", "l2", "l3"],
             distance=213, rule="SUS304_t2_R2", body_name=BL, name="SF_RX06R_LOCK_BLADE"),
           C("solid.box", corner=[-321.5, 91, 465.25], length=183, width=5, height=5.5, operation="cut",
             targets=[BL], name="RX06R_BLADE_SLOT"),
           cyl(2.75, 5, [-321.5, 91, 468], [0, 1, 0], [BL], "RX06R_BLADE_SLOT_E1"),
           cyl(2.75, 5, [-138.5, 91, 468], [0, 1, 0], [BL], "RX06R_BLADE_SLOT_E2")]
stage_8 += [cyl(2.75, 4, [x, 117, 562], [0, 1, 0], [BL], "RX06R_BLADE_HOLE_%d" % (i + 1))
            for i, x in enumerate(BLADE_X)]
stage_8 += [C("material.assign", bodies=[BL], material="SUS304"),
            C("component.activate", component=0)]

# ---- 9) 볼트 6 (작은 설계 넣기 -> 링크 끊기 -> 리지드), 메타
stage_9 = []
for name, at in LOCK + BLADE_B:
    stage_9.append(C("component.insert_design", path=OUTP + "/d_%s.sc" % name, name=name, parent="root",
                     translate=at))
for name, _ in LOCK + BLADE_B:
    stage_9.append(C("component.break_link", component=name))
stage_9 += [C("joint.rigid_group", occurrences=["U4_XCAR:1"] + [n + ":1" for n, _ in LOCK]),
            C("joint.rigid_group", occurrences=["U4_XAXIS:1"] + [n + ":1" for n, _ in BLADE_B])]
for name, _ in LOCK:
    stage_9.append(C("component.metadata.set", component=name, part_number="CB5-16", bom_type="purchased",
                     description="MISUMI CB5-16 (RX-06R lock bolt, carriage web M5 tap, 3 N.m)"))
for name, _ in BLADE_B:
    stage_9.append(C("component.metadata.set", component=name, part_number="CB5-12", bom_type="purchased",
                     description="MISUMI CB5-12 (RX-06R lock blade to beam front wall M5 tap, 4 N.m)"))
stage_9 += [
    C("component.metadata.set", component="SSEB13-570_RX06", part_number="SSEB13-220", bom_type="purchased",
      description="MISUMI SSEB13 miniature guide, rail L220 x2 (STEP SSEB13-570 rail cut at X -115), 2 blocks per rail"),
    C("component.metadata.set", component="U4_XAXIS",
      description="RX-06R: fixed side of U4 X adjust axis (rails, stops, lock blade + CB5-12 x4), rigid to frame beam"),
    C("component.metadata.set", component="U4_XCAR",
      description="RX-06R: moving carriage of U4 X adjust axis (P_RX06_CARRIAGE, 4 blocks, lock clamp + CB5-16 x2), J_U4_X hand set + bolt lock"),
]

# ---- 10) 저장 전
stage_10 = [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("browser.visibility", visible=False, folder="sketches")]

STAGES = [("stage_0_name", stage_0), ("stage_1_joints", stage_1), ("stage_2_tldelete", stage_2),
          ("stage_3_compdelete", stage_3), ("stage_4_carriage_sketch", stage_4), ("stage_5_rail", stage_5),
          ("stage_6_xcar", stage_6), ("stage_7_beam", stage_7), ("stage_8_blade", stage_8),
          ("stage_9_bolts", stage_9), ("stage_10_presave", stage_10)]


def main():
    os.makedirs(STAGE, exist_ok=True)
    for name, cmds in MINIS.items():
        with open(os.path.join(STAGE, "mini_%s.json" % name), "w", encoding="utf-8") as f:
            json.dump(cmds, f, ensure_ascii=False, indent=0)
    allc = []
    for name, cmds in STAGES:
        with open(os.path.join(STAGE, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(cmds, f, ensure_ascii=False)
        allc += cmds
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8") as f:
        json.dump(allc, f, ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"base": BASE, "result": RESULT,
                   "note": "RX-06R. 앱(MCP)에서 stage_0 -> save -> stage_1~10 -> save 순서로 실행. "
                           "볼트 작은 설계 model/d_*.sc 는 mini_*.json 을 CLI 로 저장한 것"},
                  f, ensure_ascii=False, indent=1)
    print("stages", len(STAGES), "commands", len(allc), "minis", len(MINIS))


if __name__ == "__main__":
    main()
