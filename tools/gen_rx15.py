# -*- coding: utf-8 -*-
"""RX-15 생성기 — 테이프 절단·끝 접기·앞끝 보내기를 판넬 밑 U7_SEAM으로 (v2.19.2 -> v2.20.0)
설계안 mech_RX-15_design.md 4절 + design1.md 4절. 실측과 달라 고친 자리는 mech_RX-15_model.md 2절.

python -X utf8 -B tools/gen_rx15.py
  출력: tools/out/mech_RX-15/model/stage_*.json (MCP batch · CLI run이 받는 명령 배열)
좌표: 모델 좌표(바늘점 원점, 테이블 면 Z 0), mm.
구매품 STEP·조인트·연구·관은 tools/out/mech_RX-15/model/s2_purchased.py · s3_tubes.py · s4_joints.py · s5_studies.py.
"""
import json, os
from gen_rx14 import C, prism, cyl, box

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-15", "model")
ROOT = C("component.activate", component=0)
st = {}

# ---- 실린더 자리(STEP 로컬: 어깨 x 0, 코 -8~0, 몸 0~138, 로드 끝(들어감) -28, 로드 나사 -28~-14)
CUT_SH = (112.0, -112.0, -33.7)     # 로컬 X -> -Y, 로드 +Y. 코 끝 Y -104, 로드 끝 Y -84
TUCK_SH = (213.0, 5.0, -30.0)       # 로컬 X -> +X, 로드 -X. 코 끝 X 205, 로드 끝 X 185
FEED_SH = (339.0, -20.0, -30.0)     # 로컬 X -> +X, 로드 -X. 코 끝 X 331, 로드 끝 X 311
B16 = [(100, -100), (124, -100), (100, -222), (124, -222), (150, 21), (178, 21), (206, 21), (318, -46), (318, -60)]


def meta(name, desc, bom=None):
    p = {"component": name, "part_number": name, "description": desc}
    if bom:
        p["bom_type"] = bom
    return [ROOT, C("component.metadata.set", **p)]


def part(name, parent):
    return [C("component.create", name=name, parent=parent)]


# ---------------------------------------------------------------- a 기존 부품 추가 가공
a = [C("component.activate", component="U2_TABLE", occurrence="U2_TABLE:1")]
PN = ["P_M04_PANEL_E2"]
a += prism("SK_RX15_PANEL_WINDOW", "XY", -12.5,
           [[76.94, -35.5], [133.5, -35.5], [137.5, -31.5], [137.5, -4.5], [76.94, -4.5]], 5, "cut", targets=PN,
           name="RX15_PANEL_WINDOW")
a += prism("SK_RX15_PANEL_RAMP", "ZX", -35.5, [[72.67, -8.0], [76.95, -9.2], [76.95, -7.9], [72.67, -7.9]], 31, "cut",
           targets=PN, name="RX15_PANEL_RAMP")
a.append(box([123.6, -89, -12.5], 1.8, 89.5, 5, "cut", PN, name="RX15_PANEL_BLADE_SLOT"))
a.append(box([97.3, -89, -12.5], 3.6, 45.5, 5, "cut", PN, name="RX15_PANEL_PIN_SLOT"))
a.append(box([137.4, -26.5, -12.5], 20.6, 22, 5, "cut", PN, name="RX15_PANEL_SLOT_E1"))
a.append(box([157, -23, -12.5], 37, 18.5, 5, "cut", PN, name="RX15_PANEL_SLOT_E2"))
a.append(box([193.9, -23, -12.5], 127.1, 6, 5, "cut", PN, name="RX15_PANEL_SLOT_E3"))
for i, (x, y) in enumerate(B16):
    a.append(cyl(2.75, 5, [x, y, -12.5], "Z", "cut", PN, name="RX15_PANEL_BOLT_%d" % (i + 1)))
a += [ROOT, C("component.activate", component="P_RX14_KIT_PLATE")]
KP = ["P_RX14_KIT_PLATE"]
a += prism("SK_RX15_KIT_RAMP", "ZX", -35.5, [[62, -5.0], [72.68, -8.0037], [72.68, -4.9], [62, -4.9]], 31, "cut",
           targets=KP, name="RX15_KIT_RAMP")
a.append(box([72.67, -35.5, -8.5], 51.43, 31, 4, "cut", KP, name="RX15_KIT_WINDOW"))
a.append(box([97.9, -43.1, -8.1], 2.4, 7.7, 2.3, "cut", KP, name="RX15_KIT_PIN_GROOVE_A"))
a.append(box([97.9, -4.6, -8.1], 2.4, 9.1, 2.3, "cut", KP, name="RX15_KIT_PIN_GROOVE_B"))
a += [ROOT, C("component.activate", component="P_RX14_DUCT"),
      box([157, -23, -6.1], 164, 6, 1.2, "cut", ["P_RX14_DUCT"], name="RX15_DUCT_CLAW_SLOT"),
      ROOT, C("component.activate", component="P_RX14_DUCT_STRIP"),
      box([157, -23, -8.1], 164, 6, 2.2, "cut", ["P_RX14_DUCT_STRIP"], name="RX15_STRIP_CLAW_SLOT"), ROOT]
st["stage_a_machining"] = a

# ---------------------------------------------------------------- b 유닛
st["stage_b_units"] = [
    C("component.create", name="U7_SEAM", parent="root", activate=False),
    C("component.create", name="U7_SEAM_CUT", parent="U7_SEAM", activate=False),
    C("component.create", name="U7_SEAM_TUCK", parent="U7_SEAM", activate=False),
    C("component.create", name="U7_SEAM_FEED", parent="U7_SEAM", activate=False),
]

# ---------------------------------------------------------------- c ① 자르기 + 접기 핀
c = []
n = "P_RX15_CUT_BASE"
c += part(n, "U7_SEAM")
c.append(box([96, -232, -24], 32, 139, 12, "new", body=n, name="RX15_CUT_BASE"))
c.append(box([106.8, -232.1, -18.4], 10.4, 139.2, 6.5, "cut", [n], name="RX15_CUT_BASE_GROOVE"))
c.append(box([100, -112, -45], 24, 4, 21.05, "join", [n], name="RX15_CUT_BASE_WALL"))
c.append(cyl(5.1, 4.2, [112, -112.1, -33.7], "Y", "cut", [n], name="RX15_CUT_BASE_BORE"))
for i, (x, y) in enumerate(B16[:4]):
    c.append(cyl(2.1, 12.2, [x, y, -24.1], "Z", "cut", [n], name="RX15_CUT_BASE_TAP_%d" % (i + 1)))
c.append(C("material.assign", bodies=[n], material="A5052"))
c += meta(n, "RX-15 cut slide base under panel E2, A5052 milling (provisional): block 32 x 139 x 12 (X 96-128, Y -232..-93), "
             "guide groove 10.4 x 6.4 full length, hanging wall t4 with D10.2 bore for CJ2B16-60SZ nose (wall Y -112..-108 by STEP nose 8), "
             "M5 tap x4 through (from panel top CB5-16)")
n = "P_RX15_CUT_SLIDE"
c += part(n, "U7_SEAM_CUT")
c.append(box([95, -230, -40], 29.25, 154, 27.8, "new", body=n, name="RX15_CUT_SLIDE"))
c.append(box([94.9, -230.1, -40.1], 29.45, 139.1, 21.9, "cut", [n], name="RX15_CUT_SLIDE_UNDER"))
c.append(box([94.9, -230.1, -18.3], 12.1, 139.1, 6.2, "cut", [n], name="RX15_CUT_SLIDE_SIDE_A"))
c.append(box([117, -230.1, -18.3], 7.35, 139.1, 6.2, "cut", [n], name="RX15_CUT_SLIDE_SIDE_B"))
c.append(box([94.9, -81, -40.1], 11.1, 5.1, 28.0, "cut", [n], name="RX15_CUT_SLIDE_TRIM_A"))
c.append(box([94.9, -91.1, -40.1], 11.1, 10.1, 21.9, "cut", [n], name="RX15_CUT_SLIDE_TRIM_B"))
c.append(box([97.6, -87.5, -12.25], 3.0, 4.0, 6.75, "join", [n], name="RX15_CUT_SLIDE_PIN_POST"))
c.append(cyl(2.1, 8.1, [112, -91.1, -33.7], "Y", "cut", [n], name="RX15_CUT_SLIDE_ROD_TAP"))
c.append(cyl(2.75, 18.5, [105.9, -82, -24], "X", "cut", [n], name="RX15_CUT_SLIDE_BLADE_BOLT"))
c.append(cyl(4.75, 2.6, [105.9, -82, -24], "X", "cut", [n], name="RX15_CUT_SLIDE_BLADE_CBORE"))
c.append(C("material.assign", bodies=[n], material="POM"))
c += meta(n, "RX-15 cut slide (one piece), POM milling (provisional): tongue 10 x 139 x 6 in the base groove, cross arm X 95-124.25, "
             "lug block X 106-124.25 / Y -91..-76 / Z -40..-12.2 (rod M5 tap depth 8, blade bolt D5.5 + cbore D9.5 x 2.5), "
             "pin post 3 x 4 up through the panel slot (stroke 40 stop at slot end Y -43.5)")
n = "P_RX15_PIN"
c += part(n, "U7_SEAM_CUT")
c.append(cyl(1.0, 47, [99.1, -83.5, -7.0], "Y", "new", body=n, name="RX15_PIN"))
c.append(C("material.assign", bodies=[n], material="SUS304"))
c += meta(n, "RX-15 tuck pin D2 x 47, SUS304 turning (provisional): axis Y at X 99.1 / Z -7, rest Y -83.5..-36.5, slides under the tape")
n = "P_RX15_BLADE"
c += part(n, "U7_SEAM_CUT")
c += prism("SK_RX15_BLADE", "YZ", 124.25,
           [[-88, -30], [-76, -30], [-76, -8], [-40, -8], [-40, -6.0], [-45, -1.2], [-88, -1.2]], 0.5, "new",
           body=n, name="RX15_BLADE")
c.append(cyl(2.75, 0.7, [124.15, -82, -24], "X", "cut", [n], name="RX15_BLADE_HOLE"))
c.append(C("material.assign", bodies=[n], material="SK5"))
c += meta(n, "RX-15 draw-cut blade t0.5, SK5 HRC58 waterjet + grinding (provisional): shank 12 x 22 with D5.5 hole, body Z -8..-1.2, "
             "edge on the top side falling 44 deg to the tip (Y -45..-40 at rest), cuts the tape in the gap X 124-125")
n = "P_RX15_BLADE_CLAMP"
c += part(n, "U7_SEAM_CUT")
c.append(box([124.75, -88, -30], 4, 12, 12, "new", body=n, name="RX15_BLADE_CLAMP"))
c.append(cyl(2.1, 4.2, [124.65, -82, -24], "X", "cut", [n], name="RX15_BLADE_CLAMP_TAP"))
c.append(C("material.assign", bodies=[n], material="SUS304"))
c += meta(n, "RX-15 blade clamp plate 12 x 12 x 4, SUS304 milling (provisional): M5 through tap, clamps the blade shank on the lug block")
st["stage_c_cut"] = c

# ---------------------------------------------------------------- d ② 접기 판
d = []
n = "P_RX15_TUCK_BASE"
d += part(n, "U7_SEAM")
d.append(box([127, -12, -40], 86, 40, 28, "new", body=n, name="RX15_TUCK_BASE"))
d.append(box([131, -12.1, -35.2], 78, 26.1, 23.3, "cut", [n], name="RX15_TUCK_BASE_CHANNEL"))
d.append(box([198, -12.1, -40.1], 11, 26.1, 5.0, "cut", [n], name="RX15_TUCK_BASE_NUT_RELIEF"))
d.append(cyl(5.1, 4.2, [208.9, 5, -30], "X", "cut", [n], name="RX15_TUCK_BASE_BORE"))
# 접기 판 귀 볼트 CB5-12 나사 끝(행정 끝 X 126.8)이 끝 벽을 지나는 자리 — 넘기기 전 확인에서 39.3 mm3 겹침이 나와 따냄
d.append(box([126.9, -12.1, -22.0], 4.2, 3.6, 10.1, "cut", [n], name="RX15_TUCK_BASE_BOLT_RELIEF"))
for i, (x, y) in enumerate(B16[4:7]):
    d.append(cyl(2.1, 12.1, [x, y, -24], "Z", "cut", [n], name="RX15_TUCK_BASE_TAP_%d" % (i + 1)))
d.append(C("material.assign", bodies=[n], material="A5052"))
d += meta(n, "RX-15 tucker base under panel E2, A5052 milling (provisional): 86 x 40 x 28 (X 127-213, Y -12..28), arm channel open to -Y "
             "(floor top Z -35.2, -X end wall X 127-131 = stroke 54 stop), front wall t4 X 209-213 with D10.2 bore for CJ2B16-60SZ nose, "
             "M5 tap x3 depth 12 (from panel top CB5-16)")
n = "P_RX15_TUCK_ARM"
d += part(n, "U7_SEAM_TUCK")
d += prism("SK_RX15_TUCK_ARM", "YZ", 185, [[-14, -35], [9, -35], [9, -26], [-8, -26], [-8, -10.2], [-14, -10.2]], 7, "new",
           body=n, name="RX15_TUCK_ARM")
d.append(cyl(2.1, 7.2, [184.9, 5, -30], "X", "cut", [n], name="RX15_TUCK_ARM_ROD_TAP"))
d.append(cyl(2.1, 7.2, [184.9, -12, -18], "X", "cut", [n], name="RX15_TUCK_ARM_EAR_TAP"))
d.append(C("material.assign", bodies=[n], material="SUS304"))
d += meta(n, "RX-15 tucker arm t7, SUS304 milling (provisional): bar Y -14..9 / Z -35..-26 on the rod end (M5 through tap), "
             "post Y -14..-8 up to Z -10.2 carrying the tucker ear (M5 through tap)")
n = "P_RX15_TUCKER"
d += part(n, "U7_SEAM_TUCK")
d += prism("SK_RX15_TUCKER", "XY", -10,
           [[131, -35], [133, -35], [137, -31], [137, -26], [157, -26], [157, -16], [192.8, -16], [192.8, -8], [157, -8],
            [157, -5], [131, -5]], 0.8, "new", body=n, name="RX15_TUCKER")
d.append(box([192, -19, -24], 0.8, 14, 14, "join", [n], name="RX15_TUCKER_EAR"))
d.append(cyl(2.75, 1.0, [191.9, -12, -18], "X", "cut", [n], name="RX15_TUCKER_EAR_HOLE"))
d.append(C("material.assign", bodies=[n], material="SUS304-1/2H"))
d += meta(n, "RX-15 tucker plate t0.8, SUS304-CSP 1/2H laser + one bend (provisional): front band X 131-137 / Y -35..-5 (4 x 4 corner cut), "
             "body X 137-157 / Y -26..-5, rail 8 wide to X 192.8, ear 14 x 14 bent down with D5.5 hole; slides inside the panel thickness Z -10..-9.2")
st["stage_d_tuck"] = d

# ---------------------------------------------------------------- e ③ 앞끝 보내기
e = []
n = "P_RX15_FEED_BASE"
e += part(n, "U7_SEAM")
e += prism("SK_RX15_FEED_BASE", "XY", -40,
           [[312, -66], [330, -66], [330, -32], [339, -32], [339, -10], [335, -10], [335, -28], [312, -28]], 28, "new",
           body=n, name="RX15_FEED_BASE")
e.append(cyl(5.1, 4.2, [334.9, -20, -30], "X", "cut", [n], name="RX15_FEED_BASE_BORE"))
for i, (x, y) in enumerate(B16[7:9]):
    e.append(cyl(2.1, 12.1, [x, y, -24], "Z", "cut", [n], name="RX15_FEED_BASE_TAP_%d" % (i + 1)))
e.append(C("material.assign", bodies=[n], material="A5052"))
e += meta(n, "RX-15 lead-end feed cylinder base under panel E2, A5052 milling one piece (provisional): foot X 312-330 / Y -66..-28, "
             "neck and front wall t4 X 335-339 / Y -32..-10 with D10.2 bore for CDJ2B16-150AZ-B nose (wall X by STEP nose 8), "
             "M5 tap x2 depth 12, clears the ball unit at (350, -50)")
n = "P_RX15_FEED_SLIDE"
e += part(n, "U7_SEAM_FEED")
e.append(box([304, -25, -36], 18, 10, 23.5, "new", body=n, name="RX15_FEED_SLIDE"))
e.append(box([320, -25.1, -13], 2.1, 10.2, 0.6, "cut", [n], name="RX15_FEED_SLIDE_STEP"))
e.append(box([310, -22.5, -12.55], 10, 5, 6.35, "join", [n], name="RX15_FEED_SLIDE_WING"))
e.append(cyl(2.1, 11.1, [311, -20, -30], "X", "cut", [n], name="RX15_FEED_SLIDE_ROD_TAP"))
e.append(cyl(2.1, 12.1, [310, -20, -17.5], "X", "cut", [n], name="RX15_FEED_SLIDE_CLAW_TAP"))
e.append(C("material.assign", bodies=[n], material="POM"))
e += meta(n, "RX-15 feed slide, POM milling (provisional): block 18 x 10 x 23.5 on the rod end (M5 tap from +X face), "
             "wing 10 x 5 up through panel / strip / duct floor slots to Z -6.2, claw bolt M5 tap")
n = "P_RX15_FEED_CLAW"
e += part(n, "U7_SEAM_FEED")
e += prism("SK_RX15_FEED_CLAW", "ZX", -25,
           [[322, -21], [322.3, -21], [322.3, -12.7], [320.3, -12.7], [320.3, -5.9], [312.5, -5.9], [310, -5.0],
            [310.1, -5.28], [312.5, -6.2], [320, -6.2], [320, -13], [322, -13]], 10, "new", body=n, name="RX15_FEED_CLAW")
e.append(box([309.9, -25.1, -13], 12.5, 2.6, 8.1, "cut", [n], name="RX15_FEED_CLAW_TRIM_A"))
e.append(box([309.9, -17.5, -13], 12.5, 2.6, 8.1, "cut", [n], name="RX15_FEED_CLAW_TRIM_B"))
e.append(cyl(2.75, 0.5, [321.9, -20, -17.5], "X", "cut", [n], name="RX15_FEED_CLAW_HOLE"))
e.append(C("material.assign", bodies=[n], material="SUS304-1/2H"))
e += meta(n, "RX-15 feed claw leaf spring t0.3, SUS304-CSP laser + bend (provisional): foot 10 x 8 with D5.5 hole on the slide +X face, "
             "strip 5 wide over the wing top, tip raised 20 deg to Z -5.0 (touches the tape underside, pushes -X only)")
st["stage_e_feed"] = e

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(k, len(v))
    json.dump({"CUT_SH": CUT_SH, "TUCK_SH": TUCK_SH, "FEED_SH": FEED_SH, "B16": B16},
              open(os.path.join(OUT, "gen_consts.json"), "w", encoding="utf-8"))
