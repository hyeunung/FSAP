# -*- coding: utf-8 -*-
"""N04 사슬 길이 변동 구간 고정 프로브 생성기 (모델링부 2026-11-03, 결정로그 N04-E02)
연구 단계의 조인트 값(J_U4_X·J_U4_Y)에서 gen_N04_chain_keys.py와 같은 식으로 사슬 앞끝을 계산하고,
바디가 없는 구간을 프로브 상자로 만든다. 출력 tools/out/probes/N04_chain_probe.json (CLI 명령 배열, 저장 없이 run --results).
프로브 상자(테이블 좌표 -> 월드 X = 테이블 X + J_U4_X, Y·Z 같음):
 (a) 바깥 P(N 거울): 앞끝 바디 뒤 Y [앞끝 + L_f, 913] · X -966~-834 · Z -5~0
     A: X [-1290.5, 앞끝 - L_f] · Y ±54 · Z -5~0
 (b) 꺾임·보관:
     P: 꺾임 Y 905~913 · Z -40~-6(판 통로 안) + 내려감 Y 905~928 · Z -79~-41, 보관 위층 Y 932~(932 + s) · Z -79~-56 (s = 앞끝 + 55 = 보관에 든 길이,
        닫힘 앞끝 -55에서 위층이 비는 가정: 사슬 길이 = 윗면 970 + 꺾임). 위층 끝 1528을 넘는 s는 '넘침' 상자로 1528 뒤에 둔다
        (위층과 아래층 사이 턱이 양쪽 10씩 남아 폭 132 사슬이 아래층으로 갈 길이 없음 -> 넘침 = 보관 길이 부족)
     A: 판 통로 내려감 X -1292~-1273 · Y ±54 · Z -117~-6, 보관 위층(턱 -122 위) X [-1292 - s, -1292] · Z -122~-117,
        s = -831 - 앞끝 (따라감 최대 -831에서 위층이 빔)
 (c) 안쪽 N+(P- 거울): 안장 -Y 끝이 멈춤 블록(Y 67)보다 +Y일 때 Y [67, Yc-71] · X -962~-838 · Z -5~0,
     안장 끝에서 드럼으로 내려가는 곳 Y [Yc-91, Yc-71] · Z -40~-5
단계: 각 연구의 식 꺾임(소수 키) 앞뒤 정수 단계, 앞끝 극단(P 최대·N 최소·A 최대·최소), 국면 L 10단계마다, 과제 범위 20자세(make_check와 같음).
가정(모델 판정 아님): 슬랫 꺾임 R·처짐·드럼 감김 형상은 상자로만 봄 -> 요구서 7절 N04-T2.
python -X utf8 -B tools/gen_N04_chain_probe.py
"""
import json, os
from gen_N04_chain_keys import interp, phase, fronts

ROOT = os.path.dirname(os.path.abspath(__file__))
M1 = os.path.join(ROOT, "out", "mech_N04", "model1")
OUTD = os.path.join(ROOT, "out", "probes")
K = json.load(open(os.path.join(M1, "chain_keys.json"), encoding="utf-8"))
ML = json.load(open(os.path.join(M1, "motion_list_v1.0.12.json"), encoding="utf-8"))
LP, LN, LA = K["L_f"]["P"], K["L_f"]["N"], K["L_f"]["A"]
CHK = json.load(open(os.path.join(ROOT, "out", "mech_N04", "model", "check_sets.json"), encoding="utf-8"))
NB = json.load(open(os.path.join(M1, "new_bodies.json"), encoding="utf-8"))
AGAINST = list(dict.fromkeys(CHK["new"] + sum(NB["bodies"].values(), []) + CHK["against"]))


def C(c, **p):
    return {"command": c, "params": p}


def boxes(jx, jy, op):
    yc = -400 + jy
    fP, fN, fA, oP, oN = fronts(jx, jy, op)
    b = []
    # (a)
    if fP + LP < 913:
        b.append(("PR_P_TOP", -966, -834, fP + LP, 913, -5, 0))
    if fN - LN > -913:
        b.append(("PR_N_TOP", -966, -834, -913, fN - LN, -5, 0))
    if fA - LA > -1290.5:
        b.append(("PR_A_TOP", -1290.5, fA - LA, -54, 54, -5, 0))
    # (b) 바깥 P·N 꺾임·보관
    for s_, f, tag in ((1, fP + 55, "P"), (-1, 470.5 - 525.5 + (55 - fN), "N")):
        s = f if tag == "P" else (55 - fN)
        # 꺾임: 판 통로 안(Y 905~913, Z -40~-6, 사슬 두께 5 + 꺾임 R 여유 3) + 판 밑에서 위층까지 내려감(Y 905~928, Z -79~-41)
        b.append(("PR_%s_BEND" % tag, -966, -834) + tuple(sorted((s_ * 905, s_ * 913))) + (-40, -6))
        b.append(("PR_%s_DROP" % tag, -966, -834) + tuple(sorted((s_ * 905, s_ * 928))) + (-79, -41))
        up = min(max(s, 0), 596)
        if up > 0.5:
            b.append(("PR_%s_STORE" % tag, -966, -834) + tuple(sorted((s_ * 932, s_ * (932 + up)))) + (-79, -56))
        if s > 596.5:
            b.append(("PR_%s_OVERFLOW" % tag, -966, -834) + tuple(sorted((s_ * 1528, s_ * (1528 + s - 596)))) + (-79, -56))
    # (b) A
    b.append(("PR_A_DROP", -1292, -1273, -54, 54, -117, -6))
    sA = -831 - fA
    if sA > 0.5:
        b.append(("PR_A_STORE", -1292 - sA, -1292, -54, 54, -122, -117))
    # (c) 안쪽 사슬
    if yc - 71 > 67.5:
        b.append(("PR_NP_SPAN", -962, -838, 67, yc - 71, -5, 0))
        b.append(("PR_NP_DOWN", -962, -838, yc - 91, yc - 71, -40, -5))
    if yc + 71 < -67.5:
        b.append(("PR_PN_SPAN", -962, -838, yc + 71, -67, -5, 0))
        b.append(("PR_PN_DOWN", -962, -838, yc + 71, yc + 91, -40, -5))
    out = []
    for nm, x0, x1, y0, y1, z0, z1 in b:
        if x1 - x0 < 0.5 or y1 - y0 < 0.5:
            continue
        out.append((nm, x0 + jx, x1 + jx, y0, y1, z0, z1))
    return out


def pose_cmds(tag, play, jx, jy, op):
    cmds = [play]
    bx = boxes(jx, jy, op)
    names = []
    for nm, x0, x1, y0, y1, z0, z1 in bx:
        cmds.append(C("solid.box", length=round(x1 - x0, 3), width=round(y1 - y0, 3), height=round(z1 - z0, 3),
                      corner=[round(x0, 3), round(y0, 3), z0], operation="new", body_name=nm))
        names.append(nm)
    cmds.append(C("inspect.clearance", bodies=names, against=AGAINST))
    cmds.append(C("solid.remove", bodies=names))
    return cmds, names


def main():
    os.makedirs(OUTD, exist_ok=True)
    allc, tags = [], []
    for st in ML["studies"]:
        name = st["name"]
        keys = {k["joint"]: k["points"] for k in st["keys"]}
        n = st["steps"]
        J = [(interp(keys[11], s), interp(keys[12], s)) for s in range(n + 1)]
        ph = [phase(*J[s]) for s in range(n + 1)]
        op = [ph[s] or (s > 0 and ph[s - 1]) or (s < n and ph[s + 1]) for s in range(n + 1)]
        sel = set()
        r = K["studies"][name]["values"]
        for j, pts in r.items():
            for p in pts:
                if abs(p[0] - round(p[0])) > 1e-6:
                    sel.update((int(p[0]), int(p[0]) + 1))
        F = [fronts(J[s][0], J[s][1], op[s]) for s in range(n + 1)]
        if n > 1:
            sel.add(max(range(n + 1), key=lambda s: F[s][0]))
            sel.add(min(range(n + 1), key=lambda s: F[s][1]))
            sel.add(max(range(n + 1), key=lambda s: F[s][2]))
            sel.add(min(range(n + 1), key=lambda s: F[s][2]))
            sel.update(s for s in range(n + 1) if ph[s] and s % 10 == 0)
        else:
            sel.add(0)
        for s in sorted(x for x in sel if 0 <= x <= n):
            c, nm = pose_cmds(None, C("motion.play", study=name, step=s, quiet=True), J[s][0], J[s][1], op[s])
            allc += c
            tags.append({"i": len(allc) - 2, "study": name, "step": s, "J": [round(J[s][0], 2), round(J[s][1], 2)], "open": op[s], "probes": nm})
    for jx in (-200, 0, 500, 800, 1217.5):
        for jy in (-355, 0, 300, 1155):
            o = phase(jx, jy)
            from gen_N04_chain_keys import vals
            pl = [C("joint.drive", joint="J_U4_X", value=jx, quiet=True), C("joint.drive", joint="J_U4_Y", value=jy, quiet=True)]
            pl += [C("joint.drive", joint=j, value=round(x, 4), quiet=True) for j, x in vals(jx, jy, o).items()]
            c, nm = pose_cmds(None, pl[0], jx, jy, o)
            c = pl + c[1:]
            allc += c
            tags.append({"i": len(allc) - 2, "pose": [jx, jy], "open": o, "probes": nm})
    allc.append(C("motion.play", study="REST", step=0, quiet=True))
    json.dump(allc, open(os.path.join(OUTD, "N04_chain_probe.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"tags": tags, "L_f": K["L_f"], "against": AGAINST}, open(os.path.join(OUTD, "N04_chain_probe_tags.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("commands", len(allc), "poses", len(tags))


if __name__ == "__main__":
    main()
