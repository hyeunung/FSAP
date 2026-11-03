# -*- coding: utf-8 -*-
"""N04 사슬 앞끝·꼬리 멈춤·안쪽 끝 막대 연구 키 생성기 (모델링부 2026-11-03, N04 수정 1·2회차, 결정로그 N04-E01·E03·E05·E07)
수정 2회차: 앞끝 Yc +- 81.5, 열림 +-55(실린더 행정 110), 막대 NP = min(62, Yc-76), PN = max(-62, Yc+76),
  J_N04_BAR_NP = NP - 62, J_N04_BAR_PN = PN + 62, J_N04_CH_N = N 앞끝 + 481.5, L_f는 하드 리밋 포함. 출력 model2/
입력: tools/out/mech_N04/model1/motion_list_v1.0.12.json (설계의 motion.list 결과, 키 joint id 11 = J_U4_X, 12 = J_U4_Y)
출력: tools/out/mech_N04/model1/chain_keys.json  {L_f, studies: {이름: {steps, values: {joint: [[step, v]...]}}}, commands}
      tools/out/mech_N04/model1/stage_keys.json   motion.study {study, keys} 명령 배열

식(테이블 좌표 = 월드 - J_U4_X, Y는 월드 그대로, 선정 mech_N04_select.md 2·8절, N04-Q2):
  Yc = -400 + J_U4_Y (원판 중심 Y), 안장 Y = Yc ± 70, 바깥 앞끝은 안장 끝에서 0.5 띄움(밀 때 틈 0~1)
  phaseL(s) = J_U4_X > 800 and |Yc| >= 200
  open(s)   = phaseL(s-1) or phaseL(s) or phaseL(s+1)  (Q2: 800 넘기 전 열고, 800 아래로 돌아온 뒤 닫음)
  바깥 P 앞끝 = max(Yc + 81.5, sP), sP = -55(닫힘) / +55(열림, 원판이 -Y 쪽일 때만 = 원판 반대쪽)  [수정 2회차]
  바깥 N 앞끝 = min(Yc - 81.5, sN), sN = +55(닫힘) / -55(열림, 원판이 +Y 쪽일 때만)
  A 앞끝 = -970(멈춤) / min(-831, -31 - J_U4_X)(따라감 = open, LOWER -X 면(월드 -30)에서 1 띄움)
  J_N04_CH_P = P 앞끝 + 55, J_N04_CH_N = N 앞끝 + 481.5, J_N04_CH_A = A 앞끝 + 970, BAR_NP = NP - 62, BAR_PN = PN + 62
  J_N04_STOP_P = 110 열림 / 0 닫힘 (로드가 꼬리를 -Y로 밀어 앞끝을 112 물림), N 거울
  J_N04_STOP_A = 150 - clamp(A 앞끝 + 970, 0, 150) (멈춤 = 150 내밀어 꼬리 붙잡음, 따라감 = 로드가 꼬리를 따라 물러남)
  L_f = min(앞끝-꺾임 거리) - 2 (P: 915 - 앞끝, N: 앞끝 + 915, A: 앞끝 + 1292.5)
열림/닫힘 전환 단계에는 반 단계 키를 더해 순서를 지킨다: 열 때 바깥 먼저(s+0.5까지) → A, 닫을 때 A 먼저 → 바깥.
안장 끝 = 멈춤(식 꺾임)이 두 단계 사이에 오면 그 소수 단계에도 키를 넣는다.
python -X utf8 -B tools/gen_N04_chain_keys.py
"""
import json, os, bisect
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_N04", "model2")
ML = os.path.join(ROOT, "out", "mech_N04", "model1", "motion_list_v1.0.12.json")  # J_U4_X·Y·U3 키는 v1.0.12 이후 그대로


def interp(pts, s):
    xs = [p[0] for p in pts]
    i = bisect.bisect_right(xs, s) - 1
    if i < 0:
        return pts[0][1]
    if i >= len(pts) - 1:
        return pts[-1][1]
    (s0, v0), (s1, v1) = pts[i], pts[i + 1]
    return v0 + (v1 - v0) * (s - s0) / (s1 - s0) if s1 != s0 else v1


def phase(jx, jy):
    yc = -400 + jy
    return jx > 800 and abs(yc) >= 200


def fronts(jx, jy, op):
    yc = -400 + jy
    openP = op and yc < 0      # 원판이 -Y 쪽 -> 반대쪽 P를 연다
    openN = op and yc > 0
    sP = SO if openP else -55     # 수정 2회차: 열림 = 닫힘 + 실린더 행정 110 = +55 (예전 +57)
    sN = -SO if openN else 55
    fP = max(yc + 81.5, sP)        # N04-E05: 막대 폭 10 + 틈 0.5
    fN = min(yc - 81.5, sN)
    fA = min(-831.0, -31.0 - jx) if op else -970.0
    return fP, fN, fA, openP, openN


SO = 55.0


def bars(jy):
    yc = -400 + jy
    return min(62.0, yc - 76), max(-62.0, yc + 76)


def vals(jx, jy, op):
    fP, fN, fA, oP, oN = fronts(jx, jy, op)
    bNP, bPN = bars(jy)
    return {"J_N04_CH_P": fP + 55, "J_N04_CH_N": fN + 481.5, "J_N04_CH_A": fA + 970,
            "J_N04_BAR_NP": bNP - 62, "J_N04_BAR_PN": bPN + 62,
            "J_N04_STOP_P": 110.0 if oP else 0.0, "J_N04_STOP_N": 110.0 if oN else 0.0,
            "J_N04_STOP_A": 150.0 - max(0.0, min(150.0, fA + 970))}


def simplify(pts, tol=1e-6):
    pts = sorted(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        (s0, v0), (s1, v1), (s2, v2) = out[-1], pts[i], pts[i + 1]
        if abs(s2 - s0) < 1e-12:
            continue
        vl = v0 + (v2 - v0) * (s1 - s0) / (s2 - s0)
        if abs(vl - v1) > tol:
            out.append(pts[i])
    if len(pts) > 1:
        out.append(pts[-1])
    return [[round(s, 4), round(v, 3)] for s, v in out]


def main():
    D = json.load(open(ML, encoding="utf-8"))
    res = {}
    dist = {"P": 1e9, "N": 1e9, "A": 1e9}
    warn = []
    for st in D["studies"]:
        keys = {k["joint"]: k["points"] for k in st["keys"]}
        n = st["steps"]
        J = [(interp(keys[11], s), interp(keys[12], s)) for s in range(n + 1)]
        ph = [phase(*J[s]) for s in range(n + 1)]
        op = [ph[s] or (s > 0 and ph[s - 1]) or (s < n and ph[s + 1]) for s in range(n + 1)]
        pts = {j: [] for j in vals(0, 0, False)}
        for s in range(n + 1):
            jx, jy = J[s]
            if op[s] and abs(-400 + jy) < 200:
                warn.append([st["name"], s, jx, jy])
            v = vals(jx, jy, op[s])
            for j, x in v.items():
                pts[j].append((s, x))
            fP, fN, fA, _, _ = fronts(jx, jy, op[s])
            dist["P"] = min(dist["P"], 915 - fP)
            dist["N"] = min(dist["N"], fN + 915)
            dist["A"] = min(dist["A"], fA + 1292.5)
            if s < n:
                jx2, jy2 = J[s + 1]
                if op[s] != op[s + 1]:
                    # 전환: 열 때 바깥 먼저, 닫을 때 A 먼저. 반 단계 지점에 중간 키
                    jm = ((jx + jx2) / 2, (jy + jy2) / 2)
                    vo = vals(jm[0], jm[1], True)
                    vc = vals(jm[0], jm[1], False)
                    mid = {}
                    for j in vo:          # 반 단계: 바깥·STOP_P/N은 열림, A는 멈춤(열 때·닫을 때 같음)
                        mid[j] = vc[j] if j in ("J_N04_CH_A", "J_N04_STOP_A") else vo[j]
                    for j, x in mid.items():
                        pts[j].append((s + 0.5, x))
                else:
                    # 안장 끝 = 멈춤이 단계 사이에 오는 곳(식 꺾임)
                    yc1, yc2 = -400 + jy, -400 + jy2
                    sP = SO if (op[s] and yc1 < 0) else -55
                    sN = -SO if (op[s] and yc1 > 0) else 55
                    for e1, e2, lv in ((yc1 + 81.5, yc2 + 81.5, sP), (yc1 - 81.5, yc2 - 81.5, sN),
                                       (yc1 - 76, yc2 - 76, 62.0), (yc1 + 76, yc2 + 76, -62.0)):
                        if (e1 - lv) * (e2 - lv) < 0:
                            t = (lv - e1) / (e2 - e1)
                            sm = s + t
                            vm = vals(jx + (jx2 - jx) * t, jy + (jy2 - jy) * t, op[s])
                            for j, x in vm.items():
                                pts[j].append((sm, x))
        res[st["name"]] = {"steps": n, "values": {j: simplify(p) for j, p in pts.items()},
                           "phaseL_steps": sum(ph), "open_steps": sum(op)}
    # 하드 리밋 자세 J_U4_X 1217.5(국면 L, 원판 +Y)도 A 앞끝이 들어가야 한다(수정 1회차 저장 후 점검: 1217.5 자세에서 A 앞끝 ↔ LOWER 1,800 mm³)
    dist["A"] = min(dist["A"], fronts(1217.5, 1155, True)[2] + 1292.5)
    # 수정 2회차(N04-E05 2항): P·N도 하드 리밋 J_U4_Y 1155 / -355 자세를 넣는다
    dist["P"] = min(dist["P"], 915 - fronts(0, 1155, False)[0])
    dist["N"] = min(dist["N"], fronts(0, -355, False)[1] + 915)
    Lf = {k: round(v - 2, 3) for k, v in dist.items()}
    # motion.study {study, keys}는 키를 통째로 바꾼다(2026-11-03 시험: REST keys 6만 남음) -> 기존 키를 함께 넣는다.
    # motion.list 값은 회전이 라디안, motion.study 입력은 도 -> J_U3_ROT(id 13) 변환.
    import math
    ROT = {13}
    cmds = []
    for st in D["studies"]:
        name = st["name"]
        r = res[name]
        old = []
        for k in st["keys"]:
            pts = [[p[0], (math.degrees(p[1]) if k["joint"] in ROT else p[1])] for p in k["points"]]
            # 수정 2회차: 일직선 위 점을 뺀다(보간 결과 같음, 명령 크기 줄임)
            old.append({"joint": k["joint"], "index": k.get("index", 0), "points": simplify(pts, 1e-4)})
        cmds.append({"command": "motion.study", "params": {"study": name, "keys": old + [
            {"joint": j, "points": p} for j, p in r["values"].items()]}})
    json.dump({"L_f": Lf, "min_dist": dist, "warn_open_small_Yc": warn, "studies": res},
              open(os.path.join(OUT, "chain_keys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(cmds, open(os.path.join(OUT, "stage_keys.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("L_f", Lf, "min_dist", dist, "warn", len(warn))
    for name, r in res.items():
        print(name, r["steps"], "phaseL", r["phaseL_steps"], "open", r["open_steps"],
              {j: len(p) for j, p in r["values"].items()})


if __name__ == "__main__":
    main()
