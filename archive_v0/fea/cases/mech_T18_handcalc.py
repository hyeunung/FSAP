# -*- coding: utf-8 -*-
"""T18 X·Y 볼나사 이송 유닛 손계산 (해석부, 2026-11-02, 대상 3D_Modeling/FSAP_v0.8.0.sc).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 + 엔진 handcalc(읽기만).
입력 형상: 모델링부 임시 STEP 6개(tools/out/mech_T18/stepout/*.step, 대기 세계 좌표). bbox·두께는 STEP VERTEX에서 읽고,
하중점·볼트 자리는 tools/gen_t18_mech.py(생성기)의 좌표(축선 Y: X 85·Z −448, X: Y −410·Z −555)를 쓴다.

하중(요구서 6-1 빈칸 → M-09: 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형 = 동작):
  운전 축력  F_op = m·a + μ·m·g  (a 2 m/s², D-12 임시; μ 0.01 구름; Y 76 kg·X 96 kg, 측정부 모델 질량)
  오조작 축력 F_mis = 2π·T_lim·η / l (행정 끝·이물 걸림, 드라이버 토크 제한 T_lim 4 N·m = T18-Q2, η 0.9, 리드 20)
  참고(제한 실패) F_max = 같은 식에 서보 순간 최대 8.36 N·m (D-51) — 판정에 쓰지 않고 SF만 남김
  자중 ×3 g (서보 2.3 kg, D-51)
속도: 과제 지시 D-12 빈 이동 300 mm/s 와 D-52(사용자 결정 대기, 기본 280 mm/s) 둘 다 계산.
실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T18_handcalc.py
결과: fea/results/mech_T18_handcalc.json, 로그 fea/results/mech_T18_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T18', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T18_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T18_handcalc_log.txt')
g = 9.81
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


def step_geo(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    pts = {m.group(1): [float(v) for v in m.group(2).split(',')]
           for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", txt)}
    vs = [pts[i] for i in re.findall(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", txt) if i in pts]
    lo = [min(v[k] for v in vs) for k in range(3)]
    hi = [max(v[k] for v in vs) for k in range(3)]
    # 판 두께: 각 축의 정점 좌표 값(반올림) 중 가장 작은 간격 쌍 = 판 두께 후보
    levels = [sorted({round(v[k], 2) for v in vs}) for k in range(3)]
    return {'min': [round(x, 2) for x in lo], 'max': [round(x, 2) for x in hi], 'n_vertex': len(vs),
            'levels': [lv if len(lv) <= 14 else lv[:6] + ['…'] + lv[-6:] for lv in levels]}


SY_SUS = 205.0     # SUS304 Rp0.2 MPa
E_SUS = 193000.0
SF_OP, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2
lead, eta = 20.0, 0.9
T_lim, T_max = 4.0, 8.36
res = {'model': 'v0.8.0', 'fea': '해석 못 함 — 환경 없음(D-16)', 'geometry': {}, 'loads': {}, 'parts': {}, 'drive': {}, 'bolts': {}}

for n in ('P_T18_YMB', 'P_T18_YNB', 'P_T18_XMB', 'P_T18_XNP', 'P_T18_XBP', 'P_T18_XSP'):
    gg = step_geo(os.path.join(STEPDIR, n + '.step'))
    res['geometry'][n] = gg
    log(f'{n}: bbox {gg["min"]} ~ {gg["max"]} (vertex {gg["n_vertex"]})')

# ---- 하중 ----
mY, mX, mu = 76.0, 96.0, 0.01
a = 2.0
F_op = {'Y': mY * a + mu * mY * g, 'X': mX * a + mu * mX * g}
F_mis = 2 * math.pi * T_lim * eta / (lead / 1000.0)
F_max = 2 * math.pi * T_max * eta / (lead / 1000.0)
W_srv = 2.3 * 3 * g
res['loads'] = {'F_op_Y_N': round(F_op['Y'], 1), 'F_op_X_N': round(F_op['X'], 1), 'F_mis_N': round(F_mis, 1),
                'F_max_ref_N': round(F_max, 1), 'W_servo_3g_N': round(W_srv, 1),
                'a_crash_X_m_s2': round(F_mis / mX, 2)}
log('하중:', res['loads'])


def ki_curved(ri, t):
    """사각 단면 곡선보 안쪽 응력 계수(Shigley 곡선보 정식)."""
    ro = ri + t
    rc = ri + t / 2
    rn = t / math.log(ro / ri)
    e = rc - rn
    s_curved = (rn - ri) / (t * e * ri)   # σ/(M/b)
    s_straight = 6.0 / (t * t)
    return s_curved / s_straight


def sec(b, t):
    return b * t * t / 6.0


def judge(sf_op, sf_mis):
    if sf_mis < SF_BREAK or sf_op < SF_BREAK:
        return '동작(영구 변형)'
    if sf_op < SF_OP or sf_mis < SF_MIS:
        return '디테일(기준 미달)'
    if sf_op >= 3 * SF_OP and sf_mis >= 3 * SF_MIS:
        return '과사양(note)'
    return '됨'


# ---- 1. P_T18_YNB  너트 받침 L t8 (MAT_Y) ----
# 웹 X50~120(b 70)·Y−678~−670, 축선 Z −448, 굽힘 안 R8(웹 끝 Z −386, 윗다리 밑면 −378), 윗다리 볼트 CB5-16 ×2 Y −640(X 55·115)
t, b = 8.0, 70.0
arm = 448.0 - 378.0      # 축선 → 윗다리 밑면(굽힘 끝, 보수)
Ki = ki_curved(8.0, t)
def ynb(F):
    M = F * arm
    s = M / sec(b, t) * Ki
    return M, s
Mo, so = ynb(F_op['Y']); Mm, sm = ynb(F_mis); Mx, sx = ynb(F_max)
# 윗다리 볼트 들림: 지렛점 = 다리 끝 Y −610(볼트까지 30) 또는 웹 바깥 −678(38) → 30이 불리
Tb_mis = Mm / 30.0 / 2
Tb_op = Mo / 30.0 / 2
# 웹 처짐(운전, 축선, 외팔 보)
d_op = handcalc.beam(t, b, arm, load=F_op['Y'], e=E_SUS, sy=SY_SUS)
res['parts']['P_T18_YNB'] = {
    'model': '웹을 굽힘 끝(윗다리 밑면 Z −378)에서 고정한 외팔, 축력은 축선 Z −448(팔 70). 곡선보 Ki %.3f(안 R8, t8)' % Ki,
    'op': {'F_N': round(F_op['Y'], 1), 'M_Nm': round(Mo / 1000, 2), 'sigma_MPa': round(so, 1), 'SF': round(SY_SUS / so, 2), 'deflect_mm': d_op['deflection_mm']},
    'mis': {'F_N': round(F_mis, 1), 'M_Nm': round(Mm / 1000, 2), 'sigma_MPa': round(sm, 1), 'SF': round(SY_SUS / sm, 2)},
    'ref_Tmax': {'F_N': round(F_max, 1), 'sigma_MPa': round(sx, 1), 'SF': round(SY_SUS / sx, 2)},
    'bolt_tension_per_bolt_N': {'op': round(Tb_op), 'mis': round(Tb_mis)},
}
r = res['parts']['P_T18_YNB']; r['verdict'] = judge(r['op']['SF'], r['mis']['SF'])
log('YNB', r)

# ---- 2. P_T18_XNP  X 너트판 t8 (MAT_X, 1300_R 바깥 옆면 X 170) ----
# 판 Y −460~−360(b 100), Z −581~−408, 축선 Z −555, 볼트 CB5-20 ×4 Y −440·−380 · Z −458·−418, 형재 밑끝 Z −478(80 높이, 홈 ±20)
t, b = 8.0, 100.0
bnet = b - 2 * 5.5
arm_pull = 555.0 - 458.0 - 8.5 / 2    # 당김: 아래 볼트 열 머리 자리 끝에서 고정
arm_push = 555.0 - 478.0              # 밂: 형재 밑 모서리에서 고정
def xnp(F):
    s_pull = F * arm_pull / sec(bnet, t)
    s_push = F * arm_push / sec(b, t)
    return max(s_pull, s_push), s_pull, s_push
so, _, _ = xnp(F_op['X']); sm, smp, smq = xnp(F_mis); sx, _, _ = xnp(F_max)
# 볼트 들림(당김): 지렛점 판 윗끝 Z −408, 볼트 열 거리 50·10(열마다 2개)
d1, d2, lF = 458 - 408, 418 - 408, 555 - 408
Tb = lambda F: F * lF * d1 / (2 * (d1 ** 2 + d2 ** 2))
d_op = handcalc.beam(t, bnet, arm_pull, load=F_op['X'], e=E_SUS, sy=SY_SUS)
res['parts']['P_T18_XNP'] = {
    'model': '평판 외팔. 당김(형재에서 떨어지는 쪽): 아래 볼트 열 Z −458 머리 자리 끝 고정, 순단면 b %.0f, 팔 %.2f / 밂: 형재 밑 모서리 Z −478 고정, b 100, 팔 77' % (bnet, arm_pull),
    'op': {'F_N': round(F_op['X'], 1), 'sigma_MPa': round(so, 1), 'SF': round(SY_SUS / so, 2), 'deflect_mm': d_op['deflection_mm']},
    'mis': {'F_N': round(F_mis, 1), 'sigma_pull_MPa': round(smp, 1), 'sigma_push_MPa': round(smq, 1), 'SF': round(SY_SUS / sm, 2)},
    'ref_Tmax': {'F_N': round(F_max, 1), 'sigma_MPa': round(sx, 1), 'SF': round(SY_SUS / sx, 2)},
    'bolt_tension_per_bolt_N': {'op': round(Tb(F_op['X'])), 'mis': round(Tb(F_mis)), 'ref_Tmax': round(Tb(F_max))},
    'fix_options': {'t10': round(SY_SUS / (F_mis * arm_pull / sec(bnet, 10.0)), 2),
                    'T_lim_3.5': round(SY_SUS / (sm * 3.5 / T_lim), 2)},
}
r = res['parts']['P_T18_XNP']; r['verdict'] = judge(r['op']['SF'], r['mis']['SF'])
log('XNP', r)

# ---- 3. P_T18_XBP  고정측 받침판 t15 (BASE, 가로대 윗면 Z −600) ----
# 추력은 BSW20(고정측)이 받는다. 축선 Z −555 = 판 윗면 −585 + 30, 판·형재 접면 −600 → 팔 45
# 판 → 형재: CB5-20 ×4(X −587·−547, Y −475·−345) + HNTT8-5, 마찰로 미끄럼 막음
T_cb5 = 4.0     # N·m, T너트 조임 토크 임시값(D-55 임시)
Fv = T_cb5 * 1000 / (0.2 * 5)
mu_s = 0.15
def xbp(F):
    slip = 4 * Fv * mu_s / F
    M = F * 45.0
    # 넘어짐: 지렛점 판 끝 X −527(또는 −607), 볼트 열 거리 60·20(열마다 2개)
    Tb = M * 60 / (2 * (60 ** 2 + 20 ** 2))
    # 판 굽힘: BSW20 볼트(X −558·−536) ↔ 판 볼트(X −547·−587) 사이, 보수로 팔 30·폭 160 순단면(구멍 2×6.8 + 2×9.5)
    s = (Tb * 2 * 30.0) / sec(160 - 2 * 9.5, 15.0)
    return slip, Tb, s
so_slip, Tbo, so = xbp(F_op['X']); sm_slip, Tbm, sm = xbp(F_mis); sx_slip, _, _ = xbp(F_max)
res['parts']['P_T18_XBP'] = {
    'model': 'BSW20 추력(축선 Z −555)을 판 → 형재 접면 Z −600(팔 45)으로. 미끄럼은 볼트 4 예압 마찰(조임 %.1f N·m 임시, μ %.2f), 넘어짐은 판 끝 지렛점' % (T_cb5, mu_s),
    'op': {'F_N': round(F_op['X'], 1), 'SF_slip': round(so_slip, 2), 'bolt_T_N': round(Tbo), 'sigma_MPa': round(so, 2), 'SF': round(SY_SUS / so, 1)},
    'mis': {'F_N': round(F_mis, 1), 'SF_slip': round(sm_slip, 2), 'bolt_T_N': round(Tbm), 'sigma_MPa': round(sm, 2), 'SF': round(SY_SUS / sm, 1)},
    'ref_Tmax': {'SF_slip': round(sx_slip, 2)},
}
r = res['parts']['P_T18_XBP']; r['verdict'] = judge(r['op']['SF'], r['mis']['SF'])
r['verdict_slip'] = '디테일(+10% 안, 임시 조임 토크)' if sm_slip < 1.1 * SF_MIS else ('디테일(기준 미달)' if sm_slip < SF_MIS else '됨')
log('XBP', r)

# ---- 4. P_T18_XSP  지지측 받침판 t15 (BUN20, 축 방향 자유 → 지름 방향 하중만) ----
m_shaft = math.pi / 4 * 0.025 ** 2 * 1.443 * 7850
Wr = m_shaft / 2 * 3 * g
s = Wr * 30 / sec(160 - 2 * 9.5, 15.0)
res['parts']['P_T18_XSP'] = {'model': 'BUN20 지지측(축 방향 자유). 축 자중 절반 ×3 g만', 'm_shaft_kg': round(m_shaft, 2),
                             'op': {'F_N': round(Wr, 1), 'sigma_MPa': round(s, 3), 'SF': round(SY_SUS / s)},
                             'verdict': '과사양(note)'}
log('XSP', res['parts']['P_T18_XSP'])

# ---- 5. P_T18_XMB  X 모터 브래킷 L t8 (BASE, 가로대 밑면 Z −640) ----
# 판 X −646~−638(서보 플랜지 면 −646), 몸 X −776~−656 → 무게중심 X ≈ −716(판에서 70), 축선 Z −555
# 발 X −646~−540·Z −648~−640, CB5-20 ×2 (X −587·−547, Y −410)
t = 8.0
Mw_plate = W_srv * 70.0                      # 판 뿌리(굽힘) 면외 굽힘, 폭 90
s_plate = Mw_plate / sec(90.0, t) * ki_curved(8.0, t)
Mw_foot = W_srv * (716.0 - 587.0)            # 발: 볼트 X −587 단면, 순폭 90−5.5
s_foot = Mw_foot / sec(90.0 - 5.5, t)
Tb_foot = Mw_foot * 47 / (47 ** 2 + 7 ** 2)  # 지렛점 발 끝 X −540, 볼트 거리 47·7
# 반력 토크(축 X 둘레): 발 Y 끝 지렛점(팔 45), 볼트 2 = Y 중심선
Tq = {'mis': T_lim, 'ref_Tmax': T_max}
s_tq = {k: v * 1000 / sec(106 - 11, t) for k, v in Tq.items()}
sm = max(s_plate, s_foot) + s_tq['mis'] * 0   # 자중과 토크는 다른 면 → 큰 쪽
res['parts']['P_T18_XMB'] = {
    'model': '서보 2.3 kg ×3 g 무게중심 판에서 70(외팔). 발은 가로대 밑면에 매달림, 지렛점 발 끝 X −540. 반력 토크는 축 X 둘레(발 Y 끝 지렛점)',
    'op': {'W_N': round(W_srv, 1), 'sigma_plate_MPa': round(s_plate, 2), 'sigma_foot_MPa': round(s_foot, 2),
           'SF': round(SY_SUS / max(s_plate, s_foot), 1), 'bolt_T_N': round(Tb_foot)},
    'mis': {'T_Nm': T_lim, 'sigma_MPa': round(s_tq['mis'], 2), 'SF': round(SY_SUS / s_tq['mis'], 1), 'bolt_T_N': round(T_lim * 1000 / 45 / 2)},
    'ref_Tmax': {'sigma_MPa': round(s_tq['ref_Tmax'], 2), 'SF': round(SY_SUS / s_tq['ref_Tmax'], 1)},
}
r = res['parts']['P_T18_XMB']; r['verdict'] = judge(r['op']['SF'], r['mis']['SF'])
r['downsize_t5_SF_op'] = round(SY_SUS / (Mw_foot / sec(84.5, 5.0)), 1)
log('XMB', r)

# ---- 6. P_T18_YMB  Y 모터 브래킷 모자형 t8 (MAT_X, 460_B 뒷면 Y 243) ----
# 서보 무게중심 Y ≈ 378, 탭 면 Y 247 → 팔 131. 옆벽 X 20~28·142~150, 높이 158(Z −558~−400), 길이 49(Y 251~300)
# X 충돌 감속(오조작) a = F_mis / mX 가 서보에 옆(X)으로
a_crash = F_mis / mX
Fx = 2.3 * (a_crash + 0) + 0
M_tab = W_srv * 131.0
Tb_tab = M_tab * 60 / (2 * (20 ** 2 + 60 ** 2))      # 지렛점 탭 밑끝 Z −558, 볼트 열 20·60
s_wall_in = M_tab / (2 * sec(8.0, 158.0) * 1.0)       # 옆벽 면내(높이 158) 굽힘 — sec(b=t, h) 형태: b·h²/6
s_wall_in = M_tab / (2 * 8.0 * 158.0 ** 2 / 6.0)
M_x = Fx * (378 - 251)
s_wall_out = M_x / (2 * sec(158.0, 8.0))
# 반력 토크(축 Y 둘레) → 옆벽 두 장(중심 간격 122) 면내 짝힘
Fc = {'mis': T_lim / 0.122, 'ref_Tmax': T_max / 0.122}
s_tq = {k: v * 49.0 / (8.0 * 158.0 ** 2 / 6.0) for k, v in Fc.items()}
res['parts']['P_T18_YMB'] = {
    'model': '모자형: 모터 면 → 옆벽 2(외팔 49, Y 251 굽힘) → 탭 → 460_B 뒷면. 자중 ×3 g, X 충돌 감속 %.1f m/s²(오조작), 반력 토크' % a_crash,
    'op': {'W_N': round(W_srv, 1), 'sigma_wall_MPa': round(s_wall_in, 3), 'bolt_T_N': round(Tb_tab), 'SF': round(SY_SUS / max(s_wall_in, 1e-9))},
    'mis': {'Fx_N': round(Fx, 1), 'sigma_wall_out_MPa': round(s_wall_out, 2), 'sigma_torque_MPa': round(s_tq['mis'], 3),
            'SF': round(SY_SUS / (s_wall_out + s_tq['mis'] + s_wall_in))},
    'ref_Tmax': {'sigma_torque_MPa': round(s_tq['ref_Tmax'], 3)},
}
r = res['parts']['P_T18_YMB']; r['verdict'] = judge(r['op']['SF'], r['mis']['SF'])
log('YMB', r)

# ---- 7. 구동(볼나사·서보, M-09 SF 2 = 과제 완료 판정) ----
def drive(ax, dr, span, m, d_shaft, Ls, Jc=4.7e-5, Jr=1.56e-4):
    nc = 15.1 * dr / span ** 2 * 1e7          # 고정–지지 λ 15.1 (미스미·THK 식)
    out = {'root_d': dr, 'span': span, 'n_crit_rpm': round(nc)}
    for v in (300, 280):
        n = v / lead * 60
        out[f'SF_crit@{v}'] = round(nc / n, 3)
    out['v_SF2_mm_s'] = round(nc / 2 * lead / 60, 1)
    out['span_SF2@300'] = round(math.sqrt(15.1 * dr * 1e7 / (2 * 900)), 1)
    Pb = 20.0 * dr ** 4 / span ** 2 * 1e4     # 고정–지지 m 20
    out.update({'P_buckle_N': round(Pb), 'SF_buckle_op': round(Pb / F_op[ax], 1), 'SF_buckle_mis': round(Pb / F_mis, 1),
                'SF_buckle_ref_Tmax': round(Pb / F_max, 1)})
    Js = math.pi / 32 * 7850 * (Ls / 1000) * (d_shaft / 1000) ** 4
    Jm = m * (lead / 1000 / (2 * math.pi)) ** 2
    Jl = Js + Jm + Jc
    ratio = Jl / Jr
    alpha = a * 1000 / lead * 2 * math.pi
    T = (m * a + mu * m * g) * lead / 1000 / (2 * math.pi * eta) + (Js + Jc + Jr) * alpha
    out.update({'J_screw': Js, 'J_mass': Jm, 'J_load': Jl, 'inertia_ratio': round(ratio, 2), 'SF_ratio': round(20 / ratio, 2),
                'T_peak_this_Nm': round(T, 3), 'SF_Tmax': round(T_max / max(T, 1.26 if ax == 'Y' else 1.71), 2),
                'J_rotor_need_SF2': round(Jl / 10, 7)})
    out['DN'] = round((d_shaft + 0.5) * 900)
    return out
res['drive']['Y'] = drive('Y', 15.9, 1181.5, mY, 20.0, 1240.0)
res['drive']['X'] = drive('X', 21.0, 1366.0, mX, 25.0, 1443.0)
res['drive']['coupling_SCXW46'] = {'T_allow': 10.0, 'SF@T_lim': round(10.0 / T_lim, 2), 'SF@T_max_ref': round(10.0 / T_max, 2)}
log('drive Y', res['drive']['Y']); log('drive X', res['drive']['X'])

# ---- 8. 새 브래킷 볼트(handcalc, 오조작 기준 SF 2) ----
res['bolts']['CB5-16_YNB→YPLATE(A5052, Le 8)'] = handcalc.calc(5, 8, res['parts']['P_T18_YNB']['bolt_tension_per_bolt_N']['mis'], torque=4.0, bolt='12.9', base='A5052', sf_min=SF_MIS)
res['bolts']['CB5-20_XNP→HNTT8-5(Le 9, 너트 S45C 근사)'] = handcalc.calc(5, 9, res['parts']['P_T18_XNP']['bolt_tension_per_bolt_N']['mis'], torque=4.0, bolt='12.9', base='S45C', sf_min=SF_MIS)
res['bolts']['CB8-25_XNUT→XNP(SUS304, Le 8)'] = handcalc.calc(8, 8, F_mis / 4 * 1.0 + 0.0, torque=10.0, bolt='12.9', base='SUS304', sf_min=SF_MIS)
res['bolts']['CB5-20_YNUT→YNB(SUS304, Le 5)'] = handcalc.calc(5, 5, F_mis / 4, torque=4.0, bolt='12.9', base='SUS304', sf_min=SF_MIS)
res['bolts']['CB8-45_BSW20→XBP(SUS304, Le 15)'] = handcalc.calc(8, 15, max(F_mis * 30 / 22 / 2, 1.0), torque=10.0, bolt='12.9', base='SUS304', sf_min=SF_MIS)
for k, v in res['bolts'].items():
    log(k, v['sf_operating'], v['sf_tightening'], 'ok' if v['ok'] else 'NG', v['near_limit'])
res['temp_values'] = {'T_cb5_into_HNTT8-5_Nm': T_cb5, 'mu_slip': mu_s, 'T_cb8_Nm': 10.0, 'K': 0.2,
                      'T_lim_driver_Nm(T18-Q2)': T_lim, 'masses_kg': {'Y': mY, 'X': mX}, 'a_m_s2(D-12)': a}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
print('OK', OUT)
