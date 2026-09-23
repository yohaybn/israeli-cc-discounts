from pathlib import Path

from swish_scraper import PAGE_URL, parse_page, scrape

HTML = (Path(__file__).parent / "fixtures" / "swish_plus.html").read_text(encoding="utf-8")


def test_parse_page_decodes_split_rsc_payload():
    records = parse_page(HTML)
    assert len(records) == 3  # four chains in the fixture, one duplicate
    first = records[0]
    assert first["club"] == "Swish Plus"
    assert first["business_name"] == "אפרודיטה"
    assert first["discount_type"] == "gift_card"
    assert first["discount_url"].startswith("https://")
    assert first["limitations"].startswith("קטגוריה:")


def test_html_notes_are_stripped_and_online_chain_flagged():
    records = parse_page(HTML)
    assert all("<" not in r["limitations"] for r in records)
    assert sum(1 for r in records if r["has_physical_store"] is False) == 1


def test_scrape_fetches_the_product_page():
    seen = []

    def fake_fetch(url):
        seen.append(url)
        return HTML

    assert len(scrape(fetch=fake_fetch)) == 3
    assert seen == [PAGE_URL]


def test_page_without_payload_returns_empty():
    assert parse_page("<html></html>") == []
