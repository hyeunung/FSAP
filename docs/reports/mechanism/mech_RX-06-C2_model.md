# RX-06-C2 모델링 — 움직이는 컴포넌트 바디를 고치는 루트 피처 옮기기 (모델링부, 2026-11-13)

요약(10줄 안):
- 저장: `FSAP_v2.15.0.sc` → **`3D_Modeling/FSAP_v2.15.1.sc`**(마지막 자리 +1, 새로 생기거나 없어진 컴포넌트 0). 통로 MCP(앱). `tools/config.json` doc 고침. 저장 상태 REST step 0, 조인트·스케치 숨김, 문서 이름 FSAP_v2.15.1.
- **형상 값 변화 0.** 피처 3,717 → 3,709(지움 22, 새로 14, 컴포넌트만 바뀜 8). 대상 8바디의 REST 부피·bbox·면 수가 작업 전과 끝자리까지 같다.
- **지시 대상:** Combine43·44(U5_CAR) · Combine45(U7_CASSETTE)는 `component.move_features`가 거부해(도구 원통을 먼저 옮겨도, 함께 옮겨도 같음) Combine + 도구 원통을 지우고 같은 자리·같은 치수의 Cylinder cut 10개를 그 컴포넌트 피처로 다시 만들었다. Cylinder351·352는 U7_CASSETTE로 옮겼다. Box326 · Combine41(+ 도구 원통 2)은 지웠다.
- **같은 꼴 더 찾아 함께 고침(지시 밖, 같은 조인트로 움직이는 바디):** P_M08_TUBE_BRKT_CST_O(U7_CASSETTE의 하위 컴포넌트) Cylinder1175·1176, 그리고 J_U7_HGT로 움직이는 U7_FIXED의 Combine42 · Extrude48 · Cylinder753·754, U6_SENSOR의 Extrude47. 지난 검도의 정적 점검이 못 본 것이다(3절).
- **끝 자세:** J_U5_X 0 · 690 · 1380, MAINT_U7 3 · 13단계(J_U7_CST_X 25 · J_U7_CST_Y 250), J_U7_HGT −4 · 6, J_U4_X 95에서 대상 바디 부피가 REST와 같고 bbox가 강체 이동과 같다(탭 구멍이 따라간다).
- **구동 시간:** `joint.drive` J_U5_X 0.65 s · J_U7_HGT 0.31 s · J_U4_X 0.36 s(작업 전 J_U4_X 한 번 465~574 s).
- 타임라인 error 0, warning 54 → 54(새 것 0). Box326 · Combine41 없음. 과제 범위 겹침 0.
- U7_BINDER는 지금 설계에 없다(Remove51로 지워짐). Cylinder351·352는 옮겼지만 그 바디의 부피·bbox 확인은 해당 없음.
- 남은 같은 꼴: 작업 대상 테이프 모형 WP_TAPE_S·L·G·V의 Split 27개(J_WP_*로 움직임). 작업 대상 모형이라 손대지 않고 구동 후보로 올린다(6절).
- 미완 없음. 예외 요청 없음.

## 0. 근거 규칙

| 규칙 | 원문 | 이번 |
|---|---|---|
| E-03 | "합격의 첫 조건은 작업 대상을 넣은 전 구간 동작과 간섭 0" · "과제 안 = 과제 범위 간섭 0" | 옮긴 바디 × 이웃을 REST와 끝 자세에서 잼(5절) |
| E-05 | "작은 형상 변경은 마지막 자리 +1" · "이미 저장·커밋된 버전 파일은 덮어쓰지 않는다" | v2.15.1 새 파일. v2.15.0은 5,632,952 B · 09:28 그대로 |
| E-15 | "기계의 모든 움직임은 CAD 조인트로 정의한다" · "부품 이름 목록으로 위치를 직접 옮기지 않는다" | 자세는 `joint.drive` · `motion.play`(MAINT_U7 · REST)로만 |
| E-16 | "합격·불합격은 … 수치로만 정한다" | 부피 · bbox · 겹침 수 |
| E-22 | "지시 좌표가 실측과 다르면 지시서의 기준을 지키는 쪽으로 정하고 보고서에 적는다" | Combine은 옮길 수 없어 지시의 기준(피처가 그 컴포넌트에 속하고 탭 구멍이 따라감, 형상 값 변화 0)을 지키는 방법으로 바꿈(2절) |
| 실행 규칙 2 | "모델링부는 SolidCraft MCP로 그린다" · "`save {}`(덮어쓰기)는 쓰지 않는다" | MCP. `save {path: v2.15.1}` 한 번 |
| 실행 규칙 19 | "저장 전에 … 조인트 글리프를 숨긴다" · "스케치도 같다" | 숨김 조인트 771 · 스케치 304(작업 전과 같음) |

## 1. 문서 확인

- 앱에 `FSAP_v2.15.0`이 열려 있었다(`inspect_design`: path v2.15.0, dirty false, 피처 3,717, error 0, warning 54). `running` 빈 목록.
- `open`은 다시 부르지 않았다. 안내서 '원복' "같은 경로를 다시 `open`해도 디스크에서 다시 읽지 않는다". 앱 안 설계가 디스크의 v2.15.0과 같은지는 저장 뒤 두 파일의 `document.json`을 견줘 확인했다(7절: 의도한 차이만 있다).
- 편집 전 `edit.checkpoint` 45. REST 연구가 있어 동작 상태 초기화는 `motion.play REST 0`.
- 지시 문서 번호: 실행 지시 (a)는 v2.13.0이라고 적었지만 `tools/config.json` doc는 v2.15.0이었고 과제 지시문 절차 2도 v2.15.0 → v2.15.1이다. config를 따랐다.

## 2. 고친 것

### 2-1. 옮긴 피처 (`component.move_features`, REST 자세 = 피처를 만든 자세, 유닛 occurrence 변환은 모두 단위 행렬)

| 피처(id) | 고치는 바디 | 전 → 후 | 걸린 시간 |
|---|---|---|---|
| Cylinder351(4735) · Cylinder352(4736) Ø4.2 cut | U7_BINDER(뒤에 Remove51로 지워짐) | 루트 → U7_CASSETTE(4722) | 약 1,040 s |
| SK_DC204_BASE_SLOT(5216) · Extrude47(5217) 슬롯 cut | P_M06_BASE | 루트 → U6_SENSOR(13) | 약 880 s |
| SK_DC204_HOLDER_SLOT(5218) · Extrude48(5219) 슬롯 cut, Cylinder753(9263) · Cylinder754(9264) Ø4.2 cut | P_M05_HOLDER | 루트 → U7_FIXED(4718) | 약 1,040 s |

### 2-2. 지우고 같은 구멍을 컴포넌트 피처로 다시 만든 것

`component.move_features`가 Combine을 거부했다. 보낸 순서와 응답:

| 시도 | 응답 |
|---|---|
| 도구 원통 2 + Combine43을 함께 U5_CAR로 | "Combine43 works on bodies that would be split between components" |
| 도구 원통 4 + Combine44를 함께 U5_CAR로 | "Combine44 works on bodies that would be split between components" |
| 도구 원통 4만 먼저 U5_CAR로(지시서의 방법) | 같은 응답 |

- 지난 RX-06 수정 1회차의 Combine41도 같은 응답이었다(mech_RX-06_model1.md 1절).
- 그래서 Combine + 도구 원통을 `timeline.delete` 한 번으로 지우고(약 640 s), 도구 원통과 같은 base · 축 · 반지름 · 깊이의 `solid.cylinder {operation: cut, targets: [바디]}`를 만든 뒤 `component.move_features`로 그 컴포넌트에 넣었다(타임라인 끝이라 14개 만들기 + 옮기기 4번이 20 s 안).
- 이 바디들의 구멍 면을 이름으로 집는 조인트·피처는 없다(`document.json` 전체에서 `<바디>:face` 참조 0, 조인트 584개는 모두 frame · point 맞춤). 그래서 구멍 피처가 바뀌어도 깨지는 참조가 없다.
- 이 구멍들 뒤에 같은 바디를 고치는 피처는 모두 cut이라 순서가 바뀌어도 결과가 같다.

| 지운 피처 | 새 피처(id) | 바디 | base · 축 | Ø × 깊이 | 들어간 컴포넌트 |
|---|---|---|---|---|---|
| Cylinder1225·1226 + Combine43 (96488~96490) | TAP_P_M03_CAR_PLATE_1·2 (98279·98280) | P_M03_CAR_PLATE | (−1990 · −1955, 80, 410) · +Y | 4.2 × 10 | U5_CAR(36) |
| Cylinder1227~1230 + Combine44 (96491~96495) | TAP_P_M03_CHAIN_ARM_1~4 (98281~98284) | P_M03_CHAIN_ARM | (−1950, 92, 612 · 636) · (−1950, 146 · 174, 818) · +X | 4.2 × 10 | U5_CAR(36) |
| Cylinder1231~1234 + Combine45 (96496~96500) | TAP_P_M05_CST_PLATE_1~4 (98285~98288) | P_M05_CST_PLATE | (58, −152.5, 304 · 320) · (58, −191.5, 162 · 198) · −X | 4.2 × 8 | U7_CASSETTE(4722) |
| Cylinder1175·1176 (96432 · 96434) | HOLE_P_M08_TUBE_BRKT_CST_O_1·2 (98289·98290) | P_M08_TUBE_BRKT_CST_O | (64.5, −191.5, 162 · 198) · −X | 5.5 × 7 | P_M08_TUBE_BRKT_CST_O(96011, U7_CASSETTE의 하위) |
| Cylinder1223·1224 + Combine42 (96485~96487) | TAP_P_M08_KDM_BRKT_1·2 (98291·98292) | P_M08_KDM_BRKT | (30, −190 · −122, 742) · −Z | 4.2 × 10 | U7_FIXED(4718) |

Cylinder1175·1176은 한 바디만 자르는 피처라 옮길 수도 있었지만, 옮기면 그 자리(타임라인 2,788번째)부터 다시 계산해 약 11분이 더 든다. 어차피 한 번 도는 지우기에 넣고 끝에서 다시 만들었다.

### 2-3. 지운 빈 피처

| 피처 | 왜 비었나 | 확인 |
|---|---|---|
| Cylinder1221·1222 + Combine41 (96482~96484) | 도구 원통이 X −330~−320 · Z 233.9~238.1, P_M02_BASE는 Z 242~250 | 지운 뒤 P_M02_BASE 380,844.131 mm³ · bbox · 면 91 그대로 |
| Box326 (97668) | 자르는 바디 P_M02R_CYLBRKT가 바로 다음 Remove82로 지워짐 | 바디 이름 목록 변화 0 |

Combine41만 지우면 도구 바디 TAP_P_M02_BASE_1·2가 루트에 남으므로 원통 2개도 함께 지웠다.

### 2-4. 만든·지운 부품

없음. 바디 이름 목록 변화 0(앱 `inspect_design` 바디 879개 이름 전후 같음). 컴포넌트 682 · occurrence 2,918 그대로. 구매품 · 볼트 · 재질 · 조인트 · 동작 연구 변화 0. 기계 정의(`tools/machine.json`) 고칠 것 없음.

## 3. 지시 밖에서 함께 고친 것과 이유

지시서의 근거(mech_RX-06_verify1.md 5절)는 저장본 `document.json`의 정적 점검이다. 같은 점검을 v2.15.0에 다시 돌리되, 컴포넌트가 움직이는지를 조인트 그래프(리지드 묶음 → 바닥까지의 조인트 경로)로 판정했다(`tools/out/mech_RX-06-C2/static_scan_before.json`).

| 컴포넌트 | 바닥까지의 조인트 | 루트 피처 | 바디 | 지시서 |
|---|---|---|---|---|
| U5_CAR | J_U5_X | Combine43 · 44 | P_M03_CAR_PLATE · CHAIN_ARM | 있음 |
| U7_CASSETTE | J_U7_HGT · CST_X · CST_Y | Cylinder351·352, Combine45 | U7_BINDER(지워짐) · P_M05_CST_PLATE | 있음 |
| U4_WHEEL_N | J_U4_X | Combine41, Box326 | P_M02_BASE · (지워진 바디) | 있음 |
| P_M08_TUBE_BRKT_CST_O(부모 U7_CASSETTE) | J_U7_HGT · CST_X · CST_Y | Cylinder1175·1176 | P_M08_TUBE_BRKT_CST_O | **없음** |
| U7_FIXED | J_U7_HGT | Extrude48, Cylinder753·754, Combine42 | P_M05_HOLDER · P_M08_KDM_BRKT | **없음** |
| U6_SENSOR | J_U7_HGT | Extrude47 | P_M06_BASE | **없음** |
| WP_TAPE_S · L · G · V | J_WP_*_X · Y · ROT | Split 27개 | TP_S_07a · TP_L_36a · TP_G_31a · TP_V_31a | 없음(6절) |

- 완료 판정 ②가 J_U7_HGT 끝 자세를 요구한다. J_U7_HGT는 U7_CASSETTE뿐 아니라 U7_FIXED · U6_SENSOR도 함께 움직인다. 이 유닛의 루트 피처를 그대로 두면 J_U7_HGT를 움직일 때 P_M05_HOLDER · P_M08_KDM_BRKT · P_M06_BASE의 슬롯 · 구멍이 제자리에 남고(이번 과제가 없애려는 바로 그 결함), 구동 한 번마다 타임라인 1,072번째부터 다시 계산한다(피처 시간 합 926 s).
- E-22 "지시서의 기준을 지키는 쪽으로"에 따라 같은 방법으로 함께 고쳤다. 형상 값 변화 0은 같다.
- 손대지 않은 것: 움직이지 않는 컴포넌트의 루트 피처(U5_WHEEL_F 18, U1_FRAME 39, U3_HEAD 20, U2_TABLE 13, U8_PNEU 아래 관 빗·클램프 등)는 지시대로 그대로 두었다.

## 4. 형상 확인 — REST와 끝 자세 (앱 `measure`, mm · mm³)

### 4-1. REST (작업 전 = 모든 편집 뒤, 끝자리까지 같음)

| 바디 | 부피 | X | Y | Z | 면 |
|---|---|---|---|---|---|
| P_M03_CAR_PLATE | 681,869.510 | −2045~−1825 | 80~92 | 160~420 | 26 |
| P_M03_CHAIN_ARM | 75,195.043 | −1950~−1910 | 80~275 | 420~848 | 14 |
| P_M05_CST_PLATE | 245,781.931 | 50~58 | −200~−40 | 20~328 | 39 |
| P_M02_BASE | 380,844.131 | −330~−140 | −60~266 | 242~250 | 91 |
| P_M08_TUBE_BRKT_CST_O | 58,244.264 | 58~88 | −266~−185 | 92~216 | 18 |
| P_M08_KDM_BRKT | 124,801.279 | 14~46 | −200~−112 | 334~742 | 21 |
| P_M05_HOLDER | 32,632.629 | 10~50 | −200~−90 | 285~334 | 34 |
| P_M06_BASE | 40,595.441 | −142~−22 | −172~−90 | 120~195 | 39 |

원본: `tools/out/mech_RX-06-C2/rest_before.json`. 지시서의 bbox(CAR_PLATE X −2045~−1825 등)와 같다.

### 4-2. 끝 자세

| 자세(조인트로 만듦) | 바디 | 부피 | bbox 실측 | 강체 이동 기대값 | 판정 |
|---|---|---|---|---|---|
| J_U5_X 1380(끝) | P_M03_CAR_PLATE | 681,869.510 | X −665~−445 · Y 80~92 · Z 160~420 | X +1380 | 맞음 |
| | P_M03_CHAIN_ARM | 75,195.043 | X −570~−530 · Y 80~275 · Z 420~848 | X +1380 | 맞음 |
| J_U5_X 690(가운데) | P_M03_CAR_PLATE | 681,869.510 | X −1355~−1135 | X +690 | 맞음 |
| | P_M03_CHAIN_ARM | 75,195.043 | X −1260~−1220 | X +690 | 맞음 |
| J_U5_X 0(끝 = REST) | 두 바디 | 같음 | REST와 같음 | — | 맞음 |
| MAINT_U7 3단계(J_U7_LATCH 12 · J_U7_CST_X 25) | P_M05_CST_PLATE | 245,781.931 | X 75~83 · Y −200~−40 · Z 20~328 | X +25 | 맞음 |
| | P_M08_TUBE_BRKT_CST_O | 58,244.264 | X 83~113 · Y −266~−185 | X +25 | 맞음 |
| MAINT_U7 13단계(+ J_U7_CST_Y 250) | P_M05_CST_PLATE | 245,781.931 | X 75~83 · Y −450~−290 · Z 20~328 | X +25 · Y −250 | 맞음 |
| | P_M08_TUBE_BRKT_CST_O | 58,244.264 | X 83~113 · Y −516~−435 · Z 92~216 | X +25 · Y −250 | 맞음 |
| | P_M08_KDM_BRKT · P_M05_HOLDER · P_M06_BASE | REST와 같음 | REST와 같음 | 안 움직임 | 맞음 |
| J_U7_HGT 6(위 끝) | P_M05_CST_PLATE | 245,781.931 | Z 26~334 | Z +6 | 맞음 |
| | P_M08_TUBE_BRKT_CST_O | 58,244.264 | Z 98~222 | Z +6 | 맞음 |
| | P_M08_KDM_BRKT | 124,801.279 | Z 340~748 | Z +6 | 맞음 |
| | P_M05_HOLDER | 32,632.629 | Z 291~340 | Z +6 | 맞음 |
| | P_M06_BASE | 40,595.441 | Z 126~201 | Z +6 | 맞음 |
| J_U7_HGT −4(아래 끝) | P_M05_CST_PLATE | 245,781.931 | Z 16~324 | Z −4 | 맞음 |
| | P_M08_TUBE_BRKT_CST_O | 58,244.264 | Z 88~212 | Z −4 | 맞음 |
| | P_M08_KDM_BRKT | 124,801.279 | Z 330~738 | Z −4 | 맞음 |
| | P_M05_HOLDER | 32,632.629 | Z 281~330 | Z −4 | 맞음 |
| | P_M06_BASE | 40,595.441 | Z 116~191 | Z −4 | 맞음 |
| J_U4_X 95(끝) | P_M02_BASE | 380,844.131 | X −425~−235 · Y −60~266 · Z 242~250 | X −95 | 맞음 |

- X · Y만 적은 줄의 나머지 축은 REST와 같다.
- J_U7_CST_X · CST_Y는 정비 연구 MAINT_U7의 순서(걸쇠 12 → X 25 → Y 250)로 놓았다. 걸쇠를 풀지 않고 Y만 250 보내는 자세는 실제 순서에 없다.
- P_M02_BASE의 면 수는 J_U4_X 95에서 92, 0에서 91이다. 부피 · bbox가 같아 면 나눔의 차이다(지난 검도 mech_RX-06_verify1.md 7절과 같은 값).
- 끝난 뒤 모든 조인트를 되돌려 8바디가 REST 값과 같음을 다시 쟀다.

### 4-3. 구동 시간(같은 앱 세션)

| 조인트 | 작업 전 | 작업 뒤 |
|---|---|---|
| J_U4_X | 465~574 s(mech_RX-06R_model1.md 107줄, 저장본 CLI) · 앱 10~15분 | 0.36 s |
| J_U5_X | 재지 않음(Combine43부터 다시 계산, 피처 시간 합 약 678 s) | 0.65 s |
| J_U7_HGT | 재지 않음(Extrude47부터, 피처 시간 합 약 926 s) | 0.31 s |
| `motion.play` MAINT_U7 · REST | — | 0.30~0.34 s |

## 5. 저장 전 검사

| 항목 | 결과 |
|---|---|
| 타임라인(`inspect_design`) | error 0. warning 54 → 54, 새로 생긴 것 0 · 없어진 것 0 · 글이 바뀐 것 0. suppressed 0. 이름이 Box326 · Combine41~45인 피처 없음 |
| 피처 수 | 3,717 → 3,709 (지움 22, 새로 14) |
| 숨김(E-11) | 숨긴 바디 97(MAT_S · MAT_G · MAT_V와 테이프 · 솔기 모형 — 작업 전과 같은 목록), 숨긴 occurrence 0, 조인트 771 · 스케치 304 |
| 리지드 그룹 · 안 묶인 부품(E-11) | `joint.list` floating 0, 조인트 584(RX-06R 끝의 목록과 이름 · 값 차이 0) |
| 재질(E-09) | 재질 표 742개가 v2.15.0과 같다. `matcheck.py` 불일치 2건은 작업 전부터 있던 표기 차이(P_M02 · P_M03_WHEEL_TREAD 'Urethane_A70' ↔ BOM '우레탄 A70'), BOM에 없는 P_M04_INSERT도 작업 전부터. 새 불일치 0 |
| 볼트 | 넣거나 옮긴 볼트 0. 탭 구멍의 자리 · 지름 · 깊이가 같아 볼트 검사 대상 없음 |
| 조인트 자기 점검(E-15) | J_U5_X 0 → 1380, J_U7_HGT −4 → 6, J_U4_X 0 → 95, MAINT_U7 0 → 13 모두 요청 값 = 도달 값, errors 0 · conflicts 0. 조인트 · 행정 · 스토퍼는 안 바꿈 |

### 과제 범위 겹침(`inspect.clearance`, clearance 0)

이웃은 측정 표(`tools/out/signatures.json`)의 bbox로 골랐다: 대상 바디 bbox(REST와 자세별로 옮긴 것)에서 3 mm 안.

| 자세 | 대상 × 상대 | 겹침 | unchecked | 걸린 시간 |
|---|---|---|---|---|
| REST | CAR_PLATE · CHAIN_ARM × 83 | 0 | 4 | 20.7 s |
| J_U5_X 1380 | 같음 | 0 | 4(같은 쌍) | 23.9 s |
| REST | CST_PLATE · TUBE_BRKT_CST_O · KDM_BRKT · HOLDER · M06_BASE × 137 | 0 | 14 | 228.7 s |
| J_U7_HGT 6 | 5 × 함께 안 움직이는 이웃 28 | 0 | 0 | 0.47 s |
| J_U7_HGT −4 | 5 × 28 | 0 | 0 | 0.44 s |
| MAINT_U7 13단계 | CST_PLATE · TUBE_BRKT_CST_O | 측정 표 bbox로, 옮긴 자리 3 mm 안에 함께 안 움직이는 바디 0개 | — | CAD 안 씀 |

- truncated 모두 false.
- unchecked는 "boolean Intersect: the operation failed: no result"로 겹침 부피를 못 낸 쌍이다. 모두 탭에 물린 볼트 ↔ 그 판이고(P_M03_CAR_PLATE ↔ CB5-12_M03_3 · 4 · CB5-16_M08_PY:44 · 45, P_M05_CST_PLATE ↔ CB5-12_M05_6~10 · CB5-16_M05_1:2~5, P_M05_HOLDER ↔ CB5-16_M05_1:2 · 3 · CB5-12_M08_PZ_KDM ×2) 하나는 관 ↔ 관 브래킷(TU0604_M08P_U7C_TUCK_B ↔ P_M08_TUBE_BRKT_CST_O, "empty result")이다. 볼트 쌍은 판정 기억(`tools/out/judged.json`, M-08 나사 물림)에 있는 쌍이다. 볼트는 판과 함께 움직여 자세가 바뀌어도 같은 쌍이 같은 응답을 낸다.
- **작업 전과 대조:** 같은 대상 · 같은 상대를 작업 전 저장본 v2.15.0에 저장본 CLI로 돌렸다(`verify/base_rest_clr_out.json`, REST). 겹침 0, unchecked 4쌍 · 14쌍으로 쌍 이름까지 작업 뒤와 같다(걸린 시간 26.2 s · 292.9 s). 이번 편집이 만든 새 겹침 · 새 unchecked는 0이다.

## 6. 남은 같은 꼴 — 구동 후보 RX-06-C3(작업 대상 테이프 모형)

| 컴포넌트 | 조인트 | 루트 피처 | 바디 |
|---|---|---|---|
| WP_TAPE_S | J_WP_S_X · Y · ROT | Split1 · Split2 · SPL_S_C05 · C06 (4) | TP_S_07a |
| WP_TAPE_L | J_WP_L_X · Y · ROT | SPL_L_D1 · D2_UL · C26~C35 (12) | TP_L_36a |
| WP_TAPE_G | J_WP_G_X · Y · ROT | SPL_G_D1 · D2_UL · C23~C30 (10) | TP_G_31a |
| WP_TAPE_V | J_WP_V_X · Y · ROT | SPL_V_D1 (1) | TP_V_31a |

- 매트와 함께 움직이는 테이프 모형 바디를 루트의 Split이 자른다. 매트가 움직인 자세에서 자르는 면이 제자리에 남는지, 그래서 테이프 조각 형상이 달라지는지는 이번에 재지 않았다(과제 범위 밖, 작업 대상 모형).
- 확인할 것: CYCLE 연구의 한 단계에서 TP_S_07a 등 조각의 부피가 REST와 같은지. 다르면 Split을 WP_TAPE_* 컴포넌트로 옮긴다(Split이 `move_features`로 옮겨지는지는 모름).

## 7. 저장 · 저장 확인

| 항목 | 값 |
|---|---|
| 순서 | 편집 → `component.rename {0, FSAP_v2.15.1}` → 설명 `document.metadata.set` → `motion.play REST 0` → `joint.drive J_U7_HGT 0` · `J_U4_X 0`(REST 연구에 키가 없는 조인트, RX-06-D8) → 조인트 · 스케치 숨김 → `save {path}` |
| 저장 응답 | 5,632,661 B, name FSAP_v2.15.1, path `3D_Modeling/FSAP_v2.15.1.sc` |
| 저장 뒤 앱 | name FSAP_v2.15.1, path v2.15.1, **dirty false**, 피처 3,709. 저장 뒤 편집 0 |
| v2.15.0 | 5,632,952 B · 2026-11-13 09:28 그대로(덮어쓰지 않음) |
| 저장본 대조(`document.json`, v2.15.0 ↔ v2.15.1) | 바뀐 것은 2절의 피처뿐: 컴포넌트만 바뀐 피처 8, 없어진 피처 22, 새 피처 14(base · 축 · 반지름 · 깊이가 지운 도구 원통과 같음). 남은 피처의 순서 같음. occurrence 2,918개(변환 포함) · 컴포넌트 682개 · 조인트 584개(값 포함) · 링크 35 · 동작 연구 9 · 재질 · 숨김 목록이 모두 같다 → 부품 위치 · 대기 포즈 그대로 |
| 저장본 CLI 측정(`solidcraft-cli eval --in FSAP_v2.15.1.sc`, `verify/saved_v2151_measure.json`) | 바디 3,188개, 피처 3,709, error 0, warning 54. 측정 표(서명) 3,188개와 이름이 모두 맞고, 부피(상대 1e-4) · bbox(0.05 mm) 차이가 난 바디 0개(REF_NEEDLE_AXIS_MARK 3.14135 ↔ 서명 3.141은 서명의 소수 셋째 자리 반올림). 대상 8바디 부피는 4-1 표와 같다. 열기 + 측정 약 18분(CLI 3개 동시) |
| 측정 표(서명) | `ledger.py sigpatch --parts tools/out/mech_RX-06-C2/sig_changed.json`: 바뀜 8(피처가 바뀐 8바디, 값은 같음) · 없어짐 0 · 전체 3,188. 문서 · 해시를 v2.15.1로 찍음. `sigcheck` reuse. 이 뒤 저장 안 함 |
| 다시 실행 재료(E-25) | `tools/out/mech_RX-06-C2/edit.json`(명령 29개) · `edit_meta.json` · `model/stage_1~6.json`. 생성기 `tools/gen_rx06c2.py` |
| 임시 STEP | 없음. 새로 힘을 받는 가공품 없음(형상 값 변화 0) |
| 스크린샷 | `tools/out/mech_RX-06-C2/shot_v2151_iso.png`(저장본 CLI snapshot, 700 × 500, 사람용 — 열어 보지 않음. 겉모습 변화 0) |

## 10. 시간

| 항목 | 값 |
|---|---|
| 걸린 시간 | 약 98분(예산 180분, 등급 S 예상 30분의 2배를 넘음) |
| 넘은 이유 | 타임라인 가운데를 고치는 명령 5번이 번마다 뒤를 다 다시 계산(1,040 + 640 + 880 + 1,040 s와 거부 응답 뒤 다시 보낸 것 = 약 61분), 저장본 CLI 확인 3개(작업 전 대조 21분 · 저장본 측정 18분 · 스냅샷 17분, 겹쳐 돎)를 기다린 시간 |
| 통로 | MCP(편집 · 자세 · 측정 · 저장) + 저장본 CLI 3번(읽기) |
| 파일 열기 | MCP `open` 0(이미 열려 있었음), CLI 3. 가장 긴 열기 약 1,000 s(CLI, 3개 동시) |
| 앱 막힘 · 재시작 | 없음 |

## 8. 못 한 것

없음(지시 · 완료 판정 ①~④).

| 완료 판정 | 결과 |
|---|---|
| ① 옮긴 뒤 REST에서 대상 바디 부피 · bbox 변화 0 | 만족(4-1). U7_BINDER는 지워진 바디라 해당 없음 |
| ② J_U5_X 양 끝, J_U7_CST_X · Y · J_U7_HGT 끝 자세에서 부피 같고 bbox가 강체 이동 | 만족(4-2) |
| ③ 타임라인 error 0 · 새 warning 0, Box326 · Combine41 없음 | 만족(5절) |
| ④ 과제 범위 간섭 0(옮긴 바디 ↔ 이웃, 끝 자세) | 겹침 0(5절). 볼트 물림 쌍은 부피 계산이 안 돼 unchecked로 나옴 — 형상이 같아 작업 전과 같다 |

## 9. 문서 담당에게 넘길 것

- 결정로그: RX-06-C2 결과(위 2 · 3절), 지시 방법과 달리 Combine은 지우고 Cylinder cut으로 다시 만든 것과 이유, 지시 밖 3유닛(TUBE_BRKT_CST_O · U7_FIXED · U6_SENSOR)을 함께 고친 것과 이유. RX-06-D7(빈 Combine41)은 지워서 닫힘.
- 구동 후보 RX-06-C3(6절).
- 디테일로 남는 것: RX-06-D8(REST 연구에 J_U4_X · J_U7_HGT 키 없음 — 이번에도 따로 0으로 돌렸다).
- BOM · 설계검토서: 부품 · 수량 · 형상 변화 0.

## 워크플로우 메모

- `component.move_features`는 Combine(도구 바디 cut)을 옮기지 못한다. 도구 원통을 먼저 옮겨도, 함께 옮겨도 "works on bodies that would be split between components"다. 지시서(와 mech_RX-06_verify1.md 5절)의 "거부되는 Combine은 TAP 도구 바디를 먼저 옮긴다"는 되지 않는다 → "Combine + 도구를 지우고 같은 치수의 cut 피처를 그 컴포넌트에 다시 만든다"로 바꾸면 좋겠다.
- 타임라인 가운데를 고치는 명령(옮기기 · 지우기)은 한 번마다 그 뒤를 다 다시 계산한다: 640~1,040 s. 전체 피처 시간 합 990 s 가운데 514 s가 P_M07_BEAM을 자르는 6개 피처(Cylinder1219 178.6 s, Combine40 146.5 s, Cylinder1327 78.6 s, Cylinder1283 54.7 s, Cylinder1326 36.9 s, Cylinder1291 19.8 s)다. 저장본 열기(약 15분)가 전체 피처 시간 합(16.5분)과 비슷해, 열기 시간도 이 6개가 큰 몫으로 보인다(따로 재지는 않았다) → 모델 무게를 다시 본다면 구매품 사본보다 이 6개 피처가 먼저다.
- 움직이는 컴포넌트 바디를 루트 피처가 고치면 그 조인트를 움직일 때마다 그 피처부터 다시 계산한다(J_U4_X 465~574 s → 고친 뒤 0.36 s). 지난 과제들의 자세 검사가 오래 걸린 원인이다(mech_RX-06R_model1.md 워크플로우 메모 3). 이 정적 점검(조인트 그래프 + 피처의 컴포넌트)을 엔진 도구로 두고 준비 점검 · 검도가 매번 돌리면 좋겠다. 지난 검도의 점검은 J_U7_HGT로 움직이는 유닛과 하위 컴포넌트를 놓쳤다.
- `inspect.clearance`에 함께 움직이는 탭 물림 볼트를 넣으면 겹침 부피를 못 내고(unchecked) 137개 상대에 229 s가 걸렸다. 자세 검사의 상대에서 함께 움직이는 바디를 빼니 28개 상대가 0.5 s였다.
- 실행 지시 (a) · (g)가 가리킨 문서 번호(v2.13.0)가 `tools/config.json`(v2.15.0)과 달랐다.
- MCP `batch`에 `motion.play` · `joint.list`를 넣으면 응답이 80 KB~770 KB라 파일로 떨어진다. `quiet`가 줄이지 않는다.
