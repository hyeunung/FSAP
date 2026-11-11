# STEP 대기 재시도 — FSAP_v2.8.13 (2026-11-11)

요약
- 대상: v2.8.13 구매 BOM의 STEP대기_ 형번(형번이 정해진 것 11개, 관 TU0604·TU0805 포함 13개). 지금 바꿀 수 있는 것(swap)은 0개.
- stepcheck·PartsLibrary/index.csv: 13개 모두 없음(SCXW46은 -12-19·-15-19만 있음).
- 미스미 로그인: 됨(지시문 (d)에 따라 2026-11-10에 확인한 상태. 이번에 브라우저로 다시 확인하지 않았다).
- 무거운 원본(WF-218): F3SG-4RA0800-14 → LITE_ 대상(이전 판정을 그대로 쓴다).
- 남은 것: SMC·미스미 9개 형번과 관 2개 받기는 구매부로 넘긴다. F39-LSGF(D-135)·KC-40340(D-121)은 not_found.
- F3SG-BRKT는 브래킷 이름이라 형번이 아니어서 뺐다. 형번이 아직 정해지지 않은 PSCS16·2400.05.12PZ·TPH-01·S-M5-2·BALL·LEVELER·체결품·867-392342(D-10)도 뺐다.

방법: CAD 파일을 열지 않았다. BOM(docs/bom/FSAP_v2.8.13_purchased.csv)에서 STEP대기_ 이름을 뽑아 목록을 만들었다. 저장하지 않았으므로 원복할 것도 없다. 결과는 tools/out/step_wait.json.

## 워크플로우 메모
- 모델에서 직접 목록을 뽑지 않고 BOM으로 대신했다(BOM이 v2.8.13과 같다는 가정).

## 재확인 v2.10.1 (2026-11-11)
- purchased-step·PartsLibrary에 새 STEP 없음 -> swap 0, waiting 그대로, lite F3SG-4RA0800-14 그대로.
