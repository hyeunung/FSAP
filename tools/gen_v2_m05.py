# -*- coding: utf-8 -*-
"""M05 U7 테이프 툴 카세트 생성기 — 기준 tools/out/M05/base.sc(v2.1.5 복사) -> tools/out/M05/cand.sc (모델링부 2026-11-04, 동시 과제 E-25)
설계안 docs/reports/mechanism/mech_M05_design.md(3절 표·10절 지시서).
python -X utf8 -B tools/gen_v2_m05.py --parts   -> tools/out/M05/parts/*.json (구매품 한 개씩 STEP을 세계 자리에 놓은 .sc 준비 스크립트)
python -X utf8 -B tools/gen_v2_m05.py           -> tools/out/M05/edit.json (base.sc에 돌리는 명령 기록)
python -X utf8 -B tools/gen_v2_m05.py --machine -> tools/out/M05/machine.json (공유 machine.json 복사본에 M05 조인트·연구)
구매품은 file.insert_step(동시 과제 금지 명령)을 기록에 넣지 않으려고, 부품마다 준비 .sc(parts/<이름>.sc)에 한 번 넣어 두고
기록에서는 component.insert_design + component.break_link로 가져온다(같은 파일이면 같은 결과).
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 좌표, U7 조인트 0(대기).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "M05")
PARTS = (OUT + "/parts").replace("\\", "/")
STEP = PRJ + "/purchased-step/"
UPPER = "STEP대기_867-392342_UPPER"


def C(cmd, **p):
    return {"command": cmd, "params": p}


def r4(v):
    return round(float(v), 4)


def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None):
    p = {"length": r4(x1 - x0), "width": r4(y1 - y0), "height": r4(z1 - z0), "corner": [r4(x0), r4(y0), r4(z0)], "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    return C("solid.box", **p)


def cyl(r, base, h, axis, op, tg=None, name=None):
    p = {"radius": r, "height": r4(h), "base": [r4(v) for v in base], "axis": axis, "operation": op}
    if tg:
        p["targets"] = tg
    if name:
        p["body_name"] = name
    return C("solid.cylinder", **p)


def cx(r, y, z, x0, x1, op, tg=None, name=None):
    return cyl(r, [x0, y, z], x1 - x0, [1, 0, 0], op, tg, name)


def cy(r, x, z, y0, y1, op, tg=None, name=None):
    return cyl(r, [x, y0, z], y1 - y0, [0, 1, 0], op, tg, name)


def cz(r, x, y, z0, z1, op, tg=None, name=None):
    return cyl(r, [x, y, z0], z1 - z0, [0, 0, 1], op, tg, name)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mat_loc(cx_, cy_, t):
    """로컬 X축 -> cx_, 로컬 Y축 -> cy_, Z = X x Y. 행 우선 3x4."""
    cz_ = cross(cx_, cy_)
    return [cx_[0], cy_[0], cz_[0], r4(t[0]), cx_[1], cy_[1], cz_[1], r4(t[1]), cx_[2], cy_[2], cz_[2], r4(t[2])]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 and abs(d[1]) > 0.5 else (0, 1, 0)


# ---------------------------------------------------------------- 구매품 자리(세계, REST)
# 실린더 STEP 실측(tools/out/M05/parts/mr_*.out.json): 로컬 X축, 머리 커버 어깨 x=0, 보스 -8~0, 로드 끝(후퇴) x=-28,
# 장착 너트 SNJ, 로드 끝 너트 NTJ ×2, 포트 로컬 +Y 면(CJ2B10 x≈7.9·57.9, y=6 / CDJ2B16 x≈10·212, y=9.15)
CYLS = {
    # 이름: (형번, 로컬X 세계방향, 로컬Y(포트) 세계방향, 어깨 자리, 이동 컴포넌트, 포트 x, 포트 면 y)
    "CJ2B10-15Z_M05_CUT": ("CJ2B10-15Z", (0, -1, 0), (0, 0, 1), (29, -174, 80.75), "U7_CUT", (7.9, 57.9), 6.0),
    "CJ2B10-15Z_M05_TUCK": ("CJ2B10-15Z", (0, -1, 0), (0, 0, -1), (29, -174, 54.6), "U7_TUCK", (7.9, 57.9), 6.0),
    "CDJ2B16-150AZ-B_M05_FEED": ("CDJ2B16-150AZ-B", (0, 0, 1), (1, 0, 0), (70, -106, 293), "U7_FEED", (10.0, 212.0), 9.15),
}
# STEP 바디 이름(준비 .sc에서 바꿈)
CYL_BODIES = {"CJ2B10-15Z": ("CJ2B10-15Z(1_0)_BODY", "CJ2B10-15Z_ROD", "SNJ-010C", "NTJ-010C"),
              "CDJ2B16-150AZ-B": ("CJ2B16-150AZ-B(1_0)_BODY", "CJ2B16-150AZ_ROD", "SNJ-016C", "NTJ-015C")}


def add(a, b, k=1.0):
    return tuple(a[i] + k * b[i] for i in range(3))


FITTINGS = []   # (이름, 포트 면 점, 포트 법선(로컬Y), 출구(로컬X), 컴포넌트)
for nm, (pn, ex, ey, t, mv, px, py) in CYLS.items():
    for i, x in enumerate(px):
        p = add(add(t, ex, x), ey, py)
        # 칼 머리 쪽 포트(Y -181.9, Z 86.75)는 출구 -X: -Y면 날개 볼트 CB5-12_M05_6(Y -195, Z 103) 렌치 길을 막는다.
        # 접기 머리 쪽 포트(Z 48.6)는 출구 -Y(수정 1회차): -X면 출구가 U6 슈·센서 공간(X -22~10)에서 4.5라 튜브 길이 없다.
        # 그 대신 막히는 날개 볼트 CB5-12_M05_5(Z 40)는 판 +X 쪽에서 넣는다(BOLTS, 날개 압입 너트).
        o = (-1, 0, 0) if (i == 0 and nm == "CJ2B10-15Z_M05_CUT") else (0, -1, 0)
        FITTINGS.append(("KQ2L06-M5A_M05_%d" % (len(FITTINGS) + 1), p, ey, o, "U7_CASSETTE"))

# 인서트 MBIS5-6.5-8: 로컬 X 0~8 = 박히는 방향, x=0 면
INSERTS = [((50, -116, 66), (-1, 0, 0), "U7_CASSETTE"), ((50, -116, 160), (-1, 0, 0), "U7_CASSETTE"),
           ((50, -116, 240), (-1, 0, 0), "U7_CASSETTE"),
           ((20, -100, 78), (0, 0, -1), "U7_CASSETTE"), ((38, -100, 78), (0, 0, -1), "U7_CASSETTE"),
           ((21, -144, 80), (0, 0, -1), "U7_CUT"), ((37, -144, 80), (0, 0, -1), "U7_CUT"),
           ((21, -144, 55.35), (0, 0, 1), "U7_TUCK"), ((37, -144, 55.35), (0, 0, 1), "U7_TUCK"),
           ((70, -106, 272), (0, 0, -1), "U7_FEED")]
# 볼트: 머리 밑면 점, 축(나사 방향), 형번, 컴포넌트, 메모
BOLTS = [((58, -80, 41.5), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 -> 바인더 브래킷"),
         ((58, -50, 41.5), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 -> 바인더 브래킷"),
         ((15, -80, 66), (0, 0, -1), "CB5-12", "U7_CASSETTE", "바인더 브래킷 -> 바인더"),
         ((15, -55, 66), (0, 0, -1), "CB5-12", "U7_CASSETTE", "바인더 브래킷 -> 바인더"),
         ((58, -116, 66), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 -> 안내 블록 인서트"),
         ((58, -116, 160), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 -> 안내 블록 인서트"),
         ((58, -116, 240), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 -> 안내 블록 인서트"),
         ((20, -100, 80), (0, 0, -1), "CB5-12", "U7_CASSETTE", "고정날 -> 안내 블록 인서트"),
         ((38, -100, 80), (0, 0, -1), "CB5-12", "U7_CASSETTE", "고정날 -> 안내 블록 인서트"),
         # 수정 2회차: CB5-12(물림 3.2, 조임 SF 0.62) -> CB5-16(너트 나사 6.01 전부 물림, 끝 X 42). 이름은 CB5-16_M05_10, CB5-12 번호 자리(_5)는 비워 다른 볼트 이름을 그대로 둔다.
         ((58, -195, 40), (-1, 0, 0), "CB5-16", "U7_CASSETTE", "판 +X -> 실린더 브래킷 날개 압입 너트(수정 1회차 튜브 길 비킴, 수정 2회차 CB5-16 조임 2.5 N·m)", ("CB5-12", "CB5-16_M05_10")),
         ((47, -195, 103), (1, 0, 0), "CB5-12", "U7_CASSETTE", "실린더 브래킷 -> 판 탭"),
         ((61, -140, 262), (-1, 0, 0), "CB5-12", "U7_CASSETTE", "보내기 브래킷 -> 판 탭"),
         ((61, -128, 278), (-1, 0, 0), "CB5-12", "U7_CASSETTE", "보내기 브래킷 -> 판 탭"),
         ((60, -180, 314), (-1, 0, 0), "CB5-12", "U7_CASSETTE", "걸쇠 -> 판 탭"),
         ((60, -164, 314), (-1, 0, 0), "CB5-12", "U7_CASSETTE", "걸쇠 -> 판 탭"),
         ((21, -144, 88), (0, 0, -1), "CB5-16", "U7_CUT", "칼 홀더·칼 -> 인서트"),
         ((37, -144, 88), (0, 0, -1), "CB5-16", "U7_CUT", "칼 홀더·칼 -> 인서트"),
         ((21, -144, 45.5), (0, 0, 1), "CB5-16", "U7_TUCK", "접기 홀더 밑에서 -> 날 -> 위 턱 인서트(위는 칼 홀더가 막음)"),
         ((37, -144, 45.5), (0, 0, 1), "CB5-16", "U7_TUCK", "접기 홀더 밑에서 -> 날 -> 위 턱 인서트(위는 칼 홀더가 막음)"),
         ((18, -94, 310), (0, 1, 0), "CB5-12", "U7_FIXED", "걸이 날개 A -> UPPER 탭"),
         ((36, -94, 310), (0, 1, 0), "CB5-12", "U7_FIXED", "걸이 날개 A -> UPPER 탭")]


def bolt_names():
    out, n = [], {"CB5-12": 0, "CB5-16": 0}
    for b in BOLTS:
        if len(b) > 5:  # 이름 고정(수정 회차에 형번만 바뀐 볼트): 원래 형번 번호 자리를 쓴다
            n[b[5][0]] += 1
            out.append(b[5][1])
            continue
        n[b[2]] += 1
        out.append("%s_M05_%d" % (b[2], n[b[2]]))
    return out


def purchased():
    """(이름, 형번, matrix, 컴포넌트, 바디 이름 바꾸기, 준비에서 지울 바디)"""
    L = []
    for nm, (pn, ex, ey, t, mv, px, py) in CYLS.items():
        B, R, S, N = CYL_BODIES[pn]
        L.append((nm, pn, mat_loc(ex, ey, t), "U7_CASSETTE", [(B, nm), (S, nm + "_NUT_MNT")], [R, N]))
        L.append((nm + "_ROD", pn, mat_loc(ex, ey, t), mv, [(R, nm + "_ROD"), (N, nm + "_NUT_ROD")], [B, S]))
    for nm, p, n, o, comp in FITTINGS:
        L.append((nm, "KQ2L06-M5A", mat_loc(o, n, p), comp, [("KQ2L06-M5A", nm)], []))
    for i, (p, d, comp) in enumerate(INSERTS):
        nm = "MBIS5-6.5-8_M05_%d" % (i + 1)
        L.append((nm, "MBIS5-6.5-8", mat_loc(d, perp(d), p), comp, [("MBIS5-6.5-8", nm)], []))
    for nm, (p, d, pn, comp, memo, *_) in zip(bolt_names(), BOLTS):
        L.append((nm, pn, mat_loc(d, perp(d), p), comp, [("Cut-Extrude1", nm)], []))
    return L


def gen_parts():
    os.makedirs(OUT + "/parts", exist_ok=True)
    jobs = []
    for nm, pn, M, comp, ren, rm in purchased():
        s = [C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=nm, matrix=M)]
        if rm:
            s.append(C("solid.remove", bodies=rm))
        s += [C("body.rename", body=a, name=b) for a, b in ren]
        s.append(C("inspect.measure"))
        fn = OUT + "/parts/prep_%s.json" % nm
        json.dump(s, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        jobs.append(nm)
    json.dump(jobs, open(OUT + "/parts/jobs.json", "w", encoding="utf-8"))
    print(len(jobs), "prep scripts")


# ---------------------------------------------------------------- 스케치 도우미
def plane(origin, xd, yd):
    return {"origin": list(origin), "x_dir": list(xd), "y_dir": list(yd)}


def unit(v):
    n = (v[0] ** 2 + v[1] ** 2) ** 0.5
    return (v[0] / n, v[1] / n)


def rloop(pts, r):
    """닫힌 다각형의 모든 모서리를 r로 둥글린 선·호 명령(2D)."""
    n = len(pts)
    T1, T2, M = [], [], []
    for i in range(n):
        P, Q, N = pts[i - 1], pts[i], pts[(i + 1) % n]
        u1, u2 = unit((P[0] - Q[0], P[1] - Q[1])), unit((N[0] - Q[0], N[1] - Q[1]))
        t1 = (Q[0] + r * u1[0], Q[1] + r * u1[1])
        t2 = (Q[0] + r * u2[0], Q[1] + r * u2[1])
        c = (Q[0] + r * (u1[0] + u2[0]), Q[1] + r * (u1[1] + u2[1]))
        w = unit((Q[0] - c[0], Q[1] - c[1]))
        T1.append(t1); T2.append(t2); M.append((c[0] + r * w[0], c[1] + r * w[1]))
    s = []
    rr = lambda q: [r4(q[0]), r4(q[1])]
    for i in range(n):
        s.append(C("sketch.arc.three_point", start=rr(T1[i]), through=rr(M[i]), end=rr(T2[i])))
        s.append(C("sketch.line", points=[rr(T2[i]), rr(T1[(i + 1) % n])]))
    return s


def prism(name, pl, pts, dist, r=0.0, inner=None, op="new", tg=None, direction=None):
    sk = "SK_" + name
    s = [C("sketch.create", plane=pl, name=sk)]
    s += rloop(pts, r) if r > 0 else [C("sketch.line", points=[[r4(a), r4(b)] for a, b in pts], closed=True)]
    if inner:
        for ipts, ir in inner:
            s += rloop(ipts, ir)
    s.append(C("sketch.finish"))
    p = {"sketch": sk, "distance": r4(dist), "operation": op}
    if op == "new":
        p["body_name"] = name
    else:
        p["targets"] = tg
    if direction:
        p["direction"] = direction
    s.append(C("solid.extrude", **p))
    return s


def YZ(x):
    return plane((x, 0, 0), (0, 1, 0), (0, 0, 1))      # 법선 +X, (u, v) = (Y, Z)


def XY(z):
    return plane((0, 0, z), (1, 0, 0), (0, 1, 0))      # 법선 +Z, (u, v) = (X, Y)


def XZ(y):
    return plane((0, y, 0), (1, 0, 0), (0, 0, 1))      # 법선 -Y, (u, v) = (X, Z)


# 가공품 이름
PLATE, BBRKT, GUIDE, CFIX, CBRKT = "P_M05_CST_PLATE", "P_M05_BINDER_BRKT", "P_M05_GUIDE", "P_M05_CUT_FIX", "P_M05_CYL_BRKT"
CHOLD, CBLADE, THOLD, TBLADE = "P_M05_CUT_HOLDER", "P_M05_CUT_BLADE", "P_M05_TUCK_HOLDER", "P_M05_TUCK_BLADE"
FBRKT, FCARR, HOLDER = "P_M05_FEED_BRKT", "P_M05_FEED_CARR", "P_M05_HOLDER"
PIN1, PIN2, LATCH, HOOK = "STEP대기_MSTH6-20_M05_1", "STEP대기_MSTH6-20_M05_2", "STEP대기_KC-40340_M05", "STEP대기_KC-40340_M05_HOOK"
NUT = "STEP대기_S-M5-2_M05"   # 수정 1회차: 실린더 브래킷 날개 압입 너트(형번 임시, PEM S-M5-2 상당)

MADE = {  # 바디: (컴포넌트, 재질)
    PLATE: ("U7_CASSETTE", "A5052"), BBRKT: ("U7_CASSETTE", "A5052"), GUIDE: ("U7_CASSETTE", "PA12"),
    CFIX: ("U7_CASSETTE", "SK5"), CBRKT: ("U7_CASSETTE", "SUS304"), FBRKT: ("U7_CASSETTE", "SUS304"),
    PIN1: ("U7_CASSETTE", "Steel"), NUT: ("U7_CASSETTE", "Steel"), PIN2: ("U7_CASSETTE", "Steel"), LATCH: ("U7_CASSETTE", "Steel"),
    CHOLD: ("U7_CUT", "PA12"), CBLADE: ("U7_CUT", "SK5"), THOLD: ("U7_TUCK", "PA12"), TBLADE: ("U7_TUCK", "SUS304"),
    FCARR: ("U7_FEED", "PA12"), HOOK: ("U7_LATCH", "Steel"), HOLDER: ("U7_FIXED", "SUS304")}


def st_prep():
    s = [C("material.create", name="PA12", density_g_cm3=1.01, color="#e8e4da"),
         C("material.create", name="SK5", density_g_cm3=7.85, color="#5f6670"),
         C("solid.remove", bodies=["U7_PATH_V"])]
    for nm, par in [("U7_FIXED", 0), ("U7_CST_STAGE", 0), ("U7_CASSETTE", 0),
                    ("U7_CUT", "U7_CASSETTE"), ("U7_TUCK", "U7_CASSETTE"), ("U7_FEED", "U7_CASSETTE"), ("U7_LATCH", "U7_CASSETTE")]:
        s.append(C("component.create", name=nm, parent=par, activate=False))
    s.append(C("component.move_bodies", bodies=["U7_BINDER"], component="U7_CASSETTE"))
    # 기존 바디에 탭: UPPER -Y 면 M5 2 깊이 10, 바인더 윗면 M5 2 깊이 8
    s += [cy(2.1, x, 310, -90.1, -80, "cut", [UPPER]) for x in (18, 36)]
    s += [cz(2.1, 15, y, 52, 60.1, "cut", ["U7_BINDER"]) for y in (-80, -55)]
    return s


def st_cassette():
    s = []
    # 판 A5052 t8, X 50~58, 모서리 R5, 손 구멍 40x40 R10
    out = [(-200, 20), (-40, 20), (-40, 75), (-106, 75), (-106, 328), (-200, 328)]
    hole = [(-190, 200), (-150, 200), (-150, 240), (-190, 240)]
    s += prism(PLATE, YZ(50), out, 8, r=5.0, inner=[(hole, 10.0)])
    s += [cx(3.0, y, z, 49, 59, "cut", [PLATE]) for (y, z) in [(-190, 300), (-125, 300)]]
    s += [cx(2.75, y, z, 49, 59, "cut", [PLATE]) for (y, z) in [(-80, 41.5), (-50, 41.5), (-116, 66), (-116, 160), (-116, 240), (-195, 40)]]
    s += [cx(2.1, y, z, 49, 59, "cut", [PLATE]) for (y, z) in [(-195, 103), (-140, 262), (-128, 278), (-180, 314), (-164, 314)]]
    # 바인더 브래킷 A5052 L: 세운 X 42~50 · Z 25~66, 누운 X 0~50 · Z 60~66, Y -90~-40
    s += prism(BBRKT, XZ(-40), [(0, 60), (42, 60), (42, 25), (50, 25), (50, 66), (0, 66)], 50)
    s += [cx(2.1, y, 41.5, 41.9, 50.1, "cut", [BBRKT]) for y in (-80, -50)]
    for y in (-80, -55):   # Y 장공 ±3
        s += [box(None, 12.25, 17.75, y - 3, y + 3, 59.9, 66.1, "cut", [BBRKT]),
              cz(2.75, 15, y - 3, 59.9, 66.1, "cut", [BBRKT]), cz(2.75, 15, y + 3, 59.9, 66.1, "cut", [BBRKT])]
    # 안내 블록 PA12
    s += prism(GUIDE, YZ(12), [(-122, 38), (-96, 38), (-96, 78), (-104.5, 78), (-104.5, 270), (-122, 270)], 38)   # 윗부분 뒷면 -104.5(고정날 볼트 머리 -104.25 비킴)
    s += [box(None, 13.5, 44.5, -111, -109, 48, 271, "cut", [GUIDE])]                       # 테이프 홈 31x2
    s += prism("M05_CHUTE", YZ(13.5), [(-111, 48), (-95, 40.5333), (-95, 42.4615), (-109, 50), (-109, 52), (-111, 52)],
               31, op="cut", tg=[GUIDE])                                                     # 굽은 슈트 -> Y -96 면 Z 41~43
    s += [box(None, 12.5, 45.5, -114, -106, 262, 271, "cut", [GUIDE]),                      # 위 깔때기
          box(None, 13, 45, -123, -109, 79.75, 82, "cut", [GUIDE]),                         # 앞 슬롯 칼
          box(None, 13, 45, -123, -109, 53.4, 55.8, "cut", [GUIDE]),                        # 앞 슬롯 접기
          box(None, 13, 45, -109, -103, 80, 82, "cut", [GUIDE]),                            # 뒤 칼 통과
          box(None, 13, 45, -109, -104, 52, 57.5, "cut", [GUIDE]),                          # 접기 주머니
          box(None, 23, 35, -109, -103, 90, 271, "cut", [GUIDE]),                           # 발톱 슬롯(위로 열림)
          box(None, 13, 45, -109.5, -95, 78, 80, "cut", [GUIDE])]                           # 고정날 자리
    s += [cx(3.4, -116, z, 42, 50.1, "cut", [GUIDE]) for z in (66, 160, 240)]               # 인서트 자리 X 50 면
    s += [cz(3.4, x, -100, 70, 78.1, "cut", [GUIDE]) for x in (20, 38)]                      # 인서트 자리 턱 윗면
    s += [cz(2.6, x, -100, 66, 70.1, "cut", [GUIDE]) for x in (20, 38)]                      # 볼트 끝 비킴
    # 고정날 SK5 t2
    s += [box(CFIX, 13, 45, -109.5, -95.5, 78, 80)]
    s += [cz(2.75, x, -100, 77.9, 80.1, "cut", [CFIX]) for x in (20, 38)]
    # 실린더 브래킷 SUS304 t3 L (판 Y -174~-171: 실린더 STEP 어깨 실측으로 지시 -177~-174에서 +3)
    s += prism(CBRKT, XY(34), [(14, -174), (47, -174), (47, -204), (50, -204), (50, -171), (14, -171)], 76)
    s += [cy(4.25, 29, z, -174.1, -170.9, "cut", [CBRKT]) for z in (80.75, 54.6)]
    s += [cx(3.57, -195, 40, 46.9, 50.1, "cut", [CBRKT]), cx(2.75, -195, 103, 46.9, 50.1, "cut", [CBRKT])]   # Z 40: 압입 너트 구멍 Ø7.14
    # STEP대기 압입 너트 S-M5-2(자루 Ø7.1 x 2.2 날개 안, 몸 Ø9.73 x 3.81 날개 -X 면, 나사 M5 = Ø4.2 자리)
    s += [cx(4.865, -195, 40, 43.19, 47, "new", name=NUT), cx(3.55, -195, 40, 47, 49.2, "join", [NUT]),
          cx(2.1, -195, 40, 43.09, 49.3, "cut", [NUT])]
    # 보내기 브래킷 SUS304 t3 L (누운 다리 Z 290~293: 실린더 어깨 실측으로 지시 293~296에서 -3)
    s += prism(FBRKT, XZ(-96), [(58, 250), (61, 250), (61, 290), (82, 290), (82, 293), (58, 293)], 49)
    s += [box(None, 57, 62, -115, -95, 249, 290, "cut", [FBRKT])]
    s += [cz(5.25, 70, -106, 289, 294, "cut", [FBRKT])]
    s += [cx(2.75, y, z, 57.9, 61.1, "cut", [FBRKT]) for (y, z) in [(-140, 262), (-128, 278)]]
    # STEP대기 핀 MSTH6-20 (판에 8 압입, -X로 12)
    s += [cx(3.0, -190, 300, 38, 58, "new", name=PIN1), cx(3.0, -125, 300, 38, 58, "new", name=PIN2)]
    # STEP대기 걸쇠 KC-40340: 밑판 t2 + 몸(닫힘) / 갈고리는 U7_LATCH
    s += [box(LATCH, 58, 60, -182, -162, 300, 328), box(None, 60, 88, -175.25, -168.75, 302, 326, "join", [LATCH])]
    s += [cx(2.75, y, 314, 57.9, 60.1, "cut", [LATCH]) for y in (-180, -164)]
    s += [box(HOOK, 64, 72, -178, -166, 326, 340), box(None, 26, 64, -178, -166, 335, 340, "join", [HOOK]),
          box(None, 27, 33, -173.5, -170.5, 331, 335, "join", [HOOK])]
    return s


def st_moving():
    s = []
    # 칼 홀더 PA12 + 칼 SK5 t1.5 (뒤 다리 3, 칼 뒤 끝 -148 + 로드 비킴 홈)
    s += [box(CHOLD, 16, 42, -151, -138, 72, 88), box(None, 15, 43, -148, -137, 80, 81.5, "cut", [CHOLD]),
          cy(2.1, 29, 80.75, -151.1, -146, "cut", [CHOLD])]
    s += [cz(3.4, x, -144, 72, 80.05, "cut", [CHOLD]) for x in (21, 37)]
    s += [cz(2.75, x, -144, 81.45, 88.1, "cut", [CHOLD]) for x in (21, 37)]
    s += prism(CBLADE, XY(80), [(13, -148), (26, -148), (26, -145.5), (32, -145.5), (32, -148), (45, -148), (45, -120), (13, -123.4)], 1.5)
    s += [cz(2.75, x, -144, 79.9, 81.6, "cut", [CBLADE]) for x in (21, 37)]
    # 접기 홀더 PA12 + 날 SUS304 t1.5 끝 R0.75
    s += [box(THOLD, 16, 42, -151, -138, 45.5, 64), box(None, 15, 43, -148, -137, 53.85, 55.35, "cut", [THOLD]),
          cy(2.1, 29, 54.6, -151.1, -146, "cut", [THOLD])]
    s += [cz(3.4, x, -144, 55.3, 63.35, "cut", [THOLD]) for x in (21, 37)]        # 위 턱 인서트 자리(볼트는 밑에서)
    s += [cz(2.75, x, -144, 45.4, 53.9, "cut", [THOLD]) for x in (21, 37)]
    s += [box(TBLADE, 14, 44, -148, -120.75, 53.85, 55.35), cx(0.75, -120.75, 54.6, 14, 44, "join", [TBLADE]),
          box(None, 26, 32, -148.1, -145.5, 53.75, 55.45, "cut", [TBLADE])]
    s += [cz(2.75, x, -144, 53.75, 55.45, "cut", [TBLADE]) for x in (21, 37)]
    # 보내기 캐리지 PA12: 몸 + 팔 + 발톱(손가락 + 휨 목 1.5)
    s += [box(FCARR, 61, 79, -110, -98.5, 245, 272), box(None, 24, 61, -102.5, -98.5, 255, 265, "join", [FCARR]),
          box(None, 24, 34, -109.5, -106, 245, 260, "join", [FCARR]), box(None, 24, 34, -106, -102.5, 258.5, 260, "join", [FCARR]),
          cz(3.4, 70, -106, 264, 272.1, "cut", [FCARR])]
    return s


def st_fixed():
    s = prism(HOLDER, XY(285), [(10, -94), (46, -94), (46, -200), (50, -200), (50, -90), (10, -90)], 49)
    s += [box(None, 18, 46, -200, -150, 330, 334, "join", [HOLDER])]
    s += [cy(2.75, x, 310, -94.1, -89.9, "cut", [HOLDER]) for x in (18, 36)]
    s += [cx(3.0, -190, 300, 45.9, 50.1, "cut", [HOLDER]),
          box(None, 45.9, 50.1, -126, -124, 297, 303, "cut", [HOLDER]),
          cx(3.0, -126, 300, 45.9, 50.1, "cut", [HOLDER]), cx(3.0, -124, 300, 45.9, 50.1, "cut", [HOLDER])]
    s += [cx(3.5, y, 314, 45.9, 50.1, "cut", [HOLDER]) for y in (-180, -164)]
    s += [box(None, 25, 35, -174, -170, 329.9, 334.1, "cut", [HOLDER])]
    return s


def st_assign():
    s = []
    comps = {}
    for b, (c, m) in MADE.items():
        comps.setdefault(c, []).append(b)
    for c, bs in comps.items():
        s.append(C("component.move_bodies", bodies=bs, component=c))
    mats = {}
    for b, (c, m) in MADE.items():
        mats.setdefault(m, []).append(b)
    for m, bs in mats.items():
        s.append(C("material.assign", bodies=bs, material=m))
    return s


# 너트 옮김(insert 뒤, 세계 mm): 실린더 브래킷 판·홀더·캐리지에 맞닿게
NUT_MOVES = {
    "CJ2B10-15Z_M05_CUT": [("_NUT_MNT", (0, 1.4, 0)), ("_NUT_ROD", (0, -0.2, 0)), ("_NUT_ROD2", (0, -0.7, 0))],
    "CJ2B10-15Z_M05_TUCK": [("_NUT_MNT", (0, 1.4, 0)), ("_NUT_ROD", (0, -0.2, 0)), ("_NUT_ROD2", (0, -0.7, 0))],
    "CDJ2B16-150AZ-B_M05_FEED": [("_NUT_MNT", (0, 0, -0.7)), ("_NUT_ROD", (0, 0, 1.0)), ("_NUT_ROD2", (0, 0, 3.5))],
}


def st_purchased():
    s = []
    for nm, pn, M, comp, ren, rm in purchased():
        s += [C("component.insert_design", path="%s/%s.sc" % (PARTS, nm), name=nm, parent=comp),
              C("component.break_link", component=nm)]
        if nm.endswith("_ROD"):
            base = nm[:-4]
            NTJ = CYL_BODIES[pn][3]
            s.append(C("body.rename", body="%s_NUT_ROD (%s:1/%s:2)" % (base, nm, NTJ), name=base + "_NUT_ROD2"))
            s.append(C("component.metadata.set", component=nm, part_number=pn, bom_type="reference",
                       description="rod, piston and rod-end nuts of %s (moving part of the same cylinder)" % base))
        else:
            s.append(C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased"))
    for base, mv in NUT_MOVES.items():
        for suf, t in mv:
            s.append(C("solid.move", bodies=[base + suf], translate=list(t)))
    # 재질(기존 구매품과 같은 식: 볼트 SCM435, 실린더 몸 Aluminum, 로드·너트 Steel, 인서트·피팅 Default 그대로)
    s.append(C("material.assign", bodies=bolt_names(), material="SCM435"))
    s.append(C("material.assign", bodies=list(CYLS.keys()), material="Aluminum"))
    s.append(C("material.assign", bodies=[b + suf for b in CYLS for suf in ("_ROD", "_NUT_MNT", "_NUT_ROD", "_NUT_ROD2")], material="Steel"))
    return s


U7J = ["J_U7_CST_X", "J_U7_CST_Y", "J_U7_CUT", "J_U7_TUCK", "J_U7_FEED", "J_U7_LATCH"]
JOINTS = [("J_U7_CST_X", "U7_FIXED:1", "U7_CST_STAGE:1", (1, 0, 0), (0, 25), (50, -150, 300)),
          ("J_U7_CST_Y", "U7_CST_STAGE:1", "U7_CASSETTE:1", (0, -1, 0), (0, 250), (50, -150, 300)),
          ("J_U7_CUT", "U7_CASSETTE:1", "U7_CUT:1", (0, 1, 0), (0, 15), (29, -146, 80.75)),
          ("J_U7_TUCK", "U7_CASSETTE:1", "U7_TUCK:1", (0, 1, 0), (0, 15), (29, -146, 54.6)),
          ("J_U7_FEED", "U7_CASSETTE:1", "U7_FEED:1", (0, 0, -1), (0, 150), (70, -106, 265)),
          ("J_U7_LATCH", "U7_CASSETTE:1", "U7_LATCH:1", (0, 0, 1), (0, 12), (68, -172, 326))]


def st_joints():
    s = [C("joint.rigid_group", occurrences=["U3_HEAD:1", "U7_FIXED:1"])]
    for nm, a, b, z, lim, o in JOINTS:
        s.append(C("joint.create", type="slider", name=nm, flip=True, quiet=True, limits=[list(lim)],
                   a={"occurrence": a, "point": list(o), "z": list(z)}, b={"occurrence": b, "point": list(o), "z": list(z)}))
    return s


def val_at(points, step):
    if step <= points[0][0]:
        return points[0][1]
    for (a, va), (b, vb) in zip(points, points[1:]):
        if a <= step <= b:
            return va if b == a else va + (vb - va) * (step - a) / (b - a)
    return points[-1][1]


def thin(pts):
    out = []
    for i, p in enumerate(pts):
        if 0 < i < len(pts) - 1 and abs(pts[i - 1][1] - p[1]) < 1e-9 and abs(pts[i + 1][1] - p[1]) < 1e-9:
            continue
        out.append(p)
    return out


def pose(K, study, step):
    return {k["joint"]: val_at(k["points"], step) for k in K[study]["keys"]}


SEAM_POSES = [("CYCLE_L", 660), ("CYCLE_S", 432), ("CYCLE_G2", 572)]
FEED_POSES = [("CYCLE_L", 716), ("CYCLE_S", 450), ("CYCLE_G2", 630)]


def seam_rows(K):
    rows, tags = [], []
    for st, stp in SEAM_POSES:
        p = pose(K, st, stp); p["J_U3_PRESSER"] = 0.0; p["J_U3_NEEDLE"] = -30.0
        for cut, tuck in [(0, 0), (7.5, 0), (15, 0), (0, 0), (0, 7.5), (0, 15), (0, 0)]:
            q = dict(p); q.update({"J_U7_CUT": cut, "J_U7_TUCK": tuck, "J_U7_FEED": 0}); rows.append(q); tags.append("%s %d" % (st, stp))
    for st, stp in FEED_POSES:
        p = pose(K, st, stp); p["J_U3_PRESSER"] = 20.0; p["J_U3_NEEDLE"] = 0.0
        for f in (0, 75, 150, 0):
            q = dict(p); q.update({"J_U7_CUT": 0, "J_U7_TUCK": 0, "J_U7_FEED": f}); rows.append(q); tags.append("%s %d" % (st, stp))
    return rows, tags


def st_studies():
    K = json.load(open(OUT + "/keys_base.json", encoding="utf-8"))
    base_j = [k["joint"] for k in K["REST"]["keys"]]
    s = []
    # REST: 기존 16키 그대로 + U7 6개 0
    ks = [{"joint": k["joint"], "points": [[a, round(b, 4)] for a, b in k["points"]]} for k in K["REST"]["keys"]]
    ks += [{"joint": j, "points": [[0, 0], [1, 0]]} for j in U7J]
    s.append(C("motion.study", study="REST", steps=1, keys=ks))
    rows, tags = seam_rows(K)
    jn = base_j + ["J_U7_CUT", "J_U7_TUCK", "J_U7_FEED"]
    ks = [{"joint": j, "points": thin([[i, round(r[j], 4)] for i, r in enumerate(rows)])} for j in jn]
    s.append(C("motion.study", name="SEAM_U7", steps=len(rows) - 1, keys=ks))
    # MAINT_U7: REST, 걸쇠 열림 12, CST_X 12.5·25, CST_Y 25~250
    r0 = pose(K, "REST", 0)
    ks = [{"joint": j, "points": [[0, round(r0[j], 4)], [13, round(r0[j], 4)]]} for j in base_j]
    ks += [{"joint": "J_U7_LATCH", "points": [[0, 0], [1, 12], [13, 12]]},
           {"joint": "J_U7_CST_X", "points": [[0, 0], [1, 0], [2, 12.5], [3, 25], [13, 25]]},
           {"joint": "J_U7_CST_Y", "points": [[0, 0], [3, 0], [13, 250]]}]
    s.append(C("motion.study", name="MAINT_U7", steps=13, keys=ks))
    return s, rows


def st_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="M05 mechanism: U7 tape tool cassette - binder, guide, cutter and tuck cylinders, lead-end feed, pins and latch (one-touch)")]


def build():
    s = st_prep() + st_cassette() + st_moving() + st_fixed() + st_assign() + st_purchased() + st_joints()
    ss, rows = st_studies()
    return s + ss + st_final(), rows


if __name__ == "__main__":
    if "--parts" in sys.argv:
        gen_parts()
    else:
        s, rows = build()
        json.dump(s, open(OUT + "/edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(len(s), "commands; SEAM_U7 rows", len(rows))
