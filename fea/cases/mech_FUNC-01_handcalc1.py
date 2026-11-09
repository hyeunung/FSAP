# -*- coding: utf-8 -*-
"""FUNC-01 해석부 수정 1회차 손계산 — v2.8.1 옆판 P_M03_LIFT_SIDE_N/P 축 여유 구멍 Ø16.5(Z 115~130) 뒤 웨브 재계산.
FEA 환경 없음(D-16) -> 손계산. 하중·경계는 mech_FUNC-01_handcalc.py(v2.8.0)와 같다(fea/models.json, 모델 안 바꿈).
바뀐 것: 웨브(t6, 바깥면이 축에서 6) 수평 단면에서 축 줄(X -1847) 가운데 활꼴(반지름 8.25, 깊이 2.25)이 빠짐 -> 남은 3.75.
단면: 유효 폭 60(옛 식과 같음) 안에서 X 방향 띠마다 두께 t(x), 판 굽힘(같은 곡률)으로 I = sum dx t^3/12, sigma_max = M (t_max/2) / I.
STEP(tools/out/mech_FUNC-01/stepout, v2.8.1 내보냄 11:06)에 r 8.25 원통면이 있는지 다시 확인한다.
"""
import json, math, re, sys

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
base = json.load(open(f'{ROOT}/fea/results/mech_FUNC-01_handcalc.json', encoding='utf-8'))
out = {'base_results': 'fea/results/mech_FUNC-01_handcalc.json (v2.8.0, 하중·경계 같음)'}

cyl = re.compile(r"CYLINDRICAL_SURFACE\('[^']*',#\d+,([-\d.Ee+]+)\)")
out['step_radii'] = {}
for n in ('P_M03_LIFT_SIDE_N', 'P_M03_LIFT_SIDE_P'):
    t = open(f'{ROOT}/tools/out/mech_FUNC-01/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    out['step_radii'][n] = sorted({round(float(r), 2) for r in cyl.findall(t)})
    assert 8.25 in out['step_radii'][n], n + ' 여유 구멍 r 8.25 없음'

T, RH, D_AX, B = 6.0, 8.25, 6.0, 60.0          # 웨브 두께, 구멍 반지름, 축 중심 -> 웨브 안쪽면, 유효 폭
cut_depth = RH - D_AX                           # 2.25
chord = 2 * math.sqrt(RH ** 2 - D_AX ** 2)      # 11.32
n = 6000; dx = B / n
I = A = 0.0; tmin = T
for i in range(n):
    x = -B / 2 + (i + 0.5) * dx
    c = max(0.0, math.sqrt(max(RH ** 2 - x ** 2, 0.0)) - D_AX) if abs(x) < RH else 0.0
    t = T - c; tmin = min(tmin, t)
    I += dx * t ** 3 / 12; A += dx * t
I0, A0 = B * T ** 3 / 12, B * T
out['section'] = {'cut_depth': round(cut_depth, 2), 'chord_X': round(chord, 2), 't_min': round(tmin, 2),
                  'I_ratio': round(I / I0, 3), 'A_ratio': round(A / A0, 3)}

H_R = 96.0                                       # 접점 Z 40 -> 축 뿌리 Z 136 (옛 식 h_r)
res = {}
for cn, r in base['results'].items():
    if cn == '들기':
        continue
    Fy = base['loads']['cases'][cn]['Fy']
    V_s = r['shaft']['V_N']
    Mx = Fy * H_R / 2                            # 두 옆판 나눔(옛 식과 같음)
    s_old = Mx / (B * T ** 2 / 6) + V_s / (B * T)
    s_new = Mx * (T / 2) / I + V_s / A
    # 홈 바닥(얇은 띠) 응력: 같은 곡률이면 t에 비례 — 정적 연성재라 Kt 넣지 않음(피로 기록용 Kt 약 1.5 곱한 값도 남김)
    s_thin = Mx * (tmin / 2) / I + V_s / A
    s_fl = r['LIFT_SIDE']['sigma_flange']        # 플랜지(Z 130~136) 형상 안 바뀜
    sf = round(205 / max(s_new, s_fl), 2) if max(s_new, s_fl) > 0 else 999.0
    req = 3.0 if cn.startswith('운전') else (2.0 if cn.startswith('오조작') else None)
    res[cn] = {'Fy': Fy, 'sigma_web_v280': round(s_old, 1), 'sigma_web_v281': round(s_new, 1),
               'sigma_groove_bottom': round(s_thin, 1), 'sigma_groove_x_Kt1.5(기록)': round(1.5 * s_thin, 1),
               'sigma_flange': s_fl, 'SF_v280': r['LIFT_SIDE']['SF'], 'SF_v281': sf, 'req': req,
               'ok': req is None or sf >= req, 'near(+10%)': req is not None and req <= sf < 1.1 * req}
out['LIFT_SIDE'] = res
json.dump(out, open(f'{ROOT}/fea/results/mech_FUNC-01_handcalc1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('section', out['section'])
for k, v in res.items():
    print(k, 'web', v['sigma_web_v280'], '->', v['sigma_web_v281'], 'SF', v['SF_v280'], '->', v['SF_v281'], 'req', v['req'], 'ok', v['ok'])
