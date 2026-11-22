# -*- coding: utf-8 -*-
"""RX-13 해석부 — STEP(v2.20.4)의 원(구멍) 중심·반지름·축을 뽑는다(순 단면·볼트 자리 근거, E-18).
결과: fea/results/mech_RX-13_stepcirc.json"""
import re, json, os
D = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_RX-13/stepout"
names = ["P_RX13_CYL_BRKT", "P_RX13_ROD_EXT", "P_M02_BASE", "P_RX06_CARRIAGE"]
out = {}
for n in names:
    txt = open(os.path.join(D, n + ".step"), encoding="latin-1").read().replace("\n", "")
    pts = {m.group(1): tuple(float(v) for v in m.group(2).split(","))
           for m in re.finditer(r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt)}
    dirs = {m.group(1): tuple(float(v) for v in m.group(2).split(","))
            for m in re.finditer(r"#(\d+)=DIRECTION\('[^']*',\(([^)]*)\)\)", txt)}
    ax = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"#(\d+)=AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),", txt)}
    rows = set()
    for m in re.finditer(r"=CIRCLE\('[^']*',#(\d+),([0-9.]+)\)", txt):
        p, d = ax[m.group(1)]
        c = pts[p]; a = dirs[d]
        rows.add((round(float(m.group(2)), 3), tuple(round(v, 2) for v in c), tuple(round(abs(v), 2) for v in a)))
    out[n] = [{"r": r, "c": list(c), "axis": list(a)} for r, c, a in sorted(rows)]
json.dump(out, open("C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-13_stepcirc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n, rows in out.items():
    print(n)
    for r in rows:
        print("  r", r["r"], "c", r["c"], "ax", r["axis"])
