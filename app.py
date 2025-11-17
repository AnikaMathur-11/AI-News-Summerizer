import os
from datetime import datetime
from typing import Dict, List

from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# -------------------------
# Config
# -------------------------
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-cnn")
TOP_K = 5  # number of top news items to show

# Newspaper -> Category -> RSS feed URL
RSS_FEEDS: Dict[str, Dict[str, str]] = {
    "The Hindu": {
        "India": "https://www.thehindu.com/news/national/feeder/default.rss",
        "World": "https://www.thehindu.com/news/international/feeder/default.rss",
        "Sports": "https://www.thehindu.com/sport/feeder/default.rss",
        "Tech": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
    },
    "Times of India": {
        "India": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "World": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "Sports": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "Tech": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
    },
    "Hindustan Times": {
        "India": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "World": "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
        "Sports": "https://www.hindustantimes.com/feeds/rss/sports/rssfeed.xml",
        "Tech": "https://www.hindustantimes.com/feeds/rss/tech/rssfeed.xml",
    },
}

# Dummy fallback news: per category, realistic but static
DUMMY_NEWS: Dict[str, List[Dict]] = {
    "India": [
        {
            "title": "Government launches new skill development initiative for students",
            "summary": "The central government has announced a nationwide skill development program aimed at improving job readiness among college students. The initiative will focus on digital skills, entrepreneurship, and collaboration with industry partners.",
            "link": "https://example.com/india-skill-development",
            "published": "Demo · India",
            "source": "The Hindu",
        },
        {
            "title": "Major metro city introduces green public transport corridor",
            "summary": "A major Indian metro has rolled out a dedicated green transport corridor with electric buses and improved cycling infrastructure, aiming to cut air pollution and promote sustainable commuting.",
            "link": "https://example.com/india-green-transport",
            "published": "Demo · India",
            "source": "Times of India",
        },
        {
            "title": "National education council proposes exam reforms for universities",
            "summary": "The national education council has proposed flexible assessment policies and more continuous evaluation in universities, with the goal of reducing exam stress and emphasizing practical learning.",
            "link": "https://example.com/india-exam-reforms",
            "published": "Demo · India",
            "source": "Hindustan Times",
        },
        {
            "title": "Monsoon forecast indicates normal rainfall across most regions",
            "summary": "The weather department has predicted normal monsoon rainfall across most parts of the country, which is expected to support agriculture and stabilize food prices.",
            "link": "https://example.com/india-monsoon-forecast",
            "published": "Demo · India",
            "source": "The Hindu",
        },
        {
            "title": "Startup ecosystem sees rise in student-led innovations",
            "summary": "Incubators across India have reported a sharp increase in student-led startups, with ideas spanning fintech, edtech, and sustainability-focused solutions.",
            "link": "https://example.com/india-student-startups",
            "published": "Demo · India",
            "source": "Hindustan Times",
        },
    ],
    "World": [
        {
            "title": "Global summit focuses on climate resilience and green technology",
            "summary": "World leaders and experts gathered at an international summit to discuss climate resilience, green technologies, and collaborative efforts to reduce carbon emissions.",
            "link": "https://example.com/world-climate-summit",
            "published": "Demo · World",
            "source": "Times of India",
        },
        {
            "title": "Tech giants agree on common AI safety principles",
            "summary": "Major technology companies from different countries have signed a voluntary agreement to follow common AI safety guidelines, focusing on transparency, fairness, and accountability.",
            "link": "https://example.com/world-ai-safety",
            "published": "Demo · World",
            "source": "The Hindu",
        },
        {
            "title": "International students return to campuses as travel rules ease",
            "summary": "Universities across the globe are witnessing a rise in international student admissions as travel restrictions are relaxed and hybrid learning options become standard.",
            "link": "https://example.com/world-students-return",
            "published": "Demo · World",
            "source": "Hindustan Times",
        },
        {
            "title": "Space agencies collaborate on new lunar exploration mission",
            "summary": "Multiple space agencies have announced a joint mission to explore the Moon’s south pole, focusing on water ice detection and long-term human presence.",
            "link": "https://example.com/world-lunar-mission",
            "published": "Demo · World",
            "source": "The Hindu",
        },
        {
            "title": "Global markets stabilize after period of volatility",
            "summary": "International financial markets have shown signs of stabilization following weeks of volatility driven by policy changes and economic data releases.",
            "link": "https://example.com/world-markets-stabilize",
            "published": "Demo · World",
            "source": "Times of India",
        },
    ],
    "Sports": [
        {
            "title": "India clinches thrilling T20 series win against top rival",
            "summary": "In a closely fought T20 series, India sealed victory in the final match with a strong batting performance and disciplined bowling at the death overs.",
            "link": "https://example.com/sports-t20-series",
            "published": "Demo · Sports",
            "source": "Hindustan Times",
        },
        {
            "title": "Young pacer shines in debut Test match",
            "summary": "A young fast bowler impressed on debut with a fiery spell, picking up key wickets and earning praise from senior players and experts.",
            "link": "https://example.com/sports-debut-pacer",
            "published": "Demo · Sports",
            "source": "The Hindu",
        },
        {
            "title": "Domestic cricket league announces new format for playoffs",
            "summary": "Organizers of a popular domestic cricket league have unveiled a revised playoff format aimed at increasing competition and engaging fans.",
            "link": "https://example.com/sports-league-format",
            "published": "Demo · Sports",
            "source": "Times of India",
        },
        {
            "title": "Indian athletes set new national records in athletics meet",
            "summary": "Several Indian athletes broke national records at a recent athletics meet, boosting confidence ahead of upcoming international tournaments.",
            "link": "https://example.com/sports-athletics-records",
            "published": "Demo · Sports",
            "source": "Hindustan Times",
        },
        {
            "title": "Coach outlines roadmap for upcoming cricket world events",
            "summary": "The national team's head coach shared a detailed roadmap covering player rotation, workload management, and preparation camps for upcoming world tournaments.",
            "link": "https://example.com/sports-coach-roadmap",
            "published": "Demo · Sports",
            "source": "The Hindu",
        },
    ],
    "Tech": [
        {
            "title": "Indian startups explore generative AI for education and healthcare",
            "summary": "Several Indian startups are experimenting with generative AI tools to improve personalized learning, medical triage, and language translation services.",
            "link": "https://example.com/tech-generative-ai-india",
            "published": "Demo · Tech",
            "source": "Hindustan Times",
        },
        {
            "title": "New smartphone series launched with focus on battery and cameras",
            "summary": "A leading smartphone manufacturer has introduced its latest series featuring larger batteries, improved night photography, and extended software support.",
            "link": "https://example.com/tech-smartphone-launch",
            "published": "Demo · Tech",
            "source": "Times of India",
        },
        {
            "title": "Government announces support scheme for deep-tech research",
            "summary": "The government has introduced a support scheme for deep-tech startups and research labs working in AI, space technology, and cybersecurity.",
            "link": "https://example.com/tech-deeptech-support",
            "published": "Demo · Tech",
            "source": "The Hindu",
        },
        {
            "title": "Universities adopt cloud-based labs for coding and ML courses",
            "summary": "Engineering colleges and universities are adopting cloud-based virtual labs to provide hands-on experience in programming, data science, and machine learning.",
            "link": "https://example.com/tech-cloud-labs",
            "published": "Demo · Tech",
            "source": "Hindustan Times",
        },
        {
            "title": "Cybersecurity experts warn about rising phishing attacks",
            "summary": "Security researchers have reported a surge in phishing attempts targeting students and remote workers, urging users to enable multi-factor authentication.",
            "link": "https://example.com/tech-phishing-warning",
            "published": "Demo · Tech",
            "source": "Times of India",
        },
    ],
}

# -------------------------
# Flask app & model
# -------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

# Load Hugging Face summarizer once
try:
    summarizer = pipeline("summarization", model=MODEL_NAME, tokenizer=MODEL_NAME)
except Exception as e:
    raise RuntimeError(f"Could not load summarization model '{MODEL_NAME}': {e}")


def clean_whitespace(text: str) -> str:
    if not text:
        return ""
    return " ".join(str(text).split())


def strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(" ", strip=True)


def summarize_text(text: str) -> str:
    text = clean_whitespace(text)
    if not text:
        return ""

    # limit length so model is safe on CPU
    text = text[:3500]

    try:
        result = summarizer(
            text,
            max_length=140,
            min_length=50,
            do_sample=False,
        )
        if isinstance(result, list) and result:
            summary = result[0].get("summary_text", "")
            return clean_whitespace(summary) or text[:400]
    except Exception:
        pass

    return text[:400] + ("..." if len(text) > 400 else "")


def fetch_feed_items(source: str, category: str, limit: int = TOP_K) -> List[Dict]:
    """
    Fetch items from RSS feed.
    Will raise or return [] if there is a network/parse issue.
    """
    url = RSS_FEEDS[source][category]
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "xml")
    items_xml = soup.find_all("item")[:limit]

    items: List[Dict] = []
    for item in items_xml:
        title = item.title.get_text(strip=True) if item.title else "(no title)"
        link = item.link.get_text(strip=True) if item.link else ""
        pub_tag = item.find("pubDate") or item.find("dc:date")
        published = pub_tag.get_text(strip=True) if pub_tag else ""
        desc_tag = item.description or item.find("description")
        description = desc_tag.get_text() if desc_tag else ""
        description = strip_html(description)

        items.append(
            {
                "title": clean_whitespace(title),
                "link": link,
                "published": published,
                "description": clean_whitespace(description),
                "source": source,
                "category": category,
            }
        )
    return items


@app.route("/", methods=["GET", "POST"])
def index():
    newspapers = list(RSS_FEEDS.keys())
    categories = ["India", "World", "Sports", "Tech"]

    selected_source = request.form.get("source", newspapers[0])
    selected_category = request.form.get("category", categories[0])

    summaries: List[Dict] = []

    if request.method == "POST":
        # Safety check
        if selected_source not in RSS_FEEDS or selected_category not in RSS_FEEDS[selected_source]:
            flash("Invalid selection. Please try again.", "danger")
            return redirect(url_for("index"))

        items: List[Dict] = []
        try:
            items = fetch_feed_items(selected_source, selected_category)
        except Exception:
            # any RSS/network problem -> we just fall back to dummy
            items = []

        if not items:
            # Use dummy news for that category, no summarizer needed
            for d in DUMMY_NEWS[selected_category]:
                summaries.append(d)
        else:
            # Summarize live news
            for item in items:
                combined = f"{item['title']}. {item['description']}".strip()
                summary = summarize_text(combined)
                summaries.append(
                    {
                        "title": item["title"],
                        "summary": summary,
                        "link": item["link"],
                        "published": item["published"],
                        "source": item["source"],
                    }
                )

    return render_template(
        "index.html",
        newspapers=newspapers,
        categories=categories,
        selected_source=selected_source,
        selected_category=selected_category,
        summaries=summaries,
        model_name=MODEL_NAME,
        last_updated=datetime.now().strftime("%b %d, %Y %I:%M %p"),
    )


@app.route("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
