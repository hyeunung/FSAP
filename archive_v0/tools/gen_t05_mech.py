# T05 테이프 공급·장력 유닛 모델링(모델링부) 생성기: v0.3.2 -> v0.4.0
# 선정 지시서 docs/reports/mechanism/mech_T05_select.md 6절(T05-S01~S08) 그대로. 지시와 다르게 정한 곳은 DEV 표(보고서 2-2절).
# 좌표: 대기 자세 세계 좌표(바늘점 원점, 매트 밑면 Z 0, 가장자리 바깥 +Y, 바늘 앞 -X). 단위 mm.
# 출력: tools/out/mech_T05/model/build.json
#   solidcraft-cli run build.json --in 3D_Modeling/FSAP_v0.3.2.sc --save 3D_Modeling/FSAP_v0.4.0.sc
import json, os, math

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_T05', 'model')
os.makedirs(OUT, exist_ok=True)
S = []


def C(cmd, params):
    S.append({"command": cmd, "params": params})


def r4(v):
    return round(v, 4)


def box(x0, x1, y0, y1, z0, z1, name=None, op=None, targets=None):
    p = {"length": r4(x1 - x0), "width": r4(y1 - y0), "height": r4(z1 - z0),
         "center": [r4((x0 + x1) / 2), r4((y0 + y1) / 2), r4((z0 + z1) / 2)]}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r4(h), "base": [r4(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def cylx(d, x0, x1, y, z, name=None, op=None, targets=None):
    a, b = min(x0, x1), max(x0, x1)
    cyl(d, [a, y, z], "X", b - a, name, op, targets)


def cyly(d, x, y0, y1, z, name=None, op=None, targets=None):
    a, b = min(y0, y1), max(y0, y1)
    cyl(d, [x, a, z], "Y", b - a, name, op, targets)


def cylz(d, x, y, z0, z1, name=None, op=None, targets=None):
    cyl(d, [x, y, z0], "Z", z1 - z0, name, op, targets)


def prism_z(pts, z0, h, sk, target):
    """XY 다각형(세계 X,Y)을 Z z0에서 +h 밀어 target에 join"""
    C("sketch.create", {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    C("sketch.line", {"points": [[r4(x), r4(y)] for x, y in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": h, "operation": "join", "targets": [target]})


# ---------------- 테이프 길 기준(지시서 6-1·6-3) ----------------
K = 0.197
SK = math.sqrt(1 + K * K)
ALPHA = math.degrees(math.atan(K))          # +11.145: 길 방향 (-0.193, 0.981)에 맞춤(DEV-1)
W = (math.cos(math.radians(ALPHA)), math.sin(math.radians(ALPHA)), 0.0)   # 폭 방향(길에 수직) (0.981, 0.193)


def xc(y): return -22.0 - K * (y - 40.0)
def zc(y): return 43.0 - 0.5 * (y - 40.0) / 515.0
def phi(y): return 90.0 * (555.0 - y) / 515.0


PL, HO, SH, HU, CA, GU, CY = ("P_T05_PLATE", "P_T05_HOLDER", "STEP대기_PSFJ16-100", "P_T05_HUB", "P_T05_CAP",
                              "P_T05_GUIDE", "STEP대기_CJ2B10-15")
PA, RO = "P_T05_PAD", "STEP대기_CJ2B10-15_ROD"
TR, TP = "MAT_TAPE_ROLL", "MAT_TAPE_PATH"

C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ================= T05:1 (HEAD 아래, 고정) =================
C("component.create", {"name": "T05", "parent": "HEAD", "activate": True, "grounded": False})

# 1) P_T05_PLATE — SUS304 t3 레이저 평판, X -78~-75, L자
C("sketch.create", {"plane": {"origin": [-78, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, "name": "SK_T05_PLATE"})
C("sketch.line", {"points": [[560, 30], [850, 30], [850, 245], [620, 245], [620, 100], [560, 100]], "closed": True})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T05_PLATE", "profiles": "all", "distance": 3, "body_name": PL})
C("solid.fillet", {"edges": [[-76.5, 560, 30], [-76.5, 850, 30], [-76.5, 850, 245], [-76.5, 620, 245],
                             [-76.5, 560, 100], [-76.5, 620, 100]], "radius": 5, "body": PL})
for (y, z) in ((730, 180), (770, 180), (730, 220), (770, 220), (640, 45), (840, 45), (570, 50), (600, 80)):
    cylx(5.5, -79, -74, y, z, op="cut", targets=[PL])

# 2) P_T05_HOLDER — PET-CF FDM
box(-88, -78, 722, 778, 172, 228, HO)                                   # 플랜지 56x56x10
cylx(36, -110, -88, 750, 200, op="join", targets=[HO])                   # 보스 Ø36
box(-108, -92, 736, 764, 214, 228, op="join", targets=[HO])              # 클램프 귀
cylx(16, -110.5, -80, 750, 200, op="cut", targets=[HO])                  # 축 구멍 Ø16 (X -78~-80 막힌 바닥)
box(-110.5, -90, 749.25, 750.75, 205, 229, op="cut", targets=[HO])       # 슬릿 폭 1.5
for (y, z) in ((730, 180), (770, 180), (730, 220), (770, 220)):
    cylx(5.5, -89, -77, y, z, op="cut", targets=[HO])                    # CB5-16 관통
    cylx(10, -89, -82.5, y, z, op="cut", targets=[HO])                   # 카운터보어 Ø10 깊이 5.5
cyly(5.5, -100, 735, 765, 222, op="cut", targets=[HO])                   # 클램프 CB5 관통
cyly(10, -100, 735, 741.5, 222, op="cut", targets=[HO])                  # -Y 카운터보어 깊이 5.5
cyly(6.4, -100, 756, 765, 222, op="cut", targets=[HO])                   # +Y M5 열압입 인서트 자리 Ø6.4 x 8

# 3) STEP대기_PSFJ16-100 — Ø16 x 100
cylx(16, -180, -80, 750, 200, SH)

# 4) P_T05_HUB — PET-CF
cylx(200, -113.5, -110.5, 750, 200, HU)
cylx(76, -150, -113.5, 750, 200, op="join", targets=[HU])
cylx(16.3, -151, -110, 750, 200, op="cut", targets=[HU])

# 5) P_T05_CAP — PET-CF (클램프는 Ø50 외곽 안: DEV-5)
cylx(90, -154, -150, 750, 200, CA)
cylx(50, -166, -154, 750, 200, op="join", targets=[CA])
cylx(16, -167, -149, 750, 200, op="cut", targets=[CA])
box(-167, -154, 749.25, 750.75, 205, 226, op="cut", targets=[CA])        # 슬릿 폭 1.5 (보스만)
cyly(10, -160, 723, 741, 217, op="cut", targets=[CA])                    # -Y 카운터보어
cyly(5.5, -160, 740, 777, 217, op="cut", targets=[CA])                   # CB5 관통
cyly(6.4, -160, 760, 777, 217, op="cut", targets=[CA])                   # +Y M5 인서트 자리

# 6) P_T05_GUIDE — PET-CF FDM C틀 한 덩어리
box(-152, -78, 553, 600, 36, 42, GU)                                     # 밑판(받침면 윗면 Z 42)
box(-88, -78, 553, 612, 36, 92, op="join", targets=[GU])                 # 등판
box(-147, -78, 555, 595, 82, 92, op="join", targets=[GU])                # 위판(보스)
box(-147, -88, 555, 562.2, 45, 82, op="join", targets=[GU])              # 패드 주머니 앞벽(밑 Z 42~45 테이프 틈)
box(-147, -88, 582.8, 588, 45, 82, op="join", targets=[GU])              # 패드 주머니 뒷벽


def wall(d0, d1, y0, y1):
    return [(xc(y0) + d0 * SK, y0), (xc(y0) + d1 * SK, y0), (xc(y1) + d1 * SK, y1), (xc(y1) + d0 * SK, y1)]


prism_z(wall(16.5, 19.5, 553, 612), 42, 20, "SK_T05_WALL_P", GU)           # +X 옆벽 t3
prism_z(wall(-19.5, -16.5, 553, 562.2), 42, 20, "SK_T05_WALL_M1", GU)      # -X 옆벽(주머니 앞)
# -X 옆벽(주머니 뒤 ~ 막대 끝): 바깥선이 외곽 X -152를 넘는 곳(Y > 599.0)은 X -152에서 자른 5각형(외곽 intersect 대신)
Y152 = 40.0 + (-22.0 + 152.0 - 19.5 * SK) / K          # 외곽선이 X -152와 만나는 Y(약 599.0)
prism_z([(xc(582.8) - 16.5 * SK, 582.8), (xc(582.8) - 19.5 * SK, 582.8), (-152.0, Y152), (-152.0, 606), (xc(606) - 16.5 * SK, 606)],
        42, 20, "SK_T05_WALL_M2", GU)
RC = (-132.3, 600.0, 51.0)
cyl(16, [RC[0] - 18.5 * W[0], RC[1] - 18.5 * W[1], RC[2]], [r4(W[0]), r4(W[1]), 0], 37, op="join", targets=[GU])  # 막대 r8
cylz(8.2, -131, 572.5, 81, 93, op="cut", targets=[GU])                   # 실린더 장착 구멍 Ø8.2
for (y, z) in ((570, 50), (600, 80)):
    cylx(6.4, -86, -77, y, z, op="cut", targets=[GU])                    # M5 열압입 인서트 자리 Ø6.4 x 8(+X 면)

# 7) STEP대기_CJ2B10-15 (튜브·장착 나사·너트, 보수 외곽 D-33)
cylz(16, -131, 572.5, 92, 162, CY)
cylz(8, -131, 572.5, 82, 92, op="join", targets=[CY])
cylz(16, -131, 572.5, 76, 82, op="join", targets=[CY])
cylz(4.4, -131, 572.5, 75, 93, op="cut", targets=[CY])                   # 로드 구멍(로드가 행정 내내 들어가 있음, DEV-3)
for z in (100, 152):
    cylx(4.2, -140, -135, 572.5, z, op="cut", targets=[CY])              # 포트 M5 자리(-X)

# ================= T05_PAD:1 (T05 아래, J_T05_PAD) =================
C("component.create", {"name": "T05_PAD", "parent": "T05", "activate": True, "grounded": False})
box(-145, -117, 562.5, 582.5, 55.5, 61.5, PA)                           # 패드 28x20x6 (조인트 0 = 올림)
box(-146, -127, 570.3, 574.7, 59.5, 62, op="cut", targets=[PA])          # T홈 목 4.4 (윗면, -X로 열림)
box(-146, -127, 568.8, 576.2, 57, 59.5, op="cut", targets=[PA])          # T홈 머리 7.4 (로드 끝 너트)
cylz(4, -131, 572.5, 61.5, 92, RO)                                       # 로드 Ø4 (DEV-3: 82 -> 92)
C("component.activate", {"component": "root"})

# ================= T05_TAPE:1 (HEAD 아래, 작업 대상 외피, BOM 밖) =================
C("component.create", {"name": "T05_TAPE", "parent": "HEAD", "activate": True, "grounded": False})
cylx(194, -146.5, -114.5, 750, 200, TR)
cylx(76, -147, -114, 750, 200, op="cut", targets=[TR])

# ② 비틀린 경간(10 mm 조각, Y 40.5 -> 552.5)
SPAN = []
y = 40.5; i = 0
while y < 552.5 - 1e-9:
    yb = min(y + 10.0, 552.5); ym = (y + yb) / 2
    ls = (yb - y) * SK + 0.6
    nm = TP if i == 0 else 'T5_SPAN_%02d' % i
    C("solid.box", {"length": 32, "width": r4(ls), "height": 1, "center": [0, 0, 0], "body_name": nm})
    C("solid.move", {"bodies": [nm], "axis": [0, 1, 0], "angle": "%.6f deg" % phi(ym)})
    C("solid.move", {"bodies": [nm], "axis": [0, 0, 1], "angle": "%.6f deg" % ALPHA,
                     "translate": [r4(xc(ym)), r4(ym), r4(zc(ym))]})
    SPAN.append(nm); y = yb; i += 1

# ① 내려오는 테이프(롤 -> 막대 뒤): 가득 롤 R 96.5, 막대 r 8.5 교차 접선(gen_sel.py와 같음)
c1 = (750.0, 200.0); c2 = (600.0, 51.0); R, r2 = 96.5, 8.5
D = (c1[0] - c2[0], c1[1] - c2[1]); L = math.hypot(*D); u = (D[0] / L, D[1] / L)
best = None
for s in (1, -1):
    a = s * math.acos((R + r2) / L)
    n = (u[0] * math.cos(a) - u[1] * math.sin(a), u[0] * math.sin(a) + u[1] * math.cos(a))
    p1 = (c1[0] - R * n[0], c1[1] - R * n[1]); p2 = (c2[0] + r2 * n[0], c2[1] + r2 * n[1])
    if p1[0] < 750 and p2[0] > 600:
        best = (p1, p2)
p_roll, p_rod = best
LEN = math.hypot(p_roll[0] - p_rod[0], p_roll[1] - p_rod[1])
ANG = math.degrees(math.atan2(p_roll[1] - p_rod[1], p_roll[0] - p_rod[0]))
e = ((p_roll[0] - p_rod[0]) / LEN, (p_roll[1] - p_rod[1]) / LEN)
# DEV-2: 아래 끝은 옆벽 윗면 Z 62 위(최저점 Z >= 62.5)에서, 위 끝은 롤 외피(r 97)를 벗어난 곳(접점에서 14.5)에서 자른다
half_t_z = 0.5 * abs(e[0])                     # 두께 1의 모서리 Z 편차
s0 = (62.5 + half_t_z - p_rod[1]) / e[1]
s1 = LEN - 14.5
pa = (p_rod[0] + s0 * e[0], p_rod[1] + s0 * e[1]); pb = (p_rod[0] + s1 * e[0], p_rod[1] + s1 * e[1])
DL = s1 - s0
C("solid.box", {"length": 32, "width": r4(DL), "height": 1, "center": [0, 0, 0], "body_name": "T5_DROP"})
C("solid.move", {"bodies": ["T5_DROP"], "axis": [1, 0, 0], "angle": "%.6f deg" % ANG,
                 "translate": [-130.5, r4((pa[0] + pb[0]) / 2), r4((pa[1] + pb[1]) / 2)]})
C("solid.combine", {"target": TP, "tools": SPAN[1:] + ["T5_DROP"], "operation": "join"})
C("component.activate", {"component": "root"})

# ================= 재질(E-09) =================
MAT = {PL: "SUS304", HO: "PET-CF", HU: "PET-CF", CA: "PET-CF", GU: "PET-CF", PA: "PET-CF",
       SH: "Steel", CY: "Steel", RO: "Steel"}
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})

# ================= 컴포넌트 속성 =================
PROPS_T05 = {
    PL: "SUS304 / 판금(레이저 평판, 굽힘 0) t3 / L자 Y560~850·Z30~100 + Y620~850·Z100~245, R5, 구멍 Ø5.5 x8. 기둥 -X 면 X -75에 맞댐",
    HO: "PET-CF / FDM H2C / 플랜지 56x56x10 + 보스 Ø36 L22 + 클램프 귀, 축 구멍 Ø16(바닥 막힘 2), CB5-16 x4 머리 묻힘(Ø10 깊이 5.5), 클램프 CB5 + M5 인서트",
    SH: "Steel / 구매품 임시 형상(E-10, D-34) / Ø16 L100 스트레이트 축",
    HU: "PET-CF / FDM H2C / 플랜지 Ø200 t3 + 심 Ø76 L36.5, 구멍 Ø16.3",
    CA: "PET-CF / FDM H2C / 원판 Ø90 t4 + 클램프 보스 Ø50 L12(슬릿 1.5, CB5 + M5 인서트, Ø50 안), 구멍 Ø16",
    GU: "PET-CF / FDM H2C / C틀 74x59x56: 밑판 받침면 Z42 + 등판 t10 + 위판 Z82~92(Ø8.2) + 옆벽 t3(안쪽 33, 11.14° 기울임) + 막대 r8 L37 + 패드 주머니 앞뒤 벽, M5 인서트 x2",
    CY: "Steel / 구매품 임시 형상(E-10, D-33) / CJ2B10-15 보수 외곽 튜브 Ø16x70 + 장착 나사 Ø8 + 너트 외곽 Ø16, 포트 -X 2",
}
PROPS_PAD = {
    PA: "PET-CF / FDM H2C / 패드 28x20x6, 윗면 T홈(목 4.4, 머리 7.4, -X로 열림)",
    RO: "Steel / 구매품 임시 형상(E-10, D-33) / CJ2B10-15 로드 Ø4",
}
PROPS_TAPE = {TR: "작업 대상 외피(BOM 밖, D-06 임시) / 가득 롤 Ø194 / 심 Ø76 x 폭 32",
              TP: "작업 대상 외피(BOM 밖, D-06 임시) / 테이프 길 두께 1 x 폭 32: 비틀린 경간 Y 40.5~552.5 + 내려오는 테이프"}
C("component.metadata.set", {"component": "T05", "properties": PROPS_T05,
                             "description": "테이프 공급·장력 유닛(T05, 고정 부품). 헤드와 리지드(HEAD 아래). 선정 T05-S01~S08"})
C("component.metadata.set", {"component": "T05_PAD", "properties": PROPS_PAD,
                             "description": "T05 장력 패드(조인트 J_T05_PAD 직선 Z -13.5~0, 저장 -12.5)"})
C("component.metadata.set", {"component": "T05_TAPE", "properties": PROPS_TAPE, "bom_type": "reference",
                             "description": "T05 작업 대상 외피: 테이프 롤·길(BOM 밖, D-06 임시값 두께 1·폭 32)"})

# ================= 리지드 그룹(E-11, M-07): 하위 컴포넌트도 조인트를 가지면 부모와 따로 풀리므로 HEAD에 묶는다 =================
C("joint.rigid_group", {"occurrences": ["HEAD:1", "T05:1", "T05_TAPE:1"]})

# ================= 조인트 J_T05_PAD =================
JP = [-131.0, 572.5, 61.5]
C("joint.create", {"type": "slider", "a": {"occurrence": "T05:1", "point": JP, "z": [0, 0, 1]},
                   "b": {"occurrence": "T05_PAD:1", "point": JP, "z": [0, 0, 1]},
                   "flip": True, "name": "J_T05_PAD", "limits": [[-13.5, 0]]})
C("joint.drive", {"joint": "J_T05_PAD", "value": -12.5, "quiet": True})

C("document.metadata.set", {"values": {"description": "T05 mechanism: dragged tape roll on PSFJ16 stub shaft, PET-CF guide with r8 bar, CJ2B10 friction pad tensioner"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
NEW = {"T05": [PL, HO, SH, HU, CA, GU, CY], "T05_PAD": [PA, RO], "T05_TAPE": [TR, TP]}
json.dump({"material": MAT, "new": NEW, "made": [PL, HO, HU, CA, GU, PA],
           "drop": {"p_rod": p_rod, "p_roll": p_roll, "len": LEN, "ang": ANG, "s0": s0, "s1": s1, "pa": pa, "pb": pb, "dl": DL},
           "alpha": ALPHA, "nspan": len(SPAN)},
          open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps; drop', [round(v, 2) for v in pa], [round(v, 2) for v in pb], round(DL, 2), 'ang', round(ANG, 3))
