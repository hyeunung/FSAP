# 준비 점검 — v1.0 두 번째 실행 2라운드(2026-11-03, 엔진 v3.7.2)

## 요약
- 결과: **ready = true**. 대상 `3D_Modeling/FSAP_v1.0.16.sc`(config.json doc, 문서 이름 FSAP_v1.0.16)와 `tools/machine.json`으로 동작 검사(E-03)를 할 수 있다.
- 통로: MCP. 앱(--control 27878) running 비어 있음, 열린 문서 FSAP_v1.0.16 dirty false 확인 뒤 저장본을 한 번 open(errors 0, features 777, 바디 158). 읽기만, 저장 안 함, 편집 없음.
- joint.list: floating 0, conflicts 0, errors 0, fixed 2. 움직이는 조인트 14개(machine.json joints 14개와 이름 일치) + 리지드 그룹.
- 동작 연구 7개: REST 1, REWIND_EMPTY 72, CYCLE_L 659, CYCLE_S 491, CYCLE_G1 528, CYCLE_G2 597, MAINT 21 — machine.json `studies` 단계 수와 모두 같다.
- 작업 대상 모형: MAT_L 1500×1500, MAT_S 300×200, MAT_G(U홈 25×150 R12.5) + TAPE_*·SEAM_*(가공 뒤 형상). 떨어진 조각 없음(machine.json fragments).
- 상태 21개 대조(조인트 값 108개, 허용 0.1): **어긋남 11개 — 모두 CYCLE_G1 상태 3개의 단계 번호가 옛 478단계 연구 기준으로 남음**(N01-S02 피벗으로 연구가 528단계가 됨). 비차단, machine.json 고칠 것.
- machine.json `doc`가 `FSAP_v1.0.15.sc`로 남아 있음(config.json은 v1.0.16). 비차단.
- gmsh: `python -B -c "import gmsh"` → ModuleNotFoundError → **false**.
- 바뀐 부품: 없음. 원복: `motion.play {study: REST, step: 0}` → moved false, conflicts 0, unmoved 0.

## 확인한 것
| 항목 | 근거 | 결과 |
|---|---|---|
| 설계 파일 | config.json `doc: ../3D_Modeling/FSAP_v1.0.16.sc`, 안내서 '문서 확인' "모든 error·warning이 null이어야 한다" | open errors 0, features 777. 타임라인 error 0, warning 4(Cylinder34·Extrude34~36 'Boolean retry' 미세 보정, Extrude34는 판금 P_DC03_YMOV 전개도 안내 포함). 동작 검사에는 영향 없음 — 판금 전개는 디테일 기록(E-02) |
| 고정부·조인트 | E-15 "움직임은 기계 정의의 조인트로만", 안내서 '동작 검사' "끝까지 고정부에 이어졌는지 joint.list의 floating" | J_U4_X(11)·J_U4_Y(12)·J_U3_ROT(13)·J_U1_PRESSER(62)·J_U1_NEEDLE(65)·J_U8_PULL(221)·J_N04_CH_P/N/A(1257~1259)·J_N04_STOP_A(1262)·J_N04_STOP_P/N(1330·1331)·J_N04_BAR_NP/PN(1332·1333). floating 0 |
| 대기 포즈 0단계 연구 | 요구서 8-6 "동작 상태 초기화: 설계 안 대기 동작 연구의 0단계" | REST step 0 = machine.json '대기'(어긋남 0) |
| 사이클 연구 | 요구서 0-3(0-8-4) ①~⑥ | CYCLE_L·S·G1·G2 + REWIND_EMPTY, 정비 MAINT |
| 기계 정의 | WF-125 | `tools/machine.json`: joints 14, units 24, studies 7, states 21, path_parts 12, baseline_overlaps 47, probe_sets 1(N04 사슬 프로브) |
| 작업 대상 양 끝 | 요구서 0-2, D-01(300×200 ~ 1500×1500 임시값), D-02·D-03 | MAT_L·MAT_S·MAT_G 있음(WF-113: D 임시값으로 만든 것은 있는 것으로 봄) |
| 가공 뒤 형상·조각 | 안내서 '동작 검사' | TAPE_L/S/G·SEAM_L/S/G 있음. 조각 없음(D-07) |
| gmsh | WF-127 | 실패 → 구상은 gmsh 없는 지시 |

참고: 연구 `steps`=N은 키 시간 0~N(단계 N까지 유효)이다. 배출 자리 상태(step = steps)는 범위 안이다. 회전 키는 연구 안에서 라디안으로 저장돼 도로 바꿔 대조했다.

## 상태 목록 ↔ 요구서 0-3·6-4
| 요구서 | 대응 상태(연구·단계) |
|---|---|
| 0-3 ① 대기·로딩 | 대기(REST 0) |
| 0-3 ② 노루발 내림 | CYCLE_L 20, CYCLE_S 36 |
| 0-3 ③ 봉제(직선·홈 안) | L·S 직선 가운데, G1 홈 안 벽 |
| 0-3 ④ 모서리·홈 회전 | L·S 볼록 45°, G1 홈 입구·두 번째 홈 입구, G1 홈 바닥 꺾임 가운데·끝 |
| 0-3 ⑤ 이음매·절단 | L·S·G2 이음매 겹침 끝 |
| 0-3 ⑥ 배출·되감기 | L 659, S 491, G2 597, REWIND_EMPTY |
| 6-4 직선 / 볼록 모서리 / 홈 입구 / 홈 바닥 꺾임 / 이음매 | 위 행과 같음 |
| 6-4 오목 모서리(계단형) | 전용 상태 없음 → 홈 바닥 꺾임(오목 180°, R12.5)으로 대표(E-19 "같은 것은 묶어 가장 불리한 하나만"). 첫 점검과 같음 |

## 어긋난 상태(machine.json 단계 번호가 옛 값)
| 상태 | machine.json step | 같은 자세가 있는 지금 단계 | 비고 |
|---|---|---|---|
| 홈 매트 홈 바닥 꺾임 가운데(가장 깊은 점) | 264 | **289**(X 450, Y 700, 회전 0°) | 지금 연구는 이 점에서 노루발 20(들림)·바늘 −30(찔림) 피벗 자세. machine.json은 노루발 0·바늘 0 |
| 홈 매트 홈 바닥 꺾임 끝(X +312.5) | 354 | **406**(1212.5, 862.5, −90°, 0, 0) | 값 일치, 단계만 다름 |
| 홈 매트 두 번째 홈 입구 회전 45° | 431 | **481**(696.707, 1045.235, −45°, 20, −30) | 값 일치, 단계만 다름 |

검도·과제 안 검사가 상태 이름으로 `motion.play`할 때 엉뚱한 자세를 잴 수 있으니 다음 모델링부(또는 machine.json을 고치는 부서)가 위 세 단계와 '가장 깊은 점'의 노루발·바늘 값을 고치고 `doc`을 v1.0.16으로 맞춘다. 라운드 끝 전체 회귀는 연구 전 단계를 돌므로 영향 없다.

## 빠진 것(missing)
1. machine.json 상태 3개(CYCLE_G1 264·354·431)의 단계 번호가 지금 연구(528단계)와 어긋남 → 289·406·481로 고칠 것(비차단).
2. machine.json `doc`가 v1.0.15 → v1.0.16으로 고칠 것(비차단).
3. 6-4 '오목 모서리'(계단형) 전용 매트 모형·상태 없음 — 홈 바닥 꺾임으로 대표(비차단, 첫 점검과 같음).

## 원복
- 저장 안 함. 편집 없음. `motion.play {study: REST, step: 0}` → moved false, conflicts 0, unmoved 0, 조인트 값 14개.

## 워크플로우 메모
- `joint.list`(15만 자)·`motion.list`(55만 자)·`motion.play`(8.7만 자)·`inspect_design`(27만 자, measure·sketches 끔)이 모두 화면 한도를 넘어 파일로 넘어간다. 요약 옵션(이름·단계 수·floating만)이 있으면 준비 점검이 더 빠르다(첫 실행 메모와 같은 문제).
- 연구를 늘리는 모델링(N01-S02 피벗 10단계 추가)이 machine.json 상태 단계 번호를 같이 고치지 않았다. 연구 단계가 바뀌면 상태 단계를 다시 찾는 단계가 모델링부 절차에 필요하다.
