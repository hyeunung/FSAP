# -*- coding: utf-8 -*-
"""fea/models.json — 디테일링 DP-2(v2.30.7) 메모만 더한다. 고정 · 접촉 · 하중 줄은 바꾸지 않는다(모델 변경 0, E-18).
다시 돌려도 같은 결과(같은 키를 덮어씀). 실행: python -X utf8 -B fea/cases/detail_DP-2_models_update.py"""
import json
P = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/models.json'
R = json.load(open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/detail_DP-2_handcalc.json', encoding='utf-8'))
m = json.load(open(P, encoding='utf-8')); parts = m['parts']
K = 'note_detail_DP-2'
HEAD = '2026-11-28 DP-2(v2.30.7) 손계산 fea/results/detail_DP-2_handcalc.json · 형상 detail_DP-2_stepgeo.json. FEA 못 함 — 환경 없음(D-16). 고정 · 하중 그대로, 단면만 STEP 탭 자리 순단면(나사 Ø5)으로. '
L = R['FLAP_BAR_L1·L2·L3']['net_at_tap']['후(깊이 15)']; X = R['FLAP_BAR_XN']['net_at_center_tap']['후(깊이 15)']
XPs = R['FLAP_BAR_XP']['sf_mis']; PIN = R['M06_G1_PIN·TOP_PIN']
notes = {
 'P_RX12C1_FLAP_BAR_L1·L2·L3': '윗 탭 4곳 밑구멍 10 → 15(Z −13 → −28). 탭 자리 Z_min 946.1 → %s, Ktn %s: 운전 %s · 오조작 %s(구멍 없는 가운데 단면 22.4 · 14.0). 가운데 처짐 0.5125 → 0.5132 mm' % (
     L['Z_min'], L['Ktn'], L['worst_hole']['run_3g']['SF'], L['worst_hole']['mis_1g+hand']['SF']),
 'P_RX12C1_FLAP_BAR_XN': '윗 탭 5곳 10 → 15. 가운데 탭(414, −750)이 충격 굽힘 최대 자리와 겹침: Z_min 2158.1 → %s. 옛 모델(전체 단면 Z 2700 · Kt 2) 5.13 · 3.41 그대로, 순단면 × Kt 2는 4.01 · 2.66, 순단면 × Ktn 2.377은 3.37 · 2.24(기준 +12 %%)' % X['Z_min'],
 'P_RX12C1_FLAP_BAR_XP': '윗 탭 4곳 10 → 15, XP_TAP_1 10 → 12, 혀 탭 2곳 10 → 관통 15. 순단면 × Ktn 2.296: 윗 탭 %s · 혀 탭 %s · XP_TAP_1 + 경첩 탭 겹침 %s(전체 단면 41.5). XP_TAP_1 ↔ 경첩 탭 살 2.07(밑구멍) · 1.41(나사)' % (
     XPs['윗 탭 15(후)']['SF'], XPs['혀 탭 관통(후)']['SF'], XPs['XP_TAP_1 + 경첩 탭 겹침(보수)']['SF']),
 'P_RX12C1_GS_ARM_BLK': '윗 탭 2 · 옆 탭 2 밑구멍 10 → 15, 볼트 CB5-12 → CB5-16(물림 7 → 11 · 6 → 10). 나사 전단 운전 6.13 → 9.64 · 5.26 → 8.76, 조임(4.5 N·m) 암나사 1.07 → 1.68 · 0.92 → 1.53. 귀판 볼트 미끄럼 0.76은 그대로(FEA-05)',
 'P_M06_G1_PIN': '뒤끝 탭 밑구멍 12 → 15(Y 1.5 → −13.5), 당김 볼트 CB5-12 → CB5-16(물림 6 → 10). 뿌리는 전에도 탭이 지나는 빈 단면(Ø10/Ø5, Z 92.04): 오조작 %s(지난 값 5.59는 속 찬 단면). 볼트 조임 암나사 0.97 → 1.61' % PIN['root_misuse(팔 36)']['빈 단면(전 · 후 같음 — 탭이 전에도 뿌리를 지남)']['SF'],
}
notes['P_M06_TOP_PIN'] = notes['P_M06_G1_PIN']
for k, v in notes.items():
    assert k in parts, k
    parts[k][K] = HEAD + v
json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts), 'DP-2 메모', len(notes))
