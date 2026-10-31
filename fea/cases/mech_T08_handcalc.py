# -*- coding: utf-8 -*-
"""T08 매트 이송 X 통판(P_T08_XPLATE_F/_B, A5052 t14) + X 블록·체결 손계산 (해석부, 2026-11-01, 대상 v0.6.11).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 + 엔진 handcalc(읽기만).
판은 t/L = 14/22(외팔 길이) = 0.64 → 얇은 판이 아니다. 고체 FEA 대상이지만 환경이 없어 보 + 단면 손계산으로 대신한다.
입력 형상: 모델링부 임시 STEP 2개(tools/out/mech_T08/stepout/*.step, 대기 세계 좌표). 판 bbox·두께는 STEP VERTEX에서 읽는다.
블록 위치(X ±150~210, Y −1021~−979 / 159~201, 윗면 Z −572)·460 위치(Y −977~−937 / 203~243)는 mech_T08_model.md 1절 CAD bbox.

하중 경로(실제 조립 경계조건, models.json에 새로 더함):
  Y 이동 묶음(MAT_Y·MAT_ROT·RING1·RING2·MAT_LARGE 96.07 kg, 무게중심 Y ≈ J_MAT_Y) → 1300 형재 2개(460_F·_B 위에 얹힘, 교차부 체결 없음 T08-S05)
  → 단순보 반력이 460 중심(Y −957 / 223)에 → 460 밑면이 판 윗면(Y −977~−937)을 누름 → 판이 블록 윗면(Y −1021~−979) 끝 −979에서 외팔
  → 블록(SV2RL28, 레일 중심 Y −1000 / 180). 460 중심 ↔ 레일 중심 편심 43 → 블록 롤 모멘트(MC).
하중(요구서 6-1 비어 있음 → M-09): A 자중 ×3 g(판정), B 운전 1 g + X 가속 2 m/s²(D-12 자리값, 참고·뒤집힘 확인).
판정: SF 일반 3(M-09), 동작 문제 = SF < 1.2. 블록 허용치 C0 12,100 N·MC 135 N·m(미스미 페이지 2026-11-01, mech_T08_concept2.md).
실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T08_handcalc.py
결과: fea/results/mech_T08_handcalc.json, 로그 fea/results/mech_T08_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T08', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T08_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T08_handcalc_log.txt')
g = 9.81
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


def step_bbox(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    pts = {}
    for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", txt):
        pts[m.group(1)] = [float(v) for v in m.group(2).split(',')]
    vids = re.findall(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", txt)
    vs = [pts[i] for i in vids if i in pts]
    lo = [min(v[k] for v in vs) for k in range(3)]
    hi = [max(v[k] for v in vs) for k in range(3)]
    return lo, hi, len(vs)


res = {'model': 'v0.6.11', 'fea': '해석 못 함 — 환경 없음(D-16)', 'parts': {}}

# ---- 형상(STEP) ----
geo = {}
for n in ('P_T08_XPLATE_F', 'P_T08_XPLATE_B'):
    lo, hi, nv = step_bbox(os.path.join(STEPDIR, n + '.step'))
    geo[n] = {'min': [round(x, 3) for x in lo], 'max': [round(x, 3) for x in hi], 'vertices': nv}
    log(f'{n}: bbox {geo[n]["min"]} ~ {geo[n]["max"]} (vertex {nv})')
res['geometry'] = geo
gF = geo['P_T08_XPLATE_F']
t = gF['max'][2] - gF['min'][2]
W = gF['max'][1] - gF['min'][1]
Lx = gF['max'][0] - gF['min'][0]
log(f'판 t {t:.2f}, Y 폭 {W:.2f}, X 길이 {Lx:.2f}')

# 블록·460 Y 위치 (앞 F; 뒤 B는 같은 모양을 Y 거울 없이 +1180 평행이동 — 블록 끝 201, 460 203~243, 편심 같은 +43)
blk_edge = -979.0      # 블록 윗면 끝(460 쪽)
blk_c = -1000.0        # 레일·블록 중심
f460 = (-977.0, -937.0)
y460 = sum(f460) / 2   # −957
bolt_y = (-1016.0, -984.0)
ecc = y460 - blk_c     # 43
arm_edge = y460 - blk_edge   # 22
arm_near = y460 - bolt_y[1]  # 27
assert abs(gF['min'][1] - (-1024)) < 0.5 and abs(gF['max'][1] - (-937)) < 0.5, '판 Y bbox가 모델 보고와 다름'

# ---- 하중 ----
m_y = 28.17 + 13.06 + 7.89 + 8.75 + 38.02     # Y 이동 묶음 kg (선정 4절, 모델 질량)
m_x = 18.07                                     # MAT_X 자체(판·460·1300·Y 레일 등)
yF_sup, yB_sup = -957.0, 223.0
span = yB_sup - yF_sup
J = (-860.0, 40.0)
fracF = max((yB_sup - j) / span for j in J)     # Y 묶음 무게중심 ≈ J_MAT_Y (DG 테이블 중심 = J)
fracB = max((j - yF_sup) / span for j in J)
mF = m_y * fracF + m_x / 2
mB = m_y * fracB + m_x / 2
log(f'Y 묶음 {m_y:.2f} kg, MAT_X {m_x} kg, 지지 간격 {span:.0f}; 앞 몫 최대 {fracF:.3f} → {mF:.1f} kg, 뒤 몫 최대 {fracB:.3f} → {mB:.1f} kg')
m_side = max(mF, mB)
cases = {}
# A: 3 g 수직
PA = m_side * g * 3 / 2         # 블록 하나(한 레일 블록 2개 X ±180에 고르게, 묶음 X 0 대칭)
# B: 1 g + X 가속 2 m/s² (D-12 자리값), 무게중심 높이: 매트면 Z ≈ −137(m1_out 패드 윗면) ↔ 블록 윗면 −572 → 435(보수, 전 질량을 매트 높이에)
a_x = 2.0
h = 435.0
blk_dx = 360.0
P1 = m_side * g / 2
dP = (m_y + m_x) * a_x * h / blk_dx / 2 * (m_side / (mF + mB) * 2)   # 한 레일 몫
PB_max, PB_min = P1 + dP, P1 - dP
cases['A_3g'] = {'P_block_N': round(PA, 1)}
cases['B_1g_ax2'] = {'P_block_max_N': round(PB_max, 1), 'P_block_min_N': round(PB_min, 1), 'h_mm': h, 'a_x': a_x}
log(f'A 3 g: 블록당 {PA:.0f} N | B 1 g + X 2 m/s²: 블록 최대 {PB_max:.0f} / 최소 {PB_min:.0f} N (뒤집힘 {"없음" if PB_min > 0 else "있음"})')

Rp_plate = 175.0   # A5052 H32 가정 보수(models.json 앞 기록과 같게)
E_al = 70000.0
C0, MC = 12100.0, 135.0


def plate(P, tag):
    b = 60.0 + 2 * t           # 블록 길이 60 + 두께 방향 45° 퍼짐 양쪽
    # 단면 1: 블록 끝 −979, 팔 22, 온 폭 b
    Z1 = b * t ** 2 / 6
    s1 = P * arm_edge / Z1
    # 단면 2(보수): 가까운 볼트 줄 −984, 팔 27, 카운터보어 Ø9.5 뺀 폭
    Z2 = (b - 9.5) * t ** 2 / 6
    s2 = P * arm_near / Z2
    I = b * t ** 3 / 12
    d = P * arm_edge ** 3 / (3 * E_al * I)
    bm = handcalc.beam(t=t, b=b, length=arm_edge, load=P, e=E_al, sy=Rp_plate, end='cantilever', sf_min=3.0)
    sf = Rp_plate / max(s1, s2)
    log(f'[{tag}] 판 굽힘: 블록 끝 σ {s1:.1f} MPa, 볼트 줄 순단면 σ {s2:.1f} MPa → SF {sf:.1f}; 처짐 {d*1000:.2f} µm; handcalc.beam {bm}')
    return {'b_eff': b, 'sigma_edge': round(s1, 2), 'sigma_net': round(s2, 2), 'SF': round(sf, 2), 'deflect_mm': round(d, 5), 'handcalc_beam': bm}


def block(P, tag):
    M = P * ecc / 1000
    u = P / C0 + M / MC
    sf = 1 / u
    log(f'[{tag}] 블록: P {P:.0f} N (P/C0 {P/C0:.3f}), 롤 M {M:.1f} N·m (M/MC {M/MC:.3f}) → 합성 SF {sf:.2f}')
    return {'P': round(P, 1), 'M_roll_Nm': round(M, 2), 'P_C0': round(P / C0, 4), 'M_MC': round(M / MC, 4), 'SF': round(sf, 2)}


def blk_bolt(P, tag):
    # 판이 가까운 볼트 줄(−984)을 받침점으로 돈다고 본다(보수, 블록 끝 −979 받침보다 팔이 김), 먼 볼트(−1016) 팔 32 하나가 받음
    F = P * arm_near / (bolt_y[1] - bolt_y[0])
    r_al = handcalc.calc(d=5, le=7.5, load=F, torque=2.0, bolt='12.9', base='A5052', dw=8.5, dh=5.5)
    r_st = handcalc.calc(d=5, le=7.5, load=F, torque=2.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5)
    log(f'[{tag}] 블록 볼트 CB5-16 인장 {F:.0f} N: 모재 A5052(보수) {r_al["sf_operating"]} / SS400 {r_st["sf_operating"]}, 조임 2 N·m {r_st["sf_tightening"]}')
    return {'F_bolt_N': round(F, 1), 'A5052_conservative': r_al, 'SS400': r_st}


res['cases'] = cases
res['A_3g'] = {'plate': plate(PA, 'A 3g'), 'block': block(PA, 'A 3g'), 'block_bolt': blk_bolt(PA, 'A 3g')}
res['B_1g_ax2'] = {'plate': plate(PB_max, 'B'), 'block': block(PB_max, 'B'), 'block_bolt': blk_bolt(PB_max, 'B')}

# 판 → 460 CB5-20 + STEP대기_HNTT8-5(물림 5 = 1.0d, 임시 치수 D-41): 수직은 압축 경로(460이 판 위). 가로 힘(X 가속)은 마찰로.
Fx = mF * a_x * 3      # 앞 460이 판에 넘기는 X 힘, 가속 ×3(보수)
mu = 0.2
N_w = mF * g
T_need = max(0.0, Fx / mu - N_w) / 4     # 볼트 하나 필요 예압
r460 = handcalc.calc(d=5, le=5.0, load=0.0, torque=2.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5)
log(f'판 → 460: X 힘 {Fx:.0f} N(가속 ×3), 마찰 μ0.2 자중 몫 {mu*N_w:.0f} N → 볼트당 필요 예압 {T_need:.0f} N; 2 N·m 예압 {r460["preload_N"]} N, 조임 SF {r460["sf_tightening"]}')
res['plate_to_460'] = {'Fx_N': round(Fx, 1), 'friction_weight_N': round(mu * N_w, 1), 'preload_need_per_bolt_N': round(T_need, 1), 'handcalc_2Nm': r460}

worst_plate = min(res['A_3g']['plate']['SF'], res['B_1g_ax2']['plate']['SF'])
res['summary'] = {
    'plate_SF_min': worst_plate, 'plate_overspec': worst_plate >= 9,
    'block_SF_A': res['A_3g']['block']['SF'], 'block_SF_B': res['B_1g_ax2']['block']['SF'],
    'block_bolt_SF_min': min(min(res[k]['block_bolt']['A5052_conservative']['sf_operating'].values()) for k in ('A_3g', 'B_1g_ax2')),
    'uplift': PB_min <= 0,
}
log('요약', json.dumps(res['summary'], ensure_ascii=False))
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
