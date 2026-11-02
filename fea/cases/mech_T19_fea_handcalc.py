# T19 해석부 손계산(E-18 등급 M, 해석 환경 없음 D-16 -> FEA 못 함). v0.10.0 다리 묶음.
# 모델링부 손계산(mech_T19_model_handcalc.py)은 반력에 동하중 1.5를 썼다. 해석부 지시 하중은 '자중 x3 g'이므로
# 같은 배치 반력(select_calc.json 3,133.8 N @1.5)을 3/1.5 = 2배로 올려 다시 본다. 단면적은 STEP 실측 부피/길이.
import json, math, os
here = os.path.dirname(os.path.abspath(__file__))
R15 = 3133.8                 # N, 동하중 1.5 반력(B_MID, select_calc.json)
R_static = R15 / 1.5         # 1 g
R3 = R_static * 3.0          # 3 g (지시 하중)
A_leg = 153898.2 / 138.0     # mm2, 다리 STEP 실측(단면 실물 460에서 자름)
M_tot = 103.9 + 186.2 + 35.6
g = 9.81
out = {'R_1g_N': R_static, 'R_3g_N': R3, 'A_leg_mm2_measured': A_leg}
cases = {}
# 1) 조절발 M16 정격 10 kN(임시, catalog.md, D-76)
cases['adjuster_M16'] = {'load_N': R3, 'cap_N': 10000.0, 'SF': 10000.0 / R3, 'SF_at_1.5': 10000.0 / R15,
                         'need_rating_for_SF2_N': 2 * R3}
# 2) 다리 압축 A6063-T5 110 MPa
s = R3 / A_leg
cases['leg_compress'] = {'MPa': s, 'SF': 110.0 / s}
# 3) 다리 좌굴(약축 I 25e4 근사, K=2 보수)
Pcr = math.pi ** 2 * 69000.0 * 25e4 / (2 * 138.0) ** 2
cases['leg_buckling'] = {'Pcr_N': Pcr, 'SF': Pcr / R3}
# 4) 받침판 굽힘: 조절발 힘이 판 가운데(다리 80 방향 가운데)에 들고, 다리 벽이 판을 X 방향 80 간격 양끝에서 받는 단순보로 본다
#    (중간 웹·폭 방향 벽 지지 무시 = 보수). 폭 40, t16. 판 아래 잠금 너트 맞변 24가 하중을 판에 넣음 -> 집중하중
L, b, t = 80.0, 40.0, 16.0
M = R3 * L / 4.0
Z = b * t ** 2 / 6.0
sb = M / Z
cases['plate_bending'] = {'M_Nmm': M, 'MPa': sb, 'SF': 205.0 / sb,
                          'defl_mm': R3 * L ** 3 / (48 * 193000.0 * b * t ** 3 / 12.0)}
# 5) 판 M16 탭 나사 전단(SUS304, 물림 16, 골지름 13.835, 유효 0.75)
As = math.pi * 13.835 * 16 * 0.75
cases['plate_M16_thread'] = {'SF': As * 0.58 * 205.0 / R3}
# 6) 다리 아랫면 지압(판 SUS304)
cases['plate_bearing'] = {'MPa': R3 / A_leg, 'SF': 205.0 / (R3 / A_leg)}
# 7) 옆 힘 0.1 g x 3 = 0.3 g(작업자 밀기·충격 임시), 다리 8 분담, 뿌리 굽힘을 브래킷(구멍 팔 30)이 받음
F_lat = 0.3 * M_tot * g / 8.0
Fb = F_lat * 138.0 / 30.0
cases['lateral_bracket'] = {'F_lat_per_leg_N': F_lat, 'bracket_N': Fb, 'cap_N': 1500.0, 'SF': 1500.0 / Fb}
# 8) 조절발 나사 기둥 굽힘(옆 힘을 기둥이 받는 경우, 판 밑 ~ 받침 팔 최대 66+15=81, 골지름 13.835)
d1 = 13.835
Mc = F_lat * 81.0
sc = Mc / (math.pi * d1 ** 3 / 32.0)
cases['adjuster_stud_bending'] = {'MPa': sc, 'SF_vs_235': 235.0 / sc}
# 9) 레일 높이 차 민감도: 형재 강축 I 근사 96e4 (D-17). 차는 1/I 에 비례
diff, allow = 0.126, 0.201
cases['rail_height_diff'] = {'diff_mm': diff, 'allow_mm': allow, 'I_used': 96e4,
                             'I_min_for_allow': 96e4 * diff / allow,
                             'note': '자중 1 g 정적 처짐 기준(레벨링 뒤 남는 차). 3 g는 강도에만 씀'}
out['cases'] = cases
sfs = {k: v.get('SF', v.get('SF_vs_235')) for k, v in cases.items() if ('SF' in v or 'SF_vs_235' in v)}
out['min_SF'] = min(sfs.values())
out['min_at'] = min(sfs, key=sfs.get)
json.dump(out, open(os.path.join(here, '..', 'results', 'mech_T19_fea_handcalc.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in sfs.items():
    print(k, round(v, 2))
print('R3', round(R3, 1), 'plate MPa', round(cases['plate_bending']['MPa'], 1), 'Imin', cases['rail_height_diff']['I_min_for_allow'])
