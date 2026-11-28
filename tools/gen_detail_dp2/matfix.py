import json, q
names = ['P_M07_BEAM', 'P_M07_SEAT_NX', 'P_M07_SEAT_PX', 'P_M07_SPLICE_NX', 'P_M07_SPLICE_PX']
b = q.call('mat_before', {'tool': 'execute', 'arguments': {'command': 'inspect.measure', 'params': {'bodies': names}}})['data']['bodies']
cm = [{'command': 'material.create', 'params': {'name': 'SS400', 'density_g_cm3': 7.85}},
      {'command': 'material.create', 'params': {'name': 'STKR400', 'density_g_cm3': 7.85}},
      {'command': 'material.assign', 'params': {'bodies': names[1:], 'material': 'SS400'}},
      {'command': 'material.assign', 'params': {'bodies': ['P_M07_BEAM'], 'material': 'STKR400'}}]
json.dump(cm, open('cmds_G_material.json', 'w', encoding='utf-8'), ensure_ascii=False)
u = q.call('matfix', {'commands': cm, 'rollback': True, 'verbose': False})
print(json.dumps(u, ensure_ascii=False)[:500])
a = q.call('mat_after', {'tool': 'execute', 'arguments': {'command': 'inspect.measure', 'params': {'bodies': names}}})['data']['bodies']
for x, y in zip(b, a): print(x['name'], x['material'], round(x['mass_g'], 3), '->', y['material'], round(y['mass_g'], 3), 'vol same', abs(x['volume_mm3'] - y['volume_mm3']) < 1e-6)
