# -*- coding: utf-8 -*-
"""N04 수정 2회차 손계산 (모델링부, FEA 환경 없음 D-16). 새로 옮긴 꼬리 멈춤 받침 P/N, 패드·러그 지압, 막대 러그.
하중: 해석 2회차와 같음 — CDJ2B16 추력 운전 0.5 MPa 100.5 N, 오조작 0.7 MPa 140.7 N (fea/results/mech_N04_fea1_handcalc.json)"""
import json, math, os
Rp = 205.0  # SUS304
F = {"run": 100.531, "mis": 140.74}
out = {"_note": "N04 수정 2회차 손계산(모델링부, D-16). 단위 mm·N·MPa", "items": []}
# 받침 L: 세운 판 X -830~-806(b 24) t4 Y 775~779, 날개 Y 767~779 Z -44~-40, 실린더 축 Z -69 -> 팔 25
b, t, L = 24.0, 4.0, 25.0
for c, f in F.items():
    M = f * L; s = 6 * M / (b * t * t)
    out["items"].append({"part": "P_N04_CYLBKT_P/_N", "where": "세운 판 뿌리 Z -44 (24×t4, 팔 25)", "case": c,
                         "M_Nmm": round(M), "stress_MPa": round(s, 2), "sf": round(Rp / s, 2), "sf_min": 3.0 if c == "run" else 2.0,
                         "ok": Rp / s >= (3.0 if c == "run" else 2.0)})
E = 193000.0; I = b * t ** 3 / 12
out["cylbkt_deflection_run_mm"] = round(F["run"] * L ** 3 / (3 * E * I), 4)
# 패드 ↔ 꼬리 러그 지압: 러그 단면(X 6 중 옆벽 밖 2 × Z 3)만 닿는다고 보면 6 mm2
A = 2 * 3.0
out["pad_lug_bearing_MPa"] = {c: round(f / A, 1) for c, f in F.items()}
out["pad_lug_note"] = "러그 재질·형상은 사슬(구매품/디테일) 쪽. 지압 23 MPa(오조작)는 SUS304·POM 러그 모두 견딤. 러그 치수는 요구서 7절 N04-T2·디테일 N04-D7"
# 막대 러그(멈춤 홈): 정하중 스프링 힘 미정(형번 미정) -> 판정 안 함, 홈 끝 지압 면적만 기록
out["bar_lug_contact_mm2"] = {"NP(Z -3~0, X -830~-829 홈 안 1 × 높이 3)": 3.0, "PN(Z -5~-3, X -830~-829 × 2)": 2.0}
out["bar_lug_note"] = "정하중 스프링 형번 미정(바디 없음). 힘 10 N이면 지압 3.3·5 MPa로 문제없음. 스프링 형번이 정해지면 다시 본다(디테일)"
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "mech_N04_fix2_handcalc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i in out["items"]: print(i["case"], i["stress_MPa"], i["sf"], i["ok"])
print(out["cylbkt_deflection_run_mm"], out["pad_lug_bearing_MPa"])
