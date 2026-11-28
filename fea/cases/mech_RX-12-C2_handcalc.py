# -*- coding: utf-8 -*-
"""RX-12-C2 해석부 손계산 (v2.25.2 후보, E-18). FEA 못 함 — 환경 없음(D-16).
대상(새 하중 부품): P_RX12C2_LBRK_COL_U · _L (SUS304 t4, 폭 40, 다리 40, 구멍 Ø5.5)
  STEP tools/out/mech_RX-12-C2/stepout/P_RX12C2_LBRK_COL.step (원 반지름 2.75 = Ø5.5 확인)
  자리(mech_RX-12-C2_model1.md 38행): U X 1278~1318 · Y 80~120 · Z -250~-210, L Z -370~-330.
  140 윗/밑면 구멍 (1305, Y 100), 기둥 -Y 면(Y 120) 구멍 (1290, Z -230 / -350).
받는 것: R2 받이 HFS8-4080-140_RX12C2 (X 1285~1325 · Y -20~120 · Z -330~-250) 외팔 140, +Y 끝이 기둥 -Y 면 맞댐.
  그 위 P_RX14_R2_BRKT(97,204 mm3 SUS304) + R2 롤러·핀, 핀 (1312, -20, 15).
하중(fea/models.json P_RX14_R2_BRKT 칸): 테이프 합력 16.0 N at 핀 / 손 100 N Y(오조작). 자중 x3 g.
기준: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-12-C2_handcalc.py -> fea/results/mech_RX-12-C2_handcalc.json"""
import json, importlib.util
ENG = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
sp = importlib.util.spec_from_file_location("handcalc", ENG); hc = importlib.util.module_from_spec(sp); sp.loader.exec_module(hc)
OUT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-12-C2_handcalc.json"
G = 9.80665
SUS, E_SUS = 205.0, 193000.0
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()}

# ---- 자중(x3 g)
m_r2 = 97204e-9 * 7930          # R2 브래킷 0.771 kg
m_roll = 0.20                   # 롤러 Ø38 + 핀 — 가정(STEP 부피 미확인, 보수 쪽)
m_140 = 0.140 * 2.7             # HFS8-4080 약 2.7 kg/m 가정(카탈로그 값 미확인)
W_tip = (m_r2 + m_roll) * 3 * G  # 핀 자리(Y -20)에 모아 보수
W_140 = m_140 * 3 * G           # 140 가운데(팔 70)
# ---- 기하(받침점·지레)
Y_face = 120.0; Y_pin = -20.0; Z_pin = 15.0
arm_y = Y_face - Y_pin          # 140
Z_bot, Z_top = -330.0, -250.0   # 140 밑/윗면 = 맞댐 끝면의 받침 모서리
Z_bU, Z_bL = -230.0, -350.0     # 기둥 볼트 줄
lev_U = Z_bU - Z_bot            # 위 L 볼트 ~ 밑 모서리 100
lev_L = Z_top - Z_bL            # 아래 L 볼트 ~ 윗 모서리 100
T_TAPE, HAND = 16.0, 100.0


def top_L_pull(Fy_away, Fz_down):
    """-Y(기둥에서 멀어짐) 당김 Fy와 아래로 Fz -> 위 L 당김(밑 모서리 받침)."""
    M = Fy_away * (Z_pin - Z_bot) + Fz_down * arm_y + W_140 * 70
    return M, M / lev_U + Fy_away

cases = {
    "운전(테이프 16 N 을 -Y 로 다, 가장 불리)": (T_TAPE, W_tip, 3.0),
    "운전(테이프 16 N 을 아래로 다)": (0.0, W_tip + T_TAPE, 3.0),
    "오조작(손 100 N -Y 당김 + 테이프 + 자중)": (HAND + T_TAPE, W_tip, 2.0),
    "오조작(손 100 N 아래 + 테이프 + 자중)": (0.0, HAND + T_TAPE + W_tip, 2.0),
}
# L 세운 다리: 기둥 볼트(Z -230)에 물리고 꺾임(Z -250)에서 힘 -> 외팔 20(볼트 중심 기준, 보수)
b_net, t = 40.0 - 5.5, 4.0
Z_leg = b_net * t * t / 6
I_leg = b_net * t ** 3 / 12
for k, (Fy, Fz, need) in cases.items():
    M, T = top_L_pull(Fy, Fz)
    sig = T * 20.0 / Z_leg
    sig_h = T * (20.0 - 8.5 / 2) / Z_leg   # 볼트 머리 좌면 끝까지(what-if, 실형상)
    rec("LBRK_COL_U_leg | " + k, M_base_Nmm=M, T_N=T, arm_mm=20.0, Z_mm3=Z_leg, sigma_MPa=sig, SF=SUS / sig, need=need,
        SF_head_edge=SUS / sig_h, defl_tip_mm=T * 20.0 ** 3 / (3 * E_SUS * I_leg),
        roller_shift_mm=T * 20.0 ** 3 / (3 * E_SUS * I_leg) / lev_U * (Z_pin - Z_bot),
        note="세운 다리 순폭 34.5(구멍 뺌) 굽힘. 누운 다리(140 윗면)는 면내 인장이라 작음")
# 아래 L: 손 +Y 밀기(기둥 쪽) -> 윗 모서리 받침, 아래 L 당김
M = HAND * (Z_pin - Z_top) + W_tip * arm_y + W_140 * 70
T = M / lev_L
rec("LBRK_COL_L_leg | 오조작(손 100 N +Y 밀기)", M_base_Nmm=M, T_N=T, sigma_MPa=T * 20 / Z_leg, SF=SUS / (T * 20 / Z_leg), need=2.0)
# ---- 볼트(새 CB5-16 + HNTT8-5), 위 L 기둥 쪽 1개가 가장 불리(E-19)
T_max = max(v["T_N"] for k, v in R.items() if k.startswith("LBRK_COL_U"))
R["bolt_CB5-16_HNTT8-5"] = hc.calc(5, 4.0, T_max, 0.0, "12.9", "S45C", 8.5, 5.5, sf_min=2.0)
R["bolt_CB5-16_HNTT8-5"]["note"] = "T너트 물림 4 가정, 조임 토크 미정(기존 모든 CB5+HNTT8-5 와 같음) -> 운전 값만"
# ---- what-if(기록만): 손 100 N ±X 옆 -> 140 이 Z축 볼트 1개씩으로 돔(마찰로만 버팀)
M_z = HAND * arm_y
mu, Fp, r_eff = 0.2, 4000.0, 3.5
rec("whatif_X_side_100N", M_Nmm=M_z, friction_capacity_Nmm=2 * mu * Fp * r_eff,
    ratio=M_z / (2 * mu * Fp * r_eff),
    note="models.json 표 하중 방향(Y) 밖. 140 쪽 볼트가 L 하나에 1개라 Z축 돌림은 마찰뿐(예압 4 kN 가정). 디테일 기록")
rec("profile_140_bending", note="HFS8-4080 단면은 t4 판 다리보다 훨씬 커서 E-19 로 L 다리만 판정")
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    print(k, {kk: v.get(kk) for kk in ("T_N", "sigma_MPa", "SF", "SF_head_edge", "verdict", "ratio", "worst", "sf_operating") if kk in v})
