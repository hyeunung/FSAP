# 구동 T08(모델링부) 생성기: v0.6.10 -> v0.6.11 — 매트 이송 X 블록 장착판
# 지시(PM T08 선정 T08-S01·S02): 460_F·B +Y 43 이동, P_S01_XSPACER_1~4 지움, P_T08_XPLATE_F·B(A5052 460x87 t14),
#   CB5-16 x8(블록 -> 판, 위 카운터보어 9.5x5.5), CB5-20 x8(판 -> 460, 밑 카운터보어 9.5x5), STEP대기_HNTT8-5 x8(E-10, D-41)
# 좌표: 대기 자세(J_MAT_X 0, J_MAT_Y -700) 세계 좌표 = MAT_X 틀. 단위 mm.
# 지시와 다르게 정한 곳: HNTT8-5 임시 형상 윗면 Y 모서리 C1(460 홈 안 45도 면과 겹침 1.153 mm3 -> 0, 보고서 mech_T08_model.md)
# 실제 모델은 MCP(앱 연결)로 같은 명령을 보내 그렸다. 이 생성기는 같은 형상을 CLI로 다시 만드는 용도다.
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_t08_mech.py  -> tools/out/mech_T08/model/build.json
#   solidcraft-cli run tools/out/mech_T08/model/build.json --in 3D_Modeling/FSAP_v0.6.10.sc --save <새 이름>.sc
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T08', 'model')
os.makedirs(OUT, exist_ok=True)
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
S = []
C = lambda c, p: S.append({"command": c, "params": p})
DN = lambda x, y, z: [0, 0, 1, x, 0, 1, 0, y, -1, 0, 0, z]   # 볼트 STEP 국소 +X(나사부) -> 세계 -Z
UP = lambda x, y, z: [0, 0, -1, x, 0, 1, 0, y, 1, 0, 0, z]   # 국소 +X -> 세계 +Z
XB = [(x, y) for y in (-1016, -984, 164, 196) for x in (-173.5, 173.5)]   # 블록 탭 축(STEP 실측 r2.067)
XN = [(x, y) for y in (-957, 223) for x in (-215, -145, 145, 215)]        # 460 밑 홈 중심
PL = {"P_T08_XPLATE_F": (-1024, -937, (-1016, -984), -957), "P_T08_XPLATE_B": (156, 243, (164, 196), 223)}

C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("document.metadata.set", {"values": {"description": "T08 mechanism: X rail blocks on one-piece A5052 plates, 460 frames +Y43, XSPACER x4 removed, CB5-16/CB5-20 x8 each"}})
# 1) 형재 이동(캡은 자식이라 함께), 받침 지움
for o in ("HFS8-4080-460_F:1", "HFS8-4080-460_B:1"):
    C("occurrence.move", {"occurrence": o, "space": "world", "translate": [0, 43, 0]})
C("solid.remove", {"bodies": ["P_S01_XSPACER_%d" % i for i in range(1, 5)]})
# 2) 판 2장(한 스케치 밀기 + 구멍)
C("component.activate", {"component": "MAT_X"})
for nm, (y0, y1, yb, yn) in PL.items():
    sk = "SK_" + nm
    C("sketch.create", {"plane": {"origin": [0, 0, -572], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    C("sketch.rectangle.two_point", {"p0": [-230, y0], "p1": [230, y1]})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 14, "body_name": nm})
    for x in (-173.5, 173.5):
        for y in yb:
            C("solid.cylinder", {"diameter": 5.5, "height": 16, "base": [x, y, -573], "axis": "Z", "operation": "cut", "targets": [nm]})
            C("solid.cylinder", {"diameter": 9.5, "height": 6, "base": [x, y, -563.5], "axis": "Z", "operation": "cut", "targets": [nm]})
    for x in (-215, -145, 145, 215):
        C("solid.cylinder", {"diameter": 5.5, "height": 16, "base": [x, yn, -573], "axis": "Z", "operation": "cut", "targets": [nm]})
        C("solid.cylinder", {"diameter": 9.5, "height": 6, "base": [x, yn, -573], "axis": "Z", "operation": "cut", "targets": [nm]})
C("material.assign", {"bodies": list(PL), "material": "A5052"})
C("component.activate", {"component": "root"})
C("component.metadata.set", {"component": "MAT_X", "properties": {
    "P_S01_XSPACER_1": None, "P_S01_XSPACER_2": None, "P_S01_XSPACER_3": None, "P_S01_XSPACER_4": None,
    "P_T08_XPLATE_F": "A5052 / 판재 절단 + 밀링 / X 블록 장착판 460×87 t14(X ±230 · Y −1024~−937 · Z −572~−558), 블록 CB5-16 ×4 위 카운터보어 Ø9.5×5.5 + 관통 Ø5.5, 460 CB5-20 ×4 밑 카운터보어 Ø9.5×5 + 관통 Ø5.5. 밀링 이유: LM 블록 장착 평면, 굽힘 없는 t14(높이 사슬)라 판금 아님, 블록 예압 좌면 크리프로 출력 불가, 블록과 형재를 Y 43 비켜 잇는 기성품 없음 (T08)",
    "P_T08_XPLATE_B": "A5052 / 판재 절단 + 밀링 / X 블록 장착판 460×87 t14(X ±230 · Y 156~243 · Z −572~−558), _F와 같은 모양(블록 −Y 쪽, 460 +Y 쪽) (T08)"}})
# 3) 볼트 실물 STEP(root에 세계 행렬 -> MAT_X로 reparent)
D16 = "MISUMI 육각 구멍붙이 볼트 M5×16 — X 블록 SV2RL28-1800 → P_T08_XPLATE 위 카운터보어 Ø9.5×5.5(좌면 Z −563.5, 블록 탭 물림 7.5, T08)"
D20 = "MISUMI 육각 구멍붙이 볼트 M5×20 — P_T08_XPLATE 밑 카운터보어 Ø9.5×5 → HFS8-4080-460 밑 홈 T너트 HNTT8-5(머리 Z −572~−567, 끝 Z −547, T08)"
B = []
for i, (x, y) in enumerate(XB, 1):
    B.append(("CB5-16_T08_XB_%d" % i, "CB5-16", DN(x, y, -563.5), D16))
for i, (x, y) in enumerate(XN, 1):
    B.append(("CB5-20_T08_XN_%d" % i, "CB5-20", UP(x, y, -567), D20))
for nm, pn, M, d in B:
    C("file.insert_step", {"path": SP + "%s/%s.stp" % (pn, pn), "name": nm, "matrix": M})
    C("body.rename", {"body": "Cut-Extrude1", "name": nm})
    C("material.assign", {"bodies": [nm], "material": "Steel"})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": "purchased", "description": d})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": "MAT_X"})
# 4) T너트 임시 형상(E-10): 16×16×5, 윗면 Y 모서리 C1, Ø4.2 관통
DN5 = "MISUMI 후입 T너트 HFS8용 M5 — STEP 대기 임시 형상 16×16×5(윗면 Y 모서리 C1, 460 홈 안 45° 면에 맞춤) + M5 기초 Ø4.2(E-10, D-41, 미스미 로그인 풀림). 460 밑 홈 턱 위 Z −552.5~−547.5 (T08)"
for i, (x, y) in enumerate(XN, 1):
    nm = "STEP대기_HNTT8-5_T08_%d" % i
    C("component.create", {"name": nm, "parent": "MAT_X", "activate": True, "grounded": False})
    C("solid.box", {"length": 16, "width": 16, "height": 5, "center": [x, y, -550], "body_name": nm})
    C("solid.cylinder", {"diameter": 4.2, "height": 7, "base": [x, y, -553.5], "axis": "Z", "operation": "cut", "targets": [nm]})
    C("solid.chamfer", {"edges": [[x, y - 8, -547.5], [x, y + 8, -547.5]], "distance": 1, "body": nm})
    C("material.assign", {"bodies": [nm], "material": "Steel"})
    C("component.metadata.set", {"component": nm, "part_number": "HNTT8-5", "bom_type": "purchased", "description": DN5})
    C("component.activate", {"component": "root"})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(S), 'steps ->', os.path.join(OUT, 'build.json'))
