# -*- coding: utf-8 -*-
"""RX-17 생성기(tools/gen_rx17.py — 설계 초안 tools/out/mech_RX-17/design/rx17_design.py에서 출력 폴더·경로만 고침, 계산·키 그대로)
출력: tools/out/mech_RX-17/model/, 입력 기본: 같은 폴더 motion_list_before.json(적용 직전 문서의 motion.list)
원래 머리말 — RX-17 설계 초안(생성기) — 시험 매트 '운전석(홈 + 좁은 띠)' WP_P(MAT_P), 모형 조인트 J_WP_P_X·Y·ROT, 연구 CYCLE_P1·CYCLE_P2.

python -X utf8 -B tools/out/mech_RX-17/design/rx17_design.py [motion_list.json]
  -> 같은 폴더에 stage_1_bodies.json, stage_2_joints.json, study_CYCLE_P1.json, study_CYCLE_P2.json, study_others.json,
     cycle_p.json(자세·구간·바퀴 키), envelope_p_design.json(넓이·겹침), contact_table_p.json(구간별 두 바퀴 접지 표), check_poses_p.json
  입력: motion.list 원본(기본 tools/out/mech_RX-17/motion_list.json — 모델링부는 적용 직전 문서 것으로 다시 받는다),
        tools/out/mech_RX-12/rx12_common.py(받침 영역·넓이 도구)
모델링부는 이 파일을 tools/gen_rx17.py로 옮겨 쓴다(출력 폴더만 tools/out/mech_RX-17/model/로).

좌표·식은 tools/gen_rx12.py와 같다: 매트 중심 c = -R(th) p (p = 바늘 밑 땀 점, 매트 좌표), 조인트 X = cx - PARK_x, Y = cy - PARK_y, ROT = th.
th = -90 - beta (beta = 땀 진행 방향의 매트 좌표 각) — 진행이 세계 -Y, 몸통이 -X.
형상은 tools/out/binder_test/bindtest.py mat_P + rounded(.., 30)과 같다(C-53 근거, 측정부 envelope_p.py 변형 A).
  그림 좌표(x 0~520, y 0~890): 몸통 y 0~720, 그 위 띠 x 0~60, 홈 입구 x 60~90 -> 바닥 폭 25(x 62.5~87.5) 반원 R 12.5 중심 (75, 732.5),
  건너편 몸통 x 90~520. 볼록 R 30: (0,0)·(520,0)·(520,890)·홈 입구 건너편 (90,890). 띠 끝 두 모서리는 각짐(변 60에 R 30 둘이 안 들어감).
  매트 좌표 = 그림 좌표 - (260, 445).
임시값: 위 치수 전부(D-01·D-02·D-03·D-213), 두께 10(D-04), e 6.5(D-78·D-144), d1 100(C-37), d2 440(D-152), 로딩 -Y 300(D-106),
        바퀴 접지 상자 X ±12.5(서명 바퀴 폭 25) · Y ±10(가정, D-93).
"""
import json, math, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
TOOLS_OUT = os.path.join(TOOLS, "out")
HERE = os.path.join(TOOLS_OUT, "mech_RX-17", "model")      # 출력 폴더(모델링부)
os.makedirs(HERE, exist_ok=True)
sys.path.insert(0, os.path.join(TOOLS_OUT, "mech_RX-12"))
import rx12_common as C  # noqa: E402

T = 10.0
WD, LB, TW, TL, MOUTH, BW, RC = 520.0, 720.0, 60.0, 170.0, 30.0, 25.0, 30.0
RB = BW / 2
TOP = LB + TL                       # 890
OFF = (WD / 2, TOP / 2)             # 그림 좌표 -> 매트 좌표
E = 6.5
PARK = (-(WD / 2 - E), -300.0)      # (-253.5, -300)
START_C = (PARK[0], 0.0)
STEP_FEED, STEP_FINE = 25.0, 5.0
PR_UP, ND_DN = 20.0, -30.0
U4_UP, U4_DN = 13.006, 0.0
SP_UP, SP_DN = 4.5, -0.4
SH_PARK = -60.0
LIFT_UP, LIFT_DN, FLOAT_MAT = 30.0, -10.0, 10.0
D1, WR = 100.0, 60.0
D2_PARK, D2_P = 1800.0, 440.0
FX_P = D2_PARK - D2_P               # J_U5_X 1360
OVERLAP = 30.0
HALF_X, HALF_Y = 12.5, 10.0         # 바퀴 접지 상자
MIN_RUN4, MIN_RUN5 = 8, 10          # 이보다 짧게 내려 있는 구간은 내리지 않는다(바퀴 오르내림 한 번 안 되는 길이)

WP_OLD = ["J_WP_%s_%s" % (k, ax) for k in "LSGV" for ax in ("X", "Y", "ROT")]
WP_W = ["J_WP_W_X", "J_WP_W_Y", "J_WP_W_ROT"]
WP_NEW = ["J_WP_P_X", "J_WP_P_Y", "J_WP_P_ROT"]
ORDER = ["J_U3_PRESSER", "J_U3_NEEDLE", "J_U4_WHEEL_ROT", "J_U5_X", "J_U5_WHEEL_ROT"] + WP_OLD[:9] + \
        ["J_U4_PRESS", "J_U6_SHIFT", "J_U7_CST_X", "J_U7_CST_Y", "J_U7_CUT", "J_U7_TUCK", "J_U7_FEED", "J_U7_LATCH",
         "J_U5_LIFT", "J_U5_FLOAT"] + WP_OLD[9:] + ["J_U6_PRESS"] + WP_W + WP_NEW
COL = {"J_U3_PRESSER": "pr", "J_U3_NEEDLE": "nd", "J_U4_PRESS": "np", "J_U4_WHEEL_ROT": "rn", "J_U5_X": "fx",
       "J_U5_LIFT": "fl", "J_U5_FLOAT": "fz", "J_U5_WHEEL_ROT": "rf", "J_U6_SHIFT": "sh", "J_U6_PRESS": "sp"}


def L(p):
    """그림 좌표 -> 매트 좌표"""
    return (p[0] - OFF[0], p[1] - OFF[1])


def rot(th, v):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def center(p, th):
    q = rot(th, p)
    return (-q[0], -q[1])


def unit(a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


# ---------------- 형상(그림 좌표) ----------------
# 홈 벽(기울기 0.909도)
W1A, W1B = (TW, TOP), (TW + (MOUTH - BW) / 2, LB + RB)                 # 띠 홈 쪽 벽 (60,890) -> (62.5,732.5)
W2A, W2B = (TW + MOUTH - (MOUTH - BW) / 2, LB + RB), (TW + MOUTH, TOP)  # 건너편 벽 (87.5,732.5) -> (90,890)
SC = (TW + MOUTH / 2, LB + RB)                                        # 홈 바닥 반원 중심 (75, 732.5)
d2w = unit(W2A, W2B)
n2w = (d2w[1], -d2w[0])                                               # 건너편 벽의 재료 쪽(+x)
_t = (TOP - RC - W2A[1] + RC * (-n2w[1])) / d2w[1]
FC = (W2A[0] + _t * d2w[0] + RC * n2w[0], TOP - RC)                   # 홈 입구 건너편 R30 중심 (119.53, 860)
FA0 = math.degrees(math.atan2(-n2w[1], -n2w[0]))                      # 벽 쪽 접점 각 179.09
d1w = unit(W1A, W1B)
n1w = (-d1w[1], d1w[0])                                               # 띠 홈 쪽 벽의 재료 쪽(-x)  (d=(0.0159,-0.9999) -> n=(-0.9999,-0.0159))
if n1w[0] > 0:
    n1w = (-n1w[0], -n1w[1])


def arc_pts(c, r, a0, a1, step=2.0):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def outline():
    """외곽(그림 좌표, 시계 방향, 시작 (520, 445))."""
    o = [(WD, TOP / 2), (WD, RC)]
    o += arc_pts((WD - RC, RC), RC, 0, -90)[1:]
    o += [(RC, 0)]
    o += arc_pts((RC, RC), RC, -90, -180)[1:]
    o += [(0, TOP), (TW, TOP), W1B]
    o += arc_pts(SC, RB, 180, 360)[1:]
    fa = (FC[0] + RC * math.cos(math.radians(FA0)), FC[1] + RC * math.sin(math.radians(FA0)))
    o += [fa]
    o += arc_pts(FC, RC, FA0, 90)[1:]
    o += [(WD - RC, TOP)]
    o += arc_pts((WD - RC, TOP - RC), RC, 90, 0)[1:]
    return o


OUT_PIC = outline()
OUTLINE = [L(p) for p in OUT_PIC]
RECTS = [(-260.0, 260.0, -445.0, 275.0), (-260.0, -200.0, 275.0, 445.0), (-170.0, 260.0, 275.0, 445.0)]   # 넓이용(홈 = 곧은 30, 모서리 R 무시)


def poly_area(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def area_exact():
    slot = (MOUTH + BW) / 2 * (TOP - (LB + RB)) + math.pi * RB * RB / 2
    c90 = (1 - math.pi / 4) * RC * RC
    phi = math.radians(FA0 - 90.0)
    cf = RC * RC * (math.tan(phi / 2) - phi / 2)
    return WD * TOP - slot - 3 * c90 - cf


def inside(p):
    """매트 좌표 점이 매트 안인가(외곽 다각형, 호 2도 조각)."""
    x, y = p; c = False
    n = len(OUTLINE)
    for i in range(n):
        x0, y0 = OUTLINE[i]; x1, y1 = OUTLINE[(i + 1) % n]
        if (y0 <= y < y1) or (y1 <= y < y0):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
    return c


# ---------------- 땀 선(그림 좌표, 외곽 안쪽 e) ----------------
SV_TIP_OUT = (E, TOP - E)                                             # 띠 끝 바깥 모서리 땀 점 (6.5, 883.5)
_t1 = (E + E * n1w[1]) / (-d1w[1])
SV_TIP_IN = (W1A[0] + _t1 * d1w[0] + E * n1w[0], TOP - E)             # 띠 끝 홈 쪽 모서리 땀 점 (53.60, 883.5)
RS_B = RB + E                                                         # 홈 바닥 땀 선 반지름 19
RS_C = RC - E                                                         # 볼록 R30 땀 선 반지름 23.5
SA_IN = (SC[0] - RS_B, SC[1])                                         # (56, 732.5)
SA_OUT = (SC[0] + RS_B, SC[1])                                        # (94, 732.5)
SF_IN = (FC[0] + RS_C * math.cos(math.radians(FA0)), FC[1] + RS_C * math.sin(math.radians(FA0)))   # (96.03, 860.37)


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

    def short(self, ph, seg=None, **tgt):
        l = self.last
        seg = l.get("seg", "") if seg is None else seg
        self.add(ph=ph, seg=seg, **{j: (l[j] + v) / 2 for j, v in tgt.items()})
        self.add(ph=ph, seg=seg, **tgt)

    def move_c(self, c1, step, ph):
        l = self.last
        Ln = math.hypot(c1[0] - l["cx"], c1[1] - l["cy"])
        n = max(1, math.ceil(Ln / step - 1e-9))
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

    def th_for(self, beta):
        """th = -90 - beta 를 지금 th에 가장 가까운 값으로(이어지게)."""
        th = -90.0 - beta
        cur = self.last.get("th", 0.0)
        while th - cur > 180.0:
            th -= 360.0
        while th - cur < -180.0:
            th += 360.0
        return th

    def sew_line(self, a, b, ph, step, seg):
        """그림 좌표 a -> b 봉제(곧은 변). step 간격."""
        beta = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        th = self.th_for(beta)
        Ln = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, math.ceil(Ln / step - 1e-9))
        for i in range(1, n + 1):
            f = i / n
            p = L((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p, seg=seg)

    def sew_arc(self, ctr, r, a0, a1, ph, seg):
        """땀 점이 호(중심 ctr, 반지름 r, 극각 a0 -> a1)를 따라가며 매트가 같이 돈다. 1도 간격."""
        n = max(1, math.ceil(abs(a1 - a0) - 1e-9))
        sgn = 1.0 if a1 > a0 else -1.0
        for i in range(1, n + 1):
            a = a0 + (a1 - a0) * i / n
            p = L((ctr[0] + r * math.cos(math.radians(a)), ctr[1] + r * math.sin(math.radians(a))))
            th = self.th_for(a + 90.0 * sgn)
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p, seg=seg)

    def turn(self, p_pic, beta1, ph, seg):
        """바늘점 둘레 피벗 1도 간격: 지금 th -> 다음 변 방향."""
        p = L(p_pic)
        th0 = self.last["th"]
        th1 = self.th_for(beta1)
        n = max(1, math.ceil(abs(th1 - th0) - 1e-9))
        for i in range(1, n + 1):
            th = th0 + (th1 - th0) * i / n
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p, seg=seg)

    def pivot(self, p_pic, beta1, name, seg):
        self.short("④ %s 정지·바늘 꽂음·슈 들기(노루발 낮은 누름 C-39)" % name, nd=ND_DN, sp=SP_UP, seg=seg)
        self.turn(p_pic, beta1, "④ %s 바늘 중심 회전" % name, seg)
        self.short("④ %s 바늘 빼기·슈 내림" % name, nd=0.0, sp=SP_DN, seg=seg)


def cycle_p():
    P = Path()
    P.add(cx=PARK[0], cy=PARK[1], th=0.0, pr=PR_UP, nd=0.0, np=U4_UP, fx=0.0, fl=LIFT_UP, fz=0.0, sh=SH_PARK, sp=SP_UP,
          ph="① 대기·로딩(매트를 올린 자리)", seg="로딩")
    P.move_c(START_C, STEP_FEED, "① 작업자가 가장자리를 노루발 표시에 맞춤")
    P.short("② 노루발 내림·센서 슈 자리로", pr=0.0, sh=0.0)
    P.add(ph="② 슈 누름·바늘 옆 바퀴 내림", sp=(SP_UP + SP_DN) / 2)
    P.add(ph="② 슈 누름·바늘 옆 바퀴 내림", sp=SP_DN)
    P.carriage(FX_P, "② 먼 쪽 대차 d2 440으로(J_U5_X 1360, 바퀴는 든 채)")
    P.add(ph="② 먼 쪽 바퀴 내림(밑에 매트가 있을 때)", seg="내림")
    i_s = len(P.poses) - 1                       # 이 자세부터 바퀴 키를 접지 계산으로 정한다(대차가 선 뒤)
    # ③ 봉제 — 시계 방향
    P.sew_line((WD - E, TOP / 2), (WD - E, RC), "③ 몸통 오른 변 앞 반(시작 변)", STEP_FEED, "몸통 오른 변")
    P.sew_arc((WD - RC, RC), RS_C, 0.0, -90.0, "③ 둥근 모서리 R30 A (520,0) 돌며 봉제", "모서리 R30 A")
    P.sew_line((WD - RC, E), (RC, E), "③ 몸통 아랫변", STEP_FEED, "몸통 아랫변")
    P.sew_arc((RC, RC), RS_C, -90.0, -180.0, "③ 둥근 모서리 R30 B (0,0) 돌며 봉제", "모서리 R30 B")
    P.sew_line((E, RC), (E, LB - 50.0), "③ 몸통 왼 변", STEP_FEED, "몸통 왼 변")
    P.sew_line((E, LB - 50.0), (E, LB), "③ 몸통 왼 변 끝 50(5 mm 간격)", STEP_FINE, "몸통 왼 변")
    P.sew_line((E, LB), SV_TIP_OUT, "③ 띠 바깥 변", STEP_FINE, "띠 바깥 변")
    P.pivot(SV_TIP_OUT, 0.0, "띠 끝 바깥 모서리(볼록, 각짐)", "회전: 띠 끝 바깥 모서리")
    P.sew_line(SV_TIP_OUT, SV_TIP_IN, "③ 띠 끝", STEP_FINE, "띠 끝")
    split = len(P.poses) - 1                     # 연구 나눔 점 = 띠 끝을 다 박은 자세(홈 입구 회전 앞)
    b_w1 = math.degrees(math.atan2(SA_IN[1] - SV_TIP_IN[1], SA_IN[0] - SV_TIP_IN[0]))
    P.pivot(SV_TIP_IN, b_w1, "홈 입구 = 띠 끝 홈 쪽 모서리(볼록, 각짐)", "회전: 홈 입구(띠 끝 홈 쪽 모서리)")
    P.sew_line(SV_TIP_IN, SA_IN, "③ 띠의 홈 쪽 벽", STEP_FINE, "띠 홈 쪽 벽")
    P.short("④ 홈 바닥 정지·바늘 꽂음·슈 들기(땀마다 멈춰 돎, 0-8-2 ②)", nd=ND_DN, sp=SP_UP, seg="홈 바닥")
    P.sew_arc(SC, RS_B, 180.0, 360.0, "④ 홈 바닥(R 12.5, 땀 선 R 19) 땀마다 멈춰 돎", "홈 바닥")
    P.short("④ 홈 바닥 끝·바늘 빼기·슈 내림", nd=0.0, sp=SP_DN, seg="홈 바닥")
    P.sew_line(SA_OUT, SF_IN, "③ 홈 건너편 벽", STEP_FINE, "홈 건너편 벽")
    P.sew_arc(FC, RS_C, FA0, 90.0, "③ 둥근 모서리 R30 홈 입구 건너편 (90,890) 돌며 봉제", "모서리 R30 홈 입구 건너편")
    P.sew_line((FC[0], TOP - E), (FC[0] + 50.0, TOP - E), "③ 홈 건너 윗변 처음 50(5 mm 간격)", STEP_FINE, "홈 건너 윗변")
    P.sew_line((FC[0] + 50.0, TOP - E), (WD - RC, TOP - E), "③ 홈 건너 윗변", STEP_FEED, "홈 건너 윗변")
    P.sew_arc((WD - RC, TOP - RC), RS_C, 90.0, 0.0, "③ 둥근 모서리 R30 C (520,890) 돌며 봉제", "모서리 R30 C")
    P.sew_line((WD - E, TOP - RC), (WD - E, TOP / 2 - OVERLAP), "③⑤ 몸통 오른 변 뒤 반 + 시작부 위 겹쳐 박기 30", STEP_FEED, "몸통 오른 변")
    i_e = len(P.poses) - 1
    P.add(ph="⑥ 노루발 들기·먼 쪽 바퀴 들기", pr=PR_UP / 2, seg="들기")
    P.add(ph="⑥ 노루발 들기·슈 들기", pr=PR_UP, sp=SP_UP)
    P.add(ph="⑥ 바늘 옆 바퀴 들기·센서 슈 대기", sh=SH_PARK / 2)
    P.add(ph="⑥ 바늘 옆 바퀴 들기·센서 슈 대기", sh=SH_PARK)
    P.carriage(0.0, "⑥ 먼 쪽 대차 대기로(J_U5_X 0)")
    l = P.last
    P.move_c((l["cx"], l["cy"] - 300.0), STEP_FEED, "⑥ 배출(-Y 300, D-106)")
    for z in P.poses:
        z.setdefault("seg", "")
    return P, split, i_s, i_e


# ---------------- 평면 판정 ----------------
def world(z, q):
    r = rot(z["th"], q)
    return (z["cx"] + r[0], z["cy"] + r[1])


def to_mat(z, w):
    return rot(-z["th"], (w[0] - z["cx"], w[1] - z["cy"]))


def frac(z, d, nx=5, ny=5):
    """바퀴 접지 상자(X -d±12.5, Y ±10)가 매트 위에 있는 비율."""
    k = 0
    for i in range(nx):
        for j in range(ny):
            w = (-d - HALF_X + 2 * HALF_X * (i + .5) / nx, -HALF_Y + 2 * HALF_Y * (j + .5) / ny)
            if inside(to_mat(z, w)):
                k += 1
    return k / (nx * ny)


def full(z, d):
    pts = [(-d + sx * HALF_X, sy * HALF_Y) for sx in (-1, -.5, 0, .5, 1) for sy in (-1, 0, 1)]
    return all(inside(to_mat(z, w)) for w in pts)


def wheel_keys(P, i_s, i_e):
    """접지 계산으로 바퀴 오르내림 키를 정한다. 내림 = 그 자세와 앞뒤 자세에서 접지 상자가 다 매트 위(가장자리를 내린 채 넘지 않게),
    MIN_RUN보다 짧은 내림 구간은 버린다."""
    N = len(P.poses)
    for key, d_of, mn in (("np", lambda z: D1, MIN_RUN4), ("fl", lambda z: D2_PARK - z["fx"], MIN_RUN5)):
        on = [i_s <= i <= i_e and full(P.poses[i], d_of(P.poses[i])) for i in range(N)]
        dn = [on[i] and (i > 0 and on[i - 1] or i == i_s) and (i + 1 < N and on[i + 1] or i == i_e) for i in range(N)]
        if key == "np":
            # 바늘 옆 바퀴는 '② 슈 누름' 둘째 자세에서 내려 대차가 가는 동안에도 내려 있다(RX-12와 같다)
            j0 = next(i for i, z in enumerate(P.poses) if z["ph"] == "② 슈 누름·바늘 옆 바퀴 내림" and z["sp"] == SP_DN)
            if all(full(P.poses[j], D1) for j in range(j0 - 1, i_s + 1)):
                for j in range(j0, i_s):
                    dn[j] = True
        i = 0
        while i < N:
            if dn[i]:
                j = i
                while j + 1 < N and dn[j + 1]:
                    j += 1
                if j - i + 1 < mn:
                    for k in range(i, j + 1):
                        dn[k] = False
                i = j + 1
            else:
                i += 1
        dn[i_e] = dn[i_e] and dn[i_e - 1]
        if key == "np" and dn[i_e]:
            for j in range(i_e + 1, i_e + 4):    # ⑥ 넷째 자세('바늘 옆 바퀴 들기')에서 든다(RX-12와 같다)
                dn[j] = True
        for i, z in enumerate(P.poses):
            if key == "np":
                z["np"] = U4_DN if dn[i] else U4_UP
                z["on4"] = full(z, D1)
            else:
                z["fl"] = LIFT_DN if dn[i] else LIFT_UP
                z["fz"] = FLOAT_MAT if dn[i] else 0.0
                z["on5"] = full(z, d_of(z))


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
        elif j == "J_WP_P_X":
            pts = [[i, round(z["cx"] - PARK[0], 4)] for i, z in enumerate(poses)]
        elif j == "J_WP_P_Y":
            pts = [[i, round(z["cy"] - PARK[1], 4)] for i, z in enumerate(poses)]
        elif j == "J_WP_P_ROT":
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


def label(i, split):
    return "P1 %d" % i if i <= split else "P2 %d" % (i - split)


D1S = (45.0, 60.0, 100.0)
D2S = [420.0 + 20 * i for i in range(70)]


def analyse(P, split):
    best, rows = {}, []
    for i, z in enumerate(P.poses):
        polys = [[world(z, q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))] for x0, x1, y0, y1 in RECTS]
        verts = [world(z, q) for q in OUTLINE]
        m = C.metrics(polys, verts)
        C.update(best, m, "%s %s ROT %.1f" % (label(i, split), z["ph"], z["th"]))
        u4 = {d: frac(z, d) for d in D1S}
        u5 = frac(z, D2_P)
        u5b = max(frac(z, d, 3, 3) for d in D2S)
        rows.append({"i": i, "step": label(i, split), "ph": z["ph"], "seg": z["seg"], "th": round(z["th"], 2), "xmax": round(m["xmax"], 1),
                     "A_+X": round(m["A_+X(X>6.5)"]), "A_볼밖": round(m["A_볼 받침 밖"]), "A_패널밖": round(m["A_패널 밖"]),
                     "A_포켓": round(m["A_포켓(X>400,Y<-300)"]), "A_X>900": round(m["A_X>900"]),
                     "u4_100": u4[100.0], "u4_60": u4[60.0], "u4_45": u4[45.0], "u5_440": u5, "u5_best": u5b,
                     "u4_down": z["np"] < 1.0, "u5_down": z["fl"] == LIFT_DN})
    return best, rows


def seg_table(rows):
    out, cur = [], None
    for r in rows:
        if not r["seg"] or r["seg"] in ("로딩", "내림", "들기"):
            cur = None
            continue
        if cur is None or cur["구간"] != r["seg"]:
            cur = {"구간": r["seg"], "단계": [r["step"], r["step"]], "자세": 0, "ROT": [r["th"], r["th"]], "X 최대": -1e9, "+X 넓이": 0, "볼 받침 밖": 0, "포켓 위": 0,
                   "_u4": [], "_u460": [], "_u445": [], "_u5": [], "_u5b": [], "U4 내림 자세": 0, "U5 내림 자세": 0,
                   "두 바퀴 다 반 미만(d1 100, d2 440)": 0, "두 바퀴 다 반 미만(d1 100, 가장 좋은 d2)": 0, "두 바퀴 다 반 미만(d1 45, 가장 좋은 d2)": 0, "연구에서 두 바퀴 다 들림": 0}
            out.append(cur)
        cur["단계"][1] = r["step"]; cur["자세"] += 1
        cur["ROT"] = [min(cur["ROT"][0], r["th"]), max(cur["ROT"][1], r["th"])]
        cur["X 최대"] = max(cur["X 최대"], r["xmax"]); cur["+X 넓이"] = max(cur["+X 넓이"], r["A_+X"])
        cur["볼 받침 밖"] = max(cur["볼 받침 밖"], r["A_볼밖"]); cur["포켓 위"] = max(cur["포켓 위"], r["A_포켓"])
        cur["_u4"].append(r["u4_100"]); cur["_u460"].append(r["u4_60"]); cur["_u445"].append(r["u4_45"]); cur["_u5"].append(r["u5_440"]); cur["_u5b"].append(r["u5_best"])
        cur["U4 내림 자세"] += r["u4_down"]; cur["U5 내림 자세"] += r["u5_down"]
        cur["두 바퀴 다 반 미만(d1 100, d2 440)"] += (r["u4_100"] < 0.5 and r["u5_440"] < 0.5)
        cur["두 바퀴 다 반 미만(d1 100, 가장 좋은 d2)"] += (r["u4_100"] < 0.5 and r["u5_best"] < 0.5)
        cur["두 바퀴 다 반 미만(d1 45, 가장 좋은 d2)"] += (r["u4_45"] < 0.5 and r["u5_best"] < 0.5)
        cur["연구에서 두 바퀴 다 들림"] += (not r["u4_down"] and not r["u5_down"])
    for c in out:
        for k, nm in (("_u4", "U4 접지 d1 100 [최소, 최대, 평균]"), ("_u460", "U4 접지 d1 60"), ("_u445", "U4 접지 d1 45"),
                      ("_u5", "U5 접지 d2 440"), ("_u5b", "U5 접지 가장 좋은 d2")):
            v = c.pop(k)
            c[nm] = [round(min(v), 2), round(max(v), 2), round(sum(v) / len(v), 2)]
    return out


def obstacle_gap(P, split):
    pts = []
    n = len(OUTLINE)
    for i in range(n):
        a, b = OUTLINE[i], OUTLINE[(i + 1) % n]
        Ln = math.hypot(b[0] - a[0], b[1] - a[1]); k = max(1, int(Ln / 5))
        pts += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    best = {}
    for i, z in enumerate(P.poses):
        W = [world(z, q) for q in pts]
        for name, (x0, x1, y0, y1) in C.OBST.items():
            d = min(math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) for x, y in W)
            if name not in best or d < best[name][0]:
                best[name] = (d, i, z["ph"], z["th"])
    return {k: dict(gap=round(v[0], 1), step=label(v[1], split), ph=v[2], rot=round(v[3], 1)) for k, v in best.items()}


def handcalc():
    """회전력 손계산(참고, tools/gen_rx12.py handcalc()와 같은 식·값). 띠 없음(RX-11 롤러 뒤, mu_s 0)."""
    g, rho = 9.81, 6.0
    mu_w, d1, d2 = 0.4, 0.100, D2_P / 1000
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
    T_ex = 0.3 * W_disk * 0.04 + 2 * 0.005 * (0.1 / 0.075) + 0.096
    I_disk = 0.5 * (583642e-9 * 2680) * 0.125 ** 2 * (0.1 / 0.075) ** 2

    def seg(name, th, w, piv, cr=0.02):
        I, Rg = about(L(piv))
        have = (mu_w * F4 * d1 if "U4" in w else 0.0) + (mu_w * (F5 - f5) * d2 if "U5" in w else 0.0)
        room = have - cr * Rg - T_ex
        Ie = I + I_disk
        tmin = math.sqrt(4 * math.radians(th) * Ie / room) if room > 0 else None
        return dict(seg=name, theta_deg=th, wheels=w, I=round(I, 3), T_roll=round(cr * Rg, 3), T_extra=round(T_ex, 3),
                    have=round(have, 3), room=round(room, 3), t_min_SF1_s=None if tmin is None else round(tmin, 2))
    return {"_식": "tools/gen_rx12.py handcalc()와 같음(면밀도 6 kg/m2 D-145, 바퀴 mu 0.4 D-95, U4 40 N·d1 0.1, U5 40 N·d2 0.44, 볼 구름 0.02 D-96, 띠 항 없음). 정지->정지 삼각 속도",
            "mass_kg": round(mass, 3),
            "seg": [seg("둥근 모서리 A (520,0) 90도, U4+U5", 90, ["U4", "U5"], (WD - RC, RC)),
                    seg("둥근 모서리 B (0,0) 90도, U4+U5", 90, ["U4", "U5"], (RC, RC)),
                    seg("띠 끝 바깥 모서리 90도, U4+U5", 90, ["U4", "U5"], SV_TIP_OUT),
                    seg("띠 끝 바깥 모서리 90도, U4 혼자", 90, ["U4"], SV_TIP_OUT),
                    seg("홈 입구(띠 끝 홈 쪽) 89도, U4 혼자(앞 구간)", 89, ["U4"], SV_TIP_IN),
                    seg("홈 입구(띠 끝 홈 쪽) 89도, 바퀴 없음(뒤 구간)", 89, [], SV_TIP_IN),
                    seg("홈 바닥 178도, U4 혼자", 178, ["U4"], SC),
                    seg("둥근 모서리 C (520,890) 90도, U4+U5", 90, ["U4", "U5"], (WD - RC, TOP - RC))]}


# ---------------- 설계 명령 ----------------
X0, Y0 = PARK[0] - OFF[0], PARK[1] - OFF[1]      # 그림 좌표 원점의 세계 자리(REST) = (-513.5, -745)


def Wd(p):
    return [round(X0 + p[0], 4), round(Y0 + p[1], 4)]


def stage_bodies():
    k = (MOUTH - BW) / 2 / (TOP - (LB + RB))      # 벽 기울기 dx/dy
    trap = [(TW - k * 1.0, TOP + 1.0), (TW + MOUTH + k * 1.0, TOP + 1.0), W2A, W1B]
    c = [{"command": "solid.box", "params": {"length": WD, "width": TOP, "height": T, "corner": [X0, Y0, 0], "operation": "new", "body_name": "MAT_P"}},
         {"command": "sketch.create", "params": {"plane": {"origin": [0, 0, -1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_MAT_P_SLOT"}},
         {"command": "sketch.line", "params": {"points": [Wd(p) for p in trap], "closed": True}},
         {"command": "sketch.finish", "params": {}},
         {"command": "solid.extrude", "params": {"sketch": "SK_MAT_P_SLOT", "distance": T + 2, "operation": "cut", "targets": ["MAT_P"]}},
         {"command": "solid.cylinder", "params": {"radius": RB, "height": T + 2, "base": Wd(SC) + [-1], "axis": [0, 0, 1], "operation": "cut", "targets": ["MAT_P"]}},
         {"command": "solid.fillet", "params": {"radius": RC,
                                               "edges": [Wd((0, 0)) + [T / 2], Wd((WD, 0)) + [T / 2], Wd((WD, TOP)) + [T / 2], Wd((TW + MOUTH, TOP)) + [T / 2]]}}]
    return c


def comp(name):
    return {"command": "component.create", "params": {"name": name, "parent": "root", "activate": False}}


def jc(nm, typ, a, b, pt, z, lim):
    return {"command": "joint.create", "params": {
        "type": typ, "name": nm, "flip": True, "limits": [lim], "quiet": True,
        "a": {"occurrence": a, "point": pt, "z": z}, "b": {"occurrence": b, "point": pt, "z": z}}}


def stage_joints():
    cp = [PARK[0], PARK[1], 0]
    c = [comp(n) for n in ("WP_P_X", "WP_P_Y", "WP_MAT_P")]
    c += [{"command": "component.move_bodies", "params": {"bodies": ["MAT_P"], "component": "WP_MAT_P"}},
          jc("J_WP_P_X", "slider", "U1_FRAME:1", "WP_P_X:1", cp, [1, 0, 0], [-3000, 3000]),
          jc("J_WP_P_Y", "slider", "WP_P_X:1", "WP_P_Y:1", cp, [0, 1, 0], [-3000, 3000]),
          jc("J_WP_P_ROT", "revolute", "WP_P_Y:1", "WP_MAT_P:1", cp, [0, 0, 1], [-360, 720])]
    return c


def bbox(z):
    W = [world(z, q) for q in OUTLINE]
    return [round(min(p[0] for p in W), 1), round(max(p[0] for p in W), 1), round(min(p[1] for p in W), 1), round(max(p[1] for p in W), 1)]


def main():
    ml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "motion_list_before.json")
    P, split, i_s, i_e = cycle_p()
    wheel_keys(P, i_s, i_e)
    wheel_rot(P)
    N = len(P.poses) - 1
    p1, p2 = P.poses[:split + 1], P.poses[split:]
    k1, k2 = keys_for(p1), keys_for(p2)
    st1 = {"command": "motion.study", "params": {"name": "CYCLE_P1", "steps": len(p1) - 1, "keys": k1}}
    st2 = {"command": "motion.study", "params": {"name": "CYCLE_P2", "steps": len(p2) - 1, "keys": k2}}
    best, rows = analyse(P, split)
    ml = json.load(open(ml_path, encoding="utf-8"))
    others, same = [], True
    for s in ml["studies"]:
        if s["name"] in ("CYCLE_P1", "CYCLE_P2"):
            continue
        ks = [{"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]} for k in s["keys"]]
        n0 = len(ks)
        have = {k["joint"] for k in ks}
        for j in WP_NEW:
            if j not in have:
                ks.append({"joint": j, "points": [[0, 0], [s["steps"], 0]]})
        same = same and ks[:n0] == [{"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]} for k in s["keys"]]
        others.append({"command": "motion.study", "params": {"study": s["name"], "steps": s["steps"], "keys": ks}})
    segs = seg_table(rows)
    ph = phases(p1) + [["— CYCLE_P2 —", 0, 0]] + phases(p2)
    # 바퀴 키가 바뀌는 단계
    chg = []
    for i in range(1, len(P.poses)):
        a, b = P.poses[i - 1], P.poses[i]
        if (a["np"] < 1.0) != (b["np"] < 1.0):
            chg.append([label(i, split), "U4 " + ("내림" if b["np"] < 1.0 else "들기"), b["ph"], round(b["th"], 1)])
        if (a["fl"] == LIFT_DN) != (b["fl"] == LIFT_DN):
            chg.append([label(i, split), "U5 " + ("내림" if b["fl"] == LIFT_DN else "들기"), b["ph"], round(b["th"], 1)])
    area = area_exact()
    info = {"steps_total": N, "split_pose": split, "steps_P1": len(p1) - 1, "steps_P2": len(p2) - 1, "sew_window": [label(i_s, split), label(i_e, split)],
            "area_mm2": round(area, 2), "volume_mm3": round(area * T, 1), "outline_poly_area": round(poly_area(OUTLINE), 1),
            "geom": {"FC": [round(v, 4) for v in FC], "FA0": round(FA0, 4), "SV_TIP_OUT": SV_TIP_OUT, "SV_TIP_IN": [round(v, 4) for v in SV_TIP_IN],
                     "SA_IN": SA_IN, "SA_OUT": SA_OUT, "SF_IN": [round(v, 4) for v in SF_IN], "PARK": PARK, "pic_origin_world": [X0, Y0]},
            "phases": ph, "wheel_changes": chg,
            "wheel_total_deg": {"U4": round(P.poses[-1]["rn"], 2), "U5": round(P.poses[-1]["rf"], 2)},
            "split_pose_values": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.poses[split].items() if k != "pt"},
            "other_studies_existing_keys_unchanged": same, "other_studies": [s["params"]["study"] for s in others],
            "poses": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in z.items() if k != "pt"} for z in P.poses]}

    def dump(nm, obj, indent=None):
        json.dump(obj, open(os.path.join(HERE, nm), "w", encoding="utf-8"), ensure_ascii=False, indent=indent)
    dump("stage_1_bodies.json", stage_bodies(), 1)
    dump("stage_2_joints.json", stage_joints(), 1)
    dump("study_CYCLE_P1.json", [st1]); dump("study_CYCLE_P2.json", [st2]); dump("study_others.json", others)
    dump("cycle_p.json", info, 1)
    gaps = obstacle_gap(P, split)
    dump("envelope_p_design.json", {"_note": "평면 강체 계산(자세 점마다). 받침 정의 tools/out/mech_RX-12/rx12_common.py. 넓이는 사각 3조각(홈 = 곧은 30, 모서리 R 무시)",
                                    "obstacle_gap": gaps, "max": C.pack(best), "rows": rows}, 1)
    dump("contact_table_p.json", {"_note": "구간별 두 바퀴 접지(접지 상자 X -d±12.5 · Y ±10이 매트 위에 있는 비율 [최소, 최대, 평균]). d1 100 = 지금 기본 자리, 45·60 = RX-16 뒤 참고. U5 d2 440 = 연구 값",
                                  "segments": segs, "wheel_changes": chg}, 1)
    hc = handcalc()
    dump("handcalc_p.json", hc, 1)
    # 자기 점검 자세
    want = [0, i_s, split]
    for name in ("xmax", "xmin", "ymax", "ymin", "A_볼 받침 밖"):
        want.append(next(r["i"] for r in rows if label(r["i"], split) == best[name][1].split(" ROT")[0].split(" ")[0] + " " + best[name][1].split(" ")[1]))
    for sg in ("띠 홈 쪽 벽", "홈 바닥", "홈 건너편 벽", "띠 바깥 변"):
        ii = [r["i"] for r in rows if r["seg"] == sg]
        want.append(ii[len(ii) // 2])
    want.append(N)
    chk = []
    for i in sorted(set(want)):
        z = P.poses[i]
        chk.append({"step": label(i, split), "ph": z["ph"], "J_WP_P_X": round(z["cx"] - PARK[0], 4), "J_WP_P_Y": round(z["cy"] - PARK[1], 4),
                    "J_WP_P_ROT": round(z["th"], 4), "bbox_x0_x1_y0_y1": bbox(z), "J_U4_PRESS": z["np"], "J_U5_LIFT": z["fl"]})
    dump("check_poses_p.json", chk, 1)
    print("steps", N, "P1", len(p1) - 1, "P2", len(p2) - 1, "split", split, "window", i_s, i_e)
    print("area", round(area, 2), "vol", round(area * T, 1), "poly", round(poly_area(OUTLINE), 1), "FC", FC, "FA0", FA0, "SV_TIP_IN", SV_TIP_IN, "SF_IN", SF_IN)
    print("others same", same, len(others), "wheel", info["wheel_total_deg"])
    for k, v in C.pack(best).items():
        if v["value"]:
            print(k, v["value"], "|", v["at"])
    for k, v in gaps.items():
        print("gap", k, v)
    for c in chg:
        print("chg", c)
    for s in segs:
        print("%-28s %s~%s n%4d ROT %s X%7.1f +X%7d 밖%6d 포%6d | U4 %s 45 %s | U5 %s best %s | dn4 %d dn5 %d | off %d/%d/%d up %d" % (
            s["구간"], s["단계"][0], s["단계"][1], s["자세"], s["ROT"], s["X 최대"], s["+X 넓이"], s["볼 받침 밖"], s["포켓 위"],
            s["U4 접지 d1 100 [최소, 최대, 평균]"], s["U4 접지 d1 45"], s["U5 접지 d2 440"], s["U5 접지 가장 좋은 d2"], s["U4 내림 자세"], s["U5 내림 자세"],
            s["두 바퀴 다 반 미만(d1 100, d2 440)"], s["두 바퀴 다 반 미만(d1 100, 가장 좋은 d2)"], s["두 바퀴 다 반 미만(d1 45, 가장 좋은 d2)"], s["연구에서 두 바퀴 다 들림"]))
    for s in hc["seg"]:
        print(s["seg"], "I", s["I"], "have", s["have"], "room", s["room"], "tmin", s["t_min_SF1_s"])
    print("mass", hc["mass_kg"], "bytes", [os.path.getsize(os.path.join(HERE, f)) for f in ("study_CYCLE_P1.json", "study_CYCLE_P2.json", "study_others.json")])
    for c in chk:
        print("chk", c["step"], c["J_WP_P_X"], c["J_WP_P_Y"], c["J_WP_P_ROT"], c["bbox_x0_x1_y0_y1"])


if __name__ == "__main__":
    main()
