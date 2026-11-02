# T17 모델링부 손계산(E-18, 해석 못 함 — 환경 없음 D-16). v0.8.5 실측 치수.
import json, math
R = {}
# 1) P_T17_TCLAMP 기둥 외팔(날개 밑 -373.5 -> 고리 높이 -393, 기둥 단면 X16 x Y10), 관 당김 2.5 N(선정 6절) + 꼬임 비틀림 반력 가정 5 N(안전쪽)
F = 5.0; L = 393 - 373.5; b, h = 10.0, 16.0
M = F * L; sig = 6 * M / (b * h * h)
R['clamp_column'] = {"F_N": F, "L_mm": L, "sigma_MPa": round(sig, 3), "PETCF_yield_MPa": 50.0, "SF": round(50.0 / sig, 1)}
# 2) 팔(X23~36 고리 쪽, 단면 Y10 x Z9) 외팔 L = 36 - 19.05
L2 = 36 - 19.05; b2, h2 = 9.0, 10.0
sig2 = 6 * F * L2 / (b2 * h2 * h2)
R['clamp_arm'] = {"L_mm": L2, "sigma_MPa": round(sig2, 3), "SF": round(50.0 / sig2, 1)}
# 3) CB5-12 -> Y판 A5052 M5 탭 물림 8: 4개 중 2개가 한 클램프, 당김 5 N -> 볼트당 2.5 N (예압 3 N·m 대비 무시)
R['cb5_12'] = {"engage_mm": 8.0, "min_1p5d": 7.5, "ok": True, "wrench_path_mm": {"(±54,-724) 아래": 38.0, "(±54,-698) 아래": 41.0}, "need": 12 + 5}
# 4) Y판 살: 탭 (±54) 가장자리 - 사각 창 X ±47.5
R['yplate_web'] = {"tap_edge_to_window_mm": round(54 - 2.1 - 47.5, 2), "M03_min": 2.5,
                   "phi10_edge_to_DG_side_mm": round(109.6 - 5 - 100, 2)}
# 5) 이젝터 브래킷 M3 탭(받침 A5052 깊이 8): 이젝터+브래킷 50.7 g, 5 G 가속 가정
m = 0.0507; a = 5 * 9.81
R['ejector_mount'] = {"mass_kg": m, "F_N_5G": round(m * a, 2), "taps": "M3 x2 깊이 8 (디테일 T17-D1 볼트)"}
# 6) 꼬임·처짐(선정 calc_sel.json 값 그대로, 모델 좌표 같음)
R['twist'] = {"L_mm": 198, "stretch_mm": 8.36, "need_mm": 10.36, "sag_h15_spare_mm": 11.87, "ok": True,
              "min_bend_R_mm": 18, "TU0604_R_provisional": 15, "D46_R10": 10}
json.dump(R, open(__file__.replace('.py', '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False))
