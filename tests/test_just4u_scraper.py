from pathlib import Path

import just4u_scraper as s

JSON = (Path(__file__).parent / "fixtures" / "just4u" / "home.json").read_text(encoding="utf-8")


def test_records():
    records = s.scrape(lambda url: JSON)
    assert len(records) == 9
    first = records[0]
    assert first["business_name"] == "ריגושים עד הבית"
    assert "185" in first["discount"]
    assert first["discount_type"] == "voucher"
    assert any(r["discount_type"] == "gift_card" for r in records)
    assert s.parse('{"groups": null}') == []
