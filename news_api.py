from Flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import feedparser
import requests
import os

app = Flask(__name__)

def get_user_location(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = resp.json()
        return {
            "city": data.get("city", ""),
            "countryCode": data.get("countryCode", "IN")
        }
    except Exception:
        return {"city": "", "countryCode": "IN"}

@app.route("/get-news")
def get_news():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    loc = get_user_location(user_ip)
    city = loc["city"]
    country = loc["countryCode"]
    query = city if city else country

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={query}&hl=en&gl={country}&ceid={country}:en"
    )

    feed = feedparser.parse(rss_url)
    articles = []

    for entry in feed.entries[:5]:
        summary = BeautifulSoup(entry.summary, "html.parser").get_text()
        image_url = None
        if 'img src="' in entry.summary:
            start = entry.summary.find('img src="') + len('img src="')
            end = entry.summary.find('"', start)
            image_url = entry.summary[start:end]

        articles.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "image": image_url,
            "location": city or country
        })

    return jsonify(articles)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
