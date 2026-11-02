# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

## v1.0 준비 — 2026-11-03 (개념 재수립)

- 요구서 0-8 전체 구동 개념 **확립**(사용자 동의 2026-11-03): 헤드 자체 이송(Dürkopp 867-392342 개조, 기둥 없음), 가운데 진공 원판 + 에어 테이블, X·Y 따라가기, 벤치마크 거의 그대로(결정로그 C-12~C-24, `docs/concept/v1-drive-concept-discussion.md`).
- v0.x(v0.0.0~v0.10.1) 모델·BOM·설계검토서·보고서·생성기·해석을 `archive_v0/`로 동결. 과제 목록을 N00~N08로 새로.
- 엔진 v3.7.0 맞춤(전체 회귀 상한·벤치마크 칸), 실행 규칙 17(v1.0 새 시작), 실행 인자 `tools/full-run-args.json`.

## Added

- 설계 v1.0.5 `3D_Modeling/FSAP_v1.0.5.sc`(구동 DC-04 정비 면·카세트 인출, DC-04-C3 고친 안): U2_BASE +X 정비 포켓 X 500~975·Y 60~700(−158,080,000 mm³, U자 바닥틀). 새 고정 컴포넌트 U8_GUIDE — `P_DC04_HANGER`(SUS304 t3 판금 굽힘 3, 플랜지 Z 122~125·다리 Y −75~−72·앞 탭·끝 탭), `STEP대기_SSEB13-560_RAIL`(X −20~540), `STEP대기_IXP-M8`(인덱스 플런저, 축 X (Y −36, Z 78)), CB5-12 ×3(실물 STEP, UPPER 밑면 Ø4.2×12 탭). U8_CASSETTE에 `STEP대기_SSEB13-560_BLOCK`·`P_DC04_CARRIER`(SUS304 t4 판금 ㄱ, 테이프 창). U8_CASSETTE 리지드 → 새 조인트 J_U8_PULL(slide +X 0~511, 손), 연구 MAINT(21)·REST 키 추가, machine.json 상태 MAINT·MAINT_CAS. N01 월드 고정 자르기(Box44·45) 정리 → Box28 X −11~11. 새 바디 ↔ 가동부·매트 겹침 0(J_U4_X −200·0·1250 × Y −400·0·1200, J_U8_PULL 0·255·511), MAINT 서는 자리·팔 길·카세트 길 0, 스윕 0→511 접촉 0·511 스토퍼, floating 0. 다시 실행(v1.0.4) 바디 47개 같음. 문서 이름 FSAP_v1.0.5. 생성기 `tools/gen_v1_dc04.py`, 결정로그 DC-04-M01~M07·디테일 D6·D7, 보고서 `docs/reports/mechanism/mech_DC-04_model.md`
- 설계 v1.0.2 `3D_Modeling/FSAP_v1.0.2.sc`(구동 N01 U1 헤드 개조 + 좁은 홈 묶음, N01-C3 수정안): U1_UPPER·U1_LOWER_POD → `STEP대기_867-392342_UPPER`·`_LOWER`(이름만, D-10), U1_BUNDLE → `STEP대기_867-392342_NOSE`(X ±11·Y −10~15·Z 46~125, 노루발대 구멍 Ø7), U1_PRESSER_BOX → `P_N01_FOOT`(S45C 밀링, 발바닥 X −10~3·Y −8~6·값 0 Z 12~14, 바늘 구멍 Ø3, 노루발대 Ø6 Z 14~80), U8_CASSETTE_BOX X ±15 → ±11. CYCLE_G1 478 → 528단계(홈 바닥 땀 피벗 10×18°, 현 3.911), CYCLE_G2 그대로. 묶음 폭 22 < 25(D-02 임시). 정적 겹침 0, J_U1_PRESSER·J_U1_NEEDLE 9자세·연구 38자세 새 겹침 0, 노루발↔SEAM 0.0 맞닿음, 바늘↔노루발 0.7, 노루발대↔노즈 0.5, 반대 벽 23.2(계산), floating 0. 새 볼트·구매품 STEP 0. 문서 이름 FSAP_v1.0.2. 생성기 `tools/gen_v1_n01.py`, `tools/machine.json`, 결정로그 N01-M01~M03, 자료대기 D-80, 보고서 `docs/reports/mechanism/mech_N01_model.md`
- 설계 v1.0.4 `3D_Modeling/FSAP_v1.0.4.sc`(구동 DC-05 수정 1회차): v1.0.3의 C1·C2 자르기(Box51~53)가 바디가 움직이는 컴포넌트(U4_X·U5_AIRTABLE) 안에서 잘려 월드에 고정돼 자세마다 형상이 바뀌던 것(J_U4_X 1250에서 테이블↔867 LOWER 99,000 mm³·↔U2_COLUMN 132,000 mm³)을 고침. 세 자르기를 지우고 N00 원래 피처(컴포넌트에 넣기 전) Box30(빔 길이 300→290, X −1050~−760)·Box33(바늘 홈 X −1292.5~220)·Box34(기둥 홈 X −762.5~220) 치수를 고침. J_U4_X −200·0·30·1222.5·1250에서 TABLE 255,099,000·BEAM 46,400,000 mm³ 일정, 1250에서 LOWER·U2_COLUMN↔TABLE 틈 10.0·BEAM↔U2_COLUMN 10.0. J_U4_X·J_U4_Y 스윕 stopped_at null, 사이클 표본 25자세 겹침 0. 다시 실행(v1.0.3·v1.0.2 기준) 바디 39개 부피·bbox 같음. 문서 이름 FSAP_v1.0.4. 생성기 `tools/gen_v1_dc05.py`(stage_2_fix), 보고서 `docs/reports/mechanism/mech_DC-05_model1.md`. 결과 문서: BOM `docs/bom/FSAP_v1.0.4_*.csv`, 설계검토서 `docs/review/FSAP_v1.0.4_review.md`, 결정로그 "구동 DC-05 결과"(디테일 DC-05-D1·D2), 요구서 5절 DC-05 해결, 자료대기 D-81
- 설계 v1.0.3 `3D_Modeling/FSAP_v1.0.3.sc`(구동 DC-05 아랫유닛 구동 자리 이동, DC-05-C1-R): 옛 U1_LOWER_DRIVE 상자(X 30~500·Y −460~−20) 지움 → `U1_LOWER_LINK`(SS400 각관 90×60 t4, X 30~650·Y ±45·Z −120~−60), `U1_LOWER_STAND`(SS400 받침, X 530~610·Y ±40·Z −380~−120), `U1_LOWER_DRIVE`(SS400 t4 끝판 X 650~654, Ø50 인로 구멍), `STEP대기_MHMF042L1U2M`(X 654~764, D-81 임시). U5_TABLE 바늘 홈 −X 끝 −1292.5·기둥 홈 −762.5로 40 늘림, U4_X_BEAM +X 면 −750 → −760. J_U4_X −200~1250(Y 0)·J_U4_Y −400~1200(X 0) 스윕 접촉 0(최소 10), 사이클 23자세 새 바디 겹침 0. machine.json U1_HEAD parts·xy_forbidden(원판 중심 X −20~350·|Y|<95, N03 소프트 리밋). 문서 이름 FSAP_v1.0.3. 생성기 `tools/gen_v1_dc05.py`, 보고서 `docs/reports/mechanism/mech_DC-05_model.md`
- v1.0.2 문서(구동 N01 결과): BOM `docs/bom/FSAP_v1.0.2_*.csv`, 설계검토서 `docs/review/FSAP_v1.0.2_review.md`, 결정로그 '구동 N01 결과'(디테일 3), 요구서 5절 N01 해결, 자료대기 D-81(STEP대기 867-392342·MHMF042L1U2M), 검도·해석 보고서·손계산
- 설계 v1.0.1 `3D_Modeling/FSAP_v1.0.1.sc`(구동 N00 전체 골격 U1~U9, 작은 변경): 유닛 차지 공간 상자 26개 — 새 고정 컴포넌트 U1_HEAD(U1_UPPER·U1_BUNDLE·U1_LOWER_POD Ø4 바늘 구멍·U1_LOWER_DRIVE), U2_BRIDGE(U2_BASE 3150×3115·U2_COLUMN·U2_BOOM), U4_FIX(U4_RAIL_A·B), U6_SENSOR, U7_TAPE(U7_ROLL·U7_PATH), U8_CASSETTE, U9_LOAD — 모두 REF_GROUND와 리지드. U5_AIRTABLE(U5_TABLE 홈 3 + U5_POST_1~4)은 U4_X와 리지드. 기존 컴포넌트에 U4_X_BEAM, U4_Y_CARR·U3_DRIVE, U3_PLATE r60·U3_COLUMN r50, U1_PRESSER_BOX, U1_NEEDLE_PIN. 조인트 5·연구 6 그대로. 정적 겹침 기계끼리 0, 연구 5개 motion.interference 기준선만(truncated 0), floating 0. 문서 이름 FSAP_v1.0.1. 생성기 `tools/gen_v1_n00.py`(stage 1~4), `tools/machine.json` 유닛·기준선, 서명·새 원장, 결정로그 N00-S01~S08·N00-M01, 보고서 `docs/reports/mechanism/mech_N00_model.md`
- 설계 v1.0.0 `3D_Modeling/FSAP_v1.0.0.sc`(v1.0 빈 설계 시작, 준비부 — 동작 검사 준비물): 고정부 `REF_GROUND`, 조인트 J_U4_X(−200~1250)·J_U4_Y(−400~1200)·J_U3_ROT(−360~720)·J_U1_PRESSER(0~20)·J_U1_NEEDLE(−30~0)(움직이는 유닛 컴포넌트는 빈 상태, 형상은 N00~), 작업 대상 모형 `WP_MAT_L` 1500×1500·`WP_MAT_S` 300×200·`WP_MAT_G` 1200×1200 + U홈 25×150 R12.5(두께 10)와 가공 뒤 형상 `WP_TAPE_*`(테이프 1·날개 10, 이음매 겹 30), 동작 연구 REST·CYCLE_L(659)·CYCLE_S(491)·CYCLE_G1(478)·CYCLE_G2(597)·REWIND_EMPTY(72). 원판 중심 봉제 행정 큰 310.7×1500·작은 80.3×300(0-8-5 ±0.4 %). 기계 정의 `tools/machine.json`(상태 19), 생성기 `tools/gen_v1_prep.py`, `tools/config.json` machine, 자료대기 0절 쓰는 곳·D-78, 보고서 `docs/reports/mechanism/mech_prep.md`
- 설계 v0.10.1 `3D_Modeling/FSAP_v0.10.1.sc`(구동 T13 헤드 받침 강성·배치, 작은 변경, T13-S): BASE 아래 새 컴포넌트 `T13` — `P_T13_SLEEVE`(SUS304 t2 판금: 앞판 Y 620~622, 옆판 X ±(90~92)·Y 620~780, 치마 Y 470~780·Z −679~−600, 굽힘 2 R2, 해방 홈 2, Ø5.5 16), `P_T13_REAR`(SUS304 t2 평판 Y 780~782·Z −598~−140, Ø5.5 6), `P_T13_FBL_T1/_T2`(SUS304 t2 판금 L, 580 앞끝 ↔ 1900_B, Ø5.5 4씩), 체결 CB5-12 ×30·HNTT8-5 ×30(실물 STEP, 물림 7.5). 기둥·580·T19 다리·헤드판·조인트 변경 0, 새 STEP대기_ 0, 새 마감캡 0. 정적 겹침 0, J_MAT_X·J_MAT_Y 9자세 겹침 0, 렌치 프로브 30 결함 0, floating 0. 흔들림 보수 0.290 ≤ 0.657(D-08 임시, 선정 손계산). 헤드판–기둥 체결은 DL-X06대로 안 그림. 루트 이름 FSAP_v0.10.1. 생성기 `tools/gen_t13_mech.py`(stage a~e), 결정로그 T13-M01~M05, 보고서 `docs/reports/mechanism/mech_T13_model.md`
- 설계 v0.10.0 `3D_Modeling/FSAP_v0.10.0.sc`(구동 T19 바닥틀 다리·조절발, 부품 묶음 신설, T19-C1): BASE 아래 새 컴포넌트 `T19` — 다리 `STEP대기_HFS8-4080-138_T19_*` ×8(실물 HFS8-4080-460 단면을 138로, Z −818~−680), 실물 HBLFSN8 ×18(윗 10·발 8), 받침판 `P_T19_FOOT_*` SUS304 t16 ×8(Z −834~−818, M16·M8 관통 탭, 브래킷 탭 자리 Ø15×2.5, C0.5), 레벨링 마운트 `STEP대기_ADJM16-66_T19_*` ×8(형번 임시 표기, 바닥 Z −900), 체결 HNTT8-8 ×28(실물)·`STEP대기_CB8-16` ×28·`STEP대기_CB8-25` ×8. 작업 높이 900 임시(D-39). 구동 조인트 변경 0(리지드 묶음 19), floating 0, 과제 범위 겹침 0(나사 물림만), 손계산 최소 SF 3.19, 레일 높이 차 0.126 < 0.201(D-17 임시). 렌치 프로브 결함 18(HBLFSN8 가로판 볼트 통로 ↔ 세로판 볼트 머리 2.7 mm, 브래킷 교체 예외 요청, 디테일 T19-D8). 루트 이름 FSAP_v0.10.0. 생성기 `tools/gen_t19_mech.py`(stage a~g), 손계산 `fea/cases/mech_T19_model_handcalc.py`, 자료대기 D-75~D-77, 결정로그 T19-M01~M06·디테일 T19-D6~D7, 보고서 `docs/reports/mechanism/mech_T19_model.md`
- 설계 v0.9.1 `3D_Modeling/FSAP_v0.9.1.sc`(구동 T16 X·Y 이송 배관·케이블 캐리어, 부품 묶음 신설, T16-C1 수정안): MAT_Y에 밸브 매니폴드 `STEP대기_SS5Y3-20-04` + `STEP대기_SY3120-5LZ_V1~V4`(거꾸로) + 이음 KQ2H04-M5A ×2·KQ2H06-M5A ×2·M-5P ×4·KQ2H06-01AS, 분기 받침 `P_T16_TEEHOLD`(PET-CF) + `STEP대기_KQ2T04-00A` ×4, Y 캐리어 받침 `P_T16_YMEND`(A5052 t6)·케이블 클립 `P_T16_YCLIP`(PET-CF). MAT_X에 `P_T16_YTRAY`(A5052 t2 판금)·`P_T16_XMEND`(A5052 t3 판금 L), BASE에 `P_T16_XGLIDE`(A5052 t2 판금). 캐리어 `STEP대기_HSP0320-2BN`(Y, R50)·`STEP대기_HSP0350-2BN`(X, R75) 대기 자세 3조각. 체결 CB5-12 ×13·CB5-16 ×2·HNTT8-5 ×9(실물), STEP대기 CB4 ×10·LBNR4 ×6. `P_T01_YPLATE` Ø10 ×2·M5 탭 ×6·M4 탭 ×2. 관·케이블은 경로 상자 `tools/motion_states.json` `t16_routes`(29). 조인트·행정·연구 변경 0, floating 0, 정적·7자세 새 겹침 0(캐리어 조각끼리·나사 물림 제외). v0.9.0 중간본(MAT_Y 하위 실물 볼트 6개 insert matrix 로컬 해석으로 Y −700 어긋남, 커밋 안 함)을 v0.9.1에서 고침 + YCLIP 볼트 머리 자리 Ø10. 루트 이름 FSAP_v0.9.1. 생성기 `tools/gen_t16_mech.py`(stage a~i), 보고서 `docs/reports/mechanism/mech_T16_model.md`
- 문서(구동 T17 결과): 설계검토서 `docs/review/FSAP_v0.8.6_review.md`, 결정로그 T17-R01~R03·디테일 T17-V1(J_MAT_Y 운전 상한 구동 후보), 요구서 5절 T17 해결(v0.8.6)
- 설계 v0.8.6 `3D_Modeling/FSAP_v0.8.6.sc`(구동 T17 수정 1): `P_T01_POST` θ270 리브 뿌리 R2(세로 2·위아래 2)를 형상으로 직접 만들어 한 바디에 join(SolidCraft fillet 원통–평면 미지원 우회, 디테일 T17-D7 해결). 경로 상자 `K_T17_LOOPA` → `LOOPA1`·`LOOPA2`로 나눔. 자료대기 D-58~D-61(KQ2H06-M5A STEP, TU0604, ZH 장착 방향, ZH2-BK1A 구멍). BOM `docs/bom/FSAP_v0.8.6_made.csv`·`_purchased.csv`(TCLAMP ×2, KQ2H06-M5A ×2, TU0604 2 m, CB5-12 +4, MBIS5 +1). 루트 이름 FSAP_v0.8.6. 생성기 `tools/gen_t17_mech_r1.py`, 보고서 `docs/reports/mechanism/mech_T17_model1.md`
- 설계 v0.8.5 `3D_Modeling/FSAP_v0.8.5.sc`(구동 T17 진공 배관 회전부 건너기, T17-C1): 이젝터 `ZH10DSA-06-06-08_T1/_T2`(실물 STEP) X축 180° 뒤집어 DG 받침 +X/−X 면으로, BASE → MAT_Y. `P_T01_YPLATE` Ø10 관통 ×2 (±109.6, −711.2)·M5 관통 탭 ×4 (±54, −724/−698), `P_S01_DGSPACER` ±X 면 M3 탭 ×4(브래킷 Ø3.2 축), `P_T01_POST` 벽 Ø8(θ270 Z −100)·속 안내 갈래 C(안 Ø5.9) 150°·30°·θ270 바깥 리브 + 연속 C홈 Ø6.5(한 바디), `P_T01_DISC` 가운데 MBIS 자리 Ø6.4×8 + Ø3 관통, `P_T01_RING1` (0, −800) M5 탭 깊이 6 + Ø3. 새 `P_T17_TCLAMP_1/_2`(PET-CF 출력, MAT_Y), `CB5-12_T17_CL_1~4`, `MBIS5-6.5-8_T17_D`(실물), E-10 `STEP대기_KQ2H06-M5A_D`(MAT_ROT)·`_R1`(RING1). 관 TU0604는 바디 없이 경로 상자 `tools/motion_states.json` `t17_routes`. 조인트·행정·연구 변경 0, floating 0, 과제 안 검사 새 겹침 0. 루트 이름 FSAP_v0.8.5. 생성기 `tools/gen_t17_mech.py`, 손계산 `fea/cases/mech_T17_model_handcalc.py`, 결정로그 T17-M01~M09·디테일 T17-D1~D8, 요구서 7절, 보고서 `docs/reports/mechanism/mech_T17_model.md`
- 설계 v0.8.4 `3D_Modeling/FSAP_v0.8.4.sc`(구동 T18-X04 X·Y 이송 너트 하중 경로 강화, 오조작 2364 N): `P_T18_YNB` SUS304 판금 L t8 → A6061-T6 절삭(cap X 20~120·Y −670~−610·Z −422~−370 + 고리 t12 Ø48, 328 274.4 mm³ / 886.3 g), `P_T18_XNP` SUS304 평판 t8 → A6061-T6 절삭(옆판 t8 + 밑판 t12 + 고리 t17 Ø54, +X 면 178 그대로, 399 506.2 mm³ / 1 078.7 g). Y 너트 CB5-20 ×4 뒤집음(물림 11.5), X 너트 `STEP대기_CB8-25` ×4 뒤집음(물림 17), YNB → Y판 CB5-16 ×2 옮김 + CB5-20 ×2 새로, XNP 옆판 CB5-20 + HNTT8-5 4 → 14조. `P_T01_YPLATE` 옛 탭 (55·115, −640) 피처 지움, 새 M5 관통 탭 ×2·Ø5.5 ×2. 정적 겹침 0(나사 물림만), J_MAT_X −620·−310·0·310·620 × J_MAT_Y −860·−700·−635·−410·−185·40 새 겹침 0, 렌치 프로브 26개 겹침 0, 끝 틈 X 13·6 · Y 117·70.5, CB5-16 끝–DG 받침 2.0, floating 0, matcheck 불일치 0. 조인트·행정·연구 변경 0. 루트 이름 FSAP_v0.8.4. 생성기 `tools/gen_t18x04_mech.py`, BOM `docs/bom/FSAP_v0.8.4_*.csv`, 결정로그 T18-M2-01~05, 자료대기 D-56, 보고서 `docs/reports/mechanism/mech_T18_model.md`
- 설계 v0.8.3 `3D_Modeling/FSAP_v0.8.3.sc`(STEPSWAP 구매품 실물 교체, 작은 변경): `STEP대기_HNTT8-5_T08_1~8` → 실물 STEP `HNTT8-5_T08_1~8`(MAT_X 아래, 460_F·B 밑 홈 Z −555.5~−546.5, 17×17×9, 1,896.0 mm³/개). 정적 겹침 0(460 턱 안면 Z −552.5 맞닿음), J_MAT_X −620·620·J_MAT_Y 40에서 같이 움직임, floating 0. CB5-20_T08_XN 물림 8.5 ≥ 7.5(1.5d). 문서 이름(루트 컴포넌트) 'FSAP_v0.6.15' → 'FSAP_v0.8.3'. 조인트·연구 변경 0. 생성기 `tools/gen_stepswap_mech.py`, BOM `docs/bom/FSAP_v0.8.3_*.csv`, 자료대기 D-41, 결정로그 STEPSWAP-M01~M02, 보고서 `docs/reports/mechanism/mech_STEPSWAP_model.md`
- 설계 v0.8.2 `3D_Modeling/FSAP_v0.8.2.sc`(구동 T14 회전부 높이 사슬, 작은 변경): `P_T01_YPLATE` t15 → t10(Z −370~−360, 1,804,655.3 mm³ / 4,836.5 g, M5 탭 Ø4.2 ×2 관통 — 탭 관통 + 상자 자르기), `P_S01_DGSPACER` 50 → 55(Z −360~−305, 1,706,648.9 mm³ / 4,573.8 g). 매트 밑면 Z 0·진공 면·DG 테이블 그대로, MAT_Y −2.0 kg. 정적 겹침 0, YNB 볼트 끝 ↔ 받침 2.0, 손계산 Y판 SF 6.21/3.29. 새 부품·볼트·조인트 0. 생성기 `tools/gen_t14_mech.py`, 손계산 `fea/cases/mech_T14_model_handcalc.py`, BOM `docs/bom/FSAP_v0.8.2_*.csv`, 결정로그 T14-S01~S06·T14-M01~M04, 보고서 `docs/reports/mechanism/mech_T14_*`
- 설계 v0.8.1 `3D_Modeling/FSAP_v0.8.1.sc`(구동 T15 T05 SNJ 스패너 자리, 작은 변경): `P_T05_GUIDE` 주머니 천장 Z 76.5~80.5(t4, 로드 구멍 Ø6, 앞 뿌리 R3) + 너트 틈 Z 80.5~85.5(X ≤ −114, −X·±Y 트임, 안 모서리 R1) + 위판 X −114 탑에서 외팔(97,979.7 → 103,027.8 mm³), `P_T05_PAD` 윗 긴 모서리 C2 ×2(9,624.6 mm³). 스패너 21×4 0°·±15/30/45° 겹침 0, 포트 0.5, 패드 틈 0.3/0.3/0.0, T05 정적 간섭 0(truncated false), 앞벽 오조작B 두 변 SF 3.80. 새 부품·볼트·조인트 0. 생성기 `tools/gen_t15_mech.py`, 손계산 `fea/cases/mech_T15_handcalc.py`, 결정로그 T15-S01~S09·T15-M01~M03, 자료대기 D-57, 보고서 `docs/reports/mechanism/mech_T15_*`
- 구동 T18 결과(v0.8.0, 문서): BOM `docs/bom/FSAP_v0.8.0_made.csv`(P_T18_* 6, P_T01_YPLATE 탭)·`_purchased.csv`(BSS2020-1240·BSS2520-1443·BSW15·BUN15·BSW20·BUN20·SCXW46 ×2·MHMF082L1U2M ×2·HFS8-4080-1140 ×2·HBLFSN8 ×8·HNTT8-8·CB8-45/35/25 신설, CB5-20 +30·CB5-16 +2·HNTT8-5 +18, BSS2020-1100·-1450 뺌), 설계검토서 `docs/review/FSAP_v0.8.0_review.md`, 결정로그 T18-R01~R05·디테일 과제 14, 자료대기 D-55·D-56 신설·D-24·D-25 대체·D-50·D-53 갱신, 요구서 5절 T18 일부(오조작 2364 N 강화 T18-X04 남음), 해석 손계산 `fea/cases/mech_T18_handcalc.py`
- 설계 v0.8.0 `3D_Modeling/FSAP_v0.8.0.sc`(구동 T18 X·Y 이송 구동 유닛, 부품 묶음 신설): 새 컴포넌트 `T18_Y`·`T18_XN`(MAT_X 리지드), `T18_YN`(MAT_Y), `T18_X`(BASE). 실물 STEP BSW15·BUN15·BSW20·BUN20·SCXW46-12-19·-15-19(GCPW39 형번 없음 → 대체)·HFS8-4080-1140 ×2·HBLFSN8 ×8·볼나사 너트 2·CB5-20 ×30·CB5-16 ×2·CB8-45 ×6·HNTT8-5 ×18·HNTT8-8 ×4. E-10 `STEP대기_BSS2020-1240`·`_BSS2520-1443`(축 길이를 유닛에 맞춰 고침)·`_MHMF082L1U2M_Y/_X`·`_CB8-35` ×4·`_CB8-25` ×4. 가공품 SUS304 `P_T18_YMB`(모자형 t8)·`YNB`(L t8)·`XMB`(L t8)·`XNP`(평판 t8)·`XBP`·`XSP`(받침판 t15, BSW20 4구멍 때문, X 축선 −570 → −555). `P_T01_YPLATE` M5 탭 자리 ×2. 새 연구 S18_XY·S18_Y·S18_X, 조인트·행정 변경 0, floating 0. 생성기 `tools/gen_t18_mech.py`, 결정로그 T18-M01~M09, 자료대기 D-50·D-53, 보고서 `docs/reports/mechanism/mech_T18_model.md`
- 설계 v0.7.2 `3D_Modeling/FSAP_v0.7.2.sc`: T07 고정 가드틀(형재 8·캡 4·스커트 판 3)을 뺌 — 동작과 무관한 외장(사용자 2026-11-01). BOM `FSAP_v0.7.2_*.csv`, `tools/motion_states.json` t07_zones 지움, 요구서 T07 비고, 자료대기 D-41 보류, 결정로그 V072-01~03
- 설계 v0.7.1 `3D_Modeling/FSAP_v0.7.1.sc`: T12 옆·뒤 커버를 뺌 — v0.6.15와 같은 형상(사용자 2026-11-01 "기구물 동작이랑 아무상관없는거잖아"). 요구서 T12·자료대기 D-48·D-49 보류, `tools/motion_states.json` v0.6.15 것으로, BOM `FSAP_v0.7.1_*.csv`, 결정로그 V071-01~04. 실행 규칙 14(커버·외장은 구동 아님). 엔진 v3.3.0용 문서: `tools/run-rules.md`, `docs/reports/engine-change-*.md`
- 구동 T12 결과(v0.7.0, 문서): BOM `docs/bom/FSAP_v0.7.0_made.csv`(가공품 P_T12_* 11)·`_purchased.csv`(HFS8-4080 2600·380·960·1420 신설, 1580·2850 +2, HFC8-4080-B +4, 경첩·걸쇠·인터록 형번 미정 행), 설계검토서 `docs/review/FSAP_v0.7.0_review.md`, 결정로그 T12-R01~R06·디테일 과제 11, 자료대기 D-48·D-49, 요구서 5절 T12 해결
- 설계 v0.7.0 `3D_Modeling/FSAP_v0.7.0.sc`(구동 T12 옆·뒤 커버, 부품 묶음 신설): 새 컴포넌트 `T12`(BASE 아래, 리지드) — 형재 E-10 상자 `STEP대기_HFS8-4080-2600/380/960/1580/2850/1420_T12_*` 16개(미스미 로그인 풀림), 캡 `HFC8-4080-B_T12_Q_*` 4개(실물 STEP), SUS304 t2 평판 `P_T12_SL_*`·`SU_*`·`BK_*` 10장. 새 `T12_DOOR` 판금 문 `P_T12_DOOR`(4변 접힘 22, 안 R2, 917×1417)와 조인트 `J_T12_DOOR`(회전 Z, 0~100°), 새 연구 `T12_정비문`. 기존 부품·연구 키 변경 0. 정적 겹침 0, 7개 연구 clear(truncated false), 문 최소 틈 1.22, floating 0, matcheck 불일치 0. 검사 상자 `tools/motion_states.json` `t12_zones`. 생성기 `tools/gen_t12_mech.py`, 보고서 `docs/reports/mechanism/mech_T12_*`
- 설계 v0.6.15 `3D_Modeling/FSAP_v0.6.15.sc`(구동 T11 링 실린더 배관 길, 작은 변경): `P_T01_POST` 세로 장공 5.5×10 ×3(90·210·330°, Z −208~−198) + 장공 높이 속 Ø40.2 다시 깎음(330° 조각 면 정리, DEV-2), `P_T01_SPIDER_1~3` 결속 구멍 Ø4 ×4씩(판금 블랭크 구멍), `P_T01_YPLATE` 결속 구멍 Ø4.5 ×2 (±10, −590). 새 E-10 임시 형상 `STEP대기_KQ2L04-M5A_R2_1~3`·`_R1_1~3`(10×16×11, 출구 +Z, 미스미 로그인 풀림). `J_MAT_ROT` 한계 −360~0(8개 연구 끝 단계 안). 관·결속 밴드 경로 상자 `tools/motion_states.json` `t11_routes`. 정적 겹침 0, 동작 연구 4개 clear(truncated false), floating 0, matcheck 불일치 0. 생성기 `tools/gen_t11_mech.py`, 보고서 `docs/reports/mechanism/mech_T11_*`
- 설계 v0.6.14 구동 T10 결과: 수정 1회차로 패드 28자세·동작 연구 8개 간섭 0 확인, T10 해결. BOM·설계검토서 v0.6.14(`docs/review/FSAP_v0.6.14_review.md`).
- 설계 v0.6.14 `3D_Modeling/FSAP_v0.6.14.sc`(구동 T10 T05 패드 위치, 작은 변경): CJ2B10-15Z 몸통·SNJ·로드·NTJ ×2·`P_T05_PAD` X +4.10(패드 중심 −126.90, 테이프 중심과 차 0.0025). `P_T05_GUIDE` 위판 Ø8.2 구멍 (−135.0→−126.90, 572.5)(옛 구멍 face.delete heal). 작업 대상 외피 `MAT_TAPE_PATH` 끝 Y 552.5~600 자름(외피 겹침 1.842→0). `J_T05_PAD` 새 축에 다시 만듦. 새 과제 T15(SNJ 스패너 자리). 보고서 `docs/reports/mechanism/mech_T10_model.md`.
- 구동 T09 결과(v0.6.13, 문서): 모델링 수정 2회차(형상 변경 0)로 3사이클 전 단계·칼 행정 0.5 mm 61자세 간섭 0 확인. T09 해결 — 맞날 틈 0.097, 오조작 T SF 2.26·칼 막힘 SF 8.17. BOM `docs/bom/FSAP_v0.6.13_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.13_review.md`, 결정로그 '구동 T09 결과'(디테일 T09-D1~D5), 요구서 5절 T09 해결, 자료대기 D-37·D-43·D-44 갱신. 보고서 `docs/reports/mechanism/mech_T09_model2.md`
- 설계 v0.6.13 `3D_Modeling/FSAP_v0.6.13.sc`(구동 T09 수정 1회차, 작은 변경): `J_T06_KNIFE` 원점 (72, −7.5, 57) → (24, −62.5, 45)(다시 만들고 8개 연구 키 그대로 다시 넣음, T09-M10). `P_T09_GBASE`·`P_T09_ARM` 남은 날카로운 모서리를 스케치 띠로 안 R1·바깥 C0.5 마감(GBASE 64 233.1 → 64 237.0 mm³, ARM 18 925.9 → 18 903.8 mm³, T09-M11·M12). 조인트 floating 0. 해석용 임시 STEP `tools/out/mech_T09/stepout/P_T09_ARM.step`·`P_T09_GBASE.step` 다시 냄. 보고서 `docs/reports/mechanism/mech_T09_model1.md`
- 설계 v0.6.12 `3D_Modeling/FSAP_v0.6.12.sc`(구동 T09 칼 팔 축 배치, 작은 변경): 축 `PSFJT16-100-M5`·`LHFR16_T06`·핀 `MS3-8`·판금 브래킷 `P_T06_BRACKET`·`P_T06_ARM`과 체결 11개 지움 → 미니어처 LM 가이드 `STEP대기_SSE2BZ12-120_RAIL`(T06)·`_BLK1/2`(T06_KNIFE)로 칼 묶음 안내, 실린더 `CJ2B16-30SZ`·로드·NTJ를 칼 줄 X 24의 (24, −89.5)로(ΔX −84 · ΔY −82). 새 가공품 `P_T09_GBASE`(A5052 절삭 한 바디, 코 앞면 판 + 레일 판 + 실린더 선반)·`P_T09_ARM`(SUS304 절삭 한 바디, 칼 다리 + 웨브 + 윗판 + 블록 패드 + 로드 탭). 체결 `CB5-16_T09_GB1~3`(실물, GB3는 칼 내림 중 패드 M3 머리와 부딪혀 (36, 125)로, T09-M03), E-10 `STEP대기_CB3-8_T09_BP1~8`·`_CB3-10_T09_RL1~5`(D-44). 침판 칼 홈 +X 벽 25.15 → 24.90(홈 폭 1.75). J_T06_KNIFE 이름·한계·연구 그대로(원점도 그대로, T09-M04). 칼 행정 0 → −30 1 mm 간격 31자세·이음매 11단계·노루발·바늘 극값 새 겹침 0, floating 0, matcheck 불일치 0. 모서리 R1/C0.5 일부는 CAD 미지원으로 디테일(T09-M07). 생성기 `tools/gen_t09_mech.py`, 결정로그 T09-M01~M09, 자료대기 D-37·D-44, 보고서 `docs/reports/mechanism/mech_T09_*`
- 설계 v0.6.11 `3D_Modeling/FSAP_v0.6.11.sc`(구동 T08 매트 이송 레일·블록·받침, 작은 변경): `HFS8-4080-460_F`·`_B`(캡 4 포함) +Y 43(Y −977~−937 / 203~243), `P_S01_XSPACER_1~4` 지움, 새 `P_T08_XPLATE_F`·`_B`(A5052 460 × 87 × 14, 블록 위 카운터보어 Ø9.5 × 5.5 ×4·460 밑 카운터보어 Ø9.5 × 5 ×4). 실물 `CB5-16_T08_XB_1~8`(블록 탭 물림 7.5)·`CB5-20_T08_XN_1~8`, E-10 `STEP대기_HNTT8-5_T08_1~8`(16 × 16 × 5 + C1, D-41). 블록 볼트를 위에서 풀 수 있게 됨(F-02, M-02). 렌치 프로브 16자리 × 5자세 이웃 겹침 0, 동작 연구 8 + 분할 2 충돌 0·truncated false, J_MAT_X 전 행정 멈춤 없음. P-08(조립 높이 42 레일)은 미스미에 없어 기각(T08-M02). 조인트·행정·연구 변경 0. 생성기 `tools/gen_t08_mech.py`, BOM `docs/bom/FSAP_v0.6.11_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.11_review.md`, 결정로그 T08-M01~M08, 자료대기 D-41, 보고서 `docs/reports/mechanism/mech_T08_*`
- 구동 T08 결과(2026-11-01): 검도 pass(블록 8 = BOM, 행정 그대로, 렌치 결함 0, 동작 간섭 0), 해석 손계산(블록당 1 428 N, X 블록 롤 SF 1.75 디테일). 결정로그 '구동 T08 결과', 설계검토서 v0.6.11 검도·강도·디테일 과제 표, 요구서 T08 해결
- 설계 v0.6.10 `3D_Modeling/FSAP_v0.6.10.sc`(디테일링 DP-3 수정 2회차, 작은 변경): `P_T05_HUB` 플랜지 테두리(r100)에 구멍 위상 표시 홈 폭 1.2 × 깊이 0.8 ×4(0°·90°·180°·270°, 위 홈이 홀더 위 클램프 틈 바로 위에 오면 렌치 구멍 4개가 볼트에 맞음, U-10). 허브 249 037.24 → 249 025.69 mm³. 허브 심 손계산(`fea/cases/detail_DP-3_hub_handcalc.py`, 해석 못 함 — D-16) 오조작 전단 SF 2.47·비틀림 9.95, 운전 SF ≥ 32. 동작 연구 9개 충돌 0·truncated false. 설계검토서 `docs/review/FSAP_v0.6.10_review.md`(정비 절 선기재), BOM v0.6.10. 생성기 `tools/gen_dp3_detail.py fix2`
- 설계 v0.6.9 `3D_Modeling/FSAP_v0.6.9.sc`(디테일링 DP-3 수정 1회차, 작은 변경): `P_T05_HUB` +X 면에 렌치 구멍 Ø9 ×4 깊이 10(홀더 `CB5-16_T05_HD_1~4`와 같은 축, r 28.28) — 렌치 프로브 Ø8.5×30 겹침 0(M-01, PM 판정 DP3-X01·X02). 살 5.22·15.63, 허브 324.5 → 321.3 g. 동작 연구 9개 충돌 0·truncated false. 생성기 `tools/gen_dp3_detail.py fix1`, BOM `docs/bom/FSAP_v0.6.9_*.csv`(정비 비고), 보고서 `docs/reports/detailing/detail_DP-3_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.8 `3D_Modeling/FSAP_v0.6.8.sc`(디테일링 DP-3 T05 테이프 공급, 작은 변경): 체결 16자리 실물 STEP — `CB5-16` ×8(평판 뿌리 2 물림 11, 홀더 4 물림 8.5, 안내 블록 2 물림 8), `CB5-20` ×2(홀더 귀 물림 7.5, 캡 보스 물림 8), `MBIS5-6.5-8` ×4, `STEP대기_SEWHEAD` M5 기초 구멍 6(D-10 임시). `P_T05_HOLDER` 카운터보어 Ø10 → Ø11·귀 윗면 Z 229·클램프 카운터보어 깊이 7.5·인서트 자리 9, `P_T05_CAP` 클램프 자리 고침, `P_T05_PAD` Z 43~63 한 덩어리 + NTJ-010C T홈(−X로 열림, 틈 0.2), `P_T05_GUIDE` 앞벽 t9.2(Y 553)·뿌리 R3 ×4·밑판 앞 윗모서리 R1. 생성기 `tools/gen_dp3_detail.py`, BOM `docs/bom/FSAP_v0.6.8_*.csv`(CB5-14·형번 미정 인서트 행 없앰), 결정로그 DL-D50~D57, 보고서 `docs/reports/detailing/detail_DP-3_model.md`
- 설계 v0.6.7 `3D_Modeling/FSAP_v0.6.7.sc`(디테일링 DP-2 수정 1회차, 작은 변경): `STEP대기_LBNR4_T01_*` ×24 지우고 스파이더 웹 밑 탭 너트판 `P_T01_NUTPLATE_R1/R2_1~3` ×6(A5052 t6 □40, Ø28.4, M4 관통 탭 ×4 PCD38 대각, C0.5, Z −104.5~−98.5) — `CB4-16` 물림 3.2 → 6, 스패너 자리 문제 없앰(PM 판정 DP2-X03). 스파이더 발 누름판 `P_T01_FOOTPLATE_1~3_N·_P` ×6(A5052 t6, 다리 쪽 C1) + `CB5-12_T01_SP*` ×12 → `STEP대기_CB5-18_T01_SP*` ×12(머리 자리 −224, 허브 물림 8). `P_T01_POST` 밑 플랜지 t8.5 → t12(윗면 −221) + 카운터보어 Ø9.5×3.5 ×3. 생성기 `tools/gen_dp2_r1.py`, BOM `docs/bom/FSAP_v0.6.7_*.csv`, 자료대기 D-37, 보고서 `docs/reports/detailing/detail_DP-2_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.6 `3D_Modeling/FSAP_v0.6.6.sc`(디테일링 DP-2 T01 회전 묶음, 작은 변경): `P_T01_HUB` SUS304 t6 → t8(Z −241~−233, DG 테이블 Ø6.6 ×6·스파이더 발 M5 탭 ×12·기둥 M5 탭 ×3), `P_T01_SPIDER_1~3` SUS304 밀어내기 → A5052 t3 판금 모자형(바깥 발 22, 안 R3, `sheet.convert` 전개 390×364.14, 구멍–굽힘 최소 8.25), `P_T01_POST` 2 짧게 + 밑·위 플랜지 일체, `P_T01_DISC`·`P_T01_RING1`·`P_T01_RING2` 매트 면 모서리 R1, 링1 카운터보어·링2 머리 자리·띠 1·3·5 Ø5.5. 체결: 실물 `CB5-12` ×15·`CB5-16` ×9·`MBIS5-6.5-8` ×3, E-10 `STEP대기_CB4-16`·`_LBNR4` ×24씩·`_CB6-18` ×6, `PSFJ16-150` ×6 → `STEP대기_PSFJT16-150-M5`. `LHFR16` ×6 구멍 대각(45°·−15°·+15°), NTJ 같은 이름 → `_NTJ_A`·`_NTJ_B`. 생성기 `tools/gen_dp2_detail.py`, BOM `docs/bom/FSAP_v0.6.6_*.csv`, 결정로그 DL-D36~D43, 자료대기 D-37·D-42·D-43, 보고서 `docs/reports/detailing/detail_DP-2_model.md`. 조인트·행정·배치 변경 0. 미완: 스파이더 2·3 링1 안쪽 M4 너트 4개 스패너 자리(DL-D40, PM 결정)
- 설계 v0.6.5 `3D_Modeling/FSAP_v0.6.5.sc`(디테일링 DP-1 수정 2회차, 작은 변경): 맞춤핀 `STEP대기_MS3-8_T06`을 미스미 카탈로그 외형도대로(한끝 R=D, 다른 끝 15° ℓ1 1.0) 다시 그리고 재질 SUJ2(58HRC~, 밀도 7.83)로 — D-43 재질·경도 확인. 칼 전 행정 `joint.sweep`을 잎 컴포넌트로 나눠 헤드·T05·T06 잎 전부 멈춤 없음(DL-D31). 스크립트 `tools/out/detail/DP-1/r2/build.json`, BOM `docs/bom/FSAP_v0.6.5_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.5_review.md`, 결정로그 DL-D30·D31, 자료대기 D-43, 보고서 `docs/reports/detailing/detail_DP-1_model2.md`. STEP 대기 7종은 미스미 로그인 풀림(login: false)으로 그대로. 조인트·행정·배치 변경 0
- 설계 v0.6.4 `3D_Modeling/FSAP_v0.6.4.sc`(디테일링 DP-1 수정 1회차, 작은 변경 — 중간 저장 v0.6.3 포함): 맞춤핀 형번 미스미 `MS3-8`로 정하고 `STEP대기_MS3-8_T06`(Ø3×8, T06_KNIFE, (77, −7.5) Z54~62)을 넣어 빈 핀 구멍 0(v0.6.3, 생성기 `tools/gen_dp1_r1.py`). 노루발 통로 입구 모따기 `Cone1` 시작을 주머니 끝벽 면에 맞춰 0.05 턱 면 2개 없앰(v0.6.4, MCP `timeline.edit`). 면 법선 두께 최소 1.018 ≥ 1.0. 홈매트 사이클은 두 연구(520·519단계)로 나눠 단계마다 검사. BOM `docs/bom/FSAP_v0.6.4_*.csv`(MS3-8 행), 설계검토서 `docs/review/FSAP_v0.6.4_review.md`, 결정로그 DL-D27~D29, 자료대기 D-43, 보고서 `docs/reports/detailing/detail_DP-1_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.2 `3D_Modeling/FSAP_v0.6.2.sc`(디테일링 DP-1 헤드 둘레, 작은 변경): `P_T06_ARM` 판금 L t3 → SUS304 절삭 L(가로 t5·세로 t3, 축 자리 Ø16 H7 깊이 2 + Ø5.5 + 맞춤핀 Ø3 H7, 안 R1·바깥 C0.5), 체결 15자리(실물 `CB5-12` ×5, `STEP대기_CB4-16` ×4·`_LBNR4` ×4·`_LBNR5` ×2·`_NTJ-015C` 1), `PSFJ16-100_T06` → `STEP대기_PSFJT16-100-M5`(끝 Ø4.2×12 + 핀 Ø3×6), `STEP대기_CJ2B16-30SZ_ROD` Z49~99 + 임시 튜브 Ø5.4(T06-D01), `STEP대기_SEWHEAD` 브래킷 기초 구멍 Ø4.2×10 ×2, `P_T02_FOOT` Rigid 10K → A6061-T6 + 통로 입구 45° 모따기 + 안 모서리 R0.5, STEP대기 구매품 컴포넌트 part_number(P-02). 생성기 `tools/gen_dp1_detail.py`, BOM `docs/bom/FSAP_v0.6.2_*.csv`(made 가공법 칸, CB5-12 한 행), 설계검토서 `docs/review/FSAP_v0.6.2_review.md`, 보고서 `docs/reports/detailing/detail_DP-1_model.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.1 `3D_Modeling/FSAP_v0.6.1.sc`(S02 STEP 대기 마무리, 작은 변경): 구매부가 `CJ2B16-30SZ`·`HFS8-4080-2850`·`-680`·`-1580` STEP을 또 못 받음(미스미 로그인 풀림) → 갈래 B. `STEP대기_HFS8-4080-1580_PL/PR` 상자를 Z −672~892로 줄여 끝마다 캡 끼움 깊이 8을 비움(S02-S03), 캡 4쌍 맞닿음 0.0·판정 불가 0. 조인트·동작 연구 변경 0, 8개 연구 겹침 0. BOM `docs/bom/FSAP_v0.6.1_*.csv`(STEP 대기 비고), 설계검토서 `docs/review/FSAP_v0.6.1_review.md`, 결정로그 S02-S01~S06·S02-M01~M03, 자료대기 D-37·D-41, 보고서 `mech_S02_*`
- v0.6.0 구동 T07 결과: 설계검토서 v0.6.0 검도·해석·디테일(T07-D01~D04)·예외 판정 요약, 결정로그 "구동 T07 결과", 요구서 T07 해결, 자료대기 D-41(1580 상자 캡 끼움 자리 비움 T07-X02, STEP 수령 뒤 교체·재판정), T07 검도·해석(손계산) 보고서
- 설계 v0.6.0 `3D_Modeling/FSAP_v0.6.0.sc`(T07 로딩·배출, 부품 묶음 신설): `BASE` 아래 `T07`(BASE와 리지드, 새 조인트 0, 동작 연구 변경 0) — 작업자 쪽 고정 가드틀. 형재 `HFS8-4080-460_GL/GR`(실물 STEP), `STEP대기_HFS8-4080-2850_G1/G4`·`-680_SL/SR`·`-1580_PL/PR`(D-41), 마감캡 `HFC8-4080-B` ×4(끝 기둥 위·아래), SUS304 t2 평판 `P_T07_SKIRT_C`(윗변 V홈 로딩 기준)·`_L`·`_R`. 커튼·버튼·자동 배출 자리는 `tools/motion_states.json` `t07_zones` 검사 상자. 8개 연구 새 겹침 0. 브래킷 HBLFSN8 24·판 체결은 안 그림. 생성기 `tools/gen_t07_mech.py`, BOM `docs/bom/FSAP_v0.6.0_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.0_review.md`(제어 순서 제약 T07-Q1~Q8), 결정로그 T07-M02~M07, 자료대기 D-13·D-38~D-41, 보고서 `mech_T07_model.md`
- 설계 v0.5.1 `3D_Modeling/FSAP_v0.5.1.sc`(T06-X03): 세 매트 `MAT_*_SEAM` 아래 날개 없앤 ㄱ자 단면으로 다시 그림(바디당 2,448 → 1,700 mm³), SEAM ↔ BOUND 겹침 748 → 0. `tools/gen_t06_mech.py` 단면, `tools/motion_states.json` check_rule, 결정로그 T07-M01. 함께: T07 측정·구상·선정 보고서(`mech_T07_*`), 결정로그 T07-S01~S10, 자료대기 D-38~D-41
- v0.5.0 구동 T06 결과: 설계검토서 `docs/review/FSAP_v0.5.0_review.md`, 결정로그 "구동 T06 결과"(디테일 T06-D01~D08), 요구서 T06 해결·7절 이음매 마감 시제품 항목, 자료대기 D-07·D-37 갱신, BOM v0.5.0 비고, T06 검도·해석(손계산) 보고서. 예외 판정 T06-X01~X03(SEAM 단면 수정 → v0.5.1 대기)
- 설계 v0.5.0 `3D_Modeling/FSAP_v0.5.0.sc`(T06 시작·끝 이음매와 절단, 부품 묶음 신설): `HEAD` 아래 `T06`(SUS304 판금 ㄴ t4 `P_T06_BRACKET`, 실물 `LHFR16_T06`, `STEP대기_CJ2B16-30SZ`), `T06` 아래 `T06_KNIFE`(SUS304 판금 ㄱ t3 `P_T06_ARM`, SK85 t1.5 `P_T06_KNIFE`, 실물 `PSFJ16-100_T06`, `STEP대기_CJ2B16-30SZ_ROD`, 조인트 `J_T06_KNIFE` 직선 Z −30~0, 저장 0). 침판 `P_T02_PLATE` 칼 받이 관통 홈 2×22 + C0.5. 작업 대상 `MAT_*_SCRAP` 지우고 `MAT_*_SEAM`·`MAT_*_TAIL`(컴포넌트 이름 `MAT_*_SEAM`). 사이클 3개에 ④-0~④-7 43단계(큰 583·작은 298·홈 1039), 모든 연구에 J_T06_KNIFE 키. 볼트는 구멍만. 생성기 `tools/gen_t06_mech.py`, BOM `docs/bom/FSAP_v0.5.0_*.csv`, `tools/motion_states.json`, 결정로그 T06-M01~M10, 자료대기 D-07·D-10·D-37, 보고서 `mech_T06_*`
- 설계 v0.4.2 `3D_Modeling/FSAP_v0.4.2.sc`(S01 T06 전 구매품 실물 STEP 교체·형재 마감캡): 임시 형상 28바디를 실물 STEP으로 — `SV2RL28-1800`·`-1300` ×2씩(옛 SV2R20, 조립 높이 42 → 28), `DGM200R-AZAC`(출력 테이블은 MAT_ROT), `CJ2B16-60SZ` ×6, `CJ2B10-15Z`, `PSFJ16-100`, 새로 `ZH10DSA-06-06-08` ×2(580 안쪽 면). 마감캡 `HFC8-4080-B` ×14(드러난 끝면 전부). 높이 차 14: 새 `P_S01_XSPACER_1~4`(A5052 t14), `P_T01_YPLATE` 14 내림 + 모터 창, 새 `P_S01_DGSPACER`(A5052 U자 t50). 스파이더 다리 −235~−95.5·보스 구멍 Ø10.5, LHFR16 10.5 내림, 링2 띠 1·3·5 로드 끝 자리, `P_T05_GUIDE` 위판 t4. 남은 STEP대기는 재봉 헤드 4(D-10)뿐. 생성기 `tools/gen_s01_step.py`, BOM `docs/bom/FSAP_v0.4.2_*.csv`, 결정로그 S01-M01~M10, 자료대기 D-16~D-36 갱신, 보고서 `mech_S01_*`
- 설계 v0.4.1 `3D_Modeling/FSAP_v0.4.1.sc`(T05 수정 1회차): `P_T05_PLATE` SUS304 t3 → t5(X −80~−75, 오조작 손계산 SF 0.80 → 2.16), 맞대는 `P_T05_HOLDER` 플랜지·`P_T05_GUIDE` 등판 +X 끝 −78 → −80(t10 → t8). 테이프 길·롤·실린더 그대로. 생성기 `tools/gen_t05_mech_r1.py`, BOM `docs/bom/FSAP_v0.4.1_*.csv`(평판 뿌리 볼트 CB5-12 → CB5-14 ×2), 결정로그 T05-M09~M12, 보고서 `mech_T05_model1.md`. 함께: v0.4.0 T05 검증·해석(손계산) 보고서
- 설계 v0.4.0 `3D_Modeling/FSAP_v0.4.0.sc`(T05 테이프 공급·장력 유닛, 부품 묶음 신설): `HEAD` 아래 `T05`(SUS304 평판 t3, PET-CF 홀더·허브·캡·안내 블록 C틀, `STEP대기_PSFJ16-100`·`STEP대기_CJ2B10-15`), `T05_PAD`(PET-CF 패드 + 로드, 조인트 `J_T05_PAD` 직선 Z −13.5~0, 저장 −12.5), 작업 대상 외피 `T05_TAPE`(`MAT_TAPE_ROLL`·`MAT_TAPE_PATH`, BOM 밖). 볼트는 구멍만. 6개 연구 2,443단계 겹침 0. 생성기 `tools/gen_t05_mech.py`, BOM `docs/bom/FSAP_v0.4.0_made.csv`·`_purchased.csv`, 결정로그 T05-S01~S08·T05-M01~M08, 자료대기 D-06·D-10·D-33·D-34, 보고서 `mech_T05_*`.
- v0.4.1 구동 T05 결과: 설계검토서 FSAP_v0.4.1_review.md, 결정로그 "구동 T05 결과", 요구서 T05 해결, T05 검도·해석(손계산) 수정 1회차 보고서(mech_T05_verify1·fea1)
- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

- 설계 v0.3.2 `3D_Modeling/FSAP_v0.3.2.sc`(T04 가장자리 센서 배치): 노루발 `P_T02_FOOT`에 영역형 반사 화이버 주머니 12.0×3.15×8·검출 슬릿 11.0×1.0(바닥 관통)·화이버 통로 Ø2.6(+X 옆면 출구)을 깎음. 화이버 머리는 형번 미정(D-32)이라 그리지 않음. 생성기 `tools/gen_t04_mech.py`, BOM `docs/bom/FSAP_v0.3.2_made.csv`·`_purchased.csv`, 결정로그 T04-S01~S07·T04-M01~M04, 자료대기 D-32, 보고서 `mech_T04_*`.
- 설계 v0.3.1 `3D_Modeling/FSAP_v0.3.1.sc`: 미스미 실물 STEP으로 구매품 22개 교체(HFS8-4080-1300·460·1900·580 형재 10, LHFR16 6, PSFJ16-150 6). 생성기 `tools/gen_v031_step.py`, STEP 9종 `purchased-step/<형번>/`(BSS2020-1100·1450, HBLFSN8은 받기만 함). 결정로그 V031-01~05, C-10(유료 STEP은 받지 않음), 자료대기 D-17~D-31 갱신(SV2R20·ZH10DS 형번 없음, DGM200R·CJ2B16 미스미 CAD 없음).

- 설계 v0.1.0 `3D_Modeling/FSAP_v0.1.0.sc`(준비부): 동작 검사 준비물 — 고정부 `BASE`, 조인트 6개(매트 X·Y 이송, 매트 회전, 헤드 회전, 노루발 들기, 바늘), 동작 연구 `대기`·사이클 3개(큰·작은·홈 매트)·꺾임 정밀 3개, 작업 대상 모형 3종과 가공 뒤 형상·떨어진 조각(임시값, 결정로그 P-01~P-06). 기계 부품은 아직 없음.
- `tools/gen_motion_prep.py`(준비물 명령 스크립트 생성기), `tools/motion_states.json`(동작 연구 상태 → 단계 표).
- 보고서 `docs/reports/mechanism/mech_prep_check.md`(준비 점검), `mech_prep.md`(준비).
- 설계 요구서 초안 `docs/design-requirements.md`(엔진 양식, 과제 T01~T07).
- 결정로그 `docs/decision-log.md`(대화 단계 C-01~C-08, 예전 ADR 목록).
- 자료대기 목록 `docs/waiting-list.md`(D-01~D-15).
- 벤치마크·특허 조사 `docs/benchmark.md`(R375X·R375A, Richpeace, 만료 특허 7건).
- 엔진 기본 배치 폴더: `docs/reports/`, `tools/`, `purchased-step/`, `fea/cases/`, `fea/results/`, `deliverables/`.
- CAD를 SolidCraft로 정함(결정로그 C-09): `tools/config.json`(cad·doc), 설계 파일 폴더 `3D_Modeling/`, 자료대기 D-16(이 컴퓨터 실행 준비).

## Changed

- 엔진 v3.4.0(실행 속도)에 맞춤: `tools/run-rules.md` 2번 — 연결은 실제 응답으로 판정(WF-121), 동시 과제 묶음(E-25)은 CLI·`base.sc`+`edit.json`→후보 .sc, 짧은/긴 계산 경계(안내서 '연결'), 원복 주의(checkpoint, 저장 뒤 편집 금지). 15번 신설 — 동시 과제 첫 실행 재실행 확인(`tools/out/replay_check.json`), 서명 해시 첫 전수 측정. `tools/workflow-args.json` `parallel: true`·date 2026-11-02. 결정로그 '외장 단계 과제' 표(X-01 T12 커버·문, X-02 T07 가드틀). `docs/reports/engine-candidates.md` WF-131·WF-132 반영 표시. 실측 정리 `docs/reports/solidcraft-mcp-cli-timing.md`.
- 요구서 8-2(설계 파일 이름·버전 규칙, v0.0.0 시작), 8-5(버전이 바뀔 때만 커밋·푸시), 8-6(CAD SolidCraft). 자료대기 D-15 해결.
- 시작 설계 `3D_Modeling/FSAP_v0.0.0.sc`(사용자가 앱에서 만든 빈 설계).

- 저장소를 MAT-RS-001 기구 개발 폴더로 바꿨다(결정로그 C-07). 기구 모델링은 MechDesign_Engine으로 한다.
- `README.md`, `CLAUDE.md`를 기구 개발용으로 다시 썼다(한글).
- ADR-004 상태를 Superseded로(C-07).
- `.gitignore`에 `tools/out/` 추가.

## Fixed

-

## Removed

- 6단계 폴더 `01_Planning` ~ `06_Business`(비어 있었음).
- `DECISIONS.md`(ADR 목록은 결정로그 "예전 ADR" 절로 옮김), `docs/decisions/ADR-TEMPLATE.md`(새 ADR을 만들지 않음).

## Deprecated

-

## Documentation

-

## Security

-

---

# [0.1.0] - 2026-07-29

## Added

- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

- Initial FSAP repository created.
- Project documentation established.
- README.md created.
- CLAUDE.md created.
- DECISIONS.md created.
- ADR management structure established.
- Initial Architecture Decision Records created (ADR-001 ~ ADR-004).
- Created phase folders (01_Planning ~ 06_Business).
- Created docs/decisions/ with ADR-TEMPLATE.md.

## Documentation

- Defined project vision.
- Defined repository structure.
- Defined documentation structure.
- Defined development workflow.
- Defined AI operating guidelines.
- Defined GitHub workflow.
- Synchronized CLAUDE.md with README.md: added ADR Management Rules and GitHub
  Rules sections, redefined DECISIONS.md as an ADR index, aligned CHANGELOG
  categories, and allowed phase repetition/overlap in the workflow.

---

# Changelog Rules

This file records completed changes only.

Do not record:

- Planned features
- Future ideas
- Discussions
- Draft documents
- Experimental concepts

Record only completed work.

---

# Categories

## Added

- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

New functionality.

---

## Changed

Behavior or architecture changes.

---

## Fixed

Bug fixes.

---

## Removed

Removed functionality.

---

## Deprecated

Features scheduled for removal.

---

## Documentation

Documentation updates.

---

## Security

Security-related improvements.

---

# Versioning

This project follows Semantic Versioning.

MAJOR.MINOR.PATCH

Example

v0.1.0

Initial release

↓

v0.2.0

Feature additions

↓

v0.3.0

Major improvements

↓

v1.0.0

Official release

---

# GitHub Release Policy

Each official GitHub Release should have a matching version in this file.

Example

GitHub Release

v0.2.0

↓

CHANGELOG

# [0.2.0]

The release notes and changelog should describe the same completed changes.

---

# Related Documents

README.md

Project overview.

CLAUDE.md

AI operating rules.

DECISIONS.md

ADR index.

docs/decisions/

Architecture Decision Records.

---

# Notes

Always keep the **Unreleased** section at the top.

When a new version is released:

1. Create a GitHub Release.
2. Move all completed items from **Unreleased** into the new version.
3. Create a fresh **Unreleased** section.
4. Keep versions in reverse chronological order.

---
