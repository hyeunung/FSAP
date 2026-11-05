# 모델링부 — DC2-08 수정 1회차 — v2.6.1 → v2.6.2 (2026-11-06)

**요약**
- 저장: **`3D_Modeling/FSAP_v2.6.2.sc`**(문서 이름 `FSAP_v2.6.2`, 설명 'DC2-08 mechanism fix1: CAD check of KDM10 socket vs valve-side tubes U7_1-6 at J_U7_HGT -4/+6'). config doc·machine.json doc 바꿈. 형상·조인트·묶음 변경 없음(이름·설명만) — version_bump last(수정 1회차, E-05 "수정 회차도 마지막 자리 새 파일").
- 지난 검증 문제(소켓 ↔ 밸브 쪽 관 TU0604_M08K_U7_1~6, HGT −4·+6 CAD 실측 미완)를 **CAD로 끝냈다**: 세 자세(HGT −4·0·+6) 모두 겹침 0, unchecked 0, truncated false. CB3-10 머리 ↔ 관 2.5 안 쌍 0.
- 걸린 방법: 관 끝면 = 소켓 포트 면(X 11.7) 같은 평면 맞닿음이 불리언을 느리게 하던 것(지난 65분·6.4 GB 미완)을, 검사 사본(저장 안 함)에서만 관을 −X 0.02 옮겨 없앴다. 자세마다 590~759 s(CLI 3병렬).
- 관 끝 0.5 줄이기(지시 5): 겹침이 없어 하지 않았다.
- 미완 0. 디테일(기록만)은 앞 회차 DC2-08-X1~X6 그대로.

## 0. 통로·시간 (E-04, E-23)
| 항목 | 값 |
|---|---|
| 연결 | `running` 빈 목록 → MCP. 막힘 0, 재시작 0 |
| 열린 문서 | 앱에 `FSAP_v2.6.1`이 열려 있고 dirty false(앞 회차가 저장한 그대로). 같은 경로 `open`은 디스크를 다시 읽지 않으므로(안내서 '원복') 열지 않고 그 세션에서 이었다 — MCP open 0 |
| 원복 | `edit.checkpoint` 73 |
| 그림(MCP) | `component.rename 0 → FSAP_v2.6.2`, `document.metadata.set description`, `motion.play REST step 0`(moved false), `joint.drive J_U7_HGT 0`(포즈 그대로), `browser.visibility joints false`, `save {path: v2.6.2}`(4,420,595 B) |
| 저장 확인 | `inspect_design`: dirty false, 이름 FSAP_v2.6.2, error 0, warning 15(전과 같은 15개 — 6004ZZ 볼 면 못 읽음·불리언 재시도 등, 이번과 무관). CLI로 저장본을 열어 잰 소켓·플러그·CB3-10 bbox가 앞 회차 REST 값과 같음 |
| 검사(CLI) | 저장본 v2.6.2에 대고 `run --results`(저장 없음) 3묶음 병렬: h0 590 s, h−4 743 s, h+6 759 s. 파일 열기 3 |

## 1. 지운 것·만든 것
없음(형상 변경 없음). 잔재 `STEP대기_KDM10-06_M08_PLUG`·`U7_CASSETTE/TU0604_M08_U7C_1~6`은 앞 회차에서 모델에 없음을 확인했다.

## 2. 소켓 ↔ 밸브 쪽 관 U7_1~6 CAD 실측 (지시 5·7, 완료 판정)
스크립트 `tools/out/mech_DC2-08/fix1/t_h{-4,0,6}.json`(생성기 `gen_fix1.py`), 결과 `res_h*.json`, 요약 `summ1.py`.
단계: ① REST bbox → ② `joint.drive J_U7_HGT h` → ③ bbox(소켓·플러그·관·CB3-10) → ④ `inspect.clearance` CB3-10 ×4 ↔ 관 6 (2.5) → ⑤ `solid.move` 관 6 −X 0.02(검사 사본만) → ⑥ `inspect.clearance` 소켓 ↔ 관 6 (1.0).
⑤의 이유: 관 끝면(X 11.7)과 소켓 포트 면(X 11.7)이 같은 평면으로 늘 맞닿아(안내서 '간섭' 3, 기준선 쌍) 불리언이 끝나지 않았다. 0.02만 떼면 같은 평면이 없어지고, 0.02 넘게 파고든 겹침은 그대로 잡힌다.

| HGT | 소켓 bbox Z | 플러그 bbox Z | 짝 축 차 Y·Z | CB3-10 ↔ 관 (2.5) | 소켓 ↔ 관 6 (1.0) 겹침 / unchecked / truncated | 가까운 틈 |
|---|---|---|---|---|---|---|
| −4 | 619~733 | 619~733 | 0 · 0 | 0쌍 | 0 / 0 / false | U7_3·U7_5 0.000, U7_1 0.012, U7_2·4·6 0.020 |
| 0 | 623~737 | 623~737 | 0 · 0 | 0쌍 | 0 / 0 / false | U7_1 0.000, 나머지 0.067~0.068 |
| +6 | 629~743 | 629~743 | 0 · 0 | 0쌍 | 0 / 0 / false | U7_1 0.000, 나머지 0.020 |

- 소켓 X 11.700~43.000, Y −167.5~−119.5는 세 자세 같음(J_U7_HGT는 Z만). 플러그 X 28~59, Y 같음.
- 관 bbox는 전체 길(X −51.5~1105.5)이라 bbox로는 가르지 못한다 — 그래서 CAD clearance로 쟀다(앞 회차 손계산 '관 X ≤ 11.7'은 끝 구간만의 말).
- 틈 0.000은 겹침이 아니라 면 맞닿음(겹침 0, 부피 없음). 실물에서는 유연관이 소켓을 따라 ±6 휜다 — 모델은 관을 고정 위치로 두고, 관 휨은 요구서 7절 기록 대상(모델 판정 아님).
- 판정: 완료 판정 "과제 범위 간섭 0(관 TU0604_M08K_U7 포함)" 충족. 지시 5의 "겹치면 끝 0.5 줄임"은 해당 없음.
- 그 밖의 자세(CST_X 25 × HGT 3, CST_Y 125·250, LATCH 12)·받침 공구 접근은 앞 회차 결과(`mech_DC2-08_model.md` 5절) 그대로 — 이번 회차는 형상을 바꾸지 않았다.

## 3. 묶음·조인트·기계 정의
변경 없음. `tools/machine.json` doc → v2.6.2, `_history`에 한 줄.

## 4. 서명·기록
- `ledger.py sigpatch --parts fix1/sig_parts_empty.json`(바뀜 0, 없어짐 0, 전체 2,649) → `sigcheck` reuse.
- 다시 실행 기록: `tools/out/mech_DC2-08/edit.json`(5 명령, 이름·설명·대기 포즈·글리프 숨김), `edit_meta.json`(base v2.6.1 → result v2.6.2). 앞 회차 기록은 `edit_v2.6.1.json`·`edit_meta_v2.6.1.json`으로 옮겨 둠.
- 임시 STEP: 새로 힘을 받는 가공품 없음(받침은 앞 회차 `stepout/P_M08_KDM_BRKT.step` 그대로).

## 5. 못 한 것
없음.

## 워크플로우 메모
- 같은 평면으로 늘 맞닿는 쌍(관 끝 = 포트 면)은 `inspect.clearance`가 수십 분~끝나지 않음(65분·6.4 GB). 검사 사본에서 한쪽을 0.02 떼고 재면 자세마다 10~13분에 끝났다. 기준선 쌍을 빼지 않고 꼭 재야 할 때 쓸 만한 방법.
- 같은 쌍의 틈이 0.020 대신 0.067로 나온 자세가 있다(면 분할 근사). 0.02 뗀 뒤 0.000이 나온 쌍도 겹침은 0 — 틈 숫자는 0.1 아래에서 정밀하지 않다.
