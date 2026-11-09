# -*- coding: utf-8 -*-
"""v2.0 준비부 생성기 — 골격 컴포넌트·조인트·작업 대상 모형·동작 연구 명령(JSON)과 기계 정의를 만든다.

python -X utf8 -B tools/gen_v2_prep.py  ->  tools/out/prep_v2/stage_*.json, study_*.json, paths.json, tools/machine.json

좌표(요구서 0-8-3): 바늘점 원점, 테이블 면 Z 0, 매트 이송 +Y(작업자 반대), 작업자 -Y, 매트 몸통은 -X 쪽.
매트는 볼 위 평면 운동(모형용 X·Y·회전, 기계 축 아님 — 실행 규칙 20). 매트마다 사슬 하나:
  U1_FRAME -J_WP_k_X-> WP_k_X -J_WP_k_Y-> WP_k_Y -J_WP_k_ROT-> WP_MAT_k (+ WP_TAPE_k 리지드)
매트 중심 c(월드) = -R(theta) p, p = 바늘 밑 매트 좌표 점. 값: X = cx - cpark_x, Y = cy - cpark_y, ROT = theta.
두 바퀴는 바늘을 지나는 X선(Y 0) 위(0-8-1). 바퀴 회전 = 바퀴 밑 매트 점의 Y 변위 / r (v + w*d).
"""
import json, math, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "prep_v2")
os.makedirs(OUT, exist_ok=True)

# --- 임시값(자료대기) ---
T = 10.0                       # 매트 두께 D-04(v0.1.0 자리값, 0절)
TAPE_T, WING = 1.0, 10.0       # D-06 자리값
OVERLAP = 30.0                 # D-07 이음매 겹침
PRESSER_UP, NEEDLE_DOWN = 20.0, -30.0   # 0-8-5 867 들림 20 / D-10 바늘 내림 30(근거 없음)
G_A, G_W, G_D = 1200.0, 25.0, 150.0     # D-01·D-02·D-03 0절: 홈 매트 외곽 1200, U홈 폭 25 깊이 150
G_R = G_W / 2
G_Y = -300.0                   # 홈 가운데 y(매트 좌표, 시작 변 x=+a/2 위) — v1 준비부 배치
MATS = {"L": (1500.0, 1500.0), "S": (300.0, 200.0), "G": (G_A, G_A)}
LOAD_DY = 300.0                # D-106 로딩: 작업자가 매트를 -Y 300에서 밀어 노루발 표시에 맞춤(근거 없음)
D1 = 100.0                     # D-99 바늘 옆 바퀴 d1
WR, WW = 60.0, 25.0            # D-93 바퀴 Ø120 폭 25
LIFT = 30.0                    # D-104 바퀴 들림(근거 없음)
D2_PARK, D2_MIN = 1800.0, 300.0  # D-105 대차: d2 300~1800(행정 1500, 0-8-3 '약 1.5 m'), 대기 1800
D2 = {"L": 1000.0, "G": 800.0, "S": None}   # D-105 매트별 d2(임시 약 2/3 폭), 작은 매트는 내리지 않음
PATCH_Y = 10.0                 # D-104 바퀴 접촉 길이 반(근거 없음, 매트 유무 판정용)
E_EDGE = 6.5                   # D-78·D-144 땀–가장자리 거리 e(F01-C1 v2.8.3, 옛 0): 바늘 경로는 매트 가장자리 안쪽 e, 대기·시작 중심 +e X
# F01-C1: 지금 설계의 연구 키는 뒤 과제(FUNC-01 등)가 고친 것이라, e 6.5 키의 정본은 tools/out/mech_F01-C1/design/newkeys.py(→ newkeys.json, 단계 번호 유지)다.

STEP_FEED, STEP_FINE, STEP_DEG = 25.0, 5.0, 1.0   # 요구서 6-4

MJ = ["J_U3_PRESSER", "J_U3_NEEDLE", "J_U4_PRESS", "J_U4_WHEEL_ROT", "J_U5_X", "J_U5_LIFT", "J_U5_WHEEL_ROT"]
REST_M = {"J_U3_PRESSER": PRESSER_UP, "J_U3_NEEDLE": 0.0, "J_U4_PRESS": LIFT, "J_U4_WHEEL_ROT": 0.0,
          "J_U5_X": 0.0, "J_U5_LIFT": LIFT, "J_U5_WHEEL_ROT": 0.0}


def rot(th, v):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def center(p, th):
    q = rot(th, p)
    return (-q[0], -q[1])


def start_c(k):
    return center((MATS[k][0] / 2 - E_EDGE, 0.0), 0.0)


def park_c(k):
    s = start_c(k)
    return (s[0], s[1] - LOAD_DY)


def in_groove_gap(p):
    """매트 좌표 점이 홈 빈 공간(직사각 + 바닥 반원) 안인지."""
    h = G_A / 2
    xb = h - G_D + G_R
    if xb <= p[0] <= h + 1e-9 and abs(p[1] - G_Y) < G_R:
        return True
    return math.hypot(p[0] - xb, p[1] - G_Y) < G_R


def on_mat(k, p):
    a, b = MATS[k]
    if abs(p[0]) > a / 2 + 1e-6 or abs(p[1]) > b / 2 + 1e-6:
        return False
    if k == "G" and in_groove_gap(p):
        return False
    return True


def on_mat_tol(k, p, tol=0.01):
    a, b = MATS[k]
    if abs(p[0]) > a / 2 + tol or abs(p[1]) > b / 2 + tol:
        return False
    if k == "G" and in_groove_gap(p):
        return False
    return True


class Path:
    def __init__(self, k):
        self.k = k
        self.poses = []   # dict: cx, cy, th, pr, nd, np, fx, fl, ph

    def add(self, **kw):
        d = dict(self.poses[-1]) if self.poses else {}
        d.update(kw)
        self.poses.append(d)

    @property
    def last(self):
        return self.poses[-1]

    def move_c(self, c1, step, ph):
        l = self.last
        L = math.hypot(c1[0] - l["cx"], c1[1] - l["cy"])
        n = max(1, math.ceil(L / step - 1e-9))
        cx, cy = l["cx"], l["cy"]
        for i in range(1, n + 1):
            f = i / n
            self.add(cx=cx + (c1[0] - cx) * f, cy=cy + (c1[1] - cy) * f, ph=ph)

    def short(self, ph, **tgt):  # 짧은 행정: 양 끝 + 가운데(6-4)
        l = self.last
        self.add(ph=ph, **{j: (l[j] + v) / 2 for j, v in tgt.items()})
        self.add(ph=ph, **tgt)

    def carriage(self, fx1, ph):
        l = self.last
        L = abs(fx1 - l["fx"])
        n = max(1, math.ceil(L / STEP_FEED - 1e-9))
        f0 = l["fx"]
        for i in range(1, n + 1):
            self.add(fx=f0 + (fx1 - f0) * i / n, ph=ph)

    def sew_line(self, p0, p1, th, ph, fine_ends=0.0):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        cuts = [0.0]
        if fine_ends > 0 and L > 2 * fine_ends:
            a, b = fine_ends, L - fine_ends
            s = 0.0
            while s < a - 1e-9:
                s = min(a, s + STEP_FINE); cuts.append(s)
            n = max(1, math.ceil((b - a) / STEP_FEED - 1e-9))
            for i in range(1, n + 1):
                cuts.append(a + (b - a) * i / n)
            s = b
            while s < L - 1e-9:
                s = min(L, s + STEP_FINE); cuts.append(s)
        else:
            step = STEP_FINE if fine_ends != 0 else STEP_FEED
            n = max(1, math.ceil(L / step - 1e-9))
            cuts += [L * i / n for i in range(1, n + 1)]
        for s in cuts[1:]:
            f = s / L
            p = (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph)

    def pivot(self, p, th0, th1, ph):
        self.short(ph + " 노루발 들기·바늘 꽂음", pr=PRESSER_UP, nd=NEEDLE_DOWN)
        n = max(1, math.ceil(abs(th1 - th0) / STEP_DEG - 1e-9))
        for i in range(1, n + 1):
            th = th0 + (th1 - th0) * i / n
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph)
        self.short(ph + " 노루발 내림", pr=0.0, nd=0.0)

    def arc(self, k, r, ang0, th0, dth, ph):
        n = max(1, math.ceil(abs(dth) / STEP_DEG - 1e-9))
        for i in range(1, n + 1):
            th = th0 + dth * i / n
            phi = math.radians(ang0 - (th - th0))
            p = (k[0] + r * math.cos(phi), k[1] + r * math.sin(phi))
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph)


def begin(k):
    P = Path(k)
    cp = park_c(k)
    P.add(cx=cp[0], cy=cp[1], th=0.0, pr=PRESSER_UP, nd=0.0, np=LIFT, fx=0.0, fl=LIFT, ph="① 대기·로딩(매트를 올린 자리)")
    P.move_c(start_c(k), STEP_FEED, "① 작업자가 가장자리를 노루발 표시에 맞춤")
    P.short("② 노루발 내림", pr=0.0)
    P.short("② 바늘 옆 바퀴 내림", np=0.0)
    if D2[k] is not None:
        P.carriage(D2_PARK - D2[k], "② 먼 쪽 대차 d2로")
        P.short("② 먼 쪽 바퀴 내림", fl=0.0)
    return P


def finish(P, start, th, a):
    P.sew_line(start, (a / 2 - E_EDGE, -OVERLAP), th, "④ 시작·끝 이음매 겹침")
    P.short("④ 사절·노루발 들기", pr=PRESSER_UP)
    P.short("⑤ 바퀴 들기", np=LIFT, fl=LIFT)
    if P.last["fx"] != 0.0:
        P.carriage(0.0, "⑤ 먼 쪽 대차 대기 자리로")
    l = P.last
    P.move_c((l["cx"], l["cy"] - LOAD_DY), STEP_FEED, "⑤ 배출(작업자가 꺼냄)")
    return P


def rect_cycle(k):
    a, b = MATS[k]
    P = begin(k)
    e = E_EDGE
    start = (a / 2 - e, 0.0)
    corners = [(a / 2 - e, -b / 2 + e), (-a / 2 + e, -b / 2 + e), (-a / 2 + e, b / 2 - e), (a / 2 - e, b / 2 - e)]
    p, th = start, 0.0
    for i, q in enumerate(corners):
        P.sew_line(p, q, th, "③ 봉제 직선")
        P.pivot(q, th, th + 90, "③ 볼록 모서리 %d" % (i + 1))
        p, th = q, th + 90
    P.sew_line(p, start, th, "③ 봉제 직선")
    return finish(P, start, th, a)


def groove_cycle():
    a = G_A
    e = E_EDGE
    P = begin("G")
    start = (a / 2 - e, 0.0)
    yN, yS = G_Y + G_R + e, G_Y - G_R - e   # 홈 벽 안쪽 e
    xb = a / 2 - G_D + G_R
    m1 = (a / 2 - e, yN)
    P.sew_line(start, m1, 0.0, "③ 봉제 직선", fine_ends=50.0)
    P.pivot(m1, 0.0, 90.0, "③ 홈 입구(볼록)")
    P.sew_line(m1, (xb, yN), 90.0, "③ 홈 안 벽", fine_ends=-1)
    P.short("③ 홈 바닥 노루발 들기·바늘 꽂음", pr=PRESSER_UP, nd=NEEDLE_DOWN)
    P.arc((xb, G_Y), G_R + e, 90.0, 90.0, -180.0, "③ 홈 바닥 꺾임(오목)")
    P.short("③ 홈 바닥 노루발 내림", pr=0.0, nd=0.0)
    m2 = (a / 2 - e, yS)
    P.sew_line((xb, yS), m2, -90.0, "③ 홈 안 벽", fine_ends=-1)
    P.pivot(m2, -90.0, 0.0, "③ 홈 입구(볼록)")
    corners = [(a / 2 - e, -a / 2 + e), (-a / 2 + e, -a / 2 + e), (-a / 2 + e, a / 2 - e), (a / 2 - e, a / 2 - e)]
    p, th = m2, 0.0
    for i, q in enumerate(corners):
        P.sew_line(p, q, th, "③ 봉제 직선", fine_ends=(50.0 if i == 0 else 0.0))
        P.pivot(q, th, th + 90, "③ 볼록 모서리 %d" % (i + 1))
        p, th = q, th + 90
    P.sew_line(p, start, th, "③ 봉제 직선")
    return finish(P, start, th, a)


def foot(x):
    return [(x + dx, dy) for dx in (-WW / 2, 0.0, WW / 2) for dy in (-PATCH_Y, 0.0, PATCH_Y)]


def wheels(P):
    """바퀴 밑 매트 유무, 홈에서 바늘 옆 바퀴 들기, 바퀴 회전(매트 점 Y 변위 / r)."""
    k = P.k
    n = len(P.poses)
    # 바퀴 밑 판정(0-8-2 ②③): 바늘 옆 바퀴는 접촉면이 홈 빈 공간 위면 든다.
    # 먼 쪽 바퀴는 접촉선(바퀴 폭, Y 0)이 매트 밖이면 든다(경계 위 = 매트 위, 모서리 회전 시작·끝).
    def near_off(z):
        if k != "G":
            return False
        return any(in_groove_gap(rot(-z["th"], (w[0] - z["cx"], w[1] - z["cy"]))) for w in foot(-D1))

    def far_off(z):
        d = D2_PARK - z["fx"]
        return not all(on_mat_tol(k, rot(-z["th"], (x - z["cx"], -z["cy"]))) for x in (-d - WW / 2, -d, -d + WW / 2))

    lifted, flifted = 0, 0
    offn = [near_off(z) for z in P.poses]
    offf = [far_off(z) for z in P.poses]
    for i, z in enumerate(P.poses):
        if not z["ph"].startswith("③"):
            continue
        near = lambda o: o[i] or (i > 0 and o[i - 1]) or (i + 1 < n and o[i + 1])
        if z["np"] == 0.0 and near(offn):
            z["np"] = LIFT; z["ph"] += " (바늘 옆 바퀴 들림)"; lifted += 1
        if z["fl"] == 0.0 and near(offf):
            z["fl"] = LIFT; z["ph"] += " (먼 쪽 바퀴 들림)"; flifted += 1
    stat = {"near_lifted_steps": lifted, "far_lifted_steps": flifted}
    for key, jn, xw in (("np", "rn", None), ("fl", "rf", None)):
        ang, maxdx, minon = 0.0, 0.0, True
        offs = 0
        for i, z in enumerate(P.poses):
            if i == 0:
                z[jn] = 0.0
                continue
            y = P.poses[i - 1]
            d = D1 if key == "np" else (D2_PARK - y["fx"])
            w = (-d, 0.0)
            if y[key] == 0.0 and z[key] == 0.0:
                p = rot(-y["th"], (w[0] - y["cx"], w[1] - y["cy"]))
                q = rot(z["th"], p)
                w2 = (z["cx"] + q[0], z["cy"] + q[1])
                ang += math.degrees((w2[1] - w[1]) / WR)
                maxdx = max(maxdx, abs(w2[0] - w[0]))
                if not all(on_mat_tol(k, rot(-z["th"], (x - z["cx"], -z["cy"]))) for x in (-d - WW / 2, -d, -d + WW / 2)):
                    offs += 1
            z[jn] = ang
        stat[jn] = {"total_deg": round(ang, 2), "max_side_slip_mm_per_step": round(maxdx, 4), "lowered_steps_off_mat": offs}
    return stat


def keys_of(P):
    k = P.k
    cp = park_c(k)
    J = {j: [] for j in MJ}
    for kk in MATS:
        for ax in ("X", "Y", "ROT"):
            J["J_WP_%s_%s" % (kk, ax)] = []
    for i, z in enumerate(P.poses):
        J["J_WP_%s_X" % k].append([i, round(z["cx"] - cp[0], 4)])
        J["J_WP_%s_Y" % k].append([i, round(z["cy"] - cp[1], 4)])
        J["J_WP_%s_ROT" % k].append([i, round(z["th"], 4)])
        J["J_U3_PRESSER"].append([i, round(z["pr"], 4)])
        J["J_U3_NEEDLE"].append([i, round(z["nd"], 4)])
        J["J_U4_PRESS"].append([i, round(z["np"], 4)])
        J["J_U4_WHEEL_ROT"].append([i, round(z["rn"], 3)])
        J["J_U5_X"].append([i, round(z["fx"], 4)])
        J["J_U5_LIFT"].append([i, round(z["fl"], 4)])
        J["J_U5_WHEEL_ROT"].append([i, round(z["rf"], 3)])
    N = len(P.poses) - 1
    out = []
    for j, pts in J.items():
        if not pts:
            out.append({"joint": j, "points": [[0, 0], [N, 0]]})
            continue
        keep = [pts[0]]
        for m in range(1, len(pts) - 1):
            a, b, c = pts[m - 1][1], pts[m][1], pts[m + 1][1]
            if abs((b - a) - (c - b)) > 1e-3:
                keep.append(pts[m])
        if len(pts) > 1:
            keep.append(pts[-1])
        out.append({"joint": j, "points": keep})
    return out


def phases(P):
    res, cur, s0 = [], None, 0
    for i, z in enumerate(P.poses):
        if z["ph"] != cur:
            if cur is not None:
                res.append([cur, s0, i - 1])
            cur, s0 = z["ph"], i
    res.append([cur, s0, len(P.poses) - 1])
    return res


# ---------------- 설계 명령 ----------------
def comp(name):
    return {"command": "component.create", "params": {"name": name, "parent": "root", "activate": False}}


def move(bodies, c):
    return {"command": "component.move_bodies", "params": {"bodies": bodies, "component": c}}


def stage_skeleton():
    cmds = [comp("U1_FRAME"),
            {"command": "solid.cylinder", "params": {"radius": 1, "height": 1, "base": [0, 0, -301], "operation": "new", "body_name": "REF_NEEDLE_AXIS_MARK"}},
            move(["REF_NEEDLE_AXIS_MARK"], "U1_FRAME"),
            {"command": "occurrence.ground", "params": {"occurrence": "U1_FRAME:1", "grounded": True}}]
    for u in ("U2_TABLE", "U3_HEAD", "U4_WHEEL_N", "U5_WHEEL_F", "U6_SENSOR", "U7_TAPE", "U8_PNEU"):
        cmds.append(comp(u))
    cmds.append({"command": "joint.rigid_group", "params": {"occurrences": [
        "U1_FRAME:1", "U2_TABLE:1", "U3_HEAD:1", "U4_WHEEL_N:1", "U5_WHEEL_F:1", "U6_SENSOR:1", "U7_TAPE:1", "U8_PNEU:1"]}})
    # 바퀴 바디(D-93 임시 Ø120×25, 내린 자세 = 값 0, 바퀴 밑 = 매트 윗면 Z 10)
    zc = T + WR
    cmds += [
        {"command": "solid.cylinder", "params": {"radius": WR, "height": WW, "base": [-D1 - WW / 2, 0, zc], "axis": [1, 0, 0], "operation": "new", "body_name": "U4_WHEEL_TIRE"}},
        {"command": "solid.cylinder", "params": {"radius": WR, "height": WW, "base": [-D2_PARK - WW / 2, 0, zc], "axis": [1, 0, 0], "operation": "new", "body_name": "U5_WHEEL_TIRE"}},
    ]
    for c in ("U3_PRESSER", "U3_NEEDLE", "U4_PRESS", "U4_WHEEL", "U5_CAR", "U5_LIFT", "U5_WHEEL"):
        cmds.append(comp(c))
    cmds += [move(["U4_WHEEL_TIRE"], "U4_WHEEL"), move(["U5_WHEEL_TIRE"], "U5_WHEEL")]
    return cmds


def jc(nm, typ, a, b, pt, z, lim):
    return {"command": "joint.create", "params": {
        "type": typ, "name": nm, "flip": True, "limits": [lim], "quiet": True,
        "a": {"occurrence": a, "point": pt, "z": z}, "b": {"occurrence": b, "point": pt, "z": z}}}


def stage_joints():
    zc = T + WR
    return [
        jc("J_U3_PRESSER", "slider", "U3_HEAD", "U3_PRESSER", [0, 0, 0], [0, 0, 1], [0, PRESSER_UP]),
        jc("J_U3_NEEDLE", "slider", "U3_HEAD", "U3_NEEDLE", [0, 0, 0], [0, 0, 1], [NEEDLE_DOWN, 0]),
        jc("J_U4_PRESS", "slider", "U4_WHEEL_N", "U4_PRESS", [-D1, 0, zc], [0, 0, 1], [0, LIFT]),
        jc("J_U4_WHEEL_ROT", "revolute", "U4_PRESS", "U4_WHEEL", [-D1, 0, zc], [1, 0, 0], [-72000, 72000]),
        jc("J_U5_X", "slider", "U5_WHEEL_F", "U5_CAR", [-D2_PARK, 0, zc], [1, 0, 0], [0, D2_PARK - D2_MIN]),
        jc("J_U5_LIFT", "slider", "U5_CAR", "U5_LIFT", [-D2_PARK, 0, zc], [0, 0, 1], [0, LIFT]),
        jc("J_U5_WHEEL_ROT", "revolute", "U5_LIFT", "U5_WHEEL", [-D2_PARK, 0, zc], [1, 0, 0], [-72000, 72000]),
    ]


def stage_workpiece():
    cmds = []
    for k in ("L", "S", "G"):
        x0, y0 = park_c(k)
        box = lambda name, xa, xb, ya, yb, za, zb, op="new", tg=None: {
            "command": "solid.box", "params": dict(
                {"length": xb - xa, "width": yb - ya, "height": zb - za, "corner": [x0 + xa, y0 + ya, za], "operation": op},
                **({"body_name": name} if op == "new" else {"targets": tg}))}
        cyl = lambda r, x, y, za, h, tg: {"command": "solid.cylinder", "params": {
            "radius": r, "height": h, "base": [x0 + x, y0 + y, za], "operation": "cut", "targets": tg}}
        a, b = MATS[k]
        o = TAPE_T
        if k in ("L", "S"):
            cmds.append(box("MAT_" + k, -a / 2, a / 2, -b / 2, b / 2, 0, T))
            cmds.append(box("TAPE_" + k, -a / 2 - o, a / 2 + o, -b / 2 - o, b / 2 + o, 0, T + TAPE_T))
            cmds.append(box(None, -a / 2 + WING, a / 2 - WING, -b / 2 + WING, b / 2 - WING, -1, T + 2, "cut", ["TAPE_" + k]))
        else:
            h = a / 2
            xb = h - G_D + G_R
            cmds.append(box("MAT_G", -h, h, -h, h, 0, T))
            cmds.append(box(None, xb, h + 10, G_Y - G_R, G_Y + G_R, -1, T + 1, "cut", ["MAT_G"]))
            cmds.append(cyl(G_R, xb, G_Y, -1, T + 2, ["MAT_G"]))
            cmds.append(box("TAPE_G", -h - o, h + o, -h - o, h + o, 0, T + TAPE_T))
            cmds.append(box(None, xb, h + 10, G_Y - G_R + o, G_Y + G_R - o, -1, T + 2, "cut", ["TAPE_G"]))
            cmds.append(cyl(G_R - o, xb, G_Y, -1, T + 3, ["TAPE_G"]))
            cmds.append(box("TAPE_G_IN", -h + WING, h - WING, -h + WING, h - WING, -1, T + 2))
            cmds.append(box(None, xb, h + 10, G_Y - G_R - WING, G_Y + G_R + WING, -2, T + 3, "cut", ["TAPE_G_IN"]))
            cmds.append(cyl(G_R + WING, xb, G_Y, -2, T + 5, ["TAPE_G_IN"]))
            cmds.append({"command": "solid.combine", "params": {"target": "TAPE_G", "tools": ["TAPE_G_IN"], "operation": "cut"}})
        cmds.append(box("SEAM_" + k, a / 2 - WING, a / 2 + 2 * TAPE_T, -OVERLAP, 0, T + TAPE_T, T + 2 * TAPE_T))
    return cmds


def stage_wp_joints():
    cmds = []
    for k in ("L", "S", "G"):
        cp = [park_c(k)[0], park_c(k)[1], 0]
        for c in ("WP_%s_X" % k, "WP_%s_Y" % k, "WP_MAT_" + k, "WP_TAPE_" + k):
            cmds.append(comp(c))
        cmds.append(move(["MAT_" + k], "WP_MAT_" + k))
        cmds.append(move(["TAPE_" + k, "SEAM_" + k], "WP_TAPE_" + k))
        cmds.append({"command": "joint.rigid_group", "params": {"occurrences": ["WP_MAT_%s:1" % k, "WP_TAPE_%s:1" % k]}})
        cmds.append(jc("J_WP_%s_X" % k, "slider", "U1_FRAME", "WP_%s_X" % k, cp, [1, 0, 0], [-3000, 3000]))
        cmds.append(jc("J_WP_%s_Y" % k, "slider", "WP_%s_X" % k, "WP_%s_Y" % k, cp, [0, 1, 0], [-3000, 3000]))
        cmds.append(jc("J_WP_%s_ROT" % k, "revolute", "WP_%s_Y" % k, "WP_MAT_" + k, cp, [0, 0, 1], [-360, 720]))
    return cmds


def all_joints():
    js = MJ[:]
    for k in MATS:
        js += ["J_WP_%s_X" % k, "J_WP_%s_Y" % k, "J_WP_%s_ROT" % k]
    return js


def main():
    paths = {"L": rect_cycle("L"), "S": rect_cycle("S"), "G": groove_cycle()}
    wstat = {k: wheels(P) for k, P in paths.items()}
    # 1000단계 표본 상한(WF-126): 넘으면 둘로 나눔
    final = {}
    for k, P in paths.items():
        if len(P.poses) - 1 > 1000:
            cut = max(i for i, z in enumerate(P.poses) if z["ph"].startswith("③ 홈 입구"))
            A, B = Path(k), Path(k)
            A.poses, B.poses = P.poses[:cut + 1], P.poses[cut:]
            final[k + "1"], final[k + "2"] = A, B
        else:
            final[k] = P
    rest = dict(REST_M)
    for j in all_joints():
        rest.setdefault(j, 0.0)
    studies = {"REST": {"command": "motion.study", "params": {"name": "REST", "steps": 1,
               "keys": [{"joint": j, "points": [[0, v], [1, v]]} for j, v in rest.items()]}}}
    info = {}
    for nm, P in final.items():
        n = len(P.poses) - 1
        studies["CYCLE_" + nm] = {"command": "motion.study", "params": {"name": "CYCLE_" + nm, "steps": n, "keys": keys_of(P)}}
        ths = [z["th"] for z in P.poses]
        info[nm] = {"steps": n, "phases": phases(P), "theta_range": [min(ths), max(ths)],
                    "cx_range": [min(z["cx"] for z in P.poses), max(z["cx"] for z in P.poses)],
                    "cy_range": [min(z["cy"] for z in P.poses), max(z["cy"] for z in P.poses)],
                    "poses": [{kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in z.items()} for z in P.poses]}
    for nm, c in (("stage_0_skeleton", stage_skeleton()), ("stage_1_joints", stage_joints()),
                  ("stage_2_workpiece", stage_workpiece()), ("stage_3_wp_joints", stage_wp_joints())):
        json.dump(c, open(os.path.join(OUT, nm + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for nm, s in studies.items():
        json.dump(s, open(os.path.join(OUT, "study_%s.json" % nm), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"paths": info, "wheels": wstat}, open(os.path.join(OUT, "paths.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for nm, v in info.items():
        sz = os.path.getsize(os.path.join(OUT, "study_CYCLE_%s.json" % nm))
        print(nm, v["steps"], "th", v["theta_range"], "cx", [round(x) for x in v["cx_range"]], "cy", [round(x) for x in v["cy_range"]], "bytes", sz)
    print(json.dumps(wstat, ensure_ascii=False))


if __name__ == "__main__":
    main()
