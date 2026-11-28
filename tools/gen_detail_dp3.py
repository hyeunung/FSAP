"""디테일링 DP-3(보 탭 · 끝판 · 관 받침) 생성기 — FSAP_v2.30.8 -> v2.31.0 (2026-11-28, 엔진 v4.1.2)

같은 형상을 다시 만드는 순서다(프로젝트 규칙 3). 단계 스크립트는 tools/gen_detail_dp3/ 에, 보낸 명령 기록은 tools/out/detail/DP-3/m0/cmds_*.json 에 있다.
새 occurrence · 컴포넌트 id는 실행 때 정해지므로 명령 기록을 그대로 돌리지 않고 이 순서로 돈다.

준비: 헤드리스 세션 하나(앱에 다른 설계가 열려 있고 앱 MCP가 3D_Modeling/ 열기를 거부할 때)
    cp 3D_Modeling/FSAP_v2.30.8.sc <작업 폴더>/base_v2308.sc
    python -X utf8 -B sworker.py 41080 base_v2308.sc      # 열기 370 s, 로컬 TCP로 요청을 받는다(q.py)
    q.py: edit.checkpoint · motion.play REST 0 · component.list -> r_complist.json · joint.list -> r_jlist.json
    pre1.py · pre2.py · pre3.py   사전 측정(보 속 면 광선, 빗 · 클램프 면, 지울 탭 둘레, 덮개 볼트 바깥)

1. build.py A   보(U1_FRAME 활성): 관통 탭 19(M4 Ø3.3 x8, M5 Ø4.2 x11) · 빈 M5 탭 4 메움(Ø4.8 join) ·
                옛 +X 끝 자리 메움 상자(X 1221~1231) 뒤 속 윤곽 스케치 SK_M07_BEAM_IN 으로 전 길이 자름(끝판 2 + 속 막 1 + 속으로 나온 메움 원통 끝)
                · 덮개 볼트 구멍 Ø5.5 x8(끝에서 18, Z 350 · 550) / 이음판 P_M07_SPLICE_NX · PX: 머리 구멍 Ø10 x2씩
2. b0~b3.json   덮개 P_M07_BEAM_CAP: 스케치(Z 262 평면, U자 3선) -> sheet.flange contour(SUS304_t3, 길이 376) -> sheet.tab(웹 위 · 아래 3.5)
                -> M5 탭 Ø4.2 x4 -> 재질 SUS304 -> component.create/move_bodies -> occurrence.copy + occurrence.move(Z 둘레 180도, +X 끝) -> joint.rigid_group
   b5.json      탭 옆 릴리프 4(굽힘 끝선에서 3 = t)
3. capbolts.py  component.paste_new(CB5-12_RX05_BEAM -> CB5-12_M07_CAP) + occurrence.copy x7 + occurrence.move + joint.rigid_group
4. combs.py lips  관 빗 11: 앞면을 Y 120.2 까지(ABC) 또는 밑 받침 살 t5(DE) + 턱 Y 120.2~123.8 · Z 647~650.1
   combs.py mats  26품번 material.assign PET-CF
5. bolts.py comb  CB5-16_M08_NZ_COMB 11 -> CB5-20_M08_NZ_COMB(실물 CB5-20 바디로 바꿔 끼움)
   bolts.py hmi   CB5-16_M08_PY:4~7 -> CB5-20_DP2:7~10 / bolts.py lbrk  CB5-16_M08_PY:3 -> STEP대기_CB5-14_DP2:8
   bolts.py cb4   CB4-25_M08 4 -> STEP대기_CB4-30_M08(생크 5 늘림)
6. 저장 전     measure 전수 -> sigdiff.py, clr.py(바뀐 바디 x 주변 틈 · 겹침), chk2.py(새 탭 물림 · 턱 +-5도), sheet.flat_pattern, export + stepinfo voids, joint.drive J_U5_X(사슬 팔 x 빗)
7. 저장        document.metadata.set description · motion.play REST 0 · browser.visibility joints/sketches false · save {path: FSAP_v2.31.0.sc}
8. 저장 뒤     solidcraft-cli run v_meas.json --in FSAP_v2.31.0.sc --results -> patch.py --write(ledger.py sigpatch: 서명 · 체결 목록 · mach_props)

수정 1회차(v2.31.0 -> v2.31.1, 검도 불합격 2건 + 예외 DP3-EX1 조건 3). 작업 폴더 tools/out/detail/DP-3/m1, 세션 포트 41081
    cp 3D_Modeling/FSAP_v2.31.0.sc <작업 폴더>/base_v2310.sc ; python -X utf8 -B sworker.py 41081 base_v2310.sc      # 열기 359.5 s
F1. fix1.py pre     edit.checkpoint · motion.play REST 0 · 빈 탭 6개 둘레 광선(쓰는 부품 없음) · 덮개 볼트 끝 앞 광선 · 보 측정
F2. fix1.py beam    보(U1_FRAME 활성): 뒷벽 탭 (1230, 300) · (1230, 600) 다시 뚫음(Ø4.2 cut, Y 320.1 -> 311.9, DP3F1_BEAM_TAP_PY_REOPEN_1 · 2)
                    + 빈 M5 탭 6 메움(Ø4.8 join 높이 8: 아랫벽 (-310 · -160, 140 · 180) Z 250~258, 앞벽 (-256 · -244, 276) Y 120~128, DP3F1_BEAM_FILL_NZ_3~6 · NY_3 · 4)
F3. fix1.py bolts   CB5-12_M07_CAP x8 -> CB5-16_M07_CAP(실물 CB5-16 바디로 바꿔 끼움: occurrence.copy CB5-16_M07_NY -> occurrence.move -> component.copy_bodies -> solid.remove 옛 바디 -> 이름 · 메타 -> 임시 occurrence 지움)
F4. fix1_chk.py measall topo joints insp thread static poses export   (검도와 같은 범위: 정적 9 x 332, 나사 129 x 5, J_U5_X · J_U4_X 5점씩 9 x 139, 보 구멍 축, 떠 있는 부품, 임시 STEP + stepinfo voids)
F5. fix1_save.py <FSAP_v2.31.1.sc>   덮개 · 문서 설명 · motion.play REST 0 · 표시 끔 · measure 전수 · save {path} 한 번
F6. solidcraft-cli run v_meas.json --in FSAP_v2.31.1.sc --results -> fix1_patch.py v_meas_out.json --write(ledger.py sigpatch) ; mkbom_made_fix1.py(가공 BOM 4행)
"""
if __name__ == '__main__':
    print(__doc__)
