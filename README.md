# Discount Finder

All your Israeli credit-card discounts and club benefits in one place.

Discount Finder collects discount offers from Israeli credit-card clubs and loyalty programs, normalizes them into a single dataset, and serves them through a fast web UI and API - so you can search every benefit you are entitled to, across every club, in one search.

**See it live: https://yohaybn.github.io/israeli-cc-discounts/**

## What you get

- One searchable catalog of hundreds of offers across all supported clubs
- Filter by club, benefit type (`סוג ההטבה`), category, or physical stores near you
- A JSON API if you want to build on the data yourself

## Data sources

| Source | What it covers |
|---|---|
| MCC (`חבר`) | Club discounts |
| HOT | Member discounts |
| HTzone | Member discounts |
| HVR (hvr.co.il) | Rechargeable and gift card discounts |
| MAX gift cards | Gift-card offers |
| MAX benefits | The full MAX benefits catalog (cashback, vouchers, experiences) |
| BUYME | BUYME supplier discounts |
| Discount Key (מפתח דיסקונט) | Discount Bank participating businesses |
| American Express Israel | The Amex rewards catalog |

| Mizrahi-Tefahot (הכרטיס) | Mizrahi-Tefahot customer club benefits |
| Gifta (גיפטא) | Stores that accept the Gifta gift card |
| Gold Card (גולד קארד) | Stores that accept the Gold Card gift card |
| Raayonit Global Tav (גלובל תו) | Chains and businesses that accept the Global Tav voucher |
| Yedioth Ahronoth subscribers (ידיעות אחרונות) | Subscriber benefits |
| Azrieli gift card (עזריאלי גיפטקארד) | Stores in Azrieli malls that accept the Azrieli gift card |
| Swish gift cards (נופשונית) | Businesses that accept Swish Plus, Perfect, Premium, Unique and Baby |
| IMA Yahad club (מועדון יחד - ההסתדרות הרפואית) | Suppliers in the Israel Medical Association Yahad club |
| Shufersal 4U (שופרסל 4U) | Vouchers and benefits in the Shufersal 4U credit-card club |
| MY OFER (קניוני עופר) | Club deals in the Ofer malls, merged across malls |
Every source is public data - no login required. New sources are added over time; each one is documented below.

## Quickstart

1. Create and activate the virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the scraper to regenerate the canonical data under `data/` and publish the HTML-facing files under `docs/data/` (this backfills `discount_type` = `billing_discount` when missing):

```bash
.venv/bin/python main.py
```

4. Start the API server:

```bash
.venv/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

5. Run smoke tests (ensure API is running):

```bash
.venv/bin/python tests/smoke_test.py
```

## The web UI

Open `docs/index.html` or the running API root at `http://127.0.0.1:8000`. The toolbar includes a `סוג ההטבה` selector to filter by `discount_type`.

## The data schema

Every offer is normalized to the same shape: `club`, `business_name`, `discount`, `discount_url`, `discount_type` (`billing_discount`, `rechargeable_card`, `voucher`, `gift_card`, `club_card`), `discount_value` (numeric percent when parseable), `has_physical_store`, `branches`, `limitations`, and optional `category`. Fields `discount_type` and `discount_value` were added on 2026-09-02.

## Contributing

Contributions are welcome - new sources, better normalization, UI improvements.

- Working with an AI coding agent? Point it at [`AGENTS.md`](AGENTS.md) - it has the repo conventions, the shared schema, and the checklist for adding a scraper.
- Adding a source by hand? Follow any existing `*_scraper.py`: a `scrape_<name>()` entry point, last-good-data behavior in `main.py`, raw capture in `save_raw_scrapers.py`, offline fixtures + tests, and a section in this README.
- Please open one PR per change and leave it open for manual review.

## Source notes

### MAX Benefits

`max_benefits_scraper.py` reads the public MAX benefits catalog API (`/api/benefits/getLobby` + paged `/api/benefits/getCategoriesLobby` per category) and normalizes each benefit into the shared schema: club `MAX`, discount text from the catalog subtitle, official benefit URL, terms in `limitations`, and `billing_discount` type for cashback offers (otherwise `voucher`). Out-of-stock and date-expired benefits are skipped. A failed or empty refresh keeps the last successful `data/discounts/max_benefits_discounts.json` file. Save the raw lobby payload for debugging with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers max_benefits
```

### Discount Key

`discount_key_scraper.py` reads Discount Bank's public participating-business page and normalizes each percentage offer into the shared schema. A failed or empty refresh keeps the last successful `data/discounts/discount_key_discounts.json` file. Save the source page for debugging with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers discount_key
```

### American Express

`amex_scraper.py` reads the public American Express Israel benefits site (https://rewards.americanexpress.co.il/) and normalizes each benefit into the shared schema. The homepage embeds the full benefit catalog as server-rendered JSON (`window.epi`), so no login is required. Out-of-stock benefits are skipped, and regular/premium point pricing is kept in `limitations`. A failed or empty refresh keeps the last successful `data/discounts/amex_discounts.json` file. Save the source page for debugging with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers amex
```

### Mizrahi-Tefahot

`mizrahi_scraper.py` reads the public catalog of Mizrahi-Tefahot's customer club "הכרטיס" (https://www.mizrahi-tefahot.co.il/hacartis/all/). The page is server-rendered HTML, one card per benefit, no login. Hot deals (coupon codes) and fixed discounts are both kept; the category comes from the benefit URL. A failed or empty refresh keeps the last successful `data/discounts/mizrahi_discounts.json`. Save the source page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers mizrahi
```

### Gifta

`gifta_scraper.py` reads the store list of the Gifta (גיפטא) gift card from the site's public WordPress REST API (`https://gifta.co.il/wp-json/wp/v2/posts`) - each post is one participating store, its excerpt holds the branch addresses (kept in `limitations`). No login. A failed or empty refresh keeps the last successful `data/discounts/gifta_discounts.json`. Save the raw API payloads with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers gifta
```

### Gold Card

`goldcard_scraper.py` reads the store list of the Gold Card (גולד קארד) gift card from the site's public WordPress REST API (`https://goldcard-gift.com/wp-json/wp/v2/brands`, plus the `brand-categories` and `cities-category` taxonomies). Cities where the store operates are kept in `limitations`. No login. A failed or empty refresh keeps the last successful `data/discounts/goldcard_discounts.json`. Save the raw API payloads with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers goldcard
```

### Raayonit Global Tav

`raayonit_scraper.py` reads the public page of Raayonit's "Global Tav" (גלובל תו) voucher (https://www.raayonit.co.il/club/?ClubNum=18&ClubVoucherTypeNum=47). It keeps both the chain tiles (one record per network, linked to the network page) and the individual businesses from the supplier grid, merging the branches of one business into a single record with addresses and phones in `limitations`. No login. A failed or empty refresh keeps the last successful `data/discounts/raayonit_global_discounts.json`. Save the source page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers raayonit_global
```

### Yedioth Ahronoth

`yedioth_scraper.py` reads the benefit tiles on the public Yedioth Ahronoth subscribers site (https://www.yedioth.co.il/) - mostly discounted tickets and products for subscribers. Server-rendered HTML, no login. A failed or empty refresh keeps the last successful `data/discounts/yedioth_discounts.json`. Save the source page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers yedioth
```

### Azrieli gift card

`azrieli_giftcard_scraper.py` lists the stores that accept the Azrieli malls gift card. The card is run by BUYME and https://www.azrielimalls.co.il/giftcard links its "בתי עסק מכבדים" list to BUYME brand 398383, so the module reuses the BUYME options fetcher (public, no login) and relabels the records as their own club. The card works only in branches inside Azrieli malls. A failed or empty refresh keeps the last successful `data/discounts/azrieli_giftcard_discounts.json`. Save the raw payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers azrieli_giftcard
```

### Swish gift cards

`swish_scraper.py` lists the businesses that accept the multi-brand Swish gift cards that Fid lists as clubs: Swish Plus, Perfect, Premium, Unique and Baby. Each card's `club` field is the card name. Each public product page (no login) embeds the full "איפה נהנים מהמתנה" list in its Next.js server-components payload (`tagsChains` -> `chainsByWallet`). The scraper decodes that payload for each card; one failing card does not drop the others. Chains in the "רכישה אונליין" category are marked online-only. A failed or empty refresh keeps the last successful `data/discounts/swish_discounts.json`. Save the raw pages with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers swish
```

### IMA Yahad club

`ima_yahad_scraper.py` reads the public catalog of the Israel Medical Association "Yahad" club (https://www.ima.org.il/yahadclub/Categories.aspx, no login). It walks every category page, collects the supplier IDs, then reads each SupplierDetails page for the discount, description and branch table (address, city, phone). The site is slow: about 160 category pages and 800 supplier pages, fetched one at a time, so a full run takes a while. Pages that time out are skipped with a warning. A failed or empty refresh keeps the last successful `data/discounts/ima_yahad_discounts.json`. Save the category page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers ima_yahad
```

### Shufersal 4U

`shufersal4u_scraper.py` reads the public benefit catalog of the Shufersal 4U credit-card club (https://www.shufersal4u.co.il/). Browsing needs no login (login is only for buying). It walks the category pages linked from the home page and their sub-categories, keeps one record per benefit uuid, and computes `discount_value` from the "לרכישה ב-X בשווי/במקום Y" price line or an "X% הנחה" text. A failed or empty refresh keeps the last successful `data/discounts/shufersal4u_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers shufersal4u
```

### MY OFER

`myofer_scraper.py` reads MY OFER, the Ofer malls customer club. The mall list comes from the home page and each mall's public deals page (`https://myofer.co.il/malls/<mall>/deals?page=N`, no login) holds 10 deals per page in its Next.js `__NEXT_DATA__`. Deals that repeat across malls are merged and list every mall in `branches`. `discount_value` comes from "ב-X בשווי/במקום Y" price lines or a percent. A full run is about 240 page loads. A failed or empty refresh keeps the last successful `data/discounts/myofer_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers myofer
```
