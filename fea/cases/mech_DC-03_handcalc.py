# -*- coding: utf-8 -*-
"""DC-03 해석부 손계산 — X·Y 케이블 베어 자리 새 하중 부품 4개 (v1.0.9). FEA 환경 없음(D-16).
형상: tools/out/mech_DC-03/stepout/P_DC03_*.step 의 꼭짓점 좌표(CARTESIAN_POINT)와 changed_parts.json bbox. 월드 mm, J 0.
  XTROUGH SUS304 t2: 바닥 Z -380~-378(U2_BASE 위에 전면 앉음, CB5 x6), 바깥 벽 Y 1485~1487 Z -378~-298(높이 80), 창 X -590~-510 Z -370~-310(위 띠 12)
  XMOV SUS304 t3 U: A면 Y 1000~1003 Z -348~-295(보 +Y 끝면, CB5 x2 X -1030·-970 Z -320), B면 Z -348~-345 Y 1003~1098, C면 Y 1098~1101 Z -348~-262. 폭 X 100
  YTRAY SUS304 t2 ㄷ: 바닥 X -1284~-1204(80) Z -360~-358, 벽 Z -358~-330(30), 받침 = 끝 탭(Y ±890~945, X -1204~-1052) + 끝 플랜지 X -1050 CB5 x2/끝(Z -325). 받침 사이 1835
  YMOV SUS304 t3: 팔 Z -173~-170 X -1277~-1025 Y -340~-280(X<-1209는 Y -340~-287), 보강 Y -283~-280 Z -188~-173 X -1209~-1031(다리 쪽 릴리프, 다리와 안 붙음),
        다리 X -1028~-1025 Z -258~-170(대차 -X 면에 CB5 x2 Y -325·-295 Z -245; 대차 면은 Z -260~-230 → 다리 Z -230~-170은 받침 없는 띠)
하중(임시값, 출처):
  베어 질량: X E4.56 2.3 kg·Y 2400.05 2.2 kg(케이블 포함, 선정 손계산 6절, D-88 임시). STEP대기 상자 질량(PA 꽉 찬 상자 61·23 kg)은 실물이 아니라 쓰지 않는다
  Y 베어 움직이는 끝: 위 줄 반 무게 4.6 N(선정). 판금 자체 질량 = changed_parts.json
  가속: X·Y 1.53 m/s²(hand_n03.json corner, N03 해석과 같음)
  운전 = 자중·베어 x3 g(지시) + 베어 밀기 10.3 N(선정 6절)
  오조작 = 정비 중 손 100 N(가장 불리한 자리·방향, DC-04와 같은 값) + 1 g
  참고(what-if, 문제로 세지 않음): 베어 걸림에서 서보 최대 힘 X 375 N·Y 224 N(N03 오조작값)이 움직이는 끝 받침에 들어옴
판정: M-09 운전 SF 3·오조작 SF 2(요구서 6-1 기본값). 6-2 변위 미정(D-08) → 처짐은 동작 틈과 비교. SUS304 Rp0.2 205, E 193 GPa. CB 12.9.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam

G = 9.81
RP, E = 205.0, 193000.0
SFMIN = {'run': 3.0, 'mis': 2.0}
mass = {'XTROUGH': 13.755, 'XMOV': 0.546, 'YTRAY': 4.516, 'YMOV': 0.510}
BEAR = {'X': 2.3, 'Y': 2.2}
PUSH = 10.3
HAND = 100.0
JAM = {'X': 375.0, 'Y': 224.0}


def judge(name, case, s=0.0, tau=0.0, extra=None):
    vm = math.sqrt(s * s + 3 * tau * tau)
    sf = RP / vm if vm else float('inf')
    m = SFMIN.get(case, 2.0)
    r = {'part': name, 'case': case, 'sigma_vm_MPa': round(vm, 2), 'sf': round(sf, 2), 'sf_min': m, 'ok': sf >= m,
         'near_10pct': m <= sf < 1.1 * m, 'motion_break': sf < 1.2, 'oversize_3x': sf >= 3 * m}
    if extra:
        r.update(extra)
    return r


def sec_I(rects):
    """rects: (b, h, yc) 가로 b, 세로 h, 도심 높이 yc. 수평축 I, 도심, 위·아래 끝 거리"""
    A = sum(b * h for b, h, _ in rects)
    yc = sum(b * h * y for b, h, y in rects) / A
    I = sum(b * h ** 3 / 12 + b * h * (y - yc) ** 2 for b, h, y in rects)
    top = max(y + h / 2 for _, h, y in rects) - yc
    bot = yc - min(y - h / 2 for _, h, y in rects)
    return A, yc, I, top, bot


R = []
# ---------- 1. YTRAY 홈통(단순 받침 1835, ㄷ 80x30 t2 위로 열림) ----------
L = 1835.0
A, yc, I, top, bot = sec_I([(80, 2, 1), (2, 28, 16), (2, 28, 16)])
c = max(top, bot)
w_run = (BEAR['Y'] + mass['YTRAY']) * G * 3 / L
M = w_run * L ** 2 / 8
d = 5 * w_run * L ** 4 / (384 * E * I)
R.append(judge('P_DC03_YTRAY 홈통 가운데', 'run', M * c / I, extra={'I_mm4': round(I), 'M_Nmm': round(M), 'defl_mm': round(d, 2),
             'note': '3 g 베어+홈통 등분포. 처짐은 베어 밑 받침 처짐일 뿐(위 여유 48)'}))
w1 = (BEAR['Y'] + mass['YTRAY']) * G / L
M = w1 * L ** 2 / 8 + HAND * L / 4
d = 5 * w1 * L ** 4 / (384 * E * I) + HAND * L ** 3 / (48 * E * I)
R.append(judge('P_DC03_YTRAY 홈통 가운데', 'mis', M * c / I, extra={'M_Nmm': round(M), 'defl_mm': round(d, 2),
             'note': '손 100 N 가운데 + 1 g. 벽 위 끝(열린 쪽) 압축 — 벽 높이/두께 14로 국부 좌굴 걱정 없음'}))
# 끝 탭: L(바닥 연장 55x2 + 끝 웹 2x60 중 아래 30만 보수로) 팔 194(끝 플랜지 X -1050 → 홈통 중심 X -1244)
At, ytc, It, tt, tb = sec_I([(55, 2, 1), (2, 28, 16)])
ct = max(tt, tb)
F_tab = (BEAR['Y'] + mass['YTRAY']) * G * 3 / 2
M = F_tab * 194
R.append(judge('P_DC03_YTRAY 끝 탭 뿌리', 'run', M * ct / It, extra={'I_mm4': round(It), 'F_N': round(F_tab, 1), 'M_Nmm': round(M)}))
F_tab_m = (BEAR['Y'] + mass['YTRAY']) * G / 2 + HAND
M_m = F_tab_m * 234   # 손이 바깥 벽 X -1284 끝에
R.append(judge('P_DC03_YTRAY 끝 탭 뿌리', 'mis', M_m * ct / It, extra={'F_N': round(F_tab_m, 1), 'M_Nmm': round(M_m), 'note': '손 100 N 탭 바로 옆 바깥 모서리'}))
# 끝 플랜지 볼트: 지렛대 = 볼트 Z -325 ↔ 플랜지 아래 끝 Z -360 = 35, 볼트 2개 나란히
bolt_run = M / 35 / 2 + F_tab / 2 * 0
bolt_mis = M_m / 35 / 2
bc = {'YT_run': calc(5, 10, bolt_run, base='A5052', sf_min=3.0), 'YT_mis': calc(5, 10, bolt_mis, base='A5052', sf_min=2.0)}

# ---------- 2. XTROUGH (바닥 전면 받침, 바깥 벽 외팔 80) ----------
# 운전: 눕힌 베어가 벽을 미는 힘 = 밀기 10.3 N, 벽 위 끝, 유효 폭 2h
bw = beam(2, 160, 80, load=PUSH, e=E, sy=RP, sf_min=3.0)
R.append(judge('P_DC03_XTROUGH 바깥 벽 뿌리', 'run', bw['stress_MPa'], extra={'defl_mm': bw['deflection_mm'], 'b_eff': 160}))
bw = beam(2, 160, 80, load=HAND, e=E, sy=RP, sf_min=2.0)
R.append(judge('P_DC03_XTROUGH 바깥 벽 뿌리', 'mis', bw['stress_MPa'], extra={'defl_mm': bw['deflection_mm'], 'b_eff': 160,
             'note': '손 100 N 벽 위 끝. 유효 폭 2h(점하중 외팔 판). 보수 폭 100이면 아래 줄'}))
bw2 = beam(2, 100, 80, load=HAND, e=E, sy=RP, sf_min=2.0)
R.append(judge('P_DC03_XTROUGH 바깥 벽 뿌리(보수 폭 100)', 'mis', bw2['stress_MPa'], extra={'defl_mm': bw2['deflection_mm']}))
# 창 위 띠: 12(Z -310~-298) x t2, 양 끝 고정 길이 80, 가운데 손 100 N(벽 바깥에서 안으로)
Iw = 12 * 2 ** 3 / 12
Mw = HAND * 80 / 8
dw = HAND * 80 ** 3 / (192 * E * Iw)
R.append(judge('P_DC03_XTROUGH 창 위 띠 12', 'mis', Mw * 1 / Iw, extra={'defl_mm': round(dw, 2), 'note': '양 끝 고정 보, 창 양옆 기둥 회전 무시(비보수 쪽이지만 띠 휨이 지배)'}))
# 바닥: U2_BASE에 전면 앉음 → 베어 3 g 접촉압 무시할 만
R.append({'part': 'P_DC03_XTROUGH 바닥', 'case': 'run', 'note': 'U2_BASE 위 전면 받침, 베어 2.3 kg x3 g / 접촉 넓이 > 0.3 m² → < 0.001 MPa', 'ok': True,
          'sf': None})

# ---------- 3. XMOV (U t3, 폭 100) ----------
# 운전: X 밀기 10.3 N + 베어 반 질량 x 가속(선정에 포함) → 판 면 안 힘. B면 면 안 굽힘(깊이 100, 길이 98)
Zb_in = 3 * 100 ** 2 / 6
R.append(judge('P_DC03_XMOV B면(X 힘 면 안)', 'run', PUSH * 98 / Zb_in))
# 오조작: 손 100 N 아래로 C면 위 끝 → B면 면 밖 외팔 98
bb = beam(3, 100, 98, load=HAND + mass['XMOV'] * G, e=E, sy=RP, sf_min=2.0)
R.append(judge('P_DC03_XMOV B면 면 밖(손 Z)', 'mis', bb['stress_MPa'], extra={'defl_mm': bb['deflection_mm']}))
bc_ = beam(3, 100, 86, load=HAND, e=E, sy=RP, sf_min=2.0)
R.append(judge('P_DC03_XMOV C면 면 밖(손 Y)', 'mis', bc_['stress_MPa'], extra={'defl_mm': bc_['deflection_mm']}))
# 손 X 100 N: B면 면 안 + A면 비틀림 T = 100 x 98(받침 무시한 자유 비틀림 하한)
T = HAND * 98
tau = T / (100 * 3 ** 2 / 3)
R.append(judge('P_DC03_XMOV A면 비틀림(손 X)', 'mis', HAND * 98 / Zb_in, tau, extra={'note': 'A면이 보 끝면에 눌려 받히는 쪽은 무시(하한)'}))
bolt_xm = calc(5, 9, HAND * 98 / 60 + HAND, base='A5052', sf_min=2.0)   # 볼트 2개 간격 60 지렛대 + 직접

# ---------- 4. YMOV (팔 + 다리, t3) ----------
xc_bear = -1245.0   # 베어 움직이는 끝 중심 X(베어 X -1277~-1213)
leg_x = -1025.0
arm_b = 1277 - 1025
xg = -1150.0       # 판금 무게중심 어림
F_bear_run = 4.6 * 3
M_run = F_bear_run * (leg_x - xc_bear) * -1 + mass['YMOV'] * G * 3 * (leg_x - xg) * -1
M_run = abs(F_bear_run * (xc_bear - leg_x)) + abs(mass['YMOV'] * G * 3 * (xg - leg_x))
Z_leg = 60 * 3 ** 2 / 6
R.append(judge('P_DC03_YMOV 다리(받침 없는 띠 Z -230~-170, 면 밖)', 'run', M_run / Z_leg, extra={'M_Nmm': round(M_run), 'Z_mm3': Z_leg}))
M_mis = HAND * arm_b + 4.6 * (xc_bear - leg_x) * -1 * -1 + mass['YMOV'] * G * 125
M_mis = HAND * arm_b + 4.6 * 220 + mass['YMOV'] * G * 125
s_leg_mis = M_mis / Z_leg
R.append(judge('P_DC03_YMOV 다리(받침 없는 띠, 면 밖)', 'mis', s_leg_mis, extra={'M_Nmm': round(M_mis), 'note': '손 100 N 팔 끝 X -1277 아래로 + 1 g'}))
# 팔 뿌리(보강 L 단면, X -1031): 보강이 다리와 안 붙어 다리 쪽 모서리 앞(X -1031)까지
Aa, yca, Ia, ta, ba = sec_I([(60, 3, 1.5 + 15), (3, 15, 7.5)])   # 팔 Z -173~-170 → 높이 15~18, 보강 0~15(Z -188~-173)
ca = max(ta, ba)
R.append(judge('P_DC03_YMOV 팔 뿌리(L 단면)', 'mis', HAND * (1277 - 1031) * ca / Ia, extra={'I_mm4': round(Ia)}))
R.append(judge('P_DC03_YMOV 팔 좁은 끝(X -1209, 평판 53)', 'mis', HAND * (1277 - 1209) / (53 * 9 / 6)))
d_tip = HAND * 68 ** 3 / (3 * E * 53 * 27 / 12) + HAND * 246 ** 3 / (3 * E * Ia)
# 다리 띠 회전 → 끝 처짐(손): 띠 길이 60 외팔, 모멘트 M_mis
theta = M_mis * 60 / (E * 60 * 27 / 12)
d_leg = theta * arm_b
R[-1]['defl_tip_mm'] = round(d_tip + d_leg, 2)
th_run = M_run * 60 / (E * 60 * 27 / 12)
d_run = th_run * 220 + F_bear_run * 220 ** 3 / (3 * E * Ia)
bolt_ym = calc(5, 9, M_mis / 13 / 2, base='A5052', sf_min=2.0)   # 지렛대 = 볼트 Z -245 ↔ 다리 아래 끝 Z -258 = 13 (보수)
bolt_ym_run = calc(5, 9, M_run / 13 / 2, base='A5052', sf_min=3.0)

# 고친 안 A(추천): 다리 양 옆 가장자리(Y -340·-280)를 -X로 15 굽힌 ㄷ 다리(Z -230~-173, 받침 없는 띠 전 길이), 팔 보강과 모서리 용접(릴리프 대신)
# 다리 웹 60x3 + 옆 플랜지 2장 3 x 15(X 방향). 굽힘 방향 = X. 새 부피는 X -1043~-1028 · Z -230~-173 띠 2줄뿐
Ag, ygc, Ig, tg, bg = sec_I([(60, 3, 1.5), (3, 15, 3 + 7.5), (3, 15, 3 + 7.5)])
cg = max(tg, bg)
fix = judge('고친 안 A YMOV ㄷ 다리(옆 플랜지 15 x2)', 'mis', M_mis * cg / Ig, extra={'I_mm4': round(Ig)})
fix_run = judge('고친 안 A YMOV ㄷ 다리(옆 플랜지 15 x2)', 'run', M_run * cg / Ig)
# 고친 안 B: 다리 t3 → 판 바꿈 없이 대차 받침 면을 Z -175까지 올림(대차 블록) — 받침 없는 띠 5
# 고친 안 C: 팔·다리 t6 판(SUS304 t6, 굽힘 R6)
fixC = judge('고친 안 C YMOV t6', 'mis', M_mis / (60 * 36 / 6))

# ---------- 참고(what-if) 베어 걸림 서보 최대 힘 ----------
wi = []
wi.append(judge('what-if XMOV A면 비틀림(걸림 X 375 N, 받침 무시)', 'mis', JAM['X'] * 98 / Zb_in, JAM['X'] * 98 / (100 * 9 / 3)))
wi.append(judge('what-if YMOV 다리 비틀림(걸림 Y 224 N, 팔 220)', 'mis', 0, JAM['Y'] * 220 / (60 * 9 / 3)))
wi.append(judge('what-if 고친 안 A ㄷ 다리(걸림 Y) — 비틀림을 옆 플랜지 짝힘으로(간격 57)', 'mis',
                JAM['Y'] * 220 / 57 * 1.0 / (3 * 15) ))

# ---------- 과사양(M-09) ----------
over = [r for r in R if r.get('sf') and r['sf'] >= 3 * r['sf_min']]

out = {'results': R, 'bolts': {'YT': bc, 'XM_mis': bolt_xm, 'YM_mis': bolt_ym, 'YM_run': bolt_ym_run},
       'YMOV_tip_defl_mm': {'run': round(d_run, 2), 'mis': R[-1]['defl_tip_mm']},
       'fix_YMOV': {'gusset': [fix, fix_run], 't6': fixC}, 'what_if_jam': wi,
       'oversize': [(r['part'], r['case'], r['sf']) for r in over],
       'section': {'YTRAY_I': round(I), 'tab_I': round(It), 'YMOV_arm_I': round(Ia), 'gusset_I': round(Ig)}}
p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-03_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in R + [fix, fix_run, fixC] + wi:
    print(f"{r['part'][:48]:48s} {r['case']:4s} SF {r.get('sf')}  {'OK' if r.get('ok') else 'NG'}{' 동작' if r.get('motion_break') else ''}")
print('bolts min SF', {k: min(v['sf_operating'].values()) for k, v in [('YT_run', bc['YT_run']), ('YT_mis', bc['YT_mis']), ('XM', bolt_xm), ('YM', bolt_ym), ('YMr', bolt_ym_run)]})
print('YMOV tip defl', out['YMOV_tip_defl_mm'], 'oversize', len(over))
