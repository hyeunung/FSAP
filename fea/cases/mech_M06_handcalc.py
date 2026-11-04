# -*- coding: utf-8 -*-
"""M06 해석부 손계산 — U6 슈·가장자리 센서(J_U6_SHIFT, CJ2B16-60SZ) + U7 롤 걸이·안내 롤러 (v2.3.0).
FEA 환경 없음(D-16) -> 손계산만(엔진 handcalc import).
형상: 모델링부 mech_M06_model.md 2절 좌표 + stepout STEP bbox(0절에서 다시 읽어 맞춤).
하중: 실린더 추력(요구서 2-4 운전 압력 미정 -> 앞 과제와 같은 0.5 MPa 임시, D-111), 손 오조작 100 N(D-79·D-83과 같은 값),
      롤 3 kg·장력 5 N(D-124), 자중 x3 g. 판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2만 '동작'.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
P = 0.5
SY = {'SUS304': 205.0, 'A5052': 195.0, 'S45C': 345.0, 'PET-CF': 60.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0, 'S45C': 205000.0, 'PET-CF': 5000.0}
SF_OP, SF_MIS = 3.0, 2.0
HAND = 100.0
out = {'assume': {'P_MPa': P, 'hand_misuse_N': HAND, 'roll_kg': 3.0, 'tape_tension_N': 5.0, 'g_factor': 3,
                  'UPPER_base': 'SS400 대용(867 주물 FC급, D-10) — handcalc 표에 FC 없음',
                  'U1_BEAM_base': 'A5052 대용(보 재질 표 값보다 낮은 쪽)',
                  'PET-CF': '항복 60(handcalc 표), E 5,000(설계안 값), FDM 층간은 기록'}}

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

def res(name, F, M, Z, mat, need, extra=None):
    s = M / Z
    sf = SY[mat] / s
    d = {'F_N': round(F, 1), 'M_Nmm': round(M, 0), 'Z_mm3': round(Z, 1), 'sigma_MPa': round(s, 2), 'mat': mat,
         'SF': round(sf, 2), 'need': need, 'verdict': verdict(sf, need)}
    if extra: d.update(extra)
    R[name] = d

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
names = ['P_M06_BASE', 'P_M06_CARR', 'P_M06_SHOE', 'P_M06_ROLL_POST', 'P_M06_ROLL_SHAFT', 'P_M06_ROLL_HUB',
         'P_M06_G1_BRKT', 'P_M06_TOP_BRKT', 'P_M06_G1_PIN', 'P_M06_TOP_PIN']
out['step_bbox'] = {}
for n in names:
    t = open(f'{ROOT}/tools/out/mech_M06/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)] if pts else None,
                           'max': [round(max(c), 2) for c in zip(*pts)] if pts else None}

F16 = math.pi / 4 * 16 ** 2 * P
out['thrust'] = {'CJ2B16_push_N': round(F16, 1), 'need_N': 2.3,
                 'note': '단동 스프링 복귀. 로드가 막혔을 때 전 추력이 슈·캐리지·BASE로 간다고 본 보수값(스프링 몫 빼지 않음)'}
R = {}
FX = max(F16, HAND)   # 슈 X 방향: 막힘 추력 100.5 / 손 100 중 큰 쪽 (오조작)
FX_OP = 5.0 + 3 * 0.35 * G * 0.3   # 운전: 매트 말림 걸림 5 N + 마찰

# ---------- 1) U6 BASE (SUS304 t3) ----------
# 실린더 탭 X -142~-139, 폭 Y 30(-145~-115), 굽힘선 Z 148, 실린더 축 Z 136 -> 팔 12
res('BASE_cyl_tab_root', F16, F16 * 12, 30 * 3 ** 2 / 6, 'SUS304', SF_MIS)
# 날개(Y 75 x t3)가 X 추력을 붙임면까지 축력으로 + 축 Z 136 / 날개 가운데 149.5 편심 13.5 굽힘(축 Y): Z = 75*9/6
res('BASE_wing_eccentric', F16, F16 * 13.5, 75 * 3 ** 2 / 6, 'SUS304', SF_MIS,
    {'axial_MPa': round(F16 / (75 * 3), 2)})
# 날개 외팔 Z 하중: 움직이는 몫 0.35 kg x3 g + 손 100 N이 캐리지 윗턱을 누름(오조작), 팔 = 붙임면 Y -91.5 -> 캐리지 가운데 Y -141 = 49.5
res('BASE_wing_cantilever_Z_misuse', HAND + 3 * 0.35 * G, (HAND + 3 * 0.35 * G) * 49.5, 58 * 3 ** 2 / 6, 'SUS304', SF_MIS,
    {'note': '굽힘 뿌리는 붙임면 굽힘선(X -80~-22, 폭 58)'})
# 붙임면 볼트 CB5-12 x2 (X -70/-32, Z 180, 축 Y) -> UPPER M5 탭 물림 9
#   X 추력: 볼트당 전단 F/2 + 축 Z 136 편심 44 -> 면 안 비틀림(볼트 간격 38, r 19) 전단 M/(2r)
#   Y 편심(축 Y -130 / 면 -91.5 = 38.5) -> 축 Z 모멘트 -> 볼트 당김 M/38
#   Z 손 하중 100 N 팔 49.5 -> 받침 Z 151 / 볼트 Z 180 = 29 -> 당김
sh = math.hypot(F16 / 2, F16 * 44 / 38)
tn = F16 * 38.5 / 38 + (HAND + 3 * 0.35 * G) * 49.5 / 29 / 2
R['BASE_bolt_CB5-12_UPPER'] = calc(d=5, le=9, load=round(math.hypot(sh, tn), 1), torque=4.5, bolt='12.9', base='SS400', sf_min=SF_MIS)
R['BASE_bolt_CB5-12_UPPER']['_load'] = {'shear_N': round(sh, 1), 'tension_N(막힘 추력 + 손 Z 동시, 보수)': round(tn, 1)}

# ---------- 2) U6 CARR (PET-CF FDM) ----------
# 다리 12(X) x 85(Y), X 힘이 슈 밑(Z 12.5~30) -> 아랫턱 뿌리 Z 124, 팔 약 111.5 (막힘 추력 축 Z 136 / 손 슈 끝 Z 12.5)
L = 124 - 12.5
I = 85 * 12 ** 3 / 12
res('CARR_leg_X_misuse', FX, FX * L, 85 * 12 ** 2 / 6, 'PET-CF', SF_MIS,
    {'defl_mm': round(FX * L ** 3 / (3 * E['PET-CF'] * I), 3), 'note': 'FDM 층 방향이 Z(세워 출력)면 층간 강도 약 0.5배 -> SF 반으로 기록'})
res('CARR_leg_X_operating', FX_OP, FX_OP * L, 85 * 12 ** 2 / 6, 'PET-CF', SF_OP,
    {'defl_mm': round(FX_OP * L ** 3 / (3 * E['PET-CF'] * I), 4)})
# 다리 Y 손 하중(슈 입술 끝을 옆으로) — 강축 85: Z = 12*85^2/6
res('CARR_leg_Y_misuse', HAND, HAND * L, 12 * 85 ** 2 / 6, 'PET-CF', SF_MIS)
# 로드 인서트 M5(아랫턱 -X 면): 밀기는 로드 너트가 -X 면을 누름(면압), 당김(스프링 복귀 약 15 N 가정)은 인서트 빠짐 — 인서트 빠짐 약 1,000 N(열압입 M5 PET 흔한 값)
R['CARR_rod_nut_bearing'] = {'F_N': round(F16, 1), 'area_mm2(너트 맞변 8 - 구멍 5.5)': round(8 ** 2 * 0.866 - math.pi / 4 * 5.5 ** 2, 1),
                             'p_MPa': round(F16 / (8 ** 2 * 0.866 - math.pi / 4 * 5.5 ** 2), 2), 'p_G_PET-CF': 60,
                             'SF': round(60 / (F16 / (8 ** 2 * 0.866 - math.pi / 4 * 5.5 ** 2)), 1)}
R['CARR_rod_nut_bearing']['verdict'] = verdict(R['CARR_rod_nut_bearing']['SF'], SF_MIS)

# ---------- 3) U6 SHOE (SUS304 t2) ----------
# 바닥 X -20~1(21) 이 세운 벽 X -20에서 외팔. 손 100 N Z(위로 밀기)
#   (a) 손바닥: 바닥 끝 X 1 선하중, 뿌리 폭 = 벽 길이 Y 80
res('SHOE_floor_palm_misuse', HAND, HAND * 21, 80 * 2 ** 2 / 6, 'SUS304', SF_MIS)
R['SHOE_floor_palm_beam'] = beam(t=2.0, b=80.0, length=21.0, load=HAND, e=E['SUS304'], sy=SY['SUS304'], sf_min=SF_MIS)
#   (b) 손끝 한 점: 입술 모서리(X 1, Y -205) — 벽 끝 Y -195 밖 10, 유효 폭 = 팔 21 + 입술 10 내밈(45° 퍼짐 한쪽) 보수
res('SHOE_floor_corner_point_misuse', HAND, HAND * math.hypot(21, 10), (21 + 10) * 2 ** 2 / 6, 'SUS304', SF_MIS,
    {'note': '판 모서리 점하중 보수식(유효 폭 31). 보로 보기 어려운 형상 -> 환경 생기면 셸 FEA'})
# 세운 벽(t2, 높이 32.5) 면 안 굽힘: 손 Z 100 N 입술 끝 Y -205 -> 볼트 Y -175 팔 30
res('SHOE_wall_inplane', HAND, HAND * 30, 2 * 32.5 ** 2 / 6, 'SUS304', SF_MIS)
# 운전: 매트 가장자리 옆 하중 5 N(설계안 임시) — 바닥/벽 판 굽힘(벽 높이 32.5 뿌리 볼트 Z 32.5 -> 바닥 Z 12.5 팔 20, 폭 80)
res('SHOE_wall_side_operating', FX_OP, FX_OP * 20, 80 * 2 ** 2 / 6, 'SUS304', SF_OP)
# 슈 볼트 CB5-12 x2 -> 다리 M5 인서트(PET-CF): X 손 100 N이 슈를 -X로 당기는 쪽(볼트 당김) + 편심 Z(32.5 -> 12.5 = 20, 볼트 간 Y 40 X 모멘트는 판 받침)
R['SHOE_bolt_CB5-12_insert'] = {'F_per_bolt_N': round(FX / 2 + HAND * 20 / 15 / 2, 1),
                                'insert_pullout_N(열압입 M5 PET 흔한 값, 임시)': 1000.0}
R['SHOE_bolt_CB5-12_insert']['SF'] = round(1000.0 / R['SHOE_bolt_CB5-12_insert']['F_per_bolt_N'], 1)
R['SHOE_bolt_CB5-12_insert']['verdict'] = verdict(R['SHOE_bolt_CB5-12_insert']['SF'], SF_MIS)

# ---------- 4) U7 ROLL_SHAFT (S45C Ø20 외팔, 플랜지 면 Y 102) ----------
Wroll = 3 * 3.0 * G
L_roll = 102 - (-110)
L_tip = 102 - (-142)
M_op = (Wroll + 5.0) * L_roll
M_mis = Wroll * L_roll + HAND * L_tip
Zs = math.pi * 20 ** 3 / 32
Is = math.pi * 20 ** 4 / 64
res('SHAFT_root_operating', Wroll + 5.0, M_op, Zs, 'S45C', SF_OP, {'Kt_fillet_note': 'Ø20->플랜지 모서리 Kt 약 1.5 기록'})
res('SHAFT_root_misuse', Wroll + HAND, M_mis, Zs, 'S45C', SF_MIS)
R['SHAFT_root_misuse_Kt1.5'] = {'SF': round(R['SHAFT_root_misuse']['SF'] / 1.5, 2)}
R['SHAFT_defl_tip_operating_mm'] = round((Wroll + 5.0) * L_roll ** 2 * (3 * L_tip - L_roll) / (6 * E['S45C'] * Is), 3)
# 플랜지 볼트 CB5-16 x3 PCD 36, 플랜지 t8 -> 기둥 A5052 물림 8. 받침 = 플랜지 바깥 r 25 아래 모서리
d = [25 + 18, 25 - 9, 25 - 9]
for tag, M in (('operating', M_op), ('misuse', M_mis)):
    T = M * max(d) / sum(x * x for x in d)
    R[f'SHAFT_flange_bolt_CB5-16_{tag}'] = calc(d=5, le=8, load=round(T + (Wroll + HAND) / 3, 1), torque=4.5, bolt='12.9',
                                                base='A5052', sf_min=SF_OP if tag == 'operating' else SF_MIS)

# ---------- 5) U7 ROLL_POST (A5052 t10 x 60, Y 110~120, Z 605~780) ----------
# 축 모멘트 M(축 X)이 판을 면 밖으로 굽힘. 위 볼트 Z 640 ~ 축 Z 750 사이 일정 모멘트. Z = 60*10^2/6
for tag, M, need in (('operating', M_op, SF_OP), ('misuse', M_mis, SF_MIS)):
    res(f'POST_plate_{tag}', Wroll + (5.0 if tag == 'operating' else HAND), M, 60 * 10 ** 2 / 6, 'A5052', need)
Ip = 60 * 10 ** 3 / 12
th = M_op * 110 / (E['A5052'] * Ip)
R['POST_tilt_operating'] = {'rad': round(th, 5), 'roll_center_drop_mm': round(th * L_roll + R['SHAFT_defl_tip_operating_mm'], 2),
                            'note': '롤 걸이 처짐은 동작 판정 대상 아님(롤-기둥·이웃 틈은 측정부 값). 기록'}
# 보 볼트 CB5-20 x2 (Z 615, 640) — 판 밑 모서리 Z 605가 보 앞면을 누르는 지렛대. 물림 13 탭(보 재질 A5052 대용)
dd = [615 - 605, 640 - 605]
for tag, M in (('operating', M_op), ('misuse', M_mis)):
    T = M * max(dd) / sum(x * x for x in dd)
    R[f'POST_beam_bolt_CB5-20_{tag}'] = calc(d=5, le=13, load=round(math.hypot(T, (Wroll + HAND) / 2), 1), torque=4.5,
                                             bolt='12.9', base='A5052', sf_min=SF_OP if tag == 'operating' else SF_MIS)

# ---------- 6) 6004ZZ, HUB ----------
R['BRG_6004ZZ'] = {'radial_max_N(오조작 한 개가 다 받음)': round(Wroll + HAND, 1), 'C0r_N': 5000, 'SF0': round(5000 / (Wroll + HAND), 1)}
# 허브 베어링 자리 Ø42 PET-CF 면압: 투영 42 x 12
R['HUB_seat_bearing'] = {'p_MPa': round((Wroll + HAND) / (42 * 12), 3), 'SF': round(60 / ((Wroll + HAND) / (42 * 12)), 0)}

# ---------- 7) 안내 롤러 핀 Ø10 (SUS304) ----------
# 자루 뿌리 Y -91.5(턱 Ø14 앞). 손 100 N 롤러 끝(머리 쪽 Y -127.5) 팔 36 / 운전 장력 합 7.1 N 롤러 가운데 팔 18
Zp = math.pi * 10 ** 3 / 32
res('PIN_root_misuse', HAND, HAND * 36, Zp, 'SUS304', SF_MIS)
res('PIN_root_operating', 5 * math.sqrt(2), 5 * math.sqrt(2) * 18, Zp, 'SUS304', SF_OP)
# 핀 당김 볼트 CB5-12(+Y에서, 핀 뒤끝 M5 탭 SUS304): 턱 Ø14 받침 반지름 7, 판 면 모멘트 = 손 x (판 -88 -> 롤러 가운데 -109.5)
Tpin = HAND * 21.5 / 7
R['PIN_pull_bolt_CB5-12'] = calc(d=5, le=8, load=round(Tpin, 1), torque=4.5, bolt='12.9', base='SUS304', sf_min=SF_MIS)

# ---------- 8) G1_BRKT / TOP_BRKT (SUS304 t3 L) ----------
for nm, wv, wf in (('G1', 75.0, 40.0), ('TOP', 50.0, 50.0)):
    # 세운 판 굽힘선(발 Z) 면 밖: 손 100 N(Z 또는 X)이 핀 축 Y -109.5 -> 판 가운데 -86.5 팔 23
    res(f'{nm}_BRKT_upright_misuse', HAND, HAND * 23, wv * 3 ** 2 / 6, 'SUS304', SF_MIS)
    # 발판 굽힘(Y -85 굽힘선 -> 볼트 줄 Y -74): 핀 Z 하중이 굽힘 넘어감, 팔 -85 -> -109.5 = 24.5
    res(f'{nm}_BRKT_foot_misuse', HAND, HAND * 24.5, wf * 3 ** 2 / 6, 'SUS304', SF_MIS)
    res(f'{nm}_BRKT_foot_operating', 5 * math.sqrt(2), 5 * math.sqrt(2) * 24.5, wf * 3 ** 2 / 6, 'SUS304', SF_OP)
    R[f'{nm}_BRKT_upright_beam_misuse'] = beam(t=3.0, b=wv, length=23.0, load=HAND, e=E['SUS304'], sy=SY['SUS304'], sf_min=SF_MIS)
    # 발 볼트 x2: 받침 = 발 +Y 끝 Y -60, 볼트 줄 Y -74 (팔 14), 하중 줄 Y -109.5 (팔 49.5)
    T = HAND * 49.5 / 14 / 2
    if nm == 'G1':
        R['G1_BRKT_bolt_CB5-12_UPPER'] = calc(d=5, le=9, load=round(T, 1), torque=4.5, bolt='12.9', base='SS400', sf_min=SF_MIS)
    else:
        R['TOP_BRKT_bolt_CB5-20_UPPER'] = calc(d=5, le=9, load=round(T, 1), torque=4.5, bolt='12.9', base='SS400', sf_min=SF_MIS)

out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_M06_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 요약
for k, v in R.items():
    if isinstance(v, dict):
        sf = v.get('SF', v.get('sf', v.get('SF_yield', '')))
        print(k, sf, v.get('verdict', v.get('ok', '')))
    else:
        print(k, v)
