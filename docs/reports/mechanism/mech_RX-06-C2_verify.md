# RX-06-C2 검도·체결 — 움직이는 컴포넌트 바디를 고치는 루트 피처 옮기기 (검도·체결부, 2026-11-13)

요약(10줄 안):
- 대상 `3D_Modeling/FSAP_v2.15.1.sc`(앱 MCP, 읽기만, 저장 안 함). 끝난 뒤 REST step 0 + J_U4_X 0 · J_U7_HGT 0, `dirty` false, 저장본 sha1 `392a1d6a…` 전후 같음.
- **판정: 불합격(동작 문제 1).** 완료 판정 ① ② ③ 만족, **④ 미달**.
- ① REST 8바디 부피 · bbox가 측정 표(`tools/out/signatures.json`)와 같다(부피 차 0.000, bbox 차 ≤ 0.0005).
- ② J_U5_X 0 · 345 · 690 · 1035 · 1380, J_U7_HGT −4 · −1.5 · 1 · 3.5 · 6, MAINT_U7 2 · 3 · 6 · 8 · 11 · 13단계(CST_X 12.5 · 25, CST_Y 75 · 125 · 200 · 250), J_U4_X 24 · 48 · 71 · 95, 그리고 HGT 6 + CST_X 25 + CST_Y 250 겹친 자세에서 부피가 REST와 같고 bbox가 강체 이동과 같다. 구멍 축도 따라간다(`body_topology`: CAR_PLATE 탭 r 2.1이 J_U5_X 1380에서 X −610 · −575, TUBE_BRKT_CST_O Ø5.5가 (83~89, −441.5, 168 · 204)).
- ③ 타임라인 error 0, warning 54(작업 전 54와 이름 · 글 같음), Box326 · Combine41~45 없음, 피처 3,709 · 바디 879.
- ④ 위 자세 모두 `inspect.clearance` overlaps 0(기준선 `P_M02_BASE` ↔ `P_RX06_CARRIAGE` 0.0276 mm³ 하나, 판정 기억에 있음). **그러나 unchecked로 남던 쌍 가운데 `P_M05_HOLDER`(U7_FIXED) ↔ `CB5-16_M05_1:2 · :3`(U7_CASSETTE)은 탭 물림이 아니라 진짜 겹침이다**: 볼트 끝 X 46이 HOLDER 벽(X 46~50, 구멍 없음)을 4 mm 뚫는다(계산 약 78.5 mm³ × 2). 이번 과제가 만든 것이 아니고 v2.15.0에도 같다(PNEU-01 수정 2회차 v2.8.8 때부터로 보임).
- 고칠 것: `CB5-16_M05_1:2 · :3` → **CB5-12**(끝 X 50.0, 판 물림 8 mm = 1.6d).
- 구동 후보 2(디테일로 기록): J_U6_PRESS 구동 한 번 395 · 460 s(같은 꼴 — U6_SHOE 피처가 U6_PRESS 바디를 고침), 루트 Move14(U3_NEEDLE_PIN). 형상은 맞게 따라간다(P_M06_SHOE 부피 같음, bbox Z −4.9).
- 원장 갱신(`ledger.py commit`)은 불합격이라 하지 않음. 새 판정 기억 0건.
- 시간: 약 110분(예상 15분의 2배 넘음 — 이유 7절).

## 0. 근거 규칙

| 규칙 | 원문 | 이번 |
|---|---|---|
| E-03 | "과제 안 = 과제 범위 간섭 0(바뀐 것과 그 주변을 관련 조인트의 몇 점에서, E-17)" | 바뀐 8바디 × 이웃을 조인트 0 · 25 · 50 · 75 · 100 %에서 |
| E-17 | "SolidCraft는 관련 조인트 … 를 양 끝·중간(0·25·50·75·100 %)에 놓고 틈·겹침을 재고" | 2절 |
| E-16 | "판정은 수치로만 한다" | 부피 · bbox · 겹침 수 · 구멍 축 |
| M-08 | "정상 겹침: 볼트 나사부의 탭 물림(채움률 < 0.5), 구매처 CAD끼리의 미세 겹침, 설계상 압입" · "옛 기준선이 진짜 겹침을 가린 일이 있었다" | HOLDER ↔ 볼트는 상대에 탭 · 구멍이 없어 정상 겹침이 아님(3절) |
| M-01 | "상대 부품의 탭 또는 너트가 실제로 있음, 물림 ≥ 1.5d" | 고치는 안 CB5-12: 물림 8 mm = 1.6d |
| 안내서 '간섭' | "메시 바디 … `unchecked`로 나온다 — 0을 '겹침 없음'으로 읽지 않는다" | unchecked 쌍을 따로 봄(3절) |
| 실행 규칙 2 | "혼자 도는 읽기 부서도 MCP로 잰다 … 저장은 하지 않는다" | 앱 MCP, `save` 0회 |

## 1. 범위(E-17)

- `ledger.py scope`: 바뀜 0 · 새로 0 · 없어짐 0 · 이웃 0(형상 값이 그대로라 서명이 안 바뀜). 그래서 대상은 지시의 바뀐 부품 8개로 잡았다: `P_M03_CAR_PLATE` · `P_M03_CHAIN_ARM`(J_U5_X), `P_M05_CST_PLATE` · `P_M08_TUBE_BRKT_CST_O`(J_U7_HGT · CST_X · CST_Y), `P_M08_KDM_BRKT` · `P_M05_HOLDER` · `P_M06_BASE`(J_U7_HGT), `P_M02_BASE`(J_U4_X).
- 이웃은 측정 표 bbox로 골랐다(여유 5 mm, 자세는 행정만큼 쓸어 넓힌 상자) + 모델링부 목록(`neighbors.json`)과 합집합: REST U5 83 · U7 140 · U4 39, 자세 U5 134(케이블 베어 링크 전부 포함) · HGT 75(뒤 2점은 함께 움직이는 탭 물림 볼트 · 관 10개를 뺀 65) · 카세트 38(28) · U4 8. 원본 `tools/out/mech_RX-06-C2/verify/vneigh.json`.
- 작업 대상 모형(매트 · 테이프)은 넣지 않았다: 바뀐 부품의 형상 값이 그대로라 작업 대상 길이 달라지지 않는다. 전체 사이클은 라운드 끝 회귀가 본다.
- 판금(M-04) · 볼트(M-01) · 포트(M-06) · LITE: 새로 넣거나 옮긴 볼트 0, 새 판금 0, 새 LITE 0 → 대상 없음. 리지드 그룹 · 안 묶인 부품: 조인트 · occurrence 변화 0(모델링부 `joint.list` floating 0, 이번 자세 구동에서 errors 0 · conflicts 0).
- 통로: 앱에 v2.15.1이 열려 있었다(`inspect_design` path v2.15.1 · dirty false · 피처 3,709). `open`은 다시 부르지 않았다(안내서 '원복': 같은 경로는 디스크에서 다시 읽지 않음). 편집 전 `edit.checkpoint` 56.

## 2. 측정(앱 `measure` · `inspect.clearance` clearance 0 · `body_topology`)

### 2-1. REST(완료 판정 ①)

| 바디 | 부피 mm³ | bbox | 면 | 측정 표와 차 |
|---|---|---|---|---|
| P_M03_CAR_PLATE | 681,869.510 | X −2045~−1825 · Y 80~92 · Z 160~420 | 26 | 0 |
| P_M03_CHAIN_ARM | 75,195.043 | X −1950~−1910 · Y 80~275 · Z 420~848 | 14 | 0 |
| P_M05_CST_PLATE | 245,781.931 | X 50~58 · Y −200~−40 · Z 20~328 | 39 | 0 |
| P_M08_TUBE_BRKT_CST_O | 58,244.264 | X 58~88 · Y −266~−185 · Z 92~216 | 18 | 0 |
| P_M08_KDM_BRKT | 124,801.279 | X 14~46 · Y −200~−112 · Z 334~742 | 21 | 0 |
| P_M05_HOLDER | 32,632.629 | X 10~50 · Y −200~−90 · Z 285~334 | 34 | 0 |
| P_M06_BASE | 40,595.441 | X −142~−22 · Y −172~−90 · Z 120~195 | 39 | 0 |
| P_M02_BASE | 380,844.131 | X −330~−140 · Y −60~266 · Z 242~250 | 91 | bbox 0.0005(RX-06 때부터) |

지시의 bbox(CAR_PLATE · CHAIN_ARM · CST_PLATE)와 같다. `U7_BINDER`는 지금 설계에 없는 바디(Remove51)라 해당 없음.

### 2-2. 자세(완료 판정 ②) — 부피는 모든 점에서 REST와 같다

| 조인트 | 점 | bbox 이동(실측) | 구동 errors · conflicts |
|---|---|---|---|
| J_U5_X | 345 · 690 · 1035 · 1380 → 0 | CAR_PLATE · CHAIN_ARM X +345 · +690 · +1035 · +1380, Y · Z 그대로. 0으로 돌려 REST 값 | 0 · 0 |
| J_U7_HGT | −4 · −1.5 · 1 · 3.5 · 6 → 0 | CST_PLATE · TUBE_BRKT_CST_O · KDM_BRKT · HOLDER · M06_BASE Z −4 · −1.5 · +1 · +3.5 · +6 | 0 · 0 |
| MAINT_U7(J_U7_LATCH 12 → CST_X → CST_Y) | 2 · 3 · 6 · 8 · 11 · 13단계 | CST_PLATE · TUBE_BRKT_CST_O X +12.5 · +25, 그 뒤 Y −75 · −125 · −200 · −250. KDM_BRKT · HOLDER · M06_BASE 그대로 | 0 |
| J_U7_HGT 6 + CST_X 25 + CST_Y 250 | 1점 | CST_PLATE X 75~83 · Y −450~−290 · Z 26~334, TUBE_BRKT_CST_O X 83~113 · Y −516~−435 · Z 98~222 | 0 · 0 |
| J_U4_X | 24 · 48 · 71 · 95 → 0 | P_M02_BASE X −24 · −48 · −71 · −95 | 0 · 0 |

구멍이 따라가는지(부피만으로는 간접이라 구멍 축을 직접 봄):
- J_U5_X 1380의 `P_M03_CAR_PLATE`: 새 탭 r 2.1 두 개가 origin (−610, 80, 410) · (−575, 80, 410), 축 Y, 깊이 10 — REST (−1990 · −1955, 80, 410) + 1380. 다른 구멍 14개도 모두 +1380.
- HGT 6 + CST_X 25 + CST_Y 250의 `P_M08_TUBE_BRKT_CST_O`: 새 Ø5.5 두 개가 (83~89, −441.5, 168 · 204) — REST (58~64, −191.5, 162 · 198) + (25, −250, 6).
- 구동 시간: J_U5_X 0.37 s, J_U4_X 0.24 s, J_U7_HGT 0.24 s, J_U7_CST_X · CST_Y · LATCH 0.21~0.23 s(모델링부 값과 같다).

### 2-3. 과제 범위 겹침(완료 판정 ④)

| 자세 | 대상 × 상대 | overlaps | unchecked | truncated |
|---|---|---|---|---|
| REST | CAR_PLATE · CHAIN_ARM × 83 | 0 | 4 | false |
| J_U5_X 345 · 690 · 1035 · 1380 | 같은 2 × 134 | 0 · 0 · 0 · 0 | 2씩(CB5-16_M08_PY:44 · 45) | false |
| REST | U7 5바디 × 140(바디마다 따로) | 0 | 14 | false |
| J_U7_HGT −4 · −1.5 · 1 | 5 × 75 | 0 · 0 · 0 | 12씩(REST와 같은 쌍) | false |
| J_U7_HGT 3.5 · 6 | 5 × 65 | 0 · 0 | 0 | false |
| MAINT_U7 2 · 3 · 6 · 8 · 11 · 13 | CST_PLATE · TUBE_BRKT_CST_O × 28 | 0 ×6 | 0 | false |
| REST | P_M02_BASE × 39 | 1 = 기준선(아래) | 19 | false |
| J_U4_X 24 · 48 · 71 · 95 | P_M02_BASE × 8(P_M07_BEAM · 관 · 관 브래킷) | 0 ×4 | 0 | false |

- 기준선: `P_M02_BASE` ↔ `P_RX06_CARRIAGE` 0.027615 mm³(넓이 103.07 mm², Z 250.0000~250.0005). 판정 기억 `c6abcde9b2e5c1982d9f`(RX-06R 검도 v2.15.0, 맞닿는 면의 수치 잔차)와 값 · 자리가 같다. 새로 남기지 않음.
- HGT 3.5 · 6과 MAINT 점에서는 함께 움직이는 탭 물림 볼트 · 관 10개(`CB5-12_M05_6~10`, `CB5-16_M05_1:2~5`, `TU0604_M08P_U7C_TUCK_B`)를 상대에서 뺐다. 대상과 한 묶음으로 움직여 REST · HGT −4 · −1.5 · 1의 결과가 그대로다. 넣으면 한 점에 약 195 s가 든다(겹침 부피를 못 내는 쌍은 캐시가 다시 쓰지 않음).
- 작업 전(v2.15.0)과 대조: 모델링부의 저장본 CLI 결과 `verify/base_rest_clr_out.json`과 U5 4쌍 · U7 14쌍이 쌍 이름까지 같다. 이번 편집이 만든 새 겹침 · 새 unchecked 0.

## 3. unchecked 쌍 — 0으로 읽지 않고 따로 본 것

| 쌍 | 응답 | 판정 |
|---|---|---|
| CAR_PLATE ↔ CB5-12_M03_3 · 4 | boolean 실패 | 판정 기억에 있음(M-08 나사 물림 9 mm) |
| CAR_PLATE ↔ CB5-16_M08_PY:44 · 45 | boolean 실패 | 새 탭 `TAP_P_M03_CAR_PLATE_1 · 2`(r 2.1, 깊이 10)에 물린 볼트: 측정 표 bbox X −1994.25~−1985.75 · −1959.25~−1950.75, Z 405.75~414.25, 나사부 Y 72~88 → 탭 축 (−1990 · −1955, Z 410)과 같고 판(Y 80~92)에 8 mm 물림. 나사 물림 |
| CST_PLATE ↔ CB5-12_M05_6~10 | boolean 실패 | 판정 기억에 있음 |
| CST_PLATE ↔ CB5-16_M05_1:2~5 | boolean 실패 | 새 탭 `TAP_P_M05_CST_PLATE_1~4`((58, −152.5, 304 · 320) · (58, −191.5, 162 · 198), −X, 깊이 8 = 판 관통)에 물린 볼트. 나사 물림 |
| HOLDER ↔ CB5-12_M08_PZ_KDM ×2 | boolean 실패 | HOLDER 윗판 탭 r 2.1(26 · 36, −184.5, Z 330~334, Cylinder753 · 754)에 물린 볼트. 나사 물림 |
| TUBE_BRKT_CST_O ↔ TU0604_M08P_U7C_TUCK_B | "empty result" | 관이 브래킷 관 구멍 r 3.25를 지남(맞닿음). 작업 전과 같음 |
| P_M02_BASE ↔ 볼트 18개(CB5-16_M02_1~4 · :2 · :3, CB5-12_M02S_BASE_1~8 · BEAM_1 · 2, CB5-16_RX08_TOP ×2) | boolean 실패(BASE_1은 "implausible result volume 281.5") | 탭 · 관통 구멍에 든 볼트. BASE_5~8은 판정 기억에 있음. 이번에 BASE의 형상 값 변화 0(지운 Combine41은 빈 cut) |
| P_M02_BASE ↔ P_M02S_PIVOT_BRKT_B | "facets pass through each other by more than 3.6e-3 mm, but they could not be intersected" | 맞닿는 면의 0.004 mm 잔차로 봄(거리 못 잼). 기록만 |
| **HOLDER ↔ CB5-16_M05_1:2 · :3** | boolean 실패, `nearest` 거리 0.0 | **진짜 겹침 — 아래** |

### 동작 문제 V1 — 카세트 볼트 끝이 고정 HOLDER 벽을 뚫는다

- 볼트 `CB5-16_M05_1 (U7_CASSETTE:1/CB5-16_M05_1:2)` · `:3`: 앱 `measure` bbox X 46.0~67.0 · Y −156.75~−148.25 · Z 299.75~308.25(:3은 Z 315.75~324.25), 부피 554.85 mm³. 머리 X 62~67, 나사부 Ø5 × 16 = X 46~62. 관 브래킷 `P_M08_TUBE_BRKT_CST_V`(X 58~62, t4) → `P_M05_CST_PLATE`(X 50~58, 탭 관통 8) → **끝 X 46~50이 판 뒷면 밖으로 4 mm 나옴**.
- `P_M05_HOLDER`(U7_FIXED, 카세트와 따로 — J_U7_CST_X · Y로 안 움직임): 밑 스케치(피처 4836)가 L자 (10,−94)·(46,−94)·(46,−200)·(50,−200)·(50,−90)·(10,−90), Z 285~334 → **+X 벽 X 46~50이 Y −200~−90 · Z 285~334 전체**. 이 벽의 구멍은 `body_topology` 로 (Y −190 · Z 300 r 3), (Y −126~−124 · Z 300 r 3 긴 구멍), (Y −180 · −164 · Z 314 r 3.5)뿐이고 **(Y −152.5, Z 304 · 320)에는 구멍이 없다**. 벽 +X 면 넓이 5,250.9 mm²(구멍 2개가 더 있으면 약 5,205).
- 그래서 볼트 끝 Ø5 × 4 mm가 벽 살 안에 있다: 겹침 계산 π·2.5²·4 ≈ **78.5 mm³ × 2**(CAD는 `inspect.interference` · `inspect.clearance` 모두 boolean 실패로 부피를 못 냄 — 볼트 끝 면 X 46이 벽 안쪽 면 X 46과 같은 평면).
- 지금까지 "탭에 물린 볼트 ↔ 그 판"으로 읽혔다(mech_RX-06-C2_model.md 5절). HOLDER에는 그 자리에 탭이 없다 → M-08 정상 겹침이 아니다.
- 이번 과제가 만든 것이 아니다: v2.15.0 저장본에서도 같은 쌍이 unchecked(`verify/base_rest_clr_out.json`). 볼트는 PNEU-01 수정 2회차(v2.8.8)에 Z 304 · 320으로 옮겨졌다(mech_PNEU-01_model2.md 35줄 "CB5-16_M05_1 PNEU01_52·53(Z 304·320) 그대로").
- 완료 판정 ④ "과제 범위 간섭 0(옮긴 바디 ↔ 이웃)"의 옮긴 바디(`P_M05_HOLDER`) ↔ 이웃이라 미달로 적는다.
- **고치는 방법:** `CB5-16_M05_1:2 · :3` 두 개를 **CB5-12**로 바꾼다(머리 자리 X 62 그대로 → 끝 X 50.0 = 판 뒷면, HOLDER와 맞닿음 0). 물림 = 판 두께 8 mm = 1.6d ≥ 1.5d(M-01). STEP `purchased-step/CB5-12/` 있음. BOM CB5-16 −2 · CB5-12 +2. CB5-10은 물림 6 mm = 1.2d라 안 됨. 길이 공차로 끝이 나올 여유까지 두려면 HOLDER 벽 (Y −152.5, Z 304 · 320)에 Ø6.5 릴리프 2개를 더한다(디테일).
- 함께 볼 것(이번에 재지 않음): `CB5-16_M05_1:4 · :5`(X 48~69, Y −191.5, Z 162 · 198)도 끝이 판 뒷면 밖으로 2 mm 나온다(X 48~50). 그 자리 X 48~50에 다른 바디가 있는지 수정 회차에서 `inspect.clearance {bodies: [:4, :5]}`로 확인.

## 4. 완료 판정

| 항목 | 결과 |
|---|---|
| ① REST에서 대상 바디 부피 · bbox 변화 0 | 만족(2-1) |
| ② J_U5_X 양 끝, J_U7_CST_X · Y · J_U7_HGT 끝 자세에서 부피 같고 bbox가 강체 이동(탭 구멍이 따라감) | 만족(2-2, 구멍 축 확인) |
| ③ 타임라인 error 0 · 새 warning 0, Box326 · Combine41 없음 | 만족(error 0, warning 54 = 작업 전 54와 이름 · 글 같음, 두 이름 없음) |
| ④ 과제 범위 간섭 0(옮긴 바디 ↔ 이웃, 끝 자세) | **미달** — V1(HOLDER ↔ 카세트 볼트 2개, 작업 전부터). 그 밖은 0 |

등급 S: 맞다(새 구매품 0, 조인트 변화 0, 형상 값 변화 0. 수정 회차의 볼트 길이 바꿈도 있는 형번).

## 5. 디테일 · 구동 후보(기록만)

| id | 무엇 | 근거 | 고칠 것 |
|---|---|---|---|
| C2-V2(구동 후보) | 같은 꼴이 U6에 남음: `U6_SHOE` 컴포넌트 피처 `U6S_SHOE_SLOT`(extrude cut) · `U6S_SHOE_TOP`(sheet_flange) · `Cylinder789`(cut)가 `U6_PRESS`의 `P_M06_SHOE`를 고친다(J_U6_PRESS로 서로 움직임) | 앱 실측 `joint.drive J_U6_PRESS` 4.5 → −0.4 약 395 s, REST로 되돌리기 약 460 s(다른 조인트 0.2~0.4 s). 형상은 맞다: −0.4에서 부피 11,712.865 그대로, bbox Z 12.1~49.6(REST 17.0~54.5에서 −4.9). CYCLE 연구의 J_U6_PRESS 키 22점 | 세 피처를 `U6_PRESS`로 옮김(`component.move_features`, 판금 플랜지가 거부되면 P_M06_SHOE를 U6_PRESS 안에서 다시 만듦) |
| C2-V3(구동 후보) | 루트 `Move14`(translate 0·0·6)가 `U3_NEEDLE`의 `U3_NEEDLE_PIN`을 고침(J_U3_NEEDLE) | 정적 점검 `verify/static_scan_after_verify.json`. 구동 시간은 따로 못 잼: J_U6_PRESS 2번 + J_U3_NEEDLE 2번 묶음이 약 1,050 s → 바늘은 한 번 약 100 s 이하로 어림 | Move14를 U3_NEEDLE로 옮기거나 바늘 형상에 +6을 넣음 |
| RX-06-C3(모델링부가 올림) | 작업 대상 테이프 모형 Split(루트 27 + `WP_TP_G_SEAM` · `WP_TP_V_SEAM` 컴포넌트의 Split 13) | 같은 정적 점검. 재지 않음 | 모델링부 보고 6절 |
| C2-V4 | 겹침 부피를 못 내는 볼트 ↔ 탭 쌍 가운데 판정 기억에 없는 것 약 30쌍(3절 표) | `tools/out/judged.json` 이름 대조 | 라운드 끝 회귀 전에 판정 기억에 올림(서명 키). 그 전에 V1처럼 상대에 탭 · 구멍이 있는지 `body_topology`로 하나씩 확인 |
| C2-V5 | `P_M02_BASE` ↔ `P_M02S_PIVOT_BRKT_B` 0.004 mm 면 잔차(검증 못 함) | 3절 | 디테일링에서 맞닿는 면 좌표 확인 |

모델링부가 못 찾은 것: 모델링부 정적 점검은 '루트 피처'만 봤다. 이번 점검은 '피처의 컴포넌트 ≠ 바디의 컴포넌트이고 그 사이에 조인트가 있음'으로 넓혀 U6_SHOE → U6_PRESS를 더 찾았다.

## 6. 원복 · 저장 확인

- 끝 상태: `motion.play REST 0` + `joint.drive` J_U4_X 0 · J_U7_HGT 0 · J_U5_X 0 · J_U7_CST_X 0 · CST_Y 0 · LATCH 0 · J_U6_PRESS 4.5 · J_U3_NEEDLE 0. 8바디 REST 값 다시 확인(`verify/r8c.json`).
- `inspect_design`: dirty false, 피처 3,709, error 0, warning 54, 바디 879. 저장 0회. 저장본 5,632,661 B · 12:49:12 · sha1 `392a1d6a04db0a87…` 전후 같음.
- `ledger.py commit`은 하지 않음(불합격).

## 7. 시간(E-23)

- 걸린 시간 약 110분(예상 S 15분). 통로 MCP(앱), 저장본 열기 0회, CAD 호출 약 55, 브라우저 0.
- 2배를 넘은 이유: ① 겹침 부피를 못 내는 볼트 ↔ 탭 쌍이 든 `inspect.clearance`가 한 자세에 약 195 s(캐시가 다시 쓰지 않음) — HGT · MAINT 11점 묶음이 약 17분 · 20분. ② 앱 응답 대기 300 s를 넘긴 묶음은 결과가 돌아오지 않아(앱은 끝까지 돎) 자세별로 다시 보냄. ③ 구동 후보 확인용 J_U6_PRESS · J_U3_NEEDLE 구동이 약 1,050 s + 395 s + 460 s.
- 앱 막힘 · 재시작 0.

## 워크플로우 메모

- MCP 호출(직접 도구 · `solidcraft-cli mcp --connect`)은 앱이 300 s 안에 답하지 않으면 "the app did not answer"로 끝나고 결과를 잃는다(앱은 계속 돈다, `pending`으로도 못 받음). 안내서의 "`batch` 하나 약 5분 안"을 "한 호출 4분 안, 넘을 것 같으면 자세 하나씩"으로 좁히면 좋겠다.
- `inspect.clearance`는 겹침 부피를 못 낸 쌍(unchecked)을 캐시하지 않아 자세마다 다시 계산한다(쌍 하나 15~180 s). 자세 검사에서는 대상과 함께 움직이는 탭 물림 볼트 · 관을 상대에서 빼는 것을 절차로 두면 좋겠다(65 상대 0.03 s ↔ 75 상대 194 s).
- 측정 표의 `component`가 볼트 사본은 자기 이름(예 `CB5-16_M05_1`)이라 '어느 유닛과 함께 움직이는지'를 서명만으로 못 가린다. 서명에 부모 유닛 경로나 조인트 경로가 있으면 함께 움직이는 바디를 자동으로 뺄 수 있다.
- unchecked "boolean 실패"를 '탭 물림'으로 읽는 관행이 진짜 겹침(V1)을 4개 버전 넘게 가렸다(M-08 "옛 기준선이 진짜 겹침을 가린 일"과 같은 꼴). unchecked 쌍은 상대 부품에 그 축의 탭 · 구멍이 있는지 `body_topology {faces: "cylinders"}`로 확인한 뒤에만 판정 기억에 올리게 하면 좋겠다.
- 큰 이웃 목록(100개 넘는 이름)을 MCP 도구 인자로 직접 쓰기 어렵다. 이번에는 스크립트 파일을 앱에 보내는 작은 클라이언트(`tools/out/mech_RX-06-C2/verify/mcpsend.py`, `solidcraft-cli mcp --connect` 위 JSON-RPC)를 썼다.
- 정적 점검(피처의 컴포넌트 ≠ 바디의 컴포넌트 + 그 사이 조인트)을 엔진 도구로 두면 준비 점검이 매번 돌릴 수 있다. 이런 피처가 있는 조인트는 구동 한 번이 수 분이라 전체 회귀 시간을 좌우한다.

## 원본 파일

`tools/out/mech_RX-06-C2/verify/`: `vneigh.json`(이웃), `s*.json`(보낸 스크립트) · `r*.json`(결과: r1_rest, r2_u5, r3_0~4, r4p0~2 · r4p2x~5x, r5p0x~6x, r6a · r6b · r6c, r8a · r8c), `holder_topology.json`, `static_scan_after_verify.json`, `inspect.json`, `summ.py` · `mcpsend.py` · `mcpwait.py`.
