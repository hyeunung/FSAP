# -*- coding: utf-8 -*-
"""DC-07 과제 범위 행정 검사(J_U4_X -200~1217.5, 25 mm) CLI 스크립트 4묶음 생성."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ch = json.load(open(os.path.join(D, "changed_names.json"), encoding="utf-8"))["changed"]
ag = ["U2_BASE", "SV2RL28-1800_N03X_A", "SV2RL28-1800_N03X_B", "STEP대기_S5M250-OPEN", "U9_LOAD_BOX",
      "P_N03_XIBKT", "P_N03_XMBKT", "CB5-20_N03XR"] + ["CB5-20_N03XR (U4_FIX:1/CB5-20_N03XR:%d)" % k for k in range(2, 61)]
vals = [-200 + 25 * i for i in range(57)] + [1217.5]
chunks = [vals[i::4] for i in range(4)]
for n, cv in enumerate(chunks):
    st = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}}]
    for v in cv:
        st.append({"command": "joint.drive", "params": {"joint": "J_U4_X", "value": v, "quiet": True}})
        st.append({"command": "inspect.clearance", "params": {"bodies": ch, "against": ag, "clearance": 1, "min_volume": 0.01}})
    json.dump(st, open(os.path.join(D, "sweep", "sweep_%d.json" % n), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(cv, open(os.path.join(D, "sweep", "sweep_%d_vals.json" % n), "w"))
    print(n, cv)
