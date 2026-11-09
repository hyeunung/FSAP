# F01-C1 모델링 — 작업 대상 모형 땀–가장자리 거리 e 0 → 6.5

## 요약
- 저장본 `3D_Modeling/FSAP_v2.8.3.sc`(4,815,490 B, 이름 FSAP_v2.8.3, 저장 뒤 dirty false). v2.8.2는 덮어쓰지 않았다. `tools/config.json` doc·`tools/machine.json` doc → v2.8.3.
- 바꾼 것: 조인트 원점 3개(`J_WP_L/S/G_X`의 a 원점, U1_FRAME 쪽)를 +6.5 X로 → 사슬 전체(WP_k_X → WP_k_Y → WP_MAT_k + WP_TAPE_k)가 세계 +6.5 X. 연구 CYCLE_L·S·G1·G2의 `J_WP_k_X·Y` 키(피벗 단계만 바뀜, 최대 6.5). SEAM_U7는 바뀔 키 0.
- 결과: REST에서 MAT_L·MAT_S·MAT_G 가장자리 X max **6.5**(L·S·G 모두), TAPE 7.5, SEAM −3.5~8.5. MAT_L 무게중심 X −743.5, ROT 10°에서도 (−743.5, −300) 그대로.
- 과제 범위 검사(19자세, MAT·TAPE·SEAM ↔ 22바디 `inspect.clearance`): **새 겹침 0**, 겹침은 바늘 기준선뿐(MAT 20.1·TAPE 22.1·SEAM 1.01 mm³). X max가 측정 표(6.5·9.19·8.69·174.6·319·156.5·919·492.5)와 0.01 안에서 같다. unchecked 0.
- 연구 키: 8개 연구 × 24키 전부를 의도값과 비교해 어긋남 0(1e-3 mm 안). 단계 수 그대로(450·716·514·630·32).
- 새·지운 부품 0, 컴포넌트 증감 0, 새 조인트 0, 행정·한계·축 그대로. 형상(바디 부피) 변화 0. 새로 힘을 받는 가공품 0 → 임시 STEP 없음.
- 저장 전 대기 포즈(REST 0), 조인트 글리프 숨김(changed 372)·**스케치 숨김(changed 208)** — 실행 규칙 19, 사용자 2026-11-09 "스케치 쓸데없이 왜켜놔 숨겨".
- 미완 없음. 통로 MCP(앱 27878), 설계 파일 열기 MCP 1회 + 저장 확인 CLI 1회 + 스냅샷 CLI 1회.

## 1. 순서
| 단계 | 내용 |
|---|---|
| 연결 | `running` → `[]`(앱 켜짐, 막힘 없음). MCP로 그림(실행 규칙 2) |
| 열기 | `open v2.8.2.sc` → 피처 2,303, 오류 0. `inspect_design` dirty false, 경고 34(예전 것) |
| 원복 | `edit.checkpoint` → 138(첫 회차, 방금 연 문서라 남은 편집 흔적 없음) |
| 그림 1 | `batch` joint.edit 3단계(0.44 s) — conflicts 0, errors 0 |
| 확인 | 바디 9개 `measure` bbox(2절) |
| 그림 2 | `motion.study` 4번(CYCLE_S·L·G1·G2, 24키 통째). 처음 CYCLE_S에 X·Y 두 키만 보냈더니 **연구 키가 두 개로 바뀌었다**(motion.study의 keys는 통째로 갈아끼움) → 24키 통째로 다시 보내 복구, 나머지 셋은 처음부터 통째. `motion.list`로 8개 연구 전부 대조(3절) |
| 검사 | 19자세 `motion.play`(quiet) + `inspect.measure` + `inspect.clearance`(batch 2번, 1.2 s·2.4 s), ROT 10° 확인, `joint.list` floating 0·conflicts 0 |
| 저장 전 | `motion.play {REST, 0}`, `browser.visibility {visible:false, folder:"joints"}`(372), `{…folder:"sketches"}`(208), `document.metadata.set description` = 'F01-C1 mechanism: work-piece models moved +6.5 X (stitch-edge distance e 6.5), WP joint origins and pivot study keys updated' |
| 저장 | `save {path: 3D_Modeling/FSAP_v2.8.3.sc}`. 문서 이름은 저장 경로를 따라 FSAP_v2.8.3(이름 바꾸는 명령 없음, 앞 보고서들과 같음) |
| 저장 확인 | MCP `inspect_design` dirty false, 경로·이름 v2.8.3, 피처 2,303, 바디 632. CLI `eval`(저장본, 320 s)로 바디 9개 bbox·부피와 바꾸지 않은 30바디 bbox 비교 → 어긋남 0. 저장 뒤 편집 0 |
| 서명 | `ledger.py sigpatch --parts out/mech_F01-C1/sig_parts.json` → 바뀜 9, 없어짐 0, 전체 2,729 |

지시 2의 '먼저 다른 이름 저장'은 편집 뒤 새 경로로 한 번만 저장했다(앞 과제 COLOR-01·FUNC-01과 같은 방식, 앞 파일 손대지 않음).

## 2. 좌표(세계, REST, mm) — 지시 2·4
| 바디 | 옛 bbox X | 새 bbox X(저장본 CLI 실측) | 지시 | Y·Z |
|---|---|---|---|---|
| MAT_L | −1500 ~ 0 | −1493.5 ~ 6.5 | −1493.5 ~ 6.5 | −1050~450, 0~10 그대로 |
| TAPE_L | −1501 ~ 1 | −1494.5 ~ 7.5 | −1494.5 ~ 7.5 | 그대로 |
| SEAM_L | −10 ~ 2 | −3.5 ~ 8.5 | −3.5 ~ 8.5 | −330~−300, 11~12 |
| MAT_S / TAPE_S / SEAM_S | −300~0 / −301~1 / −10~2 | −293.5~6.5 / −294.5~7.5 / −3.5~8.5 | 같음 | 그대로 |
| MAT_G / TAPE_G / SEAM_G | −1200~0 / −1201~1 / −10~2 | −1193.5~6.5 / −1194.5~7.5 / −3.5~8.5 | 같음 | 그대로 |
부피 그대로(MAT_L 22,500,000, MAT_G 14,363,172.0, TAPE_G 610,978.3, SEAM 360). `TAPE_G_IN`이라는 바디는 없다(지시서 예시 이름, 측정 표에도 없음 — TAPE_G 하나가 홈 안까지 감싼 바디).
무게중심: MAT_L (−743.5, −300, 5), MAT_S (−143.5, −300, 5), MAT_G (−594.85, −299.23, 5)(홈 때문에 비대칭, 옛 −601.35 + 6.5). ROT 10°: MAT_L 중심 (−743.5, −300, 5) 그대로.

조인트(세계 프레임, 축·flip·한계 그대로):
| 조인트 | 옛 원점 | 새 원점(세계) | CAD에서 바꾼 것 |
|---|---|---|---|
| J_WP_L_X·Y·ROT | (−750, −300, 0) | (−743.5, −300, 0) | J_WP_L_X a 원점(U1_FRAME:1 점 스냅)만 (−743.5, −300, 0) |
| J_WP_S_X·Y·ROT | (−150, −300, 0) | (−143.5, −300, 0) | J_WP_S_X a 원점만 |
| J_WP_G_X·Y·ROT | (−600, −300, 0) | (−593.5, −300, 0) | J_WP_G_X a 원점만 |

**지시와 다르게 한 것(같은 결과):** 지시 2·3은 '바디를 +6.5 이동하고 9조인트의 a·b 원점을 고친다'였다. 사슬 첫 조인트의 고정 쪽(a) 원점만 +6.5 옮기면 그 아래 occurrence(WP_k_X·WP_k_Y·WP_MAT_k·WP_TAPE_k)가 통째로 +6.5 가서, 바디 bbox·회전 중심·모든 세계 프레임이 지시 값과 같아진다(위 표·`joint.inspect` 세계 frame origin −743.5 확인). 바디 이동 명령 9번과 원점 수정 18번 대신 명령 3번이라 바디 형상 이력·부품 좌표를 건드리지 않는다. 차이: Y·ROT 조인트와 X 조인트 b 쪽의 **부품 좌표 snap 값은 옛 −750 등 그대로**(occurrence가 +6.5 놓임). 기계 정의 `machine.json`의 origin은 세계 값(−743.5 …)으로 적고 `_note`에 이 사실을 남겼다.

## 3. 연구 키 — 지시 5
| 연구 | 단계 | 바꾼 키 | 옛 점 → 새 점(직선 구간 압축) | 의도값과 차 | 다른 키 |
|---|---|---|---|---|---|
| CYCLE_L | 716 | J_WP_L_X·Y | 366·375 → 366·383 | 0 | 22키 그대로 |
| CYCLE_S | 450 | J_WP_S_X·Y | 366·367 → 366·390 | 0 | 22키 그대로 |
| CYCLE_G1 | 514 | J_WP_G_X·Y | 362·372 → 364·376 | 0 | 22키 그대로 |
| CYCLE_G2 | 630 | J_WP_G_X·Y | 366·375 → 366·384 | 0 | 22키 그대로 |
| SEAM_U7 | 32 | 없음(newkeys 변화 0단계) | — | 0 | 그대로 |
| REST·MAINT_HEAD·MAINT_U7 | — | 없음 | — | 0 | 그대로 |
- 새 키 = `design/newkeys.json` 전 단계 값을 일직선 점만 빼고(오차 ≤ 5.6e-5 mm) 보냈다(`studyc_*.json`). 회전 키는 원래 도(unit deg) 그대로.
- 대조: `motion_list_after.json` vs `motion_list_before.json`+newkeys, 각 연구 전 단계 보간값 비교 → `verify_keys.json` bad 0(8개 연구 × 24키).
- 옛 키와 바뀐 단계 수: X 356(G1 178)·Y 376~391 — 설계안 '피벗 380·381·190·381 단계, 최대 6.5'와 같은 범위(설계안은 X·Y 합집합 수).

## 4. 과제 범위 동작 확인 — 지시 6, E-22
19자세(pick_poses.json), 각 자세 `motion.play`(quiet) → MAT·TAPE·SEAM_k ↔ 22바디(`against_short.json`) `inspect.clearance` 2 mm. 결과 원본 `tools/out/mech_F01-C1/m_v0.json`·`m_v12.json`.

| 자세 | 매트 X max(실측) | 측정 표 | 겹침(mm³) | 가까운 것(mm) |
|---|---|---|---|---|
| CYCLE_L 51 | 6.5 | 6.5 | 0 | LOWER·원판 0, 바퀴 0.001, 이음매↔노루발 0, 테이프↔노루발 1.0, 테이프↔슈 1.5 |
| CYCLE_L 82 | 6.5(Y min −6.5) | 6.5 | 바늘 20.1·22.11 | 바퀴 0.042·0.044 |
| CYCLE_L 127 | 9.19 | 9.19 | 바늘 20.1·22.11 | 바퀴 0.014·0.033 |
| CYCLE_L 300 | 8.69 | 8.69 | 바늘 20.1·22.1 | 바퀴 0·0.017 |
| CYCLE_L 667 | 6.5 | 6.5 | 0 | 이음매↔바인더 1.0, 테이프↔슈 1.5 |
| CYCLE_S 17 | 6.5 | 6.5 | 0 | 노루발·바퀴만 |
| CYCLE_S 22 | 6.5 | 6.5 | 바늘 20.1·22.11 | 바퀴 0.028 |
| CYCLE_S 67 | 9.19 | 9.19 | 바늘 20.1·22.11 | 바퀴 0.032 |
| CYCLE_S 433 | 6.5 | 6.5 | 0 | 이음매↔바인더 1.0 |
| CYCLE_G1 60 | 6.5 | 6.5 | 0 | 이음매↔바인더 1.0, 테이프↔슈 1.5 |
| CYCLE_G1 120 | 174.56 | 174.6 | 바늘 20.1·22.11 | 바퀴 0.008·0.018 |
| CYCLE_G1 200 | 319.0 | 319 | 0 | 바퀴 0.012·0.02, 노루발 1.0 |
| CYCLE_G1 300 | 156.5 | 156.5 | 바늘 20.1·22.11 | 바퀴 0.01·0.026 |
| CYCLE_G1 400 | 919.0 | 919 | 0 | 바퀴 0.023, 노루발 1.0 |
| CYCLE_G1 480 | 492.51 | 492.5 | 바늘 20.1·22.11 | 바퀴 0.006 |
| SEAM_U7 3 | 6.5 | 6.5 | 바늘 20.09·22.1 | 이음매↔슈 0.5, 테이프↔슈 1.5 |
| SEAM_U7 10 | 6.5 | 6.5 | 바늘 20.1·22.11·SEAM 1.01 | 이음매↔바인더 1.0 |
| SEAM_U7 17 | 6.5 | 6.5 | 바늘 20.1·22.11·SEAM 1.01 | 이음매↔바인더 1.0, 테이프↔슈 1.5 |
| SEAM_U7 23 | 6.5 | 6.5 | 0 | LOWER·원판 0만 |
- 겹침은 모두 기준선 `U3_NEEDLE ↔ WP_*`(M-08 원문 '의도된 겹침은 기준선으로 남긴다'). 새 겹침 0, unchecked 0.
- 측정부가 조인트를 몰아 미리 잰 값과 실제 모델 값이 같다(옛 키에 +6.5 얹은 미리 재기 = 새 원점 + 새 키).
- 전 사이클 `motion.interference`는 돌리지 않았다(지시 6-1, 회귀부 몫).

## 5. 저장 전 검사 — 지시 6
| 항목 | 결과 |
|---|---|
| 그린 부품 bbox·부피 | 2절, 부피 변화 0 |
| 새 겹침 | 0(4절) |
| 숨김 목록(E-11) | 숨긴 바디 9 = MAT·TAPE·SEAM_L/S/G(v2.8.2부터 숨겨 둔 작업 대상 모형, 이번에 바꾸지 않음 — 표시만 꺼진 것이라 검사에는 들어갔다: 4절 clearance가 9바디를 재었음). 숨긴 occurrence 0. 조인트 글리프·스케치는 규칙 19로 숨김 |
| 리지드 그룹·떠 있는 것 | `joint.list` floating 0, conflicts 0, 조인트 372 |
| 재질(E-09) | 바뀐 바디 없음(모형 9바디 Default 그대로). 가공품 BOM 대상 변화 없음 |
| 조인트 자기 점검(E-15) | 바꾼 것은 원점뿐(축·한계 ±3000·−360~720 그대로). 모형 조인트(model_only)라 스토퍼 없음. 19자세·ROT 10°로 사슬 전체(X → Y → MAT·TAPE)가 같이 움직임 확인. `joint.sweep`은 돌리지 않음(행정 변화 없음) |
| 볼트 | 바꾼 체결 0 → 볼트 검사 대상 없음 |
| 강도·FEA(E-18) | 모형 조인트뿐, 하중 경로 변화 없음 → 대상 없음 |

## 6. 고친 파일 — 지시 7·8
- `tools/machine.json`: doc v2.8.3, `J_WP_{L,S,G}_{X,Y,ROT}` origin (−743.5/−143.5/−593.5, −300, 0)·`_note`(e 6.5, CAD 원점 처리), states 10값(피벗 자세: 큰 매트 45°·90°, 작은 매트 45°, 홈 입구 회전 시작·45°·두 번째 45°, G2 45° — 새 키 값으로), baseline `U3_NEEDLE ↔ WP_*` 수치 'MAT 20.1·TAPE 22.1·SEAM 1.01 mm³(e 6.5)', `_history` 한 줄.
- `docs/waiting-list.md` D-78: 땀–가장자리 거리 0 → 6.5(D-144), 쓰는 곳에 F01-C1·gen_v2_prep E_EDGE·newkeys.py.
- `tools/gen_v2_prep.py`: `E_EDGE = 6.5` — `start_c`(→ `park_c`) +e, 직선·모서리 경로 안쪽 e, 홈 벽 안쪽 e·바닥 원호 r 12.5+6.5, 이음매 겹침 줄 안쪽 e. 지금 설계의 연구는 뒤 과제(FUNC-01 등)가 고친 키라, e 6.5 키의 정본은 `tools/out/mech_F01-C1/design/newkeys.py`(단계 번호 유지)라고 머리에 적었다. 생성기는 `tools/machine.json`도 다시 쓰므로 이번에는 돌리지 않았다(파싱 확인만).
- `CHANGELOG.md` v2.8.3 한 줄. `tools/config.json` doc.
- 서명 `tools/out/signatures.json`: 9바디 bbox 갱신(sigpatch, doc v2.8.3).

## 7. 제어 제약(U-09, 설계검토서용 기록)
- 가장자리 센서 목표값·노루발 밑 표시 = **바늘 +X 6.5**. 슈 위 센서 E32-D36P1 감지면 X −17.5~17.5 안에 새 가장자리 X 6.5가 들어 있다(설계안 미완 기록 그대로) — 시야 판정·목표값 확정은 제어 단계, 요구서 7절.

## 8. 시간·통로(E-23)
- 걸린 시간 약 21분(1,175 s 시점 기록 + 보고). CAD 호출: MCP 약 27(running·open·inspect 3·joint 3·measure 3·motion.study 5·motion.list 2·검사 batch 2·저장 전 batch·save·revision 2·joint.list·list_commands 3), CLI 2(저장 확인 eval 320 s, 스냅샷). 브라우저 0.
- 가장 긴 열기: CLI 저장본 eval 약 320 s(열기 포함) — 모델 무게 상한 240 s를 넘을 수 있다(안내서 '모델 무게'). MCP open은 몇 초.
- 앱 막힘 0, 재시작 0. 한 번 measure batch 응답 중 'Connection closed'가 났으나 `running` 빈 목록, 편집은 그대로 남아 있었다(앱 재시작 아님).
- 스냅샷 `tools/out/mech_F01-C1/snap_v2.8.3_iso.png`(사람용, 열어 보지 않음).

## 9. 다시 실행 재료(E-25)
- `tools/out/mech_F01-C1/edit.json`: 최종 결과를 만든 11명령(joint.edit 3, motion.study 4 통째, REST, 숨김 2, metadata). 처음 CYCLE_S에 보낸 X·Y만의 motion.study는 탐색으로 보고 뺐다(다음 호출이 통째로 덮음).
- `edit_meta.json`: base v2.8.2, result v2.8.3.

## 워크플로우 메모
- `motion.study {study, keys}`로 기존 연구를 고치면 keys가 **통째로 갈아끼워진다**(준 키만 남음). 몇 키만 바꿀 때도 `motion.list`로 전체 키를 받아 다 넣어야 한다. 지시서 5)는 이미 '통째로'라고 적었으나, 안내서·스킬에 함정으로 적어 두면 좋다.
- 연구 키가 큰(연구당 14~15 KB) motion.study는 MCP 인자로 직접 보내야 해서 호출 인자가 커진다. 파일을 읽어 실행하는 MCP 명령이 없다.
- `inspect.measure`에 `bodies` 목록을 줘도 CLI eval은 모든 바디(2,760)를 잰다(MCP는 batch 안 `inspect.measure {bodies}`로 그 바디만 줬음).
