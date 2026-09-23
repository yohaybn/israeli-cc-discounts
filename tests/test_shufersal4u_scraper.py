from pathlib import Path

from shufersal4u_scraper import BASE_URL, category_links, parse_category, saving_percent, scrape

FIX = Path(__file__).parent / "fixtures" / "shufersal4u"
HOME = (FIX / "home.html").read_text(encoding="utf-8")
CAT7 = (FIX / "category_7.html").read_text(encoding="utf-8")


def test_category_links_prefer_real_names():
    links = category_links(HOME)
    assert links["7"] == "מזון"
    assert links["68"] == "מסעדות"


def test_saving_percent_variants():
    assert saving_percent("לרכישה ב-₪90 בשווי ₪100") == 10.0
    assert saving_percent("לרכישה ב-170 ₪ בשווי 200 ₪") == 15.0
    assert saving_percent("לרכישה ב-₪98 במקום ₪124") == 21.0
    assert saving_percent("שוברים ב-15% הנחה") == 15.0
    assert saving_percent("החל מ-₪168") is None


def test_parse_category_tiles():
    records = parse_category(CAT7, "מזון")
    assert len(records) > 20
    first = records[0]
    assert first["club"] == "שופרסל 4U"
    assert first["discount_type"] == "voucher"
    assert first["discount_url"].startswith(BASE_URL + "?page=Benefit&uuid=")
    assert "category_id" not in first["discount_url"]
    assert first["category"] == "מזון"


def test_scrape_walks_categories_and_dedupes_by_uuid():
    def fake_fetch(url):
        if url == BASE_URL:
            return HOME
        if url.endswith("id=7"):
            return CAT7
        return "<html></html>"

    records = scrape(fetch=fake_fetch)
    urls = [r["discount_url"] for r in records]
    assert len(urls) == len(set(urls))
    assert len(records) == len({r["discount_url"] for r in parse_category(CAT7)})
