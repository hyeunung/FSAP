# -*- coding: utf-8 -*-
"""DC2-03 아랫유닛 북 교체 길 생성기 — 기준 v2.0.2 복사본(tools/out/DC2-03/base.sc) -> cand.sc (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_DC2-03_design.md 지시서를 그린다. 동시 과제(E-25) 명령 기록.
python -B tools/gen_v2_dc203.py -> tools/out/DC2-03/model/stage_*.json, tools/out/DC2-03/edit.json, edit_meta.json
좌표: 바늘점 원점, 테이블 면 Z 0, 이송 +Y.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "out", "DC2-03")
LOWER = "STEP대기_867-392342_LOWER"
CB12 = PRJ.replace("\\", "/") + "/purchased-step/CB5-12/CB5-12.stp"
TRAY = "P_DC203_TRAY"
ZB = -250.0          # U1_BASE 윗면 = 받이 판 밑면
T = 1.5              # SUS304 t1.5
RIM_TOP = -235.0     # 테두리 위 끝
HOLES = [(100.0, -130.0), (450.0, -130.0)]


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box_cut(x0, x1, y0, y1, z0, z1, tg):
    return C("solid.box", length=round(x1 - x0, 3), width=round(y1 - y0, 3), height=round(z1 - z0, 3),
             corner=[x0, y0, z0], operation="cut", targets=[tg])


def stage_cuts():
    return [
        # 1) U2_SUB: 칸 <-> 포켓 벽 트기 + 아래팔 비스듬 띠
        box_cut(40, 640, -250, -200, -250, -40, "U2_SUB"),
        # 2) U2_PLATE 밑면 홈(윗면 살 Z -6~0 남김), 바늘판 구멍 Y -65와 이어짐
        box_cut(-30, 30, -130, -65, -40, -6, "U2_PLATE"),
        # 3) LOWER 북 문 자리(임시, 기종 조건 D-10·D-101)
        box_cut(-15, 15, -60, -10, -37, -8, LOWER),
    ]


def stage_tray():
    # 바닥 윤곽: X -80~518 · Y -198~-62. 세 변을 접은 뒤 -Y 테두리 X 400~518을 굽힘 구역째 잘라 비운다
    # (윤곽을 X 400에서 들인 1회차는 edge flange가 -Y 변 전체로 접혀 Q4B 1,770 mm3 겹침 — 기록을 고쳐 다시 돌림).
    zt = ZB + T
    h = RIM_TOP - ZB  # 15, 바깥 가상 꼭짓점(밑면)부터
    return [
        C("sheet.manage_rules", name="SUS304_t1.5", thickness="1.5", bend_radius="1.5", k_factor="0.44",
          corner_relief_shape="rectangular", corner_relief="1.5", active=True),
        C("sketch.create", plane={"origin": [0, 0, ZB], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_DC203_TRAY"),
        C("sketch.rectangle.two_point", p0=[-80, -198], p1=[518, -62]),
        C("sketch.finish"),
        C("sheet.flange", type="base", sketch="SK_DC203_TRAY", rule="SUS304_t1.5", body_name=TRAY),
        C("sheet.flange", type="edge", edges=[[200, -62, zt], [-80, -130, zt], [160, -198, zt]], height=h, angle=90,
          body=TRAY, corner_relief_shape="rectangular", corner_relief=1.5),
        # -Y 테두리 X 400~518 비움(개구 쪽으로 쓸어 꺼냄): 벽 + 굽힘 구역(Y -198~-195)
        # 접힌 굽힘은 가공이 거부된다 -> 펴서 자르고 다시 접는다. 편 -Y 날개 = 굽힘 구역 Y -198.39~-195 + 평판 12
        C("sheet.unfold", body=TRAY),
        C("solid.box", length=119, width=17, height=4, corner=[400, -212, ZB - 1.25], operation="cut", targets=[TRAY]),
        C("sheet.refold", body=TRAY),
        # 구멍 Ø5.5 ×2
        C("sketch.create", plane={"origin": [0, 0, zt + 1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_DC203_TRAY_H"),
    ] + [C("sketch.circle.center", center=[x, y], radius=2.75) for (x, y) in HOLES] + [
        C("sketch.finish"),
        C("solid.extrude", sketch="SK_DC203_TRAY_H", distance=4, direction="negative", operation="cut", targets=[TRAY]),
        C("material.assign", bodies=[TRAY], material="SUS304"),
        C("component.move_bodies", bodies=[TRAY], component="U1_FRAME"),
        # 5) U1_BASE 윗면 기초 구멍 Ø4.2 깊이 13 ×2 (M5 탭 자리)
    ] + [C("solid.cylinder", radius=2.1, height=13, base=[x, y, ZB - 13], operation="cut", targets=["U1_BASE"])
         for (x, y) in HOLES]


def mat_mz(x, y, z):
    """볼트 STEP 국소 +X(나사 방향) -> 월드 -Z, 머리 밑면 = (x, y, z). (M01 gen_v2_m01.mat '-Z'와 같음)"""
    rows = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
    t = [x, y, z]
    return [v for i in range(3) for v in (rows[i] + [t[i]])]


def stage_bolts():
    s, occ, bodies = [], ["U1_FRAME:1"], []
    for i, (x, y) in enumerate(HOLES, 1):
        nm = "CB5-12_DC203_%d" % i
        s += [C("file.insert_step", path=CB12, name=nm, matrix=mat_mz(x, y, ZB + T)),
              C("body.rename", body="Cut-Extrude1", name=nm),
              C("component.metadata.set", component=nm, part_number="CB5-12", bom_type="purchased")]
        occ.append(nm + ":1")
        bodies.append(nm)
    s += [C("material.assign", bodies=bodies, material="SCM435"),
          C("joint.rigid_group", occurrences=occ)]
    return s


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints")]


STAGES = [("cuts", stage_cuts), ("tray", stage_tray), ("bolts", stage_bolts), ("final", stage_final)]


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
    json.dump({"base": "tools/out/DC2-03/base.sc (= 3D_Modeling/FSAP_v2.0.2.sc)", "result": "tools/out/DC2-03/cand.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("edit.json", len(allc))


if __name__ == "__main__":
    main()
