# T13 해석부 손계산 (v0.10.1, 헤드 받침 비틀림 상자). 해석 못 함 — 환경 없음(D-16) → 손계산만(E-18).
# 모델: 선정·모델링(tools/out/mech_T13/select_calc.py)과 같은 계열. 치수는 해석용 STEP bbox에서 다시 읽는다.
# 더한 것: (1) STEP 실측 치수로 상자 다시 계산, (2) 뒤 모서리 전단 이음(볼트) 미끄럼 시 열린 단면 상한,
#          (3) 앞판·옆판 전단 좌굴, (4) 맞댐 L 편심(29 x 29) 반영 볼트 무리, (5) L 다리 단면 응력, (6) 자중 3 g.
import json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEP = os.path.join(ROOT, 'tools', 'out', 'mech_T13', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T13_handcalc.json')
PT = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)\)")


def bbox(name):
    s = open(os.path.join(STEP, name + '.step'), errors='ignore').read()
    pts = {}
    for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)\)", s):
        pts[m.group(1)] = tuple(map(float, m.group(2, 3, 4)))
    vids = re.findall(r"VERTEX_POINT\('[^']*',\s*#(\d+)\)", s)
    p = [pts[v] for v in vids if v in pts]  # 꼭짓점만(축 원점 제외)
    return [[round(min(q[i] for q in p), 2), round(max(q[i] for q in p), 2)] for i in range(3)]


bb = {n: bbox(n) for n in ('P_T13_SLEEVE', 'P_T13_REAR', 'P_T13_FBL_T1', 'P_T13_FBL_T2')}

# ---- 하중·재료
F = 20.0                 # 끌림 N (완료 판정, D-10)
Yc = 740.0               # 기둥 중심 Y = 바늘(Y 0)에서 팔
T = F * Yc               # N*mm
G = 74.8e3; Es = 193e3; nu = 0.29; Sy = 205.0   # SUS304
t = 2.0
LIM = 0.657              # D-08 임시

# ---- (1) 닫힌 상자, STEP 실측 중심선
sl, re_ = bb['P_T13_SLEEVE'], bb['P_T13_REAR']
x_out = sl[0][1]                       # 옆판 바깥 X 92
bx = 2 * (x_out - t / 2)               # 중심선 폭
y_front = 621.0                        # 앞판 Y 620~622 (모델링 보고서 1절) 중심
y_rear = re_[1][0] + t / 2             # 뒤판 Y 780~782 중심
by = y_rear - y_front
H = re_[2][1] - (-600.0)               # 상자 높이: 머리 Z -140 ~ 580 윗면 Z -600
A = bx * by; s = 2 * (bx + by)
J = 4 * A * A * t / s
theta = T * H / (G * J)
box = dict(bx=bx, by=by, H=H, A=A, J_mm4=round(J), sway_mm=round(theta * Yc, 4),
           q_N_per_mm=round(T / (2 * A), 4), tau_MPa=round(T / (2 * A) / t, 4))

# ---- (2) 뒤 모서리(옆판–뒤판 선 맞닿음, 기둥·볼트로만 이음) 전단 흐름 전달
q = T / (2 * A)
corner_line = q * H                    # 한 모서리가 넘길 전단 N
slip = 3.5e3 * 0.2                     # M5 12.9 조임력 3.5 kN x 마찰 0.2 (선정과 같음)
per_side_bolts = 3                     # 뒤판–기둥 한 줄 3개(옆판 쪽은 4개, 불리한 쪽)
corner = dict(corner_shear_N=round(corner_line, 1), per_bolt_N=round(corner_line / per_side_bolts, 1),
              slip_sf=round(slip / (corner_line / per_side_bolts), 1))
# 상한: 이음이 미끄러져 열린 단면(U 판 + 평판)이 된다면 J_open = sum(b t^3 / 3)
b_open = bx + 2 * (by) + bx            # 앞 + 옆 2 + 뒤 (펼친 길이)
J_open = b_open * t ** 3 / 3
open_sway = T * H / (G * J_open) * Yc
corner['open_section_sway_mm_if_slipped'] = round(open_sway, 1)
corner['note'] = '닫힌 단면은 뒤 모서리 볼트가 미끄러지지 않는 것이 전제. 미끄럼 SF가 커서 성립'

# ---- (3) 전단 좌굴 (4변 단순 지지, 보수)
def tau_cr(a, b):
    a, b = max(a, b), min(a, b)
    k = 5.35 + 4.0 * (b / a) ** 2
    return k * math.pi ** 2 * Es / (12 * (1 - nu ** 2)) * (t / b) ** 2
buck = dict(front_tau_cr_MPa=round(tau_cr(H, bx), 1), side_tau_cr_MPa=round(tau_cr(H, by), 1),
            tau_MPa=box['tau_MPa'])
buck['sf'] = round(min(buck['front_tau_cr_MPa'], buck['side_tau_cr_MPa']) / box['tau_MPa'], 0)

# ---- 흔들림 합계: 580 축·굽힘·공통 몫은 바뀌지 않은 부재(구상 3 값 재사용, 선정과 같음)
c3 = json.load(open(os.path.join(ROOT, 'tools', 'out', 'mech_T13', 'v0100', 'concept3_calc.json'), encoding='utf-8'))
rail_axial = c3['base_axial']['sway_mm']; rail_bend = c3['base_580_bend']['sway_mm']
common = c3['common_reference']['beam1900_Yflex_mm'] + c3['common_reference']['rail580_X_cantilever_mm']
judge = box['sway_mm'] + rail_axial + rail_bend
total = 2 * judge + common
xslip = c3['xslip']['worst_wallbolt_only_no_leg_mm']
sway = dict(box=box['sway_mm'], rail580_axial=rail_axial, rail580_bend=rail_bend, judge=round(judge, 4),
            judge_x2=round(2 * judge, 3), common=round(common, 3), total_conservative=round(total, 3),
            xslip_upper=xslip, limit=LIM, ok=(total <= LIM and xslip <= LIM))

# ---- (4) 맞댐 L: 580 앞끝 세로 반력 + 편심
M1 = 141.6e3; M3 = 424.9e3            # 기둥 하나 무게 모멘트 1 g / 3 g (D-31)
R1 = M1 / 540.0; R3 = M3 / 540.0
fb = bb['P_T13_FBL_T2']               # X 90~135, Y 200~245
eY = 230.0 - (200.0 + t / 2)          # 다리 A 볼트 줄 Y 230 ↔ 굽힘 중심
eX = 120.0 - (90.0 + t / 2)           # 다리 B 볼트 줄 X ±120 ↔ 굽힘 중심
pitch = 40.0                          # 두 볼트 Z -660·-620
axial = 105.7                         # 상자 비틀림 축력 짝(선정)
def fbl(R):
    # 다리 B 볼트 무리가 편심 모멘트 R*eX를 면 안 짝(Z 40)으로 받음 (다리 A는 R*eY, 대칭이라 같은 크기)
    v = R / 2; h = R * max(eX, eY) / pitch
    per = math.sqrt(v ** 2 + h ** 2 + (axial / 2) ** 2)
    return per
p1 = fbl(R1); p3 = fbl(R3)
bear_allow = 1.5 * Sy
As_M5 = 14.2
fbl_res = dict(R1_N=round(R1, 1), R3_N=round(R3, 1), ecc_mm=[eX, eY],
               per_bolt_1g_N=round(p1, 1), per_bolt_3g_N=round(p3, 1),
               slip_sf_1g=round(slip / p1, 2), slip_sf_3g=round(slip / p3, 2),
               bearing_MPa_3g=round(p3 / (5 * t), 1), bearing_sf_3g=round(bear_allow / (p3 / (5 * t)), 2),
               bolt_shear_MPa_3g=round(p3 / As_M5, 1), bolt_shear_sf_3g=round(0.6 * 1080 / (p3 / As_M5), 1),
               selection_per_bolt_3g_N=397.0)
# (5) L 다리 단면(높이 72, t2) 면 안 굽힘: M = R3 * e
hL = fb[2][1] - fb[2][0]
IL = t * hL ** 3 / 12
sigL = R3 * max(eX, eY) * (hL / 2) / IL
tauL = 1.5 * R3 / (hL * t)
vm = math.sqrt(sigL ** 2 + 3 * tauL ** 2)
fbl_res.update(leg_h=hL, leg_sigma_MPa=round(sigL, 1), leg_tau_MPa=round(tauL, 1), leg_vm_MPa=round(vm, 1),
               leg_sf=round(Sy / vm, 1), edge_min_mm=15.0, edge_ratio=3.0)

# ---- (6) 자중 3 g (판 4개 질량, 모델링 실측)
mass = dict(SLEEVE=4.3975, REAR=1.3343, FBL=0.0975)
w3 = (mass['SLEEVE'] + mass['REAR']) * 9.81 * 3
sw = dict(load_3g_N=round(w3, 1), per_bolt_N=round(w3 / 14, 1), note='옆 8 + 뒤 6 볼트 미끄럼 저항 700 N/개에 비해 작다')

out = dict(note='T13 해석부 손계산 v0.10.1. 해석 못 함 — 환경 없음(D-16). 자리값: I 80 cm4(D-27), 끌림 20 N(D-10), 무게 모멘트(D-31), 조임력 3.5 kN·마찰 0.2(디테일 확인)',
           step_bbox=bb, box=box, corner=corner, buckling=buck, sway=sway, front_butt_L=fbl_res, selfweight=sw)
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('box sway', box['sway_mm'], 'total', sway['total_conservative'], 'xslip', xslip, 'ok', sway['ok'])
print('corner per bolt', corner['per_bolt_N'], 'slip sf', corner['slip_sf'], 'open-if-slipped', corner['open_section_sway_mm_if_slipped'])
print('buckling sf', buck['sf'])
print('FBL per bolt 3g', fbl_res['per_bolt_3g_N'], 'slip sf 1g/3g', fbl_res['slip_sf_1g'], fbl_res['slip_sf_3g'],
      'bearing sf', fbl_res['bearing_sf_3g'], 'leg sf', fbl_res['leg_sf'])
print('bbox', json.dumps(bb))
