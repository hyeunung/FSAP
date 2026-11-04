# -*- coding: utf-8 -*-
"""M06 U6 센서 + 슈, U7 롤 걸이 생성기 — 기준 3D_Modeling/FSAP_v2.2.0.sc -> 3D_Modeling/FSAP_v2.3.0.sc (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M06_design.md(3절 표) + 모델링 지시서.
python -X utf8 -B tools/gen_v2_m06.py --parts   -> tools/out/mech_M06/parts/prep_*.json (구매품 한 개씩 STEP을 세계 자리에 놓은 준비 스크립트)
python -X utf8 -B tools/gen_v2_m06.py           -> tools/out/mech_M06/edit.json (v2.2.0에 돌리는 명령 기록)
python -X utf8 -B tools/gen_v2_m06.py --solo    -> tools/out/mech_M06/work/solo.json (빈 설계에서 새 부품만 — 형상 확인용)
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm, J_U6_SHIFT 0(작동) 기준. 대기(REST)는 J_U6_SHIFT -60(비킴).
구매품은 M05와 같은 길: 부품마다 준비 .sc(parts/<이름>.sc)에 file.insert_step 한 번, 기록에서는 component.insert_design + break_link.
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M06").replace("\\", "/")
PARTS = OUT + "/parts"
STEP = PRJ + "/purchased-step/"
UPPER = "STEP대기_867-392342_UPPER"
HANGER = "P_M01_HANGER"
BEAM = "U1_BEAM"


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


def cyl(r, base, h, axis, op, tg=None, name=None):
    p = {"radius": r, "height": r4(h), "base": [r4(v) for v in base], "axis": axis, "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


def cx(r, y, z, x0, x1, op, tg=None, name=None):
    return cyl(r, [x0, y, z], x1 - x0, [1, 0, 0], op, tg, name)


def cy(r, x, z, y0, y1, op, tg=None, name=None):
    return cyl(r, [x, y0, z], y1 - y0, [0, 1, 0], op, tg, name)


def cz(r, x, y, z0, z1, op, tg=None, name=None):
    return cyl(r, [x, y, z0], z1 - z0, [0, 0, 1], op, tg, name)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mat_loc(cx_, cy_, t):
    """로컬 X축 -> cx_, 로컬 Y축 -> cy_, Z = X x Y. 행 우선 3x4."""
    cz_ = cross(cx_, cy_)
    return [cx_[0], cy_[0], cz_[0], r4(t[0]), cx_[1], cy_[1], cz_[1], r4(t[1]), cx_[2], cy_[2], cz_[2], r4(t[2])]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (0, 1, 0)


def plane(origin, xd, yd):
    return {"origin": list(origin), "x_dir": list(xd), "y_dir": list(yd)}


def XY(z):
    return plane((0, 0, z), (1, 0, 0), (0, 1, 0))      # 법선 +Z, (u, v) = (X, Y)


def XZ(y):
    return plane((0, y, 0), (1, 0, 0), (0, 0, 1))      # 법선 -Y, (u, v) = (X, Z)


def YZ(x):
    return plane((x, 0, 0), (0, 1, 0), (0, 0, 1))      # 법선 +X, (u, v) = (Y, Z)


def poly_sketch(name, pl, pts):
    return [C("sketch.create", plane=pl, name=name),
            C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True),
            C("sketch.finish")]


def hole_cut(name, pl, centers, r, dist, body, direction=None):
    s = [C("sketch.create", plane=pl, name=name)]
    s += [C("sketch.circle.center", center=[r4(a), r4(b)], radius=r) for a, b in centers]
    s.append(C("sketch.finish"))
    p = {"sketch": name, "distance": dist, "operation": "cut", "targets": [body]}
    if direction:
        p["direction"] = direction
    s.append(C("solid.extrude", **p))
    return s


# ---------------------------------------------------------------- 이름
BASE, CARR, SHOE = "P_M06_BASE", "P_M06_CARR", "P_M06_SHOE"
POST, SHAFT, HUB, WASHER = "P_M06_ROLL_POST", "P_M06_ROLL_SHAFT", "P_M06_ROLL_HUB", "P_M06_ROLL_WASHER"
G1B, G1P, G1R = "P_M06_G1_BRKT", "P_M06_G1_PIN", "P_M06_G1_ROLLER"
TPB, TPP, TPR = "P_M06_TOP_BRKT", "P_M06_TOP_PIN", "P_M06_TOP_ROLLER"
ROLL, TWH, TWV = "U7_TAPE_ROLL", "U7_TAPEWAY_H", "U7_TAPEWAY_V"
CB3 = ["STEP대기_CB3-10_M06_1", "STEP대기_CB3-10_M06_2"]
INS3 = ["STEP대기_INSERT_M3_M06_1", "STEP대기_INSERT_M3_M06_2"]

MADE = {  # 바디: (컴포넌트, 재질)
    BASE: ("U6_SENSOR", "SUS304"),
    CARR: ("U6_SHOE", "PET-CF"), SHOE: ("U6_SHOE", "SUS304"),
    CB3[0]: ("U6_SHOE", "Steel"), CB3[1]: ("U6_SHOE", "Steel"), INS3[0]: ("U6_SHOE", "Steel"), INS3[1]: ("U6_SHOE", "Steel"),
    POST: ("U7_ROLL_MOUNT", "A5052"), SHAFT: ("U7_ROLL_MOUNT", "S45C"), HUB: ("U7_ROLL_MOUNT", "PET-CF"),
    WASHER: ("U7_ROLL_MOUNT", "SUS304"),
    G1B: ("U7_ROLL_MOUNT", "SUS304"), G1P: ("U7_ROLL_MOUNT", "SUS304"), G1R: ("U7_ROLL_MOUNT", "PET-CF"),
    TPB: ("U7_ROLL_MOUNT", "SUS304"), TPP: ("U7_ROLL_MOUNT", "SUS304"), TPR: ("U7_ROLL_MOUNT", "PET-CF"),
    ROLL: ("U7_ROLL_MOUNT", "Default"), TWH: ("U7_ROLL_MOUNT", "Default"), TWV: ("U7_ROLL_MOUNT", "Default"),
}

# ---------------------------------------------------------------- 실린더 CJ2B16-60SZ (STEP 실측 tools/out/mech_M06/work/probe_faces_out.json)
# 로컬 X: 로드 커버 어깨 x=0, 장착 나사 보스 Ø10(M10) x -8~0, 몸 x 0~138(Ø18.3), 헤드 커버 포트 M5 x 133 · 로컬 +Y 면 y 9.15,
# 로드 Ø5(M5 나사 끝) 후퇴 끝 x -28, 로드 끝 너트 NTJ-015C ×2 x -24.5~-16.5, 장착 너트 SNJ-016C x -6.3~-2.3.
# 세계: 로컬 X -> -X(로드가 +X로 나옴), 로컬 Y(포트) -> +Z, 축선 Y -130 · Z 136.
# 어깨(탭 바깥면) X -142: 로드 끝 작동 X -54(캐리지 인서트에 6 물림, 캐리지 -X 면 -60에 너트 2개), 비킴 X -114.
CYL_T = (-142.0, -130.0, 136.0)
CYL_X, CYL_Y = (-1, 0, 0), (0, 0, 1)
ROD_T = (CYL_T[0] + 60.0, CYL_T[1], CYL_T[2])      # 로드 묶음은 작동(J 0) 자리로 +60

# ---------------------------------------------------------------- 볼트 (머리 밑면 점, 축, 형번, 컴포넌트, 이름)
BOLTS = [
    ((-70, -93, 180), (0, 1, 0), "CB5-12", "U6_SENSOR", "CB5-12_M06_1", "BASE 붙임면 -> UPPER -Y 면 새 탭"),
    ((-32, -93, 180), (0, 1, 0), "CB5-12", "U6_SENSOR", "CB5-12_M06_2", "BASE 붙임면 -> UPPER -Y 면 새 탭"),
    ((-20, -175, 32.5), (-1, 0, 0), "CB5-12", "U6_SHOE", "CB5-12_M06_3", "슈 장공 -> 캐리지 다리 인서트"),
    ((-20, -135, 32.5), (-1, 0, 0), "CB5-12", "U6_SHOE", "CB5-12_M06_4", "슈 장공 -> 캐리지 다리 인서트"),
    ((670, -145, 750), (0, 1, 0), "CB5-12", "U7_ROLL_MOUNT", "CB5-12_M06_8", "와셔 -> 축 앞끝 탭"),
    ((505, -85, 625), (0, -1, 0), "CB5-12", "U7_ROLL_MOUNT", "CB5-12_M06_9", "G1 세운 판 +Y -> G1 핀 탭"),
    ((44, -85, 595), (0, -1, 0), "CB5-12", "U7_ROLL_MOUNT", "CB5-12_M06_10", "꼭대기 세운 판 +Y -> 꼭대기 핀 탭"),
    ((465, -74, 563), (0, 0, -1), "CB5-12", "U7_ROLL_MOUNT", "CB5-12_M06_11", "G1 발 -> UPPER 윗면 새 탭"),
    ((485, -74, 563), (0, 0, -1), "CB5-12", "U7_ROLL_MOUNT", "CB5-12_M06_12", "G1 발 -> UPPER 윗면 새 탭"),
    ((670, 102, 768), (0, 1, 0), "CB5-16", "U7_ROLL_MOUNT", "CB5-16_M06_1", "축 플랜지 -> 기둥 탭"),
    ((670 - 15.5885, 102, 741), (0, 1, 0), "CB5-16", "U7_ROLL_MOUNT", "CB5-16_M06_2", "축 플랜지 -> 기둥 탭"),
    ((670 + 15.5885, 102, 741), (0, 1, 0), "CB5-16", "U7_ROLL_MOUNT", "CB5-16_M06_3", "축 플랜지 -> 기둥 탭"),
    ((670, 110, 615), (0, 1, 0), "CB5-20", "U7_ROLL_MOUNT", "CB5-20_M06_1", "롤 기둥 -> 보 앞면 탭(M07)"),
    ((670, 110, 640), (0, 1, 0), "CB5-20", "U7_ROLL_MOUNT", "CB5-20_M06_2", "롤 기둥 -> 보 앞면 탭(M07)"),
    ((28, -74, 571), (0, 0, -1), "CB5-20", "U7_ROLL_MOUNT", "CB5-20_M06_3", "꼭대기 발 + HANGER 선반 -> UPPER 윗면 새 탭"),
    ((52, -74, 571), (0, 0, -1), "CB5-20", "U7_ROLL_MOUNT", "CB5-20_M06_4", "꼭대기 발 + HANGER 선반 -> UPPER 윗면 새 탭"),
]
# 인서트 MBIS5-6.5-8: 로컬 X 0~8 = 박히는 방향, x=0 면
INSERTS = [((-22, -175, 32.5), (-1, 0, 0)), ((-22, -135, 32.5), (-1, 0, 0)), ((-60, -130, 136), (1, 0, 0))]


def purchased():
    """(이름, 형번 폴더, matrix, 컴포넌트, 바디 이름 바꾸기, 지울 바디, part_number, bom)"""
    L = []
    nm = "CJ2B16-60SZ_M06"
    L.append((nm, "CJ2B16-60SZ", mat_loc(CYL_X, CYL_Y, CYL_T), "U6_SENSOR",
              [("CJ2B16-60SZ(0_0)_BODY", nm), ("SNJ-016C", nm + "_NUT_MNT")],
              ["CJ2B16-60SZ_ROD", "NTJ-015C"], "CJ2B16-60SZ", "purchased"))
    L.append((nm + "_ROD", "CJ2B16-60SZ", mat_loc(CYL_X, CYL_Y, ROD_T), "U6_SHOE",
              [("CJ2B16-60SZ_ROD", nm + "_ROD"), ("NTJ-015C", nm + "_NUT_ROD")],
              ["CJ2B16-60SZ(0_0)_BODY", "SNJ-016C"], "CJ2B16-60SZ", "reference"))
    # 피팅: 헤드 커버 포트(로컬 x 133, 포트 면 y 9.15) -> 세계 (-275, -130, 145.15), 출구 -X
    port = (CYL_T[0] - 133.0, CYL_T[1], CYL_T[2] + 9.15)
    L.append(("KQ2L06-M5A_M06", "KQ2L06-M5A", mat_loc((-1, 0, 0), (0, 0, 1), port), "U6_SENSOR",
              [("KQ2L06-M5A", "KQ2L06-M5A_M06")], [], "KQ2L06-M5A", "purchased"))
    # 화이버 머리: 로컬 X(15, 감지면 x -2.5) -> +Z, 로컬 Y(35, 화이버 쪽 +) -> -X, 로컬 Z(5) -> -Y
    L.append(("E32-D36P1_2M_M06", "E32-D36P1_2M", mat_loc((0, 0, 1), (-1, 0, 0), (2.5, -109.5, 23.5)), "U6_SHOE",
              [("NONE", "E32-D36P1_2M_M06")], [], "E32-D36P1 2M", "purchased"))
    for i, (p, d) in enumerate(INSERTS, 1):
        n = "MBIS5-6.5-8_M06_%d" % i
        L.append((n, "MBIS5-6.5-8", mat_loc(d, perp(d), p), "U6_SHOE", [("MBIS5-6.5-8", n)], [], "MBIS5-6.5-8", "purchased"))
    for i, t in enumerate([(670, -80, 750), (670, -130, 750)], 1):
        n = "6004ZZ_M06_%d" % i
        L.append((n, "6004ZZ", mat_loc((0, -1, 0), (0, 0, 1), t), "U7_ROLL_MOUNT",
                  [("6004ZZ " + a, "%s_%s" % (n, b)) for a, b in (("Outer ring", "OUTER"), ("Inner ring", "INNER"), ("Shield1", "SHIELD1"), ("Shield2", "SHIELD2"))],
                  [], "6004ZZ", "purchased"))
    for p, d, pn, comp, n, memo in BOLTS:
        L.append((n, pn, mat_loc(d, perp(d), p), comp, [("Cut-Extrude1", n)], [], pn, "purchased"))
    return L


def gen_parts():
    os.makedirs(PARTS, exist_ok=True)
    jobs = []
    for nm, pn, M, comp, ren, rm, part_no, bom in purchased():
        s = [C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=nm, matrix=M)]
        if rm:
            s.append(C("solid.remove", bodies=rm))
        s += [C("body.rename", body=a, name=b) for a, b in ren]
        s.append(C("inspect.measure"))
        json.dump(s, open(PARTS + "/prep_%s.json" % nm, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        jobs.append(nm)
    json.dump(jobs, open(PARTS + "/jobs.json", "w", encoding="utf-8"))
    print(len(jobs), "prep scripts")


# ---------------------------------------------------------------- 판금 규칙
def st_rules():
    return [C("sheet.manage_rules", name="SUS304_t3", thickness="3", bend_radius="3", k_factor="0.44",
              relief_width="1", relief_depth="1.5", active=True),
            C("sheet.manage_rules", name="SUS304_t2", thickness="2", bend_radius="2", k_factor="0.44",
              relief_width="1", relief_depth="1", active=False)]


# ---------------------------------------------------------------- U6 고정: BASE
def st_base():
    # 평판 윤곽(Z 148 밑면, t3 위로): 날개 X -139~-22 · Y -172~-97, 혀 X -80~-22 · Y -97~-90, 탭 자리 X -142~-139 · Y -145~-115
    out = [(-139, -172), (-22, -172), (-22, -90), (-80, -90), (-80, -97), (-139, -97), (-139, -115), (-142, -115), (-142, -145), (-139, -145)]
    s = poly_sketch("SK_M06_BASE", XY(148), out)
    s += [C("sheet.flange", type="base", sketch="SK_M06_BASE", rule="SUS304_t3", body_name=BASE),
          # 붙임면: 혀 +Y 끝 위로(바깥 가상 꼭짓점 Z 148 -> 끝 195)
          C("sheet.flange", type="edge", edges=[[-51, -90, 151]], height=47, angle=90, body=BASE),
          # 실린더 탭: -X 끝 아래로(바깥 가상 꼭짓점 Z 151 -> 끝 120)
          C("sheet.flange", type="edge", edges=[[-142, -130, 148]], height=31, angle=90, body=BASE)]
    s += hole_cut("SK_M06_BASE_H1", XZ(-89), [(-70, 180), (-32, 180)], 2.75, 5, BASE)          # 붙임면 Ø5.5 ×2 (-Y로 5)
    s += hole_cut("SK_M06_BASE_H2", YZ(-143), [(-130, 136)], 5.25, 5, BASE)                    # 탭 Ø10.5(M10×1 장착 나사, +X로 5)
    return s


# ---------------------------------------------------------------- U6 움직임: 캐리지·슈·인서트 자리
def st_shoe():
    s = []
    # 캐리지 C 단면(YZ) X -60~-22
    cprof = [(-177, 124), (-100, 124), (-100, 147.7), (-172, 147.7), (-172, 151), (-110, 151), (-110, 156), (-177, 156)]
    s += poly_sketch("SK_M06_CARR", YZ(-60), cprof)
    s.append(C("solid.extrude", sketch="SK_M06_CARR", distance=38, operation="new", body_name=CARR))
    s += [box(None, -34, -22, -185, -100, 21, 124.5, "join", [CARR]),      # 다리(아랫턱으로 0.5 겹쳐 붙임)
          box(None, -22.5, 18, -107, -100, 21, 36, "join", [CARR])]       # 팔(다리로 0.5 겹쳐 붙임)
    # 인서트 자리 Ø6.8 깊이 8 + 볼트 끝 Ø5.2
    s += [cx(3.4, y, 32.5, -30, -21.9, "cut", [CARR]) for y in (-175, -135)]
    s += [cx(2.6, y, 32.5, -33, -29.9, "cut", [CARR]) for y in (-175, -135)]
    s += [cx(3.4, -130, 136, -60.1, -52, "cut", [CARR]), cx(2.6, -130, 136, -52.1, -50, "cut", [CARR])]
    # M3 인서트 자리 Ø4 깊이 6 (팔 -Y 면, 머리 구멍 X 2.5 · Z 23.5 / 33.5)
    s += [cy(2.0, 2.5, z, -107.1, -101, "cut", [CARR]) for z in (23.5, 33.5)]
    # STEP대기 M3 인서트(Ø4 × 5, 안 Ø3) + STEP대기 CB3-10(머리 Ø5.5 × 3 + 자루 Ø3 × 10)
    for i, z in enumerate((23.5, 33.5)):
        s += [cy(2.0, 2.5, z, -107, -102, "new", name=INS3[i]), cy(1.5, 2.5, z, -107.1, -101.9, "cut", [INS3[i]])]
        s += [cy(2.75, 2.5, z, -115, -112, "new", name=CB3[i]), cy(1.5, 2.5, z, -112, -102, "join", [CB3[i]])]
    # 슈 SUS304 t2: 바닥(Z 12.5 위로 t2) X -22~1 · Y -195~-115, 세운 벽(-X 끝 위로 Z 45), 입술(-Y 끝 20° 위로 10)
    s += poly_sketch("SK_M06_SHOE", XY(12.5), [(-22, -195), (1, -195), (1, -115), (-22, -115)])
    s += [C("sheet.flange", type="base", sketch="SK_M06_SHOE", rule="SUS304_t2", body_name=SHOE),
          C("sheet.flange", type="edge", edges=[[-22, -155, 14.5]], height=32.5, angle=90, body=SHOE),
          C("sheet.flange", type="edge", edges=[[-9, -195, 14.5]], height=10.642, angle=20, body=SHOE)]
    # 벽 세로 장공 Ø5.5 × 15 (Z 25~40) ×2
    s += [C("sketch.create", plane=YZ(-23), name="SK_M06_SHOE_SL")]
    s += [C("sketch.slot.center_to_center", p0=[y, 27.75], p1=[y, 37.25], width=5.5) for y in (-175, -135)]
    s += [C("sketch.finish"), C("solid.extrude", sketch="SK_M06_SHOE_SL", distance=4, operation="cut", targets=[SHOE])]
    return s


# ---------------------------------------------------------------- U7 롤 걸이
def st_roll():
    s = [box(POST, 640, 700, 110, 120, 605, 780)]
    s += [cy(2.75, 670, z, 109.9, 120.1, "cut", [POST]) for z in (615, 640)]                     # CB5-20 Ø5.5
    pcd = [(670, 768), (670 - 15.5885, 741), (670 + 15.5885, 741)]
    s += [cy(2.1, x, z, 109.9, 120.1, "cut", [POST]) for x, z in pcd]                             # 플랜지 M5 탭 ×3
    # 축 S45C: 플랜지 Ø50 t8(Y 102~110) + 축 Ø20(Y -142~102) + 어깨 Ø25(Y -80~-74)
    s += [cy(25, 670, 750, 102, 110, "new", name=SHAFT), cy(10, 670, 750, -142, 102.5, "join", [SHAFT]),
          cy(12.5, 670, 750, -80, -74, "join", [SHAFT]), cy(2.1, 670, 750, -142.1, -130, "cut", [SHAFT])]
    s += [cy(2.75, x, z, 101.9, 110.1, "cut", [SHAFT]) for x, z in pcd]
    # 허브 PET-CF: 심 자리 Ø76 (Y -142~-78) + 뒤 턱 Ø110 t5 (Y -78~-73), 베어링 자리 Ø42 ×2, 사이 Ø30
    s += [cy(38, 670, 750, -142, -77.5, "new", name=HUB), cy(55, 670, 750, -78, -73, "join", [HUB]),
          cy(21, 670, 750, -142.1, -130, "cut", [HUB]), cy(15, 670, 750, -130.1, -91.9, "cut", [HUB]),
          cy(21, 670, 750, -92, -80, "cut", [HUB]), cy(15, 670, 750, -80.1, -72.9, "cut", [HUB])]
    # 와셔 SUS t3 Ø24 (Y -145~-142) 구멍 Ø5.5
    s += [cy(12, 670, 750, -145, -142, "new", name=WASHER), cy(2.75, 670, 750, -145.1, -141.9, "cut", [WASHER])]
    # 테이프 롤 차지 Ø300 × 60 (심 Ø76)
    s += [cy(150, 670, 750, -140, -80, "new", name=ROLL), cy(38, 670, 750, -140.1, -79.9, "cut", [ROLL])]
    # 안내 롤러 G1 브래킷(판금 L): 세운 판(XZ, Y -88~-85) X 455~530 · Z 560~650, 발 X 455~495 (Y -88 -> -60)
    s += poly_sketch("SK_M06_G1B", XZ(-85), [(455, 560), (495, 560), (495, 563), (530, 563), (530, 650), (455, 650)])
    s += [C("sheet.flange", type="base", sketch="SK_M06_G1B", rule="SUS304_t3", body_name=G1B),
          C("sheet.flange", type="edge", edges=[[475, -85, 560]], height=28, angle=90, body=G1B)]
    s += hole_cut("SK_M06_G1B_H1", XY(559), [(465, -74), (485, -74)], 2.75, 5, G1B, direction="positive")
    s += hole_cut("SK_M06_G1B_H2", XZ(-84), [(505, 625)], 2.75, 5, G1B)
    # 꼭대기 롤러 브래킷(판금 L): 발 X 20~70 · Y -88~-60 · Z 568~571, 세운 판 Y -88~-85 · Z ~620
    s += poly_sketch("SK_M06_TPB", XY(568), [(20, -88), (70, -88), (70, -60), (20, -60)])
    s += [C("sheet.flange", type="base", sketch="SK_M06_TPB", rule="SUS304_t3", body_name=TPB),
          C("sheet.flange", type="edge", edges=[[45, -88, 571]], height=52, angle=90, body=TPB)]
    s += hole_cut("SK_M06_TPB_H1", XY(567), [(28, -74), (52, -74)], 2.75, 5, TPB, direction="positive")
    s += hole_cut("SK_M06_TPB_H2", XZ(-84), [(44, 595)], 2.75, 5, TPB)
    # 핀(SUS304 선반): 머리 Ø16 (Y -131.5~-127.5), 자루 Ø10 (-127.5~-91.5), 턱 Ø14 (-91.5~-88), 턱 끝 M5 탭 깊이 12
    # 롤러(PET-CF): Ø30 (Y -127.4~-91.6) + 턱 Ø38 × 1.9/2.9 (테이프 폭 31: Y -125.5~-94.5), 구멍 Ø10.2
    for P, R, x, z in ((G1P, G1R, 505, 625), (TPP, TPR, 44, 595)):
        s += [cy(8, x, z, -131.5, -127.5, "new", name=P), cy(5, x, z, -127.6, -91.5, "join", [P]),
              cy(7, x, z, -91.6, -88, "join", [P]), cy(2.1, x, z, -100, -87.9, "cut", [P])]
        s += [cy(15, x, z, -127.4, -91.6, "new", name=R), cy(19, x, z, -127.4, -125.5, "join", [R]),
              cy(19, x, z, -94.5, -91.6, "join", [R]), cy(5.1, x, z, -127.5, -91.5, "cut", [R])]
    # 테이프 길 차지
    s += [box(TWH, 60, 488, -125.5, -94.5, 610, 611), box(TWV, 13.5, 44.5, -125.5, -94.5, 340, 580)]
    return s


# ---------------------------------------------------------------- 기존 바디 가공(탭·구멍)
def st_host():
    s = [cy(2.1, x, 180, -90.1, -78, "cut", [UPPER]) for x in (-70, -32)]                # UPPER -Y 면 M5 탭 깊이 12
    s += [cz(2.1, x, -74, 548, 560.1, "cut", [UPPER]) for x in (465, 485, 28, 52)]        # UPPER 윗면 M5 탭 깊이 12
    s += [cz(2.75, x, -74, 559.9, 568.1, "cut", [HANGER]) for x in (28, 52)]              # HANGER 선반 Ø5.5
    s += [cy(2.1, 670, z, 119.9, 133, "cut", [BEAM]) for z in (615, 640)]                # 보 앞면 M5 탭 깊이 13
    return s


def st_assign():
    s = []
    comps, mats = {}, {}
    for b, (c, m) in MADE.items():
        comps.setdefault(c, []).append(b)
        mats.setdefault(m, []).append(b)
    for c, bs in comps.items():
        s.append(C("component.move_bodies", bodies=bs, component=c))
    for m, bs in mats.items():
        if m != "Default":
            s.append(C("material.assign", bodies=bs, material=m))
    return s


NUT_MOVES = [("CJ2B16-60SZ_M06_NUT_MNT", (0.7, 0, 0)), ("CJ2B16-60SZ_M06_NUT_ROD", (-2.5, 0, 0)), ("CJ2B16-60SZ_M06_NUT_ROD2", (-2.5, 0, 0))]


def st_purchased():
    s = []
    for nm, pn, M, comp, ren, rm, part_no, bom in purchased():
        s += [C("component.insert_design", path="%s/%s.sc" % (PARTS, nm), name=nm, parent=comp),
              C("component.break_link", component=nm)]
        if bom == "reference":
            s.append(C("body.rename", body="CJ2B16-60SZ_M06_NUT_ROD (%s:1/NTJ-015C:2)" % nm, name="CJ2B16-60SZ_M06_NUT_ROD2"))
            s.append(C("component.metadata.set", component=nm, part_number=part_no, bom_type="reference",
                       description="rod and rod-end nuts of CJ2B16-60SZ_M06 (moving part of the same cylinder)"))
        else:
            s.append(C("component.metadata.set", component=nm, part_number=part_no, bom_type="purchased"))
    for b, t in NUT_MOVES:
        s.append(C("solid.move", bodies=[b], translate=list(t)))
    s.append(C("material.assign", bodies=[b[4] for b in BOLTS], material="SCM435"))
    s.append(C("material.assign", bodies=["CJ2B16-60SZ_M06"], material="Aluminum"))
    s.append(C("material.assign", bodies=["CJ2B16-60SZ_M06_ROD", "CJ2B16-60SZ_M06_NUT_MNT", "CJ2B16-60SZ_M06_NUT_ROD",
                                          "CJ2B16-60SZ_M06_NUT_ROD2"] +
               ["6004ZZ_M06_%d_%s" % (i, k) for i in (1, 2) for k in ("OUTER", "INNER", "SHIELD1", "SHIELD2")], material="Steel"))
    return s


def st_prep():
    return [C("solid.remove", bodies=["U6_SHOE_SENSOR", "U7_ROLL", "U7_PATH_H"]),
            C("component.create", name="U6_SHOE", parent=0, activate=False),
            C("component.create", name="U7_ROLL_MOUNT", parent=0, activate=False)]


def st_joints():
    return [C("joint.rigid_group", occurrences=["U1_FRAME:1", "U7_ROLL_MOUNT:1"]),
            C("joint.create", type="slider", name="J_U6_SHIFT", flip=True, quiet=True, limits=[[-60, 0]],
              a={"occurrence": "U6_SENSOR:1", "point": [-41, -130, 136], "z": [1, 0, 0]},
              b={"occurrence": "U6_SHOE:1", "point": [-41, -130, 136], "z": [1, 0, 0]})]


ROT = {"J_U4_WHEEL_ROT", "J_U5_WHEEL_ROT", "J_WP_L_ROT", "J_WP_S_ROT", "J_WP_G_ROT", "J_U4_PRESS", "J_U4_DISK", "J_U4_CYL_PIN", "J_U4_ROD_PIN"}
SHIFT_KEYS = {
    "REST": [[0, -60], [1, -60]],
    "MAINT_HEAD": [[0, -60], [1, -60]],
    "CYCLE_S": [[0, -60], [12, -60], [14, 0], [434, 0], [436, -60], [450, -60]],
    "CYCLE_L": [[0, -60], [12, -60], [14, 0], [668, 0], [670, -60], [716, -60]],
    "CYCLE_G1": [[0, -60], [12, -60], [14, 0], [514, 0]],
    "CYCLE_G2": [[0, 0], [574, 0], [576, -60], [630, -60]],
    "SEAM_U7": [[0, 0], [20, 0], [21, -60], [32, -60]],
    "MAINT_U7": [[0, -60], [13, -60]],
}


def st_studies():
    """motion.study {study} 은 keys를 통째로 바꾼다(실측: 키 하나만 주면 나머지가 지워짐) -> 기준 키(keys_base.json) + J_U6_SHIFT."""
    K = json.load(open(OUT + "/keys_base.json", encoding="utf-8"))
    s = []
    for k, v in SHIFT_KEYS.items():
        # motion.list는 회전 키를 라디안으로 돌려주고 motion.study는 도로 받는다(WF-117) -> 회전 조인트는 도로 바꿔 넣는다
        ks = [{"joint": x["joint"], "points": [[a, round(b * 180.0 / math.pi, 6) if x["joint"] in ROT else b] for a, b in x["points"]]}
              for x in K[k]["keys"]] + [{"joint": "J_U6_SHIFT", "points": v}]
        s.append(C("motion.study", study=k, steps=K[k]["steps"], keys=ks))
    return s


def st_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M06 mechanism: U6 shoe and edge sensor on -X retract cylinder, U7 tape roll holder, guide rollers and tape path")]


def build():
    return (st_prep() + st_rules() + st_base() + st_shoe() + st_roll() + st_host() + st_assign()
            + st_purchased() + st_joints() + st_studies() + st_final())


def solo():
    """빈 설계 형상 확인용: 새 가공품 + 측정."""
    return st_rules() + st_base() + st_shoe() + st_roll() + [C("inspect.measure")]


if __name__ == "__main__":
    os.makedirs(OUT + "/work", exist_ok=True)
    if "--machine" in sys.argv:
        pass
    elif "--parts" in sys.argv:
        gen_parts()
    elif "--solo" in sys.argv:
        json.dump(solo(), open(OUT + "/work/solo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("solo", len(solo()))
    else:
        s = build()
        json.dump(s, open(OUT + "/edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(len(s), "commands")


# ---------------------------------------------------------------- 기계 정의(E-15)
def gen_machine():
    """공유 machine.json에 M05 복사본의 U7 조인트·연구(합치기에서 빠짐)를 들이고 M06을 더한다."""
    m05 = json.load(open(ROOT + "/out/M05/machine.json", encoding="utf-8"))
    m = json.load(open(ROOT + "/machine.json", encoding="utf-8"))
    for k in ("joints", "studies"):
        for j, v in m05[k].items():
            if j not in m[k]:
                m[k][j] = v
    m["units"]["U7_TAPE"] = m05["units"]["U7_TAPE"]
    m["states"] = m05["states"]
    m["doc"] = "../3D_Modeling/FSAP_v2.3.0.sc"
    m["joints"]["J_U6_SHIFT"] = {
        "cad": "J_U6_SHIFT", "type": "slide", "unit": "U6_SHOE", "axis": [1, 0, 0], "origin": [-41, -130, 136],
        "rest": -60, "min": -60, "max": 0,
        "_note": "M06(v2.3.0) 슈·센서 비킴. CJ2B16-60SZ 단동 스프링 복귀(축선 Y -130 · Z 136, 로드 +X). 0 = 작동(공기, 슈 바닥 X -20~1 · 센서 머리 X -17.5~17.5 바늘 앞), "
                 "-60 = 비킴(스프링, 행정 끝 = 조인트 한계). 연구: 로딩 -60 -> 노루발 내림(14)에서 0 -> 봉제 0 -> 사절·노루발 들기 뒤 -60"}
    m["units"]["U6_SENSOR"] = {"parts": ["P_M06_BASE", "CJ2B16-60SZ_M06", "KQ2L06-M5A_M06", "CB5-12_M06_1", "CB5-12_M06_2"], "moving": False,
                               "components": ["U6_SENSOR", "CJ2B16-60SZ_M06", "KQ2L06-M5A_M06", "CB5-12_M06_1", "CB5-12_M06_2"],
                               "_note": "M06(v2.3.0): 고정 판금 P_M06_BASE(SUS304 t3, UPPER -Y 면 CB5-12 ×2) + 실린더 몸 CJ2B16-60SZ_M06(+장착 너트) + 피팅 KQ2L06-M5A_M06. 옛 상자 U6_SHOE_SENSOR 지움. U1_FRAME 리지드"}
    m["units"]["U6_SHOE"] = {"parts": ["P_M06_CARR", "P_M06_SHOE", "CJ2B16-60SZ_M06_ROD", "CJ2B16-60SZ_M06_NUT_ROD", "E32-D36P1_2M_M06",
                                       "STEP대기_CB3-10_M06", "STEP대기_INSERT_M3_M06", "MBIS5-6.5-8_M06", "CB5-12_M06_3", "CB5-12_M06_4"],
                             "moving": True, "joints": ["J_U6_SHIFT"], "components": ["U6_SHOE"],
                             "_note": "M06(v2.3.0): J_U6_SHIFT로 움직임. 캐리지 P_M06_CARR(PET-CF, 날개를 C자로 물고 미끄러짐)·슈 P_M06_SHOE(SUS304 t2, 바닥 Z 12.5)·화이버 머리 E32-D36P1_2M_M06(감지면 Z 21, X -17.5~17.5 · Y -112~-107)·로드 묶음"}
    m["units"]["U7_ROLL_MOUNT"] = {"parts": ["P_M06_ROLL", "P_M06_G1", "P_M06_TOP", "U7_TAPE_ROLL", "U7_TAPEWAY", "6004ZZ_M06", "CB5-12_M06_8", "CB5-12_M06_9",
                                             "CB5-12_M06_10", "CB5-12_M06_11", "CB5-12_M06_12", "CB5-16_M06", "CB5-20_M06"], "moving": False,
                                   "components": ["U7_ROLL_MOUNT"],
                                   "_note": "M06(v2.3.0): 롤 기둥(보 앞면)·외팔 축·허브 + 6004ZZ ×2, 안내 롤러 G1(UPPER 윗면)·꼭대기 롤러(HANGER 선반), 차지 U7_TAPE_ROLL Ø300×60·U7_TAPEWAY_H/V. 옛 U7_ROLL·U7_PATH_H 지움. U1_FRAME 리지드. 테이프 롤은 회전 대칭이라 조인트 없음"}
    for k, v in SHIFT_KEYS.items():
        if k in m["studies"]:
            m["studies"][k].setdefault("_keys_M06", v)
    for st in m["states"]:
        stp, sd = st["step"], st["study"]
        pts = SHIFT_KEYS.get(sd, [[0, -60]])
        val = pts[0][1]
        for (a, va), (b, vb) in zip(pts, pts[1:]):
            if a <= stp <= b:
                val = va if b == a else va + (vb - va) * (stp - a) / (b - a)
                break
        else:
            if stp >= pts[-1][0]:
                val = pts[-1][1]
        st["joints"]["J_U6_SHIFT"] = round(val, 3)
    json.dump(m, open(ROOT + "/machine.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json", len(m["joints"]), "joints", len(m["studies"]), "studies")


if __name__ == "__main__" and "--machine" in sys.argv:
    gen_machine()
