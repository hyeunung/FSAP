"""DP-4 수정 1회차 저장: 문서 설명 · 대기 자세 · 표시 끔 -> 전수 측정 -> save {path: 새 번호}(한 번, 저장 뒤 편집 없음) -> 임시 STEP 4.
usage(작업 폴더 tools/out/detail/DP-4/m1 에서): python -X utf8 -B ../../../../gen_detail_dp4/m1_save.py <새 .sc 절대 경로>"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx
from fx import C, ex, tool
dst = sys.argv[1]
assert not os.path.exists(dst), 'already exists: ' + dst
DESC = ('DP-4 detailing fix1: P_RXDC03_RISER_BRKT sheet-look solid (SUS304 t3) -> one milled piece P_RXDC03_RISER_BRKT_밀링 (A5052-H32: base t6, solid column 15x10.5 Z 256-470, web only Z 470-484.25, shelf t2.75, inside R3 x4), '
        'its bolts CB5-12 x2 + CB4-12 x1 -> CB5-16 x3 (block ledge M5 through taps, engagement 10; the M4 tap at (-280.5, 78.25) is gone, ear bolt at (-265.25, 79)); '
        'P_RXDC03_LEAD_GUIDE sheet-look solid -> printed P_RXDC03_LEAD_GUIDE_3DP (PET-CF: plate t5, leg 16x12, seat pad 20 x t6, tie tab t7), bolts CB5-12 x2 -> CB5-16 x2; '
        'P_RXDC03_BEAM_CLAMP back to t3 R3, width 14 -> 24, wall top Z 636 -> 639, upper hole and beam tap Z 630 -> 631.5 (M-04 violations 0); '
        'P_RXDC03_T2_GUIDE plate +X end -280 -> -276.5, second hole and block tap (-286, 75) -> (-284, 75) (M-04 violations 0). '
        'Base: v2.31.2 DP-4 detailing')
shot = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/dp4_fix1_iso.png'
try:
    fx.q.ask({'tool': 'screenshot', 'arguments': {'source': 'model', 'view': 'iso', 'width': 700, 'height': 500, 'path': shot}, 'save': fx.WD + '/r_shot.json'}, 470, fx.PORT)
    print('screenshot', os.path.exists(shot))
except Exception as e:
    print('screenshot fail', repr(e)[:200])
cmds = [C('document.metadata.set', key='description', value=DESC),
        C('motion.play', study='REST', step=0),
        C('browser.visibility', visible=False, folder='joints'),
        C('browser.visibility', visible=False, folder='sketches')]
r = fx.run('presave', cmds, verbose=True)
print('presave ok', 'rest moved', r[1].get('moved'), 'conflicts', r[1].get('conflicts'))
t = time.time()
m = tool('meas_final', 'measure')['data']
print('measure all', len(m['bodies']), '%.1f s' % (time.time() - t), 'open bodies', [b['name'] for b in m['bodies'] if not b.get('closed')][:5])
i0 = tool('insp_pre', 'inspect_design', measure=False, sketches=False, timeline=False, bodies=False, joints=False)['data']
print('before save', {k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')})
t = time.time()
s = tool('save', 'save', path=dst)
print('save', json.dumps(s, ensure_ascii=False)[:400], '%.1f s' % (time.time() - t))
i1 = tool('insp_end', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
tl = i1.get('timeline') or []
fe = tl.get('features') if isinstance(tl, dict) else tl
res = dict(dst=dst, save=s, before={k: i0.get(k) for k in ('name', 'dirty', 'marker', 'path')}, after={k: i1.get(k) for k in ('name', 'dirty', 'marker', 'path')},
           features=len(fe), errors=sum(1 for f in fe if f.get('error')), warnings=sum(1 for f in fe if f.get('warning')),
           suppressed=[f['name'] for f in fe if f.get('suppressed')], bodies=len(i1.get('bodies', [])))
print('after save', res['after'], 'features', res['features'], 'errors', res['errors'], 'warnings', res['warnings'], 'bodies', res['bodies'])
json.dump(res, open('save_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
SO = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/stepout/'
for n, f in (('P_RXDC03_RISER_BRKT_밀링', 'P_RXDC03_RISER_BRKT.step'), ('P_RXDC03_LEAD_GUIDE_3DP', 'P_RXDC03_LEAD_GUIDE.step'),
             ('P_RXDC03_T2_GUIDE_판금', 'P_RXDC03_T2_GUIDE.step'), ('P_RXDC03_BEAM_CLAMP_판금', 'P_RXDC03_BEAM_CLAMP.step')):
    u = tool('exp_' + f[9:11], 'export', path=SO + f, bodies=[n])
    print('export', json.dumps(u['data'], ensure_ascii=False)[:200])
i2 = tool('insp_exp', 'inspect_design', measure=False, sketches=False, timeline=False, bodies=False, joints=False)['data']
print('after export', {k: i2.get(k) for k in ('name', 'dirty', 'path')})
