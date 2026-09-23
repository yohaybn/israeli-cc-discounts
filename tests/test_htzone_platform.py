import json
from pathlib import Path

import goldnorth_scraper
import htzone_platform
import metzer_scraper

FIX = Path(__file__).parent / "fixtures" / "htzone_platform"
HOME = (FIX / "metzer_home.html").read_text(encoding="utf-8")
CAT = (FIX / "metzer_category_4747.html").read_text(encoding="utf-8")
ITEMS = json.loads((FIX / "metzer_items.json").read_text(encoding="utf-8"))
BASE = "https://metzer.htzone.co.il/"


def test_page_helpers():
    assert "4747" in htzone_platform.category_ids(HOME)
    assert len(htzone_platform.category_ids(HOME)) >= 20
    assert htzone_platform.block_ids(CAT)[0] == "6848"
    assert len(htzone_platform.page_token(CAT)) == 32
    assert htzone_platform.category_name(CAT) == "הטבות מיוחדות למצר"


def test_parse_items_keeps_benefits_only():
    records = htzone_platform.parse_items(ITEMS, BASE, "מצר", "cat", "note")
    assert len(records) == len(ITEMS) - 1  # the shop product is skipped
    first = records[0]
    assert first["business_name"] == "כתר פלסטיק"
    assert first["discount"].startswith("5% הנחה")
    assert first["discount_value"] == 5.0
    assert first["discount_url"] == BASE + "item/119553"
    assert first["category"] == "cat" and first["limitations"] == "note"


def test_crawl_with_fake_io():
    pages = {BASE: HOME}
    posts = []

    def fetch(url):
        return pages.get(url, CAT)

    def post(url, data):
        posts.append(data)
        assert url == BASE + "ajax" and data["act"] == "category_items" and data["token"]
        return ITEMS if data["id"] == "6848" else {}

    records = htzone_platform.crawl(BASE, "מצר", fetch, post)
    assert len(records) == len(ITEMS) - 1
    assert len({p["id"] for p in posts}) == len(posts)  # each block fetched once


def test_club_modules():
    for module in (metzer_scraper, goldnorth_scraper):
        assert module.SOURCE_KEY and module.CLUB_NAME and module.BASE_URL.endswith(".htzone.co.il/")
        records = module.scrape(lambda url: HOME if url == module.BASE_URL else CAT, lambda url, data: ITEMS)
        assert records and all(r["club"] == module.CLUB_NAME for r in records)
