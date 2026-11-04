# -*- coding: utf-8 -*-
"""DC2-04 수정 1회차 생성기 — 기준 3D_Modeling/FSAP_v2.3.1.sc -> 3D_Modeling/FSAP_v2.3.2.sc (모델링부 2026-11-04)
검증 문제: P_M05_HOLDER 날개 A 장공은 조임 마찰로만 Z를 버틴다(손 X 100 N 짝힘 -> 볼트당 536.8 N, 미끄럼 SF 1.18).
고침: 날개 A 아래 끝(Z 285) 밑 양 끝(X 14·42)에 미는 볼트 2개(M4 멈춤나사 + 잠금 너트, UPPER -Y 면에 받침 블록),
      장공 볼트 CB5-12_M05_11·12 밑에 평 와셔 M5 SUS t1.
python -X utf8 -B tools/gen_v2_dc204_fix1.py          -> tools/out/mech_DC2-04/fix1/parts/prep_*.json + edit_fix1.json
python -X utf8 -B tools/gen_v2_dc204_fix1.py --check  -> tools/out/mech_DC2-04/fix1/check.json (기록 + 저장 전 검사, 저장 안 함)
python -X utf8 -B tools/gen_v2_dc204_fix1.py --machine -> tools/machine.json 유닛 부품 목록 고침
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm, h 0(J_U7_HGT 0).
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_DC2-04", "fix1").replace("\\", "/")
PARTS = OUT + "/parts"
STEP = PRJ + "/purchased-step/"
UPPER = "STEP대기_867-392342_UPPER"
HOLDER = "P_M05_HOLDER"
BLK = "P_DC204_PUSH_BLK"
SS = ["STEP대기_SETSCREW_M4x25_DC204_1", "STEP대기_SETSCREW_M4x25_DC204_2"]
NUT = ["STEP대기_NUT_M4_DC204_1", "STEP대기_NUT_M4_DC204_2"]
WSH = ["STEP대기_WASHER_M5_DC204_1", "STEP대기_WASHER_M5_DC204_2"]
NEWB = ["CB5-12_DC204_1", "CB5-12_DC204_2"]
OLDB = ["CB5-12_M05_11", "CB5-12_M05_12"]

# 치수
BX0, BX1, BY0, BY1, BZ0, BZ1 = 8.0, 48.0, -98.0, -90.0, 250.0, 276.0   # 받침 블록 SUS304 (UPPER -Y 면 Y -90에 붙음)
SX = (14.0, 42.0)          # 미는 볼트 X (날개 A X 10~46 양 끝)
SY = -94.1                 # 미는 볼트 축 Y (날개 A Y -94~-90: 끝 Ø4가 -96.1~-92.1, 날개와 1.9 폭 맞닿음; 너트 꼭짓점 4.04 -> -90.06, UPPER와 0.06)
SZ0, SZ1 = 260.0, 285.0    # M4x25 h 0: 끝 Z 285 = 날개 A 아래 끝
NZ0, NZ1 = 276.0, 279.2    # 잠금 너트 M4 1종(맞변 7, 높이 3.2) 블록 윗면 위
BOLT_Z = (257.0, 269.0)    # 블록 고정 CB5-12 X 28, 자리파기 Ø9.5 깊이 5.4 -> 머리 밑 Y -92.6
BOLT_X = 28.0
WY0, WY1 = -95.0, -94.0    # 와셔 M5 소형(JIS B 1256, 바깥 Ø10 · 안 Ø5.3 · t1)


def C(cmd, **p):
    return {"command": cmd, "params": p}


def r4(v):
    return round(float(v), 4)


def cyl(r, base, h, axis, op, tg=None, name=None):
    p = {"radius": r, "height": r4(h), "base": [r4(v) for v in base], "axis": axis, "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


def cy(r, x, z, y0, y1, op, tg=None, name=None):
    return cyl(r, [x, y0, z], y1 - y0, [0, 1, 0], op, tg, name)


def cz(r, x, y, z0, z1, op, tg=None, name=None):
    return cyl(r, [x, y, z0], z1 - z0, [0, 0, 1], op, tg, name)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mat_loc(cx_, cy_, t):
    cz_ = cross(cx_, cy_)
    return [cx_[0], cy_[0], cz_[0], r4(t[0]), cx_[1], cy_[1], cz_[1], r4(t[1]), cx_[2], cy_[2], cz_[2], r4(t[2])]


def XY(z):
    return {"origin": [0, 0, z], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}


# ---------------------------------------------------------------- 구매품 준비(CB5-12 실물 STEP)
def gen_parts():
    os.makedirs(PARTS, exist_ok=True)
    for nm, z in zip(NEWB, BOLT_Z):
        s = [C("file.insert_step", path=STEP + "CB5-12/CB5-12.stp", name=nm,
               matrix=mat_loc((0, 1, 0), (0, 0, 1), (BOLT_X, -92.6, z))),
             C("body.rename", body="Cut-Extrude1", name=nm),
             C("inspect.measure")]
        json.dump(s, open(PARTS + "/prep_%s.json" % nm, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


# ---------------------------------------------------------------- 기록
def st_block():
    s = [C("solid.box", length=BX1 - BX0, width=BY1 - BY0, height=BZ1 - BZ0, corner=[BX0, BY0, BZ0],
           operation="new", body_name=BLK)]
    s += [cz(2.0, x, SY, BZ0 - 0.1, BZ1 + 0.1, "cut", [BLK]) for x in SX]                    # M4 탭(호칭 Ø4) 관통
    for z in BOLT_Z:
        s += [cy(2.75, BOLT_X, z, BY0 - 0.1, BY1 + 0.1, "cut", [BLK]),                        # Ø5.5 관통
              cy(4.75, BOLT_X, z, BY0 - 0.1, -92.6, "cut", [BLK])]                            # 자리파기 Ø9.5 깊이 5.4
    s += [C("solid.chamfer", edges=[[BX0, BY0, (BZ0 + BZ1) / 2], [BX1, BY0, (BZ0 + BZ1) / 2]], distance=0.5, body=BLK)]
    # UPPER -Y 면 M5 탭(Ø4.2 깊이 12)
    s += [cy(2.1, BOLT_X, z, -90.1, -78, "cut", [UPPER]) for z in BOLT_Z]
    return s


def hexagon(cx_, cy_, s_flat):
    r = s_flat / 2 / math.cos(math.radians(30))
    return [[r4(cx_ + r * math.cos(math.radians(60 * k))), r4(cy_ + r * math.sin(math.radians(60 * k)))] for k in range(6)]


def st_fasteners():
    s = []
    for i, x in enumerate(SX):
        # 멈춤나사 M4x25 평끝(JIS B 1177), 육각 구멍 2 -> Ø2.3 깊이 2 자리
        s += [cz(2.0, x, SY, SZ0, SZ1, "new", name=SS[i]), cz(1.15, x, SY, SZ0 - 0.1, SZ0 + 2, "cut", [SS[i]])]
        # 잠금 너트 M4 1종(맞변 7, 높이 3.2), 맞변이 UPPER 면과 나란
        nm = "SK_DC204_NUT_%d" % (i + 1)
        s += [C("sketch.create", plane=XY(NZ0), name=nm),
              C("sketch.line", points=hexagon(x, SY, 7.0), closed=True),
              C("sketch.finish"),
              C("solid.extrude", sketch=nm, distance=NZ1 - NZ0, operation="new", body_name=NUT[i]),
              cz(2.0, x, SY, NZ0 - 0.1, NZ1 + 0.1, "cut", [NUT[i]])]
    # 와셔 + 장공 볼트 -Y 1
    for i, (b, x) in enumerate(zip(OLDB, (18.0, 36.0))):
        s += [cy(5.0, x, 310, WY0, WY1, "new", name=WSH[i]), cy(2.65, x, 310, WY0 - 0.1, WY1 + 0.1, "cut", [WSH[i]]),
              C("solid.move", bodies=[b], translate=[0, -1, 0])]
    return s


def st_assign():
    s = [C("component.move_bodies", bodies=[BLK] + NUT + WSH, component="U3_HEAD"),
         C("component.move_bodies", bodies=SS, component="U7_FIXED"),
         C("material.assign", bodies=[BLK] + WSH, material="SUS304"),
         C("material.assign", bodies=SS, material="SCM435"),
         C("material.assign", bodies=NUT, material="Steel")]
    for nm in NEWB:
        s += [C("component.insert_design", path="%s/%s.sc" % (PARTS, nm), name=nm, parent="U3_HEAD"),
              C("component.break_link", component=nm),
              C("component.metadata.set", component=nm, part_number="CB5-12", bom_type="purchased")]
    s.append(C("material.assign", bodies=NEWB, material="SCM435"))
    return s


def st_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="DC2-04 mechanism fix1: U7 holder slot push screws M4 x2 with block on UPPER, M5 washers under slot bolts")]


def build():
    return st_block() + st_fasteners() + st_assign() + st_final()


# ---------------------------------------------------------------- 저장 전 검사(과제 범위)
def check():
    sig = json.load(open(ROOT + "/out/signatures.json", encoding="utf-8"))
    ALL = [p["name"] for p in sig["parts"].values()]
    NEW = [BLK] + SS + NUT + WSH + NEWB
    def near(b):   # 새 부품 둘레(카세트 움직임 포함) 상자에 걸치는 것만
        x0, x1, y0, y1, z0, z1 = b
        return x1 > -40 and x0 < 100 and y1 > -150 and y0 < -60 and z1 > 200 and z0 < 520
    AG = [p["name"] for p in sig["parts"].values() if p["name"] not in NEW and (near(p["bbox"]) or p["unit"] == "U7_TAPE")]
    print("against", len(AG))
    MOVED = OLDB
    seq, idx = build()[:-3], []

    def add(tag, cmd):
        idx.append((len(seq), tag))
        seq.append(cmd)

    def drv(j, v):
        seq.append(C("joint.drive", joint=j, value=v, quiet=True))

    add("meas", C("inspect.measure", bodies=NEW + OLDB + [UPPER, HOLDER]))
    for h in (-4.0, -1.5, 1.0, 3.5, 6.0):
        drv("J_U7_HGT", h)
        add("HGT %+g" % h, C("inspect.clearance", bodies=NEW + MOVED, against=AG + [], clearance=1, nearest=1))
        add("HGT %+g self" % h, C("inspect.clearance", bodies=NEW, against=NEW + MOVED, clearance=0.5))
    drv("J_U7_HGT", 0)
    # U7 카세트 조인트 0·25·50·75·100 % (HGT 0)
    for j, lo, hi in (("J_U7_CST_X", 0, 25), ("J_U7_CST_Y", 0, 250), ("J_U7_FEED", 0, 150), ("J_U7_CUT", 0, 15),
                      ("J_U7_TUCK", 0, 15), ("J_U7_LATCH", 0, 12)):
        for f in (0.25, 0.5, 0.75, 1.0):
            drv(j, lo + (hi - lo) * f)
            add("%s %g" % (j, f), C("inspect.clearance", bodies=NEW + MOVED, against=AG, clearance=1, nearest=1))
        drv(j, lo)
    # THICK 자세(HGT -4 / +6 + 노루발 + 바퀴), 칼·접기 15 · 보내기 150
    for st, v in (("THICK_6", -4), ("THICK_16", 6)):
        drv("J_U7_HGT", v)
        drv("J_U6_HGT", v)
        for j, x in (("J_U7_CUT", 15), ("J_U7_TUCK", 15)):
            drv(j, x)
        add("%s CUT/TUCK15" % st, C("inspect.clearance", bodies=NEW + MOVED, against=AG, clearance=1, nearest=1))
        drv("J_U7_CUT", 0); drv("J_U7_TUCK", 0); drv("J_U7_FEED", 150)
        add("%s FEED150" % st, C("inspect.clearance", bodies=NEW + MOVED, against=AG, clearance=1, nearest=1))
        drv("J_U7_FEED", 0)
    drv("J_U7_HGT", 0); drv("J_U6_HGT", 0)
    # 자기 점검: HGT 9 -> 6 멈춤, 멈춤나사 따라옴
    drv("J_U7_HGT", 9)
    add("HGT 9 meas", C("inspect.measure", bodies=SS + NUT + [HOLDER, BLK]))
    drv("J_U7_HGT", -9)
    add("HGT -9 meas", C("inspect.measure", bodies=SS + NUT + [HOLDER, BLK]))
    drv("J_U7_HGT", 0)
    seq.append(C("motion.play", study="REST", step=0, quiet=True))
    add("joints", C("joint.list"))
    json.dump(seq, open(OUT + "/check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(idx, open(OUT + "/check_idx.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(len(seq), "check commands")


def gen_machine():
    p = ROOT + "/machine.json"
    m = json.load(open(p, encoding="utf-8"))
    u3 = m["units"]["U3_HEAD"]["parts"]
    for n in ("P_DC204_PUSH_BLK", "STEP대기_NUT_M4_DC204", "STEP대기_WASHER_M5_DC204", "CB5-12_DC204"):
        if n not in u3:
            u3.append(n)
    u7 = m["units"]["U7_TAPE"]["parts"]
    if "STEP대기_SETSCREW_M4x25_DC204" not in u7:
        u7.append("STEP대기_SETSCREW_M4x25_DC204")
    m["units"]["U7_TAPE"]["_note_DC204_fix1"] = (
        "DC2-04 수정 1(v2.3.2): 날개 A 아래 끝 미는 볼트 M4x25 ×2(X 14·42, Y -94.1)는 U7_FIXED에 둔다 — 제품 교체 때 J_U7_HGT를 맞춘 뒤 "
        "끝을 날개 아래 끝에 대고 잠그므로 위치 = J_U7_HGT. 받침 블록·잠금 너트·와셔는 U3_HEAD(UPPER)")
    j = m["joints"]["J_U7_HGT"]
    j["_note"] = j.get("_note", "") + " / 수정 1(v2.3.2): 맞춘 뒤 미는 볼트 M4 ×2를 날개 A 아래 끝(Z 285 + h)에 대고 잠금 너트로 잠근다(장공 마찰만으로 버티지 않음)"
    m["doc"] = "../3D_Modeling/FSAP_v2.3.2.sc"
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json updated")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--machine" in sys.argv:
        gen_machine()
    elif "--check" in sys.argv:
        check()
    else:
        gen_parts()
        s = build()
        json.dump(s, open(OUT + "/edit_fix1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(len(s), "commands")
