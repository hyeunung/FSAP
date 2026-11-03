# 모델링부 — N01 U1 헤드 개조 + 좁은 홈 묶음 (2026-11-03, 엔진 v3.7.2)

## 요약(10줄)
- 저장: `3D_Modeling/FSAP_v1.0.2.sc`(문서 이름 FSAP_v1.0.2, 139,230 B). 작업 전 v1.0.1(덮어쓰지 않음). 통로 MCP(앱 27878), 저장 뒤 확인은 저장본 CLI.
- 바뀐 바디 5(순증 0, 전체 36): `STEP대기_867-392342_UPPER`·`_LOWER`(이름만), `STEP대기_867-392342_NOSE`(새), `P_N01_FOOT`(새, S45C 밀링), `U8_CASSETTE_BOX`(X ±11). 지운 바디: U1_BUNDLE·U1_PRESSER_BOX.
- 연구 CYCLE_G1 478 → 528단계(홈 바닥 173~406, 땀 10 × 18°, 현 3.911). CYCLE_G2 597은 키가 이전과 같다.
- 정적 겹침 0. 노루발 0·10·20 × 바늘 0·−15·−30에서 바늘↔노루발 0.7, 노루발대↔노즈 0.5, 겹침 0.
- 연구 38자세(G1 29·G2 3·S 3·L 3) 새 겹침 0: 노루발↔SEAM 0.0(맞닿음), ↔TAPE 1.0, ↔MAT 2.0, 카세트↔TAPE 2.0. 바늘↔MAT_G 10.19 mm³·↔TAPE_G 22.11 mm³(기준선).
- 홈 바닥 바늘↔반대 벽 최소 23.2(계산, stitch_calc), 묶음 폭 최대 22 < 25(D-02 임시).
- 조인트 자기 점검: J_U1_PRESSER 20 → 0, J_U1_NEEDLE 0 → −30 모두 끝까지(stopped_at 없음), floating 0.
- 새 볼트·구매품 STEP 0. 867-392342·MHMF042L1U2M STEP 없음(stepcheck) → STEP대기_867 3개(D-10·D-80). 서보는 DC-05.
- 미완 0. 해석: 노루발 임시 STEP만 내보냄(FEA 환경 없음 D-16).

## 1. 통로·절차
| 항목 | 내용 |
|---|---|
| 연결 판정 | `running` 응답(빈 큐), `inspect_design` 응답 — 앱 연결됨. 열린 문서 FSAP_v1.0.1 dirty false·undo 0·타임라인 error·warning 0 |
| 순서 | `open v1.0.1` → `edit.checkpoint`(225) → `batch` 형상 17단계 → `batch` 연구 + REST + 측정 → `batch` 정적·노루발×바늘 검사 30단계 → REST step 0·`contact.check`(충돌 0) → `save {path: FSAP_v1.0.2.sc}` → 이후 편집 없음 |
| 문서 이름 | 저장 응답 name `FSAP_v1.0.2`(파일 이름에서 정해짐 — 별도 rename 명령은 `document.*`에 없음) |
| 저장 확인 | 저장본 CLI `run --results`(저장 안 함): 바디 36, 바꾸지 않은 U2_BOOM·U6_SENSOR_BOX·U5_TABLE bbox·부피 그대로, floating [] |
| 동작 상태 | 저장 전 `motion.play REST 0`(X·Y·회전 0, 노루발 20, 바늘 0) |
| 연구 단계 검사 | 출력이 커서 앱 대신 저장본 CLI에서 같은 명령으로(5.1 s). 100단계 안팎이라 앱에서도 되지만 화면 출력량 때문에 CLI로 옮김 |
| 파일 | 생성기 `tools/gen_v1_n01.py` → `tools/out/mech_N01/model/stage_1_geom.json`·`stage_2_study.json`, 기록 `tools/out/mech_N01/edit.json`(18단계)·`edit_meta.json`, 검사 `make_chk.py`·`chk_cmds.json`·`verify_cli.json` → `verify_cli_out.json`·`verify_summary.json`, 자기 점검 `sweep.json` → `sweep_out.json`, 그림 `v1.0.2_iso.png`(저장만, 열지 않음) |

## 2. 만든·바꾼·지운 부품(세계 좌표 mm)
| 컴포넌트 | 바디 | X | Y | Z | 부피 mm³ | 재질 | 비고 |
|---|---|---|---|---|---|---|---|
| U1_HEAD | `STEP대기_867-392342_UPPER`(이름 바꿈) | −80~500 | ±90 | 125~560 | 45,414,000 | Default | 867 공식 PDF 암 밑 335×125(D-10·D-79). 윗면 = U2_BOOM 밑면 맞닿음 |
| U1_HEAD | `STEP대기_867-392342_NOSE`(새) | ±11 | −10~15 | 46~125 | 40,410.2 | Default | 노루발대 구멍 Ø7 축 (−5, −3) 관통. 윗면 UPPER와 맞닿음(join 안 함), 바늘 꼭대기 45와 틈 1.0 |
| U1_HEAD | `STEP대기_867-392342_LOWER`(이름 바꿈) | ±30 | ±45 | −120~0 | 647,497.5 | Default | 바늘 구멍 Ø4 그대로, 가마 Ø32는 내부라 안 그림 |
| U1_HEAD | U1_LOWER_DRIVE | 30~500 | −460~−20 | −140~−60 | 그대로 | Default | DC-05 |
| U1_PRESSER | `P_N01_FOOT`(새) | −10~3 | −8~6 | 값 0: 12~80 / REST 20: 32~100 | 2,215.8 | **S45C**(7.85, 17.39 g) | 발바닥 t2(Z 12~14), 바늘 구멍 Ø3 (0, 0), 노루발대 Ø6 축 (−5, −3) Z 14~80 join. 밀링(U-05, 3000 땀/분 마모·바늘 구멍 정밀·발바닥 마감 1-1) |
| U8_CASSETTE | U8_CASSETTE_BOX(좁힘) | ±11(전 ±15) | −45~−21 | 13~124 | 58,608 | Default | 묶음 폭 22 |
| U1_NEEDLE | U1_NEEDLE_PIN | r0.8 | | 값 0: 13~45 | 64.3 | Default | 그대로 |
| — | U1_BUNDLE, U1_PRESSER_BOX | | | | | | **지움**(solid.remove) |

- 그리는 법: `joint.drive J_U1_PRESSER 0` 뒤 세계 좌표로 그리고 `component.move_bodies`로 U1_PRESSER·U1_HEAD로 옮김. 관통 자르기는 위아래 1 mm 더 길게(N01-M02). 카세트는 X −16~−11·11~16 상자로 잘라 이름·컴포넌트 유지.
- 리지드: 새 바디는 기존 컴포넌트(U1_HEAD = REF_GROUND 리지드, U1_PRESSER = J_U1_PRESSER)에 들어가 리지드 그룹 누락 0. 숨김 0(모든 바디 visible true).
- 재질(E-09): 가공품은 P_N01_FOOT 하나, S45C를 `material.create`(밀도 7.85)로 만들어 지정. CAD 기본 Steel 안 씀. 나머지는 차지 공간 상자·STEP대기_(Default). 가공품 BOM이 아직 없어 matcheck는 '검사 대상 없음(BOM 없음)'(실행 규칙 9).
- 형재 0 → 마감캡 대상 0(U-19). 볼트 0 → 빈 구멍: 노즈 Ø7 구멍은 노루발대(Ø6) 통로라 빈 구멍 아님.

## 3. STEP대기 임시 형상(E-10)
| 형번 | stepcheck | 처리 | 치수 출처 |
|---|---|---|---|
| 867-392342 | 없음(같은 계열 없음) | `STEP대기_867-392342_UPPER/NOSE/LOWER` | Dürkopp 867 공식 PDF(암 밑 335×125, 노루발 들림 20, 가마 Ø32), 노즈 폭은 묶음 폭 D-02 임시 25 안(선정 N01-S03). 미스미에 없음(요구서 3-1) → 사용자 자료 D-10 |
| MHMF042L1U2M | 없음 | N01에서 안 넣음(지시서 H15, DC-05) | — |

자료대기 D-80에 이름 3개를 적었다. 구매 사이트는 열지 않았다(새 구매품 없음).

## 4. 검증 수치(E-16, 수치로만)
| 항목 | 결과 |
|---|---|
| 정적 `inspect.interference`(NOSE·FOOT·카세트·UPPER·LOWER·U6·U7_PATH·바늘·U5_TABLE, REST) | 겹침 0(truncated false) |
| 정적 틈 | NOSE↔UPPER 0.0(맞닿음 Z 125), FOOT↔NOSE 0.5, FOOT↔바늘 0.7, 바늘↔NOSE 1.0, UPPER↔카세트 1.0, U6↔카세트 1.0 |
| 노루발 0·10·20 × 바늘 0·−15·−30(9자세, 지시서 G12) | 겹침 0. 바늘↔노루발 최소 0.7(구멍 Ø3 안), 노루발대↔노즈 0.5, 바늘↔LOWER 1.2(Ø4 구멍 안) |
| CYCLE_G1 22·50·97·144·160, 피벗 끝 183·206·229·252·275·298·321·344·367·390·404, 이송 끝 186·209·232·255·278·301·324·347·370·393, 407·430·528 | 새 겹침 0 |
| CYCLE_G2 0·573·574 / CYCLE_S 36·453·454 / CYCLE_L 20·637·638 | 새 겹침 0 |
| 최소 틈(38자세 중) | 노루발↔SEAM_* 0.0(맞닿음), ↔TAPE_* 1.0, ↔MAT_* 2.0. 카세트↔TAPE 2.0·↔SEAM 1.0. 센서↔TAPE 2.0. LOWER↔매트·테이프 0.0(작업면 Z 0, 기준선) |
| 기준선 겹침 | 바늘↔MAT_G 최대 10.19 mm³, ↔TAPE_G 22.11 mm³(바늘 꽂힘, M-08) — 예상값과 같다 |
| 홈 바닥 바늘 중심 180° 회전 중 반대 벽 틈 | 최소 23.2 > 0(stitch_calc far_wall_min, 바늘 겉면 → 반대 테이프 안면), 바늘 꽂힘 중 바늘이 매트 가장자리에서 벗어난 거리 0.0 |
| 홈 건너편 매트 몸통↔헤드 | MAT_G↔NOSE·UPPER·FOOT·카세트·센서 겹침 0(최소 2.0) |
| 작업면 위 바늘 둘레 묶음 폭 | 노즈 22·카세트 22·센서 20·노루발 13 → 최대 22 < 25(D-02 임시) |
| 조인트 자기 점검(`joint.sweep`, 저장본) | J_U1_PRESSER 20 → 0(대상 U1_HEAD·U8·U6·U1_NEEDLE): stopped_at 없음, 시작 맞닿음 없음. J_U1_NEEDLE 0 → −30(대상 U1_HEAD·U1_PRESSER·U8): stopped_at 없음. 행정 끝 = 조인트 한계(스토퍼) |
| floating | 0 |
| 전 사이클 motion.interference | 돌리지 않음(지시서 G14, 라운드 끝 회귀 몫) |

## 5. 기계 정의·연구(E-15)
- `tools/machine.json`: units.U1_HEAD.parts = ["STEP대기_867-392342_", "U1_LOWER_DRIVE"], units.U1_PRESSER.parts = ["P_N01_FOOT"], studies.CYCLE_G1.steps 528(_note 홈 바닥 땀 피벗 10×18°, N01-S02). baseline_overlaps에 P_N01_FOOT↔SEAM_* 맞닿음 Z 12, NOSE↔UPPER 맞닿음 Z 125, 노루발대↔노즈 구멍 틈 0.5를 더하고 옛 이름(U1_UPPER·U1_LOWER_POD)을 새 이름으로 고침.
- 설계 안 연구 CYCLE_G1을 `motion.study {study: "CYCLE_G1", steps: 528, keys}`(15.4 KB, 나누지 않음)로 고침. 조인트 한계·종류는 바꾸지 않음.
- 생성기 `tools/gen_v1_n01.py`: stitch_arc·groove_cycle_new를 옮김(gen_v1_prep.py는 import만). 결과 G1 528, 홈 바닥 [173, 406] 234단계, 현 3.9109, G2 597 키 같음 True(`study_info.json`).

## 6. 서명·임시 STEP
- `ledger.py sigpatch --parts tools/out/mech_N01/changed_parts.json --removed U1_HEAD/U1_UPPER,U1_HEAD/U1_BUNDLE,U1_HEAD/U1_LOWER_POD,U1_PRESSER/U1_PRESSER_BOX` → 바뀜 5, 없어짐 4, 전체 36. `sigcheck` reuse(문서·해시 같음).
- 임시 STEP(해석용, E-06 예외): `tools/out/mech_N01/stepout/P_N01_FOOT.step`(14,532 B). 하중 노루발 누름·끌림. FEA 환경 없음 → 해석 못 함(D-16), 선정 손계산 σ 약 69 MPa(N01-D4).

## 7. 설계검토서에 남길 제어 순서 제약(U-09)
- (a) 홈 바닥 땀마다: 바늘 하사점(−30) 확인 → 노루발 20 → 피벗(X·Y·회전 위치 모드) → 노루발 0 → 바늘 상승 → 1땀 Y 이송.
- (b) 피벗 중 헤드 이송·바늘 상하 금지. (c) 이송 중 회전 금지.
- (d) 아랫축 서보는 윗축 위치에 1:1 전자 동기, 위상 허용(가마 타이밍 약 1~2°, D-10)을 넘으면 즉시 정지.

## 8. 못 한 것·넘긴 것
- 미완 0.
- 넘긴 것(지시서대로, 디테일 기록): 매달기 판·볼트 CB5·핀 → N07(N01-D1), 서보 MHMF042L1U2M 배치 → DC-05(N01-D2), 노루발 밑 ≤ 10 판정 → D-04·D-10(N01-D3), 안발·침판 입술 → N05·7절(N01-D6).
- 외부: 867-392342 STEP 없음(사용자 자료 D-10), MHMF042L1U2M STEP 없음(D-80).

## 워크플로우 메모
- 지시문 절차 2('먼저 다른 이름으로 저장')와 실행 규칙 2('그린 뒤 save {path: 새 번호}', 저장 뒤 편집 금지)가 순서가 다르다. 실행 규칙 2(N00과 같은 순서)를 따랐다.
- `joint.sweep`의 `against`는 바디가 아니라 occurrence 이름(`U1_HEAD:1`)을 받는다(바디 이름을 주면 "no occurrence"로 실패).
- 문서 이름은 `save {path}`가 파일 이름에서 정한다. `document.*`에 이름 바꾸기 명령은 없다.
