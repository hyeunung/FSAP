# DC-01 모델링 — 매트 끝 300 안 홈 회전 U4 혼자, C-37 (다)로 판정 (모델링부, 2026-11-10)

## 요약
- 저장: `3D_Modeling/FSAP_v2.8.9.sc`(기준 v2.8.8 다른 이름 저장, 마지막 자리 +1). 통로는 MCP(앱이 켜져 있었고 `running` 목록 비어 있음). 앱 응답 끊김이 1번 있었고, 끊긴 묶음은 작게 나눠 다시 보냄(재시작 0). `tools/config.json` doc와 `tools/machine.json` doc → v2.8.9.
- 형상·부품·조인트·연구 변경 **0**. 설계 파일에서 바뀐 것은 문서 설명(metadata), joints 숨김(410)·sketches 숨김(255)뿐(규칙 19). 저장 확인 결과 2,969바디가 모두 같음(4절).
- U홈 CYCLE_G1 바닥에서 U4 혼자 도는 구간 = 연구 **321~390단계(ROT −21 → −90, 69°)**, J_U5_LIFT 30(들림). 시간 키(`machine.json _timing.CYCLE_G1_바닥.U4만`) **3.0 + 3.4×5 = 20 s(≥ 6 s)** 그대로 두고 확인함. 구름 0.02, 가속 포함 **SF 1.057**. U4 밑 원판 끌림까지 넣으면 **1.024**. 구름 0.05면 0.49라서 D-96 선정 조건(≤ 0.02)이 필요함.
- 같은 바닥의 U4+U5 피벗 키는 **0.8 → 1.2 s**로 늘림. U5 밑 띠 μs 0.30에서 SF 0.836 → **1.054**(해석부 VGR-01-R3 지적 중 G1 바닥 몫). 바닥 피벗 합은 27.8 → 31.4 s.
- 과제 범위 간섭: 321·338·356·373·390(0·25·50·75·100 %)에서 MAT_G·TAPE_G와 바늘 둘레 23바디 사이에 **새 겹침 0**. 겹침은 바늘 기준선 MAT 20.1·TAPE 22.1 mm³뿐임.
- 문서: FUNC-01 ⑥·⑦(홈 매트 64.2 → **92.8 s**), 자료대기 D-96, 요구서 DC-01(VGR) '해결(검도 확인 대기)', 결정로그 DC-01-M1~M4, CHANGELOG.
- 미완: 없음. 구동 후보로 남는 것: CYCLE_L·S·G 모서리 U4+U5의 띠 저항(VGR-01-R3, 이번 범위 밖).

## 1. 근거 규칙
- C-37 (다) 원문: "볼 유닛 선정 조건 구름 저항 ≤ 0.02(필요 ≤ 0.0285, 40 N·μ 0.4·d₁ 0.1), 그 구간 회전 ≥ 6 s(가속 포함 SF ≥ 1 확인)". (가)·(나)는 하지 않음.
- E-02 "합격은 동작·간섭". 회전력이 모자라 매트가 미끄러지는 것은 기능 깨짐이라 시간 키로 고침.
- E-05: 수정도 새 번호로 저장. 규칙 19: 저장 전 joints·sketches 숨김. E-08: 저장 전 REST 0.
- E-18 "FEA는 형상·하중 경로가 바뀐 부품만". 형상 변경이 0이라 손계산만 함. 해석 환경도 없음(D-16).
- E-17 과제 범위 검사: 관련 조인트(J_WP_G_ROT)의 0·25·50·75·100 % 점에서 inspect.clearance. 전 사이클 motion.interference는 돌리지 않음.

## 2. 작업 순서 (MCP)
| 단계 | 한 일 |
|---|---|
| 연결 | `running` 빈 목록 → `open v2.8.8.sc`(피처 3,082, 오류 0) → `edit.checkpoint` 26 |
| 연구 확인 | `motion.list`: CYCLE_G1 514단계. J_WP_G_ROT 키 [210, 90]→[390, −90](1°/단계), J_U5_LIFT [320, −10]→[321, 30]→[492, 30]→[493, −10], J_U3_NEEDLE −30(바늘이 매트 안, 피벗 중심) |
| 간섭 | 5점 `motion.play CYCLE_G1` + `inspect.clearance`(첫 5점 묶음은 앱 응답 끊김 → 1·1·2점씩 다시 보냄) |
| 저장 전 | `document.metadata.set description` "DC-01 mechanism: CYCLE_G1 groove-bottom pivot timing (U4-only 20 s, U4+U5 1.2 s/pivot); geometry unchanged", joints·sketches 숨김, `motion.play REST 0`(conflicts 0) |
| 저장 | `save {path: 3D_Modeling/FSAP_v2.8.9.sc}` 5,237,905 B, 문서 이름 FSAP_v2.8.9. 저장 뒤 편집 없음 |

다시 실행할 때 쓰는 기록: `tools/out/mech_DC-01/edit.json`(4명령)·`edit_meta.json`(base v2.8.8 → result v2.8.9).

## 3. 시간 키와 회전력 (`tools/out/mech_DC-01/g1calc.py` → `g1calc.json`)
식은 VGR-01 수정 1회차 `fix1calc.py`와 같음. 관성·구름 팔은 `c37design.json` G 매트 피벗 점 φ −21·−45·−90(I 4.801~4.879 kg·m²). 원판 끌림·베어링·관성은 fix1calc 값(0.0347 + 0.0133 N·m, I_eq)을 씀. 잡는 토크는 U4 0.4×40×0.1 = 1.60 N·m, U5 0.4×40×0.8 = 12.8 N·m. 속도는 정지→정지 삼각, α = 4θ/t².

| 구간(연구 단계) | 키 옛 → 새 | A 판정 조건(구름 0.02) | B + 원판 | C + 띠 μs 0.15 | C + 띠 μs 0.30 | D 구름 0.05 |
|---|---|---|---|---|---|---|
| 90 → −21 U4+U5, 12°×9 + 3°(210~321) | 0.8 → **1.2** ×9, 0.6 | 1.908 → 3.601 | 1.889 → 3.548 | 1.159 → 1.625 | 0.836 → **1.054** | 2.51 |
| −21 → −90 **U4 혼자**, 9° + 12°×5(321~390) | 3.0 + 3.4×5 그대로(20 s) | **1.057** | **1.024** | 1.024 | 1.024 | 0.492 |

- 필요 최소 시간(SF 1.02, 세 피벗 점 중 불리한 쪽): U4 혼자 9° 3.0 s, 12° 3.4 s. U4+U5 12° 1.2 s(μs 0.30), 3° 0.6 s.
- U4 혼자 각가속도 한계(원판 포함) 0.080 rad/s², 최고 각속도 7.06 °/s.
- `tools/machine.json _timing.CYCLE_G1_바닥`: 'U4+U5' "12° 피벗 1.2 ×9 + 3° 0.6", '연구 단계'·'U4혼자_합'·'_근거' 키 더함. `한계.U4혼자_alpha_rad_s2_원판끌림포함.G1` 0.080을 더함. 옛 값은 `tools/out/mech_DC-01/machine_timing_before.json`.
- 이번 회차에 새로 힘을 받는 가공품은 없음. U4 바퀴 접선 하중은 16 N·0.96 N·m로 VGR-01과 같고, MOT-01 모델 58.3 N·3.5 N·m 안에 듦. 그래서 임시 STEP을 내지 않음(exported_steps 빈 배열).

## 4. 검증 수치
- 과제 범위 간섭(`tools/out/mech_DC-01/clr_g1_steps.json`): 5점 모두 겹침은 U3_NEEDLE_PIN↔MAT_G 20.097·TAPE_G 22.107 mm³뿐임. 이것은 기준선(machine.json baseline_overlaps, F01-C1 실측)과 같음. 맞닿음 0: 아랫축 LOWER·P_M02_DISK·P_DC205_STRIP(매트가 볼 면 위에 얹힘). 가장 가까운 것: U4 트레드↔MAT_G 0.011~0.038, TAPE_G↔P_M06_SHOE 1.5. truncated false, unchecked 0. 각 점 motion.play conflicts 0.
- 저장 확인: CLI `eval inspect.measure`를 v2.8.9와 v2.8.8에 돌려 비교함(`savecheck_new.json`·`savecheck_old.json`·`savecheck_cmp.json`). 결과: 2,969 = 2,969바디이고 이름·부피·bbox 차이는 최대 5.4×10⁻¹⁰ mm(부동소수 잡음)라 다른 것 0. 열기와 측정은 CLI 2개를 나란히 돌려 약 16분 걸림.
- 서명: `ledger.py sigpatch --parts tools/out/mech_DC-01/sig_parts_empty.json` → 바뀜 0, 없어짐 0, 전체 2,881(`tools/out/signatures.json`).
- 숨김·리지드·재질: 새 바디가 0이라 바뀐 것 없음. 조인트 자기 점검: 바꾼 조인트가 0이라 하지 않음.

## 5. 못 한 것
- 없음. 이번 범위 밖 구동 후보: CYCLE_L·S·G 모서리 U4+U5 회전의 U5 밑 띠 저항(VGR-01-R3). 같은 식으로 시간 키를 점검해야 함.
- 구름 저항 실측(≤ 0.02)은 시제품 전 저울 시험으로 함(요구서 7절, D-96).

## 워크플로우 메모
- MCP `motion.play` 결과는 quiet일 때도 occurrence 자세와 조인트 값 전부를 돌려줌. 5점 묶음은 50만 자를 넘었고, 이때 앱 응답 끊김(os error 10060)이 1번 생김. 짧은 점검도 1~2점씩 보내야 함.
