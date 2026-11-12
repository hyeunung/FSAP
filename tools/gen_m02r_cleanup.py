# -*- coding: utf-8 -*-
"""M02R 잔재 정리 생성기 (v2.13.0 -> v2.14.0).

같은 형상을 다시 만들 수 있게 남기는 명령 생성기다(실행 규칙 3).
  python -B tools/gen_m02r_cleanup.py
가 tools/out/mech_M02R/model6/stage_*.json 과 tools/out/mech_M02R/edit.json,
edit_meta.json 을 다시 쓴다.

하는 일
 1) 스프링 탭 볼트 CB5-12_M02S_BASE_5~8 을 X s+-7 -> s+-12 (s = -295, -185),
    탭 P_M02S_SPRING_TAB_1/_2 날개를 X s+-12 -> s+-16.5, 탭 볼트 구멍과
    P_M02_BASE M5 탭 4개를 같은 자리로(피처 정의를 고쳐 메운 자국이 없다).
 2) 옛 크랭크 U4 빈 컴포넌트 21개(+ CB5-12_M02_2) 지우기.
 3) 팔(ARM_SIDE_N/_P, ARM_TIE)에 떨어진 조각: 들림 자세(13.006도)에서 th0 좌표로
    만들어져 빗나간 메움·탭 피처를 th0 좌표(= U4_PRESS 로컬)로 바로잡고,
    탭이 없는 ARM_TIE 메움 2개는 지운다.

큰 파일에서는 피처 하나를 고칠 때마다 그 뒤 피처 전부를 다시 계산한다
(v2.13.0: 꼬리 235개 130 s, 전체 약 19분). 그래서 타임라인 마커를 가장 앞
피처(위치 277) 앞으로 내려 놓고 고침·지우기를 모두 한 뒤 한 번만 끝까지 올린다.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_M02R")
STAGE = os.path.join(OUT, "model6")
BASE = "3D_Modeling/FSAP_v2.13.0.sc"
RESULT = "3D_Modeling/FSAP_v2.14.0.sc"
DOC_NAME = "FSAP_v2.14.0"


def E(feature, fields):
    return {"command": "timeline.edit", "params": {"feature": feature, "set": fields}}


def C(command, **params):
    return {"command": command, "params": params}


# --- 1) 볼트 4개: 리지드 조인트를 풀고 옮긴 뒤 다시 묶는다(마커가 끝에 있을 때) ---
BOLTS = [("CB5-12_M02S_BASE_5:1", 97861, -5), ("CB5-12_M02S_BASE_6:1", 97862, 5),
         ("CB5-12_M02S_BASE_7:1", 97863, -5), ("CB5-12_M02S_BASE_8:1", 97864, 5)]
stage_0 = [E(97729, {"corner": [-311.5, 40, 238], "length": "33"})]  # 탭 1 날개 판
stage_0 += [C("joint.delete", joint=j) for _, j, _ in BOLTS]
stage_0 += [C("occurrence.move", occurrence=o, space="world", translate=[dx, 0, 0])
            for o, _, dx in BOLTS]
stage_0 += [C("joint.rigid_group",
              occurrences=["U4_WHEEL_N:1"] + [o for o, _, _ in BOLTS])]

# --- 마커를 CDM2C20-25Z import(위치 277) 앞으로 ---
stage_1 = [C("timeline.rollback", position=277)]

# --- 2) 피처 정의 고침(마커 뒤라 다시 계산하지 않는다) ---
stage_2 = [
    # 탭 1 볼트 구멍, 탭 2 날개 판·볼트 구멍
    E(97732, {"base": [-307, 50, 237.9]}), E(97733, {"base": [-283, 50, 237.9]}),
    E(97740, {"corner": [-201.5, 40, 238], "length": "33"}),
    E(97743, {"base": [-197, 50, 237.9]}), E(97744, {"base": [-173, 50, 237.9]}),
    # P_M02_BASE M5 탭 4개
    E(97686, {"base": [-307, 50, 241.9]}), E(97687, {"base": [-283, 50, 241.9]}),
    E(97688, {"base": [-197, 50, 241.9]}), E(97689, {"base": [-173, 50, 241.9]}),
    # 팔 옆판 메움(th0 좌표): r 4.5 구멍(X -160, Z 122), 옛 부시 구멍 r 9(X -300, Z 70)
    E(97613, {"base": [-160, -37, 122], "axis": [0, 1, 0]}),
    E(97614, {"base": [-160, 31, 122], "axis": [0, 1, 0]}),
    E(97678, {"base": [-300, -37, 70], "axis": [0, 1, 0]}),
    E(97679, {"base": [-300, 31, 70], "axis": [0, 1, 0]}),
    # 옆판 P 의 그네 볼트 M5 탭 2개(CB5-16_M02S_1·_2 자리)
    E(97692, {"base": [-300, 37.1, 100], "axis": [0, -1, 0]}),
    E(97693, {"base": [-166, 37.1, 120], "axis": [0, -1, 0]}),
    # ARM_TIE 크랭크 탭 메움 2개: 탭이 없어 떨어진 조각만 만든다 -> 지움
    C("timeline.delete", features=[97680, 97681]),
]

# --- 3) 옛 U4C 관(스케치·파이프·옮김)과 옛 바디를 지운 Remove83 ---
stage_3 = [C("timeline.delete",
             features=[97620, 97621, 97622, 97625, 97626, 97627, 97670])]

# --- 4) 빈 컴포넌트: 맨 위 묶음 13개(밑 8개 포함 21개) + CB5-12_M02_2 ---
EMPTY = ["CB5-16_M02_10", "CDM2C20-25Z", "I-020B_M02", "CB5-16_M02R_1", "CB5-16_M02R_2",
         "CB5-16_M02R_3", "CB5-16_M02R_4", "CB5-20_M02R_1", "CB5-20_M02R_2",
         "CB4-12_M02R_CLV", "CB4-12_M02R_CRK", "CB4-12_M02_PIV", "CB5-12_M02_PIV"]
stage_4 = [C("component.delete", component=c) for c in EMPTY]
stage_4 += [E(97544, {"bodies": ["P_M02_CYLBRKT", "CB5-12_M02_1"]}),
            C("component.delete", component="CB5-12_M02_2")]

# --- 5) 한 번에 끝까지 다시 계산(약 19분, 응답이 끊겨도 앱은 계속 돈다) ---
stage_5 = [C("timeline.rollback", position="end")]

# --- 6) 저장 전: 이름·숨김·대기 자세 ---
stage_6 = [
    C("motion.play", study="REST", step=0, quiet=True),
    C("browser.visibility", visible=False, folder="joints"),
    C("browser.visibility", visible=False, folder="sketches"),
    C("component.rename", component=0, name=DOC_NAME),  # 문서 이름 = 루트 컴포넌트 이름
]

STAGES = [("stage_0_bolts_tab1", stage_0), ("stage_1_rollback", stage_1),
          ("stage_2_edits", stage_2), ("stage_3_tldelete", stage_3),
          ("stage_4_compdelete", stage_4), ("stage_5_rollend", stage_5),
          ("stage_6_presave", stage_6)]


def main():
    os.makedirs(STAGE, exist_ok=True)
    allc = []
    for name, cmds in STAGES:
        with open(os.path.join(STAGE, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(cmds, f, ensure_ascii=False, indent=0)
        allc += cmds
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8") as f:
        json.dump(allc, f, ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"base": BASE, "result": RESULT,
                   "note": "M02R 잔재 정리. 앱(MCP)에서 stage_0~6 순서로 실행. "
                           "옛 기록은 edit_v2103.json·edit_meta_v2103.json"},
                  f, ensure_ascii=False, indent=1)
    print("stages", len(STAGES), "commands", len(allc))


if __name__ == "__main__":
    main()
