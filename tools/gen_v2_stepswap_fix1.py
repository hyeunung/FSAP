# -*- coding: utf-8 -*-
"""STEPSWAP 수정 1 생성기 — v2.5.6 -> v2.5.7 (모델링부 2026-11-05)
KDM10-06 실물 교체(SW-R6): 소켓(KDM10S-06, U8_PNEU) + 플러그(KDM10P-06, U7_CASSETTE), 짝 방향 = 세계 X(플러그 +X, CST_X +25로 빠짐).
STEP 축 그대로(회전 없음), 원점 (40, -143.5, 680). 소켓 귀 뒷면 X 20에 받침판 P_M08_KDM_BRKT(A5052) 앞면을 대고 CB3-10 ×4(뒤에서 +X).
관: U8 쪽 TU0604_M08K_U7_1~6(소켓 -X 면 X 11.7), 카세트 쪽 TU0604_M08K_U7C_1~6(플러그 +X 면 X 59).
python -X utf8 -B tools/gen_v2_stepswap_fix1.py  -> tools/out/mech_STEPSWAP/fix1/edit_fix1.json
"""
import itertools
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_m08 as m8  # noqa: E402
from gen_v2_m02 import C, box, cyl, mat_assign  # noqa: E402
import gen_v2_stepswap as sw  # noqa: E402

PRJ = os.path.dirname(ROOT).replace("\\", "/")
STEP = PRJ + "/purchased-step/"
OUT = os.path.join(ROOT, "out", "mech_STEPSWAP", "fix1")

XS, YC, ZC = 40.0, -143.5, 680.0          # KDM STEP 원점(세계)
COL = {"A": YC - 10.0, "B": YC + 10.0}     # 포트 열 Y: -153.5(A 관) / -133.5(B 관)
ROWS = {1: ZC - 17, 2: ZC - 17, 3: ZC, 4: ZC, 5: ZC + 17, 6: ZC + 17}   # 관 k -> 포트 줄 Z
COLK = {1: "A", 3: "A", 5: "A", 2: "B", 4: "B", 6: "B"}
X_SOCK = XS - 28.3                         # 소켓 피팅 끝면 X 11.7
X_PLUG = XS + 19.0                         # 플러그 피팅 끝면 X 59
BR = "P_M08_KDM_BRKT"

# 카세트 안 관(gen_v2_m08_fix1.stage_u7c) — 오름 길까지 그대로, 줄 Y만 -143.5 -> -153.5, 끝을 플러그 +X 면으로
a, b, c = 79.65, 86.15, 92.65
LA, LB = COL["A"], COL["B"]


def u7c():
    T = {1: [(14.5, -181.9, 100.25), (4, -181.9, 100.25), (4, -249, 100.25), (4, -249, 345), (a, -249, 345), (a, LA, 345), (a, LA, ROWS[1])],
         2: [(29, -246.4, 100.25), (29, -256, 100.25), (29, -256, 335), (a, -256, 335), (a, LB, 335), (a, LB, ROWS[2])],
         3: [(29, -196.4, 35.1), (29, -212, 35.1), (45, -212, 35.1), (45, -270, 35.1), (45, -270, 365), (b, -270, 365), (b, LA, 365),
             (b, LA, ROWS[3])],
         4: [(29, -246.4, 35.1), (29, -263, 35.1), (29, -263, 355), (b, -263, 355), (b, LB, 355), (b, LB, ROWS[4])],
         5: [(c, -120.5, 303), (c, LA, 303), (c, LA, ROWS[5])],
         6: [(c, -120.5, 505), (c, LB, 505), (c, LB, ROWS[6])]}
    for k in T:
        T[k].append((X_PLUG, COL[COLK[k]], ROWS[k]))
    return T


# U8 쪽: 옛 길(gen_v2_stepswap.tubes) 앞부분 + (x_t, lane, z0) -> (x_t, lane, zl) -> (x_t, col, zl) -> (x_t, col, row) -> (X_SOCK, col, row)
LANE = {3: 130.0, 4: 140.0, 5: 150.0}
XT_C = [-8.0, -16.0, -24.0, -32.0, -40.0, -48.0]
ZL_C = [655.5, 671.5, 688.5, 705.5, 714.5, 723.5]


def u8_head():
    Y = sw.PORT_Y - 13.5
    H = {}
    n = 0
    for st in (3, 4, 5):
        x = sw.ST[st]
        n += 1
        H[n] = ([sw.A0(x), (x, Y, 295), (x, 14, 295), (x, 14, 670), (x, LANE[st], 670)], LANE[st], 670.0)
        n += 1
        H[n] = ([sw.B0(x), (x, Y, 660), (x, LANE[st], 660)], LANE[st], 660.0)
    return H


def u8_route(xt, zl):
    T = {}
    for k, (head, lane, z0) in u8_head().items():
        col, row = COL[COLK[k]], ROWS[k]
        p = head + [(xt[k], lane, z0)]
        if abs(zl[k] - z0) > 1e-6:
            p.append((xt[k], lane, zl[k]))
        p.append((xt[k], col, zl[k]))
        if abs(row - zl[k]) > 1e-6:
            p.append((xt[k], col, row))
        p.append((X_SOCK, col, row))
        T[k] = p
    return T


def segdist(p1, q1, p2, q2):
    """두 선분 사이 최소 거리(수치 표본)."""
    best = 1e9
    N = 24
    for i in range(N + 1):
        t = i / N
        P = [p1[j] + t * (q1[j] - p1[j]) for j in range(3)]
        d = [q2[j] - p2[j] for j in range(3)]
        L2 = sum(v * v for v in d) or 1e-12
        s = max(0.0, min(1.0, sum((P[j] - p2[j]) * d[j] for j in range(3)) / L2))
        Q = [p2[j] + s * d[j] for j in range(3)]
        best = min(best, math.dist(P, Q))
    return best


def mind(T, only_tail=8):
    """관끼리 중심선 최소 거리(바뀐 끝부분 구간만)."""
    ks = sorted(T)
    worst = (1e9, None)
    for i, j in itertools.combinations(ks, 2):
        A, B = T[i][-only_tail:], T[j][-only_tail:]
        for u in range(len(A) - 1):
            for v in range(len(B) - 1):
                dd = segdist(A[u], A[u + 1], B[v], B[v + 1])
                if dd < worst[0]:
                    worst = (dd, (i, j, u, v))
    return worst


def search():
    """배치(tools/out/mech_STEPSWAP/fix1/search.py 로 찾음: 축 정렬 선분 사이 중심 거리 >= 8 = 관 지름 6 + 틈 2)."""
    xt = {1: -8.0, 2: -16.0, 3: -24.0, 4: -48.0, 5: -32.0, 6: -40.0}
    zl = {1: 671.5, 2: 655.5, 3: 688.5, 4: 705.5, 5: 714.5, 6: 723.5}
    return xt, zl, 8.0


def kdm():
    s = []
    gone = ["STEP대기_KDM10-06_M08", "STEP대기_KDM10-06_M08_PLUG"]
    old_t = ["TU0604_M08S_U7_%d" % k for k in range(1, 7)] + ["TU0604_M08_U7C_%d" % k for k in range(1, 7)]
    # 옛 U7C 관 컴포넌트는 지우지 않는다: 그 안의 피처를 지우면 앞선 Remove(같은 이름 바디, M08 수정 1)가 바디를 못 찾음(CLI 1차 실행 실패)
    # -> 바디만 지우고, 새 관 바디를 그 컴포넌트로 옮긴 뒤 컴포넌트 이름을 새 이름으로 바꾼다
    s += [C("solid.remove", bodies=gone + old_t)] + [C("component.delete", component=x) for x in gone + old_t[:6]]
    # 받침판: 앞판(YZ 다각형, X 14~20) + 발(XY, X 12~142 · Y -86~-52 · Z 650~656, 옛 CB5-12 ×2 자리)
    web = [(-172, 618), (-112, 618), (-112, 656), (-50, 656), (-50, 742), (-172, 742)]
    cm = m8.prism_yz(BR, web, 14.0, 20.0)
    foot = m8.prism(BR + "_F", [(12, -86), (142, -86), (142, -52), (12, -52)], 650.0, 656.0, op="join", tg=[BR])
    cm += foot
    # 피팅 창(Y YC±17, Z ZC±41)·나사 구멍 Ø3.4 ×4·발 구멍 Ø5.5 ×2
    cm.append(box(None, 13, 21, YC - 17, YC + 17, ZC - 41, ZC + 41, op="cut", tg=[BR]))
    for dy in (-14, 14):
        for dz in (-49.5, 49.5):
            cm.append(cyl(1.7, [13.0, YC + dy, ZC + dz], 8.0, [1, 0, 0], "cut", [BR]))
    for x in (97.0, 133.0):
        cm.append(cyl(2.75, [x, -60.0, 649.0], 8.0, [0, 0, 1], "cut", [BR]))
    s += m8.made(cm, [BR], "A5052")
    s.append(C("component.activate", component="U8_PNEU"))
    s += [C("file.insert_step", path=STEP + "KDM10-06/KDM10-06.stp", name="KDM10-06_M08", matrix=[1, 0, 0, XS, 0, 1, 0, YC, 0, 0, 1, ZC]),
          C("body.rename", body="KDM10S-06", name="KDM10S-06_M08"), C("body.rename", body="KDM10P-06", name="KDM10P-06_M08"),
          C("component.metadata.set", component="KDM10-06_M08", part_number="KDM10-06", bom_type="purchased",
            description="SMC KDM10-06 multi-connector STEP: socket KDM10S-06 on bracket (U8), plug KDM10P-06 on cassette (U7), mating +X (STEPSWAP fix1)"),
          C("component.unlock", component="KDM10-06_M08"),
          C("occurrence.reparent", occurrence="KDM10P-06:1", parent="U7_CASSETTE"),
          C("component.activate", component=0)]
    # CB3-10 ×4: 받침판 뒷면(X 14)에서 +X, 소켓 귀(X 20~)에 물림 4
    places = [(14.0, YC + dy, ZC + dz) for dy in (-14, 14) for dz in (-49.5, 49.5)]
    s += m8.insert_group("CB3-10/CB3-10.stp", "CB3-10_M08_PX_KDM", ((1, 0, 0), (0, 0, 1), m8.cross((1, 0, 0), (0, 0, 1))), places,
                         "Cut-Extrude1", "CB3-10", desc="Misumi CB3-10, KDM10S-06 socket ears -> bracket (from bracket back, +X)", mat="SCM435")
    s.append(C("component.metadata.set", component="CB5-12_M08_NZ_KDM", part_number="CB5-12", bom_type="purchased",
               description="Misumi CB5-12, KDM bracket foot -> hanger top M5 tap (STEPSWAP fix1)"))
    return s


def tubes(xt, zl):
    s = []
    for k, pts in u8_route(xt, zl).items():
        nm = "TU0604_M08K_U7_%d" % k
        s += [C("component.create", name=nm, parent="U8_PNEU", activate=False)]
        s += json.loads(json.dumps(m8.tube(nm, pts, 3.0, 15.0)).replace('"SK_%s"' % nm, '"SK_%s_K"' % nm))
        s += [mat_assign([nm], "Default"), C("component.move_bodies", bodies=[nm], component=nm),
              C("component.metadata.set", component=nm, part_number="TU0604", bom_type="purchased",
                description="SMC TU0604 tube, valve -> KDM10S-06 socket (STEPSWAP fix1)")]
    for k, pts in u7c().items():
        nm = "TU0604_M08K_U7C_%d" % k
        oc = "TU0604_M08_U7C_%d" % k
        s += json.loads(json.dumps(m8.tube(nm, pts, 3.0, 15.0)).replace('"SK_%s"' % nm, '"SK_%s_K"' % nm))
        s += [mat_assign([nm], "Default"), C("component.move_bodies", bodies=[nm], component=oc),
              C("component.rename", component=oc, name=nm),
              C("component.metadata.set", component=nm, part_number="TU0604", bom_type="purchased",
                description="SMC TU0604 tube, cassette cylinder -> KDM10P-06 plug (STEPSWAP fix1)")]
    return s


def belt():
    """v2.5.6 벨트 곧은 가닥이 STEP 길이 3,960 그대로 X -2220 ~ 1740으로 그려져 보 앞 공압(매니폴드·밸브·관)과 겹쳤다
    (사본 검사에서 CB4-25 :3 ↔ HTBO_L 8.84 mm3로 드러남). 가닥은 두 풀리 중심 사이 X -2220 ~ -390만 남긴다."""
    return [box(None, -390.0, 1745.0, 95.0, 117.0, 335.0, 445.0, op="cut", tg=["HTBO-S5M150-792_M03", "HTBO-S5M150-792_M03_L"])]


def final():
    rig8 = ["U8_PNEU:1", "KDM10-06_M08:1", "KDM10S-06:1"] + ["CB3-10_M08_PX_KDM:%d" % i for i in range(1, 5)]
    return [C("joint.rigid_group", occurrences=rig8), C("joint.rigid_group", occurrences=["U7_CASSETTE:1", "KDM10P-06:1"]),
            C("component.activate", component=0),
            C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("component.rename", component=0, name="FSAP_v2.5.7"),
            C("document.metadata.set", key="description",
              value="STEPSWAP mechanism fix1: KDM10-06 real STEP (socket on bracket, plug on cassette, mate +X), 12 tubes rerouted")]


def main():
    os.makedirs(OUT, exist_ok=True)
    r = search()
    xt, zl, d = r
    print("tube layout xt", xt, "zl", zl, "min centre dist", round(d, 2))
    T8, T7 = u8_route(xt, zl), u7c()
    print("cassette min", round(mind(T7, 4)[0], 2))
    s = kdm() + tubes(xt, zl) + belt() + final()
    json.dump(s, open(os.path.join(OUT, "edit_fix1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"xt": xt, "zl": zl, "min": d, "u8": T8, "u7c": T7}, open(os.path.join(OUT, "layout.json"), "w", encoding="utf-8"), indent=1)
    print("commands", len(s))


if __name__ == "__main__":
    main()
