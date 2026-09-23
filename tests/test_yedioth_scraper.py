from pathlib import Path

from yedioth_scraper import SOURCE_URL, parse_yedioth_html, scrape

HTML = (Path(__file__).parent / "fixtures" / "yedioth_homepage.html").read_text(encoding="utf-8")


def test_parse_boxes_and_dedupe():
    records = parse_yedioth_html(HTML)
    assert len(records) == 3
    first = records[0]
    assert first["club"] == "ידיעות אחרונות"
    assert first["business_name"] == "תערוכת הפרחים - מסע בין עולמות"
    assert first["discount"] == "כרטיס ב- 99 ₪"
    assert first["discount_url"].startswith("https://www.yedioth.co.il/products/")
    assert first["discount_type"] == "voucher"


def test_subtitle_equal_to_title_gets_generic_text():
    book = [r for r in parse_yedioth_html(HTML) if r["business_name"] == "ספר החודש"][0]
    assert book["discount"] == "הטבה למנויי ידיעות אחרונות: ספר החודש"


def test_changed_markup_returns_empty():
    assert parse_yedioth_html("<html></html>") == []


def test_scrape_fetches_homepage():
    seen = []
    assert len(scrape(fetch=lambda url: seen.append(url) or HTML)) == 3
    assert seen == [SOURCE_URL]
