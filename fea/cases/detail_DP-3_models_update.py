# -*- coding: utf-8 -*-
"""fea/models.json — 디테일링 DP-3(v2.31.0). 고정 · 접촉 · 하중 줄은 바꾸지 않고 메모(note_detail_DP-3)만 더한다. 새 부품 P_M07_BEAM_CAP 한 줄을 더한다(E-18 "표에 없는 부품은 실제 조립 경계조건으로 정해 더한다").
다시 돌려도 같은 결과(같은 키를 덮어씀). 실행: python -X utf8 -B fea/cases/detail_DP-3_models_update.py"""
import json
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = ROOT + '/fea/models.json'
R = json.load(open(ROOT + '/fea/results/detail_DP-3_handcalc.json', encoding='utf-8'))
m = json.load(open(P, encoding='utf-8')); parts = m['parts']
K = 'note_detail_DP-3'
HEAD = '2026-11-28 DP-3(v2.31.0) 손계산 fea/results/detail_DP-3_handcalc.json · 형상 detail_DP-3_stepgeo.json. FEA 못 함 — 환경 없음(D-16). '
T = R['1d_tipping']
def sf(key, case): return [v for k, v in T.items() if k.startswith(key)][0][case]['볼트 복원 포함 SF']
RUN, MIS = '운전 3 g + 끌림 Y 30 N', '오조작 3 g + 손 500 N + 끌림 Y 100 N'
dB = R['1e_open_end_distortion']['B']
notes = {
 'P_M07_BEAM': '끝판 2장을 떼어 끝 단면이 열림(덮개는 가로막으로 세지 않음), 관통 탭 19 · Ø5.5 4. 고정 · 하중 줄은 v2.3.4 그대로 두고 같은 식으로 다시 풂: 표 모델 %s / %s, 지금 경간 3650(기둥 PX X 1270~1350) · 보 270.25 kg %s / %s(DP-3 몫 -0.01). '
               '민감도(판정 근거 아님): 지금 서명 질량 어림 %s / %s, 받침을 바깥 R12 접점 Y 132부터로 보면 %s / %s. 새 항 — 열린 끝 단면 찌그러짐(탄성 받침 위 보 유추): 벽 굽힘 SF %s / %s, 얹힘 80 띠 혼자 %s / %s. '
               '하중 표(헤드 67.24 · HMI 없음 · 레귤레이터 6 kg)는 v2.3.4 값이라 전체 해석부가 고쳐야 함' % (
     sf('A ', RUN), sf('A ', MIS), sf('B ', RUN), sf('B ', MIS), sf('C ', RUN), sf('C ', MIS), sf('D 지금', RUN), sf('D 지금', MIS),
     dB[RUN]['SF'], dB[MIS]['SF'], dB['얹힘 길이 80 띠 혼자(가장 보수)']['운전 MPa · SF'][1], dB['얹힘 길이 80 띠 혼자(가장 보수)']['오조작 MPa · SF'][1]),
 'P_M07_SPLICE_NX': '덮개 볼트 머리 구멍 Ø10 x2(X 끝에서 18, Z 350 · 550). 순단면 x Kt 3: %s MPa SF %s(구멍 없을 때 %s MPa). 넘어짐 SF는 보와 같음' % (
     R['2_splice']['x Kt 3 MPa'], R['2_splice']['SF'], R['2_splice']['전체 단면(구멍 없음) MPa']),
 'P_M08_TUBE_FIXTURES(RISER·SO·KDM·CAR·ARM·U6·COMB_ML·CLAMP_F/L)': '26품번(COMB_ML_1~9 · COMB_U5_1 · 2 · CLAMP_F_1~6 · L_1~6 · SO_1~3) 재질 A5052 -> PET-CF: 기준값 항복 60 MPa(handcalc 표) · E 5,000 · 층간 0.5배, 한계 면압 60. '
     '고정 · 하중 그대로. 가장 약한 것 CLAMP_SO_2 · 3 오조작 %s(층간이면 %s), 관 빗 %s. 머리 좌면 41개: 4.5 N·m 0.44 -> 1.5 N·m 지정 1.32(소형 평와셔 Ø9 + 2.0 N·m 1.20). 턱(높이 3.1 · 살 3.6) 혼자 %s' % (
     R['4_pet_cf_parts']['CLAMP_SO_2 · SO_3(판 t8 폭 20, 외팔 38)']['SF'], R['4_pet_cf_parts']['CLAMP_SO_2 · SO_3(판 t8 폭 20, 외팔 38)']['층간(0.5배 30 MPa)로 보면'],
     R['4_pet_cf_parts']['COMB_ML_7(높이 68 — 가장 불리)']['SF(PET-CF 60)'], R['4_pet_cf_parts']['턱(돌림 막음)']['턱 혼자(볼트 풀림) SF']),
}
notes['P_M07_SPLICE_PX'] = notes['P_M07_SPLICE_NX']
for k, v in notes.items():
    assert k in parts, k
    parts[k][K] = HEAD + v
c = R['3_cap']
parts['P_M07_BEAM_CAP'] = {
 'case': 'cases/detail_DP-3_handcalc.py', 'step': 'tools/out/detail/DP-3/stepout/P_M07_BEAM_CAP.step', 'version': 'v2.31.0',
 'fixed': '플랜지 2개(Y 128.2~131.2 · 308.8~311.8, 길이 25)가 보 앞 · 뒷벽 안쪽에 CB5-12 x4(X 끝에서 18, Z 350 · 550) — 덮개 플랜지 M5 탭 물림 3.0(판 두께)',
 'contact': '보 안벽과 틈 0.2(옆) · 0.5(위 · 아래). 웹 바깥면 = 보 끝면. 보의 가로막 노릇은 하지 않는다고 봄',
 'load': '운전: 자중 2.03 kg x 3 g(볼트 전단). 오조작: 손 100 N 웹 가운데(D-38 전 임시) — 플랜지 사이 177.6 단순 받침, 점 하중 유효 폭 20 + 0.6 L',
 'criteria': {'value': '운전 SF 3, 오조작 SF 2(SUS304 항복 205, E 193 GPa). 조임은 암나사 전단 SF >= 1(handcalc)', 'source': '요구서 6-1(M-09 기본값), M-04 판 탭'},
 'status': HEAD + '손 100 N 웹 %s MPa SF %s(처짐 %s mm). 탭 물림 3.0 암나사 전단 한도 %s N -> 4.5 N·m 0.48 · 2.0 N·m 1.09 · 1.5 N·m 1.45 · 1.0 N·m 2.17' % (
     c['손 100 N 가운데']['t3 MPa · SF'][0], c['손 100 N 가운데']['t3 MPa · SF'][1], c['손 100 N 가운데']['처짐 t3 mm'], c['탭 물림 3.0 조임']['암나사 전단 한도 N'])}
json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts), 'DP-3 메모', len(notes), '+ 새 줄 P_M07_BEAM_CAP')
for k in notes: print(k[:40], '|', parts[k][K][len(HEAD):][:200])
