from pathlib import Path

import love_card_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "love_card" / "terms.html").read_text(encoding="utf-8")


def test_brand_names():
    assert s.brand_names(HTML) == ["קסטרו", "הודיס", "טופ-טן", "קרולינה למקה", "אורבניקה", "קיקו", "YVES ROCHER"]


def test_records():
    records = s.scrape(lambda url: HTML)
    assert len(records) == 7
    assert records[0]["discount_type"] == "gift_card"
    assert s.parse("<p>no list</p>") == []
