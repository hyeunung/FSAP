# STEPSWAP 모델링 — HNTT8-5 실물 교체 (v0.8.2 → v0.8.3, 엔진 v3.4.0)

요약
- 바뀐 부품: `STEP대기_HNTT8-5_T08_1~8` 지움 → 실물 STEP `HNTT8-5_T08_1~8` 넣음(MAT_X 아래, 각자 컴포넌트, Steel).
- 좌표: X ±145·±215, Y −957(460_F)·223(460_B), Z −555.5~−546.5(17×17×9, 1,896.0 mm³/개, 14.88 g).
- 검증: 새 겹침 0(이웃 9바디, 대기·X −620·X 620/Y 40), 460 턱 안면 Z −552.5 맞닿음 0.0, floating 0, 재질 Steel.
- 물림: CB5-20_T08_XN 끝 Z −547 → 물림 8.5 ≥ 1.5d 7.5(T08-S05 풀림).
- HNTT8-5 `STEP대기_` 0. 모델 전체 `STEP대기_` 99 → 91.
- 문서 이름(루트 컴포넌트) 'FSAP_v0.6.15' → 'FSAP_v0.8.3'(실행 규칙 2).
- 조인트·행정·연구 변경 0. 새 하중 가공품 0 → 임시 STEP 없음.
- 통로 MCP(앱 켜짐, `running` 빈 큐 응답). 저장 확인은 CLI `run --results` 1회(저장 뒤 앱 편집 없음).
- 미완 없음.

## 1. 근거 규칙
- E-10 "STEP을 못 받으면 `STEP대기_<형번>` 임시 형상" → 받은 뒤 실물로 바꾼다(선정 지시서 mech_step_wait.md).
- E-05·요구서 8-2: 새 번호 `3D_Modeling/FSAP_v0.8.3.sc`로 저장, `tools/config.json` doc 갱신.
- M-01 나사 물림 1.5d: M5 → 7.5.
- 실행 규칙 2 "저장 전에 문서 이름(앱 제목)을 새 버전 이름으로 바꾼다" → `component.rename {root → FSAP_v0.8.3}`.

## 2. 배치 (STEPSWAP-M01)
- STEP: `purchased-step/HNTT8-5/HNTT8-5.stp`(stepcheck '있음'), 바디 이름 `Tap1` → 컴포넌트 이름으로 바꿈.
- 규칙: `tools/gen_t18_mech.py` tnut()와 같음 — 로컬 Y = 바깥 법선, 원점 = 형재 겉면 − 2.5·법선.
- 460 밑면 Z −558(460_F bbox 실측) → 원점 Z −555.5. 행렬 [1,0,0,x; 0,0,1,y; 0,−1,0,−555.5].
- 임시 형상(Z −552.5~−547.5)과 비교: 실물은 어깨(목 3)가 홈 입구에 들어가 밑으로 3 더 내려오고, 위로 1 더 올라간다(−546.5).

| 바디 | bbox min | bbox max |
|---|---|---|
| HNTT8-5_T08_1 | (−223.5, −965.5, −555.5) | (−206.5, −948.5, −546.5) |
| HNTT8-5_T08_2 | (−153.5, −965.5, −555.5) | (−136.5, −948.5, −546.5) |
| HNTT8-5_T08_3 | (136.5, −965.5, −555.5) | (153.5, −948.5, −546.5) |
| HNTT8-5_T08_4 | (206.5, −965.5, −555.5) | (223.5, −948.5, −546.5) |
| HNTT8-5_T08_5 | (−223.5, 214.5, −555.5) | (−206.5, 231.5, −546.5) |
| HNTT8-5_T08_6 | (−153.5, 214.5, −555.5) | (−136.5, 231.5, −546.5) |
| HNTT8-5_T08_7 | (136.5, 214.5, −555.5) | (153.5, 231.5, −546.5) |
| HNTT8-5_T08_8 | (206.5, 214.5, −555.5) | (223.5, 231.5, −546.5) |

(저장본 v0.8.3을 CLI로 다시 읽은 값, 대기 포즈)

## 3. 검증 (수치, E-16)
- `inspect.clearance` 새 너트 8 × 이웃 9(460_F·B, 캡 HFC8-4080-B ×4, P_T08_XPLATE_F·B, HNTT8-5_T18_YMB_3 — 서명 bbox 10 mm 안): 겹침 0, 판정 불가 0. 맞닿음 8쌍(460 턱 안면 Z −552.5, 거리 0.0).
- 볼트 짝 CB5-20_T08_XN ↔ 너트: 나사 물림 자리라 불리언 판정 제외(지시 '나사 물림 제외'). 손계산 물림 8.5(Z −555.5 ~ −547) ≥ 7.5. 볼트 끝은 너트 윗면 −546.5보다 0.5 아래.
- 조인트 자기 점검: `J_MAT_X` −620 → 너트 1 X −843.5~−826.5(Δ −620), +620 → 396.5~413.5(Δ +620), 너트 8도 같음. `J_MAT_Y` 40에서 너트 안 움직임(MAT_X 아래 단이라 맞음). 그 자세에서 겹침 0.
- 행정 끝: −620·620 = 조인트 한계(스토퍼, 기존 그대로).
- 너트는 460 단면 안(홈 속)에 들어 있어 다른 유닛과 만날 수 있는 것은 460이 먼저 만난다 → 전 구간 새 겹침 0은 460의 기존 판정으로 이어진다. 전 사이클 `motion.interference`는 돌리지 않음(지시 6-1, 실행 규칙 2).
- `joint.list`: floating 0, conflicts 0. 새 너트는 MAT_X 하위 컴포넌트라 MAT_X를 따른다.
- 재질: 8개 모두 Steel(T18 HNTT8-5와 같음). 숨김 바디 없음.
- 저장 뒤 확인: CLI `run verify_saved.json --in FSAP_v0.8.3.sc --results`(3분 34초) — 바디 387(변경 전과 같음), `STEP대기_HNTT8-5` 0, 메타 설명 새 것.
- 서명: `ledger.py sigpatch` 바뀜 8·없어짐 8·전체 387, doc v0.8.3, doc_hash 찍힘.

## 4. 저장
- `3D_Modeling/FSAP_v0.8.3.sc`(14,172,459 B), 설명 'STEPSWAP mechanism: T08 T-nuts STEP-pending HNTT8-5 x8 replaced by MISUMI STEP (460 bottom slot Z-555.5)'.
- 순서: open v0.8.2 → `edit.checkpoint`(13) → 너트 1 시험 → 7개 묶음 → 검사 → `motion.play 대기 0` → 루트 이름 → `save {path}`. 저장 뒤 편집 없음.
- 열 때 dirty 확인은 `inspect_design` 대신 `document.metadata`(설명이 v0.8.2 T14 그대로)와 open 결과(errors 0)로 봄 — 1670 피처 전체 inspect는 응답이 너무 커서.
- 스크린샷: `tools/out/mech_STEPSWAP/v083_iso.png`(CLI snapshot, 열지 않음).

## 5. 바꾼 문서
- `tools/config.json` doc → v0.8.3
- BOM `docs/bom/FSAP_v0.8.3_made.csv`(v0.8.2와 같음)·`_purchased.csv`(HNTT8-5 행 모델 바디·비고)
- 자료대기 D-41에 STEPSWAP 기록, 결정로그 STEPSWAP-M01·M02, CHANGELOG v0.8.3
- 생성기 `tools/gen_stepswap_mech.py` → `tools/out/mech_STEPSWAP/edit.json`(45단계), `edit_meta.json`

## 6. 못 한 것
- 없음. 남은 `STEP대기_` 91개는 다른 형번(구매부가 받을 16종, 형번 미정 SEWHEAD·NEEDLE D-10)이라 이 과제 범위 밖.

## 워크플로우 메모
- `inspect.clearance`에 `bodies`만 주면 그 안의 쌍만 잰다(pairs_checked 0). 이웃과 재려면 `against`를 줘야 한다. 안내서 '간섭' 절에 적어 둘 만함.
- `inspect.measure {body}`를 CLI `run --results`로 부르면 body 인자가 무시되고 전 바디를 잰다(결과 2.8 MB). 저장본 바디 목록 확인에는 오히려 쓸모 있었다.
- 큰 설계에서 `inspect_design`(measure·sketches·joints false여도)은 응답이 커서 dirty 확인용으로 무겁다. `document.revision`·`document.metadata`로 대신했다.
