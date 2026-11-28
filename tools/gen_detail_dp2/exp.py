import json, q, os
OUT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-2/stepout'
parts = ['P_RX12C1_FLAP_BAR_L1', 'P_RX12C1_FLAP_BAR_L2', 'P_RX12C1_FLAP_BAR_L3', 'P_RX12C1_FLAP_BAR_XN', 'P_RX12C1_FLAP_BAR_XP', 'P_RX12C1_GS_ARM_BLK', 'P_M06_G1_PIN', 'P_M06_TOP_PIN']
res = {}
for p in parts:
    u = q.call('exp_' + p, {'tool': 'export', 'arguments': {'path': '%s/%s.step' % (OUT, p), 'bodies': [p]}})
    res[p] = (u.get('isError'), str(u['data'])[:200]); print(p, res[p])
