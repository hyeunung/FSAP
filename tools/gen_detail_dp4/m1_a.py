import json, m1q
from m1q import q, C
for pfx in ('timeline.', 'sheet.', 'solid.remove', 'solid.delete', 'body.', 'material.', 'occurrence.', 'joint.rigid', 'joint.del', 'parts.', 'file.insert', 'component.', 'appearance.', 'document.'):
    d = q.tool('lc_' + pfx.strip('.').replace('.', '_'), 'list_commands', prefix=pfx, fields=['id', 'params'])['data']
    for c in (d if isinstance(d, list) else d.get('commands', [])):
        print(c['id'], '|', json.dumps(c.get('params'), ensure_ascii=False)[:330])
