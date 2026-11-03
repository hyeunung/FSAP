# -*- coding: utf-8 -*-
"""DC-05 아랫유닛 구동 자리 이동 생성기 — v1.0.2 -> v1.0.3 -> v1.0.4 (모델링부 2026-11-03, 엔진 v3.7.2)
수정 1회차(v1.0.4): v1.0.3은 C1·C2 자르기를 바디가 움직이는 컴포넌트(U4_X·U5_AIRTABLE)에 들어간 뒤에 잘라
자르기가 월드에 고정됐다(자세마다 형상이 바뀜, mech_DC-05_verify.md 1절). 그 세 자르기(Box51~53)를 지우고,
N00이 컴포넌트에 넣기 전에 만든 원래 피처(Box30 빔, Box33 바늘 홈, Box34 기둥 홈)의 치수를 고친다
(= gen_v1_n00.py 65·70·71행 값을 바꾼 것과 같음. 자르기가 move_bodies 앞에 있어 바디와 함께 움직인다).
python -B tools/gen_v1_dc05.py -> model/stage_1_geom.json(v1.0.2 기준, 자르기 없음), model/stage_2_fix.json,
  edit.json(v1.0.3 -> v1.0.4에 실제로 보낸 명령), edit_full_v102.json(v1.0.2 -> v1.0.4 한 번에)
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
        # C1·C2는 stage_2_fix(원래 피처 치수 고침)로 한다 — 컴포넌트에 든 바디를 자르면 월드에 고정된다
        # 재질(E-09)
        {"command": "material.create", "params": {"name": "SS400", "density_g_cm3": 7.85, "color": "#8a8f96"}},
        {"command": "material.assign", "params": {"bodies": ["U1_LOWER_LINK", "U1_LOWER_STAND", "U1_LOWER_DRIVE"],
                                                  "material": "SS400"}},
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
    ]


def fix_stage(delete_bad=True):
    st = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}}]
    if delete_bad:  # v1.0.3에만 있는 잘못된 자르기 3개
        st.append({"command": "timeline.delete", "params": {"features": ["Box51", "Box52", "Box53"]}})
    st += [
        # C2 U4_X_BEAM X -1050~-760(폭 290): N00 Box30 길이 300 -> 290
        {"command": "timeline.edit", "params": {"feature": "Box30", "set": {"length": "290"}}},
        # C1 바늘 홈 X -1292.5~220: N00 Box33
        {"command": "timeline.edit", "params": {"feature": "Box33", "set": {"corner": [-1292.5, -55, -41], "length": "1512.5"}}},
        # C1 기둥 홈 X -762.5~220: N00 Box34
        {"command": "timeline.edit", "params": {"feature": "Box34", "set": {"corner": [-762.5, -530, -41], "length": "982.5"}}},
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
    ]
    return st


def dump(obj, *parts):
    json.dump(obj, open(os.path.join(OUT, *parts), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    g = geom_stage()
    f = fix_stage(True)
    dump(g, "model", "stage_1_geom.json")
    dump(f, "model", "stage_2_fix.json")
    dump(f, "edit.json")
    dump({"base": "3D_Modeling/FSAP_v1.0.3.sc", "result": "3D_Modeling/FSAP_v1.0.4.sc"}, "edit_meta.json")
    dump(g + fix_stage(False), "edit_full_v102.json")
    print("stage_1", len(g), "stage_2", len(f))


if __name__ == "__main__":
    main()
