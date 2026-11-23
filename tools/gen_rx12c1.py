# RX-12-C1 접이 매트 받침(U2_FLAP) 명령 생성기 — mech_RX-12-C1_design.md·_design1.md·_design2.md 7절
# 출력: tools/out/mech_RX-12-C1/model/stage_*.json (MCP batch path 로 보냄)
import json, math, os, sys

OUT = os.path.join(os.path.dirname(__file__), 'out', 'mech_RX-12-C1', 'model')
os.makedirs(OUT, exist_ok=True)
ST = {}


def stage(name):
    ST[name] = []
    return ST[name]


def box(L, name, body, x0, x1, y0, y1, z0, z1, op='new', targets=None):
    p = {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4),
         "corner": [x0, y0, z0], "operation": op, "name": name}
    if op == 'new':
        p["body_name"] = body
    if targets:
        p["targets"] = targets
    L.append({"command": "solid.box", "params": p})


def cyl(L, name, r, base, axis, h, op='cut', targets=None, body=None):
    p = {"radius": r, "height": round(h, 4), "base": [round(v, 4) for v in base], "axis": axis,
         "operation": op, "name": name}
    if targets:
        p["targets"] = targets
    if body:
        p["body_name"] = body
    L.append({"command": "solid.cylinder", "params": p})


def act(L, comp):
    L.append({"command": "component.activate", "params": {"component": comp}})


def mat(L, bodies, m):
    L.append({"command": "material.assign", "params": {"bodies": bodies, "material": m}})


# ---------------- 좌표(설계안) ----------------
BALL_X = [450 + 100 * i for i in range(7)]
BALL_Y = [-350 - 100 * j for j in range(9)]
BAR_Y = {"L1": -400, "L2": -800, "L3": -1100}
BAR_BOLT_X = [500, 700, 900, 1050]
END_BOLT_Y = [-330, -560, -750, -940, -1180]
XN_X, XP_X = 414.0, 1092.5
ARM_BOLTS = [(1050, -1190), (1070, -1190)]
LATCH_Y = {"A": -412, "B": -1088}
HINGE_YC = {"A": -325, "B": -1155}  # B: 설계 -1175 -> -1155(기둥 B 홈 줄 Y -1155에 맞춤)
AX = (1105.0, -48.0)  # 경첩 축 (X, Z)
A_PT = (1073.0, -1235.0, -368.0)
P_PT = (1055.0, -1235.0, -48.0)
U = (P_PT[0] - A_PT[0], 0.0, P_PT[2] - A_PT[2])
L0 = math.hypot(U[0], U[2])
U = (U[0] / L0, 0.0, U[2] / L0)


def along(s):
    return [A_PT[0] + U[0] * s, A_PT[1], A_PT[2] + U[2] * s]


# ---------------- S00 준비 ----------------
L = stage('S00_setup')
L.append({"command": "edit.checkpoint", "params": {}})
L.append({"command": "document.metadata.set", "params": {"key": "description", "value": "RX-12-C1 mechanism: folding mat support flap U2_FLAP over +X/-Y pocket, hinge X1105, gas spring, latches A/B"}})

# ---------------- S01 컴포넌트 ----------------
L = stage('S01_components')
for nm, par in [("U2_FLAP_MOUNT", "U2_TABLE"), ("U2_FLAP", "U2_TABLE"), ("U2_FLAP_LATCH_A", "U2_FLAP"), ("U2_FLAP_LATCH_B", "U2_FLAP"),
                ("STEP대기_HHPSN8", "U2_FLAP"), ("STEP대기_HHPSN8_FIXLEAF", "U2_FLAP_MOUNT"),
                ("HFS8-4080-234_RX12C1", "U2_FLAP_MOUNT"), ("HFS8-4080-200_RX12C1", "U2_FLAP_MOUNT"),
                ("STEP대기_GASSPRING_F1120_S60_L325", "U2_FLAP_MOUNT"), ("STEP대기_GASSPRING_F1120_S60_L325_ROD", "STEP대기_GASSPRING_F1120_S60_L325")]:
    L.append({"command": "component.create", "params": {"name": nm, "parent": par, "activate": False}})

# ---------------- S02 판(U2_FLAP) ----------------
L = stage('S02_flap_plate')
act(L, "U2_FLAP")
PL = "P_RX12C1_FLAP_PL"
box(L, "RX12C1_FLAP_PL", PL, 405, 1100, -1200, -305, -13, -8)
k = 0
for x in BALL_X:
    for y in BALL_Y:
        k += 1
        cyl(L, f"RX12C1_FLAP_PL_BALLHOLE_{k}", 18, [x, y, -14], "Z", 7, targets=[PL])
holes = [(x, BAR_Y[b]) for b in ("L1", "L2", "L3") for x in BAR_BOLT_X] + [(XN_X, y) for y in END_BOLT_Y] + [(XP_X, y) for y in END_BOLT_Y] + ARM_BOLTS
for i, (x, y) in enumerate(holes, 1):
    cyl(L, f"RX12C1_FLAP_PL_BOLTHOLE_{i}", 2.75, [x, y, -14], "Z", 7, targets=[PL])
mat(L, [PL], "A5052")
act(L, 0)

# ---------------- S03 막대·팔 블록·귀판·혀(U2_FLAP) ----------------
L = stage('S03_flap_bars')
act(L, "U2_FLAP")
for b, yc in BAR_Y.items():
    nm = f"P_RX12C1_FLAP_BAR_{b}"
    box(L, f"RX12C1_BAR_{b}", nm, 423, 1085, yc - 5, yc + 5, -43, -13)
    for i, x in enumerate(BAR_BOLT_X, 1):
        cyl(L, f"RX12C1_BAR_{b}_TAP_{i}", 2.1, [x, yc, -23], "Z", 10.01, targets=[nm])
    mat(L, [nm], "A5052")
XN = "P_RX12C1_FLAP_BAR_XN"
box(L, "RX12C1_BAR_XN", XN, 405, 423, -1200, -305, -43, -13)
XP = "P_RX12C1_FLAP_BAR_XP"
box(L, "RX12C1_BAR_XP", XP, 1085, 1100, -1200, -305, -43, -13)
for nm, xc in ((XN, XN_X), (XP, XP_X)):
    for i, y in enumerate(END_BOLT_Y, 1):
        cyl(L, f"{nm[2:]}_TAP_{i}", 2.1, [xc, y, -23], "Z", 10.01, targets=[nm])
    for t, y in LATCH_Y.items():
        x0 = 404 if nm == XN else 1084
        cyl(L, f"{nm[2:]}_LATCHHOLE_{t}", 4.15, [x0, y, -28], "X", 20, targets=[nm])
# XP +X 면 탭: 경첩 잎(판 쪽) 2x2, 혀 2
for h, yc in HINGE_YC.items():
    for i, dy in enumerate((-10, 10), 1):
        cyl(L, f"RX12C1_BAR_XP_HINGETAP_{h}{i}", 2.1, [1090, yc + dy, -28], "X", 10.01, targets=[XP])
for i, y in enumerate((-1125, -1115), 1):
    cyl(L, f"RX12C1_BAR_XP_TONGUETAP_{i}", 2.1, [1090, y, -33], "X", 10.01, targets=[XP])
mat(L, [XN, XP], "A5052")
ARM = "P_RX12C1_GS_ARM_BLK"
box(L, "RX12C1_GS_ARM_BLK", ARM, 1040, 1080, -1224, -1180, -43, -13)
for i, (x, y) in enumerate(ARM_BOLTS, 1):
    cyl(L, f"RX12C1_GS_ARM_TOPTAP_{i}", 2.1, [x, y, -23], "Z", 10.01, targets=[ARM])
for i, x in enumerate((1048, 1072), 1):
    cyl(L, f"RX12C1_GS_ARM_SIDETAP_{i}", 2.1, [x, -1224, -28], "Y", 10, targets=[ARM])
mat(L, [ARM], "A5052")
LUG = "P_RX12C1_GS_LUG"
box(L, "RX12C1_GS_LUG", LUG, 1040, 1080, -1230, -1224, -63, -13)
for i, x in enumerate((1048, 1072), 1):
    cyl(L, f"RX12C1_GS_LUG_HOLE_{i}", 2.75, [x, -1231, -28], "Y", 8, targets=[LUG])
cyl(L, "RX12C1_GS_LUG_PINHOLE", 4.0, [P_PT[0], -1231, P_PT[2]], "Y", 8, targets=[LUG])
mat(L, [LUG], "SUS304")
PINP = "P_RX12C1_GS_PIN_P"
cyl(L, "RX12C1_GS_PIN_P", 4.0, [P_PT[0], -1240, P_PT[2]], "Y", 18, op='new', body=PINP)
mat(L, [PINP], "SCM435")
TG = "P_RX12C1_UPSTOP_TONGUE"
box(L, "RX12C1_UPSTOP_TONGUE", TG, 1100, 1135, -1132, -1108, -43, -13)
box(L, "RX12C1_UPSTOP_TONGUE_STEP", None, 1106, 1140, -1133, -1107, -50, -23, op='cut', targets=[TG])
for i, y in enumerate((-1125, -1115), 1):
    cyl(L, f"RX12C1_UPSTOP_TONGUE_HOLE_{i}", 2.75, [1099, y, -33], "X", 8, targets=[TG])
mat(L, [TG], "A5052")
act(L, 0)

# ---------------- S04 빗장 막대 ----------------
L = stage('S04_latch_rods')
for t, y in LATCH_Y.items():
    act(L, f"U2_FLAP_LATCH_{t}")
    nm = f"P_RX12C1_LATCH_ROD_{t}"
    cyl(L, f"RX12C1_LATCH_ROD_{t}", 4.0, [392, y, -28], "X", 717, op='new', body=nm)
    cyl(L, f"RX12C1_LATCH_ROD_{t}_HANDLE", 4.0, [1105, y, -68], "Z", 40, op='join', targets=[nm])
    L.append({"command": "solid.sphere", "params": {"radius": 8, "center": [1105, y, -68], "operation": "join", "targets": [nm], "name": f"RX12C1_LATCH_ROD_{t}_KNOB"}})
    mat(L, [nm], "SUS303")
act(L, 0)

# ---------------- S05 경첩 간이 형상 ----------------
L = stage('S05_hinge')
yc = HINGE_YC["A"]
act(L, "STEP대기_HHPSN8")
box(L, "RX12C1_HHPSN8_LEAF_FLAP", "STEP대기_HHPSN8_LEAF_FLAP", 1100, 1103, yc - 20, yc + 20, -43, -13)
cyl(L, "RX12C1_HHPSN8_BARREL", 5.0, [AX[0], yc - 20, AX[1]], "Y", 40, op='new', body="STEP대기_HHPSN8_BARREL")
for i, dy in enumerate((-10, 10), 1):
    cyl(L, f"RX12C1_HHPSN8_LEAF_FLAP_HOLE_{i}", 2.75, [1099, yc + dy, -28], "X", 5, targets=["STEP대기_HHPSN8_LEAF_FLAP"])
mat(L, ["STEP대기_HHPSN8_LEAF_FLAP", "STEP대기_HHPSN8_BARREL"], "SUS304")
act(L, "STEP대기_HHPSN8_FIXLEAF")
box(L, "RX12C1_HHPSN8_LEAF_FIX", "STEP대기_HHPSN8_LEAF_FIX", 1107, 1110, yc - 20, yc + 20, -88, -53)
for i, z in enumerate((-60, -80), 1):
    cyl(L, f"RX12C1_HHPSN8_LEAF_FIX_HOLE_{i}", 2.75, [1106, yc, z], "X", 5, targets=["STEP대기_HHPSN8_LEAF_FIX"])
mat(L, ["STEP대기_HHPSN8_LEAF_FIX"], "SUS304")
act(L, 0)

# ---------------- S06 고정 부품(U2_FLAP_MOUNT) ----------------
L = stage('S06_mount')
act(L, "U2_FLAP_MOUNT")
TAB = "P_RX12C1_TAB_PL"
box(L, "RX12C1_TAB_PL", TAB, 976, 1150, -345, -200, -16, -8)
box(L, "RX12C1_TAB_PL_NOTCH", None, 960, 1110, -350, -300, -20, -4, op='cut', targets=[TAB])
cyl(L, "RX12C1_TAB_PL_BALLHOLE", 18, [1050, -230, -17], "Z", 10, targets=[TAB])
for i, y in enumerate((-325, -285), 1):
    cyl(L, f"RX12C1_TAB_PL_BOLTHOLE_{i}", 4.5, [1130, y, -17], "Z", 10, targets=[TAB])
mat(L, [TAB], "A5052")
for t, y in LATCH_Y.items():
    nm = f"P_RX12C1_LATCH_BLK_{t}"
    box(L, f"RX12C1_LATCH_BLK_{t}", nm, 380, 402, y - 12, y + 12, -165, -20)
    cyl(L, f"RX12C1_LATCH_BLK_{t}_ROD_HOLE", 4.15, [383, y, -28], "X", 20, targets=[nm])
    cyl(L, f"RX12C1_LATCH_BLK_{t}_SENSOR_TAP", 3.4, [395, y, -28], "Y", 13, targets=[nm])
    for i, z in enumerate((-152, -112), 1):
        cyl(L, f"RX12C1_LATCH_BLK_{t}_BOLT_{i}", 2.75, [379, y, z], "X", 24, targets=[nm])
        cyl(L, f"RX12C1_LATCH_BLK_{t}_CBORE_{i}", 4.75, [388, y, z], "X", 15, targets=[nm])
    mat(L, [nm], "A5052")
CL = "P_RX12C1_GS_CLEVIS"
box(L, "RX12C1_GS_CLEVIS", CL, 1060, 1110, -1254, -1216, -385, -255)
box(L, "RX12C1_GS_CLEVIS_SLOT", None, 1050, 1104, -1248, -1222, -395, -245, op='cut', targets=[CL])
cyl(L, "RX12C1_GS_CLEVIS_PINHOLE", 4.0, [A_PT[0], -1255, A_PT[2]], "Y", 40, targets=[CL])
for i, (y, z) in enumerate([(-1243, -270), (-1227, -270), (-1243, -310), (-1227, -310)], 1):
    cyl(L, f"RX12C1_GS_CLEVIS_BOLT_{i}", 2.75, [1103, y, z], "X", 8, targets=[CL])
mat(L, [CL], "A5052")
PINA = "P_RX12C1_GS_PIN_A"
cyl(L, "RX12C1_GS_PIN_A", 4.0, [A_PT[0], -1254, A_PT[2]], "Y", 38, op='new', body=PINA)
mat(L, [PINA], "SCM435")
for t, y in (("A", -400), ("B", -1100)):
    nm = f"P_RX12C1_STOP_{t}"
    box(L, f"RX12C1_STOP_{t}", nm, 1100, 1110, y - 15, y + 15, -320, -260)
    for i, z in enumerate((-270, -310), 1):
        cyl(L, f"RX12C1_STOP_{t}_BOLT_{i}", 2.75, [1099, y, z], "X", 12, targets=[nm])
        cyl(L, f"RX12C1_STOP_{t}_CBORE_{i}", 4.75, [1099, y, z], "X", 6.5, targets=[nm])
    mat(L, [nm], "POM")
UB = "P_RX12C1_UPSTOP_BLK"
box(L, "RX12C1_UPSTOP_BLK", UB, 1118, 1145, -1135, -1108, -90, -40)
for i, z in enumerate((-62, -82), 1):
    cyl(L, f"RX12C1_UPSTOP_BLK_BOLT_{i}", 2.75, [1130, -1136, z], "Y", 29, targets=[UB])
    cyl(L, f"RX12C1_UPSTOP_BLK_CBORE_{i}", 4.75, [1130, -1127, z], "Y", 20, targets=[UB])
cyl(L, "RX12C1_UPSTOP_BLK_M6TAP", 2.5, [1128, -1120, -52], "Z", 12.01, targets=[UB])
mat(L, [UB], "A5052")
act(L, 0)

# ---------------- S07 가스 스프링 간이 형상 ----------------
L = stage('S07_gasspring')
GC = "STEP대기_GASSPRING_F1120_S60_L325_BODY"
act(L, "STEP대기_GASSPRING_F1120_S60_L325")
cyl(L, "RX12C1_GS_BODY", 11.0, along(6), [U[0], 0, U[2]], 201, op='new', body=GC)
cyl(L, "RX12C1_GS_BORE", 5.0, along(20), [U[0], 0, U[2]], 190, targets=[GC])
cyl(L, "RX12C1_GS_EYE_A", 8.0, [A_PT[0], -1240, A_PT[2]], "Y", 10, op='join', targets=[GC])
cyl(L, "RX12C1_GS_EYE_A_HOLE", 4.1, [A_PT[0], -1241, A_PT[2]], "Y", 12, targets=[GC])
mat(L, [GC], "Steel")
GR = "STEP대기_GASSPRING_F1120_S60_L325_ROD"
act(L, "STEP대기_GASSPRING_F1120_S60_L325_ROD")
cyl(L, "RX12C1_GS_ROD", 4.0, along(125), [U[0], 0, U[2]], L0 - 125 - 4.5, op='new', body=GR)
cyl(L, "RX12C1_GS_EYE_P", 8.0, [P_PT[0], -1240, P_PT[2]], "Y", 10, op='join', targets=[GR])
cyl(L, "RX12C1_GS_EYE_P_HOLE", 4.1, [P_PT[0], -1241, P_PT[2]], "Y", 12, targets=[GR])
mat(L, [GR], "Steel")
act(L, 0)

# ---------------- S08 형재 사본 ----------------
L = stage('S08a_profile_copy')
L.append({"command": "component.copy_bodies", "params": {"bodies": ["HFS8-4080-510_M07"], "component": "HFS8-4080-234_RX12C1"}})
L.append({"command": "component.copy_bodies", "params": {"bodies": ["HFS8-4080-510_M07"], "component": "HFS8-4080-200_RX12C1"}})


def profile_stage(nameA, nameB):
    L = stage('S08b_profiles')
    for comp, src, nm, length, yc in (("HFS8-4080-234_RX12C1", nameA, "HFS8-4080-234_RX12C1", 234, -305),
                                       ("HFS8-4080-200_RX12C1", nameB, "HFS8-4080-200_RX12C1", 200, -1175)):
        act(L, comp)
        L.append({"command": "body.rename", "params": {"body": src, "name": nm}})
        box(L, f"RX12C1_{nm[9:12]}_TRIM", None, -2320, -2200, -1540, -1460, -840 + length, -300, op='cut', targets=[nm])
        L.append({"command": "solid.move", "params": {"bodies": [nm], "axis": [0, 0, 1], "angle": 90, "origin": [-2260, -1500, 0],
                                                     "translate": [1130 + 2260, yc + 1500, 590], "name": f"RX12C1_{nm[9:12]}_MOVE"}})
        mat(L, [nm], "Aluminum")
    act(L, 0)
    return L


def dump():
    for k, v in ST.items():
        json.dump(v, open(os.path.join(OUT, f'stage_{k}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print({k: len(v) for k, v in ST.items()})


if __name__ == '__main__':
    if len(sys.argv) > 2:
        profile_stage(sys.argv[1], sys.argv[2])
    dump()


# ---------------- S09 사본(볼·볼트·너트·캡·브래킷 묶음·경첩 B) ----------------
SRC = {"CB5-12": 909, "CB5-16": 8345, "HNTT8-5": 1506, "CB6-20": 8742, "CAP": 1120, "BALL": 6037}
BALL1 = (-2050.0, -1450.0)


def bolt_list():
    """(이름표, 원본, 부모, 자리 점, 방향 d, 수직 p) — 볼트: local x = d(넣는 방향), 원점 = 머리 자리. 너트: local x = 홈 방향, local y = 면 바깥 법선, 원점 = 윗면 중심"""
    B = []
    for b, yc in BAR_Y.items():
        for x in BAR_BOLT_X:
            B.append(("CB5-12", "U2_FLAP", (x, yc, -8), (0, 0, -1), (1, 0, 0)))
    for y in END_BOLT_Y:
        B.append(("CB5-12", "U2_FLAP", (XN_X, y, -8), (0, 0, -1), (1, 0, 0)))
        B.append(("CB5-12", "U2_FLAP", (XP_X, y, -8), (0, 0, -1), (1, 0, 0)))
    for x, y in ARM_BOLTS:
        B.append(("CB5-12", "U2_FLAP", (x, y, -8), (0, 0, -1), (1, 0, 0)))
    for h, yc in HINGE_YC.items():
        for dy in (-10, 10):
            B.append(("CB5-12", "U2_FLAP", (1103, yc + dy, -28), (-1, 0, 0), (0, 0, 1)))
    for x in (1048, 1072):
        B.append(("CB5-12", "U2_FLAP", (x, -1230, -28), (0, 1, 0), (0, 0, 1)))
    for y in (-1125, -1115):
        B.append(("CB5-12", "U2_FLAP", (1106, y, -33), (-1, 0, 0), (0, 0, 1)))
    # 고정
    for h, yc in HINGE_YC.items():
        for z in (-60, -80):
            B.append(("CB5-12", "U2_FLAP_MOUNT", (1107, yc, z), (1, 0, 0), (0, 0, 1)))
            B.append(("HNTT8-5", "U2_FLAP_MOUNT", (1112.5, yc, z), (0, 0, 1), (-1, 0, 0)))
    for y in (-400, -1100):
        for z in (-270, -310):
            B.append(("CB5-12", "U2_FLAP_MOUNT", (1105.5, y, z), (1, 0, 0), (0, 0, 1)))
            B.append(("HNTT8-5", "U2_FLAP_MOUNT", (1112.5, y, z), (0, 1, 0), (-1, 0, 0)))
    for y in LATCH_Y.values():
        for z in (-152, -112):
            B.append(("CB5-16", "U2_FLAP_MOUNT", (388, y, z), (-1, 0, 0), (0, 0, 1)))
            B.append(("HNTT8-5", "U2_FLAP_MOUNT", (377.5, y, z), (0, 1, 0), (1, 0, 0)))
    for y, z in ((-1243, -270), (-1227, -310)):
        B.append(("CB5-16", "U2_FLAP_MOUNT", (1104, y, z), (1, 0, 0), (0, 0, 1)))
        B.append(("HNTT8-5", "U2_FLAP_MOUNT", (1112.5, y, z), (0, 1, 0), (-1, 0, 0)))
    for z in (-62, -82):
        B.append(("CB5-16", "U2_FLAP_MOUNT", (1130, -1127, z), (0, -1, 0), (0, 0, 1)))
        B.append(("HNTT8-5", "U2_FLAP_MOUNT", (1130, -1137.5, z), (0, 0, 1), (0, 1, 0)))
    B.append(("CB6-20", "U2_FLAP_MOUNT", (1128, -1120, -29.06), (0, 0, -1), (1, 0, 0)))
    B.append(("CAP", "HFS8-4080-200_RX12C1", (1130, -1175, -50), (0, 1, 0), (1, 0, 0)))  # x=80 방향, y=40 방향(z=x×y=-Z 안쪽)
    return B


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def frame(kind, d, p):
    if kind in ("HNTT8-5",):
        x, y = d, p
        z = cross(x, y)
    elif kind == "CAP":
        x, y = d, p
        z = cross(x, y)
    else:
        x, z = d, p
        y = cross(z, x)
    return x, y, z


def to_matrix(kind, pt, d, p):
    x, y, z = frame(kind, d, p)
    return [x[0], y[0], z[0], pt[0], x[1], y[1], z[1], pt[1], x[2], y[2], z[2], pt[2]]


def copies_stage():
    L = stage('S09a_copies')
    for x in BALL_X:
        for y in BALL_Y:
            L.append({"command": "occurrence.copy", "params": {"occurrence": SRC["BALL"], "parent": "U2_FLAP", "in_place": True, "translate": [x - BALL1[0], y - BALL1[1], 0]}})
    L.append({"command": "occurrence.copy", "params": {"occurrence": SRC["BALL"], "parent": "U2_FLAP_MOUNT", "in_place": True, "translate": [1050 - BALL1[0], -230 - BALL1[1], 0]}})
    for kind, par, pt, d, p in bolt_list():
        L.append({"command": "occurrence.copy", "params": {"occurrence": SRC[kind], "parent": par, "in_place": True}})
    # 브래킷 묶음(P_M07_LBRKC_PZ_NX:1 + 볼트 2 + 너트 2) x 4
    for _ in range(4):
        for o in (7752, 8124, 8107, 8024, 8016):
            L.append({"command": "occurrence.copy", "params": {"occurrence": o, "parent": "U2_FLAP_MOUNT", "in_place": True}})
    L.append({"command": "occurrence.copy", "params": {"occurrence": 100274, "parent": "U2_FLAP", "in_place": True, "translate": [0, HINGE_YC["B"] - HINGE_YC["A"], 0]}})
    L.append({"command": "occurrence.copy", "params": {"occurrence": 100276, "parent": "U2_FLAP_MOUNT", "in_place": True, "translate": [0, HINGE_YC["B"] - HINGE_YC["A"], 0]}})
    return L


BRK = [(-90, -242.5), (90, -367.5), (-90, -1112.5), (90, -1237.5)]


def moves_stage(ids):
    """ids: S09a 결과의 새 occurrence id 목록(같은 순서)"""
    L = stage('S09b_moves')
    i = 64
    for kind, par, pt, d, p in bolt_list():
        L.append({"command": "occurrence.move", "params": {"occurrence": ids[i], "space": "world", "to_matrix": to_matrix(kind, pt, d, p)}})
        i += 1
    for ang, yc in BRK:
        for _ in range(5):
            L.append({"command": "occurrence.move", "params": {"occurrence": ids[i], "space": "world", "axis": [0, 0, 1], "angle": f"{ang} deg",
                                                              "origin": [1247.5, 180, -227.5], "translate": [1130 - 1247.5, yc - 180, 0]}})
            i += 1
    return L
