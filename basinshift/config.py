"""Yapılandırma yükleyici.

Öncelik sırası (yüksekten düşüğe):
    1. Ortam değişkeni  BASINSHIFT_DATA_<VERİSETİ>  (örn. BASINSHIFT_DATA_CLIMATE_DAILY=nasa)
    2. Ortam değişkeni  BASINSHIFT_DATA             (tüm veri setleri için)
    3. config.yaml -> data.sources.<veriseti>
    4. config.yaml -> data.default_source
"""
from __future__ import annotations

import copy
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = ROOT / "tables"
DEFAULT_CONFIG_PATH = ROOT / "config.yaml"

DATASETS = (
    "climate_daily",
    "soil_moisture",
    "ndvi",
    "precip_satellite",
    "water_storage",
    "climate_deltas",
    "terrain",
    "soil_properties",
)
VALID_SOURCES = ("synthetic", "nasa", "files")


class ConfigError(ValueError):
    """Geçersiz yapılandırma."""


@lru_cache(maxsize=4)
def _load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(path: str | os.PathLike | None = None) -> dict:
    """config.yaml'ı okur ve ortam değişkeni geçersiz kılmalarını uygular."""
    cfg_path = Path(path or os.environ.get("BASINSHIFT_CONFIG", DEFAULT_CONFIG_PATH))
    cfg = copy.deepcopy(_load_yaml(str(cfg_path)))
    data = cfg.setdefault("data", {})
    sources = data.setdefault("sources", {}) or {}
    data["sources"] = sources

    global_override = os.environ.get("BASINSHIFT_DATA")
    if global_override:
        data["default_source"] = global_override
        for ds in DATASETS:
            sources[ds] = None

    for ds in DATASETS:
        env_val = os.environ.get(f"BASINSHIFT_DATA_{ds.upper()}")
        if env_val:
            sources[ds] = env_val

    default = data.get("default_source", "synthetic")
    if default not in VALID_SOURCES:
        raise ConfigError(f"data.default_source geçersiz: {default!r} (seçenekler: {VALID_SOURCES})")
    for ds in DATASETS:
        src = sources.get(ds) or default
        if src not in VALID_SOURCES:
            raise ConfigError(f"data.sources.{ds} geçersiz: {src!r} (seçenekler: {VALID_SOURCES})")
        sources[ds] = src

    # Göreli yolları proje köküne göre çöz
    cache = data.setdefault("cache", {})
    cache["dir"] = str((ROOT / cache.get("dir", "data/cache")).resolve())
    data["files_dir"] = str((ROOT / data.get("files_dir", "data/external")).resolve())
    return cfg


def source_for(cfg: dict, dataset: str) -> str:
    if dataset not in DATASETS:
        raise ConfigError(f"Bilinmeyen veri seti: {dataset}")
    return cfg["data"]["sources"][dataset]


def get(cfg: dict, dotted: str, default: Any = None) -> Any:
    cur: Any = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur
