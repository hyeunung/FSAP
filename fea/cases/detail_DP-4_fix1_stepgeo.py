# -*- coding: utf-8 -*-
"""DP-4 해석부 수정 1회차(v2.31.3): 바뀐 하중 부품 STEP 4개에서 상자 · 원통(구멍 · 굽힘 R · 모서리 R) · 평면 자리를 읽는다.
CAD 안 씀(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로"). 읽는 법은 detail_DP-4_stepgeo.py와 같다(DP-3의 parse · holes 함수 그대로).
입력: tools/out/detail/DP-4/stepout/P_RXDC03_{RISER_BRKT,LEAD_GUIDE,BEAM_CLAMP,T2_GUIDE}.step (2026-11-29 03:51, 모델링부가 v2.31.3에서 내보낸 것)
실행: python -X utf8 -B fea/cases/detail_DP-4_fix1_stepgeo.py -> fea/results/detail_DP-4_fix1_stepgeo.json"""
import re, json, os, hashlib
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
NEW = ROOT + "/tools/out/detail/DP-4/stepout"
src = open(ROOT + "/fea/cases/detail_DP-3_stepgeo.py", encoding="utf-8").read()
head = src.split("\nR = {}\n")[0]                       # parse · holes · count 함수부만
ns = {}
exec(compile(head, "detail_DP-3_stepgeo.py(함수부)", "exec"), ns)
holes = ns["holes"]


def planes(p):
    """평면 자리: 축에 나란한 것은 (축, 좌표), 기운 것은 ('기움', 법선, 원점)."""
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s*\n\s*", "", t)
    ents = dict(re.findall(r"#(\d+)\s*=\s*([^;]*);", t))
    pts, dirs = {}, {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: pts[k] = tuple(float(x) for x in m.group(1).split(",")); continue
        m = re.match(r"DIRECTION\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: dirs[k] = tuple(float(x) for x in m.group(1).split(","))
    out, tilt = set(), set()
    for v in ents.values():
        m = re.match(r"PLANE\s*\('[^']*',\s*#(\d+)\)", v)
        if not m: continue
        a = re.match(r"AXIS2_PLACEMENT_3D\s*\('[^']*',\s*#(\d+),\s*#(\d+)", ents[m.group(1)])
        o, d = pts[a.group(1)], dirs[a.group(2)]
        ai = max(range(3), key=lambda i: abs(d[i]))
        if abs(abs(d[ai]) - 1) < 1e-6: out.add(("XYZ"[ai], round(o[ai], 3)))
        else:
            s = 1 if d[ai] > 0 else -1
            n = tuple(round(s * x, 5) for x in d)
            tilt.add((n, round(s * sum(x * y for x, y in zip(d, o)), 3)))     # 법선 · 원점까지 거리(법선 방향)
    return sorted(out), sorted(tilt)


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


R = {}
for name in ("P_RXDC03_RISER_BRKT", "P_RXDC03_LEAD_GUIDE", "P_RXDC03_BEAM_CLAMP", "P_RXDC03_T2_GUIDE"):
    new = NEW + "/" + name + ".step"
    h = holes(new); pa, pt = planes(new)
    R[name] = {"file": new.replace(ROOT + "/", ""), "sha256_16": sha(new), "bytes": os.path.getsize(new), "new": h, "planes_new": pa, "planes_tilted": pt}
    print(name, "상자", h["bbox"], "크기", h["size"], sha(new), os.path.getsize(new))
    for c in h["cyl"]: print("   원통", c)
    print("   평면", pa)
    if pt: print("   기운 평면(법선, 거리)", pt)
json.dump(R, open(ROOT + "/fea/results/detail_DP-4_fix1_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
