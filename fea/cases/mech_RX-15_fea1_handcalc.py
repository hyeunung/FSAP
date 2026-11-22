# -*- coding: utf-8 -*-
"""RX-15 해석부 1회차 손계산 (v2.20.1, E-18). FEA 못 함 — 환경 없음(D-16).
대상: 새 하중 부품 P_RX15_BLADE_CLAMP(날 누름 판 + 등 받이 턱)와 그 체결(CB5-20_RX15 한 개).
형상: tools/out/mech_RX-15/stepout/P_RX15_BLADE_CLAMP.step 꼭짓점·원(11-23 00:38)
  판 X 124.75~128.75(t4) · Y -89.5~-76 · Z -30~-18, 턱 X 124.35~124.75 · Y -89.5~-88 · Z -30~-18
  탭 밑구멍 Ø4.2 관통(축 X, Y -82 · Z -24)
조립(mech_RX-15_design1.md 4-1, model1.md 2절): 볼트 머리(-X, POM 블록 자리파기 X 108.5) -> POM 블록 15.75 -> 날 t0.5 -> 누름 판 탭(물림 3.75).
  누름 판이 닿는 것은 날(0.0)과 볼트 나사뿐. 블록 +X 면 124.25 ↔ 턱 끝 124.35 틈 0.1.
하중: 절단 힘 H(-Y, 날 끝 Z -3.6) 임시 20~40 N(D-06), 날 변 44° 아래 힘 V = 1.04 H(설계 5절), 걸림(실린더 멈춤) H 80 N(Ø16 0.5 MPa 100.5 - 스프링 20 임시).
기준: 요구서 6-1 = M-09 기본값(일반 3, 오조작 2). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-15_fea1_handcalc.py -> fea/results/mech_RX-15_fea1_handcalc.json"""
import json, math, subprocess, sys
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/"
OUT = ROOT + "fea/results/mech_RX-15_fea1_handcalc.json"
HC = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
SUS, POM = 205.0, 60.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}

# ---------------------------------------------------------------- 0. 형상(STEP)
BOLT = (-82.0, -24.0)                     # Y, Z
TIP = (-42.5, -3.6)                       # 날 변 가운데(대기 자세, 슬라이드와 함께 움직여 상대 자리는 같다)
ry, rz = TIP[0] - BOLT[0], TIP[1] - BOLT[1]          # 39.5, 20.4
rec("geom", plate_X=[124.75, 128.75], plate_Y=[-89.5, -76.0], plate_Z=[-30.0, -18.0], ledge_X=[124.35, 124.75], ledge_Y=[-89.5, -88.0],
    tap_drill_d=4.2, bolt_YZ=list(BOLT), tip_arm_Y=ry, tip_arm_Z=rz, clamp_touches="날(0.0) · 볼트 나사뿐. 블록과 0.1 틈")

# ---------------------------------------------------------------- 1. 볼트 축(X) 둘레 모멘트
def torque(H, V):                          # Tx = ry*Fz - rz*Fy, F = (-H, -V)
    return ry * (-V) - rz * (-H)
CASES = {"H20": (20.0, 0.0, 3.0), "H40": (40.0, 0.0, 3.0), "H40_V41.6": (40.0, 41.6, 3.0), "H20_V20.8": (20.0, 20.8, 3.0),
         "jam_H80": (80.0, 0.0, 2.0), "jam_H80_V83": (80.0, 83.2, 2.0)}
for k, (H, V, need) in CASES.items():
    rec("M_" + k, H_N=H, V_N=V, Tx_Nmm=torque(H, V), need=need)

# ---------------------------------------------------------------- 2. 턱이 회전을 막는가 — 하중 경로
# 턱은 누름 판에 있고, 누름 판은 같은 볼트 한 개에만 물려 블록에 걸리는 데가 없다 -> 날 + 누름 판이 한 몸으로 볼트 축 둘레를 돈다.
# 턱 반력은 날과 누름 판 사이 안쪽 힘이라 블록으로 전달되지 않는다. 회전을 막는 것은 마찰뿐.
# 마찰 토크(예압 Fp): 날 ↔ POM 블록 면 mu 0.2 x 유효 반지름 4.5 + (가) 볼트가 함께 돌 때 머리 ↔ POM 자리 mu 0.2 x 3.5
#                                                                (나) 볼트는 서고 나사가 풀리는 쪽으로 돌 때 나사 0.26 mm (mu_t 0.15 · d2 4.48, 리드 0.127 뺌)
mu, r_face, r_head = 0.2, 4.5, 3.5
k_a = mu * r_face + mu * r_head
k_b = mu * r_face + (0.15 * 4.48 / 2 / math.cos(math.radians(30)) - 0.8 / (2 * math.pi))
rec("friction_torque_per_N", with_bolt_turning=k_a, thread_loosening=k_b, used=min(k_a, k_b))
k = min(k_a, k_b)
A_head = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
for T_Nm, relax in ((1.5, 1.0), (1.5, 0.5), (0.7, 1.0)):
    Fp = T_Nm * 1000 / (0.2 * 5) * relax
    cap = Fp * k
    row = dict(tighten_Nm=T_Nm, relax=relax, preload_N=Fp, head_seat_on_POM_MPa=T_Nm * 1000 / (0.2 * 5) / A_head, POM_Rp_MPa=POM, cap_Nmm=cap)
    for ck, (H, V, need) in CASES.items():
        row["SF_" + ck] = round(cap / abs(torque(H, V)), 3)
    rec("slip_T%.1f_relax%.1f" % (T_Nm, relax), **row)
# 판정에 쓰는 값: 조임 1.5 N·m(POM 좌면 SF 1.32가 한계), POM 크리프로 예압 반 남음
Fp = 750.0
rec("SLIP_rotation_blade", preload_N=Fp, cap_Nmm=Fp * k, M_Nmm=abs(torque(40, 0)), SF=Fp * k / abs(torque(40, 0)), need=3.0,
    SF_H20=Fp * k / abs(torque(20, 0)), SF_jam=Fp * k / abs(torque(80, 83.2)), SF_no_relax_H40=1500 * k / abs(torque(40, 0)),
    note="턱은 이 값에 기여 0. 미끄러지면 볼트 구멍(Ø5.5)으로는 회전이 안 멈춘다")
# 미끄러진 뒤 닿는 곳: 날 끝 팔 39.5
rec("slip_consequence", tip_arm_mm=ry, to_tuck_plate_gap_mm=1.2, angle_to_tuck_deg=math.degrees(1.2 / ry),
    blade_top_Z=-1.2, table_Z=0.0, angle_to_table_plane_deg=math.degrees(1.2 / ry),
    note="1.74°에서 날 밑이 접기 판 윗면(Z -9.2)에 닿거나(아래로), 날 윗변이 테이블 면 Z 0 위로 나온다(위로)")

# ---------------------------------------------------------------- 3. 턱이 블록에 걸린다고 볼 때(가정값 검토 — 수정 뒤 모습)
# 턱/핀이 블록에 물리면: 볼트 둘레 모멘트를 턱 반쪽(6, 삼각 분포 합력 팔 4)이 받는다
for ck in ("H40", "jam_H80_V83"):
    H, V, need = CASES[ck]
    M = abs(torque(H, V)); RL = M / 4.0
    rec("ledge_if_keyed_" + ck, M_Nmm=M, R_ledge_N=RL, bearing_mean_MPa=RL / (0.4 * 6), bearing_peak_MPa=2 * RL / (0.4 * 6),
        SF=SUS / (RL / (0.4 * 6)), need=need, SF_peak=SUS / (2 * RL / (0.4 * 6)), root_shear_MPa=RL / (1.5 * 6), SF_root_shear=0.577 * SUS / (RL / (1.5 * 6)),
        lip_bend_MPa=RL * 0.2 / (6 * 1.5 ** 2 / 6), bolt_side_reaction_N=RL - H, blade_hole_bearing_MPa=(RL - H) / (0.5 * 5.0))
# 맞춤 핀 2개(Ø2, Y -82 · Z -28.5 · -15, 간격 13.5 — 볼트 구멍 Ø5.5 가장자리와 살 0.75, 섕크 밑변과 0.5) 안
for ck in ("H40", "jam_H80_V83"):
    H, V, need = CASES[ck]
    M = abs(torque(H, V)); Fpin = M / 13.5 + math.hypot(H, V) / 2
    rec("fix_two_pins_" + ck, pin_d=2.0, spacing=13.5, F_pin_N=Fpin, POM_bearing_MPa=Fpin / (2 * 8), SF=POM / (Fpin / (2 * 8)), need=need,
        blade_bearing_MPa=Fpin / (0.5 * 2), pin_shear_MPa=Fpin / math.pi)

# ---------------------------------------------------------------- 4. 누름 판 몸·탭
for T_Nm in (1.5, 0.7):
    out = subprocess.run([sys.executable, "-X", "utf8", "-B", HC, "--d", "5", "--pitch", "0.8", "--le", "3.75", "--load", "40", "--torque", str(T_Nm),
                          "--bolt", "12.9", "--base", "SUS304", "--dw", "8.5", "--dh", "5.5"], capture_output=True, text=True, encoding="utf-8").stdout
    R["tap_SUS304_T%.1f" % T_Nm] = json.loads(out)
    out = subprocess.run([sys.executable, "-X", "utf8", "-B", HC, "--d", "5", "--pitch", "0.8", "--le", "3.75", "--load", "40", "--torque", str(T_Nm),
                          "--bolt", "12.9", "--base", "POM", "--dw", "8.5", "--dh", "5.5"], capture_output=True, text=True, encoding="utf-8").stdout
    R["head_seat_POM_T%.1f" % T_Nm] = json.loads(out)["sf_tightening"]
A_face = 12.0 * 12.0 - math.pi * 2.75 ** 2
rec("clamp_face_pressure", preload_N=1500.0, area_mm2=A_face, p_MPa=1500.0 / A_face, note="날을 사이에 둔 평면 눌림. 누름 판 굽힘 없음(뒤가 블록 면)")
rec("self_weight_3g", mass_g=4.76, F_N=4.76e-3 * 9.81 * 3, note="무시")
rec("overspec", note="누름 판 t4는 나사 물림(3.75, 0.75d)이 정한다 — 줄일 두께 없음. 오히려 물림 1.5d(M-01) 미달")

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for key in ("M_H40", "M_H40_V41.6", "M_jam_H80_V83", "friction_torque_per_N", "SLIP_rotation_blade", "slip_consequence", "ledge_if_keyed_H40", "ledge_if_keyed_jam_H80_V83", "fix_two_pins_H40", "fix_two_pins_jam_H80_V83", "clamp_face_pressure"):
    print(key, json.dumps(R[key], ensure_ascii=False))
for key in ("tap_SUS304_T1.5", "tap_SUS304_T0.7"):
    print(key, R[key]["sf_tightening"], R[key]["sf_operating"], R[key]["engage_ratio"])
print("head_seat_POM", R["head_seat_POM_T1.5"], R["head_seat_POM_T0.7"])
