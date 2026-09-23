from pathlib import Path

import happygift_scraper as s

HTML = (Path(__file__).parent / "fixtures" / "happygift" / "coupon_5041.html").read_text(encoding="utf-8")


def test_extract_suppliers_resolves_branch_references():
    suppliers = s.extract_suppliers(HTML)
    assert len(suppliers) == 4
    referenced = suppliers[0]
    assert referenced["supplierBranches"] == "$28"
    assert referenced["_branches"] and referenced["_branches"][0]["supplierId"] == int(referenced["id"])


def test_records_shape():
    records = s.parse_page(HTML, "+HappyGift", "5041")
    by_name = {r["business_name"]: r for r in records}
    assert set(by_name) == {"ספייסז - רשת חנויות קולינאריות", "רשת מסעדות Frame", "ג'ויה רמת החייל", "Wine Club"}
    frame = by_name["רשת מסעדות Frame"]
    assert frame["club"] == "+HappyGift"
    assert frame["discount_type"] == "gift_card"
    assert frame["discount_url"] == "https://catalog.happygift.co.il/coupon-suppliers/5041"
    assert len(frame["branches"]) == 3
    assert all(b.get("address") for b in frame["branches"])
    assert "<" not in frame["limitations"]
    assert by_name["Wine Club"]["has_physical_store"] is False
    assert by_name["Wine Club"]["branches"] == []


def test_text_chunk_uses_utf8_byte_length():
    payload = '0:{}\n7:T6,שלוםX'  # "שלום" is 8 bytes, so only the first 3 letters fit in 6 bytes
    assert s.text_chunk(payload, "7") == "שלו"
    assert s.text_chunk(payload, "9") == ""


def test_parse_pg_json_array_skips_bad_items():
    value = '{"{\\"id\\":1,\\"name\\":\\"א\\"}","not json"}'
    assert s.parse_pg_json_array(value) == [{"id": 1, "name": "א"}]
    assert s.parse_pg_json_array("{}") == []


def test_scrape_merges_physical_and_digital_coupons():
    pages = []

    def fake_fetch(url):
        pages.append(url)
        return HTML

    records = s.scrape(fake_fetch)
    assert len(pages) == 3
    clubs = {r["club"] for r in records}
    assert clubs == {"+HappyGift", "HappyGift Multi"}
    multi = [r for r in records if r["club"] == "HappyGift Multi"]
    assert len(multi) == 4  # same fixture under 3198 and 4313 merged per business
    assert len({r["business_name"] for r in multi}) == 4


def test_page_without_payload():
    assert s.parse_page("<html></html>", "+HappyGift", "5041") == []
    assert s.scrape(lambda url: "<html></html>") == []


def test_one_failing_coupon_does_not_drop_the_others():
    def flaky(url):
        if url.endswith("/3198"):
            raise RuntimeError("boom")
        return HTML

    records = s.scrape(flaky)
    assert {r["club"] for r in records} == {"+HappyGift", "HappyGift Multi"}
