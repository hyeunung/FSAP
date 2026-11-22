# -*- coding: utf-8 -*-
"""RX-14 해석부 수정 1회차 손계산 (v2.19.1, E-18). FEA 못 함 — 환경 없음(D-16).
바뀐 5부품만 다시 본다(E-21): P_RX14_KIT_SEAT · KIT_PLATE · KIT_COVER · DUCT · DUCT_LID.
형상: tools/out/mech_RX-14/stepout/*.step(2026-11-22 21:25) 꼭짓점 + tools/gen_rx14.py · gen_rx14_fix1.py 단면.
하중·기준은 첫 회차(fea/cases/mech_RX-14_handcalc.py)와 같다: 클램프 196 N, 손 100 N(오조작), 운전 SF 3 · 오조작 SF 2, SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-14_fea1_handcalc.py -> fea/results/mech_RX-14_fea1_handcalc.json"""
import json, math, importlib.util
ENG = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
sp = importlib.util.spec_from_file_location("handcalc", ENG); hc = importlib.util.module_from_spec(sp); sp.loader.exec_module(hc)
OUT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-14_fea1_handcalc.json"
SUS, SUS_H, A5052, E_SUS, G_SUS = 205.0, 470.0, 195.0, 193000.0, 74000.0
F_CL, HAND = 196.0, 100.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}

# ================================================================ F1 클램프 하중 경로 (KIT_PLATE 귀 Y 17~48, KIT_SEAT 턱 X 94~122 · Y 40~48 · 윗면 Z -20)
# STEP: KIT_PLATE y 최대 48, z -20(귀 밑) / KIT_SEAT x 94, y 40·48, z -20(턱 윗면). 판넬 창 모서리 Y 15, 클램프 힘 Y 30.
b, t = 20.0, 3.0
Zs, Is = b * t * t / 6, b * t ** 3 / 12
for tag, ys in (("ledge_mid_Y44", 44.0), ("ledge_inner_edge_Y40", 40.0)):
    a1, b1 = 30 - 15.0, ys - 30.0
    L = a1 + b1
    M = F_CL * a1 * b1 / L
    rec("F1_ear_two_supports_" + tag, support_Y=[15.0, ys], clamp_Y=30.0, hold_down_on_panel_edge_N=F_CL * b1 / L, ledge_reaction_N=F_CL * a1 / L,
        tip_moment_Nmm=0.0, M_Nmm=M, Z_mm3=Zs, sigma_MPa=M / Zs, mat="SUS304", SF=SUS / (M / Zs), need=3.0,
        defl_at_clamp_mm=F_CL * a1 ** 2 * b1 ** 2 / (3 * E_SUS * Is * L),
        note="힘 자리 Y 30이 두 받침(Y 15 · 턱) 사이 -> 기울이는 모멘트 0. 첫 회차는 받침 밖 15 mm였다")
rec("F1_ledge_bearing", reaction_N=F_CL * 15 / 29, area_mm2=20.0 * 8.0, p_MPa=F_CL * 15 / 29 / 160.0, mat="A5052", SF=A5052 / (F_CL * 15 / 29 / 160.0), need=3.0,
    note="귀 폭 20 x 턱 Y 8. 턱은 포켓 바닥(Z -27)에서 솟은 살 7이라 눌림만")
# 받침 블록 볼트: 힘 고리가 판넬을 사이에 두고 닫힌다(판이 위에서 94.6 N, 블록이 밑에서 94.6 N). 볼트 몫은 첫 회차 보수값(196/3 = 65.3 N, SF 68.9) 안쪽 -> 새 계산 없음(E-19)
rec("F1_seat_bolt_note", net_up_on_seat_N=F_CL - F_CL * 15 / 29, verdict="됨(첫 회차 값 안쪽)",
    note="클램프 반력 196 N 위로 - 턱 누름 101.4 N 아래로 = 94.6 N이 블록을 판넬 밑면에 누른다. CB5-12 x3은 첫 회차 65.3 N/개 계산(운전 최저 68.9)보다 작다")
# 높이 맞춤 민감도(정밀 체인): 귀 밑면(판금 굽힘 2번 너머 Z -20)과 턱 윗면(밀링)이 안 맞아 틈 g가 있을 때
a, Lt = 15.0, 29.0
c_tip = a ** 3 / (3 * E_SUS * Is) + a ** 2 * (Lt - a) / (2 * E_SUS * Is)      # 클램프 힘 1 N당 귀 끝(Y 44) 처짐
g_elastic = F_CL * c_tip                                                    # 귀가 휘어서 메울 수 있는 틈
theta_bind = 0.024 / 3.0                                                    # 핀 물림 기울기(첫 회차와 같은 값)
g_bind = theta_bind * Lt
rows = []
for g in (0.05, 0.1, 0.2, 0.3):
    tilt = min(max(g - g_elastic, 0.0) / Lt, theta_bind)
    rows.append({"gap_mm": g, "binder_lift_Y_m46_mm": round(tilt * 61, 3), "pin_bind": bool(g - g_elastic >= g_bind)})
rec("F1_height_match_sensitivity", ear_tip_defl_per_N_mm=c_tip, gap_closed_by_ear_bending_mm=g_elastic, gap_at_pin_bind_mm=g_bind + g_elastic,
    force_to_close_0p3_gap_by_bending_N=0.3 / c_tip, table=rows, sheet_bend_tolerance_mm=0.3, binder_margin_mm=0.5,
    verdict="디테일(정밀 체인)",
    note="틈이 0.061 mm보다 크면 귀가 휘어서는 못 메우고 판이 Y 15 모서리로 기운다(틈 0.3에서 바인더 쪽 0.49 mm 들리고 핀이 다시 물린다). "
         "판금 굽힘 너머 공차 ±0.3(M-04)이라 턱 높이는 조정식(세트 스크루 받이 · 심)이어야 한다. 귀가 0.3 낮으면(턱에 먼저 닿음) 판 +Y 변이 떠서 클램프가 귀를 휘어 내린다 - 이쪽은 안 기운다")

# ================================================================ F2 덮개 코 (KIT_COVER 다리 Y -37~-36 · -4~-3, X 31~64. STEP: z 0.0 · -0.5 꼭짓점 생김)
# 윗판 t1: 다리 사이 안쪽 경간 32, 가운데선 33. 코 길이(X) 33
Lc, bx = 33.0, 33.0
Z_full = bx * 1.0 / 6
M_pt, M_fg = HAND * Lc / 4, HAND / 4 * (Lc - 15 / 2.0)
b_edge = 15 + 0.29 * Lc                                    # 끝(X 31 자유 변)을 누를 때 유효 폭: 손가락 15 + 경간의 0.29
for tag, M, bw in (("center_point_load_full_width", M_pt, bx), ("center_finger15_full_width", M_fg, bx), ("free_edge_point_load", M_pt, b_edge), ("free_edge_finger15", M_fg, b_edge)):
    sig = M / (bw / 6.0)
    rec("F2_nose_top_on_legs_" + tag, span_mm=Lc, eff_width_mm=bw, M_Nmm=M, sigma_MPa=sig, mat="SUS304-1/2H(470)", SF=SUS_H / sig, need=2.0,
        SF_if_SUS304_annealed=SUS / sig, defl_mm=HAND * Lc ** 3 / (48 * E_SUS * bw / 12.0))
# handcalc.py beam은 외팔·guided만 있어 양쪽 받침 보에는 쓰지 않았다(식 PL/4 직접)
sig_w = M_pt / (b_edge / 6.0)
rec("F2_nose_operating_allowable", yield_force_N=SUS_H * (b_edge / 6.0) * 4 / Lc, allowable_at_SF3_N=SUS_H * (b_edge / 6.0) * 4 / Lc / 3, gap_under_top_mm=1.5, tape_mm=1.0,
    defl_at_100N_worst_mm=HAND * Lc ** 3 / (48 * E_SUS * b_edge / 12.0),
    note="매트가 타고 넘는 힘은 유연체라 모델로 판정하지 않음(요구서 7절). 다리가 받쳐 코가 테이프를 누르지 않는다(100 N 처짐 0.19 < 틈 0.5)")
# 다리: t1 x 높이 1.5(X 31~46), 눌림·가로
rec("F2_leg_compression", F_each_N=HAND / 2, area_mm2=1.0 * 15, p_MPa=HAND / 2 / 15.0, SF=SUS_H / (HAND / 2 / 15.0), need=2.0, note="X 31~46의 15 mm가 바늘판 Z 0에 얹힘. 좌굴 없음(높이 1.5 = 두께의 1.5배)")
rec("F2_nose_lateral_Y_hand", M_Nmm=HAND * 33, Z_mm3=1.0 * 34 ** 2 / 6, sigma_MPa=HAND * 33 / (34 ** 2 / 6.0), SF=SUS_H / (HAND * 33 / (34 ** 2 / 6.0)), need=2.0,
    note="코 끝을 Y로 손 100 N: 윗판 면 안 굽힘(폭 34), 뿌리 X 64")

# ================================================================ F3 홈통·뚜껑 (X 125~975, 귀 6: X 140·200·400·600·800·960, 폭 16, +Y 쪽에만)
A1, y1, A2, y2 = 34.0, 0.5, 8.0, 3.0
yb = (A1 * y1 + A2 * y2) / (A1 + A2)
I_d = 34 / 12.0 + A1 * (yb - y1) ** 2 + 2 * (1 * 4 ** 3 / 12.0) + A2 * (y2 - yb) ** 2
c_top = 5 - yb; Z_d = I_d / c_top; I_l = 34 / 12.0; share = I_d / (I_d + I_l)
# (가) 끝 외팔 7 — X 방향 굽힘(수정 대상이던 것)
for tag, Lx in (("left_X125_132", 7.0), ("right_X968_975", 7.0)):
    M = HAND * Lx * share
    rec("F3_end_cantilever_Xbend_" + tag, cantilever_mm=Lx, Z_mm3=Z_d, M_Nmm=M, sigma_MPa=M / Z_d, mat="SUS304", SF=SUS / (M / Z_d), need=2.0,
        before_fix_SF=(0.43 if "left" in tag else 0.32))
# (나) 귀가 +Y 한쪽에만 있다 — 귀 자리에서 뚜껑 가운데(Y -20)를 누르면 귀 뿌리(Y -3, 단면 16 x 1)가 Y 방향 외팔 뿌리가 된다. 바닥 밑 판넬까지 틈 2
arm = 17.0                                                 # Y -20 -> 귀 뿌리 Y -3
M_ear = HAND * arm
Z_ear = 16 * 1.0 / 6
My_one = SUS * Z_ear
n_ear = 2                                                  # 홈통 귀 + 뚜껑 귀(겹쳐 같이 조임)
SF_y = n_ear * My_one / M_ear
SF_p = 1.5 * n_ear * My_one / M_ear                        # 직사각 단면 소성 힌지(형상 계수 1.5)
th_y = My_one * 3.0 / (E_SUS * 16 / 12.0)                  # 귀 세운 다리 3 mm의 항복 회전
d_floor = (HAND / 2 * 0.64) * 33 ** 3 / (3 * E_SUS * 40 / 12.0)   # 바닥 판(유효 폭 40) Y 방향 휨, 항복 하중에서
rec("F8_ear_root_one_sided_hand_at_ear", arm_mm=arm, M_Nmm=M_ear, ear_section="16 x 1 (홈통 귀) + 16 x 1 (뚜껑 귀)", My_each_Nmm=My_one,
    force_to_first_yield_N=n_ear * My_one / arm, force_to_plastic_hinge_N=1.5 * n_ear * My_one / arm, mat="SUS304", SF=SF_y, SF_plastic_hinge=SF_p, need=2.0,
    far_edge_drop_at_yield_mm=th_y * 34 + d_floor, gap_to_panel_mm=2.0, rotation_until_floor_touches_panel_rad=2 / 34.0,
    note="-Y 쪽(Y -37)에 받침이 없어 홈통·뚜껑이 귀 줄(Y -3)을 축으로 한쪽으로 매달려 있다. 귀 6곳 어디서나 같고, 끝 귀(X 140 · 960)도 같다. "
         "항복 때 먼 변 처짐이 틈 2보다 작아 판넬이 받기 전에 귀가 꺾인다(꺾인 뒤 2 mm에서 판넬에 닿아 멈춤). 첫 회차에서 못 본 하중 경로다(끝 외팔만 봤다)")
# (다) 귀 사이 경간(가운데선 200, 안쪽 184) 가운데를 누를 때 — X 방향 굽힘 + 한쪽 받침 비틀림
Ls = 184.0
for tag, k in (("fixed_ends_PL/8", 1 / 8.0), ("continuous_0.171PL", 0.171), ("simple_PL/4", 1 / 4.0)):
    M = HAND * Ls * k * share
    rec("F8_midspan_Xbend_" + tag, span_mm=Ls, M_Nmm=M, sigma_MPa=M / Z_d, mat="SUS304", SF=SUS / (M / Z_d), need=2.0)
J_d, J_l = (34 + 4 + 4) * 1.0 / 3, 34 * 1.0 / 3
T_half = HAND * arm / 2
tw_duct_only = T_half * (Ls / 2) / (G_SUS * J_d)
tw_both = T_half * (Ls / 2) / (G_SUS * (J_d + J_l))
rec("F8_midspan_torsion", T_each_side_Nmm=T_half, J_duct_mm4=J_d, J_lid_mm4=J_l, twist_rad_duct_only=tw_duct_only, twist_rad_duct_plus_lid=tw_both,
    far_edge_drop_mm=[tw_both * 34, tw_duct_only * 34], gap_to_panel_mm=2.0, tau_MPa=T_half * 1.0 / (J_d + J_l),
    defl_at_yield_simple_mm=SUS * Ls ** 2 / (12 * E_SUS * c_top), ear_root_SF_with_half_torque=n_ear * My_one / T_half,
    note="열린 얇은 단면이라 비틀림이 무르다: 100 N에서 먼 변이 1.4~2.6 mm 내려와 판넬(틈 2)에 닿을 수 있다(비틀림 전단 34 MPa, 탄성). "
         "X 방향 굽힘 항복 처짐은 0.75 mm(단순 받침)로 틈 2보다 작다 -> 판넬이 받기 전에 벽 윗변이 항복할 수 있다(끝 조건에 따라 SF 0.63~1.26)")
# (라) 고친 뒤: 바닥 밑 전 길이 받침(t2 띠 또는 바닥을 판넬에 얹음) -> 손 하중은 뚜껑 경간 34만 남는다(첫 회차 값)
M_t = HAND / 4 * (34 - 7.5); Z_t = 49 * 1.0 / 6
rec("F8_after_fix_floor_supported", lid_span_mm=34.0, sigma_MPa=M_t / Z_t, SF=SUS / (M_t / Z_t), need=2.0, wall_compress_MPa=HAND / 2 / (1.0 * 49),
    note="안 1: 바닥 밑 t2 받침 띠(폭 30, 전 길이, 점용접 또는 판넬에 접착). 안 2: 홈통 바닥을 Z -8~-7로 내려 판넬에 얹고 카세트 입구에서 2 올림. "
         "안 3: -Y 쪽에도 발(볼트 없음)을 귀 자리마다 + 경간 가운데 — 경간 84로 줄어도 단순 받침 SF 1.38이라 모자람")
# 발만 더하는 안 3의 수치
M3 = HAND * 84 / 4 * share
rec("F8_option3_feet_span84_simple", sigma_MPa=M3 / Z_d, SF=SUS / (M3 / Z_d), need=2.0)

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    if "SF" in v:
        print("%-52s SF %6.2f / %s  %s" % (k, v["SF"], v.get("need"), v.get("verdict")))
    else:
        print("%-52s %s" % (k, v.get("verdict", str({kk: v[kk] for kk in list(v)[:4]}))[:110]))
