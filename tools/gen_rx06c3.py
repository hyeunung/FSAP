# RX-06-C3 생성기 — 움직이는 컴포넌트 바디를 고치는 피처를 그 바디의 컴포넌트로 옮긴다.
# 형상 변화 0. 작업 전 FSAP_v2.22.0.sc(REST 자세) → FSAP_v2.22.1.sc
# 사용: python -B tools/gen_rx06c3.py  → tools/out/mech_RX-06-C3/model/stage_1.json · edit.json · edit_meta.json
#
# 단계
#  1) U6_SHOE 피처 4개(스케치 SK_M06_SHOE_SL2 · U6S_SHOE_SLOT · U6S_SHOE_TOP · Cylinder789)를 U6_PRESS로.
#     component.move_features는 REST(J_U6_PRESS 4.5)의 world 자리를 지키도록 좌표를 Z −4.5 바꾼다.
#  2) 바뀐 좌표를 설계 값(바디 기준)으로 되돌린다 — 슬롯 스케치 평면 Z 0, 날개 모서리 Z 50,
#     로드 구멍 base Z 46.5 · 높이 5(FIX-045가 10으로 늘린 것을 원래 값으로).
#  3) 루트 Move14(U3_NEEDLE_PIN +Z 6)를 U3_NEEDLE로.
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_RX-06-C3')
os.makedirs(os.path.join(OUT, 'model'), exist_ok=True)

SK_SLOT, SLOT, TOP, ROD_HOLE, MOVE14 = 96814, 96815, 96816, 96817, 5222

stage = [
    {"command": "component.move_features",
     "params": {"features": [SK_SLOT, SLOT, TOP, ROD_HOLE], "component": "U6_PRESS"}},
    {"command": "timeline.edit",
     "params": {"feature": SK_SLOT, "set": {"plane": {"type": "custom", "plane": {
         "origin": [-23.0, 0.0, 0.0], "x_dir": [0.0, 1.0, 0.0], "y_dir": [0.0, 0.0, 1.0]}}}}},
    {"command": "timeline.edit",
     "params": {"feature": TOP, "set": {"edges": [[-20.0, -155.0, 50.0]]}}},
    {"command": "timeline.edit",
     "params": {"feature": ROD_HOLE, "set": {"base": [-8.0, -166.0, 46.5], "height": "5"}}},
    {"command": "component.move_features",
     "params": {"features": [MOVE14], "component": "U3_NEEDLE"}},
]

json.dump(stage, open(os.path.join(OUT, 'model', 'stage_1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(stage, open(os.path.join(OUT, 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"base": "3D_Modeling/FSAP_v2.22.0.sc", "result": "3D_Modeling/FSAP_v2.22.1.sc",
           "note": "REST 자세에서 실행. 끝에 문서 이름·설명·REST·숨김·save는 따로(모델 보고서 7절)."},
          open(os.path.join(OUT, 'edit_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('steps', len(stage))
