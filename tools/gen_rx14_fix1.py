# -*- coding: utf-8 -*-
"""RX-14 수정 1회차 생성기 (v2.19.0 -> v2.19.1): 검증에서 나온 동작 문제 F1·F2·F3
python -X utf8 -B tools/gen_rx14_fix1.py   -> tools/out/mech_RX-14/model1/stage_*.json (MCP batch · CLI run 명령 배열)
좌표: 측정 좌표계 = 모델 좌표(바늘점 원점, 테이블 면 Z 0), mm.
 F1 받침 블록 포켓에 귀 끝 받이 턱(X 94~122 · Y 40~48 · 윗면 Z -20) + 받이 귀를 Y 48까지
 F2 덮개 옆벽을 X 31까지 내려 다리로(바늘판 Z 0 · 혀 윗면에 얹음), 재질 SUS304-1/2H
 F3 홈통·뚜껑을 판넬 끝 X 975에서 끊음(935 -> 850), 왼쪽 귀 한 곳 더(X 140) + 판넬 M5 탭 + CB5-12
"""
import json, os
from gen_rx14 import C, prism, cyl, box

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mech_RX-14", "model1")
st = {}
ROOT = C("component.activate", component=0)

# F3-1 홈통·뚜껑 길이 (이력 고침)
st["stage_1_duct_len"] = [
    C("timeline.edit", feature="RX14_DUCT", set={"extent": {"distance": "850"}}),
    C("timeline.edit", feature="RX14_DUCT_LID", set={"length": "850"}),
]

# F1 받이 턱 + 귀 늘림
f1 = [C("component.activate", component="P_RX14_KIT_SEAT")]
f1 += prism("SK_RX14F1_SEAT_LEDGE", "XY", -27, [[94, 40], [122, 40], [122, 48], [94, 48]], 7, "join",
            targets=["P_RX14_KIT_SEAT"], name="RX14F1_SEAT_LEDGE")
f1 += [ROOT, C("component.activate", component="P_RX14_KIT_PLATE")]
f1 += prism("SK_RX14F1_KIT_EAR_EXT", "YZ", 96, [[40, -17], [48, -17], [48, -20], [40, -20]], 20, "join",
            targets=["P_RX14_KIT_PLATE"], name="RX14F1_KIT_EAR_EXT")
f1 += [ROOT]
st["stage_2_f1_ledge_ear"] = f1

# F2 덮개 다리 (X-Z 단면): 바늘판 위 Z 0(X 31~46), 혀 윗면 경사(X 46~62), 판 윗면 Z -5(X 62~64)
LEG = [[31, 0], [46, 0], [46, -0.5], [62, -5], [64, -5], [64, -2], [60, -2], [44, 1.5], [31, 1.5]]
f2 = [C("component.activate", component="P_RX14_KIT_COVER")]
f2 += prism("SK_RX14F2_COVER_LEG_A", "ZX", -37, LEG, 1, "join", targets=["P_RX14_KIT_COVER"], name="RX14F2_COVER_LEG_A")
f2 += prism("SK_RX14F2_COVER_LEG_B", "ZX", -4, LEG, 1, "join", targets=["P_RX14_KIT_COVER"], name="RX14F2_COVER_LEG_B")
f2 += [ROOT,
       C("material.create", name="SUS304-1/2H", density_g_cm3=7.93, color="#c8ccd0"),
       C("material.assign", bodies=["P_RX14_KIT_COVER"], material="SUS304-1/2H"),
       C("component.metadata.set", component="P_RX14_KIT_COVER", part_number="P_RX14_KIT_COVER",
         description="RX-14 low tape cover on the cassette, SUS304-1/2H t1.0 sheet metal (provisional, D-212): top Z -1 (X 60-124), ramp, "
                     "nose top Z 2.5 over the needle plate (X 31-44), side walls down to X 31 as legs on needle plate + tongue (fix1 F2), "
                     "feet spot-welded to the plate x4")]
st["stage_3_f2_cover_legs"] = f2

# F3-2 왼쪽 귀 X 140 (기존 귀와 같은 단면)
X6 = 140
f3 = [C("component.activate", component="U2_TABLE", occurrence="U2_TABLE:1"),
      cyl(2.1, 5, [X6, 5, -12.5], "Z", "cut", ["P_M04_PANEL_E2"], name="RX14_PANEL_TAP_6"), ROOT,
      C("component.activate", component="P_RX14_DUCT")]
f3 += prism("SK_RX14_DUCT_EAR_6", "YZ", X6 - 8, [[-3, -5], [-2, -5], [-2, -7], [11, -7], [11, -8], [-3, -8]], 16, "join",
            targets=["P_RX14_DUCT"], name="RX14_DUCT_EAR_6")
f3 += [cyl(2.75, 1.4, [X6, 5, -8.2], "Z", "cut", ["P_RX14_DUCT"], name="RX14_DUCT_HOLE_6"), ROOT,
       C("component.activate", component="P_RX14_DUCT_LID")]
f3 += prism("SK_RX14_LID_EAR_6", "YZ", X6 - 8, [[-3, -1], [-1, -1], [-1, -6], [11, -6], [11, -7], [-2, -7], [-2, -2], [-3, -2]], 16, "join",
            targets=["P_RX14_DUCT_LID"], name="RX14_LID_EAR_6")
f3 += [cyl(2.75, 1.4, [X6, 5, -7.2], "Z", "cut", ["P_RX14_DUCT_LID"], name="RX14_LID_HOLE_6"), ROOT,
       C("component.metadata.set", component="P_RX14_DUCT", part_number="P_RX14_DUCT",
         description="RX-14 fixed tape duct (U channel) in the valley between ball rows, SUS304 t1.0 sheet metal (provisional): "
                     "X 125-975 (ends at panel edge, fix1 F3), floor Z -6..-5, walls to Z -2, 6 ears joggled down to the panel "
                     "(X 140, 200, 400, 600, 800, 960), hole D5.5"),
       C("component.metadata.set", component="P_RX14_DUCT_LID", part_number="P_RX14_DUCT_LID",
         description="RX-14 tape duct lid (low cover below the table surface, top Z -1), SUS304 t1.0 sheet metal (provisional, D-212): "
                     "X 125-975 (fix1 F3), 6 ears on the duct ears, hole D5.5"),
       # 볼트: 받침 블록 첫 볼트 (50, 8, -8)를 (140, 5, -6)으로 복사
       C("occurrence.copy", occurrence="CB5-12_RX14:1", in_place=True, translate=[X6 - 50, 5 - 8, -6 - (-8)])]
st["stage_4_f3_left_ear"] = f3

for k, v in st.items():
    json.dump(v, open(os.path.join(OUT, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(k, len(v))
