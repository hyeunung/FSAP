# -*- coding: utf-8 -*-
"""DC2-08 생성기 — v2.6.0 -> v2.6.1 (모델링부 2026-11-06)
KDM10 소켓 받침을 U7_FIXED(걸이 P_M05_HOLDER 묶음, J_U7_HGT 자식)로 옮겨 플러그와 같이 높이 조정을 따라가게 한다.
- P_M08_KDM_BRKT 형상 바꿈(앞판 F X14~20·Y-194~-112·Z618~742 + 기둥 P X14~46·Y-200~-194·Z340~742 + 발 G X14~46·Y-200~-180·Z334~340)
- P_M05_HOLDER 날개 C에 M5 탭(Ø4.2) 관통 2 at (26/36, -184.5)
- CB5-12_M08_NZ_KDM ×2 지움, CB5-12_M08_PZ_KDM ×2 새로(머리 밑 Z 340, 축 -Z)
- 소켓 KDM10-06_M08(KDM10S-06)·CB3-10_M08_PX_KDM ×4·받침·새 CB5-12 -> U7_FIXED 리지드 그룹(U8_PNEU 리지드에서 뺌)
python -X utf8 -B tools/gen_v2_dc208.py  -> tools/out/mech_DC2-08/stage_A.json, stage_B.json, stage_C.json, edit.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m08 as m8  # noqa: E402
from gen_v2_m02 import C, box, cyl, mat_assign  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
STEP = PRJ + "/purchased-step/"
OUT = os.path.join(ROOT, "out", "mech_DC2-08")
BR = "P_M08_KDM_BRKT"
HOLDER = "P_M05_HOLDER"
FIX = "U7_FIXED"
YC, ZC = -143.5, 680.0
FOOT_H = [(26.0, -184.5), (36.0, -184.5)]
NEWV = "FSAP_v2.6.1"

# 옆 윤곽(Y, Z): 발 G + 기둥 P + 앞판 F 바깥 -> X 14~46으로 민 뒤 앞판 쪽 X 20~46을 잘라 낸다(같은 평면 join 회피, 실행 규칙 8)
POLY = [(-200, 334), (-180, 334), (-180, 340), (-194, 340), (-194, 618), (-112, 618), (-112, 742), (-200, 742)]


def stage_a():
    s = [C("component.activate", component=0),
         C("solid.remove", bodies=[BR]),
         C("sketch.create", plane={"origin": [14.0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_DC208_BRKT"),
         C("sketch.line", points=[[float(a), float(b)] for a, b in POLY], closed=True),
         C("sketch.finish"),
         C("solid.extrude", sketch="SK_DC208_BRKT", distance=32.0, operation="new", body_name=BR),
         box(None, 20.0, 47.0, -194.0, -111.0, 617.0, 743.0, op="cut", tg=[BR]),          # 앞판 F 두께 6만 남김
         box(None, 13.0, 21.0, YC - 17, YC + 17, ZC - 41, ZC + 41, op="cut", tg=[BR])]   # 피팅 창(그대로)
    for dy in (-14, 14):
        for dz in (-49.5, 49.5):
            s.append(cyl(1.7, [13.0, YC + dy, ZC + dz], 8.0, [1, 0, 0], "cut", [BR]))   # 귀 구멍 Ø3.4 ×4(그대로)
    for x, y in FOOT_H:
        s.append(cyl(2.75, [x, y, 333.0], 8.0, [0, 0, 1], "cut", [BR]))                  # 발 구멍 Ø5.5 ×2
    s += [mat_assign([BR], "A5052"), C("component.move_bodies", bodies=[BR], component=FIX)]
    for x, y in FOOT_H:
        s.append(cyl(2.1, [x, y, 329.9], 4.2, [0, 0, 1], "cut", [HOLDER]))               # 날개 C M5 탭(Ø4.2) 관통
    return s


def stage_b():
    nm = "CB5-12_M08_PZ_KDM"
    p0 = (FOOT_H[0][0], FOOT_H[0][1], 340.0)
    s = [C("component.delete", component="CB5-12_M08_NZ_KDM"),
         C("file.insert_step", path=STEP + "CB5-12/CB5-12.stp", name=nm, matrix=m8.mrow((0, 0, -1), (0, 1, 0), (1, 0, 0), p0)),
         C("body.rename", body="Cut-Extrude1", name=nm),
         C("component.metadata.set", component=nm, part_number="CB5-12", bom_type="purchased",
           description="Misumi CB5-12, KDM bracket foot -> P_M05_HOLDER wing C M5 tap (from top, -Z) (DC2-08)"),
         mat_assign([nm], "SCM435"),
         C("occurrence.reparent", occurrence=nm + ":1", parent=FIX),
         C("occurrence.copy", occurrence=nm + ":1", in_place=True, translate=[FOOT_H[1][0] - FOOT_H[0][0], 0.0, 0.0])]
    old = ["Rigid Group 18:9071", "Rigid Group 18:9075", "Rigid Group 18:9080", "Rigid Group 18:9082",
           "Rigid Group 18:9083", "Rigid Group 18:9084"]
    s += [C("joint.delete", joint=j) for j in old]
    s += [C("occurrence.reparent", occurrence="KDM10-06_M08:1", parent=FIX)]
    s += [C("occurrence.reparent", occurrence="CB3-10_M08_PX_KDM:%d" % i, parent=FIX) for i in range(1, 5)]
    s += [C("joint.rigid_group", occurrences=["U7_FIXED:1", "KDM10-06_M08:1", "KDM10S-06:1"]
            + ["CB3-10_M08_PX_KDM:%d" % i for i in range(1, 5)] + [nm + ":1", nm + ":2"]),
          C("component.metadata.set", component="KDM10-06_M08", part_number="KDM10-06", bom_type="purchased",
            description="SMC KDM10-06 multi-connector STEP: socket KDM10S-06 on bracket (U7_FIXED, follows J_U7_HGT), plug KDM10P-06 on cassette (U7), mating +X (DC2-08)"),
          C("component.metadata.set", component="CB3-10_M08_PX_KDM", part_number="CB3-10", bom_type="purchased",
            description="Misumi CB3-10, KDM10S-06 socket ears -> bracket (U7_FIXED, from bracket back, +X) (DC2-08)")]
    return s


def stage_c():
    return [C("component.activate", component=0),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("component.rename", component=0, name=NEWV),
            C("document.metadata.set", key="description",
              value="DC2-08 mechanism: KDM10 socket bracket moved onto U7 holder so socket follows J_U7_HGT with the plug")]


def main():
    os.makedirs(OUT, exist_ok=True)
    st = {"A": stage_a(), "B": stage_b(), "C": stage_c()}
    allc = []
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, "stage_%s.json" % k), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        allc += v
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print({k: len(v) for k, v in st.items()}, "total", len(allc))


if __name__ == "__main__":
    main()
