# RX-13 U4 누름 실린더를 보 앞면 앞·모터 바로 위로 (C-50) 명령 생성기 (v2.20.2 -> v2.20.3).
# 실행: python -B tools/gen_rx13.py  -> tools/out/mech_RX-13/model/stage_*.json
# 좌표: 월드 mm, REST(J_U4_PRESS 13.006 들림, J_U4_X 0). 로드 묶음은 J_U4S_ROD 25(나옴 끝, 핀 Y 131.9)로 그린다.
# 지시와 다른 것(보고서 2절): 관 세움 자리(지금 관은 (-161.006, 79)·(-161.006, 70) 장공으로 내려온다),
#   엘보 출구 끝 14.5(STEP 실측), 잠금 너트(HNTT8-5는 T 홈 너트라 M8 얇은 너트 임시 형상).
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-13', 'model')
STEP = os.path.join(os.path.dirname(ROOT), 'purchased-step').replace('\\', '/')
os.makedirs(OUT, exist_ok=True)

XR, ZR = -240.0, 223.0          # 로드 축선
PIN = 131.9                     # REST 핀 Y (J_U4S_ROD 25)

def C(cmd, **p): return {"command": cmd, "params": p}
def box(name, x0, y0, z0, x1, y1, z1, op="new", targets=None):
    p = dict(corner=[x0, y0, z0], length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation=op)
    if op == "new": p["body_name"] = name
    if targets: p["targets"] = targets
    return C("solid.box", **p)
def cyl(r, h, base, axis, op, targets=None, name=None):
    p = dict(radius=r, height=h, base=base, axis=axis, operation=op)
    if targets: p["targets"] = targets
    if name: p["body_name"] = name
    return C("solid.cylinder", **p)
def flat(R, t): return [R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2]]
def hexpts(cx, cz, af):
    R = af / 2 / math.cos(math.radians(30))
    return [[round(cx + R * math.cos(math.radians(a)), 4), round(cz + R * math.sin(math.radians(a)), 4)] for a in range(0, 360, 60)]

stages = {}
BASE = "P_M02_BASE"
CY = "STEP대기_CDQSYB20-25DCM"
ROD = "STEP대기_CDQSYB20-25DCM_ROD"
BR = "P_RX13_CYL_BRKT_밀링"
EXT = "P_RX13_ROD_EXT_선반"
NUT = "STEP대기_NUT-M8_RX13"
KN = "STEP대기_Y-020B"; KP = "STEP대기_Y-020B_PIN"
HEADB = [(-252.75, 210.25), (-227.25, 210.25), (-252.75, 235.75), (-227.25, 235.75)]   # 실린더 M6 탭 (X, Z), 피치 25.5
EARB = [(-267, -31.1), (-267, -15.1), (-213, -31.1), (-213, -15.1)]                    # 귀 M5 (X, Y)
PORT_ROD = (-240, 13.4); PORT_HEAD = (-240, -30.1)                                      # 아래 면 Z 205 포트 (X, Y), 끝에서 8(임시 D-188)

# ---- 1. 지우기 (조인트·바디는 먼저 직접 보냄: joint.delete J_U4S_ROD·97865·97866, solid.remove 5바디)
stages['1_remove'] = [C("joint.delete", joint="J_U4S_ROD"), C("joint.delete", joint=97865), C("joint.delete", joint=97866),
                      C("solid.remove", bodies=["STEP대기_CDQ2YA20-25DMZ", "STEP대기_CDQ2YA20-25DMZ_ROD", "P_M02S_CYL_BRKT", KN, KP])]
stages['1b_deloccs'] = [C("selection.delete", occurrences=["CB5-12_M02S_BEAM_1:1", "CB5-12_M02S_BEAM_2:1"] + ["CB5-12_M02S_CYL_%d:1" % i for i in (1, 2, 3, 4)])]

# ---- 2. 윗판: 보 밑 연장부 자름(옛 M5 탭 2 포함) + 브래킷 볼트 통과 구멍 4
s2 = [C("component.activate", component="U4_WHEEL_N"),
      box(None, -331, 140, 241, -139, 267, 251, op="cut", targets=[BASE])]
for (x, y) in EARB:
    s2.append(cyl(2.75, 8.2, [x, y, 241.9], [0, 0, 1], "cut", targets=[BASE]))
s2.append(C("component.activate", component="root"))
stages['2_base'] = s2

# ---- 3. 실린더 몸(임시 형상) + 브래킷 (U4S_CYL 활성)
s3 = [C("component.activate", component="U4S_CYL"),
      box(CY, -258, -38.1, 205, -222, 21.4, 241),
      cyl(5.25, 30.1, [XR, 21.5, ZR], [0, -1, 0], "cut", targets=[CY])]          # 로드 구멍 D10.5 깊이 30
for (x, z) in HEADB:
    s3.append(cyl(2.5, 10.1, [x, -38.2, z], [0, 1, 0], "cut", targets=[CY]))      # 머리 쪽 M6 탭 자리 D5 깊이 10
for (x, y) in (PORT_ROD, PORT_HEAD):
    s3.append(cyl(2.55, 4.1, [x, y, 204.9], [0, 0, 1], "cut", targets=[CY]))      # 포트 M5 D5.1 깊이 4
s3 += [C("material.assign", bodies=[CY], material="Aluminum"),
       C("sketch.create", plane={"origin": [-275, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX13_CYL_BRKT"),
       C("sketch.line", points=[[-45.1, 203], [-38.1, 203], [-38.1, 234], [-8.1, 234], [-8.1, 242], [-45.1, 242]], closed=True),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_RX13_CYL_BRKT", distance=70, operation="new", body_name=BR, name="EX_RX13_CYL_BRKT"),
       box(None, -259, -38.1, 234, -221, -8.0, 242.1, op="cut", targets=[BR])]     # 귀 사이(몸 자리 + 틈 1)
for (x, z) in HEADB:
    s3.append(cyl(3.3, 7.2, [x, -45.2, z], [0, 1, 0], "cut", targets=[BR]))        # 앞벽 D6.6 통과
for (x, y) in EARB:
    s3.append(cyl(2.1, 8.2, [x, y, 233.9], [0, 0, 1], "cut", targets=[BR]))        # 귀 M5 탭 관통 8
s3 += [C("material.assign", bodies=[BR], material="SUS304"),
       C("component.metadata.set", component="U4S_CYL", part_number="CDQSYB20-25DCM", bom_type="purchased",
         description="STEP pending (E-10, D-188): SMC CQSY smooth compact cylinder bore 20 stroke 25 (CDQSYB20-25DCM), body 36x36x59.5 placeholder from catalog outline, M6 taps on head face, M5 ports on bottom face (port positions temporary) + P_RX13_CYL_BRKT SUS304 milled bracket under P_M02_BASE (RX-13, C-50)"),
       C("component.activate", component="root")]
stages['3_cyl'] = s3

# ---- 4. 로드 묶음 (U4S_ROD 활성): 로드 + 너트, 연장봉, 잠금 너트, 너클, 핀
s4 = [C("component.activate", component="U4S_ROD"),
      cyl(5, 34, [XR, 16.9, ZR], [0, 1, 0], "new", name=ROD),                      # 로드 D10 Y 16.9~50.9
      cyl(4, 14, [XR, 50.9, ZR], [0, 1, 0], "join", targets=[ROD]),                # 수나사 M8 Y 50.9~64.9
      C("sketch.create", plane={"origin": [0, 55.9, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX13_ROD_NUT"),
      C("sketch.line", points=hexpts(XR, ZR, 13), closed=True), C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX13_ROD_NUT", distance=5, operation="join", targets=[ROD], name="EX_RX13_ROD_NUT"),   # 로드 너트 대변 13 x 5
      cyl(7, 45, [XR, 55.9, ZR], [0, 1, 0], "new", name=EXT),                      # 연장봉 D14 Y 55.9~100.9
      cyl(4, 14, [XR, 100.9, ZR], [0, 1, 0], "join", targets=[EXT]),               # 수나사 M8 Y 100.9~114.9
      cyl(3.4, 12.1, [XR, 55.8, ZR], [0, 1, 0], "cut", targets=[EXT]),             # 암나사 M8 자리 D6.8 깊이 12
      box(None, -248, 74.4, 215, -246, 82.4, 231, op="cut", targets=[EXT]),        # 스패너 면 대변 12 x 8
      box(None, -234, 74.4, 215, -232, 82.4, 231, op="cut", targets=[EXT]),
      C("sketch.create", plane={"origin": [0, 105.9, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX13_LOCK_NUT"),
      C("sketch.line", points=hexpts(XR, ZR, 13), closed=True), C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX13_LOCK_NUT", distance=5, operation="new", body_name=NUT, name="EX_RX13_LOCK_NUT"),  # 잠금 너트 Y 100.9~105.9
      cyl(3.4, 5.2, [XR, 100.8, ZR], [0, 1, 0], "cut", targets=[NUT]),
      C("sketch.create", plane={"origin": [0, 0, 213], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_RX13_KNUCKLE"),
      C("sketch.line", points=[[-251, PIN - 26], [-229, PIN - 26], [-229, PIN + 10], [-234.8, PIN + 10], [-234.8, PIN - 14],
                               [-245.2, PIN - 14], [-245.2, PIN + 10], [-251, PIN + 10]], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX13_KNUCKLE", distance=20, operation="new", body_name=KN, name="EX_RX13_KNUCKLE"),
      cyl(4.05, 24, [-252, PIN, ZR], [1, 0, 0], "cut", targets=[KN]),              # 핀 구멍
      cyl(3.4, 12.2, [XR, PIN - 26.1, ZR], [0, 1, 0], "cut", targets=[KN]),        # 암나사 M8 자리
      cyl(6, 2, [-253, PIN, ZR], [1, 0, 0], "new", name=KP),
      cyl(4, 23.5, [-251, PIN, ZR], [1, 0, 0], "join", targets=[KP]),
      C("material.create", name="SUS303", density_g_cm3=7.93),
      C("material.assign", bodies=[ROD, KP], material="S45C"),
      C("material.assign", bodies=[KN, NUT], material="Steel"),
      C("material.assign", bodies=[EXT], material="SUS303"),
      C("component.metadata.set", component="U4S_ROD", part_number="CDQSYB20-25DCM rod + Y-020B", bom_type="purchased",
        description="STEP pending: CQSY rod D10 (male M8x1.25, rod nut 13x5) + P_RX13_ROD_EXT SUS303 turned extension D14x45 + M8 thin lock nut (placeholder, part number open) + SMC Y-020B single knuckle (fork to +Y, pin D8). Pull = press (RX-13)"),
      C("component.activate", component="root")]
stages['4_rod'] = s4

# ---- 5. 구매품: 볼트 8(실물 STEP), 엘보 2(있는 것 옮김)
R_PY = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]        # 볼트 로컬 +x -> 월드 +Y (앞에서 뒤로)
R_NZ = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]        # 로컬 +x -> 월드 -Z (위에서 아래로)
BOLTS = []
for i, (x, z) in enumerate(HEADB, 1):
    BOLTS.append(("CB6-16", "CB6-16_RX13_CYL_%d" % i, R_PY, (x, -45.1, z), "RX-13 cylinder head face M6 tap <- bracket front wall (U-12 exception: cylinder tap fixes M6)"))
for i, (x, y) in enumerate(EARB, 1):
    BOLTS.append(("CB5-16", "CB5-16_RX13_BRKT_%d" % i, R_NZ, (x, y, 250), "RX-13 bracket ear M5 tap <- P_M02_BASE top plate (from above)"))
s5 = [C("component.activate", component="root")]
for (spec, name, R, t, desc) in BOLTS:
    s5 += [C("file.insert_step", path="%s/%s/%s.stp" % (STEP, spec, spec), name=name, matrix=flat(R, t)),
           C("body.rename", body="Cut-Extrude1", name=name),
           C("component.metadata.set", component=name, part_number=spec, bom_type="purchased", description=desc),
           C("material.assign", bodies=[name], material="SCM435")]
stages['5_bolts'] = s5
s5b = [C("occurrence.reparent", occurrence="%s:1" % b[1], parent="U4S_CYL") for b in BOLTS]
# 엘보: STEP 로컬 = 나사 끝 -y(3), 몸 +y 18.7, 출구 +x 14.5. 나사 -y -> 월드 +Z(포트 안), 출구 +x -> 월드 +Y(로드 쪽)·+X(머리 쪽)
KQ = [("KQ2L06-M5A_M02S_ROD", [[0, 0, -1], [1, 0, 0], [0, -1, 0]], (PORT_ROD[0], PORT_ROD[1], 205),
       "SMC KQ2L06-M5A elbow M5-OD6, U4 press cylinder rod-side port (bottom face), outlet +Y = press line from valve A / IR1000 (RX-13)"),
      ("KQ2L06-M5A_M02S_HEAD", [[1, 0, 0], [0, 0, 1], [0, -1, 0]], (PORT_HEAD[0], PORT_HEAD[1], 205),
       "SMC KQ2L06-M5A elbow M5-OD6, U4 press cylinder head-side port (bottom face), outlet +X = lift line from valve B (RX-13)")]
for (name, R, t, desc) in KQ:
    s5b += [C("occurrence.move", occurrence=name + ":1", space="world", to_matrix=flat(R, t)),
            C("component.metadata.set", component=name, part_number="KQ2L06-M5A", bom_type="purchased", description=desc)]
stages['5b_place'] = s5b

# ---- 6. 관: 고정 구간은 세움 Z 340 아래를 자르고, U4 구간을 U4_WHEEL_N 아래 새 컴포넌트로
def tube(name, segs, parent, desc):
    sk = "SK_" + name
    r4 = lambda v: [round(x, 4) for x in v]
    c = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    L = 0.0
    for s in segs:
        if s[0] == "l":
            c.append(C("sketch.line3d", points=[r4(s[1]), r4(s[2])])); L += math.dist(s[1], s[2])
        else:   # ("a", start, center, end) 90도 호
            st, ce, en = s[1], s[2], s[3]
            R = math.dist(st, ce)
            m = [(st[i] + en[i]) / 2 - ce[i] for i in range(3)]
            ml = math.sqrt(sum(x * x for x in m))
            mid = [ce[i] + m[i] / ml * R for i in range(3)]
            c.append(C("sketch.arc3d", start=r4(st), through=r4(mid), end=r4(en))); L += R * math.pi / 2
    c += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(segs))], diameter=6.0, operation="new", body_name=name),
          C("material.assign", bodies=[name], material="Default"),
          C("component.create", name=name, parent=parent, activate=False),
          C("component.move_bodies", bodies=[name], component=name),
          C("component.metadata.set", component=name, part_number="TU0604", bom_type="purchased", description=desc)]
    return c, round(L, 1)
ZJ = 340.0
XS = -161.006
ROD_END = (PORT_ROD[0], PORT_ROD[1] + 14.5, 191.5)      # 엘보 출구 끝(포트 축에서 14.5 — STEP 실측), 관 축은 포트 면에서 13.5
HEAD_END = (PORT_HEAD[0] + 14.5, PORT_HEAD[1], 191.5)
A_segs = [("l", [XS, 79, ZJ], [XS, 79, 207.5]),
          ("a", [XS, 79, 207.5], [XS - 16, 79, 207.5], [XS - 16, 79, 191.5]),
          ("l", [XS - 16, 79, 191.5], [-225, 79, 191.5]),
          ("a", [-225, 79, 191.5], [-225, 64, 191.5], [-240, 64, 191.5]),
          ("l", [-240, 64, 191.5], list(ROD_END))]
B_segs = [("l", [XS, 70, ZJ], [XS, 70, 239]),
          ("a", [XS, 70, 239], [XS - 16, 70, 239], [XS - 16, 70, 223]),
          ("l", [XS - 16, 70, 223], [-192.5, 70, 223]),
          ("a", [-192.5, 70, 223], [-192.5, 55, 223], [-207.5, 55, 223]),
          ("l", [-207.5, 55, 223], [-207.5, -15.1, 223]),
          ("a", [-207.5, -15.1, 223], [-207.5, -15.1, 208], [-207.5, -30.1, 208]),
          ("l", [-207.5, -30.1, 208], [-207.5, -30.1, 206.5]),
          ("a", [-207.5, -30.1, 206.5], [-222.5, -30.1, 206.5], [-222.5, -30.1, 191.5]),
          ("l", [-222.5, -30.1, 191.5], list(HEAD_END))]
cA, LA = tube("TU0604_M08P_U4_A2_U4", A_segs, "U4_WHEEL_N",
              "SMC TU0604 OD6, U4 press line (valve A / IR1000 -> rod-side port), U4 segment (moves with J_U4_X); flexible bridge to U8 segment at riser Z 340 (RX-13)")
cB, LB = tube("TU0604_M08P_U4_B_U4", B_segs, "U4_WHEEL_N",
              "SMC TU0604 OD6, U4 lift line (valve B -> head-side port), U4 segment (moves with J_U4_X); flexible bridge to U8 segment at riser Z 340 (RX-13)")
s6 = [C("component.activate", component="root"),
      box(None, -216, 55, 185, -155, 222, ZJ, op="cut", targets=["TU0604_M08P_U4_A2", "TU0604_M08P_U4_B"]),
      C("component.metadata.set", component="TU0604_M08P_U4_A2", part_number="TU0604", bom_type="purchased",
        description="SMC TU0604 OD6, U4 press line, U8 fixed segment down to riser (-161,79) Z 340; continues as TU0604_M08P_U4_A2_U4 (RX-13)"),
      C("component.metadata.set", component="TU0604_M08P_U4_B", part_number="TU0604", bom_type="purchased",
        description="SMC TU0604 OD6, U4 lift line, U8 fixed segment down to riser (-161,70) Z 340; continues as TU0604_M08P_U4_B_U4 (RX-13)"),
      C("component.activate", component="U4_WHEEL_N")] + cA + cB + [C("component.activate", component="root")]
stages['6_tubes'] = s6

# ---- 7. 조인트: 리지드 묶음 + 로드 슬라이더(축 +Y, 0 = 후퇴 끝 = 누름 쪽, 25 = 나옴 끝 = 들림) + 그네 따라가기 링크
RIG = ["U4_WHEEL_N:1"] + ["%s:1" % b[1] for b in BOLTS] + [k[0] + ":1" for k in KQ] + ["TU0604_M08P_U4_A2_U4:1", "TU0604_M08P_U4_B_U4:1"]
stages['7_joints'] = [
    C("joint.rigid_group", occurrences=RIG),
    C("joint.create", type="slider", name="J_U4S_ROD", flip=True, limits=[[0, 25]], values=[25],
      a={"occurrence": "U4S_CYL:1", "point": [XR, 21.4, ZR], "z": [0, 1, 0]},
      b={"occurrence": "U4S_ROD:1", "point": [XR, 21.4 + 25, ZR], "z": [0, 1, 0]}),
    # 핀 Y = 112.99 + 1.4535*theta (M02R 링크와 같은 핀 자리), 로드 값 = 핀 Y - 106.9
    C("joint.motion_link", a="J_U4_PRESS", b="J_U4S_ROD", ratio=1.4535, offset=6.09)]
stages['8_final'] = [C("motion.play", study="REST", step=0, quiet=True),
                     C("browser.visibility", visible=False, folder="joints"),
                     C("browser.visibility", visible=False, folder="sketches")]

for k, v in stages.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"tube_len": {"A2_U4": LA, "B_U4": LB}, "bolts": [[b[0], b[1], list(b[3])] for b in BOLTS],
           "rod_end": ROD_END, "head_end": HEAD_END}, open(os.path.join(OUT, 'gen_meta.json'), 'w'), indent=1)
print({k: len(v) for k, v in stages.items()}, LA, LB)
