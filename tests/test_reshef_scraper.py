from pathlib import Path

import reshef_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "reshef" / "benefits.html").read_text(encoding="utf-8")


def test_records():
    records = s.scrape(lambda url: HTML)
    assert len(records) == 9
    assert records[0]["discount_type"] == "club_card"
    assert any(r["discount_type"] == "discount" for r in records)
    assert all(r["discount_url"].startswith("http") for r in records)
    assert s.parse("<p>none</p>") == []
