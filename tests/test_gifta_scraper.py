import json
from pathlib import Path

import pytest

from gifta_scraper import normalize_gifta, scrape
from wp_catalog import term_names

FIXTURES = Path(__file__).parent / "fixtures"
POSTS = json.loads((FIXTURES / "gifta_posts.json").read_text(encoding="utf-8"))
CATEGORIES = json.loads((FIXTURES / "gifta_categories.json").read_text(encoding="utf-8"))


def fake_fetch(url):
    if "/categories?" in url:
        return json.dumps(CATEGORIES if "page=1&" in url else [])
    if "/posts?" in url:
        return json.dumps(POSTS if "page=1&" in url else [])
    raise AssertionError(url)


def test_normalize_posts():
    records = normalize_gifta(POSTS, term_names(CATEGORIES))
    assert len(records) == 5
    first = records[0]
    assert first["club"] == "גיפטא"
    assert first["business_name"] == "גולף אנד קו"
    assert first["discount_type"] == "gift_card"
    assert first["category"] == "לבית"
    assert first["discount_url"].startswith("https://gifta.co.il/")


def test_branch_addresses_land_in_limitations_without_pins():
    leader = [r for r in normalize_gifta(POSTS, term_names(CATEGORIES)) if r["business_name"] == "לידר"][0]
    assert leader["limitations"].startswith("סניפים: ")
    assert "📍" not in leader["limitations"]
    assert "אופקים" in leader["limitations"]


def test_site_categories_are_not_used_as_store_category():
    amiroz = [r for r in normalize_gifta(POSTS, term_names(CATEGORIES)) if r["business_name"] == "אמירוז"][0]
    assert amiroz["category"] != "Uncategorized"


def test_duplicate_posts_are_dropped():
    assert len(normalize_gifta(POSTS + POSTS[:2], term_names(CATEGORIES))) == 5


def test_scrape_walks_the_wp_api():
    assert len(scrape(fetch=fake_fetch)) == 5


def test_scrape_raises_when_api_is_blocked():
    def blocked(url):
        raise RuntimeError("403")

    with pytest.raises(RuntimeError):
        scrape(fetch=blocked)
