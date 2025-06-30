import feedparser
import requests

def fetch_news():
    url = "https://www.securityweek.com/feed/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        print(" Status:", response.status_code)
        return []

    feed = feedparser.parse(response.text)
    news = []

    for entry in feed.entries[:10]:
        news.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "N/A"),
            "summary": entry.get("summary", "No summary")
        })

    return news