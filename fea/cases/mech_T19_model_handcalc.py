# T19 모델링부 손계산(E-18 등급 M: 형상·하중 경로가 새로 생긴 다리 묶음만). 해석 환경 없음(D-16) -> FEA 못 함, 손계산으로 판정.
# 하중: 선정 손계산 tools/out/mech_T19/select_calc.json 의 가장 큰 다리 반력(C1 배치, B_MID) 3,133.8 N. 치수는 v0.10.0 모델 실측.
# 허용치는 모두 임시(카탈로그 근사, catalog.md): 레벨링 마운트 M16 정격 10,000 N, HFS8-4080 단면적 1,200 mm2, 약축 I 25e4 mm4,
# A6063-T5 내력 110 MPa, E 69 GPa, SUS304 항복 205 MPa(전단 0.58 배), HBLFSN8 허용 1,500 N/개.
import json, math, os
R = 3133.8                     # N, 가장 큰 다리 반력(B_MID)
M_tot = 103.9 + 186.2 + 35.6   # kg, 이송 + 헤드 + 바닥틀(선정과 같은 질량표)
out = {}
# 1) 조절발 M16 정격
out['adjuster_M16_SF'] = 10000.0 / R
# 2) 다리 압축(A6063, 단면 1,200 mm2)
sig = R / 1200.0
out['leg_compress_MPa'] = sig
out['leg_compress_SF'] = 110.0 / sig
# 3) 다리 좌굴: L 138, 윗끝 형재·아랫끝 판에 브래킷으로 묶였지만 보수 쪽 K=2(한끝 자유)
L, E, I = 138.0, 69000.0, 25e4
Pcr = math.pi ** 2 * E * I / (2.0 * L) ** 2
out['leg_buckling_Pcr_N'] = Pcr
out['leg_buckling_SF'] = Pcr / R
# 4) 받침판 M16 관통 탭 나사 전단(SUS304 t16, 물림 16, 골지름 13.835, 유효 0.75)
As = math.pi * 13.835 * 16.0 * 0.75
tau = 0.58 * 205.0
out['plate_M16_thread_shear_SF'] = As * tau / R
# 5) 판 지압: 다리 아랫면(단면 1,200 mm2)이 판 윗면에 바로 앉고, 조절발 축이 다리 80 방향 가운데 -> 판 굽힘 팔 0(축이 다리 발자국 안)
out['plate_bearing_MPa'] = R / 1200.0
out['plate_bearing_SF'] = 205.0 / out['plate_bearing_MPa']
# 6) 옆 힘: 전체 무게의 0.1 g(작업자 밀기·지진 임시) 를 다리 8개가 나눔 -> 다리 뿌리 굽힘은 브래킷 2개(윗·발)가 받음
F_lat = 0.1 * M_tot * 9.81 / 8.0
Mroot = F_lat * L
out['lateral_per_leg_N'] = F_lat
out['lateral_bracket_force_N'] = Mroot / 30.0      # 브래킷 구멍 팔 30(세로판 구멍 높이)
out['bracket_SF'] = 1500.0 / out['lateral_bracket_force_N']
# 7) 세로판 CB8-16 + HNTT8-8 물림(체결은 디테일, 기록만): 가로판 t9 -> 물림 16-9-2.5 = 4.5, 세로판 자리 8.2 -> 16-8.2-2.5 = 5.3, 1.5d = 12
out['CB8_16_engage_mm'] = {"horizontal": 16 - 9 - 2.5, "vertical": 16 - 8.2 - 2.5, "need_1.5d": 12}
out['CB8_25_engage_mm'] = 25 - 9          # 판 M8 탭 물림 16 >= 12
out['min_SF'] = min(out['adjuster_M16_SF'], out['leg_compress_SF'], out['leg_buckling_SF'],
                    out['plate_M16_thread_shear_SF'], out['plate_bearing_SF'], out['bracket_SF'])
out['pass_SF2'] = out['min_SF'] >= 2.0
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mech_T19_model_handcalc.json')
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, round(v, 3) if isinstance(v, float) else v)
