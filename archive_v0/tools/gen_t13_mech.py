# T13(모델링부) 생성기: v0.10.0 -> v0.10.1 — 헤드 받침 비틀림 상자(T13-S = 구상 3 + 치마 + 맞댐 L)
# 지시서: docs/reports/mechanism/mech_T13_select.md 지시서 1~8. 좌표는 세계 대기(바늘점 원점, 매트 밑면 Z 0, +Y 헤드 쪽), mm.
# 정적(BASE 아래 T13 컴포넌트, T19 방식), 새 조인트 0. 다르게 정한 곳은 docs/reports/mechanism/mech_T13_model.md 'DEV' 표.
# 쓰는 법: python -B tools/gen_t13_mech.py -> tools/out/mech_T13/model/stage_<a..e>.json (MCP batch 로 차례로), edit.json = 이어 붙인 것
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T13', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
STAGES = {}
S = None
VER = "FSAP_v0.10.1"
TOPC = "T13"
RULE = "SUS304_t2_R2"


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


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (1, 0, 0)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def hole(d, ax, a0, a1, c, body):
    i = {'X': 0, 'Y': 1, 'Z': 2}[ax]
    base = list(c)
    base.insert(i, min(a0, a1))
    cyl(d, base, ax, abs(a1 - a0), op="cut", targets=[body])


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


def prism_z(name, sk, pts, z0, z1):
    C("sketch.create", {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": r6(z1 - z0), "operation": "new", "body_name": name})


META = []
MAT = {}
STEELB = []
NEW = []
BOLTS = []      # {bolt, nut, seat, dir, plate, beam}


def mat(bodies, m):
    for b in bodies:
        MAT[b] = m


def comp(nm, pn, bom, desc):
    C("component.activate", {"component": TOPC})
    C("component.create", {"name": nm, "parent": TOPC, "activate": True, "grounded": False})
    META.append({"component": nm, "part_number": pn, "bom_type": bom, "description": desc})


def ins(step, name, mat_, rename, desc, par):
    C("component.activate", {"component": par})
    C("file.insert_step", {"path": SP + step + '/' + step + '.stp', "name": name, "matrix": [r6(v) for v in mat_]})
    for old, new in rename.items():
        C("body.rename", {"body": old, "name": new})
    C("component.metadata.set", {"component": name, "part_number": step, "bom_type": "purchased", "description": desc})
    NEW.append(name)


def joint(tag, seat, d, s, plate, beam, par):
    # CB5-12 STEP: 머리 로컬 X -k~0, 몸통 +X. seat = 머리 자리면(판 바깥면) 점, d = 넣는 방향
    # HNTT8-5 STEP: 윗면 로컬 Y=0, 길이 로컬 X(홈 방향). at = 형재 겉면 구멍 중심(= seat + 2d), n = -d
    bn, nn = "CB5-12_T13_" + tag, "HNTT8-5_T13_" + tag
    ins("CB5-12", bn, M(d, perp(d), seat), {"Cut-Extrude1": bn},
        "MISUMI 육각 구멍붙이 볼트 M5x12 — %s t2 바깥에서 -> %s 홈 HNTT8-5 (T13 v0.10.1)" % (plate, beam), par)
    at = [seat[i] + 2.0 * d[i] for i in range(3)]
    n = [-c for c in d]
    o = [at[i] - 2.5 * n[i] for i in range(3)]
    ins("HNTT8-5", nn, M(s, n, o), {"Tap1": nn}, "MISUMI 후입 T너트 HNTT8-5 — %s 홈, %s (T13 v0.10.1)" % (beam, plate), par)
    STEELB.extend([bn, nn])
    BOLTS.append({"bolt": bn, "nut": nn, "spec": "CB5-12", "seat": [r6(v) for v in seat], "dir": list(d),
                  "plate": plate, "beam": beam, "slot": list(s)})


SLV, REAR = "P_T13_SLEEVE", "P_T13_REAR"
FBL = {"T1": "P_T13_FBL_T1", "T2": "P_T13_FBL_T2"}
SIDES = (("T1", -1), ("T2", 1))   # T1 = -X, T2 = +X

# ---------------------------------------------------------------------------
# a: 대기, T13 컴포넌트, 판금 규칙, 상자(P_T13_SLEEVE) 판금
stage('a')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("sheet.manage_rules", {"name": RULE, "thickness": 2, "k_factor": 0.44, "bend_radius": 2, "active": False})
C("component.activate", {"component": "BASE"})
C("component.create", {"name": TOPC, "parent": "BASE", "activate": True, "grounded": False})
C("component.metadata.set", {"component": TOPC, "bom_type": "phantom",
                             "description": "T13 헤드 받침 비틀림 상자 묶음(BASE 정적, T13-S) (T13 v0.10.1)"})
SLV_DESC = ("SUS304 t2 / 판금(안 R2, 굽힘 2 세로) / 헤드 받침 상자: 앞판 X-92~92·Y620~622·Z-600~-140, 옆판 X±(90~92)·Y620~780·Z-600~-140, "
            "치마 Y470~780·Z-679~-600(옆판과 한 평면), 굽힘 해방 홈 Y619~625·Z-604~-600, Ø5.5 옆 4 + 치마 4 쪽당, 앞판 구멍 없음, "
            "윗끝 헤드판 맞닿음(체결 없음 DL-X06) (T13 v0.10.1)")
comp(SLV, SLV, "normal", SLV_DESC)
# 한 스케치 H 단면(옆 다리 Y470~780 + 앞판 Y620~622) Z-679~-140 -> 잘라 L 외곽·앞판 높이
prism_z(SLV, "SK_T13_SLEEVE",
        [(-92, 470), (-90, 470), (-90, 620), (90, 620), (90, 470), (92, 470), (92, 780), (90, 780), (90, 622),
         (-90, 622), (-90, 780), (-92, 780)], -679, -140)
box((-90, 90, 619, 623, -680, -600), op="cut", targets=[SLV])          # 앞판 아래(치마 높이) 없앰
box((-93, 93, 469, 620, -600, -139), op="cut", targets=[SLV])          # 옆판 앞(Y<620) 위쪽 없앰 -> 치마 앞 연장만
for sx in (-1, 1):
    box((min(sx * 89, sx * 93), max(sx * 89, sx * 93), 619, 625, -604, -600), op="cut", targets=[SLV])   # 굽힘 해방 홈
C("solid.fillet", {"edges": [[-92, 620, -370], [92, 620, -370]], "radius": 4, "body": SLV})   # 바깥 R4 = 안 R2 + t
C("solid.fillet", {"edges": [[-90, 622, -370], [90, 622, -370]], "radius": 2, "body": SLV})   # 안 R2
for tag, sx in SIDES:
    x0, x1 = sx * 89, sx * 93
    for y in (720, 760):
        for z in (-560, -180):
            hole(5.5, 'X', x0, x1, (y, z), SLV)
    for y in (485, 765):
        for z in (-660, -620):
            hole(5.5, 'X', x0, x1, (y, z), SLV)
C("sheet.convert", {"body": SLV, "face": [0, 620, -370], "rule": RULE,
                    "bends": [[-92 + 4 - 2.8284, 620 + 4 - 2.8284, -370], [92 - 4 + 2.8284, 620 + 4 - 2.8284, -370]],
                    "body_name": SLV})
mat([SLV], "SUS304")
NEW.append(SLV)

# ---------------------------------------------------------------------------
# b: 뒤판(레이저 평판) + 맞댐 L 2(판금)
stage('b')
REAR_DESC = ("SUS304 t2 / 레이저 평판 / 헤드 받침 뒤판 X-92~92·Y780~782·Z-598~-140(580 캡 윗모서리와 2 띄움), "
             "Ø5.5 x6 (X±70; Z-560·-370·-180) 기둥 뒷면 홈 (T13 v0.10.1)")
comp(REAR, REAR, "normal", REAR_DESC)
box((-92, 92, 780, 782, -598, -140), REAR)
for x in (-70, 70):
    for z in (-560, -370, -180):
        hole(5.5, 'Y', 779, 783, (x, z), REAR)
mat([REAR], "SUS304")
NEW.append(REAR)
for tag, sx in SIDES:
    nm = FBL[tag]
    desc = ("SUS304 t2 / 판금 세로 L(안 R2) / 580_%s 앞끝 ↔ 1900_B 맞댐: 다리 A X%s(90~92)·Y200~245, 다리 B Y200~202·X%s(90~135), Z-676~-604, "
            "Ø5.5 A (Y230; Z-660·-620) · B (X%s120; Z-660·-620) (T13 v0.10.1)") % (tag, '-' if sx < 0 else '+', '-' if sx < 0 else '+', '-' if sx < 0 else '+')
    comp(nm, nm, "normal", desc)
    pts = [(90, 200), (90, 245), (92, 245), (92, 202), (135, 202), (135, 200)]
    pts = [(sx * a, b) for a, b in pts]
    if sx < 0:
        pts = pts[::-1]
    prism_z(nm, "SK_T13_FBL_" + tag, pts, -676, -604)
    C("solid.fillet", {"edges": [[sx * 90, 200, -640]], "radius": 4, "body": nm})
    C("solid.fillet", {"edges": [[sx * 92, 202, -640]], "radius": 2, "body": nm})
    for z in (-660, -620):
        hole(5.5, 'X', sx * 89, sx * 93, (230, z), nm)
        hole(5.5, 'Y', 199, 203, (sx * 120, z), nm)
    C("sheet.convert", {"body": nm, "face": [sx * 112, 200, -640], "rule": RULE,
                        "bends": [[sx * (90 + 4 - 2.8284), 200 + 4 - 2.8284, -640]], "body_name": nm})
    mat([nm], "SUS304")
    NEW.append(nm)

# ---------------------------------------------------------------------------
# c: 옆판·치마 볼트 16
stage('c')
ZD, YD, XD = (0, 0, 1), (0, 1, 0), (1, 0, 0)
for tag, sx in SIDES:
    d = (-sx, 0, 0)
    k = 0
    for y in (720, 760):
        for z in (-560, -180):
            k += 1
            joint("SIDE_%s_%d" % (tag, k), (sx * 92, y, z), d, ZD, SLV + " 옆판 " + tag, "HFS8-4080-460_P" + tag[1], SLV)
    k = 0
    for y in (485, 765):
        for z in (-660, -620):
            k += 1
            joint("SKIRT_%s_%d" % (tag, k), (sx * 92, y, z), d, YD, SLV + " 치마 " + tag, "HFS8-4080-580_" + tag, SLV)

# ---------------------------------------------------------------------------
# d: 뒤판 볼트 6, 맞댐 L 볼트 8
stage('d')
for side, x in (("L", -70), ("R", 70)):
    for k, z in enumerate((-560, -370, -180), 1):
        joint("REAR_%s_%d" % (side, k), (x, 782, z), (0, -1, 0), ZD, REAR, "HFS8-4080-460_P" + ("1" if x < 0 else "2"), REAR)
for tag, sx in SIDES:
    k = 0
    for z in (-660, -620):
        k += 1
        joint("FBL_%s_%d" % (tag, k), (sx * 92, 230, z), (-sx, 0, 0), YD, FBL[tag] + " 다리 A", "HFS8-4080-580_" + tag, FBL[tag])
    for z in (-660, -620):
        k += 1
        joint("FBL_%s_%d" % (tag, k), (sx * 120, 202, z), (0, -1, 0), XD, FBL[tag] + " 다리 B", "HFS8-4080-1900_B", FBL[tag])

# ---------------------------------------------------------------------------
# e: 재질·메타·이름·리지드·대기
stage('e')
C("component.activate", {"component": "root"})
mat(STEELB, "Steel")
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})
for mm in META:
    C("component.metadata.set", mm)
C("component.rename", {"component": "root", "name": VER})
C("document.metadata.set", {"values": {"description": "T13 mechanism: head support torsion box - SUS304 t2 sheet sleeve with skirts, rear plate, two butt L brackets, CB5-12 + HNTT8-5 x30"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

if __name__ == '__main__':
    allc = []
    for n in sorted(STAGES):
        json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        allc += STAGES[n]
        print(n, len(STAGES[n]))
    json.dump(allc, open(os.path.join(ROOT, 'tools', 'out', 'mech_T13', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    bodies = sorted(MAT)
    json.dump({"bodies": bodies, "components": NEW, "bolts": STEELB, "materials": MAT, "joints": BOLTS, "changed": bodies},
              open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allc), 'bodies', len(bodies))
