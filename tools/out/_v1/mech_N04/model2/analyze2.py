# -*- coding: utf-8 -*-
import json, os, collections
H = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(H, "check2_out.json"), encoding="utf-8").read()
d = json.loads(t[t.find("{") if t.find("{") < t.find("[") or t.find("[") < 0 else t.find("["):])
R = d["results"] if isinstance(d, dict) else d
T = json.load(open(os.path.join(H, "check2_tags.json"), encoding="utf-8"))
S = {"poses_overlap": [], "break_overlap": [], "min_near": {}, "measure": {}, "joints": None, "doc": None}
for tg in T:
    r = R[tg["i"]]
    r = r.get("result", r) if isinstance(r, dict) else r
    if tg["kind"] in ("pose", "break"):
        ov = [(o["a"], o["b"], round(o["volume_mm3"], 1)) for o in r.get("overlaps", [])]
        if ov:
            S["poses_overlap" if tg["kind"] == "pose" else "break_overlap"].append([tg.get("pose") or [tg["study"], tg["step"]], ov])
        for n in r.get("near", []):
            k = tuple(sorted((n["a"], n["b"])))
            if n["distance_mm"] > 0 and (k not in S["min_near"] or n["distance_mm"] < S["min_near"][k][0]):
                S["min_near"][k] = [round(n["distance_mm"], 3), tg.get("pose") or [tg["study"], tg["step"]]]
    elif tg["kind"] == "measure":
        bb = r.get("bodies", [r])[0] if "bodies" in r else r
        S["measure"][tg["body"]] = {"vol": round(bb.get("volume", 0), 1), "bbox": bb.get("bounding_box") or bb.get("bbox")}
    elif tg["kind"] == "joints":
        S["joints"] = {"floating": r.get("floating"), "conflicts": r.get("conflicts"), "n": len(r.get("joints", []))}
    elif tg["kind"] == "doc":
        bs = r.get("bodies", [])
        S["doc"] = {"dirty": r.get("dirty"), "bodies": len(bs), "errors": [f.get("name") for f in r.get("timeline", []) if f.get("error")],
                    "default_mat_N04": [b["name"] for b in bs if b["name"].startswith(("P_N04", "STEP대기_CDJ2B16")) and b.get("material") in (None, "Default")],
                    "hidden": [b["name"] for b in bs if b.get("visible") is False]}
S["min_near"] = {" | ".join(k): v for k, v in sorted(S["min_near"].items(), key=lambda x: x[1][0])[:25]}
json.dump(S, open(os.path.join(H, "check2_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pose overlaps", len(S["poses_overlap"]), S["poses_overlap"][:4]); print("break overlaps", len(S["break_overlap"]), S["break_overlap"][:4])
print("joints", S["joints"]); print("doc", S["doc"])
for k, v in list(S["min_near"].items())[:12]: print(k, v)
