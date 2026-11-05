# -*- coding: utf-8 -*-
"""구동 후보 M07-K1 생성기 — 받침틀 브래킷 교체(M5, 렌치 길). 기준 3D_Modeling/FSAP_v2.5.2.sc -> 3D_Modeling/FSAP_v2.5.3.sc
(모델링부 2026-11-05, 보고서 docs/reports/mechanism/mech_M07-K1_model.md, 결정로그 '구동 후보 M07-K1' 1~5항)
python -X utf8 -B tools/gen_v2_m07.py k1   (또는 이 파일 직접)  -> tools/out/mech_M07-K1/model/stage_*.json, edit.json, lists.json
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm.

브래킷 한 개 = 구석 점 o(맞닿는 두 형재 면의 교선, 폭 가운데), n1 = 다리 A가 붙는 면의 바깥 법선, n2 = 다리 B가 붙는 면의 바깥 법선.
다리 A: n1 방향 0~t, n2 방향 0~LA, 구멍 A는 n2 방향 dA. 다리 B: n2 방향 0~t, n1 방향 0~LB, 구멍 B는 n1 방향 dB. 폭 30(lx = n2 x n1, ±15).
모양 셋(지시서 1항 "구멍 두 개 모두 구석에서 30"을 홈 자리에 맞춘 것, 보고서 2절):
  S  45 x 45, 구멍 30/30   — 두 구멍이 모두 홈을 따라 옮겨지는 자리(M07 YX·LEG·LEGY, M04 가로대 끝 XB, M04R XB)
  T  75 x 45, 구멍 60/30   — 다리 A 면의 홈이 구석과 평행해 30에 홈이 없는 자리: 다음 홈(구석에서 60)으로(M07 YM 9개)
  C  45 x 45, 구멍 20/30   — 다리 A 구멍을 구석에서 20 홈에 두는 자리: M07 COL 8개(40 면 홈 하나), M04 레일-침목 72개(위 홈 Z -32는 볼 몸통이 렌치 길을 막아 아래 홈 Z -72). M-04 구멍-굽힘 미달 -> 예외 요청
볼트 CB5-16(실물 STEP, 로컬 +X = 축, 원점 = 머리 밑면), 너트 HNTT8-5(실물 STEP, 로컬 X = 홈 방향, 로컬 Y = 면 바깥 법선, 원점 = 면 - 2.5).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, mat_assign  # noqa: E402
import gen_v2_m07 as m7  # noqa: E402
import gen_v2_m04 as m4  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUTT = os.path.join(ROOT, "out", "mech_M07-K1")
OUT = os.path.join(OUTT, "model")
STEP = PRJ + "/purchased-step/"
T = 6.0
W = 30.0
SHAPES = {"S": (45.0, 30.0, 45.0, 30.0), "T": (75.0, 60.0, 45.0, 30.0), "C": (45.0, 20.0, 45.0, 30.0)}   # LA, dA, LB, dB
M04R_XF = [-380.0, -265.0, -45.0]
r4 = m7.r4
add = m7.add
cross = m7.cross
tag = m7.tag


def neg(v):
    return tuple(-a for a in v)


def all_brackets():
    """(unit, 접두, o, n1, n2, s1, s2, 모양, 종류, 옛 컴포넌트)"""
    B = []
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    for o, n1, n2, s1, s2, kind in m7.brackets():
        shp = {"YM": "T", "COL": "C"}.get(kind, "S")
        B.append(("U1_FRAME", "M07", tuple(map(float, o)), n1, n2, s1, s2, shp, kind,
                  "HBLFSN8_M07_%s_%s" % (tag(n1), tag(n2))))
    for i, (xs, ry) in enumerate(m4.crossings()):
        sd = m4.bracket_side(i, xs, ry)
        B.append(("U2_TABLE", "M04", (float(xs), float(ry + 20 * sd), -92.0), (0, sd, 0), Z, X, Y, "C", "RAIL",
                  "HBLFSN8_M04_%s" % ("P" if sd > 0 else "N")))
    for a, b in m4.CROSS:
        for yend, sd in ((a, 1), (b, -1)):
            B.append(("U2_TABLE", "M04", (-380.0, float(yend), -72.0), (0, sd, 0), X, X, Y, "S", "XB",
                      "HBLFSN8_M04_X%s" % ("P" if sd > 0 else "N")))
    for xf in M04R_XF:
        for yend, sd in ((-280.0, 1), (280.0, -1)):
            B.append(("U2_TABLE", "M04", (xf, yend, -72.0), (0, sd, 0), X, X, Y, "S", "XBR",
                      "HBLFSN8_M04R_X%s" % ("P" if sd > 0 else "N")))
    return B


def geom(b):
    unit, pre, o, n1, n2, s1, s2, shp, kind, old = b
    LA, dA, LB, dB = SHAPES[shp]
    lx = cross(n2, n1)
    ha = add(o, n2, dA)            # 구멍 A(면1 위)
    hb = add(o, n1, dB)            # 구멍 B(면2 위)
    return {"lx": lx, "ha": ha, "hb": hb,
            "bolts": [(add(ha, n1, T), neg(n1)), (add(hb, n2, T), neg(n2))],
            "nuts": [(add(ha, n1, -2.5), n1, s1), (add(hb, n2, -2.5), n2, s2)]}


def comp_name(b):
    unit, pre, o, n1, n2, s1, s2, shp, kind, old = b
    return "P_%s_LBRK%s_%s_%s" % (pre, "" if shp == "S" else shp, tag(n1), tag(n2))


def lbody(nm, b):
    """첫 자리에 L 하나: (u = n2, v = n1) 단면을 lx로 30 밀고 구멍 둘을 자른 뒤 판금 변환(굽힘 = 바깥 구석 모서리, 내R = 규칙 6)."""
    unit, pre, o, n1, n2, s1, s2, shp, kind, old = b
    LA, dA, LB, dB = SHAPES[shp]
    g = geom(b)
    lx = g["lx"]
    org = add(o, lx, -W / 2)
    sk = "SK_" + nm
    pts = [(0, 0), (LA, 0), (LA, T), (T, T), (T, LB), (0, LB)]
    s = [C("sketch.create", plane={"origin": list(org), "x_dir": list(n2), "y_dir": list(n1)}, name=sk),
         C("sketch.line", points=[[r4(u), r4(v)] for u, v in pts], closed=True),
         C("sketch.finish"),
         C("solid.extrude", sketch=sk, distance=W, operation="new", body_name=nm)]
    for p, d in ((g["ha"], n1), (g["hb"], n2)):
        s.append(C("solid.cylinder", radius=2.75, height=T + 1.0, base=list(add(p, d, -0.5)), axis=list(d), operation="cut", targets=[nm]))
    s.append(C("sheet.convert", body=nm, face=list(add(o, n2, (LA + dA) / 2)), rule="SUS304_t6", bends=[list(o)]))
    return s


def group(items, key):
    g = {}
    for it in items:
        g.setdefault(key(it), []).append(it)
    return g


def stage_lbrk(pre):
    s = []
    gb = group([b for b in all_brackets() if b[1] == pre], comp_name)
    for nm, bl in gb.items():
        unit = bl[0][0]
        p0 = bl[0][2]
        LA, dA, LB, dB = SHAPES[bl[0][7]]
        s.append(C("component.create", name=nm, parent=unit, activate=False))
        s += lbody(nm, bl[0])
        s += [mat_assign([nm], "SUS304"), C("component.move_bodies", bodies=[nm], component=nm),
              C("component.metadata.set", component=nm, part_number=nm, bom_type="normal",
                description="SUS304 t6 sheet metal L bracket %gx%gx30, inner R6, holes 5.5 at %g/%g from corner (M07-K1)" % (LA, LB, dA, dB))]
        s += [m7.copy(nm + ":1", [b[2][i] - p0[i] for i in range(3)]) for b in bl[1:]]
    return s, {k: len(v) for k, v in gb.items()}


def insert_group(path, comp, cols, places, src_body, pn, unit, mat, desc):
    p0 = places[0]
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=m7.mrow(*cols, p0)),
         C("body.rename", body=src_body, name=comp),
         C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc),
         mat_assign([comp], mat),
         C("occurrence.reparent", occurrence=comp + ":1", parent=unit)]
    s += [m7.copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def fast_lists(pre):
    bolts, nuts = [], []
    for b in all_brackets():
        if b[1] != pre:
            continue
        g = geom(b)
        for (p, d), kk in zip(g["bolts"], "AB"):
            bolts.append((b[0], p, d, b[8] + "-" + kk))
        for (p, n, sd), kk in zip(g["nuts"], "AB"):
            nuts.append((b[0], p, n, sd, b[8] + "-" + kk))
    return bolts, nuts


def stage_nuts(pre):
    _, nuts = fast_lists(pre)
    gn = group(nuts, lambda x: (x[0], tuple(x[2]), tuple(x[3])))
    s = []
    names = {}
    for (unit, n, sd), pl in gn.items():
        comp = "HNTT8-5_%sK_%s_%s" % (pre, tag(n), tag(sd))
        cols = (sd, n, cross(sd, n))
        s += insert_group("HNTT8-5/HNTT8-5.stp", comp, cols, [x[1] for x in pl], "Tap1", "HNTT8-5", unit, "Steel",
                          "Misumi HNTT8-5 STEP (M07-K1 bracket T-nut)")
        names[comp] = len(pl)
    return s, names


def stage_bolts(pre):
    bolts, _ = fast_lists(pre)
    gb = group(bolts, lambda x: (x[0], tuple(x[2])))
    s = []
    names = {}
    for (unit, d), pl in gb.items():
        comp = "CB5-16_%sK_%s" % (pre, tag(d))
        cols = (d, m7.perp(d), cross(d, m7.perp(d)))
        s += insert_group("CB5-16/CB5-16.stp", comp, cols, [x[1] for x in pl], "Cut-Extrude1", "CB5-16", unit, "SCM435",
                          "Misumi CB5-16 STEP (M07-K1 bracket bolt)")
        names[comp] = len(pl)
    return s, names


OLD_M07 = ["HBLFSN8_M07_%s" % k for k in ("NX_PZ", "NY_NX", "NY_PX", "NZ_NX", "NZ_NY", "NZ_PX", "NZ_PY", "PX_PZ", "PY_NX", "PY_PX", "PZ_NX", "PZ_PX")]
OLD_M07_BOLT = ["CB5-12_M07_%s" % k for k in ("NX", "NY", "NZ", "PX", "PY", "PZ")]
OLD_M04 = ["HBLFSN8_M04_P", "HBLFSN8_M04_N", "HBLFSN8_M04_XP", "HBLFSN8_M04_XN", "HBLFSN8_M04R_XP", "HBLFSN8_M04R_XN"]
OLD_M04_BOLT = ["STEP대기_CB8-16_M04_%s" % k for k in ("NX", "NY", "NZ", "PY")] + ["CB8-16_M04R_%s" % k for k in ("NX", "NY", "PY")]
OLD_M04_NUT = ["HNTT8-8_M04_%s" % k for k in ("PY", "NY", "PZ", "PX")]


def stage_delete():
    """옛 브래킷·볼트·너트 지우기. STEP 넣기 컴포넌트는 component.delete만(바디를 먼저 지우면 타임라인 피처가 깨짐, M04R 보고서),
    STEP대기 임시(component.create + move_bodies)는 바디를 먼저 지우고 컴포넌트를 지운다(M04 fix2 보고)."""
    dn = json.load(open(os.path.join(OUTT, "del_m07_nuts.json"), encoding="utf-8"))
    s = [C("component.delete", component=c) for c in OLD_M07 + OLD_M04]
    s += [C("component.delete", component=c) for c in OLD_M07_BOLT]
    s.append(C("selection.delete", occurrences=dn))
    s += [C("component.delete", component=c) for c in OLD_M04_NUT]
    tmp = [c for c in OLD_M04_BOLT if c.startswith("STEP")]
    s.append(C("solid.remove", bodies=tmp))
    s += [C("component.delete", component=c) for c in OLD_M04_BOLT]
    return s


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M07-K1 mechanism: base frame brackets HBLFSN8 to SUS304 t6 sheet L (M07 55, M04 94), CB5-16 + HNTT8-5")]


def main():
    os.makedirs(OUT, exist_ok=True)
    stages = []
    lists = {}
    for pre in ("M07", "M04"):
        sl, nl = stage_lbrk(pre)
        sn, nn = stage_nuts(pre)
        sb, nb = stage_bolts(pre)
        stages += [("%s_lbrk" % pre, sl), ("%s_nuts" % pre, sn), ("%s_bolts" % pre, sb)]
        lists[pre] = {"lbrk": nl, "nuts": nn, "bolts": nb}
    stages = [stages[0], stages[3], ("delete", stage_delete()), stages[1], stages[2], stages[4], stages[5], ("final", stage_final())]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st))
    br = all_brackets()
    lists["brackets"] = [{"unit": b[0], "pre": b[1], "corner": list(b[2]), "n1": list(b[3]), "n2": list(b[4]), "shape": b[7], "kind": b[8],
                          "old": b[9], "comp": comp_name(b), **{k: list(v) for k, v in geom(b).items() if k in ("lx", "ha", "hb")}} for b in br]
    bl = []
    nl = []
    for pre in ("M07", "M04"):
        bo, nu = fast_lists(pre)
        bl += [{"unit": u, "spec": "CB5-16", "seat": list(p), "axis": list(d), "kind": k} for u, p, d, k in bo]
        nl += [{"unit": u, "pos": list(p), "normal": list(n), "slot": list(sd), "kind": k} for u, p, n, sd, k in nu]
    lists["bolt_list"], lists["nut_list"], lists["commands"] = bl, nl, len(allc)
    json.dump(allc, open(os.path.join(OUTT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.5.2.sc", "result": "3D_Modeling/FSAP_v2.5.3.sc", "generator": "tools/gen_v2_m07k1.py"},
              open(os.path.join(OUTT, "edit_meta.json"), "w", encoding="utf-8"))
    json.dump(lists, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: lists[k] for k in ("M07", "M04")}, len(br), "brackets", len(bl), "bolts", len(allc), "cmds")


if __name__ == "__main__":
    main()
