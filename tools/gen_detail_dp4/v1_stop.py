"""DP-4 검도: 리드 안내(출력품, 살이 커짐) ↔ 스토퍼 움직이는 묶음. J_U4_STOP 0~20 x J_U4_PRESS(스톱 이동 허용 범위 >= 1.515). 세션 41085."""
import os, json, fx
fx.PORT = 41085; fx.WD = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/v1'; os.chdir(fx.WD)
from fx import ex, clr, drive
LG = ['P_RXDC03_LEAD_GUIDE_3DP', 'CB5-16_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_2']
ST = ['P_RX08_STOP_BLOCK_밀링', 'STEP대기_CDQ2A25-20DMZ_ROD', 'STEP대기_NUT-M10_RX19', 'STEP대기_CDQ2A25-20DMZ']
R = {}
for p in (1.515, 5.676, 12.5995, 19.523):
    drive('J_U4_PRESS', p)
    for s in (0, 5, 10, 15, 20):
        drive('J_U4_STOP', s)
        r = clr('st_%s_%s' % (p, s), LG, ST, 6.0, 3)
        R['PRESS_%s_STOP_%s' % (p, s)] = r
drive('J_U4_STOP', 20); drive('J_U4_PRESS', 19.523)
r = ex('rest2', 'motion.play', study='REST', step=0); print('rest', str(r['data'])[:60])
json.dump(R, open('stop.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
