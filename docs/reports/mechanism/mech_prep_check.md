# 준비 점검 — v1.0 첫 실행 다시 점검(2026-11-03, 엔진 v3.7.1)

## 요약
- 결과: **ready = true**. 준비부가 만든 `3D_Modeling/FSAP_v1.0.0.sc`(문서 이름 FSAP_v1.0.0)와 `tools/machine.json`으로 동작 검사(E-03)를 할 수 있다. 앞 점검(ready=false, 파일 없음)은 준비부 앞 시점이라 이번 점검으로 대체한다.
- 통로: MCP 한 번 open(앱 --control 27878, 직전 문서 dirty false, running 비어 있음). 읽기만, 저장 안 함. 끝에 `motion.play REST step 0`으로 원복(조인트 전부 rest 값).
- joint.list: floating 0, conflicts 0, errors 0, fixed = occurrence 0·2(root·REF_GROUND). 조인트 5개 + 리지드 그룹 6개(매트·테이프 → U3_ROT).
- 동작 연구 6개: REST(1, 대기 0단계), CYCLE_L(659), CYCLE_S(491), CYCLE_G1(478), CYCLE_G2(597), REWIND_EMPTY(72). machine.json `studies` 단계 수와 모두 같다.
- 작업 대상 모형: 큰 매트 1500×1500, 작은 매트 300×200, 가장 좁은 U홈 매트(25×150, R12.5) + 가공 뒤 형상(TAPE_*·SEAM_*). 떨어진 조각 없음(machine.json fragments, 근거 적힘).
- gmsh: 불러오기 실패(ModuleNotFoundError) → gmsh=false.
- 비차단 빈칸 1: 6-4 '오목 모서리'(0-2의 계단형 오목 모서리) 전용 모형·상태 없음. 홈 바닥 꺾임(오목 180°, R12.5)이 같은 회전 방향의 더 불리한 경우라 E-19로 대표한다. 계단형 모형은 N00/N03에서 더하길 권한다.
- 참고: 기계 형상(U1~U9 차지 공간 상자)이 아직 없어 간섭 대상은 매트끼리뿐이다 — N00 몫이며 동작 정의 준비 여부와는 별개.
- 바뀐 부품: 없음.

## 확인한 것
| 항목 | 근거 | 결과 |
|---|---|---|
| 설계 파일 | config.json `doc: ../3D_Modeling/FSAP_v1.0.0.sc` | 있음(66,911 B), open errors 0, features 30 |
| 고정부·조인트 | 안내서 '동작 검사', E-15 "움직임은 기계 정의의 조인트로만" | REF_GROUND 고정, J_U4_X·J_U4_Y(slider)·J_U3_ROT(revolute)·J_U1_PRESSER·J_U1_NEEDLE(slider), floating 없음 |
| 대기 포즈 0단계 연구 | 요구서 8-6 "동작 상태 초기화: 설계 안 대기 동작 연구의 0단계" | REST step 0: X 0, Y 0, 회전 0°, 노루발 20(들림), 바늘 0 — machine.json '대기' 상태와 같음 |
| 사이클 연구 | 요구서 0-3 ①~⑤(0-8-4) | CYCLE_L·S·G1·G2 + REWIND_EMPTY |
| 기계 정의 | WF-125 | `tools/machine.json`: joints 5, units(REF·U1~U9), studies 6, states 19, path_parts 7, baseline_overlaps 4 |
| 작업 대상 양 끝 | 요구서 0-2, D-01(300×200 ~ 1500×1500 임시값), D-02·D-03 | MAT_L·MAT_S·MAT_G 있음(WF-113: D 임시값으로 만든 것은 있는 것으로 봄) |
| 가공 뒤 형상·조각 | 안내서 '동작 검사' | TAPE_L/S/G·SEAM_L/S/G 있음, 조각 없음(절단은 바인더 앞, 실 끝은 헤드 내장 사절) |
| gmsh | `python -B -c "import gmsh"` | 실패 |

## 상태 목록 ↔ 요구서 0-3·6-4
| 요구서 | 대응 상태(연구·단계) |
|---|---|
| 0-3 ① 올리고 시작 | 대기(REST 0) |
| 0-3 ② 시작점·물림 | 노루발 내림(CYCLE_L 20, CYCLE_S 36) |
| 0-3 ③ 돌리며 봉제(홈 안 포함) | 직선 가운데(L 621, S 450), 홈 안 벽(G1 158), 모서리·홈 회전 |
| 0-3 ④ 이음매·절단 | 이음매 겹침 끝(L 638, S 454, G2 574) |
| 0-3 ⑤ 배출 | 배출 자리(L 659, S 491, G2 597), 되감기(REWIND_EMPTY 36) |
| 6-4 직선 | L 621, S 450 |
| 6-4 볼록 모서리 | L 97, S 87 |
| 6-4 오목 모서리 | **전용 상태 없음** → 홈 바닥 꺾임으로 대표(E-19 "같은 것은 묶어 가장 불리한 하나만") |
| 6-4 홈 입구 | G1 97, G1 431 |
| 6-4 홈 바닥 꺾임 | G1 264, G1 354 |
| 6-4 시작·끝 이음매 | L 638, S 454, G2 574 |

## 빠진 것(missing)
1. 6-4 '오목 모서리'(계단형) 전용 매트 모형·상태 — 비차단(E-19 대표), N00/N03에서 계단형 오목 모서리 모형 추가 권장.

## 원복
- 저장 안 함. 편집 없음. `motion.play {study: REST, step: 0}` → moved false, conflicts 0, 조인트 값 J_U4_X 0·J_U4_Y 0·J_U3_ROT 0°·J_U1_PRESSER 20·J_U1_NEEDLE 0.

## 워크플로우 메모
- `joint.list`+`motion.list`를 한 batch로 부르면 응답이 30만 자(연구 keys 전체)라 파일로 넘어간다. 준비 점검용으로는 연구 이름·단계 수만 주는 요약 옵션이 있으면 좋겠다.
