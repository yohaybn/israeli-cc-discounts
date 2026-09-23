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
