# 모델링부 STEPSWAP r3 — CB5-6 실물 교체 (v2.6.3 → v2.6.4, 2026-11-06)

요약
- 저장: `3D_Modeling/FSAP_v2.6.4.sc`(마지막 자리 +1: 임시 컴포넌트 `STEP대기_CB5-6_M08_PY_LC2F`를 같은 부품의 실물 컴포넌트 `CB5-6_M08_PY_LC2F`로 바꾼 것뿐이라 유닛·부품 묶음이 새로 생기거나 없어지지 않음 — v2.5.9 r2와 같은 판정). `tools/config.json` doc·`tools/machine.json` doc·유닛 부품 이름 갱신. 통로 **MCP**(앱 running 빈 목록, 막힘 없음).
- 바꾼 것: `STEP대기_CB5-6_M08_PY_LC2F:1·:2` → `CB5-6_M08_PY_LC2F:1·:2`(미스미 CB5-6 STEP, `purchased-step/CB5-6/CB5-6.stp`). 자리·bbox 임시와 같음.
- 지시 형번의 `STEP대기_` 남은 것 0(다시 연 저장본 바디 2,649개 이름 검색).
- 과제 안 검사(REST, J_U5_X 0·690·1380): 새 겹침 0, truncated false. unchecked 2쌍은 나사부 ↔ 2E 금구 M5 탭(M-08 의도 물림, M08R 때와 같음).
- 리지드: 새 occurrence 2개 dof 6 → U8_PNEU와 리지드 그룹(9282·9283) → dof 0. floating 0, conflicts 0.
- 저장본 다시 열기(CLI, 297 s): 타임라인 실패 0, bbox·부피 앱과 같음.
- 미완: 없음. 외부: 없음.
- 지난 STEPSWAP 보고서(v2.5.9)는 `mech_STEPSWAP_model_v2.5.9.md`로 옮김.

## 1. 통로·문서 확인

- `running` → 빈 목록. 열린 문서는 이름 'FSAP_v2.6.3', `path: null`, `dirty: true`, **undo 0·redo 0**, 피처 1,998, 오류 0. 이 세션에서 편집한 것이 없어 버릴 사람 편집이 없다고 판정(r2와 같은 상태). 지시서 (b)의 'merged' 문서는 이미 없었다. 저장본 `3D_Modeling/FSAP_v2.6.3.sc`를 `open`(오류 0, 피처 1,998).
- 경고 15건(6004ZZ 볼 면 못 읽음, Extrude30 Boolean retry 등)은 저장본에 원래 있던 것이고 이번 과제와 무관.
- `motion.play REST step 0` → `edit.checkpoint` → 그림(batch 2개: 지우기 0.9 s, 넣기 8.0 s) → 리지드 그룹 → REST·조인트 글리프 숨김(규칙 19)·루트 이름 'FSAP_v2.6.4'·설명 'STEPSWAP mechanism: STEP-wait CB5-6 x2 (2E curtain bracket, U8) swapped to Misumi CB5-6 STEP' → `save {path: v2.6.4}`(4,428,487 B). 저장 뒤 편집 없음(스크린샷만).
- 기록: `tools/out/mech_STEPSWAP/edit.json`(16 명령), `edit_meta.json`(base v2.6.3 → result v2.6.4). 지난 회차 기록은 `edit_v2.5.8.json`·`edit_meta_v2.5.8.json`으로 남김. 리지드 그룹은 MCP에서 occurrence id [18, 9279]·[18, 9281]로 보냈고 기록에는 이름(`U8_PNEU:1`, `CB5-6_M08_PY_LC2F:1·:2`)과 id 메모를 함께 적었다.

## 2. 바꾼 부품과 좌표(세계, REST)

볼트 STEP 틀: 로컬 +X = 나사 축, 원점 = 머리 밑면(미스미 SolidWorks 2016 STEP, 바디 'Cut-Extrude1' — CB4-25·CB6-16과 같음). 넣기 행렬 `[0,-1,0,-2315, 1,0,0,-1561, 0,0,1,100]`(로컬 X → 세계 +Y).

| 새 부품 | 유닛(부모) | 자리 | bbox | 부피·질량 | 지운 임시 형상 |
|---|---|---|---|---|---|
| `CB5-6_M08_PY_LC2F:1` | U8_PNEU(항등) | 머리 밑면 Y −1561(옆 투광 L 날개 바깥면), 축 +Y, X −2315, Z 100. 끝 Y −1555 = 커튼 면 | X −2319.25~−2310.75, Y −1566~−1555, Z 95.75~104.25 | 358.6 mm³, 2.82 g, SCM435 | `STEP대기_CB5-6_M08_PY_LC2F:1` |
| `CB5-6_M08_PY_LC2F:2` | U8_PNEU | 같은 축, Z 700 | Z 695.75~704.25(나머지 같음) | 같음 | `STEP대기_CB5-6_M08_PY_LC2F:2` |

- 임시 형상과 bbox가 같다. 부피는 실물이 육각 구멍·모따기 몫만큼 작다(401.5 → 358.6).
- 지운 순서: `selection.delete` 두 occurrence(옮김 피처 BodyTransfer199·리지드 9245가 같이 지워짐) → 원래 자리로 돌아온 임시 바디 `solid.remove`(Remove43). 임시 컴포넌트 정의도 남지 않음(`component.metadata` → 없음). r2의 Remove41 실패(지운 바디를 만든 피처가 component.delete로 같이 사라짐)와 달리 `component.delete`를 쓰지 않아, 다시 연 저장본에서 타임라인 실패 0.
- 빈 구멍 0: 2E 금구 임시 판의 M5 탭(Ø4.2 깊이 3)과 L 날개 구멍을 같은 자리·같은 지름으로 그대로 쓴다.
- 조인트: 새 조인트 없음. 리지드 그룹 9282·9283(U8_PNEU ↔ 볼트), 고정 유닛이라 행정 없음. machine.json은 doc·유닛 부품 이름(`STEP대기_CB5-6_M08_PY_LC2F` → `CB5-6_M08_PY_LC2F`)만 바꾸고 `_history`에 한 줄.

## 3. 검사(수치, E-16)

과제 안 검사(지시 6-1). CB5-6은 고정 유닛 U8에 있어 직접 구동 조인트가 없다. 가장 가까운 가동부 U5(J_U5_X)를 M08R과 같이 0·690·1380(0·50·100 %)에서 보았다. 전 사이클 motion.interference는 돌리지 않았다.

| 자세 | 대상 | against | 겹침 | 가까움 | unchecked |
|---|---|---|---|---|---|
| REST | CB5-6 :1 | P_M08_LC2F_BRKT_SM_1·F3SG-4RA0800-14_M08_2E·STEP대기_F39-LSGF_M08_2E | 0 | L 날개 0.000(머리 자리 맞닿음) | F39 2E 금구(나사 물림, boolean 실패) |
| REST | CB5-6 :2 | P_M08_LC2F_BRKT_SM_2·F3SG 2E·STEP대기_F39-LSGF_M08_2E_2 | 0 | L 날개 0.000 | F39 2E_2 금구(나사 물림) |
| J_U5_X 0·690·1380 | 둘 다 nearest 4 | 전체 | 0 | 서로 591.5 외 가까운 바디 없음 | 0 |

- 커튼 F3SG 2E와는 따로 재도 겹침 0, 거리 0.5 안 0(끝 Y −1555가 커튼 면과 같은 평면, M08R과 같음).
- unchecked 2쌍은 나사부 ↔ M5 탭 물림(M-08 의도 겹침, M08R 'CB5-6 ↔ 금구 M5 탭 17.3 mm³ ×2'와 같은 쌍). 실물이 같은 자리·같은 지름이라 물림 길이 3 그대로.
- 숨김: 바디 9개(MAT·TAPE·SEAM 모형 ×3, C-31 의도). occurrence 숨김 0. 조인트 글리프 숨김(규칙 19).
- 재질: 새 바디 SCM435(기존 CB 볼트와 같음). 가공품 변화 없음 → matcheck 대상 없음.
- 볼트 검사: 자리·방향·길이가 임시와 같아 새 막힘 없음. 물림 3(0.6d)은 디테일 M08R-D1 그대로(기록만, E-02).
- 강도: 새로 힘을 받는 가공품 없음 → 임시 STEP 없음, FEA 없음.
- 원본: `tools/out/mech_STEPSWAP/r3/verify.json`·`verify_out.json`. 스크린샷(저장만) `tools/out/mech_STEPSWAP/r3/cb56_iso.png`.

### 3-1. 저장본 확인(다시 연 파일)

`solidcraft-cli run r3/verify.json --in 3D_Modeling/FSAP_v2.6.4.sc --results`(297 s): 오류 출력 없음(타임라인 실패 0), 바디 2,649(v2.6.3과 같음: 임시 2 빠지고 실물 2 들어옴), `CB5-6_M08_PY_LC2F`·`(…:2)` bbox·부피가 앱 측정과 같음, 바꾸지 않은 `P_M08_LC2F_BRKT_SM_1·_2`·`F3SG-4RA0800-14_M08_2E`의 bbox·부피가 서명과 같음, `joint.list` floating 0·conflicts 0, 새 occurrence 9279·9281 dof 0. 바디 이름에 `STEP대기_CB5-6` 0.
- 서명: `ledger.py sigpatch`(바뀜 2, 없어짐 2, 전체 2,649), 볼트는 `r3/changed_bolts.json`.

## 4. 문서

- BOM: `docs/bom/FSAP_v2.6.4_purchased.csv`(CB5-6 행: 실물 STEP), `FSAP_v2.6.4_made.csv`(v2.6.3과 같음).
- 자료대기 D-135: 2E 금구 볼트 CB5-6 해결로 적음. 남은 것은 금구 F39-LSGF ×8(원문 대조·STEP).
- CHANGELOG v2.6.4 한 줄.

## 5. 못 한 것

- 없음.

## 6. 근거 규칙

- E-05 "형상이 바뀌면 새 번호로 저장": 마지막 자리 +1.
- E-10 "STEP대기_ 임시 형상을 실물로 바꿀 수 있는지 본다", 실행 규칙 10 "받은 STEP은 purchased-step/<형번>/<형번>.stp".
- E-11 숨김·리지드 누락 0, E-16 수치로만, M-08 나사 물림은 의도 겹침.
