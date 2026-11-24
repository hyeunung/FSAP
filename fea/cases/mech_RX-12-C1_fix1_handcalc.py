# RX-12-C1 수정 1회차 손계산: 펴짐 끝 감쇠 + 올림 완충 멈춤(우레탄 패드 A·B, r 707)
# FEA 못 함 — 환경 없음(자료대기 D-16). 입력은 mech_RX-12-C1_handcalc.json UNCONTROLLED_RISE·r2_gasspring.json 값.
import json, math, os

I = 2.367            # 판 묶음 경첩 축 관성 kg·m² (handcalc.json)
M_net = 13.73        # 0° 순 올림 모멘트 공차 끝 N·m (r2_gasspring)
M_nom = 7.39
E_free_nom, E_free_tol = 13.528, 20.339   # 감쇠 없을 때 0° 도착 에너지 J
# 기하(모델 v2.27.1, 월드 mm): 경첩 축 (1105, -48), 핀 P (1055, -48), 핀 A (1073, -368)
rP = 50.0
rod_cos = 320.0 / math.hypot(18.0, 320.0)
lever_rod = rP * rod_cos      # 로드 속도 = lever_rod * ω (mm/s, ω rad/s)
r_pad = 1105.0 - 398.0        # 패드 중심 X 398 → 707
r_tongue = 23.0               # 혀 ↔ CB6-20 (X 1128)
gap_pad = 0.30                # 패드 윗면 Z -31.3 ↔ 브래킷 턱 밑면 Z -31.0
latch_float = 0.15            # 빗장 Ø8 ↔ Ø8.3 → 판 끝이 뜰 수 있는 양(r 710)
gap_tongue_old, gap_tongue = 0.06, 0.12   # CB6-20 머리 Z -23.06 → -23.12
# 우레탄 패드 Ø10 t5, Urethane A70 (Gent: E = 0.0981(56+7.66S)/(0.137505(254-2.54S)), S=70)
S = 70.0
E_u = 0.0981 * (56 + 7.66 * S) / (0.137505 * (254 - 2.54 * S))  # MPa
A = math.pi * 5.0 ** 2
t = 5.0
shape = A / (math.pi * 10.0 * t)
Ec = E_u * (1 + 2 * shape ** 2)
k_pad = Ec * A / t            # N/mm, 한 개
n_pad = 2
k_tot = k_pad * n_pad
Ktheta = k_tot * 1e3 * (r_pad / 1e3) ** 2     # N·m/rad
# 판 묶음 굽힘(handcalc.json 기준 k_theta = EI/L 7378 N·m/rad, L 0.70 m)
EI = 7378.2 * 0.70            # N·m²
L = 0.70

def case(v_rod):
    w = v_rod / lever_rod                         # rad/s
    KE = 0.5 * I * w ** 2
    th0 = gap_pad / r_pad                         # 패드 닿는 각
    # 0.5 K (th-th0)^2 = KE + M_net*th  (스프링 일 포함) → 풀기
    a = 0.5 * Ktheta; b = -Ktheta * th0 - M_net; c = 0.5 * Ktheta * th0 ** 2 - KE - M_net * 0
    # M_net*th 항: 0.5K x² - M_net (x+th0) = KE, x = th-th0
    # 0.5K x² - M_net x - (KE + M_net th0) = 0
    x = (M_net + math.sqrt(M_net ** 2 + 2 * Ktheta * (KE + M_net * th0))) / Ktheta
    th = th0 + x
    defl = x * r_pad                              # mm
    F_tot = k_tot * defl                          # N
    F_one = F_tot * 0.6                           # 한쪽 몫(비틀림 치우침 60 %)
    # 판 굽힘으로 경첩 쪽(혀) 기울기가 더 감: 단순 지지 등분포 wL³/24EI
    w_line = F_tot / L
    th_bend = w_line * L ** 3 / (24 * EI)
    th_root = th + th_bend
    return dict(v_rod_mm_s=v_rod, omega=round(w, 4), KE_J=round(KE, 4), pad_defl_mm=round(defl, 3),
                pad_strain=round((defl + 0) / t, 3), F_total_N=round(F_tot, 1), F_one_N=round(F_one, 1),
                theta_chord_mrad=round(th * 1e3, 3), theta_root_mrad=round(th_root * 1e3, 3),
                tongue_engage_mrad_old=round(gap_tongue_old / r_tongue * 1e3, 3),
                tongue_engage_mrad=round(gap_tongue / r_tongue * 1e3, 3),
                tongue_touch=th_root > gap_tongue / r_tongue)

cases = {f"{v} mm/s": case(v) for v in (5, 10, 15, 20, 25)}
# 혀가 닿지 않는 최대 로드 속도(이분법)
lo, hi = 0.1, 200.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    if case(mid)["tongue_touch"]: hi = mid
    else: lo = mid
v_allow = lo
# 감쇠 없을 때(참고): 패드만으로 받을 수 있나
def pad_only(E):
    x = (M_net + math.sqrt(M_net ** 2 + 2 * Ktheta * (E + M_net * gap_pad / r_pad))) / Ktheta
    return round(x * r_pad, 2), round(k_tot * x * r_pad, 0)
d_free, F_free = pad_only(E_free_nom)
# 정지(빗장 뺀 채 0°): 패드가 받침, 순 모멘트 / r
F_static = M_net / (r_pad / 1e3)
d_static = F_static / k_tot
# 브래킷 턱(외팔 X 390 → 패드 X 398, 단면 폭 24 × 두께 11, A5052 σy 195 MPa)
F_design = cases["20 mm/s"]["F_one_N"] * 2.0      # 오조작 계수 2를 하중에
Zs = 24 * 11 ** 2 / 6
sig_brkt = F_design * 8.0 / Zs
SF_brkt = 195.0 / sig_brkt
# 브래킷 볼트 CB5-12 ×2 (SCM435 12.9) → HNTT8-5: 수직 힘은 마찰로. 축력 M5 12.9 약 6.0 kN(체결 토크 7 N·m 기준 표값), μ 0.15
slip = 2 * 6000 * 0.15
SF_slip_brkt = slip / F_design
# 러그 CB5-16 ×2 → XN 막대 M5 탭(물림 10): 지레 7/9 인장
T_lug = F_design * 7.0 / 9.0
SF_lug_bolt = (2 * 6000) / T_lug       # 축력 대비(벌어짐)
res = dict(
    method="손계산(FEA 못 함 — 환경 없음, D-16)",
    pad=dict(material="Urethane_A70", E_MPa=round(E_u, 2), shape_factor=round(shape, 2), Ec_MPa=round(Ec, 2),
             k_one_N_mm=round(k_pad, 1), k_total_N_mm=round(k_tot, 1), K_theta_Nm_rad=round(Ktheta, 0),
             r_pad_mm=r_pad, gap_mm=gap_pad, latch_float_mm=latch_float, gap_minus_float=round(gap_pad - latch_float, 3)),
    lever_rod_mm=round(lever_rod, 3), cases=cases,
    rod_speed_allow_no_tongue_mm_s=round(v_allow, 1),
    undamped_ref=dict(E_J=E_free_nom, pad_defl_mm=d_free, F_N=F_free, verdict="감쇠 없으면 패드 행정(혀까지)·변형률을 크게 넘음 → 감쇠는 필수"),
    static_rest_unlatched=dict(F_total_N=round(F_static, 1), pad_defl_mm=round(d_static, 3),
                               tip_above_nominal_mm=round(gap_pad + d_static, 3)),
    bracket=dict(F_design_N=round(F_design, 1), sigma_MPa=round(sig_brkt, 2), SF=round(SF_brkt, 1),
                 SF_slip=round(SF_slip_brkt, 1)),
    lug_bolt=dict(T_N=round(T_lug, 1), SF_vs_preload=round(SF_lug_bolt, 1)),
    damper_spec="가스 스프링 펴짐 끝 오일 감쇠(end-position damping in extension), 감쇠 구간 ≥ 15 mm(0°는 완전 신장 4.49 앞), 0° 도착 로드 속도 ≤ 10 mm/s 목표 · 상한 = rod_speed_allow_no_tongue",
)
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "results"), exist_ok=True)
out = os.path.join(os.path.dirname(__file__), "..", "results", "mech_RX-12-C1_fix1_handcalc.json")
json.dump(res, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("pad", "rod_speed_allow_no_tongue_mm_s", "static_rest_unlatched", "bracket", "lug_bolt")}, ensure_ascii=False))
for k, v in cases.items(): print(k, v)
print("undamped", res["undamped_ref"])
