# 검도·체결부 — N00 전체 골격(U1~U9) 검증 (2026-11-03, 엔진 v3.7.1)

## 요약(10줄)
- 대상: `3D_Modeling/FSAP_v1.0.1.sc`(문서 이름 FSAP_v1.0.1, 바디 36). 통로 MCP(앱 27878) — 열린 문서 dirty false 확인 뒤 저장본을 한 번 `open`, 저장 안 함. 끝에 `motion.play REST 0`, dirty false·undo 0 확인.
- 범위(E-17): `ledger.py scope --joints-changed` → 전체 검사(원장 비어 있음, 새로 36). 관련 조인트 5개 전부(J_U4_X·J_U4_Y·J_U3_ROT·J_U1_PRESSER·J_U1_NEEDLE).
- 과제 안 검사: 연구 5개의 0·25·50·75·100 % 25자세 + X·Y 행정 끝 자세 11 = **36자세**에서 `inspect.clearance`(틈 5 mm, skip_within component). 전체 사이클은 돌지 않음(라운드 끝 회귀 몫).
- 결과: **기준선 밖 새 겹침 0**, 자세 재생 막힘 0(unmoved·contact 0), truncated·unchecked 0. 남은 겹침은 기준선뿐(매트↔자기 테이프, 바늘 −30↔매트·테이프, REF 표시점↔U4_X_BEAM).
- 행정(0-8-5, ±5 %): 큰 매트 310.66×1500.0(+0.21 %·0 %), 작은 매트 80.27×300.0(+0.34 %·0 %), 홈 매트 G2 248.5×1200(120×120 행 대비 −0.59 %·0 %) — 모두 안.
- U2 다리 휘두름 영역 안: 0(작업면 위 다리는 U2_COLUMN 하나, 36자세에서 매트와 5 mm 안 접근 없음, 측정부 최소 187.5).
- 정한 치수 결정로그 기록 확인: N00-S02(기계 3150×3115×1580), S03(브리지 Z 125), S04(원판 r60·중심–바늘 최소 100), S05(작업면 900, D-79), M01.
- 볼트 새로 0, 포트 0, 판금 0. 리지드: `joint.list` floating []·conflicts []·errors [].
- 판정: **pass**(동작 문제 0). 디테일 1건(machine.json U3_ROT 바디 접두어). 등급 L 맞음.

## 1. 통로·절차
| 항목 | 내용 |
|---|---|
| 연결 | `running` 빈 큐, `document.inspect` 응답 → 앱 연결. 열린 문서 FSAP_v1.0.1, dirty false, undo 0, 타임라인 error·warning 모두 null |
| 열기 | `open 3D_Modeling/FSAP_v1.0.1.sc` 1번(features 86, errors 0) |
| 숨김 | 0(36바디 모두 visible true) |
| 검사 | `batch` 1번: `motion.play`(quiet) + `inspect.clearance` × 36자세, 끝에 `motion.play REST 0`. 합 30.0 s |
| 원복 | 저장 안 함. 마지막 REST step 0. 뒤에 `inspect_design` dirty false·undo 0·redo 0(체크포인트 217은 앱이 이미 비움 — 형상 변경이 없어 되돌릴 것 없음) |
| 파일 | `tools/out/mech_N00/verify/`: `points_raw.json`(원자료), `poses.json`, `extreme_steps.json`, `analyze.py` → `points_summary.json`, `stroke_check.json`, `judge.py` |

## 2. 과제 범위 동작 검사(E-03 과제 안, E-17)
자세(연구·단계): CYCLE_L 0·165·330·494·659 + 18·50·97·142(X·Y 끝), CYCLE_S 0·123·246·368·491 + 132·146, CYCLE_G1 0·120·239·358·478 + 142·354·413, CYCLE_G2 0·149·298·448·597 + 28·120, REWIND_EMPTY 0·18·36·54·72.
판정 방법: 그 연구에서 쓰는 매트(L·S·G)만 대상으로 넣고, 다른 매트는 뺐다(연구마다 한 장만 씀). REWIND_EMPTY는 빈 원판이라 매트를 뺐다.

| 구분 | 결과 |
|---|---|
| 기준선 밖 새 겹침(M-08) | **0** |
| 매트↔자기 테이프 | L 9·S 7·G 15자세(기준선, 감쌈) |
| U1_NEEDLE_PIN↔매트·테이프 | 바늘 −30 자세에서만(L 2·S 3·G 6, 기준선) |
| REF_NEEDLE_AXIS_MARK↔U4_X_BEAM | 6자세, 3.14 mm³(표시점, 기준선) |
| 가까운 쌍(> 0, 5 mm 안) | 1.0: 바늘·노루발↔U1_BUNDLE, 노루발↔U8, U1_UPPER·U6↔U8(고정끼리 1 mm 띄움), SEAM↔바늘·U8 / 1.2: 바늘↔U1_LOWER_POD(구멍)·노루발 / 2.0: 테이프↔U6·U8·노루발 / 3.0: 매트↔바늘 |
| 맞닿음 0 mm(부피 0) | U4_X_BEAM↔레일·기둥 4·U4_Y_CARR, U3_DRIVE↔U3_COLUMN, 매트↔원판·테이블(얹힘) — 의도된 받침면 |
| 대상 통로 | 매트가 헤드 밑을 지나는 길에서 고정 바디와 겹침 0. 노루발 들림(20) 중 회전 자세 겹침 0 |

## 3. 완료 판정 대조
| 판정 | 기준 | 측정 | 결과 |
|---|---|---|---|
| 매트 3장 한 사이클 과제 범위 간섭 0 | 기준선 밖 0 | 36자세 0(모델링부 CLI 전 단계 `motion.interference`도 기준선뿐) | 통과 |
| 원판 중심 행정 0-8-5 ±5 % | 310×1500, 80×300, 250×1200 | 310.66×1500.0, 80.27×300.0, 248.53×1200.0(봉제 구간 = 바늘 −30 단계) | 통과 |
| 휘두름 영역 안 U2 다리 0 | 0개 | U2_COLUMN(X 500~620, Y −520~−400)은 실제 휘두름 경로 밖(+X·−Y 빈 모서리, 측정부), 36자세 접근 없음 | 통과 |
| 정한 치수 결정로그 기록 | 기계 크기·브리지·원판–바늘·작업면 | N00-S02~S05, N00-M01 있음 | 통과 |

참고: U4 X 전체 행정 1373.2는 0-8-3 "X 약 0.5 m"보다 크다. 대기 자리 D-78·홈 매트 넘김 탓이며 결정로그 N00-S06에 이미 있다(판정 항목 아님).

## 4. 볼트·리지드·포트·판금
- 새로 넣거나 옮긴 볼트 0 → M-01 대상 없음. 포트 0(M-06 대상 없음). 판금 0(M-04 대상 없음).
- 리지드(E-11): `joint.list` floating [], conflicts [], errors []. 고정 7컴포넌트 + REF_GROUND 한 묶음, U5_AIRTABLE + U4_X 한 묶음(모델링부 기록과 같음).

## 5. 문제
| kind | 무엇 | 어디 | 수치 | 고치는 법 |
|---|---|---|---|---|
| 디테일 | 기계 정의 U3_ROT `parts: ["U3_"]` 접두어가 U4_Y 소속 U3_DRIVE까지 잡는다 | `tools/machine.json` units.U3_ROT | U3_ 바디 3개 중 1개(U3_DRIVE)가 다른 유닛 | `parts: ["U3_PLATE","U3_COLUMN"]`으로 바꾸고 U4_Y parts에 U3_DRIVE를 명시(회귀 묶음 나눔이 틀리지 않게) |

관찰(문제 아님): 노루발 상자 내림(0) 밑면 Z 13은 테이프 윗면 Z 11보다 2 mm 위다. 선정이 "바늘 둘레 상자 Z ≥ 13(이음매 겹 12 + 1)"로 둔 차지 공간이며, 실제 노루발이 작업물을 누르는 형상은 N01 몫이다. 누름·눌림 복원은 요구서 7절(모델로 판정하지 않음).

## 6. 판정 기억·원장
- `paircache.py judge` 10건(매트↔테이프 3, 바늘↔매트·테이프 6, REF↔U4_X_BEAM 1) → `tools/out/judged…`. 조인트·배치가 바뀌면 다시 본다.
- `ledger.py commit --date 2026-11-03` → 원장 부품 36.

## 7. 등급
L 맞음 — 새 조인트 5·동작 연구·유닛 9개 전부 새로(E-18). 새 구매품 0.

## 8. 시간(E-23)
통로 MCP, CAD 호출 9(running·document.inspect·open·list_commands·batch 3·describe·inspect_design), 파일 열기 1, 브라우저 0. 걸린 시간은 최종 출력 timing.

## 워크플로우 메모
- `inspect.clearance`를 bodies·against 없이(전 바디 37) 부르고 연구별 매트만 사후에 거르는 편이 인자 크기·시간 모두 작았다(자세당 약 0.8 s).
- `edit.checkpoint` 번호가 긴 batch 뒤 `no checkpoint`로 사라졌다(형상 변경 없는 포즈 재생만 했는데). 읽기 부서는 REST step 0 + dirty 확인으로 충분했다.
