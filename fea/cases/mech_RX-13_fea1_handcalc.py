# -*- coding: utf-8 -*-
"""RX-13 해석부 손계산(2026-11-23, v2.20.4). FEA 못 함 — 환경 없음(D-16).
새 하중 부품: P_RX13_CYL_BRKT_밀링(SUS304), P_RX13_ROD_EXT_선반(SUS303),
고친 부품: P_M02_BASE(보 밑 연장 지움·통과 구멍 Ø5.5 x4·장공 반달 자리 R4 x2), P_RX06_CARRIAGE(발 장공 반달 자리 R4 x2).
하중 길: 로드(+Y 밂 = 들기 / -Y 당김 = 누름) -> 실린더 몸 -> (밂) 머리 쪽 면이 앞벽을 누름 / (당김) CB6-16 x4 인장
        -> 앞벽 -> 귀 2 -> CB5-16 x4 -> 윗판 P_M02_BASE -> 피벗 쪽으로 닫힌 고리(Y 힘). 캐리지에는 자중 x3 g와 바퀴 힘만 간다.
형상 근거: fea/results/mech_RX-13_stepgeo.json · mech_RX-13_stepcirc.json (STEP v2.20.4 bbox·구멍), 질량 tools/out/signatures.json.
힘 근거: tools/out/mech_RX-13/design/swing_rx13.json (핀 힘·텅 기울기), 요구서 2-4 공급 0.5 MPa.
실행: python -X utf8 -B fea/cases/mech_RX-13_fea1_handcalc.py
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SW = json.load(open(ROOT + '/tools/out/mech_RX-13/design/swing_rx13.json', encoding='utf-8'))
SF_OP, SF_MIS = 3.0, 2.0            # 요구서 6-1 비어 M-09 기본값(fea/models.json criteria)
SY = {'SUS304': 205.0, 'SUS303': 205.0, 'S45C': 345.0, 'A5052': 195.0}
E_SUS = 193000.0
g = 9.81
R = {'_설명': 'RX-13 해석부 손계산. 좌표 = 월드, J_U4_X 0, REST(들림 13.006). 판정 운전 SF 3 · 오조작 SF 2, SF < 1.2는 영구 변형(동작)'}


def sf_rec(name, sig_op, sig_mis, mat, note=''):
    s_op, s_mis = SY[mat] / sig_op, SY[mat] / sig_mis
    R[name] = {'sigma_op_MPa': round(sig_op, 1), 'sigma_mis_MPa': round(sig_mis, 1), 'SF_op': round(s_op, 2), 'SF_mis': round(s_mis, 2),
               'ok': s_op >= SF_OP and s_mis >= SF_MIS, 'yield_ok': min(s_op, s_mis) >= 1.2,
               'near_limit': (0.9 * SF_OP <= s_op <= 1.1 * SF_OP) or (0.9 * SF_MIS <= s_mis <= 1.1 * SF_MIS), 'material': mat, 'note': note}


# ---------- 0. 하중 ----------
A_push, A_pull = SW['A_lift_push'], SW['A_press_pull']        # 314.16 · 235.62 mm2
P_SUP, P_REG_MAX = 0.5, 0.2                                    # 공급(요구서 2-4) · IR1000 상한
F_push = P_SUP * A_push                                        # 들기(밸브 B, 공급압 그대로) — 운전이자 오조작
F_pull_op, F_pull_mis = P_REG_MAX * A_pull, P_SUP * A_pull     # 누름: 운전 = IR1000 상한, 오조작 = 레귤레이터 고장
hold = SW['spring_kept_f6.28']['rod_force_hold_air0_N']
F_pin_lift = hold['lift(밑 40, +30)']                          # 들림 유지 때 핀 힘 60.4 N
TILT_LIFT, TILT_SEW, TILT_END = 8.2, 4.8, 8.9                  # 텅 장공 기울기(°) 들림 / 봉제 / 누름 끝 (설계안 2절)
MU = 0.15                                                      # 핀(S45C)–텅 장공(SUS304) 미끄럼 마찰(윤활, 임시 — 보수로 옆힘에 더함)
m = {'cyl': 0.1986, 'brkt': 0.2013, 'rod': 0.0303, 'ext': 0.0564, 'nut': 0.0043, 'knuckle': 0.0770, 'pin': 0.0110,
     'cb6x4': 4 * 0.00662, 'cb5x4': 4 * 0.00436, 'elbow_x2': 2 * 0.00167}   # kg, signatures.json(v2.20.4)
m_rodgrp = m['rod'] + m['ext'] + m['nut'] + m['knuckle'] + m['pin']


def side(F, tilt):
    """핀이 받는 로드 축 직각 힘(Z): 장공 벽 수직력의 Z 몫 + 장공 길이 방향 마찰(보수로 같은 쪽) + 로드 묶음 자중 x3 g의 절반"""
    t = math.tan(math.radians(tilt))
    return F * (t + MU) / (1 - MU * t) + 0.5 * m_rodgrp * 3 * g


S = {'op_lift_hold': side(F_pin_lift, TILT_LIFT), 'op_press_end_0.2': side(F_pull_op, TILT_END),
     'mis_pull_0.5_press_end': side(F_pull_mis, TILT_END), 'mis_pull_0.5_sew': side(F_pull_mis, TILT_SEW),
     'mis_push_jam_lift': side(F_push, TILT_LIFT)}
S_noMu = {'op_lift_hold': F_pin_lift * math.tan(math.radians(TILT_LIFT)), 'mis_pull_0.5_press_end': F_pull_mis * math.tan(math.radians(TILT_END)),
          'mis_push_jam_lift': F_push * math.tan(math.radians(TILT_LIFT))}
R['load'] = {'F_push_0.5MPa_N': round(F_push, 1), 'F_pull_op_0.2MPa_N': round(F_pull_op, 1), 'F_pull_mis_0.5MPa_N': round(F_pull_mis, 1),
             'F_pin_lift_hold_N': F_pin_lift, 'mu_slot(임시)': MU, 'side_N': {k: round(v, 1) for k, v in S.items()},
             'side_N_마찰·자중 뺌(설계안 방식)': {k: round(v, 1) for k, v in S_noMu.items()},
             'm_rod_group_kg': round(m_rodgrp, 3),
             '_note': '들기 끝에서는 실린더 스트로크 끝(로드 값 24.994/25)이 받아 핀에는 60.4 N만 간다. mis_push_jam_lift는 들림 도중 그네가 막혀 0.5 MPa 밂 157 N이 전부 핀에 걸리는 보수 경우'}

# ---------- 1. P_RX13_CYL_BRKT (SUS304) ----------
# 앞벽 X -275~-205(70) · Y -45.1~-38.1(t7) · Z 203~242(39), 귀 2: X 폭 16 · Y -38.1~-8.1 · Z 234~242(t8)
# 귀 M5 탭 Y -31.1 · -15.1, 앞벽 Ø6.6 x4 (X -252.75·-227.25, Z 210.25·235.75), 로드 축 Z 223, 윗판 맞닿는 면 Z 242
ARM_Z = 242.0 - 223.0                                          # 축 ~ 맞닿는 면 19
W_cyl = (m['cyl'] + m['cb6x4'] + m['elbow_x2']) * 3 * g        # 실린더 몸 쪽 자중 x3 g
W_rod = m_rodgrp * 3 * g                                       # 로드 묶음(보수: 핀이 안 받친다고 봄)
M_w_wall = W_cyl * (-8.35 + 38.1) + W_rod * (90.0 + 38.1)      # 앞벽 뒷면(Y -38.1) 둘레 자중 모멘트 N·mm
W_all = W_cyl + W_rod + (m['brkt'] + m['cb5x4']) * 3 * g

# 1-1 귀: 첫 탭(Y -31.1) 순 단면 (16 - 5) x 8, 모멘트 = 축 힘 x 19의 절반(귀 2), + 귀 인장
Z_ear = (16.0 - 5.0) * 8.0 ** 2 / 6
A_ear = (16.0 - 5.0) * 8.0


def ear(F):
    return (F * ARM_Z / 2 + M_w_wall / 2) / Z_ear + F / 2 / A_ear


sf_rec('brkt_ear_net', ear(F_push), ear(F_push), 'SUS304',
       f'순 단면 11 x 8(Z {Z_ear:.0f}), 팔 {ARM_Z:.0f}(축 Z 223 ~ 면 Z 242). 설계안은 팔 15(귀 가운데) 10 MPa. 안쪽 모서리 날카로움 Kt 3 가정 봉우리 {3 * ear(F_push):.0f} MPa(SF {205 / (3 * ear(F_push)):.1f}) — 연성 정하중이라 판정엔 안 씀(RX-13-K3)')
# 1-2 앞벽: (i) 귀 사이 X 방향 보(경간 54, 폭 36 분포 하중, 높이 39 - 구멍 2 x 6.6) (ii) 귀 옆 벽 띠(폭 16)가 축 Z 223 -> 귀 Z 238까지 외팔 15
Z_wall_x = (39.0 - 2 * 6.6) * 7.0 ** 2 / 6
M_wall_x = F_push / 2 * 27.0 - F_push / 2 * 9.0
Z_wall_loc = 16.0 * 7.0 ** 2 / 6
M_wall_loc = F_push / 2 * (238.0 - 223.0)
sf_rec('brkt_wall_span', M_wall_x / Z_wall_x, M_wall_x / Z_wall_x, 'SUS304', f'귀 사이 보: M {M_wall_x:.0f} N·mm, Z {Z_wall_x:.0f}')
sf_rec('brkt_wall_local', M_wall_loc / Z_wall_loc, M_wall_loc / Z_wall_loc, 'SUS304', f'귀 옆 띠 16 x 7 외팔 15: M {M_wall_loc:.0f} N·mm, Z {Z_wall_loc:.0f}(퍼짐 무시 = 보수)')
# 1-3 기울어짐 -> 핀 자리 처짐(로드 정렬)
th_ear = (F_push * ARM_Z / 2) * 7.0 / (E_SUS * (11.0 * 8.0 ** 3 / 12))
th_wall = M_wall_loc * 15.0 / (E_SUS * (16.0 * 7.0 ** 3 / 12))
R['brkt_tilt'] = {'theta_ear_rad': round(th_ear, 6), 'theta_wall_rad': round(th_wall, 6), 'pin_dz_mm(팔 170)': round((th_ear + th_wall) * 170.0, 3),
                  'note': '0.5 MPa 밂 157 N. 핀은 장공 길이 방향(거의 Z)으로 미끄러져 흡수 — 너클 갈래 옆 틈 0.2, 로드 구멍 틈 0.25보다 작다(기록, 6-2 처짐 기준 미정 D-08)'}
# 1-4 볼트
T_m5_push = F_push * ARM_Z / 16.0 / 2                          # 보수: 볼트 두 줄 간격 16을 우력 팔로, 앞줄 2개가 받음
T_m5_w = W_all / 4 + (m['brkt'] * 3 * g * 27.0) / 16.0 / 2
T_m5 = T_m5_push + T_m5_w
R['CB5-16_RX13_BRKT(M5, SUS304 귀 탭 물림 8)'] = calc(d=5, le=8, load=round(T_m5, 1), base='SUS304', sf_min=SF_OP)
T_m6_op = F_pull_op / 4 + M_w_wall / 25.5 / 2
T_m6_mis = F_pull_mis / 4 + M_w_wall / 25.5 / 2
R['CB6-16_RX13_CYL(M6, 실린더 몸 알루미늄 탭 물림 9) 운전'] = calc(d=6, le=9, load=round(T_m6_op, 1), base='A5052-H112', sf_min=SF_OP)
R['CB6-16_RX13_CYL(M6, 실린더 몸 알루미늄 탭 물림 9) 오조작'] = calc(d=6, le=9, load=round(T_m6_mis, 1), base='A5052-H112', sf_min=SF_MIS)
R['brkt_slip'] = {'shear_N': round(F_push, 1), 'preload_N_x4(M5 12.9 7 N·m 일반값 D-108)': 4 * 7000.0, 'mu': 0.15,
                  'SF': round(4 * 7000.0 * 0.15 / F_push, 1), 'T_m5_N_each': round(T_m5, 1), 'T_m6_N_each_op_mis': [round(T_m6_op, 1), round(T_m6_mis, 1)],
                  'note': '실린더 몸 재질은 임시 형상이라 가장 약한 A5052-H112(110)로 봄. 볼트 힘이 예압보다 훨씬 작아 이음 안 벌어짐'}

# ---------- 2. 로드 사슬: 로드 수나사 M8x1.25 -> P_RX13_ROD_EXT(Ø14, SUS303) -> 잠금 너트 -> 너클 -> 핀 ----------
d3 = 8.0 - 1.22687 * 1.25                                       # M8x1.25 골 지름 6.466
Z_m8 = math.pi * d3 ** 3 / 32
A_m8 = math.pi * d3 ** 2 / 4
ARM_ROD_ROOT = 131.894 - 50.894                                 # 핀 ~ 로드 수나사 뿌리(로드 너트 앞면) 81.0 — 자세와 무관(로드와 같이 감)
ARM_EXT_ROOT = 131.894 - 100.894                                # 핀 ~ 연장봉 수나사 뿌리 31.0
ARM_BUSH_LIFT, ARM_BUSH_END = 131.894 - 21.4, 107.016 - 21.4   # 핀 ~ 로드 쪽 면(부시) 110.5 / 85.6
ARM_M02R = 26.0 + 5.0                                           # 옛 M02R: 너클 면~핀 26 + 너트 5


def rod_sig(Fax, Fs, arm, Z=Z_m8, A=A_m8):
    return Fs * arm / Z + Fax / A


cases = {'op_lift_hold': (F_pin_lift, S['op_lift_hold']), 'op_press_end_0.2': (F_pull_op, S['op_press_end_0.2']),
         'mis_pull_0.5_press_end': (F_pull_mis, S['mis_pull_0.5_press_end']), 'mis_pull_0.5_sew': (F_pull_mis, S['mis_pull_0.5_sew']),
         'mis_push_jam_lift': (F_push, S['mis_push_jam_lift'])}
rod = {}
for k, (Fax, Fs) in cases.items():
    need = SF_OP if k.startswith('op') else SF_MIS
    s_root = rod_sig(Fax, Fs, ARM_ROD_ROOT)
    s_ext = rod_sig(Fax, Fs, ARM_EXT_ROOT)
    s_old = rod_sig(Fax, Fs, ARM_M02R)
    rod[k] = {'side_N': round(Fs, 1), 'M_root_Nmm': round(Fs * ARM_ROD_ROOT), 'sigma_rod_root_MPa': round(s_root, 1),
              'SF_rod_root(SUS304 205 보수)': round(205 / s_root, 2), 'SF_rod_root(S45C 345, 모델 재질)': round(345 / s_root, 2),
              'sigma_ext_male_root_MPa': round(s_ext, 1), 'SF_ext_male_root(SUS303 205)': round(205 / s_ext, 2),
              'SF_옛 M02R 팔 31(SUS304 205)': round(205 / s_old, 2), 'need': need,
              'ok_205': 205 / s_root >= need, 'ok_345': 345 / s_root >= need, 'yield_ok_205': 205 / s_root >= 1.2}
R['rod_chain'] = rod
R['rod_chain_note'] = {'d3_mm': round(d3, 3), 'Z_m8_mm3': round(Z_m8, 2), 'arm_rod_root_mm': ARM_ROD_ROOT, 'arm_ext_root_mm': ARM_EXT_ROOT,
                       'note': '로드 재질: 임시 형상은 S45C(345)로 지정돼 있으나 CQS φ20 실물 로드 재질은 카탈로그에서 확인 못 함(D-188) -> 스테인리스(205)면 오조작 SF가 2에 못 미친다. '
                               '옆힘은 장공 기울기 몫 + 마찰 μ 0.15(같은 쪽으로 보수) + 로드 묶음 자중 x3 g 절반. 설계안은 기울기 몫만(8.7 N) 셈'}
# 연장봉 몸: 암나사 쪽 Ø14 - M8(바깥 지름 8) 고리 단면, 스패너 면 대변 12
Z_ext_f = math.pi * (14.0 ** 4 - 8.0 ** 4) / (32 * 14.0)
s_ext_f = S['mis_push_jam_lift'] * (131.894 - 55.894) / Z_ext_f + F_push / (math.pi / 4 * (196 - 64))
R['ext_female_section'] = {'Z_mm3': round(Z_ext_f, 1), 'sigma_mis_MPa': round(s_ext_f, 1), 'SF_mis': round(205 / s_ext_f, 1), 'note': '암나사 끝 Y 55.9, 팔 76. 과사양 아님(Ø14는 M8 암나사·스패너 면이 정함)'}
# 부시 옆 모멘트(카탈로그 허용 옆하중 미확인 — RX-13-K1)
R['bush_moment_Nm'] = {'op_lift_hold(마찰 포함)': round(S['op_lift_hold'] * ARM_BUSH_LIFT / 1000, 2), 'op_lift_hold(설계안 8.7 N)': round(8.7 * ARM_BUSH_LIFT / 1000, 2),
                       'op_press_end_0.2': round(S['op_press_end_0.2'] * ARM_BUSH_END / 1000, 2), 'mis_pull_0.5_press_end': round(S['mis_pull_0.5_press_end'] * ARM_BUSH_END / 1000, 2),
                       'mis_push_jam_lift': round(S['mis_push_jam_lift'] * ARM_BUSH_LIFT / 1000, 2),
                       'rod_Ø10_at_bush_sigma_mis_MPa': round(S['mis_push_jam_lift'] * ARM_BUSH_LIFT / (math.pi * 1000 / 32), 1),
                       'note': 'CQSY φ20 허용 옆하중 그래프는 카탈로그부가 못 읽음 — 임시(D-188). 스무스 실린더는 옆하중에 마찰이 민감하다(누름 힘 창 f ≤ 10 N과 엮임)'}
# 나사 물림: 로드 수나사 -> 연장봉 암나사 9(= 14 - 너트 5), 연장봉 수나사 -> 너클 9
R['M8_rod_into_ext(물림 9, SUS303 -> SUS304 값)'] = calc(d=8, pitch=1.25, le=9, load=round(F_push, 1), bolt='A2-70', base='SUS304', sf_min=SF_OP) if 'pitch' in calc.__code__.co_varnames else calc(d=8, le=9, load=round(F_push, 1), bolt='A2-70', base='SUS304', sf_min=SF_OP)
# 좌굴: Ø10 로드, 길이 110.5, 한쪽 자유
Pcr = math.pi ** 2 * 206000.0 * (math.pi * 10.0 ** 4 / 64) / (4 * ARM_BUSH_LIFT ** 2)
R['buckling'] = {'Pcr_N': round(Pcr), 'SF': round(Pcr / F_push, 1)}

# ---------- 3. P_M02_BASE (SUS304 t8) ----------
# 3-1 스토퍼 탭 둘레 띠(표 모델 RX-08 그대로): 양끝 고정 띠 35, 볼트 당김 합을 가운데 점하중, 폭 = 장공 +X 끝 ~ 판 끝 X -140
R08 = json.load(open(ROOT + '/fea/results/mech_RX-08_handcalc.json', encoding='utf-8'))
Fst = R08['load']['F_stop_N']
Tb = {k: Fst[k] * 5.0 / 2 for k in ('op', 'mis')}
Mb = {k: 2 * Tb[k] * 35.0 / 8 for k in Tb}


def strip(w):
    Z = w * 8.0 ** 2 / 6
    return {'w_mm': round(w, 2), 'sigma_op': round(Mb['op'] / Z, 1), 'sigma_mis': round(Mb['mis'] / Z, 1), 'SF_op': round(205 / (Mb['op'] / Z), 2), 'SF_mis': round(205 / (Mb['mis'] / Z), 2)}


W_OLD, W_NEW = -140.0 + 157.0, -140.0 + 159.506 - 4.0          # 17.0 -> 15.506 (반달 R4, 중심 X -159.506, Y 70·79 — 탭 (-146, 69·79) 바로 옆)
R['base_tap_strip'] = {'표 모델(폭 전부) v2.12.1 장공 벽 X -157': strip(W_OLD), '표 모델(폭 전부) v2.20.4 반달 자리 X -155.506': strip(W_NEW),
                       'what-if 탭 Ø5 뺀 순 단면 v2.12.1': strip(W_OLD - 5.0), 'what-if 탭 Ø5 뺀 순 단면 v2.20.4': strip(W_NEW - 5.0),
                       'ligament_notch_to_tap_mm': round((-146.0 - 2.5) - (-159.506 + 4.0), 2), 'ligament_old_mm': 8.5,
                       'note': '표 모델 하중은 볼트 당김 합(F x 5) 전부를 띠 가운데 점하중으로 본 보수값(실제 순 하중은 F). 판정은 표 모델(폭 전부)로, 순 단면 값은 기록'}
s = R['base_tap_strip']['표 모델(폭 전부) v2.20.4 반달 자리 X -155.506']
R['base_tap_strip']['ok'] = s['SF_op'] >= SF_OP and s['SF_mis'] >= SF_MIS
# 실제 하중 길 대조(가정 검토): 순 하중 F를 가운데 + 볼트(X -146)·받침(X -140) 우력 F x 30을 띠 비틀림으로 양끝에 반씩
wn = W_NEW - 5.0
Zb, Wt = wn * 64 / 6, 0.24 * wn * 64                            # b/t 1.3 -> β 0.24(직사각 비틀림)
alt = {}
for k in ('op', 'mis'):
    sg, tau = Fst[k] * 35.0 / 8 / Zb, Fst[k] * 30.0 / 2 / Wt
    alt[k] = {'sigma': round(sg, 1), 'tau': round(tau, 1), 'vm': round(math.hypot(sg, math.sqrt(3) * tau), 1), 'SF': round(205 / math.hypot(sg, math.sqrt(3) * tau), 2)}
R['base_tap_strip']['대조: 순 하중 F + 우력 비틀림(순 단면 %.2f x 8)' % wn] = alt
# 3-2 새 통과 구멍 Ø5.5 x4 둘레 · 앞 외팔(발 앞끝 Y 45 단면, 폭 190)
M_base = F_push * ARM_Z + W_all * (45.0 + 20.0)
Z_base = 190.0 * 64 / 6
R['base_front_cantilever'] = {'M_add_Nmm': round(M_base), 'sigma_add_MPa': round(M_base / Z_base, 2),
                              'note': '브래킷이 더하는 몫만(우력 157 x 19 + 자중 x3 g x 팔 65). Y -31.1·-15.1 줄 순 폭 190 - 2 x 5.5 = 179(-5.8 %). 구멍 ~ 판 앞끝 Y -60 살 26.2, 구멍 사이 16 - 5.5 = 10.5'}
R['base_removed'] = {'mass_kg_before_after': [3.020, 2.286], 'note': '보 밑 연장(Y 140~266)과 옛 실린더 닫힌 고리 하중(RX-06 plate_ext 항목)이 없어짐 — 그 항목은 판정 대상에서 뺀다'}

# ---------- 4. 묶음 무게중심 이동 -> 레일 블록 · 캐리지 뿌리 · 발 볼트(RX-06R 값 다시 판정) ----------
R06 = json.load(open(ROOT + '/fea/results/mech_RX-06R_handcalc.json', encoding='utf-8'))
m_old, y_old, Y_REF = 12.161, 33.6, 112.0                       # RX-06R 묶음 · 레일 중심(역산: Mx 28.6 N·m)
rem = [(3.020 - 2.286, 203.0), (0.155, 242.2), (0.147, 200.2), (0.0296, 181.9), (0.0805, 139.9), (0.011, 131.9), (6 * 0.00374, 235.0)]
add = [(m['brkt'], -36.3), (m['cyl'], -8.35), (m['rod'], 40.9), (m['ext'], 83.0), (m['nut'], 103.4), (0.0770, 123.9), (0.011, 131.9), (m['cb6x4'], -40.1), (m['cb5x4'], -23.1)]
m_new = m_old - sum(a for a, _ in rem) + sum(a for a, _ in add)
y_new = (m_old * y_old - sum(a * b for a, b in rem) + sum(a * b for a, b in add)) / m_new
ratio = m_new * (Y_REF - y_new) / (m_old * (Y_REF - y_old))
rb = R06['rail_blocks']['날 힘 없음(잠금 풂)']
blocks = {}
for k, v in rb.items():
    need = v['need']
    P = v['P_max_N'] * max(1.0, ratio)
    blocks[k] = {'P_max_old_N': v['P_max_N'], 'P_max_new_N': round(P, 1), 'SF_C0_2kN(보수 임시)': round(2000 / P, 2), 'need': need, 'ok': 2000 / P >= need}
car = {k: {'SF_old': v['SF'], 'SF_new': round(v['SF'] / max(1.0, ratio), 1), 'need': v['need']} for k, v in R06['carriage'].items() if isinstance(v, dict) and 'Mx_root_Nm' in v}
fb = R06['foot_bolts_M5']
R['cg_shift'] = {'m_bundle_kg': [m_old, round(m_new, 3)], 'y_cg_mm': [y_old, round(y_new, 1)], 'Mx_ratio': round(ratio, 3),
                 'rail_blocks': blocks, 'carriage_root': car,
                 'foot_bolt_M5': {'load_old_N': fb['inputs']['load_N'], 'load_new_N': round(fb['inputs']['load_N'] * ratio, 1),
                                  'SF_암나사 전단_old_new': [fb['sf_operating']['암나사 전단'], round(fb['sf_operating']['암나사 전단'] / ratio, 2)], 'need': SF_OP},
                 'note': '보수: 블록 최대 힘·뿌리 모멘트·발 볼트 힘 전체에 자중 모멘트 비를 곱함(바퀴 힘 몫까지). 바퀴 누름 N은 당김 넓이로 줄어(0.5 MPa 107 N < 134.9 N) 옛 값이 보수'}
# 캐리지 발 장공 반달 자리: 장공을 지나는 Y 단면 폭 115 - 18.5 -> 115 - 20.0
R['carriage_slot_notch'] = {'net_width_mm': [115 - 18.5, 115 - (175.5 - 155.506)], 'change_%': round((1 - (115 - 19.994) / (115 - 18.5)) * 100, 1),
                            'note': '뿌리(웹 Y 95~107)는 장공(Y 66~84) 밖이라 뿌리 단면 115 x 12 그대로. 장공 +X 벽 ~ 발 볼트 (-150, 50·85) 구멍 Ø5.5 사이 살 X로 2.76, Y로 떨어져 있음(볼트 Y 50·85, 반달 Y 70·79)'}

# ---------- 5. 힘 계산 대조(완료 판정 '누름 창·자국 SF·회전 SF·행정 여유') ----------
chk = {}
for f in ('spring_kept_f6.28', 'spring_kept_f9.42'):
    d = SW[f]
    e = d['eval']
    chk[f] = {'p_set': d['p_set'], 'press_SF(0.2/p)': round(0.2 / d['p_set'], 3), 'press_SF_ok(>=1.5)': 0.2 / d['p_set'] >= 1.5,
              'rot_SF': [e[t]['rot_SF'] for t in ('6', '10', '16')], 'mark_SF_nom(51.6/N)': [round(51.6 / e[t]['N_nom'], 3) for t in ('6', '10', '16')],
              'N_nom_check(N_free + k p)': [round(e[t]['N_free'] + e[t]['N_per_MPa_pull'] * d['p_set'], 2) for t in ('6', '10', '16')],
              'N_nom_design': [e[t]['N_nom'] for t in ('6', '10', '16')],
              'min_ok': min([e[t]['rot_SF'] for t in e] + [e[t]['mark_SF_nom'] for t in e]) >= 1.0}
chk['lift_SF(0.5 MPa 밂 - f 6.28)/핀 힘'] = {k: round((F_push - 6.28) / v, 2) for k, v in hold.items()}
chk['stroke'] = {'used_mm': 24.878, 'of': 25.0, 'margin_lift_end_mm': 0.006, 'margin_press_end_mm': 0.116, 'note': '모델 실측(mech_RX-13_model.md 4절). 들림 끝은 스트로크 끝이 정하는 설계(여유 0이 의도), 누름 끝 여유 0.116은 M02R 0.1과 같음. 로드 나사 ±3 조정 자리'}
R['force_recheck'] = chk

# ---------- 5-2. 옆힘이 만드는 실린더 안 마찰(누름 창 f <= 10 N 민감도, 가정 검토 — 판정 아님) ----------
p_set = SW['spring_kept_f6.28']['p_set']
F_sew = p_set * A_pull                                          # 봉제 때 당김 30.2 N
ARM_BUSH_SEW = 112.99 - 21.4
fr = {}
for name, Fs in (('설계안 방식(기울기 몫만)', F_sew * math.tan(math.radians(TILT_SEW))), ('마찰 μ 0.15 + 자중 x1 g 절반', F_sew * (math.tan(math.radians(TILT_SEW)) + MU) / (1 - MU * math.tan(math.radians(TILT_SEW))) + 0.5 * m_rodgrp * g)):
    for span in (20.0, 30.0):                                   # 피스톤 ~ 부시 받침 간격(실물 미확인, 임시)
        Mb_ = Fs * ARM_BUSH_SEW
        Rb = Mb_ / span
        fr['%s, 받침 간격 %.0f' % (name, span)] = {'side_N': round(Fs, 1), 'M_Nm': round(Mb_ / 1000, 2), 'f_add_N(μ 0.1, 받침 2곳)': round(0.1 * (2 * Rb + Fs), 1),
                                              'f_total_N': round(6.28 + 0.1 * (2 * Rb + Fs), 1), 'window_ok(f <= 10)': 6.28 + 0.1 * (2 * Rb + Fs) <= 10.0}
fr['M02R(팔 62.1, 2.5 N), 받침 간격 20'] = {'f_add_N': round(0.1 * (2 * 2.5 * 62.1 / 20 + 2.5), 1)}
R['side_friction_whatif'] = fr

# ---------- 요약 ----------
summ = []


def add_s(item, sf, need, kind='', note=''):
    summ.append({'item': item, 'SF': sf, 'need': need, 'ok': sf >= need, 'kind_if_ng': kind if sf < need else '', 'note': note})


add_s('브래킷 귀 순 단면(0.5 MPa 밂)', R['brkt_ear_net']['SF_op'], SF_OP)
add_s('브래킷 앞벽 귀 옆 띠', R['brkt_wall_local']['SF_op'], SF_OP)
add_s('브래킷 앞벽 귀 사이 보', R['brkt_wall_span']['SF_op'], SF_OP)
add_s('브래킷 미끄럼(M5 x4 마찰)', R['brkt_slip']['SF'], SF_OP)
add_s('로드 수나사 뿌리 운전 들림 유지(205)', rod['op_lift_hold']['SF_rod_root(SUS304 205 보수)'], SF_OP, '디테일', '기준 ±10 % 안')
add_s('로드 수나사 뿌리 오조작 0.5 MPa 당김 누름 끝(205)', rod['mis_pull_0.5_press_end']['SF_rod_root(SUS304 205 보수)'], SF_MIS, '디테일', 'S45C 345면 %.2f' % rod['mis_pull_0.5_press_end']['SF_rod_root(S45C 345, 모델 재질)'])
add_s('로드 수나사 뿌리 오조작 들림 도중 막힘 0.5 MPa 밂(205)', rod['mis_push_jam_lift']['SF_rod_root(SUS304 205 보수)'], SF_MIS, '디테일', 'S45C 345면 %.2f' % rod['mis_push_jam_lift']['SF_rod_root(S45C 345, 모델 재질)'])
add_s('연장봉 수나사 뿌리 오조작(SUS303)', rod['mis_push_jam_lift']['SF_ext_male_root(SUS303 205)'], SF_MIS)
add_s('윗판 스토퍼 탭 띠 운전(표 모델)', s['SF_op'], SF_OP)
add_s('윗판 스토퍼 탭 띠 오조작(표 모델)', s['SF_mis'], SF_MIS)
add_s('윗판 스토퍼 탭 띠 운전(what-if 순 단면)', R['base_tap_strip']['what-if 탭 Ø5 뺀 순 단면 v2.20.4']['SF_op'], SF_OP, '디테일', '하중 5배 보수, 대조 모델 SF %.2f' % alt['op']['SF'])
add_s('윗판 스토퍼 탭 띠 오조작(what-if 순 단면)', R['base_tap_strip']['what-if 탭 Ø5 뺀 순 단면 v2.20.4']['SF_mis'], SF_MIS, '디테일', '하중 5배 보수, 대조 모델 SF %.2f' % alt['mis']['SF'])
for k, v in blocks.items():
    add_s('레일 블록 ' + k, v['SF_C0_2kN(보수 임시)'], v['need'])
for k, v in car.items():
    add_s('캐리지 뿌리 ' + k, v['SF_new'], v['need'])
add_s('발 볼트 M5 암나사 전단', R['cg_shift']['foot_bolt_M5']['SF_암나사 전단_old_new'][1], SF_OP)
R['summary'] = summ
R['min_SF'] = min(x['SF'] for x in summ)
R['motion_problem(SF < 1.2)'] = [x['item'] for x in summ if x['SF'] < 1.2]

json.dump(R, open(ROOT + '/fea/results/mech_RX-13_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('load', R['load']['side_N'])
for x in summ:
    print('%-52s SF %6.2f need %.1f %s %s' % (x['item'], x['SF'], x['need'], 'ok' if x['ok'] else 'NG(' + x['kind_if_ng'] + ')', x['note']))
print('tilt', R['brkt_tilt']['pin_dz_mm(팔 170)'], 'bush', R['bush_moment_Nm'])
print('cg', R['cg_shift']['m_bundle_kg'], R['cg_shift']['y_cg_mm'], R['cg_shift']['Mx_ratio'])
print('strip', json.dumps(R['base_tap_strip'], ensure_ascii=False)[:900])
print('bolts', {k: (v['sf_operating'], v['ok']) for k, v in R.items() if isinstance(v, dict) and 'sf_operating' in v})
print('force', json.dumps(chk, ensure_ascii=False)[:900])
print('fric', json.dumps(fr, ensure_ascii=False))
print('motion problems', R['motion_problem(SF < 1.2)'])
