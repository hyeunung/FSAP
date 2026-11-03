# -*- coding: utf-8 -*-
"""M04 해석부 3회차 손계산 — U2 볼 테이블 수정 2회차(v2.1.5). FEA 환경 없음(D-16) -> 손계산만.
바뀐 것(모델링부 mech_M04_model2.md 2절): 체결만.
  - CB8-20 x8 -> CB8-15 x8(머리 밑 Z -9, 끝 Z -24, 레일 홈 바닥 살 Z -24.5와 0.5)
  - HNTT8-8 220·HNTT8-5 96 너트를 홈 겉면 쪽 3.0(어깨가 윗턱 밑면에 닿음), 침목 너트 108 90° 돌림
    -> 기존 볼트 물림 변화: CB8-16 5.3, 레벨러 5.5, 접시 M5 3.5 (모델링부 chk1 손 판정)
가공품(센터판·패널·형재) 형상·하중 경로는 안 바뀜 -> 1회차·2회차 결과를 읽어 쓴다(E-17·E-19).
판정 M-09: 운전 SF 3, 오조작 SF 2, 조임 SF 1. SF < 1.2만 동작.
"""
import json, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
out = {}
r0 = json.load(open(f'{ROOT}/fea/results/mech_M04_handcalc.json', encoding='utf-8'))
r1 = json.load(open(f'{ROOT}/fea/results/mech_M04_fea1_handcalc.json', encoding='utf-8'))

# 0) 센터판 STEP 확인(지시서 '새 하중 부품'): v2.1.4 내보낸 것과 같은 bbox인지
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
t = open(f'{ROOT}/tools/out/mech_M04/stepout/P_M04_INSERT.step', encoding='utf-8', errors='ignore').read()
pts = [tuple(map(float, m)) for m in pat.findall(t)]
bb = {'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}
out['insert_step'] = {'bbox': bb, 'same_as_fea1': bb == {'min': r1['step_bbox']['P_M04_INSERT']['min'], 'max': r1['step_bbox']['P_M04_INSERT']['max']},
                      'note': 'v2.1.5에서 센터판은 안 바뀜(모델링부 2절). 1회차 결과(SF 126.6, 처짐 0.037) 그대로'}

TANG_OP = 95.5   # 오조작 접선 N (mech_M02, U4 원판 -> 센터판)
TORQUE_M8 = 10.0  # N·m 임시(fea1과 같음, 시방 없음)
TORQUE_M5 = 4.0   # N·m 임시: 알루미늄 형재 T너트 M5 흔한 값, 시방 없음

# 1) CB8-15 x8 (새 체결): 물림 = 너트 목 윗면 Z -14.5 ~ 너트 밑 Z -23.5 = 9 (끝 -24가 너트 밑을 0.5 지남)
le15 = (-14.5) - (-23.5)
F_ax = TANG_OP * 20.0 / 430.0 + 1.0
seat = calc(8, le15, F_ax, torque=TORQUE_M8, bolt='12.9', base='A5052', dw=13.0, dh=9.0, sf_min=3.0)
thr = calc(8, le15, F_ax, torque=TORQUE_M8, bolt='12.9', base='SS400', dw=13.0, dh=9.0, sf_min=3.0)
grip = 3.0 + 5.5
out['CB8_15'] = {
    'le_mm': le15, 'engage_ratio': round(le15 / 8, 2), 'grip_mm': grip,
    'shank_check': {'head_seat_Z': -9.0, 'tip_Z': -24.0, 'floor_rib_Z': -24.5, 'tip_gap_mm': 0.5,
                    'free_thread_below_grip_mm': round((-9.0 - grip) - (-24.0), 1),
                    'note': '끝이 바닥 살에 닿지 않아 예압이 센터판에 걸린다(M04-X8 해결). 다만 틈 0.5는 너트 어깨-턱 밀착 뒤 값이라 너트 놓임 공차 ±0.3·볼트 길이 공차(JIS m 등급 15 +0/-0.7 근처)면 0.2~1.2'},
    'calc_seat_A5052': seat, 'calc_thread_SS400(T너트)': thr,
    'slip_SF_오조작': round(8 * TORQUE_M8 * 1000 / (0.2 * 8) * 0.2 / TANG_OP, 1),
}

# 2) 옮긴 너트에 물린 기존 볼트(물림 변화만 다시 봄, 가장 불리한 하나씩 E-19)
lev = r0['leveler_M8']
out['leveler_M8_le5.5'] = {'F_N': lev['F_N'],
                          'calc': calc(8, 5.5, lev['F_N'], torque=0.0, bolt='4.8', base='SS400', dw=13.3, dh=8.5, sf_min=2.0),
                          'prev_le6_암나사SF': lev['tnut_calc']['sf_operating']['암나사 전단'],
                          'note': '하중 846 N은 압축(침목 -> 레벨러)이라 너트는 홈 턱 밑면을 밀어 올림. 나사가 받는 힘은 그 전부로 봄(보수). 조임 토크는 잠금 너트 구조라 없음'}
# CB8-16 브래킷: 레일은 침목 위에 얹혀 수직 하중은 맞닿음이 받음 -> 볼트는 예압 + 보수 외력(오조작 접선 전부 1개)
out['CB8_16_bracket_le5.3'] = {'calc_thread_SS400': calc(8, 5.3, TANG_OP, torque=TORQUE_M8, bolt='12.9', base='SS400', dw=13.0, dh=9.0, sf_min=3.0),
                               'calc_seat_A6063(브래킷 HBLFSN8 좌면, A6063 근사 A6061-T6 대신 보수로 A5052)': calc(8, 5.3, TANG_OP, torque=TORQUE_M8, bolt='12.9', base='A5052', dw=13.0, dh=9.0, sf_min=3.0),
                               'note': '브래킷은 위치 잡기. 수직 하중은 레일 밑면-침목 윗면 압축(1회차 frame). 외력은 보수 가정'}
# 접시 M5 x10 -> HNTT8-5 (패널 누름): 드는 하중 없음, 조임만
out['FS_M5_panel_le3.5'] = {'calc_thread_SS400': calc(5, 3.5, 10.0, torque=TORQUE_M5, bolt='10.9', base='SS400', dw=10.4, dh=5.5, sf_min=3.0),
                            'calc_seat_SUS304': calc(5, 3.5, 10.0, torque=TORQUE_M5, bolt='10.9', base='SUS304', dw=10.4, dh=5.5, sf_min=3.0),
                            'note': '외력 10 N 보수(판 들림 없음). 좌면은 원통 자리 근사 Ø10.4 -> 실제 접시 90° 좌면은 더 넓은 경사면'}

# 3) 완료 판정 3항: 판 처짐(매트 + 바퀴 100 N) — 판·하중 경로 안 바뀜, 2회차 값 그대로
out['completion_deflection'] = {'W2_B_100N_mm': r1['summary']['완료판정3_처짐(매트+바퀴100N)_W2_B_mm'],
                                'insert_오조작_mm': r1['summary']['insert_defl_오조작_mm'],
                                'source': 'fea/results/mech_M04_fea1_handcalc.json (v2.1.4, 판 형상 v2.1.5와 같음)'}

def w(c):
    allv = dict(c['sf_operating']); allv.update(c['sf_tightening'])
    return {k: v for k, v in allv.items()}
out['summary'] = {
    'insert_step_same': out['insert_step']['same_as_fea1'],
    'CB8_15_le': le15, 'CB8_15_tip_gap': 0.5,
    'CB8_15_thread': w(thr), 'CB8_15_seat': {k: v for k, v in w(seat).items() if '좌면' in k or '볼트' in k},
    'leveler_le5.5': w(out['leveler_M8_le5.5']['calc']),
    'CB8_16_le5.3': w(out['CB8_16_bracket_le5.3']['calc_thread_SS400']),
    'FS_M5_le3.5_thread': w(out['FS_M5_panel_le3.5']['calc_thread_SS400']),
    'FS_M5_seat_SUS304': {k: v for k, v in w(out['FS_M5_panel_le3.5']['calc_seat_SUS304']).items() if '좌면' in k},
    'W2_defl_100N_mm': out['completion_deflection']['W2_B_100N_mm'],
}
json.dump(out, open(f'{ROOT}/fea/results/mech_M04_fea2_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out['summary'], ensure_ascii=False, indent=1))
