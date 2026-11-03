# -*- coding: utf-8 -*-
"""N04 수정 2회차 저장 후 점검(CLI run --results, 저장 없음): 29자세 + 막대 식 꺾임 단계 + 측정 + joint.list"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(H, "poses.json"), encoding="utf-8"))[:-1]
T = json.load(open(os.path.join(H, "poses_tags.json"), encoding="utf-8"))
K = json.load(open(os.path.join(H, "chain_keys.json"), encoding="utf-8"))
B = P[T[0]["i"]]["params"]["bodies"]
cmds = list(P); tags = [dict(t, kind="pose") for t in T]
for st, r in K["studies"].items():
    sel = set()
    for j in ("J_N04_BAR_NP", "J_N04_BAR_PN", "J_N04_CH_P", "J_N04_CH_N"):
        for s, v in r["values"][j]:
            if abs(s - round(s)) > 1e-6:
                sel.update((int(s), int(s) + 1))
    for s in sorted(sel):
        if 0 <= s <= r["steps"]:
            cmds.append({"command": "motion.play", "params": {"study": st, "step": s, "quiet": True}})
            cmds.append({"command": "inspect.clearance", "params": {"bodies": B, "clearance": 0.4}})
            tags.append({"i": len(cmds) - 1, "kind": "break", "study": st, "step": s})
cmds.append({"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}})
CH = ["P_N04_STORE_P", "P_N04_STORE_N", "STEP대기_CDJ2B16-110_P", "STEP대기_CDJ2B16-110_N", "STEP대기_CDJ2B16-110_P_ROD",
      "STEP대기_CDJ2B16-110_N_ROD", "P_N04_STOP_PAD_P", "P_N04_STOP_PAD_N", "P_N04_CYLBKT_P", "P_N04_CYLBKT_N",
      "P_N04_PIN_3", "P_N04_PIN_4", "P_N04_CHAIN_P_HEAD", "P_N04_CHAIN_N_HEAD", "P_N04_CHAIN_NP_BAR",
      "P_N04_CHAIN_PN_BAR", "P_N04_PANEL", "P_N04_NECK"]
for b in CH:
    cmds.append({"command": "inspect.measure", "params": {"body": b}})
    tags.append({"i": len(cmds) - 1, "kind": "measure", "body": b})
cmds.append({"command": "joint.list", "params": {}}); tags.append({"i": len(cmds) - 1, "kind": "joints"})
cmds.append({"command": "document.inspect", "params": {"sketches": False, "joints": False}}); tags.append({"i": len(cmds) - 1, "kind": "doc"})
json.dump(cmds, open(os.path.join(H, "check2.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(tags, open(os.path.join(H, "check2_tags.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(cmds), len(tags))
