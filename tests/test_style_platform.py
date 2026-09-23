from pathlib import Path

import adif_scraper
import egged_driver_scraper
import insurance_agents_scraper
import police_funds_scraper
import lahav_scraper
import lifestyle_club_scraper
import volunteers_club_scraper
import tzair_scraper
import icard_scraper
import hibenefit_scraper
import style_platform
import workers_style_scraper

FIX = Path(__file__).parent / "fixtures"
HOME = (FIX / "style_platform" / "workers_home.html").read_text(encoding="utf-8")
CAT7 = (FIX / "style_platform" / "workers_category_7.html").read_text(encoding="utf-8")
BOX_ITEM_CAT = (FIX / "shufersal4u" / "category_7.html").read_text(encoding="utf-8")
BASE = "https://workers.style.co.il/"


def test_category_links():
    links = style_platform.category_links(HOME)
    assert links["7"] == "מזון"
    assert len(links) >= 8


def test_parse_product_title_template():
    records = style_platform.parse_category(CAT7, BASE, "כח לעובדים", "מזון", "note")
    assert len(records) > 50
    first = records[0]
    assert first["club"] == "כח לעובדים"
    assert first["discount_url"].startswith(BASE + "?page=Benefit&uuid=")
    assert first["category"] == "מזון"
    assert first["limitations"] == "note"
    assert any(r["discount_value"] for r in records)


def test_parse_box_item_template():
    records = style_platform.parse_category(BOX_ITEM_CAT, "https://www.shufersal4u.co.il/", "x")
    assert len(records) > 20
    assert all(r["business_name"] for r in records)


def test_crawl_dedupes_and_skips_generic_category_label():
    def fake_fetch(url):
        if url == BASE:
            return HOME
        if url.endswith("id=7"):
            return CAT7
        return "<html></html>"

    records = style_platform.crawl(BASE, "כח לעובדים", fake_fetch)
    urls = [r["discount_url"] for r in records]
    assert len(urls) == len(set(urls))
    assert records


def test_thin_modules_use_their_base_url():
    for module in (workers_style_scraper, adif_scraper, hibenefit_scraper, egged_driver_scraper, insurance_agents_scraper, police_funds_scraper, lahav_scraper, lifestyle_club_scraper, volunteers_club_scraper, tzair_scraper, icard_scraper):
        seen = []

        def fake_fetch(url, seen=seen):
            seen.append(url)
            return "<html></html>"

        assert module.scrape(fetch=fake_fetch) == []
        assert seen == [module.BASE_URL]
