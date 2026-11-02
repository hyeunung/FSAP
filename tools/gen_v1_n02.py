# -*- coding: utf-8 -*-
"""N02 U3 진공 원판 + 회전 조향 생성기 — v1.0.5 -> v1.0.6 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_N02_select.md(N02-C3 고친 안)를 그린다.
python -B tools/gen_v1_n02.py -> tools/out/mech_N02/edit.json, edit_meta.json, model/stage_*.json
좌표: 바늘점 원점 mm, 작업면 Z 0. REST(J_U4_X·Y 0, J_U3_ROT 0)에서 그린다.
원판 축 상대 (x, y) -> 월드 (x - 900, y - 400). Z는 월드.
- 바디는 루트에서 피처를 다 만든 뒤 컴포넌트로 옮긴다(움직이는 컴포넌트 안에서 자르면 자르기가 월드에 고정, DC-05 메모).
- U4_Y_CARR 탭은 그 바디를 만든 Box39·Box40 바로 뒤(BodyTransfer31 앞)로 마커를 돌려 넣는다.
- 판금(SPCC t4 R4 K0.44)은 sheet.flange contour, 구멍은 평행 스케치 + 압출 자르기(DC-04 메모).
- 지시서와 다르게 그린 곳: 씰 볼트 각 30·150·270°(90°는 KQ2H06 포트와 Z 0.5 겹침),
  +Y 벽 관 구멍 X -20(브래킷 피함), O링을 사각 단면 고리(토러스 간섭 계산 느림), 풀리 임시 외형을 양 플랜지 + 몸통(벨트와 이 물림 겹침을 피함), 모터 축 구멍을 장공 ±5(벨트 장력 이동).
"""
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N02")
CX, CY = -900.0, -400.0
PS = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/"
CB12, CB20, ZH = PS + "CB5-12/CB5-12.stp", PS + "CB5-20/CB5-20.stp", PS + "ZH10DSA-06-06-08/ZH10DSA-06-06-08.stp"

PLATE, SHAFT, COLLAR = "P_N02_PLATE", "P_N02_SHAFT", "P_N02_COLLAR"
FRAME, HOUSING, RET, SEAL, MBKT = "P_N02_FRAME", "P_N02_HOUSING", "P_N02_RETAINER", "P_N02_SEAL", "P_N02_MBKT"
PUL60, PUL20, BELT = "STEP대기_HTPA60S5M150-A-N30", "STEP대기_HTPA20S5M150-A-N12", "STEP대기_HTBN635S5M-150"
CRBH, KQ2, MOTOR = "STEP대기_CRBH5013", "STEP대기_KQ2H06-M5A", "STEP대기_AZM66AC-PS25"
OR1, OR2 = "STEP대기_JIS-P25_1", "STEP대기_JIS-P25_2"
SEAL_ANG = (30, 150, 270)


def C(cmd, **p):
    return {"command": cmd, "params": p}


def W(x, y):
    return [round(CX + x, 4), round(CY + y, 4)]


def cyl(r, h, x, y, z, op="new", name=None, tg=None, axis="Z"):
    b = W(x, y) + [z]
    p = {"radius": r, "height": h, "base": b, "axis": axis, "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.cylinder", **p)


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0, "corner": W(x0, y0) + [z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def polar(r, deg):
    a = math.radians(deg)
    return (round(r * math.cos(a), 4), round(r * math.sin(a), 4))


PCD45 = [polar(40, a) for a in (45, 135, 225, 315)]
WEB4 = [(sx * 45, sy * 60) for sx in (1, -1) for sy in (1, -1)]
HB4 = [(sx * 45, sy * 55) for sx in (1, -1) for sy in (1, -1)]
SEAL3 = [polar(37.5, a) for a in SEAL_ANG]
MB2 = [(-112.5, 30), (-112.5, -30)]


def down_plane(z, name):
    """법선 -Z 평면: 스케치 (u, v) = (X, -Y)."""
    return C("sketch.create", plane={"origin": [0, 0, z], "x_dir": [1, 0, 0], "y_dir": [0, -1, 0]}, name=name)


def uv_down(x, y):
    w = W(x, y)
    return [w[0], -w[1]]


def rev_plane(x, y, name):
    """축 단면 평면(축을 지남, 법선 -Y): (u, v) = (X - 축X, Z)."""
    w = W(x, y)
    return C("sketch.create", plane={"origin": [w[0], w[1], 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name=name)


def revolve(x, y, name, body, pts):
    w = W(x, y)
    return [rev_plane(x, y, "SK_" + name), C("sketch.line", points=pts, closed=True), C("sketch.finish"),
            C("solid.revolve", axis={"origin": [w[0], w[1], 0], "dir": [0, 0, 1]}, operation="new", body_name=body)]


# ---------------- stage 1: 지우기·캐리어 탭·조인트 한계 ----------------
def stage_prep():
    st = [C("motion.play", study="REST", step=0, quiet=True),
          C("solid.remove", bodies=["U3_PLATE", "U3_COLUMN", "U3_DRIVE"]),
          C("timeline.roll_to", feature="Box40")]
    for (x, y) in WEB4 + SEAL3 + MB2:   # 18) U4_Y_CARR M5 탭 Ø4.2 깊이 12 (윗면 Z -230)
        st.append(cyl(2.1, 12, x, y, -242, "cut", tg=["U4_Y_CARR"]))
    st += [C("timeline.rollback", position="end"),
           C("joint.limits", joint="J_U4_X", min=-200, max=1217.5)]
    return st


# ---------------- stage 2: 판금 ----------------
def stage_sheet():
    st = [C("sheet.manage_rules", name="SPCC_t4", thickness="4", bend_radius="4", k_factor="0.44", active=True)]
    # 6) 틀 ㄷ자: 단면 YZ(법선 +X), X -55 ~ 55
    w0 = W(-55, 0)
    st += [C("sketch.create", plane={"origin": [w0[0], 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_N02_FRAME"),
           C("sketch.line", points=[[CY + 75, -131], [CY + 75, -230], [CY - 75, -230], [CY - 75, -131]]),
           C("sketch.finish"),
           C("sheet.flange", type="contour", sketch="SK_N02_FRAME", curves=["l1", "l2", "l3"], distance=110, rule="SPCC_t4", body_name=FRAME)]
    # 14) 모터 받침 Z자: 단면 XZ(법선 -Y), Y 50 -> -50
    st += [C("sketch.create", plane={"origin": [0, CY + 50, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_N02_MBKT"),
           C("sketch.line", points=[[CX - 100, -230], [CX - 160, -230], [CX - 160, -199], [CX - 270, -199]]),
           C("sketch.finish"),
           C("sheet.flange", type="contour", sketch="SK_N02_MBKT", curves=["l1", "l2", "l3"], distance=100, rule="SPCC_t4", body_name=MBKT)]
    return st


def stage_sheet_holes():
    st = []
    # 벽 구멍 Ø5.5 ×2씩 (X ±35, Z -143): +Y 벽 바깥면에서 -Y로 두 벽을 뚫음
    st += [C("sketch.create", plane={"origin": [0, CY + 75, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_N02_FRAME_H1")]
    st += [C("sketch.circle.center", center=[CX + x, -143], radius=2.75) for x in (35, -35)]
    st += [C("sketch.finish"), C("solid.extrude", distance=150, operation="cut", targets=[FRAME])]
    # +Y 벽 관 구멍 Ø10 (X -20, Z -210): 지시 X 0은 ZH10DSA 브래킷(X -0.45~8.55)이 반쯤 막아 X -20으로 옮김
    st += [C("sketch.create", plane={"origin": [0, CY + 75, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_N02_FRAME_H2"),
           C("sketch.circle.center", center=[CX - 20, -210], radius=5), C("sketch.finish"),
           C("solid.extrude", distance=4, operation="cut", targets=[FRAME])]
    # 웹 구멍(틀) + 아래 날개 구멍(모터 받침): Z -226 -> -230
    st += [down_plane(-226, "SK_N02_WEB_H")]
    st += [C("sketch.circle.center", center=uv_down(x, y), radius=2.75) for (x, y) in WEB4 + SEAL3 + MB2]
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[FRAME, MBKT])]
    # 윗 날개: 모터 축 장공 Ø36 ±5, 장착 장공 4.5 ±5 (□60 구멍 자리 49.5)
    st += [down_plane(-195, "SK_N02_MBKT_H"),
           C("sketch.slot.center_to_center", p0=uv_down(-220, 0), p1=uv_down(-210, 0), width=36)]
    for sx in (1, -1):
        for sy in (1, -1):
            hx, hy = -215 + sx * 24.75, sy * 24.75
            st.append(C("sketch.slot.center_to_center", p0=uv_down(hx - 5, hy), p1=uv_down(hx + 5, hy), width=4.5))
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[MBKT])]
    return st


# ---------------- stage 3: 가공품·임시 형상 ----------------
def stage_solid():
    st = []
    # 1) 원판
    st += [cyl(60, 15, 0, 0, -15, name=PLATE), cyl(4, 15, 0, 0, -15, "cut", tg=[PLATE])]
    st += [cyl(2.1, 12, x, y, -15, "cut", tg=[PLATE]) for (x, y) in PCD45]
    st += [down_plane(0, "SK_N02_PLATE_RING")]
    st += [C("sketch.circle.center", center=uv_down(0, 0), radius=r) for r in (23.5, 26.5, 43.5, 46.5)]
    st += [C("sketch.finish"),
           C("solid.extrude", distance=2, operation="cut", targets=[PLATE], exact_regions=True,
             profiles=[{"point": uv_down(25, 0)}, {"point": uv_down(45, 0)}])]
    st += [down_plane(0, "SK_N02_PLATE_RAD")]
    for a in (0, 90, 180, 270):
        if a in (0, 180):
            s = 1 if a == 0 else -1
            st.append(C("sketch.rectangle.two_point", p0=uv_down(s * 10, -1.5), p1=uv_down(s * 45, 1.5)))
        else:
            s = 1 if a == 90 else -1
            st.append(C("sketch.rectangle.two_point", p0=uv_down(-1.5, s * 10), p1=uv_down(1.5, s * 45)))
    st += [C("sketch.finish"), C("solid.extrude", distance=2, operation="cut", targets=[PLATE])]
    # 2) 축(회전 단면)
    st += revolve(0, 0, "N02_SHAFT", SHAFT, [
        [4, -15], [50, -15], [50, -25], [20, -25], [20, -136], [28, -136], [28, -142], [25, -142], [25, -155],
        [15, -155], [15, -190], [12.5, -190], [12.5, -222], [0, -222], [0, -212], [4, -212]])
    st += [cyl(2.75, 10, x, y, -25, "cut", tg=[SHAFT]) for (x, y) in PCD45]
    st.append(cyl(2, 30, 0, -15, -210, "cut", tg=[SHAFT], axis="Y"))
    # 3) 칼라
    st += [cyl(29, 10, 0, 0, -165, name=COLLAR), cyl(15, 10, 0, 0, -165, "cut", tg=[COLLAR])]
    # 4) 축 풀리 60T(양 플랜지 r50, 몸통 r47.2 = 외경 94.4)
    st += revolve(0, 0, "N02_PUL60", PUL60, [
        [15, -190], [50, -190], [50, -188], [47.2, -188], [47.2, -167], [50, -167], [50, -165], [15, -165]])
    # 7) 하우징
    st += [box(HOUSING, -55, 55, -71, 71, -155, -131),
           cyl(40, 13, 0, 0, -155, "cut", tg=[HOUSING]), cyl(33, 11, 0, 0, -142, "cut", tg=[HOUSING])]
    for x in (35, -35):
        st.append(cyl(2.1, 10, x, 61, -143, "cut", tg=[HOUSING], axis="Y"))
        st.append(cyl(2.1, 10, x, -71, -143, "cut", tg=[HOUSING], axis="Y"))
    st += [cyl(2.1, 12, x, y, -155, "cut", tg=[HOUSING]) for (x, y) in HB4]
    # 8) 크로스 롤러
    st += [cyl(40, 13, 0, 0, -155, name=CRBH), cyl(25, 13, 0, 0, -155, "cut", tg=[CRBH])]
    # 9) 누름 링
    st += [box(RET, -55, 55, -71, 71, -160, -155), cyl(33, 5, 0, 0, -160, "cut", tg=[RET])]
    st += [cyl(2.75, 5, x, y, -160, "cut", tg=[RET]) for (x, y) in HB4]
    # 10) 진공 씰 슬리브(회전 단면) + 포트
    st += revolve(0, 0, "N02_SEAL", SEAL, [
        [12.5, -226], [45, -226], [45, -220], [30, -220], [30, -195], [12.5, -195], [12.5, -200.65],
        [15.2, -200.65], [15.2, -205.35], [12.5, -205.35], [12.5, -208], [14.5, -208], [14.5, -212],
        [12.5, -212], [12.5, -214.65], [15.2, -214.65], [15.2, -219.35], [12.5, -219.35]])
    st += [cyl(2.75, 6, x, y, -226, "cut", tg=[SEAL]) for (x, y) in SEAL3]
    st += [box(None, -11, 11, 28, 31, -215.5, -204.5, "cut", [SEAL]),
           cyl(2.1, 14, 0, 14, -210, "cut", tg=[SEAL], axis="Y")]
    # 11) O링 P25 ×2: 사각 단면 고리 Ø25/Ø30.4 × 3.5(홈을 채우는 외곽). 토러스는 간섭 계산이 160 s/쌍이라 바꿈
    for z, n in ((-217, OR1), (-203, OR2)):
        st += [cyl(15.2, 3.5, 0, 0, z - 1.75, name=n), cyl(12.5, 3.5, 0, 0, z - 1.75, "cut", tg=[n])]
    # 12) KQ2H06-M5A: 몸 Ø11 Y 30~50 + 나사 M5 Y 28~30
    st += [cyl(5.5, 20, 0, 30, -210, name=KQ2, axis="Y"), cyl(2.5, 2, 0, 28, -210, "join", tg=[KQ2], axis="Y")]
    # 15) 모터 AZM66AC-PS25 임시 외형
    st += [box(MOTOR, -245, -185, -30, 30, -364, -199), cyl(6, 34, -215, 0, -199, "join", tg=[MOTOR])]
    # 16) 모터 풀리 20T(플랜지 r19, 몸통 r15.35)
    st += revolve(-215, 0, "N02_PUL20", PUL20, [
        [6, -190], [19, -190], [19, -188], [15.35, -188], [15.35, -167], [19, -167], [19, -165], [6, -165]])
    # 17) 벨트: 두 원의 볼록 껍질 차, Z -185 ~ -170
    st += [C("sketch.create", plane={"origin": [0, 0, -185], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_N02_BELT")]
    for (R, r) in ((51.2, 19.3), (47.8, 15.9)):
        nx = -(R - r) / 215.0
        ny = math.sqrt(1 - nx * nx)
        c1, c2 = W(0, 0), W(-215, 0)
        p1t = [c1[0] + R * nx, c1[1] + R * ny]
        p1b = [c1[0] + R * nx, c1[1] - R * ny]
        p2t = [c2[0] + r * nx, c2[1] + r * ny]
        p2b = [c2[0] + r * nx, c2[1] - r * ny]
        p1t, p1b, p2t, p2b = [[round(v, 4) for v in p] for p in (p1t, p1b, p2t, p2b)]
        st += [C("sketch.line", points=[p1t, p2t]),
               C("sketch.arc.three_point", start=p2t, end=p2b, through=[c2[0] - r, c2[1]]),
               C("sketch.line", points=[p2b, p1b]),
               C("sketch.arc.three_point", start=p1b, end=p1t, through=[c1[0] + R, c1[1]])]
    st += [C("sketch.finish"), C("solid.extrude", distance=15, operation="new", body_name=BELT)]
    return st


# ---------------- stage 4: 재질·컴포넌트 ----------------
U3_BODIES = [PLATE, SHAFT, COLLAR, PUL60]
U4_BODIES = [FRAME, HOUSING, CRBH, RET, SEAL, OR1, OR2, KQ2, MBKT, MOTOR, PUL20, BELT]


def stage_assign():
    return [
        C("material.create", name="A5052", density_g_cm3=2.68, color="#c9cdd2"),
        C("material.create", name="SPCC", density_g_cm3=7.85, color="#7d8288"),
        C("material.create", name="A2017", density_g_cm3=2.79, color="#d4d7db"),
        C("material.create", name="NBR", density_g_cm3=1.25, color="#1e1e1e"),
        C("material.create", name="CR_GF", density_g_cm3=1.35, color="#2a2a2a"),
        C("material.assign", bodies=[PLATE, HOUSING, RET, SEAL], material="A5052"),
        C("material.assign", bodies=[SHAFT, COLLAR], material="S45C"),
        C("material.assign", bodies=[FRAME, MBKT], material="SPCC"),
        C("material.assign", bodies=[PUL60, PUL20], material="A2017"),
        C("material.assign", bodies=[CRBH, MOTOR], material="Steel"),
        C("material.assign", bodies=[OR1, OR2], material="NBR"),
        C("material.assign", bodies=[BELT], material="CR_GF"),
        C("material.assign", bodies=[KQ2], material="Brass"),
        C("component.move_bodies", bodies=U3_BODIES, component="U3_ROT"),
        C("component.move_bodies", bodies=U4_BODIES, component="U4_Y"),
    ]


# ---------------- stage 5: 실물 STEP(ZH10DSA·볼트) ----------------
def mat(d, x, y, z):
    """볼트 STEP 국소 +X(나사 방향) -> 월드 d. 자리면 = (x, y, z)."""
    w = W(x, y)
    rows = {"+Z": [[0, 0, -1], [0, 1, 0], [1, 0, 0]], "-Z": [[0, 0, 1], [0, 1, 0], [-1, 0, 0]],
            "-Y": [[0, 0, -1], [-1, 0, 0], [0, 1, 0]], "+Y": [[0, 0, 1], [1, 0, 0], [0, 1, 0]]}[d]
    t = [w[0], w[1], z]
    return [v for i in range(3) for v in (rows[i] + [t[i]])]


def bolt_list():
    b = []   # (이름, STEP, 방향, x, y, 자리면 z, 소속)
    for i, (x, y) in enumerate(PCD45, 1):
        b.append(("CB5-20_N02P_%d" % i, CB20, "+Z", x, y, -25, "U3_ROT"))
    n = 0
    for x in (35, -35):
        n += 1; b.append(("CB5-12_N02Y_%d" % n, CB12, "-Y", x, 75, -143, "U4_Y"))
        n += 1; b.append(("CB5-12_N02Y_%d" % n, CB12, "+Y", x, -75, -143, "U4_Y"))
    for (x, y) in HB4:
        n += 1; b.append(("CB5-12_N02Y_%d" % n, CB12, "+Z", x, y, -160, "U4_Y"))
    for (x, y) in WEB4:
        n += 1; b.append(("CB5-12_N02Y_%d" % n, CB12, "-Z", x, y, -226, "U4_Y"))
    for (x, y) in MB2:
        n += 1; b.append(("CB5-12_N02Y_%d" % n, CB12, "-Z", x, y, -226, "U4_Y"))
    for i, (x, y) in enumerate(SEAL3, 1):
        b.append(("CB5-20_N02Y_%d" % i, CB20, "-Z", x, y, -220, "U4_Y"))
    return b


def bolt_point(d, x, y, z):
    """bolts.json 위치·축(월드)."""
    w = W(x, y)
    ax = {"+Z": [0, 0, 1], "-Z": [0, 0, -1], "+Y": [0, 1, 0], "-Y": [0, -1, 0]}[d]
    if d in ("+Y", "-Y"):
        return [w[0], CY + y, z], ax
    return [w[0], w[1], z], ax


def zh_matrix():
    # 국소 X -> 월드 X, 국소 Y -> 월드 -Z, 국소 Z -> 월드 +Y. 브래킷 자리면(국소 Z -9.6) = 벽 바깥면 Y 75.
    # 국소 X -19.4~42.3 -> 상대 X -30.85~30.85, 국소 Y -18.4~6.6 -> Z -215~-190
    w = W(-11.45, 84.6)
    return [1, 0, 0, w[0], 0, 0, 1, w[1], 0, -1, 0, -208.4]


def stage_step():
    st = [C("file.insert_step", path=ZH, name="ZH10DSA-06-06-08", matrix=zh_matrix()),
          C("body.rename", body="ZH10DSA-06-06-08(0)_BODY", name="ZH10DSA-06-06-08"),
          C("body.rename", body="ZH2-BK1A-1-A_ZH_NEW", name="ZH10DSA-06-06-08_BKT"),
          C("material.assign", bodies=["ZH10DSA-06-06-08", "ZH10DSA-06-06-08_BKT"], material="Aluminum")]
    names = {"U3_ROT": [], "U4_Y": ["ZH10DSA-06-06-08:1"]}
    bodies = []
    for (nm, path, d, x, y, z, unit) in bolt_list():
        st += [C("file.insert_step", path=path, name=nm, matrix=mat(d, x, y, z)),
               C("body.rename", body="Cut-Extrude1", name=nm)]
        names[unit].append(nm + ":1")
        bodies.append(nm)
    st += [C("material.assign", bodies=bodies, material="SCM435"),
           C("joint.rigid_group", occurrences=["U3_ROT:1"] + names["U3_ROT"]),
           C("joint.rigid_group", occurrences=["U4_Y:1"] + names["U4_Y"]),
           C("motion.play", study="REST", step=0, quiet=True)]
    return st


STAGES = [("prep", stage_prep), ("sheet", stage_sheet), ("sheet_holes", stage_sheet_holes),
          ("solid", stage_solid), ("assign", stage_assign), ("step", stage_step)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.5.sc", "result": "3D_Modeling/FSAP_v1.0.6.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bl = []
    for (nm, path, d, x, y, z, unit) in bolt_list():
        p, ax = bolt_point(d, x, y, z)
        bl.append({"name": nm, "spec": nm.split("_")[0], "pos": p, "axis": ax, "unit": unit})
    json.dump(bl, open(os.path.join(OUT, "model", "bolts_plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc))


if __name__ == "__main__":
    main()
