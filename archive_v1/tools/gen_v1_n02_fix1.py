# -*- coding: utf-8 -*-
"""N02 수정 1회차 생성기 — v1.0.6 -> v1.0.7 (모델링부 2026-11-03, 엔진 v3.7.2)
검증 동작 문제(진공 관 길 막힘, mech_N02_verify.md 3절)를 고친다.
python -B tools/gen_v1_n02_fix1.py -> tools/out/mech_N02/model1/stage_*.json, tools/out/mech_N02/edit.json
좌표: 월드 mm, REST(J_U4_X·Y 0, J_U3_ROT 0). 원판 축 = (-900, -400).
- +Y 벽 관 구멍 Ø10: X -920, Z -210 -> X -855, Z -170 (SK_N02_FRAME_H2 원을 옮김).
  지시는 Z -210이지만 그 자리에서 +Y로 나온 관은 ZH10DSA 배기 포트(+X 끝, X -869.2, Y -315.4, Z -208.4)
  앞 35 mm 피팅 공간(M-06)을 지난다. Z -170으로 올려 배기 공간(Z -215.4~-201.4)을 비운다.
- STEP대기_KQ2H06-M5A(곧은) -> STEP대기_KQ2L06-M5A(엘보, 관 출구 +X, 관 축 Y -361).
- 관 TU0604_N02(Ø6, 굽힘 R15, 외곽 원통): 엘보 출구 -> 안쪽 +X -> +Z -> +Y -> 벽 구멍 -> 바깥 수평 -> 진공 포트 위 -> -Z.
"""
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N02")
KQ_OLD, KQL, TUBE = "STEP대기_KQ2H06-M5A", "STEP대기_KQ2L06-M5A", "TU0604_N02"
R_TUBE, R_BEND = 3.0, 15.0
# 관 중심선 꼭짓점(월드)
PTS = [(-882.5, -361.0, -210.0),   # 엘보 소켓 끝
       (-855.0, -361.0, -210.0),   # +X -> +Z
       (-855.0, -361.0, -170.0),   # +Z -> +Y
       (-855.0, -307.0, -170.0),   # +Y -> 진공 포트 쪽(수평, 벽 바깥)
       (-911.45, -315.4, -170.0),  # 수평 -> -Z
       (-911.45, -315.4, -190.0)]  # 진공 포트 윗면


def C(cmd, **p):
    return {"command": cmd, "params": p}


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, s): return [v * s for v in a]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def norm(a): return math.sqrt(dot(a, a))
def unit(a): n = norm(a); return [v / n for v in a]
def rnd(a): return [round(v, 12) for v in a]


def frame(d):
    """법선 d인 평면의 x_dir, y_dir (x × y = d)."""
    ref = [0, 0, 1] if abs(d[2]) < 0.9 else [1, 0, 0]
    x = unit(cross(ref, d))
    y = cross(d, x)
    return rnd(x), rnd(y)


def disc_sketch(p, d, name):
    x, y = frame(d)
    return [C("sketch.create", plane={"origin": rnd(p), "x_dir": x, "y_dir": y}, name=name),
            C("sketch.circle.center", center=[0, 0], radius=R_TUBE),
            C("sketch.finish")]


def tube_cmds():
    st, segs, first = [], [], True
    n = len(PTS)
    start = list(PTS[0])
    k = 0
    for i in range(1, n):
        din = unit(sub(PTS[i], PTS[i - 1]))
        if i < n - 1:
            dout = unit(sub(PTS[i + 1], PTS[i]))
            th = math.acos(max(-1, min(1, dot(din, dout))))
            t = R_BEND * math.tan(th / 2)
            t1 = sub(PTS[i], mul(din, t))
        else:
            t1 = list(PTS[i])
        L = norm(sub(t1, start))
        k += 1
        st += disc_sketch(start, din, "SK_N02_TUBE_S%d" % k)
        p = {"distance": round(L, 12), "operation": "new" if first else "join"}
        if first:
            p["body_name"] = TUBE
        else:
            p["targets"] = [TUBE]
        st.append(C("solid.extrude", **p))
        segs.append({"seg": "S%d" % k, "from": rnd(start), "to": rnd(t1), "L": round(L, 3)})
        first = False
        if i < n - 1:
            bis = unit(sub(dout, din))
            cen = add(PTS[i], mul(bis, R_BEND / math.cos(th / 2)))
            ax = unit(cross(din, dout))
            t2 = add(PTS[i], mul(dout, t))
            st += disc_sketch(t1, din, "SK_N02_TUBE_B%d" % k)
            st.append(C("solid.revolve", axis={"origin": rnd(cen), "dir": rnd(ax)}, angle="%.12f deg" % math.degrees(th),
                        operation="join", targets=[TUBE]))
            segs.append({"seg": "B%d" % k, "from": rnd(t1), "to": rnd(t2), "center": rnd(cen),
                         "deg": round(math.degrees(th), 3), "t": round(t, 3)})
            start = t2
    return st, segs


def stage_fix():
    st = [C("motion.play", study="REST", step=0, quiet=True),
          C("solid.remove", bodies=[KQ_OLD]),
          # 벽 관 구멍 옮김: 스케치 (u, v) = (X, Z)
          C("sketch.edit", sketch="SK_N02_FRAME_H2"),
          C("sketch.move", entities=["c2"], translate=[65, 40]),
          C("sketch.finish")]
    # 엘보 KQ2L06-M5A 임시 외형: 나사 M5 Y -372~-370, 몸 Ø11 Y -370~-354, 소켓 Ø11 X -900~-882.5 (관 축 Y -361, Z -210)
    st += [C("solid.cylinder", radius=5.5, height=16, base=[-900, -370, -210], axis="Y", operation="new", body_name=KQL),
           C("solid.cylinder", radius=2.5, height=2, base=[-900, -372, -210], axis="Y", operation="join", targets=[KQL]),
           C("solid.cylinder", radius=5.5, height=17.5, base=[-900, -361, -210], axis="X", operation="join", targets=[KQL])]
    return st


def stage_tube():
    st, segs = tube_cmds()
    st += [C("material.create", name="PU", density_g_cm3=1.2, color="#3a6fd8"),
           C("material.assign", bodies=[KQL], material="Brass"),
           C("material.assign", bodies=[TUBE], material="PU"),
           C("component.move_bodies", bodies=[KQL, TUBE], component="U4_Y"),
           C("motion.play", study="REST", step=0, quiet=True)]
    return st, segs


def main():
    d = os.path.join(OUT, "model1")
    os.makedirs(d, exist_ok=True)
    s1 = stage_fix()
    s2, segs = stage_tube()
    json.dump(s1, open(os.path.join(d, "stage_1_fix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(s2, open(os.path.join(d, "stage_2_tube.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(segs, open(os.path.join(d, "tube_path.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(s1 + s2, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.6.sc", "result": "3D_Modeling/FSAP_v1.0.7.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("stage_1", len(s1), "stage_2", len(s2))
    for g in segs:
        print(g)


if __name__ == "__main__":
    main()
