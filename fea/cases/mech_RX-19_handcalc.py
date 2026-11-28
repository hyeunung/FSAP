# RX-19 해석부 손계산 (v2.29.0, 2026-11-24). FEA 못 함 — 환경 없음(D-16).
# 형상: mech_RX-19_model.md 2-1~2-5(그린 치수), STEP tools/out/mech_RX-19/stepout/*.step
# 하중: 실린더 CDQSYB20(D20, 로드 10) 머리 0.5 MPa 157.1 N, 로드 쪽 0.127 MPa 29.9 N(운전)·0.5 MPa 117.8 N(오조작, 레귤레이터 고장)
#       스톱 토크 운전 3,686 N·mm = 무게·스프링 2,339(N_free 30.5 × 76.69) + 공기 1,346(29.9 × 45)
#       오조작 = 0.5 MPa 당김 117.8 × 45 + (무게·스프링) × 3 g
#       스토퍼 CDQ2A25(D25, 로드 10) 0.5 MPa 밂 245.4 · 당김 206.2 N
# 판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), 과사양 = 필요치 3배 이상(note)
import json, math, os
A5052 = dict(sy=195.0, E=70000.0, G=26300.0)
S45C = dict(sy=343.0, E=205000.0)
P_RUN, P_MIS = 0.127, 0.5
A_HEAD20 = math.pi/4*20**2; A_ROD20 = A_HEAD20 - math.pi/4*10**2
F_LIFT = A_HEAD20*0.5; F_PULL_RUN = A_ROD20*P_RUN; F_PULL_MIS = A_ROD20*P_MIS
A_HEAD25 = math.pi/4*25**2; A_ROD25 = A_HEAD25 - math.pi/4*10**2
T_WS = 30.5*(75+1.69)                     # 무게·스프링(띄움 자세 N_free × 팔)
T_RUN = T_WS + F_PULL_RUN*45              # 3,686
T_MIS = 3*T_WS + F_PULL_MIS*45
ARM_STOP = 150-135                        # 처음 닿음 Z 150, 핀 Z 135
F_RUN = T_RUN/ARM_STOP; F_MIS = T_MIS/ARM_STOP
W = 46.75                                 # 매단 무게(설계안)
def rect_W(b, h): return b*h*h/6
def rect_I(b, h): return b*h**3/12
def tors_a(a, b): return (1/3 - 0.21*(b/a))   # 직사각 비틀림 계수(a ≥ b)
def sf(sig, sy): return round(sy/sig, 2) if sig > 0 else None
out = {"loads": {"F_lift_N": round(F_LIFT, 1), "F_pull_run_N": round(F_PULL_RUN, 1), "F_pull_mis_N": round(F_PULL_MIS, 1),
                 "T_stop_run_Nmm": round(T_RUN, 0), "T_stop_mis_Nmm": round(T_MIS, 0),
                 "F_stop_run_N": round(F_RUN, 1), "F_stop_mis_N": round(F_MIS, 1),
                 "stopper_push_N": round(A_HEAD25*0.5, 1), "stopper_pull_N": round(A_ROD25*0.5, 1)}}
# 1) 블록 스톱 받침 기둥 (X -268.5~-260 = 8.5, Y 5~29 = 24, Z 150~236), 하중 -Y, 작용 Z 155(머리 보 Z 150~160 가운데) -> L 81
bx, hy, L = 8.5, 24.0, 236-155
arm_t = 21 + 4.25                         # 머리 보 하중 가운데 X -239 ↔ 기둥 가운데 X -264.25
a, b = hy, bx; ka = tors_a(a, b); Jt = ka*a*b**3
def post(F):
    s = F*L/rect_W(bx, hy); T = F*arm_t; t = T/(ka*a*b*b); vm = math.hypot(s, math.sqrt(3)*t)
    d_b = F*L**3/(3*A5052["E"]*rect_I(bx, hy)); th = T*L/(A5052["G"]*Jt); d_t = th*arm_t
    return {"sigma": round(s, 1), "tau": round(t, 1), "vm": round(vm, 1), "SF": sf(vm, A5052["sy"]), "d_bend": round(d_b, 4), "d_tors": round(d_t, 4)}
# 머리 보 X -260~-228 (L 32, 하중 가운데 팔 21) · Y 17~29 (12) · Z 150~160 (10)
def head(F):
    s = F*21/rect_W(10, 12); d = F*21**3/(3*A5052["E"]*rect_I(10, 12))
    return {"sigma": round(s, 1), "SF": sf(s, A5052["sy"]), "d": round(d, 4)}
sup = {}
for k, F in (("run", F_RUN), ("mis", F_MIS)):
    p, h = post(F), head(F); tot = p["d_bend"] + p["d_tors"] + h["d"]
    sup[k] = {"F": round(F, 1), "post": p, "head": h, "defl_total_Y": round(tot, 3), "float_0.5_ok": tot < 0.5}
# 오조작 뜸 초과분: 받침 강성 vs 로드 강성(Ø12 외팔 22, E 205 GPa)
k_sup = F_RUN/sup["run"]["defl_total_Y"]; k_rod = 3*205000*(math.pi*12**4/64)/22**3
over = max(0.0, sup["mis"]["defl_total_Y"] - 0.5)
F_rod_side = over*k_sup*k_rod/(k_sup+k_rod) if over > 0 else 0.0
# 받침이 0.5에서 멈추지 않으면 그 뒤 하중은 로드·받침이 나눈다 -> 로드 몫 근사
F_rod_side = F_MIS - 0.5*k_sup if over > 0 else 0.0
F_rod_side = F_rod_side*k_rod/(k_rod+k_sup)
sup["k_support_N_mm"] = round(k_sup, 0); sup["k_rod_N_mm"] = round(k_rod, 0)
sup["mis_over_float_mm"] = round(over, 3); sup["mis_rod_side_N"] = round(F_rod_side, 0)
sup["mis_rod_bend_MPa"] = round(F_rod_side*22/(math.pi*12**3/32), 1)
out["block_stop_support"] = sup
# 2) 스톱 블록 P_RX08_STOP_BLOCK (X 18 · Y 36.4 · Z 16, M8 탭 축 Z 158): 텅 면 → 블록 → 머리 보, 압축(같은 Z 150~160)
net_z = (158 - 6.8/2) - 150                 # 탭 구멍 밑까지 순 높이
A_net = 18*net_z; A_bear_head = 18*10
blk = {}
for k, F in (("run", F_RUN), ("mis", F_MIS)):
    s = F/A_net; line = F/12.0               # 텅 폭 12에 선 닿음(1.515° 처음 닿음, Z 150 모서리)
    blk[k] = {"sigma_net": round(s, 1), "SF": sf(s, A5052["sy"]), "head_bearing": round(F/A_bear_head, 1),
              "edge_line_N_per_mm": round(line, 1), "edge_bed1mm_MPa": round(line/1.0, 1), "edge_bed1mm_SF": sf(line/1.0, A5052["sy"])}
out["stop_block"] = blk
# 3) 그네 텅 (X -246~-234 = 12 · Y 65~85 = 20, Z 116~160; 위 X 8 · Z 160~205)
tg = {}
tg["stop_run"] = {"sigma": round(F_RUN*(150-116)/rect_W(12, 20), 1)}
tg["stop_mis"] = {"sigma": round(F_MIS*(150-116)/rect_W(12, 20), 1)}
tg["lift_root116"] = {"sigma": round(F_LIFT*(180-116)/rect_W(12, 20), 1)}
tg["lift_root160"] = {"sigma": round(F_LIFT*(180-160)/rect_W(8, 20), 1)}
tg["slot_bearing_MPa"] = round(F_LIFT/(8*8), 2)
for v in tg.values():
    if isinstance(v, dict): v["SF"] = sf(v["sigma"], A5052["sy"])
out["swing_tongue"] = tg
# 4) 핀 반력(그네 힘 평형). 스톱 오조작: 스톱 +Y F_MIS(Z 150), 로드 -Y 117.8(Z 180), 무게 3W 아래
R = {"press_run": math.hypot(F_PULL_RUN, 51.6 - W), "lift": math.hypot(F_LIFT, W),
     "stop_run": math.hypot(F_RUN - F_PULL_RUN, W), "stop_mis": math.hypot(F_MIS - F_PULL_MIS, 3*W)}
out["pin_reaction_N"] = {k: round(v, 1) for k, v in R.items()}
Rmax_run = max(R["press_run"], R["lift"], R["stop_run"]); Rmis = R["stop_mis"]
# 러그 X -158~-136 (22) · Y 61~89 (28), Z 236 → 135 외팔 101, 하중 Y
Ly = 101; Iy = rect_I(22, 28)
lug = {}
for k, F in (("run", Rmax_run), ("mis", Rmis)):
    s = F*Ly/rect_W(22, 28); lug[k] = {"F": round(F, 1), "sigma": round(s, 2), "SF": sf(s, A5052["sy"]), "tip_d": round(F*Ly**3/(3*A5052["E"]*Iy), 4)}
out["block_lug"] = lug
# 핀 PSFJ12-80: 러그(가운데 X -147)에서 하중, 부시 가운데(X -170 · -122) 받침, 경간 48 → 3점 굽힘(보수)
Wp = math.pi*12**3/32; Ap = math.pi*36
pin = {}
for k, F in (("run", Rmax_run), ("mis", Rmis)):
    s = F*48/4/Wp; pin[k] = {"bend": round(s, 1), "SF_bend": sf(s, S45C["sy"]), "tau_double": round(F/(2*Ap), 2),
                             "bush_p_MPa": round(F/2/(12*10), 2), "lug_bear_MPa": round(F/(12*22), 2)}
out["pin"] = pin
# 뺨(그네, t12 · Y 59~91, 부시 구멍 Ø18): 한 장 몫 F/2, 뿌리 Z 116 팔 19, 구멍 둘레 순 인장
ck = {}
for k, F in (("run", Rmax_run), ("mis", Rmis)):
    s = F/2*19/rect_W(12, 32); nt = F/2/((32-18)*12)
    ck[k] = {"sigma_root": round(s, 1), "SF": sf(s, A5052["sy"]), "net_tension": round(nt, 2)}
out["swing_cheek"] = ck
# 앞 띠 목(X -132~-120 · Z 104~116 = 12 × 12, Y 31~45 L 14): 앞판에 매단 무게(바퀴·감속기·서보) → 윗판
W_front = 42.0; Mb = W_front*(45-1.38); Tt = W_front*(170-126)   # 무게중심 Y 1.38, X 약 -170(서보·감속기 쪽), 목 가운데 X -126
neck = {}
for k, g in (("run", 1.0), ("mis_3g", 3.0)):
    s = g*Mb/rect_W(12, 12); t = g*Tt/(0.208*12**3); vm = math.hypot(s, math.sqrt(3)*t)
    neck[k] = {"sigma": round(s, 1), "tau": round(t, 1), "vm": round(vm, 1), "SF": sf(vm, A5052["sy"])}
out["swing_neck"] = neck
# 5) 바퀴 접지점 처짐 합(누름 끝 N 51.6 + 옆힘 16 N = μ0.4 × 40)
Ix = rect_I(28, 22)
F_y = R["press_run"]
d_lug_Z = (F_y*Ly**2/(2*A5052["E"]*Iy))*75                          # 러그 기울기 × Y 팔 75
Fs, Ms = 16.0, 16.0*125
d_lug_X = (Fs*Ly**3/(3*A5052["E"]*Ix) + Ms*Ly**2/(2*A5052["E"]*Ix)) + (Fs*Ly**2/(2*A5052["E"]*Ix) + Ms*Ly/(A5052["E"]*Ix))*125
Jn = 0.141*12**4; Ineck = rect_I(12, 12)
M_n = 51.6*45; T_n = 51.6*23                                          # 바퀴 X -103 ↔ 목 X -126
th_b = M_n*14/(A5052["E"]*Ineck); th_t = T_n*14/(A5052["G"]*Jn)
d_neck_Z = th_b*45 + th_t*23; d_neck_X = th_t*100 + 16*100*14/(A5052["G"]*Jn)*100
d_cheek = 0.002
tot_Z = d_lug_Z + d_neck_Z; tot_X = d_lug_X + d_neck_X + d_cheek
out["wheel_contact_defl"] = {"lug_Z": round(d_lug_Z, 4), "neck_Z": round(d_neck_Z, 4), "sum_Z": round(tot_Z, 4),
                             "lug_X": round(d_lug_X, 4), "neck_X": round(d_neck_X, 4), "cheek_X": d_cheek, "sum_X": round(tot_X, 4),
                             "sum_abs": round(tot_Z + tot_X, 3), "limit": 0.5, "ok": tot_Z + tot_X < 0.5}
# 과사양 note(M-09: SF ≥ 필요치 3배)
notes = []
if lug["run"]["SF"] >= 9: notes.append("러그 운전 SF %.0f ≥ 9: 강도로는 과사양, 폭은 바퀴 접지 강성·핀 구멍 자리로 정함" % lug["run"]["SF"])
if blk["run"]["SF"] >= 9: notes.append("스톱 블록 운전 SF %.0f: 크기는 M8 탭·조인트 자리로 정함" % blk["run"]["SF"])
if pin["run"]["SF_bend"] >= 9: notes.append("핀 Ø12 운전 SF %.0f: 부시 MPFZ12 구멍으로 정함" % pin["run"]["SF_bend"])
out["overspec_notes"] = notes
here = os.path.dirname(os.path.abspath(__file__))
dst = os.path.join(here, "..", "results", "mech_RX-19_handcalc.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("loads", "pin_reaction_N")}, ensure_ascii=False))
for k in ("block_stop_support", "stop_block", "swing_tongue", "block_lug", "pin", "swing_cheek", "swing_neck", "wheel_contact_defl"):
    print(k, json.dumps(out[k], ensure_ascii=False))
