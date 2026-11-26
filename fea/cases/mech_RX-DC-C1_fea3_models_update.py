# RX-DC-C1 해석부 3회차(수정 1회차 뒤): fea/models.json 세움 받침 항목을 v2.30.5 형상·조립(앞 누름 볼트)으로 갱신, 블록 항목에 새 M4 탭 한 줄
import json
p = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/models.json"
d = json.load(open(p, encoding="utf-8"))
e = d["parts"]["P_RXDC03_RISER_BRKT_판금"]
e["case"] = "cases/mech_RX-DC-C1_fea3_handcalc.py (v2.30.4: cases/mech_RX-DC-C1_fea2_handcalc.py, v2.30.3: cases/mech_RX-DC-C1_fea_handcalc.py, RX-DC-03: cases/mech_RX-DC-03_fix2_handcalc.py 외)"
e["fixed"] = ("v2.30.5: 밑판 X -308.6~-273 · Y 83~97 · Z 250~253 + 플랜지 X -288~-273 · Y 74.5~83 · Z 250~253(한 몸)이 블록 P_RX19_BLOCK 선반 윗면(Z 250)에 얹힘. "
              "누르는 것은 볼트 머리 셋뿐 — 뒤 CB5-12 x2(X -288 · -278, Y 90, 머리 앞 끝 Y 85.75)와 앞 CB4-12 x1(X -280.5 · Y 78.25, 머리 Ø7: X -284~-277 · Y 74.75~81.75, 블록 M4 막힌 탭 밑구멍 Ø3.3 Z 240~250, 물림 9). "
              "블록 윗면은 받침을 밀기만 한다(당기지 못함). 웨브 X -288~-273 · Y 82~85 · Z 253~487, 꺾음 날 2개 X -288~-285 · -276~-273, Y 74.5~82, Z 253~445(ㄷ 단면, 밑은 플랜지와 한 몸). "
              "머리 ↔ 두 날 안쪽 면 1.0, 머리 ↔ 웨브 앞면 0.25. 받침점: +Y 당김 = 웨브 밑(가운데 Y 83.5, 볼트 지렛대 5.25 — 보수), -Y 당김 = 플랜지 앞 끝 Y 74.5")
e["load"] = ("운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄(D-232 임시) + 자중 x3 g(5.5 N, 축 방향). 오조작: 케이블 손 당김 50 N(임시, D-38 전) — +Y · -Y · X 각각(뿌리 받침이 방향마다 다르다). "
             "비틀림 팔은 ㄷ 단면 전단 중심(X -280.5 · Y 87.18, e = 3b^2/(h+6b), b 9 · h 12)에서 먼 타이까지: Y 당김 19.5, X 당김 13.18")
mc3 = (" | 2026-11-27 3회차: 모델(비대칭 굽힘 식 + 방향별 뿌리 받침)은 그대로. 달라진 것은 조립(앞 누름 볼트)과 "
                                                  "전단 중심 식의 b(2회차 고침안 6 -> STEP 치수 9, τ 차이 1 MPa 안). 새로 본 곳: 머리 ~ 날 발 사이 플랜지 짧은 굽힘")
if "3회차" not in e.get("model_change", ""):
    e["model_change"] = e.get("model_change", "") + mc3
e["status"] = ("손계산 fea/results/mech_RX-DC-C1_fea3_handcalc.json. FEA 못 함 — 환경 없음(D-16). 한 몸(Z 250 외곽 Y 74.5까지, Z 253에 두 날 바깥 밑 모서리 없음, 솔리드 1). "
               "ㄷ 단면 Ix 864.84 · Iy 2,497.5 · Ixy 0: 오조작 50 N ±Y VM 88.3 · SF 2.32, ±X 5.49, 가장 불리한 각 2.20. 운전 10 N 11.61 · 27.44. Z 445 웨브만 오조작 2.20(그대로). "
               "+Y 당김: 앞 볼트 당김 2,243 N(보수) — 엔진 handcalc M4 12.9 · A5052 물림 9 암나사 전단 2.21 · 나사 인장 4.31, 플랜지 전단 2.37~3.23, 좌면 2.06. "
               "-Y 당김: 웨브 당김 1,649 N을 앞 머리(Y 81.75)와 뒤 머리(Y 85.75) 사이 4 mm 판이 받음 σ 72 · SF 2.84. 끝 처짐 오조작 Y 1.46 · X 0.45, 운전 0.29. "
               "디테일 RXDCC1-FEA-D4: +Y 오조작에서 머리 ~ 날 발 사이 플랜지 짧은 굽힘(팔 2.9, 폭 7.5 x t3) 첫 항복 SF 0.96(날 발 회전 자유) · 1.19~1.41(일부 구속) · 1.93(막힘), 소성 힌지 1.45~2.89 — 기준 1.2 근처라 손계산으로 못 가름, 고체 FEA 필요. "
               "디테일 RXDCC1-FEA-D5: M4 탭 밑구멍 10에 볼트 끝이 바닥 위 1(유효 물림 7이면 1.72, A5052-H112면 1.25 · 둘 다면 0.97)")
e["step"] = "tools/out/mech_RX-DC-C1/stepout/P_RXDC03_RISER_BRKT_판금.step"
e["version"] = "v2.30.5"
b = d["parts"]["P_RX19_BLOCK_밀링"]
note = (" | RX-DC-C1(v2.30.5): 선반 윗면 (X -280.5 · Y 78.25)에 M4 막힌 탭(밑구멍 Ø3.3 Z 240~250) — 세움 받침 앞 누름 볼트 CB4-12, 오조작 +Y 당김 2,243 N(보수) 암나사 전단 SF 2.21"
        "(A5052 195 · 물림 9, fea/results/mech_RX-DC-C1_fea3_bolt_M4_le9.json). T2_2 탭 벽 1.89(RXDCC1-D7)")
if "RX-DC-C1(v2.30.5)" not in b["status"]:
    b["status"] += note
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
