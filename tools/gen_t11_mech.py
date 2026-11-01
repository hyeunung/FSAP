# T11 링2 포트 방향(모델링부) 생성기: v0.6.14 -> v0.6.15
# 지시서 docs/reports/mechanism/mech_T11_select.md (T11-S = 구상 2 수정안) 그대로. 다르게 정한 곳은 mech_T11_model.md 'DEV' 표.
# 좌표: 세계 대기(회전 중심 C (0,-700)). 스파이더 1 틀 = +Y(90도). 2·3은 C 둘레 +120·+240도.
# 회전 복사는 solid.move 회전 대신 좌표를 직접 돌려 그린다(회전 중심 혼동 없음).
# 쓰는 법: python -B tools/gen_t11_mech.py -> tools/out/mech_T11/model/b_<A..C>.json (MCP batch로 차례로 보냄)
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T11', 'model')
os.makedirs(OUT, exist_ok=True)
CX, CY = 0.0, -700.0
ANG = {"1": 0.0, "2": 120.0, "3": 240.0}
B = {}
S = None


def batch(k):
    global S
    S = B.setdefault(k, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def rot(x, y, a):
    """세계 점 (x,y)를 C 둘레 a도 돌림."""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    dx, dy = x - CX, y - CY
    return (r6(CX + dx * c - dy * s), r6(CY + dx * s + dy * c))


def rotv(vx, vy, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (r6(vx * c - vy * s), r6(vx * s + vy * c))


POST, YP = "P_T01_POST", "P_T01_YPLATE"
SP = ["P_T01_SPIDER_%d" % i for i in (1, 2, 3)]

# ======================= A: POST 장공 ×3, 스파이더 결속 구멍 Ø4 ×12 (MAT_ROT) =======================
batch('A')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "MAT_ROT"})
# DEV-2: 기둥 속 Ø40 면에 330도 근처 실 같은 조각 면이 있어(옛 구멍 두 번 겹침) 330도 장공 절삭이 부피 -722(맞으면 -486)로
# 틀어지고 그 뒤 불리언이 실패했다. 장공 높이만 Ø40.2로 다시 깎아(Z -212~-194, -226.98 mm3) 조각 면을 없앤 뒤 장공을 낸다.
C("solid.cylinder", {"diameter": 40.2, "height": 18, "base": [CX, CY, -212.0], "axis": "Z", "operation": "cut", "targets": [POST]})
for k, a in ANG.items():
    # 장공: 평면 원점 = 반지름 35(Y -665) 점, x_dir = 원주 t, y_dir = +Z, 법선 = t x z = -반지름(안쪽)
    ox, oy = rot(0.0, -665.0, a)
    tx, ty = rotv(1.0, 0.0, a)
    sk = "SK_T11_POSTSLOT_%s" % k
    C("sketch.create", {"plane": {"origin": [ox, oy, 0.0], "x_dir": [tx, ty, 0.0], "y_dir": [0.0, 0.0, 1.0]}, "name": sk})
    C("sketch.slot.center_to_center", {"p0": [0.0, -205.25], "p1": [0.0, -200.75], "width": 5.5})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 26, "operation": "cut", "targets": [POST]})
# 결속 구멍: 스파이더 1 틀 +X 다리(X 27~30), 축 X, 바닥 X 26 높이 5
for k, a in ANG.items():
    # 판금 바디라 판에 수직인 평행 압출 절삭만 된다(블랭크 구멍). 평면: 원점 = 틀 (26, -700), x_dir = 반지름, y_dir = +Z, 법선 = 원주 t(+X 틀)
    ox, oy = rot(26.0, -700.0, a)
    rx, ry = rotv(0.0, 1.0, a)
    sk = "SK_T11_TIE_%s" % k
    C("sketch.create", {"plane": {"origin": [ox, oy, 0.0], "x_dir": [rx, ry, 0.0], "y_dir": [0.0, 0.0, 1.0]}, "name": sk})
    for (y, z) in ((-400.0, -197.5), (-400.0, -208.5), (-560.0, -197.5), (-560.0, -208.5)):
        C("sketch.circle.center", {"center": [r6(y + 700.0), z], "radius": 2.0})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 5, "operation": "cut", "targets": [SP[int(k) - 1]]})
C("component.activate", {"component": "root"})

# ======================= B: Y판 결속 구멍 Ø4.5 ×2 (MAT_Y) =======================
batch('B')
C("component.activate", {"component": "MAT_Y"})
for x in (-10.0, 10.0):
    C("solid.cylinder", {"diameter": 4.5, "height": 17.0, "base": [x, -590.0, -371.0], "axis": "Z",
                         "operation": "cut", "targets": [YP]})
C("component.activate", {"component": "root"})

# ======================= C: STEP대기_KQ2L04-M5A ×6 (MAT_ROT 하위 구매품) =======================
# 외곽 10(원주) x 16(반지름) x 11(Z -237~-226), 포트 면에 앉음: R2 r 419.15~435.15, R1 r 199.15~215.15
# (지시 Y -280.80은 몸통 끝 -280.85와 0.05 떠 있어 '앉음 거리 0' 기준에 맞춰 -280.85로 둠 — DEV-1)
batch('C')
FIT = {"R2": 419.15, "R1": 199.15}
NAMES = []
for ring, r0 in FIT.items():
    for k, a in ANG.items():
        nm = "STEP대기_KQ2L04-M5A_%s_%s" % (ring, k)
        NAMES.append(nm)
        C("component.activate", {"component": "MAT_ROT"})
        C("component.create", {"name": nm, "parent": "MAT_ROT", "activate": True, "grounded": False})
        tx, ty = rotv(1.0, 0.0, a)
        rx, ry = rotv(0.0, 1.0, a)
        sk = "SK_T11_%s_%s" % (ring, k)
        C("sketch.create", {"plane": {"origin": [CX, CY, -237.0], "x_dir": [tx, ty, 0.0], "y_dir": [rx, ry, 0.0]}, "name": sk})
        C("sketch.line", {"points": [[-5, r0], [5, r0], [5, r0 + 16], [-5, r0 + 16]], "closed": True})
        C("sketch.finish", {})
        C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 11, "body_name": nm})
        C("material.assign", {"bodies": [nm], "material": "Steel"})
        C("component.metadata.set", {"component": nm, "part_number": "KQ2L04-M5A", "bom_type": "purchased",
                                     "description": "SMC(MISUMI) 원터치 엘보 KQ2L04-M5A — 링%s 실린더 포트 M5, 관 Ø4 출구 +Z. STEP 대기 임시 외곽 10x16x11(측정 Q_FIT, 카탈로그 미확인) (T11)" % ring[1]})
C("component.activate", {"component": "root"})
C("joint.rigid_group", {"occurrences": ["MAT_ROT:1"] + [n + ":1" for n in NAMES]})

json.dump(B, open(os.path.join(OUT, 'batches.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for k_, v in B.items():
    json.dump(v, open(os.path.join(OUT, 'b_%s.json' % k_), 'w', encoding='utf-8'), ensure_ascii=False)
    print(k_, len(v))
print(json.dumps(NAMES, ensure_ascii=False))
