# 디테일링 DP-3 해석부 2회차(v0.6.10) — P_T05_HUB 손계산 다시 풀기 + 다른 모델 교차 확인
# 해석 못 함 — 환경 없음(자료대기 D-16). 하중·재료는 detail_DP-3_hub_handcalc.py와 같다(D-06·D-05 임시값).
# 형상은 tools/out/detail/DP-3/stepout2/P_T05_HUB.step 에서 읽은 값(원통면 r38·r8.15·r4.5 x4, 구멍 바닥 X -120.5).
# 바뀌지 않은 부품(앞벽·홀더 좌면 등)은 fea/results/detail_DP-3_handcalc.json 값을 그대로 옮긴다(E-17·E-21).
# 쓰는 법: python -B -X utf8 fea/cases/detail_DP-3_fea2_check.py
import json, math, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEP = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-3', 'stepout2', 'P_T05_HUB.step')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_fea2_check.json')
PREV = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_handcalc.json')
HUBJ = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_hub_handcalc.json')
pi = math.pi

# 1) STEP 형상 확인
txt = open(STEP, encoding='utf-8', errors='ignore').read()
radii = sorted(round(float(r), 3) for r in re.findall(r"CYLINDRICAL_SURFACE\('',#\d+,([0-9.Ee+-]+)\)", txt))
pts = [tuple(float(v) for v in m) for m in re.findall(r"CARTESIAN_POINT\('',\(([-0-9.Ee+]+),([-0-9.Ee+]+),([-0-9.Ee+]+)\)\)", txt)]
xs = [p[0] for p in pts]
geo = {"cyl_radii": radii, "n_r4.5": sum(1 for r in radii if abs(r - 4.5) < 0.01),
       "has_r38": any(abs(r - 38) < 0.01 for r in radii), "has_r8.15": any(abs(r - 8.15) < 0.01 for r in radii),
       "x_min": round(min(xs), 3), "x_max": round(max(xs), 3),
       "hole_bottom_X-120.5": any(abs(x + 120.5) < 0.01 for x in xs)}
# 구멍 가운데: 바닥 원 위 점들의 (Y,Z) 평균은 못 쓰므로 조건만 확인. 축 거리 r28.28 = 20·√2(볼트 Y 730/770, Z 180/220)
R_H = 20 * math.sqrt(2)
geo["R_hole_center"] = round(R_H, 3)
geo["ok"] = geo["n_r4.5"] == 4 and geo["has_r38"] and geo["has_r8.15"] and geo["hole_bottom_X-120.5"]

# 2) 재료·하중(모델링부 손계산과 같음)
SG, TAU = 30.0, 15.0
W = 0.48 * 9.81
F_mis = 417.5 + W
F_op = math.hypot(31.9, W)
D_CORE, D_BORE, D_H = 76.0, 16.3, 9.0
L_HUB = 39.5            # X -150 ~ -110.5
L_CORE = 36.5           # 심 X -150 ~ -113.5
L_HOLE = 10.0
res = {"case": "detail_DP-3_fea2 P_T05_HUB v0.6.10", "fea": "해석 못 함 — 환경 없음(D-16)", "geometry": geo, "checks": {}}

# 3) 모델링부 식 다시 풀기(같은 식) — 결과 파일과 같은지
hub_prev = json.load(open(HUBJ, encoding='utf-8'))
res["checks"]["모델링부_식_재현"] = {k: hub_prev["checks"][k]["순단면전단"]["SF"] for k in ("운전", "오조작")}

# 4) 교차 모델 A: 지름 단면 전단을 허브 길이 전체로(구멍 구간 10은 순폭, 나머지는 온폭). Kt 3은 구멍 구간에만 쓰는 대신 평균에 그대로 곱해 보수
def shear_full(F):
    A = (D_CORE - D_BORE - 2 * D_H) * L_HOLE + (D_CORE - D_BORE) * (L_HUB - L_HOLE)
    tau = 2 * F / A * 3.0
    return round(A, 1), round(tau, 3), round(TAU / tau, 2)
# 교차 모델 B: 롤 받침 폭 32(X -146.5~-114.5) 중 구멍 구간 6만 순폭, 나머지 26은 온폭 — 롤 면압이 지나는 길이로만
def shear_roll(F):
    A = (D_CORE - D_BORE - 2 * D_H) * 6.0 + (D_CORE - D_BORE) * 26.0
    tau = 2 * F / A * 3.0
    return round(A, 1), round(tau, 3), round(TAU / tau, 2)
# 교차 모델 C: 바깥 살 5.22를 구멍 둘레 곡면 판으로 — 구멍 지름 9를 건너는 단순지지(양단 고정보다 불리, M = wl²/8)
def outer_ss(F):
    p = F / (D_CORE * 32.0)
    t = D_CORE / 2 - (R_H + D_H / 2)
    w = p * 6.0
    M = w * D_H ** 2 / 8
    Z = 6.0 * t ** 2 / 6
    s = M / Z * 3.0          # Kt 3 보수
    return round(t, 2), round(s, 3), round(SG / s, 1)
for case, F, sfm in (("운전", F_op, 3.0), ("오조작", F_mis, 2.0)):
    a = shear_full(F); b = shear_roll(F); c = outer_ss(F)
    res["checks"][case] = {"F_N": round(F, 2), "SF_min": sfm,
        "A_전길이전단": {"A_mm2": a[0], "tau_Kt_MPa": a[1], "SF": a[2]},
        "B_롤폭전단": {"A_mm2": b[0], "tau_Kt_MPa": b[1], "SF": b[2]},
        "C_바깥살_단순지지_Kt3": {"t_mm": c[0], "sigma_MPa": c[1], "SF": c[2]},
        "pass": min(a[2], b[2], c[2]) >= sfm}

# 5) 플랜지 뿌리(models.json 참고 하중: 롤 자중 x3 g를 플랜지 끝, 지렛대 62) — 구멍 r ≤ 32.78 < 38이라 뿌리 둘레 r38 단면은 그대로
Fr = 0.48 * 9.81 * 3
M = Fr * 62
b = 60.0      # models.json 띠 60
t = 3.0
s = M / (b * t ** 2 / 6)
res["checks"]["플랜지뿌리_참고"] = {"hole_outer_r": round(R_H + D_H / 2, 2), "root_r": 38.0, "unchanged": R_H + D_H / 2 < 38,
    "sigma_MPa": round(s, 3), "SF": round(SG / s, 1), "groove_note": "위상 홈 r99.2~100은 플랜지 끝(지렛대 바깥), 하중 자리 아님"}

# 6) 바뀌지 않은 판정값 옮김
prev = json.load(open(PREV, encoding='utf-8'))
fw = prev["A_guide_front_wall"]
hb = prev["B_holder_flange"]
res["carried_unchanged"] = {
    "앞벽_두변_실측L40.5": fw["실측_L40.5"]["sf_two_edge_est"], "앞벽_두변_옛식L37": fw["옛식_L37"]["sf_two_edge_est"],
    "앞벽_외팔_실측": fw["실측_L40.5"]["sf_cantilever"], "앞벽_외팔_옛식": fw["옛식_L37"]["sf_cantilever"],
    "앞벽_항복선_점하중": fw["항복선_점하중_모서리"]["sf_elastic_m"],
    "홀더좌면_와셔없음": hb["좌면_와셔없음"]["sf_tightening"]["조임 좌면"],
    "홀더좌면_와셔Ø10": hb["좌면_와셔Ø10"]["sf_tightening"]["조임 좌면"]}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('geo ok', geo["ok"], 'r4.5 x', geo["n_r4.5"], 'x', geo["x_min"], geo["x_max"])
print('재현', res["checks"]["모델링부_식_재현"])
for k in ("운전", "오조작"):
    c = res["checks"][k]
    print(k, 'F', c["F_N"], 'A', c["A_전길이전단"]["SF"], 'B', c["B_롤폭전단"]["SF"], 'C', c["C_바깥살_단순지지_Kt3"]["SF"], c["pass"])
print('플랜지', res["checks"]["플랜지뿌리_참고"])
print('옮김', res["carried_unchanged"])
