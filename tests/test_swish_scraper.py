from pathlib import Path

from swish_scraper import CARDS, parse_page, scrape

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


def test_scrape_fetches_every_card_and_labels_club():
    seen = []

    def fake_fetch(url):
        seen.append(url)
        return HTML

    records = scrape(fetch=fake_fetch)
    assert seen == list(CARDS.values())
    assert len(records) == 3 * len(CARDS)
    assert {r["club"] for r in records} == set(CARDS)
    perfect = [r for r in records if r["club"] == "Swish Perfect"]
    assert perfect[0]["discount"] == "מכבד את גיפט קארד Swish Perfect"


def test_one_failing_card_does_not_drop_others():
    def fake_fetch(url):
        if url == CARDS["Swish Unique"]:
            raise RuntimeError("boom")
        return HTML

    records = scrape(fetch=fake_fetch)
    assert "Swish Unique" not in {r["club"] for r in records}
    assert len(records) == 3 * (len(CARDS) - 1)


def test_page_without_payload_returns_empty():
    assert parse_page("<html></html>") == []
