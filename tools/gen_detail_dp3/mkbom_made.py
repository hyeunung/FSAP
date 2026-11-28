"""DP-3: 가공 BOM을 새 번호로 복사해 이 묶음이 바꾼 행만 고친다(E-09 '재질 불일치 0', 지시서 ④ '용접 표기 없앰' · ⑥ 재질).
구매 BOM(볼트 수량) · 설계검토서는 문서 담당 몫이라 만들지 않는다.
usage: python -X utf8 -B tools/gen_detail_dp3/mkbom_made.py"""
import csv, json, re
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/'
SRC = ROOT + 'docs/bom/FSAP_v2.30.8_made.csv'
DST = ROOT + 'docs/bom/FSAP_v2.31.0_made.csv'
mp = json.load(open(ROOT + 'tools/out/mach_props.json', encoding='utf-8'))
rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
H = rows[0]
I = {h: i for i, h in enumerate(H)}
out = [H]
n_mat = 0
for r in rows[1:]:
    pn = r[I['품번']]
    if re.match(r'P_M08_TUBE_(COMB_(ML|U5)_\d|CLAMP_(F|L|SO)_\d)$', pn):
        assert r[I['재질']] == 'A5052', r
        r[I['재질']] = 'PET-CF'
        r[I['만드는 법']] = '출력'
        r[I['가공법']] = 'FDM(H2C) PET-CF, 관 구멍 축(X)을 세워 출력 · 볼트 구멍 Ø5.5 + 자리파기 Ø9.5 그대로(U-11: 출력품은 비용이 늘지 않음) · 탭 자리 없음(인서트 0)'
        r[I['질량 g(1개)']] = '%.1f' % mp[pn]['mass_g']
        note = 'DP-3(v2.31.0): 재질 A5052 밀링 → PET-CF 출력(MF-01 · FA-C1)'
        if 'COMB' in pn:
            r[I['형상']] = re.sub(r'Y 124~197|124, 197|158, 197', lambda m: {'Y 124~197': 'Y 120.2~197', '124, 197': '120.2, 197', '158, 197': '120.2, 197'}[m.group(0)], r[I['형상']]).replace('650.1', '647.0').replace('CB5-16', 'CB5-20')
            r[I['형상']] += ' · 밑면 턱(보 앞 윗모서리에 걸림): Y 120.2~123.8 · Z 647.0~650.1 · 폭 16' + (' · 밑 받침 살 t5 Y 120.2~158' if pn in ('P_M08_TUBE_COMB_ML_8', 'P_M08_TUBE_COMB_U5_2') else ' · 앞면 Y 124 → 120.2 한 면')
            note += ' · 돌림 막는 턱 높이 3.1(FA-A3, M-12) · 볼트 CB5-16 → CB5-20(보 탭 물림 8.0)'
        r[I['비고']] = note + ' / ' + r[I['비고']]
        n_mat += 1
    elif pn == 'P_M07_BEAM':
        r[I['이름']] = '전폭 보(각관)'
        r[I['가공법']] = '절단·드릴·탭'
        r[I['형상']] = '각관 400×200×8 L3730 X −2380~1350 · Y 120~320 · Z 250~650 · 양 끝 열림(덮개 P_M07_BEAM_CAP ×2) · 끝에서 18 자리 Ø5.5 ×8 · M5 · M4 관통 탭'
        r[I['질량 g(1개)']] = '%.0f' % mp[pn]['mass_g']
        r[I['비고']] = 'DP-3(v2.31.0): 끝판 t8 ×2(용접)와 옛 끝 자리 막 1 mm를 뗌 → 덮개 판금을 볼트로(SH-15, U-05 "용접은 하지 않는다"). 관통 탭 +19(M4 8 · M5 11, FA-B6), 빈 M5 탭 4 없앰(FA-M2), 덮개 볼트 구멍 Ø5.5 ×8 / ' + r[I['비고']]
    elif pn in ('P_M07_SPLICE_NX', 'P_M07_SPLICE_PX'):
        r[I['형상']] += ' · Ø10 ×2(보 덮개 볼트 머리 자리, Z 350 · 550)'
        r[I['질량 g(1개)']] = '%.0f' % mp[pn]['mass_g']
        r[I['비고']] = 'DP-3(v2.31.0): 보 끝에서 18 자리에 Ø10 ×2 — 덮개 뒷벽 볼트 CB5-12 머리가 이음판 속(머리 윗면이 판 겉보다 1 낮음), 이음판은 덮개 볼트를 풀지 않고 뗀다 / ' + r[I['비고']]
    out.append(r)
    if pn == 'P_M07_BEAM':
        cap = [''] * len(H)
        cap[I['품번']] = 'P_M07_BEAM_CAP'
        cap[I['이름']] = '보 끝 덮개'
        cap[I['컴포넌트']] = 'U1_FRAME'
        cap[I['모델 바디']] = 'P_M07_BEAM_CAP ×2(occurrence :1 −X 끝 · :2 +X 끝, Z 둘레 180° 돌려 같은 품번)'
        cap[I['수량']] = '2'
        cap[I['재질']] = 'SUS304 t3'
        cap[I['만드는 법']] = '판금'
        cap[I['가공법']] = '레이저·굽힘 R3 ×2·M5 탭 ×4'
        cap[I['형상']] = 'U자: 웹 183.6×383(위 · 아래 탭 3.5, 굽힘 끝에서 릴리프 3) + 플랜지 25 ×2(Z 262~638), 전개 223.2×383.0, M5 탭 ×4(굽힘 끝선–구멍 가장자리 9.9)'
        cap[I['질량 g(1개)']] = '%.0f' % mp['P_M07_BEAM_CAP']['mass_g']
        cap[I['가격']] = '미확인'
        cap[I['비고']] = 'DP-3(v2.31.0): 새로. 보 끝면과 한 면(X −2380 · 1350, 단차 0), 보 앞 · 뒷벽 Ø5.5로 CB5-12 ×4, 물림 3.0 = 판 두께(M-04 t ≥ 피치 × 3 = 2.4). 조임 토크는 얇은 판 탭 기준으로 낮게(손계산 1.0 N·m에서 암나사 전단 SF 2.2)'
        out.append(cap)
assert n_mat == 12, n_mat
with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f).writerows(out)
print('rows', len(rows), '->', len(out), 'material rows', n_mat, DST)
