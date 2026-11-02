# -*- coding: utf-8 -*-
"""N02 해석 2회차(수정 1회차 v1.0.7) 손계산 — 바뀐 하중 부품은 P_N02_FRAME 하나(관 구멍 Ø10 이동). FEA 환경 없음(D-16).
형상(STEP tools/out/mech_N02/stepout/P_N02_FRAME.step 07:34, 면 bbox·법선으로 읽음):
  +Y 벽 Y -329~-325 (t4), X -955~-845 (폭 110, X -845가 자유 끝), 평면 Z -222(굽힘 R4/8 끝)~-131.
  관 구멍 Ø10: 중심 X -855, Z -170 (옛 X -920, Z -210). 하우징 볼트 구멍 Ø5.5: X -935·-865, Z -143.
하중·판정은 1회차 mech_N02_handcalc.py와 같다(운전 SF 3, 오조작 SF 2, SPCC Rp 205, 요구서 6-1 = M-09).
관 TU0604(PU Ø6)는 구멍 안 지름 방향 틈 2.0이라 벽에 하중을 주지 않는다(mech_N02_model1.md 1절).
보수: 구멍 둘레 응력 집중 Kt 3(평판 원공 인장 최대값 쪽), 벽 둘이 나눠 받지만 구멍 난 +Y 벽을 기준으로 본다.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

RP, E = 205.0, 205000.0
T = 4.0
SFMIN = {'run': 3.0, 'mis': 2.0}
F_LAT = {'run': 100.0, 'mis': 200.0}
F_BELT = {'run': 454.0, 'mis': 300.0 + 8.0 / 0.015915}
KT = 3.0
X0, X1 = -955.0, -845.0
HX, HZ, HR = -855.0, -170.0, 5.0
HX_OLD, HZ_OLD = -920.0, -210.0
Z_BOLT, Z_BRG, Z_ROOT = -143.0, -148.5, -226.0
out = {'shape': {'wall_X': [X0, X1], 'wall_t': T, 'hole_new': [HX, HZ, 2 * HR], 'hole_old': [HX_OLD, HZ_OLD, 2 * HR]}}


def sfrec(s, c, extra=None):
    sf = RP / s if s else float('inf')
    r = {'stress_MPa': round(s, 2), 'sf': round(sf, 2), 'sf_min': SFMIN[c], 'ok': sf >= SFMIN[c],
         'near_10pct': SFMIN[c] <= sf < 1.1 * SFMIN[c], 'motion_break': sf < 1.2}
    if extra:
        r.update(extra)
    return r


# 판금 규칙(M-03 39행 '구멍에서 바깥면까지 살 2.5 이상', M-04 '구멍–굽힘선 거리 ≥ 2t')
edge_new = X1 - (HX + HR)                  # 구멍 가장자리 → 자유 끝
bend_new = (HZ - HR) - (-222.0)            # 구멍 아래 가장자리 → 굽힘 끝
bend_old = (HZ_OLD - HR) - (-222.0)
d_bolt = math.hypot(HX - (-865.0), HZ - Z_BOLT) - HR - 2.75
out['sheet_rules'] = {'edge_to_free_end_mm': edge_new, 'edge_rule_min': 2.5, 'edge_ok': edge_new >= 2.5,
                      'hole_to_bend_mm': bend_new, 'bend_rule_min': 2 * T, 'bend_ok': bend_new >= 2 * T,
                      'old_hole_to_bend_mm': bend_old, 'old_bend_ok': bend_old >= 2 * T,
                      'hole_to_housing_bolt_hole_edge_mm': round(d_bolt, 1)}

# 순단면(구멍 지나는 Z -170 단면, X 방향 띠): 폭 110에서 X -860~-850 빠짐
def net_section():
    segs = [(X0, HX - HR), (HX + HR, X1)]
    A = sum((b - a) * T for a, b in segs)
    xc = sum((b - a) * T * (a + b) / 2 for a, b in segs) / A
    I = sum(T * (b - a) ** 3 / 12 + (b - a) * T * ((a + b) / 2 - xc) ** 2 for a, b in segs)
    return A, xc, I


A_n, xc_n, I_n = net_section()
I_g = T * 110 ** 3 / 12
out['net_section_Z-170'] = {'A_mm2': round(A_n, 1), 'xc': round(xc_n, 2), 'I_mm4': round(I_n), 'I_gross_mm4': round(I_g),
                            'I_ratio': round(I_n / I_g, 3)}

for c in ('run', 'mis'):
    # 1) 면외(Y 가로 /2, 하우징 볼트 Z -143 하중): 구멍 단면 Z -170 팔 27, 순폭 100, Kt 3 / 뿌리 Z -226 팔 83 폭 110(1회차)
    Fy = F_LAT[c] / 2
    M_o = Fy * (Z_BOLT - HZ)
    s_o = KT * 6 * M_o / ((110 - 2 * HR) * T ** 2)
    out[f'FRAME_hole_outplane_{c}'] = sfrec(s_o, c, {'M_Nmm': round(M_o, 1), 'Kt': KT})
    out[f'FRAME_root_outplane_{c}'] = beam(t=4, b=110, length=83, load=Fy, e=E, sy=RP, sf_min=SFMIN[c])
    # 2) 면내(X 벨트 + 가로, 베어링 중심 Z -148.5): 구멍 단면 팔 21.5, 벽 둘 → +Y 벽 절반(보수로 전부도 같이)
    Fx = F_BELT[c] + F_LAT[c]
    for share, tag in ((0.5, 'half'), (1.0, 'all')):
        M_i = Fx * share * (Z_BRG - HZ)
        s_hole = M_i * abs((HX + HR) - xc_n) / I_n * KT          # 구멍 가장자리(자유 끝 쪽) Kt 3
        s_edge = M_i * abs(X1 - xc_n) / I_n                        # 자유 끝 섬유(살 5)
        tau = 1.5 * Fx * share / A_n * KT                           # 전단 최대(보수 Kt 곱)
        vm = max(s_hole, math.sqrt(s_edge ** 2 + 3 * tau ** 2))
        out[f'FRAME_hole_inplane_{tag}_{c}'] = sfrec(vm, c, {'M_Nmm': round(M_i, 1), 's_hole_Kt_MPa': round(s_hole, 2),
                                                               's_free_edge_MPa': round(s_edge, 2), 'tau_Kt_MPa': round(tau, 2)})
    # 3) 살 띠(구멍 → 자유 끝 5 × t4) 국부: 웹 들림 짝힘(벽 끝 X -845에 몰림) Fc를 띠 하나가 다 받는다고 본 상한
    M_root = Fx * (Z_BRG - Z_ROOT)
    Fc = M_root / 110
    s_lig = KT * Fc / (edge_new * T)
    out[f'FRAME_ligament_upper_bound_{c}'] = sfrec(s_lig, c, {'Fc_N': round(Fc, 1), 'note': '물리적으로 Fc는 Z -226 뿌리(구멍 아래 51)에서 생기고 띠까지 오며 퍼진다. 상한 참고'})

# 1회차 뿌리 값과 비교(같아야 함): 면외 SF 14.49 / 7.24
json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_N02_fea1_handcalc.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in out.items():
    if isinstance(v, dict) and 'sf' in v:
        print(k, v['sf'], 'ok' if v['ok'] else 'NG')
    elif isinstance(v, dict) and k.startswith('FRAME_root'):
        print(k, v.get('sf'))
print('sheet', out['sheet_rules'])
print('net', out['net_section_Z-170'])
