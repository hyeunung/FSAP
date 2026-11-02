# 상용 자동 카매트·카펫 바인딩(테두리 봉제) 기계 조사

조사일 2026-11-03. 공개 웹 자료만 봤다. 출처 신뢰도 표시:
- **[원문]** WebFetch로 페이지 본문을 직접 읽어 확인.
- **[검색요약]** 원 페이지가 403 등으로 열리지 않아 검색엔진 요약문으로만 확인. 원문 대조가 필요하다.

대상 기계 목록(찾은 것):
1. RI.MA.C. R375X (이탈리아) — 테이프 바인딩, 헤드 고정·매트 회전
2. RI.MA.C. R375A / R375A-SC (이탈리아) — 테이프 바인딩, 헤드 Durkopp 867-290342 개조
3. Richpeace 자동 매트(지면 매트) 바인딩기 (중국 톈진) — 로딩·배출 매니퓰레이터 포함 라인형
4. Van de Wiele(Vandewiele) TITAN 계열 (벨기에) — TITAN 2530AG/DK2530 AG·2530AHC(카매트 테이프 바인더), DK4640S·5540·5540M(카매트 자동 오버에징 로봇)
5. Dürkopp Adler 867-392342-M (독일) — 카매트 바인딩용 평판 재봉기 헤드(수동 기계, 헤드 참고용)
6. 중국 무명 "Full Automatic Mat Overedging Machine" (china.org.ru 목록) / Suzhou Artisan 특허(CN209114134U)
7. 일본 Matsuka US5493980 (상용 기계 여부 불명, 카매트 전용 특허)
8. 네덜란드 Willems 카매트 오버에징 자동기 (페이지 열기 실패)
- 한국: 상용 자동 카매트 바인딩기를 찾지 못했다.
- 미국 Gaylord 등 카펫 바인더: 이번 검색에서 자동(조향 포함) 카매트 기계로 나오는 것은 없었다. 휴대형 카펫 바인더 특허만 나왔다(US6055918, US7124696 — 본문 미확인).

---

## 1. 누가 매트를 이송하나 — 재봉 헤드의 자체 이송(톱니·바늘이송·교대 노루발·풀러)인가, 기계 축(X/Y/회전 서보)인가?

### Takeaway
공개 자료로 이송 방식을 밝힌 상용 기계는 거의 없다. R375A는 Durkopp 867 계열(헤드 자체 이송) 헤드를 쓰고 매트를 움직이는 별도 장치("car-mat moving")가 있다고만 하며, Richpeace는 "상하 프레스 휠"이 봉제 방향을 잡는다. TITAN 로봇형은 로봇 팔이 매트를 헤드로 가져간다. Matsuka 특허와 Suzhou Artisan 특허는 롤러/벨트가 매트 면을 눌러 이송한다.

### Cited Findings
- R375X: "modified sewing head structure"로 봉제 중 매트가 자유롭게 움직이게 했고, "modified feeding system"과 새 테이프 커팅 유닛으로 매트가 헤드 밑을 지나가 회전 공간이 늘었다. 이송 기구의 종류(톱니·풀러·서보 축)는 적혀 있지 않다. [원문] — [rimac.it R375X](https://www.rimac.it/en/products/r375x/)
- R375A: "a particular system of edge reading and car-mat moving"으로 여러 형상을 바인딩한다. 이동 기구 상세 없음. [원문] — [rimac.it R375](https://www.rimac.it/en/products/r375/)
- R375A 헤드는 "DURKOPP 867-290342 specially modified for binding". [원문] — [rimac.it R375](https://www.rimac.it/en/products/r375/)
- 같은 867 계열의 현행 카매트 바인딩 모델 867-392342-M: "High top feed stroke up to 9 mm"(상부 이송 스트로크), 최대 땀 길이 12 mm, 좁은 내·외 반경용 "Preselectable second stitch length". 이송 방식의 이름(바늘이송·교대 노루발 등)은 페이지에 없다. [원문] — [Dürkopp Adler 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- 867 계열 중고 목록 867-290322M, 867-290142M은 "triple-feed"(3중 이송)로 기재. [검색요약] — [machineseeker 867-290322M](https://www.machineseeker.com/durkopp+adler-867-290322m/i-18408171)
- Richpeace: 가변 센서가 매트 외곽을 감지해 "upper and lower press wheels"(상하 프레스 휠)에 신호를 보내 봉제 방향을 제어한다. [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- TITAN 5540(카매트 자동 오버에징): 매트를 하나씩 집어 "airtable"(에어 테이블)에 놓고, 로봇 팔이 재봉 헤드로 공급한다. [검색요약, 카탈로그 PDF 403] — [directindustry TITAN 5540 PDF](https://pdf.directindustry.com/pdf/vandewiele/titan-5540/172691-1134635.html)
- Matsuka US5493980(카매트용, 1996 등록, 소멸): 프레임에 고정된 여러 이송 롤러(축이 바늘 쪽을 향함)를 모터가 벨트로 정·역 구동. 위쪽 누름 롤러를 실린더로 3단(누름/살짝 띄움/완전 올림) 승강. 매트를 놓는 테이블은 고정. [원문] — [Google Patents US5493980A](https://patents.google.com/patent/US5493980A/en)
- Suzhou Artisan CN209114134U(바닥매트 테이핑기, 2018 출원, 소멸): 서보 모터가 구동하는 롤러 프레임에 고무 이송 벨트, 수직 실린더로 내려 매트를 누르고 봉제선을 따라 이동시킨다. [원문] — [Google Patents CN209114134U](https://patents.google.com/patent/CN209114134U/en)

### Inferences
- (추정) R375A는 Durkopp 867(3중 이송 계열) 헤드를 쓰므로 직선 이송은 헤드 자체 이송, 방향 전환은 별도 "car-mat moving" 장치로 보인다. R375X는 "modified feeding system"을 언급하므로 이송 방식을 바꾼 것으로 보이나 무엇으로 바꿨는지는 알 수 없다.
- (추정) Richpeace의 "상하 프레스 휠"은 매트 위아래를 물고 회전 방향을 주는 휠로 읽힌다. 파일 면을 휠이 누를 가능성이 높다(C-03 관점의 위험).

### Gaps
- R375X·R375A의 이송·회전 기구 상세(서보 축 여부, 회전 중심)는 공개 자료에 없다. 브로셔·영상도 찾지 못했다.
- TITAN 로봇이 봉제 중에도 매트를 쥐고 조향하는지, 헤드 이송에 맡기는지 확인 못 함.

---

## 2. 매트를 어떻게 잡나(진공 테이블·클램프·판·롤러·매니퓰레이터), 파일 면을 누르는 것이 있나?

### Takeaway
상용 기계 페이지는 잡는 방식을 거의 밝히지 않는다. 확인된 것은 TITAN의 에어 테이블(+로봇 팔), Richpeace의 매니퓰레이터 로딩과 상하 프레스 휠, 특허 쪽의 롤러·벨트 누름(Matsuka, Suzhou Artisan)이다. 롤러·벨트로 면을 누르는 방식은 이 기계가 피하려는 방식이다.

### Cited Findings
- R375X·R375A: 잡는 방법은 적혀 있지 않다. 작업자가 손으로 올리고 시작. [원문] — [R375X](https://www.rimac.it/en/products/r375x/), [R375](https://www.rimac.it/en/products/r375/)
- R375A 옵션 "Habraken system": 일부 누벅 테이프의 장력을 줄여 완성 매트를 더 평평하게. [원문] — [R375](https://www.rimac.it/en/products/r375/)
- Richpeace: 공급 트레이가 정위치로 자동 상승, 매니퓰레이터가 매트를 집어 봉제 영역으로. 봉제 중 잡는 방식은 미기재(프레스 휠만 언급). [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- TITAN 5540: 매트를 에어 테이블에 놓고 로봇 팔이 헤드로 공급. [검색요약] — [TITAN 5540 PDF](https://pdf.directindustry.com/pdf/vandewiele/titan-5540/172691-1134635.html)
- Matsuka US5493980: 노루발이 매트를 누르고, 봉제 후 가장자리 들뜸을 막는 평판 누름 패드(승강 실린더)가 따로 있다. 누름 롤러는 "at both surfaces"를 누른다. [원문] — [US5493980A](https://patents.google.com/patent/US5493980A/en)
- Suzhou Artisan CN209114134U: 이송 벨트가 "directly pressed against the surface of the floor mat fabric"(매트 원단 면에 직접 눌림). [원문] — [CN209114134U](https://patents.google.com/patent/CN209114134U/en)

### Inferences
- (추정) 에어 테이블(TITAN)은 매트를 띄워 마찰을 줄이는 용도로 보이며, 면을 누르지 않고 매트를 움직이는 상용 사례로 참고할 만하다. 실제 구조(공기 분출 vs 흡착)는 미확인.

### Gaps
- R375X의 잡기 방식(진공·클램프 유무)은 공개되지 않았다. 이 기계 설계에서 가장 궁금한 부분이지만 답이 없다.

---

## 3. 회전·조향은 어떻게, 어느 중심으로 하나? 헤드가 도나?

### Takeaway
R375X는 "automatic piece rotation"(매트 자동 회전)이라고만 하고 중심은 밝히지 않는다. 회전 중심을 밝힌 자료는 특허뿐이다: Matsuka는 이송 롤러를 역회전시켜 바늘을 중심으로 약 90° 돌리고, Suzhou Artisan은 바늘을 중심으로 회전하는 서보 레버로 돌린다. 헤드가 도는 상용 기계는 확인되지 않았다.

### Cited Findings
- R375X: "profile reading system, combined with automatic piece rotation, allows precise processing of complex shapes." 헤드 이동 여부는 미기재. [원문] — [R375X](https://www.rimac.it/en/products/r375x/)
- Richpeace: 센서 신호를 받은 상하 프레스 휠이 봉제 방향을 제어. 회전 중심 미기재. [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- Matsuka US5493980: 코너에서 누름 롤러가 매트를 물고 이송 롤러가 역회전해 매트를 바늘 둘레로 약 90° 돌린다. [원문] — [US5493980A](https://patents.google.com/patent/US5493980A/en)
- Suzhou Artisan CN209114134U: 바늘을 회전 중심으로 하는 레버를 서보 모터가 돌리고, 레버 아래 끝의 배플(수직 실린더로 승강)이 매트 옆면을 밀어 돌린다. [원문] — [CN209114134U](https://patents.google.com/patent/CN209114134U/en)

### Inferences
- (추정) 바늘점 중심 회전이 특허 쪽의 공통 해법이다. R375X도 매트가 헤드 밑을 지나며 돈다는 설명상 바늘 근처 중심 회전일 가능성이 있으나 근거 없음.

### Gaps
- R375X/R375A 회전 축(서보 회전 테이블인지, 롤러 차동인지), 회전 속도, 회전 중심 — 공개 자료 없음.
- TITAN 로봇형의 조향 방식(로봇이 돌리는지) 미확인.

---

## 4. 가장자리 센서의 종류와 위치

### Takeaway
상용 기계는 센서 종류를 공개하지 않는다("profile reading", "edge reading", "variable sensor"). 특허 쪽에서는 접촉식 스윙암+엔코더(Matsuka, 광센서는 보조), 스프링 감지 암(US6557478), 광센서(US5216969) 등이 쓰였다.

### Cited Findings
- R375X "profile reading system", R375A "edge reading". 센서 종류·위치 미기재. [원문] — [R375X](https://www.rimac.it/en/products/r375x/), [R375](https://www.rimac.it/en/products/r375/)
- R375X·R375A: 형상 자동 인식으로 매트 형상마다 프로그램할 필요가 없다. [원문] — [R375X](https://www.rimac.it/en/products/r375x/), [R375](https://www.rimac.it/en/products/r375/)
- Richpeace: "variable sensor"가 외곽을 감지. [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- TITAN DK4640S(2011년식 중고): 형상 프로그램 없이 헤드가 매트를 찾아 봉제 시작. TITAN 5540 계열은 "reads and measures the shape of the carpet". [검색요약] — [wotol DK4640S](https://www.wotol.com/product/titan-dk4650-60-x-100-cm-automatic-overedging-system-for-car-mats/1810328)
- Matsuka US5493980: 주 센서는 로터리 엔코더 축에 피벗한 C자 스윙암, 암의 감지 바가 스프링으로 매트 가장자리에 닿고 엔코더가 각도를 읽는다. 보조로 매트 위아래 광센서 한 쌍(주로 큰 반경 코너). 쓰러진 파일이 광센서를 헷갈리게 해서 기계식 암을 주 센서로 했다. [원문] — [US5493980A](https://patents.google.com/patent/US5493980A/en)
- US6557478: 스프링 센서에 연결된 감지 암 2개로 가장자리 위치를 감지하며 센서는 선형 변위 트랜스듀서(LVDT류). [검색요약] — [Google Patents US6557478](https://patents.google.com/patent/US6557478)
- Suzhou Artisan CN209114134U: 매트 가장자리 센서, 침판 위 초기 위치 센서, 실 끊김 센서 등. 종류 미기재. [원문] — [CN209114134U](https://patents.google.com/patent/CN209114134U/en)

### Inferences
- (추정) 파일이 긴 카매트에서는 광센서가 쓰러진 파일에 속을 수 있다는 Matsuka의 지적이 이 기계 센서 선정에 직접 참고가 된다(접촉식 또는 측면 투과식 고려).

### Gaps
- 상용 기계의 센서 종류·바늘 앞 거리 — 어디에도 공개 없음.

---

## 5. 코너·오목 곡선·좁은 홈 처리(정지·바늘 내림·노루발 올림·회전)

### Takeaway
코너 처리를 밝힌 상용 자료는 TITAN 2530AG의 "내·외 코너 모두 테이프 봉제, 최소 내측 반경 30 mm"와 "코너마다 노루발·바늘을 올린 채 자동 정지"(둘 다 검색요약)가 거의 유일하다. Dürkopp 867-392342-M은 좁은 반경용 두 번째 땀 길이를 둔다. 좁은 V·U 홈을 처리한다고 밝힌 상용 기계는 없다.

### Cited Findings
- TITAN 2530AG: 테이프를 매트 가장자리에 "both internal and external corners"로 봉제, "minimum internal radius of 30 mm". [검색요약, 원 페이지 403] — [directindustry Van de Wiele](https://www.directindustry.com/prod/van-de-wiele/product-172691-2046145.html)
- TITAN 2530AG(같은 페이지): "automatically stop at every corner with pressure foot and needle up". [검색요약] — [directindustry Van de Wiele](https://www.directindustry.com/prod/van-de-wiele/product-172691-2046145.html)
- TITAN 4500AHC: "Allows easy sewing of inner turns." [원문] — [vandewiele.com overedging](https://vandewiele.com/textile-solutions/sewing/overedging)
- Dürkopp 867-392342-M: 용도 "car mats and folding tops of convertibles", "flat workpieces with inner and outer radii". 좁은 내·외 반경용 두 번째 땀 길이 선택, 노루발 최대 20 mm 들어올림, 공압 노루발 리프트, 자동 되박음. [원문] — [Dürkopp 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- Matsuka US5493980: 작업자가 코너 수를 입력(예시 5개). 코너 감지 시 이송 피치를 줄이고 매트를 돌린 뒤 표준 피치로 복귀. 안쪽(오목) 곡선은 피치를 길게·이송을 빠르게. 마지막 코너 뒤 타이머로 정지. [원문] — [US5493980A](https://patents.google.com/patent/US5493980A/en)
- R375X/R375A: 코너·홈 처리 방식 미기재. [원문] — [R375X](https://www.rimac.it/en/products/r375x/)

### Inferences
- (추정) 상용 테이프 바인더의 오목 한계는 내측 반경 30 mm 수준(TITAN 2530AG)으로 보인다. 이보다 좁은 V·U 홈은 공개된 상용 기계가 다루지 않는다 — 이 기계의 차별점이 될 수 있다. 단 TITAN 수치는 원문 미확인.
- (추정) TITAN 2530AG의 "노루발·바늘 올린 채 정지"는 반자동(작업자가 돌림) 기계의 동작으로 읽힌다. US5367966의 "바늘 내림+노루발 올림 회전"과는 다르다.

### Gaps
- R375X의 최소 오목 반경·홈 처리 — 공개 없음(자료대기 D-14 그대로).
- TITAN 2530AG 원문(403) 대조 필요.

---

## 6. 테이프 공급(롤·서보 공급·장력), 테이프 절단, 열절단

### Takeaway
R375 계열은 테이프 커팅 유닛과 열절단 옵션, 장력 저감 옵션(Habraken)을 둔다. Dürkopp 867-392342-M은 "차동 바인딩 장치"로 무장력 테이프 공급을 한다. Van de Wiele는 테이프 폭 22~150 mm를 다룬다고 한다. 서보 공급 구조를 밝힌 것은 Suzhou Artisan 특허뿐이다.

### Cited Findings
- R375X: 새 테이프 커팅 유닛(표준), 옵션 "Hot tape cutting" — 올 풀림 방지를 위해 열절단이 필요한 테이프용. [원문] — [R375X](https://www.rimac.it/en/products/r375x/)
- R375A: 옵션 "TAPE HOT CUT SYSTEM"(풀림 방지), "Habraken system"(누벅 테이프 장력 저감). [원문] — [R375](https://www.rimac.it/en/products/r375/)
- Dürkopp 867-392342-M: "differential moving binding device for a tension-free tape feed", 버튼으로 차동 단계 선택, 한쪽·양쪽 접힘 또는 열린 끝 테이프 대응, 여러 표준 바인딩 어태치먼트와 맞춤 어태치먼트, 실 자르개. [원문] — [Dürkopp 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- Van de Wiele 테이프 바인딩: "Tapes from 22 mm till 150 mm can be sewn on the edge of carpets." 카매트용은 TITAN 2530AHC(사진 라벨 "Titan DK2530 AG"). [원문] — [vandewiele.com tape-binding](https://vandewiele.com/textile-solutions/sewing/tape-binding)
- Richpeace: 라벨 자동 길이 당김·절단·마킹, 자동 트리머. 테이프 공급 기구 미기재. 오버록 폭 5 mm 또는 10 mm. [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- Suzhou Artisan CN209114134U: 테이프가 접힘·공급 조립체를 지나며 공압 푸시로드가 슬롯으로 밀고, 바늘 안쪽 당김 실린더로 들어가며, 공압 핀이 바늘 위치까지 밀고 에어 분사가 안내. 절단은 공압 판이 테이프를 반 접어 두 개의 헤링본 날 사이로 밀어 바깥 날이 닫히며 자른다. 절단 뒤 끝을 두 겹으로 접는다. [원문] — [CN209114134U](https://patents.google.com/patent/CN209114134U/en)

### Gaps
- R375X 테이프 폭·공급 방식(서보 여부)·장력 제어 — 공개 없음.

---

## 7. 시작·끝 이음매 처리(겹침 길이, 접어 넣기, 맞대기)

### Takeaway
시작·끝 처리를 밝힌 상용 자료는 TITAN 5540의 "로봇이 매트를 당겨 실을 자르고 마지막 땀을 뒤에서 초음파 용착으로 고정"(오버에징, 검색요약)뿐이다. 테이프 바인딩 이음매(겹침·접기) 수치는 어디에도 없다. Suzhou Artisan 특허는 테이프 끝을 접어 두 겹으로 마무리한다.

### Cited Findings
- TITAN DK4640/5540: 곡선 봉제 후 로봇이 매트를 당기고, 마지막 땀을 뒤에서 초음파 용착으로 고정, 실을 자른 뒤 완성 매트를 팔레트에 적재. [검색요약] — [TITAN 5540 PDF](https://pdf.directindustry.com/pdf/vandewiele/titan-5540/172691-1134635.html), [wotol DK4640S](https://www.wotol.com/product/titan-dk4650-60-x-100-cm-automatic-overedging-system-for-car-mats/1810328)
- Suzhou Artisan CN209114134U: 테이프 절단 뒤 접힘 판·삽입 판으로 꼬리 끝을 두 겹으로 접는다. 라벨은 공압 그리퍼가 서보 벨트 레일로 바늘까지 옮겨 바인딩과 함께 봉제. [원문] — [CN209114134U](https://patents.google.com/patent/CN209114134U/en)
- Dürkopp 867-392342-M: 자동 되박음(backtacking). [원문] — [Dürkopp 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)

### Gaps
- R375X/R375A/Richpeace의 시작·끝 처리 — 공개 없음. 겹침 길이 수치 출처 없음.

---

## 8. 배출, 사이클 타임, 매트 크기, 전원, 공기, 설치 면적, rpm, 헤드 모델

### Takeaway
수치가 있는 기계는 R375X, R375A, Richpeace, TITAN DK4640S, 중국 무명 오버에징기다. 모두 2000 rpm 근처(TITAN 3200, 중국 무명 최대 3500)이고, 헤드 모델을 밝힌 것은 R375A(Durkopp 867-290342 개조)뿐이다.

### Cited Findings

| 기계 | 배출 | 사이클 | 매트 크기 | 전원·공기 | 면적·무게 | 속도 | 헤드 | 출처 |
|---|---|---|---|---|---|---|---|---|
| R375X | 미기재. 수동 로딩, 1명이 최대 3대 | 미기재(재질·크기·땀길이·형상·로딩속도에 따라) | 20×30 ~ 120×120 cm, 요청 시 150×150 | 220 V 50/60 Hz, 2000 W, 6 bar | 미기재 | 최대 2000 rpm | 미기재 | [원문] [R375X](https://www.rimac.it/en/products/r375x/) |
| R375A | 기계 뒤로 자동 배출 | 앞좌석 약 45~50 s, 뒷좌석 약 35~40 s(봉제만, 로딩 제외) | 최대 80×60 cm | 220 V 50/60 Hz, 2000 W, 6 bar | 미기재 | 2000 rpm | Durkopp 867-290342 바인딩용 개조 | [원문] [R375](https://www.rimac.it/en/products/r375/) |
| R375A-SC | 수동 배출 | 위와 같음 | 위와 같음 | 위와 같음 | 미기재 | 2000 rpm | 위와 같음 | [원문] [R375](https://www.rimac.it/en/products/r375/) |
| Richpeace 자동 매트 바인딩기 | 배출 매니퓰레이터 → 배출 트레이 | 미기재 | 모델명에 "1300×700"(정의 없음) | 6 kW, 3P380. 공기 미기재 | 설치 4300×2400×2300 mm | 2000 rpm | 미기재. 10.2인치 조작 화면 | [원문] [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html) |
| TITAN DK4640S (2011 중고) | 로봇 배출·팔레트 적재 | 미기재 | 60×100 cm | 미기재 | 안전 펜스 | 3200 땀/분, 땀 폭 12 mm | 미기재 | [검색요약] [wotol](https://www.wotol.com/product/titan-dk4650-60-x-100-cm-automatic-overedging-system-for-car-mats/1810328) |
| TITAN 5540 | 로봇 팔레트 적재. 1명이 최대 4대 감독 | 미기재 | 미기재 | 미기재 | 미기재 | 미기재 | 미기재 | [검색요약] [TITAN 5540 PDF](https://pdf.directindustry.com/pdf/vandewiele/titan-5540/172691-1134635.html) |
| 중국 무명 "Full Automatic Mat Overedging Machine"(오버에징·절단·네 변 접기) | 미기재 | 350 pcs/h | 60~90 cm | 380 V, 5 kW, 공기 >0.6 MPa | 900×200×200 cm, 1450 kg | 2000~3500 r/min | 미기재. 가격 US$93,400~98,070 | [검색요약, 403] [china.org.ru](https://china.org.ru/product/60663811226) |
| Dürkopp 867-392342-M(헤드) | — | — | — | 헤드 직결 구동 | — | 최대 3000 땀/분, 땀 길이 최대 12 mm, 노루발 리프트 20 mm, 실 Nm 10/3 | 자체 | [원문] [Dürkopp](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html) |

- Richpeace 기계 구성: 자동 공급·자동 바인딩·자동 라벨링·자동 배출 4부분. 옵션 자동 마킹(문자·날짜·QR). [원문] — [richpeace.com](https://www.richpeace.com/cnc_sewing_for_hometextile-show-1286.html)
- R375X·R375A 모두 터치스크린에서 파라미터를 프로그램으로 저장·호출. [원문] — [R375X](https://www.rimac.it/en/products/r375x/), [R375](https://www.rimac.it/en/products/r375/)
- Vandewiele의 카매트 관련 오버에징 모델: TITAN 2500AHC, 4500AHC(고속, 내측 회전 쉬움), 4510AHC, 5540(카매트 자동 오버에징). 4510CHC는 두께 18 mm까지, 땀 폭 10/15/19 mm. [원문] — [vandewiele.com overedging](https://vandewiele.com/textile-solutions/sewing/overedging)
- Vandewiele 브랜드 페이지는 신제품 "FULLY AUTOMATIC OVEREDGING ROBOT : TITAN 5540M"을 내세우며 상세 사양은 없다. [원문] — [vandewiele.com/brands/titan](https://vandewiele.com/brands/titan)

### Inferences
- (추정) TITAN DK4640 → 5540 → 5540M은 같은 계열의 후속 모델로 보이나 확인 자료 없음.
- (추정) 오버에징(실로 감침)과 테이프 바인딩은 다른 공정이다. TITAN 로봇형·중국 무명기는 오버에징이라 테이프 공급·이음매 문제는 없다. 테이프 바인딩 완전자동으로 공개된 것은 R375X/R375A와 Richpeace 정도다.
- (추정) R375A 사이클(앞 45~50 s)은 이 기계의 사이클 목표 비교 기준으로 쓸 수 있다.

### Gaps
- R375X 사이클·무게·외형, Richpeace 사이클·매트 크기 범위 — 공개 없음.
- 동영상: 이번 조사에서 R375X·Richpeace·TITAN의 기구를 보여주는 YouTube 영상 설명을 찾지 못했다(검색 결과에 영상 링크 없음).
- Willems(네덜란드) 카매트 오버에징 자동기는 "yarn or band"(실 또는 띠)로 완전 자동 마감한다는 검색요약만 있고 페이지는 인증서 오류로 열리지 않았다 — [willems-ip.com](http://www.willems-ip.com/productie-automatisering-en/references/festonneerautomaten-voor-autovloermatten/?lang=en). 또 Handsaeme(벨기에)는 "sewing machines follow the side of the carpet, even if it is slightly bowed"(검색요약, 페이지 403) — [Handsaeme PDF](https://pdf.directindustry.com/pdf/handsaeme-machinery/automated-carpet-finishing/172010-1007632.html).
- 한국 상용 자동 카매트 바인딩기, Jack·Typical 등 중국 대형 재봉기 업체의 카매트 자동 바인딩기, 터키 업체 — 검색에서 찾지 못했다.
- Dürkopp 바인딩 브로셔 PDF(https://partner.duerkopp-adler.com/commons/news/downloads/Duerkopp-Adler_Binding_DIN-A4_EN.pdf)는 압축 PDF라 본문을 읽지 못했다. 867-290342의 원래 사양(이송 방식)은 확인 못 함.
