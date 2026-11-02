# -*- coding: utf-8 -*-
"""v1.0 준비부 생성기 — 작업 대상 모형·조인트·동작 연구 명령(JSON)을 만든다.

python -B tools/gen_v1_prep.py  ->  tools/out/prep_v1/stage_*.json, studies.json, paths.json

좌표(요구서 0-8-3): 바늘점 원점, 작업면 Z 0, 매트 이송 +Y(작업자 반대), 작업자 -Y.
매트 몸통은 바늘의 -X 쪽, 가장자리는 바늘 X 0을 지난다(바인더 방향 가정, 결정은 N00/N01).
원판 중심 c(월드) = -R(theta) p, p = 바늘 밑에 있는 매트 좌표 점(매트 좌표 원점 = 원판 중심 = 매트 가운데).
조인트 값: J_U4_X = cx - C0x, J_U4_Y = cy - C0y, J_U3_ROT = theta(deg).
"""
import json, math, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "prep_v1")
os.makedirs(OUT, exist_ok=True)

C0 = (-900.0, -400.0)        # 대기(로딩) 원판 중심 — 준비부 임시, N00/N08이 정함
T = 10.0                     # 매트 두께 D-04 v0.1.0 자리값
TAPE_T, WING = 1.0, 10.0     # D-06 v0.1.0 자리값
OVERLAP = 30.0               # D-07 이음매 겹침(대화 기록 20~30, T06 구상 L 30)
PRESSER_UP, NEEDLE_DOWN = 20.0, -30.0   # 0-8-5 들림 20 / D-10 v0.1.0 바늘 내림 30
# 홈 매트(D-01·D-02·D-03 v1.0 임시값), 외곽은 D-01 v0.1.0 MAT_GROOVE 1200
G_A = 1200.0
G_W, G_D = 25.0, 150.0
G_R = G_W / 2
G_Y = -300.0                 # 홈 가운데 y(매트 좌표, 시작 변 x=+600 위) — 준비부 배치
MATS = {"L": (1500.0, 1500.0), "S": (300.0, 200.0), "G": (G_A, G_A)}

STEP_FEED, STEP_FINE, STEP_DEG = 25.0, 5.0, 1.0


def rot(th, v):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def center(p, th):
    q = rot(th, p)
    return (-q[0], -q[1])


class Path:
    def __init__(self):
        self.poses = []   # (cx, cy, th, presser, needle, phase)

    def add(self, cx, cy, th, pr, nd, ph):
        self.poses.append((cx, cy, th, pr, nd, ph))

    @property
    def last(self):
        return self.poses[-1]

    def move_c(self, c1, step, ph):
        cx, cy, th, pr, nd, _ = self.last
        L = math.hypot(c1[0] - cx, c1[1] - cy)
        n = max(1, math.ceil(L / step - 1e-9))
        for i in range(1, n + 1):
            f = i / n
            self.add(cx + (c1[0] - cx) * f, cy + (c1[1] - cy) * f, th, pr, nd, ph)

    def tool(self, pr1, nd1, ph):  # 짧은 행정: 양 끝 + 가운데
        cx, cy, th, pr, nd, _ = self.last
        self.add(cx, cy, th, (pr + pr1) / 2, (nd + nd1) / 2, ph)
        self.add(cx, cy, th, pr1, nd1, ph)

    def sew_line(self, p0, p1, th, ph, fine_ends=0.0):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        # 구간 나눔: 끝 fine_ends 길이는 5 mm, 나머지 25 mm
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
        _, _, _, pr, nd, _ = self.last
        for s in cuts[1:]:
            f = s / L
            p = (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)
            c = center(p, th)
            self.add(c[0], c[1], th, pr, nd, ph)

    def pivot(self, p, th0, th1, ph):  # 바늘 중심 회전(노루발 들고 바늘 꽂음)
        self.tool(PRESSER_UP, NEEDLE_DOWN, ph + " 노루발 들기·바늘 꽂음")
        n = max(1, math.ceil(abs(th1 - th0) / STEP_DEG - 1e-9))
        for i in range(1, n + 1):
            th = th0 + (th1 - th0) * i / n
            c = center(p, th)
            self.add(c[0], c[1], th, PRESSER_UP, NEEDLE_DOWN, ph)
        self.tool(0.0, 0.0, ph + " 노루발 내림")

    def arc(self, k, r, ang0, th0, dth, ph):
        """매트 좌표 원 중심 k, 반경 r 위를 따라 봉제(오목 홈 바닥, 왼쪽 꺾임 dth<0).
        바늘점 p(phi) = k + r(cos phi, sin phi), phi = ang0 + (th - th0)."""
        n = max(1, math.ceil(abs(dth) / STEP_DEG - 1e-9))
        _, _, _, pr, nd, _ = self.last
        for i in range(1, n + 1):
            th = th0 + dth * i / n
            phi = math.radians(ang0 - (th - th0))
            p = (k[0] + r * math.cos(phi), k[1] + r * math.sin(phi))
            c = center(p, th)
            self.add(c[0], c[1], th, pr, nd, ph)


def rect_cycle(a, b):
    P = Path()
    P.add(C0[0], C0[1], 0.0, PRESSER_UP, 0.0, "① 대기·로딩")
    start = (a / 2, 0.0)
    P.move_c(center(start, 0.0), STEP_FEED, "② 시작점으로")
    P.tool(0.0, 0.0, "② 노루발 내림")
    corners = [(a / 2, -b / 2), (-a / 2, -b / 2), (-a / 2, b / 2), (a / 2, b / 2)]
    p, th = start, 0.0
    names = ["직선", "직선", "직선", "직선"]
    for i, q in enumerate(corners):
        P.sew_line(p, q, th, "③ 봉제 " + names[i])
        P.pivot(q, th, th + 90, "④ 볼록 모서리 %d" % (i + 1))
        p, th = q, th + 90
    P.sew_line(p, start, th, "③ 봉제 직선")
    end = (a / 2, -OVERLAP)
    P.sew_line(start, end, th, "⑤ 이음매 겹침")
    P.tool(PRESSER_UP, 0.0, "⑤ 사절·노루발 들기")
    P.move_c(C0, STEP_FEED, "⑥ 배출 자리로")
    return P


def groove_cycle():
    a = G_A
    P = Path()
    P.add(C0[0], C0[1], 0.0, PRESSER_UP, 0.0, "① 대기·로딩")
    start = (a / 2, 0.0)
    P.move_c(center(start, 0.0), STEP_FEED, "② 시작점으로")
    P.tool(0.0, 0.0, "② 노루발 내림")
    yN = G_Y + G_W / 2          # 홈 북쪽 벽(먼저 만남)
    yS = G_Y - G_W / 2
    xb = a / 2 - G_D + G_R      # 벽 끝(바닥 반원 시작) x
    m1 = (a / 2, yN)
    P.sew_line(start, m1, 0.0, "③ 봉제 직선", fine_ends=50.0)
    P.pivot(m1, 0.0, 90.0, "④ 홈 입구(볼록)")
    P.sew_line(m1, (xb, yN), 90.0, "③ 홈 안 벽", fine_ends=-1)
    # 바닥 반원: 원 중심 (xb, G_Y), 북쪽 점(각 90°)에서 시작, 왼쪽으로 180° (theta 90 -> -90)
    P.tool(PRESSER_UP, NEEDLE_DOWN, "④ 홈 바닥 노루발 들기·바늘 꽂음")
    P.arc((xb, G_Y), G_R, 90.0, 90.0, -180.0, "④ 홈 바닥 꺾임")
    P.tool(0.0, 0.0, "④ 홈 바닥 노루발 내림")
    m2 = (a / 2, yS)
    P.sew_line((xb, yS), m2, -90.0, "③ 홈 안 벽", fine_ends=-1)
    P.pivot(m2, -90.0, 0.0, "④ 홈 입구(볼록)")
    corners = [(a / 2, -a / 2), (-a / 2, -a / 2), (-a / 2, a / 2), (a / 2, a / 2)]
    p, th = m2, 0.0
    for i, q in enumerate(corners):
        P.sew_line(p, q, th, "③ 봉제 직선", fine_ends=(50.0 if i == 0 else 0.0))
        P.pivot(q, th, th + 90, "④ 볼록 모서리 %d" % (i + 1))
        p, th = q, th + 90
    P.sew_line(p, start, th, "③ 봉제 직선")
    P.sew_line(start, (a / 2, -OVERLAP), th, "⑤ 이음매 겹침")
    P.tool(PRESSER_UP, 0.0, "⑤ 사절·노루발 들기")
    P.move_c(C0, STEP_FEED, "⑥ 배출 자리로")
    return P


def keys_of(P):
    J = {"J_U4_X": [], "J_U4_Y": [], "J_U3_ROT": [], "J_U1_PRESSER": [], "J_U1_NEEDLE": []}
    for i, (cx, cy, th, pr, nd, _) in enumerate(P.poses):
        J["J_U4_X"].append([i, round(cx - C0[0], 4)])
        J["J_U4_Y"].append([i, round(cy - C0[1], 4)])
        J["J_U3_ROT"].append([i, round(th, 4)])
        J["J_U1_PRESSER"].append([i, round(pr, 4)])
        J["J_U1_NEEDLE"].append([i, round(nd, 4)])
    # 같은 값이 이어지는 점은 줄인다(선형 보간이므로 꺾이는 점만 남김)
    out = []
    for j, pts in J.items():
        keep = [pts[0]]
        for k in range(1, len(pts) - 1):
            a, b, c = pts[k - 1][1], pts[k][1], pts[k + 1][1]
            if abs((b - a) - (c - b)) > 1e-6:
                keep.append(pts[k])
        if len(pts) > 1:
            keep.append(pts[-1])
        out.append({"joint": j, "points": keep})
    return out


def phases(P):
    res, cur, s0 = [], None, 0
    for i, pz in enumerate(P.poses):
        if pz[5] != cur:
            if cur is not None:
                res.append([cur, s0, i - 1])
            cur, s0 = pz[5], i
    res.append([cur, s0, len(P.poses) - 1])
    return res


def bodies_stage():
    x0, y0 = C0
    cmds = []
    box = lambda name, xa, xb, ya, yb, za, zb, op="new", tg=None: {
        "command": "solid.box", "params": dict(
            {"length": xb - xa, "width": yb - ya, "height": zb - za, "corner": [x0 + xa, y0 + ya, za],
             "operation": op}, **({"body_name": name} if op == "new" else {"targets": tg}))}
    cyl = lambda r, x, y, za, h, tg: {"command": "solid.cylinder", "params": {
        "radius": r, "height": h, "base": [x0 + x, y0 + y, za], "operation": "cut", "targets": tg}}
    for k in ("L", "S"):
        a, b = MATS[k]
        cmds.append(box("MAT_" + k, -a / 2, a / 2, -b / 2, b / 2, 0, T))
        o = TAPE_T
        cmds.append(box("TAPE_" + k, -a / 2 - o, a / 2 + o, -b / 2 - o, b / 2 + o, 0, T + TAPE_T))
        cmds.append(box(None, -a / 2 + WING, a / 2 - WING, -b / 2 + WING, b / 2 - WING, -1, T + 2, "cut", ["TAPE_" + k]))
        cmds.append(box("SEAM_" + k, a / 2 - WING, a / 2 + 2 * TAPE_T, -OVERLAP, 0, T + TAPE_T, T + 2 * TAPE_T))
    a = G_A; h = a / 2
    xb = h - G_D + G_R
    cmds.append(box("MAT_G", -h, h, -h, h, 0, T))
    cmds.append(box(None, xb, h + 10, G_Y - G_R, G_Y + G_R, -1, T + 1, "cut", ["MAT_G"]))
    cmds.append(cyl(G_R, xb, G_Y, -1, T + 2, ["MAT_G"]))
    o = TAPE_T
    cmds.append(box("TAPE_G", -h - o, h + o, -h - o, h + o, 0, T + TAPE_T))
    cmds.append(box(None, xb, h + 10, G_Y - G_R + o, G_Y + G_R - o, -1, T + 2, "cut", ["TAPE_G"]))
    cmds.append(cyl(G_R - o, xb, G_Y, -1, T + 3, ["TAPE_G"]))
    cmds.append(box("TAPE_G_IN", -h + WING, h - WING, -h + WING, h - WING, -1, T + 2))
    cmds.append(box(None, xb, h + 10, G_Y - G_R - WING, G_Y + G_R + WING, -2, T + 3, "cut", ["TAPE_G_IN"]))
    cmds.append(cyl(G_R + WING, xb, G_Y, -2, T + 5, ["TAPE_G_IN"]))
    cmds.append({"command": "solid.combine", "params": {"target": "TAPE_G", "tools": ["TAPE_G_IN"], "operation": "cut"}})
    cmds.append(box("SEAM_G", h - WING, h + 2 * TAPE_T, -OVERLAP, 0, T + TAPE_T, T + 2 * TAPE_T))
    return cmds


def comps_stage():
    cmds = []
    for k in ("L", "S", "G"):
        cmds.append({"command": "component.create", "params": {"name": "WP_MAT_" + k, "parent": "root", "activate": False}})
        cmds.append({"command": "component.move_bodies", "params": {"bodies": ["MAT_" + k], "component": "WP_MAT_" + k}})
        cmds.append({"command": "component.create", "params": {"name": "WP_TAPE_" + k, "parent": "root", "activate": False}})
        cmds.append({"command": "component.move_bodies", "params": {"bodies": ["TAPE_" + k, "SEAM_" + k], "component": "WP_TAPE_" + k}})
    cmds.append({"command": "joint.rigid_group", "params": {"occurrences": [
        "U3_ROT:1", "WP_MAT_L:1", "WP_MAT_S:1", "WP_MAT_G:1", "WP_TAPE_L:1", "WP_TAPE_S:1", "WP_TAPE_G:1"]}})
    for nm, comp, lim in (("J_U1_PRESSER", "U1_PRESSER", [0, PRESSER_UP]), ("J_U1_NEEDLE", "U1_NEEDLE", [NEEDLE_DOWN, 0])):
        cmds.append({"command": "component.create", "params": {"name": comp, "parent": "root", "activate": False}})
        cmds.append({"command": "joint.create", "params": {
            "type": "slider", "name": nm, "flip": True, "limits": [lim], "quiet": True,
            "a": {"occurrence": "REF_GROUND", "point": [0, 0, 0], "z": [0, 0, 1]},
            "b": {"occurrence": comp, "point": [0, 0, 0], "z": [0, 0, 1]}}})
    return cmds


def skeleton_stage():
    """stage 0: 고정부와 원판 이송 조인트(실제 실행에서는 X 한계를 -200~850으로 만든 뒤 joint.limits로 -200~1250)."""
    o = [C0[0], C0[1], 0]
    j = lambda nm, a, b, z, lim, typ="slider": {"command": "joint.create", "params": {
        "type": typ, "name": nm, "flip": True, "limits": [lim], "quiet": True,
        "a": {"occurrence": a, "point": o, "z": z}, "b": {"occurrence": b, "point": o, "z": z}}}
    return [
        {"command": "component.create", "params": {"name": "REF_GROUND", "parent": "root", "activate": False}},
        {"command": "solid.cylinder", "params": {"radius": 1, "height": 1, "base": [0, 0, -301], "operation": "new", "body_name": "REF_NEEDLE_AXIS_MARK"}},
        {"command": "component.move_bodies", "params": {"bodies": ["REF_NEEDLE_AXIS_MARK"], "component": "REF_GROUND"}},
        {"command": "component.create", "params": {"name": "U4_X", "parent": "root", "activate": False}},
        {"command": "component.create", "params": {"name": "U4_Y", "parent": "root", "activate": False}},
        {"command": "component.create", "params": {"name": "U3_ROT", "parent": "root", "activate": False}},
        {"command": "occurrence.ground", "params": {"occurrence": "REF_GROUND:1", "grounded": True}},
        j("J_U4_X", "REF_GROUND", "U4_X", [1, 0, 0], [-200, 1250]),
        j("J_U4_Y", "U4_X", "U4_Y", [0, 1, 0], [-400, 1200]),
        j("J_U3_ROT", "U4_Y", "U3_ROT", [0, 0, 1], [-360, 720], "revolute"),
    ]


def main():
    G = groove_cycle()
    # 홈 매트는 1000단계(motion.interference 표본 상한, WF-126)를 넘어 둘로 나눈다:
    # G1 = ① ~ 두 번째 홈 입구 회전 끝(노루발 내림), G2 = 그 자세부터 ⑥까지
    cut = max(i for i, p in enumerate(G.poses) if p[5].startswith("④ 홈 입구"))
    G1, G2 = Path(), Path()
    G1.poses = G.poses[:cut + 1]
    G2.poses = G.poses[cut:]
    paths = {"L": rect_cycle(*MATS["L"]), "S": rect_cycle(*MATS["S"]), "G1": G1, "G2": G2}
    studies = []
    info = {}
    rest = {"J_U4_X": 0, "J_U4_Y": 0, "J_U3_ROT": 0, "J_U1_PRESSER": PRESSER_UP, "J_U1_NEEDLE": 0}
    studies.append({"command": "motion.study", "params": {"name": "REST", "steps": 1,
                    "keys": [{"joint": j, "points": [[0, v], [1, v]]} for j, v in rest.items()]}})
    for k, P in paths.items():
        n = len(P.poses) - 1
        studies.append({"command": "motion.study", "params": {"name": "CYCLE_" + k, "steps": n, "keys": keys_of(P)}})
        xs = [p[0] for p in P.poses]; ys = [p[1] for p in P.poses]; ths = [p[2] for p in P.poses]
        sew = [p for p in P.poses if not p[5].startswith(("①", "②", "⑥"))] or P.poses
        info[k] = {"steps": n, "phases": phases(P),
                   "cx_range_all": [min(xs), max(xs)], "cy_range_all": [min(ys), max(ys)],
                   "cx_range_sew": [min(p[0] for p in sew), max(p[0] for p in sew)],
                   "cy_range_sew": [min(p[1] for p in sew), max(p[1] for p in sew)],
                   "theta_range": [min(ths), max(ths)],
                   "poses": [[round(v, 4) if isinstance(v, float) else v for v in p] for p in P.poses]}
    rw = {"J_U4_X": 0, "J_U4_Y": 0, "J_U1_PRESSER": PRESSER_UP, "J_U1_NEEDLE": 0}
    studies.append({"command": "motion.study", "params": {"name": "REWIND_EMPTY", "steps": 72,
                    "keys": [{"joint": "J_U3_ROT", "points": [[0, 360], [72, 0]]}] +
                            [{"joint": j, "points": [[0, v], [72, v]]} for j, v in rw.items()]}})
    json.dump(skeleton_stage(), open(os.path.join(OUT, "stage_0_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(bodies_stage(), open(os.path.join(OUT, "stage_1_bodies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(comps_stage(), open(os.path.join(OUT, "stage_2_comps_joints.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(studies, open(os.path.join(OUT, "stage_3_studies.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(info, open(os.path.join(OUT, "paths.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in info.items():
        print(k, v["steps"], "cx_sew", [round(x, 1) for x in v["cx_range_sew"]], "cy_sew", [round(x, 1) for x in v["cy_range_sew"]],
              "th", v["theta_range"])
    print("studies bytes", os.path.getsize(os.path.join(OUT, "stage_3_studies.json")))


if __name__ == "__main__":
    main()
