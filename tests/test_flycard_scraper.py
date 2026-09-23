from pathlib import Path

import flycard_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "flycard" / "flycard.html").read_text(encoding="utf-8")


def test_records():
    records = s.scrape(lambda url: HTML)
    assert len(records) == 3
    assert records[0]["discount"].startswith("מתנת הצטרפות")
    assert records[1]["discount"].startswith("הטבת יום הולדת")
    assert s.parse("<p>none</p>") == []
