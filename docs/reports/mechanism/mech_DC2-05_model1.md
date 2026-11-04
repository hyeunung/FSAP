# 모델링부 — DC2-05 먼 쪽 바퀴 밑 받침, 수정 1회차 (2026-11-04, 동시 과제 E-25, CLI)

요약
- 지적: 누름판 P_DC205_DISC(SUS304 t4 Ø50)가 CB5-12 표준 조임 4.5 N·m(예압 4,500 N)에서 항복(SF 0.53, 판 계수 k 2.2로 0.33).
- 고친 것: 형상은 그대로. 볼트 컴포넌트 `CB5-12_DC205`(8 occurrence) 메타데이터에 조임 토크 **0.6 N·m**(예압 약 600 N), **중강도 나사 고정제(Loctite 243 상당)**, "표준 4.5 N·m 금지"를 적었다(description·properties). 같은 내용을 체결 기록 `changed_bolts.json`(torque_Nm 0.6, preload_N 600, threadlocker)과 결정 조각 `tools/out/DC2-05/docs/model.md` DC2-05-M3에 남김. BOM·도면 비고는 합치기 뒤 문서 단계가 이 메타데이터로 옮긴다.
- 기록 `tools/out/DC2-05/edit.json` 69단계 중 바뀐 단계는 59(`component.metadata.set`) 하나. 생성기 `tools/gen_dc2_05.py`도 같이 고침(`--bolt-body "CB5-12_M02_1 (2)"`로 돌림).
- 후보 `tools/out/DC2-05/cand.sc`를 base.sc에서 다시 만듦(5분 32초). 새 바디 17개 측정이 수정 전 후보와 같음 → replay_ok.
- 손계산(예압 비례): 누름판 σ 386×600/4500 = 51.5 MPa(k 2.2: 82.5) → SF 3.98(2.48) ≥ 1.2. A5052 탭 조임 전단 SF 1.19×4500/600 ≈ 8.9(검증부 최소 5.38 이상과 맞음).
- 미완: 없음. 해석은 환경 없음(D-16), 형상이 안 바뀌어 임시 STEP은 앞 회차 것이 그대로 유효.

## 근거 규칙 (원문)
- 지시문: "문제마다 원인을 고치고(형상·위치·행정·볼트), 다른 부분은 건드리지 않는다." → 원인은 조임력이므로 볼트 조임 지정만 바꾸고 형상·다른 부품은 그대로 둠.
- 검증 지적 fix: "형상은 그대로 두고 CB5-12_DC205 조임 토크를 0.6 N·m로 지정하고 중강도 나사 고정제를 쓴다 … 도면·BOM 비고에 적는다." → 그대로 따름.
- E-25(지시문): "설계 요구서·결정로그·BOM·config.json·git은 건드리지 않는다(합치기 뒤 한 번에)." → BOM 비고는 직접 쓰지 않고 모델 메타데이터·결정 조각에 둠.
- E-09 이름·재질: 바뀐 것 없음(CB5-12, SCM435, bom_type purchased 유지).

## 1. 바뀐 것
| 대상 | 전 | 후 |
|---|---|---|
| `CB5-12_DC205` description | "Misumi CB5-12 STEP (copied from CB5-12_M02_1), DC2-05 strip clamp" | 위 + ". Tightening torque 0.6 N*m (not standard 4.5), medium-strength threadlocker" |
| `CB5-12_DC205` properties | 없음 | 조임토크 "0.6 N·m (표준 4.5 N·m 금지, 예압 약 600 N)", 나사고정제 "중강도 (Loctite 243 상당)", 근거 "DC2-05 수정 1회차 …" |
| 형상·좌표·재질·조인트 | — | 바뀜 없음 (P_DC205_STRIP X −1,826~−391 · Y ±25 · Z −11.8~0, DISC ×8 Z −16~−12, CB5-12 ×8 머리 Z −21~−16) |

- 0.6 N·m 근거: 예압 F ≈ T/(K·d) = 0.6/(0.2×0.005) = 600 N. 바퀴 누름 약 90 N은 띠를 W2에 미는 방향이라 볼트는 띠 위치만 잡으면 되고, 600 N으로 충분(띠가 들리는 하중 없음). 풀림은 나사 고정제로 막는다.
- 대안 t6 누름판은 머리 밑 길이가 늘어 CB5-15가 필요(stepcheck 미보유)해 택하지 않음.

## 2. 검사 (수치)
- 다시 실행: `solidcraft-cli run edit.json --in base.sc --save cand.sc` 성공(work/run_r1_*.txt).
- 비교 스크립트 `work/cmp_r1.json`(motion.play REST 0 → component.metadata → inspect.measure 새 바디 17 → assembly.bom)을 수정 전 후보 `work/cand_r0.sc`와 새 `cand.sc`에 돌림: 결과 0(포즈)·2(측정 17 바디) 글자 단위 같음, 1(메타데이터)·3(BOM 설명)만 다름 → 형상 변화 0. `replay.json` r1에 기록.
- 형상이 같으므로 앞 회차의 과제 범위 검사(새 겹침 0, 띠 윗면 Z 0.000, 트레드 ↔ 띠 LIFT −10 X 0·690·1,380 맞닿음 0.0016, LIFT 0 X 800·1,000 10.0)가 그대로 유효. 다시 돌리지 않음(E-17 바뀐 범위 = 메타데이터만).
- 서명: `ledger.py sigpatch --signatures tools/out/DC2-05/signatures.json --doc cand.sc --parts changed_parts.json --bolts changed_bolts.json --removed <D25H 28>` → 바뀜 17, 없어짐 28, 전체 3,634. `ledger.py scope` → 새로 17, 없어짐 28, 이웃 7(`tools/out/DC2-05/scope.json`). 참고: 서명 표에는 torque 칸이 담기지 않는다(체결 기록 changed_bolts.json에는 있음).

## 3. 넘길 것
- 합치기·문서: BOM CB5-12(DC2-05 8개) 비고 "조임 0.6 N·m, 중강도 나사 고정제, 표준 토크 금지". 도면 조립 주기 같음. 결정로그 DC2-05-M3(조각).
- 해석: 임시 STEP `tools/out/mech_DC2-05/stepout/P_DC205_STRIP.step`·`P_DC205_DISC.step`(형상 같음). 하중 조건만 예압 600 N으로.
- 제어 순서 제약(U-09): 새로 없음. 'J_U5_LIFT −10은 매트 없을 때만' 유지.

## 워크플로우 메모
- 생성기를 인자 없이 돌리면 볼트 단계가 빠진 56단계가 나온다(`--bolt-body` 필요). 기본값으로 넣어 두면 수정 회차가 덜 헷갈린다.
- 조임 토크처럼 형상이 아닌 지정은 서명 표에 담을 자리가 없다. 체결 기록·메타데이터로만 전달된다.
