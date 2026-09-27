import json
from datetime import datetime, timezone
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
            if "getBenefits" in body["query"]:
                seen.append(body["variables"]["f"]["shopId"])
                return PAYLOAD
            return {"data": {"products": {"count": 0, "items": []}}}

        records = module.scrape(post)
        assert seen[0] == shop and len(records) == 6 and records[0]["club"] == module.CLUB_NAME


def test_product_request_and_pagination():
    calls = []
    def post(url, body):
        calls.append(body["variables"]["filter"])
        assert "isNoRemainingCoupons(shopId:\"1\")" in body["query"]
        page = body["variables"]["filter"]["page"]
        return {"data": {"products": {"count": 201,
            "items": [{"id": str(page * 200 + i)} for i in range(200 if page == 0 else 1)]}}}
    items = uniq_platform.fetch_products("1", post)
    assert len(items) == 201
    assert [x["page"] for x in calls] == [0, 1]


def test_parse_coupon_product_only_and_skip_invalid():
    base = {"id": "55", "name": "קולנוע א", "type": "coupon", "price": 40,
            "originalPrice": 60, "unitsInStock": 10, "validUntil": "2026-12-31T20:00:00.000Z",
            "description": "<p>מימוש בסניפים</p>"}
    items = [base, {**base, "id": "56", "type": "regular"},
             {**base, "id": "57", "type": "QR"},
             {**base, "id": "58", "unitsInStock": 0},
             {**base, "id": "59", "isNoRemainingCoupons": True},
             {**base, "id": "60", "validUntil": "2026-01-01T00:00:00Z"},
             {**base, "id": "61", "price": 0}]
    records = uniq_platform.parse_coupons(items, "club", "https://example.com/", "member",
                                          now=datetime(2026, 9, 27, tzinfo=timezone.utc))
    assert len(records) == 1
    assert records[0]["discount_url"] == "https://example.com/product/55"
    assert records[0]["discount_type"] == "coupon"
    assert records[0]["discount_value"] is None
    assert records[0]["price"] == 40
    assert records[0]["original_price"] == 60
    assert records[0]["valid_until"] == base["validUntil"]
    assert records[0]["voucher_type"] == "coupon"


def test_club_modules_include_coupons_without_losing_benefits():
    for module in (uniq_scraper, tau_club_scraper):
        def post(url, body):
            if "getBenefits" in body["query"]:
                return PAYLOAD
            return {"data": {"products": {"count": 1, "items": [{"id": "55", "name": "קולנוע א",
                "type": "coupon", "price": 40, "originalPrice": 60, "unitsInStock": 10}]}}}
        result = module.scrape(post)
        assert len(result) == 7
        assert result[-1]["discount_type"] == "coupon"


def test_failed_coupon_catalog_raises_for_last_good_fallback():
    # Returning only benefits would overwrite the source file and lose prior coupons.
    import pytest
    def post(url, body):
        if "getBenefits" in body["query"]:
            return PAYLOAD
        return {"errors": [{"message": "catalog temporarily unavailable"}]}
    with pytest.raises(ValueError, match="products query failed"):
        uniq_scraper.scrape(post)


def test_truncated_product_catalog_fails_instead_of_dropping_coupons():
    import pytest
    def post(url, body):
        return {"data": {"products": {"count": 300, "items": [{"id": "1"}]}}}
    with pytest.raises(ValueError, match="ended early"):
        uniq_platform.fetch_products("1", post)
