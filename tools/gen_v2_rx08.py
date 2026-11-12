# RX-08 U4 중간 높이 스토퍼 실린더 생성기 (v2.11.1 -> v2.12.0). 단계 파일을 tools/out/mech_RX-08/model/stage_*.json 으로 쓴다.
# 실행: python -B tools/gen_v2_rx08.py
# 좌표: 월드, REST(J_U4_PRESS 13.006, J_U4_X 0), 스토퍼 OFF(J_U4_STOP 0, 로드 전진 끝)로 그린다.
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-08', 'model')
STEP = os.path.join(os.path.dirname(ROOT), 'purchased-step').replace('\\', '/')
os.makedirs(OUT, exist_ok=True)
OUTP = OUT.replace('\\', '/')

def C(cmd, **p):
    return {"command": cmd, "params": p}

def box(name, x0, y0, z0, x1, y1, z1, op="new", targets=None):
    p = dict(corner=[x0, y0, z0], length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation=op)
    if op == "new": p["body_name"] = name
    if targets: p["targets"] = targets
    return C("solid.box", **p)

def cyl(r, h, base, axis, op, targets=None, name=None):
    p = dict(radius=r, height=h, base=base, axis=axis, operation=op)
    if targets: p["targets"] = targets
    if name: p["body_name"] = name
    return C("solid.cylinder", **p)

def flat(R, t):  # R rows 3x3, t -> 12 list
    return [R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2]]

# ---------- 0. 작은 구매품 설계(CLI): 원점 기준, 넣을 때 translate
I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
R_X_TO_Z = [[0, 0, -1], [0, 1, 0], [1, 0, 0]]     # 로컬 +x(나사 끝 쪽) -> 월드 +Z (머리 아래)
R_X_TO_NZ = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]    # 로컬 +x -> 월드 -Z (머리 위)
R_KQ_A = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]      # KQ2L06: 나사 로컬 -y -> 월드 -Y(포트 안), 출구 로컬 +x -> 월드 -X
minis = {
    "d_cb5x": [C("file.insert_step", path=STEP + "/CB5-16/CB5-16.stp", name="CB5-16", matrix=flat(I, [0, 0, 0])),
               C("body.rename", body="Cut-Extrude1", name="CB5-16_RX08_LIP")],
    "d_cb5z": [C("file.insert_step", path=STEP + "/CB5-16/CB5-16.stp", name="CB5-16", matrix=flat(R_X_TO_Z, [0, 0, 0])),
               C("body.rename", body="Cut-Extrude1", name="CB5-16_RX08_TOP")],
    "d_cb8": [C("file.insert_step", path=STEP + "/CB8-20/CB8-20.stp", name="CB8-20", matrix=flat(R_X_TO_NZ, [0, 0, 0])),
              C("body.rename", body="Cut-Extrude1", name="CB8-20_RX08")],
    "d_nut": [C("parts.insert", family="hex_nut", size="M8", point=[0, 0, 0], direction=[0, 0, 1], name="NUT"),
              C("body.rename", body="Body1", name="STEP대기_NUT-M8_RX08")],
    "d_kqa": [C("file.insert_step", path=STEP + "/KQ2L06-M5A/KQ2L06-M5A.stp", name="KQ", matrix=flat(R_KQ_A, [0, 0, 0])),
              C("body.rename", body="KQ2L06-M5A", name="KQ2L06-M5A_RX08_HEAD")],
    "d_kqb": [C("file.insert_step", path=STEP + "/KQ2L06-M5A/KQ2L06-M5A.stp", name="KQ", matrix=flat(I, [0, 0, 0])),
              C("body.rename", body="KQ2L06-M5A", name="KQ2L06-M5A_RX08_ROD")],
}
for k, v in minis.items():
    json.dump(v + [C("inspect.measure", summary=True)], open(os.path.join(OUT, 'mini_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

stages = {}
# ---------- 1. 컴포넌트 + 구매품 넣기
LIP = [(71, 79), (97, 79), (71, 105), (97, 105)]
TOPB = [(-146, 69), (-146, 79)]          # 지시 (Y 98)은 다리(Y 86~104) 안이라 Y 79로 옮김(보고서)
s1 = [C("component.create", name="U4_STOP", parent="U4_WHEEL_N", activate=False),
      C("component.create", name="STEP대기_CDQ2A25-20DMZ", parent="U4_WHEEL_N", activate=False)]
for i, (y, z) in enumerate(LIP):
    p = dict(path=OUTP + "/d_cb5x.sc", name="CB5-16_RX08_LIP", parent="U4_WHEEL_N", translate=[-268, y, z])
    if i: p["reuse"] = True
    s1.append(C("component.insert_design", **p))
for i, (x, y) in enumerate(TOPB):
    p = dict(path=OUTP + "/d_cb5z.sc", name="CB5-16_RX08_TOP", parent="U4_WHEEL_N", translate=[x, y, 234])
    if i: p["reuse"] = True
    s1.append(C("component.insert_design", **p))
s1 += [C("component.insert_design", path=OUTP + "/d_cb8.sc", name="CB8-20_RX08", parent="U4_STOP", translate=[-150, 70, 133.72]),
       C("component.insert_design", path=OUTP + "/d_nut.sc", name="STEP대기_NUT-M8_RX08", parent="U4_STOP", translate=[-150, 70, 124]),
       C("component.insert_design", path=OUTP + "/d_kqa.sc", name="KQ2L06-M5A_RX08_HEAD", parent="U4_WHEEL_N", translate=[-250, 104, 92]),
       C("component.insert_design", path=OUTP + "/d_kqb.sc", name="KQ2L06-M5A_RX08_ROD", parent="U4_WHEEL_N", translate=[-217, 104, 92])]
for c in ["CB5-16_RX08_LIP", "CB5-16_RX08_TOP", "CB8-20_RX08", "STEP대기_NUT-M8_RX08", "KQ2L06-M5A_RX08_HEAD", "KQ2L06-M5A_RX08_ROD"]:
    s1.append(C("component.break_link", component=c))
stages['1_insert'] = s1

# ---------- 2. 고정 쪽 가공품·실린더 몸 (U4_WHEEL_N 활성)
BR = "P_RX08_STOP_BRKT_밀링"
CY = "STEP대기_CDQ2A25-20DMZ"
s2 = [C("component.activate", component="U4_WHEEL_N"),
      C("sketch.create", plane={"origin": [0, 104, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX08_STOP_BRKT"),
      C("sketch.line", points=[[-268, 60], [-140, 60], [-140, 242], [-152, 242], [-152, 72], [-257.5, 72], [-257.5, 112], [-268, 112]], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX08_STOP_BRKT", distance=40, operation="new", body_name=BR, name="EX_RX08_STOP_BRKT"),
      box(None, -153, 63, 72, -139, 86, 234, op="cut", targets=[BR]),          # 다리 Y 86~104만 남김(윗판은 Y 64~104)
      box(None, -200, 79, 69, -139, 89, 72.01, op="cut", targets=[BR])]        # 발 윗면 키 홈 폭 10 깊이 3
for (y, z) in LIP:
    s2.append(cyl(2.75, 10.7, [-268.1, y, z], [1, 0, 0], "cut", targets=[BR]))   # 립 Ø5.5 통과
for (x, y) in TOPB:
    s2.append(cyl(2.75, 8.2, [x, y, 233.9], [0, 0, 1], "cut", targets=[BR]))    # 윗판 Ø5.5 통과(지시 M5 탭 -> 통과, 보고서)
    s2.append(cyl(2.1, 8.2, [x, y, 241.9], [0, 0, 1], "cut", targets=["P_M02_BASE"]))  # BASE M5 탭 관통
# BASE 관 장공 넓힘: 새 관 2줄(X -169, Y 70·79), 굽힘 호가 BASE 안에 걸림
s2.append(box(None, -175.5, 66, 241, -164.9, 84, 251, op="cut", targets=["P_M02_BASE"]))
# 실린더 몸 임시 형상
s2 += [box(CY, -257.5, 64, 72, -210, 104, 112),
       cyl(6.2, 22, [-210, 84, 92], [-1, 0, 0], "cut", targets=[CY]),          # 로드 자리(후퇴 20 + 2)
       cyl(2.5, 8, [-250, 104, 92], [0, -1, 0], "cut", targets=[CY]),           # 포트 머리 쪽
       cyl(2.5, 8, [-217, 104, 92], [0, -1, 0], "cut", targets=[CY])]           # 포트 로드 쪽
for (y, z) in LIP:
    s2.append(cyl(2.1, 8, [-257.5, y, z], [1, 0, 0], "cut", targets=[CY]))      # M5 탭 4
s2 += [C("material.assign", bodies=[BR], material="SUS304"),
       C("material.assign", bodies=[CY], material="Aluminum"),
       C("component.move_bodies", bodies=[CY], component=CY)]
stages['2_fixed'] = s2

# ---------- 3. 움직이는 쪽: 로드·멈춤 블록 (U4_STOP 활성), 대차 발 장공
BL = "P_RX08_STOP_BLOCK_밀링"
RD = "STEP대기_CDQ2A25-20DMZ_ROD"
s3 = [C("component.activate", component="U4_STOP"),
      C("sketch.create", plane={"origin": [0, 104, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX08_STOP_BLOCK"),
      C("sketch.line", points=[[-167, 72], [-143.5, 72], [-143.5, 124], [-156.5, 124], [-156.5, 100], [-167, 100]], closed=True),
      C("sketch.finish"),
      C("solid.extrude", sketch="SK_RX08_STOP_BLOCK", distance=40, operation="new", body_name=BL, name="EX_RX08_STOP_BLOCK"),
      box(None, -153, 80, 71, -143, 105, 125, op="cut", targets=[BL]),
      box(None, -157, 80, 100, -152.9, 105, 125, op="cut", targets=[BL]),
      box(None, -166.5, 79.1, 69.2, -153.5, 88.9, 72.1, op="join", targets=[BL]),   # 밑면 키(발 홈)
      cyl(4.4, 12, [-167, 84, 92], [1, 0, 0], "cut", targets=[BL]),                 # M10x1.25 탭 깊이 12
      cyl(3.4, 54, [-150, 70, 71], [0, 0, 1], "cut", targets=[BL]),                 # M8 탭 관통
      cyl(6, 43, [-210, 84, 92], [1, 0, 0], "new", name=RD),
      cyl(5, 10, [-167, 84, 92], [1, 0, 0], "join", targets=[RD]),                  # M10 수나사(블록 탭 안)
      C("material.assign", bodies=[BL], material="SUS304"),
      C("material.assign", bodies=[RD], material="S45C"),
      C("component.activate", component="U4_XCAR"),
      box(None, -174, 66, 249, -164.9, 84, 263, op="cut", targets=["P_RX06_CARRIAGE"]),
      C("component.activate", component="root")]
stages['3_moving'] = s3

# ---------- 4. 관 2줄 (꺾인 점 + 굽힘 R15)
def tube_cmds(name, comp, pts, radii, desc, make_comp=True):
    def sub(a, b): return [a[i]-b[i] for i in range(3)]
    def add(a, b): return [a[i]+b[i] for i in range(3)]
    def mul(a, s): return [x*s for x in a]
    def norm(a):
        l = math.sqrt(sum(x*x for x in a)); return [x/l for x in a]
    segs = []; cur = pts[0]
    for i in range(1, len(pts)-1):
        p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
        d1 = norm(sub(p1, p0)); d2 = norm(sub(p2, p1))
        cosang = max(-1, min(1, sum(d1[k]*d2[k] for k in range(3))))
        th = math.acos(cosang); R = radii[i-1]
        tl = R*math.tan(th/2)
        assert math.dist(p0, p1) + 1e-6 >= tl and math.dist(p1, p2) + 1e-6 >= tl, (name, i)
        a = sub(p1, mul(d1, tl)); b = add(p1, mul(d2, tl))
        bis = norm(sub(d2, d1)); dc = R/math.cos(th/2)
        cen = add(p1, mul(bis, dc))
        mid = add(cen, mul(norm(sub(p1, cen)), R))
        if math.dist(cur, a) > 0.01: segs.append(("L", cur, a))
        segs.append(("A", a, mid, b)); cur = b
    if math.dist(cur, pts[-1]) > 0.05: segs.append(("L", cur, pts[-1]))
    # 곧은 구간이 양 끝 굽힘의 접선 길이를 다 담는지
    def tlen(i):
        d1 = norm(sub(pts[i], pts[i-1])); d2 = norm(sub(pts[i+1], pts[i]))
        th = math.acos(max(-1, min(1, sum(d1[k]*d2[k] for k in range(3)))))
        return radii[i-1]*math.tan(th/2)
    for i in range(1, len(pts)-2):
        assert math.dist(pts[i], pts[i+1]) + 1e-6 >= tlen(i) + tlen(i+1), (name, 'seg', i)
    r4 = lambda v: [round(x, 4) for x in v]
    sk = "SK_%s" % name
    cmds = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    for s in segs:
        if s[0] == "L": cmds.append(C("sketch.line3d", points=[r4(s[1]), r4(s[2])]))
        else: cmds.append(C("sketch.arc3d", start=r4(s[1]), through=r4(s[2]), end=r4(s[3])))
    cmds.append(C("sketch.finish"))
    cmds.append(C("solid.pipe", path_sketch=sk, path=["w%d" % (i+1) for i in range(len(segs))], diameter=6.0, operation="new", body_name=name))
    cmds += [C("material.assign", bodies=[name], material="Default")]
    if make_comp: cmds.append(C("component.create", name=comp, parent="U8_PNEU", activate=False))
    cmds += [C("component.move_bodies", bodies=[name], component=comp),
             C("component.metadata.set", component=comp, part_number="TU0604", bom_type="purchased", description=desc)]
    L = 0.0
    for s in segs:
        if s[0] == "L": L += math.dist(s[1], s[2])
        else: L += math.dist(s[1], s[3]) * math.pi / (2 * math.sqrt(2))
    return cmds, round(L, 1)

VX = 1123.25          # 8번 밸브 중심 X(7번 1112.75 + 10.5)
A_pts = [[-264.5, 117.5, 92], [-282, 117.5, 92], [-282, 148, 92], [-216.5, 148, 92], [-216.5, 148, 208], [-216.5, 79, 208],
         [-169, 79, 208], [-169, 79, 270], [-169, 88, 300], [-169, 88, 391], [-107, 88, 391], [-85, 110, 391], [VX, 110, 391],
         [VX, 63, 391], [VX, 63, 370.6]]
B_pts = [[-202.5, 117.5, 92], [-186, 117.5, 92], [-186, 156, 92], [-216.5, 156, 92], [-216.5, 156, 234], [-216.5, 70, 234],
         [-169, 70, 234], [-169, 70, 275], [-169, 61, 305], [-169, 61, 381], [-95, 61, 381], [-95, 110, 381], [1155, 110, 381],
         [1155, 63, 381], [1155, 63, 312], [VX, 63, 312], [VX, 63, 331.4]]
cA, LA = tube_cmds("TU0604_M08P_RX08_A", "TU0604_M08P_RX08_A", A_pts, [15] * (len(A_pts) - 2),
                   "SMC TU0604 OD6, RX-08 stopper cylinder head port (push = OFF) <-> valve 8 B (PZ). Riser (-216.5,148) -> under BASE Y 79 -> slot (-169,79) -> Y 88 -> Z 391 along Y 110 (below clamps F, comb)", make_comp=False)
cB, LB = tube_cmds("TU0604_M08P_RX08_B", "TU0604_M08P_RX08_B", B_pts, [15] * (len(B_pts) - 2),
                   "SMC TU0604 OD6, RX-08 stopper cylinder rod port (pull = ON) <-> valve 8 A (NZ). Riser (-216.5,156) -> under BASE Y 70 -> slot (-169,70) -> Y 61 -> Z 381 along Y 110 -> X 1155 -> up into NZ", make_comp=False)
stages['4_tubes'] = [C("timeline.delete", features=["SK_TU0604_M08P_RX08_A", "SK_TU0604_M08P_RX08_B"])] + cA + cB   # 수정 1: 첫 길(Z 460/470)은 보 앞 클램프 F·조정기와 겹쳐 지우고 다시

# ---------- 5. U8 매니폴드 07 -> 08, 8번 밸브·피팅
MF7 = "STEP대기_SS5Y3-20-07_M08"
MF8 = "STEP대기_SS5Y3-20-08_M08"
s5 = [C("solid.remove", bodies=[MF7]),
      box(MF8, 1035, 100, 325.5, 1138, 120, 374.5)]
for x in (1039.8, 1133.2):
    for z in (343, 359):
        s5.append(cyl(2.25, 20.2, [x, 120.1, z], [0, -1, 0], "cut", targets=[MF8]))
s5 += [C("material.assign", bodies=[MF8], material="Aluminum"),
       C("component.move_bodies", bodies=[MF8], component=MF7),
       C("component.rename", component=MF7, name=MF8),
       C("component.metadata.set", component=MF8, part_number="SS5Y3-20-08", bom_type="purchased",
         description="STEP wait (E-10): SMC SY3000 bar manifold 8 stations (SS5Y3-20-08), temp box L 103 = 07 box 92.5 + one pitch 10.5, H 49, D 20, mount holes 4.5 at both ends (RX-08)")]
for o in ["STEP대기_TPH-01_1:1", "STEP대기_TPH-01_2:1", "STEP대기_TPH-01_3:1", "CB4-25_M08:3", "CB4-25_M08:4"]:
    s5.append(C("occurrence.move", occurrence=o, space="world", translate=[10.5, 0, 0]))
s5 += [C("occurrence.copy", occurrence="SY3120-5LZD-M5_M08:7", parent="U8_PNEU", in_place=True, translate=[10.5, 0, 0]),
       C("occurrence.copy", occurrence="KQ2L06-M5A_M08S_NZ:7", parent="U8_PNEU", in_place=True, translate=[10.5, 0, 0]),
       C("occurrence.copy", occurrence="KQ2L06-M5A_M08S_PZ:6", parent="U8_PNEU", in_place=True, translate=[10.5, 0, 0])]
stages['5_manifold'] = s5

for k, v in stages.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"tube_len": {"RX08_A": LA, "RX08_B": LB}}, open(os.path.join(OUT, 'gen_meta.json'), 'w'), indent=1)
print({k: len(v) for k, v in stages.items()}, LA, LB)
