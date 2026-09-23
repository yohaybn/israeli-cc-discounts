from pathlib import Path

import dolcemaster_platform as platform
import tovplus_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "tovplus" / "category.html").read_text(encoding="utf-8")


def test_benefit_text_prices():
    text, percent = platform.benefit_text({"club_price": 79, "market_price": 159, "short_description": "<p>חנוכה | רחבי הארץ</p>"})
    assert text == "79 ₪ במקום 159 ₪ (50% חיסכון) - חנוכה | רחבי הארץ"
    assert percent == 50.0
    assert platform.benefit_text({"club_price": 0, "market_price": 0, "short_description": "<p>הטבת פלוס</p>"}) == ("", None)


def test_crawl_dedupes_products_across_categories():
    calls = []

    def fetch(url):
        calls.append(url)
        return HTML

    products = platform.crawl("https://tovplus.org.il", 1241, fetch)
    assert len(products) == 3
    assert calls[0] == "https://tovplus.org.il/category/1241"
    assert "https://tovplus.org.il/category/1275" in calls


def test_scrape_records():
    records = s.scrape(lambda url: HTML)
    assert len(records) == 3
    assert records[0]["business_name"] == "סביב העולם ב80 יום"
    assert records[0]["discount"] == "89 ₪ במקום 229 ₪ (61% חיסכון)"
    assert records[0]["discount_value"] == 61.0
    assert records[0]["discount_url"] == "https://tovplus.org.il/product/35617"
