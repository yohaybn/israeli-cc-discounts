import json
from pathlib import Path

import moneyplan_scraper
import studentgroup_scraper

FIX = Path(__file__).parent / "fixtures"
SG = json.loads((FIX / "studentgroup" / "products.json").read_text(encoding="utf-8"))
MP = json.loads((FIX / "moneyplan" / "benefits.json").read_text(encoding="utf-8"))


def test_studentgroup_parse():
    records = studentgroup_scraper.parse(SG)
    assert len(records) == 5
    assert records[0]["business_name"] == "every"
    assert records[0]["discount"] == "קופון every תוספי תזונה מעניק 40% הנחה כולל כפל מבצעים"
    assert records[0]["discount_value"] == 40.0
    assert "מעודכן" not in records[1]["discount"]


def test_moneyplan_parse():
    records = moneyplan_scraper.parse(MP)
    assert len(records) == 4
    assert records[0]["business_name"] == "מיטב טרייד"
    assert "חתול פיננסי" in records[0]["discount"]
    assert records[0]["discount_url"].startswith("https://moneyplan.co.il/benefits/")


def test_scrape_uses_fetch():
    assert len(studentgroup_scraper.scrape(lambda url: json.dumps(SG))) == 5
    assert len(moneyplan_scraper.scrape(lambda url: json.dumps(MP))) == 4
