# -*- coding: utf-8 -*-
"""regfix 손계산(해석부, FEA 환경 없음 D-16). v1.0.16 안쪽 끝 막대 이(齒) 멈춤.
대상: 새로 만들거나 옮긴 것만 — NP 막대 +X 끝, PN 막대 러그, 판 이 NP·PN.
하중: 정하중 스프링 운전 20 N, 오조작 100 N(사슬을 손으로 당김) — mech_N04_fea.md 하중표·D-89와 같음.
기준: 운전 SF 3, 오조작 SF 2(M-09 기본값, 요구서 6-1), SF < 1.2 영구 변형.
면 선택: STEP(tools/out/mech_regfix/stepout/P_N04_CHAIN_BAR_regfix.step) 바디별 bbox·고유 좌표에서 확인(옛 좌표 재사용 금지)."""
import re, sys, json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
STEP = sys.argv[1]

# ---- 1. STEP 바디 bbox·고유 좌표 ----
txt = open(STEP, encoding="latin-1").read()
ents = {int(m.group(1)): m.group(2) for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*$", txt, re.M | re.S)}
def pts(root):
    seen, stack, P = set(), [root], []
    while stack:
        i = stack.pop()
        if i in seen or i not in ents: continue
        seen.add(i); e = ents[i]
        if e.startswith("CARTESIAN_POINT"):
            c = re.search(r"\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)", e)
            if c: P.append(tuple(float(v) for v in c.groups()))
            continue
        if e.startswith(("DIRECTION", "VECTOR")): continue
        stack += [int(x) for x in re.findall(r"#(\d+)", e)]
    return P
bodies = {}
for i, e in ents.items():
    if e.startswith("MANIFOLD_SOLID_BREP"):
        name = re.search(r"'([^']*)'", e).group(1)
        u = [sorted(set(round(p[k], 2) for p in pts(i))) for k in range(3)]
        bodies[name] = {"bbox": [[x[0], x[-1]] for x in u],
                        "uniq": [x if len(x) <= 16 else x[:8] + ["..."] + x[-8:] for x in u]}

RP = {"A6063": 110.0, "A5052": 195.0}   # A6063-T5 0.2% 내력, A5052-H32 상당(이 덩어리를 실물 금속으로 볼 때)
F = {"run": 20.0, "mis": 100.0}
SFMIN = {"run": 3.0, "mis": 2.0}
items = []
def add(part, where, mode, case, stress, mat, note=""):
    sf = RP[mat] / stress
    j = "부러짐/영구변형" if sf < 1.2 else ("기준 미달(디테일)" if sf < SFMIN[case] else ("과사양" if sf >= 3 * SFMIN[case] else "통과"))
    items.append({"part": part, "where": where, "mode": mode, "case": case, "F_N": F[case],
                  "stress_MPa": round(stress, 1), "mat": mat, "sf": round(sf, 2), "sf_min": SFMIN[case], "judge": j, "note": note})

for c, f in F.items():
    # (a) NP 맞닿음 지압: NP 막대 +Y 끝면 Y 67, 겹침 X -831.5~-830.5(1) x Z -2.5~-0.5(2) = 2 mm2. 허용 지압 1.5 Rp
    A = 1.0 * 2.0
    add("P_N04_CHAIN_NP_BAR / PANEL 이 NP", "맞닿음 Y 67 (X 1 x Z 2 = 2 mm2)", "지압(허용 1.5Rp)", c, f / A / 1.5, "A6063")
    # (b) NP 이 뿌리: 판 -830 면에 붙은 이 X 1.5 x Y 10 x Z 2. 힘 Y, 작용점 X -831(겹침 가운데) -> 팔 1.0
    M = f * 1.0; Zm = 2.0 * 10.0 ** 2 / 6; tau = f / (10.0 * 2.0)
    s = math.sqrt((M / Zm) ** 2 + 3 * tau ** 2)
    add("P_N04_PANEL 이 NP", "뿌리 X -830 면(Y 10 x Z 2, 팔 1.0)", "굽힘+전단(von Mises)", c, s, "A5052",
        "판은 A5052_HC 허니컴(표피 1+1). 이 덩어리를 금속 블록으로 볼 때 값")
    # (c) PN 맞닿음 지압: 러그 -Y 끝면 -66.5, 겹침 X -832.5~-830.5(2) x Z -5~-3.5(1.5) = 3 mm2
    A = 2.0 * 1.5
    add("P_N04_CHAIN_PN_BAR / PANEL 이 PN", "맞닿음 Y -66.5 (X 2 x Z 1.5 = 3 mm2)", "지압(허용 1.5Rp)", c, f / A / 1.5, "A6063")
    # (d) PN 이 뿌리: X 2.5 x Y 10.5 x Z 1.5, 작용점 X -831.5 -> 팔 1.5
    M = f * 1.5; Zm = 1.5 * 10.5 ** 2 / 6; tau = f / (10.5 * 1.5)
    s = math.sqrt((M / Zm) ** 2 + 3 * tau ** 2)
    add("P_N04_PANEL 이 PN", "뿌리 X -830 면(Y 10.5 x Z 1.5, 팔 1.5)", "굽힘+전단(von Mises)", c, s, "A5052",
        "판은 A5052_HC 허니컴. 이 덩어리를 금속 블록으로 볼 때 값")
    # (e) PN 러그 목: 러그 X -832.5~-830.5 · Y -66.5~-57.5 · Z -5~-3, 몸 X -969~-832 · Z -3~0.
    #     러그와 몸이 붙은 면 = Z -3 면 중 X -832.5~-832(0.5) x Y 9 = 4.5 mm2. 힘 Y, 작용점 Z -4.25 -> 팔 1.25
    M = f * 1.25; Zm = 0.5 * 9.0 ** 2 / 6; tau = f / (0.5 * 9.0)
    s = math.sqrt((M / Zm) ** 2 + 3 * tau ** 2)
    add("P_N04_CHAIN_PN_BAR 러그", "러그-몸 이음 Z -3 면(X 0.5 x Y 9 = 4.5 mm2, 팔 1.25)", "굽힘+전단(von Mises)", c, s, "A6063",
        "러그가 몸 끝(-832)보다 1.5 튀어나와 몸과 겹치는 길이가 X 0.5뿐")
    # (f) NP 막대 끝: 막대 몸 10 x 3 단면이 그대로 닿으므로 끝 단면 압축 = f / 30 (참고)
    add("P_N04_CHAIN_NP_BAR", "끝 단면 10 x 3 압축(참고, 지배는 (a) 지압)", "압축(참고)", c, f / 30.0, "A6063")

# 허용 하중(오조작 SF 2) — 무엇이 지배하는지
allow = {}
allow["PN 러그 목 (SF2)"] = round(RP["A6063"] / 2 / math.sqrt((1.25 / (0.5 * 81 / 6)) ** 2 + 3 * (1 / 4.5) ** 2), 1)
allow["NP 지압 (SF2)"] = round(1.5 * RP["A6063"] * 2.0 / 2, 1)
allow["PN 지압 (SF2)"] = round(1.5 * RP["A6063"] * 3.0 / 2, 1)
# 고친 안: 러그를 몸 밑으로 X -838~-830.5(몸과 겹침 6) 늘리면 (PIN_3/4 X -834~-833과 겹치므로 PIN을 Y로 옮기거나 러그에 홈)
fixM = 1.25 / (6.0 * 81 / 6); fixT = 1 / (6.0 * 9.0)
allow["PN 러그 목, 겹침 6으로 늘림 (SF2)"] = round(RP["A6063"] / 2 / math.sqrt(fixM ** 2 + 3 * fixT ** 2), 1)

out = {"_note": "regfix 손계산(해석부, D-16 FEA 환경 없음). 단위 mm·N·MPa", "step": os.path.basename(STEP),
       "bodies": bodies, "loads": {"run": "정하중 스프링 20 N(D-89 임시)", "mis": "사슬 손으로 당김 100 N(mech_N04_fea.md 하중표)"},
       "items": items, "allow_N": allow}
json.dump(out, open(os.path.join(RES, "mech_regfix_handcalc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in bodies.items(): print(k, v["bbox"])
for i in items: print(i["case"], i["sf"], i["judge"], i["part"], "|", i["mode"])
print(allow)
