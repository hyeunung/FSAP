# 디테일링 DP-2 수정 1회차(모델링부) 생성기: v0.6.6 -> v0.6.7
# 지시: 검증 문제 4건 + PM 예외 판정 DP2-X03(안 (a) 웹 밑 탭 너트판).
#  (1)(2) STEP대기_LBNR4_T01_* 24개 삭제 -> P_T01_NUTPLATE_R<링>_<스파이더> 6장(A5052 t6 □40, Ø28.4, M4 관통 탭 ×4 PCD38 대각, Z -104.5~-98.5, 바깥 모서리 C0.5)
#  (3) 스파이더 발 누름판 P_T01_FOOTPLATE_<스파이더>_<N|P> 6장(A5052 t6, 옆 34~52 × 축 방향 r100~145, Z -230~-224, 다리 쪽 C1)
#      CB5-12_T01_SP* 12개 -> STEP대기_CB5-18_T01_SP* 12개(머리 자리 -224, 끝 -242, 허브 물림 8) — CB5-18 STEP 없음(stepcheck, 같은 계열 CB5-12·16·20)
#  (4) P_T01_POST 밑 플랜지 윗면 -224.5 -> -221(t12) + 볼트 자리 카운터보어 Ø9.5 × 3.5(머리 자리 -224.5 그대로)
# 좌표: 대기 세계 좌표(gen_dp2_detail.py 와 같음).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp2_r1.py   -> tools/out/detail/DP-2/r1/build.json
#   solidcraft-cli run tools/out/detail/DP-2/r1/build.json --in 3D_Modeling/FSAP_v0.6.6.sc --save 3D_Modeling/FSAP_v0.6.7.sc
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-2', 'r1')
os.makedirs(OUT, exist_ok=True)
AX = (0.0, -700.0)
TH3 = (90.0, 210.0, 330.0)
S = []
INFO = {"nutplates": [], "footplates": [], "bolts": []}


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def uv(th):
    t = math.radians(th)
    u = (math.cos(t), math.sin(t))
    return u, (-u[1], u[0])


def pt(th, r, a=0.0):
    u, v = uv(th)
    return (r6(AX[0] + r * u[0] + a * v[0]), r6(AX[1] + r * u[1] + a * v[1]))


def polar(r, deg):
    t = math.radians(deg)
    return (r6(AX[0] + r * math.cos(t)), r6(AX[1] + r * math.sin(t)))


def cylz(d, x, y, z0, z1, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(z1 - z0), "base": [r6(x), r6(y), r6(z0)], "axis": "Z"}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def prism(name, sk, origin, xd, yd, pts, dist):
    C("sketch.create", {"plane": {"origin": [r6(v) for v in origin], "x_dir": [r6(v) for v in xd], "y_dir": [r6(v) for v in yd]}, "name": sk})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": dist, "body_name": name})


def hexpts(af, rot=0.0):
    rc = af / math.sqrt(3)
    return [(rc * math.cos(math.radians(30 + 60 * k + rot)), rc * math.sin(math.radians(30 + 60 * k + rot))) for k in range(6)]


C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ================= (1)(2) LBNR4 24 삭제 -> 탭 너트판 6장 =================
C("component.activate", {"component": "root"})
for ring in ("R1", "R2"):
    for i in (1, 2, 3):
        for k in (1, 2, 3, 4):
            C("component.delete", {"component": "STEP대기_LBNR4_T01_%s_%d_%d" % (ring, i, k)})
C("component.activate", {"component": "MAT_ROT"})
for ring, rr in (("R1", 240), ("R2", 460)):
    for i, th in enumerate(TH3, 1):
        u, v = uv(th)
        x0, y0 = pt(th, rr)
        nm = "P_T01_NUTPLATE_%s_%d" % (ring, i)
        prism(nm, "SK_DP2R1_NP_%s_%d" % (ring, i), [x0, y0, -104.5], [u[0], u[1], 0], [v[0], v[1], 0],
              [(-20, -20), (20, -20), (20, 20), (-20, 20)], 6)
        E = []
        for z in (-104.5, -98.5):
            for su, sv in ((20, 0), (-20, 0), (0, 20), (0, -20)):
                E.append([r6(x0 + su * u[0] + sv * v[0]), r6(y0 + su * u[1] + sv * v[1]), z])
        for su, sv in ((20, 20), (20, -20), (-20, 20), (-20, -20)):
            E.append([r6(x0 + su * u[0] + sv * v[0]), r6(y0 + su * u[1] + sv * v[1]), -101.5])
        C("solid.chamfer", {"edges": E, "distance": 0.5, "body": nm})                    # 바깥 모서리 C0.5 (12)
        cylz(28.4, x0, y0, -105, -98, op="cut", targets=[nm])                            # 가운데 Ø28.4
        for k in range(4):
            q = math.radians(th + 45 + 90 * k)
            cylz(3.3, x0 + 19 * math.cos(q), y0 + 19 * math.sin(q), -105, -98, op="cut", targets=[nm])   # M4 관통 탭(기초 구멍 Ø3.3)
        C("material.assign", {"bodies": [nm], "material": "A5052"})
        INFO["nutplates"].append({"name": nm, "c": [x0, y0], "th": th})

# ================= (3) 발 누름판 6장 + CB5-12 -> STEP대기_CB5-18 =================
for i, th in enumerate(TH3, 1):
    u, v = uv(th)
    for tag, a0, a1, ac in (("N", -52, -34, -34), ("P", 34, 52, 34)):
        nm = "P_T01_FOOTPLATE_%d_%s" % (i, tag)
        o = pt(th, 100)
        prism(nm, "SK_DP2R1_FP_%d_%s" % (i, tag), [o[0], o[1], -230], [u[0], u[1], 0], [v[0], v[1], 0],
              [(0, a0), (45, a0), (45, a1), (0, a1)], 6)
        C("solid.chamfer", {"edges": [list(pt(th, 122.5, ac)) + [-230], list(pt(th, 122.5, ac)) + [-224]], "distance": 1, "body": nm})   # 다리 쪽 C1
        for rr in (110, 135):
            x, y = pt(th, rr, 44 if tag == "P" else -44)
            cylz(5.5, x, y, -231, -223, op="cut", targets=[nm])
        C("material.assign", {"bodies": [nm], "material": "A5052"})
        INFO["footplates"].append({"name": nm, "th": th, "a": [a0, a1]})

C("component.activate", {"component": "root"})
FEET = []
for i, th in enumerate(TH3):
    for rr in (110, 135):
        for a in (-44, 44):
            FEET.append((i + 1,) + pt(th, rr, a))
for j, (si, x, y) in enumerate(FEET, 1):
    C("component.delete", {"component": "CB5-12_T01_SP%d_%d" % (si, (j - 1) % 4 + 1)})
for j, (si, x, y) in enumerate(FEET, 1):
    nm = "STEP대기_CB5-18_T01_SP%d_%d" % (si, (j - 1) % 4 + 1)
    C("component.activate", {"component": "MAT_ROT"})
    C("component.create", {"name": nm, "parent": "MAT_ROT", "activate": True, "grounded": False})
    cylz(8.5, x, y, -224, -219, nm)
    cylz(5, x, y, -242, -223.8, op="join", targets=[nm])
    prism("T_DP2R1_S5_%d" % j, "SK_DP2R1_S5_%d" % j, [x, y, -222], [1, 0, 0], [0, 1, 0], hexpts(4), 3)
    C("solid.combine", {"target": nm, "tools": ["T_DP2R1_S5_%d" % j], "operation": "cut"})
    C("material.assign", {"bodies": [nm], "material": "Steel"})
    C("component.metadata.set", {"component": nm, "part_number": "CB5-18", "bom_type": "purchased",
                                 "description": "MISUMI 육각 구멍붙이 볼트 M5×18 (STEP 대기 D-37, 임시 형상 JIS B 1176 머리 Ø8.5×5 + 몸통 Ø5, 육각 구멍 4) — 발 누름판 t6 + 스파이더 발 t3 → 허브 t8 탭(물림 8, DP-2 수정 1)"})
    INFO["bolts"].append({"name": nm, "pn": "CB5-18", "xy": [x, y], "head_top": -219, "seat": -224, "tip": -242})

# ================= (4) P_T01_POST 밑 플랜지 t8.5 -> t12 + 카운터보어 Ø9.5 × 3.5 =================
C("component.activate", {"component": "MAT_ROT"})
cylz(120, AX[0], AX[1], -224.5, -221, op="join", targets=["P_T01_POST"])
cylz(40, AX[0], AX[1], -234, -220, op="cut", targets=["P_T01_POST"])
for ang in (30.0, 150.0, 270.0):
    x, y = polar(50, ang)
    cylz(5.5, x, y, -234, -220, op="cut", targets=["P_T01_POST"])
    cylz(9.5, x, y, -224.5, -220, op="cut", targets=["P_T01_POST"])
C("material.assign", {"bodies": ["P_T01_POST"], "material": "PET-CF"})

# ================= 컴포넌트 속성 =================
C("component.activate", {"component": "root"})
PROPS = {
    "P_T01_HUB": "SUS304 / 레이저 평판 t8 / R20~R150 Z-241~-233(DP-2 t6->t8, 윗면 +2). 구멍: DG 테이블 Ø6.6 ×6 PCD155, 스파이더 발 M5 관통 탭 ×12, 기둥 M5 관통 탭 ×3 r50",
    "P_T01_SPIDER_1": "A5052 / 판금 t3 모자형(굽힘 4, 안 R3, K 0.44) / 웹 Z-98.5~-95.5, 다리 X±27~30, 바깥 발 폭 22 Z-233~-230, r100~490. 구멍: 부시 Ø28.4 ×2 + 플랜지 Ø4.5 ×8(대각), SNJ Ø10.5 ×2, 발 Ø5.5 ×4. 깊은 ㄷ 절곡은 업체 확인(D-42), 안 되면 3분할",
    "P_T01_SPIDER_2": "A5052 / 판금 t3 모자형 / 스파이더1과 같은 모양(허브 중심 +120°)",
    "P_T01_SPIDER_3": "A5052 / 판금 t3 모자형 / 스파이더1과 같은 모양(허브 중심 -120°)",
    "P_T01_POST": "PET-CF / FDM H2C / 관 Ø60/Ø40 Z-233~-12.5 + 밑 플랜지 Ø120×12(Z-233~-221, Ø5.5 ×3 r50 + 윗면 카운터보어 Ø9.5×3.5, 머리 자리 -224.5) + 위 플랜지 Ø100×8(Ø5.5 ×3 r45) 한 덩어리. 조임 1.5 N·m, 와셔 D-43(DP-2 수정 1: 밑 플랜지 t8.5->t12, 오조작 SF 2.52)",
    "P_T01_DISC": "Rigid 10K / SLA Form 3 / 진공 원판 R55 t12, 윗면 바깥 R1, 밑면 인서트 자리 Ø6.4×9 ×3 r45(MBIS5-6.5-8)",
}
for p in INFO["nutplates"]:
    PROPS[p["name"]] = "A5052 / 레이저 절단 평판 t6 + M4 탭 / □40 Z-104.5~-98.5(스파이더 웹 밑면에 붙음), 가운데 Ø28.4, M4 관통 탭 ×4 PCD38 스파이더 축에 대각, 바깥 모서리 C0.5. LBNR4 너트 4개 대신(DP2-X03). 판 대각 56.6 > 다리 사이 54라 돌지 않음"
for p in INFO["footplates"]:
    PROPS[p["name"]] = "A5052 / 레이저 절단 평판 t6 / 스파이더 발 누름판 옆 34~52 × 축 방향 45(r100~145) Z-230~-224, Ø5.5 ×2(r110·r135), 다리 쪽 C1. 발 국부 굽힘 SF 0.85 -> 3.36(DP-2 수정 1)"
C("component.metadata.set", {"component": "MAT_ROT", "properties": PROPS})
C("document.metadata.set", {"values": {"description": "DP-2 detailing rev1: LBNR4 x24 replaced by 6 tapped nut plates A5052 t6 under spider webs (M4 engagement 6), spider foot clamp plates A5052 t6 x6 with CB5-18 x12 (STEP-wait), post bottom flange t12 with counterbores; rest as v0.6.6"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(INFO, open(os.path.join(OUT, 'build_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps; nutplates', len(INFO["nutplates"]), 'footplates', len(INFO["footplates"]), 'bolts', len(INFO["bolts"]))
