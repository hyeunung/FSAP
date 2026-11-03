# -*- coding: utf-8 -*-
"""N04 수정 2회차 형상 생성기 (모델링부 2026-11-03, v1.0.14 -> v1.0.15)
고침: 검도 N04-F06(바깥 사슬 보관 길이) + PM 판정 N04-E05·E07(안쪽 사슬 끝 막대 바디 + Y 슬라이더)
 - 보관 P/N: U턴 2층(위층 턱 Y 1430~1528 없앰, 끝벽 Y 1528.5~1530), +X 옆벽에 꼬리 러그 홈(위층·U턴·아래층)
 - 꼬리 멈춤 CDJ2B16-110 P/N: 보관 밖 옆(X -828~-808, Z -79~-59, 축 Y), 몸 Y 779~919 / -919~-779, 로드가 +Y(P)/-Y(N)로 꼬리 러그를 민다
 - 받침 P_N04_CYLBKT_P/_N: SUS304 t4 L, Y 767~779 / -779~-767
 - 바깥 앞끝 P/N: 길이 L_f 76.5 (앞끝 식 Yc +- 81.5, 하드 리밋 J_U4_Y 1155/-355 포함)
 - 안쪽 끝 막대 NP/PN: 바디 + U5_BAR_NP/_PN + J_N04_BAR_NP/_PN, 막대 끝 러그가 판 +X 벽 홈(끝 Y 67 / -66.5)에 걸려 멈춤
 - 멈춤 블록 PIN_3/4 X -834~-832 (PN 러그와 0.5)
출력: tools/out/mech_N04/model2/stage_*.json (MCP batch 순서대로)
python -X utf8 -B tools/gen_v1_n04_fix2.py
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N04", "model2")


def C(c, **p):
    return {"command": c, "params": p}


def box(name, x0, x1, y0, y1, z0, z1, op="new", targets=None):
    p = dict(length=round(x1 - x0, 3), width=round(y1 - y0, 3), height=round(z1 - z0, 3),
             corner=[x0, y0, z0], operation=op)
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = targets
    return C("solid.box", **p)


def ym(y0, y1, s):
    return (y0, y1) if s > 0 else (-y1, -y0)


def store(s):
    n = "P_N04_STORE_P" if s > 0 else "P_N04_STORE_N"
    c = [box(n, -970, -830, *ym(930, 1530, s), -125, -40)]
    t = [n]
    c.append(box(None, -958.5, -841.5, *ym(929, 1528.5, s), -123.5, -39, "cut", t))
    c.append(box(None, -968.5, -831.5, *ym(929, 1528.5, s), -123.5, -81.5, "cut", t))
    c.append(box(None, -968.5, -831.5, *ym(929, 1528.5, s), -80, -39, "cut", t))
    c.append(box(None, -968.5, -831.5, *ym(1430, 1528.5, s), -81.6, -79.9, "cut", t))   # U턴: 턱 없앰
    # +X 옆벽 꼬리 러그 홈
    c.append(box(None, -832, -829.5, *ym(933, 1528.5, s), -79.5, -75.5, "cut", t))     # 위층
    c.append(box(None, -832, -829.5, *ym(1478, 1528.5, s), -123, -75.5, "cut", t))     # U턴
    c.append(box(None, -832, -829.5, *ym(1280, 1528.5, s), -123, -119, "cut", t))      # 아래층
    return c


def cyl(s):
    t = "P" if s > 0 else "N"
    body = "STEP대기_CDJ2B16-110_" + t
    c = [C("solid.cylinder", radius=10, height=140, base=[-818, 779 if s > 0 else -919, -69], axis="Y",
           operation="new", body_name=body),
         C("solid.cylinder", radius=3, height=114, base=[-818, 806 if s > 0 else -920, -69], axis="Y",
           operation="cut", targets=[body]),
         C("solid.cylinder", radius=2.5, height=123, base=[-818, 809 if s > 0 else -932, -69], axis="Y",
           operation="new", body_name=body + "_ROD"),
         box("P_N04_STOP_PAD_" + t, -829.5, -813, *ym(932, 936, s), -79, -63)]
    k = "P_N04_CYLBKT_" + t
    c.append(box(k, -830, -806, *ym(767, 779, s), -81, -40))
    c.append(box(None, -831, -805, *ym(766, 775, s), -82, -44, "cut", [k]))
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    rem = ["P_N04_STORE_P", "P_N04_STORE_N", "STEP대기_CDJ2B16-110_P", "STEP대기_CDJ2B16-110_N",
           "STEP대기_CDJ2B16-110_P_ROD", "STEP대기_CDJ2B16-110_N_ROD", "P_N04_STOP_PAD_P", "P_N04_STOP_PAD_N",
           "P_N04_CYLBKT_P", "P_N04_CYLBKT_N", "P_N04_PIN_3", "P_N04_PIN_4",
           "P_N04_CHAIN_P_HEAD", "P_N04_CHAIN_N_HEAD"]
    st1 = [C("motion.play", study="REST", step=0, quiet=True),
           C("joint.delete", joint="J_N04_STOP_P"), C("joint.delete", joint="J_N04_STOP_N"),
           C("solid.remove", bodies=rem)]
    st2 = store(1) + store(-1) + cyl(1) + cyl(-1)
    st2 += [box("P_N04_PIN_3", -834, -832, 57, 67, -5, -3), box("P_N04_PIN_4", -834, -832, -67, -57, -5, -3)]
    # 판 +X 벽 막대 러그 홈 (NP: Z -3~0, 끝 Y 67 / PN: Z -5~-3, 끝 Y -66.5)
    st2 += [box(None, -830, -828.5, -850, 67, -3, 0.5, "cut", ["P_N04_PANEL", "P_N04_NECK"]),
            box(None, -830, -828.5, -66.5, 850, -5, -3, "cut", ["P_N04_PANEL"])]
    # 바깥 앞끝(L_f 76.5) + 막대
    st2 += [box("P_N04_CHAIN_P_HEAD", -966, -834, -55, 21.5, -5, 0),
            box("P_N04_CHAIN_N_HEAD", -966, -834, -558, -481.5, -5, 0),
            box("P_N04_CHAIN_NP_BAR", -969, -829, 57, 67, -3, 0),
            box("P_N04_CHAIN_PN_BAR", -969, -831, -67, -57, -3, 0),
            box(None, -831.5, -829, -66.5, -57.5, -5, -3, "join", ["P_N04_CHAIN_PN_BAR"])]
    st3 = [C("material.assign", bodies=["P_N04_STORE_P", "P_N04_STORE_N", "P_N04_STOP_PAD_P", "P_N04_STOP_PAD_N",
                                        "P_N04_CYLBKT_P", "P_N04_CYLBKT_N", "P_N04_PIN_3", "P_N04_PIN_4"], material="SUS304"),
           C("material.assign", bodies=["STEP대기_CDJ2B16-110_P", "STEP대기_CDJ2B16-110_N",
                                        "STEP대기_CDJ2B16-110_P_ROD", "STEP대기_CDJ2B16-110_N_ROD"], material="Stainless Steel"),
           C("material.assign", bodies=["P_N04_CHAIN_P_HEAD", "P_N04_CHAIN_N_HEAD", "P_N04_CHAIN_NP_BAR",
                                        "P_N04_CHAIN_PN_BAR"], material="A6063"),
           C("component.move_bodies", bodies=["P_N04_STORE_P", "P_N04_STORE_N", "STEP대기_CDJ2B16-110_P",
                                              "STEP대기_CDJ2B16-110_N", "P_N04_CYLBKT_P", "P_N04_CYLBKT_N",
                                              "P_N04_PIN_3", "P_N04_PIN_4"], component="U5_AIRTABLE"),
           C("component.move_bodies", bodies=["STEP대기_CDJ2B16-110_P_ROD", "P_N04_STOP_PAD_P"], component="U5_STOP_P"),
           C("component.move_bodies", bodies=["STEP대기_CDJ2B16-110_N_ROD", "P_N04_STOP_PAD_N"], component="U5_STOP_N"),
           C("component.move_bodies", bodies=["P_N04_CHAIN_P_HEAD"], component="U5_CHAIN_P"),
           C("component.move_bodies", bodies=["P_N04_CHAIN_N_HEAD"], component="U5_CHAIN_N"),
           C("component.create", name="U5_BAR_NP", parent="root", activate=False),
           C("component.move_bodies", bodies=["P_N04_CHAIN_NP_BAR"], component="U5_BAR_NP"),
           C("component.create", name="U5_BAR_PN", parent="root", activate=False),
           C("component.move_bodies", bodies=["P_N04_CHAIN_PN_BAR"], component="U5_BAR_PN"),
           C("joint.create", type="slider", name="J_N04_STOP_P", flip=True, limits=[[0, 110]], quiet=True,
             a={"occurrence": "U5_AIRTABLE", "point": [-818, 932, -69], "z": [0, 1, 0]},
             b={"occurrence": "U5_STOP_P", "point": [-818, 932, -69], "z": [0, 1, 0]}),
           C("joint.create", type="slider", name="J_N04_STOP_N", flip=True, limits=[[0, 110]], quiet=True,
             a={"occurrence": "U5_AIRTABLE", "point": [-818, -932, -69], "z": [0, -1, 0]},
             b={"occurrence": "U5_STOP_N", "point": [-818, -932, -69], "z": [0, -1, 0]}),
           C("joint.create", type="slider", name="J_N04_BAR_NP", flip=True, limits=[[-893, 0]], quiet=True,
             a={"occurrence": "U5_AIRTABLE", "point": [-900, 62, -3], "z": [0, 1, 0]},
             b={"occurrence": "U5_BAR_NP", "point": [-900, 62, -3], "z": [0, 1, 0]}),
           C("joint.create", type="slider", name="J_N04_BAR_PN", flip=True, limits=[[0, 893]], quiet=True,
             a={"occurrence": "U5_AIRTABLE", "point": [-900, -62, -3], "z": [0, 1, 0]},
             b={"occurrence": "U5_BAR_PN", "point": [-900, -62, -3], "z": [0, 1, 0]}),
           C("joint.limits", joint="J_N04_CH_P", min=0, max=891.5),
           C("joint.limits", joint="J_N04_CH_N", min=-355, max=536.5),
           C("joint.list", **{})]
    for i, s in enumerate((st1, st2, st3), 1):
        json.dump(s, open(os.path.join(OUT, "stage_%d.json" % i), "w", encoding="utf-8"), ensure_ascii=False)
        print("stage", i, len(s))


if __name__ == "__main__":
    main()
