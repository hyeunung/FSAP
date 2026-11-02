# -*- coding: utf-8 -*-
"""T15 손계산 — T05 안내 블록 P_T05_GUIDE (v0.8.1). 해석 못 함 — 환경 없음(자료대기 D-16).
앞벽 오조작B(DP-3 기준 417.5 N)를 새 천장 밑면 Z 76.5 기준으로 다시 따지고, 위판(데크) 외팔을 본다.
PET-CF FDM 허용 30 MPa(층간 보수값, DP-3와 같음). 실행: python -B fea/cases/mech_T15_handcalc.py
"""
S_ALLOW = 30.0  # MPa, PET-CF FDM 층간 보수값(DP-3)


def cant(F, L, b, t):
    M = F * L
    sig = 6.0 * M / (b * t * t)
    return M, sig, S_ALLOW / sig


rows = []
# 앞벽 오조작B: 패드 옆 하중 417.5 N이 Z 45에 걸림, 앞벽 b 59(X 방향 지지 폭), t 9.2
for name, L in (("앞벽 오조작B v0.8.0(뿌리 위판 밑 85.5까지 40.5)", 40.5),
                ("앞벽 오조작B v0.8.1(새 천장 밑면 76.5까지 31.5)", 31.5)):
    M, s, sf = cant(417.5, L, 59.0, 9.2)
    # 두 변 지지(밑판·천장 양쪽 고정) ~ 외팔 모멘트의 1/2
    rows.append((name, M, s, sf, 2 * sf, 2 * sf / 1.3))
# 데크 외팔: 탑 앞면 X -114 → 실린더 축 X -126.9, L 12.9, b 35, t 4
for name, F in (("데크 운전 0.7 MPa (CJ2B10 Ø10, 54.98 N)", 3.14159265 * 5 ** 2 * 0.7),
                ("데크 운전 0.5 MPa", 3.14159265 * 5 ** 2 * 0.5),
                ("데크 오조작 100 N(가정, D-57)", 100.0)):
    M, s, sf = cant(F, 12.9, 35.0, 4.0)
    rows.append((name, M, s, sf, None, sf / 1.5))
for r in rows:
    name, M, s, sf, sf2, kt = r
    extra = ("  두 변 SF %.2f, Kt1.3 %.2f" % (sf2, kt)) if sf2 else ("  Kt1.5 %.2f" % kt)
    print("%s: M %.0f N·mm, σ %.2f MPa, 외팔 SF %.2f%s" % (name, M, s, sf, extra))
# 데크 처짐(운전 0.7 MPa), E 2.5 GPa(D-57)
E = 2500.0
F = 3.14159265 * 25 * 0.7
I = 35.0 * 4.0 ** 3 / 12.0
d = F * 12.9 ** 3 / (3 * E * I)
th = F * 12.9 ** 2 / (2 * E * I)
print("데크 처짐 %.3f mm, 기울기 %.4f rad, 패드 X 흔들림(로드+패드 34.5) %.2f mm" % (d, th, th * 34.5))
