# -*- coding: utf-8 -*-
# VGR-01 해석부 손계산 (2026-11-10) — C-37 (다) 회전력 검산. FEA 환경 없음(D-16)이라 손계산.
# 1) 매트 관성·구름 토크를 2.5 mm 격자로 독립 재계산(설계안은 5 mm) 2) machine.json _timing 실제 시간 키로 구간별 SF
# 3) 설계안에 없던 저항: U4 밑 원판(P_M02_DISK, 중심 (-175,0), 자유 회전) 끌림·관성, U5 밑 PTFE 띠(P_DC205_STRIP, D-97 mu 0.15~0.3) 미끄럼
import json, math, os
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
OUT = ROOT + "/fea/results/mech_VGR-01_handcalc.json"
g, rho = 9.81, 6.0                 # 면밀도 6 kg/m2 (D-145, D-04 높은 쪽)
mu_w, d1, d2 = 0.4, 0.100, 0.440   # 바퀴-파일 mu (D-95 낮은 쪽), d1 100, d2 440 (D-152)
F4 = 40.0                          # U4 누름 (C-37)
F5, f5 = 44.0, 4.0                 # U5 누름·플로트 미끄럼 저항 (D-146)
a, h, st = 1200.0, 600.0, 2.5
GY, al, rb, e = -300.0, 15.0, 2.0, 6.5
CV = (h - 150.0 + rb / math.sin(math.radians(al)), GY)
s, c = math.sin(math.radians(al)), math.cos(math.radians(al))
def void(x, y):
    dx, dy = x - CV[0], y - CV[1]
    if math.hypot(dx, dy) <= rb: return True
    return dx * c > -rb * s and (-s * dx + c * dy) <= rb and (-s * dx - c * dy) <= rb and x <= h
n = int(a / st); dA = (st / 1000) ** 2
cells = [(-h + (i + .5) * st, -h + (j + .5) * st) for i in range(n) for j in range(n)]
cells = [p for p in cells if not void(*p)]
mass = rho * dA * len(cells)
m2y = round(GY - ((h - e - (h - 150.0)) * math.tan(math.radians(al)) + e / c), 3)
P = {"apex_mid": (CV[0] - (rb + e), GY), "entrance_m2": (593.5, m2y), "entrance_m1": (593.5, 2 * GY - m2y)}
def about(p):
    I = R = 0.0
    for x, y in cells:
        r = math.hypot(x - p[0], y - p[1]) / 1000; I += r * r; R += r
    return rho * dA * I, rho * dA * g * R
props = {k: about(v) for k, v in P.items()}

# U4 밑 원판: 원판 위 매트 무게 끌림(원판 회전은 바퀴 접점이 정함, 나머지 면은 상대 미끄럼) — 어림 mu 0.3 x 2.89 N x 평균 상대 팔 0.04
W_disk = rho * math.pi * 0.125 ** 2 * g
T_disk_scrub = 0.3 * W_disk * 0.04
T_disk_brg = 2 * 0.005 * (0.1 / 0.075)       # 6004ZZ x2 시동 토크 어림 0.005 N·m씩, 바퀴 접점 팔 비 0.1/0.075
I_disk = 0.5 * (583642e-9 * 2680) * 0.125 ** 2 * (0.1 / 0.075) ** 2   # A5052 원판 관성(매트 피벗 기준 환산)
def seg(name, th, t, w, piv, cr=0.02, mus=None, extra=True):
    I, Rg = props[piv]; alpha = 4 * math.radians(th) / t ** 2
    have = mu_w * F4 * d1
    T_strip = 0.0
    if "U5" in w:
        have += mu_w * (F5 - f5) * d2
        if mus is not None: T_strip = mus * (F5 - f5) * d2   # 바퀴가 매트를 띠 위로 미끄러뜨림
    T_ex = (T_disk_scrub + T_disk_brg) if extra else 0.0
    Ie = I + (I_disk if extra else 0.0)
    need = cr * Rg + Ie * alpha + T_ex + T_strip
    room = have - cr * Rg - T_ex - T_strip
    tmin = math.sqrt(4 * math.radians(th) * Ie / room) if room > 0 else None
    return dict(seg=name, theta_deg=th, t_s=t, wheels=w, pivot=piv, alpha=round(alpha, 4), T_roll=round(cr * Rg, 3),
                T_acc=round(Ie * alpha, 3), T_extra=round(T_ex, 3), T_strip=round(T_strip, 3), need=round(need, 3),
                have=round(have, 3), SF=round(have / need, 3), t_min_SF1=None if tmin is None else round(tmin, 2))
T = [("입구1 0→75", 75, 2.5, ["U4", "U5"], "entrance_m1"), ("입구1 0→75 (m2 불리 쪽)", 75, 2.5, ["U4", "U5"], "entrance_m2"),
     ("꼭짓점 75→50", 25, 1.2, ["U4", "U5"], "apex_mid"), ("꼭짓점 -25→-35", 10, 1.0, ["U4", "U5"], "apex_mid"),
     ("꼭짓점 -35→-50 U4만", 15, 3.5, ["U4"], "apex_mid"), ("꼭짓점 -50→-75 U4만", 25, 4.5, ["U4"], "apex_mid"),
     ("입구2 -75→-30 U4만", 45, 9.0, ["U4"], "entrance_m2"), ("입구2 -30→0", 30, 1.5, ["U4", "U5"], "entrance_m2")]
R = {"mass_kg": round(mass, 3), "grid_mm": st, "pivots": P,
     "props": {k: dict(I=round(v[0], 3), Rg=round(v[1], 3)) for k, v in props.items()},
     "extra": dict(W_disk_N=round(W_disk, 2), T_disk_scrub=round(T_disk_scrub, 4), T_disk_brg=round(T_disk_brg, 4), I_disk_eq=round(I_disk, 4)),
     "A_criteria_as_stated": [seg(*x, extra=False) for x in T],
     "B_with_disk": [seg(*x) for x in T],
     "C_strip_mu0.15": [seg(*x, mus=0.15) for x in T],
     "C_strip_mu0.30": [seg(*x, mus=0.30) for x in T],
     "D_roll0.05_whatif": [seg(*x, cr=0.05, extra=False) for x in T]}
# U4 혼자 구간: 6 s 하한 그대로였다면(검산)
R["U4_only_at_6s"] = [seg(x[0], x[1], 6.0, x[3], x[4]) for x in T if x[3] == ["U4"]]
# U4 혼자 구간 하중(새 하중 부품 P_M02_WHEEL_U4_drive): 접선 mu x 40 = 16 N, 바퀴 r 0.06 -> 0.96 N·m (MOT-01 모델 58.3 N·3.5 N·m 이하)
R["U4_wheel_load"] = dict(tangential_N=mu_w * F4, wheel_torque_Nm=round(mu_w * F4 * 0.06, 3), envelope_case="P_M02_* 운전 접선 58.3 N / 3.5 N·m")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("mass", R["mass_kg"], R["props"], R["extra"])
for k in ("A_criteria_as_stated", "B_with_disk", "C_strip_mu0.15", "C_strip_mu0.30", "D_roll0.05_whatif", "U4_only_at_6s"):
    print(k, [(r["seg"], r["SF"], r["t_min_SF1"]) for r in R[k]])
