# DC-04 모델링 — 정비 면·카세트 인출·가마 꺼내는 길 (v1.0.4 → v1.0.5)

요약(10줄 안쪽)
- 저장본 `3D_Modeling/FSAP_v1.0.5.sc`(문서 이름 FSAP_v1.0.5, REST, dirty false, 바디 47). `tools/config.json` doc을 바꿨다. 통로는 MCP(앱 --control 27878, `running` 빈 큐, `inspect_design` 응답)다.
- 새 부품은 6종 8바디다: `P_DC04_HANGER`(SUS304 t3 판금, 굽힘 3), `P_DC04_CARRIER`(SUS304 t4 판금 ㄱ, 굽힘 1), `STEP대기_SSEB13-560_RAIL`·`_BLOCK`, `STEP대기_IXP-M8`, `CB5-12_1~3`(실물 STEP). 새 컴포넌트는 U8_GUIDE(고정)다.
- 바꾼 부품: U2_BASE 포켓 −158,080,000 mm³, 867 UPPER 밑면 Ø4.2×12 탭 ×3, U8_CASSETTE_BOX(N01 월드 고정 자르기 정리, 형상 같음). 새 조인트 J_U8_PULL(slide +X 0~511, 손), 연구 MAINT(21단계), REST에 J_U8_PULL 0 키를 넣었다.
- 판정(F): 새 바디는 가동부·매트 3장과 겹침 0이다(J_U4_X −200·0·1250 × J_U4_Y −400·0·1200, J_U8_PULL 0·255·511). MAINT에서 서는 자리·팔 길·카세트 길(PR_CAS_SLIDE)도 겹침 0이다. 운전 자세에서 서는 자리·팔 길↔테이블·매트 겹침은 DC04-Q1로 처리한다.
- 손 닿는 거리(D-82 ≤ 600)는 선정값을 그대로 쓴다(카세트 498·가마 474·바늘 504·노루발 501·플런저 572). 포켓 면 X 500과 부품 자리가 지시서대로라 바뀌지 않는다.
- 자기 점검: floating 0, 스윕 0→511 stopped_at null, 511에서 캐리어 +X 531 = 끝 탭 531(스토퍼). 다시 실행(edit.json → v1.0.4) 바디 47개의 부피·bbox가 같다.
- 지시와 다르게 그린 곳 3: 걸이 앞 혀 추가·다리 끝 X 522(M02), 캐리어 러그 전 높이(M03), 앞 탭 위 Z 119(지시와 같음). 근거는 2절.
- 미완: 없다. 외부 대기: SSEB13-560·IXP-M8·CB3-8 STEP(D-83), 867 UPPER 탭 자리(D-10). 해석 못 함 — 환경 없음(D-16).

## 1. 문서 확인·원복·통로
| 항목 | 값 |
|---|---|
| 앱 상태 | `running` 빈 큐. FSAP_v1.0.4가 dirty false·undo 0으로 열려 있었다. `open FSAP_v1.0.4.sc`의 결과는 errors 0, features 107이다 |
| 원복 | 흔적 없음. `edit.checkpoint`(269)는 다음 호출에서 "no checkpoint"였다(측정·선정 때와 같음). 시험 삽입 1건은 undo로 지웠다 |
| 동작 상태 | REST step 0에서 그리고, 저장 전에 REST step 0으로 되돌렸다 |
| 저장 | `save {path: 3D_Modeling/FSAP_v1.0.5.sc}` → name FSAP_v1.0.5, 238,478 B. 저장 뒤에는 편집하지 않았다(export·screenshot만 했다) |
| 저장 확인 | `inspect_design` dirty false, 타임라인 error·warning 0. 저장본에 CLI `run --results`(저장 안 함)로 바디 47을 쟀다. 바꾸지 않은 부품의 bbox는 v1.0.4와 같다(다시 실행 비교) |
| CAD 호출 | MCP 약 40, CLI 3(확인 1·다시 실행 1·측정 1). 파일 열기 3(MCP open 1, CLI 2) |

## 2. 만든 부품·좌표(바늘점 원점, mm, REST)
| 부품 | 컴포넌트 | 재질·방법 | bbox X / Y / Z | 부피 mm³ | 비고 |
|---|---|---|---|---|---|
| P_DC04_HANGER | U8_GUIDE | SUS304 t3 판금(R3, K 0.44) | −24~534 / −90~−26 / 64~125 | 86,357 | 플랜지 Y −90~−72·Z 122~125(X −24~522), 다리 Y −75~−72, 앞 탭 X −24~−21·Y −75~−26·Z 64~119, 끝 탭 X 531~534·Y −75~−49·Z 64~92. Ø5.5 ×3(X −10·240·480, Y −84), M8 자리 Ø8(Y −36, Z 78). 전개 622.6×73.8, 굽힘 3(540·55·28), 모서리 릴리프 자동 |
| P_DC04_CARRIER | U8_CASSETTE | SUS304 t4 판금 ㄱ(R4) | −20~20 / −52~−30 / 64~124 | 11,989 | 판 Y −52~−48(평면 X −12~20), 러그 X −20~−16·Y −44~−30(전 높이), Ø6H7 (Y −36, Z 78), 테이프 창 X −10~10·Z 70~85 |
| STEP대기_SSEB13-560_RAIL | U8_GUIDE | 임시 형상(E-10) | −20~540 / −72~−64 / 99.5~112.5 | 58,240 | M3 구멍은 디테일 DC-04-D1 |
| STEP대기_SSEB13-560_BLOCK | U8_CASSETTE | 임시 형상 | −20~20 / −64~−52 / 92.5~119.5 | 12,960 | |
| STEP대기_IXP-M8 | U8_GUIDE | 임시 형상 | −64~−16 / −42~−30 / 72~84 | 4,816 | 몸 Ø12 X −64~−24, 나사 Ø8 X −24~−21, 핀 Ø6 X −21~−16 |
| CB5-12_1~3 | 각자(REF 리지드) | SCM435, 실물 STEP | 머리 Z 117~122, 나사 Z 122~134 | 476 ×3 | (X −10·240·480, Y −84), 머리 −Z |

치수 출처(E-10): SSEB13-560·IXP-M8 외형은 선정 보고서 3-3·4와 `tools/out/mech_DC-04/catalog.md`(미스미 카탈로그 외형도 웹 규격표의 레일 폭 13·높이 8, 블록 길이 40, 인덱스 플런저 M8 몸 40·핀 Ø6)를 그대로 썼다. 형번 임시는 D-83에 있다. CB3-8은 이번에 그리지 않았다(DC-04-D1).

바꾼 부품:
| 부품 | 바뀜 | 부피 전→후 |
|---|---|---|
| U2_BASE | 포켓 자르기 X 500~985 · Y 60~700 · Z −910~−370 → U자, +X 다리 Y −1555~60·700~1560 | 5,102,370,000 → 4,944,290,000 (−158,080,000 = 칸 부피) |
| STEP대기_867-392342_UPPER | 밑면 Ø4.2 깊이 12 ×3 (Z 125~137) | 45,414,000 → 45,413,502 |
| U8_CASSETTE_BOX | Box44·45 지움, Box28 X −11~11 | 58,608 그대로(511에서도 58,608) |

지시와 다르게 그린 곳(지시서의 기준을 지키는 쪽으로 정함):
- **M02 걸이 앞 혀·다리 끝:** 앞 탭(Z 64~119)이 다리 모서리에서 굽혀 나오려면 다리에도 Z 64~92가 있어야 한다. 그래서 앞 혀 X −24~−10을 더했다. 끝 탭을 Z 64~92로만 굽히려고 다리 위쪽 끝을 X 522로 띄웠다. 그 결과 플랜지는 X −24~522이고, 볼트 X 480 자리는 그대로다. 테이프 길 X −10~10은 비웠다.
- **M03 캐리어 러그 전 높이:** 지시는 Z 64~92인데 Z 64~124로 그렸다. 판금 edge flange가 −X 모서리 전체를 굽혔다. 러그 X −20~−16·Y −48~−30·Z 92~124 칸에는 다른 바디가 없다. 인출 길 PR_CAS_SLIDE 겹침 0, 노즈 틈 20.6이다. 판의 평평한 면은 굽힘 R4 때문에 X −12부터다.
- 앞 탭 위 끝 Z 119는 지시와 같다(판금 모서리 릴리프 자동).

## 3. 조인트·기계 정의(E-15)
- J_U8_PULL: slider, a = U8_GUIDE:1, b = U8_CASSETTE:1, 원점 (0, −50, 100), z +X, flip true, 한계 0~511. 511로 움직여 +X(카세트 X 500~522)인지 확인했다.
- 지운 조인트: Rigid Group 2:108(REF_GROUND ↔ U8_CASSETTE).
- 새 리지드: REF_GROUND ↔ U8_GUIDE·CB5-12_1~3(Rigid Group 2:211·2:202·2:205·2:208).
- `joint.list`: floating 0, conflicts 0. U8_CASSETTE dof 1이다.
- 연구: REST(6키, J_U8_PULL 0)를 넣었다. MAINT는 21단계로, step 0 = MAINT, step 21 = MAINT_CAS다. 기존 CYCLE 연구에는 J_U8_PULL 키가 없어 REST 값 0이 유지된다.
- machine.json:
  - joints에 J_U8_PULL을 더했다.
  - units에 U8_CASSETTE(moving true, 부품 더함)와 U8_GUIDE를 넣었다.
  - studies에 MAINT를 더했다.
  - states의 '대기'에 J_U8_PULL 0을 넣고, MAINT·MAINT_CAS를 더했다.
  - doc은 v1.0.5다.

## 4. 검증 수치(E-16 수치만, E-17 과제 범위)
### 4-1. 새·바뀐 바디 ↔ 주변(MCP inspect.clearance, skip_within component)
대상 9바디(새 8 + U8_CASSETTE_BOX), against는 867 UPPER·NOSE·LOWER, U6, U7, FOOT, NEEDLE, LOWER_LINK·STAND·DRIVE, 서보, U2_COLUMN·BOOM, U5_TABLE, U4_X_BEAM, U4_Y_CARR, U3_DRIVE·PLATE, 매트 3장·TAPE·SEAM이다.

| 자세 | 겹침 | 가까운 쌍 |
|---|---|---|
| J_U8_PULL 0, J_U4_X −200 × Y −400·0·1200 | 0 | UPPER↔HANGER 0.0(플랜지 맞닿음), UPPER↔CARRIER·카세트 1.0, U6↔카세트 1.0, U6↔CARRIER·HANGER 4.0 |
| J_U4_X 1250 × Y −400·1200, J_U4_X 0 × Y 0 (clearance 30) | 0 | U7_PATH↔HANGER 5.0, U7_PATH↔CB5-12_1 6.75, TAPE_L↔카세트 4.47, 노즈↔카세트 11.0, 테이블↔카세트 16.4 |
| MAINT, J_U8_PULL 255 | 0 | BLOCK↔RAIL 0.0(얹힘), UPPER↔CARRIER·카세트 1.0 |
| MAINT_CAS, J_U8_PULL 511 | 0 | UPPER↔카세트·CARRIER 1.0(X 500 가장자리) |

- 새 바디끼리(inspect.interference 9바디)는 겹침 0이다. HANGER↔RAIL은 면 맞닿음이라 unchecked 1이다.
- UPPER↔CB5-12 ×3은 나사 물림(Ø5 ↔ 탭 Ø4.2)이라 검사에서 뺐다(unchecked).
- 가동부(U3·U4·U5·매트, Z ≤ 12)는 새 부품(Z ≥ 64)과 30 안에 들지 않는다. 그래서 X·Y 자세에 따라 결과가 바뀌지 않는다.

### 4-2. 정비 길(CLI, 저장본, 프로브 = 선정 좌표, clearance 0.4)
| 프로브 | MAINT(J_U4_X −200) | J_U4_X 0 | J_U4_X 1250 |
|---|---|---|---|
| PR_STAND X 500.5~975 · Y 100~700 · Z −379.5~1100 | **0** | 0 | 테이블 11,388,000·매트 L/G·TAPE(DC04-Q1) |
| PR_ARM X 30.5~500 · Y 45.5~560 · Z −59.5~124.5 | **0** | 테이블 3,625,900(DC04-Q1) | 테이블·매트(DC04-Q1) |
| PR_CAS_SLIDE X 20.5~531 · Y −64~−30 · Z 64~124 | **0**(HANGER·RAIL 맞닿음 0.0) | 0 | 0 |
| PR_KEY1~3 볼트 머리 아래 Ø8.5×30 | **0**(머리와 맞닿음) | 0 | 0 |
| PR_HAND_A(플런저 손 길) X −70~−12 · Y −31~15.5 | HANGER 앞 탭 825, CARRIER 러그 240, 플런저 179.9 | 같음 | 같음 |

PR_HAND_A 겹침은 선정 프로브가 앞 탭(Y −72~−26)과 러그(Y −48~−30) 끝 1~5 mm를 덮어서 생긴다. 지시 좌표 그대로도 생기고, 손이 잡는 플런저 손잡이(X −64~−24) 자리라 F 판정 항목이 아니다. 러그를 전 높이로 그려 240이 됐다(지시 높이면 112).

### 4-3. 조인트 자기 점검
- `joint.sweep J_U8_PULL 0→511`(U8_CASSETTE ↔ U8_GUIDE·U1_HEAD·U6·U7·U1_PRESSER·CB5-12 ×3, 53표본): stopped_at null이다. 처음부터 맞닿은 쌍은 GUIDE↔CASSETTE(레일–블록 얹힘)다.
- 따라 움직인 부품은 U8_CASSETTE_BOX·CARRIER·BLOCK, 곧 유닛 전부다. 511에서 카세트 X 500~522, 캐리어 X 491~531이다.
- 스토퍼: 511에서 캐리어 +X 면 X 531이 끝 탭 −X 면 X 531에 닿는다. 블록은 Z 92.5 이상이라 끝 탭(Z ≤ 92)에 닿지 않는다.

### 4-4. 숨김·리지드·재질(E-09·E-11)
- 숨김 바디 0(`inspect_design` visible 전부 true).
- 리지드 누락 0이다(floating 0, 새 부품은 U8_GUIDE·U8_CASSETTE 컴포넌트 안, 볼트는 REF 리지드).
- 재질: HANGER·CARRIER는 SUS304(7.93, 새로 만듦, Steel 기본값 아님), CB5-12는 SCM435다. STEP대기_ 3바디는 기존 STEP대기_ 관례대로 Default다.
- matcheck: 가공품 BOM이 없어 검사 대상이 없다(실행 규칙 9, BOM은 문서부).

### 4-5. 볼트(안내서 '볼트 검사')
| 볼트 | 머리 | 물림 | 렌치 길 | 빈 구멍 |
|---|---|---|---|---|
| CB5-12 ×3 | Z 117~122, 플랜지 밑면 자리 | UPPER Z 125~134 = 9 ≥ 7.5(1.5d) | 머리 아래 Ø8.5×30 겹침 0 | 0(플랜지 Ø5.5 ×3·UPPER Ø4.2 ×3 모두 볼트, 앞 탭 Ø8은 플런저, 러그 Ø6은 핀) |

## 5. 임시 STEP(해석용, E-06 예외)
`tools/out/mech_DC-04/stepout/P_DC04_HANGER.step`(44,691 B), `P_DC04_CARRIER.step`(18,443 B). 해석 못 함 — 환경 없음(자료대기 D-16). 선정 손계산은 플랜지 SF 4.1(오조작 100 N), 블록 SF 185다.

## 6. 측정 표·다시 실행
- `ledger.py sigpatch --parts tools/out/mech_DC-04/changed_parts.json --bolts changed_bolts.json` → 바뀜 11, 전체 47. sigcheck reuse.
- 다시 실행: `tools/gen_v1_dc04.py` → `edit.json`(64명령, stage 3)을 v1.0.4에 CLI로 돌렸다(`replay.sc`). 저장본과 바디 47개의 부피·bbox가 같다(`replay.json` ok).
- 스크린샷: `tools/out/mech_DC-04/dc04_iso.png`(열어 보지 않음).

## 7. 설계검토서에 남길 제어 순서 제약(U-09)
- DC04-Q1: 포켓(X 500~975 · Y 60~700)에 사람이 있으면 전 축을 멈춘다. 사람은 MAINT에서만 들어간다. 운전 자세 J_U4_X 0·1250에서 서는 자리·팔 길이 테이블·매트와 겹친다(4-2).
- DC04-Q2: J_U8_PULL 0(플런저 걸림)을 확인하기 전에는 노루발 내림·봉제를 하지 않는다.
- DC04-Q3: J_U8_PULL ≠ 0이면 X·Y·회전·바늘을 움직이지 않는다.

## 8. 디테일(E-02, 기록만)
- DC-04-D1 레일·블록 M3 볼트: CB3 STEP이 없고, 블록 볼트 머리 ↔ 카세트 틈이 0이다.
- DC-04-D2 플런저 고정 너트(앞 탭 t3에 M8).
- DC-04-D3 포켓 둘레 바닥틀 살 20(N07 형재화).
- DC-04-D4 867 UPPER 밑면 M5 탭 자리(D-10 실물).
- DC-04-D5 테이프 길(캐리어 창 Z 70~85, 걸이 X −10~10 비움, N05·N06).
- DC-04-D6(새) 걸이 Ø5.5 구멍–굽힘 거리: 구멍 가장자리 ↔ 굽힘 끝 3.25(평면 기준, 2t = 6 미만, M-04). 구멍을 Y −86으로 옮기거나 플랜지를 20으로 늘린다.
- DC-04-D7(새) 캐리어 러그 높이(M03): 판금 부분 플랜지(릴리프 홈)로 Z 64~92로 줄일지 N05 클램프 자리와 함께 본다.

## 워크플로우 메모
- SolidCraft 판금 규칙 바인딩: `sheet.flange base`에 rule을 주지 않으면 그 뒤 `manage_rules active`로 바뀐 규칙을 따라 다시 계산된다. 이번에 걸이가 t4로 바뀌었다(부피 86,720 → 110,654). base에 `rule`을 꼭 준다.
- 판금 바디에 `solid.cylinder` cut은 거부된다. 평행 스케치 + `solid.extrude` cut만 된다.
- `edit.checkpoint`가 다음 MCP 호출에서 사라진다("no checkpoint", 측정·선정·모델링 모두). 원복은 undo로 했다.
- 움직이게 바꾼 유닛에 N01 때의 월드 고정 자르기가 남아 있었다(DC-05와 같은 종류). 구동 과제에서 고정 유닛을 움직이게 바꿀 때는 그 유닛 바디에 컴포넌트 이동 뒤 자르기가 있는지 먼저 본다.
