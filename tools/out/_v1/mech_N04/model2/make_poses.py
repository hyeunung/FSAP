# -*- coding: utf-8 -*-
"""N04 수정 2회차 과제 범위 자세 검사 명령 생성 (MCP batch/CLI 공용). 출력 poses.json, poses_tags.json"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from gen_N04_chain_keys import vals, phase
H = os.path.dirname(os.path.abspath(__file__))
B = ["P_N04_STORE_P", "P_N04_STORE_N", "STEP대기_CDJ2B16-110_P", "STEP대기_CDJ2B16-110_N",
     "STEP대기_CDJ2B16-110_P_ROD", "STEP대기_CDJ2B16-110_N_ROD", "P_N04_STOP_PAD_P", "P_N04_STOP_PAD_N",
     "P_N04_CYLBKT_P", "P_N04_CYLBKT_N", "P_N04_PIN_3", "P_N04_PIN_4", "P_N04_CHAIN_P_HEAD", "P_N04_CHAIN_N_HEAD",
     "P_N04_CHAIN_A_HEAD", "P_N04_CHAIN_NP_BAR", "P_N04_CHAIN_PN_BAR", "P_N04_SADDLE", "P_N04_CHAIN_NP_TAIL",
     "P_N04_CHAIN_PN_TAIL"]
poses = [(x, y) for x in (-200, 0, 500, 800, 1217.5) for y in (-355, 0, 300, 1155)]
poses += [(0, 538), (0, 536.5), (0, 263.5), (0, 262), (0, 400), (1000, 1000), (1000, -200), (500, 538), (500, 262)]
cmds, tags = [], []
for x, y in poses:
    o = phase(x, y)
    cmds += [{"command": "joint.drive", "params": {"joint": "J_U4_X", "value": x, "quiet": True}},
             {"command": "joint.drive", "params": {"joint": "J_U4_Y", "value": y, "quiet": True}}]
    cmds += [{"command": "joint.drive", "params": {"joint": j, "value": round(v, 4), "quiet": True}} for j, v in vals(x, y, o).items()]
    cmds.append({"command": "inspect.clearance", "params": {"bodies": B, "clearance": 0.4}})
    tags.append({"i": len(cmds) - 1, "pose": [x, y], "open": o})
cmds.append({"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}})
json.dump(cmds, open(os.path.join(H, "poses.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(tags, open(os.path.join(H, "poses_tags.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(cmds), len(tags))
