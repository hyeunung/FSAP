# -*- coding: utf-8 -*-
"""M04R 해석부 손계산 — U2 볼 테이블 사진대로(C-31), v2.4.0. FEA 환경 없음(D-16) -> 손계산만.
바뀐 것(mech_M04R_model.md 요약): 볼 2,596 -> 827(피치 100 반 칸 격자 B), 센터판 P_M04_INSERT 지움,
패널 6장 볼 구멍 O36 피치 100으로 다시(E2 X -410~975, 원판 구멍 r130, 아랫유닛 구멍),
가로대 HFS8-4080-560 x3(CM1 판 받침, CM_A·CM_B 원판 받침), 받침판 SUS304 t4 x2, CB5-20 x4, HBLFSN8 x6 + CB8-16 x12.
판정 M-09(요구서 6-1 비어 기본값): 운전 SF 3, 오조작 SF 2, 조임 SF 1. SF < 1.2만 동작.
완료 판정: 볼 하나 하중(D-92 임시 누름) SF >= 2.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
out = {'assumptions': {}}
A = out['assumptions']

# 0) 새 하중 부품 STEP bbox (면 선택용 확인, 옛 좌표 재사용 금지)
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
bbs = {}
for n in ['P_M04R_DB_SHIM_A', 'P_M04R_DB_SHIM_B', 'P_M04_PANEL_E2', 'P_M04_PANEL_W2', 'HFS8-4080-560_M04']:
    t = open(f'{ROOT}/tools/out/mech_M04R/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    bbs[n] = {'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)]}
out['step_bbox'] = bbs

# 1) 볼 하나 하중
balls = json.load(open(f'{ROOT}/tools/out/mech_M04R/design/balls_B827.json', encoding='utf-8'))['pts']
RATING = 200.0          # N, D-96 임시(미스미 볼롤러 압입형 표 약 200 N, catalog.md) - 형번 미확인
PITCH = 100.0
MAT_PA = 40.9           # Pa, 매트 면하중(M04 1회차 models.json P_M04_PANEL_W2와 같음)
A['ball_rating_N'] = 'D-96 임시 200 (형번 미확인)'
# U5 바퀴 길: 띠 P_DC205_STRIP X -1826~-391, Y +-25. 바퀴 폭 25(Y +-12.5). 볼 구 r 12.7
strip_hits = [p for p in balls if -1826 - 12.7 <= p[0] <= -391 + 12.7 and abs(p[1]) < 12.5 + 12.7]
# U4 바퀴는 원판(r125) 위. 원판 구멍 r130 안 볼 수
disk_hits = [p for p in balls if math.hypot(p[0] + 175, p[1]) < 130 + 12.7]
mat_one = MAT_PA * 1e-6 * PITCH * PITCH * 3   # 3 g
D92_MAX = 100.0     # N, D-92 바퀴 누름 최대 임시(바늘 옆 30~100, 먼 쪽 20~100)
HAND = 100.0        # N, 작업자 손 오조작(M04 완료 판정 기준과 같음)
cases = {
    '매트 자중 x3 g (운전)': {'F': mat_one, 'sf_min': 3.0},
    'D-92 누름 최대 100 N이 볼 하나에 (바퀴가 띠·원판을 벗어난 가정, 오조작)': {'F': D92_MAX + mat_one, 'sf_min': 2.0},
    '작업자 손 100 N 볼 하나에 몰림 (오조작)': {'F': HAND + mat_one, 'sf_min': 2.0},
}
for k, v in cases.items():
    v['F'] = round(v['F'], 3)
    v['sf'] = round(RATING / v['F'], 2)
    v['ok'] = v['sf'] >= v['sf_min']
    v['near'] = v['sf_min'] <= v['sf'] < 1.1 * v['sf_min']
out['ball_single'] = {'count': len(balls), 'balls_under_U5_wheel_path': len(strip_hits), 'balls_in_disk_hole': len(disk_hits),
                      'rating_N': RATING, 'cases': cases,
                      'need_rating_for_sf2_N': round(2 * (HAND + mat_one), 1),
                      'note': '실제 바퀴 누름(U4 원판, U5 띠)은 볼 몫 0 — 바퀴 길에 볼 0개. 판정은 손·D-92 100 N 몰림 오조작 SF 2'}

# 2) 패널 SUS304 t4 타공 O36 피치 100 (리거먼트 효율 0.64)
T = 4.0; NU = 0.3; E = 193000.0; SY = 205.0
D_H = 36.0
KLIG = PITCH / (PITCH - D_H)      # 응력 집중(공칭 x p/(p-d)), 1회차 같은 식
EST = 0.5                         # E*/E 임시(리거먼트 0.64, ASME 정사각 배열 표 근사 약 0.55 -> 보수 0.5)
A['panel_lig'] = f'p/(p-d) {KLIG:.4f}, E*/E {EST} (보수)'
R0 = 22.0   # 볼 테 O44가 하중을 줌
def roark_1d(W, b, beta, alpha):
    s = 3 * W / (2 * math.pi * T ** 2) * ((1 + NU) * math.log(2 * b / (math.pi * R0)) + beta)
    y = alpha * W * b ** 2 / (E * EST * T ** 3)
    return s * KLIG, y
pan = {}
# 2a) E2 가운데 칸: 센터판 자리였던 X -45(원판 구멍 끝)/45(아랫유닛 구멍)~545(레일 +-100 시작), 레일 Y +-300만 받침 -> 긴 판 경간 600(a/b ~1, 보수로 긴 판 beta 1.0 alpha 0.1851)
for nm, W, smin in [('손 100 N (오조작)', HAND, 2.0)]:
    s, y = roark_1d(W, 600.0, 1.000, 0.1851)
    pan['E2 가운데 칸 X 45~545 경간 600 ' + nm] = {'sigma_MPa': round(s, 2), 'sf': round(SY / s, 2), 'sf_min': smin, 'deflection_mm': round(y, 3)}
# 2b) E2 원판 구멍 가장자리(Y +-130)에서 레일 Y +-300까지 외팔 170, 유효 폭 2L 340 (보수, 옆 판 이어짐 무시)
L = 170.0; B = 2 * L
I = B * T ** 3 / 12
M = HAND * L
s = M * (T / 2) / I * KLIG
y = HAND * L ** 3 / (3 * E * EST * I)
pan['E2 원판 구멍 가장자리 외팔 170 손 100 N (오조작)'] = {'sigma_MPa': round(s, 2), 'sf': round(SY / s, 2), 'sf_min': 2.0, 'deflection_mm': round(y, 3)}
# 2c) W2 바퀴 길: 띠가 바퀴 누름을 받아 보스 8자리 + 판 위 띠 면으로 판에 퍼짐(DC2-05 결과 그대로) — 볼 구멍만 피치 100으로 바뀜.
#     띠 밖 볼 하나 손 100 N: 레일 Y +-100 사이 맑은 경간 160 긴 판(1회차 판정 B 모델)
s, y = roark_1d(HAND, 160.0, 1.000, 0.1851)
pan['W2 레일 +-100 사이 경간 160 손 100 N (오조작)'] = {'sigma_MPa': round(s, 2), 'sf': round(SY / s, 2), 'sf_min': 2.0, 'deflection_mm': round(y, 3)}
# 2d) 자중: E2 21.3 kg x 3 g 면하중, 경간 600 띠 단순보(폭 1 mm)
q = (21.3 * G * 3) / (1385 * 600) + MAT_PA * 3e-6     # N/mm2
Mq = q * 600 ** 2 / 8
s = Mq * 6 / T ** 2 * KLIG
y = 5 * q * 600 ** 4 / (384 * E * EST * T ** 3 / 12)
pan['E2 자중+매트 x3 g 경간 600 (운전)'] = {'sigma_MPa': round(s, 2), 'sf': round(SY / s, 2), 'sf_min': 3.0, 'deflection_mm': round(y, 3),
                                         'note': '보 단순지지(판 2방향·막 효과 무시, 보수). 1 g 처짐은 1/3'}
# 2e) 같은 칸 2방향 판(Roark 표 11.4 1a 네 변 단순지지 등분포, b 500 = X 45~545, a 600, a/b 1.2 alpha 0.0626), 1 g — 볼 꼭대기 높이용
q1 = (21.3 * G) / (1385 * 600) + MAT_PA * 1e-6
y2 = 0.0626 * q1 * 500 ** 4 / (E * EST * T ** 3)
pan['E2 가운데 칸 2방향 판 자중 1 g 처짐 (높이 사슬)'] = {'sigma_MPa': 0.0, 'sf': 999.0, 'sf_min': 3.0, 'deflection_mm': round(y2, 3), 'note': '볼 꼭대기가 원판 윗면보다 이만큼 낮아짐(높이 공차 비교용)'}
for v in pan.values():
    v['ok'] = v['sf'] >= v['sf_min']; v['near'] = v['sf_min'] <= v['sf'] < 1.1 * v['sf_min']
out['panels'] = pan

# 3) 가로대 HFS8-4080-560 (A6063-T5 항복 145, E 69 GPa). I 하한 1.5e5 mm4(설계부, 단면 표 미확인)
EA = 69000.0; SYA = 145.0; IX = 1.5e5; C = 40.0; LS = 560.0
A['hfs8_4080_I'] = 'I 하한 1.5e5 mm4 (설계부 값, 카탈로그 미확인 — 실제는 더 큼)'
cm = {}
# CM_A/CM_B: 원판 묶음 61 N x3 g + 누름 오조작 453.3 N(U5 값, U4 190.9 N보다 큼 — 보수) -> 볼트 자리 Y +-120 두 점
DISK_W = 61.0 * 3
PRESS = 453.3
P = (DISK_W + PRESS) / 2 / 2          # 가로대 2개 x 두 점
a = LS / 2 - 120
Mc = P * a
s = Mc * C / IX
y = P * a * (3 * LS ** 2 - 4 * a ** 2) / (24 * EA * IX)
cm['CM_A·CM_B 원판 받침 (오조작)'] = {'P_each_N': round(P, 1), 'M_Nm': round(Mc / 1000, 2), 'sigma_MPa': round(s, 2), 'sf': round(SYA / s, 2), 'sf_min': 2.0, 'deflection_mm': round(y, 4)}
# CM1: 판 받침. 보수로 E2 전부 + W2 1/4 (21.3 + 7.5 kg) x3 g 등분포 + 손 100 N 가운데
w_tot = (21.3 + 7.5) * G * 3
Mw = w_tot * LS / 8 + HAND * LS / 4
s = Mw * C / IX
y = 5 * w_tot * LS ** 3 / (384 * EA * IX) + HAND * LS ** 3 / (48 * EA * IX)
cm['CM1 판 받침 자중 x3 g + 손 100 N (오조작)'] = {'W_N': round(w_tot, 1), 'M_Nm': round(Mw / 1000, 2), 'sigma_MPa': round(s, 2), 'sf': round(SYA / s, 2), 'sf_min': 2.0, 'deflection_mm': round(y, 4)}
for v in cm.values():
    v['ok'] = v['sf'] >= v['sf_min']; v['over_spec'] = v['sf'] > 5 * v['sf_min']
out['cross_members'] = cm

# 4) 받침판 SUS304 t4 (가로대 윗면 폭 40 위 전면 지지, DISK_BASE와 사이 압축만)
F_sh = (DISK_W + PRESS) / 2
area = 40 * 40 * 2   # DISK_BASE와 닿는 곳: 볼트 자리 두 곳 둘레 40x40 (보수 — 실제는 40 x 270 대부분)
p = F_sh / area
out['shim'] = {'F_N': round(F_sh, 1), 'contact_mm2_min': area, 'bearing_MPa': round(p, 3), 'sf_vs_pG400': round(400 / p, 1),
               'note': '전면 받침이라 굽힘 없음(얇은 판이지만 보 아님 — 경간 0). 압축만'}

# 5) 체결 (조임 토크 시방 없음 임시: M5 4 N·m, M8 10 N·m — M04 3회차와 같음)
bolts = {}
# CB5-20 x4: DISK_BASE -> 받침판 -> HNTT8-5(가로대 윗홈). 외력: 오조작 접선 95.5 N(mech_M02) 마찰 / 4 + 위로 뜨는 힘 없음(누름은 아래)
bolts['CB5-20 x4 (DISK_BASE, 접선 오조작 95.5 N/4 축 환산 보수)'] = calc(5, 5.5, 95.5 / 4, torque=4.0, bolt='12.9', base='SS400', sf_min=2.0)
# 미끄럼: 예압 4 N·m/(0.2x5)=4000 N x 4 x mu 0.15 vs 95.5
fv5 = 4.0 * 1000 / (0.2 * 5)
bolts['CB5-20 미끄럼'] = {'friction_N': round(fv5 * 4 * 0.15, 1), 'tangential_N': 95.5, 'sf': round(fv5 * 4 * 0.15 / 95.5, 1)}
# CB8-16 x12: 브래킷 하나 = 가로대 끝 반력. CM1 반력이 가장 큼
R_cm1 = (w_tot + HAND) / 2
bolts['CB8-16 (HBLFSN8, CM1 끝 반력 축 환산 보수)'] = calc(8, 5.3, R_cm1, torque=10.0, bolt='12.9', base='SS400', sf_min=2.0)
fv8 = 10.0 * 1000 / (0.2 * 8)
bolts['CB8-16 미끄럼 (브래킷 다리 하나 1개, 반력 전부)'] = {'friction_N': round(fv8 * 0.15, 1), 'shear_N': round(R_cm1, 1), 'sf': round(fv8 * 0.15 / R_cm1, 2)}
A['nut_material'] = 'HNTT8 T너트 강(SS400 근사), 물림 5.5(M5)·5.3(M8) 모델링부 값'
A['torque'] = 'M5 4 N·m, M8 10 N·m 임시(시방 없음)'
out['bolts'] = bolts

json.dump(out, open(f'{ROOT}/fea/results/mech_M04R_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 15줄 요약
print('balls', len(balls), 'under U5 path', len(strip_hits), 'in disk hole', len(disk_hits))
for k, v in cases.items(): print(' ball', k[:30], v['F'], 'SF', v['sf'])
for k, v in pan.items(): print(' pan', k[:34], v['sigma_MPa'], 'SF', v['sf'], 'y', v['deflection_mm'])
for k, v in cm.items(): print(' cm', k[:20], v['sigma_MPa'], 'SF', v['sf'], 'y', v['deflection_mm'])
print(' shim', out['shim']['bearing_MPa'])
for k, v in bolts.items(): print(' bolt', k[:24], v.get('worst', ''), v.get('sf_operating', v.get('sf')), v.get('sf_tightening', ''), v.get('ok', ''))
print(' bbox', {k: (v['min'], v['max']) for k, v in bbs.items()})
