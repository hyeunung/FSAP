# -*- coding: utf-8 -*-
"""DP-4 해석부 수정 1회차(v2.31.3): 손계산에 쓸 단면을 STEP에서 잰다(E-18 "손계산의 단면은 가정하지 말고 측정 자료의 최소 단면으로").
gmsh(OCC)로 부품을 얇은 판(두께 0.02)과 겹쳐 그 조각의 부피 / 두께 = 단면 넓이, 조각의 상자 = 단면 외곽을 낸다. 부품 전체 부피 · 상자도 낸다(서명과 대조).
CAD 안 씀. 솔버 아님(해석 못 함 — 환경 없음, D-16). gmsh만 있는 ~/.mechdesign/stepvenv 로 돈다.
실행: ~/.mechdesign/stepvenv/Scripts/python.exe -I fea/cases/detail_DP-4_fix1_sections.py <STEP 폴더> <결과.json>"""
import sys, json, math
import gmsh

STEPDIR, OUT = sys.argv[1], sys.argv[2]
TH = 0.02
# (부품, 이름, 자르는 축, 자리, 자를 범위 상자[없으면 전체])
CUTS = [
    ("P_RXDC03_RISER_BRKT", "기둥 뿌리 바로 위 Z 259.5(R3 끝 위)", "Z", 259.5, None),
    ("P_RXDC03_RISER_BRKT", "기둥 뿌리 Z 256.05", "Z", 256.05, None),
    ("P_RXDC03_RISER_BRKT", "기둥 가운데 Z 360", "Z", 360.0, None),
    ("P_RXDC03_RISER_BRKT", "기둥 위 끝 Z 469.9", "Z", 469.9, None),
    ("P_RXDC03_RISER_BRKT", "웨브만 구간 밑 Z 470.1", "Z", 470.1, None),
    ("P_RXDC03_RISER_BRKT", "웨브만 구간 가운데 Z 476", "Z", 476.0, None),
    ("P_RXDC03_RISER_BRKT", "웨브 위 R3 시작 Z 481.2", "Z", 481.2, None),
    ("P_RXDC03_RISER_BRKT", "선반 Z 485.6", "Z", 485.6, None),
    ("P_RXDC03_RISER_BRKT", "밑판 Z 253", "Z", 253.0, None),
    ("P_RXDC03_RISER_BRKT", "귀 뿌리 X -270(R3 끝), Z 250~256", "X", -270.0, (None, None, None, None, 250.0, 256.0)),
    ("P_RXDC03_RISER_BRKT", "귀 볼트 줄 X -265.25, Z 250~256", "X", -265.25, (None, None, None, None, 250.0, 256.0)),
    ("P_RXDC03_RISER_BRKT", "뒤꿈치 뿌리 Y 85.05(기둥 뒷면), Z 250~256", "Y", 85.05, (None, None, None, None, 250.0, 256.0)),
    ("P_RXDC03_RISER_BRKT", "뒤 볼트 줄 Y 90, Z 250~256", "Y", 90.0, (None, None, None, None, 250.0, 256.0)),
    ("P_RXDC03_RISER_BRKT", "선반 X -288.05(웨브 -X 면 옆)", "X", -291.1, (None, None, None, None, 484.25, 487.0)),
    ("P_RXDC03_RISER_BRKT", "선반 Y 82.2(웨브 앞면 앞)", "Y", 82.2, (None, None, None, None, 484.25, 487.0)),
    ("P_RXDC03_RISER_BRKT", "선반 먼 타이 홈 줄 X -300", "X", -300.0, (None, None, None, None, 484.25, 487.0)),
    ("P_RXDC03_LEAD_GUIDE", "다리 X -270", "X", -270.0, None),
    ("P_RXDC03_LEAD_GUIDE", "다리 뿌리(패드 쪽) X -252.05", "X", -252.05, None),
    ("P_RXDC03_LEAD_GUIDE", "다리 뿌리(판 쪽) X -291.55", "X", -291.55, None),
    ("P_RXDC03_LEAD_GUIDE", "좌면 패드 X -249", "X", -249.0, None),
    ("P_RXDC03_LEAD_GUIDE", "세운 판 X -294", "X", -294.0, None),
    ("P_RXDC03_LEAD_GUIDE", "세운 판 앞쪽 X -295.8", "X", -295.8, None),
    ("P_RXDC03_LEAD_GUIDE", "타이 판 뿌리 X -296.65", "X", -296.65, None),
    ("P_RXDC03_LEAD_GUIDE", "타이 판 X -308", "X", -308.0, None),
    ("P_RXDC03_BEAM_CLAMP", "선반 Y 90", "Y", 90.0, None),
    ("P_RXDC03_BEAM_CLAMP", "선반 굽힘 끝선 Y 113.95", "Y", 113.95, None),
    ("P_RXDC03_BEAM_CLAMP", "벽 굽힘 끝선 Z 609.55", "Z", 609.55, None),
    ("P_RXDC03_BEAM_CLAMP", "벽 아래 구멍 줄 Z 619.5", "Z", 619.5, None),
    ("P_RXDC03_BEAM_CLAMP", "벽 위 구멍 줄 Z 631.5", "Z", 631.5, None),
    ("P_RXDC03_T2_GUIDE", "립 Z 220", "Z", 220.0, None),
    ("P_RXDC03_T2_GUIDE", "플랜지 굽힘 끝선 X -304.55", "X", -304.55, None),
    ("P_RXDC03_T2_GUIDE", "플랜지 첫 구멍 줄 X -296", "X", -296.0, None),
    ("P_RXDC03_T2_GUIDE", "플랜지 둘째 구멍 줄 X -284", "X", -284.0, None),
]

gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
R = {}
for part in sorted(set(c[0] for c in CUTS)):
    gmsh.clear(); gmsh.model.add(part)
    ents = gmsh.model.occ.importShapes(STEPDIR + "/" + part + ".step")
    gmsh.model.occ.synchronize()
    vols = [e for e in ents if e[0] == 3]
    bb = gmsh.model.getBoundingBox(3, vols[0][1]) if len(vols) == 1 else None
    vol = sum(gmsh.model.occ.getMass(3, t) for d, t in vols)
    com = gmsh.model.occ.getCenterOfMass(3, vols[0][1])
    R[part] = {"n_solids": len(vols), "volume": round(vol, 3), "bbox": [round(v, 3) for v in bb] if bb else None, "com": [round(v, 3) for v in com],
               "n_faces": len(gmsh.model.getEntities(2)), "sections": {}}
    x0, y0, z0, x1, y1, z1 = bb
    for p, name, ax, pos, lim in CUTS:
        if p != part: continue
        lo = [x0 - 1, y0 - 1, z0 - 1]; hi = [x1 + 1, y1 + 1, z1 + 1]
        if lim:
            for i in range(3):
                if lim[2 * i] is not None: lo[i] = lim[2 * i]
                if lim[2 * i + 1] is not None: hi[i] = lim[2 * i + 1]
        i = "XYZ".index(ax); lo[i] = pos - TH / 2; hi[i] = pos + TH / 2
        box = gmsh.model.occ.addBox(lo[0], lo[1], lo[2], hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        out, _ = gmsh.model.occ.intersect([(3, box)], vols, removeObject=True, removeTool=False)
        gmsh.model.occ.synchronize()
        pieces = []
        for d, t in out:
            if d != 3: continue
            v = gmsh.model.occ.getMass(3, t); b = gmsh.model.getBoundingBox(3, t); c = gmsh.model.occ.getCenterOfMass(3, t)
            I = gmsh.model.occ.getMatrixOfInertia(3, t)          # 무게중심 둘레, 밀도 1
            pieces.append({"area": round(v / TH, 3), "bbox": [round(x, 3) for x in b], "centroid": [round(x, 3) for x in c],
                           "I_about_centroid_axes(mm4, 조각 부피 관성 / 두께)": [round(I[0] / TH, 2), round(I[4] / TH, 2), round(I[8] / TH, 2)]})
        R[part]["sections"][name] = {"axis": ax, "pos": pos, "pieces": pieces, "area_sum": round(sum(q["area"] for q in pieces), 3)}
        if out: gmsh.model.occ.remove([e for e in out if e[0] == 3], recursive=True); gmsh.model.occ.synchronize()
gmsh.finalize()
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for part, v in R.items():
    print(part, "부피", v["volume"], "상자", v["bbox"], "면", v["n_faces"])
    for n, s in v["sections"].items():
        print("  ", n, "넓이", s["area_sum"], "|", "; ".join("%s" % (q["bbox"],) for q in s["pieces"]))
