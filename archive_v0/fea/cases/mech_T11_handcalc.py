# -*- coding: utf-8 -*-
"""구동 T11 해석부 손계산 — 링2 포트 방향(배관 길) v0.6.15.
바뀐 하중 부품: P_T01_POST(세로 장공 5.5x10 x3, 장공 높이 속 Ø40.2), P_T01_SPIDER_1~3(결속 구멍 Ø4 x4),
P_T01_YPLATE(결속 구멍 Ø4.5 x2). 해석 못 함 — 환경 없음(D-16) → 손계산.
경계조건·하중은 fea/models.json 그대로(모델 바꾸지 않음). 기준값: 이전 결과 JSON.
"""
import json, math, os, re, sys

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
STEP = ROOT + '/tools/out/mech_T11/stepout/'
OUT = ROOT + '/fea/results/mech_T11_handcalc.json'
pi = math.pi
AX = (0.0, -700.0)

def step_geom(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    pts = {}
    for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", s):
        v = [float(x) for x in m.group(2).split(',')]
        if len(v) == 3:
            pts[int(m.group(1))] = v
    ax2 = {}
    for m in re.finditer(r"#(\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)", s):
        ax2[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    dirs = {}
    for m in re.finditer(r"#(\d+)\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", s):
        dirs[int(m.group(1))] = [float(x) for x in m.group(2).split(',')]
    cyl = []
    for m in re.finditer(r"CYLINDRICAL_SURFACE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*([-0-9.Ee+]+)\s*\)", s):
        a = ax2.get(int(m.group(1)))
        if a:
            cyl.append(dict(r=round(float(m.group(2)), 3), p=[round(x, 3) for x in pts[a[0]]], d=[round(x, 3) for x in dirs[a[1]]]))
    P = list(pts.values())
    bb = [[min(p[i] for p in P), max(p[i] for p in P)] for i in range(3)]
    return dict(bbox=[[round(a, 3), round(b, 3)] for a, b in bb], cyl=cyl, pts=P)

R = dict(method='손계산(표준 라이브러리). 해석 못 함 — 환경 없음(D-16). 모델 = fea/models.json 그대로', checks=[], parts={})
def chk(part, what, step, used, tol=0.05):
    ok = abs(step - used) <= tol
    R['checks'].append(dict(part=part, what=what, step=step, used=used, ok=ok))
    return ok

G = {k: step_geom(STEP + k + '.step') for k in ('P_T01_POST', 'P_T01_SPIDER_1', 'P_T01_YPLATE')}
R['step_bbox'] = {k: v['bbox'] for k, v in G.items()}

# ---------------------------------------------------------------- 기둥 P_T01_POST
po = G['P_T01_POST']
# 관 면은 STEP에서 B-spline이라 점 구름의 반지름·Z로 잰다
from collections import Counter
rc = Counter(round(math.hypot(x - AX[0], y - AX[1]), 1) for x, y, z in po['pts'] if -221 < z < -15)
R['post_point_radius_top'] = rc.most_common(4)
chk('P_T01_POST', '관 바깥 R(점 최빈)', max(r for r, n in rc.most_common(3) if r < 31), 30.0)
chk('P_T01_POST', '속 R(장공 높이 다시 깎음, 점 최빈)', 20.1 if rc[20.1] > 1000 else 0.0, 20.1)
inner_z = sorted(round(z, 2) for x, y, z in po['pts'] if abs(math.hypot(x - AX[0], y - AX[1]) - 20.1) < 0.02)
chk('P_T01_POST', '속 Ø40.2 Z 밑', inner_z[0], -212.0); chk('P_T01_POST', '속 Ø40.2 Z 위', inner_z[-1], -194.0)
sp_ = [(x, y, z) for x, y, z in po['pts'] if 29.5 < math.hypot(x - AX[0], y - AX[1]) < 30.5 and -209 < z < -197]
slot_z = (min(z for *_, z in sp_), max(z for *_, z in sp_))
chk('P_T01_POST', '장공 Z 밑', round(slot_z[0], 2), -208.0); chk('P_T01_POST', '장공 Z 위', round(slot_z[1], 2), -198.0)
ang = Counter(int(round(math.degrees(math.atan2(y - AX[1], x - AX[0])) % 360 / 120.0 - 0.75) % 3) for x, y, z in sp_)
R['post_slot_points_by_sector'] = dict(ang)
half = {}
for x, y, z in sp_:
    a_ = math.degrees(math.atan2(y - AX[1], x - AX[0])) % 360
    c_ = min((90, 210, 330), key=lambda q: abs((a_ - q + 180) % 360 - 180))
    half[c_] = max(half.get(c_, 0), abs((a_ - c_ + 180) % 360 - 180))
R['post_slot_half_angle_deg_r30'] = {k: round(v, 2) for k, v in half.items()}
for k, v in half.items():
    chk('P_T01_POST', '장공 %d° 폭(r30 호)' % k, round(2 * math.radians(v) * 30.0, 2), 5.5, 0.1)
Ro, Ri, Ri0 = 30.0, 20.1, 20.0
W_SLOT, N_SLOT = 5.5, 3
F_MIS = 275.587          # 작은 매트 충돌 마찰 한계(mech_T01_fea1_handcalc.json F_lat_mis), 원판 윗면 Z -0.5
F_OP = None
try:
    T01 = json.load(open(ROOT + '/fea/results/mech_T01_fea1_handcalc.json', encoding='utf-8'))
    s = json.dumps(T01)
    m = re.search(r'"F_lat": ([0-9.]+)', s)
    F_OP = float(m.group(1)) if m else None
    m = re.search(r'"F_lat_mis": ([0-9.]+)', s)
    F_MIS = float(m.group(1)) if m else F_MIS
except Exception as e:
    R['load_read_error'] = str(e)
Z_LOAD = -0.5
SY = 20.0                # PET-CF 층간 자리값(models.json P_T01_POST)
SF_REQ, SF_MIS_REQ, SF_BREAK = 3.0, 2.0, 1.2

def sec_props(Ro, Ri, cut_angles_deg, w, theta_load_deg, n=7200, nr=40):
    """관 단면에서 장공(원주 폭 w, 벽 관통) 자리를 빼고 수치 적분. 굽힘 축 ⟂ 하중 방향."""
    A = Sx = Ixx = 0.0
    ymax = 0.0
    dth = 2 * pi / n
    for i in range(n):
        th = (i + 0.5) * dth
        for j in range(nr):
            r = Ri + (j + 0.5) * (Ro - Ri) / nr
            dr = (Ro - Ri) / nr
            x_t = r * th
            cut = False
            for a in cut_angles_deg:
                da = (th - math.radians(a) + pi) % (2 * pi) - pi
                if abs(da * r) < w / 2:
                    cut = True; break
            if cut:
                continue
            dA = r * dth * dr
            y = r * math.cos(th - math.radians(theta_load_deg))   # 하중 방향 거리
            A += dA; Sx += y * dA
    yc = Sx / A
    for i in range(n):
        th = (i + 0.5) * dth
        for j in range(nr):
            r = Ri + (j + 0.5) * (Ro - Ri) / nr
            dr = (Ro - Ri) / nr
            cut = any(abs(((th - math.radians(a) + pi) % (2 * pi) - pi) * r) < w / 2 for a in cut_angles_deg)
            if cut:
                continue
            dA = r * dth * dr
            y = r * math.cos(th - math.radians(theta_load_deg)) - yc
            Ixx += y * y * dA
            if r > Ro - dr:
                ymax = max(ymax, abs(y))
    return A, yc, Ixx, ymax + (Ro - Ri) / nr / 2

gross_I = pi * (Ro ** 4 - Ri0 ** 4) / 4
gross_Z = gross_I / Ro
slots = (90.0, 210.0, 330.0)
worst = None; rows = []
for th in range(0, 120, 5):                  # 3회 대칭 → 0~120°
    A, yc, I, ym = sec_props(Ro, Ri, slots, W_SLOT, th, n=1440, nr=12)
    Zn = I / ym
    rows.append(dict(load_dir_deg=th, A=round(A, 1), I=round(I, 0), y_max=round(ym, 2), Z_net=round(Zn, 0)))
    if worst is None or Zn < worst[1]:
        worst = (th, Zn, I, ym, A)
R['parts']['P_T01_POST'] = post = dict(material='PET-CF(층간 자리값 20 MPa)', gross_Z_root=round(gross_Z, 0), net_by_dir=rows)
th_w, Zn, In, ym, An = worst
L_slot = Z_LOAD - (-208.0)              # 장공 밑끝(가장 불리) 레버
L_root = Z_LOAD - (-221.0)
M_mis_slot = F_MIS * L_slot
M_mis_root = F_MIS * L_root
s_nom = M_mis_slot / Zn
# 장공 응력 집중: 하중(축) 방향으로 긴 장공 → 원형 구멍 Kt 3 이하. 보수로 Kt 3(Peterson 무한판 원공, 축 방향 장공은 더 낮음)
KT = 3.0
s_pk = KT * M_mis_slot / gross_Z        # 순단면 대신 총단면 기준 Kt(Peterson 정의) — 비교용
s_pk_net = KT * s_nom                   # 보수 상한: 순단면 응력 × Kt
post.update(worst_load_dir_deg=th_w, Z_net_min=round(Zn, 0), A_net=round(An, 1),
            lever_slot=L_slot, M_mis_slot=round(M_mis_slot, 0),
            sigma_nom_net_mis=round(s_nom, 2), SF_nom_net_mis=round(SY / s_nom, 2),
            Kt=KT, sigma_peak_gross_mis=round(s_pk, 2), SF_peak_gross_mis=round(SY / s_pk, 2),
            sigma_peak_net_mis=round(s_pk_net, 2), SF_peak_net_mis=round(SY / s_pk_net, 2),
            root_sigma_mis_v0614=round(M_mis_root / gross_Z, 2), SF_root_v0614=round(SY / (M_mis_root / gross_Z), 2),
            root_sigma_mis_after=round(M_mis_root / gross_Z, 2),
            note='관 뿌리(Z -221) 단면은 그대로(장공은 Z -208~-198, 뿌리 위 13). 속 Ø40.2 다시 깎기는 Z -212~-194만')
if F_OP:
    M_op = F_OP * L_slot
    post.update(F_op=F_OP, sigma_peak_net_op=round(KT * M_op / Zn, 3), SF_peak_net_op=round(SY / (KT * M_op / Zn), 1))
# 장공 사이 기둥 살(원주 방향 띠): 바깥 둘레 2π·30/3 − 5.5
post['ligament_outer_arc_mm'] = round(2 * pi * Ro / 3 - W_SLOT, 2)
post['ligament_inner_arc_mm'] = round(2 * pi * Ri / 3 - W_SLOT, 2)
post['slot_to_flange_top_mm'] = round(-208.0 - (-221.0), 2)
# 결속 밴드 힘(배관 Ø4 묶음, 자리값 50 N 상한 — 밴드 체결 힘 크기, 기록용) → 장공 끝 지압
F_TIE = 50.0
post['tie_bearing_MPa'] = round(F_TIE / (W_SLOT * (Ro - Ri)), 2)

# ---------------------------------------------------------------- 스파이더 (A5052 t3 모자형)
sp = G['P_T01_SPIDER_1']
holes = [c for c in sp['cyl'] if abs(c['r'] - 2.0) < 0.01]
hz = sorted(set(round(c['p'][2], 2) for c in holes))
hy = sorted(set(round(c['p'][1], 1) for c in holes))
R['spider_holes'] = dict(n_cyl_faces=len(holes), z=hz, y=hy)
chk('P_T01_SPIDER_1', '결속 구멍 Z 위', hz[-1] if hz else 0.0, -197.5)
chk('P_T01_SPIDER_1', '결속 구멍 Z 밑', hz[0] if hz else 0.0, -208.5)
PREV = json.load(open(ROOT + '/fea/results/detail_DP-2_handcalc.json', encoding='utf-8'))
SP = PREV['parts']['P_T01_SPIDER_1~3']
SYA = 175.0
I_sp, zc = SP['I'], SP['zc_from_bottom']        # 발 밑 Z -233 기준
z_na = -233.0 + zc
c_max = zc                                       # 밑 끝까지(가장 먼 섬유는 웹 위 쪽이 더 멀다: 위 -95.5)
c_top = -95.5 - z_na
cmax = max(c_max, c_top)
sp_rows = {}
cases = SP['cases']['새 모델: 발 볼트 피벗 r143.4']
for lab, key_s in (('운전 3 g', 'sigma_3g'), ('막힘', 'sigma_jam')):
    s_max = cases[key_s]                          # 최대 섬유 응력(이전 결과)
    M = s_max * I_sp / cmax
    for zh in hz:
        y = abs(zh - z_na)
        s_h = M * y / I_sp
        # 구멍 2개(양 벽) 빠진 I: ΔI ≈ 2·(d·t·y²) (구멍 자리 단면의 벽 높이 방향 d 만큼 빠짐)
        dI = 2 * (4.0 ** 3 * 3.0 / 12 + 4.0 * 3.0 * y ** 2)
        s_h_net = M * y / (I_sp - dI)
        sp_rows['%s Z%.1f' % (lab, zh)] = dict(y_from_NA=round(y, 2), sigma_nom=round(s_h_net, 3),
                                               sigma_peak_Kt3=round(3 * s_h_net, 3), SF=round(SYA / (3 * s_h_net), 1),
                                               bound_Kt3_x_max_fiber_SF=round(SYA / (3 * s_max), 1))
R['parts']['P_T01_SPIDER_1~3'] = dict(material='A5052 t3', z_NA=round(z_na, 2), holes=sp_rows,
    note='구멍 r 140(Y -560)은 발 볼트 줄(외팔 뿌리 r143.4) 안 — 발이 허브에 눌린 자리라 굽힘이 더 작다. r 300(Y -400)은 외팔 안. 보수로 뿌리 모멘트를 둘 다에 씀',
    edge_to_foot_bend_mm=round(-208.5 - 2.0 - (-230.0), 2), prev_SF_3g=SP['cases']['새 모델: 발 볼트 피벗 r143.4']['SF_3g'],
    lateral_bound_SF=round(SYA / (3 * cases['lateral_DGmax_sigma']), 1))

# ---------------------------------------------------------------- Y판 (A5052 t15)
yp = G['P_T01_YPLATE']
yh = [c for c in yp['cyl'] if abs(c['r'] - 2.25) < 0.01]
R['yplate_holes'] = sorted(set((round(c['p'][0], 2), round(c['p'][1], 2)) for c in yh))
chk('P_T01_YPLATE', '결속 구멍 수(위치)', len(R['yplate_holes']), 2, 0)
YP = json.load(open(ROOT + '/fea/results/mech_T01_fea1_handcalc.json', encoding='utf-8'))['parts']['P_T01_YPLATE']
s3, sh = YP['sigma_3g'], YP['sigma_hit']
R['parts']['P_T01_YPLATE'] = dict(material='A5052 t15', prev_sigma_3g=round(s3, 2), prev_sigma_hit=round(sh, 2),
    bound_Kt3_x_max_3g=dict(sigma=round(3 * s3, 2), SF=round(SYA / (3 * s3), 2), req=3.0),
    bound_Kt3_x_max_hit=dict(sigma=round(3 * sh, 2), SF=round(SYA / (3 * sh), 2), req=2.0),
    note='구멍 (±10, -590)은 판 가운데 줄기(|x| < 47.5), DG 바닥(±100, -800~-600) 밖 10 — 판정 띠(DG 모서리 → 블록 (±150, -860/-540), 폭 100)에서 x 90 이상 떨어짐. 보수 상한으로 최대 응력 × Kt 3을 써도 기준 넘음')

R['all_checks_ok'] = all(c['ok'] for c in R['checks'])
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('checks ok', R['all_checks_ok'], [c for c in R['checks'] if not c['ok']])
print('post', R['post_point_radius_top'], R['post_slot_half_angle_deg_r30'])
p = R['parts']['P_T01_POST']
print('POST worst dir', p['worst_load_dir_deg'], 'Znet', p['Z_net_min'], 'gross', p['gross_Z_root'])
print('POST mis nom', p['sigma_nom_net_mis'], p['SF_nom_net_mis'], 'peak gross', p['sigma_peak_gross_mis'], p['SF_peak_gross_mis'], 'peak net', p['sigma_peak_net_mis'], p['SF_peak_net_mis'])
print('POST op', p.get('F_op'), p.get('SF_peak_net_op'), 'root', p['SF_root_v0614'])
print('SPIDER holes', R['spider_holes'], json.dumps(R['parts']['P_T01_SPIDER_1~3']['holes'], ensure_ascii=False))
print('YPLATE', R['yplate_holes'], R['parts']['P_T01_YPLATE']['bound_Kt3_x_max_3g'], R['parts']['P_T01_YPLATE']['bound_Kt3_x_max_hit'])
