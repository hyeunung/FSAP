# RX-12-C3 모델링 보고서 — 수정 1회차 (v2.21.0 → v2.21.1)

## 요약

- 바꾼 것: 연구 CYCLE_W2의 키 한 줄뿐. `J_WP_W_X` 끝 `[478, 0] → [585, 0]`을 `[478, 0] → [572, 0] → [573, −15] → [585, −15]`로(결정로그 RX-12-C3-X1 지시 그대로). 매트를 몸통 쪽 −X로 15 뺀 뒤 −Y 300으로 꺼낸다.
- 기계 부품 · 볼트 · 구매품 · 조인트 정의 · 형상 변경 0. 바디 3,236 · 조인트 623 · 연구 14개 그대로. 저장본 대조: 바디 bbox 차 최대 0, 부피 합 같음, joint.list 같음.
- 결과: CYCLE_W2 573~585 전 단계에서 조각 44 + SEAM_W + MAT_W ↔ 54바디 겹침 0 · 1.5 mm 안 쌍 0(truncated false, unchecked 0). 574 · 575의 SEAM_W ↔ 바인더 턱 벽 6.25 · 1.0 mm³가 없어졌다.
- CYCLE_W2 전 구간 간섭(저장본 CLI, 5묶음 모두 truncated false): U7_KIT ↔ WP_TAPE_W가 95~114(기준선 27)만 남음(지난 회차 95~114 + 574~575). 나머지 쌍 · 구간은 v2.21.0과 같다.
- CYCLE_W1은 키가 안 바뀌어 지난 결과 그대로(E-17, 다시 돌리지 않음).
- 기준선(machine.json baseline_overlaps)에 SEAM_* ↔ 바인더 줄을 넣지 않았다(RX-12-C3-X1 · X2 기각).
- 미완: 없음. CYCLE_L 705 · 706의 SEAM_L ↔ 턱 벽은 이 과제 범위 밖(RX-12-C3-X2 → RX-18).
- 통로: MCP(열기 · 다른 이름 저장 · 키 고침 · 자기 점검 · 저장) + CLI(저장 확인 · 전 구간 간섭 · 배출 14단계).

## 근거 규칙

- E-03 "작업 대상·떨어진 조각·이웃 유닛과 겹치지 않고, 빠져야 할 것이 실제로 빠져나간다" — 배출 단계의 이음매 겹 ↔ 턱 벽 겹침을 0으로.
- M-08 "정상 겹침: 볼트 나사부의 탭 물림(채움률 < 0.5), 구매처 CAD끼리의 미세 겹침, 설계상 압입" — 작업 대상 ↔ 기계 부품 겹침은 여기 들지 않아 기준선에 넣지 않음(PM 판정 RX-12-C3-X1 기각).
- E-05 · WF-179: 앞 파일을 덮어쓰지 않고 마지막 자리 +1 새 파일(v2.21.1). E-15: 움직임은 기계 정의의 조인트 키로만.
- 요구서 0-8-4 ⑥ "노루발·바퀴·슈 들기, 작업자가 꺼냄" — 배출은 기계 축이 아니라 작업자 손. −Y 300은 임시 자세(자료대기 D-106), 턱 벽 안쪽 면 X 8.0은 임시 형상(D-211).

## 한 일

| 순서 | 내용 | 결과 |
|---|---|---|
| 1 | MCP `open` v2.21.0 → `inspect_design` | 오류 0 · 피처 3,618 · dirty false |
| 2 | `save {path: FSAP_v2.21.1.sc}`(다른 이름 저장), tools/config.json doc 바꿈 | 문서 이름 FSAP_v2.21.1 |
| 3 | `edit.checkpoint` → `motion.study` CYCLE_W2(585단계 · 키 75줄, J_WP_W_X만 바꿈) | ok, keys 75 |
| 4 | `motion.list` 전후 대조(연구 14개) | 바뀐 줄 = CYCLE_W2 J_WP_W_X 하나 |
| 5 | 자기 점검(앱): W2 572 · 573 · 574 · 575 · 576 · 580 · 585에서 `inspect.clearance`(1.5) | 아래 표 |
| 6 | REST step 0 · 조각 · 조인트 · 스케치 숨김 · 설명 → `save {path: v2.21.1}` | 64,706,693 바이트 |
| 7 | 저장본 CLI: 저장 확인 · CYCLE_W2 전 구간 `motion.interference` · 572~585 14단계 | 아래 |
| 8 | machine.json · 서명 표(`ledger.py sigpatch`, 바뀜 0 · 문서 해시만) · edit.json | |

생성기: `tools/gen_rx12c3_fix1.py`(입력 `tools/out/mech_RX-12-C3/model/motion_list_after.json`, 출력 `tools/out/mech_RX-12-C3/model1/`).

## 키(바뀐 것)

| 연구 | 조인트 | 앞(v2.21.0) | 뒤(v2.21.1) |
|---|---|---|---|
| CYCLE_W2 | J_WP_W_X | … [478, 0] → [585, 0] | … [478, 0] → [572, 0] → [573, −15] → [585, −15] |

- J_WP_W_Y는 그대로([514, 330] → [573, 330] → [585, 30]). 572 → 573은 X만 움직이는 단계다(같은 단계에 J_U5_X가 대기 0으로 들어옴 — 바퀴는 들린 상태).
- 단계 수 585 그대로. 한 단계 이동 최대 25 mm(−Y) · 15 mm(−X) — 요구서 6-4 간격 안.

## 검증 수치

자기 점검(앱, `model1/selfcheck_summary.json`)과 저장본 CLI(`model1/cli/eject_summary.json`)가 같은 값이다. 대상 = 조각 44 + SEAM_W + MAT_W(46바디), 상대 = 지난 회차 574단계 검사와 같은 54바디.

| 단계 | SEAM_W X | SEAM_W Y | 겹침 | 1.5 mm 안 쌍 |
|---|---|---|---|---|
| 572 | −3.5~8.5 | 0~30 | TL_FEED ↔ TP_W_01a 150.0 mm³(기준선 19, v2.21.0과 같음) | TL_FEED ↔ MAT_W 0 · TP_W_01a ↔ 바인더 0.5 · TL_FEED ↔ SEAM_W 1.5 |
| 573 | −18.5~−6.5 | 0~30 | 0 | 0 |
| 574 | −18.5~−6.5 | −25~5 | 0 | 0 |
| 575 | −18.5~−6.5 | −50~−20 | 0 | 0 |
| 576~585(저장본 10단계 모두) | −18.5~−6.5 | … −300~−270 | 0 | 0 |

- truncated false · unchecked 0(전 단계).
- 이음매 겹 바깥면 X 8.5 → −6.5: 턱 벽 안쪽 면 X 8.0과 틈 14.5. 조각 바깥면 X 7.5 → −7.5.

CYCLE_W2 전 구간 `motion.interference`(저장본 CLI, 586표본, `model1/cli/mi_summary.json`, 252 s):

| 묶음 | 쌍 | truncated | v2.21.0과 다른 것 |
|---|---|---|---|
| A1(U3 · U4) | 74 | false | 없음 |
| A2a(U5_WHEEL_F) | 2 | false | 없음(겹침 0) |
| A2b(U5 나머지) | 68 | false | 없음(겹침 0) |
| A3(U7 · 테이블) | 40 | false | U7_KIT ↔ WP_TAPE_W: 95~114 + 574~575 → **95~114**(기준선 27만). U7_TAPE_FEED ↔ WP_TAPE_W: 19~115 + 513~585 → 19~115 + 513~572(기준선 19, 테이프끼리 — 573부터 매트가 빠져 끝남) |
| B | 13 | false | 없음(겹침 0) |

저장 확인(`model1/cli/savecheck_summary.json`): 바디 3,236, v2.21.0 저장본과 bbox 차 최대 0 · 움직인 바디 0, 부피 합 366,505,096.4 mm³ 같음, joint.list 같음(623), 연구 차이 = CYCLE_W2 J_WP_W_X 한 줄. 타임라인 오류 0(열 때 errors 0).

REST 자세 확인: SEAM_W X −3.5~8.5 · Y −330~−300 · Z 11~12, TP_W_17a X −493.667~−383.5 · Y −560~−549(지시서 값과 같음).

## machine.json(`model1/machine_changes.json`)

- doc → FSAP_v2.21.1.sc
- studies.CYCLE_W2 `_note` ⑥: '⑥ 매트를 몸통 쪽 -X 15로 뺌(J_WP_W_X 572 = 0 → 573 = -15) 573 · ⑥ 배출(-X 15 → -Y 300, D-106) 574~585', `_keys_WP_W_eject` 한 줄 더함
- states '오목 매트 배출(끝)'(CYCLE_W2 585): J_WP_W_X 0 → −15, phase '⑥ 배출(-X 15 → -Y 300, D-106)'
- temp_values D-106에 새 배출 자세, `_history` 한 줄
- joints · baseline_overlaps 변화 0

## 문서 담당에게(PM 판정 지시)

- 설계검토서 6절 작업 순서: '⑥ 매트를 몸통 쪽으로 15 mm 이상 빼고 당겨 꺼낸다(그대로 −Y로 당기면 이음매 두 겹이 턱 벽을 0.5 스침, 임시 D-211 · D-04)'.
- 자료대기 D-106 쓰는 곳에 새 배출 자세. 요구서 7절 기록 한 줄(배출 때 −X로 빼지 않고 당기면 걸리는지, 이음매 두 겹이 바인더 입을 지나는지 D-211 — 기준선 아님).
- 요구서 5절 RX-18 내용 칸 끝에 '배출 단계 이음매 겹 ↔ 바인더 턱 벽(결정로그 RX-12-C3-X2)'. 결정로그 RX-12-C3-X3 기록(봉제 중 501~514 두 겹이 턱 안을 지날 때 손계산 0.5 모자람 — RX-18 · D-211).

## 못 한 것 · 범위 밖

- 못 한 것 없음.
- 범위 밖(알려진 항목): CYCLE_L 705 · 706 SEAM_L ↔ 턱 벽(6.25 · 1.0 mm³), CYCLE_S · G2 · V 배출 단계는 재지 않음 — RX-18(결정로그 RX-12-C3-X2).
- 스크린샷: 찍지 않았다(형상 변화 0, 저장 상태에서 조각 숨김).
- 임시 STEP · FEA: 대상 없음(힘 받는 가공품 변화 0).

## 파일

- 저장본 `3D_Modeling/FSAP_v2.21.1.sc`, 생성기 `tools/gen_rx12c3_fix1.py`
- `tools/out/mech_RX-12-C3/model1/`: study_CYCLE_W2.json · stage_9_finish.json · study_diff_actual.json · selfcheck_summary.json · machine_changes.json · cli/(mi_summary · eject_summary · savecheck_summary)
- `tools/out/mech_RX-12-C3/edit.json`(지난 회차 182명령 + 이번 6명령, base v2.20.4) · `edit_meta.json`. 지난 회차 것은 edit_round0.json

## 워크플로우 메모

- MCP `batch {path}`는 서버가 허용한 폴더(3D_Modeling · 복구 폴더 · 임시 폴더)만 읽는다. tools/out 아래 명령 파일은 거부돼 지난 회차의 `model/mcp_send.py`(앱에 붙는 MCP 서버를 `--allow-path workspace`로 따로 띄움)로 보냈다.
- 이번 저장본 CLI 열기 + 검사는 151~252 s였다(3개 병렬). 실행 안내의 13~27분보다 짧다.
- `inspect_design`은 timeline · bodies · joints · sketches를 다 꺼도 defects · sketches 요약으로 137 KB가 돌아온다.
- 시간: 약 17분(예산 120분). CAD 호출 MCP 9 · CLI 3, 파일 열기 4(MCP 1 + CLI 3).
