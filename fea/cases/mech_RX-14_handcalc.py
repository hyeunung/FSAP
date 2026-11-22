# -*- coding: utf-8 -*-
"""RX-14 해석부 손계산 (v2.19.0, E-18). FEA 못 함 — 환경 없음(D-16).
형상: tools/out/mech_RX-14/stepout/*.step 꼭짓점(fea/results/mech_RX-14_stepgeo.json) + tools/gen_rx14.py 단면.
하중: 토글 클램프 MC01-5 체압력 196 N(catalog.md), 테이프 장력 10 N(D-06 임시), 자중 x3 g, 손 100 N(오조작, fea/models.json 선례).
기준: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-14_handcalc.py  ->  fea/results/mech_RX-14_handcalc.json"""
import json, math, sys, importlib.util
ENG = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
sp = importlib.util.spec_from_file_location("handcalc", ENG); hc = importlib.util.module_from_spec(sp); sp.loader.exec_module(hc)
OUT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-14_handcalc.json"
G = 9.80665
SUS, S45C, A5052, E_SUS, E_ST = 205.0, 345.0, 195.0, 193000.0, 205000.0
F_CL, T_TAPE, HAND = 196.0, 10.0, 100.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()}

# ---------------------------------------------------------------- 1. 카세트 판 P_RX14_KIT_PLATE (SUS304 t3)
# 받이 귀: 폭 20(X 96~116), 목 Y 15~20(Z -8~-5), 세운 살 Y 17~20, 귀 Y 17~40(Z -20~-17). 클램프 암 Y 24~36 -> 힘 자리 Y 30.
# 판은 판넬 윗면(Z -8)에 얹힘. 판넬 창 X 49~123 · Y 15~49 -> 판이 받쳐지는 끝은 Y 15.
b, t = 20.0, 3.0
Zs = b * t * t / 6
M_edge = F_CL * (30 - 15)                     # 판넬 창 끝 Y 15에서
rec("KIT_PLATE_ear_neck", F_N=F_CL, arm_mm=15.0, M_Nmm=M_edge, Z_mm3=Zs, sigma_MPa=M_edge / Zs, mat="SUS304", SF=SUS / (M_edge / Zs), need=3.0,
    note="클램프 힘이 판에 다 걸릴 때(핀이 물려 기울기를 막은 뒤). 굽힘선 2곳 응력 집중은 넣지 않음")
I_ear = b * t ** 3 / 12
rec("KIT_PLATE_ear_deflection", defl_mm=F_CL * 15 ** 3 / (3 * E_SUS * I_ear), note="목·귀를 팔 15의 외팔로 본 값(세운 살 회전 제외)")
# 하중 경로: 누르는 자리 Y 30은 받침 끝 Y 15 밖 15 mm -> 판이 Y 15 모서리를 축으로 기운다(-Y 쪽이 뜸)
M_tip = F_CL * 15
W_kit = 0.2 * G                                # 카세트 약 0.2 kg(설계안 M-06)
M_rest = W_kit * (15 - (-14))                  # 무게 중심을 판 가운데 Y -14로 봄
c_fit = 0.024                                  # 핀 Ø6 h7(0/-0.012) x 구멍 H7(+0.012/0) 가장 큰 틈
theta = c_fit / 3.0                            # 판 두께 3에서 핀이 물릴 때까지 기울기 rad
rec("KIT_clamp_load_path", clamp_Y=30.0, support_edge_Y=15.0, tip_moment_Nmm=M_tip, weight_restoring_Nmm=M_rest,
    ratio_tip_over_restoring=M_tip / M_rest, tilt_until_pin_bind_rad=theta, lift_at_plate_edge_Y_m43_mm=theta * (15 + 43),
    lift_at_binder_Y_m46_mm=theta * (15 + 46), pin_edge_force_total_N=M_tip / 3.0, pin_edge_force_each_N=M_tip / 3.0 / 2,
    clamp_force_before_bind_N=M_rest / 15.0,
    verdict="동작(하중 경로)",
    note="클램프 196 N이 받침 밖에 걸려 카세트를 판넬에 누르지 못한다. 핀이 구멍 모서리에 물릴 때까지 기울고(틈 0.024 기준 0.46도), "
         "그 뒤로는 핀 2개가 구멍 위·아래 모서리(간격 3)로 짝힘 약 980 N을 받는다. 물리기 전 누름은 무게 몫 약 4 N뿐")
# 고친 뒤(귀 끝 받이 턱 Y 44): 귀가 양쪽 받침 보
a1, b1 = 30 - 15.0, 44 - 30.0
M_fix = F_CL * a1 * b1 / (a1 + b1)
rec("KIT_PLATE_ear_after_fix_pad_Y44", M_Nmm=M_fix, sigma_MPa=M_fix / Zs, SF=SUS / (M_fix / Zs), need=3.0, hold_down_on_plate_N=F_CL * b1 / (a1 + b1),
    note="안 1: 받침 블록 포켓에 귀 끝 받이 턱(Y 40~48, 윗면 Z -20). 판 누름은 판 끝 Y 15에 약 95 N")
# 핀 MSTH6-20: 가로 힘 손 100 N(한 개가 다 받음), 받침 윗면 Z -12 ~ 판 가운데 Z -6.5 팔 5.5
Zp = math.pi * 6 ** 3 / 32
rec("KIT_pin_lateral_misuse", F_N=HAND, M_Nmm=HAND * 5.5, sigma_MPa=HAND * 5.5 / Zp, shear_MPa=HAND / (math.pi * 9), plate_bearing_MPa=HAND / (6 * 3.0),
    mat="S45C 대용(핀 강)", SF=S45C / (HAND * 5.5 / Zp), need=2.0)

# ---------------------------------------------------------------- 2. 받침 블록 P_RX14_KIT_SEAT (A5052)
# 클램프 반력(위로 196 N)이 암 자리 X 94에 걸림. 플랜지 X 51~84, M4 x4 (54.5·80.5, 22.5·40.5). 축은 플랜지 먼 끝 X 51.
arm = 94 - 51.0
l1, l2 = 80.5 - 51, 54.5 - 51
T_near = F_CL * arm * l1 / (2 * (l1 ** 2 + l2 ** 2))
R["SEAT_clamp_bolt_CB4-12"] = hc.calc(4, 5.0, T_near, torque=1.5, bolt="12.9", base="A5052", dw=7.0, dh=4.5, sf_min=3.0)
R["SEAT_clamp_bolt_CB4-12"]["_load"] = {"T_near_each_N": round(T_near, 1), "note": "지레(축 X 51). 물림 5 = 1.25d < 1.5d(RX-14-V2). 조임 1.5 N·m 가정"}
# 포켓 바닥 살 t5: 폭 33(Y 16~48, +Y 열림), X 50~122 양쪽 벽 받침, 볼트 줄 X 80.5에 2 x T_near
P = 2 * T_near; a2, b2 = 80.5 - 50, 122 - 80.5
M_fl = P * a2 * b2 / 72.0
Z_fl = (33 - 2 * 3.3) * 25 / 6
rec("SEAT_pocket_floor", P_N=P, M_Nmm=M_fl, Z_mm3=Z_fl, sigma_MPa=M_fl / Z_fl, mat="A5052", SF=A5052 / (M_fl / Z_fl), need=3.0,
    SF_if_H112_110=110 / (M_fl / Z_fl), note="단순 받침 보(구멍 Ø3.3 x2 뺀 폭). Y 16 벽 받침은 넣지 않음(보수)")
# 받침 블록 → 판넬 CB5-12 x3: 머리는 판넬 위, 탭 깊이 10, 물림 12 - 4 = 8. 설계안 값 볼트당 65 N(클램프 반력을 다 받는다고 본 보수값)
R["SEAT_bolt_CB5-12_x3"] = hc.calc(5, 8.0, F_CL / 3, torque=4.5, bolt="12.9", base="A5052", dw=8.5, dh=5.5, sf_min=3.0)

# ---------------------------------------------------------------- 3. 덮개 P_RX14_KIT_COVER (SUS304 t1)
# 옆벽·발은 X 64~124뿐. X 31~64는 폭 34(Y -37~-3) t1 판만 내민 외팔 33. 코(X 31~44) 밑면 Z 1.5, 바늘판 윗면 Z 0 -> 틈 1.5(테이프 1 있으면 0.5)
L, bw, tt = 64 - 31.0, 34.0, 1.0
Zc = bw * tt ** 2 / 6; Ic = bw * tt ** 3 / 12
k_c = 3 * E_SUS * Ic / L ** 3
F_y = SUS * Zc / L
d_y = F_y / k_c
for name, gap in (("with_tape_gap0.5", 0.5), ("no_tape_gap1.5", 1.5)):
    sig = SUS * gap / d_y
    rec("COVER_nose_bottoming_" + name, cantilever_mm=L, k_N_mm=k_c, force_to_yield_N=F_y, defl_at_yield_mm=d_y, gap_mm=gap, force_to_bottom_N=k_c * gap,
        sigma_at_bottom_MPa=sig, mat="SUS304", SF=SUS / sig, need=(3.0 if gap < 1 else 2.0),
        note=("운전: 매트가 타고 넘어 코가 테이프에 닿을 때까지 눌림" if gap < 1 else "오조작: 테이프 없이 손으로 누름(68 N이면 바늘판에 닿음, 손 100 N 기준)"))
b_engine = hc.beam(tt, bw, L, load=F_y, e=E_SUS, sy=SUS, end="cantilever", sf_min=2.0)
R["COVER_nose_handcalc_beam_check"] = b_engine
# 고친 뒤: 코 양옆에 다리(바늘판·혀에 얹힘) -> 윗판은 Y 34 경간 양쪽 받침, 손가락 폭 15, 유효 폭 = 코 길이 29
M_n = HAND / 4 * (34 - 15 / 2.0); Z_n = 29 * 1.0 / 6
rec("COVER_nose_after_fix_side_legs", M_Nmm=M_n, Z_mm3=Z_n, sigma_MPa=M_n / Z_n, SF_SUS304=SUS / (M_n / Z_n), SF_SUS304_half_hard_470=470 / (M_n / Z_n), need=2.0,
    defl_mm=HAND * 34 ** 3 / (48 * E_SUS * 29 / 12.0), note="안: 옆벽을 X 31까지 내리고(다리) 재질 SUS304-1/2H")
# 낮은 구간(X 64~124, 옆벽 있음, 윗면 Z -1 = 테이블 면 아래): 경간 34, 손 100 N
M_t = HAND / 4 * (34 - 7.5); Z_t = 49 * 1.0 / 6
rec("COVER_top_span_misuse", M_Nmm=M_t, Z_mm3=Z_t, sigma_MPa=M_t / Z_t, mat="SUS304", SF=SUS / (M_t / Z_t), need=2.0, defl_mm=HAND * 34 ** 3 / (48 * E_SUS * 49 / 12.0))

# ---------------------------------------------------------------- 4. 홈통 P_RX14_DUCT + 뚜껑 P_RX14_DUCT_LID (SUS304 t1)
# 홈통 단면: 바닥 34x1 + 벽 1x4 둘. 귀 5곳(X 200·400·600·800·960, 폭 16). 끝 외팔: 오른쪽 968~1060 = 92, 왼쪽 125~192 = 67
A1, y1, A2, y2 = 34.0, 0.5, 8.0, 3.0
yb = (A1 * y1 + A2 * y2) / (A1 + A2)
I_d = 34 / 12.0 + A1 * (yb - y1) ** 2 + 2 * (1 * 4 ** 3 / 12.0) + A2 * (y2 - yb) ** 2
c_d = 5 - yb; Z_d = I_d / c_d; I_l = 34 / 12.0; share = I_d / (I_d + I_l)
w3g = (305.8 + 263.2) / 935.0 / 1000 * G * 3
for name, Lc, floor in (("right_X968_1060", 92.0, "밑에 판넬 없음(판넬 X 약 975까지)"), ("left_X125_192", 67.0, "밑 판넬까지 틈 2")):
    M_h = HAND * Lc * share
    d_yield = SUS * Lc ** 2 / (3 * E_SUS * c_d)
    rec("DUCT_end_misuse_" + name, cantilever_mm=Lc, I_mm4=I_d, Z_mm3=Z_d, M_Nmm=M_h, sigma_MPa=M_h / Z_d, mat="SUS304", SF=SUS / (M_h / Z_d), need=2.0,
        force_to_yield_N=SUS * Z_d / Lc / share, tip_defl_at_yield_mm=d_yield, note="손 100 N 끝 누름(뚜껑 위). " + floor)
    M_w = w3g * Lc ** 2 / 2
    rec("DUCT_end_selfweight3g_" + name, w_N_mm=w3g, M_Nmm=M_w, sigma_MPa=M_w / Z_d, SF=SUS / (M_w / Z_d), need=3.0)
# 뚜껑 경간(홈통 벽 위 34), 손 100 N
rec("LID_span_misuse", M_Nmm=M_t, Z_mm3=Z_t, sigma_MPa=M_t / Z_t, mat="SUS304", SF=SUS / (M_t / Z_t), need=2.0, defl_mm=HAND * 34 ** 3 / (48 * E_SUS * 49 / 12.0),
    note="테이프 길 높이 3(테이프 1)에 처짐 0.10 -> 막지 않음")
# 귀 볼트 CB5-12 x5: 판넬 t4 탭 물림 4(0.8d). 외력은 자중·테이프뿐(1 N 안쪽) -> 조임이 지배
R["DUCT_ear_bolt_CB5-12_panel_t4"] = hc.calc(5, 4.0, 5.0, torque=4.5, bolt="12.9", base="SUS304", dw=8.5, dh=5.5, sf_min=3.0)
R["DUCT_ear_bolt_CB5-12_panel_t4"]["_note"] = "판넬 재질 SUS304로 봄(요구서 2-1 판금). 조임 4.5 N·m이면 암나사 전단이 기준 — 토크를 낮추거나 너트(RX-14-K4)"
R["DUCT_ear_bolt_CB5-12_panel_t4_2Nm"] = hc.calc(5, 4.0, 5.0, torque=2.0, bolt="12.9", base="SUS304", dw=8.5, dh=5.5, sf_min=3.0)

# ---------------------------------------------------------------- 5. R1 받침 P_RX14_R1_BRKT (SUS304 t6 ㄷ자)
# 뒷판 Y 114~120(보 앞면, CB5-16 x2 at X 1127 · Z 580/620), 팔 X 1155~1161 · Z 560~711(151), 앞판 Y 1.5~7.5, 핀 (1137, 681), 롤러 가운데 Y -20
F_op = math.sqrt(2) * T_TAPE + (31.81 + 32.98) / 1000 * G * 3      # 테이프 90도 감김 + 롤러·핀 x3 g
armR1 = 114 + 20.0
for name, F, need in (("operating", F_op, 3.0), ("misuse_hand", HAND, 2.0)):
    Za = 151 * 36 / 6.0; Ia = 151 * 216 / 12.0
    Zb = 80 * 36 / 6.0                                             # 뒷판 모서리(Z 560~640)
    sig = max(F * armR1 / Za, F * armR1 / Zb)
    rec("R1_arm_and_backplate_" + name, F_N=F, arm_mm=armR1, sigma_arm_MPa=F * armR1 / Za, sigma_back_corner_MPa=F * armR1 / Zb, mat="SUS304",
        SF=SUS / sig, need=need, defl_roller_mm=F * armR1 ** 3 / (3 * E_SUS * Ia))
    Tb = F * armR1 / 12.0 / 2                                      # 뒷판 끝 X 1115를 축으로, 볼트 X 1127 팔 12, 볼트 2
    R["R1_bolt_CB5-16_beam_" + name] = hc.calc(5, 10.0, Tb, torque=4.5, bolt="12.9", base="A5052", dw=8.5, dh=5.5, sf_min=need)
    R["R1_bolt_CB5-16_beam_" + name]["_load"] = {"T_each_N": round(Tb, 1), "note": "보 재질은 A5052 대용(M06 선례), 물림 16 - 6 = 10"}

# ---------------------------------------------------------------- 6. R2 받침 P_RX14_R2_BRKT (SUS304 t6 ㄴ자)
# 세운 판 X 1113~1161(48) · Y 1.5~7.5 · Z -244~45, 핀 Z 15 -> 발 윗면에서 259. 롤러 가운데 Y -20(판 가운데 Y 4.5에서 24.5). 발 볼트 (1130, 20·40)
H, off = 259.0, 24.5
Zw = 48 * 36 / 6.0; Iw = 48 * 216 / 12.0; Zst = 6 * 48 ** 2 / 6.0; Ist = 6 * 48 ** 3 / 12.0; J = 48 * 6 ** 3 / 3.0; Gs = 74000.0
sig_op = F_op * H / Zst + F_op * off / Zw
rec("R2_upright_operating", F_N=F_op, sigma_MPa=sig_op, tau_torsion_MPa=3 * F_op * off / (48 * 36), mat="SUS304", SF=SUS / sig_op, need=3.0,
    defl_X_mm=F_op * H ** 3 / (3 * E_SUS * Ist), twist_rad=F_op * off * H / (Gs * J), note="테이프 합력(XZ 면)을 X로 다 걸고, 치우침 24.5의 굽힘·비틀림 더함")
sig_m = HAND * H / Zw
rec("R2_upright_misuse_hand_Y", F_N=HAND, M_Nmm=HAND * H, sigma_MPa=sig_m, mat="SUS304", SF=SUS / sig_m, need=2.0, defl_Y_mm=HAND * H ** 3 / (3 * E_SUS * Iw),
    note="롤러를 축 방향(Y)으로 손 100 N. 얇은 쪽 굽힘, 탄성 처짐(되돌아옴)")
Mo = HAND * H
T_pY = Mo * 31.5 / (31.5 ** 2 + 11.5 ** 2)       # +Y로 밀 때 발 끝 Y 51.5 축, 볼트 Y 20 팔 31.5
T_mY = Mo * 38.5 / (38.5 ** 2 + 18.5 ** 2)       # -Y로 밀 때 발 끝 Y 1.5 축, 볼트 Y 40 팔 38.5
T_foot = max(T_pY, T_mY)
for tq in (4.5, 3.0):
    for le, tag in ((3.5, "CB5-12_le3.5"), (7.5, "CB5-16_le7.5")):
        k = "R2_foot_bolt_%s_%.1fNm" % (tag, tq)
        R[k] = hc.calc(5, le, T_foot, torque=tq, bolt="12.9", base="SS400", dw=8.5, dh=5.5, sf_min=2.0)
        R[k]["_load"] = {"T_worst_N": round(T_foot, 1), "note": "T너트 HNTT8-5 강(SS400 대용). 오조작 손 100 N"}

# ---------------------------------------------------------------- 7. 롤 축 P_M06_ROLL_SHAFT (S45C Ø20, 자른 뒤 Y -52~110) · 기둥 · 볼트
# 뿌리 = 플랜지 면 Y 102. 롤 가운데 Y -20(베어링 Y -46 · 4) -> 팔 122, 앞끝 Y -52 -> 팔 154
for tag, m_roll, tens in (("model_5.12kg", 5.12, T_TAPE), ("D-124_3kg", 3.0, T_TAPE)):
    m_rot = m_roll + 0.368 + 0.103 + 0.010
    Fz = m_rot * G * 3 + tens
    Zsft = math.pi * 20 ** 3 / 32; Isft = math.pi * 20 ** 4 / 64
    M = Fz * 122
    rec("SHAFT_root_operating_" + tag, F_N=Fz, arm_mm=122.0, M_Nmm=M, sigma_MPa=M / Zsft, mat="S45C", SF=S45C / (M / Zsft), SF_with_Kt2=S45C / (2 * M / Zsft), need=3.0,
        defl_roll_1g_mm=(m_rot * G) * 122 ** 3 / (3 * E_ST * Isft), before_cut_M_Nmm=Fz * 212, note="자르기 전 팔 212 -> 122(모멘트 0.58배)")
    Mm = HAND * 154 + m_rot * G * 122
    rec("SHAFT_root_misuse_" + tag, M_Nmm=Mm, sigma_MPa=Mm / Zsft, mat="S45C", SF=S45C / (Mm / Zsft), need=2.0)
    # 플랜지 CB5-16 x3 PCD 36, 플랜지 Ø50 아래 모서리 축
    Tfl = M * 43 / (43 ** 2 + 2 * 16 ** 2)
    R["SHAFT_flange_bolt_CB5-16_" + tag] = hc.calc(5, 8.0, Tfl, torque=4.5, bolt="12.9", base="A5052", dw=8.5, dh=5.5, sf_min=3.0)
    R["SHAFT_flange_bolt_CB5-16_" + tag]["_load"] = {"T_worst_N": round(Tfl, 1), "note": "기둥 A5052 t10 탭(물림 16 - 8 = 8)"}
    # 기둥 P_M06_ROLL_POST(A5052 60 x 10, 형상 그대로): 면 밖 굽힘
    Zpost = (60 - 11) * 100 / 6.0
    rec("POST_bending_operating_" + tag, M_Nmm=M, sigma_MPa=M / Zpost, mat="A5052", SF=A5052 / (M / Zpost), need=3.0, note="형상 변화 없음. 하중 팔만 줄어듦")
    # 기둥 볼트 CB5-20 x2 (Z 615/640), 밑 모서리 Z 605 축, 보 앞면 Y 120 ~ 롤 가운데 Y -20 = 140
    Mb = Fz * 140; Tpost = Mb * 35 / (35 ** 2 + 10 ** 2)
    R["POST_bolt_CB5-20_" + tag] = hc.calc(5, 10.0, Tpost, torque=4.5, bolt="12.9", base="A5052", dw=8.5, dh=5.5, sf_min=3.0)
    R["POST_bolt_CB5-20_" + tag]["_load"] = {"T_worst_N": round(Tpost, 1), "before_cut_T_N": round(Fz * 230 * 35 / (35 ** 2 + 10 ** 2), 1)}

# ---------------------------------------------------------------- 8. 걸이 P_M05_HOLDER (자른 뒤 X 10~50 · Y -100~-90 · Z 285~334)
R["HOLDER_note"] = {"verdict": "됨(하중 줄어듦)", "note": "Y < -100의 걸쇠·핀 팔을 잘라 걸쇠 당김 1,500 N과 U7 움직이는 묶음 2.5 kg이 없어졌다. 남은 판(날개 A, UPPER 체결 CB5-12 x2 장공)의 단면·체결은 "
                    "v2.6.7(REG-02 fix1) 그대로라 DC2-04 손계산(fea/results/mech_DC2-04_handcalc.json)의 하중보다 작다. 새 계산 없음(E-19)"}

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    if "SF" in v:
        print("%-46s SF %7.2f / %s  %s" % (k, v["SF"], v.get("need"), v.get("verdict")))
    elif "sf_operating" in v:
        allv = dict(v["sf_operating"]); allv.update(v["sf_tightening"])
        print("%-46s 볼트 worst %s %.2f ok=%s near=%s 물림비 %.2f" % (k, v["worst"], allv[v["worst"]], v["ok"], v["needs_fea"], v["engage_ratio"]))
    else:
        print("%-46s %s" % (k, v.get("verdict", "")))
