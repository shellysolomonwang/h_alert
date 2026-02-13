import json
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

HERMES_BAGS_URL = "https://www.hermes.com/us/en/category/leather-goods/bags-and-clutches/womens-bags-and-clutches/#|"


@dataclass
class BagAvailability:
    name: str
    in_stock: bool


def fetch_page_html(timeout: int = 15) -> str:
    response = requests.get(HERMES_BAGS_URL, timeout=timeout)
    response.raise_for_status()
    return response.text


def _normalize(name: str) -> str:
    return " ".join(name.split()).strip().lower()


def parse_availability(html: str) -> dict[str, bool]:
    soup = BeautifulSoup(html, "html.parser")
    availability: dict[str, bool] = {}

    for script in soup.find_all("script", type="application/ld+json"):
        raw = (script.string or "").strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue

        candidates = payload if isinstance(payload, list) else [payload]
        for candidate in candidates:
            entries = candidate.get("itemListElement") if isinstance(candidate, dict) else None
            if not entries:
                continue
            for entry in entries:
                product = entry.get("item", {}) if isinstance(entry, dict) else {}
                name = product.get("name")
                offers = product.get("offers", {})
                stock_state = offers.get("availability", "") if isinstance(offers, dict) else ""
                if isinstance(name, str) and name:
                    availability[_normalize(name)] = "instock" in stock_state.lower()

    for card in soup.select('[data-testid="product-item"], .product-item, .product-grid-item'):
        text = card.get_text(" ", strip=True).lower()
        name_el = card.select_one('[data-testid="product-item-name"], .product-item-name, a[title]')
        name = ""
        if name_el:
            name = name_el.get("title") or name_el.get_text(" ", strip=True)
        if not name:
            continue

        normalized = _normalize(name)
        in_stock = "add to cart" in text and "notify me" not in text and "out of stock" not in text
        availability.setdefault(normalized, in_stock)

    return availability


def get_available_bags() -> dict[str, bool]:
    return parse_availability(fetch_page_html())
