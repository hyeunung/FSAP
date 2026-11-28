# -*- coding: utf-8 -*-
"""RX-15-A4 해석부 손계산 (v2.25.3) — 자르기 슬라이드 A6061-T6 + 혀 바닥 틈 0.05
python -X utf8 -B fea/cases/mech_RX-15_fea3_handcalc.py  -> fea/results/mech_RX-15_fea3_handcalc.json

하중 위치 · 경계조건은 fea2 4절(fea/cases/mech_RX-15_fea2_handcalc.py)과 모델링부 handcalc_a4.py와 같다(E-22, 모델 안 바꿈).
  날 끝 H(-Y) · V(-Z), 블록 뒷면(로드 너트 자리)에서 48.5 앞, 로드 축 Z -33.7에서 30.1 위.
  (가) 혀 10 x 6 외팔(받침 앞끝 Y -93에서 Lt = s - 2), 혀가 홈 안에서 기울어 틈(바닥 + 뚜껑)을 닫은 뒤 받음.
  (나) 로드 Ø5 외팔(코 끝에서 Lr = 13 + s), 부시 틈이 닫힌 뒤 받음. 두 길은 같은 날 끝 처짐을 나눔.
이번에 더 본 것(모델링부 · 검도 계산 위에):
  1) 자르는 구간 전체 CUT 7~36(1 mm 간격)과 절단 힘 20 · 40 · 걸림 49 N, 부시 틈 0 · 0.006, 홈 바닥 틈 0 · 0.05 · 0.1 · 0.2(공차)
  2) 아래 힘 비 V/H 1.04(날 변 마찰 0, 가장 불리) 외 0.77 · 0.56(fea2 감도) — 로드 SF 감도
  3) 마찰 · 부하율을 스프링을 뺀 밀기 80.5 N으로(CJ2B16-60SZ는 단동 스프링 복귀. 모델링부 · 검도는 100.5 N을 씀)
  4) 로드 피로(맥동, Goodman), 홈 앞끝 눌림 접촉 폭 감도(1 · 0.5 · 0.2 mm), 아노다이징 두께와 틈
임시값: 절단 힘 20~40 N(D-06), 걸림 49 N, 부시 틈 0.006 rad, 스프링 20 N, 로드 Ø5 SUS304(내력 205 · 인장 520 · 피로 한도 240),
        A6061-T6 내력 245, A5052 내력 195(받침), 마찰 0.1~0.3.
"""
import json, math, os

E_SUS, E_AL = 193000.0, 68900.0
SUS_Y, SUS_U, SUS_E = 205.0, 520.0, 240.0
AL_Y, A5052_Y = 245.0, 195.0
I_r, Z_r = math.pi * 5 ** 4 / 64, math.pi * 5 ** 3 / 32
I_t, Z_t = 10 * 6 ** 3 / 12.0, 10 * 6 ** 2 / 6.0
G_LID = 0.2
THRUST = math.pi * 16 ** 2 / 4 * 0.5          # 100.5 N
SPRING = 20.0                                 # 임시(fea2 · T06 선정과 같은 값)
NET = THRUST - SPRING                         # 80.5 N
A_ROD = math.pi * 5 ** 2 / 4


def tips(s, H, V, E_t):
    Lt, Lr = s - 2.0, 13.0 + s
    Mb = V * 48.5 - H * 30.1
    tip_t = (Mb * Lt ** 2 / 2 + V * Lt ** 3 / 3) / (E_t * I_t) + (Mb * Lt + V * Lt ** 2 / 2) / (E_t * I_t) * 48.5
    tip_r = (Mb * Lr ** 2 / 2 + V * Lr ** 3 / 3) / (E_SUS * I_r) + (Mb * Lr + V * Lr ** 2 / 2) / (E_SUS * I_r) * 48.5
    Mg = V * (48.5 + Lt) - H * 30.1
    Mn = V * (48.5 + Lr) - H * 30.1
    return Lt, Lr, tip_t, tip_r, Mg, Mn


def share(V, kt, kr, dg, dp):
    """kt (d - dg)+ + kr (d - dp)+ = V 를 d로 푼다(구간 선형)."""
    a, b = sorted([(dg, kt), (dp, kr)])
    if kt * 0 + (b[0] - a[0]) * a[1] >= V:      # 먼저 닿는 길만으로 끝남
        d = a[0] + V / a[1]
    else:
        d = (V + a[1] * a[0] + b[1] * b[0]) / (a[1] + b[1])
    return d, kt * max(0.0, d - dg), kr * max(0.0, d - dp)


def solve(s, H, V, gb, play, E_t=E_AL):
    Lt, Lr, tip_t, tip_r, Mg, Mn = tips(s, H, V, E_t)
    Le = 137.0 - s                                           # 홈 안 혀 길이
    dg = (gb + G_LID) / Le * (48.5 + Lt + Le / 2)            # fea2 · 모델링부와 같은 식
    dp = play * (Lr + 48.5)
    d, Ft, Fr = share(V, V / tip_t, V / tip_r, dg, dp)
    sig_r = (Fr / V) * Mn / Z_r
    sig_ax = NET / A_ROD                                     # 로드 축 압축(밀기)
    sig_t = (Ft / V) * Mg / Z_t
    P = (Ft / V) * Mg / Le
    Rm, Rl = Ft + P, P
    return dict(s=s, H=H, V=round(V, 1), gap_bottom=gb, play=play, tongue_free=Lt, rod_free=Lr,
                tip_drop_mm=round(d, 3), tongue_N=round(Ft, 1), rod_side_N=round(Fr, 1),
                rod_bend_MPa=round(sig_r, 1), rod_axial_MPa=round(sig_ax, 1),
                rod_SF=round(SUS_Y / (sig_r + sig_ax), 2),
                tongue_MPa=round(sig_t, 1), tongue_SF=round(AL_Y / sig_t, 2) if sig_t > 0 else None,
                mouth_N=round(Rm, 1), lid_N=round(Rl, 1), sumR=round(Rm + Rl, 1))


R = {"loads": dict(thrust_N=round(THRUST, 1), spring_N=SPRING, net_push_N=round(NET, 1), V_over_H=1.04)}

# 1) 구간 전체 쓸기
sweep = []
for s in range(7, 37):
    for H in (20.0, 40.0, 49.0):
        for gb in (0.0, 0.05, 0.1, 0.2):
            for play in (0.0, 0.006):
                sweep.append(solve(float(s), H, 1.04 * H, gb, play))
R["sweep_n"] = len(sweep)


def worst(rows, key, hi=False):
    return (max if hi else min)(rows, key=lambda r: (r[key] if r[key] is not None else 1e9) * (1 if not hi else 1))


nom = [r for r in sweep if r["gap_bottom"] == 0.05]
R["worst_rod_H40_gap0.05"] = worst([r for r in nom if r["H"] == 40.0], "rod_SF")
R["worst_rod_jam49_gap0.05"] = worst([r for r in nom if r["H"] == 49.0], "rod_SF")
R["worst_rod_H20_gap0.05"] = worst([r for r in nom if r["H"] == 20.0], "rod_SF")
R["worst_tongue_gap0.05"] = worst(nom, "tongue_SF")
R["max_mouth_gap0.05"] = worst(nom, "mouth_N", hi=True)
for gb in (0.0, 0.1, 0.2):
    R["worst_rod_H40_gap%.2f" % gb] = worst([r for r in sweep if r["gap_bottom"] == gb and r["H"] == 40.0], "rod_SF")
    R["worst_rod_jam49_gap%.2f" % gb] = worst([r for r in sweep if r["gap_bottom"] == gb and r["H"] == 49.0], "rod_SF")

# 2) 아래 힘 비 감도(CUT 36, H 40, 틈 0.05, 부시 0)
R["V_over_H_sensitivity"] = {"%.2f" % k: solve(36.0, 40.0, k * 40.0, 0.05, 0.0)["rod_SF"] for k in (1.04, 0.77, 0.56)}

# 3) 마찰 · 부하율 — 밀기 80.5 N(스프링 뺌)
fr = {}
for H in (40.0, 49.0):
    rows = [r for r in nom if r["H"] == H]
    big = worst(rows, "sumR", hi=True)
    d = dict(sumR_N=big["sumR"], at=dict(s=big["s"], play=big["play"]), mu_stall=round((NET - H) / big["sumR"], 3))
    for mu in (0.1, 0.2, 0.3):
        d["load_ratio_mu%.1f" % mu] = round((H + mu * big["sumR"]) / NET, 3)
        d["load_ratio_mu%.1f_thrust100.5" % mu] = round((H + mu * big["sumR"]) / THRUST, 3)
    d["mu_for_ratio_0.7"] = round((0.7 * NET - H) / big["sumR"], 3)
    fr["H%d" % H] = d
R["friction"] = fr

# 4) 로드 피로(맥동 0 -> 최대, 40 N 가장 불리) Goodman
w = R["worst_rod_H40_gap0.05"]
smax = w["rod_bend_MPa"] + w["rod_axial_MPa"]
sa = sm = smax / 2
R["rod_fatigue_H40"] = dict(sigma_max_MPa=round(smax, 1), sa=round(sa, 1), sm=round(sm, 1),
                            SF_goodman=round(1 / (sa / SUS_E + sm / SUS_U), 2), need=2.0)
# 홈 앞끝 눌림 — 접촉 폭 감도(A6061 혀 245 / A5052 받침 195, 약한 쪽)
m = R["max_mouth_gap0.05"]["mouth_N"]
R["mouth_bearing"] = {"w%.1f" % wd: dict(p_MPa=round(m / (10 * wd), 1), SF_A5052=round(A5052_Y / (m / (10 * wd)), 1)) for wd in (1.0, 0.5, 0.2)}
# 아노다이징 두께와 위아래 틈(바닥 0.05 + 뚜껑 0.2 = 0.25)
R["coating_gap"] = dict(total_gap=0.25,
                        hard_anodize_50um_growth_both_faces=0.05, groove_anodize_10um_growth_both=0.01,
                        remaining=round(0.25 - 0.05 - 0.01, 3),
                        note="혀 두께가 0.05 늘면 바닥 틈은 조립 높이(로드 축)로 정해지므로 바닥 0.025 · 뚜껑 0.175 쪽으로 나뉨 — 맞물림 없음")

print("net push %.1f N (thrust %.1f - spring %.0f)" % (NET, THRUST, SPRING))
for k in ("worst_rod_H20_gap0.05", "worst_rod_H40_gap0.05", "worst_rod_jam49_gap0.05", "worst_rod_H40_gap0.00", "worst_rod_H40_gap0.10", "worst_rod_H40_gap0.20", "worst_rod_jam49_gap0.20"):
    r = R[k]; print("%-26s s%2d play%.3f rod %5.1f N SF %5.2f tip %.3f" % (k, r["s"], r["play"], r["rod_side_N"], r["rod_SF"], r["tip_drop_mm"]))
t = R["worst_tongue_gap0.05"]; print("tongue worst SF %.2f (s%d H%d)" % (t["tongue_SF"], t["s"], t["H"]))
print("mouth max %.1f N (s%d H%d)" % (m, R["max_mouth_gap0.05"]["s"], R["max_mouth_gap0.05"]["H"]), R["mouth_bearing"])
print("V/H", R["V_over_H_sensitivity"])
print("friction", json.dumps(R["friction"]))
print("fatigue", R["rod_fatigue_H40"])
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "mech_RX-15_fea3_handcalc.json")
R["sweep"] = sweep
json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("->", out)
