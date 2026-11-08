# REG-01 모델링 r4: 전체 회귀 못 본 범위 이어 보기 (FSAP_v2.6.5 그대로, 2026-11-06, 엔진 v3.9.3)

요약
- **바뀐 부품: 없음.** 형상·조인트·행정·동작 연구 변경 0, 저장 0(읽기 전용 회귀, 등급 S). 대상 `3D_Modeling/FSAP_v2.6.5.sc`(LITE 저장본, config.json doc 그대로).
- **본 범위(regrun 2개 동시, 각 상한 30분):** CYCLE_G1 129~391·393~394·397~398·401·405(269단계) + STATES 33·34 + POSE 8~39(34점) = 303점.
- **연구(CYCLE_G1) 269단계: 기준선 밖 겹침 0**, truncated 0, unmoved 0, stopped 0, U7_BINDER 오염 0.
- **자세 34점: 기준선 밖 겹침 1** — **POSE 8**(J_U6_HGT +6, J_U7_HGT −4, J_U6_SHIFT 0, 노루발 20, 바늘 0)에서 `P_M05_GUIDE ↔ P_M06_CARR` 291.7 mm³(상자 X 12~18, Y −107~−100, Z 34~42). 같은 자세에 `P_M05_GUIDE ↔ E32-D36P1_2M_M06`는 판정 못 함(boolean 실패). truncated·unmoved·stopped 0.
- POSE 8은 machine.json의 "두 조인트(J_U6_HGT·J_U7_HGT)는 같은 값" 밖의 **맞춤 잘못 자세**(10 mm 어긋남)다. 정의 밖 자세로 칠지, 설계로 막을지는 규칙 예외라 스스로 정하지 않고 올린다(E-14, 아래 6절).
- **못 본 범위:** CYCLE_G1 392·395~396·399~400·402~404·406~514(117), CYCLE_G2 0~630(631), MAINT_U7 9(1), POSE 40~181 중 새 자세 135점, F_STATES 0~34(35).
- 미완: 완료 판정 "못 본 범위 기준선 밖 겹침 0"은 아님 — POSE 8 겹침 1과 위 못 본 범위.

## 근거 규칙
- E-03 "라운드 끝 = 전체 사이클 간섭 0". E-17 전체 회귀 실행 절차 "어림 합이 전체 상한을 넘으면 시작 전에 앞 묶음부터 상한 안에 드는 만큼만 돌리고 나머지는 못 본 범위로 정한다".
- 요구서 6-4 "전체 회귀 상한 30분", 호출 상한 8분(E-04). 선정 지시서 "구상·수정 회차 없이 회귀 실행만 한다 … 남은 범위는 다음 회귀로 넘긴다".
- E-14 규칙 예외는 스스로 주지 않고 올린다.
- 실행 규칙 3 "형상이 바뀌면 항상 새 번호로 저장" — 형상 변경이 없어 저장하지 않았다(version_bump none, v2.6.6 만들지 않음).

## 1. 문서 확인·통로
- MCP `running` 빈 목록(막힘 없음). `inspect_design`: 이름 `FSAP_v2.6.4`, **dirty true, path null**, revision 635, undo 0 — LITE 때와 같은 상태다. 안내서 '문서 확인' "dirty면 open 전에 멈추고 보고한다 … 버리지 않는다"에 따라 앱 문서는 열지도 바꾸지도 않았다. **앱에 열린 FSAP_v2.6.4(dirty, path null)는 사람이 확인해야 한다.**
- 회귀는 실행 규칙 2 "오래 걸리는 동작 간섭 검사는 앱(MCP)에서 돌리지 않는다"대로 CLI 헤드리스 세션으로 했다. 다른 부서의 solidcraft-cli 프로세스는 건드리지 않았다.
- 원복·동작 상태 초기화: 앱 편집이 없어 원복 대상 없음. 헤드리스 세션은 단계마다 `motion.play`(REST 또는 연구 단계)로 시작한다.

## 2. 방법
- 폴더 `tools/out/mech_REG-01/r4/`. `worker.py`·`chunk7.py`(J_U6_HGT·J_U7_HGT·J_U6_SHIFT 0 초기화 포함)·`ask.py`·`sets.json`·`states.json`·`poses.json`·`an.py`는 r3 그대로(경로만 r4).
- 헤드리스 세션 12개가 v2.6.5를 한 번씩 열었다(동시 열기 295~353 s): 연구 39901~39908(8), 자세 39911~39914(4, 연구와 나눔, WF-183).
- `sets.json`: LITE로 바뀐 `P_M07_BEAM`은 `near_red`·`near_all`에 있고, 움직이는 115바디 전체 검사에도 들어 있어 연구 단계마다 둘레를 본다(바뀐 바디 둘레). `P_DC205_STRIP`은 bbox 변화 0(밑면 탭 구멍만, mech_LITE_verify.md).
- 명세: `specA.json` CYCLE_G1 129~514 → CYCLE_G2 0~630 → MAINT_U7 9. `specB.json` STATES 33~34 → POSE 새 자세 167점(`../measure_remaining_plan.json` pose_new, 같은 자세 8점 뺌, E-19) → F_STATES 0~34.
- regrun: `--call-limit 480 --total-limit 1800 --trial-steps 4 --trial-limit 360 --trial-poses 1`, A 8병렬·B 4병렬 동시. 실행 `run.sh`, 기록 `run_log.txt`, 결과 `runsA/regrun.json`·`runsB/regrun.json`, 모음 `an_runsA.json`·`an_runsB.json`.

## 3. 결과

| 범위 | 본 점 | 기준선 밖 겹침 | truncated | unmoved·stopped |
|---|---|---|---|---|
| CYCLE_G1 129~391·393~394·397~398·401·405 | 269 | 0 | 0 | 0 |
| STATES 33·34 | 2 | 0 | 0 | 0 |
| POSE 8 | 1 | **1** | 0 | 0 |
| POSE 9~39 | 31 | 0 | 0 | 0 |

- regrun A: status partial, 어림 6,656 s > 1,800 s → 앞 274단계 계획, 실제 1,801.7 s, killed 0, skipped 0. 본 269단계(상한에 걸린 7단계는 못 본 범위). 실측 약 52.5 s/단계(8병렬).
- regrun B: status partial, 어림 10,914 s(시험 215 s/점) > 1,800 s → 앞 33점 계획(시험 1점 더해 34), 실제 1,096 s, killed 0. 첫 점은 182~369 s, 그 뒤는 44~53 s/점(4병렬 약 12 s/점).
- 기준선(M-08)에 든 것만 걸림(연구): `MAT_G ↔ TAPE_G` 269회, `U3_NEEDLE_PIN ↔ MAT_G·TAPE_G` 각 234회.
- 못 잰 쌍(기존, 나사·핀 물림 의도): `I-020B_M02 ↔ CDM2C20-25Z_ROD`·`_NUT`, `KDM10P-06_M08 ↔ KDM10S-06_M08`. 새로 `P_M05_GUIDE ↔ E32-D36P1_2M_M06`(POSE 8 한 점, boolean 실패).
- 손 조정 조인트 오염: 묶음 첫 단계 U7_BINDER 상자 104곳(연구 70·자세 34) 모두 그 단계 값대로, 넘어옴 0.

### POSE 8 겹침
- 자세: `J_U6_SHIFT 0, J_U6_HGT +6, J_U7_HGT −4, J_U3_PRESSER 20, J_U3_NEEDLE 0`(나머지 REST).
- 겹침: `P_M05_GUIDE`(U7 카세트 안내) ↔ `P_M06_CARR`(U6 캐리지), 291.7 mm³, X 12~18 · Y −107~−100 · Z 34~42. U6을 6 올리고 U7을 4 내려 둘이 10 mm 엇갈린 자세다. 반대 엇갈림 POSE 9(U6 −4, U7 +6, SHIFT −60)는 겹침 0.
- machine.json J_U6_HGT·J_U7_HGT 원문: "값 = 매트 두께 - 10, 두 조인트(J_U6_HGT·J_U7_HGT)는 같은 값, 기계 축 아님". POSE 8·9만 두 값이 다른 자세다(183점 중 2점).
- 이번 과제는 회귀만이라 형상을 고치지 않았다(선정 지시서). 판정은 기계적으로 bad 1이다.

## 4. 못 본 범위(다음 회귀가 먼저 본다)

| 범위 | 단계·점 | 이유 |
|---|---|---|
| CYCLE_G1 392·395~396·399~400·402~404·406 | 9 | 전체 상한 |
| CYCLE_G1 407~514 | 108 | 어림 초과(시작 전) |
| CYCLE_G2 0~630 | 631 | 어림 초과(시작 전) |
| MAINT_U7 9 | 1 | 어림 초과(시작 전) |
| POSE 40~181 새 자세 | 135 | 어림 초과(시작 전) |
| F_STATES 0~34 | 35 | 어림 초과(시작 전) |

- 누계(v2.6.3~v2.6.5): CYCLE_L 0~716, CYCLE_S 0~450, CYCLE_G1 0~391(일부 빠짐)·393~394·397~398·401·405, STATES 0~25·31~34, MAINT_HEAD 0~1, MAINT_U7 0·3·4·7·8·12·13, POSE 0~39 — POSE 8 말고 기준선 밖 겹침 0. 이미 STATES로 본 연구 단계(CYCLE_G1 467, CYCLE_G2 75·315·574·630)는 measure_remaining_plan.json에 있다.
- 어림: 남은 연구 약 757단계 ≈ 52.5 s × 757 / 8 ≈ 83분(30분 회귀 3번), 자세 170점 ≈ 12 s/점(4병렬 정상 상태) ≈ 34분 + 세션 첫 점. 자세 쪽은 이번 실측이면 회귀 1~2번에 끝난다.

## 5. 저장·기록
- 저장 없음(형상 안 바뀜, version_bump none). config.json·machine.json·signatures.json 그대로 — sigpatch 대상 없음. 커밋 없음(실행 규칙 4: 새 버전 .sc를 저장했을 때만).
- `tools/out/mech_REG-01/edit.json` = `[]`, `edit_meta.json` = {base·result: v2.6.5}. r3 기록은 `r3_keep/edit_v2.6.4.json`·`edit_meta_v2.6.4.json`, r3 보고서는 `mech_REG-01_model_v2.6.4.md`.
- 해석: 새로 힘을 받는 가공품 없음 → 임시 STEP 없음.
- 스크린샷: 형상 변경이 없어 찍지 않았다.

## 6. 규칙 예외 요청(E-14)
- 규칙: REG-01 완료 판정 "못 본 범위 기준선 밖 겹침 0", M-08 기준선.
- 자리: POSE 8, `P_M05_GUIDE ↔ P_M06_CARR` 291.7 mm³.
- 근거: machine.json에서 두 손 조정 조인트는 "같은 값"으로 정의돼 있고, POSE 8은 그 정의 밖의 10 mm 어긋남 자세다. 같은 값 자세(POSE 0~7·10~39)는 모두 겹침 0.
- 안: (가) 두 HGT 값이 다른 자세(POSE 8·9)를 정의 밖으로 보고 회귀 자세 목록에서 뺀다(기록만), 또는 (나) 엇갈림을 실제로 막는 구동 후보를 만든다(U6·U7 높이를 한 판·한 조정으로 묶기, 또는 GUIDE↔CARR 사이 틈 키우기). 사용자 또는 선정부가 정한다.

## 워크플로우 메모
- regrun 자세 어림이 세션 첫 점(열기 직후 182~369 s)을 per_step으로 써서 정상 상태(44~53 s/점)의 4~5배로 잡았다. 자세 쪽 30분 상한에 1,096 s만 쓰고 끝났다 — 시험 점을 2점째로 재거나 첫 점을 빼면 한 번에 더 본다.
- run.sh 끝의 worker `quit` 보내기가 끝나지 않아(5분 넘게) 이 과제의 worker python 12개와 그 headless solidcraft-cli 12개만 PID로 골라 멈췄다. 다른 부서 solidcraft-cli(42608·46988)는 그대로 둠.
- 앱 문서 FSAP_v2.6.4 dirty(path null)가 LITE부터 그대로 남아 있다. 모델링부가 MCP로 열 수 없는 상태가 이어진다.
