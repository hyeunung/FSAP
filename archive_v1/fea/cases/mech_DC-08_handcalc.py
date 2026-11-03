# -*- coding: utf-8 -*-
"""DC-08 해석부 손계산 — P_N04_INLET(PA12 3D 출력 플랜지 니플, v1.0.18). FEA 환경 없음(D-16).
형상(임시 STEP tools/out/mech_DC-08/stepout/P_N04_INLET.step, mech_DC-08_model.md 2절, 월드 mm REST):
  축 (-1185, 1143) Z. 니플 Ø38/Ø34 Z -85~-45(외팔 40, 끝 C1), 플랜지 Ø70 t5 Z -45~-40, 끼움 턱 Ø46 Z -40~-39(판 구멍 Ø46).
  고정: 플랜지 윗면 Z -40 링(Ø70 - Ø46, 2,187 mm²)이 판 밑 표피에 에폭시 접착. 끼움 턱이 옆 힘을 판 구멍 벽(표피 t1)에 기댐.
하중(출처):
  호스(ID38/OD46, 형번 미정 D-89): 0.5 m x 0.3 kg/m(덕트 호스 일반값, 임시) = 0.15 kg.
  호스 R150 굽힘 반력 F_bend: 형번 미정 -> 임시 20 N(덕트 호스 일반, 이 부서 가정) 니플 끝.
  INLET·호스·베어 움직이는 끝이 모두 U4_X와 함께 움직임(model 2절) -> 호스 상대 굽힘 운동 없음, 가속은 자중 x3 g에 포함.
  내압: 블로어 15 kPa(D-89 임시, 구멍 막힘 최대 정압) -> 떼는 힘 p x pi/4 x 31^2(model 11.3 N) 대신 보수로 Ø46 끼움 지름 전체.
  오조작: 손으로 호스 당김 100 N(M-09 기본 손 하중) 니플 끝 옆 + 같은 100 N 축 방향(따로), 자중 x1 g.
판정: 운전 SF 3, 오조작 SF 2(요구서 6-1, M-09 기본값), SF < 1.2 영구 변형.
재질(임시, E-12): PA12(SLS) 인장 항복 45 MPa(선정과 같음). 에폭시-PA12 접착 전단·박리 2 MPa(낮은 표면 에너지, 표면 처리 없는 보수값; 선정 5 MPa 대신).
"""
import json, math, re

G = 9.81
SY_PA12 = 45.0
S_BOND = 2.0
SFMIN = {'run': 3.0, 'mis': 2.0}
STEP = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_DC-08/stepout/P_N04_INLET.step'

# STEP bbox 확인(면 선택용 좌표를 옛 케이스에서 가져오지 않는다)
txt = open(STEP, encoding='utf-8', errors='ignore').read()
pts = [tuple(float(v) for v in m.split(',')) for m in re.findall(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", txt)]
pts = [q for q in pts if abs(q[0]) > 1 and abs(q[1]) > 1]   # 축 놓임 원점 (0,0,0) 등은 빼고 형상 점만
xs, ys, zs = zip(*pts)
bbox = [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)]

D, d, L = 38.0, 34.0, 40.0          # 니플
A_n = math.pi / 4 * (D**2 - d**2)
W_n = math.pi * (D**4 - d**4) / (32 * D)
Do, Di, tf = 70.0, 46.0, 5.0         # 접착 링
A_b = math.pi / 4 * (Do**2 - Di**2)
W_b = math.pi * (Do**4 - Di**4) / (32 * Do)
m_hose = 0.15
p = 0.015                            # MPa
F_press = p * math.pi / 4 * Di**2   # 보수

cases = {}
def case(name, kind, F_side, F_ax):
    M_n = F_side * L
    s_n = M_n / W_n + F_ax / A_n
    hoop = p * (d / 2) / ((D - d) / 2)
    M_b = F_side * (L + tf)
    s_b = M_b / W_b + F_ax / A_b      # 링 바깥 끝 박리(보수: 끼움 턱 기댐 무시)
    tau_b = F_side / A_b
    # 플랜지 t5 링 판: 니플 뿌리 r19 -> 접착 안쪽 r23 사이 짧은 띠(4)에 축력이 걸림, 전단으로 봄
    tau_f = F_ax / (math.pi * D * tf)
    sf_n = SY_PA12 / max(s_n, hoop)
    sf_b = S_BOND / math.hypot(s_b, tau_b)
    sf_f = (SY_PA12 / math.sqrt(3)) / tau_f if tau_f > 0 else None
    cases[name] = {
        'kind': kind, 'F_side_N': round(F_side, 2), 'F_axial_N': round(F_ax, 2),
        'nipple_sigma_MPa': round(s_n, 3), 'hoop_MPa': round(hoop, 3), 'SF_nipple': round(sf_n, 1),
        'bond_peel_MPa': round(s_b, 3), 'bond_shear_MPa': round(tau_b, 4), 'SF_bond': round(sf_b, 1),
        'flange_shear_MPa': round(tau_f, 3), 'SF_flange': round(sf_f, 1) if sf_f else None,
        'SF_min_req': SFMIN[kind],
        'ok': min(sf_n, sf_b, sf_f or 1e9) >= SFMIN[kind],
    }

w3 = m_hose * G * 3
case('run_side', 'run', 20.0 + w3, F_press + w3)
case('mis_side', 'mis', 100.0 + m_hose * G, F_press)
case('mis_axial', 'mis', 20.0, 100.0 + F_press + m_hose * G)

# 판 P_N04_PANEL: 밑 표피 Ø46 구멍만 (-1023,1040) -> (-1185,1143) 이동, 부피 변화 0.
# 기둥 바깥 면 X -1050에서 -X 외팔. 새 구멍은 뿌리에서 135 바깥(굽힘 모멘트 ∝ (L-x)^2, 외팔 끝 X -2010: L 960)
L_cant = 2010 - 1050
x_new = 1185 - 1050
ratio_M = ((L_cant - x_new) / L_cant) ** 2
S_ROOT = {'run': 9.6, 'mis': 17.2}   # mech_N04_fea.md 4절 PANEL ±X 외팔 뿌리 표피(구멍 없음)
SY_SKIN = 175.0
KT = 3.0                              # 넓은 판 원 구멍
panel = {'change': '밑 표피 Ø46 구멍 위치만, 하중 경로·두께·재질 그대로(부피 변화 0)',
         'cantilever_L_mm': L_cant, 'hole_from_root_mm': x_new,
         'moment_ratio_at_hole_vs_root': round(ratio_M, 3)}
for k in ('run', 'mis'):
    s_h = S_ROOT[k] * ratio_M * KT
    panel[k] = {'skin_at_hole_MPa': round(s_h, 1), 'SF': round(SY_SKIN / s_h, 1), 'SF_min_req': SFMIN[k], 'ok': SY_SKIN / s_h >= SFMIN[k]}

out = {'model': 'mech_DC-08 handcalc v1.0.18', 'fea': '해석 못 함 — 환경 없음(D-16)',
       'step_bbox': bbox, 'nipple': {'A': round(A_n, 1), 'W': round(W_n, 1)},
       'bond': {'A': round(A_b, 1), 'W': round(W_b, 1)}, 'F_press_N': round(F_press, 2),
       'cases': cases, 'panel': panel}
json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-08_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
