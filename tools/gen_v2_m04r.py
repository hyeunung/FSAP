# -*- coding: utf-8 -*-
"""M04R U2 볼 테이블 사진대로 다시 (C-31) — v2.3.4 -> v2.4.0 (모델링부 2026-11-05)
설계안 docs/reports/mechanism/mech_M04R_design.md, 보고서 docs/reports/mechanism/mech_M04R_model.md.
python -X utf8 -B tools/gen_v2_m04.py m04r   -> tools/out/mech_M04R/model/stage_m04r_*.json, tools/out/mech_M04R/edit.json
기존 gen_v2_m04 단계(stage_*.json)는 그대로 두고 이 단계만 더한다.
- 사각 센터판 P_M04_INSERT를 빼고, 볼 피치 100 반 칸 격자(balls_B827.json, D-96 임시)로 바꾼다.
- 센터판이 지던 판·원판 묶음은 가로대 HFS8-4080-560 ×3(CM1·CM_A·CM_B)와 받침판 2장이 받는다.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m04 as g  # noqa: E402
from gen_v2_m02 import C, box, cz, mat_assign  # noqa: E402

OUTD = os.path.join(ROOT, "out", "mech_M04R")
OUT = os.path.join(OUTD, "model")
STEP = g.STEP
U2 = g.U2
LIP, SHIFT = g.LIP, g.NUT_SHIFT

BALLS = [tuple(p) for p in json.load(open(os.path.join(OUTD, "design", "balls_B827.json"), encoding="utf-8"))["pts"]]
PANELS = {
    "W1": [(-2175, -400, -1555, -300)],
    "W2": [(-2175, -410, -300, 300)],
    "W3": [(-2175, -400, 300, 1560)],
    "E1": [(-400, 400, -1555, -300)],
    "E2": [(-410, 400, -300, 300), (400, 975, -250, 300)],
    "E3": [(-400, 975, 300, 1560)],
}
E2_LINE = [[-410, -300], [400, -300], [400, -250], [975, -250], [975, 300], [-410, 300]]
BOSS_X = [-1750, -1600, -1400, -1250, -1000, -800, -600, -450]     # 띠 보스(DC2-05) 구멍 Ø36, Y 0
CM1_Y = [-250, -150, -50, 50, 150, 250]                             # CM1 윗홈 X -400 접시 M5
DB_B = [(-285, 120), (-285, -120), (-65, 120), (-65, -120)]         # DISK_BASE 구멍 Ø5.5
X_FACES = [-380.0, -265.0, -45.0]                                   # 가로대 +X 면(CM1·CM_A·CM_B)
CM_PLACES = [(-400.0, -280.0, -52.0), (-285.0, -280.0, -92.0), (-65.0, -280.0, -92.0)]
CROSS_COLS = ((0, 1, 0), (0, 0, 1), (1, 0, 0))
CB_COLS = {"-Y": ((0, -1, 0), (1, 0, 0), (0, 0, 1)), "+Y": ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
           "-X": ((-1, 0, 0), (0, 1, 0), (0, 0, -1)), "-Z": ((0, 0, -1), (0, 1, 0), (1, 0, 0))}  # STEP 볼트: 로컬 +X = 축(머리 -> 끝), 원점 = 머리 밑면

# 지울 것(v2.3.4 실측 이름)
FHS_LEDGE = ["STEP대기_FHS-M5-10_M04:%d" % i for i in list(range(37, 43)) + list(range(79, 85))]
PZ_INS = ["HNTT8-8_M04_PZ:%d" % i for i in range(73, 81)]
CAPS = ["HFC8-4080-B_M04_E:6", "HFC8-4080-B_M04_E:8"]
CB516 = ["CB5-16_M02_%d" % i for i in range(15, 19)]
INS, CB15, BALL = "P_M04_INSERT", "STEP대기_CB8-15_M04", "STEP대기_BALL_D25_M04"
D25H_LEFT = "STEP대기_BALL_D25H_M04"   # DC2-05가 컴포넌트를 지울 때 남은 바디 잔재 하나(X -1800, Y 0)


def pname(k):
    return "P_M04_PANEL_" + k


def panel_of(x, y):
    hits = [k for k, r in PANELS.items() if g.in_rects(x, y, r)]
    assert len(hits) == 1, (x, y, hits)
    return hits[0]


BY_PANEL = {k: [] for k in PANELS}
for p in BALLS:
    BY_PANEL[panel_of(*p)].append(p)


def grid_rects(pts):
    """피치 100 반 칸 격자 (50+100i, 50+100j) -> 묶음 사각 [(i0,i1,j0,j1)]."""
    S = {(round((x - 50) / 100), round((y - 50) / 100)) for x, y in pts}
    out = []
    while S:
        i0, j0 = min(S, key=lambda t: (t[1], t[0]))
        i1 = i0
        while (i1 + 1, j0) in S:
            i1 += 1
        j1 = j0
        while all((i, j1 + 1) in S for i in range(i0, i1 + 1)):
            j1 += 1
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                S.discard((i, j))
        out.append((i0, i1, j0, j1))
    return out


def circ_pattern(rects, r):
    s = [C("sketch.circle.center", center=[50.0 + 100.0 * i0, 50.0 + 100.0 * j0], radius=r) for (i0, i1, j0, j1) in rects]
    for n, (i0, i1, j0, j1) in enumerate(rects, 1):
        ni, nj = i1 - i0 + 1, j1 - j0 + 1
        if ni * nj > 1:
            p = {"entities": ["c%d" % n], "count": ni, "spacing": 100, "dir": [1, 0]}
            if nj > 1:
                p.update(count2=nj, spacing2=100, dir2=[0, 1])
            s.append(C("sketch.pattern.rectangular", **p))
    return s


def screw_pts(k):
    """접시 M5 자리: 레일 윗홈(slot) 그대로 + E2의 CM1 윗홈(cm1). 센터판 턱(ledge)·센터판 위 제외는 없앰."""
    rects = PANELS[k]
    pts = []
    for ry in g.RAIL_Y:
        for x in g.XS:
            if not any(a + 40 <= x <= b - 40 for a, b in g.rail_segs(ry)):
                continue
            inside = [rr for rr in rects if rr[0] + 40 <= x <= rr[1] - 40 and rr[2] < ry < rr[3]]
            if inside and inside[0][2] + 20 < ry < inside[0][3] - 20:
                pts.append((x, ry, "slot"))
    if k == "E2":
        pts += [(-400, y, "cm1") for y in CM1_Y]
    return sorted(set(pts))


def stage_del():
    s = [C("motion.play", study="REST", step=0, quiet=True),
         C("solid.remove", bodies=[INS, D25H_LEFT]),
         C("selection.delete", occurrences=PZ_INS + FHS_LEDGE + CAPS),
         C("solid.remove", bodies=[CB15]), C("component.delete", component=CB15)]
    # CB5-16_M02_15~18은 STEP 넣기(Import) 바디라 component.delete가 만든 피처째 지운다.
    # 먼저 solid.remove를 넣으면 그 Remove 피처가 다시 계산 때 'unknown body'로 실패했다(앱 저장본 CLI 확인, 보고서 4절).
    s += [C("component.delete", component=c) for c in CB516]
    s += [C("solid.remove", bodies=[BALL]), C("component.delete", component=BALL)]
    return s


def panel_cmds(k):
    nm = pname(k)
    sk = "SK_M04R_" + k
    r = PANELS[k]
    if len(r) == 1:
        a, b, c, d = r[0]
        outline = C("sketch.rectangle.two_point", p0=[a, c], p1=[b, d])
    else:
        outline = C("sketch.line", points=E2_LINE, closed=True)
    s = [C("sketch.create", plane={"origin": [0, 0, g.PZ0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk)]
    s += circ_pattern(grid_rects(BY_PANEL[k]), 18.0)
    s += [C("sketch.circle.center", center=[x, y], radius=2.75) for x, y, _ in screw_pts(k)]
    if k == "W2":
        s += [C("sketch.circle.center", center=[x, 0], radius=18.0) for x in BOSS_X]
    s += [outline, C("sketch.finish"), C("solid.extrude", sketch=sk, distance=4, operation="new", body_name=nm)]
    if k == "E2":   # 원판 구멍 r130(틈 5)·아랫유닛 구멍 X -55~45 · Y ±65
        s += [cz(130.0, -175, 0, -13, -7, "cut", [nm]), box(None, -55, 45, -65, 65, -13, -7, "cut", [nm])]
    return s


def stage_panels(ks):
    s = [C("solid.remove", bodies=[pname(k) for k in ks])]
    for k in ks:
        s += panel_cmds(k)
    s += [mat_assign([pname(k) for k in ks], "SUS304"), C("component.move_bodies", bodies=[pname(k) for k in ks], component=U2)]
    return s


def stage_cs():
    s = []
    for k in PANELS:
        sk = "SK_M04R_CS_" + k
        s += [C("sketch.create", plane={"origin": [0, 0, g.PZ1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk)]
        s += [C("sketch.circle.center", center=[x, y], radius=5.2) for x, y, _ in screw_pts(k)]
        s += [C("sketch.finish"), C("solid.extrude", sketch=sk, distance=2.45, direction="negative", operation="cut", targets=[pname(k)])]
    return s


def stage_profiles():
    comp = body = "HFS8-4080-560_M04"
    s = g.insert_group("HFS8-4080-1900/HFS8-4080-1900.stp", comp, CROSS_COLS, CM_PLACES, [("Boss-Extrude1", body)],
                       pn="HFS8-4080-560", desc="Misumi HFS8-4080-1900 STEP, end face offset to L560 (M04R cross members)", mat="Aluminum")
    s.insert(len(s) - (len(CM_PLACES) - 1) - 1, C("solid.offset_face", faces=["%s:face:0" % body], distance=560 - 1900, body=body))
    return s


def stage_brackets():
    s = []
    for sd, yy in ((+1, -280.0), (-1, 280.0)):
        comp = "HBLFSN8_M04R_X%s" % ("P" if sd > 0 else "N")
        s += g.insert_group("HBLFSN8/HBLFSN8.stp", comp, g.XB_COLS[sd], [(xf, yy, -72.0) for xf in X_FACES], [("NONE", comp)],
                            pn="HBLFSN8", mat="Aluminum")
    s.append(C("joint.rigid_group", occurrences=["U2_TABLE:1", "HBLFSN8_M04R_XP:1", "HBLFSN8_M04R_XN:1"]))
    return s


def fasteners():
    """새 브래킷 6개의 너트(최종 = fix2 3.0 옮김 뒤)·볼트(머리 밑면, 축)."""
    nuts = {"PY": [], "NY": [], "PX": []}
    bolts = {"-Y": [], "+Y": [], "-X": []}
    for xf in X_FACES:
        for yend, sd in ((-280.0, 1), (280.0, -1)):
            nuts["PY" if sd > 0 else "NY"].append((xf + 20.0, yend - sd * (LIP - SHIFT), -72.0))
            bolts["-Y" if sd > 0 else "+Y"].append((xf + 20.0, yend + sd * 9.0, -72.0))
            nuts["PX"].append((xf - LIP + SHIFT, yend + sd * 30.0, -72.0))
            bolts["-X"].append((xf + 8.2, yend + sd * 30.0, -72.0))
    return nuts, bolts


NUT_SRC = {"PY": ("HNTT8-8_M04_PY:1", (-2135.0, -1482.5, -72.0)), "NY": ("HNTT8-8_M04_NY:1", (-2135.0, -1217.5, -72.0)),
           "PX": ("HNTT8-8_M04_PX:1", (-382.5, 350.0, -72.0))}
N5_SRC = ("HNTT8-5_M04:1", (-2100.0, -1500.0, -14.5))
N5_PTS = [(-400.0, y, -12.0 - LIP + SHIFT) for y in CM1_Y] + [(x, y, -52.0 - LIP + SHIFT) for x, y in DB_B]
FHS_SRC = ("STEP대기_FHS-M5-10_M04:1", (-2100.0, -1500.0, -8.0))
CB8_BODY = "Cut-Extrude1"   # STEP 안 바디 이름(CLI 확인: 로컬 +X = 축, 원점 = 머리 밑면)
CB5_BODY = "Cut-Extrude1"


def copies(src, pts):
    occ, p0 = src
    return [g.copy(occ, [p[i] - p0[i] for i in range(3)]) for p in pts]


def stage_nuts():
    nuts, _ = fasteners()
    s = []
    for k, pl in nuts.items():
        s += copies(NUT_SRC[k], pl)
    s += copies(N5_SRC, N5_PTS)
    # 가로대(Y 방향 홈)의 HNTT8-5는 목 긴 쪽을 홈 길이 방향으로: 세계 Z축 90°(fix2 PZ와 같은 이유)
    s += [C("occurrence.move", occurrence="HNTT8-5_M04:%d" % (97 + i), space="world", axis=[0, 0, 1], angle="90 deg", origin=list(p))
          for i, p in enumerate(N5_PTS)]
    return s


def stage_bolts():
    _, bolts = fasteners()
    s = []
    for d, pl in bolts.items():
        comp = "CB8-16_M04R_%s" % d.replace("+", "P").replace("-", "N")
        s += g.insert_group("CB8-16/CB8-16.stp", comp, CB_COLS[d], pl, [(CB8_BODY, comp)], pn="CB8-16",
                            desc="Misumi CB8-16 STEP (M04R bracket bolts)", mat="SCM435")
    s += g.insert_group("CB5-20/CB5-20.stp", "CB5-20_M04R", CB_COLS["-Z"], [(x, y, -40.0) for x, y in DB_B], [(CB5_BODY, "CB5-20_M04R")],
                        pn="CB5-20", desc="Misumi CB5-20 STEP (M04R DISK_BASE to CM_A/CM_B)", mat="SCM435")
    # 접시 M5 6개(CM1 윗홈)는 새 컴포넌트 STEP대기_FHS-M5-10_M04R로 둔다. 기존 컴포넌트에서 복사하면
    # 중간 occurrence를 지운 뒤라 새 이름이 :97~:102로 기존 E3 접시와 겹쳤다(앱 저장본 확인, 보고서 4절).
    comp = "STEP대기_FHS-M5-10_M04R"

    def fhs(p):
        return [C("solid.cone", radius=5.0, height=-2.5, top_radius=2.5, base=list(p), axis="Z", operation="new", body_name=comp),
                cz(2.5, p[0], p[1], p[2] - 10.0, p[2] - 2.5, "join", [comp])]
    s += g.tmp_comp(comp, fhs, comp, [(-400.0, y, -8.0) for y in CM1_Y], "FHS-M5-10",
                    "placeholder ISO 10642 M5x10 flat head (head 10, 90 deg), CM1 top slot (M04R, D-117)", "SCM435")
    return s


def stage_shims():
    s = []
    for tag, xc in (("A", -285.0), ("B", -65.0)):
        nm = "P_M04R_DB_SHIM_" + tag
        s += [box(nm, xc - 20, xc + 20, -135, 135, -52, -48)]
        s += [cz(2.75, xc, y, -53, -47, "cut", [nm]) for y in (120, -120)]
    s += [mat_assign(["P_M04R_DB_SHIM_A", "P_M04R_DB_SHIM_B"], "SUS304"),
          C("component.move_bodies", bodies=["P_M04R_DB_SHIM_A", "P_M04R_DB_SHIM_B"], component=U2)]
    return s


def stage_balls(chunk=None):
    """BALL 컴포넌트를 첫 자리에 다시 만들고 나머지는 세계 이동 복사. chunk=(a,b)면 복사 a..b-1만."""
    pts = [(x, y, 0.0) for x, y in BALLS]
    if chunk is None:
        return g.tmp_comp(BALL, g.ball_body(BALL), BALL, pts[:1], "BALL-D25.4(D-96)",
                          "placeholder resin ball transfer 25.4 press-fit, rating >= 200 N required (M04R, D-96)", "Nylon")
    a, b = chunk
    p0 = pts[0]
    return [g.copy(BALL + ":1", [p[i] - p0[i] for i in range(3)]) for p in pts[a:b]]


HIDE = ["MAT_L", "MAT_S", "MAT_G", "TAPE_L", "TAPE_S", "TAPE_G", "SEAM_L", "SEAM_S", "SEAM_G"]


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, items=HIDE),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M04R mechanism: 827 ball transfers on pitch 100, center plate removed, HFS8-4080-560 cross members x3, shims, CB5-20")]


def all_stages(ball_chunk=200):
    st = [("1_del", stage_del())]
    st += [("2_panels_%s" % k, stage_panels([k])) for k in PANELS]
    st += [("3_cs", stage_cs()), ("4_profiles", stage_profiles()), ("5_brackets", stage_brackets()),
           ("6_nuts", stage_nuts()), ("7_bolts", stage_bolts()), ("8_shims", stage_shims()), ("9_balls_0", stage_balls())]
    n = len(BALLS)
    for a in range(1, n, ball_chunk):
        st.append(("9_balls_%d" % a, stage_balls((a, min(n, a + ball_chunk)))))
    st.append(("10_final", stage_final()))
    return st


def m04r():
    os.makedirs(OUT, exist_ok=True)
    allc = []
    for nm, s in all_stages():
        json.dump(s, open(os.path.join(OUT, "stage_m04r_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += s
        print(nm, len(s), len(json.dumps(s, ensure_ascii=False)))
    json.dump(allc, open(os.path.join(OUTD, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    nuts, bolts = fasteners()
    lists = {"balls": len(BALLS), "balls_by_panel": {k: len(v) for k, v in BY_PANEL.items()},
             "ball_rects": {k: len(grid_rects(v)) for k, v in BY_PANEL.items()},
             "screws": {k: len(screw_pts(k)) for k in PANELS}, "fhs_total": 108 - 12 + 6,
             "nuts8": {k: len(v) for k, v in nuts.items()}, "bolts16": {k: len(v) for k, v in bolts.items()}, "nuts5": len(N5_PTS)}
    json.dump(lists, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(lists, ensure_ascii=False), "cmds", len(allc))
