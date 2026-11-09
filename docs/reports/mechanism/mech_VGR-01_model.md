# VGR-01 모델링 — 좁은 V자 홈 시험 매트 WP_V·CYCLE_V (모델링부, 2026-11-10)

## 요약
- 저장: `3D_Modeling/FSAP_v2.8.4.sc`(기준 v2.8.3, 번호 마지막 자리 +1). 통로 MCP(앱 --control 27878, 막힘 0).
- 새로 만든 것: 작업 대상 모형 WP_V(MAT_V·TAPE_V·SEAM_V), 컴포넌트 WP_V_X·WP_V_Y·WP_MAT_V·WP_TAPE_V, 모형 조인트 J_WP_V_X·Y·ROT, 연구 CYCLE_V 486단계. 기계 부품·볼트·BOM 변경 0.
- 다른 연구 8개(REST·CYCLE_S·L·G1·G2·MAINT_HEAD·SEAM_U7·MAINT_U7)에 J_WP_V_* 0 키(옛 키 변화 0, motion.list 대조).
- U5 키: 꼭짓점 ROT −35에서 매트 정지 한 단계(321) 동안 들고, 입구2 ROT −30 정지 한 단계(440) 동안 내림. J_U5_X 1360, J_U4_PRESS V 전 구간 0.
- 과제 범위 검사 30자세: 기준선 밖 새 겹침 0(바늘 MAT 20.1·TAPE 22.1 mm³뿐), U5↔TAPE_V 0, 꼭짓점 −35에서 U5↔MAT_V 0.021, 바늘–홈 벽 최소 5.7.
- C-37 회전력(손계산 그대로): U4 혼자 꼭짓점 8.0 s(SF 1.056·1.053), 입구2 9.0 s(1.028), U4+U5 최저 1.227.
- machine.json(조인트 3·유닛 WP_V·연구 CYCLE_V·states 4 + 전체 J_WP_V_* 0·baseline L·S·G·V·_timing), 설계검토서 v2.8.4(ⓐ~ⓔ), 결정로그 VGR-01-M1~M4.
- 미완: 없음(CYCLE_V 전 단계 motion.interference는 검도 몫 — 지시서 5).

## 1. 작업 순서
| 단계 | 한 일 |
|---|---|
| 연결 | `running` 빈 목록 → `open v2.8.3.sc`(피처 2,303, 오류 0, 몇 초). `document.revision` 1(방금 연 문서, 편집 흔적 없음) → `edit.checkpoint` 17 → `motion.play REST 0` |
| 그림 1 | batch 20단계 5.3 s: 상자·다각형 스케치 cut·원 cut·combine(`tools/out/mech_VGR-01/model/stage_1_bodies.json`) |
| 그림 2 | batch: 컴포넌트 4·move_bodies·rigid_group·joint.create 3(`stage_2_joints.json`) + 시험 구동 X 10·Y 20·ROT 90 → 0 |
| 연구 | `motion.study` CYCLE_V 새로(27키) + 다른 8개 통째(27키씩) |
| 검사 | 30자세 `motion.play`(quiet) + `inspect.measure` + `inspect.clearance` 2 mm(batch 4번), `joint.list` |
| 저장 전 | WP_V 바디 숨김, `browser.visibility` joints·sketches 숨김, `document.metadata.set description`, `motion.play REST 0` |
| 저장 | `save {path: 3D_Modeling/FSAP_v2.8.4.sc}`(4.83 MB). 문서 이름은 경로를 따라 FSAP_v2.8.4 |
| 저장 뒤 | 임시 STEP export(편집 아님), CLI 저장 확인·스냅샷(4절) |

생성기: `tools/gen_v2_vgr01.py` → `tools/out/mech_VGR-01/model/stage_*.json`·`study_CYCLE_V.json`·`study_others.json`·`cycle_v.json`. 다시 실행 기록 `tools/out/mech_VGR-01/edit.json`(44명령)·`edit_meta.json`.

## 2. 만든 부품·좌표 (세계, REST)
| 바디(컴포넌트) | 만든 법 | bbox mm | 부피 mm³ |
|---|---|---|---|
| MAT_V (WP_MAT_V) | 상자 −1193.5~6.5 × −900~300 × 0~10 − 다각형 [(−136.29, −598.068), (16.5, −557.128), (16.5, −642.872), (−136.29, −601.932)] Z −1~11 − 원 R2 중심 (−135.773, −600) | −1193.5~6.5, −900~300, 0~10 | 14,339,810.5 (손계산 14,339,812) |
| TAPE_V (WP_TAPE_V) | 상자 ±601 − 다각형(1 안쪽)·원 R1 − TAPE_V_IN(±590 − 다각형(10 바깥)·원 R12), combine cut | −1194.5~7.5, −901~301, 0~11 | 602,877.6 |
| SEAM_V (WP_TAPE_V) | 상자 −3.5~8.5 × −330~−300 × 11~12 (SEAM_G와 같음) | 같음 | 360 |

매트 좌표(중심 기준)로는 설계안 1회차 5절 좌표 그대로다(대기 중심 (−593.5, −300)을 더함). 바닥 x 455.727, 입구 반폭 40.19. 재질 Default(밀도 1.29, MAT·TAPE_L/S/G와 같음), 숨김(L·S·G와 같음). 원 cut 3개에 'Boolean retry: tool displacement 0.0034 mm' 경고가 붙었다 — 원이 다각형 꼭짓점에 접해서 생긴 것이고 부피 손계산과 0.0001 % 안에서 같다.

| 조인트 | 종류 | a → b | 원점·축 | 한계 |
|---|---|---|---|---|
| J_WP_V_X | slider | U1_FRAME:1 → WP_V_X:1 | (−593.5, −300, 0) +X, flip | ±3000 |
| J_WP_V_Y | slider | WP_V_X:1 → WP_V_Y:1 | 같음 +Y | ±3000 |
| J_WP_V_ROT | revolute | WP_V_Y:1 → WP_MAT_V:1 | 같음 +Z | −360~720 |

리지드 WP_MAT_V:1 + WP_TAPE_V:1. 시험 구동: X 10·Y 20에서 SEAM_V 무게중심 (12.5, −295) = 식 값, ROT 90에서 (−568.5, 316) = 식 값(반시계 +, CYCLE 생성식과 같은 방향).

## 3. 연구 CYCLE_V (486단계, 6-4 간격)
| 단계 | 구간 | ROT° | 노루발/바늘 | U5 |
|---|---|---|---|---|
| 0~12 | 대기 → 노루발 표시(Y +300) | 0 | 20/0 | LIFT 30 |
| 13~16 | 노루발 내림·센서 슈 0, U4 내림(15→16) | 0 | 0/0 | — |
| 17~71 | 먼 쪽 대차 X 0 → 1360(d₂ 440, 25 mm) | 0 | | |
| 72~73 | U5 내림 LIFT −10·FLOAT 10 | 0 | | 내림 |
| 74~100 | 접근 봉제 254.8(끝 50은 5 mm) | 0 | | |
| 101~179 | 입구1 피벗 P1 (593.5, −254.82) 0→75 | 0→75 | 20/−30 | 내림 |
| 180~208 | 위 벽 142.8(5 mm) | 75 | 0/0 | |
| 209~363 | 꼭짓점 호 r 8.5 중심 (457.727, −300) 75→−75. **321 = ROT −35 정지·U5 들기** | 75→−75 | 20/−30 | −35까지 내림 |
| 364~392 | 아래 벽 142.8 | −75 | 0/0 | 들림 |
| 393~472 | 입구2 피벗 P2 (593.5, −345.18) −75→0. **440 = ROT −30 정지·U5 내림** | −75→0 | 20/−30 | −30부터 내림 |
| 473~482 | 떠나기 봉제 50 | 0 | 0/0 | |
| 483~486 | 노루발 들기 → 바퀴 들기·센서 슈 −60 | 0 | 20 | LIFT 30 |

- 매트 좌표는 `gen_v2_prep.py`와 같은 식(c = −R(θ)p)이다. 키 압축 뒤 바늘 경로 오차는 최대 0.00007 mm(지시 0.02 안). 30자세 MAT_V bbox는 식 값과 0.000 mm 차이다.
- 바퀴 회전 키는 내린 동안 바퀴 밑 매트 점 Y 변위 / r 60이다(U4 합 585.1°, U5 합 479.7°).
- **지시와 다른 점 2가지.** (1) 단계 수 486 — 설계안은 "약 410"이라 했다. 내림·대차 55단계와 접근 봉제 27단계를 넣으면 6-4 간격으로 486이 된다. (2) U5 승강을 회전 중 한 단계(CYCLE_G1 방식)가 아니라 같은 ROT에서 멈춘 한 단계로 넣었다 — _timing의 "ROT −35 정지·U5 들기"와 맞추고, 들리는 동안 매트가 돌지 않게 했다. 각은 지시 그대로 −35·−30이다. 생성기 far_off는 쓰지 않았다. 지시 각을 직접 넣었으므로 덮어쓴 값도 없다.
- J_U4_PRESS: 0~15 8.627, 16~485 0, 486 8.627(REST 한계 8.626으로 잘림, 다른 연구와 같음).

## 4. 검증 수치
### 4-1. 과제 범위 간섭(E-17, 지시서 5와 같은 범위)
30자세(0·12·16·73·87·100·102·140·177·194·208·230·266·300·319·320·321·322·340·361·378·392·410·439·440·441·455·470·482·486)에서 `inspect.clearance {bodies: MAT_V·TAPE_V·SEAM_V, against 23, clearance 2, skip_within component}`. against = `tools/out/mech_VGR-01/model/against_short.json`(바늘·노루발·U4 바퀴·팔·원판·U5 바퀴·앞판·옆판·센서·867 아랫유닛·바인더·카세트·슈·P_DC205_STRIP). 결과 원본 `chk0~3.json`.

| 항목 | 값 |
|---|---|
| 새 겹침(기준선 밖) | **0** (30자세 모두, truncated false, unchecked 0) |
| 바늘 꽂음(baseline) | 바늘 내림 19자세 MAT_V 20.096~20.098·TAPE_V 22.106~22.108 mm³(F01-C1 기준선과 같음) |
| U5 ↔ TAPE_V | 0자세(가장 가까운 자세에서도 near 목록 없음) |
| U5 ↔ MAT_V (꼭짓점 −34·−35 / 입구2 −30 내림 직후) | 0.005 / 0.021 / 0.021 (맞닿음, 부피 0) |
| U5 들린 뒤(−36, 322) | U5 근처 2 mm 안 0 |
| U4 ↔ MAT_V | 0.000~0.040 (맞닿음), U4 ↔ TAPE_V 0 |
| 노루발 ↔ SEAM_V / TAPE_V | 0.0(baseline 맞닿음) / 1.0 |
| 슈 ↔ TAPE_V | 1.5 |

- 208(위 벽 끝)에서 clearance가 노루발 ↔ TAPE_V 0.0을 냈다(점 Z 12.0). 같은 자세 measure로 TAPE_V Z max 11.000, 노루발 Z min 12.000이고 `inspect.interference` 0이다. 실제 틈은 1.0이고, 0.0은 도구 표시 문제로 본다(워크플로우 메모).
- 홈 바닥·꼭짓점 회전 중 반대 벽 틈(완료 판정): 바늘 내림 전 단계에서 바늘 표면 ↔ 홈 빈 곳 경계 최소 **5.7**(MAT_V)·6.7(TAPE_V 안쪽 면)이다(`gapcheck.json`). 측정부의 보수 셈 4.7(e − 테이프 1 − 반경 0.8)보다 크고, 모두 > 0이다. 바늘 겹침 부피가 모든 바늘 내림 자세에서 같아 바늘이 늘 재료 안에 있다.

### 4-2. 조인트·숨김·리지드·재질
| 항목 | 값 |
|---|---|
| joint.list | 조인트 376(372 + 새 4), floating 0, conflicts 0 |
| 조인트 자기 점검 | 새 조인트는 model_only 모형 축. 시험 구동 3축(X 10·Y 20·ROT 90 → 0) 식과 같음. 매트 3장이 대기 자리에 겹쳐 있어 행정 끝 sweep은 의미가 없다(baseline WP_*_L·S·G·V). 기계 조인트는 바꾸지 않았다 |
| 숨김(E-11) | 숨긴 바디 12 = MAT·TAPE·SEAM_L/S/G/V(작업 대상 모형, 표시만 끔. 검사에는 들어감 — clearance가 잼). 숨긴 occurrence 0. 조인트 376·스케치 214(새 3 포함) 숨김(규칙 19) |
| 재질(E-09) | 새 바디는 작업 대상 모형이라 BOM 밖, Default(기존 WP와 같음). 가공품 변경 0. matcheck 대상 없음 |
| 연구 대조 | motion.list 전후: 9연구 키 27개씩, 보낸 값과 차 0, 옛 24키 변화 0(`motion_list_before/after.json`) |

### 4-3. 회전력(C-37, 완료 판정 강도 항목)
손계산 `tools/out/mech_VGR-01/design/c37design2.json`을 다시 셈해 같음을 확인했다. 구름 0.02, μ 0.4, U4 40 N, d₁ 0.1 m → U4 가능 1.60 N·m.

| 구간 | 바퀴 | θ° | t s | 필요 N·m | SF |
|---|---|---|---|---|---|
| 꼭짓점 75→−25 피벗 ×4 | U4+U5 | 25 | 1.2 | 6.691 | 1.291 |
| 꼭짓점 −25→−35 | U4+U5 | 10 | 1.0 | 4.330 | 1.995 |
| 꼭짓점 −35→−50 | U4만 | 15 | 3.5 | 1.516 (1.123 + 4.594×0.0855) | **1.056** |
| 꼭짓점 −50→−75 | U4만 | 25 | 4.5 | 1.519 | **1.053** |
| 입구2 −75→−30 | U4만 | 45 | 9.0 | 1.556 | **1.028** |
| 입구2 −30→0 | U4+U5 | 30 | 1.5 | 7.039 | 1.227 |

U4 혼자 회전 시간: 꼭짓점 40° 8.0 s, 입구2 45° 9.0 s(둘 다 ≥ 6 s). 모델의 U5 승강 각(−35·−30)이 이 표의 경계와 같다.

### 4-4. 저장 확인
- MCP 저장 뒤 편집 없음. 저장본에 대고 `solidcraft-cli run savecheck.json --results`(측정·CYCLE_V 320 재생·REST): 결과 `tools/out/mech_VGR-01/model/savecheck_out.json`(아래 9절에 결과를 적는다).
- 서명: `ledger.py sigpatch --parts tools/out/mech_VGR-01/model/sig_parts.json` → 바뀜 3(MAT_V·TAPE_V·SEAM_V 새로), 없어짐 0, 전체 2,732.

### 4-5. 임시 STEP
새로 힘을 받는 가공품은 없다. 완료 판정 강도 항목(U4 회전력)의 힘 경로 부품 P_M02_WHEEL·P_M02_WHEEL_TREAD(형상 변경 없음)를 참고로 냈다: `tools/out/mech_VGR-01/stepout/P_M02_WHEEL_U4_drive.step`. FEA 환경이 없다(해석 못 함 — 환경 없음, 자료대기 D-16). 강도는 위 손계산이다.

## 5. machine.json·config.json
- config doc → `../3D_Modeling/FSAP_v2.8.4.sc`, machine doc 같음.
- joints J_WP_V_X·Y·ROT(model_only, 원점 (−593.5, −300, 0)), units WP_V, studies CYCLE_V(단계 구간·d₂ 440·_keys_M06·_u5_far_off 메모), 다른 연구에 `_keys_WP_V` 메모.
- `_timing`(동작에는 안 씀): CYCLE_V 입구1 2.5, 꼭짓점 U4+U5 [1.2, 1.2, 1.2, 1.2, 1.0], ROT −35 정지·U5 들기, U4 [3.5, 4.5], 입구2 U4 9.0, ROT −30 정지·U5 내림, U4+U5 1.5. CYCLE_G1 바닥(1회차 그대로). 한계 α 0.1039·0.0459·0.0902 rad/s², ω 11.1 °/s.
- states: 전체 30개에 J_WP_V_* 0, 새 4개(CYCLE_V 148 입구1 45°·320 꼭짓점 −35·322 −36·440 입구2 −30).
- baseline_overlaps 'WP_*_L·S·G' → 'WP_*_L·S·G·V'(WP_V는 WP_G와 같은 대기 자리).
- 갱신 스크립트 `tools/out/mech_VGR-01/model/upd_machine.py`.

## 6. 문서
- 결정로그 '구동 VGR-01 모델링 결과 (2026-11-10)' VGR-01-M1~M4. 테이프 처리 방법(미터 접기·25° 피벗·V홈 카세트 테이프 D-153)은 이미 '구동 VGR-01 설계안 (2026-11-10)'에 결과 결정 줄로 있다.
- 요구서 VGR-01 ③은 설계부가 C-37로 고쳐 적었다(이번에 바꾸지 않음). 상태 칸을 '모델 반영(v2.8.4) — 검도 대기'로.
- 자료대기 D-152 쓰는 곳에 v2.8.4 단계 번호.
- 설계검토서 `docs/review/FSAP_v2.8.4_review.md`(제어 순서 제약 ⓐ~ⓔ). BOM `docs/bom/FSAP_v2.8.4_*.csv`(v2.8.3 복사, 변경 0). CHANGELOG.

## 7. 규칙 점검
- E-05: 새 컴포넌트 WP_V_X·WP_V_Y·WP_MAT_V·WP_TAPE_V가 생겼다. 다만 지시서가 "새로 생기거나 없어지는 컴포넌트(유닛·부품 묶음)가 없다 → v2.8.4"로 정했고, 이 넷은 기계 유닛·부품 묶음이 아닌 작업 대상 모형(BOM 밖)이라 지시대로 마지막 자리 +1로 두었다. version_bump last, 근거를 결과에 적는다.
- E-02: 기계 부품의 볼트·두께·재질은 손대지 않았다.
- E-15: 움직임은 새 모형 조인트와 연구 키로만, machine.json 같이 고침.
- E-16: 판정은 수치로만. 스크린샷은 CLI 스냅샷 파일로만 저장하고 열지 않았다.
- E-10·U-07: 새 구매품 0.
- 실행 규칙 19: 조인트·스케치 숨김. 실행 규칙 8: 상자 같은 면 join 없음(다각형은 스케치 extrude cut).
- C-03: U4 누름 40 N 그대로.

## 8. 못 한 것
없음. CYCLE_V 전 단계 `motion.interference`는 지시서 5대로 검도가 CLI로 본다(486단계 > 100이라 앱에서 돌리지 않음).

## 9. 저장 확인 결과
CLI `run --results` 4분 24초(열기 포함). 저장본 REST에서 MAT_V·TAPE_V·SEAM_V·MAT_G·P_M03_CAR_PLATE·P_M02_WHEEL_TREAD·P_M01_FOOT bbox·부피가 MCP 저장 전 값과 같다(차 0). 저장본 CYCLE_V 320에서 MAT_V bbox −1030.012~641.262 × −327.35~1343.924(식 값과 같음), U5 접지 P_M03_WHEEL_TREAD X −452.5~−427.5(d₂ 440)·밑면 Z 10.0 = 매트 윗면. 연구·위치가 저장본에 들어 있다. MCP 저장 뒤 편집 0.

## 시간
- 걸린 시간·호출 수는 결과 timing에 적는다.

## 워크플로우 메모
- `motion.study {study, keys}`는 키를 통째로 갈아끼운다. 모든 연구에 조인트 키 하나를 더하려면 연구 8개를 통째(약 80 KB)로 MCP 인자에 직접 다시 써야 했다. 파일을 읽어 실행하는 MCP 명령이 없어서 출력 토큰이 많이 들고 옮겨 적기 실수의 위험도 있다(motion.list 대조로 확인함). 연구에 키 하나를 더하는 명령이나 batch 단계에 파일 인자를 받는 방법이 있으면 좋다.
- `inspect.clearance`가 Z로 1 mm 떨어진 두 바디(노루발 Z 12 ↔ TAPE_V Z 11)에 distance 0.0과 같은 점을 냈다(interference 0, bbox 1.0). clearance 0.0만으로 맞닿음을 판정하면 틀릴 수 있다. 0.0은 bbox·interference로 다시 본다.
- 설계안의 단계 수 "약 410"은 내림·대차 단계를 빼고 센 값이었다. 단계 수 어림에 '내림·대차 단계 포함'을 적어 두면 모델링 보고가 지시와 어긋나 보이지 않는다.
