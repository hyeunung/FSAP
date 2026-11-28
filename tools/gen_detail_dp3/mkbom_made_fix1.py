"""DP-3 수정 1회차: 가공 BOM을 새 번호(v2.31.1)로 복사해 이 회차가 바꾼 행만 고친다(E-09 재질 불일치 0, 예외 DP3-EX1 조건 4의 덮개 비고).
구매 BOM(볼트 수량 CB5-12 -8 · CB5-16 +8) · 설계검토서 조임 토크 표는 문서 담당 몫이라 만들지 않는다.
usage: python -X utf8 -B tools/gen_detail_dp3/mkbom_made_fix1.py"""
import csv, json
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/'
SRC = ROOT + 'docs/bom/FSAP_v2.31.0_made.csv'
DST = ROOT + 'docs/bom/FSAP_v2.31.1_made.csv'
mp = json.load(open(ROOT + 'tools/out/mach_props.json', encoding='utf-8'))
rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
H = rows[0]
I = {h: i for i, h in enumerate(H)}
out = [H]
n = 0
for r in rows[1:]:
    pn = r[I['품번']]
    if pn == 'P_M07_BEAM':
        r[I['질량 g(1개)']] = '%.0f' % mp[pn]['mass_g']
        r[I['비고']] = ('DP-3 수정 1회차(v2.31.1): 뒷벽 M5 탭 2개 (X 1230, Z 300 · 600)의 안쪽 끝 1 mm 막힘을 다시 뚫음(이음판 볼트 CB5-16_M07_NY:7 · :8 물림 8.0), '
                       '쓰는 부품 없는 M5 탭 6개 메움 — 아랫벽 (X −310 · −160, Y 140 · 180), 앞벽 (X −256 · −244, Z 276)(FA-M2 빈 탭 0) / ' + r[I['비고']])
        n += 1
    elif pn == 'P_M07_BEAM_CAP':
        assert 'CB5-12' in r[I['비고']], r
        r[I['비고']] = ('M5 탭 4 — 조임 1.0 N·m(상한 1.5) + 나사 고정제, M-01 예외 DP3-EX1 / DP-3 수정 1회차(v2.31.1): 덮개 볼트 CB5-12 → CB5-16 ×4(끝마다, 볼트 끝이 플랜지 안쪽 면을 4.8 지남 — CB5-12는 0.8), '
                       '덮개 형상은 그대로. 마감 덮개로만 쓴다(다른 것을 달거나 정비 때마다 여닫으면 예외가 끝난다) / ' + r[I['비고']])
        n += 1
    elif pn in ('P_M07_SPLICE_NX', 'P_M07_SPLICE_PX'):
        assert 'CB5-12' in r[I['비고']], r
        r[I['비고']] = r[I['비고']].replace('덮개 뒷벽 볼트 CB5-12 머리', '덮개 뒷벽 볼트 CB5-16(수정 1회차 v2.31.1에서 CB5-12 → CB5-16, 머리 자리는 같음) 머리', 1)
        n += 1
    out.append(r)
assert n == 4, n
with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f).writerows(out)
print('written', DST, 'rows', len(out) - 1, 'edited', n)
