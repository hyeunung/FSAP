# -*- coding: utf-8 -*-
"""N03 해석부 손계산 — U4 X·Y 따라가기 받침 새 하중 부품 8개 (v1.0.8). FEA 환경 없음(D-16).
형상: mech_N03_model.md 2절 bbox(= tools/out/mech_N03/stepout/*.step, changed_parts.json). 월드 mm, J 0.
하중(임시값, 출처):
  이동 질량: m_x 167 kg·m_y 35 kg(선정 가정, CAD U4_X 57.3·U4_Y 11.6 kg ≤ 가정 → 보수), 큰 매트 9 kg(N02와 같음)
  벨트 유효 장력 F_eff: 운전 = 모서리 위치 모드 X 282.7 N·Y 75.3 N(hand_n03.json corner, a 1.53 m/s²)
                         오조작 = 서보 최대 토크로 스토퍼에 멈춤 X 8.36 N·m / r 22.28(HTPA28 PD 44.56) = 375 N, Y 4.46 / 19.90 = 224 N
  벨트 초장력 T0(가닥당, N03-D3 미확인 임시): X 25폭 150 N(N02 S5M 15폭 값 그대로 = 보수), Y 15폭 100 N
  풀리 축 반경 하중 = 2·T0 + F_eff (느슨한 쪽이 안 풀린다고 본 보수값)
  따라가기: X 61.4·Y 29.9 N(선정 손계산) — 편구동 요(yaw) 반력으로 블록 굴림 마찰 더 봄(μ 0.005, 보수)
  자중 x3 g(지시), 오조작은 1 g + 위 힘
판정: M-09 운전 SF 3·오조작 SF 2(요구서 6-1 기본값). 6-2 변위 미정(D-08) → 처짐은 동작 틈(최소 5.0 mm, mech_N03_model.md 5절)과 비교.
재질: A5052-H34 Rp0.2 175(JIS 하한, N02와 같음), SPCC 205(N02와 같음), S45C 345(아이들러 축 제안), CB 12.9.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

G = 9.81
RP = {'A5052': 175.0, 'SPCC': 205.0, 'S45C': 345.0}
EM = {'A5052': 70000.0, 'SPCC': 205000.0}
SFMIN = {'run': 3.0, 'mis': 2.0}
GF = {'run': 3.0, 'mis': 1.0}
m = {'beam': 44.033, 'xmot': 5.705, 'ymot': 2.749, 'xbkt': 0.542, 'ybkt': 0.203, 'xi': 0.359, 'yi': 0.277,
     'xclamp': 0.288, 'xplate': 0.046, 'yclamp': 0.050, 'pul_x': 0.109, 'pul_y': 0.064}
M_X, M_Y, M_MAT = 167.0, 35.0, 9.0
FEFF = {'X': {'run': 282.7, 'mis': 8.36 / 0.02228}, 'Y': {'run': 75.3, 'mis': 4.46 / 0.01990}}
T0 = {'X': 150.0, 'Y': 100.0}
FOLLOW = {'X': 61.4, 'Y': 29.9, 'limit': 100.0}
out = {'loads': {'F_eff_N': {k: {c: round(v, 1) for c, v in d.items()} for k, d in FEFF.items()}, 'T0_N': T0,
                 'radial_N': {k: {c: round(2 * T0[k] + FEFF[k][c], 1) for c in ('run', 'mis')} for k in T0}}}


def res(name, s, mat, case, extra=None, tau=0.0):
    vm = math.sqrt(s ** 2 + 3 * tau ** 2)
    sf = RP[mat] / vm if vm else float('inf')
    r = {'stress_vm_MPa': round(vm, 2), 'sf': round(sf, 2), 'sf_min': SFMIN[case], 'ok': sf >= SFMIN[case],
         'near_10pct': SFMIN[case] <= sf < 1.1 * SFMIN[case], 'oversize_3x': sf >= 3 * SFMIN[case], 'motion_break': sf < 1.2}
    if extra:
        r.update(extra)
    out[name] = r


# ---- 1) U4_X_BEAM 단면: 윗판 290x15 + 웹 10x4 + 8x2 = 56 폭 x 49 높이, 밑 열림 (Z -352~-288)
A1, z1 = 290 * 15, 49 + 7.5
A2, z2 = 56 * 49, 24.5
zb = (A1 * z1 + A2 * z2) / (A1 + A2)
I = 290 * 15 ** 3 / 12 + A1 * (z1 - zb) ** 2 + 56 * 49 ** 3 / 12 + A2 * (z2 - zb) ** 2
Zbot, Ztop = I / zb, I / (64 - zb)
L = 1920.0      # X 레일 중심 Y ±960 사이
out['BEAM_section'] = {'I_mm4': round(I), 'z_bar_mm': round(zb, 2), 'Z_bot_mm3': round(Zbot), 'Z_top_mm3': round(Ztop), 'span_mm': L}
m_rest = M_X - m['beam'] - 4 * 0.275 - M_Y          # 보 위 나머지(에어 테이블·Y 레일·Y 모터 묶음) → 고른 하중
for c in ('run', 'mis'):
    Wu = (m['beam'] + m_rest) * GF[c] * G
    P = (M_Y + M_MAT) * GF[c] * G + (300.0 if c == 'mis' else 0.0)   # 오조작: 손 짚음 300 N 가운데(작업자 기댐)
    Mmid = Wu * L / 8 + P * L / 4
    res(f'BEAM_mid_{c}', Mmid / Zbot, 'A5052', c, {'M_Nmm': round(Mmid), 'W_udl_N': round(Wu, 1), 'P_mid_N': round(P, 1)})
Wu1, P1 = (m['beam'] + m_rest) * G, (M_Y + M_MAT) * G
d1 = 5 * Wu1 * L ** 3 / (384 * EM['A5052'] * I) + P1 * L ** 3 / (48 * EM['A5052'] * I)
out['BEAM_deflection_1g'] = {'mm': round(d1, 3), 'min_motion_gap_mm': 5.0, 'motion_ok': d1 < 5.0,
                             'note': '보 위 유닛이 같이 처짐(원판·테이블 모두 보 위) → 상대 틈 변화는 더 작음. 정밀 한도 6-2 미정(D-08) → 디테일 N03-D1'}
# 보 평면 굽힘(벨트가 −Y 끝에서 X로 끎): M ≈ F·L/2, 윗판 단면 Z = 15·290²/6
for c in ('run', 'mis'):
    Mz = FEFF['X'][c] * 2000 / 2
    res(f'BEAM_inplane_{c}', Mz / (15 * 290 ** 2 / 6), 'A5052', c, {'M_Nmm': round(Mz)})

# ---- 2) 편구동 요 반력 → X 블록 옆 힘·볼트 CB5-20_N03XB, 따라가기 저항 다시 계산
#   XB 볼트는 보 카운터보어 → SV2RL28 블록 강 탭(물림 8)이라 모재 S45C로 봄(블록 재질 보수 대용).
#   벨트 물림 Y −1120, 이동 무게 중심 Y 최대 +241(Y 대차 1150) → 팔 1361. 레일마다 블록 2개 간격 70(X −935·−865).
arm = 1120 + M_Y * 1150 / M_X
yaw = {}
for c, F in (('follow', FOLLOW['X']), ('run', FEFF['X']['run']), ('mis', FEFF['X']['mis'])):
    yaw[c] = F * arm / (2 * 70)
out['XBLOCK_yaw_lateral_N'] = {k: round(v, 1) for k, v in yaw.items()}
out['XBLOCK_yaw_lateral_N']['arm_mm'] = round(arm, 1)
out['XBLOCK_C0_SF'] = {c: round(12100 / yaw[c], 2) for c in ('run', 'mis')}
extra_roll = 4 * yaw['follow'] * 0.005
fx = FOLLOW['X'] + extra_roll
out['FOLLOW_recheck'] = {'X_N': round(fx, 1), 'Y_N': FOLLOW['Y'], 'extra_roll_yaw_N': round(extra_roll, 1),
                         'vector_N': round(math.hypot(fx, FOLLOW['Y']), 1), 'limit_D79_N': FOLLOW['limit'],
                         'ok': math.hypot(fx, FOLLOW['Y']) <= FOLLOW['limit']}
for c in ('run', 'mis'):
    fs = yaw[c] / 2                       # 블록 하나 볼트 2개
    out[f'XB_CB5-20_{c}'] = {'shear_per_bolt_N': round(fs, 1),
                             'calc': calc(5, 8, fs / 0.2, torque=6.0, bolt='12.9', base='S45C', dw=8.5, dh=5.5, sf_min=SFMIN[c])}

# ---- 3) P_N03_XMBKT SPCC t4 L (X −1370~−1270 폭 100, 세움판 Y −1140~−1136, 소켓 Ø70, 축 Z −330 = 밑판 위 50)
#   모터 5.7 kg 무게 중심 세움판에서 −Y 56, 풀리 중심 세움판에서 +Y 18. 반경 하중 X 방향.
t = 4.0
for c in ('run', 'mis'):
    W = (m['xmot'] + m['pul_x']) * GF[c] * G
    R = 2 * T0['X'] + FEFF['X'][c]
    Mx, Mz = W * 56, R * 18
    s_root = 6 * Mx / (100 * t ** 2) + R * 50 / (t * 100 ** 2 / 6)
    tau_root = 3 * Mz / (100 * t ** 2)
    res(f'XMBKT_root_{c}', s_root, 'SPCC', c, {'Mx_Nmm': round(Mx), 'Mz_Nmm': round(Mz)}, tau=tau_root)
    # 소켓 옆 띠(폭 15 x 2, 위 띠 10): 플랜지 볼트 PCD 90(±31.8)에서 오는 면 밖 힘. 고르게 나눔 / 한쪽이 다 받음(보수)
    fb_mx, fb_mz = Mx / (2 * 63.6), Mz / (2 * 63.6)
    M_even = 2 * fb_mx * 31.8 / 2 + fb_mz * 2 * 31.8 / 2
    M_one = (fb_mx + fb_mz) * 31.8 * 2 / 2 + 0.0
    zl = 15 * t ** 2 / 6
    res(f'XMBKT_ligament_even_{c}', M_even / (2 * zl), 'SPCC', c, {'ligament_mm': 15})
    res(f'XMBKT_ligament_one_{c}', M_one / zl, 'SPCC', c, {'ligament_mm': 15, 'note': '한쪽 띠가 위 볼트 하중을 다 받음(위 띠 10 무시)'})

# ---- 4) P_N03_YMBKT SPCC t4 L (모터판 X −884~−880, Y 1004~1075, Z −325~−258 높이 67, 소켓 Ø52)
for c in ('run', 'mis'):
    W = (m['ymot'] + m['pul_y']) * GF[c] * G
    R = 2 * T0['Y'] + FEFF['Y'][c]
    My, Mz = W * 48, R * 18
    s = 6 * Mz / (67 * t ** 2) + W * 36 / (t * 67 ** 2 / 6)
    tau = 3 * My / (67 * t ** 2)
    res(f'YMBKT_root_{c}', s, 'SPCC', c, {'My_Nmm': round(My), 'Mz_Nmm': round(Mz)}, tau=tau)
    # 소켓 둘레 띠 위 6.5·아래 8.5(Z), 먼 쪽 볼트 쌍(+Y)의 면 밖 힘을 두 띠가 팔 35로 굽 쪽에 넘김
    fb = Mz / 70 + My / 70
    res(f'YMBKT_ligament_{c}', (fb / 2) * 35 / (6.5 * t ** 2 / 6), 'SPCC', c, {'ligament_mm': 6.5, 'note': '모터 플랜지 강성 무시(보수)'})

# ---- 5) P_N03_XIBKT SPCC t4 ㄷ (옆판 폭 X 60, 축 Z −330 = 밑판 위 50), 반경 하중 −X, 옆판 2장 나눔
for c in ('run', 'mis'):
    R = 2 * T0['X'] + FEFF['X'][c] + (m['xi'] + m['pul_x']) * GF[c] * G * 0
    Mside = R / 2 * 50
    res(f'XIBKT_side_inplane_{c}', Mside / (t * 52 ** 2 / 6), 'SPCC', c, {'net_width_mm': 52, 'bearing_MPa': round(R / 2 / (8 * t), 1)})
    # 아이들러 축(미작도 N03-D7, 제안 Ø8 S45C) 양 옆판 사이 46 가운데 하중
    for dax in (8, 10):
        res(f'XIDLER_axle_D{dax}_{c}', R * 46 / 4 / (math.pi * dax ** 3 / 32), 'S45C', c)

# ---- 6) P_N03_YIBKT SPCC t4 ㄷ (옆판 X 4, Z −320~−265 높이 55, 축 Y −1035 → 보 끝면 Y −1000에서 35)
for c in ('run', 'mis'):
    R = 2 * T0['Y'] + FEFF['Y'][c]
    s = R / 2 / (55 * t) + (R / 2) * (292.5 - 292.5) / 1
    res(f'YIBKT_side_{c}', s, 'SPCC', c, {'note': '힘 +Y가 옆판 면 안 압축. 보 끝면 부착 귀 미작도(N03-D6)'})
    for dax in (8,):
        res(f'YIDLER_axle_D{dax}_{c}', R * 42 / 4 / (math.pi * dax ** 3 / 32), 'S45C', c)

# ---- 7) P_N03_XCLAMP SPCC t4 L: 수평판 폭 60(X), 굽 Y −1004 → 벨트 중심 Y −1120 팔 116, 세움판 Z −316~−296, CB5-16 x2 X −1035·−1005 Z −310
for c in ('run', 'mis'):
    F = FEFF['X'][c]
    Mz = F * 116
    res(f'XCLAMP_horiz_inplane_{c}', Mz / (t * 60 ** 2 / 6), 'SPCC', c, {'Mz_Nmm': round(Mz)})
    # 세움판 면 밖: Mz가 굽 선에서 Y 힘 짝(팔 40)으로 들어와 볼트 줄 Z −310까지 팔 10(굽 −300 → 볼트 머리 가장자리)
    fy = Mz / 40
    res(f'XCLAMP_vert_outplane_{c}', 6 * fy * 10 / (30 * t ** 2), 'SPCC', c, {'F_pair_N': round(fy, 1), 'eff_width_mm': 30})
    # 볼트 지레(맞닿는 끝 X −990 기준, 볼트 팔 45·15)
    f1 = Mz / (45 + 15 * 15 / 45)
    out[f'XC_CB5-16_{c}'] = {'tension_max_N': round(f1, 1), 'shear_per_bolt_N': round(F / 2, 1),
                             'calc': calc(5, 12, f1 + F / 2 / 0.2, torque=6.0, bolt='12.9', base='A5052', dw=8.5, dh=5.5, sf_min=SFMIN[c])}

# ---- 8) P_N03_XCLAMP_PLATE A5052 60x35x8.2: 치형 물림 → 벨트 힘을 L 판에 넘김(물림판 조임 볼트 미작도 N03-D4)
for c in ('run', 'mis'):
    F = FEFF['X'][c]
    res(f'XPLATE_shear_{c}', 0.0, 'A5052', c, tau=F / (35 * 8.2))

# ---- 9) P_N03_YCLAMP (CB5-12 → 대차 A5052 탭 물림 8: 조임 토크 4.5 N·m로 낮춰 봄 — 6 N·m면 암나사 0.92) A5052 26x50x18, 벨트 통로 Z −271 → 대차 밑 Z −260 팔 11, CB5-12 x2 Y 간격 30
for c in ('run', 'mis'):
    F = FEFF['Y'][c] + (m['yclamp']) * GF[c] * G
    M = F * 11
    # 카운터보어 Ø9.5 옆 띠: (26−9.5)/2 = 8.25 x2, 높이 18 → 굽힘 단면 Y 방향
    res(f'YCLAMP_body_{c}', M / (2 * 8.25 * 18 ** 2 / 6), 'A5052', c)
    ft = M / 30
    out[f'YC_CB5-12_{c}'] = {'tension_N': round(ft, 1), 'shear_per_bolt_N': round(F / 2, 1),
                             'calc': calc(5, 8, ft + F / 2 / 0.2, torque=4.5, bolt='12.9', base='A5052', dw=8.5, dh=5.5, sf_min=SFMIN[c])}

json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_N03_handcalc.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in out.items():
    if isinstance(v, dict) and 'sf' in v:
        flag = 'MOTION' if v['motion_break'] else ('LOW' if not v['ok'] else ('near' if v['near_10pct'] else ('over' if v['oversize_3x'] else '')))
        print(f"{k:34s} {v['stress_vm_MPa']:8.2f} MPa SF {v['sf']:7.2f} {flag}")
    elif isinstance(v, dict) and 'calc' in v:
        print(f"{k:34s} bolt ok={v['calc'].get('ok')} {json.dumps({kk: vv for kk, vv in v['calc'].items() if kk != 'inputs'}, ensure_ascii=False)[:200]}")
print(json.dumps({k: out[k] for k in ('BEAM_section', 'BEAM_deflection_1g', 'XBLOCK_yaw_lateral_N', 'XBLOCK_C0_SF', 'FOLLOW_recheck')}, ensure_ascii=False))
