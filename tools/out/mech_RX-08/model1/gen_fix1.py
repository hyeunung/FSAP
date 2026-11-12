# RX-08 수정 1회차: 관 RX08_A·_B를 U4 쪽(U4_WHEEL_N 아래)·U8 쪽(U8_PNEU 아래) 두 구간으로 다시 그린다.
# 길은 v2.12.0 기록(tools/out/mech_RX-08/edit.json 64~90, 99~129)과 같고, 세움(X -169)의 Z 340에서 끊는다.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(HERE, '..', 'edit.json'), encoding='utf-8'))
ZJ = 340.0

def curves(lo, hi):
    return [E[i] for i in range(lo, hi + 1)]

def split_riser(step, zj):
    """세움 직선(같은 X·Y, Z만 바뀜)을 zj에서 두 직선으로."""
    (p0, p1) = step['params']['points']
    a = {'command': 'sketch.line3d', 'params': {'points': [p0, [p0[0], p0[1], zj]]}}
    b = {'command': 'sketch.line3d', 'params': {'points': [[p0[0], p0[1], zj], p1]}}
    return a, b

def piece(name, sk, comp_parent, comp_name, cs, activate, desc):
    st = [{'command': 'component.activate', 'params': {'component': activate}},
          {'command': 'sketch.create', 'params': {'plane': 'XY', 'name': sk}},
          {'command': 'sketch.options', 'params': {'sketch_3d': True}}]
    st += cs
    st += [{'command': 'sketch.finish', 'params': {}},
           {'command': 'solid.pipe', 'params': {'path_sketch': sk, 'path': ['w%d' % (i + 1) for i in range(len(cs))],
                                                 'diameter': 6.0, 'operation': 'new', 'body_name': name}},
           {'command': 'material.assign', 'params': {'bodies': [name], 'material': 'Default'}}]
    if comp_parent:
        st.append({'command': 'component.create', 'params': {'name': comp_name, 'parent': comp_parent, 'activate': False}})
    st.append({'command': 'component.move_bodies', 'params': {'bodies': [name], 'component': comp_name}})
    st.append({'command': 'component.metadata.set', 'params': {'component': comp_name, 'part_number': 'TU0604',
                                                                'bom_type': 'purchased', 'description': desc}})
    return st

stages = {}
stages['s0_delete'] = [{'command': 'timeline.delete', 'params': {'features': ['SK_TU0604_M08P_RX08_A', 'BodyTransfer598',
                                                                             'SK_TU0604_M08P_RX08_B', 'BodyTransfer599']}}]
# A: 64..79 + 세움 80 끊기 + 81..90
a1, a2 = split_riser(E[80], ZJ)
stages['s1_A_U4'] = piece('TU0604_M08P_RX08_A_U4', 'SK_TU0604_M08P_RX08_A_U4', 'U4_WHEEL_N', 'TU0604_M08P_RX08_A_U4',
                          curves(64, 79) + [a1], 'U4_WHEEL_N',
                          'SMC TU0604 OD6, RX-08 head port side, U4 segment (moves with J_U4_X); flexible bridge to U8 segment at Z 340')
stages['s2_A_U8'] = piece('TU0604_M08P_RX08_A', 'SK_TU0604_M08P_RX08_A2', None, 'TU0604_M08P_RX08_A',
                          [a2] + curves(81, 90), 'root',
                          'SMC TU0604 OD6, RX-08 stopper cylinder head port (push = OFF) <-> valve 8 B (PZ), U8 segment from Z 340')
b1, b2 = split_riser(E[115], ZJ)
stages['s3_B_U4'] = piece('TU0604_M08P_RX08_B_U4', 'SK_TU0604_M08P_RX08_B_U4', 'U4_WHEEL_N', 'TU0604_M08P_RX08_B_U4',
                          curves(99, 114) + [b1], 'U4_WHEEL_N',
                          'SMC TU0604 OD6, RX-08 rod port side, U4 segment (moves with J_U4_X); flexible bridge to U8 segment at Z 340')
stages['s4_B_U8'] = piece('TU0604_M08P_RX08_B', 'SK_TU0604_M08P_RX08_B2', None, 'TU0604_M08P_RX08_B',
                          [b2] + curves(116, 129), 'root',
                          'SMC TU0604 OD6, RX-08 stopper cylinder rod port (pull = ON) <-> valve 8 A (NZ), U8 segment from Z 340')
stages['s5_rigid'] = [{'command': 'component.activate', 'params': {'component': 'root'}},
                      {'command': 'joint.rigid_group', 'params': {'occurrences': ['U4_WHEEL_N:1', 'TU0604_M08P_RX08_A_U4:1', 'TU0604_M08P_RX08_B_U4:1']}}]
for k, v in stages.items():
    json.dump(v, open(os.path.join(HERE, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(k, len(v))
allc = []
for k in sorted(stages):
    allc += stages[k]
json.dump(allc, open(os.path.join(HERE, 'fix1_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
