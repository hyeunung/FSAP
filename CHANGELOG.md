# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

- v2.12.2 RX-08 수정 2회차: 타임라인 Remove86(97923) 대상이 없는 이름 SSEB13-220_RX06_RAIL이라 오류로 남아 보이던 STEP 원본 레일 Chamfer2(X −335~235, 관 클램프 L_4·L_5와 겹침)를 Remove86 대상을 Chamfer2로 바꿔 지움. 그린 상자 레일 SSEB13-570_RX06_RAIL(X −335~−125)은 그대로. 레일·블록 ↔ 이웃 21개 겹침 0(레일–L_5 13.0, L_6 9.0). 열기 오류 0. 보고서 docs/reports/mechanism/mech_RX-08_model2.md
- v2.12.1 RX-08 수정 1회차: 스토퍼 관 TU0604_M08P_RX08_A·_B를 세움 Z 340에서 U4 쪽(새 컴포넌트 TU0604_M08P_RX08_A_U4·_B_U4, U4_WHEEL_N 아래 강체 — J_U4_X를 따라감)·U8 쪽(정적)으로 나눔. 길·굽힘 R15 그대로. 검사: J_U4_X 95 실제 구동에서 새 U4 바디 ↔ 고정 이웃 겹침 0, J_U4_PRESS 13.006·3.751·0·−4.11(STOP 0)·13.006·0.95(STOP 20) 실제 구동 겹침 0, joint.sweep 멈춤 0.932°(메시 공차 0.229), 0.95°에서 머리–그네 0.0147. machine.json U4_WHEEL_N 부품·doc. 보고서 docs/reports/mechanism/mech_RX-08_model1.md
- v2.12.0 RX-08 U4 중간 높이 스토퍼(C-42, D-163): 새 컴포넌트 U4_STOP(U4_WHEEL_N 아래: 로드·P_RX08_STOP_BLOCK_밀링 SUS304·CB8-20·STEP대기_NUT-M8)·STEP대기_CDQ2A25-20DMZ, 받침 P_RX08_STOP_BRKT_밀링(SUS304), CB5-16 ×6, KQ2L06-M5A ×2, 관 TU0604_M08P_RX08_A·_B(보 앞 Z 391/381, 클램프 F 밑). 조인트 J_U4_STOP(직동 0 OFF~20 ON), REST 키, machine.json 상태 FLOAT_10_2. BASE M5 탭 2·관 장공 넓힘, 캐리지 발 장공 넓힘. U8: 매니폴드 07 → STEP대기_SS5Y3-20-08_M08, 8번 밸브 SY3120·KQ2L06 ×2 복사, 마개 TPH ×3·CB4-25 ×2 +10.5. 멈춤각 CAD 0.95°(머리–그네 0.0014). 보고서 docs/reports/mechanism/mech_RX-08_model.md
- v2.11.1 RX-06 수정 1회차(형상 값 변화 0): P_M02_BASE·ARM_SIDE_N·_P·ARM_TIE를 고치던 루트 피처 34개를 component.move_features로 U4_WHEEL_N(24)·U4_PRESS(10)에 옮김(J_U4_X 이동 때 조각이 남던 원인). 레일 STEP 자르기·축 계단 단면은 못 함(축은 STEP 끝 가공 Ø15가 BSW20·BUN20 Ø20 저널과 안 맞아 보고, D-191). J95 형상·9점 간섭 미확인. BOM docs/bom/FSAP_v2.11.1_*(v2.11.0과 같음), 보고서 docs/reports/mechanism/mech_RX-06_model1.md
- v2.11.0 RX-06 U4 X 위치 조절축(C-42, BOM docs/bom/FSAP_v2.11.0_*): 새 컴포넌트 U4_XAXIS(보 앞 SSEB13 레일 2줄 Z 266·440 X −335~−125, BSW20·BUN20 + 스페이서 F·S, 끝 멈춤 P_RX06_STOP_A·B), U4_XCAR(P_RX06_CARRIAGE A5052, 블록 4, BSS2020 너트, CB6-20 ×4, 발 볼트 CB5-16 ×6), BSS2020-1100_RX06(축 Ø20×351) + STEP대기_HANDLE_D50, U4_DISK_BASE(원판 받침 묶음을 테이블에 강체). 조인트 J_U4_X(직동 0~95, d₁ = 100 + J)·J_U4_XSCREW(링크 18°/mm), U4_WHEEL_N ↔ 틀 강체를 캐리지 강체로 바꿈. P_M02_BASE 보 밑 연장·윗면 248·탭, P_M02S_CYL_BRKT 윗날개 Z 236~242, 볼트 BEAM_1·2 −8·BASE_4 (−159,110), 관 U6·U4_A2·U4_B 다시(X −84 통로), 클램프 L_6 −106. 보고서 docs/reports/mechanism/mech_RX-06_model.md
- v2.10.4 SIM-01 2회차(형상 변경 0): v2.10.3에서 숨김으로 저장된 L 매트·테이프 조각(MAT_L·SEAM_L·TP_L_* 48바디)을 켜서 저장(S·G·V는 같은 자리 대안이라 숨김). M02R 저장본에 대고 U4 묶음 간섭 5연구 겹침 0(truncated false), 영상 5연구 각 167프레임(tools/out/mech_SIM-01/anim3). 보고서 docs/reports/mechanism/mech_SIM-01_model.md
- v2.10.3 M02R 3회차(C-41, 판정 일부 — E-05상 v2.11.0이었어야 함, v2.11.0에서 바로잡음; BOM·설계검토서 docs/bom/FSAP_v2.10.3_*, docs/review/FSAP_v2.10.3_review.md): U4 누름을 보 고정 사각 실린더 + 축 X 그네 브래킷으로. 옛 모터 위 크랭크 묶음(CDM2C20-25Z·I-020B·엘보·관 U4C·CYLBRKT·CRANK·볼트) 바디와 조인트 J_U4_CYL_PIN·CYL_ROD·ROD_PIN 지움(빈 컴포넌트 21 남음), base 세운 다리 지움. 새 `P_M02S_SWING`(A5052, 피벗 (Y 120, Z 140) 축 X, 텅 장공)·`P_M02S_CYL_BRKT`(SUS304 t6, 보 밑)·`P_M02S_PIVOT_BRKT_A·_B`·`P_M02S_SPRING_TAB_1·_2`, `STEP대기_CDQ2YA20-25DMZ`(저마찰 임시, D-188)·`_ROD`·`STEP대기_Y-020B`·`STEP대기_PSFJ12-200`·`STEP대기_PSCS12-10_1·_2`·`STEP대기_AUT12-45`(D-189), KQ2L06-M5A ×2, CB5-12 ×14·CB5-16 ×2·CB5-20, 관 U4_A2·U4_B 끝 다시. J_U4_PRESS 축 X(−4.11~13.006), J_U4S_ROD(0~25)는 선형 링크로 따라감, 연구 9개 키 환산. 패킹 마찰 f 9.42 N 넣어 IR1000 0.102 MPa·스프링 57.4 N → 회전 SF 1.013~1.079, 자국 SF 최소 1.013
- v2.10.2 M02R: U4 바퀴 누름을 누운 실린더 + 핀 축 크랭크로(C-40). 보유 CDM2C20-25Z·I-020B·엘보 2를 모터 위에 눕힘(고정 핀 (−161.006, 225), 크랭크 핀 θ0 (−347.8, 203.6), 6.54°), 새 `P_M02R_CYLBRKT`(SUS304)·`P_M02R_CRANK`(A5052 포크)·`P_M02R_CRANK_PIN`(S45C)·`P_M02R_CRANK_WASHER`·CB5-16 ×4·CB5-20 ×2·CB4-12 ×2, 옛 P_M02_CYLBRKT·CB5-12 ×2·너클 핀 묶음·CB4-12 ×2 지움, 팔·BASE 옛 구멍 메움. 조인트 J_U4_CYL_PIN·J_U4_CYL_ROD(0 = 내림 끝, 24.97 = 들림)·J_U4_ROD_PIN 다시, 고리 오차 0. U8: KQ2L06-01AS_M08R_IN_1, STEP대기_KQ2R06-08A_2, 관 U4_A1·U4_A2·U4_B·REG1_SUP·U4C_A·U4C_B, 클램프 F_6 + CB5-16 ×2, L_2 구멍 r 3.25, KQ2L08 IN 지움. 40 N = 0.0768 MPa, 모터 위 최고 Z 336 → 255. machine.json 조인트·`_reserved` D-163. 생성기 `tools/gen_v2_m02r.py`, 보고서 docs/reports/mechanism/mech_M02R_model.md
- v2.10.0 SIM-01: 봉제 진행 테이프 시뮬레이션 — 새 컴포넌트 `U7_TAPE_LINE`(TL_UP 롤→G1→TOP→세로 20,814 mm³, TL_TWIST 비틀림 90° 7,528, TL_LOW 슬롯→출구 r4→28° 9,298.9, U7_ROLL_MOUNT 리지드)·`U7_TAPE_FEED`(TL_FEED ㄷ자 225, U7_CASSETTE 리지드), 자리 상자 U7_TAPEWAY_H·V와 그 BodyTransfer 지움, P_M05_GUIDE 출구 필렛 R3(136,639.8 → 136,623.3). TAPE_L·S·G·V를 땀 선 호 ≤150(L 2조각 155.2) 조각 118개로 나눠 컴포넌트 `WP_TP_<M>_nn`·`WP_TP_<M>_SEAM` 122개 + 슬라이더 `J_TP_*` 122개(0 붙음·2000 대기), 연구 REST·CYCLE_L·S·G1·G2·V 키(땀이 조각 끝을 지난 단계에 붙임). machine.json joints·units·studies·baseline. 보고서 docs/reports/mechanism/mech_SIM-01_model.md
- v2.9.0 U6S: U6 슈 세로 누름·들기 — 세운 CJ2B10-15Z_M06P(받은 STEP, 축 X −8 · Y −152) + 판금 브래킷 P_M06_PCYL_BRKT(SUS304 t3) + 턱 칼라 P_M06_SLIDE_COLLAR_1·2, 슈 벽 Z 50·판금 윗날개·장공 7.1×17.1, 새 조인트 J_U6_PRESS(U6_SHOE → U6_PRESS, −5.0~+4.5, 대기 +4.5)와 연구 9개 키(피벗·대기 들림, 직선 봉제 −0.4), machine.json. 관 U6P_A·_B 움직이는 쪽, 7번 밸브·STEP대기_SS5Y3-20-07_M08(06 바디 지움). IR1000:3 0.18 MPa → 8.71~21.59 N, 여유율 1.344, 자국 SF 2.09, 회전 SF 1.009~1.047. 과제 범위 겹침 0. 미완: 고정 쪽 관·고리·U8 회로 다시 잇기
- v2.9.0 U6S 문서: BOM `docs/bom/FSAP_v2.9.0_*.csv`, 설계검토서 `docs/review/FSAP_v2.9.0_review.md`, 결정로그 '구동 U6S 결과'(디테일 U6S-D1~D9, 기울기 자국 SF 1.35 < 2), 요구서 U6S 일부, 해석 손계산 `fea/cases/mech_U6S_handcalc.py`
- DC-03 닫음(C-38, 2026-11-11, v2.8.13 그대로 — 형상·조인트·연구 키 변화 0): L 1500·G 1200 모서리 U4+U5 그대로, U4 혼자는 U5가 매트 밖인 짧은 구간만(G1 바닥·출구, V 꼭짓점·입구2). 판정 선 구름 c_max 0.0202(μ 0.4·면밀도 6, 7절 실측 조건), L U4+U5 c ≤ 0.021. 요구서 DC-03·FUNC-01 ②·⑦·7절, 자료대기 D-95·D-96, machine.json _timing 메모·한계 c_max, 결정로그 DC-03-K1~C4. 보고서 docs/reports/mechanism/mech_DC-03_model.md
- v2.8.13 DC-04: 회전(피벗) 중 노루발 봉제 높이·낮은 누름(C-39). 동작 연구 CYCLE_L·S·G1·G2·V의 J_U3_PRESSER 키(회전 중 0, 들림 20은 로딩·배출만), machine.json states 13개·_timing 9곳(노루발 끌림 T_f 0.096 N·m 포함, 최저 SF 1.009, F4 ≤ 15.9 N, 바늘 옆힘 ≤ 9.8 N). 형상·조인트·구매품 변화 없음. 회전 자세 7점 겹침 0. 결정로그 DC-04-M01~M05, 보고서 docs/reports/mechanism/mech_DC-04_model.md
- v2.8.12 PNEU-01R 수정 1회차: 체인 고정 끝 임시 형상 STEP대기_2400.05.12PZ_F의 관 통로 (Y 250, Z 661) 축 X만 r 3.25 → 3.75(Ø7.5). 검도 문제 12PZ_F ↔ TU0604_M08P_U5_A 3.648 mm³ → 0(최소 0.217 mm). 부피 −87.96 mm³, 이웃 통로 살 5.0. 관·조인트·볼트 변화 없음. 결정로그 PNEU-01-M15, 보고서 docs/reports/mechanism/mech_PNEU-01R_model1.md
- v2.8.11 PNEU-01R: 공압 관–구멍 벽 겹침 2쌍 해소 — P_M08_TUBE_COMB_U5_2 구멍 (−1235.5, 190, 661) 축 −X, P_M08_RISER_COMB_1 구멍 (1049.75, 53) 축 Z만 r 3.25 → 3.5(Ø7.0, 높이 그대로). 부피 −84.8·−42.4 mm³, 관 ↔ 빗 최소 0.370·0.109 mm, 겹침 0, 이웃 구멍 살 7.67·7.75. 관 경로·조인트 변화 없음. 결정로그 PNEU-01-M13·M14, 보고서 docs/reports/mechanism/mech_PNEU-01R_model.md
- v2.8.10 LITE: 모델 무게 줄이기(형상 변경 0). P_M07_BEAM 탭 37 + Cylinder989를 Box16 바로 뒤 스케치 3장 extrude cut으로, 필렛 띠 탭 4는 끝 Combine 하나로, 앞판 X 구멍 메움·다시 뚫기 16개 지우고 옛 cut r 2.1로(timeline.delete 63). CLI 열기 844.4 → 396.9 s(−53 %, 상한 240 s 미달 — 남은 무게 디테일). lite_check 바디 2,969·BOM 179행/2,616·모델 bbox 차 0, 보 부피 −2.6 mm³. 앱 문서 dirty라 CLI로 저장. 보고서 docs/reports/mechanism/mech_LITE_model.md
- v2.8.9 DC-01: 형상 변경 없음(문서 설명만, 조인트·스케치 숨김). C-37 (다) U홈 CYCLE_G1 바닥 U4 혼자 69°(321~390단계) 시간 키 3.0 + 3.4×5 = 20 s 그대로 확인 — 구름 0.02 SF 1.057, 원판 끌림 포함 1.024. 같은 바닥 U4+U5 피벗 0.8 → 1.2 s(U5 밑 띠 μs 0.30 SF 0.836 → 1.054, `tools/machine.json` `_timing`). 과제 범위 5점 새 겹침 0. FUNC-01 ⑥·⑦(홈 매트 92.8 s)·D-96·요구서 DC-01 고쳐 적음. 계산 `tools/out/mech_DC-01/g1calc.json`, 보고서 docs/reports/mechanism/mech_DC-01_model.md
- v2.8.8 PNEU-01 수정 2회차: 검도 1회차 문제 6건 — CLAMP_F_5 X −120 → −100(U4_B 꺾임 원호 밖), CLAMP_SO_1 블록 X 981~997 + REG1_OUT 멍에 X 904~920(볼트 옛 탭 X 944·976, 보 Z 262 탭 메움 커널 실패), COMB_KDM 앞판 Y 112~120 → 88~96 + 날개·보 귀, U7_4/5/6_B 꺾임 Z 775 → 781·R 30 → 20(+41.3 mm), AIR_IN_BRKT Z 256~304·볼트 Z 261·299, BRKT_CST_V 띠 폭 13 → 30·윗판 Z 532·아래판 FEED_A 여유 구멍(오조작 SF 0.70 → 1.53). 새로 그린 기운 관 구멍 길이 늘림. 보 탭 메움 4·새로 4. 관–고정품 겹침 0, 고정 간격 26줄 ≤ 300. BOM v2.8.8, 생성기 `tools/gen_v2_pneu01_fix2.py`, 결정로그 PNEU-01-M6~M12, 요구서 7절 통구멍 관 항목.
- v2.8.7 PNEU-01 수정 1회차: 공압 관 고정품 30개(빗·클램프·브래킷, A5052, 관 통구멍 Ø6.5/Ø8.5) + CB5-16 57개(기존 STEP occurrence 복사)·M5 탭, U5 체인 2400.05.075.0 23링크 행정 표시 모형(아래·위 가닥 17+17, 굽힘 5, 슬라이더 35 + J_U5_X motion link, 링크 안 관 토막·굽힘 관 R 81.5/69.5 — 체인 안 관 1,078.4·1,040.7 일정), 옛 체인 바디 22 지움, 체인 고정 끝 STEP대기 관 통로 ×2, CST_O SPCC·볼트 2, AIR_IN_BRKT 볼트 2. BOM `docs/bom/FSAP_v2.8.7_*`, 자료대기 D-155~D-161(PNEU-01 D-a~D-g), 생성기 `tools/gen_v2_pneu01_fix1.py`.
- v2.8.6 PNEU-01(일부): 공압 관 25줄(직각 꺾기) → 26줄 접선 원호 굽힘(최소 R 16/40, 바디 35, TU0604 29.9 m·TU0805 0.8 m, `tools/gen_v2_pneu01.py`). 밸브 1·3 −Y 10 + 개별 급기 스페이서 STEP대기, 레귤 OUT KQ2L08 → KQ2L06-01AS 실물 STEP ×2, 새 이음·막음 STEP대기(KQ2E08·KQ2T08 ×2·KQ2H08·AN110 ×2·TPH-01 ×3·M-5P·KQ2P-06 ×8·AS2201F-01-06S ×2), 받침 P_M08_AIR_IN_BRKT, 카세트 빗판 P_M08_TUBE_BRKT_CST_O(수정 2 지시). 미완: U5 체인 다시 그리기·체인 안 관, 고정품 29·볼트 62, 움직이는 축 행정 검사(보고서 mech_PNEU-01_model.md).
- v2.8.5 VGR-01 수정 1회차: 형상 변경 없음(문서 설명만). 검도 지적 — U5 바퀴 밑 고정 PTFE 띠(P_DC205_STRIP) 미끄럼 μs·40 N·0.44가 회전력 셈에 빠짐 → `tools/machine.json` `_timing` CYCLE_V U4+U5 키 μs 0.30 기준: 입구1 2.5→4.1 s, 꼭짓점 25° 1.2→2.0 s ×4, 10° 1.0→1.3 s, 입구2 30° 1.5→2.6 s, 입구2 U4 혼자 9.0→9.5 s(원판 끌림). 최저 SF 1.009(`tools/out/mech_VGR-01/fix1calc.json`). 자료대기 D-154·D-96·D-97, 결정로그 VGR-01-M5, 설계검토서 v2.8.5. 저장 전 조인트·스케치 숨김. 보고서 docs/reports/mechanism/mech_VGR-01_model1.md
- VGR-01 완료 판정(2026-11-10): 해결. BOM v2.8.5(v2.8.4 그대로), 설계검토서 v2.8.5 완료 판정 절, 결정로그 "구동 VGR-01 결과", 요구서 VGR-01 해결.
- v2.8.4 VGR-01: 좁은 V홈 시험 매트 **WP_V** 새로(D-150 V 30°·R_b 2·깊이 150, U홈과 같은 자리) — 컴포넌트 `WP_V_X`·`WP_V_Y`·`WP_MAT_V`(MAT_V 1200×1200×10, V30_r2 빈 곳)·`WP_TAPE_V`(TAPE_V 두께 1·날개 10, SEAM_V), 리지드 묶음, 모형 조인트 `J_WP_V_X`·`J_WP_V_Y`·`J_WP_V_ROT`(대기 중심 (−593.5, −300), WP_G와 같은 자리). 연구 **CYCLE_V 486단계**(입구1 피벗 0→75° · 위 벽 142.8 · 꼭짓점 호 r 8.5·75→−75° · 아래 벽 · 입구2 피벗 −75→0°, J_U5_X 1360(d₂ 440), U5는 ROT −35 정지 단계 321에서 들고 −30 정지 단계 440에서 내림, J_U4_PRESS 전 구간 0). 다른 연구 8개에 J_WP_V_* 0 키. 30자세 과제 범위 clearance 새 겹침 0(바늘 기준선 MAT 20.1·TAPE 22.1 mm³뿐), U5↔TAPE_V 맞닿음 0(−35에서 MAT 0.021), 바늘–홈 벽 틈 최소 5.7. machine.json(조인트·유닛·연구·states 4·baseline L·S·G·V·_timing), 생성기 `tools/gen_v2_vgr01.py`. 기계 부품·BOM 변경 0. 보고서 docs/reports/mechanism/mech_VGR-01_model.md
- v2.8.3 F01-C1: 작업 대상 모형 땀–가장자리 거리 e 0 → 6.5(D-78·D-144). `J_WP_L/S/G_X`의 a 원점(U1_FRAME)을 +6.5 X로 옮겨 사슬 전체(WP_k_X·Y·MAT·TAPE·SEAM)가 +6.5 X — REST 가장자리 X 6.5(MAT 3장), 중심 (−743.5/−143.5/−593.5, −300), ROT 10°에서 중심 그대로. 연구 CYCLE_L·S·G1·G2의 `J_WP_k_X·Y` 키를 피벗 단계만 새 값으로(최대 6.5, 단계 수·다른 22키 그대로), SEAM_U7 그대로. 19자세 확인 새 겹침 0(바늘 기준선 MAT 20.1·TAPE 22.1·SEAM 1.01 mm³). `tools/machine.json` 원점·states 10값·기준선, `tools/gen_v2_prep.py` E_EDGE 6.5. 저장 전 조인트·스케치 숨김(실행 규칙 19). 형상·부품 수 변화 0
- v2.8.2 COLOR-01: 모델 색 통일(형상 변화 없음). 색표 13칸(결정로그 COLOR-S1) — 재질 색 편집 6(SCM435 #b4b9bf, A5052·A6061 #ccd0d6, S45C·SK5 #9ea4ac, PET-CF #d4d4d0, 재질 이름·밀도·배정 그대로) + 바디 외관 지정 231 원본 바디(COL_F_FASTENER·COL_PM·COL_RW·COL_RG·COL_PT·COL_SF·COL_EV·COL_TP·COL_WP). 2,729 바디 색표 밖 0, 체결 1,198 흑색 0. 피처 2,303·바디 632·BOM 변화 0. 보고서 docs/reports/mechanism/mech_COLOR-01_model.md
- v2.8.1 FUNC-01 수정 1회차: U5 플로트 옆판 `P_M03_LIFT_SIDE_N/P` 웹에 축 여유 구멍 Ø16.5(중심 (−1847, ±43), REST Z 115~130)를 깎음 — `PSFJ16-150_F01_N/P`가 웹을 Z 116~129에서 2 mm 파고들던 겹침(검도 v2.8.0) 해소. 옆판 부피 −248.1 mm³씩, 플랜지 Ø16 H7(Z 130~136)·받침 블록 그대로. 조인트·행정·연구 변화 없음
- v2.8.0 FUNC-01: 먼 쪽 바퀴 **U5 플로트** — 새 컴포넌트 `U5_FLOAT`(옆판 N·P·앞판·센서·HG-KR23_M03W·PGX62-H-10_M03W)·새 `U5_LIFT`(승강판·MGP 끝판+봉), 새 조인트 `J_U5_FLOAT`(Z 0~20), LHFR16 ×2·PSFJ16-150 ×2(실물 STEP), 축 받침 `P_F01_SHAFT_HLD_N/P`, `STEP대기_PSCS16` ×4, 와셔 `P_F01_SPRING_SEAT` ×2, `STEP대기_SPRING_d1.6_OD44_L132` ×2. 옆판 위 플랜지 Z 156 → 136, 앞판 140 → 134, 승강판 서보 창·−Y 넓힘, CB5-12_M03_7~10 지움. 바인더 `U7_BINDER` → 접는 바인더 `P_M05_BINDER`(2단 45° 접기 통로, PA12/SLA), 바늘판 아랫날개 홈 1.4. `IR1000-01BG_M08:2` 묶음(브래킷 볼트 2·이음 2·관 2) 지움. 연구 8·states 26·회귀 자세의 J_U5_LIFT 0~2 → (−10, FLOAT v+10). 과제 범위 겹침 0. 보고서 docs/reports/mechanism/mech_FUNC-01_model.md, 결정로그 F01-M1~M4
- v2.7.0 MOT-01: 서보·감속기 C-36 실물 교체 — `STEP대기_MHMF022L1U2M`·`_U5X`·`_U5W`·`STEP대기_VRXF-PB-60-10`·`_U5X`·`_U5W` → `HG-KR23_M02`·`_M03W`·`_M03X`, `PGX62-H-10_M02`·`_M03W`·`_M03X`(실물 STEP), U3 아랫축 새 묶음 `HG-KR43_U3` + `P_U3_LDRV_BRKT` + `STEP대기_SCXW46-14-15`(U3_LOWER_DRIVE X 40~368로 줄임). 체결: CB5-16 ×32·CB5-12 ×4·CB4-12 ×4·SFB5-12·HNTT8-5 ×4·MPFZ12-10 ×2, 핀·스페이서·와셔 가공품 11, 옛 CB5-20 ×12 지움. 앞판 Ø50 H8 관통·M5 관통 탭, 팔·승강 옆판 안쪽 홈 2, 바퀴 허브 막힌 구멍·키홈, U5X 브래킷 웨브 Y 82, 아이들러 축 Y 90~115, 옆면 볼트 Z ±15 → ±19(Ø50 구멍과 겹침 풀기). BOM `docs/bom/FSAP_v2.7.0_*.csv`, 결정로그 MT-01~06
- v2.6.8 STEPSWAP r4: 레귤레이터 `STEP대기_IR1000-01BG_M08_N/F/S`(+_BRKT) → SMC 실물 STEP `IR1000-01BG_M08:1~3`(몸통·게이지 G33-2-01·세트 너트·브래킷 P36201023, X 700·800·900). 실물 치수대로 포트 Z 511 → 482(손잡이 윗면 Z 565 그대로), 몸 폭 ±12.5 → ±17.5, 브래킷 뒷면 Y 120 = 보 앞면. 브래킷 볼트 CB5-12_M08_PY ×6 → CB4-12_M08_REG ×6(열쇠 구멍 M4, X ±14 · Z 527.8). 이음 KQ2L08-01AS → `_M08R_PX/NX`(포트 면 X ±17.5 · Z 482), 관 TU0805 6줄 → `_M08T_REG_*`(매니폴드 쪽 끝 그대로). 조인트·행정 변화 없음. 과제 안 새 겹침 0. 게이지 시선 틈 3.2 → 약 17.9(손계산, M08-X6). BOM FSAP_v2.6.8_*, 자료대기 D-132, 보고서 docs/reports/mechanism/mech_STEPSWAP_model.md

- v2.6.7 REG-02 수정 1회차: 장공 볼트 CB5-16_REG02_1~4 → CB5-20_REG02_1~4(미스미 실물 STEP, UPPER 물림 6·7 → 10, 조임 암나사 전단 SF 1.15 → 1.92), 1·2 밑 와셔 `STEP대기_WASHER_M5_REG02_1·2` 새로(네 볼트 같은 쌓임), UPPER 탭 3·4 깊이 10 → 12. 4번 볼트 자리 X 36 → 33(판 장공·HOLDER 날개 A 장공·Ø5.5 구멍·UPPER 탭·와셔 DC204_2 함께) — 렌치 길이 h +6·카세트 장착에서 핀 MSTH6-20_M05:2에 걸리던 것 0.75 비킴(날개 A 장공 가장자리 ↔ 굽힘선 7.25 → 10.25, DC2-04-X2도 풀림). 조인트·행정 그대로. 과제 범위 J_U7_HGT −4·−1.5·1·3.5·+6 × SHIFT 0(−4·+6은 −60도) 겹침 0, 렌치 프로브 4 겹침 0. 보고서 docs/reports/mechanism/mech_REG-02_model1.md

- v2.6.6 REG-02(C-34): U6 센서 묶음·U7 카세트 걸이 높이 조정을 하나로. `J_U6_HGT` 지우고 U6_SENSOR를 U7_FIXED에 리지드 `J_U6_ON_U7FIX`(조정은 `J_U7_HGT` 하나, −4~+6). 공통 높이 판 `P_REG02_HGT_PLATE`(SUS304 t5) + 압입 스터드·너트 ×4(STEP대기, D-142), 장공 볼트 CB5-12 ×4 → CB5-16_REG02_1~4(실물 STEP), 와셔 −Y 5, BASE·HOLDER Ø4.0 구멍 각 2, 오류 피처 Move15·16 지움. 회귀 자세 183 → 181점(옛 POSE 8·9 뺌, `tools/gen_v2_poses.py`), machine.json states J_U6_HGT 키 지움. 과제 범위 겹침 0, KDM10 짝 축 0. 미완: GUIDE↔CARR 틈 2.0 < 10(예외 요청). 보고서 docs/reports/mechanism/mech_REG-02_model.md

- v2.6.5 LITE(모델 무게 줄이기, WF-196): 형상·부품 수·BOM은 그대로 두고 피처 이력만 바꿈. P_M07_BEAM — Box16을 처음부터 X −2380~1230·Y 120~320으로, 구멍 묶음 HB·HK·HT를 R12·속 앞으로, 외곽 깎기 SK_M07_BEAM_OUT+Extrude51·끝 늘이기 OffsetFace20 지우고 Fillet1(R12 긴 모서리 4), 속 IN X −2381·3612(boolean retry 6 → 1). P_DC205_STRIP — Hole1~8 → SK_DC205_TAP+TAP_DC205 cut 한 번 + cosmetic 나사 M5 ×8. CLI 열기 242.1 s → 100.1 s(상한 240). BOM 125행/2,457 같음, 다른 바디 2,647개 bbox·무게중심 차 0, 모델 bbox 같음, 보 공칭 복귀(+27.8 g). 앱 문서 dirty라 CLI run --save. 생성기 gen_v2_m07·gen_v2_m07_fix1·gen_dc2_05 고침. 보고서 docs/reports/mechanism/mech_LITE_model.md

- v2.6.4 STEPSWAP r3: STEP대기_CB5-6_M08_PY_LC2F ×2(옆 투광 L 날개 → 2E 금구 M5 탭) → 미스미 CB5-6 실물 STEP `CB5-6_M08_PY_LC2F:1·:2`(같은 자리·bbox, U8 리지드 9282·9283). 조인트·행정 변화 없음. 과제 안 새 겹침 0(나사 물림 unchecked 2는 M-08 의도). BOM FSAP_v2.6.4_*, 자료대기 D-135, 보고서 docs/reports/mechanism/mech_STEPSWAP_model.md

- v2.6.3 REG-01: 동작 연구 키만 바꿈(형상·조인트 정의 변경 없음). CYCLE_L·S·G1·G2·MAINT_HEAD에 U7 조인트 6개(J_U7_CST_X·CST_Y·CUT·TUCK·FEED·LATCH) 대기값 0 키, SEAM_U7에 CST_X·CST_Y·LATCH 0, MAINT_U7에 CUT·TUCK·FEED 0 — 연구 전환 때 U7 상태 넘어옴 0(U7_BINDER 대기 상자 확인). 회귀 CYCLE_L 79~379 중 282단계 기준선 밖 겹침 0, 남은 약 2,100단계·자세 218점 못 본 범위. 보고서 docs/reports/mechanism/mech_REG-01_model.md

- v2.6.2 DC2-08 수정 1회차: 형상 변경 없음(문서 이름·설명만). 소켓 KDM10S-06_M08 ↔ 밸브 쪽 관 TU0604_M08K_U7_1~6을 J_U7_HGT −4·0·+6에서 CAD 실측(검사 사본에서만 관 −X 0.02 떼어 같은 평면 맞닿음 제거) — 겹침 0, unchecked 0, truncated false. CB3-10 머리 ↔ 관 2.5 안 0. 보고서 docs/reports/mechanism/mech_DC2-08_model1.md

- v2.6.1 DC2-08: KDM10 다관 커넥터 소켓 받침 `P_M08_KDM_BRKT` 새 형상(앞판+기둥+발, A5052)으로 걸이 `P_M05_HOLDER` 날개 C 위(M5 탭 2 새로)에 CB5-12_M08_PZ_KDM ×2로 고정, 소켓·CB3-10 ×4·받침을 U8_PNEU → U7_FIXED 리지드(J_U7_HGT 따라감). 옛 CB5-12_M08_NZ_KDM ×2 지움. HGT −4·0·+6 × CST_X 0·25에서 짝 축 어긋남 0, 과제 범위 겹침 0. 결정로그 DC2-08-M1~M4, 보고서 docs/reports/mechanism/mech_DC2-08_model.md

- v2.6.0 M08R(C-32): 라이트 커튼 임시 F3SG-4RA1520-14 ×4 → Omron F3SG-4RA0800-14 실물 STEP 2세트(앞 1E·1R, 옆 2E·2R, Z −45~818). 기둥 HFS8-4080-2370 → 1650(FL), 1900 → 1175(FR·R), 위 캡 내림. 위 금구·LC2F 판·CB5-12 ×4·HNTT8-5 ×4 Z −700. 2E 금구 볼트 CB5-12 ×2 → STEP대기_CB5-6. 금구 8 → STEP대기_F39-LSGF(이름·형번). 금구 4 컴포넌트 U8 리지드 묶음. 과제 안 새 겹침 0. 컴포넌트 생김·없어짐으로 가운데 자리(E-05). 중간 파일 v2.5.10(같은 형상). 결정로그 M08R-M1~M4·S3, 보고서 docs/reports/mechanism/mech_M08R_model.md

- v2.5.9 STEPSWAP r2: STEP대기 CB6-16 ×2(U5 승강판 → MGP 끝판)·CB4-25 ×4(SS5Y3 베이스 → 보 앞벽) 미스미 실물 STEP으로 교체(같은 자리, 조인트·행정 변화 없음). 과제 안 검사 새 겹침 0. BOM FSAP_v2.5.9_*, 자료대기 D-115·D-129, 보고서 docs/reports/mechanism/mech_STEPSWAP_model.md

- v2.5.8 회귀 수정 REG-01-X1: CYCLE_G1 J_U5_LIFT 키 [320,0] → [318,0],[319,1],[320,1](먼 쪽 바퀴 트레드가 320단계 테이프 윗면에 0.4 mm 들어가던 것). 형상 변경 없음, 318~321 겹침 0. 보고서 docs/reports/mechanism/mech_regfix.md
- v2.5.8 전체 회귀 다시 돌림(문서만): pass, 새 겹침 0, 못 본 범위 약 1,900단계 디테일 기록. 설계검토서 docs/review/FSAP_v2.5.8_review.md, 결정로그 REG-02

- v2.5.7 STEPSWAP 수정 1: KDM10-06 실물 STEP(소켓 U8 받침판 P_M08_KDM_BRKT + CB3-10 ×4, 플러그 U7_CASSETTE, 짝 방향 +X = CST_X), U7 관 12줄 다시(_M08K_), 벨트 HTBO 곧은 가닥 X −2220~−390으로 자름(v2.5.6에서 X 1740까지 뻗어 보 앞 공압과 겹침). 사본 125개 겹침 수치 확인. 보고서 docs/reports/mechanism/mech_STEPSWAP_model1.md
- v2.5.6 STEPSWAP: STEP대기 16형번 실물 STEP 교체(풀리 N16·6200ZZ·벨트 HTBO-S5M150-792·MGPM25-40Z·CB6-20·SFB5-10 ×102·MSTH6-20·CB3-10·기둥 HFS8-80160-1090·KQ2L08·SS5Y3·SY3120·LR6·CB4-20), MGP 가운데 +20·대차판·승강판 구멍 다시, 공압 피팅·관 17줄 다시, 새 STEP대기 CB6-16 ×2·CB4-25 ×4, KDM10-06 남음. BOM FSAP_v2.5.6, 결정로그 SW-R1~R7·SW-D1~D5, 자료대기 D-115·117·120·126·128·129

- v2.5.5 DC2-03 결과 문서: BOM·설계검토서(FSAP_v2.5.5, v2.5.4 변경 포함), 결정로그 DC2-03 결과·디테일 DC203-D1~D6, 요구서 DC2-03 해결, 자료대기 D-82·D-108 쓰는 곳

- v2.5.3 M07-K1 결과 문서: BOM·설계검토서(FSAP_v2.5.3), 결정로그 결과·디테일 M07K-D1~D5, 요구서 M07 행 갱신, 자료대기 D-54·D-116 갱신

- v2.5.2 M08 결과 문서: BOM·설계검토서(FSAP_v2.5.2), 결정로그 M08 결과·디테일 M08-X1~X7, 요구서 M08 해결, 자료대기 D-132~D-141 새로·D-129 갱신

- v2.3.2 DC2-04 결과 문서: BOM·설계검토서(FSAP_v2.3.2), 결정로그 DC2-04 결과·디테일 DC2-04-T1~T6, 요구서 DC2-04 해결, 자료대기 D-127 갱신

- v2.3.0 결과 문서: BOM·설계검토서(FSAP_v2.3.0), 결정로그 M06 결과·디테일 M06-D1~D4, 요구서 M06 해결·DC2-02 메모, 자료대기 D-125 갱신·D-126(CB3-10 STEP 대기).

- v2.2.0 결과 문서: BOM·설계검토서(FSAP_v2.2.0), 결정로그 DC2-05·M05 결과·디테일·합치기 절, 요구서 DC2-05·M05 해결, 자료대기 D-97 갱신·D-120~D-122.

- 대화 결정(문서만, 모델 변경 없음): 결정로그 C-25 재봉 헤드는 사양으로 정하고 867·Juki LU-2810·썬스타를 견적 비교, C-26 3D프린터식(패턴 재봉기 모양) 기각·R375X 방식 유지. 자료대기 D-10에 견적 비교·치수 재확인 조건 추가.
- v1.0.16 결과 문서: BOM·설계검토서(FSAP_v1.0.16), 결정로그 RF-04~07, 다시 돌린 전체 회귀 본 범위 새 겹침 0(못 본 범위 G1 뒤·G2·자세 325~349·PRB 남음).

## v2.3.4 뒤 — 엔진 v3.9.2로 다시 켬 (2026-11-04)

- 엔진 v3.9.2 맞춤: 실행 인자 `tools/full-run-args.json` → `tools/run-args.json`(엔진 /mech-start 규약), 날짜·안내 갱신. 이전 실행은 M08 도중 멈춤
- 새 과제 M04R(결정로그 C-31): 볼 테이블을 R375X 사진대로 — 볼 수백 개(임시 피치 100), 사각 센터판 뺌, 매트 모형 기본 숨김

## v2.5.5 — 2026-11-05 (DC2-03 수정 1: 북 받이 판 −X 끝 받침)
- 검증 동작 문제(받이 판 외팔 378, 손 100 N SF 1.10) 고침: 새 세로 받침 `HFS8-4080-300_DC203`(X −38~2·Y −280~20·Z −330~−250)을 M07 아래 레일 `HFS8-4080-3450_M07:3` 윗면에 얹고 T형 L브래킷 `P_M07_LBRKT_PX_PZ`·`_NX_PZ` 각 1 + CB5-16·HNTT8-5 각 4로 고정, 열린 끝 2곳 끝캡 HFC8-4080-B
- 받이 판 `P_DC203_TRAY`에 구멍 Ø5.5 2개(X −18·Y −230/−170) + CB5-12·HNTT8-5 ×2 → 양끝 받침
- 생성기 `tools/gen_v2_dc203_fix2.py`, 보고서 `docs/reports/mechanism/mech_DC2-03_model1.md`. 앞 단계(검증·해석) 문서 함께 넣음

## v2.5.4 — 2026-11-05 (DC2-03: 아랫유닛 북 교체 길 + 포켓 바닥 비우기)
- `STEP대기_867-392342_LOWER` 북 문 자리(X ±15·Y −60~−10·Z −41~−12, 임시 D-10), 북 받이 판 `P_DC203_TRAY`(SUS304 t1.5, X −38~378·Y −276~−40) + CB5-12·HNTT8-5 ×2
- M07 바닥틀 포켓 구간 비움: 앞 레일 → HFS8-4080-2680 + 165(끝캡 2), 세로 :7·:8 → HFS8-4080-1740 ×2, 새 가로대 HFS8-4080-730, S형 L브래킷 7 + CB5-16·HNTT8-5 각 14, 옛 브래킷 3·볼트 6·너트 6 지움
- 생성기 `tools/gen_v2_dc203_fix1.py`, 보고서 `docs/reports/mechanism/mech_DC2-03_model.md`

## v2.4.0 — 2026-11-05 (M04R: U2 볼 테이블 사진대로, C-31)
- 볼 트랜스퍼 `STEP대기_BALL_D25_M04` 2,596 → 827(피치 100 반 칸 격자, D-96 임시), 사각 센터판 `P_M04_INSERT` 뺌, 매트·테이프·이음매 모형 9바디 기본 숨김
- 패널 6장 다시(볼 구멍 Ø36 피치 100). E2 X −410~975로 넓혀 센터판 자리를 덮음(원판 구멍 r130, 아랫유닛 구멍), W2 끝 X −410·띠 보스 구멍 Ø36 ×8, E1·E3 홈 메움
- 새 받침: 가로대 `HFS8-4080-560_M04` ×3(CM1·CM_A·CM_B) + `HBLFSN8_M04R_XP/XN` ×6 + `CB8-16_M04R_*` ×12(실물 STEP) + T너트, 받침판 `P_M04R_DB_SHIM_A/B`, DISK_BASE 체결 `CB5-20_M04R` ×4(머리 위)
- 지움: `STEP대기_CB8-15_M04` ×8, PZ 너트 8, 판 끝 접시 12, `CB5-16_M02_15~18`, 레일 ±100 서쪽 끝 캡 2, 잔재 바디 `STEP대기_BALL_D25H_M04` 1. 접시 M5 6개는 `STEP대기_FHS-M5-10_M04R`
- 과제 범위 겹침 0(REST·J_U4_PRESS −1.867·0·J_U5_X 1380). 보고서 `docs/reports/mechanism/mech_M04R_model.md`

## v2.3.4 — 2026-11-04 (M07 수정 1회차: 보를 기둥 위에 얹음, T너트 볼트 물림)
- 보 `P_M07_BEAM`을 X −2380~1230(3,610)으로 늘여 끝 80이 기둥 윗면 Z 250에 얹힌다(양의 받침). 끝 속은 1 mm 들인 끝판 t8 ×2(용접, 보 바디에 합침). 270.46 kg
- 기둥 `STEP대기_HFS8-80160-1090_M07_NX/PX`·`HFS8-4080-1090_M07_NX/PX`(옛 1482): Z −840~250. 기둥 위 캡 4개(`STEP대기_HFC8-80160-B_M07_NX/PX`, `HFC8-4080-B_M07_T` ×2)는 보가 막아 지움
- 뒤 이음판 `P_M07_SPLICE_NX/PX`를 L꼴 SS400 t6(Z 150~640)으로 다시 그림: 보 쪽 구멍 그대로, 4080 쪽 구멍 Z 300·600 → 175·220
- 볼트: 받침 세로 다리 CB5-12 ×12 → **CB5-20**(물림 8.5), 이음판 4080 쪽 CB5-12 ×8 → **CB5-16**(물림 7.5). 그 T너트 8개 Z 175·220으로 옮김
- 받침틀 HBLFSN8 체결은 PM 판정 M07-E01대로 그대로(구동 후보 M07-K1). 생성기 `tools/gen_v2_m07_fix1.py`. 손계산 `fea/cases/mech_M07_fix1_handcalc.py`. 보고서 `docs/reports/mechanism/mech_M07_model1.md`

## v2.3.3 — 2026-11-04 (M07 U1 프레임 + 보)
- 보 `U1_BEAM` → `P_M07_BEAM`: STKR400 각관 400×200×t8(X −2300~1150 · Y 120~320 · Z 250~650), 바깥 R12·안 R4, 기존 탭 그대로, 새 M5 탭 16·공구 구멍 Ø10 ×4
- 기둥: `STEP대기_HFS8-80160-1482_M07_NX/PX` + 실물 `HFS8-4080-1482_M07_NX/PX`, 위 캡 4, 풋 6. 보–기둥 받침 L `P_M07_SEAT_NX/PX`(SS400 t9 판금)·뒤 이음판 `P_M07_SPLICE_NX/PX`(SS400 t6)
- 받침틀: HFS8-4080 3450 ×3·2960 ×9·510 ×6·430 ×3, 캡 6, 풋 9, HBLFSN8 55, CB5-12 ×130 + HNTT8-5 ×130, CB5-20 ×8, CB5-16 ×8
- 지움: 차지 상자 `U1_COL_NX`·`U1_COL_PX`·`U1_BASE`. 새 조인트 0. machine.json U1_FRAME 부품. 자료대기 D-128. 생성기 `tools/gen_v2_m07.py`. 보고서 `docs/reports/mechanism/mech_M07_model.md`

## v2.3.2 — 2026-11-04 (DC2-04 수정 1회차: U7 걸이 장공 미는 볼트)
- `P_M05_HOLDER` 날개 A 장공의 Z 미끄럼(손 오조작 짝힘 SF 1.18) 고침: 받침 블록 `P_DC204_PUSH_BLK`(SUS304 절삭, UPPER −Y 면 CB5-12 ×2 + 새 M5 탭 2) + 미는 볼트 M4×25 ×2(X 14·42, U7_FIXED)·잠금 너트 M4 ×2
- 장공 볼트 `CB5-12_M05_11·12` 밑 평 와셔 M5 SUS t1, 볼트 −Y 1
- 새 구매품 임시 형상 STEP대기 멈춤나사·너트·와셔(자료대기 D-127). machine.json 유닛 부품·J_U7_HGT 메모. 생성기 `tools/gen_v2_dc204_fix1.py`. 보고서 `docs/reports/mechanism/mech_DC2-04_model1.md`

## v2.3.1 — 2026-11-04 (DC2-04 매트 두께 높이 사슬)
- D-04 임시 두께 범위 6~16을 h = 두께 − 10 하나로: `P_M06_BASE` 붙임면·`P_M05_HOLDER` 날개 A 구멍 Ø5.5 ×2 → 세로 장공(높이 −4~+6)
- 새 손 조정 조인트 `J_U6_HGT`(U3_HEAD ↔ U6_SENSOR)·`J_U7_HGT`(U3_HEAD ↔ U7_FIXED) slide +Z −4~6, 값 0. 지운 리지드 U1_FRAME↔U6_SENSOR·U3_HEAD↔U7_FIXED. 장공 볼트 CB5-12 ×4는 U3_HEAD로
- `J_U3_PRESSER` 하한 −4, 바늘 `U3_NEEDLE_PIN` +6(위 끝 Z 19)·`J_U3_NEEDLE` −36~0
- machine.json: 새 조인트·THICK_6·THICK_16 상태·U4 높이 식 키 표·D-04 임시값·바퀴↔테이프 기준선 정리(M00-X6). 생성기 `tools/gen_v2_dc204.py`. 보고서 `docs/reports/mechanism/mech_DC2-04_model.md`

## v2.3.0 — 2026-11-04 (M06 U6 센서 + 슈, U7 롤 걸이)
- 새 컴포넌트 U6_SHOE(J_U6_SHIFT slide +X −60~0, 대기 −60 비킴)·U7_ROLL_MOUNT(U1_FRAME 리지드). 지움: 차지 상자 U6_SHOE_SENSOR·U7_ROLL·U7_PATH_H
- U6 고정: P_M06_BASE(SUS304 t3 판금, 날개·붙임면·실린더 탭), CJ2B16-60SZ 실물 STEP(몸·장착 너트), KQ2L06-M5A, CB5-12 ×2(UPPER −Y 면 새 M5 탭)
- U6 움직임: P_M06_CARR(PET-CF), P_M06_SHOE(SUS304 t2 판금, 바닥 Z 12.5·입술 20°·장공), E32-D36P1_2M 머리, CJ2B16 로드 묶음, MBIS5-6.5-8 ×3, CB5-12 ×2, STEP대기 CB3-10 ×2·M3 인서트 ×2
- U7: 롤 기둥 A5052 t10·축 S45C·허브 PET-CF + 6004ZZ ×2·와셔, 안내 롤러 G1·꼭대기 롤러(판금 L·핀·롤러), 차지 U7_TAPE_ROLL·U7_TAPEWAY_H/V, CB5-12 ×5·CB5-16 ×3·CB5-20 ×4(UPPER 윗면 탭 4·HANGER 선반 구멍 2·보 앞면 탭 2)
- 연구 8개 모두 J_U6_SHIFT 키, machine.json(M05 조인트·연구도 들임). 생성기 `tools/gen_v2_m06.py`. 보고서 `docs/reports/mechanism/mech_M06_model.md`

## v2.2.0 — 2026-11-04 (동시 과제 합치기: DC2-05 먼 쪽 바퀴 받침 + M05 U7 테이프 툴 카세트)
- DC2-05: 먼 쪽 바퀴 줄 고하중 볼 `STEP대기_BALL_D25H_M04` 28을 지우고 A5052 받침 띠 P_DC205_STRIP + SUS304 누름판 P_DC205_DISC_1~8 + CB5-12_DC205 ×8(조임 0.6 N·m·중강도 나사 고정제)
- M05: U7 테이프 툴 카세트(U7_FIXED·U7_CST_STAGE·U7_CASSETTE·U7_CUT·U7_TUCK·U7_FEED·U7_LATCH) — 바인더·안내·절단 CJ2B10-15Z·접기 CJ2B10-15Z·리드 끝 보내기 CDJ2B16-150AZ-B·위치 핀·걸쇠, 조인트 6·연구 SEAM_U7·MAINT_U7. 수정 2회차 CB5-12_M05_5 → CB5-16_M05_10(조임 2.5 N·m)
- 합치기: 두 기록을 v2.1.5에 차례로 다시 실행, 바뀐 바디가 과제 후보와 모두 일치, 발자국 경계 간섭 0. 보고서 `docs/reports/mechanism/mech_merge_DC2-05-M05.md`

## v2.1.5 — 2026-11-04 (M04 수정 2회차: T너트 자리·센터판 볼트 길이)
- HNTT8-8 ×220·HNTT8-5 ×96 전부 홈 겉면 쪽으로 3.0 옮김: 실물 STEP의 목(높이 3, 폭 9.8)이 홈 입구에 들고 어깨가 윗턱 밑면에 닿는 조인 자리. 바닥 살 2 mm 묻힘 없앰(검도 V2)
- 침목 홈 너트 PZ:1~72·NZ:1~36은 목 긴 쪽이 홈 폭 방향이라 턱을 240 mm³ 파고들었음 → 너트 축 둘레 90° 돌림
- 센터판 볼트 CB8-20 ×8 → `STEP대기_CB8-15_M04` ×8(끝 Z −24, 홈 바닥 살 Z −24.5와 0.5, 물림 9)(검도 V1). CB8-20 바디 잔재까지 지움
- 검사: 너트 316 ↔ 형재 겹침 0(boolean 다 됨), 탐침 100개 겹침 0, 동작 6자세 새 겹침 0. 보고서 `docs/reports/mechanism/mech_M04_model2.md`
- 문서(M04 결과): BOM `docs/bom/FSAP_v2.1.5_{made,purchased}.csv`(v2.1.2 + 가공품 7·구매품 19행), 설계검토서 `docs/review/FSAP_v2.1.5_review.md`(v2.1.3~v2.1.5 묶음), 결정로그 "구동 M04 결과", 요구서 5절 M04 해결, 자료대기 D-116~D-119. 해석 손계산 `fea/cases/mech_M04_fea2_handcalc.py`.

## v2.1.4 — 2026-11-04 (M04 수정 1회차: 볼 트랜스퍼·센터판 체결)
- 볼 트랜스퍼 2,624개를 occurrence로 넣음: 수지 `STEP대기_BALL_D25_M04` 2,596(Nylon) + 먼 쪽 바퀴 줄 Y 0 고하중 `STEP대기_BALL_D25H_M04` 28(Steel, 필요 정격 ≥ 550 N, 동작 M04-F1)
- 센터판 P_M04_INSERT Y ±315로 다시 만듦(윗면 턱 Z −12.05), CB8-20 ×8(`STEP대기_CB8-20_M04`) + HNTT8-8 ×8 레일 Y ±300 윗면 홈. E1·E3 홈, E2 끝 0.05 물림
- 검사: 과제 범위 겹침 0(탭 물림 12 제외), 매트 밑 볼 L 최소 680·G 최소 382. 보고서 `docs/reports/mechanism/mech_M04_model1.md`

## v2.1.3 — 2026-11-04 (M04 U2 볼 테이블)

- U2_PLATE·U2_SUB를 지우고 센터판 P_M04_INSERT(A5052 t40, 윗면 Z 0), SUS304 t4 타공 패널 6장(압입 구멍 Ø36 2,624·M5 자리 108), HFS8-4080 틀 30본(실물 STEP 길이 맞춤)·마감캡 44·HBLFSN8 88·HNTT8-8 212·HNTT8-5 96, STEP대기 CB8-16 176·접시 M5×10 108·레벨러 36.
- 볼 트랜스퍼 바디는 넣지 못함(CAD 결합이 끝나지 않음, 예외 요청). 이음 줄 접시 M5·센터판 CB8-20은 T홈 밖이라 넣지 않음(예외 요청).
- 과제 범위 6자세 새 겹침 0. 생성기 tools/gen_v2_m04.py, 보고서 docs/reports/mechanism/mech_M04_model.md.

## v2.1.2 — 2026-11-04 (M03 U5 먼 쪽 바퀴 대차)

- `3D_Modeling/FSAP_v2.1.2.sc`(210바디): U5 차지 상자 6개를 지우고 SV2RL28-1800 레일(보 앞면 Y 120, Z 300)·블록 2(U5_CAR), X 구동(P_M03_DRV_BRKT, 서보·감속기 임시, S5M 60T 풀리 2, 6200ZZ 임시, 벨트 임시 띠, 아이들러 브래킷·축), 대차판(A5052 t12)·벨트 클램프(PET-CF)·MGPM25-40Z 임시·체인 팔, 승강부(LIFT_TOP·옆판·U4 바퀴 묶음 X −1700 복사·E32), igus 2400.05.075.0(약 22링크로 자름)·끝 브래킷 임시, 볼트 46을 넣었다. 유닛 컴포넌트 변화 없음.
- 조인트: J_U5_LIFT 0~30 → −10~30. 동작 연구 CYCLE_L·G1·G2 J_U5_LIFT 테이프 위 1.0 구간(모서리마다). 과제 범위 간섭 0(X 5점 × LIFT 2점, 4연구 U5 ↔ 매트·테이프 clear).
- `tools/machine.json`·`tools/config.json` doc → v2.1.2, 생성기 `tools/gen_v2_m03.py`. 보고서 `docs/reports/mechanism/mech_M03_{measure,design,donecheck,model}.md`.
- v2.1.2 문서: BOM(가공품 +14·구매품 +16행)·설계검토서 v2.1.2, 결정로그 M03 결과·디테일 M03-V1~V7, 요구서 M03 해결, 자료대기 D-114·D-115·D-95 쓰는 곳. 보고서 mech_M03_verify·fea, 해석 손계산 `fea/cases/mech_M03_handcalc.py`.

## v2.1.1 — 2026-11-04 (DC2-06 바늘 옆 바퀴 ↔ 머리판 탈착 길)

- `3D_Modeling/FSAP_v2.1.1.sc`(105바디, 형상·부품·볼트·조인트 변경 없음): 동작 연구 `MAINT_HEAD`(step 0 = REST, step 1 = J_U4_PRESS −1.867 실린더 전진 끝)를 더했다. step 1에서 U4 가동 17바디 대 전체 겹침 0, 머리판 통로(X −140~−80 · Y ±90 · Z 125~560) 겹침 0(트레드 틈 1.14), 바퀴 밑 Z 3.11, d₁ 100 유지.
- `tools/machine.json` 상태 "정비: 머리판 탈착(매트 없음, U4 내림 끝·공급 차단)"과 연구 MAINT_HEAD를 더했고, `tools/config.json`·`tools/machine.json` doc → v2.1.1로 바꿨다. 생성기 `tools/gen_v2_dc206.py`. 보고서 `docs/reports/mechanism/mech_DC2-06_design.md`·`_measure.md`·`_model.md`.

## v2.1.0 — 2026-11-04 (M02 U4 바늘 옆 바퀴)

- 결과 문서: BOM·설계검토서(FSAP_v2.1.0), 결정로그 "구동 M02 결과", 요구서 M02 해결, 자료대기 D-112·D-113, 검도·해석 보고서·손계산.

- `3D_Modeling/FSAP_v2.1.0.sc`(105바디): U4 차지 상자 6개(U4_MOUNT·HOLDER·DRIVE·WHEEL_TIRE·DISK·DISK_BRG)를 지우고 P_M02_BASE(SUS304 t8 L, 보 밑 ±5° 원호 장공)·CYLBRKT(t4 용접)·ARM_SIDE_N/P(t6)·FRONT(t12)·ARM_TIE·WHEEL(A6061)+WHEEL_TREAD(우레탄)·SNS_BRKT·DISK(Ø250)·DISK_SHAFT·DISK_HSG·DISK_BASE, 임시 형상 STEP대기_MHMF022L1U2M·STEP대기_VRXF-PB-60-10, 실물 STEP CDM2C20-25Z·I-020B·6004ZZ ×2·E32-D36P1_2M·CB5-16 ×21·CB5-20 ×4·CB5-12 ×2. U1_BEAM·U2_PLATE 밑면 M5 탭 4씩. 새 컴포넌트 U4_DISK·U4_CYL·U4_ROD.
- 조인트: J_U4_PRESS 슬라이더 → 회전(−1.867~8.626°, 피벗 (−300, 70)), 실린더 닫힌 고리 J_U4_CYL_PIN·J_U4_CYL_ROD·J_U4_ROD_PIN, J_U4_DISK. 동작 연구 5개 J_U4_PRESS 키 접촉 추종(0·0.306·0.611·8.627). 매트 3장 4연구 전 단계 U4 충돌 0.
- `tools/machine.json`·`tools/config.json` doc → v2.1.0, 생성기 `tools/gen_v2_m02.py`. 보고서 `docs/reports/mechanism/mech_M02_model.md`, 결정로그 M02-M1~M4, 자료대기 D-111 고침.

## v2.0.2 — 2026-11-04 (M01 U3 헤드 개조 + 좁은 홈 묶음)

- `3D_Modeling/FSAP_v2.0.2.sc`(55바디): U3_UPPER·U3_LOWER_POD → `STEP대기_867-392342_UPPER`(윗면 M5 탭 6)·`_LOWER`(이름만), `STEP대기_867-392342_NOSE` 새로, U3_PRESSER_BOX → `P_M01_FOOT`(S45C, 발바닥 t2 + 코 + 노루발대 Ø6), U3_HANGER → `P_M01_HANGER`(SUS304 t8 L 판금, 헤드 윗면 위 선반 + 보 앞면 세운 판, 장공 10), CB5-16 ×10(실물 STEP, U3_HEAD 리지드), U1_BEAM 앞면 M5 탭 4, U7_BINDER·U7_PATH_V(바닥 Z 22)·U6_SHOE_SENSOR 모양 고침.
- 조인트·행정 그대로(J_U3_PRESSER 0~20, J_U3_NEEDLE −30~0). 과제 범위 간섭 0(홈 매트 CYCLE_G1 17자세 + G2 574, 노루발×바늘 9자세). `tools/machine.json`·`tools/config.json` doc → v2.0.2, 생성기 `tools/gen_v2_m01.py`. 보고서 `docs/reports/mechanism/mech_M01_model.md`.

## v2.0.1 — 2026-11-03 (M00 전체 골격)

- `3D_Modeling/FSAP_v2.0.1.sc`: 유닛 차지 공간 상자 32개(U1 보·기둥·바닥틀, U2 볼 테이블, U3 윗헤드·아랫유닛·노루발·바늘, U4 바늘 옆 바퀴 자리·원판 Ø250, U5 레일·체인·대차·승강, U6 슈·센서, U7 바인더·테이프 길·롤, U8 레귤레이터·라이트 커튼·HMI·경광등)를 기존 컴포넌트에 넣음. `J_U5_X` 한계 0~1380(d₂ 420~1800).
- 기계 크기 3750 × 3165 × 1900, 보 밑면 Z 250, 볼 테이블 3150 × 3115 윗면 Z 0, 작업면 높이 900, 작업자 포켓 +X·−Y.
- 과제 범위 간섭 0. `tools/machine.json` doc·J_U5_X·units·temp_values·baseline 고침, 생성기 `tools/gen_v2_m00.py`, 설계검토서 `docs/review/FSAP_v2.0.1_review.md`(제어 순서 M00-Q1~Q3), 결정로그 M00-D01~D10·M00-M01~M03, 자료대기 D-105 고침·D-107.
- 보고서 `docs/reports/mechanism/mech_M00_{measure,design,model,verify}.md`. 문서: BOM `docs/bom/FSAP_v2.0.1_*.csv`(머리줄만, 부품 0), 설계검토서 변경 표·디테일 M00-X6, 결정로그 "구동 M00 결과", 요구서 M00 해결.

## v2.0.0 — 2026-11-03 (준비부: 빈 설계 골격)

- 새 설계 `3D_Modeling/FSAP_v2.0.0.sc`(new_design): 고정부 U1_FRAME + 유닛 빈 컴포넌트 7개, 조인트 기계 7개(노루발·바늘·바늘 옆 바퀴 누름·회전·먼 쪽 대차 X·승강·바퀴 회전) + 매트 모형 평면 운동 9개, 바퀴 2(Ø120×25 임시), 매트 3장(1500×1500·300×200·U홈 25 매트) + 가공 뒤 테이프 띠·이음매.
- 동작 연구 REST·CYCLE_L 716·CYCLE_S 450·CYCLE_G1 514·CYCLE_G2 630, 기계 정의 `tools/machine.json`(상태 22), 생성기 `tools/gen_v2_prep.py`·`gen_v2_machine.py`, 서명·원장 새로.
- 자료대기 D-104~D-106(바퀴 들림·d2 범위·로딩 자세). 보고서 `docs/reports/mechanism/mech_prep.md`.

## v2.0 준비 — 2026-11-03 (개념 다시 세움)

- 요구서 0-8 v2 **확립**(사용자 동의 "응, 시작", 2026-11-03): R375X 제품 사진 그대로 — 볼 트랜스퍼 테이블, 헤드 3중 이송이 끌고 서보 바퀴 2개(바늘 옆 늘·먼 쪽 X 대차 필요할 때)가 약하게 눌러 잡기·방향, 두 바퀴는 바늘을 지나는 X선 위(속도 v + ω·d), 가장자리를 바인더 쪽으로 붙이기, 매단 분리형 헤드. 결정로그 C-27~C-30(C-03 고침, C-21 대체), 자료대기 D-92~D-103, 요구서 4-1·7절, 초안 `docs/concept/v2-drive-concept-draft.md`.
- v1.0.x(v1.0.0~v1.0.18) 모델·BOM·설계검토서·보고서·생성기·해석·machine.json을 `archive_v1/`로 동결, 측정 원본은 `tools/out/_v1/`. 과제 목록을 M00~M08로 새로(v1.0 목록은 `archive_v1/docs/task-list-v1.md`).
- 실행 규칙 20(v2.0 새 시작), `tools/config.json` doc → FSAP_v2.0.0.sc, 실행 인자 shellNote v2.0.

## v1.0 준비 — 2026-11-03 (개념 재수립)

- 요구서 0-8 전체 구동 개념 **확립**(사용자 동의 2026-11-03): 헤드 자체 이송(Dürkopp 867-392342 개조, 기둥 없음), 가운데 진공 원판 + 에어 테이블, X·Y 따라가기, 벤치마크 거의 그대로(결정로그 C-12~C-24, `docs/concept/v1-drive-concept-discussion.md`).
- v0.x(v0.0.0~v0.10.1) 모델·BOM·설계검토서·보고서·생성기·해석을 `archive_v0/`로 동결. 과제 목록을 N00~N08로 새로.
- 엔진 v3.7.0 맞춤(전체 회귀 상한·벤치마크 칸), 실행 규칙 17(v1.0 새 시작), 실행 인자 `tools/full-run-args.json`.

## Added

- 설계 v1.0.18 `3D_Modeling/FSAP_v1.0.18.sc`(구동 DC-08 송풍 호스 꺾임 자리, 결정로그 DC-08-S01~S04·DC-08-M01~M03): `P_N04_INLET`을 축 (−1185, 1143)의 한 덩어리 회전체(끼움 턱 Ø46×1 + 플랜지 Ø70×5 + 니플 Ø38×40 C1, 관통 Ø34, PA12 출력, 24,444 mm³)로 다시 그림, `P_N04_PANEL` 밑 표피 Ø46 구멍 피처 중심만 (−1023, 1040) → (−1185, 1143)(부피 변화 0). 호스·밴드는 형번 미정이라 바디 없음(N04-S07, D-89). 과제 범위 J_U4_X −200~1217.5 25 mm 58자세 INLET·PANEL 겹침 0. 보고서 `docs/reports/mechanism/mech_DC-08_model.md`
- 설계 v1.0.17 `3D_Modeling/FSAP_v1.0.17.sc`(구동 DC-07 X 편구동 요 반력, 결정로그 DC-07-S01~S06·DC-07-M01~M04): X 블록 4개 중심 X −935·−865 → −1000·−810(간격 190), CB5-20_N03XB ×8 → X −993.5·−816.5(카운터보어 피처 Cylinder72~87 자리 고침, 메우지 않음). `U4_X_BEAM` 밑면 레일 A 블록 자리마다 한 몸 턱 2(안쪽 기준 Y −939~−931, 바깥 누름 Y −992~−982, Z −365~−352)·바깥 턱 M5 탭 ×6. 새 구매품 `STEP대기_MSSF5-10_1~6`(멈춤나사 M5×10 평끝, Steel, U4_X). 블록·볼트 리지드 묶음 12개를 같은 이름으로 다시 묶음. 생성기 `tools/gen_v1_dc07.py`, 자료대기 D-91, 보고서 `docs/reports/mechanism/mech_DC-07_model.md`
- 설계 v1.0.16 `3D_Modeling/FSAP_v1.0.16.sc`(라운드 끝 회귀 수정, 결정로그 RF-01~RF-03): 안쪽 끝 막대 `P_N04_CHAIN_NP_BAR`·`_PN_BAR` +X 끝 −829 → −830.5(PN 몸 −832, 러그 X −832.5~−830.5), 판 벽 홈 Box252·253(루트 피처라 자세마다 자리가 바뀌던 것) 끔, 판 −830 면에 멈춤 이 2(NP Y 67~77 · Z −2.5~−0.5, PN Y −77~−66.5 · Z −5~−3.5), PIN_3/4 X −834~−833. 새 피처는 바디의 컴포넌트 안. 회귀 문제 자세 14개 겹침 0, J_U4_X 800 막대 ↔ LOWER 0.5, sweep stopped_at null. 생성 명령 `tools/out/mech_regfix/stage_regfix.json`, 보고서 `docs/reports/mechanism/mech_regfix.md`
- 구동 N04 결과(v1.0.15, 문서): BOM `docs/bom/FSAP_v1.0.15_made.csv`(U5_POST 행 지움, P_N04_* 21행)·`_purchased.csv`(VB-004-E2·CDJ2B16-110 ×2·CDJ2B16-150·HFS8-4080-248 ×4 STEP대기), 설계검토서 `docs/review/FSAP_v1.0.15_review.md`, 결정로그 N04-R01~R04·디테일 N04-D9·D11~D16, 요구서 5절 N04·DC-01 해결, 자료대기 D-90, 해석 손계산 `fea/cases/mech_N04_fea2_*.py`
- 설계 v1.0.15 `3D_Modeling/FSAP_v1.0.15.sc`(구동 N04 수정 2회차, 결정로그 N04-F07~F11, PM 판정 N04-E05~E07): 바깥 사슬 보관 `P_N04_STORE_P/_N` U턴 2층(위층 턱 Y ±1430~1528.5 없앰, 끝벽, +X 옆벽 꼬리 러그 홈) — 보관 넘침 0. 꼬리 멈춤 `STEP대기_CDJ2B16-110_P/_N`을 보관 밖 옆(X −828~−808, Y ±779~919)으로 옮기고 `J_N04_STOP_P/N`을 ±Y로 다시 만듦, 받침 `P_N04_CYLBKT_P/_N` t4 L 24 폭, 패드 16.5×4×16. 안쪽 끝 막대 `P_N04_CHAIN_NP_BAR`·`_PN_BAR`(A6063)를 U5_BAR_NP/PN + 슬라이더 `J_N04_BAR_NP/PN`으로, 판 +X 벽 홈 2(높이 다름)에 물려 멈춤. PIN_3/4 X 2폭. 앞끝 P/N L_f 76.5, 식 Yc ±81.5·열림 ±55, 연구 7개 키 다시 씀. 29자세·꺾임 128단계 겹침 0, 프로브 154자세 보관 0, cov_hybrid unsup 0. 생성기 `tools/gen_v1_n04_fix2.py`, 보고서 `docs/reports/mechanism/mech_N04_model2.md`
- 설계 v1.0.14 `3D_Modeling/FSAP_v1.0.14.sc`(구동 N04 수정 1회차, 결정로그 N04-E01~E04·N04-F01~F06. v1.0.13은 같은 회차 중간 저장 — 저장 후 점검에서 A 앞끝 길이 47 → 42(하드 리밋 1217.5)와 보관 A ↔ Y 케이블 베어 1,100 mm³를 고쳐 v1.0.14): 사슬 앞끝 바디 `P_N04_CHAIN_P_HEAD`·`_N_HEAD`(132×92.5×5)·`_A_HEAD`(42×108×5, A6063)를 새 컴포넌트 U5_CHAIN_P/N/A + 슬라이더 `J_N04_CH_P/N/A`로, 꼬리 멈춤 로드·패드를 U5_STOP_P/N/A + 슬라이더 `J_N04_STOP_P/N/A`(0~110·0~110·0~150)로 뗌(실린더 몸 로드 구멍 Ø6). 연구 7개 키를 `tools/gen_N04_chain_keys.py` 식으로 다시 씀(모션 링크 없음). 검도 P1 보관 안내 P/N 바깥 X −970~−830(안쪽 137), P2 판 A 꺾임 통로 X −1292.5~−1272.5·Y ±55·Z −41~−5 + 보관 A X −2000~−1272.5(Z −172 아래 X −1278~−1272.5 따냄, Y 케이블 베어와 1). 해석: 실린더 받침 P/N SUS304 t4(세운 판 Y 1533~1537, 날개 8), A 통 블록 t8×40×148 + 받침판 60×40×4, 안장 다리 폭 100(X −950~−850). 멈춤 블록 4를 X 4폭(−970~−966·−834~−830)으로 좁혀 바깥 사슬 앞끝 길과 비킴. 안쪽 사슬 드럼 쪽 끝 구간 `P_N04_CHAIN_NP_TAIL`·`_PN_TAIL`(U4_Y). 고정 프로브 `tools/gen_N04_chain_probe.py` → `tools/out/probes/N04_chain_probe.json`(machine.json probe_sets). 생성기 `tools/gen_v1_n04_fix1.py`
- 설계 v1.0.12 `3D_Modeling/FSAP_v1.0.12.sc`(구동 N04 U5 에어 테이블, N04-S = C3 고친 안 + C2): U5_TABLE·U5_POST_1~4 지움 → U5_AIRTABLE `P_N04_PANEL`(Al 허니컴 h38 + A5052 1+1, 재질 A5052_HC 0.19, 홈 3·턱·솔 주머니 4·목 주머니·밑 표피 Ø46, 48.3 kg)·`P_N04_NECK`(A6061)·`STEP대기_HFS8-4080-248` ×4·사슬 보관 `P_N04_STORE_P/_N/_A`(SUS304 t1.5)·꼬리 멈춤 `STEP대기_CDJ2B16-110_P/_N`·`STEP대기_CDJ2B16-150_A`·받침 `P_N04_CYLBKT_P/_N/_A`(SUS304 t2)·멈춤 블록 `P_N04_PIN` ×4·송풍 입구 `P_N04_INLET`(PA12), U4_Y `P_N04_SADDLE`(SUS304 t2, Ø126)·감개 드럼 2(A6063)·받침 2(SUS304 t1.5), U1_HEAD `P_N04_TAIL`(SUS304 t3 U자)·`P_N04_TAIL_BKT`, U2_BRIDGE `STEP대기_VB-004-E2`·`P_N04_BLOWER_BASE`. 새 조인트·볼트 0. 매트 받침 4개 연구 안 받친 단계 0(cov_hybrid), 20자세 clearance 겹침 0(제어 금지 1자세 제외, machine.json xy_forbidden 추가), J 800·Yc −100 안장 ↔ LOWER·꼬리판 4.0, J_U4_X·J_U4_Y 스윕 stopped_at null, 외팔 처짐 ±X 0.40/손 0.55 mm. 생성기 `tools/gen_v1_n04.py`, 결정로그 N04-M01~M05, 자료대기 D-89, 보고서 `docs/reports/mechanism/mech_N04_model.md`
- 설계 v1.0.11 `3D_Modeling/FSAP_v1.0.11.sc`(구동 DC-03 수정 2회차): `P_DC03_YMOV` 옆판 2장(X −1043~−1028, Y −340~−337·−283~−280)을 Z −258(다리 아래 끝)까지 내림 — 다리 전 높이 ㄷ 단면. 부피 69,720 → 72,240 mm³(553 → 573 g), bbox 그대로. 오조작 SF 0.69 → 3.77(검증 손계산 안 A2). 8자세 + REST clearance 3 겹침 0(맞닿음은 Y 베어 윗면·대차·볼트 머리뿐). 조인트·볼트·다른 부품 변경 0. 생성기 `tools/gen_dc03.py --fix2`, 결정로그 DC-03-M03, 보고서 `docs/reports/mechanism/mech_DC-03_model2.md`
- 설계 v1.0.10 `3D_Modeling/FSAP_v1.0.10.sc`(구동 DC-03 수정 1회차): `P_DC03_YMOV` 다리 ㄷ 보강 — 양 옆 −X 15 옆판(X −1043~−1028, Z −230~−173/−176, Y −340~−337·−283~−280) + 다리 +Y 릴리프 메움·보강 플랜지 모서리 용접. 부피 64,365 → 69,720 mm³(510 → 553 g). 오조작 SF 0.69 → 3.98(손계산). 8자세 + REST clearance 3 겹침 0(맞닿음은 Y 베어 윗면·대차·볼트 머리뿐). 조인트·볼트·다른 부품 변경 0. 생성기 `tools/gen_dc03.py --fix1`, 결정로그 DC-03-M01·M02, 보고서 `docs/reports/mechanism/mech_DC-03_model1.md`
- 설계 v1.0.9 `3D_Modeling/FSAP_v1.0.9.sc`(구동 DC-03 X·Y 케이블 베어 자리, DC-03-S = C3 고친 안): U4_FIX `P_DC03_XTROUGH`(SUS304 t2 판금 홈통 X −1260~490·Y 1086~1487·Z −380~−298, 바깥 벽 케이블 창 X −590~−510) + `STEP대기_E4.56.10.150.0`(X 베어 눕힌 고리 차지 띠) + CB5-12 ×6(→U2_BASE 탭), U4_X `P_DC03_XMOV`(SUS304 t3 U, 보 +Y 끝면, 송풍 호스 기둥 비움) + `P_DC03_YTRAY`(SUS304 t2, 걸이 탭 일체, 보 −X 면) + `STEP대기_2400.05.075.0`(Y 베어 세운 고리 차지 상자) + CB5-12 ×6, U4_Y `P_DC03_YMOV`(SUS304 t3, 대차 −X 면) + CB5-12 ×2. U2_BASE·U4_X_BEAM·U4_Y_CARR M5 탭 깊이 12 ×6·×6·×2. 새 조인트 0, 리지드 3묶음 추가, floating 0. 8자세 clearance 겹침 0(맞닿음만), REST 유닛 안 겹침 0. 문서 이름 FSAP_v1.0.9. 생성기 `tools/gen_dc03.py`, 자료대기 D-88, 보고서 `docs/reports/mechanism/mech_DC-03_model.md`
- 설계 v1.0.8 `3D_Modeling/FSAP_v1.0.8.sc`(구동 N03 U4 X·Y 따라가기 받침, N03-C1 고친 안): U4_RAIL_A·B 지움 → X·Y 레일 SV2RL28-1800 ×4(실물 STEP, 레일 U4_FIX·U4_X, 블록 U4_X·U4_Y), U4_X_BEAM A5052 리브 보(X −1050~−760·Z −352~−288, 밑 포켓 4·슬롯 X −911~−889), U5_POST_1~4 밑 −288, X 서보·Y 서보 `STEP대기_MHMF082L1U2M_N03X`·`STEP대기_MHMF042L1U2M_N03Y`, 풀리 `STEP대기_HTPA28S5M250-A-N19`·`STEP대기_HTPA25S5M150-A-N14` ×2씩, 오픈 벨트 `STEP대기_S5M250-OPEN`·`STEP대기_S5M150-OPEN`, 판금 SPCC t4 브래킷 4·X 물림, A5052 물림판·Y 물림, CB5-20 ×136·CB5-16 ×2·CB5-12 ×2(실물 STEP). J_U4_Y 한계 −400~1200 → −355~1155, machine.json xy_forbidden 추가. 5자세 clearance 겹침 0, J_U4_X·J_U4_Y 전 행정 스윕 접촉 0(최소 5.5·5.0), floating 0. 생성기 `tools/gen_v1_n03.py`, 자료대기 D-80 쓰는 곳, 보고서 `docs/reports/mechanism/mech_N03_model.md`
- 설계 v1.0.7 `3D_Modeling/FSAP_v1.0.7.sc`(구동 N02 수정 1회차, 진공 관 길): P_N02_FRAME +Y 벽 관 구멍 Ø10을 X −920·Z −210 → X −855·Z −170으로 옮김(ZH10DSA 배기 포트 앞 35 mm 비움, M-06), `STEP대기_KQ2H06-M5A` 지움 → `STEP대기_KQ2L06-M5A` 엘보, 관 `TU0604_N02`(Ø6 R15, PU, 씰 포트 → 벽 구멍 → ZH 진공 포트) 새로 그림(U4_Y). 10자세·J_U4_X 5점 clearance 10 겹침 0, U4_Y 안 겹침 0(관–구멍 2.0), 다시 실행 84/84 같음. 생성기 `tools/gen_v1_n02_fix1.py`, 결정로그 N02-M07·M08, 자료대기 D-85 고침, 보고서 `docs/reports/mechanism/mech_N02_model1.md`
- 설계 v1.0.6 `3D_Modeling/FSAP_v1.0.6.sc`(구동 N02 U3 진공 원판 + 회전 조향, N02-C3 고친 안): U3_PLATE·U3_COLUMN·U3_DRIVE 지움 → U3_ROT `P_N02_PLATE`(A5052 Ø120 t15, 동심·방사 홈, 밀봉 띠 r55~60)·`P_N02_SHAFT`(S45C, 플랜지 Ø100·목 Ø40·어깨 Ø56·베어링 Ø50·풀리 Ø30·씰 Ø25, 속 Ø8)·`P_N02_COLLAR`·`STEP대기_HTPA60S5M150-A-N30`·CB5-20 ×4, U4_Y `P_N02_FRAME`(SPCC t4 ㄷ 판금)·`P_N02_HOUSING`·`STEP대기_CRBH5013`·`P_N02_RETAINER`·`P_N02_SEAL`(O링 홈 2·고리 홈·M5 포트)·`STEP대기_JIS-P25` ×2·`STEP대기_KQ2H06-M5A`·ZH10DSA-06-06-08(실물 STEP)·`P_N02_MBKT`(SPCC t4 Z 판금, 장공)·`STEP대기_AZM66AC-PS25`·`STEP대기_HTPA20S5M150-A-N12`·`STEP대기_HTBN635S5M-150`·CB5-12 ×14·CB5-20 ×3, U4_Y_CARR M5 탭 ×9. J_U4_X 한계 1250 → 1217.5. 10자세 clearance 겹침 0, J_U4_X 스윕 −200~1217.5 접촉 0(최소 16.0), floating 0, 다시 실행 83/83 같음. 문서 이름 FSAP_v1.0.6. 생성기 `tools/gen_v1_n02.py`, `tools/machine.json`, 결정로그 N02-M01~M06, 자료대기 D-85, 보고서 `docs/reports/mechanism/mech_N02_model.md`
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
- v2.1.1 문서: BOM·설계검토서 v2.1.1, 결정로그 DC2-06 결과·디테일 D1·D2, 요구서 DC2-06 해결, 자료대기 D-10 쓰는 곳
- v2.3.4 문서: BOM·설계검토서 v2.3.4, 결정로그 '구동 M07 결과', 요구서 M07 해결, 자료대기 D-128 갱신

## v2.5.0 — 2026-11-05 (M08: U8 공압·안전 자리)
- 차지 상자 `U8_REG`·`U8_LC_L`·`U8_LC_R`·`U8_LAMP`·`U8_HMI` 지움 → 레귤레이터 `STEP대기_IR1000-01BG_M08_N/F/S`(보 앞면 X 700/800/900) + 이음 KQ2L08 ×6, 매니폴드 `STEP대기_SS5Y3-20-06_M08` + 밸브 SY3120 ×6 + `KQ2L06-M5A_M08` ×11(실물 STEP)
- 라이트 커튼 F3SG-4RA1520-14 ×2쌍(STEP대기) + 기둥 `HFS8-4080-2370_M08_FL`·`HFS8-4080-1900_M08_FR/_R`(실물 STEP) + 캡 6 + 이음판·판금 L 9, 경광등 LR6(STEP대기, 보 윗면), HMI 받침판·팔 `HFS8-4080-570_M08_HMI`·패널 받침·패널 자리
- 다관 커넥터 KDM10-06 고정 반쪽(걸이 위) + 플러그(U7_CASSETTE), 관 TU0805 ×6·TU0604 ×11(3D 스케치 + pipe, 굽힘 호)
- 새 컴포넌트 53개 → 가운데 자리(E-05). 새 조인트 0. 보고서 `docs/reports/mechanism/mech_M08_model.md`

## v2.5.1 — 2026-11-05 (M08 수정 1: 미완 6건)
- U4 실린더 CDM2C20 포트(Rc1/8 실측)에 `KQ2L06-01AS_M08_U4_1/2`(U4_CYL 아래), 관을 핀 축 이음점에서 고정 관 U4_A/B ↔ 실린더 쪽 관 `TU0604_M08_U4C_A/B`로 나눔
- U5: 고정 관 U5_A/B를 베어 고정 끝(X -1262)까지, MGPM25 −X 면에 `KQ2L06-01AS_M08_U5_1/2` + 대차 쪽 관 `TU0604_M08_U5C_1/2`(U5_CAR)
- 카세트 안 관 `TU0604_M08_U7C_1~6`(플러그 → FEED·CUT·TUCK 피팅, U7_CASSETTE)
- 라이트 커튼 기본 금구 `STEP대기_F3SG-BRKT_M08_1E/1R/2R/2E` + CB5-12·HNTT8-5, 옆 투광 L 날개 −Y 3
- 경광등 `STEP대기_CB4-12_M08` ×3, 다관 커넥터 CB5-12 ×2, 보 윗면 관 빗 `P_M08_TUBE_COMB_ML_1~4` + CB5-16 ×4
- 판금 10개 `sheet.convert`(규칙 SUS304_t4·t6 새로), HMI 판 T → L(날개 팔 −X 면, 볼트·너트 옮김)
- 수정 회차 → 끝 자리(E-05). 새 조인트 0. 보고서 `docs/reports/mechanism/mech_M08_model1.md`

## v2.5.2 — 2026-11-05 (M08 수정 2: 움직인 자세 측정)
- 형상 변경 없음(설명 메타만). v2.5.1을 다른 이름으로 저장(E-05)
- U4 누름 4점·U7 작동 4점·카세트 뺌 6점에서 새 관·이음·플러그 간섭 측정 — 새 겹침 0(맞닿음 0.0 두 곳, 기준선 쌍은 손계산). 보고서 `docs/reports/mechanism/mech_M08_model2.md`

## v2.5.3 — 2026-11-05 (M07-K1: 받침틀 브래킷 판금 L + M5, 렌치 길)
- 기성 브래킷 `HBLFSN8_M07_*` 55 · `HBLFSN8_M04_*` 88 · `HBLFSN8_M04R_*` 6(U-13 같은 기준) → 판금 L SUS304 t6(내R 6, `sheet.convert`) 149: `P_M07_LBRK*`(45×45, 구멍 30/30) · `P_M07_LBRKT*`(75×45, 60/30, Y 부재-가운데 X 부재 9) · `P_M07_LBRKC*`·`P_M04_LBRKC*`(45×45, 20/30, 기둥 8·레일-침목 72) · `P_M04_LBRK*`(가로대 끝 22)
- 체결 CB5-12 110 · CB8-16(STEP대기 176 + 실물 12) → `CB5-16_M07K/M04K_*` 298(실물 STEP), 너트 HNTT8-5 브래킷 몫 110 · HNTT8-8 188 → `HNTT8-5_M07K/M04K_*` 298(실물 STEP). 레벨러 너트 HNTT8-8_M04_NZ·받침/이음판 너트 20은 그대로
- 저장본 검사: 새 볼트 298 빼는 길 프로브(Ø8.5 × 30) 겹침 0, 새 바디 745 ↔ 이웃 겹침 0, floating 0. 레일 다리 위 홈(Z −32) 안은 볼 몸통이 프로브를 막아(62곳 216.6 mm³) 아래 홈(Z −72)으로 고침
- 생성기 `tools/gen_v2_m07k1.py`(`gen_v2_m07.py k1`), 보고서 `docs/reports/mechanism/mech_M07-K1_model.md`
