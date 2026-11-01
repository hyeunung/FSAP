# 구동 T15 모델링 — T05 SNJ 스패너 자리 (v0.8.0 → v0.8.1)

요약(10줄)
- 바뀐 부품: `P_T05_GUIDE`(PET-CF FDM, 천장 Z 76.5~80.5 + 너트 틈 Z 80.5~85.5 + 외팔 위판), `P_T05_PAD`(윗 긴 모서리 C2 ×2). 지운 부품 0, 새 부품·구매품·볼트 0, 조인트·행정 변경 0.
- 부피: GUIDE 97,979.7 → **103,027.8 mm³**(지시 기준과 같음), PAD 9,736.6 → **9,624.6 mm³**. bbox 둘 다 그대로.
- 스패너 판 21×4: 0°·±15°·±30°·±45° 겹침 **0**(위판 밑면 85.5 맞닿음만). 23×4 ±30° 0. 포트 상자 0.5.
- 패드 안내 틈: J −12.5 / 0 / −13.5에서 **0.3 / 0.3 / 0.0(받침면)**, 10자세 스캔 겹침 0.
- 앞벽 오조작B 손계산: 두 변 SF 2.95 → **3.80**(외팔 1.90, Kt 1.3 2.92) ≥ 2. 데크 운전 SF 3.95, 오조작 100 N(가정) 2.17.
- 정적 간섭(T05 영역 17쌍, budget 300 s): **0**, truncated false, unchecked = 기준선 8쌍 그대로.
- 통로: **MCP**(open v0.8.0 → inspect dirty false → batch → 대기 포즈 → save v0.8.1). 검사는 CLI로 저장본에 대고.
- 미완: joint.sweep은 접촉 예산 초과로 거부 → drive + clearance 10자세 스캔으로 대신(T03 선례). 디테일 d1~d4 기록만.

## 1. 통로·문서 확인

- 실제 연결: `running` 응답 정상, `document.inspect` 응답(dirty false, path null) → MCP로 그림. `open FSAP_v0.8.0.sc`(errors 0, features 1656).
- 저장: `save {path: 3D_Modeling/FSAP_v0.8.1.sc}`(14,241,570 B). `save {}` 덮어쓰기 안 씀. `tools/config.json` doc → `../3D_Modeling/FSAP_v0.8.1.sc`.
- 다시 열기: errors 0, features 1665, dirty false, GUIDE 부피·bbox 저장 전과 같음. 타임라인 warning 23 → 25(새 둘은 `Boolean retry: tool displacement 2.16e-4 mm` — 틈 자르기·다듬기 상자, 결과 정상).
- 동작 상태 초기화: 시작·끝 `motion.play {study:"대기", step:0}`, 저장 전 `joint.drive J_T05_PAD −12.5`.
- 문서 설명(document.metadata description): "T15 mechanism: T05 guide pocket ceiling Z76.5-80.5 + nut slot Z80.5-85.5 for thin spanner on SNJ, pad top C2 x2".

## 2. 그린 것(선정 지시서 [1]·[2] 순서 그대로, T15-S09)

| # | 명령 | 좌표 | 결과 |
|---|---|---|---|
| a | solid.box join F1 | X −150~−88, Y 561~584, Z 76.5~81.0 | Box148 |
| b | solid.box join F2 | X −115.5~−88, Y 561~584, Z 80.0~86.0 | Box149 |
| c | sketch T15_SLOT(origin (0,580,0), x=세계 X, y=세계 Z) 둥근 사각 [−160,80.5]–[−114,85.5] R1 → extrude symmetric 80 cut | Y 540~620 관통 | Extrude138 |
| d | solid.box cut | X −160~−147, Y 550~600, Z 76.0~86.5 | Box150 → 부피 103,029.48 |
| e | solid.fillet R3 | 모서리 (−130, 562.2, 76.5) | Fillet33 |
| f | solid.cylinder cut Ø6 h6 | 바닥 (−126.9, 572.5, 75.5), 축 Z | Cylinder614 → **103,027.80** |
| g | solid.chamfer C2 ×2 (`P_T05_PAD`, J −12.5) | (−120, 562.5, 63)·(−120, 582.5, 63) | Chamfer97·98 → **9,624.56** |

- metadata(T05 properties `P_T05_GUIDE`): "PET-CF / FDM H2C / C틀: 밑판 받침면 Z42(앞 윗모서리 R1) + 등판 t8 + 앞벽 t9.2(Y553~562.2) + 옆벽 t3 + 막대 r8 + 주머니 천장 Z76.5~80.5(t4, 로드 구멍 Ø6, 앞 뿌리 R3) + 너트 틈 Z80.5~85.5(X≤−114, −X·±Y 트임, 안 모서리 R1) + 위판 Z85.5~89.5(t4, Ø8.2, X−114 탑에서 외팔), MBIS5-6.5-8 x2 등판 관통 Ø6.4 (DP-3, T15)". 다른 T05 부품 문구는 그대로 다시 넣음.
- metadata(T05_PAD `P_T05_PAD`): "… 패드 28x20x20(Z43~63) 한 덩어리, 윗 긴 모서리 C2 x2(T15), NTJ-010C T홈 … (DP-3)".
- 재질 PET-CF(밀도 1.29) 그대로, 재질 불일치 0. 숨김 변경 0, 리지드 그룹 변경 0(HEAD 그대로, 새 바디 0).
- 손대지 않음: CJ2B10-15Z_T05_BODY·SNJ·ROD·NTJ ×2, J_T05_PAD(직선 Z −13.5~0, 대기 −12.5), DP-3 체결 GD_1·GD_2(CB5-16 + MBIS5-6.5-8) — 등판 관통 자리라 옮길 것 없음. machine.json/동작 연구 변경 없음(E-15).
- 생성기 `tools/gen_t15_mech.py`(→ `tools/out/mech_T15/gen_t15.json`).

## 3. 저장 전·후 자기 점검(E-22, 저장본 v0.8.1에 CLI `run --results`, 저장 안 함)

스크립트 `tools/out/mech_T15/model_chk2.json`(PM sel11 프로브와 같은 도구·좌표) → `model_chk2_out.json`, 요약 `chk2_summary.txt`. 프로브는 CLI 사본에만 만들었고 저장본에는 없다(4-f 충족).

| 항목 | 기준 | 결과 |
|---|---|---|
| (a) 스패너 21×4, 축 (−126.9, 572.5), 0°·±15°·±30°·±45°, Z 81.5~85.5, clearance 2 | 겹침 0 | **0**(위판 밑면 85.5 맞닿음 0.0만) |
| 23×4 ±30°, 손잡이 ±Y | 겹침 0 | 0 |
| 21×5 ±15°(참고, 머리 두께 한계 확인용) | — | +15°: Z 80.5 같은 평면 맞닿음 0.075 mm³ → 머리 두께 ≤ 4.5(D-57) |
| (b) 포트 상자 X −168.25~−133.25·Y 566.5~578.5·Z 90~150.5 | 겹침 0 | 0, 블록과 0.5 |
| (c) 패드 ↔ 안내 블록 J −12.5 / 0 / −13.5 | 0.3 / 0.3 / 0.0 | **0.3 / 0.3 / 0.0**(받침면 Z 42) |
| (d) inspect.interference T05 영역, budget 300 | 0, truncated false | count 0, checked 17, truncated false, unchecked 8 = 기준선과 같음 |
| (e) 행정 −13.5 → 0 | 막힘 없음 | joint.sweep 거부(접촉 예산 초과, T05 STEP 바디) → drive −13.5·−12·−10·−8·−6·−4·−2·−1·−0.5·0 + clearance(PAD·NTJ·ROD ↔ GUIDE): 전부 겹침 0, truncated false, 최소 0.3(받침면 0.0). 로드 ↔ 천장 구멍 Ø6 1.0 |
| 새 GUIDE ↔ 전 바디 clearance 2.5 | 겹침 0 | 0(unchecked: GD_1·GD_2 인서트 2쌍 = 기준선) |

unchecked 기준선 8쌍: GUIDE–MBIS5 GD_1·GD_2, SEWHEAD–CB5-16_RT_1, CB5-16–MBIS5 GD_1·GD_2, BODY–SNJ, ROD–NTJ ×2(모두 나사 물림·STEP 하위 바디, v0.8.0과 같음).

스크린샷(사람용, 열어 보지 않음): `tools/out/mech_T15/v081_iso.png`.

## 4. 강도 손계산(E-18, 해석 못 함 — 환경 없음, D-16)

`fea/cases/mech_T15_handcalc.py` → `tools/out/mech_T15/handcalc_out.txt`. PET-CF 허용 30 MPa(DP-3 보수값).

| 항목 | 하중·치수 | σ | SF |
|---|---|---|---|
| 앞벽 오조작B v0.8.0 | 417.5 N × 40.5, b 59, t 9.2 | 20.32 | 외팔 1.48, 두 변 2.95 |
| **앞벽 오조작B v0.8.1** | 417.5 N × 31.5(Z 45 → 천장 밑면 76.5) | 15.80 | 외팔 1.90, **두 변 3.80** ≥ 2, Kt 1.3 2.92 |
| 데크 운전 0.7 MPa | 54.98 N × 12.9, b 35, t 4 | 7.60 | **3.95** ≥ 3, 처짐 0.084, 패드 X 0.34 (T10 ≤ 0.5) |
| 데크 오조작 | 100 N(가정, D-57) | 13.82 | **2.17** ≥ 2 (Kt 1.5 넣으면 1.45 → d1) |

해석용 임시 STEP(E-06 예외): `tools/out/mech_T15/stepout/P_T05_GUIDE.step`(116,811 B).

## 5. 설계검토서에 남길 것

- 제어 순서 제약: 새로 없음.
- 정비 절차(SNJ 풀기): 공압 차단·배기 → 얇은 스패너(맞변 11, 머리 두께 ≤ 4.5, 폭 ≤ 23, 15° 머리)를 −X 입구로 Z 80.5~85.5 틈에 넣는다 → 30°씩 SNJ를 푼다 → 너트가 천장에 앉으면 계속 돌려 몸통을 4 들어 나사에서 뺀다 → 패드를 +X로 15 밀어 NTJ를 T홈 −X 입구로 뺀다 → 실린더를 위로 뺀다. 블록·패드·등판은 떼지 않는다.
- 디테일 기록(E-02, 고치지 않음): d1 데크 R1 Kt 넣으면 오조작 SF 1.45 / d2 출력 방향은 +X 면(X −80) 바닥 / d3 JIS 보통 스패너(두께 6) 안 들어감 / d4 X −147 끝면 미세 경계. 자료대기 D-57.

## 6. 못 한 것·메모

- joint.sweep(4-e)은 엔진 접촉 예산 초과로 두 번 거부(`occurrences T05_PAD:1, against T05:1`, step 0.5 포함). 10자세 drive + clearance로 같은 판정을 했다. 기능상 판정은 끝났다고 본다.
- 매트·테이프 거동은 판정하지 않음(요구서 7절).

## 워크플로우 메모

- `joint.sweep`은 T05처럼 STEP 하위 바디가 많은 유닛에서 접촉 예산을 넘는다(T03 선례와 같음). 지시서에 sweep 대신 drive 스캔을 기본으로 두면 한 번 덜 돈다.
- `inspect.clearance`에 바디 이름 `CJ2B10-15Z_T05_NTJ_2`는 없다(NTJ 두 개가 같은 이름, occurrence 경로로만 구별).
