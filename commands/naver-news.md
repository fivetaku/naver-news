---
name: naver-news
description: 네이버 뉴스 검색 API로 뉴스레터를 만듭니다
arguments:
  - name: keyword
    description: 검색할 키워드
    required: false
---

$ARGUMENTS가 있으면 해당 키워드로, 없으면 키워드를 물어본 후 naver-news 스킬의 워크플로우를 실행한다.

Read `skills/naver-news/SKILL.md` and execute the workflow with keyword: $ARGUMENTS
