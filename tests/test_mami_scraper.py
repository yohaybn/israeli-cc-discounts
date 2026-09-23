from pathlib import Path

import mami_scraper

FIX = Path(__file__).parent / "fixtures" / "mami"
BRANDS = (FIX / "brands.html").read_text(encoding="utf-8")
CAT = (FIX / "category_fashion.html").read_text(encoding="utf-8")


def test_parse_brands():
    records = mami_scraper.parse_brands(BRANDS)
    assert len(records) == 6
    assert records[0]["business_name"] == "סיקרט"
    assert records[0]["discount"] == "10% צבירת Mami Money"
    assert records[0]["discount_value"] == 10.0
    assert records[0]["discount_url"] == "https://www.hi-mami.com/brands/seacret"


def test_parse_campaigns():
    records = mami_scraper.parse_campaigns(CAT, "fashion")
    assert len(records) == 5
    assert records[0]["business_name"] == "גוטקס | gottex"
    assert records[0]["discount"] == "אקסטרה 10% הנחה"
    assert records[0]["category"] == "fashion"
    assert "campaignId=" in records[0]["discount_url"]


def test_scrape_with_fake_fetch():
    home = '<a href="/categories/fashion">x</a>'
    pages = {mami_scraper.BASE_URL: home, mami_scraper.BRANDS_URL: BRANDS}
    records = mami_scraper.scrape(lambda url: pages.get(url, CAT))
    assert len(records) == 11
