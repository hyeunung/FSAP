# -*- coding: utf-8 -*-
"""N04 해석부 손계산 — U5 에어 테이블 새 하중 부품 9개 (v1.0.12). FEA 환경 없음(D-16).
형상: stage_4_under·5_y·6_fix.json 명령(= tools/out/mech_N04/stepout/*.step bbox, 이 스크립트가 STEP 점 bbox로 다시 확인). 월드 mm, J 0.
하중(임시값, 출처):
  자중 x3 g(운전, 지시) / x1 g(오조작). 판 면밀도 7.60 kg/m²(CAD, D-89), 큰 매트 12.9 kg/m²(mech_N04_model.md 6절).
  손: 운전 100 N(작업자가 매트를 놓으며 누름, 모델링부 처짐 손계산과 같은 값) / 오조작 300 N(기대어 짚음, N03 해석과 같은 값).
      작은 받침(안장·꼬리판)은 손바닥 100x100 고른 압력(운전 0.01 MPa, 오조작 0.03 MPa)으로 받는다(매트를 사이에 둔 손).
  공기실 압력: 운전 338 Pa(C2 운전점), 오조작 12 kPa(구멍이 다 막혀 블로어 최대 정압, catalog.md 1절 '약 12 kPa').
  꼬리 멈춤 실린더 CDJ2B16(보어 16): 운전 0.5 MPa(요구서 2-4 운전 압력 미정 -> 0-6 공급 0.5 MPa 기본값) 추력 100.5 N,
      오조작 0.7 MPa(조절기 최대 가정) 140.7 N. 사슬 끝이 걸려 로드가 멈추면 추력이 전부 받침으로 간다.
  정하중 스프링 약 20 N(D-89, 선정 12절) / 오조작: 사슬을 손으로 당김 100 N.
  사슬 질량: 선정 9절 사슬 6.5 kg 전부를 보관 하나에 몰아 봄(보수).
  매트 끌림(안장 옆 힘): 운전 30 N / 오조작 100 N(D-79 봉제 끌림 전부).
  블로어 11 kg(catalog.md 1절) x3 g.
판정: M-09 운전 SF 3·오조작 SF 2(요구서 6-1 기본값), SF < 1.2 = 영구 변형(동작). 6-2 변위 미정(D-08).
재질 항복(하한): SUS304 205, A5052-H34 표피 175, A6061-T6 245, SS400 245, 접착 겹침 전단 15(에폭시 필름 어림, 임시).
"""
import json, math, re, sys, os
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

G = 9.81
RP = {'SUS304': 205.0, 'A5052': 175.0, 'A6061': 245.0, 'SS400': 245.0, 'BOND': 15.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0, 'SS400': 205000.0}
SFMIN = {'run': 3.0, 'mis': 2.0}
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
out = {'_note': '손계산(FEA 환경 없음 D-16). 단위 mm·N·MPa', 'step_bbox': {}, 'items': []}


def item(part, where, case, stress, mat, extra=None, shear=False):
    rp = RP[mat] / math.sqrt(3) if shear else RP[mat]
    sf = rp / stress if stress else float('inf')
    r = {'part': part, 'where': where, 'case': case, 'stress_MPa': round(stress, 2), 'mat': mat,
         'shear': shear, 'sf': round(sf, 2), 'sf_min': SFMIN[case], 'ok': sf >= SFMIN[case],
         'near_10pct': SFMIN[case] <= sf < 1.1 * SFMIN[case], 'oversize_3x': sf >= 3 * SFMIN[case],
         'motion_break': sf < 1.2}
    if extra:
        r.update(extra)
    out['items'].append(r)
    return r


# ---- 0) STEP bbox 확인(형상 = 지시서 좌표인지)
def step_bbox(p):
    xs, ys, zs = [], [], []
    with open(p, encoding='latin-1') as f:
        for m in re.finditer(r"CARTESIAN_POINT\('[^']*',\(([-\d.Ee+]+),([-\d.Ee+]+),([-\d.Ee+]+)\)\)", f.read().replace(' ', '')):
            v = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
            if v == (0.0, 0.0, 0.0):          # 축 놓기 점(원점)은 뺀다
                continue
            xs.append(v[0]); ys.append(v[1]); zs.append(v[2])
    if not xs:
        return None
    return [[round(min(v), 2), round(max(v), 2)] for v in (xs, ys, zs)]


sd = ROOT + '/tools/out/mech_N04/stepout'
for fn in sorted(os.listdir(sd)):
    if fn.endswith('.step'):
        out['step_bbox'][fn] = step_bbox(sd + '/' + fn)

# ---- 1) P_N04_PANEL 허니컴 판(표피 1+1, 심 거리 d 39) ±X 외팔 L 960
d, tf = 39.0, 1.0
q_self, q_mat = 7.60, 12.9                                    # kg/m²
for case, gf, hand, b_eff in (('run', 3.0, 100.0 / 1000.0, None), ('mis', 1.0, 300.0, 500.0)):
    q = (q_self + q_mat) * gf * G * 1e-6                     # N/mm²
    L = 960.0
    m_q = q * L ** 2 / 2                                     # N·mm/mm
    m_h = hand * L if b_eff is None else hand * L / b_eff     # 운전: 폭 1 m 선하중 0.1 N/mm, 오조작: 모서리 집중 300 N, 유효 폭 500
    v = q * L + (hand if b_eff is None else hand / b_eff)
    item('P_N04_PANEL', '±X 외팔 뿌리 표피(기둥 바깥 면, L 960)', case, (m_q + m_h) / (tf * d), 'A5052',
         {'M_Nmm_per_mm': round(m_q + m_h, 1), 'core_shear_MPa': round(v / d, 4), 'core_shear_sf_vs_0.9MPa': round(0.9 / (v / d), 1)})
# 공기실 압력: 표피를 벌리는 평면 인장(심·접착), 판 전체 굽힘 없음(내압)
for case, p in (('run', 338e-6), ('mis', 12e-3)):
    item('P_N04_PANEL', '공기실 압력 → 심 평면 인장(접착)', case, p, 'BOND',
         {'pressure_MPa': p, 'note': '접착 평면 인장 강도 어림 15 MPa를 항복 자리에 씀(임시)'})
# 오조작 손바닥 300 N 국부 눌림
item('P_N04_PANEL', '손바닥 100x100 국부 심 압축', 'mis', 300.0 / 1e4, 'BOND',
     {'note': '허니컴 심 압축 강도 약 1.5 MPa(임시) 대비 SF ' + str(round(1.5 / 0.03, 0))})

# ---- 2) 혀(Y −390~−55, 폭 335, L 1040) → 옮김 띠(X −836~−762.5, 73.5 × d 39 상자) 비틀림 → 목 인서트
W, Lt = 335.0, 1040.0
for case, gf, P in (('run', 3.0, 100.0), ('mis', 1.0, 300.0)):
    q = (q_self + q_mat) * gf * G * 1e-6 * W                  # N/mm
    T = q * Lt ** 2 / 2 + P * Lt                              # N·mm, 혀 뿌리 모멘트 = 옮김 띠·목의 비틀림
    V = q * Lt + P
    # 혀 뿌리 단면(X −762.5, 폭 335) 표피 굽힘
    Lr = Lt - (836 - 762.5)
    m_root = q * Lr ** 2 / 2 + P * Lr
    item('P_N04_PANEL', '혀 뿌리 표피 굽힘(X −762.5, 폭 335)', case, m_root / (tf * d * W), 'A5052', {'M_Nmm': round(m_root)})
    # 옮김 띠: 닫힌 상자 73.5 × 39(표피 1, 홈 벽 마감 t1.5) 브레트 전단 흐름
    A_box = 73.5 * d
    qflow = T / (2 * A_box)
    item('P_N04_PANEL', '옮김 띠 X −836~−762.5 표피 비틀림 전단(목 쪽 끝 Y −390)', case, qflow / tf, 'A5052',
         {'T_Nmm': round(T), 'shear_flow_N_mm': round(qflow, 1)}, shear=True)
    # 목 인서트 A6061 67.5 × 38 직사각 비틀림(b/c 1.78: α 0.239)
    tau = T / (0.239 * 67.5 * 38 ** 2)
    item('P_N04_NECK', '목 인서트 비틀림(단면 67.5×38)', case, tau, 'A6061', {'T_Nmm': round(T)}, shear=True)
    # 목 굽힘(Y 길이 140, 하중 V가 혀 가운데 Y −222에서 → 팔 168 + 140)
    Mx = V * (390 - 222.5) + V * 140
    item('P_N04_NECK', '목 굽힘(Y −530 끝, Z 67.5·38²/6)', case, Mx / (67.5 * 38 ** 2 / 6), 'A6061', {'V_N': round(V, 1)})
    # 목 ↔ 심 접착 면(Y −390·−530 두 면 67.5×38) 비틀림 전단 — 표피가 이어져 있어 실제는 이보다 낮음(보수)
    item('P_N04_NECK', '목 ↔ 판 접착 면 비틀림 전단(67.5×38, 표피 무시)', case, tau, 'BOND', {'note': '접착 전단 강도 어림 15 MPa(임시)'})

# ---- 3) P_N04_SADDLE SUS304 t2: 윗판(132×140, 가운데 Ø126) 다리 2(X −915~−885, t4) 바깥 날개 X −966~−915
cx, cy, r = -900.0, -400.0, 63.0


def flap(pres, xe=-915.0):
    """날개(X < −915, 원 밖) 위 고른 압력 → X −915 선 모멘트. 손바닥 100x100(X −966~−866 쪽) 안 넓이만."""
    F = M = A = 0.0
    n = 200
    for i in range(n):
        x = -966 + (xe + 966) * (i + 0.5) / n
        for j in range(n):
            y = -470 + 140.0 * (j + 0.5) / n
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                continue
            dA = ((xe + 966) / n) * (140.0 / n)
            A += dA; F += pres * dA; M += pres * dA * (xe - x)
    return A, F, M


yh = math.sqrt(r * r - 15 ** 2)
b_sec = 2 * (70 - yh)                         # X −915 단면 판 폭(위아래 띠)
for case, p in (('run', 0.01), ('mis', 0.03)):
    A, F, M = flap(p)
    for t in (2.0, 3.0):
        Z = b_sec * t ** 2 / 6
        item('P_N04_SADDLE' + ('' if t == 2 else '(t3 안)'), '윗판 날개 뿌리 X −915(단면 폭 %.1f, t%g)' % (b_sec, t), case, M / Z, 'SUS304',
             {'flap_area_mm2': round(A), 'F_N': round(F, 1), 'M_Nmm': round(M, 1)})
# 고친 안: 다리 폭 30 → 100(X −950~−850), 날개 뿌리 X −950
yh2 = math.sqrt(r * r - 50 ** 2)
b2 = 2 * (70 - yh2)
for case, p in (('run', 0.01), ('mis', 0.03)):
    A, F, M = flap(p, -950.0)
    item('P_N04_SADDLE(다리 폭 100 안)', '윗판 날개 뿌리 X −950(단면 폭 %.1f, t2)' % b2, case, M / (b2 * 4 / 6), 'SUS304',
         {'flap_area_mm2': round(A), 'F_N': round(F, 1), 'M_Nmm': round(M, 1)})
# 날개 끝 처짐(t2, 오조작) vs 밑 턱(Z −5)과의 틈 3
A, F, M = flap(0.03)
arm = M / F
dl = F * arm ** 3 / (3 * E['SUS304'] * b_sec * 2 ** 3 / 12) * (51 / arm) ** 0
out['saddle_flap_tip_deflect_mis_t2_mm'] = round(F * arm ** 2 * (3 * 51 - arm) / (6 * E['SUS304'] * b_sec * 8 / 12), 3)
# 다리 2개(30 × t4, 높이 129) 옆 힘(Y) — 두 다리 면 밖 굽힘
for case, f in (('run', 30.0), ('mis', 100.0)):
    item('P_N04_SADDLE', '다리 뿌리 면 밖 굽힘(30×t4 ×2, 팔 129)', case, f * 129 / (2 * 30 * 16 / 6), 'SUS304')

# ---- 4) P_N04_TAIL(SUS304 t3, U자) 받침 TAIL_BKT 윗판(X 60~360) 위에 얹힘. −X 끝 X −30~60 외팔 90
def tail_overhang(pres):
    F = M = 0.0
    n = 300
    for i in range(n):
        x = -30 + 100.0 * (i + 0.5) / n          # 손바닥 X −30~70, Y ±50
        if x >= 60:
            continue
        for j in range(n):
            y = -50 + 100.0 * (j + 0.5) / n
            if x < 30 and abs(y) < 46:           # LOWER 따낸 자리
                continue
            dA = (100.0 / n) ** 2
            F += pres * dA; M += pres * dA * (60 - x)
    return F, M


for case, p in (('run', 0.01), ('mis', 0.03)):
    F, M = tail_overhang(p)
    sig_root = M / (104 * 9 / 6)
    item('P_N04_TAIL', '−X 외팔 뿌리 X 60(폭 104, t3)', case, sig_root, 'SUS304', {'F_N': round(F, 1), 'M_Nmm': round(M)})
    # U자 팔 6×t3, X −30~30 외팔 60: 팔 위 손바닥 넓이 Y 46~50 × 60
    fa = p * 4 * 60
    item('P_N04_TAIL', 'U자 팔 뿌리 X 30(6×t3, 외팔 60)', case, fa * 30 / (6 * 9 / 6), 'SUS304', {'F_N': round(fa, 2)})
# TAIL_BKT ㄷ(윗판 80×t3 + 옆벽 2×t3 높이 54, 길이 300): 손 300 N 압축 + 끌림 100 N(Y, Z 0) 옆벽 면 밖
for case, fv, fy in (('run', 100.0, 30.0), ('mis', 300.0, 100.0)):
    sig_c = fv / (2 * 300 * 3)
    sig_b = fy * 57 / (2 * 300 * 9 / 6)
    item('P_N04_TAIL_BKT', '옆벽 압축 + 면 밖 굽힘(끌림, 팔 57)', case, sig_c + sig_b, 'SUS304')

# ---- 5) 꼬리 멈춤 실린더 받침 CYLBKT(SUS304 t2 L) — 세운 판 면 밖 굽힘, 팔 = 실린더 축 → 꺾임(Z −41)
F_cyl = {'run': math.pi / 4 * 16 ** 2 * 0.5, 'mis': math.pi / 4 * 16 ** 2 * 0.7}
for nm, b, arm, mcyl, lcg in (('P_N04_CYLBKT_P/_N', 50.0, 112 - 41.0, 0.354, 70.0), ('P_N04_CYLBKT_A', 40.0, 180 - 41.0, 0.454, 90.0)):
    for case in ('run', 'mis'):
        gf = 3.0 if case == 'run' else 1.0
        Mt = F_cyl[case] * arm
        Mw = mcyl * gf * G * lcg if nm.endswith('_A') else 0.0     # A: 몸이 +X로 매달림 → 같은 판 같은 방향 굽힘. P/N: 축 Y라 무게는 판 면 안
        for t in (2.0, 3.0, 4.0):
            Z = b * t ** 2 / 6
            item(nm + ('' if t == 2 else '(t%g 안)' % t), '세운 판 꺾임 뿌리(폭 %g, 팔 %g, t%g)' % (b, arm, t), case, (Mt + Mw) / Z, 'SUS304',
                 {'F_cyl_N': round(F_cyl[case], 1), 'M_Nmm': round(Mt + Mw)})
        # 날개(판 밑면 체결, 길이 10·8) 지렛대: 볼트가 날개 가운데라 보면 끌어내는 힘 ≈ M / (날개 길이/2 + t)
        lw = 10.0 if not nm.endswith('_A') else 8.0
        out.setdefault('cylbkt_prying_N', {})[nm + ' ' + case] = round((Mt + Mw) / (lw / 2 + 2), 0)
# 고친 안 A: 같은 bbox(X −2010~−2000) 안 통 블록 SUS304 두께 8·10(가공), 판 밑 받침판 60 길이 인서트 줄 간격 50
for t in (8.0, 10.0):
    for case in ('run', 'mis'):
        gf = 3.0 if case == 'run' else 1.0
        M = F_cyl[case] * 139 + 0.454 * gf * G * 90
        item('P_N04_CYLBKT_A(통 블록 t%g 안)' % t, '블록 뿌리(40×t%g, 팔 139)' % t, case, M / (40 * t ** 2 / 6), 'SUS304', {'M_Nmm': round(M)})
        out.setdefault('cylbkt_prying_N', {})['A 블록 + 받침판 인서트 줄 간격 50 ' + case] = round(M / 50, 0)
# 처짐: 세운 판 끝(실린더 축)이 추력으로 밀리는 양(t2, 운전) — 꼬리 멈춤 위치 오차
for nm, b, arm in (('P_N04_CYLBKT_P/_N', 50.0, 71.0), ('P_N04_CYLBKT_A', 40.0, 139.0)):
    out.setdefault('cylbkt_beam', {})[nm] = beam(2.0, b, arm, load=F_cyl['run'], e=E['SUS304'], sy=RP['SUS304'], sf_min=3.0)

# ---- 6) 감개 받침 WIND_BKT(SUS304 t1.5): 세운 판(126 × t1.5, XZ면) 면 밖(Y) 굽힘, 팔 = 발 Z −130 → 드럼 축 Z −80
for case, f, gf in (('run', 20.0, 3.0), ('mis', 100.0, 1.0)):
    wd = 0.211 * gf * G
    M = f * 50.0
    item('P_N04_WIND_BKT', '세운 판 뿌리 면 밖(126×t1.5, 팔 50)', case, M / (126 * 1.5 ** 2 / 6), 'SUS304', {'F_N': f})
    # 볼(72.5 길이 Y, 70 높이, t1.5) 드럼 축 하중 반씩 — 면 안 굽힘(축 Y −510, 뿌리 Y −472.5 팔 37.5)
    fc = math.hypot(f / 2, wd / 2)
    item('P_N04_WIND_BKT', '볼 뿌리 면 안 굽힘(70 높이 × t1.5, 팔 37.5)', case, fc * 37.5 / (1.5 * 70 ** 2 / 6), 'SUS304')

# ---- 7) 보관 안내 STORE(SUS304 t1.5 ㄷ 2층): 바닥판 폭 129 단순 받침 + 턱 10 외팔, 옆벽 매달림 인장
for nm, span, Lst in (('P_N04_STORE_P/_N', 129.0, 600.0), ('P_N04_STORE_A', 109.0, 690.0)):
    for case, gf in (('run', 3.0), ('mis', 1.0)):
        w = 6.5 * gf * G / Lst                       # N/mm(길이 방향)
        m_bot = (w / span) * span ** 2 / 8           # 폭 1 mm 띠
        item(nm, '바닥판 가운데(폭 %g 단순, t1.5)' % span, case, m_bot / (1.5 ** 2 / 6), 'SUS304')
        m_led = (w / 2) * 10.0                       # 턱 끝에 반씩
        item(nm, '가운데 층 턱 뿌리(외팔 10, t1.5)', case, m_led / (1.5 ** 2 / 6), 'SUS304')
        item(nm, '옆벽 매달림 인장(2 × t1.5)', case, (w + 0.0) / (2 * 1.5), 'SUS304')

# ---- 8) 블로어 받침 BLOWER_BASE(SS400 t3, 340×330): 바닥에 얹힘이 기본, 보수로 네 귀 받침 단순 보
for case, gf in (('run', 3.0), ('mis', 1.0)):
    P = 11.0 * gf * G
    M = P * 340 / 8
    item('P_N04_BLOWER_BASE', '네 귀 받침 가정 가운데(보수, 330×t3)', case, M / (330 * 9 / 6), 'SS400')

# ---- 9) 기둥 HFS8-4080-248(구매품, 참고): 압축·X 가속 굽힘
m_move = 81.0
P = m_move * 3 * G / 4
out['post_ref'] = {'axial_N': round(P, 1), 'axial_MPa(A 약 1,500 mm² 임시)': round(P / 1500, 2),
                   'X_accel_bend_MPa(I 1.4e5 약축, c 20)': round(m_move * 2.0 / 4 * 248 * 20 / 1.4e5, 2)}

json.dump(out, open(ROOT + '/fea/results/mech_N04_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
bad = [i for i in out['items'] if not i['ok']]
print('items', len(out['items']), 'not ok', len(bad), 'motion_break', sum(i['motion_break'] for i in out['items']))
for i in out['items']:
    flag = 'BREAK' if i['motion_break'] else ('NG' if not i['ok'] else ('OVER' if i['oversize_3x'] else 'ok'))
    print('%-5s %-22s %-4s %8.2f SF %6.2f  %s' % (flag, i['part'][:22], i['case'], i['stress_MPa'], i['sf'], i['where'][:40]))
print('bbox', json.dumps(out['step_bbox'], ensure_ascii=False))
print('prying', out['cylbkt_prying_N'], 'flapdef', out['saddle_flap_tip_deflect_mis_t2_mm'])
print('cylbeam', {k: (v['deflection_mm'], v['sf']) for k, v in out['cylbkt_beam'].items()})
