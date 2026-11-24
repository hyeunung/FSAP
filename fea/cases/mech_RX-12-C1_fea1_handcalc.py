# RX-12-C1 해석 1회차(모델 v2.27.1, 수정 1회차 새 하중 부품) 손계산
# FEA 못 함 — 환경 없음(engine/fea/.venv 미설치, 자료대기 D-16). CAD 안 씀.
# 형상: STEP 꼭짓점 bbox(fea/results/mech_RX-12-C1_fea1_bbox.json). 하중: fea/results/mech_RX-12-C1_fix1_handcalc.json
# 대상: P_RX12C1_BUMP_BRKT_A(·B 같은 형상), BUMP_LUG_A(·B), BUMP_PAD_A(·B), FLAP_BAR_XN(밑면 M5 탭 4 더함) + 새 볼트 CB5-12 ×4 · CB5-16 ×4
import json, math, os, sys
sys.path.insert(0, "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools")
import handcalc  # 엔진 도구(읽기만)

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
fx = json.load(open(os.path.join(R, "mech_RX-12-C1_fix1_handcalc.json"), encoding="utf8"))
bb = json.load(open(os.path.join(R, "mech_RX-12-C1_fea1_bbox.json"), encoding="utf8"))

SY_AL = 195.0      # A5052 σy (models.json RX12C1 기준값)
NEED_RUN, NEED_MIS = 3.0, 2.0   # M-09 기본값(요구서 6-1 비어 있음)

# ---- 하중 경우 ----
r_pad = fx["pad"]["r_pad_mm"]           # 707
M_net_tol = 13.73                        # 0° 순 올림 모멘트 공차 끝 N·m
share = 0.6                              # 한쪽 몫(비틀림 치우침) — fix1과 같음
cases = {}
c20 = fx["cases"]["20 mm/s"]
cases["운전: 감쇠 도착 20 mm/s(D-231 상한)"] = dict(F_one=c20["F_one_N"], need=NEED_RUN)
# 혀가 닿는 상한 31 mm/s: fix1 식으로 다시 셈(오조작: 감쇠가 상한 밖으로 빠름)
I = 2.367; lever = fx["lever_rod_mm"]; Kth = fx["pad"]["K_theta_Nm_rad"]; ktot = fx["pad"]["k_total_N_mm"]
def F_tot_at(v):
    w = v / lever; KE = 0.5 * I * w * w; th0 = 0.30 / r_pad
    x = (M_net_tol + math.sqrt(M_net_tol ** 2 + 2 * Kth * (KE + M_net_tol * th0))) / Kth
    return ktot * x * r_pad, x * r_pad
F31, d31 = F_tot_at(31.0)
cases["오조작: 도착 31 mm/s(혀 닿기 직전)"] = dict(F_one=share * F31, need=NEED_MIS, pad_defl=d31)
# 손으로 빗장 뺀 판 끝(r 710)을 100 N 들어 올림(오조작 손 100 N, models.json 관례)
F_hand = (100 * 0.710 + M_net_tol) / (r_pad / 1e3)
cases["오조작: 빗장 뺀 판 끝 손 100 N 위로"] = dict(F_one=share * F_hand, need=NEED_MIS)
worst_run = max((c for c in cases.values() if c["need"] == NEED_RUN), key=lambda c: c["F_one"])
worst_mis = max((c for c in cases.values() if c["need"] == NEED_MIS), key=lambda c: c["F_one"])

out = dict(method="손계산(FEA 못 함 — 환경 없음, D-16)", load_cases={k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in cases.items()})

def sf_pair(sig_per_N):
    return dict(run=dict(F=round(worst_run["F_one"], 1), sigma=round(sig_per_N * worst_run["F_one"], 2), SF=round(SY_AL / (sig_per_N * worst_run["F_one"]), 2), need=NEED_RUN),
                mis=dict(F=round(worst_mis["F_one"], 1), sigma=round(sig_per_N * worst_mis["F_one"], 2), SF=round(SY_AL / (sig_per_N * worst_mis["F_one"]), 2), need=NEED_MIS))

# ---- 1. 패드 Urethane A70 Ø10 t5 ----
A_pad = math.pi * 25
pad = {}
for k, c in cases.items():
    F = c["F_one"]; defl = F / fx["pad"]["k_one_N_mm"]
    pad[k] = dict(F_N=round(F, 1), stress_MPa=round(F / A_pad, 2), strain=round(defl / 5.0, 3))
out["PAD"] = dict(part="P_RX12C1_BUMP_PAD_A·B", cases=pad, limit="우레탄 압축 되풀이 변형률 ≤ 0.25(일반 설계 지침), 한 번 충격 ≤ 0.40",
                  note="선형 k(형상계수 0.5) — 0.25 넘으면 실제는 더 단단해져 눌림은 이보다 작다(보수)")

# ---- 2. 브래킷 BUMP_BRKT_A: 세움 X 380~390(두께 10)·폭 Y 24, 턱 X 390~403 · Z −31~−20(두께 11) ----
b = 24.0
# 2-1 턱 뿌리(X 390) 굽힘: 패드 가운데 X 398 → 팔 8. 안쪽 모서리 Kt 2.5(가공 모서리 r 0.5 가정)
Z_tooth = b * 11 ** 2 / 6
s_tooth = 8.0 * 2.5 / Z_tooth
# 2-2 세움 굽힘: 패드 힘(+Z 방향 반력은 −Z로 턱을 누름…) 세움 단면 중립축 X 385 → 팔 13, 윗 볼트 줄 순단면
# 순단면: X 380~384 폭 24−5.5, X 384~390 폭 24−9.5(자리파기) — 중립축 구해 Z_min
segs = [(380, 384, 24 - 5.5), (384, 390, 24 - 9.5)]
Atot = sum((x2 - x1) * w for x1, x2, w in segs)
xc = sum((x2 - x1) * w * (x1 + x2) / 2 for x1, x2, w in segs) / Atot
Iy = sum(w * (x2 - x1) ** 3 / 12 + (x2 - x1) * w * ((x1 + x2) / 2 - xc) ** 2 for x1, x2, w in segs)
Zn = Iy / max(xc - 380, 390 - xc)
s_col = (398 - xc) / Zn + 1 / Atot      # 굽힘 + 축 인장, per N
# 2-3 볼트 CB5-12 ×2 → HNTT8-5(T너트, 강): 지렛대 받침 = 접촉면 윗끝 Z −20(아래쪽이 벌어짐), 볼트 Z −112 · −152
M_face = 18.0          # 패드 X 398 − 프로파일 면 X 380
d1, d2 = 112 - 20, 152 - 20
T_bolt_per_N = M_face * d2 / (d1 ** 2 + d2 ** 2)
torque_T = 4.5          # N·m(가정, T너트 조임) → 예압 4.5 kN
pre = torque_T * 1000 / (0.2 * 5)
mu = 0.15
slip_per_N = 1.0 / (2 * pre * mu)      # 수직 전단은 2볼트 마찰
hc_brkt = handcalc.calc(5, 5.5, worst_mis["F_one"] * T_bolt_per_N + 1e-9, torque_T, "12.9", "SS400", 8.5, 5.5, sf_min=NEED_MIS)
out["BRKT"] = dict(part="P_RX12C1_BUMP_BRKT_A·B", A5052=SY_AL,
                   tooth=dict(Z_mm3=round(Z_tooth, 1), Kt=2.5, **sf_pair(s_tooth)),
                   column_net=dict(A_mm2=round(Atot, 1), xc=round(xc, 2), Z_mm3=round(Zn, 1), **sf_pair(s_col)),
                   bolts_CB5_12=dict(lever_pivot="접촉면 윗끝 Z −20", T_bolt_mis_N=round(worst_mis["F_one"] * T_bolt_per_N, 1),
                                     preload_N=round(pre), slip_SF_run=round(1 / (slip_per_N * worst_run["F_one"]), 2),
                                     slip_SF_mis=round(1 / (slip_per_N * worst_mis["F_one"]), 2), handcalc=hc_brkt))

# ---- 3. 러그 BUMP_LUG_A: 바닥 X 393~423 · Z −49~−43(t6), 세움 X 393~405 · Z −43~−36.3, 볼트 X 414 ×2, XN 밑면 X 405~423 ----
# 패드 반력은 러그를 아래(−Z)로 당긴다 → 러그가 XN 밑면에서 떨어지는 쪽. 받침 = XN 밑면 +X 끝 X 423(러그 끝).
# fix1 식(팔 7/9, 받침 X 405)은 받침 방향이 반대 — 여기서 바로잡음: T = F·(423−398)/(423−414)
T_lug_per_N = (423 - 398) / (423 - 414)
M_boltline = (T_lug_per_N - 1) * (423 - 414)     # = 16 per N
Z_net = (24 - 2 * 5.5) * 6 ** 2 / 6
s_lug_bolt = M_boltline / Z_net
Z_gross = 24 * 6 ** 2 / 6
s_lug_corner = 2.5 * (405 - 398) / Z_gross        # 안쪽 모서리 (405, −43), Kt 2.5
torque_L = 4.5   # N·m, A5052 탭
hc_lug_run = handcalc.calc(5, 10, worst_run["F_one"] * T_lug_per_N / 2, torque_L, "12.9", "A5052", 8.5, 5.5, sf_min=NEED_RUN)
hc_lug_mis = handcalc.calc(5, 10, worst_mis["F_one"] * T_lug_per_N / 2, torque_L, "12.9", "A5052", 8.5, 5.5, sf_min=NEED_MIS)
out["LUG"] = dict(part="P_RX12C1_BUMP_LUG_A·B",
                  lever=dict(pivot="XN 밑면 +X 끝 X 423", T_total_per_F=round(T_lug_per_N, 3), fix1_value=round(7 / 9, 3),
                             note="fix1 손계산은 받침을 X 405로 잡아 볼트 당김을 3.6배 작게 셈 — 판정은 바뀌지 않음(아래 SF)"),
                  bolt_line=dict(Z_net=Z_net, **sf_pair(s_lug_bolt)),
                  corner=dict(Z_gross=Z_gross, Kt=2.5, **sf_pair(s_lug_corner)),
                  bolts_CB5_16_into_XN_tap=dict(T_one_run_N=round(worst_run["F_one"] * T_lug_per_N / 2, 1),
                                               T_one_mis_N=round(worst_mis["F_one"] * T_lug_per_N / 2, 1),
                                               handcalc_run=hc_lug_run, handcalc_mis=hc_lug_mis))

# ---- 4. XN 막대 X 405~423(18) · Z −43~−13(30), 빗장 뺀 충격: 패드 A·B(Y −448 · −1052, 사이 604) 단순지지, 판 묶음 관성 합을 가운데 한 점(보수) ----
span = 1052 - 448
Z_xn = 18 * 30 ** 2 / 6
def xn(Ftot, need):
    s = 2.0 * Ftot * span / 4 / Z_xn         # Kt 2(볼·빗장 구멍)
    return dict(F_total=round(Ftot, 1), sigma=round(s, 2), SF=round(SY_AL / s, 2), need=need)
# 탭 Ø4.2 깊이 13(X 414, 막대 폭 가운데) 둘레 살: (18 − 4.2)/2 = 6.9
out["XN"] = dict(part="P_RX12C1_FLAP_BAR_XN", Z_mm3=Z_xn, span_mm=span,
                 run=xn(worst_run["F_one"] / share, NEED_RUN), mis=xn(worst_mis["F_one"] / share, NEED_MIS),
                 tap_wall_mm=round((18 - 4.2) / 2, 2), tap_depth_vs_bar="탭 Z −43~−30, 막대 윗면 −13까지 17 남음(볼 구멍·윗 탭과 안 만남: 탭 Y −454·−442·−1058·−1046 ↔ 빗장 Y −412·−1088)")

# ---- 5. 감쇠가 없을 때(D-231 사양이 빠진 가스 스프링이 들어오면) — 참고 ----
out["UNDAMPED_REF"] = dict(pad_defl_mm=fx["undamped_ref"]["pad_defl_mm"], pad_thickness=5.0,
                           verdict="패드 두께 5보다 더 눌려야 함 → 바닥 닿고 혀 충격 되살아남. 감쇠 가스 스프링은 구매 사양 필수 조건(D-231)")

# ---- 판정 모음 ----
rows = []
def add(name, d, key="SF"):
    for t in ("run", "mis"):
        if t in d:
            rows.append((f"{name} {t}", d[t][key], d[t]["need"]))
add("BRKT 턱", out["BRKT"]["tooth"]); add("BRKT 세움", out["BRKT"]["column_net"])
add("LUG 볼트줄", out["LUG"]["bolt_line"]); add("LUG 모서리", out["LUG"]["corner"])
add("XN 굽힘", out["XN"])
rows.append(("BRKT 볼트 미끄럼 run", out["BRKT"]["bolts_CB5_12"]["slip_SF_run"], NEED_RUN))
rows.append(("BRKT 볼트 미끄럼 mis", out["BRKT"]["bolts_CB5_12"]["slip_SF_mis"], NEED_MIS))
for nm, hc, need in (("LUG CB5-16 run", hc_lug_run, NEED_RUN), ("LUG CB5-16 mis", hc_lug_mis, NEED_MIS), ("BRKT CB5-12 mis", hc_brkt, NEED_MIS)):
    rows.append((nm + " 운전 최소", min(hc["sf_operating"].values()), need))
    if hc["sf_tightening"]:
        rows.append((nm + " 조임 최소", min(hc["sf_tightening"].values()), 1.0))
out["summary"] = [dict(item=a, SF=round(b_, 2), need=c, ok=b_ >= c, over_3x=b_ >= 3 * c) for a, b_, c in rows]
out["action"] = [r for r in out["summary"] if not r["ok"]]
json.dump(out, open(os.path.join(R, "mech_RX-12-C1_fea1_handcalc.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("load cases:", out["load_cases"])
print("PAD:", pad)
for r in out["summary"]:
    print(f"{r['item']:24s} SF {r['SF']:8.2f} need {r['need']} {'OK' if r['ok'] else 'NG'}{' (3x)' if r['over_3x'] else ''}")
print("NG:", len(out["action"]))
