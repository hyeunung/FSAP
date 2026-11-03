# -*- coding: utf-8 -*-
"""M04 해석부 손계산 — U2 볼 테이블(v2.1.3). FEA 환경 없음(D-16) -> 손계산만.
형상: tools/out/mech_M04/stepout/*.step 꼭짓점 bbox(면 선택 대신 bbox로 치수 확인) + mech_M04_design.md 2절 치수.
하중(지시서): 작업 저항 = 바퀴 누름(M03 U5 운전 238.6 N / 오조작 453.3 N, M02 U4 운전 153.8 N / 오조작 190.9 N),
              매트 무게 40.9 Pa(design_check), 자중 x3 g. 완료 판정 3항 '판 처짐(매트 + 바퀴 누름 100 N)'은 따로 기록.
판정 M-09: 운전 SF 3, 오조작 SF 2. SF < 1.2(부러짐·영구 변형)만 동작.
평판식(Roark 7판 표 11.4):
  1d 네 변 단순지지, 가운데 작은 원 r0 하중: sigma = 3W/(2 pi t^2) [(1+nu) ln(2b/(pi r0')) + beta], y = alpha W b^2/(E t^3)
     b/a -> long plate(a/b >= 3): beta 1.000, alpha 0.1851. 정사각(a/b 1): beta 0.435, alpha 0.1267(설계안 design_check가 쓴 값)
  r0' = sqrt(1.6 r0^2 + t^2) - 0.675 t (r0 < 0.5 t일 때만), 아니면 r0
타공: 정사각 피치 p 50, 구멍 d 36 -> 리거먼트 eta = (p-d)/p = 0.28. 굽힘 유효 E*/E 0.20(측정부 가정, 설계안과 같음),
      리거먼트 응력 = 공칭 x p/(p-d)(ASME VIII-2 5.E 방식 간이).
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
out = {}
SY = {'SUS304': 205.0, 'A5052': 195.0, 'A6063-T5': 145.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0, 'A6063-T5': 69000.0}
SF_REQ = {'운전': 3.0, '오조작': 2.0}
NU = 0.3

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
names = ['P_M04_INSERT', 'P_M04_PANEL_W1', 'P_M04_PANEL_W2', 'P_M04_PANEL_W3', 'P_M04_PANEL_E1', 'P_M04_PANEL_E2', 'P_M04_PANEL_E3']
out['step_bbox'] = {}
for n in names:
    t = open(f'{ROOT}/tools/out/mech_M04/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)], 'max': [round(max(c), 2) for c in zip(*pts)],
                           'holes_d36_circles': len(re.findall(r"CIRCLE\('[^']*',#\d+,\s*18\.?0*\s*\)", t))}

# ---------- 1) 하중 ----------
t = 4.0; p = 50.0; dh = 36.0
eta = (p - dh) / p
kl = 1.0 / eta                        # 리거먼트 응력 계수 3.57
EF = 0.20
Es = E['SUS304'] * EF
solid = 1 - math.pi / 4 * dh ** 2 / p ** 2
q_plate = 7.93e-6 * t * solid * G     # N/mm2, 1 g
q_ball = 0.015 * G / p ** 2           # 볼 유닛 15 g/개 임시(D-96)
q_mat = 40.9e-6                       # design_check 매트 무게
q1 = q_plate + q_ball + q_mat
q3 = 3 * (q_plate + q_ball) + q_mat   # 자중 x3 g, 매트는 작업 하중(그대로)
out['area_load'] = {'q_plate_1g': q_plate, 'q_ball_1g': q_ball, 'q_mat': q_mat, 'q_1g_total': q1, 'q_3g_total': q3, 'eta': eta, 'k_lig': round(kl, 3)}
WHEEL_U5 = {'기준100N(완료판정)': 100.0, '운전': 238.6, '오조작': 453.3}   # mech_M03_handcalc.json cases N
WHEEL_U4 = {'운전': 153.8, '오조작': 190.9}                               # mech_M02 (원판 위)


def rr0(r0):
    return math.sqrt(1.6 * r0 * r0 + t * t) - 0.675 * t if r0 < 0.5 * t else r0


def plate_point(W, b, r0, beta=1.000, alpha=0.1851):
    s = 3 * W / (2 * math.pi * t * t) * ((1 + NU) * math.log(2 * b / (math.pi * rr0(r0))) + beta)
    y = alpha * W * b * b / (Es * t ** 3)
    return s, y


def strip_uniform(q, L):          # 한 방향 띠 단순지지, 폭 1 mm
    I = t ** 3 / 12
    return 6 * (q * L * L / 8) / t ** 2, 5 * q * L ** 4 / (384 * Es * I)


# ---------- 2) W2 먼 쪽 바퀴 길(볼 줄 Y 0, 레일 Y +-100) ----------
res = {}
variants = {'A 보수: 경간 200(레일 중심)·r0 18(구멍)': (200.0, 18.0), 'B 실형: 맑은 경간 160(레일 면)·r0 20(테 O44/O36 중간)': (160.0, 20.0)}
for vn, (b, r0) in variants.items():
    for cn, W in WHEEL_U5.items():
        s, y = plate_point(W, b, r0)
        su, yu = strip_uniform(q3 if cn != '기준100N(완료판정)' else q1, b)
        _, yu1 = strip_uniform(q1, b)
        sl = (s + su) * kl
        req = SF_REQ.get(cn, 3.0)
        res[f'{vn} | {cn}'] = {'W_N': W, 'sigma_nominal': round(s + su, 1), 'sigma_ligament': round(sl, 1), 'SF': round(SY['SUS304'] / sl, 2),
                               'SF_req': req, 'defl_point_mm': round(y, 3), 'defl_uniform_1g_mm': round(yu1, 3), 'defl_total_mm': round(y + yu1, 3)}
# 옛 모델(설계안 design_check: 정사각 alpha 0.1267, 균일하중 없음) 같은 형상으로
s_old, y_old = plate_point(100.0, 200.0, 18.0, beta=0.435, alpha=0.1267)
res['옛 모델(design_check, 정사각 판 가정) | 100 N'] = {'defl_point_mm': round(y_old, 3), 'sigma_nominal': round(s_old, 1),
                                                    'note': 'W2는 1795 x 600 판을 레일 +-100이 200 띠로 나눔 -> a/b ~ 9, 긴 판 계수가 맞다(새 모델)'}
out['W2_wheel_path'] = res

# 일반 경간 300(작업자 100 N 참고 — 바퀴는 지나지 않음)
s, y = plate_point(100.0, 300.0, 18.0)
su, yu = strip_uniform(q3, 300.0)
out['general_span300_100N_ref'] = {'sigma_ligament': round((s + su) * kl, 1), 'SF': round(205 / ((s + su) * kl), 2), 'defl_mm': round(y + strip_uniform(q1, 300)[1], 3)}
# E2 동쪽 혀(X 400~545, 레일 +-100 시작 X 545, 센터판 턱 X 105~125): 한 방향 띠 440 보수
su, yu = strip_uniform(q3, 440.0)
out['E2_strip440_selfweight'] = {'sigma_ligament_3g': round(su * kl, 1), 'SF': round(205 / (su * kl), 1), 'defl_1g_mm': round(strip_uniform(q1, 440)[1], 3),
                                 'note': '아랫유닛 칸 위, 바퀴 안 지나감. 설계안 0.10(정사각 판·매트만)보다 큼'}
# E2 포켓 가장자리 내밈 150(M04-X3), 작업자 100 N, 유효 폭 2 x 150
bm = beam(t, 300.0, 150.0, load=100.0, e=Es, sy=205.0, end='cantilever', sf_min=3.0)
out['E2_pocket_edge_worker100N'] = {'beam': bm, 'note': '가장자리 36 안에는 구멍 없음 -> 리거먼트 계수 안 씀. 기록만(M04-X3)'}

# ---------- 3) 볼 1개(D-96 임시 정격 100 N) ----------
RATING = 100.0
out['ball_single'] = {k: {'load_N': W, 'SF_vs_rating': round(RATING / W, 2)} for k, W in WHEEL_U5.items()}
out['ball_single']['_note'] = '바퀴 폭 25 < 피치 50 -> 바퀴 밑 볼 0~1개(design_check far_wheel_row_Y0 28개). 정격 100 N은 catalog.md 임시값(D-96)'
need = 1.2 * WHEEL_U5['오조작']
out['ball_single']['_rating_needed_N'] = {'운전 SF3 기준': round(3 * WHEEL_U5['운전'], 0), '오조작 SF 1.2(영구 변형 경계)': round(need, 0),
                                          '운전 정격 그대로(SF 1)': WHEEL_U5['운전']}

# ---------- 4) 센터판 P_M04_INSERT (A5052 t40, 레일 Y +-300에 얹힘, 원판 구멍 O270) ----------
m_ins = 24.0
m_disk = 5.0                  # 원판 1.56 kg + 하우징·베이스·베어링 임시(M02 STEP 질량 미집계)
L = 600.0
bnet = 525.0 - 270.0          # 원판 중심 X -175 단면(Y 방향 보, 폭은 X 방향)
I_ins = bnet * 40 ** 3 / 12
ins = {}
for cn, W in WHEEL_U4.items():
    P = W + (3 * m_disk * G)
    wq = 3 * m_ins * G / L
    M = P * L / 4 + wq * L * L / 8
    sg = M * 20 / I_ins
    req = SF_REQ[cn]
    ins[cn] = {'P_N': round(P, 1), 'M_Nmm': round(M, 0), 'sigma': round(sg, 2), 'SF': round(SY['A5052'] / sg, 1), 'SF_req': req,
               'defl_mm': round(P * L ** 3 / (48 * E['A5052'] * I_ins) + 5 * wq * L ** 4 / (384 * E['A5052'] * I_ins), 4)}
# 밑면 턱 t12 x 폭 525 전단(한쪽)
V = (WHEEL_U4['오조작'] + 3 * (m_disk + m_ins) * G) / 2
ins['ledge_shear_오조작'] = {'V_N': round(V, 1), 'tau': round(V / (525 * 12), 3), 'SF': round(0.577 * 195 / (V / (525 * 12)), 0)}
ins['_note'] = ('구멍 O270 단면을 보 폭 255로 본 보수식. 볼트(CB8-20) 없이 얹힘: 위로 드는 힘 없음, Y는 몸통(Y +-280)이 레일 안쪽 면에, '
                'X는 윗면 턱 단차(X -380·105)가 패널 끝에 걸림 -> 바퀴 접선 95.5 N(M02 오조작)은 맞닿음으로 받는다(마찰 0.2 x 426 N = 85 N에 기대지 않음)')
out['insert'] = ins

# DISK_BASE 매달림 M5 탭 4(A5052, 깊이 10) — 바퀴가 원판을 누르면 볼트 인장
Fb = (WHEEL_U4['오조작'] + 3 * m_disk * G) / 4
out['insert_tap_M5'] = {'per_bolt_오조작_N': round(Fb, 1),
                        'calc': calc(5, 10.0, Fb, torque=0.0, bolt='12.9', base='A5052', sf_min=2.0),
                        'note': '조임 토크 기록 없음 -> 조임 상태 점검 생략(체결 바뀐 것만 보는 체결부 몫). 물림 10 = 2d(M-01 1.5d 이상)'}

# ---------- 5) 받침 틀 HFS8-4080 레일·침목(A6063-T5 가정, I 강축 89.6e4 가정 = 설계안) ----------
I_r = 89.6e4; Z_r = I_r / 40
q_rail_self = 1120.6e-6 * 2.7e-3 * G * 3 / 1000 * 1000   # N/mm, 3 g (단면 1120.6 mm2)
q_rail_self = 1120.6 * 2.7e-6 * G * 3
trib = 200.0                                               # 레일 +-100 몫 폭(Y 0 ~ Y 200)
qr = trib * q3 + q_rail_self
rl = {}
for cn, W in {'운전': WHEEL_U5['운전'], '오조작': WHEEL_U5['오조작']}.items():
    P = W / 2                                              # 바퀴 Y 0 -> 레일 +-100 반씩
    Lr = 600.0
    M = P * Lr / 4 + qr * Lr * Lr / 8
    sg = M / Z_r
    rl[cn] = {'P_N': P, 'sigma': round(sg, 2), 'SF': round(SY['A6063-T5'] / sg, 1), 'defl_mm': round(P * Lr ** 3 / (48 * E['A6063-T5'] * I_r), 4)}
# 침목: 레벨러 간격 약 616(L3080 / 5칸, 임시), 가운데 레일 반력 + 레일 300 간격 고른 몫
Ls = 616.0
R_rail = qr * 600 + WHEEL_U5['오조작'] / 2
M_s = R_rail * Ls / 4 + (qr * 600 / 300) * Ls ** 2 / 8
rl['sleeper_오조작'] = {'R_rail_N': round(R_rail, 1), 'sigma': round(M_s / Z_r, 2), 'SF': round(SY['A6063-T5'] / (M_s / Z_r), 1)}
out['frame'] = rl

# 레벨러 M8 x 36(STEP대기, 정격 미정): 틀 전체 480 kg(설계안) x 3 g / 36 + 바퀴 오조작 한 곳에 전부(보수)
F_lev = 480 * G * 3 / 36 + WHEEL_U5['오조작']
out['leveler_M8'] = {'F_N': round(F_lev, 1), 'thread_compress_MPa': round(F_lev / 36.6, 1),
                     'tnut_calc': calc(8, 6.0, F_lev, torque=0.0, bolt='4.8', base='SS400', sf_min=2.0),
                     'note': 'HNTT8-8 나사 길이 6 가정(1.5d 미만 -> 너트 + 고정 너트로 받는 구조, 기록). 레벨러 정격은 STEP대기·형번 미정'}

# ---------- 6) 요약 ----------
w2 = out['W2_wheel_path']
out['summary'] = {
    '완료판정3_처짐(매트+바퀴100N)': {k: v['defl_total_mm'] for k, v in w2.items() if '100N' in k},
    'W2_운전_SF': {k: v['SF'] for k, v in w2.items() if '운전' in k},
    'W2_오조작_SF': {k: v['SF'] for k, v in w2.items() if '오조작' in k},
    'ball_SF_운전': out['ball_single']['운전']['SF_vs_rating'], 'ball_SF_오조작': out['ball_single']['오조작']['SF_vs_rating'],
    'insert_SF_오조작': out['insert']['오조작']['SF'], 'rail_SF_오조작': out['frame']['오조작']['SF'],
}
json.dump(out, open(f'{ROOT}/fea/results/mech_M04_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out['summary'], ensure_ascii=False, indent=1))
for n, v in out['step_bbox'].items():
    print(n, v['min'], v['max'], 'circles r18:', v['holes_d36_circles'])
