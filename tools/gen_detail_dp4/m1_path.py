"""끼우는 길(M-12) 프로브: 세움 받침 -X 로 60.6 + 10, 리드 안내 -X 로 72.6 + 10 쓸어 본 상자. 재고 지운다."""
import json, fx, nb
from fx import ex, C, run, clr
RB = 'P_RXDC03_RISER_BRKT_밀링'; LG = 'P_RXDC03_LEAD_GUIDE_3DP'
cm = [C('component.activate', component='U4_XCAR'),
      C('solid.box', corner=[-389.2, 65, 484.3], length=121.2, width=20, height=2.7, operation='new', name='PP_SH', body_name='PP_SH'),
      C('solid.box', corner=[-358.6, 74.5, 256.05], length=85.6, width=10.5, height=228.2, operation='new', name='PP_COL', body_name='PP_COL'),
      C('solid.box', corner=[-375.6, 83, 250.05], length=87.6, width=14, height=5.95, operation='new', name='PP_BASE', body_name='PP_BASE'),
      C('solid.box', corner=[-318.6 - 82.6, 41.5, 82.3], length=82.6, width=60.7, height=79.4, operation='new', name='PP_LG', body_name='PP_LG'),
      C('component.activate', component='root')]
run('pp_build', cm, rec=False)
P = ['PP_SH', 'PP_COL', 'PP_BASE', 'PP_LG']
boxes = [[-389.2, -268, 65, 85, 484.3, 487], [-358.6, -273, 74.5, 85, 256, 484.3], [-375.6, -288, 83, 97, 250, 256], [-401.2, -318.6, 41.5, 102.2, 82.3, 161.7]]
SELF = {RB, LG, 'P_RXDC03_RISER_BRKT_판금', 'P_RXDC03_LEAD_GUIDE_판금', 'CB5-12_RXDC03_RISER_1', 'CB5-12_RXDC03_RISER_2', 'CB4-12_RXDCC1_RISER_3', 'CB5-12_RXDC03_GUIDE_1', 'CB5-12_RXDC03_GUIDE_2'}
AG = sorted(set(nb.neighbors([], 2, boxes)) - SELF - set(P))
flex = [a for a in AG if a.startswith('STEP대기_MR-') or a.startswith('STEP대기_HG-KR23') or a.startswith('TU0') or 'PTFE' in a or a.startswith('CBL')]
hard = [a for a in AG if a not in flex]
print('against hard', len(hard), 'flex', len(flex), flex)
R = {'hard': clr('pp_hard', P, hard, 1.0, 20), 'flex': clr('pp_flex', P, flex, 0.5, 20), 'against_hard': hard}
run('pp_del', [C('timeline.delete', features=['PP_SH', 'PP_COL', 'PP_BASE', 'PP_LG'])], rec=False)
json.dump(R, open('path1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
