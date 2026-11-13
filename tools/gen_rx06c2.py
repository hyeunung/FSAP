# -*- coding: utf-8 -*-
"""RX-06-C2 명령 생성기 — 움직이는 컴포넌트 바디를 고치는 루트 피처를 그 컴포넌트로 옮긴다.

기준 FSAP_v2.15.0.sc -> 결과 FSAP_v2.15.1.sc (형상 값 변화 0, 피처 소속만 바뀜).
실행: python -B tools/gen_rx06c2.py  -> tools/out/mech_RX-06-C2/model/stage_*.json, edit.json, edit_meta.json
앱(MCP)에서는 stage 하나를 execute/batch 하나로 보낸다(단계마다 전체 재계산 11~16분).

방법
- 한 바디만 고치는 피처(Cylinder cut, 스케치 + Extrude cut)는 component.move_features 로 옮긴다.
- Combine(TAP 도구 바디 cut)은 move_features 가 거부한다("works on bodies that would be split
  between components" — 도구 원통을 먼저 옮겨도, 함께 옮겨도 같다). 그래서 Combine + 도구 원통을
  지우고 같은 자리·같은 치수의 Cylinder cut 을 만들어 그 컴포넌트로 옮긴다(형상 같음).
- 빈 피처(Combine41 + 도구 원통 2, Box326)는 지운다.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "out", "mech_RX-06-C2")
MODEL = os.path.join(OUT, "model")

U5_CAR, U7_CASSETTE, U7_FIXED, U6_SENSOR = 36, 4722, 4718, 13
TUBE_BRKT_CST_O = 96011

# 지우는 피처 (id)
DELETE = [
    96432, 96434,                      # Cylinder1175·1176 (P_M08_TUBE_BRKT_CST_O Ø5.5 cut) -> 다시 만듦
    96482, 96483, 96484,               # Cylinder1221·1222 + Combine41 (P_M02_BASE 빈 cut) -> 지움
    96485, 96486, 96487,               # Cylinder1223·1224 + Combine42 (P_M08_KDM_BRKT) -> 다시 만듦
    96488, 96489, 96490,               # Cylinder1225·1226 + Combine43 (P_M03_CAR_PLATE)
    96491, 96492, 96493, 96494, 96495, # Cylinder1227~1230 + Combine44 (P_M03_CHAIN_ARM)
    96496, 96497, 96498, 96499, 96500, # Cylinder1231~1234 + Combine45 (P_M05_CST_PLATE)
    97668,                             # Box326 (지워진 P_M02R_CYLBRKT 를 자르던 빈 cut)
]

# 다시 만드는 구멍: (피처 이름, 대상 바디, base, axis, 반지름, 깊이, 갈 컴포넌트)
HOLES = [
    ("TAP_P_M03_CAR_PLATE_1", "P_M03_CAR_PLATE", [-1990.0, 80.0, 410.0], [0, 1, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M03_CAR_PLATE_2", "P_M03_CAR_PLATE", [-1955.0, 80.0, 410.0], [0, 1, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M03_CHAIN_ARM_1", "P_M03_CHAIN_ARM", [-1950.0, 92.0, 612.0], [1, 0, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M03_CHAIN_ARM_2", "P_M03_CHAIN_ARM", [-1950.0, 92.0, 636.0], [1, 0, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M03_CHAIN_ARM_3", "P_M03_CHAIN_ARM", [-1950.0, 146.0, 818.0], [1, 0, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M03_CHAIN_ARM_4", "P_M03_CHAIN_ARM", [-1950.0, 174.0, 818.0], [1, 0, 0], 2.1, 10, U5_CAR),
    ("TAP_P_M05_CST_PLATE_1", "P_M05_CST_PLATE", [58.0, -152.5, 304.0], [-1, 0, 0], 2.1, 8, U7_CASSETTE),
    ("TAP_P_M05_CST_PLATE_2", "P_M05_CST_PLATE", [58.0, -152.5, 320.0], [-1, 0, 0], 2.1, 8, U7_CASSETTE),
    ("TAP_P_M05_CST_PLATE_3", "P_M05_CST_PLATE", [58.0, -191.5, 162.0], [-1, 0, 0], 2.1, 8, U7_CASSETTE),
    ("TAP_P_M05_CST_PLATE_4", "P_M05_CST_PLATE", [58.0, -191.5, 198.0], [-1, 0, 0], 2.1, 8, U7_CASSETTE),
    ("HOLE_P_M08_TUBE_BRKT_CST_O_1", "P_M08_TUBE_BRKT_CST_O", [64.5, -191.5, 162.0], [-1, 0, 0], 2.75, 7, TUBE_BRKT_CST_O),
    ("HOLE_P_M08_TUBE_BRKT_CST_O_2", "P_M08_TUBE_BRKT_CST_O", [64.5, -191.5, 198.0], [-1, 0, 0], 2.75, 7, TUBE_BRKT_CST_O),
    ("TAP_P_M08_KDM_BRKT_1", "P_M08_KDM_BRKT", [30.0, -190.0, 742.0], [0, 0, -1], 2.1, 10, U7_FIXED),
    ("TAP_P_M08_KDM_BRKT_2", "P_M08_KDM_BRKT", [30.0, -122.0, 742.0], [0, 0, -1], 2.1, 10, U7_FIXED),
]


def stages():
    st = []
    # 1. U7_BINDER(뒤에 Remove51 로 지워지는 바디)를 자르던 Cylinder351·352 -> U7_CASSETTE
    st.append([{"command": "component.move_features",
                "params": {"features": [4735, 4736], "component": U7_CASSETTE}}])
    # 2. Combine 묶음·빈 피처 지움
    st.append([{"command": "timeline.delete", "params": {"features": DELETE}}])
    # 3. 구멍을 Cylinder cut 으로 다시 만들고 컴포넌트로 옮김
    s3 = []
    for name, body, base, axis, r, h, _ in HOLES:
        s3.append({"command": "solid.cylinder",
                   "params": {"radius": r, "height": h, "base": base, "axis": axis,
                              "operation": "cut", "targets": [body], "name": name}})
    for comp in (U5_CAR, U7_CASSETTE, TUBE_BRKT_CST_O, U7_FIXED):
        s3.append({"command": "component.move_features",
                   "params": {"features": [h[0] for h in HOLES if h[6] == comp], "component": comp}})
    st.append(s3)
    # 4. P_M06_BASE 슬롯(SK_DC204_BASE_SLOT + Extrude47) -> U6_SENSOR
    st.append([{"command": "component.move_features",
                "params": {"features": [5216, 5217], "component": U6_SENSOR}}])
    # 5. P_M05_HOLDER 슬롯(SK_DC204_HOLDER_SLOT + Extrude48)·Cylinder753·754 -> U7_FIXED
    st.append([{"command": "component.move_features",
                "params": {"features": [5218, 5219, 9263, 9264], "component": U7_FIXED}}])
    # 6. 이름·설명·대기 포즈·숨김
    st.append([
        {"command": "component.rename", "params": {"component": 0, "name": "FSAP_v2.15.1"}},
        {"command": "document.metadata.set",
         "params": {"key": "description",
                    "value": "RX-06-C2 mechanism: root features on moving-unit bodies moved into U5_CAR/U7_CASSETTE/U7_FIXED/U6_SENSOR, empty cuts removed"}},
        {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
        # REST 연구에 키가 없는 조인트(RX-06-D8)는 따로 0 으로
        {"command": "joint.drive", "params": {"joint": "J_U7_HGT", "value": 0, "quiet": True}},
        {"command": "joint.drive", "params": {"joint": "J_U4_X", "value": 0, "quiet": True}},
        {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
        {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
    ])
    return st


def main(skip=()):
    os.makedirs(MODEL, exist_ok=True)
    st = stages()
    edit = []
    for i, s in enumerate(st, 1):
        with open(os.path.join(MODEL, "stage_%d.json" % i), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
        if i not in skip:
            edit += s
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8") as f:
        json.dump(edit, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"base": "3D_Modeling/FSAP_v2.15.0.sc", "result": "3D_Modeling/FSAP_v2.15.1.sc",
                   "note": "RX-06-C2. 앱(MCP)에서 stage_1~6 순서로 실행 뒤 save. 건너뛴 stage: %s" % (list(skip) or "없음")},
                  f, ensure_ascii=False, indent=1)
    print("stages", len(st), "commands", len(edit))


if __name__ == "__main__":
    import sys
    main(skip=tuple(int(x) for x in sys.argv[1:]))
