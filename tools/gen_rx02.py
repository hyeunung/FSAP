# RX-02 바늘 냉각 공기 노즐 명령 생성기 (v2.23.0 -> v2.24.0).
# 실행: python -B tools/gen_rx02.py  -> tools/out/mech_RX-02/model/stage_*.json (MCP batch path 로 순서대로 보냄)
# 좌표: 월드 mm(바늘점 원점, 테이블 면 Z 0), REST. 근거: docs/reports/mechanism/mech_RX-02_design.md 3절 · 지시서 0~10.
# 지시와 다른 것(보고서 2절):
#  - 노즐 관 위 끝 Z 113 -> 109, 블록 Ø4.05 구멍 깊이 8 -> 4, Ø2.5 이음 Z 109~110:
#    지시대로면 M5 포트 안쪽 Ø2.5(Z 108.75~111.25, X 30~38)가 끼운 관 벽(Z 105~113)에 막혀 공기가 안 나감.
#  - 9번 B 막음은 같은 자리 관계인 STEP대기_M-5P_4(5번 B, X 1091.75)의 형상을 X +42로 그림(_1은 다른 자리).
#  - AS1211F 임시 형상에 나사 M5 L4(X 40~44)를 넣음(설계안 3-1 표).
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-02', 'model')
STEP = os.path.join(os.path.dirname(ROOT), 'purchased-step').replace('\\', '/')
os.makedirs(OUT, exist_ok=True)

def C(cmd, **p): return {"command": cmd, "params": p}
def r4(v): return [round(float(x), 4) for x in v]
def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None, fname=None):
    p = dict(corner=r4([x0, y0, z0]), length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation=op)
    if op == "new": p["body_name"] = name
    if tg: p["targets"] = tg
    if fname: p["name"] = fname
    return C("solid.box", **p)
def cyl(r, base, h, axis, op="new", tg=None, name=None, fname=None):
    p = dict(radius=r, height=h, base=r4(base), axis=axis, operation=op)
    if tg: p["targets"] = tg
    if name: p["body_name"] = name
    if fname: p["name"] = fname
    return C("solid.cylinder", **p)
def comp(name, body, pn, bom, desc, mat, parent="U8_PNEU", create=True):
    c = [C("material.assign", bodies=[body], material=mat)]
    if create: c.append(C("component.create", name=name, parent=parent, activate=False))
    c += [C("component.move_bodies", bodies=[body], component=name),
          C("component.metadata.set", component=name, part_number=pn, bom_type=bom, description=desc)]
    return c
X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]
NX, NY, NZ = [-1, 0, 0], [0, -1, 0], [0, 0, -1]
W = "STEP대기_"
stages = {}

# ---- 1. 옮길 5개: 압력 스위치 엘보의 리지드 조인트만 지움(나머지 4개는 U8_PNEU 안 사본이라 조인트 없음) 후 +10.5
MOV = [W + "TPH-01_1:1", W + "TPH-01_3:1", "CB4-25_M08:3", "CB4-25_M08:4", "KQ2L06-01AS_M08V_PSW:1"]
stages['1_move'] = ([C("component.activate", component="root"),
                     C("joint.delete", joint="Rigid Group 18:99534")] +
                    [C("occurrence.move", occurrence=o, space="world", translate=[10.5, 0, 0]) for o in MOV])

# ---- 2. 매니폴드 08 -> 09 (gen_v2_rx08.py s5 와 같은 방법)
MF8 = W + "SS5Y3-20-08_M08"
MF9 = W + "SS5Y3-20-09_M08"
s2 = [C("solid.remove", bodies=[MF8], name="RM_SS5Y3_08_RX02"),
      box(MF9, 1035, 1148.5, 100, 120, 325.5, 374.5, fname="RX02_MF9")]
for x in (1039.8, 1143.7):
    for z in (343, 359):
        s2.append(cyl(2.25, [x, 120.1, z], 20.2, NY, "cut", tg=[MF9], fname="RX02_MF9_H_%d_%d" % (round(x), z)))
s2 += [C("material.assign", bodies=[MF9], material="Aluminum"),
       C("component.move_bodies", bodies=[MF9], component=MF8),
       C("component.rename", component=MF8, name=MF9),
       C("component.metadata.set", component=MF9, part_number="SS5Y3-20-09", bom_type="purchased",
         description="STEP wait (E-10): SY3000 bar manifold 9 stations, temp box L 113.5 = 08 box 103 + pitch 10.5 (RX-02)")]
stages['2_manifold'] = s2

# ---- 3. 9번 스테이션: 밸브·A 엘보 사본, B 막음(STEP대기_M-5P_4 와 같은 형상 X +42)
P9 = W + "M-5P_9"
s3 = [C("occurrence.copy", occurrence="SY3120-5LZD-M5_M08:8", parent="U8_PNEU", in_place=True, translate=[10.5, 0, 0]),
      C("occurrence.copy", occurrence="KQ2L06-M5A_M08S_NZ:8", parent="U8_PNEU", in_place=True, translate=[10.5, 0, 0]),
      cyl(4, [1133.75, 67.5, 356.1], 4, Y, "new", name=P9, fname="RX02_M5P_9_HEAD"),
      cyl(2.5, [1133.75, 71.5, 356.1], 4, Y, "join", tg=[P9], fname="RX02_M5P_9_THREAD")]
s3 += comp(P9, P9, "M-5P", "purchased", "placeholder (STEP pending): SMC M-5P plug for valve 9 B port (nozzle valve single acting, RX-02)", "Default")
stages['3_station9'] = s3

# ---- 4. 관
def unit(v):
    n = math.sqrt(sum(x * x for x in v)); return [x / n for x in v]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, s): return [x * s for x in a]
def arcmid(st, ce, en):
    R = math.dist(st, ce)
    m = unit([(st[i] - ce[i]) + (en[i] - ce[i]) for i in range(3)])
    return [ce[i] + m[i] * R for i in range(3)]
def poly_segs(pts, radii):
    """꺾은선 + 꼭짓점 R -> [("l",a,b) | ("a",st,ce,en)]"""
    segs = []; cur = pts[0]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d1 = unit(sub(p1, p0)); d2 = unit(sub(p2, p1))
        th = math.acos(max(-1, min(1, sum(d1[k] * d2[k] for k in range(3)))))
        R = radii[i - 1]; tl = R * math.tan(th / 2)
        a = sub(p1, mul(d1, tl)); b = add(p1, mul(d2, tl))
        cen = add(p1, mul(unit(sub(d2, d1)), R / math.cos(th / 2)))
        assert math.dist(cur, a) >= -1e-6 and math.dist(p1, p2) + 1e-6 >= tl
        if math.dist(cur, a) > 0.01: segs.append(("l", cur, a))
        segs.append(("a", a, cen, b)); cur = b
    if math.dist(cur, pts[-1]) > 0.05: segs.append(("l", cur, pts[-1]))
    # 곧은 구간이 양 끝 접선 길이를 담는지
    def tlen(i):
        d1 = unit(sub(pts[i], pts[i - 1])); d2 = unit(sub(pts[i + 1], pts[i]))
        th = math.acos(max(-1, min(1, sum(d1[k] * d2[k] for k in range(3))))); return radii[i - 1] * math.tan(th / 2)
    for i in range(1, len(pts) - 2):
        assert math.dist(pts[i], pts[i + 1]) + 1e-6 >= tlen(i) + tlen(i + 1), ('seg', i)
    return segs
def tube(name, segs, dia, sk, wall=None, fname=None):
    c = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    L = 0.0
    for s in segs:
        if s[0] == "l":
            c.append(C("sketch.line3d", points=[r4(s[1]), r4(s[2])])); L += math.dist(s[1], s[2])
        else:
            st, ce, en = s[1], s[2], s[3]
            R = math.dist(st, ce)
            ang = math.acos(max(-1, min(1, sum((st[i] - ce[i]) * (en[i] - ce[i]) for i in range(3)) / R / R)))
            c.append(C("sketch.arc3d", start=r4(st), through=r4(arcmid(st, ce, en)), end=r4(en))); L += R * ang
    p = dict(path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(segs))], diameter=dia, operation="new", body_name=name,
             name=fname or ("PIPE_%s_RX02" % name))
    if wall: p["wall"] = wall
    c += [C("sketch.finish"), C("solid.pipe", **p)]
    return c, L

# PSW: RX-01 S_segs 와 같은 모양, X 1145.4 -> 1155.9 (S 굽힘 어긋남 4.4 -> 14.9)
s50, c50 = math.sin(math.radians(50)), math.cos(math.radians(50))
XP = 1155.9
m50 = [0, -s50, c50]
p0 = [XP, 107.5 + 15.5 * m50[1], 351 + 15.5 * m50[2]]
L1 = (p0[1] - (99.30 - 20 * c50)) / s50
p1 = [p0[i] + L1 * m50[i] for i in range(3)]
c1 = [XP, 99.30, p1[2] + 20 * s50]
e1 = [XP, 79.30, c1[2]]
off = XP - 1141.0
th = math.acos(1 - off / 60.0)
a2s = [XP, 79.30, 420.0]; c2 = [XP - 30, 79.30, 420.0]
a2e = [c2[0] + 30 * math.cos(th), 79.30, 420.0 + 30 * math.sin(th)]
c3 = [a2e[0] + 30 * math.cos(th), 79.30, a2e[2] + 30 * math.sin(th)]
a3e = [c3[0] - 30, 79.30, c3[2]]
endS = [1141.0, 79.30, 470.5]
S_segs = [("l", p0, p1), ("a", p1, c1, e1), ("l", e1, a2s), ("a", a2s, c2, a2e), ("a", a2e, c3, a3e), ("l", a3e, endS)]
tS, LS = tube("TU0604_M08P_PSW", S_segs, 6.0, "SK_TU0604_M08P_PSW_RX02")
# RX08_B: (-95,110,381)까지는 옛 길 그대로, 끝 고리만 바꿈. 꼭짓점 R15
B_pts = [[-169, 61, 340], [-169, 61, 381], [-95, 61, 381], [-95, 110, 381],
         [1100, 110, 381], [1120, 104, 381], [1164.5, 104, 381], [1164.5, 32, 381], [1164.5, 32, 300],
         [1123.25, 32, 300], [1123.25, 63, 300], [1123.25, 63, 331.4]]
B_segs = poly_segs(B_pts, [15] * (len(B_pts) - 2))
tB, LB = tube("TU0604_M08P_RX08_B", B_segs, 6.0, "SK_TU0604_M08P_RX08_B_RX02")
# NOZ: 9번 A -> 헤드 블록 속도 조절 이음 입
N_pts = [[1133.75, 63, 331.4], [1133.75, 63, 268], [1133.75, 48, 245], [1133.75, 48, 200], [880, 48, 200],
         [880, 98, 200], [57.5, 98, 200], [57.5, 98, 110], [57.5, 44.5, 110]]
N_segs = poly_segs(N_pts, [15] * (len(N_pts) - 2))
tN, LN = tube("TU0604_RX02_NOZ", N_segs, 6.0, "SK_TU0604_RX02_NOZ")
NOZ_POLY = sum(math.dist(N_pts[i], N_pts[i + 1]) for i in range(len(N_pts) - 1))
s4 = [C("component.activate", component="root"),
      C("solid.remove", bodies=["TU0604_M08P_PSW"], name="RM_TU0604_M08P_PSW_RX02")] + tS + comp(
      "TU0604_M08P_PSW", "TU0604_M08P_PSW", "TU0604", "purchased",
      "SMC TU0604 polyurethane tube OD6, manifold +X end plate P -> pressure switch, cut length %.1f, bends R 20/30/30 (RX-01, RX-02 end plate +10.5)" % LS,
      "Default", create=False)
s4 += [C("solid.remove", bodies=["TU0604_M08P_RX08_B"], name="RM_TU0604_M08P_RX08_B_RX02")] + tB + comp(
      "TU0604_M08P_RX08_B", "TU0604_M08P_RX08_B", "TU0604", "purchased",
      "SMC TU0604 OD6, RX-08 stopper cylinder rod port (pull = ON) <-> valve 8 A (NZ), U8 segment from Z 340; RX-02 end loop X 1164.5 / Y 32 (clear of moved PSW tube)",
      "Default", create=False)
s4 += tN + comp("TU0604_RX02_NOZ", "TU0604_RX02_NOZ", "TU0604", "purchased",
                "SMC TU0604 polyurethane tube OD6, valve 9 A (NZ elbow) -> along beam front Z 200 -> behind head arm Y 98 -> speed controller AS1211F on nozzle block, cut length %.0f, bends R15 (RX-02)" % LN,
                "Default")
stages['4_tubes'] = s4

# ---- 5. 노즐 묶음 U3_NOZZLE (U3_HEAD 아래)
NC = "U3_NOZZLE"
BLK = "P_RX02_NOZ_BLK_MILL"
PIP = "P_RX02_NOZ_PIPE"
SPD = W + "AS1211F-M5-06"
UP = W + "867-392342_UPPER"
ZT = 109.0      # 노즐 관 위 끝(지시 113 -> 109, 보고서)
s5 = [C("component.activate", component="root"),
      C("component.create", name=NC, parent="U3_HEAD", activate=False),
      C("component.metadata.set", component=NC, bom_type="phantom",
        description="RX-02 needle cooling air nozzle group (block + bent nozzle tube + speed controller + 2x CB5-20) under head arm"),
      box(BLK, 16, 44, 16, 44, 105, 125, fname="RX02_NOZ_BLK"),
      cyl(2.1, [44.1, 30, 110], 6.1, NX, "cut", tg=[BLK], fname="RX02_NOZ_BLK_M5_PORT"),          # M5 탭 깊이 6 (X 38~44)
      cyl(1.25, [38.05, 30, 110], 8.05, NX, "cut", tg=[BLK], fname="RX02_NOZ_BLK_D25_X"),         # Ø2.5 X 30~38
      cyl(2.025, [30, 30, 104.9], ZT - 104.9, Z, "cut", tg=[BLK], fname="RX02_NOZ_BLK_D405"),     # 관 구멍 Ø4.05 Z 105~109
      cyl(1.25, [30, 30, ZT - 0.05], 110.0 - ZT + 0.05, Z, "cut", tg=[BLK], fname="RX02_NOZ_BLK_D25_Z")]  # Ø2.5 Z 109~110
for (x, y) in ((23, 23), (23, 37)):
    s5 += [cyl(2.75, [x, y, 104.9], 20.2, Z, "cut", tg=[BLK], fname="RX02_NOZ_BLK_D55_%d" % y),
           cyl(4.75, [x, y, 104.9], 10.1, Z, "cut", tg=[BLK], fname="RX02_NOZ_BLK_CB95_%d" % y)]
s5 += [C("solid.thread", face=[44.0 - 3.0, 30 + 2.1, 110], designation="M5", modeled=False)]
s5 += comp(BLK, BLK, BLK, "normal",
           "Nozzle block, A5052 milling 28x28x20 (provisional): +X face M5 port (tap 6) -> D2.5 -> D4.05 socket for nozzle tube from below; "
           "2x D5.5 + counterbore D9.5 depth 10 from below for CB5-20 into head arm M5 taps (RX-02)", "A5052", parent=NC)
# 노즐 관 SUS304 Ø4 x 0.5, 꺾임 R10
B0, BEND, TIP = [30, 30, ZT], [30, 30, 62.5], [11, 11, 35.6]
P_segs = poly_segs([B0, BEND, TIP], [10])
tP, LP = tube(PIP, P_segs, 4.0, "SK_RX02_NOZ_PIPE", wall=0.5, fname="RX02_NOZ_PIPE")
s5 += tP + comp(PIP, PIP, PIP, "normal",
                "Bent nozzle tube, SUS304 tube OD4 x t0.5, bend R10 45 deg, tip (11,11,35.6) aims at needle axis Z 20 (22.0 mm, 45 deg), "
                "inserted 4 into block and brazed/bonded (detail); length %.1f (RX-02)" % LP, "SUS304", parent=NC)
# 속도 조절 이음 임시 형상(E-12)
s5 += [box(SPD, 44, 62, 24.5, 35.5, 104.5, 115.5, fname="RX02_AS1211F_BODY"),
       cyl(2.5, [40, 30, 110], 4.0, X, "join", tg=[SPD], fname="RX02_AS1211F_THREAD"),
       cyl(4.0, [62, 30, 110], 10.0, X, "join", tg=[SPD], fname="RX02_AS1211F_KNOB"),
       cyl(5.0, [57.5, 30, 110], 14.5, Y, "join", tg=[SPD], fname="RX02_AS1211F_MOUTH")]
s5 += comp(SPD, SPD, "AS1211F-M5-06", "purchased",
           "STEP wait (E-10/E-12), dimensions temporary: SMC AS1211F-M5-06 meter-in elbow speed controller M5 - OD6; "
           "body 18x11x11, needle knob D8 to +X, tube mouth D10 to +Y (end Y 44.5), thread M5 L4 (RX-02)", "Default", parent=NC)
# 헤드 임시 형상 밑면 M5 탭 깊이 13 x2 (이력 끝)
s5 += [C("component.activate", component="U3_HEAD")]
for (x, y) in ((23, 23), (23, 37)):
    s5.append(cyl(2.1, [x, y, 124.9], 13.1, Z, "cut", tg=[UP], fname="RX02_ARM_TAP_%d" % y))
s5 += [C("component.activate", component="root")]
stages['5_nozzle'] = s5

# ---- 6. 볼트 CB5-20 x2 (실물 STEP). 로컬 +X = 축(머리 -> 끝) -> 월드 +Z, 원점 = 머리 밑면(좌면) Z 115
s6 = []
for i, (x, y) in enumerate(((23, 23), (23, 37))):
    nm = "CB5-20_RX02_%d" % (i + 1)
    s6 += [C("file.insert_step", path=STEP + "/CB5-20/CB5-20.stp", name=nm, matrix=[0, 0, -1, x, 0, 1, 0, y, 1, 0, 0, 115]),
           C("body.rename", body="Cut-Extrude1", name=nm),
           C("component.metadata.set", component=nm, part_number="CB5-20", bom_type="purchased",
             description="Misumi CB5-20 STEP, RX-02 nozzle block to head arm M5 tap (from below, head in counterbore)"),
           C("material.assign", bodies=[nm], material="SCM435"),
           C("occurrence.reparent", occurrence=nm + ":1", parent=NC)]
stages['6_bolts'] = s6

# ---- 7. 리지드 묶음
stages['7_rigid'] = [C("joint.rigid_group", occurrences=["U3_HEAD:1", NC + ":1", "CB5-20_RX02_1:1", "CB5-20_RX02_2:1"]),
                     C("joint.rigid_group", occurrences=["U8_PNEU:1", "KQ2L06-01AS_M08V_PSW:1"])]

# ---- 8. 옮긴 CB4-25 :3 · :4 의 보 앞벽 M4 탭(옛 자리 X 1133.2에도 탭이 없었음 — 나사 짝 없는 볼트를 옮긴 자리에서 바로잡음)
stages['8_beam_tap'] = [C("component.activate", component="U1_FRAME")] + [
    cyl(1.65, [1143.7, 119.9, z], 8.2, Y, "cut", tg=["P_M07_BEAM"], fname="RX02_BEAM_M4_TAP_%d" % z) for z in (343, 359)] + [
    C("component.activate", component="root")]

order = ['1_move', '2_manifold', '3_station9', '4_tubes', '5_nozzle', '6_bolts', '7_rigid', '8_beam_tap']
allc = []
for k in order:
    json.dump(stages[k], open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    allc += stages[k]
json.dump(allc, open(os.path.join(os.path.dirname(OUT), 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
meta = {"PSW": {"len": round(LS, 2), "theta_deg": round(math.degrees(th), 3), "a3e": r4(a3e), "p1": r4(p1), "e1": r4(e1)},
        "RX08_B": {"len": round(LB, 2)}, "NOZ": {"len": round(LN, 2), "poly": round(NOZ_POLY, 2)},
        "PIPE": {"len": round(LP, 2), "segs": [[s[0]] + [r4(p) for p in s[1:]] for s in P_segs]}}
json.dump(meta, open(os.path.join(OUT, 'tubes.json'), 'w', encoding='utf-8'), indent=1)
print({k: len(stages[k]) for k in order}); print(json.dumps(meta))
