"""수정 1회차 단계 1: T2(EX4) + 블록 턱 탭(EX1 3·4항, EX4 1항) — 있는 피처를 제자리에서 고친다(timeline.edit)"""
import json, time, fx
from fx import ex, C, run
print(json.dumps(ex('ckpt', 'edit.checkpoint')['data'], ensure_ascii=False)[:200])
E = lambda f, **s: C('timeline.edit', feature=f, set=s)
t = time.time()
r = run('s1_t2', [E('RXDC03_T2_FLANGE', length='34.1')], verbose=True)
print('one edit', round(time.time() - t, 1), 's', json.dumps(r, ensure_ascii=False)[:400])
r = run('s1_taps', [
    E('RXDC03_T2_HOLE_2', base=[-284.0, 75.0, 232.0]),
    E('RXDC03_BLK_TAP_T2_2', base=[-284.0, 75.0, 236.0]),
    E('RXDC03_BLK_TAP_RS_1', base=[-288.0, 90.0, 235.0], height='16'),
    E('RXDC03_BLK_TAP_RS_2', base=[-278.0, 90.0, 235.0], height='16'),
    E('RXDCC1_BLK_TAP_RS_3', base=[-265.25, 79.0, 235.0], height='16', radius='2.1'),
    C('timeline.rename', feature='RXDCC1_BLK_TAP_RS_3', name='DP4_BLK_TAP_RS_3_M5')], verbose=False)
print(json.dumps(r, ensure_ascii=False)[:600])
m = fx.meas(['P_RXDC03_T2_GUIDE_판금', 'P_RX19_BLOCK_밀링'])
for k, v in m.items(): print(k, v)
