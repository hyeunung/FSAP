"""DC2-05 먼 쪽 바퀴 밑 받침 — 편집 명령 기록 생성기 (v2.1.5 기준).

python -B tools/gen_dc2_05.py [--upto N] [--bolt-body NAME]
→ tools/out/DC2-05/edit.json
지시서: docs/reports/mechanism/mech_DC2-05_design.md
금지 명령(file.insert_step, solid.fillet, solid.chamfer, solid.offset_face,
component.activate, timeline.delete)은 쓰지 않는다. R0.5·C0.5는 단면·끝 절삭 스케치로 만든다.
CB5-12는 기존 CB5-12_M02_1 STEP 바디를 component.copy_bodies로 복사해 옮긴다.
"""
import json, math, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "DC2-05", "edit.json")

XS = [-1750, -1600, -1400, -1250, -1000, -800, -600, -450]
X0, X1 = -1826.0, -391.0
# 띠 밑면: 도면 두께 8.00 ±0.03, 모델은 7.99(밑면 Z -7.99) — 판 W2 윗면(Z -8)과 같은 평면 맞닿음에서
# boolean이 0.0026 mm 두께 가짜 겹침 95 mm³를 내서(검사 va 1회차) 0.01 띄움. 윗면 Z 0은 그대로.
ZB = -7.99
STRIP = "P_DC205_STRIP"
BOLT_COMP = "CB5-12_DC205"
SRC_BOLT = "CB5-12_M02_1"          # 기존 CB5-12 STEP 바디(머리 위, 머리 밑면 (-176,24,254), 끝 Z 242)
SRC_SEAT = (-176.0, 24.0, 254.0)


def c(cmd, **p):
    return {"command": cmd, "params": p}


def build(bolt_body):
    e = [c("motion.play", study="REST", step=0, quiet=True)]
    # 1) 띠 단면(Y-Z), 윗면 긴 모서리 R0.5, 밑면 긴 모서리 C0.5 → +X 1435
    e.append(c("sketch.create", plane={"origin": [X0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]},
               name="SK_DC205_STRIP"))
    e.append(c("sketch.line", points=[[-24.5, ZB], [24.5, ZB], [25, ZB + 0.5], [25, -0.5]]))
    e.append(c("sketch.arc.center_point", center=[24.5, -0.5], start=[25, -0.5], end=[24.5, 0]))
    e.append(c("sketch.line", points=[[24.5, 0], [-24.5, 0]]))
    e.append(c("sketch.arc.center_point", center=[-24.5, -0.5], start=[-24.5, 0], end=[-25, -0.5]))
    e.append(c("sketch.line", points=[[-25, -0.5], [-25, ZB + 0.5], [-24.5, ZB]]))
    e.append(c("sketch.finish"))
    e.append(c("solid.extrude", sketch="SK_DC205_STRIP", distance=X1 - X0, operation="new",
               body_name=STRIP))
    # 2) 끝 모서리: 윗면 R0.5, 밑면 C0.5 — X-Z 단면 절삭 도구, Y +30 → -30
    s = 0.5 * math.sqrt(0.5)
    e.append(c("sketch.create", plane={"origin": [0, 30, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]},
               name="SK_DC205_ENDS"))
    # -X 윗 끝
    e.append(c("sketch.line", points=[[X0 + 0.5, 0], [X0 + 0.5, 0.3], [X0 - 0.3, 0.3], [X0 - 0.3, -0.5], [X0, -0.5]]))
    e.append(c("sketch.arc.three_point", start=[X0, -0.5], end=[X0 + 0.5, 0],
               through=[X0 + 0.5 - s, -0.5 + s]))
    # +X 윗 끝
    e.append(c("sketch.line", points=[[X1 - 0.5, 0], [X1 - 0.5, 0.3], [X1 + 0.3, 0.3], [X1 + 0.3, -0.5], [X1, -0.5]]))
    e.append(c("sketch.arc.three_point", start=[X1, -0.5], end=[X1 - 0.5, 0],
               through=[X1 - 0.5 + s, -0.5 + s]))
    # -X 밑 끝 C0.5 (선 X+Z = X0-7.5)
    e.append(c("sketch.line", points=[[X0 + 0.8, ZB - 0.3], [X0 - 0.3, ZB + 0.8], [X0 - 0.3, ZB - 0.3]], closed=True))
    # +X 밑 끝 C0.5 (선 Z = X - X1 - 7.5)
    e.append(c("sketch.line", points=[[X1 - 0.8, ZB - 0.3], [X1 + 0.3, ZB + 0.8], [X1 + 0.3, ZB - 0.3]], closed=True))
    e.append(c("sketch.finish"))
    e.append(c("solid.extrude", sketch="SK_DC205_ENDS", distance=60, operation="cut", targets=[STRIP]))
    # 3) 보스 Ø35.6 Z -11.8~-8 (0.1 겹쳐 join), M5 탭 나사 8.3, 밑구멍 끝 Z -3.0
    for x in XS:
        e.append(c("solid.cylinder", radius=17.8, height=3.9, base=[x, 0, -11.8], axis="Z",
                   operation="join", targets=[STRIP]))
    for x in XS:
        e.append(c("solid.hole", position=[x, 0, -11.8], thread="M5", depth=8.8, thread_depth=8.3,
                   targets=[STRIP]))
    # 4) 누름판 Ø50 t4, Z -16~-12, 구멍 Ø5.5
    discs = []
    for i, x in enumerate(XS, 1):
        n = f"P_DC205_DISC_{i}"
        discs.append(n)
        e.append(c("solid.cylinder", radius=25, height=4, base=[x, 0, -16], axis="Z",
                   operation="new", body_name=n))
        e.append(c("solid.cylinder", radius=2.75, height=6, base=[x, 0, -17], axis="Z",
                   operation="cut", targets=[n]))
    e.append(c("material.assign", bodies=[STRIP], material="A5052"))
    e.append(c("material.assign", bodies=discs, material="SUS304"))
    e.append(c("component.move_bodies", bodies=[STRIP] + discs, component="U2_TABLE"))
    # 5) 지울 것: 고하중 볼 28
    e.append(c("component.delete", component="STEP대기_BALL_D25H_M04"))
    # 6) CB5-12 ×8: 기존 STEP 바디 복사 → X축 180° 돌려 머리 밑, 머리 밑면 Z -16
    e.append(c("component.create", name=BOLT_COMP, parent="U2_TABLE", activate=False))
    e.append(c("component.copy_bodies", bodies=[SRC_BOLT], component=BOLT_COMP))
    if bolt_body:
        if bolt_body != BOLT_COMP:
            e.append(c("body.rename", body=bolt_body, name=BOLT_COMP))
        e.append(c("material.assign", bodies=[BOLT_COMP], material="SCM435"))
        sx, sy, sz = SRC_SEAT
        x = XS[0]
        mat = [1, 0, 0, x - sx, 0, -1, 0, 0 + sy, 0, 0, -1, -16 + sz]
        e.append(c("occurrence.move", occurrence=BOLT_COMP + ":1", space="world", matrix=mat))
        e.append(c("component.metadata.set", component=BOLT_COMP, part_number="CB5-12",
                   bom_type="purchased",
                   description="Misumi CB5-12 STEP (copied from CB5-12_M02_1), DC2-05 strip clamp. "
                               "Tightening torque 0.6 N*m (not standard 4.5), medium-strength threadlocker",
                   properties={"조임토크": "0.6 N·m (표준 4.5 N·m 금지, 예압 약 600 N)",
                               "나사고정제": "중강도 (Loctite 243 상당)",
                               "근거": "DC2-05 수정 1회차: 누름판 SUS304 t4 Ø50 4.5 N·m에서 항복 SF 0.53"}))
        for x in XS[1:]:
            e.append(c("occurrence.copy", occurrence=BOLT_COMP + ":1", in_place=True,
                       translate=[x - XS[0], 0.0, 0.0]))
        e.append(c("motion.play", study="REST", step=0, quiet=True))
        e.append(c("browser.visibility", visible=False, folder="joints"))
    return e


if __name__ == "__main__":
    a = sys.argv[1:]
    bb = a[a.index("--bolt-body") + 1] if "--bolt-body" in a else None
    e = build(bb)
    if "--upto" in a:
        e = e[: int(a[a.index("--upto") + 1])]
    out = a[a.index("--out") + 1] if "--out" in a else OUT
    with open(out, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)
    print(out, len(e))
