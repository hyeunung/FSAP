# -*- coding: utf-8 -*-
"""DC-04 해석부 손계산 — P_DC04_HANGER(SUS304 t3)·P_DC04_CARRIER(SUS304 t4)·CB5-12·레일 M3·플런저 핀 (v1.0.5).
FEA 환경 없음(D-16) -> 해석 못 함 — 환경 없음. 형상 = tools/out/mech_DC-04/changed_parts.json bbox, stepout/*.step.
좌표(바늘점 원점, mm): 플랜지 Y -90~-72 Z 122~125(UPPER 밑면 125에 맞닿음), CB5-12 x3 (X -10·240·480, Y -84).
  다리 Y -75~-72(중면 -73.5), 레일 Y -72~-64 Z 99.5~112.5(옆붙임, 중심 Y -68, Z 106), 블록 Y -64~-52, 캐리어 판 Y -52~-48,
  카세트 Y -45~-21(중심 -33). 인출 511에서 블록 X 491~531, 카세트 끝 X 522, 끝 탭 X 531~534 Y -75~-49 Z 64~92.
  앞 탭 X -24~-21 Y -75~-26 Z 64~119, 플런저 M8 (Y -36, Z 78), 핀 Ø6이 캐리어 러그 Ø6H7에 들어감.
하중(D-83 임시): 카세트+캐리어 3.3 kg. 운전 = 자중 x3 g(97.1 N) 카세트 중심 Y -33.
  오조작 = 손 100 N 아래로 카세트 +Y 끝(Y -21, 인출 511 X 522) + 자중 1 g(32.4 N) -> 132.4 N.
  봉제 반력 50 N(운전, X 방향 플런저 핀), 손 당김 100 N(오조작, +X로 끝 탭 / -X로 플런저).
판정: M-09 운전 SF 3, 오조작 SF 2(SUS304 Rp0.2 205). 처짐: 카세트 위 틈 1.0(UPPER), 밑 틈 4(U6) 안.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

E, SY = 193000.0, 205.0
g = 9.81
m = 3.3
W_run = m * g * 3            # 97.1
W_mis = 100.0 + m * g        # 132.4
Y_piv, Y_bolt, Y_leg = -90.0, -84.0, -73.5
Y_cg, Y_edge = -33.0, -21.0
out = {'model': 'mech_DC-04 handcalc v1.0.5', 'fea': '해석 못 함 — 환경 없음(D-16)', 'loads': {'W_run_N': round(W_run, 1), 'W_mis_N': round(W_mis, 1)}, 'cases': {}}

cases = [('run', W_run, Y_cg, 3.0), ('mis', W_mis, Y_edge, 2.0)]

for tag, W, Yl, sfmin in cases:
    # 1) 플랜지 볼트 CB5-12: 지렛대(받침 = 플랜지 -Y 끝 Y -90, 볼트 팔 6). 가까운 볼트 하나가 다 받는다고 봄(열린 L 단면 비틀림 약함).
    T = W * (Yl - Y_piv) / (Y_bolt - Y_piv)
    for base in ('A5052', 'SS400'):   # 867 UPPER 모재 미정(D-10) -> 보수 A5052, 참고 SS400(주철 대용)
        out['cases'][f'bolt_CB5-12_{tag}_{base}'] = calc(5, 9.0, T, torque=4.0, bolt='12.9', base=base, sf_min=sfmin)
    # 2) 플랜지 굽힘: 볼트 구멍 단면, 모멘트 R x 6, 유효 폭 84 - 구멍 5.5
    R = T - W
    out['cases'][f'flange_{tag}'] = beam(3.0, 84 - 5.5, 6.0, load=R, e=E, sy=SY, sf_min=sfmin)
    # 3) 다리 굽힘(굽힘선 Z 122, 하중 편심 = Yl - 다리 중면), 유효 폭 60(블록 40 + 굽힘선까지 16 x 2, 끝 X 522 쪽 잘림 보수)
    out['cases'][f'leg_{tag}'] = beam(3.0, 60.0, Yl - Y_leg, load=W, e=E, sy=SY, sf_min=sfmin)
    # 다리 회전으로 생기는 카세트 내려앉음(굽힘선 -> 레일 16 mm 구간 회전 x 팔)
    I = 60 * 27 / 12.0
    th = W * (Yl - Y_leg) * 16.0 / (E * I)
    out['cases'][f'leg_{tag}']['cassette_drop_mm'] = round(th * (Yl - Y_leg), 3)
    # 4) 레일 M3 볼트(다리 t3 탭 물림 3 = DC-04-D1): 받침 = 레일 밑 모서리(팔 6.5), 블록 길이 안 2개 몫
    Tr = W * (Yl - (-72.0)) / 6.5 / 2
    out['cases'][f'rail_M3_{tag}'] = calc(3, 3.0, Tr, bolt='12.9', base='SUS304', sf_min=sfmin)
    # 5) 블록 롤링 모멘트 MC(레일 중심 Y -68에서 편심), 허용 임시 20 N·m(D-83, MGN12급 하한 쪽)
    Mc = W * (Yl - (-68.0)) / 1000
    out['cases'][f'block_MC_{tag}'] = {'M_Nm': round(Mc, 2), 'allow_Nm_tmp': 20.0, 'sf': round(20.0 / Mc, 2), 'sf_min': sfmin}
    # 6) 캐리어 판 t4 굽힘(판 Y -50 -> 하중 Yl), 폭 X 32
    out['cases'][f'carrier_{tag}'] = beam(4.0, 32.0, Yl - (-50.0), load=W, e=E, sy=SY, sf_min=sfmin)

# 7) X 방향: 봉제 반력 50 N(운전, 플런저가 받음) / 손 당김 100 N(오조작)
for tag, F, sfmin in [('run', 50.0, 3.0), ('mis', 100.0, 2.0)]:
    out['cases'][f'front_tab_{tag}'] = beam(3.0, 55.0, -36.0 - (-72.0), load=F, e=E, sy=SY, sf_min=sfmin)   # 앞 탭: 굽힘 -72 -> 플런저 -36
    out['cases'][f'end_tab_{tag}'] = beam(3.0, 28.0, -50.0 - (-72.0), load=F, e=E, sy=SY, sf_min=sfmin)     # 끝 탭: 굽힘 -72 -> 캐리어 -50
    tau = F / (math.pi * 9.0)
    sb = F * 3.0 / (math.pi * 6 ** 3 / 32)
    out['cases'][f'pin_{tag}'] = {'tau_MPa': round(tau, 2), 'sigma_b_MPa': round(sb, 2), 'sf_vs_SUS304': round(SY / math.sqrt(sb ** 2 + 3 * tau ** 2), 1), 'sf_min': sfmin}
    out['cases'][f'lug_bearing_{tag}'] = {'p_MPa': round(F / (6 * 4), 2), 'sf': round(SY / (F / 24), 1), 'sf_min': sfmin}

# 8) 끝 탭 충돌(참고): 3.3 kg 0.5 m/s, 멈춤 길 1 mm(완충 없음) -> 등가 정하중
F_imp = m * 0.5 ** 2 / (2 * 0.001)
out['cases']['end_tab_impact_ref'] = beam(3.0, 28.0, 22.0, load=F_imp, e=E, sy=SY, sf_min=1.2)
out['cases']['end_tab_impact_ref']['F_equiv_N'] = round(F_imp, 1)

def sf_of(r):
    if 'sf' in r:
        return r['sf']
    if 'sf_operating' in r:
        return min(r['sf_operating'].values())
    return r.get('sf_vs_SUS304')
out['summary'] = {k: {'sf': sf_of(v), 'sf_min': v.get('sf_min', v.get('inputs', {}).get('sf_min'))} for k, v in out['cases'].items()}
p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-04_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out['summary'].items():
    print(k, v)
