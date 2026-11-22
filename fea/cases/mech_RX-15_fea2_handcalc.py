# -*- coding: utf-8 -*-
"""RX-15 해석부 2회차 손계산 (v2.20.2, E-18). FEA 못 함 — 환경 없음(D-16).
대상(새 하중 부품 STEP 5개, 11-23 01:33): P_RX15_CUT_SLIDE · P_RX15_BLADE · P_RX15_BLADE_CLAMP · P_RX15_BLADE_PIN_L · _U
형상은 STEP 꼭짓점·원에서 읽음(옛 좌표 재사용 안 함):
  슬라이드(POM): 혀 X 107~117 · Y -230~-91 · Z -18.2~-12.2(10 x 6), 가로 팔 X 95~124.25 · Y -91~-81, 블록 X 106~124.25 · Y -91~-76 · Z -40~-12.2,
                 핀 기둥 X 97.6~100.6 · Y -87.5~-83.5 · Z -12.2~-5.5, 로드 탭 밑구멍 r 2.1 축 Y (X 112, Z -33.7) Y -91~-83,
                 날 핀 구멍 r 1.0 축 X (Y -82, Z -30 · -16) X 116.25~124.25, 볼트 구멍 r 2.75, 와셔 자리 r 4.75 X 106~109.5
  날(SK5 t0.5): 섕크 Y -88~-76 · Z -33~-1.2, 팔 Y -76~-40 · Z -8~-1.2(높이 6.8), 날 변 (-45, -1.2)~(-40, -6), 핀 구멍 r 1.0 둘, 볼트 구멍 r 2.75
  누름 판(SUS304): X 124.75~128.75 · Y -89.5~-76 · Z -33~-18, 탭 밑구멍 r 2.1, 핀 도피 r 1.3
  핀(SUS304): r 1.0, X 116.25~126.25
  받침 P_RX15_CUT_BASE(같은 폴더 STEP, 상대 부품): 홈 X 106.8~117.2 · Z -18.4~-12, Y -232~-93. 판넬 P_M04_PANEL_E2 Z -12~-8(홈 뚜껑, 핀 기둥 장공 +Y 끝 Y -43.5)
  실린더 CJ2B16-60SZ: 축 Y (X 112, Z -33.7), 코 끝 Y -104, 로드 끝 대기 Y -84, 로드 Ø5(카탈로그 기억값, catalog.md)
하중: 절단 힘 H(-Y, 날 변 가운데 Y -42.5 · Z -3.6) 20~40 N 임시(D-06), 날 변 44° 아래 힘 V = 1.04 H(설계 수정 1 7절),
      실린더 Ø16 x 0.5 MPa 100.5 N - 스프링 20(임시) = 80.5 N(멈춤·걸림). 걸림에서 절단 힘은 안내 마찰을 빼고 49 N(설계 7절 비 66.2/40), 위쪽 값 80 N.
기준: 요구서 6-1 = M-09 기본값(일반 3, 오조작·걸림 2). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-15_fea2_handcalc.py -> fea/results/mech_RX-15_fea2_handcalc.json"""
import json, math, subprocess, sys
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/"
OUT = ROOT + "fea/results/mech_RX-15_fea2_handcalc.json"
HC = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
SUS, POM, SK5 = 205.0, 60.0, 1000.0          # Rp MPa. POM·SK5(열처리 어림, 설계 7절)는 임시
E_POM, E_SUS, E_ST, E_AL = 2800.0, 193000.0, 206000.0, 69000.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}


THRUST = math.pi / 4 * 16 ** 2 * 0.5
F_STOP = THRUST - 20.0
CASES = {"H20": (20.0, 20.8, 3.0), "H40": (40.0, 41.6, 3.0), "jam_H49": (49.0, 51.0, 2.0), "jam_H80_upper": (80.0, 83.2, 2.0)}
rec("loads", thrust_N=THRUST, spring_N_tmp=20.0, stop_N=F_STOP, V_over_H=1.04, jam_H_with_guide_friction=F_STOP / (66.2 / 40.0))

# ================================================================ 1. 맞춤 핀 2개 (v2.20.2)
PIN_Z = (-30.0, -16.0); PIN_Y = -82.0; TIP = (-42.5, -3.6)
cy, cz = PIN_Y, sum(PIN_Z) / 2
ry, rz = TIP[0] - cy, TIP[1] - cz                      # 39.5, 19.4
SP = PIN_Z[1] - PIN_Z[0]                              # 14
for k, (H, V, need) in CASES.items():
    M = ry * (-V) - rz * (-H)                          # X 축 둘레
    Fmax = max(math.hypot(-H / 2 + s * M / SP, -V / 2) for s in (1, -1))
    p_u = Fmax / (2.0 * 8.0)
    p_edge = p_u * (4 + 6 * 0.25 / 8.0)                # 외팔로 박힌 핀, e 0.25 · L 8 (검도 RX-15-V6 식)
    rec("pin_" + k, M_Nmm=M, F_pin_N=Fmax, POM_bearing_uniform_MPa=p_u, SF=POM / p_u, need=need,
        POM_bearing_edge_MPa=p_edge, SF_edge=POM / p_edge, edge_verdict=verdict(POM / p_edge, need),
        blade_hole_bearing_MPa=Fmax / (2.0 * 0.5), SF_blade_hole=SK5 / (Fmax / 1.0),
        pin_shear_MPa=Fmax / math.pi, SF_pin_shear=0.577 * SUS / (Fmax / math.pi),
        pin_bend_MPa=Fmax * 0.25 * 32 / (math.pi * 8), SF_pin_bend=SUS / (Fmax * 0.25 * 32 / (math.pi * 8)),
        blade_shearout_MPa=Fmax / (2 * 5.0 * 0.5), note="핀만으로(볼트 마찰 0). 날 구멍 옆 살 5.0 · 밑 살 2.0 · 볼트 구멍과 2.25")
# 핀 Ø3이면(가장자리 눌림)
for k in ("H40", "jam_H49"):
    F = R["pin_" + k]["F_pin_N"]
    rec("pin_d3_" + k, edge_MPa=F / (3 * 8) * (4 + 6 * 0.25 / 8), SF=POM / (F / (3 * 8) * (4 + 6 * 0.25 / 8)), need=CASES[k][2])

# ================================================================ 2. 날 (SK5 t0.5)
Zarm = 0.5 * 6.8 ** 2 / 6; Iarm = 0.5 * 6.8 ** 3 / 12
for k, (H, V, need) in CASES.items():
    Mr = V * (TIP[0] + 76.0) - H * 1.0                 # 팔 뿌리 Y -76, 도심 Z -4.6, H는 Z -3.6
    s = Mr / Zarm + H / (0.5 * 6.8)
    rec("blade_arm_root_" + k, M_Nmm=Mr, sigma_MPa=s, SF=SK5 / s, need=need, tip_defl_mm=V * 33.5 ** 3 / (3 * E_ST * Iarm),
        note="SK5 내력 1,000 MPa 어림(임시). HRC 50 이상(약 1,400)이면 SF x 1.4")
# 섕크: 핀 줄(구멍 Ø2 뺀 순단면, 폭 12)
Znet = 0.5 * (12 ** 3 - 2 ** 3) / 12 / 6.0
for k, (H, V, need) in CASES.items():
    M = abs(ry * (-V) - rz * (-H))
    rec("blade_shank_net_" + k, M_Nmm=M, sigma_MPa=M / Znet, SF=SK5 / (M / Znet), need=need)
Iw = 6.8 * 0.5 ** 3 / 12
rec("blade_buckling", Pcr_free_N=math.pi ** 2 * E_ST * Iw / (4 * 36 ** 2), Pcr_guided_N=math.pi ** 2 * E_ST * Iw / (0.7 * 36) ** 2,
    SF_guided_H40=math.pi ** 2 * E_ST * Iw / (0.7 * 36) ** 2 / 40, SF_guided_jam49=math.pi ** 2 * E_ST * Iw / (0.7 * 36) ** 2 / 49,
    note="틈 안내(카세트 판·덮개 0.25)에 기댄다 — 설계 7절과 같음, 변화 없음")

# ================================================================ 3. 슬라이드 (POM) — 실린더 추력 경로
# 3-1 로드 탭 M5 x 8 (POM)
out = subprocess.run([sys.executable, "-X", "utf8", "-B", HC, "--d", "5", "--pitch", "0.8", "--le", "8", "--load", "%.1f" % F_STOP, "--torque", "0.5",
                      "--bolt", "A2-70", "--base", "POM", "--dw", "8", "--dh", "5"], capture_output=True, text=True, encoding="utf-8").stdout
try: R["rod_tap_POM"] = json.loads(out)
except Exception: R["rod_tap_POM"] = {"raw": out[:400]}
A_th = math.pi * 5.0 * 8.0 * 0.5                       # 암나사 전단 어림(지름 x 물림 x 0.5)
rec("rod_tap_POM_shear", load_N=F_STOP, area_mm2=A_th, tau_MPa=F_STOP / A_th, SF=0.577 * POM / (F_STOP / A_th), need=3.0, engage_ratio=8 / 5.0)
# 3-2 멈춤(핀 기둥 3 x 4, 판넬 t4 장공 끝) — 사이클마다 걸림
arm = (-10.0) - (-12.2)
s_col = F_STOP * arm / (3 * 4 ** 2 / 6.0)
rec("stop_column", F_N=F_STOP, arm_mm=arm, bend_MPa=s_col, shear_MPa=F_STOP / 12.0, bearing_MPa=F_STOP / (3 * 4.0), SF=POM / s_col, need=3.0,
    note="설계 7절은 65 N · 팔 2로 SF 3.7. 실린더 효율을 빼지 않은 80.5 N · 팔 2.2(판넬 두께 가운데). 충격 계수는 안 넣음")
# 3-3 가로 팔(블록 옆 X 106에서 기둥 X 99.1까지 6.9, 단면 Y 10 x Z 6)
rec("cross_arm", bend_MPa=F_STOP * 6.9 / (6 * 10 ** 2 / 6.0), torsion_MPa=F_STOP * 5.2 / (0.237 * 10 * 6 ** 2), SF=POM / (F_STOP * 6.9 / 100.0), need=3.0)
# 3-4 멈춤 자세의 혀(로드 Z -33.7 ↔ 기둥 Z -10 어긋남): 앞이 들림 -> 블록 윗면이 판넬 밑(틈 0.2)에 닿고 혀가 받침 앞끝 Y -93에서 바닥을 누름
M_stop = F_STOP * (18.5 + 5.2)
P = M_stop / 57.0                                      # 블록 앞끝 Y -36 ↔ 받침 앞끝 Y -93
rec("tongue_at_stop", M_Nmm=M_stop, couple_N=P, root_M_Nmm=P * 42, sigma_MPa=P * 42 / 60.0, SF=POM / (P * 42 / 60.0), need=3.0,
    note="사이클마다. 변형은 틈 0.2로 묶임")

# ================================================================ 4. 절단 아래 힘 V를 누가 받나 (하중 경로)
# 가동 묶음(슬라이드 + 날)에 걸리는 것: 날 끝 (-H, -V), 로드 축력(+Y, Z -33.7). 날 끝은 블록 뒷면(로드 너트 자리)보다 48.5 앞.
# 안내: (가) POM 혀 10 x 6이 받침 홈(바닥 틈 0.2, 뚜껑 = 판넬 밑 틈 0.2)에, (나) 블록에 M5로 꽉 물린 실린더 로드 Ø5(코 끝 Y -104에서 외팔)
I_t = 10 * 6 ** 3 / 12.0; Z_t = 10 * 6 ** 2 / 6.0
I_r = math.pi * 5 ** 4 / 64; Z_r = math.pi * 5 ** 3 / 32
BUSH = 0.006                                           # 로드 부시 틈 rad(U6S 때 값, 임시)
rows = {}
for s in (20.0, 36.0):                                 # 자르는 구간 CUT 6.6~36(날 ↔ 테이프 모형 겹침 1.7 -> 15.0에서 되짚음)
    Lr = 13.0 + s                                      # 코 끝 -> 블록 뒷면
    Lt = s - 2.0                                       # 받침 앞끝 Y -93 -> 혀 뿌리
    for k, (H, V, need) in CASES.items():
        Mb = V * 48.5 - H * 30.1                       # 블록 뒷면에서(앞 숙임 +). 30.1 = 날 끝 Z -3.6 ↔ 로드 Z -33.7
        # (가) 혀만(로드가 굽힘을 안 받는다고 볼 때): 받침 앞끝 단면
        Mg = V * (48.5 + Lt) - H * 30.1
        th_t = (Mb * Lt + V * Lt ** 2 / 2) / (E_POM * I_t)
        w_t = (Mb * Lt ** 2 / 2 + V * Lt ** 3 / 3) / (E_POM * I_t)
        tip_t = w_t + th_t * 48.5
        # (나) 로드만(혀는 틈 0.2 안에서 뜬다)
        Mn = V * (48.5 + Lr) - H * 30.1
        th_r = (Mb * Lr + V * Lr ** 2 / 2) / (E_SUS * I_r)
        w_r = (Mb * Lr ** 2 / 2 + V * Lr ** 3 / 3) / (E_SUS * I_r)
        tip_r = w_r + th_r * 48.5
        w_mouth = max(0.0, (V * (Lr - Lt) ** 2 / 6 * (3 * Lr - (Lr - Lt)) + Mb * (Lr - Lt) ** 2 / 2) / (E_SUS * I_r)) if Lr > Lt else 0.0
        sig_r = Mn / Z_r
        rows["s%d_%s" % (s, k)] = dict(H=H, V=V, rod_free_mm=Lr, tongue_free_mm=Lt,
            tongue_only=dict(M_at_guide_mouth_Nmm=round(Mg, 1), sigma_MPa=round(Mg / Z_t, 1), SF=round(POM / (Mg / Z_t), 2), tip_drop_mm=round(tip_t, 2)),
            rod_only=dict(side_load_N=V, M_at_nose_Nmm=round(Mn, 1), sigma_MPa=round(sig_r, 1), SF_yield_205=round(SUS / sig_r, 2), SF_yield_450=round(450 / sig_r, 2),
                          SF_collapse_205=round(1.7 * SUS / sig_r, 2), tip_drop_elastic_mm=round(tip_r, 2), tip_drop_with_bush_play_mm=round(tip_r + BUSH * (Lr + 48.5), 2),
                          tongue_at_guide_mouth_drop_mm=round(w_mouth, 3)), need=need)
R["down_force_path"] = rows
w = rows["s36_H40"]; j = rows["s36_jam_H49"]; l = rows["s36_H20"]
rec("DOWN_FORCE_GUIDE", SF=w["rod_only"]["SF_yield_205"], need=3.0, SF_H20=l["rod_only"]["SF_yield_205"], SF_jam49=j["rod_only"]["SF_yield_205"],
    SF_H40_Rp450=w["rod_only"]["SF_yield_450"], SF_jam49_Rp450=j["rod_only"]["SF_yield_450"],
    side_load_N_H20_H40_jam=[l["V"], w["V"], j["V"]], tip_drop_rod_mm_H20_H40_jam=[l["rod_only"]["tip_drop_with_bush_play_mm"], w["rod_only"]["tip_drop_with_bush_play_mm"], j["rod_only"]["tip_drop_with_bush_play_mm"]],
    tip_drop_tongue_only_mm_H20_H40=[l["tongue_only"]["tip_drop_mm"], w["tongue_only"]["tip_drop_mm"]], gap_blade_to_tuck_plate_mm=1.2, edge_height_mm=4.8,
    note="CUT 36(자르기 끝). 로드 Rp 205는 SUS304 풀림값(엔진 표), 450은 냉간 인발 어림 — 둘 다 임시. 로드 Ø5는 카탈로그 기억값")
# 아래 힘 비(날 변 마찰)에 따른 민감도: V/H = 1/tan(44° + 마찰각)
sens = {}
for mu in (0.0, 0.15, 0.3):
    r = 1 / math.tan(math.radians(44) + math.atan(mu)); H = 40.0; V = r * H; Lr = 49.0
    Mn = V * (48.5 + Lr) - H * 30.1
    sens["mu%.2f" % mu] = dict(V_over_H=round(r, 3), side_load_N=round(V, 1), rod_sigma_MPa=round(Mn / Z_r, 1), SF_yield_205=round(SUS / (Mn / Z_r), 2))
R["down_force_sensitivity_H40"] = sens
# 가로(X): 날 X 124.5 ↔ 로드 X 112 -> 500 N·mm(40 N)
My = 40.0 * 12.5; Lr = 49.0
rec("yaw_H40", M_Nmm=My, tip_side_mm=My * Lr ** 2 / 2 / (E_SUS * I_r) + My * Lr / (E_SUS * I_r) * 48.5, slot_gap_mm=0.25, note="날이 틈 0.25 안에서 옆 면에 닿음. 핀 기둥 ↔ 장공 0.3")

# 고친 뒤 모습(가정값 검토)
# (a) 날 밑 받침(고정, 날 팔 밑 Z -8): V가 받침으로 바로 간다. 받침 반력 = V x 팔 비
# (b) 혀를 금속으로 + 틈 줄임: 혀만으로 받을 때
fix = {}
for nm, E, Rp in (("POM 10x6(지금)", E_POM, POM), ("POM 10x12", E_POM, POM), ("A6061-T6 10x6", E_AL, 240.0), ("SUS304 10x6", E_SUS, SUS)):
    h = 12.0 if "x12" in nm else 6.0
    I = 10 * h ** 3 / 12; Z = 10 * h ** 2 / 6; H, V, Lt = 40.0, 41.6, 34.0
    Mb = V * 48.5 - H * 30.1; Mg = V * (48.5 + Lt) - H * 30.1
    tip = (Mb * Lt ** 2 / 2 + V * Lt ** 3 / 3) / (E * I) + (Mb * Lt + V * Lt ** 2 / 2) / (E * I) * 48.5
    fix[nm] = dict(tip_drop_mm=round(tip, 2), sigma_MPa=round(Mg / Z, 1), SF=round(Rp / (Mg / Z), 2), play_tilt_tip_mm=round(0.4 / (137 - 36) * (48.5 + 34 + 101 / 2), 2))
R["fix_tongue_material_H40_s36"] = fix
rec("fix_blade_rest", note="날 팔 밑(Z -8)에 고정 받침: V 41.6 N이 받침으로 감. 받침 면 0.5 x 5 = 2.5 mm² -> 16.6 MPa, 미끄럼 마찰 0.15 x 41.6 = 6.2 N(추력 여유에서 뺌)",
    bearing_MPa=41.6 / 2.5, friction_N=0.15 * 41.6)

# ================================================================ 5. 누름 판 · 자중
rec("clamp", note="Z -33까지 늘림 + 핀 도피 Ø2.6. 하중 경로에서 빠짐(날은 핀이 건다) — 누르는 일만. 탭 물림 3.75(0.75d)는 1회차 A2 그대로", face_mm2=13.5 * 15 - math.pi * 2.75 ** 2 - math.pi * 1.3 ** 2)
rec("self_weight_3g", slide_g=22.6, blade_g=2.3, clamp_g=5.9, F_N=(22.6 + 2.3 + 5.9) * 1e-3 * 9.81 * 3, note="0.9 N — 무시")

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for key in ("loads", "pin_H40", "pin_jam_H49", "pin_jam_H80_upper", "pin_d3_jam_H49", "blade_arm_root_H40", "blade_arm_root_jam_H49", "blade_shank_net_jam_H49", "blade_buckling",
            "rod_tap_POM_shear", "stop_column", "cross_arm", "tongue_at_stop", "DOWN_FORCE_GUIDE", "down_force_sensitivity_H40", "yaw_H40", "fix_tongue_material_H40_s36"):
    print(key, json.dumps(R[key], ensure_ascii=False))
for k, v in rows.items(): print(k, json.dumps(v, ensure_ascii=False))
print("rod_tap handcalc", {k: R["rod_tap_POM"].get(k) for k in ("sf_tightening", "sf_operating", "engage_ratio")})
