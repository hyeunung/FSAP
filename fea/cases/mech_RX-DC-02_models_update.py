# -*- coding: utf-8 -*-
"""RX-DC-02 해석부: fea/models.json 갱신(뒤집은 스프링 자리의 핀 P 팔·클레비스 볼·받침 고리)."""
import json
P = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/models.json"
m = json.load(open(P, encoding="utf-8"))
parts = m["parts"]
crit = parts["P_RX12C1_GS_PIN_P"]["criteria"]
LOAD = ("가스 스프링 힘(r2_gasspring.json, 눈 중심 간 271.76~320.51은 RX-12-C1과 같음): 운전 최대 1,573 N 압축(-90, 공차 끝 F1 1,232 · L_ext 327). "
        "오조작 [RX-DC-02] 펴는 중 손 놓침 -> 펴짐 끝 감쇠 순 인장 2,034 N(E 20.34 J / 감쇠 15 mm x 최고/평균 1.5, 임시 D-231)")
CASE = "cases/mech_RX-DC-02_fea_handcalc.py"
parts["P_RX12C1_GS_PIN_P"].update(case=CASE,
    fixed="[RX-DC-02 v2.29.3] 귀판 t6(Y -1230~-1224) 구멍에 외팔, 핀 Ø8 Y -1249~-1222. 팔 = 귀판 가운데 ~ 몸통 눈 가운데 15(3 + SPACER_P 7 + 5). 전 RX-12-C1 팔 8",
    contact="몸통 눈 Ø8.2(Y -1247~-1237)", load=LOAD)
parts["P_RX12C1_GS_LUG"].update(case=CASE,
    load=LOAD + ". 눈 치우침 15(전 8)의 면 밖 굽힘, 지압은 평균(선형 모서리 지압은 참고만)")
parts["P_RX12C1_GS_CLEVIS"].update(case=CASE,
    fixed="뒤판이 :9 -X 면에 CB5-16 ×2 대각(Z -270·-310), 아래 모서리 Z -385 받침. [RX-DC-02] -Y 볼(Y -1254~-1248)은 Z -330 위를 깎아 X 1059~1104 · Z -385~-330 t6만 남음(뒤판 X 1104에서 외팔 31)",
    contact="핀 A 두 볼 지압 — 볼 가운데 Y -1251 / -1219(사이 32), 로드 눈 Y -1242(-Y 볼에서 9) -> -Y 볼 몫 0.72 F",
    load=LOAD)
parts["P_RX12C1_GS_PIN_A"].update(case=CASE, fixed="클레비스 볼 두 장 단순지지(가운데 Y -1251 / -1219), 하중점 Y -1242", load=LOAD)
parts["P_RXDC02_GS_SPACER_A"] = dict(case=CASE,
    fixed="핀 A에 끼움(Ø8 ↔ Ø8.2), Y -1237~-1222, 로드 눈과 클레비스 +Y 볼 사이",
    contact="양 끝면(로드 눈 · 볼)", load="지름 방향 하중 없음(핀 처짐 0.017 < 틈 0.1). 축 방향 = 스프링 힘 10 % 가정(마찰·기울기)",
    criteria=crit)
parts["P_RXDC02_GS_SPACER_P"] = dict(case=CASE,
    fixed="핀 P에 끼움, Y -1237~-1230, 몸통 눈과 귀판 사이", contact="양 끝면",
    load="SPACER_A와 같은 꼴·같은 하중 계통(E-19 묶음, 불리한 쪽 = A)", criteria=crit)
json.dump(m, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(parts))
