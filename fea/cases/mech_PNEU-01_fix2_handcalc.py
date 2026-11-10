# -*- coding: utf-8 -*-
"""PNEU-01 수정 2 손계산 — 형상·하중 경로가 바뀐 관 고정품(E-18). 해석 환경 없음(D-16) -> 손계산.
하중·기준은 수정 1 해석부와 같다(fea/cases/mech_PNEU-01_fea1_handcalc.py): A5052 항복 195 MPa, E 70 GPa,
운전 = 관 자중 x3 g + 압력 펴짐 힘 1줄, 오조작 = 관 1줄 손 당김 50 N(가장 먼 구멍, 가장 불리한 방향). 기준 SF 운전 3, 오조작 1.2(검도 1회차 기준).
치수는 생성기 tools/gen_v2_pneu01_fix2.py 상자 좌표(v2.8.8).
"""
import json, math
SY, E, G = 195.0, 70000.0, 9.81
F_MIS = 50.0
w0604 = math.pi / 4 * (6 ** 2 - 4 ** 2) * 1.2e-3
Fp0604 = 0.5 * math.pi / 4 * 4 ** 2


def wt(n, span=300.0):
    return n * w0604 * span / 1000 * G * 3


def sf(s):
    return round(SY / s, 2) if s > 0 else 999.0


R = {}


def sec(name, F_op, F_mis, L, Z, note, I=None):
    so, sm = F_op * L / Z, F_mis * L / Z
    R[name] = {"L_mm": L, "Z_mm3": round(Z, 1), "sigma_op_MPa": round(so, 2), "SF_op": sf(so), "sigma_mis_MPa": round(sm, 2),
               "SF_mis": sf(sm), "note": note}
    if I:
        R[name]["defl_op_mm"] = round(F_op * L ** 3 / (3 * E * I), 3)
        R[name]["defl_mis_mm"] = round(F_mis * L ** 3 / (3 * E * I), 3)


# 1) CST_V 세움 띠: t4 폭 30(Y -159~-129), 뿌리 = 카세트 판 윗끝 Z328, 윗 가로판 구멍 평면 Z532 -> L 204
F_op = wt(6) + Fp0604
b, t, L = 30.0, 4.0, 532.0 - 328.0
sec("CST_V_strip_X", F_op, F_MIS, L, b * t ** 2 / 6, "띠 두께 방향(+X, 판에서 떨어지는 쪽), 윗판 Z532", I=b * t ** 3 / 12)
sec("CST_V_strip_Y", F_op, F_MIS, L, t * b ** 2 / 6, "띠 폭 방향(Y)", I=t * b ** 3 / 12)
# 가로판 Z 하중(팔 84 -> 끝 구멍까지 80): 띠에 두께 방향 굽힘 F x 80
sec("CST_V_strip_Zload", F_op, F_MIS, 80.0, b * t ** 2 / 6, "가로판 끝 Z 하중 -> 띠 두께 방향 굽힘")
# 아래 가로판 Y -164~-127(폭 37) - 구멍 2(Ø6.5) 뿌리
sec("CST_V_armL_Z", F_op, F_MIS, 80.0, (37 - 2 * 6.5) * t ** 2 / 6, "아래 가로판 뿌리 t4 폭 37 - 구멍 2")
sec("CST_V_armU_Z", F_op, F_MIS, 80.0, (33 - 2 * 6.5) * t ** 2 / 6, "윗 가로판 뿌리 t4 폭 33 - 구멍 2")
# 2) COMB_KDM: 앞판 t8(Y88~96) X80, 날개 t6(Z620~626) -> 귀(Y112~120) 볼트 2
F_op = wt(6) + Fp0604
sec("KDM_plate_Y", F_op, F_MIS, 710.0 - 626.0, 80 * 8 ** 2 / 6, "앞판: 가장 높은 구멍 Z710에서 Y 당김, 뿌리 날개 윗면 Z626")
sec("KDM_flange_Y", F_op, F_MIS, 710.0 - 623.0, 80 * 6 ** 2 / 6, "날개 t6: 앞판 Y 하중 모멘트가 날개 단면(X80 x t6)을 굽힘")
sec("KDM_flange_Zload", F_op, F_MIS, 112.0 - 92.0, 80 * 6 ** 2 / 6, "날개: 앞판 Z 하중이 날개 길이 20(Y92->112)으로 굽힘")
sec("KDM_arm_X", F_op, F_MIS, 745.0 - 665.0, 8 * 68 ** 2 / 6, "팔 Y40(형상 같음, 웹 Y44~96으로 짧아짐)")
# 3) SO_1: 블록(X981~997) 그대로 꼴, 멍에 X904~920 Y72~113 Z232~256 (REG1_OUT 1줄, Y82 Z240)
F1 = wt(1) + Fp0604
sec("SO1_yoke_Z", F1, F_MIS, 112.0 - 82.0, 16 * 24 ** 2 / 6, "멍에: 관 Z 당김, 귀 앞면 Y112까지 30")
sec("SO1_yoke_X", F1, F_MIS, 112.0 - 82.0, 24 * 16 ** 2 / 6, "멍에: 관 축(X) 당김")
sec("SO1_ear_Y", F1, F_MIS, 944.0 - 912.0, 20 * 8 ** 2 / 6, "귀 t8 Z20: 멍에 Y 하중 -> 가까운 볼트 X944까지 32")
F2 = wt(2) + Fp0604
sec("SO1_block_Z", F2, F_MIS, 112.0 - 53.0, 16 * 38 ** 2 / 6, "블록: U6 구멍 Y53 -> 귀 Y112 59 (수정 1과 같은 꼴, X 이동만)")
# 4) AIR_IN_BRKT: t4 판 Y96~120 Z256~304 + 날개 t4 X1152~1166(볼트 Z261·299). KQ2E08 관 1줄 TU0805 당김
w0805 = math.pi / 4 * (8 ** 2 - 5 ** 2) * 1.2e-3
F_op = 1 * w0805 * 300 / 1000 * G * 3 + 0.5 * math.pi / 4 * 25
sec("AIR_plate_X", F_op, F_MIS, 116.0 - 108.0, 48 * 4 ** 2 / 6 - 13.2 * 4 ** 2 / 6, "판 t4 Z48 - 구멍 Ø13.2: 관 축(X) 당김, 날개 Y116까지 8")
sec("AIR_flange_X", F_op, F_MIS, 1159.0 - 1152.0, 48 * 4 ** 2 / 6, "날개 t4 Z48: 판에서 볼트 X1159까지 7")
json.dump(R, open("C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_PNEU-01_fix2_handcalc.json", "w", encoding="utf8"),
          ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, "op", v["SF_op"], "mis", v["SF_mis"], v.get("defl_op_mm", ""))
