# DC-08 모델링 — 송풍 호스 꺾임 자리 (v1.0.17 → v1.0.18)

요약
- 저장본 `3D_Modeling/FSAP_v1.0.18.sc`(문서 이름 FSAP_v1.0.18, REST, dirty false, 바디 164 그대로, 피처 817 그대로). `tools/config.json`·`tools/machine.json` doc를 v1.0.18로. 통로 MCP(앱 --control 27878), 저장 뒤 검사만 CLI.
- 바뀐 부품 2: `P_N04_INLET`(축 (−1185, 1143) 한 덩어리 회전체, PA12, 24,444 mm³), `P_N04_PANEL`(밑 표피 Ø46 구멍 피처 중심만 이동, 부피 변화 0). 지운 부품 0, 새 조인트 0, 볼트 0.
- 호스 판정(계산): R150 ≥ 임시 최소 R150(D-88), X 거리 155(브래킷 −1030)·153(−1032)·195(첫 링크) ≥ 150, 니플 끝 아래 곧은 구간 52, 굽힘 바깥 최저 Z −310.
- 과제 범위 검사 J_U4_X −200~1217.5, 25 mm 58자세: INLET·PANEL ↔ 고정 부품 겹침 0, truncated false, unchecked 0. INLET↔PANEL은 맞닿음 0(설계 끼움).
- 따로 보고: 같은 검사에서 매트 MAT_L·MAT_G ↔ U2_COLUMN 겹침이 J_U4_X ≥ 650에서 나왔다(J_U4_Y·회전 0 자세). 매트·기둥은 이번에 바꾸지 않았고 사이클 연구 자세(회귀)에서는 0이었다 → 이번 변경과 관계없음, 검도·회귀가 볼 것(4절).
- 미완: 없음. 외부 대기: 덕트 호스·밴드 형번(D-89), 끝 브래킷 실물 길이(D-88 STEP 교체). 설계검토서 호스 경로 기재는 문서부.

## 1. 문서 확인·원복·통로

- `running` 빈 큐. `inspect_design`: 열린 설계 **dirty true, path null**, 이름 FSAP_v1.0.17, undo 0·redo 0, 바디 164·피처 817(v1.0.17 저장본과 같은 수). 측정·선정부가 보고한 상태 그대로다.
- 안내서 '문서 확인' "dirty면 … 버리지 않는다"(E-01·E-04)를 지키려고 **열린 설계를 먼저 `tools/out/mech_DC-08/app_dirty_backup_before_DC08.sc`(5,206,704 B)로 저장해 남겼다**. 그다음 `open 3D_Modeling/FSAP_v1.0.17.sc`(errors 0, features 817). undo 0이라 앱 재시작 뒤 복구본으로 보이지만, 판단은 사람에게 남긴다(결정로그 DC-08-M03). 사본은 지우지 않았다.
- `edit.checkpoint`(3) → `motion.play REST step 0`(이미 REST, moved false). 원복할 흔적 없음(첫 회차).
- 타임라인 경고 11개(Boolean retry 등)는 편집 전후 같은 목록이다. error 0.

## 2. 만든·바꾼 부품 (지시서 1~5)

| 부품 | 한 일 | 좌표·치수 | 확인 수치 |
|---|---|---|---|
| `P_N04_PANEL`(U5_AIRTABLE, A5052_HC) | 밑 표피 구멍 피처 **Cylinder160**(r23, h2, cut, base Z −41)의 base만 (−1023, 1040) → (−1185, 1143) (`timeline.edit`) | 구멍 Ø46, Z −40~−39 | 부피 254,174,808.3006 → 254,174,808.3006(변화 0). 원통 면 2쪽(r 23.000, 축 (−1185.0, 1143.0)) 뿐, 옛 자리 면 없음 = 표피 꽉 참. 새 구멍 따로 내거나 메우지 않음(U-10) |
| `P_N04_INLET`(U5_AIRTABLE, PA12, 3D 출력) | 옛 Cylinder153(새 몸 r23 h16)·Cylinder154(cut r19)를 지우고 같은 자리(Box156 뒤, BodyTransfer106 앞)에 `SK_DC08_INLET`(평면 원점 (−1185, 1143, 0), x=X, y=Z) + `Revolve_DC08_INLET`(축 (−1185, 1143) Z, 360°, body_name P_N04_INLET) | 단면(r, z): (17,−85)(18,−85)(19,−84)(19,−45)(35,−45)(35,−40)(23,−40)(23,−39)(17,−39). 끼움 턱 Ø46 Z −40~−39, 플랜지 Ø70 Z −45~−40, 니플 Ø38 Z −85~−45 끝 C1, 관통 Ø34 Z −85~−39 | bbox X −1220~−1150 · Y 1108~1178 · Z −85~−39, 중심 (−1185.0, 1143.0). 부피 24,444.0 mm³ = 목표 24,504 − C1 고리 약 59(계산 24,445). 질량 24.69 g. 면 9(원뿔 1 = C1), 닫힘 1 shell |

- 회전체를 한 피처로 만들고 덧붙인 피처는 없다. `timeline.redefine`이 피처 종류를 바꾸지 못해(Cylinder → Revolve 거부) 옛 피처 둘을 지우고 같은 자리에 새로 넣었다. 같은 이름 몸이 같은 자리에서 생기므로 BodyTransfer106(→ 컴포넌트 117 U5_AIRTABLE)이 오류 없이 이어 받았다(DC-08-M02).
- 고정: 플랜지 윗면(Z −40)을 판 밑면에 에폭시 접착(볼트 없음, 디테일 DC-08-D1).
- `P_DC03_XMOV`·베어·홈통: 고치지 않음. 저장본 XMOV bbox X −1050~−950 · Y 1000~1101 · Z −348~−262, 부피 68,898.2 그대로.
- 지운 부품 0, 남은 구멍 0(옛 판 구멍은 피처가 옮겨 가 없음, 옛 INLET 구멍은 몸과 함께 없어짐).
- 구매품: 덕트 호스 ID38/OD46·호스 밴드 40~60 ×2는 **바디를 그리지 않음**(형번 미정, N04-S07, E-10 "형번이 정해지지 않은 추정 바디 … 금지", 지시서 3). 그래서 STEP대기_ 임시 형상도 두지 않았다. stepcheck: DHPU38·HFB40-60·HBW40-60 없음, E4.56.10.150.0 있음(이번에 안 바꿈).
- 문서 설명: `DC-08 mechanism: N04 inlet moved to (-1185,1143) on cable carrier axis, flange nipple PA12, panel hole moved`.

## 3. 호스 경로(계산 판정, 설계검토서에 넣을 것)

| 구간 | 좌표 | 수치 |
|---|---|---|
| 니플 끼움 | 축 (−1185, 1143), Z −85~−45 | 밴드 1: Z −75~−66, 나사부 −X |
| 수직 곧은 구간 | Z −85 → −137 | 52 |
| 굽힘 R150 1/4호 | 중심 (X −1035, Y 1143, Z −137), 끝 (−1035, Z −287)에서 +X | R150 ≥ 임시 최소 R150(D-88). 굽힘 바깥(반경 173) 최저 Z −310 |
| 수평 | Z −287 · Y 1143 → 끝 브래킷 면 −1030 + J, 첫 링크 −990 + J | X 거리(축→): 브래킷 −1030 155, −1032 153, 첫 링크 195 — 모두 ≥ R 150 |
| 블로어 쪽 | 밴드 2: 블로어 출구(위치 미확인, D-89) | — |

- 쓸기: 호스 −X 끝 −1208 + J. J −200에서 −1408로 쓸기 한도 −1410 안.
- 호스 위 면 Z −264 = 베어 안 윗면(Z 여유 0, DC-08-D2).
- 축 X −1185는 허용 −1187 ≤ X_c ≤ −1182 안.

## 4. 저장 전·후 검사 (E-16·E-17·E-22)

| 항목 | 결과 |
|---|---|
| 주변 틈(MCP, REST) | `inspect.clearance` INLET vs 이웃 90바디, clearance 120: 겹침 0. 판 맞닿음 0(접촉, 부피 0), 다음 STEP대기_E4.56.10.150.0 165.0, HFS8_1 176.6, STORE_P 180.0, 2400.05.075.0 215.1 |
| 리지드 그룹(E-11) | `joint.list` floating 0, errors 0, conflicts 0. INLET은 컴포넌트 117 = U5_AIRTABLE(U4_X와 리지드) |
| 숨김 | 숨긴 바디 0 |
| 재질(E-09) | INLET PA12(1.01 g/cm³), PANEL A5052_HC 그대로 |
| 조인트 자기 점검 | 새 조인트·행정 변경 없음. INLET이 U5_AIRTABLE 몸이라 J_U4_X를 따라감을 아래 58자세로 확인(겹침 0) |
| 과제 범위(CLI, 저장본) | `solidcraft-cli run sweep_n.json --in FSAP_v1.0.18.sc --results` 4묶음 병렬 185 s. 58자세(−200~1200 25 간격 + 1217.5). bodies: INLET·PANEL·MAT_L·MAT_S·MAT_G, against: U4_FIX 12종 + CB5-20_N03XR 60·CB5-12_DC03XT 6 + U2_BRIDGE 5. truncated false, unchecked 0. **INLET·PANEL 겹침 0** |
| 매트 겹침(이번 변경과 무관) | MAT_L ↔ U2_COLUMN J 650~1217.5(최대 144,000 mm³), MAT_G ↔ U2_COLUMN J 825~1217.5. J_U4_Y·회전이 REST인 채 X만 끝까지 민 자세다. 매트·기둥은 이번에 안 바꿨고(signatures 그대로), 회귀(mech_regression_2.md)는 사이클 자세에서 매트↔고정 0이었다. 검도·회귀가 X 단독 자세가 실제 사이클에 있는지 본다 |
| 저장 확인 | 저장 뒤 `inspect_design` dirty false, 이름 FSAP_v1.0.18, 바디 164, error 0. CLI 저장본 측정: INLET·PANEL·XMOV·U4_X_BEAM bbox·부피가 앱 값과 같음(`savecheck_out.json`) |
| 서명 | `ledger.py sigpatch --parts out/mech_DC-08/changed_parts.json`: 바뀜 2, 없어짐 0, 전체 312 |
| 볼트 | 새·옮긴 볼트 없음 |
| 강도(새로 만든 것만, 손계산) | 선정 보고서 값: 니플 σ 0.21 MPa·후프 0.43 MPa / PA12 45 MPa → SF > 60, 접착 0.041 MPa / 에폭시 5 MPa → SF > 100. FEA 못 함 — 환경 없음(D-16) |

## 5. 제어 순서 제약(U-09)

새로 생기는 것 없음. 송풍 ON은 사이클 ① 그대로.

## 6. 산출물

- 저장본 `3D_Modeling/FSAP_v1.0.18.sc`, 앱 dirty 사본 `tools/out/mech_DC-08/app_dirty_backup_before_DC08.sc`
- 기록 `tools/out/mech_DC-08/edit.json`(11단계)·`edit_meta.json`(base v1.0.17 → result v1.0.18)
- 검사 `tools/out/mech_DC-08/gen_sweep.py`, `sweep/out_0~3.json`, `sweep_summary.json`, `savecheck_out.json`, `changed_parts.json`
- 임시 STEP(해석용) `tools/out/mech_DC-08/stepout/P_N04_INLET.step`
- 스크린샷(사람용, 열지 않음) `tools/out/mech_DC-08/dc08_iso.png`

## 시간·통로 (E-23)

- 걸린 시간 약 15분(모델링 등급 M 예상 90분 안). CAD 호출: MCP 약 22(running·inspect 2·open·save 2·batch 5·execute 8·export·list 3), CLI 7(sweep 4·savecheck·snapshot·script 1 실패). 설계 파일 열기: MCP 1, CLI 6. 브라우저 0.

## 워크플로우 메모

- 앱 열린 설계가 dirty(path null, undo 0)로 남아 측정·선정이 CLI로 갔고 모델링부도 멈출 뻔했다. 사본 저장 후 open으로 풀었다. 앞 부서가 이 상태를 만나면 "사본 저장 → open" 절차를 안내서에 두면 좋겠다.
- `solidcraft-cli script`는 컴포넌트가 있는 설계를 못 뽑는다(#886, 1분 50초 걸려 실패). 피처 찾기는 `inspect_design` 타임라인 + `timeline.inspect`가 빠르다.
- `timeline.redefine`은 피처 종류를 바꾸지 못한다. 모양 종류가 바뀌는 다시 그리기는 "같은 자리 지우고 같은 이름 몸으로 새로"가 BodyTransfer를 살린다.
- 과제 범위 검사에 매트를 넣으라는 지시가 J_U4_X 단독 자세라 사이클에 없는 매트↔기둥 겹침이 나온다. 매트는 사이클 연구 자세로 보게 지시하면 좋겠다.
