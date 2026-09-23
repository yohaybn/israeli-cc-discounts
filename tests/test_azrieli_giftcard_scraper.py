import json
from pathlib import Path

from azrieli_giftcard_scraper import BUYME_BRAND_ID, normalize_azrieli, scrape

PAYLOAD = json.loads((Path(__file__).parent / "fixtures" / "azrieli_giftcard_buyme.json").read_text(encoding="utf-8"))


def test_normalize_relabels_buyme_stores():
    records = normalize_azrieli(PAYLOAD["stores"])
    assert len(records) == 4  # five stores in the fixture, one duplicate
    first = records[0]
    assert first["club"] == "עזריאלי גיפטקארד"
    assert first["business_name"] == "שילב"
    assert first["discount_type"] == "gift_card"
    assert first["discount_url"].startswith("https://buyme.co.il/brands/398383")
    assert "<" not in first["limitations"]
    assert "אזורים:" in first["limitations"]


def test_online_only_store_is_not_physical():
    records = normalize_azrieli(PAYLOAD["stores"])
    assert sum(1 for r in records if r["has_physical_store"] is False) == 1


def test_scrape_uses_the_azrieli_brand_id():
    seen = []

    def fake_fetch(brand_id):
        seen.append(brand_id)
        return PAYLOAD

    assert len(scrape(fetch=fake_fetch)) == 4
    assert seen == [BUYME_BRAND_ID]


def test_empty_payload_returns_empty():
    assert scrape(fetch=lambda brand_id: {}) == []
