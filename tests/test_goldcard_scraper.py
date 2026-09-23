import json
from pathlib import Path

from goldcard_scraper import normalize_goldcard, scrape
from wp_catalog import term_names

FIXTURES = Path(__file__).parent / "fixtures"
BRANDS = json.loads((FIXTURES / "goldcard_brands.json").read_text(encoding="utf-8"))
CATEGORIES = json.loads((FIXTURES / "goldcard_brand_categories.json").read_text(encoding="utf-8"))
CITIES = json.loads((FIXTURES / "goldcard_cities.json").read_text(encoding="utf-8"))


def fake_fetch(url):
    for key, data in (("/brands?", BRANDS), ("/brand-categories?", CATEGORIES), ("/cities-category?", CITIES)):
        if key in url:
            return json.dumps(data if "page=1&" in url else [])
    raise AssertionError(url)


def _records():
    return normalize_goldcard(BRANDS, term_names(CATEGORIES), term_names(CITIES))


def test_normalize_brands():
    records = _records()
    assert len(records) == 4
    first = records[0]
    assert first["club"] == "גולד קארד"
    assert first["business_name"] == "גולד בייבי"
    assert first["discount_type"] == "gift_card"
    assert first["category"] == "ילדים ותינוקות"
    assert first["limitations"].startswith("ערים: ")
    assert "בני ברק" in first["limitations"]


def test_html_entities_are_decoded():
    names = [r["business_name"] for r in _records()]
    assert "נועה קידס & הום" in names


def test_scrape_walks_the_wp_api():
    assert len(scrape(fetch=fake_fetch)) == 4


def test_empty_api_returns_no_records():
    assert scrape(fetch=lambda url: "[]") == []
