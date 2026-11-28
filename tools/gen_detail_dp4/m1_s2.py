"""수정 1회차 단계 2: 보 앞 받침(EX3) t3 R3 폭 24 · 위 구멍 Z 631.5 + 리드 안내(EX2) 출력품 살 — 제자리 편집"""
import json, time, sys, fx
from fx import ex, C, run
E = lambda f, **s: C('timeline.edit', feature=f, set=s)
st = sys.argv[1]
if st == 'clamp':
    r = run('s2_clamp_a', [C('timeline.delete', feature='DP4_CLAMP_SHELF_T4')], verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:500])
    r = run('s2_clamp_b', [
        E('DP4_CLAMP_SHEET', rule='SUS304_t3', bends=[[-345.0, 120.0, 603.5]], faces=[[-345.0, 90.0, 603.5]]),
        E('RXDCC1_CLAMP_WALL', corner=[-357.0, 117.0, 603.5], length='24', height='35.5'),
        E('RXDCC1_CLAMP_SHELF', corner=[-357.0, 68.0, 603.5], length='24'),
        E('RXDCC1_CLAMP_HOLE_2', base=[-345.0, 116.0, 631.5]),
        E('RXDCC1_BEAM_TAP_2', base=[-345.0, 120.0, 631.5])], verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:700])
    names = ['P_RXDC03_BEAM_CLAMP_판금', 'P_M07_BEAM']
if st == 'guide':
    r = run('s2_guide', [
        E('RXDC03_GUIDE_PLATE', length='5'),
        E('RXDC03_GUIDE_TIE', width='5'),
        E('RXDC03_GUIDE_ARM', corner=[-296.6, 74.0, 132.0], height='12'),
        E('RXDC03_GUIDE_TAB', corner=[-252.0, 74.0, 132.0], length='6', width='20', height='31'),
        E('RXDC03_GUIDE_HOLE_1', base=[-253.0, 80.0, 150.0], height='8'),
        E('RXDC03_GUIDE_HOLE_2', base=[-253.0, 80.0, 159.0], height='8'),
        C('body.rename', body='P_RXDC03_LEAD_GUIDE_판금', name='P_RXDC03_LEAD_GUIDE_3DP'),
        C('material.assign', bodies=['P_RXDC03_LEAD_GUIDE_3DP'], material='PET-CF')], verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:900])
    names = ['P_RXDC03_LEAD_GUIDE_3DP', 'P_RX19_SWING_밀링']
m = fx.meas(names)
for k, v in m.items(): print(k, v)
