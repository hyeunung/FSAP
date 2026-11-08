# 전체 회귀 14회차: FSAP_v2.6.8 (2026-11-09, 엔진 v3.9.3) — 부분(전체 상한 30분)

요약
- 대상: `3D_Modeling/FSAP_v2.6.8.sc`(md5 6bb56a07…, 2,666바디). 읽기만 했고 저장 0, 앱(MCP) 사용 0.
- **본 범위(이번 361점, 기준선 밖 새 겹침 0, truncated 0, unmoved·stopped 0):**
  - POSE 전체 검사 0~7·12~123·125·128~129·134 (127점)
  - F_STATES U6_SENSOR·U6_SHOE·U7#0~#4/8 12~34, U7#5~#7/8 11~34 (233점) — 지난 못 본 범위 다 봄
  - F_STATES U5_WHEEL_F 0, CYCLE_L 23~25
- **못 본 범위(다음 회귀가 먼저 본다):** POSE 124·126·127·130~133·135~180 / CYCLE_L 26~716, CYCLE_S 0~450, CYCLE_G1 0~514, CYCLE_G2 0~630, SEAM_U7 0~32, MAINT_HEAD 0~1, MAINT_U7 0~13 / F_STATES U3_HEAD·U4_WHEEL_N·U5_WHEEL_F 1~34.
- 어림 14,536 s(연구 55 s/단계, 자세 155 s/점, fslow 170 s/점, fchg 5 s/점) > 상한 1,800 s → 시작 전에 앞 363단계만 돌림(regrun). 실제 1,800.8 s(상한에서 자세 8점 끊김). 부서 전체 약 46분.
- 저장 전후 비교(v2.6.7 → v2.6.8): 바꾸지 않은 바디의 위치·부피·재질 변화 0. 바디 차이는 STEPSWAP r4 목록과 같다(새 30, 없어짐 24).
- 원장: sigcheck reuse("문서·해시가 같다", 2,666). `ledger.py commit --date 2026-11-09`로 본 범위 3항목만 넣음(통과 항목 53).
- 동작 문제 0, 디테일 0. STEPSWAP의 바뀐 유닛 U8은 고정 유닛이라 조인트가 없고, 새 30바디는 모델링부 검사(30 ↔ 42 겹침 0)와 이번 near 집합(재분류) 안에서 본 범위 겹침 0.

## 근거 규칙
- E-03: "어느 단계든 합격의 첫 조건은 작업 대상을 넣은 전 구간 동작과 간섭 0", 라운드 끝 = 전체 사이클 간섭 0.
- E-17 전체 회귀 실행 절차(WF-153·WF-178): "어림 합이 상한을 넘으면 시작 전에 범위를 줄이고 못 본 범위를 먼저 정한다 … 묶음 순서는 지난 회귀의 못 본 범위 → 이번 라운드에 바뀐 유닛 → 나머지".
- E-04: "한 번의 도구 호출은 8분 안", "오래 걸리는 계산(전체 사이클 간섭)은 늘 CLI".
- 요구서 6-4: 간격(이송 25 mm, 회전 5°, 좁은 곳 5 mm·1°), 전체 회귀 상한 30분. 연구 단계는 이 간격으로 만든 그대로(CYCLE_L 716, CYCLE_S 450, CYCLE_G1 514, CYCLE_G2 630, SEAM_U7 32, MAINT_HEAD 1, MAINT_U7 13).
- M-08 기준선: MAT↔TAPE↔SEAM(같은 매트), U3_NEEDLE_PIN↔MAT·TAPE·SEAM(바늘 꽂음).
- 결정로그 C-34·REG02-R01: J_U6_HGT를 지우고 높이 조정은 J_U7_HGT 하나. 두 값이 어긋난 자세(옛 POSE 8·9)는 회귀 자세 정의에서 뺐다(181점 정의, `poses.json` 그대로). 이번 회귀도 이 정의를 쓴다 — 사용자 2026-11-08 "가장 이상적인 방향으로 진행해"에 따른 C-34를 그대로 따른다.

## 1. 방법
- 폴더 `tools/out/mech_regrun/reg16/`. 회귀 13(reg15)의 묶음 정의를 그대로 쓰고(`mkspec16.py` → `spec16.json`, 345묶음 2,853단계), 순서는 지난 못 본 범위 그대로: U6·U7 빠른 검사 → POSE → 연구 → U3·U4·U5.
- 헤드리스 세션 12개(`sup.py 12 40061 base.sc`, 파일 한 번씩 열기, 302~370 s). base.sc = v2.6.8 복사(md5 같음).
- 바디 목록: v2.6.8 REST `inspect.measure`(`dump14.py` → `bodies_v268.json`, 2,666바디, 63 s). 나눔(`classify14.py` → `sets.json`)을 v2.6.8로 다시 만듦: 움직이는 325(mov_red 112, 체결·관 213), near_all 138(v2.6.7 132 → 새 IR1000·관 등이 들어감), near_red 87.
- regrun 세 번:
  - runsB: 시험 상한 120 s에서 자세·연구·fslow 시험이 timeout → trial_error.
  - runsC: 시험 상한 300 s에서 자세·fslow 시험 timeout → trial_error.
  - runs: `--trial-limit 470 --trial-poses 1 --trial-steps 2 --parallel 12 --total-limit 1800`. 시험 모두 ok → 어림 14,536 s로 앞 363단계만 계획, 355묶음 ok·8묶음 cut(전체 상한).
- 집계 `an16.py` → `an16.json`(runs·runsB·runsC 합침).

## 2. 결과
| 범위 | 점 | 기준선 밖 겹침 | truncated | unmoved·stopped |
|---|---|---|---|---|
| POSE 0~7·12~123·125·128~129·134 | 127 | 0 | 0 | 0 |
| F_STATES U6_SENSOR·U6_SHOE·U7#0~#4/8 12~34 | 161 | 0 | 0 | 0 |
| F_STATES U7#5~#7/8 11~34 | 72 | 0 | 0 | 0 |
| F_STATES U5_WHEEL_F 0 | 1 | 0 | 0 | 0 |
| CYCLE_L 23~25 | 3 | 0 | 0 | 0 |

- 기준선 겹침: MAT_L↔TAPE_L 등(M-08).
- unchecked(기존 의도 쌍): I-020B_M02 ↔ CDM2C20-25Z_ROD 132·_NUT 8(클레비스 핀 물림), P_M07_BEAM ↔ CB5-16_M03_1~8·CB5-12_M03_1·2(나사 물림) 각 1.
- 점당 시간: POSE 평균 78 s(최대 294), F_STATES U6·U7 17~50 s(최대 222), U5 168 s, CYCLE_L 48 s.
- 빠져야 할 것(조각) 없음 — 이 기계는 떨어지는 조각이 없다(요구서 0-3, 테이프 자투리는 U7 연구 범위).

## 3. 못 본 범위(coverage.unseen)
- 어림 초과(시작 전): CYCLE_G1 0~514, CYCLE_G2 0~630, CYCLE_L 25~716(25는 본 범위), CYCLE_S 0~450, SEAM_U7 0~32, MAINT_HEAD 0~1, MAINT_U7 0~13, POSE 136~180, F_STATES U3_HEAD·U4_WHEEL_N·U5_WHEEL_F 1~34.
- 전체 상한에서 끊김: POSE 124·126·127·130·131·132·133·135.
- 참고: 이 범위의 v2.6.5 누계 결과는 겹침 0이고, v2.6.5 → v2.6.7 바뀐 19바디는 회귀 12에서 전 구간 겹침 0(결정로그 RGSEE-C1). v2.6.7 → v2.6.8은 고정 유닛 U8만 바뀌어 움직이는 바디의 형상·조인트 변화 0.

## 4. 저장 전후 비교(WF-044)
- `compare16.py` → `compare16.json`: v2.6.7 REST(`bodies_v267.json`, 2,660) ↔ v2.6.8 REST(`bodies_v268.json`, 2,666).
- 새 30: IR1000-01BG_M08_BODY·GAUGE·SETNUT·BRKT ×3, CB4-12_M08_REG ×6, KQ2L08-01AS_M08R_PX/NX ×3, TU0805_M08T_REG_IN/OUT_1~3.
- 없어진 24: STEP대기_IR1000-01BG_M08_F/N/S(+_BRKT), KQ2L08-01AS_M08_PX/NX ×3, TU0805_M08S_REG_IN/OUT_1~3, CB5-12_M08_PY :1~:6.
- 같은 이름 바디 중 bbox 차이 1건 `CB5-12_M08_PY` 1,641.6 mm: 이름 밀림이다. v2.6.7의 :1~:6(레귤레이터 브래킷 볼트)을 지워 옛 :7(X 310.75, Y −1529, Z −314.25)이 이름 없는 첫 이름을 받았다 — v2.6.8 `CB5-12_M08_PY` bbox가 옛 :7과 같고, :8~:10은 그대로. 실제 이동 0.
- 부피·재질 변화 0. 결론: 바꾸지 않은 부품의 위치·재질 변화 0.

## 5. 원장·원복
- sigcheck: reuse("문서·해시가 같다", 2,666).
- commit(본 범위만): `regress:v2.6.8:POSE 전체 검사(회귀 14) 0-7·12-123·125·128-129·134`, `regress:v2.6.8:F_STATES(빠른 검사, 회귀 14): U6_SENSOR·U6_SHOE·U7#0~#4/8 12-34, U7#5~#7/8 11-34, U5 0`, `regress:v2.6.8:CYCLE_L 전체 검사(회귀 14) 23-25`. 통과 항목 53.
- 원복: 앱 문서(solidcraft.exe 17112)는 열지도 바꾸지도 않았다. 헤드리스 세션은 점마다 `motion.play`(REST 또는 상태 단계)로 시작했다. 끝에 감독 `stop`으로 이 회귀의 세션 12개만 닫음(03:08:19 stopped). 다른 부서의 solidcraft-cli(17444)는 건드리지 않음.

## 6. 파일
- 명세·실행: `tools/out/mech_regrun/reg16/spec16.json`, `runs/regrun.json`, `runsB/`, `runsC/`
- 집계: `an16.json`. 바디·나눔: `bodies_v268.json`, `sets.json`. 비교: `compare16.json`

## 워크플로우 메모
- regrun 시험 상한 기본 120 s가 자세 한 점(이 모델 155 s)·fslow 한 점(170 s)보다 짧아 trial_error가 두 번 났다(약 7분 손실). 시험 상한을 호출 상한(470 s)으로 두거나, 시험 점 수를 1로 줄이는 것을 기본으로 하면 된다(WF-178 확장 후보).
- 이 모델의 남은 전체 회귀 어림은 14,536 s(12병렬 벽시계)로 30분 상한의 약 8배다. 회귀마다 30분씩 앞에서부터 보면 연구 전체 검사(약 2,350단계)는 7~8회차 뒤에야 한 바퀴 돈다. 점당 시간의 대부분은 자세 구동(`joint.drive J_U7_HGT`·카세트 조인트, 회귀 12 메모)이다. 연구 전체 검사를 바뀐 바디 쌍(D_ 묶음)으로 줄이는 규칙이나 상한을 모델 크기에 맞추는 기준이 필요하다.
