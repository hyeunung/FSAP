# 전체 회귀 — 라운드 끝(M00, FSAP_v2.0.1) (2026-11-03)

요약
- **본 범위:** 연구 4개 전 단계 CYCLE_L 0~716 · CYCLE_S 0~450 · CYCLE_G1 0~514 · CYCLE_G2 0~630(2,313단계) + 기계 자세 171점(J_U5_X 0~1380 25 mm 간격 57점 × 조인트 묶음 3가지). **못 본 범위: 없음.**
- **어림 44 s / 실제 245 s**(전체 상한 1,800 s 안, 호출 끊김 0, 패닉 0, 뺀 단계 0). 실행기 regrun, 5묶음 병렬.
- **판정: 동작 문제 0 → pass.** 기준선(M-08) 밖 새 겹침 0, truncated 0, 행정 막힘 0(자세 구동 접촉 정지 0, J_U5_X 1380 끝까지 감), 매트 통로 막힘 0.
- 바꾸지 않은 부품 12개(매트·테이프·이음매 9, 바퀴 2, REF 1): v2.0.0 → v2.0.1 bbox 차 0.0000 mm, 부피 차 0, 표시 같음, 재질 Default 같음.
- 기록(디테일): 바퀴 타이어 ↔ 테이프 띠·이음매 겹침 깊이 최대 1.00 mm(테이프 두께), 부피 최대 307 mm³ — 7쌍 208단계. 같은 쌍 46단계는 커널이 교차 계산을 못 해 unchecked(옆 단계는 1.0 mm로 재짐). M02·M03가 판정(요구서 7절).
- 떨어지는 조각 없음(machine.json workpiece_stages.fragments) — 빠져나감 검사 대상 없음.
- 원장 갱신: `ledger.py commit` — regression, state:CYCLE_L/S/G1/G2 전 구간, pose:J_U5_X_0-1380x3.

## 근거 규칙
- E-03: "라운드 끝 = 전체 사이클 간섭 0". 대상 모형은 요구서 0-2 크기 범위 양 끝(1500×1500, 300×200)과 가장 좁은 홈 매트.
- E-17 전체 회귀 실행 절차(WF-153): 시험 → 어림 → 호출 8분 → 오류 즉시 → 전체 상한 30분. regrun.py run으로 돌렸다.
- 요구서 6-4: "이송 행정(X·Y) 25 mm, 원판 회전 5°, 바늘 둘레 반경 50 mm 안·홈 안·모서리 회전 구간은 5 mm·1°, 짧은 행정(노루발·바늘 등 15 mm 이하)은 양 끝 + 가운데. 전체 회귀 상한 30분".
- M-08: 의도된 겹침은 기준선으로 적고 뺀다(machine.json baseline_overlaps).
- E-04: 오래 걸리는 계산은 늘 CLI, 앱(MCP)에서 돌리지 않는다. 이번 부서는 MCP를 쓰지 않았다(앱 문서 열지 않음, 원복할 것 없음 — 안내서 '원복' "읽기 부서가 CLI로만 쟀다면 원복할 것이 없다").

## 1. 검사 범위와 간격

| 묶음 | 종류 | 범위 | 간격(요구서 6-4) | 대상 바디 |
|---|---|---|---|---|
| CYCLE_L | 연구 | 0~716 (717) | 연구에 이미 6-4 간격으로 키를 둠(이송 25 mm, 홈·바늘 둘레 5 mm, 회전 1°) | 기계 34 + MAT_L·TAPE_L·SEAM_L |
| CYCLE_S | 연구 | 0~450 (451) | 같음 | 기계 34 + MAT_S·TAPE_S·SEAM_S |
| CYCLE_G1 | 연구 | 0~514 (515) | 같음 | 기계 34 + MAT_G·TAPE_G·SEAM_G |
| CYCLE_G2 | 연구 | 0~630 (631) | 같음 | 기계 34 + MAT_G·TAPE_G·SEAM_G |
| POSE | 자세 | 0~170 (171) | J_U5_X 0~1380 25 mm(57점), LIFT·PRESS·PRESSER·NEEDLE 짧은 행정 양 끝 + 가운데(모두 내림 0·0·0·−30 / 가운데 15·15·10·−15 / 모두 들림 30·30·20·0) | 기계 34 |

- 사이클 상태(0-3 ①~⑤, 6-4 직선·볼록 모서리·홈 입구·홈 바닥 꺾임·시작·끝 이음매)는 연구 단계 안에 다 있다(machine.json states). 6-4 '오목 모서리(계단형)'는 매트 모형에 없다(준비부 기록 그대로, 홈 바닥 반원만).
- 가공 전 → 가공 뒤: 테이프 띠·이음매를 처음부터 넣은 보수적 모형(workpiece_stages). 조각 없음.
- 회전 J_U4_WHEEL_ROT·J_U5_WHEEL_ROT는 형상이 바뀌지 않는 회전이라 연구 값 그대로(따로 쓸지 않음).
- 한 연구에서는 그 매트 3바디만 넣었다(나머지 두 장은 로딩 자리에 겹쳐 둔 모형, 기준선).

## 2. 실행(regrun)

- 명세 `tools/out/mech_regrun/spec.json`, 묶음 실행기 `tools/out/mech_regrun/chunk.py`(단계마다 motion.play 또는 joint.drive → inspect.interference budget_s 120), 결과 `tools/out/mech_regrun/runs/regrun.json`, 분석 `analyze.py` → `analysis.json`.
- 시험: 자세 5점 1.0 s(점당 0.143 s), 연구 20단계 2.0 s(단계당 0.085 s). 오류 없음.
- 본 실행: POSE 5~170 15.1 s, CYCLE_L 20~716 172.2 s, CYCLE_G1 189.2 s, CYCLE_G2 200.2 s, CYCLE_S 243.2 s — 모두 ok.
- 파일 열기: 저장본 복사본 `base.sc`(sha1 43d19b1… 원본과 같음) 163 KB, CLI 호출마다 1번 — 시험 2 + 본 5 = 7번.

## 3. 결과

| 항목 | 값 |
|---|---|
| 기준선 밖 새 겹침 | 0 |
| truncated·budget_exceeded | 0 |
| 자세 구동 접촉 정지 | 0 (joint.drive 855회, J_U5_X 0~1380 57값 다 감) |
| 연구 unmoved | 0 |
| 기준선 겹침(뺀 것) | 같은 매트 MAT↔TAPE↔SEAM 2,314건, 바늘 U3_NEEDLE_PIN↔매트·테이프 2,970건 |
| unchecked | 46 — 모두 U4_WHEEL_TIRE↔TAPE_*(CYCLE_S 23, G2 16, L 6, G1 1) |

바퀴 ↔ 테이프 겹침(디테일 기록, M-08 기준선 후보 — machine.json "바퀴가 이미 박은 테이프 띠·이음매 위를 지날 때 깊이 1.0 mm"):

| 연구 | 쌍 | 단계 수 | 부피 최대 mm³ | 깊이(Z) 최대 mm | 단계 구간(앞 몇) |
|---|---|---|---|---|---|
| CYCLE_L | U4_WHEEL_TIRE↔TAPE_L | 31 | 307.2 | 1.002 | 159~161, 248, 316~328, 542~555 |
| CYCLE_L | U5_WHEEL_TIRE↔TAPE_L | 3 | 206.9 | 1.0 | 326~328 |
| CYCLE_S | U4_WHEEL_TIRE↔TAPE_S | 105 | 250.5 | 1.0 | 20~22, 24~35, 99~104, 126~132, 135~141, 205~220 … |
| CYCLE_S | U4_WHEEL_TIRE↔SEAM_S | 38 | 151.1 | 1.0 | 96~115, 333~350 |
| CYCLE_G1 | U4_WHEEL_TIRE↔TAPE_G | 11 | 88.3 | 0.96 | 99~100, 432~434, 499~504 |
| CYCLE_G2 | U4_WHEEL_TIRE↔TAPE_G | 16 | 250.4 | 1.0 | 3~4, 40~41, 184, 255, 454~462, 540 |
| CYCLE_G2 | U5_WHEEL_TIRE↔TAPE_G | 4 | 207.0 | 1.0 | 120~122, 315 |

- 깊이가 모두 테이프 두께 1 mm 안이다(바퀴 밑 Z 10 = 매트 윗면, 테이프 띠 Z 10~11). 기계 부품끼리·기계↔매트 몸통 겹침은 0. 바퀴가 테이프 위를 눌러도 되는지는 모델로 판정하지 않는다(CLAUDE.md, 요구서 7절) — M02·M03가 판정하고 기준선을 '부피 0'에서 '깊이 ≤ 1 mm'로 고칠지 정한다.
- unchecked 46은 같은 쌍의 메시 면이 2.6~2.9 mm 넘게 지나쳐 정확 교차를 못 한 것. 앞뒤 단계에서 같은 쌍이 깊이 1.0 mm로 재졌고 바퀴·테이프 형상이 같으므로 같은 접촉으로 본다.

## 4. 저장 전후 비교(바꾸지 않은 부품, WF-044)

`document.inspect {measure:true}`로 FSAP_v2.0.0·v2.0.1을 각각 CLI로 쟀다(`tools/out/mech_regrun/di_2.0.0.json`·`di_2.0.1.json`, `compare.json`).
- v2.0.0 12바디 → v2.0.1 44바디. 새로 32(U1~U8 차지 공간 상자, M00), 없어짐 0.
- 같이 있는 12바디(MAT·TAPE·SEAM ×3, U4_WHEEL_TIRE, U5_WHEEL_TIRE, REF_NEEDLE_AXIS_MARK): bbox 차 최대 0.0000 mm, 부피 차 0, visible 같음. 재질 44바디 모두 Default(signatures.json, 바뀜 없음). v2.0.1 문서 이름 FSAP_v2.0.1, dirty false.
- 결과: 엉뚱하게 움직인 부품 없음.

## 5. 원장

- `ledger.py sigcheck` → reuse(문서·해시 같음, 44부품). 측정 다시 하지 않음.
- `ledger.py commit --passed regression state:CYCLE_L:0-716 state:CYCLE_S:0-450 state:CYCLE_G1:0-514 state:CYCLE_G2:0-630 pose:J_U5_X_0-1380x3` → 부품 44, 통과 항목 6.

## 워크플로우 메모

- regrun 어림 44 s가 실제 245 s의 1/5 남짓이었다. 시험은 2묶음 병렬(단계당 0.085 s)인데 본 실행은 5묶음 병렬이라 묶음마다 단계당 약 0.25~0.54 s로 늘었다(작은 파일에서도 CLI 병렬 경쟁). 시험 병렬 수를 본 실행 병렬 수에 맞추면 어림이 맞을 것이다(이번엔 상한 1,800 s에 한참 못 미쳐 영향 없음).
- `motion.interference`에 단계 범위 인자가 없어 regrun의 {first}·{last} 묶음과 맞지 않는다. 단계마다 motion.play + inspect.interference 스크립트를 만드는 묶음 실행기(chunk.py)로 했다. 엔진 안내서에 이 묶음 실행기 틀이 있으면 다음 부서가 다시 짜지 않아도 된다.
