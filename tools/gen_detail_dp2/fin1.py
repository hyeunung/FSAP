import json, q
cm = [{'command': 'selection.delete', 'params': {'occurrences': [101076]}},
      {'command': 'component.activate', 'params': {'component': 'U7_ROLL_MOUNT'}},
      {'command': 'solid.cylinder', 'params': {'radius': 2.1, 'height': 3.01, 'base': [1312.0, -13.5, 15.0], 'axis': [0, 1, 0], 'operation': 'cut', 'targets': ['P_M06_G1_PIN'], 'name': 'DP2_M06_G1_PIN_TAP_DEEP'}},
      {'command': 'solid.cylinder', 'params': {'radius': 2.1, 'height': 3.01, 'base': [1312.0, -13.5, 681.0], 'axis': [0, 1, 0], 'operation': 'cut', 'targets': ['P_M06_TOP_PIN'], 'name': 'DP2_M06_TOP_PIN_TAP_DEEP'}},
      {'command': 'component.activate', 'params': {'component': 'root'}}]
json.dump(cm, open('cmds_F.json', 'w', encoding='utf-8'), ensure_ascii=False)
u = q.call('fin1', {'commands': cm, 'rollback': True, 'verbose': False})
print(json.dumps(u, ensure_ascii=False)[:900])
u = q.call('fin1_meas', {'tool': 'execute', 'arguments': {'command': 'inspect.measure', 'params': {'bodies': ['P_M06_G1_PIN', 'P_M06_TOP_PIN']}}})
sig = json.load(open('../../../signatures.json', encoding='utf-8'))['parts']
for b in u['data']['bodies']:
    o = sig['U7_ROLL_MOUNT/' + b['name']]
    print(b['name'], round(b['volume_mm3'], 3), 'old', o['volume'], 'removed', round(o['volume'] - b['volume_mm3'], 3), 'expected', round(3.14159265 * 2.1 ** 2 * 3, 3), b['bbox'], b['closed'])
