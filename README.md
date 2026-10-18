# 뉴미디어 뉴스, 왜 어떤 영상은 더 많이 볼까? · V6

[HTML 발표](https://mschoooo.github.io/news-topic-views-2025/?v=6) · [15페이지 PDF](https://mschoooo.github.io/news-topic-views-2025/versions/v6/news-topics-v6.pdf) · [상세 부록](https://mschoooo.github.io/news-topic-views-2025/appendix.html) · [버전 기록](https://mschoooo.github.io/news-topic-views-2025/versions/)

V5의 15장 구성과 연구 내용을 유지하고 표지·가독성·애니메이션을 다듬었다. 새 제목을 중심으로 실제 영상 이미지를 재배치하고, 7장의 두 비율은 막대와 점으로 구분했다. 11장은 제목 단어 포함 여부만 색과 모양으로 구분한다. 14장은 취재 질문·제목 후보·다음 결정에 집중하고 측정 세부 사항은 노트와 부록에 보존했다.

뉴미디어 정보 채널 운영자의 주제·제목 선택을 위해 방송사 5개 채널의 2025년 일반 영상 1,680편을 살펴보는 탐색 발표다. 핵심 연구 질문은 “방송사 뉴미디어 뉴스 채널에서 콘텐츠 주제에 따라 조회수는 어떻게 달라지는가?”이다. 조회수는 2026-10-18 수집 당시 누적값이다. 관찰한 차이를 인과효과나 미래 성과로 해석하지 않는다.

- [제작 전 수정 계획](v6_revision_plan.md)
- [전체 구성과 시각화](improvement_plan.md)
- [V5 대비 수정 기록](revision_log.md)
- [발표 노트](speaker_notes.md)
- [실제 이미지 출처](image_sources.md)
- [분류·사례 검토](analysis_review.md)
- [QA 검증 기록](qa_report.md)과 [검사 결과 JSON](v6_qa_results.json)

원본 source.csv 7열·1,680행과 research_data.json·analysis.py·v4_metrics.json·분류 규칙은 유지했다. `python analysis.py`, `python analysis_review.py`, `python build_v6.py` 순서로 같은 폴더에서 재현할 수 있다. pandas/numpy가 필요하다. V1~V5의 고정 HTML·데이터·코드·이미지·PDF도 보존한다.

발표 조작: 방향키·Space 이동, N 노트, O 목차, F 전체화면. Anime.js로 수치와 그래프를 짧게 연출하며, 움직임 줄이기·PDF·라이브러리 실패 시 최종 상태를 즉시 표시한다. PDF는 한 슬라이드당 한 페이지의 16:9 고정본이다.

실제 프로필 5개와 썸네일 9개의 권리는 각 제작사에 있다. 이미지의 과거 수정 이력은 분석하지 않았다. 로컬 Anime.js(MIT)와 Pretendard(OFL) 라이선스는 assets에 있다.
