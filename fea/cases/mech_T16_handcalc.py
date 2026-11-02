# T16 해석부 손계산(E-18, 해석 못 함 — 환경 없음 D-16). v0.9.1 새 하중 부품 6종 + 새 체결.
# 치수: mech_T16_model.md 2절(저장본 실측 bbox) · mech_T16_select.md 5절(판 두께·굽힘·구멍 자리).
# STEP T16_made_v091.step 은 합쳐진 한 PRODUCT라 부품별 bbox를 STEP에서 나누지 않고 전체 외곽만 확인한다.
import json, math, re, sys, importlib.util, os

ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py'
spec = importlib.util.spec_from_file_location('handcalc', ENG); hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
STEP = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_T16/stepout/T16_made_v091.step'

g = 9.81
E_AL, RP_AL = 70000.0, 175.0      # A5052 판금 H32 가정 보수(models.json 관례)
E_PC, RP_PC = 3000.0, 30.0        # PET-CF FDM 층간 보수값(models.json 관례)
SF_OP, SF_AB, SF_PERM = 3.0, 2.0, 1.2   # M-09 기본값: 운전 3, 오조작(비상) 2, 1.2 미만 = 영구 변형
A_OP, A_EM = 2.0, 9.8             # 가감속 m/s²: 운전 2(T18-Q3, 280 mm/s·2 m/s²), 비상 감속 9.8(T18-Q3 '≥ 4 m/s²(9.8)')
MU = 0.3                          # 캐리어–미끄럼판 마찰(선정 4-3 임시값과 같음)
# 캐리어 질량(임시, 카탈로그 미수령 D-63 제안): HSP0320 0.25 kg/m, HSP0350 0.35 kg/m, 안 케이블·관
KG_Y = 0.25 + 0.21                # Y: 캐리어 + DGM 2·다심·공급관
KG_X = 0.35 + 0.36                # X: 캐리어 + Y 캐리어 내용물 + Y 서보 동력·엔코더
LY, LX = 0.62, 0.86               # 캐리어 길이 m(선정 4-1)
R = {'_inputs': {'A5052_Rp': RP_AL, 'PETCF_Rp': RP_PC, 'a_op': A_OP, 'a_em': A_EM, 'mu': MU,
                 'kg_per_m_Y': KG_Y, 'kg_per_m_X': KG_X, 'L_Y_m': LY, 'L_X_m': LX, 'SF': [SF_OP, SF_AB, SF_PERM]}}

# 0) STEP 읽기 확인
s = open(STEP, encoding='latin1').read()
pts = [tuple(map(float, m.groups())) for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([-\d.Ee+]+),([-\d.Ee+]+),([-\d.Ee+]+)\)", s)]
R['step'] = {'points': len(pts), 'bbox': [[round(min(c), 1), round(max(c), 1)] for c in zip(*pts)] if pts else None,
             'breps': len(re.findall(r'MANIFOLD_SOLID_BREP', s)), 'faces': len(re.findall(r'ADVANCED_FACE', s))}

def sec_rect(b, t): return b * t ** 2 / 6.0, b * t ** 3 / 12.0

# 1) XMEND 세움 팔 t3 × 폭 46, 뿌리(굽힘 안쪽 Z −481) → 아래 볼트 Z −588: 외팔 107. 굽힘 R3 Kt 1.5(보수)
mX_move = 0.6 * KG_X * LX             # 이동 줄 + 반 고리(전체의 0.6)
F_op = mX_move * (A_OP + MU * g)
F_em = mX_move * (A_EM + MU * g)
Lx, bx, tx, Kt = 107.0, 46.0, 3.0, 1.5
Zx, Ix = sec_rect(bx, tx)
def xm(F):
    sig = Kt * F * Lx / Zx
    return {'F_N': round(F, 2), 'sigma_MPa': round(sig, 2), 'SF': round(RP_AL / sig, 1),
            'deflect_mm': round(F * Lx ** 3 / (3 * E_AL * Ix), 3)}
R['XMEND_arm'] = {'L_mm': Lx, 'b': bx, 't': tx, 'Kt': Kt, 'Z_mm3': Zx, 'op': xm(F_op), 'em': xm(F_em), 'select_6p4N': xm(6.4),
                  'beam_tool': hc.beam(tx, bx, Lx, load=F_em, e=E_AL, sy=RP_AL, sf_min=SF_AB),
                  'capacity_F_at_SF2_N': round(RP_AL / SF_AB * Zx / (Kt * Lx), 1),
                  'capacity_F_at_SF1p2_N': round(RP_AL / SF_PERM * Zx / (Kt * Lx), 1)}
# 창(Y −276~−248, Z −578~−558) 위 끝 단면 폭 18, 아래 볼트까지 30
Zw, _ = sec_rect(46 - 28, tx)
R['XMEND_window'] = {'b': 18, 'L_mm': 30, 'sigma_em_MPa': round(Kt * F_em * 30 / Zw, 2), 'SF_em': round(RP_AL / (Kt * F_em * 30 / Zw), 1)}
# 날개 지렛대: 모멘트 F·110 / 지렛대 18(볼트 X 150 ↔ 날개 끝 X 168) / 볼트 2
Tb = F_em * 110 / 18 / 2
R['XMEND_flange_bolt'] = {'T_per_bolt_em_N': round(Tb, 1),
                          'CB5_12_HNTT8_5': hc.calc(5, 8.5, Tb, torque=3.0, bolt='12.9', base='SS400', sf_min=SF_AB)}
# 세움 Ø4.5 구멍 CB4-12 + LBNR4: 전단 F/2, 판 t3 지압
R['XMEND_cb4'] = {'shear_per_bolt_N': round(F_em / 2, 2), 'bearing_MPa': round(F_em / 2 / (4 * tx), 3)}

# 2) YMEND A5052 t6 평판, 폭 41(X), 볼트 줄 L84 → 캐리어 볼트 L105: 외팔 21. 자중 ×3 g + 비상 끌림 × 높이 10
mY_upper = 0.6 * KG_Y * LY
Fv = 0.5 * KG_Y * 0.3765 * 3 * g        # 윗줄(대기 376.5)의 반을 이동단이 받음, ×3 g
Fh = mY_upper * A_EM                   # 자기지지라 마찰 없음
Zy, Iy = sec_rect(41.0, 6.0)
M = Fv * 21 + Fh * 10
R['YMEND'] = {'Fv_3g_N': round(Fv, 2), 'Fh_em_N': round(Fh, 2), 'M_Nmm': round(M, 1), 'sigma_MPa': round(M / Zy, 3), 'SF': round(RP_AL / (M / Zy), 0),
              'M4_tap_le6': hc.calc(4, 6.0, (Fv + Fh * 10 / 19) / 2 + 0.01, torque=1.5, bolt='12.9', base='A5052', sf_min=SF_AB),
              'CB5_16_le10': hc.calc(5, 10.0, M / 12 / 2 + Fv / 2 + 0.01, torque=3.0, bolt='12.9', base='A5052', sf_min=SF_AB)}

# 3) YCLIP PET-CF: 볼트 X −112 → 바깥 끝 X −176: 외팔 64. 벽 2개(L52~58 폭 6, L88~95 폭 7) × 높이 9
cab = 0.21 * 0.15 * 3 * g              # 클립 안·밖 케이블 150 mm, ×3 g
Zc = (6 + 7) * 9 ** 2 / 6.0; Ic = (6 + 7) * 9 ** 3 / 12.0
sigc = cab * 64 / Zc
q = cab / (58 * 30)                    # 바닥 t1.5, 벽 사이 30 양끝 고정 띠
sig_floor = (q * 30 ** 2 / 12) * 6 / 1.5 ** 2
R['YCLIP'] = {'F_3g_N': round(cab, 3), 'L_mm': 64, 'sigma_MPa': round(sigc, 3), 'SF': round(RP_PC / sigc, 0),
              'deflect_mm': round(cab * 64 ** 3 / (3 * E_PC * Ic), 4), 'floor_sigma_MPa': round(sig_floor, 4),
              'capacity_pull_at_SF2_N': round(RP_PC / SF_AB * Zc / 64, 1)}

# 4) TEEHOLD PET-CF 받침 t4 × 길이 85: 분기 4개, 관 당김 5 N/개(T17 안전쪽 가정과 같음) + 자중 ×3 g
Ft = 4 * 5.0
Zt, _ = sec_rect(85.0, 4.0)
sig_t = (Ft / 2) * 12 / Zt            # 한쪽 2개가 볼트 줄(X 0)에서 12 떨어져 아래로 당김
Tb_t = Ft * 15 / 65 / 1 + Ft / 2      # 수평 당김 20 N × 높이 15 / 볼트 간격 65 + 아래로 당김 몫
R['TEEHOLD'] = {'F_pull_total_N': Ft, 'sigma_MPa': round(sig_t, 3), 'SF': round(RP_PC / sig_t, 0),
                'CB5_12_le8': hc.calc(5, 8.0, Tb_t, torque=1.5, bolt='12.9', base='A5052', sf_min=SF_AB),
                'seat_PETCF_note': 'CB5 머리 Ø8.5 좌면 PET-CF p_G 60 — 1.5 N·m 이하(조임 좌면 SF 참조)',
                'tee_retention': '분기를 홈에 끼우기만 함 — 잡는 힘 근거 없음(디테일)'}

# 5) YTRAY t2: 바닥 외팔 X −172 → 캐리어 중심 −195.5 = 23.5(아랫줄 최대 456 + 반 고리, ×3 g)
Wl = KG_Y * (0.456 + 0.08) * 3 * g
qy = Wl / 456
Mfl = qy * 23.5
R['YTRAY'] = {'W_3g_N': round(Wl, 2), 'floor_sigma_MPa': round(Mfl * 6 / 2 ** 2, 3), 'SF': round(RP_AL / (Mfl * 6 / 4), 0),
              'bolt_T_N': round(qy * 210 * 45 / 20 / 1 + Wl / 3, 2),
              'fixed_end_Fy_em_N': round(mY_upper * A_EM, 2), 'fixed_end_M_Nmm': round(mY_upper * A_EM * 15, 1)}

# 6) XGLIDE t2 윗판 212 + 날개 35 ×2, 맑은 지간 1,323(1140 안쪽 면) 단순 지지. 자중 ×3 g 등분포 + 캐리어 전체 ×3 g 가운데 집중
A1, y1 = 212 * 2, 1.0; A2, y2 = 2 * 35 * 2, 2 + 17.5
yb = (A1 * y1 + A2 * y2) / (A1 + A2)
I = 212 * 8 / 12 + A1 * (yb - y1) ** 2 + 2 * (2 * 35 ** 3 / 12) + A2 * (y2 - yb) ** 2
c = 37 - yb
Lg = 1323.0
w_self = 798536e-9 * 2680 * 3 * g / Lg   # N/mm
P = KG_X * LX * 3 * g
Mg = w_self * Lg ** 2 / 8 + P * Lg / 4
d1 = (5 * (w_self / 3) * Lg ** 4 / (384 * E_AL * I)) + (P / 3) * Lg ** 3 / (48 * E_AL * I)
R['XGLIDE'] = {'I_mm4': round(I, 0), 'c_mm': round(c, 2), 'M_Nmm': round(Mg, 0), 'sigma_MPa': round(Mg * c / I, 2), 'SF': round(RP_AL / (Mg * c / I), 0),
               'deflect_1g_mm': round(d1, 3), 'deflect_3g_mm': round(3 * d1, 3),
               'hole_phi30_note': '케이블 내림 구멍 Ø30 (100, −112): 가운데 근처 윗판 폭 212 → 182, 날개는 그대로라 I 감소 < 5 %'}

# 7) 캐리어 끝 쇠 자리(X 이동단) — 걸림(오조작) 때 XMEND가 견디는 힘
R['jam_capacity'] = {'XMEND_F_SF2_N': R['XMEND_arm']['capacity_F_at_SF2_N'], 'XMEND_F_SF1p2_N': R['XMEND_arm']['capacity_F_at_SF1p2_N'],
                     'servo_peak_thrust_N_est': round(2 * math.pi * 7.16 * 0.9 / 0.020, 0),
                     'note': 'MHMF082(750 W) 최대 토크 7.16 N·m(임시, D-62 쪽 카탈로그) · 리드 20 · 효율 0.9 가정. 걸림은 서보 토크 제한·추종 오차 경보로 막는다(제어 U-09)'}

out = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_T16_handcalc.json'
json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
summ = {k: {kk: vv for kk, vv in v.items() if kk in ('SF', 'sigma_MPa', 'op', 'em', 'deflect_3g_mm', 'capacity_F_at_SF2_N', 'SF_em', 'T_per_bolt_em_N')} for k, v in R.items() if isinstance(v, dict) and not k.startswith('_')}
print(json.dumps(summ, ensure_ascii=False)[:3000])
print('bolts', {k: R[k][b]['ok'] for k, b in [('XMEND_flange_bolt', 'CB5_12_HNTT8_5'), ('YMEND', 'M4_tap_le6'), ('YMEND', 'CB5_16_le10'), ('TEEHOLD', 'CB5_12_le8')]})
print('worst', {k: (R[k][b]['worst'], R[k][b]['sf_tightening']) for k, b in [('XMEND_flange_bolt', 'CB5_12_HNTT8_5'), ('YMEND', 'M4_tap_le6'), ('TEEHOLD', 'CB5_12_le8')]})
print('step', R['step'])
