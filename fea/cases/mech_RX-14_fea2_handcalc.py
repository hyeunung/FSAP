# -*- coding: utf-8 -*-
"""RX-14 해석부 수정 2회차 손계산 (v2.19.2, E-18). FEA 못 함 — 환경 없음(D-16).
바뀐 것만 다시 본다(E-21): 새 부품 P_RX14_DUCT_STRIP와 그것이 받치는 P_RX14_DUCT · P_RX14_DUCT_LID.
형상: tools/out/mech_RX-14/stepout/*.step 꼭짓점(띠 21:47, 홈통·뚜껑 21:25 — 그대로).
  띠   X 125~975 · Y -35~-5 · Z -8~-6, 따냄 R 22.5 x 8 (가운데 X 150..850 · Y -50, 현 X ±16.771)
  홈통 바닥 Z -6~-5, 벽 Y -37~-36 · -4~-3 (윗변 Z -2), 귀 Z -8~-7 (Y -3~11)
  뚜껑 Z -2~-1, Y -37~-3
하중·기준은 앞 회차와 같다: 손 100 N(오조작) SF 2, SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-14_fea2_handcalc.py -> fea/results/mech_RX-14_fea2_handcalc.json"""
import json, math
OUT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-14_fea2_handcalc.json"
SUS, SUS_H, E_SUS = 205.0, 470.0, 193000.0
HAND = 100.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}

# ================================================================ 1. F8 귀 뿌리 — 하중 경로
# 누르는 자리 Y -20 은 띠(Y -35~-5) 바로 위: 뚜껑 -> 두 벽 -> 바닥 -> 띠 -> 판넬. 귀 뿌리(Y -3) 팔 0.
rec("F8_ear_root_after_strip", load_Y=-20.0, strip_Y=[-35.0, -5.0], arm_to_ear_root_before_mm=17.0, M_ear_before_Nmm=1700.0, M_ear_after_Nmm=0.0,
    SF_before=0.64, verdict="없어짐", note="벽 가운데선 Y -36.5 · -3.5 는 띠 변 밖 1.5 — 3절")
# 귀 사이 경간 X 굽힘: 띠가 전 길이로 판넬에 얹힘 -> X 방향 경간 없음(따냄 자리는 4절)
rec("F8_midspan_Xbend_after_strip", span_before_mm=184.0, span_after_mm=0.0, SF_before=[0.63, 1.26], verdict="없어짐")

# ================================================================ 2. 뚜껑 t1, 벽 가운데선 경간 33 (앞 회차는 34로 봄 — 불리한 쪽으로 34 유지)
L, c = 34.0, 15.0                     # 경간, 손가락 폭
M_fg = HAND / 4 * (L - c / 2)         # 손가락 폭 15 에 고르게
M_pt = HAND * L / 4                   # 점 하중
b_in = 0.58 * L + 2 * c               # 안쪽 유효 폭(Westergaard 0.58 L + 2c) = 49.7 -> 앞 회차 49 와 같은 값
b_in = 49.0
b_ed = c + 0.29 * L                   # 자유 끝 변(X 125 · 975)에서: 안쪽의 반 = 24.9 (수정 1회차 덮개 코와 같은 식)
for tag, M, b in (("inner_finger15", M_fg, b_in), ("inner_point", M_pt, b_in), ("free_end_finger15", M_fg, b_ed), ("free_end_point", M_pt, b_ed)):
    sig = M / (b / 6.0)
    rec("LID_span34_" + tag, span_mm=L, eff_width_mm=b, M_Nmm=M, sigma_MPa=sig, mat="SUS304(205)", SF=SUS / sig, need=2.0,
        SF_plastic_hinge=1.5 * SUS / sig, SF_if_half_hard_470=SUS_H / sig, defl_mm=HAND * L ** 3 / (48 * E_SUS * b / 12.0), gap_under_lid_mm=3.0)
# 끝 변은 +Y 쪽이 귀(X 132~148 · 952~968, 끝에서 7)에서 조여져 한쪽 고정에 가깝다: 한쪽 고정-한쪽 받침 가운데 하중 M = 3PL/16
M_pr = 3 * HAND * L / 16 * (1 - c / (2 * L))
rec("LID_free_end_finger15_propped", M_Nmm=M_pr, sigma_MPa=M_pr / (b_ed / 6), mat="SUS304(205)", SF=SUS / (M_pr / (b_ed / 6)), need=2.0,
    note="끝에서 7 mm 자리 귀 볼트가 +Y 변을 누름 -> 실제는 단순 받침(1.28)과 이 값 사이")

# ================================================================ 3. 벽 밑 바닥 — 벽 가운데선이 띠 변 밖 1.5
M_w = HAND / 2 * 1.5
rec("FLOOR_wall_overhang_1p5", overhang_mm=1.5, F_wall_N=HAND / 2, eff_width_mm=b_in, M_Nmm=M_w, sigma_MPa=M_w / (b_in / 6.0), mat="SUS304", SF=SUS / (M_w / (b_in / 6.0)), need=2.0,
    shear_MPa=HAND / 2 / (b_in * 1.0), note="받침이라 과사양으로 세지 않음")
rec("FLOOR_wall_overhang_free_end", eff_width_mm=b_ed, sigma_MPa=M_w / (b_ed / 6.0), mat="SUS304", SF=SUS / (M_w / (b_ed / 6.0)), need=2.0)

# ================================================================ 4. 따냄 자리 8곳 (현 33.54, 깊이 Y -35 -> -27.5)
# 모델: 볼 유닛 플랜지(Ø44 · 윗면 Z -6, STEP대기_ 임시 외형)가 같은 높이에서 바닥을 받는다 -> 안 받는 띠 0.5.
# 가정값 검토(임시 외형이 달라져 플랜지가 안 받을 때): -Y 벽(1 x 4, Z -6~-2)이 현 33.54를 건너는 보. 바닥 판·뚜껑 몫은 뺀다(불리한 쪽).
chord = 2 * math.sqrt(22.5 ** 2 - 15.0 ** 2)
Zw = 1.0 * 4.0 ** 2 / 6
for tag, k in (("continuous_PL/8", 1 / 8.0), ("simple_PL/4", 1 / 4.0)):
    M = HAND / 2 * chord * k
    rec("RELIEF_wall_beam_no_flange_" + tag, chord_mm=chord, section="벽 1 x 4", Z_mm3=Zw, M_Nmm=M, sigma_MPa=M / Zw, mat="SUS304", SF=SUS / (M / Zw), need=2.0,
        note="가정값 검토(what-if) — 지금 모델은 플랜지가 받아 이 하중 경로가 없다. 수정 지시의 근거로 쓰지 않는다")
rec("RELIEF_as_modeled", unsupported_gap_mm=0.5, verdict="됨(플랜지 윗면 Z -6 이 받음, 닿음 0.0 — 검도 verify2/sum_b1.json)")

# ================================================================ 5. 눌림
rec("STRIP_bearing_on_panel", F_N=HAND, area_mm2=30.0 * 15.0, p_MPa=HAND / 450.0, mat="SUS304", SF=SUS / (HAND / 450.0), need=2.0, note="받침 — 과사양으로 세지 않음. 따냄 자리 남는 살 22.5 x 15 로는 0.30 MPa")
rec("STRIP_selfweight_3g", mass_g=382.3, F_N=0.3823 * 9.81 * 3, note="판넬에 얹힘. 점용접은 위치만 잡는다(운전 하중 없음)")

# ================================================================ 6. 높이 맞춤(정밀 체인): 귀 단 2(Z -8 -> -6, 굽힘 2번) ↔ 띠 t2
# (가) 단이 커서 띠 밑이 뜬다(틈 g): 귀 줄을 축으로 내려앉는다. 수정 1회차 값 — 항복 64 N 에서 먼 변 처짐 0.81
g_tol, d_y, F_y = 0.3, 0.81, 64.0
rec("FIT_gap_side", gap_mm=g_tol, force_to_seat_N=F_y * g_tol / d_y, ear_root_use_ratio=g_tol / d_y, far_edge_drop_at_yield_mm=d_y,
    verdict="됨(탄성 안)", note="틈 0.3 은 24 N 에 닫히고 그 뒤는 띠가 받는다. 귀 뿌리는 항복의 37 %. 틈 0.81 까지 탄성")
# (나) 단이 작아 귀가 판넬에서 뜬다(g): 볼트가 귀를 끌어내린다 — 귀 세운 다리 3, 평평한 귀 팔(뿌리 Y -3 -> 볼트 Y 5) 8
I_e = 16 * 1.0 ** 3 / 12
My = SUS * 16 * 1.0 / 6
d_ear_y = My * 8.0 ** 2 / (3 * E_SUS * I_e)       # 귀 팔 8 외팔이 항복할 때 끝 처짐
rec("FIT_lift_side", ear_arm_mm=8.0, ear_lift_at_yield_mm=d_ear_y, tol_mm=g_tol, verdict="디테일(정밀 체인)",
    note="귀가 0.045 mm 넘게 뜨면 볼트 조임이 귀를 굽혀 앉힌다(영구 굽힘, 기능은 유지 — 귀는 위치 고정용). 굽힘 공차 ±0.3(M-04)")

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    if "SF" in v:
        print("%-44s SF %6.2f / %s  sig %7.1f  %s" % (k, v["SF"], v.get("need"), v.get("sigma_MPa", v.get("p_MPa", 0)), v.get("verdict")))
    else:
        print("%-44s %s" % (k, v.get("verdict", "")))
print("chord", round(chord, 2), "b_ed", round(b_ed, 2), "ear lift at yield", round(d_ear_y, 4))
