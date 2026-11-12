# -*- coding: utf-8 -*-
"""RX-08 해석부 손계산(2026-11-12, v2.12.1). FEA 못 함 — 환경 없음(D-16).
새 하중 부품: P_RX08_STOP_BRKT_밀링(SUS304), P_RX08_STOP_BLOCK_밀링(SUS304), P_M02_BASE(고침: M5 탭 x2, 관 장공 넓힘).
하중 길(설계안 mech_RX-08_design.md 55행): 그네 윗판 -> 볼트 머리 CB8-20 -> 블록 탑 -> 브래킷 발 윗면 -> 기둥(인장) -> 윗판 -> CB5-16 x2 -> BASE.
모델링부 handcalc_rx08.json은 1 g·0.2 MPa 한 경우(204.3 N) -> 해석부 지시 '자중 x3 g'·운전/오조작 두 경우로 다시 셈.
치수: mech_RX-08_model.md 1절 표(월드, J_U4_STOP 20 = ON 받침 자세).
실행: python -X utf8 -B fea/cases/mech_RX-08_handcalc.py
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc  # noqa: E402

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
SC = json.load(open(ROOT + '/tools/out/mech_RX-08/stop_calc.json', encoding='utf-8'))
SF_OP, SF_MIS = 3.0, 2.0          # 요구서 6-1 비어 M-09 기본값
SY = {'SUS304': 205.0, 'A5052': 195.0}
R = {'_설명': 'RX-08 해석부 손계산. 좌표 = 측정 좌표계, J_U4_X 0, J_U4_STOP 20(ON), 그네 0.95° 받침'}

# ---------- 0. 하중 ----------
ARM = 120.0 - 76.5                 # 피벗 Y 120 - 머리 +Y 끝 닿음 Y 76.5 (설계안)
st = SC['stop_reaction']
T0 = st['thick16 p0']['T_Nm']      # 무게+스프링(1 g) 몫, 두께 16이 큰 쪽
T02 = st['thick16 p0.2']['T_Nm']
k_p = (T02 - T0) / 0.2             # N·m / MPa
T_op = T02 + 2 * T0                # 운전: IR1000 상한 0.2 MPa + 무게 몫 3 g(스프링 몫까지 3배, 보수)
T_mis = T0 + k_p * 0.5 + 2 * T0    # 오조작: 공급 0.5 MPa 전부(레귤레이터 고장) + 3 g
F = {'op': T_op * 1000 / ARM, 'mis': T_mis * 1000 / ARM, '1g_0.2': T02 * 1000 / ARM, '1g_0.102': st['thick16 p0.102']['T_Nm'] * 1000 / ARM}
R['load'] = {'arm_mm': ARM, 'T_Nm': {'p0_1g': T0, 'p0.2_1g': T02, 'op': round(T_op, 3), 'mis': round(T_mis, 3)},
             'F_stop_N': {k: round(v, 1) for k, v in F.items()},
             '_note': '두께 16 매트 θ 3.751 반력(측정 4절)이 두께 10보다 큼 -> 가장 불리한 하나(E-19)'}

def sf_rec(name, sig_op, sig_mis, mat, note=''):
    s_op, s_mis = SY[mat] / sig_op, SY[mat] / sig_mis
    R[name] = {'sigma_op_MPa': round(sig_op, 1), 'sigma_mis_MPa': round(sig_mis, 1), 'SF_op': round(s_op, 2), 'SF_mis': round(s_mis, 2),
               'ok': s_op >= SF_OP and s_mis >= SF_MIS, 'yield_ok': s_mis >= 1.2, 'material': mat, 'note': note}

# 받침점(ON): 볼트 축 (X -170, Y 70) — 블록 탑 X -176.5~-163.5 · Y 64~80 밑 발 윗면
LX, LY = -170.0, 70.0
# ---------- 1. 브래킷 발(외팔 판, t12, 키 홈 깊이 3 -> t_eff 9) ----------
col = {'x': (-152.0, -140.0), 'y': (86.0, 104.0)}
d_corner = math.hypot(col['x'][0] - LX, col['y'][0] - LY)       # 받침점 -> 기둥 모서리
b_eff, t_eff = 20.0, 9.0                                        # 보수: 폭 40 중 절반, 홈 뺀 두께
Zf = b_eff * t_eff ** 2 / 6
sf_rec('brkt_foot', F['op'] * d_corner / Zf, F['mis'] * d_corner / Zf, 'SUS304',
       f'팔 = 받침점~기둥 모서리 {d_corner:.1f} mm, 단면 {b_eff}x{t_eff}(키 홈 3 뺌, 폭 절반 보수)')

# ---------- 2. 기둥(12 X x 18 Y, 인장 + 두 방향 편심 굽힘) ----------
cx, cy = sum(col['x']) / 2, sum(col['y']) / 2
ex, ey = cx - LX, cy - LY
A = 12 * 18
Zy = 18 * 12 ** 2 / 6      # X 방향 편심 굽힘(깊이 12)
Zx = 12 * 18 ** 2 / 6      # Y 방향 편심 굽힘(깊이 18)
k_col = 1 / A + ex / Zy + ey / Zx
sf_rec('brkt_column', F['op'] * k_col, F['mis'] * k_col, 'SUS304',
       f'편심 ex {ex:.0f}·ey {ey:.0f}, 바닥·꼭대기 같은 모멘트. 피벗 브래킷 B 면 닿음은 받침으로 안 셈(보수). 안쪽 모서리 R 없으면 응력 집중(정적 연성재라 SF에 안 넣음)')

# ---------- 3. 윗판(12 X x 8 Z, 기둥 Y 86~104 -> 볼트 Y 69·79) ----------
# 자른 면 Y 86: 굽힘(X축) M = F x (86 - 70), 비틀림(Y축) T = F x ex
def top_plate(t, b=12.0):
    Zb = b * t ** 2 / 6
    r = max(b, t) / min(b, t)
    alpha = 0.208 if r < 1.25 else (0.231 if r < 1.75 else 0.246)   # Roark 직사각 비틀림 tau = T/(alpha b t^2)
    Wt = alpha * max(b, t) * min(b, t) ** 2
    def vm(Fz):
        s = Fz * (col['y'][0] - LY) / Zb
        tau = Fz * ex / Wt
        return math.sqrt(s * s + 3 * tau * tau)
    return vm, Zb, Wt
vm8, Zb8, Wt8 = top_plate(8.0)
sf_rec('brkt_top_plate', vm8(F['op']), vm8(F['mis']), 'SUS304',
       f'자른 면 Y 86 굽힘 팔 {col["y"][0] - LY:.0f}, 비틀림 팔 {ex:.0f}, Zb {Zb8:.0f}, Wt {Wt8:.1f}. 볼트 둘 다 Y < 86이라 비틀림 전부가 Y 86 단면을 지남. 1 g 0.2 MPa(204 N) SF {SY["SUS304"] / vm8(F["1g_0.2"]):.2f}')
vm12, _, _ = top_plate(12.0)
R['brkt_top_plate_t12_whatif'] = {'sigma_op_MPa': round(vm12(F['op']), 1), 'sigma_mis_MPa': round(vm12(F['mis']), 1),
                                  'SF_op': round(205 / vm12(F['op']), 2), 'SF_mis': round(205 / vm12(F['mis']), 2),
                                  'note': '윗판 Z 234~242 -> Z 230~242(t12, 밑으로 4). 같은 경계조건(실형상)'}

# ---------- 4. 윗판 볼트 CB5-16 x2 (지레: 받침점 윗판 +X 끝 X -140, 볼트 X -146) ----------
lever = (-140.0 - LX) / (-140.0 + 146.0)          # 30 / 6
Tb = {k: F[k] * lever / 2 for k in ('op', 'mis')}
R['top_bolts_M5_op'] = calc(d=5, le=8, load=round(Tb['op'], 1), base='SUS304', sf_min=SF_OP)
R['top_bolts_M5_mis'] = calc(d=5, le=8, load=round(Tb['mis'], 1), base='SUS304', sf_min=SF_MIS)
R['top_bolts_M5_sep'] = {'note': 'M5 12.9 조임 7 N·m(D-108 일반값) 예압 7,000 N/개 > 오조작 볼트 힘 -> 이음 안 벌어짐(윗판을 고정단으로 본 근거)',
                         'preload_N': 7000.0, 'load_mis_N': round(Tb['mis'], 1), 'SF_sep': round(7000.0 / Tb['mis'], 2)}

# ---------- 5. P_M02_BASE (SUS304 t8): 새 M5 탭 둘레 ----------
# 캐리지 발 볼트 (-150,50)·(-150,85) 사이 양끝 고정 띠(길이 35), 볼트 힘 합 가운데, 폭 = 장공 끝 X -157 ~ -140 = 17
span, wb, tb = 35.0, 17.0, 8.0
Zbase = wb * tb ** 2 / 6
Mb = {k: 2 * Tb[k] * span / 8 for k in Tb}
sf_rec('base_tap_strip', Mb['op'] / Zbase, Mb['mis'] / Zbase, 'SUS304',
       '보수: 지레 압축(윗판 +X 끝)이 같은 띠를 밀어 올려 실제 순 하중은 F뿐 — 볼트 당김 합 전부를 띠 가운데 점하중으로 셈. 장공 X -175.5~-157이 띠 폭을 줄임')
lig = (-157.0) - (-146.0) - 2.5
R['base_slot_ligament'] = {'mm': lig, 'note': '장공 +X 끝 X -157 ~ 탭 Ø5(X -146) 사이 살 8.5 mm(> d 5)'}

# ---------- 6. 멈춤 블록 탑(13 x 16, Z 72~124) 압축·M8 탭 ----------
A_tower = 13.0 * 16.0 - math.pi / 4 * 6.8 ** 2
sf_rec('block_tower', F['op'] / A_tower, F['mis'] / A_tower, 'SUS304', 'M8 탭 구멍 Ø6.8 뺀 순 단면 압축')
R['adj_bolt_CB8_mis'] = calc(d=8, le=10.28, load=round(F['mis'], 1), base='SUS304', sf_min=SF_MIS)

# ---------- 7. 머리 모서리 닿음(그네 A5052 윗판, 0.95° 기울어 평머리 모서리 선접촉) ----------
w_c, L_c = 0.5, 13.0               # 임시: 선접촉 폭 0.5(가정), 머리 지름 13 현
pc = {k: F[k] / (w_c * L_c) for k in ('op', 'mis')}
R['head_edge_bearing'] = {'p_op_MPa': round(pc['op'], 1), 'p_mis_MPa': round(pc['mis'], 1),
                          'SF_op': round(195 / pc['op'], 2), 'SF_mis': round(195 / pc['mis'], 2),
                          'note': '접촉 폭 0.5 mm는 가정값(근거 없음). 되풀이 닿음 자국 -> 둥근 머리 스토퍼 볼트(설계안 9-2)로 없앰'}

# ---------- 8. 그네 윗판(A5052 t12) 받침점 -> 피벗 보스 굽힘 ----------
d_sw = 30.0                       # 받침점 Y 76.5 -> 보스 Ø26 끝 Y 107
b_sw = 13.0 + 2 * d_sw            # 45° 퍼짐
Zsw = b_sw * 12.0 ** 2 / 6
sf_rec('swing_plate', F['op'] * d_sw / Zsw, F['mis'] * d_sw / Zsw, 'A5052', '그네 윗판 X +끝(-161) 근처 받침, 45° 퍼짐 폭')

# ---------- 9. 실린더(완료 판정 문구) ----------
A25 = math.pi / 4 * 25 ** 2
R['cylinder'] = {'push_0.5MPa_N': round(A25 * 0.5, 1), 'need_set_0.102_x1.5_N': round(F['1g_0.102'] * 1.5, 1),
                 'SF_set': round(A25 * 0.5 / F['1g_0.102'], 2), 'SF_at_0.2': round(A25 * 0.5 / F['1g_0.2'], 2),
                 'note': '받침 면 수평 -> 실린더 축 힘 0. 짐 진 채 빼기(설계안 μ0.3 두 면) 122.6 N 밀기 SF 2.00. 전환은 들림(J_U4_PRESS 13.006)에서만'}
R['lip'] = {}
M_lip = A25 * 0.5 * 20.0
Z_lip = 40 * 10.5 ** 2 / 6
sf_rec('brkt_lip', M_lip / Z_lip, M_lip / Z_lip, 'SUS304', '립 X -268~-257.5(t10.5) 높이 Z 72~112, 실린더 축 Z 92 -> 팔 20, 추력 245 N(최대)')
del R['lip']

json.dump(R, open(ROOT + '/fea/results/mech_RX-08_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('F', {k: round(v, 1) for k, v in F.items()})
for k, v in R.items():
    if isinstance(v, dict) and 'sigma_op_MPa' in v:
        print(k, v['sigma_op_MPa'], v['sigma_mis_MPa'], 'SF', v['SF_op'], v['SF_mis'], 'ok' if v.get('ok', True) else 'NG')
    elif isinstance(v, dict) and 'sf_operating' in v:
        print(k, v['inputs']['load_N'], v['sf_operating'], v['ok'])
print('cyl', R['cylinder'])
print('t12', R['brkt_top_plate_t12_whatif'])
