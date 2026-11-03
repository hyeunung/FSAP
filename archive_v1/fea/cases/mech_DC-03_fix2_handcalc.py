# -*- coding: utf-8 -*-
"""DC-03 해석부 3회차 손계산 — P_DC03_YMOV 고친 안(fix2, v1.0.11). FEA 환경 없음(D-16).
형상(tools/out/mech_DC-03/stepout/P_DC03_YMOV_fix2.step 꼭짓점 77개, 월드 mm, J 0):
  다리 웹 X -1028~-1025, Y -340~-280(60), Z -258~-170, t3
  옆판1 X -1043~-1028, Y -340~-337, Z -258~-173 / 옆판2 X -1043~-1028(위쪽 -1025), Y -283~-280, Z -258~-176
  웹 볼트 구멍 2개 Y -327.75~-322.25 / -297.75~-292.25(지름 5.5), Z -245
  대차 U4_Y_CARR -X 면 X -1025, Z -260~-230
경계조건: 2회차(models.json P_DC03_YMOV)와 같다. 하중이 다리 위를 -X로 돌려 볼트 위 판은 들뜨고,
  고정은 볼트 조임 자리(Z -239까지), 지레 받침은 다리 아래 끝 Z -258. 모멘트는 다리 길이 따라 일정.
하중: 2회차와 같음, 판금 질량 fix2 0.573 kg(부피 72,240.3 mm3)
판정: M-09 운전 SF 3·오조작 SF 2, SF < 1.2 영구 변형(동작)
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

G = 9.81
RP, E = 205.0, 193000.0
SFMIN = {'run': 3.0, 'mis': 2.0}
M_YMOV = 0.573
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


M_run = F_bear_run * 220 + M_YMOV * G * 3 * 125
M_mis = HAND * (1277 - 1025) + 4.6 * 220 + M_YMOV * G * 125

# ㄷ 단면(웹 60x3 + 옆판 3x15 x2), 굽힘 축은 Y 방향, 거리는 X
ch = [(60, 3, 1.5), (3, 15, 3 + 7.5), (3, 15, 3 + 7.5)]
A_c, yc_c, I_c, t_c, b_c = sec_I(ch)
c_c = max(t_c, b_c)
# 볼트 구멍 자리 Z -245: 웹에서 5.5 x 2 = 11 뺌
ch_net = [(60 - 11, 3, 1.5), (3, 15, 3 + 7.5), (3, 15, 3 + 7.5)]
A_n, yc_n, I_n, t_n, b_n = sec_I(ch_net)
c_n = max(t_n, b_n)

R = []
R.append(judge('Z -258~-170 ㄷ 단면(옆판 다리 아래 끝까지)', 'run', M_run * c_c / I_c, extra={'I_mm4': round(I_c), 'c_mm': round(c_c, 2)}))
R.append(judge('Z -258~-170 ㄷ 단면(옆판 다리 아래 끝까지)', 'mis', M_mis * c_c / I_c))
R.append(judge('볼트 구멍 자리 Z -245 순단면(웹 -11), 모멘트 전부 가정(안전 쪽)', 'run', M_run * c_n / I_n, extra={'I_mm4': round(I_n), 'c_mm': round(c_n, 2)}))
R.append(judge('볼트 구멍 자리 Z -245 순단면(웹 -11), 모멘트 전부 가정(안전 쪽)', 'mis', M_mis * c_n / I_n))
# 옛 위험 띠 Z -239~-230: 이제 ㄷ 단면 → 위 첫 줄과 같음(참고 표시)
R.append(judge('2회차 위험 띠 Z -239~-230(이제 ㄷ)', 'mis', M_mis * c_c / I_c, extra={'was_sf': 0.69}))

# 옆판-웹 이음(용접 필릿 a2 가정) 전단 흐름, V = 손 100 N + 자중
Q = 2 * 3 * 15 * abs((3 + 7.5) - yc_c)
q = (HAND + M_YMOV * G) * Q / I_c
tau_w = q / (2 * 0.7 * 2)
weld = {'q_N_per_mm': round(q, 2), 'fillet_a2_tau_MPa': round(tau_w, 2), 'sf': round(RP / math.sqrt(3) / tau_w, 1)}

# 볼트 CB5-12 x2, 지레 13(볼트 Z -245 ↔ 다리 아래 끝 Z -258), 대차 A5052 암나사
bolt_mis = calc(5, 9, M_mis / 13 / 2, base='A5052', sf_min=2.0)
bolt_run = calc(5, 9, M_run / 13 / 2, base='A5052', sf_min=3.0)

# 팔 끝 처짐(다리 회전, Z -239~-170 길이 69 ㄷ 단면, 탄성)
theta = M_mis * 69 / (E * I_c)
defl = round(theta * 252, 3)

out = {'case': 'mech_DC-03_fix2_handcalc', 'part': 'P_DC03_YMOV (fix2, v1.0.11)', 'mass_kg': M_YMOV,
       'M_Nmm': {'run': round(M_run), 'mis': round(M_mis)},
       'section': {'I_channel_mm4': round(I_c), 'c_mm': round(c_c, 2), 'I_net_mm4': round(I_n), 'c_net_mm': round(c_n, 2)},
       'results': R, 'weld': weld, 'bolt': {'mis': bolt_mis, 'run': bolt_run}, 'tip_defl_from_leg_mis_mm': defl}
json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-03_fix2_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
for r in R:
    print(r['case'], r['part'], r['sigma_vm_MPa'], 'SF', r['sf'], 'OK' if r['ok'] else ('BREAK' if r['motion_break'] else 'NEAR'))
print('weld', weld)
print('tip defl mis', defl)
print('bolt mis', bolt_mis)
print('bolt run', bolt_run)
