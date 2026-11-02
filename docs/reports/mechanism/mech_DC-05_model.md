# DC-05 모델링 — 아랫유닛 구동 자리 이동(v1.0.2 → v1.0.3)

요약
- 저장본: `3D_Modeling/FSAP_v1.0.3.sc`(문서 이름 FSAP_v1.0.3, REST 자세, dirty false). `tools/config.json` doc을 이 파일로 바꿨다.
- 지움: 옛 `U1_LOWER_DRIVE` 상자(X 30~500·Y −460~−20·Z −140~−60).
- 새로 만듦(U1_HEAD): `U1_LOWER_LINK` 각관 90×60 t4(X 30~650), `U1_LOWER_STAND` 받침(X 530~610·Z −380~−120), `U1_LOWER_DRIVE` 끝판 t4(X 650~654, Ø50 구멍), `STEP대기_MHMF042L1U2M`(X 654~764, D-81 임시).
- 고침: `U5_TABLE` 두 홈의 −X 끝을 40 늘림(−1292.5·−762.5), `U4_X_BEAM` +X 면 −750 → −760.
- 완료 판정: U1_LOWER_DRIVE X 650 ≥ 390. J_U4_X −200~1250(Y 0) 스윕은 stopped_at null(최소 틈 10). J_U4_Y −400~1200(X 0)도 접촉 0. 사이클 표본 23자세에서 새 바디 겹침 0.
- 금지 띠: 1250/400 자세에서 U3_COLUMN↔LINK가 81,620 mm³ 겹친다. 지시서대로 예상한 겹침이다. machine.json `xy_forbidden`에 넣었고 N03 소프트 리밋으로 넘긴다.
- 통로: MCP. 앱에서 open v1.0.2 → checkpoint → batch → 검사 → save {path: v1.0.3} 순서로 했다. 저장 확인은 CLI eval로 했다. 새 볼트·조인트는 없다. FEA는 못 했다(환경 없음, D-16).
- 미완은 없다. 디테일로 넘긴 것은 7절에 적었다.

## 1. 통로·순서(E-04, 실행 규칙 2)
| 단계 | 내용 |
|---|---|
| 연결 | `running` 응답 [] · `inspect_design` 응답 정상 → 앱 켜짐. 열린 설계 FSAP_v1.0.2, dirty false |
| 열기 | `open 3D_Modeling/FSAP_v1.0.2.sc` → features 96, errors 0. 타임라인 error·warning 모두 null |
| 원복 | `edit.checkpoint` 242(편집 전) |
| 그림 | `batch` 15단계 = `tools/out/mech_DC-05/model/stage_1_geom.json`(생성기 `tools/gen_v1_dc05.py`) |
| 검사 | `batch` 측정 6 + 스윕 2, `batch` 자세별 clearance 10자세, `batch` 사이클 표본 23자세(결과는 `tools/out/mech_DC-05/cyc_result.json`) |
| 저장 | REST step 0 → `save {path: 3D_Modeling/FSAP_v1.0.3.sc}` → name FSAP_v1.0.3, dirty false. 이후 편집 없음(임시 STEP export만 했다) |
| 저장 확인 | CLI `solidcraft-cli eval verify.json --in FSAP_v1.0.3.sc`: 바디 39(36 − 1 + 4). 바꾼 바디와 바꾸지 않은 U2_COLUMN·U3_COLUMN·MAT_L의 bbox가 저장 전과 같다(`saved_bodies.json`) |
| 문서 이름 | save 응답 name `FSAP_v1.0.3`(파일 이름에서 정해짐) |

## 2. 만든·지운·고친 부품(좌표: 바늘점 원점 mm, J_U4_X·Y 0)
| 부품 | 유닛(컴포넌트) | bbox X / Y / Z | 부피 mm³ | 질량 g | 재질·제작 |
|---|---|---|---|---|---|
| U1_LOWER_LINK(새) | U1_HEAD | 30~650 / −45~45 / −120~−60, 안 Y ±41·Z −116~−64 | 704,320 | 5,529 | SS400(STKR400) 각관 90×60 t4 절단, 양끝 베어링 자리 가공, 용접 없음 |
| U1_LOWER_STAND(새) | U1_HEAD | 530~610 / −40~40 / −380~−120 | 1,664,000 | 13,062(꽉 찬 차지 형상) | SS400 판금 ㄷ 기둥 + 바닥판 t4(상세는 디테일) |
| U1_LOWER_DRIVE(새로 그림, 같은 이름) | U1_HEAD | 650~654 / −45~45 / −120~−60, Ø50 구멍 축 (Y 0, Z −90) | 13,747 | 108 | SS400 t4 레이저 평판, 굽힘 없음 |
| STEP대기_MHMF042L1U2M(새) | U1_HEAD | 654~764 / −30~30 / −120~−60 | 396,000 | (Default) | 구매품 임시 형상(E-10) |
| U5_TABLE(고침) | U5_AIRTABLE | −2010~210 / −1545~1560 / −40~0 | 255,099,000 | — | 바늘 홈 X −1292.5~220, 기둥 홈 X −762.5~220 |
| U4_X_BEAM(고침) | U4_X | −1050~−760 / −1000~1000 / −340~−260 | 46,400,000 | — | 폭 290 |
| U1_LOWER_DRIVE 옛 상자(지움) | U1_HEAD | 30~500 / −460~−20 / −140~−60 | — | — | — |

- 리지드: 새 바디 4개는 `component.move_bodies`로 U1_HEAD에 넣었다. U1_HEAD는 REF와 리지드다(Rigid Group 2:73). `joint.list`에서 floating은 0이다.
- 숨김: 모든 바디가 visible true다(숨김 0).
- 재질: SS400(7.85 g/cm³)을 새로 만들어 가공품 3개에 줬다. 구매품 임시 형상은 Default로 두었다(N01의 STEP대기_와 같다). matcheck: 가공품 BOM에 새 부품이 아직 없다. BOM 갱신은 문서부가 한다.
- 빈 구멍: 끝판 Ø50은 서보 인로 자리이고 서보 임시 형상이 맞닿아 있다. 볼트 구멍은 이번에 만들지 않았다(체결은 디테일).
- 지시와 다른 점: 각관 속은 YZ 단면 스케치 대신 상자 자르기(X 29~651)로 만들었다. 결과 형상은 같다. 빔 자르기 상자는 X −760~−749로 1을 넘겨 같은 평면 자르기를 피했다. 결과 bbox는 지시와 같다(결정로그 DC-05-M01·M02).

## 3. 검사(E-16 수치, E-17 과제 범위)
### 3-1. 스윕(지시 F①②)
`joint.sweep`, step 25, refine 0.01, occurrences U3_ROT·U4_Y·U4_X·U5_AIRTABLE, against U1_HEAD·U2_BRIDGE·U4_FIX·U6_SENSOR·U7_TAPE·U8_CASSETTE·U9_LOAD.

| 스윕 | stopped_at | 최소 틈(쌍·값) |
|---|---|---|
| J_U4_X −200→1250, Y 0 | **null(끝까지)** | U1_HEAD↔U5_AIRTABLE 10.0(−200), U4_X↔U2_BRIDGE 10.0(1250), U2_BRIDGE↔U5 10.0(300), U9_LOAD↔U5 10.0 |
| J_U4_Y −400→1200, X 0 | **null(끝까지)** | U1_HEAD↔U5 10.0, U4_X↔U2_BRIDGE 40.0, U9↔U5 10.0 |

`touching_at_start`의 U4_FIX↔U4_X(레일 미끄럼 접촉)는 N00부터 있던 것이고 바뀌지 않았다.

### 3-2. 새 바디 clearance(지시 F③④, 15 mm 안쪽)
| 자세 X/Y | 겹침 | 가장 가까운 것 |
|---|---|---|
| 0/0 | 0 | LINK↔LOWER 0.0(X 30 면 맞붙음, 설계), STAND↔U2_BASE 0.0(Z −380 얹힘, 설계), LINK↔U5_TABLE 22.4 |
| −200/0 | 0 | LINK↔TABLE 30.0 |
| 162.5/0, 525/0, 887.5/0 | 0 | LINK·끝판↔TABLE 22.4, 서보↔TABLE 32.0, LINK↔MAT 60 |
| 1250/0 | 0 | STAND↔U4_X_BEAM 30.0, 끝판↔TABLE 22.4 |
| 1212.5/862.5 | 0 | 같은 값, STAND↔BEAM 67.5 |
| 0/−400, 0/1200 | 0 | LINK↔TABLE 22.4 |
| **1250/400** | **U3_COLUMN↔LINK 81,620 mm³**(bbox X 300~400·Y ±45·Z −120~−60) | LINK↔U3_DRIVE 10.0(Z, 점 415,45,−130/−120) — 금지 띠, 예상대로 |

### 3-3. 사이클 표본(과제 범위, 6-1)
`motion.play` 0·25·50·75·100 % 단계에서 새 바디 4개와 움직이는 바디·매트·테이프의 clearance를 쟀다. CYCLE_L 5, CYCLE_S 5, CYCLE_G1 5, CYCLE_G2 5, REWIND_EMPTY 3, 모두 23자세다. **겹침 0, truncated false**이고 최소는 LINK·끝판↔U5_TABLE 22.4다. 전 사이클 `motion.interference`는 돌리지 않았다(실행 규칙 2 '오래 걸리는 검사는 앱에서 돌리지 않는다', 라운드 끝 전체 회귀가 한다, E-03).

### 3-4. 조인트 자기 점검(E-15)
새 조인트는 없다. 바꾼 유닛은 U1_HEAD(고정)·U4_X·U5_AIRTABLE이다. J_U4_X·J_U4_Y는 전 행정 −200~1250·−400~1200을 끝까지 갔다(스토퍼는 limits). REST에서 X 0·Y 0·회전 0·노루발 20·바늘 0으로 저장했다.

## 4. 기계 정의(E-15)
`tools/machine.json`
- U1_HEAD parts에 `U1_LOWER_LINK`·`U1_LOWER_STAND`·`STEP대기_MHMF042L1U2M`을 더하고 `_note`를 고쳤다.
- 최상위에 `xy_forbidden: [{"plate_center_x":[-20,350],"plate_center_y":[-95,95],"reason":"DC-05 U1_LOWER_LINK ↔ U3_COLUMN r50, N03 소프트 리밋"}]`를 더했다.
- `doc`이 v1.0.1로 남아 있어(N01 때 고치지 않음) v1.0.3으로 고쳤다.

## 5. 서명·임시 STEP·다시 실행 재료
- `ledger.py sigpatch --parts tools/out/mech_DC-05/changed_parts.json --removed U1_HEAD/U1_LOWER_DRIVE` → 바뀜 6, 없어짐 1, 전체 39. `sigcheck` reuse(문서·해시 같음).
- 임시 STEP(해석용, E-06 예외): `tools/out/mech_DC-05/stepout/U1_LOWER_LINK.step`(8,904 B), `U1_LOWER_STAND.step`(5,545 B), `U1_LOWER_DRIVE.step`(10,026 B). 하중 길은 받침 → LINK 외팔 530 → STAND → U2_BASE이고, 서보는 끝판에 달린다. FEA 환경이 없어 해석하지 못했다(D-16). 선정 손계산은 σ 4.2 MPa, SF 58, 처짐 0.06 mm(3배 하중)다.
- `tools/out/mech_DC-05/edit.json`(stage_1_geom.json과 같은 15단계), `edit_meta.json` {base v1.0.2, result v1.0.3}.
- 사람용 그림: `tools/out/mech_DC-05/dc05_iso.png`(열어 보지 않음).

## 6. STEP 대기 임시 형상(E-10)
| 형번 | 바디 | 치수 | 출처 |
|---|---|---|---|
| MHMF042L1U2M | STEP대기_MHMF042L1U2M | □60 × 몸 110, 축 −X, 축선 Y 0·Z −90 | 선정 지시서 B4의 임시값(D-81)이다. 카탈로그 외형도 쪽·표는 이 부서가 확인하지 못했다(브라우저 미사용, 실행 규칙 10 '기다리지 않는다'). stepcheck '없음', PartsLibrary 없음 |

자료대기 D-81의 '쓰는 곳'에 v1.0.3·생성기·이 보고서를 더했다.

## 7. 설계검토서에 남길 제어 순서 제약(U-09)·디테일(E-02, 기록만)
- N03 소프트 리밋: 원판 중심 X −20~350·|Y| < 95 진입 금지(machine.json xy_forbidden).
- 아랫축 서보는 헤드 주축과 전자 동기 1:1이다(N01-S06).
- 디테일:
  - 커플링 형번(Ø40×약 40, 각관 안 X 약 600~645)
  - 각관 안 베어링
  - 볼트와 렌치 길(측면 ±Y로 접근): LINK↔STAND, STAND↔U2_BASE, 끝판↔LINK, 서보↔끝판
  - 가마↔바늘 정렬(외팔 처짐 3배 0.06 mm, 1배 약 0.02 mm)
  - U3_DRIVE를 키울 때 LINK와의 Z 틈 10 유지(실측 10.0, 1250/400). DC-06 모터는 −X·+Y 쪽으로 키우고 위로 키우지 않는다
  - STAND 판금 상세

## 워크플로우 메모
- `export`는 폴더가 없으면 실패한다(stepout을 먼저 만들어야 함).
- `motion.play`를 `quiet: true`로 불러도 자세가 바뀌면 occurrence 자세 목록을 돌려준다. 23자세 batch 응답이 146 KB가 되어 파일로 빠졌다. 큰 표본 검사는 응답을 줄이는 방법이 필요하다.
- 지시문 절차 2('먼저 다른 이름으로 저장')와 실행 규칙 2('그린 뒤 save {path}', 저장 뒤 편집 금지)는 순서가 다르다. 실행 규칙 2를 따랐다(N01과 같다).
