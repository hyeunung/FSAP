# -*- coding: utf-8 -*-
"""M08R 라이트 커튼 짧게 + 기둥 3개 줄임(C-32) 생성기 — v2.5.9 -> v2.6.0 (중간 저장 v2.5.10) (모델링부 2026-11-06)
지시서 docs/reports/mechanism/mech_M08R_design1.md, 보고서 docs/reports/mechanism/mech_M08R_model.md.
python -X utf8 -B tools/gen_v2_m08r.py -> tools/out/mech_M08R/edit.json, edit_meta.json
MCP로 실제 보낸 명령을 그대로 적었다(탐색·실패·되돌린 명령 제외).
주의: occurrence id(9155·9157·9190·9192 …, 18 = U8_PNEU:1)는 v2.5.9를 연 그 세션에서 매긴 값이다.
      다른 세션·CLI에서 다시 돌리면 id가 다를 수 있다 -> file.insert_step 결과의 occurrence로 바꿔 넣는다.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M08R")
STEP = PRJ + "/purchased-step/F3SG-4RA0800-14/F3SG-4RA0800-14.stp"
W = "STEP대기_"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def main():
    s = [C("motion.play", study="REST", step=0, quiet=True),
         C("component.rename", component=0, name="FSAP_v2.6.0"),
         C("document.metadata.set", key="description",
           value="M08R mechanism: light curtains shortened to F3SG-4RA0800-14 STEP, columns cut to 1650/1175, upper brackets lowered 700")]
    # 1) 옛 임시 커튼 4개 지움
    old = [W + "F3SG-4RA1520-14_M08_" + k for k in ("1E", "1R", "2E", "2R")]
    s += [C("solid.remove", bodies=old)] + [C("component.delete", component=c) for c in old]
    # 2) F3SG-4RA0800-14 실물 STEP x2 (STEP Y -> 세계 +Z, 세계 Z = STEP Y - 30)
    #    앞 쌍: STEP Z -> 세계 -X, X -> -Y. 투광 L(STEP Z 100~135) X -2260~-2225, 렌즈 +X. 수광 D 하위 occurrence를 세계 +X 2450(로컬 -Z) -> X 325~360
    s += [C("component.activate", component="U8_PNEU"),
          C("file.insert_step", path=STEP, name="F3SG-4RA0800-14_M08_1", matrix=[0, 0, -1, -2125, -1, 0, 0, -1617.5, 0, 1, 0, -30]),
          C("component.unlock", component="F3SG-4RA0800-14_M08_1"),
          C("occurrence.move", occurrence=9157, path=[18, 9155, 9157], space="world", translate=[2450, 0, 0]),
          C("joint.rigid_group", occurrences=[18, 9155, 9157, 9159, 9161, 9163, 9165, 9167, 9169, 9170])]
    #    옆 쌍: STEP Z -> 세계 -Y. 투광 L Y -1555~-1520, 렌즈 +Y. 수광 D 세계 +Y 1425 -> Y 5~40
    s += [C("component.activate", component="U8_PNEU"),
          C("file.insert_step", path=STEP, name="F3SG-4RA0800-14_M08_2", matrix=[1, 0, 0, -2312.5, 0, 0, -1, -1420, 0, 1, 0, -30]),
          C("component.unlock", component="F3SG-4RA0800-14_M08_2"),
          C("occurrence.move", occurrence=9192, path=[18, 9190, 9192], space="world", translate=[0, 1425, 0]),
          C("joint.rigid_group", occurrences=[18, 9190, 9192, 9194, 9196, 9198, 9200, 9202, 9204, 9205])]
    ren = [("NONE", "1_CAP"), ("NONE (2)", "1R"), ("NONE (3)", "1R_CON"), ("NONE (4)", "1E"), ("NONE (5)", "1E_CON"),
           ("NONE (6)", "2_CAP"), ("NONE (7)", "2R"), ("NONE (8)", "2R_CON"), ("NONE (9)", "2E"), ("NONE (10)", "2E_CON")]
    s += [C("body.rename", body=a, name="F3SG-4RA0800-14_M08_" + b) for a, b in ren]
    s += [C("component.metadata.set", component="F3SG-4RA0800-14_M08_1", part_number="F3SG-4RA0800-14", bom_type="purchased",
            description="Omron F3SG-4RA0800-14 safety light curtain set STEP, front pair: emitter L 1E (FL column +X face) / receiver D 1R (FR column -X face), protective height 800 (M08R, C-32)"),
          C("component.metadata.set", component="F3SG-4RA0800-14_M08_2", part_number="F3SG-4RA0800-14", bom_type="purchased",
            description="Omron F3SG-4RA0800-14 safety light curtain set STEP, side pair: emitter L 2E (Y -1555) / receiver D 2R (R column -Y face), protective height 800 (M08R, C-32)")]
    # 3) 기둥 위끝 줄임(1900 STEP 끝면 오프셋): FL 1530 -> 810, FR·R 1530 -> 805
    s += [C("solid.offset_face", faces=[[-2295, -1635, 1530]], distance=-720, body="HFS8-4080-2370_M08_FL"),
          C("solid.offset_face", faces=[[395, -1635, 1530]], distance=-725, body="HFS8-4080-1900_M08_FR"),
          C("solid.offset_face", faces=[[-2335, 115, 1530]], distance=-725, body="HFS8-4080-1900_M08_R")]
    for o, n, L, z in (("HFS8-4080-2370_M08_FL", "HFS8-4080-1650_M08_FL", 1650, "-840~810"),
                       ("HFS8-4080-1900_M08_FR", "HFS8-4080-1175_M08_FR", 1175, "-370~805"),
                       ("HFS8-4080-1900_M08_R", "HFS8-4080-1175_M08_R", 1175, "-370~805")):
        s += [C("body.rename", body=o, name=n)]
    for o, n, L, z, w in (("HFS8-4080-2370_M08_FL", "HFS8-4080-1650_M08_FL", 1650, "-840~810", "front-left"),
                          ("HFS8-4080-1900_M08_FR", "HFS8-4080-1175_M08_FR", 1175, "-370~805", "front-right"),
                          ("HFS8-4080-1900_M08_R", "HFS8-4080-1175_M08_R", 1175, "-370~805", "rear")):
        s += [C("component.rename", component=o, name=n)]
    for n, L, z, w in (("HFS8-4080-1650_M08_FL", 1650, "-840~810", "front-left"),
                       ("HFS8-4080-1175_M08_FR", 1175, "-370~805", "front-right"),
                       ("HFS8-4080-1175_M08_R", 1175, "-370~805", "rear")):
        s += [C("component.metadata.set", component=n, part_number="HFS8-4080-%d" % L, bom_type="purchased",
                description="Misumi HFS8-4080-1900 STEP, top end face offset to L%d (Z %s), M08 light curtain column %s (M08R, C-32)" % (L, z, w))]
    # 위 캡·위 볼트·너트: U8 리지드 한 줄씩 풀고 옮긴 뒤 다시 묶음
    rj = [7345, 7346, 7347, 7593, 7596, 7597, 7286, 7609, 7612, 7613, 7312]
    mv = [(6991, -720), (6993, -725), (6994, -725), (7543, -700), (7548, -700), (7549, -700), (7113, -700),
          (7571, -700), (7576, -700), (7577, -700), (7151, -700)]
    s += [C("joint.delete", joint=j) for j in rj]
    s += [C("occurrence.move", occurrence=o, space="world", translate=[0, 0, dz]) for o, dz in mv]
    s += [C("joint.rigid_group", occurrences=[18] + [o for o, _ in mv])]
    # 4) 위 금구 4개·LC2F 판 ΔZ -700
    s += [C("component.activate", component="U8_PNEU"),
          C("solid.move", bodies=[W + "F3SG-BRKT_M08_1E_2", W + "F3SG-BRKT_M08_1R_2", W + "F3SG-BRKT_M08_2R_2", W + "F3SG-BRKT_M08_2E_2",
                                  "P_M08_LC2F_BRKT_SM_2"], translate=[0, 0, -700])]
    # 5) CB5-12_M08_PY_LC2F x2 -> STEP대기_CB5-6 (머리 Ø8.5x5 Y -1566~-1561, M5x6 끝 -1555)
    cb = W + "CB5-6_M08_PY_LC2F"
    s += [C("selection.delete", occurrences=["CB5-12_M08_PY_LC2F:1", "CB5-12_M08_PY_LC2F:2"]),
          C("component.activate", component="U8_PNEU"),
          C("component.create", name=cb, parent="U8_PNEU", activate=False),
          C("solid.cylinder", radius=4.25, height=5, base=[-2315, -1566, 100], axis=[0, 1, 0], operation="new", body_name=cb),
          C("solid.cylinder", radius=2.5, height=6, base=[-2315, -1561, 100], axis=[0, 1, 0], operation="join", targets=[cb]),
          C("material.assign", bodies=[cb], material="SCM435"),
          C("component.move_bodies", bodies=[cb], component=cb),
          C("component.metadata.set", component=cb, part_number="CB5-6", bom_type="purchased",
            description="placeholder Misumi CB5-6 (head 8.5x5, M5x6): side emitter L wing -> 2E bracket M5 tap, end at curtain face Y -1555 (M08R, no STEP)"),
          C("occurrence.copy", occurrence=cb + ":1", in_place=True, translate=[0, 0, 600])]
    # 6) 금구 이름 F3SG-BRKT -> F39-LSGF
    for k in ("1E", "1R", "2E", "2R"):
        o, n = W + "F3SG-BRKT_M08_" + k, W + "F39-LSGF_M08_" + k
        s += [C("body.rename", body=o, name=n), C("body.rename", body=o + "_2", name=n + "_2"), C("component.rename", component=o, name=n),
              C("component.metadata.set", component=n, part_number="F39-LSGF", bom_type="purchased",
                description="placeholder Omron F39-LSGF standard mounting bracket x2 (F3SG-R accessory, lower Z 85~115 / upper Z 685~715; model no. D-135 provisional, no STEP) (M08R)")]
    s += [C("joint.rigid_group", occurrences=[18, 9240, 9244])]
    # 7) 금구 4 컴포넌트가 리지드 묶음 밖(dof 6)이었다 -> U8과 묶음
    s += [C("joint.rigid_group", occurrences=[18, 7419, 7429, 7439, 7460])]
    # 8) 대기 포즈·조인트 글리프 숨김
    s += [C("motion.play", study="REST", step=0, quiet=True), C("browser.visibility", visible=False, folder="joints"),
          C("component.activate", component=0)]
    os.makedirs(OUT, exist_ok=True)
    json.dump(s, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": PRJ + "/3D_Modeling/FSAP_v2.5.9.sc", "result": PRJ + "/3D_Modeling/FSAP_v2.6.0.sc",
               "channel": "MCP", "note": "occurrence ids are session ids of the MCP session that opened v2.5.9"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(s), "commands")


if __name__ == "__main__":
    main()
