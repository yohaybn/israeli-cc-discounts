"""Registry of additional scrapers run by main.py with last-good-data fallback.

Each entry names a module that exposes:

* ``SOURCE_KEY`` - metadata key and data file stem (``data/discounts/<key>_discounts.json``)
* ``CLUB_NAME`` - label used in log lines
* ``scrape()`` - returns records in the shared schema (see AGENTS.md)
* ``fetch_raw()`` - returns ``{filename: text}`` of the raw source payloads

Adding a source is one line here plus the module, fixtures and tests.
"""

import importlib

EXTRA_SOURCE_MODULES: list[str] = [
    "tau_club_scraper",
    "uniq_scraper",
    "azrieli_malls_scraper",
    "mami_scraper",
    "cashdo_scraper",
    "oti_scraper",
    "rami_levy_club_scraper",
    "living_scraper",
    "shachar_scraper",
    "corporate_scraper",
    "powercard_scraper",
    "campus_card_scraper",
    "amdocs_scraper",
    "yoter_scraper",
    "icard_scraper",
    "goldnorth_scraper",
    "metzer_scraper",
    "tzair_scraper",
    "volunteers_club_scraper",
    "lifestyle_club_scraper",
    "lahav_scraper",
    "police_funds_scraper",
    "insurance_agents_scraper",
    "egged_driver_scraper",
    "hibenefit_scraper",
    "adif_scraper",
    "workers_style_scraper",
    "dreamcard_scraper",
    "myofer_scraper",
    "shufersal4u_scraper",
    "ima_yahad_scraper",
    "swish_scraper",
    "azrieli_giftcard_scraper",
    "yedioth_scraper",
    "raayonit_scraper",
    "goldcard_scraper",
    "gifta_scraper",
    "mizrahi_scraper",
]


def load_extra_sources():
    """Import every registered source module, skipping ones that fail to import."""
    modules = []
    for name in EXTRA_SOURCE_MODULES:
        try:
            modules.append(importlib.import_module(name))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[WARNING] Could not import source module {name}: {exc}")
    return modules
