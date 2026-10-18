# 버전 기록

| 버전 | 내용 | HTML | PDF |
|---|---|---|---|
| v4 최종본 | FINAL_REVISION_GUIDE 기준 전면 재설계. 공식 프로필5개·실제 썸네일9개, 본문15장+별도 상세 부록, 기획 가설과 검증으로 연결 | [발표 열기](v4/index.html) | [15페이지 PDF](v4/news-topics-v4.pdf) |
| v3 | 전체 주제 분포→성과 정의→전체 성과→채널별 차이→실제 제목으로 개념 설명→기획 결정으로 흐름 재설계. 본문 17장 + 부록 3장 | [발표 열기](v3/index.html) | [20페이지 PDF](v3/news-topics-v3.pdf) |
| v2 | 운영자의 주제·제목 선택에서 출발. 제목 특징 6개·기획 조합·후속 실험 추가. 본문 17장 + 부록 3장 | [발표 열기](v2/index.html) | [20페이지 PDF](v2/news-topics-v2.pdf) |
| v1 | 최초 발표본. 본문 14장 + 부록 2장 | [발표 열기](v1/index.html) | [16페이지 PDF](v1/news-topics-v1.pdf) |

각 버전의 HTML, CSS/JS/자산, 사용한 데이터·분석 코드와 PDF를 고정 보관한다. 파일 해시는 각 버전의 `manifest.json`에 기록한다. 기존 버전은 덮어쓰지 않는다.

생성: `python tools/save_version.py vN`. PDF 페이지 수·렌더링·링크를 검증한 후 버전 기록과 Git 태그를 갱신한다.
