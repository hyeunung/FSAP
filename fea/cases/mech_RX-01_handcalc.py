# -*- coding: utf-8 -*-
"""RX-01 해석부 손계산(2026-11-23, v2.22.4). FEA 못 함 — 환경 없음(D-16).
새 하중 부품: P_M08_VP_PLATE(A5052 t6 평판, 밸브 받침), P_M08_PSW_BRKT(A5052 t4 Z꼴 판금, 압력 스위치 받침).
새 체결: CB3-40 x2(밸브 -> 판 M3 탭), CB5-16 x2(판 -> 기둥 T홈 HNTT8-5), CB5-16 x2(받침 -> 보 앞벽 M5 탭), CB3-8 x2(받침 -> 스위치 몸 M3 탭).
형상 근거: STEP tools/out/mech_RX-01/stepout/*.step 의 CARTESIAN_POINT bbox(아래 step_bbox), 질량 tools/out/signatures.json.
하중: 운전 = 자중 x 3 g(밸브·스위치는 공압으로 밖에 힘을 내지 않음, 관 당김은 오조작에 포함), 오조작 = 손 100 N(RX-10과 같은 값, D-79)
  가장 불리한 점·방향. 판정 운전 SF 3 · 오조작 SF 2(요구서 6-1 비어 M-09 기본값), SF < 1.2는 영구 변형(동작).
실행: python -X utf8 -B fea/cases/mech_RX-01_handcalc.py
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SIG = json.load(open(ROOT + '/tools/out/signatures.json', encoding='utf-8'))
SF_OP, SF_MIS = 3.0, 2.0
SY_A5052, E_AL = 195.0, 70000.0
g = 9.81
F_MIS = 100.0
R = {'_설명': 'RX-01 해석부 손계산. 좌표 = 월드(측정 좌표계), REST. 운전 SF 3 · 오조작 SF 2, SF < 1.2 = 영구 변형(동작)'}


def step_bbox(name):
    """VERTEX_POINT가 가리키는 점만으로 bbox(원점·축 자리 점 제외). 면 선택은 이 bbox·법선으로(옛 좌표 재사용 금지)."""
    txt = open(ROOT + '/tools/out/mech_RX-01/stepout/%s.step' % name, encoding='utf-8', errors='replace').read()
    pts = dict((m.group(1), tuple(float(m.group(i)) for i in (2, 3, 4))) for m in
               re.finditer(r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([-0-9.E+]+),([-0-9.E+]+),([-0-9.E+]+)\)\)", txt))
    vids = re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)", txt)
    vs = [pts[v] for v in vids]
    xs, ys, zs = ([p[i] for p in vs] for i in range(3))
    return [round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3), round(min(zs), 3), round(max(zs), 3)]


def mass(key):
    for k, v in SIG.get('parts', SIG).items():
        if isinstance(v, dict) and k.endswith(key):
            return v['mass'] / 1000.0
    raise KeyError(key)


def rec(name, sf_op, sf_mis, note):
    R[name] = {'SF_op': None if sf_op is None else round(sf_op, 2), 'SF_mis': round(sf_mis, 2),
               'ok': (sf_op is None or sf_op >= SF_OP) and sf_mis >= SF_MIS,
               'yield_ok': sf_mis >= 1.2,
               'near_limit': (sf_op is not None and 0.9 * SF_OP <= sf_op <= 1.1 * SF_OP) or 0.9 * SF_MIS <= sf_mis <= 1.1 * SF_MIS,
               'note': note}


bb_plate, bb_brkt = step_bbox('P_M08_VP_PLATE'), step_bbox('P_M08_PSW_BRKT')
R['step_bbox'] = {'P_M08_VP_PLATE': bb_plate, 'P_M08_PSW_BRKT': bb_brkt}
R['step_bbox_matches_model'] = {
    'P_M08_VP_PLATE': bb_plate == [1150.0, 1190.0, 114.0, 120.0, 111.0, 249.0],
    'P_M08_PSW_BRKT': bb_brkt == [1124.0, 1158.0, 70.0, 120.0, 466.0, 552.0]}

# ---------- 밸브 쪽 ----------
m_valve = mass('STEP대기_VP342-5DZ1-01A') + mass('KQ2L08-01AS_M08V_A') + mass('KQ2L08-01AS_M08V_P') + mass('STEP대기_AN110-01_3')
m_plate = mass('P_M08_VP_PLATE')
W_op_v = (m_valve + m_plate) * 3 * g                     # N, 운전 자중 x3 g
# 운전: 밸브 무게중심 Y ~98.5(몸 가운데) -> 기둥 면 Y 120까지 팔 21.5, 판 볼트 Z 120·240 두 줄 중 위 볼트가 당김(받침점 판 아래 끝 Z 111)
arm_v = 120.0 - 98.5
T_op_plate = W_op_v * arm_v / (240.0 - 111.0)             # 판 윗볼트 당김
T_op_valve = m_valve * 3 * g * (114.0 - 98.5) / (223.0 - 129.1)  # 밸브 윗볼트(Z 223) 당김, 받침점 파일럿 밑 Z 129.1
# 오조작: DIN 끝 X 1107.3을 -Y로 100 N, 받침점 몸 +X 모서리 X 1190, 볼트 줄 X 1170(팔 20) -> 한 볼트가 다 받음(보수)
T_mis_valve = F_MIS * (1190.0 - 1107.3) / (1190.0 - 1170.0)
R['loads_valve'] = {'m_valve_kg': round(m_valve, 4), 'm_plate_kg': round(m_plate, 4), 'W_op_N': round(W_op_v, 2),
                    'T_op_plate_bolt_N': round(T_op_plate, 2), 'T_op_valve_bolt_N': round(T_op_valve, 2), 'T_mis_N': round(T_mis_valve, 1),
                    'note': 'P 엘보(X 1199.8) 당김 100 x 49.8/20 = 249 N < 413.5 N. +Y(기둥 쪽) 밂은 판·기둥 면 압축이라 볼트 몫 0'}

for tag, d, le, base, load_op, torque, dw, dh in [
        ('CB3-40 x2 (밸브 -> 판 M3 탭, 물림 6)', 3, 6.0, 'A5052', T_op_valve, 0.63, 5.5, 3.2),
        ('CB5-16 x2 (판 -> HNTT8-5, 물림 7.5)', 5, 7.5, 'S45C', T_op_plate, 3.0, 8.5, 5.5)]:
    op = calc(d, le, max(load_op, 1e-6), torque, '12.9', base, dw, dh, sf_min=SF_OP)
    mi = calc(d, le, T_mis_valve, torque, '12.9', base, dw, dh, sf_min=SF_MIS)
    R[tag] = {'operating': op, 'misuse': mi}

# 판 굽힘: 판 볼트 Z 120·240 단순보(스팬 120, 보수 — 실제는 두 볼트로 면에 눌린 고정에 가깝다), 밸브 윗볼트 Z 183(a 63·b 57)에 집중 하중
L, a = 120.0, 183.0 - 120.0
b = L - a
Zs = (40.0 - 3.0) * 6.0 ** 2 / 6.0                       # M3 탭 자리 순 단면
I = 40.0 * 6.0 ** 3 / 12.0
for case, P in [('op', T_op_valve * 2), ('mis', T_mis_valve)]:
    M = P * a * b / L
    R.setdefault('P_M08_VP_PLATE 굽힘', {})[case] = {'P_N': round(P, 2), 'M_Nmm': round(M, 1), 'sigma_MPa': round(M / Zs, 2),
                                                    'SF': round(SY_A5052 / (M / Zs), 2),
                                                    'defl_mm': round(P * a ** 2 * b ** 2 / (3 * E_AL * I * L), 3)}
pl = R['P_M08_VP_PLATE 굽힘']
rec('P_M08_VP_PLATE 굽힘 판정', pl['op']['SF'], pl['mis']['SF'],
    '단순보 스팬 120(볼트 Z 120↔240), 순 단면 37 x 6. t6 -> t5면 오조작 SF %.2f(과사양 note)' %
    (SY_A5052 / (T_mis_valve * a * b / L / ((37.0 * 25.0) / 6.0))))

# ---------- 스위치 쪽 ----------
m_sw = mass('STEP대기_ISE20-N-M-C6L-L') * 2.0             # 임시 형상 31 g -> 실물 불명이라 2배(보수)
m_br = mass('P_M08_PSW_BRKT')
# 앞 날개 스위치 무게중심 Y ~64.5, 벽 날개 뒷면 Y 120 -> 팔
arm_sw_op = 120.0 - 64.5
M_op = (m_sw * arm_sw_op + m_br * (120.0 - 95.0)) * 3 * g
M_mis = F_MIS * (120.0 - 45.0)                           # 스위치 앞 Y 45에 아래로 100 N(설계 1회차와 같음, 팔 75 보수 — 굽힘 시작 Y 116까지는 71)
Zb = 34.0 * 4.0 ** 2 / 6.0
rec('P_M08_PSW_BRKT 가로판 굽힘', SY_A5052 / (M_op / Zb), SY_A5052 / (M_mis / Zb),
    '가로판 34 x 4, 모멘트 운전 %.0f · 오조작 %.0f N·mm. 연성 재질 정하중이라 굽힘 R4 응력 집중 계수는 넣지 않음(참고: Kt 1.2면 %.2f)' %
    (M_op, M_mis, SY_A5052 / (1.2 * M_mis / Zb)))
R['P_M08_PSW_BRKT beam 도구(외팔 L 75)'] = beam(4.0, 34.0, 75.0, load=F_MIS, e=E_AL, sy=SY_A5052, end='cantilever', sf_min=SF_MIS)
# 앞 날개: -Y로 100 N이 스위치 가운데(Z 486)에, 날개 뿌리(굽힘 Z 512) 팔 26, Ø16 구멍 자리 순 폭 34 - 16 = 18
Zf = 18.0 * 4.0 ** 2 / 6.0
rec('P_M08_PSW_BRKT 앞 날개 굽힘(-Y 100 N)', None, SY_A5052 / (F_MIS * 26.0 / Zf), '순 단면 18 x 4(Ø16 구멍 자리), 팔 26')
# 받침 볼트: 지렛대 받침점 벽 날개 밑 Z 516, 볼트 Z 536 -> 팔 20, 두 볼트
T_sw_op, T_sw_mis = M_op / 20.0 / 2.0, M_mis / 20.0 / 2.0
R['CB5-16 x2 (받침 -> 보 앞벽 M5 탭 t8 SS400)'] = {
    'operating': calc(5, 8.0, T_sw_op, 3.0, '12.9', 'SS400', 8.5, 5.5, sf_min=SF_OP),
    'misuse': calc(5, 8.0, T_sw_mis, 3.0, '12.9', 'SS400', 8.5, 5.5, sf_min=SF_MIS)}
# 스위치 몸 CB3-8: 받침점 스위치 밑 Z 471, 볼트 Z 486(팔 15), 앞 Y 45 -> 뒤 Y 70 팔 25. 몸 수지 탭(임시 물림 4) — handcalc 표에 수지 'POM'(Rp 60)으로 보수(설계 1회차 30 MPa 가정은 별도 행)
T_cb38_mis = F_MIS * 25.0 / 15.0 / 2.0
T_cb38_op = m_sw * 3 * g * (70.0 - 57.5) / 15.0 / 2.0
R['CB3-8 x2 (받침 -> 스위치 몸 M3 탭, 물림 4 임시)'] = {
    'operating': calc(3, 4.0, max(T_cb38_op, 1e-6), 0.3, '12.9', 'POM', 5.5, 3.4, sf_min=SF_OP),
    'misuse': calc(3, 4.0, T_cb38_mis, 0.3, '12.9', 'POM', 5.5, 3.4, sf_min=SF_MIS),
    'resin_30MPa_check': {'A_th_mm2': round(math.pi * 3 * 4 * 0.75 * 0.5, 2),
                          'SF_mis': round(0.6 * 30.0 * math.pi * 3 * 4 * 0.75 * 0.5 / T_cb38_mis, 2),
                          'note': '몸 수지 항복 30 MPa 가정(설계 1회차) — 물림 4는 1.5d 4.5보다 짧다(임시 탭 깊이, 실물 STEP·취급설명서 대기)'}}
R['loads_switch'] = {'m_switch_kg_x2': round(m_sw, 4), 'm_brkt_kg': round(m_br, 4), 'M_op_Nmm': round(M_op, 1), 'M_mis_Nmm': round(M_mis, 1),
                     'T_bolt_op_N': round(T_sw_op, 2), 'T_bolt_mis_N': round(T_sw_mis, 1)}
R['tip_deflection_mis_mm'] = round(F_MIS * 75.0 ** 3 / (3 * E_AL * 34.0 * 4.0 ** 3 / 12.0), 3)

# ---------- 요약 ----------
rows = []
def walk(prefix, node):
    if isinstance(node, dict):
        if 'SF' in node and isinstance(node['SF'], (int, float)):
            rows.append((prefix, node['SF']))
        for k, v in node.items():
            if k in ('sf', 'SF_op', 'SF_mis') and isinstance(v, (int, float)):
                rows.append((prefix + '.' + k, v))
            elif k in ('sf_operating', 'sf_tightening') and isinstance(v, dict):
                rows.extend([(prefix + '.' + k + '.' + kk, vv) for kk, vv in v.items() if vv != float('inf')])
            elif isinstance(v, dict) and k not in ('inputs',):
                walk(prefix + '.' + k, v)
walk('', R)
R['_min_rows'] = sorted(rows, key=lambda r: r[1])[:8]
json.dump(R, open(ROOT + '/fea/results/mech_RX-01_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({'bbox_ok': R['step_bbox_matches_model'], 'min_rows': R['_min_rows']}, ensure_ascii=False, indent=0))
