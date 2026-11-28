# -*- coding: utf-8 -*-
"""DP-3 해석부 손계산(v2.31.0) — 보 탭 · 끝판 · 관 받침. FEA 못 함 — 환경 없음(D-16). CAD 안 씀.
입력: fea/results/detail_DP-3_stepgeo.json(STEP 형상), tools/out/signatures.json(v2.31.0 질량 · 상자), fea/models.json(고정 · 하중 표).
보는 것
 1) 보 P_M07_BEAM: 끝판을 떼어 끝 단면이 열렸다 = 하중 경로가 바뀐 부품(E-18). 끝 얹힘 넘어짐(표 모델 그대로 · 지금 경간 · 지금 질량 어림 · 모서리 R12 받침),
    열린 끝 단면 찌그러짐(탄성 받침 위 보 유추), 웨브 크리플링, 굽힘 + 구멍 응력 집중, Z 처짐
 2) 이음판 SPLICE_NX · PX: Ø10 머리 구멍 2개 순단면
 3) 덮개 BEAM_CAP(SUS304 t3): 손 100 N 판 굽힘, 탭 물림 3.0의 조임 한도
 4) 관 빗 · 클램프 26품번 A5052 -> PET-CF: 단면 · 볼트 좌면(조임) · 턱
 5) 길이 · 탭이 바뀐 볼트 묶음(handcalc.calc)
실행: python -X utf8 -B fea/cases/detail_DP-3_handcalc.py -> fea/results/detail_DP-3_handcalc.json"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc as bolt
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
GEO = json.load(open(ROOT + '/fea/results/detail_DP-3_stepgeo.json', encoding='utf-8'))
SIG = json.load(open(ROOT + '/tools/out/signatures.json', encoding='utf-8'))
PARTS = SIG['parts']
G = 9.81
E_s, G_s, nu = 205000.0, 79000.0, 0.3
SY = 245.0                       # STKR400 · SS400 (models.json 기준값)
SY_SUS, SY_PET, E_PET = 205.0, 60.0, 5000.0
R = {'_doc': SIG.get('doc'), '_doc_hash': SIG.get('doc_hash')}

# ------------------------------------------------------------------ 1) 보
bb = GEO['P_M07_BEAM']['new']['bbox']
B, D, t = bb[1][1] - bb[1][0], bb[2][1] - bb[2][0], 8.0
ro = max(c['r'] for c in GEO['P_M07_BEAM']['new']['cyl'] if c['axis'] == 'X')        # 바깥 모서리 R(STEP 12 — 실물 미확인 가정값)
ri = min(c['r'] for c in GEO['P_M07_BEAM']['new']['cyl'] if c['axis'] == 'X')
assert (B, D, ro, ri) == (200.0, 400.0, 12.0, 4.0), (B, D, ro, ri)


def hw(z, b, d, r):            # 둥근 모서리 사각형의 반 너비(z = 가운데에서 높이)
    s = d / 2 - abs(z)
    if s < 0: return 0.0
    return b / 2 if s >= r else b / 2 - r + math.sqrt(max(r * r - (r - s) ** 2, 0.0))


def sect(n=40000):
    A = Iy = Iz = 0.0
    dz = D / n
    for i in range(n):
        z = -D / 2 + (i + .5) * dz
        o, c = hw(z, B, D, ro), hw(z, B - 2 * t, D - 2 * t, ri)
        A += 2 * (o - c) * dz; Iy += 2 * (o - c) * z * z * dz; Iz += 2 / 3 * (o ** 3 - c ** 3) * dz
    return A, Iy, Iz


A, Iy, Iz = sect()
rm = (ro + ri) / 2
Am = (B - t) * (D - t) - (4 - math.pi) * rm ** 2
pm = 2 * ((B - t) + (D - t)) - (8 - 2 * math.pi) * rm
J = 4 * Am ** 2 * t / pm
beam_sig = PARTS['U1_FRAME/P_M07_BEAM']
m_beam_now = beam_sig['mass'] / 1000.0
R['1a_section'] = {'B': B, 'D': D, 't': t, 'R_out(STEP, 실물 미확인)': ro, 'R_in': ri, 'A_mm2': round(A, 1), 'Iy_mm4': round(Iy), 'Iz_mm4': round(Iz), 'J_mm4': round(J),
                   '옛 모델(모서리 각짐) A · Iy · Iz': [9344.0, round((B * D ** 3 - (B - 16) * (D - 16) ** 3) / 12), round((D * B ** 3 - (D - 16) * (B - 16) ** 3) / 12)],
                   'm_beam_kg(서명)': round(m_beam_now, 2), 'A x L x 7.85': round(A * (bb[0][1] - bb[0][0]) * 7.85e-6, 2)}

# 받침: 기둥 80160 + 4080 윗면(서명 상자)
pn, pp = PARTS['U1_FRAME/HFS8-80160-1090_M07']['bbox'], PARTS['U1_FRAME/HFS8-80160-1090_M07 (U1_FRAME:1/HFS8-80160-1090_M07:2)']['bbox']
XA, XB = (pn[0] + pn[1]) / 2, (pp[0] + pp[1]) / 2
R['1b_support'] = {'기둥 NX X': pn[:2], '기둥 PX X': pp[:2], '얹힘 Y(80160 + 4080)': [pn[2], PARTS['U1_FRAME/HFS8-4080-1090_M07_NX']['bbox'][3]], '경간': [XA, XB, XB - XA],
                   '표 모델(v2.3.4) 경간': [-2340.0, 1190.0, 3530.0]}
YC = 220.0
# 표 모델 하중(fea/models.json P_M07_BEAM load, v2.3.4): (이름, kg, X, Y)
LOADS_T = [('U3 헤드+매달기', 67.24, 200.0, 0.0), ('U4 묶음', 17.2, -235.0, 0.0), ('U7 롤', 6.5, 670.0, -100.0), ('U8 레귤레이터', 6.0, 800.0, 100.0), ('U5 구동', 4.5, -2220.0, 0.0),
           ('U5 레일', 3.94, -1240.0, 100.0)]
CAR_T = (20.76, (-1930.0, -550.0), 0.0)


def pts_table(gf, car_at):
    p = [(m * G * gf, x, y) for _, m, x, y in LOADS_T]
    p.append((CAR_T[0] * G * gf, car_at, CAR_T[2]))
    return p


def on_beam_bodies():
    """지금 서명 질량 어림: 보에 걸린 바디(유닛 · 높이로 고름) — 무게중심 대신 상자 가운데(어림)."""
    fixed, moving, by = [], [], {}
    for k, v in PARTS.items():
        u = v.get('unit') or k.split('/')[0]
        x0, x1, y0, y1, z0, z1 = v['bbox']; m = (v.get('mass') or 0) / 1000.0
        xc, yc, zc = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
        if m <= 0 or not (-2400 <= xc <= 1500): continue
        take = False
        if u.startswith(('U3_HEAD', 'U4_', 'U5_', 'U6_', 'U7_ROLL_MOUNT')): take = z1 > 5 and zc > 0
        elif u == 'U8_PNEU': take = z0 >= 230 and yc >= -500
        if not take: continue
        by.setdefault(u, [0.0, 0.0, 0.0]); by[u][0] += m; by[u][1] += m * xc; by[u][2] += m * yc
        (moving if u in ('U5_CAR', 'U5_FLOAT', 'U5_LIFT', 'U5_WHEEL') else fixed).append((m, xc, yc))
    summ = {u: {'kg': round(a[0], 2), 'x': round(a[1] / a[0], 1), 'y': round(a[2] / a[0], 1)} for u, a in sorted(by.items())}
    return fixed, moving, summ


FIX, MOV, SUMM = on_beam_bodies()
R['1c_on_beam_now(서명 상자 가운데 어림)'] = {'유닛별': SUMM, '합 kg': round(sum(v['kg'] for v in SUMM.values()), 2), '표 모델 합 kg': round(sum(l[1] for l in LOADS_T) + CAR_T[0], 2),
                                         '고른 법': 'U3_HEAD · U4_* · U5_* · U6_* · U7_ROLL_MOUNT 가운데 테이블 면 위(z_max > 5 · 가운데 > 0) 바디, U8_PNEU는 z_min >= 230 · Y 가운데 >= -500(보 면 · HMI 팔). 달린 몫을 가르지 않은 어림'}


def pts_now(gf, car_shift):
    return [(m * G * gf, x, y) for m, x, y in FIX] + [(m * G * gf, x + car_shift, y) for m, x, y in MOV]


CASES = [('정지 1 g', 1, (), 0.0, 1.0), ('운전 3 g + 끌림 Y 30 N', 3, ((0.0, 200.0, 0.0),), 30.0, 3.0), ('오조작 3 g + 손 500 N + 끌림 Y 100 N', 3, ((500.0, 200.0, -90.0),), 100.0, 2.0)]
FP = 4000.0                                   # D-54 임시 예압(CB5 4 N·m)
F_SEAT, F_SPL = min(2 * FP, 6 * FP * 0.15), 4 * FP * 0.15     # 받침 L(가로 다리 Y 280 CB5-20 x2 당김 / 세로 다리 마찰 6개), 이음판 기둥 쪽 마찰 4개


def ends(pts, gf, xa, xb, m_beam, x_ends, m_end):
    L = xb - xa
    Rb = sum(P * (x - xa) for P, x, _ in pts) / L; Ra = sum(P for P, _, _ in pts) - Rb
    Tb = sum(P * (YC - y) * (x - xa) for P, x, y in pts) / L; Ta = sum(P * (YC - y) for P, _, y in pts) - Tb
    wb = m_beam * G * gf; xc = sum(x_ends) / 2
    Rb += wb * (xc - xa) / L + m_end * G * gf; Ra += wb * (xb - xc) / L + m_end * G * gf
    return Ra, Rb, Ta, Tb


def tipping(model, xa, xb, m_beam, x_ends, m_end, pivot):
    """pivot = 앞 모서리에서 실제 받침 시작까지(0: 표 모델, 12: 바깥 R12 접점 Y 132)"""
    out = {}; L = xb - xa
    for nm, gf, ex, drag, need in CASES:
        worst = None
        for ci, car in enumerate((0, 1)):
            pts = (pts_table(gf, CAR_T[1][car]) if model == 'table' else pts_now(gf, 1380.0 * car)) + list(ex)
            Ra, Rb, Ta, Tb = ends(pts, gf, xa, xb, m_beam, x_ends, m_end)
            Md = drag * 238.0 * (200 - xa) / L
            for end, Rv, T in (('NX', Ra, Ta + drag * 238.0 - Md), ('PX', Rb, Tb + Md)):
                e = T / Rv
                half = 100.0 - pivot
                sf_b = (Rv * half + F_SEAT * (160.0 - pivot) + F_SPL * (200.0 - pivot)) / T
                c = {'끝': end, '대차': '먼 끝(+1380)' if car else 'REST', 'R_N': round(Rv), 'T_Nmm': round(T), 'e_mm': round(e, 1), '받침 반폭': half,
                     '볼트 없이(반폭/e)': round(half / e, 2), '볼트 복원 포함 SF': round(sf_b, 2), '필요': need,
                     '판정': '됨' if sf_b >= need else ('디테일' if sf_b >= 1.2 else '동작'), '기준 대비 %': round((sf_b / need - 1) * 100, 1)}
                if worst is None or c['볼트 복원 포함 SF'] < worst['볼트 복원 포함 SF']: worst = c
        out[nm] = worst
    return out


END_T = 2.34 + 3.63
m_cap = PARTS['U1_FRAME/P_M07_BEAM_CAP']['mass'] / 1000.0 + 4 * 0.00374
END_N = 2.34 + 3.62 + m_cap
xe_now = (bb[0][0], bb[0][1])
R['1d_tipping'] = {
    'A 표 모델 그대로(v2.3.4: 경간 3530 · 보 270.46 kg · 끝판 있음)': tipping('table', -2340.0, 1190.0, 270.46, (-2380.0, 1230.0), END_T, 0.0),
    'B0 표 하중 + DP-3 전 형상(경간 %g · 보 279.14 kg)' % (XB - XA): tipping('table', XA, XB, 279.14, xe_now, END_T, 0.0),
    'B 표 하중 + 지금 형상(보 %.2f kg · 끝판 없음 · 덮개 %.2f kg)' % (m_beam_now, m_cap): tipping('table', XA, XB, m_beam_now, xe_now, END_N, 0.0),
    'C 지금 질량 어림 + 지금 형상': tipping('now', XA, XB, m_beam_now, xe_now, END_N, 0.0),
    'D 지금 질량 어림 + 받침 Y 132부터(바깥 R12)': tipping('now', XA, XB, m_beam_now, xe_now, END_N, ro),
    'E 표 하중 + 받침 Y 132부터': tipping('table', XA, XB, m_beam_now, xe_now, END_N, ro),
    'note': 'SF = (R x 반폭 + 받침 L 3,600 N x 팔 + 이음판 마찰 2,400 N x 팔) / T. 예압 4 kN · μ 0.15는 D-54 임시. C · D의 질량은 서명 상자 가운데 어림이라 판정 근거가 아니라 민감도다'}
# 이음판 기둥 쪽 볼트 4 -> 6이면(마찰 +1,200 N)
_F = F_SPL
F_SPL = 6 * FP * 0.15
R['1d_tipping']['D + 이음판 기둥 쪽 CB5-16 4 -> 6'] = tipping('now', XA, XB, m_beam_now, xe_now, END_N, ro)
F_SPL = _F

# 열린 끝 단면 찌그러짐: 끝 반력이 밑벽 -> 앞 웨브로 들어가 생기는 비틀림 T 가운데 절반이 찌그러뜨리는 몫(M_D = T/2).
# 끝판(가로막)이 없으면 벽 굽힘(틀 강성 K_D = 24 D/(b + d))과 벽 면내 굽힘(I_Dw = b^2 d^2 t (b + d)/96)이 받는다 — 탄성 받침 위 보 유추, 반무한 보 끝 집중 하중.
b_c, d_c = B - t, D - t
Dp = E_s * t ** 3 / (12 * (1 - nu ** 2))
K_D = 24 * Dp / (b_c + d_c)
I_Dw = b_c ** 2 * d_c ** 2 * t * (b_c + d_c) / 96.0
lam = (K_D / (4 * E_s * I_Dw)) ** 0.25
dist = {'틀 강성 K_D_N': round(K_D), 'I_Dw_mm6': '%.4g' % I_Dw, '1/λ_mm': round(1 / lam, 1)}
for key in ('B 표 하중 + 지금 형상(보 %.2f kg · 끝판 없음 · 덮개 %.2f kg)' % (m_beam_now, m_cap), 'C 지금 질량 어림 + 지금 형상'):
    for nm, gf, ex, drag, need in CASES:
        T = R['1d_tipping'][key][nm]['T_Nmm']
        MD = T / 2.0
        gam = 2 * MD * lam / K_D                       # 끝 단면 각 변화 rad
        mc = K_D * gam / 4.0                           # 구석 벽 굽힘 모멘트 N·mm/mm
        s_fr = 6 * mc / t ** 2
        Bm = 0.3224 * MD / lam                         # 찌그러짐 바이모멘트 최대
        s_w = Bm * (b_c * d_c / 8.0) / I_Dw
        s = s_fr + s_w
        dist.setdefault(key[:1], {})[nm] = {'T_Nmm': T, '각 변화 mrad': round(gam * 1000, 3), '앞 · 뒤 웨브 높이 차 mm(γ b/2)': round(gam * b_c / 2, 3),
                                            '벽 굽힘 MPa': round(s_fr, 2), '면내(뒤틀림) MPa': round(s_w, 2), 'SF': round(SY / s, 1), '필요': need}
# 가장 보수: 틀 작용을 얹힘 길이 80 mm 띠가 혼자 받는다(구석 모멘트 T/8)
for k2 in ('B', 'C'):
    Tm = dist[k2]['오조작 3 g + 손 500 N + 끌림 Y 100 N']['T_Nmm']; To = dist[k2]['운전 3 g + 끌림 Y 30 N']['T_Nmm']
    dist[k2]['얹힘 길이 80 띠 혼자(가장 보수)'] = {'운전 MPa · SF': [round(6 * To / 8 / (80 * t * t), 1), round(SY / (6 * To / 8 / (80 * t * t)), 2)],
                                          '오조작 MPa · SF': [round(6 * Tm / 8 / (80 * t * t), 1), round(SY / (6 * Tm / 8 / (80 * t * t)), 2)]}
# 바늘점 Y: 끌림이 더하는 찌그러짐 몫(각 변화 / 2 x 팔 438)
for F in (30.0, 100.0):
    dT = F * 238.0 * (200 - XA) / (XB - XA)
    g2 = 2 * (dT / 2) * lam / K_D
    dist['바늘점 Y 더해지는 몫 mm(끌림 %d N)' % F] = round(g2 / 2 * 438.0, 4)
dist['note'] = '끝판이 있던 v2.30.8까지는 끝 단면이 가로막으로 묶여 이 항이 0이었다(표 모델에 없던 항). 덮개(t3, 틈 0.2, M5 x4)는 가로막으로 세지 않았다'
R['1e_open_end_distortion'] = dist

# 웨브 크리플링: 편심이 커서 앞 웨브 한 장이 다 받는다고 봄(AISC J10-3a 꼴, 끝판 없음)
Nb = 80.0
Rn_web = 0.40 * t ** 2 * (1 + 3 * (Nb / D)) * math.sqrt(E_s * SY)
Rmax = max(v['R_N'] for k, vv in R['1d_tipping'].items() if isinstance(vv, dict) and k[:1] in 'BC' for v in vv.values())
R['1f_web_crippling'] = {'Rn_웨브 1장_N': round(Rn_web), 'R_end_max_N': Rmax, 'SF(앞 웨브 1장)': round(Rn_web / Rmax, 1), 'note': '과사양 아님 — 단면은 강성 · 탭 물림 8이 정함'}


# 굽힘 응력 + 새 구멍 응력 집중, Z 처짐(표 하중, 지금 경간)
def dp(P, xp, x, EI, xa=XA, xb=XB):
    L = xb - xa; a = xp - xa; bq = L - a; xx = x - xa
    if xx <= a: return P * bq * xx * (L ** 2 - bq ** 2 - xx ** 2) / (6 * L * EI)
    return P * a * (L - xx) * (L ** 2 - a ** 2 - (L - xx) ** 2) / (6 * L * EI)


def mom(pts, gf, xs):
    L = XB - XA
    Ra = sum(P for P, _, _ in pts) - sum(P * (x - XA) for P, x, _ in pts) / L + m_beam_now * G * gf / 2
    w = m_beam_now * G * gf / (xe_now[1] - xe_now[0])
    return Ra * (xs - XA) - sum(P * (xs - x) for P, x, _ in pts if x < xs) - w * (xs - XA) ** 2 / 2


st = {}
for key, fn in (('표 하중', lambda gf, c: pts_table(gf, CAR_T[1][c])), ('지금 질량 어림', lambda gf, c: pts_now(gf, 1380.0 * c))):
    for nm, gf, ex, drag, need in CASES[1:]:
        best = 0.0
        for c in (0, 1):
            pts = fn(gf, c) + list(ex)
            for xs in [q[1] for q in pts if XA < q[1] < XB] + [(XA + XB) / 2]:
                best = max(best, mom(pts, gf, xs))
        My = drag * (200 - XA) * (XB - 200) / (XB - XA)
        Tm = max(R['1d_tipping']['B 표 하중 + 지금 형상(보 %.2f kg · 끝판 없음 · 덮개 %.2f kg)' % (m_beam_now, m_cap) if key == '표 하중' else 'C 지금 질량 어림 + 지금 형상'][nm]['T_Nmm'], 1)
        tau = Tm / (2 * Am * t)
        s = best / (Iy / (D / 2)) + My / (Iz / (B / 2))
        seq = math.sqrt(s ** 2 + 3 * tau ** 2)
        st[key + ' / ' + nm] = {'M_Nmm': round(best), 'σ_eq_MPa': round(seq, 2), 'SF(전체 단면)': round(SY / seq, 1), '구멍 Kt 3 SF': round(SY / (3 * seq), 1), '필요': need}
R['1g_beam_stress'] = st
EIv = E_s * Iy
w1 = m_beam_now * G / (xe_now[1] - xe_now[0])
defl = {}
for x in (0.0, 200.0):
    n = 400; dx = (XB - XA) / n
    d0 = sum(dp(w1 * dx, XA + (i + .5) * dx, x, EIv) for i in range(n)) + sum(dp(P, xp, x, EIv) for P, xp, _ in pts_table(1, CAR_T[1][0]))
    d1 = sum(dp(w1 * dx, XA + (i + .5) * dx, x, EIv) for i in range(n)) + sum(dp(P, xp, x, EIv) for P, xp, _ in pts_now(1, 0.0) if XA < xp < XB)
    defl['X %d' % x] = {'1 g 표 하중': round(d0, 4), '1 g 지금 질량 어림': round(d1, 4), '표 모델 값(v2.3.4)': {0.0: 0.0487, 200.0: 0.0435}[x]}
R['1h_beam_deflection_Z_mm'] = defl

# ------------------------------------------------------------------ 2) 이음판
sp = GEO['P_M07_SPLICE_NX']['new']
W, tp = sp['size'][0], sp['size'][1]
h10 = [c for c in sp['cyl'] if c['r'] == 5.0]
edge = min(abs(c['center'][0] - sp['bbox'][0][0]) for c in h10)
Fz = F_SPL; arm = 100.0                               # 보 쪽 볼트 줄 X -2240 <-> 기둥 쪽 X -2340
half = Fz / 2
An = (W - 10.0) * tp
In = tp * W ** 3 / 12 - (tp * 10.0 ** 3 / 12 + tp * 10.0 * (W / 2 - edge) ** 2)
s_n = half / An + half * arm * (W / 2) / In
R['2_splice'] = {'판': [W, tp, sp['size'][2]], 'Ø10 구멍': [c['center'] for c in h10], '구멍 가운데 -> 판 끝': edge, '구멍 가장자리 -> 판 끝 살': edge - 5.0,
                 '하중': '넘어짐 복원 마찰 2,400 N(위 줄 Z 600 볼트 몫 1,200 N이 Z 350 · 550 단면을 지남) + 줄 어긋남 100',
                 '순단면 MPa': round(s_n, 2), 'x Kt 3 MPa': round(3 * s_n, 2), 'SF': round(SY / (3 * s_n), 1), '전체 단면(구멍 없음) MPa': round(half / (W * tp) + half * arm * 6 / (tp * W ** 2), 2),
                 'note': '판 두께 6은 넘어짐 볼트 줄 강성 · 머리 구멍 깊이(머리 5 + 1)가 정함. 구멍 2개가 SF를 %.0f %% 낮춤' % ((1 - (half / (W * tp) + half * arm * 6 / (tp * W ** 2)) / s_n) * 100)}

# ------------------------------------------------------------------ 3) 덮개
cp = GEO['P_M07_BEAM_CAP']['new']
tc = 3.0
span = cp['size'][1] - 2 * tc                          # 플랜지 안쪽 너비
Mh = 100.0 * span / 4.0
beff = 20.0 + 0.6 * span                               # 한 방향 판의 점 하중 유효 폭(손 20 + 0.6 L)
s3 = 6 * Mh / (beff * tc ** 2); s2 = 6 * Mh / (beff * 2.0 ** 2)
Ic = beff * tc ** 3 / 12
R['3_cap'] = {'웹': [cp['size'][1], cp['size'][2], tc], '경간(플랜지 사이, 단순 받침 보수)': span, '유효 폭': round(beff, 1), '손 100 N 가운데': {'t3 MPa · SF': [round(s3, 1), round(SY_SUS / s3, 2)], 't2 MPa · SF': [round(s2, 1), round(SY_SUS / s2, 2)],
              '처짐 t3 mm': round(100.0 * span ** 3 / (48 * 193000.0 * Ic), 3)},
              '자중 3 g 볼트 전단 N/개': round(m_cap * G * 3 / 4, 1), '손 100 N 볼트 전단 N/개': 25.0, '받음 MPa(나사 Ø5 x t3)': round(25.0 / 15.0, 2),
              '과사양(M-09)': 't3 손 SF %.1f >= 2 x 3 = 6 이지만 두께는 M-04 판 탭 t >= 피치 x 3 = 2.4가 정함(t2는 탭 불가 -> 너트 필요). 줄이지 않는다' % (SY_SUS / s3)}
cap_t = {}
for tq in (4.5, 3.0, 2.0, 1.5, 1.0):
    c = bolt(d=5, le=3.0, load=25.0, torque=tq, base='SUS304', dw=8.5, dh=5.5, sf_min=2.0)
    cap_t['%.1f N·m' % tq] = {'예압 N': c['preload_N'], '조임 암나사 전단': c['sf_tightening']['조임 암나사 전단'], '운전 암나사 전단': c['sf_operating']['암나사 전단']}
ath3 = math.pi * 5 * 3.0 * 0.375
cap_t['암나사 전단 한도 N'] = round(0.6 * SY_SUS * ath3, 0); cap_t['SF 1.0 토크 N·m'] = round(0.6 * SY_SUS * ath3 * 0.2 * 5 / 1000, 2)
cn = bolt(d=5, le=4.5, load=25.0, torque=2.0, base='SUS304', sf_min=2.0)
cap_t['클린칭 너트 물림 4.5(SUS, 형번 미정)에 2.0 N·m'] = cn['sf_tightening']['조임 암나사 전단']
R['3_cap']['탭 물림 3.0 조임'] = cap_t

# ------------------------------------------------------------------ 4) 관 빗 · 클램프 PET-CF
F_MIS = 50.0
pet = {}


def comb(name, top_z, n_low):
    g = GEO[name]['new']; y0, y1 = g['bbox'][1]; zroot = 650.1
    Ly = y1 - y0
    # Z 660 단면(관 구멍 3줄 + 자리파기 Ø9.5가 지남): X 굽힘(두께 16)
    Inet = ((Ly - n_low * 6.5 - 9.5) * 16 ** 3 + 9.5 * (16 ** 3 - 9.5 ** 3)) / 12.0
    Mx = F_MIS * (top_z - 660.0)
    s = Mx * 8.0 / Inet
    T = F_MIS * (top_z - 650.0) / 8.0                 # 볼트 당김(블록 옆 모서리 받침, 반폭 8)
    Tz = F_MIS * (197.0 - 130.0) / (197.0 - 166.0)    # 위로 당김: 뒤 끝 Y 197 받침
    return {'상자 Y': [y0, y1], '관 구멍 단면(Z 660) I_net': round(Inet), 'X 당김 50 N 굽힘 MPa': round(s, 2), 'SF(PET-CF 60)': round(SY_PET / s, 1),
            '옛(A5052 195, 전체 단면 73 x 16)': round(195.0 / (F_MIS * 48 / (73 * 16 ** 2 / 6)), 1), '볼트 당김 N(X 당김)': round(T, 1), '볼트 당김 N(Z 당김)': round(Tz, 1),
            '윗끝 X 처짐 mm': round(F_MIS * (top_z - 650.0) ** 3 / (3 * E_PET * Ly * 16 ** 3 / 12), 3)}


pet['COMB_ML_1~6·9(높이 47~48, 관 8)'] = comb('P_M08_TUBE_COMB_ML_5', 698.0, 3)
pet['COMB_ML_7(높이 68 — 가장 불리)'] = comb('P_M08_TUBE_COMB_ML_7', 718.0, 2)
pet['COMB_ML_8 · U5_1 · U5_2(관 2)'] = comb('P_M08_TUBE_COMB_ML_8', 698.0, 0)
# CLAMP_F(24 x 18 x 50, 볼트 2 Z 462, 관 Z 430 · 440), CLAMP_L(24 x 18 x 32~52, 볼트 Z 296/276, 관 Z 262 · 280), SO_1(외팔 67), SO_2(판 t8 폭 20 외팔 38)
def clampF(zb, ztop, zh):
    M = F_MIS * (zb - zh)
    s = M * 9.0 / (5.0 * 18 ** 3 / 12)                 # 볼트 줄 단면: 자리파기 2개 사이 · 옆 살 5만(보수)
    return {'볼트 줄 단면 MPa(-Y 당김)': round(s, 2), 'SF': round(SY_PET / s, 1), '볼트 당김 N/개': round(F_MIS * (ztop - zh) / (ztop - zb) / 2, 1)}


pet['CLAMP_F_1~6'] = clampF(462.0, 470.0, 430.0)
pet['CLAMP_L_2(높이 52 — L 가운데 가장 불리)'] = clampF(296.0, 304.0, 262.0)
Zs = 38 * 16 ** 2 / 6; s = F_MIS * 67 / Zs
pet['CLAMP_SO_1'] = {'블록 뿌리 MPa': round(s, 2), 'SF': round(SY_PET / s, 1), '옛 A5052': 94.38, '볼트 당김 N/개': 167.5, '끝 처짐 mm': round(F_MIS * 67 ** 3 / (3 * E_PET * 38 * 16 ** 3 / 12), 3)}
Zs2 = (20 - 6.5) * 8 ** 2 / 6; s = F_MIS * 38 / Zs2
pet['CLAMP_SO_2 · SO_3(판 t8 폭 20, 외팔 38)'] = {'뿌리 MPa': round(s, 2), 'SF': round(SY_PET / s, 2), '옛 A5052': 14.78, '필요': 2.0,
                                              '층간(0.5배 30 MPa)로 보면': round(30.0 / s, 2), '끝 처짐 mm': round(F_MIS * 38 ** 3 / (3 * E_PET * (20 - 6.5) * 8 ** 3 / 12), 2)}
# 턱: Y 120.2~123.8(살 3.6), 높이 3.1, 폭 16. 볼트 축 Y 166 둘레로 돌면 턱 구석(X ±8)이 보 모서리에 닿는다 -> 팔 8
lip_t, lip_h, lip_w = 3.6, 3.1, 6.2                    # 구석 점 접촉의 유효 폭 = 2 x 높이(가정)
Zl = lip_w * lip_t ** 2 / 6
Ncap = SY_PET * Zl / lip_h
pet['턱(돌림 막음)'] = {'살 · 높이 · 유효 폭(가정 2h)': [lip_t, lip_h, lip_w], '구석 접촉 힘 한도 N(항복)': round(Ncap, 1), '막는 토크 한도 N·mm(팔 8)': round(Ncap * 8),
                    '관 X 당김 50 N이 주는 토크 N·mm(관 Y 130, 볼트 Y 166)': 50 * 36,
                    '턱 혼자(볼트 풀림) SF': round(Ncap * 8 / (50 * 36), 2),
                    '머리 마찰 토크(조임 토크의 절반)를 턱이 혼자 받을 때 SF': {'4.5 N·m': round(Ncap * 8 / 2250, 2), '2.0 N·m': round(Ncap * 8 / 1000, 2), '1.5 N·m': round(Ncap * 8 / 750, 2)},
                    '밑면 마찰 토크 N·mm(예압 x μ 0.15 x 반지름 20 어림)': {'1.5 N·m': round(1500 * 0.15 * 20), '2.0 N·m': round(2000 * 0.15 * 20)},
                    'note': '조이는 동안에는 밑면 마찰 반지름(약 20)이 머리 마찰 반지름(3.5)보다 커서 빗이 돌지 않는다 — 턱은 처음 자리 잡기와 볼트가 풀렸을 때만 받는다. 유효 폭 · 마찰 반지름은 가정(FEA 대기)'}
R['4_pet_cf_parts'] = pet

# 좌면: 머리 Ø8.5 / 구멍 Ø5.5 = 33.0 mm2, PET-CF 한계면압 60(handcalc 표)
seat = {}
for lbl, dw in (('머리 바로(Ø8.5)', 8.5), ('소형 평와셔 Ø9(자리파기 Ø9.5 안)', 9.0), ('평와셔 Ø10(자리파기 없는 SO)', 10.0)):
    ab = math.pi / 4 * (dw ** 2 - 5.5 ** 2)
    seat[lbl] = {'넓이 mm2': round(ab, 1), '한도 N': round(60 * ab), 'SF 1.0 토크 N·m': round(60 * ab * 0.2 * 5 / 1000, 2),
                 '좌면 SF': {'%.1f N·m' % tq: round(60 * ab / (tq * 1000 / (0.2 * 5)), 2) for tq in (4.5, 3.0, 2.0, 1.5)}}
seat['A5052였을 때(210 MPa) 4.5 N·m'] = round(210 * math.pi / 4 * (8.5 ** 2 - 5.5 ** 2) / 4500, 2)
seat['볼트 수'] = {'관 빗 CB5-20': 11, 'CLAMP_F CB5-16': 12, 'CLAMP_L CB5-16': 12, 'CLAMP_SO CB5-16': 6, '합': 41}
R['4b_pet_cf_seat'] = seat

# ------------------------------------------------------------------ 5) 볼트 묶음(E-19: 묶음 안 가장 큰 하중 하나)
TQ4 = 2.2          # M4: M5 4.5 N·m와 같은 나사 응력(4500 x 8.78/14.2 = 2,782 N) -> 2.2 N·m (요구서에 조임 토크 표 없음, 임시)
reg_T = 100.0 * (120.0 - 51.5) / (536.3 - 527.8) / 2   # 손 100 N 위로, 게이지 앞 Y 51.5, 받침 윗끝 Z 536.3 받침
GR = [
 ('관 빗 CB5-20 x11 -> 보 윗벽 탭(4.5 N·m 관례)', dict(d=5, le=8.0, load=pet['COMB_ML_7(높이 68 — 가장 불리)']['볼트 당김 N(X 당김)'], torque=4.5, base='SS400', sf_min=2.0), 'PET-CF'),
 ('관 빗 CB5-20 x11 (1.5 N·m 지정)', dict(d=5, le=8.0, load=pet['COMB_ML_7(높이 68 — 가장 불리)']['볼트 당김 N(X 당김)'], torque=1.5, base='SS400', sf_min=2.0), 'PET-CF'),
 ('CLAMP_F · L CB5-16 x24 -> 보 앞벽 탭(1.5 N·m 지정)', dict(d=5, le=8.0, load=pet['CLAMP_L_2(높이 52 — L 가운데 가장 불리)']['볼트 당김 N/개'], torque=1.5, base='SS400', sf_min=2.0), 'PET-CF'),
 ('CLAMP_SO CB5-16 x6 -> 보 앞벽 탭(1.5 N·m 지정)', dict(d=5, le=8.0, load=167.5, torque=1.5, base='SS400', sf_min=2.0), 'PET-CF'),
 ('HMI 받침 CB5-20 x4 -> 보 앞벽 새 탭', dict(d=5, le=8.0, load=240.0, torque=4.5, base='SS400', sf_min=3.0), 'A5052'),
 ('LBRK_R3 CB5-14 x1 -> 보 앞벽 새 탭', dict(d=5, le=8.0, load=146.0, torque=4.5, base='SS400', sf_min=2.0), 'SUS304'),
 ('레귤레이터 CB4-12 x6 -> 보 앞벽 새 탭', dict(d=4, le=8.0, load=round(reg_T, 1), torque=TQ4, base='SS400', dw=7.0, dh=4.5, sf_min=2.0), 'SS400'),
 ('매니폴드 CB4-30 x4 -> 보 앞벽 탭', dict(d=4, le=8.0, load=100.0, torque=TQ4, base='SS400', dw=7.0, dh=4.5, sf_min=2.0), 'A5052'),
 ('덮개 CB5-12 x8 -> 덮개 플랜지 탭 t3(1.5 N·m 지정)', dict(d=5, le=3.0, load=25.0, torque=1.5, base='SUS304', sf_min=2.0), 'SS400'),
]
rows = {}
for nm, kw, seat_mat in GR:
    c = bolt(**kw)
    # 좌면은 머리가 앉는 쪽 재질로 다시(handcalc는 base 하나로 좌면 · 암나사를 같이 봄)
    from handcalc import BASE
    dw = kw.get('dw', 8.5); dh = kw.get('dh', 5.5)
    seat_sf = BASE[seat_mat][1] * math.pi / 4 * (dw ** 2 - dh ** 2) / c['preload_N']
    rows[nm] = {'물림': kw['le'], '물림/d': c['engage_ratio'], '외력 N': kw['load'], '조임 N·m': kw['torque'], '예압 N': c['preload_N'], '운전': c['sf_operating'],
                '조임 볼트 응력': c['sf_tightening']['조임 볼트 응력'], '조임 암나사 전단': c['sf_tightening']['조임 암나사 전단'], '좌면(%s)' % seat_mat: round(seat_sf, 2),
                '기준': kw['sf_min'], 'M-01 1.5d': kw['le'] >= 1.5 * kw['d']}
R['5_bolts'] = rows
R['5_note'] = {'M4 조임 토크': 'M5 4.5 N·m와 같은 나사 응력 -> 2.2 N·m(임시)', '레귤레이터 손 100 N': '게이지 앞 Y 51.5에서 위로, 받침 윗끝 Z 536.3 받침(팔 8.5) -> 볼트 %.0f N/개' % reg_T,
               'HMI 240 N · LBRK 146 N': 'detail_2026-11-28_handcalc.json 값 그대로(하중 · 받침 그대로, 물림만 6 -> 8)'}

json.dump(R, open(ROOT + '/fea/results/detail_DP-3_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, json.dumps(v, ensure_ascii=False)[:420])
