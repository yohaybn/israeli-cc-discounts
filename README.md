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
| DREAM CARD VIP (דרים קארד) | Fox group brands with 15% cashback on the DREAM CARD VIP card |
| כח לעובדים (workers.style.co.il) | Benefits in the כח לעובדים club |
| עדיף (adif.style.co.il) | Benefits in the עדיף consumer club |
| Hi-Benefit (לשכת רואי החשבון) | Benefits for Hi-Benefit card holders (Institute of CPAs) |
| אגד דרייבר (Egged club) | Benefits in the Egged Driver club |
| לשכת סוכני הביטוח | Benefits for Israel Insurance Agents Association members |
| קרנות השוטרים / הסוהרים | Consumer club of the police and prison-service funds |
| להב (לשכת העצמאים) | Benefits for Lahav (self-employed association) members |
| לייף סטייל | Benefits in the Lifestyle club |
| מועדון המתנדבים | Benefits in the volunteers club |
| צעיר (Tzair card) | Benefits for Tzair card holders |
| מצר | HTzone white-label club site (metzer.htzone.co.il), merchant benefits and vouchers |
| גולד צפון | HTzone white-label club site (goldnorth.htzone.co.il) |
| תעשייה אווירית (ICARD) | style platform club site (icard.style.co.il) |
| יותר | Soldiers' club business list (yoter.co.il), billing discounts |
| אמדוקס | style platform club site (https://amdocs.style.co.il/) |
| קמפוסכרט | style platform club site (https://campus.style.co.il/) |
| PowerCard | style platform club site (https://powercard.style.co.il/) |
| קורפורייט (CORPORATE) | style platform club site (https://www.mycorporate.co.il/) |
| שחר | Engineers' union club public benefits page (m-shachar.org.il) |
| Living | style platform club site (https://www.livingclub.co.il/) |
| רמי לוי המועדון | style platform club site (https://rmrm.style.co.il/) |
| אותי - עמותה ישראלית לאוטיזם | style platform club site (https://oti.style.co.il/) |
| Cashdo | Cashback club store list (cashdo.co.il paging.json) |
| Mami - מאמי | Coupon club brand list and campaigns (hi-mami.com) |
| קניוני עזריאלי | Mall coupons page (azrielimalls.co.il/coupons) |
| uniq | uniq-club platform GraphQL (shop 1) |
| אוניברסיטת תל אביב TAU | uniq-club platform GraphQL (shop 2) |
| סטודנט גרופ | Student coupon club (studentgroup.co.il WP REST) |
| חתול פיננסי | Community benefits (moneyplan.co.il WP REST) |
| Samsung Members | Samsung Israel Members / Galaxy VIP benefits page |
| קופונופש | Leisure/tickets club (cpnclub.co.il public API) |
| איחוד הצלה | Volunteer benefits club (4u.1221.org.il WooCommerce Store API) |
| טוב פלוס | State employees' club טוב+ (tovplus.org.il category pages) |
| מחסני השוק גיפטקארד Wincard | Brands accepting the WINcard gift card (m-shuk.net WP REST) |
| DREAM CARD גיפט | Chains accepting the DREAM CARD gift card (dcgift.co.il) |
| מועדון W | W (דאבל יו) card benefits page (w-card.co.il) |
| LOVE gift card | Brands accepting the LOVE CARD (Castro-Hoodies terms page) |
| Just4u / NEW CARD | Gift vouchers and partner businesses (public app API) |
| WinCard+ מחסני השוק | Credit-card benefits (public page) |
| FLY CARD אל על | Card benefits (public Isracard page) |
| רשף - גמלאי כבאות | Association partner benefits (public page) |
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

### DREAM CARD VIP

`dreamcard_scraper.py` covers the DREAM CARD VIP club (Fox group brands), whose credit card gives 15% cashback in every club brand (https://www.dreamcard.co.il/dreamcard-vip/). The club web app has two public API calls that need no login: `Brands/GetBrands` and `Branches/GetBranchesData`. The scraper emits one record per active brand with its store branches (a store listed as "FOX / FOX HOME" counts for both). A failed or empty refresh keeps the last successful `data/discounts/dreamcard_discounts.json`. Save the raw API payloads with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers dreamcard
```

### כח לעובדים

`workers_style_scraper.py` reads the public benefit catalog at https://workers.style.co.il/. The site runs on the same "style" benefits platform as Shufersal 4U, so the crawl lives in the shared `style_platform.py`: it walks the category pages and their sub-categories, keeps one record per benefit uuid and computes `discount_value` from the price line. Browsing needs no login (login is only for buying). A failed or empty refresh keeps the last successful `data/discounts/koach_laovdim_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers koach_laovdim
```

### עדיף

`adif_scraper.py` reads the public benefit catalog at https://adif.style.co.il/. The site runs on the same "style" benefits platform as Shufersal 4U, so the crawl lives in the shared `style_platform.py`: it walks the category pages and their sub-categories, keeps one record per benefit uuid and computes `discount_value` from the price line. Browsing needs no login (login is only for buying). A failed or empty refresh keeps the last successful `data/discounts/adif_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers adif
```

### Hi-Benefit

`hibenefit_scraper.py` reads the public benefit catalog at https://www.benefit-icpas.co.il/. The site runs on the same "style" benefits platform as Shufersal 4U, so the crawl lives in the shared `style_platform.py`: it walks the category pages and their sub-categories, keeps one record per benefit uuid and computes `discount_value` from the price line. Browsing needs no login (login is only for buying). A failed or empty refresh keeps the last successful `data/discounts/hibenefit_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers hibenefit
```

### אגד דרייבר

`egged_driver_scraper.py` reads the public benefit catalog at https://www.eggedclub.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/egged_driver_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers egged_driver
```

### לשכת סוכני הביטוח

`insurance_agents_scraper.py` reads the public benefit catalog at https://insurance.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/insurance_agents_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers insurance_agents
```

### קרנות השוטרים / קרנות הסוהרים

`police_funds_scraper.py` reads the public benefit catalog at https://ks.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/police_funds_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers police_funds
```

### להב - לשכת העצמאים

`lahav_scraper.py` reads the public benefit catalog at https://lahav.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/lahav_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers lahav
```

### לייף סטייל

`lifestyle_club_scraper.py` reads the public benefit catalog at https://lifestyle.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/lifestyle_club_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers lifestyle_club
```

### מועדון המתנדבים

`volunteers_club_scraper.py` reads the public benefit catalog at https://mitnadvim4u.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/volunteers_club_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers volunteers_club
```

### צעיר

`tzair_scraper.py` reads the public benefit catalog at https://young.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/tzair_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers tzair
```

### מצר

`metzer_scraper.py` reads the public benefit catalog at https://metzer.htzone.co.il/ (no login; login is only for buying). The site runs on the HTzone white-label platform: the crawl is `htzone_platform.crawl`, which opens every category page and loads its item blocks through the public `/ajax` call (`act=category_items`) with the page token. Shop products sold on the site (furniture, appliances) are skipped; only merchant benefits and attraction vouchers are kept. A failed or empty refresh keeps the last successful `data/discounts/metzer_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers metzer
```

### גולד צפון

`goldnorth_scraper.py` reads the public benefit catalog at https://goldnorth.htzone.co.il/ (no login; login is only for buying). The site runs on the HTzone white-label platform, so the crawl is `htzone_platform.crawl` (see מצר above). A failed or empty refresh keeps the last successful `data/discounts/goldnorth_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers goldnorth
```

### תעשייה אווירית (ICARD)

`icard_scraper.py` reads the public benefit catalog at https://icard.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/icard_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers icard
```

### יותר

`yoter_scraper.py` reads the public business list of מועדון יותר (the soldiers' club of האגודה למען החייל) at https://yoter.co.il/רשימת-בתי-עסק/ (no login). Each `a.logo-item` tile gives the business name, the benefit line, the discount badge and its category. A failed or empty refresh keeps the last successful `data/discounts/yoter_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers yoter
```

### אמדוקס

`amdocs_scraper.py` reads the public benefit catalog at https://amdocs.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/amdocs_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers amdocs
```

### קמפוסכרט

`campus_card_scraper.py` reads the public benefit catalog at https://campus.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/campus_card_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers campus_card
```

### PowerCard

`powercard_scraper.py` reads the public benefit catalog at https://powercard.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/powercard_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers powercard
```

### קורפורייט (CORPORATE)

`corporate_scraper.py` reads the public benefit catalog at https://www.mycorporate.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). Its tiles give business names only, without a benefit line, so `discount` repeats the name. A failed or empty refresh keeps the last successful `data/discounts/corporate_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers corporate
```

### שחר

`shachar_scraper.py` reads the public benefits page of שחר (the club of הסתדרות המהנדסים) at https://www.m-shachar.org.il/benefit/ (no login). Each `a.stand_item` tile gives the title and a summary line. The club's larger catalog is on a Megalean site that needs login, so only the public page is covered. A failed or empty refresh keeps the last successful `data/discounts/shachar_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers shachar
```

### Living

`living_scraper.py` reads the public benefit catalog at https://www.livingclub.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/living_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers living
```

### רמי לוי המועדון

`rami_levy_club_scraper.py` reads the public benefit catalog at https://rmrm.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/rami_levy_club_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers rami_levy_club
```

### אותי - עמותה ישראלית לאוטיזם

`oti_scraper.py` reads the public benefit catalog at https://oti.style.co.il/ (no login; login is only for buying). The site runs on the shared "style" benefits platform, so the crawl is `style_platform.crawl` (see כח לעובדים above). A failed or empty refresh keeps the last successful `data/discounts/oti_discounts.json`. Save the home page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers oti
```

### Cashdo

`cashdo_scraper.py` reads the public store list of Cashdo, a cashback club for online stores, from `https://cashdo.co.il/paging.json` (the endpoint behind https://cashdo.co.il/all-stores; no login). Each tile gives the store name, its page and the cashback line. Cashback is credited after the purchase, so records use `billing_discount` and are online-only. A failed or empty refresh keeps the last successful `data/discounts/cashdo_discounts.json`. Save the payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers cashdo
```

### Mami - מאמי

`mami_scraper.py` reads the public, server-rendered pages of Mami - מאמי at https://www.hi-mami.com/ (no login): the brand list at `/brands` (standing benefit per brand) and the current campaign tiles on each `/categories/<slug>` page linked from the home page (time-limited deals). A failed or empty refresh keeps the last successful `data/discounts/mami_discounts.json`. Save the home and brand pages with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers mami
```

### קניוני עזריאלי

`azrieli_malls_scraper.py` reads the public coupons page of קניוני עזריאלי at https://www.azrielimalls.co.il/coupons (server-rendered, no login). Each coupon card gives the store, the deal, the participating mall and the validity date. The same deal repeats per mall, so cards are grouped by store and deal and the malls are listed in `limitations`. The page is large (~30MB). A failed or empty refresh keeps the last successful `data/discounts/azrieli_malls_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers azrieli_malls
```

### uniq

`uniq_scraper.py` reads the benefits of uniq (https://www.uniq-club.co.il/) from the public GraphQL endpoint of the uniq-club platform (`https://admin.uniq-club.co.il/api/graphql`, query `getBenefits` with `shopId` 1; no login). The shared client is `uniq_platform.py`. A failed or empty refresh keeps the last successful `data/discounts/uniq_discounts.json`. Save the payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers uniq
```

### אוניברסיטת תל אביב TAU

`tau_club_scraper.py` reads the benefits of the Tel Aviv University club (https://www.tauclub.co.il/) from the same public GraphQL endpoint as uniq (`shopId` 2; see uniq above). A failed or empty refresh keeps the last successful `data/discounts/tau_club_discounts.json`. Save the payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers tau_club
```

### סטודנט גרופ

`studentgroup_scraper.py` reads the coupons of סטודנט גרופ from the public WordPress REST API (`https://studentgroup.co.il/wp-json/wp/v2/product`, no login). The benefit line comes from each coupon's SEO title. A failed or empty refresh keeps the last successful `data/discounts/studentgroup_discounts.json`. Save the first page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers studentgroup
```

### חתול פיננסי

`moneyplan_scraper.py` reads the benefits of חתול פיננסי from the public WordPress REST API (`https://moneyplan.co.il/wp-json/wp/v2/benefits`, no login). The benefit line is each post's SEO description. A failed or empty refresh keeps the last successful `data/discounts/moneyplan_discounts.json`. Save the payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers moneyplan
```

### Samsung Members

`samsung_members_scraper.py` reads the public Samsung Members / Galaxy VIP benefits page (`https://www.samsung.com/il/mobile/samsung-members/benefits/`, no login). Each carousel card is one benefit. A failed or empty refresh keeps the last successful `data/discounts/samsung_members_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers samsung_members
```

### קופונופש

`cpnclub_scraper.py` reads the leisure suppliers of קופונופש from the site's public back-end search (`https://be.cpnclub.co.il/api/v2/search/club`, paged, no login). `info.discount` gives the headline percent when published. A failed or empty refresh keeps the last successful `data/discounts/cpnclub_discounts.json`. Save the first page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers cpnclub
```

### איחוד הצלה

`ihud_hatzala_scraper.py` reads the volunteer benefits of איחוד הצלה from the public WooCommerce Store API of the club site (`https://4u.1221.org.il/wp-json/wc/store/v1/products`, no login). The benefit line is the first line of the short description that names a discount, price or gift. A failed or empty refresh keeps the last successful `data/discounts/ihud_hatzala_discounts.json`. Save the first page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers ihud_hatzala
```

### טוב פלוס

`tovplus_scraper.py` reads טוב+ (the state employees' club) through the shared `dolcemaster_platform.py`. Public category pages (`https://tovplus.org.il/category/<id>`, no login) embed their products with club and market prices in `window.__PRELOADED_STATE__`; the crawl walks the category tree and dedupes by product ID. The home page sits behind a bot check, so the crawl starts from a category page. A failed or empty refresh keeps the last successful `data/discounts/tovplus_discounts.json`. Save one category page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers tovplus
```

### מחסני השוק גיפטקארד Wincard

`wincard_giftcard_scraper.py` lists the brands that accept the מחסני השוק WINcard gift card, from the public WordPress REST collection `https://m-shuk.net/wp-json/wp/v2/giftcardbrands` (no login). A failed or empty refresh keeps the last successful `data/discounts/wincard_giftcard_discounts.json`. Save the payload with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers wincard_giftcard
```

### DREAM CARD גיפט

`dreamcard_giftcard_scraper.py` lists the FOX-group chains that accept the DREAM CARD gift card (a separate product from the DREAM CARD VIP club in `dreamcard_scraper.py`), from the public page `https://www.dcgift.co.il/brands` (no login). A failed or empty refresh keeps the last successful `data/discounts/dreamcard_giftcard_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers dreamcard_giftcard
```

### מועדון W

`w_card_scraper.py` reads the card benefits of מועדון W (the "דאבל יו" card of GOLF and Steimatzky) from the public page `https://w-card.co.il/` (no login). A failed or empty refresh keeps the last successful `data/discounts/w_card_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers w_card
```

### LOVE gift card

`love_card_scraper.py` lists the Castro-Hoodies group brands that accept the LOVE CARD gift card, taken from the brand clause in the card's public terms page (`https://www.hoodies.co.il/tqnvn-love-card`, no login). A failed or empty refresh keeps the last successful `data/discounts/love_card_discounts.json`. Save the page with:

```bash
.venv/bin/python save_raw_scrapers.py --scrapers love_card
```

### Just4u / NEW CARD

Public JSON endpoint the Angular app itself calls (`/api/newapi/getHomepageItems`, no login). Lists NEW CARD / Just4u voucher items with face price and featured partner businesses.

```bash
.venv/bin/python save_raw_scrapers.py --scrapers just4u
```

### WinCard+ מחסני השוק

Public card page, Elementor icon boxes with the WinCard+ card benefits.

```bash
.venv/bin/python save_raw_scrapers.py --scrapers wincard_plus
```

### FLY CARD אל על

Public Isracard FLY CARD page (Wix repeater of card benefits). El Al own pages load via an API behind a Reblaze challenge, so they are not used.

```bash
.venv/bin/python save_raw_scrapers.py --scrapers flycard
```

### רשף - גמלאי כבאות והצלה

Public WordPress/Elementor benefits page of the retired firefighters association: partner tiles (figure + figcaption). Tiles pointing to other clubs are labelled club_card.

```bash
.venv/bin/python save_raw_scrapers.py --scrapers reshef
```
