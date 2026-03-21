"""Normalization helpers shared across source adapters."""

from __future__ import annotations

from collections.abc import Iterable


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def coalesce(*values: object) -> str:
    for value in values:
        text = clean_text(value)
        if text:
            return text
    return ""


def parse_year(value: object) -> str:
    text = clean_text(value)
    if not text:
        return ""
    if len(text) >= 4 and text[:4].isdigit():
        return text[:4]
    return ""


def parse_numeric_text(value: object) -> tuple[str, str]:
    text = clean_text(value)
    if not text:
        return "", ""
    normalized = text.replace(",", "")
    try:
        number = float(normalized)
    except ValueError:
        return "", text
    if number.is_integer():
        return str(int(number)), ""
    return str(number), ""


def select_series(all_columns: Iterable[str], preferred: Iterable[str] | None, id_columns: Iterable[str]) -> tuple[str, ...]:
    id_set = {column for column in id_columns}
    columns = [column for column in all_columns if column not in id_set]
    if preferred is None:
        return tuple(columns)
    preferred_set = [column for column in preferred if column in columns]
    return tuple(preferred_set)

