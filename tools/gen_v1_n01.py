# -*- coding: utf-8 -*-
"""N01 U1 헤드 개조 + 좁은 홈 묶음 생성기 — v1.0.1 -> v1.0.2 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_N01_select.md(N01-C3 수정안)를 그대로 그린다.
python -B tools/gen_v1_n01.py -> tools/out/mech_N01/model/stage_1_geom.json, stage_2_study.json,
                                 tools/out/mech_N01/edit.json(이어 붙인 것), study_info.json
gen_v1_prep.py는 import만 하고 고치지 않는다.
좌표: 바늘점 원점, 작업면 Z 0, 이송 +Y. 노루발은 J_U1_PRESSER = 0 자세의 세계 좌표로 그린다.
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v1_prep as G

OUT = os.path.join(ROOT, "out", "mech_N01")
STITCH = 4.0  # D-12 임시 땀 길이
P867 = "STEP대기_867-392342_"


# ---------- 연구: 홈 바닥 땀 피벗(tools/out/mech_N01_sel/stitch_calc.py에서 옮김) ----------
def stitch_arc(P, k, r, ang0, th0, dth, ph):
    """오목 홈 바닥: 땀마다 ① 노루발 20·바늘 -30, 바늘점 둘레 피벗 ② 노루발 0·바늘 0, 현 이송(theta 고정).
    처음·끝 피벗은 반각(dth/2n), 가운데는 dth/n."""
    arc_len = abs(dth) / 180.0 * math.pi * r
    n = max(1, math.ceil(arc_len / STITCH - 1e-9))
    d = dth / n
    pts = []
    for j in range(n + 1):
        phi = math.radians(ang0 - j * d)
        pts.append((k[0] + r * math.cos(phi), k[1] + r * math.sin(phi)))
    th = th0
    for j in range(n + 1):
        half = (j == 0 or j == n)
        th1 = th + (d / 2 if half else d)
        P.pivot(pts[j], th, th1, ph + " 피벗 %d" % j)
        th = th1
        if j < n:
            P.sew_line(pts[j], pts[j + 1], th, ph + " 이송 %d" % j, fine_ends=-1)
    return n, 2 * r * math.sin(math.radians(abs(d) / 2))


def groove_cycle_new():
    a = G.G_A
    P = G.Path()
    P.add(G.C0[0], G.C0[1], 0.0, G.PRESSER_UP, 0.0, "① 대기·로딩")
    start = (a / 2, 0.0)
    P.move_c(G.center(start, 0.0), G.STEP_FEED, "② 시작점으로")
    P.tool(0.0, 0.0, "② 노루발 내림")
    yN = G.G_Y + G.G_W / 2
    yS = G.G_Y - G.G_W / 2
    xb = a / 2 - G.G_D + G.G_R
    m1 = (a / 2, yN)
    P.sew_line(start, m1, 0.0, "③ 봉제 직선", fine_ends=50.0)
    P.pivot(m1, 0.0, 90.0, "④ 홈 입구(볼록)")
    P.sew_line(m1, (xb, yN), 90.0, "③ 홈 안 벽", fine_ends=-1)
    i0 = len(P.poses)
    n, chord = stitch_arc(P, (xb, G.G_Y), G.G_R, 90.0, 90.0, -180.0, "④ 홈 바닥")
    i1 = len(P.poses) - 1
    m2 = (a / 2, yS)
    P.sew_line((xb, yS), m2, -90.0, "③ 홈 안 벽", fine_ends=-1)
    P.pivot(m2, -90.0, 0.0, "④ 홈 입구(볼록)")
    # 이후(G2)는 gen_v1_prep.groove_cycle과 같다
    corners = [(a / 2, -a / 2), (-a / 2, -a / 2), (-a / 2, a / 2), (a / 2, a / 2)]
    p, th = m2, 0.0
    for i, q in enumerate(corners):
        P.sew_line(p, q, th, "③ 봉제 직선", fine_ends=(50.0 if i == 0 else 0.0))
        P.pivot(q, th, th + 90, "④ 볼록 모서리 %d" % (i + 1))
        p, th = q, th + 90
    P.sew_line(p, start, th, "③ 봉제 직선")
    P.sew_line(start, (a / 2, -G.OVERLAP), th, "⑤ 이음매 겹침")
    P.tool(G.PRESSER_UP, 0.0, "⑤ 사절·노루발 들기")
    P.move_c(G.C0, G.STEP_FEED, "⑥ 배출 자리로")
    return P, (i0, i1), n, chord


def split(P):
    cut = max(i for i, p in enumerate(P.poses) if p[5].startswith("④ 홈 입구"))
    g1, g2 = G.Path(), G.Path()
    g1.poses = P.poses[:cut + 1]
    g2.poses = P.poses[cut:]
    return g1, g2


# ---------- 형상 ----------
def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0, "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return {"command": "solid.box", "params": p}


def cyl(r, x, y, z0, z1, op, tg=None, name=None):
    p = {"radius": r, "height": z1 - z0, "base": [x, y, z0], "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return {"command": "solid.cylinder", "params": p}


def geom_stage():
    s = [
        # 노루발을 값 0에 놓고 세계 좌표로 그린다(E-15)
        {"command": "joint.drive", "params": {"joint": "J_U1_PRESSER", "value": 0, "quiet": True}},
        {"command": "joint.drive", "params": {"joint": "J_U1_NEEDLE", "value": 0, "quiet": True}},
        # A1·A3 이름만 바꿈(형상 그대로)
        {"command": "body.rename", "params": {"body": "U1_UPPER", "name": P867 + "UPPER"}},
        {"command": "body.rename", "params": {"body": "U1_LOWER_POD", "name": P867 + "LOWER"}},
        # A2·B5 옛 상자 지움
        {"command": "solid.remove", "params": {"bodies": ["U1_BUNDLE", "U1_PRESSER_BOX"]}},
        # A2 노즈: X -11~11, Y -10~15, Z 46~125, 노루발대 구멍 Ø7 축 (-5,-3) 관통
        box(P867 + "NOSE", -11, 11, -10, 15, 46, 125),
        cyl(3.5, -5, -3, 45, 126, "cut", [P867 + "NOSE"]),
        {"command": "component.move_bodies", "params": {"bodies": [P867 + "NOSE"], "component": "U1_HEAD"}},
        # B5 노루발 P_N01_FOOT(값 0): 발바닥 X -10~3·Y -8~6·Z 12~14, 바늘 구멍 Ø3, 노루발대 Ø6 Z 14~80
        box("P_N01_FOOT", -10, 3, -8, 6, 12, 14),
        cyl(3.0, -5, -3, 14, 80, "join", ["P_N01_FOOT"]),
        cyl(1.5, 0, 0, 11, 15, "cut", ["P_N01_FOOT"]),
        {"command": "component.move_bodies", "params": {"bodies": ["P_N01_FOOT"], "component": "U1_PRESSER"}},
        # C6 카세트 X ±15 -> ±11 (Y -45~-21, Z 13~124 그대로)
        box(None, -16, -11, -46, -20, 12, 125, "cut", ["U8_CASSETTE_BOX"]),
        box(None, 11, 16, -46, -20, 12, 125, "cut", ["U8_CASSETTE_BOX"]),
        # 재질(E-09): S45C 밀링
        {"command": "material.create", "params": {"name": "S45C", "density_g_cm3": 7.85, "color": "#9aa0a6"}},
        {"command": "material.assign", "params": {"bodies": ["P_N01_FOOT"], "material": "S45C"}},
    ]
    return s


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    P, (i0, i1), n, chord = groove_cycle_new()
    g1, g2 = split(P)
    old = G.groove_cycle()
    _, og2 = split(old)
    k1 = G.keys_of(g1)
    k2_new, k2_old = G.keys_of(g2), G.keys_of(og2)
    same_g2 = (k2_new == k2_old) and len(g2.poses) == len(og2.poses)
    study = [{"command": "motion.study", "params": {"study": "CYCLE_G1", "steps": len(g1.poses) - 1, "keys": k1}},
             {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}}]
    geo = geom_stage()
    json.dump(geo, open(os.path.join(OUT, "model", "stage_1_geom.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(study, open(os.path.join(OUT, "model", "stage_2_study.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(geo + study, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False)
    # 피벗 끝·이송 끝 단계(검사용)
    piv_end, feed_end = [], []
    for i in range(i0, i1 + 1):
        ph = P.poses[i][5]
        nx = P.poses[i + 1][5] if i + 1 < len(P.poses) else ""
        if ph != nx:
            (piv_end if "피벗" in ph else feed_end).append(i)
    info = {"G1_steps": len(g1.poses) - 1, "G2_steps": len(g2.poses) - 1, "G2_same_keys": same_g2,
            "bottom": [i0, i1, i1 - i0 + 1], "stitches": n, "chord": round(chord, 4),
            "pivot_end_steps": piv_end, "feed_end_steps": feed_end,
            "study_bytes": os.path.getsize(os.path.join(OUT, "model", "stage_2_study.json"))}
    json.dump(info, open(os.path.join(OUT, "study_info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(info)


if __name__ == "__main__":
    main()
