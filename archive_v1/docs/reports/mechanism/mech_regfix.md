# 회귀 수정 — 안쪽 끝 막대 멈춤 (v1.0.15 → v1.0.16)

요약
- 저장본 `3D_Modeling/FSAP_v1.0.16.sc`(문서 이름 FSAP_v1.0.16, REST). `tools/config.json` doc 갱신. 통로 MCP(앱 --control 27878, `running` → `[]`, open 오류 0).
- 바뀐 부품: `P_N04_CHAIN_NP_BAR`, `P_N04_CHAIN_PN_BAR`, `P_N04_PANEL`(멈춤 이 2 더함, 홈 2 끔), `P_N04_NECK`(홈 끔), `P_N04_PIN_3`, `P_N04_PIN_4`. 조인트·연구 키·볼트 변경 0.
- 원인(RF-01): 판·목 벽 홈 `Box252`·`Box253`이 **루트 컴포넌트 피처**로 움직이는 바디(U5_AIRTABLE)를 잘랐다. 루트 피처는 다시 계산되는 순간의 월드 자세로 잘라서, REST(J_U4_X 0)에서만 홈이 막대 자리에 있었다. 그래서 REST만 겹침 0이고 나머지 거의 전 단계에서 판이 막대 끝 X −830~−829를 채웠다.
- 고침(RF-02): 홈 멈춤을 버리고 판 −830 면에 붙인 **이(齒) 멈춤**으로 바꿨다. 막대·러그 +X 끝은 −830.5(LOWER·꼬리판 선 −830과 0.5)다.
- 결과: 회귀 문제 자세 14개에서 막대 ↔ 전 바디 겹침 0(truncated false). J_U4_X 800에서 막대 ↔ LOWER 0.5. sweep NP·PN stopped_at null(맞닿음은 시작부터 얹힘·멈춤 접촉뿐).
- 미완: 전체 회귀는 다음 회귀 부서가 한다(E-03 라운드 끝 한 번). 강도(물림 X 1~2 mm)는 디테일 N04-D13 갱신으로 기록만 했다(E-02).

## 1. 순서와 통로

| 단계 | 내용 |
|---|---|
| 연결 | `running` → `[]`, `open` FSAP_v1.0.15.sc 오류 0·피처 769 |
| 문서 확인 | 처음 연 직후는 편집 전이었다. `edit.checkpoint`는 실패한 batch와 함께 되돌려져(rolled_back) 원복점이 남지 않았다. 대신 지운 피처 id로 되돌림을 관리했다(아래 3절) |
| 동작 상태 초기화 | `motion.play {study: REST, step: 0}` |
| 원인 확인 | REST에서 inspect.clearance 막대 ↔ 판·목·PIN 겹침 0. CYCLE_G1 9단계(J_U4_X 135)에서 NP ↔ PANEL 30 mm³(X −830~−829 · Y −301~−291 · Z −3~0), PN ↔ PANEL 5 mm³ — 회귀 summary와 같음. 판 면 목록에 홈 면(X −828.5)이 없었다. `timeline.inspect Box252`: corner [−830, −850, −3], participants PANEL·NECK, component 키 없음(루트) |
| 그림 | 3절 |
| 저장 전 검사 | 14자세 + REST + J 800 clearance, sweep 2, joint.solve conflicts [] |
| 저장 | REST로 두고 `save {path: 3D_Modeling/FSAP_v1.0.16.sc}` → name FSAP_v1.0.16. 저장 뒤 편집 없음(임시 STEP export만) |
| 저장본 확인 | CLI `run --results`(저장 없음), 4절 |

`inspect.interference`는 같은 자세에서 겹침 0을 냈고 `inspect.clearance`(clearance 0)가 30 mm³를 냈다. 판정은 회귀와 같은 clearance로 했다.

## 2. 원인 — 루트 피처가 움직이는 바디를 자름

- v1.0.15 수정 2회차(mech_N04_model2.md stage_2 30·31단계)는 홈 상자 2개를 루트에서 월드 좌표로 그렸다. 그때 자세가 REST였으므로 REST에서는 맞았다.
- 같은 방식으로 이번에 루트에 상자를 그려 보니, G1 9단계에서 PN 막대 부피가 4,146 → 87 mm³로 바뀌었다. 루트 피처가 막대가 그 순간 있는 월드 자리를 잘랐다. 그래서 형상이 자세마다 달라진다.
- 회귀 P2(J_U4_X 800, 월드 −30에서 LOWER·꼬리판과 겹침)는 이와 별개로 막대 끝 −829가 판 −830 선(= J 800에서 LOWER −X 면)을 넘었기 때문이다. 홈 멈춤은 막대가 −830을 넘어야 하므로 홈을 제자리에 고쳐도 P2가 남는다. 그래서 멈춤 방식을 바꿨다.

## 3. 고친 것(RF-02·RF-03)

새 피처는 모두 그 바디의 컴포넌트를 활성화해 그 안에 만들었다. 자세는 REST, J_N04_BAR_NP 0이다. 이때 U4_X·U5_AIRTABLE·U5_BAR_NP·U5_BAR_PN 원점이 모두 0이라 컴포넌트 좌표가 월드와 같다. 생성 명령은 `tools/out/mech_regfix/stage_regfix.json`에 있다.

| 부품 | 전(v1.0.15) | 후(v1.0.16) |
|---|---|---|
| `Box252`·`Box253`(판·목 홈) | 루트 피처, 켜짐 | **끔**(suppressed). 판 윗면 1.5 틈과 옆 홈이 없어졌다 |
| `P_N04_CHAIN_NP_BAR` | X −969~−829 · Y 57~67 · Z −3~0, 4,200 mm³ | X −969~**−830.5**, 4,155 mm³(Box259, U5_BAR_NP) |
| `P_N04_CHAIN_PN_BAR` | 몸 X −969~−831, 러그 X −831.5~−829 · Z −5~−3, 4,185 mm³ | 몸 X −969~**−832**, 러그 X **−832.5~−830.5** · Y −66.5~−57.5 · Z −5~−3, 4,146 mm³, 한 덩어리(shells 1)(Box260~262, U5_BAR_PN) |
| `P_N04_PIN_3`/`_4` | X −834~−832 | X −834~**−833**(PN 러그와 0.5)(Box263·264, U5_AIRTABLE) |
| `P_N04_PANEL` 이 NP | 없음 | X −831.5~−830 · Y 67~77 · Z −2.5~−0.5(Box265). NP 막대 +Y 끝 Y 67이 닿음, 물림 X 1 × Z 2 |
| `P_N04_PANEL` 이 PN | 없음 | X −832.5~−830 · Y −77~−66.5 · Z −5~−3.5(Box266, 턱 Z −5 위에 앉음). PN 러그 −Y 끝 −66.5가 닿음, 물림 X 2 × Z 1.5 |

엇갈림:
- PN 몸(−832) ↔ NP 이(−831.5): 0.5
- PN 러그(Z −3 위끝) ↔ NP 이(Z −2.5): 0.5
- NP 막대(Z −3 밑) ↔ PN 이(Z −3.5): 0.5
- 이 두 개는 안장·바깥 앞끝 길 X −966~−834 밖이다(N04-E05 '따를 것' 7 "막대를 잡는 면은 안장·바깥 앞끝이 쓸고 가는 X −966~−834 · Z −5~0 밖에 둔다").
- 이는 X < −830이고 LOWER는 Y ±45라서 J 800에서도 만나지 않는다.

판 부피는 254,174,738.9 → 254,174,808.3 mm³(+69.4 = 이 30 + 39.4, 홈 2를 끈 뒤)이고 shells 1이다.

중간에 실패한 것(되돌림):
- 루트에서 OffsetFace·상자로 처음 그렸다. Box252·253을 끄며 다시 계산되자 PN 결합 상자가 "닿지 않음" 경고를 내고 막대가 두 조각이 됐다. 그 피처 8개를 지웠다.
- 다음에 컴포넌트 안에서 그렸는데, 앞 batch의 REST 재생이 롤백돼 자세가 G1 9단계에 있었다. 막대가 쪼개져서 피처 8개를 지웠다.
- 세 번째에 REST를 따로 확인하고 다시 그렸다. 지금 타임라인에 남은 내 피처는 Box259~266 8개와 Box252·253 끄기뿐이다.

## 4. 검사

### 4-1. 회귀 문제 자세(MCP, clearance 0, 막대 2 ↔ 전 바디 + 막대끼리)

| 자세 | 겹침 | truncated |
|---|---|---|
| CYCLE_G1 9·113, CYCLE_G2 592·596 | 0 | false |
| CYCLE_S 135·140·145·343·346·352·353(J_U4_X 800 근처, LOWER·꼬리판 겹침 자리) | 0 | false |
| MAINT 0(J_U4_X −200) | 0 | false |
| CYCLE_L 100·400 | 0 | false |

결과 `tools/out/mech_regfix/poses_summary.json`(원본 `poses_out.json`)

### 4-2. 멈춤·J 800·sweep(MCP)

| 항목 | 값 |
|---|---|
| REST 틈(0.6 안) | NP ↔ NECK 0.5, NP ↔ 판 0.5, NP ↔ N 앞끝 0.5. PN ↔ 판 0(러그가 PN 이에 멈춤 접촉 + 턱 위 얹힘), PN ↔ PIN_2·_4 0(얹힘). 매트 ↔ 막대 0(윗면 Z 0 맞닿음) |
| NP J 0 | NP ↔ 판 0 = NP 이에 멈춤 접촉, 겹침 0 |
| PN J 0 | PN ↔ 판·PIN_4 0(멈춤 접촉·얹힘), 겹침 0 |
| sweep J_N04_BAR_NP −120 → 0 (step 2, ↔ U5_AIRTABLE) | stopped_at null(시작부터 PIN 얹힘) |
| sweep J_N04_BAR_NP −538 → −130 | −134.01에서 멈춤: 막대 밑면 Z −3이 PIN_2/_4 윗면 Z −3에 올라타는 얹힘 접촉(겹침 아님, v1.0.15와 같은 얹힘). 그 뒤 구간은 위 줄 |
| sweep J_N04_BAR_PN 0 → 893 (step 5) | stopped_at null(시작부터 얹힘) |
| J_U4_X 800, NP −100(Y −43~−33, LOWER Y ±45 안), PN 0 | 겹침 0, NP ↔ LOWER **0.5** |
| J_U4_X 800, NP 0, PN 120 | 겹침 0, 0.6 안 쌍 없음 |
| joint.solve | conflicts [], errors [] |

결과 `tools/out/mech_regfix/stop_j800_out.json`

### 4-3. 저장본 확인(CLI, 저장 없음)

`solidcraft-cli run tools/out/mech_regfix/cli_verify.json --in FSAP_v1.0.16.sc --results`(1분 39초) → `cli_verify_out.json`. 파일을 새로 읽어 다시 계산한 결과다.

| 항목 | 값 |
|---|---|
| CYCLE_G1 9단계(J_U4_X 135) 바디 | NP 4,155 · PN 4,146 · PIN_3/4 20 · 판 254,174,808.3 mm³(shells 1). MCP의 REST 값과 같다(자세 의존 없음) |
| 겹침(clearance 0, 막대 2 ↔ 전 바디) | G1 9: 0, S 346: 0, MAINT 0: 0. truncated false |
| joint.list | floating [], conflicts [], 조인트 225 |
| document.inspect | dirty false, 바디 158, 숨김 0, 타임라인 오류 0, 이름 FSAP_v1.0.16 |

## 5. 저장 전 검사(안내서)

- 숨김: 새 바디 0, 바디 수 158 그대로. 리지드 그룹: 새 컴포넌트 0. 재질: 바뀐 바디는 원래 재질 그대로(A6063·A5052_HC·SUS304).
- 볼트: 새 볼트 0, 렌치 접근 해당 없음.
- 임시 STEP(힘 받는 바뀐 가공품): `tools/out/mech_regfix/stepout/P_N04_CHAIN_BAR_regfix.step`(NP·PN 막대, PIN_3/4). 판은 이 2만 더했고 하중 경로가 같은 판 −830 면이라 따로 내지 않았다.
- 강도: 해석 환경이 없다(자료대기 D-16). 정하중 스프링 형번이 미정이라 멈춤 지압은 판정하지 않았다(v1.0.15와 같음). 디테일 N04-D13에 물림 치수를 갱신했다(E-02 "강도 여유 … 디테일로 기록만").

## 6. 결정로그·문서

- 결정로그 `## 회귀 수정 — 안쪽 끝 막대 멈춤 (2026-11-03)`: RF-01~RF-03, 디테일 N04-D13(갱신)·N04-D17.
- CHANGELOG v1.0.16. config.json doc → FSAP_v1.0.16.sc.
- 요구서 7절 N04-T2(홈이 매트 쪽에 남기는 틈)는 홈을 껐으므로 해당이 없어졌다. 판 윗면에는 이제 틈이 없다. 이 NP의 윗면 Z −0.5는 판 −830 면 밖(X < −830)이고 매트 밑 Z 0보다 0.5 아래다.

## 워크플로우 메모

- 루트 컴포넌트 피처(상자·자르기)가 움직이는 컴포넌트의 바디를 고치면, 다시 계산될 때의 자세로 형상이 달라진다. 이번 회귀 P1의 원인이다. 모델링 지시에 "움직이는 바디를 고치는 피처는 그 컴포넌트 안에서, 컴포넌트 좌표 = 월드인 자세에서 만든다"는 점검을 두고, 저장 전 검사에서 '바디 부피를 REST와 다른 자세에서 비교'하면 잡힌다(N04-D17: 남은 곳 전수 확인 안 함).
- `edit.checkpoint`를 실패한 batch 안에 두면 같이 롤백되어 원복점이 사라진다. 원복점은 단독 호출로 잡아야 한다.
- 같은 batch의 `motion.play` REST가 다른 단계 실패로 롤백되면 자세가 앞 자세에 남는다. 좌표로 그리기 전에 자세를 따로 확인해야 한다.
- `inspect.interference`와 `inspect.clearance`(clearance 0)가 같은 자세에서 다른 답(0 / 30 mm³)을 냈다. 회귀와 같은 clearance로 판정했다.
