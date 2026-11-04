# -*- coding: utf-8 -*-
"""M07 해석 2회차(해석부) — v2.3.4: 보를 기둥 윗면에 얹음(L3610, 끝판 t8), 기둥 L1090, CB5-20/16.
FEA 환경 없음(D-16) -> 손계산. 모델링부 넘기기 전 손계산(mech_M07_fix1_handcalc.py)과 독립으로 다시 세운다.
새로 보는 것: (1) STEP bbox로 형상 확인, (2) 끝 얹힘 면의 비틀림 편심(헤드가 보 앞 Y 0에 매달림) -> 합력이 받침면 안인지,
(3) 웨브 국부 크리플링(AISC J10-3 꼴), (4) 바늘점 Y·X 흔들림을 새 지지(기둥 윗끝 Z 250, 받침틀 묶음 Z -250, 높이 500)로 다시,
(5) 보 처짐(1 g) 다시. 하중·임시값은 v2.3.3 해석부와 같다(D-54, D-79, D-08, D-107).
"""
import json, math, os, re
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
E_s, G_s, E_a = 205000.0, 79000.0, 70000.0
SY = 245.0
SY_AL = 160.0
R = {}

# ---- 1) STEP bbox (CARTESIAN_POINT 전체) ----
def bbox(p):
    txt = open(p, encoding='utf-8', errors='ignore').read()
    pts = re.findall(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)", txt)
    xs = [tuple(map(float, q)) for q in pts]
    lo = [round(min(v[i] for v in xs), 2) for i in range(3)]
    hi = [round(max(v[i] for v in xs), 2) for i in range(3)]
    return {'n_pts': len(xs), 'min': lo, 'max': hi}

sd = f'{ROOT}/tools/out/mech_M07/stepout'
R['1_step_bbox'] = {f: bbox(f'{sd}/{f}') for f in ('P_M07_BEAM_v2.3.4.step', 'P_M07_SPLICE_v2.3.4.step', 'M07_end_joint_v2.3.4.step')}

# ---- 2) 보 단면·하중 ----
B, D, t = 200.0, 400.0, 8.0
A = B * D - (B - 2 * t) * (D - 2 * t)
Iy = (B * D**3 - (B - 2 * t) * (D - 2 * t)**3) / 12
Iz = (D * B**3 - (D - 2 * t) * (B - 2 * t)**3) / 12
Am = (B - t) * (D - t); pm = 2 * ((B - t) + (D - t)); J = 4 * Am**2 * t / pm
m_beam, L_beam = 270.46, 3610.0
xa, xb = -2340.0, 1190.0            # 기둥 중심(얹힘 80의 가운데)
L = xb - xa
Yc = 220.0                          # 보·받침면 Y 중심(Y 120~320)
# (질량 kg, X, Y) Y는 보수 가정: 매단 것은 바늘 줄 Y 0, 롤은 Y -100(롤 X 520~820·Y -220~20 중심)
loads = [('U3 헤드+매달기', 67.24, 200.0, 0.0), ('U4 묶음', 17.2, -235.0, 0.0), ('U7 롤', 6.5, 670.0, -100.0),
         ('U8 레귤레이터', 6.0, 800.0, 100.0), ('U5 구동', 4.5, -2220.0, 0.0)]
m_rail, rail_x = 3.94, (-2140.0, -340.0)
m_car = 29.2 - 3.94 - 4.5
car_x = (-1930.0, -550.0)
m_end = 2.34 + 3.63


def pts_of(gf, car_at, extra=()):
    p = [(m * G * gf, x, y) for _, m, x, y in loads]
    p.append((m_car * G * gf, car_at, 0.0))
    p.append((m_rail * G * gf, sum(rail_x) / 2, 100.0))
    p += list(extra)
    return p


def end_forces(gf, car_at, extra=()):
    """끝 반력 Ra(NX)·Rb(PX)와 끝 비틀림 반력(N·mm, X축). 비틀림은 단순 지지 보처럼 거리 비로 나눔(양 끝 비틀림 고정)."""
    p = pts_of(gf, car_at, extra)
    Rb = sum(P * (x - xa) for P, x, _ in p) / L
    Ra = sum(P for P, _, _ in p) - Rb
    Tb = sum(P * (Yc - y) * (x - xa) for P, x, y in p) / L
    Ta = sum(P * (Yc - y) for P, _, y in p) - Tb
    wb = m_beam * G * gf; xc = (-2380 + 1230) / 2
    Rb += wb * (xc - xa) / L + m_end * G * gf; Ra += wb * (xb - xc) / L + m_end * G * gf
    return Ra, Rb, Ta, Tb


cases = [('정지 1 g', 1, ()), ('운전 3 g + 끌림 Y 30 N', 3, ((0.0, 200.0, 0.0),)), ('오조작 3 g + 손 500 N + 끌림 Y 100 N', 3, ((500.0, 200.0, -90.0),))]
drag = {'정지 1 g': 0.0, '운전 3 g + 끌림 Y 30 N': 30.0, '오조작 3 g + 손 500 N + 끌림 Y 100 N': 100.0}
ecc = {}
for nm, gf, ex in cases:
    worst = None
    for cx in car_x:
        Ra, Rb, Ta, Tb = end_forces(gf, cx, ex)
        F = drag[nm]
        Mdrag = F * (250.0 - 12.0) * (200 - xa) / L     # 끌림 Y가 기둥 윗면(Z 250)에 주는 X축 모멘트, PX 몫
        for end, Rv, T in (('NX', Ra, Ta), ('PX', Rb, Tb)):
            Md = Mdrag if end == 'PX' else F * 238.0 - Mdrag
            e = (T + Md) / Rv
            cand = {'끝': end, 'car_X': cx, 'R_N': round(Rv), 'T_Nmm': round(T + Md), 'e_mm(-Y 쪽)': round(e, 1),
                    'e/반폭100': round(e / 100.0, 2), 'e/핵 33.3': round(e / (200 / 6), 2)}
            if worst is None or cand['e/반폭100'] > worst['e/반폭100']:
                worst = cand
    ecc[nm] = worst
R['2_end_bearing_eccentricity'] = ecc
R['2_note'] = '합력 편심 e < 반폭 100이면 보가 기둥 위에서 앞(-Y)으로 넘어가지 않음(볼트 없이도). e > 핵 33.3이면 뒤 모서리(Y 320) 접촉압이 0으로 떨어져 뒤쪽이 살짝 뜨려 함 -> 이음판·받침 볼트(예압 4 kN x 10)가 묶음'

# 뒤 모서리 들림 힘(e > 핵일 때 볼트가 막아야 하는 몫, 보수: 뒤 볼트 줄 Y 300에서 앞 모서리 Y 120 회전)
lift = {}
Fp, nb = 4000.0, 10
for nm, v in ecc.items():
    Rv, T = v['R_N'], v['T_Nmm']
    # 앞 모서리(Y 120) 기준 회전: 넘기려는 모멘트 T - R*100(합력이 받침 가운데에 있을 때 복원) -> 음이면 안 넘어감
    tip = T - Rv * 100.0
    lift[nm] = {'넘김 모멘트 - 자중 복원(N·mm, 음이면 안전)': round(tip), '넘어짐 안전율(반폭 100 / e, 볼트 없이)': round(100.0 / max(v['e_mm(-Y 쪽)'], 1e-6), 2)}
R['3_tipping'] = lift

# 볼트가 더하는 복원(앞 모서리 Y 120 회전): 받침 가로 다리 Y 280 줄 CB5-20 x2(인장, 예압 4 kN) -> 세로 다리 -> 기둥 면 마찰(CB5-20 x6 x 4 kN x 0.15)
# 둘 중 작은 것, 팔 160. 이음판(Y 320~326) 기둥 쪽 마찰 CB5-16 x4 x 4 kN x 0.15, 팔 200.
F_seat = min(2 * Fp, 6 * Fp * 0.15); F_spl = 4 * Fp * 0.15
for nm, v in ecc.items():
    Rv, T = v['R_N'], v['T_Nmm']
    need = 1.0 if nm.startswith('정지') else (3.0 if nm.startswith('운전') else 2.0)
    sf = (Rv * 100.0 + F_seat * 160.0 + F_spl * 200.0) / T
    R['3_tipping'][nm].update({'볼트 복원 포함 안전율': round(sf, 2), '필요': need, '판정': '됨' if sf >= need else ('디테일' if sf >= 1.2 else '동작')})

# ---- 4) 웨브 국부 크리플링(끝 반력, AISC J10-3a 꼴, 웨브 2장) ----
Nb, d = 80.0, 400.0
Rn_web = 0.40 * t**2 * (1 + 3 * (Nb / d) * (t / t)**1.5) * math.sqrt(E_s * SY * t / t)
Rmax = max(end_forces(3, cx, ((500.0, 200.0, -90.0),))[1] for cx in car_x)
R['4_web_crippling'] = {'Rn_per_web_N': round(Rn_web), 'R_end_max_N(오조작)': round(Rmax), 'SF(웨브 2장)': round(2 * Rn_web / Rmax, 1),
                        'note': '끝판 t8이 끝면 1 mm 안에 있어 실제는 더 큼. 과사양 note(단면은 강성·탭 물림으로 정함, U-01)'}

# ---- 5) 바늘점 Y 흔들림(끌림 Y, 바늘점 Z 12) ----
# 새 지지: 기둥(80160 강축 1,500 cm4 임시, 4080 몫 무시) 받침틀 묶음 Z -250에서 외팔, 윗끝 Z 250에 보가 얹혀 볼트로 묶임.
# 보는 Y 굽힘 EIz로 두 기둥 윗끝을 잇고, 비틀림 GJ로 기둥 윗끝 회전을 잇는다.
# 바늘점은 기둥 윗끝보다 238 아래 -> 윗끝에 F와 Mx = +238 F(윗끝 기울기를 거꾸로 돌림).
Ic_s, Ic_w = 1500e4, 420e4
h = 500.0
EIc = E_a * Ic_s
EIh = E_s * Iz


def dp(P, xp, x, EI):
    a = xp - xa; b = L - a; xx = x - xa
    if xx <= a: return P * b * xx * (L**2 - b**2 - xx**2) / (6 * L * EI)
    return P * a * (L - xx) * (L**2 - a**2 - (L - xx)**2) / (6 * L * EI)


sway_y = {}
for F in (30.0, 100.0):
    a = 200 - xa; b = xb - 200
    Fpx = F * a / L                         # PX 기둥 몫(큰 쪽, 보수)
    Mpx = Fpx * 238.0
    v_top = Fpx * h**3 / (3 * EIc) - Mpx * h**2 / (2 * EIc)
    s_top = Fpx * h**2 / (2 * EIc) - Mpx * h / EIc
    v_signed = v_top - s_top * 238.0
    v_cons = Fpx * h**3 / (3 * EIc) + Mpx * h**2 / (2 * EIc) + (Fpx * h**2 / (2 * EIc) + Mpx * h / EIc) * 238.0  # 부호 무시 합(보수)
    dy_b = dp(F, 200.0, 0.0, EIh)
    T = F * (450.0 - 12.0)
    phi = T * a * b / (G_s * J * L)
    sway_y[f'{int(F)} N'] = {'기둥(부호 고려)': round(v_signed, 5), '기둥(부호 무시 보수)': round(v_cons, 5), '보 가로': round(dy_b, 5),
                             '보 비틀림 x 팔 438': round(phi * 438.0, 5),
                             '바늘점 Y 합(보수)': round(v_cons + dy_b + phi * 438.0, 4), '바늘점 Y 합(부호 고려)': round(abs(v_signed) + dy_b + phi * 438.0, 4)}
R['5_needle_sway_Y_mm (기둥 높이 500)'] = sway_y

# ---- 6) 바늘점 X 흔들림(대차 가속 + 끌림 X, 기둥 약축 420 cm4, 높이 500) ----
Fx = m_car * 2.0 + 30.0
kf = 12 * E_a * Ic_w / h**3                         # 윗끝이 보에 고정(문틀)
v_pin = (Fx / 2) * h**3 / (3 * E_a * Ic_w) + (Fx / 2) * 200.0 * h**2 / (2 * E_a * Ic_w)   # 윗끝 핀 + 하중 높이 Z 450(보 도심)
R['6_needle_sway_X_mm (기둥 높이 500)'] = {'Fx_N': round(Fx, 1), '윗끝 고정(문틀)': round(Fx / (2 * kf), 4), '윗끝 핀(보수)': round(v_pin, 4),
                                           'v2.3.3(h 900)': {'고정': 0.0074, '핀': 0.0296}}

# ---- 7) 보 Z 처짐(1 g) 다시 ----
EIv = E_s * Iy
w_self = m_beam * G / L_beam


def dudl(w, x, EI, x0, x1, n=400):
    dx = (x1 - x0) / n
    return sum(dp(w * dx, x0 + (i + .5) * dx, x, EI) for i in range(n))


defl = {}
for x in (0.0, 200.0):
    st = dudl(w_self, x, EIv, xa, xb) + dudl(m_rail * G / 1800, x, EIv, *rail_x) + sum(dp(m * G, xp, x, EIv) for _, m, xp, _ in loads)
    st += dp(m_car * G, car_x[0], x, EIv)
    defl[f'X {int(x)}'] = {'정하중_1g': round(st, 4), '대차 X 0->1380 변화': round(dp(m_car * G, car_x[1], x, EIv) - dp(m_car * G, car_x[0], x, EIv), 5),
                           'U4 누름 100 N 변화': round(-dp(100.0, -235.0, x, EIv), 5), 'U5 누름 90 N(REST/끝)': [round(-dp(90.0, -1800.0, x, EIv), 5), round(-dp(90.0, -420.0, x, EIv), 5)]}
R['7_beam_deflection_Z_mm'] = defl

# ---- 8) 보 응력(3 g, 굽힘 + 비틀림) ----
Zy, Zz = Iy / (D / 2), Iz / (B / 2)
st8 = {}
for nm, gf, ex in cases[1:]:
    best = 0
    for cx in car_x:
        p = pts_of(gf, cx, ex)
        Ra = sum(P for P, _, _ in p) - sum(P * (x - xa) for P, x, _ in p) / L
        Ra += m_beam * G * gf * (xb - (-2380 + 1230) / 2) / L
        for xs in [q[1] for q in p] + [xa + L / 2]:
            M = Ra * (xs - xa) - sum(P * (xs - x) for P, x, _ in p if x < xs) - m_beam * G * gf / L_beam * (xs - xa)**2 / 2
            best = max(best, M)
    F = drag[nm]
    My = F * (200 - xa) * (xb - 200) / L
    Ta, Tb = end_forces(gf, -550.0, ex)[2:]
    tau = max(Ta, Tb) / (2 * Am * t)
    s = best / Zy + My / Zz
    seq = math.sqrt(s**2 + 3 * tau**2)
    st8[nm] = {'M_Nmm': round(best), 'T_max_Nmm': round(max(Ta, Tb)), 'sigma_eq_MPa': round(seq, 2), 'SF': round(SY / seq, 1)}
R['8_beam_stress'] = st8

os.makedirs(f'{ROOT}/fea/results', exist_ok=True)
json.dump(R, open(f'{ROOT}/fea/results/mech_M07_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, json.dumps(v, ensure_ascii=False)[:600])
