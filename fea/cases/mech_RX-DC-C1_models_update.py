# RX-DC-C1 해석부: fea/models.json P_RXDC03_RISER_BRKT_판금 항목을 v2.30.3 형상으로 갱신
import json
p = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/models.json"
d = json.load(open(p, encoding="utf-8"))
e = d["parts"]["P_RXDC03_RISER_BRKT_판금"]
e["case"] = "cases/mech_RX-DC-C1_fea_handcalc.py (RX-DC-03: cases/mech_RX-DC-03_fix2_handcalc.py 외)"
e["fixed"] = ("v2.30.3: 밑판 X -308.6~-273 · Y 83~97 · Z 250~253이 블록 P_RX19_BLOCK 윗면(Z 250)에 CB5-12 x2(X -288 · -278, Y 90, 막힌 탭 깊이 10)로 체결. "
              "웨브 X -288~-273 · Y 82~85 · Z 253~487, 꺾음 날 X -288~-285 · Y 74.5~82 · Z 253~445(밑면 Z 253 밑에 밑판 없음 — 자유 끝). "
              "뿌리 Z 253에서 실제로 붙은 곳은 웨브 밑 Y 83~85(STEP 그대로 15x2), 판금 굽힘으로 보면 웨브 15x3뿐. 지렛대 받침점: 밑판 앞 끝 Y 82 · 뒤 끝 Y 97")
e["contact"] = "선반 X -318.6~-268 · Y 65~85 · Z 484~487, 케이블 타이 구멍 중심 X -300 · -280, Y 74(타이로 세로 케이블 2줄이 묶임). 하중점 Z 487(뿌리에서 234)"
e["load"] = "운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄(D-232 임시) + 자중 x3 g(4.45 N, 축 방향). 오조작: 케이블 손 당김 50 N(임시, D-38 전) — Y(얇은 쪽)·X 각각, 먼 타이 X -300에서 비틀림 팔 19.5"
e["status"] = ("손계산 fea/results/mech_RX-DC-C1_fea_handcalc.json. FEA 못 함 — 환경 없음(D-16). 뿌리 판금 실제(웨브 15x3): 오조작 Y SF 0.39(동작, RXDCC1-FEA-P1), 운전 2줄 Y SF 1.97(디테일). "
               "STEP 그대로(15x2): 운전 SF 0.87. 고침안(밑판을 꺾음 날 밑 Y 74.5까지, RX-DC-03 fix2와 같은 수): 오조작 Y 1.32(디테일 RXDCC1-D2) · X 2.55, 운전 6.59. Z 445 웨브만 오조작 2.20. "
               "볼트 오조작 846 N/개 암나사(A5052, 물림 9) SF 7.33. 처짐 오조작 2.18 · 운전 0.44")
e["step"] = "tools/out/mech_RX-DC-C1/stepout/P_RXDC03_RISER_BRKT_판금.step"
e["version"] = "v2.30.3"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
