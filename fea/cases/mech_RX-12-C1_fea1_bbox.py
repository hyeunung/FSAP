# RX-12-C1 해석 1회차(수정 1회차 부품): STEP 꼭짓점(VERTEX_POINT) bbox와 원통면 반지름
import re, json, sys, os
D = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_RX-12-C1/stepout/"
names = ["P_RX12C1_BUMP_BRKT_A", "P_RX12C1_BUMP_LUG_A", "P_RX12C1_BUMP_PAD_A", "P_RX12C1_FLAP_BAR_XN"]
out = {}
for n in names:
    t = open(D + n + ".step", encoding="latin1").read()
    ents = dict(re.findall(r"#(\d+)\s*=\s*(.*?);\s*\n", t, re.S))
    pts = {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\(\s*'[^']*'\s*,\s*\(([^)]*)\)", v)
        if m:
            pts[k] = [float(x) for x in m.group(1).split(",")]
    vp = []
    for k, v in ents.items():
        m = re.match(r"VERTEX_POINT\(\s*'[^']*'\s*,\s*#(\d+)", v)
        if m and m.group(1) in pts:
            vp.append(pts[m.group(1)])
    radii = sorted({round(float(m), 3) for m in re.findall(r"CYLINDRICAL_SURFACE\([^,]*,#\d+,\s*([0-9.Ee+-]+)\)", t)})
    bb = [[round(min(p[i] for p in vp), 3), round(max(p[i] for p in vp), 3)] for i in range(3)] if vp else None
    # 꼭짓점 X·Z 값 목록(단면 판독용)
    xs = sorted({round(p[0], 2) for p in vp}); zs = sorted({round(p[2], 2) for p in vp}); ys = sorted({round(p[1], 2) for p in vp})
    out[n] = dict(bbox=bb, n_vertex=len(vp), cyl_radii=radii, xs=xs[:40], ys=ys[:40], zs=zs[:40])
res = os.path.join(os.path.dirname(__file__), "..", "results", "mech_RX-12-C1_fea1_bbox.json")
json.dump(out, open(res, "w", encoding="utf8"), ensure_ascii=False, indent=1)
for n, v in out.items():
    print(n, v["bbox"], "R", v["cyl_radii"])
    print("  X", v["xs"]); print("  Y", v["ys"]); print("  Z", v["zs"])
