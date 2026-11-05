# 준비 점검 — FSAP_v2.5.8 (2026-11-05)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.5.8.sc`(config doc). 고정부·조인트·대기 연구·사이클 연구·매트 모형 3장·가공 뒤 형상이 다 있다.
- 통로: **MCP**. `running` 빈 목록(막힌 요청 없음). 앱에 열린 문서는 이미 `FSAP_v2.5.8`, `dirty: false`, revision 1 — 저장 안 된 'merged' 문서는 남아 있지 않아 버릴 것도, 다시 열 것도 없었다(open 0, save 0).
- `joint.list`: floating **0**, conflicts 0, errors 0, fixed [0, 2]. 조인트 295 = 리지드 266 + 슬라이더 20 + 회전 9. machine.json joints 29개가 이름까지 모두 있다.
- 동작 연구 8개 모두 `motion.play step 0` 성공(conflicts 0, unmoved 0): CYCLE_L · CYCLE_S · CYCLE_G1 · CYCLE_G2 · MAINT_HEAD · SEAM_U7 · MAINT_U7 · REST(마지막, 대기 포즈로 초기화).
- 타임라인 1,978 피처: error 0, warning 15(불리언 재시도 7, 면 이름 다시 찾음 4, STEP 볼 면 못 읽음 3 등 — 막지 않음).
- gmsh: **불러올 수 없음**(ModuleNotFoundError). 구상은 gmsh 없이 한다(WF-127).
- 미완(막지는 않음): 6-4 계단형 '오목 모서리' 매트 모형 없음(앞 점검과 같다). machine.json `doc`이 아직 `FSAP_v2.5.7.sc`(config는 v2.5.8; v2.5.8은 CYCLE_G1 J_U5_LIFT 319·320단계 값만 바뀜, 조인트·상태 목록 같음). 최상위 바디 이름 기준 `STEP대기_` 46개 — 구매부·STEP 교체 몫.
- 바뀐 부품: 없음(읽기만, 저장 0).

## 1. 근거 규칙
- 안내서 '동작 검사': "끝까지 고정부에 이어졌는지 `joint.list`의 `floating`", "사이클(요구서 0-3)을 동작 연구로", "작업 대상 모형(요구서 0-2 크기 양 끝, 가공 뒤 형상·조각)".
- 안내서 '동작 상태 초기화': "설계 안에 \"대기\" 포즈를 0단계로 둔 동작 연구 … `motion.play {\"study\": \"<이름>\", \"step\": 0}`."
- 안내서 '문서 확인': "열린 설계가 `dirty`(저장 안 된 변경)면 `open` 전에 멈추고 보고한다." — dirty false라 해당 없음.
- 실행 규칙 7: "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다(ready=true …)"(WF-113).

## 2. 점검표

| 항목 | 필요 | 있음 | 근거 |
|---|---|---|---|
| 고정부 | 접지 컴포넌트 | 있음 | joint.list fixed [0, 2] |
| 조인트, floating 없음 | 0-8 v2 구동 | 있음 | 295개, floating [], conflicts [], errors [] |
| 대기 0단계 연구 | REST | 있음 | motion.play REST 0 ok |
| 사이클 연구 | 0-3 ①~⑤ | 있음 | CYCLE_L·S·G1·G2 / 정비 MAINT_HEAD·MAINT_U7 / 이음매 SEAM_U7, 모두 step 0 ok |
| 기계 정의 | 유닛·상태·path_parts | 있음 | tools/machine.json: units 13, joints 29, studies 8, states 26, path_parts 6(U2_~U7_), baseline_overlaps 19, temp_values 11 |
| 크기 범위 양 끝 | 0-2, D-01 | 있음(임시) | MAT_L, MAT_S (D-01) |
| 가장 좁은 홈 매트 | 6-4 | 있음(임시) | MAT_G (D-02·D-03) |
| 가공 뒤 형상 | 테이프 띠·이음매 | 있음(임시) | TAPE_L·S·G, SEAM_L·S·G (D-06·D-07) |
| 떨어진 조각 | 0-8-4 ⑤ | 해당 없음 | machine.json workpiece_stages.fragments: 조각 없음(D-07) |
| 매트 평면 운동 모형 | 볼 위 X·Y·회전 | 있음 | J_WP_k_X·Y·ROT(k=L·S·G), 기계 축 아님(실행 규칙 20) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4
machine.json states 26개, 앞 점검(v2.5.5)과 같다.

| 요구서 | 대응 상태 |
|---|---|
| 0-3 ① 올리고 시작 | 대기, 큰 매트 로딩 끝 |
| 0-3 ② 시작점·바인더 물림 | 큰/작은 매트 바퀴 내림(+ SEAM_U7 연구) |
| 0-3 ③ 외곽 봉제·회전 | 직선, 볼록 모서리 45°·90°, 홈 입구 회전, 홈 안 벽, 홈 바닥 꺾임(오목), 모서리 끝 테이프 위, THICK_6·16 |
| 0-3 ④ 이음매 | 큰·작은·홈 매트 이음매 겹침 끝 |
| 0-3 ⑤ 배출 | 큰·작은·홈 매트 배출 |
| 정비 | 머리판 탈착(MAINT_HEAD), MAINT_U7 |
| 6-4 오목 모서리(계단형) | 없음 — 홈 바닥 오목 반원으로 대신(막지 않음, 앞 점검과 같음) |

## 4. 원복
- 편집 0. 마지막에 `motion.play {study: REST, step: 0}` — 대기 포즈. 저장 0.

## 워크플로우 메모
- `inspect_design`(measure·sketches·joints false)도 69만 자, `motion.play` 8개 묶음 결과가 950만 자(positions 2,501개씩 돌려줌)라 파일로 넘어갔다. 준비 점검에는 conflicts·unmoved만 필요하므로 요약 응답 인자가 있으면 좋겠다.
