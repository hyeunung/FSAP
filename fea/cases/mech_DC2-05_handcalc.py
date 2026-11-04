# -*- coding: utf-8 -*-
"""DC2-05 해석부 손계산 — 먼 쪽 바퀴 밑 받침(후보 tools/out/DC2-05/cand.sc). FEA 환경 없음(D-16) -> 손계산만.
새 하중 부품: P_DC205_STRIP(A5052 1,435x50x8 + 밑 보스 D35.6x3.8 x8), P_DC205_DISC(SUS304 t4 D50 구멍 D5.5 x8), CB5-12 x8.
형상: 모델링부 mech_DC2-05_model.md 1절 + stepout STEP bbox(0절에서 다시 읽음).
하중: 바퀴 누름 운전 90 N(D-92), 하중 케이스 운전 238.6 N·오조작 453.3 N(D-96, M03 cases), 띠 마찰 mu 0.3(상한 임시),
      볼트 조임 토크 4.5 N·m(앞 과제 M5 대 A5052와 같은 값, K 0.2), 자중 x3 g(띠 1.614 kg).
판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2만 '동작'.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
NU = 0.3
SY = {'SUS304': 205.0, 'A5052': 195.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0}
SF_OP, SF_MIS = 3.0, 2.0
P_RUN, P_OP, P_MIS = 90.0, 238.6, 453.3
MU = 0.3
T_STD = 4.5
out = {'assume': {'wheel_run_N': P_RUN, 'case_op_N': P_OP, 'case_misuse_N': P_MIS, 'mu_strip_max': MU,
                  'torque_std_Nm': T_STD, 'K': 0.2, 'strip_kg': 1.614}}

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
out['step_bbox'] = {}
for n in ['P_DC205_STRIP', 'P_DC205_DISC']:
    t = open(f'{ROOT}/tools/out/mech_DC2-05/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)] if pts else None,
                           'max': [round(max(c), 2) for c in zip(*pts)] if pts else None}

def plate_center(P, a, t, r0, e):
    """둘레 단순지지 원판, 가운데 반경 r0 원 하중 P (Roark/Timoshenko 근사)."""
    D = e * t ** 3 / (12 * (1 - NU ** 2))
    s = 3 * P / (2 * math.pi * t ** 2) * ((1 + NU) * math.log(a / r0) + 1)
    w = P * a ** 2 * (3 + NU) / (16 * math.pi * D * (1 + NU))
    return s, w, D

R = {}
# ---------- 1) 띠가 빈 구멍 D36 위를 건넘(보스 없는 구멍 20개). 트레드 25x20 접촉 -> 같은 넓이 원 r0 12.6, 보수로 r0 5 ----------
for tag, P, need in [('run', P_RUN, SF_OP), ('op', P_OP, SF_OP), ('misuse', P_MIS, SF_MIS)]:
    s, w, D = plate_center(P, 18.0, 8.0, 5.0, E['A5052'])
    sf = SY['A5052'] / s
    R[f'STRIP_over_hole_{tag}'] = {'P_N': P, 'a': 18.0, 't': 8.0, 'r0': 5.0, 'sigma': round(s, 2), 'w_mm': round(w, 5),
                                   'SF': round(sf, 1), 'need': need, 'verdict': verdict(sf, need)}
# 같은 자리를 띠 폭 50 · 지간 36 단순보(가운데 하중)로 본 상한 확인
Mb = P_MIS * 36 / 4; Zb = 50 * 8 ** 2 / 6
R['STRIP_over_hole_beam_check_misuse'] = {'sigma': round(Mb / Zb, 2), 'SF': round(SY['A5052'] / (Mb / Zb), 1),
    'w_mm': round(P_MIS * 36 ** 3 / (48 * E['A5052'] * 50 * 8 ** 3 / 12), 5), 'note': '원판보다 보수(둘레 받침 무시)'}
# ---------- 2) 띠 윗면 면압(경질 알루마이트 PTFE) ----------
R['STRIP_contact_pressure'] = {'run_MPa': round(P_RUN / (25 * 20), 3), 'misuse_MPa': round(P_MIS / (25 * 20), 3),
                               'note': '경질 알루마이트 허용 면압(수십 MPa)에 비해 아주 작음. 매트 눌림자국은 요구서 7절(시제품)'}
# ---------- 3) 볼트 CB5-12 -> 띠 보스 A5052 탭, 물림 7.8 ----------
Fdrag = MU * P_MIS
R['BOLT_CB5_le7.8_A5052_std_torque'] = calc(d=5, le=7.8, load=round(Fdrag, 1), torque=T_STD, bolt='12.9', base='A5052', sf_min=SF_MIS)
R['BOLT_note'] = {'drag_N': round(Fdrag, 1), 'note': '끌림은 보스 8개 D35.6이 판 구멍 D36에 끼워 받음(틈 0.2). 볼트에 인장 외력 없음 -> 보수로 끌림 전부를 볼트 하나 외력으로 넣음'}
# ---------- 4) 누름판 DISC SUS304 t4: 볼트 머리(r 4.25)가 가운데를 밀고 판 W2 밑면 r 18에서 받침. 보스 밑과 틈 0.2 ----------
Fp_std = T_STD * 1000 / (0.2 * 5)
s4, w4, D4 = plate_center(Fp_std, 18.0, 4.0, 4.25, E['SUS304'])
# 같은 판을 Timoshenko 표 3 경우 1(바깥 단순지지, 안 모서리 선하중, a/b 4.24 -> k ~2.2) 로 확인
k_t = 2.2
s4_t = k_t * Fp_std / 4.0 ** 2
F_close = Fp_std * 0.2 / w4   # 틈 0.2를 탄성으로 닫는 힘
mp = SY['SUS304'] * 4.0 ** 2 / 4
P_col = 2 * math.pi * mp / (1 - 2 * 4.25 / (3 * 18.0))
R['DISC_preload_std_torque'] = {'torque_Nm': T_STD, 'preload_N': round(Fp_std, 0), 'sigma_formula': round(s4, 1),
    'sigma_timoshenko_k2.2': round(s4_t, 1), 'SF': round(SY['SUS304'] / s4, 2), 'SF_timoshenko': round(SY['SUS304'] / s4_t, 2),
    'w_elastic_mm': round(w4, 4), 'F_to_close_gap0.2_N': round(F_close, 0), 'plastic_collapse_N': round(P_col, 0),
    'verdict': verdict(SY['SUS304'] / s4, SF_OP),
    'note': '표준 토크로 조이면 누름판 가운데가 항복(접시꼴 영구 변형), 틈 0.2는 탄성으로 안 닫힘 -> 보스가 힘을 못 받음'}
# 고치는 안 A: 토크 지정(형상 그대로)
for T in [1.0, 0.6]:
    Fp = T * 1000 / (0.2 * 5)
    s, w, _ = plate_center(Fp, 18.0, 4.0, 4.25, E['SUS304'])
    st = k_t * Fp / 16
    R[f'DISC_fixA_torque_{T}'] = {'preload_N': round(Fp, 0), 'sigma_formula': round(s, 1), 'sigma_timoshenko': round(st, 1),
        'SF': round(SY['SUS304'] / s, 2), 'SF_timoshenko': round(SY['SUS304'] / st, 2), 'w_mm': round(w, 4),
        'verdict': verdict(SY['SUS304'] / max(s, st), SF_OP)}
# 고치는 안 B: 보스 3.8 -> 4.0(보스 밑 = 판 W2 밑 Z -12, 틈 0). 조임 힘이 보스로 바로 감. 판 W2 두께 공차 +d 만큼만 누름판이 휨
for dlt in [0.03, 0.05]:
    F = F_close * dlt / 0.2
    s = SY['SUS304'] * 0 + plate_center(F, 18.0, 4.0, 4.25, E['SUS304'])[0]
    st = k_t * F / 16
    R[f'DISC_fixB_boss4.0_W2_thick+{dlt}'] = {'F_bend_N': round(F, 0), 'sigma_formula': round(s, 1), 'sigma_timoshenko': round(st, 1),
        'SF': round(SY['SUS304'] / s, 2), 'SF_timoshenko': round(SY['SUS304'] / st, 2), 'verdict': verdict(SY['SUS304'] / max(s, st), SF_OP),
        'note': '나머지 조임 힘은 보스 밑면 D35.6 접촉(면압 아주 작음). 판 W2는 띠 밑면과 누름판 사이에 0 틈으로 물림'}
R['BOLT_fixA_torque_1.0'] = calc(d=5, le=7.8, load=round(Fdrag, 1), torque=1.0, bolt='12.9', base='A5052', sf_min=SF_MIS)
# ---------- 5) 자중 x3 g: 띠가 판 W2에 고르게 얹힘 ----------
R['STRIP_selfweight_3g'] = {'N': round(1.614 * 3 * G, 1), 'note': '판 W2 윗면 전면 받침 -> 응력 무시'}
# ---------- 6) 열 늘음 차 ----------
R['thermal'] = {'dL_mm': round((23e-6 - 17.3e-6) * 1300 * 20, 3), 'radial_gap_x2_mm': 0.4, 'ok': True}
out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-05_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, {kk: v.get(kk) for kk in ('sigma', 'sigma_formula', 'sigma_timoshenko', 'sigma_timoshenko_k2.2', 'SF', 'SF_timoshenko', 'verdict', 'ok', 'preload_N', 'w_mm')} if isinstance(v, dict) else v)
print('bbox', out['step_bbox'])
