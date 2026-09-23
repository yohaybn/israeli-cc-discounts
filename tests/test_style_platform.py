from pathlib import Path

import adif_scraper
import egged_driver_scraper
import insurance_agents_scraper
import police_funds_scraper
import lahav_scraper
import lifestyle_club_scraper
import volunteers_club_scraper
import tzair_scraper
import oti_scraper
import rami_levy_club_scraper
import living_scraper
import corporate_scraper
import powercard_scraper
import campus_card_scraper
import amdocs_scraper
import icard_scraper
import hibenefit_scraper
import style_platform
import workers_style_scraper

FIX = Path(__file__).parent / "fixtures"
HOME = (FIX / "style_platform" / "workers_home.html").read_text(encoding="utf-8")
CAT7 = (FIX / "style_platform" / "workers_category_7.html").read_text(encoding="utf-8")
BOX_ITEM_CAT = (FIX / "shufersal4u" / "category_7.html").read_text(encoding="utf-8")
BASE = "https://workers.style.co.il/"


def test_category_links():
    links = style_platform.category_links(HOME)
    assert links["7"] == "מזון"
    assert len(links) >= 8


def test_parse_product_title_template():
    records = style_platform.parse_category(CAT7, BASE, "כח לעובדים", "מזון", "note")
    assert len(records) > 50
    first = records[0]
    assert first["club"] == "כח לעובדים"
    assert first["discount_url"].startswith(BASE + "?page=Benefit&uuid=")
    assert first["category"] == "מזון"
    assert first["limitations"] == "note"
    assert any(r["discount_value"] for r in records)


def test_parse_box_item_template():
    records = style_platform.parse_category(BOX_ITEM_CAT, "https://www.shufersal4u.co.il/", "x")
    assert len(records) > 20
    assert all(r["business_name"] for r in records)


def test_crawl_dedupes_and_skips_generic_category_label():
    def fake_fetch(url):
        if url == BASE:
            return HOME
        if url.endswith("id=7"):
            return CAT7
        return "<html></html>"

    records = style_platform.crawl(BASE, "כח לעובדים", fake_fetch)
    urls = [r["discount_url"] for r in records]
    assert len(urls) == len(set(urls))
    assert records


def test_thin_modules_use_their_base_url():
    for module in (workers_style_scraper, adif_scraper, hibenefit_scraper, egged_driver_scraper, insurance_agents_scraper, police_funds_scraper, lahav_scraper, lifestyle_club_scraper, volunteers_club_scraper, tzair_scraper, icard_scraper, oti_scraper, rami_levy_club_scraper, living_scraper, corporate_scraper, powercard_scraper, campus_card_scraper, amdocs_scraper):
        seen = []

        def fake_fetch(url, seen=seen):
            seen.append(url)
            return "<html></html>"

        assert module.scrape(fetch=fake_fetch) == []
        assert seen == [module.BASE_URL]


CORPORATE_CAT = (FIX / "style_platform" / "corporate_category_16.html").read_text(encoding="utf-8")
CORPORATE_BASE = "https://www.mycorporate.co.il/"


def test_corporate_card_tiles_are_card_discounts_not_vouchers():
    # Regression: קורפורייט benefits were all labeled "voucher" (שובר). Corporate is an Isracard
    # credit card; a "5% הנחה" tile is an automatic discount when paying with the club card.
    records = style_platform.parse_category(
        CORPORATE_CAT, CORPORATE_BASE, "קורפורייט", "לבית", default_type=corporate_scraper.DISCOUNT_TYPE
    )
    by_name = {r["business_name"]: r for r in records}
    assert len(records) == 59  # every tile of the card template is parsed, not only ones with img alt
    home_sale = by_name["הום סייל"]
    assert home_sale["discount_type"] == "billing_discount"
    card_tiles = [r for r in records if r["discount"].startswith(("5% הנחה", "10% הנחה"))]
    assert card_tiles
    assert all(r["discount_type"] == "billing_discount" for r in card_tiles)
    assert all(r["discount_value"] in (5.0, 10.0) for r in card_tiles)
    assert not any(r["discount"] == r["business_name"] for r in card_tiles)


def test_corporate_purchase_tiles_stay_vouchers():
    records = style_platform.parse_category(
        CORPORATE_CAT, CORPORATE_BASE, "קורפורייט", default_type=corporate_scraper.DISCOUNT_TYPE
    )
    vouchers = [r for r in records if r["discount_type"] == "voucher"]
    assert vouchers
    textile = next(r for r in records if r["business_name"] == "שובר לרשת ערד טקסטיל")
    assert textile["discount_type"] == "voucher"
    assert textile["discount_value"] == 15.0  # ב-₪85 בשווי ₪100


def test_corporate_scraper_crawls_as_billing_discount():
    def fake_fetch(url):
        if url == corporate_scraper.BASE_URL:
            return '<a href="?page=category&id=16">לבית</a>'
        return CORPORATE_CAT

    records = corporate_scraper.scrape(fetch=fake_fetch)
    types = {r["discount_type"] for r in records}
    assert types == {"billing_discount", "voucher"}


def test_other_style_clubs_keep_voucher_default():
    records = style_platform.parse_category(CAT7, BASE, "כח לעובדים", "מזון")
    assert records and all(r["discount_type"] == "voucher" for r in records)
    assert style_platform.tile_type("5% הנחה") == "voucher"
    assert style_platform.tile_type("5% הנחה", "billing_discount") == "billing_discount"
    assert style_platform.tile_type("לרכישה", "billing_discount") == "voucher"


def test_card_discount_percent_in_title_is_kept():
    html = (
        '<a class="card product" href="/?page=Benefit&uuid=ABC-1"><span class="product-title-bold">15% הנחה ב- AVIS</span>'
        '<span class="product-title-regular">חברת השכרת רכב</span><button class="add-button">לפרטים</button></a>'
    )
    [record] = style_platform.parse_category(html, CORPORATE_BASE, "קורפורייט", default_type="billing_discount")
    assert record["discount_type"] == "billing_discount"
    assert record["discount"] == "15% הנחה ב- AVIS - חברת השכרת רכב"
    assert record["discount_value"] == 15.0
