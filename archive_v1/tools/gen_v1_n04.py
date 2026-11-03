# -*- coding: utf-8 -*-
"""N04 U5 에어 테이블 생성기 — v1.0.11 -> v1.0.12 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_N04_select.md 8절(N04-S)과 부서 지시문을 그린다.
python -B tools/gen_v1_n04.py -> tools/out/mech_N04/model/stage_*.json (MCP batch로 차례로 보냄), edit.json, edit_meta.json
좌표: 바늘점 원점 월드 mm, REST(J_U4_X 0·J_U4_Y 0, 원판 중심 -900, -400)에서 루트에 그리고,
모든 자르기를 마친 뒤 component.move_bodies로 유닛 컴포넌트에 옮긴다(움직이는 컴포넌트 안 바디를 루트 자르기로
고치면 조인트를 움직였을 때 자르기가 따라가지 않는다 — 이 부서 시험에서 확인).
- 사슬 슬랫·솔 털·정하중 스프링·호스는 그리지 않는다(선정 8절, E-10).
- HFS8-4080-248은 STEP이 없다 -> STEP대기_ 상자 + T홈(열림 8·안쪽 16·깊이 9.5) + 중심 구멍 Ø7 ×2(HFS8-4080-460 단면 근사).
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N04")

PANEL, NECK = "P_N04_PANEL", "P_N04_NECK"
POSTS = [("STEP대기_HFS8-4080-248_%d" % (i + 1), xc, yc) for i, (xc, yc) in
         enumerate([(-1030, 940), (-770, 940), (-1030, -940), (-770, -940)])]
STP, STN, STA = "P_N04_STORE_P", "P_N04_STORE_N", "P_N04_STORE_A"
CYP, CYN, CYA = "STEP대기_CDJ2B16-110_P", "STEP대기_CDJ2B16-110_N", "STEP대기_CDJ2B16-150_A"
CBP, CBN, CBA = "P_N04_CYLBKT_P", "P_N04_CYLBKT_N", "P_N04_CYLBKT_A"
PINS = ["P_N04_PIN_%d" % i for i in range(1, 5)]
INLET = "P_N04_INLET"
SADDLE = "P_N04_SADDLE"
DRN, DRP = "P_N04_WIND_N_DRUM", "P_N04_WIND_P_DRUM"
WBN, WBP = "P_N04_WIND_N_BKT", "P_N04_WIND_P_BKT"
TAIL, TBKT = "P_N04_TAIL", "P_N04_TAIL_BKT"
BLOW, BBASE = "STEP대기_VB-004-E2", "P_N04_BLOWER_BASE"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4),
         "corner": [x0, y0, z0], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cut(tg, x0, x1, y0, y1, z0, z1):
    return box(None, x0, x1, y0, y1, z0, z1, "cut", [tg])


def cyl(r, h, base, axis="Z", op="new", name=None, tg=None):
    p = {"radius": r, "height": h, "base": [round(v, 4) for v in base], "axis": axis, "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.cylinder", **p)


# ---------------- stage 1: 지우기·재질 만들기 ----------------
def stage_prep():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("solid.remove", bodies=["U5_TABLE", "U5_POST_1", "U5_POST_2", "U5_POST_3", "U5_POST_4"]),
            C("material.create", name="A5052_HC", density_g_cm3=0.19, color="#c2c6cc"),
            C("material.create", name="A6061", density_g_cm3=2.70, color="#cfd3d8"),
            C("material.create", name="A6063", density_g_cm3=2.69, color="#d8dbe0"),
            C("material.create", name="PA12", density_g_cm3=1.01, color="#4a4a4a")]


# ---------------- stage 2: 판(허니컴 h38 + 표피 1+1) ----------------
def stage_panel():
    P = PANEL
    st = [box(P, -2010, 210, -1545, 1560, -40, 0)]
    st += [cut(P, -970, -830, -915, 915, -5, 1),            # 원판 홈 위
           cut(P, -964, -836, -895, 895, -41, -5),          # 원판 홈 아래(턱 6)
           cut(P, -970, -830, 895, 915, -41, -5),           # 꺾임 통로 +Y
           cut(P, -970, -830, -915, -895, -41, -5),         # 꺾임 통로 -Y
           cut(P, -1292.5, 211, -55, 55, -5, 1),            # 바늘 홈 위(+X 끝 열림)
           cut(P, -970, 211, -55, 55, -41, -5),             # 바늘 홈 아래 C·+X 구간 ±55
           cut(P, -1292.5, -970, -51, 51, -41, -5),         # A 구간 아래 ±51(턱 4)
           cut(P, -762.5, 211, -530, -390, -41, 1),         # 기둥 홈(+X 끝 열림)
           cut(P, -830, 211, 55, 64, -8, 1),                # 솔 주머니 4
           cut(P, -830, 211, -64, -55, -8, 1),
           cut(P, -762.5, 211, -539, -530, -8, 1),
           cut(P, -762.5, 211, -390, -381, -8, 1),
           cut(P, -830, -762.5, -530, -390, -39, -1),       # 목 인서트 주머니
           cyl(23, 2, (-1023, 1040, -41), op="cut", tg=[P])]  # 송풍 입구 밑 표피 Ø46
    st.append(box(NECK, -830, -762.5, -530, -390, -39, -1))
    return st


# ---------------- stage 3: 기둥 STEP대기_HFS8-4080-248 ×4 ----------------
def stage_posts():
    st = []
    z0, z1 = -288, -40
    for nm, xc, yc in POSTS:
        st.append(box(nm, xc - 20, xc + 20, yc - 40, yc + 40, z0, z1))
        for sx in (-1, 1):            # X 면 T홈 2개씩(Y ±20)
            f = xc + 20 * sx
            for dy in (-20, 20):
                y = yc + dy
                st.append(cut(nm, min(f + sx, f - 2.5 * sx), max(f + sx, f - 2.5 * sx), y - 4, y + 4, z0 - 1, z1 + 1))
                st.append(cut(nm, min(f - 2.5 * sx, f - 9.5 * sx), max(f - 2.5 * sx, f - 9.5 * sx), y - 8, y + 8, z0 - 1, z1 + 1))
        for sy in (-1, 1):            # Y 면 T홈 1개씩(X 가운데)
            f = yc + 40 * sy
            st.append(cut(nm, xc - 4, xc + 4, min(f + sy, f - 2.5 * sy), max(f + sy, f - 2.5 * sy), z0 - 1, z1 + 1))
            st.append(cut(nm, xc - 8, xc + 8, min(f - 2.5 * sy, f - 9.5 * sy), max(f - 2.5 * sy, f - 9.5 * sy), z0 - 1, z1 + 1))
        for dy in (-20, 20):
            st.append(cyl(3.5, 250, (xc, yc + dy, z0 - 1), op="cut", tg=[nm]))
    return st


# ---------------- stage 4: 판 밑(보관 안내·실린더·받침·멈춤 블록·입구) ----------------
def store_y(nm, y0, y1):
    """바깥 사슬 보관 안내 2층(SUS t1.5): 옆벽 X -966~-964.5·-835.5~-834(Z -125~-40), 바닥 -125~-123.5, 위층 턱 Z -81.5~-80 폭 10."""
    return [box(nm, -966, -834, y0, y1, -125, -40),
            cut(nm, -954.5, -845.5, y0 - 1, y1 + 1, -123.5, -39),
            cut(nm, -964.5, -835.5, y0 - 1, y1 + 1, -123.5, -81.5),
            cut(nm, -964.5, -835.5, y0 - 1, y1 + 1, -80, -39)]


def stage_under():
    st = store_y(STP, 930, 1530) + store_y(STN, -1530, -930)
    # A 사슬 보관(SUS t1.5): 옆벽 Y ±(54.5~56)·Z -200~-40, 바닥 -200~-198.5, 턱 Z -123.5~-122 폭 10
    st += [box(STA, -2000, -1310, -56, 56, -200, -40),
           cut(STA, -2001, -1309, -44.5, 44.5, -198.5, -39),
           cut(STA, -2001, -1309, -54.5, 54.5, -198.5, -123.5),
           cut(STA, -2001, -1309, -54.5, 54.5, -122, -39)]
    # 꼬리 멈춤 실린더 임시 형상(몸 Ø20, 로드 Ø5)
    st += [cyl(10, 140, (-900, 1393, -112), "Y", name=CYP), cyl(2.5, 13, (-900, 1381, -112), "Y", "join", tg=[CYP]),
           cyl(10, 140, (-900, -1533, -112), "Y", name=CYN), cyl(2.5, 13, (-900, -1394, -112), "Y", "join", tg=[CYN]),
           cyl(10, 180, (-2000, 0, -180), "X", name=CYA), cyl(2.5, 13, (-1821, 0, -180), "X", "join", tg=[CYA])]
    # 실린더 받침 L(SUS t2): 세운 판 + 판 밑면에 닿는 위 날개
    st += [box(CBP, -925, -875, 1533, 1545, -125, -40), cut(CBP, -926, -874, 1535, 1546, -126, -42),
           box(CBN, -925, -875, -1545, -1533, -125, -40), cut(CBN, -926, -874, -1546, -1535, -126, -42),
           box(CBA, -2010, -2000, -20, 20, -192, -40), cut(CBA, -2011, -2002, -21, 21, -193, -42)]
    # 안쪽 사슬 끝 막대 멈춤 블록(SUS304) — 원판 홈 아래 턱 위. 위 Z -3(안장 밑면 -2와 1, 3절)
    k = 0
    for (x0, x1) in ((-970, -964), (-836, -830)):
        for (y0, y1) in ((57, 67), (-67, -57)):
            st.append(box(PINS[k], x0, x1, y0, y1, -5, -3))
            k += 1
    # 송풍 입구(PA12 출력): 관 OD46/ID38, Z -55~-39(위 1은 밑 표피 Ø46 구멍에 끼움)
    st += [cyl(23, 16, (-1023, 1040, -55), name=INLET), cyl(19, 18, (-1023, 1040, -56), op="cut", tg=[INLET])]
    return st


# ---------------- stage 5: U4_Y(안장·감개) ----------------
def wind(drum, bkt, s):
    """s = -1(-Y 쪽, 드럼 중심 Y -510) / +1(+Y 쪽, -290). 원판 중심 Y -400 기준 거울."""
    m = lambda y: -800 - y if s > 0 else y          # -Y 쪽 좌표를 +Y 쪽으로 거울
    yy = lambda a, b: sorted((m(a), m(b)))
    st = [cyl(35, 124, (-962, m(-510), -80), "X", name=drum), cyl(32, 126, (-963, m(-510), -80), "X", "cut", tg=[drum])]
    y0, y1 = yy(-475, -471.5)
    st.append(box(bkt, -960, -840, y0, y1, -131, -129.5))                       # 발(FRAME 윗면)
    y0, y1 = yy(-473.5, -472)
    st.append(box(None, -963, -837, y0, y1, -130, -50, "join", [bkt]))          # 세운 판
    y0, y1 = yy(-545, -472.5)
    st.append(box(None, -964, -962.5, y0, y1, -115, -45, "join", [bkt]))        # 볼 2(드럼 축 받침)
    st.append(box(None, -837.5, -836, y0, y1, -115, -45, "join", [bkt]))
    return st


def stage_y():
    st = [box(SADDLE, -966, -834, -470, -330, -131, 0),
          cut(SADDLE, -967, -833, -466, -334, -132, -2),
          cut(SADDLE, -967, -915, -471, -329, -132, -2),
          cut(SADDLE, -885, -833, -471, -329, -132, -2),
          cyl(63, 4, (-900, -400, -3), op="cut", tg=[SADDLE])]
    st += wind(DRN, WBN, -1) + wind(DRP, WBP, 1)
    return st


# ---------------- stage 6: U1_HEAD(꼬리판·받침) + 바닥(블로어) ----------------
def stage_fix():
    return [box(TAIL, -30, 385, -52, 52, -3, 0), cut(TAIL, -31, 30, -46, 46, -4, 1),
            box(TBKT, 60, 360, -40, 40, -60, -3), cut(TBKT, 59, 361, -37, 37, -61, -6),
            box(BLOW, -600, -300, 1600, 1890, -900, -610),
            box(BBASE, -620, -280, 1580, 1910, -903, -900)]


U5_B = [PANEL, NECK] + [p[0] for p in POSTS] + [STP, STN, STA, CYP, CYN, CYA, CBP, CBN, CBA] + PINS + [INLET]
Y_B = [SADDLE, DRN, DRP, WBN, WBP]
H_B = [TAIL, TBKT]
F_B = [BLOW, BBASE]


def stage_assign():
    return [
        C("material.assign", bodies=[PANEL], material="A5052_HC"),
        C("material.assign", bodies=[NECK], material="A6061"),
        C("material.assign", bodies=[p[0] for p in POSTS] + [DRN, DRP], material="A6063"),
        C("material.assign", bodies=[STP, STN, STA, CBP, CBN, CBA, SADDLE, WBN, WBP, TAIL, TBKT] + PINS, material="SUS304"),
        C("material.assign", bodies=[CYP, CYN, CYA], material="Stainless Steel"),
        C("material.assign", bodies=[INLET], material="PA12"),
        C("material.assign", bodies=[BLOW], material="Aluminum"),
        C("material.assign", bodies=[BBASE], material="SS400"),
        C("component.move_bodies", bodies=U5_B, component="U5_AIRTABLE"),
        C("component.move_bodies", bodies=Y_B, component="U4_Y"),
        C("component.move_bodies", bodies=H_B, component="U1_HEAD"),
        C("component.move_bodies", bodies=F_B, component="U2_BRIDGE"),
        C("document.metadata.set", key="description",
          value="N04 mechanism: U5 air table, honeycomb panel 3 grooves, chain stores, CDJ2B16 tail stops x3, saddle, tail plate, ring blower"),
        C("motion.play", study="REST", step=0, quiet=True)]


STAGES = [("prep", stage_prep), ("panel", stage_panel), ("posts", stage_posts), ("under", stage_under),
          ("y", stage_y), ("fix", stage_fix), ("assign", stage_assign)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.11.sc", "result": "3D_Modeling/FSAP_v1.0.12.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"U5_AIRTABLE": U5_B, "U4_Y": Y_B, "U1_HEAD": H_B, "U2_BRIDGE": F_B},
              open(os.path.join(OUT, "model", "new_bodies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc))


if __name__ == "__main__":
    main()
