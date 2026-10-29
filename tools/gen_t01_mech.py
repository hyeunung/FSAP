# T01 매트 잡기·회전 유닛 모델 생성기 (구동부 모델링, v0.1.0 -> v0.2.1).
# 수정 1회차(2026-10-30, mech_T01_model1.md): v0.2.0과 다른 곳은 둘뿐이다.
#   (1) 동작 연구 키: motion.list는 회전 조인트 값을 rad로 주고 motion.study는 deg로 받는다 -> 회전 조인트 점 값만 math.degrees.
#   (2) P_T01_RING2 t3 -> t5(윗면 -2 유지, Z -7~-2). 띠 Z -12~-7, 링2 샤프트·로드 윗끝 -10 -> -12(띠 밑면에 붙음).
# 원본: tools/out/mech_T01/select/gen_probe.py (선정 지시서 형상). 차이:
#   - 베드·기둥 프로브(P_BED*, P_COL*)는 저장 스크립트에 넣지 않는다(검사 스크립트에만, chk_*.json).
#   - P_T01_POST R20~R30, P_T01_HUB R20~R150 (지시서 값. 프로브는 R12~30 / R32~150이었다).
#   - 스파이더 ㄷ은 웹+다리를 한 바디로(다리를 웹 윗면 -85까지 올려 join).
#   - 재질 지정, 조인트 한계, 컴포넌트 속성(부품별 재질·만드는 법), 대기 0단계로 두고 저장.
# 쓰는 법: python -B tools/gen_t01_mech.py  -> tools/out/mech_T01/model/build.json, chk_*.json
#   build: solidcraft-cli run build.json --in 3D_Modeling/FSAP_v0.1.0.sc --save 3D_Modeling/FSAP_v0.2.1.sc
#   결과 폴더 tools/out/mech_T01/model1 (v0.1.0 기준 자료 a0_out.json은 tools/out/mech_T01/model 것을 읽는다)
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T01', 'model1')
os.makedirs(OUT, exist_ok=True)
A0 = json.load(open(os.path.join(ROOT, 'tools', 'out', 'mech_T01', 'model', 'a0_out.json'), encoding='utf-8'))  # v0.1.0: [document.inspect, joint.list, motion.list, material.list]
AX = (0.0, -700.0)
S = []
C = lambda c, p: S.append({"command": c, "params": p})
MAT = {}      # body -> material
PROP = {}     # component -> {body: "재질 / 만드는 법"}


def reg(comp, body, mat, how=None):
    MAT[body] = mat
    if how:
        PROP.setdefault(comp, {})[body] = how


def polar(r, th):
    t = math.radians(th)
    return (AX[0] + r * math.cos(t), AX[1] + r * math.sin(t))


def cyl(r, rr, th, z0, z1, name, op=None, targets=None):
    x, y = polar(rr, th) if rr else AX
    p = {"radius": r, "height": round(z1 - z0, 4), "base": [round(x, 4), round(y, 4), z0]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def annulus(r0, r1, z0, z1, name):
    cyl(r1, 0, 0, z0, z1, name)
    cyl(r0, 0, 0, z0 - 1, z1 + 1, None, op="cut", targets=[name])


def quad(r0, r1, w0, w1, th):
    t = math.radians(th)
    ux, uy = math.cos(t), math.sin(t)
    vx, vy = -uy, ux
    return [[round(AX[0] + a * ux + b * vx, 4), round(AX[1] + a * uy + b * vy, 4)]
            for (a, b) in ((r0, w0), (r1, w0), (r1, w1), (r0, w1))]


def prism(polys, z0, z1, name, sk, op=None, targets=None):
    C("sketch.create", {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    for pts in polys:
        for i in range(len(pts)):
            C("sketch.line", {"points": [pts[i], pts[(i + 1) % len(pts)]]})
    C("sketch.finish", {})
    p = {"sketch": sk, "profiles": "all", "distance": round(z1 - z0, 4)}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.extrude", p)


def box(x0, x1, y0, y1, z0, z1, name, op=None, targets=None):
    p = {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0,
         "center": [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


TH3 = (90.0, 210.0, 330.0)   # 스파이더 팔·실린더 각(MAT_ROT 기준, +X에서 반시계). 90 = 대기 때 +Y
TH6 = tuple(90.0 + 60 * i for i in range(6))
SIDE = {-150: "L", 150: "R"}

# ---------- 재질(없는 것만 만든다) ----------
for nm, rho, col in (("Rigid 10K", 1.65, "#d8d8d0"), ("PET-CF", 1.29, "#303030"),
                     ("SUS304", 7.93, "#b8bcc0"), ("A5052", 2.68, "#c8ccd4")):
    C("material.create", {"name": nm, "density_g_cm3": rho, "color": col})

# ---------- MAT_ROT (회전부) ----------
C("component.activate", {"component": "MAT_ROT"})
cyl(55, 0, 0, -12.5, -0.5, "P_T01_DISC")
reg("MAT_ROT", "P_T01_DISC", "Rigid 10K", "Rigid 10K / SLA Form 3 / 진공 원판 R55 t12")
annulus(20, 30, -235, -12.5, "P_T01_POST")
reg("MAT_ROT", "P_T01_POST", "PET-CF", "PET-CF / FDM H2C / 중공 기둥 Ø60/Ø40")
annulus(20, 150, -241, -235, "P_T01_HUB")
reg("MAT_ROT", "P_T01_HUB", "SUS304", "SUS304 / 레이저 평판 t6")
for i, th in enumerate(TH3):
    n = "P_T01_SPIDER_%d" % (i + 1)
    # ㄷ 단면(접선 a, 높이 Z)을 팔 시작 r100의 반경 방향 평면에 그려 r100->r490(390) 밀어낸다: 한 바디
    t = math.radians(th)
    u = (math.cos(t), math.sin(t)); v = (-u[1], u[0])
    o = (AX[0] + 100 * u[0], AX[1] + 100 * u[1])
    C("sketch.create", {"plane": {"origin": [round(o[0], 4), round(o[1], 4), 0], "x_dir": [round(v[0], 6), round(v[1], 6), 0],
                                  "y_dir": [0, 0, 1]}, "name": "SK_" + n})
    pts = [(-30, -235), (-27, -235), (-27, -88), (27, -88), (27, -235), (30, -235), (30, -85), (-30, -85)]
    for j in range(len(pts)):
        C("sketch.line", {"points": [list(pts[j]), list(pts[(j + 1) % len(pts)])]})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": "SK_" + n, "profiles": "all", "distance": 390, "body_name": n})
    for rr, hr in ((190, 9.5), (410, 9.5), (240, 14.5), (460, 14.5)):
        cyl(hr, rr, th, -90, -83, None, op="cut", targets=[n])
    reg("MAT_ROT", n, "SUS304", "SUS304 / 판금 t3 ㄷ(곧은 절곡 2회)")
    for rr, tag in ((190, "R1"), (410, "R2")):
        nb = "STEP대기_CJ2B16-60S_%s_%d" % (tag, i + 1)
        cyl(9, rr, th, -215, -85, nb)
        reg("MAT_ROT", nb, "Steel")
    for rr, tag in ((240, "R1"), (460, "R2")):
        nb = "STEP대기_LHFR16_%s_%d" % (tag, i + 1)
        cyl(14, rr, th, -122, -85, nb)
        cyl(24, rr, th, -85, -80, None, op="join", targets=[nb])
        cyl(8.5, rr, th, -123, -79, None, op="cut", targets=[nb])
        reg("MAT_ROT", nb, "Steel")
C("component.activate", {"component": "root"})

# ---------- RING1 / RING2 (새 루트 컴포넌트 + 직선 조인트) ----------
for nm in ("RING1", "RING2"):
    C("component.create", {"name": nm, "activate": True, "grounded": False})
    if nm == "RING1":
        annulus(75, 300, -10.5, -0.5, "P_T01_RING1")
        reg(nm, "P_T01_RING1", "A5052", "A5052 / 밀링 / 진공 링 R75~R300 t10")
        for i, th in enumerate(TH3):
            b1 = "STEP대기_PSFJ16-150_R1_%d" % (i + 1)
            b2 = "STEP대기_CJ2B16-60S_ROD_R1_%d" % (i + 1)
            cyl(8, 240, th, -160.5, -10.5, b1)
            cyl(2.5, 190, th, -85, -10.5, b2)
            reg(nm, b1, "Steel"); reg(nm, b2, "Steel")
    else:
        annulus(310, 520, -7, -2, "P_T01_RING2")
        reg(nm, "P_T01_RING2", "A5052", "A5052 / 레이저 평판 / 받침 링 R310~R520 t5")
        for i, th in enumerate(TH6):
            b = "P_T01_RING2_STRAP_%d" % (i + 1)
            prism([quad(320, 515, -20, 20, th)], -12, -7, b, "SK_STRAP_%d" % (i + 1))
            reg(nm, b, "A5052", "A5052 / 레이저 평판 / 띠 40×195 t5")
        for i, th in enumerate(TH3):
            b1 = "STEP대기_PSFJ16-150_R2_%d" % (i + 1)
            b2 = "STEP대기_CJ2B16-60S_ROD_R2_%d" % (i + 1)
            cyl(8, 460, th, -162, -12, b1)
            cyl(2.5, 410, th, -85, -12, b2)
            reg(nm, b1, "Steel"); reg(nm, b2, "Steel")
    C("component.activate", {"component": "root"})
    C("joint.create", {"type": "slider", "a": {"occurrence": "MAT_ROT:1", "point": [AX[0], AX[1], 0], "z": [0, 0, 1]},
                       "b": {"occurrence": nm + ":1", "point": [AX[0], AX[1], 0], "z": [0, 0, 1]},
                       "flip": True, "name": "J_" + nm, "limits": [[-60, 0]]})

# ---------- MAT_Y ----------
C("component.activate", {"component": "MAT_Y"})
box(-100, 100, AX[1] - 100, AX[1] + 100, -341, -241, "STEP대기_DGM200R-AZAC")
box(-45, 45, AX[1] - 260, AX[1] - 100, -336, -246, None, op="join", targets=["STEP대기_DGM200R-AZAC"])
reg("MAT_Y", "STEP대기_DGM200R-AZAC", "Steel")
box(-200, 200, AX[1] - 250, AX[1] + 250, -356, -341, "P_T01_YPLATE")
reg("MAT_Y", "P_T01_YPLATE", "A5052", "A5052 / 밀링 / Y 이동판 400×500 t15")
k = 0
for sx in (-150, 150):
    for sy in (-160, 160):
        k += 1
        b = "STEP대기_SV2R20-1300_BLK_%d" % k
        box(sx - 22, sx + 22, AX[1] + sy - 36, AX[1] + sy + 36, -380, -356, b)
        reg("MAT_Y", b, "Steel")
C("component.activate", {"component": "root"})

# ---------- MAT_X ----------
C("component.activate", {"component": "MAT_X"})
for sx in (-150, 150):
    b1 = "STEP대기_SV2R20-1300_%s" % SIDE[sx]
    b2 = "STEP대기_HFS8-4080-1300_%s" % SIDE[sx]
    box(sx - 10, sx + 10, -1060, 240, -398, -380, b1)
    box(sx - 20, sx + 20, -1060, 240, -478, -398, b2)
    reg("MAT_X", b1, "Steel"); reg("MAT_X", b2, "Aluminum")
k = 0
for cy, tag in ((-1000, "F"), (180, "B")):
    b = "STEP대기_HFS8-4080-460_%s" % tag
    box(-230, 230, cy - 20, cy + 20, -558, -478, b)
    reg("MAT_X", b, "Aluminum")
    for sx in (-180, 180):
        k += 1
        bb = "STEP대기_SV2R20-1800_BLK_%d" % k
        box(sx - 36, sx + 36, cy - 22, cy + 22, -582, -558, bb)
        reg("MAT_X", bb, "Steel")
C("component.activate", {"component": "root"})

# ---------- BASE ----------
C("component.activate", {"component": "BASE"})
for cy, tag in ((-1000, "F"), (180, "B")):
    b1 = "STEP대기_SV2R20-1800_%s" % tag
    b2 = "STEP대기_HFS8-4080-1900_%s" % tag
    box(-900, 900, cy - 10, cy + 10, -600, -582, b1)
    box(-950, 950, cy - 20, cy + 20, -680, -600, b2)
    reg("BASE", b1, "Steel"); reg("BASE", b2, "Aluminum")
C("component.activate", {"component": "root"})

# ---------- 재질 지정 ----------
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})

# ---------- 컴포넌트 속성(가공품의 재질·만드는 법, E-09) ----------
DESC = {"RING1": "T01 진공 링1(R75~R300), 단동 실린더로 60 내림",
        "RING2": "T01 받침 링2(R310~R520), 단동 실린더로 60 내림"}
for comp, props in PROP.items():
    p = {"component": comp, "properties": props}
    if comp in DESC:
        p["description"] = DESC[comp]
    C("component.metadata.set", p)

# ---------- 조인트 한계 ----------
C("joint.limits", {"joint": "J_MAT_X", "min": -620, "max": 620})
C("joint.limits", {"joint": "J_MAT_Y", "min": -860, "max": 40})

# ---------- 동작 연구에 링 키를 더한다(motion.study 편집은 키를 통째로 바꾸므로 기존 키를 그대로 다시 넣음) ----------
jn = {j['id']: j['name'] for j in A0[1]['joints']}
REV = {j['name'] for j in A0[1]['joints'] if j['type'] == 'revolute'}   # motion.list rad -> motion.study deg
RK = {
    '대기': ([[0, 0], [1, 0]], [[0, 0], [1, 0]]),
    '사이클_큰매트': ([[0, 0], [540, 0]], [[0, 0], [540, 0]]),
    '사이클_작은매트': ([[0, -60], [255, -60]], [[0, 0], [6, 0], [7, -60], [250, -60], [251, 0], [255, 0]]),
    '사이클_홈매트': ([[0, 0], [996, 0]], [[0, 0], [429, 0], [430, -60], [734, -60], [735, 0], [996, 0]]),
    '상태_홈매트_홈': ([[0, 0], [461, 0]], [[0, 0], [15, 0], [16, -60], [461, -60]]),
    '상태_홈매트_오목모서리': ([[0, 0], [93, 0]], [[0, 0], [93, 0]]),
    '상태_큰매트_볼록모서리': ([[0, 0], [92, 0]], [[0, 0], [92, 0]]),
}
studies = {s['name']: s for s in A0[2]['studies']}
assert set(RK) == set(studies), (set(RK), set(studies))
for nm, (k1, k2) in RK.items():
    s = studies[nm]
    keys = [{"joint": jn[kk['joint']],
             "points": [[a, round(math.degrees(v), 9)] for a, v in kk['points']] if jn[kk['joint']] in REV else kk['points']}
            for kk in s['keys']]
    keys += [{"joint": "J_RING1", "points": k1}, {"joint": "J_RING2", "points": k2}]
    C("motion.study", {"study": nm, "steps": s['steps'], "keys": keys})
std = {jn[kk['joint']]: kk['points'][0][1] for kk in studies['대기']['keys']}
rw = [{"joint": j, "points": [[0, v], [72, v]]} for j, v in std.items() if j != 'J_MAT_ROT']
rw += [{"joint": "J_MAT_ROT", "points": [[0, -360], [72, 0]]},
       {"joint": "J_RING1", "points": [[0, 0], [72, 0]]}, {"joint": "J_RING2", "points": [[0, 0], [72, 0]]}]
C("motion.study", {"name": "되감기", "steps": 72, "keys": rw})

# ---------- 문서 설명, 저장 자세 ----------
C("document.metadata.set", {"values": {"description": "T01 mechanism rev1: vacuum disc + 2 vacuum/support rings on DGM200R rotary, X/Y rails (STEP placeholders); rotary keys in deg, ring2 t5"}})
C("motion.play", {"study": "대기", "step": 0})
json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({"material": MAT, "props": PROP}, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# =================== 검사 스크립트(저장본 v0.2.0에 대고, --save 없이) ===================
PRB = []
for nm, (x0, x1, y0, y1, z0, z1) in (("P_BED", (-50, 50, -30, 660, -40, -0.5)),
                                    ("P_COL", (-75, 75, 660, 860, -950, 300))):
    PRB.append({"command": "component.create", "params": {"name": nm, "grounded": True, "activate": True}})
    PRB.append({"command": "solid.box", "params": {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0,
                                                   "center": [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2], "body_name": nm}})
    PRB.append({"command": "component.activate", "params": {"component": "root"}})
T01 = ["MAT_ROT:1", "RING1:1", "RING2:1", "MAT_Y:1", "MAT_X:1"]
PROBES = ["P_BED:1", "P_COL:1"]
MATOF = {'사이클_큰매트': 'LARGE', '상태_큰매트_볼록모서리': 'LARGE', '사이클_작은매트': 'SMALL',
         '사이클_홈매트': 'GROOVE', '상태_홈매트_홈': 'GROOVE', '상태_홈매트_오목모서리': 'GROOVE'}
names = ['대기'] + list(MATOF) + ['되감기']
for i, nm in enumerate(names):
    ex = list(PRB)
    ex.append({"command": "motion.interference", "params": {"study": nm, "occurrences": T01, "against": PROBES, "budget_s": 1500}})
    if nm in MATOF:
        kk = MATOF[nm]
        ex.append({"command": "motion.interference", "params": {
            "study": nm, "occurrences": ["MAT_%s:1" % kk, "MAT_%s_BOUND:1" % kk, "MAT_%s_SCRAP:1" % kk],
            "against": T01 + ["BASE:1"], "budget_s": 1500}})
    ex.append({"command": "motion.interference", "params": {"study": nm, "occurrences": ["RING1:1", "RING2:1"],
                                                            "against": ["MAT_ROT:1", "MAT_Y:1", "MAT_X:1"], "budget_s": 1500}})
    ex.append({"command": "motion.interference", "params": {"study": nm, "occurrences": ["MAT_ROT:1", "MAT_Y:1", "MAT_X:1"],
                                                            "against": ["BASE:1"], "budget_s": 1500}})
    ex.append({"command": "motion.interference", "params": {"study": nm, "occurrences": ["MAT_ROT:1"],
                                                            "against": ["MAT_Y:1", "MAT_X:1"], "budget_s": 1500}})
    ex.append({"command": "motion.interference", "params": {"study": nm, "occurrences": ["MAT_Y:1"],
                                                            "against": ["MAT_X:1"], "budget_s": 1500}})
    ex.append({"command": "motion.play", "params": {"study": "대기", "step": 0}})
    json.dump(ex, open(os.path.join(OUT, 'chk_study_%d.json' % i), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(names, open(os.path.join(OUT, 'chk_names.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# 정적 검사: 문서, 조인트, 바디 측정, 전수 겹침, 자세 확인, 빈 공간 프로브
st = [{"command": "document.inspect", "params": {"measure": True}},
      {"command": "joint.list", "params": {}},
      {"command": "motion.list", "params": {}},
      {"command": "inspect.interference", "params": {"budget_s": 1200}}]
for o in ("MAT_ROT:1", "RING1:1", "RING2:1", "MAT_Y:1", "MAT_X:1", "BASE:1"):
    st.append({"command": "occurrence.properties", "params": {"occurrence": o}})
for comp in ("MAT_ROT", "RING1", "RING2", "MAT_Y", "MAT_X", "BASE"):
    st.append({"command": "component.metadata", "params": {"component": comp}})
st.append({"command": "motion.play", "params": {"study": "사이클_작은매트", "step": 100}})
for o in ("RING1:1", "RING2:1"):
    st.append({"command": "occurrence.properties", "params": {"occurrence": o, "descendants": False}})
st.append({"command": "motion.play", "params": {"study": "대기", "step": 0}})
# 비워 둘 공간 프로브(PM 예외 판정 T01-X01~X04): Y 묶음 공간은 MAT_X 안 X ±100 · Y -1300~+260 · Z -478~-356
# (200×1560×122, 중심 (0,-520,-417)), X 묶음 공간은 바닥 고정 X -1150~950 · Y -470~-350 · Z -580~-480.
# J_MAT_Y -860·0·+40에서 잰다(저장하지 않음).
st += [{"command": "component.activate", "params": {"component": "MAT_X"}},
       {"command": "solid.box", "params": {"length": 200, "width": 1560, "height": 122, "center": [0, -520, -417], "body_name": "VOID_Y"}},
       {"command": "component.activate", "params": {"component": "root"}},
       {"command": "component.create", "params": {"name": "P_VOID", "grounded": True, "activate": True}},
       {"command": "solid.box", "params": {"length": 2100, "width": 120, "height": 100, "center": [-100, -410, -530], "body_name": "VOID_X"}},
       {"command": "component.activate", "params": {"component": "root"}}]
for yv in (-860, 0, 40):
    st += [{"command": "joint.drive", "params": {"joint": "J_MAT_Y", "value": yv}},
           {"command": "inspect.interference", "params": {"bodies": ["VOID_Y", "VOID_X"] + list(MAT), "budget_s": 600}}]
st.append({"command": "motion.play", "params": {"study": "대기", "step": 0}})
json.dump(st, open(os.path.join(OUT, 'chk_static.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# 해석용 임시 STEP(E-06 예외): 새로 힘을 받는 가공품
MADE = [b for b in MAT if b.startswith('P_T01_')]
EXP = [b for b in MADE if b.startswith('P_T01_RING2')]   # 이번 회차에 두께·자리가 바뀐 하중 부품
ex = [{"command": "file.export", "params": {"path": os.path.join(OUT, '..', 'stepout', b + '.step').replace('\\', '/'),
                                            "format": "step", "bodies": [b]}} for b in EXP]
json.dump(ex, open(os.path.join(OUT, 'export_step.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(MADE, open(os.path.join(OUT, 'made.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(S), 'build commands;', len(MAT), 'bodies;', len(MADE), 'made')
