# -*- coding: utf-8 -*-
"""PNEU-01 모델링 생성기 — 기준 3D_Modeling/FSAP_v2.8.5.sc -> FSAP_v2.8.6.sc (모델링부 2026-11-10)
설계안 mech_PNEU-01_design.md / _design1.md / _design2.md, 관 경로 tools/out/mech_PNEU-01/design/routes.json.
python -X utf8 -B tools/gen_v2_pneu01.py -> tools/out/mech_PNEU-01/model/stage_*.json
(밸브 1·3 -Y 10 이동은 앱에서 먼저 한 묶음: stage_0_valve.json)
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "out", "mech_PNEU-01", "model")
STEP = PRJ.replace("\\", "/") + "/purchased-step/"
ROUTES = json.load(open(os.path.join(ROOT, "out", "mech_PNEU-01", "design", "routes.json"), encoding="utf8"))["tubes"]


def C(cmd, **p):
    return {"command": cmd, "params": p}


def r4(v):
    return round(float(v), 4)


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def addv(a, b, k=1.0): return [a[i] + k * b[i] for i in range(3)]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def norm(a):
    n = math.sqrt(dot(a, a)); return [v / n for v in a]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": r4(x1 - x0), "width": r4(y1 - y0), "height": r4(z1 - z0), "corner": [r4(x0), r4(y0), r4(z0)], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, base, h, axis, op="new", tg=None, name=None):
    p = {"radius": r4(r), "height": r4(h), "base": [r4(v) for v in base], "axis": [r4(v) for v in axis] if not isinstance(axis, str) else axis,
         "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


BENDLOG = []


def tube_cmds(name, pts, R, r):
    """꺾은선 + 모서리마다 접선 이어진 원호(반지름 R_i). 꺾임 0인 점은 호 없음."""
    n = len(pts)
    Rl = R if isinstance(R, list) else [R] * (n - 2)
    u = [norm(sub(pts[i + 1], pts[i])) for i in range(n - 1)]
    L = [math.sqrt(dot(sub(pts[i + 1], pts[i]), sub(pts[i + 1], pts[i]))) for i in range(n - 1)]
    t = [0.0] * n
    th = [0.0] * n
    for i in range(1, n - 1):
        c = max(-1.0, min(1.0, dot(u[i - 1], u[i])))
        th[i] = math.acos(c)
        t[i] = Rl[i - 1] * math.tan(th[i] / 2) if th[i] > 1e-4 else 0.0
    for i in range(n - 1):
        if t[i] + t[i + 1] > L[i] + 1e-6:
            raise SystemExit("%s seg %d: tangents %.2f+%.2f > %.2f" % (name, i, t[i], t[i + 1], L[i]))
    sk = "SK_" + name
    s = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    w = 0
    for i in range(n - 1):
        a0 = addv(pts[i], u[i], t[i])
        b0 = addv(pts[i + 1], u[i], -t[i + 1])
        if dot(sub(b0, a0), sub(b0, a0)) > 0.0025:
            s.append(C("sketch.line3d", points=[[r4(v) for v in a0], [r4(v) for v in b0]]))
            w += 1
        j = i + 1
        if j < n - 1 and t[j] > 0:
            P = pts[j]
            st = addv(P, u[i], -t[j])
            en = addv(P, u[j], t[j])
            bis = norm(sub(u[j], u[i]))
            Rj = Rl[j - 1]
            cen = addv(P, bis, Rj / math.cos(th[j] / 2))
            mid = addv(cen, bis, -Rj)
            s.append(C("sketch.arc3d", start=[r4(v) for v in st], through=[r4(v) for v in mid], end=[r4(v) for v in en]))
            w += 1
            BENDLOG.append((name, j, Rj, round(math.degrees(th[j]), 1)))
    s += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (k + 1) for k in range(w)], diameter=2 * r, operation="new", body_name=name)]
    return s


def length(pts, R):
    n = len(pts)
    Rl = R if isinstance(R, list) else [R] * (n - 2)
    tot = 0.0
    for i in range(n - 1):
        tot += math.sqrt(dot(sub(pts[i + 1], pts[i]), sub(pts[i + 1], pts[i])))
    for i in range(1, n - 1):
        u0 = norm(sub(pts[i], pts[i - 1])); u1 = norm(sub(pts[i + 1], pts[i]))
        thh = math.acos(max(-1, min(1, dot(u0, u1))))
        if thh > 1e-4:
            tt = Rl[i - 1] * math.tan(thh / 2)
            tot += Rl[i - 1] * thh - 2 * tt
    return tot


TUBELOG = {}


def place_tube(name, pts, R, r, comp, parent=None, reuse=None, pn=None, desc=None):
    """관 바디를 그리고 컴포넌트에 넣는다. reuse = 옛 관 컴포넌트(이름 바꿔 다시 씀), 없으면 새 컴포넌트."""
    pn = pn or ("TU0805" if r > 3.5 else "TU0604")
    desc = desc or "SMC %s polyurethane tube OD%d, cut to length (PNEU-01 route, bends R>=%s)" % (
        pn, int(2 * r), min(R) if isinstance(R, list) else R)
    TUBELOG[name] = {"pts": [[r4(v) for v in p] for p in pts], "R": R, "r": r, "comp": comp, "len": round(length(pts, R), 1), "pn": pn,
                     "reuse": reuse}
    s = []
    if reuse:
        s.append(C("component.rename", component=reuse, name=name))
    else:
        s.append(C("component.create", name=name, parent=parent, activate=False))
    s += tube_cmds(name, pts, R, r)
    s += [C("material.assign", bodies=[name], material="Default"),
          C("component.move_bodies", bodies=[name], component=name),
          C("component.metadata.set", component=name, part_number=pn, bom_type="purchased", description=desc)]
    return s


def P(name):
    t = ROUTES[name]
    return [list(map(float, p)) for p in t["pts"]], t["R"], float(t["r"])


# ------------------------------------------------------------------ 옛 관
OLD_TUBES = ["TU0604_M08S_U6", "TU0604_M08S_U5_A", "TU0604_M08S_U5_B",
             "TU0604_M08K_U7_1", "TU0604_M08K_U7_2", "TU0604_M08K_U7_3", "TU0604_M08K_U7_4", "TU0604_M08K_U7_5", "TU0604_M08K_U7_6",
             "TU0604_M08_U4C_A", "TU0604_M08_U4C_B", "TU0604_M08_U5C_1", "TU0604_M08_U5C_2",
             "TU0604_M08K_U7C_1", "TU0604_M08K_U7C_2", "TU0604_M08K_U7C_3", "TU0604_M08K_U7C_4", "TU0604_M08K_U7C_5", "TU0604_M08K_U7C_6",
             "TU0805_M08T_REG_IN_1", "TU0805_M08T_REG_IN_3", "TU0805_M08T_REG_OUT_1", "TU0805_M08T_REG_OUT_3"]
# (U4_A 컴포넌트는 지움, U4_B 바디는 이미 Remove52로 지움)
REUSE = {"TU0604_M08P_U4_B": "TU0604_M08S_U4_B", "TU0604_M08P_U6": "TU0604_M08S_U6",
         "TU0604_M08P_U5_A": "TU0604_M08S_U5_A", "TU0604_M08P_U5_B": "TU0604_M08S_U5_B",
         "TU0604_M08P_U7_4_A": "TU0604_M08K_U7_1", "TU0604_M08P_U7_4_B": "TU0604_M08K_U7_2",
         "TU0604_M08P_U7_5_A": "TU0604_M08K_U7_3", "TU0604_M08P_U7_5_B": "TU0604_M08K_U7_4",
         "TU0604_M08P_U7_6_A": "TU0604_M08K_U7_5", "TU0604_M08P_U7_6_B": "TU0604_M08K_U7_6",
         "TU0604_M08P_U4C_A": "TU0604_M08_U4C_A", "TU0604_M08P_U4C_B": "TU0604_M08_U4C_B",
         "TU0604_M08P_U5C_1": "TU0604_M08_U5C_1", "TU0604_M08P_U5C_2": "TU0604_M08_U5C_2",
         "TU0604_M08P_U7C_CUT_A": "TU0604_M08K_U7C_1", "TU0604_M08P_U7C_CUT_B": "TU0604_M08K_U7C_2",
         "TU0604_M08P_U7C_TUCK_A": "TU0604_M08K_U7C_3", "TU0604_M08P_U7C_TUCK_B": "TU0604_M08K_U7C_4",
         "TU0604_M08P_U7C_FEED_A": "TU0604_M08K_U7C_5", "TU0604_M08P_U7C_FEED_B": "TU0604_M08K_U7C_6",
         "TU0805_M08P_MAIN_1": "TU0805_M08T_REG_IN_1", "TU0805_M08P_REG3_IN": "TU0805_M08T_REG_IN_3",
         "TU0604_M08P_REG1_OUT": "TU0805_M08T_REG_OUT_1", "TU0604_M08P_REG3_OUT": "TU0805_M08T_REG_OUT_3"}

# 세로 다리 이음(J_U6_HGT·J_U7_HGT): 고정 쪽은 이음점에서 끝나고 움직이는 쪽은 이음점 위 4에서 시작
JOIN_UP = 4.0
REG_OUT_X = {"TU0604_M08P_REG1_OUT": 727.94, "TU0604_M08P_REG3_OUT": 927.94}   # KQ2L06-01AS 출구(레귤 OUT, 계산)


def stage_tubes(which):
    s = []
    names = [n for n in ROUTES]
    for nm in names:
        pts, R, r = P(nm)
        comp = ROUTES[nm]["comp"]
        if which == 1 and not (nm.startswith("TU0604_M08P_U4") or nm.startswith("TU0604_M08P_U5") or nm.startswith("TU0604_M08P_U6")):
            continue
        if which == 2 and not nm.startswith("TU0604_M08P_U7_"):
            continue
        if which == 3 and not (nm.startswith("TU0604_M08P_U7C") or nm.startswith("TU0805") or nm.startswith("TU0604_M08P_REG")):
            continue
        if nm in REG_OUT_X:
            x = REG_OUT_X[nm]
            pts[0][0] = x
            pts[1][0] = x
        if nm == "TU0805_M08P_MAIN":
            # 티 2개(X 980, 870.9, 몸 반길이 18)에서 끊는다
            p1 = [[1130.0, 108, 280], [998.0, 108, 280]]
            p2 = [[962.0, 108, 280], [888.9, 108, 280]]
            p3 = [[852.9, 108, 280]] + pts[2:]
            s += place_tube("TU0805_M08P_MAIN_1", p1, 40.0, r, comp, reuse=REUSE["TU0805_M08P_MAIN_1"])
            s += place_tube("TU0805_M08P_MAIN_2", p2, 40.0, r, comp, parent="U8_PNEU")
            s += place_tube("TU0805_M08P_MAIN_3", p3, R[1:] if isinstance(R, list) else R, r, comp, parent="U8_PNEU")
            continue
        if nm == "TU0604_M08P_U6" or nm.startswith("TU0604_M08P_U7_"):
            k = len(pts) - 2          # 세로 다리 아래 꼭짓점
            top = pts[k - 1]
            Rl = R if isinstance(R, list) else [R] * (len(pts) - 2)
            ztop = top[2] - Rl[k - 2] * 1.0     # 위 모서리(90°) 접선점
            zbot = pts[k][2] + Rl[k - 1] * 1.0  # 아래 모서리(90°) 접선점
            zj = round((ztop + zbot) / 2.0, 1)
            up = pts[:k] + [[top[0], top[1], zj]]
            lo = [[top[0], top[1], zj + JOIN_UP]] + pts[k:]
            s += place_tube(nm, up, Rl[:k - 1], r, comp, reuse=REUSE.get(nm), parent="U8_PNEU")
            lp = "U6_SENSOR" if nm == "TU0604_M08P_U6" else "U7_FIXED"
            s += place_tube(nm + "_L", lo, [Rl[k - 1]], r, lp, parent=lp,
                            desc="SMC TU0604 tube, lower piece below vertical overlap joint (moves with J_U%s_HGT), same tube as %s" % (
                                "6" if lp == "U6_SENSOR" else "7", nm))
            continue
        s += place_tube(nm, pts, R, r, comp, reuse=REUSE.get(nm), parent=comp)
    return s


# ------------------------------------------------------------------ STEP대기 이음·막음
def tmp(comp, parent, bodies_cmds, bodies, pn, desc):
    return ([C("component.create", name=comp, parent=parent, activate=False)] + bodies_cmds +
            [C("solid.combine", target=bodies[0], tools=bodies[1:], operation="join")] * (1 if len(bodies) > 1 else 0) +
            [C("material.assign", bodies=[bodies[0]], material="Default"),
             C("component.move_bodies", bodies=[bodies[0]], component=comp),
             C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc)])


X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]


def stage_fittings():
    s = []
    W = "STEP대기_"
    # 개별 급기 스페이서(1·3번 밸브 밑, 밸브는 -Y 10 옮김)
    for k, x in ((1, 1049.75), (3, 1070.75)):
        b = W + "SY30M-38-1A-C6_%d" % k
        s += tmp(b, "U8_PNEU", [box(b, x - 4.9, x + 4.9, 90.0, 100.0, 291.7, 373.5), cyl(5.0, [x, 95.0, 285.0], 6.7, Z, name=b + "_B")],
                 [b, b + "_B"], "SY30M-38-1A-C6",
                 "STEP wait: SY3000 individual SUP spacer t10 (temp D-d), C6 SUP port -Z face, valve station %d" % k)
    # 유니온 티 Ø8 ×2
    for k, x in ((1, 980.0), (2, 870.9)):
        b = W + "KQ2T08-00A_%d" % k
        s += tmp(b, "U8_PNEU", [cyl(6.5, [x - 18, 108, 280], 36, X, name=b), cyl(6.5, [x, 108, 280], 18, Z, name=b + "_B")],
                 [b, b + "_B"], "KQ2T08-00A", "STEP wait: SMC union tee OD8 (body L36, branch 18 temp)")
    # 격벽 유니온 + 받침
    b = W + "KQ2E08-00A_1"
    s += tmp(b, "U8_PNEU", [cyl(6.5, [1130, 108, 280], 42, X, name=b), cyl(7.0, [1144, 108, 280], 4, X, name=b + "_N1"),
                            cyl(7.0, [1152, 108, 280], 4, X, name=b + "_N2")],
             [b, b + "_N1", b + "_N2"], "KQ2E08-00A", "STEP wait: SMC bulkhead union OD8 (L42, 2 nuts, temp)")
    s += [box("P_M08_AIR_IN_BRKT", 1148, 1152, 96, 120, 266, 294), box("P_M08_AIR_IN_BRKT_F", 1152, 1166, 116, 120, 266, 294),
          C("solid.combine", target="P_M08_AIR_IN_BRKT", tools=["P_M08_AIR_IN_BRKT_F"], operation="join"),
          cyl(6.6, [1147, 108, 280], 6, X, op="cut", tg=["P_M08_AIR_IN_BRKT"]),
          cyl(2.75, [1159, 115, 273], 6, Y, op="cut", tg=["P_M08_AIR_IN_BRKT"]),
          cyl(2.75, [1159, 115, 287], 6, Y, op="cut", tg=["P_M08_AIR_IN_BRKT"]),
          C("material.assign", bodies=["P_M08_AIR_IN_BRKT"], material="A5052"),
          C("component.create", name="P_M08_AIR_IN_BRKT", parent="U8_PNEU", activate=False),
          C("component.move_bodies", bodies=["P_M08_AIR_IN_BRKT"], component="P_M08_AIR_IN_BRKT"),
          C("component.metadata.set", component="P_M08_AIR_IN_BRKT", part_number="P_M08_AIR_IN_BRKT", bom_type="normal",
            description="Air inlet bulkhead bracket, A5052 t4 laser cut + bend (sheet), 2x M5 to beam front")]
    # 매니폴드 -X 끝판: P 스트레이트, R 소음기 ×2 / +X 끝판 막음 ×3
    b = W + "KQ2H08-01AS_1"
    s += tmp(b, "U8_PNEU", [cyl(6.5, [1020, 107.5, 351], 15, X, name=b), cyl(4.0, [1035, 107.5, 351], 4, X, name=b + "_T")],
             [b, b + "_T"], "KQ2H08-01AS", "STEP wait: SMC straight R1/8-OD8 (hex 14, L19 temp)")
    for k, z in ((1, 334.5), (2, 367.5)):
        b = W + "AN110-01_%d" % k
        s += tmp(b, "U8_PNEU", [cyl(5.5, [1012, 107.5, z], 23, X, name=b), cyl(4.0, [1035, 107.5, z], 4, X, name=b + "_T")],
                 [b, b + "_T"], "AN110-01", "STEP wait: SMC silencer R1/8 (D11 L23 temp)")
    for k, z in ((1, 334.5), (2, 351.0), (3, 367.5)):
        b = W + "TPH-01_%d" % k
        s += tmp(b, "U8_PNEU", [cyl(5.0, [1117, 107.5, z], 6, X, name=b), cyl(4.0, [1112.6, 107.5, z], 4.4, X, name=b + "_T")],
                 [b, b + "_T"], "TPH-01", "STEP wait: R1/8 hex socket plug (temp part no. D-g)")
    b = W + "M-5P_1"
    s += tmp(b, "U8_PNEU", [cyl(4.0, [1070.75, 57.5, 357.35], 4, Y, name=b), cyl(2.5, [1070.75, 61.5, 357.35], 4, Y, name=b + "_T")],
             [b, b + "_T"], "M-5P", "STEP wait: SMC M5 plug for valve 3 B port (single acting U6)")
    # KDM10 빈 구멍 막음(소켓 -X 면 x 11.7, 플러그 +X 면 x 59), 줄 Z 646·714 × 열 Y -153.5·-133.5
    k = 0
    for side, x0, ax, par in (("S", 1.7, X, "U7_FIXED"), ("P", 59.0, X, "U7_CASSETTE")):
        for z in (646.0, 714.0):
            for y in (-153.5, -133.5):
                k += 1
                b = W + "KQ2P-06_%d" % k
                s += tmp(b, par, [cyl(4.0, [x0, y, z], 10, ax, name=b)], [b], "KQ2P-06",
                         "STEP wait: SMC plug OD6 for empty KDM10 port (%s side)" % ("socket" if side == "S" else "plug"))
    return s


def stage_u5_as():
    """U5 대차 KQ2L06-01AS_M08_U5_1·2 -> AS2201F-01-06S(미터 아웃) STEP대기, 같은 출구."""
    s = []
    for k, p, lx in ((1, [-1986.5, 45.5, 231.5], Z), (2, [-1986.5, 45.5, 190.5], [0, -1, 0])):
        ly = [-1, 0, 0]
        A = addv(p, ly, 14.2)
        old = "KQ2L06-01AS_M08_U5_%d" % k
        b = "STEP대기_AS2201F-01-06S_U5_%d" % k
        s += [C("solid.remove", bodies=[old]), C("component.rename", component=old, name=b),
              cyl(6.0, addv(A, lx, -14.0), 29.5, lx, name=b),
              cyl(5.0, p, 14.2, ly, name=b + "_N"),
              cyl(4.0, addv(A, lx, -26.0), 12.0, lx, name=b + "_K"),
              C("solid.combine", target=b, tools=[b + "_N", b + "_K"], operation="join"),
              C("material.assign", bodies=[b], material="Default"),
              C("component.move_bodies", bodies=[b], component=b),
              C("component.metadata.set", component=b, part_number="AS2201F-01-06S", bom_type="purchased",
                description="STEP wait: SMC AS2201F-01-06S elbow speed controller meter-out R1/8-OD6 (U5 lift), outlet as KQ2L06-01AS (temp D-c)")]
    return s


def stage_reg_out():
    s = [C("component.delete", component="KQ2L08-01AS_M08R_PX")]
    return s


def stage_reg_out2():
    s = []
    lx, ly = [0, 0, -1], [1, 0, 0]
    lz = cross(lx, ly)
    for k, x in ((1, 713.74), (3, 913.74)):
        comp = "KQ2L06-01AS_M08R_OUT_%d" % k
        p = [x, 95.0, 481.2]
        s += [C("file.insert_step", path=STEP + "KQ2L06-01AS/KQ2L06-01AS.stp", name=comp,
                matrix=[r4(v) for i in range(3) for v in (lx[i], ly[i], lz[i], p[i])]),
              C("body.rename", body="KQ2L06-01AS", name=comp),
              C("component.metadata.set", component=comp, part_number="KQ2L06-01AS", bom_type="purchased",
                description="SMC KQ2L06-01AS elbow R1/8-OD6 on IR1000 OUT %d (PNEU-01, was KQ2L08-01AS)" % k),
              C("material.assign", bodies=[comp], material="Default"),
              C("occurrence.reparent", occurrence=comp + ":1", parent="U8_PNEU")]
    s.append(C("joint.rigid_group", occurrences=["U8_PNEU:1", "KQ2L06-01AS_M08R_OUT_1:1", "KQ2L06-01AS_M08R_OUT_3:1"]))
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    st = {"1_remove": [C("solid.remove", bodies=OLD_TUBES)],
          "2_tubes_u456": stage_tubes(1), "3_tubes_u7": stage_tubes(2), "4_tubes_cst_reg": stage_tubes(3),
          "5_fittings": stage_fittings(), "6_u5_as": stage_u5_as(), "7_regout_del": stage_reg_out(), "8_regout_ins": stage_reg_out2()}
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, "stage_%s.json" % k), "w", encoding="utf8"), ensure_ascii=False)
        print(k, len(v))
    json.dump({"tubes": TUBELOG, "bends": BENDLOG}, open(os.path.join(OUT, "tubelog.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
    print("tubes", len(TUBELOG), "TU0604 mm", round(sum(v["len"] for v in TUBELOG.values() if v["pn"] == "TU0604"), 1),
          "TU0805 mm", round(sum(v["len"] for v in TUBELOG.values() if v["pn"] == "TU0805"), 1))


if __name__ == "__main__":
    main()


# ------------------------------------------------------------------ 카세트 바깥 관 빗판 CST_O (수정 2 지시)
CSTO_TUBES = ["TU0604_M08P_U7C_CUT_A", "TU0604_M08P_U7C_CUT_B", "TU0604_M08P_U7C_TUCK_A", "TU0604_M08P_U7C_TUCK_B"]


def seg_at_x(name, x=85.0):
    """관 중심선(접선 잘린 직선 구간)이 X=x를 지나는 점·방향."""
    pts, R, r = P(name)
    n = len(pts)
    Rl = R if isinstance(R, list) else [R] * (n - 2)
    u = [norm(sub(pts[i + 1], pts[i])) for i in range(n - 1)]
    t = [0.0] * n
    for i in range(1, n - 1):
        th = math.acos(max(-1, min(1, dot(u[i - 1], u[i]))))
        t[i] = Rl[i - 1] * math.tan(th / 2) if th > 1e-4 else 0.0
    for i in range(n - 1):
        a0 = addv(pts[i], u[i], t[i]); b0 = addv(pts[i + 1], u[i], -t[i + 1])
        if (a0[0] - x) * (b0[0] - x) <= 0 and abs(b0[0] - a0[0]) > 1e-6:
            k = (x - a0[0]) / (b0[0] - a0[0])
            c = addv(a0, sub(b0, a0), k)
            if -300 <= c[1] <= -180 and 60 <= c[2] <= 250:
                return c, u[i]
    raise SystemExit("no straight crossing for " + name)


def stage_csto():
    b = "P_M08_TUBE_BRKT_CST_O"
    s = [box(b, 82, 88, -266, -206, 92, 216), box(b + "_W", 58, 88, -212, -206, 150, 210), box(b + "_F", 58, 64, -206, -185, 150, 210),
         C("solid.combine", target=b, tools=[b + "_W", b + "_F"], operation="join")]
    info = {}
    for nm in CSTO_TUBES:
        c, d = seg_at_x(nm)
        h = 14.0 / abs(d[0])
        base = addv(c, d, -h / 2)
        s.append(cyl(3.25, base, h, d, op="cut", tg=[b]))
        info[nm] = {"center_x85": [r4(v) for v in c], "dir": [r4(v) for v in d]}
    s += [C("material.assign", bodies=[b], material="Steel"),
          C("component.create", name=b, parent="U7_CASSETTE", activate=False),
          C("component.move_bodies", bodies=[b], component=b),
          C("component.metadata.set", component=b, part_number=b, bom_type="normal",
            description="Cassette outer tube comb plate, SPCC t6 sheet (laser + bend, temp; SUS sheet review at detailing), 4 slanted tube holes OD6.5")]
    json.dump(info, open(os.path.join(OUT, "csto_holes.json"), "w"), indent=1)
    return s


if __name__ == "__main__":
    st = stage_csto()
    json.dump(st, open(os.path.join(OUT, "stage_9_csto.json"), "w", encoding="utf8"), ensure_ascii=False)
    print(open(os.path.join(OUT, "csto_holes.json")).read())


# ------------------------------------------------------------------ 고침 1: X 250 빗(COMB_ML_1) 안에서 5·6번 관이 오르기 시작해 구멍 벽과 겹침(8~45 mm³)
# 오름 시작 꼭짓점 (250, lane, z) -> (238, lane, z): 접선점이 빗 -X 면(X 242) 밖으로 나간다.
def stage_fix_comb():
    s = []
    for nm in ("TU0604_M08P_U7_5_A", "TU0604_M08P_U7_5_B", "TU0604_M08P_U7_6_A", "TU0604_M08P_U7_6_B"):
        pts, R, r = P(nm)
        for p in pts:
            if abs(p[0] - 250.0) < 1e-6:
                p[0] = 238.0
        k = len(pts) - 2
        Rl = R if isinstance(R, list) else [R] * (len(pts) - 2)
        top = pts[k - 1]
        zj = round(((top[2] - Rl[k - 2]) + (pts[k][2] + Rl[k - 1])) / 2.0, 1)
        up = pts[:k] + [[top[0], top[1], zj]]
        cmds = tube_cmds(nm, up, Rl[:k - 1], r)
        cmds[0]["params"]["name"] = "SK_" + nm + "_F2"
        cmds[-1]["params"]["path_sketch"] = "SK_" + nm + "_F2"
        s += [C("solid.remove", bodies=[nm])] + cmds + [C("component.move_bodies", bodies=[nm], component=nm)]
        TUBELOG[nm]["pts"] = [[r4(v) for v in p] for p in up]
        TUBELOG[nm]["len"] = round(length(up, Rl[:k - 1]), 1)
    return s


if __name__ == "__main__":
    st = stage_fix_comb()
    json.dump(st, open(os.path.join(OUT, "stage_10_fix_comb.json"), "w", encoding="utf8"), ensure_ascii=False)
    json.dump({"tubes": TUBELOG, "bends": BENDLOG}, open(os.path.join(OUT, "tubelog.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
