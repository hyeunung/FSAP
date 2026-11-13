# -*- coding: utf-8 -*-
"""RX-11 U5 먼 쪽 바퀴 밑 받침을 X축 자유 롤러 2줄로 (C-45) 생성기 (v2.16.0 -> v2.17.0).

같은 형상을 다시 만들 수 있게 남기는 명령 생성기다(실행 규칙 3).
  python -X utf8 -B tools/gen_rx11.py
가 tools/out/mech_RX-11/model/stage_*.json 과 tools/out/mech_RX-11/edit.json, edit_meta.json 을 다시 쓴다.

앱(MCP)에서 stage_0 -> save{path} -> stage_1 ... stage_9 -> save{path} 순서로 실행했다.
지시서: docs/reports/mechanism/mech_RX-11_design.md (설계안 지시서 [1]~[10]).
좌표: 세계 좌표 mm, REST. 새 부품은 모두 U2_TABLE 아래(접지에 이어진 고정 묶음, 조인트 없음).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-11")
STAGE = os.path.join(OUT, "model")
STEP = os.path.join(os.path.dirname(HERE), "purchased-step").replace("\\", "/")
BASE = "3D_Modeling/FSAP_v2.16.0.sc"
RESULT = "3D_Modeling/FSAP_v2.17.0.sc"
DOC_NAME = "FSAP_v2.17.0"
DESC = "RX-11 mechanism: U5 under-wheel support = 2 rows of free rollers on X (C-45), PTFE strip set removed"
U2 = "U2_TABLE"

SADDLE_X = [-1838.0 + 216.0 * i for i in range(8)]          # -1838 ... -326
ROLL_X0 = [-1830.0 + 216.0 * i for i in range(7)]           # 롤러 -X 끝: -1830 ... -534
ROW_Y = [11.0, -11.0]
ZC = -10.0                                                   # 롤러·축 중심 Z (윗면 Z 0)
S = 3.0 * math.sqrt(0.5)                                     # R3 호의 가운데 점 띄움


def C(command, **params):
    return {"command": command, "params": params}


def yz_plane(x):
    """Y-Z 단면 스케치 평면(스케치 x = 세계 Y, y = 세계 Z, 법선 +X)."""
    return {"origin": [x, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}


def copies(comp, n, dx=216.0):
    return [C("occurrence.copy", occurrence=comp + ":1", in_place=True, translate=[dx * k, 0.0, 0.0])
            for k in range(1, n)]


# ---- 0) 새 번호 문서: 이름·설명 (그 뒤 save {path})
stage_0 = [C("motion.play", study="REST", step=0, quiet=True),
           C("component.rename", component=0, name=DOC_NAME),
           C("document.metadata.set", key="description", value=DESC)]

# ---- 1) 걷어 내기: 띠(스케치 3·돌출 3·보스 8·나사 8) + 누름판 8(원통 16) + 옮김 9 + 볼트 복사·옮김, 볼트 컴포넌트
DEL = ([4661, 4662, 4663, 4664] + list(range(4665, 4673)) + [95001, 95002] + list(range(95003, 95011))
       + list(range(4681, 4697)) + list(range(4697, 4706)) + [4708, 4709])
stage_1 = [C("timeline.delete", features=DEL),
           C("component.delete", component="CB5-12_DC205")]

# ---- 2) 판 긴 홈 2 (U2_TABLE 안 피처, 판 밑 Z -13 평면에서 +Z 6 관통)
W2, E2 = "P_M04_PANEL_W2", "P_M04_PANEL_E2"
stage_2 = [C("component.activate", component=U2, occurrence=U2 + ":1"),
           C("sketch.create", plane={"origin": [0, 0, -13], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]},
             name="SK_RX11_SLOT_W2"),
           # 판 +X 끝(X -410)보다 5 더 나가 열린 끝을 만든다. 닫힌 끝 X -1847, 모서리 R 3
           C("sketch.line", points=[[-405, 23], [-405, -23], [-1844, -23]]),
           C("sketch.arc.three_point", start=[-1844, -23], end=[-1847, -20], through=[-1844 - S, -20 - S]),
           C("sketch.line", points=[[-1847, -20], [-1847, 20]]),
           C("sketch.arc.three_point", start=[-1847, 20], end=[-1844, 23], through=[-1844 - S, 20 + S]),
           C("sketch.line", points=[[-1844, 23], [-405, 23]]),
           C("sketch.finish"),
           C("solid.extrude", sketch="SK_RX11_SLOT_W2", distance=6, operation="cut", targets=[W2],
             name="RX11_SLOT_W2"),
           C("sketch.create", plane={"origin": [0, 0, -13], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]},
             name="SK_RX11_SLOT_E2"),
           # 판 -X 끝(X -410)보다 5 더 나가 열린 끝. 닫힌 끝 X -317, 모서리 R 3
           C("sketch.line", points=[[-415, -23], [-415, 23], [-320, 23]]),
           C("sketch.arc.three_point", start=[-320, 23], end=[-317, 20], through=[-320 + S, 20 + S]),
           C("sketch.line", points=[[-317, 20], [-317, -20]]),
           C("sketch.arc.three_point", start=[-317, -20], end=[-320, -23], through=[-320 + S, -20 - S]),
           C("sketch.line", points=[[-320, -23], [-415, -23]]),
           C("sketch.finish"),
           C("solid.extrude", sketch="SK_RX11_SLOT_E2", distance=6, operation="cut", targets=[E2],
             name="RX11_SLOT_E2"),
           C("component.activate", component=0)]

# ---- 3) 가로 형재 통과 홈: X -420 자리(HFS8-4080-560_M04:1, occurrence 5953)를 따로 정의로 나눈 뒤 깎는다
# component.paste_new 는 "copy geometry differs for body HFS8-4080-560_M04" 로 거부됐다(STEP + 끝면 오프셋을 다시 만든 형상이
# 원본과 다름). 그래서 남는 자리(:2, X -305)의 바디를 새 컴포넌트로 복사(component.copy_bodies)해 X -420 자리로 옮기고
# 옛 :1 자리를 지운 뒤, 루트에서 세계 좌표로 깎았다(복사 원본 :2·:3 은 그대로).
NOTCH_COMP = "HFS8-4080-560_M04_NOTCH"
stage_3 = [C("component.create", name=NOTCH_COMP, parent=U2, activate=False),
           C("component.copy_bodies", bodies=["HFS8-4080-560_M04 (U2_TABLE:1/HFS8-4080-560_M04:2)"],
             component=NOTCH_COMP),
           C("body.rename", body="HFS8-4080-560_M04 (2)", name=NOTCH_COMP),
           C("occurrence.move", occurrence=NOTCH_COMP + ":1", space="world", translate=[-115, 0, 40]),
           C("selection.delete", occurrences=[5953]),
           # X 전체(-420~-380, 양쪽 1 더), Y -24~+24, Z -23~-12(위로 1 더)
           C("solid.box", corner=[-421, -24, -23], length=42, width=48, height=12, operation="cut",
             targets=[NOTCH_COMP], name="RX11_HFS_NOTCH"),
           C("component.metadata.set", component=NOTCH_COMP, part_number="HFS8-4080-560", bom_type="purchased",
             description="Misumi HFS8-4080 L560 (STEP HFS8-4080-1900 cut), RX-11 extra machining: top notch "
                         "48 x 11 deep across the 40 width at mid length (roller pass-through)")]

# ---- 4) 새들 P_RX11_SADDLE x8 (A5052 밀링 잠정)
SAD = "P_RX11_SADDLE"
x0 = SADDLE_X[0]


def u_groove(c):
    """축 홈 단면: 폭 6.2, 위로 열림(Z -1 까지 그림), 바닥 반원 R 3.1 중심 Z -9.9."""
    return [C("sketch.line", points=[[c - 3.1, -9.9], [c - 3.1, -1], [c + 3.1, -1], [c + 3.1, -9.9]]),
            C("sketch.arc.three_point", start=[c + 3.1, -9.9], end=[c - 3.1, -9.9], through=[c, -13.0])]


stage_4 = [C("component.create", name=SAD, parent=U2),
           C("sketch.create", plane=yz_plane(x0 - 7), name="SK_RX11_SADDLE"),
           C("sketch.line", points=[[-26.5, -2], [26.5, -2], [26.5, -8], [22.5, -8], [22.5, -16], [-22.5, -16],
                                    [-22.5, -8], [-26.5, -8]], closed=True),
           C("sketch.finish"),
           C("solid.extrude", sketch="SK_RX11_SADDLE", distance=14, operation="new", body_name=SAD,
             name="RX11_SADDLE"),
           # 축 홈 4: -X 면에서 깊이 6(스케치는 면 밖 1), +X 면에서 깊이 6(가운데 벽 2)
           C("sketch.create", plane=yz_plane(x0 - 8), name="SK_RX11_SADDLE_GROOVE_A")]
stage_4 += u_groove(11.0) + u_groove(-11.0)
stage_4 += [C("sketch.finish"),
            C("solid.extrude", sketch="SK_RX11_SADDLE_GROOVE_A", distance=7, operation="cut", targets=[SAD],
              name="RX11_SADDLE_GROOVE_A"),
            C("sketch.create", plane=yz_plane(x0 + 1), name="SK_RX11_SADDLE_GROOVE_B")]
stage_4 += u_groove(11.0) + u_groove(-11.0)
stage_4 += [C("sketch.finish"),
            C("solid.extrude", sketch="SK_RX11_SADDLE_GROOVE_B", distance=7, operation="cut", targets=[SAD],
              name="RX11_SADDLE_GROOVE_B"),
            # 볼트 자리: Ø5.5 관통, 카운터보어 Ø9.5 깊이 6(자리 면 Z -8) — U-11 이유: 머리가 매트 밑면 Z 0 아래
            C("solid.cylinder", radius=2.75, height=10, base=[x0, 0, -17], axis="Z", operation="cut", targets=[SAD],
              name="RX11_SADDLE_HOLE"),
            C("solid.cylinder", radius=4.75, height=7, base=[x0, 0, -8], axis="Z", operation="cut", targets=[SAD],
              name="RX11_SADDLE_CBORE"),
            C("material.assign", bodies=[SAD], material="A5052"),
            C("component.activate", component=0),
            C("component.metadata.set", component=SAD, part_number=SAD,
              description="RX-11 roller saddle, A5052 milling (provisional), 14 x 53 x 14, shaft grooves 6.2 x4, "
                          "M5 clearance + counterbore D9.5 x 6")]
stage_4 += copies(SAD, 8)

# ---- 5) 클램프 P_RX11_CLAMP x8 (A5052 밀링 잠정)
CLP = "P_RX11_CLAMP"
stage_5 = [C("component.create", name=CLP, parent=U2),
           C("sketch.create", plane=yz_plane(x0 - 7), name="SK_RX11_CLAMP"),
           C("sketch.line", points=[[-30, -31], [30, -31], [30, -12], [23.5, -12], [23.5, -16.5], [-23.5, -16.5],
                                    [-23.5, -12], [-30, -12]], closed=True),
           C("sketch.finish"),
           C("solid.extrude", sketch="SK_RX11_CLAMP", distance=14, operation="new", body_name=CLP,
             name="RX11_CLAMP"),
           # M5 탭 세로 관통(밑구멍 Ø4.2, Z -31~-16.5, 양쪽 1 더) + 나사 표시
           C("solid.cylinder", radius=2.1, height=16.5, base=[x0, 0, -32], axis="Z", operation="cut", targets=[CLP],
             name="RX11_CLAMP_TAP"),
           C("solid.thread", face=[x0 + 2.1, 0, -24], designation="M5", modeled=False),
           C("material.assign", bodies=[CLP], material="A5052"),
           C("component.activate", component=0),
           C("component.metadata.set", component=CLP, part_number=CLP,
             description="RX-11 roller saddle clamp (under panel), A5052 milling (provisional), 14 x 60 x 19, "
                         "M5 tap through")]
stage_5 += copies(CLP, 8)

# ---- 6) 볼트 CB5-20 x8: STEP 로컬 +X = 축(머리 -> 끝), 원점 = 머리 밑면 -> 축 -Z, 머리 밑 Z -8
BOLT = "CB5-20_RX11"
stage_6 = [C("file.insert_step", path=STEP + "/CB5-20/CB5-20.stp", name=BOLT,
             matrix=[0, 0, 1, x0, 0, 1, 0, 0, -1, 0, 0, -8]),
           C("body.rename", body="Cut-Extrude1", name=BOLT),
           C("component.metadata.set", component=BOLT, part_number="CB5-20", bom_type="purchased",
             description="Misumi CB5-20 STEP, RX-11 saddle to clamp through panel slot (3 N.m)"),
           C("material.assign", bodies=[BOLT], material="SCM435"),
           C("occurrence.reparent", occurrence=BOLT + ":1", parent=U2)]
stage_6 += copies(BOLT, 8)

# ---- 7) 롤러 STEP대기_RORLM20-6-L200 x14 (E-10 임시 형상: 외경 20, 길이 200, 속 Ø12, 양 끝 5 구간 Ø6)
ROL = "STEP대기_RORLM20-6-L200"
r0 = ROLL_X0[0]
stage_7 = [C("component.create", name=ROL, parent=U2),
           C("solid.cylinder", radius=10, height=200, base=[r0, ROW_Y[0], ZC], axis="X", operation="new",
             body_name=ROL, name="RX11_ROLLER"),
           C("solid.cylinder", radius=3, height=202, base=[r0 - 1, ROW_Y[0], ZC], axis="X", operation="cut",
             targets=[ROL], name="RX11_ROLLER_BORE6"),
           C("solid.cylinder", radius=6, height=190, base=[r0 + 5, ROW_Y[0], ZC], axis="X", operation="cut",
             targets=[ROL], name="RX11_ROLLER_BORE12"),
           C("material.assign", bodies=[ROL], material="Steel"),
           C("component.activate", component=0),
           C("component.metadata.set", component=ROL, part_number="RORLM20-6-L200", bom_type="purchased",
             description="placeholder (STEP pending, D-200): Misumi RORLM20-6-L200 pipe roller with bearings "
                         "B696ZZ x2, D20 x L200, shaft bore 6, steel electroless nickel")]
stage_7 += copies(ROL, 7)
stage_7 += [C("occurrence.copy", occurrence=ROL + ":1", in_place=True, translate=[216.0 * k, -22.0, 0.0])
            for k in range(7)]

# ---- 8) 축 STEP대기_SFJ6-213 x14 (Ø6 x 213, 롤러 양 끝에서 6.5)
SHF = "STEP대기_SFJ6-213"
stage_8 = [C("component.create", name=SHF, parent=U2),
           C("solid.cylinder", radius=3, height=213, base=[r0 - 6.5, ROW_Y[0], ZC], axis="X", operation="new",
             body_name=SHF, name="RX11_SHAFT"),
           C("material.assign", bodies=[SHF], material="Steel"),
           C("component.activate", component=0),
           C("component.metadata.set", component=SHF, part_number="SFJ6-213", bom_type="purchased",
             description="placeholder (STEP pending, D-200): Misumi SFJ6-213 linear shaft D6 g6 x L213, "
                         "roller fixed axle resting in saddle grooves")]
stage_8 += copies(SHF, 7)
stage_8 += [C("occurrence.copy", occurrence=SHF + ":1", in_place=True, translate=[216.0 * k, -22.0, 0.0])
            for k in range(7)]

# ---- 9) 저장 전
stage_9 = [C("motion.play", study="REST", step=0, quiet=True),
           C("browser.visibility", visible=False, folder="joints"),
           C("browser.visibility", visible=False, folder="sketches")]

STAGES = [("stage_0_name", stage_0), ("stage_1_delete", stage_1), ("stage_2_slots", stage_2),
          ("stage_3_hfs_notch", stage_3), ("stage_4_saddle", stage_4),
          ("stage_5_clamp", stage_5), ("stage_6_bolts", stage_6), ("stage_7_rollers", stage_7),
          ("stage_8_shafts", stage_8), ("stage_9_presave", stage_9)]


def main():
    os.makedirs(STAGE, exist_ok=True)
    allc = []
    for name, cmds in STAGES:
        with open(os.path.join(STAGE, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(cmds, f, ensure_ascii=False)
        allc += cmds
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8") as f:
        json.dump(allc, f, ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"base": BASE, "result": RESULT,
                   "note": "RX-11. 앱(MCP)에서 stage_0 -> save{path} -> stage_1~9 -> save{path} 순서로 실행"},
                  f, ensure_ascii=False, indent=1)
    print("stages", len(STAGES), "commands", len(allc))


if __name__ == "__main__":
    main()
