# 합치기부 — DC2-05·M05 합치기 (2026-11-04, 동시 과제 E-25, CLI)

요약
- 합친 과제 2개: **DC2-05**(먼 쪽 바퀴 밑 받침, 수정 1회차) → **M05**(U7 테이프 툴 카세트, 수정 2회차). 둘 다 실패 없음.
- 기준 `3D_Modeling/FSAP_v2.1.5.sc` → 새 버전 **`3D_Modeling/FSAP_v2.2.0.sc`**(1,585,862 B, md5 7b56780716fcaeee01d487ebe5575f7e). `tools/config.json`·`tools/machine.json` doc → v2.2.0.
- 바디 비교: 기준 3,645 → 합친 3,703(측정 이름 기준). 과제마다 바뀐 바디(DC2-05 +17 −27, M05 +69 −1 ~2)의 이름·부피·bbox·재질이 각 과제 cand와 모두 같고, 나머지 바디는 기준과 같다(불일치 0, 이름 겹침 0).
- 번호: 가운데 자리 +1(v2.1.5 → v2.2.0). 새 컴포넌트 CB5-12_DC205·U7_FIXED·U7_CST_STAGE·U7_CASSETTE 외, 없어진 컴포넌트 STEP대기_BALL_D25H_M04.
- 발자국 경계 간섭: **겹침 0**(DC2-05 바뀐 17바디 × M05 발자국 88바디, M05 바뀐 71바디 × DC2-05 발자국 83바디). 0.5 안은 P_DC205_STRIP ↔ TAPE_L·TAPE_G 0.0 맞닿음(허용, 작업 대상 얹힘)뿐.
- 측정 표: `ledger.py sigpatch` 바뀜 88·없어짐 30 → 3,702부품, sigcheck `reuse`. 체결 목록 bolts.json 406(없어진 CB5-12_M05_5 뺌). 판정 기억 112 → 173건.
- 앱: 켜져 있으나 열린 문서(FSAP_v2.1.2, path 없음)가 **dirty**라 open 하지 않았다(버리지 않음). 사용자가 직접 v2.2.0을 열어야 한다.
- 미완: 없음.

## 1. 근거 규칙 (원문)
- E-25(안내서 '편집 명령 기록·다시 실행'): "합치기: 기준 파일에 과제 기록을 차례로 `run --in <기준> --save <새 번호>`. 앞 과제가 만든 바디 이름이 겹치면 실패로 보고 그 과제를 뺀다."
- E-05·요구서 8-2: 형상이 바뀌면 `3D_Modeling/FSAP_v<주>.<부>.<수>.sc` 새 번호로 저장. 번호(WF-177): 이 저장에서 새로 생기거나 없어지는 컴포넌트가 있으면 "가운데 자리 +1·마지막 0".
- 안내서 '간섭': "많은 바디를 볼 때는 `inspect.clearance`를 먼저 쓴다 … `against`에 모델 전체를 주지 않는다."
- E-17(안내서 '서명'): "바뀐 바디만 재서 `ledger.py sigpatch --project … --parts <바뀐 것.json> --removed <이름,…>`로 고친다 … 볼트를 바꿨으면 … `--bolts <바뀐 체결.json>`도 준다."
- 안내서 '문서 확인': "앱에 연결돼 있고 열린 설계가 `dirty`(저장 안 된 변경)면 `open` 전에 멈추고 보고한다 … 그 변경은 사람이 한 것으로 보고 버리지 않는다."
- 실행 규칙 4: "새 버전 .sc를 저장했을 때만 FSAP 저장소에서 커밋하고 푸시한다."

## 2. 다시 실행
작업 폴더 `tools/out/merge_DC2-05-M05/`(run.sh, done.txt). 기준 = `tools/config.json` doc = FSAP_v2.1.5.sc(두 과제 base.sc와 md5 같음 99f82538…).

| 단계 | 명령 | 결과 | 시간 |
|---|---|---|---|
| 1 | `solidcraft-cli run DC2-05/edit.json --in FSAP_v2.1.5.sc --save step1.sc` (69단계) | rc 0, 10,339,277 B | 381 s |
| 2 | `solidcraft-cli run M05/edit.json --in step1.sc --save merged.sc` (329단계) | rc 0, 1,585,862 B | 179 s |
| 측정 | `eval meas.json`(REST step 0 + `inspect.measure`) — 기준·DC2-05 cand·M05 cand 병렬, 합친 결과 | rc 0 4건 | 104~211 s, 175 s |

비교(`compare.py` → `compare.json`, 부피 상대 1e-6·bbox 1e-3 mm·재질):

| 과제 | cand 바디 | 새로 생김 | 없어짐 | 바뀜 | 합친 결과와 | 판정 |
|---|---|---|---|---|---|---|
| DC2-05 | 3,635 | 17 (P_DC205_STRIP, P_DC205_DISC_1~8, CB5-12_DC205 ×8) | 27 (STEP대기_BALL_D25H_M04 occurrence) | 0 | 일치 | 합침 |
| M05 | 3,713 | 69 (U7 카세트·고정부·실린더·피팅·볼트 등) | 1 (U7_PATH_V) | 2 (STEP대기_867-392342_UPPER 탭 2, U7_BINDER 자리 옮김) | 일치 | 합침 |

- 합친 결과 3,703 = 기준 3,645 + 17 − 27 + 69 − 1. 기대 바디와 불일치 0, 남는 바디 0. 두 과제의 바뀐 이름 겹침 0.
- 서명 기준 경로 수는 3,702(측정의 같은 이름 바디 1개 차, 볼 occurrence 28개가 측정에서 27개 이름).
- 메모: v2.2.0 파일은 1.6 MB로 v2.1.5(9.8 MB)보다 작다. M05 cand(1.58 MB)도 같은 크기이고, 바디 수·부피·bbox가 모두 맞아 형상 손실은 없다(M05 기록의 `component.insert_design`·`break_link` 뒤 저장 방식 차이로 본다).

## 3. 저장·번호
- 저장: `merged.sc`를 `3D_Modeling/FSAP_v2.2.0.sc`로 복사(같은 md5). 이미 있는 버전 파일을 덮어쓰지 않음(v2.2.0 없음 확인). 문서 이름은 파일 이름에서 오며(`document.metadata`에 이름 칸 없음) FSAP_v2.2.0이다.
- 저장 상태: 마지막 단계 `motion.play REST step 0`, `browser.visibility joints false`(M05 기록 끝).
- 번호 근거(실제 그린 결과):
  - 새 컴포넌트: `CB5-12_DC205`(U2_TABLE 밑, ×8 occurrence) · `U7_FIXED`·`U7_CST_STAGE`·`U7_CASSETTE`·`U7_CUT`·`U7_TUCK`·`U7_FEED`·`U7_LATCH` · 구매품 컴포넌트 43(CJ2B10-15Z_M05_CUT/_TUCK(+ROD), CDJ2B16-150AZ-B_M05_FEED(+ROD), KQ2L06-M5A_M05_1~6, MBIS5-6.5-8_M05_1~10, CB5-16_M05_1~10, CB5-12_M05_1~4·6~12)
  - 없어진 컴포넌트: `STEP대기_BALL_D25H_M04`(28 occurrence)
  - 지시문은 M05의 components_added를 빈 목록(수정 2회차 변경만)으로 적었으나, M05 기록은 기준 v2.1.5에 카세트 전체를 새로 만든다. 어느 쪽이든 가운데 자리 +1이라 번호는 v2.2.0 그대로다.
- 다시 만들기: `tools/out/DC2-05/edit.json` → `tools/out/M05/edit.json`(부품 설계 `tools/out/M05/parts/*.sc`를 넣는다)을 v2.1.5에 차례로. 생성기 `tools/gen_dc2_05.py`·`tools/gen_v2_m05.py`.

## 4. 발자국 경계 간섭
`bnd.py`로 집합을 만들고 `bnd.json`(REST step 0 + `inspect.clearance` 2회, clearance 0.5, skip_within component)을 합친 파일에 CLI `run --results` 한 번(126 s).
- 발자국 = 지시 envelope(DC2-05 X −1830~−390·Y −30~30·Z −40~0, M05 X −15~520·Y −200~−25·Z 12.5~300)과 바뀐 바디 bbox의 합, 2 mm 여유.

| 바뀐 바디 | 상대 발자국 안 바디(against) | 검사 쌍 | 겹침 | 0.5 안 |
|---|---|---|---|---|
| DC2-05 17 | M05 발자국 88 | 2 (가지치기 1,494) | 0 | P_DC205_STRIP ↔ TAPE_L 0.0, ↔ TAPE_G 0.0 |
| M05 71 | DC2-05 발자국 83 | 2 (가지치기 5,891) | 0 | 없음 |

- 못 잰 쌍(unchecked) 0. 0.0 맞닿음 두 개는 매트 모형 테이프가 받침 띠 위에 얹힌 것(DC2-05 검도 1회차 허용 판정과 같음).
- boundary_ok = true.

## 5. 측정 표·판정 기억
- `ledger.py sigpatch --project tools --parts patch_parts.json --removed <30> --bolts patch_bolts.json`: "서명 고침: 바뀜 88, 없어짐 30, 전체 3702". doc = FSAP_v2.2.0.sc, doc_hash 87b3999189d75a68, bolts_stale 없음. `sigcheck` → `reuse`.
  - parts 88 = DC2-05 새 17 + M05 새 70 + `U3_HEAD/STEP대기_867-392342_UPPER`(M5 탭 2, 부피 −276.75 mm³ — ledger 허용 1e-4 안이라 diff가 못 잡지만 실제로 달라 넣음, M05 검도 메모).
  - removed 30 = STEP대기_BALL_D25H_M04 28 + U7_TAPE/U7_BINDER·U7_TAPE/U7_PATH_V(U7_CASSETTE 밑으로 옮김).
- bolts.json: 과제 부서가 이미 공유 목록에 넣어 둔 상태였다(407). 수정 2회차로 없어진 `CB5-12_M05_5`가 남아 있어 뺐다 → 406.
- 판정 기억 `out/judged.json` 112 → 173건(키 = 두 부품 서명 해시, 상대 위치 없음):
  - DC2-05: P_M03_WHEEL_TREAD ↔ P_DC205_STRIP(LIFT −10 받침 접촉), P_DC205_STRIP ↔ MAT_L·MAT_G·TAPE_L·TAPE_G(얹힘), CB5-12_DC205 ×8 ↔ P_DC205_STRIP(M-08 나사 물림), P_DC205_DISC_* ↔ P_M04_PANEL_W2, CB5-12_DC205 ↔ DISC(체결면).
  - M05: CB5-16_M05_10 ↔ STEP대기_S-M5-2_M05(나사 물림), CB5-16_M05_10 ↔ P_M05_CST_PLATE(좌면), P_M05_CUT_BLADE ↔ P_M05_CUT_FIX(전단 맞닿음), M05 볼트 ↔ 체결 목록의 탭·인서트 쪽 부품(M-08).
  - 남기지 않음: PV_BOLT_EXT16 탐침(모델에 없음), 피팅 6·로드 1의 포트 물림(쌍 이름이 보고서에 없음 — 다음 회귀에서 다시 올라오면 그때 판정).

## 6. 앱 표시
- `running` 응답 있음(앱 켜짐). `inspect_design`: 열린 문서 이름 FSAP_v2.1.2, path null, **dirty true**. 안내서 '문서 확인'대로 open 하지 않았다(열면 저장 안 된 변경이 버려진다). 사용자가 그 변경을 확인한 뒤 `3D_Modeling/FSAP_v2.2.0.sc`를 직접 열면 된다.

## 7. 시간(E-23)
- 약 21분(1,260 s). CLI 호출 9(측정 4·실행 2·문서 정보 2·경계 1), 파일 열기 9(CLI 호출마다), MCP 2(running·inspect_design, open 없음), 브라우저 0. 예상(합치기 M 60분) 안.

## 워크플로우 메모
- 지시문의 M05 components_added·changed_parts가 수정 2회차 변경(CB5-16_M05_10)만 담았다. 합치기 기준은 라운드 기준 버전이라 과제 전체 변경(카세트 전체)을 담아야 번호 판단·경계 검사 범위가 맞는다.
- 동시 과제 부서가 공유 `out/bolts.json`에 이미 썼다(E-25는 공유 서명을 과제 사본에만 고치라고 한다). 지난 회차 볼트(CB5-12_M05_5)가 남아 있었다.
- `ledger.diff`는 부피 상대 1e-4 안 차이를 바뀜으로 안 센다. 큰 바디에 탭 구멍 2개(−277 mm³ / 45,413,004 mm³)를 낸 변경이 서명에 안 잡힌다(M05 검도 메모와 같은 문제).
- 앱에 dirty 문서가 남아 있어 합치기부가 결과를 보여 주지 못했다.
