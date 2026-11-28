"""DP-4 수정 1회차: 가공 BOM을 새 번호(v2.31.3)로 복사해 이 회차가 바꾼 6행만 고친다(E-09 재질 불일치 0). mach_props.json의 바뀐 품번도 세션 측정값으로 고친다.
구매 BOM · 설계검토서는 문서 담당 몫이라 만들지 않는다.
usage(작업 폴더 tools/out/detail/DP-4/m1 에서): python -X utf8 -B ../../../../gen_detail_dp4/m1_mkbom.py"""
import csv, json, shutil, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/'
SRC = ROOT + 'docs/bom/FSAP_v2.31.2_made.csv'
DST = ROOT + 'docs/bom/FSAP_v2.31.3_made.csv'
MP = ROOT + 'tools/out/mach_props.json'
RB, LG, T2, CL, BLK, BEAM = 'P_RXDC03_RISER_BRKT_밀링', 'P_RXDC03_LEAD_GUIDE_3DP', 'P_RXDC03_T2_GUIDE_판금', 'P_RXDC03_BEAM_CLAMP_판금', 'P_RX19_BLOCK_밀링', 'P_M07_BEAM'
m = fx.meas([RB, LG, T2, CL, BLK, BEAM], 'm_bom')
json.dump(m, open('meas_bom.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if not os.path.exists('mach_props_before_DP4F1.json'):
    shutil.copyfile(MP, 'mach_props_before_DP4F1.json')
mp = json.load(open(MP, encoding='utf-8'))
mp.pop('P_RXDC03_RISER_BRKT_판금', None); mp.pop('P_RXDC03_LEAD_GUIDE_판금', None)
for pn in (RB, LG, T2, CL, BLK, BEAM):
    mp[pn] = dict(mats=[m[pn]['material']], mass_g=m[pn]['mass'], nb=1)
    print(pn, mp[pn])
json.dump(mp, open(MP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
H = rows[0]; I = {h: i for i, h in enumerate(H)}
out = [H]; n = 0
for r in rows[1:]:
    pn = r[I['품번']]
    if pn == BLK:
        r[I['재질']] = 'A5052-H32'
        r[I['형상']] = r[I['형상']].replace('세움 받침 앞 누름 M4 막힌 탭 깊이 10 ×1(X −280.5·Y 78.25, 선반 윗면 Z 250 → 240)',
                                        '선반(Z 236~250) M5 관통 탭 ×3(세움 받침 — X −288·−278 Y 90, 귀 X −265.25 Y 79) + 밑에서 M5 막힌 탭 깊이 10 ×2(T2 — X −296·−284, Y 75)')
        assert 'M5 관통 탭 ×3' in r[I['형상']]
        r[I['질량 g(1개)']] = '%.0f' % m[pn]['mass']
        r[I['비고']] = ('DP-4 수정 1회차(v2.31.3): 조질 H32 지정(H112면 M5 조임 암나사 전단 0.86 — DP4-EX1). 선반의 M4 막힌 탭(X −280.5·Y 78.25) 없앰 → 귀 자리 (−265.25, 79) M5 관통 탭, '
                       '세움 받침 뒤 탭 2개 (−288·−278, 90) 막힌 깊이 10 → 관통(CB5-16 물림 10), T2 둘째 탭 (−286, 75) → (−284, 75)(탭 사이 12). 탭 둘레 살 최소 5.8. 헤드 쪽 외곽 · 스톱 기둥 · 다리는 그대로(RX-16 보류) / ' + r[I['비고']])
        n += 1
    elif pn == 'P_RXDC03_LEAD_GUIDE_판금':
        r[I['품번']] = LG; r[I['모델 바디']] = LG + ' ×1'
        r[I['이름']] = 'U4 그네 서보 커넥터 받침(세운 판 + 다리 + 좌면 패드 + 타이 판, 출력 한 덩어리)'
        r[I['재질']] = 'PET-CF'; r[I['만드는 법']] = '출력'; r[I['가공법']] = 'FDM(H2C) PET-CF · 볼트 구멍 Ø5.5 다듬기 · 층 법선 = 세운 판 폭 방향(다리 길이 X가 층을 따라)'
        r[I['형상']] = ('그네 좌표: 세운 판 t5 X −296.6~−291.6·Y 52~96·Z 86~144(가운데 각 5.676° 기울임, 커넥터 닿는 면 X −296.6 그대로) + 타이 판 t7 Y 84~91·Z 136~146(−X 끝 X −318.6 그대로) + '
                       '다리 16 × 12 Y 74~90·Z 132~144 + 좌면 패드 t6 X −252~−246·Y 74~94·Z 132~164.5(그네 맞댐면 X −246 그대로, Ø5.5 ×2 자리 그대로)')
        r[I['질량 g(1개)']] = '%.1f' % m[LG]['mass']
        r[I['비고']] = ('DP-4 수정 1회차(v2.31.3, DP4-EX2): 판금(SUS304 t3, 접히지 않음) → PET-CF 출력 한 덩어리(U-05 · M-13). 품번 P_RXDC03_LEAD_GUIDE_판금 → _3DP. 볼트 CB5-12 ×2 → CB5-16 ×2(그네 텅 M5 관통 탭 t12, 물림 10), '
                       '조임 1.5 N·m(PET-CF 좌면). 손계산 오조작 50 N 지배 SF 2.19(다리 층간 2.31 · 타이 판 층간 2.23 · 패드 구멍 단면 2.19). 87.1 → %.1f g / ' % m[LG]['mass'] + r[I['비고']])
        n += 1
    elif pn == T2:
        r[I['형상']] = 't3 · 안쪽 R3(판금 기능, 규칙 SUS304_t3, 전개 52.89 × 18.0, 굽힘 1): 립 X −310.6~−307.6·Y 66~84·Z 212~236 + 판 밑 플랜지 X −310.6~−276.5·Z 233~236(Ø5.5 ×2, X −296·−284, Y 75)'
        r[I['질량 g(1개)']] = '%.1f' % m[pn]['mass']
        r[I['비고']] = ('DP-4 수정 1회차(v2.31.3, DP4-EX4): 둘째 구멍 (−286, 75) → (−284, 75), 판 +X 끝 −280 → −276.5. M-04 표 위반 0 — 구멍–굽힘 9.24 ≥ 9, 구멍 사이 6.5 ≥ 6, 구멍–판 끝 4.75 ≥ 4.5 / ' + r[I['비고']])
        n += 1
    elif pn == 'P_RXDC03_RISER_BRKT_판금':
        r[I['품번']] = RB; r[I['모델 바디']] = RB + ' ×1'
        r[I['이름']] = 'U4 연장 케이블 세움 받침(밑판 + 기둥 + 선반, 밀링 한 덩어리)'
        r[I['재질']] = 'A5052-H32'; r[I['만드는 법']] = '가공'; r[I['가공법']] = 'CNC 밀링(셋업 4: ±Y 윤곽 · +Z 타이 홈 · −Z 볼트 구멍, 안쪽 R3 · 타이 홈 R1)'
        r[I['형상']] = ('밑판 t6 Z 250~256: X −305~−258·Y 71.75~97에서 구석 X −305~−288·Y 71.75~83 뺌(Ø5.5 ×3 — X −288·−278 Y 90, 귀 X −265.25 Y 79) + 기둥 X −288~−273·Y 74.5~85 속 참 Z 256~470 + '
                       '웨브만 Y 82.25~85·Z 470~484.25(선반 밑 케이블 길) + 선반 X −318.6~−268·Y 65~85·Z 484.25~487(타이 홈 4 × 2 양 끝 R1 ×2, X −300·−280, Y 73~75) + 기둥–밑판 · 웨브–선반 안쪽 R3 ×4')
        r[I['질량 g(1개)']] = '%.1f' % m[RB]['mass']
        r[I['비고']] = ('DP-4 수정 1회차(v2.31.3, DP4-EX1): 판금(SUS304 t3 솔리드, 접히는 형상은 뿌리 SF 0.79) → A5052-H32 밀링 한 덩어리(M-04 · M-13). 품번 P_RXDC03_RISER_BRKT_판금 → _밀링. '
                       '볼트 CB5-12 ×2 + CB4-12 ×1 → CB5-16 ×3(블록 선반 M5 관통 탭, 물림 10 — U4_XCAR의 M4 0). 케이블 쪽 면(웨브 앞 · 선반 밑) 0.25 물림 — 케이블 임시 형상 틈 0.75 → 1.0. '
                       '손계산 오조작 50 N: 기둥 뿌리 4.56 · 웨브만 구간 2.96 · 선반 7.37 · 귀 뿌리 2.38(보수) · 귀 볼트 암나사 전단 2.63. 188.0 → %.1f g / ' % m[RB]['mass'] + r[I['비고']])
        n += 1
    elif pn == CL:
        r[I['형상']] = 't3 · 안쪽 R3(판금 기능, 규칙 SUS304_t3, 전개 24.0 × 82.29, 굽힘 1): 벽 X −357~−333·Y 117~120·Z 603.5~639(Ø5.5 ×2, X −345, Z 619.5·631.5) + 선반 Y 68~120·Z 603.5~606.5(윗면 Z 606.5 그대로)'
        r[I['질량 g(1개)']] = '%.1f' % m[pn]['mass']
        r[I['비고']] = ('DP-4 수정 1회차(v2.31.3, DP4-EX3): t4 · R4 → t3 · R3로 되돌리고 폭 14 → 24, 벽 끝 Z 636 → 639, 위 구멍 Z 630 → 631.5. M-04 표 위반 0 — 구멍–굽힘 10.64 ≥ 9, 구멍 사이 6.5 ≥ 6, 구멍–판 끝 4.75 ≥ 4.5(옆 9.25). '
                       '선반 손계산 오조작 SF 2.25(굽은 보 2.27 · 구멍 단면 2.25, 폭 14였다면 1.32). 볼트 CB5-12 ×2 머리 자리 Y 116 → 117(물림 8.0) / ' + r[I['비고']])
        n += 1
    elif pn == BEAM:
        r[I['비고']] = 'DP-4 수정 1회차(v2.31.3, DP4-EX3): 앞벽 M5 관통 탭 (X −345, Z 630) → Z 631.5로 옮김(보 앞 받침 위 볼트, 피처 RXDCC1_BEAM_TAP_2를 고침 — 빈 탭 0, 부피 그대로) / ' + r[I['비고']]
        n += 1
    out.append(r)
assert n == 6, n
with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f).writerows(out)
print('written', DST, 'rows', len(out) - 1, 'edited', n)
