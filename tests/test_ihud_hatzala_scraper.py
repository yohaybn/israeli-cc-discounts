import json
from pathlib import Path

import ihud_hatzala_scraper as s

RAW = (Path(__file__).parent / "fixtures" / "ihud_hatzala" / "products.json").read_text(encoding="utf-8")


def test_parse_products():
    records = s.parse(json.loads(RAW))
    assert len(records) == 4
    assert records[1]["business_name"] == "בורגרס בר תלפיות"
    assert records[1]["discount"] == "15% הנחה על כל התפריט!"
    assert records[1]["discount_value"] == 15.0
    assert records[3]["discount"].startswith("18₪")
    assert records[0]["discount_url"].startswith("https://4u.1221.org.il/product/")


def test_benefit_line_skips_generic_intro():
    html = "<p>🧡<strong>צוות רווחת המתנדב שמח להציג</strong>🧡</p><p>20% הנחה בחנות</p>"
    assert s.benefit_line(html) == "20% הנחה בחנות"


def test_scrape_single_short_page():
    calls = []

    def fetch(url):
        calls.append(url)
        return RAW

    assert len(s.scrape(fetch)) == 4
    assert len(calls) == 1
