"""디테일링 DP-2 수정 1회차 생성기 — FSAP_v2.30.7 → v2.30.8 (2026-11-28, 엔진 v4.1.2)

검증 문제(기준 1건): 플랩 바 P_RX12C1_FLAP_BAR_XP 의 XP_TAP_1(밑구멍 Ø4.2 깊이 12, 축 (1092.5, -330), Z -13 → -25)에
CB5-16 이 11 들어가 끝–바닥 1.0 mm → 머리가 앉기 전에 불완전 나사에 걸린다(M-01).
고침: 그 occurrence 하나만 CB5-16_DP2:15 → STEP대기_CB5-14_DP2 occurrence(같은 부모 U2_FLAP · 같은 local 행렬). 들어감 9.0 · 끝–바닥 3.0.

같은 형상을 다시 만드는 순서(프로젝트 규칙 3). 단계 스크립트는 tools/gen_detail_dp2_fix1/ 에 있다.
occurrence id 는 실행 때 정해지므로 명령 기록(tools/out/detail/DP-2/edit_fix1.json)의 id 는 그 실행의 값이다.

준비: 헤드리스 세션 하나(앱 MCP가 3D_Modeling/ 열기를 거부할 때)
    cp 3D_Modeling/FSAP_v2.30.7.sc <작업 폴더>/base_v2307.sc
    python -X utf8 -B sworker.py 41070 base_v2307.sc       # 열기 약 524 s(SolidCraft 0.51.2), q.py 가 로컬 TCP 로 요청
    q.py: edit.checkpoint · motion.play REST 0 · component.list · joint.list(r_jlist.json)

1. fix.py        occurrence.copy {component: STEP대기_CB5-14_DP2, parent: U2_FLAP}
                 occurrence.move {space: local, to_matrix: [0,0,1,1092.5, 0,1,0,-330, -1,0,0,-8]}   (머리 밑 (1092.5, -330, -8), 넣는 방향 -Z)
                 selection.delete {occurrences: [CB5-16_DP2:15]}       (옛 occurrence 에 조인트 0 — 부모 U2_FLAP 이 J_U2_FLAP 으로 돈다)
2. chk.py        새 볼트 x 주변(상자 2 mm) inspect.clearance, body_topology(바 · 볼트 · 판 원통), J_U2_FLAP -22.5 · -45 · -67.5 · -90 새 겹침, joint.list
3. 저장 전       document.metadata.set description · motion.play REST 0 · browser.visibility joints/sketches false
4. 저장          save {path: 3D_Modeling/FSAP_v2.30.8.sc}  (한 번, 저장 뒤 편집 없음) → tools/config.json doc
5. 저장 뒤       solidcraft-cli run v_meas.json --in FSAP_v2.30.8.sc --results → 서명과 대조(저장 확인)
                 patch_fix1.py --write   (ledger.py sigpatch: 서명 1 바꿈 · 1 지움, 체결 목록 1줄)
"""
if __name__ == '__main__':
    print(__doc__)
