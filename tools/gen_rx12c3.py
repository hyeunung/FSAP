# -*- coding: utf-8 -*-
"""RX-12-C3 생성기 — 긴 매트 MAT_W의 테이프 띠·조각 모형(SIM-01 방식).

python -X utf8 -B tools/gen_rx12c3.py [motion_list_before.json]
입력: tools/out/mech_RX-12-C3/design1/pieces.json(조각 표 · 상자 rest 좌표 · 조인트 원점 · 키, 생성기 design1/pieces.py),
      tools/out/mech_RX-12-C3/design1/keys_W.json(CYCLE_W1·W2 add = 조각 키, replace = 바퀴 키),
      tools/out/mech_RX-12-C3/model/motion_list_before.json(적용 직전 문서의 motion.list)
출력(tools/out/mech_RX-12-C3/model/):
  stage_1_bodies.json   컴포넌트 WP_TAPE_W + WP_TP_W_01~38 · WP_TP_W_SEAM, 상자 바디 44 + 1
  stage_2_joints.json   J_TP_W_01~38 · J_TP_W_SEAM 슬라이더 39(a = WP_MAT_W:1, +Z, flip true, 0~2000)
  study_CYCLE_W1.json · study_CYCLE_W2.json   조각 키 39줄 더함 + J_U4_PRESS · J_U5_FLOAT 바꿈
  study_others.json     나머지 연구에 J_TP_W_* 0 키
  stage_9_finish.json   숨김(조각 · 조인트 · 스케치) · 설명 · REST
  study_diff.json       기존 키 전후 대조(바뀐 줄 = W1·W2의 두 바퀴 키뿐이어야 한다)
기계 부품 · 볼트 · 구매품 변경 0. 임시값: 매트 1500x700 · 오목 500x300(D-01·D-02), 두께 10(D-04), 테이프 두께 1 · 날개 10(D-07).
"""
import json, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(TOOLS, "out", "mech_RX-12-C3")
DES = os.path.join(TASK, "design1")
HERE = os.path.join(TASK, "model")
os.makedirs(HERE, exist_ok=True)
VER = "v2.21.0"

P = json.load(open(os.path.join(DES, "pieces.json"), encoding="utf-8"))
K = json.load(open(os.path.join(DES, "keys_W.json"), encoding="utf-8"))
ROWS = P["pieces"] + [P["seam"]]
JN = [r["joint"] for r in ROWS]
BODIES = [b["name"] for r in ROWS for b in r["bodies"]]


def stage_bodies():
    c = [{"command": "component.create", "params": {"name": "WP_TAPE_W", "parent": 0, "activate": False}}]
    for r in ROWS:
        c.append({"command": "component.create", "params": {"name": r["comp"], "parent": "WP_TAPE_W", "activate": False}})
        for b in r["bodies"]:
            x0, x1, y0, y1, z0, z1 = b["rest"]
            c.append({"command": "solid.box", "params": {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4),
                                                        "corner": [x0, y0, z0], "operation": "new", "body_name": b["name"]}})
        c.append({"command": "component.move_bodies", "params": {"bodies": [b["name"] for b in r["bodies"]], "component": r["comp"]}})
    return c


def stage_joints():
    c = []
    for r in ROWS:
        p = r["origin_rest"]
        c.append({"command": "joint.create", "params": {
            "type": "slider", "name": r["joint"], "flip": True, "limits": [[0, 2000]], "quiet": True,
            "a": {"occurrence": "WP_MAT_W:1", "point": p, "z": [0, 0, 1]},
            "b": {"occurrence": r["comp"] + ":1", "point": p, "z": [0, 0, 1]}}})
    return c


def norm(k):
    return {"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]}


def studies(ml):
    out, diff = {}, {}
    for s in ml["studies"]:
        nm, N = s["name"], s["steps"]
        old = [norm(k) for k in s["keys"]]
        ks = json.loads(json.dumps(old))
        have = {k["joint"] for k in ks}
        assert not (have & set(JN)), (nm, have & set(JN))
        if nm in K:
            assert K[nm]["steps"] == N, (nm, N)
            for k in ks:
                if k["joint"] in K[nm]["replace"]:
                    k["points"] = K[nm]["replace"][k["joint"]]
            assert all(j in have for j in K[nm]["replace"])
            for j in JN:
                ks.append({"joint": j, "points": K[nm]["add"][j]})
        else:
            for j in JN:
                ks.append({"joint": j, "points": [[0, 0], [N, 0]]})
        n0 = len(old)
        chg = [[a["joint"], a["points"], b["points"]] for a, b in zip(old, ks[:n0])
               if json.dumps(a["points"]) != json.dumps([[float(x), float(y)] for x, y in b["points"]])]
        diff[nm] = {"steps": N, "keys_before": n0, "keys_after": len(ks), "added": len(ks) - n0, "changed_existing": chg}
        out[nm] = {"command": "motion.study", "params": {"study": nm, "steps": N, "keys": ks}}
    return out, diff


def main():
    ml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "motion_list_before.json")
    ml = json.load(open(ml_path, encoding="utf-8"))

    def dump(nm, obj, indent=None):
        json.dump(obj, open(os.path.join(HERE, nm), "w", encoding="utf-8"), ensure_ascii=False, indent=indent)
    sb, sj = stage_bodies(), stage_joints()
    dump("stage_1_bodies.json", sb, 1)
    dump("stage_2_joints.json", sj, 1)
    st, diff = studies(ml)
    dump("study_CYCLE_W1.json", [st["CYCLE_W1"]])
    dump("study_CYCLE_W2.json", [st["CYCLE_W2"]])
    others = [v for k, v in st.items() if k not in ("CYCLE_W1", "CYCLE_W2")]
    dump("study_others.json", others)
    dump("study_diff.json", diff, 1)
    fin = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
           {"command": "browser.visibility", "params": {"visible": False, "items": BODIES}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
           {"command": "document.metadata.set", "params": {"key": "description",
                                                           "value": "RX-12-C3 mechanism: MAT_W tape band model WP_TAPE_W (38 pieces + seam, J_TP_W_* stage sliders), CYCLE_W1/W2 keys"}}]
    dump("stage_9_finish.json", fin, 1)
    vol = sum((b["rest"][1] - b["rest"][0]) * (b["rest"][3] - b["rest"][2]) * (b["rest"][5] - b["rest"][4]) for r in ROWS for b in r["bodies"])
    print("comps", 1 + len(ROWS), "bodies", len(BODIES), "joints", len(sj), "cmds", len(sb), len(sj), "vol", round(vol, 2))
    for nm, d in diff.items():
        print(nm, d["steps"], d["keys_before"], "->", d["keys_after"], "changed", [c[0] for c in d["changed_existing"]])


if __name__ == "__main__":
    main()
