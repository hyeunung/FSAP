# -*- coding: utf-8 -*-
"""구동 T17 해석부 손계산 — 진공 배관 회전부 건너기 (v0.8.6).
바뀐 하중 부품: P_T01_POST(벽 Ø8 θ270 Z -100, 안내 갈래 C 2, θ270 리브 + C홈 + 뿌리 R2),
곁가지: P_T01_RING1(M5 탭 + Ø3 (0,-800)), P_T01_DISC(Ø6.4 + Ø3 축 가운데), P_T01_YPLATE(Ø10 x2, M5 탭 x4),
C클립 3종(관 끼움 변형). 해석 못 함 — 환경 없음(D-16) -> 손계산. 경계조건·하중은 fea/models.json 그대로.
"""
import json, math, re
from collections import Counter

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEP = ROOT + '/tools/out/mech_T17/stepout/'
OUT = ROOT + '/fea/results/mech_T17_handcalc.json'
pi = math.pi
AX = (0.0, -700.0)
R = dict(method='손계산(표준 라이브러리). 해석 못 함 — 환경 없음(D-16). 모델 = fea/models.json 그대로(바꾸지 않음)',
         checks=[], parts={}, problems=[])

def chk(part, what, step, used, tol=0.1):
    ok = abs(step - used) <= tol
    R['checks'].append(dict(part=part, what=what, step=round(step, 3), used=used, ok=ok))
    return ok

def pts_of(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    P = [[float(x) for x in m.group(1).split(',')]
         for m in re.finditer(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", s)]
    return [p for p in P if len(p) == 3]

# ------------------------------------------------ STEP 형상 확인(면 선택은 STEP 점 구름으로)
po = pts_of(STEP + 'P_T01_POST.step')
rr = lambda p: math.hypot(p[0] - AX[0], p[1] - AX[1])
near = [p for p in po if -106 < p[2] < -94]
rc = Counter(round(rr(p), 1) for p in near)
chk('P_T01_POST', 'Z -100 관 바깥 R(점 최빈)', 30.0 if rc[30.0] > 100 else 0.0, 30.0)
chk('P_T01_POST', 'Z -100 관 속 R(점 최빈)', 20.0 if rc[20.0] > 100 else 0.0, 20.0)
hole = [p for p in near if p[1] < AX[1] - 25 and abs(p[0]) < 6]
chk('P_T01_POST', '벽 Ø8 반폭(X 최대)', max(abs(p[0]) for p in hole), 4.0)
chk('P_T01_POST', '벽 Ø8 Z 가운데', (min(p[2] for p in hole) + max(p[2] for p in hole)) / 2, -100.0, 0.5)
_s = open(STEP + 'P_T01_POST.step', encoding='utf-8', errors='ignore').read()
_cp = {m.group(1): [float(x) for x in m.group(2).split(',')]
       for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", _s)}
_vx = [_cp[m.group(1)] for m in re.finditer(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", _s) if m.group(1) in _cp]
rib = [p for p in _vx if p[1] < AX[1] - 30.5 and abs(p[0]) <= 5.3 and -146 < p[2] < -117]
chk('P_T01_POST', '리브 Y 끝(-756.25, 꼭짓점)', min(p[1] for p in rib), -756.25)  # 점 구름 최소 -760은 축 배치점

# ------------------------------------------------ 기둥 Z -100 단면(벽 Ø8 관통)
Ro, Ri = 30.0, 20.0
F_MIS = 275.587   # 작은 매트 충돌 마찰 한계(models.json P_T01_POST, mech_T01_fea1 F_lat_mis), 원판 윗면 Z -0.5
F_OP = 20.8564    # 운전(끌림 20 N + 이송 가속), mech_T11_handcalc.json F_op
Z_LOAD, Z_HOLE, D_HOLE = -0.5, -100.0, 8.0
SY, SF_REQ, SF_MIS_REQ, SF_BREAK = 20.0, 3.0, 2.0, 1.2
KT = 3.0          # 관 횡구멍 굽힘 Kt(Peterson d/D 0.13 -> 약 2.3), 보수로 3 (T11과 같은 방식)

def sec(load_deg, n=1440, nr=20):
    A = Sy = 0.0; cells = []
    dth = 2 * pi / n; dr = (Ro - Ri) / nr
    for i in range(n):
        th = (i + 0.5) * dth
        da = (th - math.radians(270.0) + pi) % (2 * pi) - pi
        for j in range(nr):
            r = Ri + (j + 0.5) * dr
            if math.cos(da) > 0 and abs(r * math.sin(da)) < D_HOLE / 2:
                continue                      # 구멍 축 -Y, 지름 8 원통이 벽을 관통
            dA = r * dth * dr
            y = r * math.cos(th - math.radians(load_deg))
            A += dA; Sy += y * dA; cells.append((y, dA, r))
    yc = Sy / A
    I = sum((y - yc) ** 2 * dA for y, dA, r in cells)
    ym = max(abs(y - yc) for y, dA, r in cells if r > Ro - dr) + dr / 2
    return A, I, ym

gross_I = pi * (Ro ** 4 - Ri ** 4) / 4
gross_Z = gross_I / Ro
rows = []; worst = None
for d in range(0, 360, 15):
    A, I, ym = sec(d)
    Zn = I / ym
    rows.append(dict(load_dir_deg=d, A=round(A, 1), Z_net=round(Zn, 0)))
    if worst is None or Zn < worst[1]:
        worst = (d, Zn, A)
L = Z_LOAD - Z_HOLE
M_mis, M_op = F_MIS * L, F_OP * L
s_nom = M_mis / worst[1]
s_pk = KT * s_nom
s_op = KT * M_op / worst[1]
T11 = json.load(open(ROOT + '/fea/results/mech_T11_handcalc.json', encoding='utf-8'))['parts']['P_T01_POST']
post = dict(material='PET-CF(층간 자리값 20 MPa)', section_Z=-100, gross_Z=round(gross_Z, 0),
            worst_load_dir_deg=worst[0], Z_net_min=round(worst[1], 0), A_net=round(worst[2], 1),
            lever_mm=L, M_mis_Nmm=round(M_mis, 0), sigma_nom_mis=round(s_nom, 2), Kt=KT,
            sigma_peak_mis=round(s_pk, 2), SF_peak_mis=round(SY / s_pk, 2),
            sigma_peak_op=round(s_op, 3), SF_peak_op=round(SY / s_op, 1),
            net_by_dir=rows,
            governing_unchanged=dict(where='장공 밑끝 Z -208(T11, v0.6.15)', SF_peak_net_mis=T11['SF_peak_net_mis'],
                                     SF_root_Z221=T11['SF_root_v0614'],
                                     note='T17은 Z -192 위만 바꿈(갈래 Z -192~-182, 리브 -145~-118, 벽 Ø8 -100). 장공·뿌리 단면 그대로'),
            added_material='안내 갈래·리브·뿌리 R2는 관 바깥에 붙은 살(하중 안 받음, 판정에서 빼서 보수)')
R['parts']['P_T01_POST'] = post

# ------------------------------------------------ 링1 (0,-800) M5 탭 관통(Ø4.2 + Ø3), r100
ring_sigma_jam = 10.063   # mech_T01_fea1 jam_rigid_supports sigma_eq(링1 최대)
R['parts']['P_T01_RING1'] = dict(material='A5052 Rp 175', hole='M5 탭 Ø4.2 Z -10.5~-4.5 + Ø3 -4.5~-0.5 at r100',
    method='링 최대 응력(막힘·강체 받침, 위치 무관 상한) x Kt 3 x 순폭 보정(폭 225 / 220.8)',
    sigma=round(ring_sigma_jam * 3 * 225 / 220.8, 2), SF=round(175 / (ring_sigma_jam * 3 * 225 / 220.8), 1), need=SF_MIS_REQ)

# ------------------------------------------------ 원판 가운데(기둥 속 r20 위, 진공 58 kPa)
q = 0.058; a = 20.0; t_full = 12.0; t_skin = 4.0
s_full = 0.75 * q * a * a / t_full ** 2           # 둘레 고정 원판, 고른 압력(Roark)
s_skin = 0.75 * q * a * a / t_skin ** 2 * 3.0     # 상한: 구멍 위 살 t4로 전체를 받는다고 + Kt 3
R['parts']['P_T01_DISC'] = dict(material='Rigid 10K 65 MPa', load='진공 58 kPa on r20(기둥 속 위)',
    sigma_t12=round(s_full, 3), sigma_upper_t4_Kt3=round(s_skin, 2), SF_upper=round(65 / s_skin, 1),
    insert='MBIS5 + KQ2H06-M5A: 관 당김 < 5 N(진공 = 관 안쪽, 피팅에 축력 없음), 조임 지시는 디테일(T17-D)')

# ------------------------------------------------ Y판 Ø10 x2 (±109.6, -711.2)
T14 = json.load(open(ROOT + '/fea/results/mech_T14_fea_handcalc.json', encoding='utf-8'))['YPLATE_t10']
L_strip = T14['A_op3g']['L']
x_far = 14.6               # 구멍 먼 끝 - DG 받침 옆면(하중선 X 100) 거리
ratio = x_far / L_strip    # 외팔 띠: 하중선에서 멀어질수록 모멘트 선형 증가
yp = {}
for k, need in (('A_op3g', SF_REQ), ('A_mis', SF_MIS_REQ)):
    s = T14[k]['sigma'] * ratio * (100 / 90) * 3.0
    yp[k] = dict(sigma_at_hole=round(s, 2), SF=round(175 / s, 2), need=need)
yp['taps_M5'] = '(±54, -724/-698)는 DG 받침 밑(X ±100 안) — 판이 받침과 블록 사이 압축만, 굽힘 띠 밖'
yp['method'] = 'T14 띠 최대 응력 x (구멍 먼 끝 14.6 / 띠 길이 %.1f) x 순폭 100/90 x Kt 3' % L_strip
R['parts']['P_T01_YPLATE'] = yp

# ------------------------------------------------ C클립 관 끼움(TU0604 PU Ø6, 입 4.5)
E_PET = 2500.0; eps_y = 50.0 / E_PET          # PET-CF 항복 변형률 2 %(D-57 E, 50 MPa)
E_PU = 40.0                                     # PU 관 E 임시(쇼어 93A 상당, 새 자료대기 후보)
def tube_k(Lc):                                 # 관 지름 방향 눌림 강성(얇은 링, 단위 길이) x 길이
    Rm, t = 2.5, 1.0
    return E_PU * (t ** 3 / 12) / (0.149 * Rm ** 3) * Lc
clips = {}
for name, din, dout, Lc in (('기둥 안내 갈래 150°/30°', 5.9, 11.0, 10.0),
                            ('TCLAMP C클립', 6.5, 11.0, 10.0)):
    h = (dout - din) / 2; Rm = (dout + din) / 4; I = Lc * h ** 3 / 12
    delta = 6.0 - 4.5
    k_c = E_PET * I / (3 * pi * Rm ** 3)           # 갈린 링 끝 벌림 강성(곡선보)
    k_t = tube_k(Lc) / delta if False else tube_k(Lc)
    d_c = delta * k_t / (k_t + k_c)                # 직렬 스프링: 관과 클립이 나눠 변형
    eps = lambda d: 2 * (h / 2) * d / (3 * pi * Rm ** 2)
    clips[name] = dict(h=round(h, 2), Rm=round(Rm, 3), k_clip_N_per_mm=round(k_c, 1), k_tube_N_per_mm=round(k_t, 1),
                       open_share_mm=round(d_c, 2), strain_pct=round(100 * eps(d_c), 2),
                       strain_pct_rigid_tube=round(100 * eps(delta), 2), SF_strain=round(eps_y / eps(d_c), 2),
                       SF_strain_rigid_tube=round(eps_y / eps(delta), 2), insert_force_N=round(k_t * (delta - d_c), 0))
# 리브 C홈: 입술 = 외팔(두께 2, 길이 약 3.5, 폭 27)
I_l = 27 * 2 ** 3 / 12; k_l = 3 * E_PET * I_l / 3.5 ** 3; k_t = tube_k(27)
d_l = 0.75 * k_t / (k_t + k_l)
clips['리브 연속 C홈'] = dict(k_lip_N_per_mm=round(k_l, 0), k_tube_N_per_mm=round(k_t, 1), lip_defl_mm=round(d_l, 4),
                          strain_pct=round(100 * 1.5 * 2 * d_l / 3.5 ** 2, 3), insert_force_N=round(k_t * 1.5, 0),
                          note='관이 거의 다 눌림 -> 한 번에 밀지 말고 끝에서부터 굴려 넣음(작업 지시)')
R['parts']['clips'] = clips
R['clip_note'] = 'PU 관 E 40 MPa 임시. 관 강성이 클립보다 작아 관이 주로 눌린다. 관이 단단하다고 둔 상한도 같이 적음. 끼움 손맛·빠짐은 시제품 확인(요구서 7절)'

# ------------------------------------------------ 판정
def prob(kind, what, where, ev, fix):
    R['problems'].append(dict(kind=kind, what=what, where=where, evidence=ev, fix=fix))
if post['SF_peak_mis'] < SF_BREAK:
    prob('동작', '기둥 벽 Ø8 단면 부러짐', 'P_T01_POST Z -100', 'SF %.2f' % post['SF_peak_mis'], '구멍 Ø6 또는 살 덧댐')
elif post['SF_peak_mis'] < SF_MIS_REQ:
    prob('디테일', '기둥 벽 Ø8 단면 오조작 SF 미달', 'P_T01_POST Z -100', 'SF %.2f' % post['SF_peak_mis'], '구멍 둘레 보강')
for nm, c in clips.items():
    sf = c.get('SF_strain')
    if sf is not None and sf < 1.2:
        prob('디테일', 'C클립 끼움 변형률 과다', nm, 'SF %.2f' % sf, '입 4.5 -> 5.0')
R['pass'] = not any(p['kind'] == '동작' for p in R['problems'])
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('checks', [(c['what'], c['step'], c['ok']) for c in R['checks']])
print('POST', {k: post[k] for k in ('worst_load_dir_deg', 'Z_net_min', 'gross_Z', 'sigma_peak_mis', 'SF_peak_mis', 'SF_peak_op')}, 'gov', post['governing_unchanged']['SF_peak_net_mis'])
print('RING1', R['parts']['P_T01_RING1']['SF'], 'DISC', R['parts']['P_T01_DISC']['SF_upper'], 'YPLATE', yp['A_op3g'], yp['A_mis'])
for k, v in clips.items(): print(k, v)
print('problems', R['problems'], 'pass', R['pass'])
