"""Havza ve nokta (tarla) tanımları."""
from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

import yaml

from ..config import TABLES_DIR


@dataclass(frozen=True)
class Site:
    id: str
    name: str
    lat: float
    lon: float
    elevation_m: float
    basin_id: str
    irrigated: bool = True
    irrigation_method: str = "sprinkler"
    water_restricted: bool = False
    precip_factor: float = 1.0
    synthetic_history: tuple[tuple[int, str], ...] = ()

    @property
    def seed(self) -> int:
        return zlib.crc32(f"{self.basin_id}:{self.lat:.3f}:{self.lon:.3f}".encode())

    @property
    def cache_key(self) -> str:
        return f"{self.basin_id}_{self.id}_{self.lat:.3f}_{self.lon:.3f}"


@dataclass(frozen=True)
class Basin:
    id: str
    name_tr: str
    name_en: str
    country: str
    currency: str
    currency_symbol: str
    ag_year_start_month: int
    rule_packs: tuple[str, ...]
    water_cost_per_m3: float
    sustainable_water_fraction: float
    map_center: tuple[float, float]
    map_zoom: int
    grace_bbox: tuple[float, float, float, float]
    synthetic: dict = field(default_factory=dict, hash=False, compare=False)
    facts_tr: tuple[str, ...] = ()
    facts_en: tuple[str, ...] = ()
    sites: tuple[Site, ...] = ()

    def name(self, lang: str) -> str:
        return self.name_tr if lang == "tr" else self.name_en

    def facts(self, lang: str) -> tuple[str, ...]:
        return self.facts_tr if lang == "tr" else self.facts_en

    def site(self, site_id: str) -> Site:
        for s in self.sites:
            if s.id == site_id:
                return s
        raise KeyError(f"{self.id} havzasında nokta yok: {site_id}")

    @property
    def is_southern(self) -> bool:
        return self.map_center[0] < 0

    def ag_year_start(self, harvest_year: int) -> date:
        """Hasat yılı etiketi verilen tarım yılının başlangıç tarihi."""
        return date(harvest_year - 1, self.ag_year_start_month, 1)

    def planting_date(self, harvest_year: int, month: int, day: int) -> date:
        start = self.ag_year_start(harvest_year)
        year = start.year if month >= self.ag_year_start_month else start.year + 1
        return date(year, month, day)


@lru_cache(maxsize=1)
def load_basins() -> dict[str, Basin]:
    with open(TABLES_DIR / "basins.yaml", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    basins: dict[str, Basin] = {}
    for bid, b in raw.items():
        sites = tuple(
            Site(
                id=sid,
                name=s["name"],
                lat=float(s["lat"]),
                lon=float(s["lon"]),
                elevation_m=float(s["elevation_m"]),
                basin_id=bid,
                irrigated=bool(s.get("irrigated", True)),
                irrigation_method=s.get("irrigation_method", "sprinkler"),
                water_restricted=bool(s.get("water_restricted", False)),
                precip_factor=float(s.get("precip_factor", 1.0)),
                synthetic_history=tuple(sorted((int(k), v) for k, v in (s.get("synthetic_history") or {}).items())),
            )
            for sid, s in b["sites"].items()
        )
        basins[bid] = Basin(
            id=bid,
            name_tr=b["name_tr"],
            name_en=b["name_en"],
            country=b["country"],
            currency=b["currency"],
            currency_symbol=b["currency_symbol"],
            ag_year_start_month=int(b["ag_year_start_month"]),
            rule_packs=tuple(b["rule_packs"]),
            water_cost_per_m3=float(b["water_cost_per_m3"]),
            sustainable_water_fraction=float(b["sustainable_water_fraction"]),
            map_center=tuple(b["map_center"]),
            map_zoom=int(b["map_zoom"]),
            grace_bbox=tuple(b["grace_bbox"]),
            synthetic=b.get("synthetic", {}),
            facts_tr=tuple(b.get("facts_tr", [])),
            facts_en=tuple(b.get("facts_en", [])),
            sites=sites,
        )
    return basins


def custom_site(basin: Basin, lat: float, lon: float, elevation_m: float | None = None,
                irrigated: bool = True, irrigation_method: str = "sprinkler",
                water_restricted: bool = False) -> Site:
    """Kullanıcının haritada/koordinatla seçtiği serbest nokta."""
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Geçersiz koordinat")
    ref = basin.sites[0]
    return Site(
        id=f"custom_{lat:.3f}_{lon:.3f}",
        name=f"{lat:.3f}, {lon:.3f}",
        lat=lat,
        lon=lon,
        elevation_m=float(elevation_m if elevation_m is not None else ref.elevation_m),
        basin_id=basin.id,
        irrigated=irrigated,
        irrigation_method=irrigation_method,
        water_restricted=water_restricted,
    )
