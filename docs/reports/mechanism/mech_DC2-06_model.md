# DC2-06 모델링 — 바늘 옆 바퀴 ↔ 머리판 탈착 길 (v2.1.0 → v2.1.1)

## 요약
- 저장본: `3D_Modeling/FSAP_v2.1.1.sc`(문서 이름 FSAP_v2.1.1, 105바디, 1,052,248 B, REST step 0, 조인트 글리프 숨김). 작업 전 문서는 `FSAP_v2.1.0.sc`이고 덮어쓰지 않았다.
- 바뀐 부품·볼트·조인트: **없음**. 설계안 지시서대로 형상을 바꾸지 않았다. 더한 것은 설계 안 동작 연구 `MAINT_HEAD`(2단계)와 `tools/machine.json`의 상태 1행 "정비: 머리판 탈착"이다.
- MAINT_HEAD step 1(J_U4_PRESS −1.867)에서 잰 값:
  - U4 가동 17바디 대 전체: 겹침 0.
  - 머리판 통로 상자(X −140~−80 · Y ±90 · Z 125~560) 대 전체: 겹침 0. 가장 가까운 바디는 트레드로 1.14다.
  - 트레드 bbox Z 3.11~123.86, 바퀴 중심 X −100(d₁ 100 유지).
- 저장본과 v2.1.0의 105바디는 이름·bbox·부피가 모두 같다(차이 0).
- `tools/config.json`·`tools/machine.json` doc → v2.1.1. 서명 sigpatch 결과: 바뀜 0, 없어짐 0, 전체 105.
- 생성기 `tools/gen_v2_dc206.py`, 명령 기록 `tools/out/mech_DC2-06/edit.json`, 수치 `tools/out/mech_DC2-06/model_check.json`.
- 미완: 없음. 867 머리판의 실제 밑끝 Z와 체결 방향은 D-10 대기다(외부 자료).

## 1. 통로·순서 (E-04, 실행 규칙 2)
- 통로: **MCP**. 앱(127.0.0.1:27878)이 켜져 있었고 `running` 응답은 빈 목록이었다.
- 열기 전 상태: 열린 설계 FSAP_v2.1.0은 `dirty: false`, undo 0이었다. 그 상태에서 `open FSAP_v2.1.0.sc`를 했다(features 303, errors 0).
- 확인 batch(checkpoint 672 안에서 함):
  - 연구 만들기 → `motion.play MAINT_HEAD 1` → `inspect.clearance` → 트레드·바퀴 measure → 임시 프로브 상자 → 프로브 clearance → `restore_checkpoint`.
  - 첫 batch는 프로브 clearance에 `against`가 없어 0쌍만 쟀다. 그래서 다시 돌렸다.
  - 두 번째 batch에서는 restore가 "no checkpoint 672"로 실패했다. 체크포인트는 첫 복원 때 소진된 상태였다. batch 롤백(undone 4)으로 원복은 됐다.
  - 원복은 `motion.list`(연구 5개 그대로)와 `document.revision`으로 확인했다.
- 본 편집 batch(checkpoint 676 뒤):
  - `motion.study MAINT_HEAD`
  - `document.metadata.set description`("DC2-06 mechanism: maintenance state MAINT_HEAD (U4 wheel lowered to stroke end) for head plate removal path")
  - `motion.play REST 0`: J_U4_PRESS 8.626, moved false(이미 대기)
  - `browser.visibility joints false`(규칙 19)
- 저장: `save {path: 3D_Modeling/FSAP_v2.1.1.sc}`를 했다. 응답 이름은 FSAP_v2.1.1이다. 저장 뒤에는 편집하지 않았다.

## 2. 동작 연구 MAINT_HEAD (E-15)
- 키는 구동 조인트 16개(REST와 같은 조인트)다. 고리 J_U4_CYL_PIN·J_U4_CYL_ROD·J_U4_ROD_PIN은 따라간다.

| 조인트 | step 0 | step 1 |
|---|---|---|
| J_U3_PRESSER | 20 | 20 |
| J_U3_NEEDLE | 0 | 0 |
| **J_U4_PRESS** | 8.627(한계 8.626으로 잘림, REST와 같음) | **−1.867** |
| J_U4_WHEEL_ROT | 0 | 0 |
| J_U5_X / J_U5_LIFT / J_U5_WHEEL_ROT | 0 / 30 / 0 | 0 / 30 / 0 |
| J_WP_L/S/G_X·Y·ROT | 0 | 0 |

- step 1을 재생한 결과는 moved true, conflicts 0, stopped_by_contact null이다. J_U4_PRESS는 −1.867(한계 끝)에 있다.
- 따라 움직인 occurrence: U4_PRESS, U4_WHEEL, U4_CYL, U4_ROD, U4_ROD_NUT, U4_CYL_CLEVIS, I-020B_M02, E32-D36P1_2M_M02, CB5-16_M02_5~10, CB5-20_M02_1~4. unmoved는 없다.
- `tools/machine.json`:
  - `studies.MAINT_HEAD {steps 1}`을 더했다.
  - `states`에 {"name":"정비: 머리판 탈착(매트 없음, U4 내림 끝·공급 차단)","study":"MAINT_HEAD","step":1,"phase":"정비"}를 더했다. joints는 REST 값에서 J_U4_PRESS만 −1.867로 바꿨다. 상태는 모두 23개다.
- 조인트·행정·한계는 바꾸지 않았다. J_U4_PRESS 한계 −1.867~8.626 안의 값이다. 조인트 자기 점검(행정 끝 = 스토퍼)은 M02에서 했고 이번에 바뀐 것이 없다. step 1의 한계 끝 도달은 위 값으로 확인했다.

## 3. 검증 수치 (E-16·E-22, 과제 범위)
대상 자세는 MAINT_HEAD step 1이다. 관련 조인트 J_U4_PRESS의 100 % 끝이 이 자세다. 0 % 끝(REST 8.626)은 측정 보고서에서 쟀고, 봉제 사이클의 상태라 판정에서 뺀다. 전 사이클 `motion.interference`는 돌리지 않았다(E-17).

| 검사 | 결과 |
|---|---|
| U4 가동 17바디(P_M02_WHEEL·WHEEL_TREAD·FRONT·ARM_SIDE_N/P·ARM_TIE·SNS_BRKT·E32-D36P1_2M_M02·STEP대기_VRXF-PB-60-10·STEP대기_MHMF022L1U2M·CB5-20_M02_1~4·I-020B_M02·CDM2C20-25Z_ROD·_NUT) 대 전체, clearance 3, skip_within component | **겹침 0**, 31쌍. 3 mm 안 근접은 같은 레버 안의 맞닿음뿐(FRONT–CB5-20 ×4 0, VRXF–WHEEL 0, SNS_BRKT–E32 0, I-020B–NUT 0, FRONT–WHEEL 1.0, SIDE–CB5-20 2.0, WHEEL·SNS_BRKT–CB5-20 2.5). unchecked: VRXF↔CB5-20 4쌍, I-020B↔ROD 1쌍(같은 묶음 안 체결, 설계안과 같음) |
| 프로브 상자 X −140~−80 · Y ±90 · Z 125~560 대 전체 104바디 | **겹침 0**. 근접: UPPER 0.0(−X 면 맞닿음), P_M02_BASE 0.0(X −140 면 맞닿음), **P_M02_WHEEL_TREAD 1.14**, P_M02_CYLBRKT 2.0 |
| 트레드 bbox | X −114.55~−85.66 · Y ±60.00 · **Z 3.110~123.858**. 기대값 123.86 ±0.05, 바퀴 밑 3.11과 맞음 |
| 바퀴 bbox | X −119.68~−85.98 · Z 13.10~113.86. 중심 X 약 −100.5(기울기 −1.867°), 축 중심은 d₁ 100 그대로 |
| 저장본 대 v2.1.0(CLI `run --results`, 각 5 s) | 바디 105/105, 이름 차이 0, bbox·부피 차이 0. 저장 자세 REST(트레드 Z 38.80~161.19) |
| 저장본 연구 목록 | REST, CYCLE_S, CYCLE_L, CYCLE_G1, CYCLE_G2, MAINT_HEAD |

- 완료 판정 "머리판 탈착 길(헤드 −X 면 앞) 과제 범위 간섭 0, d₁ 100 유지"를 충족한다.
- 숨김 목록: hidden_bodies 0이다. 리지드 그룹은 바뀐 것이 없고, 새 부품이 없어 재질 불일치 대상도 없다(E-09·E-11).
- 새 볼트가 없어 볼트 검사 대상이 없다. 새로 힘을 받는 가공품도 없어 임시 STEP이 없다.
- 해석: 형상·하중 경로가 바뀐 부품이 없어 FEA 대상이 없다(E-18). 무게로 내림을 유지하는 손계산(SF 2.4)은 설계안 3절에 있다.
- 스크린샷: `tools/out/mech_DC2-06/FSAP_v2.1.1_iso.png`(CLI snapshot, 열어 보지 않음).

## 4. 설계검토서에 남길 제어 순서 제약 (U-09, 문서부에 넘김)
- 정비 상태(MAINT_HEAD)에 들어가는 조건: 매트 없음(E32-D36P1 OFF), 바퀴 서보 OFF, 노루발 들림(J_U3_PRESSER 20), U5 REST.
- U4 실린더는 전진(내림) 쪽으로 움직인다. 속도는 배기 미터아웃으로 조절하고 피스톤 250 mm/s 이하로 둔다.
- 내림 끝을 확인한 뒤 U4 공급을 차단하고 배기한다(잠금·표시). 그다음 머리판 탈착과 바늘대·노루발대 조정을 한다.
- 머리판 체결을 확인하기 전에는 후퇴(들림)를 금지한다.
- 봉제 사이클 중에는 머리판 탈착을 금지한다(REST 포함). REST에서는 밑띠(Z 125~165)가 77,038 mm³ 겹친다.

## 5. 규칙 자기 점검
- **E-05** "형상이 바뀌면 새 번호": 형상은 바뀌지 않았다. 다만 연구와 상태를 더해 문서가 바뀌었다. 새 컴포넌트는 생기지도 없어지지도 않았으므로 마지막 자리 +1로 v2.1.1이다. 이미 있는 파일은 덮어쓰지 않았다.
- **E-15** "움직임은 기계 정의의 조인트로만": 새 상태는 기존 조인트 값으로만 정의했다. machine.json과 설계 안 연구를 함께 고쳤다.
- **E-16** "판정은 수치로만": 위 표가 판정 근거다. 스크린샷은 저장만 했다.
- **E-17** 과제 범위: 바뀐 바디가 0이라 U4 가동 묶음과 통로 프로브만, 정비 자세 1점에서 쟀다.
- **실행 규칙 19** 조인트 글리프 숨김: 82개를 숨겼다(조인트는 그대로 있다).
- **C-03** "영구 눌림자국 금지": 정비 상태는 매트 없음이 진입 조건이다.

## 6. 디테일·남는 것 (E-02, 기록만, 설계안 7절과 같음)
- DC2-06-D1: 실린더 내림 끝 확인 스위치 자리(정비 인터록, D-M9 계열)를 제어 단계에서 정한다.
- DC2-06-D2: 머리판 실물 밑끝 Z는 D-10 STEP을 받은 뒤 통로를 다시 잰다. Z < 124면 U4를 통째 떼는 방식(위치핀 + 원터치)으로 간다.
- DC2-06-D3: 모델 한계 −1.867°와 실물 행정 끝(약 −1.94°)의 차이를 다음 검도에서 다룬다.

## 워크플로우 메모
- 프로브 상자 하나만 `bodies`로 주고 `against`를 빼면 `inspect.clearance`가 0쌍을 잰다. "bodies 안의 쌍만" 보기 때문이다. 프로브 검사에는 `against`(나머지 전부)를 꼭 준다. 이것은 안내서 '동작 검사'에 적을 후보다.
- `edit.restore_checkpoint`는 한 번 복원하면 그 체크포인트가 없어진다(다음 restore는 "no checkpoint"). 확인을 되풀이하려면 매번 새로 체크포인트를 잡는다. 설계안 메모(restore 인자 필요)와 같은 계열이다.
- `motion.list`·`describe_command`를 같은 batch에 넣으면 응답이 30만 자를 넘는다(연구 키 전부가 응답에 들어감). 목록만 볼 때는 따로 부르고 파일에서 이름만 뽑는다.
