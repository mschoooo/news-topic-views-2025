# 버전 기록

| 버전 | 내용 | HTML | PDF |
|---|---|---|---|
| v6 최종본 | V5의 연구·구성을 유지하고 새 표지, 7·11·14장 가독성, 수치·그래프 연출 개선. 브라우저·실제 모바일·PDF QA | [발표 열기](v6/index.html) | [15페이지 PDF](v6/news-topics-v6.pdf) |
| v5 최종본 | V4의 15장 연구 발표·14개 실물 이미지를 유지하고 실제 모바일 화면 배율을 보정. 데스크톱·실제 모바일·PDF·공개 URL QA | [발표 열기](v5/index.html) | [15페이지 PDF](v5/news-topics-v5.pdf) |
| v4 중간 검증본 | 가이드 기준 전면 재설계. 공개 QA에서 모바일 배율 문제를 확인하여 V5로 보정. 고정본 보존 | [발표 열기](v4/index.html) | [15페이지 PDF](v4/news-topics-v4.pdf) |
| v3 | 전체 주제 분포→성과 정의→전체 성과→채널별 차이→실제 제목으로 개념 설명→기획 결정으로 흐름 재설계. 본문 17장 + 부록 3장 | [발표 열기](v3/index.html) | [20페이지 PDF](v3/news-topics-v3.pdf) |
| v2 | 운영자의 주제·제목 선택에서 출발. 제목 특징 6개·기획 조합·후속 실험 추가. 본문 17장 + 부록 3장 | [발표 열기](v2/index.html) | [20페이지 PDF](v2/news-topics-v2.pdf) |
| v1 | 최초 발표본. 본문 14장 + 부록 2장 | [발표 열기](v1/index.html) | [16페이지 PDF](v1/news-topics-v1.pdf) |

각 버전의 HTML, CSS/JS/자산, 사용한 데이터·분석 코드와 PDF를 고정 보관한다. 파일 해시는 각 버전의 `manifest.json`에 기록한다. 기존 버전은 덮어쓰지 않는다.

생성: `python tools/save_version.py vN`. PDF 페이지 수·렌더링·링크를 검증한 후 버전 기록과 Git 태그를 갱신한다.
