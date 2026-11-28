# -*- coding: utf-8 -*-
"""DP-4 해석부: 바뀐 하중 부품 STEP(보 앞 받침 · T2 안내)과 재질만 바뀐 관 받침(U6)에서 상자 · 원통(구멍 · 굽힘 R) · 평면 자리를 읽는다.
CAD 안 씀(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로"). 읽는 법은 detail_DP-3_stepgeo.py와 같다(parse · holes 함수 그대로).
전(v2.31.1): tools/out/detail/DP-4/m0/pre_CLAMP.step · pre_T2.step(모델링부가 고치기 전에 내보낸 것)
후(v2.31.2): tools/out/detail/DP-4/stepout/P_RXDC03_BEAM_CLAMP.step · P_RXDC03_T2_GUIDE.step
재질만: tools/out/detail/stepout/P_M08_TUBE_BRKT_U6.step(스냅샷 v2.30.6 — 형상 그대로, 서명 상자 · 부피로 대조)
실행: python -X utf8 -B fea/cases/detail_DP-4_stepgeo.py -> fea/results/detail_DP-4_stepgeo.json"""
import re, json, os, hashlib
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
NEW = ROOT + "/tools/out/detail/DP-4/stepout"
PRE = ROOT + "/tools/out/detail/DP-4/m0"
SNAP = ROOT + "/tools/out/detail/stepout"
src = open(ROOT + "/fea/cases/detail_DP-3_stepgeo.py", encoding="utf-8").read()
head = src.split("\nR = {}\n")[0]                       # parse · holes · count 함수부만
ns = {}
exec(compile(head, "detail_DP-3_stepgeo.py(함수부)", "exec"), ns)
holes, parse = ns["holes"], ns["parse"]


def planes(p):
    """평면 자리(축에 나란한 것만): 축 · 좌표."""
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s*\n\s*", "", t)
    ents = dict(re.findall(r"#(\d+)\s*=\s*([^;]*);", t))
    pts, dirs = {}, {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: pts[k] = tuple(float(x) for x in m.group(1).split(",")); continue
        m = re.match(r"DIRECTION\s*\('[^']*',\s*\(([^)]*)\)\)", v)
        if m: dirs[k] = tuple(float(x) for x in m.group(1).split(","))
    out = set()
    for v in ents.values():
        m = re.match(r"PLANE\s*\('[^']*',\s*#(\d+)\)", v)
        if not m: continue
        a = re.match(r"AXIS2_PLACEMENT_3D\s*\('[^']*',\s*#(\d+),\s*#(\d+)", ents[m.group(1)])
        o, d = pts[a.group(1)], dirs[a.group(2)]
        ai = max(range(3), key=lambda i: abs(d[i]))
        if abs(abs(d[ai]) - 1) < 1e-6: out.add(("XYZ"[ai], round(o[ai], 3)))
    return sorted(out)


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


R = {}
for name, new, old in (("P_RXDC03_BEAM_CLAMP", NEW + "/P_RXDC03_BEAM_CLAMP.step", PRE + "/pre_CLAMP.step"),
                       ("P_RXDC03_T2_GUIDE", NEW + "/P_RXDC03_T2_GUIDE.step", PRE + "/pre_T2.step"),
                       ("P_M08_TUBE_BRKT_U6", SNAP + "/P_M08_TUBE_BRKT_U6.step", None)):
    h = holes(new)
    R[name] = {"file": new.replace(ROOT + "/", ""), "sha256_16": sha(new), "bytes": os.path.getsize(new), "new": h, "planes_new": planes(new)}
    if old and os.path.exists(old):
        R[name]["old"] = holes(old); R[name]["planes_old"] = planes(old); R[name]["old_file"] = old.replace(ROOT + "/", "")
    print(name, "상자", h["bbox"], "크기", h["size"])
    for c in h["cyl"]: print("   원통", c)
    print("   평면", R[name]["planes_new"])
    if "old" in R[name]:
        print("   전 상자", R[name]["old"]["bbox"]); [print("   전 원통", c) for c in R[name]["old"]["cyl"]]
json.dump(R, open(ROOT + "/fea/results/detail_DP-4_stepgeo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
