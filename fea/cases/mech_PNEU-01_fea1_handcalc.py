# -*- coding: utf-8 -*-
"""PNEU-01 해석부 손계산 (E-18: 새로 만든 하중 부품 = 관 고정품 30, 대표 9바디 STEP + 같은 꼴 묶음 E-19).
해석 환경 없음(D-16) -> FEA 대신 손계산. 치수는 생성기 tools/gen_v2_pneu01_fix1.py fixtures() 상자 좌표(v2.8.7)와
서명 tools/out/signatures.json(받침 부품 bbox)에서 읽은 값.

하중 (요구서 6-1 = M-09 기본값: 운전 SF 3, 오조작 SF 2, A5052 항복 195 MPa, E 70 GPa)
 - 운전: 관 자중 x3 g (TU0604 18.8 g/m, TU0805 36.8 g/m, 자유 구간 <= 300 mm 몫) +
         관 압력 펴짐 힘 1줄(공급 0.5 MPa x 안지름 넓이: TU0604 6.3 N, TU0805 9.8 N, 보수: 고정품마다 1줄이 한 방향으로 다 민다)
 - 오조작(임시값): 관 1줄을 손으로 잡아당김 50 N, 가장 먼 관 구멍에서 X·Y·Z 가운데 가장 불리한 방향
   (근거: 원터치 이음 관 빠짐 전 손 힘 수준. 납품처 기준 없음 -> 자료대기 D-16 쓰는 곳에 적음)
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc as bolt, beam

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SY, E = 195.0, 70000.0
G = 9.81
P = 0.5  # MPa
F_MIS = 50.0
w0604 = math.pi / 4 * (6 ** 2 - 4 ** 2) * 1.2e-3  # g/mm -> 0.0188
w0805 = math.pi / 4 * (8 ** 2 - 5 ** 2) * 1.2e-3
Fp0604 = P * math.pi / 4 * 4 ** 2
Fp0805 = P * math.pi / 4 * 5 ** 2


def wt(n, span=300.0, w=w0604):
    return n * w * span / 1000 * G * 3  # N (g -> kg -> N, x3 g)


def sf(s):
    return round(SY / s, 2) if s > 0 else 999.0


out = {'_load': {'w_TU0604_g_per_m': round(w0604 * 1000, 1), 'w_TU0805_g_per_m': round(w0805 * 1000, 1),
                 'F_press_TU0604_N': round(Fp0604, 2), 'F_press_TU0805_N': round(Fp0805, 2), 'F_misuse_N': F_MIS}}
R = {}


def sec(name, M_op, Z_op, M_mis, Z_mis, note):
    so, sm = M_op / Z_op, M_mis / Z_mis
    R[name] = {'sigma_op_MPa': round(so, 2), 'SF_op': sf(so), 'sigma_mis_MPa': round(sm, 2), 'SF_mis': sf(sm), 'note': note}


# ---- 1) P_M08_TUBE_BRKT_CST_V: t4 세움 띠 X58~62 · Y-159~-146(폭 13) · Z296~530, 볼트 Z304·320 -> 카세트 판 X50~58 · Z20~328
#      판 윗끝 Z328 위로 띠 자유(외팔). 윗 가로판 Z518~522(구멍 평면 Z520) X62~146(팔 84), 관 U7C 6줄 + 아랫판 5줄
Lv = 520 - 328      # 띠 외팔 길이 192
Lh = 146 - 62 - 4   # 가로판 끝 관 구멍까지 팔(보수 80)
Zx = 13 * 4 ** 2 / 6      # 띠 두께 방향(X) 34.7
Zy = 4 * 13 ** 2 / 6      # 띠 폭 방향(Y) 112.7
n_up = 6
F_op = wt(n_up) + Fp0604
# 운전: 펴짐 힘 X 방향(가장 약한 쪽) 윗 가로판에서
sec('CST_V_strip_X', F_op * Lv, Zx, F_MIS * Lv, Zx, '띠 뿌리 Z328, 하중 +X(판에서 떨어지는 쪽) 윗판 Z520')
sec('CST_V_strip_Y', F_op * Lv, Zy, F_MIS * Lv, Zy, '띠 뿌리 Z328, 하중 Y')
sec('CST_V_strip_Zload', F_op * Lh, Zx, F_MIS * Lh, Zx, '가로판 끝 Z 하중 -> 띠에 F x 80 굽힘(두께 방향)')
Zarm = (33 - 2 * 6.5) * 4 ** 2 / 6
sec('CST_V_arm_Z', F_op * Lh, Zarm, F_MIS * Lh, Zarm, '가로판 뿌리 t4 폭 33 - 구멍 2')
I_strip = 13 * 4 ** 3 / 12
R['CST_V_strip_X']['defl_op_mm'] = round(F_op * Lv ** 3 / (3 * E * I_strip), 2)
R['CST_V_strip_X']['k_N_per_mm'] = round(3 * E * I_strip / Lv ** 3, 2)
R['CST_V_strip_X']['F_yield_N'] = round(SY * Zx / Lv, 1)
R['CST_V_beam_tool'] = beam(t=4, b=13, length=Lv, load=F_MIS, e=E, sy=SY, end='cantilever', sf_min=2.0)
# 고침 안: 띠를 가로판 폭(Y-160~-127, 33)으로 넓히고 t5, 또는 t4 + 굽힘 날개 15(L)
fix = {}
for nm, b, t in (('t4_b33', 33, 4), ('t5_b33', 33, 5), ('t6_b33', 33, 6)):
    fix[nm] = sf(F_MIS * Lv / (b * t ** 2 / 6))
# L 단면 t4: 띠 33 x 4 + 날개 15(X 방향, 띠 끝) -> X 방향 굽힘 단면 계수
b1, t1, h2, t2 = 33.0, 4.0, 15.0, 4.0
A1, A2 = b1 * t1, t2 * (h2 - t1)
y1, y2 = t1 / 2, t1 + (h2 - t1) / 2
yc = (A1 * y1 + A2 * y2) / (A1 + A2)
I = b1 * t1 ** 3 / 12 + A1 * (yc - y1) ** 2 + t2 * (h2 - t1) ** 3 / 12 + A2 * (y2 - yc) ** 2
fix['t4_b33_L15'] = sf(F_MIS * Lv / (I / max(yc, h2 - yc)))
R['CST_V_fix_SF_mis'] = fix
# 볼트: +X 당김 -> 띠 밑끝 Z296 받침점, 볼트 Z304(팔 8)·Z320(팔 24)
M = F_MIS * (520 - 296)
k = M / (8 ** 2 + 24 ** 2)
R['CST_V_bolt_T_mis_N'] = round(k * 24, 1)
out['bolt_CST_V_CB5-16_le8_mis'] = bolt(d=5, le=8, load=round(k * 24, 1), torque=4.5, base='A5052', sf_min=2.0)

# ---- 2) P_M08_RISER_COMB_1/2: 판 t8 X1040~1112(72) · Y-15~112 외팔 127, 관 구멍 10/8(Ø6.5·Ø8.5) + 귀 Y112~120 볼트 2
Lr = 112 - (-15)
Zr = (72 - 3 * 8.5) * 8 ** 2 / 6   # 한 단면에 구멍 3개(보수)
F_op_r = wt(8) + wt(2, w=w0805) + Fp0805
sec('RISER_COMB_plate_Z', F_op_r * Lr, Zr, F_MIS * Lr, Zr, '판 뿌리(귀 면 Y112), Z 하중 끝 Y-15')
T = F_MIS * Lr / 26 / 2   # RISER_1: 귀 밑변 Z396 받침, 볼트 Z422(팔 26)
R['RISER_COMB_bolt_T_mis_N'] = round(T, 1)
out['bolt_RISER_CB5-16_le8_mis'] = bolt(d=5, le=8, load=round(T, 1), torque=4.5, base='A5052', sf_min=2.0)

# ---- 3) P_M08_TUBE_COMB_KDM: Y40 팔(t8, X-88~-20, Z665~745) <- 웹(t8 X-88~-80, Y44~112, Z665~722) <- 보 앞면 판(X-88~-8, Z620~722)
Za = (80 - 2 * 6.5) * 8 ** 2 / 6
sec('COMB_KDM_arm_Y', (wt(6) + Fp0604) * 56, Za, F_MIS * 56, Za, '팔 뿌리 X-80, Y 하중 X-24')
Zw = 57 * 8 ** 2 / 6
sec('COMB_KDM_web_X', (wt(6) + Fp0604) * 72, Zw, F_MIS * 72, Zw, '웹 뿌리 Y112, X 하중 Y40')
T = F_MIS * 76 / 12 / 2  # Z 하중(팔 Y40 -> 판 Y116, 팔 76), 판 밑변 Z620 받침 볼트 Z632(팔 12)
R['COMB_KDM_bolt_T_mis_N'] = round(T, 1)
out['bolt_COMB_KDM_CB5-16_le8_mis'] = bolt(d=5, le=8, load=round(T, 1), torque=4.5, base='A5052', sf_min=2.0)

# ---- 4) P_M08_TUBE_BRKT_KDM: 판 t8 X-76~46 · Y-196~-116(80) on KDM_BRKT 윗면(X14~46) -> 외팔 X14 -> -70 (84)
Zk = (80 - 2 * 6.5) * 8 ** 2 / 6
sec('BRKT_KDM_plate_Z', (wt(6) + Fp0604) * 84, Zk, F_MIS * 84, Zk, '받침 끝 X14 단면, Z 하중 X-70')
T = F_MIS * 84 / 16 / 2
R['BRKT_KDM_bolt_T_mis_N'] = round(T, 1)
out['bolt_BRKT_KDM_CB5-16_le8_mis'] = bolt(d=5, le=8, load=round(T, 1), torque=4.5, base='A5052', sf_min=2.0)

# ---- 5) P_M08_TUBE_CLAMP_SO_1: 블록 X952~968(16) · Y45~112(외팔 67) · Z232~270(38) + 귀 Z252~272 볼트 Z262
Zs = 38 * 16 ** 2 / 6
sec('CLAMP_SO_1_X', (wt(2) + Fp0805) * 67, Zs, F_MIS * 67, Zs, '블록 뿌리 Y112, X 하중 Y50')
T = F_MIS * 67 / 10 / 2  # Z 하중, 귀 끝 받침 -> 볼트 팔 10
R['CLAMP_SO_1_bolt_T_mis_N'] = round(T, 1)
out['bolt_SO_1_CB5-16_le8_mis'] = bolt(d=5, le=8, load=round(T, 1), torque=4.5, base='A5052', sf_min=2.0)
# SO_2/3: 판 t8 폭 20 외팔 38(SO_2)
Zs2 = (20 - 6.5) * 8 ** 2 / 6
sec('CLAMP_SO_2_Z', (wt(1) + Fp0604) * 38, Zs2, F_MIS * 38, Zs2, '판 t8 폭 20 - 구멍, 외팔 38(보수: 구멍을 뿌리에)')

# ---- 6) P_M08_TUBE_CLAMP_CAR: 판 t8 X-1990~-1955(35) · Y48~72, 귀 Y72~80 볼트 Z410 -> 대차 판 Y80
Zc = (35 - 2 * 6.5) * 8 ** 2 / 6
sec('CLAMP_CAR_Z', (wt(2) + Fp0604) * 32, Zc, F_MIS * 32, Zc, '귀 면 Y80 단면, Z 하중 Y48')
# ---- 7) P_M08_TUBE_BRKT_ARM_1: 판 t8(Z616~624) X-1990~-1956 · Y46~78, 귀 t6 X-1956~-1950 · Y46~100 · Z604~644
#      체인 팔 면 X-1950 은 Y80~275 -> 귀 Y46~80 은 Y 방향 외팔
Zp = (32 - 6.5) * 8 ** 2 / 6
sec('ARM_1_plate_Z', (wt(2) + Fp0604) * 40, Zp, F_MIS * 40, Zp, '판 뿌리(귀 면 X-1956), Z 하중 X-1990')
Ze = 40 * 6 ** 2 / 6
sec('ARM_1_ear_X', (wt(2) + Fp0604) * 20, Ze, F_MIS * 20, Ze, '귀 Y80 단면(체인 팔 끝), X 하중 Y60')
tq = F_MIS * 31
tau = tq / (0.30 * 40 * 6 ** 2)
R['ARM_1_ear_torsion'] = {'tau_mis_MPa': round(tau, 2), 'SF_mis': round(SY / math.sqrt(3) / tau, 2)}
T = F_MIS * 40 / 8 / 2
R['ARM_1_bolt_T_mis_N'] = round(T, 1)
out['bolt_ARM_1_CB5-16_le10_mis'] = bolt(d=5, le=10, load=round(T, 1), torque=4.5, base='SUS304', sf_min=2.0)
# ARM_2: 판 t8 세움(Z800~836, 36) X 외팔 40, Y 하중
Za2 = (36 - 6.5) * 8 ** 2 / 6
sec('ARM_2_plate_Y', (wt(2) + Fp0604) * 40, Za2, F_MIS * 40, Za2, '판 뿌리(귀 면), Y 하중 X-1985')
# ---- 8) P_M08_TUBE_BRKT_U6: 블록 18x20x20 + 귀 t8 Y±16 Z222~272, 볼트 Z236 Y±8 -> BASE -X 면
Zu = 32 * 8 ** 2 / 6
sec('BRKT_U6_ear', (wt(1) + Fp0604) * 17, Zu, F_MIS * 17, Zu, '귀 블록 밑 Z252, Z 하중 X-347')
# ---- 9) 블록류(COMB_ML·CLAMP_F·CLAMP_L): 꽉 찬 블록, 가장 불리 COMB_ML 높이 48 · 두께 16
Zb = 73 * 16 ** 2 / 6
sec('COMB_ML_block_X', (wt(8) + Fp0604) * 48, Zb, F_MIS * 48, Zb, '보 윗면 뿌리 Z650, X 하중 윗끝')
T = F_MIS * 48 / 8
R['COMB_ML_bolt_T_mis_N'] = round(T, 1)
out['bolt_COMB_ML_CB5-16_le9.9_mis'] = bolt(d=5, le=9.9, load=round(T, 1), torque=4.5, base='SS400', sf_min=2.0)

out['sections'] = R
worst = sorted(((v['SF_mis'], k) for k, v in R.items() if isinstance(v, dict) and 'SF_mis' in v and 'sigma_mis_MPa' in v))
out['worst_mis'] = worst[:4]
out['worst_op'] = sorted(((v['SF_op'], k) for k, v in R.items() if isinstance(v, dict) and 'SF_op' in v))[:3]
json.dump(out, open(f'{ROOT}/fea/results/mech_PNEU-01_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('worst_mis', out['worst_mis'])
print('worst_op', out['worst_op'])
print('CST_V', R['CST_V_strip_X'], R['CST_V_fix_SF_mis'])
for k, v in out.items():
    if k.startswith('bolt_'):
        print(k, {kk: v[kk] for kk in v if kk in ('sf', 'SF', 'sf_min', 'ok', 'sf_thread', 'sf_bolt', 'sf_seat')} or str(v)[:160])
