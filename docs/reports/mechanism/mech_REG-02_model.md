# REG-02 모델링 — U6·U7 높이 조정 하나로 묶기 (C-34)

## 요약 (10줄)
- 저장: `3D_Modeling/FSAP_v2.6.6.sc`(작업 전 v2.6.5, 마지막 자리 +1 — 새로 생기거나 없어진 유닛 컴포넌트 없음). 통로 MCP(앱 --control 27878, 열린 문서 v2.6.5 dirty false·undo 0 확인 뒤 이어 그림).
- 조인트: `J_U6_HGT` 지움 → `U6_SENSOR:1`을 `U7_FIXED:1`에 리지드 `J_U6_ON_U7FIX`. 높이 조정은 `J_U7_HGT` 하나(−4~+6, 값 = 두께 − 10). 두 값이 다른 자세는 모델에서 만들 수 없다.
- 새 부품: 공통 높이 판 `P_REG02_HGT_PLATE`(SUS304 t5 절삭, U7_FIXED), 압입 스터드 `STEP대기_FH4-M4-15_REG02_1~4` + `STEP대기_NUT_M4_REG02_1~4`(1·2 U6_SENSOR, 3·4 U7_FIXED), 장공 볼트 `CB5-16_REG02_1~4`(U3_HEAD, 미스미 실물 STEP).
- 지운 것: `CB5-12_M06_1·2`, `CB5-12_M05_11·12`(컴포넌트), DC2-04 fix1의 이동 피처 Move15·16(지운 볼트를 가리켜 오류). 바꾼 것: `P_M06_BASE`·`P_M05_HOLDER` Ø4.0 구멍 각 2, 와셔 `STEP대기_WASHER_M5_DC204_1·2` −Y 5.
- 과제 범위 검사(inspect.clearance, J_U7_HGT −4·0·+6, J_U6_SHIFT −60·0): 새 겹침 0, truncated 0. 맞닿음은 판↔BASE·HOLDER, 스터드↔구멍, 장공 끝(행정 끝)뿐.
- U6이 J_U7_HGT를 따라감: CARR Z 21→17(−4)·슈 바닥 12.5→8.5(−4)/18.5(+6). KDM10S·P bbox Y·Z 차 0(−4·+6).
- 회귀 자세 정의: `tools/gen_v2_poses.py`로 J_U6_HGT≠J_U7_HGT 자세 2점(옛 POSE 8·9) 빼고 J_U6_HGT 키 지움(183 → 181점, 옛 10~182 → 새 8~180). machine.json states 26개에서 J_U6_HGT 키 지움.
- **미완 1:** P_M05_GUIDE ↔ P_M06_CARR 틈 2.0 mm(J_U6_SHIFT 0, 모든 HGT 같음) < 지시 10. 기능 위치(슈·센서·바인더·테이프 길)를 옮겨야 풀려 스스로 정하지 않고 예외 요청(E-14, 6절).
- 디테일 기록(E-02): CB5-16 UPPER 물림 7/6 mm(1.4d/1.2d, 옛 9/7) — CB5-20이면 11/10(탭 깊이 12 안). CB5-16_REG02_4 렌치 길이 h +6에서 카세트 MSTH6-20과 판정 못 함(boolean 실패, 손계산 육각 렌치 Ø4.6이면 0.3 mm 걸침).
- 해석: 판은 새 하중 부품 → 임시 STEP `tools/out/mech_REG-02/stepout/P_REG02_HGT_PLATE.step`. 해석 못 함 — 환경 없음(D-16), 손계산 4절.

## 1. 통로·시간
- SolidCraft MCP. `running` 빈 목록 → `inspect_design`: 앱에 이미 `FSAP_v2.6.5.sc`가 열려 있었고 dirty false·undo 0·revision 3(디스크 그대로)이라 다시 열지 않고 이어 씀(파일 열기 0회, MCP). 막힘·재시작 0.
- 순서: 다른 이름 저장 v2.6.6(빈 새 버전, 설명 'REG-02 mechanism: …') → config.json doc v2.6.6 → 그림(batch 7회, 각 0.3~20 s) → 대기 포즈 REST 0 → 조인트 숨김 → `save {path: v2.6.6}` → 저장본 타임라인 오류 2(Move15·16) 발견 → 지우고 대기 포즈·숨김 → 다시 `save {path: v2.6.6}`(같은 새 번호 파일, 덮어쓰기 `save {}` 아님).
- 저장 확인: CLI `run savechk.json --in FSAP_v2.6.6.sc --results`(445 s, 열기 포함 한 번): 바디 560(+프로브 8), 타임라인 오류 0, 바뀐 바디 bbox 아래 표와 같음, 바꾸지 않은 CARR·GUIDE·UPPER·PUSH_BLK bbox 그대로.

## 2. 만든·바꾼·지운 부품 (h = J_U7_HGT 0, 대기 포즈)

| 부품 | 유닛/컴포넌트 | 재질·만드는 법 | bbox X / Y / Z (mm) | 부피 mm³ |
|---|---|---|---|---|
| P_REG02_HGT_PLATE (새) | U7_TAPE / U7_FIXED | SUS304 t5 절삭(판 + BASE 쪽 1 mm 패드), 세로 모서리 R3 | −80~44 / −99~−93 / 157~330 | 36,425.0 |
| STEP대기_FH4-M4-15_REG02_1·2 (새) | U6_SENSOR | 압입 스터드 M4×15(스테인리스, 임시 Ø4×15) | X −58·−44, Y −105~−90, Z 177~181 | 188.5 |
| STEP대기_FH4-M4-15_REG02_3·4 (새) | U7_FIXED | 같음 | X 27, Y −105~−90, Z 291~295 · 323~327 | 188.5 |
| STEP대기_NUT_M4_REG02_1~4 (새) | 1·2 U6_SENSOR, 3·4 U7_FIXED | SUS304 M4 너트(맞변 7·높이 3.2) | Y −102.2~−99 | 95.6 |
| CB5-16_REG02_1·2 (새, 실물 STEP) | U3_HEAD | SCM435 | X −70·−32, Y −104~−83, Z 175.75~184.25 | 554.8 |
| CB5-16_REG02_3·4 (새, 실물 STEP) | U3_HEAD | SCM435 | X 18·36, Y −105~−84, Z 305.75~314.25 | 554.8 |
| P_M06_BASE (바꿈) | U6_SENSOR | 붙임면 Ø4.0 구멍 2(X −58·−44, Z 179, 판금 돌출 cut) | 그대로 | 40,670.8 → 40,595.4 |
| P_M05_HOLDER (바꿈) | U7_FIXED | 날개 A Ø4.0 구멍 2(X 27, Z 293·325) | 그대로 | 32,733.1 → 32,632.6 |
| STEP대기_WASHER_M5_DC204_1·2 (옮김) | U3_HEAD | Y −95~−94 → −100~−99(판 앞) | X 18·36, Z 310 | 그대로 |
| CB5-12_M06_1·2, CB5-12_M05_11·12 (지움) | U3_HEAD | → CB5-16_REG02_1~4로 교체 | — | — |

- 판 장공 4: 폭 5.5, 중심선 Z 174~184(X −70·−32)·Z 304~314(X 18·36) — 기존 판금 장공과 같은 자리·길이. 스터드 구멍 Ø4.5 ×4. 판 아래 끝(날개 쪽) Z 287: 미는 볼트 끝 285와 2, 고정 너트 위 279.2와 h −4에서 3.8.
- 구멍 피처 소속: HOLDER 구멍(Cylinder766·768)·BASE 구멍(SK_REG02_BASE_STUD·Extrude121)을 각 부품 컴포넌트로 옮김. 처음엔 루트에 있어 HGT +6에서 구멍이 세계 좌표에 남아 스터드 3·4와 50.3 mm³씩 겹쳤다 → 옮긴 뒤 −4·+6 모두 맞닿음만.
- 숨김: 바디 9개(MAT·TAPE·SEAM 모형 3세트, 기존 의도), 조인트 글리프 전부(규칙 19). 리지드 그룹: `joint.list` floating 0, conflicts 0. 새 바디는 모두 유닛 컴포넌트 안(판·스터드·너트 move_bodies, 볼트 U3_HEAD 하위 컴포넌트).
- 재질: 새 가공품 SUS304, 볼트 SCM435, 스터드 Stainless Steel(400계 가정), 너트 SUS304. matcheck: 가공품 BOM이 이번 번호로 없음 → '검사 대상 없음'(실행 규칙 9).

## 3. 조인트·기계 정의 (E-15)
- CAD: `J_U6_HGT`(id 5220) 지움, `J_U6_ON_U7FIX`(rigid, U7_FIXED:1 ↔ U6_SENSOR:1, id 95073) 새로. `J_U7_HGT` 그대로(−4~+6). 동작 연구 8개 키에 J_U6_HGT 없음(motion.list 확인) → 연구 고칠 것 없음.
- 자기 점검: J_U7_HGT −4·+6 구동 → U6(CARR·SHOE·스터드 1·2)과 U7(판·HOLDER·KDM10S·스터드 3·4) 모두 같은 량 이동. 행정 끝 = 조인트 한계 = 판 장공 끝(−4에서 판 장공 끝 ↔ CB5-16_REG02_1·2·4 맞닿음 0.0). `joint.sweep`은 "contact sweep collision budget" 초과로 거부 → 구동 점(−4·−1.5·0·+6)으로 대신 봄.
- machine.json: `joints.J_U6_HGT` 지움, `J_U7_HGT._note_REG02`, `units.U6_SENSOR.joints` = [J_U7_HGT]·부품에 스터드·너트 1·2, `units.U7_TAPE` 부품에 판·스터드·너트 3·4, `units.U3_HEAD` 부품 CB5-12_M05_11·12 → `CB5-16_REG02_`, states 26개에서 J_U6_HGT 키 지움, doc v2.6.6, `_history` 한 줄.
- 회귀 자세 정의: `tools/gen_v2_poses.py`(새 생성기) → `tools/out/mech_REG-01/poses.json`·`r5/poses.json`·`tools/out/poses_v266.json` 181점. 옛 번호 대응 `tools/out/mech_REG-02/poses_map.json`(옛 POSE 8·9 뺌, 옛 10~182 → 새 8~180 — REG-01 못 본 범위 'POSE 8~182'는 새 번호로 'POSE 8~180'). 회귀 실행기 `mech_REG-01/r5/chunk7.py`·`reg12/chunk10.py`·`mech_regrun/reg13/chunk10.py`의 손 조정 초기화를 J_U7_HGT 하나로 고침(없는 조인트를 몰면 실패).

## 4. 검증 수치 (E-16, 과제 범위)
대상(바뀜·새로) 17바디, 주변 43바디(bbox X −100~70 · Y −140~−75 · Z 140~360에 걸리는 것 + U6 슈·센서·실린더·KDM10).

| 자세 | 결과 |
|---|---|
| HGT −4, SHIFT −60 | 겹침 0, truncated false. unchecked 4 = UPPER ↔ CB5-16_REG02_1~4(나사 물림, M-08 의도) |
| HGT +6, SHIFT −60 | 겹침 0(구멍 피처 옮긴 뒤), unchecked 같은 4 |
| HGT 0·−4·+6 × 판·BASE·HOLDER ↔ 스터드·너트·볼트·와셔 | 겹침 0, 맞닿음만(0.0) |
| HGT 0·−4, SHIFT 0 — U6 ↔ GUIDE·판·볼트 | 겹침 0. **GUIDE ↔ CARR 2.0**, GUIDE ↔ 센서 E32 4.92, 판 ↔ CARR 9.35, CARR ↔ CB5-16_REG02_2 15.2 |
| 볼트 렌치·너트 소켓 프로브(Ø8.5×30, Ø11×30) × HGT −4·0·+6 | 겹침 0, 0.5 안 0. +6에서 PROBE_B4 ↔ MSTH6-20_M05 판정 못 함(boolean 실패) |
| KDM10S ↔ KDM10P 짝 축 | −4: Z 619~733 둘 다, +6: 629~743 둘 다, Y −167.5~−119.5 같음 → 어긋남 0 |

- 회귀 자세 정의에 J_U6_HGT ≠ J_U7_HGT 자세: 0(J_U6_HGT 키 자체가 없음).
- 공통 판 체결 공구 막힘: 장공 볼트 4·너트 4 프로브 겹침 0. 판정 못 한 1쌍(B4 ↔ MSTH6-20, h +6)은 디테일로.

손계산(새로 만든 체결만, E-18):
- 스터드 FH4-M4 ×2(U6 쪽): 장공 볼트를 푼 높이 조정 때 U6 묶음 무게(BASE 322 + CARR 258 + SHOE 67 + 실린더·센서 등 약 250 g ≈ 0.9 kg, 9 N)를 전단으로 받음. M4 유효 단면 8.78 mm² × 2 → 0.5 MPa. 조여 있을 때는 장공 볼트 마찰이 받아 스터드 몫 거의 0. 여유 충분.
- 스터드 ×2(U7 쪽): U7 묶음 2.5 kg(D-127 임시값) + U6 0.9 kg = 34 N이 미는 볼트로 가고, 스터드는 U6 몫 9 N만 판↔HOLDER 사이로 넘김. 위와 같은 크기.
- 장공 볼트 CB5-16: 조임·마찰 경로는 DC2-04와 같음(볼트 4개가 이제 두 묶음을 함께 조임 — 미끄럼 저항은 4개 몫으로 합쳐짐). 물림 7(BASE 쪽)/6(날개 쪽) mm.

## 5. 못 한 것
- 완료 판정 'P_M05_GUIDE ↔ P_M06_CARR 틈 ≥ 10': 2.0(J_U6_SHIFT 0 작동 자세, 모든 HGT 값에서 같음 — 두 묶음이 한 판에 묶여 상대 Z가 0으로 고정). 지시 '공통 판 위 두 묶음 상대 위치를 띄워'는 U6 −Z(슈 바닥·센서 감지면이 매트에서 뜸) 또는 U7 +Z(바인더 끝 Z 13이 테이프 자리에서 뜸)·X·Y 이동(센서가 바늘 앞에서 벗어남)이라 기능 기준선이 바뀐다. 스스로 정하지 않고 예외 요청(아래 6절).
- `joint.sweep` 자기 점검은 도구 예산 초과로 거부 — 구동 점 검사로 대신함.

## 6. 예외 요청 (E-14)
- 규칙: 결정로그 C-34 완료 판정 "같은 값인 범위(−4·0·+6) 전부에서 P_M05_GUIDE ↔ P_M06_CARR 틈 ≥ 10".
- 자리: GUIDE 아래 끝(X 12~50 · Z 38)과 CARR 센서 팔 위 끝(X ≤ 18 · Z 36), Y −107~−100, J_U6_SHIFT 0.
- 근거 수치: 실측 2.0 mm(v2.6.5와 v2.6.6 같음). 10은 두 조정이 10 mm 어긋날 수 있을 때의 몫이었는데, 이제 두 묶음 사이 상대 움직임은 J_U6_SHIFT(−X로 멀어지는 쪽)뿐이다. 틈 2.0인 채로 지금까지 회귀 겹침 0(POSE 8 제외).
- 제안: ① 틈 기준을 정적 최소 틈(예: ≥ 2, 부품 공차·흔들림 몫)으로 바꾼다, 또는 ② GUIDE 아래 끝 X 12~28 부분을 Z 46까지 8 mm 잘라 ≥ 10을 만든다(테이프 홈 31×2의 아래 안내가 반쯤 짧아짐 — 테이프 거동은 요구서 7절 시제품 확인 대상). 어느 쪽이든 설계부·사용자 판단.

## 7. 디테일 기록 (E-02, 수정 회차 안 씀)
- CB5-16_REG02_1~4 UPPER 물림 7/6 mm(1.4d/1.2d), 옛 CB5-12는 9/7. CB5-20이면 11/10(탭 깊이 12 안) — 헤드 재질(D-10)이 알루미늄이면 2d 권장.
- CB5-16_REG02_4 렌치 길(h +6): 카세트 핀 MSTH6-20_M05와 판정 못 함, 손계산 육각 렌치 맞변 4(Ø4.6)이면 X 0.3 mm 걸침(Z 307.7~308.9). 옛 CB5-12_M05_12와 같은 자리(새로 생긴 것 아님, 머리 −Y 5 나옴). 높이 조정은 h를 바꾸기 전 위치에서 풀므로 실제로는 풀 때 h −4~0 쪽이면 걸림 없음.
- 스터드 FH4-M4-15: SUS 판금 t3(BASE)에 400계 압입 스터드 최소 판 두께·구멍 Ø(4.0 가정)는 PEM 카탈로그 확인 필요 → 자료대기 D-142.
- 판 BASE 쪽 패드 1 mm는 날개 A(t4)와 BASE 붙임면(t3)의 바깥면 차이를 메움. 판을 한 판에서 1 mm 깎아 만든다(절삭).

## 8. 쓴 임시값
- D-142(새): 압입 스터드 FH4-M4-15(PEM 400계 스테인리스, 머리 같은 면) ×4·M4 너트 SUS ×4 — 형번·STEP 미정, 임시 형상 Ø4×15·맞변 7×3.2.
- D-127: U7 묶음 2.5 kg(손계산), μ 0.15.
- D-04: 두께 6~16 → h −4~+6(그대로).

## 9. 파일
- 명령 기록 `tools/out/mech_REG-02/edit.json`(95단계), `edit_meta.json`, 생성기 단계 `tools/out/mech_REG-02/model/stage_A.json`·`stage_B.json`·`gen.py`
- 검사 `tools/out/mech_REG-02/savechk.json`·`savechk_measure.json`·`scope.json`, 서명 고침 `parts_changed.json`·`bolts_changed.json`(ledger sigpatch: 바뀜 17, 없어짐 4, 전체 2,658)
- 스크린샷(사람용, 열지 않음) `tools/out/mech_REG-02/FSAP_v2.6.6_iso.png`
- 임시 STEP `tools/out/mech_REG-02/stepout/P_REG02_HGT_PLATE.step`

## 워크플로우 메모
- 루트 타임라인에서 다른 컴포넌트의 바디에 `solid.cylinder cut`을 하면 구멍이 세계 좌표에 남아 조인트로 움직일 때 바디를 따라가지 않았다(HOLDER, +6에서 스터드와 50.3 mm³). 스케치 + 돌출 cut(BASE)은 따라갔다. 움직이는 부품에 구멍을 낼 때는 `component.move_features`로 그 부품 컴포넌트에 옮기고, 0이 아닌 자세에서 구멍↔끼움 부품을 다시 재야 한다.
- 지운 볼트를 가리키던 앞 과제의 `solid.move` 피처가 오류로 남는다(Move15·16). 볼트를 지울 때 `timeline.dependents`로 이어진 피처를 함께 본다.
- `joint.sweep`이 큰 묶음(U7_FIXED + U6_SENSOR ↔ U3_HEAD)에서 "contact sweep collision budget" 거부. 안내서 '조인트 자기 점검'에 대안(구동 점 + clearance)을 적어 둘 만하다.
