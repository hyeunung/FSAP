"""T14 구동 모델링(v0.8.1 -> v0.8.2): Y판 P_T01_YPLATE t15 -> t10(Z -370~-360), DG 받침 P_S01_DGSPACER 50 -> 55(Z -360~-305).
선정 T14-S(= T14-C2). 같은 형상 다시 만들기:
  python -B tools/gen_t14_mech.py && solidcraft-cli run tools/out/mech_T14/gen_t14.json --in 3D_Modeling/FSAP_v0.8.1.sc --save <새 번호>.sc
(모델링부 실제 통로는 MCP batch, 같은 명령 순서.)

Y판은 지시서의 solid.offset_face(-5) 대신 '탭 관통 + 상자 자르기'로 만든다(지시서 3절 대안 경로).
offset_face로 윗면을 -360으로 내리면 블라인드 탭 Ø4.2의 천장 면(-360)이 남아 윗면과 두께 0으로 겹친다
(커널 면 20, 천장 면 2개, 윗면에 구멍 고리 없음). 상자 자르기로 만들면 커널 면 18, 관통 탭이 된다.
부피·질량은 두 길이 같다(1,804,655.3 mm3, 4,836.5 g).
좌표는 대기 자세(MAT_Y Y -700) 월드 좌표다.
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
C = []
def cmd(c, p): C.append({"command": c, "params": p})
YP, DG = "P_T01_YPLATE", "P_S01_DGSPACER"
cmd("motion.play", {"study": "대기", "step": 0, "quiet": True})
# 2) DG 받침 밑면 -355 -> -360
cmd("solid.offset_face", {"faces": [[75, -700, -355]], "distance": 5, "body": DG})
# 3) Y판: M5 탭 기초 Ø4.2 x2 관통(t15 상태에서), 윗면 5 mm 걷어 내기(-360)
cmd("solid.cylinder", {"diameter": 4.2, "height": 17, "base": [55, -640, -371], "axis": "Z", "operation": "cut", "targets": [YP]})
cmd("solid.cylinder", {"diameter": 4.2, "height": 17, "base": [115, -640, -371], "axis": "Z", "operation": "cut", "targets": [YP]})
cmd("solid.box", {"length": 410, "width": 510, "height": 6, "center": [0, -700, -357], "operation": "cut", "targets": [YP]})
cmd("document.metadata.set", {"values": {"description": "T14 mechanism: Y plate t15->t10 (Z-370~-360), DG spacer extended down to Z-360 (H55), mat bottom Z0 unchanged"}})
cmd("motion.play", {"study": "대기", "step": 0, "quiet": True})
os.makedirs(os.path.join(H, "out", "mech_T14"), exist_ok=True)
json.dump(C, open(os.path.join(H, "out", "mech_T14", "gen_t14.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(C))
