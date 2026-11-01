# -*- coding: utf-8 -*-
"""T14 구상 3 (계면 고정·국부 보스) 손계산. 해석 못 함 - 환경 없음(D-16).
기준값은 mech_T01_fea.md 2절 표(t10 링1, t15 Y판)를 두께 비로 옮긴다.
굽힘 응력 ~ 1/t^2, 처짐 ~ 1/t^3 (같은 받침·같은 하중, 판 띠/곡선보 모델과 같음).
단차 모서리 R3 응력 집중 Kt = 1.3 (보수 자리값, 판 단차 r/t = 0.5).
"""
import json, math, os

A5052 = dict(E=70300.0, allow=175.0, rho=2.68e-6)
KT = 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'out', 'mech_T14', 'c3_handcalc.json')

R = {}
# ---------------- 링1: 웹 t10 -> t6, 받침 보스 3개(바닥 -10.5 그대로)
t0, t1 = 10.0, 6.0
sig_op0, sig_jam0, d_op0, d_jam0 = 0.87, 7.9, 0.008, 1.8      # mech_T01_fea 2절 (운전 3g / 막힘 힘 제어)
k_s, k_d = (t0 / t1) ** 2, (t0 / t1) ** 3
sig_op1, sig_jam1 = sig_op0 * k_s * KT, sig_jam0 * k_s * KT
vol0 = 2648705.8
pad_area = 80 * 32 - 4 * (8 ** 2 - math.pi * 8 ** 2 / 4)      # 반경 80 x 접선 32, 모서리 R8
pad_cb = math.pi * (9.5 / 2) ** 2                               # 카운터보어 자리(보스 안, 원래도 비어 있음)
vol1 = vol0 * (t1 / t0) + 3 * (pad_area - pad_cb) * (t0 - t1)
R['RING1'] = dict(t_web=t1, sigma_op=sig_op1, SF_op=A5052['allow'] / sig_op1, sigma_jam=sig_jam1,
                  SF_jam=A5052['allow'] / sig_jam1, defl_op_1g=d_op0 * k_d, defl_jam=d_jam0 * k_d,
                  vol0=vol0, vol1=vol1, m0=vol0 * A5052['rho'], m1=vol1 * A5052['rho'], pad_area=pad_area)

# ---------------- Y판: 패드(DG 받침 밑 210 x 245) t15, 그 밖 t10(윗면 -360). 위험 단면 = 패드 가장자리
s15_op, s15_hit, d15 = 11.8, 11.3, 0.015
# 패드 가장자리를 받침 끝보다 5 바깥에 둠 -> 외팔 길이 78 -> 73 (모멘트 비 73/78)
L0, L1 = math.hypot(50, 60), math.hypot(45, 55)
k_m = L1 / L0
s10_op = s15_op * (15 / 10) ** 2 * k_m * KT
s10_hit = s15_hit * (15 / 10) ** 2 * k_m * KT
# 처짐 상한: 외팔 전체를 t10으로 본다
d10 = d15 * (15 / 10) ** 3
vol_y0 = 2707121.4
removed = (400 * 500 - 210 * 245) * 5.0
R['YPLATE'] = dict(pad='X -105~105, Y -842.5~-597.5, top -355', web_top=-360.0, L0=L0, L1=L1,
                   sigma_op=s10_op, SF_op=A5052['allow'] / s10_op, sigma_hit=s10_hit, SF_hit=A5052['allow'] / s10_hit,
                   defl_1g_upper=d10, vol0=vol_y0, removed_upper=removed, vol1_lower=vol_y0 - removed,
                   m0=vol_y0 * A5052['rho'], m1_lower=(vol_y0 - removed) * A5052['rho'])

# ---------------- 체결 물림(M-01 >= 1.5d) - 바뀌는 것 없음 확인
R['fasteners'] = dict(
    CB5_12_RG1=dict(cb_depth=5.5, under_head_in_pad=10 - 5.5, engage_shaft=7.5, need=7.5, ok=True, note='보스 안 t10 그대로'),
    CB5_16_T18_YNB=dict(engage=8.0, need=7.5, end_to_spacer=7.0, ok=True, note='패드 안 t15 그대로'),
    MBIS5_disc=dict(insert=8, skin_above=4, ok=True, note='원판 그대로'),
    hub_M5=dict(engage=8, need=7.5, ok=True), hub_CB6_18=dict(engage=10, need=9, ok=True))

# ---------------- 스파이더 높이 정리 (식)
z_ring1_contact, shoulder_to_rod_tip, z_hub_top = -10.5, 85.0, -233.0
R['SPIDER'] = dict(z_web_top=z_ring1_contact - shoulder_to_rod_tip,
                   height=(z_ring1_contact - shoulder_to_rod_tip) - z_hub_top)
# 사슬 합
R['chain'] = dict(sum=15 + 50 + 64 + 8 + 220.5 + 12 + 0.5, expect=370.0)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if not isinstance(vv, dict)})
