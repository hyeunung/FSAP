# -*- coding: utf-8 -*-
"""N03 U4 X·Y 따라가기 받침 생성기 — v1.0.7 -> v1.0.8 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_N03_select.md 5절(N03-C1 고친 안)을 그린다.
python -B tools/gen_v1_n03.py -> tools/out/mech_N03/model/stage_*.json (MCP batch로 차례로 보냄), edit.json, edit_meta.json
좌표: 바늘점 원점 월드 mm, J_U4_X·J_U4_Y 0(REST)에서 그린다.
- 움직이는 컴포넌트 바디(U4_X_BEAM, U4_Y_CARR)와 U2_BASE에 내는 구멍은 그 바디를 만든 Box 바로 뒤로 마커를 돌려 넣는다(N02 메모).
- SV2RL28-1800 STEP: 국소(SolidWorks Y 위) -> 월드 행렬. X 레일 [1,0,0 / 0,0,-1 / 0,1,0], Y 레일 [0,0,1 / 1,0,0 / 0,1,0].
  넣은 결과(행렬만): 레일 X -30~1770 · Y ±10 · Z 0~15.5, 카운터보어 Ø9.5 Z 7~15.5 / Ø6 0~7, 구멍 X 0~1740 피치 60(30개),
  블록 2개 X -6.61~53.39 · 154.23~214.23, Y ±21, Z 5.5~28, 탭 M5(Ø4.134) 블록 중심 +6.5, 폭 ±16, 깊이 10.4.
- 볼트는 실물 STEP 한 개를 넣어 유닛 컴포넌트로 옮긴 뒤 occurrence.copy(translate)로 나머지를 놓는다.
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N03")
PS = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/"
SV = PS + "SV2RL28-1800/SV2RL28-1800.stp"
CB20, CB16, CB12 = PS + "CB5-20/CB5-20.stp", PS + "CB5-16/CB5-16.stp", PS + "CB5-12/CB5-12.stp"

BEAM = "U4_X_BEAM"
XMOT, YMOT = "STEP대기_MHMF082L1U2M_N03X", "STEP대기_MHMF042L1U2M_N03Y"
XPUL1, XPUL2 = "STEP대기_HTPA28S5M250-A-N19_1", "STEP대기_HTPA28S5M250-A-N19_2"
YPUL1, YPUL2 = "STEP대기_HTPA25S5M150-A-N14_1", "STEP대기_HTPA25S5M150-A-N14_2"
XBELT, YBELT = "STEP대기_S5M250-OPEN", "STEP대기_S5M150-OPEN"
XMBKT, XIBKT, YMBKT, YIBKT = "P_N03_XMBKT", "P_N03_XIBKT", "P_N03_YMBKT", "P_N03_YIBKT"
XCL, XCLP, YCL = "P_N03_XCLAMP", "P_N03_XCLAMP_PLATE", "P_N03_YCLAMP"

# 레일·블록
XR_Y = (-960.0, 960.0)          # X 레일 중심선 Y
XR_TX = -1260.0                 # 레일 X -1290~510
YR_X = (-945.0, -855.0)         # Y 레일 중심선 X
YR_TY = -870.0                  # 레일 Y -900~900
BLK_C = (23.391264, 184.232465)  # 블록 bbox 중심(레일 국소 X)
XB_T = (-935.0, -865.0)
YB_T = (-496.45, -303.55)
HOLES = [60.0 * k for k in range(30)]   # 레일 구멍(국소 X)
XR_HOLES = [(XR_TX + h, y) for y in XR_Y for h in HOLES]          # X 레일 볼트(월드 X, Y)
YR_HOLES = [(x, YR_TY + h) for x in YR_X for h in HOLES]          # Y 레일 볼트
# 블록 탭 = 블록 occurrence 원점. 첫 블록은 STEP 안에서 180° 돌아 있어 bbox 중심 +6.5, 둘째 블록은 -6.5(MCP 실측 transform)
XB_HOLES = [(xb + d, y + s) for y in XR_Y for xb, d in zip(XB_T, (6.5, -6.5)) for s in (-16, 16)]
YB_HOLES = [(x + s, yb + d) for x in YR_X for yb, d in zip(YB_T, (6.5, -6.5)) for s in (-16, 16)]
XC_HOLES = [(-1035.0, -310.0), (-1005.0, -310.0)]   # (X, Z) 보 -Y 끝면
YC_HOLES = [(-900.0, -415.0), (-900.0, -385.0)]     # (X, Y) 대차 밑면


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4),
         "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, h, base, axis="Z", op="new", name=None, tg=None):
    p = {"radius": r, "height": h, "base": [round(v, 4) for v in base], "axis": axis, "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.cylinder", **p)


def plane(origin, xd, yd, name):
    return C("sketch.create", plane={"origin": origin, "x_dir": xd, "y_dir": yd}, name=name)


def down_plane(z, name):   # 법선 -Z, (u, v) = (X, -Y)
    return plane([0, 0, z], [1, 0, 0], [0, -1, 0], name)


# ---------------- stage 1: 지우기·치수 고침·조인트 한계 ----------------
def stage_prep():
    st = [C("motion.play", study="REST", step=0, quiet=True),
          C("solid.remove", bodies=["U4_RAIL_A", "U4_RAIL_B"]),
          C("timeline.edit", feature="Box30", set={"corner": [-1050.0, -1000.0, -352.0], "length": "290", "width": "2000", "height": "64"})]
    for f, (x0, y0) in zip(("Box35", "Box36", "Box37", "Box38"), [(-1040, 900), (-840, 900), (-1040, -980), (-840, -980)]):
        st.append(C("timeline.edit", feature=f, set={"corner": [float(x0), float(y0), -288.0], "height": "248"}))
    st.append(C("joint.limits", joint="J_U4_Y", min=-355, max=1155))
    return st


# ---------------- stage 2: 보(U4_X_BEAM) 포켓·슬롯·탭·카운터보어 ----------------
def stage_beam():
    st = [C("timeline.roll_to", feature="Box30")]
    for (x0, x1) in ((-1040, -950), (-940, -919), (-881, -860), (-850, -770)):
        st.append(box(None, x0, x1, -890, 890, -353, -303, "cut", [BEAM]))
    st.append(box(None, -911, -889, -1001, 1001, -353, -303, "cut", [BEAM]))      # Y 벨트 아래 가닥 슬롯
    st.append(down_plane(-288, "SK_N03_BEAM_TAP"))                               # Y 레일 탭 M5 Ø4.2 깊이 13.5
    st += [C("sketch.circle.center", center=[x, -y], radius=2.1) for (x, y) in YR_HOLES]
    st += [C("sketch.finish"), C("solid.extrude", distance=13.5, operation="cut", targets=[BEAM])]
    for (x, y) in XB_HOLES:                                                       # X 블록 볼트 카운터보어(남는 살 12)
        st.append(cyl(4.75, 53, (x, y, -340), op="cut", tg=[BEAM]))
        st.append(cyl(2.75, 13, (x, y, -353), op="cut", tg=[BEAM]))
    for (x, z) in XC_HOLES:                                                       # X 물림 CB5-16 탭(-Y 끝면)
        st.append(cyl(2.1, 13, (x, -1000, z), axis="Y", op="cut", tg=[BEAM]))
    st.append(C("timeline.rollback", position="end"))
    return st


# ---------------- stage 3: 대차(U4_Y_CARR) 카운터보어·탭 ----------------
def stage_carr():
    st = [C("timeline.roll_to", feature="Box40")]
    for (x, y) in YB_HOLES:
        st.append(cyl(4.75, 19, (x, y, -248), op="cut", tg=["U4_Y_CARR"]))
        st.append(cyl(2.75, 13, (x, y, -261), op="cut", tg=["U4_Y_CARR"]))
    for (x, y) in YC_HOLES:
        st.append(cyl(2.1, 12, (x, y, -260), op="cut", tg=["U4_Y_CARR"]))
    st.append(C("timeline.rollback", position="end"))
    return st


# ---------------- stage 4: 바닥틀(U2_BASE) X 레일 탭 ----------------
def stage_base():
    st = [C("timeline.roll_to", feature="Box22"), down_plane(-380, "SK_N03_BASE_TAP")]
    # 첫 구멍 (X -1260, Y -960) -> uv (-1260, 960), 패턴 X 30×60, -v(=+Y) 2×1920
    st += [C("sketch.circle.center", center=[XR_TX, -XR_Y[0]], radius=2.1),
           C("sketch.pattern.rectangular", entities=["c1"], count=30, spacing=60, dir=[1, 0], count2=2, spacing2=1920, dir2=[0, -1])]
    st += [C("sketch.finish"), C("solid.extrude", distance=15, operation="cut", targets=["U2_BASE"]),
           C("timeline.rollback", position="end")]
    return st


# ---------------- stage 5: 판금(SPCC t4 R4) ----------------
def flange(name, sk, origin, xd, yd, pts, dist):
    n = len(pts) - 1
    return [plane(origin, xd, yd, sk), C("sketch.line", points=pts), C("sketch.finish"),
            C("sheet.flange", type="contour", sketch=sk, curves=["l%d" % (i + 1) for i in range(n)], distance=dist,
              rule="SPCC_t4", body_name=name)]


def stage_sheet():
    st = []
    # X 모터 브래킷 L: 단면 YZ(법선 +X), X -1370 -> -1270
    st += flange(XMBKT, "SK_N03_XMBKT", [-1370, 0, 0], [0, 1, 0], [0, 0, 1], [[-1136, -285], [-1136, -380], [-1260, -380]], 100)
    # X 아이들러 ㄷ: 단면 YZ, X 250 -> 310
    st += flange(XIBKT, "SK_N03_XIBKT", [250, 0, 0], [0, 1, 0], [0, 0, 1],
                 [[-1095, -300], [-1095, -380], [-1145, -380], [-1145, -300]], 60)
    # Y 모터 브래킷 L: 평면 XY(Z -325, 법선 +Z), 높이 67
    st += flange(YMBKT, "SK_N03_YMBKT", [0, 0, -325], [1, 0, 0], [0, 1, 0], [[-780, 1000], [-884, 1000], [-884, 1075]], 67)
    # Y 아이들러 ㄷ: 평면 XY(Z -320), 높이 55, +Y로 열림
    st += flange(YIBKT, "SK_N03_YIBKT", [0, 0, -320], [1, 0, 0], [0, 1, 0],
                 [[-875, -1000], [-875, -1065], [-925, -1065], [-925, -1000]], 55)
    # X 벨트 물림 L: 단면 YZ, X -1050 -> -990
    st += flange(XCL, "SK_N03_XCLAMP", [-1050, 0, 0], [0, 1, 0], [0, 0, 1], [[-1140, -296], [-1000, -296], [-1000, -316]], 60)
    return st


def stage_sheet_holes():
    st = []
    # Y 모터 브래킷 다리 윗부분 잘라 Z -325~-288로
    st.append(box(None, -876, -779, 999, 1005, -288, -257, "cut", [YMBKT]))
    # X 모터 세운 판: 소켓 Ø70 + □80 구멍 Ø6.6 4(PCD 90)
    st += [plane([0, -1136, 0], [1, 0, 0], [0, 0, 1], "SK_N03_XMBKT_H"),
           C("sketch.circle.center", center=[-1320, -330], radius=35)]
    st += [C("sketch.circle.center", center=[-1320 + sx * 31.82, -330 + sz * 31.82], radius=3.3) for sx in (1, -1) for sz in (1, -1)]
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[XMBKT])]
    # X 아이들러: 축 구멍 Ø8.2(두 옆판) + 바닥 장공 X ±10 ×2
    st += [plane([0, -1095, 0], [1, 0, 0], [0, 0, 1], "SK_N03_XIBKT_H1"),
           C("sketch.circle.center", center=[280, -330], radius=4.1), C("sketch.finish"),
           C("solid.extrude", distance=50, operation="cut", targets=[XIBKT])]
    st += [down_plane(-376, "SK_N03_XIBKT_H2")]
    st += [C("sketch.slot.center_to_center", p0=[270, -y], p1=[290, -y], width=5.5) for y in (-1128, -1112)]
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[XIBKT])]
    # Y 모터 플랜지 판: 스피곳 Ø52 + □60 구멍 Ø5.5 4(49.5)
    st += [plane([-884, 0, 0], [0, 1, 0], [0, 0, 1], "SK_N03_YMBKT_H"),
           C("sketch.circle.center", center=[1040, -292.5], radius=26)]
    st += [C("sketch.circle.center", center=[1040 + sy * 24.75, -292.5 + sz * 24.75], radius=2.75) for sy in (1, -1) for sz in (1, -1)]
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[YMBKT])]
    # Y 아이들러: 축 장공 Y ±8(두 옆판)
    st += [plane([-925, 0, 0], [0, 1, 0], [0, 0, 1], "SK_N03_YIBKT_H"),
           C("sketch.slot.center_to_center", p0=[-1043, -292.5], p1=[-1027, -292.5], width=8.2), C("sketch.finish"),
           C("solid.extrude", distance=50, operation="cut", targets=[YIBKT])]
    # X 물림 다리: Ø5.5 ×2
    st += [plane([0, -1000, 0], [1, 0, 0], [0, 0, 1], "SK_N03_XCLAMP_H")]
    st += [C("sketch.circle.center", center=[x, z], radius=2.75) for (x, z) in XC_HOLES]
    st += [C("sketch.finish"), C("solid.extrude", distance=4, operation="cut", targets=[XCL])]
    return st


# ---------------- stage 7: 임시 형상·가공품 ----------------
def pulley(name, c, axis, w0, body_r, flange_r, width, bore):
    """축 axis(Y 또는 X) 양 플랜지 2 + 몸통."""
    def at(s):
        return [c[0], s, c[2]] if axis == "Y" else [s, c[1], c[2]]
    return [cyl(flange_r, 2, at(w0), axis, name=name),
            cyl(body_r, width - 4, at(w0 + 2), axis, "join", tg=[name]),
            cyl(flange_r, 2, at(w0 + width - 2), axis, "join", tg=[name]),
            cyl(bore, width, at(w0), axis, "cut", tg=[name])]


def stadium(a, b, zc, R):
    """(u, v) 평면 경기장 고리: 중심 (a, zc)·(b, zc), 반지름 R."""
    r = lambda p: [round(p[0], 4), round(p[1], 4)]
    return [C("sketch.line", points=[r([a, zc + R]), r([b, zc + R])]),
            C("sketch.arc.three_point", start=r([b, zc + R]), end=r([b, zc - R]), through=r([b + R, zc])),
            C("sketch.line", points=[r([b, zc - R]), r([a, zc - R])]),
            C("sketch.arc.three_point", start=r([a, zc - R]), end=r([a, zc + R]), through=r([a - R, zc]))]


XPD_R, YPD_R = 28 * 5 / math.pi / 2, 25 * 5 / math.pi / 2   # 22.282, 19.894


def stage_solid():
    st = []
    # 서보 임시 외형
    st += [box(XMOT, -1360, -1280, -1252, -1140, -370, -290), cyl(9.5, 35, (-1320, -1140, -330), "Y", "join", tg=[XMOT])]
    st += [box(YMOT, -880, -784, 1010, 1070, -322.5, -262.5), cyl(7, 30, (-910, 1040, -292.5), "X", "join", tg=[YMOT])]
    # 풀리 28T(PD 44.56, 외경 43.42) 폭 31, 25T(PD 39.79, 외경 38.65) 폭 21
    st += pulley(XPUL1, (-1320, 0, -330), "Y", -1135.5, 21.71, 25, 31, 9.5)
    st += pulley(XPUL2, (280, 0, -330), "Y", -1135.5, 21.71, 25, 31, 11)     # 아이들러: 베어링 구멍 Ø22 추가공
    st += pulley(YPUL1, (0, 1040, -292.5), "X", -910, 19.33, 22.5, 21, 7)
    st += pulley(YPUL2, (0, -1035, -292.5), "X", -910, 19.33, 22.5, 21, 9.5)  # 아이들러: 베어링 구멍 Ø19
    # X 벨트 25폭: 평면 XZ(Y -1107.5, 법선 -Y), 안 = 피치 반지름, 두께 3.4
    st += [plane([0, -1107.5, 0], [1, 0, 0], [0, 0, 1], "SK_N03_XBELT")]
    st += stadium(-1320, 280, -330, XPD_R + 3.4) + stadium(-1320, 280, -330, XPD_R)
    st += [C("sketch.finish"), C("solid.extrude", distance=25, operation="new", body_name=XBELT)]
    # Y 벨트 15폭: 평면 YZ(X -907.5, 법선 +X)
    st += [plane([-907.5, 0, 0], [0, 1, 0], [0, 0, 1], "SK_N03_YBELT")]
    st += stadium(-1035, 1040, -292.5, YPD_R + 3.4) + stadium(-1035, 1040, -292.5, YPD_R)
    st += [C("sketch.finish"), C("solid.extrude", distance=15, operation="new", body_name=YBELT)]
    # X 물림판(A5052, 벨트 위 가닥 밑, 치형면)
    st.append(box(XCLP, -1050, -990, -1137.5, -1102.5, -316, round(-330 + XPD_R - 0.08, 3)))
    # Y 물림(A5052): 벨트 통로 + CB5-12 카운터보어(밑에서)
    st += [box(YCL, -913, -887, -425, -375, -278, -260),
           box(None, -908, -892, -426, -374, -273, -269, "cut", [YCL])]
    for (x, y) in YC_HOLES:
        st += [cyl(4.75, 15, (x, y, -279), op="cut", tg=[YCL]), cyl(2.75, 5, (x, y, -264), op="cut", tg=[YCL])]
    return st


FIX_B = [XMOT, XMBKT, XPUL1, XPUL2, XIBKT, XBELT]
X_B = [YMOT, YMBKT, YPUL1, YPUL2, YIBKT, YBELT, XCL, XCLP]
Y_B = [YCL]


def stage_assign():
    return [
        C("material.assign", bodies=[BEAM, XCLP, YCL], material="A5052"),
        C("material.assign", bodies=[XMBKT, XIBKT, YMBKT, YIBKT, XCL], material="SPCC"),
        C("material.assign", bodies=[XPUL1, XPUL2, YPUL1, YPUL2], material="A2017"),
        C("material.assign", bodies=[XMOT, YMOT], material="Steel"),
        C("material.assign", bodies=[XBELT, YBELT], material="CR_GF"),
        C("component.move_bodies", bodies=FIX_B, component="U4_FIX"),
        C("component.move_bodies", bodies=X_B, component="U4_X"),
        C("component.move_bodies", bodies=Y_B, component="U4_Y"),
    ]


# ---------------- stage 9: 레일 STEP 넣기(블록 옮기기는 occurrence id를 보고 stage 10) ----------------
MX = [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0]
MY = [0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0]
RAILS = [("SV2RL28-1800_N03X_A", MX, (XR_TX, XR_Y[0], -380.0)), ("SV2RL28-1800_N03X_B", MX, (XR_TX, XR_Y[1], -380.0)),
         ("SV2RL28-1800_N03Y_1", MY, (YR_X[0], YR_TY, -288.0)), ("SV2RL28-1800_N03Y_2", MY, (YR_X[1], YR_TY, -288.0))]


def withT(m, t):
    m = list(m)
    m[3], m[7], m[11] = t
    return m


def stage_rails():
    st = []
    for nm, m, t in RAILS:
        st += [C("file.insert_step", path=SV, name=nm, matrix=withT(m, t)),
               C("body.rename", body="Cap Screw1", name=nm),
               C("body.rename", body="Tap1", name=nm + "_BLK"),
               C("material.assign", bodies=[nm, nm + "_BLK"], material="Steel"),
               C("component.metadata.set", component=nm, part_number="SV2RL28-1800", bom_type="purchased",
                 description="MISUMI LM 가이드 레일 폭 20 H28 L1800 블록 2 (N03 %s)" % ("X 이송" if "_N03X" in nm else "Y 이송")),
               C("component.unlock", component=nm)]
    return st


def stage_blocks(ids):
    """ids: {rail name: (top occ, [block occ 1, block occ 2])} — 블록 bbox 중심 순서 BLK_C."""
    st = []
    for nm, m, t in RAILS:
        top, blks = ids[nm]
        if "_N03X" in nm:
            for occ, c0, tgt in zip(blks, BLK_C, XB_T):
                st.append(C("occurrence.move", occurrence=occ, space="world", translate=[round(tgt - (XR_TX + c0), 6), 0, 0]))
            par_top, par_blk = "U4_FIX", "U4_X"
        else:
            for occ, c0, tgt in zip(blks, BLK_C, YB_T):
                st.append(C("occurrence.move", occurrence=occ, space="world", translate=[0, round(tgt - (YR_TY + c0), 6), 0]))
            par_top, par_blk = "U4_X", "U4_Y"
        st.append(C("component.capture_position"))
        for occ in blks:
            st.append(C("occurrence.reparent", occurrence=occ, parent=par_blk))
        st.append(C("occurrence.reparent", occurrence=top, parent=par_top))
    return st


# ---------------- stage 11: 볼트(실물 STEP 1개 + occurrence.copy) ----------------
def bmat(d, p):
    rows = {"+Z": [[0, 0, -1], [0, 1, 0], [1, 0, 0]], "-Z": [[0, 0, 1], [0, 1, 0], [-1, 0, 0]],
            "+Y": [[0, 0, 1], [1, 0, 0], [0, 1, 0]]}[d]
    return [v for i in range(3) for v in (rows[i] + [round(p[i], 4)])]


def bolt_groups():
    return [  # (이름, STEP, 형번, 방향, 자리면 점들, 부모, 설명)
        ("CB5-20_N03XR", CB20, "CB5-20", "-Z", [(x, y, -373.0) for (x, y) in XR_HOLES], "U4_FIX", "X 레일 -> U2_BASE 탭(물림 13)"),
        ("CB5-20_N03YR", CB20, "CB5-20", "-Z", [(x, y, -281.0) for (x, y) in YR_HOLES], "U4_X", "Y 레일 -> 보 리브 탭(물림 13)"),
        ("CB5-20_N03XB", CB20, "CB5-20", "-Z", [(x, y, -340.0) for (x, y) in XB_HOLES], "U4_X", "보 카운터보어 -> X 블록 탭(물림 8)"),
        ("CB5-20_N03YB", CB20, "CB5-20", "-Z", [(x, y, -248.0) for (x, y) in YB_HOLES], "U4_Y", "대차 카운터보어 -> Y 블록 탭(물림 8)"),
        ("CB5-16_N03XC", CB16, "CB5-16", "+Y", [(x, -1004.0, z) for (x, z) in XC_HOLES], "U4_X", "X 물림 L 다리 -> 보 -Y 끝면 탭(물림 12)"),
        ("CB5-12_N03YC", CB12, "CB5-12", "+Z", [(x, y, -264.0) for (x, y) in YC_HOLES], "U4_Y", "Y 물림 카운터보어 -> 대차 밑면 탭(물림 8)"),
    ]


def stage_bolts():
    st = []
    for nm, path, pn, d, pts, par, desc in bolt_groups():
        p0 = pts[0]
        st += [C("file.insert_step", path=path, name=nm, matrix=bmat(d, p0)),
               C("body.rename", body="Cut-Extrude1", name=nm),
               C("material.assign", bodies=[nm], material="SCM435"),
               C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased",
                 description="MISUMI 육각 구멍붙이 볼트 %s — %s (N03)" % (pn, desc)),
               C("occurrence.reparent", occurrence=nm + ":1", parent=par)]
        for p in pts[1:]:
            st.append(C("occurrence.copy", occurrence=nm + ":1", translate=[round(p[i] - p0[i], 4) for i in range(3)]))
    st.append(C("motion.play", study="REST", step=0, quiet=True))
    return st


STAGES = [("prep", stage_prep), ("beam", stage_beam), ("carr", stage_carr), ("base", stage_base),
          ("sheet", stage_sheet), ("sheet_holes", stage_sheet_holes), ("solid", stage_solid), ("assign", stage_assign),
          ("rails", stage_rails)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    ids_path = os.path.join(OUT, "model", "rail_ids.json")
    stages = list(STAGES)
    if os.path.exists(ids_path):
        ids = json.load(open(ids_path, encoding="utf-8"))
        stages.append(("blocks", lambda: stage_blocks(ids)))
        stages.append(("bolts", stage_bolts))
    for i, (nm, f) in enumerate(stages, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.7.sc", "result": "3D_Modeling/FSAP_v1.0.8.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bl = []
    for nm, path, pn, d, pts, par, desc in bolt_groups():
        ax = {"+Z": [0, 0, 1], "-Z": [0, 0, -1], "+Y": [0, 1, 0]}[d]
        for k, p in enumerate(pts, 1):
            bl.append({"name": "%s:%d" % (nm, k), "spec": pn, "pos": list(p), "axis": ax, "unit": par})
    json.dump(bl, open(os.path.join(OUT, "model", "bolts_plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc), "bolts", len(bl))


if __name__ == "__main__":
    main()
