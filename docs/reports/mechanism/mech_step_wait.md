# STEP 대기 재시도 (v1.0.16, 2026-11-03)

요약: 모델 v1.0.16에 STEP대기_ 바디 36개(형번 22종). 저장소·PartsLibrary 모두 없음(HFS8-4080은 다른 길이만 있음, 248 길이 없음) → 바꿀 것 0. 미스미 로그인 풀림이라 받지 않음(실행 규칙 10·12). 형상은 임시 그대로 진행.

- 목록: CLI document.inspect(tools/out/sw_inspect.json). 설계 이력 script는 컴포넌트 설계 미지원(#886).
- 확인: stepcheck.py 형번별, PartsLibrary/STEP 폴더.
- 미스미: 새 탭에서 kr.misumi-ec.com 머리 '로그인 / 회원가입' 확인 → 풀림. 재로그인 안 함.
- CAD 앱은 열지 않음(읽기만, 저장 없음, 동작 상태 변경 없음).

| 형번 | 이유 |
|---|---|
| 2400.05.075.0 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| CRBH5013 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| E4.56.10.150.0 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HFS8-4080-248 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HTBN635S5M-150 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HTPA20S5M150-A-N12 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HTPA25S5M150-A-N14 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HTPA28S5M250-A-N19 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| HTPA60S5M150-A-N30 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| IXP-M8 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| JIS-P25 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| S5M150-OPEN | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| S5M250-OPEN | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| SSEB13-560 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| VB-004-E2 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| AZM66AC-PS25 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| CDJ2B16-110 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| CDJ2B16-150 | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| KQ2L06-M5A | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| MHMF042L1U2M | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| MHMF082L1U2M | login: 미스미 로그인 풀림(머리에 '로그인 / 회원가입'), 재로그인 안 함 — 저장소·PartsLibrary에도 없음 |
| 867-392342 | not_found: Dürkopp 재봉 헤드 실물 자료는 사용자 자료 대기(D-10) |

## 워크플로우 메모
- `solidcraft-cli script`가 컴포넌트 있는 설계에서 미지원(#886) — 목록은 document.inspect로 대신.
