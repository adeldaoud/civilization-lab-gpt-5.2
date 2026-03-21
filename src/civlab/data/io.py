"""Filesystem and serialization helpers for the empirical data layer."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlparse
from urllib.request import urlopen

from civlab.data.models import AssetFormat, CanonicalSchema, DatasetAsset

csv.field_size_limit(1024 * 1024 * 64)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename_from_url(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or fallback


def download_to_path(url: str, destination: Path) -> Path:
    ensure_directory(destination.parent)
    with urlopen(url) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return destination


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: object) -> Path:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return path


def write_canonical_csv(path: Path, schema: CanonicalSchema, rows: Iterable[dict[str, str]]) -> int:
    ensure_directory(path.parent)
    fieldnames = [column.name for column in schema.columns]
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
            count += 1
    return count


def zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def read_zip_csv_rows(path: Path, member_selector: Callable[[str], bool]) -> tuple[str, list[dict[str, str]]]:
    with zipfile.ZipFile(path) as archive:
        member_name = next(
            name
            for name in archive.namelist()
            if member_selector(name) and name.lower().endswith(".csv") and "__macosx" not in name.lower()
        )
        with archive.open(member_name) as handle:
            wrapper = io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")
            return member_name, list(csv.DictReader(wrapper))


def default_raw_path(root: Path, source_key: str, asset: DatasetAsset) -> Path:
    filename = asset.default_filename or safe_filename_from_url(asset.download_url or asset.url, asset.slug)
    return root / "data" / "raw" / source_key / filename


def default_processed_path(root: Path, source_key: str, asset: DatasetAsset) -> Path:
    suffix = ".csv"
    if asset.canonical_table is None:
        suffix = ".json"
    table_label = asset.canonical_table.value if asset.canonical_table else asset.slug
    return root / "data" / "processed" / source_key / f"{asset.slug}__{table_label}{suffix}"

