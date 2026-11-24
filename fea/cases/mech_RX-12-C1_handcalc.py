# -*- coding: utf-8 -*-
"""RX-12-C1 해석부 손계산 (v2.27.0, U2_FLAP 접이 받침, E-18). FEA 못 함 — 환경 없음(D-16).
치수: mech_RX-12-C1_model.md 2-1·2-2 표, STEP bbox(stepout/*.step CARTESIAN_POINT)로 확인.
가스 스프링 힘·모멘트: tools/out/mech_RX-12-C1/r2_gasspring.json(명목 L_ext 325·F1 1120, 공차 끝 327·1232).
판 묶음 자중 W 141 N, 무게중심 반지름 353(r2_gasspring.py).
기준: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2 = 동작.
오조작 하중: 손 100 N(이 프로젝트 models.json 관례, RX-12-C2와 같음), 펴는 중 손 놓침(감쇠 없는 올림).
실행: python -X utf8 -B fea/cases/mech_RX-12-C1_handcalc.py -> fea/results/mech_RX-12-C1_handcalc.json"""
import json, math, re, glob, os, importlib.util
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
ENG = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
sp = importlib.util.spec_from_file_location("handcalc", ENG); hc = importlib.util.module_from_spec(sp); sp.loader.exec_module(hc)
OUT = ROOT + "/fea/results/mech_RX-12-C1_handcalc.json"
G = 9.80665
E_AL, SY_AL = 70300.0, 195.0          # A5052-H32(이 프로젝트 기존 값)
SY_SUS, SY_303, SY_SCM = 205.0, 205.0, 785.0
SY_POM = 60.0
R = {}

def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"

def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()}

# ---- STEP bbox 확인
bb = {}
for f in sorted(glob.glob(ROOT + "/tools/out/mech_RX-12-C1/stepout/*.step")):
    pts = re.findall(r"CARTESIAN_POINT\('[^']*',\(([-\d.E+, ]+)\)\)", open(f, encoding="latin-1").read())
    xs = [tuple(float(v) for v in p.split(",")) for p in pts]
    xs = [p for p in xs if len(p) == 3]
    if xs:
        bb[os.path.basename(f)[:-5]] = [[round(min(p[i] for p in xs), 2), round(max(p[i] for p in xs), 2)] for i in range(3)]
R["_step_bbox"] = bb

# ---- 가스 스프링
gs = json.load(open(ROOT + "/tools/out/mech_RX-12-C1/r2_gasspring.json", encoding="utf-8"))
nom = gs["cases"]["Lext325_F1120"]["rows"]; tol = gs["cases"]["Lext327_F1232"]["rows"]
F_GS_MAX = max(r["F"] for r in tol)                 # 1571 N(-90, 공차 끝)
F_GS0_N, F_GS0_T = nom[0]["F"], tol[0]["F"]        # 0°
W_FLAP, RG = 141.0, 0.353
def energy(rows, a, b):                              # 올림 에너지 J(phi a -> b, 순 모멘트 > 0만)
    e = 0.0
    for r0, r1 in zip(rows, rows[1:]):
        if a >= r1["phi"] >= b or a >= r0["phi"] >= b:
            m = 0.5 * (max(r0["net"], 0) + max(r1["net"], 0)); e += m * math.radians(5)
    return e
E_N, E_T = energy(nom, 0, -75), energy(tol, 0, -75)
rec("gas_spring", F0_nom=F_GS0_N, F0_tol=F_GS0_T, Fmax_tol=F_GS_MAX, net0_nom=nom[0]["net"], net0_tol=tol[0]["net"],
    E_rise_nom_J=E_N, E_rise_tol_J=E_T, note="-75~0 순 올림 모멘트 적분(손 놓으면 판이 스스로 올라오는 에너지)")

# ---- 1. 가스 스프링 핀 P(Ø8 SCM435, 외팔: 귀판 t6 Y -1230~-1224, 눈 폭 10 Y -1240~-1230)
d = 8.0; A = math.pi * d * d / 4; Zp = math.pi * d ** 3 / 32
lev = 3.0 + 5.0                                     # 귀판 두께 가운데 ~ 눈 가운데
s_b = F_GS_MAX * lev / Zp; tau = F_GS_MAX / A
rec("GS_PIN_P_bend", part="P_RX12C1_GS_PIN_P", F_N=F_GS_MAX, lever_mm=lev, sigma=s_b, SF=SY_SCM / s_b, need=3.0)
rec("GS_PIN_P_shear", part="P_RX12C1_GS_PIN_P", tau=tau, SF=0.58 * SY_SCM / tau, need=3.0)
# 2. 귀판 SUS304 t6 폭 40: 지압, 면 밖 굽힘(눈 치우침 8)
brg = F_GS_MAX / (d * 6.0)
rec("GS_LUG_bearing", part="P_RX12C1_GS_LUG", p=brg, SF=SY_SUS / brg, need=3.0)
s_lug = F_GS_MAX * lev / (40 * 6 ** 2 / 6)
rec("GS_LUG_outplane", part="P_RX12C1_GS_LUG", sigma=s_lug, SF=SY_SUS / s_lug, need=3.0)
# 귀판 CB5-12 ×2(-Y에서 팔 블록 탭): 전단 = 스프링 힘 / 2
lug_b = hc.calc(5.0, 7.0, F_GS_MAX / 2, base="A5052")
rec("GS_LUG_bolts", part="CB5-12 x2 (귀판->팔 블록)", per_bolt_N=F_GS_MAX / 2, handcalc=lug_b,
    slip_SF=(2 * 4000 * 0.15) / F_GS_MAX, note="미끄럼 SF는 예압 4 kN·μ0.15 가정(RX-12-C1 설계 관례). 미끄러져도 구멍 틈 0.25 뒤 몸통 전단으로 받음")
# 3. 팔 블록 → 판 CB5-12 ×2(위에서): -90에서 스프링 힘이 판에서 떼는 쪽일 때 인장
blk_b = hc.calc(5.0, 7.0, F_GS_MAX / 2, base="A5052")
rec("GS_ARM_BLK_bolts", part="CB5-12 x2 (판->팔 블록)", per_bolt_N=F_GS_MAX / 2, handcalc=blk_b)
# 4. 클레비스 A5052(볼 사이 26, 볼 t6 ×2), 핀 A 두 면 전단
rec("GS_PIN_A_shear", part="P_RX12C1_GS_PIN_A", tau=F_GS_MAX / (2 * A), SF=0.58 * SY_SCM / (F_GS_MAX / (2 * A)), need=3.0)
brg_c = F_GS_MAX / (2 * d * 6.0)
rec("GS_CLEVIS_bearing", part="P_RX12C1_GS_CLEVIS", p=brg_c, SF=SY_AL / brg_c, need=3.0)
tear = 2 * 2 * (17.0 - 4.0) * 6.0 * 0.58 * SY_AL
rec("GS_CLEVIS_tearout", part="P_RX12C1_GS_CLEVIS", cap_N=tear, SF=tear / F_GS_MAX, need=3.0)
# 클레비스 뒤판 볼트 CB5-16 ×2 대각: 모멘트(팔 31) 인장 + 미끄럼(= RX12C1-D8)
M_cl = F_GS_MAX * 31.0
k = M_cl / (115.0 ** 2 + 75.0 ** 2); T1 = k * 115.0
rec("GS_CLEVIS_bolts", part="CB5-16 x2 (클레비스->:9)", M_Nmm=M_cl, T_max_N=T1,
    slip_SF=(2 * 4000 * 0.15) / F_GS_MAX, handcalc=hc.calc(5.0, 8.0, T1, base="A5052"),
    note="미끄럼 SF < 1 = 기존 디테일 RX12C1-D8(검도 0.85와 같은 계통, 최대 힘 1571로 다시 셈)")

# ---- 5. 경첩 반력(0°): 위 힘 합 = 스프링 Fz - W - 빗장 반력
lat0 = nom[0]["net"] / 0.710                         # 빗장(r 710)이 누르는 힘
Fz_h_n = F_GS0_N - W_FLAP - lat0; Fz_h_t = F_GS0_T - W_FLAP - tol[0]["net"] / 0.710
per_h = max(Fz_h_t, F_GS_MAX) / 2                     # -90은 스프링 힘 대부분이 경첩으로
rec("HINGE_reaction", part="STEP대기_HHPSN8 x2", hinge_total_0deg_nom_N=Fz_h_n, hinge_total_0deg_tol_N=Fz_h_t,
    per_hinge_max_N=per_h, note="경첩 허용 하중 자료 없음(형번·STEP 대기) — 실물 형번 받을 때 카탈로그 허용 ≥ 3 × per_hinge_max 확인")
rec("HINGE_leaf_bolts_slip", part="CB5-12 x2 / 경첩 (판쪽·기둥쪽)", per_hinge_N=per_h,
    slip_SF=(2 * 4000 * 0.15) / per_h, need=3.0, handcalc=hc.calc(5.0, 6.0, per_h / 2, base="A5052"))
R["HINGE_leaf_bolts_slip"]["verdict"] = verdict(R["HINGE_leaf_bolts_slip"]["slip_SF"], 3.0)

# ---- 6. 판 t5(A5052, 볼 구멍 Ø36 피치 100 → 살 0.64): 가장 큰 칸 400(Y) × 662(X), 네 변 단순지지
a, b, t = 662.0, 400.0, 5.0
eff = 0.64; Kt = 2.5
beta1, alpha_c, alpha_u, beta_u = 0.875, 0.1715, 0.0906, 0.5172   # Roark 표 11.4(a/b 1.6)
r0 = 10.0; nu = 0.33
P = 100.0
s_c = 3 * P / (2 * math.pi * t * t) * ((1 + nu) * math.log(2 * b / (math.pi * r0)) + beta1)
s_c_net = s_c / eff * Kt
y_c = alpha_c * P * b * b / (E_AL * t ** 3) / eff
rec("FLAP_PL_misuse_100N", part="P_RX12C1_FLAP_PL", sigma_gross=s_c, sigma_peak=s_c_net, SF=SY_AL / s_c_net, need=2.0,
    defl_mm=y_c, note="손 100 N(반지름 10)이 가장 큰 칸 가운데. 살 0.64·구멍 Kt 2.5로 보수")
q3 = W_FLAP / (0.695 * 0.895) * 1e-6 * 3            # N/mm2, 자중 ×3 g(판 묶음 전체를 판 넓이로)
s_u = beta_u * q3 * b * b / (t * t) / eff * Kt; y_u = alpha_u * q3 * b ** 4 / (E_AL * t ** 3) / eff
rec("FLAP_PL_selfweight_3g", part="P_RX12C1_FLAP_PL", q_Nmm2=q3, sigma_peak=s_u, SF=SY_AL / s_u, need=3.0, defl_mm=y_u)
hb = hc.beam(t=5.0, b=100.0 * eff, length=400.0, load=P / 2, end="guided", sf_min=2.0)
rec("FLAP_PL_beam_check", part="P_RX12C1_FLAP_PL", handcalc_beam=hb, note="handcalc beam(띠 폭 100×살 0.64, 400 양끝 고정, 100 N 반씩) — 판 공식 교차 확인")

# ---- 7. 막대 L2 10×30×662 단순지지(XN↔XP), 몫 넓이 350×662
Ib, Zb, L = 10 * 30 ** 3 / 12, 10 * 30 ** 2 / 6, 662.0
w1 = W_FLAP / (0.695 * 0.895) * (0.350 * 0.662)      # 1 g 몫
s3 = 3 * w1 * L / 8 / Zb
s_mis = (w1 * L / 8 + P * L / 4) / Zb
y_mis = 5 * w1 * L ** 3 / (384 * E_AL * Ib) + P * L ** 3 / (48 * E_AL * Ib)
rec("FLAP_BAR_L2_3g", part="P_RX12C1_FLAP_BAR_L1·L2·L3", w1_N=w1, sigma=s3, SF=SY_AL / s3, need=3.0)
rec("FLAP_BAR_L2_misuse", part="P_RX12C1_FLAP_BAR_L1·L2·L3", sigma=s_mis, SF=SY_AL / s_mis, need=2.0, defl_mm=y_mis)
# 8. XN 18(X)×30(Z) 빗장 A·B 사이 676 단순지지, 가운데에 L2 반력 + 손 100 N
Ix, Zx, Lx = 18 * 30 ** 3 / 12, 18 * 30 ** 2 / 6, 676.0
s_xn = (w1 / 2 + P) * Lx / 4 / Zx
y_xn = (w1 / 2 + P) * Lx ** 3 / (48 * E_AL * Ix)
rec("FLAP_BAR_XN_misuse", part="P_RX12C1_FLAP_BAR_XN", sigma=s_xn, SF=SY_AL / s_xn, need=2.0, defl_mm=y_xn,
    note="빗장 사이 가운데 볼 꼭대기 처짐 — 이음 높이차(볼 위 매트가 넘는 곳)")
# 9. 빗장 막대 Ø8 SUS303: 블록(X 383~402)↔XN(X 405~423), 틈 3 + 물림 가운데 ~ 12
F_lat = P + max(lat0, tol[0]["net"] / 0.710)
s_rod = F_lat * 12.0 / Zp
rec("LATCH_ROD", part="P_RX12C1_LATCH_ROD_A·B", F_N=F_lat, sigma=s_rod, SF=SY_303 / s_rod, need=2.0)
# 10. 빗장 블록 A5052 22×24, 아래로 145 매달림, 빗장 구멍 Z -28 / 볼트 줄은 블록 +X 면 홈(블록 -X 면 기준 굽힘 팔 ~ 빗장 높이)
rec("LATCH_BLK", part="P_RX12C1_LATCH_BLK_A·B", F_N=F_lat, handcalc=hc.calc(5.0, 6.0, F_lat, base="A5052"),
    note="빗장 힘이 블록 볼트 2개 미끄럼(1.2 kN)보다 훨씬 작음")

# ---- 11. 올림 멈춤 혀(빗장 뺀 채 0°): 팔 X 1106~1135 · Y 24 · Z 10, 나사 X 1128
F_st_n, F_st_t = nom[0]["net"] * 1000 / 23.0, tol[0]["net"] * 1000 / 23.0
Zt = 24 * 10 ** 2 / 6
s_t = F_st_t * 22.0 / Zt
rec("UPSTOP_TONGUE_static", part="P_RX12C1_UPSTOP_TONGUE", F_nom_N=F_st_n, F_tol_N=F_st_t, sigma=s_t, SF=SY_AL / s_t, need=3.0)
M_fl = F_st_t * (1128 - 1100)
T_fl = M_fl / 10.0 / 2
rec("UPSTOP_TONGUE_bolts", part="CB5-12 x2 (혀->XP)", T_per_bolt_N=T_fl, handcalc=hc.calc(5.0, 6.0, T_fl, base="A5052"))
cap_thread = math.pi * 6 * 9.06 * 0.5 * 0.58 * SY_AL
rec("UPSTOP_CB6-20_thread", part="CB6-20 → P_RX12C1_UPSTOP_BLK M6 탭", cap_N=cap_thread, SF=cap_thread / F_st_t, need=3.0)
rec("UPSTOP_BLK_slip", part="CB5-16 x2 (블록->기둥 B)", slip_SF=(2 * 4000 * 0.15) / F_st_t, need=3.0)
R["UPSTOP_BLK_slip"]["verdict"] = verdict(R["UPSTOP_BLK_slip"]["slip_SF"], 3.0)

# ---- 12. 펴는 중 손 놓침(감쇠 없음): 판이 스스로 올라와 혀가 CB6-20 머리를 침
I_fl = W_FLAP / G * (RG ** 2 + 0.20 ** 2)            # 경첩 축 관성(무게중심 353 + 판 회전반지름 0.20 가정)
w_n, w_t = math.sqrt(2 * E_N / I_fl), math.sqrt(2 * E_T / I_fl)
Iall = 3 * 22500.0 + 9323.0 * eff                   # 막대 3 + 판(겹친 효과 무시, 보수 아닌 쪽 — 낮은 강성)
EIf = E_AL * Iall * 1e-6                             # N·m2 (mm4·MPa → N·mm2 → ×1e-6)
kth_list = {"강성 낮게(EI/L, 판 묶음 외팔 0.70 m)": EIf / 0.70 * 0.3, "강성 기준(EI/L)": EIf / 0.70, "강성 높게(3EI/L)": 3 * EIf / 0.70}
cap_tongue_yield = SY_AL * Zt / 22.0                 # 혀 첫 항복 힘 N
imp = {}
for kname, kth in kth_list.items():
    Mpk = w_n * math.sqrt(I_fl * kth) + nom[0]["net"]
    Fpk = Mpk / 0.023
    imp[kname] = dict(k_theta_Nm_per_rad=round(kth, 1), M_peak_Nm=round(Mpk, 1), F_tongue_N=round(Fpk), SF_tongue=round(cap_tongue_yield / Fpk, 3))
# 혀 SF 2를 지키는 펴짐 끝 각속도 한도(강성 기준)
kth0 = kth_list["강성 기준(EI/L)"]
M_allow = cap_tongue_yield / 2 * 0.023 - tol[0]["net"]
w_allow = max(M_allow, 0) / math.sqrt(I_fl * kth0)
rec("UNCONTROLLED_RISE", part="P_RX12C1_UPSTOP_TONGUE · CB6-20 · UPSTOP_BLK", I_kgm2=I_fl, E_nom_J=E_N, E_tol_J=E_T,
    omega_nom=w_n, omega_tol=w_t, tip_speed_r710_mps=w_n * 0.710, tongue_yield_N=cap_tongue_yield, cases=imp,
    omega_allow_rad_s=w_allow, rod_speed_allow_mm_s=w_allow * 49.92, SF=min(v["SF_tongue"] for v in imp.values()), need=2.0,
    note="혀는 경첩 축에서 23 mm라 에너지를 흡수할 행정이 없다(12 J를 1.75 kN으로 받으려면 혀 자리에서 14 mm = 35°). "
         "판 묶음 굽힘이 유일한 완충 — 강성을 0.3배로 낮게 잡아도 SF < 1.2")
R["UNCONTROLLED_RISE"]["verdict"] = verdict(R["UNCONTROLLED_RISE"]["SF"], 2.0)

# ---- 13. -90 POM 멈춤
F_pom = abs(tol[-1]["net"]) / 0.212 + P
p_pom = F_pom / 2 / (10 * 30)
rec("STOP_POM", part="P_RX12C1_STOP_A·B", F_total_N=F_pom, p=p_pom, SF=SY_POM / p_pom, need=2.0)
# ---- 14. 혀 판(고정) t8: 기둥 A 볼트 X 1130에서 끝 X 976 외팔 154, 폭 100
It8, Zt8 = 100 * 8 ** 3 / 12, 100 * 8 ** 2 / 6
s_tab = P * 154 / Zt8; y_tab = P * 154 ** 3 / (3 * E_AL * It8)
rec("TAB_PL_misuse", part="P_RX12C1_TAB_PL", sigma=s_tab, SF=SY_AL / s_tab, need=2.0, defl_mm=y_tab)
tab_b = hc.calc(8.0, 10.0, P * 154 / 20.0 / 2, base="A5052")
rec("TAB_PL_bolts", part="CB8-16 x2 (혀 판->기둥 A 끝 탭)", handcalc=tab_b)

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k_, v in R.items():
    if k_.startswith("_"): continue
    print(k_, {kk: vv for kk, vv in v.items() if kk in ("SF", "slip_SF", "sigma", "sigma_peak", "defl_mm", "verdict", "F_N", "per_hinge_max_N", "omega_nom", "omega_allow_rad_s", "rod_speed_allow_mm_s", "E_nom_J", "E_tol_J")})
