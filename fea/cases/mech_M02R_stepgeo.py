# -*- coding: utf-8 -*-
"""M02R 해석부(4회차, v2.14.0) — 새 하중 부품 STEP 6개의 꼭짓점 bbox·원통 면(반지름·축·자리)·고유 좌표를 뽑는다.
손계산의 단면을 가정하지 않고 형상 자료의 최소 단면으로 쓰기 위한 것(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로").
CAD를 쓰지 않는다(STEP 글자만 읽음). 결과: fea/results/mech_M02R_stepgeo.json
실행: python -X utf8 -B fea/cases/mech_M02R_stepgeo.py
"""
import re, json, os

ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
D = ROOT + "/tools/out/mech_M02R/stepout"
NAMES = ["P_M02S_SPRING_TAB_1", "P_M02S_SPRING_TAB_2", "P_M02_ARM_SIDE_N", "P_M02_ARM_SIDE_P", "P_M02_ARM_TIE", "P_M02_BASE"]


def parse(path):
    txt = open(path, encoding="latin-1").read()
    txt = re.sub(r"\s*\n\s*", "", txt)
    ent = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*?)\);", txt)}

    def nums(s):
        m = re.search(r"\(([-0-9.Ee+,\s]+)\)", s)
        return tuple(float(v) for v in m.group(1).split(",")) if m else None

    pts = {k: nums(v[1]) for k, v in ent.items() if v[0] == "CARTESIAN_POINT"}
    dirs = {k: nums(v[1]) for k, v in ent.items() if v[0] == "DIRECTION"}
    V = []
    for k, v in ent.items():
        if v[0] == "VERTEX_POINT":
            r = re.findall(r"#(\d+)", v[1])
            if r and r[0] in pts:
                V.append(pts[r[0]])
    bb = [[round(min(p[i] for p in V), 3), round(max(p[i] for p in V), 3)] for i in range(3)]
    cyl = []
    for k, v in ent.items():
        if v[0] == "CYLINDRICAL_SURFACE":
            refs = re.findall(r"#(\d+)", v[1])
            rad = float(v[1].split(",")[-1])
            ax = ent.get(refs[0])
            if not ax:
                continue
            ar = re.findall(r"#(\d+)", ax[1])
            o = pts.get(ar[0]); d = dirs.get(ar[1]) if len(ar) > 1 else None
            cyl.append({"r": round(rad, 3), "origin": [round(c, 3) for c in o], "axis": [round(c, 3) for c in d] if d else None})
    # 같은 축선(반지름·축 방향·축에 수직인 자리)이면 하나로
    seen, uniq = set(), []
    for c in cyl:
        a = c["axis"] or [0, 0, 0]
        main = max(range(3), key=lambda i: abs(a[i]))
        perp = tuple(round(c["origin"][i], 1) for i in range(3) if i != main) if abs(a[main]) > 0.999 else tuple(round(x, 1) for x in c["origin"])
        key = (c["r"], main if abs(a[main]) > 0.999 else tuple(round(x, 2) for x in a), perp)
        if key in seen:
            continue
        seen.add(key); uniq.append(c)
    uq = [sorted({round(p[i], 2) for p in V}) for i in range(3)]
    n_shell = sum(1 for v in ent.values() if v[0] in ("CLOSED_SHELL",))
    n_solid = sum(1 for v in ent.values() if v[0] in ("MANIFOLD_SOLID_BREP",))
    return {"n_vertex": len(V), "bbox": bb, "size": [round(b[1] - b[0], 3) for b in bb], "closed_shell": n_shell, "solid": n_solid,
            "cylinders": sorted(uniq, key=lambda c: (c["r"], c["origin"])), "x": uq[0][:80], "y": uq[1][:80], "z": uq[2][:80]}


out = {"_설명": "M02R v2.14.0 임시 STEP 6개 형상(글자 파싱). 좌표는 STEP 그대로(부품 원점 = 측정 좌표계인지 bbox로 대조)"}
for n in NAMES:
    out[n] = parse(os.path.join(D, n + ".step"))
json.dump(out, open(ROOT + "/fea/results/mech_M02R_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n in NAMES:
    r = out[n]
    print(n, "v", r["n_vertex"], "bbox", r["bbox"], "shell", r["closed_shell"], "solid", r["solid"], "cyl", len(r["cylinders"]))
    for c in r["cylinders"][:14]:
        print("   r", c["r"], "o", c["origin"], "ax", c["axis"])
