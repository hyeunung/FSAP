# -*- coding: utf-8 -*-
"""v2.0 기계 정의 tools/machine.json 생성기(준비부 2026-11-03). gen_v2_prep.py를 먼저 돌려 out/prep_v2/paths.json이 있어야 한다.

python -X utf8 -B tools/gen_v2_machine.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gen_v2_prep as G

P = json.load(open(os.path.join(ROOT, "out", "prep_v2", "paths.json"), encoding="utf-8"))["paths"]


def jv(k, nm, step):
    """paths.json 자세 → 조인트 값(연구 키와 같은 셈)."""
    z = P[nm]["poses"][step]
    cp = G.park_c(k)
    v = {"J_U3_PRESSER": z["pr"], "J_U3_NEEDLE": z["nd"], "J_U4_PRESS": z["np"], "J_U4_WHEEL_ROT": round(z["rn"], 3),
         "J_U5_X": z["fx"], "J_U5_LIFT": z["fl"], "J_U5_WHEEL_ROT": round(z["rf"], 3),
         "J_WP_%s_X" % k: round(z["cx"] - cp[0], 4), "J_WP_%s_Y" % k: round(z["cy"] - cp[1], 4), "J_WP_%s_ROT" % k: round(z["th"], 4)}
    return v, z["ph"]


def st(name, k, nm, step, stage, note=None):
    v, ph = jv(k, nm, step)
    d = {"name": name, "study": "CYCLE_" + nm, "step": step, "joints": v, "phase": ph,
         "workpiece": {"mat": "WP_MAT_%s:1" % k, "tape": "WP_TAPE_%s:1" % k, "stage": stage}}
    if note:
        d["_note"] = note
    return d


def main():
    S = G.LIFT
    joints = {
        "J_U3_PRESSER": {"cad": "J_U3_PRESSER", "type": "slide", "unit": "U3_HEAD", "axis": [0, 0, 1], "origin": [0, 0, 0], "rest": G.PRESSER_UP, "min": 0, "max": G.PRESSER_UP,
                         "_note": "0 = 내림(봉제), 20 = 들림(0-8-5 867 공식 PDF, 임시 C-25). 컴포넌트 U3_PRESSER는 비어 있음 — M00/M01이 노루발 바디를 값 0(내림) 자세 좌표로 넣는다"},
        "J_U3_NEEDLE": {"cad": "J_U3_NEEDLE", "type": "slide", "unit": "U3_HEAD", "axis": [0, 0, 1], "origin": [0, 0, 0], "rest": 0, "min": G.NEEDLE_DOWN, "max": 0,
                        "_note": "0 = 바늘 위, -30 = 꽂음(D-10 자리값 '바늘 내림 30', 근거 없음). 컴포넌트 U3_NEEDLE 비어 있음 — M01이 값 0 자세로 넣는다"},
        "J_U4_PRESS": {"cad": "J_U4_PRESS", "type": "slide", "unit": "U4_WHEEL_N", "axis": [0, 0, 1], "origin": [-G.D1, 0, G.T + G.WR], "rest": S, "min": 0, "max": S,
                       "_note": "바늘 옆 바퀴 누름·들기. 0 = 내림(바퀴 밑 = 매트 윗면 Z 10), 30 = 들림(D-104 임시). 실제는 핀 스윙 암 + 세로 실린더(D-99) — 준비부는 세로 슬라이더로 둠, M02가 스윙 암으로 바꿀 수 있다"},
        "J_U4_WHEEL_ROT": {"cad": "J_U4_WHEEL_ROT", "type": "rotate", "unit": "U4_WHEEL_N", "axis": [1, 0, 0], "origin": [-G.D1, 0, G.T + G.WR], "rest": 0, "min": -72000, "max": 72000,
                           "_note": "서보 바퀴 회전(+X 축, + = 바퀴 밑이 +Y로). 연구 값 = 바퀴 밑 매트 점의 Y 변위 / r 60(속도 v + w·d1). 형상이 바뀌지 않는 회전이라 간섭 검사에는 영향 없음"},
        "J_U5_X": {"cad": "J_U5_X", "type": "slide", "unit": "U5_WHEEL_F", "axis": [1, 0, 0], "origin": [-G.D2_PARK, 0, G.T + G.WR], "rest": 0, "min": 0, "max": G.D2_PARK - G.D2_MIN,
                   "_note": "먼 쪽 대차 X. d2(바늘–먼 쪽 바퀴) = 1800 - 값. 0 = 대기(d2 1800), 1500 = d2 300(D-105 임시: d2 ≥ 2·d1 + 바퀴 묶음 폭 100). 큰 매트 d2 1000(값 800), 홈 매트 d2 800(값 1000), 작은 매트 내리지 않음"},
        "J_U5_LIFT": {"cad": "J_U5_LIFT", "type": "slide", "unit": "U5_WHEEL_F", "axis": [0, 0, 1], "origin": [-G.D2_PARK, 0, G.T + G.WR], "rest": S, "min": 0, "max": S,
                      "_note": "먼 쪽 바퀴 승강. 0 = 내림, 30 = 들림(D-104). 바퀴 접촉선(폭 25)이 매트 밖이면 앞뒤 한 단계 여유로 든다(0-8-2 ③)"},
        "J_U5_WHEEL_ROT": {"cad": "J_U5_WHEEL_ROT", "type": "rotate", "unit": "U5_WHEEL_F", "axis": [1, 0, 0], "origin": "대차와 함께 움직임, 대기 때 (-1800, 0, 70)", "rest": 0, "min": -72000, "max": 72000,
                           "_note": "먼 쪽 서보 바퀴 회전. 값 = 바퀴 밑 매트 점의 Y 변위 / r 60(속도 v + w·d2)"},
    }
    for k in ("L", "S", "G"):
        cp = G.park_c(k)
        for ax, typ, axis in (("X", "slide", [1, 0, 0]), ("Y", "slide", [0, 1, 0]), ("ROT", "rotate", [0, 0, 1])):
            joints["J_WP_%s_%s" % (k, ax)] = {"cad": "J_WP_%s_%s" % (k, ax), "type": typ, "unit": "WP_" + k, "axis": axis,
                                               "origin": [cp[0], cp[1], 0], "rest": 0, "min": -3000 if ax != "ROT" else -360, "max": 3000 if ax != "ROT" else 720, "model_only": True,
                                               "_note": "작업 대상 모형 조인트(볼 위 평면 운동, 기계 축 아님 — 실행 규칙 20). 매트 중심 = 대기 중심 (%.1f, %.1f) + (X, Y), 회전은 그 중심" % cp}
    units = {
        "U1_FRAME": {"parts": ["U1_", "REF_"], "moving": False, "_note": "고정(접지). M00이 전폭 보·기둥 상자를 넣는다"},
        "U2_TABLE": {"parts": ["U2_"], "moving": False},
        "U3_HEAD": {"parts": ["U3_"], "moving": True, "components": ["U3_HEAD", "U3_PRESSER", "U3_NEEDLE"]},
        "U4_WHEEL_N": {"parts": ["U4_"], "moving": True, "components": ["U4_WHEEL_N", "U4_PRESS", "U4_WHEEL"]},
        "U5_WHEEL_F": {"parts": ["U5_"], "moving": True, "components": ["U5_WHEEL_F", "U5_CAR", "U5_LIFT", "U5_WHEEL"]},
        "U6_SENSOR": {"parts": ["U6_"], "moving": False, "_note": "슈 비키는 실린더 조인트는 M06"},
        "U7_TAPE": {"parts": ["U7_"], "moving": False},
        "U8_PNEU": {"parts": ["U8_"], "moving": False},
        "WP_L": {"parts": ["MAT_L", "TAPE_L", "SEAM_L"], "moving": True, "workpiece": True},
        "WP_S": {"parts": ["MAT_S", "TAPE_S", "SEAM_S"], "moving": True, "workpiece": True},
        "WP_G": {"parts": ["MAT_G", "TAPE_G", "SEAM_G"], "moving": True, "workpiece": True},
    }
    rest = {j: v["rest"] for j, v in joints.items()}
    states = [{"name": "대기", "study": "REST", "step": 0, "joints": rest, "phase": "① 대기·로딩",
               "workpiece": {"stage": "none_or_any", "_note": "매트 3장이 각자 로딩 자리(시작점에서 -Y 300)에 겹쳐 있다. 연구마다 한 장만 움직인다"}}]
    states += [
        st("큰 매트 로딩 끝(가장자리를 노루발 표시에)", "L", "L", 12, "before"),
        st("큰 매트 바퀴 내림·먼 쪽 대차 d2 1000", "L", "L", 50, "before"),
        st("큰 매트 직선 봉제 가운데", "L", "L", 65, "sewing"),
        st("큰 매트 볼록 모서리 45°", "L", "L", 127, "sewing"),
        st("큰 매트 볼록 모서리 끝 90°", "L", "L", 172, "sewing"),
        st("큰 매트 이음매 겹침 끝", "L", "L", 668, "after_seam"),
        st("큰 매트 배출", "L", "L", 716, "after"),
        st("작은 매트 바퀴 내림(먼 쪽 바퀴 대기)", "S", "S", 16, "before"),
        st("작은 매트 직선 봉제", "S", "S", 18, "sewing"),
        st("작은 매트 볼록 모서리 45°", "S", "S", 67, "sewing"),
        st("작은 매트 이음매 겹침 끝", "S", "S", 434, "after_seam"),
        st("작은 매트 배출", "S", "S", 450, "after"),
        st("홈 매트 홈 입구 회전 시작(바늘 옆 바퀴 들림)", "G", "G1", 90, "sewing"),
        st("홈 매트 홈 입구 회전 45°", "G", "G1", 133, "sewing"),
        st("홈 매트 홈 안 벽", "G", "G1", 195, "sewing"),
        st("홈 매트 홈 바닥 꺾임 가운데(가장 깊은 점, 오목)", "G", "G1", 300, "sewing"),
        st("홈 매트 홈 바닥 꺾임 끝(먼 쪽 바퀴 들림)", "G", "G1", 390, "sewing", "홈 건너편 매트 몸통이 바늘 +X 쪽으로 온다(헤드 밑을 지남, M01 합격 기준)"),
        st("홈 매트 두 번째 홈 입구 회전 45°", "G", "G1", 467, "sewing"),
        st("홈 매트 볼록 모서리 45°", "G", "G2", 75, "sewing"),
        st("홈 매트 이음매 겹침 끝", "G", "G2", 574, "after_seam"),
        st("홈 매트 배출", "G", "G2", 630, "after"),
    ]
    m = {
        "_설명": "FSAP MAT-RS-001 v2.0 기계 정의(엔진 E-15, 틀 templates/machine-definition.json). 준비부 2026-11-03. 움직임은 설계 파일의 조인트로만. 값: slide mm, rotate deg. 좌표: 바늘점 원점, 테이블 면 Z 0, 매트 이송 +Y, 작업자 -Y, 매트 몸통 -X(요구서 0-8-3). 생성기 tools/gen_v2_prep.py(설계 명령·연구) + tools/gen_v2_machine.py(이 파일)",
        "cad": "solidcraft", "doc": "../3D_Modeling/FSAP_v2.0.0.sc",
        "joints": joints, "units": units,
        "studies": {
            "REST": {"steps": 1, "_note": "대기 포즈(동작 상태 초기화 = motion.play REST step 0)"},
            "CYCLE_L": {"steps": P["L"]["steps"], "workpiece": ["WP_MAT_L:1", "WP_TAPE_L:1"], "mat": "1500x1500", "d2": G.D2["L"]},
            "CYCLE_S": {"steps": P["S"]["steps"], "workpiece": ["WP_MAT_S:1", "WP_TAPE_S:1"], "mat": "300x200", "d2": None, "_note": "먼 쪽 바퀴는 대기(들림, d2 1800)"},
            "CYCLE_G1": {"steps": P["G1"]["steps"], "workpiece": ["WP_MAT_G:1", "WP_TAPE_G:1"], "mat": "1200x1200 U홈 25x150 R12.5", "d2": G.D2["G"], "_note": "① ~ 두 번째 홈 입구 회전 끝. 홈 바닥 211~390"},
            "CYCLE_G2": {"steps": P["G2"]["steps"], "workpiece": ["WP_MAT_G:1", "WP_TAPE_G:1"], "mat": "1200x1200 U홈", "d2": G.D2["G"], "_note": "G1 끝 자세 ~ ⑤(1000단계 표본 상한 WF-126 때문에 둘로 나눔)"},
        },
        "workpiece_stages": {"_note": "SolidCraft는 작업 대상을 설계 안 바디로 둔다(안내서 '동작 검사'). WP_MAT_* = 가공 전 매트, WP_TAPE_* = 가공 뒤 형상(테이프 감긴 외곽 띠 TAPE_*, 두께 1·날개 10 + 이음매 겹 SEAM_* 30). stage: before = MAT만, sewing = MAT(+TAPE 보수적), after_seam·after = MAT + TAPE",
                             "fragments": "떨어지는 조각 없음 — 0-8-4 ⑤ 절단은 바인더 앞 한 번(앞끝은 바인더에 남고 US4688499, 끝은 접어 넣음 US6044783A). 실 끝은 헤드 내장 사절. 조각이 생기는 방식으로 바뀌면 M05가 모형을 넣는다(D-07)"},
        "states": states,
        "_states_note": "요구서 0-3 ①~⑤(0-8-4)와 6-4(직선, 볼록 모서리, 오목 모서리, 홈 입구, 홈 바닥 꺾임, 시작·끝 이음매)에 대응. 6-4 '오목 모서리'(계단형 날카로운 오목)는 매트 모형에 없다 — 홈 바닥 오목 반원(180° 왼쪽 꺾임)만 있다(mech_prep.md '못 한 것'). 연구 간격: 이송 25 mm, 홈 안·홈 입구 앞뒤 50 mm는 5 mm, 회전 1°, 노루발·바늘·바퀴 승강은 양 끝 + 가운데(요구서 6-4).",
        "baseline_overlaps": [
            {"a": "WP_MAT_*", "b": "WP_TAPE_* (같은 매트)", "reason": "테이프 띠가 매트 가장자리 10 mm를 덮는 모형(같이 움직임)"},
            {"a": "WP_*_L·S·G", "b": "다른 WP_*", "reason": "매트 3장이 로딩 자리에 겹쳐 있다. 연구마다 한 장만 검사"},
            {"a": "U4_WHEEL·U5_WHEEL", "b": "WP_MAT_* 윗면", "reason": "바퀴 내림 = 매트 윗면 Z 10 맞닿음(누름은 모델로 판정 안 함, 요구서 7절). CLI 확인 CYCLE_S·G1: 바퀴↔매트 겹침 0"},
            {"a": "U4_WHEEL·U5_WHEEL", "b": "WP_TAPE_* 띠(Z 10~11)", "reason": "바퀴가 이미 박은 테이프 띠·이음매 위를 지날 때 깊이 1.0 mm(테이프 두께) 겹침, 부피 0 — CYCLE_S 8구간, CYCLE_G1 바늘 옆 5구간·먼 쪽 177~183. 모서리 회전 때 바퀴가 다음 변 띠 위에 온다. 의도된 접촉 후보 — M02·M03가 판정(바퀴가 테이프 위를 눌러도 되는지 7절)"},
            {"a": "U3_NEEDLE", "b": "WP_* (바늘점 둘레)", "reason": "바늘이 매트를 꿰뚫는 의도된 겹침(M-08). M01이 바늘 바디를 넣으면 부피를 적는다"},
            {"a": "REF_NEEDLE_AXIS_MARK", "b": "-", "reason": "Ø2×1 표시점(Z -301). 점검에서 REF 건너뜀(config skip_tops)"},
        ],
        "workpiece_module": "", "_workpiece_note": "작업 대상 모형은 설계 안 바디(gen_v2_prep.py stage_2_workpiece). 크기 범위 양 끝 1500×1500·300×200 + 가장 좁은 홈 매트(D-01·D-02·D-03)",
        "state_hook": "", "_hook_note": "쓰지 않음(SolidCraft)",
        "path_parts": ["U2_", "U3_", "U4_", "U5_", "U6_", "U7_"],
        "_path_note": "매트가 지나가는 테이블 면(U2), 바늘 둘레 묶음(U3), 바퀴(U4·U5), 슈·센서(U6), 바인더·테이프 길(U7). 바뀌면 원장이 전체 검사로 넓힌다",
        "temp_values": {"D-01": "매트 300×200 ~ 1500×1500", "D-02·D-03": "U홈 폭 25·깊이 150·바닥 R12.5, 홈 매트 외곽 1200, 홈 자리 시작 변 가운데에서 300", "D-04": "매트 두께 10",
                        "D-06·D-07": "테이프 두께 1·날개 10, 이음매 겹침 30", "D-10": "노루발 들림 20, 바늘 내림 30", "D-93": "바퀴 Ø120×25", "D-99": "d1 100",
                        "D-104": "바퀴 들림 30, 접촉 길이 ±10(새)", "D-105": "대차 d2 300~1800, 대기 1800, 큰 매트 d2 1000·홈 매트 800·작은 매트 안 내림(새)",
                        "D-106": "로딩: 시작점에서 -Y 300 자리에 올려 +Y로 밀어 맞춤, 배출: 끝 자세에서 -Y 300(새)"},
    }
    json.dump(m, open(os.path.join(ROOT, "machine.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("states", len(states), "joints", len(joints))


if __name__ == "__main__":
    main()
