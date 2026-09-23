import json
from pathlib import Path

from dreamcard_scraper import build_records, scrape, stores_by_chain

FIX = Path(__file__).parent / "fixtures" / "dreamcard"
BRANDS = json.loads((FIX / "brands.json").read_text(encoding="utf-8"))
BRANCHES = json.loads((FIX / "branches.json").read_text(encoding="utf-8"))


def by_name(records, english):
    return next(r for r in records if f"({english})" in r["business_name"])


def test_records_per_brand():
    records = build_records(BRANDS, BRANCHES)
    assert len(records) == 4
    fox = by_name(records, "FOX")
    assert fox["club"] == "DREAM CARD VIP"
    assert fox["discount_value"] == 15
    assert fox["discount_type"] == "club_card"
    assert fox["business_name"] == "פוקס (FOX)"


def test_shared_store_counts_for_both_brands():
    records = build_records(BRANDS, BRANCHES)
    assert len(by_name(records, "FOX")["branches"]) == 2  # "FOX / FOX HOME" store + a FOX store
    assert len(by_name(records, "FOX HOME")["branches"]) == 1


def test_name_normalization_and_alias():
    records = build_records(BRANDS, BRANCHES)
    assert by_name(records, "THE CHILDREN'S PLACE")["has_physical_store"] is True
    assert by_name(records, "QUICKSILVER")["has_physical_store"] is True


def test_branch_fields():
    stores = stores_by_chain(BRANCHES)
    branch = stores["FOXHOME"][0]
    assert branch["name"] and branch["city"]


def test_scrape_calls_both_endpoints():
    calls = []

    def fake_post(endpoint):
        calls.append(endpoint)
        return BRANDS if endpoint.startswith("Brands") else BRANCHES

    assert len(scrape(post=fake_post)) == 4
    assert calls == ["Brands/GetBrands", "Branches/GetBranchesData"]
