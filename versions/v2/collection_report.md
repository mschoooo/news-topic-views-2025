# 유튜브 2025년 일반 영상 수집 보고서

수집 시각(KST): 2026-10-18T17:29:47.614730+09:00
최종 CSV: 1,680행 / UTF-8 BOM / 7열

## 공식 채널과 수집 건수

- 14F (MBC): https://www.youtube.com/@14FMBC (채널 ID: UCLKuglhGlMmDteQKoniENIQ) — 575건
- 크랩 KLAB (KBS): https://www.youtube.com/@KLAB (채널 ID: UCoxT1kQSLq564FwpK473w-g) — 370건
- 스브스뉴스 (SBS): https://www.youtube.com/subusunews (채널 ID: UCQabORQKQRHP-iUqe-xIFvg) — 315건
- 소탐대실 (JTBC): https://www.youtube.com/@_sotam_ (채널 ID: UChuNP1cNlhUkUOQzBbH-C_Q) — 47건
- 비디오머그 (SBS): https://www.youtube.com/@videomug0 (채널 ID: UCMEbRpvuwTbXxGiyDb1mT8w) — 373건

## 수집 방법과 기준

.env의 FIRECRAWUL_API_KEY를 읽어 Firecrawl v2 search 및 scrape API를 사용했다. 키 값은 결과물과 로그에 기록하지 않았다. Firecrawl search의 채널 검색 결과와 YouTube 원본 HTML의 채널 이름·ID·설명·공식 방송사 이메일/링크로 채널을 대조했다. 소탐대실의 JTBC 소속은 JTBC 공식 기사 https://news.jtbc.co.kr/article/NB12133757 에서도 확인했다.

일반 영상 탭(/videos)의 최신순 목록에서 continuation을 반복 호출해 2년 이상 된 목록까지 탐색했다. 이 호출과 영상 페이지 fetch는 모두 Firecrawl scrape의 executeJavascript 액션 안에서 실행했으며, 별도 YouTube API 키나 yt-dlp를 사용하지 않았다. 8~11개월 전 및 1년 전 항목을 넓게 후보로 확보하고, 각 영상의 ytInitialPlayerResponse.videoDetails 및 microformat.playerMicroformatRenderer에서 정확한 메타데이터를 추출했다. 상대 날짜로 최종 업로드 날짜를 추정하지 않았다.

업로드 날짜는 원본 uploadDate를 한국 시간(Asia/Seoul, UTC+09:00)으로 변환한 YYYY-MM-DD이며 2025-01-01~2025-12-31만 포함한다. 조회수는 수집 당시 누적 정수이며 2025년 말 조회수가 아니다. 영상 길이는 HH:MM:SS이다. 제목·설명은 페이지에서 실제 반환된 텍스트를 보존했다.

쇼츠는 일반 영상 탭만 탐색하여 제외했다. 짧은 영상이라는 이유만으로 일반 영상을 제거하지 않았다. isLiveContent/isLive/liveBroadcastDetails가 있는 항목은 라이브 및 다시보기로 제외했다. 영상 ID 기준 중복을 제거하고 채널 ID 일치를 검사했다.

## 검증 결과

- 상세정보 확인: 2,240/2,240 후보
- 중복 제거: 0행
- 기간 외/라이브 제외: {'기간 외': 558, '라이브 방송 또는 다시보기': 2}
- 열별 누락값: {'채널명': 0, '영상 제목': 0, '영상 URL': 0, '업로드 날짜': 0, '조회수': 0, '영상 길이': 0, '영상 설명': 0}
- 실패/누락 보고 항목: 0건 (collection_failures.json 참조)

## 오류와 수집 범위의 한계

초기 markdown/html 응답에는 YouTube 401 오류가 표시되었으나 rawHtml 내부 초기 데이터는 확보할 수 있었다. 원본 데이터 파싱 및 Firecrawl 브라우저 액션으로 목록과 상세정보를 수집해 해결했다. Firecrawl 429 요청 제한은 요청 간격 조절과 재시도로 처리했다.

공개된 일반 영상 탭에 현재 표시되고 접근 가능한 영상이 수집 범위이다. 이미 삭제·비공개·지역 제한되어 목록에 나타나지 않는 영상은 발견·집계할 수 없으므로, 과거 업로드 전체의 절대적인 완전성은 보장하지 않는다. 그 수나 내용을 임의로 만들지 않았다. 발견한 후보의 상세 수집 실패 또는 필드 누락은 별도 JSON에 실제 URL과 이유를 기록했다.

raw 폴더에는 Firecrawl 실제 응답과 provenance.json을 보존해 검증 가능하게 했다.