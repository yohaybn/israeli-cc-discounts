from pathlib import Path

import miluim_benefits_scraper as s

JSON = (Path(__file__).parent / "fixtures" / "miluim_benefits" / "benefits.json").read_text(encoding="utf-8")


def test_records():
    records = s.scrape(lambda url: JSON)
    assert len(records) == 4
    assert records[0]["business_name"] == "אבחון תעסוקתי דיגיטלי"
    assert records[0]["discount_url"].startswith("https://www.miluim.idf.il/benefits-list/")
    assert "קריירה" in records[0]["limitations"]
    assert s.parse('{"benefits": []}') == []
