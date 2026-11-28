"""디테일링 DP-2(체결 길이 · 탭 깊이) 생성기 — FSAP_v2.30.6 → v2.30.7 (2026-11-28, 엔진 v4.1.2)

같은 형상을 다시 만드는 순서다(프로젝트 규칙 3). 단계 스크립트는 tools/gen_detail_dp2/ 에 있다.
새 occurrence · 컴포넌트 id는 실행 때 정해지므로 명령 기록(tools/out/detail/DP-2/edit.json)을 그대로 돌리지 않고 이 순서로 돈다.

준비: 헤드리스 세션 하나(앱 MCP가 3D_Modeling/ 열기를 거부할 때)
    cp 3D_Modeling/FSAP_v2.30.6.sc <작업 폴더>/base.sc
    python -X utf8 -B sworker.py 41050 base.sc          # 열기 약 206 s, 로컬 TCP로 요청을 받는다(q.py)
    q.py: edit.checkpoint · motion.play REST 0 · component.list → r_complist.json · joint.list → r_jlist.json

1. targets.py   체결부 판정(tools/out/detail/fasten_v2306/f_bolts.json)에서 바꿀 볼트 189개와 새 형번을 정한다 → targets.json
                T너트 볼트는 표준 길이(16 · 20) 먼저, 한 단 올리면 홈 바닥에 닿을 때만 14 · 22
2. taps.py      timeline.roll_to {feature: 100414} 뒤 탭 구멍 28개의 base · height 를 timeline.edit 로 고치고 timeline.roll_to_end
                (플랩 바 22 · 팔 블록 윗면 2: 깊이 10 → 15, XP_TAP_1 만 12 / 팔 블록 옆 2: 10 → 15 / 혀 탭 2: 바 15 관통)
3. 손으로      component.paste_new {component: CB5-16_M04K_NY, parent: U8_PNEU} → CB5-16_DP2 (이름 · part_number CB5-16)
                occurrence.move 로 PY:7 자리에 놓고 component.copy_bodies → CB5-12_M08_PY 컴포넌트에 실물 CB5-16 바디
4. do.py A      PY 4(옛 바디 solid.remove · 이름 CB5-16_M08_PY_DP2) · 허브 볼트 2 제자리 교체
   do.py A2     롤 핀 볼트 2(자리 행렬 직접: 머리 밑 (1312, 7.5, 15 · 681), 넣는 방향 -Y)
   do.py B      임시 형상: 받은 STEP 생크를 solid.cylinder join 으로 늘림(SFB5-16 109 · CB5-22 4 · CB5-14 6)
   do.py C, C2  CB5-12_M03_3 36 · CB5-12_RX14 2 → CB5-16_DP2 occurrence(같은 부모 · 같은 local 행렬), 옛 occurrence 지움
   do.py D      STEP대기_CB5-14_DP2(새 컴포넌트) 6, CB5-12_M08_PX 8 제자리 교체
   do.py E      CB5-20_DP2(새 컴포넌트) 6, CB5-16_U3_BRKT 4 제자리 교체
5. fin1.py      씨앗 occurrence(CB5-16_DP2:1) 지움, 롤 핀 2개 밑구멍 12 → 15(끝에 자르는 원통 2)
6. matfix.py    재질 SS400 · STKR400 만들어 보 · 받침 · 이음판 5개에 지정(E-09, 밀도 7.85 그대로)
7. 저장 전     inspect.measure 전수 → sigdiff.py, clr.py · clr2.py(바뀐 바디 × 주변 틈 · 겹침), flapchk.py(J_U2_FLAP 4점), exp.py(임시 STEP · voids)
8. 저장        document.metadata.set description · motion.play REST 0 · browser.visibility joints/sketches false · save {path: FSAP_v2.30.7.sc}
9. 저장 뒤     solidcraft-cli run v_meas.json --in FSAP_v2.30.7.sc --results → patch.py --write(ledger.py sigpatch: 서명 · 체결 목록 · mach_props)
"""
if __name__ == '__main__':
    print(__doc__)
