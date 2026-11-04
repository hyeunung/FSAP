# -*- coding: utf-8 -*-
"""DC2-05 해석부 1회차(수정 뒤) 손계산. 수정: 형상 그대로, CB5-12_DC205 x8 조임 0.6 N·m + 중강도 나사 고정제(model1).
FEA 환경 없음(D-16) -> 손계산만. 앞 회차 식(mech_DC2-05_handcalc.py)을 그대로 쓰고 0.6 N·m와 조임 흩어짐 +-30%를 본다.
"""
import json, math, re, sys, hashlib
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
NU = 0.3
SY = {'SUS304': 205.0, 'A5052': 195.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0}
SF_OP, SF_MIS = 3.0, 2.0
P_MIS = 453.3
MU = 0.3
K = 0.2
T_SET = 0.6
SCATTER = 0.30   # 손 토크렌치 조임 흩어짐 +-30% (가정, VDI 2230 손 토크렌치 수준)
k_t = 2.2

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

def plate_center(P, a, t, r0, e):
    D = e * t ** 3 / (12 * (1 - NU ** 2))
    s = 3 * P / (2 * math.pi * t ** 2) * ((1 + NU) * math.log(a / r0) + 1)
    w = P * a ** 2 * (3 + NU) / (16 * math.pi * D * (1 + NU))
    return s, w

out = {'assume': {'torque_set_Nm': T_SET, 'K': K, 'scatter': SCATTER, 'mu_strip_max': MU, 'case_misuse_N': P_MIS,
                  'note': '형상은 앞 회차와 같음(모델링부 model1: 바뀐 단계 component.metadata.set 하나)'}}
# 0) STEP 형상 확인(해시·bbox)
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
out['step'] = {}
for n in ['P_DC205_STRIP', 'P_DC205_DISC']:
    b = open(f'{ROOT}/tools/out/mech_DC2-05/stepout/{n}.step', 'rb').read()
    pts = [tuple(map(float, m)) for m in pat.findall(b.decode('utf-8', 'ignore'))]
    out['step'][n] = {'sha1': hashlib.sha1(b).hexdigest()[:12], 'min': [round(min(c), 2) for c in zip(*pts)]}

R = {}
Fdrag = MU * P_MIS
for tag, T in [('set', T_SET), ('upper', T_SET * (1 + SCATTER)), ('lower', T_SET * (1 - SCATTER))]:
    Fp = T * 1000 / (K * 5)
    s, w = plate_center(Fp, 18.0, 4.0, 4.25, E['SUS304'])
    st = k_t * Fp / 16
    sf = SY['SUS304'] / max(s, st)
    R[f'DISC_torque_{tag}'] = {'torque_Nm': round(T, 2), 'preload_N': round(Fp, 0), 'sigma_formula': round(s, 1),
        'sigma_timoshenko': round(st, 1), 'SF_min': round(sf, 2), 'w_mm': round(w, 4), 'gap_mm': 0.2,
        'verdict_op': verdict(sf, SF_OP), 'yield': sf < 1.0}
    R[f'BOLT_torque_{tag}'] = calc(d=5, le=7.8, load=round(Fdrag, 1), torque=round(T, 2), bolt='12.9', base='A5052', sf_min=SF_MIS)
# 띠 미끄럼: 예압 x 8 x 마찰(띠 밑 A5052 ↔ SUS 판, mu 0.15 보수) vs 끌림
Fp_low = T_SET * (1 - SCATTER) * 1000 / (K * 5)
R['STRIP_slip'] = {'clamp_total_N': round(8 * Fp_low, 0), 'friction_N': round(0.15 * 8 * Fp_low, 0), 'drag_N': round(Fdrag, 1),
                   'SF': round(0.15 * 8 * Fp_low / Fdrag, 2),
                   'note': '흩어짐 아래쪽에서도 마찰로 버팀. 넘어도 보스 D35.6 ↔ 구멍 D36(틈 0.2)이 받음'}
# 보스 측면 지압(넘었을 때 끌림 전부를 보스 하나가): 접촉 높이 3.8 x 투영폭 35.6 의 절반 보수
R['BOSS_bearing'] = {'p_MPa': round(Fdrag / (3.8 * 35.6 * 0.5), 2), 'SF': round(SY['A5052'] / (Fdrag / (3.8 * 35.6 * 0.5)), 0)}
out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-05_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, json.dumps(v, ensure_ascii=False)[:300])
print('step', out['step'])
