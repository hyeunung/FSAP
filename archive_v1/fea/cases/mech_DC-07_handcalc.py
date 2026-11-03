# -*- coding: utf-8 -*-
"""DC-07 해석부 손계산 — U4_X_BEAM 레일 A 턱 + M5 멈춤나사, X 블록 간격 190 (v1.0.17). FEA 환경 없음(D-16).
형상(임시 STEP tools/out/mech_DC-07/stepout/U4_X_BEAM.step, mech_DC-07_model.md 2절, 월드 mm J 0):
  X 블록 중심 X -1000·-810(간격 190), 레일 A Y -960(-Y, 잠금), 레일 B Y +960(마찰만). 블록 Z -374.5~-352, 장착면 Z -352.
  안쪽 기준 턱 X 62 x Y 8(-939~-931) x Z 13(-365~-352), 블록 +Y 면이 Y -939에 맞닿음 → 하중 높이 = 뿌리 아래 6.5.
  바깥 누름 턱 X 62 x Y 10(-992~-982) x Z 13, M5 탭 3/블록 Z -360(뿌리 아래 8), 멈춤나사 STEP대기_MSSF5-10 평끝 Ø3.5, 물림 9.
  CB5-20_N03XB 2/블록(Y -976·-944, 간격 32), 예압 6,000 N(6 N·m, N03와 같음).
하중(출처):
  편구동 요 짝힘: 벨트 F_eff X 운전 282.7 N·오조작 375.2 N(mech_N03_handcalc.py FEFF), 팔 1,361(같은 식 1120 + m_y·1150/m_x).
  이동 질량 +17 %(N04-D4) → 둘 다 x1.17(오조작은 서보 토크 한계라 실제로 안 늘지만 보수로 곱함).
  Y 이송 반력(새로 더함, 선정 손계산에 없던 것): F_eff Y 운전 75.3 x1.17·오조작 224 N, 레일 A 두 블록이 나눔.
  레일 A 블록이 한 X 자리 힘 전부를 받는다고 봄(레일 B 이음 마찰 몫 0, 보수).
판정: 과제 완료 판정 — 이음 SF 운전 3·오조작 2(요구서 6-1, M-09), 블록 C0 SF 지금 값(4.4/3.32) 이상.
재질(임시, E-12): 블록 몸통 345(선정과 같음), 보 A5052-H112 110(77 두께 판, handcalc BASE 하한), 멈춤나사 45H.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

SFMIN = {'run': 3.0, 'mis': 2.0}
FX = {'run': 282.7, 'mis': 8.36 / 0.02228}
FY = {'run': 75.3, 'mis': 4.46 / 0.01990}
K = 1.17
ARM = 1120 + 35.0 * 1150 / 167.0
SP_OLD, SP_NEW = 70.0, 190.0
C0_LAT = 12100.0           # N03 손계산과 같은 블록 옆 정격(SV2RL28 C0)
SY_BLK, SY_BEAM = 345.0, 110.0
PRELOAD = 6000.0
MU = 0.2
out = {'model': 'mech_DC-07 handcalc v1.0.17', 'fea': '해석 못 함 — 환경 없음(D-16)', 'arm_mm': round(ARM, 1), 'cases': {}}


def sf_row(val, case):
    return {'sf': round(val, 2), 'sf_min': SFMIN[case], 'ok': val >= SFMIN[case],
            'near_10pct': SFMIN[case] <= val < 1.1 * SFMIN[case], 'motion_break': val < 1.2}


for c in ('run', 'mis'):
    yaw_st = FX[c] * K * ARM / SP_NEW           # 한 X 자리 짝힘(레일 A 혼자)
    ytr = (FY[c] * (K if c == 'run' else 1.0)) / 2  # Y 반력, 레일 A 두 블록
    F = yaw_st + ytr                            # 가장 불리한 블록(같은 방향 더함)
    r = {'yaw_station_N': round(yaw_st, 1), 'y_reaction_per_block_N': round(ytr, 1), 'F_block_N': round(F, 1)}
    # 1) 멈춤나사 끝 면압(3개 분담 / 조정 전 2개)
    a = math.pi / 4 * 3.5 ** 2
    for n in (3, 2):
        p = F / n / a
        r[f'setscrew_bearing_{n}'] = dict(sf_row(SY_BLK / p, c), p_MPa=round(p, 1), per_screw_N=round(F / n, 1))
    # 2) 멈춤나사 암나사(A5052-H112, 물림 9), 조임 1.0 N·m
    hc = calc(5, 9, F / 3, torque=1.0, bolt='12.9', base='A5052-H112', dw=5.0, dh=4.2, sf_min=SFMIN[c])
    r['setscrew_female_thread'] = {'sf': hc['sf_operating'].get('암나사 전단'), 'calc': hc}
    # 3) 턱 뿌리 굽힘+전단(Mises)
    for nm, t, h in (('inner_shoulder', 8.0, 6.5), ('outer_shoulder', 10.0, 8.0)):
        sig = F * h / (62 * t ** 2 / 6)
        tau = F / (62 * t)
        vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
        r[nm] = dict(sf_row(SY_BEAM / vm, c), sigma_MPa=round(sig, 1), tau_MPa=round(tau, 1), vm_MPa=round(vm, 1))
    # 4) 블록 기울임 → 볼트 분리(팔 9.5, 볼트 Y 간격 32, 한 볼트가 다 받음)
    dF = F * 9.5 / 32
    r['bolt_separation'] = dict(sf_row(PRELOAD / dF, c), dF_N=round(dF, 1))
    # 5) 블록 C0
    r['block_C0'] = {'sf': round(C0_LAT / F, 2), 'before': {'run': 4.4, 'mis': 3.32}[c], 'ok': C0_LAT / F >= {'run': 4.4, 'mis': 3.32}[c]}
    # 6) 참고: 레일 B 이음 마찰(모양 잠금 아님). 탄성 분담이 반이라 보면 미세 미끄럼 SF
    capB = 2 * PRELOAD * MU
    r['railB_friction_ref'] = {'share_half_N': round(F / 2, 1), 'cap_N': capB, 'sf': round(capB / (F / 2), 2),
                               'note': '레일 A 두 자리가 Y 양방향으로 잠겨 보가 돌거나 Y로 갈 수 없으므로 레일 B 이음은 전체 미끄럼이 일어나지 않는다. 미세 미끄럼이 나도 힘이 레일 A로 넘어갈 뿐 — 판정 대상 아님(기록)'}
    # 비교: 옛 간격 70 마찰 이음
    old = FX[c] * K * ARM / SP_OLD / 2
    r['old_sp70_friction_sf'] = round(2 * PRELOAD * MU / old, 2)
    out['cases'][c] = r

worst = []
for c, r in out['cases'].items():
    for k, v in r.items():
        if isinstance(v, dict) and 'sf_min' in v and not k.endswith('_2'):
            worst.append((v['sf'] / v['sf_min'], c, k, v['sf']))
worst.sort()
out['worst'] = [{'case': c, 'item': k, 'sf': s, 'ratio': round(q, 2)} for q, c, k, s in worst[:3]]
out['completion'] = {
    'joint_slip_or_separation': all(out['cases'][c][k]['ok'] for c in out['cases']
                                    for k in ('setscrew_bearing_3', 'inner_shoulder', 'outer_shoulder', 'bolt_separation')),
    'female_thread': all((out['cases'][c]['setscrew_female_thread']['sf'] or 0) >= SFMIN[c] for c in out['cases']),
    'block_C0': all(out['cases'][c]['block_C0']['ok'] for c in out['cases']),
}
json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-07_handcalc.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(json.dumps({'worst': out['worst'], 'completion': out['completion'],
                  'F': {c: out['cases'][c]['F_block_N'] for c in out['cases']},
                  'C0': {c: out['cases'][c]['block_C0']['sf'] for c in out['cases']},
                  'thread': {c: out['cases'][c]['setscrew_female_thread']['sf'] for c in out['cases']},
                  'two_screw': {c: out['cases'][c]['setscrew_bearing_2']['sf'] for c in out['cases']}}, ensure_ascii=False))
