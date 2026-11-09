# -*- coding: utf-8 -*-
"""VGR-01 모델링 생성기 — 좁은 V자 홈 매트 모형 WP_V(MAT_V·TAPE_V·SEAM_V), 모형 조인트 J_WP_V_X·Y·ROT, 연구 CYCLE_V.

python -X utf8 -B tools/gen_v2_vgr01.py  ->  tools/out/mech_VGR-01/model/stage_*.json, study_*.json, cycle_v.json

근거: 설계안 docs/reports/mechanism/mech_VGR-01_design.md 부록 2·5절(1회차), _design1.md 3절, _design2.md 4절.
좌표·식은 tools/gen_v2_prep.py와 같다(매트 중심 c = -R(th) p, p = 바늘 밑 매트 좌표 점, X = cx - cpark_x).
가정: D-150(V 30°, R_b 2, 깊이 150, U홈 자리), D-152(d2 440 -> J_U5_X 1360), D-104(바퀴 r 60), D-78·D-144(e 6.5).
U5 키(design2 4-2): 꼭짓점 ROT -35에서 정지·들기, 입구2 ROT -30에서 정지·내림. 생성기 far_off 판정은 쓰지 않고 지시 각으로 둔다.
"""
import json, math, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_VGR-01", "model")
os.makedirs(OUT, exist_ok=True)

T, TAPE_T, WING, OVERLAP = 10.0, 1.0, 10.0, 30.0
PR_UP, ND_DN = 20.0, -30.0
D1, WR = 100.0, 60.0
D2_PARK, D2_V = 1800.0, 440.0
FX_V = D2_PARK - D2_V            # J_U5_X 1360
LIFT_UP, LIFT_DN, FLOAT_MAT = 30.0, -10.0, 10.0   # FUNC-01: 내림 = LIFT -10 + FLOAT 10(매트 윗면 Z 10)
U4_UP, U4_DN = 8.627, 0.0        # J_U4_PRESS(deg): 들림 8.627, 매트 윗면 0 (CYCLE_G1과 같음)
SH_PARK = -60.0                  # J_U6_SHIFT 대기
A = 1200.0
E = 6.5
STEP_FEED, STEP_FINE = 25.0, 5.0
PARK = (-593.5, -300.0)          # WP_G와 같은 대기 중심(F01-C1 e 6.5)
START_C = (-593.5, 0.0)

# V30_r2 경로(vgeom.json, vsweep2.py와 같음)
P1 = (593.5, -254.82); A0 = (455.527, -291.79); A1 = (455.527, -308.21); P2 = (593.5, -345.18)
AC = (457.727, -300.0)
R_ARC = math.hypot(A0[0] - AC[0], A0[1] - AC[1])
LIFT_AT_VERTEX = -35.0           # design2: U5 들기(옛 -40)
LOWER_AT_ENTRY2 = -30.0

WP_J = ["J_WP_%s_%s" % (k, ax) for k in "LSGV" for ax in ("X", "Y", "ROT")]
ORDER = ["J_U3_PRESSER", "J_U3_NEEDLE", "J_U4_WHEEL_ROT", "J_U5_X", "J_U5_WHEEL_ROT"] + WP_J[:9] + \
        ["J_U4_PRESS", "J_U6_SHIFT", "J_U7_CST_X", "J_U7_CST_Y", "J_U7_CUT", "J_U7_TUCK", "J_U7_FEED", "J_U7_LATCH",
         "J_U5_LIFT", "J_U5_FLOAT"] + WP_J[9:]


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

    def sew_line(self, p0, p1, th, ph, fine_ends=0.0):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        cuts = [0.0]
        if fine_ends > 0 and L > 2 * fine_ends:
            a, b = fine_ends, L - fine_ends
            s = 0.0
            while s < a - 1e-9:
                s = min(a, s + STEP_FINE); cuts.append(s)
            n = max(1, math.ceil((b - a) / STEP_FEED - 1e-9))
            cuts += [a + (b - a) * i / n for i in range(1, n + 1)]
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
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p)

    def turn(self, p, th0, th1, ph, hold=None):
        """바늘점 p 둘레 피벗 1° 간격. hold = (각, {키}) : 그 각에서 정지 한 단계 더(U5 승강)."""
        n = max(1, math.ceil(abs(th1 - th0) - 1e-9))
        for i in range(1, n + 1):
            th = th0 + (th1 - th0) * i / n
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p)
            if hold and abs(th - hold[0]) < 1e-9:
                self.add(ph=ph + " 정지·" + hold[2], **hold[1])

    def arc(self, k, r, ang0, th0, dth, ph, hold=None):
        n = max(1, math.ceil(abs(dth) - 1e-9))
        for i in range(1, n + 1):
            th = th0 + dth * i / n
            phi = math.radians(ang0 - (th - th0))
            p = (k[0] + r * math.cos(phi), k[1] + r * math.sin(phi))
            c = center(p, th)
            self.add(cx=c[0], cy=c[1], th=th, ph=ph, pt=p)
            if hold and abs(th - hold[0]) < 1e-9:
                self.add(ph=ph + " 정지·" + hold[2], **hold[1])


def cycle_v():
    P = Path()
    P.add(cx=PARK[0], cy=PARK[1], th=0.0, pr=PR_UP, nd=0.0, np=U4_UP, fx=0.0, fl=LIFT_UP, fz=0.0, sh=SH_PARK,
          ph="① 대기·로딩(매트를 올린 자리)")
    P.move_c(START_C, STEP_FEED, "① 작업자가 가장자리를 노루발 표시에 맞춤")
    P.short("② 노루발 내림·센서 슈 내림", pr=0.0, sh=0.0)
    P.add(ph="② 바늘 옆 바퀴 내림")                      # CYCLE_G1 15: 8.627 그대로
    P.add(ph="② 바늘 옆 바퀴 내림", np=U4_DN)            # CYCLE_G1 16: 0
    P.carriage(FX_V, "② 먼 쪽 대차 d2 440으로(J_U5_X 1360)")
    P.short("② 먼 쪽 바퀴 내림", fl=LIFT_DN, fz=FLOAT_MAT)
    start = (A / 2 - E, 0.0)
    P.sew_line(start, P1, 0.0, "③ 접근 봉제", fine_ends=50.0)
    P.short("③ V 입구1(볼록) 노루발 들기·바늘 꽂음", pr=PR_UP, nd=ND_DN)
    P.turn(P1, 0.0, 75.0, "③ V 입구1(볼록) 피벗 U4+U5")
    P.short("③ V 입구1 노루발 내림", pr=0.0, nd=0.0)
    P.sew_line(P1, A0, 75.0, "③ V 위 벽", fine_ends=-1)
    P.short("③ V 꼭짓점 노루발 들기·바늘 꽂음", pr=PR_UP, nd=ND_DN)
    a0 = math.degrees(math.atan2(A0[1] - AC[1], A0[0] - AC[0]))
    P.arc(AC, R_ARC, a0, 75.0, -150.0, "③ V 꼭짓점 호(오목)",
          hold=(LIFT_AT_VERTEX, {"fl": LIFT_UP, "fz": 0.0}, "먼 쪽 바퀴 들기(ROT -35)"))
    P.short("③ V 꼭짓점 노루발 내림", pr=0.0, nd=0.0)
    P.sew_line(A1, P2, -75.0, "③ V 아래 벽(먼 쪽 바퀴 들림)", fine_ends=-1)
    P.short("③ V 입구2(볼록) 노루발 들기·바늘 꽂음", pr=PR_UP, nd=ND_DN)
    P.turn(P2, -75.0, 0.0, "③ V 입구2(볼록) 피벗",
           hold=(LOWER_AT_ENTRY2, {"fl": LIFT_DN, "fz": FLOAT_MAT}, "먼 쪽 바퀴 내림(ROT -30)"))
    P.short("③ V 입구2 노루발 내림", pr=0.0, nd=0.0)
    P.sew_line(P2, (A / 2 - E, P2[1] - 50.0), 0.0, "③ 떠나기 봉제 50", fine_ends=-1)
    P.short("④ 노루발 들기", pr=PR_UP)
    P.short("④ 바퀴 들기·센서 슈 대기", fl=LIFT_UP, fz=0.0, sh=SH_PARK)
    P.poses[-1]["np"] = U4_UP
    return P


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


def keys_v(P):
    N = len(P.poses) - 1
    col = {"J_U3_PRESSER": "pr", "J_U3_NEEDLE": "nd", "J_U4_PRESS": "np", "J_U4_WHEEL_ROT": "rn", "J_U5_X": "fx",
           "J_U5_LIFT": "fl", "J_U5_FLOAT": "fz", "J_U5_WHEEL_ROT": "rf", "J_U6_SHIFT": "sh"}
    out = []
    for j in ORDER:
        if j in col:
            nd = 3 if j.endswith("ROT") else 4
            pts = [[i, round(z[col[j]], nd)] for i, z in enumerate(P.poses)]
        elif j == "J_WP_V_X":
            pts = [[i, round(z["cx"] - PARK[0], 4)] for i, z in enumerate(P.poses)]
        elif j == "J_WP_V_Y":
            pts = [[i, round(z["cy"] - PARK[1], 4)] for i, z in enumerate(P.poses)]
        elif j == "J_WP_V_ROT":
            pts = [[i, round(z["th"], 4)] for i, z in enumerate(P.poses)]
        else:
            pts = [[0, 0], [N, 0]]
        out.append({"joint": j, "points": compress(pts)})
    return out


def interp(pts, t):
    if t <= pts[0][0]:
        return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= t <= b:
            return va if b == a else va + (vb - va) * (t - a) / (b - a)
    return pts[-1][1]


def needle_check(P, keys):
    K = {k["joint"]: k["points"] for k in keys}
    worst = 0.0
    for i, z in enumerate(P.poses):
        if z.get("pt") is None:
            continue
        cx = PARK[0] + interp(K["J_WP_V_X"], i); cy = PARK[1] + interp(K["J_WP_V_Y"], i); th = interp(K["J_WP_V_ROT"], i)
        p = rot(-th, (-cx, -cy))
        worst = max(worst, math.hypot(p[0] - z["pt"][0], p[1] - z["pt"][1]))
    return worst


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
X0, Y0 = PARK


def w(p):
    return [round(X0 + p[0], 4), round(Y0 + p[1], 4)]


def box(name, xa, xb, ya, yb, za, zb):
    return {"command": "solid.box", "params": {"length": xb - xa, "width": yb - ya, "height": zb - za,
                                               "corner": [X0 + xa, Y0 + ya, za], "operation": "new", "body_name": name}}


def poly_cut(pts, za, h, target, nm):
    return [
        {"command": "sketch.create", "params": {"plane": {"origin": [0, 0, za], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": nm}},
        {"command": "sketch.line", "params": {"points": [w(p) for p in pts], "closed": True}},
        {"command": "sketch.finish", "params": {}},
        {"command": "solid.extrude", "params": {"sketch": nm, "distance": h, "operation": "cut", "targets": [target]}},
    ]


def cyl_cut(r, za, h, target):
    return {"command": "solid.cylinder", "params": {"radius": r, "height": h, "base": [X0 + AC[0], Y0 + AC[1], za],
                                                    "operation": "cut", "targets": [target]}}


def stage_bodies():
    h = A / 2
    c = [box("MAT_V", -h, h, -h, h, 0, T)]
    c += poly_cut([(457.21, -298.068), (610, -257.128), (610, -342.872), (457.21, -301.932)], -1, 12, "MAT_V", "SK_VGR01_MAT_V")
    c.append(cyl_cut(2.0, -1, 13, "MAT_V"))
    c.append(box("TAPE_V", -h - TAPE_T, h + TAPE_T, -h - TAPE_T, h + TAPE_T, 0, T + TAPE_T))
    c += poly_cut([(457.469, -299.034), (610, -258.163), (610, -341.837), (457.469, -300.966)], -1, 13, "TAPE_V", "SK_VGR01_TAPE_V")
    c.append(cyl_cut(1.0, -1, 14, "TAPE_V"))
    c.append(box("TAPE_V_IN", -h + WING, h - WING, -h + WING, h - WING, -1, T + 2))
    c += poly_cut([(454.622, -288.409), (610, -246.775), (610, -353.225), (454.622, -311.591)], -2, 15, "TAPE_V_IN", "SK_VGR01_TAPE_V_IN")
    c.append(cyl_cut(12.0, -2, 16, "TAPE_V_IN"))
    c.append({"command": "solid.combine", "params": {"target": "TAPE_V", "tools": ["TAPE_V_IN"], "operation": "cut"}})
    c.append(box("SEAM_V", h - WING, h + 2 * TAPE_T, -OVERLAP, 0, T + TAPE_T, T + 2 * TAPE_T))
    return c


def comp(name):
    return {"command": "component.create", "params": {"name": name, "parent": "root", "activate": False}}


def jc(nm, typ, a, b, pt, z, lim):
    return {"command": "joint.create", "params": {
        "type": typ, "name": nm, "flip": True, "limits": [lim], "quiet": True,
        "a": {"occurrence": a, "point": pt, "z": z}, "b": {"occurrence": b, "point": pt, "z": z}}}


def stage_joints():
    cp = [X0, Y0, 0]
    c = [comp(n) for n in ("WP_V_X", "WP_V_Y", "WP_MAT_V", "WP_TAPE_V")]
    c += [{"command": "component.move_bodies", "params": {"bodies": ["MAT_V"], "component": "WP_MAT_V"}},
          {"command": "component.move_bodies", "params": {"bodies": ["TAPE_V", "SEAM_V"], "component": "WP_TAPE_V"}},
          {"command": "joint.rigid_group", "params": {"occurrences": ["WP_MAT_V:1", "WP_TAPE_V:1"]}},
          jc("J_WP_V_X", "slider", "U1_FRAME:1", "WP_V_X:1", cp, [1, 0, 0], [-3000, 3000]),
          jc("J_WP_V_Y", "slider", "WP_V_X:1", "WP_V_Y:1", cp, [0, 1, 0], [-3000, 3000]),
          jc("J_WP_V_ROT", "revolute", "WP_V_Y:1", "WP_MAT_V:1", cp, [0, 0, 1], [-360, 720])]
    return c


def main():
    P = cycle_v()
    wheel_rot(P)
    keys = keys_v(P)
    N = len(P.poses) - 1
    nerr = needle_check(P, keys)
    study = {"command": "motion.study", "params": {"name": "CYCLE_V", "steps": N, "keys": keys}}
    # 다른 연구: 지금 키 통째 + J_WP_V_* 0 (motion.study keys는 통째 갈아끼움, F01-C1)
    ml = json.load(open(os.path.join(OUT, "motion_list_before.json"), encoding="utf-8"))
    others = []
    for s in ml["studies"]:
        ks = [{"joint": k["joint_name"], "index": k.get("index", 0), "points": k["points"]} for k in s["keys"]]
        have = {k["joint"] for k in ks}
        for j in WP_J[9:]:
            if j not in have:
                ks.append({"joint": j, "points": [[0, 0], [s["steps"], 0]]})
        others.append({"command": "motion.study", "params": {"study": s["name"], "steps": s["steps"], "keys": ks}})
    ph = phases(P)
    lift_step = next(i for i, z in enumerate(P.poses) if "먼 쪽 바퀴 들기(ROT -35)" in z["ph"])
    lower_step = next(i for i, z in enumerate(P.poses) if "먼 쪽 바퀴 내림(ROT -30)" in z["ph"])
    info = {"steps": N, "needle_path_err_max_mm": round(nerr, 5), "phases": ph,
            "u5_lift_hold_step": lift_step, "u5_lower_hold_step": lower_step,
            "wheel_total_deg": {"U4": round(P.poses[-1]["rn"], 2), "U5": round(P.poses[-1]["rf"], 2)},
            "poses": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in z.items() if k != "pt"} for z in P.poses]}
    for nm, c in (("stage_1_bodies", stage_bodies()), ("stage_2_joints", stage_joints())):
        json.dump(c, open(os.path.join(OUT, nm + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump([study], open(os.path.join(OUT, "study_CYCLE_V.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(others, open(os.path.join(OUT, "study_others.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(info, open(os.path.join(OUT, "cycle_v.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("steps", N, "needle err", round(nerr, 5), "lift", lift_step, "lower", lower_step, info["wheel_total_deg"])
    for p in ph:
        print(p)
    print("study bytes", os.path.getsize(os.path.join(OUT, "study_CYCLE_V.json")),
          "others bytes", os.path.getsize(os.path.join(OUT, "study_others.json")))


if __name__ == "__main__":
    main()
