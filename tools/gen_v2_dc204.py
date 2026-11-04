# -*- coding: utf-8 -*-
"""DC2-04 매트 두께 높이 사슬 생성기 — 기준 3D_Modeling/FSAP_v2.3.0.sc -> 3D_Modeling/FSAP_v2.3.1.sc (모델링부 2026-11-04)
설계안 docs/reports/mechanism/mech_DC2-04_design.md + 모델링 지시서.
python -X utf8 -B tools/gen_v2_dc204.py           -> tools/out/mech_DC2-04/edit.json (v2.3.0에 돌리는 명령 기록)
python -X utf8 -B tools/gen_v2_dc204.py --check   -> tools/out/mech_DC2-04/model/trial.json (기록 + 저장 전 검사, 저장 안 함)
python -X utf8 -B tools/gen_v2_dc204.py --machine -> tools/machine.json 고침
좌표: 바늘점 원점, 테이블 면 Z 0, 세계 mm. h = 매트 두께 - 10.
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC2-04").replace("\\", "/")
BASE, HOLDER = "P_M06_BASE", "P_M05_HOLDER"
BOLTS = ["CB5-12_M06_1", "CB5-12_M06_2", "CB5-12_M05_11", "CB5-12_M05_12"]


def C(cmd, **p):
    return {"command": cmd, "params": p}


def XZ(y):
    return {"origin": [0, y, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}   # 법선 -Y, (u, v) = (X, Z)


def slot_cut(name, y, slots, dist, body):
    s = [C("sketch.create", plane=XZ(y), name=name)]
    s += [C("sketch.slot.center_to_center", p0=[x, z0], p1=[x, z1], width=5.5) for x, z0, z1 in slots]
    s.append(C("sketch.finish"))
    s.append(C("solid.extrude", sketch=name, distance=dist, operation="cut", targets=[body]))
    return s


def zb(d):
    r = math.radians(d)
    return 70 + 200 * math.sin(r) - 60 * math.cos(r) - 12.5 * abs(math.sin(r))


def th(t):
    lo, hi = -5.0, 9.0
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if zb(m) < t else (lo, m)
    return round(m, 4)


# ---------------------------------------------------------------- 기록
def st_slots():
    # 1) BASE 붙임면(Y -93~-90) Ø5.5 2 -> 세로 장공 중심선 Z 174~184
    s = slot_cut("SK_DC204_BASE_SLOT", -89, [(-70, 174, 184), (-32, 174, 184)], 5, BASE)
    # 2) HOLDER 날개 A(Y -94~-90) Ø5.5 2 -> 세로 장공 중심선 Z 304~314
    s += slot_cut("SK_DC204_HOLDER_SLOT", -89.9, [(18, 304, 314), (36, 304, 314)], 4.2, HOLDER)
    return s


def st_joints():
    s = [C("joint.delete", joint="Rigid Group 2:14"),      # U1_FRAME:1 <-> U6_SENSOR:1
         C("joint.delete", joint="Rigid Group 8:4719")]    # U3_HEAD:1 <-> U7_FIXED:1
    # 볼트는 UPPER 탭에 물린다 -> U3_HEAD로 (M-07)
    s += [C("occurrence.reparent", occurrence=b + ":1", parent="U3_HEAD") for b in BOLTS]
    s += [C("joint.create", type="slider", name="J_U6_HGT", flip=True, quiet=True, limits=[[-4, 6]], values=[0],
            a={"occurrence": "U3_HEAD:1", "point": [-51, -90, 180], "z": [0, 0, 1]},
            b={"occurrence": "U6_SENSOR:1", "point": [-51, -90, 180], "z": [0, 0, 1]}),
          C("joint.create", type="slider", name="J_U7_HGT", flip=True, quiet=True, limits=[[-4, 6]], values=[0],
            a={"occurrence": "U3_HEAD:1", "point": [27, -90, 310], "z": [0, 0, 1]},
            b={"occurrence": "U7_FIXED:1", "point": [27, -90, 310], "z": [0, 0, 1]}),
          C("joint.drive", joint="J_U6_HGT", value=0, quiet=True),
          C("joint.drive", joint="J_U7_HGT", value=0, quiet=True)]
    # 4) 노루발 하한 -4, 5) 바늘 +6 · 범위 -36~0
    s += [C("joint.limits", joint="J_U3_PRESSER", min=-4, max=20),
          C("solid.move", bodies=["U3_NEEDLE_PIN"], translate=[0, 0, 6]),
          C("joint.limits", joint="J_U3_NEEDLE", min=-36, max=0)]
    return s


def st_final():
    return [C("motion.play", study="REST", step=0, quiet=True),
            C("browser.visibility", visible=False, folder="joints"),
            C("document.metadata.set", key="description",
              value="DC2-04 mechanism: mat thickness 6-16 height chain, U6/U7 vertical slots and setup sliders, presser -4, needle +6")]


def build():
    return st_slots() + st_joints() + st_final()


# ---------------------------------------------------------------- 저장 전 검사
def lists():
    s = json.load(open(ROOT + "/out/signatures.json", encoding="utf-8"))
    P = list(s["parts"].values())
    mov = [p["name"] for p in P if p["unit"] in ("U6_SENSOR", "U6_SHOE", "U7_TAPE") and p["name"] not in BOLTS]
    head = ["P_M01_FOOT", "U3_NEEDLE_PIN"]
    ag = [p["name"] for p in P if p["unit"] not in ("U2_TABLE", "WP", "U6_SENSOR", "U6_SHOE", "U7_TAPE")
          and p["name"] not in head and p["bbox"][4] < 700] + BOLTS
    u45 = [p["name"] for p in P if p["unit"] in ("U4_WHEEL_N", "U5_WHEEL_F")]
    return mov, head, ag, u45


def check():
    mov, head, ag, u45 = lists()
    seq, idx = [], []

    def add(tag, cmd):
        idx.append((len(seq), tag)); seq.append(cmd)

    def drv(j, v):
        seq.append(C("joint.drive", joint=j, value=v, quiet=True))

    MEAS = [BASE, "P_M06_CARR", "P_M06_SHOE", "CJ2B16-60SZ_M06", HOLDER, "P_M05_CST_PLATE", "U7_BINDER", "P_M05_GUIDE"] + BOLTS
    seq += build()
    add("joint.list", C("joint.list"))
    add("REST meas", C("inspect.measure", bodies=MEAS + head))
    # 조인트 자기 점검: 한계 밖으로 몰아 멈추는지
    drv("J_U6_HGT", 9); drv("J_U7_HGT", 9)
    add("HGT 9 -> clamp", C("inspect.measure", bodies=MEAS))
    drv("J_U6_HGT", -9); drv("J_U7_HGT", -9)
    add("HGT -9 -> clamp", C("inspect.measure", bodies=MEAS))
    drv("J_U3_PRESSER", -10); drv("J_U3_NEEDLE", -50)
    add("PRESSER -10 / NEEDLE -50 -> clamp", C("inspect.measure", bodies=head))
    add("NEEDLE -36 vs fixed", C("inspect.clearance", bodies=["U3_NEEDLE_PIN"], against=ag, clearance=1, nearest=1))
    drv("J_U3_PRESSER", 20); drv("J_U3_NEEDLE", 0)
    add("NEEDLE 0 vs fixed", C("inspect.clearance", bodies=["U3_NEEDLE_PIN"], against=ag, clearance=10, nearest=3))
    # HGT 0·25·50·75·100 % (REST 자세)
    for h in (-4, -1.5, 1, 3.5, 6):
        drv("J_U6_HGT", h); drv("J_U7_HGT", h)
        add("REST HGT %+g" % h, C("inspect.clearance", bodies=mov + head, against=ag, clearance=1, nearest=1))
        if h in (-4, 6):
            add("bolts HGT %+g" % h, C("inspect.clearance", bodies=BOLTS, against=[BASE, HOLDER], clearance=0.5, nearest=1))
    # THICK_6 · THICK_16 (+ 칼·접기 15, 앞끝 보내기 150)
    for nm, h, pres, u4, u5 in (("THICK_6", -4, -4, -0.54, -2), ("THICK_16", 6, 6, 2.4289, 8)):
        t = 10 + h
        slab = "S_T%d" % t
        drv("J_U6_HGT", h); drv("J_U7_HGT", h); drv("J_U6_SHIFT", 0); drv("J_U3_PRESSER", pres)
        drv("J_U4_PRESS", u4); drv("J_U5_X", 800); drv("J_U5_LIFT", u5)
        seq.append(C("solid.box", length=2500, width=1600, height=t + 2, corner=[-2100, -1100, 0], operation="new", body_name=slab))
        add(nm + " moved-vs-fixed", C("inspect.clearance", bodies=mov + head, against=ag, clearance=1, nearest=1))
        add(nm + " slab", C("inspect.clearance", bodies=[slab], against=mov + head + u45, clearance=3, nearest=1))
        add(nm + " meas", C("inspect.measure", bodies=["P_M02_WHEEL_TREAD", "P_M03_WHEEL_TREAD", "P_M01_FOOT", "P_M06_SHOE", "U7_BINDER", "U3_NEEDLE_PIN"]))
        drv("J_U7_CUT", 15); drv("J_U7_TUCK", 15)
        add(nm + " CUT/TUCK15", C("inspect.clearance", bodies=mov + head, against=ag, clearance=1, nearest=1))
        drv("J_U7_CUT", 0); drv("J_U7_TUCK", 0); drv("J_U3_PRESSER", 20); drv("J_U7_FEED", 150)
        add(nm + " FEED150", C("inspect.clearance", bodies=mov + head, against=ag, clearance=1, nearest=1))
        drv("J_U7_FEED", 0)
        seq.append(C("solid.remove", bodies=[slab]))
    drv("J_U6_HGT", 0); drv("J_U7_HGT", 0)
    seq.append(C("motion.play", study="REST", step=0, quiet=True))
    add("final joint.list", C("joint.list"))
    add("final meas", C("inspect.measure", bodies=MEAS + head))
    os.makedirs(OUT + "/model", exist_ok=True)
    json.dump(seq, open(OUT + "/model/trial.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"idx": idx, "mov": len(mov), "ag": len(ag)}, open(OUT + "/model/trial_idx.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("trial", len(seq), "mov", len(mov), "ag", len(ag))


# ---------------------------------------------------------------- 기계 정의(E-15)
def gen_machine():
    m = json.load(open(ROOT + "/machine.json", encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.3.1.sc"
    J = m["joints"]
    note = "DC2-04(v2.3.1) 제품 교체 때 손 조정, 값 = 매트 두께 - 10, 두 조인트(J_U6_HGT·J_U7_HGT)는 같은 값, 기계 축 아님, 사이클 연구에서 움직이지 않음. "
    J["J_U6_HGT"] = {"cad": "J_U6_HGT", "type": "slide", "unit": "U6_SHOE", "axis": [0, 0, 1], "origin": [-51, -90, 180],
                     "min": -4, "max": 6, "rest": 0, "setup": True,
                     "_note": note + "U6_SENSOR 통째(BASE·실린더·캐리지·슈·센서)가 U3_HEAD(UPPER -Y 면)에 대해 +Z. P_M06_BASE 붙임면 세로 장공 5.5(중심선 Z 174~184) + CB5-12_M06_1·2(U3_HEAD 쪽, UPPER 탭). 행정 끝 = 장공 끝(조인트 한계)"}
    J["J_U7_HGT"] = {"cad": "J_U7_HGT", "type": "slide", "unit": "U7_TAPE", "axis": [0, 0, 1], "origin": [27, -90, 310],
                     "min": -4, "max": 6, "rest": 0, "setup": True,
                     "_note": note + "U7_FIXED 통째(걸이 P_M05_HOLDER + 카세트 묶음)가 U3_HEAD에 대해 +Z. 날개 A 세로 장공 5.5(중심선 Z 304~314) + CB5-12_M05_11·12(U3_HEAD 쪽, UPPER 탭). 행정 끝 = 장공 끝(조인트 한계)"}
    J["J_U3_PRESSER"]["min"] = -4
    J["J_U3_PRESSER"]["_note"] = ("0 = 발바닥 Z 12(두께 10 이음매), 봉제 값 = h(매트 두께 - 10): -4 = Z 8(두께 6 이음매), 6 = Z 18(두께 16 이음매), "
                                  "20 = 들림(867 공식 PDF, 임시 C-25). DC2-04(v2.3.1) 하한 0 -> -4. 컴포넌트 U3_PRESSER = P_M01_FOOT(M01, v2.0.2). "
                                  "실제 헤드가 봉제 높이 8~18을 받는지는 D-10")
    J["J_U3_NEEDLE"]["min"] = -36
    J["J_U3_NEEDLE"]["_note"] = ("DC2-04(v2.3.1) 바늘 형상 +6(U3_NEEDLE_PIN Z 19~116): 0 = 위 끝(바늘 끝 Z 19, 두께 16 이음매 18 위 1), "
                                 "-36 = 아래 끝(끝 Z -17, 예전과 같음). 지금 연구의 -30 키는 끝 Z -11(테이블 밑, 매트를 꿰뚫음)이라 그대로. "
                                 "컴포넌트 U3_NEEDLE = U3_NEEDLE_PIN. 바늘대 위 끝·행정은 헤드 사양(D-10)")
    keys = {6: -1.0815, 7: -0.8105, 8: -0.5400, 11: 0.3053, 12: 0.6101, 16: 1.8245, 17: 2.1269, 18: 2.4289}
    J["J_U4_PRESS"]["_note"] = ("M02(v2.1.0) 핀 스윙 레버(U4_PRESS) 회전, + = 들림. 8.626 = 들림 끝(조인트 한계; 실린더 후퇴 끝 8.6265가 스토퍼, 바퀴 밑 38.8), "
                                "-1.867 = 실린더 나옴 끝(바퀴 밑 3.11). 작동(접촉 추종, DC2-04 바로잡음): 바퀴 밑 z = 70 + 200·sinθ − 60·cosθ − 12.5·|sinθ| "
                                "(레버 핀 (-300, 0, 70), 바퀴 중심 반지름 200, 바퀴 r 60, 반폭 12.5) — 0 = z 10. 키 표 keys_z(목표 z -> θ°). "
                                "실린더 CDM2C20-25Z(J_U4_CYL_PIN·J_U4_CYL_ROD·J_U4_ROD_PIN 닫힌 고리)가 따라감")
    J["J_U4_PRESS"]["keys_z"] = {str(k): v for k, v in keys.items()}
    m["temp_values"]["D-04"] = "매트 두께 범위 6~16(임시, DC2-04 — 근거 없음, 승용차 카펫 매트 통상 범위 자리값). 모형은 두께 10"
    # 상태
    m["states"] = [s for s in m["states"] if s.get("name") not in ("THICK_6", "THICK_16")]
    rest = dict(next(s for s in m["states"] if s["study"] == "REST" and s["step"] == 0)["joints"])
    for s in m["states"]:
        s["joints"].setdefault("J_U6_HGT", 0)
        s["joints"].setdefault("J_U7_HGT", 0)
    for nm, h, pres, u4, lift, t in (("THICK_6", -4, -4, -0.5400, -2, 6), ("THICK_16", 6, 6, 2.4289, 8, 16)):
        j = dict(rest)
        j.update({"J_U6_HGT": h, "J_U7_HGT": h, "J_U3_PRESSER": pres, "J_U4_PRESS": u4, "J_U5_X": 800, "J_U5_LIFT": lift, "J_U6_SHIFT": 0})
        m["states"].append({"name": nm, "study": "REST", "step": 0, "joints": j, "phase": "DC2-04 두께 범위 끝 봉제 자세",
                            "workpiece": {"stage": "band", "_note": "이음매 윗면 접촉 봉제 자세: 두께 %d 매트 띠 Z 0~%d(이음매 윗면) 위에 노루발·두 바퀴 접촉, 슈 작동. "
                                                                   "모형은 두께 10 그대로 — 검사는 띠를 만들어 잼(저장 안 함)" % (t, t + 2)}})
    # 기준선(M00-X6)
    new = "접촉 추종(J_U4_PRESS θ(z) 식, J_U5_LIFT = z − 10)으로 겹침 0, 맞닿음(부피 0)만 허용 — DC2-04 측정 6자세 최소 틈 0.002~0.134"
    for b in m["baseline_overlaps"]:
        if b["a"].startswith("U4_WHEEL") and ("WP_TAPE" in b["b"]):
            b["reason"] = new + " (M00-X6 정리, 옛 '깊이 1.0 mm, 부피 0' 줄)"
        if b["a"].startswith("U4_WHEEL(P_M02") and "SEAM" in b["b"]:
            b["reason"] = new + " (M00-X6 정리, 옛 '남으면 키 0.310' 줄)"
    u = m["units"]
    u["U6_SENSOR"]["parts"] = [p for p in u["U6_SENSOR"]["parts"] if p not in BOLTS]
    u["U6_SENSOR"]["components"] = [p for p in u["U6_SENSOR"]["components"] if p not in BOLTS]
    u["U6_SENSOR"]["moving"] = True
    u["U6_SENSOR"]["joints"] = ["J_U6_HGT"]
    u["U6_SENSOR"]["_note"] = u["U6_SENSOR"]["_note"].replace("U1_FRAME 리지드", "") + \
        " DC2-04(v2.3.1): U1_FRAME 리지드 지움 -> J_U6_HGT(U3_HEAD에 대해 Z, 손 조정). CB5-12_M06_1·2는 U3_HEAD로 옮김"
    for b in ("CB5-12_M06_", "CB5-12_M05_11", "CB5-12_M05_12"):
        if b not in u["U3_HEAD"]["parts"]:
            u["U3_HEAD"]["parts"].append(b)
    u["U3_HEAD"]["_note"] += " DC2-04(v2.3.1): 높이 조절 장공 볼트 CB5-12_M06_1·2·CB5-12_M05_11·12를 U3_HEAD로(UPPER 탭에 물림)"
    u["U7_TAPE"].setdefault("joints_setup", ["J_U7_HGT"])
    u["U7_TAPE"]["_note"] += " DC2-04(v2.3.1): U7_FIXED↔U3_HEAD 리지드 지움 -> J_U7_HGT(Z 손 조정). CB5-12_M05_11·12는 U3_HEAD로"
    json.dump(m, open(ROOT + "/machine.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("machine.json", len(J), "joints", len(m["states"]), "states")


if __name__ == "__main__":
    if "--machine" in sys.argv:
        gen_machine()
    elif "--check" in sys.argv:
        check()
    else:
        s = build()
        json.dump(s, open(OUT + "/edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        json.dump({"base": "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/3D_Modeling/FSAP_v2.3.0.sc",
                   "result": "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/3D_Modeling/FSAP_v2.3.1.sc",
                   "generator": "tools/gen_v2_dc204.py"}, open(OUT + "/edit_meta.json", "w", encoding="utf-8"), indent=1)
        print(len(s), "commands")
