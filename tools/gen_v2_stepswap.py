# -*- coding: utf-8 -*-
"""STEPSWAP STEP대기 실물 교체 생성기 — v2.5.5 -> v2.5.6 (모델링부 2026-11-05)
지시서 docs/reports/mechanism/mech_step_wait.md. 보고서 docs/reports/mechanism/mech_STEPSWAP_model.md.
python -X utf8 -B tools/gen_v2_stepswap.py  -> tools/out/mech_STEPSWAP/edit.json, edit_meta.json
규칙(CLI 실측, 장난감 설계 t2·t3): file.insert_step matrix는 활성 컴포넌트 기준(로컬), solid.box·cylinder 좌표는 세계.
U5_LIFT 는 REST에서 세계 +30 Z(로컬 = 세계 - 30), U6_SHOE 는 세계 -60 X. 나머지 유닛은 항등.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m08 as m8  # noqa: E402  (tube(), r4)
from gen_v2_m02 import C, box, cyl, mat_assign  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
STEP = PRJ + "/purchased-step/"
OUT = os.path.join(ROOT, "out", "mech_STEPSWAP")
CL = os.path.join(OUT, "cl_out.json")      # 작업 전 component.list(compact) 결과


def rows(X, Y, Z, t):
    """로컬 축 X·Y·Z의 상(세계 또는 부모 좌표)과 원점 t -> row-major 3x4."""
    return [X[0], Y[0], Z[0], t[0], X[1], Y[1], Z[1], t[1], X[2], Y[2], Z[2], t[2]]


def act(comp):
    return C("component.activate", component=comp)


def ins(path, comp, m, renames, pn, desc, bom="purchased"):
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=m)]
    s += [C("body.rename", body=a, name=b) for a, b in renames]
    s.append(C("component.metadata.set", component=comp, part_number=pn, bom_type=bom, description=desc))
    return s


def cp(occ, d):
    return C("occurrence.copy", occurrence=occ, in_place=True, translate=[round(v, 4) for v in d])


def occ_translations(comp):
    d = json.load(open(CL, encoding="utf-8"))[0]
    for c in d["components"]:
        if c["name"] == comp:
            out = []
            for o in c["occurrences"]:
                t = o.get("transform")
                out.append((0.0, 0.0, 0.0) if not t else tuple(t[3][:3]))
            return out
    raise KeyError(comp)


PX, NX, PY, NY, PZ, NZ = (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def bolt_m(ax, t):
    """볼트 STEP(로컬 +X = 축, 원점 = 머리 밑면)."""
    ref = PZ if abs(ax[2]) < 0.5 else PX
    y = cross(ref, ax)
    return rows(ax, y, cross(ax, y), t)


# ====================================================================== 1. U1 기둥 HFS8-80160-1090 ×2
def s_columns():
    s = [C("solid.remove", bodies=["STEP대기_HFS8-80160-1090_M07_NX", "STEP대기_HFS8-80160-1090_M07_PX"]), act("U1_FRAME")]
    s += ins("HFS8-80160-1090/HFS8-80160-1090.stp", "HFS8-80160-1090_M07", rows(PZ, PY, NX, (-2340, 200, -840)),
             [("Boss-Extrude1", "HFS8-80160-1090_M07")], "HFS8-80160-1090",
             "Misumi HFS8-80160-1090 STEP, columns NX (:1) and PX (:2) (STEPSWAP)")
    s += [mat_assign(["HFS8-80160-1090_M07"], "Aluminum"), cp("HFS8-80160-1090_M07:1", (3530, 0, 0))]
    return s


# ====================================================================== 2. U5 먼 쪽 바퀴: 풀리·베어링·벨트
YC = (PY, PZ, PX)      # 로컬 X -> 세계 +Y


def s_u5_drive():
    s = [C("component.delete", component="STEP대기_HTPA60S5M150-A-N16"), act(0)]
    nm = "HTPA60S5M150-A-N16_M03"
    s += ins("HTPA60S5M150-A-N16/HTPA60S5M150-A-N16.stp", nm, rows(*YC, (-2220, 95.5, 390)),
             [("Cut-Extrude2", nm + "_HUB"), ("Revolve2[1]", nm + "_FLANGE1"), ("Revolve2[2]", nm + "_FLANGE2"),
              ("Cut-Extrude3", nm + "_SET1"), ("Cut-Extrude4", nm + "_SET2")], "HTPA60S5M150-A-N16",
             "Misumi HTPA60S5M150-A-N16 STEP, X drive pulley on VRXF output shaft (STEPSWAP)")
    s.append(C("joint.rigid_group", occurrences=["U5_WHEEL_F:1", nm + ":1"]))
    # 6200ZZ ×2 (아이들러 축, Y 97~106 · 106~115)
    s += [C("solid.remove", bodies=["STEP대기_6200ZZ_1", "STEP대기_6200ZZ_2", "STEP대기_HTBNS5M150-3960"]), act("U5_WHEEL_F")]
    b = "6200ZZ_M03"
    s += ins("6200ZZ/6200ZZ.stp", b, rows(*YC, (-390, 97, 390)),
             [("6200ZZ Outer ring", b + "_OUTER"), ("6200ZZ Inner ring", b + "_INNER"), ("6200ZZ Shield1", b + "_SHIELD1"),
              ("6200ZZ Shield2", b + "_SHIELD2")], "6200ZZ", "Misumi 6200ZZ STEP (balls not in STEP), idler bearings x2 (STEPSWAP)")
    s.append(cp(b + ":1", (0, 9, 0)))
    # 벨트 HTBO-S5M150-792: 곧은 STEP 띠 2토막(위·아래 가닥) + 감긴 반원 2(띠 단면 회전, 같은 컴포넌트)
    u, l = "HTBO-S5M150-792_M03", "HTBO-S5M150-792_M03_L"
    s += [act("U5_WHEEL_F")]
    s += ins("HTBO-S5M150-792/HTBO-S5M150-792.stp", u, rows(PX, PZ, NY, (-2220, 106, 439.5)), [("LPattern2", u)],
             "HTBO-S5M150-792", "Misumi HTBO-S5M150-792 open-end belt (rule 18, replaces HTBNS5M150-3960): upper run cut to "
             "pulley span + two wraps (belt section revolved) - REST shape")
    s += [act("U5_WHEEL_F")]
    s += ins("HTBO-S5M150-792/HTBO-S5M150-792.stp", l, rows(PX, NZ, PY, (-2220, 106, 340.5)), [("LPattern2", l)],
             "HTBO-S5M150-792", "lower run of the same belt HTBO-S5M150-792 (one belt drawn in two components; counted in "
             + u + ")", bom="reference")
    s += [act(u), box(None, -390, 1745, 97, 115, 436, 443, "cut", [u])]
    s += [act(l), box(None, -390, 1745, 97, 115, 337, 345, "cut", [l]), box(None, -2027, -2023, 97, 115, 337, 345, "cut", [l])]
    s += [act(u)]
    for tag, xc, x0, x1 in (("D", -2220, -2220, -2150), ("I", -390, -460, -390)):
        w = "%s_WRAP_%s" % (u, tag)
        s += [cyl(50.45, [xc, 98.5, 390], 15, [0, 1, 0], "new", name=w), cyl(47.25, [xc, 98.4, 390], 15.2, [0, 1, 0], "cut", [w]),
              box(None, x0, x1, 97, 115, 335, 445, "cut", [w])]
    s += [act(0)]
    return s


# ====================================================================== 3. U5 승강: MGPM25-40Z 실물 + 대차판·승강판 구멍 + 볼트
MX = -1920.0                       # MGP 가운데 X(임시 -1940에서 +20: 끝판 탭 Y 46 줄이 옆판 플랜지 CB5-12(-1975, 46)를 피함)
CAR_B = [(x, z) for x in (MX - 17, MX + 17) for z in (197.0, 241.0)]          # 몸 M6 탭(뒤, 깊이 12) <- 대차판 뒤에서
PLT_B = [(x, y) for x in (MX - 39, MX + 39) for y in (46.0, 72.0)]            # 끝판 M6 탭(밑, 깊이 8.46)
BLK_H = [(-1993.5, 284.0), (-1993.5, 316.0), (-1866.5, 284.0), (-1866.5, 316.0)]
CLAMP_B = [(x, z) for x in (-2035.0, -2015.0) for z in (332.0, 352.0)]
ARM_B = [(-1940.0, 88.0), (-1920.0, 88.0)]
FLG_B = [(x, y) for x in (-1975.0, -1835.0) for y in (-46.0, 46.0)]


def s_u5_lift():
    s = [C("solid.remove", bodies=["STEP대기_MGPM25-40Z_BODY", "P_M03_CAR_PLATE"] + ["STEP대기_CB6-20_M03_%d" % i for i in range(1, 5)]),
         act("U5_CAR")]
    P = "P_M03_CAR_PLATE"
    s += [box(P, -2045, -1825, 80, 92, 160, 420)]
    s += [cyl(2.75, [x, 79, z], 14, [0, 1, 0], "cut", [P]) for x, z in BLK_H + CLAMP_B]
    s += [cyl(3.3, [x, 79, z], 14, [0, 1, 0], "cut", [P]) for x, z in CAR_B]
    s += [cyl(2.1, [x, y, 408], 13, [0, 0, 1], "cut", [P]) for x, y in ARM_B]
    s += [mat_assign([P], "A5052")]
    g = "MGPM25-40Z_M03"
    s += ins("MGPM25-40Z/MGPM25-40Z.stp", g, rows(PZ, NX, NY, (MX, 59, 180)),
             [("MGPM25-40Z(0)_BODY", g + "_BODY"), ("MGPM25-40Z(0)_ROD", g + "_ROD"), ("MGP-Z_PLUG_25", g + "_PLUG")], "MGPM25-40Z",
             "SMC MGPM25-40Z STEP (retracted = REST). Body and plugs in U5_CAR, plate+rods sub-occurrence moved to U5_LIFT (STEPSWAP)")
    s += [C("component.unlock", component=g),
          C("occurrence.reparent", occurrence="MGPM25-40Z(0)_ROD:1", parent="U5_LIFT")]
    s += [act("U5_CAR")]
    s += ins("CB6-20/CB6-20.stp", "CB6-20_M03_CAR", bolt_m(NY, (CAR_B[0][0], 92, CAR_B[0][1])), [("Cut-Extrude1", "CB6-20_M03_CAR")],
             "CB6-20", "Misumi CB6-20 STEP, car plate (from behind) -> MGP body M6 tap, engagement 8 (STEPSWAP)")
    s += [cp("CB6-20_M03_CAR:1", (x - CAR_B[0][0], 0, z - CAR_B[0][1])) for x, z in CAR_B[1:]]
    # 승강판(로컬 Z 126~134 = 세계 156~164) 다시: 새 끝판 탭 자리 Ø6.6
    T = "P_M03_LIFT_TOP"
    s += [C("solid.remove", bodies=["STEP대기_MGPM25-40Z_PLATE", T] + ["STEP대기_CB6-20_M03_%d" % i for i in range(5, 9)]), act("U5_LIFT")]
    s += [box(T, -1990, -1820, -55, 78, 156, 164)]
    s += [cyl(3.3, [x, y, 155], 10, [0, 0, 1], "cut", [T]) for x, y in PLT_B]
    s += [cyl(2.1, [x, y, 155], 10, [0, 0, 1], "cut", [T]) for x, y in FLG_B]
    s += [cyl(3.3, [x, y, 149], 8, [0, 0, 1], "cut", ["P_M03_LIFT_SIDE_P"]) for x, y in PLT_B if y < 50]
    s += [mat_assign([T], "SUS304")]
    y46 = [p for p in PLT_B if p[1] < 50]
    s += ins("CB6-20/CB6-20.stp", "CB6-20_M03_LIFT", bolt_m(PZ, (y46[0][0], y46[0][1], 120)), [("Cut-Extrude1", "CB6-20_M03_LIFT")],
             "CB6-20", "Misumi CB6-20 STEP, side flange + lift top -> MGP plate M6 tap, engagement 6 (STEPSWAP)")
    s += [cp("CB6-20_M03_LIFT:1", (y46[1][0] - y46[0][0], 0, 0))]
    s += [act("U5_LIFT")]
    w = []
    for i, (x, y) in enumerate([p for p in PLT_B if p[1] > 50], 1):
        nm = "STEP대기_CB6-16_M03_%d" % i
        s += [cyl(5.0, [x, y, 150], 6, [0, 0, 1], "new", name=nm), cyl(3.0, [x, y, 156], 16, [0, 0, 1], "join", [nm])]
        w.append(nm)
    s += [mat_assign(w, "SCM435"), act(0)]
    s += [C("joint.rigid_group", occurrences=["U5_CAR:1", g + ":1", "MGPM25-40Z(0)_BODY:1", "MGP-Z_PLUG_25:1", "MGP-Z_PLUG_25:2"]),
          C("joint.rigid_group", occurrences=["U5_LIFT:1", "MGPM25-40Z(0)_ROD:1"])]
    return s


# ====================================================================== 4. U2 접시 볼트 SFB5-10 ×102
def s_fhs():
    s = []
    for old, new, base in (("STEP대기_FHS-M5-10_M04", "SFB5-10_M04", (-2100.0, -1500.0)),
                           ("STEP대기_FHS-M5-10_M04R", "SFB5-10_M04R", (-400.0, -250.0))):
        tr = occ_translations(old)
        s += [C("solid.remove", bodies=[old]), C("component.delete", component=old), act("U2_TABLE")]
        s += ins("SFB5-10/SFB5-10.stp", new, bolt_m(NZ, (base[0], base[1], -10.8)), [("Cut-Extrude1", new)], "SFB5-10",
                 "Misumi SFB5-10 (FHS-M5-10) flat head STEP, head top Z -8 (STEPSWAP, D-117)")
        s += [mat_assign([new], "SCM435")]
        s += [cp(new + ":1", t) for t in tr[1:]]
    s.append(act(0))
    return s


# ====================================================================== 5. U7 핀 MSTH6-20 ×2, U6 볼트 CB3-10 ×2
def s_small():
    s = [C("solid.remove", bodies=["STEP대기_MSTH6-20_M05_1", "STEP대기_MSTH6-20_M05_2"]), act("U7_CASSETTE")]
    s += ins("MSTH6-20/MSTH6-20.stp", "MSTH6-20_M05", rows(PX, PY, PZ, (58, -190, 300)), [("Tap1", "MSTH6-20_M05")], "MSTH6-20",
             "Misumi MSTH6-20 STEP, cassette locating pins (STEPSWAP)")
    s += [mat_assign(["MSTH6-20_M05"], "Steel"), cp("MSTH6-20_M05:1", (0, 65, 0))]
    s += [C("solid.remove", bodies=["STEP대기_CB3-10_M06_1", "STEP대기_CB3-10_M06_2"]), act("U6_SHOE")]
    s += ins("CB3-10/CB3-10.stp", "CB3-10_M06", bolt_m(PY, (2.5, -112, 23.5)), [("Cut-Extrude1", "CB3-10_M06")], "CB3-10",
             "Misumi CB3-10 STEP, shoe -> carrier M3 insert (STEPSWAP)")
    s += [mat_assign(["CB3-10_M06"], "SCM435"), cp("CB3-10_M06:1", (0, 0, 10)), act(0)]
    return s


# ====================================================================== 6. U8 공압: KQ2L08 ×6, 매니폴드·밸브·피팅, 경광등, 관
REG_X = [700.0, 800.0, 900.0]
RY, ZP = 95.1, 511.0
ST = [1044.5 + 5.25 + 10.5 * k for k in range(6)]
VY = 100.0                     # 밸브 붙는 면(베이스 윗면) Y
PORT_Y = VY - 23.5             # 밸브 A·B 포트 면 Y 76.5
ZA, ZB = 351.0 - 5.1, 351.0 + 5.1
MB = [(1117 + z, 374.5 + x) for z in (-77.2, -4.8) for x in (-31.5, -15.5)]   # 베이스 M4 관통 (X, Z)
LAMP_H = [(1190.0, 290.0), (1172.679, 260.0), (1207.321, 260.0)]


def s_pneu():
    gone = ("STEP대기_KQ2L08-01AS_M08_PX", "STEP대기_KQ2L08-01AS_M08_NX", "STEP대기_SS5Y3-20-06_M08", "STEP대기_SY3120-5LZD-M5_M08",
            "STEP대기_CB4-20_M08", "KQ2L06-M5A_M08_NZ", "KQ2L06-M5A_M08_PZ", "STEP대기_LR6-302WJBW-RYG_M08", "STEP대기_CB4-12_M08") + tuple(TUBES)
    # 바디를 먼저 지운다: 루트에서 그려 옮긴 바디는 컴포넌트만 지우면 루트로 돌아온다(장난감 설계 t4 실측)
    # KQ2L06-M5A_M08_NZ/PZ 는 STEP으로 넣은 컴포넌트(바디를 만든 Import 피처가 그 안에 있음) -> 지우기만(2차 실행: Remove가 사라진 바디를 찾지 못해 실패)
    s = [C("solid.remove", bodies=[g for g in gone if not g.startswith("KQ2L06-M5A")])] + [C("component.delete", component=c) for c in gone]
    rig = []
    # 레귤레이터 이음(로컬 Y = 나사 축, 포트 면 Y 4.0, 관 출구 로컬 +X at Y 15.6)
    for side, sg in (("PX", 1), ("NX", -1)):
        nm = "KQ2L08-01AS_M08_" + side
        ly = PX if sg > 0 else NX
        s += [act("U8_PNEU")]
        s += ins("KQ2L08-01AS/KQ2L08-01AS.stp", nm, rows(NZ, ly, cross(NZ, ly), (REG_X[0] + sg * 8.5, RY, ZP)), [("KQ2L08-01AS", nm)],
                 "KQ2L08-01AS", "SMC KQ2L08-01AS elbow STEP, regulator %s port (STEPSWAP)" % side)
        s += [cp(nm + ":1", (100, 0, 0)), cp(nm + ":1", (200, 0, 0))]
        rig += ["%s:%d" % (nm, i) for i in (1, 2, 3)]
    # 매니폴드 베이스: 로컬 Z(길이 82) -> 세계 +X, 로컬 Y(두께 20) -> -Y(밑면 Y 120 = 보 앞면), 로컬 X(폭 49) -> +Z
    R = (PZ, NY, PX)
    s += [act("U8_PNEU")]
    s += ins("SS5Y3-20-06/SS5Y3-20-06.stp", "SS5Y3-20-06_M08", rows(*R, (1117, 120, 374.5)), [("SS5Y3-20-06", "SS5Y3-20-06_M08")],
             "SS5Y3-20-06", "SMC SS5Y3-20-06 manifold base 6 stations STEP (STEPSWAP)")
    rig.append("SS5Y3-20-06_M08:1")
    s += [act("U8_PNEU")]
    s += ins("SY3120-5LZD-M5/SY3120-5LZD-M5.stp", "SY3120-5LZD-M5_M08", rows(*R, (ST[0], VY, 351.0)),
             [("SY3120-5LZD-M5_B", "SY3120-5LZD-M5_M08")], "SY3120-5LZD-M5",
             "SMC SY3120-5LZD-M5 valve STEP, stations 1-6, solenoid down (STEPSWAP)")
    s += [cp("SY3120-5LZD-M5_M08:1", (10.5 * k, 0, 0)) for k in range(1, 6)]
    rig += ["SY3120-5LZD-M5_M08:%d" % i for i in range(1, 7)]
    # 피팅 KQ2L06-M5A: 로컬 X = 출구, 로컬 Y = 포트 바깥 법선, 원점 = 포트 면
    # 새 이름 _M08S_: 지운 바디 이름은 Remove 피처가 잡고 있어 body.rename 대상이 될 수 없다(CLI 1차 실행 291단계 실패)
    for nm, lx, z, sts in (("KQ2L06-M5A_M08S_NZ", NZ, ZA, range(6)), ("KQ2L06-M5A_M08S_PZ", PZ, ZB, (0, 1, 3, 4, 5))):
        sts = list(sts)
        s += [act("U8_PNEU")]
        s += ins("KQ2L06-M5A/KQ2L06-M5A.stp", nm, rows(lx, NY, cross(lx, NY), (ST[sts[0]], PORT_Y, z)), [("KQ2L06-M5A", nm)],
                 "KQ2L06-M5A", "SMC KQ2L06-M5A elbow STEP on SY3120 A/B port (STEPSWAP)")
        s += [cp(nm + ":1", (ST[k] - ST[sts[0]], 0, 0)) for k in sts[1:]]
        rig += ["%s:%d" % (nm, i) for i in range(1, len(sts) + 1)]
    # 베이스 고정 볼트 M4 ×4: 베이스 두께 20 + 보 앞벽 물림 5 -> CB4-25(STEP 없음, 임시)
    s += [C("component.create", name="STEP대기_CB4-25_M08", parent="U8_PNEU", activate=True)]
    bn = "STEP대기_CB4-25_M08"
    x0, z0 = MB[0]
    s += [cyl(3.5, [x0, VY - 4, z0], 4, [0, 1, 0], "new", name=bn), cyl(2.0, [x0, VY, z0], 25, [0, 1, 0], "join", [bn]),
          mat_assign([bn], "SCM435"),
          C("component.metadata.set", component=bn, part_number="CB4-25", bom_type="purchased",
            description="placeholder Misumi CB4-25 (head 7x4, M4x25): SS5Y3 base -> beam front wall M4 tap (STEPSWAP, no STEP: login)")]
    s += [act(0)] + [cp(bn + ":1", (x - x0, 0, z - z0)) for x, z in MB[1:]]
    # 경광등 LR6: 로컬 Z 위, 밑면 로컬 Z -12 = 보 윗면 650, 구멍 PCD 40 -> 세계 LAMP_H(180° 돌림)
    s += [act("U8_PNEU")]
    lr = "LR6-302WJBW-RYG_M08"
    s += ins("LR6-302WJBW-RYG/LR6-302WJBW-RYG.stp", lr, rows(NX, NY, PZ, (1190, 270, 662)),
             [("brep_1", lr + "_1"), ("brep_2", lr + "_2"), ("brep_3", lr + "_3"), ("brep_6", lr + "_4"), ("brep_1 (2)", lr + "_5")],
             "LR6-302WJBW-RYG", "PATLITE LR6-302WJBW-RYG STEP (representative LR6-302WJB), on beam top (STEPSWAP)")
    rig.append(lr + ":1")
    s += [act("U8_PNEU")]
    s += ins("CB4-20/CB4-20.stp", "CB4-20_M08_LAMP", bolt_m(NZ, (LAMP_H[0][0], LAMP_H[0][1], 661.5)), [("Cut-Extrude1", "CB4-20_M08_LAMP")],
             "CB4-20", "Misumi CB4-20 STEP, LR6 base (hole top Z 661.5) -> beam top M4 tap, engagement 8 (STEPSWAP)")
    s += [mat_assign(["CB4-20_M08_LAMP"], "SCM435")]
    s += [cp("CB4-20_M08_LAMP:1", (x - LAMP_H[0][0], y - LAMP_H[0][1], 0)) for x, y in LAMP_H[1:]]
    rig += ["CB4-20_M08_LAMP:%d" % i for i in (1, 2, 3)]
    s += [act(0)]
    # 관 다시
    for nm0, (r, pts) in tubes().items():
        nm = nm0.replace("_M08_", "_M08S_")
        pn = nm.split("_")[0]
        s += [C("component.create", name=nm, parent="U8_PNEU", activate=False)]
        tc = json.loads(json.dumps(m8.tube(nm, pts, r, 20.0 if r > 3.5 else 15.0)).replace('"SK_%s"' % nm, '"SK_%s_SW"' % nm))
        s += tc
        s += [mat_assign([nm], "Default"), C("component.move_bodies", bodies=[nm], component=nm),
              C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased",
                description="SMC %s polyurethane tube, cut to length (route M08, re-routed STEPSWAP)" % pn)]
    s.append(C("joint.rigid_group", occurrences=["U8_PNEU:1"] + rig))
    return s


A0 = lambda x: (x, PORT_Y - 13.5, ZA - 14.5)    # A 피팅 관 끝(출구 -Z) = (x, 63, 331.4)
B0 = lambda x: (x, PORT_Y - 13.5, ZB + 14.5)    # B 피팅 관 끝(출구 +Z) = (x, 63, 370.6)
TUBES = (["TU0805_M08_REG_IN_%d" % i for i in (1, 2, 3)] + ["TU0805_M08_REG_OUT_%d" % i for i in (1, 2, 3)]
         + ["TU0604_M08_U4_A", "TU0604_M08_U4_B", "TU0604_M08_U6", "TU0604_M08_U5_A", "TU0604_M08_U5_B"]
         + ["TU0604_M08_U7_%d" % i for i in range(1, 7)])


def tubes():
    T = {}
    zport = [374.5 - 40, 374.5 - 23.5, 374.5 - 7]     # 베이스 -X 끝면 포트 Rc1/8 (Y 107.5)
    for i, x in enumerate(REG_X):
        zi = 305.0 + 10 * i
        xi, xo, zt = x - 24.1, x + 24.1, ZP - 16.4
        T["TU0805_M08_REG_IN_%d" % (i + 1)] = (4.0, [(xi, RY, zt), (xi, RY, zi), (xi, 50, zi), (1140, 50, zi)])
        T["TU0805_M08_REG_OUT_%d" % (i + 1)] = (4.0, [(xo, RY, zt), (xo, RY, zport[i]), (xo, 107.5, zport[i]), (1035, 107.5, zport[i])])
    X1, X2, X3 = ST[0], ST[1], ST[2]
    Y = PORT_Y - 13.5
    T["TU0604_M08_U4_A"] = (3.0, [A0(X1), (X1, Y, 270), (X1, 105, 270), (-165, 105, 270), (-165, 105, 330), (-165, 45, 330)])
    T["TU0604_M08_U4_B"] = (3.0, [B0(X1), (X1, Y, 385), (X1, 22, 385), (1020, 22, 385), (1020, 22, 278), (1020, 112, 278),
                                  (-175, 112, 278), (-175, 112, 320), (-175, 45, 320)])
    T["TU0604_M08_U6"] = (3.0, [A0(X3), (X3, Y, 262), (X3, 105, 262), (-347, 105, 262), (-347, 105, 158.65),
                                (-347, -130, 158.65), (-289.5, -130, 158.65)])
    T["TU0604_M08_U5_A"] = (3.0, [A0(X2), (X2, Y, 295), (X2, 14, 295), (1032, 14, 295), (1032, 14, 690), (1032, 190, 690), (-1242, 190, 690)])
    T["TU0604_M08_U5_B"] = (3.0, [B0(X2), (X2, Y, 400), (1040, Y, 400), (1040, Y, 680), (1040, 182, 680), (-1242, 182, 680)])
    lane = {3: 130.0, 4: 140.0, 5: 150.0}
    turnA = {3: 127.5, 4: 112.5, 5: 97.5}
    turnB = {3: 135.0, 4: 120.0, 5: 105.0}
    n = 0
    for st in (3, 4, 5):
        x = ST[st]
        n += 1
        T["TU0604_M08_U7_%d" % n] = (3.0, [A0(x), (x, Y, 295), (x, 14, 295), (x, 14, 670), (x, lane[st], 670),
                                           (turnA[st], lane[st], 670), (turnA[st], -40, 670)])
        n += 1
        T["TU0604_M08_U7_%d" % n] = (3.0, [B0(x), (x, Y, 660), (x, lane[st], 660), (turnB[st], lane[st], 660), (turnB[st], -40, 660)])
    return T


def s_final():
    # 6200ZZ STEP은 안 리지드 묶음이 있어 유닛과 묶지 않으면 floating(1차 저장 후보 joint.list) -> 유닛과 리지드
    return [C("joint.rigid_group", occurrences=["U5_WHEEL_F:1", "6200ZZ_M03:1", "6200ZZ_M03:2"]), act(0),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("component.rename", component=0, name="FSAP_v2.5.6"),
            C("document.metadata.set", key="description",
              value="STEPSWAP mechanism: STEP-wait parts swapped to purchased STEP (pulley, bearings, belt, MGP, bolts, pins, columns, pneumatics)")]


STAGES = [("columns", s_columns), ("u5_drive", s_u5_drive), ("u5_lift", s_u5_lift), ("fhs", s_fhs), ("small", s_small),
          ("pneu", s_pneu), ("final", s_final)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"), ensure_ascii=False)
        if not only or nm in only:
            allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.5.5.sc", "result": "3D_Modeling/FSAP_v2.5.6.sc", "generator": "tools/gen_v2_stepswap.py"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("commands", len(allc))


if __name__ == "__main__":
    main()


def patch_machine():
    p = os.path.join(ROOT, "machine.json")
    m = json.load(open(p, encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.5.6.sc"
    rep = {"U1_FRAME": {"STEP대기_HFS8-80160": ["HFS8-80160-1090_M07"]},
           "U2_TABLE": {"STEP대기_FHS-M5-10_M04": ["SFB5-10_M04"]},
           "U5_WHEEL_F": {"STEP대기_HTPA60S5M150-A-N16": ["HTPA60S5M150-A-N16_M03"], "STEP대기_6200ZZ_": ["6200ZZ_M03"],
                          "STEP대기_HTBNS5M150-3960": ["HTBO-S5M150-792_M03"], "STEP대기_MGPM25-40Z_": ["MGPM25-40Z_M03", "MGPM25-40Z(0)_", "MGP-Z_PLUG_25"],
                          "STEP대기_CB6-20_M03": ["CB6-20_M03", "STEP대기_CB6-16_M03"]},
           "U7_TAPE": {"STEP대기_MSTH6-20_M05": ["MSTH6-20_M05"]},
           "U6_SHOE": {"STEP대기_CB3-10_M06": ["CB3-10_M06"]},
           "U8_PNEU": {"STEP대기_KQ2L08": ["KQ2L08-01AS_M08"], "STEP대기_SS5Y3": ["SS5Y3-20-06_M08"], "STEP대기_SY3120": ["SY3120-5LZD-M5_M08"],
                       "STEP대기_CB4-20_M08": ["STEP대기_CB4-25_M08", "CB4-20_M08_LAMP"], "STEP대기_LR6": ["LR6-302WJBW-RYG_M08"],
                       "STEP대기_CB4-12_M08": []}}
    for u, r in rep.items():
        parts = m["units"][u]["parts"]
        new = []
        for x in parts:
            new += r.get(x, [x])
        m["units"][u]["parts"] = new
    m["units"]["U5_WHEEL_F"]["_note"] = m["units"]["U5_WHEEL_F"].get("_note", "") + (
        " STEPSWAP(v2.5.6): MGPM25-40Z 실물(가운데 X -1940 -> -1920, 몸·플러그 U5_CAR, 끝판+봉 하위 부품 U5_LIFT), 벨트 HTBO-S5M150-792(REST 형상: "
        "곧은 STEP 위·아래 가닥 + 감긴 반원 2), 구동 풀리 N16·6200ZZ ×2 실물. 조인트·행정 그대로")
    m["units"]["U8_PNEU"]["_note"] = m["units"]["U8_PNEU"].get("_note", "") + (
        " STEPSWAP(v2.5.6): SS5Y3-20-06 베이스(보 앞면 Y 120, X 1035~1117, Z 325.5~374.5)+SY3120 ×6(솔레노이드 아래), KQ2L06-M5A 피팅 포트 면 Y 76.5로, "
        "관 17줄 다시(_M08S_), KQ2L08 실물, LR6 실물 + CB4-20 ×3. KDM10-06은 STEP대기 그대로(미완)")
    m.setdefault("_history", []).append("2026-11-05 STEPSWAP v2.5.6: STEP대기 실물 교체(조인트·행정·연구 변화 없음)")
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json patched")


if __name__ == "__main__" and "--machine" in sys.argv:
    patch_machine()
