# M02R 3회차(C-41) 모델링 명령 생성기: 보 고정 사각 실린더 + 축 X 그네 브래킷
# 좌표: J_U4_PRESS 0(θ0, 봉제 두께 10) 측정 좌표계. 출력 tools/out/mech_M02R/model5/stage_*.json
import json, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mech_M02R", "model5")
STEP = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step"
CYL = "STEP대기_CDQ2YA20-25DMZ"     # 임시 형번(저마찰 CQ2Y 계열, D-188)
PIV = (120.0, 140.0)               # 피벗 (Y, Z), 축 X
ZR = 223.0                         # 로드 축선 Z
XR = -240.0                        # 로드 축선 X
PIN0 = 112.99                      # θ0 핀 Y
PIN_RET = 131.93                   # 후퇴 끝 핀 Y
S0 = PIN_RET - PIN0                # θ0 행정 18.94
UT = ((PIN0 - PIV[0]), (ZR - PIV[1]))
_r = math.hypot(*UT); U = (UT[0] / _r, UT[1] / _r)   # 텅 방향(Y,Z)

def C(cmd, **p): return {"command": cmd, "params": p}
def box(name, corner, size, op="new", targets=None):
    p = {"length": size[0], "width": size[1], "height": size[2], "corner": list(corner), "operation": op}
    if op == "new": p["body_name"] = name
    else: p["targets"] = [name]
    return C("solid.box", **p)
def cyl(name, base, axis, r, h, op="new"):
    p = {"radius": r, "height": h, "base": list(base), "axis": list(axis), "operation": op}
    if op == "new": p["body_name"] = name
    else: p["targets"] = [name]
    return C("solid.cylinder", **p)
def r6(v): return round(v, 4)

R_UP = [[0, 0, -1], [0, 1, 0], [1, 0, 0]]     # 볼트 로컬 +x → 세계 +Z (밑에서 위로)
R_MY = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]     # 로컬 +x → 세계 −Y
def mat(R, t): return [R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2]]
def bolt(spec, name, R, t, desc):
    return [C("file.insert_step", path=f"{STEP}/{spec}/{spec}.stp", name=name, matrix=mat(R, t)),
            C("body.rename", body="Cut-Extrude1", name=name),
            C("component.metadata.set", component=name, part_number=spec, bom_type="purchased", description=desc),
            C("material.assign", bodies=[name], material="SCM435")]

stages = {}

# 1. 옛 조인트·바디 지우기 (빠른 것)
stages["1_remove"] = [
    C("joint.delete", joint="J_U4_ROD_PIN"), C("joint.delete", joint="J_U4_CYL_ROD"), C("joint.delete", joint="J_U4_CYL_PIN"),
    C("solid.remove", bodies=["P_M02R_CYLBRKT", "P_M02R_CRANK", "P_M02R_CRANK_PIN", "P_M02R_CRANK_WASHER",
                              "P_M02_CLEVIS_PIN", "P_M02_CLEVIS_WASHER", "P_M02_PIVOT_PIN", "P_M02_PIVOT_SPACER", "P_M02_PIVOT_WASHER"]),
]
# 2. 옛 occurrence 지우기 (느림, execute 따로)
stages["2_deloccs"] = [C("selection.delete", occurrences=[
    "CDM2C20-25Z:1", "I-020B_M02:1", "CB5-16_M02R_1:1", "CB5-16_M02R_2:1", "CB5-16_M02R_3:1", "CB5-16_M02R_4:1",
    "CB5-20_M02R_1:1", "CB5-20_M02R_2:1", "CB4-12_M02R_CLV:1", "CB4-12_M02R_CRK:1",
    "CB4-12_M02_PIV:1", "CB4-12_M02_PIV:2", "CB5-12_M02_PIV:1", "CB5-16_M02_10:1"])]

# 3. 피벗 조인트 고침 + 기존 부품 형상 정리(메움·탭)
p3 = [C("joint.edit", joint="J_U4_PRESS",
        a={"occurrence": "U4_WHEEL_N:1", "point": [XR, PIV[0], PIV[1]], "z": [-1, 0, 0]},
        b={"occurrence": "U4_PRESS:1", "point": [XR, PIV[0], PIV[1]], "z": [-1, 0, 0]}, flip=True),
      C("joint.limits", joint="J_U4_PRESS", min=-4.11, max=13.006)]
# base 세운 다리 제거, CYLBRKT 구멍 메움
p3.append(box("P_M02_BASE", (-326, -61, 49), (47, 9, 193), op="cut"))
for (x, y, r) in [(-175, 20, 2.8), (-175, -20, 2.8), (-149, 20, 2.8), (-149, -20, 2.8), (-176, 24, 2.3), (-148, -24, 2.3)]:
    p3.append(cyl("P_M02_BASE", (x, y, 242), (0, 0, 1), r, 8, op="join"))
# 옛 피벗 부시 구멍(암 옆판) · ARM_TIE 크랭크 탭 메움
p3.append(cyl("P_M02_ARM_SIDE_N", (-300, -37, 70), (0, 1, 0), 9.05, 6, op="join"))
p3.append(cyl("P_M02_ARM_SIDE_P", (-300, 31, 70), (0, 1, 0), 9.05, 6, op="join"))
for x in (-270, -260):
    p3.append(cyl("P_M02_ARM_TIE", (x, 0, 109), (0, 0, 1), 2.15, 12, op="join"))
# 새 탭 구멍: base(피벗 브래킷 4, 스프링 탭 4), 보(실린더 브래킷 2), 암 옆판 P(CB5-16 2)
BASE_TAPS = [(-318, 108), (-306, 108), (-168, 110), (-168, 126), (-302, 50), (-288, 50), (-192, 50), (-178, 50)]
for (x, y) in BASE_TAPS:
    p3.append(cyl("P_M02_BASE", (x, y, 241.9), (0, 0, 1), 2.1, 8.2, op="cut"))
for x in (-255, -225):
    p3.append(cyl("P_M07_BEAM", (x, 248, 249.9), (0, 0, 1), 2.1, 8.1, op="cut"))
for (x, z) in ((-300, 100), (-166, 120)):   # 실측 옆판 윤곽(Z ≤ 107, 귀 X −175~−145 Z ≤ 132)에 맞춤
    p3.append(cyl("P_M02_ARM_SIDE_P", (x, 37.1, z), (0, -1, 0), 2.1, 6.2, op="cut"))
stages["3_joint_fill"] = p3

# 4. 그네 P_M02S_SWING (A5052 밀링, U4_PRESS)
SW = "P_M02S_SWING"
p4 = [C("sketch.create", plane={"origin": [-320, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02S_SWING_L"),
      C("sketch.line", points=[[37, 92], [45, 92], [45, 141], [120, 141], [120, 153], [37, 153]], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_M02S_SWING_L", distance=159, operation="new", body_name=SW, name="EX_M02S_SWING_L"),
      cyl(SW, (-322, PIV[0], PIV[1]), (1, 0, 0), 13, 162, op="join")]
# 텅 (YZ 판 t10, X −245~−235): 피벗 → r 83 슬롯 모양 폭 20
p1 = [PIV[0] + U[0] * 83.0, PIV[1] + U[1] * 83.0]
p4 += [C("sketch.create", plane={"origin": [-245, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02S_TONGUE"),
       C("sketch.slot.center_to_center", p0=[PIV[0], PIV[1]], p1=[r6(p1[0]), r6(p1[1])], width=20),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_M02S_TONGUE", distance=10, operation="join", targets=[SW], name="EX_M02S_TONGUE")]
# 스프링 귀 2
for s in (-295, -185):
    p4.append(box(SW, (s - 2.5, 44, 152), (5, 12, 8), op="join"))
# 빼기: 축 구멍 Ø13, MPFZ 자리 r9.02 깊이 7, 장공, 귀 구멍, 볼트 구멍
p4.append(cyl(SW, (-323, PIV[0], PIV[1]), (1, 0, 0), 6.5, 164, op="cut"))
p4.append(cyl(SW, (-322.01, PIV[0], PIV[1]), (1, 0, 0), 9.02, 7.01, op="cut"))
p4.append(cyl(SW, (-167.0, PIV[0], PIV[1]), (1, 0, 0), 9.02, 7.01, op="cut"))
q0 = [PIV[0] + U[0] * 82.8, PIV[1] + U[1] * 82.8]; q1 = [PIV[0] + U[0] * 84.1, PIV[1] + U[1] * 84.1]
p4 += [C("sketch.create", plane={"origin": [-245.1, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02S_SLOT"),
       C("sketch.slot.center_to_center", p0=[r6(q0[0]), r6(q0[1])], p1=[r6(q1[0]), r6(q1[1])], width=8.2),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_M02S_SLOT", distance=10.2, operation="cut", targets=[SW], name="EX_M02S_SLOT")]
for s in (-295, -185):
    p4.append(cyl(SW, (s - 3, 50, 156), (1, 0, 0), 2.25, 6, op="cut"))
for (x, z) in ((-265, 111), (-300, 100), (-166, 120)):
    p4.append(cyl(SW, (x, 45.1, z), (0, -1, 0), 2.75, 8.2, op="cut"))
p4 += [C("material.assign", bodies=[SW], material="A5052"), C("component.move_bodies", bodies=[SW], component="U4_PRESS")]
# MPFZ 두 개를 새 보스 양 끝으로 (Rz −90°)
RZ = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]
p4.append(C("joint.delete", joint=95401)); p4.append(C("joint.delete", joint=95402))   # MPFZ ↔ U4_PRESS 리지드(v2.10.2 id)
p4.append(C("occurrence.move", occurrence="MPFZ12-10_M02_N:1", space="world", matrix=mat(RZ, (-285, -180, 70))))
p4.append(C("occurrence.move", occurrence="MPFZ12-10_M02_P:1", space="world", matrix=mat(RZ, (-197, -180, 70))))
p4.append(C("joint.rigid_group", occurrences=["U4_PRESS:1", "MPFZ12-10_M02_N:1", "MPFZ12-10_M02_P:1"]))
stages["4_swing"] = p4

# 5. 고정쪽: 피벗 브래킷 A·B, 축, 칼라, 스프링 탭, 스프링 끝 조각
p5 = []
def lbrkt(name, xs_plate, xs_flange):   # SUS304 t4 L, Y 103~133
    xa, xb = xs_plate; fa, fb = xs_flange
    if fa < xa:   # 날개가 −X 쪽 (B)
        pts = [[xa, 128], [xb, 128], [xb, 242], [fa, 242], [fa, 238], [xa, 238]]
    else:         # 날개가 +X 쪽 (A)
        pts = [[xa, 128], [xb, 128], [xb, 238], [fb, 238], [fb, 242], [xa, 242]]
    sk = "SK_" + name
    return [C("sketch.create", plane={"origin": [0, 133, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name=sk),
            C("sketch.line", points=pts, closed=True), C("sketch.finish"),
            C("solid.extrude", sketch=sk, distance=30, operation="new", body_name=name, name="EX_" + name)]
p5 += lbrkt("P_M02S_PIVOT_BRKT_A", (-330, -326), (-330, -300))
p5 += lbrkt("P_M02S_PIVOT_BRKT_B", (-156, -152), (-180, -156))
p5.append(cyl("P_M02S_PIVOT_BRKT_A", (-331, PIV[0], PIV[1]), (1, 0, 0), 6.05, 6, op="cut"))
p5.append(cyl("P_M02S_PIVOT_BRKT_B", (-157, PIV[0], PIV[1]), (1, 0, 0), 6.05, 6, op="cut"))
for (x, y) in ((-318, 108), (-306, 108)):
    p5.append(cyl("P_M02S_PIVOT_BRKT_A", (x, y, 237.9), (0, 0, 1), 2.75, 4.2, op="cut"))
for (x, y) in ((-168, 110), (-168, 126)):
    p5.append(cyl("P_M02S_PIVOT_BRKT_B", (x, y, 237.9), (0, 0, 1), 2.75, 4.2, op="cut"))
p5 += [cyl("STEP대기_PSFJ12-200", (-342, PIV[0], PIV[1]), (1, 0, 0), 6, 200),
       cyl("STEP대기_PSCS12-10_1", (-340, PIV[0], PIV[1]), (1, 0, 0), 12, 10),
       cyl("STEP대기_PSCS12-10_1", (-341, PIV[0], PIV[1]), (1, 0, 0), 6.0, 12, op="cut"),
       cyl("STEP대기_PSCS12-10_2", (-152, PIV[0], PIV[1]), (1, 0, 0), 12, 10),
       cyl("STEP대기_PSCS12-10_2", (-153, PIV[0], PIV[1]), (1, 0, 0), 6.0, 12, op="cut")]
for i, s in enumerate((-295, -185), 1):
    tn = f"P_M02S_SPRING_TAB_{i}"
    p5 += [box(tn, (s - 12, 40, 238), (24, 20, 4)), box(tn, (s - 2, 44, 228), (4, 12, 11), op="join"),
           cyl(tn, (s - 3, 50, 234), (1, 0, 0), 2.25, 6, op="cut"),
           cyl(tn, (s - 7, 50, 237.9), (0, 0, 1), 2.75, 4.2, op="cut"), cyl(tn, (s + 7, 50, 237.9), (0, 0, 1), 2.75, 4.2, op="cut")]
    top = f"STEP대기_AUT12-45_{i}_TOP"; bot = f"STEP대기_AUT12-45_{i}_BOT"
    p5 += [cyl(top, (s, 50, 204), (0, 0, 1), 6, 23), cyl(top, (s - 5, 50, 226), (0, 0, 1), 1, 8, op="join"),
           cyl(top, (s - 5, 50, 234), (1, 0, 0), 1, 10, op="join"),
           cyl(bot, (s, 50, 161), (0, 0, 1), 6, 25), cyl(bot, (s - 5, 50, 156), (0, 0, 1), 1, 6, op="join"),
           cyl(bot, (s - 5, 50, 156), (1, 0, 0), 1, 10, op="join")]
fixed = ["P_M02S_PIVOT_BRKT_A", "P_M02S_PIVOT_BRKT_B", "P_M02S_SPRING_TAB_1", "P_M02S_SPRING_TAB_2"]
p5.append(C("material.assign", bodies=fixed, material="SUS304"))
p5.append(C("material.assign", bodies=["STEP대기_PSFJ12-200"], material="S45C"))
p5.append(C("material.assign", bodies=["STEP대기_PSCS12-10_1", "STEP대기_PSCS12-10_2"], material="S45C"))
sp = [f"STEP대기_AUT12-45_{i}_{e}" for i in (1, 2) for e in ("TOP", "BOT")]
p5.append(C("material.assign", bodies=sp, material="SUS304"))
p5.append(C("component.move_bodies", bodies=fixed + ["STEP대기_PSFJ12-200", "STEP대기_PSCS12-10_1", "STEP대기_PSCS12-10_2",
                                                     "STEP대기_AUT12-45_1_TOP", "STEP대기_AUT12-45_2_TOP"], component="U4_WHEEL_N"))
p5.append(C("component.move_bodies", bodies=["STEP대기_AUT12-45_1_BOT", "STEP대기_AUT12-45_2_BOT"], component="U4_PRESS"))
stages["5_fixed"] = p5

# 6. 실린더 묶음: U4S_CYL(실린더 임시 + CYL_BRKT), U4S_ROD(로드 + 너클 + 핀) — 로드는 θ0 자리(핀 Y 112.99)로 그림
p6 = []
BR = "P_M02S_CYL_BRKT"
p6 += [C("sketch.create", plane={"origin": [-265, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02S_CYL_BRKT"),
       C("sketch.line", points=[[222.43, 205], [228.43, 205], [228.43, 244], [262, 244], [262, 250], [222.43, 250]], closed=True),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_M02S_CYL_BRKT", distance=50, operation="new", body_name=BR, name="EX_M02S_CYL_BRKT")]
HEADB = [(XR - 12.75, ZR - 12.75), (XR + 12.75, ZR - 12.75), (XR - 12.75, ZR + 12.75), (XR + 12.75, ZR + 12.75)]
for (x, z) in HEADB:
    p6.append(cyl(BR, (x, 228.53, z), (0, -1, 0), 2.75, 6.2, op="cut"))
for x in (-255, -225):
    p6.append(cyl(BR, (x, 248, 243.9), (0, 0, 1), 2.75, 6.2, op="cut"))
p6 += [box(CYL, (-258, 177.93, 205), (36, 44.5, 36)),
       cyl(CYL, (XR, 177.83, ZR), (0, 1, 0), 5.25, 30.1, op="cut")]
for (x, z) in HEADB:
    p6.append(cyl(CYL, (x, 222.53, z), (0, -1, 0), 2.1, 8.1, op="cut"))
for y in (186, 214):
    p6.append(cyl(CYL, (-221.9, y, ZR), (-1, 0, 0), 2.55, 4.1, op="cut"))
p6 += [C("material.assign", bodies=[BR], material="SUS304"), C("material.assign", bodies=[CYL], material="Aluminum"),
       C("component.create", name="U4S_CYL", parent="root", activate=False),
       C("component.move_bodies", bodies=[CYL, BR], component="U4S_CYL"),
       C("component.metadata.set", component="U4S_CYL", part_number="CDQ2YA20-25DMZ", bom_type="purchased",
         description="STEP pending: SMC smooth (low-friction) compact cylinder bore 20 stroke 25, tapped both ends, rod male thread, temporary part number (D-188); body 36x36x44.5 placeholder + P_M02S_CYL_BRKT SUS304 t6 L")]
pin = PIN0
ROD = "STEP대기_CDQ2YA20-25DMZ_ROD"; KN = "STEP대기_Y-020B"; KP = "STEP대기_Y-020B_PIN"
p6 += [cyl(ROD, (XR, pin + 26, ZR), (0, 1, 0), 5, 48),
       C("sketch.create", plane={"origin": [0, 0, 213], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_M02S_KNUCKLE"),
       C("sketch.line", points=[[-251, pin - 10], [-245.2, pin - 10], [-245.2, pin + 14], [-234.8, pin + 14], [-234.8, pin - 10],
                                [-229, pin - 10], [-229, pin + 26], [-251, pin + 26]], closed=True),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_M02S_KNUCKLE", distance=20, operation="new", body_name=KN, name="EX_M02S_KNUCKLE"),
       cyl(KN, (-252, pin, ZR), (1, 0, 0), 4.05, 24, op="cut"),
       cyl(KP, (-253, pin, ZR), (1, 0, 0), 6, 2),
       cyl(KP, (-251, pin, ZR), (1, 0, 0), 4, 23.5, op="join"),
       C("material.assign", bodies=[ROD, KP], material="S45C"), C("material.assign", bodies=[KN], material="Steel"),
       C("component.create", name="U4S_ROD", parent="root", activate=False),
       C("component.move_bodies", bodies=[ROD, KN, KP], component="U4S_ROD"),
       C("component.metadata.set", component="U4S_ROD", part_number="CDQ2YA20-25DMZ rod + Y-020B", bom_type="purchased",
         description="STEP pending: cylinder rod D10 + SMC Y-020B single knuckle (pin D8), placeholder")]
stages["6_cyl"] = p6

# 7. 볼트·피팅 넣기
p7 = []
B = []
for i, x in enumerate((-255, -225), 1):
    B.append(("CB5-12", f"CB5-12_M02S_BEAM_{i}", R_UP, (x, 248, 244), "U4S_CYL", "CYL_BRKT to beam bottom (M5 tapped)"))
for i, (x, z) in enumerate(HEADB, 1):
    B.append(("CB5-12", f"CB5-12_M02S_CYL_{i}", R_MY, (x, 228.43, z), "U4S_CYL", "cylinder head to CYL_BRKT"))
for i, (x, y) in enumerate(BASE_TAPS, 1):
    B.append(("CB5-12", f"CB5-12_M02S_BASE_{i}", R_UP, (x, y, 238), "U4_WHEEL_N", "pivot bracket / spring tab to base top plate (M5 tapped)"))
B.append(("CB5-20", "CB5-20_M02S_1", R_MY, (-265, 45, 111), "U4_PRESS", "swing + arm side P to ARM_TIE (was CB5-16_M02_10)"))
for i, (x, z) in enumerate(((-300, 100), (-166, 120)), 1):
    B.append(("CB5-16", f"CB5-16_M02S_{i}", R_MY, (x, 45, z), "U4_PRESS", "swing to arm side P (M5 tapped through)"))
for (spec, name, R, t, par, desc) in B:
    p7 += bolt(spec, name, R, t, desc)
KQ = [("KQ2L06-M5A_M02S_ROD", [[0, 1, 0], [-1, 0, 0], [0, 0, 1]], (-222, 186, ZR)),
      ("KQ2L06-M5A_M02S_HEAD", [[0, 1, 0], [0, 0, -1], [-1, 0, 0]], (-222, 214, ZR))]
for (name, R, t) in KQ:
    p7 += [C("file.insert_step", path=f"{STEP}/KQ2L06-M5A/KQ2L06-M5A.stp", name=name, matrix=mat(R, t)),
           C("body.rename", body="KQ2L06-M5A", name=name),
           C("component.metadata.set", component=name, part_number="KQ2L06-M5A", bom_type="purchased",
             description="SMC KQ2L06-M5A elbow M5-OD6 on U4 cylinder port (M02R swing)"),
           C("material.assign", bodies=[name], material="Default")]
stages["7_parts"] = p7
# 8. 다시 넣기·조인트
p8 = []
for (spec, name, R, t, par, desc) in B:
    p8.append(C("occurrence.reparent", occurrence=f"{name}:1", parent=par))
for (name, R, t) in KQ:
    p8.append(C("occurrence.reparent", occurrence=f"{name}:1", parent="U4S_CYL"))
p8.append(C("joint.rigid_group", occurrences=["U4_WHEEL_N:1", "U4S_CYL:1"] + [f"{b[1]}:1" for b in B if b[4] in ("U4_WHEEL_N", "U4S_CYL")] + [f"{k[0]}:1" for k in KQ]))
p8.append(C("joint.rigid_group", occurrences=["U4_PRESS:1"] + [f"{b[1]}:1" for b in B if b[4] == "U4_PRESS"]))
p8.append(C("joint.create", type="slider", name="J_U4S_ROD", flip=True, limits=[[0, 25]], values=[S0],
            a={"occurrence": "U4S_CYL:1", "point": [XR, 177.93, ZR], "z": [0, -1, 0]},
            b={"occurrence": "U4S_ROD:1", "point": [XR, 177.93 - S0, ZR], "z": [0, -1, 0]}))
fr = {"origin": [XR, PIN0, ZR], "z": [1, 0, 0], "x": [0, r6(U[0]), r6(U[1])]}
p8.append(C("joint.create", type="pin_slot", name="J_U4S_SLOT", flip=True,
            a={"occurrence": "U4_PRESS:1", "frame": fr}, b={"occurrence": "U4S_ROD:1", "frame": fr}))
stages["8_joints"] = p8

# 9. 관 U4_A2·U4_B 끝 다시
A2 = [("l", [[727.94, 95.0, 465.7], [727.94, 95.0, 456.0]]),
      ("a", [727.94, 95.0, 456.0], [723.8111, 97.2167, 444.6863], [713.8431, 102.5681, 440.0]),
      ("l", [[713.8431, 102.5681, 440.0], [706.6465, 106.4317, 440.0]]),
      ("a", [706.6465, 106.4317, 440.0], [699.7722, 109.0943, 440.0], [692.4562, 110.0, 440.0]),
      ("l", [[692.4562, 110.0, 440.0], [-144.9, 110.0, 440.0]]),
      ("a", [-144.9, 110.0, 440.0], [-166.1132, 109.3156, 431.2399], [-174.9, 107.6634, 410.0911]),
      ("l", [[-174.9, 107.6634, 410.0911], [-174.9, 100.7025, 320.992]]),
      ("a", [-174.9, 100.7025, 320.992], [-173.6865, 99.6554, 312.41], [-170.1486, 97.9481, 304.6133]),
      ("l", [[-170.1486, 97.9481, 304.6133], [-165.9916, 96.153, 298.1508]]),
      ("a", [-165.9916, 96.153, 298.1508], [-162.282, 94.551, 289.9616], [-161.006, 94.0, 280.9361]),
      ("l", [[-161.006, 94.0, 280.9361], [-161.006, 94.0, 208.5]]),
      ("a", [-161.006, 94.0, 208.5], [-165.692, 94.0, 197.186], [-177.006, 94.0, 192.5]),
      ("l", [[-177.006, 94.0, 192.5], [-192.5, 94.0, 192.5]]),
      ("a", [-192.5, 94.0, 192.5], [-203.814, 98.686, 192.5], [-208.5, 110.0, 192.5]),
      ("l", [[-208.5, 110.0, 192.5], [-208.5, 198.0, 192.5]]),
      ("a", [-208.5, 198.0, 192.5], [-208.5, 209.314, 197.186], [-208.5, 214.0, 208.5])]
UB = [("l", [[1049.75, 53.0, 370.6], [1049.75, 53.0, 400.0]]),
      ("a", [1049.75, 53.0, 400.0], [1043.9721, 59.6199, 421.2132], [1030.0229, 75.6018, 430.0]),
      ("l", [[1030.0229, 75.6018, 430.0], [1008.9663, 99.7271, 430.0]]),
      ("a", [1008.9663, 99.7271, 430.0], [998.7779, 107.3113, 430.0], [986.3645, 110.0, 430.0]),
      ("l", [[986.3645, 110.0, 430.0], [-120.9114, 110.0, 430.0]]),
      ("a", [-120.9114, 110.0, 430.0], [-124.9626, 109.7252, 430.0], [-128.9395, 108.9059, 430.0]),
      ("l", [[-128.9395, 108.9059, 430.0], [-132.1001, 108.0281, 430.0]]),
      ("a", [-132.1001, 108.0281, 430.0], [-152.5397, 102.3514, 421.2132], [-161.006, 100.0, 400.0]),
      ("l", [[-161.006, 100.0, 400.0], [-161.006, 100.0, 328.6274]]),
      ("a", [-161.006, 100.0, 328.6274], [-161.006, 96.2393, 314.0844], [-161.006, 85.9, 303.1875]),
      ("l", [[-161.006, 85.9, 303.1875], [-161.006, 84.1, 302.0625]]),
      ("a", [-161.006, 84.1, 302.0625], [-161.006, 73.7607, 291.1656], [-161.006, 70.0, 276.6226]),
      ("l", [[-161.006, 70.0, 276.6226], [-161.006, 70.0, 239.0]]),
      ("a", [-161.006, 70.0, 239.0], [-165.692, 70.0, 227.686], [-177.006, 70.0, 223.0]),
      ("l", [[-177.006, 70.0, 223.0], [-192.5, 70.0, 223.0]]),
      ("a", [-192.5, 70.0, 223.0], [-203.814, 74.686, 223.0], [-208.5, 86.0, 223.0]),
      ("l", [[-208.5, 86.0, 223.0], [-208.5, 171.5, 223.0]])]
p9 = []
for (comp, segs, minr) in (("TU0604_M08P_U4_A2", A2, 16), ("TU0604_M08P_U4_B", UB, 16)):
    sk = f"SK_{comp}_M02S"
    p9 += [C("solid.remove", bodies=[comp]), C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    for s in segs:
        if s[0] == "l": p9.append(C("sketch.line3d", points=s[1]))
        else: p9.append(C("sketch.arc3d", start=s[1], through=s[2], end=s[3]))
    p9 += [C("sketch.finish"),
           C("solid.pipe", path_sketch=sk, path=[f"w{i}" for i in range(1, len(segs) + 1)], diameter=6.0, operation="new", body_name=comp),
           C("material.assign", bodies=[comp], material="Default"),
           C("component.move_bodies", bodies=[comp], component=comp),
           C("component.metadata.set", component=comp, part_number="TU0604", bom_type="purchased",
             description=f"SMC TU0604 polyurethane tube OD6, cut to length (M02R swing route to KQ2L06-M5A, bends R>={minr})")]
stages["9_tubes"] = p9

os.makedirs(OUT, exist_ok=True)
for k, v in stages.items():
    json.dump(v, open(os.path.join(OUT, f"stage_{k}.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"U": U, "S0": S0, "bolts": [[b[0], b[1], b[3], b[4]] for b in B]}, open(os.path.join(OUT, "gen_meta.json"), "w", encoding="utf-8"), ensure_ascii=False)
print({k: len(v) for k, v in stages.items()}, U, S0)
