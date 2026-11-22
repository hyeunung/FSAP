# -*- coding: utf-8 -*-
"""RX-12-C3 수정 1회차 생성기 — CYCLE_W2 배출 길(⑥)을 '-X 15 먼저, 그다음 -Y 300'으로.

python -X utf8 -B tools/gen_rx12c3_fix1.py [motion_list.json]
근거: 결정로그 RX-12-C3-X1(기각) — 이음매 모형 SEAM_W(두 겹, 바깥면 X 8.5)가 배출(-Y) 중 바인더 턱 벽(X 8~12)을
      0.5 스침(W2 574 · 575, 6.25 · 1.0 mm3). 매트를 몸통 쪽 -X로 15 뺀 뒤 당기면 겹침 0
      (형상 시험 tools/out/mech_RX-12-C3/exception/eject_summary.json).
입력: tools/out/mech_RX-12-C3/model/motion_list_after.json(v2.21.0의 motion.list)
출력(tools/out/mech_RX-12-C3/model1/):
  study_CYCLE_W2.json   J_WP_W_X 키 끝 [478, 0] -> [585, 0] 을 [478, 0] -> [572, 0] -> [573, -15] -> [585, -15] 로.
                        단계 수 585, J_WP_W_Y(573: 330 -> 585: 30)와 다른 키 74줄은 그대로.
  stage_9_finish.json   REST 0 · 숨김(조각 · 조인트 · 스케치) · 설명
  study_diff.json       전후 대조(바뀐 줄 = J_WP_W_X 하나여야 한다)
기계 부품 · 볼트 · 구매품 · 조인트 정의 변경 0. 배출 -Y 300은 임시 자세(D-106), 턱 벽 X 8은 임시 형상(D-211).
"""
import json, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(TOOLS, "out", "mech_RX-12-C3")
HERE = os.path.join(TASK, "model1")
os.makedirs(HERE, exist_ok=True)
STUDY, JOINT = "CYCLE_W2", "J_WP_W_X"
T_HOLD, T_OUT, DX = 572.0, 573.0, -15.0


def norm(k):
    return {"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]}


def main():
    ml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TASK, "model", "motion_list_after.json")
    ml = json.load(open(ml_path, encoding="utf-8"))
    s = [x for x in ml["studies"] if x["name"] == STUDY][0]
    N = s["steps"]
    assert N == 585, N
    old = [norm(k) for k in s["keys"]]
    ks = json.loads(json.dumps(old))
    hit = [k for k in ks if k["joint"] == JOINT]
    assert len(hit) == 1
    pts = hit[0]["points"]
    assert pts[-1] == [float(N), 0.0] and pts[-2][0] <= T_HOLD and abs(pts[-2][1]) < 1e-9, pts[-3:]
    hit[0]["points"] = pts[:-1] + [[T_HOLD, 0.0], [T_OUT, DX], [float(N), DX]]
    y = [k for k in ks if k["joint"] == "J_WP_W_Y"][0]["points"]
    assert y[-2] == [T_OUT, 330.0] and y[-3][1] == 330.0 and y[-3][0] <= T_HOLD, y[-3:]   # 572~573은 X만 움직인다
    chg = [[a["joint"], a["points"][-3:], b["points"][-4:]] for a, b in zip(old, ks) if a != b]
    assert [c[0] for c in chg] == [JOINT], chg

    def dump(nm, obj, indent=None):
        json.dump(obj, open(os.path.join(HERE, nm), "w", encoding="utf-8"), ensure_ascii=False, indent=indent)
    dump("study_CYCLE_W2.json", [{"command": "motion.study", "params": {"study": STUDY, "steps": N, "keys": ks}}])
    dump("study_diff.json", {STUDY: {"steps": N, "keys": len(ks), "changed": chg}}, 1)
    P = json.load(open(os.path.join(TASK, "design1", "pieces.json"), encoding="utf-8"))
    bodies = [b["name"] for r in P["pieces"] + [P["seam"]] for b in r["bodies"]]
    fin = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
           {"command": "browser.visibility", "params": {"visible": False, "items": bodies}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
           {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
           {"command": "document.metadata.set", "params": {"key": "description",
            "value": "RX-12-C3 mechanism fix1: CYCLE_W2 eject path J_WP_W_X -15 at step 573 before -Y 300 (seam clears binder lip)"}}]
    dump("stage_9_finish.json", fin, 1)
    print("keys", len(ks), "changed", chg)


if __name__ == "__main__":
    main()
