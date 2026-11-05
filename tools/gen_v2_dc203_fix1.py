# -*- coding: utf-8 -*-
"""DC2-03 아랫유닛 북 교체 길(직렬, 설계안 수정 1회차) 생성기 — 기준 3D_Modeling/FSAP_v2.5.3.sc -> 3D_Modeling/FSAP_v2.5.4.sc
(모델링부 2026-11-05, 설계 docs/reports/mechanism/mech_DC2-03_design1.md, 보고서 docs/reports/mechanism/mech_DC2-03_model.md)
python -X utf8 -B tools/gen_v2_dc203_fix1.py -> tools/out/mech_DC2-03/model/stage_*.json, edit.json, edit_meta.json, lists.json
좌표: 바늘점 원점, 테이블 면 Z 0, 바닥 Z -840, 세계 mm.

A. 지난 안: LOWER 북 문 자리 자르기, 받이 판 P_DC203_TRAY(SUS304 t1.5 판금), CB5-12 + HNTT8-5 ×2(바닥틀 :6 윗면 홈 X 360).
B. 포켓 바닥 비우기: 앞 레일 HFS8-4080-3450_M07:1 -> 2680 + 165 두 토막(새 컴포넌트, 같은 1140 STEP 끝면 늘이기/줄이기),
   :7·:8 -> HFS8-4080-1740_M07 ×2, 새 가로대 HFS8-4080-730_M07, 끝캡 HFC8-4080-B 2(기존 _E·_W 복사), S형 L브래킷 7(기존 복사) +
   CB5-16·HNTT8-5 각 14(기존 복사), 옛 브래킷 3·볼트 6·너트 6 지움.
지시와 다른 곳: 지시 (4)는 3450 바디를 잘라 두 바디로 — 그 바디는 앞·뒤·가운데 3 자리가 한 정의를 나눈 복사라 자르면 셋 다 잘린다.
   그래서 앞 자리(:1)를 지우고 같은 STEP으로 두 토막을 새 컴포넌트로 넣는다(결과 형상 같음). :7·:8도 같은 까닭.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, mat_assign  # noqa: E402
import gen_v2_m07 as m7  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUTT = os.path.join(ROOT, "out", "mech_DC2-03")
OUT = os.path.join(OUTT, "model")
STEP = PRJ + "/purchased-step/"
U1 = "U1_FRAME"
LOWER = "STEP대기_867-392342_LOWER"
TRAY = "P_DC203_TRAY"
ZB, T = -250.0, 1.5
HOLES = [(360.0, -230.0), (360.0, -110.0)]
F1140 = "HFS8-4080-1140/HFS8-4080-1140.stp"

# ---------------------------------------------------------------- A. 지난 안
def stage_lower():
    return [C("solid.box", length=30, width=50, height=29, corner=[-15, -60, -41], operation="cut", targets=[LOWER])]


def stage_tray():
    zt = ZB + T
    s = [C("sheet.manage_rules", name="SUS304_t1.5", thickness="1.5", bend_radius="1.5", k_factor="0.44",
           corner_relief_shape="rectangular", corner_relief="1.5", active=True),
         C("component.create", name=TRAY, parent=U1, activate=False),
         C("sketch.create", plane={"origin": [0, 0, ZB], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_DC203_TRAY"),
         C("sketch.rectangle.two_point", p0=[-38, -276], p1=[378, -40]),
         C("sketch.finish"),
         C("sheet.flange", type="base", sketch="SK_DC203_TRAY", rule="SUS304_t1.5", body_name=TRAY),
         # +Y 끝 Y -40(LOWER 밑, Z -200까지 빈 곳): 지시 -64는 떨어뜨림 길 D1(Y ≤ -61)과 +Y 테두리가 589 mm3 겹쳐 24 늘림(저장 후 확인 1회차)
         # 사방 테두리 90° 위로, 위 끝 Z -233.5(밑면 바깥 꼭짓점부터 16.5 = 판 윗면 위 15)
         C("sheet.flange", type="edge", edges=[[170, -40, zt], [-38, -158, zt], [170, -276, zt], [378, -158, zt]],
           height=16.5, angle=90, body=TRAY, corner_relief_shape="rectangular", corner_relief=1.5),
         C("sketch.create", plane={"origin": [0, 0, zt + 1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name="SK_DC203_TRAY_H")]
    s += [C("sketch.circle.center", center=[x, y], radius=2.75) for x, y in HOLES]
    s += [C("sketch.finish"),
          C("solid.extrude", sketch="SK_DC203_TRAY_H", distance=4, direction="negative", operation="cut", targets=[TRAY]),
          mat_assign([TRAY], "SUS304"),
          C("component.move_bodies", bodies=[TRAY], component=TRAY),
          C("component.metadata.set", component=TRAY, part_number=TRAY, bom_type="normal",
            description="SUS304 t1.5 sheet metal bobbin tray 416x236, 4 rims 15 up, R1.5, holes 5.5 x2 (DC2-03)")]
    return s


def insert(path, comp, cols, places, src_body, pn, mat, desc):
    p0 = places[0]
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=m7.mrow(*cols, p0)),
         C("body.rename", body=src_body, name=comp),
         C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc),
         mat_assign([comp], mat),
         C("occurrence.reparent", occurrence=comp + ":1", parent=U1)]
    s += [m7.copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def stage_tray_bolts():
    bcols = ((0, 0, -1), (0, 1, 0), (1, 0, 0))            # CB 로컬 +X(축) -> -Z, 원점 = 머리 밑
    ncols = ((0, 1, 0), (0, 0, 1), (1, 0, 0))            # HNTT 로컬 X = 홈 방향(+Y), 로컬 Y = 면 법선(+Z)
    s = insert("CB5-12/CB5-12.stp", "CB5-12_DC203", bcols, [(x, y, ZB + T) for x, y in HOLES], "Cut-Extrude1", "CB5-12",
               "SCM435", "Misumi CB5-12 STEP (DC2-03 bobbin tray)")
    s += insert("HNTT8-5/HNTT8-5.stp", "HNTT8-5_DC203", ncols, [(x, y, ZB - 2.5) for x, y in HOLES], "Tap1", "HNTT8-5",
                "Steel", "Misumi HNTT8-5 STEP (DC2-03 bobbin tray T-nut)")
    return s


# ---------------------------------------------------------------- B. 포켓 바닥 비우기
DEL = ["HFS8-4080-3450_M07:1", "HFS8-4080-2960_M07:7", "HFS8-4080-2960_M07:8",
       "P_M07_LBRK_PY_PX:7", "P_M07_LBRK_PY_PX:8", "P_M07_LBRK_PY_PX:9",
       "CB5-16_M07K_NY:7", "CB5-16_M07K_NY:8", "CB5-16_M07K_NY:9",
       "CB5-16_M07K_NX:13", "CB5-16_M07K_NX:15", "CB5-16_M07K_NX:17",
       "HNTT8-5_M07K_PY_PX:7", "HNTT8-5_M07K_PY_PX:8", "HNTT8-5_M07K_PY_PX:9",
       "HNTT8-5_M07K_PX_PY:13", "HNTT8-5_M07K_PX_PY:15", "HNTT8-5_M07K_PX_PY:17"]


def stage_delete():
    return [C("selection.delete", occurrences=DEL)]


def prof(comp, cols, places, L):
    """HFS8-4080-1140 STEP을 넣고 끝면(로컬 X 1140)을 L로 늘이거나 줄인다(M07 받침틀과 같은 길, 실행 규칙 18)."""
    p0 = places[0]
    lx, ly, lz = cols
    fp = [m7.r4(p0[i] + 1140 * lx[i] + 6.3472 * ly[i] + 18.5178 * lz[i]) for i in range(3)]
    s = [C("file.insert_step", path=STEP + F1140, name=comp, matrix=m7.mrow(*cols, p0)),
         C("body.rename", body="Boss-Extrude1", name=comp),
         C("solid.offset_face", faces=[fp], distance=m7.r4(L - 1140), body=comp),
         C("component.metadata.set", component=comp, part_number="HFS8-4080-%d" % L, bom_type="purchased",
           description="Misumi HFS8-4080-1140 STEP, end face offset to L%d (DC2-03)" % L),
         mat_assign([comp], "Aluminum"),
         C("occurrence.reparent", occurrence=comp + ":1", parent=U1)]
    s += [m7.copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def stage_profiles():
    s = prof("HFS8-4080-2680_M07", m7.XM_COLS, [(-2300.0, -1500.0, -290.0)], 2680)
    s += prof("HFS8-4080-165_M07", m7.XM_COLS, [(985.0, -1500.0, -290.0)], 165)
    s += prof("HFS8-4080-1740_M07", m7.YM_COLS, [(565.0, -260.0, -290.0), (955.0, -260.0, -290.0)], 1740)
    s += prof("HFS8-4080-730_M07", m7.XM_COLS, [(380.0, -280.0, -290.0)], 730)
    # 끝캡: 왼 토막 +X 끝(X 380) = 앞 _E:1(1150)을 -770, 오른 토막 -X 끝(X 985) = 앞 _W:1(-2300)을 +3285
    s += [m7.copy("HFC8-4080-B_M07_E:1", [-770.0, 0.0, 0.0]), m7.copy("HFC8-4080-B_M07_W:1", [3285.0, 0.0, 0.0])]
    return s


# 브래킷·볼트·너트: 기존 :1 자리(세계) — M07-K1 생성기 geom과 signatures(v2.5.3) bbox로 확인
SRC = {"P_M07_LBRK_PY_PX:1": (-2260.0, -1480.0, -270.0), "P_M07_LBRK_PY_NX:1": (1110.0, -1480.0, -270.0),
       "CB5-16_M07K_NY:1": (-2230.0, -1474.0, -270.0), "CB5-16_M07K_NX:1": (-2254.0, -1450.0, -270.0),
       "CB5-16_M07K_PX:1": (1104.0, -1450.0, -270.0), "HNTT8-5_M07K_PY_PX:1": (-2230.0, -1482.5, -270.0),
       "HNTT8-5_M07K_PX_PY:1": (-2262.5, -1450.0, -270.0), "HNTT8-5_M07K_NX_PY:1": (1112.5, -1450.0, -270.0)}
# (이름, 구석 X, 구석 Y, n2 X 부호): n1 = +Y(레일 또는 가로대 +Y 면), 구석 Z -270(다리 폭 Z -285~-255)
NEWB = [("K0", 340.0, -1480.0, -1), ("K1", 380.0, -260.0, 1), ("K2", 545.0, -260.0, -1), ("K3", 585.0, -260.0, 1),
        ("K4", 935.0, -260.0, -1), ("K5", 975.0, -260.0, 1), ("K6", 1110.0, -260.0, -1)]


def items(o, sx):
    ox, oy, oz = o
    ha = (ox + 30 * sx, oy, oz)
    hb = (ox, oy + 30, oz)
    px = "PX" if sx > 0 else "NX"
    return [("P_M07_LBRK_PY_%s:1" % px, o),
            ("CB5-16_M07K_NY:1", (ha[0], ha[1] + 6, oz)),
            ("CB5-16_M07K_%s:1" % ("NX" if sx > 0 else "PX"), (hb[0] + 6 * sx, hb[1], oz)),
            ("HNTT8-5_M07K_PY_PX:1", (ha[0], ha[1] - 2.5, oz)),
            ("HNTT8-5_M07K_%s_PY:1" % px, (hb[0] - 2.5 * sx, hb[1], oz))]


def stage_brackets():
    s, lst = [], []
    for nm, x, y, sx in NEWB:
        for src, p in items((x, y, -270.0), sx):
            d = [m7.r4(p[i] - SRC[src][i]) for i in range(3)]
            s.append(m7.copy(src, d))
            lst.append({"bracket": nm, "src": src, "pos": list(p), "translate": d})
    return s, lst


def stage_final():
    occ = ["U1_FRAME:1", "HFS8-4080-2680_M07:1", "HFS8-4080-165_M07:1", "HFS8-4080-1740_M07:1", "HFS8-4080-730_M07:1",
           "CB5-12_DC203:1", "HNTT8-5_DC203:1"]
    return [C("joint.rigid_group", occurrences=occ),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="DC2-03 mechanism: bobbin door cut, SUS304 t1.5 tray, front rail split, crossbar 730, 7 L brackets")]


def main():
    os.makedirs(OUT, exist_ok=True)
    sb, lst = stage_brackets()
    stages = [("1_lower", stage_lower()), ("2_delete", stage_delete()), ("3_profiles", stage_profiles()),
              ("4_brackets", sb), ("5_tray", stage_tray()), ("6_tray_bolts", stage_tray_bolts()), ("7_final", stage_final())]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st))
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.5.3.sc", "result": "3D_Modeling/FSAP_v2.5.4.sc", "generator": "tools/gen_v2_dc203_fix1.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))
    json.dump({"deleted": DEL, "copies": lst, "commands": len(allc)}, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(len(allc), "cmds")


if __name__ == "__main__":
    main()
