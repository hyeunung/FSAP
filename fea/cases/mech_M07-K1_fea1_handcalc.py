# -*- coding: utf-8 -*-
"""M07-K1 해석부 손계산 — 받침틀 판금 L(SUS304 t6) + CB5-16 + HNTT8-5 (v2.5.3)

모델링부 손계산(fea/results/mech_M07-K1_handcalc.json)을 독립으로 다시 본다.
바꾼 점: (1) 굽힘 구석 고정 외팔(팔 = 구멍 - (t+R) - 머리 반지름) + 곡률보 응력 집중 Kt 1.3,
(2) 무게를 실제로 브래킷이 받는 자리(M04·M04R 가로대 끝, 가로대가 레일 옆면에 브래킷으로만 묶임)를 따로,
(3) 편심 모멘트에 의한 볼트 지렛대 당김, (4) 판 좌면, (5) 마찰만 본 미끄럼(참고, 홈 형상 물림이 받음).
FEA: 엔진 해석 환경 engine/fea/.venv 없음 -> 해석 못 함 — 환경 없음(D-16).
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # 엔진 도구 읽기만

E_SUS, RP_SUS, PG_SUS = 193000.0, 205.0, 400.0
T, R_IN, B = 6.0, 6.0, 30.0
R_HEAD = 8.5 / 2           # CB5 머리
KT_BEND = 1.3              # 곡률보 안쪽 섬유(R_in/t = 1, ro/ri = 2, Winkler 근사)
SF_MIS = 2.0               # M-09 오조작
TORQ, K = 4.0, 0.2         # D-54 CB5 4 N·m
FV = TORQ * 1000 / (K * 5)  # 4000 N
MU = 0.15                  # D-54

out = {'task': 'M07-K1', 'dept': '해석부', 'date': '2026-11-05', 'version': 'v2.5.3',
       'fea': '해석 못 함 — 환경 없음(자료대기 D-16)'}

# --- 하중 경우 ---
F_LAT = round((500 + 71.5) / 2, 1)      # 286 N: 오조작 손 + 대차 반력, 이음 하나 브래킷 2개(모델링부와 같음)
R_CM1 = 473.8                           # M04R 손계산 CM1 끝 반력(자중 x3 g + 손 100 N), 가로대 끝 브래킷 1개가 전부
out['loads'] = {
    'A_옆힘_벌어짐_N': F_LAT,
    'A_desc': 'M07 YX·YM·LEG·LEGY·COL, M04 레일-침목: 부재끼리 얹힘/레벨러로 자중 전달 -> 브래킷은 옆힘·벌어짐만',
    'B_가로대끝_수직_N': R_CM1,
    'B_desc': 'M04 XB 16·M04R 6(S형, 가로대 +X 옆면 <-> 레일 안쪽 면): 가로대 무게가 브래킷으로만 감. 가장 큰 CM1 끝 반력으로 묶음(E-19)',
}

# --- A: 벌어짐 — 다리 굽힘(굽힘 구석 고정, 볼트 머리 안쪽 가장자리에 F) ---
legs = {'T(구멍 60)': 60.0, 'S(구멍 30)': 30.0, 'C(구멍 20)': 20.0}
A = {}
for name, hole in legs.items():
    arm = hole - (T + R_IN) - R_HEAD
    arm_old = hole - R_HEAD
    r = beam(T, B, max(arm, 1.0), F_LAT, 0.0, E_SUS, RP_SUS, 'cantilever', SF_MIS)
    s = r['stress_MPa'] * KT_BEND
    A[name] = {'arm_mm': arm, 'sigma_nom_MPa': r['stress_MPa'], 'Kt': KT_BEND, 'sigma_MPa': round(s, 1),
               'sf': round(RP_SUS / s, 2), 'sf_min': SF_MIS, 'ok': RP_SUS / s >= SF_MIS,
               '옛 모델(머리 가장자리 고정, 팔 %.2f, Kt 없음) sf' % arm_old:
                   round(RP_SUS / (6 * F_LAT * arm_old / (B * T * T)), 2),
               'beam_tool': r}
out['A_plate_bending'] = A

# A 볼트: 지렛대 2배
out['A_bolt_572'] = calc(5, 7.5, 2 * F_LAT, torque=TORQ, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS)

# --- B: 가로대 끝 수직(굽힘축 방향) ---
# 두 볼트가 구석에서 각 30 -> 편심 모멘트 M = F x 30 (보수: 한 다리 단면이 전부 받음)
M = R_CM1 * 30.0
Zw = B * T * T / 6                       # 180 mm3 (약축 굽힘)
sig_b = M / Zw
alpha = 0.291                            # b/t = 5 직사각 비틀림
tau_t = M / (alpha * B * T * T)
tau_y = 0.577 * RP_SUS
F_pry = M / 15.0                         # 다리 폭 반(15)을 팔로 볼트 당김
As5 = 14.2
Bres = {
    'M_Nmm': round(M), 'sigma_bend_MPa': round(sig_b, 1), 'sf_bend': round(RP_SUS / sig_b, 2),
    'tau_torsion_MPa': round(tau_t, 1), 'sf_torsion': round(tau_y / tau_t, 2),
    'bolt_shear_MPa': round(R_CM1 / As5, 1), 'sf_bolt_shear': round(0.6 * 1100 / (R_CM1 / As5), 1),
    'plate_bearing_MPa': round(R_CM1 / (5 * T), 1), 'sf_bearing': round(1.5 * RP_SUS / (R_CM1 / (5 * T)), 1),
    'tnut_neck_bearing': '홈 방향과 수직(레일 홈 X·가로대 홈 Y, 하중 Z) -> T너트 목이 홈 턱에 닿아 형상으로 받음. 허용 하중 카탈로그 없음(D-54)',
    'friction_only': {'friction_N': FV * MU, 'sf': round(FV * MU / R_CM1, 2),
                      'note': '마찰만 본 값(참고). 하중 방향이 홈과 수직이라 미끄러지지 않음 -> 판정에 쓰지 않음'},
    'bolt_pry_N': round(F_pry),
    'bolt_pry': calc(5, 7.5, F_pry, torque=TORQ, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_MIS),
}
Bres['sf_min_case'] = min(Bres['sf_bend'], Bres['sf_torsion'])
out['B_crossbar_end'] = Bres

# --- 좌면: CB5 머리 -> SUS304 판 ---
ab = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
out['seat_SUS304'] = {'preload_N': FV, 'area_mm2': round(ab, 1), 'p_MPa': round(FV / ab, 1), 'sf_vs_pG400': round(PG_SUS / (FV / ab), 2)}

# --- 물림 ---
out['engagement'] = {'Le_mm': 7.5, '1.5d_mm': 7.5, 'ok': True, 'source': '모델링부 저장본: 끝 = 형재 겉면 아래 10, 너트 나사 2.5~11.5'}

sfs = {'A_T': A['T(구멍 60)']['sf'], 'A_S': A['S(구멍 30)']['sf'], 'A_C': A['C(구멍 20)']['sf'],
       'B_bend': Bres['sf_bend'], 'B_torsion': Bres['sf_torsion'], 'seat': out['seat_SUS304']['sf_vs_pG400']}
out['min_sf'] = min(sfs.values()); out['min_where'] = min(sfs, key=sfs.get); out['sfs'] = sfs
out['verdict'] = 'SF >= 2 전부 통과' if out['min_sf'] >= SF_MIS else 'SF < 2 있음'

p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_M07-K1_fea1_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({'sfs': sfs, 'min': out['min_sf'], 'where': out['min_where'],
                  'A_bolt_worst': out['A_bolt_572']['worst'], 'A_bolt_ok': out['A_bolt_572']['ok'],
                  'B_pry_N': Bres['bolt_pry_N'], 'B_pry_ok': Bres['bolt_pry']['ok'], 'B_pry_sf': Bres['bolt_pry']['sf_operating'],
                  'B_fric_sf': Bres['friction_only']['sf']}, ensure_ascii=False))
