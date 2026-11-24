# RX-DC-03 모델링 수정 2회차 — 세움 받침 꺾음 날 뿌리 (2026-11-24)

요약
- 저장: `3D_Modeling/FSAP_v2.30.2.sc`(기준 v2.30.1을 먼저 다른 이름으로 저장한 뒤 고침, md5 828adccf8649519777420135a4ad2723). `tools/config.json` doc → v2.30.2. 통로 MCP(앱에 열려 있던 v2.30.1, dirty false, 다시 열지 않음).
- 바꾼 부품: `P_RXDC03_RISER_BRKT_판금` 하나. 꺾음 날 아래 플랜지 X −308.6~−296.6 · Y 83~97 · Z 250~253(t3) join, 피처 `RXDC03_RISER_FOLD_FLANGE`(U4_XCAR 활성). 13,609.45 → **14,113.45 mm³**(+504, 기대값과 같음), 107.9 → **111.9 g**.
- 오조작 50 N 뿌리: SF 0.63 → **3.48**(해석부 권장안 A 손계산, `fea/results/mech_RX-DC-03_fix1_handcalc.json` fixA). 해석 못 함 — 환경 없음(D-16).
- 블록 윗면 Z 250은 X −305부터다. 늘린 플랜지는 X −305~−296.6이 앉고 3.6은 블록 밖(블록은 고치지 않음, 결정로그 RXDC03-F2-2).
- 과제 범위 겹침 0(J_U4_X 0·47.5·95, PRESS 0). U5 C-46 한계 틈 **7.068** ≥ 5.5 그대로. J95 bbox X −413.6~−363(플랜지가 J_U4_X를 따라감).
- 새 부품·지운 부품·조인트 변경 없음. 볼트 변경 없음. d₁ 45 헤드 상자 여유 바뀌지 않음.
- BOM: `docs/bom/FSAP_v2.30.2_made.csv`(세움 받침 행) · `_purchased.csv`(v2.30.1 복사, 변경 없음).
- 미완: 없음.

## 1. 문서 확인 · 다른 이름 저장

| 단계 | 한 것 | 확인 |
|---|---|---|
| 앱 상태 | `running` 빈 목록, `inspect_design` name FSAP_v2.30.1, path 3D_Modeling/FSAP_v2.30.1.sc, dirty false | 수정 1 저장 상태 그대로(원복할 흔적 없음, 수정 회차라 E-08 원복 대상 아님) |
| 다른 이름 저장 | `save {path: 3D_Modeling/FSAP_v2.30.2.sc}` 68,183,543 B → 열린 문서 name FSAP_v2.30.2 | config.json doc → `../3D_Modeling/FSAP_v2.30.2.sc` |
| 편집 전 | `edit.checkpoint` 186 | |
| 설명 | `document.metadata.set description` = "RX-DC-03 mechanism fix2: riser fold root tied to base flange, flange X-308.6..-296.6 Y83..97 Z250..253 (+4.0 g, misuse SF 3.48)" | |

## 2. 블록 윗면 확인(지시: X −308.6~−305에서도 Z 250인가)

view.pick(REST) 결과:

| 광선 | 맞은 것 |
|---|---|
| (−302, 90) · (−297.5, 96.7) · (−297.5, 84.5) 아래로 | `P_RX19_BLOCK_밀링` 윗면 Z 250 |
| (−306, 96.7) · (−308.3, 96.7) 아래로 | 매트 MAT_L Z 10(블록 없음) |
| (−308.3, 84.5) · (−306, 84.5) Z 252.5에서 아래로 | 그네 쪽 `P_RXDC03_LEAD_GUIDE_판금` Z 133.9(블록 없음) |
| X −320에서 +X로, Z 249.5, Y 84.5 · 90 · 96.5 | 블록 −X 면 **X −305.0** |

→ 블록 윗면은 X −305부터. 지시 수정안 A의 좌표(X −308.6~−296.6)는 그대로 두었다. 꺾음 날 단면(X −308.6~−296.6)을 아래에서 다 이어야 L 단면이 뿌리까지 일하기 때문이다. 앉는 길이는 8.4 / 12, 블록 밖 3.6은 플랜지 판 자체가 받는다. 앉는 면 누름 641 N(해석부 fold_bottom_force) / (8.4 × 3) ≈ 25 MPa로 문제없다. 블록 아래 X −308.6~−305에는 Z 134 위로 Z 250까지 아무것도 없다.

## 3. 바꾼 것

| 부품 | 전(v2.30.1) | 후(v2.30.2) |
|---|---|---|
| `P_RXDC03_RISER_BRKT_판금` | 꺾음 날 X −308.6~−296.6 · Y 83~86 · Z 253~392, 아래 끝 Z 253 자유단(Z 250 층 최소 X −296.6). 13,609.45 mm³ · 107.9 g | 꺾음 날 아래 플랜지 X −308.6~−296.6 · Y 83~97 · Z 250~253 join → 꺾음 날 · 세운 판 · 판 위 플랜지가 한 몸. **14,113.45 mm³ · 111.9 g**(SUS304 7.93) · 면 22 · 닫힌 바디 1. bbox REST X −318.6~−268 · Y 73~97 · Z 250~392(그대로), J95 X −413.6~−363 |

피처: `solid.box corner (−308.6, 83, 250) length 12 width 14 height 3 join targets P_RXDC03_RISER_BRKT_판금`, `component.activate U4_XCAR` 아래(수정 1의 교훈 RXDC03-F1-3). 저장본 document.json: id 101041, component 97892(U4_XCAR).

재질 SUS304 그대로, 리지드 그룹 그대로(같은 바디). 새 부품 · 지운 부품 · 조인트 · 행정 변경 없음 → machine.json · 동작 연구 고침 없음.

## 4. 검사(수치, E-16 · E-22 — 과제 안 범위)

### 4-1. 세움 받침 vs 이웃 91(inspect.clearance 10 mm, PRESS 0) — `tools/out/mech_RX-DC-03/model2/c1.json`

| 이웃 | J_U4_X 95 | 47.5 | 0 |
|---|---|---|---|
| 겹침 | **0** | **0** | **0** |
| 블록 · RISER_1 · RISER_2 | 0(앉는 면 접촉) | 0 | 0 |
| STEP대기_MR-PWS1CBL5M-A2-H | 0.75 | 0.75 | 0.75 |
| STEP대기_MR-J3ENCBL5M-A2-H | 2.14 | 2.14 | 2.14 |
| 구름 고리(_LOOP) | — | — | PWR 1.75 · ENC 2.14 |
| P_M08_TUBE_CLAMP_L_6 | 5.0 | 5.0 | — |
| P_M03_GCOV_SM | 7.068 | — | — |
| CB5-12_RXDC03_T2_1 · _2 | 7.43 | 7.43 | 7.43 |

수정 1과 같은 값이다. 새 플랜지에 10 mm 안으로 새로 나온 것은 없다(가장 가까운 것은 여전히 T2 볼트 7.43, 플랜지 −Y 끝 Y 83 · Z 250 자리).

J_U4_PRESS 4자세(0 · 19.523 · −8.171 · 5.676): 바꾼 것은 블록(U4_XCAR) 쪽 Z ≥ 250이고 그네 쪽 부품 꼭대기는 Z 163이라 87 넘게 떨어진다. 그네 쪽에서 바뀐 쌍이 없어 개념 W 검사 값(스토퍼 `P_RX08_STOP_BLOCK_밀링` 3.71 · Y-020B 6.86)이 그대로다. 스토퍼는 이웃 91에 들어 있고 10 mm 안에 나오지 않았다.

### 4-2. U5 C-46 한계(J_U4_X 95 · J_U5_X 1365 · 1310 × LIFT 30 · −10) — `model2/c1_u5.json`

| J_U5_X | LIFT 30 | LIFT −10 |
|---|---|---|
| 1365 | **7.068** | 7.068 |
| 1310 | 7.068 | 7.068 |

최소 7.068 ≥ 5.5. 가까운 자리는 타이 판 −X 끝(X −413.6 @J95)이고 새 플랜지(J95 X −403.6~−391.6)는 그보다 10 안쪽이다.

### 4-3. 볼트 · 렌치 길

볼트를 바꾸지 않았다. 새 플랜지는 Z 250~253, X ≤ −296.6이라 RISER_1 머리(X −292.25~−283.75 · Z 253~258) 렌치 길(머리 위 Ø8.5 × 30, Z 258~288)에 들어가지 않는다. 머리 ↔ 플랜지 −X 쪽 4.35. 막힘 0(수정 1 값 그대로).

### 4-4. 하중 손계산(E-18, FEA 못 함 — 환경 없음 D-16)

해석부 안 A 값(`fea/results/mech_RX-DC-03_fix1_handcalc.json` fixA_flange_extend)을 그대로 쓴다. 그린 형상이 그 전제(플랜지 X −308.6~−296.6 · Y 83~97 · Z 250~253, 꺾음 날과 한 몸)와 같다.

| 경우 | σ MPa | SF(σy 205) | 처짐 mm |
|---|---|---|---|
| 운전 위 팔 10.9 N | 12.8 | 15.97 | 0.031 |
| 오조작 50 N 타이 Z 344(팔 91) | 39.2 | 5.23 | 0.042 |
| 오조작 50 N 위 팔(팔 137) | 59.0 | **3.48** | 0.143 |
| f1(끝 50 g) | 340.6 Hz | | |
| 꺾음 날 아래 힘 641 N → 이음 전단 15.3 · 모살 a2×12 19.1 MPa | | | |
| 볼트(+X 쪽) 411 N, M5 12.9 · A5052 물림 9 | 암나사 전단 SF 15.09 | | |

## 5. 저장 · 측정 표

- 저장 전: `motion.play REST 0`(moved true, unmoved 0), joints · sketches 숨김, `save {path: 3D_Modeling/FSAP_v2.30.2.sc}` 68,183,407 B.
- 저장 확인(저장본 document.json): name FSAP_v2.30.2, 피처 `RXDC03_RISER_FOLD_FLANGE` corner (−308.6, 83, 250) 12 × 14 × 3 component 97892, RXDC03 124(v2.30.1 122 + 피처 이름 · 설명), U4_CABLE_LOOP 2(v2.30.1과 같음), "id" 38,559(+1).
- 측정 표: `ledger.py sigpatch --doc 3D_Modeling/FSAP_v2.30.2.sc --parts tools/out/mech_RX-DC-03/model2/sig_parts.json` → 바뀜 1, 전체 3,758. 앞 표 `model2/signatures_before.json`.
- 임시 STEP(해석부): `tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix2.step`(REST, 52,453 B).
- 다시 실행 재료: `tools/out/mech_RX-DC-03/edit.json`(7단계, 다른 이름 저장 뒤) · `edit_meta.json`(base v2.30.1 → result v2.30.2). 수정 1 기록은 `model1/`의 결과 파일로 남음.
- 사람용 스크린샷: 찍지 않음(외관은 사용자가 앱에서 본다).
- 결정로그: 끝에 '구동 RX-DC-03 수정 2' 표(RXDC03-F2-1 · F2-2).

## 6. 문서 담당에게 넘길 것

- CHANGELOG: v2.30.2(RX-DC-03 수정 2, 마지막 +1, 컴포넌트 증감 없음) 줄.
- BOM: `FSAP_v2.30.2_made.csv` 세움 받침 행(형상에 꺾음 날 아래 플랜지, 질량 111.9, 비고 수정 2) · `_purchased.csv`(변경 없음).
- 커밋: `FSAP_v2.30.2.sc`(수정 1의 v2.30.0 · v2.30.1 · 되돌린 v2.29.3이 아직 안 올라갔으면 함께).

## 워크플로우 메모

1. MCP 서버의 허용 폴더가 `3D_Modeling`·recovery·서버 임시 폴더뿐이라 `batch {path}` · `export {path}`에 `tools/out/` 경로를 줄 수 없었다(머리말은 `--allow-path workspace`라 했다). 검사 스크립트와 임시 STEP은 서버 임시 폴더에 복사해 쓰고 `tools/out/`으로 옮겼다.
2. `batch` 안의 `inspect.measure {body, summary:true}`가 이번에도 모든 바디를 재 4 MB 응답이 났다(수정 1 메모 4와 같음). `motion.play`도 positions 전체를 돌려 135 KB가 났다. 한 바디는 `measure` 도구를 따로 부른다.
3. 해석부 수정안의 '블록 윗면이 X −308.6~−305에서도 Z 250인지'는 STEP만으로는 알 수 없어 모델링부에 남겨졌다. 해석부가 받침 상대 부품 윤곽도 함께 내보내면 수정안이 처음부터 앉는 길이를 셈에 넣을 수 있다.
