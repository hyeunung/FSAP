# -*- coding: utf-8 -*-
"""M08 수정 1회차 생성기 — 기준 3D_Modeling/FSAP_v2.5.0.sc -> 3D_Modeling/FSAP_v2.5.1.sc (모델링부 2026-11-05)
지난 검증 미완 6건: U4 실린더 포트 이음·관 끝, U5 베어 고정 끝·대차 쪽 관·이음, 카세트 안 관 U7C_1~6,
라이트 커튼 기본 금구·볼트, 경광등 CB4-12·다관 커넥터 CB5-12·보 윗면 관 빗, 판금 부품 판금 기능(sheet.convert).
python -X utf8 -B tools/gen_v2_m08_fix1.py -> tools/out/mech_M08/fix1/stage_*.json, tools/out/mech_M08/edit.json, lists_fix1.json
보고서 docs/reports/mechanism/mech_M08_model1.md.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m08 as m8  # noqa: E402
from gen_v2_m02 import C, box, cz, cy, cx, mat_assign  # noqa: E402

PRJ = m8.PRJ
OUTT = m8.OUTT
OUT = os.path.join(OUTT, "fix1")
STEP = m8.STEP
U8 = m8.U8
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX_, NY_, NZ_ = (-1, 0, 0), (0, -1, 0), (0, 0, -1)
r4, mrow, cross, perp, tag = m8.r4, m8.mrow, m8.cross, m8.perp, m8.tag
TUBES = {}
BOLTS = []      # (형번, 머리 밑 점, 축, 컴포넌트, 메모)
NUTS = []       # (점, 면 바깥 법선, 홈 방향, 컴포넌트)
ADDED = []


def tube_named(name, pts, comp=None, parent=U8, replace=False, r=3.0, R=15.0, pn="TU0604"):
    """관을 그리고(스케치 이름 _F1) 컴포넌트에 넣는다. replace=True면 같은 이름 바디를 지우고 같은 컴포넌트에 다시 넣는다."""
    TUBES[name] = {"r": r, "pts": [list(p) for p in pts], "parent": parent}
    cmds = m8.tube(name, pts, r, R)
    for c in cmds:
        p = c["params"]
        if p.get("name") == "SK_" + name:
            p["name"] = "SK_" + name + "_F1"
        if p.get("path_sketch") == "SK_" + name:
            p["path_sketch"] = "SK_" + name + "_F1"
    if replace:
        return [C("solid.remove", bodies=[name])] + cmds + [mat_assign([name], "Default"),
                                                            C("component.move_bodies", bodies=[name], component=name)]
    ADDED.append(name)
    return m8.tmp_comp(name, cmds, [name], pn, "SMC %s polyurethane tube, cut to length (route M08 fix1)" % pn, parent=parent)


def fitting(comp, p, lx, ly, parent):
    lz = cross(lx, ly)
    ADDED.append(comp)
    return [C("file.insert_step", path=STEP + "KQ2L06-01AS/KQ2L06-01AS.stp", name=comp, matrix=[round(v, 12) for i in range(3) for v in (lx[i], ly[i], lz[i], p[i])]),
            C("body.rename", body="KQ2L06-01AS", name=comp),
            C("component.metadata.set", component=comp, part_number="KQ2L06-01AS", bom_type="purchased",
              description="SMC KQ2L06-01AS elbow R1/8-6 (M08 fix1)"),
            mat_assign([comp], "Default"),
            C("occurrence.reparent", occurrence=comp + ":1", parent=parent)]


def outlet(p, lx, ly, ax=15.5, ay=14.2):
    return tuple(r4(p[i] + ax * lx[i] + ay * ly[i]) for i in range(3))


# ====================================================================== U4 실린더 포트(KQ2L06-01AS ×2) + 관
# 실린더 CDM2C20-25Z 포트 Rc1/8(구멍 r 4.28 실측) — 헤드 쪽(위) 면 중심 (-150.76, 0, 287.21), 로드 쪽(아래) (-153.99, 0, 216.28),
# 바깥 법선 n = (0.99894, 0, -0.04600)(REST, 실린더 2.6° 기움). 핀 축 J_U4_CYL_PIN (-161.006, y, 325.72) // Y(고정, U4_WHEEL_N).
# 고정 관(U8)은 핀 축 위 점에서 끝나고, 거기서 실린더 쪽 관(U4_CYL)이 이어진다 — 실린더가 돌아도 이음점은 그대로.
import math
_A4 = math.asin(0.046)
N4 = (math.cos(_A4), 0.0, -math.sin(_A4))
PIN_X, PIN_Z = -161.006, 325.72
U4P = {"1": (-150.76, 0.0, 287.21), "2": (-153.99, 0.0, 216.28)}


def stage_u4():
    s = []
    o = {}
    for k, p in U4P.items():
        s += fitting("KQ2L06-01AS_M08_U4_%s" % k, p, Y, N4, "U4_CYL")
        o[k] = outlet(p, Y, N4)
    X1 = m8.ST[0]
    s += tube_named("TU0604_M08_U4_A", [m8.A0(X1), (X1, 36.5, 270), (X1, 105, 270), (PIN_X, 105, 270), (PIN_X, 105, 334),
                                        (PIN_X, 55, 334), (PIN_X, 55, PIN_Z)], replace=True)
    s += tube_named("TU0604_M08_U4_B", [m8.B0(X1), (X1, 36.5, 385), (X1, 22, 385), (1020, 22, 385), (1020, 22, 278), (1020, 112, 278),
                                        (PIN_X, 112, 278), (PIN_X, 112, 342), (PIN_X, 45, 342), (PIN_X, 45, PIN_Z)], replace=True)
    s += tube_named("TU0604_M08_U4C_A", [(PIN_X, 55, PIN_Z), (PIN_X, 55, 310), (o["1"][0], 55, 310), (o["1"][0], 55, o["1"][2]), o["1"]],
                    parent="U4_CYL")
    s += tube_named("TU0604_M08_U4C_B", [(PIN_X, 45, PIN_Z), (PIN_X, 45, 300), (-127, 45, 300), (-127, 45, o["2"][2]),
                                         (o["2"][0], 45, o["2"][2]), o["2"]], parent="U4_CYL")
    return s


# ====================================================================== U5: 베어 고정 끝까지 + 대차 쪽(MGPM25 포트 KQ2L06-01AS ×2)
# MGPM25-40Z 포트(Rc1/8): 실물 STEP의 막음 플러그 자리(로드 끝에서 11.5·52.5, 두께 중심 +13.5)를 STEP대기 몸 -X 면(X -1986.5)에 둔다.
U5P = {"1": ((-1986.5, 45.5, 231.5), Z), "2": ((-1986.5, 45.5, 190.5), NY_)}


def stage_u5():
    s = []
    X2 = m8.ST[1]
    s += tube_named("TU0604_M08_U5_A", [m8.A0(X2), (X2, 36.5, 316), (X2, 14, 316), (1032, 14, 316), (1032, 14, 690), (1032, 190, 690),
                                        (-1280, 190, 690), (-1280, 230, 690), (-1280, 230, 672.5), (-1262, 230, 672.5)], replace=True)
    s += tube_named("TU0604_M08_U5_B", [m8.B0(X2), (X2, 36.5, 400), (1040, 36.5, 400), (1040, 36.5, 680), (1040, 182, 680),
                                        (-1287, 182, 680), (-1287, 243, 680), (-1287, 243, 662.5), (-1262, 243, 662.5)], replace=True)
    o = {}
    for k, (p, lx) in U5P.items():
        s += fitting("KQ2L06-01AS_M08_U5_%s" % k, p, lx, NX_, "U5_CAR")
        o[k] = outlet(p, lx, NX_)
    s += tube_named("TU0604_M08_U5C_1", [o["1"], (o["1"][0], 45.5, 817.5), (o["1"][0], 230, 817.5), (-1930, 230, 817.5)], parent="U5_CAR")
    s += tube_named("TU0604_M08_U5C_2", [o["2"], (o["2"][0], 20, 190.5), (o["2"][0], 20, 827.5), (o["2"][0], 243, 827.5),
                                         (-1930, 243, 827.5)], parent="U5_CAR")
    return s


# ====================================================================== U7 카세트 안 관(플러그 -Y 면 -> FEED·CUT·TUCK 피팅)
def stage_u7c():
    s = []
    a, b, c = 79.65, 86.15, 92.65            # 오름 길 X(간격 6.5), 줄 Y -133.5 / -143.5
    T = {1: [(14.5, -181.9, 100.25), (4, -181.9, 100.25), (4, -249, 100.25), (4, -249, 345), (a, -249, 345), (a, -143.5, 345),
             (a, -143.5, 694), (125, -143.5, 694), (125, -80, 694)],
         2: [(29, -246.4, 100.25), (29, -256, 100.25), (29, -256, 335), (a, -256, 335), (a, -133.5, 335), (a, -133.5, 694),
             (105, -133.5, 694), (105, -80, 694)],
         3: [(29, -196.4, 35.1), (29, -212, 35.1), (45, -212, 35.1), (45, -270, 35.1), (45, -270, 365), (b, -270, 365),
             (b, -143.5, 365), (b, -143.5, 686), (125, -143.5, 686), (125, -80, 686)],
         4: [(29, -246.4, 35.1), (29, -263, 35.1), (29, -263, 355), (b, -263, 355), (b, -133.5, 355), (b, -133.5, 686),
             (105, -133.5, 686), (105, -80, 686)],
         5: [(c, -120.5, 303), (c, -143.5, 303), (c, -143.5, 678), (125, -143.5, 678), (125, -80, 678)],
         6: [(c, -120.5, 505), (c, -133.5, 505), (c, -133.5, 678), (105, -133.5, 678), (105, -80, 678)]}
    for k, pts in T.items():
        s += tube_named("TU0604_M08_U7C_%d" % k, pts, parent=m8.CST)
    return s


# ====================================================================== 커튼 기본 금구·볼트, 옆 투광 L 고침
BRZ = (100.0, 1400.0)


def stage_curtain():
    s = []
    L = {"1E": [(-2260, -1600), (-2232, -1600), (-2232, -1597), (-2257, -1597), (-2257, -1565), (-2260, -1565)],
         "1R": [(360, -1600), (360, -1565), (357, -1565), (357, -1597), (332, -1597), (332, -1600)],
         "2R": [(-2343, 75), (-2340, 75), (-2340, 40), (-2330, 40), (-2330, 10), (-2333, 10), (-2333, 37), (-2343, 37)]}
    HOLE = {"1E": ((-2260, -1580), X), "1R": ((357, -1580), X), "2R": ((-2343, 60), X)}
    for k, pts in L.items():
        nm = "STEP대기_F3SG-BRKT_M08_" + k
        body = []
        (hx, hy), d = HOLE[k]
        for i, h in enumerate(BRZ):
            bn = nm if i == 0 else nm + "_2"
            body += m8.prism(bn, pts, h - 15, h + 15) + [m8.hole(bn, (hx, hy, h), d, 3)]
        s += m8.tmp_comp(nm, body, [nm, nm + "_2"], "F3SG-BRKT",
                         "Omron F3SG-R standard mounting bracket x2 (accessory, model no. D-129; placeholder t3 L, M08 fix1)")
        ADDED.append(nm)
    for h in BRZ:
        BOLTS.append(("CB5-12", (-2257.0, -1580.0, h), NX_, "LC", "1E 금구 -> 앞왼 기둥 +X 면"))
        NUTS.append(((-2262.5, -1580.0, h), X, Z, "LC"))
        BOLTS.append(("CB5-12", (357.0, -1580.0, h), X, "LC", "1R 금구 -> 앞오른 기둥 -X 면"))
        NUTS.append(((362.5, -1580.0, h), NX_, Z, "LC"))
        BOLTS.append(("CB5-12", (-2343.0, 60.0, h), X, "LC", "2R 금구 -> 뒤 기둥 -X 면"))
        NUTS.append(((-2337.5, 60.0, h), NX_, Z, "LC"))
    # 2E: 옆 투광 L 날개를 -Y로 3 옮기고(Y -1561~-1558) 그 자리에 금구 판 t3(Y -1558~-1555, M5 탭)
    s += [C("solid.remove", bodies=["P_M08_LC2F_BRKT_SM_1", "P_M08_LC2F_BRKT_SM_2"])]
    sm = []
    for i, h in enumerate(BRZ):
        nm = "P_M08_LC2F_BRKT_SM_%d" % (i + 1)
        cm = m8.prism(nm, [(-2303, -1620), (-2300, -1620), (-2300, -1558), (-2330, -1558), (-2330, -1561), (-2303, -1561)], h - 15, h + 15)
        for c in cm:
            if c["params"].get("name") == "SK_" + nm:
                c["params"]["name"] = "SK_" + nm + "_F1"
            if c["params"].get("sketch") == "SK_" + nm:
                c["params"]["sketch"] = "SK_" + nm + "_F1"
        sm += cm + [m8.hole(nm, (-2303, -1580, h), X, 3), m8.hole(nm, (-2315, -1561, h), Y, 3)]
    s += m8.made(sm, ["P_M08_LC2F_BRKT_SM_1", "P_M08_LC2F_BRKT_SM_2"], "SUS304")
    nm = "STEP대기_F3SG-BRKT_M08_2E"
    body = []
    for i, h in enumerate(BRZ):
        bn = nm if i == 0 else nm + "_2"
        body += [box(bn, -2330, -2300, -1558, -1555, h - 15, h + 15), m8.hole(bn, (-2315, -1558, h), Y, 3, 2.1)]
    s += m8.tmp_comp(nm, body, [nm, nm + "_2"], "F3SG-BRKT", "Omron F3SG-R standard mounting bracket x2 (accessory, model no. D-129; placeholder plate t3 M5 tap, M08 fix1)")
    ADDED.append(nm)
    # 2E 커튼 끝 금구 볼트 끝 자리(임시 형상 구멍 Ø5.5 깊이 10)
    s += [C("solid.cylinder", radius=2.75, height=10.5, base=[-2315, -1555.5, h], axis=[0, 1, 0], operation="cut",
            targets=["STEP대기_F3SG-4RA1520-14_M08_2E"]) for h in BRZ]
    # 옛 날개 볼트(CB5-12_M08_PY :11·:12, 머리 밑 Y -1558)는 리지드 묶음이라 옮길 수 없어 지우고 Y -1561에 새로 넣는다
    s += [C("selection.delete", occurrences=["CB5-12_M08_PY:11", "CB5-12_M08_PY:12"])]
    for h in BRZ:
        BOLTS.append(("CB5-12", (-2315.0, -1561.0, h), Y, "LC2F", "옆 투광 L 날개 -> 2E 금구 M5 탭"))
    return s


# ====================================================================== 경광등 CB4-12 ×3, 다관 커넥터 CB5-12 ×2, 보 윗면 관 빗 ×4
LAMP_H = [(1190.0, 290.0), (1172.679, 260.0), (1207.321, 260.0)]
KDM_H = [(97.0, -60.0), (133.0, -60.0)]
COMB_X = [250.0, 650.0, -350.0, -950.0]
COMB_T = [(130, 660), (130, 670), (140, 660), (140, 670), (150, 660), (150, 670), (182, 680), (190, 690)]


def stage_misc():
    s = []
    lamp = "STEP대기_LR6-302WJBW-RYG_M08"
    for x, y in LAMP_H:
        s += [cz(2.25, x, y, 649.9, 654.1, "cut", [lamp]), cz(4.0, x, y, 653.9, 670, "cut", [lamp])]
    bn = "STEP대기_CB4-12_M08"
    x0, y0 = LAMP_H[0]
    bb = [cz(3.5, x0, y0, 654, 658, "new", None, bn), cz(2.0, x0, y0, 642, 654.5, "join", [bn])]
    s += m8.tmp_comp(bn, bb, [bn], "CB4-12", "Misumi CB4-12 socket head cap screw (placeholder, LR6 base -> beam top M4 tap)", mat="SCM435",
                     copies=[(x - x0, y - y0, 0) for x, y in LAMP_H[1:]])
    ADDED.append(bn)
    kdm = "STEP대기_KDM10-06_M08"
    for x, y in KDM_H:
        s += [cz(2.75, x, y, 650.0, 656.1, "cut", [kdm]), cz(5.0, x, y, 656, 675.1, "cut", [kdm])]
        BOLTS.append(("CB5-12", (x, y, 656.0), NZ_, "KDM", "다관 커넥터 고정 반쪽 -> 걸이 윗판 M5 탭"))
    made = []
    for i, c in enumerate(COMB_X):
        nm = "P_M08_TUBE_COMB_ML_%d" % (i + 1)
        made += [box(nm, c - 8, c + 8, 124, 197, 650.1, 697)]
        made += [cx(3.3, y, z, c - 9, c + 9, "cut", [nm]) for y, z in COMB_T]
        made += [cz(4.75, c, 166, 660, 697.1, "cut", [nm]), cz(2.75, c, 166, 650, 660.1, "cut", [nm])]
        BOLTS.append(("CB5-16", (c, 166.0, 660.0), NZ_, "COMB", "관 빗 -> 보 윗면 M5 탭"))
    s += m8.made(made, ["P_M08_TUBE_COMB_ML_%d" % (i + 1) for i in range(len(COMB_X))], "A5052")
    return s


# ====================================================================== HMI 판: T(판+날개) -> L 판금(날개를 팔 -X 면으로)
def stage_hmi():
    nm = "P_M08_HMI_PLATE_SM"
    s = [C("solid.remove", bodies=[nm]), C("component.delete", component="CB5-12_M08_NX"),
         C("component.delete", component="HNTT8-5_M08_PX_PY")]
    cm = m8.prism(nm, [(1163, -465), (1442, -465), (1442, -463), (1165, -463), (1165, -400), (1163, -400)], 343, 557)
    for c in cm:
        if c["params"].get("name") == "SK_" + nm:
            c["params"]["name"] = "SK_" + nm + "_F1"
        if c["params"].get("sketch") == "SK_" + nm:
            c["params"]["sketch"] = "SK_" + nm + "_F1"
    cm += [m8.hole(nm, (1163, -431.5, z), X, 2) for z in (420, 460)]
    s += m8.made(cm, [nm], "SUS304")
    for z in (420.0, 460.0):
        BOLTS.append(("CB5-12", (1163.0, -431.5, z), X, "HMI", "패널 받침 날개 -> 팔 -X 면"))
        NUTS.append(((1167.5, -431.5, z), NX_, Y, "HMI"))
    return s


# ====================================================================== 볼트·너트(실물 STEP)
def stage_fast():
    s, g, gn = [], {}, {}
    for pn, p, d, k, _m in BOLTS:
        g.setdefault((pn, tuple(d), k), []).append(p)
    for (pn, d, k), pl in g.items():
        comp = "%s_M08_%s_%s" % (pn, tag(d), k)
        s += m8.insert_group("%s/%s.stp" % (pn, pn), comp, (d, perp(d), cross(d, perp(d))), pl, "Cut-Extrude1", pn, mat="SCM435")
        ADDED.append(comp)
    for p, n, sd, k in NUTS:
        gn.setdefault((tuple(sd), tuple(n), k), []).append(p)
    for (sd, n, k), pl in gn.items():
        comp = "HNTT8-5_M08_%s_%s_%s" % (tag(n), tag(sd), k)
        s += m8.insert_group("HNTT8-5/HNTT8-5.stp", comp, (sd, n, cross(sd, n)), pl, "Tap1", "HNTT8-5", mat="Steel")
        ADDED.append(comp)
    return s, g, gn


# ====================================================================== 판금 기능(sheet.convert)
SHEETS = [  # 바디, 규칙, 고정 면 점, 굽힘 모서리 점
    ("P_M08_LC_BRKT_FR_SM_1", "SUS304_t4", (360, -1560, -290), (360, -1520, -290)),
    ("P_M08_LC_BRKT_FR_SM_2", "SUS304_t4", (360, -1560, -52), (360, -1520, -52)),
    ("P_M08_LC2F_BRKT_SM_1", "SUS304_t3", (-2300, -1590, 100), (-2300, -1558, 100)),
    ("P_M08_LC2F_BRKT_SM_2", "SUS304_t3", (-2300, -1590, 1400), (-2300, -1558, 1400)),
    ("P_M08_LBRK_R1_SM", "SUS304_t6", (-2340, 95, -300), (-2340, 120, -300)),
    ("P_M08_LBRK_R2_SM", "SUS304_t6", (-2340, 95, 150), (-2340, 120, 150)),
    ("P_M08_LBRK_R3_SM", "SUS304_t6", (-2340, 95, 600), (-2340, 120, 600)),
    ("P_M08_LBRK_H1_SM", "SUS304_t6", (1185, 110, 505), (1185, 110, 480)),
    ("P_M08_LBRK_H2_SM", "SUS304_t6", (1185, 110, 375), (1185, 110, 400)),
    ("P_M08_HMI_PLATE_SM", "SUS304_t2", (1300, -465, 450), (1163, -465, 450)),
]


def stage_sheet():
    s = [C("sheet.manage_rules", name="SUS304_t4", thickness="4", bend_radius="4", k_factor="0.44", relief_width="1", relief_depth="1.5", active=False),
         C("sheet.manage_rules", name="SUS304_t6", thickness="6", bend_radius="6", k_factor="0.44", relief_width="1", relief_depth="1.5", active=False)]
    for b, rule, f, e in SHEETS:
        s.append(C("sheet.convert", body=b, face=list(f), rule=rule, bends=[list(e)]))
    return s


def stage_final():
    rg = [o for o in m8.RIGID]
    s = [C("joint.rigid_group", occurrences=["U8_PNEU:1"] + rg)] if rg else []
    s += [C("motion.play", study="REST", step=0, quiet=True),
          C("browser.visibility", visible=False, folder="joints"),
          C("document.metadata.set", key="description",
            value="M08 mechanism fix1: U4/U5 cylinder port elbows and tube ends, cassette tubes U7C, curtain brackets, lamp/connector screws, tube combs, sheet metal")]
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    m8.RIGID.clear()
    st = [("1_u4", stage_u4()), ("2_u5", stage_u5()), ("3_u7c", stage_u7c()), ("4_curtain", stage_curtain()),
          ("5_misc", stage_misc()), ("6_hmi", stage_hmi())]
    sf, g, gn = stage_fast()
    st += [("7_fast", sf), ("8_sheet", stage_sheet()), ("9_final", stage_final())]
    allc = []
    for nm, cmds in st:
        json.dump(cmds, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += cmds
        print(nm, len(cmds))
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.5.0.sc", "result": "3D_Modeling/FSAP_v2.5.1.sc", "generator": "tools/gen_v2_m08_fix1.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))
    lists = {"added": ADDED, "rigid": m8.RIGID, "tubes": TUBES, "bends": m8.BENDS,
             "bolt_list": [{"spec": pn, "seat": list(p), "axis": list(d), "kind": k, "memo": mm} for pn, p, d, k, mm in BOLTS],
             "nut_list": [{"pos": list(p), "normal": list(n), "slot": list(sd), "kind": k} for p, n, sd, k in NUTS],
             "commands": len(allc)}
    json.dump(lists, open(os.path.join(OUT, "lists_fix1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(ADDED), "added", len(m8.RIGID), "rigid", len(allc), "commands")


if __name__ == "__main__":
    main()
