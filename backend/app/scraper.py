"""
Scraper for carsensor.net: collect make, model, year, price, color, link.
Upsert key: link. Retry logic for network errors.
"""
import re
import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.carsensor.net"
NEW_LISTINGS_URL = "https://www.carsensor.net/usedcar/index.html?NEW=1&SORT=19"
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 2


def _parse_price_yen(text: str) -> int | None:
    """Parse Japanese price like '739.8万円' to integer yen (7398000)."""
    if not text:
        return None
    m = re.search(r"([\d,.]+\s*)(万?)\s*円", text)
    if not m:
        return None
    num_str = m.group(1).replace(",", "").strip()
    try:
        val = float(num_str)
    except ValueError:
        return None
    if "万" in (m.group(2) or ""):
        val *= 10_000
    return int(val)


def _parse_year(text: str) -> int | None:
    """Parse year from text like '2025(R07)年' or '年式 2025'."""
    if not text:
        return None
    m = re.search(r"20\d{2}", text)
    return int(m.group(0)) if m else None


def _extract_make_model(title: str) -> tuple[str | None, str | None]:
    """From listing title get first token as make, rest as model (simplified)."""
    if not title or not title.strip():
        return None, None
    parts = title.strip().split()
    if not parts:
        return None, None
    make = parts[0]
    model = " ".join(parts[1:]) if len(parts) > 1 else None
    if model and len(model) > 200:
        model = model[:200] + "..."
    return make or None, model or None


def fetch_with_retry(client: httpx.Client, url: str) -> httpx.Response:
    """GET with basic retry on network errors."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            r = client.get(url, timeout=30.0, follow_redirects=True)
            r.raise_for_status()
            return r
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_error = e
            logger.warning("Attempt %s failed for %s: %s", attempt + 1, url, e)
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(RETRY_BACKOFF_SEC * (attempt + 1))
    raise last_error


def scrape_listing_page(html: str, base_url: str = BASE_URL) -> list[dict[str, Any]]:
    """
    Parse the new listings HTML and return list of dicts with
    make, model, year, price, color, link. Color may be None if not on listing.
    """
    soup = BeautifulSoup(html, "lxml")
    results = []

    # New listings: links to detail pages like /usedcar/detail/AU6854026490/index.html
    # Often in a list or section; we look for links containing /usedcar/detail/
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if "/usedcar/detail/" not in href:
            continue
        full_link = urljoin(base_url, href)
        title = (a.get_text() or "").strip()
        if not title:
            continue

        make, model = _extract_make_model(title)
        price = _parse_price_yen(title)
        year = _parse_year(title)
        # Color: not always in listing snippet; we leave None or try detail later
        color = None

        results.append({
            "make": make,
            "model": model,
            "year": year,
            "price": price,
            "color": color,
            "link": full_link,
        })

    # Deduplicate by link (same link can appear twice in HTML)
    seen = set()
    unique = []
    for r in results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)
    return unique


def fetch_detail_color(client: httpx.Client, detail_url: str) -> str | None:
    """Optional: fetch detail page and try to extract exterior color (外装色)."""
    try:
        r = fetch_with_retry(client, detail_url)
        soup = BeautifulSoup(r.text, "lxml")
        # Common pattern: 外装色 or "Color" / カラー
        for label in ["外装色", "カラー", "色"]:
            el = soup.find(string=re.compile(label))
            if el:
                parent = el.parent
                if parent:
                    next_ = parent.find_next_sibling()
                    if next_:
                        return next_.get_text(strip=True)[:64]
        return None
    except Exception as e:
        logger.debug("Could not fetch color from %s: %s", detail_url, e)
        return None


def run_scrape(max_listings: int = 50, fetch_colors: bool = False) -> list[dict[str, Any]]:
    """
    Run full scrape: fetch new listings page, parse, optionally enrich with color.
    Returns list of car dicts (make, model, year, price, color, link).
    """
    with httpx.Client(headers={"User-Agent": "AutoAdService/1.0 (test)"}) as client:
        r = fetch_with_retry(client, NEW_LISTINGS_URL)
        cars = scrape_listing_page(r.text)
        if max_listings:
            cars = cars[:max_listings]
        if fetch_colors and cars:
            for car in cars:
                if not car.get("color"):
                    car["color"] = fetch_detail_color(client, car["link"])
    return cars
