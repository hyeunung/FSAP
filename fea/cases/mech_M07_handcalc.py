# -*- coding: utf-8 -*-
"""M07 해석부 손계산 — U1 프레임 + 보 (v2.3.3).
FEA 환경 없음(D-16) -> 손계산만. 형상: stepout STEP bbox(0절) + mech_M07_model.md 3절 좌표.
하중: 걸린 질량(mech_M07_design.md 3절 = 측정 보고서 5절) x 3 g, 끌림 운전 30 N / 오조작 100 N(D-79·D-08 임시),
      오조작 손 500 N @ X 200(설계안 임시), 누름 U4 100 N·U5 90 N(위로 = 끝 반력을 줄이므로 강도에서는 뺌).
체결 임시값: D-54(HNTT8-5 + CB5 4 N·m -> 예압 4 kN, μ 0.15; 참고 μ 0.2).
판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2 = '동작'(부러짐·영구 변형·미끄러져 내려앉음).
"""
import json, math, re, os
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
E_s, G_s, E_a = 205000.0, 79000.0, 70000.0
SY_SS400, SY_STKR = 245.0, 245.0
SF_OP, SF_MIS = 3.0, 2.0
R = {}

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
bb = {}
for n in ['P_M07_BEAM', 'P_M07_SEAT_NX', 'P_M07_SEAT_PX', 'P_M07_SPLICE_NX', 'P_M07_SPLICE_PX']:
    txt = open(f'{ROOT}/tools/out/mech_M07/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [p for p in (tuple(map(float, m)) for m in pat.findall(txt)) if any(abs(c) > 1e-9 for c in p) and not (abs(p[0]) < 1e-9 or abs(p[1]) < 1e-9 or abs(p[2]) < 1e-9)]
    bb[n] = [round(min(p[i] for p in pts), 2) for i in range(3)] + [round(max(p[i] for p in pts), 2) for i in range(3)]
R['0_step_bbox(xmin,ymin,zmin,xmax,ymax,zmax)'] = bb

# ---------- 1) 보 단면 ----------
B, D, t = 200.0, 400.0, 8.0
A = B * D - (B - 2 * t) * (D - 2 * t)
Iy = (B * D**3 - (B - 2 * t) * (D - 2 * t)**3) / 12
Iz = (D * B**3 - (D - 2 * t) * (B - 2 * t)**3) / 12
Am = (B - t) * (D - t); pm = 2 * ((B - t) + (D - t)); J = 4 * Am**2 * t / pm
xa, xb = -2291.0 + 4.5, 1141.0 - 4.5     # 받침 가로 다리 위 하중 중심 근처(받침 길이 100의 안쪽 끝 기준 보수: 받침 바깥 굽힘 근처)
xa, xb = -2291.0, 1141.0                 # 설계안과 같은 단순 지지 경간(보수)
L = xb - xa
m_beam = 249.99                           # CAD 질량(changed_parts.json)
w_self = m_beam * G / 3450.0              # N/mm (전 길이 분포, 경간 밖 끝 9 mm는 무시)
R['1_beam_section'] = {'A': round(A), 'Iy': round(Iy), 'Iz': round(Iz), 'J': round(J), 'L_span': L, 'mass_kg': m_beam}

loads = {  # 이름: (kg, X)
    'U3 윗헤드 + 매달기': (67.24, 200.0), 'U4 묶음': (17.2, -235.0), 'U7 롤 걸이 + 롤': (6.5, 670.0),
    'U8 레귤레이터': (6.0, 800.0), 'U5 구동': (4.5, -2220.0),
}
m_rail, rail_x = 3.94, (-2140.0, -340.0)
m_car = 29.2 - 3.94 - 4.5                 # 20.76 kg, X -1930 (REST) ~ -550
car_x = (-1930.0, -550.0)
m_seat, m_splice = 2.34, 3.21             # 끝마다(보 쪽 몫 전부를 끝 반력에 보수로 더함)

def reactions(gf, extra_P=(), car_at=-1930.0):
    """양 끝 반력(N, 아래로 받친 힘) — gf: 중력 배수."""
    pts = [(m * G * gf, x) for m, x in loads.values()]
    pts.append((m_car * G * gf, car_at))
    pts.append((m_rail * G * gf, sum(rail_x) / 2))
    pts += list(extra_P)
    Rb = sum(P * (x - xa) for P, x in pts) / L
    Ra = sum(P for P, _ in pts) - Rb
    wb = m_beam * G * gf
    xc = (-2300 + 1150) / 2
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

# ---------- 2) 보 굽힘·비틀림 응력(3 g) ----------
def Mmax_beam(gf, extra=()):
    best = 0
    for cx in car_x:
        Ra, Rb, pts = reactions(gf, extra, cx)
        Ra -= (m_seat + m_splice) * G * gf
        for xs in [p[1] for p in pts] + [xa + L / 2]:
            M = Ra * (xs - xa) - sum(P * (xs - x) for P, x in pts if x < xs) - w_self * gf * (xs - xa)**2 / 2
            best = max(best, M)
    return best
Zy = Iy / (D / 2); Zz = Iz / (B / 2)
for nm, gf, extra, need, Fy in [('운전 3 g + 끌림 30 N', 3, (), SF_OP, 30.0), ('오조작 3 g + 손 500 N + 끌림 100 N', 3, ((500.0, 200.0),), SF_MIS, 100.0)]:
    M = Mmax_beam(gf, extra)
    My = Fy * (200 - xa) * (xb - 200) / L
    T = Fy * (450.0 - 12.0)                     # 바늘점 Z 12 -> 보 도심 Z 450
    tau = T / (2 * Am * t)
    s = M / Zy + My / Zz
    seq = math.sqrt(s**2 + 3 * tau**2)
    sf = SY_STKR / seq
    R[f'3_beam_stress {nm}'] = {'M_Nmm': round(M), 'sigma_MPa': round(s, 2), 'tau_MPa': round(tau, 3), 'SF': round(sf, 1), 'need': need, 'verdict': verdict(sf, need)}

# ---------- 3) 보 처짐·바늘점 흔들림(1 g 운전 변화, 기록 — 6-2 미정 D-08) ----------
EIv, EIh = E_s * Iy, E_s * Iz
def dp(P, xp, x, EI):
    a = xp - xa; b = L - a; xx = x - xa
    if xx <= a: return P * b * xx * (L**2 - b**2 - xx**2) / (6 * L * EI)
    return P * a * (L - xx) * (L**2 - a**2 - (L - xx)**2) / (6 * L * EI)
def dudl(w, x, EI, x0=xa, x1=xb, n=400):
    dx = (x1 - x0) / n
    return sum(dp(w * dx, x0 + (i + .5) * dx, x, EI) for i in range(n))
d = {}
for x in (0.0, 200.0):
    st = dudl(w_self, x, EIv) + dudl(m_rail * G / 1800, x, EIv, *rail_x) + sum(dp(m * G, xp, x, EIv) for m, xp in loads.values())
    st += dp(m_car * G, car_x[0], x, EIv)
    d[f'X {int(x)}'] = {'정하중 처짐_1g': round(st, 4),
                        '대차 X 0->1380 변화': round(dp(m_car * G, car_x[1], x, EIv) - dp(m_car * G, car_x[0], x, EIv), 5),
                        'U4 누름 100 N 변화': round(-dp(100.0, -235.0, x, EIv), 5),
                        'U5 누름 90 N (REST/끝)': [round(-dp(90.0, -1800.0, x, EIv), 5), round(-dp(90.0, -420.0, x, EIv), 5)],
                        '정하중 처짐_3g(참고)': round(3 * st, 4)}
R['4_beam_deflection_mm'] = d
# 끌림 Y: 보 가로 + 비틀림 + 기둥(80160 강축 1,500 cm4·약축 420 cm4 임시 + 4080 몫 무시, 높이 = 받침틀 묶음 Z -250 ~ 보 도심 Z 450 = 700, 설계안 900 보수)
Ic_s, Ic_w = 1500e4, 420e4
for h_col in (700.0, 900.0):
    drag = {}
    for F in (30.0, 100.0):
        lever = 438.0
        T = F * lever; a = 200 - xa; b = xb - 200
        dy_b = dp(F, 200.0, 0.0, EIh)
        phi = T * a * b / (G_s * J * L)
        M_px = T * a / L                        # 큰 쪽 끝 모멘트 몫(보수: 한 기둥이 받음)
        th = M_px * h_col / (E_a * Ic_s); dtop = M_px * h_col**2 / (2 * E_a * Ic_s)
        dsh = (F / 2) * h_col**3 / (3 * E_a * Ic_s)
        tot = dy_b + phi * lever + th * lever + dtop + dsh
        drag[f'{int(F)} N'] = {'보 가로': round(dy_b, 5), '보 비틀림': round(phi * lever, 5), '기둥': round(th * lever + dtop + dsh, 5), '바늘점 Y 합': round(tot, 4)}
    R[f'5_needle_drag_Y_mm (기둥 높이 {int(h_col)})'] = drag
Fx = m_car * 2.0 + 30.0
kf = 12 * E_a * Ic_w / 900.0**3; kp = 3 * E_a * Ic_w / 900.0**3
R['6_needle_sway_X_mm'] = {'Fx_N(대차 20.76 kg x 2 m/s2 + 30 N 임시)': round(Fx, 1), '기둥 위 고정': round(Fx / (2 * kf), 4), '기둥 위 핀': round(Fx / (2 * kp), 4)}

# ---------- 4) 보 -> 기둥 끝 체결: T너트 마찰(하중 길 유일, 양의 받침 없음) ----------
Fp, mu = 4000.0, 0.15                         # D-54
p_M5 = 0.8
def nut_preload(engage):
    """HNTT8-5(강 T너트) 물림 길이가 허용하는 예압 상한: 나사 벗겨짐(너트 쪽) A = pi*d*Le*0.75, tau = 0.58*245."""
    if engage < p_M5: return 0.0
    cap = math.pi * 5.0 * engage * 0.75 * 0.58 * 245.0
    return min(Fp, cap / 1.2)               # 벗겨짐 SF 1.2 안의 예압만 인정
seat_eng, splice_eng = 0.5, 3.5              # 모델 실측(mech_M07_model.md 5절, M07-D7)
fix_eng = 7.5                                # CB5-20/CB5-16으로 바꾼 뒤(M07-D7 고치는 법)
fr = {}
for tag, es, ep in [('지금 모델(물림 0.5 / 3.5)', seat_eng, splice_eng), ('볼트 길이만 고친 뒤(물림 7.5)', fix_eng, fix_eng)]:
    Fs = 6 * nut_preload(es); Fsp = 4 * nut_preload(ep)
    for m in (0.15, 0.2):
        cap = (Fs + Fsp) * m
        row = {}
        for cn, cv in cases.items():
            sf = cap / cv['R_max_N']
            need = SF_MIS if '오조작' in cn else SF_OP
            row[cn] = {'SF': round(sf, 2), 'verdict': verdict(sf, need) if '1 g' not in cn else ('참고(정지)' if sf >= 1.2 else '동작')}
        fr[f'{tag} μ{m}'] = {'clamp_seat_N': round(Fs), 'clamp_splice_N': round(Fsp), 'slip_cap_N': round(cap), 'by_case': row}
R['7_end_slip'] = fr

# ---------- 5) 받침 L 굽힘(SS400 t9, 폭 180) ----------
Zs = 180 * 9**2 / 6
for cn in ('운전 3 g', '오조작 3 g + 손 500 N @X 200'):
    Rm = cases[cn]['R_max_N']
    for arm in (41.0, 50.0):                  # 굽힘 안 R 끝(X -2291)~가로 다리 하중 중심 X -2250 / 설계안 50
        s = Rm * arm / Zs; need = SF_MIS if '오조작' in cn else SF_OP
        R[f'8_seat_bend {cn} 팔 {int(arm)}'] = {'R_N': Rm, 'sigma_MPa': round(s, 1), 'SF': round(SY_SS400 / s, 2), 'need': need, 'verdict': verdict(SY_SS400 / s, need)}
# 받침 세로 다리 볼트 들뜸(편심 모멘트 R x 45, 다리 밑 끝 Z 150 회전점, 볼트 줄 Z 175·220)
for cn in ('운전 3 g',):
    M = cases[cn]['R_max_N'] * 45.0
    T_top = M * 70.0 / (3 * (25.0**2 + 70.0**2))
    R['9_seat_bolt_prying 운전 3 g'] = {'M_Nmm': round(M), 'T_per_top_bolt_N': round(T_top), 'note': '예압 4 kN이면 접면 압이 남음(볼트 길이 고친 뒤), 지금 물림 0.5면 예압 0이라 다리가 들림'}

# ---------- 6) 이음판 t6·보 쪽 탭 볼트(전단, 지지형) ----------
Rm = cases['오조작 3 g + 손 500 N @X 200']['R_max_N']
tau_b = Rm / (4 * 14.2)
R['10_splice_CB5-16_beam_tap_shear(끝 반력 전부를 4개가 받는 최악)'] = {'tau_MPa': round(tau_b, 1), 'SF(12.9 전단 0.6x1080)': round(0.6 * 1080 / tau_b, 1)}
tau_p = Rm / (6 * 380)
R['11_splice_plate_shear'] = {'tau_MPa': round(tau_p, 2), 'SF': round(0.58 * SY_SS400 / tau_p, 0), 'verdict': verdict(0.58 * SY_SS400 / tau_p, SF_MIS)}

# ---------- 7) 기둥 압축·좌굴(HFS8-80160 임시 A 약 5,000 mm2, 약축 420 cm4, 길이 1482 외팔 보수) ----------
Ac = 5000.0
Pc = cases['오조작 3 g + 손 500 N @X 200']['R_max_N'] + 43.39 * G * 3
Pcr = math.pi**2 * E_a * Ic_w / (2.0 * 1482.0)**2
R['12_column'] = {'P_N': round(Pc), 'sigma_MPa': round(Pc / Ac, 2), 'Pcr_cantilever_N': round(Pcr), 'SF_buckling': round(Pcr / Pc, 0)}

os.makedirs(f'{ROOT}/fea/results', exist_ok=True)
json.dump(R, open(f'{ROOT}/fea/results/mech_M07_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    if k.startswith(('2_', '3_', '7_', '8_')): print(k, json.dumps(v, ensure_ascii=False)[:300])
