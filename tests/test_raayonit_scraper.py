from pathlib import Path

from raayonit_scraper import SOURCE_URL, parse_raayonit_html, scrape

FIXTURE = Path(__file__).parent / "fixtures" / "raayonit_global_tav.html"
HTML = FIXTURE.read_text(encoding="utf-8")


def _by_name():
    return {r["business_name"]: r for r in parse_raayonit_html(HTML)}


def test_networks_and_businesses_are_parsed():
    records = parse_raayonit_html(HTML)
    assert len(records) == 7
    assert all(r["club"] == "גלובל קארד - רעיונית" for r in records)
    assert all(r["discount_type"] == "gift_card" for r in records)


def test_network_tile_links_to_network_page():
    cafe = _by_name()["CaféCafé"]
    assert "NetworkNum=25" in cafe["discount_url"]
    assert cafe["category"] == "רשתות"


def test_business_branches_are_merged():
    mexicana = _by_name()["מקסיקנה תל אביב"]
    assert mexicana["limitations"].count("כתובת:") == 3
    assert "שרונה מרקט" in mexicana["limitations"]
    assert mexicana["discount_url"] == SOURCE_URL


def test_online_store_is_not_physical():
    assert _by_name()["מזקקת אולגר - OLGAR DISTILLERY"]["has_physical_store"] is False
    assert _by_name()["BEN AMI"]["has_physical_store"] is True


def test_changed_markup_returns_empty():
    assert parse_raayonit_html("<html><body>maintenance</body></html>") == []


def test_scrape_fetches_source_url():
    seen = []
    assert len(scrape(fetch=lambda url: seen.append(url) or HTML)) == 7
    assert seen == [SOURCE_URL]
