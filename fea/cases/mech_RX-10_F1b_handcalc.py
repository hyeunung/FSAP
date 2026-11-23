# -*- coding: utf-8 -*-
"""RX-10-F1b 해석부 손계산(2026-11-23, v2.22.3 — 윗 너트 축 틈 2.3 · 로드 장공 5 x 14). FEA 못 함 — 환경 없음(D-16).
1) 옛 모델: fea/cases/mech_RX-10_F1_handcalc.py 를 같은 형상(새 STEP)에 틈만 바꿔 그대로 풂 -> fea/results/mech_RX-10_F1b_oldmodel.json
2) 새 모델(바꾼 것 3가지): (a) 옆힘 팔을 실제 닿는 너트 면(아래 너트 윗면 / 윗 너트 밑면)에서 실린더 코까지로
   (b) 굽힘 단면을 둘로 — 코 부시 자리 Ø4 민 단면, 나사 윗끝 M4 골 단면 (c) 기울기 한도에 칼라 장공 폭 걸림(7.1 - 7.0)을 더함
실행: python -X utf8 -B fea/cases/mech_RX-10_F1b_handcalc.py  ->  fea/results/mech_RX-10_F1b_handcalc.json
"""
import json, math, io, contextlib

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
src = open(ROOT + '/fea/cases/mech_RX-10_F1_handcalc.py', encoding='utf-8').read()
sig = json.load(open(ROOT + '/tools/out/signatures.json', encoding='utf-8'))['parts']
bb = lambda k: sig[k]['bbox']                                           # [x0, x1, y0, y1, z0, z1]
NUT_UP, NUT_LO = bb('U6_PRESS/CJ2B10-15Z_M06P_NUT_ROD'), bb('U6_PRESS/CJ2B10-15Z_M06P_NUT_ROD (U6_PRESS:1/NTJ-010C:2)')
ROD, CYL = bb('U6_PRESS/CJ2B10-15Z_M06P_ROD'), bb('U6_SHOE/CJ2B10-15Z_M06P')
G_NUT_SIG = round(NUT_UP[4] - 54.5, 3)
# ---------- 1. 옛 모델 그대로(틈만 실측값) ----------
old = src.replace('G_NUT, NUT_AC, NUT_AF, T_WING = 0.6,', 'G_NUT, NUT_AC, NUT_AF, T_WING = %s,' % G_NUT_SIG).replace('G2, S2 = 2.2, 7.0', 'G2, S2 = 2.3, 7.0') \
         .replace('/fea/results/mech_RX-10_F1_handcalc.json', '/fea/results/mech_RX-10_F1b_oldmodel.json')
assert old != src and 'F1b_oldmodel' in old
ns = {'__name__': 'old'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(old, 'old', 'exec'), ns)
g = lambda k: ns[k]
S, R0, rodslot, wing_xy = g('S'), g('R'), g('rodslot'), g('wing_xy')
HAND, SY, KB = g('HAND'), g('SY'), g('KB')
Y_TIP, Y_FLAT, Y_ROD, Y_CN, Y_CP, Y_FRONT, Y_STOP = (g(k) for k in ('Y_TIP', 'Y_FLAT', 'Y_ROD', 'Y_CN', 'Y_CP', 'Y_FRONT', 'Y_STOP'))
G_UP, G_DN, G_STOP, NUT_AC, NUT_AF, T_WING = (g(k) for k in ('G_UP', 'G_DN', 'G_STOP', 'NUT_AC', 'NUT_AF', 'T_WING'))
F_LIFT, F_LIFT_MAX, F_HI, My4, MyT = (g(k) for k in ('F_LIFT', 'F_LIFT_MAX', 'F_HI', 'My4', 'MyT'))
gap_need, R_SLOT, R_COL, Z_COL, Z_SHOE = g('gap_need'), g('R_SLOT'), g('R_COL'), g('Z_COL'), g('Z_SHOE')
R = {'_설명': 'RX-10-F1b 해석부 손계산(v2.22.3). 형상 = 임시 STEP 2개(REST) + 서명 bbox. 옛 모델 값은 mech_RX-10_F1b_oldmodel.json'}

# ---------- 2. 새 모델 입력 ----------
W = 0.139297 * 9.80665                                                  # 모델링 1회차 실측 139.297 g
Y_CG = -177.1
Z_WT = 54.5                                                             # 윗날개 윗면(STEP)
Z_NOSE, Z_END = CYL[4], ROD[4]                                          # 실린더 코 밑 69.3, 로드 끝 49.3
THREAD = 15.0                                                           # M4 나사 길이(SMC CJ2 Ø10 A 치수 15 — D-210 임시, 모형 나사부 15.0과 같음)
Z_THR = Z_END + THREAD
G_NUT = NUT_UP[4] - Z_WT                                                # 윗 너트 밑 56.8 - 54.5
SLOT_P = (rodslot[-1][1] + 2.5) - (Y_ROD + 2.0)                         # 로드 ↔ 장공 +Y 끝
SLOT_N = (Y_ROD - 2.0) - (rodslot[0][1] - 2.5)                          # -Y 끝
PITCH = Y_CP - Y_CN
C_SLOT = R_SLOT - R_COL                                                 # 칼라 ↔ 장공 벽 틈(한쪽) 0.05
TH_JAM = math.acos(1 - 2 * C_SLOT / PITCH)                              # 두 칼라가 장공 벽에 엇갈려 닿는 기울기: PITCH (1 - cos th) = 2c
TH_KIN = (G_UP + G_DN) / PITCH                                          # 장공 끝(Z)만 볼 때의 한도 — 앞 회차 모델
H_W = Z_WT - Z_COL                                                      # 들림 자세에서 윗날개 윗면 ~ 칼라 선
NUT_Y = (NUT_UP[3] - NUT_UP[2]) / 2                                     # 모형 너트 Y 반폭(맞모가 Y 방향 = 가장 불리)
R['입력'] = {'윗 너트 축 틈(서명)': round(G_NUT, 3), '로드 ↔ 장공 +Y / -Y': [round(SLOT_P, 3), round(SLOT_N, 3)], '장공 원통 축': rodslot,
           '실린더 코 밑 Z · 로드 끝 Z · 나사 윗끝 Z(임시 15)': [Z_NOSE, Z_END, Z_THR], '아래 너트 윗면 Z · 윗 너트 밑면 Z': [NUT_LO[5], NUT_UP[4]],
           '모형 너트 Y 반폭': round(NUT_Y, 3), '칼라 장공 폭 틈(한쪽) · 칼라 사이': [round(C_SLOT, 3), PITCH],
           '기울기 한도 rad — 칼라 장공 폭 걸림 / 장공 끝': [round(TH_JAM, 4), round(TH_KIN, 4)], 'W N': round(W, 3),
           'My Ø4 · My M4 골 N·mm': [round(My4), round(MyT)]}


def rod(F, th, ext, upper, mu=0.2):
    """로드 굽힘: 축 힘 x 너트 모서리 편심(맞모 반 4.04, 상한 — 실제는 장공 옆 살에만 닿아 3.5 이하) + 옆힘 F tan(th + atan mu) x 팔.
    단면 둘: 코 부시 자리(Ø4 민 단면, 팔 = 닿는 면 ~ 코 + 내밈), 나사 윗끝(M4 골, 팔 = 닿는 면 ~ 나사 윗끝)."""
    zc = NUT_UP[4] if upper else NUT_LO[5]
    lb, lt = (Z_NOSE - zc) + ext, Z_THR - zc
    H = F * math.tan(th + math.atan(mu))
    mb, mt = F * NUT_AC / 2 + H * lb, F * NUT_AC / 2 + H * lt
    return {'옆힘 N': round(H, 1), '팔(코 / 나사 윗끝)': [round(lb, 2), round(lt, 2)], '굽힘 N·mm(코 / 나사 윗끝)': [round(mb, 1), round(mt, 1)],
            'SF 첫 항복(코 Ø4 / 나사 윗끝 M4 골)': [round(My4 / mb, 2), round(MyT / mt, 2)], 'SF': round(min(My4 / mb, MyT / mt), 2),
            '참고 SF(나사가 코까지)': round(MyT / mb, 2)}


C = {}


def case(tag, F, th, ext, upper, hw, sign, note=''):
    """sign +1 = 끝이 내려감(윗날개가 로드에 대해 -Y로 -> +Y 틈을 씀), -1 = 끝이 올라감(-Y 틈)."""
    shift = hw * math.sin(th) + 31 * (1 - math.cos(th))
    have = SLOT_P if sign > 0 else SLOT_N
    need = gap_need(th)
    d = {'기울기 rad': round(th, 4), '로드 축 힘 = 탭 힘 N': round(F, 1), '너트 축 틈 필요(맞모) / 있음': [round(need, 3), round(G_NUT, 3)],
         '장공 옆 이동 / 있음(%s)' % ('+Y' if sign > 0 else '-Y'): [round(shift, 2), round(have, 2)], '로드 내밈 mm': round(ext, 2),
         '판정': '안 낌' if need < G_NUT and shift < have else '낌'}
    d.update(rod(F, th, ext, upper))
    d['SF(mu 0.4)'] = rod(F, th, ext, upper, 0.4)['SF']
    if note:
        d['비고'] = note
    C[tag] = d


Z_SEAM, Z_MAT, Z_BALL = 12.1, 10.0, 0.0
ARM_F = Y_CP - Y_FLAT
# A. 들림 · 끝 들기: 멈춤 턱이 받음. 로드가 버티면 th = 0.5 / 60, 붙듦을 넘으면 +Y 칼라 장공 윗끝까지(매트 없음)
thA = G_STOP / (Y_ROD - Y_STOP)
FA = (HAND * (Y_STOP - Y_TIP) + W * (Y_CG - Y_STOP)) / (Y_ROD - Y_STOP)
case('A1 들림·끝 들기(로드가 버팀)', FA, thA, (Y_ROD - Y_STOP) * thA, False, 0.0, -1, '멈춤 턱 힘 %.1f N, 들기 붙듦 ÷ 축 힘 %.2f~%.2f' % (HAND + FA - W, F_LIFT / FA, F_LIFT_MAX / FA))
thA2 = (G_STOP + G_DN) / (Y_CP - Y_STOP)
case('A2 들림·끝 들기(붙듦을 넘어 로드가 끌려 나옴, 매트 없음) — 한도 칼라 장공 폭', F_LIFT_MAX, min(thA2, TH_JAM), (Y_ROD - Y_STOP) * min(thA2, TH_JAM), False, 0.0, -1)
case('A2 들림·끝 들기(붙듦을 넘음) — 상한 가정(+Y 칼라 장공 윗끝)', F_LIFT_MAX, thA2, (Y_ROD - Y_STOP) * thA2, False, 0.0, -1)
# B. 들림 · 끝 누르기: +Y 칼라 둘레. 한도 = min(밑에 닿음, 칼라 장공 폭 걸림). 상한 가정 = 장공 끝 0.2525(폭 걸림을 안 볼 때)
for tag, ztop in (('B1 들림·끝 누르기 이음매 윗면 Z 12.1', Z_SEAM), ('B2 들림·끝 누르기 매트 윗면 Z 10', Z_MAT), ('B3 들림·끝 누르기 볼 윗점 Z 0', Z_BALL), ('B4 들림·끝 누르기 밑에 없음', None)):
    thg = TH_KIN if ztop is None else min(TH_KIN, (Z_SHOE - ztop + G_UP) / ARM_F)
    th = min(thg, TH_JAM)
    case('%s — 한도 %s' % (tag, '칼라 장공 폭' if th < thg else '밑에 닿음'), F_LIFT_MAX, th, (Y_CP - Y_ROD) * th - G_UP, False, H_W + G_UP, +1)
    if thg > TH_JAM:
        case('%s — 상한 가정(폭 걸림 없음)' % tag, F_LIFT_MAX, thg, (Y_CP - Y_ROD) * thg - G_UP, False, H_W + G_UP, +1)
# C. 누름(매트 위) · 끝 들기: 바닥 +Y 끝 둘레, 멈춤 턱. 로드는 윗 너트로 누름(틈 2.3이 먼저 닫힘)
for tag, dz in (('C1 누름 -0.4·끝 들기', 4.9), ('C2 누름 -2.5(매트 윗면)·끝 들기', 7.0)):
    th = min(TH_JAM, (G_STOP + dz) / (Y_FRONT - Y_STOP))
    Sc = (HAND * (Y_FRONT - Y_TIP) - F_HI * (Y_FRONT - Y_ROD) - W * (Y_FRONT - Y_CG)) / (Y_FRONT - Y_STOP)
    case(tag, F_HI, th, dz + G_NUT - (Y_FRONT - Y_ROD) * th, True, H_W - dz, -1, '멈춤 턱 힘 %.1f N' % Sc)
# D·E. 매트 없이 -5.0까지 누른 채(운전 사이클 밖)
thD = (G_STOP + G_DN) / (Y_CP - Y_STOP)
for tag, th in (('D 누름 -5.0(매트 없음)·끝 들기 — 한도 칼라 장공 폭', min(thD, TH_JAM)), ('D 누름 -5.0·끝 들기 — 상한 가정(멈춤 턱까지)', thD)):
    case(tag, F_HI, th, G_DN + G_NUT - (Y_CP - Y_ROD) * th, True, H_W - G_DN, -1)
thE = min(TH_KIN, (Z_SHOE - G_DN - Z_BALL) / (Y_CN - Y_FLAT))
for tag, th in (('E 누름 -5.0(매트 없음)·끝 누르기 — 한도 칼라 장공 폭', min(thE, TH_JAM)), ('E 누름 -5.0·끝 누르기 — 상한 가정(볼 윗점)', thE), ('E 누름 -5.0·끝 누르기 — 상한 가정(장공 끝)', TH_KIN)):
    case(tag, F_HI, th, G_DN + G_NUT - (Y_ROD - Y_CN) * th, True, H_W - G_DN, +1)
# F. 누름(매트 위) · 끝 누르기: 평탄 끝(Y -234.3) 둘레로 넘어가려면 손 x 10.7 > 로드 x 68.3 + W x 57.2
for tag, dz in (('F1 누름 -0.4·끝 누르기', 4.9), ('F2 누름 -2.5·끝 누르기', 7.0)):
    tip_lo = (9.85 * (Y_ROD - Y_FLAT) + W * (Y_CG - Y_FLAT)) / (Y_FLAT - Y_TIP)
    tip_hi = (F_HI * (Y_ROD - Y_FLAT) + W * (Y_CG - Y_FLAT)) / (Y_FLAT - Y_TIP)
    th = min(TH_JAM, (G_UP + dz) / ARM_F)
    case(tag, F_HI, th, dz + G_NUT - (Y_ROD - Y_FLAT) * th, True, H_W - dz, +1,
         '넘어가기 시작하는 손 힘 %.0f N(누름 띠 아래 끝 9.85 N) ~ %.0f N(위 끝 23.8 N)' % (tip_lo, tip_hi))
R['경우'] = C
REF = '참고 SF(나사가 코까지)'
R['가장 불리한 값'] = {'로드 굽힘 SF 최저(mu 0.2) — 모형 한도': min(v['SF'] for k, v in C.items() if '상한 가정' not in k),
                  '로드 굽힘 SF 최저(mu 0.2) — 상한 가정 포함': min(v['SF'] for v in C.values()), 'SF 최저(mu 0.4) — 상한 가정 포함': min(v['SF(mu 0.4)'] for v in C.values()),
                  '참고 SF 최저(나사가 코까지) — 모형 한도 / 상한 가정 포함': [min(v[REF] for k, v in C.items() if '상한 가정' not in k), min(v[REF] for v in C.values())],
                  '탭 힘 최대 N / 136': [round(max(v['로드 축 힘 = 탭 힘 N'] for v in C.values()), 1), 136], '낌': [k for k, v in C.items() if v['판정'] != '안 낌'],
                  '너트 축 틈 여유 최소(있음 - 필요)': round(min(v['너트 축 틈 필요(맞모) / 있음'][1] - v['너트 축 틈 필요(맞모) / 있음'][0] for v in C.values()), 3)}

# ---------- 3. 칼라 장공 폭 걸림에서 손 힘이 가는 곳(들림 · 끝 누르기 · 밑에 없음) ----------
M0 = HAND * (Y_CP - Y_TIP) - F_LIFT_MAX * (Y_CP - Y_ROD) + W * (Y_CP - Y_CG)      # +Y 칼라 둘레
CAP_PET = 40.2 * 77.6                                                   # 인서트 자리 PET-CF 받음 한도(옛 해석: 77.6 N에서 SF 40.2)
s, c = math.sin(TH_JAM), math.cos(TH_JAM)
J = {'+Y 칼라 둘레 모멘트 N·mm': round(M0), '쐐기 팔 PITCH sin th': round(PITCH * s, 2)}
rest = F_LIFT_MAX * (Y_CP - Y_ROD) - W * (Y_CP - Y_CG)                  # 손을 뗀 뒤 되돌리는 모멘트(들기 붙듦 - 무게)
for mu in (0.0, 0.1, 0.2, 0.3):
    n = M0 / (PITCH * (mu * c + s))
    lock = mu * c > s
    n_hold = rest / (PITCH * (mu * c - s)) if lock else None
    J['mu %.1f' % mu] = {'칼라 Y 힘 N': round(n), '칼라 Z 마찰 짝힘 N': round(mu * n), '슈 벽 장공 받음 MPa(Ø7 x t2) / SF(1.5 Sy)': [round(n / 14, 1), round(1.5 * SY / (n / 14), 2)],
                         'PET-CF 인서트 받음 SF(한도 %d N)' % CAP_PET: round(CAP_PET / n, 2), 'M5 12.9 전단 SF(14.2 mm2 x 660 MPa)': round(14.2 * 660 / n, 1),
                         '손을 떼도 걸린 채 남는 Y 힘 문턱 N': round(n_hold) if lock else None,
                         '그 문턱에 이르는 손 힘 N': round(HAND * n_hold / n, 1) if lock else None,
                         '걸린 슈를 푸는 손 힘 N(끝을 위로, 손 100 N으로 눌렀을 때)': round((n * PITCH * (mu * c - s) - rest) / (Y_CP - Y_TIP), 1) if lock else None}
J['걸림 뒤 더 기우는 양(칼라 · 인서트 눌림 합 0.05 / 0.1 mm 가정) rad'] = [round(math.acos(1 - (2 * C_SLOT + d) / PITCH), 4) for d in (0.05, 0.1)]
J['폭 걸림을 없애려면 -Y 장공 폭(0.2525 rad까지)'] = round(2 * R_COL + 2 * C_SLOT + PITCH * (1 - math.cos(TH_KIN)), 2)
J['운전 중(누름, 바닥이 따라 눕는 데 필요한 기울기 0.0035 rad) 폭 걸림까지 남는 기울기 rad'] = round(TH_JAM - 0.0035, 4)
J['걸린 채 남은 슈 평탄 끝(Y -234.3) 밑 높이 Z(들림 17에서)'] = round(Z_SHOE + G_UP - (Y_CP - Y_FLAT) * s, 2)
R['칼라 장공 폭 걸림'] = J

# ---------- 4. 윗날개 탭(장공 5 x 14) ----------
F = F_LIFT_MAX
b_eff = NUT_AF + 2 * 9.5
strip_w = wing_xy[0][1] - (-68.0 + 2.5)
s_root = 6 * F * 12 / (b_eff * T_WING ** 2)
s_strip = (F / 2) * 14 / 8 / (strip_w * T_WING ** 2 / 6)
R['윗날개'] = {'탭 뿌리(팔 12, 유효 폭 %.0f = 너트 맞변 + 45도 x 9.5) σ MPa / SF(굽힘 계수 1.3)' % b_eff: [round(s_root, 1), round(SY / (KB * s_root), 2)],
             '장공 바깥 살(폭 %.1f x t2, 길이 14 양끝 고정, 힘 절반) σ MPa / SF' % strip_w: [round(s_strip, 1), round(SY / (KB * s_strip), 2)],
             '탭 힘 / 기준': [F, 136], '장공 ↔ 윗날개 끝 살(+Y / -Y)': [round(wing_xy[1][1] - (rodslot[-1][1] + 2.5), 2), round((rodslot[0][1] - 2.5) - wing_xy[1][0], 2)]}
# ---------- 5. 새 하중 길(멈춤 턱 ~ 벽 볼트): 형상 · 힘 그대로 -> 옛 모델 값 ----------
R['새 하중 길(브래킷 — 형상 그대로)'] = {k: v for k, v in R0['새 하중 길'].items() if not k.startswith('handcalc')}
dW = W - 0.139782 * 9.80665                                             # v2.17.2 슈 139.782 g 대비
R['그대로인 값'] = {'슈 질량 g': 139.297, '무게 변화 N(v2.17.2 대비)': round(dW, 4), '잡음 비': round((9.85 + dW) / 9.36, 3), '자국 SF': round(2.285 * 21.59 / (21.59 + dW), 3),
               '들기 SF': round(5.34 * 0.139782 / 0.139297, 2)}
R['옛 모델(앞 회차 식 그대로) 요약'] = {k: {kk: v[kk] for kk in v if kk.startswith('SF') or kk.startswith('로드 굽힘') or kk == '판정'} for k, v in R0['경우'].items()}
json.dump(R, open(ROOT + '/fea/results/mech_RX-10_F1b_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
for k, v in R.items():
    if isinstance(v, dict) and k in ('경우', '칼라 장공 폭 걸림'):
        for kk, vv in v.items():
            print(kk, json.dumps(vv, ensure_ascii=False))
    else:
        print(k, json.dumps(v, ensure_ascii=False))
