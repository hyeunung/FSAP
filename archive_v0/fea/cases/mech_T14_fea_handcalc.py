# -*- coding: utf-8 -*-
"""T14 해석부(v0.8.2) — Y판 t10, DG 받침 H55 손계산. 해석 못 함 - 환경 없음(D-16).
형상은 해석용 STEP(tools/out/mech_T14/stepout)의 bbox·구멍에서 읽은 값이다.
  P_T01_YPLATE  : X ±200, Y -950~-450, Z -370~-360(t10), 창 X ±47.5 · Y -870~-665, 구멍 Ø4.2 ×2(관통 탭, YNB) · Ø4.5 ×2(결속)
  P_S01_DGSPACER: X ±100, Y -837.5~-600, Z -360~-305(H55), Ø8.5 ×4 (±85, -785/-615)
모델은 fea/models.json P_T01_YPLATE(옛 t15와 같은 모델, 두께만 바뀜) + 이번에 더한 P_S01_DGSPACER.
"""
import json, math, os, sys

sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
import handcalc  # noqa: E402

RP = 175.0          # A5052 H32 가정 Rp(보수), models.json
G = 9.81
W = 81.8            # Y판 위 얹힌 질량 kg(concept2 4-1, v0.8.2 -2.0 kg은 보수로 무시)
F_SERVO = 1080.0    # 오조작 서보 최대 힘 N(models.json)
R = {'basis': '해석 못 함 - 환경 없음(D-16). 손계산', 'Rp': RP, 'need': {'op': 3.0, 'mis': 2.0}}

def plate(t):
    out = {}
    # A. models.json 모델: DG 바닥 모서리(100,-600) -> 블록 중심(150,-540) 대각 외팔 띠 폭 100
    L = math.hypot(50, 60)
    F3 = W * G * 3
    s = (F3 / 4 * L) / (100 * t * t / 6)
    out['A_op3g'] = dict(L=L, sigma=s, SF=RP / s)
    # A 오조작: 짝힘 F x 346 / 200(받침 발자국 X 폭)의 반을 한 블록 + 1 g
    Fc = F_SERVO * 346.0 / 200.0
    s = ((Fc / 2 + W * G / 4) * L) / (100 * t * t / 6)
    out['A_mis'] = dict(couple_N=Fc, sigma=s, SF=RP / s)
    # B. 교차 모델: X 방향 띠(받침 끝 X100 -> 블록 X150, 팔 50), 폭 = 받침 Y 길이 237.5 의 반(블록 2개가 나눔 아님, 보수로 한 줄 100)
    s = (F3 / 2 / 2 * 50) / (100 * t * t / 6)
    out['B_op3g_strip_x'] = dict(sigma=s, SF=RP / s)
    # C. YNB 볼트 당김(T18 오조작 1319 N/개 x 2)이 Y판 국부 굽힘: 고정 원판 중심 집중하중(Roark 11.2 16), a=60(블록·받침까지 보수), r0'=1.6t 보정
    P = 2 * 1319.0
    a = 60.0
    r0 = 4.25  # 볼트 머리·좌면 반지름 대신 구멍 반지름(보수)
    rp = math.sqrt(1.6 * r0 ** 2 + t * t) - 0.675 * t if r0 < 0.5 * t else r0
    nu = 0.33
    s_c = 3 * P / (2 * math.pi * t * t) * (1 + nu) * math.log(a / rp)
    s_e = 3 * P / (2 * math.pi * t * t)
    out['C_YNB_local'] = dict(P_N=P, a=a, sigma_center=s_c, sigma_edge=s_e, SF=RP / max(s_c, s_e))
    # 처짐 비 (t15 기준 0.015 mm, 1 g)
    out['defl_1g_mm'] = 0.015 * (15.0 / t) ** 3
    out['defl_3g_mm'] = 3 * out['defl_1g_mm']
    return out

R['YPLATE_t10'] = plate(10.0)
R['YPLATE_t15_old'] = plate(15.0)   # 옛 형상, 같은 모델(E-18 비교)

# DG 받침 H55: 옆힘 F 서보 x 팔(매트면 0 -> 받침 밑 -360). 단면은 실측 부피/높이
A = 1706648.9 / 55.0
Zs = 940104.0       # model_handcalc 단면계수(U 발자국 200 x 237.5) — 보수 확인: 꽉 찬 사각 1.58e6의 0.6배
s = F_SERVO / A + F_SERVO * 360.0 / Zs
R['DGSPACER_H55'] = dict(A=A, Zs=Zs, sigma=s, SF=RP / s, over_spec=(RP / s) / 2.0 >= 3)
# 받침 압축(3 g 자중 + 오조작 짝힘 한쪽 몫)
s = (W * G * 3 + F_SERVO * 346.0 / 200.0) / A
R['DGSPACER_comp'] = dict(sigma=s, SF=RP / s)

# 체결: YNB CB5-16 -> Y판 관통 탭 물림 8(-370~-362), 볼트 끝 ↔ 받침 밑면 2.0. 물림은 t15 블라인드 때와 같음
R['bolt_CB5-16_YNB'] = handcalc.calc(5, 8, 1319.0, torque=4.0, bolt='12.9', base='A5052', sf_min=2.0)

# 높이 사슬
R['chain'] = dict(sum=10 + 55 + 64 + 8 + 220.5 + 12 + 0.5, expect=370.0)

OUT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_T14_fea_handcalc.json'
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
def r3(v):
    return {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()} if isinstance(v, dict) else v
for k in ('YPLATE_t10', 'YPLATE_t15_old'):
    for kk, vv in R[k].items():
        print(k, kk, r3(vv))
for k in ('DGSPACER_H55', 'DGSPACER_comp', 'chain'):
    print(k, r3(R[k]))
b = R['bolt_CB5-16_YNB']
print('bolt', b['sf_operating'], b['sf_tightening'], b['ok'])
