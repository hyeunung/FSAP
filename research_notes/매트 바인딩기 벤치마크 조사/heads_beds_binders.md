# 바인딩용 봉제 헤드 — 바늘 밑 기구(베드)·이송·바인더 조사

조사일 2026-11-03. 표기 규칙: "확인된 사실"(Cited Findings)은 출처 URL을 붙였다. 출처 없는 수치는 넣지 않았다. 추정은 Inferences에만 있다.
PDF 원문 확인(2026-11-03 갱신): DA 공식 PDF 세 개를 직접 읽었다.
- **[PDF-S]** = DA "867-M SPECIALS" 카탈로그(문서번호 9099 100867 07, DE/EN, 12/2020), 6쪽. 받은 곳: [Castle_Sewing.pdf](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf). 파일 이름은 Castle Sewing이지만 내용은 DA 공식 카탈로그다.
- **[PDF-E]** = DA "867-M ECO" 데이터시트(9099 100867 10, 12/2020), 6쪽. [DA_867-M-ECO_deen_12-2020.pdf](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf)
- **[PDF-B]** = DA 제품정보 "Assembly set for double needle binding operations"(December 2020), 1쪽. [Duerkopp-Adler_Binding_DIN-A4_EN.pdf](https://partner.duerkopp-adler.com/commons/news/downloads/Duerkopp-Adler_Binding_DIN-A4_EN.pdf)

## 0. 867 매트 바인딩 사양 치수 요약표(코디네이터 요청 항목)

| 항목 | 값 | 판정 | 출처 |
|---|---|---|---|
| 베드 형식 | 평판(flatbed), 1본침 본봉 | 확인 | [PDF-S] 1·4쪽 |
| 암 밑 공간(clearance) | **C = 335 mm(폭, 바늘~암 기둥) × D = 125 mm(높이, 베드면~암 밑)** | 확인. 그림 기호상 C는 가로, D는 세로 | [PDF-S] 4쪽 맨 아래 표, [PDF-E] 2·4쪽("335 mm wide and 125 mm high") |
| 노루발 밑 통과 높이 — 봉제 중 | **A = 최대 10 mm**("Clearance when sewing") | 확인 | [PDF-S] 4쪽, [PDF-E] 4쪽 |
| 노루발 들림 | **B = 최대 20 mm**("Clearance when lifting"), 392342는 자동(공압), 392040은 자동 들림 없음 | 확인 | [PDF-S] 4쪽 |
| 최대 소재 두께 | 공식 "최대 두께" 항목은 없다. 봉제 중 통과 높이 A = 10 mm가 상한이다 | A값은 확인, "최대 두께 ≒ 10 mm"라는 해석은 추정 | [PDF-S] 4쪽 |
| 교대 노루발 행정 | 최대 9 mm, 다이얼 조정, 무릎 스위치로 빠른 행정 전환 | 확인 | [PDF-S] 4쪽 |
| 훅 | **수직 훅 XXL, Ø 32 mm, 바늘 왼쪽 배치("Hook to the left of the needle")** | 확인 | [PDF-S] 4쪽 |
| 이송 | 하송 + 바늘 이송 + 교대 노루발 상송(3중 이송) | 확인 | [PDF-S] 4쪽 |
| 땀길이 / 속도 | 최대 12 mm(두 번째 땀길이 미리 선택 가능) / 최대 3,000 st/min(행정·땀길이에 따라 자동 제한) | 확인 | [PDF-S] 2·4쪽 |
| 실 트리머 | 자동 되박음 + 실 트리머, 남는 실 약 15 mm 이하(392342) | 확인 | [PDF-S] 4쪽 |
| 바늘 / 실 | 134-35, Nm 90–180 / Nm 80/3–10/3 | 확인 | [PDF-S] 4쪽 |
| 공기 | 0.7 NL/행정, 6 bar(392342) | 확인 | [PDF-S] 4쪽 |
| 헤드 무게 | 55–58 kg | 확인 | [PDF-S] 4쪽 |
| 외형(길이·폭·높이) | 최대 1,060 × 500 × 1,700 mm | 값은 확인. 테이블·스탠드를 포함한 기계 전체로 보이는 것(높이 1,700)은 추정 | [PDF-S] 4쪽 |
| 베드판 크기, 베드 높이, 바늘에서 베드 앞·옆 끝까지 거리 | **세 PDF 어디에도 없다** | 미확인 | — |
| 바인더 장착 | 바인더(이동식, "moving binder")와 테이프 안내(세로 핀 5개짜리 가이드)가 **베드판 위**에 놓인다. 2본침용 세트는 "swivel rail(회전 레일)"로 바인더를 젖혀 빼는 구조다 | 사진·문구 확인. 치수는 없다 | [PDF-S] 1·3쪽 사진, [PDF-B] 1쪽 |
| 2본침 바인딩 세트 | 0867 V92772(바늘 간격 4 mm), 0867 V92789(바늘 간격 6 mm). "모든 2본침 M-TYPE 평판기용" | 확인 | [PDF-B] 1쪽 |

## 1. Dürkopp Adler 867 계열(특히 867-290342, RI.MA.C. R375A 탑재 헤드) — 베드·이송·훅·땀길이·속도·트리머·노루발 들림

### Takeaway
867은 **평판(flat bed)** 본봉 M-TYPE 헤드다. 자동차 매트 바인딩 전용 사양(867-392342, 867-392040)의 공식 페이지에 따르면 상부 이송(top feed) 행정은 최대 9 mm, 땀길이는 최대 12 mm, 속도는 최대 3,000 st/min이다. 노루발은 공압으로 최대 20 mm 들리고, XXL 훅과 사용자가 따로 조정할 수 있는 이동식 바인더(moving binding device)가 들어간다. 867-290342라는 서브클래스 자체의 공식 사양은 찾지 못했다.

### Cited Findings
- 867-392342는 M-TYPE **flat bed** 바인딩 전용 사양이다. 용도는 "자동차 매트와 컨버터블 접이식 지붕의 바인딩, 안팎 R(inner and outer radii)이 있는 평평한 부품, 한쪽·양쪽 접힘 테이프나 오픈엣지 테이프"다. — [Dürkopp Adler 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- 867-392342 사양: 장력 없이 테이프를 보내는 **차동(differential) 이동식 바인더**(푸시버튼으로 조정), top feed stroke 최대 9 mm, **XXL 훅**(밑실 용량 큼), 땀길이 최대 12 mm(두 번째 땀길이 미리 선택 가능), 최대 3,000 st/min, **공압 노루발 들림 최대 20 mm**, 실 트리머, 자동 되박음, 최대 실 굵기 Nm 10/3, 헤드에 붙은 직결 모터. — [Dürkopp Adler 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- 867-392040도 같은 용도(자동차 매트·컨버터블 지붕)다. 이동식 바인더, top feed stroke 최대 9 mm, XXL 훅, 땀길이 최대 12 mm, 3,000 st/min, 노루발 들림 최대 20 mm, Nm 10/3. — [Dürkopp Adler 867-392040](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392040.html)
- 867-M SPECIALS(바인딩·트리밍용 1본침 본봉 평판) 카탈로그에 자동차 매트가 대상물로 나온다. 오픈엣지·접힘 테이프 모두 되고, 안쪽·바깥쪽 곡선에서 장력을 낮게 유지하는 차동 바인더를 쓴다(검색 요약 기준). — [Babylock DA867special 카탈로그](https://corporate.babylock.co.jp/wp-content/uploads/2022/04/DA867special-FG_VF_AE　カタログ.pdf); [Castle Sewing 867-M PDF](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)
- **암 밑 공간(clearance)은 335 mm(폭) × 125 mm(높이)로 확정한다.** [PDF-E] 2쪽 본문에 "large clearance (335 mm wide and 125 mm high)"라고 적혀 있다. [PDF-S]와 [PDF-E]의 4쪽 표에도 C = 335, D = 125로 나온다. 앞서 검색 요약에서 본 160 mm와 297 mm는 공식 PDF에서 확인되지 않았다(다른 기종이거나 다른 열을 잘못 읽은 것으로 보임). 롱암 867-70은 폭이 700 mm다(검색 요약 기준). — [PDF-E 2·4쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf); [PDF-S 4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf); [DA 867-70 M](https://partner.duerkopp-adler.com/commons/download/public/867-70-M/DA_867-70-M_deen_12-2020.pdf)
- 노루발 밑 통과 높이: 봉제 중 A = 최대 10 mm, 들었을 때 B = 최대 20 mm. 867 매트 바인딩 사양(392040·392342)과 ECO 4종 모두 같다. — [PDF-S 4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf); [PDF-E 4쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf)
- 훅: 867-M SPECIALS(392040/392342/393342/394342)는 모두 **수직 훅 XXL Ø 32 mm, 바늘 왼쪽**이다. ECO는 L 훅 또는 XXL 훅을 쓰고, XXL 훅의 밑실 용량은 표준 훅보다 70% 많다. — [PDF-S 4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf); [PDF-E 2·4쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf)
- 품번 규칙: ECO에서 867-190xxx는 1본침(Einnadel), 867-290xxx는 2본침(Zweinadel, 바늘 간격 4–60 mm)이다. — [PDF-E 3·4쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf)
- 컨트롤: SPECIALS는 DAC classic과 조작판 OP1000(프로그램 제어), 직결 구동이다. ECO는 헤드에 내장된 DAC eco M-TYPE이고 니들 포지셔닝·소프트스타트 기능이 있다. — [PDF-S 2·4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf); [PDF-E 2쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf)
- 867-392342-M(LG) 용도 원문: 자동차 매트, 텐트, 차양 발란스, 컨버터블 지붕을 오픈엣지 또는 접힘 바인딩 테이프로 장력 낮게 바인딩한다. 이동식 바인더와 바인딩 봉제 장치를 갖춘다. 그 밖에 "좁은 안쪽·바깥쪽 R에서 고른 땀을 내기 위한 두 번째 땀길이"가 있다. — [PDF-S 2·3쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)
- 867-394342-M(AE): 바인더 바로 앞에서 소재 가장자리를 자르는 전환식 가장자리 커터와 이동식 바인더, 큰 폐기물 슈트를 갖춘다. — [PDF-S 2·3쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)
- 867-M ECO 데이터시트와 SPECIALS의 바늘 시스템은 134-35(Nm 90–180)다. — [PDF-E 4쪽](https://partner.duerkopp-adler.com/commons/download/public/867-M/DA_867-M-ECO_deen_12-2020.pdf); [PDF-S 4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)
- 867-290342-100 중고 매물 설명은 "2 Nadeln(2본침), 완전자동"이 전부다. 같은 품번을 단 다른 매물은 "자동 롱암 지퍼 봉제기"로 적혀 있다. 이송·바인더·노루발 정보는 없다. — [maschinensucher 867-290342-100](https://www.maschinensucher.de/d%C3%BCrkopp+adler-867-290342-100/i-20729477)
- DA 공식 서브클래스 페이지 0867-290342.html은 HTTP 404다(없거나 단종). — [시도한 URL](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-290342.html)
- DA "2본침 바인딩 조립 세트"는 모든 2본침 M-TYPE 평판기용 업그레이드다. 0867 V92772는 바늘 간격 4 mm, 0867 V92789는 6 mm용이다. "평평하고 밀림 없는 가장자리"를 만들고, swivel rail(회전 레일)로 빠르게 전환한다. 제품 사진은 자동차 매트(검은 카펫, 파란 2줄 땀)를 바인딩하는 장면이다. — [PDF-B 1쪽](https://partner.duerkopp-adler.com/commons/news/downloads/Duerkopp-Adler_Binding_DIN-A4_EN.pdf)

### Inferences
- 품번 규칙(290xxx = 2본침, [PDF-E] 확인)과 매물 설명("2 Nadeln")을 함께 보면 867-290342는 **2본침 평판 M-TYPE이다(추정, 신뢰 높음).** 끝자리 "342"는 SPECIALS의 392342·393342와 같아서 자동 노루발 들림·트리머·OP1000 같은 CLASSIC 장비 묶음일 가능성이 있다(추정). 바인딩 기능은 [PDF-B]의 2본침 바인딩 세트(4 또는 6 mm)를 붙여 얻는 구성일 가능성이 있다(추정). R375A가 파란 2줄 땀의 매트 사진과 같은 2본침 바인딩을 하는지 확인해야 한다.
- 1본침 XXL Ø 32 mm 훅 기준으로 보면, 바늘 밑 베드 안에는 최소 Ø 32 mm 훅과 그 회전 공간이 바늘 왼쪽으로 치우쳐 들어간다(추정). 2본침이면 바늘 간격(4/6 mm)만큼 떨어진 훅이 두 개 있다(추정).
- 평판 베드라서 **바늘 밑에는 바늘판과 그 밑의 훅·이송 톱니 기구가 넓은 평면 베드 전체로 깔려 있다.** 매트는 베드 위에 얹혀 지나간다. 그러니 "베드가 V/U 홈 안으로 들어간다"는 개념은 평판에 맞지 않는다. 헤드 쪽에서 홈에 들어갈 수 있는 것은 바늘·노루발·바인더 끝뿐이다. 홈 안쪽 반경을 따라가려면 매트 쪽이 회전해야 한다(R375X처럼 헤드 고정·매트 회전).
- 진공 매트 고정판은 평판 베드의 윗면 높이(바늘판 면)와 같은 높이로 붙거나 그보다 조금 낮게 겹쳐야 한다. 바늘 주변(바늘판·톱니 영역)은 고정판이 비켜야 한다. 이 영역의 치수는 확인 못 했다(Gaps).
- 노루발 공압 들림 최대 20 mm는 매트 두께와 바인더 높이를 합한 값의 상한을 정하는 데 쓸 수 있다.

### Gaps
- 867 베드판(Grundplatte) 외형 치수, 테이블 위 베드 높이, 바늘 중심에서 베드 앞·옆 끝까지의 거리, 바늘판 크기: 세 공식 PDF(카탈로그·데이터시트)에 없다. 사용설명서(Betriebsanleitung)의 테이블 가공도(Tischplattenzeichnung)나 DA 서비스 자료에 있을 가능성이 높다. manualmachine은 403으로 막혀 있다. 대리점이나 DA에 테이블 컷아웃 도면을 요청하는 것이 확실하다.
- 867-290342의 공식 정의(용도·바인더 유무).
- 867 바인딩 사양에 퓰러(puller)가 있는지: 공식 PDF의 장비 표에 퓰러 항목이 없다.

## 2. 그 밖에 바인딩에 쓰는 헤드 — 포스트베드·실린더베드·카펫 바인더

### Takeaway
Dürkopp Adler가 자동차 매트 바인딩용으로 공식 문서에 적은 기종은 **867-M(평판)**뿐이다. 868-M은 포스트베드로 시트커버·대시보드용이다. 업계 전용기 Van de Wiele TITAN 2530AHC/2530AG(자동차 매트·카펫 테이프 바인딩)는 **최소 안쪽 반경 30 mm**를 공개 사양으로 낸다. 이 값은 R10 mm 홈에 비해 크다.

### Cited Findings
- DA 868-M은 **포스트베드**이고 자동차 시트커버·대시보드 커버링용이다. 자동차 매트 바인딩기로 적혀 있지 않다. — [Babylock DA868 M 카탈로그](https://corporate.babylock.co.jp/wp-content/uploads/2022/04/DA868-M　カタログ.pdf)
- DA 869는 하송(lower feed)이 있는 1본침 **프리암(free-arm)** 기종이고, 매트 바인딩 언급은 없다. — [Duerkopp Adler 869 매뉴얼(manualmachine)](https://manualmachine.com/duerkoppadler/869/15107928-operating-instruction)
- DA 888은 "Column Quilting Machine"(포스트형)으로 매물에 나온다. — [machineseeker 888-356122-M](https://www.machineseeker-india.com/d%C3%BCrkopp+adler-888-356122-m/i-20284900)
- Van de Wiele TITAN 2530AHC는 "자동차 카펫용 테이프 바인딩"이다. 카탈로그 기준 **최소 안쪽 반경 30 mm**, 테이프는 최대 32 mm다(검색 요약 기준). 형제기 TITAN 2530AG는 "자동차 매트 바인딩 전용 설계"이고 안쪽·바깥쪽 코너 모두 테이프를 둘러 박으며 **최소 안쪽 반경 30 mm**다. — [Van de Wiele TITAN 2530AHC 카탈로그(DirectIndustry PDF)](https://pdf.directindustry.com/pdf/vandewiele/titan-2530ahc/172691-1134622.html); [Van de Wiele TITAN 2530AG(DirectIndustry)](https://www.directindustry.com/prod/van-de-wiele/product-172691-2046145.html)
- Van de Wiele의 테이프 바인딩 페이지에는 "22 mm부터 150 mm까지의 테이프"를 카펫 가장자리에 박을 수 있다고 나온다(제품군 전체 기준). TITAN 3700C는 중작업용 2중 환봉(double chainstitch) 카펫 테이프 바인더다. — [Van de Wiele Tape binding](https://vandewiele.com/textile-solutions/sewing/tape-binding)
- Union Special 53100 계열은 고속 중작업 1본침 **평판** 지그재그기이고, 퓰러가 바로 붙어 있다(closed-coupled puller). 용도에 카펫 바인딩이 있다(매물 설명). — [sewingmachine.com Union Special](https://sewingmachine.com/products/used-commercial-33)
- 포럼 실무 의견: 자동차·보트 카펫은 테이블 장착 워킹풋(교대 노루발) 기종을 흔히 쓴다. 방 카펫은 바늘 뒤에 모터 퓰러 휠이 있는 기계로 박지만 자동차 카펫에는 늘 필요하지는 않다. 파일 높이 9 mm 카펫이면 약 10 mm를 박을 수 있어야 하고 노루발을 들었을 때 최소 12 mm가 떠야 한다. Consew 206RB5의 노루발 들림은 9/16"(14.25 mm)다. Pfaff 145/545/1245에는 애프터마켓 동기식 바인더 세트가 있다. — [Leatherworker.net 92952](https://leatherworker.net/forum/topic/92952-sewing-machine-models-for-carpet-bindingauto-upholstery)
- 자동차 매트 봉제 장치 특허(US 6155186)는 봉제 헤드, 봉제 테이블, 매트 이동 기구로 이루어진다. 매트와 봉제면 사이에 마찰 저감 부재를 둬서 매트를 잘 미끄러지게 한다. 종속항에 매트 가장자리 바인딩이 있다(검색 요약 기준). — [US 6155186 PDF](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6155186)
- 평판용 바인더를 포스트베드에 쓰면 정렬이 어긋나 이송이 제대로 안 된다는 주의가 있다. 다만 출처 품질이 낮은 스핀 콘텐츠로 보인다. — [aegro (저품질 출처)](https://www.portal-consultores.aegro.com.br/?p=51732)

### Inferences
- 공개 사양으로 확인된 전용 매트 바인더의 최소 안쪽 반경은 30 mm다. 같은 계열의 R375X/R375A도 비슷한 제약을 가질 수 있다. 바인더·노루발이 R10 홈 안쪽을 돌아 나가는 것은 표준 기술 범위 밖일 가능성이 크다. 시제품 확인 항목으로 분명히 해야 한다.
- 포스트베드(868 계열)는 바늘 밑 베드가 기둥(post) 하나로 좁아진다. 원리상 진공판과 공간을 나누기에는 유리하다. 하지만 기둥 지름·높이 수치는 확인 못 했다. 바인딩 용도로 DA가 매트에 권하는 기종도 아니다.

### Gaps
- Pfaff 335/1245/2545, Juki, Mitsubishi, Brother, Typical, Siruba의 바인딩용 포스트/실린더 기종에 대해 베드 폭·지름·기둥 높이 수치를 하나도 찾지 못했다(조사 시간 부족).
- DA 868/869 포스트·실린더 지름과 높이 수치는 미확인이다.
- Gaylord, Consew 카펫 바인더의 공식 사양을 찾지 못했다.
- TITAN 2530AHC 카탈로그 원문은 403이라 읽지 못했다. 30 mm, 32 mm 값은 검색 요약 기준이다.

## 3. 바인더(폴더·깔때기) 어태치먼트 — 2단·4단 접힘, 장착 위치, 치수, 테이프 폭

### Takeaway
DA 867 바인딩 사양은 **이동식(차동) 바인더**를 쓴다. 공식 사진에서는 이 바인더가 베드판 위, 노루발 앞에 놓여 있다. 2본침 M-TYPE에는 회전 레일식 바인딩 세트(바늘 간격 4/6 mm)가 따로 있다. 테이프는 한쪽 접힘, 양쪽 접힘, 오픈엣지를 모두 받는다. 일반 바인더는 헤드 쪽 구멍이나 베드 쪽 구멍에 장착한다. 바인더 몸체의 치수 수치는 찾지 못했다.

### Cited Findings
- 867-392342/392040의 테이프는 "한쪽 또는 양쪽 접힘, 또는 오픈엣지"다. 바인더는 "차동 이동식(differentiable moving binder)"이고 푸시버튼으로 조정한다. 테이프와 소재 구조에 맞는 표준 바인딩 어태치먼트 종류가 많다. — [DA 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html); [DA 867-392040](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392040.html)
- 일반 바인더 세트는 헤드의 장착 구멍에 붙이는 것도 있고 베드의 장착 구멍에 붙이는 것도 있다. 옛 특허에는 바인더 베이스판을 봉제기 베드판에 고정하는 브래킷이 있다. — [US 985257 (Google Patents)](https://patents.google.com/patent/US985257); [Walmart 바인더 세트 설명](https://www.walmart.com/ip/267989089)
- Sailrite는 바닥재 바인딩에 1-1/4"(약 32 mm) 스윙어웨이 바인더(#120474)를 쓴다. 바인더를 노루발에 최대한 가깝게 두고, 바인더 밑동 쪽 베드에 자석 가이드를 둬서 봉제 중 바인더가 비켜 나가지 않게 하라고 권한다. — [Sailrite 곡선 바인딩 팁](https://www.sailrite.com/Tips-for-Binding-Curves-on-Carpet-and-Flooring) (본문은 직접 열람 실패. 검색 요약 기준)
- 467/767 계열용 "Raw Edge Binder(4단·생지 숨김형)와 binding gauge, moving arm" 세트가 애프터마켓에 있다. 67/167/267/69/269용 바인딩 워킹풋 세트도 있다. — [eBay KHF2](https://www.ebay.de/itm/266981234567); [eBay GCKP269F](https://www.ebay.de/itm/266874030848)
- Van de Wiele 카펫 테이프 바인딩: 테이프 22–150 mm(제품군), 2530AHC 최대 32 mm(검색 요약 기준). — [Van de Wiele Tape binding](https://vandewiele.com/textile-solutions/sewing/tape-binding)

- DA 공식 사진을 보면 바인더(깔때기)는 노루발 바로 앞 오른쪽, 베드판 위에 있다. 테이프는 베드판 오른쪽 뒤에 세운 세로 핀 4~5개짜리 테이프 가이드를 거쳐 들어온다(867-392342 표지와 3쪽 매트 사진, 394342 사진). 2본침 세트도 바인더가 베드판 위의 회전 레일(swivel rail)에 붙어 있고, 테이프 가이드는 베드판 뒤쪽에 서 있다. — [PDF-S 1·3·5쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf); [PDF-B 1쪽](https://partner.duerkopp-adler.com/commons/news/downloads/Duerkopp-Adler_Binding_DIN-A4_EN.pdf)
- 이 바인더는 "mitgehende Einfassvorrichtung", 즉 소재와 함께 움직이는 이동식 바인더다. "differenzierbar"(차동 조정 가능)로 안쪽·바깥쪽 R에서 장력을 낮춘다. — [PDF-S 2·3·4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)

### Inferences
- 공식 사진 기준으로 DA 매트 바인더는 **헤드가 아니라 베드판 위에 장착**된다(사진 판독이라 추정이지만 신뢰는 높다). 이전 메모에 적었던 "헤드 쪽에 매달림" 추정은 이것으로 대체한다. "mitgehend(따라 움직임)"는 바인더가 이송과 함께 앞뒤로 움직인다는 뜻으로 보인다(추정). 그렇다면 바인더 출구는 바늘 바로 앞에서 베드 면에 붙어 있다. 바늘 앞의 매트 가장자리 센서와 매트 진공판 가장자리는 바인더 몸체, 회전 레일, 테이프 가이드가 차지한 베드판 오른쪽 앞·뒤 영역과 공간을 다툰다.
- 사진에서 바인더 몸체는 노루발 폭과 비슷하거나 그보다 조금 큰 크기로 보이지만, 실제 치수는 미확인이다.
- 바인더 깔때기는 매트 가장자리를 위아래에서 감싸야 하므로 아래 날개가 베드 면 높이(매트 밑면 높이)까지 내려온다. 진공판 가장자리는 바늘 근처에서 이 아래 날개가 지나갈 틈을 비워 둬야 한다.

### Gaps
- 바인더 깔때기의 길이·폭·높이와 출구에서 바늘까지의 거리 수치는 찾지 못했다.
- 2단 대 4단 접힘 바인더의 두꺼운 소재 적용 한계(소재 두께 대 테이프 폭) 데이터가 없다.

## 4. 퓰러(노루발 뒤 롤러)와 노루발 들림·최대 소재 두께

### Takeaway
카펫 바인딩 퓰러는 **톱니·홈이 있는 구동 롤러가 소재를 물어 당기는 장치**다. 원리상 소재를 누른다. DA 867 매트 바인딩 사양의 공식 페이지에는 퓰러 언급이 없다. 노루발 들림은 867 바인딩 사양에서 공압 최대 20 mm다.

### Cited Findings
- 카펫 바인딩기의 퓰러는 보통 구동 모터에 연결된 롤러다. 롤러에는 카펫을 물기 위한 길이 방향 홈이나 이가 있다. 2중 퓰러는 방향 안정성이 더 좋아서 카펫 가장자리에서 벗어나지 않는다(특허 기술). — [US 5875723 (Google Patents)](https://patents.google.com/patent/US5875723); [US 6055918 (Google Patents)](https://patents.google.com/patent/US6055918)
- 퓰러는 카펫을 봉제 기구 쪽으로 끌어당긴다(휴대형이면 기계를 카펫 가장자리를 따라 나아가게 한다). — [US 7124696 (Google Patents)](https://patents.google.com/patent/US7124696)
- Union Special 53100은 퓰러가 바로 붙은 카펫 바인딩 겸용 평판기다. — [sewingmachine.com](https://sewingmachine.com/products/used-commercial-33)
- 자동차 카펫에는 퓰러가 늘 필요하지는 않다(포럼 실무 의견). — [Leatherworker.net 92952](https://leatherworker.net/forum/topic/92952-sewing-machine-models-for-carpet-bindingauto-upholstery)
- DA 867 바인딩 사양: 공압 노루발 들림 최대 20 mm, top feed stroke 최대 9 mm. — [DA 867-392342](https://partner.duerkopp-adler.com/en/main/products/MS_01_flatbed_1_specials/0867-392342.html)
- 867 롱암 매물 설명: 노루발 들림 20 mm, 노루발 행정 최대 9 mm(봉제 속도에 따라 자동 조정). — [exapro 867-70](https://www.exapro.com/durkopp-adler-867-70-p250131057/)
- Consew 206RB5 노루발 들림 9/16"(14.25 mm). — [Leatherworker.net 92952](https://leatherworker.net/forum/topic/92952-sewing-machine-models-for-carpet-bindingauto-upholstery)
- DA 867 매트 바인딩 사양의 공식 표: 노루발 밑 통과 높이는 **봉제 중 A = 최대 10 mm, 들었을 때 B = 최대 20 mm**다. 교대 노루발 행정은 최대 9 mm이고, 행정과 땀길이에 따라 속도가 자동으로 제한된다. 장비 표(이송·훅·바인더·커터·트리머 등)에 퓰러 항목은 없다. — [PDF-S 4쪽](https://cdn.shopify.com/s/files/1/0719/8408/7323/files/Castle_Sewing.pdf)

### Inferences
- 홈 있는 롤러 퓰러는 매트 윗면을 물고 누른다. 영구 눌림자국 금지(결정로그 C-03)와 정면으로 부딪힐 가능성이 높다. DA 매트 바인딩 사양은 퓰러 없이 하송·바늘이송·교대 노루발(M-TYPE의 일반 이송)과 차동 바인더로 테이프를 보내는 구성으로 보인다(퓰러 미기재가 근거. 공식 확인 아님).
- 봉제 중 통과 높이가 10 mm이므로, 바인딩 테이프로 감싼 매트 가장자리의 압축 전 두께는 대략 10 mm 이하여야 한다(추정. 압축 전후 기준을 DA가 밝히지 않았다). 들림 20 mm는 매트를 넣고 뺄 때의 여유다.

### Gaps
- DA가 "최대 소재 두께"라는 항목을 따로 내지는 않는다. 봉제 중 통과 높이 A = 10 mm만 있다. 압축 전 두께인지 압축 후 두께인지는 미확인이다.
- 노루발이 누르는 힘(압력)과 노루발 밑면 형상: 눌림자국 판단에 필요하지만 자료가 없다.
- R375A가 퓰러를 쓰는지 여부.
