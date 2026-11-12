# -*- coding: utf-8 -*-
"""RX-06 해석부 손계산(2026-11-12, v2.11.0). FEA 못 함 — 환경 없음(D-16).
새·고친 하중 부품: P_RX06_CARRIAGE(A5052), P_RX06_SPACER_F·S, P_RX06_STOP_A(·B), P_M02S_CYL_BRKT(고침), P_M02_BASE(고침: 보 체결 -> 캐리지 발 매달기).
구매품 몫: SSEB13-570 블록 4, BSS2020 너트·축, BSW20·BUN20.
모델링부 handcalc_rx06.json(1 g, 하중 조합 하나)을 자중 x3 g·운전/오조작 두 경우로 다시 셈(해석부 지시 '자중 x3 g').
실행: python -X utf8 -B fea/cases/mech_RX-06_handcalc.py
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
MOD = json.load(open(ROOT + '/tools/out/mech_RX-06/model/handcalc_rx06.json', encoding='utf-8'))
g = 9.81
SF_OP, SF_MIS = 3.0, 2.0                      # 요구서 6-1 비어 M-09 기본값
SY = {'A5052': 195.0, 'SUS304': 205.0, 'S55C': 400.0}
R = {'_설명': 'RX-06 해석부 손계산. 좌표 = 측정 좌표계, J_U4_X 0(블록·캐리지·묶음이 같이 움직여 레일 하중은 J와 무관)'}

# ---------- 0. 입력 ----------
m_bundle, cg_bundle = 10.815, (-215.6, 33.6, 156.6)        # 측정 1-2(설계안 3절)
m_car, cg_car = 1.51, (-182.5, 92.0, 380.0)                 # 웹+발 형상 중심(어림)
m_nut, cg_nut = 0.6, (-182.5, 70.0, 530.0)                  # 임시(설계안)
P0 = (-182.5, 112.0, 353.0)                                 # 블록 4개 중심(X -221·-144, Z 266·440, 레일 윗면 Y 112.5 앞)
dX, dZ = 77.0 / 2, 174.0 / 2
blocks = [(sx * dX, sz * dZ) for sx in (-1, 1) for sz in (-1, 1)]
wheel = (-100.0, 0.0, 10.0)                                 # 접지점(d1 100, 바늘 줄 Y 0, 접점 Z 10 설계안)
nut_pt = (-182.5, 70.0, 530.0)
p_set_max, p_sup = 0.2, 0.5                                 # IR1000 상한, 요구서 0-6 공급
N_of_p = lambda p: 13.0 + 217.0 * p                         # M02R 설계안 레버 식
A_head, A_rod = 314.2, 235.6                                # CDQ2 Ø20 / 로드 Ø10
HAND = 100.0                                                # 오조작 손 힘(D-79), 손잡이 r 25
r_hand, lead, eta_b, eta_f = 0.025, 0.020, 0.9, 0.9
C0_prov = 2000.0                                            # SSEB13 블록 C0 보수 임시(설계안, 카탈로그 미확인)

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def blockloads(forces):
    """forces: [(point mm, F N)]. Fx는 너트가 받는다(반력으로 더함). 반환 블록별 Fy·Fz·P."""
    Fx = sum(f[0] for _, f in forces)
    forces = forces + [(nut_pt, (-Fx, 0.0, 0.0))]
    F = [sum(f[i] for _, f in forces) for i in range(3)]
    M = [0.0, 0.0, 0.0]
    for p, f in forces:
        r = tuple((p[i] - P0[i]) / 1000.0 for i in range(3))
        c = cross(r, f)
        M = [M[i] + c[i] for i in range(3)]
    sx2, sz2 = 4 * (dX/1000) ** 2, 4 * (dZ/1000) ** 2
    out = []
    for bx, bz in blocks:
        bxm, bzm = bx/1000, bz/1000
        # Mx = -sum(dz*Fy), Mz = sum(dx*Fy), My = -sum(dx*Fz)  (블록 Y 같음)
        Fy = -(F[1]/4) + (M[0]*bzm/sz2) - (M[2]*bxm/sx2)
        Fz = -(F[2]/4) + (M[1]*bxm/sx2)
        out.append({'blk': (round(P0[0]+bx, 1), round(P0[2]+bz, 1)), 'Fy': round(Fy, 1), 'Fz': round(Fz, 1), 'P': round(abs(Fy)+abs(Fz), 1)})
    return {'F_N': [round(v, 1) for v in F], 'M_Nm': [round(v, 2) for v in M], 'blocks': out,
            'P_max_N': max(b['P'] for b in out)}

def grav(k):
    return [(cg_bundle, (0, 0, -k*m_bundle*g)), (cg_car, (0, 0, -k*m_car*g)), (cg_nut, (0, 0, -k*m_nut*g))]

# ---------- 1. 레일 블록 ----------
N_op = N_of_p(p_set_max); N_mis = N_of_p(p_sup)
cases = {
    'A_들기_3g': grav(3),
    'B_운전_누름_3g(N 덜어 줌 무시)': grav(3) + [(wheel, (0.4*N_op, 18.0, 0))],
    'C_운전_누름_3g(N 반영)': grav(3) + [(wheel, (0.4*N_op, 18.0, N_op))],
    'D_오조작_공급압_전부_3g(N 무시)': grav(3) + [(wheel, (0.5*N_mis, 0.5*N_mis, 0))],
}
rail = {}
for k, fs in cases.items():
    r = blockloads(fs)
    lim = SF_MIS if k.startswith('D') else SF_OP
    r['SF_C0prov'] = round(C0_prov / r['P_max_N'], 2); r['SF_need'] = lim
    rail[k] = r
R['rail_blocks'] = rail
R['rail_note'] = {'N_op_N(0.2 MPa)': round(N_op, 1), 'N_mis_N(0.5 MPa)': round(N_mis, 1),
                  'model_1g_P_N': MOD['rail_screw']['rail']['P_block_N']}

# 레일 M3 볼트(피치 60, 레일 210 -> 4개/줄, 모델에 없음 = 디테일 D1): 레일을 떼는 힘
Fy_pull = max(max(-b['Fy'] for b in r['blocks']) for r in rail.values())
R['rail_bolt_M3'] = calc(d=3, le=5, load=round(2*Fy_pull/4, 1), base='SS400')

# ---------- 2. 볼나사·손잡이·멈춤 ----------
T_hand_mis = HAND * r_hand
Fa_mis = 2*math.pi*T_hand_mis*eta_f/lead                    # 끝 멈춤에 손 100 N으로 비틀어 붙임
Fx_op, Fx_mis = 0.4*N_op, 0.5*N_mis
T_bd = lambda F: F*lead*eta_b/(2*math.pi)
R['screw'] = {
    'Fa_hand_mis_N': round(Fa_mis, 1),
    'Fx_op_N': round(Fx_op, 1), 'Fx_mis_N': round(Fx_mis, 1),
    'T_backdrive_op_Nm': round(T_bd(Fx_op), 3), 'T_backdrive_mis_Nm': round(T_bd(Fx_mis), 3),
    'lock_need_Nm': round(max(SF_OP*T_bd(Fx_op), SF_MIS*T_bd(Fx_mis)), 3),
    'C0a_prov_N': 13000.0, 'SF_axial_mis': round(13000.0/Fa_mis, 1),
    # 손잡이 반경 방향 손 100 N, BSW20 끝(X -392)에서 손잡이 중심(-435)까지 43, 구동 저널 Ø12(D-53 STEP 실측, 모델 축은 Ø20 단순 원통)
    'journal_sigma_MPa': round(HAND*43.0/(math.pi*12**3/32), 1),
}
R['screw']['journal_SF'] = round(SY['S55C']/R['screw']['journal_sigma_MPa'], 1)
R['nut_bolts_M6'] = calc(d=6, le=11.5, load=round(Fa_mis/4, 1), base='A5052')
# BSW20 + SPACER_F: 축력이 축선(Y 70)에서 보 앞면(Y 120)까지 50 떨어져 4 x M6 중 2개가 당김(줄 간격 어림 40)
F_bsw_t = Fa_mis*0.050/0.040/2
R['bsw_spacer_bolts_M6'] = calc(d=6, le=12, load=round(F_bsw_t, 1), base='SS400')
R['spacer_bearing'] = {'note': '스페이서 F·S는 압축만(유닛 밑면 전면 접촉), 축력은 볼트 조임 마찰로 넘어감',
                       'friction_capacity_N(4 x M6 예압 6 kN x mu 0.15, 어림)': 3600.0, 'Fa_N': round(Fa_mis, 1)}
# 끝 멈춤 STOP_A·B(SUS304 X2 x Z12 x Y4.5): 블록 끝이 닿음
A_c = 12*4.5
R['stop'] = {'contact_mm2': A_c, 'p_op_MPa': round(MOD['stop']['F_axial_N']/A_c, 2), 'p_mis_MPa': round(Fa_mis/A_c, 2),
             'shear_root_MPa(멈춤 밑 12x2 단면, 고정 미정 D5)': round(Fa_mis/(12*2), 1),
             'SF_root': round(0.58*SY['SUS304']/(Fa_mis/(12*2)), 2),
             'note': '닿는 쪽 = 블록 끝(엔드캡·실, 수지). 엔드캡 허용 힘은 카탈로그에 없음 -> 디테일'}

# ---------- 3. 캐리지 ----------
Zsec = 115*12**2/6.0                                        # 웹·발 뿌리 단면 115 x 12
def car_root(fs):
    # 발 뿌리(Y 95, Z 256) 기준 X축 모멘트(묶음 + 바퀴 힘)
    pr = (0, 95.0, 256.0); Mx = 0.0
    for p, f in fs:
        r = ((p[0]-pr[0])/1000, (p[1]-pr[1])/1000, (p[2]-pr[2])/1000)
        Mx += cross(r, f)[0]
    return Mx
car = {}
for k, fs in cases.items():
    fs_b = [x for x in fs if x[0] in (cg_bundle, wheel)]
    Mx = abs(car_root(fs_b)); s = Mx*1e3/Zsec
    lim = SF_MIS if k.startswith('D') else SF_OP
    car[k] = {'Mx_root_Nm': round(Mx, 2), 'sigma_MPa': round(s, 2), 'SF': round(SY['A5052']/s, 1), 'SF_need': lim}
R['carriage_root'] = car
# 발 볼트 6 x CB5-16(윗판 SUS304 t6 탭, 물림 4): 모델링부 1 g 162.5 N을 Mx 비로 키움
Mx1 = MOD['rail_screw']['carriage']['M_root_Nm']
k_up = max(v['Mx_root_Nm'] for v in car.values())/Mx1
F_foot = MOD['foot_bolts']['F_max_N']*k_up
R['foot_bolts_M5'] = calc(d=5, le=4, load=round(F_foot, 1), base='SUS304')
R['foot_bolts_M5']['scale_from_model'] = round(k_up, 2)

# ---------- 4. 윗판 연장·실린더 브래킷 (U4 묶음 안 닫힌 고리) ----------
F_cyl_op = A_head*p_set_max; F_cyl_lift = A_rod*p_sup; F_cyl_mis = A_head*p_sup
Zp = 190*6**2/6.0
s_plate = F_cyl_mis*155/Zp                                  # 보수: 실린더 힘을 연장 끝 세로힘으로(설계안 모델과 같은 틀)
R['plate_ext'] = {'F_cyl_op_N': round(F_cyl_op, 1), 'F_lift_N': round(F_cyl_lift, 1), 'F_mis_N': round(F_cyl_mis, 1),
                  'sigma_mis_MPa': round(s_plate, 1), 'SF_mis': round(SY['SUS304']/s_plate, 1),
                  'deflection_mis_mm': round(MOD['rail_screw']['plate_ext']['deflection_mm']*F_cyl_mis/100.0, 3),
                  'gap_to_beam_mm': MOD['rail_screw']['plate_ext']['gap_to_beam_mm']}
# CYL_BRKT 세운 다리(폭 50, t6) 팔: 실린더 축 Z 223 -> 날개 Z 239 = 16(보수로 M02R 값 27도)
Zl = 50*6**2/6.0
R['cyl_brkt'] = {a: {'sigma_MPa': round(F_cyl_mis*a/Zl, 1), 'SF_mis': round(SY['SUS304']/(F_cyl_mis*a/Zl), 1)} for a in (16, 27)}
# 날개 볼트 CB5-12_M02S_CYL_3·4: 지렛대 거리 15(어림) -> 당김 2개 나눔
R['cyl_brkt_bolts_M5'] = calc(d=5, le=6, load=round(F_cyl_mis*27/15/2, 1), base='SUS304')

# ---------- 5. 판정 모음 ----------
worst = []
for k, r in rail.items(): worst.append(('블록 ' + k, r['SF_C0prov'], r['SF_need']))
for k, r in car.items(): worst.append(('캐리지 뿌리 ' + k, r['SF'], r['SF_need']))
worst += [('발 볼트 M5', R['foot_bolts_M5']['sf_operating']['암나사 전단'], SF_OP),
          ('너트 볼트 M6', R['nut_bolts_M6']['sf_operating']['암나사 전단'], SF_MIS),
          ('BSW 볼트 M6', R['bsw_spacer_bolts_M6']['sf_operating']['암나사 전단'], SF_MIS),
          ('레일 볼트 M3', R['rail_bolt_M3']['sf_operating']['암나사 전단'], SF_OP),
          ('축 저널', R['screw']['journal_SF'], SF_MIS),
          ('멈춤 뿌리', R['stop']['SF_root'], SF_MIS),
          ('윗판 연장', R['plate_ext']['SF_mis'], SF_MIS),
          ('실린더 브래킷', R['cyl_brkt'][27]['SF_mis'], SF_MIS),
          ('실린더 브래킷 볼트', R['cyl_brkt_bolts_M5']['sf_operating']['암나사 전단'], SF_MIS)]
R['summary'] = [{'item': a, 'SF': b, 'need': c, 'ok': b >= c} for a, b, c in worst]
json.dump(R, open(ROOT + '/fea/results/mech_RX-06_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for s in R['summary']:
    print(f"{s['item']}: SF {s['SF']} (기준 {s['need']}) {'OK' if s['ok'] else 'NG'}")
print('blocks P max', {k: v['P_max_N'] for k, v in rail.items()})
print('screw', R['screw']); print('stop', R['stop']['p_mis_MPa'], 'plate', R['plate_ext']['sigma_mis_MPa'])
