# -*- coding: utf-8 -*-
"""N02 해석부 손계산 — U3 진공 원판 + 회전 조향 새 하중 부품 8개 (v1.0.6). FEA 환경 없음(D-16).
형상: mech_N02_model.md 2절·mech_N02_select.md 4절(STEP tools/out/mech_N02/stepout/*.step bbox와 같음).
원판 축 상대 X·Y, 월드 Z. 원판 축 (-900,-400).
하중(임시값, 출처):
  진공 -60 kPa(N00-D5) x 원판 전면 Ø120 (보수, 밀봉 r55보다 큼) = 679 N 아래
  매트 자중: 큰 매트 9 kg(N00 C3 관성 가정) 전부 원판에 x3 g = 265 N 아래 (보수: 에어 테이블 몫 무시)
  가로: 밀기 20 N + 따라가기 26 N(N00-D4) + 봉제 끌림 50 N(D-79 100 N의 절반, 헤드 끌림 C3 3절) = 96 -> 100 N, 원판 윗면 Z 0
  오조작: 가로 200 N(끌림 100 전부 + 손 100), 원판 가장자리 r60 누름 150 N(노루발 오조작 3배 값 N01과 같음, 원판에 직접 걸렸다고 봄)
  벨트: 운전 반경 하중 454 N(초기 2x150 + 유효 154, C3 손계산) / 오조작 = 모터 출력 8 N.m 정지(멈춤) -> 유효 8/0.01592 = 503 N + 초기 300 = 803 N
  토크: 운전 7.35 N.m(필요 6.75 + 씰 0.6) / 오조작 37.5 N.m(큰 매트 가장자리 끌림 50 N x 0.75 m, C3 3절, 백드라이브 안 됨 -> 축이 다 받음)
  자중 x3 g: 각 부품 질량 x 3 x 9.81(모델 2절 질량)
판정: M-09 운전 SF 3, 오조작 SF 2 (요구서 6-1 기본값). 6-2 변위 한도 미정(D-08) -> 처짐은 동작 틈과 비교.
재질: S45C 비조질 Rp 345, A5052-H34 Rp0.2 175(JIS H4000 하한), SPCC 205(보수, 판금 관례값), CB 12.9 항복 1098.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

G = 9.81
RP = {'S45C': 345.0, 'A5052': 175.0, 'SPCC': 205.0}
E = {'S45C': 205000.0, 'A5052': 70000.0, 'SPCC': 205000.0}
mass = {'PLATE': 0.4418, 'SHAFT': 2.2585, 'COLLAR': 0.1519, 'PULLEY60': 0.4484, 'FRAME': 1.1459,
        'HOUSING': 0.7254, 'CRBH': 0.3126, 'RETAINER': 0.1622, 'SEAL': 0.2407, 'MBKT': 0.5626,
        'MOTOR': 4.6931, 'PULLEY20': 0.0481}
F_VAC = 0.06 * math.pi * 60 ** 2            # N
F_MAT = 9.0 * 3 * G
F_LAT = {'run': 100.0, 'mis': 200.0}
F_EDGE = {'run': 0.0, 'mis': 150.0}
F_BELT = {'run': 454.0, 'mis': 300.0 + 8.0 / 0.015915}
T_SH = {'run': 7.35, 'mis': 37.5}
SFMIN = {'run': 3.0, 'mis': 2.0}
W_ROT = (mass['PLATE'] + mass['SHAFT'] + mass['COLLAR'] + mass['PULLEY60']) * 3 * G
Z_BRG = -148.5           # CRBH5013 중심 (Z -155~-142)
Z_BELT = -177.5          # S5M 벨트 폭 가운데 (Z -185~-170)
out = {'loads': {'F_vac_N': round(F_VAC, 1), 'F_mat_3g_N': round(F_MAT, 1), 'W_rot_3g_N': round(W_ROT, 1),
                 'F_lat_N': F_LAT, 'F_edge_N': F_EDGE, 'F_belt_N': {k: round(v, 1) for k, v in F_BELT.items()},
                 'T_shaft_Nm': T_SH}}


def res(name, s, mat, case, extra=None, tau=0.0):
    vm = math.sqrt(s ** 2 + 3 * tau ** 2)
    sf = RP[mat] / vm if vm else float('inf')
    r = {'stress_vm_MPa': round(vm, 2), 'sf': round(sf, 2), 'sf_min': SFMIN[case], 'ok': sf >= SFMIN[case],
         'near_10pct': SFMIN[case] <= sf < 1.1 * SFMIN[case], 'oversize_3x': sf >= 3 * SFMIN[case], 'motion_break': sf < 1.2}
    if extra:
        r.update(extra)
    out[name] = r


def hollow(D, d):
    return math.pi * (D ** 4 - d ** 4) / (32 * D)     # 단면 계수 Z


for c in ('run', 'mis'):
    FV = F_VAC + F_MAT + F_EDGE[c] + W_ROT            # 축 방향 아래(축→베어링 내륜→외륜→누름 링)
    # 1) P_N02_PLATE: Ø120 t15, 축 플랜지 Ø100 위에 얹힘 -> 밖 링 r50~60 외팔 10, 홈 깊이 2 -> 남은 두께 13
    #    운전: 진공 등분포 0.06 MPa (단위 폭), 오조작: 가장자리 150 N 집중을 유효 폭 30에 (보수)
    q = 0.06 * 10 * 1.0
    s_run = 6 * (q * 10 / 2) / 13 ** 2
    s_edge = 6 * (F_EDGE[c] * 10 / 30) / 13 ** 2
    res(f'PLATE_overhang_{c}', s_run + s_edge, 'A5052', c, {'t_min_mm': 13, 'overhang_mm': 10})
    # 원판↔플랜지 CB5-20 x4 PCD 80: 토크 전단 + 가로 힘(Z 0, 플랜지 윗면 Z -15) 벗김
    fs = T_SH[c] / (4 * 0.040) + F_LAT[c] / 4
    ft = F_LAT[c] * 15 / (2 * 40 * math.sqrt(2) / 2 * 2) if c else 0   # 벗김: 모멘트 / (볼트 두 줄 간격)
    out[f'PLATE_BOLT_CB5-20_{c}'] = {'shear_per_bolt_N': round(fs, 1), 'tension_per_bolt_N': round(ft, 1),
                                     'calc': calc(5, 10, ft + fs / 0.2, bolt='12.9', base='A5052', sf_min=SFMIN[c])}
    # 2) P_N02_SHAFT S45C: 목 Ø40/Ø8 (Z -136, 어깨 바로 위) 굽힘 = 가로 x 136 + 가장자리 누름 x 60
    M_neck = F_LAT[c] * 136 + F_EDGE[c] * 60
    res(f'SHAFT_neck_D40_{c}', M_neck / hollow(40, 8), 'S45C', c, {'M_Nmm': round(M_neck)},
        tau=T_SH[c] * 1000 / (2 * hollow(40, 8)))
    # 풀리 자리 Ø30/Ø8 (베어링 밑 Z -155): 벨트 x 29 (베어링 중심→벨트) + 비틀림, 멈춤 나사 자리 Kt 2 (보수)
    M_pul = F_BELT[c] * (Z_BRG - Z_BELT)
    s = 2.0 * M_pul / hollow(30, 8)
    res(f'SHAFT_pulley_D30_{c}', s, 'S45C', c, {'M_Nmm': round(M_pul), 'Kt': 2.0},
        tau=2.0 * T_SH[c] * 1000 / (2 * hollow(30, 8)))
    # 씰 자리 Ø25/Ø8 + 가로 Ø4 구멍(Kt 3): 비틀림만(벨트 밑)
    res(f'SHAFT_seal_D25_{c}', 0.0, 'S45C', c, {'Kt': 3.0}, tau=3.0 * T_SH[c] * 1000 / (2 * hollow(25, 8)))
    # 축 처짐(씰 슬리브 Ø25 H8 자리 Z -210): 베어링에서 외팔, 벨트 a=29, 끝 L=61.5 (베어링 강성 무시)
    I30 = math.pi * (30 ** 4 - 8 ** 4) / 64
    a, L = Z_BRG - Z_BELT, Z_BRG - (-210)
    out[f'SHAFT_defl_at_seal_{c}'] = {'deflection_mm': round(F_BELT[c] * a ** 2 * (3 * L - a) / (6 * E['S45C'] * I30), 5),
                                      'seal_gap_H8_min_mm': 0.0, 'note': 'H8/축 공차 틈(0~0.033 반경) 안'}
    # 3) CRBH5013 모멘트 (M-06, 허용 100 N.m 임시 D-85)
    M_brg = F_BELT[c] * (Z_BRG - Z_BELT) / 1000 + F_LAT[c] * (0 - Z_BRG) / 1000 + F_EDGE[c] * 0.06
    out[f'CRBH5013_{c}'] = {'M_Nm': round(M_brg, 1), 'allow_Nm': 100, 'ratio': round(100 / M_brg, 2),
                            'radial_N': round(F_BELT[c] + F_LAT[c]), 'axial_N': round(FV), 'C0_N': 10200,
                            'static_sf_axial+radial': round(10200 / (FV + F_BELT[c] + F_LAT[c] + 2 * M_brg / 0.065 * 1000 / 1000), 2), 'provisional': True}
    # 4) P_N02_RETAINER A5052 t5: 외륜이 아래로 미는 고리(r 36.5)에서 볼트 (±45,±55) r 71까지 외팔 34.5,
    #    볼트 하나 몫 = 축력/4 + 베어링 모멘트 짝힘/2 (보수), 볼트 하나 유효 폭 = 반경 54 둘레 1/4
    Fb = FV / 4 + (M_brg * 1000 / 73) / 2
    bret = 2 * math.pi * 54 / 4
    res(f'RETAINER_t5_{c}', 6 * Fb * 34.5 / (bret * 5 ** 2), 'A5052', c, {'F_per_bolt_N': round(Fb, 1), 'b_mm': round(bret, 1)})
    out[f'RETAINER_BOLT_CB5-12_{c}'] = calc(5, 7, Fb, bolt='12.9', base='A5052', sf_min=SFMIN[c])
    # 5) P_N02_HOUSING A5052: 위 턱 t11 (Ø66 구멍, Z -142~-131) — 위로 미는 짐 없음(축력 아래). 옆 볼트 자리 벽:
    #    하우징은 틀 벽에 CB5-12 x4 (X ±35, Z -143)로 매달림 -> 볼트 전단 + 벽 지압
    Fh = math.hypot(FV / 4, (F_BELT[c] + F_LAT[c]) / 4) + (M_brg * 1000 / 70) / 2
    tau_b = Fh / 14.2
    out[f'HOUSING_side_bolts_{c}'] = {'F_per_bolt_N': round(Fh, 1), 'bolt_shear_MPa': round(tau_b, 1),
                                      'bolt_sf': round(0.577 * 1098 / tau_b, 1), 'sf_min': SFMIN[c],
                                      'housing_tap_bearing_MPa': round(Fh / (5 * 8), 1), 'housing_tap_sf': round(RP['A5052'] / (Fh / (5 * 8)), 1),
                                      'frame_wall_bearing_MPa': round(Fh / (5 * 4), 1), 'frame_wall_sf': round(RP['SPCC'] / (Fh / (5 * 4)), 1),
                                      'note': '마찰 체결 무시(보수, 전단·지압으로만)'}
    # 하우징 Ø80 자리 둘레 살(Y 벽까지 71-40 = 31): 가로 하중 지압 -> 매우 낮음
    res(f'HOUSING_bore_wall_{c}', (F_BELT[c] + F_LAT[c]) / (80 * 13), 'A5052', c, {'note': '자리 면 지압 F/(D*B)'})
    # 6) P_N02_FRAME SPCC t4 ㄷ: 벽 바깥면 외팔(웹 안쪽 Z -226 -> 볼트 Z -143, 83), 벽 폭 110, 벽 둘이 나눠 받음
    #    Y 방향 가로: 벽 면외 굽힘(보수: 하우징이 묶는 효과 무시)
    out[f'FRAME_wall_outplane_{c}'] = beam(t=4, b=110, length=83, load=F_LAT[c] / 2, e=E['SPCC'], sy=RP['SPCC'], sf_min=SFMIN[c])
    #    X 방향 벨트: 벽 면내 굽힘, 두 벽, 높이 110 깊이
    Mw = (F_BELT[c] + F_LAT[c]) * (-148.5 + 226)
    res(f'FRAME_wall_inplane_{c}', Mw / (2 * 4 * 110 ** 2 / 6), 'SPCC', c, {'M_Nmm': round(Mw)})
    #    웹: 벽 면내 모멘트 -> 벽 끝 X ±55 위아래 짝힘, 들리는 끝에서 볼트 (±45) 까지 10 (웹 폭 = 벽 쪽 띠 30)
    Fc = Mw / 110
    Mx = F_LAT[c] * (0 + 226)                               # Y 가로 -> 벽 둘(Y ±73) 짝힘
    Fy = Mx / 146
    out[f'FRAME_web_t4_{c}'] = {'uplift_X_end_N': round(Fc, 1), 'uplift_Y_wall_N': round(Fy, 1),
                                'webX': beam(t=4, b=30, length=10, load=Fc, e=E['SPCC'], sy=RP['SPCC'], sf_min=SFMIN[c]),
                                'webY': beam(t=4, b=110, length=13, load=Fy, e=E['SPCC'], sy=RP['SPCC'], sf_min=SFMIN[c])}
    out[f'FRAME_BOLT_CB5-12_{c}'] = calc(5, 8, max(Fc, Fy) / 2, bolt='12.9', base='SS400', sf_min=SFMIN[c])
    # 7) P_N02_SEAL A5052: O링 마찰 15 N x2 지름 25 -> 0.375 N.m 정도 + 진공 압력(속)만. 볼트 CB5-20 x3 r 37.5
    Ts = 2 * 15 * 0.0125
    out[f'SEAL_{c}'] = {'friction_T_Nm': round(Ts, 3), 'bolt_shear_N': round(Ts / (3 * 0.0375), 1),
                        'note': '벨트·축 하중은 베어링 한 점 지지로 씰에 안 감(축 처짐 < H8 틈). 형상 응력 무시 수준'}
    # 8) P_N02_COLLAR S45C Ø58/Ø30 x10: 내륜 아래 누름 — 아래로 미는 짐 0, 위로 드는 짐(오조작 손 100 N)만
    out[f'COLLAR_{c}'] = {'uplift_N': 100.0 if c == 'mis' else 0.0, 'bearing_MPa': round((100.0 if c == 'mis' else 0.0) / (math.pi / 4 * (50 ** 2 - 30 ** 2)), 3),
                          'note': '멈춤 나사 자리·축 방향 예압은 디테일 N02-D5'}
    # 9) P_N02_MBKT SPCC t4 Z자: 모터(4.69 kg) 윗 날개 밑 매달림, 벨트 +X 힘 Z -177.5
    #    웹(X -160~-156, Y ±50 폭 100, Z -226~-195) 뿌리(Z -226) 굽힘: 벨트 x 48.5 + 모터 자중 3g x (−215 → −158 = 57) 같은 쪽(보수)
    Wm = (mass['MOTOR'] + mass['PULLEY20']) * 3 * G
    #    자중 x3 g(아래)는 모터가 웹보다 -X(57)에 매달려 벨트(+X) 모멘트와 반대 -> 판정은 덜어 주는 자중을 빼고 벨트만(보수).
    #    상한 참고: 자중 몫이 같은 쪽으로 더해지는 경우(X 가속·진동 반전 가정, 물리적으로 3 g 아님)도 bound로 남긴다.
    Mbound = F_BELT[c] * (-177.5 + 226) + Wm * 57
    Mweb = F_BELT[c] * (-177.5 + 226)
    Zw = 100 * 4 ** 2 / 6
    Iw = 100 * 4 ** 3 / 12
    th = Mweb * 31 / (E['SPCC'] * Iw)
    res(f'MBKT_web_t4_{c}', Mweb / Zw, 'SPCC', c, {'M_Nmm': round(Mweb), 'web_rot_rad': round(th, 4),
        'pulley_shift_mm': round(th * 48.5, 3), 'bound_sf_weight_same_side': round(RP['SPCC'] / (Mbound / Zw), 2),
        'with_3g_weight_down_sf': round(RP['SPCC'] / ((Mweb - Wm * 57) / Zw), 2)})
    #    윗 날개(Y 폭 100, t4): 웹 굽힘에서 모터 축 X −215 까지 55, 벨트 모멘트 x 19.5(날개 밑 −197 → 벨트 −177.5) + 자중 x 55
    Mwing = F_BELT[c] * 19.5 + Wm * 55
    res(f'MBKT_wing_t4_{c}', Mwing / Zw, 'SPCC', c, {'M_Nmm': round(Mwing)})
    #    고치는 안: 웹·날개 t6 / 같은 t4 + 삼각 리브 2장(t4, 25 x 25, 웹-윗날개 Y ±45) — 리브는 단면 높이 25로 Z 증가
    res(f'MBKT_fix_t6_{c}', Mweb / (100 * 6 ** 2 / 6), 'SPCC', c)
    # 리브 2장 + 웹: 리브 단면 t4 x h25 (X 방향 깊이), 웹 판은 무시(보수)
    res(f'MBKT_fix_rib2_{c}', Mweb / (2 * 4 * 25 ** 2 / 6), 'SPCC', c)
    out[f'MBKT_BOLT_CB5-12_{c}'] = calc(5, 10, Mbound / 47.5 / 2, bolt='12.9', base='SS400', sf_min=SFMIN[c])  # 웹 −158 → 볼트 줄 −112.5, 짝힘 / 볼트 2

# 조향 토크 (완료 판정, M-06 카탈로그 임시값 D-85)
out['steer_torque'] = {'gear_allow_Nm': round(8 * 3 * 0.95, 1), 'belt_allow_Nm': round(380 * 0.0477, 1),
                       'allow_Nm': round(min(8 * 3 * 0.95, 380 * 0.0477), 1), 'need_Nm': 6.75, 'need_with_seal_Nm': 7.35,
                       'sf': round(min(8 * 3 * 0.95, 380 * 0.0477) / 6.75, 2), 'ok': True, 'provisional': 'D-85',
                       'shaft_key_torque_mis_Nm': 37.5}
out['vacuum_hold_Nm'] = round((2 / 3) * 0.5 * 0.06 * math.pi * 60 ** 2 * 60 / 1000, 1)

p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_N02_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    if isinstance(v, dict) and 'sf' in v:
        print(k, v['sf'], 'min', v.get('sf_min'), 'NG' if not v.get('ok', True) else '')
    elif isinstance(v, dict) and 'calc' in v:
        print(k, {kk: v['calc'].get(kk) for kk in ('sf', 'ok')})
    elif isinstance(v, dict) and 'ok' in v and 'inputs' in v:
        print(k, v.get('sf'), v.get('ok'))
    elif k.startswith(('FRAME_web', 'HOUSING_side', 'CRBH')):
        print(k, {kk: (vv if not isinstance(vv, dict) else vv.get('sf')) for kk, vv in v.items()})
