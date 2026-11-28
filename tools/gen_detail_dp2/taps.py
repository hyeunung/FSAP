import json, q, sys
ids = [100374,100375,100376,100377,100379,100380,100381,100382,100384,100385,100386,100387,100390,100391,100392,100393,100394,100397,100398,100399,100400,100401,100411,100412,100413,100414,100408,100409]
if sys.argv[1] == 'inspect':
    u = q.call('taps_inspect', {'commands': [{'command': 'timeline.inspect', 'params': {'feature': i}} for i in ids], 'verbose': True})
    res = u['data']['results']
    out = []
    for i, r in zip(ids, res):
        d = r['definition']; out.append(dict(id=i, name=r['name'], base=d['base'], axis=d['axis'], height=d['height'], radius=d['radius'], part=d['participants']))
        print(i, r['name'], d['base'], d['axis'], d['height'], d['participants'])
    json.dump(out, open('taps_before.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
else:
    before = json.load(open('taps_before.json', encoding='utf-8'))
    cmds = []; plan = []
    for t in before:
        b = list(t['base']); ax = t['axis']; n = t['name']
        if 'SIDETAP' in n:
            new = dict(base=b, height='15')          # 입구 y -1224 그대로, 깊이 10 -> 15
        elif 'TONGUETAP' in n:
            new = dict(base=[1084.99, b[1], b[2]], height='15.02')   # 바 XP 15 관통
        else:
            new = dict(base=[b[0], b[1], -28.0], height='15.01')     # 입구 z -13, 깊이 10 -> 15
        if t['id'] == 100397:
            new = dict(base=[b[0], b[1], -25.0], height='12.01')   # 경첩 탭(y -335, z -28)과 0.8 mm 옆이라 깊이 12까지만
        cmds.append({'command': 'timeline.edit', 'params': {'feature': t['id'], 'set': new}})
        plan.append(dict(id=t['id'], name=n, before=dict(base=t['base'], height=t['height']), after=new))
    json.dump(plan, open('taps_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(cmds, open('stage_1_taps.json', 'w', encoding='utf-8'), ensure_ascii=False)
    u = q.call('taps_edit', {'commands': cmds, 'rollback': True})
    print(json.dumps(u, ensure_ascii=False)[:1500])
