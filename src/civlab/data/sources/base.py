"""Base class for empirical source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from civlab.data.io import default_raw_path, download_to_path
from civlab.data.models import DownloadResult, NormalizationResult, SourceSummary


class DataSourceAdapter(ABC):
    """Abstract interface for empirical source adapters."""

    key: str

    @abstractmethod
    def describe(self) -> SourceSummary:
        """Return static metadata about the source and its assets."""

    def get_asset(self, asset_slug: str):
        for asset in self.describe().assets:
            if asset.slug == asset_slug:
                return asset
        raise KeyError(f"Unknown asset '{asset_slug}' for source '{self.key}'.")

    def download_asset(self, asset_slug: str, root: Path, **_: object) -> DownloadResult:
        asset = self.get_asset(asset_slug)
        if asset.download_url is None:
            raise ValueError(f"Asset '{asset_slug}' does not expose a direct download URL.")
        path = default_raw_path(root, self.key, asset)
        download_to_path(asset.download_url, path)
        return DownloadResult(asset=asset, path=path)

    @abstractmethod
    def normalize_asset(
        self,
        asset_slug: str,
        raw_path: Path,
        output_path: Path,
        **kwargs: object,
    ) -> NormalizationResult:
        """Normalize a raw asset into a canonical table."""
