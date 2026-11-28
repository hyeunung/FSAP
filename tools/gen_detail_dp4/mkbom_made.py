"""DP-4: 가공 BOM을 새 번호(v2.31.2)로 복사해 이 회차가 바꾼 3행만 고친다(E-09 재질 불일치 0). mach_props.json의 3품번도 세션 측정값으로 고친다.
구매 BOM · 설계검토서는 문서 담당 몫이라 만들지 않는다.
usage(작업 폴더 tools/out/detail/DP-4/m0 에서): python -X utf8 -B ../../../../gen_detail_dp4/mkbom_made.py"""
import csv, json, shutil, os
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/'
SRC = ROOT + 'docs/bom/FSAP_v2.31.1_made.csv'
DST = ROOT + 'docs/bom/FSAP_v2.31.2_made.csv'
MP = ROOT + 'tools/out/mach_props.json'
chk = json.load(open('chk.json', encoding='utf-8'))['measure']
if not os.path.exists('mach_props_before_DP4.json'):
    shutil.copyfile(MP, 'mach_props_before_DP4.json')
mp = json.load(open(MP, encoding='utf-8'))
for pn in ('P_M08_TUBE_BRKT_U6', 'P_RXDC03_T2_GUIDE_판금', 'P_RXDC03_BEAM_CLAMP_판금'):
    mp[pn] = dict(mp[pn], mats=[chk[pn]['material']], mass_g=round(chk[pn]['mass_g'], 3))
    print(pn, mp[pn])
json.dump(mp, open(MP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
H = rows[0]; I = {h: i for i, h in enumerate(H)}
out = [H]; n = 0
for r in rows[1:]:
    pn = r[I['품번']]
    if pn == 'P_M08_TUBE_BRKT_U6':
        r[I['재질']] = 'PET-CF'; r[I['만드는 법']] = '출력'; r[I['가공법']] = 'FDM(H2C) PET-CF · 볼트 구멍 Ø5.5 다듬기'
        r[I['질량 g(1개)']] = '%.1f' % mp[pn]['mass_g']
        r[I['비고']] = 'DP-4(v2.31.2): 재질 A5052 → PET-CF(관 빗 · 클램프와 같은 재질, 형상 그대로) / ' + r[I['비고']]
        n += 1
    elif pn == 'P_RXDC03_T2_GUIDE_판금':
        r[I['형상']] = 't3 · 안쪽 R3(판금 기능, 규칙 SUS304_t3, 전개 49.39 × 18.0, 굽힘 1): 립 X −310.6~−307.6·Y 66~84·Z 212~236 + 판 밑 플랜지 X −310.6~−280·Z 233~236(Ø5.5 ×2)'
        r[I['질량 g(1개)']] = '%.1f' % mp[pn]['mass_g']
        r[I['비고']] = 'DP-4(v2.31.2): 솔리드 → 판금 기능(sheet.convert), 두께 그대로 t3, 굽힘 안쪽 R3. M-04 남은 것: 구멍 사이 4.5 < 2t 6, 구멍–판 끝 3.25 < 1.5t 4.5(탭 자리 — 예외 요청 DP4-EX2) / ' + r[I['비고']]
        n += 1
    elif pn == 'P_RXDC03_BEAM_CLAMP_판금':
        r[I['형상']] = 't4 · 안쪽 R4(판금 기능, 규칙 SUS304_t4, 전개 14.0 × 78.55, 굽힘 1): 벽 X −352~−338·Y 116~120·Z 602.5~636(Ø5.5 ×2, Z 619.5·630) + 선반 Y 68~120·Z 602.5~606.5(윗면 Z 606.5 그대로)'
        r[I['질량 g(1개)']] = '%.1f' % mp[pn]['mass_g']
        r[I['비고']] = ('DP-4(v2.31.2): t3 → t4(FEA-10 오조작 SF 1.76 → 3.19), 솔리드 → 판금 기능, 보 맞댐면 Y 120 · 선반 윗면 Z 606.5 그대로(벽은 −Y로, 선반은 밑으로 두꺼워짐). 볼트 CB5-12 ×2 머리 자리 Y 117 → 116(물림 8.0 = 보 벽 두께). '
                       'M-04 남은 것: 구멍–굽힘 10.77 < 2t+R 12, 구멍 사이 5.0 < 8, 구멍–판 끝 3.25 · 4.25 < 6(보 탭 자리 — 예외 요청 DP4-EX3) / ' + r[I['비고']])
        n += 1
    out.append(r)
assert n == 3, n
with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f).writerows(out)
print('written', DST, 'rows', len(out) - 1, 'edited', n)
