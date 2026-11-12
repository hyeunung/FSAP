# RX-06 U4 X 위치 조절축 생성기 (v2.10.4 -> v2.11.0). 단계 파일을 tools/out/mech_RX-06/model/stage_*.json 으로 쓴다.
# 실행: python -B tools/gen_v2_rx06.py
import json, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'mech_RX-06', 'model')
os.makedirs(OUT, exist_ok=True)

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

# ---- 행렬: occurrence.move(space world, matrix)는 world' = A*world + t (실측 2026-11-12)
def mat_mul(A, B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mat_T(A): return [[A[j][i] for j in range(3)] for i in range(3)]
def mat_vec(A, v): return [sum(A[i][k]*v[k] for k in range(3)) for i in range(3)]
def cols(ex, ey, ez): return [[ex[i], ey[i], ez[i]] for i in range(3)]
def rel_move(R0, t0, RD, tD):
    A = mat_mul(RD, mat_T(R0)); At0 = mat_vec(A, t0)
    t = [tD[i] - At0[i] for i in range(3)]
    return [A[0][0], A[0][1], A[0][2], t[0], A[1][0], A[1][1], A[1][2], t[1], A[2][0], A[2][1], A[2][2], t[2]]

# ---- 관 경로: 꺾인 점 + 꺾임 반경 -> line3d/arc3d
def tube_cmds(name, comp, pts, radii, desc):
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
        a = sub(p1, mul(d1, tl)); b = add(p1, mul(d2, tl))
        bis = norm(sub(d2, d1)); dc = R/math.cos(th/2)
        cen = add(p1, mul(bis, dc))
        mid = add(cen, mul(norm(sub(p1, cen)), R))
        segs.append(("L", cur, a)); segs.append(("A", a, mid, b)); cur = b
    if math.dist(cur, pts[-1]) > 0.05: segs.append(("L", cur, pts[-1]))
    r4 = lambda v: [round(x, 4) for x in v]
    cmds = [C("solid.remove", bodies=[name]), C("sketch.create", plane="XY", name="SK_%s_RX06" % name), C("sketch.options", sketch_3d=True)]
    for s in segs:
        if s[0] == "L": cmds.append(C("sketch.line3d", points=[r4(s[1]), r4(s[2])]))
        else: cmds.append(C("sketch.arc3d", start=r4(s[1]), through=r4(s[2]), end=r4(s[3])))
    cmds.append(C("sketch.finish"))
    cmds.append(C("solid.pipe", path_sketch="SK_%s_RX06" % name, path=["w%d" % (i+1) for i in range(len(segs))], diameter=6.0, operation="new", body_name=name))
    cmds.append(C("material.assign", bodies=[name], material="Default"))
    cmds.append(C("component.move_bodies", bodies=[name], component=comp))
    cmds.append(C("component.metadata.set", component=comp, part_number="TU0604", bom_type="purchased", description=desc))
    L = 0.0
    for s in segs:
        if s[0] == "L": L += math.dist(s[1], s[2])
        else:
            ch = math.dist(s[1], s[3]); R = None
            L += ch * 1.11  # quarter arc approx (arc/chord = pi/(2*sqrt2))
    return cmds, round(L, 1)

stages = {}
# ===== 1 원판 묶음 나눔 (앱에서 이미 실행: stage_1)
stages['1_disk'] = [
    C("component.create", name="U4_DISK_BASE", parent="root", activate=False),
    C("component.move_bodies", bodies=["P_M02_DISK_BASE", "P_M02_DISK_HSG"], component="U4_DISK_BASE"),
] + [C("joint.delete", joint=j) for j in ["Rigid Group 10:419", "Rigid Group 10:434", "Rigid Group 10:479", "Rigid Group 10:482", "Rigid Group 10:485", "Rigid Group 10:488"]] + [
    C("joint.rigid_group", occurrences=["U2_TABLE:1", "U4_DISK_BASE:1", "6004ZZ_M02_1:1", "6004ZZ_M02_2:1", "CB5-16_M02_11:1", "CB5-16_M02_12:1", "CB5-16_M02_13:1", "CB5-16_M02_14:1"]),
    C("joint.edit", joint="J_U4_DISK", a={"occurrence": "U4_DISK_BASE:1", "point": [-175, 0, 0], "z": [0, 0, 1]}, b={"occurrence": "U4_DISK:1", "point": [-175, 0, 0], "z": [0, 0, 1]}, flip=True),
    C("component.metadata.set", component="U4_DISK_BASE", description="RX-06: fixed disk base group (DISK_BASE, HSG, 6004ZZ x2, CB5-16 x4) split from U4_WHEEL_N, rigid to U2_TABLE"),
]
# ===== 2 컴포넌트 + 레일 STEP(앱에서 실행: insert 21분) + 나사 부품 설계 넣기
stages['2_insert'] = [
    C("component.create", name="U4_XAXIS", parent="root", activate=False),
    C("component.create", name="U4_XCAR", parent="root", activate=False),
    C("file.insert_step", path="C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/SSEB13-570/SSEB13-570.stp", name="SSEB13-570_RX06_R1", matrix=[1, 0, 0, -325, 0, -1, 0, 120, 0, 0, -1, 266]),
    C("component.insert_design", path="C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/mech_RX-06/model/rx06_screw_parts.sc", name="RX06_SCREW_PARTS", parent="root"),
]
# ===== 3 구매품 정리
s3 = [
    C("component.break_link", component="RX06_SCREW_PARTS"),
    C("component.rename", component="RX06_SCREW_PARTS", name="BSW20_RX06"),
    C("component.create", name="BUN20_RX06", parent="root", activate=False),
    C("component.create", name="BSS2020-1100_RX06", parent="root", activate=False),
    C("component.create", name="BSS2020-1100_RX06_NUT", parent="root", activate=False),
    C("component.create", name="STEP대기_HANDLE_D50", parent="root", activate=False),
    C("component.move_bodies", bodies=["BUN20_RX06_BODY", "BUN20_RX06_RING"], component="BUN20_RX06"),
    C("component.move_bodies", bodies=["BSS2020-1100_RX06_NUT"], component="BSS2020-1100_RX06_NUT"),
    # 축: STEP 축 바디가 불리언(자르기)을 받지 않아(no result) 같은 지름 Ø20 x 351 원통으로 그림(보고서)
    cyl(10, 351, [-445, 70, 530], [1, 0, 0], "new", name="BSS2020-1100_RX06_SHAFT"),
    C("component.move_bodies", bodies=["BSS2020-1100_RX06_SHAFT"], component="BSS2020-1100_RX06"),
    # 손잡이 임시 형상 Ø50 x 20 + 손잡이 봉 Ø12 x 30 (축 끝 X -445 바깥)
    cyl(25, 20, [-445, 70, 530], [-1, 0, 0], "new", name="STEP대기_HANDLE_D50"),
    cyl(6, 30, [-465, 88, 530], [-1, 0, 0], "join", targets=["STEP대기_HANDLE_D50"]),
    C("component.move_bodies", bodies=["STEP대기_HANDLE_D50"], component="STEP대기_HANDLE_D50"),
    # 레일: STEP 레일도 자르기를 받지 않음 -> STEP 레일 바디를 빼고 같은 단면(폭 12, 높이 7.5) 210 길이로 그려 같은 레일 컴포넌트에 넣음
    C("solid.remove", bodies=["Chamfer2"]),
    box("SSEB13-570_RX06_RAIL", -335, 112.5, 260, -125, 120, 272),
    C("component.move_bodies", bodies=["SSEB13-570_RX06_RAIL"], component="RAIL_SSEB13-570"),
    C("body.rename", body="LPattern2", name="SSEB13-570_RX06_BLOCK"),
    C("component.rename", component="SSEB13-570_RX06_R1", name="SSEB13-570_RX06"),
]
for c, pn, ty, d in [("BSW20_RX06", "BSW20", "purchased", "MISUMI BSW20 ball screw support unit, fixed side (RX-06 U4 X axis)"),
                      ("BUN20_RX06", "BUN20", "purchased", "MISUMI BUN20 ball screw support unit, supported side (RX-06)"),
                      ("BSS2020-1100_RX06", "BSS2020-1100", "purchased", "MISUMI BSS2020 rolled ball screw lead 20, cut to 351 (shaft drawn as dia 20 cylinder: STEP shaft refuses boolean trim)"),
                      ("BSS2020-1100_RX06_NUT", "BSS2020-1100", "reference", "nut of BSS2020-1100 (counted with the screw line)"),
                      ("STEP대기_HANDLE_D50", "HDLC-D50(temp)", "purchased", "STEP pending: MISUMI HDLC series handle dia 50, temporary part number, lock lever (E-10)"),
                      ("SSEB13-570_RX06", "SSEB13-570", "purchased", "MISUMI SSEB13 miniature guide, rail cut to 210 (rail drawn from STEP section: STEP rail refuses boolean trim), 2 blocks per rail"),
                      ("U4_XAXIS", None, None, "RX-06: fixed side of U4 X adjust axis (rails, BSW20/BUN20, spacers, stops), rigid to frame beam"),
                      ("U4_XCAR", None, None, "RX-06: moving carriage of U4 X adjust axis (P_RX06_CARRIAGE, 4 blocks, nut), J_U4_X")]:
    p = dict(component=c, description=d)
    if pn: p["part_number"] = pn
    if ty: p["bom_type"] = ty
    s3.append(C("component.metadata.set", **p))
stages['3_parts'] = s3

# ===== 4 가공품: 캐리지·스페이서·멈춤
CAR = "P_RX06_CARRIAGE"
s4 = [
    C("sketch.create", plane={"origin": [-240, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX06_CARRIAGE"),
    C("sketch.line", points=[[45, 250], [107, 250], [107, 565], [95, 565], [95, 262], [45, 262]], closed=True),
    C("sketch.finish"),
    C("solid.extrude", sketch="SK_RX06_CARRIAGE", distance=115, operation="new", body_name=CAR, name="EX_RX06_CARRIAGE"),
    box(None, -174.5, 47, 497, -162.5, 95.5, 563, op="join", targets=[CAR]),
    cyl(23.5, 13, [-175, 70, 530], [1, 0, 0], "cut", targets=[CAR]),
]
for (y, z) in [(55.3, 504.5), (55.3, 555.5), (84.7, 504.5), (84.7, 555.5)]:
    s4.append(cyl(2.5, 13, [-175, y, z], [1, 0, 0], "cut", targets=[CAR]))   # M6 탭(너트 플랜지)
FOOT = [(-232, 50), (-215, 50), (-150, 50), (-215, 85), (-180, 85), (-150, 85)]
for (x, y) in FOOT:
    s4.append(cyl(2.75, 13, [x, y, 249.5], [0, 0, 1], "cut", targets=[CAR]))  # M5 통과
s4.append(box(None, -165, 66, 249, -157, 84, 263, op="cut", targets=[CAR]))  # 관 통과 장공
s4 += [C("material.assign", bodies=[CAR], material="A5052"), C("component.move_bodies", bodies=[CAR], component="U4_XCAR")]
s4 += [box("P_RX06_SPACER_F", -392, 100, 482.5, -340, 120, 577.5), box("P_RX06_SPACER_S", -120, 100, 482.5, -94, 120, 577.5),
       box("P_RX06_STOP_A", -335, 108, 260, -333, 112.5, 272), box("P_RX06_STOP_B", -127, 108, 260, -125, 112.5, 272),
       C("material.assign", bodies=["P_RX06_SPACER_F", "P_RX06_SPACER_S"], material="A5052"),
       C("material.assign", bodies=["P_RX06_STOP_A", "P_RX06_STOP_B"], material="SUS304"),
       C("component.move_bodies", bodies=["P_RX06_SPACER_F", "P_RX06_SPACER_S", "P_RX06_STOP_A", "P_RX06_STOP_B"], component="U4_XAXIS")]
stages['4_made'] = s4

# ===== 5 윗판·실린더 브래킷 고침, 볼트 옮김
B = "P_M02_BASE"
s5 = [
    box(None, -275, 199, 242, -205, 266, 248, op="join", targets=[B]),        # 보 밑 연장(브래킷 받침)
    box(None, -335, 116, 248, -135, 270, 251, op="cut", targets=[B]),         # Y>=116 윗면 248(보 밑면과 틈 2)
    cyl(4.05, 8, [-161.006, 94, 242], [0, 0, 1], "join", targets=[B]),        # 관 U4_A2 옛 구멍 메움
    box(None, -165, 66, 241, -157, 84, 251, op="cut", targets=[B]),           # 관 U4_A2·U4_B 장공
    cyl(2.15, 8, [-168, 126, 242], [0, 0, 1], "join", targets=[B]),           # BASE_4 옛 구멍 메움
    cyl(2.1, 8, [-159, 110, 242], [0, 0, 1], "cut", targets=[B]),             # BASE_4 새 탭
    cyl(2.8, 4, [-168, 126, 238], [0, 0, 1], "join", targets=["P_M02S_PIVOT_BRKT_B"]),
    cyl(2.75, 4, [-159, 110, 238], [0, 0, 1], "cut", targets=["P_M02S_PIVOT_BRKT_B"]),
]
for (x, y) in FOOT:
    s5.append(cyl(2.1, 8.2, [x, y, 241.9], [0, 0, 1], "cut", targets=[B]))   # 캐리지 볼트 M5 탭
for x in (-255, -225):
    s5.append(cyl(2.1, 6.2, [x, 248, 241.9], [0, 0, 1], "cut", targets=[B]))  # 브래킷 볼트 M5 탭
# 실린더 브래킷: 윗날개를 Z 236~242로(윗판 밑), 실린더 볼트 머리 자리 홈
K = "P_M02S_CYL_BRKT"
s5 += [
    C("solid.remove", bodies=[K]),
    C("sketch.create", plane={"origin": [-265, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_M02S_CYL_BRKT_RX06"),
    C("sketch.line", points=[[222.43, 205], [228.43, 205], [228.43, 236], [262, 236], [262, 242], [222.43, 242]], closed=True),
    C("sketch.finish"),
    C("solid.extrude", sketch="SK_M02S_CYL_BRKT_RX06", distance=50, operation="new", body_name=K, name="EX_M02S_CYL_BRKT_RX06"),
]
for (x, z) in [(-252.75, 210.25), (-227.25, 210.25), (-252.75, 235.75), (-227.25, 235.75)]:
    s5.append(cyl(2.75, 6.2, [x, 228.53, z], [0, -1, 0], "cut", targets=[K]))
for x in (-255, -225):
    s5.append(cyl(2.75, 6.2, [x, 248, 235.9], [0, 0, 1], "cut", targets=[K]))
s5 += [box(None, -258, 228.43, 235.9, -247.5, 234.5, 242.1, op="cut", targets=[K]),
       box(None, -232.5, 228.43, 235.9, -222, 234.5, 242.1, op="cut", targets=[K]),
       C("material.assign", bodies=[K], material="SUS304"),
       C("component.move_bodies", bodies=[K], component="U4S_CYL")]
s5 += [C("occurrence.move", occurrence="CB5-12_M02S_BEAM_1:1", space="world", translate=[0, 0, -8]),
       C("occurrence.move", occurrence="CB5-12_M02S_BEAM_2:1", space="world", translate=[0, 0, -8]),
       C("occurrence.move", occurrence="CB5-12_M02S_BASE_4:1", space="world", translate=[9, -16, 0])]
stages['5_base'] = s5

# ===== 6 볼트 자리: CB5-16_M02_1~4 -> 캐리지 발 볼트(위에서), +2 복사; CB6-20 너트 볼트 4
R0_cb5 = cols([0, 0, 1], [0, 1, 0], [-1, 0, 0])   # 가정: 머리 아래(로컬 x -> +Z)
RD_cb5 = cols([0, 0, -1], [0, 1, 0], [1, 0, 0])
s6 = []
old = [("CB5-16_M02_1:1", (-310, 140, 242)), ("CB5-16_M02_2:1", (-310, 180, 242)), ("CB5-16_M02_3:1", (-160, 140, 242)), ("CB5-16_M02_4:1", (-160, 180, 242))]
for (occ, t0), (x, y) in zip(old, FOOT[:4]):
    s6.append(C("occurrence.move", occurrence=occ, space="world", matrix=rel_move(R0_cb5, list(t0), RD_cb5, [x, y, 262])))
stages['6_bolts'] = s6
# 복사 볼트는 결과 occurrence id를 보고 따로 옮긴다(아래 함수)
def cb5_copy_move(occ_id, x, y):
    return C("occurrence.move", occurrence=occ_id, space="world", matrix=rel_move(R0_cb5, [-310, 140, 242], RD_cb5, [x, y, 262]))
R0_cb6 = cols([0, -1, 0], [1, 0, 0], [0, 0, 1]); t0_cb6 = [-1937, 92, 197]
RD_cb6 = cols([-1, 0, 0], [0, 1, 0], [0, 0, -1])
def cb6_copy_move(occ_id, y, z, R0=R0_cb6, t0=t0_cb6):
    return C("occurrence.move", occurrence=occ_id, space="world", matrix=rel_move(R0, t0, RD_cb6, [-154, y, z]))

# ===== 8 관
U6_pts = [[1070.75, 53.0, 331.4], [1070.75, 53.0, 262.0], [950.0, 53.0, 262.0], [850.0, 108.0, 262.0], [-84.0, 108.0, 262.0], [-84.0, 32.0, 262.0], [-347.0, 32.0, 262.0], [-347.0, -130.0, 262.0], [-347.0, -130.0, 210.3]]
U6_R = [30, 30, 30, 15, 15, 15, 30]  # (-347,32) R15: 관 브래킷 U6(Y <= 16) 들어가기 전 곧게(앱 검사 겹침 23 mm3 고침)
A2_pts = [[727.94, 95.0, 465.7], [727.94, 95.0, 440.0], [700.0, 110.0, 440.0], [-84.0, 110.0, 440.0], [-84.0, 79.0, 440.0], [-161.006, 79.0, 440.0], [-161.006, 79.0, 192.5], [-208.5, 79.0, 192.5], [-208.5, 214.0, 192.5], [-208.5, 214.0, 208.5]]
B_pts = [[1049.75, 53.0, 370.6], [1049.75, 53.0, 430.0], [1000.02, 110.0, 430.0], [-84.0, 110.0, 430.0], [-84.0, 70.0, 430.0], [-161.006, 70.0, 430.0], [-161.006, 70.0, 223.0], [-208.5, 70.0, 223.0], [-208.5, 171.5, 223.0]]
s8 = []
c1, L6 = tube_cmds("TU0604_M08P_U6", "TU0604_M08P_U6", U6_pts, U6_R, "SMC TU0604 OD6 (RX-06 route: leaves along X -84 corridor before carriage, Y 30 in front of carriage foot)")
c2, LA = tube_cmds("TU0604_M08P_U4_A2", "TU0604_M08P_U4_A2", A2_pts, [16, 30, 15, 15, 15, 16, 16, 16], "SMC TU0604 OD6 (RX-06 route: X -84 corridor, riser (-161,79) through carriage foot slot)")
c3, LB = tube_cmds("TU0604_M08P_U4_B", "TU0604_M08P_U4_B", B_pts, [30, 30, 15, 15, 15, 16, 16], "SMC TU0604 OD6 (RX-06 route: X -84 corridor, riser (-161,70) through carriage foot slot)")
s8 = c1 + c2 + c3
s8 += [C("occurrence.move", occurrence="P_M08_TUBE_CLAMP_L_6:1", space="world", translate=[-106, 0, 0]),
       C("occurrence.move", occurrence="CB5-16_M08_PY:30", space="world", translate=[-106, 0, 0]),
       C("occurrence.move", occurrence="CB5-16_M08_PY:31", space="world", translate=[-106, 0, 0])]
stages['8_tubes'] = s8

for k, v in stages.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"tube_len": {"U6": L6, "U4_A2": LA, "U4_B": LB}}, open(os.path.join(OUT, 'gen_meta.json'), 'w'), indent=1)
print({k: len(v) for k, v in stages.items()}, L6, LA, LB)
