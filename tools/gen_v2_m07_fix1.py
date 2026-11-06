# -*- coding: utf-8 -*-
"""M07 수정 1회차 생성기 — 기준 3D_Modeling/FSAP_v2.3.3.sc -> 3D_Modeling/FSAP_v2.3.4.sc (모델링부 2026-11-04)
검증 문제 3건 중 (1) 받침 세로 다리·이음판 T너트 볼트 물림, (3) 보 끝 양의 받침(안 A: 보를 기둥 위에 얹음)을 고친다.
(2) 받침틀 브래킷 볼트는 PM 예외 판정(기각)대로 이번 회차에 고치지 않고 구동 후보 M07-K1로 넘긴다.
python -X utf8 -B tools/gen_v2_m07_fix1.py  -> tools/out/mech_M07/fix1/stage_*.json, tools/out/mech_M07/edit.json
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cy, mat_assign  # noqa: E402
from gen_v2_m07 import (U1, BEAM, SPL, COL, COLCAP, STEP, insert_group, perp, cross, tag, copy, XZ, r4)  # noqa: E402

OUTT = os.path.join(ROOT, "out", "mech_M07")
OUT = os.path.join(OUTT, "fix1")
DZ = 642.0 - 250.0           # 기둥 윗끝 642 -> 250 (392 짧게), 길이 1482 -> 1090
COLN = {s: "STEP대기_HFS8-80160-1090_M07_" + s for s in ("NX", "PX")}
AUXO = {s: "HFS8-4080-1482_M07_" + s for s in ("NX", "PX")}
AUXN = {s: "HFS8-4080-1090_M07_" + s for s in ("NX", "PX")}
AUXXY = {"NX": (-2340.0, 300.0), "PX": (1190.0, 300.0)}


def stage_prep():
    return [C("motion.play", study="REST", step=0, quiet=True)]


def stage_columns():
    """기둥 80160(STEP대기)·4080 윗끝을 Z 642 -> 250으로, 기둥 위 캡 4개를 지운다(보가 얹혀 막힌 끝)."""
    s = []
    for sd in ("NX", "PX"):
        xc = -2340.0 if sd == "NX" else 1190.0
        s += [C("solid.offset_face", faces=[[xc, 200.0, 642.0]], distance=-DZ, body=COL[sd]),
              C("body.rename", body=COL[sd], name=COLN[sd])]
        x, y = AUXXY[sd]
        # 4080 끝면 위 점: STEP 로컬 (L, 6.3472, 18.5178), 로컬 X -> +Z, 로컬 Y -> X, 로컬 Z -> Y (gen_v2_m07 AUX_COLS)
        s += [C("solid.offset_face", faces=[[r4(x + 6.3472), r4(y + 18.5178), 642.0]], distance=-DZ, body=AUXO[sd]),
              C("body.rename", body=AUXO[sd], name=AUXN[sd]),
              C("component.rename", component=AUXO[sd], name=AUXN[sd]),
              C("component.metadata.set", component=AUXN[sd], part_number="HFS8-4080-1090",
                description="Misumi HFS8-4080-1140 STEP, end face offset to L1090")]
    s += [C("solid.remove", bodies=[COLCAP["NX"], COLCAP["PX"]]),
          C("component.delete", component="HFC8-4080-B_M07_T")]
    return s


def stage_beam():
    """보 끝면을 80씩 늘여 X -2380~1230(3610), 끝 속은 1 mm 들인 끝판 t8로 막는다(용접, 보 바디에 합침)."""
    # 두 끝면을 따로 offset하면 두 번째가 "a corner whose faces don't meet the same way" 로 거부돼 한 번에 둘을 민다
    # v2.6.5 LITE: 끝 늘이기 offset_face 80은 없앴다 — 보 상자를 gen_v2_m07.stage_beam에서 처음부터 X -2380~1230으로 둔다.
    return [box(None, -2379.0, -2371.0, 127.0, 313.0, 257.0, 643.0, "join", [BEAM]),
            box(None, 1221.0, 1229.0, 127.0, 313.0, 257.0, 643.0, "join", [BEAM])]


def splice(sd):
    """뒤 이음판 SS400 t6 (Y 320~326). 위(보 뒷벽) 넓고 밑(4080 뒷면, Z 150~250)은 기둥 폭만 — L꼴 윤곽."""
    if sd == "NX":
        pts = [(-2380, 150), (-2300, 150), (-2300, 260), (-2200, 260), (-2200, 640), (-2380, 640)]
        hb, hc = (-2260, -2220), (-2360, -2320)
    else:
        pts = [(1230, 150), (1150, 150), (1150, 260), (1060, 260), (1060, 640), (1230, 640)]
        hb, hc = (1070, 1110), (1170, 1210)
    nm = SPL[sd]
    sk = "SK_M07_SPLICE2_" + sd
    s = [C("sketch.create", plane=XZ(326.0), name=sk),
         C("sketch.line", points=[[float(a), float(b)] for a, b in pts], closed=True),
         C("sketch.finish"),
         C("solid.extrude", sketch=sk, distance=6, operation="new", body_name=nm)]
    s += [cy(2.75, x, z, 319.9, 326.1, "cut", [nm]) for x in hb for z in (300, 600)]
    s += [cy(2.75, x, z, 319.9, 326.1, "cut", [nm]) for x in hc for z in (175, 220)]
    return s


def stage_splice():
    s = [C("solid.remove", bodies=[SPL["NX"], SPL["PX"]])]
    s += splice("NX") + splice("PX")
    s += [mat_assign([SPL["NX"], SPL["PX"]], "Steel"),
          C("component.move_bodies", bodies=[SPL["NX"], SPL["PX"]], component=U1)]
    return s


def stage_fasteners():
    """받침 세로 다리 CB5-12 x12 -> CB5-20(물림 8.5), 이음판 4080 쪽 CB5-12 x8 -> CB5-16(물림 7.5)·Z 175/220으로, T너트 8개 같이 옮김."""
    s = [C("selection.delete", occurrences=["CB5-12_M07_NX:%d" % i for i in range(37, 43)] +
           ["CB5-12_M07_PX:%d" % i for i in range(16, 22)] + ["CB5-12_M07_NY:%d" % i for i in range(14, 22)])]
    # 이음판 T너트 HNTT8-5_M07_PY_PZ:3..10 (X -2360,-2320,1170,1210 x Z 300,600) -> Z 175,220
    k = 3
    for x in (-2360, -2320, 1170, 1210):
        for z0, z1 in ((300, 175), (600, 220)):
            s.append(C("occurrence.move", occurrence="HNTT8-5_M07_PY_PZ:%d" % k, space="world",
                       translate=[0, 0, z1 - z0], move_grounded=True))
            k += 1
    # CB5-20 세로 다리(머리 밑 = 다리 안면 X -2291 / 1141, 축 -X / +X)
    for sd, vf, d in (("NX", -2291.0, (-1, 0, 0)), ("PX", 1141.0, (1, 0, 0))):
        cols = (d, perp(d), cross(d, perp(d)))
        places = [(vf, float(y), float(z)) for y in (140, 220, 300) for z in (175, 220)]
        s += insert_group("CB5-20/CB5-20.stp", "CB5-20_M07_%s" % tag(d), cols, places, "Cut-Extrude1", "CB5-20", mat="SCM435")
    # CB5-16 이음판 -> 4080 뒤 홈: CB5-16_M07_NY:1 (-2260, 326, 300)에서 세계 이동 복사
    for x in (-2360, -2320, 1170, 1210):
        for z in (175, 220):
            s.append(copy("CB5-16_M07_NY:1", [x + 2260, 0, z - 300]))
    return s


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M07 mechanism fix1: beam rests on column tops (L3610, end plates), columns L1090, CB5-20/16 T-nut bolts")]


def main():
    os.makedirs(OUT, exist_ok=True)
    stages = [("1_prep", stage_prep()), ("2_columns", stage_columns()), ("3_beam", stage_beam()),
              ("4_splice", stage_splice()), ("5_fasteners", stage_fasteners()), ("6_final", stage_final())]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st))
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.3.3.sc", "result": "3D_Modeling/FSAP_v2.3.4.sc", "generator": "tools/gen_v2_m07_fix1.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
