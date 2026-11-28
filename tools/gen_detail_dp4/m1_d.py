import json, math, fx
from fx import ex, C
a = math.radians(19.523); c, s = math.cos(a), math.sin(a)
T = (-40.8031, 32.8254)
def W(x, y, z): return [x, c * y + s * z + T[0], -s * y + c * z + T[1]]
rays = []; tags = []
for y in (72, 74.5, 75.5, 80, 88, 94, 94.6, 95.4, 96.5, 100):
    rays.append({'origin': W(-262, y, 155), 'dir': [1, 0, 0]}); tags.append(('y', y))
for z in (112, 116, 118, 120, 130, 140, 150, 156, 159, 160.5, 161.5, 162.5, 163.5, 166):
    rays.append({'origin': W(-262, 85, z), 'dir': [1, 0, 0]}); tags.append(('z', z))
for z in (150, 159):
    rays.append({'origin': W(-262, 80, z), 'dir': [1, 0, 0]}); tags.append(('hole+', z))
    rays.append({'origin': W(-200, 80, z), 'dir': [-1, 0, 0]}); tags.append(('hole-', z))
d = ex('pick_sw', 'view.pick', rays=rays, all=True)['data']
H = d.get('hits', d.get('results', d)) if isinstance(d, dict) else d
for t, h in zip(tags, H):
    hs = h if isinstance(h, list) else (h.get('hits') if isinstance(h, dict) and 'hits' in h else [h])
    print(t, [(x.get('body')[:22], round(x['point'][0], 3)) for x in hs if x][:5])
