from pathlib import Path

from ima_yahad_scraper import parse_categories, parse_supplier, parse_supplier_list, scrape

FIX = Path(__file__).parent / "fixtures" / "ima_yahad"


def read(name):
    return (FIX / name).read_text(encoding="utf-8")


def test_parse_categories():
    categories = parse_categories(read("categories.html"))
    assert len(categories) > 100
    assert categories["5926"] == "אופטיקה ואופטומטריה"


def test_parse_supplier_list():
    assert parse_supplier_list(read("suppliers_5926.html"))[:2] == ["5", "7"]


def test_parse_supplier_with_branches():
    record = parse_supplier(read("supplier_5.html"), "5", "אופטיקה")
    assert record["business_name"] == 'אופטיקה גליקליס בע"מ'
    assert record["discount"] == "9%"
    assert record["discount_value"] == 9
    assert record["discount_url"].endswith("SupplierDetails.aspx?supId=5")
    assert record["has_physical_store"] is True
    assert record["branches"][0] == {"address": "מבצע יואב 49", "city": "באר שבע", "phone": "08-6421042"}
    assert record["category"] == "אופטיקה"


def test_parse_supplier_without_name_returns_none():
    assert parse_supplier("<html></html>", "1") is None


def test_scrape_crawls_categories_then_suppliers():
    pages = {
        "Categories.aspx": read("categories.html"),
        "Suppliers.aspx?CategoryId=5926": read("suppliers_5926.html"),
        "SupplierDetails.aspx?supId=5": read("supplier_5.html"),
        "SupplierDetails.aspx?supId=7": read("supplier_7.html"),
    }

    def fake_fetch(url):
        for key, html in pages.items():
            if url.endswith(key):
                return html
        raise RuntimeError("not in fixture")

    records = scrape(fetch=fake_fetch)
    assert [r["business_name"] for r in records] == ['אופטיקה גליקליס בע"מ', "אופטיקה זמיר"]


def _fixture_fetch(delay_for=None):
    import time

    pages = {
        "Categories.aspx": read("categories.html"),
        "Suppliers.aspx?CategoryId=5926": read("suppliers_5926.html"),
        "SupplierDetails.aspx?supId=5": read("supplier_5.html"),
        "SupplierDetails.aspx?supId=7": read("supplier_7.html"),
    }

    def fake_fetch(url):
        if delay_for and url.endswith(delay_for):
            time.sleep(0.05)  # the first supplier finishes last; order must still hold
        for key, html in pages.items():
            if url.endswith(key):
                return html
        raise RuntimeError("not in fixture")

    return fake_fetch


def test_parallel_scrape_keeps_order_and_matches_serial():
    serial = scrape(fetch=_fixture_fetch(), workers=1)
    parallel = scrape(fetch=_fixture_fetch(delay_for="supId=5"), workers=4)
    assert parallel == serial
    assert [r["business_name"] for r in parallel] == ['אופטיקה גליקליס בע"מ', "אופטיקה זמיר"]


def test_parallel_scrape_uses_several_workers():
    import threading
    import time

    active = {"now": 0, "max": 0}
    lock = threading.Lock()
    base = _fixture_fetch()

    def counting_fetch(url):
        with lock:
            active["now"] += 1
            active["max"] = max(active["max"], active["now"])
        try:
            time.sleep(0.02)
            return base(url)
        finally:
            with lock:
                active["now"] -= 1

    scrape(fetch=counting_fetch, workers=4)
    assert active["max"] >= 2
