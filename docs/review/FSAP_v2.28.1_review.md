# FSAP v2.28.1 설계검토서 — 구동 전체 회귀 수정 (2026-11-24)

## 요약
- 저장본 `3D_Modeling/FSAP_v2.28.1.sc`(앞 v2.28.0). 형상 변경 0, 컴포넌트 증감 0 → 마지막 자리 +1(E-05 "아니면 마지막 자리 +1").
- BOM `docs/bom/FSAP_v2.28.1_made.csv`·`_purchased.csv` = v2.28.0과 같음(바디 변경 없음).
- 다시 돌린 전체 회귀(`mech_regression2_2.md`): **판정 못 함** — 메모리 부족(커밋 여유 6.1 GB < 헤드리스 세션 약 11.8 GB, 앱 pid 40328 커밋 68.4 GB)으로 한 단계도 돌리지 못함. 완료 기준 미충족.
- 미완: 전체 회귀(상태 61 + 연구 15개 + FAST), machine.json J_U4S_SLOT 정리, 서명표 갱신.

## 바꾼 것 (전 → 후 · 이유)
| 항목 | 전(v2.28.0) | 후(v2.28.1) | 이유 |
|---|---|---|---|
| J_U7_HGT 저장 값 | 6.0 | 0.0 | 대기값(machine.json rest 0)과 달라 U7_FIXED + U6 묶음 48바디가 Z +6에 저장됨 |
| REST 연구 키 | J_U7_HGT 등 없음 | J_U7_HGT·J_U4_X·J_U2_FLAP·LATCH_A·B 대기 상수 키 5개 추가 | 안내서 '동작 상태 초기화' "저장 전에는 항상 이 포즈로 돌려놓는다" — REST 0이 HGT를 되돌리지 못했음 |
| CYCLE_* 10개 연구 키 | 새 대기 조인트 키 없음 | 위 5 + J_U4_STOP·J_U7_KIT_T06·T10·T16·J_WP_T06·T10·T16_Z 대기 상수 12개씩 | RX-DC-01-D1(THICK 상태 뒤 모형이 −3000에 남음) 해소 |

## 확인 (수치)
- REST 0 재생 뒤 조인트 679개 값 = v2.28.0 저장값(HGT만 0). joint.list floating 0·conflicts 0·errors 0, rest 245개 일치.
- REST 0 전수 measure 3,777바디: 과제 밖 변화 0.
- 되돌린 48바디 둘레 새 겹침 0. 기준선 1쌍(TU0604_M08P_U6 ↔ TU0604_M08P_U6_L 113.1 mm³)은 v2.25.2와 같은 자리.

## 남은 문제 (전체 회귀 결과)
| 종류 | 무엇 | 고칠 방법 | 외부 |
|---|---|---|---|
| 디테일 | 전체 회귀 한 단계도 못 돌림(메모리 부족) — 상태 61·연구 15개(627점)·FAST 61점 못 봄 | 사용자가 SolidCraft 앱을 닫거나 다시 켠 뒤(커밋 여유 ≥ 약 25 GB) `tools/out/mech_regrun/reg26/spec26.json`으로 regrun.py run | 예(사용자) |
| 디테일 | machine.json `J_U4S_SLOT`(RX-19 기록용 장공)이 CAD 조인트에 없음 | machine.json에서 빼거나 기록용 표시 | 아니오 |
| 디테일 | 서명표가 v2.28.0 것(sigcheck full) | 다음 회귀가 v2.28.1 measure로 sigpatch | 아니오 |

강도·FEA: 해당 없음(형상·하중 경로 변경 0, E-18).
