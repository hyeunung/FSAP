"""DP-3 수정 1회차 저장: 덮개 설명 · 문서 설명 · 대기 자세 · 표시 끔 -> 전수 측정 -> save {path: 새 번호} (한 번, 저장 뒤 편집 없음).
usage(작업 폴더 tools/out/detail/DP-3/m1 에서): python -X utf8 -B ../../../../gen_detail_dp3/fix1_save.py <새 .sc 절대 경로>"""
import json, sys, os, time, q
q.ask.__defaults__ = (470, 41081)


def _call(name, req, timeout=470):
    req = dict(req)
    req['save'] = os.path.abspath('r_%s.json' % name).replace(os.sep, '/')
    q.ask(req, timeout)
    return q.unwrap(req['save'])


q.call = _call
dst = sys.argv[1]
assert not os.path.exists(dst), 'already exists: ' + dst


def C(command, **params):
    return {'command': command, 'params': params}


DESC = ('DP-3 detailing fix1: beam P_M07_BEAM back-wall M5 taps at (X 1230, Z 300/600) re-opened (old-end fill box had closed 1 mm of them), '
        '6 unused M5 taps filled (bottom wall X -310/-160 Y 140/180, front wall X -256/-244 Z 276); end cap bolts CB5-12 -> CB5-16 x8 '
        '(M-01 exception DP3-EX1: tighten 1.0 N.m, max 1.5, removable threadlocker). Base: v2.31.0 DP-3 detailing (beam taps, bolted sheet end caps, tube comb lips, PET-CF combs/clamps)')
Cs = q.call('cl_save', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']
cap = [c for c in Cs if c['name'] == 'P_M07_BEAM_CAP'][0]
cmds = [C('component.metadata.set', component=cap['id'], part_number='P_M07_BEAM_CAP', bom_type='normal',
          description='Beam end cap, SUS304 sheet metal t3 R3 (laser + press brake, 2 bends): web 183.6x383 flush with beam end face, 2 flanges 25 inside front/back walls, 4x M5 tap; 4x CB5-16 through beam walls (DP-3, fix1). M5 tap x4 - tighten 1.0 N.m (max 1.5) + removable threadlocker, M-01 exception DP3-EX1. x2, +X one turned 180 deg about Z'),
        C('document.metadata.set', key='description', value=DESC),
        C('motion.play', study='REST', step=0),
        C('browser.visibility', visible=False, folder='joints'),
        C('browser.visibility', visible=False, folder='sketches')]
u = q.call('presave', {'commands': cmds, 'rollback': True, 'verbose': False})
d = u['data']
assert d.get('ok'), json.dumps(d, ensure_ascii=False)[:1500]
print('presave ok', d.get('completed'), 'rest moved', d['results'][2].get('moved'), 'conflicts', d['results'][2].get('conflicts'))
json.dump(cmds, open('cmds_presave.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
t = time.time()
m = q.call('meas_final', {'tool': 'measure', 'arguments': {}})['data']
print('measure all', len(m['bodies']), '%.1f s' % (time.time() - t))
i0 = q.call('insp_pre', {'tool': 'inspect_design', 'arguments': {'measure': False, 'sketches': False, 'timeline': False, 'bodies': False, 'joints': False}})['data']
print('before save', {k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')})
t = time.time()
s = q.call('save', {'tool': 'save', 'arguments': {'path': dst}})
print('save', json.dumps(s, ensure_ascii=False)[:400], '%.1f s' % (time.time() - t))
i1 = q.call('insp_end', {'tool': 'inspect_design', 'arguments': {'measure': False, 'sketches': False, 'timeline': 'summary', 'bodies': 'names', 'joints': False}})['data']
tl = i1.get('timeline') or []
fe = tl.get('features') if isinstance(tl, dict) else tl
print('after save', {k: i1.get(k) for k in ('name', 'dirty', 'marker', 'path')}, 'features', len(fe), 'errors', sum(1 for f in fe if f.get('error')), 'warnings', sum(1 for f in fe if f.get('warning')), 'bodies', len(i1.get('bodies', [])))
json.dump(dict(dst=dst, save=s, before={k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')}, after={k: i1.get(k) for k in ('name', 'dirty', 'marker', 'path')}, features=len(fe), errors=sum(1 for f in fe if f.get('error')), warnings=sum(1 for f in fe if f.get('warning')), bodies=len(i1.get('bodies', []))), open('save_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
