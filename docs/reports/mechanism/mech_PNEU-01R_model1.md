# PNEU-01R 모델링 수정 1회차 — 체인 고정 끝 관 통로 (2026-11-10)

요약
- 저장: `3D_Modeling/FSAP_v2.8.12.sc`(기준 v2.8.11, 마지막 자리 +1, 수정 1회차 — 생기거나 없어진 컴포넌트 없음). `tools/config.json` doc 갱신, 앱 제목 `FSAP_v2.8.12`.
- 바뀐 부품 1: `STEP대기_2400.05.12PZ_F`(U5_WHEEL_F, 체인 고정 끝 임시 형상) 관 통로 (Y 250, Z 661) 축 X만 r 3.25 → 3.75(Ø7.5). 이웃 통로 (Y 250, Z 673) r 3.25 그대로.
- 부피 28,917.11 → 28,829.15 mm³(−87.96, 계산 π·(3.75²−3.25²)·8 = 87.96 — 통로가 지나는 윗블록 X −1230.5~−1222.5 길이 8). bbox 그대로.
- 겹침: 검도 문제 #1(12PZ_F ↔ TU0604_M08P_U5_A 3.648 mm³) → 0. 최소 거리 0.217 mm(통로 벽 Y 246.25 ↔ 관 246.47).
- 살: 이웃 통로와 12 − 3.75 − 3.25 = 5.0 ≥ 1, 블록 아랫면 Z 654까지 661 − 3.75 − 654 = 3.25.
- 관 경로·조인트·행정·기계 정의·볼트 변화 없음. 미완 없음.
- 통로 MCP(앱 --control 27878, running 빈 목록). 열기 약 640 s.

## 1. 한 일
검도 mech_PNEU-01R_verify.md 4절 #1의 첫째 고치는 법(통로 키우기)을 택했다. 관 꼭짓점을 옮기는 둘째 안은 관 바디(이미 검도를 통과한 경로·굽힘 R)를 다시 만들어야 하고 이웃 관·빗 틈을 다시 재야 해서, 지시서의 '다른 부분은 건드리지 않는다'에 더 맞는 쪽으로 정했다.

| 부품 | 명령 | base | 축 | h | 전 부피 | 후 부피 | 차 |
|---|---|---|---|---|---|---|---|
| STEP대기_2400.05.12PZ_F(Steel, 임시 형상) | solid.cylinder cut r 3.75 (Cylinder788) | (−1264, 250, 661) | +X | 44 | 28,917.111 | 28,829.154 | −87.96 |

같은 base·축·길이로 model1(v2.8.7)의 r 3.25 통로 cut과 동축이다. `body_topology`: face 14·15 cylinder r 3.7500, 원점 (−1230.5, 250, 661) 축 X. face 12·13 r 3.2500 (Z 673) 그대로.

저장 전: `component.rename 0 → FSAP_v2.8.12`, `document.metadata.set description`('PNEU-01R mechanism fix1: 12PZ_F tube passage (Y250,Z661) axis X r3.25->3.75, clears TU0604_M08P_U5_A'), `browser.visibility joints·sketches false`(실행 규칙 19), `motion.play REST 0`(conflicts 0, moved false), `save {path: FSAP_v2.8.12.sc}`(5,237,632 B). 저장 뒤 편집 없음.

다른 이름 저장: v2.8.11을 디스크에서 v2.8.12로 복사한 뒤 v2.8.12를 open 했다(열린 문서 경로가 처음부터 새 이름, v2.8.11은 손대지 않음). 끝 저장도 `save {path}`.

## 2. 완료 판정
| 항목 | 기준 | 결과 |
|---|---|---|
| 남은 문제 #1 겹침 | 0 | 12PZ_F ↔ U5_A overlaps 0, 최소 0.217 mm(`inspect.clearance` clearance 0.5, min_volume 1e-7, tolerance 1e-9) |
| 앞 두 쌍(PNEU-01R 원 과제) | 0 | 부품 바뀌지 않음 — COMB_U5_2 25,261.565·RISER 90,811.254 저장본 그대로(검도 verify 0.370·0.109 mm 유지) |
| 벽 두께 | ≥ 1 | 이웃 통로 5.0, 아랫면 3.25, 윗블록 옆면 Y 200·273까지 46.25·19.25 |
| 관 굽힘 R | ≥ 최소 굽힘 반경 | 관 바디 바뀌지 않음 — TU0604 R 16 ≥ 15 |
| 과제 범위 간섭 | 0 | 12PZ_F ↔ 이웃 8(U5_A·U5_B·체인 링크 L:1·L_TA·L_TB·COMB_U5_2·CB5-12_M03_1·2) overlaps 0. U5_B는 unchecked(boolean Intersect empty = 겹침 0, 검도와 같다). 맞닿음 0: CB5-12_M03_1·2(볼트 자리면), 링크 L:1(끝면) — 기존 의도 맞닿음, 바뀌지 않음. L_TB 0.250 |

범위: 12PZ_F bbox ±5 안 바디 27개(`tools/out/mech_PNEU-01R/near_fix1.json`). 체인 링크 사본 L:2~L:7(같은 서명, E-19)은 대표 L:1·L_TA·L_TB로 보았고, 보 P_M07_BEAM은 구멍을 키우는 cut(재질만 빼는 것)이 새 겹침을 만들 수 없어 뺐다(쌍 하나 340~390 s). 12PZ_F와 이웃은 모두 체인 고정 끝 쪽 고정품이라 움직이는 조인트 0·25·50·75·100 % 점의 형상이 대기 자세와 같아 대기 자세 한 번으로 쟀다.

## 3. 저장 확인
CLI `solidcraft-cli eval`(저장본 v2.8.12, 7분 40초): 바디 2,969(전과 같음), 12PZ_F 부피 28,829.154·bbox 그대로, U5_A 88,137.607·COMB_U5_2·RISER_COMB_1 부피·bbox 그대로(`tools/out/mech_PNEU-01R/savecheck1_out.json`).

서명: `ledger.py sigpatch --parts out/mech_PNEU-01R/parts_changed_fix1.json` 바뀜 1, 없어짐 0, 전체 2,881. 이어서 `sigcheck` reuse(문서·해시 같음).

## 4. 볼트·리지드·재질·STEP
새로 넣거나 옮긴 볼트 없음. 새 부품 없음(리지드 그룹 누락 없음, E-11). 재질 Steel 그대로(임시 형상). 12PZ_F는 igus 2400.05.12PZ 체인 고정 끝 STEP대기 형상 — 실물 STEP으로 바꿀 때 관 통로 Ø7.5(Z 661)·Ø6.5(Z 673)를 다시 본다(실물에는 관 통로가 없을 수 있어 그때 관이 끝판 안을 지나는지 재확인). 임시 STEP: 새로 힘을 받는 가공품 없음.

## 5. 못 한 것
- 스크린샷: 앱 화면은 사용자가 실시간으로 보고 있어 따로 저장하지 않았다(바뀐 것은 지름 0.5 mm, 외관 차 없음).
- 디테일(기록만): U4_B ↔ RISER_COMB_1 틈 0.109 mm(검도 #2, 그대로).

## 6. 기록
- 명령 기록 `tools/out/mech_PNEU-01R/edit.json`, `edit_meta.json`({base v2.8.11, result v2.8.12}). v2.8.11 회차 기록은 `edit_v2.8.11.json`·`edit_meta_v2.8.11.json`으로 옮겨 두었다.
- 결정로그 PNEU-01-M15.

## 워크플로우 메모
- `inspect.measure {body}`가 batch 안에서 body를 무시하고 모든 바디(2,969)를 돌려 7 MB 결과가 나왔다. 한 바디는 `measure` 도구나 `body_topology`로 잴 것.
- 앞 회차 모델링부의 과제 범위 검사가 '바뀐 부품 ↔ 주변'만 보아 '주변 ↔ 주변'(12PZ_F ↔ U5_A) 기존 겹침을 놓쳤다. 이웃끼리 겹침은 과제 범위 밖이지만 검도가 잡으면 수정 회차가 하나 더 든다.
