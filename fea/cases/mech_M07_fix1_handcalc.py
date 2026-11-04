# -*- coding: utf-8 -*-
"""M07 수정 1회차 모델링부 넘기기 전 손계산(E-22) — v2.3.4 (보를 기둥 위에 얹음, 볼트 CB5-20/16).
FEA 환경 없음(D-16) -> 손계산만. 하중·임시값은 mech_M07_handcalc.py(v2.3.3 해석부)와 같다:
걸린 질량 x 3 g, 끌림 30/100 N(D-79·D-08 임시), 오조작 손 500 N @ X 200, D-54(HNTT8-5 + CB5 4 N·m -> 예압 4 kN, μ 0.15).
바뀐 것: 보 X -2380~1230(3,610, 끝판 t8 2장, CAD 270.46 kg), 지지 = 기둥 윗면 얹힘(단순 지지 경간 = 기둥 중심 X -2340 ~ 1190, 3,530 보수),
기둥 L1090(Z -840~250), 받침 세로 다리 CB5-20 물림 8.5, 이음판 4080 쪽 CB5-16 물림 7.5(Z 175·220).
"""
import json, math, os
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
E_s, G_s, E_a = 205000.0, 79000.0, 70000.0
SY_SS400, SY_STKR, SY_AL = 245.0, 245.0, 160.0      # 알루미늄 6063-T5 내력 임시(형재)
SF_OP, SF_MIS = 3.0, 2.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'


B, D, t = 200.0, 400.0, 8.0
A = B * D - (B - 2 * t) * (D - 2 * t)
Iy = (B * D**3 - (B - 2 * t) * (D - 2 * t)**3) / 12
Iz = (D * B**3 - (D - 2 * t) * (B - 2 * t)**3) / 12
Am = (B - t) * (D - t); pm = 2 * ((B - t) + (D - t)); J = 4 * Am**2 * t / pm
m_beam = 270.46
L_beam = 3610.0
xa, xb = -2340.0, 1190.0          # 기둥 중심(얹힘 길이 80의 가운데) — 단순 지지 보수
L = xb - xa
w_self = m_beam * G / L_beam
R['1_beam'] = {'A': round(A), 'Iy': round(Iy), 'Iz': round(Iz), 'L_beam': L_beam, 'L_span(기둥 중심)': L, 'mass_kg': m_beam}

loads = {'U3 윗헤드 + 매달기': (67.24, 200.0), 'U4 묶음': (17.2, -235.0), 'U7 롤 걸이 + 롤': (6.5, 670.0),
         'U8 레귤레이터': (6.0, 800.0), 'U5 구동': (4.5, -2220.0)}
m_rail, rail_x = 3.94, (-2140.0, -340.0)
m_car = 29.2 - 3.94 - 4.5
car_x = (-1930.0, -550.0)
m_seat, m_splice = 2.34, 3.63


def reactions(gf, extra_P=(), car_at=-1930.0):
    pts = [(m * G * gf, x) for m, x in loads.values()]
    pts.append((m_car * G * gf, car_at))
    pts.append((m_rail * G * gf, sum(rail_x) / 2))
    pts += list(extra_P)
    Rb = sum(P * (x - xa) for P, x in pts) / L
    Ra = sum(P for P, _ in pts) - Rb
    wb = m_beam * G * gf
    xc = (-2380 + 1230) / 2
    Rb += wb * (xc - xa) / L; Ra += wb * (xb - xc) / L
    Ra += (m_seat + m_splice) * G * gf; Rb += (m_seat + m_splice) * G * gf
    return Ra, Rb, pts


cases = {}
for nm, gf, extra in [('정지 1 g', 1, ()), ('운전 3 g', 3, ()), ('오조작 3 g + 손 500 N @X 200', 3, ((500.0, 200.0),))]:
    best = None
    for cx in car_x:
        Ra, Rb, _ = reactions(gf, extra, cx)
        cand = (max(Ra, Rb), Ra, Rb, cx)
        best = cand if best is None or cand[0] > best[0] else best
    cases[nm] = {'R_NX_N': round(best[1]), 'R_PX_N': round(best[2]), 'R_max_N': round(best[0]), 'car_X': best[3]}
R['2_end_reactions'] = cases

# ---- 보 끝 얹힘: 양의 받침(미끄러짐 하중 길 없음) ----
# 보 밑벽(t8)이 기둥 윗면 80 x 200에 닿는다. 웨브 국부 항복(AISC J10-2 꼴): R / (2 t (N + 2.5 k)), N 80, k = t + R12 = 20
Nb, kk = 80.0, 20.0
brg = {}
for cn, cv in cases.items():
    Rm = cv['R_max_N']
    s_web = Rm / (2 * t * (Nb + 2.5 * kk))
    A_col = 5000.0 + 1115.0          # 80160 임시 단면 + 4080 단면(실물 1,215,782 mm3 / 1090)
    s_col = Rm / A_col
    need = SF_MIS if '오조작' in cn else SF_OP
    brg[cn] = {'R_N': Rm, '웨브 국부 응력_MPa': round(s_web, 2), 'SF_web': round(SY_STKR / s_web, 0),
               '기둥 윗면 지압_MPa': round(s_col, 2), 'SF_col': round(SY_AL / s_col, 0), 'verdict': verdict(min(SY_STKR / s_web, SY_AL / s_col), need)}
R['3_end_bearing'] = brg

# 들림(위로 미는 힘) 확인: 누름 U4 100 N + U5 90 N 위로 vs 보 끝 정하중
up = 100.0 + 90.0
R['4_uplift'] = {'up_N(누름 반력 합, 한 끝이 다 받는 보수)': up, 'R_min_1g_N': round(min(cases['정지 1 g']['R_NX_N'], cases['정지 1 g']['R_PX_N'])),
                 'margin': round(min(cases['정지 1 g']['R_NX_N'], cases['정지 1 g']['R_PX_N']) / up, 1), 'note': '끝 반력이 늘 아래 -> 들림 없음. 볼트는 가로 묶음만'}

# ---- 끝 체결 볼트(가로 묶음, 예압) — 고친 물림 ----
Fp, mu, p_M5 = 4000.0, 0.15, 0.8


def nut_cap(engage):
    if engage < p_M5: return 0.0
    return math.pi * 5.0 * engage * 0.75 * 0.58 * 245.0


bolts = {'받침 세로 CB5-20 + HNTT8-5 (끝마다 6)': (8.5, 6), '이음판 4080 쪽 CB5-16 + HNTT8-5 (끝마다 4)': (7.5, 4)}
bt = {}
clamp = 0.0
for k, (e, n) in bolts.items():
    cap = nut_cap(e)
    pre = min(Fp, cap / 1.2)
    clamp += n * pre
    bt[k] = {'engage_mm': e, '1.5d': 7.5, '나사 벗겨짐 하중_N': round(cap), '예압_N': round(pre), 'SF_strip(예압 4 kN)': round(cap / Fp, 2), 'verdict': verdict(cap / Fp, SF_MIS)}
Fx = m_car * 2.0 + 30.0              # 대차 가속 2 m/s2 + 끌림 30 N(X)
Fy = 100.0                           # 오조작 끌림 Y
lat_cap = mu * (clamp + cases['정지 1 g']['R_max_N'] * 0)   # 얹힘 마찰은 보수로 뺌
bt['가로 미끄럼(끝마다)'] = {'clamp_N': round(clamp), 'cap_N(μ0.15)': round(lat_cap), 'F_X_N': round(Fx, 1), 'F_Y_N': Fy,
                       'SF': round(lat_cap / max(Fx, Fy), 1), 'verdict': verdict(lat_cap / max(Fx, Fy), SF_MIS)}
R['5_end_bolts'] = bt

# ---- 보 굽힘·비틀림 응력(3 g) ----
Zy = Iy / (D / 2); Zz = Iz / (B / 2)


def Mmax_beam(gf, extra=()):
    best = 0
    for cx in car_x:
        Ra, Rb, pts = reactions(gf, extra, cx)
        Ra -= (m_seat + m_splice) * G * gf
        for xs in [p[1] for p in pts] + [xa + L / 2]:
            M = Ra * (xs - xa) - sum(P * (xs - x) for P, x in pts if x < xs) - w_self * gf * (xs - xa)**2 / 2
            best = max(best, M)
    return best


for nm, gf, extra, need, Fyy in [('운전 3 g + 끌림 30 N', 3, (), SF_OP, 30.0), ('오조작 3 g + 손 500 N + 끌림 100 N', 3, ((500.0, 200.0),), SF_MIS, 100.0)]:
    M = Mmax_beam(gf, extra)
    My = Fyy * (200 - xa) * (xb - 200) / L
    T = Fyy * (450.0 - 12.0)
    tau = T / (2 * Am * t)
    s = M / Zy + My / Zz
    seq = math.sqrt(s**2 + 3 * tau**2)
    R[f'6_beam_stress {nm}'] = {'M_Nmm': round(M), 'sigma_MPa': round(s, 2), 'SF': round(SY_STKR / seq, 1), 'need': need, 'verdict': verdict(SY_STKR / seq, need)}

# ---- 보 처짐·바늘점 흔들림(1 g, 기록 — 6-2 미정 D-08) ----
EIv = E_s * Iy


def dp(P, xp, x, EI):
    a = xp - xa; b = L - a; xx = x - xa
    if xx <= a: return P * b * xx * (L**2 - b**2 - xx**2) / (6 * L * EI)
    return P * a * (L - xx) * (L**2 - a**2 - (L - xx)**2) / (6 * L * EI)


def dudl(w, x, EI, x0=xa, x1=xb, n=400):
    dx = (x1 - x0) / n
    return sum(dp(w * dx, x0 + (i + .5) * dx, x, EI) for i in range(n))


old = json.load(open(f'{ROOT}/fea/results/mech_M07_handcalc.json', encoding='utf-8')).get('4_beam_deflection_mm', {})
d = {}
for x in (0.0, 200.0):
    st = dudl(w_self, x, EIv) + dudl(m_rail * G / 1800, x, EIv, *rail_x) + sum(dp(m * G, xp, x, EIv) for m, xp in loads.values())
    st += dp(m_car * G, car_x[0], x, EIv)
    o = old.get(f'X {int(x)}', {}).get('정하중 처짐_1g')
    d[f'X {int(x)}'] = {'정하중 처짐_1g': round(st, 4), 'v2.3.3': o, '증가_%': round((st / o - 1) * 100, 1) if o else None,
                        '대차 X 0->1380 변화': round(dp(m_car * G, car_x[1], x, EIv) - dp(m_car * G, car_x[0], x, EIv), 5),
                        'U4 누름 100 N 변화': round(-dp(100.0, -235.0, x, EIv), 5)}
R['7_beam_deflection_mm'] = d

# ---- 기둥 압축·좌굴(L1090, 외팔 보수) ----
Ic_w = 420e4
Pc = cases['오조작 3 g + 손 500 N @X 200']['R_max_N'] + 31.91 * G * 3
Pcr = math.pi**2 * E_a * Ic_w / (2.0 * 1090.0)**2
R['8_column'] = {'P_N': round(Pc), 'sigma_MPa': round(Pc / 5000.0, 2), 'Pcr_cantilever_N': round(Pcr), 'SF_buckling': round(Pcr / Pc, 0)}

os.makedirs(f'{ROOT}/fea/results', exist_ok=True)
json.dump(R, open(f'{ROOT}/fea/results/mech_M07_fix1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, json.dumps(v, ensure_ascii=False)[:420])
