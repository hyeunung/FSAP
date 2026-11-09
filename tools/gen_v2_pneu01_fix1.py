# -*- coding: utf-8 -*-
"""PNEU-01 수정 1회차 생성기 — 기준 3D_Modeling/FSAP_v2.8.6.sc -> FSAP_v2.8.7.sc (모델링부 2026-11-10)
고정품 29개(빗·클램프·브래킷) + CB5-16 볼트(기존 볼트 occurrence 복사) + 탭 구멍, U5 체인 23링크 행정 표시 모형 + 체인 안 관,
체인 고정 끝 관 통로, CST_O 재질 SPCC·볼트.
python -X utf8 -B tools/gen_v2_pneu01_fix1.py -> tools/out/mech_PNEU-01/model1/stage_*.json
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_PNEU-01", "model1")
sys.path.insert(0, OUT)
from cross import sample, T  # noqa: E402  (그려진 관 중심선 표본)


def C(cmd, **p):
    return {"command": cmd, "params": p}


def r4(v):
    return round(float(v), 4)


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": r4(x1 - x0), "width": r4(y1 - y0), "height": r4(z1 - z0), "corner": [r4(x0), r4(y0), r4(z0)], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, base, h, axis, op="new", tg=None, name=None):
    p = {"radius": r4(r), "height": r4(h), "base": [r4(v) for v in base], "axis": [r4(v) for v in axis], "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


AX = {0: [1, 0, 0], 1: [0, 1, 0], 2: [0, 0, 1]}
U7 = lambda n: "_U7_" in n
U5 = lambda n: "_U5_" in n
U7C = lambda n: "U7C" in n


def crossings(ax, val, cond):
    hits, seen = [], set()
    for n, t in T.items():
        S = sample(t["pts"], t["R"], 0.5)
        for i in range(len(S) - 1):
            a, b = S[i], S[i + 1]
            if (a[ax] - val) * (b[ax] - val) > 0 or a[ax] == b[ax]:
                continue
            u = (val - a[ax]) / (b[ax] - a[ax])
            p = [a[q] + u * (b[q] - a[q]) for q in range(3)]
            if not cond(p, n):
                continue
            d = [b[q] - a[q] for q in range(3)]
            L = math.sqrt(sum(v * v for v in d)); d = [v / L for v in d]
            key = tuple(round(v, 0) for v in p)
            if key in seen:
                continue
            seen.add(key)
            hits.append((n, p, d, t["r"]))
    return hits


def tube_holes(body, ax, val, thick, cond, log):
    s = []
    for n, p, d, r in crossings(ax, val, cond):
        h = thick / max(abs(d[ax]), 0.2) + 3.0
        base = [p[q] - d[q] * h / 2 for q in range(3)]
        s.append(cyl(r + 0.25, base, h, d, op="cut", tg=[body]))
        log.setdefault(body, []).append({"tube": n, "at": [r4(v) for v in p], "dir": [r4(v) for v in d], "r_hole": r + 0.25})
    return s


# 볼트 원본(기존 CB5-16 occurrence) : (이름, 머리 받침면 중심, 축 방향(나사 쪽))
SRC = {"PY": ("CB5-16_M08_PY:4", [1170.0, 110.0, 350.0], [0, 1, 0]),
       "NZ": ("CB5-16_M08_NZ_COMB:1", [250.0, 166.0, 660.0], [0, 0, -1]),
       "PX": ("CB5-16_M08_PX:1", [-2346.0, 100.0, -300.0], [1, 0, 0]),
       "NX": ("CB5-16_M05_1:1", [58.0, -80.0, 41.5], [-1, 0, 0])}
BOLTS = []
TAPS = {}


def bolt(kind, bp, parent, body, through, mount, cb=0.0, tap=10.0, tag=""):
    """bp = 머리 받침면 중심. body: 볼트가 지나는 고정품(여유 구멍 r2.75, 두께 through), cb: 머리 자리(r4.75) 깊이,
    mount: 탭 구멍(r2.1) 낼 바디(받침면 + through 부터 tap 길이)."""
    src, sbp, d = SRC[kind]
    tr = [r4(bp[q] - sbp[q]) for q in range(3)]
    s = [C("occurrence.copy", occurrence=src, parent=parent, in_place=True, translate=tr)]
    s.append(cyl(2.75, [bp[q] - d[q] * 0.5 for q in range(3)], through + 1.0, d, op="cut", tg=[body]))
    if cb > 0:
        s.append(cyl(4.75, [bp[q] - d[q] * (cb + 0.5) for q in range(3)], cb + 0.5, d, op="cut", tg=[body]))
    if mount:
        TAPS.setdefault(mount, []).append(([bp[q] + d[q] * through for q in range(3)], tap, d))
    BOLTS.append({"src": src.split(":")[0], "kind": kind, "bearing": [r4(v) for v in bp], "parent": parent, "through": body,
                  "mount": mount, "tag": tag})
    return s


def finish(body, parent, desc, mat="A5052", pn=None):
    return [C("material.assign", bodies=[body], material=mat),
            C("component.create", name=body, parent=parent, activate=False),
            C("component.move_bodies", bodies=[body], component=body),
            C("component.metadata.set", component=body, part_number=pn or body, bom_type="normal", description=desc)]


HOLES = {}
FIXLOG = {}
BEAM = "P_M07_BEAM"


def fixtures():
    st = []
    # 1) 보 윗면 빗 (기존 COMB_ML 꼴: X 16, 볼트 1개 위에서, 머리 자리)
    for nm, c, full in (("ML_9", 1000, True), ("ML_5", 950, True), ("ML_6", 450, True), ("ML_7", 50, True),
                        ("ML_8", -650, False), ("U5_1", -100, False), ("U5_2", -1245, False)):
        b = "P_M08_TUBE_COMB_" + nm
        if full:
            cond = lambda p, n: p[2] >= 650 and 120 <= p[1] <= 200 and (U5(n) or U7(n))
        else:
            cond = lambda p, n: p[2] >= 650 and 120 <= p[1] < 200 and U5(n)
        zt = max(697.0, max(p[2] for _, p, _, _ in crossings(0, c, cond)) + 8.0)
        y0 = 124 if full else 158
        s = [box(b, c - 8, c + 8, y0, 197, 650.1, zt)] + tube_holes(b, 0, c, 16, cond, HOLES)
        s += bolt("NZ", [c, 166, 660], "U8_PNEU", b, 9.9, BEAM, cb=zt - 660, tag=b)
        s += finish(b, "U8_PNEU", "Tube comb on beam top, A5052 milled, X16, OD6.5 tube holes, 1x CB5-16 counterbored")
        st += s
        FIXLOG[b] = {"bbox": [c - 8, c + 8, y0, 197, 650.1, zt], "parent": "U8_PNEU"}
    # 2) 보 앞면 클램프 F(U4 2줄 Y110 Z430/440), L(U6 Z262 · MAIN Z280)
    for k, c in enumerate((950, 650, 350, 50, -120)):
        b = "P_M08_TUBE_CLAMP_F_%d" % (k + 1)
        cond = lambda p, n: abs(p[1] - 110) < 3 and "_U4_" in n
        s = [box(b, c - 12, c + 12, 102, 120, 420, 470)] + tube_holes(b, 0, c, 24, cond, HOLES)
        for dx in (-6, 6):
            s += bolt("PY", [c + dx, 112, 462], "U8_PNEU", b, 8, BEAM, cb=10, tag=b)
        s += finish(b, "U8_PNEU", "Tube clamp block on beam front, A5052 milled, 2 tube holes, 2x CB5-16 counterbored")
        st += s
        FIXLOG[b] = {"bbox": [c - 12, c + 12, 102, 120, 420, 470], "parent": "U8_PNEU"}
    for k, (c, who) in enumerate(((1100, "MAIN"), (800, "MAIN U6"), (500, "U6"), (200, "U6"), (-100, "U6"), (-250, "U6"))):
        b = "P_M08_TUBE_CLAMP_L_%d" % (k + 1)
        cond = lambda p, n, w=who: abs(p[1] - 108) < 3 and any(("_" + q) in n for q in w.split())
        if who == "MAIN":
            z0, z1, zb = 268, 304, 296
        elif "MAIN" in who:
            z0, z1, zb = 252, 304, 296
        else:
            z0, z1, zb = 252, 284, 276
        s = [box(b, c - 12, c + 12, 102, 120, z0, z1)] + tube_holes(b, 0, c, 24, cond, HOLES)
        for dx in (-6, 6):
            s += bolt("PY", [c + dx, 112, zb], "U8_PNEU", b, 8, BEAM, cb=10, tag=b)
        s += finish(b, "U8_PNEU", "Tube clamp block on beam front, A5052 milled, 2x CB5-16 counterbored")
        st += s
        FIXLOG[b] = {"bbox": [c - 12, c + 12, 102, 120, z0, z1], "parent": "U8_PNEU"}
    # 3) 밸브 위 세움 빗 Z400 / Z620 (판 + 보 앞면 귀)
    for k, z in enumerate((400, 620)):
        b = "P_M08_RISER_COMB_%d" % (k + 1)
        cond = lambda p, n: 1035 <= p[0] <= 1115
        ze = z + 32 if z == 400 else 648
        s = [box(b, 1040, 1112, -15, 112, z - 4, z + 4), box(b + "_E", 1040, 1112, 112, 120, z - 4, ze),
             C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 2, z, 8, cond, HOLES)
        zb = z + 22 if z == 400 else 638
        for x in (1046, 1106):
            s += bolt("PY", [x, 112, zb], "U8_PNEU", b, 8, BEAM, tag=b)
        s += finish(b, "U8_PNEU", "Riser tube comb over valve manifold, A5052 milled L (plate t8 + ear to beam front), 2x CB5-16")
        st += s
        FIXLOG[b] = {"bbox": [1040, 1112, -15, 120, z - 4, ze], "parent": "U8_PNEU"}
    # 4) 띄움 클램프 SO_1(X960), SO_2·3(Z300)
    b = "P_M08_TUBE_CLAMP_SO_1"
    cond = lambda p, n: (n.endswith("_U6") or "REG1_OUT" in n) and p[1] < 100
    s = [box(b, 952, 968, 45, 112, 232, 270), box(b + "_E", 938, 982, 112, 120, 252, 272),
         C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 0, 960, 16, cond, HOLES)
    for x in (944, 976):
        s += bolt("PY", [x, 112, 262], "U8_PNEU", b, 8, BEAM, tag=b)
    s += finish(b, "U8_PNEU", "Stand-off tube clamp from beam front, A5052 milled, 2 tube holes, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [938, 982, 45, 120, 232, 272], "parent": "U8_PNEU"}
    for k, (nmr, xc, yc) in enumerate((("REG1_OUT", 729.1, 82.0), ("REG3_OUT", 927.94, 95.0))):
        b = "P_M08_TUBE_CLAMP_SO_%d" % (k + 2)
        cond = lambda p, n, w=nmr: w in n
        s = [box(b, xc - 10, xc + 10, yc - 8, 112, 296, 304), box(b + "_E", xc - 20, xc + 20, 112, 120, 296, 322),
             C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 2, 300, 8, cond, HOLES)
        for dx in (-14, 14):
            s += bolt("PY", [xc + dx, 112, 314], "U8_PNEU", b, 8, BEAM, tag=b)
        s += finish(b, "U8_PNEU", "Stand-off tube clamp (horizontal plate + ear to beam front), A5052 milled, 2x CB5-16")
        st += s
        FIXLOG[b] = {"bbox": [xc - 20, xc + 20, yc - 8, 120, 296, 322], "parent": "U8_PNEU"}
    # 5) U6 받침 (P_M02_BASE -X 면)
    b = "P_M08_TUBE_BRKT_U6"
    cond = lambda p, n: n.endswith("_U6") and abs(p[0] + 347) < 3
    s = [box(b, -356, -338, -10, 10, 252, 272), box(b + "_E", -338, -330, -16, 16, 222, 272),
         C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 1, 0, 20, cond, HOLES)
    for y in (-8, 8):
        s += bolt("PX", [-338, y, 236], "U4_WHEEL_N", b, 8, "P_M02_BASE", tag=b)
    s += finish(b, "U4_WHEEL_N", "U6 tube support on wheel base -X face, A5052 milled L, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-356, -330, -16, 16, 222, 272], "parent": "U4_WHEEL_N"}
    # 6) KDM 빗(보 앞면 판 Y112~120) + Y40 팔(웹 X -88~-80)
    b = "P_M08_TUBE_COMB_KDM"
    c1 = lambda p, n: U7(n) and -90 <= p[0] <= -5 and p[2] > 650
    s = [box(b, -88, -8, 112, 120, 620, 722), box(b + "_W", -88, -80, 44, 112, 665, 722), box(b + "_A", -88, -20, 36, 44, 665, 745),
         C("solid.combine", target=b, tools=[b + "_W", b + "_A"], operation="join")]
    s += tube_holes(b, 1, 116, 8, c1, HOLES) + tube_holes(b, 1, 40, 8, c1, HOLES)
    for x in (-80, -16):
        s += bolt("PY", [x, 112, 632], "U8_PNEU", b, 8, BEAM, tag=b)
    s += finish(b, "U8_PNEU", "KDM tube comb on beam front with Y40 arm for slanted U7 run, A5052 milled, 12 holes, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-88, -8, 36, 120, 620, 745], "parent": "U8_PNEU"}
    # 7) KDM 받침 위 판 Z742~750 (U7_FIXED, 세로 다리 9)
    b = "P_M08_TUBE_BRKT_KDM"
    cond = lambda p, n: U7(n) and p[1] < -120 and p[0] < 0
    s = [box(b, -76, 46, -196, -116, 742, 750)] + tube_holes(b, 2, 746, 8, cond, HOLES)
    for y in (-190, -122):
        s += bolt("NZ", [30, y, 750], "U7_FIXED", b, 8, "P_M08_KDM_BRKT", tag=b)
    s += finish(b, "U7_FIXED", "U7 vertical tube comb plate on KDM bracket top, A5052 t8 milled, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-76, 46, -196, -116, 742, 750], "parent": "U7_FIXED"}
    # 8) 대차 판 클램프 Z400, 체인 팔 받침 Z620, 팔 밑 Y160 (U5_CAR)
    b = "P_M08_TUBE_CLAMP_CAR"
    cond = lambda p, n: "U5C" in n
    s = [box(b, -1990, -1955, 48, 72, 396, 404), box(b + "_E", -1995, -1950, 72, 80, 396, 416),
         C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 2, 400, 8, cond, HOLES)
    for x in (-1990, -1955):
        s += bolt("PY", [x, 72, 410], "U5_CAR", b, 8, "P_M03_CAR_PLATE", tag=b)
    s += finish(b, "U5_CAR", "U5C tube clamp on carriage plate front, A5052 milled L, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-1995, -1950, 48, 80, 396, 416], "parent": "U5_CAR"}
    b = "P_M08_TUBE_BRKT_ARM_1"
    s = [box(b, -1990, -1956, 46, 78, 616, 624), box(b + "_E", -1956, -1950, 46, 100, 604, 644),
         C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 2, 620, 8, cond, HOLES)
    for z in (612, 636):
        s += bolt("PX", [-1956, 92, z], "U5_CAR", b, 6, "P_M03_CHAIN_ARM", tag=b)
    s += finish(b, "U5_CAR", "U5C tube support on chain arm -X face, A5052 milled L, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-1990, -1950, 46, 100, 604, 644], "parent": "U5_CAR"}
    b = "P_M08_TUBE_BRKT_ARM_2"
    cond2 = lambda p, n: "U5C" in n and p[2] > 800
    s = [box(b, -1990, -1956, 156, 164, 800, 836), box(b + "_E", -1956, -1950, 140, 180, 800, 836),
         C("solid.combine", target=b, tools=[b + "_E"], operation="join")] + tube_holes(b, 1, 160, 8, cond2, HOLES)
    for y in (146, 174):
        s += bolt("PX", [-1956, y, 818], "U5_CAR", b, 6, "P_M03_CHAIN_ARM", tag=b)
    s += finish(b, "U5_CAR", "U5C tube support under chain arm (Y160), A5052 milled L, 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [-1990, -1950, 140, 180, 800, 836], "parent": "U5_CAR"}
    # 9) 카세트 세로 다리 빗 CST_V (U7_CASSETTE, 판 +X 면)
    b = "P_M08_TUBE_BRKT_CST_V"
    cond = lambda p, n: U7C(n) and p[0] >= 95
    s = [box(b, 58, 62, -159, -146, 296, 530), box(b + "_L", 62, 146, -160, -127, 338, 342), box(b + "_U", 62, 146, -160, -127, 518, 522),
         C("solid.combine", target=b, tools=[b + "_L", b + "_U"], operation="join")]
    s += tube_holes(b, 2, 340, 4, cond, HOLES) + tube_holes(b, 2, 520, 4, cond, HOLES)
    for z in (304, 320):
        s += bolt("NX", [62, -152.5, z], "U7_CASSETTE", b, 4, "P_M05_CST_PLATE", tap=8, tag=b)
    s += finish(b, "U7_CASSETTE", "Cassette vertical-leg tube comb, A5052 t4 sheet (laser + 2 bends, same side), 2x CB5-16")
    st += s
    FIXLOG[b] = {"bbox": [58, 146, -160, -127, 296, 530], "parent": "U7_CASSETTE"}
    return st


def extras():
    """CST_O 재질·볼트, AIR_IN_BRKT 볼트, 체인 고정 끝 관 통로."""
    s = [C("material.create", name="SPCC", density_g_cm3=7.85, color="#8a8d91"),
         C("material.assign", bodies=["P_M08_TUBE_BRKT_CST_O"], material="SPCC")]
    for z in (162, 198):
        s += bolt("NX", [64, -191.5, z], "U7_CASSETTE", "P_M08_TUBE_BRKT_CST_O", 6, "P_M05_CST_PLATE", tap=8, tag="P_M08_TUBE_BRKT_CST_O")
    for z in (273, 287):
        BOLTS.append({"src": "CB5-16_M08_PY", "kind": "PY", "bearing": [1159, 116, z], "parent": "U8_PNEU",
                      "through": "P_M08_AIR_IN_BRKT", "mount": BEAM, "tag": "P_M08_AIR_IN_BRKT"})
        s += [C("occurrence.copy", occurrence=SRC["PY"][0], parent="U8_PNEU", in_place=True, translate=[1159 - 1170, 116 - 110, z - 350]),
              ]
        TAPS.setdefault(BEAM, []).append(([1159, 120, z], 12, [0, 1, 0]))
    for z in (661, 673):
        s.append(cyl(3.25, [-1264, 250, z], 44, [1, 0, 0], op="cut", tg=["STEP대기_2400.05.12PZ_F"]))
    return s


# ------------------------------------------------------------------ U5 체인 행정 표시 모형 (설계안 4절)
XF, XM0, XC0, ZC, RP = -1222.5, -1930.0, -1165.05, 742.5, 75.0
OLD_CHAIN = ["2400.05.075.0_UPPER"] + ["2400.05.075.0_L%02d_%s" % (i, s) for i in range(1, 8) for s in ("BAR", "SIDE1", "SIDE2")]
CHAINLOG = {}


def link_body(name, xc, zp):
    """바깥 73 x 35 / 안 50 x 25 사각 링크, X 길이 46(피치), 피치선 zp."""
    return [box(name, xc - 23, xc + 23, 200, 273, zp - 17.5, zp + 17.5),
            box(None, xc - 24, xc + 24, 211.5, 261.5, zp - 12.5, zp + 12.5, op="cut", tg=[name])]


def chain():
    s = [C("solid.remove", bodies=OLD_CHAIN)]
    # 아래 가닥 링크 컴포넌트 (첫 링크 g=0, 고정 끝에 붙음)
    g = [(j - 1) / 16.0 for j in range(1, 18)]
    L = "2400.05.075.0_U5_LINK_L"
    x1 = XF + 23
    s += link_body(L, x1, 667.5)
    s += [cyl(3.0, [x1 - 23, 250, 661], 46, [1, 0, 0], name=L + "_TA"), cyl(3.0, [x1 - 23, 250, 673], 46, [1, 0, 0], name=L + "_TB"),
          C("material.assign", bodies=[L], material="ABS Plastic"),
          C("component.create", name=L, parent="U5_WHEEL_F", activate=False),
          C("component.move_bodies", bodies=[L, L + "_TA", L + "_TB"], component=L),
          C("component.metadata.set", component=L, part_number="2400.05.075.0", bom_type="reference",
            description="igus E4.1 2400.05.075.0 link (stroke display model, lower run) with 2x TU0604 in chain; real chain 23 links x 46 = 1058 mm")]
    U = "2400.05.075.0_U5_LINK_U"
    xu = XM0 + 23
    s += link_body(U, xu, 817.5)
    s += [cyl(3.0, [xu - 23, 250, 824], 46, [1, 0, 0], name=U + "_TA"), cyl(3.0, [xu - 23, 250, 812], 46, [1, 0, 0], name=U + "_TB"),
          C("material.assign", bodies=[U], material="ABS Plastic"),
          C("component.create", name=U, parent="U5_WHEEL_F", activate=False),
          C("component.move_bodies", bodies=[U, U + "_TA", U + "_TB"], component=U),
          C("component.metadata.set", component=U, part_number="2400.05.075.0", bom_type="reference",
            description="igus E4.1 2400.05.075.0 link (stroke display model, upper run) with 2x TU0604 in chain")]
    # 굽힘 묶음: 5링크 + 반원 관 2
    B = "2400.05.075.0_U5_BEND"
    names = []
    for k in range(5):
        nm = "%s_K%d" % (B, k + 1)
        th = 18 + 36 * k
        s += link_body(nm, 0, -RP)
        s += [C("solid.move", bodies=[nm], axis=[0, -1, 0], angle="%g deg" % th),
              C("solid.move", bodies=[nm], translate=[XC0, 0, ZC])]
        names.append(nm)
    for nm, R in ((B + "_TA", 81.5), (B + "_TB", 69.5)):
        sk = "SK_" + nm
        s += [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True),
              C("sketch.arc3d", start=[XC0, 250, ZC - R], through=[XC0 + R, 250, ZC], end=[XC0, 250, ZC + R]),
              C("sketch.finish"),
              C("solid.pipe", path_sketch=sk, path=["w1"], diameter=6.0, operation="new", body_name=nm)]
        names.append(nm)
    s += [C("material.assign", bodies=names[:5], material="ABS Plastic"),
          C("component.create", name=B, parent="U5_WHEEL_F", activate=False),
          C("component.move_bodies", bodies=names, component=B),
          C("component.metadata.set", component=B, part_number="2400.05.075.0", bom_type="reference",
            description="igus 2400.05.075.0 bend R75 (5 links, 178.6 deg) with TU0604 R81.5/R69.5, moves at 0.5 x J_U5_X")]
    CHAINLOG.update({"lower": [{"g": gg, "center_x_s0": r4(XF + 23 + 11.45 * gg), "ratio": r4(0.5 * gg)} for gg in g],
                     "upper": [{"g": gg, "center_x_s0": r4(XM0 + 23 + 718.95 * gg), "ratio": r4(1 - 0.5 * gg)} for gg in g],
                     "bend": {"center_x_s0": XC0, "z": ZC, "ratio": 0.5}})
    return s


def chain_copies():
    s = []
    for j, e in enumerate(CHAINLOG["lower"][1:], start=2):
        s.append(C("occurrence.copy", occurrence="2400.05.075.0_U5_LINK_L:1", in_place=True, translate=[r4(e["center_x_s0"] - (XF + 23)), 0, 0]))
    for j, e in enumerate(CHAINLOG["upper"][1:], start=2):
        s.append(C("occurrence.copy", occurrence="2400.05.075.0_U5_LINK_U:1", in_place=True, translate=[r4(e["center_x_s0"] - (XM0 + 23)), 0, 0]))
    return s


def taps():
    """M5 탭 구멍(r2.1): 받침 바디마다 원기둥을 모아 한 번에 cut(큰 보에 하나씩 cut하면 24 s)."""
    s = []
    for m, lst in TAPS.items():
        tools = []
        for k, (b, h, d) in enumerate(lst):
            if m == BEAM and abs(b[0] - 1000) < 1e-6 and abs(b[1] - 166) < 1e-6:
                continue  # ML_9 탭은 첫 시험 묶음에서 이미 냈다
            nm = "TAP_%s_%d" % (m, k + 1)
            s.append(cyl(2.1, b, h, d, name=nm)); tools.append(nm)
        if tools:
            s.append(C("solid.combine", target=m, tools=tools, operation="cut"))
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    st = {"A_fixtures": fixtures(), "B_extras": extras(), "C_chain": chain(), "D_chain_copies": chain_copies()}
    st["E_taps"] = taps()
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, "stage_%s.json" % k), "w", encoding="utf8"), ensure_ascii=False)
        print(k, len(v))
    json.dump({"holes": HOLES, "fixtures": FIXLOG, "bolts": BOLTS, "chain": CHAINLOG},
              open(os.path.join(OUT, "fixlog.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("bolts", len(BOLTS), "holes", sum(len(v) for v in HOLES.values()), "fixtures", len(FIXLOG))
    for b, v in HOLES.items():
        print(b, len(v))


def chain_joints():
    """링크마다 U5_WHEEL_F에 X 미끄럼 + J_U5_X motion link(비율 = 설계안 4절 식)."""
    s = []
    J = []
    for j, e in enumerate(CHAINLOG["lower"], start=1):
        if e["ratio"] == 0:
            continue
        J.append(("2400.05.075.0_U5_LINK_L:%d" % j, "J_U5_CHN_L%02d" % j, [e["center_x_s0"], 236.5, 667.5], e["ratio"]))
    for j, e in enumerate(CHAINLOG["upper"], start=1):
        J.append(("2400.05.075.0_U5_LINK_U:%d" % j, "J_U5_CHN_U%02d" % j, [e["center_x_s0"], 236.5, 817.5], e["ratio"]))
    J.append(("2400.05.075.0_U5_BEND:1", "J_U5_CHN_B", [XC0, 236.5, ZC], 0.5))
    for occ, nm, pt, ratio in J:
        s.append(C("joint.as_built", type="slider", a="U5_WHEEL_F:1", b=occ,
                   at={"occurrence": occ, "point": pt, "z": [1, 0, 0]}, name=nm, quiet=True))
        s.append(C("joint.motion_link", a="J_U5_X", b=nm, ratio=ratio))
    return s


if __name__ == "__main__":
    st = chain_joints()
    json.dump(st, open(os.path.join(OUT, "stage_F_chain_joints.json"), "w", encoding="utf8"), ensure_ascii=False)
    print("F", len(st))
