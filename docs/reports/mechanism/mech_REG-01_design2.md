# REG-01 기구설계 수정 2회차 — 판정을 실행 가능한 도구로 (FSAP_v2.6.4, 2026-11-06)

요약
- **같은 안 REG-01-D1.** 형상·조인트·연구·구매품 변경 0, CAD 저장 0, 이번 회차 CAD 열기 0. 범위·회차(A1~A4)·세션 나누기는 `mech_REG-01_design.md`·`design1.md` 그대로.
- **고친 곳:** 1회차의 '규칙(글)'을 회귀 담당이 그대로 돌리는 **도구 `tools/out/mech_REG-01/r4/`**로 바꿨다 — chunk7.py(J_U6_SHIFT 0 몰기·POSE 이어 몰기 실제 반영), judge.py(완료 판정 3항목 + 남은 못 본 범위 자동 계산).
- **judge.py 빈 시험:** r3 결과(an_runsA·B)를 넣으면 bad 0·truncated 0·unmoved 0·stopped 0, 남은 못 본 범위 1,424단계(CYCLE_S 86·G1 509·G2 627·POSE 167·F_STATES 35) = 측정 보고서의 1,222 + 167 + 35와 정확히 같다.
- **이 파일 이름의 2026-11-04 판(v2.5.8 묶음 계획)은 덮어썼다.** 옛 내용은 결정로그 '구동 REG-01 설계안' 수정 2(2026-11-04) 행에 남아 있다.
- **미완:** 겹침·truncated·unmoved 실제 값은 회귀 실행 결과다. 이 부서는 회귀를 돌리지 않는다(E-17 "전체 사이클은 라운드 끝 전체 회귀가 한 번"). judge.json `pass_all`이 회귀 담당의 합불이다.

## 1. 안 되는 곳과 고친 것

| 안 되는 곳 | 1회차 | 2회차(이번) |
|---|---|---|
| 못 본 범위 기준선 밖 겹침 0 | 규칙: an.py `bad` 0 | `r4/judge.py`가 an_*.json을 모아 `bad` 수와 목록(≤50)을 judge.json에. 기준선은 an.py `base_ok`(MAT/TAPE/SEAM_L·S·G끼리, U3_NEEDLE_PIN↔MAT·TAPE) = machine.json baseline_overlaps(M-08) |
| truncated 0 | 규칙: 끊긴 단계 유닛 묶음별 다시 재기, 남으면 못 본 범위 | judge.py가 **truncated 단계를 본 것에서 뺀다**(파일마다). 다시 잰 an 파일에 깨끗한 결과가 있으면 그때 본 것. 그래서 truncated는 자동으로 `unseen`에 들어가고 겹침 0으로 셈되지 않는다 |
| 행정 막힘·unmoved 0 | 규칙: unmoved·stopped 0 | judge.py `unmoved`·`stopped` 수. chunk7은 joint.drive 결과 `unmoved`·`stopped_by_contact`·`stopped_by_loop`를 단계마다 모은다(r3 그대로) |
| (도구) J_U6_SHIFT 0 몰기 | 지시만 | r4/chunk7.py 84·86줄 튜플 → `('J_U6_HGT','J_U7_HGT','J_U6_SHIFT')` 반영(2곳), py_compile 통과 |
| (도구) POSE 이어 몰기 | 지시만 | 묶음 첫 점만 `motion.play REST 0`, 다음 점은 앞 점에만 있던 조인트를 0으로 되돌린 뒤 이 점 값으로 joint.drive. 자세 병목(REST 왕복, joint.drive 264.6 s 실측)을 줄임 |

합격 = judge.json `pass_all` true(bad·unmoved·stopped 0 그리고 unseen 0). `pass_seen_range` true이고 unseen이 남으면(30분 상한에 끊김) 남은 단계를 다음 못 본 범위로 기록한다(완료 판정 "상한에 끊긴 범위는 다음 못 본 범위로 기록").

## 2. 회귀 담당 실행 순서
1. 도구는 `tools/out/mech_REG-01/r4/`(worker.py·ask.py·sets.json·states.json·poses.json은 r3 복사, 바뀐 것 chunk7.py·judge.py). 대상 저장본 v2.6.4. sets.json 검사 목록에 교체 바디 CB5-6_M08_PY_LC2F는 U8 고정 바디라 들지 않는다(측정 보고서, 옛 이름도 안 들었음) — 고칠 것 없음.
2. 연구 세션 8개: A1~A4(약 300단계씩, 8병렬 5.9 s/단계), 자세 세션 2개(POSE 167·F_STATES 35, 시험 20점으로 어림). regrun 시험 20단계 → 어림 → 1,800 s 상한, 호출 ≤ 480 s, 커널 패닉 즉시 멈춤(E-17, 요구서 6-4).
3. 회차마다 `python -B r4/an.py <runs폴더>` → an_<runs>.json. truncated 단계는 FAST_BY_UNIT 묶음별 다시 재서 별도 runs 폴더 → an.
4. 끝에 `python -B r4/judge.py an_*.json` → judge.json. 보고서 표에 bad·truncated·unmoved·stopped·unseen_steps.
5. 각 세션 `motion.play REST 0`, 저장 없음.

## 3. 규칙 자기 점검
- E-02: 개념·형상 그대로, concept_conflict 없음.
- E-08 원복: CAD를 열지 않음(앱 세션·저장본 손대지 않음). 1회차 CLI 확인값(CB5-6_M08_PY_LC2F 2개, STEP대기_CB5-6 0, J_U6_SHIFT −60~0) 그대로.
- E-17: 검사 범위 = 측정 보고서 measure_remaining_plan.json 그대로(judge.py가 같은 파일을 읽어 범위를 정함 — 손으로 다시 적지 않음).
- E-18: 형상·하중 경로 변화 없음 → 손계산·FEA 없음. M-06·U-14·U-12·M-04·U-10·U-07/E-10·U-01·M-01·M-02: 새 부품·볼트 없음.
- 실행 규칙 1: 엔진 폴더 손대지 않음(도구는 프로젝트 tools/out 안).

## 워크플로우 메모
- 검증 과제(등급 S)의 기구설계부 완료 판정이 회귀 결과 항목이라 수정 회차로 met을 만들 수 없다(2회째 반복). 설계부 판정을 '판정 도구가 돌고 범위가 측정과 같은가'로, 결과 항목은 회귀 담당으로 나누면 회차를 아낀다(1회차 메모와 같은 문제, 반복 2).
