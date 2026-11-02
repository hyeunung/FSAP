# -*- coding: utf-8 -*-
"""T18-X04 X·Y 이송 너트 하중 경로 강화 손계산 (해석부, 2026-11-02, 대상 3D_Modeling/FSAP_v0.8.4.sc).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 + 엔진 handcalc(읽기만 import).
입력 형상: 모델링부 임시 STEP 3개(tools/out/mech_T18/stepout/P_T18_YNB·P_T18_XNP·P_T01_YPLATE.step, 대기 세계 좌표).
bbox는 STEP VERTEX에서 읽어 모델링 보고서(mech_T18_model.md 2절) 치수와 맞는지 확인하고, 단면·구멍·볼트 자리는 그 표의 좌표를 쓴다.

하중(과제 완료 판정): 오조작 2364 N = 2π·8.36 N·m(서보 순간 최대, D-51)·η 0.9 / 리드 20. 드라이버 토크 제한(T18-Q2)이 빠진 경우.
판정: 과제 완료 판정 SF ≥ 2(M-09 오조작 2), SF < 1.2 = 영구 변형 = 동작. 물림 YNUT ≥ 7.5, CB8 ≥ 12, CB5-16 ≥ 7.5.
모델 계열(fea/models.json): 받는 팔(고리)을 뿌리에서 고정한 외팔 + 축선 하중, 볼트 무리는 강체 지렛점 모델(선형 분배). v0.8.0과 같은 계열이다.
실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T18_x04_handcalc.py
결과: fea/results/mech_T18_x04_handcalc.json, 로그 fea/results/mech_T18_x04_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T18', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T18_x04_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T18_x04_handcalc_log.txt')
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


def step_bbox(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    pts = {m.group(1): [float(v) for v in m.group(2).split(',')]
           for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", txt)}
    vs = [pts[i] for i in re.findall(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", txt) if i in pts]
    return {'min': [round(min(v[k] for v in vs), 2) for k in range(3)],
            'max': [round(max(v[k] for v in vs), 2) for k in range(3)], 'n_vertex': len(vs)}


RP_6061, E_6061 = 240.0, 68900.0
RP_5052 = 175.0          # Y판(H32 가정 보수, models.json P_T01_YPLATE와 같음)
SF_REQ, SF_BREAK = 2.0, 1.2
F = 2 * math.pi * 8.36 * 0.9 / 0.020      # 2363.9 N
res = {'model': 'v0.8.4', 'task': 'T18-X04', 'fea': '해석 못 함 — 환경 없음(D-16)', 'F_N': round(F, 1),
       'geometry': {}, 'parts': {}, 'bolts': {}, 'engage': {}}
log('오조작 축력 F = %.1f N' % F)

expect = {'P_T18_YNB': ([20, -670, -476], [120, -610, -370]),
          'P_T18_XNP': ([130, -530, -590], [178, -290, -408])}
for n in ('P_T18_YNB', 'P_T18_XNP', 'P_T01_YPLATE'):
    gg = step_bbox(os.path.join(STEPDIR, n + '.step'))
    if n in expect:
        gg['matches_model_report'] = all(abs(a - b) < 0.05 for a, b in zip(gg['min'] + gg['max'], expect[n][0] + expect[n][1]))
    res['geometry'][n] = gg
    log(n, 'bbox', gg['min'], '~', gg['max'], 'vertex', gg['n_vertex'], 'match', gg.get('matches_model_report'))


def verdict(sf):
    return '동작(영구 변형)' if sf < SF_BREAK else ('디테일(기준 미달)' if sf < SF_REQ else ('과사양 문턱(note)' if sf >= 3 * SF_REQ else '됨'))


def ring_scan(width_lo, width_hi, t, z_root, z_axis, r_hole, taps, z_dir):
    """고리 단면 훑기: 뿌리 z_root → 축선 z_axis. 단면 폭 = 고리 폭 − 큰 구멍 현 − 탭 구멍(그 높이를 지나는 것). 팔 = |z − z_axis|.
    z_dir: 뿌리에서 축선 쪽 부호(−1 = 아래로). taps: [(z, d)] 같은 높이 탭 2개씩."""
    best = None
    rows = []
    span = abs(z_root - z_axis)
    n = 200
    for i in range(n + 1):
        dz = span * i / n
        z = z_root + z_dir * dz
        arm = abs(z - z_axis)
        if arm < 1.0:
            continue
        b = width_hi - width_lo
        dh = abs(z - z_axis)
        if dh < r_hole:
            b -= 2 * math.sqrt(r_hole ** 2 - dh ** 2)
        for zt, d in taps:
            if abs(z - zt) < d / 2:
                b -= 2 * 2 * math.sqrt((d / 2) ** 2 - (z - zt) ** 2)   # 같은 높이 탭 2개
        if b <= 0:
            continue
        s = F * arm / (b * t * t / 6.0)
        rows.append((round(z, 2), round(b, 2), round(arm, 2), round(s, 1)))
        if best is None or s > best[3]:
            best = rows[-1]
    return best, rows


# ---------------- 1. P_T18_YNB (A6061-T6 절삭: cap + 고리) ----------------
# 고리 X 50~120(폭 70)·Y −655~−643(t12, 축력 방향)·Z −476~−422, 구멍 Ø48 (X85, Z−448), M5 탭 Ø4.2 Z −433.25/−462.75
best, rows = ring_scan(50, 120, 12.0, -422.0, -448.0, 24.0, [(-433.25, 4.2), (-462.75, 4.2)], -1)
root_s = F * 26.0 / (70 * 12 ** 2 / 6.0)
Kt_root = 1.5   # 뿌리 R3 / t12 (r/t 0.25, 단차 굽힘 Kt 근사 Peterson) — 뿌리 공칭에만
ynb_ring = {'model': '고리를 cap 밑면 Z −422에서 고정한 외팔, 축력 F를 너트 축선 Z −448에 ±Y(팔 26). 단면 = 폭 70 − Ø48 현 − 같은 높이 M5 탭 2개, 두께 t12',
            'root_nominal': {'sigma_MPa': round(root_s, 1), 'Kt_R3': Kt_root, 'sigma_peak_MPa': round(root_s * Kt_root, 1),
                             'SF_nominal': round(RP_6061 / root_s, 2), 'SF_peak': round(RP_6061 / (root_s * Kt_root), 2)},
            'worst_net_section': {'z': best[0], 'b_net': best[1], 'arm': best[2], 'sigma_MPa': best[3], 'SF': round(RP_6061 / best[3], 2)}}
ynb_ring['SF'] = min(ynb_ring['root_nominal']['SF_peak'], ynb_ring['worst_net_section']['SF'])
ynb_ring['verdict'] = verdict(ynb_ring['SF'])
# 고리 처짐(외팔, 운전 검토 아님 — 오조작 2364 N에서 참고)
d_ring = handcalc.beam(12.0, 70.0, 26.0, load=F, e=E_6061, sy=RP_6061, sf_min=SF_REQ)
ynb_ring['deflect_at_axis_mm'] = d_ring['deflection_mm']

# cap → Y판: 볼트 4 (X 30: CB5-16 아래→Y판 탭 Le 8 / X 112: CB5-20 위→cap 탭 Le 10), 줄 Y −657·−623. 접면 Z −370.
M_cap = F * (448.0 - 370.0)
r_far, r_near = 670 - 657 + 34, 657 - 623 - 21        # 지렛점 −610: 47·13 / 지렛점 −670: 47(−623)·13(−657)
r_far, r_near = 47.0, 13.0
T_cap = M_cap * r_far / (2 * (r_far ** 2 + r_near ** 2))
V_cap = F / 4
ynb_cap = {'model': '축력 F가 접면 Z −370 아래 78에 걸린 모멘트를 볼트 4개가 강체 지렛점(cap 끝 Y −610 또는 −670) 둘레로 선형 분배. 줄 2개씩 팔 47·13',
           'M_Nmm': round(M_cap), 'T_max_per_bolt_N': round(T_cap, 1), 'V_per_bolt_N': round(V_cap, 1)}
# cap 몸체(100×60×52) 굽힘 — 고리 뿌리(Y −655~−643) ↔ 볼트 줄 사이 팔 ≤ 26, 폭 100 − 카운터보어 Ø9.5 ×2
s_cap = 2 * T_cap * 26.0 / ((100 - 2 * 9.5) * 52 ** 2 / 6.0)
ynb_cap['cap_body_sigma_MPa'] = round(s_cap, 1)
ynb_cap['cap_body_SF'] = round(RP_6061 / s_cap, 1)
res['parts']['P_T18_YNB'] = {'ring': ynb_ring, 'cap': ynb_cap}
log('YNB 고리', ynb_ring)
log('YNB cap', ynb_cap)

# 볼트: handcalc.calc (sf_min 2)
B = {}
B['YNB→Y판 CB5-16 (A5052 탭 Le 8)'] = handcalc.calc(5, 8.0, T_cap, torque=4.0, bolt='12.9', base='A5052', dw=8.5, dh=5.5, sf_min=SF_REQ)
B['YNB→Y판 CB5-20 (cap A6061 탭 Le 10)'] = handcalc.calc(5, 10.0, T_cap, torque=4.0, bolt='12.9', base='A6061-T6', dw=8.5, dh=5.5, sf_min=SF_REQ)
B['YNUT CB5-20 ×4 → 고리 (A6061 Le 11.5)'] = handcalc.calc(5, 11.5, F / 4, torque=4.0, bolt='12.9', base='A6061-T6', dw=8.5, dh=5.5, sf_min=SF_REQ)
B['XNUT CB8-25 ×4 → 고리 (A6061 Le 17)'] = handcalc.calc(8, 17.0, F / 4, torque=10.0, bolt='12.9', base='A6061-T6', dw=13.0, dh=8.5, sf_min=SF_REQ)
# cap 볼트 전단(마찰 무시, 볼트 몸 전단 0.6·Rp)
sf_shear = 0.6 * 1100 * 14.2 / V_cap
res['bolts'] = B
res['bolts_extra'] = {'YNB cap 볼트 전단 SF (마찰 무시)': round(sf_shear, 1),
                      'YNB cap 미끄럼 SF (예압 4 kN×4, μ 0.15, D-54)': round(4 * 4000 * 0.15 / F, 2)}

# Y판 국부 굽힘: X 30 볼트 2개(Y판 탭에 물림) 당김 2×T_cap, 고정 원판 a60 (T14와 같은 Roark 11.2 16)
P = 2 * T_cap; t = 10.0; a = 60.0; r0 = 4.25; nu = 0.33
rp = math.sqrt(1.6 * r0 ** 2 + t * t) - 0.675 * t if r0 < 0.5 * t else r0
s_c = 3 * P / (2 * math.pi * t * t) * (1 + nu) * math.log(a / rp)
res['parts']['P_T01_YPLATE'] = {'model': 'X 30 볼트 2개 당김 합 P를 고정 원판(a 60, 블록·받침까지 보수) 중심 집중하중으로(Roark 11.2 case 16, r0 보정). T14 검사와 같은 모델',
                                'P_N': round(P, 1), 'sigma_center_MPa': round(s_c, 1), 'SF': round(RP_5052 / s_c, 2)}
res['parts']['P_T01_YPLATE']['verdict'] = verdict(res['parts']['P_T01_YPLATE']['SF'])
log('Y판 국부', res['parts']['P_T01_YPLATE'])

# ---------------- 2. P_T18_XNP (A6061-T6 절삭: 옆판 t8 + 밑판 t12 + 고리 t17) ----------------
best, rows = ring_scan(-460, -360, 17.0, -490.0, -555.0, 27.0, [(-538.0, 6.8), (-572.0, 6.8)], -1)
root_s = F * 65.0 / (100 * 17 ** 2 / 6.0)
xr = {'model': '고리를 밑판 밑면 Z −490에서 고정한 외팔, 축력 F를 축선 Z −555에 ±X(팔 65). 단면 = 폭 100 − Ø54 현 − 같은 높이 M8 탭 2, 두께 t17',
      'root_nominal': {'sigma_MPa': round(root_s, 1), 'Kt_R3': 1.6, 'sigma_peak_MPa': round(root_s * 1.6, 1),
                       'SF_nominal': round(RP_6061 / root_s, 2), 'SF_peak': round(RP_6061 / (root_s * 1.6), 2)},
      'worst_net_section': {'z': best[0], 'b_net': best[1], 'arm': best[2], 'sigma_MPa': best[3], 'SF': round(RP_6061 / best[3], 2)}}
xr['SF'] = min(xr['root_nominal']['SF_peak'], xr['worst_net_section']['SF'])
xr['verdict'] = verdict(xr['SF'])
xr['deflect_at_axis_mm'] = handcalc.beam(17.0, 100.0, 65.0, load=F, e=E_6061, sy=RP_6061, sf_min=SF_REQ)['deflection_mm']

# 밑판 t12 (X 130~178): 고리(X 138~155) → 옆판(X 170) 사이 모멘트 F × (축선 −555 ↔ 밑판 중립 −484) = F·71
M_bp = F * 71.0
bp = {}
for lab, w in (('폭 240 전폭', 240.0), ('고리 폭 100 + 45° 퍼짐 2×15', 130.0), ('고리 폭 100만(하한)', 100.0)):
    s = M_bp / (w * 12 ** 2 / 6.0)
    bp[lab] = {'sigma_MPa': round(s, 1), 'SF': round(RP_6061 / s, 2)}
xb = {'model': '밑판을 옆판 모서리에서 고정, 고리 쪽 모멘트 F·71', 'M_Nmm': round(M_bp), 'cases': bp,
      'SF': bp['고리 폭 100 + 45° 퍼짐 2×15']['SF']}
xb['verdict'] = verdict(xb['SF'])

# 옆판 t8 → 1300_R: CB5-20 ×14 (줄 Z −458·−418 × 7). 당김(+X): 지렛점 옆판 윗끝 −408, 팔 147, 줄 팔 50·10
d1, d2, lF = 50.0, 10.0, 147.0
T1 = F * lF * d1 / (7 * (d1 ** 2 + d2 ** 2))
T2 = T1 * d2 / d1
R = 7 * T1 + 7 * T2 - F
# 밂(−X): 지렛점 옆판 밑끝 −490, 팔 65, 줄 팔 32·72
T_push = F * 65 * 72 / (7 * (32 ** 2 + 72 ** 2))
# 옆판 굽힘(지렛 모델, 판이 벌어진다고 본 상한): 최대 모멘트는 아래 줄 Z −458
M_sp = R * 50.0 - 7 * T2 * 40.0
sp = {}
for lab, w, nh in (('전폭 240, 구멍 7', 240.0, 7), ('고리 폭 100 + 밑판 퍼짐 2×32 = 164, 구멍 5', 164.0, 5)):
    bnet = w - nh * 5.5
    bb = handcalc.beam(8.0, bnet, 50.0, load=M_sp / 50.0, e=E_6061, sy=RP_6061, sf_min=SF_REQ)
    sp[lab] = {'b_net': bnet, 'sigma_MPa': bb['stress_MPa'], 'SF': bb['sf'], 'thin': bb['thin'], 'needs_fea': bb['needs_fea']}
xs = {'model': '옆판(t8, 높이 82)을 지렛점(윗끝 −408)과 볼트 줄 사이 보로 봄. 볼트 예압 4 kN ≫ 최대 당김이면 접면이 안 벌어져 이 값은 상한',
      'T_row_lower_N': round(T1, 1), 'T_row_upper_N': round(T2, 1), 'pivot_R_N': round(R, 1), 'T_push_max_N': round(T_push, 1),
      'M_max_Nmm': round(M_sp), 'cases': sp, 'SF': sp['전폭 240, 구멍 7']['SF'],
      'SF_lower_bound': sp['고리 폭 100 + 밑판 퍼짐 2×32 = 164, 구멍 5']['SF'],
      'separation_SF': round(4000.0 / T1, 2)}
xs['verdict'] = verdict(xs['SF'])
res['parts']['P_T18_XNP'] = {'ring': xr, 'base_plate': xb, 'side_plate': xs}
log('XNP 고리', xr)
log('XNP 밑판', xb)
log('XNP 옆판', xs)

B['XNP→1300_R CB5-20 + HNTT8-5 ×14 (볼트 쪽)'] = handcalc.calc(5, 5.0, T1, torque=4.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=SF_REQ)
res['bolts_extra']['HNTT8-5 립 뽑힘 SF (허용 2.0 kN/개 임시, D-54)'] = round(2000.0 / T1, 2)
res['bolts_extra']['XNP 옆판 분리 SF (예압 4 kN / 최대 당김)'] = round(4000.0 / T1, 2)

# 물림(모델링 보고서 실측)
res['engage'] = {'YNUT CB5-20': (11.5, 7.5), 'XNUT CB8-25': (17.0, 12.0), 'CB5-16_T18_YNB → Y판': (8.0, 7.5), 'CB5-20_T18_YNB → cap': (10.0, 7.5)}
res['engage'] = {k: {'Le': v[0], 'need': v[1], 'ok': v[0] >= v[1]} for k, v in res['engage'].items()}

for k, v in B.items():
    log(k, 'op', v['sf_operating'], 'tight', v['sf_tightening'], 'ok', v['ok'], 'near', v['near_limit'])
log('추가', res['bolts_extra'])
log('물림', res['engage'])

json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
