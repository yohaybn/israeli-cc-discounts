from pathlib import Path

from myofer_scraper import BASE_URL, deals_url, parse_deals_page, parse_malls, scrape

FIX = Path(__file__).parent / "fixtures" / "myofer"


def read(name):
    return (FIX / name).read_text(encoding="utf-8")


PAGES = {
    BASE_URL: read("home.html"),
    deals_url("grand-mall-petah-tikva"): read("deals_a.html"),
    deals_url("grand-mall-petah-tikva", 2): read("deals_a_p2.html"),
    deals_url("nahariya-mall"): read("deals_b.html"),
}


def test_parse_malls():
    assert [m["slug"] for m in parse_malls(read("home.html"))] == ["grand-mall-petah-tikva", "nahariya-mall"]


def test_deals_url_pages():
    assert deals_url("x") == "https://myofer.co.il/malls/x/deals"
    assert deals_url("x", 3) == "https://myofer.co.il/malls/x/deals?page=3"


def test_parse_deals_page():
    mall = {"slug": "grand-mall-petah-tikva", "name": "עופר הקניון הגדול"}
    records, total = parse_deals_page(read("deals_a.html"), mall)
    assert total == 12
    assert len(records) == 4
    first = records[0]
    assert first["club"] == "MY OFER - קניוני עופר"
    assert first["business_name"] == "CASTRO"
    assert first["discount_value"] == 20.0
    assert first["branches"] == [{"mall": "עופר הקניון הגדול"}]
    assert "<" not in first["limitations"]


def test_scrape_pages_and_merges_shared_deals():
    seen = []

    def fake_fetch(url):
        seen.append(url)
        return PAGES[url]

    records = scrape(fetch=fake_fetch)
    assert deals_url("grand-mall-petah-tikva", 2) in seen
    assert len(records) == 8
    shared = [r for r in records if len(r["branches"]) == 2]
    assert len(shared) == 1
    assert shared[0]["discount_url"] == BASE_URL
    assert all("_deal_id" not in r for r in records)


def test_empty_page():
    assert parse_deals_page("<html></html>", {"slug": "x", "name": "x"}) == ([], 0)
