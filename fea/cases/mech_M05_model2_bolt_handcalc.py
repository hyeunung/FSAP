# -*- coding: utf-8 -*-
"""M05 모델링부 수정 2회차 — 바꾼 체결 1곳: CB5-12_M05_5 -> CB5-16_M05_10 (판 +X -> 실린더 브래킷 날개 압입 너트).
FEA 환경 없음(D-16), 체결만 바뀐 자리(E-18) -> 손계산. 하중·가정은 수정 1회차 해석(mech_M05_fea1_handcalc.py)과 같다.
머리 밑면 X 58, 축 -X, 끝 X 42(실물 STEP bbox 42~63). 압입 너트 나사 X 43.19~49.2 -> 나사 전부 물림 6.01.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = 0.5
SF_OP = 3.0
F = 2 * math.pi / 4 * 10 ** 2 * P
Fb = round(F * (50 - 29) / 21 / 2 + F / 2, 1)   # 1회차와 같은 보수 합
le = round(49.2 - 43.19, 2)
R = {'assume': {'P_MPa': P, 'nut_base': 'SS400 대용(압입 너트 강재, 형번 임시 S-M5-2)', 'bolt_load_N': Fb},
     'bolt': 'CB5-16_M05_10', 'head_seat_X': 58, 'tip_X': 42, 'nut_thread_X': [43.19, 49.2], 'le_mm': le,
     'protrude_past_nut_mm': round(43.19 - 42, 2)}
for T in (2.5, 4.5):
    R['T%.1f' % T] = calc(d=5, le=le, load=Fb, torque=T, bolt='12.9', base='SS400', sf_min=SF_OP)
json.dump(R, open(f'{ROOT}/fea/results/mech_M05_model2_bolt_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1)[:2500])
