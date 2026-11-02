# T19(모델링부) 생성기: v0.9.1 -> v0.10.0 — 바닥틀 다리·조절발(X 레일 받침), 부품 묶음 신설(부 번호 +1, 요구서 8-2)
# 지시서: docs/reports/mechanism/mech_T19_select.md 4절. 좌표는 세계, mm. 정적(BASE 아래 T19 컴포넌트), 새 조인트 0.
# 다르게 정한 곳은 docs/reports/mechanism/mech_T19_model.md 'DEV' 표.
# HBLFSN8 STEP(실측): 로컬 X 폭 ±15, 판 A(접촉면 y=0, 법선 +Y, 두께 8.2 자리) 구멍 Ø8.2 (0, *, 30) 축 Y,
#   판 B(접촉면 z=0, 법선 +Z, 두께 9) 구멍 Ø8.2 (0, 20, *) 축 Z, 탭 2(접촉면 밖 -2, 폭 10). 놓는 법: 로컬 Y = 다리 옆면 바깥 법선,
#   로컬 Z = 가로면(형재 밑면 / 판 윗면) 바깥 법선. 그래서 세로판 = 판 A(구멍이 가로면에서 30), 가로판 = 판 B(구멍이 다리 면에서 20, 두께 9).
# 쓰는 법: python -B tools/gen_t19_mech.py -> tools/out/mech_T19/model/stage_<a..f>.json (MCP batch 로 차례로), edit.json = 이어 붙인 것
import json, os, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T19', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
STAGES = {}
S = None
VER = "FSAP_v0.10.0"
TOPC = "T19"


def stage(n):
    global S
    S = STAGES.setdefault(n, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 4)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def M(lx, ly, t):
    lz = cross(lx, ly)
    return [lx[0], ly[0], lz[0], t[0], lx[1], ly[1], lz[1], t[1], lx[2], ly[2], lz[2], t[2]]


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def span(d, ax, a0, a1, c, **k):
    # ax 방향 a0~a1, c = 나머지 두 좌표(축 순서대로)
    i = {'X': 0, 'Y': 1, 'Z': 2}[ax]
    base = list(c)
    base.insert(i, min(a0, a1))
    cyl(d, base, ax, abs(a1 - a0), **k)


def box(bb, name=None, op=None, targets=None):
    p = {"length": r6(bb[1] - bb[0]), "width": r6(bb[3] - bb[2]), "height": r6(bb[5] - bb[4]),
         "center": [r6((bb[0] + bb[1]) / 2), r6((bb[2] + bb[3]) / 2), r6((bb[4] + bb[5]) / 2)]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
        p["operation"] = "new"
    C("solid.box", p)


META = []
MAT = {}
STEELB, WAITB, NEW = [], [], []


def mat(bodies, m):
    for b in bodies:
        MAT[b] = m


def ins(step, name, mat_, rename, pn, desc):
    C("file.insert_step", {"path": SP + step + '/' + step + '.stp', "name": name, "matrix": [r6(v) for v in mat_]})
    for old, new in rename.items():
        C("body.rename", {"body": old, "name": new})
    C("component.metadata.set", {"component": name, "part_number": pn, "bom_type": "purchased", "description": desc})
    NEW.append(name)


def comp(nm, pn, bom, desc):
    C("component.activate", {"component": TOPC})
    C("component.create", {"name": nm, "parent": TOPC, "activate": True, "grounded": False})
    META.append({"component": nm, "part_number": pn, "bom_type": bom, "description": desc})


def axn(d):
    return 'X' if d[0] else ('Y' if d[1] else 'Z')


def wait_cb8(name, seat, d, L):
    # E-10 임시 형상 CB8-L: 머리 Ø13 x 8 + 몸통 Ø8 x L (MISUMI CB 규격표 M8: dk 13, k 8)
    ax = axn(d)
    i = {'X': 0, 'Y': 1, 'Z': 2}[ax]
    s = d[i]
    a = seat[i]
    o = [seat[j] for j in range(3) if j != i]
    span(13, ax, a - s * 8, a, o, name=name)
    span(8, ax, a, a + s * L, o, op="join", targets=[name])
    WAITB.append(name)
    NEW.append(name)


def tnut(name, at, n, s, desc):
    # HNTT8-8: 윗면 로컬 Y=0(어깨 Y-3, 두께 9), 길이 로컬 X(홈 방향) ±8.5. at = 형재 겉면 구멍 중심, n = 겉면 바깥 법선
    o = [at[i] - 2.5 * n[i] for i in range(3)]
    ins("HNTT8-8", name, M(s, n, o), {"Tap1": name}, "HNTT8-8", desc)
    STEELB.append(name)


def brk(name, corner, nL, nH, desc):
    lx = cross(nL, nH)
    ins("HBLFSN8", name, M(lx, nL, corner), {"NONE": name}, "HBLFSN8", desc)
    mat([name], "Aluminum")


def add(a, b, k=1.0):
    return tuple(a[i] + k * b[i] for i in range(3))


ZT, ZP = -680.0, -818.0          # 형재 밑면, 판 윗면
ZPB = -834.0                      # 판 밑면
ZF = -900.0                       # 바닥
UP, DN = (0, 0, 1), (0, 0, -1)
# 자리: (이름, 다리 bbox(x0,x1,y0,y1), 80 방향, 축(x,y), 윗 브래킷 면 법선들, 발 브래킷 면 법선, 형재 밑면 홈 방향, 형재)
LEGS = [
    ("F_XM", (-950, -870, -1020, -980), 'X', (-910, -1000), [(1, 0, 0)], (1, 0, 0), (1, 0, 0), "HFS8-4080-1900_F"),
    ("F_MID", (-40, 40, -1020, -980), 'X', (0, -1000), [(-1, 0, 0), (1, 0, 0)], (1, 0, 0), (1, 0, 0), "HFS8-4080-1900_F"),
    ("F_XP", (870, 950, -1020, -980), 'X', (910, -1000), [(-1, 0, 0)], (-1, 0, 0), (1, 0, 0), "HFS8-4080-1900_F"),
    ("B_XM", (-950, -870, 160, 200), 'X', (-910, 180), [(1, 0, 0)], (1, 0, 0), (1, 0, 0), "HFS8-4080-1900_B"),
    ("B_MID", (-40, 40, 160, 200), 'X', (0, 180), [(-1, 0, 0), (1, 0, 0)], (1, 0, 0), (1, 0, 0), "HFS8-4080-1900_B"),
    ("B_XP", (870, 950, 160, 200), 'X', (910, 180), [(-1, 0, 0)], (-1, 0, 0), (1, 0, 0), "HFS8-4080-1900_B"),
    ("T1", (-90, -50, 700, 780), 'Y', (-70, 740), [(0, -1, 0)], (0, -1, 0), (0, 1, 0), "HFS8-4080-580_T1"),
    ("T2", (50, 90, 700, 780), 'Y', (70, 740), [(0, -1, 0)], (0, -1, 0), (0, 1, 0), "HFS8-4080-580_T2"),
]


def face_pt(bb, n):
    # 다리 옆면 위의 홈 중심선(XY) — n 방향 면
    cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
    if n[0] > 0:
        return (bb[1], cy)
    if n[0] < 0:
        return (bb[0], cy)
    if n[1] > 0:
        return (cx, bb[3])
    return (cx, bb[2])


PLATES = {}
FOOT_TAP = {}
# ---------------------------------------------------------------------------
# a: 대기 포즈, T19 컴포넌트(BASE 아래), 다리 8(HFS8-4080-460 실물 단면 -> 138로 자름)
stage('a')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "BASE"})
C("component.create", {"name": TOPC, "parent": "BASE", "activate": True, "grounded": False})
C("component.metadata.set", {"component": TOPC, "bom_type": "phantom",
                             "description": "T19 바닥틀 다리·조절발 묶음(BASE 정적, 작업 높이 900 임시 D-39) (T19 v0.10.0)"})
for tag, bb, d80, axc, ufs, ff, sd, beam in LEGS:
    nm = "STEP대기_HFS8-4080-138_T19_" + tag
    cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
    ly = (1, 0, 0) if d80 == 'X' else (0, 1, 0)
    C("component.activate", {"component": TOPC})
    ins("HFS8-4080-460", nm, M(DN, ly, (cx, cy, ZT)), {"Boss-Extrude1": nm}, "HFS8-4080-138",
        "MISUMI 알루미늄 프레임 8 시리즈 40x80 L138 다리 %s (STEP대기: HFS8-4080-460 실물 단면을 138로 자름, 윗면 %s 밑면 Z-680, 아랫면 받침판 Z-818, 끝은 형재·판이 덮어 캡 없음) (T19 v0.10.0)" % (tag, beam))
    # 자르기는 T19(단위 변환)를 활성으로 둔 채 세계 좌표 상자로 — 넣은 STEP 컴포넌트를 활성화하면 상자가 그 로컬로 읽힌다(실측)
    box((bb[0] - 1, bb[1] + 1, bb[2] - 1, bb[3] + 1, -1141, ZP), op="cut", targets=[nm])
    mat([nm], "Aluminum")

# ---------------------------------------------------------------------------
# b: 윗 브래킷 10 + CB8-16 x2 + HNTT8-8 x2 씩
stage('b')
for tag, bb, d80, axc, ufs, ff, sd, beam in LEGS:
    for j, nL in enumerate(ufs, 1):
        sfx = tag if len(ufs) == 1 else "%s_%d" % (tag, j)
        fx, fy = face_pt(bb, nL)
        corner = (fx, fy, ZT)
        C("component.activate", {"component": TOPC})
        bn = "HBLFSN8_T19_U_" + sfx
        brk(bn, corner, nL, DN, "MISUMI 8 시리즈 탭붙이 브래킷 — 다리 %s 윗끝 ↔ %s 밑면 (T19 v0.10.0)" % (tag, beam))
        # 가로판(판 B, 두께 9): 구멍 = 다리 면에서 20, 머리 아래 -> 위로 형재 밑면 홈 T너트
        h = add(corner, nL, 20.0)
        C("component.activate", {"component": TOPC})
        wait_cb8("STEP대기_CB8-16_T19_U_%s_1" % sfx, (h[0], h[1], ZT - 9.0), UP, 16)
        tnut("HNTT8-8_T19_U_%s_1" % sfx, (h[0], h[1], ZT), DN, sd,
             "MISUMI 후입 T너트 HNTT8-8 — %s 밑면 홈, 윗 브래킷 %s (T19 v0.10.0)" % (beam, sfx))
        # 세로판(판 A, 자리 8.2): 구멍 = 형재 밑면에서 30 아래, 머리 다리 반대쪽 -> 다리 옆 홈 T너트
        v = (fx, fy, ZT - 30.0)
        C("component.activate", {"component": TOPC})
        wait_cb8("STEP대기_CB8-16_T19_U_%s_2" % sfx, add(v, nL, 8.2), tuple(-c for c in nL), 16)
        tnut("HNTT8-8_T19_U_%s_2" % sfx, v, nL, UP,
             "MISUMI 후입 T너트 HNTT8-8 — 다리 %s 옆 홈, 윗 브래킷 %s (T19 v0.10.0)" % (tag, sfx))

# ---------------------------------------------------------------------------
# c: 받침판 8 (SUS304 t16, 레이저 + 탭 + 탭 자리 Ø15 깊이 2.5), C0.5
stage('c')
for tag, bb, d80, axc, ufs, ff, sd, beam in LEGS:
    pn = "P_T19_FOOT_" + tag
    if d80 == 'X':
        pb = (bb[0], bb[1] + 45, bb[2], bb[3]) if ff[0] > 0 else (bb[0] - 45, bb[1], bb[2], bb[3])
    else:
        pb = (bb[0], bb[1], bb[2] - 45, bb[3])
    fx, fy = face_pt(bb, ff)
    tap8 = add((fx, fy, ZP), ff, 20.0)
    FOOT_TAP[tag] = tap8
    PLATES[tag] = pb
    desc = ("SUS304 / 레이저 평판 t16 + 탭 / 받침판 %s X%g~%g·Y%g~%g·Z-834~-818, M16 관통 탭(Ø14) (%g,%g) 조절발, "
            "M8 관통 탭(Ø6.8) (%g,%g) 발 브래킷 CB8-25 + 브래킷 탭 자리 Ø15 깊이 2.5, 모서리 C0.5 (T19 v0.10.0)") % (
        tag, pb[0], pb[1], pb[2], pb[3], axc[0], axc[1], tap8[0], tap8[1])
    comp(pn, "P_T19_FOOT", "normal", desc)
    bb3 = (pb[0], pb[1], pb[2], pb[3], ZPB, ZP)
    box(bb3, pn)
    xm, ym, zm = (pb[0] + pb[1]) / 2, (pb[2] + pb[3]) / 2, (ZPB + ZP) / 2
    edges = []
    for y in (pb[2], pb[3]):
        for z in (ZPB, ZP):
            edges.append([r6(xm), y, z])
    for x in (pb[0], pb[1]):
        for z in (ZPB, ZP):
            edges.append([x, r6(ym), z])
    for x in (pb[0], pb[1]):
        for y in (pb[2], pb[3]):
            edges.append([x, y, r6(zm)])
    C("solid.chamfer", {"edges": edges, "distance": 0.5, "body": pn})
    span(14, 'Z', ZPB - 1, ZP + 1, axc, op="cut", targets=[pn])
    span(6.8, 'Z', ZPB - 1, ZP + 1, (tap8[0], tap8[1]), op="cut", targets=[pn])
    span(15, 'Z', ZP - 2.5, ZP + 1, (tap8[0], tap8[1]), op="cut", targets=[pn])
    mat([pn], "SUS304")
    NEW.append(pn)

# ---------------------------------------------------------------------------
# d: 발 브래킷 8 + CB8-16 + HNTT8-8 (세로판) + CB8-25 (가로판 -> 판 M8 탭)
stage('d')
for tag, bb, d80, axc, ufs, ff, sd, beam in LEGS:
    fx, fy = face_pt(bb, ff)
    corner = (fx, fy, ZP)
    C("component.activate", {"component": TOPC})
    bn = "HBLFSN8_T19_F_" + tag
    brk(bn, corner, ff, UP, "MISUMI 8 시리즈 탭붙이 브래킷 — 다리 %s 아랫끝 ↔ 받침판 P_T19_FOOT_%s (T19 v0.10.0)" % (tag, tag))
    h = FOOT_TAP[tag]
    C("component.activate", {"component": TOPC})
    wait_cb8("STEP대기_CB8-25_T19_F_%s_1" % tag, (h[0], h[1], ZP + 9.0), DN, 25)
    v = (fx, fy, ZP + 30.0)
    wait_cb8("STEP대기_CB8-16_T19_F_%s_2" % tag, add(v, ff, 8.2), tuple(-c for c in ff), 16)
    tnut("HNTT8-8_T19_F_%s_2" % tag, v, ff, UP, "MISUMI 후입 T너트 HNTT8-8 — 다리 %s 옆 홈, 발 브래킷 (T19 v0.10.0)" % tag)

# ---------------------------------------------------------------------------
# e: 조절발 8 STEP대기_ADJM16-66 (받침 Ø60x20, M16 기둥 Ø16 Z-880~-803, 잠금 너트 맞변 24 x 13 Z-847~-834)
stage('e')
RH = 12.0 / math.cos(math.radians(30))
for tag, bb, d80, axc, ufs, ff, sd, beam in LEGS:
    an = "STEP대기_ADJM16-66_T19_" + tag
    comp(an, "ADJM16-66", "purchased",
         "레벨링 마운트 M16 공칭 높이 66 조정 ±15 (형번 임시 표기, 정격 >= 6.3 kN 미스미 형번 확인 D-75) — 받침판 %s 밑, 축 (%g,%g), "
         "카탈로그 외형 임시: 받침 Ø60xH20, 나사 M16 Z-880~-803, 잠금 너트 맞변 24x13 (T19 v0.10.0)" % (tag, axc[0], axc[1]))
    span(60, 'Z', ZF, ZF + 20, axc, name=an)
    span(16, 'Z', ZF + 20, -803, axc, op="join", targets=[an])
    sk = "SK_T19_ADJNUT_" + tag
    C("sketch.create", {"plane": {"origin": [0, 0, -847], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    pts = [[r6(axc[0] + RH * math.cos(math.radians(30 + 60 * k))), r6(axc[1] + RH * math.sin(math.radians(30 + 60 * k)))] for k in range(6)]
    C("sketch.line", {"points": pts, "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 13, "operation": "join", "targets": [an]})
    mat([an], "Steel")
    NEW.append(an)

# ---------------------------------------------------------------------------
# f: 재질·메타·이름·대기
stage('f')
C("component.activate", {"component": "root"})
mat(STEELB + WAITB, "Steel")
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})
for mm in META:
    C("component.metadata.set", mm)
C("component.rename", {"component": "root", "name": VER})
C("document.metadata.set", {"values": {"description": "T19 mechanism: base frame legs HFS8-4080-138 x8 (STEP wait), HBLFSN8 x18, SUS304 foot plates x8, M16 leveling mounts x8 (STEP wait), work height 900 provisional"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ---------------------------------------------------------------------------
# g: HBLFSN8 STEP(조립 STEP: 안에 BRACKET_HBLFSN8 하위 + 리지드 그룹)이 T19에 묶이지 않아 joint.list floating 18 -> T19와 리지드(T18 방식)
stage('g')
C("joint.rigid_group", {"occurrences": ["T19:1"] + ["HBLFSN8_T19_U_" + s + ":1" for s in
                                                     ("F_XM", "F_MID_1", "F_MID_2", "F_XP", "B_XM", "B_MID_1", "B_MID_2", "B_XP", "T1", "T2")]
                        + ["HBLFSN8_T19_F_" + t[0] + ":1" for t in LEGS]})
C("joint.rigid_group", {"occurrences": ["BASE:1", "T19:1"]})   # 위 묶음이 T19를 BASE에서 떼어 floating 1 -> BASE와 리지드(T18_X 방식)
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

if __name__ == '__main__':
    allc = []
    for n in sorted(STAGES):
        json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        allc += STAGES[n]
        print(n, len(STAGES[n]))
    json.dump(allc, open(os.path.join(ROOT, 'tools', 'out', 'mech_T19', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    bodies = sorted(MAT)
    json.dump({"bodies": bodies, "components": NEW, "bolts": STEELB, "wait_bolts": WAITB, "materials": MAT,
               "plates": PLATES, "foot_tap": FOOT_TAP, "changed": bodies},
              open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allc), 'bodies', len(bodies))
