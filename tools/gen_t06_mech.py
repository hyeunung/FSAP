# T06 시작·끝 이음매와 절단(모델링부) 생성기: v0.4.2 -> v0.5.0 (새 묶음 T06·T06_KNIFE, 부 번호 +1)
# 선정 지시서 docs/reports/mechanism/mech_T06_select.md 5절(T06-C1 수정안) 그대로. 다르게 정한 곳은 보고서 2-2절 DEV 표.
# 좌표: 대기 세계 좌표(P-02: 바늘점 원점, 매트 밑면 Z 0, 가장자리 바깥 +Y, 꿰맨 쪽 +X). 단위 mm.
#   * 이 설계의 feature 좌표는 세계 대기 좌표(probe2: 매트·HEAD 하위 컴포넌트에서 center 0 상자 -> 세계 0).
#   * file.insert_step matrix는 3x4 행 우선(부모 로컬) -> root에 넣고 occurrence.reparent(세계 위치 유지).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_t06_mech.py      -> tools/out/mech_T06/model/build.json
#   solidcraft-cli run tools/out/mech_T06/model/build.json --in 3D_Modeling/FSAP_v0.5.0.sc(= v0.4.2 + 설명) --save 3D_Modeling/FSAP_v0.5.0.sc
# 입력: tools/out/mech_T06/model/info0_out.json (v0.4.2 joint.list·motion.list, 동작 연구 키를 다시 짠다)
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T06', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
SHEET = '--no-sheet' not in sys.argv
S = []


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def box(x0, x1, y0, y1, z0, z1, name=None, op=None, targets=None):
    p = {"length": r6(x1 - x0), "width": r6(y1 - y0), "height": r6(z1 - z0),
         "center": [r6((x0 + x1) / 2), r6((y0 + y1) / 2), r6((z0 + z1) / 2)]}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def cylz(d, x, y, z0, z1, name=None, op=None, targets=None):
    cyl(d, [x, y, z0], "Z", z1 - z0, name, op, targets)


def cylx(d, x0, x1, y, z, name=None, op=None, targets=None):
    cyl(d, [min(x0, x1), y, z], "X", abs(x1 - x0), name, op, targets)


def prism(name, sk, origin, xd, yd, pts, dist):
    C("sketch.create", {"plane": {"origin": origin, "x_dir": xd, "y_dir": yd}, "name": sk})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": dist, "body_name": name})


YC = -7.5
XS, XC = 72.0, 108.0          # 안내축·실린더 축 X
KN, AR, BR = "P_T06_KNIFE", "P_T06_ARM", "P_T06_BRACKET"
CY, RO = "STEP대기_CJ2B16-30SZ", "STEP대기_CJ2B16-30SZ_ROD"
LH, SH = "LHFR16_T06", "PSFJ16-100_T06"
c45 = math.cos(math.radians(45))

C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("material.create", {"name": "SK85", "density_g_cm3": 7.85, "color": "#5f6670"})

# ================= 실물 STEP(root에 세계 행렬, 뒤에 reparent) =================
C("component.activate", {"component": "root"})
# LHFR16: STEP +X(플랜지 X0 자리파기 면 -> 몸통 X37) -> 세계 +Z, 플랜지 밑면 Z 77. STEP Y -> (cos45, sin45): 구멍 PCD 38이 45° 자리
C("file.insert_step", {"path": SP + "LHFR16/LHFR16.stp", "name": LH,
                       "matrix": [0, c45, -c45, XS, 0, c45, c45, YC, 1, 0, 0, 77]})
C("body.rename", {"body": "CBORE for Socket Head Cap Screw4", "name": LH})
# PSFJ16-100: STEP +X(길이 0~100) -> 세계 +Z, Z 57~157
C("file.insert_step", {"path": SP + "PSFJ16-100/PSFJ16-100.stp", "name": SH,
                       "matrix": [0, 1, 0, XS, 0, 0, 1, YC, 1, 0, 0, 57]})
C("body.rename", {"body": "Chamfer1", "name": SH})

# ================= T06:1 (HEAD 아래, 고정) =================
C("component.create", {"name": "T06", "parent": "HEAD", "activate": True, "grounded": False})
# P_T06_BRACKET — SUS304 t4 ㄴ자: 세로 다리 X 40~44 · Z 73~140, 가로 판 X 40~122 · Z 73~77, Y -34~+19. 안쪽 R4, 바깥 R8
prism(BR, "SK_T06_BRACKET", [0, 19, 0], [1, 0, 0], [0, 0, 1],
      [(40, 73), (122, 73), (122, 77), (44, 77), (44, 140), (40, 140)], 53)
C("solid.fillet", {"edges": [[44, -7.5, 77]], "radius": 4, "body": BR})
C("solid.fillet", {"edges": [[40, -7.5, 73]], "radius": 8, "body": BR})
for y in (-27.0, 12.0):
    cylx(5.5, 39, 45, y, 130, op="cut", targets=[BR])                       # 헤드 M5 탭 자리 Ø5.5 ×2
cylz(18, XS, YC, 72, 78, op="cut", targets=[BR])                            # 축 Ø18
cylz(10.5, XC, YC, 72, 78, op="cut", targets=[BR])                          # 실린더 보스 Ø10.5
for sx in (1, -1):
    for sy in (1, -1):
        cylz(4.5, XS + sx * 13.435, YC + sy * 13.435, 72, 78, op="cut", targets=[BR])   # LHFR16 M4 ×4
# STEP대기_CJ2B16-30SZ — 60SZ 실측 보수 외곽(E-10, D-37): 튜브 Ø18.3 Z 77~215 + 보스 Ø10 Z 69~77 + 장착 너트 외곽 Ø16.2 Z 69~73
cylz(18.3, XC, YC, 77, 215, CY)
cylz(10, XC, YC, 69, 77, op="join", targets=[CY])
cylz(16.2, XC, YC, 69, 73, op="join", targets=[CY])
cylx(4.13, XC + 9.15 - 6, XC + 9.15 + 0.5, YC, 210, op="cut", targets=[CY])  # 포트 M5 자리(+X, 헤드 끝에서 5: 60SZ 실측)

# ================= T06_KNIFE:1 (T06 아래, J_T06_KNIFE) =================
C("component.create", {"name": "T06_KNIFE", "parent": "T06", "activate": True, "grounded": False})
# P_T06_KNIFE — SK85 t1.5, X 23.25~24.75, 비스듬한 날 (Y -18, Z 27.5) -> (Y +3, Z 29.7)
prism(KN, "SK_T06_KNIFE", [23.25, 0, 0], [0, 1, 0], [0, 0, 1],
      [(-18, 27.5), (3, 29.7), (3, 52.5), (-18, 52.5)], 1.5)
for y in (-12.5, -2.5):
    cylx(5.5, 22.75, 25.25, y, 42, op="cut", targets=[KN])
# P_T06_ARM — SUS304 t3 ㄱ자: 세로 다리 X 24.75~27.75 · Z 36.5~57, 가로 다리 X 24.75~120 · Z 54~57, Y -18~+3. 안쪽 R3, 바깥 R6
prism(AR, "SK_T06_ARM", [0, 3, 0], [1, 0, 0], [0, 0, 1],
      [(24.75, 36.5), (27.75, 36.5), (27.75, 54), (120, 54), (120, 57), (24.75, 57)], 21)
C("solid.fillet", {"edges": [[27.75, -7.5, 54]], "radius": 3, "body": AR})
C("solid.fillet", {"edges": [[24.75, -7.5, 57]], "radius": 6, "body": AR})
for y in (-12.5, -2.5):
    cylx(5.5, 24.25, 28.25, y, 42, op="cut", targets=[AR])                  # 칼 CB5-12 ×2
cylz(6, XC, YC, 53.5, 57.5, op="cut", targets=[AR])                         # 로드 Ø6(띄움)
# STEP대기_CJ2B16-30SZ_ROD — 로드 Ø5 Z 49~69 + 로드 끝 너트 외곽 Ø9.24 Z 50~54(팔 밑)
cylz(5, XC, YC, 49, 69, RO)
cylz(9.24, XC, YC, 50, 54, op="join", targets=[RO])
C("component.activate", {"component": "root"})
C("occurrence.reparent", {"occurrence": LH + ":1", "parent": "T06"})
C("occurrence.reparent", {"occurrence": SH + ":1", "parent": "T06_KNIFE"})

# ================= 판금(M-04, 안내서 '판금'): 굽힘을 R로 그린 바디를 판금으로 =================
if SHEET:
    C("sheet.manage_rules", {"name": "SUS304 t3", "thickness": "3 mm", "bend_radius": "3 mm", "k_factor": "0.44", "active": False})
    C("sheet.manage_rules", {"name": "SUS304 t4", "thickness": "4 mm", "bend_radius": "4 mm", "k_factor": "0.44", "active": False})
    C("sheet.convert", {"body": AR, "face": [90, 0, 57], "rule": "SUS304 t3", "bends": [[r6(30.75 - 3 * c45), -7.5, r6(51 + 3 * c45)]]})
    C("sheet.convert", {"body": BR, "face": [95, 10, 73], "rule": "SUS304 t4", "bends": [[r6(44 + 4 - 4 * c45), -7.5, r6(77 + 4 - 4 * c45)]]})

# ================= HEAD: 침판 칼 받이 홈(관통) + C0.5 =================
C("component.activate", {"component": "HEAD"})
box(23.15, 25.15, -18.5, 3.5, -4.1, -1.0, op="cut", targets=["P_T02_PLATE"])
C("solid.chamfer", {"edges": [[25.15, -7.5, -1.05]], "distance": 0.5, "body": "P_T02_PLATE"})
C("component.activate", {"component": "root"})

# ================= 작업 대상: SCRAP 지우고 SEAM·TAIL(SCRAP이 있던 컴포넌트, 이름 MAT_*_SEAM) =================
SEC = [(-10, -1), (2, -1), (2, 13), (-10, 13), (-10, 12), (1, 12), (1, 0), (-10, 0)]
for key, off in (('LARGE', -100.0), ('SMALL', -600.0), ('GROOVE', -100.0)):
    comp = 'MAT_%s_SCRAP' % key
    C("component.activate", {"component": comp})
    C("solid.remove", {"bodies": ['MAT_%s_SCRAP' % key]})
    prism('MAT_%s_SEAM' % key, 'SK_T06_SEAM_%s' % key, [-30, 0, 0], [0, 1, 0], [0, 0, 1],
          [(y + off, z) for y, z in SEC], 68)
    box(-34.5, -30, 2 + off, 5 + off, 4.5, 5.5, 'MAT_%s_TAIL' % key)
    C("component.activate", {"component": "root"})
    C("component.rename", {"component": comp, "name": 'MAT_%s_SEAM' % key})
    C("component.metadata.set", {"component": 'MAT_%s_SEAM' % key, "bom_type": "reference",
                                 "description": "작업 대상(BOM 밖, 임시값 D-07): 이음매 겹 층 SEAM(④ 자세 로컬 X -30~38, U 껍질 t1, 가장자리 1 들림)·절단 꼬리 TAIL(X -34.5~-30). SEAM은 ④-1a부터, TAIL은 ④-6부터 유효"})

# ================= 재질(E-09) =================
MAT = {BR: "SUS304", AR: "SUS304", KN: "SK85", CY: "Steel", RO: "Steel", LH: "Steel", SH: "Steel"}
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})

# ================= 컴포넌트 속성 =================
PROPS_T06 = {
    BR: "SUS304 / 판금 t4 ㄴ자(굽힘 1, 안쪽 R4) / 세로 다리 X40~44·Z73~140 + 가로 판 X40~122·Z73~77, 폭 Y-34~+19. 구멍: 헤드 Ø5.5 ×2(Y-27·+12, Z130), 축 Ø18, 실린더 보스 Ø10.5, LHFR16 Ø4.5 ×4(45°)",
    CY: "Steel / 구매품 임시 형상(E-10, D-37) / CJ2B16-30SZ: 60SZ 실측 보수 외곽 튜브 Ø18.3 Z77~215 + 보스 Ø10 Z69~77 + 장착 너트 외곽 Ø16.2 Z69~73, 포트 M5 +X(Z210)",
}
PROPS_KN = {
    AR: "SUS304 / 판금 t3 ㄱ자(굽힘 1, 안쪽 R3) / 세로 다리 X24.75~27.75·Z36.5~57 + 가로 다리 X24.75~120·Z54~57, 폭 Y-18~+3. 구멍: 칼 Ø5.5 ×2(Z42), 로드 Ø6(108,-7.5). 축 자리(72,-7.5) 맞닿음만(D-37)",
    KN: "SK85 / 레이저 절단 + 날 연삭·열처리 t1.5 / X23.25~24.75 · Y-18~+3 · Z 날 27.5→29.7(약 6°)~52.5, 구멍 Ø5.5 ×2",
    RO: "Steel / 구매품 임시 형상(E-10, D-37) / CJ2B16-30SZ 로드 Ø5 Z49~69 + 로드 끝 너트(NTJ-015C) 외곽 Ø9.24 Z50~54",
}
C("component.metadata.set", {"component": "T06", "properties": PROPS_T06,
                             "description": "시작·끝 이음매 절단 유닛(T06, 고정 부품). 헤드와 리지드(HEAD 아래). 선정 T06-C1 수정안"})
C("component.metadata.set", {"component": "T06_KNIFE", "properties": PROPS_KN,
                             "description": "T06 가위칼 묶음(조인트 J_T06_KNIFE 직선 Z -30~0, 0 = 올림(스프링), -30 = 절단(공기), 저장 0)"})
C("component.metadata.set", {"component": LH, "part_number": "LHFR16", "bom_type": "purchased",
                             "description": "MISUMI 플랜지붙이 리니어 부시 Ø16 역 카운터보어 (T06 칼 안내, 브래킷 윗면 Z77, 구멍 45°)"})
C("component.metadata.set", {"component": SH, "part_number": "PSFJ16-100", "bom_type": "purchased",
                             "description": "MISUMI 리니어 샤프트 Ø16 L100 (T06 칼 안내축, 팔 윗면 Z57에 맞닿음, 체결 D-37)"})
C("component.metadata.set", {"component": "HEAD", "properties": {
    "P_T02_PLATE": "S50C / 밀링 / 침판 80x50 t3 + 아래 노즈 r8.5 Z -1.05~3.5, 바늘 구멍 Ø2, 칼 받이 관통 홈 2x22(X23.15~25.15·Y-18.5~+3.5) + C0.5(+X 윗모서리)"}})

# ================= 리지드 그룹(E-11, M-07) + 조인트 J_T06_KNIFE =================
C("joint.rigid_group", {"occurrences": ["HEAD:1", "T06:1"]})
JP = [XS, YC, 57.0]
C("joint.create", {"type": "slider", "a": {"occurrence": "T06:1", "point": JP, "z": [0, 0, 1]},
                   "b": {"occurrence": "T06_KNIFE:1", "point": JP, "z": [0, 0, 1]},
                   "flip": True, "name": "J_T06_KNIFE", "limits": [[-30, 0]]})
C("joint.drive", {"joint": "J_T06_KNIFE", "value": 0, "quiet": True})

# ================= 동작 연구(E-15): 사이클 3개에 ④-0~④-7 넣기, 모든 연구에 J_T06_KNIFE =================
A0 = json.load(open(os.path.join(OUT, 'info0_out.json'), encoding='utf-8'))
jn = {j['id']: j['name'] for j in A0[1]['joints']}
REV = {j['name'] for j in A0[1]['joints'] if j['type'] == 'revolute'}
studies = {s['name']: s for s in A0[2]['studies']}
CYC = {'사이클_큰매트': (534, -600.0), '사이클_작은매트': (224, -100.0), '사이클_홈매트': (990, -600.0)}
MAIN = ('J_MAT_X', 'J_MAT_Y', 'J_MAT_ROT', 'J_HEAD_ROT', 'J_PRESSER', 'J_NEEDLE')
ADD = 43
T = [1, 2, 8, 9, 15, 19, 20, 26, 32, 44]


def val(pts, t):
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= t <= b:
            return va if b == a else va + (vb - va) * (t - a) / (b - a)
    return pts[-1][1]


def newv(j, t, y4, v0):
    if j == 'J_MAT_X':
        return {1: 0, 2: 0, 8: 30, 9: 30, 15: 60, 44: 0}.get(t, 60)
    if j == 'J_MAT_Y':
        return y4 if t == 1 else (y4 - 1 if t <= 15 else y4 - 21)
    if j == 'J_PRESSER':
        return 2 if t <= 8 else 10
    if j == 'J_NEEDLE':
        return -30 if t <= 8 else 0
    return v0          # 회전·헤드: ④ 값 그대로


NEWSTEPS = {}
for nm, s in studies.items():
    keys = []
    for kk in s['keys']:
        j = jn[kk['joint']]
        pts = [[a, math.degrees(v) if j in REV else v] for a, v in kk['points']]
        if nm in CYC:
            s4, y4 = CYC[nm]
            v0 = val(pts, s4)
            if j in MAIN:
                assert abs(val(pts, s4) - {'J_MAT_X': 0, 'J_MAT_Y': y4, 'J_PRESSER': 0, 'J_NEEDLE': -30}.get(j, v0)) < 1e-6, (nm, j, v0)
                new = [p for p in pts if p[0] <= s4] + [[s4 + t, newv(j, t, y4, v0)] for t in T] + \
                      [[p[0] + ADD, p[1]] for p in pts if p[0] > s4 + 1]
            else:
                new = [p for p in pts if p[0] <= s4] + [[p[0] + ADD, p[1]] for p in pts if p[0] > s4]
            pts = new
        keys.append({"joint": j, "points": [[a, round(v, 9)] for a, v in pts]})
    steps = s['steps'] + (ADD if nm in CYC else 0)
    if nm in CYC:
        s4 = CYC[nm][0]
        keys.append({"joint": "J_T06_KNIFE", "points": [[0, 0], [s4 + 20, 0], [s4 + 26, -30], [s4 + 32, 0], [steps, 0]]})
    else:
        keys.append({"joint": "J_T06_KNIFE", "points": [[0, 0], [steps, 0]]})
    NEWSTEPS[nm] = steps
    C("motion.study", {"study": nm, "steps": steps, "keys": keys})

C("document.metadata.set", {"values": {"description": "T06 mechanism: lap-stitch seam then CJ2B16 spring-return scissor knife behind needle on PSFJ16 guide + LHFR16, plate slot"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
NEW = {"T06": [BR, CY, LH], "T06_KNIFE": [AR, KN, SH, RO]}
json.dump({"material": MAT, "new": NEW, "made": [BR, AR, KN], "steps": NEWSTEPS, "cyc": CYC, "add": ADD, "t": T},
          open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps', NEWSTEPS)
