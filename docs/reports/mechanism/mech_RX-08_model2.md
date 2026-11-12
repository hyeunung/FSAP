# RX-08 수정 2회차 — U4 레일 STEP 원본 잔재(Chamfer2) 지움 (모델링부, 2026-11-12)

요약(10줄 안):
- 저장: `3D_Modeling/FSAP_v2.12.1.sc` → 먼저 다른 이름 저장 **`FSAP_v2.12.2.sc`**(마지막 자리 +1, 수정 2회차) → 고친 뒤 같은 경로에 save. 통로 **MCP(앱)**, 앱 막힘 0. `tools/config.json` doc·`tools/machine.json` doc를 v2.12.2로.
- 고친 것(검증 문제 1, 사용자 "이거 안보이냐고"): 타임라인 **Remove86(97923)** 대상이 없는 이름 `SSEB13-220_RX06_RAIL`이라 오류가 나 STEP 원본 레일 **Chamfer2**(X −335~235, 44,563 mm³)가 지워지지 않고 보였다. 대상을 `Chamfer2`로 바꿈(`timeline.edit`, 재계산 128피처 42 s). 오류 사라짐(error null), Chamfer2 바디 없음.
- 지시서의 '더 작은 변경' 쪽을 택함: 그린 상자 레일 `SSEB13-570_RX06_RAIL`(X −335~−125·Y 112.5~120·Z 260~272, 18,900 mm³)은 그대로 둠. STEP 레일을 되살려 자르는 ① 안은 새 형상·새 이름이 생겨 범위가 커서 택하지 않음(실물 STEP 모양 레일은 디테일 RX-06-E1로 남음).
- 검사(REST, J_U4_X 0, 레일은 정적): 레일·블록 4 ↔ 보·스톱 A/B·관 클램프 L_4·L_5·SO_2·SO_3·CB5-16_M08_PY:26~29·U4/RX08 관·대차·축·너트 21개 → **겹침 0**. 레일–L_5 13.0, 레일–L_6 9.0, 레일–PY:28 15.17 mm. 접촉 0은 장착면(레일–보, 레일 끝–스톱 A/B).
- RX-08 새 바디(스토퍼·관 4·피팅·볼트·밸브 8)는 손대지 않음 → 검증 1회차의 겹침 0 그대로. 조인트·행정·배치 변화 없음.
- 미완 0. 해석 못 함 — 환경 없음(D-16), 힘 손계산은 v2.12.0과 같음(밀기 SF 1.69).

## 0. 근거 규칙

| 규칙 | 원문 요지 | 이번 |
|---|---|---|
| E-05 | "수정 회차도 마지막 자리 새 파일" | v2.12.1 → v2.12.2 다른 이름 저장 뒤 고침. version_bump last |
| E-04 / 실행 규칙 2 | "앱이 켜져 있으면 반드시 MCP로" | `running` 빈 목록 → open(v2.12.1) → 전부 MCP |
| E-16 | "판정은 수치로만" | clearance 수치로 판정, 스크린샷 없음 |
| E-17 | 과제 안 검사는 바뀐 바디·주변 | 지운 Chamfer2 자리(레일·블록) ↔ 이웃 21개, J_U4_X 0(레일 정적이라 95 불필요) |
| 실행 규칙 19 | 저장 전 조인트·스케치 숨김 | `browser.visibility` joints·sketches false |

## 1. 바꾼 것

| 피처 | 전 | 후 |
|---|---|---|
| Remove86 (97923) | bodies ["SSEB13-220_RX06_RAIL"] → `unknown body` 오류 | bodies ["Chamfer2"], error null |

- 지운 바디: `Chamfer2`(SSEB13-570_RX06:1/RAIL_SSEB13-570, STEP 원본 레일, 두 배치 모두 — 같은 컴포넌트).
- 만든 바디: 없음. 남은 레일은 그린 상자 `SSEB13-570_RX06_RAIL`(v2.11.0부터 있던 것).
- 저장본 `document.json`에서 Remove86 = `{"bodies":["Chamfer2"]}` 확인.

## 2. 검사 수치

- `measure SSEB13-570_RX06_RAIL`: bbox X −335~−125, Y 112.5~120, Z 260~272, 18,900 mm³.
- `measure Chamfer2`: unknown body name(없어짐).
- `inspect.clearance`(레일·블록 5 ↔ 21, clearance 0.5): overlaps 0, unchecked 0, 390 s. near: 레일–보 0(장착면), 레일–스톱 A·B 0(끝 맞닿음), 블록:2–스톱 B 0.05(v2.11.0부터 같음, J_U4_X 0 끝).
- `inspect.clearance`(레일·대차·BASE ↔ 클램프 L_4·5·6, PY:26~29, RX08 관 4): overlaps 0. 레일 최소 9.0(L_6). BASE–RX08_B_U4 0.99, 대차–RX08_B_U4 1.00(앞 회차와 같음).
- 저장 상태: REST 연구 step 0(moved false — 이미 REST), J_U4_STOP 0, J_U4_PRESS 13.006, J_U4_X 0.
- 서명: `ledger.py sigpatch --removed Chamfer2/Chamfer2` → 바뀜 0, 없어짐 1, 전체 3,186.

## 3. 기록

- 명령 기록 `tools/out/mech_RX-08/edit.json`(timeline.edit 1개), `edit_meta.json`(base v2.12.1 → result v2.12.2).
- 임시 STEP: 하중 부품 형상 변화 없음 → 앞 회차 `tools/out/mech_RX-08/stepout/`(P_RX08_STOP_BRKT·P_RX08_STOP_BLOCK·P_M02_BASE) 그대로 씀.

## 4. 못 한 것·남는 것

- 미완 0.
- 디테일(기록만): U4 레일이 STEP 원본 모양이 아니라 그린 상자(RX-06-E1). 바꾸려면 mech_RX-06_model1.md 3절 방법(Remove86에서 Chamfer2를 빼고 로컬 cut).

## 워크플로우 메모

- 피처 대상이 이름으로 걸려 있어 앞 회차 이름 바꾸기가 Remove 피처를 깨뜨렸고, 열 때 `errors: 1`이 보였는데도 두 회차 동안 남았다. 열기 결과의 errors가 0이 아니면 모델링부가 먼저 그 피처를 보도록 안내하면 좋겠다.
