# -*- coding: utf-8 -*-
"""P_T01_HUB 받침 반경 r85 재계산(디테일링 해석부 2026-10-31). DGM200R-AZAC 실물 STEP 출력 테이블 Ø170(mech_S01_measure.md 표) →
T01 2회차 모델(cases/mech_T01_fea1_handcalc.py hub_case, 같은 식) 그대로 r_s = 85, 하중은 그 결과 JSON의 r100 F_out·F_in에서 V·M 역산.
결과: fea/results/detail_hub_r85.json"""
import json, math, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
d = json.load(open(os.path.join(ROOT, 'fea', 'results', 'mech_T01_fea1_handcalc.json'), encoding='utf-8'))
hub = d['parts']['P_T01_HUB']; k100 = [k for k in hub if 'r100' in k][0]
E, SY = 193000.0, 205.0
def VM(c): return c['F_out'] - c['F_in_bolt'], 50.0 * c['F_in_bolt']
def case(r_s, V, M, t):
    F_out = V + M / 50.0; F_in = M / 50.0
    Mh = F_out * (150 - r_s) - F_in * max(0.0, 100 - r_s)
    b = min(60 + 2 * (150 - r_s), 2 * math.pi * r_s / 3)
    sig = Mh / (b * t ** 2 / 6)
    return dict(r=r_s, t=t, sigma=round(sig, 2), SF=round(SY / sig, 2), F_in_bolt=round(F_in, 1))
out = {'check_r100_t6': {}, 'r85': []}
V3, M3 = VM(hub[k100]['normal_3g']); Vj, Mj = VM(hub[k100]['jam'])
out['check_r100_t6'] = dict(SF_3g=case(100, V3, M3, 6)['SF'], prev=hub[k100]['SF_3g'], SF_jam=case(100, Vj, Mj, 6)['SF'], prev_jam=hub[k100]['SF_jam'])
for t in (6.0, 8.0, 10.0):
    out['r85'].append(dict(t=t, op_3g=case(85, V3, M3, t), jam=case(85, Vj, Mj, t)))
json.dump(out, open(os.path.join(ROOT, 'fea', 'results', 'detail_hub_r85.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
