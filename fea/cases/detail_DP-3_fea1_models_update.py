# -*- coding: utf-8 -*-
"""fea/models.json — 디테일링 DP-3 수정 1회차(v2.31.1). 고정 · 접촉 · 하중 줄의 뜻은 바꾸지 않는다.
 - P_M07_BEAM: 메모 note_detail_DP-3_fea1 한 줄(앞 회차 메모 note_detail_DP-3은 그대로)
 - P_M07_BEAM_CAP: 볼트 형번 CB5-12 -> CB5-16(예외 DP3-EX1 조건 ③), version v2.31.1, 조임 조건(목표 1.0 · 상한 1.5 N·m)을 criteria에, status에 수정 1회차 값
다시 돌려도 같은 결과(같은 키를 덮어씀). 실행: python -X utf8 -B fea/cases/detail_DP-3_fea1_models_update.py"""
import json
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = ROOT + '/fea/models.json'
R = json.load(open(ROOT + '/fea/results/detail_DP-3_fea1_handcalc.json', encoding='utf-8'))
G = json.load(open(ROOT + '/fea/results/detail_DP-3_fea1_stepgeo.json', encoding='utf-8'))
m = json.load(open(P, encoding='utf-8')); parts = m['parts']
HEAD = '2026-11-29 DP-3 수정 1회차(v2.31.1, 서명 587fb3c7f3bb4b2a) 손계산 fea/results/detail_DP-3_fea1_handcalc.json · 형상 detail_DP-3_fea1_stepgeo.json. FEA 못 함 — 환경 없음(D-16). '
T = R['1d_tipping']
def sf(key, case): return [v for k, v in T.items() if k.startswith(key)][0][case]['볼트 복원 포함 SF']
RUN, MIS = '운전 3 g + 끌림 Y 30 N', '오조작 3 g + 손 500 N + 끌림 Y 100 N'
dB = R['1e_open_end_distortion']['B']
bm = G['P_M07_BEAM']
parts['P_M07_BEAM']['note_detail_DP-3_fea1'] = HEAD + (
    '보 STEP 다시 읽음: 원통 축 %d -> %d(없어진 축 %d = 메운 Ø4.2 탭 6, 새 축 %d), 뒷벽 탭 (X 1230, Z 300 · 600)이 Y 312~320 전부 뚫림, 상자 그대로, 보 %.4f kg(+5.0 g). '
    '단면 · 받침 · 하중 경로 그대로라 앞 회차와 값이 같다(비교 %d줄 가운데 달라진 것은 보 질량 한 줄): 넘어짐 %s / %s, 열린 끝 찌그러짐 %s / %s(얹힘 80 띠 혼자 %s / %s). '
    '민감도(판정 근거 아님): 지금 질량 어림 %s / %s, 받침 Y 132부터 %s / %s — FEA 대기 · 하중 표 갱신은 앞 회차 메모와 같음' % (
        len(bm['prev_v2310']['cyl']), len(bm['new']['cyl']), len(bm['fix1_gone']), len(bm['fix1_born']), R['6_fix1_diff']['전체'][0]['v2.31.1'], R['6_fix1_diff']['비교 수'],
        sf('B ', RUN), sf('B ', MIS), dB[RUN]['SF'], dB[MIS]['SF'], dB['얹힘 길이 80 띠 혼자(가장 보수)']['운전 MPa · SF'][1], dB['얹힘 길이 80 띠 혼자(가장 보수)']['오조작 MPa · SF'][1],
        sf('C ', RUN), sf('C ', MIS), sf('D 지금', RUN), sf('D 지금', MIS)))
c = parts['P_M07_BEAM_CAP']; x = R['7_cap_tap_exception']
c['case'] = 'cases/detail_DP-3_handcalc.py (수정 1회차 입력: cases/detail_DP-3_fea1_handcalc.py)'
c['version'] = 'v2.31.1'
c['fixed'] = ('플랜지 2개(Y 128.2~131.2 · 308.8~311.8, 길이 25)가 보 앞 · 뒷벽 안쪽에 CB5-16 x4(X 끝에서 18, Z 350 · 550) — 덮개 플랜지 M5 탭 물림 3.0(판 두께), '
              '볼트 끝이 플랜지 안쪽 면을 4.8 지남(v2.31.0은 CB5-12 · 0.8)')
c['criteria'] = {'value': '운전 SF 3, 오조작 SF 2(SUS304 항복 205, E 193 GPa). 조임은 암나사 전단 SF >= 1(handcalc) — 조임 목표 1.0 N·m · 상한 1.5 N·m + 분해 가능한 나사 고정제',
                 'source': '요구서 6-1(M-09 기본값), M-04 판 탭, 결정로그 DP3-EX1(M-01 예외, 조건 ① · ②)'}
c['status_fix1'] = HEAD + ('한도 %s N 그대로. 조임 암나사 전단 — K 0.2: 1.0 N·m %s · 1.5 N·m %s / K 0.14(나사 고정제 윤활 가정): 1.0 N·m %s · 1.5 N·m %s(기준 1.0의 +1 %% — 상한선). '
                           '1.0 N·m에서 분리 SF %s(손 100 N), 마찰로 덮개 잡기 %s(자중 3 g). 볼트 끝 나옴 %s(불완전 나사부 2피치 가정 뒤 %s 남음). 손 100 N 웹 SF %s 그대로' % (
    x['암나사 전단 한도 N'], x['K 0.20 · 1.0 N·m']['조임 암나사 전단'], x['K 0.20 · 1.5 N·m']['조임 암나사 전단'], x['K 0.14 · 1.0 N·m']['조임 암나사 전단'], x['K 0.14 · 1.5 N·m']['조임 암나사 전단'],
    x['K 0.20 · 1.0 N·m']['분리(예압/외력)'], x['마찰로 덮개 잡기(1.0 N·m x4, μ 0.15) / 자중 3 g'], x['볼트 끝이 플랜지 안쪽 면을 지난 길이 mm(서명 상자)'],
    x['불완전 나사부 2피치(1.6, 가정) 뒤 남는 온 나사 여유 mm'], R['3_cap']['손 100 N 가운데']['t3 MPa · SF'][1]))
json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts))
print('P_M07_BEAM |', parts['P_M07_BEAM']['note_detail_DP-3_fea1'][len(HEAD):][:400])
print('P_M07_BEAM_CAP |', c['status_fix1'][len(HEAD):][:400])
