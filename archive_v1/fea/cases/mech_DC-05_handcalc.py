# -*- coding: utf-8 -*-
"""DC-05 해석부 손계산 — U1_LOWER_LINK·U1_LOWER_STAND·U1_LOWER_DRIVE (SS400, v1.0.3). FEA 환경 없음(D-16).
형상(임시 STEP tools/out/mech_DC-05/stepout/*.step, bbox = changed_parts.json):
  LINK  각관 90(Y)x60(Z) t4, X 30~650, 축선 Y0 Z-90. X 30 끝면에 아랫유닛(STEP대기_867-392342_LOWER) 맞붙음.
  STAND 80x80 기둥 X 530~610, Z -380(U2_BASE 윗면)~-120(LINK 밑면), 높이 260. 모델은 꽉 찬 차지 형상, 계획은 '판금 ㄷ + 바닥판 t4'(상세 디테일).
  DRIVE 끝판 t4 □90x60, Ø50 구멍, X 650~654. 서보 STEP대기_MHMF042L1U2M X 654~764(1.2 kg 임시, D-81).
하중(임시값, D-79·D-10):
  아랫유닛 5.1 kg(선정 6절) x 3 g, LINK 자중 x 3 g.
  운전: 노루발 누름 50 N(D-10 자리값, 침판 위 -> 아랫유닛으로 아래로) + 봉제 끌림 100 N(D-79 전부를 아래 톱니가 받는다고 봄, 작업면 Z 0, 가장 불리한 Y 방향).
  오조작: 누름 150 N(N01과 같음, 3배) + 끌림 100 N.
  서보: 1.2 kg x 3 g 끝판 밖 55 mm, 최대 토크 3.8 N·m(400 W 계열 순간 최대 임시).
판정: M-09 운전 SF 3, 오조작 SF 2(SS400 항복 245). 처짐 한도는 요구서 6-2 미정(D-08) -> 기록만, 가마↔바늘 틈 대비로 본다.
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam

E, G, SY = 205000.0, 79000.0, 245.0
g = 9.81
out = {'model': 'mech_DC-05 handcalc v1.0.3', 'fea': '해석 못 함 — 환경 없음(D-16)', 'cases': {}}

def tube(b, h, t):
    """사각관 b(Y) x h(Z) t: 굽힘 Iy(수직 굽힘), Iz(수평 굽힘), Bredt 비틀림."""
    bi, hi = b - 2 * t, h - 2 * t
    iy = (b * h ** 3 - bi * hi ** 3) / 12.0
    iz = (h * b ** 3 - hi * bi ** 3) / 12.0
    am = (b - t) * (h - t)
    per = 2 * ((b - t) + (h - t))
    j = 4 * am ** 2 * t / per
    return dict(Iy=iy, Iz=iz, Zy=iy / (h / 2), Zz=iz / (b / 2), Am=am, J=j, A=b * h - bi * hi)

def vm(s, tau):
    return math.sqrt(s ** 2 + 3 * tau ** 2)

# ---- 1) LINK 외팔 (STAND -X 면 X 530 고정 -> X 0 아랫유닛 무게중심, L 530) ----
L = 530.0
S = tube(90, 60, 4)
w_self = S['A'] * 7.85e-6 * g * 3          # N/mm, 3 g
z_off = 90.0                               # 끌림 작용 Z 0 ↔ 각관 축 Z -90
for name, press, drag, sfmin in [('LINK_run', 50, 100, 3.0), ('LINK_mis', 150, 100, 2.0)]:
    Pv = 5.1 * g * 3 + press
    Mv = Pv * L + w_self * L ** 2 / 2      # N·mm, 수직
    Mh = drag * L                          # 수평(Y 끌림)
    T = drag * z_off                       # 비틀림
    sig = Mv / S['Zy'] + Mh / S['Zz']      # 모서리 합산(보수)
    tau = T / (2 * S['Am'] * 4)
    sv = vm(sig, tau)
    dv = Pv * L ** 3 / (3 * E * S['Iy']) + w_self * L ** 4 / (8 * E * S['Iy'])
    dh = drag * L ** 3 / (3 * E * S['Iz'])
    th = T * L / (G * S['J'])
    out['cases'][name] = dict(Pv_N=round(Pv, 1), Mv_Nm=round(Mv / 1e3, 1), Mh_Nm=round(Mh / 1e3, 1), T_Nm=round(T / 1e3, 2),
                              sigma_MPa=round(sig, 2), tau_MPa=round(tau, 2), vm_MPa=round(sv, 2), SF=round(SY / sv, 1), sf_min=sfmin,
                              defl_v_mm=round(dv, 4), defl_h_mm=round(dh, 4), twist_rad=round(th, 7),
                              twist_at_needle_mm=round(th * z_off, 4))
# 처짐 중 변동분(누름 50 N 켜짐/꺼짐, 1배) — 가마↔바늘 정렬 변동
out['cases']['LINK_press_var'] = dict(dP_N=50, defl_v_mm=round(50 * L ** 3 / (3 * E * S['Iy']), 4))
out['section_LINK'] = {k: round(v, 1) for k, v in S.items()}

# ---- 2) STAND 기둥 (밑 Z -380 고정, 높이 260) ----
H = 260.0
xarm = 570.0                               # 기둥 중심 X 570 ↔ 아랫유닛 X 0
zarm = 380.0                               # 작업면 Z 0 ↔ 기둥 밑
link_w = S['A'] * 7.85e-6 * 620 * g * 3    # 각관 전체 3 g
servo_w = 1.2 * g * 3
for shape, Ss in [('closed_80x80_t4', tube(80, 80, 4)), ('solid_80x80_model', None)]:
    for name, press, drag, sfmin in [('run', 50, 100, 3.0), ('mis', 150, 100, 2.0)]:
        Pv = 5.1 * g * 3 + press
        N = Pv + link_w + servo_w
        Mxz = Pv * xarm + link_w * (570 - 340) - servo_w * (709 - 570)   # 수직 하중의 기둥 굽힘(근사)
        Myz = drag * zarm                  # Y 끌림 -> 기둥 밑 굽힘
        T = drag * xarm                    # Y 끌림 -> 기둥 비틀림(Z 축)
        if Ss is None:
            a = 80.0
            Zb = a ** 3 / 6
            A = a * a
            J = 0.1406 * a ** 4
            tau = T / (0.208 * a ** 3)
        else:
            Zb, A, J = Ss['Zy'], Ss['A'], Ss['J']
            tau = T / (2 * Ss['Am'] * 4)
        sig = N / A + Mxz / Zb + Myz / Zb
        sv = vm(sig, tau)
        th = T * H / (G * J)
        out['cases'][f'STAND_{shape}_{name}'] = dict(N_N=round(N, 1), M_vert_Nm=round(Mxz / 1e3, 1), M_drag_Nm=round(Myz / 1e3, 1),
                                                    T_Nm=round(T / 1e3, 1), sigma_MPa=round(sig, 2), tau_MPa=round(tau, 2),
                                                    vm_MPa=round(sv, 2), SF=round(SY / sv, 1), sf_min=sfmin,
                                                    twist_rad=round(th, 7), lateral_at_needle_mm=round(th * xarm, 4))

# 계획 형상 '판금 ㄷ t4'(열린 단면) 비교 — 비틀림이 약하다
t = 4.0
J_open = (80 + 80 + 80) * t ** 3 / 3
for name, drag, sfmin in [('run', 100, 3.0)]:
    T = drag * xarm
    tau = T * t / J_open
    th = T * H / (G * J_open)
    out['cases'][f'STAND_open_channel_t4_{name}'] = dict(J_mm4=round(J_open, 0), T_Nm=round(T / 1e3, 1), tau_MPa=round(tau, 1),
                                                        SF_shear=round((SY / math.sqrt(3)) / tau, 2), twist_rad=round(th, 5),
                                                        twist_deg=round(math.degrees(th), 2), lateral_at_needle_mm=round(th * xarm, 2))

# ---- 3) DRIVE 끝판 t4 (서보 무게 외팔 + 토크) ----
M_servo = servo_w * 55.0                   # N·mm 끝판 면 굽힘
# 끝판은 각관 끝 둘레에 붙음 -> 서보 플랜지 □60가 안쪽 82x52 창을 넘는 띠(위·아래 각 4)에 걸침. 보수: 폭 60 판 t4 외팔 길이 4
r = beam(t=4, b=60, length=4.0, load=M_servo / 30.0, e=E, sy=SY, sf_min=3.0)   # 위·아래 띠 짝힘(팔 30)
out['cases']['DRIVE_plate_servo_weight'] = dict(M_Nmm=round(M_servo, 1), strip=r)
tq = 3.8e3
tau_pl = tq / (2 * S['Am'] * 4)            # 토크는 끝판 -> 각관 둘레 전단
out['cases']['DRIVE_plate_torque'] = dict(T_Nm=3.8, tau_MPa=round(tau_pl, 3), SF=round((SY / math.sqrt(3)) / tau_pl, 0))

json.dump(out, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_DC-05_handcalc.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in out['cases'].items():
    print(k, {kk: vv for kk, vv in v.items() if kk in ('SF', 'SF_shear', 'vm_MPa', 'defl_v_mm', 'defl_h_mm', 'lateral_at_needle_mm', 'twist_deg')} if isinstance(v, dict) else v)
