from pathlib import Path
from unittest.mock import patch

import mizrahi_scraper
from mizrahi_scraper import SOURCE_URL, parse_mizrahi_html

FIXTURE = Path(__file__).parent / "fixtures" / "mizrahi_hacartis_all.html"


def _records():
    return parse_mizrahi_html(FIXTURE.read_text(encoding="utf-8"))


def test_parse_fixture_dedupes_and_normalizes():
    records = _records()
    # Five cards in the fixture, one is a duplicate of the first.
    assert len(records) == 4
    first = records[0]
    assert first["club"] == "מזרחי טפחות"
    assert first["business_name"] == "Airalo"
    assert first["discount"] == '20% הנחה על חבילות eSIM לחו"ל'
    assert first["discount_value"] == 20.0
    assert first["discount_url"] == "https://www.mizrahi-tefahot.co.il/hacartis/tourism/airalo-hot-0926/"
    assert first["category"] == "תיירות"
    assert first["limitations"] == "קוד הטבה"
    assert first["branches"] == []


def test_regular_card_uses_percent_badge_and_full_description():
    museum = _records()[-1]
    assert museum["business_name"] == "מוזיאון הרמן שטרוק חיפה"
    assert museum["discount"].startswith("10% הנחה - ")
    assert not museum["discount"].endswith("...")
    assert museum["discount_value"] == 10.0


def test_online_offer_is_not_physical():
    voye = [r for r in _records() if r["business_name"] == "Voye"][0]
    assert voye["has_physical_store"] is False
    assert voye["discount_value"] is None


def test_changed_markup_returns_empty():
    assert parse_mizrahi_html("<html><body><div>nothing</div></body></html>") == []


def test_scrape_fetches_catalog_page():
    with patch.object(mizrahi_scraper, "fetch_text", return_value=FIXTURE.read_text(encoding="utf-8")) as fetch:
        assert len(mizrahi_scraper.scrape()) == 4
    fetch.assert_called_once_with(SOURCE_URL)
