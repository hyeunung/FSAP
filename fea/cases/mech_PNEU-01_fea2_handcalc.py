# -*- coding: utf-8 -*-
"""PNEU-01 해석부 2회차 손계산 (v2.8.8, 새 하중 부품 STEP 4개). 해석 환경 없음(D-16) -> FEA 대신 손계산.
치수 = 새 하중 부품 STEP 꼭짓점 bbox·평면 좌표(fea/results/mech_PNEU-01_fea2_stepgeo.json, 이 폴더 mech_PNEU-01_fea2_stepgeo.py).
하중·기준 = fea/models.json(P_M08_TUBE_BRKT_CST_V·P_M08_TUBE_FIXTURES 행) = 요구서 6-1 'M-09 기본값':
  운전 SF 3, 오조작 SF 2(A5052 항복 195, E 70 GPa). 운전 = 관 자중 x3 g(300 mm 몫) + 압력 펴짐 1줄(0.5 MPa x 안지름 넓이),
  오조작 = 관 1줄 손 당김 50 N(임시값, D-16 쓰는 곳) 가장 먼 관 구멍·가장 불리한 방향.
모델링부 fea/cases/mech_PNEU-01_fix2_handcalc.py 와 같은 식을 STEP 좌표로 다시 짚고(하중점은 윗판 윗면 Z536 보수),
옮긴 볼트 CB5-16 4개(F_5 2·AIR 2)와 띠가 바뀐 CST_V 볼트 2개를 handcalc.calc로 본다.
결과: fea/results/mech_PNEU-01_fea2_handcalc.json"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc as bolt, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SY, E, G, F_MIS = 195.0, 70000.0, 9.81, 50.0
SF_OP, SF_MIS = 3.0, 2.0
w0604 = math.pi / 4 * (6 ** 2 - 4 ** 2) * 1.2e-3
w0805 = math.pi / 4 * (8 ** 2 - 5 ** 2) * 1.2e-3
Fp0604 = 0.5 * math.pi / 4 * 4 ** 2
Fp0805 = 0.5 * math.pi / 4 * 5 ** 2
geo = json.load(open(f'{ROOT}/fea/results/mech_PNEU-01_fea2_stepgeo.json', encoding='utf-8'))


def wt(n, w=w0604, span=300.0):
    return n * w * span / 1000 * G * 3


def judge(sf_op, sf_mis):
    if sf_mis < 1.2 or sf_op < 1.2:
        return '동작'
    if sf_mis < SF_MIS or sf_op < SF_OP:
        return '디테일'
    return '됨'


out = {'_criteria': {'SF_op': SF_OP, 'SF_mis': SF_MIS, 'source': 'fea/models.json = 요구서 6-1(M-09 기본값)'}, 'parts': {}, 'bolts': {}}
P = out['parts']


def sec(name, F_op, L, Z, note, I=None):
    so, sm = F_op * L / Z, F_MIS * L / Z
    r = {'L_mm': round(L, 1), 'Z_mm3': round(Z, 1), 'sigma_op': round(so, 2), 'SF_op': round(SY / so, 2),
         'sigma_mis': round(sm, 2), 'SF_mis': round(SY / sm, 2), 'note': note}
    if I:
        r['defl_op_mm'] = round(F_op * L ** 3 / (3 * E * I), 2)
        r['k_N_mm'] = round(3 * E * I / L ** 3, 3)
    r['judge'] = judge(r['SF_op'], r['SF_mis'])
    P[name] = r


# 1) CST_V: STEP bbox X58~146 Y-164~-127 Z296~536. 띠 X58~62(t4) Y-159~-129(폭 30). 카세트 판 윗끝 Z328(서명 P_M05_CST_PLATE)
g = geo['P_M08_TUBE_BRKT_CST_V']
t = g['x'][1] - g['x'][0]                      # 4
b = -129.0 - (-159.0)                         # 30 (y 좌표 -159, -129)
assert abs(t - 4) < 1e-6 and -159.0 in g['y'] and -129.0 in g['y']
z_top = g['bbox'][2][1]                       # 536 (보수: 윗판 윗면)
L = z_top - 328.0
F_op = wt(6) + Fp0604
sec('CST_V_strip_X', F_op, L, b * t ** 2 / 6, f'띠 두께 방향 +X, 뿌리 Z328 -> 하중점 Z{z_top:.0f}(윗판 윗면, 보수)', I=b * t ** 3 / 12)
sec('CST_V_strip_Y', F_op, L, t * b ** 2 / 6, '띠 폭 방향 Y', I=t * b ** 3 / 12)
sec('CST_V_strip_Zload', F_op, 146.0 - 62.0, b * t ** 2 / 6, '가로판 끝(X146) Z 하중 -> 띠 두께 방향 굽힘, 팔 84(보수: 끝 모서리)')
sec('CST_V_armU_Z', F_op, 146.0 - 62.0, (33 - 2 * 6.5) * t ** 2 / 6, '윗 가로판 Y-160~-127(33) - 구멍 2, t4, 팔 84')
sec('CST_V_armL_Z', F_op, 146.0 - 62.0, (37 - 2 * 6.5) * t ** 2 / 6, '아래 가로판 Y-164~-127(37) - 구멍 2, t4, 팔 84')
out['beam_CST_V'] = beam(t=4, b=30, length=L, load=F_MIS, sf_min=SF_MIS)
out['beam_CST_V']['F_yield_N'] = round(SY * (b * t ** 2 / 6) / L, 1)

# 2) COMB_KDM: X-88~-8, Y36~120, Z620~745. 앞판 Y88~96(t8) 폭 80, 날개 Z620~626(t6), 귀 Y112~120
F_op = wt(6) + Fp0604
zh = 736.0                                    # 판에서 가장 높은 구멍 꼭짓점 735.28 -> 보수 736
sec('KDM_plate_Y', F_op, zh - 626.0, 80 * 8 ** 2 / 6, '앞판 t8 폭 80: 가장 높은 꼭짓점 Z736(보수)에서 Y 당김, 뿌리 날개 윗면 Z626')
sec('KDM_flange_Y', F_op, zh - 620.0, 80 * 6 ** 2 / 6, '날개 t6 X80: 앞판 Y 하중 모멘트(팔 Z736->620)')
sec('KDM_flange_Zload', F_op, 120.0 - 92.0, 80 * 6 ** 2 / 6, '날개: Z 하중, 앞판 가운데 Y92 -> 귀 끝 Y120 28')
sec('KDM_arm_X', F_op, 745.0 - 665.0, 8 * 68 ** 2 / 6, '팔(t8, 높이 68) X 당김, 팔 80')

# 3) SO_1: X904~1003 Y45~120 Z232~272. 멍에 X904~920 Y72~113 Z232~256, 블록 X981~997, 귀 Y112~120 t8
F1, F2 = wt(1) + Fp0604, wt(2) + Fp0604
sec('SO1_yoke_Z', F1, 120.0 - 82.0, 16 * 24 ** 2 / 6, '멍에 16x24: 관(Y82) Z 당김, 받침 면 Y120까지 38(보수)')
sec('SO1_yoke_X', F1, 120.0 - 82.0, 24 * 16 ** 2 / 6, '멍에: 관 축 X 당김, 38')
sec('SO1_ear_Y', F1, 944.0 - 904.0, 20 * 8 ** 2 / 6, '귀 t8 Z20: 멍에 끝 X904 -> 가까운 볼트 X944 40(보수)')
sec('SO1_block_Z', F2, 120.0 - 45.0, 16 * 38 ** 2 / 6, '블록 16x38: 끝 Y45 -> 받침 Y120 75(보수)')

# 4) AIR_IN_BRKT: X1148~1166 Y96~120 Z256~304. 판 X1148~1152 t4, 날개 X1152~1166 Y116~120 t4. KQ2E08 몸 구멍
F_op = wt(1, w0805) + Fp0805
hole = 13.2
sec('AIR_plate_X', F_op, 116.0 - 96.0, (48 - hole) * 4 ** 2 / 6, f'판 t4 Z48 - 구멍 Ø{hole}: X 당김, 판 끝 Y96 -> 날개 Y116 20(보수)')
sec('AIR_flange_X', F_op, 1166.0 - 1148.0, 48 * 4 ** 2 / 6, '날개 t4 Z48: 판 X1148 -> 날개 끝 X1166 18(보수)')

# 볼트(CB5-16, 12.9, 조임 4.5 N·m) — 오조작 하중, 지렛대(받침점 = 귀 끝 모서리)
B = out['bolts']
# CST_V: +X 당김 Z536, 받침점 띠 밑끝 Z296, 볼트 Z304·320(팔 8·24) -> 위 볼트 몫
M = F_MIS * (z_top - 296.0)
k = M / (8 ** 2 + 24 ** 2)
B['CST_V_CB5-16_le8_A5052'] = bolt(d=5, le=8, load=round(k * 24, 1), torque=4.5, base='A5052', sf_min=SF_MIS)
# F_5: 블록 X-112~-88 Y102~120 Z420~470, 볼트 X-106·-94 Z462 축 Y, 보 STKR400 벽 t8 -> le 8.
#  -Y 당김 50 N은 볼트 2개가 나눠 받지만 보수로 1개가 다 받고, Z 당김 지렛대(관 Y111 -> 면 Y120 팔 9, 받침점 Z420 -> 볼트 42) 더함
T_F5 = F_MIS + F_MIS * 9 / 42
B['F_5_CB5-16_le8_SS400'] = bolt(d=5, le=8, load=round(T_F5, 1), torque=4.5, base='SS400', sf_min=SF_MIS)
# AIR: 볼트 X1159 Y116->보 Z261·299, 보 벽 t8 -> le 8(모델링부 '탭 깊이 12'는 벽 8 넘음 -> 보수 8)
#  -Y 당김(관을 보에서 떼는 쪽) 50 N 1개가 다 받음 + X 당김 지렛대(구멍 Y108 -> 면 Y120 팔 12, 받침 X1166 -> 볼트 7)
T_AIR = F_MIS + F_MIS * 12 / 7
B['AIR_CB5-16_le8_SS400'] = bolt(d=5, le=8, load=round(T_AIR, 1), torque=4.5, base='SS400', sf_min=SF_MIS)

json.dump(out, open(f'{ROOT}/fea/results/mech_PNEU-01_fea2_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for kk, v in P.items():
    print(f"{kk:20s} op {v['SF_op']:8.2f} mis {v['SF_mis']:7.2f} {v['judge']}")
print('beam CST_V', out['beam_CST_V']['sf'], out['beam_CST_V']['deflection_mm'], 'Fy', out['beam_CST_V']['F_yield_N'])
for kk, v in B.items():
    print(kk, v['inputs']['load_N'], v['sf_operating'], v['sf_tightening'], v['ok'], v['needs_fea'])
