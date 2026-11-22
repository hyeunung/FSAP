# -*- coding: utf-8 -*-
"""RX-15 수정 2회차 생성기 — 날을 슬라이드 블록에 맞춤 핀 2개로 건다 (v2.20.1 -> v2.20.2)
python -X utf8 -B tools/gen_rx15_fix2.py
  출력: tools/out/mech_RX-15/model2/stage_h_blade_pins.json (MCP batch · CLI run이 받는 명령 배열)
문제(검도 1회차): 날 등 받이 턱이 누름 판에 있고 누름 판은 볼트 하나에만 물려, 날 + 누름 판이 볼트 축 둘레로 돈다(막는 것은 마찰뿐).
고침: 핀 Ø2 × 10 두 개를 슬라이드 블록(POM)에 8 박고(X 116.25~124.25) 날(X 124.25~124.75)을 꿴다. 축 X, Y -82, Z -30 · -16(간격 14).
  - 날 섕크를 Z -30 -> -33으로 늘림(아래 핀 구멍 살: 밑변 2.0, 볼트 구멍과 2.25).
  - 누름 판도 Z -33까지 늘리고 아래 핀 도피 구멍 Ø2.6(핀은 날 밖으로 1.5 나옴, X 126.25까지). 위 핀은 누름 판 위(Z -18)로 1.0 떠 있다.
  - 볼트 머리 밑 강 와셔(소형 평와셔 M5 5.3 × 9 × 1): 블록 머리 자리 Ø9.5를 2.5 -> 3.5로 파고(X 109.5까지) 그 사이에 와셔. 볼트 자리 그대로.
gen_rx14를 import하지 않는다(import하면 RX-14 묶음 파일을 다시 쓴다)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-15", "model2")
ROOT = {"command": "component.activate", "params": {"component": 0}}
Y0, ZL, ZU = -82.0, -30.0, -16.0     # 핀 축 자리
X0, X1, XB = 116.25, 126.25, 124.25  # 핀 X 범위, 블록 +X 면


def C(cmd, **p):
    return {"command": cmd, "params": p}


def cyl(r, h, base, op, targets=None, body=None, name=None):
    p = {"radius": r, "height": h, "base": [float(v) for v in base], "axis": "X", "operation": op, "name": name}
    if targets:
        p["targets"] = targets
    if body:
        p["body_name"] = body
    return C("solid.cylinder", **p)


def prism(sk, plane, pts, dist, target, name):
    return [C("sketch.create", plane=plane, name=sk), C("sketch.line", points=pts, closed=True), C("sketch.finish"),
            C("solid.extrude", sketch=sk, distance=dist, operation="join", targets=[target], name=name)]


g = []
# --- 슬라이드 블록: 핀 구멍 2, 와셔 자리
n = "P_RX15_CUT_SLIDE"
g += [ROOT, C("component.activate", component=n),
      cyl(1.0, 8.1, [X0, Y0, ZL], "cut", [n], name="RX15_CUT_SLIDE_BLADE_PIN_L"),
      cyl(1.0, 8.1, [X0, Y0, ZU], "cut", [n], name="RX15_CUT_SLIDE_BLADE_PIN_U"),
      cyl(4.75, 1.1, [108.4, Y0, -24.0], "cut", [n], name="RX15_CUT_SLIDE_WASHER_SEAT"),
      ROOT, C("component.metadata.set", component=n, part_number=n,
              description="RX-15 cut slide (one piece), POM milling (provisional): tongue 10 x 139 x 6 in the base groove, cross arm X 95-124.25, "
                          "lug block X 106-124.25 / Y -91..-76 / Z -40..-12.2 (rod M5 tap depth 8, blade bolt D5.5 + cbore D9.5 x 3.5 for a steel washer, "
                          "blade pin holes D2 x 8 at Y -82 / Z -30 and -16 from the +X face), pin post 3 x 4 up through the panel slot (stroke 40 stop at slot end Y -43.5)")]
# --- 날: 섕크 Z -33까지, 핀 구멍 2
n = "P_RX15_BLADE"
g += [C("component.activate", component=n)]
g += prism("SK_RX15_BLADE_SHANK_EXT", {"origin": [XB, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]},
           [[-88.0, -33.0], [-76.0, -33.0], [-76.0, -29.5], [-88.0, -29.5]], 0.5, n, "RX15_BLADE_SHANK_EXT")
g += [cyl(1.0, 0.7, [XB - 0.1, Y0, ZL], "cut", [n], name="RX15_BLADE_PIN_HOLE_L"),
      cyl(1.0, 0.7, [XB - 0.1, Y0, ZU], "cut", [n], name="RX15_BLADE_PIN_HOLE_U"),
      ROOT, C("component.metadata.set", component=n, part_number=n,
              description="RX-15 draw-cut blade t0.5, SK5 HRC58 waterjet + grinding (provisional): shank 12 x 25 (Z -33..-8) with D5.5 bolt hole and "
                          "two D2 pin holes (Y -82 / Z -30 and -16, keyed to the slide lug block), body Z -8..-1.2, "
                          "edge on the top side falling 44 deg to the tip (Y -45..-40 at rest), cuts the tape in the gap X 124-125")]
# --- 누름 판: Z -33까지, 아래 핀 도피 구멍
n = "P_RX15_BLADE_CLAMP"
g += [C("component.activate", component=n)]
g += prism("SK_RX15_BLADE_CLAMP_EXT", {"origin": [0, 0, -33.0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]},
           [[124.75, -89.5], [128.75, -89.5], [128.75, -76.0], [124.75, -76.0]], 3.5, n, "RX15_BLADE_CLAMP_EXT")
g += [cyl(1.3, 4.2, [124.65, Y0, ZL], "cut", [n], name="RX15_BLADE_CLAMP_PIN_RELIEF"),
      ROOT, C("component.metadata.set", component=n, part_number=n,
              description="RX-15 blade clamp plate 15 x 13.5 x 4 (Z -33..-18), SUS304 milling (provisional): M5 through tap, clamps the blade shank on the lug block, "
                          "D2.6 relief for the lower blade pin, back ledge 0.4 x 1.5 x 12 behind the shank back edge Y -88")]
# --- 핀 2
for nm, z in (("P_RX15_BLADE_PIN_L", ZL), ("P_RX15_BLADE_PIN_U", ZU)):
    g += [C("component.create", name=nm, parent="U7_SEAM_CUT"),
          cyl(1.0, X1 - X0, [X0, Y0, z], "new", body=nm, name=nm.replace("P_", "")),
          C("material.assign", bodies=[nm], material="SUS304"),
          ROOT, C("component.metadata.set", component=nm, part_number="P_RX15_BLADE_PIN",
                  description="RX-15 blade locating pin D2 x 10, SUS304 turning (provisional, a JIS B 1354 parallel pin 2 x 10 can replace it): "
                              "pressed 8 into the POM slide lug block from the +X face, passes the blade (t0.5), 1.5 proud. Axis X, Y -82, Z %g" % z)]
# --- 와셔(형번 미정 -> STEP대기_)
nm = "STEP대기_WASHER_M5S_RX15"
g += [C("component.create", name=nm, parent="U7_SEAM_CUT"),
      cyl(4.5, 1.0, [108.5, Y0, -24.0], "new", body=nm, name="RX15_WASHER"),
      cyl(2.65, 1.2, [108.4, Y0, -24.0], "cut", [nm], name="RX15_WASHER_BORE"),
      C("material.assign", bodies=[nm], material="SUS304"),
      ROOT, C("component.metadata.set", component=nm, part_number="WASHER_M5_SMALL", bom_type="purchased",
              description="Provisional shape (model number open): small plain washer M5, 5.3 x 9 x 1 (ISO 7092 / JIS B 1256 small), steel or SUS, "
                          "under the head of CB5-20_RX15 on the POM lug block (spreads the head seat, keeps preload against creep)")]
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    json.dump(g, open(os.path.join(OUT, "stage_h_blade_pins.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("stage_h_blade_pins", len(g))
