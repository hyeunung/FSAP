# 재실행 확인부 — 2026-11-04

요약
- 시험: mech_M00 기록(edit.json 61단계)을 FSAP_v2.0.0.sc 복사본(tools/out/replay_check/base.sc)에 CLI `run`으로 다시 실행 → replay.sc.
- 비교: 저장본 FSAP_v2.0.1.sc와 바디 44/44 이름·부피·bbox 모두 일치. ok=true.
- 확인된 명령 종류: solid.box, solid.cylinder, component.move_bodies, joint.drive, joint.limits, motion.play, browser.visibility.
- 미확인(안내서 '확인 전 기본 금지', solidcraft.md '편집 명령 기록·다시 실행' 원문 "확인 전 기본 금지: file.insert_step, 면을 좌표로 집는 solid.offset_face·solid.fillet·solid.chamfer, component.activate, 타임라인 삭제"): file.insert_step, solid.offset_face, solid.fillet, solid.chamfer, component.activate, 타임라인 삭제 — 이 종류를 쓰는 과제(DC2-01·DC2-03·DC2-05·M05 가운데)는 묶음에서 빼고 직렬로.
- 원본 파일은 바꾸지 않음. 결과 tools/out/replay_check.json, 작업 파일 tools/out/replay_check/.

## 워크플로우 메모
- M00 기록에 STEP 넣기·면 집기 명령이 없어 위험 종류는 이번에 확인하지 못했다. 다음 직렬 과제가 그런 명령을 쓴 기록을 남기면 그것으로 다시 확인한다.
