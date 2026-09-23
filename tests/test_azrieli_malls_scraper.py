from pathlib import Path

import azrieli_malls_scraper

HTML = (Path(__file__).parent / "fixtures" / "azrieli_malls" / "coupons.html").read_text(encoding="utf-8")


def test_parse_groups_malls():
    records = azrieli_malls_scraper.parse(HTML)
    assert len(records) == 5  # 6 cards, one deal repeated in two malls
    first = records[0]
    assert first["business_name"] == "ארנקי אולגה"
    assert first["discount_value"] == 50.3
    assert first["discount_url"] == "https://www.azrielimalls.co.il/malls/haifa/coupons/54918"
    assert "חיפה" in first["limitations"]
    papaya = next(r for r in records if r["business_name"] == "papaya")
    assert "רמלה, ירושלים" in papaya["limitations"]


def test_scrape_uses_fetch():
    assert len(azrieli_malls_scraper.scrape(lambda url: HTML)) == 5
