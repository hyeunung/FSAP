# RX-DC-03 개념 W 생성기 (모델링부 2026-11-24)
# 좌표: θ0(J_U4_PRESS 0) · J_U4_X 0 · J_U5_X 0 월드. 단계 파일 tools/out/mech_RX-DC-03/model/s*.json
import json, math, os, sys
OUT = os.path.join(os.path.dirname(__file__), 'out', 'mech_RX-DC-03', 'model')
os.makedirs(OUT, exist_ok=True)

def r(v, n=4):
    return [round(x, n) for x in v]

def unit(v):
    l = math.sqrt(sum(x * x for x in v)); return [x / l for x in v]

def arc_mid(c, s, e):
    v = unit([(s[i] - c[i]) + (e[i] - c[i]) for i in range(3)])
    R = math.sqrt(sum((s[i] - c[i]) ** 2 for i in range(3)))
    return [c[i] + R * v[i] for i in range(3)]

def path_cmds(sk, segs, comp):
    """segs: [('L', p0, p1) | ('A', start, through, end)]"""
    cmds = [{"command": "sketch.create", "params": {"plane": "XY", "name": sk}},
            {"command": "sketch.options", "params": {"sketch_3d": True}}]
    for s in segs:
        if s[0] == 'L':
            cmds.append({"command": "sketch.line3d", "params": {"points": [r(s[1]), r(s[2])]}})
        else:
            cmds.append({"command": "sketch.arc3d", "params": {"start": r(s[1]), "through": r(s[2]), "end": r(s[3])}})
    cmds.append({"command": "sketch.finish", "params": {}})
    return cmds, ["w%d" % (i + 1) for i in range(len(segs))]

def pipe(sk, segs, dia, body, comp):
    c, ids = path_cmds(sk, segs, comp)
    c.append({"command": "solid.pipe", "params": {"path_sketch": sk, "path": ids, "diameter": dia,
              "operation": "new", "body_name": body, "name": "PIPE_" + sk[3:]}})
    return c

def box(x0, x1, y0, y1, z0, z1, name, op="new", body=None, targets=None):
    p = {"corner": [x0, y0, z0], "length": round(x1 - x0, 4), "width": round(y1 - y0, 4),
         "height": round(z1 - z0, 4), "operation": op, "name": name}
    if body: p["body_name"] = body
    if targets: p["targets"] = targets
    return {"command": "solid.box", "params": p}

def cyl(rad, h, base, axis, name, op, targets=None, body=None):
    p = {"radius": rad, "height": h, "base": base, "axis": axis, "operation": op, "name": name}
    if targets: p["targets"] = targets
    if body: p["body_name"] = body
    return {"command": "solid.cylinder", "params": p}

def act(c):
    return {"command": "component.activate", "params": {"component": c}}

def mat(bodies, m):
    return {"command": "material.assign", "params": {"bodies": bodies, "material": m}}

GUIDE = "P_RXDC03_LEAD_GUIDE_판금"
T2 = "P_RXDC03_T2_GUIDE_판금"
RISER = "P_RXDC03_RISER_BRKT_판금"
CLAMP = "P_RXDC03_BEAM_CLAMP_판금"
SWING = "P_RX19_SWING_밀링"
BLOCK = "P_RX19_BLOCK_밀링"
BEAM = "P_M07_BEAM"
CE = "STEP대기_HG-KR23_CONN_ENC"
CP = "STEP대기_HG-KR23_CONN_PWR"
LE = "STEP대기_HG-KR23_LEAD_ENC"
LP = "STEP대기_HG-KR23_LEAD_PWR"
COIL = "STEP대기_HG-KR23_LEAD_LOOP"
XE = "STEP대기_MR-J3ENCBL5M-A2-H"
XP = "STEP대기_MR-PWS1CBL5M-A2-H"
TT = "STEP대기_PTFE_TUBE_8x7"
DIA = 6.5      # 리드·연장 케이블 외경 임시(D-232)
XL = -314.6    # 케이블 중심선 X
TILT = 5.676   # 가운데 각(θ0 틀에서 +Z -> -Y)
PIV = [XL, 75.0, 140.0]

# ---------- s1: 그네(U4_PRESS) ----------
s1 = [act("U4_PRESS"),
      box(-296.6, -293.6, 52, 96, 86, 144, "RXDC03_GUIDE_PLATE", body=GUIDE),
      box(-318.6, -295.0, 84, 87, 136, 146, "RXDC03_GUIDE_TIE", op="join", targets=[GUIDE]),
      box(-318.6, -296.6, 52, 74, 86, 136, "RXDC03_CONN_ENC", body=CE),
      box(-318.6, -296.6, 74, 96, 86, 136, "RXDC03_CONN_PWR", body=CP),
      {"command": "solid.move", "params": {"bodies": [GUIDE, CE, CP], "axis": [1, 0, 0], "angle": "%s deg" % TILT,
                                            "origin": PIV, "name": "RXDC03_TILT"}},
      box(-296.6, -246.0, 74, 88, 141, 144, "RXDC03_GUIDE_ARM", op="join", targets=[GUIDE]),
      box(-249.0, -246.0, 74, 88, 141, 163, "RXDC03_GUIDE_TAB", op="join", targets=[GUIDE]),
      cyl(2.75, 5, [-250.0, 80, 150], "X", "RXDC03_GUIDE_HOLE_1", "cut", [GUIDE]),
      cyl(2.75, 5, [-250.0, 80, 159], "X", "RXDC03_GUIDE_HOLE_2", "cut", [GUIDE]),
      cyl(2.1, 12, [-246.0, 80, 150], "X", "RXDC03_SWING_TAP_1", "cut", [SWING]),
      cyl(2.1, 12, [-246.0, 80, 159], "X", "RXDC03_SWING_TAP_2", "cut", [SWING]),
      cyl(30.25, 13, [-318.6, 15, 103], "X", "RXDC03_COIL", "new", body=COIL),
      cyl(23.75, 13, [-318.6, 15, 103], "X", "RXDC03_COIL_IN", "cut", [COIL]),
      ]
# 모터 리드(그네 위 고정만): L1 XY 면 R27, 이어 YZ 면(X -314.6) 중심선 오프셋 ±4
a = math.acos(1 - 15.95 / 62.0)
t = math.radians(TILT)
d1 = (-math.sin(t), math.cos(t))
def lead(dz, name, sk):
    z0 = 68.05 + dz
    segs = []
    p0 = [-287.6, -34.9, z0]; c = [-287.6, -7.9, z0]; p1 = [XL, -7.9, z0]
    segs.append(('A', p0, arc_mid(c, p0, p1), p1))
    q = [XL, -2.9, z0]; segs.append(('L', p1, q))
    # 오른쪽 굽힘(아래로) 중심 (-2.9, 37.05), 반지름 31 + dz
    R1 = 31 + dz; c1 = [XL, -2.9, 37.05]
    e1 = [XL, -2.9 + R1 * math.sin(a), 37.05 + R1 * math.cos(a)]
    segs.append(('A', q, arc_mid(c1, q, e1), e1))
    R2 = 31 - dz; c2 = [XL, 38.60, 83.11]
    s2 = [XL, c2[1] - R2 * math.sin(a), c2[2] - R2 * math.cos(a)]
    e2 = [XL, 38.60, 83.11 - R2]
    segs.append(("A", e1, arc_mid(c2, e1, e2), e2))
    f0 = [XL, 48.50, 83.11 - R2]; segs.append(('L', e2, f0))
    c3 = [XL, 48.50, 83.11]
    # 끝: 중심 - R2 * 왼쪽 법선(d1) ; 왼쪽 법선 of (dy,dz) = (-dz, dy)
    nl = (-d1[1], d1[0])
    f1 = [XL, c3[1] - R2 * nl[0], c3[2] - R2 * nl[1]]
    segs.append(('A', f0, arc_mid(c3, f0, f1), f1))
    # 길이
    L = 27 * math.pi / 2 + 5 + R1 * a + R2 * a + 9.9 + R2 * (math.pi / 2 + t)
    return pipe(sk, segs, DIA, name, "U4_PRESS"), L, f1
cE, LEN_E, endE = lead(+4, LE, "SK_RXDC03_LEAD_ENC")
cP, LEN_P, endP = lead(-4, LP, "SK_RXDC03_LEAD_PWR")
s1 += cE + cP
s1 += [mat([GUIDE], "SUS304"), mat([CE, CP], "Nylon"), mat([LE, LP, COIL], "Default"), act("root")]

# ---------- s2: 블록(U4_XCAR) ----------
s2 = [act("U4_XCAR"),
      box(-330, -305, 64, 100, 236, 250, "RXDC03_BLK_SLOT", op="cut", targets=[BLOCK]),
      box(-310.6, -307.6, 66, 84, 212, 236, "RXDC03_T2_LIP", body=T2),
      box(-310.6, -280.0, 66, 84, 233, 236, "RXDC03_T2_FLANGE", op="join", targets=[T2]),
      cyl(2.75, 5, [-296, 75, 232], "Z", "RXDC03_T2_HOLE_1", "cut", [T2]),
      cyl(2.75, 5, [-286, 75, 232], "Z", "RXDC03_T2_HOLE_2", "cut", [T2]),
      cyl(2.1, 10, [-296, 75, 236], "Z", "RXDC03_BLK_TAP_T2_1", "cut", [BLOCK]),
      cyl(2.1, 10, [-286, 75, 236], "Z", "RXDC03_BLK_TAP_T2_2", "cut", [BLOCK]),
      box(-296.6, -293.6, 83, 97, 250, 392, "RXDC03_RISER_PLATE", body=RISER),
      box(-296.6, -273.0, 83, 97, 250, 253, "RXDC03_RISER_FLANGE", op="join", targets=[RISER]),
      box(-318.6, -295.0, 83, 86, 330, 350, "RXDC03_RISER_TIE", op="join", targets=[RISER]),
      box(-296.6, -268.0, 73, 89, 389, 392, "RXDC03_RISER_ARM", op="join", targets=[RISER]),
      cyl(2.75, 5, [-286, 90, 249], "Z", "RXDC03_RISER_HOLE_1", "cut", [RISER]),
      cyl(2.75, 5, [-278, 90, 249], "Z", "RXDC03_RISER_HOLE_2", "cut", [RISER]),
      cyl(2.1, 10, [-286, 90, 240], "Z", "RXDC03_BLK_TAP_RS_1", "cut", [BLOCK]),
      cyl(2.1, 10, [-278, 90, 240], "Z", "RXDC03_BLK_TAP_RS_2", "cut", [BLOCK]),
      ]
for i, y in enumerate([71, 79]):
    nm = TT + "_%d" % (i + 1)
    s2 += [cyl(4.0, 20, [XL, y, 212], "Z", "RXDC03_PTFE_%d" % (i + 1), "new", body=nm),
           cyl(3.5, 20, [XL, y, 212], "Z", "RXDC03_PTFE_IN_%d" % (i + 1), "cut", [nm])]
def xcable(y, body, sk):
    p0 = [XL, y, 142]; p1 = [XL, y, 344]; c = [-274.6, y, 344]; p2 = [-274.6, y, 384]; p3 = [-268.0, y, 384]
    segs = [('L', p0, p1), ('A', p1, arc_mid(c, p1, p2), p2), ('L', p2, p3)]
    return pipe(sk, segs, DIA, body, "U4_XCAR")
s2 += xcable(71, XE, "SK_RXDC03_XCAB_ENC") + xcable(79, XP, "SK_RXDC03_XCAB_PWR")
s2 += [mat([T2, RISER], "SUS304"), mat([TT + "_1", TT + "_2"], "PTFE"), mat([XE, XP], "Default"), act("root")]

# ---------- s3: 보 앞 고정 받침(U4_XAXIS) · 보 탭(U1_FRAME) ----------
s3 = [act("U4_XAXIS"),
      box(-352, -338, 117, 120, 507.5, 540, "RXDC03_CLAMP_WALL", body=CLAMP),
      box(-352, -338, 68, 120, 507.5, 510.5, "RXDC03_CLAMP_SHELF", op="join", targets=[CLAMP]),
      cyl(2.75, 5, [-345, 116, 522], "Y", "RXDC03_CLAMP_HOLE_1", "cut", [CLAMP]),
      cyl(2.75, 5, [-345, 116, 534], "Y", "RXDC03_CLAMP_HOLE_2", "cut", [CLAMP]),
      ]
for y, body, sk in [(71, XE + "_FIX", "SK_RXDC03_XFIX_ENC"), (79, XP + "_FIX", "SK_RXDC03_XFIX_PWR")]:
    s3 += pipe(sk, [('L', [-360, y, 514], [-345, y, 514])], DIA, body, "U4_XAXIS")
s3 += [mat([CLAMP], "SUS304"), mat([XE + "_FIX", XP + "_FIX"], "Default"),
       act("U1_FRAME"),
       cyl(2.1, 8, [-345, 120, 522], "Y", "RXDC03_BEAM_TAP_1", "cut", [BEAM]),
       cyl(2.1, 8, [-345, 120, 534], "Y", "RXDC03_BEAM_TAP_2", "cut", [BEAM]),
       act("root")]

# ---------- s4: 구름 고리(U4_CABLE_LOOP, J_U4_X 의 1/2) ----------
s4 = [{"command": "component.create", "params": {"name": "U4_CABLE_LOOP", "parent": "root", "activate": True}}]
for y, body, sk in [(71, XE + "_LOOP", "SK_RXDC03_LOOP_ENC"), (79, XP + "_LOOP", "SK_RXDC03_LOOP_PWR")]:
    segs = [('L', [-268.0, y, 384], [-235.0, y, 384]),
            ('A', [-235.0, y, 384], [-170.0, y, 449], [-235.0, y, 514]),
            ('L', [-235.0, y, 514], [-297.5, y, 514])]
    s4 += pipe(sk, segs, DIA, body, "U4_CABLE_LOOP")
s4 += [mat([XE + "_LOOP", XP + "_LOOP"], "Default"), act("root")]

json.dump(s1, open(os.path.join(OUT, 's1_swing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(s2, open(os.path.join(OUT, 's2_block.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(s3, open(os.path.join(OUT, 's3_frame.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(s4, open(os.path.join(OUT, 's4_loop.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print("steps", len(s1), len(s2), len(s3), len(s4))
print("lead ENC %.1f PWR %.1f  surplus %.1f / %.1f" % (LEN_E, LEN_P, 300 - LEN_E, 300 - LEN_P))
print("entry ENC", r(endE, 2), "PWR", r(endP, 2))

# ---------- 전체 기록(edit.json): 자세·모터 돌림·s1~s4·고리 조인트·볼트·다듬기·REST·숨김·저장 ----------
STEP_CB = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/CB5-12/CB5-12.stp"
pre = [{"command": "joint.drive", "params": {"joint": "J_U4_X", "value": 0, "quiet": True}},
       {"command": "joint.drive", "params": {"joint": "J_U4_PRESS", "value": 0, "quiet": True}},
       {"command": "joint.drive", "params": {"joint": "J_U5_X", "value": 0, "quiet": True}},
       {"command": "joint.delete", "params": {"joint": 95400}},
       {"command": "occurrence.move", "params": {"occurrence": "HG-KR23_M02:1", "space": "world", "axis": [1, 0, 0], "angle": "-90 deg", "origin": [-218, 0, 70]}},
       {"command": "joint.rigid_group", "params": {"occurrences": ["U4_PRESS:1", "HG-KR23_M02:1"]}},
       {"command": "material.create", "params": {"name": "PTFE", "density_g_cm3": 2.2, "color": "#f4f4f0"}}]
trim = [act("U4_XCAR"), box(-320, -309, 66, 86, 141, 150, "RXDC03_XCAB_TRIM", op="cut", targets=[XE, XP]), act("root")]
jnt = [{"command": "joint.as_built", "params": {"type": "slider", "a": "U4_XAXIS:1", "b": "U4_CABLE_LOOP:1",
        "at": {"frame": {"origin": [-180, 107, 353], "z": [-1, 0, 0]}}, "name": "J_U4_LOOP", "limits": [[0, 47.5]], "quiet": True}},
       {"command": "joint.motion_link", "params": {"a": "J_U4_X", "b": "J_U4_LOOP", "ratio": 0.5}}]
RM = {'+X': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '+Y': [[0, -1, 0], [1, 0, 0], [0, 0, 1]],
      '+Z': [[0, 0, -1], [0, 1, 0], [1, 0, 0]], '-Z': [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]}
BOLTS = [('CLAMP_1', (-345, 117, 522), '+Y', 'U4_XAXIS:1'), ('CLAMP_2', (-345, 117, 534), '+Y', 'U4_XAXIS:1'),
         ('GUIDE_1', (-249, 80, 150), '+X', 'U4_PRESS:1'), ('GUIDE_2', (-249, 80, 159), '+X', 'U4_PRESS:1'),
         ('T2_1', (-296, 75, 233), '+Z', 'U4_XCAR:1'), ('T2_2', (-286, 75, 233), '+Z', 'U4_XCAR:1'),
         ('RISER_1', (-286, 90, 253), '-Z', 'U4_XCAR:1'), ('RISER_2', (-278, 90, 253), '-Z', 'U4_XCAR:1')]
bol = []
for n, p, dd, g in BOLTS:
    nm = 'CB5-12_RXDC03_' + n
    bol += [{"command": "file.insert_step", "params": {"path": STEP_CB, "name": nm, "matrix": [RM[dd][i] + [p[i]] for i in range(3)]}},
            {"command": "body.rename", "params": {"body": "Cut-Extrude1", "name": nm}},
            mat([nm], "SCM435"),
            {"command": "joint.rigid_group", "params": {"occurrences": [g, nm + ':1']}}]
end = [{"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}},
       {"command": "browser.visibility", "params": {"visible": False, "folder": "joints"}},
       {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
       {"command": "save", "params": {"path": "3D_Modeling/FSAP_v2.29.3.sc"}}]
EDIT = pre + s1 + s2 + trim + s3 + s4 + jnt + bol + end
ED = os.path.join(os.path.dirname(__file__), 'out', 'mech_RX-DC-03')
json.dump(EDIT, open(os.path.join(ED, 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({"base": "3D_Modeling/FSAP_v2.29.3.sc", "result": "3D_Modeling/FSAP_v2.29.3.sc",
           "note": "WF-027: 직전 과제가 형상 변경 없이 v2.29.3으로만 저장 -> 같은 문서에 이어 그리고 같은 이름으로 저장. 기준 형상 = v2.29.2(커밋 9b0966d 기준 v2.29.3). 생성기 tools/gen_rxdc03.py",
           "steps": len(EDIT)}, open(os.path.join(ED, 'edit_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("edit steps", len(EDIT))
