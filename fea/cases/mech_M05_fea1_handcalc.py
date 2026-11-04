# -*- coding: utf-8 -*-
"""M05 해석부 수정 1회차 — 바뀐 하중 부품 2개(P_M05_CYL_BRKT, P_M05_CST_PLATE)와 옮긴 체결 1곳(CB5-12_M05_5 -> 압입 너트).
FEA 환경 없음(D-16) -> 손계산. 바뀐 것은 체결 자리 하나(E-18 '체결만 바뀐 자리는 손계산').
형상: mech_M05_model1.md 2절 + stepout STEP bbox. 하중: 1차 해석(mech_M05_handcalc.py)과 같음(0.5 MPa 임시, CJ2B10 x2).
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = 0.5
SY = {'SUS304': 205.0, 'A5052': 195.0}
SF_OP, SF_MIS = 3.0, 2.0
out = {'assume': {'P_MPa': P, 'nut_base': 'SS400 대용(압입 너트 강재, 형번 임시 S-M5-2)', 'torque_Nm': 4.5}}

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
out['step_bbox'] = {}
for n in ['P_M05_CYL_BRKT', 'P_M05_CST_PLATE']:
    t = open(f'{ROOT}/tools/out/mech_M05/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    # 배치 원점(0,0,0) 제외
    pts = [p for p in pts if any(abs(c) > 1e-6 for c in p)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)],
                           'max': [round(max(c), 2) for c in zip(*pts)]}

F10 = math.pi / 4 * 10 ** 2 * P          # CJ2B10 추력
F = 2 * F10
Tb = F * (50 - 29) / 21 / 2             # 1차와 같은 지레(볼트 하나 몫 인장)
Fb = round(Tb + F / 2, 1)               # 1차와 같은 보수 합(인장 + 전단 몫)
R = {'bolt_load_N': Fb}

# 1) 볼트 CB5-12_M05_5: 머리 X 58~63, 끝 X 46. 판 X 50~58(Ø5.5 관통), 날개 X 47~50, 너트 나사 X 43.19~49.2
le_now = 49.2 - 46.0
R['CB5-12_nut_le3.2'] = calc(d=5, le=round(le_now, 2), load=Fb, torque=4.5, bolt='12.9', base='SS400', sf_min=SF_OP)
R['CB5-15_nut_le6.0'] = calc(d=5, le=6.0, load=Fb, torque=4.5, bolt='12.9', base='SS400', sf_min=SF_OP)
R['le_over_d_now'] = round(le_now / 5, 2)
R['CB5-15_tip_X'] = 58 - 15
R['nut_end_X'] = 43.19

# 2) 볼트 머리 좌면 -> A5052 판(+X 면 X 58): 좌면 지름 8.5, 구멍 5.5
Ah = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
ph = 4.5e3 / (0.2 * 5) / Ah              # 조임력 F = T/(k d) 기준 면압
R['head_bearing_A5052'] = {'preload_N': round(4.5e3 / (0.2 * 5), 0), 'A_mm2': round(Ah, 1), 'p_MPa': round(ph, 0),
                           'limit_A5052_pG': 'handcalc 표 값(calc 결과 안 head/bearing)'}

# 3) 압입 너트 몸 플랜지 -> SUS304 날개 -X 면(인장은 너트를 날개 쪽으로 당김: 빠짐 방향 아님)
Af = math.pi / 4 * (9.73 ** 2 - 7.14 ** 2)
pf = (4.5e3 / (0.2 * 5) + Fb) / Af
R['nut_flange_bearing_SUS304'] = {'A_mm2': round(Af, 1), 'p_MPa': round(pf, 0), 'SF_vs_Rp': round(SY['SUS304'] / pf, 2),
                                  'note': '조임력이 플랜지 좌면으로 날개를 판에 누름(판-날개-플랜지 샌드위치). 면압 한계 p_G 400(SUS304)과 비교'}
R['nut_flange_bearing_SUS304']['SF_vs_pG'] = round(400 / pf, 2)

# 4) 판 구멍 M5 탭(Ø4.2) -> Ø5.5 관통: 그 자리(Y -195, Z 40)는 1차 최저 SF 자리(걸쇠 Z 314)에서 274 떨어짐
#    판 Y 폭 160에서 구멍 지름 1.3 늘어난 순단면 변화
R['plate_net_section_change_pct'] = round((5.5 - 4.2) / 160 * 100, 2)

# 5) 브래킷 날개 Ø5.5 -> Ø7.14: 날개 끝 거리(구멍 중심 Z 40 ↔ 날개 아래 끝 Z 34 = 6), 날개 Y 폭 -204~-171 중 볼트 Y -195 -> 끝 9
e = 40 - 34
R['wing_edge_distance'] = {'e_mm': e, 'e_over_D': round(e / 7.14, 2),
                           'shear_out_MPa': round(Fb / (2 * (e - 7.14 / 2) * 3), 1)}
R['wing_edge_distance']['SF'] = round(SY['SUS304'] * 0.577 / R['wing_edge_distance']['shear_out_MPa'], 1)
R['wing_edge_distance']['verdict'] = verdict(R['wing_edge_distance']['SF'], SF_OP)

out['R'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_M05_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])
