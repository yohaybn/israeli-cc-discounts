from pathlib import Path

import shachar_scraper

HTML = (Path(__file__).parent / "fixtures" / "shachar" / "benefits.html").read_text(encoding="utf-8")


def test_parse_tiles():
    records = shachar_scraper.parse(HTML)
    assert len(records) == 8
    assert all(r["club"] == "שחר" and r["business_name"] for r in records)
    assert any("הבית למחול" == r["business_name"] and r["discount"] == "NEW EARTH" for r in records)
    assert all(r["discount_url"].startswith("http") for r in records)


def test_scrape_uses_fetch():
    assert len(shachar_scraper.scrape(lambda url: HTML)) == 8
