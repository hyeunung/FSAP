# REG-01 모델링: 동작 연구에 U7 조인트 키 넣기 + 못 본 범위 회귀 (FSAP_v2.6.3, 2026-11-06)

요약
- **바꾼 것:** 동작 연구 7개의 키만. CYCLE_L·CYCLE_S·CYCLE_G1·CYCLE_G2·MAINT_HEAD에 U7 조인트 6개(J_U7_CST_X·CST_Y·CUT·TUCK·FEED·LATCH, 5004~5009) 대기값 0 키, SEAM_U7에 CST_X·CST_Y·LATCH 0, MAINT_U7에 CUT·TUCK·FEED 0. 이제 8개 연구가 모두 같은 조인트 23개를 키로 잡는다. 형상·조인트 정의·행정·부품 변화 0, 새·지운 부품 0.
- **저장:** `3D_Modeling/FSAP_v2.6.3.sc`(4,420,677 B, 마지막 자리 +1, 컴포넌트 생김·없어짐 0). config.json·machine.json doc 갱신.
- **U7 상태 넘어옴 0:** 저장본 헤드리스 세션에서 MAINT_U7 13(카세트 빠짐 CST_X 25·CST_Y 250·LATCH 12) → CYCLE_L·S·G2 0, SEAM_U7 23·16 → CYCLE_G1 0·MAINT_HEAD 0으로 바꿔 봤다. 바꾼 뒤 U7 조인트 6개 모두 0, U7_BINDER 상자 X −11~40·Y −95~−9·Z 13~60(대기)과 같다. 회귀 묶음 61개 첫 단계에서도 모두 이 상자였다.
- **회귀(regrun, 상한 30분):** CYCLE_L 79~346과 348~379 중 14단계, 모두 282단계를 봤다. 기준선 밖 겹침 0, truncated 0, unmoved 0, 행정 막힘 0.
- **못 본 범위(남음):** CYCLE_L 0~78·347·350~352·355~357·360~362·365~367·370~372·375~377·380~716, CYCLE_G1 0~514, CYCLE_G2 0~630, CYCLE_S 0~450, STATES 0~25·31~34, MAINT_HEAD 0~1, MAINT_U7 0·3·4·7~9·12·13, POSE 0~182, F_STATES 0~34. 모두 2,098단계와 자세 점 218개다. 어림은 단계당 46 s에 8병렬로 13,520 s였다.
- **시간:** 과제 전체 약 62분. 앱 키 편집은 몇 초, 앱 확인 batch 하나가 약 15분 막혔다(5절). 세션 8개 열기 433~445 s, regrun 1,801 s.

## 근거 규칙
- E-03 "라운드 끝 = 전체 사이클 간섭 0". E-17 전체 회귀 실행 절차: "어림 합이 전체 상한을 넘으면 시작 전에 범위를 줄이고 '못 본 범위'를 먼저 정한다". 실행기는 `regrun.py run`이다.
- 요구서 6-4: 이송 X·Y 25 mm, 회전 5°, 좁은 곳 5 mm·1°, 상한 30분.
- E-15 "움직임은 기계 정의의 조인트로만". 연구 키를 바꿨으므로 machine.json `studies`에 `_keys_U7`과 `_history`를 적었다.
- E-05 번호: 새로 생기거나 없어진 컴포넌트가 없으므로 마지막 자리를 +1 했다(v2.6.2 → v2.6.3).
- M-08 기준선(machine.json baseline_overlaps). 아래 겹침은 모두 기준선 줄과 같다.

## 1. 문서 확인·원복
| 항목 | 내용 |
|---|---|
| 연결 | `running` 빈 목록 → MCP(앱 --control 27878)로 그렸다 |
| 열린 문서 | 앱에 `FSAP_v2.6.2`가 열려 있었다. dirty true, undo 0, redo 0, path null, 피처 1,998, 마지막 피처 9267 CB5-12_M08_PZ_KDM. 동작 연구 8개는 디스크 v2.6.2(`mech_regrun5/motion_list.json`)와 완전히 같았다. 앞 과제 DC2-08 모델링부 기록과 같은 상태다(dirty·undo 0·path null). 안내서 '문서 확인'의 "버리지 않는다"를 지켜 `open`(메모리 버림)을 하지 않고, 그 세션에서 `edit.checkpoint`(80)로 이어 그렸다. 지시문 (b)의 'merged' 문서는 열려 있지 않았다 |
| 동작 상태 초기화 | `motion.play REST 0` moved false(이미 대기) |
| 시험 1회 | `motion.study {study:560, keys:[1개]}` → keys 1(키 목록을 통째로 바꾼다는 것 확인) → undo. 그다음부터는 기존 키 전부와 새 키를 함께 보냈다 |

## 2. 그린 것(키만, MCP `motion.study {study, name, steps, keys}`)
| 연구 | id | steps | 키 수 | 넣은 키(값 0, 0단계·끝단계 두 점) |
|---|---|---|---|---|
| CYCLE_L | 117 | 716 | 17 → 23 | 5004~5009 |
| CYCLE_S | 116 | 450 | 17 → 23 | 5004~5009 |
| CYCLE_G1 | 118 | 514 | 17 → 23 | 5004~5009 |
| CYCLE_G2 | 119 | 630 | 17 → 23 | 5004~5009 |
| MAINT_HEAD | 560 | 1 | 17 → 23 | 5004~5009 |
| SEAM_U7 | 5010 | 32 | 20 → 23 | 5004 CST_X·5005 CST_Y·5009 LATCH |
| MAINT_U7 | 5011 | 13 | 20 → 23 | 5006 CUT·5007 TUCK·5008 FEED |
| REST | 115 | 1 | 23 | 그대로 |

- **함정(워크플로우 메모):** `motion.list`는 회전 조인트 값(47·50·84·99·114·270)을 라디안으로 준다. `motion.study`의 키 값은 도(°)를 받는다. 그래서 회전 조인트 값을 도로 바꿔 다시 보냈다(예: 270 0.15057 rad → 8.627°).
- **확인:** 편집 뒤 `motion.list`(`k/motion_list_app_after.json`)를 편집 전(`k/motion_list_app_before.json`)과 비교했다(`k/ver.py`). 8개 연구 모두 id·steps가 같다. 기존 키는 모든 점에서 차 0이고 빠진 키 0이다. 새 키는 모두 값 0이고, 모든 연구가 U7 6개를 키로 잡는다(`k/ver_after.txt`).
- 저장 전: `component.rename 0 → FSAP_v2.6.3`, `document.metadata.set description`('REG-01 mechanism: add U7 joint keys (0) …'), `motion.play REST 0`(moved false), `joint.drive J_U7_HGT 0`(moved false), `browser.visibility joints false`(규칙 19). 그다음 `save {path: FSAP_v2.6.3.sc}`.
- 저장 확인: `inspect_design` dirty false, 이름 FSAP_v2.6.3, 바디 551(전과 같음), 피처 1,998(같음), error 0, warning 15(전과 같은 15개). 숨김 9개는 매트·테이프·솔기 모형으로 의도한 것이다. 저장본을 CLI 세션 8개로 열어 회귀를 돌렸다(바디 이름·자세 정상, U7_BINDER 대기 상자가 같음).
- 서명: 바뀐 바디가 0이라 `ledger.py sigpatch --parts {}(빈 목록) --bolts [](빈 목록)`로 문서 해시만 찍었다 → `sigcheck` reuse(2,649).
- 부품·볼트·재질·리지드 그룹·조인트 정의 변화 0이다. 그래서 E-09·E-11 검사, 볼트 검사, 조인트 자기 점검, 임시 STEP은 대상이 없다(형상이 그대로).
- 사람용 그림: `tools/out/mech_REG-01/v2.6.3_rest_iso.png`(열어 보지 않음).

## 3. U7 상태 넘어옴 확인(완료 판정 1)
저장본 v2.6.3을 연 헤드리스 세션(39401)에서 `motion.play` 뒤 `inspect.measure U7_BINDER`를 쟀다(`reg/probe.py` → `reg/probe_u7.json`).

| 앞 단계 | 다음 단계 | 다음 단계의 U7 5004~5009 | U7_BINDER 상자 X·Y·Z |
|---|---|---|---|
| MAINT_U7 13 (25·250·…·12) | CYCLE_L 0 | 0·0·0·0·0·0 | −11~40 · −95~−9 · 13~60 (대기) |
| SEAM_U7 23 (FEED 150) | CYCLE_G1 0 | 전부 0 | 대기 |
| MAINT_U7 13 | CYCLE_S 0 | 전부 0 | 대기 |
| SEAM_U7 16 (CUT 15) | MAINT_HEAD 0 | 전부 0 | 대기 |
| MAINT_U7 13 | CYCLE_G2 0 | 전부 0 | 대기 |

MAINT_U7 13 자체의 상자는 X 14~65·Y −345~−259다(카세트 빠짐). mech_regression_4 3절에서 오염됐던 상자 X 14~65·Y −195~−109(CST_Y 100)는 이번에 한 번도 나오지 않았다. 회귀 묶음 61개의 첫 단계도 모두 대기 상자였다. **넘어옴 0.**

## 4. 회귀(완료 판정 2)
- 방법: mech_regrun5와 같다. `reg/worker.py`가 저장본을 붙잡은 헤드리스 세션 8개(39401~39408)를 쓴다. 검사 묶음은 `reg/chunk6.py`(chunk5 + 아래 두 가지)이고, 바디 나눔 `sets.json`(v2.6.2 대기 2,649바디; 형상이 같아 그대로)도 같다. 단계마다 `motion.play` → `inspect.clearance`(움직이는 115 + 그 연구 매트 3바디, 전체 대상과 둘레 87 대상) 순이다.
  - chunk5와 다른 점 ①: 연구가 U7을 모두 키로 잡으므로 U7을 0으로 모는 `joint.drive`를 뺐다(KEYED 비움).
  - 다른 점 ②: 묶음 첫 단계마다 U7_BINDER 상자를 쟀다.
- regrun: `--trial-steps 4 --trial-limit 360 --call-limit 480 --total-limit 1800 --parallel 8`. 시험 CYCLE_L 79~82는 ok였고 단계당 46.3 s였다(지난 회귀 실측 40~60 s에 맞춰 시험 수를 줄여 이번엔 시험 실패 0). 어림 13,520 s가 상한을 넘어 시작 전에 앞 311단계만 남겼다. 상한에 끊긴 뒤 본 단계는 282단계다.
- 명세 순서(사이클 못 본 범위 먼저): CYCLE_L 79~694 → CYCLE_G1 → CYCLE_G2 → CYCLE_S → CYCLE_L 0~78·695~716(의심 범위의 U7 바디) → STATES 0~23·31~32 → MAINT_HEAD.

| 범위 | 단계 | 새 겹침 | truncated | 비고 |
|---|---|---|---|---|
| CYCLE_L 79~346 | 268 | 0 | 0 | 두 번째~네 번째 변(먼 쪽 대차 X 800 고정, 회전 90·180°) |
| CYCLE_L 348~349·353~354·358~359·363~364·368~369·373~374·378~379 | 14 | 0 | 0 | 묶음 끝에서 상한에 끊긴 조각 |

- 걸린 겹침은 모두 기준선이다.
  - MAT_L ↔ TAPE_L: 282회, 기준선 "테이프 띠가 매트 가장자리 10 mm를 덮는 모형".
  - U3_NEEDLE_PIN ↔ MAT_L·TAPE_L: 각 186회, 기준선 "U3_NEEDLE_PIN(-30) 바늘 꽂음 의도 겹침".
- 못 잰 쌍(기존과 같음, 각 282회):
  - `I-020B_M02 ↔ CDM2C20-25Z_ROD`: 기준선 "로드 끝 나사 물림".
  - `KDM10P-06_M08 ↔ KDM10S-06_M08`: DC2-08 플러그가 소켓에 물린 핀·구멍 짝이다.
- unmoved 0, stopped_by_contact·loop 0, 죽은 세션 0, killed_calls 0.
- 원장: `ledger.py commit --passed "regress:v2.6.3:CYCLE_L:79-346,348-349,…,378-379(282단계)"`.

## 5. 앱 막힘·시간(E-23)
- 앱에서 연구 전환 확인 batch 11단계를 보냈다(MAINT_U7 13 포즈 3번 포함). MCP 호출이 os error 10060으로 끊겼다. `running`으로 보니 이 연결(87)의 engine.batch가 계속 돌고 있었다. 다시 보내지 않고 기다렸다. 약 15분 뒤 끝났지만 결과는 받지 못했다. 다른 연결이 막은 것이 아니라 내 요청이 길었던 것이라 앱을 다시 켜지 않았다(mcp_restarts 없음).
- 같은 확인은 저장본 헤드리스 세션에서 다시 했다(3절). MAINT_U7 포즈 한 번이 134~160 s로, 카세트를 빼고 넣는 자세 전환이 느리다.
- 시간: 과제 시작 → 끝 약 62분. CAD 호출은 MCP 약 22회와 CLI 세션 8개(regrun·probe)다. 설계 파일 열기는 앱 0회(열린 세션에서 이음), CLI 세션 8회(433~445 s, 동시)다.

## 6. 못 한 것
- **못 본 범위:** 아래 2,098단계와 자세 점 218개. 다음 회귀가 먼저 본다.

  | 범위 | 단계 | 이유 |
  |---|---|---|
  | CYCLE_L 380~716, CYCLE_L 347·350~352·355~357·360~362·365~367·370~372·375~377 | 359 | 전체 상한(어림 초과·상한에 끊김) |
  | CYCLE_G1 0~514, CYCLE_G2 0~630, CYCLE_S 0~450 | 1,598 | 어림 초과(시작 전) |
  | CYCLE_L 0~78·695~716 (지난 회귀 의심 범위의 U7 바디) | 101 | 어림 초과(시작 전). U7 말고 다른 바디는 v2.6.2 회귀에서 겹침 0 |
  | STATES 0~25·31~34, MAINT_HEAD 0~1, MAINT_U7 0·3·4·7~9·12·13 | 40 | 어림 초과(시작 전). MAINT_U7 1·2·5·6·10·11은 v2.6.2 회귀에서 봄 |
  | POSE 0~182, F_STATES 0~34 | 218점 | 자세 점당 135~265 s, 시작 전에 뺌 |

- 형상이 v2.6.2와 같다. v2.6.2 회귀가 본 범위(SEAM_U7 0~32, MAINT_U7 6단계, STATES 26~30)와 이번 282단계를 합친 것이 지금까지 유효하게 본 범위다.

## 7. 다시 실행 재료
- `tools/out/mech_REG-01/edit.json`: 명령 12개. motion.study 7개(회전 값은 도) + 이름·설명·REST·HGT 0·조인트 숨김.
- `edit_meta.json` {base v2.6.2, result v2.6.3}. 시험 1회(→ undo)와 edit.checkpoint는 기록에서 뺐다.
- 키 생성기는 `k/gen.py`다(motion.list → 키 + U7 0, 라디안 → 도).

## 워크플로우 메모
- **`motion.list` 키 값은 회전 조인트를 라디안으로 준다. `motion.study`는 도를 받는다.** 그대로 다시 보내면 회전 키가 57배 작아진다. 연구 키를 고치는 도구는 단위를 바꿔야 한다. 또 `motion.study {study}`는 키 목록을 통째로 바꾼다(합치지 않는다).
- **큰 키 목록(연구 하나 16~18 KB)을 MCP 인자로 손으로 옮겨 적어야 했다.** 파일에서 명령을 읽어 앱에 보내는 길이 없다. 매번 편집 뒤 `motion.list`를 비교해 옮겨 적은 오류를 잡았다(차 0).
- **앱에서 카세트 포즈(MAINT_U7 13)를 여러 번 바꾸는 batch는 15분이 걸렸다**(포즈 한 번 134~160 s). 연구 전환 확인 같은 자세 전환 시험은 CLI 세션에서 한다.
- regrun 시험 단계 수를 실측 단계당 시간(46 s)에서 4로 정하니 시험 실패 0이었다(지난 회귀 3번 실패). 8병렬로도 30분 상한에서 약 280단계라, 사이클 2,300단계를 다 보려면 회귀 4~5번 또는 단계당 시간 줄이기(검사 대상 축소)가 필요하다.
