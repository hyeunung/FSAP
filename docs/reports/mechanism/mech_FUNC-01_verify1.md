# FUNC-01 검도·체결 수정 1회차 — v2.8.1 (옆판 축 여유 구멍)

## 요약 (10줄)
- 대상: `3D_Modeling/FSAP_v2.8.1.sc`. 바뀐 부품 `U5_FLOAT/P_M03_LIFT_SIDE_N`·`P_M03_LIFT_SIDE_P`(ledger scope: 바뀜 2, 새로 0, 없어짐 0, 이웃 19)
- 지난 동작 문제(축 PSFJ16-150_F01_N/P ↔ 옆판 웹 2 mm 파고듦)는 **해소**: 옆판 P에 원통면 r 8.25(면 39, 중심 (−1847, 43), 축 Z, 중심 Z 122.5, 넓이 186.1 mm²)가 생겨 Z 115~130을 덮는다. 축 r 8 → 반지름 틈 0.25
- REST에서 skip_within null로 옆판 N·P ↔ 축·받침 블록·LHFR16: 겹침 0, unchecked 0(지난번엔 동축이라 unchecked였음). 맞닿음 0은 블록 윗면 Z 116, 축↔플랜지 구멍 시작 모서리 Z 130(H7 끼움, 의도)
- 과제 범위 자세 J_U5_LIFT {−10, 30} × J_U5_FLOAT {0, 20} 4자세: 겹침 0, unchecked 0. FLOAT 20의 옆판↔P_M03_LIFT_TOP 맞닿음 0은 위 기계 정지(의도)
- 깎기만 한 변경이라 새 겹침이 생길 수 없다(재료 제거). 새·옮긴 볼트 0, 판금 아님, 리지드 그룹 변화 없음
- 동작 문제 0 → pass. 원장 갱신(부품 2729, 통과 항목 53)
- 디테일: 웹 6 → 3.75 남음(강도 손계산은 디테일 단계, 하중은 축이 받침 블록·플랜지로 받음 — 웹은 하중 경로 아님)
- 미완: 없음(과제 범위). 전체 사이클은 라운드 끝 회귀가 본다

## 1. 통로·시간
| 항목 | 값 |
|---|---|
| 통로 | MCP. `running` 빈 목록 확인 뒤 `open` v2.8.1 1회(피처 2,303, 오류 0) |
| 호출 | open 1, batch 5(실패 2: restore_checkpoint id 소실 — 포즈만 바뀌어 `motion.play REST 0`으로 원복), body_topology 1 |
| 원복 | 저장 없음. 끝에 `motion.play REST step 0` 성공 |

## 2. 지난 문제 확인
| 항목 | v2.8.0 | v2.8.1 |
|---|---|---|
| 옆판 P 축 구멍 면 | r 8, Z 129~136뿐 | r 8(Z 130~136 플랜지 H7) + **r 8.25 Z 115~130**(면 39) |
| 축 ↔ 옆판 웹 | 활꼴 약 185 mm³/쪽 겹침 | 반지름 틈 0.25, 겹침 0 |
| clearance REST(skip null) | unchecked(동축) | overlaps 0, unchecked 0 |

원본: `tools/out/mech_FUNC-01/fix1/topo_side_P_v281.json`(옆판 P 위상).

## 3. 과제 범위 동작 검사 (E-03·E-17)
bodies 옆판 N·P, against U5 이웃(케이블 베어 링크·대차판·MGPM25·PGX62·HG-KR23·CB5/CB6·LIFT_TOP·FRONT·블록·LHFR16·축·PSCS16·스프링·시트) + P_M04_PANEL_E2 + MAT_L·G·S, 틈 0.5.

| J_U5_LIFT | J_U5_FLOAT | 겹침 | 0.5 안 | unchecked |
|---|---|---|---|---|
| REST | REST | 0 | 블록 Z 116·축 Z 130 맞닿음 0(의도) | 0 |
| −10 | 0 | 0 | 없음 | 0 |
| −10 | 20 | 0 | 옆판↔LIFT_TOP 0(기계 정지) | 0 |
| 30 | 20 | 0 | 옆판↔LIFT_TOP 0(기계 정지) | 0 |
| 30 | 0 | 0 | 없음 | 0 |

옆판·축·블록은 모두 U5_FLOAT 안이라 J_U5_FLOAT·LIFT로 상대 위치가 바뀌지 않는다. J_U5_X는 유닛 전체를 옮겨 이웃과의 상대 위치가 같다(라운드 끝 회귀 범위).

## 4. 체결·판금
새·옮긴 볼트 없음(M-01 대상 0), 공압 포트 변화 없음(M-06), 판금 아님(M-04 대상 아님), 리지드 그룹 누락 없음(E-11).

## 5. 판정
- 동작 문제 0 → pass
- 완료 판정: 과제 범위 간섭 0은 이번 수정 범위에서 충족. ①~⑦ 손계산·바인더 형상·좁은 홈 폭은 앞 검도(mech_FUNC-01_verify.md)·계산서(mech_FUNC-01_calc.md)에서 이미 본 것으로, 이번 변경(옆판 구멍)과 무관해 다시 보지 않았다
- 등급 M 맞음(새 구매품·조인트 변화 없음)
- 원장 `ledger.py commit --date 2026-11-08` 완료

## 워크플로우 메모
- `edit.checkpoint` id(113)가 같은 세션의 다음 batch 뒤 `restore_checkpoint`에서 "no checkpoint"로 사라졌다. 포즈만 바꾼 읽기 부서는 `motion.play` step 0으로 원복하면 충분했다.
- `motion.play`를 batch에 넣으면 응답이 1.2 MB가 된다(verbose false여도). 읽기 부서는 motion.play를 단독 호출로 빼는 편이 낫다.
