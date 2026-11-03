# -*- coding: utf-8 -*-
"""N04 해석부 3회차 손계산 — v1.0.15(수정 2회차)에서 새로 그리거나 옮긴 하중 부품.
대상 STEP: tools/out/mech_N04/stepout/P_N04_CYLBKT_fix2.step, P_N04_STORE_fix2.step, P_N04_CHAIN_BAR_fix2.step
FEA 환경 없음(D-16). 형상은 fea/results/mech_N04_fea2_stepbbox.json(이 STEP 바디별 점 bbox·고유 좌표)에서 assert로 확인.
하중·기준은 해석 2회차(mech_N04_fea1_handcalc.py 머리말)와 같다:
  CDJ2B16 추력 0.5 MPa 100.5 N / 0.7 MPa 140.7 N, 자중·사슬 x3 g(운전) / x1 g(오조작), 사슬 6.5 kg 전부 보관 하나(보수),
  손바닥 100x100 0.01 / 0.03 MPa. 판정 M-09 운전 SF 3·오조작 SF 2, SF < 1.2 = 영구 변형(동작).
항복(하한): SUS304 205, A6063-T5 110. E: SUS304 193000, A6063 69000, nu 0.3.
"""
import json, math, os, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
bb = json.load(open(os.path.join(RES, 'mech_N04_fea2_stepbbox.json'), encoding='utf-8'))
RP = {'SUS304': 205.0, 'A6063': 110.0}
E = {'SUS304': 193000.0, 'A6063': 69000.0}
SFMIN = {'run': 3.0, 'mis': 2.0}
F = {'run': math.pi / 4 * 16 ** 2 * 0.5, 'mis': math.pi / 4 * 16 ** 2 * 0.7}
GF = {'run': 3.0, 'mis': 1.0}
PALM = {'run': 0.01, 'mis': 0.03}
G = 9.81
out = {'_note': 'N04 해석 3회차 손계산(FEA 환경 없음 D-16). 단위 mm·N·MPa', 'items': [], 'other': {}}


def item(part, where, case, s, mat, note=''):
    sf = RP[mat] / s if s else float('inf')
    lvl = '동작' if sf < 1.2 else ('됨' if sf >= SFMIN[case] else '디테일')
    out['items'].append({'part': part, 'where': where, 'case': case, 'stress_MPa': round(s, 1), 'mat': mat,
                         'sf': round(sf, 2), 'sf_min': SFMIN[case], 'judge': lvl, 'note': note})

# ---- 형상 확인(STEP) ----
c = bb['P_N04_CYLBKT_P']['uniq']
assert c[0] == [-830.0, -806.0] and c[1] == [767.0, 775.0, 779.0] and c[2] == [-81.0, -44.0, -40.0]
s = bb['P_N04_STORE_P']['uniq']
assert 1528.5 in s[1] and -79.5 in s[2] and -75.5 in s[2] and -123.0 in s[2] and -119.0 in s[2]
assert bb['P_N04_CHAIN_NP_BAR']['bbox'] == [[-969.0, -829.0], [-481.0, -471.0], [-3.0, 0.0]]
assert bb['P_N04_CHAIN_PN_BAR']['uniq'][0] == [-969.0, -831.5, -831.0, -829.0]
cyl = bb['STEPSTEP_WAIT_CDJ2B16-110_P']['bbox']   # 몸 X -828.1~-807.9, Z -80.06~-57.94 -> 축 X -818, Z -69
ax_x, ax_z = (cyl[0][0] + cyl[0][1]) / 2, (cyl[2][0] + cyl[2][1]) / 2

# ---- 1. 꼬리 멈춤: 패드가 러그를 미는 힘선(모델링 보고서 2-1, 패드 X -829.5~-813, 러그 X -831~-828 · 위층 홈 Z -79.5~-75.5) ----
lug_x = (-829.5 + -828.0) / 2          # 패드와 러그가 겹치는 X 띠 가운데
lug_z = (-78.5 + -75.5) / 2            # 러그 3 높이(홈 4 안 가운데)
ex, ez = ax_x - lug_x, ax_z - lug_z    # 로드 축에서 힘선까지
e = math.hypot(ex, ez)
out['other']['line_of_force'] = {'rod_axis': [round(ax_x, 2), round(ax_z, 2)], 'lug': [lug_x, lug_z],
                                 'ex': round(ex, 2), 'ez': round(ez, 2), 'e': round(e, 2)}
d_rod = 5.0
Wr = math.pi * d_rod ** 3 / 32
for k, f in F.items():
    item('CDJ2B16-110 로드(구매품, 참고 M-06)', '로드 Ø5 편심 굽힘(패드 힘선 편심 e)', k, f * e / Wr, 'SUS304',
         '편심 모멘트 %.0f Nmm. 끝 옆 힘으로 바꾸면 약 %.1f N(가이드 길이 12 가정) - SMC 허용치(D-89)와 비교 필요' % (f * e, f * e / (123 + 12)))
# 받침 세운 판 뿌리 Z -44, 단면 X 24 x t4. 힘선 Z = 러그 높이(모델링부 손계산은 축 Z -69, 팔 25)
b, t = 24.0, 4.0
arm_root = -44.0 - lug_z
for k, f in F.items():
    item('P_N04_CYLBKT_P/_N', '세운 판 뿌리 Z -44(24 x t4, 힘선 팔 %.1f)' % arm_root, k, 6 * f * arm_root / (b * t * t), 'SUS304')
    tau = f * abs(ex) / (0.282 * b * t * t)   # 힘선 X 편심 -> 뿌리 단면 비틀림(b/t 6, alpha 0.282)
    item('P_N04_CYLBKT_P/_N', '세운 판 뿌리 비틀림(X 편심 %.2f)' % ex, k, tau * math.sqrt(3), 'SUS304', '등가 sqrt3 tau')
# 날개(Y 767~779, t4, 폭 24) 인서트 끌어냄: 발꿈치 Y 767(힘 -Y, 판 바깥 -Y 끝), 인서트 가운데 Y 771
arm_panel = -40.0 - lug_z
M_p = {k: f * arm_panel for k, f in F.items()}
pull = {k: m / (771 - 767) for k, m in M_p.items()}
out['other']['insert_pull_N'] = {'now(날개 -Y, 지렛대 4)': {k: round(v) for k, v in pull.items()},
                                 'fix(날개 +Y Y 775~795, 발꿈치 775, 인서트 789, 지렛대 14)': {k: round(m / 14) for k, m in M_p.items()},
                                 'M_panel_Nmm': {k: round(v) for k, v in M_p.items()}}
for k in F:
    item('P_N04_CYLBKT_P/_N', '날개 굽힘(24 x t4, 인서트까지 M)', k, 6 * M_p[k] / (b * t * t), 'SUS304')
Ib = b * t ** 3 / 12
out['other']['cylbkt_tip_deflection_mm'] = {k: round(f * arm_root ** 3 / (3 * E['SUS304'] * Ib), 3) for k, f in F.items()}
# 패드-러그 지압(겹침 X 1.5 x Z 3)
out['other']['pad_lug_bearing_MPa'] = {k: round(f / (1.5 * 3.0), 1) for k, f in F.items()}

# ---- 2. 보관 P/N(SUS304 t1.5) ----
t = 1.5
D = E['SUS304'] * t ** 3 / (12 * (1 - 0.3 ** 2))
m_chain = 6.5
W_in = -968.5 - (-831.5)
W_in = abs(W_in)                          # 바닥 안쪽 폭 137
L_sep = 1528.5 - 933.0                   # +X 벽 아래쪽이 위쪽과 떨어진 길이(위층 홈)
h_wall = 125.0 - 40.0                    # -X 옆벽 높이 85(판 밑면 Z -40에 매달림)
res = {}
for k, g in GF.items():
    q = m_chain * G * g / (L_sep * W_in)   # 사슬 전부가 떨어진 구간 바닥에(보수)
    m = q * W_in ** 2 / 2                  # +X 쪽이 홈으로 떨어져 바닥은 -X 벽에서 외팔 띠
    sig = 6 * m / t ** 2
    item('P_N04_STORE_P/_N', '바닥 -X 꺾임(외팔 띠 137, +X 벽이 위층 홈으로 떨어짐)', k, sig, 'SUS304',
         '양쪽 벽 지지였던 2회차 14.6(운전)의 약 4배')
    item('P_N04_STORE_P/_N', '-X 옆벽 위 끝 Z -40(같은 m)', k, sig, 'SUS304')
    d_plate = q * W_in ** 4 / (8 * D)
    th = m * h_wall / D
    res[k] = {'q_MPa': round(q, 5), 'bottom_mm': round(d_plate, 2), 'wall_rot_mm': round(th * W_in, 2),
              'plusX_edge_drop_mm': round(d_plate + th * W_in, 2)}
out['other']['store_plusX_edge_drop'] = res
out['other']['store_plusX_edge_drop_note'] = ('+X 벽 아래쪽(Y 933~1528.5)은 위층 홈 Z -79.5~-75.5로 위쪽과 떨어지고 Y 930~933(3)과 끝벽에만 이어진다. '
                                              '끝벽·앞 3 폭 이음의 도움은 무시(긴 쪽 596 ≫ 137). 오조작 열은 x1 g(정지 처짐)')
# 끝벽(U턴 받이) X 137 x Z 83.5 판, 네 변 단순 지지, 고른 하중(사슬 끝을 실린더 추력 2배로 되받는 보수 값)
a, bw = W_in, 125.0 - 1.5 - 40.0
beta = 0.4872   # Roark 표 11.4 case 1a, a/b = 1.64
for k, f in F.items():
    q = 2 * f / (a * bw)
    item('P_N04_STORE_P/_N', '끝벽 Y 1528.5~1530(137 x 83.5, 네 변 지지, 2F 고르게)', k, beta * q * bw ** 2 / t ** 2, 'SUS304',
         'U턴 받이 힘의 실제 값은 사슬 마찰 수준. 막힘(안장 Y 축 밀어 넣기)은 서보 토크 제한으로 막는다(U-09 제어 제약)')
# 위층 턱(폭 10, t1.5): 사슬 전부가 위층 두 턱(길이 500)에
for k, g in GF.items():
    w = m_chain * G * g / (2 * 500.0)
    item('P_N04_STORE_P/_N', '위층 턱 X 10 x t1.5(Y 930~1430)', k, 6 * w * 5.0 / t ** 2, 'SUS304')

# ---- 3. 안쪽 사슬 끝 막대 A6063 140 x 10 x 3 ----
span = (-834.0) - (-966.0)   # 슬롯 X -966~-834에 양 끝 얹힘(사슬 몸 지지 무시, 보수)
bw, tb = 10.0, 3.0
Zb = bw * tb ** 2 / 6
Ib = bw * tb ** 3 / 12
for k, p in PALM.items():
    P = p * bw * 100.0       # 손바닥 100 x 100 가운데, 막대 폭 10 몫
    M = P / 2 * span / 2 - P / 2 * 100.0 / 4
    item('P_N04_CHAIN_NP/PN_BAR', '막대 가운데 굽힘(지지 %.0f, 10 x t3, 손바닥 몫 %.0f N)' % (span, P), k, M / Zb, 'A6063')
out['other']['bar_deflection_mm'] = {k: round(p * bw * 100.0 * span ** 3 / (48 * E['A6063'] * Ib), 2) for k, p in PALM.items()}
out['other']['bar_point300_ref'] = {'stress_MPa': round(300 * span / 4 / Zb), 'note': '300 N 한 점은 폭 10 막대에 맞지 않는 하중(사슬 칸도 같은 폭)이라 참고만. 판정은 손바닥 모델(작은 받침 규칙)'}
# 멈춤 러그 지압: NP 홈 물림 X 1(-830~-829) x Z 3, PN 1 x Z 2. 허용 지압 1.5 Rp / SF
for name, A in (('NP', 3.0), ('PN', 2.0)):
    out['other']['bar_lug_allow_N_' + name] = {k: round(1.5 * RP['A6063'] * A / SFMIN[k], 1) for k in SFMIN}
out['other']['bar_lug_note'] = '정하중 스프링 형번 미정(바디 없음). 물림 X 1 mm는 막대 X 놀이가 1을 넘으면 빠진다(정밀 체인, 검도 몫)'

json.dump(out, open(os.path.join(RES, 'mech_N04_fea2_handcalc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i in out['items']:
    print(i['case'], i['sf'], i['judge'], i['part'], i['where'][:40])
print(json.dumps(out['other'], ensure_ascii=False)[:1500])
