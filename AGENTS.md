# 발표 덱 버전 관리

이 저장소의 덱을 새로 제작하거나 수정해 완성할 때마다 버전을 올리고 HTML 스냅샷과 PDF를 함께 보관하세요. 사용자가 명시적으로 요청한 작업 규칙입니다.

- `versions/v1/`은 최초 발표본이며 덮어쓰지 않습니다.
- `python tools/save_version.py vN`으로 다음 버전을 저장합니다. PDF는 16:9, 한 슬라이드당 한 페이지입니다.
- PDF 페이지 수·한글·도표·링크를 검증하고 `versions/README.md`, `versions/index.html`, Git 태그 `vN`을 갱신합니다.
- 덱을 배포할 때 해당 PDF도 함께 배포합니다.
