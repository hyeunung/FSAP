# RX-13 수정 1회차 명령 생성기 (v2.20.3 -> v2.20.4).
# 실행: python -B tools/gen_rx13_fix1.py -> tools/out/mech_RX-13/fix1/stage_*.json
# 1) 잠금 너트 임시 형상 이름을 고른 형번으로: STEP대기_NUT-M8_RX13 -> STEP대기_NT-02_RX13 (SMC 로드 끝 너트 M8x1.25, B 13 x H 5)
# 2) U4 누름 관 세움(X -161.006)을 X -159.506으로 1.5 옮겨 RX08 관 세움(X -169)과 틈 1.994 -> 3.494 (허용 >= 3).
#    옛 스케치(이력 가운데)를 고치면 뒤 전체를 다시 계산하므로, 이력 끝에서 옛 바디를 지우고 같은 이름으로 다시 쓴다.
#    경로 원본: 저장본 document.json의 3D 와이어(tools/out/mech_FIX-045/doc/document.json, v2.12.x에서 그린 뒤 그대로).
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-13', 'fix1')
DOC = os.path.join(ROOT, 'out', 'mech_FIX-045', 'doc', 'document.json')
DX = -1.5
def C(cmd, **p): return {"command": cmd, "params": p}
r4 = lambda v: [round(x, 4) for x in v]
doc = json.load(open(DOC, encoding='utf-8'))
wires = {f['name']: f['sketch']['wires'] for f in doc['features'] if isinstance(f, dict) and str(f.get('name', '')).startswith('SK_TU0604_M08P_RX08')}

def piece(body, comp, sk_old, first, last, keep_start, keep_end, cutbox, desc_tag, end_x=None):
    """sk_old의 와이어 first..last(0부터, 둘 다 포함)를 X로 DX 옮겨 다시 쓸고 body에 합친다.
    keep_start/keep_end: 그 끝점은 옮기지 않는다(옛 관과 이어지는 자리)."""
    ws = wires[sk_old][first:last + 1]
    sk = "SK_%s_F1" % body
    tmp = body + "_F1TMP"
    c = [C("component.activate", component=comp),
         C("solid.box", corner=cutbox[0], length=round(cutbox[1][0] - cutbox[0][0], 4), width=round(cutbox[1][1] - cutbox[0][1], 4),
           height=round(cutbox[1][2] - cutbox[0][2], 4), operation="cut", targets=[body], name="CUT_%s_F1" % body),
         C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    L = 0.0
    n = len(ws)
    for i, w in enumerate(ws):
        fit = [list(p) for p in w['fit']]
        for j, p in enumerate(fit):
            fixed = (i == 0 and j == 0 and keep_start) or (i == n - 1 and j == len(fit) - 1 and keep_end)
            if not fixed: p[0] += DX
            elif end_x is not None and i == n - 1: p[0] = end_x   # 옛 곧은 줄 가운데에서 잇는다(호 이음 자리에서 자르면 합치기가 실패했다)
        if 'arc' in w:
            c.append(C("sketch.arc3d", start=r4(fit[0]), through=r4(fit[1]), end=r4(fit[-1])))
            a = w['arc']; R = a['radius']
            ch = math.dist(a['start'], a['end']); L += 2 * R * math.asin(min(1, ch / 2 / R))
        else:
            c.append(C("sketch.line3d", points=[r4(fit[0]), r4(fit[-1])])); L += math.dist(fit[0], fit[-1])
    c += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(n)], diameter=6.0, operation="new", body_name=tmp, name="PIPE_%s_F1" % body),
          C("solid.combine", target=body, tools=[tmp], operation="join", name="JOIN_%s_F1" % body),
          C("material.assign", bodies=[body], material="Default"),
          C("component.activate", component="root")]
    return c, round(L, 2)

st = {}
st['1_nut'] = [C("body.rename", body="STEP대기_NUT-M8_RX13", name="STEP대기_NT-02_RX13"),
               C("component.metadata.set", component="U4S_ROD", part_number="CDQSYB20-25DCM rod + NT-02 + Y-020B", bom_type="purchased",
                 description="STEP pending: CQSY rod D10 (male M8x1.25, rod nut 13x5) + P_RX13_ROD_EXT SUS303 turned extension D14x45 + SMC NT-02 rod end nut M8x1.25 (B 13 x H 5, lock nut, STEP pending) + SMC Y-020B single knuckle (fork to +Y, pin D8). Pull = press (RX-13)")]
# ---- 2안(채택): U4 누름 관 세움 2줄을 +X로 1.5(X -161.006 -> -159.506), 윗판·캐리지 발 장공 +X 벽에 R4 반달 자리 2.
#   1안(RX08 관 세움을 -X로 1.5)은 버렸다: RX08_B_U4의 호가 윗판 두께 안을 지나 장공 -X 벽(X -175.5)에 닿았고(겹침 0.05 mm3),
#   그쪽 벽 옆에는 캐리지 볼트 CB5-16_M02_1:2 (X -184.25~-175.75)가 있어 장공을 넓힐 수 없다. (stage 기록 fix1/try1/)
XS_OLD = -161.006; DXU = 1.5; XS = XS_OLD + DXU; ZJ = 340.0
uw = {f['name']: f['sketch']['wires'] for f in doc['features'] if isinstance(f, dict) and f.get('name') in ('SK_TU0604_M08P_U4_A2_RX06', 'SK_TU0604_M08P_U4_B_RX06')}
def pipe(body, segs):
    """segs: ('l', p0, p1) | ('a', start, through, end). 옛 바디를 지우고 같은 이름·같은 컴포넌트에 다시 쓴다."""
    sk = "SK_%s_F1" % body
    c = [C("solid.remove", bodies=[body], name="RM_%s_F1" % body), C("component.activate", component=body),
         C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    for g in segs:
        if g[0] == 'l': c.append(C("sketch.line3d", points=[r4(g[1]), r4(g[2])]))
        else: c.append(C("sketch.arc3d", start=r4(g[1]), through=r4(g[2]), end=r4(g[3])))
    c += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(segs))], diameter=6.0, operation="new", body_name=body, name="PIPE_%s_F1" % body),
          C("material.assign", bodies=[body], material="Default"),
          C("component.activate", component="root")]
    return c
def fixed(sk_old):
    """U8 고정 구간: 와이어 1~8 그대로, 9(가로 줄) 끝점 +DXU, 10(호) +DXU, 11(세움) +DXU이고 Z 340에서 끝."""
    out = []
    for i, w in enumerate(uw[sk_old][:11]):
        fit = [list(q) for q in w['fit']]
        if i == 8: fit[-1][0] += DXU
        if i >= 9:
            for q in fit: q[0] += DXU
        if i == 10: fit[-1][2] = ZJ
        out.append(('a', fit[0], fit[1], fit[-1]) if 'arc' in w else ('l', fit[0], fit[-1]))
    return out
def arc90(st, ce, en):
    R = math.dist(st, ce); m = [(st[k] + en[k]) / 2 - ce[k] for k in range(3)]; ml = math.sqrt(sum(x * x for x in m))
    return ('a', st, [ce[k] + m[k] / ml * R for k in range(3)], en)
ROD_END = (-240.0, 13.4 + 14.5, 191.5); HEAD_END = (-240.0 + 14.5, -30.1, 191.5)
A_segs = [('l', [XS, 79, ZJ], [XS, 79, 207.5]), arc90([XS, 79, 207.5], [XS - 16, 79, 207.5], [XS - 16, 79, 191.5]),
          ('l', [XS - 16, 79, 191.5], [-225, 79, 191.5]), arc90([-225, 79, 191.5], [-225, 64, 191.5], [-240, 64, 191.5]),
          ('l', [-240, 64, 191.5], list(ROD_END))]
B_segs = [('l', [XS, 70, ZJ], [XS, 70, 239]), arc90([XS, 70, 239], [XS - 16, 70, 239], [XS - 16, 70, 223]),
          ('l', [XS - 16, 70, 223], [-192.5, 70, 223]), arc90([-192.5, 70, 223], [-192.5, 55, 223], [-207.5, 55, 223]),
          ('l', [-207.5, 55, 223], [-207.5, -15.1, 223]), arc90([-207.5, -15.1, 223], [-207.5, -15.1, 208], [-207.5, -30.1, 208]),
          ('l', [-207.5, -30.1, 208], [-207.5, -30.1, 206.5]), arc90([-207.5, -30.1, 206.5], [-222.5, -30.1, 206.5], [-222.5, -30.1, 191.5]),
          ('l', [-222.5, -30.1, 191.5], list(HEAD_END))]
# 장공: 세움 자리마다 R4 원통을 윗판(Z 242~250)·캐리지 발(Z 250~262)에서 뺀다 -> +X 벽 X -157 -> 반달 끝 X -155.506 (관과 틈 1.0, 지금과 같음)
#   자르기는 그 바디의 컴포넌트를 활성으로 두고 한다. root에서 자르면 자리가 월드에 남아 J_U4_X를 따라가지 않았다
#   (X 95에서 관 ↔ 윗판 8.84 · 캐리지 13.27 mm3 겹침으로 드러나 timeline.delete로 지우고 다시 함 — stage_2x_slot_redo).
def slot(comp, body, z0, h):
    return [C("component.activate", component=comp)] + [
        C("solid.cylinder", radius=4.0, height=h, base=[XS, y, z0], axis=[0, 0, 1], operation="cut", targets=[body],
          name="CUT_RX13F1_SLOT_%s_Y%d" % (body.split('_')[1], y)) for y in (70, 79)]
st['2_slot'] = slot("U4_WHEEL_N", "P_M02_BASE", 241.9, 8.2) + slot("U4_XCAR", "P_RX06_CARRIAGE", 249.9, 12.2) + [C("component.activate", component="root")]
st['3_tubes_u4'] = pipe("TU0604_M08P_U4_A2_U4", A_segs) + pipe("TU0604_M08P_U4_B_U4", B_segs)
st['4_tubes_fix'] = pipe("TU0604_M08P_U4_A2", fixed('SK_TU0604_M08P_U4_A2_RX06')) + pipe("TU0604_M08P_U4_B", fixed('SK_TU0604_M08P_U4_B_RX06'))
st['9_final'] = [C("motion.play", study="REST", step=0, quiet=True),
                 C("browser.visibility", visible=False, folder="joints"),
                 C("browser.visibility", visible=False, folder="sketches")]
os.makedirs(OUT, exist_ok=True)
for k, v in st.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in st.items()})
for k in ('4_tubes_fix',):
    for s in st[k]:
        if s['command'].startswith('sketch.') and s['command'] != 'sketch.create': print(k, json.dumps(s['params']))
