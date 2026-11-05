# 모델링부(회귀 수정) — REG-01-X1 CYCLE_G1 먼 쪽 바퀴 트레드·테이프 겹침 (v2.5.7 → v2.5.8)

## 요약
- 바뀐 것: 동작 연구 CYCLE_G1의 J_U5_LIFT 키 하나. `[320,0]` → `[318,0],[319,1],[320,1]`(321은 30 그대로). 형상·조인트·구매품·컴포넌트 변화 0.
- 결과: 318·319·320·321단계 P_M03_WHEEL_TREAD·P_M03_WHEEL ↔ TAPE_G·MAT_G·SEAM_G 겹침 0(고치기 전 320단계 0.4 mm, 1.352 mm³).
- 다른 키 16개·다른 연구는 고치기 전과 같음(차 1e-6 안, 아래 2절).
- 저장: `3D_Modeling/FSAP_v2.5.8.sc`(MCP save {path}), 앱 제목 `FSAP_v2.5.8`, `tools/config.json` doc 갱신, 서명 sigpatch(바뀐 바디 0).
- 통로: MCP(앱 127.0.0.1:27878 켜져 있음, running 응답 빈 큐).
- 미완: 없음. 전체 사이클 간섭은 라운드 끝 회귀(REG-01 묶음 spec_v258_*)가 본다.

## 1. 원인과 고침
- 원인: CYCLE_G1에서 먼 쪽 대차가 바퀴를 내린 채(J_U5_LIFT 0) 320단계까지 가다가 321단계에 30으로 들린다. 320단계에서 매트 회전·이송(J_WP_G_X 280.498, J_WP_G_Y 740.092)으로 테이프 윗면이 트레드 밑으로 들어와 0.4 mm 겹쳤다(tools/out/mech_regrun3/analysis.json).
- 고침(REG-01 설계안 `mech_REG-01_design2.md` 3절 키 그대로): 319·320단계에 바퀴를 1 mm 띄운다. 176~184단계에서 이미 쓰는 1 mm 띄움과 같은 방식이다. 1 mm는 J_U5_LIFT 한계 [−10, 30] 안이고, 320→321 사이에 원래도 지나던 0~30 범위 안이라 새로 쓸어 가는 공간이 없다.
- 형상 변경 없음, 실행 규칙 "문제마다 원인을 고친다. 그 밖은 건드리지 않는다"대로 키 하나만.

## 2. 한 일(MCP, 파일 한 번 open)
1. `open` v2.5.7(errors 0, 피처 1,978). 앞 실행의 'merged' 문서와 다른 경로를 디스크에서 새로 읽었다. `inspect_design`은 결과가 커서 부르지 않았고, open 직후라 편집 없음으로 봤다.
2. `edit.checkpoint` → `motion.study {study:CYCLE_G1, keys:[J_U5_LIFT만]}` 1차 시도: **키를 통째로 바꿔 나머지 16개가 지워짐**(gen_v2_m06.py 주석과 같은 실측). `edit.restore_checkpoint`는 "no checkpoint 2"로 거부되어 `undo` 2번으로 되돌리고, `motion.list`로 17개 키가 v2.5.7과 같은지 확인했다.
3. 17개 키 전체를 다시 넣음. motion.list는 회전 값을 라디안으로 주고 motion.study는 도로 받으므로(WF-117) 회전 조인트 47·50·84·99·114·270은 ×180/π. 명령 기록 `tools/out/mech_regfix/edit.json`(CLI로 다시 만들 수 있음).
4. 확인: 고친 뒤 `motion.list`(`tools/out/mech_regfix/studies_after.json`)와 고치기 전(`cycle_g1_v257_live.json`)을 비교 — 연구 이름 같음, CYCLE_G1 외 연구 차 0, CYCLE_G1 키 16개 최대 차 ≤ 1e-6, J_U5_LIFT만 12점 → 14점.
5. 318~321단계 `inspect.clearance` 겹침 0(`tools/out/mech_regfix/clearance_318_321.json`).
6. `component.rename {component:0, name:FSAP_v2.5.8}` → `browser.visibility {visible:false, folder:"joints"}`(실행 규칙 19) → `motion.play REST 0` → `save {path: 3D_Modeling/FSAP_v2.5.8.sc}`. 저장 뒤 편집 없음.

## 3. 저장 전 검사
| 항목 | 결과 |
|---|---|
| 겹침(바뀐 범위 318~321) | 0 |
| 숨김 | 조인트 글리프 숨김. 숨긴 바디는 매트 모형 MAT·TAPE·SEAM 9개(기존 의도, C-31) |
| 리지드 그룹·재질 | 바뀐 바디 없음 — 해당 없음 |
| 볼트·강도·임시 STEP | 새로 만들거나 옮긴 부품 없음 — 해당 없음, exported_steps 없음 |

## 4. 번호(E-05)
- 새로 생기거나 없어진 컴포넌트 없음 → 마지막 자리 +1: v2.5.7 → v2.5.8.

## 5. 규칙 근거
| 규칙 | 원문 | 판정 |
|---|---|---|
| E-03 | 합격은 동작·간섭 | 바뀐 단계 겹침 0 |
| E-15 | 움직임은 기계 정의의 조인트로만 만든다 | 기존 조인트 J_U5_LIFT 키만 바꿈 |
| 실행 규칙 2 | `save {}`(덮어쓰기)는 쓰지 않는다 | `save {path: v2.5.8}` |
| 실행 규칙 3 | 형상이 바뀌면 항상 새 번호로 저장 | 새 번호 v2.5.8, config doc 갱신 |

## 워크플로우 메모
- `motion.study {study}`가 keys를 통째로 바꾸는 것을 지시문(키 하나 바꾸기)이 모르고 냈다. 회귀 수정 지시에 "다른 키를 모두 다시 넣고 회전은 도로" 한 줄이 있으면 1차 시도·되돌리기가 없어진다.
- `edit.checkpoint`를 batch 안에서 만들면 다음 execute에서 `edit.restore_checkpoint`가 "no checkpoint"로 거부됐다. undo로는 되돌아갔다.
