# -*- coding: utf-8 -*-
"""DC2-04 해석부 손계산 — 구멍 -> 세로 장공으로 바뀐 체결 2곳(v2.3.1).
  P_M06_BASE 붙임면 장공 2(X -70/-32, 볼트 Z 180, 장공 중심선 Z 174~184, 폭 5.5) -> UPPER 탭 CB5-12 x2
  P_M05_HOLDER 날개 A 장공 2(X 18/36, 볼트 Z 310, 중심선 Z 304~314, 폭 5.5) -> UPPER 탭 CB5-12 x2
바뀐 하중 경로: 장공 방향(Z)은 볼트 몸 받침이 없어 마찰로만 버틴다. Z 힘 = 자중·Z 외력 + 면 안 비틀림(축 Y) 짝힘.
FEA 환경 없음(D-16) -> 손계산(엔진 handcalc import). 판정 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), SF < 1.2만 '동작'.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
SF_OP, SF_MIS = 3.0, 2.0
HAND = 100.0
P = 0.5
F16 = math.pi / 4 * 16 ** 2 * P          # CJ2B16 / CDJ2B16 밀기 100.5 N (D-111 임시 0.5 MPa)
FV = 4.5e3 / (0.2 * 5)                   # 예압 T/(K d) = 4,500 N (handcalc와 같은 식, 4.5 N m)
MU = {'base': 0.15, 'what_if': 0.20}     # 건조 SUS304 - 주물/도장면 마찰(보수 0.15, 참고 0.2)
DW, DH, SLOT_W = 8.5, 5.5, 5.5            # CB5 머리 Ø8.5, 장공 폭 5.5


def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    return '됨'


def step_bbox(path):
    pts = []
    for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", open(path, encoding='latin-1').read()):
        v = [float(x) for x in m.group(1).split(',')]
        if len(v) == 3: pts.append(v)
    return {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}


def head_area_slot(dw=DW, w=SLOT_W):
    """머리 원(r = dw/2)에서 폭 w 띠(장공이 머리 지름보다 길다)를 뺀 좌면 넓이."""
    r, x = dw / 2, w / 2
    strip = 2 * (x * math.sqrt(r * r - x * x) + r * r * math.asin(x / r))
    return math.pi * r * r - strip


out = {'assume': {'P_MPa': P, 'F16_push_N': round(F16, 1), 'preload_N': FV, 'mu': MU, 'hand_misuse_N': HAND, 'g_factor': 3,
                  'U6_group_kg': 1.0, 'U7_group_kg': 2.5,
                  'mass_src': 'parts_table(v2.3.1): U6 BASE 0.32 + 실린더 0.06 + U6_SHOE 0.32 = 0.70 -> 1.0 보수. U7 CASSETTE 1.26 + FIXED 0.26 + CUT·TUCK·FEED 0.03 = 1.56 + 실린더·걸쇠 구매품 -> 2.5 보수(D-M05-2 2.0보다 큼)',
                  'UPPER_base': 'SS400 대용(867 주물, D-10)', 'pG_SUS304': 400},
       'step_bbox': {}}
for n in ('P_M06_BASE', 'P_M05_HOLDER'):
    out['step_bbox'][n] = step_bbox(f'{ROOT}/tools/out/mech_DC2-04/stepout/{n}.step')

R = {}
# ---------- 0) 머리 좌면(장공 위 CB5 머리 직접, 와셔 없음) ----------
A_round = math.pi / 4 * (DW ** 2 - DH ** 2)
A_slot = head_area_slot()
R['head_bearing'] = {'A_round_mm2': round(A_round, 1), 'A_slot_mm2': round(A_slot, 1),
                     'p_round_MPa': round(FV / A_round, 0), 'p_slot_MPa': round(FV / A_slot, 0),
                     'SF_pG_round': round(400 * A_round / FV, 2), 'SF_pG_slot': round(400 * A_slot / FV, 2), 'need': 1.0,
                     'note': '머리 Ø8.5가 장공 폭 5.5를 가로질러 좌면이 두 초승달만 남음. 기준 1.0은 넘지만 여유 20 %. 와셔(평 와셔 M5 Ø10 이상 t1 이상, SUS)를 끼우면 원래 값 이상'}
R['head_bearing']['verdict'] = '됨(기준 근처 note)' if R['head_bearing']['SF_pG_slot'] >= 1.0 else '디테일'


def slip(tag, Fz_each, Fx_each, tension_each, need, extra):
    d = {'Fz_per_bolt_N': round(Fz_each, 1), 'Fx_per_bolt_N': round(Fx_each, 1), 'F_res_N': round(math.hypot(Fz_each, Fx_each), 1),
         'bolt_tension_ext_N': round(tension_each, 1), 'need': need}
    for k, mu in MU.items():
        cap = mu * (FV - tension_each)
        sf = cap / math.hypot(Fz_each, Fx_each)
        d[f'slip_cap_mu{mu}_N'] = round(cap, 0)
        d[f'SF_slip_mu{mu}'] = round(sf, 2)
        d[f'verdict_mu{mu}'] = verdict(sf, need)
    d.update(extra)
    R[tag] = d


# ---------- 1) U6: P_M06_BASE 장공 (볼트 간 X 38, 볼트 줄 Z 180) ----------
W6 = 3 * 1.0 * G
S6 = 38.0
# 운전: 매트 말림 걸림 X 5 N + 마찰(M06과 같은 FX_OP)이 슈 끝 Z 12.5 -> 팔 167.5
FX_OP = 5.0 + 3 * 0.35 * G * 0.3
slip('U6_BASE_slot_operating', FX_OP * (180 - 12.5) / S6 + W6 / 2, FX_OP / 2, 0.0, SF_OP,
     {'load': 'X 운전 6.0 N @ 슈 끝 Z 12.5 (면 안 비틀림 짝힘) + 자중 3 g / 2'})
# 오조작 a: 실린더 로드 막힘 100.5 N(축 Z 136, 팔 44) — M06과 같은 하중
slip('U6_BASE_slot_misuse_blocked_cyl', F16 * 44 / S6 + W6 / 2, F16 / 2, F16 * 38.5 / 38, SF_MIS,
     {'load': '막힘 추력 X 100.5 @ Z 136 짝힘 + 자중, 당김은 Y 편심 몫(M06 식)'})
# 오조작 b: 손 X 100 N @ 슈 끝 Z 12.5 (M06 CARR 다리 하중과 같은 자리)
slip('U6_BASE_slot_misuse_hand_X_shoe', HAND * (180 - 12.5) / S6 + W6 / 2, HAND / 2, 0.0, SF_MIS,
     {'load': '손 X 100 @ 슈 끝 Z 12.5 -> 팔 167.5 짝힘 + 자중'})
# 오조작 c: 손 Z 100 N (캐리지 윗턱, M06 날개 외팔 하중) -> 두 볼트 같은 방향
slip('U6_BASE_slot_misuse_hand_Z', (HAND + W6) / 2, 0.0, (HAND + W6) * 49.5 / 29 / 2, SF_MIS,
     {'load': '손 Z 100 + 자중, 당김은 M06 날개 외팔 지렛대 식'})

# ---------- 2) U7: P_M05_HOLDER 날개 A 장공 (볼트 간 X 18, 볼트 줄 Z 310) ----------
W7 = 3 * 2.5 * G
S7 = 18.0
Mx_op = 50 * (300 - 40)                     # 봉제 반력 Y 50 N 의 X축 모멘트(M05 식) -> 날개 A 떼짐 T = M/25
T_op = Mx_op / 25.0 / 2
T_mis = (100 * (300 - 220) + Mx_op) / 25.0 / 2
# 운전: 테이프 장력 10 N(D-06) X 방향 @ 테이프 길 Z 약 20 -> 팔 290, + 자중
slip('U7_HOLDER_slot_operating', 10 * (310 - 20) / S7 + W7 / 2, 10 / 2, T_op, SF_OP,
     {'load': '테이프 장력 X 10 @ Z 20 짝힘 + 자중 3 g, 당김 = 봉제 반력 떼짐 몫'})
# 오조작 a: 이송 실린더 CDJ2B16(축 -Z) 로드가 매트·테이블에 막힘 -> 위로 100.5 (자중 빼지 않음)
slip('U7_HOLDER_slot_misuse_feed_blocked', F16 / 2, 0.0, T_op, SF_MIS,
     {'load': 'CDJ2B16 막힘 Z 100.5 두 볼트 같은 방향(자중 몫은 빼지 않은 보수)'})
# 오조작 b: 손 X 100 N @ 손 구멍 Z 220(M05 손 하중 자리) -> 팔 90 짝힘 + 자중
slip('U7_HOLDER_slot_misuse_hand_X_220', HAND * (310 - 220) / S7 + W7 / 2, HAND / 2, T_op, SF_MIS,
     {'load': '손 X 100 @ Z 220 짝힘 + 자중, 당김 = 봉제 반력 떼짐 몫'})
# 오조작 c: 손 Y 100 @ Z 220 (M05 오조작) -> 장공 방향 힘은 자중만, 당김은 떼짐 최대
slip('U7_HOLDER_slot_misuse_hand_Y_220', W7 / 2, HAND / 2, T_mis, SF_MIS,
     {'load': '손 Y 100(면 밖) -> Z 성분 자중만, Y 전단은 판 굽힘 받침, 당김 T 최대'})
# what-if(기록만): 손 X 100 을 카세트 바닥(바인더 Z 12.5)에 -> 팔 297.5
slip('U7_HOLDER_slot_whatif_hand_X_bottom', HAND * (310 - 12.5) / S7 + W7 / 2, HAND / 2, T_op, SF_MIS,
     {'load': 'what-if 기록만: 손 X 100 @ Z 12.5. M05 손 하중 자리(Z 220)가 아님 -> 판정에 쓰지 않음', 'whatif': True})

# ---------- 3) 볼트 자체(handcalc): 장공은 볼트 몸 하중을 줄일 뿐 키우지 않음 -> 가장 불리한 당김+전단으로 한 번 ----------
worst = max((v for k, v in R.items() if k.startswith(('U6', 'U7')) and not v.get('whatif')), key=lambda v: v['F_res_N'] + v['bolt_tension_ext_N'])
R['bolt_CB5-12_UPPER_worst'] = calc(d=5, le=9, load=round(worst['F_res_N'] + worst['bolt_tension_ext_N'], 1), torque=4.5,
                                    bolt='12.9', base='SS400', dw=DW, dh=7.42, sf_min=SF_MIS)
R['bolt_CB5-12_UPPER_worst']['_note'] = 'dh 7.42 = 장공 좌면 넓이(13.5 mm2)와 같은 환형 등가. 좌면 한계는 SS400 표값이라 SUS304 판(400) 값은 head_bearing 쪽을 본다'

# ---------- 4) 판 살: 장공으로 굽힘 단면이 바뀌는지 ----------
R['plate_section'] = {'P_M06_BASE': '굽힘 뿌리 Z 151 (장공 아래 끝 171.25 위) — 단면 그대로, M06 값 유지',
                      'P_M05_HOLDER': '떼짐 판 굽힘(굽힘선 X 46 -> 볼트 X 36 지레 10) — 장공은 Z로 길어 X 단면 그대로, M05 값 유지',
                      'edge': 'BASE 장공 위 끝 -> 판 끝 8.25(≥ 2.5), HOLDER 아래 16.25·위 17.25'}

out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_DC2-04_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    if k.startswith(('U6', 'U7')):
        print(k, v['F_res_N'], v['bolt_tension_ext_N'], v['SF_slip_mu0.15'], v['verdict_mu0.15'], v['SF_slip_mu0.2'], v['verdict_mu0.2'])
print('head', R['head_bearing'])
print('bolt', R['bolt_CB5-12_UPPER_worst']['worst'], R['bolt_CB5-12_UPPER_worst']['ok'], R['bolt_CB5-12_UPPER_worst']['sf_operating'], R['bolt_CB5-12_UPPER_worst']['sf_tightening'])
print('bbox', out['step_bbox'])
