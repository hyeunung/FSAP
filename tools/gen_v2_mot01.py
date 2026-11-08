# -*- coding: utf-8 -*-
"""MOT-01 — 모터·감속기 체결 + C-36 실물 교체(v2.6.8 -> v2.7.0) 단계 생성기.
python -X utf8 -B tools/gen_v2_mot01.py -> tools/out/mech_MOT-01/model/stage_*.json

편집 자세: J_U4_PRESS = 0(팔 수평, U4_PRESS 로컬 = 세계), J_U5_LIFT = 0(U5_LIFT·U5_WHEEL 로컬 = 세계, 바퀴 축 Z 70).
지시서 좌표(REST)는 이 자세로 바꿔 쓴다: U4 s -> X = -132 + s, t -> Z = 70 + t. U5W Z(REST) - 30.
STEP 행렬은 활성 컴포넌트 로컬(=이 자세에서 세계). 볼트 STEP 로컬 +X = 머리 -> 끝, x 0 = 머리 자리면.
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cx, cy, cz, mat_assign, T as CLV, P0 as KNK  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
STEP = PRJ + "/purchased-step/"
OUT = os.path.join(ROOT, "out", "mech_MOT-01", "model")
R = 24.749                                   # P.C.D 70 / 2 / sqrt2
SQ = [(a * R, b * R) for a in (-1, 1) for b in (-1, 1)]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mat(lx, ly, t):
    lz = cross(lx, ly)
    return [round(v, 9) for i in range(3) for v in (lx[i], ly[i], lz[i], t[i])]


def mat_z(lz, ly, t):
    """로컬 +Z·+Y를 주고 X = Y x Z."""
    lx = cross(ly, lz)
    return [round(v, 9) for i in range(3) for v in (lx[i], ly[i], lz[i], t[i])]


def perp(d):
    return (0.0, 1.0, 0.0) if abs(d[1]) < 0.5 else (-d[1], 0.0, 0.0)


def bolt_ins(pn, name, d, seat, body="Cut-Extrude1", mat_name="SCM435", desc=None):
    s = [C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=name, matrix=mat(d, perp(d), seat)),
         C("body.rename", body=body, name=name),
         C("component.metadata.set", component=name, part_number=pn, bom_type="purchased", description=desc or ""),
         C("material.assign", bodies=[name], material=mat_name)]
    return s


def copies(name, seat0, seats):
    return [C("occurrence.copy", occurrence=name + ":1", in_place=True,
              translate=[round(p[i] - seat0[i], 4) for i in range(3)]) for p in seats]


def bolt_set(pn, name, d, seats, comp, desc, body="Cut-Extrude1", mat_name="SCM435"):
    s = [C("component.activate", component=comp)]
    s += bolt_ins(pn, name, d, seats[0], body, mat_name, desc)
    s += copies(name, seats[0], seats[1:])
    return s


# ------------------------------------------------------------------ A. 지우기(STEP대기 6 바디)
OLD = ["STEP대기_MHMF022L1U2M", "STEP대기_MHMF022L1U2M_U5X", "STEP대기_MHMF022L1U2M_U5W",
       "STEP대기_VRXF-PB-60-10", "STEP대기_VRXF-PB-60-10_U5X", "STEP대기_VRXF-PB-60-10_U5W"]


def stage_remove():
    return [C("solid.remove", bodies=OLD)]


# ------------------------------------------------------------------ B. 실물 STEP 넣기
X, Y, Z = (1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)
NX, NY, NZ = (-1.0, 0, 0), (0, -1.0, 0), (0, 0, -1.0)
STEPS = {
    # 이름: (형번 폴더, 컴포넌트, 로컬 +Z, 로컬 +Y, 원점)
    "PGX62-H-10_M02": ("PGX62-H-10", "U4_PRESS", X, Z, (-132.0, 0, 70.0)),
    "HG-KR23_M02": ("HG-KR23", "U4_PRESS", X, Z, (-211.0, 0, 70.0)),
    "PGX62-H-10_M03W": ("PGX62-H-10", "U5_LIFT", X, Z, (-1832.0, 0, 70.0)),
    "HG-KR23_M03W": ("HG-KR23", "U5_LIFT", X, NZ, (-1911.0, 0, 70.0)),
    "PGX62-H-10_M03X": ("PGX62-H-10", "U5_WHEEL_F", Y, Z, (-2220.0, 82.0, 390.0)),
    "HG-KR23_M03X": ("HG-KR23", "U5_WHEEL_F", Y, Z, (-2220.0, 3.0, 390.0)),
    "HG-KR43_U3": ("HG-KR43", "U3_HEAD", NX, Z, (430.0, 0, -90.0)),
}


def stage_step(name, ly=None):
    pn, comp, lz, ly0, t = STEPS[name]
    return [C("component.activate", component=comp),
            C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=name, matrix=mat_z(lz, ly or ly0, t)),
            C("component.activate", component=0)]


# PGX 바디(넣은 순서) -> 이름 끝. None = 중복이라 지움
PGX_ORDER = ["CASE", "KSB_O", "SHAFT", "KEY", "INPUT", "BUSH", "KSB_I", None, None, "ADAPTER",
             "PLUG1", "PLUG2", "ABOLT1", "ABOLT2", "ABOLT3", "ABOLT4", "CLAMP_BOLT", "CLAMP"]
PGX_MAT = {"CASE": "Steel", "SHAFT": "S45C", "KEY": "S45C", "INPUT": "Steel", "BUSH": "Aluminum", "ADAPTER": "Aluminum",
           "KSB_O": "Default", "KSB_I": "Default", "PLUG1": "Steel", "PLUG2": "Steel", "ABOLT1": "SCM435", "ABOLT2": "SCM435",
           "ABOLT3": "SCM435", "ABOLT4": "SCM435", "CLAMP_BOLT": "SCM435", "CLAMP": "Steel"}
DESC = {
    "PGX62-H-10_M02": "Misumi(Shinpo) PGX62-H-10 planetary 1/10, adapter 7MP62A machined for HG-KR23 (C-36). U4 needle-side wheel, output face s 0 (MOT-01)",
    "PGX62-H-10_M03W": "Misumi(Shinpo) PGX62-H-10 planetary 1/10, adapter for HG-KR23 (C-36). U5 far-side wheel (lift), output face X -1832 (MOT-01)",
    "PGX62-H-10_M03X": "Misumi(Shinpo) PGX62-H-10 planetary 1/10, adapter for HG-KR23 (C-36). U5 carriage X drive, output face Y 82, pulley N16 (MOT-01)",
    "HG-KR23_M02": "Mitsubishi HG-KR23 200 W servo, straight shaft (C-36), U4 wheel (MOT-01)",
    "HG-KR23_M03W": "Mitsubishi HG-KR23 200 W servo, straight shaft (C-36), U5 wheel (MOT-01)",
    "HG-KR23_M03X": "Mitsubishi HG-KR23 200 W servo, straight shaft (C-36), U5 carriage X (MOT-01)",
    "HG-KR43_U3": "Mitsubishi HG-KR43 400 W servo, straight shaft (C-36), U3 867 lower shaft 1:1 electronic sync (MOT-01)",
}


def stage_pgx_names(name, created, wheel_comp=None):
    """created = file.insert_step 결과의 created_bodies(넣은 순서)."""
    s, dup = [], []
    for raw, suf in zip(created, PGX_ORDER):
        if suf is None:
            dup.append(raw)
        else:
            s.append(C("body.rename", body=raw, name="%s_%s" % (name, suf)))
    s.insert(0, C("solid.remove", bodies=dup))
    for m in sorted(set(PGX_MAT.values())):
        s.append(C("material.assign", bodies=["%s_%s" % (name, k) for k, v in PGX_MAT.items() if v == m], material=m))
    s.append(C("component.metadata.set", component=name, part_number="PGX62-H-10", bom_type="purchased", description=DESC[name]))
    if wheel_comp:
        s.append(C("component.move_bodies", bodies=[name + "_SHAFT", name + "_KEY"], component=wheel_comp))
    return s


def stage_motor_names(name, created):
    pn = STEPS[name][0]
    return [C("body.rename", body=created[0], name=name), C("material.assign", bodies=[name], material="Steel"),
            C("component.metadata.set", component=name, part_number=pn, bom_type="purchased", description=DESC[name])]


# ------------------------------------------------------------------ C. 가공품 고치기
ARM_N, ARM_P, FRONT2, WHEEL2 = "P_M02_ARM_SIDE_N", "P_M02_ARM_SIDE_P", "P_M02_FRONT", "P_M02_WHEEL"
LSN, LSP, FRONT3, WHEEL3 = "P_M03_LIFT_SIDE_N", "P_M03_LIFT_SIDE_P", "P_M03_FRONT", "P_M03_WHEEL"
DRV, ISH = "P_M03_DRV_BRKT", "P_M03_IDLER_SHAFT"


def front_mods(nm, x0):
    """앞판 X x0~x0+12, 축 (Y 0, Z 70): Ø50 관통, Ø5.5 4개 -> M5 관통 탭(Ø4.2)."""
    s = [cx(25.02, 0, 70, x0 - 1, x0 + 13, "cut", [nm])]   # Ø50 H8 (+0.039), 기존 Ø50 자리파기와 같은 면 피함
    s += [cx(2.85, y, 70 + z, x0, x0 + 12, "join", [nm]) for y, z in SQ]
    s += [cx(2.1, y, 70 + z, x0 - 1, x0 + 13, "cut", [nm]) for y, z in SQ]
    return s


def wheel_mods(nm, dx):
    """바퀴 허브(U4 X -119~-87.5 + dx): 막힌 구멍 s 13~36, 키홈 5 x 2.3(+Z), 막벽 Ø5.5 + 자리파기 Ø9.5 x 5."""
    return [cx(8.1, 0, 70, -96 + dx, -87.5 + dx, "join", [nm]),
            box(None, -119.5 + dx, -96 + dx, -2.5, 2.5, 76.0, 80.3, "cut", [nm]),
            cx(2.75, 0, 70, -97 + dx, -87 + dx, "cut", [nm]),
            cx(4.75, 0, 70, -92.5 + dx, -87 + dx, "cut", [nm])]


def stage_u4_mods():
    # 움직이는 유닛 바디의 특징은 그 컴포넌트를 활성으로 두고 만든다 — 루트에서 만들면 세계 좌표로 남아 자세가 바뀔 때마다
    # 다시 계산되며 어긋난다(실측: REST에서 앞판·옆판에 떨어진 조각, joint.drive 1회 140~290 s). MOT-01 1회차는 component.move_features로 옮김.
    s = [C("component.activate", component="U4_PRESS"), box(None, -214, -134, -33, -30, 39, 104, "cut", [ARM_N]),
         box(None, -214, -134, 30, 33, 39, 104, "cut", [ARM_P]),
         C("solid.fillet", edges=[[-214, -32, 104], [-134, -32, 104]], radius=3),
         C("solid.fillet", edges=[[-214, 32, 104], [-134, 32, 104]], radius=3)]
    s += front_mods(FRONT2, -132) + [C("component.activate", component="U4_WHEEL")] + wheel_mods(WHEEL2, 0.0) + [C("component.activate", component=0)]
    return s


def stage_u5_mods():
    s = [C("component.activate", component="U5_LIFT"), box(None, -1914, -1834, -33, -30, 29, 104, "cut", [LSN]),
         box(None, -1914, -1834, 30, 33, 29, 104, "cut", [LSP])]
    s += front_mods(FRONT3, -1832) + [C("component.activate", component="U5_WHEEL")] + wheel_mods(WHEEL3, -1700.0) + [C("component.activate", component="U5_WHEEL_F")]
    # 대차 X 구동 브래킷: 웨브 Y 86 -> 82, Ø50 관통, M5 관통 탭 4
    s += [box(None, -2280, -2160, 82, 86, 330, 450, "join", [DRV]),
          cy(25.02, -2220, 390, 81, 91, "cut", [DRV])]
    s += [cy(2.85, -2220 + a, 390 + b, 86, 90, "join", [DRV]) for a, b in SQ]
    s += [cy(2.1, -2220 + a, 390 + b, 81, 91, "cut", [DRV]) for a, b in SQ]
    # 아이들러 축 Y 82~117 -> 90~115, 양 끝 M5 탭
    s += [box(None, -396, -384, 81, 90, 383, 397, "cut", [ISH]),
          box(None, -396, -384, 115, 118, 383, 397, "cut", [ISH]),
          cy(2.1, -390, 390, 89.9, 100, "cut", [ISH]),
          cy(2.1, -390, 390, 103, 115.1, "cut", [ISH]), C("component.activate", component=0)]
    return s


def stage_u3_mods():
    B = "P_U3_LDRV_BRKT"
    s = [C("component.activate", component="U3_HEAD"),
         box(None, 368, 501, -61, 61, -201, -59, "cut", ["U3_LOWER_DRIVE"]),
         box(B, 418, 430, -45, 45, -140, -50),
         box(None, 418, 545, 45, 53, -140, -50, "join", [B]),
         box(None, 418, 545, -53, -45, -140, -50, "join", [B]),
         box(None, 537, 545, -53, 53, -172, -50, "join", [B]),
         cx(25.02, 0, -90, 417, 431, "cut", [B])]
    s += [cx(2.1, a, -90 + b, 417, 431, "cut", [B]) for a, b in SQ]
    s += [cx(2.75, y, z, 536, 546, "cut", [B]) for y in (-38, 38) for z in (-112, -152)]
    s += [cx(23, 0, -90, 368, 412, "new", name="STEP대기_SCXW46-14-15"),
          cx(7, 0, -90, 390, 413, "cut", ["STEP대기_SCXW46-14-15"]),
          mat_assign([B], "A6061"), mat_assign(["STEP대기_SCXW46-14-15"], "Aluminum"),
          C("component.activate", component=0)]
    return s


# ------------------------------------------------------------------ D. 새 핀·와셔
def stage_pins(mp_r):
    """mp_r = MPFZ12-10 바깥 반지름(실측) — 팔 피벗 구멍을 그 지름(H7)으로 넓힌다."""
    PP, PS, PW = "P_M02_PIVOT_PIN", "P_M02_PIVOT_SPACER", "P_M02_PIVOT_WASHER"
    KP, KSN, KSP, KW = "P_M02_KNUCKLE_PIN", "P_M02_KNUCKLE_SPACER_N", "P_M02_KNUCKLE_SPACER_P", "P_M02_KNUCKLE_WASHER"
    CP, CW = "P_M02_CLEVIS_PIN", "P_M02_CLEVIS_WASHER"
    px, pz = -300.0, 70.0
    kx, kz = KNK
    tx, tz = CLV
    s = [C("component.activate", component="U4_WHEEL_N"),
         cy(6, px, pz, -60, 40.2, "new", name=PP), cy(12, px, pz, -65, -60, "join", [PP]),
         cy(2.1, px, pz, 30.2, 40.3, "cut", [PP]),
         cy(2.25, px - 9, pz, -65.1, -59.9, "cut", [PP]), cy(2.25, px + 9, pz, -65.1, -59.9, "cut", [PP]),
         cy(1.65, px - 9, pz, -60.1, -51.9, "cut", ["P_M02_BASE"]), cy(1.65, px + 9, pz, -60.1, -51.9, "cut", ["P_M02_BASE"]),
         cy(10, px, pz, -52, -40, "new", name=PS), cy(6.25, px, pz, -52.1, -39.9, "cut", [PS]),
         cy(10, px, pz, 40.2, 43.2, "new", name=PW), cy(2.75, px, pz, 40.1, 43.3, "cut", [PW]),
         cy(4, tx, tz, -19.5, 19.5, "new", name=CP), cy(7, tx, tz, -23.5, -19.5, "join", [CP]),
         cy(1.65, tx, tz, 7.5, 19.6, "cut", [CP]),
         cy(6, tx, tz, 19.5, 21.5, "new", name=CW), cy(2.25, tx, tz, 19.4, 21.6, "cut", [CW]),
         mat_assign([PP, PS, CP], "S45C"), mat_assign([PW, CW], "SUS304"),
         C("component.activate", component="U4_PRESS"),
         cy(mp_r, px, pz, -38, -30, "cut", [ARM_N]), cy(mp_r, px, pz, 30, 38, "cut", [ARM_P]),
         cy(4, kx, kz, -37, 37, "new", name=KP), cy(7, kx, kz, -41, -37, "join", [KP]),
         cy(1.65, kx, kz, 25, 37.1, "cut", [KP]),
         cy(7, kx, kz, -30.8, -10, "new", name=KSN), cy(4.25, kx, kz, -30.9, -9.9, "cut", [KSN]),
         cy(7, kx, kz, 10, 30.8, "new", name=KSP), cy(4.25, kx, kz, 9.9, 30.9, "cut", [KSP]),
         cy(7, kx, kz, 37, 39, "new", name=KW), cy(2.25, kx, kz, 36.9, 39.1, "cut", [KW]),
         mat_assign([KP], "S45C"), mat_assign([KSN, KSP, KW], "SUS304"),
         C("component.activate", component="U5_WHEEL_F"),
         cy(10, -390, 390, 87, 90, "new", name="P_M03_IDLER_WASHER_O"), cy(2.75, -390, 390, 86.9, 90.1, "cut", ["P_M03_IDLER_WASHER_O"]),
         cy(6.5, -390, 390, 115, 118, "new", name="P_M03_IDLER_WASHER_I"),
         cy(2.75, -390, 390, 114.9, 118.1, "cut", ["P_M03_IDLER_WASHER_I"]),
         mat_assign(["P_M03_IDLER_WASHER_O", "P_M03_IDLER_WASHER_I"], "SUS304"),
         C("component.activate", component=0),
         # 접시 자리 90°: solid.hole countersink는 축·와셔를 통째로 지워(실측) 원뿔 자르기로 그린다
         C("solid.cone", radius=5.05, top_radius=2.5, height=2.55, base=[-390, 118.05, 390], axis=[0, -1, 0],
           operation="cut", targets=["P_M03_IDLER_WASHER_I"])]
    return s


# ------------------------------------------------------------------ E. 볼트
def stage_bolts():
    s = []
    mot = [(-218.0, y, 70 + z) for y, z in SQ] + [(-140.0, y, 70 + z) for y, z in SQ]
    s += bolt_set("CB5-16", "CB5-16_M02_MOT", X, mot, "U4_PRESS",
                  "Misumi CB5-16: HG-KR23 flange -> PGX adapter tap x4, PGX flange counterbore -> P_M02_FRONT M5 tap x4 (MOT-01)")
    s += bolt_set("CB4-12", "CB4-12_M02_KNK", NY, [(KNK[0], 39.0, KNK[1])], "U4_PRESS",
                  "Misumi CB4-12: knuckle pin end M4 tap, washer 2 (MOT-01)")
    s += bolt_set("CB5-12", "CB5-12_M02_HUB", NX, [(-92.5, 0, 70.0)], "U4_WHEEL",
                  "Misumi CB5-12: wheel hub end wall -> PGX output shaft end M5 (MOT-01)")
    s += bolt_set("CB4-12", "CB4-12_M02_PIV", Y, [(-309.0, -65.0, 70.0), (-291.0, -65.0, 70.0)], "U4_WHEEL_N",
                  "Misumi CB4-12: pivot pin head -> P_M02_BASE leg M4 tap x2 (MOT-01)")
    s += bolt_set("CB5-12", "CB5-12_M02_PIV", NY, [(-300.0, 43.2, 70.0)], "U4_WHEEL_N",
                  "Misumi CB5-12: pivot pin end M5 tap, washer 3 (MOT-01)")
    s += bolt_set("CB4-12", "CB4-12_M02_CLV", NY, [(CLV[0], 21.5, CLV[1])], "U4_WHEEL_N",
                  "Misumi CB4-12: cylinder clevis pin end M4 tap, washer 2 (MOT-01)")
    motw = [(-1918.0, y, 70 + z) for y, z in SQ] + [(-1840.0, y, 70 + z) for y, z in SQ]
    s += bolt_set("CB5-16", "CB5-16_M03_MOTW", X, motw, "U5_LIFT",
                  "Misumi CB5-16: HG-KR23 -> PGX adapter x4, PGX -> P_M03_FRONT x4, U5 far wheel (MOT-01)")
    s += bolt_set("CB5-12", "CB5-12_M03_HUB", NX, [(-1792.5, 0, 70.0)], "U5_WHEEL",
                  "Misumi CB5-12: U5 wheel hub end -> PGX shaft end M5 (MOT-01)")
    motx = [(-2220 + a, -4.0, 390 + b) for a, b in SQ] + [(-2220 + a, 74.0, 390 + b) for a, b in SQ]
    s += bolt_set("CB5-16", "CB5-16_M03_MOTX", Y, motx, "U5_WHEEL_F",
                  "Misumi CB5-16: HG-KR23 -> PGX adapter x4, PGX -> P_M03_DRV_BRKT M5 tap x4, carriage X drive (MOT-01)")
    s += bolt_set("CB5-12", "CB5-12_M03_IDL", Y, [(-390.0, 87.0, 390.0)], "U5_WHEEL_F",
                  "Misumi CB5-12: idler shaft outer end M5 tap DP10, washer 3 (MOT-01)")
    s += bolt_set("SFB5-12", "SFB5-12_M03_IDL", NY, [(-390.0, 115.2, 390.0)], "U5_WHEEL_F",
                  "Misumi SFB5-12: idler shaft inner end M5 tap DP12, countersunk washer (MOT-01)", body="Cut-Extrude1")
    s += bolt_set("CB5-16", "CB5-16_U3_MOT", NX, [(437.0, y, -90 + z) for y, z in SQ], "U3_HEAD",
                  "Misumi CB5-16: HG-KR43 flange -> P_U3_LDRV_BRKT M5 tap x4 (MOT-01)")
    s += bolt_set("CB5-16", "CB5-16_U3_BRKT", X, [(537.0, y, z) for y in (-38.0, 38.0) for z in (-112.0, -152.0)], "U3_HEAD",
                  "Misumi CB5-16: P_U3_LDRV_BRKT -> HFS8-4080 slot T-nut x4 (MOT-01)")
    s.append(C("component.activate", component=0))
    return s


def nut_set(x_top):
    """HNTT8-5: 로컬 -Y = 홈 안쪽(+X), y 0 = 윗면(홈 턱 안면)."""
    seats = [(x_top, y, z) for y in (-38.0, 38.0) for z in (-112.0, -152.0)]
    nm = "HNTT8-5_U3_BRKT"
    m = mat((0, 1.0, 0), NX, seats[0])   # 긴 쪽(로컬 x)을 홈 길이(Y)로 — 첫 안(로컬 x -> Z)은 홈 벽과 230 mm³ 겹침(실측)
    s = [C("component.activate", component="U3_HEAD"),
         C("file.insert_step", path=STEP + "HNTT8-5/HNTT8-5.stp", name=nm, matrix=m),
         C("body.rename", body="Tap1", name=nm),
         C("component.metadata.set", component=nm, part_number="HNTT8-5", bom_type="purchased",
           description="Misumi HNTT8-5 post-assembly T-nut, HFS8-4080-1720_M04 -X face slots, P_U3_LDRV_BRKT x4 (MOT-01)"),
         C("material.assign", bodies=[nm], material="Steel")]
    s += copies(nm, seats[0], seats[1:])
    s.append(C("component.activate", component=0))
    return s


def mpfz_set():
    s = [C("component.activate", component="U4_PRESS")]
    for side, d, seat in (("N", Y, (-300.0, -37.0, 70.0)), ("P", NY, (-300.0, 37.0, 70.0))):
        nm = "MPFZ12-10_M02_" + side
        s += [C("file.insert_step", path=STEP + "MPFZ12-10/MPFZ12-10.stp", name=nm, matrix=mat(d, perp(d), seat)),
              C("body.rename", body="Fillet2", name=nm),
              C("component.metadata.set", component=nm, part_number="MPFZ12-10", bom_type="purchased",
                description="Misumi MPFZ12-10 flanged oil-free bushing, arm side %s pivot hole, flange outside (MOT-01)" % side),
              C("material.assign", bodies=[nm], material="Default")]
    s.append(C("component.activate", component=0))
    return s


def dump(name, s):
    os.makedirs(OUT, exist_ok=True)
    json.dump(s, open(os.path.join(OUT, "stage_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return s


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = {"remove": stage_remove, "u4mods": stage_u4_mods, "u5mods": stage_u5_mods, "u3mods": stage_u3_mods,
           "bolts": stage_bolts, "mpfz": mpfz_set}
    if what in fns:
        print(json.dumps(dump(what, fns[what]()), ensure_ascii=False, separators=(",", ":")))
    elif what.startswith("step:"):
        nm = what[5:]
        print(json.dumps(dump("step_" + nm, stage_step(nm)), ensure_ascii=False, separators=(",", ":")))
    elif what.startswith("pins:"):
        print(json.dumps(dump("pins", stage_pins(float(what[5:]))), ensure_ascii=False, separators=(",", ":")))
    elif what.startswith("nuts:"):
        print(json.dumps(dump("nuts", nut_set(float(what[5:]))), ensure_ascii=False, separators=(",", ":")))
    else:
        print("CLV", CLV, "KNK", KNK)


# ------------------------------------------------------------------ 앞판 옆면 볼트 옮김(Ø50 관통과 겹침 풀기)
# 옆면 볼트 CB5-16_M02_5~8·_M03_9~12(Z 70 ±15)의 끝이 Ø50 H8 관통 구멍 안으로 0.6 들어가 감속기 파일럿과 겹친다.
# -> Z 70 ±19 로 옮기고, 앞판 탭은 Y ±20.5~±31(구멍 벽 1.6 남김), 팔·승강 옆판·센서 브래킷 구멍도 같이 옮긴다.
SIDE_OLD, SIDE_NEW = (55.0, 85.0), (51.0, 89.0)


def side_mods(x, front, sn, sp, sns):
    s = []
    for zo, zn in zip(SIDE_OLD, SIDE_NEW):
        s += [cy(2.2, x, zo, -31, -21.6, "join", [front]), cy(2.2, x, zo, 21.6, 31, "join", [front]),   # 구멍 안(bore)에는 채우지 않음
              cy(2.1, x, zn, -32, -20.5, "cut", [front]), cy(2.1, x, zn, 20.5, 32, "cut", [front]),
              cy(2.85, x, zo, -37, -31, "join", [sn]), cy(2.85, x, zo, 31, 37, "join", [sp]),
              cy(2.75, x, zn, -38, -30, "cut", [sn]), cy(2.75, x, zn, 30, 38, "cut", [sp]),
              cy(2.85, x, zo, -39, -37, "join", [sns]), cy(2.75, x, zn, -40, -36, "cut", [sns])]
    return s


def side_bolts(x, names, comp):
    """names = (Z51 N, Z51 P, Z89 N, Z89 P). N: 머리 센서 브래킷(Y -39) -> +Y, P: 머리 옆판(Y 37) -> -Y."""
    s = [C("component.activate", component=comp)]
    for nm, (z, side) in zip(names, ((51.0, "N"), (51.0, "P"), (89.0, "N"), (89.0, "P"))):
        d, seat = (Y, (x, -39.0, z)) if side == "N" else (NY, (x, 37.0, z))
        s += bolt_ins("CB5-16", nm, d, seat,
                      desc="Misumi CB5-16: side plate -> front plate side M5 tap, moved Z 70%+d (MOT-01, clears Ø50 H8 bore)" % (z - 70))
    s.append(C("joint.rigid_group", occurrences=[comp + ":1"] + [n + ":1" for n in names]))
    s.append(C("component.activate", component=0))
    return s


M02S = ["CB5-16_M02_%d" % i for i in (5, 6, 7, 8)]
M03S = ["CB5-16_M03_%d" % i for i in (9, 10, 11, 12)]


def stage_side():
    s = [C("timeline.delete", features=M02S + M03S)]
    s += [C("component.activate", component="U4_PRESS")] + side_mods(-126.0, FRONT2, ARM_N, ARM_P, "P_M02_SNS_BRKT")
    s += [C("component.activate", component="U5_LIFT")] + side_mods(-1826.0, FRONT3, LSN, LSP, "P_M03_SNS_BRKT") + [C("component.activate", component=0)]
    s += side_bolts(-126.0, M02S, "U4_PRESS") + side_bolts(-1826.0, M03S, "U5_LIFT")
    return s


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "side":
    print(json.dumps(dump("side", stage_side()), ensure_ascii=True, separators=(",", ":")))


# ------------------------------------------------------------------ 전체 기록(edit.json) — 앱에 보낸 순서(탐색·롤백된 시험 제외)
CB20 = [513, 516, 519, 522, 856, 859, 862, 865, 868, 871, 874, 877]   # CB5-20_M02_1~4·_M03_1~8 (v2.6.8 피처 id)


def stage_pose_edit():
    return [C("edit.checkpoint"), C("motion.play", study="REST", step=0, quiet=True),
            C("joint.drive", joint=270, value=0, quiet=True), C("joint.drive", joint=49, value=0, quiet=True)]


def stage_steps():
    s = []
    for nm in STEPS:
        s += stage_step(nm)
    return s


def stage_rigid():
    G = {"U4_PRESS": ["PGX62-H-10_M02:1", "HG-KR23_M02:1", "MPFZ12-10_M02_N:1", "MPFZ12-10_M02_P:1", "CB4-12_M02_KNK:1"] + ["CB5-16_M02_MOT:%d" % i for i in range(1, 9)],
         "U4_WHEEL": ["CB5-12_M02_HUB:1"],
         "U4_WHEEL_N": ["CB4-12_M02_PIV:1", "CB4-12_M02_PIV:2", "CB5-12_M02_PIV:1", "CB4-12_M02_CLV:1"],
         "U5_LIFT": ["PGX62-H-10_M03W:1", "HG-KR23_M03W:1"] + ["CB5-16_M03_MOTW:%d" % i for i in range(1, 9)],
         "U5_WHEEL": ["CB5-12_M03_HUB:1"],
         "U5_WHEEL_F": ["PGX62-H-10_M03X:1", "HG-KR23_M03X:1", "CB5-12_M03_IDL:1", "SFB5-12_M03_IDL:1"] + ["CB5-16_M03_MOTX:%d" % i for i in range(1, 9)],
         "U3_HEAD": ["HG-KR43_U3:1"] + ["CB5-16_U3_MOT:%d" % i for i in range(1, 5)] + ["CB5-16_U3_BRKT:%d" % i for i in range(1, 5)]
                    + ["HNTT8-5_U3_BRKT:%d" % i for i in range(1, 5)]}
    return [C("joint.rigid_group", occurrences=[u + ":1"] + o) for u, o in G.items()]


def stage_save(name):
    return [C("motion.play", study="REST", step=0, quiet=True), C("browser.visibility", visible=False, folder="joints"),
            C("component.rename", component=0, name=name),
            C("document.metadata.set", key="description",
              value="MOT-01 mechanism: HG-KR23x3/HG-KR43/PGX62-H-10x3 real STEP, motor/gearbox/pin fasteners, U3 lower-shaft bracket")]


def full_record():
    import sys as _s
    _s.path.insert(0, os.path.join(OUT))
    from pgx_created import BASE
    s = stage_pose_edit() + [C("timeline.delete", features=CB20), C("solid.remove", bodies=OLD)] + stage_steps()
    for nm, suf, wc in (("PGX62-H-10_M02", "", "U4_WHEEL"), ("PGX62-H-10_M03W", " (2)", "U5_WHEEL"), ("PGX62-H-10_M03X", " (3)", None)):
        s += stage_pgx_names(nm, [b + suf for b in BASE], wc)
    for nm, raw in (("HG-KR23_M02", "HG-KR23"), ("HG-KR23_M03W", "HG-KR23 (2)"), ("HG-KR23_M03X", "HG-KR23 (3)"), ("HG-KR43_U3", "HG-KR43_")):
        s += stage_motor_names(nm, [raw])
    s += stage_u4_mods() + stage_u5_mods() + stage_u3_mods() + mpfz_set() + stage_pins(9.0) + stage_bolts() + nut_set(548.0)
    s += stage_rigid() + stage_side()
    return s


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "record":
    e = full_record() + stage_save(sys.argv[2])
    d = os.path.dirname(OUT)
    json.dump(e, open(os.path.join(d, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.6.8.sc", "result": "3D_Modeling/%s.sc" % sys.argv[2],
               "generator": "tools/gen_v2_mot01.py record (MCP batch, MOT-01)"},
              open(os.path.join(d, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("edit.json", len(e))
