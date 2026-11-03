# DC-04 검도·체결 — 정비 면·카세트 인출·가마 꺼내는 길 (v1.0.5)

요약(10줄 안쪽)
- 대상 `3D_Modeling/FSAP_v1.0.5.sc`(문서 이름 FSAP_v1.0.5, 바디 47). 통로 MCP(앱 27878, 저장본 open 1회, save 안 함) + 프로브 상자를 만드는 검사만 CLI `run --results`(저장 안 함) 2회.
- 범위(E-17 scope, --joints-changed): full. 바뀜 U2_BASE, 새로 8(HANGER·RAIL·IXP·CB5-12 ×3·BLOCK·CARRIER), 이웃 7. 관련 조인트 J_U8_PULL·J_U4_X·J_U4_Y·J_U3_ROT·J_U1_PRESSER·J_U1_NEEDLE.
- 과제 범위 겹침 0: J_U8_PULL 0·127.75·255.5·383.25·511, J_U4_X 5점 × J_U4_Y 5점(25자세) + 회전 45·90·180·270, 노루발 0·10·20 × 바늘 −30·−15·0.
- `joint.sweep J_U8_PULL 0→511`: stopped_at null. 511에서 캐리어 +X 면이 끝 탭 X 531에 맞닿는다(스토퍼).
- 정비 길(MAINT·MAINT_CAS): 가마 길(좁게·넓게)·팔 길·카세트 손 길·카세트 들어 빼는 길·플런저 손 길·볼트 키 길 겹침 0.
- 손 닿는 거리(D-82 ≤ 600): 카세트 498, 가마 474, 바늘 504, 플런저 572. 모두 기준 안이다.
- 볼트 CB5-12 ×3: 물림 9 ≥ 7.5(1.5d), 키 길 겹침 0, floating 0. 탭 물림은 판정 기억에 남겼다.
- 동작 문제 0 → pass. 디테일 2: 캐리어 러그 Ø6 구멍–굽힘 5 < 8(2t, 새 DC-04-D8), 걸이 Ø5.5 구멍–굽힘 3.25 < 6(모델링 DC-04-D6 확인).
- 등급: M → L로 다시 매김. 새 조인트 J_U8_PULL과 새 연구 MAINT가 생겼다(E-18 L 정의). 절차는 같아서 다시 돌 필요는 없다.
- 원장 `ledger.py commit` 했다(부품 47, 통과 항목 9). 끝에 REST step 0, dirty false, undo 0.

## 1. 통로·문서·원복(E-04·E-08)
| 항목 | 값 |
|---|---|
| 앱 | `running` 빈 큐 → `open FSAP_v1.0.5.sc` errors 0, features 138, name FSAP_v1.0.5 |
| 쓴 명령 | MCP: joint.list, joint.drive, motion.play, joint.sweep, inspect.clearance, inspect.interference, inspect_design. 형상을 바꾸는 명령은 쓰지 않았다 |
| CLI | 프로브 상자(solid.box)가 필요한 검사 2개만 `solidcraft-cli run <script> --in FSAP_v1.0.5.sc --results`(`--save` 없음). 앱 문서에 임시 바디를 넣지 않으려고 이렇게 했다(안내서 연결 'MCP로 읽을 때는 아무것도 바꾸지 않는 명령만'). 238 KB 파일이라 열기는 1초 안이다 |
| 끝 상태 | `motion.play REST 0` → `inspect_design`: dirty false, undo 0, redo 0, 타임라인 error·warning 0, 바디 47 |
| 숨김(E-11) | 47바디 모두 visible true. 숨김 0 |
| 서명 | `ledger.py sigcheck` → reuse(문서·해시 같음, 부품 47) |

## 2. 범위(E-17)
`ledger.py scope --joints-changed` → full. 이유: 조인트·행정이 바뀜, 이동 유닛 부품이 바뀜(U8_CASSETTE), 여러 유닛에 걸침(U2_BRIDGE·U8_CASSETTE·U8_GUIDE).
- 대상 바디(10): P_DC04_HANGER, STEP대기_SSEB13-560_RAIL, STEP대기_IXP-M8, CB5-12_1~3, STEP대기_SSEB13-560_BLOCK, P_DC04_CARRIER, U8_CASSETTE_BOX, U2_BASE.
- against: 이웃 7(UPPER·U1_LOWER_STAND·U2_COLUMN·U4_RAIL_A/B·U8_CASSETTE_BOX·U9_LOAD_BOX)과 관련 유닛(U1 NOSE·LOWER·LINK·DRIVE·서보, U2_BOOM, U6, U7, U1_PRESSER·NEEDLE, U3·U4·U5 가동부)이다. 매트 3장·TAPE·SEAM도 넣었다. 새 부품은 테이프 길(U7_PATH)과 매트 위 공간 옆에 있어서 작업 대상 모형을 넣었다. 모델 전체는 주지 않았다.
- 전체 사이클(motion.interference)은 돌리지 않았다(라운드 끝 전체 회귀가 본다, E-03).

## 3. 과제 범위 동작 검사(E-03·M-08)
### 3-1. 정적(REST, clearance 3)
| 쌍 | 거리 mm | 판정 |
|---|---|---|
| UPPER ↔ HANGER | 0.0 | 플랜지 윗면 Z 125 맞닿음(볼트로 붙는 면) |
| UPPER ↔ CB5-12 ×3 | unchecked(boolean 실패) | M5 나사부 Z 125~134가 UPPER Ø4.2 탭에 물림. 탭 물림이라 허용(M-08). `inspect.interference`로 다시 재도 같은 이유로 unchecked였다. 판정 기억 3건(`out/judged.json` 9612e6…, d5182b…, 80a23b…) |
| U2_BASE ↔ LOWER_STAND·RAIL_A/B·U9 | 0.0 | 기존 맞닿음(Z −380, 기준선) |
| U6 ↔ 카세트 | 1.0 | 기존과 같다 |
| UPPER ↔ CARRIER·카세트 | 1.0 | 윗틈 1 |
| 그 밖 | — | IXP ↔ U6 18.6, BLOCK ↔ UPPER 5.5, RAIL ↔ UPPER 12.5 |
겹침 0이다.

### 3-2. J_U8_PULL(바꾼 조인트) 0·25·50·75·100 %, MAINT(J_U4_X −200)
대상은 BLOCK·CARRIER·카세트, against는 U8_GUIDE 바디 전부, UPPER·NOSE, U2, U6, U7, FOOT, NEEDLE, U5_TABLE, 매트 3장이다.
| 값 | 겹침 | 가까운 쌍 |
|---|---|---|
| 127.75 · 255.5 · 383.25 | 0 | BLOCK ↔ RAIL 0.0(얹힘, 미끄럼 짝), UPPER ↔ CARRIER·카세트 1.0 |
| 511 | 0 | CARRIER ↔ HANGER 끝 탭 0.0(X 531, 스토퍼), BLOCK ↔ HANGER 0.5, UPPER ↔ 카세트·CARRIER 1.0(X 500 모서리) |
- `joint.sweep J_U8_PULL 0→511`(U8_CASSETTE ↔ U1_HEAD·U6·U7, 512표본): stopped_at null, touching_at_start 없음.
- U8_GUIDE를 against에 넣은 sweep은 "contact sweep collision budget"으로 거부됐다(레일–블록이 늘 맞닿아 있어서). 대신 위 5점과 511 맞닿음으로 본다.
- floating 0, U8_CASSETTE dof 1(joint.list).

### 3-3. 이웃 유닛 조인트(J_U4_X·J_U4_Y·J_U3_ROT), J_U8_PULL 0
대상 10바디 ↔ U5(테이블·기둥 4), U4_X_BEAM, U4_Y_CARR, U3 3바디, 매트 3장·TAPE·SEAM이다(clearance 1).
| 자세 | 겹침 | 1 mm 안 |
|---|---|---|
| J_U4_X −200·162.5·525·887.5·1250 × J_U4_Y −400·0·400·800·1200(25자세), 회전 0 | 0 | 0 |
| (1250, −400) 회전 45·90 / (−200, 0) 180 / (525, 400) 270 | 0 | 0 |
가동부는 Z 12 이하이고, 새 고정 부품은 Z 64 이상이다. U2_BASE 포켓은 자르기만 했다. 그래서 X·Y·회전에 따라 새로 생기는 쌍이 없다.

### 3-4. 노루발·바늘(J_U1_PRESSER·J_U1_NEEDLE), J_U8_PULL 0
| 자세 | FOOT ↔ 카세트 | NEEDLE ↔ 카세트 | FOOT ↔ HANGER·CARRIER·IXP |
|---|---|---|---|
| 노루발 0, 바늘 −30 | 13.0 | 20.2 | 25.0 · 26.2 · 29.0 |
| 10, −15 | 13.0 | 20.2 | 25.0 · 26.2 · 29.0 |
| 20, 0(REST) | 13.0 | 20.2 | 25.0 · 26.2 · 29.0 |
겹침 0이다.

## 4. 정비 길(완료 판정 ①, CLI 프로브, 저장 안 함)
결과 파일: `tools/out/mech_DC-04_verify/probe_out.json`, `probe2_out.json`. against는 3-1·3-3의 바디 전부와 새 부품이다.
| 프로브(바늘점 원점 mm) | 자세 | 겹침 | 가장 가까움 |
|---|---|---|---|
| VP_HOOK_N 가마 길 좁게 X 30.5~975 · Y ±20 · Z −40~−1 | MAINT | **0** | LOWER 0.5 |
| VP_HOOK_W 가마 길 넓게 X 30.5~975 · Y ±45 · Z −59.5~−0.5 | MAINT | **0** | LOWER·LINK·LOWER_DRIVE·서보 0.5 |
| VP_ARM 팔 길 X 30.5~500 · Y 45.5~560 · Z −59.5~124.5 | MAINT | **0** | UPPER 0.5, LOWER·LINK 0.71 |
| VP_HAND_CAS 카세트 손 길 X 12~499.5 · Y −20.5~40 · Z 15~120 | MAINT·MAINT_CAS | **0** | NOSE 1.0, 카세트 0.71~1.12 |
| VP_CAS_LIFT 카세트 들어 빼기 X 500.5~522 · Y −45~−21 · Z 124.5~559.5 | MAINT_CAS | **0** | U2_BOOM·UPPER·카세트 0.5 |
| 카세트·CARRIER·BLOCK(511) ↔ 서는 자리·팔·가마 길 | MAINT_CAS | **0** | 2 안 없음 |
| VP_KEY1~3 볼트 머리 아래 Ø8.5 칸 Z 85~116.9 | MAINT | **0** | 볼트 머리 0.1 |
| VP_PL_GRIP 플런저 손잡이 +Y 쪽 X −70~−24.5 · Y −29.5~20 · Z 64~124 | MAINT | **0** | IXP·HANGER 0.5 |
| VP_PL_APPR 노즈 +Y 돌아가는 길 X −11.5~12 · Y 15.5~40 · Z 15~124 | MAINT | **0** | NOSE 0.5 |
| VP_STAND 서는 자리 X 500.5~975 · Y 60.5~699.5 · Z −379.5~1100 | MAINT | U2_BOOM 423,030 | 아래 참고 |
- 서는 자리를 포켓 전폭(Y 60.5~)으로 잡으면 U2_BOOM(X −80~620 · Y −520~90 · Z 560~680)과 X 500.5~620 · Y 60.5~90 띠(폭 29.5)에서 겹친다. 바닥(Z −900)에서 붐 밑면까지는 1,460이다. 모델링부 프로브 PR_STAND는 Y 100부터라 0이었다. 이 띠는 포켓 모서리 위 머리 높이다. 사람 몸 가운데는 이 띠에서 150 넘게 떨어지고, 손 닿는 거리는 Y 100 기준으로 다시 재도 600 안이다(카세트 507, 바늘 510, 플런저 580). 그래서 판정을 막지 않고 디테일 메모로 남긴다(5절 D9).

## 5. 손 닿는 거리(완료 판정 ②, D-82 임시 ≤ 600)
기준점은 포켓 면 최근점 (X 500, Y 60)이고, 수평 거리를 잰다(D-82 정의).
| 잡는 점 | 좌표 (X, Y) | 거리 | 판정 |
|---|---|---|---|
| 카세트(운전 자리, 당기기 시작) | (11, −33) | 497.8 | ≤ 600 |
| 가마 앞 | (30, 0) | 473.8 | ≤ 600 |
| 바늘 | (0, 0) | 503.6 | ≤ 600 |
| 노루발 | (3, 0) | 500.6 | ≤ 600 |
| 플런저 손잡이 끝 | (−64, −36) | 572.1 | ≤ 600 |
선정값(498·474·504·501·572)과 같다. 플런저로 가는 손 길은 4절 VP_HAND_CAS → VP_PL_APPR → VP_PL_GRIP로 이어지며 겹침이 0이다.

## 6. 볼트·리지드·포트·판금(M-01·E-11·M-06·M-04)
### 6-1. 새 볼트 CB5-12 ×3(E-19: 같은 형번·같은 쌍 HANGER–UPPER·같은 축 −Z → 한 묶음)
주변이 다르다(1번은 U7_PATH 옆, 3번은 X 480). 그래서 키 길은 셋 다 따로 봤다.
| 항목 | 값 | 합격 |
|---|---|---|
| 삽입·렌치 | 머리 Z 117, 아래로 Ø8.5 × 32 칸(Z 85~116.9) 겹침 0. 머리 밑 다음 바디는 테이블(Z 0)과 매트(Z 12)이고, 축 방향 빈 공간은 105 이상이다 ≥ 17(L 12 + 5) | 예 |
| 물림 | UPPER Z 125~134 = 9 ≥ 7.5(1.5d) | 예 |
| 상대 | UPPER 밑면 Ø4.2 × 12 탭 ×3(STEP대기 형상, 실물 자리는 D-10, DC-04-D4) | 예(자료대기) |
| 빈자리 | HANGER Ø5.5 ×3 모두 볼트가 있다. 앞 탭 Ø8은 IXP, 러그 Ø6은 핀 | 예 |
| 리지드(E-11) | CB5-12_1~3 ↔ REF_GROUND(2:202·2:205·2:208), U8_GUIDE ↔ REF_GROUND(2:211). 물린 HANGER(U8_GUIDE)와 같은 고정 묶음이다. floating 0 | 누락 0 |
- 이웃 틈: CB5-12_1 ↔ U7_PATH 6.75(모델링 측정). 머리 Ø8.5 칸 기준이다.
### 6-2. 포트(M-06): 공압 부품이 없어 대상이 없다.
### 6-3. 판금(M-04, 기록만 — mechanism 모드에서는 디테일)
| 부품 | 구멍 | 구멍 가장자리 ↔ 굽힘 끝(평면 기준) | 2t | 판정 |
|---|---|---|---|---|
| P_DC04_HANGER t3 R3 | Ø5.5 ×3 (Y −84) | 3.25(굽힘 끝 Y −78 ↔ 구멍 끝 −81.25) | 6 | 미달(DC-04-D6, 모델링부 기록과 같음) |
| P_DC04_HANGER | 앞 탭 Ø8 (Y −36, Z 78) | 다리 쪽 굽힘에서 30 넘음 | 6 | 예 |
| P_DC04_CARRIER t4 R4 | 러그 Ø6H7 (Y −36, Z 78) | 5.0(러그 평면 시작 Y −44 ↔ 구멍 끝 −39) | 8 | **미달(새 DC-04-D8)** |
- 펀치 갇힘·두께 고르지 않음은 없다. 둘 다 BaseFlange + EdgeFlange 판금 피처이고, 타임라인 오류가 없다.

## 7. 문제
| kind | 무엇·어디 | 수치 | 고치는 법 |
|---|---|---|---|
| 디테일 | DC-04-D8(새): P_DC04_CARRIER 러그 Ø6H7 구멍–굽힘 거리 | 5.0 < 8(2t) | 러그를 Y −24까지 늘린다(X −20~−16, 카세트 X −11과 틈 5). Ø6H7을 Y −32로 옮기면 9 ≥ 8이 된다. IXP-M8 축과 걸이 앞 탭 Ø8도 Y −32로 같이 옮기고, 앞 탭 끝을 Y −26에서 −22로 늘린다(Ø8 살 6, IXP Y −38~−26). 아니면 러그 블록을 기계 가공 부품으로 따로 만든다 |
| 디테일 | DC-04-D6(확인): HANGER Ø5.5 구멍–굽힘 | 3.25 < 6 | 모델링부 안: 구멍을 Y −86으로 옮기거나 플랜지를 20으로 늘린다 |
| 디테일 | DC-04-D9(새, 메모): 포켓 모서리 X 500~620 · Y 60~90 위 머리 높이(바닥 +1,460)에 U2_BOOM이 걸린다 | VP_STAND ↔ BOOM 423,030 mm³ | 서는 자리 표시는 Y ≥ 100으로 한다(손 닿는 거리 580 이하로 유지). 외장 단계 정비 면 표시와 함께 본다(실행 규칙 14). 키 큰 작업자 기준은 D-38 |

동작 문제는 0이다.

## 8. 등급(E-18)
M → **L**. E-18 표에서 L은 "새 구동 유닛, 새 조인트·동작 연구"다. 이 과제는 새 조인트 J_U8_PULL(slide, 손)과 새 연구 MAINT(21단계)를 만들었다. 구매품도 3종 새로 넣었다(SSEB13-560·IXP-M8·CB5-12). M과 L은 같은 절차("지금 절차")라서 이번 결과에는 영향이 없다.

## 9. 원장·판정 기억
- `ledger.py commit --date 2026-11-03` → 부품 47, 통과 항목 9.
- `paircache.py judge`: UPPER ↔ CB5-12_1/2/3 탭 물림 3건.

## 10. 시간·호출(E-23)
MCP 호출 약 11번(batch 7, 단독 4), CLI 2번, 파일 열기 3번(MCP open 1번, CLI 2번).

## 워크플로우 메모
- U8_GUIDE를 against에 넣은 `joint.sweep`은 "contact sweep collision budget"으로 거부된다. 레일–블록처럼 늘 맞닿는 미끄럼 짝이 있는 유닛은 against에서 짝을 빼고 sweep하고, 짝은 점 검사로 본다. 같은 일이 생기면 안내서 '조인트 자기 점검'에 적을 후보다.
- 볼트 나사부 ↔ 탭 구멍 쌍은 `inspect.clearance`·`inspect.interference` 둘 다 boolean 실패로 unchecked가 된다. 0을 "겹침 없음"으로 읽지 않도록 판정 기억으로 남겼다.
- 읽기 부서가 프로브 상자를 만들어야 할 때 MCP 문서에 임시 바디를 넣지 않고 CLI `run --results`(저장 안 함)로 돌렸다. 작은 파일은 1초 안에 끝났다.
