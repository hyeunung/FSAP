# STEPSWAP(모델링부) 생성기: v0.8.2 -> v0.8.3 — STEP대기_HNTT8-5_T08_1~8 -> 실물 STEP HNTT8-5
# 배치 규칙은 gen_t18_mech.py tnut()와 같다: HNTT 로컬 Y=0 윗면(어깨 Y-3, 두께 -Y 9), 원점 = 형재 겉면 구멍 중심 - 2.5*바깥 법선.
# T08: 460_F·B 밑면(Z -558, 임시 형상 밑면 -552.5 = 턱 안면 = 겉면 + 5.5) 홈(X 방향), 법선 (0,0,-1) -> 원점 Z -555.5
# 쓰는 법: python -B tools/gen_stepswap_mech.py -> tools/out/mech_STEPSWAP/edit.json (MCP batch 로 보냄)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_STEPSWAP')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
S = []
C = lambda c, p: S.append({"command": c, "params": p})
XN = [(x, y) for y in (-957, 223) for x in (-215, -145, 145, 215)]   # gen_t08_mech.py 와 같은 순서(_1~_8)
ZB = -558.0
DESC = "MISUMI 후입 T너트 HFS8 8시리즈 M5 HNTT8-5 (실물 STEP purchased-step/HNTT8-5) — HFS8-4080-460 밑 홈, Z -555.5~-546.5, CB5-20_T08_XN 짝 (T08, STEPSWAP v0.8.3)"
C("component.activate", {"component": "MAT_X"})
for i, (x, y) in enumerate(XN, 1):
    old = "STEP대기_HNTT8-5_T08_%d" % i
    nm = "HNTT8-5_T08_%d" % i
    C("component.delete", {"component": old})
    # 로컬 X -> 세계 X(홈 방향), 로컬 Y -> 세계 -Z(바깥 법선), 로컬 Z = X x Y -> 세계 +Y
    C("file.insert_step", {"path": SP + "HNTT8-5/HNTT8-5.stp", "name": nm,
                           "matrix": [1, 0, 0, x, 0, 0, 1, y, 0, -1, 0, ZB + 2.5]})
    C("body.rename", {"body": "Tap1", "name": nm})
    C("material.assign", {"bodies": [nm], "material": "Steel"})
    C("component.metadata.set", {"component": nm, "part_number": "HNTT8-5", "bom_type": "purchased", "description": DESC})
C("component.activate", {"component": "root"})
C("component.rename", {"component": "root", "name": "FSAP_v0.8.3"})   # 앱 제목이 v0.6.15로 남아 있던 것 고침(run-rules 2)
C("document.metadata.set", {"values": {"description": "STEPSWAP mechanism: T08 T-nuts STEP-pending HNTT8-5 x8 replaced by MISUMI STEP (460 bottom slot Z-555.5)"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
json.dump(S, open(os.path.join(OUT, 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps ->', os.path.join(OUT, 'edit.json'))
