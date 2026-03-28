#!/usr/bin/env python3
# 네이버 뉴스 검색 API 호출 + 24시간 필터링 스크립트
import sys
import json
import os
import re
import html
import subprocess
import urllib.parse
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

KST = timezone(timedelta(hours=9))

def load_env(env_path):
    """Read .env file and return dict of key-value pairs."""
    env = {}
    if not os.path.exists(env_path):
        return env
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env

def clean_html(text):
    """Remove HTML tags and unescape HTML entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()

def fetch_news(keyword, client_id, client_secret, display=100):
    """Call Naver News Search API via curl and return JSON response."""
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_keyword}&display={display}&sort=date"

    try:
        result = subprocess.run(
            ["curl", "-s", "-w", "\n%{http_code}", url,
             "-H", f"X-Naver-Client-Id: {client_id}",
             "-H", f"X-Naver-Client-Secret: {client_secret}"],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.rsplit("\n", 1)
        body = parts[0]
        status = int(parts[1]) if len(parts) > 1 else 0

        if status == 401 or status == 403:
            print(json.dumps({
                "error": f"API 인증 실패 (HTTP {status})",
                "hint": "NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 확인하세요."
            }), file=sys.stderr)
            sys.exit(1)
        elif status != 200:
            print(json.dumps({"error": f"API 오류 (HTTP {status})", "detail": body}), file=sys.stderr)
            sys.exit(1)

        return json.loads(body)
    except subprocess.TimeoutExpired:
        print(json.dumps({"error": "API 호출 시간 초과", "hint": "인터넷 연결 상태를 확인하세요."}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "네트워크 오류", "detail": str(e), "hint": "인터넷 연결 상태를 확인하세요."}), file=sys.stderr)
        sys.exit(1)

def filter_24h(items, hours=24):
    """Filter news items published within the last N hours."""
    now = datetime.now(KST)
    cutoff = now - timedelta(hours=hours)
    filtered = []
    seen_titles = set()

    for item in items:
        try:
            pub_date = parsedate_to_datetime(item["pubDate"])
        except (ValueError, TypeError):
            continue

        if pub_date < cutoff:
            continue

        clean_title = clean_html(item["title"])
        if clean_title in seen_titles:
            continue
        seen_titles.add(clean_title)

        filtered.append({
            "title": clean_title,
            "description": clean_html(item.get("description", "")),
            "link": item.get("originallink") or item.get("link", ""),
            "pubDate": pub_date.strftime("%Y-%m-%d %H:%M"),
            "source": item.get("originallink", "").split("/")[2] if item.get("originallink", "").startswith("http") else ""
        })

    return filtered

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "키워드를 입력하세요. 사용법: python3 fetch_news.py <키워드> [.env경로]"}), file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1].strip()
    if not keyword:
        print(json.dumps({"error": "빈 키워드입니다. 검색할 키워드를 입력하세요."}), file=sys.stderr)
        sys.exit(1)

    # Load .env
    env_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
    env = load_env(env_path)

    client_id = env.get("NAVER_CLIENT_ID", os.environ.get("NAVER_CLIENT_ID", ""))
    client_secret = env.get("NAVER_CLIENT_SECRET", os.environ.get("NAVER_CLIENT_SECRET", ""))

    if not client_id or not client_secret:
        print(json.dumps({
            "error": "API 키가 설정되지 않았습니다.",
            "hint": f".env 파일 위치: {os.path.abspath(env_path)}",
            "format": "NAVER_CLIENT_ID=your_id\nNAVER_CLIENT_SECRET=your_secret"
        }), file=sys.stderr)
        sys.exit(1)

    # Fetch and filter
    data = fetch_news(keyword, client_id, client_secret)
    items = data.get("items", [])
    filtered = filter_24h(items)

    result = {
        "keyword": keyword,
        "total_fetched": len(items),
        "total_filtered": len(filtered),
        "generated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
        "items": filtered
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
