# -*- coding: utf-8 -*-
"""T14 모델링(v0.8.2) 손계산 — 줄인 부재 Y판 t15 -> t10, 늘린 DG 받침 50 -> 55.
해석 못 함 - 환경 없음(D-16). 식은 mech_T14_concept2.md 4-1절과 같고, 부피·질량은 v0.8.2 실측값이다.
"""
import json, os

ALLOW = 175.0  # A5052 허용(항복 기준) MPa, mech_T01_fea와 같음
R = {}

# Y판 t10: 운전 3 g
W_kg = 81.8                       # 얹힌 질량(concept2 4-1, MAT_Y 위 묶음). 이번 변경으로 2.0 kg 줄지만 보수로 그대로 둔다
F3g = W_kg * 9.81 * 3             # N
L = 78.1                          # DG 바닥 모서리 -> 블록 중심 대각 팔 mm
b, t = 100.0, 10.0
M = F3g / 4 * L                   # N*mm
Z = b * t ** 2 / 6
s_op = M / Z
R['YPLATE_op3g'] = dict(F_N=F3g, M_Nmm=M, Z_mm3=Z, sigma=s_op, SF=ALLOW / s_op, need=3.0)

# Y판 t10: 오조작(서보 최대 힘 1,080 N, 매트 면 -> Y판 윗면 -360 팔 346, 블록 쌍 간격 200, 폭 200) + 1 g
F = 1080.0
arm = 346.0
# 보수 모델: 짝힘(F x 팔 / 블록 쌍 간격 200)의 반을 블록 하나가 받고, 대각 팔 L·유효 폭 100으로 굽힘(concept2의 폭 200 모델 6.67보다 불리)
Fc = F * arm / 200.0
M2 = (Fc / 2 + W_kg * 9.81 / 4) * L
s_hit = M2 / (100.0 * t ** 2 / 6)
R['YPLATE_misuse'] = dict(couple_N=Fc, M_Nmm=M2, sigma=s_hit, SF=ALLOW / s_hit, need=2.0)

# 처짐(판 띠 외팔 1/t^3, t15 기준 0.015 mm)
R['YPLATE_defl_1g'] = dict(t15=0.015, t10=0.015 * (15 / 10) ** 3, limit='D-08 미정 -> 요구서 7절')

# DG 받침 55 옆힘
A = 31022.0
Zs = 940104.0
s_dg = F / A + F * 360.0 / Zs
R['DGSPACER'] = dict(sigma=s_dg, SF=ALLOW / s_dg, need=2.0)

# 실측(v0.8.2)
R['measured'] = dict(YPLATE=dict(vol=1804655.3, mass_g=4836.5, z=[-370, -360]),
                     DGSPACER=dict(vol=1706648.9, mass_g=4573.8, z=[-360, -305]),
                     delta_mass_g=(4836.5 - 7255.1) + (4573.8 - 4156.9))
R['spider'] = dict(H=(-10.5 - 85.0) - (-233.0))
R['chain'] = dict(sum=10 + 55 + 64 + 8 + 220.5 + 12 + 0.5, expect=370.0)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'out', 'mech_T14', 'model_handcalc.json')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
