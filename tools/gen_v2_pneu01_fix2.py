# -*- coding: utf-8 -*-
"""PNEU-01 수정 2회차 생성기 — 기준 3D_Modeling/FSAP_v2.8.7.sc(다른 이름 저장 v2.8.8) -> FSAP_v2.8.8.sc (모델링부 2026-11-10)
검도 1회차 문제 6건:
 1 CLAMP_F_5 X -120 -> -100 (관 꺾임점 -125 원호 밖)
 2 CLAMP_SO_1 X 960 -> 983 (U6 축 X, REG1_OUT 비스듬 곧은 구간 축)
 3 COMB_KDM 앞판 Y 112~120 -> Y 88~96 (관 6줄 R30 원호 밖 곧은 구간), 아래 날개 + 보 앞면 귀(볼트 자리 그대로)
 4 U7_4/5/6_B 위 토막: 꺾임점 Z 775 -> 781, 세로 내림 굽힘 R 30 -> 20 (호 끝 Z 761, BRKT_KDM +6 윗면 756과 5)
 5 AIR_IN_BRKT Z 266~294 -> 256~304, 볼트 Z 261·299
 6 BRKT_CST_V 세움 띠 폭 13 -> 30 (Y -159~-129, t4) — 외팔 강도
보 탭: 옛 자리 6개 메움(join), 새 자리 6개 cut. 볼트는 기존 occurrence를 world 이동.
python -X utf8 -B tools/gen_v2_pneu01_fix2.py -> tools/out/mech_PNEU-01/model2/stage_*.json, model/tubelog.json 갱신(옛 것 model2/tubelog_v287.json)
"""
import copy, json, math, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
H = os.path.join(ROOT, "out", "mech_PNEU-01")
OUT = os.path.join(H, "model2")
os.makedirs(OUT, exist_ok=True)
TL = os.path.join(H, "model", "tubelog.json")
BAK = os.path.join(OUT, "tubelog_v287.json")
if not os.path.exists(BAK):
    shutil.copy(TL, BAK)

# 1) 관 기록 갱신(B 위 토막 3줄) — crossings가 새 경로를 보도록 먼저 쓴다
sys.path.insert(0, ROOT)
import gen_v2_pneu01 as G  # noqa: E402

TLD = json.load(open(BAK, encoding="utf8"))
BNEW = {}
for k in ("4", "5", "6"):
    nm = "TU0604_M08P_U7_%s_B" % k
    t = TLD["tubes"][nm]
    pts = [list(p) for p in t["pts"]]
    R = list(t["R"])
    assert abs(pts[7][2] - 775) < 1e-6 and abs(pts[8][2] - 775) < 1e-6, (nm, pts[7], pts[8])
    pts[7][2] = 781.0
    pts[8][2] = 781.0
    R[7] = 20.0
    t["pts"] = pts
    t["R"] = R
    t["len"] = round(G.length(pts, R), 1)
    BNEW[nm] = (pts, R, t["r"])
json.dump(TLD, open(TL, "w", encoding="utf8"), ensure_ascii=False, indent=0)

OUT1 = os.path.join(H, "model1")
sys.path.insert(0, OUT1)
import gen_v2_pneu01_fix1 as F  # noqa: E402  (cross.T는 갱신된 tubelog를 읽는다)

C, box, cyl, finish = F.C, F.box, F.cyl, F.finish


def tube_holes(body, ax, val, thick, cond, log):
    """fix1과 같되 구멍 길이를 기운 관 표면이 판 두께를 다 지나도록 늘린다: h = (t + 2 (r+0.25) sin th) / cos th + 3."""
    s = []
    for n, p, d, r in F.crossings(ax, val, cond):
        c = max(abs(d[ax]), 0.2); sn = math.sqrt(max(0.0, 1 - c * c))
        h = (thick + 2 * (r + 0.25) * sn) / c + 3.0
        base = [p[q] - d[q] * h / 2 for q in range(3)]
        s.append(cyl(r + 0.25, base, h, d, op="cut", tg=[body]))
        log.setdefault(body, []).append({"tube": n, "at": [round(v, 4) for v in p], "dir": [round(v, 4) for v in d], "r_hole": r + 0.25, "h": round(h, 2)})
    return s
BEAM = "P_M07_BEAM"
HOLES, FIX, BOLTS, TAPFILL, TAPNEW = {}, {}, [], [], []


def bolt_move(occ, old_bp, new_bp, d, body, through, cb=0.0, mount=BEAM, tap=10.0, tag=""):
    """기존 볼트 occurrence를 옮기고 새 고정품에 여유 구멍(r2.75)·머리 자리(r4.75), 보 탭 옛 자리 메움·새 자리 cut 기록."""
    tr = [round(new_bp[q] - old_bp[q], 4) for q in range(3)]
    s = [C("occurrence.move", occurrence=occ, space="world", translate=tr)]
    s.append(cyl(2.75, [new_bp[q] - d[q] * 0.5 for q in range(3)], through + 1.0, d, op="cut", tg=[body]))
    if cb > 0:
        s.append(cyl(4.75, [new_bp[q] - d[q] * (cb + 0.5) for q in range(3)], cb + 0.5, d, op="cut", tg=[body]))
    if mount:
        TAPFILL.append(([old_bp[q] + d[q] * through for q in range(3)], tap, d))
        TAPNEW.append(([new_bp[q] + d[q] * through for q in range(3)], tap, d))
    BOLTS.append({"occ": occ, "old": old_bp, "new": new_bp, "axis": d, "through": body, "mount": mount, "tag": tag})
    return s


def fixtures():
    st = {}
    Y = [0, 1, 0]
    # --- 1 F_5
    b = "P_M08_TUBE_CLAMP_F_5"; c = -100.0
    cond = lambda p, n: abs(p[1] - 110) < 3 and "_U4_" in n
    s = [C("solid.remove", bodies=[b]), box(b, c - 12, c + 12, 102, 120, 420, 470)] + tube_holes(b, 0, c, 24, cond, HOLES)
    for occ, ox, nx in (("CB5-16_M08_PY:18", -126.0, -106.0), ("CB5-16_M08_PY:19", -114.0, -94.0)):
        s += bolt_move(occ, [ox, 112, 462], [nx, 112, 462], Y, b, 8, cb=10, tag=b)
    s += [C("material.assign", bodies=[b], material="A5052"), C("component.move_bodies", bodies=[b], component=b)]
    st["1_F5"] = s
    FIX[b] = [c - 12, c + 12, 102, 120, 420, 470]
    # --- 2 SO_1 : 블록 X 981~997(구멍 축 X 989, U6 Y53·REG1_OUT 비스듬 곧은 구간), 귀 X 938~1003.
    #     볼트는 옛 자리 X 944·976 그대로(보 탭 그대로). 보(강 각관, 아래 모서리 Z 250 근처) Z 262 탭 메움이 커널에서 실패해서
    #     (union no result, 3회) 지시(X 975~991, 볼트 967·999)에서 블록을 +6 옮기고 볼트를 옛 탭에 둔다. 976 머리 끝 X 980.25 - 블록 981 = 0.75.
    b = "P_M08_TUBE_CLAMP_SO_1"; c = 989.0
    cond = lambda p, n: (n.endswith("_U6") or "REG1_OUT" in n) and p[1] < 100
    s = [C("solid.remove", bodies=[b]), box(b, 981, 997, 45, 112, 232, 270), box(b + "_E", 904, 1003, 112, 120, 252, 272),
         box(b + "_Y", 904, 920, 72, 113, 232, 256),
         C("solid.combine", target=b, tools=[b + "_E", b + "_Y"], operation="join")] + tube_holes(b, 0, c, 16, cond, HOLES)
    # 둘째 멍에 X 904~920: REG1_OUT(X 축 곧은 구간 Y82 Z240)만 잡는다 — SO_2(Z300)~SO_1 자유 구간 314 -> 300 이하
    s += tube_holes(b, 0, 912, 16, lambda p, n: "REG1_OUT" in n and abs(p[1] - 82) < 1, HOLES)
    for x in (944.0, 976.0):
        s.append(cyl(2.75, [x, 111.5, 262], 9.0, Y, op="cut", tg=[b]))
        BOLTS.append({"occ": "CB5-16_M08_PY:%d" % (36 if x == 944 else 37), "old": [x, 112, 262], "new": [x, 112, 262], "axis": Y,
                      "through": b, "mount": BEAM, "tag": b})
    s += [C("material.assign", bodies=[b], material="A5052"), C("component.move_bodies", bodies=[b], component=b)]
    st["2_SO1"] = s
    FIX[b] = [904, 1003, 45, 120, 232, 272]
    # --- 3 COMB_KDM : 앞판 Y88~96, 아래 날개 Z620~626, 보 앞면 귀 Y112~120 Z620~648(볼트 자리 그대로), 웹·팔
    b = "P_M08_TUBE_COMB_KDM"
    c1 = lambda p, n: F.U7(n) and -90 <= p[0] <= -5 and p[2] > 650
    s = [C("solid.remove", bodies=[b]),
         box(b, -88, -8, 88, 96, 620, 722),
         box(b + "_F", -88, -8, 88, 120, 620, 626),
         box(b + "_E", -88, -8, 112, 120, 620, 648),
         box(b + "_W", -88, -80, 44, 96, 665, 722),
         box(b + "_A", -88, -20, 36, 44, 665, 745),
         C("solid.combine", target=b, tools=[b + "_F", b + "_E", b + "_W", b + "_A"], operation="join")]
    s += tube_holes(b, 1, 92, 8, c1, HOLES) + tube_holes(b, 1, 40, 8, c1, HOLES)
    for x in (-80, -16):
        s.append(cyl(2.75, [x, 111.5, 632], 9.0, Y, op="cut", tg=[b]))          # 귀 볼트 여유 구멍
        s.append(cyl(5.0, [x, 87.5, 632], 9.0, Y, op="cut", tg=[b]))           # 앞판 렌치 구멍(육각 렌치 축 방향)
    s += [C("material.assign", bodies=[b], material="A5052"), C("component.move_bodies", bodies=[b], component=b),
          C("component.metadata.set", component=b, part_number=b, bom_type="normal",
            description="KDM tube comb: front plate Y88-96 on straight tube runs + bottom flange + ear to beam front, web, Y40 arm; A5052 milled, 12 holes, 2x CB5-16 (wrench holes)")]
    st["3_KDM"] = s
    FIX[b] = [-88, -8, 36, 120, 620, 745]
    # --- 5 AIR_IN_BRKT
    b = "P_M08_AIR_IN_BRKT"
    X = [1, 0, 0]
    s = [C("solid.remove", bodies=[b]), box(b, 1148, 1152, 96, 120, 256, 304), box(b + "_F", 1152, 1166, 116, 120, 256, 304),
         C("solid.combine", target=b, tools=[b + "_F"], operation="join"),
         cyl(6.6, [1147, 108, 280], 6, X, op="cut", tg=[b])]
    for occ, oz, nz in (("CB5-16_M08_PY:46", 273.0, 261.0), ("CB5-16_M08_PY:47", 287.0, 299.0)):
        s += bolt_move(occ, [1159, 116, oz], [1159, 116, nz], Y, b, 4, tap=12.0, tag=b)
    s += [C("material.assign", bodies=[b], material="A5052"), C("component.move_bodies", bodies=[b], component=b)]
    st["5_AIR"] = s
    FIX[b] = [1148, 1166, 96, 120, 256, 304]
    # --- 6 CST_V 다시 그림: 띠 폭 13 -> 30 (Y -159~-129, t4, 외팔 강도), 가로판 L Z338~342 그대로(폭 Y -164~-127, FEED_A는 r6 여유 구멍), U Z518~522 -> 530~534(띠 위끝 Z530 -> 536)
    #     (FEED_A Z343 꺾임 원호 끝 Z347.7, FEED_B Z505 꺾임 원호가 옛 판 두께 안 — 통구멍 블록 조건 PNEU01-E03 (가) 옮김)
    b = "P_M08_TUBE_BRKT_CST_V"
    condv = lambda p, n: F.U7C(n) and p[0] >= 95
    s = [C("solid.remove", bodies=[b]), box(b, 58, 62, -159, -129, 296, 536),
         box(b + "_L", 62, 146, -164, -127, 338, 342), box(b + "_U", 62, 146, -160, -127, 530, 534),
         C("solid.combine", target=b, tools=[b + "_L", b + "_U"], operation="join")]
    # 아래 판 Z340: CUT·TUCK 4줄만 잡고 FEED_A(Z343 꺾임 원호가 판 두께 안)는 r6 여유 구멍으로 지나게 한다(잡지 않음)
    s += tube_holes(b, 2, 340, 4, lambda p, n: condv(p, n) and "FEED" not in n, HOLES) + tube_holes(b, 2, 532, 4, condv, HOLES)
    s.append(cyl(6.0, [104.0, -153.5, 336.0], 8.0, [0, 0, 1], op="cut", tg=[b]))
    for z in (304, 320):   # 볼트 CB5-16_M05_1_PNEU01_52·53 자리 그대로(카세트 판 탭 그대로)
        s.append(cyl(2.75, [62.5, -152.5, z], 5.0, [-1, 0, 0], op="cut", tg=[b]))
    s += [C("material.assign", bodies=[b], material="A5052"), C("component.move_bodies", bodies=[b], component=b),
          C("component.metadata.set", component=b, part_number=b, bom_type="normal",
            description="Cassette vertical-leg tube comb, A5052 t4 sheet: strap 30 wide + 2 flanges Z340/532 (laser + 2 bends, same side), 2x CB5-16")]
    st["6_CSTV"] = s
    FIX[b] = [58, 146, -160, -127, 296, 536]
    return st


def tubes():
    s = []
    for nm, (pts, R, r) in BNEW.items():
        k = len(pts)  # 위 토막 그대로(이음점 Z 736에서 끝남)
        cmds = G.tube_cmds(nm, pts, R, r)
        cmds[0]["params"]["name"] = "SK_" + nm + "_F3"
        cmds[-1]["params"]["path_sketch"] = "SK_" + nm + "_F3"
        s += [C("solid.remove", bodies=[nm])] + cmds + [C("material.assign", bodies=[nm], material="Default"),
                                                       C("component.move_bodies", bodies=[nm], component=nm)]
    return s


def taps():
    """보(강 각관) 탭: 옛 자리는 r2.4 원기둥 join으로 하나씩 메우고(여러 개 한 번에 union은 커널 실패), 새 자리는 하나씩 cut."""
    s = []
    for b, h, d in TAPFILL:
        s.append(cyl(2.4, b, h + 0.5, d, op="join", tg=[BEAM]))
    for b, h, d in TAPNEW:
        s.append(cyl(2.1, b, h, d, op="cut", tg=[BEAM]))
    return s


if __name__ == "__main__":
    st = {"T_tubes": tubes()}
    st.update(fixtures())
    st["Z_taps"] = taps()
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, "stage_%s.json" % k), "w", encoding="utf8"), ensure_ascii=False)
        print(k, len(v))
    json.dump({"holes": HOLES, "fixtures": FIX, "bolts": BOLTS, "tapfill": TAPFILL, "tapnew": TAPNEW,
               "tubes": {n: {"pts": v[0], "R": v[1], "len": TLD["tubes"][n]["len"]} for n, v in BNEW.items()}},
              open(os.path.join(OUT, "fixlog2.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for b, v in HOLES.items():
        print(b, len(v), [(h["tube"][-8:], [round(x, 1) for x in h["at"]]) for h in v])
