# SolidCraft MCP/CLI 실측 기록 정리 (FSAP MAT-RS-001)

2026-11-02. 엔진(MechDesign_Engine v3.4.0)의 SolidCraft MCP/CLI 배치를 정하기 위한 자료다. 이 프로젝트에서 SolidCraft를 실제로 돌린 기록만 모았다. 새로 재지 않았고 추정하지 않았다. 기록에 없는 것은 "기록 없음"으로 적었다.

- 출처: `docs/reports/` 아래 부서 보고서, `tools/out/` 시간표·스크립트, `tools/run-rules.md`.
- 이 정리를 만든 세션에서는 SolidCraft를 돌리지 않았다(대화 기록 없음).
- **가장 큰 빈칸:** MCP `open` 시간과, 열린 뒤 MCP 측정 명령 하나의 시간은 **기록 없음**. MCP와 CLI 열기 비용을 같은 파일로 바로 비교할 수 없다.

## 0. 파일 크기·바디 수

크기는 지금 디스크의 `3D_Modeling/` 기준. 바디 수는 보고서에 적힌 값.

| 파일 | 크기(B) | 바디 | 바디 수 출처 |
|---|---|---|---|
| v0.3.1 | 1,439,023 | 기록 없음 | — |
| v0.3.2 | 1,082,414 | 기록 없음 | — |
| v0.4.2 | 5,479,356 | occurrence 126 | mech_S01_model.md:109 |
| v0.5.0 / v0.6.0 | 3,326,623 / 3,497,847 | 기록 없음 | — |
| v0.6.1 | 3,465,551 | 161 | mech_regression.md:22 |
| v0.6.10 | 6,908,558 | 261 | mech_T08_measure.md:208 |
| v0.6.13 | 11,535,623 | 288 | mech_T10_measure.md:110 |
| v0.7.0 | 12,144,856 | 325 (T13 선정은 320) | mech_T12_model.md:105, mech_T13_select.md:164 |
| v0.7.1 | 11,988,235 | 289 | mech_T13_measure.md:88 |
| v0.7.2 | 11,836,976 | 279 | queue_2026-11-01_1.md:3, mech_STEPSWAP_model.md:5 |
| v0.8.0 | 14,081,913 | 387 | mech_T18_verify.md:55 |
| v0.8.2 | 14,265,280 | 387 (검사 대상 385 + 바뀐 2) | mech_T14_model.md:60 |

## 1. 파일 열기 비용

| 항목 | 값 | 파일 | 출처 |
|---|---|---|---|
| CLI 한 번 열기 | 14 s 이하 (회귀 작업 하나 최소 14 s, 열기 포함) | v0.6.1 (3.5 MB, 161바디) | tools/out/mech_regression/times.txt |
| CLI 한 번 열기 | 약 3분 | v0.6.14 (11.7 MB) | mech_T10_model1.md:91 |
| CLI `eval` `document.inspect` 하나 | 약 3분 20초 | v0.7.2 (11.8 MB, 279바디) | queue_2026-11-01_1.md:3 |
| CLI 한 번 열기 | 1회 3~5분 | 약 12 MB | engine-change-prompt_speed.md:7 |
| CLI 한 번 열기 | 약 3분 | v0.8.0 (14.1 MB, 387바디) | mech_T18_verify.md:193 |
| CLI 한 번 열기 | 3.5분 | v0.8.1 (14.2 MB) | mech_T14_measure.md:239 |
| CLI 읽기만 하다 거부됨 | 3분 30초 뒤 "too many bodies" | v0.8.2 | mech_T14_model.md:126 |
| MCP `open` | **기록 없음** (피처 수·오류 0만 있음) | v0.7.2, v0.8.0 | mech_STEPSWAP_model.md:16, mech_T15_model.md:15 |
| 열린 뒤 MCP 측정 하나 | **기록 없음** | — | — |
| 참고: MCP 편집 | `batch` 31단계 약 15분 (단계마다 전체 재계산 약 60초), MCP 호출 시간 초과 | v0.6.11 → v0.6.12 | mech_T09_model.md:24, :186 |

## 2. 부서별로 실제 쓴 통로

| 부서 | 통로 | 호출·열기 수 | 시간 | 출처 |
|---|---|---|---|---|
| 측정 T18 | CLI | 16회 = 열기 16회 (실제 측정 약 7개) | 26분 | engine-candidates.md:27 (WF-131), engine-change-prompt_speed.md:7 |
| 측정 T14 | CLI | 기록 없음 | 열기 3.5분 + 스크립트 9분 | mech_T14_measure.md:5, :239 |
| 측정 T09·T15·S02 | CLI | 기록 없음 | 기록 없음 | mech_T09_measure.md:4, mech_T15_measure.md:3, mech_S02_measure.md:4 |
| 측정 부서 MCP 사용 | 기록 없음 (모두 CLI) | — | — | — |
| 선정 T07 | CLI `run --results` | 1회 | 169 s | mech_T07_select.md:22 |
| 선정 T08 | CLI | 1회 | 158 s | mech_T08_select.md:17 |
| 선정 T13 | CLI | 기록 없음 | `inspect.clearance` 404 s + 열기 | mech_T13_select.md:164 |
| 검도 T14·T18 | CLI만 | 기록 없음 | T18: 열기 약 3분, 병렬 5~8개면 실행마다 30~60분 | mech_T14_verify.md:3, mech_T18_verify.md:3, :193 |
| 검도 T07 | CLI 7병렬 | 기록 없음 | 약 25분 | mech_T07_verify.md:137, tools/out/mech_T07_verify/run.sh:4 |
| 회귀 (v0.6.1) | CLI, `xargs -P 18` | 228작업 = 열기 228회 | 작업 합 57,702 s, 작업당 14~3,319 s, 중앙값 88 s | tools/out/mech_regression/runall.sh:3, times.txt |
| 회귀 보충 | CLI, `-P 19` | 496작업 = 열기 496회 | 합 62,195 s, 최대 1,559 s, 중앙값 35 s | tools/out/mech_regression/runall2.sh:3, rtimes.txt |
| 모델링 S01·T04·T05·S02 | CLI `run --save` | 기록 없음 | 기록 없음 | mech_S01_model.md:146, mech_T04_model.md:22, mech_S02_model.md:10 |
| 모델링 DP-1·DP-2 | CLI (MCP headless) | 기록 없음 | DP-2: CLI run 11분 (`component.delete` 약 29 s, `body.rename` 약 20 s) | detail_DP-1_model.md:10, detail_DP-2_model.md:151 |
| 모델링 T09·T10·T11·T12·T14·T15·T18·STEPSWAP | MCP로 그리고, 검사는 CLI | 기록 없음 | 기록 없음 (T09 편집만 1절) | mech_T09_model.md:4, mech_T14_model.md:3, mech_T15_model.md:10, mech_T18_model.md:3 |

회귀 전체 벽시계 시간은 기록 없음. 18병렬이므로 가장 긴 작업 3,319 s(약 55분)보다는 길다.

## 3. 오래 걸린 계산

| 명령 | 규모 | 통로 | 시간·결과 | 출처 |
|---|---|---|---|---|
| `motion.interference` | 1,000표본 연구, 움직이는 7묶음 | **MCP** | 약 45분째 앱 꺼짐 (실행 규칙에는 "42분 넘게 → 앱 멈춤 → 사용자가 끔") | mech_T14_model.md:125, run-rules.md:14 |
| 같은 검사를 나눠서 | 바꾼 쪽 + 이웃 하나씩, 7연구 | CLI 병렬 | 6분 안 | mech_T14_model.md:125 |
| 짧은 연구 | 93단계 | **MCP** | truncated false (시간 기록 없음) | mech_T14_model.md:77 |
| `motion.interference` | 전체 occurrence 126 | CLI | 1단계 527 s, 단계당 약 20 s (8개 동시), budget 3000에서 멈춤 | mech_S01_model.md:109, :152 |
| `motion.interference` | 77 ↔ 107 occurrence, 5,236쌍 | CLI | budget 2400 s에서 표본 10%만 보고 truncated | mech_T06_verify.md:33 |
| `motion.interference` | 18점유 780쌍, 94표본 | CLI 6병렬 | 312 s. 997표본 연구는 50분 넘게 예상돼 중단 | mech_T04_verify.md:26, :116 |
| `motion.interference` | 연구 3개 / 4개 | CLI | 2,182 s / 4,303 s | mech_T10_model1.md:34-35 |
| `motion.interference` | 3사이클, budget 500 × 3 | CLI | 25분 안에 안 끝남 | mech_T09_model1.md:8 |
| `motion.interference` | 매트 연구 (노루발 1 ↔ 매트 3) | CLI | 3~5초 | mech_T04_model.md:168 |
| `motion.interference` 회귀 | 링 ↔ MAT_ROT 동축 쌍 | CLI | 작업 하나 최대 2,546 s. 그 쌍을 빼면 작업당 약 20 s | mech_regression.md:157 |
| `inspect.interference` | 프로브 50 + 85바디 | CLI | 26분. 같은 것을 `clearance`로 재면 3분 43초 | mech_T09_measure.md:220 |
| `inspect.interference` | 쌍 2개 | CLI | 33 s, 42 s | mech_T07_verify.md:74 |
| `inspect.interference` | 28자세 | CLI | 385 s | mech_T10_model1.md:33 |
| `inspect.clearance` | 288바디 against | CLI | 40분 넘게 안 끝나 멈춤 (메모리 12 GB). 근처로 좁히니 3분 51초·3분 10초 | mech_T10_measure.md:106, :110 |
| `inspect.clearance` | 261바디, 프로브 140 × 자세 5 | CLI | 약 64분 | mech_T08_measure.md:208 |
| `inspect.clearance` | 큰 접지 프로브 | CLI | 단계당 약 15 s (작은 매트 0.7 s), 292단계 묶음 70분 | mech_T07_measure.md:239 |
| `inspect.clearance` | 52프로브 × 320바디 | CLI | 404 s | mech_T13_select.md:164 |
| `inspect.clearance` | 프로브 174 | CLI | 258 s | detail_DP-2_verify.md:159 |
| `inspect.clearance` | 바뀐 11 ↔ 278, 100단계 묶음 | CLI 6병렬 | 30분 넘게 걸려 멈춤 | mech_T11_verify.md:92 |
| `inspect.clearance` | 새 부품만 against | — | 0.1 s | mech_T12_model.md:145 |

**budget_s 때문에 끊긴 경우**

- T06 검도: budget 2400 s, 표본 10% (mech_T06_verify.md:33).
- S01 모델링: budget 3000 s, 4연구 미완 (mech_S01_model.md:109).
- T12 모델링: `inspect.interference` budget 400 s에서 89쌍을 못 봄 (mech_T12_model.md:145).
- 끝까지 간 예: S01 수정 회차 budget 20000에 3,385 s (mech_S01_model1.md:18), T13 측정 budget 7000에 7연구 모두 truncated false (mech_T13_measure.md:88).

## 4. 나눠 돌리기

| 경우 | 나눔 | 전체 시간 | 나누지 않았을 때 | 출처 |
|---|---|---|---|---|
| S01: 4연구 2,252단계 | 20병렬 | 약 56분 (3,385 s) | 직렬 추정 약 3시간 | mech_S01_model1.md:18, :56 |
| T02: 바디 단위 1,553단계 | 7병렬 | 약 11분 | 홈 사이클 하나에 1,580 s (T02 모델링부, 같은 조건인지 기록 없음) | mech_T02_measure.md:201, mech_T02_model.md:166 |
| T07 검도: clearance 100단계 청크 | 7병렬 | 약 25분 | 기록 없음 | mech_T07_verify.md:137 |
| T14: 사이클_홈매트 | 4묶음 (+ 나머지 연구도 CLI 병렬) | 6분 안 | MCP 한 번에 돌리다 45분째 앱 꺼짐 | mech_T14_model.md:75, :125 |
| T06: 단계별 clearance + 새 부품만 | 나눔 수 기록 없음 | 6분 | 한 번에 → 2400 s에서 10%만 봄 | mech_T06_verify.md:33, :126 |
| T18 검도: 묶음 A·B (약 190바디 이하) | 2묶음 × 연구 | 기록 없음 | 14 occurrence(약 380바디)는 거부됨 | mech_T18_verify.md:64, :191 |
| 회귀 v0.6.1 | 228작업 18병렬 / 496작업 19병렬 | 벽시계 기록 없음 (작업 합 57,702 s / 62,195 s) | — | runall.sh, runall2.sh, times.txt, rtimes.txt |
| 병렬의 역효과 | 14 MB 파일 5~8병렬 | 실행마다 30~60분 | — | mech_T18_verify.md:193 |

## 5. 문제가 났던 것

| 문제 | 내용 | 출처 |
|---|---|---|
| 같은 경로를 다시 `open` | 디스크에서 다시 읽지 않고 메모리의 편집을 그대로 둠 (피처 1,668 / 1665→1666). 되돌리기는 undo로 함 | mech_T14_model.md:122, mech_T15_model1.md:16, :50 |
| 저장 뒤 편집이 남음 | MCP로 `save {path}` 한 뒤 편집이 다시 열었을 때 들어 있음 (앱 자동 저장으로 보임) | mech_T09_model1.md:160 |
| 문서 이름 | v0.7.1~v0.8.2 앱 제목이 'FSAP_v0.6.15'로 남아 헷갈림 | run-rules.md:12, mech_STEPSWAP_model.md:16 |
| dirty 확인 빠짐 | `open` 전에 `inspect_design`을 안 봄 | mech_STEPSWAP_model.md:17, :62 |
| headless 판정 오류 | 서버 안내는 headless인데 실제로는 앱에 연결됨 (WF-082 반복) | mech_T09_model.md:24, final_mech_2026-10-31_S01-T06-T07-S02.md:112 |
| 큰 인자 | 키 133 KB는 MCP로 보내지 않고 CLI로 처리 | mech_T09_model1.md:24 |
| 앱을 껐을 때 돌던 명령 | 그 명령의 결과가 어떻게 됐는지는 **기록 없음**. 일반론으로 "앱을 끄면 돌던 명령이 실패한다"고만 적혀 있음. 그 연구는 CLI로 다시 돌림 | engine-change-prompt_speed.md:22, mech_T14_model.md:125 |
| 잠금 파일 | `.~FSAP_v0.7.0.sc.lock`, `.~FSAP_v0.8.2.sc.lock`이 남아 있음 (영향 기록 없음) | `3D_Modeling/` 목록 |

## 6. 판단 (기록에서 끌어낸 것이고, 실측한 경계는 아님)

| 항목 | 판단 | 근거 |
|---|---|---|
| 앱에서 해도 되는 계산 | 수십 초~몇 분 안에 끝나는 정적 확인, 좁힌 `clearance`, 100단계 안팎의 짧은 연구 | MCP 93단계 연구 성공 (mech_T14_model.md:77), clearance 0.1 s (mech_T12_model.md:145) |
| CLI로 보낼 계산 | 1,000표본 연구, 바디 약 190개 넘는 contact sweep, 수 분 넘게 걸릴 것 | MCP 42~45분 멈춤 (mech_T14_model.md:125), 약 380바디 거부 (mech_T18_verify.md:191), 320 occurrence 거부 (mech_T14_model.md:126) |
| 시간 경계 | 기록상 MCP가 견딘 가장 긴 시간은 없음. 멈춘 시점은 42~45분. 다른 부서들은 한 번 호출 8분 상한(E-04)을 썼음. **MCP 측정 시간이 기록에 없어** 경계를 정하려면 "MCP 열기 1회 + 측정 1회" 시간을 따로 재야 함 | mech_T09_measure.md:220, mech_T04_verify.md:116 |
| CLI의 고정비 | 12~14 MB(279~387바디)에서 호출마다 약 3~3.5분. 짧은 측정 여러 개를 CLI로 따로 부르면 열기에 시간이 거의 다 듦 (26분 중 대부분) | 1절, engine-candidates.md:27 (WF-131) |
| 회귀 나눔 수 | 3.5 MB 파일에서는 18~19병렬로 다 끝남 (rc 0). 14 MB 파일에서는 5~8병렬이면 실행마다 30~60분으로 늘었고, 4묶음은 6분 안에 끝남. 지금 크기라면 **4~5개**, 묶음당 약 190바디 이하가 기록과 맞음 | runall.sh, mech_T18_verify.md:193, mech_T14_model.md:125 |
