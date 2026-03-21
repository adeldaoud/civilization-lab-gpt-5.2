"""World Bank API download helpers."""

from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen


def fetch_indicator_series(indicator_code: str, *, per_page: int = 20000) -> list[dict[str, object]]:
    page = 1
    results: list[dict[str, object]] = []
    while True:
        query = urlencode({"format": "json", "per_page": per_page, "page": page})
        url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?{query}"
        with urlopen(url) as response:
            payload = json.loads(response.read().decode("utf-8"))
        metadata = payload[0]
        results.extend(payload[1])
        if metadata["page"] >= metadata["pages"]:
            break
        page += 1
    return results

