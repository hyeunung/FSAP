# 준비 점검 — FSAP_v2.6.4 (2026-11-06, 엔진 v3.9.3 재시작)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.6.4.sc`(tools/config.json doc = machine.json doc).
- 통로: **CLI**(MCP 안 씀). `running` 빈 목록이었으나 앱의 열린 문서 `FSAP_v2.6.4`가 **`dirty: true`, `path: null`, revision 635**(메타 "STEPSWAP mechanism: … CB5-6 x2 … swapped"). 저장본을 `open`하면 이 변경이 버려지므로 열지 않았다(안내서 '문서 확인'). 앱 문서는 건드리지 않음 — 버린 것 없음.
- CLI `solidcraft-cli run tools/out/prep/prep_check.json --in FSAP_v2.6.4.sc --results`(저장 없음) 1회, 242 s.
- `joint.list`: floating **0**, conflicts 0, errors 0, fixed [0, 2]. 조인트 317 = 리지드 288 + 슬라이더 20 + 회전 9. machine.json joints 29개 이름 모두 있음.
- 동작 연구 8개 `motion.play step 0` 모두 conflicts 0, unmoved 0: CYCLE_L·CYCLE_S·CYCLE_G1·CYCLE_G2·MAINT_HEAD·SEAM_U7·MAINT_U7·REST(마지막, 대기 포즈).
- 작업 대상 모형(저장본 안 이름): MAT_L·MAT_S·MAT_G, TAPE_ 4, SEAM_ 계열 있음.
- gmsh: **불러올 수 없음**(ModuleNotFoundError). 구상은 gmsh 없이(WF-127).
- 미완(막지 않음): 6-4 계단형 '오목 모서리' 매트 모형 없음(홈 바닥 오목 반원으로 대신). `STEP대기_` 구매품은 STEPWAIT 몫. 앱의 저장 안 된 문서 처리는 모델링부/사용자 판단.
- 바뀐 부품: 없음(읽기만, 저장 0).

## 1. 근거 규칙
- 안내서 '문서 확인': "열린 설계가 `dirty`(저장 안 된 변경)면 `open` 전에 멈추고 보고한다." — dirty true라 MCP open 안 함. 실행 규칙 2 "앱이 꺼져 있거나 MCP 호출이 실제로 실패할 때만 CLI로 하고 이유를 보고서에 적는다" — 이유: open 하면 앱의 저장 안 된 변경을 버리게 됨.
- 안내서 '동작 검사': "끝까지 고정부에 이어졌는지 `joint.list`의 `floating`", "사이클(요구서 0-3)을 동작 연구로", "작업 대상 모형(요구서 0-2 크기 양 끝, 가공 뒤 형상·조각)".
- 안내서 '동작 상태 초기화': "`motion.play {\"study\": \"<이름>\", \"step\": 0}`" — CLI 스크립트 마지막 단계 REST step 0.
- 실행 규칙 7: "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"(WF-113).

## 2. 점검표

| 항목 | 필요 | 있음 | 근거 |
|---|---|---|---|
| 고정부 | 접지 컴포넌트 | 있음 | joint.list fixed [0, 2] |
| 조인트, floating 없음 | 0-8 v2 구동 | 있음 | 317개, floating [], conflicts [], errors [] |
| 대기 0단계 연구 | REST | 있음 | motion.play REST 0, conflicts 0 |
| 사이클 연구 | 0-3 ①~⑤ | 있음 | CYCLE_L·S·G1·G2 / MAINT_HEAD·MAINT_U7 / SEAM_U7, 모두 step 0 ok |
| 기계 정의 | 유닛·상태·path_parts | 있음 | tools/machine.json: units 13, joints 29, studies 8, states 26, path_parts 6, temp_values 11 |
| 크기 범위 양 끝 | 0-2, D-01 | 있음(임시) | MAT_L, MAT_S |
| 가장 좁은 홈 매트 | 6-4 | 있음(임시) | MAT_G (D-02·D-03) |
| 가공 뒤 형상 | 테이프 띠·이음매 | 있음(임시) | TAPE_ 4, SEAM_ (D-06·D-07) |
| 떨어진 조각 | 0-8-4 ⑤ | 해당 없음 | machine.json workpiece_stages: 조각 없음(D-07) |
| 매트 평면 운동 모형 | 볼 위 X·Y·회전 | 있음 | J_WP_k_X·Y·ROT, 기계 축 아님(실행 규칙 20) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4
machine.json states 26개, 앞 점검(같은 v2.6.4)과 같다.

| 요구서 | 대응 상태 |
|---|---|
| 0-3 ① 올리고 시작 | 대기, 큰 매트 로딩 끝 |
| 0-3 ② 시작점·바인더 물림 | 큰/작은 매트 바퀴 내림(+ SEAM_U7) |
| 0-3 ③ 외곽 봉제·회전 | 직선, 볼록 모서리 45°·90°, 홈 입구 회전, 홈 안 벽, 홈 바닥 꺾임(오목), 모서리 끝 테이프 위, THICK_6·16 |
| 0-3 ④ 이음매 | 큰·작은·홈 매트 이음매 겹침 끝 |
| 0-3 ⑤ 배출 | 큰·작은·홈 매트 배출 |
| 정비 | MAINT_HEAD, MAINT_U7 |
| 6-4 오목 모서리(계단형) | 없음 — 홈 바닥 오목 반원으로 대신(막지 않음) |

## 4. 원복
- 앱: 아무 호출도 편집하지 않음(document.inspect 1회만). 저장본: CLI `run` --save 없음, 마지막 단계 REST step 0. 저장 0.

## 워크플로우 메모
- 앱에 이름은 `FSAP_v2.6.4`인데 path null·dirty true인 문서가 남아 있었다(STEPSWAP 메타). 앞 실행의 모델링부가 저장 뒤 편집했거나 저장 전 끝난 흔적으로 보인다. 다음 MCP 부서는 open 전에 이 문서를 어떻게 할지 정해야 한다(버리지 말 것).
- `document.inspect`는 measure·sketches·joints를 꺼도 70만 자였다. dirty·name·path만 보는 가벼운 질의가 있으면 좋겠다(반복).
