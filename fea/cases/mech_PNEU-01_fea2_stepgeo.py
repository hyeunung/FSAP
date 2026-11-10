# -*- coding: utf-8 -*-
"""PNEU-01 해석부 2 — 새 하중 부품 STEP(v2.8.8) 꼭짓점 좌표로 bbox·고유 좌표 평면을 뽑는다(면 선택 근거, E-18).
결과: fea/results/mech_PNEU-01_fea2_stepgeo.json"""
import re, json, sys, os
D = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_PNEU-01/stepout"
names = ["P_M08_TUBE_BRKT_CST_V", "P_M08_TUBE_COMB_KDM", "P_M08_TUBE_CLAMP_SO_1", "P_M08_AIR_IN_BRKT"]
out = {}
for n in names:
    txt = open(os.path.join(D, n + "_v288.step"), encoding="latin-1").read().replace("\n", "")
    pts = {m.group(1): tuple(float(v) for v in m.group(2).split(","))
           for m in re.finditer(r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt)}
    vids = [m.group(1) for m in re.finditer(r"=VERTEX_POINT\('[^']*',#(\d+)\)", txt)]
    V = [pts[v] for v in vids if v in pts]
    bb = [[round(min(p[i] for p in V), 2), round(max(p[i] for p in V), 2)] for i in range(3)]
    uniq = [sorted({round(p[i], 2) for p in V}) for i in range(3)]
    circ = sorted({round(float(m.group(1)), 3) for m in re.finditer(r"=CIRCLE\('[^']*',#\d+,([0-9.]+)\)", txt)})
    out[n] = {"n_vertex": len(V), "bbox": bb, "x": uniq[0][:60], "y": uniq[1][:60], "z": uniq[2][:60], "circle_r": circ}
json.dump(out, open("C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_PNEU-01_fea2_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n, r in out.items():
    print(n, r["n_vertex"], r["bbox"], "R", r["circle_r"][:8])
