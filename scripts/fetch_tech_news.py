import feedparser

def get_tech_news():
    url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(url)

    if not feed.entries:
        print("❌ No articles found in RSS.")
        return None

    first = feed.entries[0]
    return {
        "title": first.title,
        "description": first.summary,
        "image_query": first.title
    }
