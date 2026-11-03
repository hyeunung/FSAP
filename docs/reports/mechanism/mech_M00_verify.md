# 검도·체결 — M00 전체 골격 (2026-11-03)

요약
- 대상: `3D_Modeling/FSAP_v2.0.1.sc`(config doc 일치, 문서 이름 FSAP_v2.0.1, 44바디, dirty false). 새 상자 32개(U1~U8), 바뀐 조인트 J_U5_X 0~1380.
- 통로: MCP(앱 켜짐, 그 시각 CAD 쓰는 부서 하나). 저장본 `open` 1번, 저장 안 함. 끝에 REST step 0, dirty false·undo 0 확인.
- 판정: 동작 문제 0 → pass. 과제 범위 간섭(바퀴·바늘·매트 기준선 밖) 0, truncated 0.
- 매트 연구 4개 × 행정 0·25·50·75·100 % = 21점(CYCLE_L 358 포함), 기계 조인트 자세 9점, J_U5_X 0→1380 sweep(25 mm) stopped_at null.
- 최소 틈(J_U5_X 1380, 모두 내림): U4↔U5 27.5 mm(U4_MOUNT·U4_HOLDER·U4_DRIVE ↔ U5_CARRIAGE·U5_HOLDER·U5_WHEEL_TIRE), U1_BEAM↔U5_CARRIAGE 22.0, 바퀴 밑 Z 10.
- 기록(디테일): 바퀴↔테이프 띠·이음매 겹침 87~234 mm³(깊이 최대 2 mm). machine.json 기준선의 '부피 0'과 다름 → 판정 기억에 남김, M02·M03가 판정.
- 새 볼트·판금·포트 없음. 리지드 그룹 누락 없음(joint.list floating []).
- 미완: 전체 사이클 간섭은 라운드 끝 회귀(E-03).

## 근거 규칙
- E-03 "과제 안 = 과제 범위 간섭 0 … 라운드 끝 = 전체 사이클 간섭 0".
- E-17 과제 안 검사: 관련 조인트를 행정 0·25·50·75·100 %에 놓고 잰다. 전체 사이클은 돌지 않는다.
- M-08 의도된 겹침은 기준선으로 적고 뺀다.
- E-02 볼트·두께·강도는 디테일로 기록만.

## 0. 범위(ledger.py scope --joints-changed)
전체 검사 예(조인트·행정·배치 바뀜, 여러 유닛). 새로 32, 바뀜 0, 없어짐 0, 이웃 7. 작업 대상 길에 닿는 부품(U2_PLATE·U2_SUB·U3_HANGER·U3_LOWER_DRIVE·U3_LOWER_POD)이 바뀌어 매트 모형 3장을 넣었다. 대상 바디: 기계 34바디(REF 제외, config skip_tops) + 연구마다 그 매트의 MAT·TAPE·SEAM 3바디. 모델 44바디 전부라 against 제한이 따로 필요 없었다(바디 수가 작아 inspect.interference 한 번 0.2~0.3 s).

## 1. 과제 범위 동작 검사 — 매트 연구 점

| 연구 | 단계(0·25·50·75·100 %) | 기준선 밖 겹침 | 기준선(M-08) |
|---|---|---|---|
| CYCLE_L (716) | 0·179·358·537·715 | 0 | MAT_L↔TAPE_L |
| CYCLE_S (450) | 0·112·225·337·449 | 0 | 바늘↔MAT_S 5.0·TAPE_S 22.1, U4_WHEEL_TIRE↔TAPE_S 234.3·SEAM_S 150.0/149.4 (112·337) |
| CYCLE_G1 (514) | 0·128·257·385·513 | 0 | 바늘↔MAT_G 5.0~10.2·TAPE_G 22.1 |
| CYCLE_G2 (630) | 0·157·315·472·629 | 0 | 바늘↔MAT_G·TAPE_G, U5_WHEEL_TIRE↔TAPE_G 87.3 (315) |

- 모든 점 truncated false, budget_exceeded false. CYCLE_S 112의 U4_WHEEL_TIRE↔TAPE_S 한 쌍은 unchecked("facets pass through … could not be intersected") — 337에서 같은 쌍이 234.3 mm³로 재졌다. 같은 겹침으로 본다.
- 매트가 기둥·라이트 커튼·HMI·대차에 닿은 점 없음. 휘두름 합집합 계산(측정 3절, donecheck)은 모델링 측 계산 그대로이고 연속 사이클은 라운드 끝 회귀가 본다.
- 결과: `tools/out/mech_M00_verify/L.json·S.json·G1.json·G2.json`.

## 2. 이웃 유닛 조인트 점 — 기계 자세

| 자세 | J_U5_X | LIFT·PRESS·PRESSER·NEEDLE | 겹침 |
|---|---|---|---|
| 모두 내림 | 0·345·690·1035·1380 | 0·0·0·−30 | 0 (5점) |
| 중간 | 1380 | 15·15·10·−15 | 0 |
| 모두 올림 | 1380·0 | 30·30·20·0 | 0 (2점) |
| sweep | 0→1380, 25 mm | 올림 | stopped_at null, stopped_by null |

J_U5_X 1380(모두 내림)의 inspect.clearance(U5 4바디 ↔ U4·U2·U1_BEAM·U5_RAIL, 200 mm 안):
- U5_RAIL↔U5_CARRIAGE 2.0(같은 유닛 안내, 의도)
- U2_PLATE↔U5_WHEEL_TIRE 10.0(바퀴 밑 Z 10 = 매트 두께)
- U1_BEAM↔U5_CARRIAGE 22.0
- U4_DRIVE↔U5_WHEEL_TIRE 27.5, U4_MOUNT↔U5_CARRIAGE 27.5, U4_HOLDER↔U5_HOLDER 27.5
- U2_PLATE↔U5_DRIVE 30.0(내림 때 대차 구동 밑면 Z 30)
대차 X 행정 끝에서 U4 묶음과 27.5 mm 남는다(d₂ 하한 420, donecheck와 같음).

## 3. 볼트·리지드 그룹·포트
- 새로 넣거나 옮긴 볼트 없음(차지 공간 상자뿐). M-01 대상 없음.
- 리지드 그룹: joint.list floating [], errors []. 유닛 부품이 조인트를 따라 움직이는 것을 위 자세들의 positions로 확인(U4_PRESS·U4_WHEEL Z 30 이동, U5_CAR·U5_LIFT·U5_WHEEL X 이동).
- 공압 포트 없음(U8_REG는 자리 상자). M-06 대상 없음.

## 4. 판금
판금 부품 없음. M-04 대상 없음.

## 5. 판정 기억(paircache)
바퀴 2개 × {TAPE·SEAM}_{S,G,L} 12쌍을 `tools/out/judged.json`에 남겼다. 근거: 강체 바퀴(내림 Z 10 고정)가 이미 박은 테이프 띠(Z 10~11)·이음매(Z 11~12) 위를 지나는 의도된 접촉 후보(machine.json baseline_overlaps). 실제 바퀴는 공압 누름으로 타고 넘는다 — 요구서 7절 기록.

## 문제

| kind | 무엇 | 어디 | 수치 | 고치는 법 |
|---|---|---|---|---|
| 디테일 | 기준선 설명 '깊이 1.0 mm, 부피 0'이 실측과 다름 | machine.json baseline_overlaps(바퀴↔WP_TAPE_*) | U4 바퀴↔TAPE_S 234.3, ↔SEAM_S 150.0 mm³(깊이 2), U5 바퀴↔TAPE_G 87.3 mm³ | M02(U4)·M03(U5)에서 누름 조인트 J_U4_PRESS·J_U5_LIFT 내림 값을 접촉 추종(밑 물체 윗면 Z 10/11/12)으로 하거나, 기준선에 쌍·부피(≤ 250 mm³, 깊이 ≤ 2 mm)·이음매 포함을 적는다 |

동작 문제 없음.

## 완료 판정 대조

| 항목 | 이번 검도 | 판정 |
|---|---|---|
| 매트 3장 0-8-4 한 사이클 과제 범위 간섭 0 | 21점 기준선 밖 0 | 됨 |
| 휘두름 영역 안 U1 기둥 0개 | 매트 점에서 기둥 겹침 0, 틈 177.3·225.9(donecheck) | 됨 |
| 대차 행정이 1500 매트 d₂ 범위 덮음 | J_U5_X 0~1380 sweep 끝까지(d₂ 420~1800 ⊃ 420~1487.5) | 됨 |
| d₂ ≥ 2·d₁ + 묶음 폭 | 420 ≥ 300, 끝 틈 27.5 | 됨 |
| 보·윗헤드·대차 밑면 높이 | 보 250·대차 220(clearance로 U1_BEAM↔대차 22) | 됨 |
| 볼 윗면 = 바늘판 윗면 Z 0 | 바퀴↔U2_PLATE 틈 10.0 = 매트 두께, 매트 밑면 접촉 부피 0 | 됨 |
| 결정로그 기록 | M00-M01~M03(모델링부) | 됨 |
| FSAP_v2.0.1.sc 저장·config doc 일치 | config doc = ../3D_Modeling/FSAP_v2.0.1.sc, 열린 문서 이름 FSAP_v2.0.1 | 됨 |

등급 L 맞음(빈 설계에서 8유닛·조인트·연구 전부).

## 시간
약 400 s, CAD 호출 약 12(MCP), 설계 파일 열기 1, 브라우저 0. 원장 `ledger.py commit` 완료(부품 44).

## 워크플로우 메모
- motion.play 결과가 단계마다 positions 전체(약 7천 자)를 돌려줘 5점 묶음이 10만 자를 넘었다. 결과를 파일로 받아 `tools/out/mech_M00_verify/summ.py`로 요약했다. motion.play에 quiet 같은 짧은 결과 인자가 있으면 좋다.
- batch 안 joint.sweep이 "contact sweep sampling budget" 오류로 실패하면 rollback이 앞 단계를 되돌리면서 edit.checkpoint(585)도 사라졌다(restore 시 "no checkpoint"). sweep에는 `step`을 꼭 주고, 읽기 검사 batch는 rollback:false로 보낸다.
