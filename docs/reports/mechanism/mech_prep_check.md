# 준비 점검 — 엔진 v3.9.2 다시 켬, M08·M04R·DC2-03 앞 (FSAP_v2.3.4) (2026-11-04)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.3.4.sc`(config doc·machine.json doc 일치, 2026-11-04 22:28 커밋)에 고정부·조인트·대기 연구·사이클 연구·매트 모형 3장·가공 뒤 형상이 다 있다.
- 앱(127.0.0.1:27878, running 빈 큐)에 이전 실행의 'merged' 문서(dirty true, path 없음, 바디 451)가 열려 있었다. 지시 (b)대로 저장하지 않고 v2.3.4 저장본을 MCP `open` 한 번(errors 0, 피처 1319)으로 바꿨다.
- `joint.list`: floating **0**, conflicts 0, errors 0, fixed [0, 2]. 조인트 181 = 리지드 152 + 슬라이더 20 + 회전 9. 기계·모형 조인트 29개가 machine.json joints 29개와 이름까지 같다.
- 동작 연구 8개 모두 `motion.play step 0` 성공(conflicts 0): REST 1 · CYCLE_L 716 · CYCLE_S 450 · CYCLE_G1 514 · CYCLE_G2 630 · MAINT_HEAD 1 · SEAM_U7 32 · MAINT_U7 13 — machine.json studies 8개와 같다.
- 동작 상태 초기화: 마지막에 `motion.play REST step 0`. 저장 0, 편집 0.
- gmsh: **불러올 수 없음**(ModuleNotFoundError) — 구상은 gmsh 없이(WF-127).
- 미완(막지 않음): 6-4 계단형 '오목 모서리' 매트 모형 없음(앞 점검과 같음). STEP대기_ 바디 56개(구매부·STEP 교체 몫, 이 점검의 준비물 아님).

## 1. 근거 규칙
- 안내서 '동작 검사': "끝까지 고정부에 이어졌는지 `joint.list`의 `floating`", "사이클(요구서 0-3)을 동작 연구로", "작업 대상 모형(요구서 0-2 크기 양 끝, 가공 뒤 형상·조각)".
- 안내서 '동작 상태 초기화': "설계 안에 \"대기\" 포즈를 0단계로 둔 동작 연구(motion study)를 만들어 두고 `motion.play {\"study\": \"<이름>\", \"step\": 0}`."
- 실행 규칙 7: "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다(ready=true …)"(WF-113).
- 실행 규칙 2: "혼자 도는 읽기 부서도 MCP로 잰다 … `open {path: 저장본}` 한 번 … 저장은 하지 않는다(`save` 금지, 끝나면 `motion.play` step 0)."

## 2. 점검표

| 항목 | 필요 | 있음 | 근거 |
|---|---|---|---|
| 고정부 | 접지 컴포넌트 | 있음 | joint.list fixed [0, 2], 리지드 152 |
| 조인트, floating 없음 | 0-8 v2 구동 | 있음 | U3 노루발·바늘, U4 누름·바퀴·디스크·실린더 핀/로드, U5 X·승강·바퀴, U6 SHIFT·HGT, U7 카세트 X·Y·절단·접어넣기·공급·걸쇠·HGT; floating [] |
| 대기 0단계 연구 | REST | 있음 | motion.play REST 0 ok |
| 사이클 연구 | 0-3 ①~⑤ | 있음 | CYCLE_L·S·G1·G2, 정비 MAINT_HEAD·MAINT_U7, 이음매 SEAM_U7, 모두 step 0 ok |
| 기계 정의 | 유닛·상태·path_parts | 있음 | tools/machine.json: units 13, joints 29, studies 8, states 26, path_parts [U2_~U7_], baseline_overlaps 19, temp_values 11 |
| 크기 범위 양 끝 | 0-2, D-01 | 있음(임시) | MAT_L, MAT_S (D-01) |
| 가장 좁은 홈 매트 | 6-4 | 있음(임시) | MAT_G (D-02·D-03) |
| 가공 뒤 형상 | 테이프 띠·이음매 | 있음(임시) | TAPE_L·S·G, SEAM_L·S·G (D-06·D-07) |
| 떨어진 조각 | 0-8-4 ⑤ | 해당 없음 | machine.json workpiece_stages.fragments: 조각 없음(D-07) |
| 매트 평면 운동 모형 | 볼 위 X·Y·회전 | 있음 | J_WP_k_X·Y·ROT(k=L·S·G), 기계 축 아님(실행 규칙 20) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4
machine.json states 26개(앞 점검 22개 + 정비 머리판 탈착, 홈 매트 모서리 끝 테이프 위, THICK_6, THICK_16).

| 요구서 | 대응 상태 |
|---|---|
| 0-3 ① 올리고 시작 | 대기, 큰 매트 로딩 끝 |
| 0-3 ② 시작점·바인더 물림 | 큰/작은 매트 바퀴 내림(+ SEAM_U7 연구) |
| 0-3 ③ 외곽 봉제·회전 | 직선, 볼록 모서리 45°·90°, 홈 입구 회전, 홈 안 벽, 홈 바닥 꺾임(오목), 모서리 끝 테이프 위, THICK_6·16 |
| 0-3 ④ 이음매·절단 | 이음매 겹침 끝(L·S·G) |
| 0-3 ⑤ 배출 | 배출(L·S·G) |
| 6-4 오목 모서리(계단형) | 없음 — 홈 바닥 오목 반원만(앞 점검과 같음, 막지 않음) |

## 4. 바뀐 부품
없음(읽기만, save 0, 편집 0).

## 워크플로우 메모
- v2.3.4 저장본 문서 이름이 'merged'로 열린다(open 응답 name "merged"). 실행 규칙 2 "저장 전에 문서 이름을 새 버전 이름으로 바꾼다"가 합치기부 저장에서 빠졌다. 다음 모델링부가 저장 전 이름을 바꿔야 한다.
- `joint.list`·`motion.play` 응답이 커서(수십만~1천5백만 자) MCP 응답이 파일로 넘어갔다. motion.play 8번 묶음이 15 MB를 돌려줬다 — 요약만 받는 옵션이 있으면 좋겠다.
- 바디 이름(MAT_·TAPE_·SEAM_, STEP대기_ 56)은 열기 전 'merged' 문서의 document.inspect에서 셌다. 지시 (b)에 따르면 v2.3.4와 내용이 같다.
