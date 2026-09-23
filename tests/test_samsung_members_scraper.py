from pathlib import Path

import samsung_members_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "samsung_members" / "benefits.html").read_text(encoding="utf-8")


def test_parse_cards():
    records = s.parse(HTML)
    assert len(records) == 4
    assert records[0]["business_name"] == "Epic Menu בר 51 | 28.09"
    assert "199" in records[0]["discount"]
    assert records[2]["discount"].startswith("50 ₪ הנחה")
    assert records[0]["discount_url"].startswith("https://www.to-mix.co.il/")


def test_scrape_uses_fetch():
    assert len(s.scrape(lambda url: HTML)) == 4
