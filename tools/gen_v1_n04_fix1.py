# -*- coding: utf-8 -*-
"""N04 수정 1회차 생성기 — v1.0.12 -> v1.0.14 (v1.0.13은 중간 저장, 점검에서 2건 고쳐 v1.0.14) (모델링부 2026-11-03, 엔진 v3.7.2)
검도 P1·P2, 해석 받침 3건(CYLBKT_P/N t4, CYLBKT_A 통 블록, 안장 다리 100), PM 예외 판정 N04-E01·E03(사슬 앞끝 바디 +
슬라이더, 꼬리 멈춤 로드 슬라이더). 그리기는 gen_v1_n04.py와 같은 방식: REST(J 0)에서 루트에 그리고 자르기를 끝낸 뒤
component.move_bodies로 옮긴다(움직이는 컴포넌트 안 바디를 루트 자르기로 고치면 자르기가 월드에 남음).
고칠 바디는 지우고 새로 그린다(판·보관 3·실린더 3·받침 3·멈춤 블록 4·안장).
python -X utf8 -B tools/gen_v1_n04_fix1.py -> tools/out/mech_N04/model1/stage_*.json, tools/out/mech_N04/edit.json
연구 키는 tools/gen_N04_chain_keys.py(stage_keys.json)가 만든다.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_v1_n04 import C, box, cut, cyl, PANEL, STP, STN, STA, CYP, CYN, CYA, CBP, CBN, CBA, PINS, SADDLE

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N04")
M1 = os.path.join(OUT, "model1")
KEYS = json.load(open(os.path.join(M1, "chain_keys.json"), encoding="utf-8"))
LP, LN, LA = KEYS["L_f"]["P"], KEYS["L_f"]["N"], KEYS["L_f"]["A"]

HP, HN, HA = "P_N04_CHAIN_P_HEAD", "P_N04_CHAIN_N_HEAD", "P_N04_CHAIN_A_HEAD"
TNP, TPN = "P_N04_CHAIN_NP_TAIL", "P_N04_CHAIN_PN_TAIL"      # 안쪽 사슬 N+·P- 드럼 쪽 끝 구간(U4_Y)
RP, RN, RA = "STEP대기_CDJ2B16-110_P_ROD", "STEP대기_CDJ2B16-110_N_ROD", "STEP대기_CDJ2B16-150_A_ROD"
PDP, PDN, PDA = "P_N04_STOP_PAD_P", "P_N04_STOP_PAD_N", "P_N04_STOP_PAD_A"
REMOVE = [PANEL, STP, STN, STA, CYP, CYN, CYA, CBP, CBN, CBA] + PINS + [SADDLE]


def stage_remove():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("solid.remove", bodies=REMOVE)]


def stage_panel():
    P = PANEL
    return [box(P, -2010, 210, -1545, 1560, -40, 0),
            cut(P, -970, -830, -915, 915, -5, 1),            # 원판 홈 위
            cut(P, -964, -836, -895, 895, -41, -5),          # 원판 홈 아래(턱 6)
            cut(P, -970, -830, 895, 915, -41, -5),           # 꺾임 통로 +Y
            cut(P, -970, -830, -915, -895, -41, -5),         # 꺾임 통로 -Y
            cut(P, -1292.5, 211, -55, 55, -5, 1),            # 바늘 홈 위(+X 끝 열림)
            cut(P, -970, 211, -55, 55, -41, -5),             # 바늘 홈 아래 C·+X 구간 ±55
            cut(P, -1272.5, -970, -51, 51, -41, -5),         # A 구간 아래 ±51(턱 4)
            cut(P, -1292.5, -1272.5, -55, 55, -41, -5),      # P2: A 사슬 꺾임 통로(판 관통)
            cut(P, -762.5, 211, -530, -390, -41, 1),         # 기둥 홈(+X 끝 열림)
            cut(P, -830, 211, 55, 64, -8, 1),                # 솔 주머니 4
            cut(P, -830, 211, -64, -55, -8, 1),
            cut(P, -762.5, 211, -539, -530, -8, 1),
            cut(P, -762.5, 211, -390, -381, -8, 1),
            cut(P, -830, -762.5, -530, -390, -39, -1),       # 목 인서트 주머니
            cyl(23, 2, (-1023, 1040, -41), op="cut", tg=[P])]


def store_y(nm, y0, y1):
    """P1: 바깥 X -970~-830, 옆벽 t1.5, 안쪽 137(사슬 132와 2.5씩), 위층 턱 폭 10 Z -81.5~-80, 바닥 -125~-123.5."""
    return [box(nm, -970, -830, y0, y1, -125, -40),
            cut(nm, -958.5, -841.5, y0 - 1, y1 + 1, -123.5, -39),
            cut(nm, -968.5, -831.5, y0 - 1, y1 + 1, -123.5, -81.5),
            cut(nm, -968.5, -831.5, y0 - 1, y1 + 1, -80, -39)]


def stage_under():
    st = store_y(STP, 930, 1530) + store_y(STN, -1530, -930)
    # P2: A 보관 X -2000~-1272.5(통로 바로 밑)
    st += [box(STA, -2000, -1272.5, -56, 56, -200, -40),
           cut(STA, -2001, -1271.5, -44.5, 44.5, -198.5, -39),
           cut(STA, -2001, -1271.5, -54.5, 54.5, -198.5, -123.5),
           cut(STA, -2001, -1271.5, -54.5, 54.5, -122, -39),
           cut(STA, -1278, -1271.5, -57, 57, -201, -172)]   # Y 케이블 베어 STEP대기_2400.05.075.0(X -1277~, Z -358~-173)와 1 띄움(v1.0.14)
    # 실린더 몸(로드 구멍 Ø6) — 로드는 따로(U5_STOP_*)
    st += [cyl(10, 140, (-900, 1393, -112), "Y", name=CYP), cyl(3, 113, (-900, 1392, -112), "Y", "cut", tg=[CYP]),
           cyl(10, 140, (-900, -1533, -112), "Y", name=CYN), cyl(3, 113, (-900, -1505, -112), "Y", "cut", tg=[CYN]),
           cyl(10, 180, (-2000, 0, -180), "X", name=CYA), cyl(3, 153, (-1972, 0, -180), "X", "cut", tg=[CYA])]
    # 받침: P/N SUS304 t4 L(세운 판 Y 1533~1537, 날개 8), A 통 블록 t8 + 받침판 60
    st += [box(CBP, -925, -875, 1533, 1545, -125, -40), cut(CBP, -926, -874, 1537, 1546, -126, -44),
           box(CBN, -925, -875, -1545, -1533, -125, -40), cut(CBN, -926, -874, -1546, -1537, -126, -44),
           box(CBA, -2010, -1950, -20, 20, -192, -40), cut(CBA, -2011, -2008, -21, 21, -193, -44),
           cut(CBA, -2000, -1949, -21, 21, -193, -44)]
    # 안쪽 사슬 끝 막대 멈춤 블록: 바깥 사슬(X -966~-834) 밖으로 좁힘 4×10×2
    k = 0
    for (x0, x1) in ((-970, -966), (-834, -830)):
        for (y0, y1) in ((57, 67), (-67, -57)):
            st.append(box(PINS[k], x0, x1, y0, y1, -5, -3))
            k += 1
    return st


def stage_y():
    """안장: 다리 X -950~-850(폭 100) t4. 안쪽 사슬 드럼 쪽 끝 구간(드럼 윗면 접선 -> 안장 끝) Z -45~-40."""
    return [box(SADDLE, -966, -834, -470, -330, -131, 0),
            cut(SADDLE, -967, -833, -466, -334, -132, -2),
            cut(SADDLE, -967, -950, -471, -329, -132, -2),
            cut(SADDLE, -850, -833, -471, -329, -132, -2),
            cyl(63, 4, (-900, -400, -3), op="cut", tg=[SADDLE]),
            box(TNP, -962, -838, -510, -471, -45, -40),
            box(TPN, -962, -838, -329, -290, -45, -40)]


def stage_heads():
    """사슬 앞끝(끝 막대 + 앞 고정 길이) REST 자세 좌표, 로드·패드(내민 0 = 13 돌출)."""
    return [box(HP, -966, -834, -55, -55 + LP, -5, 0),
            box(HN, -966, -834, -470.5 - LN, -470.5, -5, 0),
            box(HA, -970 - LA, -970, -54, 54, -5, 0),
            cyl(2.5, 123, (-900, 1381, -112), "Y", name=RP), cyl(8, 3, (-900, 1378, -112), "Y", name=PDP),
            cyl(2.5, 123, (-900, -1504, -112), "Y", name=RN), cyl(8, 3, (-900, -1381, -112), "Y", name=PDN),
            cyl(2.5, 163, (-1971, 0, -180), "X", name=RA), cyl(8, 3, (-1808, 0, -180), "X", name=PDA)]


U5_B = [PANEL, STP, STN, STA, CYP, CYN, CYA, CBP, CBN, CBA] + PINS
COMPS = [("U5_CHAIN_P", [HP]), ("U5_CHAIN_N", [HN]), ("U5_CHAIN_A", [HA]),
         ("U5_STOP_P", [RP, PDP]), ("U5_STOP_N", [RN, PDN]), ("U5_STOP_A", [RA, PDA])]
#            name, comp, point, axis z, limits
JOINTS = [("J_N04_CH_P", "U5_CHAIN_P", [-900, -55, -5], [0, 1, 0], [0, 913 - LP + 55]),
          ("J_N04_CH_N", "U5_CHAIN_N", [-900, -470.5, -5], [0, 1, 0], [-913 + LN + 470.5, 525.5]),
          ("J_N04_CH_A", "U5_CHAIN_A", [-970, 0, -5], [1, 0, 0], [-1290.5 + LA + 970, 139]),
          ("J_N04_STOP_P", "U5_STOP_P", [-900, 1381, -112], [0, -1, 0], [0, 110]),
          ("J_N04_STOP_N", "U5_STOP_N", [-900, -1381, -112], [0, 1, 0], [0, 110]),
          ("J_N04_STOP_A", "U5_STOP_A", [-1808, 0, -180], [1, 0, 0], [0, 150])]


def stage_assign():
    st = [C("material.assign", bodies=[PANEL], material="A5052_HC"),
          C("material.assign", bodies=[STP, STN, STA, CBP, CBN, CBA, SADDLE, PDP, PDN, PDA] + PINS, material="SUS304"),
          C("material.assign", bodies=[CYP, CYN, CYA, RP, RN, RA], material="Stainless Steel"),
          C("material.assign", bodies=[HP, HN, HA, TNP, TPN], material="A6063"),
          C("component.move_bodies", bodies=U5_B, component="U5_AIRTABLE"),
          C("component.move_bodies", bodies=[SADDLE, TNP, TPN], component="U4_Y")]
    for nm, bodies in COMPS:
        st += [C("component.create", name=nm, parent="root", activate=False),
               C("component.move_bodies", bodies=bodies, component=nm)]
    for jn, comp, pt, z, lim in JOINTS:
        st.append(C("joint.create", type="slider", name=jn, flip=True, limits=[lim], quiet=True,
                    a={"occurrence": "U5_AIRTABLE", "point": pt, "z": z},
                    b={"occurrence": comp, "point": pt, "z": z}))
    return st


STAGES = [("remove", stage_remove), ("panel", stage_panel), ("under", stage_under), ("y", stage_y),
          ("heads", stage_heads), ("assign", stage_assign)]


def main():
    os.makedirs(M1, exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(M1, "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"), ensure_ascii=False)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    keys = json.load(open(os.path.join(M1, "stage_keys.json"), encoding="utf-8"))
    fin = [C("document.metadata.set", key="description",
             value="N04 fix1: chain head sliders and tail-stop rod sliders, wider outer stores, A chain passage, stiffer cylinder brackets, wide saddle legs"),
           C("motion.play", study="REST", step=0, quiet=True)]
    json.dump(fin, open(os.path.join(M1, "stage_8_final.json"), "w", encoding="utf-8"), ensure_ascii=False)
    allc += keys + fin
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.12.sc", "result": "3D_Modeling/FSAP_v1.0.14.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    new = {"U5_AIRTABLE": U5_B, "U4_Y": [SADDLE, TNP, TPN]}
    new.update({c: b for c, b in COMPS})
    json.dump({"removed_recreated": REMOVE, "bodies": new, "L_f": KEYS["L_f"],
               "joints": [{"name": j[0], "comp": j[1], "point": j[2], "z": j[3], "limits": j[4]} for j in JOINTS]},
              open(os.path.join(M1, "new_bodies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc))


if __name__ == "__main__":
    main()
