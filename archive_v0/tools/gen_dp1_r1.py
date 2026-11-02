# 디테일링 DP-1 수정 1회차(모델링부) 생성기: v0.6.2 -> v0.6.3
# 지난 검증 문제 '맞춤핀 Ø3 바디 없음(D-43)': 미스미 맞춤핀 MS3-8(스트레이트, D 공차 +0.010/+0.005 = m6,
# 2026-10-31 미스미 한국 검색으로 형번 확인, 로그인 풀림이라 STEP 못 받음) -> E-10 임시 형상 STEP대기_MS3-8.
# 자리: 팔 핀 구멍 Ø3 H7 관통(Z 54~57) + 축 핀 구멍 Ø3 × 6(Z 57~63), 중심 (77, -7.5).
# 핀 Z 54~62(밑끝 팔 밑면과 같은 높이, 축 구멍 바닥 Z 63까지 1 남김 = 공기 빠짐).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp1_r1.py
#   solidcraft-cli run tools/out/detail/DP-1/r1/build.json --in 3D_Modeling/FSAP_v0.6.2.sc --save 3D_Modeling/FSAP_v0.6.3.sc
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-1', 'r1')
os.makedirs(OUT, exist_ok=True)
S = []


def C(c, p):
    S.append({"command": c, "params": p})


PX, PY = 77.0, -7.5
PN = "STEP대기_MS3-8_T06"

C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "T06_KNIFE"})
C("component.create", {"name": PN, "parent": "T06_KNIFE", "activate": True, "grounded": False})
C("solid.cylinder", {"diameter": 3, "height": 8, "base": [PX, PY, 54], "axis": "Z", "body_name": PN})
for z in (54, 62):
    C("solid.chamfer", {"edges": [[PX + 1.5, PY, z]], "distance": 0.3, "body": PN})
C("material.assign", {"bodies": [PN], "material": "Steel"})
C("component.metadata.set", {"component": PN, "part_number": "MS3-8", "bom_type": "purchased",
                             "description": "MISUMI 맞춤핀 MS3-8 스트레이트 Ø3 m6(+0.010/+0.005) L8 (STEP 대기 D-43, 임시 형상 끝 C0.3) — T06 축-팔 돌림 멈춤"})
C("component.activate", {"component": "root"})
C("document.metadata.set", {"values": {"description": "DP-1 detailing rev1: dowel pin MS3-8 (STEP-wait) in T06 arm/shaft pin holes"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(S), 'steps')
