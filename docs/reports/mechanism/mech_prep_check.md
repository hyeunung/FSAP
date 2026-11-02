# 준비 점검 — v1.0 두 번째 실행(2026-11-03, 엔진 v3.7.2)

## 요약
- 결과: **ready = true**. 대상 `3D_Modeling/FSAP_v1.0.1.sc`(config.json doc, 문서 이름 FSAP_v1.0.1)와 `tools/machine.json`으로 동작 검사(E-03)를 할 수 있다.
- 통로: MCP. 앱(--control 27878) running 비어 있음, 열린 문서 FSAP_v1.0.1 dirty false 확인 뒤 저장본을 한 번 open(errors 0, features 86). 읽기만, 저장 안 함, 편집 없음.
- joint.list: floating 0, conflicts 0, errors 0, fixed = occurrence 0·2(root·REF_GROUND). 움직이는 조인트 5개 + 리지드 그룹 15개(매트·테이프 6 → U3_ROT, 고정 유닛 8 → REF_GROUND, U5 → U4_X).
- 동작 연구 6개: REST(1), REWIND_EMPTY(72), CYCLE_L(659), CYCLE_S(491), CYCLE_G1(478), CYCLE_G2(597) — machine.json `studies` 단계 수와 모두 같다.
- machine.json 상태 19개를 연구 키(단계 = 시간)에서 보간해 대조: 어긋남 0(허용 0.1).
- 작업 대상 모형: 큰 매트 MAT_L 1500×1500, 작은 매트 MAT_S 300×200, U홈 매트 MAT_G(25×150, R12.5) + 가공 뒤 형상 TAPE_*·SEAM_*. 떨어진 조각 없음(machine.json fragments 근거).
- gmsh: `python -B -c "import gmsh"` → ModuleNotFoundError → **false**.
- 비차단 빈칸 1: 6-4 '오목 모서리'(계단형) 전용 모형·상태 없음 — 홈 바닥 꺾임으로 대표(E-19). 첫 실행 점검과 같음.
- 바뀐 부품: 없음. 원복: `motion.play {study: REST, step: 0}` → moved false, conflicts 0.

## 확인한 것
| 항목 | 근거 | 결과 |
|---|---|---|
| 설계 파일 | config.json `doc: ../3D_Modeling/FSAP_v1.0.1.sc` | open errors 0, features 86, 바디 36(REF 1, WP 9, 유닛 상자 26) |
| 고정부·조인트 | 안내서 '동작 검사', E-15 "움직임은 기계 정의의 조인트로만" | J_U4_X(11)·J_U4_Y(12) slider, J_U3_ROT(13) revolute, J_U1_PRESSER(62)·J_U1_NEEDLE(65) slider. 사슬 REF_GROUND→U4_X→U4_Y→U3_ROT, floating 없음. 한계값이 machine.json min·max와 같음 |
| 대기 포즈 0단계 연구 | 요구서 8-6 "동작 상태 초기화: 설계 안 대기 동작 연구의 0단계" | REST step 0: X 0, Y 0, 회전 0°, 노루발 20(들림), 바늘 0 = machine.json '대기' |
| 사이클 연구 | 요구서 0-3 ①~⑥(0-8-4) | CYCLE_L·S·G1·G2 + REWIND_EMPTY |
| 기계 정의 | WF-125 | `tools/machine.json`: joints 5, units 14(REF·U1~U9 세부), studies 6, states 19, path_parts 7, baseline_overlaps 15(N00 맞닿음 포함) |
| 작업 대상 양 끝 | 요구서 0-2, D-01(300×200 ~ 1500×1500 임시값), D-02·D-03 | MAT_L·MAT_S·MAT_G 있음(WF-113: D 임시값으로 만든 것은 있는 것으로 봄) |
| 가공 뒤 형상·조각 | 안내서 '동작 검사' | TAPE_L/S/G·SEAM_L/S/G 있음. 조각 없음(절단은 바인더 앞, 실 끝은 헤드 내장 사절, D-07) |
| gmsh | WF-127 | 실패 → 구상은 gmsh 없는 지시 |

## 상태 목록 ↔ 요구서 0-3·6-4
| 요구서 | 대응 상태(연구·단계) |
|---|---|
| 0-3 ① 대기·로딩 | 대기(REST 0) |
| 0-3 ② 노루발 내림 | CYCLE_L 20, CYCLE_S 36 |
| 0-3 ③ 봉제(직선·홈 안) | L 621, S 450, G1 158 |
| 0-3 ④ 모서리·홈 회전 | L 97, S 87, G1 97·431(홈 입구), G1 264·354(홈 바닥 꺾임) |
| 0-3 ⑤ 이음매·절단 | L 638, S 454, G2 574 |
| 0-3 ⑥ 배출·되감기 | L 659, S 491, G2 597, REWIND_EMPTY 36 |
| 6-4 직선 / 볼록 모서리 / 홈 입구 / 홈 바닥 꺾임 / 이음매 | 위 행과 같음 |
| 6-4 오목 모서리(계단형) | **전용 상태 없음** → 홈 바닥 꺾임(오목 180°, R12.5)으로 대표(E-19 "같은 것은 묶어 가장 불리한 하나만") |

## 빠진 것(missing)
1. 6-4 '오목 모서리'(계단형) 전용 매트 모형·상태 — 비차단. N03(또는 매트 모형을 고치는 과제)에서 계단형 모형 추가 권장.

## 원복
- 저장 안 함. 편집 없음. `motion.play {study: REST, step: 0}` → moved false, conflicts 0, 조인트 값 0·0·0°·20·0.

## 워크플로우 메모
- `motion.list`가 여전히 23만 자(키 전체)라 파일로 넘어간다. 첫 실행 메모와 같은 문제(연구 이름·단계 수만 주는 요약 옵션 필요).
