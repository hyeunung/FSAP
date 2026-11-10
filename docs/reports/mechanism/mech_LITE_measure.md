# 측정부 — LITE(모델 무게 줄이기) 측정 2회째 (2026-11-10, 저장본 v2.8.9)

**요약**
- CLI로 혼자 열었을 때 열기 시간: **844.4 s**. 상한 240 s의 3.5배다. v2.6.5(LITE 1회째 뒤)에는 100.1 s였다.
  - 계산: CLI `run` 한 번 983.8 s − 단계 합 139.4 s.
  - 앱 타임라인 재계산 합은 1,021.5 s다(피처 3,082개).
- **다시 무거워진 원인은 보 `P_M07_BEAM` 하나다. PNEU-01(v2.8.7·v2.8.8)에서 더한 탭 피처가 원인이다.**
  - 보 재계산 679.6 s(전체의 67 %) 가운데 PNEU-01 뒤 피처가 655.0 s이고, 그 앞 피처는 23.9 s다.
  - `Combine40`: 탭 공구 42개(`TAP_P_M07_BEAM_2~43`)를 cut 한 번으로 뺀다. 이것만 **335.9 s**이고 boolean 재시도가 44번 일어난다. 최종은 tool_nudge 7.27e-3 mm다.
  - `Cylinder1281~1292`: 옛 탭을 join으로 메운 4개와 새 탭 cut 4개다. 합 **318 s**이고, 1292 하나가 110.1 s다.
- 두 번째 원인은 `P_M03_FRONT` 81.2 s와 `P_M02_FRONT` 62.7 s다(MOT-01 v2.7.0). 옛 구멍을 join으로 메우는 Cylinder 16개가 합 약 119 s이고, 각각 1.6~19.6 s에 nudge 재시도가 붙는다.
- 같은 구매품 사본(볼 827·CB5-16 485·HNTT8-5 473·SFB5-10 102 등)은 원인이 아니다. 이미 한 정의에 여러 occurrence로 들어 있다. STEP BaseFeature 297개는 합 2.5 s, 관 PipeFeature 104개는 38.1 s다.
- 어림: 세 바디의 메움·탭 이력을 싸게 바꾸면 열기는 **약 200 s 안팎**이다. 앱 재계산 비율로 셌다: 844 × (1,021.5 − 655 − 119) / 1,021.5 ≈ 205 s. 보 탭을 일찍 묶어 빼면 그 피처 값(수 s~수십 s)이 더해진다. 240 s 안에 들어오지만 여유는 작다.
- 전 상태 기준을 새로 남겼다: `tools/out/lite_check.json` `before`.
  - 바디 2,969개 각각의 bbox·무게중심·부피
  - BOM 179행, 수량 합 2,616
  - 모델 bbox X −2650.0~1442.0, Y −2015.0~2195.0, Z −900.0~915.5. 질량 1,153.76 kg, 무게중심 (−582.92, 63.81, 88.73)
  - v2.6.4·v2.6.5 기록은 `tools/out/lite_check_v265.json`로 옮겼다.
- **already_ok = false**(열기 844.4 s > 240 s).
- **알림:** 앱에 열린 `FSAP_v2.8.9`가 **dirty**다(undo 200, revision 458). 그래서 `open`하지 않았고, 앱 쪽은 아무것도 바꾸지 않았다(0절).

## 0. 통로·측정 표
| 항목 | 값 |
|---|---|
| sigcheck | `{"mode":"reuse","reason":"문서·해시가 같다","parts":2881}`. `tools/out/signatures.json`을 다시 썼다(E-17) |
| 통로 | MCP 읽기 2회(`running` 빈 목록, `inspect_design` measure·sketches·joints false)와 CLI `run --results --timings --profile` 1회(혼자, 백그라운드) |
| MCP `open`을 하지 않은 이유 | 앱에 이미 `FSAP_v2.8.9`(path `3D_Modeling/FSAP_v2.8.9.sc`)가 열려 있고 `dirty: true`, undo 200, redo 0이었다. 안내서 '문서 확인'의 "dirty면 open 전에 멈추고 보고하고, 버리지 않는다"를 따랐다. 같은 경로 `open`은 디스크를 다시 읽지 않는다는 원복 주의(실행 규칙 2)도 있다. 그래서 열기 시간과 전 상태 측정은 저장본에 대고 CLI로 한 번에 했다 |
| 동작 상태 초기화 | 앱 설계·포즈를 바꾸지 않았으므로 할 것이 없다(dirty 문서에 `motion.play`를 하지 않음) |
| 문서 확인 | 앱 쪽 타임라인 error 0, warning 47. warning은 모두 "Boolean retry"다 |
| 저장본 이력 | `.sc` zip에서 `document.json`을 바로 읽었다(`tools/out/mech_LITE/v289_document.json`). 피처 3,082, 컴포넌트 511, occurrence 2,721. 2개 이상 놓인 컴포넌트 129개, 사본 occurrence 2,210개 |

## 1. 열기 시간 차지 원인

### 1-1. 실측
| 무엇 | 값 | 근거 |
|---|---|---|
| CLI `run` 전체(혼자) | 983.8 s | `tools/out/mech_LITE/v289/base_check.time` |
| 단계 합 | 139.4 s | `assembly.bom` 0.0 s, 루트 `component.properties` 139.4 s(테셀레이션 134.1 s) |
| **열기(전체 − 단계)** | **844.4 s** | 상한 240 s |
| 앱 타임라인 재계산 합 | 1,021.5 s | `tools/out/mech_LITE/app_inspect_now.txt` 피처별 `ms` |
| 지난 기록 | v2.6.4 242.1 s → v2.6.5 100.1 s | `tools/out/lite_check_v265.json` |

### 1-2. 피처 종류별(앱 재계산)
| 종류 | 개수 | 시간 s |
|---|---|---|
| CylinderFeature | 1,310 | **589.1** |
| CombineFeature | 52 | **346.7**(Combine40만 335.9) |
| PipeFeature | 104 | 38.1 |
| ExtrudeFeature | 143 | 20.9 |
| BoxFeature | 318 | 11.4 |
| OffsetFacesFeature | 30 | 5.6 |
| ChamferFeature | 5 | 2.7 |
| BaseFeature(STEP) | 297 | 2.5 |
| 그 밖(Fillet 4, Sphere 3, 판금 28, Thread 8, Sketch 255 등) | — | 각 2 미만 |

### 1-3. 바디별(앱 재계산, 위 순서)
| 바디 | 시간 s | 피처 수 | 무거운 피처 |
|---|---|---|---|
| **P_M07_BEAM** | **679.6** | 35 (+탭 공구 42) | 아래 1-4 |
| P_M03_FRONT | 81.2 | 30 | 메움 join Cylinder794~797(r 2.85, 6.0~10.5 s), 878·879·888·889(r 2.2, 8.1~9.7 s). 바로 뒤에 같은 자리 cut r 2.1(1.4~1.8 s) |
| P_M02_FRONT | 62.7 | 29 | 메움 join Cylinder782~785(r 2.85, 6.1~19.6 s), 858·859·868·869(r 2.2, 1.6~7.2 s). 뒤에 같은 자리 cut |
| P_M08_TUBE_COMB_KDM | 22.6 | 37 | Cylinder 구멍 각 1.3~1.6 s(재시도 없음) |
| (바디 없는 Extrude) | 16.6 | 39 | Extrude52 4.7 s(W) |
| P_M03_LIFT_SIDE_P / _N | 7.2 / 5.8 | 19 / 15 | — |
| 그 밖 | 각 7 미만 | | |

### 1-4. P_M07_BEAM 피처(`tools/out/mech_LITE/heavy_bodies_v289.json`)
| 피처(타임라인 순번) | 무엇 | s | 재시도 |
|---|---|---|---|
| Box16 ~ Cylinder989(34~2547), 23개 | 몸통·속·R12·옛 탭 cut | 합 23.9 | Cylinder989 19.9 s 하나만 큼 |
| Cylinder1179~1220(2820~2861) | 탭 공구 바디 42개 new_body r 2.1. +Y 축 h10 34개, −Z 축 h10 6개(Z 650.1 윗면), +Y 축 h12 2개 | 작음 | — |
| **Combine40**(2862) | 보 − 탭 공구 42 cut(keep_tools false) | **335.9** | 44(refined_tolerance 반복 → tool_nudge 7.27e-3 mm, 2e-6 rad) |
| Cylinder1281·1283·1284·1285(3035~3038) | 옛 탭 **join 메움** r 2.4: (−126,120,462)·(1159,120,273)·(1159,120,287)·(−114,120,462) | 11.1·30.8·26.1·24.3 | 각 2 |
| Cylinder1289~1292(3048~3051) | 새 탭 cut r 2.1: (−106,120,462)·(−94,120,462)·(1159,120,261)·(1159,120,299) | 47.3·47.9·21.5·**110.1** | 각 2 |

PNEU-01 뒤 보 피처는 합 655.0 s다. 피처 하나가 보에 대한 boolean 하나이고, 보 면이 많고(탭 수십 개) nudge된 형상이라 하나에 20~110 s가 든다.

### 1-5. 사본(구매품)
| 형번 | BOM 수량 | 정의 수 | 판정 |
|---|---|---|---|
| BALL-D25.4(D-96) | 827 | 1 | 이미 정의 1개 + occurrence |
| CB5-16 | 485 | 73 | 정의마다 STEP BaseFeature, 합쳐도 이득 수 s |
| HNTT8-5 | 473 | 30 | 위와 같음 |
| SFB5-10 | 102 | 2 | 위와 같음 |
| HFC8-4080-B | 58 | 10 | 위와 같음 |
| TU0604 | 28 | 28 | 관 Pipe(바디마다 경로가 달라 사본 아님). 관 Pipe 104개 합 38.1 s |
| KQ2P-06 | 8 | 8 | 작음 |

STEP BaseFeature 297개는 모두 합쳐 2.5 s다. 사본을 묶어도 열기는 줄지 않는다. 지난 LITE-R2와 같은 결론이다.

## 2. 대상 부품(구상용)
| 부품 | 유닛·컴포넌트 | bbox X / Y / Z (mm) | 재질 | 부피 mm³ / 질량 g |
|---|---|---|---|---|
| P_M07_BEAM | U1_FRAME | −2380~1230 / 120~320 / 250~650 | Steel(STKR400 각관 400×200×t8, R12/R4) | 34,452,828.9 / 270,454.7 |
| P_M03_FRONT | U5_FLOAT | −1832~−1820 / −31~31 / 60~134 | SUS304 | 30,123.2 / 238.9 |
| P_M02_FRONT | U4_PRESS | −139.9~−116.0 / −31~31 / 55.65~136.55 | SUS304 | 34,586.6 / 274.3 |

- 값은 `signatures.json` 재사용이다. 바디마다의 bbox·무게중심·부피 전수는 `lite_check.json` `before.bodies`에 있다.
- 체결은 바꾸지 않는다. 탭 자리·지름·깊이는 1-4 표와 `heavy_bodies_v289.json`의 base·axis·radius·height가 그대로 기준이다.
- 이번 과제의 구동 요소: **없다.** 형상 변경 0인 모델 표현 과제이고, 조인트·행정은 바꾸지 않는다.

## 3. 통로·이웃 가동 유닛·작업 대상
이 과제는 형상을 바꾸지 않으므로(완료 판정 "형상 변경 0") 새 통로·프로브와 동작 상태별 점유를 잴 필요가 없다. 같은 이유로 매트 모형 위치, 가공 뒤 형상, 떨어진 조각도 해당 없다. 전후 같음은 `lite_check`(바디 2,969개 bbox·무게중심·부피, BOM, 모델 bbox)로 판정한다.

## 4. 같은 실수를 막을 기각·주의
| 근거 | 내용 |
|---|---|
| LITE-R2(결정로그 2026-11-06) | 사본 묶기는 바꾸지 않는다. 원문 "이미 정의 1개 + occurrence로 되어 있어 열기 차지가 작음". 이번에도 같다(BaseFeature 합 2.5 s) |
| T10-S02(결정로그) | 원문 "옛 구멍을 `face.delete`(heal)로 메우고 … join 메움은 쓰지 않는다". 지금 보와 M02/M03 앞판의 join 메움(Cylinder r 2.4·2.85·2.2)이 바로 무거운 피처다. 메움 대신 처음부터 그 옛 구멍 공구를 빼는 것이 맞다. 메운 구멍을 다시 뚫는 쌍(같은 자리 join → cut)은 순형상이 같다 |
| M07-D9 / LITE 1회째 | 보가 nudge(공칭에서 벗어남)되면 뒤 boolean이 모두 재시도 연쇄로 느려진다. v2.6.5에서 공칭으로 돌렸지만, Combine40 nudge 7.27e-3 mm로 다시 공칭에서 벗어났다. 보 bbox가 공칭(120/320/250/650)인지 전후 함께 본다 |
| PNEU-01-M11 | 원문 "보 옛 탭(Z 273·287) 메움·새 탭 cut". CHANGELOG v2.8.8에는 "보 Z 262 탭 메움 커널 실패"도 있다. 옛 탭 공구를 Combine40 tools에서 빼면 메움이 필요 없다(공구 바디 이름은 `heavy_bodies_v289.json` `Combine40_tools`) |
| 실행 규칙 2·3 | 앱 문서 dirty면 바꿔 끼우지 않는다. 모델링은 `solidcraft-cli run edit.json --in FSAP_v2.8.9.sc --save FSAP_v2.8.10.sc`를 쓰거나, 사용자 확인 뒤 MCP로 한다. 새 번호 v2.8.10이다 |
| LITE 1회째 BOM | 패턴 바디로 묶어 BOM 수가 줄면 안 된다(안내서 '모델 무게'). 이번 안은 사본을 건드리지 않으니 해당 없다 |

구상 부서가 쓸 방향(측정 근거만 적고, 안을 정하지는 않음):
- (가) 보의 탭 공구 42개와 Cylinder1289~1292 새 탭 4개를 보 몸통이 단순할 때 cut 한 번으로 뺀다. 옛 탭 4개(메움 대상)는 처음부터 공구에서 뺀다. 그러면 Cylinder1281~1285 메움은 지운다. 자리는 Cylinder989 앞, 또는 LITE 1회째처럼 구멍 묶음을 속 빼기 앞에 둔다.
- (나) P_M02_FRONT·P_M03_FRONT: 옛 구멍 cut과 그 구멍의 join 메움 쌍을 함께 지운다. 메운 뒤 같은 자리를 다시 cut하는 것만 남긴다.
- 어느 안이든 보 공칭 bbox 복귀(nudge 0)를 확인한다.

## 5. 이미 되는지
| 판정 항목 | 지금 | 기준 | 결과 |
|---|---|---|---|
| 열기 시간 | 844.4 s(CLI 혼자) | ≤ 240 s 또는 줄인 만큼 | **안 됨** |
| 부품 수·자리·BOM 전후 같음 | `before`만 있음(바디 2,969, BOM 179행/2,616) | after와 같음 | 아직 |
| 형상 변경 0 | — | — | 아직 |

**already_ok = false.**

## 6. 파일
- `tools/out/lite_check.json`: 새 기준 `before`(v2.8.9). 옛 v2.6.4·v2.6.5 기록은 `tools/out/lite_check_v265.json`
- `tools/out/mech_LITE/v289/`: `base_check.json`, `run_base.sh`, `base_check.out.json`, `base_check.time`, `bom_v289.json`, `mk_baseline.py`
- `tools/out/mech_LITE/feat_cost289.json`, `feat_cost289.py`: 바디별·피처별 비용, 사본 통계
- `tools/out/mech_LITE/heavy_bodies_v289.json`: 보·앞판 2개의 피처 전부(자리·축·반지름·깊이·s·재시도), Combine40 공구 이름
- `tools/out/mech_LITE/app_inspect_now.txt`, `v289_document.json`: 원본

## 7. 시간
- 걸린 시간 약 1,150 s(측정 예상 20분, 등급 M)
- CAD 호출: MCP 2회, CLI 1회
- 설계 파일 열기: 1회(CLI). 가장 긴 열기 `open_s` 844.4 s
- 앱 재시작: 0

## 워크플로우 메모
- LITE를 한 번 하고(v2.6.5) 뒤 과제(PNEU-01)가 같은 보에 탭을 42+8개 더해서 다시 3.5배가 됐다. 모델링부가 무거운 바디(보)에 피처를 더할 때 그 피처 ms를 보는 장치가 없다. 개선후보: 새 피처 하나가 30 s를 넘으면 모델링부 보고서에 적고, 그 자리에서 "일찍 묶어 빼기"로 바꾼다.
- 바꿔 말하면 `runstats`가 v2.8.7 저장 직후에 열기 증가를 잡지 못했다.
