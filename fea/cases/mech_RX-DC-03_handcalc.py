# RX-DC-03 해석부 손계산 (개념 W, v2.29.3, 2026-11-24). FEA 못 함 — 환경 없음(D-16).
# 형상: mech_RX-DC-03_model.md 2절(그린 치수), STEP tools/out/mech_RX-DC-03/stepout/*.step(최대 좌표 일치 확인)
# 재질: SUS304 t3 판금(항복 205, E 193 GPa, G 74 GPa). 볼트 CB5-12(12.9).
# 하중(임시값, 근거 없음 — 실물 케이블 굽힘 강성·납품처 기준 D-38 전):
#   운전: 케이블 굽힘 되돌림 힘 1줄 5 N(모델링부 값) x 2줄 = 10 N + 받는 무게(커넥터·리드·케이블 몫) x 3 g
#   오조작: 케이블 1줄 손 당김 50 N(PNEU-01 해석부와 같은 임시값), 가장 불리한 방향(판 두께 방향)
# 판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), 영구 변형 SF < 1.2 = 동작
import json, math, os, sys
sys.path.insert(0, "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools")
import handcalc as hc
SUS = dict(sy=205.0, E=193000.0, G=74000.0)
g = 9.81
F_CAB = 5.0; N_CAB = 2; F_MIS = 50.0
def W_(b, t): return b*t*t/6
def I_(b, t): return b*t**3/12
def sf(s): return round(SUS["sy"]/s, 2) if s > 0 else None
def cant(F, L, b, t):
    s = F*L/W_(b, t); d = F*L**3/(3*SUS["E"]*I_(b, t))
    return {"F": round(F, 2), "L": L, "sigma": round(s, 1), "SF": sf(s), "defl": round(d, 3)}
def freq(L, b, t, m_tip, m_beam):
    k = 3*SUS["E"]*I_(b, t)/L**3*1000.0          # N/m
    m = m_tip + 0.236*m_beam
    return round(math.sqrt(k/m)/(2*math.pi), 1)
out = {"assume": {"cable_return_N_each": F_CAB, "cables": N_CAB, "mis_hand_pull_N": F_MIS, "g_factor": 3}}
# 1) 그네 리드 받침 LEAD_GUIDE: 팔 X -296.6~-246(뿌리 탭 X -246, 그네에 Ø5.5 x2), 폭 14(Y 74~88), t3(Z 141~144) 외팔 47.6
m_lg = 0.0871 + 0.05*2 + 0.02          # 판 + 커넥터 쌍 2(임시 각 50 g) + 리드 몫
run = 0.1*g*3 + N_CAB*F_CAB            # 무게 3 g + 케이블 2줄 되돌림 힘(가장 불리하게 같은 쪽)
lg = {"arm_run": cant(run, 47.6, 14, 3), "arm_mis": cant(F_MIS, 47.6, 14, 3)}
# 세운 판(Y 52~96 폭 44, Z 86~144 높이 58)이 팔에서 매달림: 케이블 옆 당김 -> 세운 판 굽힘 + 팔 비틀림
T = F_MIS*58; a, b = 14.0, 3.0; ka = 1/3 - 0.21*(b/a)*(1 - b**4/(12*a**4))
tau = T/(ka*a*b*b); th = T*47.6/(SUS["G"]*ka*a*b**3)
lg["plate_mis"] = cant(F_MIS, 58, 44, 3)
sY = F_MIS*47.6/W_(3, 14)                 # 같은 Y 당김의 팔 굽힘(폭 14가 굽힘 높이, 강한 쪽)
lg["arm_twist_mis"] = {"T_Nmm": T, "tau": round(tau, 1), "sigma_Y": round(sY, 1), "vm": round(math.hypot(sY, math.sqrt(3)*tau), 1),
                       "SF": sf(math.hypot(sY, math.sqrt(3)*tau)), "tip_move_mm": round(th*58, 2)}
lg["f1_Hz"] = freq(47.6, 14, 3, m_lg - 0.0871, 0.0871)
lg["swing_extra_torque_Nmm"] = round(m_lg*g*3*7, 1)      # 무게 중심 Y 약 82 - 핀 Y 75 = 7, 3 g (RX-19 무게·스프링 토크 2,339과 비교)
out["P_RXDC03_LEAD_GUIDE"] = lg
# 2) T2 안내 립: X -310.6~-307.6(t3), 폭 18(Y 66~84), 판 밑 플랜지 Z 233~236에서 매달림 21(Z 212~233)
out["P_RXDC03_T2_GUIDE"] = {"run": cant(N_CAB*F_CAB + 0.02*g*3, 21, 18, 3), "mis": cant(F_MIS, 21, 18, 3)}
# 3) 세움 받침 RISER_BRKT: 세운 판 X -296.6~-293.6(t3) · Y 83~97(14) · Z 253~392, 판 위 플랜지 Z 250~253 볼트 2
#    하중 두께 방향(X)이 약한 쪽. 운전 = 위 팔 Z 390(팔 137), 오조작 = 케이블 타이 Z 344(팔 91)와 위 팔 Z 390(137) 둘 다
r = {"run_top": cant(N_CAB*F_CAB + 0.03*g*3, 137, 14, 3),
     "mis_tie": cant(F_MIS, 91, 14, 3), "mis_top": cant(F_MIS, 137, 14, 3),
     "run_Y_dir": cant(N_CAB*F_CAB, 137, 3, 14)}
r["f1_Hz_tip20g"] = freq(139, 14, 3, 0.02, 0.074)
r["f1_Hz_tip50g"] = freq(139, 14, 3, 0.05, 0.074)
r["head_excite_Hz"] = {"2000rpm": 33.3, "3000rpm": 50.0}
# 고침안: 세운 판 -X 쪽에 꺾음 날 X -308.6~-296.6 · Y 83~86 · Z 253~392(지금 타이 판 X -318.6~-295 · Y 83~86과 한 판)
A1, x1, I1 = 3*14, -295.1, 14*3**3/12
A2, x2, I2 = 12*3, -302.6, 3*12**3/12
xc = (A1*x1 + A2*x2)/(A1 + A2)
I_L = I1 + A1*(x1 - xc)**2 + I2 + A2*(x2 - xc)**2
c = max(abs(-308.6 - xc), abs(-293.6 - xc)); W_L = I_L/c
sL = F_MIS*137/W_L
kL = 3*SUS["E"]*I_L/137**3*1000
r["fix_L_flange"] = {"I": round(I_L, 0), "W": round(W_L, 1), "mis_top_sigma": round(sL, 1), "SF": sf(sL),
                     "defl_mis_top": round(F_MIS*137**3/(3*SUS["E"]*I_L), 3),
                     "f1_Hz_tip50g": round(math.sqrt(kL/(0.05 + 0.236*0.074*1.5))/(2*math.pi), 1), "mass_add_g": round(12*3*139*7.93e-3, 1)}
# 플랜지 볼트(X -288 고친 뒤 · -278, Y 90), 지렛대 받침점: +X 당김 -> 플랜지 끝 X -273, -X 당김 -> 판 바깥 면 X -296.6
M = F_MIS*137
dp = [abs(-288 - (-273)), abs(-278 - (-273))]; dn = [abs(-288 - (-296.6)), abs(-278 - (-296.6))]
Fb = max(M*max(dp)/sum(d*d for d in dp), M*max(dn)/sum(d*d for d in dn))
r["flange_bolt_mis_N"] = round(Fb, 0)
r["flange_bolt_calc"] = hc.calc(5, 9, Fb, 0.0, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
out["P_RXDC03_RISER_BRKT"] = r
# 4) 보 앞 받침 BEAM_CLAMP: 선반 Y 68~120(t3 Z 507.5~510.5, 폭 14), 벽 안쪽 면 Y 117에서 외팔 49, 벽 Ø5.5 Z 522·534로 보 앞면
bc = {"run": cant(N_CAB*F_CAB + 0.07*g*3, 49, 14, 3), "mis": cant(F_MIS, 49, 14, 3)}
Mb = F_MIS*49; d = [522 - 507.5, 534 - 507.5]
bc["wall_bolt_mis_N"] = round(Mb*max(d)/sum(x*x for x in d), 0)
bc["wall_bolt_calc"] = hc.calc(5, 8, bc["wall_bolt_mis_N"], 0.0, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)
bc["rest_gap_mm"] = 0.25
out["P_RXDC03_BEAM_CLAMP"] = bc
# 5) 판 위 경간 굽힘(완료 판정 확인, 모델링부 식 재현): 경간 115, 처짐 h에서 반 사인 R = L^2/(pi^2 h/2)... 모델링부 값 132.6 · 66.3 을 기록
out["route_R"] = {"note": "케이블 경로 R은 기하 값 — 검도 재계산(L4 69.5, 판 위 132.6 반 사인 · 66.3 양끝 고정) 그대로, 해석부는 다시 셈하지 않음"}
os.makedirs("C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results", exist_ok=True)
p = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-DC-03_handcalc.json"
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def s(*a): print(*a)
s("LG arm run/mis", (lg["arm_run"]["SF"], lg["arm_mis"]["SF"]), "twist", lg["arm_twist_mis"], "f1", lg["f1_Hz"], "swingT", lg["swing_extra_torque_Nmm"])
s("LG plate mis", lg["plate_mis"])
s("T2", out["P_RXDC03_T2_GUIDE"])
s("RISER", {k: r[k] for k in ("run_top", "mis_tie", "mis_top", "run_Y_dir", "f1_Hz_tip20g", "f1_Hz_tip50g", "fix_L_flange", "flange_bolt_mis_N")})
s("RISER bolt", r["flange_bolt_calc"])
s("BC", bc["run"], bc["mis"], bc["wall_bolt_mis_N"], bc["wall_bolt_calc"])
