# -*- coding: utf-8 -*-
"""RX-15 수정 1회차 생성기 — 날 누름 판 P_RX15_BLADE_CLAMP의 날 등 받이 턱 (v2.20.0 -> v2.20.1)
python -X utf8 -B tools/gen_rx15_fix1.py
  출력: tools/out/mech_RX-15/model1/stage_g_clamp_ledge.json (MCP batch · CLI run이 받는 명령 배열)
턱: 누름 판을 -Y로 1.5 늘이고(Y -89.5~-88) 그 띠를 -X로 0.4 내밀어(X 124.35~124.75) 날 섕크의 등(-Y 변, Y -88)을 받친다.
    날 두께 0.5보다 0.1 낮아 누름 판은 날을 그대로 누른다(블록 +X 면 124.25와 0.1). 높이 Z -30~-18(누름 판 전 높이).
    절단 반력(-Y, 날 끝 Z -3)이 날을 볼트(Y -82, Z -24) 둘레로 돌리면 볼트 위쪽 등이 -Y로 가 턱에 닿는다(Z -24~-18).
gen_rx14를 import하지 않는다(import하면 RX-14 묶음 파일을 다시 쓴다, mech_RX-15_model.md 워크플로우 메모 7)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-15", "model1")


def C(cmd, **p):
    return {"command": cmd, "params": p}


n = "P_RX15_BLADE_CLAMP"
g = [C("component.activate", component=0), C("component.activate", component=n),
     C("sketch.create", plane={"origin": [0, 0, -30.0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_RX15_BLADE_CLAMP_LEDGE"),
     C("sketch.line", points=[[124.35, -89.5], [128.75, -89.5], [128.75, -87.5], [124.75, -87.5], [124.75, -88.0], [124.35, -88.0]], closed=True),
     C("sketch.finish"),
     C("solid.extrude", sketch="SK_RX15_BLADE_CLAMP_LEDGE", distance=12, operation="join", targets=[n], name="RX15_BLADE_CLAMP_LEDGE"),
     C("component.activate", component=0),
     C("component.metadata.set", component=n, part_number=n,
       description="RX-15 blade clamp plate 12 x 13.5 x 4, SUS304 milling (provisional): M5 through tap, clamps the blade shank on the lug block, "
                   "back ledge 0.4 x 1.5 x 12 behind the shank back edge Y -88 (stops blade rotation about the bolt)")]
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    json.dump(g, open(os.path.join(OUT, "stage_g_clamp_ledge.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("stage_g_clamp_ledge", len(g))
