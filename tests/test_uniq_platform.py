import json
from pathlib import Path

import tau_club_scraper
import uniq_platform
import uniq_scraper

PAYLOAD = json.loads((Path(__file__).parent / "fixtures" / "uniq_platform" / "tau_benefits.json").read_text(encoding="utf-8"))


def test_request_body():
    body = uniq_platform.request_body("2")
    assert body["variables"]["f"] == {"shopId": "2", "take": 1000}
    assert "getBenefits" in body["query"]


def test_parse():
    records = uniq_platform.parse(PAYLOAD, "club", "https://site/", "note")
    assert len(records) == 6
    first = records[0]
    assert first["business_name"] == "בר המזג | תל אביב"
    assert first["discount"] == "5% הנחה במעמד החיוב"
    assert first["discount_value"] == 5.0
    assert first["limitations"] == "note"
    assert records[2]["discount_value"] == 4.0


def test_club_modules_use_their_shop():
    for module, shop in ((uniq_scraper, "1"), (tau_club_scraper, "2")):
        seen = []

        def post(url, body):
            seen.append(body["variables"]["f"]["shopId"])
            return PAYLOAD

        records = module.scrape(post)
        assert seen == [shop] and len(records) == 6 and records[0]["club"] == module.CLUB_NAME
