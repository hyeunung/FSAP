# -*- coding: utf-8 -*-
"""DC-03 해석부 2회차 손계산 — P_DC03_YMOV 고친 안(fix1, v1.0.10). FEA 환경 없음(D-16).
형상(tools/out/mech_DC-03/stepout/P_DC03_YMOV_fix1.step 꼭짓점, 월드 mm, J 0):
  다리 웹 X -1028~-1025, Y -340~-280(60), Z -258~-170, t3
  옆판1 X -1043~-1028, Y -340~-337, Z -230~-173 / 옆판2 X -1043~-1025, Y -283~-280, Z -230~-176 (Z -230 아래 없음)
  볼트 CB5-12 x2 Y -325·-295, Z -245, 머리 Z -249~-241(-X 면, X -1033까지)
  대차 U4_Y_CARR -X 면 X -1025, Z -260~-230
경계조건(모델 바꿈, 보고서 맨 위):
  옛 모델(1회차): 대차 면 Z -260~-230 전체가 다리를 고정 → 위험 단면 Z -230(ㄷ 단면)
  새 모델: 하중(팔 끝 아래로)이 다리 위쪽을 -X(대차에서 떨어지는 쪽)로 돌린다 → 볼트 위 판은 대차에서 들뜬다.
           고정은 볼트 머리 조임 자리(머리 끝 Z -241 + 조임 원뿔 약 t3 x 0.6 → Z -239)뿐, 지레 받침은 다리 아래 끝 Z -258.
           → Z -239~-230 웹만(60x3) 띠가 같은 모멘트를 받는다(모멘트는 다리 길이 따라 일정)
하중: 1회차와 같음(models.json P_DC03_YMOV), 판금 질량 fix1 0.553 kg
판정: M-09 운전 SF 3·오조작 SF 2, SF < 1.2 영구 변형(동작)
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

G = 9.81
RP, E = 205.0, 193000.0
SFMIN = {'run': 3.0, 'mis': 2.0}
M_YMOV = 0.553
HAND = 100.0
F_bear_run = 4.6 * 3


def judge(name, case, s=0.0, tau=0.0, extra=None):
    vm = math.sqrt(s * s + 3 * tau * tau)
    sf = RP / vm if vm else float('inf')
    m = SFMIN[case]
    r = {'part': name, 'case': case, 'sigma_vm_MPa': round(vm, 1), 'sf': round(sf, 2), 'sf_min': m, 'ok': sf >= m,
         'near_10pct': m <= sf < 1.1 * m, 'motion_break': sf < 1.2, 'oversize_3x': sf >= 3 * m}
    if extra:
        r.update(extra)
    return r


def sec_I(rects):
    A = sum(b * h for b, h, _ in rects)
    yc = sum(b * h * y for b, h, y in rects) / A
    I = sum(b * h ** 3 / 12 + b * h * (y - yc) ** 2 for b, h, y in rects)
    top = max(y + h / 2 for _, h, y in rects) - yc
    bot = yc - min(y - h / 2 for _, h, y in rects)
    return A, yc, I, top, bot


# 모멘트(다리 단면, 1회차 식, 질량만 fix1)
M_run = F_bear_run * 220 + M_YMOV * G * 3 * 125
M_mis = HAND * (1277 - 1025) + 4.6 * 220 + M_YMOV * G * 125

Z_web = 60 * 3 ** 2 / 6
A_c, yc_c, I_c, t_c, b_c = sec_I([(60, 3, 1.5), (3, 15, 3 + 7.5), (3, 15, 3 + 7.5)])
c_c = max(t_c, b_c)

R = []
# 옛 모델: Z -230 고정, ㄷ 단면
R.append(judge('옛 모델 Z -230 ㄷ 단면', 'run', M_run * c_c / I_c, extra={'model': 'old', 'I_mm4': round(I_c)}))
R.append(judge('옛 모델 Z -230 ㄷ 단면', 'mis', M_mis * c_c / I_c, extra={'model': 'old'}))
# 새 모델: Z -239~-230 웹만
R.append(judge('새 모델 Z -239~-230 웹만 띠(볼트 조임 끝 ~ 옆판 시작)', 'run', M_run / Z_web, extra={'model': 'new', 'Z_mm3': Z_web}))
R.append(judge('새 모델 Z -239~-230 웹만 띠(볼트 조임 끝 ~ 옆판 시작)', 'mis', M_mis / Z_web, extra={'model': 'new'}))
# 새 모델, ㄷ 단면 위(Z -230 위) — 옆판 시작 자리
R.append(judge('새 모델 Z -230 위 ㄷ 단면', 'mis', M_mis * c_c / I_c, extra={'model': 'new'}))
# 웹 띠 길이 9 회전 → 팔 끝 처짐(탄성 가정)
theta = M_mis * 9 / (E * 60 * 27 / 12)
R[3]['defl_tip_from_band_mm'] = round(theta * 252, 2)

# 고친 안 A2: 옆판 2장을 Z -258까지 내림(X -1043~-1028, Y -340~-337 / -283~-280). 볼트 머리와 Y 7.75 그대로
R_fix = [judge('고친 안 A2 옆판 Z -258까지(볼트 자리도 ㄷ)', 'mis', M_mis * c_c / I_c),
         judge('고친 안 A2 옆판 Z -258까지(볼트 자리도 ㄷ)', 'run', M_run * c_c / I_c)]
# 고친 안 B2: 볼트 머리 밑 누름 띠판 SUS t6 x 54(Y -337~-283) x Z -258~-228, 옆판에 용접 → 띠 Z -239~-230이 t3+t6
Zb2 = 54 * 9 ** 2 / 6 + 6 * 3 ** 2 / 6
R_fix.append(judge('고친 안 B2 누름 띠판 t6(볼트 길이 +6, CB5-16)', 'mis', M_mis / Zb2))

# 옆판-웹 이음(모델은 한 바디, 실물 용접 또는 굽힘) 전단 흐름: V = 100 N
Q = 2 * 3 * 15 * abs((3 + 7.5) - yc_c)
q = (HAND + M_YMOV * G) * Q / I_c   # N/mm
weld = {'q_N_per_mm': round(q, 2), 'fillet_a2_tau_MPa': round(q / (2 * 0.7 * 2), 2), 'sf': round(RP / math.sqrt(3) / (q / (2 * 0.7 * 2)), 1)}

# 볼트: 모멘트 같음 → 지레 13(볼트 Z -245 ↔ 다리 아래 끝 Z -258)
bolt_mis = calc(5, 9, M_mis / 13 / 2, base='A5052', sf_min=2.0)
bolt_run = calc(5, 9, M_run / 13 / 2, base='A5052', sf_min=3.0)

out = {'case': 'mech_DC-03_fix1_handcalc', 'part': 'P_DC03_YMOV (fix1, v1.0.10)', 'M_Nmm': {'run': round(M_run), 'mis': round(M_mis)},
       'section': {'Z_web_mm3': Z_web, 'I_channel_mm4': round(I_c), 'c_mm': round(c_c, 2), 'yc_mm': round(yc_c, 2)},
       'results': R, 'fix': R_fix, 'weld': weld, 'bolt': {'mis': bolt_mis, 'run': bolt_run}}
json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-03_fix1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
for r in R + R_fix:
    print(r['case'], r['part'], r['sigma_vm_MPa'], 'SF', r['sf'], 'OK' if r['ok'] else ('BREAK' if r['motion_break'] else 'NEAR'))
print('weld', weld)
print('bolt mis', {k: bolt_mis[k] for k in bolt_mis if 'sf' in k.lower()} if isinstance(bolt_mis, dict) else bolt_mis)
