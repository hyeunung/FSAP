# -*- coding: utf-8 -*-
"""DC2-06 바늘 옆 바퀴 <-> 머리판 탈착 길 생성기 — v2.1.0 -> v2.1.1 (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_DC2-06_design.md. 형상·부품·볼트·조인트 변경 없음.
설계 안에 동작 연구 MAINT_HEAD(2단계: step 0 = REST, step 1 = J_U4_PRESS -1.867)를 더한다.
python -X utf8 -B tools/gen_v2_dc206.py  -> tools/out/mech_DC2-06/edit.json, edit_meta.json
그다음 MCP batch(또는 solidcraft-cli run edit.json --in FSAP_v2.1.0.sc --save FSAP_v2.1.1.sc).
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC2-06")

REST = {"J_U3_PRESSER": 20.0, "J_U3_NEEDLE": 0.0, "J_U4_PRESS": 8.627, "J_U4_WHEEL_ROT": 0.0,
        "J_U5_X": 0.0, "J_U5_LIFT": 30.0, "J_U5_WHEEL_ROT": 0.0}
for m in "LSG":
    for a in ("X", "Y", "ROT"):
        REST["J_WP_%s_%s" % (m, a)] = 0.0
MAINT = dict(REST, J_U4_PRESS=-1.867)  # 실린더 전진 끝(조인트 한계), 고리 J_U4_CYL_*는 따라감


def edit():
    keys = [{"joint": j, "points": [[0, REST[j]], [1, MAINT[j]]]} for j in REST]
    return [
        {"command": "motion.study", "params": {"name": "MAINT_HEAD", "steps": 1, "keys": keys}},
        {"command": "document.metadata.set", "params": {"key": "description", "value":
            "DC2-06 mechanism: maintenance state MAINT_HEAD (U4 wheel lowered to stroke end) for head plate removal path"}},
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
        {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
    ]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(edit(), f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"base": "3D_Modeling/FSAP_v2.1.0.sc", "result": "3D_Modeling/FSAP_v2.1.1.sc"}, f, indent=1)
    print("edit.json", len(edit()), "명령")
