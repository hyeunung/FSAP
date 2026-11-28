# -*- coding: utf-8 -*-
"""디테일링 DP-2(체결 길이 · 탭 깊이, v2.30.7) 해석부 손계산. FEA 못 함 — 환경 없음(자료대기 D-16). CAD 안 씀.
형상: fea/results/detail_DP-2_stepgeo.json(STEP 원통 자리 · 깊이, 전 = tools/out/detail/stepout v2.30.6).
하중 · 고정: fea/models.json 그대로(모델 변경 0). 지난 케이스 값은 결과 json에서 읽는다.
단면: E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로" -> 탭 자리 순단면(나사 바깥지름 Ø5를 밑구멍 깊이 전체에 — 보수).
기준: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2, 3배 넘으면 과사양). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/detail_DP-2_handcalc.py -> fea/results/detail_DP-2_handcalc.json"""
import json, math, sys
sys.path.insert(0, "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools")
import handcalc as hc   # 엔진 도구(읽기만)
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
RES = ROOT + "/fea/results/"
geo = json.load(open(RES + "detail_DP-2_stepgeo.json", encoding="utf-8"))
c1 = json.load(open(RES + "mech_RX-12-C1_handcalc.json", encoding="utf-8"))
f1 = json.load(open(RES + "mech_RX-12-C1_fea1_handcalc.json", encoding="utf-8"))
SY_AL, E_AL, SY_SUS = 195.0, 70300.0, 205.0
D_TH = 5.0            # M5 나사 바깥지름(순단면에 쓰는 구멍 지름)
T_NM = 4.5            # 조임 토크 N·m(이 프로젝트 M5 관례: RX-14 · RX-12-C1 fea1 손계산) -> 예압 4.5 kN
FV_SLIP, MU = 4000.0, 0.15   # 미끄럼은 예압 4 kN · μ 0.15(D-54, 낮은 쪽)
out = {"method": "손계산(FEA 못 함 — 환경 없음, D-16). 모델 표 fea/models.json 그대로",
       "assume": {"조임 토크 N·m": T_NM, "미끄럼 예압 N": FV_SLIP, "mu": MU, "순단면 구멍 지름": D_TH,
                  "T너트 HNTT8-5 모재": "SS400 대용(RX-14 선례)", "PGX62 축 모재": "S45C 대용(카탈로그 재질 미확인 — SS400이어도 조임 암나사 전단 1.64)"}}

def net(b, h, dh, th):
    """폭 b · 높이 h 직사각 단면, 윗면에서 지름 dh · 깊이 th 구멍. 중립축(밑면 기준) · I · Z_top · Z_bot."""
    a1, y1 = b * (h - th), (h - th) / 2.0
    a2, y2 = (b - dh) * th, h - th / 2.0
    A = a1 + a2; yc = (a1 * y1 + a2 * y2) / A
    I = b * (h - th) ** 3 / 12 + a1 * (y1 - yc) ** 2 + (b - dh) * th ** 3 / 12 + a2 * (y2 - yc) ** 2
    return {"A": round(A, 1), "yc": round(yc, 3), "I": round(I, 1), "Z_top": round(I / (h - yc), 1), "Z_bot": round(I / yc, 1)}

def ktn(d, w):
    """가운데 구멍 있는 유한 폭 판(인장)의 순단면 응력 집중(Peterson/Heywood 식): 2 + (1 - d/w)^3."""
    return round(2.0 + (1.0 - d / w) ** 3, 3)

def sfrow(sig, need, sy=SY_AL):
    sf = sy / sig
    return {"sigma_MPa": round(sig, 2), "SF": round(sf, 2), "need": need, "margin_pct": round((sf / need - 1) * 100, 1),
            "ok": sf >= need, "near(±10%)": abs(sf / need - 1) <= 0.10, "over_3x": sf >= 3 * need}

# ---------- 1. 플랩 바 L1 · L2 · L3 (A5052 10(Y) × 30(Z) × 662, XN↔XP 단순지지) ----------
L = 662.0; b, h = 10.0, 30.0
w1 = c1["FLAP_BAR_L2_3g"]["w1_N"]; P = 100.0; w = w1 / L
holes = [500 - 423.0, 700 - 423.0, 900 - 423.0, 1050 - 423.0]          # STEP: 탭 X 500 · 700 · 900 · 1050, 바 X 423~1085
sec = {"gross": {"I": b * h ** 3 / 12, "Z": b * h * h / 6}, "tap10(전)": net(b, h, D_TH, 10.0), "tap15(후)": net(b, h, D_TH, 15.0)}
kt = ktn(D_TH, b)
rows = {}
for tag, s in (("전(깊이 10)", sec["tap10(전)"]), ("후(깊이 15)", sec["tap15(후)"])):
    zmin = min(s["Z_top"], s["Z_bot"]); worst = None
    for x in holes:
        Mw = w * x * (L - x) / 2.0                                    # 1 g 고른 하중
        Mh = P * x * (L - x) / L                                      # 손 100 N이 그 탭 바로 위(가운데보다 불리)
        r = {"x": x, "run_3g": sfrow(kt * 3 * Mw / zmin, 3.0), "mis_1g+hand": sfrow(kt * (Mw + Mh) / zmin, 2.0)}
        if worst is None or r["mis_1g+hand"]["SF"] < worst["mis_1g+hand"]["SF"]: worst = r
    rows[tag] = {"Z_min": zmin, "Ktn": kt, "worst_hole": worst}
def defl(Ihole):
    """가운데 처짐(단위 하중법, 1 g 고른 하중 + 가운데 손 100 N). 탭 자리 ±2.5만 I가 줄어듦."""
    n = 6620; dx = L / n; d = 0.0
    for i in range(n):
        x = (i + 0.5) * dx
        M = w * x * (L - x) / 2.0 + (P * x / 2.0 if x <= L / 2 else P * (L - x) / 2.0)
        m = x / 2.0 if x <= L / 2 else (L - x) / 2.0
        I = Ihole if any(abs(x - hx) <= D_TH / 2 for hx in holes) else sec["gross"]["I"]
        d += M * m / (E_AL * I) * dx
    return d
dg, d10, d15 = defl(sec["gross"]["I"]), defl(sec["tap10(전)"]["I"]), defl(sec["tap15(후)"]["I"])
out["FLAP_BAR_L1·L2·L3"] = {"model": "models.json 그대로: XN↔XP 662 단순지지, 몫 넓이 350×662 자중 ×3 g / 1 g + 손 100 N",
    "section": sec, "gross_midspan(지난 값)": {"run": c1["FLAP_BAR_L2_3g"]["SF"], "mis": c1["FLAP_BAR_L2_misuse"]["SF"]},
    "net_at_tap": rows, "defl_mm": {"구멍 없음(지난 값)": round(dg, 4), "탭 10(전)": round(d10, 4), "탭 15(후)": round(d15, 4), "DP-2로 늘어난 값": round(d15 - d10, 5)},
    "tap_wall_mm": (b - D_TH) / 2, "bottom_remain_mm": h - 15.0}

# ---------- 2. XN (A5052 18(X) × 30(Z) × 895) ----------
bx = 18.0
sx = {"gross": {"I": bx * h ** 3 / 12, "Z": bx * h * h / 6}, "tap10(전)": net(bx, h, D_TH, 10.0), "tap15(후)": net(bx, h, D_TH, 15.0)}
ktx = ktn(D_TH, bx)
# (가) 0° 빗장 A·B 사이 676 단순지지, 가운데(Y −750 = 탭 자리)에 L2 반력 + 손 100 N
M_lat = (w1 / 2 + P) * 676.0 / 4
# (나) 빗장 뺀 충격: 패드 A·B 사이 604, 가운데 한 점(fea1). 가운데 Y −750에 윗면 탭이 있다
span = f1["XN"]["span_mm"]; Frun, Fmis = f1["XN"]["run"]["F_total"], f1["XN"]["mis"]["F_total"]
xn = {}
for tag, s in (("전(깊이 10)", sx["tap10(전)"]), ("후(깊이 15)", sx["tap15(후)"])):
    zmin = min(s["Z_top"], s["Z_bot"])
    xn[tag] = {"Z_min": zmin,
               "latch_mis(순단면 × Ktn)": sfrow(ktx * M_lat / zmin, 2.0),
               "bump_run(순단면 × Ktn %.3f)" % ktx: sfrow(ktx * Frun * span / 4 / zmin, 3.0),
               "bump_mis(순단면 × Ktn %.3f)" % ktx: sfrow(ktx * Fmis * span / 4 / zmin, 2.0),
               "bump_run(순단면 × Kt 2, 옛 모델 Kt)": sfrow(2.0 * Frun * span / 4 / zmin, 3.0),
               "bump_mis(순단면 × Kt 2, 옛 모델 Kt)": sfrow(2.0 * Fmis * span / 4 / zmin, 2.0)}
out["FLAP_BAR_XN"] = {"model": "models.json 그대로: (가) 빗장 A·B 676 단순지지 + 가운데 L2 반력 + 손 100 N, (나) load_bump 패드 A·B 604 가운데 한 점 Kt 2",
    "section": sx, "Ktn": ktx, "old_model_gross_Kt2(지난 값, 형상 같음)": {"run": f1["XN"]["run"]["SF"], "mis": f1["XN"]["mis"]["SF"]},
    "net_at_center_tap": xn, "F_run_N": Frun, "F_mis_N": Fmis,
    "note": "가운데 탭(414, −750)이 최대 굽힘 자리와 겹친다. 밑면 탭 4(깊이 13)는 그대로이고 가운데에서 300 떨어져 있다"}

# ---------- 3. XP (A5052 15(X) × 30(Z) × 895) ----------
bp = 15.0
Fh = c1 and (11.4 * 9.80665 * 3 / 4 + 100.0)       # detail_2026-11-28: 3 g 반 + 손 100 N이 경첩 하나에
Mh = Fh * 230.0 / 4
sp = {"gross": {"I": bp * h ** 3 / 12, "Z": bp * h * h / 6}, "윗 탭 10(전)": net(bp, h, D_TH, 10.0), "윗 탭 15(후)": net(bp, h, D_TH, 15.0), "윗 탭 12(XP_TAP_1)": net(bp, h, D_TH, 12.0)}
# 혀 탭(X 방향, Z −33 = 밑면에서 10, 관통 15 — 전에는 깊이 10): 높이 5 띠가 폭 15(전 10)만큼 빠짐. 중립축 가운데(15)에서 5 아래
def side_hole(depth):
    I = bp * h ** 3 / 12 - (depth * D_TH ** 3 / 12 + depth * D_TH * 5.0 ** 2)
    A = bp * h - depth * D_TH
    return {"A": A, "I": round(I, 1), "Z": round(I / 15.0, 1)}
sp["혀 탭 10(전)"], sp["혀 탭 관통(후)"] = side_hole(10.0), side_hole(15.0)
# XP_TAP_1(Y −330, Z −13~−25) + 경첩 탭(Y −335, Z −28 ± 2.5, X 깊이 10)을 같은 단면에 겹쳐 본 보수 값
I_comb = net(bp, h, D_TH, 12.0)["I"] - (10.0 * D_TH ** 3 / 12 + 10.0 * D_TH * 2.0 ** 2)
sp["XP_TAP_1 + 경첩 탭 겹침(보수)"] = {"I": round(I_comb, 1), "Z": round(I_comb / 17.5, 1)}
zs = {k: (v.get("Z") or min(v["Z_top"], v["Z_bot"])) for k, v in sp.items()}
ktp = ktn(D_TH, bp)
wall_pilot = math.hypot(5.0 - 2.1, 3.0) - 2.1          # XP_TAP_1 밑구멍 바닥 테두리 ↔ 경첩 탭 원통(Ø4.2끼리)
wall_thread = math.hypot(5.0 - 2.5, 3.0) - 2.5         # 나사 바깥지름 Ø5끼리
out["FLAP_BAR_XP"] = {"model": "models.json 그대로: 접이판 묶음 11.4 kg ×3 g 반 + 손 100 N이 경첩 하나에, 230 가운데",
    "Fh_N": round(Fh, 1), "M_Nmm": round(Mh, 1), "Z": zs, "Ktn": ktp,
    "sf_mis": {k: sfrow(ktp * Mh / z if k != "gross" else Mh / z, 2.0) for k, z in zs.items()},
    "XP_TAP_1↔경첩 탭 살 mm": {"밑구멍 Ø4.2끼리": round(wall_pilot, 2), "나사 Ø5끼리": round(wall_thread, 2), "옆으로 본 틈(모델링 보고서)": 0.8,
                          "note": "윗 탭은 Z −25에서 멈추고 경첩 탭 윗선은 Z −25.9(나사 −25.5) — 높이로 0.5~0.9 떨어져 실제 가장 얇은 살은 빗변 값"}}

# ---------- 4. 롤 핀 G1 · TOP (SUS304, 자루 Ø10, 턱 Ø14, 머리 Ø16. 뒤끝 M5 탭) ----------
Z_solid = math.pi * 10 ** 3 / 32
Z_holl = math.pi * (10 ** 4 - D_TH ** 4) / (32 * 10)
HAND = 100.0
root = -2.1                       # STEP: 턱 Ø14 Y −2.1~1.5, 자루 Ø10 Y −38~−2.1, 탭 Y 1.5 → −13.5(전 −10.5)
pin = {"Z_solid(지난 손계산)": round(Z_solid, 2), "Z_hollow(Ø10/Ø5)": round(Z_holl, 2),
       "root_misuse(팔 36)": {"지난 값(속 찬 단면)": sfrow(HAND * 36 / Z_solid, 2.0, SY_SUS), "빈 단면(전 · 후 같음 — 탭이 전에도 뿌리를 지남)": sfrow(HAND * 36 / Z_holl, 2.0, SY_SUS)},
       "root_operating(7.1 N 팔 18)": sfrow(5 * math.sqrt(2) * 18 / Z_holl, 3.0, SY_SUS),
       "탭 끝 단면(전 Y −10.5 팔 27.6 → 후 Y −13.5 팔 24.6)": {"전": sfrow(HAND * 27.6 / Z_solid, 2.0, SY_SUS), "후(빈 단면이 3 더 김)": sfrow(HAND * 27.6 / Z_holl, 2.0, SY_SUS)},
       "wall_mm": {"밑구멍 Ø4.2": 2.9, "나사 Ø5": 2.5},
       "note": "뿌리(턱 앞)는 DP-2 전에도 탭이 지나는 빈 단면이었다. 지난 손계산이 속 찬 단면으로 봐 5.59였고 빈 단면으로 5.24 — DP-2가 낮춘 것이 아니라 단면을 측정대로 바로잡은 값"}
out["M06_G1_PIN·TOP_PIN"] = pin

# ---------- 5. 가스 스프링 팔 블록 (A5052 40 × 44 × 30) ----------
F_GS = c1["gas_spring"]["Fmax_tol"]
out["GS_ARM_BLK"] = {"model": "models.json 그대로: 가스 스프링 최대 %.0f N, 볼트 인장으로 보수(F/2)" % F_GS,
    "taps": "윗 탭 2(X 1050 · 1070, Y −1190) 깊이 10 → 15, 옆 탭 2(X 1048 · 1072, Z −28) 깊이 10 → 15(Y −1224 → −1209)",
    "윗 탭↔옆 탭 끝 거리 mm": round(1209 - 1190 - 2.5, 1), "윗 탭 밑 남은 살 mm": 15.0, "옆 탭 X 가장자리 살 mm": 8.0 - 2.5,
    "block_shear_MPa": round(F_GS / (40.0 * 30.0), 2), "slip_귀판(그대로)": round(2 * FV_SLIP * MU / F_GS, 2),
    "note": "귀판 볼트 미끄럼 0.76은 길이와 상관없다(FEA-05, 맞춤 핀 Ø5 ×2 — DP-6 몫). DP-2로는 나사 전단만 오른다"}

# ---------- 6. 볼트 묶음(E-19: 같은 부품 쌍 · 형번 · 축 방향, 가장 불리한 하나) ----------
B = []
def bolt(key, n, spec, le_old, le_new, load, need, base, seat, cls="12.9", dw=8.5, note="", torque=T_NM, src=""):
    """seat: 머리가 앉는 모재(좌면). 암나사 모재 base와 다르면 좌면만 따로 본다."""
    new = hc.calc(5, le_new, load, torque, cls, base, dw, 5.5, sf_min=need)
    old = hc.calc(5, le_old, load, torque, cls, base, dw, 5.5, sf_min=need)
    pg = hc.BASE[seat][1]; ab = math.pi / 4 * (dw * dw - 5.5 * 5.5)
    seat_sf = pg * ab / new["preload_N"]
    new["sf_tightening"]["조임 좌면"] = round(seat_sf, 2); old["sf_tightening"]["조임 좌면"] = round(seat_sf, 2)
    ok = all(v >= need for v in new["sf_operating"].values()) and all(v >= 1.0 for v in new["sf_tightening"].values()) and le_new >= 7.5
    near = [k for k, v in new["sf_operating"].items() if need <= v < 1.1 * need] + [k for k, v in new["sf_tightening"].items() if 1.0 <= v < 1.1]
    strip_N = 0.6 * hc.BASE[base][0] * math.pi * 5 * le_new * 0.375
    r = {"key": key, "n": n, "spec": spec, "le_old": le_old, "le_new": le_new, "load_N": round(load, 1), "need": need, "base": base, "seat": seat, "class": cls,
         "old": {"op": old["sf_operating"], "tight": old["sf_tightening"]}, "new": {"op": new["sf_operating"], "tight": new["sf_tightening"]},
         "torque_limit_Nm(암나사 SF 1)": round(strip_N * 0.2 * 5 / 1000, 2), "ok": ok, "needs_fea": bool(near), "near": near, "note": note, "load_src": src}
    B.append(r); return r

up = c1["UPSTOP_TONGUE_bolts"]["T_per_bolt_N"]
T_bump = f1["load_cases"]["오조작: 도착 31 mm/s(혀 닿기 직전)"]["F_one"] * 18.0 * 132 / (92.0 ** 2 + 132.0 ** 2)
W_FLAP = 141.0
bolt("테이블 판넬 접시 SFB5-16 → HNTT8-5", 109, "SFB5-16", 3.5, 9.0, 100.0, 2.0, "SS400", "SUS304", cls="10.9", dw=10.0,
     note="접시 머리 Ø10 원뿔 자리(투영 넓이). 판넬이 형재에 눌리는 쪽이라 볼트 인장은 판을 드는 손 100 N뿐", src="오조작 손 100 N(D-38 임시)")
bolt("플랩 판 → 바 5품번(윗 탭, XP_TAP_1 뺌)", 21, "CB5-16", 7.0, 11.0, W_FLAP * 3 / 23 + 100.0, 2.0, "A5052", "A5052",
     note="판 t5 A5052. −90° 때 판 묶음 141 N ×3 g를 23개가 나눔 + 손 100 N이 볼트 하나에(보수)", src="mech_RX-12-C1 W 141 N")
bolt("플랩 판 → XP_TAP_1(지금 CB5-16)", 1, "CB5-16", 7.0, 11.0, W_FLAP * 3 / 23 + 100.0, 2.0, "A5052", "A5052",
     note="검도 기준 1건 자리 — 밑구멍 12라 볼트 끝–바닥 1.0. 수치는 되지만 끝까지 못 조인다(M-01)")
bolt("플랩 판 → XP_TAP_1(검도 수정안 CB5-14)", 1, "CB5-14", 7.0, 9.0, W_FLAP * 3 / 23 + 100.0, 2.0, "A5052", "A5052", note="검도 수정안: 물림 9.0")
bolt("플랩 판 → 팔 블록 윗 탭", 2, "CB5-16", 7.0, 11.0, F_GS / 2, 3.0, "A5052", "A5052", src="models.json 가스 스프링 최대 ÷ 2(볼트 인장으로 보수)")
bolt("귀판 → 팔 블록 옆 탭", 2, "CB5-16", 6.0, 10.0, F_GS / 2, 3.0, "A5052", "SUS304", note="전단을 인장 값으로 본 보수. 미끄럼 0.76은 그대로(FEA-05)", src="〃")
bolt("혀 → XP 옆 탭(관통)", 2, "CB5-16", 6.0, 10.0, up, 3.0, "A5052", "A5052", src="mech_RX-12-C1 UPSTOP_TONGUE_bolts")
bolt("롤 핀 G1 · TOP 당김 볼트", 2, "CB5-16", 6.0, 10.0, HAND * 21.5 / 7, 2.0, "SUS304", "SUS304", note="지난 손계산은 물림 8로 가정(실측 전 6.0)", src="mech_M06 손 100 N × 21.5 / 7")
bolt("허브 볼트 → PGX62 축 탭(U4 · U5)", 2, "CB5-16", 4.75, 8.5, 100.0, 2.0, "S45C", "A6061-T6",
     note="키 허브의 축 방향 빠짐 막음. 누름 100 N × μ 0.8 = 80 N(운전)보다 큰 손 100 N으로 봄. 축 재질은 가정", src="D-92 누름 30~100 N")
bolt("POM 멈춤 STOP_A · B → HNTT8-5", 4, "CB5-16", 5.0, 9.0, c1["STOP_POM"]["F_total_N"] / 2, 2.0, "SS400", "POM", src="mech_RX-12-C1 STOP_POM")
bolt("POM 멈춤 — 조임 2.0 N·m 지정안", 4, "CB5-16", 5.0, 9.0, c1["STOP_POM"]["F_total_N"] / 2, 2.0, "SS400", "POM", torque=2.0, note="좌면 Ø8.5/Ø5.5 머리 그대로")
bolt("POM 멈춤 — 조임 2.0 N·m + 소형 와셔 Ø9(D-216)", 4, "CB5-16", 5.0, 9.0, c1["STOP_POM"]["F_total_N"] / 2, 2.0, "SS400", "POM", torque=2.0, dw=9.0, note="자리파기 Ø9.5에 들어가는 와셔")
bolt("범퍼 브래킷 BUMP_BRKT_A · B → HNTT8-5", 4, "CB5-16", 5.5, 9.0, T_bump, 2.0, "SS400", "A5052", src="mech_RX-12-C1_fea1 지렛대(오조작 31 mm/s)")
bolt("경첩 고정 잎 → HNTT8-5", 4, "CB5-14", 6.5, 8.5, c1["HINGE_reaction"]["per_hinge_max_N"] / 2, 3.0, "SS400", "SUS304", note="전단을 인장 값으로 본 보수. 경첩 잎 재질은 STEP 대기(SUS304로 봄)", src="mech_RX-12-C1 경첩 하나 786.5 N")
bolt("빗장 블록 LATCH_BLK_A · B → HNTT8-5", 4, "CB5-20", 5.5, 9.0, c1["LATCH_BLK"]["F_N"] / 2, 2.0, "SS400", "A5052", src="mech_RX-12-C1 LATCH_BLK")
bolt("위 멈춤 블록 UPSTOP_BLK → HNTT8-5", 2, "CB5-20", 5.5, 9.0, c1["UPSTOP_TONGUE_static"]["F_tol_N"] / 2, 2.0, "SS400", "A5052", note="미끄럼 2.01(기준 +0.5 %)은 길이와 상관없이 그대로", src="mech_RX-12-C1 혀 정적 597 N")
bolt("원판 받침 DISK_BASE + 심 → HNTT8-5", 4, "CB5-22", 5.5, 7.5, 95.5 / 4, 2.0, "SS400", "SUS304", src="mech_M04R 접선 오조작 95.5 N ÷ 4")
bolt("U3 LDRV_BRKT → HNTT8-5", 4, "CB5-20", 5.0, 9.0, 153.7, 2.0, "SS400", "A6061-T6", note="헤드 취부(D-10) — 기록", src="mech_MOT-01 U3 오조작 T 153.7 N")
bolt("R2 브래킷 발 → HNTT8-5", 2, "CB5-16", 3.5, 7.5, 725.5, 2.0, "SS400", "SUS304", src="mech_RX-14 오조작 손 100 N 지렛대")
bolt("커튼 받침 F39-LSGF · LC2F_BRKT → HNTT8-5", 8, "CB5-14", 6.25, 8.5, 100.0, 2.0, "SS400", "SUS304", note="받침 하나가 손 100 N 전부(가정 검토 값)", src="detail_2026-11-28 LC2F")
bolt("커튼 기둥 받침 LC_BRKT_FR_SM → HNTT8-5", 8, "CB5-16", 5.5, 9.0, 460.1 / 2, 2.0, "SS400", "SUS304", src="detail_2026-11-28 단 반력 460.1 N ÷ 2")
bolt("커튼 이음판 LC_JOINT_FL_WJ → HNTT8-5", 4, "CB5-16", 3.5, 7.5, 530.8, 2.0, "SS400", "A5052", src="detail_2026-11-28 볼트 짝힘 530.8 N")
out["bolts"] = B
out["insert_MBIS5(안 바꿈)"] = {"n": 4, "engage_mm": 7.56, "note": "인서트 · 볼트 · 하중 그대로 — 지난 판정(mech_U6S: 축 링 조임 ≤ 1.2 N·m 조건, PCYL_BRKT 2.77) 그대로. 체결 목록의 물림만 2.6 → 7.56으로 바로잡힘"}

# ---------- 판정 모음 ----------
S = []
def add(item, r): S.append({"item": item, **{k: r[k] for k in ("SF", "need", "margin_pct", "ok", "near(±10%)", "over_3x")}})
wh = out["FLAP_BAR_L1·L2·L3"]["net_at_tap"]["후(깊이 15)"]["worst_hole"]
add("L1~L3 탭 순단면 운전", wh["run_3g"]); add("L1~L3 탭 순단면 오조작", wh["mis_1g+hand"])
xa = out["FLAP_BAR_XN"]["net_at_center_tap"]["후(깊이 15)"]
for k, v in xa.items():
    if k != "Z_min": add("XN " + k, v)
add("XP 윗 탭 15 오조작", out["FLAP_BAR_XP"]["sf_mis"]["윗 탭 15(후)"]); add("XP 혀 탭 관통 오조작", out["FLAP_BAR_XP"]["sf_mis"]["혀 탭 관통(후)"])
add("XP_TAP_1 + 경첩 탭 오조작", out["FLAP_BAR_XP"]["sf_mis"]["XP_TAP_1 + 경첩 탭 겹침(보수)"])
add("핀 뿌리 오조작(빈 단면)", pin["root_misuse(팔 36)"]["빈 단면(전 · 후 같음 — 탭이 전에도 뿌리를 지남)"]); add("핀 뿌리 운전", pin["root_operating(7.1 N 팔 18)"])
out["summary_parts"] = S
out["summary_bolts"] = [{"key": r["key"], "n": r["n"], "le": "%s → %s" % (r["le_old"], r["le_new"]),
                         "op_min": min(r["new"]["op"].values()), "need": r["need"], "tight_min": min(r["new"]["tight"].values()),
                         "tight_min_old": min(r["old"]["tight"].values()), "ok": r["ok"], "needs_fea": r["needs_fea"]} for r in B]
out["ng"] = [s["item"] for s in S if not s["ok"]] + [r["key"] for r in B if not r["ok"]]
out["near"] = [s["item"] for s in S if s["near(±10%)"]] + [r["key"] + " " + "·".join(r["near"]) for r in B if r["needs_fea"]]
json.dump(out, open(RES + "detail_DP-2_handcalc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 화면 15줄 요약(E-20)
print("부품 판정 %d줄: 미달 %d · 기준 ±10%% 안 %d" % (len(S), sum(not s["ok"] for s in S), sum(s["near(±10%)"] for s in S)))
for s in sorted(S, key=lambda s: s["margin_pct"])[:5]: print("  %-46s SF %6.2f / %s (%+.1f %%)" % (s["item"], s["SF"], s["need"], s["margin_pct"]))
print("볼트 묶음 %d줄: 안 됨 %d · FEA 확인 %d" % (len(B), sum(not r["ok"] for r in B), sum(r["needs_fea"] for r in B)))
for r in sorted(B, key=lambda r: min(r["new"]["tight"].values()))[:5]:
    print("  %-46s 조임 최소 %5.2f(전 %5.2f) 운전 최소 %6.2f / %s" % (r["key"][:46], min(r["new"]["tight"].values()), min(r["old"]["tight"].values()), min(r["new"]["op"].values()), r["need"]))
print("처짐 L바 mm:", out["FLAP_BAR_L1·L2·L3"]["defl_mm"])
print("-> fea/results/detail_DP-2_handcalc.json")
