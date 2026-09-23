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
