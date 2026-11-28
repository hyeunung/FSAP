"""수정 1회차 단계 3: 세움 받침(EX1) — 옛 판금 모양 피처 17개를 지우고 A5052-H32 밀링 한 덩어리로 다시 그린다"""
import json, time, sys, fx
from fx import ex, C, run
st = sys.argv[1]
RB = 'P_RXDC03_RISER_BRKT_밀링'
OLD = ['RXDC03_RISER_PLATE', 'RXDC03_RISER_FLANGE', 'RXDC03_RISER_TIE', 'RXDC03_RISER_ARM', 'RXDC03_RISER_HOLE_1', 'RXDC03_RISER_HOLE_2', 'RXDC03_RISER_FOLD', 'RXDC03_RISER_FOLD_FLANGE',
       'RXDCC1_RISER_TRIM', 'RXDCC1_RISER_WEB', 'RXDCC1_RISER_FOLD', 'RXDCC1_RISER_SHELF', 'RXDCC1_RISER_TIE_S1', 'RXDCC1_RISER_TIE_S2', 'RXDCC1_RISER_ROOT_FLANGE', 'RXDCC1_RISER_FOLD_2', 'RXDCC1_RISER_HOLE_3']
if st == 'del':
    r = run('s3_del', [C('timeline.delete', features=OLD)], verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:900])
if st == 'build':
    B = lambda n, c, l, w, h, op='cut': C('solid.box', corner=c, length=l, width=w, height=h, operation=op, name=n, targets=[RB])
    cm = [C('component.activate', component='U4_XCAR'),
          C('solid.box', corner=[-318.6, 65, 256], length=50.6, width=20, height=231, operation='new', name='DP4R_STOCK', body_name=RB),
          B('DP4R_CUT_L', [-319.6, 64, 255], 31.6, 22, 229.25),
          B('DP4R_CUT_R', [-273, 64, 255], 6, 22, 229.25),
          B('DP4R_CUT_F', [-288, 64, 255], 15, 10.5, 229.25),
          B('DP4R_WEB_POCKET', [-289, 73.5, 470], 17, 8.75, 14.25),
          B('DP4R_BASE', [-305, 71.75, 250], 47, 25.25, 6, 'join'),
          B('DP4R_BASE_NOTCH', [-306, 70.75, 249], 18, 12.25, 7)]
    for i, (x, y) in enumerate([(-288, 90), (-278, 90), (-265.25, 79)]):
        cm.append(C('solid.cylinder', radius=2.75, height=8, base=[x, y, 249], axis='Z', operation='cut', name='DP4R_HOLE_%d' % (i + 1), targets=[RB]))
    for i, x0 in enumerate((-302, -282)):
        cm.append(B('DP4R_TIE_S%d' % (i + 1), [x0 + 1, 73, 483], 2, 2, 5))
        cm.append(C('solid.cylinder', radius=1, height=5, base=[x0 + 1, 74, 483], axis='Z', operation='cut', name='DP4R_TIE_S%d_A' % (i + 1), targets=[RB]))
        cm.append(C('solid.cylinder', radius=1, height=5, base=[x0 + 3, 74, 483], axis='Z', operation='cut', name='DP4R_TIE_S%d_B' % (i + 1), targets=[RB]))
    cm.append(C('solid.fillet', edges=[[-273, 79.75, 256], [-288, 84, 256], [-288, 83.625, 484.25], [-273, 83.625, 484.25]], radius=3, name='DP4R_FILLET_R3'))
    cm.append(C('material.assign', bodies=[RB], material='A5052'))
    cm.append(C('component.activate', component='root'))
    r = run('s3_build', cm, verbose=False)
    print(json.dumps(r, ensure_ascii=False)[:1500])
m = fx.meas([RB, 'P_RX19_BLOCK_밀링'] if st == 'build' else ['P_RX19_BLOCK_밀링'])
for k, v in m.items(): print(k, v)
