import json
from pathlib import Path

import cpnclub_scraper as s

RAW = (Path(__file__).parent / "fixtures" / "cpnclub" / "search_club.json").read_text(encoding="utf-8")


def test_parse_suppliers():
    records = s.parse(json.loads(RAW)["data"])
    assert len(records) == 6
    assert records[0]["business_name"] == "אנחנו כבר גדולים"
    assert records[0]["discount_value"] is None
    assert records[0]["branches"] == []
    assert records[1]["branches"] == ["ראשון לציון"]
    gader = records[-1]
    assert gader["discount"] == "עד 17% הנחה לחברי קופונופש"
    assert gader["discount_value"] == 17.0
    assert gader["discount_url"] == "https://cpnclub.co.il/supplier/חמת-גדר"


def test_scrape_stops_after_last_page():
    calls = []

    def fetch(url):
        calls.append(url)
        return RAW

    assert len(s.scrape(fetch)) == 6
    assert len(calls) == 1
