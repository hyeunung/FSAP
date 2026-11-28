# -*- coding: utf-8 -*-
"""DP-3 해석부 수정 1회차(v2.31.1): 다시 내보낸 보 STEP 하나만 다시 읽는다(E-21 "남은 것만").
나머지 8개 STEP(덮개 · 이음판 2 · 관 빗 5)은 22:56 그대로라 detail_DP-3_stepgeo.json 값을 그대로 쓴다(파일 시각 · sha256으로 확인).
읽는 법은 detail_DP-3_stepgeo.py와 같다(같은 함수 holes를 불러 씀). CAD 안 씀.
실행: python -X utf8 -B fea/cases/detail_DP-3_fea1_stepgeo.py -> fea/results/detail_DP-3_fea1_stepgeo.json"""
import json, os, re, hashlib, time
from collections import Counter
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
SRC = ROOT + "/tools/out/detail/DP-3/stepout"
PREV = ROOT + "/fea/results/detail_DP-3_stepgeo.json"          # v2.31.0 때 읽은 값
OUT = ROOT + "/fea/results/detail_DP-3_fea1_stepgeo.json"

# 같은 읽는 법: 앞 회차 스크립트에서 함수 정의만 가져온다(그 스크립트의 실행부는 돌리지 않는다)
src = open(ROOT + "/fea/cases/detail_DP-3_stepgeo.py", encoding="utf-8").read()
head = src.split("\nR = {}\n")[0]
assert "def holes(p):" in head and "def count(h):" in head
ns = {}
exec(compile(head, "detail_DP-3_stepgeo.py(함수부)", "exec"), ns)
holes, count = ns["holes"], ns["count"]

R = json.load(open(PREV, encoding="utf-8"))
prev_beam = R["P_M07_BEAM"]["new"]                              # v2.31.0
p = f"{SRC}/P_M07_BEAM.step"
new = holes(p)
key = lambda c: (c["axis"], c["r"], tuple(c["center"]))
kp, kn = {key(c): c for c in prev_beam["cyl"]}, {key(c): c for c in new["cyl"]}
gone = [kp[k] for k in kp if k not in kn]
born = [kn[k] for k in kn if k not in kp]
changed = [{"축": k[0], "r": k[1], "가운데": k[2], "전": [kp[k]["from"], kp[k]["to"]], "후": [kn[k]["from"], kn[k]["to"]]}
           for k in kn if k in kp and (kp[k]["from"], kp[k]["to"]) != (kn[k]["from"], kn[k]["to"])]
files = {}
for f in sorted(os.listdir(SRC)):
    if f.startswith(("P_M07_", "P_M08_")) and f.endswith(".step"):
        st = os.stat(f"{SRC}/{f}")
        files[f] = {"mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)), "bytes": st.st_size,
                    "sha256_16": hashlib.sha256(open(f"{SRC}/{f}", "rb").read()).hexdigest()[:16]}
R["P_M07_BEAM"] = {"new": new, "old": R["P_M07_BEAM"]["old"], "prev_v2310": prev_beam, "count_new": count(new), "count_prev_v2310": count(prev_beam),
                   "count_old": R["P_M07_BEAM"].get("count_old"),
                   "fix1_gone": gone, "fix1_born": born, "fix1_changed_extent": changed}
# 다시 뚫은 뒷벽 탭 2개 (X 1230, Z 300 · 600): 앞 · 뒷벽 구멍이 한 축 열쇠로 묶여 범위(120~320)로는 안 보인다 -> 원 자리(Y)를 직접 본다
verts, cyl, circ = ns["parse"](p)
reopen = {}
for z in (300.0, 600.0):
    ys = sorted({round(co[1], 3) for (co, cd), cr in circ if abs(cr - 2.1) < 1e-3 and abs(co[0] - 1230.0) < 1e-2 and abs(co[2] - z) < 1e-2})
    reopen["X 1230 · Z %g" % z] = {"Ø4.2 원 자리 Y": ys, "뒷벽(Y 312~320) 전부 뚫림": 312.0 in ys and 320.0 in ys and not any(312.0 < y < 320.0 for y in ys)}
R["P_M07_BEAM"]["fix1_reopened_taps"] = reopen
R["_fea1"] = {"doc": "FSAP_v2.31.1", "다시 읽은 STEP": "P_M07_BEAM.step", "그대로 쓴 STEP": [f for f in files if f != "P_M07_BEAM.step"], "files": files}
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

dia = lambda rows: dict(sorted(Counter("%s Ø%g" % (c["axis"], 2 * c["r"]) for c in rows).items()))
print("보 상자", new["bbox"], "| v2.31.0", prev_beam["bbox"], "| 같음", new["bbox"] == prev_beam["bbox"])
print("원통 축 수 v2.31.0 -> v2.31.1:", len(prev_beam["cyl"]), "->", len(new["cyl"]))
print("  지름별 전", dia(prev_beam["cyl"])); print("  지름별 후", dia(new["cyl"]))
print("없어진 축", len(gone), [(c["axis"], 2 * c["r"], c["center"]) for c in gone])
print("새 축", len(born), [(c["axis"], 2 * c["r"], c["center"], c["from"], c["to"]) for c in born])
print("범위가 바뀐 축", len(changed), changed[:6])
print("다시 뚫은 탭", reopen)
print("STEP 시각", {f: v["mtime"][11:] for f, v in files.items()})
print("->", OUT)
