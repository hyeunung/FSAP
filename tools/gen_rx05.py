# RX-05 U5 대차 홈 솔 덮개 — 명령 생성기 (v2.22.4 -> v2.23.0)
# 사용: python -B tools/gen_rx05.py  -> tools/out/mech_RX-05/model/stage_*.json
# 큰 설계(피처 약 3,750)에서는 명령 하나마다 앱이 오래 걸려, 구멍·볼트는 피처/컴포넌트 패턴으로 묶는다.
import json, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mech_RX-05", "model")
os.makedirs(OUT, exist_ok=True)
STEP = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def stage(name, cmds):
    with open(os.path.join(OUT, f"stage_{name}.json"), "w", encoding="utf-8") as f:
        json.dump(cmds, f, ensure_ascii=False, indent=1)
    return cmds


def box(name, body, x0, x1, y0, y1, z0, z1, op="new", targets=None):
    p = dict(corner=[x0, y0, z0], length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4),
             operation=op, name=name)
    if op == "new":
        p["body_name"] = body
    else:
        p["targets"] = targets or [body]
    return C("solid.box", **p)


def holes(name, target, r, base, axis, h, n1, d1, s1, n2=None, d2=None, s2=None):
    """원통 구멍 하나 + 피처 직사각 패턴(2단계)"""
    cmds = [C("solid.cylinder", radius=r, height=h, base=base, axis=axis, operation="cut",
              targets=target if isinstance(target, list) else [target], name=name)]
    p = dict(features=[name], dir1=d1, count1=n1, spacing1=s1, name=name + "_P")
    if n2:
        p.update(dir2=d2, count2=n2, spacing2=s2)
    cmds.append(C("solid.pattern.rectangular", **p))
    return cmds


# 구멍 자리 (지시서)
X7 = (-2140, 280.0)     # CB5-12 7곳: -2140 ~ -460
XT = (-2015, 187.5)     # B1 · B2 / 윗판 9곳: -2015 ~ -515, Y 38(지시 39 -> 38: CB4 머리 R3.5가 립 굽힘 안 R2(Y 42~44)에 0.02 mm³ 걸림) · Y 95
XB3 = (-2160, 215.0)    # B3 / 앞벽 9곳: -2160 ~ -440
XB4 = (-2140, 210.0)    # B4 / 받침 윗 날개 9곳: -2140 ~ -460
PX = [1, 0, 0]

# ---------- 1. 덮개 P_M03_GCOV_SM — A5052 t2 R2 판금(상자로 접은 모양 -> sheet.recognize로 굽힘 R2) ----------
CV = "P_M03_GCOV_SM"
s1 = [
    C("component.activate", component="root"),
    C("sheet.manage_rules", name="A5052_t2_R2", thickness="2", bend_radius="2", k_factor="0.44",
      corner_relief_shape="rectangular", corner_relief="2", material="A5052", active=True),
    box("RX05_GCOV_TOP", CV, -2180, -420, 27, 120, 466, 468),
    box("RX05_GCOV_WIN", CV, -2015, -515, 46, 90, 465, 469, op="cut"),          # 솔 창 관통
    box("RX05_GCOV_LIP", CV, -2010, -520, 44, 46, 440, 466, op="join"),          # 창 앞 립(아래로)
    box("RX05_GCOV_FRONT", CV, -2180, -420, 27, 29, 290, 466, op="join"),        # 앞벽
    box("RX05_GCOV_BOT", CV, -2180, -420, 29, 37, 290, 292, op="join"),          # 밑 날개(안쪽)
    box("RX05_GCOV_BACK", CV, -2180, -420, 118, 120, 468, 520, op="join"),       # 뒤 날개(위로)
]
# 구멍은 판금으로 바꾸기 전에(굽힘·이음과 떨어진 자리, 바꾼 뒤엔 오림으로 남는다)
s1 += holes("RX05_GCOV_TOP_H", CV, 2.25, [XT[0], 38, 465.8], [0, 0, 1], 2.4, 9, PX, XT[1], 2, [0, 1, 0], 57)
s1 += holes("RX05_GCOV_FRONT_H", CV, 2.25, [XB3[0], 26.8, 297], [0, 1, 0], 2.4, 9, PX, XB3[1])
s1 += holes("RX05_GCOV_BACK_H", CV, 2.75, [X7[0], 117.8, 500], [0, 1, 0], 2.4, 7, PX, X7[1])
s1 += [
    C("sheet.recognize", body=CV, face=[-1300, 35, 468],
      bends=[[-1300, 27, 468], [-1300, 27, 290], [-1300, 120, 466], [-1300, 46, 468]]),
    # 끝 날개 ×2: 앞벽 끝 모서리에서 +Y로 굽힘(바깥 가상 꼭짓점 Y 27 -> 끝 Y 80)
    C("sheet.flange", edges=[[-2180, 27, 380], [-420, 27, 380]], height=53, angle=90, flip=True,
      body=CV, name="RX05_GCOV_ENDS"),
]
stage("1_cover", s1)

# ---------- 2. 받침 P_M03_GCOV_RBRKT_SM — A5052 t3 R3 Z자 ----------
RB = "P_M03_GCOV_RBRKT_SM"
s2 = [
    C("sheet.manage_rules", name="A5052_t3_R3", thickness="3", bend_radius="3", k_factor="0.44",
      corner_relief_shape="rectangular", corner_relief="3", material="A5052", active=True),
    C("sketch.create", plane={"origin": [0, 0, 247], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_RX05_RBRKT"),
    C("sketch.rectangle.two_point", p0=[-2160, 114], p1=[-440, 150]),
    C("sketch.finish"),
    C("sheet.flange", type="base", sketch="SK_RX05_RBRKT", rule="A5052_t3_R3", body_name=RB, name="RX05_RBRKT_FOOT"),  # 보 밑 다리 Z 247~250
    # 세운 판 Y 114~117(지시 117~120에서 -3: 굽힘 안 R3이 보 밑 앞 모서리(Y 120 · Z 250)를 파고들어 3,322 mm³ 겹침 -> 3 띄움)
    # 바깥 가상 꼭짓점 Z 247 -> 261, 반대로 접은 윗 날개는 Y 117 -> 100(-Y)
    C("sheet.flange", edges=[[-1300, 114, 250]], height=14, angle=90, then=[{"height": 17, "flip": True}],
      body=RB, name="RX05_RBRKT_WALL"),
]
s2 += holes("RX05_RBRKT_FOOT_H", RB, 2.75, [X7[0], 140, 246.8], [0, 0, 1], 3.4, 7, PX, X7[1])
s2 += holes("RX05_RBRKT_TOP_H", RB, 2.25, [XB4[0], 105, 257.8], [0, 0, 1], 3.4, 9, PX, XB4[1])
s2 += [C("sheet.manage_rules", name="A5052_t2_R2", active=True)]
stage("2_rbrkt", s2)

# ---------- 3. 솔 띠 4개 (STEP대기_ 임시 형상: 홀더 10×10 A5052 + 털 t4 나일론) ----------
B = "STEP대기_BRSEAL_"
H1, T1 = B + "B25_1_HOLDER", B + "B25_1_BRISTLE"
H2, T2 = B + "B25_2_HOLDER", B + "B25_2_BRISTLE"
H3, T3 = B + "B40_1_HOLDER", B + "B40_1_BRISTLE"
H4, T4 = B + "B25_3_HOLDER", B + "B25_3_BRISTLE"
s3 = [
    box("RX05_B1_HOLDER", H1, -2025, -505, 34, 44, 468, 478),
    box("RX05_B1_BRISTLE", T1, -2025, -505, 44, 69, 471, 475),
    box("RX05_B2_HOLDER", H2, -2025, -505, 90, 100, 468, 478),
    box("RX05_B2_BRISTLE", T2, -2025, -505, 65, 90, 471, 475),
    # B3 홀더: 앞벽–밑 날개 굽힘 안 R2와 닿지 않게 앞 아래 모서리 2×2 모따기, 끝 날개 굽힘 안 R2를 피해 X -2176 ~ -424
    C("sketch.create", plane={"origin": [-2176, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX05_B3_HOLDER"),
    C("sketch.line", points=[[31, 292], [39, 292], [39, 302], [29, 302], [29, 294]], closed=True),
    C("sketch.finish"),
    C("solid.extrude", sketch="SK_RX05_B3_HOLDER", distance=1752, operation="new", body_name=H3, name="RX05_B3_HOLDER"),
    box("RX05_B3_BRISTLE", T3, -2178, -422, 39, 80, 295, 299),
    box("RX05_B4_HOLDER", H4, -2160, -440, 100, 110, 261, 271),
    box("RX05_B4_BRISTLE", T4, -2160, -440, 75, 100, 264, 268),
]
# 홀더 M4 탭 자리(Ø3.3, 홀더 관통 10)
s3 += holes("RX05_B12_TAP", [H1, H2], 1.65, [XT[0], 38, 467.8], [0, 0, 1], 10.4, 9, PX, XT[1], 2, [0, 1, 0], 57)
s3 += holes("RX05_B3_TAP", [H3], 1.65, [XB3[0], 28.8, 297], [0, 1, 0], 10.4, 9, PX, XB3[1])
s3 += holes("RX05_B4_TAP", [H4], 1.65, [XB4[0], 105, 260.8], [0, 0, 1], 10.4, 9, PX, XB4[1])
stage("3_brush", s3)

# ---------- 4. 보 M5 탭 14 (앞벽 Y 120~128 · 밑벽 Z 250~258, 이력 끝 피처) ----------
s4 = [C("component.activate", component="U1_FRAME")]
s4 += holes("RX05_BEAM_TAP_F", "P_M07_BEAM", 2.1, [X7[0], 119.9, 500], [0, 1, 0], 8.2, 7, PX, X7[1])
s4 += holes("RX05_BEAM_TAP_B", "P_M07_BEAM", 2.1, [X7[0], 140, 249.9], [0, 0, 1], 8.2, 7, PX, X7[1])
s4 += [C("component.activate", component="root")]
stage("4_beam", s4)

# ---------- 5. 컴포넌트 · 재질 · 속성 ----------
s5 = [C("component.create", name="U5_GCOV", parent="U5_WHEEL_F", activate=False),
      C("component.metadata.set", component="U5_GCOV", part_number="U5_GCOV", bom_type="phantom",
        description="U5 carriage groove brush cover (RX-05): sheet cover + Z bracket + 4 brush strips, fixed under U5_WHEEL_F to beam P_M07_BEAM")]
made = [
    (CV, "A5052-H32 sheet metal t2 R2 (laser + press brake) groove cover X -2180..-420: top with brush window 1500x44 + front lip, front wall, inner bottom flange, 2 end flanges, back flange 7x D5.5 to beam front (RX-05)"),
    (RB, "A5052-H32 sheet metal t3 R3 Z bracket X -2160..-440 under beam: foot 7x D5.5 to beam bottom, top flange 9x D4.5 carries brush B4 (RX-05)"),
]
for comp, desc in made:
    s5 += [C("material.assign", bodies=[comp], material="A5052"),
           C("component.create", name=comp, parent="U5_GCOV", activate=False),
           C("component.move_bodies", bodies=[comp], component=comp),
           C("component.metadata.set", component=comp, part_number=comp, bom_type="normal", description=desc)]
brushes = [
    ("B25_1", H1, T1, "BRSEAL-H10-B25", "top front, X -2025..-505, bristle Y 44->69 (25)"),
    ("B25_2", H2, T2, "BRSEAL-H10-B25", "top back, X -2025..-505, bristle Y 90->65 (25)"),
    ("B40_1", H3, T3, "BRSEAL-H10-B40", "bottom front, holder X -2176..-424, bristle X -2178..-422 Y 39->80 (41)"),
    ("B25_3", H4, T4, "BRSEAL-H10-B25", "bottom back, X -2160..-440, bristle Y 100->75 (25)"),
]
s5 += [C("material.assign", bodies=[H1, H2, H3, H4], material="A5052"),
       C("material.assign", bodies=[T1, T2, T3, T4], material="Nylon")]
for tag, hb, tb, pn, where in brushes:
    comp = B + tag
    s5 += [C("component.create", name=comp, parent="U5_GCOV", activate=False),
           C("component.move_bodies", bodies=[hb, tb], component=comp),
           C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased",
             description=f"STEP pending (E-10 provisional): strip brush seal, holder 10x10 A5052 + nylon bristle t4, {where}, holder M4 tap x9 (provisional; part number not fixed, RX-05)")]
stage("5_comp", s5)


# ---------- 6. 볼트 (purchased-step STEP + 컴포넌트 패턴) ----------
def mat_y(x, y, z):   # 나사 쪽 +Y, 원점 = 머리 밑
    return [0, 1, 0, x, 1, 0, 0, y, 0, 0, -1, z]


def mat_z(x, y, z):   # 나사 쪽 +Z
    return [0, 1, 0, x, 0, 0, 1, y, 1, 0, 0, z]


def bolts(spec, name, desc, p0, mk, n1, s1, n2=None, d2=None, s2=None):
    cmds = [C("file.insert_step", path=f"{STEP}/{spec}/{spec}.stp", name=name, matrix=mk(*p0)),
            C("body.rename", body="Cut-Extrude1", name=name),
            C("component.metadata.set", component=name, part_number=spec, bom_type="purchased", description=desc),
            C("material.assign", bodies=[name], material="SCM435"),
            C("occurrence.reparent", occurrence=f"{name}:1", parent="U5_GCOV")]
    p = dict(components=[name], dir1=PX, count1=n1, spacing1=s1, name="RX05_PAT_" + name)
    if n2:
        p.update(dir2=d2, count2=n2, spacing2=s2)
    cmds.append(C("solid.pattern.rectangular", **p))
    return cmds


s6 = bolts("CB5-12", "CB5-12_RX05_BEAM", "Misumi CB5-12 STEP, RX-05: cover back flange to beam front wall M5 tap x7 (Z 500)",
           (X7[0], 118, 500), mat_y, 7, X7[1])
s6 += bolts("CB5-12", "CB5-12_RX05_BRKT", "Misumi CB5-12 STEP, RX-05: Z bracket foot to beam bottom wall M5 tap x7 (Y 140)",
            (X7[0], 140, 247), mat_z, 7, X7[1])
s6 += bolts("CB4-12", "CB4-12_RX05_TOP", "Misumi CB4-12 STEP, RX-05: brush holders B1 B2 from under cover top M4 x18",
            (XT[0], 38, 466), mat_z, 9, XT[1], 2, [0, 1, 0], 57)
s6 += bolts("CB4-12", "CB4-12_RX05_B3", "Misumi CB4-12 STEP, RX-05: brush holder B3 through cover front wall M4 x9 (Z 297)",
            (XB3[0], 27, 297), mat_y, 9, XB3[1])
s6 += bolts("CB4-12", "CB4-12_RX05_B4", "Misumi CB4-12 STEP, RX-05: brush holder B4 from under bracket top flange M4 x9 (Y 105)",
            (XB4[0], 105, 258), mat_z, 9, XB4[1])
stage("6_bolts", s6)

# ---------- 7. 관 TU0604_M08P_U5C_2 경로 고침 ----------
R = 20.0


def add(a, b): return [x + y for x, y in zip(a, b)]
def sub(a, b): return [x - y for x, y in zip(a, b)]
def mul(a, k): return [x * k for x in a]
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def unit(a): n = math.sqrt(dot(a, a)); return [x / n for x in a]


segs = []
P = [-2000.7, 30.0, 190.5]
D = [0.0, -1.0, 0.0]


def line(L):
    global P
    Q = add(P, mul(D, L)); segs.append(("line", [P, Q])); P = Q


def arc(dnew):
    global P, D
    d0, d1 = unit(D), unit(dnew)
    th = math.acos(max(-1.0, min(1.0, dot(d0, d1))))
    n = unit(sub(d1, mul(d0, dot(d0, d1))))
    c = add(P, mul(n, R))
    at = lambda a: add(c, mul(add(mul(n, -math.cos(a)), mul(d0, math.sin(a))), R))
    segs.append(("arc", [P, at(th / 2), at(th)]))
    P, D = at(th), d1


line(10.0)                                  # 피팅 AS2201F_U5_2 출구(-Y) 직선 10
arc([0, 0, 1.0])                            # -Y -> +Z, R20
line(5.0)
h = [-1979.0 - P[0], 49.0 - P[1], 0.0]
H = math.sqrt(dot(h, h)); u = unit(h)
th = math.radians(45.0)
L = (H - 2 * R * (1 - math.cos(th))) / math.sin(th)
arc(add(mul(u, math.sin(th)), [0, 0, math.cos(th)]))   # S 굽힘: (-2000.7, 0) -> (-1979, 49), Z 288 밑에서 끝
line(L)
arc([0, 0, 1.0])
line(360.0 - P[2])                          # X -1979 · Y 49 위로(Z 285.7 ~ 360)
th2 = math.acos(1 - (56.0 - P[1]) / (2 * R))
arc([0, math.sin(th2), math.cos(th2)])      # 작은 S: Y 49 -> 56
arc([0, 0, 1.0])
line(782.0 - P[2])                          # 관 클램프(Z 396~416) 통과 자리 · 그 위는 옛 경로 그대로
segs += [
    ("arc", [[-1979.0, 56.0, 782.0], [-1979.0, 64.7868, 803.2132], [-1979.0, 86.0, 812.0]]),
    ("line", [[-1979.0, 86.0, 812.0], [-1979.0, 220.0, 812.0]]),
    ("arc", [[-1979.0, 220.0, 812.0], [-1970.2132, 241.2132, 812.0], [-1949.0, 250.0, 812.0]]),
    ("line", [[-1949.0, 250.0, 812.0], [-1930.0, 250.0, 812.0]]),
]


def seglen(s):
    k, pts = s
    if k == "line":
        return math.dist(pts[0], pts[1])
    a, m, b = pts                                     # 세 점 호: 반지름 = abc / 4·넓이, 각 = 2·asin(현 / 2R)
    la, lb, lc = math.dist(m, b), math.dist(a, b), math.dist(a, m)
    sp = (la + lb + lc) / 2
    area = math.sqrt(max(sp * (sp - la) * (sp - lb) * (sp - lc), 1e-12))
    r = la * lb * lc / (4 * area)
    return r * 2 * math.asin(min(1.0, lb / (2 * r)))


total = sum(seglen(s) for s in segs)
r4 = lambda v: [round(c, 4) for c in v]
s7 = [C("component.activate", component="root"),
      C("solid.remove", bodies=["TU0604_M08P_U5C_2"], name="RM_TU0604_M08P_U5C_2_RX05"),
      C("sketch.create", plane="XY", name="SK_TU0604_M08P_U5C_2_RX05"),
      C("sketch.options", sketch_3d=True)]
for k, pts in segs:
    if k == "line":
        s7.append(C("sketch.line3d", points=[r4(pts[0]), r4(pts[1])]))
    else:
        s7.append(C("sketch.arc3d", start=r4(pts[0]), through=r4(pts[1]), end=r4(pts[2])))
s7 += [C("sketch.finish"),
       C("solid.pipe", path_sketch="SK_TU0604_M08P_U5C_2_RX05", path=[f"w{i + 1}" for i in range(len(segs))],
         diameter=6.0, operation="new", body_name="TU0604_M08P_U5C_2", name="PIPE_TU0604_M08P_U5C_2_RX05"),
       C("material.assign", bodies=["TU0604_M08P_U5C_2"], material="Default"),
       C("component.move_bodies", bodies=["TU0604_M08P_U5C_2"], component="TU0604_M08P_U5C_2"),
       C("component.metadata.set", component="TU0604_M08P_U5C_2", part_number="TU0604", bom_type="purchased",
         description=f"SMC TU0604 polyurethane tube OD6, cut length {total:.1f} (RX-05 reroute behind groove cover: up at X -2000.7 in front, S-bend to X -1979 Y 49 below Z 288, S to Y 56 at Z 360-383, then PNEU-01 route; bends R20 provisional)")]
stage("7_tube", s7)
json.dump({"segments": segs, "length_mm": total}, open(os.path.join(OUT, "tube_u5c2.json"), "w"), indent=1)
print("tube length", round(total, 2), "segments", len(segs))
for n in ("1_cover", "2_rbrkt", "3_brush", "4_beam", "5_comp", "6_bolts", "7_tube"):
    print(n, len(json.load(open(os.path.join(OUT, f"stage_{n}.json"), encoding="utf-8"))))
