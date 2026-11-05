# 모델링부 STEPSWAP r2 — CB4-25·CB6-16 실물 교체 (v2.5.8 → v2.5.9, 2026-11-05)

요약
- 저장: `3D_Modeling/FSAP_v2.5.9.sc`(마지막 자리 +1, 새로 생기거나 없어진 유닛·부품 묶음 없음). `tools/config.json` doc·`tools/machine.json` doc·유닛 부품 갱신. 통로 **MCP**(앱 running 빈 목록, 막힘 없음).
- 바꾼 것: `STEP대기_CB6-16_M03_1·_2` → `CB6-16_M03_LIFT:1·:2`(미스미 CB6-16 STEP), `STEP대기_CB4-25_M08:1~4` → `CB4-25_M08:1~4`(미스미 CB4-25 STEP). 실물 치수가 임시 형상과 같아 자리·물림 그대로(bbox 일치).
- 지시 형번의 `STEP대기_` 남은 것 0(저장 문서 바디 이름 검색).
- 과제 안 검사: CB6-16은 J_U5_LIFT −10·0·10·20·30(0~100 %) 다섯 점, CB4-25는 REST — 새 겹침 0. J_U5_X 345~1380 쓸린 상자 안 고정 바디 0(서명 bbox). floating 0.
- 저장 1차본은 다시 열면 타임라인 실패(`Remove41: unknown body`) → 그 피처를 지우고 같은 번호로 다시 저장(3절). 1차본은 `tools/out/mech_STEPSWAP/r2/cand_v259_remove41_broken.sc`로 옮김(커밋 전, 사용자 안 봄).
- 미완: 없음. 외부: 없음(두 STEP은 purchased-step·PartsLibrary에 이미 있음).
- 지난 STEPSWAP 보고서(v2.5.6)는 같은 이름이라 `mech_STEPSWAP_model_v2.5.6.md`로 옮겨 남김.

## 1. 통로·문서 확인

- `running` → 빈 목록. 열린 문서는 이름 'FSAP_v2.5.8', `path: null`, `dirty: true`, **undo 0·redo 0**(그 세션에서 편집한 것이 없음). 이름·피처 수(1,978)가 v2.5.8과 같고 파일에 묶이지 않아 dirty로 보인 것이라, 버릴 사람 편집이 없다고 판정하고 저장본 `3D_Modeling/FSAP_v2.5.8.sc`를 `open`(오류 0, 피처 1,978). 지시서 (b)의 'merged' 문서는 이미 없었다.
- `motion.play REST step 0` → `edit.checkpoint` → 그림(batch 2개, 6.1 s·22.2 s) → 검사 batch(82.6 s) → REST·조인트 글리프 숨김(규칙 19)·루트 이름 'FSAP_v2.5.9'·설명 'STEPSWAP mechanism: STEP-wait CB6-16 x2 (U5 lift top) and CB4-25 x4 (SS5Y3 base) swapped to Misumi STEP' → `save {path: v2.5.9}`.
- 기록: `tools/out/mech_STEPSWAP/edit.json`(24 명령, `r2/stage_1_cb6.json` + `r2/stage_2_cb4.json` + 끝 단계 + Remove41 삭제), `edit_meta.json`(base v2.5.8 → result v2.5.9). 지난 회차 기록은 `edit_v2.5.7.json`·`edit_meta_v2.5.7.json`으로 남김.

## 2. 바꾼 부품과 좌표(세계, REST)

볼트 STEP 틀: 로컬 +X = 나사 축, 원점 = 머리 밑면(CB6-20과 같은 미스미 SolidWorks 2016 STEP, 바디 'Cut-Extrude1').

| 새 부품 | 유닛(부모) | 자리 | bbox | 부피·질량 | 지운 임시 형상 |
|---|---|---|---|---|---|
| `CB6-16_M03_LIFT:1·:2` | U5_LIFT(로컬 = 세계 −30 Z) | 머리 밑면 Z 156(승강판 `P_M03_LIFT_TOP` 밑면), 축 +Z, X −1959·−1881, Y 72. 물림 8(MGP 끝판 M6 탭 깊이 8.46) | X −1964~−1954 / −1886~−1876, Y 67~77, Z 150~172 | 843.3 mm³, 6.62 g, SCM435 | `STEP대기_CB6-16_M03_1·_2`(바디, Remove40) |
| `CB4-25_M08:1~4` | U8_PNEU(항등) | 머리 밑면 Y 100(SS5Y3 베이스 윗면), 축 +Y, X 1039.8·1112.2 × Z 343·359. 물림 5(보 앞벽 M4) | X 1036.3~1043.3 / 1108.7~1115.7, Y 96~125, Z 339.5~346.5 / 355.5~362.5 | 448.6 mm³, 3.52 g, SCM435 | 컴포넌트 `STEP대기_CB4-25_M08`(:1~4, solid.remove + component.delete) |

- 임시 형상과 bbox가 같다(CB6-16 Z 150~172, CB4-25 Y 96~125). 부피는 실물이 육각 구멍·모따기 몫만큼 작음(923.5 → 843.3, 468.0 → 448.6).
- 부품 번호(part_number)·bom_type purchased·설명은 컴포넌트 metadata에. 조인트: 둘 다 그 유닛 컴포넌트의 하위 occurrence라 유닛을 따라 움직인다(새 조인트 없음). `joint.list` floating 0, conflicts 0.
- 지운 것 잔재: 바디·컴포넌트 0. 빈 구멍 0(같은 자리에 같은 지름).
- 조인트·행정·연구 변화 없음 → machine.json은 doc와 유닛 부품 이름만 바꿈(`STEP대기_CB6-16_M03` → `CB6-16_M03_LIFT`, `STEP대기_CB4-25_M08` → `CB4-25_M08`), `_history`에 한 줄.

## 3. 저장 확인 — 1차 저장본 실패와 고침

- 1차 저장 뒤 CLI(`solidcraft-cli run r2/verify.json --in v2.5.9 --results`)가 "1 timeline feature(s) failed … Remove41: unknown body `STEP대기_CB4-25_M08`"로 끝났다. 앱 안에서는 오류 0이었다(다시 계산 안 함).
- 원인: 임시 볼트 바디를 `solid.remove`(Remove41)한 뒤 컴포넌트를 `component.delete`하자 그 바디를 만든 피처(8914·8915)가 같이 지워져, 다시 열 때 Remove41이 지울 바디를 못 찾는다(v2.5.6 회차 실패 ②와 같은 종류).
- 고침: `timeline.dependents Remove41`(딸린 것·깨질 것 0) → `timeline.delete Remove41` → REST → 1차본을 `tools/out/mech_STEPSWAP/r2/cand_v259_remove41_broken.sc`로 옮기고 같은 경로 `3D_Modeling/FSAP_v2.5.9.sc`에 다시 저장(3,599,851 B). 1차본은 이 세션 안에서만 있었고 커밋 전이다.
- 다시 저장한 파일을 CLI로 다시 열어 확인: 4절 끝.

## 4. 검사(수치, E-16)

과제 안 검사(지시 6-1, 관련 조인트 0·25·50·75·100 %, `inspect.clearance` clearance 0.5, 전 사이클 motion.interference 돌리지 않음). 결과 원본 `tools/out/mech_STEPSWAP/r2/check_out.json`.

| 자세 | 대상 | against | 겹침 | 가까움 | unchecked |
|---|---|---|---|---|---|
| REST | CB4-25_M08 | P_M07_BEAM·SS5Y3-20-06_M08·SY3120 ×6·관 8줄·HTBO 벨트 2 | 0 | SS5Y3 0.000(머리 자리 맞닿음) | P_M07_BEAM(나사 물림, boolean 실패) |
| J_U5_LIFT −10 / 0 / 10 / 20 / 30 | CB6-16_M03_LIFT | MGPM25-40Z_M03_ROD·_BODY·P_M03_CAR_PLATE·P_M03_LIFT_TOP·P_M03_LIFT_SIDE_P | 0 | LIFT_TOP 0.000(머리 자리 맞닿음) | MGPM25-40Z_M03_ROD(끝판 탭 나사 물림) |

- unchecked 2쌍은 나사부 ↔ 탭 구멍 물림(M-08 의도 겹침, 기준선 'CB5-*·STEP대기_CB6-20_M03_* ↔ 탭 구멍 부품'과 같은 종류). 실물이 임시 형상과 같은 자리·같은 지름이라 물림 길이(8·5)도 같다.
- J_U5_X(0~1380): CB6-16은 U5 전체와 같이 움직인다. 쓸린 상자 X −1964~−496 · Y 67~77 · Z 110~172(승강 −10 포함)에 U5 밖 고정 바디 0(서명 bbox, `tools/out/signatures.json`).
- CB4-25 둘레에 움직이는 부품 없음(U8 고정, 벨트 가닥은 X −2220~−390).
- 숨김: 바디 9개(MAT·TAPE·SEAM 모형 ×3, C-31 '매트 모형 기본 숨김', 의도). occurrence 숨김 0. 조인트 글리프 숨김(규칙 19).
- 재질: 새 바디 2종 SCM435(볼트, 기존 CB6-20·CB4-20과 같음). 가공품 변화 없음 → matcheck 대상 없음.
- 볼트 검사(렌치 접근): 자리·방향이 임시 형상과 같아 이번 과제에서 새로 생긴 막힘 없음. 접근 프로브는 구동 단계 규칙상 디테일 기록(E-02) — 아래 6절.
- 강도: 새로 힘을 받는 가공품 없음 → 임시 STEP 없음, FEA 없음(D-16 환경 없음과 무관).
- 저장본 다시 열기: 4-1.

### 4-1. 저장본 확인(다시 연 파일)

`solidcraft-cli run r2/verify.json --in 3D_Modeling/FSAP_v2.5.9.sc --results`(다시 저장한 파일, 4분 54초): 타임라인 실패 0, 바디 2,641(전수 측정 목록), `CB6-16_M03_LIFT:1·:2`·`CB4-25_M08:1~4` bbox·부피가 앱 측정과 같음, 바꾸지 않은 `P_M03_LIFT_TOP`(X −1990~−1820 · Y −55~78 · Z 156~164, 179,342 mm³)·`SS5Y3-20-06_M08`이 서명과 같음, `joint.list` floating 0·conflicts 0. 바디 이름에 `STEP대기_CB4-25`·`STEP대기_CB6-16` 0. 서명은 이 파일 기준으로 sigpatch 다시(해시). 결과 `tools/out/mech_STEPSWAP/r2/verify_out.json`.

## 5. 문서

- BOM `docs/bom/FSAP_v2.5.9_purchased.csv`(CB6-16·CB4-25 행: 모델 바디 실물 STEP, 자료대기 '-'), `FSAP_v2.5.9_made.csv`(v2.5.7과 같음, v2.5.8은 BOM 그대로).
- 자료대기 D-115(CB6-16)·D-129(CB4-25)에 교체 기록.
- 결정로그 '구동 STEPSWAP r2' SW2-01. CHANGELOG [Unreleased] 한 줄.
- 서명: `ledger.py sigpatch --parts r2/changed_parts.json --removed <임시 6> --bolts r2/changed_bolts.json`(바뀜 6, 없어짐 6). `tools/out/bolts.json`의 옛 `STEP대기_CB4-25`·`STEP대기_CB6-16` 6줄은 sigpatch가 남겨 지움(워크플로우 메모).

## 6. 디테일로 남김(E-02, 수정 회차 안 씀)

- SW2-D1: CB6-16 머리(Z 150~156) 아래 육각 렌치 길(−Z), CB4-25 머리 앞(−Y, 밸브 줄 X 1044.5~1107.5 바깥) 렌치 길 프로브 확인.

## 워크플로우 메모

- STEP으로 바꿀 때 임시 바디를 `solid.remove`한 뒤 그 컴포넌트를 `component.delete`하면 Remove 피처가 다시 열 때 실패한다(앱 안에서는 오류 0으로 보임). 임시 형상이 컴포넌트째면 `component.delete`만 쓰거나, 지운 뒤 `timeline.dependents`/저장본 CLI 다시 열기로 확인해야 한다. 이번 회차와 v2.5.6 회차 두 번 반복.
- `ledger.py sigpatch --removed`는 서명 parts만 지우고 `bolts.json`의 같은 볼트 줄은 남긴다(이름이 바뀐 볼트는 두 줄이 됨).
- `inspect.clearance`에 `bodies`만 주면 against가 비어 0쌍을 잰다(목록 안 쌍만). 주변은 늘 against로 준다.
- 지시서 (b)의 dirty 'merged' 문서 설명이 실제(이름 FSAP_v2.5.8, path null, undo 0)와 달랐다.
