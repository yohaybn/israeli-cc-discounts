from pathlib import Path

import yoter_scraper

HTML = (Path(__file__).parent / "fixtures" / "yoter" / "business_list.html").read_text(encoding="utf-8")


def test_parse_tiles():
    records = yoter_scraper.parse(HTML)
    assert len(records) == 12
    first = records[0]
    assert first["club"] == "יותר"
    assert first["business_name"] == "ONYX אוניקס"
    assert first["discount"] == "10% הנחה באתר אוניקס"
    assert first["discount_value"] == 10.0
    assert first["discount_url"].startswith("https://yoter.co.il/")
    assert first["category"] == "חשמל מחשבים ושונות"
    assert not first["has_physical_store"]


def test_scrape_uses_fetch():
    assert len(yoter_scraper.scrape(lambda url: HTML)) == 12
    assert yoter_scraper.fetch_raw(lambda url: HTML) == {"business_list.html": HTML}
