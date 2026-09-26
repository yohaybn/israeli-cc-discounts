# Agent Instructions

Guidance for AI agents (and humans) working in this repository. Read this before making changes.

## What this project is

Discount Finder aggregates discount and benefit offers from Israeli credit-card clubs and loyalty programs into one normalized dataset, served by a small FastAPI backend and a static web UI published from `docs/` via GitHub Pages.

Pipeline: source scrapers (`scrapers/`) -> `main.py` (normalize, dedupe, merge) -> `data/discounts/*.json` + `docs/data/*.json` -> `scripts/join_businesses.py` (business matching) -> `api_server.py` / `docs/index.html`.

## Repository layout

- `main.py` - entry point: runs all scrapers, normalizes, dedupes, writes `data/discounts/` and `docs/data/`, keeps per-source metadata. Run from the repo root: `python main.py`.
- `scrapers/` - all source scrapers and their shared helpers:
  - `*_scraper.py` - one module per source (MCC, HOT, HTzone, HVR, MAX, BUYME, Discount Key, American Express, and many more).
  - `*_platform.py` - shared crawl logic for families of look-alike club sites (`style_platform.py`, `htzone_platform.py`, `uniq_platform.py`, `dolcemaster_platform.py`).
  - `scraper_utils.py` - shared fetch/normalize helpers.
  - `wp_catalog.py` - shared WordPress REST collection client.
  - `extra_sources.py` - registry of the extra sources `main.py` runs; adding a source is one line in `EXTRA_SOURCE_MODULES`.
  - Modules import each other by bare name (`from scraper_utils import fetch_text`); `main.py`, `scripts/save_raw_scrapers.py` and the root `conftest.py` put `scrapers/` on `sys.path`, so imports just work. There is no package and no `__init__.py` on purpose - each scraper also runs standalone: `python scrapers/<name>_scraper.py`.
- `api_server.py` - FastAPI service over the generated data; `run_api.sh` starts it.
- `scripts/join_businesses.py` - joins discounts with the business/branch dataset (Near Me). Owner-run only (see below).
- `scripts/build_static_shards.py` - publishes the lightweight business index and detail shards, plus geographic cells for the static map. `main.py` builds the discounts index after a successful scrape; `join_businesses.py` rebuilds the map cells. To initialize after merging frontend changes without waiting for the next scrape, run `python scripts/build_static_shards.py` on the owner server from the repository root with current `docs/data/*.json`, then `git add docs/data/business_index.json docs/data/benefit_hashes-*.json docs/data/discount_shards/ docs/data/nearby_index.json docs/data/nearby_shards/ && git commit -m "Build static search and map indexes" && git push origin main`. This creates the indexes and hashed shards without rerunning any scrapers. Confirm the counts printed by the builder match the legacy inputs before committing. Existing browsers use the old data until the generated files are published; the main list falls back to legacy JSON when the index is not yet available, but Near Me reports a loading error until the geographic index lands. Generated files do not belong in agent PRs.
- `scripts/build_templates.py` - renders `templates/` into the static pages under `docs/`.
- `scripts/save_raw_scrapers.py` - saves raw source payloads under `data/raw/` for debugging (`--scrapers <name>` or `--all`).
- `docs/` - static frontend (GitHub Pages). Data files it loads live in `docs/data/`; do not move them - the Pages site and `scripts/join_businesses.py` depend on those exact paths.
- `templates/` - source templates for the static pages; edit here, then run `scripts/build_templates.py`.
- `tests/` - pytest suite with fixtures under `tests/fixtures/`, plus plain-node frontend tests (`tests/*.js`); `tests/smoke_test.py` needs a running API.
- `conftest.py` - repo-root pytest bootstrap that puts the repo root and `scrapers/` on `sys.path`.
- `run_daily.sh`, `scrape_and_sync.sh` - the owner's cron wrappers (see "Daily cron flow"). Not for use in development.

## Running things

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python main.py                      # full scrape run: data/discounts/ + docs/data/
python scrapers/amex_scraper.py     # one scraper, standalone (live network)
python scripts/save_raw_scrapers.py --scrapers amex   # capture raw payloads to data/raw/
python -m pytest -q tests/          # unit tests (fully offline)
node tests/test_share_link.js       # one frontend test (repeat per tests/*.js)
python scripts/build_templates.py   # rebuild docs/ pages from templates/
```

## The shared schema

Every scraper returns a list of dicts with these fields:

| Field | Type | Notes |
|---|---|---|
| `club` | string | Club/program name as shown to users (e.g. `MAX`, `מפתח דיסקונט`) |
| `business_name` | string | Business or offer title |
| `discount` | string | Human-readable discount text (plain text, no HTML) |
| `discount_url` | string | Canonical link to the offer |
| `discount_type` | enum | `billing_discount`, `rechargeable_card`, `voucher`, `gift_card`, `club_card` |
| `discount_value` | number \| null | Percent value when the discount is a parseable percent |
| `has_physical_store` | bool | `false` for online-only offers |
| `branches` | list | Branch objects when known, otherwise `[]` |
| `limitations` | string | Terms and conditions, plain text |
| `category` | string | Optional source category |

## Adding or changing a scraper

Conventions every source follows (see `scrapers/amex_scraper.py` or `scrapers/max_benefits_scraper.py` for a recent example):

1. Create `scrapers/<name>_scraper.py` with one `scrape()` entry point returning normalized records, plus `SOURCE_KEY`, `CLUB_NAME` and `fetch_raw()`; keep fetch, extract and normalize as separate functions so each is testable. Reuse a `*_platform.py` helper if the site is a known platform family.
2. Register it in `scrapers/extra_sources.py` (`EXTRA_SOURCE_MODULES`, one line). `main.py` then runs it, writes `data/discounts/<SOURCE_KEY>_discounts.json` only on a non-empty result, records the outcome with `mark_source(...)`, and on failure falls back to the previous file (last-good-data behavior). `mark_source` keeps the real `last_successful_scrape` on failure and marks the source `stale`, so the site shows true per-club dates. Never delete or empty an existing data file because one run failed. The core sources (MCC, HOT, HTzone, HVR, MAX, BUYME, Discount Key, Amex) are wired directly in `main.py` instead.
3. Add a `save_<name>_raw()` function to `scripts/save_raw_scrapers.py` and register it in the `--all` list, the `--scrapers` help text and the dispatch block.
4. Add real (trimmed) fixtures under `tests/fixtures/` and pytest tests that run fully offline: normalization, dedupe, edge cases (expired/out-of-stock/malformed), and a mocked network walk. Live-network checks are manual, not part of the test suite.
5. Document the source in `README.md` (one section per source, including the raw-capture command).

## Daily cron flow (owner's server)

The owner's server runs the data refresh from a checkout at `/home/ubuntu/discount-finder`:

- `run_daily.sh` (cron) runs `.venv/bin/python main.py`, then `scripts/join_businesses.py`, commits any changed data files (`data/`, `docs/data/`) and pushes to `main`.
- `scrape_and_sync.sh` is the older variant (also runs `fetch_osm_data.py`).
- A GitHub Actions workflow (`.github/workflows/daily_fetch.yml`) runs `fetch_osm_data.py` nightly to refresh `docs/data/businesses/*.json`.

Entry points (`main.py`, `api_server.py`, `fetch_osm_data.py`) and `scripts/join_businesses.py` stay at fixed paths on purpose - do not move them, and do not repoint the cron wrappers at your own environment. If entry-point paths ever change, the server checkout needs a manual `git pull --rebase` after the merge.

## Hard rules

- Public data only. Never bypass logins, OTP, CAPTCHAs, Cloudflare or any other access control. If a source starts blocking, stop and report - do not work around it.
- Never commit generated data: no `data/` or `docs/data/` changes from local runs in a PR (`data/` is git-ignored; `docs/data/` is owner-generated). Data regeneration and `scripts/join_businesses.py` are run by the repo owner on request, not as part of code PRs.
- One concern per PR, based on the latest `main`. Leave PRs open for the owner's manual review; do not merge or enable auto-merge.
- Do not modify the cron wrappers (`run_daily.sh`, `scrape_and_sync.sh`) to point at your environment; they contain the owner's server paths.

## Checks before opening a PR

```bash
python -m pytest -q tests/            # unit tests (offline)
for t in tests/*.js; do node "$t"; done   # frontend tests
python -m compileall -q <changed .py files>
git diff --check                      # whitespace/errors
```

Then run one live scrape of the changed source (`python scrapers/<name>_scraper.py`) and confirm the normalized record count looks sane. Note the count in the PR description.

The whole suite should pass on a clean checkout. Tests that read generated data (`data/discounts/`) skip when it is missing; the dedupe check falls back to the committed `docs/data/all_combined_discounts.json`.
