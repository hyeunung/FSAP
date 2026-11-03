# -*- coding: utf-8 -*-
"""M02 U4 바늘 옆 바퀴 생성기 — v2.0.2 -> v2.1.0 (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M02_design.md(1·2·4·5·8절) + mech_M02_design1.md(수정 1회차: 접촉 추종 키).
python -X utf8 -B tools/gen_v2_m02.py            -> tools/out/mech_M02/model/stage_*.json, edit.json, edit_meta.json, keys.json
python -X utf8 -B tools/gen_v2_m02.py --machine  -> tools/machine.json 도 고침
좌표: 바늘점 원점, 테이블 면 Z 0. 레버 부품은 J_U4_PRESS 0(바퀴 밑 Z 10) 자세의 세계 좌표로 그린다.
실물 STEP(CDM2C20-25Z + I-020B) 핀 사이 후퇴 183.5 -> 위 핀을 지시 (-163.9, 262.4)에서 같은 축선 위로 옮김(보고서 2절).
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M02")
STEP = PRJ + "/purchased-step/"
KEY = {"Z": "STEP대기_"}

# ---------- 레버·실린더 기하 ----------
PIV = (-300.0, 70.0)          # 피벗 (X, Z), 축 -Y(+ = 들림)
TH_LO, TH_UP = -1.867, 8.627
TH_UP_STOP = 8.626           # 조인트 한계(실린더 후퇴 끝 8.6265 바로 앞)
P0 = (-160.0, 122.0)          # 로드 핀(θ 0)
T_DESIGN = (-163.9, 262.4)    # 설계안 위 핀(후퇴 120 임시)
L_RET = 183.5                 # 실물: 클레비스 핀(로컬 117) - 로드 끝 핀(로컬 -66.5)
STROKE = 25.0


def rotp(p, th):
    """피벗 둘레 θ(도, + = 들림) — (x, z)."""
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    dx, dz = p[0] - PIV[0], p[1] - PIV[1]
    return (PIV[0] + dx * c - dz * s, PIV[1] + dx * s + dz * c)


P_UP = rotp(P0, TH_UP)
_d = (T_DESIGN[0] - P_UP[0], T_DESIGN[1] - P_UP[1])
_n = math.hypot(*_d)
T = (round(P_UP[0] + L_RET * _d[0] / _n, 3), round(P_UP[1] + L_RET * _d[1] / _n, 3))


def ext(th):
    q = rotp(P0, th)
    return math.hypot(T[0] - q[0], T[1] - q[1]) - L_RET


E0 = ext(0.0)
_u = ((T[0] - P0[0]) / (E0 + L_RET), (T[1] - P0[1]) / (E0 + L_RET))
U0 = (_u[0], 0.0, _u[1])      # 실린더 로컬 +X(클레비스 쪽) = 세계 U0


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4), "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, base, h, axis, op, tg=None, name=None):
    p = {"radius": r, "height": round(h, 4), "base": [round(v, 4) for v in base], "axis": axis, "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


def cz(r, x, y, z0, z1, op, tg=None, name=None):
    return cyl(r, [x, y, z0], z1 - z0, [0, 0, 1], op, tg, name)


def cy(r, x, z, y0, y1, op, tg=None, name=None):
    return cyl(r, [x, y0, z], y1 - y0, [0, 1, 0], op, tg, name)


def cx(r, y, z, x0, x1, op, tg=None, name=None):
    return cyl(r, [x0, y, z], x1 - x0, [1, 0, 0], op, tg, name)


def mat_assign(bodies, m):
    return C("material.assign", bodies=bodies, material=m)


# ---------- 부품 이름 ----------
BASE, CYLB = "P_M02_BASE", "P_M02_CYLBRKT"
ARM_N, ARM_P, FRONT, TIE = "P_M02_ARM_SIDE_N", "P_M02_ARM_SIDE_P", "P_M02_FRONT", "P_M02_ARM_TIE"
WHEEL, TREAD, SNS = "P_M02_WHEEL", "P_M02_WHEEL_TREAD", "P_M02_SNS_BRKT"
DISK, SHAFT, HSG, DBASE = "P_M02_DISK", "P_M02_DISK_SHAFT", "P_M02_DISK_HSG", "P_M02_DISK_BASE"
SERVO, GEAR = "STEP대기_MHMF022L1U2M", "STEP대기_VRXF-PB-60-10"
DC = (-175.0, 0.0)            # 원판 중심

BEAM_B = [(-310, 140), (-310, 180), (-160, 140), (-160, 180)]
BRK_B = [(-176, 24), (-148, -24)]
HSG_B = [(DC[0] + 38 * math.cos(math.radians(a)), 38 * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
DB_B = [(-285, 120), (-285, -120), (-65, 120), (-65, -120)]
DISK_B = [(DC[0] + 18 * math.cos(math.radians(a)), 18 * math.sin(math.radians(a))) for a in (90, 210, 330)]
GEAR_B = [(24.749 * sy, 70 + 24.749 * sz) for sy in (-1, 1) for sz in (-1, 1)]   # (Y, Z) P.C.D 70


def stage_prep():
    return [C("joint.drive", joint="J_U4_PRESS", value=0, quiet=True),
            C("joint.delete", joint="J_U4_PRESS"),
            C("joint.create", type="revolute", name="J_U4_PRESS", flip=True, limits=[[TH_LO, TH_UP]], quiet=True,
              a={"occurrence": "U4_WHEEL_N", "point": [PIV[0], 0, PIV[1]], "z": [0, -1, 0]},
              b={"occurrence": "U4_PRESS", "point": [PIV[0], 0, PIV[1]], "z": [0, -1, 0]}),
            C("solid.remove", bodies=["U4_MOUNT", "U4_HOLDER", "U4_DRIVE", "U4_WHEEL_TIRE", "U4_DISK", "U4_DISK_BRG"]),
            C("material.create", name="A5052", density_g_cm3=2.68, color="#b8c0c8"),
            C("material.create", name="A6061", density_g_cm3=2.70, color="#aab4be"),
            C("material.create", name="Urethane_A70", density_g_cm3=1.20, color="#d9a33a")]


def arc_slot(c, p, r_half_deg=5.0, w=5.5):
    a0 = math.atan2(p[1] - c[1], p[0] - c[0]) - math.radians(r_half_deg)
    R = math.hypot(p[0] - c[0], p[1] - c[1])
    st = [round(c[0] + R * math.cos(a0), 4), round(c[1] + R * math.sin(a0), 4)]
    return C("sketch.slot.arc_center", center=list(c), start=st, sweep=2 * r_half_deg, width=w)


def stage_fixed():
    s = []
    # BASE: YZ 단면 L을 X -330 -> -140 으로 밈, 세운 다리 X -325~-280 만 남김
    s += [C("sketch.create", plane={"origin": [-330, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02_BASE"),
          C("sketch.line", points=[[-60, 50], [-52, 50], [-52, 242], [200, 242], [200, 250], [-60, 250]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M02_BASE", distance=190, operation="new", body_name=BASE),
          box(None, -331, -325, -61, -51, 49, 242, "cut", [BASE]),
          box(None, -280, -139, -61, -51, 49, 242, "cut", [BASE])]
    # 보 밑 다리 원호 장공 4(바퀴 수직축 (-100, 0) 둘레 ±5°)
    s += [C("sketch.create", plane={"origin": [0, 0, 251], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_M02_BASE_SLOT")]
    s += [arc_slot((-100.0, 0.0), p) for p in BEAM_B]
    s += [C("sketch.finish"), C("solid.extrude", sketch="SK_M02_BASE_SLOT", distance=10, direction="negative", operation="cut", targets=[BASE])]
    s += [box(None, -179, -145, -15, 15, 241, 251, "cut", [BASE])]                  # 실린더 통과 장공 34x30
    s += [cz(2.1, x, y, 241, 251, "cut", [BASE]) for (x, y) in BRK_B]               # 브래킷 M5 탭
    s += [cy(6.0, PIV[0], PIV[1], -61, -51, "cut", [BASE])]                          # 피벗 Ø12 H8
    s += [cz(2.1, x, y, 249, 262, "cut", ["U1_BEAM"]) for (x, y) in BEAM_B]          # U1_BEAM 밑면 M5 탭 깊이 12
    # CYLBRKT(SUS304 t4 용접): 밑판 + 귀 2(위 핀 Ø9)
    s += [box(CYLB, -182, -142, -30, 30, 250, 254),
          box(None, -179, -145, -15, 15, 249, 255, "cut", [CYLB]),
          box(None, T[0] - 10, T[0] + 10, 15.5, 19.5, 253, 336, "join", [CYLB]),
          box(None, T[0] - 10, T[0] + 10, -19.5, -15.5, 253, 336, "join", [CYLB]),
          cy(4.5, T[0], T[1], -20, 20, "cut", [CYLB])]
    s += [cz(2.75, x, y, 249, 255, "cut", [CYLB]) for (x, y) in BRK_B]
    # 원판 받침판·하우징(고정)
    s += [box(DBASE, -300, -50, -135, 135, -48, -40),
          cz(31, DC[0], 0, -49, -39, "cut", [DBASE])]
    s += [cz(2.1, x, y, -49, -39, "cut", [DBASE]) for (x, y) in HSG_B]
    s += [cz(2.75, x, y, -49, -39, "cut", [DBASE]) for (x, y) in DB_B]
    s += [cz(2.1, x, y, -41, -28, "cut", ["U2_PLATE"]) for (x, y) in DB_B]           # U2_PLATE 밑면 M5 탭
    s += [cz(45, DC[0], 0, -56, -48, "new", name=HSG),
          cz(30, DC[0], 0, -48, -24, "join", [HSG]),
          cz(21, DC[0], 0, -57, -23, "cut", [HSG])]
    s += [cz(2.75, x, y, -57, -47, "cut", [HSG]) for (x, y) in HSG_B]
    s += [mat_assign([BASE, CYLB, DBASE], "SUS304"), mat_assign([HSG], "A5052"),
          C("component.move_bodies", bodies=[BASE, CYLB, DBASE, HSG], component="U4_WHEEL_N")]
    return s


def stage_lever():
    s = []
    prof = [[-320, 40], [-120, 40], [-120, 107], [-145, 107], [-145, 132], [-175, 132], [-175, 107],
            [-250, 107], [-250, 126], [-280, 126], [-280, 107], [-320, 107]]
    for nm, y0 in ((ARM_N, -31), (ARM_P, 37)):
        sk = "SK_" + nm
        s += [C("sketch.create", plane={"origin": [0, y0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name=sk),
              C("sketch.line", points=prof, closed=True), C("sketch.finish"),
              C("solid.extrude", sketch=sk, distance=6, operation="new", body_name=nm)]
    arms = [ARM_N, ARM_P]
    s += [cy(8.0, PIV[0], PIV[1], -38, 38, "cut", arms),             # 부시 Ø16
          cy(4.5, P0[0], P0[1], -38, 38, "cut", arms)]               # 로드 핀 Ø9(실물 I-020B 구멍)
    s += [cy(2.75, x, z, -38, 38, "cut", arms) for (x, z) in ((-126, 55), (-126, 85), (-265, 111))]
    # 앞판
    s += [box(FRONT, -132, -120, -31, 31, 30, 110),
          cx(25, 0, 70, -133, -129, "cut", [FRONT]),
          cx(9, 0, 70, -133, -119, "cut", [FRONT])]
    s += [cx(2.75, y, z, -133, -119, "cut", [FRONT]) for (y, z) in GEAR_B]
    s += [cy(2.1, -126, z, -32, -19, "cut", [FRONT]) for z in (55, 85)]
    s += [cy(2.1, -126, z, 19, 32, "cut", [FRONT]) for z in (55, 85)]
    # 뒤 막대
    s += [box(TIE, -275, -255, -31, 31, 101, 121),
          cy(2.1, -265, 111, -32, -19, "cut", [TIE]), cy(2.1, -265, 111, 19, 32, "cut", [TIE])]
    # 감속기·서보 임시 형상(E-10)
    s += [box(GEAR, -207, -132, -30, 30, 40, 100),
          cx(25, 0, 70, -132, -129, "join", [GEAR]),
          cx(8, 0, 70, -129, -97, "join", [GEAR]),
          cx(5.75, 0, 70, -208, -177, "cut", [GEAR])]
    s += [cx(2.1, y, z, -144, -132, "cut", [GEAR]) for (y, z) in GEAR_B]
    s += [box(SERVO, -287, -207, -30, 30, 40, 100),
          cx(5.5, 0, 70, -207, -177, "join", [SERVO])]
    # 센서 브래킷 t2: YZ 단면 L을 X -132 -> -115, 세운 쪽 X -120 넘는 부분 잘라냄, 센서 탭
    s += [C("sketch.create", plane={"origin": [-132, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02_SNS"),
          C("sketch.line", points=[[-95, 41], [-37, 41], [-37, 95], [-39, 95], [-39, 43], [-95, 43]], closed=True),
          C("sketch.finish"),
          C("solid.extrude", sketch="SK_M02_SNS", distance=17, operation="new", body_name=SNS),
          box(None, -120, -114, -39.5, -36.5, 43, 96, "cut", [SNS]),
          box(None, -117.5, -115.5, -94, -66, 25, 42, "join", [SNS])]
    s += [cy(2.75, -126, z, -40, -36, "cut", [SNS]) for z in (55, 85)]
    s += [cx(1.6, -80, z, -118, -115, "cut", [SNS]) for z in (27.5, 37.5)]
    # 바퀴: 허브 A6061 + 우레탄 A70 t10
    s += [cx(50, 0, 70, -112.5, -87.5, "new", name=WHEEL),
          cx(18, 0, 70, -119, -112.5, "join", [WHEEL]),
          cx(8, 0, 70, -120, -86, "cut", [WHEEL]),
          cx(60, 0, 70, -112.5, -87.5, "new", name=TREAD),
          cx(50, 0, 70, -113, -87, "cut", [TREAD])]
    s += [mat_assign([ARM_N, ARM_P, FRONT, SNS], "SUS304"), mat_assign([TIE], "A5052"),
          mat_assign([WHEEL], "A6061"), mat_assign([TREAD], "Urethane_A70"),
          mat_assign([GEAR, SERVO], "Steel"),
          C("component.move_bodies", bodies=[ARM_N, ARM_P, FRONT, TIE, GEAR, SERVO, SNS], component="U4_PRESS"),
          C("component.move_bodies", bodies=[WHEEL, TREAD], component="U4_WHEEL")]
    return s


def stage_disk():
    s = [C("component.create", name="U4_DISK", parent="root", activate=False),
         cz(125, DC[0], 0, -12, 0, "new", name=DISK),
         cz(10, DC[0], 0, -13, 1, "cut", [DISK])]
    s += [cz(4.75, x, y, -5.5, 1, "cut", [DISK]) for (x, y) in DISK_B]
    s += [cz(2.75, x, y, -13, 1, "cut", [DISK]) for (x, y) in DISK_B]
    s += [cz(10, DC[0], 0, -62, -2, "new", name=SHAFT),
          cz(25, DC[0], 0, -22, -12, "join", [SHAFT])]
    s += [cz(2.1, x, y, -23, -11, "cut", [SHAFT]) for (x, y) in DISK_B]
    s += [mat_assign([DISK], "A5052"), mat_assign([SHAFT], "S45C"),
          C("component.move_bodies", bodies=[DISK, SHAFT], component="U4_DISK"),
          C("joint.create", type="revolute", name="J_U4_DISK", flip=True, quiet=True, limits=[[-72000, 72000]],
            a={"occurrence": "U4_WHEEL_N", "point": [DC[0], 0, 0], "z": [0, 0, 1]},
            b={"occurrence": "U4_DISK", "point": [DC[0], 0, 0], "z": [0, 0, 1]})]
    return s


def mat3(cols, t):
    """cols = 로컬 X·Y·Z 축의 세계 방향(열), t = 로컬 원점의 세계 위치 -> 행 우선 3x4."""
    return [round(cols[j][i], 9) if j < 3 else round(t[i], 4) for i in range(3) for j in range(4)]


def mat_loc(cols, t):
    return [round(v, 9) for i in range(3) for v in (cols[0][i], cols[1][i], cols[2][i], t[i])]


def cyl_cols():
    ux, _, uz = U0
    return [(ux, 0.0, uz), (uz, 0.0, -ux), (0.0, 1.0, 0.0)]


def stage_cyl():
    """실물 STEP 하위 부품을 그대로 U4_CYL·U4_ROD로 쓴다(바디 옮김 뒤 빈 STEP 컴포넌트는 지울 수 없어서, 모델링부 보고서 3절).
    joint.create는 STEP 하위 부품의 로컬 x축으로 90° 돌려 버려 joint.as_built로 맺는다."""
    cols = cyl_cols()
    Tw = [T[0], 0.0, T[1]]
    t_cyl = tuple(Tw[i] - 117.0 * U0[i] for i in range(3))
    t_re = tuple(Tw[i] - L_RET * U0[i] for i in range(3))
    zr = [-U0[0], 0, -U0[2]]
    return [C("file.insert_step", path=STEP + "CDM2C20-25Z/CDM2C20-25Z.stp", name="CDM2C20-25Z", matrix=mat_loc(cols, t_cyl)),
            C("body.rename", body="CDM2C20-25Z(0)_BODY", name="CDM2C20-25Z_BODY"),
            C("body.rename", body="CM2C20-25Z(0_0)_ROD", name="CDM2C20-25Z_ROD"),
            C("body.rename", body="NT-02_CM2(20)", name="CDM2C20-25Z_NUT"),
            C("body.rename", body="CM-C020B_Z(20_C_0_0)_FITTING", name="CDM2C20-25Z_CLEVIS"),
            C("component.unlock", component="CDM2C20-25Z"),
            C("component.rename", component="CDM2C20-25Z(0)_BODY", name="U4_CYL"),
            C("component.rename", component="CM2C20-25Z(0_0)_ROD", name="U4_ROD"),
            C("component.rename", component="NT-02_CM2(20)", name="U4_ROD_NUT"),
            C("component.rename", component="CM-C020B_Z(20_C_0_0)_FITTING", name="U4_CYL_CLEVIS"),
            C("component.metadata.set", component="CDM2C20-25Z", part_number="CDM2C20-25Z", bom_type="purchased",
              description="SMC CM2 Ø20 st25 single clevis (design CDM2C20-25AZ, Misumi STEP CDM2C20-25Z)"),
            C("component.metadata.set", component="U4_CYL", bom_type="inseparable"),
            C("component.metadata.set", component="U4_ROD", bom_type="inseparable"),
            C("component.metadata.set", component="U4_ROD_NUT", bom_type="inseparable"),
            C("component.metadata.set", component="U4_CYL_CLEVIS", bom_type="inseparable"),
            C("file.insert_step", path=STEP + "I-020B/I-020B.stp", name="I-020B_M02", matrix=mat_loc(cols, t_re)),
            C("body.rename", body="I-020B_CM3", name="I-020B_M02"),
            C("component.metadata.set", component="I-020B_M02", part_number="I-020B", bom_type="purchased"),
            C("material.assign", bodies=["CDM2C20-25Z_BODY", "CDM2C20-25Z_CLEVIS"], material="Aluminum"),
            C("material.assign", bodies=["CDM2C20-25Z_ROD", "CDM2C20-25Z_NUT", "I-020B_M02"], material="Steel"),
            C("joint.rigid_group", occurrences=["U4_CYL:1", "U4_CYL_CLEVIS:1"]),
            C("joint.rigid_group", occurrences=["U4_ROD:1", "U4_ROD_NUT:1", "I-020B_M02:1"]),
            C("joint.as_built", type="revolute", name="J_U4_CYL_PIN", a="U4_WHEEL_N:1", b="U4_CYL:1",
              at={"occurrence": "U4_WHEEL_N:1", "point": Tw, "z": [0, 1, 0]}, limits=[[-15, 15]], quiet=True),
            C("joint.as_built", type="slider", name="J_U4_CYL_ROD", a="U4_CYL:1", b="U4_ROD:1",
              at={"occurrence": "U4_CYL:1", "point": Tw, "z": zr}, limits=[[0, STROKE]], quiet=True),
            C("joint.drive", joint="J_U4_CYL_ROD", value=round(E0, 4), quiet=True)]


def stage_loop():
    return [C("joint.as_built", type="revolute", name="J_U4_ROD_PIN", a="U4_ROD:1", b="U4_PRESS:1",
              at={"occurrence": "U4_PRESS:1", "point": [P0[0], 0, P0[1]], "z": [0, 1, 0]})]


# ---------- 구매품 ----------
DIR = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}


def bolt_cols(d):
    a = DIR[d]
    ref = (0, 0, 1) if abs(a[2]) < 0.5 else (1, 0, 0)
    # y = ref x a 정규, z = a x y
    y = (ref[1] * a[2] - ref[2] * a[1], ref[2] * a[0] - ref[0] * a[2], ref[0] * a[1] - ref[1] * a[0])
    z = (a[1] * y[2] - a[2] * y[1], a[2] * y[0] - a[0] * y[2], a[0] * y[1] - a[1] * y[0])
    return [a, y, z]


def bolt_list():
    b = []   # (이름, 형번, 방향, 머리 밑면 점, 묶음)
    for i, (x, y) in enumerate(BEAM_B, 1):
        b.append(("CB5-16_M02_%d" % i, "CB5-16", "+Z", (x, y, 242), "U4_WHEEL_N"))
    n = 5
    for (z) in (55, 85):
        b.append(("CB5-16_M02_%d" % n, "CB5-16", "+Y", (-126, -39, z), "U4_PRESS")); n += 1
        b.append(("CB5-16_M02_%d" % n, "CB5-16", "-Y", (-126, 37, z), "U4_PRESS")); n += 1
    b.append(("CB5-16_M02_%d" % n, "CB5-16", "+Y", (-265, -37, 111), "U4_PRESS")); n += 1
    b.append(("CB5-16_M02_%d" % n, "CB5-16", "-Y", (-265, 37, 111), "U4_PRESS")); n += 1
    for (x, y) in HSG_B:
        b.append(("CB5-16_M02_%d" % n, "CB5-16", "+Z", (round(x, 4), round(y, 4), -56), "U4_WHEEL_N")); n += 1
    for (x, y) in DB_B:
        b.append(("CB5-16_M02_%d" % n, "CB5-16", "+Z", (x, y, -48), "U4_WHEEL_N")); n += 1
    for (x, y) in DISK_B:
        b.append(("CB5-16_M02_%d" % n, "CB5-16", "-Z", (round(x, 4), round(y, 4), -5.5), "U4_DISK")); n += 1
    for i, (y, z) in enumerate(GEAR_B, 1):
        b.append(("CB5-20_M02_%d" % i, "CB5-20", "-X", (-120, round(y, 4), round(z, 4)), "U4_PRESS"))
    for i, (x, y) in enumerate(BRK_B, 1):
        b.append(("CB5-12_M02_%d" % i, "CB5-12", "-Z", (x, y, 254), "U4_WHEEL_N"))
    return b


def stage_purchased():
    s, groups = [], {"U4_WHEEL_N": ["U4_WHEEL_N:1", "CDM2C20-25Z:1"], "U4_PRESS": ["U4_PRESS:1"], "U4_DISK": ["U4_DISK:1"]}
    # 매트 유무 센서(머리 감지면 로컬 -X -> 세계 -Z, 두께 로컬 Z -> 세계 -X)
    s += [C("file.insert_step", path=STEP + "E32-D36P1_2M/E32-D36P1_2M.stp", name="E32-D36P1_2M_M02",
            matrix=mat_loc([(0, 0, 1), (0, 1, 0), (-1, 0, 0)], (-113, -80, 27.5))),
          C("body.rename", body="NONE", name="E32-D36P1_2M_M02"),
          C("component.metadata.set", component="E32-D36P1_2M_M02", part_number="E32-D36P1 2M", bom_type="purchased")]
    groups["U4_PRESS"].append("E32-D36P1_2M_M02:1")
    # 6004ZZ ×2 (로컬 +X -> 세계 +Z)
    for i, z0 in ((1, -36), (2, -56)):
        nm = "6004ZZ_M02_%d" % i
        s += [C("file.insert_step", path=STEP + "6004ZZ/6004ZZ.stp", name=nm, matrix=mat_loc([(0, 0, 1), (0, 1, 0), (-1, 0, 0)], (DC[0], 0, z0)))]
        for part, short in (("Outer ring", "OUTER"), ("Inner ring", "INNER"), ("Shield1", "SHIELD1"), ("Shield2", "SHIELD2")):
            s.append(C("body.rename", body="6004ZZ " + part, name="%s_%s" % (nm, short)))
        s.append(C("component.metadata.set", component=nm, part_number="6004ZZ", bom_type="purchased"))
        s.append(C("material.assign", bodies=["%s_%s" % (nm, k) for k in ("OUTER", "INNER", "SHIELD1", "SHIELD2")], material="Steel"))
        groups["U4_WHEEL_N"].append(nm + ":1")
    bodies = []
    for (nm, pn, d, at, g) in bolt_list():
        s += [C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=nm, matrix=mat_loc(bolt_cols(d), at)),
              C("body.rename", body="Cut-Extrude1", name=nm),
              C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased")]
        bodies.append(nm)
        groups[g].append(nm + ":1")
    s += [C("material.assign", bodies=bodies, material="SCM435")]
    s += [C("joint.rigid_group", occurrences=v) for v in groups.values()]
    return s


# ---------- 접촉 추종 키(수정 1회차) ----------
sys.path.insert(0, ROOT)
MATS = {"L": (1500.0, 1500.0), "S": (300.0, 200.0), "G": (1200.0, 1200.0)}
G_A, G_W, G_D, G_Y = 1200.0, 25.0, 150.0, -300.0
G_R = G_W / 2
WING, OVL = 10.0, 30.0


def rot2(th, v):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def h_at(k, p):
    a, b = MATS[k]
    px, py = p
    h = None
    in_mat = abs(px) <= a / 2 and abs(py) <= b / 2
    in_out = abs(px) <= a / 2 + 1 and abs(py) <= b / 2 + 1
    inner = abs(px) < a / 2 - WING and abs(py) < b / 2 - WING
    if k == "G":
        xb = a / 2 - G_D + G_R
        ds = abs(py - G_Y) if px >= xb else math.hypot(px - xb, py - G_Y)
        if in_mat and ds >= G_R:
            h = 10.0
        if in_out and ds >= G_R - 1 and not (inner and ds >= G_R + WING):
            h = 11.0
    else:
        if in_mat:
            h = 10.0
        if in_out and not inner:
            h = 11.0
    if a / 2 - WING <= px <= a / 2 + 2 and -OVL <= py <= 0:
        h = 12.0
    return h


FOOT = [(-112.5 + 2.5 * i, -16 + 0.5 * j) for i in range(11) for j in range(65)]


def ztop_eff(k, z):
    best = 10.0
    for (wx, wy) in FOOT:
        p = rot2(-z["th"], (wx - z["cx"], wy - z["cy"]))
        h = h_at(k, p)
        if h is None:
            continue
        drop = 60.0 - math.sqrt(3600.0 - wy * wy)
        best = max(best, h - drop)
    return best


def theta_of(zt):
    if zt <= 10.0 + 1e-9:
        return 0.0
    if zt <= 11.0 + 1e-9:
        return 0.306
    if zt <= 12.0 + 1e-9:
        return 0.611
    return math.ceil(math.degrees(math.asin((zt - 10.0) / 187.5)) * 1000) / 1000


def press_keys():
    paths = json.load(open(os.path.join(ROOT, "out", "prep_v2", "paths.json"), encoding="utf-8"))["paths"]
    res, stat = {}, {}
    for nm, info in paths.items():
        k = nm[0]
        P = info["poses"]
        zt = [ztop_eff(k, z) for z in P]
        vals = []
        for i, z in enumerate(P):
            if z["np"] > 0:
                vals.append(TH_UP)
                continue
            m = max(zt[max(0, i - 1):i + 2])
            vals.append(theta_of(m))
        res["CYCLE_" + nm] = vals
        stat["CYCLE_" + nm] = {"steps": len(P) - 1, "lifted": sum(1 for v in vals if v == TH_UP),
                               "0": sum(1 for v in vals if v == 0.0), "0.306": sum(1 for v in vals if v == 0.306),
                               "0.611": sum(1 for v in vals if v == 0.611),
                               "other": sorted(set(v for v in vals if v not in (0.0, 0.306, 0.611, TH_UP)))}
    return res, stat


def thin(pts, tol=1e-4):
    """선형 보간으로 같은 값이 나오는 가운데 점을 뺀다(연구는 점 사이를 선형 보간 — 움직임 그대로)."""
    if len(pts) <= 2:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if c[0] == a[0]:
            continue
        v = a[1] + (c[1] - a[1]) * (b[0] - a[0]) / (c[0] - a[0])
        if abs(v - b[1]) > tol:
            out.append(b)
    out.append(pts[-1])
    return out


def stage_studies(keys):
    """motion.study 편집은 keys 전체를 바꾼다(모델링부 실측) -> 준비부 연구(prep_v2/study_*.json, v2.0.2와 같음 확인)에서
    J_U4_PRESS 키만 바꿔 전체 키로 다시 준다. 값은 도(회전)·mm."""
    s = []
    for nm in ["REST"] + list(keys.keys()):
        p = json.load(open(os.path.join(ROOT, "out", "prep_v2", "study_%s.json" % nm), encoding="utf-8"))["params"]
        if nm == "REST":
            pts = [[0, TH_UP], [1, TH_UP]]
        else:
            vals = keys[nm]
            pts = [[i, v] for i, v in enumerate(vals)
                   if i == 0 or i == len(vals) - 1 or v != vals[i - 1] or v != vals[i + 1]]
        ks = [{"joint": k["joint"], "points": [[a, round(b, 3)] for a, b in thin(k["points"], 1e-3)]} for k in p["keys"] if k["joint"] != "J_U4_PRESS"]
        ks.append({"joint": "J_U4_PRESS", "points": pts})
        s.append(C("motion.study", study=nm, steps=p["steps"], keys=ks))
    return s


def stage_final():
    # 실린더 후퇴 끝(고리 한계 8.6265°)이 들림 끝 스토퍼다. 한계를 8.626으로 두어 키 8.627이 고리 멈춤 대신 한계로 잘리게 한다
    # (고리 멈춤이면 motion.play가 fraction 0.99994에서 멈춰 다른 조인트도 덜 간다, 모델링부 실측).
    return [C("joint.limits", joint="J_U4_PRESS", min=TH_LO, max=TH_UP_STOP),
            C("joint.drive", joint="J_U4_WHEEL_ROT", value=0, quiet=True),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description", value="M02 mechanism: U4 near wheel - servo+gearhead wheel, pin swing lever, CM2 cylinder, free disk")]


def patch_machine(keys):
    p = os.path.join(ROOT, "machine.json")
    m = json.load(open(p, encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.1.0.sc"
    j = m["joints"]
    j["J_U4_PRESS"] = {"cad": "J_U4_PRESS", "type": "rotate", "unit": "U4_WHEEL_N", "axis": [0, -1, 0],
                       "origin": [PIV[0], 0, PIV[1]], "rest": TH_UP_STOP, "min": TH_LO, "max": TH_UP_STOP,
                       "_note": ("M02(v2.1.0) 핀 스윙 레버(U4_PRESS) 회전, + = 들림. 0 = 바퀴 밑 Z 10(매트 윗면), 8.626 = 들림 끝(조인트 한계; 실린더 후퇴 끝 8.6265가 스토퍼, 바퀴 밑 38.8; 연구 키 8.627은 한계로 잘림), "
                                 "-1.867 = 실린더 나옴 끝(바퀴 밑 3.1). 작동(접촉 추종): theta = asin((z_top-10)/187.5) [deg], 187.5 = 레버 200 - 바퀴 반폭 12.5, "
                                 "소수 셋째 자리 올림 — 매트 10 -> 0, 테이프 11 -> 0.306, 이음매 12 -> 0.611. 실린더 CDM2C20-25Z(J_U4_CYL_PIN·J_U4_CYL_ROD·J_U4_ROD_PIN 닫힌 고리)가 따라감")}
    j["J_U4_WHEEL_ROT"]["unit"] = "U4_WHEEL_N"
    j["J_U4_WHEEL_ROT"]["_note"] = j["J_U4_WHEEL_ROT"]["_note"] + " M02: 바퀴 P_M02_WHEEL(+TREAD), 원점 = 바퀴 중심(J_U4_PRESS 0에서 (-100, 0, 70)), U4_PRESS를 따라 돈다"
    j["J_U4_DISK"] = {"cad": "J_U4_DISK", "type": "rotate", "unit": "U4_WHEEL_N", "axis": [0, 0, 1], "origin": [DC[0], 0, 0],
                      "rest": 0, "min": -72000, "max": 72000, "follower": True,
                      "_note": "M02 밑 자유 회전 원판 P_M02_DISK Ø250(6004ZZ ×2). 구동 없음 — 형상이 회전 대칭이라 간섭 검사에 영향 없음"}
    for nm, d in (("J_U4_CYL_PIN", "실린더 위 핀(U4_WHEEL_N ↔ U4_CYL, 축 Y)"), ("J_U4_CYL_ROD", "실린더 로드 슬라이더(U4_CYL ↔ U4_ROD, 0~25 = 로드 나옴)"),
                  ("J_U4_ROD_PIN", "로드 끝 핀(U4_ROD ↔ U4_PRESS, 고리 닫음)")):
        j[nm] = {"cad": nm, "type": "rotate" if "PIN" in nm else "slide", "unit": "U4_WHEEL_N", "follower": True,
                 "_note": "M02 닫힌 고리 따라감(키 없음, M-07). " + d}
    j["J_U4_CYL_ROD"].update({"min": 0, "max": STROKE, "rest": 0.0})
    u = m["units"]["U4_WHEEL_N"]
    u["parts"] = ["U4_", "P_M02_", "STEP대기_MHMF022L1U2M", "STEP대기_VRXF-PB-60-10", "CDM2C20-25Z_", "I-020B_M02",
                  "6004ZZ_M02_", "E32-D36P1_2M_M02", "CB5-16_M02", "CB5-20_M02", "CB5-12_M02"]
    u["components"] = ["U4_WHEEL_N", "U4_PRESS", "U4_WHEEL", "U4_DISK", "U4_CYL", "U4_ROD"]
    u["_note"] = ("M02(v2.1.0): 고정 U4_WHEEL_N = P_M02_BASE(SUS304 t8 L, U1_BEAM 밑)·P_M02_CYLBRKT(SUS304 t4 용접)·P_M02_DISK_BASE·P_M02_DISK_HSG·6004ZZ ×2. "
                  "U4_PRESS(레버) = ARM_SIDE_N/P·FRONT·ARM_TIE·SNS_BRKT·STEP대기_VRXF-PB-60-10·STEP대기_MHMF022L1U2M·E32-D36P1_2M. U4_WHEEL = P_M02_WHEEL·P_M02_WHEEL_TREAD. "
                  "U4_DISK = P_M02_DISK·P_M02_DISK_SHAFT. U4_CYL·U4_ROD = CDM2C20-25Z + I-020B. 볼트 CB5-16_M02_1~23·CB5-20_M02_1~4·CB5-12_M02_1~2")
    for st in m["states"]:
        jj = st.get("joints", {})
        if "J_U4_PRESS" not in jj:
            continue
        if st["study"] == "REST":
            jj["J_U4_PRESS"] = TH_UP_STOP
        elif st["study"] in keys:
            v = keys[st["study"]][st["step"]]
            jj["J_U4_PRESS"] = TH_UP_STOP if v == TH_UP else v
        else:
            jj["J_U4_PRESS"] = TH_UP if jj["J_U4_PRESS"] > 0 else 0.0
    bl = m["baseline_overlaps"]
    bl.append({"a": "U4_WHEEL(P_M02_WHEEL_TREAD)", "b": "WP_TAPE_*·SEAM_*",
               "reason": "M02 수정 1회차: 접촉 추종 키(테이프 0.306°, 이음매 0.611°)로 바퀴 밑 11.002·12.003 — 겹침 0이어야 한다. 남으면 키 0.310·0.615"})
    bl.append({"a": "CB5-*_M02_*", "b": "탭 구멍 부품", "reason": "나사 물림(Ø5 축 ↔ Ø4.2 탭) 의도된 겹침(M-08)"})
    bl.append({"a": "U4_ROD(CDM2C20-25Z_ROD)", "b": "I-020B_M02", "reason": "로드 끝 나사 물림(같은 리지드 묶음)"})
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


STAGES = [("prep", stage_prep), ("fixed", stage_fixed), ("lever", stage_lever), ("disk", stage_disk),
          ("cyl", stage_cyl), ("loop", stage_loop), ("purchased", stage_purchased)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    keys, kstat = press_keys()
    allc = []
    stages = STAGES + [("studies", lambda: stage_studies(keys)), ("final", stage_final)]
    for i, (nm, f) in enumerate(stages, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v2.0.2.sc", "result": "3D_Modeling/FSAP_v2.1.0.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    geo = {"T_top_pin": T, "P0_rod_pin": P0, "P_up": [round(v, 3) for v in P_UP], "U0": [round(v, 6) for v in U0],
           "ext": {"lo": round(ext(TH_LO), 3), "0": round(E0, 3), "up": round(ext(TH_UP), 3)}, "keys": kstat}
    json.dump(geo, open(os.path.join(OUT, "model", "geom.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(geo, ensure_ascii=False))
    if "--machine" in sys.argv:
        patch_machine(keys)
        print("machine.json patched")


if __name__ == "__main__":
    main()
