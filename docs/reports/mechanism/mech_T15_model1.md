# 구동 T15 모델링 수정 1회차 — J_T05_PAD joint.sweep 판정 (v0.8.1 그대로)

요약(10줄)
- 지난 문제: joint.sweep J_T05_PAD −13.5→0이 "contact sweep collision budget" 초과로 거부, sweep 결과 없음.
- 원인: 상대 집합 `T05:1`이 하위 occurrence 전부(CJ2B10 STEP 바디·볼트 CB5/MBIS5·PSFJ 축·T05_PAD 자신)를 품어 접촉 예산을 넘는다. step·구간을 줄여도(0.1 mm, 0.5 mm 구간) 같은 거부 → 형상 문제가 아니라 검사 집합 문제.
- 해결: 저장하지 않는 임시 분리(`component.from_bodies [P_T05_GUIDE]` → 상대 `P_T05_GUIDE:1`)로 상대를 안내 블록 하나로 좁히고, 2 mm 구간으로 나눠 sweep. 끝나고 undo로 되돌림.
- 결과: −12.5→0 전 구간 막힘 없음(stopped_by null), 최소 틈 0.30(J 0에서 메시 0.295, 메시 오차 0.107 안). −12.5→−13.5는 −13.494에서 받침면 Z 42와 맞닿아 멈춤 = 행정 끝 스토퍼(−13.5, refine 0.01 안).
- 움직인 집합 `T05_PAD:1` = P_T05_PAD + CJ2B10-15Z_T05_ROD + NTJ ×2(유닛 부품 전부, occurrence.properties 확인).
- 형상·조인트·체결 변경 0. 새 버전 저장 없음(v0.8.1 그대로, tools/config.json doc 그대로). 커밋 없음(규칙 4: 새 .sc 없음).
- 미완 0. 디테일 d1~d4는 지난 보고서(mech_T15_model.md) 그대로 기록만.

## 1. 통로·문서
- MCP(앱 실행 중, `running` 응답 정상, 열린 문서 dirty false·path null 확인 뒤 `open FSAP_v0.8.1.sc` errors 0).
- 시작 `motion.play {study:"대기", step:0}`. 끝 `motion.play 대기 0` + `joint.drive J_T05_PAD −12.5`, 패드 ↔ 안내 0.30 확인.
- 임시 분리는 `undo`("Create Components from Bodies")로 되돌렸고 save하지 않았다. 파일 FSAP_v0.8.1.sc 수정 시각 05:07:41 그대로(이번 작업 전). `save {}` 안 씀.
- 참고: 같은 경로 `open`은 앱의 현재 설계를 버리지 않았다(features 1665→1666 유지). 되돌림은 undo로 했다.

## 2. 거부 재현(CLI, 저장본 v0.8.1)
| 시도 | 결과 |
|---|---|
| T05_PAD:1 vs T05:1, step 0.1 / 0.25, −13.5→0 | 예산 초과 |
| 같은 쌍, −12.5→−11.5 (1 mm) | 예산 초과 |
| occurrences [T05_PAD:1, T05:1] | 예산 초과 |
| contact.create [T05_PAD:1, T05:1] + contact_sets | 예산 초과 |
| (앱) 350 vs 356(T05_TAPE:1) | 통과 → 움직이는 쪽은 문제 없음 |
| (앱) 350 vs 289 (id) | 예산 초과 |
| (앱) 350 vs P_T05_GUIDE:1 (임시 분리), −13.5→0 한 번에 | 예산 초과 |
| (앱) 350 vs P_T05_GUIDE:1, 2 mm 구간 | 통과 |

스크립트·출력: tools/out/mech_T15/sw_*.json, v1~v3.json, *_res.txt.

## 3. joint.sweep 결과 (J_T05_PAD, 상대 P_T05_GUIDE:1, step 0.25 / 끝 구간 0.1, refine 0.01)
| 구간 | stopped_by | 최소 틈 mm |
|---|---|---|
| −12.5 → −10.5 | 없음 | 0.300 (전 샘플) |
| −10.5 → −8.5 | 없음 | — |
| −8.5 → −6.5 | 없음 | — |
| −6.5 → −4.5 | 없음 | — |
| −4.5 → −2.5 | 없음 | — |
| −2.5 → 0 | 없음 | 0.300, J 0에서 0.295(메시, 정확값 0.30 = C2 ↔ 천장 뿌리 R3) |
| −12.5 → −13.5 | −13.494에서 받침면 (−140.9, 582.5, 42.0) | −13.3 0.2, −13.4 0.1 → 행정 끝 스토퍼 |

판정: 패드(로드·너트 포함)는 전 행정에서 안내 블록에 막히지 않고, 행정 끝 −13.5는 받침면이 스토퍼다(E-15 조인트 자기 점검). 지난 회차 10자세 drive+clearance 결과(0.3/0.3/0.0)와 같다.
로드 ↔ 천장 로드 구멍 Ø6: inspect.clearance 1.0(반경 틈, 로드가 Z로만 움직여 행정 내내 같음).

## 4. 지시서 [4] 나머지 항목
(a)~(d)·(f)는 지난 회차(mech_T15_model.md) 결과 그대로 유효하다(형상 변경 없음): 스패너 판 21×4 7각도 겹침 0, 포트 상자 0.5, 정적 간섭 0(truncated false, unchecked 기준선 8쌍), 앞벽 오조작B 손계산 SF 3.80 ≥ 2. 임시 STEP은 지난 회차 tools/out/mech_T15/stepout/ 그대로(형상 같음).

## 워크플로우 메모
- joint.sweep 상대로 STEP·볼트 하위 occurrence를 많이 품은 부모 occurrence를 주면 접촉 예산을 넘는다. 바디 단위 상대 지정이 없으므로, 대상 바디를 저장하지 않는 임시 분리(component.from_bodies) 후 2 mm 구간으로 나눠 돌리면 통과한다. 되돌림은 undo(같은 경로 open은 현재 설계를 버리지 않음).
