from pathlib import Path

import w_card_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "w_card" / "home.html").read_text(encoding="utf-8")


def test_parse_boxes():
    records = s.parse(HTML)
    assert len(records) == 3
    assert records[0]["business_name"] == "סטימצקי"
    assert records[0]["discount"] == "10% צבירת נקודות על קניות ברשת סטימצקי"
    assert records[1]["business_name"] == "GOLF וסטימצקי"
    assert records[1]["discount_value"] == 20.0


def test_scrape_uses_fetch():
    assert len(s.scrape(lambda url: HTML)) == 3
