import json
from pathlib import Path

import dreamcard_giftcard_scraper as dreamcard_scraper
import wincard_giftcard_scraper

FIX = Path(__file__).parent / "fixtures"
WIN = json.loads((FIX / "wincard_giftcard" / "giftcardbrands.json").read_text(encoding="utf-8"))
DC = (FIX / "dreamcard_giftcard" / "brands.html").read_text(encoding="utf-8")


def test_wincard_brands():
    records = wincard_giftcard_scraper.parse(WIN)
    assert len(records) == 3
    assert records[0]["business_name"] == "הסטוק | Hastock"
    assert records[1]["business_name"] == "פוקס הום – FOX HOME"
    assert records[0]["discount_type"] == "gift_card"
    assert len(wincard_giftcard_scraper.scrape(lambda url: json.dumps(WIN))) == 3


def test_dreamcard_brands_skip_menu_icon():
    records = dreamcard_scraper.parse(DC)
    assert [r["business_name"] for r in records] == ["FOX", "FOX home", "AMERICAN EAGLE"]
    assert records[0]["discount_url"] == "https://www.dreamcard.co.il/stores/FOX_stores"
    assert "קז'ואל" in records[0]["limitations"]
