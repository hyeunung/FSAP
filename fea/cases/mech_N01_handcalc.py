# -*- coding: utf-8 -*-
"""N01 해석부 손계산 — P_N01_FOOT (S45C, v1.0.2). FEA 환경 없음(D-16).
형상(STEP tools/out/mech_N01/stepout/P_N01_FOOT.step bbox X -10~3, Y -8~6):
  발바닥 t2 (Z 12~14, 값 0), 바늘 구멍 Ø3 (0,0), 노루발대 Ø6 축 (-5,-3) Z 14~80, 노즈 구멍 Ø7 밑면 Z 46.
하중(임시값):
  누름 50 N (D-10 자리값, v0.x T02~T04와 같음) / 끌림 운전 30 N (= 마찰 상한 mu 0.6 x 50 N)
  오조작: 누름 150 N (3배, 노루발이 두꺼운 이음매·이물에 걸림), 끌림 100 N (D-79 봉제 끌림 전부가 노루발에)
  자중 x3 g: 17.39 g x 3 x 9.81 = 0.51 N (무시 수준, 더해 둠)
판정: M-09 운전 SF 3, 오조작 SF 2 (요구서 6-1 기본값). 처짐은 바늘↔노루발 틈 0.7(모델 실측)보다 작아야 동작.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

E, RP = 205000.0, 345.0       # S45C 비조질(JIS G4051 항복 하한 약 345 MPa)
W = 17.39e-3 * 9.81 * 3       # 자중 3 g
out = {}

# 1) 발바닥 t2 외팔 — 노루발대 가장자리(r 3)에서 가장 먼 모서리 (3,6)까지 sqrt(8^2+9^2)-3 = 9.04
L_tip = math.hypot(3 + 5, 6 + 3) - 3.0
cases = {
    'sole_run_selectbasis_b13_L12': dict(t=2, b=13, length=12, load=50 + W, sf_min=3),   # 선정 N01-D4 식 재현
    'sole_run_b6_Ltip': dict(t=2, b=6, length=round(L_tip, 2), load=50 + W, sf_min=3),     # 끝 집중, 폭 = 대 지름(보수)
    'sole_mis_b6_Ltip': dict(t=2, b=6, length=round(L_tip, 2), load=150 + W, sf_min=2),
    # 뿌리 유효폭 = 대 반둘레 pi*r = 9.42 (끝 하중이 대 바깥 반둘레로 퍼짐, 보수 하한과 판 실제 사이)
    'sole_run_bhalfper_Ltip': dict(t=2, b=round(math.pi * 3, 2), length=round(L_tip, 2), load=50 + W, sf_min=3),
    'sole_mis_bhalfper_Ltip': dict(t=2, b=round(math.pi * 3, 2), length=round(L_tip, 2), load=150 + W, sf_min=2),
    # 고치는 안: 발바닥 t3 (끝 집중 폭 6 보수식)
    'fix_t3_mis_b6_Ltip': dict(t=3, b=6, length=round(L_tip, 2), load=150 + W, sf_min=2),
}
for k, c in cases.items():
    out[k] = beam(e=E, sy=RP, **c)

# 2) 노루발대 Ø6 원형 외팔 — 노즈 밑면 Z 46 → 발바닥 가운데 Z 13 (레버 33, 노루발 내림 값 0이 최악)
d, lev = 6.0, 46.0 - 13.0
I = math.pi * d ** 4 / 64; Zs = math.pi * d ** 3 / 32
for k, f, sfm in [('bar_drag_run', 30.0, 3), ('bar_drag_mis', 100.0, 2)]:
    m = f * lev; s = m / Zs; dfl = f * lev ** 3 / (3 * E * I)
    out[k] = {'F_N': f, 'lever_mm': lev, 'stress_MPa': round(s, 1), 'sf': round(RP / s, 2), 'sf_min': sfm,
              'ok': RP / s >= sfm, 'near_10pct': sfm <= RP / s < 1.1 * sfm, 'deflection_mm': round(dfl, 3),
              'gap_needle_foot_mm': 0.7, 'motion_ok': dfl < 0.7}
# 3) 대 좌굴(오조작 누름 150 N, 노즈 구멍에서 위 끝까지 안내, 아래 자유 — 외팔 K=2, 길이 33)
Pcr = math.pi ** 2 * E * I / (2 * lev) ** 2
out['bar_buckle_mis'] = {'Pcr_N': round(Pcr), 'F_N': 150, 'sf': round(Pcr / 150, 1)}
# 4) 대-발바닥 뿌리 전단(오조작 끌림 100 N, Ø6 단면)
out['bar_root_shear_mis'] = {'tau_MPa': round(100 / (math.pi * 9), 2), 'sf': round(0.577 * RP / (100 / (math.pi * 9)), 1)}
# 과사양(M-09: 필요치 3배 이상)
out['oversize_note'] = {k: v['sf'] for k, v in out.items() if isinstance(v, dict) and 'sf' in v and v['sf'] >= 3 * v.get('inputs', v).get('sf_min', 3)}

p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_N01_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    if isinstance(v, dict) and 'sf' in v:
        print(k, 'sigma/tau', v.get('stress_MPa', v.get('tau_MPa', '')), 'SF', v['sf'], 'defl', v.get('deflection_mm', ''))
print('oversize', out['oversize_note'])
