"""Configuration loading and path resolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"


@dataclass
class Config:
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> "Config":
        with open(path, "r", encoding="utf-8") as fh:
            return cls(raw=yaml.safe_load(fh))

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def path(self, key: str) -> Path:
        p = Path(self.raw[key])
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    def data_path(self, sub: str) -> Path:
        p = Path(self.raw["data"][sub])
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()
