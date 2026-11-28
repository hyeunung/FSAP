# -*- coding: utf-8 -*-
"""DP-3 해석부: 바뀐 하중 부품 STEP(보 · 덮개 · 이음판 2 · 관 빗 5종)에서 상자와 원통(구멍 · 모서리 R) 자리를 읽는다.
CAD 안 씀(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로"). 읽는 법은 detail_DP-2_stepgeo.py와 같다.
실행: python -X utf8 -B fea/cases/detail_DP-3_stepgeo.py -> fea/results/detail_DP-3_stepgeo.json"""
import re, json, os
from collections import Counter
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
SRC = ROOT + "/tools/out/detail/DP-3/stepout"
OLD = ROOT + "/tools/out/detail/stepout"      # 스냅샷(v2.30.6) STEP — 전 · 후 대조
NAMES = ["P_M07_BEAM", "P_M07_BEAM_CAP", "P_M07_SPLICE_NX", "P_M07_SPLICE_PX", "P_M08_TUBE_COMB_ML_1", "P_M08_TUBE_COMB_ML_5",
         "P_M08_TUBE_COMB_ML_7", "P_M08_TUBE_COMB_ML_8", "P_M08_TUBE_COMB_U5_2"]
# 재질만 바뀐 15품번(형상 그대로 — 스냅샷 STEP)
MAT_ONLY = ["P_M08_TUBE_CLAMP_F_1", "P_M08_TUBE_CLAMP_L_1", "P_M08_TUBE_CLAMP_L_2", "P_M08_TUBE_CLAMP_L_3",
            "P_M08_TUBE_CLAMP_SO_1", "P_M08_TUBE_CLAMP_SO_2", "P_M08_TUBE_CLAMP_SO_3"]


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
    cyl, circ = [], []
    for v in ents.values():
        m = re.match(r"CYLINDRICAL_SURFACE\s*\('[^']*',\s*#(\d+),\s*([-\d.Ee+]+)\)", v)
        if m and m.group(1) in ax: cyl.append((ax[m.group(1)], float(m.group(2))))
        m = re.match(r"CIRCLE\s*\('[^']*',\s*#(\d+),\s*([-\d.Ee+]+)\)", v)
        if m and m.group(1) in ax: circ.append((ax[m.group(1)], float(m.group(2))))
    return verts, cyl, circ


def holes(p):
    verts, cyl, circ = parse(p)
    bb = [[round(min(a[i] for a in verts), 3), round(max(a[i] for a in verts), 3)] for i in range(3)]
    out = {}
    for (o, d), r in cyl:
        ai = max(range(3), key=lambda i: abs(d[i]))
        key = (ai, round(r, 3), tuple(round(o[i], 2) for i in range(3) if i != ai))
        ext = out.setdefault(key, [])
        for (co, cd), cr in circ:
            if abs(cr - r) < 1e-3 and all(abs(co[i] - o[i]) < 1e-2 for i in range(3) if i != ai):
                ext.append(co[ai])
    rows = []
    for (ai, r, cen), ext in sorted(out.items()):
        if not ext: continue
        rows.append({"axis": "XYZ"[ai], "r": r, "center": cen, "from": round(min(ext), 3), "to": round(max(ext), 3), "depth": round(max(ext) - min(ext), 3)})
    return {"bbox": bb, "size": [round(b[1] - b[0], 3) for b in bb], "cyl": rows, "n_vertex": len(verts)}


def count(h):
    c = Counter((x["axis"], x["r"], x["depth"]) for x in h["cyl"])
    return {"%s r%s 깊이%s" % k: n for k, n in sorted(c.items())}


R = {}
for n in NAMES:
    new = holes(f"{SRC}/{n}.step")
    old = holes(f"{OLD}/{n}.step") if os.path.exists(f"{OLD}/{n}.step") else None
    R[n] = {"new": new, "old": old, "count_new": count(new), "count_old": count(old) if old else None}
    print(n, "상자", new["bbox"], "| 전", old["bbox"] if old else "없음")
    print("   원통 후", R[n]["count_new"]); print("   원통 전", R[n]["count_old"])
for n in MAT_ONLY:
    R[n] = {"new": holes(f"{OLD}/{n}.step"), "old": "같음(재질만 바뀜)"}
# 보 구멍 가운데 이번에 생긴 것(전 목록에 없는 축)
ok = {(c["axis"], c["r"], c["center"]) for c in R["P_M07_BEAM"]["old"]["cyl"]}
newh = [c for c in R["P_M07_BEAM"]["new"]["cyl"] if (c["axis"], c["r"], c["center"]) not in ok]
gone = [c for c in R["P_M07_BEAM"]["old"]["cyl"] if (c["axis"], c["r"], c["center"]) not in {(x["axis"], x["r"], x["center"]) for x in R["P_M07_BEAM"]["new"]["cyl"]}]
R["P_M07_BEAM"]["new_holes"] = newh; R["P_M07_BEAM"]["gone_holes"] = gone
print("보 새 원통", len(newh), Counter((c["axis"], c["r"]) for c in newh), "| 없어진 원통", len(gone), Counter((c["axis"], c["r"]) for c in gone))
json.dump(R, open(ROOT + "/fea/results/detail_DP-3_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
