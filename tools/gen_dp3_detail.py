# 디테일링 DP-3(모델링부) 생성기: v0.6.7 -> v0.6.8 — T05 테이프 공급
# 지시(PM DP-3): (1) 체결 16자리 (2) P_T05_HOLDER 카운터보어 Ø11·귀 윗면 229 (3) P_T05_PAD Z 63 한 덩어리 + NTJ T홈
#                (4) P_T05_GUIDE 앞벽 Y 553(두께 9.2)·뿌리 R3·밑판 앞 윗모서리 R1 (5) 막힌 인서트 자리 깊이 9
# 좌표: 대기 자세 세계 좌표(바늘점 원점, 매트 밑면 Z 0, 가장자리 바깥 +Y, 바늘 앞 -X). 단위 mm.
# 지시와 다르게 정한 곳(M-01 물림 >= 7.5를 지키는 쪽): 보고서 DEV 표.
#   DEV-1 안내 블록 볼트 CB5-12 -> CB5-16(인서트 L8 등판 관통이라 CB5-12는 물림 7)
#   DEV-2 홀더 클램프 카운터보어 깊이 5.5 -> 7.5(CB5-20 물림 5.5 -> 7.5)
#   DEV-3 캡 클램프: 카운터보어 바닥 741 -> 742, 인서트 자리를 Y 753~762(깊이 9)로 내리고 위는 Ø7 빈 구멍(곡면 보스에서 인서트가 튀어나오지 않게)
#   DEV-4 위판 앞면도 Y 553(앞벽과 한 면, U-10 단차 금지)
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp3_detail.py  -> tools/out/detail/DP-3/build.json
#   solidcraft-cli run tools/out/detail/DP-3/build.json --in 3D_Modeling/FSAP_v0.6.7.sc --save 3D_Modeling/FSAP_v0.6.8.sc
#   수정 1회차: python -B tools/gen_dp3_detail.py fix1 -> build_fix1.json
#   solidcraft-cli run tools/out/detail/DP-3/build_fix1.json --in 3D_Modeling/FSAP_v0.6.8.sc --save 3D_Modeling/FSAP_v0.6.9.sc
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-3')
os.makedirs(OUT, exist_ok=True)
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'full'
SIDEWALL = VARIANT in ('full', 'side')
S = []
INFO = {"bolts": []}


def C(c, p):
    S.append({"command": c, "params": p})


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


def cylx(d, x0, x1, y, z, **k):
    a, b = min(x0, x1), max(x0, x1)
    cyl(d, [a, y, z], "X", b - a, **k)


def cyly(d, x, y0, y1, z, **k):
    a, b = min(y0, y1), max(y0, y1)
    cyl(d, [x, a, z], "Y", b - a, **k)


# STEP 몸통은 국소 +X(볼트: 머리 자리면 x=0, 나사부가 +X / 인서트: 넣는 면 x=0, 안쪽이 +X) — 시험 실행 bbox로 확인
PX = lambda x, y, z: [1, 0, 0, r4(x), 0, 1, 0, r4(y), 0, 0, 1, r4(z)]      # 국소 +X -> 세계 +X
MX = lambda x, y, z: [-1, 0, 0, r4(x), 0, -1, 0, r4(y), 0, 0, 1, r4(z)]    # 국소 +X -> 세계 -X
PY = lambda x, y, z: [0, -1, 0, r4(x), 1, 0, 0, r4(y), 0, 0, 1, r4(z)]     # 국소 +X -> 세계 +Y
MY = lambda x, y, z: [0, 1, 0, r4(x), -1, 0, 0, r4(y), 0, 0, 1, r4(z)]     # 국소 +X -> 세계 -Y


def insert(pn, nm, M, par, body0, desc, bt="purchased"):
    C("component.activate", {"component": "root"})
    C("file.insert_step", {"path": SP + "%s/%s.stp" % (pn, pn), "name": nm, "matrix": M})
    C("body.rename", {"body": body0, "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": bt, "description": desc})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})
    INFO["bolts"].append({"name": nm, "pn": pn, "parent": par, "matrix": M})


HO, GU, PA, CA, HEADB = "P_T05_HOLDER", "P_T05_GUIDE", "P_T05_PAD", "P_T05_CAP", "STEP대기_SEWHEAD"

# ================= 수정 1회차(fix1): v0.6.8 -> v0.6.9 — P_T05_HUB 렌치 구멍 Ø9 x4 =================
# 검증 DP-3: HD_1~4 렌치 프로브 Ø8.5x30(X -87.5 -> -117.5)이 허브 플랜지(X -110.5)에 막힘(M-01·M-02). PM 판정 DP3-X01·X02.
# 허브 X -150~-110.5, 심 Ø76, 축 구멍 Ø16.3. 구멍 축 = 볼트 축(Y 730·770, Z 180·220) = 축(Y750,Z200) 기준 r 28.28, 45°·135°·225°·315°.
# +X 면에서 막힌 깊이 10(X -120.5~-110.5). 살: 심 바깥 38 - 32.78 = 5.22, 축 구멍 23.78 - 8.15 = 15.63(M-03 >= 2.5).
if VARIANT == 'fix1':
    HUB = "P_T05_HUB"
    C("motion.play", {"study": "대기", "step": 0, "quiet": True})
    C("component.activate", {"component": "T05"})
    for (y, z) in ((730, 180), (770, 180), (730, 220), (770, 220)):
        cylx(9, -120.5, -110.2, y, z, op="cut", targets=[HUB])            # 렌치 구멍 Ø9 깊이 10(+X 면 X -110.5에서)
    C("component.activate", {"component": "root"})
    C("component.metadata.set", {"component": "T05", "properties": {
        HUB: "PET-CF / FDM H2C / 플랜지 + 심 Ø76, 축 구멍 Ø16.3, 렌치 구멍 Ø9 x4 깊이 10(+X 면, 홀더 CB5-16 x4와 같은 축, r28.28 45°간격) — 롤을 손으로 돌려 구멍을 볼트에 맞추고 육각 렌치 4로 푼다 (DP-3 fix1)"}})
    C("document.metadata.set", {"values": {"description": "DP-3 fix1: T05 hub wrench access holes D9 x4 depth 10 on the +X face, coaxial with holder bolts CB5-16 x4 (M-01 wrench access); rest as v0.6.8"}})
    C("motion.play", {"study": "대기", "step": 0})
    json.dump(S, open(os.path.join(OUT, 'build_fix1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(S), 'steps', VARIANT)
    sys.exit(0)

C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ================= (3) P_T05_PAD: Z 43~63 한 덩어리 + NTJ-010C T홈(-X로 열림) =================
# NTJ-010C 실측: 맞변 7(Y 569~576), 모서리 8.08(X -135.04~-126.96), 너트 A Z 53.3~56.5, B Z 57~60.2. 로드 Ø4(Z 49~64), 로드 끝 Z 49.
C("component.activate", {"component": "T05_PAD"})
C("body.rename", {"body": PA, "name": "OLD_P_T05_PAD_Z49"})
C("solid.remove", {"bodies": ["OLD_P_T05_PAD_Z49"]})
box(-145, -117, 562.5, 582.5, 43, 63, PA)                                  # 28 x 20 x 20, 누름 면 Z 43
box(-146, -128.8, 570.3, 574.7, 49, 64, op="cut", targets=[PA])            # 목 4.4(로드 Ø4 + 0.4), 바닥 Z 49 = 로드 끝(미는 접촉)
box(-146, -126.75, 568.8, 576.2, 53.1, 60.4, op="cut", targets=[PA])      # 너트 주머니: 맞변 7 + 0.4, 높이 53.3~60.2 ± 0.2, 모서리 -126.958 + 0.208
C("material.assign", {"bodies": [PA], "material": "PET-CF"})

C("component.activate", {"component": "T05"})
# ================= (2) P_T05_HOLDER =================
for (y, z) in ((730, 180), (770, 180), (730, 220), (770, 220)):
    cylx(11, -89, -82.5, y, z, op="cut", targets=[HO])                     # 카운터보어 Ø10 -> Ø11, 바닥 X -82.5 그대로(밑 살 2.5)
C("solid.offset_face", {"faces": [[-100, 742.62, 228], [-100, 757.37, 228]], "distance": 1, "body": HO})   # 귀 윗면 Z 228 -> 229
box(-110.5, -90, 749.25, 750.75, 205, 230, op="cut", targets=[HO])         # 슬릿 1.5 윗면까지
C("solid.offset_face", {"faces": [[-100, 741.5, 226.0]], "distance": -2, "body": HO})                    # DEV-2 클램프 카운터보어 깊이 5.5 -> 7.5(머리 자리 Y 743.5)
C("solid.offset_face", {"faces": [[-100, 756, 225.0]], "distance": -1, "body": HO})   # (5) 인서트 자리 바닥 Y 756 -> 755(깊이 8 -> 9). 같은 지름 원통 자르기는 불 연산 실패


# ================= DEV-3 P_T05_CAP 클램프 =================
C("solid.offset_face", {"faces": [[-160, 741, 221.0]], "distance": -1, "body": CA})                      # 카운터보어 바닥 741 -> 742
C("solid.offset_face", {"faces": [[-160, 760, 220.0]], "distance": -7, "body": CA})  # 인서트 자리 바닥 Y 760 -> 753(인서트 754~762, 깊이 9)
cyly(7, -160, 762, 778, 217, op="cut", targets=[CA])                       # 인서트 위 빈 구멍 Ø7(곡면 보스 밖으로 안 튀어나옴)

# ================= (4) P_T05_GUIDE =================
if True:
    box(-147, -88, 553, 555, 45, 89.5, op="join", targets=[GU])            # 앞벽·위판 앞면 Y 555 -> 553(두께 9.2, DEV-4)
    # 앞벽 뿌리 R3: 두 모서리를 한 번에 주면 "a blend ending in an earlier round"로 거부 -> 하나씩
    C("solid.fillet", {"edges": [[-88, 562.2, 65]], "radius": 3, "body": GU})          # 앞벽–등판 안 모서리 R3
    C("solid.fillet", {"edges": [[-117, 562.2, 85.5]], "radius": 3, "body": GU})       # 앞벽–위판 안 모서리 R3
    if SIDEWALL:
        C("solid.fillet", {"edges": [[-108.05, 562.2, 55]], "radius": 3, "body": GU})  # 앞벽–+X 옆벽(안쪽 면) R3
        C("solid.fillet", {"edges": [[-104.99, 562.2, 55]], "radius": 3, "body": GU})  # 앞벽–+X 옆벽(바깥 면) R3
    C("solid.fillet", {"edges": [[-147.5, 553, 42], [-123, 553, 42], [-95.6, 553, 42]], "radius": 1, "body": GU})   # 밑판 앞 윗모서리 R1

# ================= (1) 헤드 기초 구멍(D-10 임시) =================
C("component.activate", {"component": "HEAD"})
for (y, z) in ((640, 45), (840, 45)):
    cylx(4.2, -76, -62, y, z, op="cut", targets=[HEADB])                   # 평판 뿌리 M5 기초 구멍 Ø4.2 x 13(X -75~-62)
for (y, z) in ((730, 180), (770, 180), (730, 220), (770, 220)):
    cylx(4.2, -76, -65, y, z, op="cut", targets=[HEADB])                   # 홀더 M5 기초 구멍 Ø4.2 x 10(X -75~-65)

# ================= (1) 체결품 실물 STEP =================
for j, (y, z) in enumerate(((640, 45), (840, 45)), 1):
    insert("CB5-16", "CB5-16_T05_RT_%d" % j, PX(-80, y, z), "T05", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — T05 평판 뿌리 t5 → 헤드 M5 탭(물림 11, 기초 구멍 Ø4.2×13 D-10, DP-3)")
for j, (y, z) in enumerate(((730, 180), (770, 180), (730, 220), (770, 220)), 1):
    insert("CB5-16", "CB5-16_T05_HD_%d" % j, PX(-82.5, y, z), "T05", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — 홀더 카운터보어 Ø11 → 평판 → 헤드 M5 탭(물림 8.5, 1.5 N·m, DP-3)")
for j, (y, z) in enumerate(((570, 50), (600, 80)), 1):
    insert("CB5-16", "CB5-16_T05_GD_%d" % j, MX(-75, y, z), "T05", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — 평판 +X 면 → 안내 블록 등판 인서트 MBIS5-6.5-8(물림 8, 1.5 N·m, DP-3)")
    insert("MBIS5-6.5-8", "MBIS5-6.5-8_T05_GD_%d" % j, MX(-80, y, z), "T05", "MBIS5-6.5-8",
           "MISUMI 수지용 인서트 M5 L8 — 안내 블록 등판 관통 Ø6.4(X -88~-80, DP-3)")
insert("CB5-20", "CB5-20_T05_CL_HO", PY(-100, 743.5, 222), "T05", "Cut-Extrude1",
       "MISUMI 육각 구멍붙이 볼트 M5×20 — 홀더 귀 클램프(머리 자리 Y 743.5, 인서트 물림 7.5, DP-3)")
insert("MBIS5-6.5-8", "MBIS5-6.5-8_T05_CL_HO", MY(-100, 764, 222), "T05", "MBIS5-6.5-8",
       "MISUMI 수지용 인서트 M5 L8 — 홀더 귀 +Y 면 자리 Ø6.4×9(DP-3)")
insert("CB5-20", "CB5-20_T05_CL_CA", PY(-160, 742, 217), "T05", "Cut-Extrude1",
       "MISUMI 육각 구멍붙이 볼트 M5×20 — 캡 보스 클램프(머리 자리 Y 742, 인서트 물림 8, DP-3)")
insert("MBIS5-6.5-8", "MBIS5-6.5-8_T05_CL_CA", MY(-160, 762, 217), "T05", "MBIS5-6.5-8",
       "MISUMI 수지용 인서트 M5 L8 — 캡 보스 자리 Ø6.4×9(Y 753~762) + 위 Ø7(DP-3)")

C("component.activate", {"component": "root"})
PROPS = {
    HO: "PET-CF / FDM H2C / 플랜지 56x56x8 + 보스 Ø36 L22 + 클램프 귀(윗면 Z229), 축 구멍 Ø16 관통, CB5-16 x4 카운터보어 Ø11 깊이 5.5(밑 살 2.5, 1.5 N·m), 클램프 CB5-20 카운터보어 Ø10 깊이 7.5 + MBIS5-6.5-8 자리 Ø6.4x9 (DP-3)",
    CA: "PET-CF / FDM H2C / 원판 Ø90 t4 + 클램프 보스 Ø50 L12(슬릿 1.5), 구멍 Ø16, 클램프 CB5-20(카운터보어 바닥 Y742) + MBIS5-6.5-8 자리 Ø6.4x9(Y753~762) + 위 Ø7 (DP-3)",
    GU: "PET-CF / FDM H2C / C틀: 밑판 받침면 Z42(앞 윗모서리 R1) + 등판 t8 + 위판 Z85.5~89.5 + 앞벽 t9.2(Y553~562.2, 뿌리 R3) + 옆벽 t3 + 막대 r8, MBIS5-6.5-8 x2 등판 관통 Ø6.4 (DP-3)",
}
C("component.metadata.set", {"component": "T05", "properties": PROPS})
C("component.metadata.set", {"component": "T05_PAD", "properties": {
    PA: "PET-CF / FDM H2C / 패드 28x20x20(Z43~63) 한 덩어리, NTJ-010C T홈(목 4.4 Z49~63, 너트 주머니 7.4 x Z53.1~60.4, -X로 열림) (DP-3)"}})
C("document.metadata.set", {"values": {"description": "DP-3 detailing: T05 tape unit fasteners (CB5-16 x8, CB5-20 x2, MBIS5-6.5-8 x4, head pilot holes D-10), holder counterbores D11 and ear top Z229, pad to Z63 with NTJ-010C T-slot, guide front wall t9.2 with R3 roots and R1 lead-in; rest as v0.6.7"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json' if VARIANT == 'full' else 'build_%s.json' % VARIANT), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(INFO, open(os.path.join(OUT, 'build_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps', VARIANT)
