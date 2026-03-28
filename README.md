# naver-news

네이버 뉴스 검색 API를 활용한 Claude Code 뉴스레터 스킬

키워드 하나로 최신 뉴스를 수집하고, 카테고리별로 정리해서 HTML 뉴스레터로 만들어줍니다.

## 설치

`skills/naver-news/` 폴더를 프로젝트의 `.claude/skills/` 에 복사합니다.

```bash
cp -r skills/naver-news ~/.claude/skills/naver-news
# 또는 프로젝트별로
cp -r skills/naver-news your-project/.claude/skills/naver-news
```

## 사용법

Claude Code에서 아래처럼 말하면 됩니다:

```
"AI 뉴스 정리해줘"
"반도체 최신 뉴스 브리핑 만들어줘"
"뉴스레터 만들어줘"
```

### 처음 사용 시

네이버 검색 API 키가 필요합니다. 스킬이 자동으로 안내해주지만, 미리 준비하려면:

1. [네이버 개발자센터](https://developers.naver.com/apps/#/register) 접속 (네이버 로그인)
2. 애플리케이션 이름: 아무거나 (예: "뉴스브리핑")
3. 사용 API: **검색** 선택
4. 비로그인 오픈 API 서비스 환경: **WEB 설정** → URL: `http://localhost/`
5. 등록 후 Client ID / Client Secret 복사

스킬 실행 시 두 값을 알려주면 `.env` 파일이 자동 생성됩니다.

## 검색 옵션

| 모드 | 설명 | 건수 |
|------|------|------|
| **최신순 6시간** | 긴급 브리핑 | 최대 100건 중 시간 필터 |
| **최신순 24시간** | 하루 뉴스 브리핑 (기본) | 최대 100건 중 시간 필터 |
| **최신순 48시간** | 주말/연휴 따라잡기 | 최대 100건 중 시간 필터 |
| **관련도순** | 주제 동향 분석 (~1개월) | 상위 30건 |

## 출력

`newsletter/` 폴더에 `{YYYYMMDD}-{키워드}.html` 형식으로 저장됩니다.

```
newsletter/
├── 20260328-클로드코드.html
├── 20260329-반도체.html
└── 20260330-AI.html
```

## 파일 구조

```
skills/naver-news/
├── SKILL.md              # 스킬 워크플로우
├── .env.example          # API 키 템플릿
├── .env                  # API 키 (자동 생성, git 제외)
└── scripts/
    └── fetch_news.py     # API 호출 + 필터링 + 중복 제거
```

## 요구사항

- Claude Code (Pro/Max 구독)
- Python 3.x (macOS/Linux 기본 포함)
- 네이버 검색 API 키 (무료, 일 25,000건)

## 라이선스

MIT
