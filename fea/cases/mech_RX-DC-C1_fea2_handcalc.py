# RX-DC-C1 해석부 2회차 손계산 — P_RXDC03_RISER_BRKT_판금(v2.30.4, 꺾음 날 밑 플랜지 덧붙임 뒤)
# python -B mech_RX-DC-C1_fea2_handcalc.py <임시 STEP> <결과 json>
# 형상: STEP 꼭짓점·원에서 직접 읽음(옛 케이스 좌표 안 씀). FEA 못 함 — 환경 없음(D-16).
# 하중(fea/models.json, D-232·D-38 임시): 운전 케이블 되돌림 5 N x 2줄, 오조작 손 당김 50 N, 선반 Z 487.
# 판정(요구서 6-1 = M-09 기본): 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형(동작). 과제 완료 판정: 오조작 뿌리 SF >= 1.2, 운전 SF >= 3.
# 모델(1회차와 달라진 것 — 보고서 맨 위에 이유):
#   옛 모델 O: L 단면 M*c/Ix (X축 굽힘만, 옆 처짐 막힘 가정, 당김 방향 구분 없음)
#   새 모델 N1: 끝이 자유인 외팔보의 비대칭 굽힘(Ixy != 0) — RX-DC-03 fix2 손계산이 쓰던 식
#   새 모델 N2: 뿌리 받침을 실제 조립대로(볼트 2개는 Y 90 뿐, 블록 윗면은 누르기만) -> Y 당김 방향별
import json, math, re, sys, collections
step, outp = sys.argv[1], sys.argv[2]
t = open(step, encoding='utf-8', errors='ignore').read()
ents = dict(re.findall(r'#(\d+)\s*=\s*([^;]*);', t))
pts = {}
for k, v in ents.items():
    m = re.match(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", v)
    if m:
        pts[k] = tuple(round(float(x), 3) for x in m.group(1).split(','))
verts = set()
for k, v in ents.items():
    m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", v)
    if m:
        verts.add(pts[m.group(1)])
byz = collections.defaultdict(set)
for a in verts:
    byz[a[2]].add((a[0], a[1]))
# 원(볼트 구멍·타이 구멍): CIRCLE -> AXIS2_PLACEMENT_3D -> 중심
circ = set()
for k, v in ents.items():
    m = re.match(r"CIRCLE\('[^']*',#(\d+),([-0-9.eE+]+)\)", v)
    if m:
        ax = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+)", ents.get(m.group(1), ''))
        if ax and ax.group(1) in pts:
            circ.add((pts[ax.group(1)], round(float(m.group(2)), 3)))
z250 = sorted(byz[250.0]); z253 = sorted(byz[253.0]); z445 = sorted(byz[445.0]); z484 = sorted(byz[484.0])
holes = sorted({(c[0][0], c[0][1], c[1]) for c in circ if c[0][2] in (250.0, 253.0)})
xs = [a[0] for a in verts]; ys = [a[1] for a in verts]; zs = [a[2] for a in verts]
geo = {
    "verts": len(verts), "bbox": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
    "z250_outline": z250, "z253": z253, "z445_fold_top": z445,
    "base_bolt_holes(x,y,r)": holes,
    # 완료 판정 1: 꺾음 날 밑면이 밑판과 한 몸 = Z 250 밑면 외곽이 Y 74.5까지 나오고, Z 253에 날 밑면 자유 모서리 꼭짓점이 없다
    "flange_bottom_at_z250": ((-288.0, 74.5) in z250) and ((-273.0, 74.5) in z250) and ((-288.0, 83.0) in z250),
    "fold_bottom_free_edge_gone": ((-288.0, 74.5) not in z253) and ((-288.0, 82.0) not in z253),
}
geo["one_body_root"] = bool(geo["flange_bottom_at_z250"] and geo["fold_bottom_free_edge_gone"])
# 단면 치수는 STEP 꼭짓점에서
fold_x = sorted({p[0] for p in z445}); fold_y = sorted({p[1] for p in z445})
web_pts = [p for p in z484 if p[1] in (82.0, 85.0) and -290 < p[0] < -270]
web_x = sorted({p[0] for p in web_pts}); web_y = sorted({p[1] for p in web_pts})
WEB = (web_x[0], web_x[-1], web_y[0], web_y[-1]); FLG = (fold_x[0], fold_x[-1], fold_y[0], fold_y[-1])
base_x = (min(p[0] for p in z250), max(p[0] for p in z250)); base_ymax = max(p[1] for p in z250)
geo["web_rect"] = WEB; geo["fold_rect"] = FLG; geo["base_width_X"] = round(base_x[1]-base_x[0], 2)

E = 193000.0; G = 74000.0; SY = 205.0; T_SH = 3.0
ZP, Z0, ZF, ZTOP = 251.5, 253.0, 445.0, 487.0     # 밑판 두께 가운데, 뿌리, 꺾음 날 끝, 하중점
L = ZTOP - Z0; Lw = ZTOP - ZF

def sec(rects):
    A = sum((x1-x0)*(y1-y0) for x0, x1, y0, y1 in rects)
    cx = sum((x1-x0)*(y1-y0)*(x0+x1)/2 for x0, x1, y0, y1 in rects)/A
    cy = sum((x1-x0)*(y1-y0)*(y0+y1)/2 for x0, x1, y0, y1 in rects)/A
    Ix = sum((x1-x0)*(y1-y0)**3/12 + (x1-x0)*(y1-y0)*((y0+y1)/2-cy)**2 for x0, x1, y0, y1 in rects)
    Iy = sum((y1-y0)*(x1-x0)**3/12 + (x1-x0)*(y1-y0)*((x0+x1)/2-cx)**2 for x0, x1, y0, y1 in rects)
    Ixy = sum((x1-x0)*(y1-y0)*((x0+x1)/2-cx)*((y0+y1)/2-cy) for x0, x1, y0, y1 in rects)
    J = sum(max(x1-x0, y1-y0)*min(x1-x0, y1-y0)**3/3 for x0, x1, y0, y1 in rects)
    corners = sorted({(x, y) for x0, x1, y0, y1 in rects for x in (x0, x1) for y in (y0, y1)})
    D = Ix*Iy - Ixy**2
    r = math.hypot((Ix-Iy)/2, Ixy)
    return dict(A=A, cx=cx, cy=cy, Ix=Ix, Iy=Iy, Ixy=Ixy, J=J, D=D, Imin=(Ix+Iy)/2-r, Imax=(Ix+Iy)/2+r, corners=corners,
                cym=max(abs(y-cy) for _, y in corners), cxm=max(abs(x-cx) for x, _ in corners))

def unsym(s, m1, m2):
    """m1 = Y 하중 모멘트(∫σy dA), m2 = X 하중 모멘트(∫σx dA). 자유 끝 외팔보. 모서리별 σ 가운데 가장 큰 것."""
    b = (m1*s["Iy"] - m2*s["Ixy"])/s["D"]; a = (m2*s["Ix"] - m1*s["Ixy"])/s["D"]
    best = max(((abs(a*(x-s["cx"]) + b*(y-s["cy"])), (x, y)) for x, y in s["corners"]))
    return best

def rnd(d, n=2):
    return {k: (round(v, n) if isinstance(v, float) else v) for k, v in d.items()}

sL = sec([WEB, FLG]); sW = sec([WEB])
res = {"geometry": geo, "section_L_root": rnd(sL), "cases": []}
tie_far = (-300.0, 74.0)
sc = (FLG[0] + T_SH/2, WEB[2] + T_SH/2)            # L 단면 전단 중심 = 두 다리 가운데선이 만나는 곳
loads = [("운전 5 N x 2줄", 10.0, 3.0), ("오조작 50 N", 50.0, 2.0)]

def judge(sf, crit):
    return "동작(영구 변형)" if sf < 1.2 else ("디테일(기준 미달)" if sf < crit else "합격")

# ---- O: 옛 모델(1회차·모델링부와 같은 식) ----
for ln, F, crit in loads:
    for d in ("Y", "X"):
        I, c = (sL["Ix"], sL["cym"]) if d == "Y" else (sL["Iy"], sL["cxm"])
        sig = F*L*c/I
        arm = abs(tie_far[0]-(-280.5)) if d == "Y" else abs(tie_far[1]-83.5)
        tau = F*arm*T_SH/sL["J"]; vm = math.hypot(sig, math.sqrt(3)*tau)
        res["cases"].append(dict(model="O 옛 모델 M*c/I", load=ln, dir=d, sigma=round(sig, 1), tau=round(tau, 1), vm=round(vm, 1), SF=round(SY/vm, 2), crit=crit, judge=judge(SY/vm, crit)))

# ---- N1: 비대칭 굽힘(끝 자유) ----
for ln, F, crit in loads:
    for d in ("Y", "X"):
        m1, m2 = (F*L, 0.0) if d == "Y" else (0.0, F*L)
        sig, at = unsym(sL, m1, m2)
        arm = abs(tie_far[0]-sc[0]) if d == "Y" else abs(tie_far[1]-sc[1])
        tau = F*arm*T_SH/sL["J"]; vm = math.hypot(sig, math.sqrt(3)*tau)
        # 끝 처짐(뿌리~445 L 단면 비대칭, 445~487 웨브만)
        k1 = (L**3 - Lw**3)/3.0; k2 = Lw**3/3.0
        if d == "Y":
            dy = F/E*(k1*sL["Iy"]/sL["D"] + k2/sW["Ix"]); dx = F/E*k1*sL["Ixy"]/sL["D"]
        else:
            dx = F/E*(k1*sL["Ix"]/sL["D"] + k2/sW["Iy"]); dy = F/E*k1*sL["Ixy"]/sL["D"]
        res["cases"].append(dict(model="N1 비대칭 굽힘", load=ln, dir=d, sigma=round(sig, 1), at_XY=at, tau=round(tau, 1), vm=round(vm, 1), SF=round(SY/vm, 2), crit=crit,
                                 judge=judge(SY/vm, crit), tip_defl_along_mm=round(dy if d == "Y" else dx, 2), tip_defl_side_mm=round(dx if d == "Y" else dy, 2)))
# 가장 불리한 당김 각(정보)
worst = max(((unsym(sL, 50.0*L*math.cos(math.radians(a)), 50.0*L*math.sin(math.radians(a)))[0], a) for a in range(0, 180)))
res["worst_direction_50N"] = dict(angle_from_Y_deg=worst[1], sigma=round(worst[0], 1), SF=round(SY/worst[0], 2), Imin=round(sL["Imin"], 1), Imax=round(sL["Imax"], 1))

# ---- N2: 뿌리 받침(실제 조립 경계) ----
# 볼트 CB5-12 x2: 구멍 중심 Y (STEP 원) — 머리 Ø8.5. 블록 윗면 Z 250은 받침을 밀기만 한다(당기지 못함).
bolt_y = sorted({h[1] for h in holes if abs(h[2]-2.75) < 0.01}); bolt_x = sorted({h[0] for h in holes if abs(h[2]-2.75) < 0.01})
by = bolt_y[0]; head_front = by - 4.25
res["root_support"] = {"bolt_centers_X": bolt_x, "bolt_center_Y": by, "bolt_head_front_edge_Y": head_front, "web_back_face_Y": WEB[3], "base_heel_Y": base_ymax,
                       "front_flange_Y": [FLG[2], 83.0], "front_hold_down_bolt": "없음(STEP 원: 밑판 구멍은 Y %.1f 두 개뿐)" % by}
# +Y 당김: 꺾음 날 쪽(-Y)이 당겨진다. 앞에는 누르는 볼트가 없으므로 뿌리 모멘트 전부가 웨브 뒷면(Y 85)과 볼트 머리(Y 85.75~) 사이의 t3 판 띠를 굽힘으로 지나야 한다
#   (받침 자유물체: 띠 왼쪽에는 블록의 미는 힘뿐 -> 띠 모멘트 >= M). 띠 폭: 웨브 폭 15(아래) · 두 볼트 머리 걸침 18.5(가운데) · 밑판 전체 35.6(위)
head_span = (bolt_x[-1]+4.25) - (bolt_x[0]-4.25)
widths = [("웨브 폭", WEB[1]-WEB[0]), ("두 볼트 머리 걸침", head_span), ("밑판 전체 폭(가장 후함)", base_x[1]-base_x[0])]
res["plusY_root_plate"] = []
for ln, F, crit in loads:
    M = F*(ZTOP-ZP)
    for wn, b in widths:
        Zel = b*T_SH**2/6.0; sig = M/Zel
        res["plusY_root_plate"].append(dict(load=ln, width=wn, b=round(b, 2), M=round(M), sigma=round(sig, 1), SF_yield=round(SY/sig, 2), plastic_hinge_factor=round(1.5*SY/sig, 2),
                                            crit=crit, judge=judge(SY/sig, crit)))
res["plusY_allow_N_at_SF1.2"] = {wn: round(b*T_SH**2/6.0*SY/1.2/(ZTOP-ZP), 1) for wn, b in widths}
res["plusY_t_needed_sheet_only_SF1.2_mm"] = {wn: round(math.sqrt(50.0*(ZTOP-ZP)*1.2/SY*6.0/b), 2) for wn, b in widths}
# +Y 볼트: 받침점 뒤 끝 Y 97
M50 = 50.0*(ZTOP-250.0)
res["bolts_now"] = {"plusY_pivot_heel": dict(lever=base_ymax-by, total_N=round(M50/(base_ymax-by)), per_bolt_N=round(M50/(base_ymax-by)/2)),
                    "minusY_pivot_flange_front": dict(lever=by-FLG[2], total_N=round(M50/(by-FLG[2])), per_bolt_N=round(M50/(by-FLG[2])/2))}
# -Y 당김: 꺾음 날이 눌려 플랜지가 블록 윗면에 얹힘(L 단면이 뿌리까지 일함 -> N1 값). 웨브 당김 합력이 밑판 띠(웨브 가운데 Y 83.5 -> 볼트 머리 앞 끝)로 감
Ft = 50.0*L/sL["Ix"]*T_SH*((sL["cy"]-FLG[2])**2 - max(0.0, sL["cy"]-FLG[3])**2)/2.0     # 꺾음 날 합력(옛 모델 분포, 어림)
a_strip = head_front - (WEB[2]+WEB[3])/2.0
Zs = head_span*T_SH**2/6.0
res["minusY_root"] = dict(fold_resultant_N=round(Ft), bearing_fold_foot_MPa=round(Ft/((FLG[1]-FLG[0])*(FLG[3]-FLG[2])), 1),
                          strip_arm_mm=a_strip, strip_sigma_free_MPa=round(Ft*a_strip/Zs, 1), strip_SF_free=round(SY/(Ft*a_strip/Zs), 2),
                          strip_sigma_guided_MPa=round(Ft*a_strip/2/Zs, 1), strip_SF_guided=round(SY/(Ft*a_strip/2/Zs), 2),
                          note="띠 굽힘은 웨브 발 회전이 자유(위) ~ 막힘(아래) 사이. 정밀 값은 FEA 몫(D-16)")
# Z 445 웨브만(팔 42) — 1회차와 같음
for ln, F, crit in loads:
    sig = F*Lw*1.5/sW["Ix"]
    res["cases"].append(dict(model="Z 445 웨브만 15x3", load=ln, dir="Y", sigma=round(sig, 1), SF=round(SY/sig, 2), crit=crit, judge=judge(SY/sig, crit)))

# ---- 고침안 K: 둘째 꺾음 날(검도 2회차 시험 형상 X -276~-273 · Y 74.5~82 · Z 253~445) + 앞 누름 볼트 ----
FL2 = (WEB[1]-T_SH, WEB[1], FLG[2], FLG[3])
sC = sec([WEB, FLG, FL2])
fix = {"section_channel": rnd(sC), "cases": []}
e_sc = 3.0*6.0**2/(12.0 + 6.0*6.0)                  # ㄷ 단면 전단 중심: 웨브 가운데선 뒤 e = 3b^2/(h+6b), b 6 · h 12
for ln, F, crit in loads:
    for d in ("Y", "X"):
        m1, m2 = (F*L, 0.0) if d == "Y" else (0.0, F*L)
        sig, at = unsym(sC, m1, m2)
        arm = abs(tie_far[0]-(WEB[0]+WEB[1])/2) if d == "Y" else abs(tie_far[1]-((WEB[2]+WEB[3])/2+e_sc))
        tau = F*arm*T_SH/sC["J"]; vm = math.hypot(sig, math.sqrt(3)*tau)
        fix["cases"].append(dict(load=ln, dir=d, sigma=round(sig, 1), tau=round(tau, 1), vm=round(vm, 1), SF=round(SY/vm, 2), crit=crit, judge=judge(SY/vm, crit)))
# 앞 누름 볼트(두 꺾음 날 사이 플랜지 X -285~-276 · Y 74.5~82 가운데): +Y 당김의 당김 받침. 지렛대 = 볼트 Y ~ 웨브 가운데(눌리는 쪽, 보수)
yb = 78.25
T_front = 50.0*(ZTOP-ZP)/(((WEB[2]+WEB[3])/2) - yb)
fix["front_bolt"] = dict(pos_XY=((FLG[1]+FL2[0])/2, yb), pocket_X=[FLG[1], FL2[0]], pocket_Y=[FLG[2], FLG[3]], lever_mm=(WEB[2]+WEB[3])/2-yb,
                         tension_misuse_N=round(T_front), tension_run_N=round(T_front/5),
                         flange_shear_MPa=round(T_front/2/((FLG[3]-FLG[2])*T_SH), 1), flange_shear_SF=round(SY/math.sqrt(3)/(T_front/2/((FLG[3]-FLG[2])*T_SH)), 2),
                         tap_wall_to_T2_2_mm={"M4": round(math.hypot((FLG[1]+FL2[0])/2+286.0, yb-75.0)-2.5-2.0, 2), "M3": round(math.hypot((FLG[1]+FL2[0])/2+286.0, yb-75.0)-2.5-1.5, 2)})
res["fix_K"] = fix
res["mass"] = dict(volume_mm3_model=19438.15, density=7.93, mass_g=round(19438.15*7.93/1000, 1), added_mm3=15*8.5*3)
json.dump(res, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("geo one_body", geo["one_body_root"], "holes", holes, "web", WEB, "fold", FLG, "baseW", geo["base_width_X"])
print("L: Ix %.1f Iy %.1f Ixy %.1f Imin %.1f cy %.2f cx %.2f" % (sL["Ix"], sL["Iy"], sL["Ixy"], sL["Imin"], sL["cy"], sL["cx"]))
for c in res["cases"]:
    print(c["model"][:14], c["load"][:6], c["dir"], "VM", c.get("vm", c["sigma"]), "SF", c["SF"], c["judge"], c.get("at_XY", ""), c.get("tip_defl_along_mm", ""), c.get("tip_defl_side_mm", ""))
print("worst", res["worst_direction_50N"])
for c in res["plusY_root_plate"]:
    print("+Y", c["load"][:6], c["width"], c["b"], "σ", c["sigma"], "SF", c["SF_yield"], "plastic", c["plastic_hinge_factor"], c["judge"])
print("allow", res["plusY_allow_N_at_SF1.2"], "t", res["plusY_t_needed_sheet_only_SF1.2_mm"])
print("bolts", res["bolts_now"]); print("-Y", res["minusY_root"])
print("fixK", [(c["load"][:6], c["dir"], c["vm"], c["SF"]) for c in fix["cases"]], fix["front_bolt"])
