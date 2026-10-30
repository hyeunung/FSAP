# S01: v0.4.1 -> v0.4.2  T06 전 구매품 실물 STEP 교체 + 형재 마감캡 + 높이 차 받침(선정 S01-C2 수정안, mech_S01_select.md).
# 모든 STEP은 root에 세계 행렬(대기 자세)로 넣고(stage1), occurrence.reparent(세계 위치 유지)로 각 유닛 컴포넌트에 옮긴다(stage2).
#   * 이 설계의 feature 좌표(solid.box center, sketch plane)는 세계 대기 좌표이고, file.insert_step matrix는 부모 로컬이다.
#     그래서 로컬 변환을 피하려고 root에 넣는다(v0.4.1 실측: 각 컴포넌트에 center 0 상자 -> 세계 0).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_s01_step.py stage1   -> tools/out/mech_S01/model/stage1.json
#   solidcraft-cli run tools/out/mech_S01/model/stage1.json --in 3D_Modeling/FSAP_v0.4.1.sc --save tools/out/mech_S01/model/s1.sc --results > .../s1_out.json
#   solidcraft-cli run tools/out/mech_S01/model/list1.json --in tools/out/mech_S01/model/s1.sc --results > .../list1_out.json
#   python -B tools/gen_s01_step.py stage2   -> stage2.json (list1_out.json의 occurrence id를 읽는다)
#   solidcraft-cli run tools/out/mech_S01/model/stage2.json --in tools/out/mech_S01/model/s1.sc --save 3D_Modeling/FSAP_v0.4.2.sc --results
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_S01', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
AX = (0.0, -700.0)
TH3 = (90.0, 210.0, 330.0)


def polar(r, th):
    t = math.radians(th)
    return (round(AX[0] + r * math.cos(t), 4), round(AX[1] + r * math.sin(t), 4))


# ---------------- 넣을 STEP(세계 대기 행렬, 3x4 행 우선) ----------------
INS = []   # (name, pn, matrix, target component, desc)


def ins(name, pn, M, comp, desc):
    INS.append((name, pn, [round(v, 12) for v in M], comp, desc))


for tag, yc in (('F', -1000), ('B', 180)):
    ins('SV2RL28-1800_' + tag, 'SV2RL28-1800', [1, 0, 0, -870, 0, 0, -1, yc, 0, 1, 0, -600], 'BASE',
        'MISUMI 중하중 LM가이드 레일 폭 20 H28 L1800 블록 2 (X 이송, 레일 BASE / 블록 MAT_X)')
for tag, xc in (('L', -150), ('R', 150)):
    ins('SV2RL28-1300_' + tag, 'SV2RL28-1300', [0, 0, 1, xc, 1, 0, 0, -1040, 0, 1, 0, -398], 'MAT_X',
        'MISUMI 중하중 LM가이드 레일 폭 20 H28 L1300 블록 2 (Y 이송, 레일 MAT_X / 블록 MAT_Y)')
ins('DGM200R-AZAC_T01', 'DGM200R-AZAC', [0, 0, -1, 0, 0, 1, 0, -795, 1, 0, 0, -305], 'MAT_Y',
    'Oriental Motor 중공 회전 액추에이터 DGII 200 AZ (매트 회전, 하우징·모터 MAT_Y / 출력 테이블 MAT_ROT)')
# CJ2B16: 포트(STEP +Y)를 팔 방향(반지름 바깥)으로: R = Rz(th) * R0, R0 rows (0,1,0),(0,0,-1),(-1,0,0)
for ring, rr in (('R1', 190), ('R2', 410)):
    for i, th in enumerate(TH3):
        cx, cy = polar(rr, th)
        c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
        ins('CJ2B16-60SZ_%s_%d' % (ring, i + 1), 'CJ2B16-60SZ', [0, c, s, cx, 0, s, -c, cy, -1, 0, 0, -98.5], 'MAT_ROT',
            'SMC(MISUMI) 에어 실린더 CJ2 단동 압출 Ø16 st60 (링 승강, 몸통 MAT_ROT / 로드 %s)' % ('RING1' if ring == 'R1' else 'RING2'))
ins('CJ2B10-15Z_T05', 'CJ2B10-15Z', [0, -1, 0, -131, 0, 0, -1, 572.5, 1, 0, 0, 89.5], 'T05',
    'SMC(MISUMI) 에어 실린더 CJ2 복동 Ø10 st15 (테이프 장력 패드, 몸통 T05 / 로드 T05_PAD, 포트 -X)')
ins('PSFJ16-100_T05', 'PSFJ16-100', [1, 0, 0, -180, 0, 1, 0, 750, 0, 0, 1, 200], 'T05', 'MISUMI 리니어 샤프트 Ø16 L100 (테이프 롤 축)')
ins('ZH10DSA-06-06-08_T1', 'ZH10DSA-06-06-08', [0, 0, 1, -40.4, 1, 0, 0, 319.4, 0, 1, 0, -653.6], 'BASE',
    'SMC(MISUMI) 진공 이젝터 ZH 직접 배관형 노즐 Ø1.0 (링1 진공, 580_T1 안쪽 면)')
ins('ZH10DSA-06-06-08_T2', 'ZH10DSA-06-06-08', [0, 0, -1, 40.4, -1, 0, 0, 342.3, 0, 1, 0, -653.6], 'BASE',
    'SMC(MISUMI) 진공 이젝터 ZH 직접 배관형 노즐 Ø1.0 (예비 진공, 580_T2 안쪽 면)')

# 마감캡: STEP Z0 면 = 끝면, +Z = 형재 안쪽(n), STEP X -> 세계 Z, STEP Y = n x X
CAPS = []   # (cap name, frame component, end center, inward n)
for fr, y in (('1900_F', -1000), ('1900_B', 180)):
    CAPS.append(('HFC8-4080-B_%s_XM' % fr, 'HFS8-4080-' + fr, (-950, y, -640), (1, 0, 0)))
    CAPS.append(('HFC8-4080-B_%s_XP' % fr, 'HFS8-4080-' + fr, (950, y, -640), (-1, 0, 0)))
for fr, x in (('580_T1', -70), ('580_T2', 70)):
    CAPS.append(('HFC8-4080-B_%s_YP' % fr, 'HFS8-4080-' + fr, (x, 780, -640), (0, -1, 0)))
for fr, x in (('1300_L', -150), ('1300_R', 150)):
    CAPS.append(('HFC8-4080-B_%s_YM' % fr, 'HFS8-4080-' + fr, (x, -1060, -438), (0, 1, 0)))
    CAPS.append(('HFC8-4080-B_%s_YP' % fr, 'HFS8-4080-' + fr, (x, 240, -438), (0, -1, 0)))
for fr, y in (('460_F', -1000), ('460_B', 180)):
    CAPS.append(('HFC8-4080-B_%s_XM' % fr, 'HFS8-4080-' + fr, (-230, y, -518), (1, 0, 0)))
    CAPS.append(('HFC8-4080-B_%s_XP' % fr, 'HFS8-4080-' + fr, (230, y, -518), (-1, 0, 0)))
for nm, comp, p, n in CAPS:
    ex = (0, 0, 1)
    ey = (n[1] * ex[2] - n[2] * ex[1], n[2] * ex[0] - n[0] * ex[2], n[0] * ex[1] - n[1] * ex[0])
    M = [ex[0], ey[0], n[0], p[0], ex[1], ey[1], n[1], p[1], ex[2], ey[2], n[2], p[2]]
    ins(nm, 'HFC8-4080-B', M, comp, 'MISUMI HFS8 시리즈용 프레임 캡 4080 폴리아미드 검정 (%s 끝면)' % nm.replace('HFC8-4080-B_', ''))

S = []
C = lambda c, p: S.append({"command": c, "params": p})

if sys.argv[1] == 'stage1':
    C("component.activate", {"component": "root"})
    for name, pn, M, comp, desc in INS:
        C("file.insert_step", {"path": SP + pn + '/' + pn + '.stp', "name": name, "matrix": M})
    json.dump(S, open(os.path.join(OUT, 'stage1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    L = [{"command": "component.list", "params": {"compact": True, "bodies": True}}]
    for name, pn, M, comp, desc in INS:
        L.append({"command": "occurrence.properties", "params": {"occurrence": name + ":1"}})
    for c in ('BASE', 'MAT_X', 'MAT_Y', 'MAT_ROT', 'RING1', 'RING2', 'T05', 'T05_PAD'):
        L.append({"command": "component.metadata", "params": {"component": c}})
    for o in ('MAT_ROT:1', 'T05:1', 'RING2:1', 'MAT_Y:1'):
        L.append({"command": "occurrence.properties", "params": {"occurrence": o, "descendants": False}})
    json.dump(L, open(os.path.join(OUT, 'list1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(INS, open(os.path.join(OUT, 'ins.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(INS), 'inserts')
    sys.exit()

# ================= stage2 =================
L1 = json.load(open(os.path.join(OUT, 'list1_out.json'), encoding='utf-8'))
COMPS = L1[0]['components']
OCC = {}
for x in COMPS:
    for q in x['occurrences']:
        OCC[q['id']] = (x, q)
TOP = {}       # insert name -> (occurrence id, [(child occ id, child component name, bodies)], own bodies)
for ch in [c for c in COMPS if c['id'] == 0][0]['children']:
    x, q = OCC[ch]
    nm = q['name'].rsplit(':', 1)[0]
    if nm in [i[0] for i in INS]:
        TOP[nm] = (q['id'], [(k, OCC[k][0]['name'], OCC[k][0]['bodies']) for k in x['children']], x['bodies'])
BB = {}        # occurrence id -> bbox(world) from occurrence.properties
for r in L1[1:1 + len(INS)]:
    for b in r['bodies']:
        BB[b['path'][-1]] = (b['bbox']['min'], b['bbox']['max'], b['name'])


def kids(nm, prefix):
    return [k for k in TOP[nm][1] if k[1].startswith(prefix)]


def bodies_of(nm):
    out = list(TOP[nm][2])
    seen = set()
    for k in TOP[nm][1]:
        for b in k[2]:
            if b not in seen:
                seen.add(b)
                out.append(b)
    return out


MADE = {}      # body -> (component, "재질 / 만드는 법")


def box(x0, x1, y0, y1, z0, z1, name=None, op=None, targets=None):
    p = {"length": round(x1 - x0, 6), "width": round(y1 - y0, 6), "height": round(z1 - z0, 6),
         "center": [round((x0 + x1) / 2, 6), round((y0 + y1) / 2, 6), round((z0 + z1) / 2, 6)]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


def cylz(r, x, y, z0, z1, name=None, op=None, targets=None):
    p = {"radius": r, "height": round(z1 - z0, 6), "base": [x, y, z0]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


# ---------- 1) MAT_ROT: 스파이더 다리 150 -> 136.5(밑 -235 그대로, 웹 -98.5~-95.5), 보스 구멍 = 실물 보스 Ø10 + 0.5 ----------
C("component.activate", {"component": "MAT_ROT"})
C("solid.remove", {"bodies": ["P_T01_SPIDER_%d" % (i + 1) for i in range(3)] +
                   ["STEP대기_CJ2B16-60S_%s_%d" % (r, i + 1) for r in ('R1', 'R2') for i in range(3)]})
for i, th in enumerate(TH3):
    n = "P_T01_SPIDER_%d" % (i + 1)
    t = math.radians(th)
    u = (math.cos(t), math.sin(t)); v = (-u[1], u[0])
    o = (AX[0] + 100 * u[0], AX[1] + 100 * u[1])
    sk = "SK_S01_SPIDER_%d" % (i + 1)
    C("sketch.create", {"plane": {"origin": [round(o[0], 4), round(o[1], 4), 0], "x_dir": [round(v[0], 9), round(v[1], 9), 0],
                                  "y_dir": [0, 0, 1]}, "name": sk})
    pts = [(-30, -235), (-27, -235), (-27, -98.5), (27, -98.5), (27, -235), (30, -235), (30, -95.5), (-30, -95.5)]
    for j in range(len(pts)):
        C("sketch.line", {"points": [list(pts[j]), list(pts[(j + 1) % len(pts)])]})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 390, "body_name": n})
    for rr, hr in ((190, 5.25), (410, 5.25), (240, 14.5), (460, 14.5)):
        x, y = polar(rr, th)
        cylz(hr, x, y, -100, -94, op="cut", targets=[n])
    MADE[n] = ("MAT_ROT", "SUS304 / 판금 t3 ㄷ(곧은 절곡 2회) / 다리 -235~-95.5(웹 -98.5~-95.5), 실린더 보스 구멍 Ø10.5, LHFR16 구멍 Ø29")
C("component.activate", {"component": "root"})
for r in ('R1', 'R2'):
    for i in range(3):
        C("occurrence.move", {"occurrence": "LHFR16_%s_%d:1" % (r, i + 1), "space": "world", "translate": [0, 0, -10.5]})

# ---------- 2) RING1/RING2: 임시 로드 지움, 링2 띠 1·3·5 밑면 자리 Ø6 x 1.5 ----------
C("component.activate", {"component": "RING1"})
C("solid.remove", {"bodies": ["STEP대기_CJ2B16-60S_ROD_R1_%d" % (i + 1) for i in range(3)]})
C("component.activate", {"component": "RING2"})
C("solid.remove", {"bodies": ["STEP대기_CJ2B16-60S_ROD_R2_%d" % (i + 1) for i in range(3)]})
for i, th in enumerate(TH3):
    x, y = polar(410, th)
    cylz(3, x, y, -12.5, -10.5, op="cut", targets=["P_T01_RING2_STRAP_%d" % (2 * i + 1)])
    MADE["P_T01_RING2_STRAP_%d" % (2 * i + 1)] = ("RING2", "A5052 / 레이저 평판 / 띠 40×195 t5, 밑면 로드 끝 자리 Ø6 깊이 1.5(밀링)")
C("component.activate", {"component": "root"})

# ---------- 3) MAT_Y: Y판 14 내림 + 모터 창, DGM U자 받침, 임시 DGM·블록 지움 ----------
C("component.activate", {"component": "MAT_Y"})
C("solid.remove", {"bodies": ["STEP대기_DGM200R-AZAC"] + ["STEP대기_SV2R20-1300_BLK_%d" % (i + 1) for i in range(4)]})
C("solid.move", {"bodies": ["P_T01_YPLATE"], "translate": [0, 0, -14]})
box(-47.5, 47.5, -870, -665, -371, -354, op="cut", targets=["P_T01_YPLATE"])
MADE["P_T01_YPLATE"] = ("MAT_Y", "A5052 / 밀링 / Y 이동판 400×500 t15(Z -370~-355), 모터·호스 창 95×205")
C("sketch.create", {"plane": {"origin": [0, 0, -355], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_S01_DGSPACER"})
U = [(-100, -837.5), (-47.5, -837.5), (-47.5, -665), (47.5, -665), (47.5, -837.5), (100, -837.5), (100, -600), (-100, -600)]
for j in range(len(U)):
    C("sketch.line", {"points": [list(U[j]), list(U[(j + 1) % len(U)])]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_S01_DGSPACER", "profiles": "all", "distance": 50, "body_name": "P_S01_DGSPACER"})
for x in (-85, 85):
    for y in (-785, -615):
        cylz(4.25, x, y, -325, -304, op="cut", targets=["P_S01_DGSPACER"])
MADE["P_S01_DGSPACER"] = ("MAT_Y", "A5052 / 밀링 / DGM 받침 U자 200×237.5×50(트임 95×172.5, -Y 열림), DGM 장착 탭 기초 구멍 Ø8.5 깊이 20 ×4")
C("component.activate", {"component": "root"})

# ---------- 4) MAT_X: X 블록 받침 ×4, 임시 레일·블록 지움 ----------
C("component.activate", {"component": "MAT_X"})
C("solid.remove", {"bodies": ["STEP대기_SV2R20-1300_L", "STEP대기_SV2R20-1300_R"] + ["STEP대기_SV2R20-1800_BLK_%d" % (i + 1) for i in range(4)]})
k = 0
for (y0, y1) in ((-1021, -979), (159, 201)):
    for (x0, x1) in ((-230, -130), (130, 230)):
        k += 1
        n = "P_S01_XSPACER_%d" % k
        box(x0, x1, y0, y1, -572, -558, n)
        MADE[n] = ("MAT_X", "A5052 / 밀링 / X 블록 받침 100×42 t14(레일 높이 차 14 메움)")
C("component.activate", {"component": "root"})

# ---------- 5) BASE: 임시 레일 지움 ----------
C("component.activate", {"component": "BASE"})
C("solid.remove", {"bodies": ["STEP대기_SV2R20-1800_F", "STEP대기_SV2R20-1800_B"]})
C("component.activate", {"component": "root"})

# ---------- 6) T05: 안내 블록 위판 전체 t4(Z 85.5~89.5), 등판 윗면 89.5, 앞·뒷벽 윗면 85.5; 임시 실린더·축 지움 ----------
C("component.activate", {"component": "T05"})
C("solid.remove", {"bodies": ["STEP대기_CJ2B10-15", "STEP대기_PSFJ16-100"]})
box(-148, -79, 552, 613, 89.5, 93, op="cut", targets=["P_T05_GUIDE"])
box(-148, -88, 562.2, 582.8, 81.5, 85.5, op="cut", targets=["P_T05_GUIDE"])
box(-148, -88, 588, 596, 81.5, 85.5, op="cut", targets=["P_T05_GUIDE"])
MADE["P_T05_GUIDE"] = ("T05", "PET-CF / FDM H2C / C틀 72x59x53.5: 밑판 받침면 Z42 + 등판 t8(윗면 89.5) + 위판 t4 Z85.5~89.5(Ø8.2) + 옆벽 t3(안쪽 33, 11.14° 기울임) + 막대 r8 L37 + 패드 주머니 앞뒤 벽(윗면 85.5), M5 인서트 x2(Ø6.4 등판 관통)")
C("component.activate", {"component": "T05_PAD"})
C("solid.remove", {"bodies": ["STEP대기_CJ2B10-15_ROD"]})
C("component.activate", {"component": "root"})

# ---------- 7) 실물 STEP: 풀기 -> 블록·로드 옮기기 -> 부모 컴포넌트로 ----------
for nm in TOP:
    if TOP[nm][1]:
        C("component.unlock", {"component": nm})


def mv(occ, t):
    C("occurrence.move", {"occurrence": occ, "space": "world", "translate": [round(v, 6) for v in t]})


def rp(occ, parent):
    C("occurrence.reparent", {"occurrence": occ, "parent": parent})


for nm, axis, targets, parent in (('SV2RL28-1800_F', 0, (-180, 180), 'MAT_X'), ('SV2RL28-1800_B', 0, (-180, 180), 'MAT_X'),
                                  ('SV2RL28-1300_L', 1, (-860, -540), 'MAT_Y'), ('SV2RL28-1300_R', 1, (-860, -540), 'MAT_Y')):
    bl = sorted(kids(nm, 'BLOCK_'), key=lambda k: BB[k[0]][0][axis])
    assert len(bl) == 2, (nm, bl)
    for (oid, cn, bs), tgt in zip(bl, targets):
        lo, hi, _ = BB[oid]
        t = [0, 0, 0]
        t[axis] = tgt - (lo[axis] + hi[axis]) / 2
        mv(oid, t)
        rp(oid, parent)
for oid, cn, bs in kids('DGM200R-AZAC_T01', 'DGii200_ring'):
    rp(oid, 'MAT_ROT')      # 출력 테이블은 매트와 함께 돈다(M-07)
for ring in ('R1', 'R2'):
    for i in range(3):
        nm = 'CJ2B16-60SZ_%s_%d' % (ring, i + 1)
        rn = kids(nm, 'CJ2B16-60SZ_ROD') + kids(nm, 'NTJ-015C')
        assert len(rn) == 3, rn
        for oid, cn, bs in rn:
            mv(oid, [0, 0, 60])
            rp(oid, 'RING1' if ring == 'R1' else 'RING2')
        for oid, cn, bs in kids(nm, 'SNJ-016C'):
            mv(oid, [0, 0, -95.5 - BB[oid][0][2]])
rn = kids('CJ2B10-15Z_T05', 'CJ2B10-15Z_ROD') + kids('CJ2B10-15Z_T05', 'NTJ-010C')
assert len(rn) == 3, rn
for oid, cn, bs in rn:
    mv(oid, [0, 0, -12.5])
    rp(oid, 'T05_PAD')
for oid, cn, bs in kids('CJ2B10-15Z_T05', 'SNJ-010C'):
    mv(oid, [0, 0, 85.5 - BB[oid][1][2]])
for name, pn, M, comp, desc in INS:
    rp(TOP[name][0], comp)

# ---------- 8) 바디 이름(<자리 이름>_<부분>), 재질·속성(E-09) ----------
PART = (('RAIL_', 'RAIL'), ('BLOCK_', 'BLOCK'), ('DG200R-AZACD-1(Single Shaft)_gear2', 'HOUSING'), ('DGii200_ring', 'TABLE'),
        ('DG200R-AZACD-1(Single Shaft)_body', 'MOTOR'), ('CJ2B16-60SZ(0_0)_BODY', 'BODY'), ('CJ2B10-15Z(1_0)_BODY', 'BODY'),
        ('CJ2B16-60SZ_ROD', 'ROD'), ('CJ2B10-15Z_ROD', 'ROD'), ('NTJ-', 'NTJ'), ('SNJ-', 'SNJ'),
        ('ZH10DSA-06-06-08(0)_BODY', 'BODY'), ('ZH2-BK1A', 'BRACKET'))
REN = {}
for name, pn, M, comp, desc in INS:
    if TOP[name][2]:
        REN[TOP[name][2][0]] = name
    for oid, cn, bs in TOP[name][1]:
        tail = [t for p, t in PART if cn.startswith(p)]
        assert len(tail) == 1, (name, cn)
        for b in bs:
            REN[b] = name + '_' + tail[0]
for old, new in REN.items():
    C("body.rename", {"body": old, "name": new})
steel, nylon = [], []
for name, pn, M, comp, desc in INS:
    (nylon if pn.startswith('HFC8') else steel).extend(REN[b] for b in bodies_of(name))
C("material.assign", {"bodies": steel, "material": "Steel"})
C("material.assign", {"bodies": nylon, "material": "Nylon"})
for mat in ('A5052', 'SUS304', 'PET-CF'):
    C("material.assign", {"bodies": [b for b in MADE if MADE[b][1].startswith(mat)], "material": mat})
for name, pn, M, comp, desc in INS:
    C("component.metadata.set", {"component": name, "part_number": pn, "bom_type": "purchased", "description": desc})
# 마감캡은 형재 컴포넌트 아래에 있다. purchased 아래 부품은 flat BOM에 안 나오므로 형재를 inseparable(한 행 + 안의 구매품도 행)로
for fr in ('1900_F', '1900_B', '580_T1', '580_T2', '1300_L', '1300_R', '460_F', '460_B', '460_P1', '460_P2'):
    C("component.metadata.set", {"component": "HFS8-4080-" + fr, "bom_type": "inseparable"})
PARTOF = {}
for name, pn, M, comp, desc in INS:
    for oid, cn, bs in TOP[name][1]:
        PARTOF.setdefault(OCC[oid][0]['id'], (cn, pn))
for cid, (cn, pn) in PARTOF.items():
    C("component.metadata.set", {"component": cid, "bom_type": "reference", "description": "%s 의 일부(구매품 STEP 하위)" % pn})
PROPS = {}
for b, (comp, how) in MADE.items():
    PROPS.setdefault(comp, {})[b] = how
DROP = {"BASE": ["STEP대기_HFS8-4080-460_P1", "STEP대기_HFS8-4080-460_P2", "STEP대기_HFS8-4080-580_T1", "STEP대기_HFS8-4080-580_T2"],
        "T05": ["STEP대기_CJ2B10-15", "STEP대기_PSFJ16-100"], "T05_PAD": ["STEP대기_CJ2B10-15_ROD"]}
for comp, keys in DROP.items():
    PROPS.setdefault(comp, {}).update({k: None for k in keys})
for comp, p in PROPS.items():
    C("component.metadata.set", {"component": comp, "properties": p})

C("document.metadata.set", {"values": {"description": "S01 mechanism: real STEP for SV2RL28 rails, DGM200R, CJ2B16-60SZ x6, CJ2B10-15Z, PSFJ16-100, ZH10DSA x2; HFC8 caps x14; 14mm spacers"}})
C("motion.play", {"study": "대기", "step": 0})
json.dump(S, open(os.path.join(OUT, 'stage2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({"made": MADE, "partof": {str(k): v for k, v in PARTOF.items()}, "top": {k: [v[0], [list(x[:2]) for x in v[1]]] for k, v in TOP.items()}},
          open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps')
