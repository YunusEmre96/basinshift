"""tables/ klasöründeki CSV/YAML bilgi tablolarının yükleyicileri.

Tüm agronomik ve ekonomik varsayımlar kodda DEĞİL, bu tablolarda durur;
böylece ziraat mühendisi ya da ekip, kod bilmeden değerleri güncelleyebilir.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
import yaml

from ..config import TABLES_DIR


@dataclass(frozen=True)
class Crop:
    id: str
    name_tr: str
    name_en: str
    family: str
    n_fixing: bool
    kc_ini: float
    kc_mid: float
    kc_end: float
    l_ini: int
    l_dev: int
    l_mid: int
    l_late: int
    root_depth_m: float
    ky: float
    heat_thr_c: float
    frost_thr_c: float
    frost_stage: str
    om_score: float
    residue_cover_months: int
    min_gap_years: int
    forage_kg_dm_da: float
    drought_tolerance: str
    deep_rooted: bool
    equipment: str
    contract_required: bool
    color: str
    local_risks_tr: str
    local_risks_en: str
    source_note: str

    @property
    def is_fallow(self) -> bool:
        return self.id == "fallow"

    @property
    def season_days(self) -> int:
        return self.l_ini + self.l_dev + self.l_mid + self.l_late

    def name(self, lang: str) -> str:
        return self.name_tr if lang == "tr" else self.name_en

    def local_risks(self, lang: str) -> str:
        return self.local_risks_tr if lang == "tr" else self.local_risks_en


@dataclass(frozen=True)
class Economics:
    crop_id: str
    plant_month: int
    plant_day: int
    ym_kg_da: float
    price_per_kg: float
    var_cost_per_da: float
    rainfed_ok: bool
    rainfed_cost_factor: float
    demand_elasticity: float
    season_scale: float
    note: str


@lru_cache(maxsize=1)
def load_crops() -> dict[str, Crop]:
    df = pd.read_csv(TABLES_DIR / "crops.csv", keep_default_na=False)
    crops = {}
    for r in df.to_dict("records"):
        crops[r["crop_id"]] = Crop(
            id=r["crop_id"], name_tr=r["name_tr"], name_en=r["name_en"], family=r["family"],
            n_fixing=bool(int(r["n_fixing"])), kc_ini=float(r["kc_ini"]), kc_mid=float(r["kc_mid"]),
            kc_end=float(r["kc_end"]), l_ini=int(r["l_ini"]), l_dev=int(r["l_dev"]), l_mid=int(r["l_mid"]),
            l_late=int(r["l_late"]), root_depth_m=float(r["root_depth_m"]), ky=float(r["ky"]),
            heat_thr_c=float(r["heat_thr_c"]), frost_thr_c=float(r["frost_thr_c"]),
            frost_stage=r["frost_stage"], om_score=float(r["om_score"]),
            residue_cover_months=int(r["residue_cover_months"]), min_gap_years=int(r["min_gap_years"]),
            forage_kg_dm_da=float(r["forage_kg_dm_da"]), drought_tolerance=r["drought_tolerance"],
            deep_rooted=bool(int(r["deep_rooted"])), equipment=r["equipment"] or "",
            contract_required=bool(int(r["contract_required"])), color=r["color"],
            local_risks_tr=r["local_risks_tr"], local_risks_en=r["local_risks_en"],
            source_note=r["source_note"],
        )
    return crops


@lru_cache(maxsize=1)
def _economics_df() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "basin_economics.csv", comment="#", keep_default_na=False)


def load_economics(basin_id: str) -> dict[str, Economics]:
    df = _economics_df()
    sub = df[df["basin"] == basin_id]
    if sub.empty:
        raise KeyError(f"basin_economics.csv içinde havza yok: {basin_id}")
    out = {}
    for r in sub.to_dict("records"):
        out[r["crop_id"]] = Economics(
            crop_id=r["crop_id"], plant_month=int(r["plant_month"]), plant_day=int(r["plant_day"]),
            ym_kg_da=float(r["ym_kg_da"]), price_per_kg=float(r["price_per_kg"]),
            var_cost_per_da=float(r["var_cost_per_da"]), rainfed_ok=bool(int(r["rainfed_ok"])),
            rainfed_cost_factor=float(r["rainfed_cost_factor"]),
            demand_elasticity=float(r["demand_elasticity"]),
            season_scale=float(r.get("season_scale") or 1.0), note=r["note"],
        )
    return out


@lru_cache(maxsize=1)
def load_rotation_effects() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "rotation_effects.csv", comment="#", keep_default_na=False)


@lru_cache(maxsize=1)
def load_farm_types_df() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "farm_types.csv", comment="#", keep_default_na=False)


@lru_cache(maxsize=1)
def load_glossary() -> dict:
    with open(TABLES_DIR / "glossary.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=4)
def load_commodity_trade(basin_id: str | None = None) -> pd.DataFrame:
    """Küresel emtia ticareti, ithalat/ihracat dengesi ve sanal su tablosu."""
    path = TABLES_DIR / "commodity_trade.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if basin_id:
        df = df[df["basin"] == basin_id].copy()
    return df


def basin_crops(basin_id: str) -> list[str]:
    """Havzada ekonomik verisi tanımlı ürünler (sıralı)."""
    crops = load_crops()
    return [c for c in load_economics(basin_id) if c in crops]
