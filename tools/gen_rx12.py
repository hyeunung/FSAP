# -*- coding: utf-8 -*-
"""RX-12 생성기 — 시험 매트 '긴 매트 + 넓은 오목' WP_W(MAT_W), 모형 조인트 J_WP_W_X·Y·ROT, 연구 CYCLE_W1·CYCLE_W2 (v2.15.2 -> v2.16.0).

python -X utf8 -B tools/gen_rx12.py
  -> tools/out/mech_RX-12/model/ 에 stage_1_bodies.json, stage_2_joints.json, study_CYCLE_W1.json, study_CYCLE_W2.json, study_others.json,
     cycle_w.json(자세·구간), envelope_w.json(넓이·겹침), handcalc_w.json(회전력 손계산)
  입력: tools/out/mech_RX-12/model/motion_list_before.json (적용 직전 문서의 motion.list — 다른 연구 키를 그대로 다시 쓰는 데 쓴다),
        tools/out/mech_RX-12/rx12_common.py (측정부 넓이 도구·받침 영역)
설계 초안 tools/out/mech_RX-12/design/rx12_design.py에서 경로만 고쳤다(계산·키는 같다).

좌표·식은 tools/gen_v2_vgr01.py와 같다: 매트 중심 c = -R(th) p (p = 바늘 밑 땀 점, 매트 좌표), 조인트 X = cx - PARK_x, Y = cy - PARK_y, ROT = th.
키 약속은 v2.15.2 설계의 CYCLE_V·CYCLE_L을 그대로 따른다
(피벗 중 노루발 0 = 낮은 누름 C-39, 바늘 -30, 슈 누름 J_U6_PRESS 4.5 / 봉제 -0.4).
임시값: 매트 1500x700x10, 오목 500x300 가운데, 모서리 R 0 (D-01·D-02·D-03), e 6.5(D-78·D-144), d2 440(D-152), 로딩 -Y 300(D-106).
"""
import json, math, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.join(TOOLS, "out", "mech_RX-12")          # 측정부 폴더(rx12_common.py)
HERE = os.path.join(MEAS, "model")                        # 출력 폴더
os.makedirs(HERE, exist_ok=True)
sys.path.insert(0, MEAS)
import rx12_common as C  # noqa: E402  (측정부 넓이 도구·받침 영역)

T = 10.0
LY, HX, NW, ND = 1500.0, 700.0, 500.0, 300.0     # 길이(매트 y), 깊이(매트 x), 오목 폭(y), 오목 깊이(x)
E = 6.5
hx, hy, nw = HX / 2, LY / 2, NW / 2
XN = -hx + ND                                     # 오목 바닥 x = -50
PARK = (-(hx - E), -300.0)                        # (-343.5, -300)
START_C = (PARK[0], 0.0)
STEP_FEED, STEP_FINE, FINE_LEN = 25.0, 5.0, 50.0
PR_UP, ND_DN = 20.0, -30.0
U4_UP, U4_DN = 13.006, 0.0
SP_UP, SP_DN = 4.5, -0.4
SH_PARK = -60.0
LIFT_UP, LIFT_DN, FLOAT_MAT = 30.0, -10.0, 10.0
D1, WR = 100.0, 60.0
D2_PARK, D2_W = 1800.0, 440.0
FX_W = D2_PARK - D2_W                             # J_U5_X 1360
OVERLAP = 30.0
HOLD_IN = 45.0                                    # 오목 안 모서리 회전 중 U5 들기·내림 정지 각(회전 시작부터)

# 매트 좌표 조각(볼록 사각 3개) — 넓이·안/밖 판정용
RECTS = [(XN, hx, -hy, hy), (-hx, XN, nw, hy), (-hx, XN, -hy, -nw)]     # 몸통, 다리1(+y), 다리2(-y)
OUTLINE = [(hx, hy), (-hx, hy), (-hx, nw), (XN, nw), (XN, -nw), (-hx, -nw), (-hx, -hy), (hx, -hy)]
# 땀 점(외곽 안쪽 e)
S0 = (hx - E, 0.0)
S2 = (hx - E, -hy + E)
S3 = (-hx + E, -hy + E)
S4 = (-hx + E, -nw - E)      # 오목 입구2(볼록)
S5 = (XN + E, -nw - E)       # 오목 안 모서리2(오목)
S6 = (XN + E, nw + E)        # 오목 안 모서리1(오목)
S7 = (-hx + E, nw + E)       # 오목 입구1(볼록)
S8 = (-hx + E, hy - E)
S1 = (hx - E, hy - E)
SMID = (XN + E, 0.0)         # 오목 바닥 가운데 = 연구 나눔 점
SEND = (hx - E, -OVERLAP)
U5_IN = 50.0                 # 먼 쪽 바퀴를 내리는·드는 점: 땀 점이 오목 벽 선(매트 y -+250)에서 50 지난 곳
SLOW = (hx - E, -nw - U5_IN)   # (343.5, -300)
SLIFT = (hx - E, nw + U5_IN)   # (343.5, 300)

WP_OLD = ["J_WP_%s_%s" % (k, ax) for k in "LSGV" for ax in ("X", "Y", "ROT")]
WP_NEW = ["J_WP_W_X", "J_WP_W_Y", "J_WP_W_ROT"]
ORDER = ["J_U3_PRESSER", "J_U3_NEEDLE", "J_U4_WHEEL_ROT", "J_U5_X", "J_U5_WHEEL_ROT"] + WP_OLD[:9] + \
        ["J_U4_PRESS", "J_U6_SHIFT", "J_U7_CST_X", "J_U7_CST_Y", "J_U7_CUT", "J_U7_TUCK", "J_U7_FEED", "J_U7_LATCH",
         "J_U5_LIFT", "J_U5_FLOAT"] + WP_OLD[9:] + ["J_U6_PRESS"] + WP_NEW
COL = {"J_U3_PRESSER": "pr", "J_U3_NEEDLE": "nd", "J_U4_PRESS": "np", "J_U4_WHEEL_ROT": "rn", "J_U5_X": "fx",
       "J_U5_LIFT": "fl", "J_U5_FLOAT": "fz", "J_U5_WHEEL_ROT": "rf", "J_U6_SHIFT": "sh", "J_U6_PRESS": "sp"}


def rot(th, v):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def center(p, th):
    q = rot(th, p)
    return (-q[0], -q[1])


class Path:
    def __init__(self):
        self.poses = []

    def add(self, **kw):
        d = dict(self.poses[-1]) if self.poses else {}
        d.update(kw)
        d.setdefault("pt", None)
        self.poses.append(d)

    @property
    def last(self):
        return self.poses[-1]

    def short(self, ph, **tgt):
        l = self.last
        self.add(ph=ph, **{j: (l[j] + v) / 2 for j, v in tgt.items()})
        self.add(ph=ph, **tgt)

    def move_c(self, c1, step, ph):
        l = self.last
        L = math.hypot(c1[0] - l["cx"], c1[1] - l["cy"])
        n = max(1, math.ceil(L / step - 1e-9))
        cx, cy = l["cx"], l["cy"]
        for i in range(1, n + 1):
            f = i / n
            self.add(cx=cx + (c1[0] - cx) * f, cy=cy + (c1[1] - cy) * f, ph=ph, pt=None)

    def carriage(self, fx1, ph):
        l = self.last
        n = max(1, math.ceil(abs(fx1 - l["fx"]) / STEP_FEED - 1e-9))
        f0 = l["fx"]
        for i in range(1, n + 1):
            self.add(fx=f0 + (fx1 - f0) * i / n, ph=ph)

    def sew_line(self, p0, p1, th, ph, fine0=False, fine1=False):
        """p0 -> p1 봉제. fine0·fine1: 그 끝 50 mm를 5 mm 간격(오목 모서리 둘레, 요구서 6-4)."""
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        a = FINE_LEN if fine0 else 0.0
        b = L - (FINE_LEN if fine1 else 0.0)
        cuts = [0.0]
        s = 0.0
        while s < a - 1e-9:
            s = min(a, s + STEP_FINE); cuts.append(s)
        n = max(1, math.ceil((b - a) / STEP_FEED - 1e-9))
        cuts += [a + (b - a) * i / n for i in range(1, n + 1)]
        s = b
        while s < L - 1e-9:
            s = min(L, s + STEP_FINE); cuts.append(s)
        for s in cuts[1:]:
            f = s / L
            p = (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p)

    def turn(self, p, th0, th1, ph, hold=None):
        """바늘점 p 둘레 피벗 1° 간격. hold = (각, {키}, 이름): 그 각에서 정지 한 단계 더(U5 승강)."""
        n = max(1, math.ceil(abs(th1 - th0) - 1e-9))
        for i in range(1, n + 1):
            th = th0 + (th1 - th0) * i / n
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p)
            if hold and abs(th - hold[0]) < 1e-9:
                self.add(ph=ph + " 정지·" + hold[2], **hold[1])

    def pivot(self, p, th0, th1, name, hold=None):
        self.short("④ %s 정지·바늘 꽂음·슈 들기(노루발 낮은 누름 C-39)" % name, nd=ND_DN, sp=SP_UP)
        self.turn(p, th0, th1, "④ %s 바늘 중심 회전" % name, hold=hold)
        self.short("④ %s 바늘 빼기·슈 내림" % name, nd=0.0, sp=SP_DN)


def cycle_w():
    P = Path()
    P.add(cx=PARK[0], cy=PARK[1], th=0.0, pr=PR_UP, nd=0.0, np=U4_UP, fx=0.0, fl=LIFT_UP, fz=0.0, sh=SH_PARK, sp=SP_UP,
          ph="① 대기·로딩(매트를 올린 자리)")
    P.move_c(START_C, STEP_FEED, "① 작업자가 가장자리를 노루발 표시에 맞춤")
    P.short("② 노루발 내림·센서 슈 자리로", pr=0.0, sh=0.0)
    P.add(ph="② 슈 누름·바늘 옆 바퀴 내림", sp=(SP_UP + SP_DN) / 2)
    P.add(ph="② 슈 누름·바늘 옆 바퀴 내림", sp=SP_DN, np=U4_DN)
    P.carriage(FX_W, "② 먼 쪽 대차 d2 440으로(J_U5_X 1360, 바퀴는 들린 채 — 바퀴 밑이 오목 빈 곳)")
    P.sew_line(S0, SLOW, 0.0, "③ 뒤 긴 변 앞 반(오목 뒤 구간, 먼 쪽 바퀴 들림)")
    P.short("③ 정지·먼 쪽 바퀴 내림(땀 점이 오목 벽 선에서 50 지남)", fl=LIFT_DN, fz=FLOAT_MAT)
    P.sew_line(SLOW, S2, 0.0, "③ 뒤 긴 변 앞 반(다리2 뒤 구간)")
    P.pivot(S2, 0.0, 90.0, "볼록 모서리 A")
    P.sew_line(S2, S3, 90.0, "③ 옆 변 A")
    P.pivot(S3, 90.0, 180.0, "볼록 모서리 B")
    P.sew_line(S3, S4, 180.0, "③ 다리2 끝 변", fine1=True)
    P.pivot(S4, 180.0, 270.0, "오목 입구2(볼록)")
    P.sew_line(S4, S5, 270.0, "③ 오목 벽2", fine0=True, fine1=True)
    P.pivot(S5, 270.0, 180.0, "오목 안 모서리2(오목)",
            hold=(270.0 - HOLD_IN, {"fl": LIFT_UP, "fz": 0.0}, "먼 쪽 바퀴 들기(ROT 225)"))
    P.sew_line(S5, SMID, 180.0, "③ 오목 바닥 앞 반(먼 쪽 바퀴 들림)", fine0=True)
    split = len(P.poses) - 1
    P.sew_line(SMID, S6, 180.0, "③ 오목 바닥 뒤 반(먼 쪽 바퀴 들림)", fine1=True)
    P.pivot(S6, 180.0, 90.0, "오목 안 모서리1(오목)",
            hold=(180.0 - HOLD_IN, {"fl": LIFT_DN, "fz": FLOAT_MAT}, "먼 쪽 바퀴 내림(ROT 135)"))
    P.sew_line(S6, S7, 90.0, "③ 오목 벽1", fine0=True, fine1=True)
    P.pivot(S7, 90.0, 180.0, "오목 입구1(볼록)")
    P.sew_line(S7, S8, 180.0, "③ 다리1 끝 변", fine0=True)
    P.pivot(S8, 180.0, 270.0, "볼록 모서리 C")
    P.sew_line(S8, S1, 270.0, "③ 옆 변 B")
    P.pivot(S1, 270.0, 360.0, "볼록 모서리 D")
    P.sew_line(S1, SLIFT, 360.0, "③ 뒤 긴 변 뒤 반(다리1 뒤 구간)")
    P.short("③ 정지·먼 쪽 바퀴 들기(땀 점이 오목 벽 선 50 앞)", fl=LIFT_UP, fz=0.0)
    P.sew_line(SLIFT, SEND, 360.0, "③⑤ 뒤 긴 변 뒤 반(오목 뒤 구간, 먼 쪽 바퀴 들림) + 시작부 위 겹쳐 박기 30")
    P.add(ph="⑥ 노루발 들기", pr=PR_UP / 2)
    P.add(ph="⑥ 노루발 들기·슈 들기", pr=PR_UP, sp=SP_UP)
    P.add(ph="⑥ 바늘 옆 바퀴 들기·센서 슈 대기", sh=SH_PARK / 2)
    P.add(ph="⑥ 바늘 옆 바퀴 들기·센서 슈 대기", sh=SH_PARK, np=U4_UP)
    P.carriage(0.0, "⑥ 먼 쪽 대차 대기로(J_U5_X 0)")
    l = P.last
    P.move_c((l["cx"], l["cy"] - 300.0), STEP_FEED, "⑥ 배출(-Y 300, D-106)")
    return P, split


def wheel_rot(P):
    for key, jn in (("np", "rn"), ("fl", "rf")):
        ang = 0.0
        for i, z in enumerate(P.poses):
            if i == 0:
                z[jn] = 0.0
                continue
            y = P.poses[i - 1]
            down = (lambda v: v < 1.0) if key == "np" else (lambda v: v == LIFT_DN)
            d = D1 if key == "np" else (D2_PARK - y["fx"])
            if down(y[key]) and down(z[key]):
                w = (-d, 0.0)
                p = rot(-y["th"], (w[0] - y["cx"], w[1] - y["cy"]))
                q = rot(z["th"], p)
                ang += math.degrees((z["cy"] + q[1] - w[1]) / WR)
            z[jn] = ang


def compress(pts):
    keep = [pts[0]]
    for m in range(1, len(pts) - 1):
        a, b, c = pts[m - 1][1], pts[m][1], pts[m + 1][1]
        if abs((b - a) - (c - b)) > 1e-4:
            keep.append(pts[m])
    if len(pts) > 1:
        keep.append(pts[-1])
    return keep


def keys_for(poses):
    N = len(poses) - 1
    out = []
    for j in ORDER:
        if j in COL:
            nd = 3 if j.endswith("ROT") else 4
            pts = [[i, round(z[COL[j]], nd)] for i, z in enumerate(poses)]
        elif j == "J_WP_W_X":
            pts = [[i, round(z["cx"] - PARK[0], 4)] for i, z in enumerate(poses)]
        elif j == "J_WP_W_Y":
            pts = [[i, round(z["cy"] - PARK[1], 4)] for i, z in enumerate(poses)]
        elif j == "J_WP_W_ROT":
            pts = [[i, round(z["th"], 4)] for i, z in enumerate(poses)]
        else:
            pts = [[0, 0], [N, 0]]
        out.append({"joint": j, "points": compress(pts)})
    return out


def phases(poses, off=0):
    res, cur, s0 = [], None, 0
    for i, z in enumerate(poses):
        if z["ph"] != cur:
            if cur is not None:
                res.append([cur, s0 + off, i - 1 + off])
            cur, s0 = z["ph"], i
    res.append([cur, s0 + off, len(poses) - 1 + off])
    return res


# ---------------- 평면 판정 ----------------
def world(z, q):
    r = rot(z["th"], q)
    return (z["cx"] + r[0], z["cy"] + r[1])


def to_mat(z, w):
    return rot(-z["th"], (w[0] - z["cx"], w[1] - z["cy"]))


def in_mat(q, tol=1e-6):
    return any(x0 - tol <= q[0] <= x1 + tol and y0 - tol <= q[1] <= y1 + tol for x0, x1, y0, y1 in RECTS)


def contact_on(z, d, half_y=3.0, half_x=12.5):
    """바퀴 접점 선(X -d±12.5, Y ±3)이 모두 매트 위인가, 매트 가장자리까지 최소 여유(매트 좌표 사각 기준, 음수 = 밖)."""
    pts = [(-d + sx * half_x, sy * half_y) for sx in (-1, 0, 1) for sy in (-1, 0, 1)]
    return all(in_mat(to_mat(z, w)) for w in pts)


def analyse(poses, split):
    best, rows = {}, []
    u4_off, u5_off, u5_could = [], [], []
    for i, z in enumerate(poses):
        polys = [[world(z, q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))] for x0, x1, y0, y1 in RECTS]
        verts = [world(z, q) for q in OUTLINE]
        m = C.metrics(polys, verts)
        C.update(best, m, "단계 %d(%s) %s ROT %.1f" % (i if i <= split else i - split, "W1" if i <= split else "W2", z["ph"], z["th"]))
        on4 = contact_on(z, D1)
        on5 = contact_on(z, D2_PARK - z["fx"])
        if z["np"] < 1.0 and not on4:
            u4_off.append(i)
        if z["fl"] == LIFT_DN and not on5:
            u5_off.append(i)
        if z["fl"] != LIFT_DN and on5 and z["fx"] == FX_W:
            u5_could.append(i)
        rows.append({"i": i, "ph": z["ph"], "th": round(z["th"], 2), "xmax": round(m["xmax"], 1), "A_+X": round(m["A_+X(X>6.5)"]),
                     "A_볼밖": round(m["A_볼 받침 밖"]), "A_패널밖": round(m["A_패널 밖"]), "A_포켓": round(m["A_포켓(X>400,Y<-300)"]),
                     "A_X>975": round(m["A_X>975"]), "u4_on": on4, "u5_on": on5})
    return best, rows, u4_off, u5_off, u5_could


def phase_max(rows):
    out, cur = [], None
    for r in rows:
        if cur is None or cur["ph"] != r["ph"]:
            cur = {"ph": r["ph"], "s0": r["i"], "s1": r["i"], "xmax": r["xmax"], "A_+X": r["A_+X"], "A_볼밖": r["A_볼밖"],
                   "A_패널밖": r["A_패널밖"], "A_포켓": r["A_포켓"], "A_X>975": r["A_X>975"]}
            out.append(cur)
        else:
            cur["s1"] = r["i"]
            for k in ("xmax", "A_+X", "A_볼밖", "A_패널밖", "A_포켓", "A_X>975"):
                cur[k] = max(cur[k], r[k])
    return out


def obstacle_gap(poses, split):
    """외곽을 5 mm로 찍어 매트 높이 층 고정 바디(평면 사각)까지 최소 거리. 겹치면 0."""
    pts = []
    n = len(OUTLINE)
    for i in range(n):
        a, b = OUTLINE[i], OUTLINE[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1]); k = int(L / 5)
        pts += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    best = {}
    for i, z in enumerate(poses):
        W = [world(z, q) for q in pts]
        for name, (x0, x1, y0, y1) in C.OBST.items():
            d = min(math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) for x, y in W)
            if name not in best or d < best[name][0]:
                best[name] = (d, i, z["ph"], z["th"])
    return {k: dict(gap=round(v[0], 1), step="%s %d" % (("W1", v[1]) if v[1] <= split else ("W2", v[1] - split)), ph=v[2], rot=round(v[3], 1)) for k, v in best.items()}


# ---------------- 회전력 손계산(tools/out/mech_VGR-01/fix1calc.py 식) ----------------
def handcalc():
    g, rho = 9.81, 6.0
    mu_w, d1, d2 = 0.4, 0.100, D2_W / 1000
    F4, F5, f5 = 40.0, 44.0, 4.0
    st = 5.0
    dA = (st / 1000) ** 2
    cells = []
    for x0, x1, y0, y1 in RECTS:
        nx, ny = int(round((x1 - x0) / st)), int(round((y1 - y0) / st))
        cells += [(x0 + (i + .5) * st, y0 + (j + .5) * st) for i in range(nx) for j in range(ny)]
    mass = rho * dA * len(cells)

    def about(p):
        I = R = 0.0
        for x, y in cells:
            r = math.hypot(x - p[0], y - p[1]) / 1000
            I += r * r; R += r
        return rho * dA * I, rho * dA * g * R
    W_disk = rho * math.pi * 0.125 ** 2 * g
    T_ex = 0.3 * W_disk * 0.04 + 2 * 0.005 * (0.1 / 0.075) + 0.096       # 원판 끌림 + 베어링 + 노루발 낮은 누름 끌림(DC-04 T_f)
    I_disk = 0.5 * (583642e-9 * 2680) * 0.125 ** 2 * (0.1 / 0.075) ** 2

    def seg(name, th, w, piv, cr=0.02, mus=0.30):
        I, Rg = about(piv)
        have = mu_w * F4 * d1
        T_strip = 0.0
        if "U5" in w:
            have += mu_w * (F5 - f5) * d2
            T_strip = mus * (F5 - f5) * d2
        room = have - cr * Rg - T_ex - T_strip
        Ie = I + I_disk
        tmin = math.sqrt(4 * math.radians(th) * Ie / room) if room > 0 else None
        return dict(seg=name, theta_deg=th, wheels=w, I=round(I, 3), T_roll=round(cr * Rg, 3), T_extra=round(T_ex, 3),
                    T_strip=round(T_strip, 3), have=round(have, 3), room=round(room, 3),
                    t_min_SF1_s=None if tmin is None else round(tmin, 2))
    segs = [("볼록 모서리 A·D (90°, U4+U5)", 90, ["U4", "U5"], S2), ("볼록 모서리 B·C (90°, U4+U5)", 90, ["U4", "U5"], S3),
            ("오목 입구2·1 (90°, U4+U5)", 90, ["U4", "U5"], S4),
            ("오목 안 모서리 U4+U5 구간 45°", 45, ["U4", "U5"], S5), ("오목 안 모서리 U4 혼자 구간 45°", 45, ["U4"], S5)]
    res = {"_식": "tools/out/mech_VGR-01/fix1calc.py seg()와 같음: 면밀도 6 kg/m2(D-145), 바퀴 mu 0.4(D-95), U4 40 N·d1 0.1, U5 40 N·d2 0.44, "
                 "볼 구름 0.02(D-96 선정 조건), U5 밑 띠 mu_s 0.30(D-97 높은 쪽), 원판 끌림·관성, 노루발 끌림 0.096 N·m(DC-04). 정지->정지 삼각 속도",
           "mass_kg": round(mass, 3), "띠 mu_s 0.30": [seg(*s) for s in segs],
           "띠 없음(RX-11 롤러 뒤, mu_s 0)": [seg(*s, mus=0.0) for s in segs]}
    return res


# ---------------- 설계 명령 ----------------
X0, Y0 = PARK


def box(name, xa, xb, ya, yb, za, zb, op="new", targets=None):
    p = {"length": xb - xa, "width": yb - ya, "height": zb - za, "corner": [round(X0 + xa, 4), round(Y0 + ya, 4), za], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = targets
    return {"command": "solid.box", "params": p}


def stage_bodies():
    return [box("MAT_W", -hx, hx, -hy, hy, 0, T),
            box(None, -hx - 1.0, XN, -nw, nw, -1, T + 1, op="cut", targets=["MAT_W"])]


def comp(name):
    return {"command": "component.create", "params": {"name": name, "parent": "root", "activate": False}}


def jc(nm, typ, a, b, pt, z, lim):
    return {"command": "joint.create", "params": {
        "type": typ, "name": nm, "flip": True, "limits": [lim], "quiet": True,
        "a": {"occurrence": a, "point": pt, "z": z}, "b": {"occurrence": b, "point": pt, "z": z}}}


def stage_joints():
    cp = [X0, Y0, 0]
    c = [comp(n) for n in ("WP_W_X", "WP_W_Y", "WP_MAT_W")]
    c += [{"command": "component.move_bodies", "params": {"bodies": ["MAT_W"], "component": "WP_MAT_W"}},
          jc("J_WP_W_X", "slider", "U1_FRAME:1", "WP_W_X:1", cp, [1, 0, 0], [-3000, 3000]),
          jc("J_WP_W_Y", "slider", "WP_W_X:1", "WP_W_Y:1", cp, [0, 1, 0], [-3000, 3000]),
          jc("J_WP_W_ROT", "revolute", "WP_W_Y:1", "WP_MAT_W:1", cp, [0, 0, 1], [-360, 720])]
    return c


def main():
    P, split = cycle_w()
    wheel_rot(P)
    N = len(P.poses) - 1
    p1, p2 = P.poses[:split + 1], P.poses[split:]
    k1, k2 = keys_for(p1), keys_for(p2)
    st1 = {"command": "motion.study", "params": {"name": "CYCLE_W1", "steps": len(p1) - 1, "keys": k1}}
    st2 = {"command": "motion.study", "params": {"name": "CYCLE_W2", "steps": len(p2) - 1, "keys": k2}}
    best, rows, u4_off, u5_off, u5_could = analyse(P.poses, split)
    # 다른 연구: 지금 키 통째 + J_WP_W_* 0 (motion.study keys는 통째 갈아끼움, F01-C1). 기존 키 값은 그대로.
    ml = json.load(open(os.path.join(HERE, "motion_list_before.json"), encoding="utf-8"))
    others, same = [], True
    for s in ml["studies"]:
        ks = [{"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]} for k in s["keys"]]
        n0 = len(ks)
        have = {k["joint"] for k in ks}
        for j in WP_NEW:
            if j not in have:
                ks.append({"joint": j, "points": [[0, 0], [s["steps"], 0]]})
        same = same and ks[:n0] == [{"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]} for k in s["keys"]]
        others.append({"command": "motion.study", "params": {"study": s["name"], "steps": s["steps"], "keys": ks}})
    ph = phases(p1) + [["— CYCLE_W2 —", 0, 0]] + phases(p2)
    holds = {z["ph"]: (i if i <= split else i - split) for i, z in enumerate(P.poses) if "정지·먼 쪽 바퀴" in z["ph"]}
    info = {"steps_total": N, "split_pose": split, "steps_W1": len(p1) - 1, "steps_W2": len(p2) - 1, "phases": ph, "holds": holds,
            "u4_down_but_contact_off_mat": u4_off, "u5_down_but_contact_off_mat": u5_off,
            "u5_lifted_though_on_mat_steps": [u5_could[0], u5_could[-1], len(u5_could)] if u5_could else [],
            "wheel_total_deg": {"U4": round(P.poses[-1]["rn"], 2), "U5": round(P.poses[-1]["rf"], 2)},
            "split_pose_values": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.poses[split].items() if k != "pt"},
            "other_studies_existing_keys_unchanged": same,
            "poses": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in z.items() if k != "pt"} for z in P.poses]}
    for nm, c in (("stage_1_bodies", stage_bodies()), ("stage_2_joints", stage_joints())):
        json.dump(c, open(os.path.join(HERE, nm + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump([st1], open(os.path.join(HERE, "study_CYCLE_W1.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump([st2], open(os.path.join(HERE, "study_CYCLE_W2.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(others, open(os.path.join(HERE, "study_others.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(info, open(os.path.join(HERE, "cycle_w.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    gaps = obstacle_gap(P.poses, split)
    for k, v in gaps.items():
        print("gap", k, v)
    env = {"obstacle_gap": gaps, "_note": "평면 강체 계산(자세 점마다, 회전 1°·이송 25/5 mm). 받침 정의는 측정부 rx12_common.py", "max": C.pack(best),
           "phase_max": phase_max(rows), "rows": rows}
    json.dump(env, open(os.path.join(HERE, "envelope_w.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hc = handcalc()
    json.dump(hc, open(os.path.join(HERE, "handcalc_w.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    area = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in RECTS)
    print("steps", N, "W1", len(p1) - 1, "W2", len(p2) - 1, "split pose", split, "area", area, "vol", area * T)
    print("holds", holds)
    print("u4 off", u4_off[:20], len(u4_off), "u5 off", u5_off[:20], len(u5_off), "u5 could", info["u5_lifted_though_on_mat_steps"])
    print("others same", same, "wheel", info["wheel_total_deg"])
    for k, v in C.pack(best).items():
        print(k, v["value"], "|", v["at"])
    print("study bytes", [os.path.getsize(os.path.join(HERE, f)) for f in ("study_CYCLE_W1.json", "study_CYCLE_W2.json", "study_others.json")])
    for s in hc["띠 mu_s 0.30"] + hc["띠 없음(RX-11 롤러 뒤, mu_s 0)"]:
        print(s["seg"], "I", s["I"], "room", s["room"], "tmin", s["t_min_SF1_s"])
    print("mass", hc["mass_kg"])


if __name__ == "__main__":
    main()
