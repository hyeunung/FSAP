# 디테일링 DP-3 수정 2회차: P_T05_HUB 렌치 구멍 Ø9 x4(깊이 10) + 위상 홈 1.2x0.8 x4 — 얇아진 심 손계산
# 해석 못 함 — 환경 없음(자료대기 D-16). 하중은 detail_DP-3_handcalc.py와 같은 값(D-06·D-05 임시값).
# 형상(v0.6.10 실측, tools/out/detail/DP-3/f2/chk_saved_out.json):
#   허브 X -150~-110.5, 플랜지 Ø200 t3(X -113.5~-110.5), 심 Ø76(X -150~-113.5), 축 구멍 Ø16.3(축 PSFJ16 Ø16)
#   렌치 구멍 Ø9 x4, r 28.28, 45°·135°·225°·315°, X -120.5~-110.5(깊이 10)
#   롤 MAT_TAPE_ROLL X -146.5~-114.5(폭 32) -> 구멍 구간과 겹치는 롤 받침 길이 X -120.5~-114.5 = 6
# 쓰는 법: python -B -X utf8 fea/cases/detail_DP-3_hub_handcalc.py
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_hub_handcalc.json')
pi = math.pi
SG = 30.0                  # PET-CF 층간 보수값(같은 묶음 해석부 값)
TAU = 0.5 * SG             # 전단 허용 근사(트레스카)
SF_OP, SF_MIS = 3.0, 2.0   # 같은 묶음 해석부 기준(M-09 기본값, 요구서 6-1 비어 있음)
G = 9.81
M_ROLL = 0.48              # kg, D-06 T05 선정 가득 롤
T_OP = 31.9                # N, 운전 장력 최대(D-06 T05 해석부, μ 0.4·0.5 MPa)
T_MIS = 417.5              # N, 오조작 테이프 걸림(D-05 매트 미끄럼)
R_ROLL = 97.0              # 가득 롤 반지름(Ø194)
D_CORE, D_BORE, D_H, R_H = 76.0, 16.3, 9.0, 28.28
L_HOLE = 10.0              # 구멍 깊이 = 얇아진 구간 축 길이
L_ROLL_IN_HOLE = 6.0       # 롤 받침과 구멍 구간이 겹치는 길이
L_ROLL = 32.0
res = {"case": "P_T05_HUB v0.6.10 심(구멍 4개 구간)", "fea": "해석 못 함 — 환경 없음(D-16)", "inputs": {
    "SG": SG, "TAU": TAU, "M_ROLL": M_ROLL, "T_OP": T_OP, "T_MIS": T_MIS, "R_ROLL": R_ROLL,
    "basis": "D-06·D-05 임시값, detail_DP-3_handcalc.py와 같은 하중"}, "checks": {}}
W = M_ROLL * G
for case, T, sfm in (("운전", T_OP, SF_OP), ("오조작", T_MIS, SF_MIS)):
    F = math.hypot(T, W) if case == "운전" else T + W   # 오조작은 같은 방향으로 더함(보수)
    # (1) 구멍 구간 순단면 전단: 하중 전부가 구멍 구간 10 mm만으로 지난다고 본다(보수). 구멍 두 개를 지나는 지름 단면
    net_w = (D_CORE - D_BORE) - 2 * D_H
    A = net_w * L_HOLE
    tau = 2.0 * F / A                                   # 두꺼운 고리 최대/평균 ≈ 2
    kt = 3.0                                            # 구멍 응력 집중 보수값
    sf1 = TAU / (tau * kt)
    # (2) 바깥 살 5.22: 롤 면압이 구멍 폭 9를 건너는 양단 고정 보
    p = F / (D_CORE * L_ROLL)                           # 롤 면압(투영)
    t_o = D_CORE / 2 - (R_H + D_H / 2)
    w = p * L_ROLL_IN_HOLE                              # N/mm (구멍 폭 방향 단위 길이당)
    Mb = w * D_H ** 2 / 12
    Zs = L_ROLL_IN_HOLE * t_o ** 2 / 6
    sig2 = Mb / Zs
    sf2 = SG / sig2
    # (3) 비틀림: 테이프 걸림이 롤 가장자리에서 허브를 돌리려 할 때(허브는 축에 헐겁게 끼워 마찰로만 돈다 -> 상한 보수)
    Tq = T * R_ROLL
    J0 = pi / 32 * (D_CORE ** 4 - D_BORE ** 4)
    Jh = 4 * (pi / 4 * D_H ** 2 * R_H ** 2 + pi * D_H ** 4 / 32)
    J = J0 - Jh
    tau3 = Tq * (D_CORE / 2) / J * kt
    sf3 = TAU / tau3
    # (4) 안 살 15.63: 축 구멍 면압(바뀌지 않음, 구멍이 축 구멍에 닿지 않음)
    t_i = (R_H - D_H / 2) - D_BORE / 2
    pb = F / (D_BORE * 39.5)
    sf4 = SG / pb
    res["checks"][case] = {
        "F_radial_N": round(F, 2), "SF_min": sfm,
        "순단면전단": {"net_w": round(net_w, 2), "A_mm2": round(A, 1), "tau_MPa": round(tau, 3), "Kt": kt, "SF": round(sf1, 2)},
        "바깥살굽힘": {"t_mm": round(t_o, 2), "p_MPa": round(p, 4), "sigma_MPa": round(sig2, 3), "SF": round(sf2, 1)},
        "비틀림": {"T_Nmm": round(Tq, 0), "J_mm4": round(J, 0), "J_loss_pct": round(100 * Jh / J0, 2), "tau_MPa": round(tau3, 3), "SF": round(sf3, 2)},
        "축구멍면압": {"t_inner_mm": round(t_i, 2), "p_MPa": round(pb, 3), "SF": round(sf4, 1)},
        "pass": min(sf1, sf2, sf3, sf4) >= sfm}
# 위상 홈 1.2 x 0.8(플랜지 테두리 r100, 플랜지 t3): 힘 경로 밖(롤은 r97 안, 테두리는 하중 없음). 플랜지 남은 높이 비 0.8/(100-38) = 1.3 %
res["checks"]["위상홈"] = {"note": "플랜지 테두리 r99.2~100, 힘 경로 밖(롤 r ≤ 97, 테두리에 닿는 것 없음). 판정 대상 아님", "loss_ratio_pct": round(100 * 0.8 / (100 - 38), 2)}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in ("운전", "오조작"):
    c = res["checks"][k]
    print(k, 'F', c["F_radial_N"], '전단 SF', c["순단면전단"]["SF"], '바깥살 SF', c["바깥살굽힘"]["SF"], '비틀림 SF', c["비틀림"]["SF"], '면압 SF', c["축구멍면압"]["SF"], 'pass', c["pass"])
print('J 손실 %', res["checks"]["운전"]["비틀림"]["J_loss_pct"])
