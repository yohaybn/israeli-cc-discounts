"""Pytest bootstrap: make the repo root and the scrapers/ directory importable.

Scraper modules live under scrapers/ and import each other by bare module name
(e.g. ``from scraper_utils import fetch_text``), so scrapers/ must be on
sys.path for the test suite. The repo root stays on sys.path so tests can
import ``main`` and ``scripts.*``.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRAPERS_DIR = os.path.join(REPO_ROOT, "scrapers")

for _path in (REPO_ROOT, SCRAPERS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)
