# -*- coding: utf-8 -*-
"""N04 해석 3회차: fix2 STEP 바디별 점 bbox·고유 좌표(면 선택 근거, 옛 좌표 재사용 금지)."""
import re, sys, json, os
out = {}
for path in sys.argv[1:]:
    txt = open(path, encoding="latin-1").read()
    ents = {}
    for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*$", txt, re.M | re.S):
        ents[int(m.group(1))] = m.group(2)
    def pts(root):
        seen, stack, P = set(), [root], []
        while stack:
            i = stack.pop()
            if i in seen or i not in ents: continue
            seen.add(i); e = ents[i]
            if e.startswith("CARTESIAN_POINT"):
                c = re.search(r"\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)", e)
                if c: P.append(tuple(float(v) for v in c.groups()))
                continue
            if e.startswith(("DIRECTION", "VECTOR")): continue
            stack += [int(x) for x in re.findall(r"#(\d+)", e)]
        return P
    for i, e in ents.items():
        if e.startswith("MANIFOLD_SOLID_BREP"):
            name = re.search(r"'([^']*)'", e).group(1).replace("\\X2\\B300\\X0\\\\X2\\AE30\\X0\\", "STEP_WAIT")
            P = pts(i)
            # 축 놓기 원점(0,0,0) 등 축 배치 점이 섞일 수 있어 bbox는 그대로 두고 고유값을 함께 남긴다
            u = [sorted(set(round(p[k], 2) for p in P)) for k in range(3)]
            out[name] = {"file": os.path.basename(path), "n": len(P),
                         "bbox": [[min(x), max(x)] for x in u],
                         "uniq": [x if len(x) <= 24 else x[:12] + ["..."] + x[-12:] for x in u]}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "mech_N04_fea2_stepbbox.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items(): print(k, v["bbox"])
