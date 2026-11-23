# -*- coding: utf-8 -*-
"""RX-18 생성기 — 운전석 매트 MAT_P의 테이프 띠·조각 모형 WP_TAPE_P + 연구 키(배출 -X 15, CYCLE_V2, 바퀴 높이 키).

python -X utf8 -B tools/gen_rx18.py [motion_list_before.json]
입력: tools/out/mech_RX-18/design/pieces_P.json(조각 표 · 바디 형상 · 조인트 원점, 생성기 design/design.py),
      tools/out/mech_RX-18/design/keys.json(CYCLE_P1·P2 add/replace, CYCLE_L·S·G2 replace, CYCLE_V2 all),
      tools/out/mech_RX-18/model/motion_list_before.json(적용 직전 문서 v2.21.1의 motion.list),
      tools/out/mech_RX-18/model/joint_list_before.json(조인트 이름 확인용)
출력(tools/out/mech_RX-18/model/):
  stage_1_bodies.json   컴포넌트 WP_TAPE_P + WP_TP_P_01~27 · WP_TP_P_SEAM, 바디 39 + 1(상자 25+1 · 네모 9 · 부채꼴 5)
  stage_2_joints.json   J_TP_P_01~27 · J_TP_P_SEAM 슬라이더 28(a = WP_MAT_P:1, +Z, flip true, 0~2000)
  study_<이름>.json      연구마다 motion.study 한 명령(15개, CYCLE_V2는 새 연구)
  study_diff.json       기존 키 전후 대조(바뀌어야 하는 줄 = keys.json replace뿐)
  stage_9_finish.json   REST 0 · 숨김(조각 · 조인트 · 스케치) · 설명
  expect.json           바디별 기대 부피 · bbox(XY)
기계 부품 · 볼트 · 구매품 변경 0. 임시값: 매트 520x890 · 홈 · 띠(D-01~D-03 · D-213), 두께 10(D-04), 테이프 두께 1 · 날개 10(D-07), 배출 자세(D-106).
"""
import json, math, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(TOOLS, "out", "mech_RX-18")
DES = os.path.join(TASK, "design")
HERE = os.path.join(TASK, "model")
os.makedirs(HERE, exist_ok=True)

P = json.load(open(os.path.join(DES, "pieces_P.json"), encoding="utf-8"))
K = json.load(open(os.path.join(DES, "keys.json"), encoding="utf-8"))
ROWS = P["pieces"] + [P["seam"]]
JN = [r["joint"] for r in ROWS]
BODIES = [b["name"] for r in ROWS for b in r["bodies"]]
TOP = "WP_TAPE_P"
MAT = "WP_MAT_P:1"
DESC = "RX-18 mechanism: MAT_P tape band model WP_TAPE_P (27 pieces + seam), eject -X15 keys L/S/G2/P2, new study CYCLE_V2"


def body_cmds(b):
    nm = b["name"]
    if b["type"] == "box":
        x0, x1, y0, y1 = b["box"]
        z0, z1 = b.get("z", [0, 11])
        return [{"command": "solid.box", "params": {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": z1 - z0,
                                                    "corner": [x0, y0, z0], "operation": "new", "body_name": nm}}]
    sk = "SK_" + nm
    c = [{"command": "sketch.create", "params": {"plane": "XY", "name": sk}}]
    if b["type"] == "quad":
        c.append({"command": "sketch.line", "params": {"points": b["pts"], "closed": True}})
    else:  # sector: pts = [안 시작, 밖 시작, 밖 끝, 안 끝]
        A_, B_, C_, D_ = b["pts"]
        sw = b["a1_deg"] - b["a0_deg"]
        c.append({"command": "sketch.line", "params": {"points": [A_, B_]}})
        c.append({"command": "sketch.arc.center_point", "params": {"center": b["center"], "start": B_, "sweep": sw}})
        c.append({"command": "sketch.line", "params": {"points": [C_, D_]}})
        c.append({"command": "sketch.arc.center_point", "params": {"center": b["center"], "start": D_, "sweep": -sw}})
    c.append({"command": "sketch.finish", "params": {}})
    c.append({"command": "solid.extrude", "params": {"distance": 11, "sketch": sk, "operation": "new", "body_name": nm}})
    return c


def bbox_xy(b):
    if b["type"] == "box":
        x0, x1, y0, y1 = b["box"]
        return [x0, x1, y0, y1]
    xs = [p[0] for p in b["pts"]]
    ys = [p[1] for p in b["pts"]]
    if b["type"] == "sector":
        cx, cy = b["center"]
        a0, a1 = sorted([b["a0_deg"], b["a1_deg"]])
        for k in range(-8, 9):
            a = 90 * k
            if a0 - 1e-9 <= a <= a1 + 1e-9:
                xs.append(cx + b["r_out"] * math.cos(math.radians(a)))
                ys.append(cy + b["r_out"] * math.sin(math.radians(a)))
    return [min(xs), max(xs), min(ys), max(ys)]


def stage_bodies():
    c = [{"command": "component.create", "params": {"name": TOP, "parent": 0, "activate": False}}]
    for r in ROWS:
        c.append({"command": "component.create", "params": {"name": r["comp"], "parent": TOP, "activate": False}})
        for b in r["bodies"]:
            c += body_cmds(b)
        c.append({"command": "component.move_bodies", "params": {"bodies": [b["name"] for b in r["bodies"]], "component": r["comp"]}})
    return c


def stage_joints():
    c = []
    for r in ROWS:
        p = r["origin_rest"]
        c.append({"command": "joint.create", "params": {
            "type": "slider", "name": r["joint"], "flip": True, "limits": [[0, 2000]], "quiet": True,
            "a": {"occurrence": MAT, "point": p, "z": [0, 0, 1]},
            "b": {"occurrence": r["comp"] + ":1", "point": p, "z": [0, 0, 1]}}})
    return c


def norm(k):
    return {"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]}


def fl(pts):
    return json.dumps([[float(x), float(y)] for x, y in pts])


def studies(ml, jnames):
    out, diff = {}, {}
    for s in ml["studies"]:
        nm, N = s["name"], s["steps"]
        old = [norm(k) for k in s["keys"]]
        ks = json.loads(json.dumps(old))
        have = {k["joint"] for k in ks}
        assert not (have & set(JN)), (nm, have & set(JN))
        spec = K.get(nm)
        if spec:
            assert spec["steps"] == N, (nm, N)
            assert all(j in have for j in spec["replace"]), nm
            for k in ks:
                if k["joint"] in spec["replace"]:
                    k["points"] = spec["replace"][k["joint"]]
        for j in JN:
            if spec and spec.get("add"):
                ks.append({"joint": j, "points": spec["add"][j]})
            else:
                ks.append({"joint": j, "points": [[0, 0], [N, 0]]})
        n0 = len(old)
        chg = [[a["joint"], a["points"], b["points"]] for a, b in zip(old, ks[:n0]) if fl(a["points"]) != fl(b["points"])]
        want = sorted(spec["replace"]) if spec else []
        assert sorted(c[0] for c in chg) == want, (nm, [c[0] for c in chg], want)
        diff[nm] = {"steps": N, "keys_before": n0, "keys_after": len(ks), "added": len(ks) - n0, "changed_existing": chg}
        out[nm] = {"command": "motion.study", "params": {"study": nm, "steps": N, "keys": ks}}
    # 새 연구 CYCLE_V2
    v = K["CYCLE_V2"]
    ks = [{"joint": j, "points": pts} for j, pts in v["all"].items()]
    miss = [k["joint"] for k in ks if k["joint"] not in jnames]
    assert not miss, miss
    assert not ({k["joint"] for k in ks} & set(JN))
    for j in JN:
        ks.append({"joint": j, "points": [[0, 0], [v["steps"], 0]]})
    out["CYCLE_V2"] = {"command": "motion.study", "params": {"name": "CYCLE_V2", "steps": v["steps"], "keys": ks}}
    diff["CYCLE_V2"] = {"steps": v["steps"], "keys_before": 0, "keys_after": len(ks), "added": len(ks), "new_study": True, "changed_existing": []}
    return out, diff


def main():
    ml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "motion_list_before.json")
    ml = json.load(open(ml_path, encoding="utf-8"))
    jl = json.load(open(os.path.join(HERE, "joint_list_before.json"), encoding="utf-8"))
    jnames = {j["name"] for j in jl["joints"]}

    def dump(nm, obj, indent=None):
        json.dump(obj, open(os.path.join(HERE, nm), "w", encoding="utf-8"), ensure_ascii=False, indent=indent)
    sb, sj = stage_bodies(), stage_joints()
    dump("stage_1_bodies.json", sb, 1)
    dump("stage_2_joints.json", sj, 1)
    st, diff = studies(ml, jnames)
    for nm, cmd in st.items():
        dump("study_%s.json" % nm, [cmd])
    dump("study_order.json", list(st.keys()))
    dump("study_diff.json", diff, 1)
    fin = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
           {"command": "browser.visibility", "params": {"visible": False, "items": BODIES}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
           {"command": "document.metadata.set", "params": {"key": "description", "value": DESC}}]
    dump("stage_9_finish.json", fin, 1)
    exp = {b["name"]: {"vol": b["vol"], "bbox_xy": bbox_xy(b), "z": b.get("z", [0, 11]), "type": b["type"], "comp": r["comp"]}
           for r in ROWS for b in r["bodies"]}
    dump("expect.json", exp, 1)
    vol = sum(b["vol"] for r in ROWS[:-1] for b in r["bodies"])
    print("comps", 1 + len(ROWS), "bodies", len(BODIES), "joints", len(sj), "cmds", len(sb), len(sj), "vol_pieces", round(vol, 1), "seam", ROWS[-1]["bodies"][0]["vol"])
    for nm, d in diff.items():
        print(nm, d["steps"], d["keys_before"], "->", d["keys_after"], "changed", [c[0] for c in d["changed_existing"]])


if __name__ == "__main__":
    main()
