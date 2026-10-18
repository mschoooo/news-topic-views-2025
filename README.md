# 다음 영상, 무슨 주제로 어떤 제목을 쓸까? — V2

뉴미디어 정보 채널 운영자의 콘텐츠 기획을 위한 탐색적 발표입니다. 방송사 5개 채널의 2025년 공개 일반 영상 1,680개에서 주제와 제목 표현의 조회수 패턴을 살펴봅니다.

[현재 발표](https://mschoooo.github.io/news-topic-views-2025/) · [V2 PDF](versions/v2/news-topics-v2.pdf) · [버전 기록](versions/)

방향키/Space 이동, N 발표 노트, O 목차, F 전체화면. 본문 17장과 방법 부록 3장으로 구성했습니다.

## 분석과 자료

source.csv는 Firecrawl 수집 원본, research_data.json은 전체 집계·영상별 주제·제목 특징, analysis.py는 재현 코드입니다. `pip install pandas numpy` 후 `python analysis.py`로 재계산할 수 있습니다. 주제 사전은 V1 그대로 고정했고 제목 특징 6개를 정규식으로 탐색했습니다. 전체 422개가 채널 내 상위 25%에 해당합니다. 조회수는 2026-10-18 누적값이며 제목 변경의 인과 효과를 뜻하지 않습니다.

## 버전

- [V1 HTML](versions/v1/) · [V1 PDF](versions/v1/news-topics-v1.pdf): 최초 발표본, 고정 보존
- [V2 HTML](versions/v2/) · [V2 PDF](versions/v2/news-topics-v2.pdf): 운영자 관점 재설계, 제목 분석·기획 적용 추가

앞으로도 각 버전의 HTML·데이터·코드와 PDF를 함께 보관합니다.

## 자산 출처

사례 썸네일: 각 YouTube 영상(1nqK8rEwPmo, G1AaGsYbJRE)의 원본 썸네일, 설명 목적. Anime.js 3.2.2 (MIT): https://github.com/juliangarnier/anime. Pretendard v1.3.9 (OFL): https://github.com/orioncactus/pretendard. 라이선스는 assets에 포함했습니다.
