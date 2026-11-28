# RX-19 명령 생성기 (v2.28.1 -> 새 번호): U4 매달림을 블록 1 + 그네 1로 (C-54)
# 실행: python -B tools/gen_rx19.py -> tools/out/mech_RX-19/model/stage_*.json
# 좌표: J_U4_X 0(d1 100) · J_U4_PRESS 0(봉제 θ0) · J_U4_STOP 0에서 월드 좌표(설계안 mech_RX-19_design*.md, 선정 지시서).
# 모양 기준: mech_RX-19_design.md 5절, design2.md 6절, final_mech_2026-11-24 수정안(스토퍼 몸 -X, 조인트 +X 끝 <= -256.5).
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-19', 'model')
M = json.load(open(os.path.join(OUT, 'measured.json'), encoding='utf-8'))  # CAD에서 잰 자리(포트 축·부시·탭 구멍)
def C(cmd, **p): return {"command": cmd, "params": p}
r4 = lambda v: [round(x, 4) for x in v]
st = {}
CAR = "P_RX06_CARRIAGE"; SW = "P_M02_FRONT"

# ---------- 1. 블록: 캐리지에 이어 붙임(U4_XCAR) ----------
s = [C("component.activate", component="U4_XCAR")]
# 1a 옛 윗판 볼트 구멍 6 메움(r2.75, Z 250~262)
for i, (x, y) in enumerate([(-232, 50), (-215, 50), (-150, 50), (-215, 85), (-180, 85), (-150, 85)]):
    s.append(C("solid.cylinder", radius=2.75, height=12, base=[x, y, 250], axis="Z", operation="join", targets=[CAR], name="RX19_BLK_FILL_%d" % (i + 1)))
# 1b 선반 t14 (Z 236~250) — 스토퍼 쪽 띠 X -424~-330 · Y 25~70
SX = M['stop_leg_x0']  # 스토퍼 다리 -X 끝
poly = [(SX, 25), (-330, 25), (-330, -44.46), (-135, -44.46), (-135, 107), (-330, 107), (-330, 70), (SX, 70)]
# (다리 -X 끝 SX는 measured.json — 스토퍼 몸 X -392~-344.5)
s += [C("sketch.create", plane={"origin": [0, 0, 236], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_RX19_BLK_SHELF"),
      C("sketch.line", points=[list(p) for p in poly], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX19_BLK_SHELF", distance=14, operation="join", targets=[CAR], name="RX19_BLK_SHELF")]
st['1_block_shelf'] = s
s = [C("component.activate", component="U4_XCAR")]
# 1c 러그(핀 받침) X -158~-136, Y 61~89, 밑 R14 반원, 핀 구멍 r6 (Y 75, Z 135)
s += [C("sketch.create", plane={"origin": [-158, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX19_BLK_LUG"),
      C("sketch.line", points=[[89, 135], [89, 236], [61, 236], [61, 135]]),
      C("sketch.arc.three_point", start=[61, 135], through=[75, 121], end=[89, 135]),
      C("sketch.circle.center", center=[75, 135], radius=6),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX19_BLK_LUG", distance=22, operation="join", targets=[CAR], name="RX19_BLK_LUG")]
# 1d 실린더 다리 X -264~-216, Y -44.46~-34.46, Z 156~236 + 볼트 구멍 r3.3 ×4
s.append(C("solid.box", corner=[-264, -44.46, 156], length=48, width=10, height=80, operation="join", targets=[CAR], name="RX19_BLK_CYL_LEG"))
for i, (x, z) in enumerate([(-252.75, 167.25), (-227.25, 167.25), (-252.75, 192.75), (-227.25, 192.75)]):
    s.append(C("solid.cylinder", radius=3.3, height=12, base=[x, -45.46, z], axis="Y", operation="cut", targets=[CAR], name="RX19_BLK_CYL_HOLE_%d" % (i + 1)))
# 1e 스톱 받침 기둥 + 머리 보 (한 스케치, XZ 단면을 Y로)
s += [C("solid.box", corner=[-268.5, 5, 150], length=8.5, width=24, height=86, operation="join", targets=[CAR], name="RX19_BLK_STOP_POST"),
      C("solid.box", corner=[-260, 17, 150], length=32, width=12, height=10, operation="join", targets=[CAR], name="RX19_BLK_STOP_BEAM")]
st['2_block_lug_leg'] = s
s = [C("component.activate", component="U4_XCAR")]
# 1f 스토퍼 다리 + 볼트 구멍 4(r2.75, 몸 볼트 자리)
s.append(C("solid.box", corner=[SX, 25.2, 138], length=12, width=44, height=98, operation="join", targets=[CAR], name="RX19_BLK_STOP_LEG"))
for i, (y, z) in enumerate(M['lip_yz']):
    s.append(C("solid.cylinder", radius=2.75, height=14, base=[SX - 1, y, z], axis="X", operation="cut", targets=[CAR], name="RX19_BLK_STOP_HOLE_%d" % (i + 1)))
# 1g U6 관 브래킷 탭 받침(옛 CB5-16_M08_PX 자리, M5 탭 축 Z 236)
s.append(C("solid.box", corner=[-330, -16, 226], length=12, width=32, height=10, operation="join", targets=[CAR], name="RX19_BLK_U6_PAD"))
# 1h 스프링 위 고리 탭 2 (t6, 고리 구멍 r2)
for i, x0 in enumerate((-148, -203)):
    s.append(C("solid.box", corner=[x0, -1, 218], length=6, width=12, height=18, operation="join", targets=[CAR], name="RX19_BLK_SPR_TAB_%d" % (i + 1)))
    s.append(C("solid.cylinder", radius=2, height=8, base=[x0 - 1, 5, 226], axis="X", operation="cut", targets=[CAR], name="RX19_BLK_SPR_HOLE_%d" % (i + 1)))
# 1i 관 구멍 r4 (선반 관통)
for i, (x, y) in enumerate(M['tube_holes']):
    s.append(C("solid.cylinder", radius=4, height=16, base=[x, y, 235], axis="Z", operation="cut", targets=[CAR], name="RX19_BLK_TUBE_HOLE_%d" % (i + 1)))
st['3_block_legs'] = s

# ---------- 2. 그네: 앞판에 이어 붙임(U4_PRESS) ----------
s = [C("component.activate", component="U4_PRESS")]
# 2a 옛 팔 옆판 볼트 탭 4 메움
for i, (c, ax, h) in enumerate(M['front_taps']):
    s.append(C("solid.cylinder", radius=M['front_tap_r'], height=h, base=c, axis=ax, operation="join", targets=[SW], name="RX19_SW_FILL_%d" % (i + 1)))
# 2b 윗판 t12 (Z 104~116) + 앞 띠 + 스프링 탭 다리
top = [(-250, 45), (-207, 45), (-207, -5), (-193, -5), (-193, 45), (-152, 45), (-152, -5), (-138, -5), (-138, 45), (-132, 45),
       (-132, -31), (-120, -31), (-120, 91), (-250, 91)]
s += [C("sketch.create", plane={"origin": [0, 0, 104], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_RX19_SW_TOP"),
      C("sketch.line", points=[list(p) for p in top], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX19_SW_TOP", distance=12, operation="join", targets=[SW], name="RX19_SW_TOP")]
# 2c 뺨 2 (앞 X -132~-120, 뒤 X -172~-160): Y 59~91, Z 116~135 + R16 머리, 부시 구멍 r7
for nm, x0 in (("FRONT", -132), ("BACK", -172)):
    sk = "SK_RX19_SW_CHEEK_" + nm
    s += [C("sketch.create", plane={"origin": [x0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name=sk),
          C("sketch.line", points=[[59, 135], [59, 116], [91, 116], [91, 135]]),
          C("sketch.arc.three_point", start=[91, 135], through=[75, 151], end=[59, 135]),
          C("sketch.circle.center", center=[75, 135], radius=9),
          C("sketch.finish"),
          C("solid.extrude", sketch=sk, distance=12, operation="join", targets=[SW], name="RX19_SW_CHEEK_" + nm)]
st['4_swing_top_cheeks'] = s
s = [C("component.activate", component="U4_PRESS")]
# 2d 텅: X -246~-234 (Z 116~160), 위 X -244~-236 (Z 160~205), Y 65~85
tg = [(-246, 116), (-234, 116), (-234, 160), (-236, 160), (-236, 205), (-244, 205), (-244, 160), (-246, 160)]
s += [C("sketch.create", plane={"origin": [0, 85, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX19_SW_TONGUE"),
      C("sketch.line", points=[list(p) for p in tg], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX19_SW_TONGUE", distance=20, operation="join", targets=[SW], name="RX19_SW_TONGUE")]
# 2e 텅 장공: 핀 축 (Y 75, Z 135)에서 반지름 44.6~47.4, 방향 6.363° (-Y 쪽), 폭 8.1
a = math.radians(6.363); u = (-math.sin(a), math.cos(a))
p0 = (75 + u[0] * 44.6, 135 + u[1] * 44.6); p1 = (75 + u[0] * 47.4, 135 + u[1] * 47.4)
s += [C("sketch.create", plane={"origin": [-247, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX19_SW_SLOT"),
      C("sketch.slot.center_to_center", p0=r4(p0), p1=r4(p1), width=8.1),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX19_SW_SLOT", distance=14, operation="cut", targets=[SW], name="RX19_SW_SLOT")]
# 2f 스프링 아래 고리판 2 (t6, Z 116~124, 구멍 r2 Z 120)
for i, x0 in enumerate((-148, -203)):
    s.append(C("solid.box", corner=[x0, -1, 116], length=6, width=12, height=8, operation="join", targets=[SW], name="RX19_SW_SPR_TAB_%d" % (i + 1)))
    s.append(C("solid.cylinder", radius=2, height=8, base=[x0 - 1, 5, 120], axis="X", operation="cut", targets=[SW], name="RX19_SW_SPR_HOLE_%d" % (i + 1)))
st['5_swing_tongue'] = s

# ---------- 3. 핀 · 칼라 (U4_WHEEL_N, 블록 쪽) ----------
s = [C("component.activate", component="U4_WHEEL_N"),
     # 부시 플랜지(두께 3)가 뺨 바깥에 나와 칼라를 3씩 밖으로: 칼라 X -185~-175 · -117~-107, 핀 X -186~-106(80)
     C("solid.cylinder", radius=6, height=80, base=[-186, 75, 135], axis="X", operation="new", body_name="STEP대기_PSFJ12-80", name="RX19_PIN"),
     C("material.assign", bodies=["STEP대기_PSFJ12-80"], material="S45C"),
     C("solid.move", bodies=["STEP대기_PSCS12-10_1"], translate=[155, -45, -5], name="RX19_MV_COLLAR_1"),
     C("solid.move", bodies=["STEP대기_PSCS12-10_2"], translate=[35, -45, -5], name="RX19_MV_COLLAR_2"),
     C("component.activate", component="root")]
st['6_pin'] = s

# ---------- 4. 스톱 블록 · 플로팅 조인트 (U4_STOP) — 스토퍼를 옮긴 뒤 ----------
JX0 = M['joint_x0']  # 조인트 -X 끝(물러남)
# U4_STOP 컴포넌트 좌표: 월드 = (x - 154.5, 139.2 - z, y + 74) -> 로컬 = (X + 154.5, Z - 74, 139.2 - Y)
def sl(p): return [round(p[0] + 154.5, 4), round(p[2] - 74, 4), round(139.2 - p[1], 4)]
FJ = "STEP대기_JA30-8-125"
s = [C("component.activate", component="U4_STOP"),
     C("solid.box", corner=sl([-268, 65.4, 150]), length=18, width=16, height=36.4, operation="new", body_name="P_RX08_STOP_BLOCK_밀링", name="RX19_STOP_BLOCK"),
     C("solid.cylinder", radius=4.0, height=12, base=sl([-268, 47.2, 158]), axis="X", operation="cut", targets=["P_RX08_STOP_BLOCK_밀링"], name="RX19_STOP_BLOCK_TAP"),
     C("material.assign", bodies=["P_RX08_STOP_BLOCK_밀링"], material="SUS304"),
     C("solid.cylinder", radius=12, height=45, base=sl([JX0, 47.2, 158]), axis="X", operation="new", body_name=FJ, name="RX19_FJ_BODY"),
     C("solid.cylinder", radius=5, height=10, base=sl([JX0, 47.2, 158]), axis="X", operation="cut", targets=[FJ], name="RX19_FJ_SOCKET"),
     C("solid.cylinder", radius=4.0, height=round(-256.0 - (JX0 + 45), 4), base=sl([JX0 + 45, 47.2, 158]), axis="X", operation="join", targets=[FJ], name="RX19_FJ_STUD"),
     C("material.assign", bodies=[FJ], material="Steel"),
     # 너클: 둘로 갈린 갈래를 다시 한 몸으로(U4S_ROD 좌표 = (-480 - X, Y - 6.984, 403 - Z))
     C("component.activate", component="U4S_ROD"),
     C("solid.move", bodies=["STEP대기_Y-020B (1)"], translate=[0, -50, 0], name="RX19_MV_KNUCKLE_2"),
     C("solid.box", corner=[-244.1, 43.98 - 6.984, 213], length=8.2, width=14, height=20, operation="new", body_name="RX19_KN_WEB", name="RX19_KNUCKLE_WEB"),
     C("solid.combine", target="STEP대기_Y-020B", tools=["STEP대기_Y-020B (1)", "RX19_KN_WEB"], operation="join"),
     C("solid.cylinder", radius=3.4, height=12, base=[-240, 43.98 - 6.984 - 0.1, 223], axis="Y", operation="cut", targets=["STEP대기_Y-020B"], name="RX19_KNUCKLE_TAP"),
     C("component.activate", component="root")]
st['8_stop_parts'] = s

# ---------- 5. 관 4줄 다시 쓸기 (포트 출구 -> 선반 구멍 -> 층별 가로 -> 이음점 Z 340) ----------
R = 10.0
def arc(st_, d_in, d_out):
    """st_에서 d_in 방향으로 들어와 d_out 방향으로 나가는 R10 90° 호 -> (start, through, end)"""
    ce = [st_[k] + R * d_out[k] for k in range(3)]
    en = [ce[k] - R * d_in[k] * -1 for k in range(3)]  # 중심 + R·d_in
    m = [(st_[k] + en[k]) / 2 - ce[k] for k in range(3)]; ml = math.sqrt(sum(x * x for x in m))
    th = [ce[k] + m[k] / ml * R for k in range(3)]
    return ('a', list(st_), th, en)
def route(p, legs):
    """p: 출구 끝점, legs: [(방향, 끝 좌표 값)] — 방향 벡터와 그 축의 목표 값. 꺾일 때마다 R10 호."""
    segs = []; cur = list(p); d = legs[0][0]
    for i, (dv, target) in enumerate(legs):
        if i > 0:
            a_ = arc(cur, d, dv); segs.append(a_); cur = a_[3]; d = dv
        ax = [k for k in range(3) if dv[k] != 0][0]
        # 다음 꺾임 호가 R만큼 쓰므로 직선은 target - R*sign (마지막 구간은 target까지)
        end = list(cur); end[ax] = target - (R * dv[ax] if i < len(legs) - 1 else 0)
        if abs(end[ax] - cur[ax]) > 1e-6: segs.append(('l', list(cur), end)); cur = end
    return segs
X_, Y_, Z_ = [1, 0, 0], [0, 1, 0], [0, 0, 1]; mX, mY = [-1, 0, 0], [0, -1, 0]
TU = M.get('tubes', {})
def tube_stage(body, segs):
    sk = "SK_%s_RX19" % body
    c = [C("solid.remove", bodies=[body], name="RM_%s_RX19" % body), C("component.activate", component=body),
         C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    for g in segs:
        if g[0] == 'l': c.append(C("sketch.line3d", points=[r4(g[1]), r4(g[2])]))
        else: c.append(C("sketch.arc3d", start=r4(g[1]), through=r4(g[2]), end=r4(g[3])))
    c += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(segs))], diameter=6.0, operation="new", body_name=body, name="PIPE_%s_RX19" % body),
          C("material.assign", bodies=[body], material="Default"),
          C("component.activate", component="root")]
    return c
if TU:
    XS = -159.506
    rod = TU['rod']; head = TU['head']; a8 = TU['rx08_a']; b8 = TU['rx08_b']
    segs = {}
    # rod: 출구 -Y -> 위 -> +Y(Z 280) -> +X(Y 79) -> 위(X XS) -> Z 340
    # 관 길(RX-19 모델링 중 다시 잡음): 올림은 모두 X0 -310~-262 · Y >= 46(고정 U6 관 Z 262 · Y 32 줄과 X -347 줄, d1 195의 U5 덮개 X <= -420 · Z >= 290을 피함)
    segs['TU0604_M08P_U4_A2_U4'] = route(rod, [(Y_, 46), (mX, -262), (Z_, 283), (Y_, 79), (X_, XS), (Z_, 340)])
    segs['TU0604_M08P_U4_B_U4'] = route(head, [(mX, -285), (Y_, 50), (Z_, 271), (Y_, 70), (X_, XS), (Z_, 340)])
    segs['TU0604_M08P_RX08_A_U4'] = route(a8, [(X_, -310), (Z_, 312), (Y_, 88), (X_, -169), (Z_, 340)])
    segs['TU0604_M08P_RX08_B_U4'] = route(b8, [(mY, 22.7), (Z_, 226), (X_, -295), (Y_, 61), (Z_, 302), (X_, -169), (Z_, 340)])
    s = []
    for b, sg in segs.items(): s += tube_stage(b, sg)
    st['7_tubes'] = s
    json.dump(segs, open(os.path.join(OUT, 'tube_paths.json'), 'w'), indent=1)

json.dump(st, open(os.path.join(OUT, 'gen_rx19_stages.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in st.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in st.items()})
