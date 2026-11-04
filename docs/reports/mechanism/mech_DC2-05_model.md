# 모델링부 — DC2-05 먼 쪽 바퀴 밑 받침 (2026-11-04, 동시 과제 E-25, CLI)

요약
- 후보 `tools/out/DC2-05/cand.sc`(기준 `base.sc` = FSAP_v2.1.5.sc). 기록 `tools/out/DC2-05/edit.json` 69단계(생성기 `tools/gen_dc2_05.py`). 다시 실행 일치(replay_ok, 바디 256 이름 + 바뀐 17 바디 부피·bbox·재질 같음, `tools/out/DC2-05/replay.json`).
- 지움: `STEP대기_BALL_D25H_M04` 컴포넌트(28 occurrence) 전부. Y ±50 줄·:270 수지 볼은 그대로.
- 새로: `P_DC205_STRIP`(A5052, 1 바디, X −1,826~−391 · Y ±25 · Z −11.8~0, 602,123 mm³, 1.614 kg) · `P_DC205_DISC_1~8`(SUS304 t4 Ø50, 구멍 Ø5.5, Z −16~−12) · `CB5-12_DC205` ×8(미스미 CB5-12 STEP 바디, 머리 Z −21~−16, 끝 Z −4).
- 과제 범위 검사: 새 겹침 0. 띠 윗면 Z 0.000(볼 꼭대기 Z 0과 같음). 트레드 ↔ 띠 J_U5_LIFT −10 X 0·690·1,380에서 0.0016(맞닿음), LIFT 0 X 800·1,000에서 10.0. 띠 ↔ 수지 볼 :270 2.0, Y ±50 줄 3.0.
- 지시서와 다른 점 1: 모델에서 띠 밑면을 Z −7.99로 둠(두께 7.99, 도면값 8.00 ±0.03 그대로). Z −8 같은 평면 맞닿음에서 boolean이 0.0026 mm 두께 가짜 겹침 95.2 mm³를 냈다(1회차). 윗면 Z 0은 그대로.
- 지시서와 다른 점 2: R0.5·C0.5를 solid.fillet·chamfer(동시 과제 금지)로 하지 않고, 단면 스케치(긴 모서리)와 끝 절삭 스케치(X 끝)로 같은 형상을 만듦. CB5-12는 file.insert_step(금지) 대신 같은 STEP으로 들어온 기존 바디 `CB5-12_M02_1`을 component.copy_bodies로 복사.
- 미완: 없음. 해석은 환경 없음(D-16) — 임시 STEP 2개 내보냄. 띠 ↔ W2는 clearance가 'Intersect empty result'로 그 쌍을 못 쟀다고 냈다(겹침 없다는 뜻으로 봄, 근거 4절). 확인용 inspect.interference를 따로 돌렸다(4절 끝).

## 근거 규칙 (원문)
- E-25(지시문): "편집은 명령 기록 … edit.json 에 쓰고 … solidcraft-cli run … --in base.sc --save cand.sc 로 만든다. … 다음 명령 종류는 쓰지 않는다(다시 실행 확인 안 됨): file.insert_step, solid.offset_face, solid.fillet, solid.chamfer, component.activate, timeline.delete." → 위 둘을 쓰지 않는 다른 길로 같은 형상을 만들었다.
- U-07 "구매처 형번 STEP이 원칙" → 볼트 바디는 미스미 CB5-12 STEP(이미 v2.1.x에 들어온 `purchased-step/CB5-12/CB5-12.stp` 바디)을 복사한 것이다. 형상·부피 476.4 mm³가 서명의 CB5-12_M03_*와 같다.
- E-09 재질·이름: 띠 A5052, 누름판 SUS304, 볼트 SCM435(기존 CB5-12와 같음). 볼트 컴포넌트 part_number CB5-12, bom_type purchased.
- E-11 리지드 그룹 누락 0: 띠·누름판은 U2_TABLE 컴포넌트의 바디, 볼트 컴포넌트는 U2_TABLE의 자식(parent 5). `joint.list` floating 없음.
- 실행 규칙 19: `browser.visibility {visible:false, folder:"joints"}` 저장 전 실행(숨긴 조인트 148).
- E-16: 판정은 수치. 스크린샷 `tools/out/mech_DC2-05/DC2-05_cand_iso.png`는 저장만.

## 1. 만든 것·지운 것 (세계 좌표 mm, REST)

| 부품 | 형상·만드는 법 | bbox (X / Y / Z) | 부피·질량 | 재질 |
|---|---|---|---|---|
| P_DC205_STRIP | YZ 단면 스케치(SK_DC205_STRIP: 50 폭, 윗 긴 모서리 R0.5 호, 밑 긴 모서리 C0.5)를 +X 1,435 밀기 → XZ 스케치(SK_DC205_ENDS) 4 윤곽으로 X 두 끝 윗 R0.5·밑 C0.5 절삭 → 보스 원통 r 17.8 ×8(Z −11.8~−7.9, join) → 보스 밑면에서 solid.hole thread M5, 깊이 8.8(밑구멍 Ø4.2 끝 Z −3.0), thread_depth 8.3(Z −3.5까지) ×8 | −1,826~−391 / ±25 / −11.8~0 | 602,123.4 mm³, 1,613.7 g | A5052 |
| P_DC205_DISC_1~8 | 원통 r 25 h 4 − 원통 r 2.75 | 중심 X −1,750·−1,600·−1,400·−1,250·−1,000·−800·−600·−450, Y 0 / Z −16~−12 | 7,758.7 mm³, 61.5 g 각 | SUS304 |
| CB5-12_DC205:1~8 | CB5-12_M02_1 바디 복사 → occurrence.move 행렬(X축 180°, 머리 밑면 → (X, 0, −16)) → occurrence.copy in_place 7 | X±4.25 / ±4.25 / −21~−4 | 476.4 mm³, 3.74 g 각 | SCM435 |
| 지움: STEP대기_BALL_D25H_M04 ×28 | component.delete | X −1,822~−428 / ±22 / −30~0 | — | — |

- 보스 자리·누름판·볼트 중심 8자리는 지시서와 같다. W2 기존 구멍 Ø36 28개 가운데 8개에 보스, 20개는 띠 밑에 빈 채(지시서 6).
- 판 W2(P_M04_PANEL_W2)는 고치지 않았다.
- 허용 범위 대조: 윗면 Z 0.000(±0.01 안), Y 폭 ±25.0(≤ ±27), −X 끝 −1,826.0(≥ −1,826), +X 끝 −391.0(≤ −390.5). 모두 맞음.
- 부품 수: −28 + 1 + 8 + 8 = 순 −11.

### 지시서와 다른 점
1. **띠 밑면 Z −7.99(모델).** 1회차 후보(밑면 Z −8.00)에서 `inspect.clearance` 띠 ↔ W2가 겹침 95.17 mm³를 냈다. 겹침 bbox Z −8.0026~−8.0000(두께 0.0026), X −1,826~−391 전 길이, 면적 83,666 mm² — 같은 평면 맞닿음의 boolean 오차다(M04 수정 1회차 'E2 끝 105.05 — 면 맞닿음 오차 제거'와 같은 종류). 2회차는 단면 스케치의 밑 높이를 −7.99로 두어 0.01 띄웠다. 윗면 Z 0, 보스 밑면 Z −11.8, 탭 위치는 그대로다. **도면 두께는 8.00 ±0.03 그대로**이고 7.99는 그 공차 안의 모델 값이다. 체결 사슬(누름판 Z −12 ↔ W2 밑면, 보스 밑면 Z −11.8)은 그대로라 볼트를 조이면 띠 밑면이 W2 윗면에 닿는다.
2. **R0.5·C0.5.** 지시서 "윗면 둘레 모서리 4개 R0.5, 밑면 둘레 C0.5". 긴 모서리 4개는 단면에 호·사선으로 넣어 밀었고, X 끝 모서리 4개는 끝 절삭 스케치(호 three_point·삼각형)로 깎았다. 네 귀퉁이는 두 R0.5가 만나는 모양(구면 귀 아님, 0.5 크기라 외관 차이 미미).
3. **볼트 넣는 법.** file.insert_step 대신 같은 STEP 바디 복사(위). 부피 476.413/476.364(STEP 원본 두 가지 표기와 같음).

## 2. 조인트·리지드 그룹·기계 정의
- 새 조인트 없음. 조인트·행정·배치 바뀐 것 없음 → machine.json 고치지 않음.
- 띠·누름판 = U2_TABLE 바디, 볼트 = U2_TABLE 자식 컴포넌트 → 테이블과 함께(움직이지 않는 쪽). `joint.list` floating 없음.
- 자기 점검(바꾼 유닛 U2는 조인트 없음): U5를 J_U5_LIFT 30 → J_U5_X 0·690·1,380·800·1,000 → LIFT −10/0으로 구동하는 동안 띠 bbox가 그대로(−1,826~−391 / ±25 / −11.8~0) — 띠가 U5를 따라 움직이지 않음.
- 저장 상태: 기록 끝에서 `motion.play REST step 0`(J_U5_LIFT 30, J_U5_X 0), 조인트 글리프 숨김.

## 3. 바퀴 길 받침 연속(완료 판정 1)
- 트레드 X 폭 25(바퀴 중심 ±12.5). J_U5_X 0 → 트레드 X −1,812.5~−1,787.5, 1,380 → −432.5~−407.5. 띠 X −1,826~−391이 전 구간을 덮는다(끝 여유 −X 13.5, +X 16.5). 트레드 Y ±60은 몸통 bbox이고 접촉선은 띠 폭 ±25 안(측정 3절). 빈 띠 0.
- 띠 윗면 Z 0.000 = 볼 꼭대기 Z 0(측정·설계안). '±0.1' 만족(모델 0.000).

## 4. 과제 범위 검사 (cand.sc, CLI, 수치)

| # | 상태 | 대상 | 결과 | 원본 |
|---|---|---|---|---|
| a | REST | 띠·누름판 ×8 ↔ W2·INSERT·MAT_L·MAT_G·P_M03_WHEEL·TREAD (clearance 3.5) | 1회차: 띠 ↔ W2 가짜 겹침 95.17(위 1절) / 누름판 ↔ W2 맞닿음 0.0 ×8, 띠 ↔ MAT_L·MAT_G 맞닿음 0.0, 나머지 3.5 넘음. 12쌍, truncated false | work/va_out.json |
| a2 | REST(2회차) | 띠 ↔ W2·INSERT (clearance 0.5) | 겹침 0, near 0. 띠 ↔ W2 쌍은 unchecked "boolean Intersect: empty result"(교집합 비어 있음). 띠 ↔ INSERT 0.5 넘음(설계 1.0) | work/vr_cand_out.json |
| b | REST | 띠·누름판 ↔ 바퀴 길 둘레 수지 볼 62(X −1,900~−350, \|Y\| ≤ 50) | 겹침 0. 최소 띠 ↔ :270 2.0, Y ±50 줄 3.0(57쌍 3.5 안) | work/vb_out.json |
| c | REST | 볼트 ×8 ↔ 띠·누름판·W2·INSERT (clearance 0.5) | 겹침 0. 볼트 머리 ↔ 누름판 맞닿음 0.0 ×8. 볼트 ↔ 띠 8쌍 unchecked "Intersect no result" — 나사 물림(볼트 Ø5 ↔ 밑구멍 Ø4.2) 자리, 비교 제외 | work/vc_out.json |
| d | LIFT −10, X 0·690·1,380 | 띠 ↔ 트레드·허브 | 겹침 0, 트레드 0.0016(맞닿음), 허브 10.0 | work/vd_out.json |
| d | LIFT 0, X 800·1,000 | 띠 ↔ 트레드 | 겹침 0, 10.0(매트 두께) | work/vd_out.json |

- 띠 ↔ W2 판단: 1회차 겹침은 Z −8.0026~−8.0 판 모양뿐이었고 보스 쪽(Z −11.8~−8) 겹침은 없었다 → 보스 ↔ 구멍 벽은 반경 0.2로 떨어져 있다. 2회차는 띠 판 부분을 0.01 올렸으므로 그 가짜 겹침 자리도 없어졌고, clearance는 교집합이 비었다고 냈다. 확인용 `inspect.interference [띠, W2]`(work/vi_out.json)를 따로 돌렸다 — 결과는 아래 '추가 확인'.
- 볼트 검사(안내서 '볼트 검사', 손계산): CB5-12 머리 밑 Z −16 → 누름판 4 + W2 4 → 보스 밑면 Z −11.8부터 나사 물림, 끝 Z −4. 물림 7.8 ≥ 1.5d 7.5(M-01). 나사 깊이 끝 Z −3.5 > 볼트 끝 Z −4(바닥 닿음 없음, 0.5). 밑구멍 끝 Z −3.0, 윗면까지 살 3.0(M-03 ≥ 2.5). 누름판 구멍 Ø5.5(볼트 Ø5 틈 0.25). 렌치 접근(밑에서 위로, 판 밑 Y ±30 · Z −80~−12 빈 공간)은 디테일 기록(E-02).
- 재질 점검: 가공품 BOM 대상 행 없음 → matcheck 생략(실행 규칙 9, BOM은 합치기 뒤). 띠 A5052·누름판 SUS304 지정 확인(측정 응답 material).
- 숨김 목록: hidden_bodies [] (숨긴 바디 0).

## 5. 다시 실행 확인 (E-25)
- edit.json을 base.sc에 다시 돌려 `work/replay.sc`를 만들고 cand.sc와 비교: 컴포넌트 바디 이름 256개 목록 같음, 바뀐 17 바디의 부피·bbox·재질·질량 같음 → `replay_ok = true`(`tools/out/DC2-05/replay.json`).
- 쓴 명령 종류: motion.play, sketch.create·line·arc.center_point·arc.three_point·finish, solid.extrude(new·cut), solid.cylinder(join·new·cut), solid.hole, material.assign, component.move_bodies·delete·create·copy_bodies·metadata.set, body.rename, occurrence.move(matrix)·copy, browser.visibility. 금지 6종 없음.

## 6. 서명·범위 (E-17)
- `ledger.py sigpatch --signatures tools/out/DC2-05/signatures.json --doc cand.sc --parts changed_parts.json --bolts changed_bolts.json --removed <D25H 28>` → 바뀜 17, 없어짐 28, 전체 3,634.
- `ledger.py scope` → 전체 검사 아니오, 바뀐 쌍만, 새로 17, 없어짐 28, 이웃 7(`tools/out/DC2-05/scope.json`).

## 7. 임시 STEP (해석용, E-06 예외)
- `tools/out/mech_DC2-05/stepout/P_DC205_STRIP.step`(2회차 형상), `P_DC205_DISC.step`(DISC_1). 해석 환경 없음(D-16) → 강도는 설계안 손계산(빈 구멍 Ø36 위 건넘 σ 9.1 MPa, SF 21).

## 8. 제어 순서 제약(U-09)
- 새로 생기는 것 없음. 기존 'J_U5_LIFT −10은 매트 없을 때만' 유지.

## 9. 합치기부에 넘길 것
- 결정로그 조각 `tools/out/DC2-05/docs/model.md`(띠 밑면 모델 7.99, 볼트 넣는 법, R·C 만드는 법). 해석 표 조각 `docs/fea-models.md`.
- 자료대기 D-97 임시값 '볼 위 그대로' → '평판 띠 P_DC205_STRIP'(설계안대로, 합치기부).
- BOM: 가공 P_DC205_STRIP 1(A5052 밀링 + 경질 알루마이트 PTFE 함침), P_DC205_DISC 8(SUS304 t4 레이저), 구매 CB5-12 +8, STEP대기_BALL_D25H_M04 −28.

## 추가 확인
- `inspect.interference [P_DC205_STRIP, P_M04_PANEL_W2]`(budget 1,500 s, 1,039 s, truncated false): interferences 0, count 0. 그 한 쌍은 'boolean Intersect: empty result'(교집합 비어 있음)로 unchecked에 남았다 — clearance와 같은 답. 두 도구 모두 겹침을 내지 않았고, 1회차의 판 모양 가짜 겹침(Z −8.0026~−8)도 사라졌다. 보스 ↔ 구멍 벽 틈은 반경 0.2(형상 값, 1회차 겹침 bbox에 보스 높이가 없음). 검도는 이 쌍을 '겹침 0, 결과는 empty-result 표기'로 보면 된다. 숫자로 된 띠 밑면 ↔ W2 윗면 거리(0.01)는 도구가 못 냈다.

## 워크플로우 메모
- 동시 과제 금지 명령(fillet·chamfer·insert_step) 아래에서도 단면 스케치·끝 절삭 스케치·기존 STEP 바디 복사(component.copy_bodies + occurrence.move matrix)로 같은 결과를 냈고 다시 실행이 일치했다. replay_check.json에 component.copy_bodies·occurrence.move(matrix)·sketch.arc.*·solid.hole을 ok 후보로 올릴 만하다.
- `inspect.clearance` 타공판(구멍 306) ↔ 띠가 한 쌍에 20분 넘게 걸렸다(va 28분, a2 23분). 같은 평면 맞닿음은 0.0026 mm 가짜 겹침을 냈다.
- 첫 확인 스크립트(v1, 39단계)를 한 번에 돌렸다가 30분 넘어 끊고 4묶음 병렬로 나눴다.
