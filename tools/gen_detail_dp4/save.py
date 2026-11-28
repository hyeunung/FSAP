"""DP-4 저장: 문서 설명 · 대기 자세 · 표시 끔 -> 전수 측정 -> save {path: 새 번호}(한 번, 저장 뒤 편집 없음) -> 임시 STEP.
usage(작업 폴더 tools/out/detail/DP-4/m0 에서): python -X utf8 -B ../../../../gen_detail_dp4/save.py <새 .sc 절대 경로>"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q
from q import C
dst = sys.argv[1]
assert not os.path.exists(dst), 'already exists: ' + dst
DESC = ('DP-4 detailing: P_RXDC03_T2_GUIDE sheet-metal feature (SUS304 t3 R3, flat 49.39x18.0, 1 bend); '
        'P_RXDC03_BEAM_CLAMP t3 -> t4 sheet-metal feature (SUS304 t4 R4, flat 14.0x78.55, 1 bend; beam face Y 120 and shelf top Z 606.5 kept), '
        'its 2 bolts CB5-12_RXDC03_CLAMP_1/_2 re-seated head Y 117 -> 116 (engagement 8.0); dead cut RX19_SW_SLOT suppressed (timeline warning 259 -> 258, no shape change); '
        'P_M08_TUBE_BRKT_U6 material A5052 -> PET-CF. Not done (needs PM decision): P_RXDC03_RISER_BRKT t4 sheet redraw + front bolt M4 -> M5, P_RXDC03_LEAD_GUIDE t4 sheet. '
        'Base: v2.31.1 DP-3 detailing fix1')
shot = os.path.abspath('../dp4_iso.png').replace(os.sep, '/')
try:
    q.ask({'tool': 'screenshot', 'arguments': {'source': 'model', 'view': 'iso', 'width': 700, 'height': 500, 'path': shot}, 'save': os.path.abspath('r_shot.json').replace(os.sep, '/')})
    print('screenshot', os.path.exists(shot))
except Exception as e:
    print('screenshot fail', repr(e)[:200])
cmds = [C('document.metadata.set', key='description', value=DESC),
        C('motion.play', study='REST', step=0),
        C('browser.visibility', visible=False, folder='joints'),
        C('browser.visibility', visible=False, folder='sketches')]
u = q.batch('presave', cmds)
d = u['data']
assert d.get('ok'), json.dumps(d, ensure_ascii=False)[:1500]
print('presave ok', d.get('completed'), 'rest moved', d['results'][1].get('moved'), 'conflicts', d['results'][1].get('conflicts'))
json.dump(cmds, open('cmds_presave.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
t = time.time()
m = q.tool('meas_final', 'measure')['data']
print('measure all', len(m['bodies']), '%.1f s' % (time.time() - t), 'open bodies', [b['name'] for b in m['bodies'] if not b.get('closed')][:5])
i0 = q.tool('insp_pre', 'inspect_design', measure=False, sketches=False, timeline=False, bodies=False, joints=False)['data']
print('before save', {k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')})
t = time.time()
s = q.tool('save', 'save', path=dst)
print('save', json.dumps(s, ensure_ascii=False)[:400], '%.1f s' % (time.time() - t))
i1 = q.tool('insp_end', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
tl = i1.get('timeline') or []
fe = tl.get('features') if isinstance(tl, dict) else tl
res = dict(dst=dst, save=s, before={k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')}, after={k: i1.get(k) for k in ('name', 'dirty', 'marker', 'path')},
           features=len(fe), errors=sum(1 for f in fe if f.get('error')), warnings=sum(1 for f in fe if f.get('warning')),
           suppressed=[f['name'] for f in fe if f.get('suppressed')], bodies=len(i1.get('bodies', [])))
print('after save', res['after'], 'features', res['features'], 'errors', res['errors'], 'warnings', res['warnings'], 'bodies', res['bodies'])
json.dump(res, open('save_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
# 임시 STEP(해석용, 저장 뒤 — 형상을 바꾸지 않는다)
SO = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/stepout/'
for n, f in (('P_RXDC03_T2_GUIDE_판금', 'P_RXDC03_T2_GUIDE.step'), ('P_RXDC03_BEAM_CLAMP_판금', 'P_RXDC03_BEAM_CLAMP.step')):
    u = q.tool('exp_' + f[9:11], 'export', path=SO + f, bodies=[n])
    print('export', json.dumps(u['data'], ensure_ascii=False)[:200])
i2 = q.tool('insp_exp', 'inspect_design', measure=False, sketches=False, timeline=False, bodies=False, joints=False)['data']
print('after export', {k: i2.get(k) for k in ('name', 'dirty', 'path')})
