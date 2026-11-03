# -*- coding: utf-8 -*-
"""M04 해석부 2회차 손계산 — U2 볼 테이블 수정 1회차(v2.1.4). FEA 환경 없음(D-16) -> 손계산만.
바뀐 하중 부품(모델링부 mech_M04_model1.md 2절): P_M04_INSERT(Y +-315, 밑면 턱 Y 280~315 레일 얹힘, CB8-20 x8),
  P_M04_PANEL_E1·E3(홈 X -380.5~105.5 · |Y| 300~315.5 관통), P_M04_PANEL_E2(끝 0.05), 고하중 볼 28(Steel).
안 바뀐 것(W1·W2·W3 판, 레일·침목·레벨러)은 1회차 결과 fea/results/mech_M04_handcalc.json 값을 그대로 읽는다(E-17·E-19).
판정 M-09: 운전 SF 3, 오조작 SF 2. SF < 1.2만 동작.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SY = {'SUS304': 205.0, 'A5052': 195.0, 'A6063-T5': 145.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0}
out = {}
prev = json.load(open(f'{ROOT}/fea/results/mech_M04_handcalc.json', encoding='utf-8'))

# ---------- 0) STEP bbox (v2.1.4 stepout) ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
out['step_bbox'] = {}
for n in ['P_M04_INSERT', 'P_M04_PANEL_E1', 'P_M04_PANEL_E2', 'P_M04_PANEL_E3']:
    t = open(f'{ROOT}/tools/out/mech_M04/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)],
                           'r14_circles(CB8 자리파기 O14->r7)': len(re.findall(r"CIRCLE\('[^']*',#\d+,\s*7\.?0*\s*\)", t)),
                           'r4.5_circles(O9 관통)': len(re.findall(r"CIRCLE\('[^']*',#\d+,\s*4\.50*\s*\)", t))}

WHEEL_U5 = {'기준100N(완료판정)': 100.0, '운전': 238.6, '오조작': 453.3}
WHEEL_U4 = {'운전': 153.8, '오조작': 190.9}
TANG_U4 = {'운전': 45.0, '오조작': 95.5}      # mech_M02 바퀴 접선(원판 -> 센터판)

# ---------- 1) 고하중 볼 28(STEP대기_BALL_D25H_M04, 필요 정격 550 N 임시) ----------
RATING_H = 550.0
v_ball = 26641.0                              # mm3, 모델링부 바디 부피
m_steel = v_ball * 7.85e-6                    # kg
m_nylon = v_ball * 1.14e-6
ball = {}
for cn, W in WHEEL_U5.items():
    Wt = W + (3 * m_steel * G if cn != '기준100N(완료판정)' else m_steel * G)
    ball[cn] = {'load_N': round(Wt, 1), 'SF_vs_rating550': round(RATING_H / Wt, 2)}
flange = math.pi / 4 * (44 ** 2 - 36 ** 2)
ball['flange_bearing_오조작'] = {'A_mm2': round(flange, 0), 'p_MPa': round(WHEEL_U5['오조작'] / flange, 2),
                               'note': '테 O44 / 구멍 O36 고리가 판 윗면 Z -8에 얹힘. SUS304 한계면압 400 대비 매우 작음'}
ball['_mass'] = {'steel_kg': round(m_steel, 3), 'nylon_kg': round(m_nylon, 3), 'assumed_1st_kg': 0.015,
                 'note': '1회차 판 하중은 15 g/개 가정. 모델 부피로는 수지 30 g·강 209 g. 판 자중 하중에 더해도 W2 처짐 +0.01 mm 미만(아래 2절)'}
ball['_note'] = '정격 550 N은 해석부 1회차가 낸 필요값(1.2 x 453.3 = 544)이다. 형번·실 정격 미확인(D-96, M04-X9) -> 형번이 오면 RATING_H만 바꿔 다시 셈'
out['ball_highload'] = ball

# ---------- 2) W2 바퀴 길 판(안 바뀜): 볼 무게 차만 더해 처짐 확인 ----------
w2 = prev['W2_wheel_path']
key_b100 = [k for k in w2 if k.startswith('B') and '100N' in k][0]
t = 4.0; Es = 193000.0 * 0.20; I = t ** 3 / 12
dq = (m_nylon - 0.015) * G / 50 ** 2          # 수지 볼 실부피 무게 차 (N/mm2), 1 g
dy = 5 * dq * 160.0 ** 4 / (384 * Es * I)
dP = m_steel * G                              # 바퀴 밑 강구 1개 무게(점)
dyP = 0.1851 * dP * 160.0 ** 2 / (Es * t ** 3)
out['W2_recheck'] = {'1st_B_100N_defl_mm': w2[key_b100]['defl_total_mm'], 'add_ball_mass_defl_mm': round(dy + dyP, 4),
                     'B_100N_defl_mm_now': round(w2[key_b100]['defl_total_mm'] + dy + dyP, 3),
                     'SF_운전_B': w2[[k for k in w2 if k.startswith('B') and '운전' in k][0]]['SF'],
                     'SF_오조작_B': w2[[k for k in w2 if k.startswith('B') and '오조작' in k][0]]['SF'],
                     'note': '판·레일·볼 꼭대기 하중 경로 안 바뀜. 강구로 바꿔도 하중은 바퀴 누름이 정함 -> 1회차 SF 그대로(M04-F2 디테일 유지)'}

# ---------- 3) 센터판 P_M04_INSERT 다시 만듦(Y +-315, 24.5 kg) ----------
m_ins = 9132870 * 2.68e-6                    # kg (모델링부 부피 x A5052 밀도)
m_disk = 5.0                                  # 1회차와 같은 임시
L = 600.0                                     # 레일 중심 간격(얹힘 띠 Y 280~315 -> 실 경간 약 595, 보수로 600)
bnet = 525.0 - 270.0
I_ins = bnet * 40 ** 3 / 12
ins = {}
for cn, W in WHEEL_U4.items():
    P = W + 3 * m_disk * G
    wq = 3 * m_ins * G / L
    M = P * L / 4 + wq * L * L / 8
    sg = M * 20 / I_ins
    ins[cn] = {'P_N': round(P, 1), 'sigma': round(sg, 2), 'SF': round(SY['A5052'] / sg, 1),
               'defl_mm': round(P * L ** 3 / (48 * E['A5052'] * I_ins) + 5 * wq * L ** 4 / (384 * E['A5052'] * I_ins), 4)}
# 턱 뿌리(Y +-280, 두께 12 = Z -12~0) 전단 + 굽힘: 턱은 레일 윗면에 통째로 얹혀 굽힘 팔 거의 0, 뿌리 전단만
V = (WHEEL_U4['오조작'] + 3 * (m_disk + m_ins) * G) / 2
tau = V / (525 * 12)
ins['ledge_root_shear_오조작'] = {'V_N': round(V, 1), 'tau_MPa': round(tau, 3), 'SF': round(0.577 * 195 / tau, 0)}
# 자리파기 밑 살 3 mm(Z -12~-9): 레일 홈 입구(HFS8 폭 10 가정 ±5) 위만 공중 -> 머리 O13(±6.5)은 홈 입구 양 턱에 바로 얹힘
ins['cbore_floor_3mm'] = {'t_mm': 3.0, 'span_over_slot_mm': round(10.0 - 9.0, 1),
                          'note': 'O9 관통이 홈 입구 10을 거의 덮어 살 3 mm는 레일 턱 위에서 압축만 받는다(굽힘 경간 약 0.5/쪽). 좌면은 4절 calc 조임 좌면으로 봄'}
ins['_note'] = '얹힘 폭 20 -> 35(Y 280~315)로 넓어짐, 경간·단면 사실상 그대로 -> 1회차와 같은 식. 위로 드는 하중 없음(바퀴 누름은 아래로)'
out['insert'] = ins

# ---------- 4) CB8-20 x 8 -> 레일 Y +-300 윗면 T홈 HNTT8-8 (새 체결) ----------
TORQUE = 10.0                                 # N·m 임시: 시방 없음. 알루미늄 형재 T너트 M8 흔한 값(D-16 해석부 임시, 체결부 확인)
LE_NUT = 6.0                                  # HNTT8-8 나사 길이 임시(1회차 레벨러와 같은 가정)
n_b = 8; mu = 0.2
fv = TORQUE * 1000 / (0.2 * 8)
slip = {cn: {'friction_N': round(n_b * fv * mu, 0), 'tangential_N': T, 'SF_slip': round(n_b * fv * mu / T, 1)} for cn, T in TANG_U4.items()}
# 외력 인장: 드는 하중 없음 -> 보수로 오조작 접선 전부가 한 줄(4개) 짝힘 인장으로 간다고 봄: 팔 Z 20(원판 윗면 -> 레일 윗면) / 볼트 줄 간격 X 430
F_ax = TANG_U4['오조작'] * 20.0 / 430.0 / 1 + 1.0
cb = calc(8, LE_NUT, F_ax, torque=TORQUE, bolt='12.9', base='A5052', dw=13.0, dh=9.0, sf_min=3.0)
nut = calc(8, LE_NUT, F_ax, torque=TORQUE, bolt='12.9', base='SS400', dw=13.0, dh=9.0, sf_min=3.0)
out['CB8_20'] = {'preload_N': round(fv, 0), 'slip': slip, 'F_axial_conservative_N': round(F_ax, 2),
                 'calc_seat_A5052(머리 좌면 = 센터판 살)': cb, 'calc_thread_SS400(T너트 암나사)': nut,
                 'grip_mm': {'insert_floor': 3.0, 'rail_lip': 5.5, 'sum': 8.5},
                 'bottoming_M04-X8': ('나사끝이 홈 안쪽 면과 거리 0(모델링부 K1). 조이면 끝이 먼저 닿아 예압이 센터판에 안 걸릴 수 있다. '
                                      '그때도 드는 하중이 없고 접선은 턱 단차·몸통 옆면 맞닿음으로 받으므로(1회차 4절) 동작 문제 아님 -> 디테일. CB8-16(물림 6 유지 확인)으로')}

# ---------- 5) E1·E3 홈 뒤 판 끝 얹힘 ----------
rail = (280.0, 320.0)
seat = rail[1] - 315.5
q_mat = 40.9e-6
q_plate = 7.93e-6 * 4 * (1 - math.pi / 4 * 36 ** 2 / 50 ** 2) * G
# 판 끝 띠: 홈 쪽 끝 띠 -> 다음 레일(|Y| 600 가정, 경간 300) 사이 한 방향 띠, 끝 반력
span = 600.0 - (315.5 + seat / 2)
R_line = (3 * q_plate + q_mat) * span / 2       # N/mm, 자중 3 g + 매트
# 작업자 100 N 이 판 끝(홈 가장자리)에 바로: 유효 폭 2 x 25(판 t4 퍼짐 가정 보수)로 얹힘 띠에
p_worker = 100.0 / (seat * 50.0)
# 끝 띠를 짚었을 때 가장자리 구멍 없는 띠(구멍은 레일 줄 |Y-300|<38 안 없음 -> 홈 끝 ~ Y 338 민판) 외팔 아님(레일 위) -> 처짐 거의 0
eh = {'seat_nominal_mm': round(seat, 1), 'seat_after_tol_mm': round(seat - 0.5 - 0.5, 1),
      'tol_note': '판 절단 ±0.2·레일 놓임 ±0.3(임시) + 레일 윗모서리 모따기 약 0.5(HFS8 외형도 임시) -> 실 얹힘 약 3.5',
      'strip_span_to_next_rail_mm': round(span, 1), 'edge_reaction_N_per_mm_3g': round(R_line, 4),
      'bearing_worker100N_MPa': round(p_worker, 2),
      'edge_strip_beam_worker100N(얹힘 놓쳤을 때 외팔 22.75 = 홈 4.5 + 레일 반폭 18.25)':
          beam(4.0, 50.0, 22.75, load=100.0, e=193000.0, sy=205.0, end='cantilever', sf_min=3.0),
      'note': ('X -380.5~105.5 구간만 판 끝이 레일 Y +-300(Y 280~320) 바깥 4.5 mm에 얹힌다(전엔 반폭 20). '
               '힘은 작아 강도 문제 아님. 얹힘이 좁아 공차가 쌓이면 판 끝이 레일에서 떨어져 빈 틈 위에 뜬다(볼 없음 띠라 매트는 판 위 아님, 볼 꼭대기 Z 0이 받음) -> 디테일')}
# 얹힘을 놓쳤을 때(최악): 판 끝이 다음 지지까지 외팔 -> 위 beam(유효 폭 50) 은 보수. 판 끝은 E1/E3 다른 구간·센터판 옆면과 이어져 실제로는 세 변 지지
out['E1_E3_slot_edge'] = eh

# ---------- 6) 요약 ----------
out['summary'] = {
    '완료판정3_처짐(매트+바퀴100N)_W2_B_mm': out['W2_recheck']['B_100N_defl_mm_now'],
    '고하중볼_SF_운전': ball['운전']['SF_vs_rating550'], '고하중볼_SF_오조작': ball['오조작']['SF_vs_rating550'],
    'W2_SF_운전_B(그대로)': out['W2_recheck']['SF_운전_B'], 'W2_SF_오조작_B(그대로)': out['W2_recheck']['SF_오조작_B'],
    'insert_SF_오조작': ins['오조작']['SF'], 'insert_defl_오조작_mm': ins['오조작']['defl_mm'],
    'CB8_preload_N': round(fv, 0), 'CB8_slip_SF_오조작': slip['오조작']['SF_slip'],
    'CB8_seat_worst': cb['worst'], 'CB8_seat_ok': cb['ok'], 'CB8_sf_tight': cb['sf_tightening'],
    'Tnut_sf_tight': nut['sf_tightening'], 'Tnut_ok': nut['ok'],
    'E1E3_seat_mm': eh['seat_nominal_mm'], 'E1E3_seat_after_tol_mm': eh['seat_after_tol_mm'],
    'E1E3_edge_cantilever_SF(최악)': eh['edge_strip_beam_worker100N(얹힘 놓쳤을 때 외팔 22.75 = 홈 4.5 + 레일 반폭 18.25)'].get('sf'),
}
json.dump(out, open(f'{ROOT}/fea/results/mech_M04_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out['summary'], ensure_ascii=False, indent=1))
for n, v in out['step_bbox'].items():
    print(n, v['min'], v['max'], v['r14_circles(CB8 자리파기 O14->r7)'], v['r4.5_circles(O9 관통)'])
