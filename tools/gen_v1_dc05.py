# -*- coding: utf-8 -*-
"""DC-05 아랫유닛 구동 자리 이동 생성기 — v1.0.2 -> v1.0.3 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_DC-05_select.md(DC-05-C1-R)를 그대로 그린다.
python -B tools/gen_v1_dc05.py -> tools/out/mech_DC-05/model/stage_1_geom.json, tools/out/mech_DC-05/edit.json
좌표: 바늘점 원점 mm, 작업면 Z 0, J_U4_X·J_U4_Y = 0(REST)에서 그린다.
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC-05")
SERVO = "STEP대기_MHMF042L1U2M"  # D-81 임시 외형(플랜지 □60, 몸 110)


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0, "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return {"command": "solid.box", "params": p}


def geom_stage():
    return [
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
        # A1 옛 차지 상자 지움
        {"command": "solid.remove", "params": {"bodies": ["U1_LOWER_DRIVE"]}},
        # B1 각관 90(Y)x60(Z) t4, X 30~650
        box("U1_LOWER_LINK", 30, 650, -45, 45, -120, -60),
        box(None, 29, 651, -41, 41, -116, -64, "cut", ["U1_LOWER_LINK"]),
        # B2 받침 기둥(차지 형상)
        box("U1_LOWER_STAND", 530, 610, -40, 40, -380, -120),
        # B3 서보 끝판 t4 + Ø50 인로 구멍(임시)
        box("U1_LOWER_DRIVE", 650, 654, -45, 45, -120, -60),
        {"command": "solid.cylinder", "params": {"radius": 25, "height": 6, "base": [649, 0, -90], "axis": "X",
                                                 "operation": "cut", "targets": ["U1_LOWER_DRIVE"]}},
        # B4 서보 임시 외형(E-10)
        box(SERVO, 654, 764, -30, 30, -120, -60),
        {"command": "component.move_bodies",
         "params": {"bodies": ["U1_LOWER_LINK", "U1_LOWER_STAND", "U1_LOWER_DRIVE", SERVO], "component": "U1_HEAD"}},
        # C1 테이블 두 홈 -X 끝 40 늘림(J_U4_X 0 좌표)
        box(None, -1292.5, -1252.5, -55, 55, -41, 1, "cut", ["U5_TABLE"]),
        box(None, -762.5, -722.5, -530, -390, -41, 1, "cut", ["U5_TABLE"]),
        # C2 X 빔 +X 10 깎기
        box(None, -760, -749, -1001, 1001, -341, -259, "cut", ["U4_X_BEAM"]),
        # 재질(E-09)
        {"command": "material.create", "params": {"name": "SS400", "density_g_cm3": 7.85, "color": "#8a8f96"}},
        {"command": "material.assign", "params": {"bodies": ["U1_LOWER_LINK", "U1_LOWER_STAND", "U1_LOWER_DRIVE"],
                                                  "material": "SS400"}},
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
    ]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    g = geom_stage()
    json.dump(g, open(os.path.join(OUT, "model", "stage_1_geom.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(g, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("steps", len(g))


if __name__ == "__main__":
    main()
