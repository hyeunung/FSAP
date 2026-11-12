# RX-08 모델링부 손계산(체결·하중, 설계안 calc.json 값을 받아 바뀐 볼트 자리로 다시)
import json, math
F = {'t10_p0.102': 132.3, 't10_p0.2': 191.1, 't16_p0.102': 145.6, 't16_p0.2': 204.3}  # 받침 반력 N(설계안 calc.json)
Fmax = 204.3
# 윗판 볼트 2개 (X -146, Y 69/79). 하중: ON 볼트 머리 (X -170) 아래로. 받침점 = 윗판 +X 끝 X -140
arm_load = -140 - (-170)      # 30
arm_bolt = -140 - (-146)      # 6
T_total = Fmax * arm_load / arm_bolt
T_bolt = T_total / 2
As_M5 = 14.2                  # mm2
proof_129 = 970 * As_M5       # N (12.9 보증하중 약 970 MPa)
# 나사 물림(BASE SUS304 t8, M5): 전단 면적 ~ pi*d*L*0.5
shear_area = math.pi * 5 * 8 * 0.5
tau_allow = 0.6 * 205         # SUS304 항복 205 x 0.6
thread_cap = shear_area * tau_allow
# 립 볼트 4개: 당길 때 실린더 몸을 +X로 당김 = 당기기 추력
pull_05 = 188.9
lip_per = pull_05 / 4
lip_cap = math.pi * 5 * 5.5 * 0.5 * (0.6 * 140)   # 실린더 몸 Al 탭 물림 5.5(임시), Al 항복 140 가정
# 조절 볼트 CB8 압축, 블록 M8 탭 물림 10.28(SUS304)
cb8_eng = 124 - 113.72
cb8_cap = math.pi * 8 * cb8_eng * 0.5 * tau_allow
# 너트 M8 위 머리 밑까지 여유(가장 낮은 셋업 H 139.58 -> 머리 밑 131.58)
nut_top = 130.8
gap_min = 131.58 - nut_top
out = dict(F_stop_N=F, top_bolts=dict(arm_load_mm=arm_load, arm_bolt_mm=arm_bolt, T_total_N=round(T_total, 1), T_per_bolt_N=round(T_bolt, 1),
                                      proof_N=round(proof_129), SF_proof=round(proof_129 / T_bolt, 1), thread_cap_N=round(thread_cap), SF_thread=round(thread_cap / T_bolt, 1)),
           lip_bolts=dict(per_bolt_N=round(lip_per, 1), thread_cap_Al_N=round(lip_cap), SF=round(lip_cap / lip_per, 1), note="밀 때는 몸이 립 면을 눌러 볼트 힘 0"),
           cb8=dict(engagement_mm=round(cb8_eng, 2), cap_N=round(cb8_cap), SF=round(cb8_cap / Fmax, 1), note="머리가 그네 윗판을 받는 압축, 너트로 풀림 막음"),
           nut_head_gap_min_mm=round(gap_min, 2),
           cylinder=dict(push_05_N=245.4, need_N=round(145.6 * 1.5, 1), SF=round(245.4 / 145.6, 2), note="문구 판정. 받침 면이 수평이라 실린더 축 힘은 0(설계안)"),
           stop_angle_cad=dict(theta_deg=0.95, head_swing_gap_mm=0.0014, theta_0p5_overlap_mm3=37.6, note="CAD: 그네 0.95°에서 머리-그네 0.0014(닿음), 0.5°에서 37.6 mm3 겹침 -> 0.95° 아래로 못 내려감"),
           tilt=dict(note="그네 축·바퀴 축 모두 X -> 바퀴 면 기울기 0°, 접지점 Y 이동만(설계안 2절: -0.58~-4.82). 떠 있는 동안 회전 SF·자국 해당 없음"))
json.dump(out, open(__file__.replace('.py', '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
