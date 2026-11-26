# RX-DC-C1 해석부 3회차(수정 1회차 뒤) 손계산 — P_RXDC03_RISER_BRKT_판금 v2.30.5(둘째 꺾음 날 + 앞 누름 볼트 M4)
# python -B mech_RX-DC-C1_fea3_handcalc.py <받침 STEP> <블록 STEP> <결과 json>
# 형상: 두 STEP의 꼭짓점·원에서 직접 읽음(옛 케이스 좌표 안 씀). FEA 못 함 — 환경 없음(D-16).
# 하중(fea/models.json, D-232·D-38 임시): 운전 케이블 되돌림 5 N x 2줄, 오조작 손 당김 50 N, 선반 Z 487.
# 판정(요구서 6-1 = M-09 기본): 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형(동작). 과제 완료 판정: 오조작 뿌리 SF >= 1.2, 운전 SF >= 3.
# 모델은 2회차(fea2)와 같다: N1 끝이 자유인 외팔보(비대칭 굽힘 식 — ㄷ 단면은 Ixy 0), N2 뿌리 받침을 실제 조립대로 방향별.
#   2회차와 달라진 것은 조립(앞 누름 볼트가 생김)과 식 한 곳(ㄷ 단면 전단 중심 b: 2회차 고침안 6 -> STEP 치수 9).
import json, math, re, sys, collections

def read_step(p):
    t = open(p, encoding='utf-8', errors='ignore').read()
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
    circ = set()
    for k, v in ents.items():
        m = re.match(r"CIRCLE\('[^']*',#(\d+),([-0-9.eE+]+)\)", v)
        if m:
            ax = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+)", ents.get(m.group(1), ''))
            if ax and ax.group(1) in pts:
                circ.add((pts[ax.group(1)], round(float(m.group(2)), 3)))
    return verts, circ, t.count('MANIFOLD_SOLID_BREP'), t.count('CLOSED_SHELL')

step, blk, outp = sys.argv[1], sys.argv[2], sys.argv[3]
verts, circ, nsolid, nshell = read_step(step)
bverts, bcirc, bsolid, bshell = read_step(blk)
byz = collections.defaultdict(set)
for a in verts:
    byz[a[2]].add((a[0], a[1]))
z250 = byz[250.0]; z253 = byz[253.0]; z445 = sorted(byz[445.0]); z484 = sorted(byz[484.0])
holes = sorted({(c[0][0], c[0][1], c[1]) for c in circ if c[0][2] in (250.0, 253.0)})
xs = [a[0] for a in verts]; ys = [a[1] for a in verts]; zs = [a[2] for a in verts]
fold_x = sorted({p[0] for p in z445}); fold_y = sorted({p[1] for p in z445})
assert len(fold_x) == 4 and len(fold_y) == 2, (fold_x, fold_y)
F1 = (fold_x[0], fold_x[1], fold_y[0], fold_y[1]); F2 = (fold_x[2], fold_x[3], fold_y[0], fold_y[1])
web_pts = [p for p in z484 if p[1] in (82.0, 85.0) and -290 < p[0] < -270]
WEB = (min(p[0] for p in web_pts), max(p[0] for p in web_pts), min(p[1] for p in web_pts), max(p[1] for p in web_pts))
outer_bottom = [(F1[0], F1[2]), (F1[0], F1[3]), (F2[1], F2[2]), (F2[1], F2[3])]      # 두 날 바깥 밑 모서리
inner_bottom = [(F1[1], F1[2]), (F1[1], F1[3]), (F2[0], F2[2]), (F2[0], F2[3])]
geo = {"verts": len(verts), "solids": nsolid, "closed_shells": nshell,
       "bbox": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
       "z250_outline": sorted(p for p in z250 if p[0] == int(p[0]) or p[1] in (74.5, 83.0, 97.0)),
       "holes_base(x,y,r)": holes, "web_rect": WEB, "fold1_rect": F1, "fold2_rect": F2,
       "flange_bottom_at_z250": all(p in z250 for p in [(-288.0, 74.5), (-273.0, 74.5), (-288.0, 83.0)]),
       "fold_outer_bottom_edges_gone_at_z253": all(p not in z253 for p in outer_bottom),
       "fold_inner_bottom_at_z253": all(p in z253 for p in inner_bottom)}
geo["one_body_root"] = bool(geo["flange_bottom_at_z250"] and geo["fold_outer_bottom_edges_gone_at_z253"] and geo["fold_inner_bottom_at_z253"] and nsolid == 1 and nshell == 1)
m5 = sorted({(h[0], h[1]) for h in holes if abs(h[2]-2.75) < 0.01}); m4 = [(h[0], h[1]) for h in holes if abs(h[2]-2.25) < 0.01]
assert len(m5) == 2 and len(m4) == 1, holes
XB, YB = m4[0]
# 블록: 새 M4 탭(밑구멍 r 1.65)과 둘레 구멍
near = sorted({(c[0], c[1]) for c in bcirc if math.hypot(c[0][0]-XB, c[0][1]-YB) < 16 and 230 < c[0][2] < 255})
tapz = sorted(c[0][2] for c in near if abs(c[1]-1.65) < 0.01 and (c[0][0], c[0][1]) == (XB, YB))
t2 = sorted({(c[0][0], c[0][1]) for c in near if abs(c[1]-2.1) < 0.01 and c[0][2] < 247 and c[0][1] < 80})
geo["block"] = {"solids": bsolid, "m4_tap_drill_r": 1.65, "m4_tap_z": tapz, "T2_taps_from_below(x,y)": t2,
                "drill_wall_to_T2_2": round(min(math.hypot(a[0]-XB, a[1]-YB) for a in t2) - 1.65 - 2.1, 2),
                "thread_wall_to_T2_2": round(min(math.hypot(a[0]-XB, a[1]-YB) for a in t2) - 2.0 - 2.5, 2)}
TAP_DEPTH = tapz[-1] - tapz[0]

E = 193000.0; G = 74000.0; NU = 0.29; SY = 205.0; T = 3.0
ZP, Z0, ZF, ZTOP = 251.5, 253.0, 445.0, 487.0
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
    return dict(A=A, cx=cx, cy=cy, Ix=Ix, Iy=Iy, Ixy=Ixy, J=J, D=Ix*Iy-Ixy**2, corners=corners)

def unsym(s, m1, m2):
    b = (m1*s["Iy"] - m2*s["Ixy"])/s["D"]; a = (m2*s["Ix"] - m1*s["Ixy"])/s["D"]
    return max(((abs(a*(x-s["cx"]) + b*(y-s["cy"])), (x, y)) for x, y in s["corners"]))

def rnd(d, n=2):
    return {k: (round(v, n) if isinstance(v, float) else v) for k, v in d.items()}

def judge(sf, crit):
    return "동작(영구 변형)" if sf < 1.2 else ("디테일(기준 미달)" if sf < crit else "합격")

sC = sec([WEB, F1, F2]); sW = sec([WEB])
res = {"geometry": geo, "section_channel_root": rnd(sC), "cases": []}
tie_far = (-300.0, 74.0)
yw = (WEB[2]+WEB[3])/2; xw = (WEB[0]+WEB[1])/2
b_f = yw - F1[2]; h_f = (F2[0]+F2[1])/2 - (F1[0]+F1[1])/2          # ㄷ 단면 가운데선 치수: 날 길이 9, 날 사이 12
e_sc = 3.0*b_f**2/(h_f + 6.0*b_f)                                 # 전단 중심: 웨브 가운데선 뒤(+Y)
res["shear_center"] = dict(b=b_f, h=h_f, e=round(e_sc, 2), XY=(xw, round(yw+e_sc, 2)), note="2회차 고침안 계산은 b 6으로 e 2.25 — 바로잡음(τ 차이 1 MPa 안)")
loads = [("운전 5 N x 2줄", 10.0, 3.0), ("오조작 50 N", 50.0, 2.0)]
for ln, F, crit in loads:
    for d in ("Y", "X"):
        m1, m2 = (F*L, 0.0) if d == "Y" else (0.0, F*L)
        sig, at = unsym(sC, m1, m2)
        arm = abs(tie_far[0]-xw) if d == "Y" else abs(tie_far[1]-(yw+e_sc))
        tau = F*arm*T/sC["J"]; vm = math.hypot(sig, math.sqrt(3)*tau)
        k1 = (L**3 - Lw**3)/3.0; k2 = Lw**3/3.0
        defl = F/E*(k1/sC["Ix"] + k2/sW["Ix"]) if d == "Y" else F/E*(k1/sC["Iy"] + k2/sW["Iy"])
        twist = F*arm*((ZF-Z0)/(G*sC["J"]) + Lw/(G*sW["J"]))
        res["cases"].append(dict(model="ㄷ 단면 뿌리 Z 253", load=ln, dir=("±Y" if d == "Y" else "±X"), sigma=round(sig, 1), at_XY=at, tau=round(tau, 1), vm=round(vm, 1),
                                 SF=round(SY/vm, 2), crit=crit, judge=judge(SY/vm, crit), tip_defl_mm=round(defl, 2), tie_defl_by_twist_mm=round(twist*arm, 2)))
worst = max(((unsym(sC, 50.0*L*math.cos(math.radians(a)), 50.0*L*math.sin(math.radians(a)))[0], a) for a in range(0, 180)))
res["worst_direction_50N"] = dict(angle_from_Y_deg=worst[1], sigma=round(worst[0], 1), SF=round(SY/worst[0], 2))
for ln, F, crit in loads:
    sig = F*Lw*1.5/sW["Ix"]
    res["cases"].append(dict(model="Z 445 웨브만 15x3(그대로)", load=ln, dir="±Y", sigma=round(sig, 1), vm=round(sig, 1), SF=round(SY/sig, 2), crit=crit, judge=judge(SY/sig, crit)))

# ---- N2: 뿌리 받침(실제 조립 경계 — 누르는 것은 CB5-12 x2 머리와 CB4-12 머리뿐, 블록 윗면은 밀기만) ----
RH4, RH5 = 3.5, 4.25
M50 = 50.0*(ZTOP-ZP); kM = 50.0*L/sC["Ix"]                       # 뿌리 응력 기울기 MPa/mm (오조작 50 N)
cy = sC["cy"]
# 꺾음 날 한 개의 당김 합력(+Y 당김): Y < cy 구간, 그 작용 Y
ft = kM*T*(cy-F1[2])**2/2.0; y_ft = F1[2] + (cy-F1[2])/3.0
comp = kM*((WEB[1]-WEB[0])*(WEB[3]-WEB[2])*(yw-cy) + 2*T*(F1[3]-cy)**2/2.0)
y_comp = (kM*(WEB[1]-WEB[0])*((WEB[3]-cy)**3-(WEB[2]-cy)**3)/3.0 + kM*2*T*(F1[3]-cy)**3/3.0)/comp + cy
sup = {"M4_hole_XY": (XB, YB), "M4_head_X": [XB-RH4, XB+RH4], "M4_head_Y": [YB-RH4, YB+RH4],
       "pocket_X": [F1[1], F2[0]], "pocket_Y": [F1[2], F1[3]],
       "head_gap_to_folds_mm": [round(XB-RH4-F1[1], 2), round(F2[0]-(XB+RH4), 2)], "head_gap_to_web_face_mm": round(F1[3]-(YB+RH4), 2),
       "M5_holes_XY": m5, "M5_head_front_edge_Y": m5[0][1]-RH5, "web_back_face_Y": WEB[3],
       "fold_tension_each_N(+Y,50N)": round(ft), "fold_tension_at_Y": round(y_ft, 2), "compression_resultant_N": round(comp), "compression_at_Y": round(y_comp, 2)}
# +Y 당김: 앞 누름 볼트 당김. 받침점(블록이 미는 곳) 가정 3가지
T_cons = M50/(yw-YB)                         # 받침점 = 웨브 가운데(보수, 2회차·모델링부와 같은 값)
T_sec = 50.0*L/(y_comp-YB)                   # 받침점 = 단면 압축 합력 자리
heel = max(p[1] for p in z250)
kr = M50/((heel-YB)**2 + 2*(heel-m5[0][1])**2)   # 밑판이 강체일 때(받침점 뒤 끝): 볼트 3개가 거리 비례
plusY = {"front_bolt_T_N": {"받침점 웨브 가운데 Y %.1f(보수)" % yw: round(T_cons), "받침점 단면 압축 합력 Y %.2f" % y_comp: round(T_sec),
                            "밑판 강체·받침점 뒤 끝 Y %.0f(가장 작음)" % heel: round(kr*(heel-YB))},
         "rear_bolt_each_N_if_rigid": round(kr*(heel-m5[0][1]))}
# 플랜지(주머니 판): 날 발 당김 -> 볼트 머리. 전단(머리 가장자리~날 안쪽 면 1 mm 띠)과 짧은 굽힘
Ash = (F1[3]-F1[2])*T
plusY["flange_shear"] = {"area_mm2_per_side": Ash, "tau_MPa(T/2 보수)": round(T_cons/2/Ash, 1), "SF(T/2 보수)": round(SY/math.sqrt(3)/(T_cons/2/Ash), 2),
                         "tau_MPa(날 당김)": round(ft/Ash, 1), "SF(날 당김)": round(SY/math.sqrt(3)/(ft/Ash), 2)}
dyb = y_ft - YB
gap_face = (XB-F1[1]) - math.sqrt(RH4**2 - dyb**2)        # 날 당김 합력 높이에서 머리 가장자리 ~ 날 안쪽 면
arm_mid = gap_face + T/2.0                                 # ~ 날 두께 가운데
Zf = (F1[3]-F1[2])*T**2/6.0; If = (F1[3]-F1[2])*T**3/12.0
Dpl = E*T**3/(12*(1-NU**2))
bend = {"gap_head_rim_to_fold_face_mm": round(gap_face, 2), "arm_to_fold_midplane_mm": round(arm_mid, 2), "span_over_thickness": round(arm_mid/T, 2),
        "Z_mm3": Zf, "plastic_moment_Nmm": round(1.5*Zf*SY)}
# 날 발 회전 구속: 날(같은 t3 판)이 웨브 모서리에 붙어 발이 도는 것을 막는 강성 k (어림: 판 강성 D x 폭 / 감쇠 길이 ~ 폭) — 낮게 0.7e6, 높게 1.9e6 N·mm/rad
variants = [("날 발 회전 자유(가장 불리)", 0.0), ("날 발 회전 일부 구속 k 0.7e6", 0.7e6), ("날 발 회전 일부 구속 k 1.9e6", 1.9e6), ("날 발 회전 막힘(안내 끝)", float("inf"))]
bend["cases"] = []
for nm, k in variants:
    r = 1.0 if k == float("inf") else (k*arm_mid/(E*If))/(1.0 + k*arm_mid/(E*If)) if k else 0.0
    Mroot = ft*arm_mid*(1.0 - r/2.0)
    s = Mroot/Zf
    bend["cases"].append(dict(model=nm, M_root_Nmm=round(Mroot), sigma_MPa=round(s, 1), SF_first_yield=round(SY/s, 2), SF_plastic_hinge=round(1.5*SY/s, 2)))
s_rigid = ft*gap_face/2.0/Zf
bend["cases"].append(dict(model="날 발 이음이 굳고 팔을 날 안쪽 면까지로(가장 후함)", M_root_Nmm=round(ft*gap_face/2.0), sigma_MPa=round(s_rigid, 1), SF_first_yield=round(SY/s_rigid, 2), SF_plastic_hinge=round(1.5*SY/s_rigid, 2)))
bend["run_10N_first_yield_SF"] = [round(c["SF_first_yield"]*5, 2) for c in bend["cases"]]
bend["note"] = "길이/두께 약 1의 짧은 판 — 보 식은 어림. 첫 항복 SF가 기준 1.2를 사이에 두고 갈린다(0.9~1.8). 고체 FEA로만 가를 수 있다(D-16)"
plusY["flange_bending_head_to_fold"] = bend
Ab = math.pi/4*((2*RH4)**2 - 4.5**2)
plusY["head_bearing"] = {"area_mm2": round(Ab, 1), "p_MPa": round(T_cons/Ab, 1), "SF": round(SY/(T_cons/Ab), 2)}
res["root_support"] = sup; res["plusY_50N"] = plusY
# -Y 당김: 날이 눌림(플랜지 -> 블록). 웨브 당김은 앞 M4 머리(뒤 가장자리 Y 81.75)와 뒤 M5 머리(앞 가장자리 Y 85.75) 사이 4 mm 판이 받음
t_web = comp; a1 = yw-(YB+RH4); a2 = (m5[0][1]-RH5)-yw; span = a1+a2
Mss = t_web*a1*a2/span
wstrip = WEB[1]-WEB[0]
minusY = {"web_tension_N": round(t_web), "strip_span_mm": span, "a_front": a1, "a_rear": a2,
          "strip_M_simply_supported_Nmm": round(Mss), "strip_sigma_MPa(폭 %.0f)" % wstrip: round(Mss/(wstrip*T*T/6), 1), "strip_SF": round(SY/(Mss/(wstrip*T*T/6)), 2),
          "strip_shear_MPa": round(t_web*max(a1, a2)/span/(wstrip*T), 1),
          "front_bolt_share_N(단순보)": round(t_web*a2/span), "rear_bolts_total_N(받침점 플랜지 앞 끝)": round(50.0*(ZTOP-250.0)/(m5[0][1]-F1[2])),
          "fold_foot_bearing_MPa": round(2*ft/(2*T*(F1[3]-F1[2])), 1)}
res["minusY_50N"] = minusY
# X 당김: 한쪽 날 당김·다른 쪽 눌림. 받침점 = 눌리는 날 가운데
Qx = T*(F1[3]-F1[2])*h_f/2 + (WEB[3]-WEB[2])*((WEB[1]-WEB[0])/2)**2/2
tx = 50.0*L*Qx/sC["Iy"]; piv = (F2[0]+F2[1])/2
dists = [piv-XB, piv-m5[0][0], piv-m5[1][0]]
kx = 50.0*(ZTOP-250.0)/sum(d*d for d in dists)
res["X_50N"] = {"half_section_tension_N": round(tx), "M4_only_N(지렛대 %.1f)" % dists[0]: round(50.0*(ZTOP-250.0)/dists[0]),
                "rigid_base_share_N[M4, M5(-288), M5(-278)]": [round(kx*d) for d in dists]}
res["M4_design_tension_N"] = round(T_cons)
res["tap"] = {"drill_depth_mm": TAP_DEPTH, "bolt_tip_Z": 253.0-12.0, "engagement_nominal_mm": 12.0-T, "engagement_over_d": (12.0-T)/4.0,
              "tip_to_drill_bottom_mm": (253.0-12.0)-tapz[0], "note": "밑구멍 깊이 10에 볼트 끝이 바닥 위 1 — 탭 불완전 나사(2~3산 = 1.4~2.1)를 빼면 유효 물림 약 7. 유효 물림 9를 쓰려면 밑구멍 12 이상(선반 t14) 또는 관통"}
res["mass"] = dict(volume_mm3_model=23710.44, density=7.93, mass_g=round(23710.44*7.93/1000, 1))
json.dump(res, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("geo one_body", geo["one_body_root"], "solids", nsolid, "holes", holes, "block tap z", tapz, "T2", t2, "wall", geo["block"]["thread_wall_to_T2_2"])
print("C: A %.1f Ix %.2f Iy %.1f Ixy %.2f cy %.3f J %.1f e %.2f" % (sC["A"], sC["Ix"], sC["Iy"], sC["Ixy"], sC["cy"], sC["J"], e_sc))
for c in res["cases"]:
    print(c["model"][:10], c["load"][:6], c["dir"], "VM", c["vm"], "SF", c["SF"], c["judge"], c.get("tip_defl_mm", ""), c.get("tie_defl_by_twist_mm", ""))
print("worst", res["worst_direction_50N"], "| fold T each %.0f @Y %.2f comp %.0f @Y %.2f" % (ft, y_ft, comp, y_comp))
print("+Y bolt T", plusY["front_bolt_T_N"], "rear", plusY["rear_bolt_each_N_if_rigid"], "shear", plusY["flange_shear"], "bearing", plusY["head_bearing"])
print("flange bend arm", bend["arm_to_fold_midplane_mm"], [(c["model"][:12], c["sigma_MPa"], c["SF_first_yield"], c["SF_plastic_hinge"]) for c in bend["cases"]])
print("-Y", minusY); print("X", res["X_50N"]); print("tap", res["tap"]["tip_to_drill_bottom_mm"], res["tap"]["drill_depth_mm"])
