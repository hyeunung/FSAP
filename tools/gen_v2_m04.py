# -*- coding: utf-8 -*-
"""M04 U2 볼 테이블 생성기 — v2.1.2 -> v2.1.3 (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_M04_design.md, 지시서(모델링부 지시문). 보고서 docs/reports/mechanism/mech_M04_model.md.
python -X utf8 -B tools/gen_v2_m04.py   -> tools/out/mech_M04/model/stage_*.json, lists.json
좌표: 바늘점 원점, 테이블 면(볼 꼭대기·센터판 윗면) Z 0. U2는 고정(조인트 없음).
반복 부품(형재 같은 길이, T너트, 브래킷, 마감캡, STEP대기 볼트·레벨러)은 방향마다 한 컴포넌트를 두고 occurrence.copy(in_place, 세계 이동)로 놓는다.
볼은 패널마다 한 단위(테·몸통·구)를 격자 패턴한 뒤 빠지는 자리를 상자로 잘라 한 바디로 둔다(E-19).
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gen_v2_m02 import C, box, cyl, cz, mat_assign  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M04", "model")
STEP = PRJ + "/purchased-step/"
U2 = "U2_TABLE"

# ---------- 설계안 상수(design_check.py 그대로) ----------
PLATE = (-2175.0, 975.0, -1555.0, 1560.0)
POCKET = (400.0, 1160.0, -1565.0, -250.0)
INSERT = (-400.0, 125.0, -300.0, 300.0)
RAIL_Y = [-1500, -1200, -900, -600, -300, -100, 100, 300, 600, 900, 1200, 1500]
RAIL_Y_SEG = {-100: [(-2175, -420), (545, 975)], 100: [(-2175, -420), (545, 975)]}
CROSS_X, BODY_R, RAIL_HALF = -400.0, 18.0, 20.0


def ball_ok(x, y):
    if not (PLATE[0] + 36 <= x <= PLATE[1] - 36 and PLATE[2] + 36 <= y <= PLATE[3] - 36):
        return False
    if x > POCKET[0] - 36 and y < POCKET[3] + 36:
        return False
    if INSERT[0] - 20 - BODY_R < x < INSERT[1] + 20 + BODY_R and INSERT[2] - BODY_R - RAIL_HALF < y < INSERT[3] + BODY_R + RAIL_HALF:
        return False
    for ry in RAIL_Y:
        segs = RAIL_Y_SEG.get(ry, [(-2175, 975)])
        if abs(y - ry) < RAIL_HALF + BODY_R and any(a - BODY_R <= x <= b + BODY_R for a, b in segs):
            return False
    if abs(x - CROSS_X) < RAIL_HALF + BODY_R and abs(y) > 300:
        return False
    return True


BALLS = [(50.0 * i, 50.0 * j) for i in range(-44, 20) for j in range(-31, 32) if ball_ok(50.0 * i, 50.0 * j)]

# ---------- 패널(SUS304 t4, Z -12~-8) ----------
PZ0, PZ1 = -12.0, -8.0
PANELS = {  # 이름: 사각형 목록(합집합)
    "W1": [(-2175, -400, -1555, -300)],
    "W2": [(-2175, -380, -300, 300)],
    "W3": [(-2175, -400, 300, 1560)],
    "E1": [(-400, 400, -1555, -300)],
    "E2": [(105, 400, -300, 300), (400, 975, -250, 300)],
    "E3": [(-400, 975, 300, 1560)],
}


def pname(k):
    return "P_M04_PANEL_" + k


def bname(k):
    return "STEP대기_BALL_D25_" + k


def in_rects(x, y, rects):
    return any(a <= x <= b and c <= y <= d for a, b, c, d in rects)


def panel_of(x, y):
    hits = [k for k, r in PANELS.items() if in_rects(x, y, r)]
    assert len(hits) == 1, (x, y, hits)
    return hits[0]


BY_PANEL = {k: [] for k in PANELS}
for p in BALLS:
    BY_PANEL[panel_of(*p)].append(p)


def grid_rects(pts):
    """격자 점 집합(50 간격)을 큰 사각 묶음으로 나눔 -> [(i0,i1,j0,j1)] 격자 번호."""
    S = {(round(x / 50), round(y / 50)) for x, y in pts}
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


def ball_unit(nm, x, y, first):
    """볼 트랜스퍼 임시 형상 하나: 테 Ø44 Z -8~-6, 몸통 Ø36 Z -30~-8, 볼 Ø25.4 중심 Z -12.7."""
    s = [cz(22.0, x, y, -8.0, -6.0, "new" if first else "join", None if first else [nm], nm if first else None),
         cz(18.0, x, y, -30.0, -8.0, "join", [nm]),
         C("solid.sphere", radius=12.7, center=[x, y, -12.7], operation="join", targets=[nm])]
    return s


def circ_pattern(rects, r, first_id=1):
    """묶음 사각형마다 원 하나(id c<n>) + 스케치 사각 패턴."""
    s = [C("sketch.circle.center", center=[50.0 * i0, 50.0 * j0], radius=r) for (i0, i1, j0, j1) in rects]
    for n, (i0, i1, j0, j1) in enumerate(rects, first_id):
        ni, nj = i1 - i0 + 1, j1 - j0 + 1
        if ni * nj > 1:
            p = {"entities": ["c%d" % n], "count": ni, "spacing": 50, "dir": [1, 0]}
            if nj > 1:
                p.update(count2=nj, spacing2=50, dir2=[0, 1])
            s.append(C("sketch.pattern.rectangular", **p))
    return s


R_D0 = math.sqrt(12.7 ** 2 - 6.7 ** 2)       # 구 Ø25.4(중심 Z -12.7)의 Z -6 단면 반지름 10.79
TAPER_D = math.degrees(math.atan((R_D0 - 4.0) / 6.0))


def stage_balls(k):
    """패널 k: 스케치 3장(몸통 Ø36 Z -30~-8 · 테 Ø44 Z -8~-6 · 볼 윗부분 Z -6~0)을 쌓아 한 바디(맞닿는 면으로만 결합).
    볼 윗부분은 구 대신 원기둥 Ø20(Z -6~0, 꼭대기 Z 0) 근사.
    구 결합(앱 20분 넘게 안 끝남)·겹치는 원뿔 결합(CLI 751 s)이 느려서 겹치지 않게 쌓는다."""
    nm = bname(k)
    rects = grid_rects(BY_PANEL[k])
    s = []
    for tag, r, z0, h, op, extra in (("B", 18.0, -30.0, 22.0, "new", {}), ("R", 22.0, -8.0, 2.0, "join", {}),
                                    ("D", 10.0, -6.0, 6.0, "join", {})):
        sk = "SK_M04_BALL_%s_%s" % (tag, k)
        s.append(C("sketch.create", plane={"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk))
        s += circ_pattern(rects, r)
        s.append(C("sketch.finish"))
        e = {"sketch": sk, "distance": h, "operation": op}
        if op == "new":
            e["body_name"] = nm
        else:
            e["targets"] = [nm]
        e.update(extra)
        s.append(C("solid.extrude", **e))
    return s, rects


def stage_balls_old(k):
    """패널 k: 묶음 사각형마다 단위 하나 + 사각 패턴(묶음 첫 단위만 new)."""
    nm = bname(k)
    s, first = [], True
    rects = grid_rects(BY_PANEL[k])
    feats = []
    for n, (i0, i1, j0, j1) in enumerate(rects):
        x, y = 50.0 * i0, 50.0 * j0
        tag = "BU_%s_%d" % (k, n)
        u = ball_unit(nm, x, y, first)
        for m, c in enumerate(u):
            c["params"]["name"] = "%s_%d" % (tag, m)
        s += u
        first = False
        ni, nj = i1 - i0 + 1, j1 - j0 + 1
        if ni * nj > 1:
            p = {"features": ["%s_%d" % (tag, m) for m in range(3)], "dir1": [1, 0, 0], "count1": ni, "spacing1": 50}
            if nj > 1:
                p.update(dir2=[0, 1, 0], count2=nj, spacing2=50)
            s.append(C("solid.pattern.rectangular", **p))
    return s, rects


# ---------- 센터판 ----------
INS = "P_M04_INSERT"
LEDGE_TAP_Y = [-250, -150, -50, 50, 150, 250]
CB8_20_X = [-350, -150, 0, 100]
DB_B = [(-285, 120), (-285, -120), (-65, 120), (-65, -120)]


def stage_prep():
    s = [C("motion.play", study="REST", step=0, quiet=True),
         C("solid.remove", bodies=["U2_PLATE", "U2_SUB"])]
    s += [box(INS, -400, 125, -300, 300, -40, 0),
          cz(135.0, -175, 0, -41, 1, "cut", [INS]),
          box(None, -45, 45, -65, 65, -41, 1, "cut", [INS])]
    s += [cz(2.1, x, y, -40.0, -30.0, "cut", [INS]) for x, y in DB_B]
    s += [box(None, -401, -380, -301, 301, -12, 1, "cut", [INS]),
          box(None, 105, 126, -301, 301, -12, 1, "cut", [INS]),
          box(None, -401, 126, 280, 301, -41, -12, "cut", [INS]),
          box(None, -401, 126, -301, -280, -41, -12, "cut", [INS])]
    s += [cz(2.1, x, y, -22.0, -12.0, "cut", [INS]) for x in (-390, 115) for y in LEDGE_TAP_Y]
    # CB8-20 자리파기 8개(Y ±290)는 넣지 않음: 레일 Y ±300 윗면 T홈 열림이 Y ±295~±305라 볼트가 홈에 들지 않고 레일 턱 살에 박힘(예외 요청 E-14, 디테일 M04-X7)
    s += [C("solid.chamfer", edges=[[-251, 300, 0], [-251, -300, 0], [-380, 151, 0], [105, 151, 0],
                                    [11, 65, 0], [11, -65, 0], [45, 21, 0]], distance=1.0, body=INS),
          C("solid.chamfer", edges=[[-310, 0, 0]], distance=0.5, body=INS),
          mat_assign([INS], "A5052")]
    return s


def panel_cmds(k):
    """윤곽 + 압입 구멍 Ø36(묶음 원 + 패턴)을 한 스케치로 그려 4 밀기."""
    nm = pname(k)
    r = PANELS[k]
    sk = "SK_M04_" + k
    if len(r) == 1:
        a, b, c, d = r[0]
        outline = C("sketch.rectangle.two_point", p0=[a, c], p1=[b, d])
    else:
        outline = C("sketch.line", points=[[105, -300], [400, -300], [400, -250], [975, -250], [975, 300], [105, 300]], closed=True)
    rects = grid_rects(BY_PANEL[k])
    return [C("sketch.create", plane={"origin": [0, 0, PZ0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk)] +         circ_pattern(rects, 18.0) + [C("sketch.circle.center", center=[x, y], radius=2.75) for x, y, _ in screw_pts(k)] + [outline, C("sketch.finish"),
                                     C("solid.extrude", sketch=sk, distance=4, operation="new", body_name=nm)]


# ---------- 접시 M5 자리 ----------
XS = [-2100 + 300 * k for k in range(11)]  # -2100 ... 900


def rail_segs(ry):
    if ry in (-100, 100):
        return [(-2175, -420), (545, 975)]
    if ry <= -300:
        return [(-2175, 380)]
    return [(-2175, 975)]


def screw_pts(k):
    """(x, y, kind) kind: slot(레일 T홈, HNTT8-5) | seam(이음 줄 ±10, T홈 밖) | ledge(센터판 턱 탭)."""
    rects = PANELS[k]
    pts = []
    for ry in RAIL_Y:
        for x in XS:
            if not any(a + 40 <= x <= b - 40 for a, b in rail_segs(ry)):
                continue
            for yy in (ry, ry - 10, ry + 10):
                inside = [rr for rr in rects if rr[0] + 40 <= x <= rr[1] - 40 and rr[2] < yy < rr[3]]
                if not inside:
                    continue
                rr = inside[0]
                interior = rr[2] + 20 < ry < rr[3] - 20
                if interior and yy == ry:
                    pts.append((x, yy, "slot"))
                elif (not interior) and yy != ry and rr[2] + 5 <= yy <= rr[3] - 5:
                    pts.append((x, yy, "seam"))
    # 가로대 이음 X -400 (|Y| > 300): W 판 X -410, E 판 X -390, 가로대 가운데 Y
    for yc in (450, 750, 1050, 1350):
        for sy in (1, -1):
            y = sy * yc
            xx = -410 if k in ("W1", "W3") else (-390 if k in ("E1", "E3") else None)
            if xx is not None and in_rects(xx, y, rects):
                pts.append((xx, y, "seam_x"))
    # 센터판 턱
    if k in ("W2", "E2"):
        xx = -390 if k == "W2" else 115
        pts += [(xx, y, "ledge") for y in LEDGE_TAP_Y]
    # 센터판 위 자리 제외
    pts = [p for p in pts if not (p[2] != "ledge" and -400 <= p[0] <= 125 and -300 <= p[1] <= 300)]
    if not ALL_SCREWS:
        # 이음 줄(레일 ±10, 가로대 X -410/-390) 자리는 T홈 열림(중심 ±5) 밖이라 넣지 않음(예외 요청, 디테일 M04-X2)
        pts = [p for p in pts if p[2] in ("slot", "ledge")]
    return sorted(set(pts))


ALL_SCREWS = False
# 볼 트랜스퍼 2,624개 바디: 이 CAD 커널에서 한 바디로 묶는 결합(패턴 join·combine 680개·겹치는 결합)이 앱 50분·CLI 5~15분 넘게 안 끝남(보고서 3절).
# 이번 저장에는 넣지 않고 패널 압입 구멍만 둔다(예외 요청). True로 하면 stage_balls를 넣는다.
WITH_BALLS = False


def stage_panels():
    s = []
    for k in PANELS:
        s += panel_cmds(k)
    s += [mat_assign([pname(k) for k in PANELS], "SUS304")]
    return s


def stage_holes(k, taper=False):
    """접시 M5 자리: 패널 스케치에 넣은 Ø5.5 관통 구멍 위에 접시 90°(윗면 Ø10.4, 깊이 2.45)를 스케치 원 + 기울기 자르기로.
    solid.hole countersink는 압입 구멍 680개 패널에서 240 s 넘게 안 끝나 바꿈."""
    sk = "SK_M04_CS_" + k
    pts = screw_pts(k)
    s = [C("sketch.create", plane={"origin": [0, 0, PZ1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, name=sk)]
    s += [C("sketch.circle.center", center=[x, y], radius=5.2) for x, y, _ in pts]
    e = {"sketch": sk, "distance": 2.45, "direction": "negative", "operation": "cut", "targets": [pname(k)]}
    if taper:
        e["taper"] = "-45 deg"
    s += [C("sketch.finish"), C("solid.extrude", **e)]
    return s


# ---------- 형재 ----------
def rails():
    out = []  # (y, x0, x1)
    for ry in RAIL_Y:
        for a, b in rail_segs(ry):
            out.append((ry, a, b))
    return out


SLEEPERS = [(-2135, -1540, 1540), (-1535, -1540, 1540), (-935, -1540, 1540), (-440, -1540, 1540),
            (360, -1535, -280), (360, 280, 1540), (565, -180, 1540), (955, -180, 1540)]
CROSS = [(sy * a, sy * b) for sy in (1, -1) for a, b in ((320, 580), (620, 880), (920, 1180), (1220, 1480))]
CROSS = [(min(a, b), max(a, b)) for a, b in CROSS]


def mrow(lx, ly, lz, t):
    return [round(v, 6) for i in range(3) for v in (lx[i], ly[i], lz[i], t[i])]


def prof_list():
    """(name, L, origin, (lx,ly,lz)) — STEP 로컬 X 0~1900 길이, Y ±40(80 쪽), Z ±20(40 쪽)."""
    L = []
    for y, a, b in rails():
        L.append(("rail", b - a, (a, y, -52.0), ((1, 0, 0), (0, 0, 1), (0, -1, 0))))
    for x, a, b in SLEEPERS:
        L.append(("sleeper", b - a, (x, a, -132.0), ((0, 1, 0), (0, 0, 1), (1, 0, 0))))
    for a, b in CROSS:
        L.append(("cross", b - a, (-400.0, a, -52.0), ((0, 1, 0), (0, 0, 1), (1, 0, 0))))
    return L


def copy(occ, d):
    return C("occurrence.copy", occurrence=occ, in_place=True, translate=[round(v, 4) for v in d])


def insert_group(path, comp, cols, places, renames=(), pn=None, desc=None, mat=None):
    """첫 자리에 STEP을 넣고 U2_TABLE 아래로 옮긴 뒤 나머지 자리는 세계 이동 복사."""
    p0 = places[0]
    s = [C("file.insert_step", path=STEP + path, name=comp, matrix=mrow(*cols, p0))]
    s += [C("body.rename", body=a, name=b) for a, b in renames]
    md = {"component": comp, "part_number": pn or comp, "bom_type": "purchased"}
    if desc:
        md["description"] = desc
    s.append(C("component.metadata.set", **md))
    if mat:
        s.append(mat_assign([b for _, b in renames], mat))
    s.append(C("occurrence.reparent", occurrence=comp + ":1", parent=U2))
    s += [copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


def stage_profiles():
    s = []
    groups = {}
    for kind, L, o, cols in prof_list():
        groups.setdefault(int(round(L)), []).append((o, cols))
    lists = {}
    for L, items in sorted(groups.items()):
        comp = "HFS8-4080-%d_M04" % L
        # 같은 길이는 방향도 같음(레일·가로대·침목이 길이로 갈림)을 확인
        assert len({c for _, c in items}) == 1, L
        body = "HFS8-4080-%d_M04" % L
        s += insert_group("HFS8-4080-1900/HFS8-4080-1900.stp", comp, items[0][1], [o for o, _ in items],
                          [("Boss-Extrude1", body)], pn="HFS8-4080-%d" % L,
                          desc="Misumi HFS8-4080-1900 STEP, end face offset to L%d" % L, mat="Aluminum")
        # 끝면(로컬 X 1900) 늘이기/줄이기 — 컴포넌트 정의라 복사본도 같이
        s.insert(len(s) - (len(items) - 1) - 1, C("solid.offset_face", faces=["%s:face:0" % body], distance=L - 1900, body=body))
        lists[comp] = len(items)
    return s, lists


def cap_places():
    W, E, S, N = [], [], [], []
    for y, a, b in rails():
        W.append((a, y, -52.0))
        E.append((b, y, -52.0))
    for x, a, b in SLEEPERS:
        S.append((x, a, -132.0))
        N.append((x, b, -132.0))
    return {"W": (((0, 0, 1), (0, -1, 0), (1, 0, 0)), W), "E": (((0, 0, 1), (0, 1, 0), (-1, 0, 0)), E),
            "S": (((0, 0, 1), (1, 0, 0), (0, 1, 0)), S), "N": (((0, 0, 1), (-1, 0, 0), (0, -1, 0)), N)}


def stage_caps():
    s = []
    for k, (cols, pl) in cap_places().items():
        comp = "HFC8-4080-B_M04_" + k
        s += insert_group("HFC8-4080-B/HFC8-4080-B.stp", comp, cols, pl, [("Fillet2", comp)], pn="HFC8-4080-B", mat="Default")
    return s


# ---------- 브래킷·볼트·너트 ----------
def crossings():
    out = []
    for ry, a, b in rails():
        for xs, c, d in SLEEPERS:
            if a <= xs <= b and c <= ry <= d:
                out.append((xs, ry))
    return out


def bracket_side(i, xs, ry):
    side = 1 if i % 2 == 0 else -1
    for xs2, c, d in SLEEPERS:
        if xs2 != xs or not (c <= ry <= d):
            continue
        if ry + 63 > d:
            side = -1
        if ry - 63 < c:
            side = 1
    return side


# 로컬 -> 세계 방향
BR_COLS = {+1: ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), -1: ((1, 0, 0), (0, 0, 1), (0, -1, 0))}
XB_COLS = {+1: ((0, 0, 1), (1, 0, 0), (0, 1, 0)),     # 가로대 끝 Y 작은 쪽(레일 면 +Y 바라봄), 가로대 +X 면
           -1: ((0, 0, -1), (1, 0, 0), (0, -1, 0))}   # 가로대 끝 Y 큰 쪽
NUT_COLS = {"+Y": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-Y": ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            "+Z": ((1, 0, 0), (0, 0, 1), (0, -1, 0)), "-Z": ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
            "+X": ((0, 1, 0), (1, 0, 0), (0, 0, -1))}
LIP = 5.5


def bracket_lists():
    br = {+1: [], -1: []}
    xb = {+1: [], -1: []}
    nuts = {"+Y": [], "-Y": [], "+Z": [], "-Z": [], "+X": []}
    bolts = {"-Y": [], "+Y": [], "-Z": [], "-X": []}   # CB8-16 머리 밑 자리와 축(머리 -> 끝) 방향
    for i, (xs, ry) in enumerate(crossings()):
        sd = bracket_side(i, xs, ry)
        br[sd].append((xs, ry + 20 * sd, -92.0))
        # 다리 A(레일 옆면): 구멍 (xs, Z -72), 판 안쪽 면 Y ry+sd*(20+9), 축 -sd Y
        nuts["+Y" if sd > 0 else "-Y"].append((xs, ry + sd * (20 - LIP), -72.0))
        bolts["-Y" if sd > 0 else "+Y"].append((xs, ry + sd * 29.0, -72.0))
        # 다리 B(침목 윗면): 구멍 (xs, ry+sd*50), 안쪽 면 Z -92+8.2, 축 -Z
        nuts["+Z"].append((xs, ry + sd * 50.0, -92.0 - LIP))
        bolts["-Z"].append((xs, ry + sd * 50.0, -92.0 + 8.2))
    for a, b in CROSS:
        xb[+1].append((-380.0, a, -72.0))
        xb[-1].append((-380.0, b, -72.0))
        for yend, sd in ((a, 1), (b, -1)):
            # 다리 A(레일 옆면 Y = yend): 구멍 X -360, 축 -sd Y
            ry_face = yend
            nuts["+Y" if sd > 0 else "-Y"].append((-360.0, ry_face - sd * LIP, -72.0))
            bolts["-Y" if sd > 0 else "+Y"].append((-360.0, ry_face + sd * 9.0, -72.0))
            # 다리 B(가로대 +X 면 X -380): 구멍 Y yend+sd*30, 축 -X
            nuts["+X"].append((-380.0 - LIP, yend + sd * 30.0, -72.0))
            bolts["-X"].append((-380.0 + 8.2, yend + sd * 30.0, -72.0))
    return br, xb, nuts, bolts


LEVELERS = [(x, y) for x in (-2135, -1535, -935, -440, 360) for y in (-1500, -900, -300, 300, 900, 1500)] + \
           [(x, y) for x in (565, 955) for y in (-100, 600, 1500)]


def stage_brackets():
    br, xb, nuts, bolts = bracket_lists()
    s = []
    for sd, pl in br.items():
        comp = "HBLFSN8_M04_%s" % ("P" if sd > 0 else "N")
        s += insert_group("HBLFSN8/HBLFSN8.stp", comp, BR_COLS[sd], pl, [("NONE", comp)], pn="HBLFSN8", mat="Aluminum")
    for sd, pl in xb.items():
        comp = "HBLFSN8_M04_X%s" % ("P" if sd > 0 else "N")
        s += insert_group("HBLFSN8/HBLFSN8.stp", comp, XB_COLS[sd], pl, [("NONE", comp)], pn="HBLFSN8", mat="Aluminum")
    # STEP 안 리지드 묶음(브래킷 ↔ 하위 BRACKET_HBLFSN8)이 바닥에 안 이어져 floating -> U2_TABLE과 묶음
    s.append(C("joint.rigid_group", occurrences=["U2_TABLE:1"] + ["HBLFSN8_M04_%s:1" % t for t in ("P", "N", "XP", "XN")]))
    return s


def stage_nuts():
    _, _, nuts, _ = bracket_lists()
    s = []
    # 센터판 CB8-20 너트는 T홈(Y ±300 ±5) 밖이라 넣지 않음(디테일 M04-X7). 레벨러 너트(침목 밑면)
    nuts["-Z"] = [(x, y, -172.0 + LIP) for x, y in LEVELERS]
    for d, pl in nuts.items():
        if not pl:
            continue
        comp = "HNTT8-8_M04_%s" % d.replace("+", "P").replace("-", "N")
        s += insert_group("HNTT8-8/HNTT8-8.stp", comp, NUT_COLS[d], pl, [("Tap1", comp)], pn="HNTT8-8", mat="Steel")
    # HNTT8-5: 레일·가로대 윗면 T홈(접시 M5 slot 자리)
    pl = []
    for k in PANELS:
        pl += [(x, y, -12.0 - LIP) for x, y, kd in screw_pts(k) if kd == "slot"]
    s += insert_group("HNTT8-5/HNTT8-5.stp", "HNTT8-5_M04", NUT_COLS["+Z"], pl, [("Tap1", "HNTT8-5_M04")], pn="HNTT8-5", mat="Steel")
    return s


def tmp_comp(comp, body_cmds, body, places, pn, desc, mat):
    """STEP대기 임시 형상: 첫 자리에 바디를 그려 새 컴포넌트(U2_TABLE 아래)로 옮기고 나머지는 복사."""
    p0 = places[0]
    s = [C("component.create", name=comp, parent=U2, activate=False)]
    s += body_cmds(p0)
    s += [mat_assign([body], mat), C("component.move_bodies", bodies=[body], component=comp),
          C("component.metadata.set", component=comp, part_number=pn, bom_type="purchased", description=desc)]
    s += [copy(comp + ":1", [p[i] - p0[i] for i in range(3)]) for p in places[1:]]
    return s


AX = {"-Y": [0, -1, 0], "+Y": [0, 1, 0], "-Z": [0, 0, -1], "-X": [-1, 0, 0]}


def cb8_cmds(nm, at, d, L):
    """CB8-L: 머리 Ø13×8(머리 밑면 at, 머리는 축 반대쪽), 축 Ø8×L(at에서 축 방향)."""
    a = AX[d]
    hb = [at[i] - 8 * a[i] for i in range(3)]
    return [cyl(6.5, hb, 8, a, "new", name=nm), cyl(4.0, list(at), L, a, "join", [nm])]


def stage_bolts():
    _, _, _, bolts = bracket_lists()
    s = []
    for d, pl in bolts.items():
        comp = "STEP대기_CB8-16_M04_%s" % d.replace("+", "P").replace("-", "N")
        s += tmp_comp(comp, lambda p, comp=comp, d=d: cb8_cmds(comp, p, d, 16), comp, pl, "CB8-16",
                      "placeholder JIS B1176 M8x16 (head 13x8)", "SCM435")
    # 센터판 CB8-20 ×8은 넣지 않음(위 stage_prep 주석)
    # 접시 M5x10: 머리 윗면 Z -8, 90° 머리 Ø10, 전체 10
    pl = []
    for k in PANELS:
        pl += [(x, y, -8.0) for x, y, _ in screw_pts(k)]
    comp = "STEP대기_FHS-M5-10_M04"

    def fhs(p):
        return [C("solid.cone", radius=5.0, height=-2.5, top_radius=2.5, base=list(p), axis="Z", operation="new", body_name=comp),
                cz(2.5, p[0], p[1], p[2] - 10.0, p[2] - 2.5, "join", [comp])]
    s += tmp_comp(comp, fhs, comp, pl, "FHS-M5-10", "placeholder ISO 10642 M5x10 flat head (head 10, 90 deg)", "SCM435")
    return s


def stage_levelers():
    comp = "STEP대기_LEVELER_M8_M04"
    pl = [(x, y, -250.0) for x, y in LEVELERS]

    def lev(p):
        x, y = p[0], p[1]
        return [cz(20.0, x, y, -250.0, -240.0, "new", None, comp), cz(6.5, x, y, -240.0, -180.0, "join", [comp]),
                cz(4.0, x, y, -180.0, -164.0, "join", [comp])]
    return tmp_comp(comp, lev, comp, pl, "LEVELER-M8", "placeholder leveling pad M8 (pad 40x10, hex 13, stud M8x16)", "Steel")


def stage_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M04 mechanism: U2 ball table - perforated SUS panels (2624 ball holes), A5052 center plate, HFS8-4080 frame, levelers")]


def main():
    os.makedirs(OUT, exist_ok=True)
    stages = [("1_prep", stage_prep()), ("2_panels", stage_panels())]
    rects = {}
    for k in PANELS:
        st, rects[k] = stage_balls(k)
        if WITH_BALLS:
            stages.append(("3_balls_" + k, st + [mat_assign([bname(k)], "Default")]))
    for k in PANELS:
        stages.append(("4_holes_" + k, stage_holes(k)))
    stages.append(("4z_move", [C("component.move_bodies", bodies=[INS] + [pname(k) for k in PANELS] + ([bname(k) for k in PANELS] if WITH_BALLS else []), component=U2)]))
    sp, plist = stage_profiles()
    stages += [("5_profiles", sp), ("6_caps", stage_caps()), ("7_brackets", stage_brackets()), ("8_nuts", stage_nuts()),
               ("9_bolts", stage_bolts()), ("10_levelers", stage_levelers()), ("11_final", stage_final())]
    allc = []
    for nm, st in stages:
        json.dump(st, open(os.path.join(OUT, "stage_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        allc += st
        print(nm, len(st), len(json.dumps(st, ensure_ascii=False, separators=(",", ":"))))
    json.dump(allc, open(os.path.join(ROOT, "out", "mech_M04", "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    br, xb, nuts, bolts = bracket_lists()
    sc = {k: screw_pts(k) for k in PANELS}
    lists = {"balls_total": len(BALLS), "balls_by_panel": {k: len(v) for k, v in BY_PANEL.items()},
             "ball_rects": {k: len(v) for k, v in rects.items()},
             "screws": {k: len(v) for k, v in sc.items()}, "screw_kinds": {kd: sum(1 for k in sc for p in sc[k] if p[2] == kd) for kd in ("slot", "seam", "seam_x", "ledge")},
             "crossings": len(crossings()), "brackets": {"P": len(br[1]), "N": len(br[-1]), "XP": len(xb[1]), "XN": len(xb[-1])},
             "nuts8": {k: len(v) for k, v in nuts.items()}, "bolts16": {k: len(v) for k, v in bolts.items()},
             "profiles": plist, "levelers": len(LEVELERS), "caps": sum(len(v[1]) for v in cap_places().values())}
    json.dump(lists, open(os.path.join(OUT, "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(lists, ensure_ascii=False))


if __name__ == "__main__":
    main()
