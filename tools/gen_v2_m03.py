# -*- coding: utf-8 -*-
"""M03 U5 먼 쪽 바퀴 대차 생성기 — v2.1.1 -> v2.1.2 (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M03_design.md(8절 지시서). 보고서 docs/reports/mechanism/mech_M03_model.md.
python -X utf8 -B tools/gen_v2_m03.py            -> tools/out/mech_M03/model/stage_*.json, edit.json, edit_meta.json
python -X utf8 -B tools/gen_v2_m03.py --machine  -> tools/machine.json 도 고침
좌표: 바늘점 원점, 테이블 면 Z 0. 기준 자세 J_U5_X 0, J_U5_LIFT 0(바퀴 밑 Z 10)에서 세계 좌표로 그린다.
U4 바퀴 묶음(앞판·감속기·서보·센서 브래킷·센서·바퀴·트레드·볼트)은 gen_v2_m02.py의 같은 형상을 X -1700 옮겨 다시 그린다(복사).
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cx, cy, cz, mat_assign, mat_loc, bolt_cols, GEAR_B, thin  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M03")
STEP = PRJ + "/purchased-step/"
DX = -1700.0                     # U4 -> U5 복사 이동

# ---------- 이름 ----------
DRV, IDB, ISH = "P_M03_DRV_BRKT", "P_M03_IDLER_BRKT", "P_M03_IDLER_SHAFT"
XGEAR, XSERVO = "STEP대기_VRXF-PB-60-10_U5X", "STEP대기_MHMF022L1U2M_U5X"
BELT = "STEP대기_HTBNS5M150-3960"
B1, B2 = "STEP대기_6200ZZ_1", "STEP대기_6200ZZ_2"
CHF, CHM = "STEP대기_2400.05.12PZ_F", "STEP대기_2400.05.12PZ_M"
PLATE, CLB, CLC, ARM = "P_M03_CAR_PLATE", "P_M03_BELT_CLAMP_BASE", "P_M03_BELT_CLAMP_CAP", "P_M03_CHAIN_ARM"
MGPB, MGPP = "STEP대기_MGPM25-40Z_BODY", "STEP대기_MGPM25-40Z_PLATE"
LTOP, LSN, LSP = "P_M03_LIFT_TOP", "P_M03_LIFT_SIDE_N", "P_M03_LIFT_SIDE_P"
FRONT, GEAR, SERVO, SNS = "P_M03_FRONT", "STEP대기_VRXF-PB-60-10_U5W", "STEP대기_MHMF022L1U2M_U5W", "P_M03_SNS_BRKT"
WHEEL, TREAD = "P_M03_WHEEL", "P_M03_WHEEL_TREAD"
E32 = "E32-D36P1_2M_M03"

# ---------- 기하 ----------
XD, XI, ZC = -2220.0, -390.0, 390.0          # 구동·아이들러 풀리 중심 X, 중심 Z
PY0 = 95.5                                    # 풀리 앞면 Y(지시 95 -> 감속기 볼트 머리 Y 90~95와 0.5 띄움)
R_BI, R_BO = 47.25, 50.65                     # 벨트 띠 안·밖 반지름(이 끝 47.2 바깥, 두께 3.4, 피치선 47.75 포함)
BY0, BY1 = 98.5, 113.5
PCD = [(24.749 * a, 24.749 * b) for a in (-1, 1) for b in (-1, 1)]
DRV_FEET = [(x, z) for x in (-2265.0, -2175.0) for z in (322.0, 458.0)]
IDL_FEET = [(x, z) for x in (-425.0, -355.0) for z in (322.0, 458.0)]
BLK_H = [(-1993.5, 284.0), (-1993.5, 316.0), (-1866.5, 284.0), (-1866.5, 316.0)]   # 블록 STEP 탭(실측)
MGP_X0, MGP_X1, MGP_Y0, MGP_Y1 = -1986.5, -1893.5, 38.0, 80.0
ROD_X = [(-1965.0, 8.0), (-1915.0, 8.0), (-1940.0, 5.0)]   # 가이드봉 Ø16 ×2 + 로드 Ø10, Y 59
ROD_Y = 59.0
MGP_BODY_B = [(x, z) for x in (-1980.0, -1900.0) for z in (190.0, 265.0)]        # 몸 관통 CB6(앞에서)
MGP_PLATE_B = [(x, y) for x in (-1981.0, -1899.0) for y in (62.0, 73.0)]        # 끝판 탭 CB6(밑에서)
CLAMP_B = [(x, z) for x in (-2035.0, -2015.0) for z in (332.0, 352.0)]
ARM_B = [(-1940.0, 88.0), (-1920.0, 88.0)]
CHM_B = [(-1940.0, 215.0), (-1940.0, 258.0)]
CHF_B = [(-1245.0, 215.0), (-1245.0, 258.0)]
FLG_B = [(x, y) for x in (-1975.0, -1835.0) for y in (-46.0, 46.0)]
CHAIN_T = (-3497.0, 208.0, 817.5)              # 체인 STEP: Y축 180° + 이동(굽힘 시작 STEP X -2300 -> -1197)
CHAIN_KEEP_X0 = -1930.0                        # 위 가닥 움직이는 끝


def hat(nm, x0, x1, yw):
    """ㄷ(모자) 판금 t4: 웨브 Y yw~yw+4 · Z 330~450, 다리 Z 330~334·446~450, 발 Y 116~120 · Z 314~334 / 446~466(보 앞면에 붙음)."""
    y1 = yw + 4
    pts = [[yw, 330], [yw, 450], [116, 450], [116, 466], [120, 466], [120, 446], [y1, 446], [y1, 334],
           [120, 334], [120, 314], [116, 314], [116, 330]]
    sk = "SK_" + nm
    return [C("sketch.create", plane={"origin": [x0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name=sk),
            C("sketch.line", points=pts, closed=True), C("sketch.finish"),
            C("solid.extrude", sketch=sk, distance=round(x1 - x0, 4), operation="new", body_name=nm)]


def ins(path, name, cols, t, renames, pn, bom="purchased", desc=None):
    s = [C("file.insert_step", path=STEP + path, name=name, matrix=mat_loc(cols, t))]
    s += [C("body.rename", body=a, name=b) for a, b in renames]
    md = {"component": name, "part_number": pn, "bom_type": bom}
    if desc:
        md["description"] = desc
    s.append(C("component.metadata.set", **md))
    return s


def bolt(nm, pn, d, at):
    return ins("%s/%s.stp" % (pn, pn), nm, bolt_cols(d), at, [("Cut-Extrude1", nm)], pn)


def cb6(nm, d, at, comp):
    """STEP대기_CB6-20 임시: 머리 Ø10×6 + 축 Ø6×20(at = 머리 밑면, d = 축 방향)."""
    a = {"+Y": (0, 1, 0), "+Z": (0, 0, 1)}[d]
    base_h = [at[i] - 6 * a[i] for i in range(3)]
    return [cyl(5.0, base_h, 6, list(a), "new", name=nm), cyl(3.0, list(at), 20, list(a), "join", [nm])]


Y_COLS = [(0, 1, 0), (0, 0, 1), (1, 0, 0)]     # STEP 로컬 X -> 세계 +Y


# ---------- 1. 준비 + 레일 (앱에서 먼저 돌린 것 그대로) ----------
def stage_rail():
    return [C("joint.drive", joint="J_U5_X", value=0, quiet=True),
            C("joint.drive", joint="J_U5_LIFT", value=0, quiet=True),
            C("file.insert_step", path=STEP + "SV2RL28-1800/SV2RL28-1800.stp", name="SV2RL28-1800",
              matrix=[1, 0, 0, -2110, 0, -1, 0, 120, 0, 0, -1, 300]),
            C("joint.delete", joint="Rigid Group 563:567"),
            C("joint.delete", joint="Rigid Group 563:568"),
            C("occurrence.reparent", occurrence="BLOCK_SV2RL28-1800:1", parent="U5_CAR"),
            C("occurrence.reparent", occurrence="BLOCK_SV2RL28-1800:2", parent="U5_CAR"),
            C("occurrence.move", occurrence="BLOCK_SV2RL28-1800:1", space="world", translate=[86.6087, 0, 0]),
            C("occurrence.move", occurrence="BLOCK_SV2RL28-1800:2", space="world", translate=[65.7675, 0, 0])]


def stage_prep():
    return [C("joint.drive", joint="J_U5_WHEEL_ROT", value=0, quiet=True),
            C("solid.remove", bodies=["U5_RAIL", "U5_CHAIN", "U5_CARRIAGE", "U5_DRIVE", "U5_HOLDER", "U5_WHEEL_TIRE"]),
            C("joint.limits", joint="J_U5_LIFT", min=-10, max=30),
            C("body.rename", body="Cap Screw1", name="SV2RL28-1800_RAIL"),
            C("body.rename", body="Tap1", name="SV2RL28-1800_BLOCK"),
            C("component.metadata.set", component="SV2RL28-1800", part_number="SV2RL28-1800", bom_type="purchased"),
            mat_assign(["SV2RL28-1800_RAIL", "SV2RL28-1800_BLOCK"], "Steel"),
            C("material.create", name="PET-CF", density_g_cm3=1.35, color="#3a3a3a")]


# ---------- 2. 고정부: 구동 묶음·아이들러·벨트 ----------
def stage_drive():
    s = hat(DRV, -2280, -2160, 86)
    s += [cy(25, XD, ZC, 85, 91, "cut", [DRV])]
    s += [cy(2.75, XD + a, ZC + b, 85, 91, "cut", [DRV]) for a, b in PCD]
    s += [cy(2.75, x, z, 115, 121, "cut", [DRV]) for x, z in DRV_FEET]
    # 감속기·서보 임시(U4 것과 같은 치수, 축 +Y)
    s += [box(XGEAR, XD - 30, XD + 30, 11, 86, ZC - 30, ZC + 30),
          cy(25, XD, ZC, 86, 89, "join", [XGEAR]),
          cy(8, XD, ZC, 89, 117, "join", [XGEAR]),
          cy(5.75, XD, ZC, 10, 41, "cut", [XGEAR])]
    s += [cy(2.1, XD + a, ZC + b, 74, 86, "cut", [XGEAR]) for a, b in PCD]
    s += [box(XSERVO, XD - 30, XD + 30, -69, 11, ZC - 30, ZC + 30),
          cy(5.5, XD, ZC, 11, 41, "join", [XSERVO])]
    # 아이들러 브래킷 + 장공 ±5
    s += hat(IDB, -440, -340, 90)
    s += [cy(5.25, XI, ZC, 89, 95, "cut", [IDB])]
    for x, z in IDL_FEET:
        s += [box(None, x - 5, x + 5, 115, 121, z - 2.75, z + 2.75, "cut", [IDB]),
              cy(2.75, x - 5, z, 115, 121, "cut", [IDB]), cy(2.75, x + 5, z, 115, 121, "cut", [IDB])]
    s += [cy(5, XI, ZC, 82, 94, "new", name=ISH), cy(7, XI, ZC, 94, 97, "join", [ISH]), cy(5, XI, ZC, 97, 117, "join", [ISH])]
    s += [cy(15, XI, ZC, 97, 106, "new", name=B1), cy(5, XI, ZC, 96, 107, "cut", [B1]),
          cy(15, XI, ZC, 106, 115, "new", name=B2), cy(5, XI, ZC, 105, 116, "cut", [B2])]
    # 보 앞면 M5 탭(깊이 12)
    s += [cy(2.1, x, z, 119, 132, "cut", ["U1_BEAM"]) for x, z in DRV_FEET + IDL_FEET]
    # 벨트: 두 풀리를 감는 띠(Y 98.5~113.5), 클램프 자리 X -2027~-2023 끊음
    s += [box(BELT, XD, XI, BY0, BY1, ZC - R_BO, ZC + R_BO),
          cy(R_BO, XD, ZC, BY0, BY1, "join", [BELT]), cy(R_BO, XI, ZC, BY0, BY1, "join", [BELT]),
          box(None, XD, XI, BY0 - 1, BY1 + 1, ZC - R_BI, ZC + R_BI, "cut", [BELT]),
          cy(R_BI, XD, ZC, BY0 - 1, BY1 + 1, "cut", [BELT]), cy(R_BI, XI, ZC, BY0 - 1, BY1 + 1, "cut", [BELT]),
          box(None, -2027, -2023, BY0 - 1, BY1 + 1, 330, 350, "cut", [BELT])]
    s += [mat_assign([DRV, IDB], "SUS304"), mat_assign([ISH], "S45C"),
          mat_assign([XGEAR, XSERVO, B1, B2], "Steel"),
          C("component.move_bodies", bodies=[DRV, IDB, ISH, XGEAR, XSERVO, B1, B2, BELT], component="U5_WHEEL_F")]
    return s


PUL_PARTS = [("Cut-Extrude2", "HUB"), ("Revolve2[1]", "FLANGE1"), ("Revolve2[2]", "FLANGE2"), ("Cut-Extrude3", "SET1"), ("Cut-Extrude4", "SET2")]


def stage_pulleys():
    s = []
    for nm, x, pn in (("STEP대기_HTPA60S5M150-A-N16", XD, "HTPA60S5M150-A-N16"), ("HTPA60S5M150-A-N30_M03", XI, "HTPA60S5M150-A-N30")):
        s += ins("HTPA60S5M150-A-N30/HTPA60S5M150-A-N30.stp", nm, Y_COLS, (x, PY0, ZC),
                 [(a, "%s_%s" % (nm, b)) for a, b in PUL_PARTS], pn,
                 desc=("Misumi HTPA60S5M150-A-N30 STEP used as N16 placeholder (bore 16)" if "N16" in pn else None))
        s.append(mat_assign(["%s_%s" % (nm, b) for _, b in PUL_PARTS], "A6061"))
    return s


CHAIN_BODIES = ["2026_11_03_12_31_49_0588 (2)"] + ["2026_11_03_12_31_49_%s%s" % (n, sfx) for n in ("0604", "0619", "0635", "0651", "0666", "0682", "0698")
                                                    for sfx in ("", " (2)", " (3)")]


def stage_chain():
    cols = [(-1, 0, 0), (0, 1, 0), (0, 0, -1)]
    ren = [("2026_11_03_12_31_49_0588 (2)", "2400.05.075.0_UPPER")]
    k = 1
    for n in ("0604", "0619", "0635", "0651", "0666", "0682", "0698"):
        for sfx, p in (("", "BAR"), (" (2)", "SIDE1"), (" (3)", "SIDE2")):
            ren.append(("2026_11_03_12_31_49_%s%s" % (n, sfx), "2400.05.075.0_L%02d_%s" % (k, p)))
        k += 1
    s = [C("file.insert_step", path=STEP + "2400.05.075.0/2400.05.075.0.stp", name="2400.05.075.0", matrix=mat_loc(cols, CHAIN_T)),
         C("solid.remove", bodies=["2026_11_03_12_31_49_0588"])]
    s += [C("body.rename", body=a, name=b) for a, b in ren]
    s += [box(None, -3600, CHAIN_KEEP_X0, 190, 290, 790, 845, "cut", ["2400.05.075.0_UPPER"]),
          C("component.metadata.set", component="2400.05.075.0", part_number="2400.05.075.0", bom_type="purchased",
            description="igus E2 R75, shortened to about 22 links (pitch 46) by trimming the straight run in the model")]
    # 고정 끝 브래킷 임시(L: 발 t4 + 세운 쪽 t8)
    s += [C("sketch.create", plane={"origin": [0, 273, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_M03_CHF"),
          C("sketch.line", points=[[-1262, 650], [-1222.5, 650], [-1222.5, 685], [-1230.5, 685], [-1230.5, 654], [-1262, 654]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M03_CHF", distance=73, operation="new", body_name=CHF)]
    s += [cz(2.75, x, y, 649, 655, "cut", [CHF]) for x, y in CHF_B]
    s += [cz(2.1, x, y, 637, 651, "cut", ["U1_BEAM"]) for x, y in CHF_B]
    s += [mat_assign([CHF], "Steel"), C("component.move_bodies", bodies=[CHF], component="U5_WHEEL_F")]
    return s


# ---------- 3. 대차 ----------
def stage_car():
    s = [box(PLATE, -2045, -1825, 80, 92, 160, 420)]
    s += [cy(2.75, x, z, 79, 93, "cut", [PLATE]) for x, z in BLK_H + CLAMP_B]
    s += [cy(2.5, x, z, 79, 93, "cut", [PLATE]) for x, z in MGP_BODY_B]
    s += [cz(2.1, x, y, 408, 421, "cut", [PLATE]) for x, y in ARM_B]
    # 벨트 클램프(PET-CF): 아래 턱 + 위 턱, 가운데 벨트 길(관통)
    s += [box(CLB, -2040, -2010, 92, 117, 325, ZC - R_BO), box(CLC, -2040, -2010, 92, 117, ZC - R_BI + 0.0, 360)]
    s += [cy(3.4, x, z, 91, 100, "cut", [CLB if z < 340 else CLC]) for x, z in CLAMP_B]
    # MGP 몸 임시: 봉 구멍 + 앞 카운터보어
    s += [box(MGPB, MGP_X0, MGP_X1, MGP_Y0, MGP_Y1, 179, 276)]
    s += [cz(r + 0.2, x, ROD_Y, 178, 277, "cut", [MGPB]) for x, r in ROD_X]
    for x, z in MGP_BODY_B:
        s += [cy(5.5, x, z, 37, 68, "cut", [MGPB]), cy(3.3, x, z, 67, 81, "cut", [MGPB])]
    # 체인 팔(Z자 t3)
    s += [C("sketch.create", plane={"origin": [-1950, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M03_ARM"),
          C("sketch.line", points=[[80, 420], [92, 420], [92, 423], [83, 423], [83, 845], [275, 845], [275, 848], [80, 848]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M03_ARM", distance=40, operation="new", body_name=ARM)]
    s += [cz(2.75, x, y, 419, 424, "cut", [ARM]) for x, y in ARM_B]
    s += [cz(2.75, x, y, 844, 849, "cut", [ARM]) for x, y in CHM_B]
    # 움직이는 끝 브래킷 임시(판, 탭)
    s += [box(CHM, -1950, -1925, 200, 273, 835, 845)]
    s += [cz(2.1, x, y, 834, 846, "cut", [CHM]) for x, y in CHM_B]
    s += [mat_assign([PLATE], "A5052"), mat_assign([CLB, CLC], "PET-CF"), mat_assign([ARM], "SUS304"),
          mat_assign([MGPB, CHM], "Steel"),
          C("component.move_bodies", bodies=[PLATE, CLB, CLC, MGPB, ARM, CHM], component="U5_CAR")]
    return s


# ---------- 4. 승강부(LIFT 0 자세) ----------
def stage_lift():
    s = [box(MGPP, MGP_X0, MGP_X1, MGP_Y0, MGP_Y1, 134, 149)]
    s += [cz(r, x, ROD_Y, 149, 239, "join", [MGPP]) for x, r in ROD_X]
    s += [cz(2.5, x, y, 133, 146, "cut", [MGPP]) for x, y in MGP_PLATE_B]
    s += [box(LTOP, -1990, -1820, -55, 78, 126, 134)]
    s += [cz(3.3, x, y, 125, 135, "cut", [LTOP]) for x, y in MGP_PLATE_B]
    s += [cz(2.1, x, y, 125, 135, "cut", [LTOP]) for x, y in FLG_B]
    for nm, pts in ((LSN, [[-37, 30], [-31, 30], [-31, 126], [-55, 126], [-55, 120], [-37, 120]]),
                    (LSP, [[31, 30], [37, 30], [37, 120], [55, 120], [55, 126], [31, 126]])):
        sk = "SK_" + nm
        s += [C("sketch.create", plane={"origin": [-1990, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name=sk),
              C("sketch.line", points=pts, closed=True), C("sketch.finish"),
              C("solid.extrude", sketch=sk, distance=170, operation="new", body_name=nm)]
    s += [cz(2.75, x, y, 119, 127, "cut", [LSN if y < 0 else LSP]) for x, y in FLG_B]
    s += [cy(2.75, -1826, z, -38, -30, "cut", [LSN]) for z in (55, 85)]
    s += [cy(2.75, -1826, z, 30, 38, "cut", [LSP]) for z in (55, 85)]
    # U4 바퀴 묶음 복사(X -1700): 앞판, 감속기, 서보, 센서 브래킷
    s += [box(FRONT, -132 + DX, -120 + DX, -31, 31, 30, 110),
          cx(25, 0, 70, -133 + DX, -129 + DX, "cut", [FRONT]),
          cx(9, 0, 70, -133 + DX, -119 + DX, "cut", [FRONT])]
    s += [cx(2.75, y, z, -133 + DX, -119 + DX, "cut", [FRONT]) for (y, z) in GEAR_B]
    s += [cy(2.1, -126 + DX, z, -32, -19, "cut", [FRONT]) for z in (55, 85)]
    s += [cy(2.1, -126 + DX, z, 19, 32, "cut", [FRONT]) for z in (55, 85)]
    s += [box(GEAR, -207 + DX, -132 + DX, -30, 30, 40, 100),
          cx(25, 0, 70, -132 + DX, -129 + DX, "join", [GEAR]),
          cx(8, 0, 70, -129 + DX, -97 + DX, "join", [GEAR]),
          cx(5.75, 0, 70, -208 + DX, -177 + DX, "cut", [GEAR])]
    s += [cx(2.1, y, z, -144 + DX, -132 + DX, "cut", [GEAR]) for (y, z) in GEAR_B]
    s += [box(SERVO, -287 + DX, -207 + DX, -30, 30, 40, 100),
          cx(5.5, 0, 70, -207 + DX, -177 + DX, "join", [SERVO])]
    s += [C("sketch.create", plane={"origin": [-132 + DX, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M03_SNS"),
          C("sketch.line", points=[[-95, 41], [-37, 41], [-37, 95], [-39, 95], [-39, 43], [-95, 43]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M03_SNS", distance=17, operation="new", body_name=SNS),
          box(None, -120 + DX, -114 + DX, -39.5, -36.5, 43, 96, "cut", [SNS]),
          box(None, -117.5 + DX, -115.5 + DX, -94, -66, 25, 42, "join", [SNS])]
    s += [cy(2.75, -126 + DX, z, -40, -36, "cut", [SNS]) for z in (55, 85)]
    s += [cx(1.6, -80, z, -118 + DX, -115 + DX, "cut", [SNS]) for z in (27.5, 37.5)]
    s += [mat_assign([LTOP, LSN, LSP, FRONT, SNS], "SUS304"), mat_assign([GEAR, SERVO, MGPP], "Steel"),
          C("component.move_bodies", bodies=[MGPP, LTOP, LSN, LSP, FRONT, GEAR, SERVO, SNS], component="U5_LIFT")]
    # 바퀴(U5_WHEEL)
    s += [cx(50, 0, 70, -112.5 + DX, -87.5 + DX, "new", name=WHEEL),
          cx(18, 0, 70, -119 + DX, -112.5 + DX, "join", [WHEEL]),
          cx(8, 0, 70, -120 + DX, -86 + DX, "cut", [WHEEL]),
          cx(60, 0, 70, -112.5 + DX, -87.5 + DX, "new", name=TREAD),
          cx(50, 0, 70, -113 + DX, -87 + DX, "cut", [TREAD]),
          mat_assign([WHEEL], "A6061"), mat_assign([TREAD], "Urethane_A70"),
          C("component.move_bodies", bodies=[WHEEL, TREAD], component="U5_WHEEL")]
    return s


# ---------- 5. 구매품 체결·센서·인서트 + 리지드 묶음 ----------
def bolt_list():
    b = []   # (이름, 형번, 방향, 머리 밑면 점, 묶음)
    n = 1
    for x, z in DRV_FEET + IDL_FEET:
        b.append(("CB5-16_M03_%d" % n, "CB5-16", "+Y", (x, 116.0, z), "U5_WHEEL_F")); n += 1
    for z in (55, 85):                                        # 옆판 -> 앞판(복사)
        b.append(("CB5-16_M03_%d" % n, "CB5-16", "+Y", (-126 + DX, -39.0, z), "U5_LIFT")); n += 1
        b.append(("CB5-16_M03_%d" % n, "CB5-16", "-Y", (-126 + DX, 37.0, z), "U5_LIFT")); n += 1
    n = 1
    for a, c in PCD:                                          # X 감속기 -> 구동 브래킷(안에서)
        b.append(("CB5-20_M03_%d" % n, "CB5-20", "-Y", (round(XD + a, 4), 90.0, round(ZC + c, 4)), "U5_WHEEL_F")); n += 1
    for (y, z) in GEAR_B:                                     # 바퀴 감속기 -> 앞판(복사)
        b.append(("CB5-20_M03_%d" % n, "CB5-20", "-X", (-120 + DX, round(y, 4), round(z, 4)), "U5_LIFT")); n += 1
    for x, z in BLK_H:                                        # 대차판 -> LM 블록(앞에서 통과)
        b.append(("CB5-20_M03_%d" % n, "CB5-20", "+Y", (x, 80.0, z), "U5_CAR")); n += 1
    for x, z in CLAMP_B:                                      # 대차판 -> 클램프 인서트
        b.append(("CB5-20_M03_%d" % n, "CB5-20", "+Y", (x, 80.0, z), "U5_CAR")); n += 1
    n = 1
    for x, y in CHF_B:
        b.append(("CB5-12_M03_%d" % n, "CB5-12", "-Z", (x, y, 654.0), "U5_WHEEL_F")); n += 1
    for x, y in ARM_B:
        b.append(("CB5-12_M03_%d" % n, "CB5-12", "-Z", (x, y, 423.0), "U5_CAR")); n += 1
    for x, y in CHM_B:
        b.append(("CB5-12_M03_%d" % n, "CB5-12", "-Z", (x, y, 848.0), "U5_CAR")); n += 1
    for x, y in FLG_B:                                        # 옆판 플랜지 -> 승강판(밑에서, MGP 끝판 피해 12)
        b.append(("CB5-12_M03_%d" % n, "CB5-12", "+Z", (x, y, 120.0), "U5_LIFT")); n += 1
    return b


def stage_purchased():
    s, groups = [], {"U5_WHEEL_F": ["U5_WHEEL_F:1", "SV2RL28-1800:1", "STEP대기_HTPA60S5M150-A-N16:1", "HTPA60S5M150-A-N30_M03:1", "2400.05.075.0:1"],
                     "U5_CAR": ["U5_CAR:1", "BLOCK_SV2RL28-1800:1", "BLOCK_SV2RL28-1800:2"], "U5_LIFT": ["U5_LIFT:1"]}
    s += ins("E32-D36P1_2M/E32-D36P1_2M.stp", E32, [(0, 0, 1), (0, 1, 0), (-1, 0, 0)], (-113 + DX, -80, 27.5), [("NONE", E32)], "E32-D36P1 2M")
    groups["U5_LIFT"].append(E32 + ":1")
    for i, (x, z) in enumerate(CLAMP_B, 1):
        nm = "MBIS5-6.5-8_M03_%d" % i
        s += ins("MBIS5-6.5-8/MBIS5-6.5-8.stp", nm, Y_COLS, (x, 92.0, z), [("MBIS5-6.5-8", nm)], "MBIS5-6.5-8")
        groups["U5_CAR"].append(nm + ":1")
    bodies = []
    for (nm, pn, d, at, g) in bolt_list():
        s += bolt(nm, pn, d, at)
        bodies.append(nm)
        groups[g].append(nm + ":1")
    s += [mat_assign(bodies, "SCM435"), mat_assign([E32], "Default")]
    # STEP대기_CB6-20 임시(바디, 묶음 컴포넌트 안)
    c6c, c6l = [], []
    for i, (x, z) in enumerate(MGP_BODY_B, 1):
        nm = "STEP대기_CB6-20_M03_%d" % i
        s += cb6(nm, "+Y", (x, 68.0, z), "U5_CAR"); c6c.append(nm)
    for i, (x, y) in enumerate(MGP_PLATE_B, 5):
        nm = "STEP대기_CB6-20_M03_%d" % i
        s += cb6(nm, "+Z", (x, y, 126.0), "U5_LIFT"); c6l.append(nm)
    s += [mat_assign(c6c + c6l, "SCM435"),
          C("component.move_bodies", bodies=c6c, component="U5_CAR"),
          C("component.move_bodies", bodies=c6l, component="U5_LIFT")]
    s += [C("joint.rigid_group", occurrences=v) for v in groups.values()]
    return s


# ---------- 6. 연구 키 ----------
LIFT_ID = 49
REV_IDS = {47, 50, 84, 99, 114, 270}
# 바퀴(U5_WHEEL) ↔ 테이프 겹침 단계(v2.1.2 그리는 중 motion.interference 실측, 깊이 ≤ 1.0 = 테이프 두께).
# 지시서는 172·315 두 점이었으나 같은 일이 모든 모서리에서 생겨(측정부 표본에 없던 단계) 같은 원리(테이프 위 1.0)로 넓힌다.
TAPE_RANGES = {"CYCLE_L": [(80, 83), (171, 174), (234, 237), (325, 328), (388, 391), (479, 482), (542, 545), (633, 636)],
               "CYCLE_G1": [(177, 183)],
               "CYCLE_G2": [(25, 31), (119, 122), (170, 173), (261, 264), (312, 315), (403, 406), (454, 457), (545, 548)]}


def lift_keys(pts, rngs, m=1):
    """J_U5_LIFT 0 구간 안에서 테이프 위 단계(앞뒤 m단계 여유)를 1.0으로. 나머지 키는 그대로."""
    n = int(max(p[0] for p in pts))
    def base(t):
        for (a, va), (b, vb) in zip(pts, pts[1:]):
            if a <= t <= b:
                return va if b == a else va + (vb - va) * (t - a) / (b - a)
        return pts[-1][1]
    v = [base(t) for t in range(n + 1)]
    for a, b in rngs:
        for t in range(a - m, b + m + 1):
            if v[t] == 0:
                v[t] = 1.0
    out = [[t, round(x, 3)] for t, x in enumerate(v)]
    return [[a, b] for a, b in thin(out, 1e-6)]
JNAME = {44: "J_U3_PRESSER", 45: "J_U3_NEEDLE", 47: "J_U4_WHEEL_ROT", 48: "J_U5_X", 49: "J_U5_LIFT", 50: "J_U5_WHEEL_ROT",
         82: "J_WP_L_X", 83: "J_WP_L_Y", 84: "J_WP_L_ROT", 97: "J_WP_S_X", 98: "J_WP_S_Y", 99: "J_WP_S_ROT",
         112: "J_WP_G_X", 113: "J_WP_G_Y", 114: "J_WP_G_ROT", 270: "J_U4_PRESS"}


def stage_studies():
    d = json.load(open(os.path.join(OUT, "model", "motion_list_v2.1.1.json"), encoding="utf-8"))
    s = []
    for st in d["studies"]:
        if st["name"] not in TAPE_RANGES:
            continue
        rngs = TAPE_RANGES[st["name"]]
        ks = []
        for k in st["keys"]:
            f = 180.0 / math.pi if k["joint"] in REV_IDS else 1.0      # motion.list는 회전 값을 라디안으로 준다(실측), motion.study는 도
            pts = [[int(p[0]), round(p[1] * f, 3)] for p in k["points"]]
            pts = [[a, b] for a, b in thin(pts, 1e-3)]
            if k["joint"] == LIFT_ID:
                pts = lift_keys(pts, rngs)
            ks.append({"joint": JNAME[k["joint"]], "points": [[a, int(b) if float(b).is_integer() else b] for a, b in pts]})
        s.append(C("motion.study", study=st["name"], steps=st["steps"], keys=ks))
    return s


def stage_final():
    return [C("joint.drive", joint="J_U5_WHEEL_ROT", value=0, quiet=True),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M03 mechanism: U5 far wheel carriage - LM rail, belt-driven servo carriage, MGP lift, servo wheel, cable chain")]


STAGES = [("rail", stage_rail), ("prep", stage_prep), ("drive", stage_drive), ("pulleys", stage_pulleys), ("chain", stage_chain),
          ("car", stage_car), ("lift", stage_lift), ("purchased", stage_purchased), ("studies", stage_studies), ("final", stage_final)]


def patch_machine():
    p = os.path.join(ROOT, "machine.json")
    m = json.load(open(p, encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.1.2.sc"
    j = m["joints"]["J_U5_LIFT"]
    j["min"], j["max"], j["rest"] = -10, 30.0, 30.0
    j["_note"] = ("M03(v2.1.2) MGPM25-40Z 가이드 실린더(몸 U5_CAR, 끝판·봉 U5_LIFT). 30 = 들림(대기, 실린더 후퇴 끝 — 끝판이 몸 밑면에 닿음), "
                  "0 = 바퀴 밑 Z 10(매트 윗면), 1.0 = Z 11(테이프 위, CYCLE_L 172·CYCLE_G2 315), 2.0 = Z 12(이음매), -10 = 행정 끝(바퀴 밑 Z 0, 매트 없을 때만). "
                  "작동: 무게 58 N + 머리 쪽 압력으로 누름 90 N(D-92). 바퀴 접촉선(폭 25)이 매트 밖이면 앞뒤 한 단계 여유로 든다(0-8-2 ③)")
    m["joints"]["J_U5_X"]["_note"] = (m["joints"]["J_U5_X"].get("_note", "") +
                                      " M03: SV2RL28-1800 레일(보 앞면 Y 120, Z 300) + 블록 2(X -2000·-1860 REST). 구동 MHMF022L1U2M + VRXF 1/10 + S5M 60T 벨트(풀리 X -2220 ↔ -390). X는 LIFT 30에서만 움직인다(U-09)")
    u = m["units"]["U5_WHEEL_F"]
    u["parts"] = ["U5_", "P_M03_", "SV2RL28-1800_", "STEP대기_MHMF022L1U2M_U5", "STEP대기_VRXF-PB-60-10_U5", "STEP대기_HTPA60S5M150-A-N16",
                  "HTPA60S5M150-A-N30_M03", "STEP대기_6200ZZ_", "STEP대기_HTBNS5M150-3960", "2400.05.075.0_", "STEP대기_2400.05.12PZ_",
                  "STEP대기_MGPM25-40Z_", "STEP대기_CB6-20_M03", "MBIS5-6.5-8_M03", "E32-D36P1_2M_M03", "CB5-16_M03", "CB5-20_M03", "CB5-12_M03"]
    u["_note"] = ("M03(v2.1.2): 고정 U5_WHEEL_F = 레일·구동 브래킷·X 서보·감속기·구동 풀리·아이들러 브래킷·축·6200ZZ ×2·아이들러 풀리·벨트(REST 형상)·케이블 체인(REST 형상)·고정 끝 브래킷. "
                  "U5_CAR = LM 블록 2·대차판·벨트 클램프 2·MGP 몸·체인 팔·움직이는 끝 브래킷. U5_LIFT = MGP 끝판·봉·승강판·옆판 2·앞판·바퀴 감속기·서보·센서 브래킷·E32. U5_WHEEL = 허브·트레드. "
                  "벨트·체인은 모양이 바뀌는 부품이라 REST 형상만 둔다(체인 ↔ 움직이는 끝 브래킷 비교 제외, baseline)")
    for st in m["states"]:
        if st["study"] == "CYCLE_L" and st["step"] == 172:
            st["joints"]["J_U5_LIFT"] = 1.0
            st["_m03"] = "모서리 끝 테이프 위 1.0(M03)"
    if not any(st["study"] == "CYCLE_G2" and st["step"] == 315 for st in m["states"]):
        base = next(st for st in m["states"] if st["study"] == "CYCLE_G2" and st["step"] == 75)
        ns = json.loads(json.dumps(base))
        ns["name"] = "홈 매트 모서리 끝 테이프 위(먼 쪽 바퀴 1.0)"
        ns["step"] = 315
        ns["joints"] = {k: v for k, v in ns["joints"].items() if k.startswith("J_U5")}
        ns["joints"]["J_U5_LIFT"] = 1.0
        ns["_m03"] = "모서리 끝 테이프 위 1.0(M03). 다른 조인트 값은 연구 CYCLE_G2 315단계를 따른다"
        m["states"].append(ns)
    bl = m["baseline_overlaps"]
    bl.append({"a": "CB5-*_M03_*·STEP대기_CB6-20_M03_*", "b": "탭 구멍 부품·MBIS5 인서트", "reason": "나사 물림(Ø5 축 ↔ Ø4.2 탭, Ø6 ↔ Ø5) 의도된 겹침(M-08)"})
    bl.append({"a": "STEP대기_2400.05.12PZ_M·P_M03_CHAIN_ARM(U5_CAR)", "b": "2400.05.075.0_*(REST 형상)",
               "reason": "M03: 케이블 체인은 모양이 바뀌는 부품이라 REST 형상만 둔다. J_U5_X ≠ 0에서 움직이는 끝 브래킷이 고정 형상의 굽힘과 겹치는 것은 실물이 아니다 — 비교에서 뺀다"})
    bl.append({"a": "P_M03_BELT_CLAMP_*(U5_CAR)", "b": "STEP대기_HTBNS5M150-3960(REST 형상)", "reason": "M03: 벨트는 REST 형상. 클램프 벨트 길은 관통이라 겹침 0이어야 한다"})
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += s
        print("stage_%d_%s" % (i, nm), len(s), len(json.dumps(s, ensure_ascii=False, separators=(",", ":"))))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.1.1.sc", "result": "3D_Modeling/FSAP_v2.1.2.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if "--machine" in sys.argv:
        patch_machine()
        print("machine.json patched")


if __name__ == "__main__":
    main()
