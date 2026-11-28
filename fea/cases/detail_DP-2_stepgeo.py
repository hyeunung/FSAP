# -*- coding: utf-8 -*-
"""DP-2 해석부: 바뀐 하중 부품 8개의 STEP에서 상자와 원통(구멍) 자리 · 깊이를 읽는다(CAD 안 씀, E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로").
원통 = CYLINDRICAL_SURFACE(반지름 · 축), 깊이 = 같은 축 위 CIRCLE(같은 반지름) 중심들의 축 방향 범위.
실행: python -X utf8 -B fea/cases/detail_DP-2_stepgeo.py -> fea/results/detail_DP-2_stepgeo.json"""
import re, json, glob, os, math
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
SRC = ROOT + "/tools/out/detail/DP-2/stepout"
NAMES = ["P_RX12C1_FLAP_BAR_L1", "P_RX12C1_FLAP_BAR_L2", "P_RX12C1_FLAP_BAR_L3", "P_RX12C1_FLAP_BAR_XN", "P_RX12C1_FLAP_BAR_XP",
         "P_RX12C1_GS_ARM_BLK", "P_M06_G1_PIN", "P_M06_TOP_PIN"]
OLD = ROOT + "/tools/out/detail/stepout"      # 스냅샷(v2.30.6) STEP — 전 · 후 대조

def parse(p):
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s*\n\s*", "", t)
    ents = dict(re.findall(r"#(\d+)\s*=\s*([^;]*);", t))
    pts, dirs, ax = {}, {}, {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: pts[k] = tuple(float(x) for x in m.group(1).split(",")); continue
        m = re.match(r"DIRECTION\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: dirs[k] = tuple(float(x) for x in m.group(1).split(","))
    for k, v in ents.items():
        m = re.match(r"AXIS2_PLACEMENT_3D\s*\('[^']*',\s*#(\d+),\s*#(\d+)", v)
        if m and m.group(1) in pts and m.group(2) in dirs: ax[k] = (pts[m.group(1)], dirs[m.group(2)])
    verts = [pts[m.group(1)] for v in ents.values() for m in [re.match(r"VERTEX_POINT\s*\('[^']*',\s*#(\d+)\)", v)] if m]
    cyl = []
    for v in ents.values():
        m = re.match(r"CYLINDRICAL_SURFACE\s*\('[^']*',\s*#(\d+),\s*([-\d.Ee+]+)\)", v)
        if m and m.group(1) in ax: cyl.append((ax[m.group(1)], float(m.group(2))))
    circ = []
    for v in ents.values():
        m = re.match(r"CIRCLE\s*\('[^']*',\s*#(\d+),\s*([-\d.Ee+]+)\)", v)
        if m and m.group(1) in ax: circ.append((ax[m.group(1)], float(m.group(2))))
    return verts, cyl, circ

def holes(p):
    verts, cyl, circ = parse(p)
    bb = [[round(min(a[i] for a in verts), 3), round(max(a[i] for a in verts), 3)] for i in range(3)]
    out = {}
    for (o, d), r in cyl:
        ai = max(range(3), key=lambda i: abs(d[i]))                     # 축 방향(주축 정렬 부품)
        key = (ai, round(r, 3), tuple(round(o[i], 2) for i in range(3) if i != ai))
        ext = out.setdefault(key, [])
        for (co, cd), cr in circ:
            if abs(cr - r) < 1e-3 and all(abs(co[i] - o[i]) < 1e-2 for i in range(3) if i != ai):
                ext.append(co[ai])
    rows = []
    for (ai, r, cen), ext in sorted(out.items()):
        if not ext: continue
        rows.append({"axis": "XYZ"[ai], "r": r, "center": cen, "from": round(min(ext), 3), "to": round(max(ext), 3), "depth": round(max(ext) - min(ext), 3)})
    return {"bbox": bb, "size": [round(b[1] - b[0], 3) for b in bb], "cyl": rows}

R = {}
for n in NAMES:
    new = holes(f"{SRC}/{n}.step")
    old = holes(f"{OLD}/{n}.step") if os.path.exists(f"{OLD}/{n}.step") else None
    R[n] = {"new": new, "old": old}
    print(n, "size", new["size"], "원통", len(new["cyl"]), "옛", (len(old["cyl"]) if old else "없음"))
    ok = {(c["axis"], c["r"], c["center"]): c for c in (old["cyl"] if old else [])}
    for c in new["cyl"]:
        o = ok.get((c["axis"], c["r"], c["center"]))
        flag = "" if (o and abs(o["depth"] - c["depth"]) < 1e-3) else ("  <- 전 %s" % (o["depth"] if o else "없음"))
        if flag or c["r"] < 2.2: print("   ", c["axis"], "r", c["r"], c["center"], c["from"], "~", c["to"], "깊이", c["depth"], flag)
json.dump(R, open(ROOT + "/fea/results/detail_DP-2_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
