from pathlib import Path

import wincard_plus_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "wincard_plus" / "wincard.html").read_text(encoding="utf-8")


def test_records():
    records = s.scrape(lambda url: HTML)
    assert len(records) == 6
    assert records[0]["discount"].startswith("100₪ מתנת הצטרפות")
    assert records[1]["discount_value"] == 8.0
    assert s.parse("<p>none</p>") == []
