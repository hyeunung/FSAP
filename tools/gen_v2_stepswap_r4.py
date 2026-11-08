# -*- coding: utf-8 -*-
"""STEPSWAP r4 — IR1000-01BG 실물 교체(v2.6.7 -> v2.6.8) 관 다시 그리기 단계 생성기.
python -X utf8 -B tools/gen_v2_stepswap_r4.py -> tools/out/mech_STEPSWAP/r4/stage_tubes.json
레귤레이터 실물: 포트 면 X ±17.5(임시 ±12.5), 포트·게이지 Z 482(임시 511), 축 Y 95(임시 95.1).
KQ2L08 관 출구 = 포트 면 + 11.6, 출구 밑 Z = 482 - 16.4 = 465.6.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m08 as m8  # noqa: E402
from gen_v2_m02 import C, mat_assign  # noqa: E402

OUT = os.path.join(ROOT, "out", "mech_STEPSWAP", "r4")
REG_X = [700.0, 800.0, 900.0]
RY, ZT = 95.0, 465.6
ZPORT = [374.5 - 40, 374.5 - 23.5, 374.5 - 7]
OLD = ["TU0805_M08S_REG_IN_%d" % i for i in (1, 2, 3)] + ["TU0805_M08S_REG_OUT_%d" % i for i in (1, 2, 3)]


def tubes():
    T = {}
    for i, x in enumerate(REG_X):
        zi = 305.0 + 10 * i
        xi, xo = x - 29.1, x + 29.1
        T["TU0805_M08T_REG_IN_%d" % (i + 1)] = [(xi, RY, ZT), (xi, RY, zi), (xi, 50, zi), (1140, 50, zi)]
        T["TU0805_M08T_REG_OUT_%d" % (i + 1)] = [(xo, RY, ZT), (xo, RY, ZPORT[i]), (xo, 107.5, ZPORT[i]), (1035, 107.5, ZPORT[i])]
    return T


def stage():
    s = [C("solid.remove", bodies=OLD)] + [C("component.delete", component=c) for c in OLD] + [C("component.activate", component=0)]
    for nm, pts in tubes().items():
        s += [C("component.create", name=nm, parent="U8_PNEU", activate=False)]
        s += json.loads(json.dumps(m8.tube(nm, pts, 4.0, 20.0)).replace('"SK_%s"' % nm, '"SK_%s_SW"' % nm))
        s += [mat_assign([nm], "Default"), C("component.move_bodies", bodies=[nm], component=nm),
              C("component.metadata.set", component=nm, part_number="TU0805", bom_type="purchased",
                description="SMC TU0805 polyurethane tube, cut to length (IR1000 real port X+-29.1 outlet, Z 465.6, STEPSWAP r4)")]
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    s = stage()
    json.dump(s, open(os.path.join(OUT, "stage_tubes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(s), "steps; bends", m8.BENDS)


# ---------------------------------------------------------------- 전체 기록(edit.json) — 앱에 보낸 순서 그대로
STEP = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/"
IR = "IR1000-01BG_M08"
B4 = "CB4-12_M08_REG"


def full():
    s = [C("motion.play", study="REST", step=0, quiet=True), C("component.activate", component="U8_PNEU"),
         # 로컬 X -> 세계 X, 로컬 Y(손잡이 축) -> 세계 +Z, 로컬 Z(게이지 쪽) -> 세계 -Y. 포트 중심 (700, 95, 482)
         C("file.insert_step", path=STEP + "IR1000-01BG/IR1000-01BG.stp", name="IR1000-01BG_M08_N",
           matrix=[1, 0, 0, 700, 0, 0, -1, 95, 0, 1, 0, 482]),
         C("component.activate", component=0),
         C("component.rename", component="IR1000-01BG_M08_N", name=IR)]
    for a, b in (("IR1000-01BG(0)_BODY", "_BODY"), ("G33-2-01_IR1000-BG", "_GAUGE"), ("IR1000(0)_SETNUT", "_SETNUT"), ("P36201023_IR", "_BRKT")):
        s.append(C("body.rename", body=a, name=IR + b))
    s += [C("component.metadata.set", component=IR, part_number="IR1000-01BG", bom_type="purchased",
            description="SMC IR1000-01BG STEP (gauge G33-2-01, bracket P36201023, set nut): precision regulators N/F/S (:1~3) X 700/800/900, "
                        "ports Z 482, knob top Z 565, bracket hung on beam front Y 120 (STEPSWAP r4)"),
          C("material.assign", bodies=[IR + "_BODY"], material="Aluminum"),
          C("material.assign", bodies=[IR + "_GAUGE"], material="ABS Plastic"),
          C("material.assign", bodies=[IR + "_SETNUT", IR + "_BRKT"], material="Steel"),
          C("occurrence.copy", occurrence=IR + ":1", in_place=True, translate=[100, 0, 0]),
          C("occurrence.copy", occurrence=IR + ":1", in_place=True, translate=[200, 0, 0]),
          C("component.activate", component=0)]
    s += [C("joint.rigid_group", occurrences=["U8_PNEU:1", IR + ":%d" % i]) for i in (1, 2, 3)]
    tmp = ["STEP대기_IR1000-01BG_M08_" + k for k in "NFS"]
    s += [C("solid.remove", bodies=sum([[t, t + "_BRKT"] for t in tmp], []))] + [C("component.delete", component=t) for t in tmp]
    s += [C("selection.delete", occurrences=["CB5-12_M08_PY:%d" % i for i in range(1, 7)]),
          C("component.activate", component="U8_PNEU"),
          C("file.insert_step", path=STEP + "CB4-12/CB4-12.stp", name=B4, matrix=[0, -1, 0, 686, 1, 0, 0, 118, 0, 0, 1, 527.8]),
          C("component.activate", component=0),
          C("body.rename", body="Cut-Extrude1", name=B4),
          C("component.metadata.set", component=B4, part_number="CB4-12", bom_type="purchased",
            description="Misumi CB4-12 STEP: IR1000 bracket P36201023 keyhole slot top (Z 527.8) -> beam front wall M4 tap, engagement 8 of t8 (STEPSWAP r4, replaces CB5-12 x6)"),
          C("material.assign", bodies=[B4], material="SCM435")]
    s += [C("occurrence.copy", occurrence=B4 + ":1", in_place=True, translate=[d, 0, 0]) for d in (28, 100, 128, 200, 228)]
    s += [C("component.activate", component=0),
          C("joint.rigid_group", occurrences=["U8_PNEU:1"] + [B4 + ":%d" % i for i in range(1, 7)]),
          C("component.delete", component="KQ2L08-01AS_M08_PX"), C("component.delete", component="KQ2L08-01AS_M08_NX")]
    for side, m, desc in (("PX", [0, 1, 0, 713.5, 0, 0, -1, 95, -1, 0, 0, 482], "OUT port (+X) face X+17.5"),
                          ("NX", [0, -1, 0, 686.5, 0, 0, 1, 95, -1, 0, 0, 482], "IN port (-X) face X-17.5")):
        nm = "KQ2L08-01AS_M08R_" + side
        s += [C("component.activate", component="U8_PNEU"),
              C("file.insert_step", path=STEP + "KQ2L08-01AS/KQ2L08-01AS.stp", name=nm, matrix=m),
              C("body.rename", body="KQ2L08-01AS", name=nm),
              C("component.metadata.set", component=nm, part_number="KQ2L08-01AS", bom_type="purchased",
                description="SMC KQ2L08-01AS elbow STEP, IR1000 %s, Z 482 (STEPSWAP r4)" % desc),
              C("occurrence.copy", occurrence=nm + ":1", in_place=True, translate=[100, 0, 0]),
              C("occurrence.copy", occurrence=nm + ":1", in_place=True, translate=[200, 0, 0])]
    s += [C("component.activate", component=0),
          C("joint.rigid_group", occurrences=["U8_PNEU:1"] + ["KQ2L08-01AS_M08R_%s:%d" % (a, i) for a in ("PX", "NX") for i in (1, 2, 3)])]
    s += stage()
    s += [C("motion.play", study="REST", step=0, quiet=True), C("browser.visibility", visible=False, folder="joints"),
          C("component.rename", component=0, name="FSAP_v2.6.8"),
          C("document.metadata.set", key="description",
            value="STEPSWAP mechanism: STEP-wait IR1000-01BG x3 swapped to SMC STEP (bracket keyhole CB4-12 x6, KQ2L08 elbows and TU0805 tubes re-placed)")]
    return s


if __name__ == "__main__":
    e = full()
    d = os.path.join(ROOT, "out", "mech_STEPSWAP")
    json.dump(e, open(os.path.join(d, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v2.6.7.sc", "result": "3D_Modeling/FSAP_v2.6.8.sc", "generator": "tools/gen_v2_stepswap_r4.py (MCP batch, STEPSWAP r4)"},
              open(os.path.join(d, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("edit.json", len(e))
