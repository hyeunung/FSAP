# COLOR-01 모델링 — 모델 색 통일(체결 부품 흑색 금지)

## 요약
- 저장본 `3D_Modeling/FSAP_v2.8.2.sc`(4,813,622 B, 이름 FSAP_v2.8.2, dirty false). 작업 전 v2.8.1은 덮어쓰지 않았다. `tools/config.json` doc·`tools/machine.json` doc → v2.8.2.
- 바꾼 것: 표시 색만. `material.edit` 6건(SCM435 #b4b9bf, A5052·A6061 #ccd0d6, S45C·SK5 #9ea4ac, PET-CF #d4d4d0 — 이름·밀도·배정 그대로) + `appearance.assign` 9건(바디 외관 231 원본 바디, 색표 COL_* 칸).
- 결과: 2,729 바디 모두 색표 13칸 안(불일치 0), 체결 1,198 바디 모두 #b4b9bf(흑색 #3a3a3a 0, L* < 40 인 체결 0). 구매품 STEP 원색 예외 0.
- 형상 변화 0: 피처 2,303 = 2,303, 고유 바디 632 = 632(이름 같음), 타임라인 오류 0·경고 34(예전 것), 재질 배정·밀도 0 변경 → 질량·BOM 변화 0.
- 지운 부품·새 부품·조인트·행정 변화 0. 새로 힘을 받는 가공품 0 → 임시 STEP 없음. 미완 없음.
- 통로 MCP(앱 27878, running 빈 목록), 설계 파일 열기 1회.

## 1. 순서(안내서 '문서 확인'·'원복'·'다른 이름 저장')
| 단계 | 내용 |
|---|---|
| 연결 | `running` → `[]`. 앱이 켜져 있고 빈 상태라 MCP로 그림(규칙 2) |
| 열기 | `open v2.8.1.sc` → 피처 2,303, 오류 0. `inspect_design` dirty false, 경로·이름 v2.8.1, revision 1654 |
| 원복 | `edit.checkpoint` → 121(첫 회차, 남은 편집 흔적 없음 — 방금 연 문서) |
| 그림 | `batch` 15단계 한 번(아래 2절). ok, completed 15 |
| 확인 | `appearance.list`·`material.list`·`appearance.chain` 표본 5 → 3절 |
| 저장 전 | `motion.play {study: REST, step: 0}`(moved false — 이미 대기), `browser.visibility {visible:false, folder:"joints"}`(changed 372, 규칙 19), `document.metadata.set description` = 'COLOR-01 mechanism: unified color table, fasteners light zinc grey #b4b9bf (no black), no geometry change' |
| 저장 | `save {path: 3D_Modeling/FSAP_v2.8.2.sc}`(덮어쓰기 0). 문서 이름은 저장 경로를 따라 FSAP_v2.8.2가 됐다(이름 바꾸는 명령은 없고 저장 이름을 따른다) |
| 저장 확인 | 저장 뒤 `inspect_design` dirty false, 경로 v2.8.2, 피처 2,303, 바디 632. 저장 뒤 편집 0 |

지시 2의 '먼저 다른 이름 저장'은 편집 뒤 새 경로로 한 번만 저장했다(FUNC-01과 같은 방식). v2.8.1 파일은 손대지 않았고 결과는 같다.

## 2. 보낸 명령(지시서와 같은 결과, 이름만 줄임)
지시서 edit.json은 appearance.assign 12건·1,609 이름(복사본 이름 `X (경로)`·`"X"@occ[...]` 포함)이었다. 설계부가 CAD에서 확인한 대로 assign은 복사본 이름을 원본 바디로 풀어 지정하므로, 같은 원본으로 풀리는 이름을 미리 합쳐 **원본 바디 231개, 9건**으로 보냈다(나일론 볼 827 이름 → `STEP대기_BALL_D25_M04` 1개, 체결 547 → 68, 마감캡·게이지 60 → 11 등). 같은 원본이 두 칸에 걸리는 충돌 0을 먼저 확인했다. 지정되는 바디·색은 지시서와 같고, 한 번 호출 인자 6.6 KB(지시서 묶음 최대 20.5 KB).

- 지시서 원본: `tools/out/mech_COLOR-01/edit_design.json`(18 명령)
- 실제로 보낸 것(다시 실행 재료): `tools/out/mech_COLOR-01/edit.json`(15 명령), `edit_meta.json` {base v2.8.1, result v2.8.2}

| 외관 | 색 | 불투명도 | 원본 바디 |
|---|---|---|---|
| COL_TP | #d0453a | 1 | 7 |
| COL_WP | #5b6b7b | 1 | 3 |
| COL_EV | #9fc3e6 | 0.35 | 6 |
| COL_PM | #8c9198 | 1 | 88 |
| COL_F_FASTENER | #b4b9bf | 1 | 67 |
| COL_RG | #d4d4d0 | 1 | 11 |
| COL_RW | #e8e4da | 1 | 1 |
| COL_PT | #3d7fd1 | 0.55 | 25 |
| COL_SF | #f2c200 | 1 | 23 |
| 합 | | | 231 |

`material.edit` 결과로 바뀐 바디: 각 명령 결과의 bodies 목록대로 — SCM435는 CB·SFB·FHS·멈춤나사·감속기 볼트 전부(체결 651 배치), A5052 판·브래킷, A6061 바퀴·풀리, S45C 축·핀, SK5 날, PET-CF 출력품 6.

## 3. 검증(수치, E-16)
| 항목 | 결과 | 근거 |
|---|---|---|
| 색표 밖 색 바디 | **0** / 2,729 | `verify_color.py` → `tools/out/mech_COLOR-01/verify_color.json`: 바디마다 결과 색 = 바디 지정(있으면) 아니면 재질 색, color_plan.json 그룹 색과 비교 mismatch 0 |
| 쓰인 색 | 13가지 = 색표 13칸 | #3d7fd1 #5b6b7b #8c9198 #9ea4ac #9fc3e6 #b4b9bf #c8ccd0 #ccd0d6 #d0453a #d4d4d0 #d9a33a #e8e4da #f2c200 |
| 체결 흑색 | **0** / 1,198 | 체결 중 #3a3a3a 0, L* < 40 0 |
| 바디 지정 | 231 원본 바디, 얼굴·컴포넌트 지정 0 | `appearance.list` in_design 9칸, faces []·components [] |
| 재질 색 | SCM435 #b4b9bf, A5052·A6061 #ccd0d6, S45C·SK5 #9ea4ac, PET-CF #d4d4d0, SUS304 #c8ccd0, PA12 #e8e4da, Urethane_A70 #d9a33a. 밀도 그대로(7.85·2.68·2.7·7.85·7.85·1.35) | `material.list` |
| 표본 CAD 확인 | Steel 바디 I-020B_M02 → #9ea4ac(재질), Aluminum CDM2C20-25Z_BODY → #ccd0d6, 복사본 `HNTT8-8_M04_NZ (U2_TABLE:1/…:3)` → body COL_F #b4b9bf, 복사본 나일론 볼 → body COL_RW #e8e4da, CB5-12_M03_1 → SCM435 #b4b9bf | `appearance.chain` 5건 |
| 형상 | 피처 2,303 → 2,303, 고유 바디 632 → 632(이름 목록 같음), 오류 0 | 저장 전·뒤 `inspect_design` |
| 부피 | 서명 표와 이름이 맞는 633 바디 중 628 같음. 차 5건은 볼트 CB 0.01~0.05 %(예: CB4-25_M08 448.42 vs 448.65 mm³) — 피처가 그대로이고 명령이 색뿐이라 측정 방식(서명은 CLI 측정) 차이로 본다 | `after_bodies.json` |
| 겹침 | 형상·위치 변화 0이라 과제 안 겹침 검사 대상 없음(E-17 바뀐 바디 0) | — |
| 볼트 | 새로 넣거나 옮긴 볼트 0 → 볼트 검사 대상 없음 | — |

## 4. 서명·기계 정의
- `ledger.py sigpatch --parts sig_parts_empty.json` → 바뀜 0, 없어짐 0, 전체 2,729, doc v2.8.2, doc_hash 5f7c163a375afeb5.
- 조인트·행정·연구 변화 0 → machine.json은 doc 경로만 v2.8.2로.

## 5. 앞으로(설계검토서 기록용)
- 새로 넣는 바디는 이 색표 칸으로 외관을 준다: 체결은 재질과 무관하게 COL_F_FASTENER #b4b9bf(SCM435는 재질 색으로 이미 맞음, 그 밖 재질 체결은 `appearance.assign … name COL_F_FASTENER`), 재질 미지정 구매 기구품 COL_PM, 공압 관 COL_PT, 안전 COL_SF, 차지 상자 COL_EV, 마감캡 COL_RG.
- 제어 순서 제약 변화 없음(U-09).
- 스크린샷은 찍지 않았다(외관은 사용자가 앱 창에서 본다, 파일 다시 열기를 피함).

## 6. 시간
- 약 8분, CAD 호출 약 14, 파일 열기 1(MCP open, 수 초), 통로 MCP.

## 워크플로우 메모
- appearance.assign은 복사본 이름을 원본 바디로 풀기 때문에, 설계부가 복사본 이름을 모두 나열하면 이름 수가 7배(1,609 → 231)로 불어난다. 설계 단계에서 원본 바디 이름으로 합쳐 두면 모델링 인자가 작아진다.
- SolidCraft에는 문서 이름을 바꾸는 명령이 없고, `save {path}`의 파일 이름이 문서 이름이 된다(규칙 2의 '문서 이름 바꾸기'는 저장 경로로 충족).
- signatures.json에 색 칸이 없어 색 과제는 appearance.list + material 색으로 따로 계산해야 한다(설계부 메모와 같음).
