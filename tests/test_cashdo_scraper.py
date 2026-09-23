from pathlib import Path

import cashdo_scraper

PAYLOAD = (Path(__file__).parent / "fixtures" / "cashdo" / "paging.json").read_text(encoding="utf-8")


def test_parse_tiles():
    records = cashdo_scraper.parse(PAYLOAD)
    assert len(records) == 5
    first = records[0]
    assert first["business_name"] == "AliExpress | אליאקספרס"
    assert first["discount"] == "עד 20% קאשבק"
    assert first["discount_value"] == 20.0
    assert first["discount_url"] == "https://cashdo.co.il/store/Aliexpress/1"
    assert first["has_physical_store"] is False


def test_scrape_uses_fetch():
    assert len(cashdo_scraper.scrape(lambda url: PAYLOAD)) == 5
