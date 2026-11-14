"""Uçtan uca kurulum: veri → senaryo → ET0 → ürün-yıl tablosu → FieldContext.

Arayüz ve testler bu tek giriş noktasını kullanır.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..data.basins import Basin, Site
from ..data.hub import DataHub, Provenance
from ..knowledge.rules import load_rule_pack
from ..knowledge.tables import basin_crops, load_crops, load_economics
from ..textutil import bi
from .et0 import et0_from_climate
from .field import FieldContext, FieldSettings
from .scenarios import Scenario, apply_scenario
from .water import build_crop_year_table


SITE_DATASETS = ["climate_daily", "soil_moisture", "ndvi", "precip_satellite", "climate_deltas",
                 "terrain", "soil_properties"]


@dataclass
class SiteData:
    climate: pd.DataFrame
    et0: pd.Series
    soil_moisture: pd.DataFrame | None
    ndvi: pd.DataFrame | None
    precip_sat: pd.DataFrame | None
    deltas: pd.DataFrame | None
    terrain: dict
    soil_props: dict
    #: BU NOKTANIN veri setlerinin kaynak kaydı (paylaşılan hub'ın "son kayıt"ı değil)
    provenance: dict[str, Provenance]


def load_site_data(hub: DataHub, site: Site, basin: Basin) -> SiteData:
    climate = hub.climate_daily(site, basin)
    sd = SiteData(
        climate=climate,
        et0=et0_from_climate(climate, site.lat, site.elevation_m),
        soil_moisture=hub.soil_moisture(site, basin),
        ndvi=hub.ndvi(site, basin),
        precip_sat=hub.precip_satellite(site, basin),
        deltas=hub.climate_deltas(site, basin),
        terrain=hub.terrain(site, basin),
        soil_props=hub.soil_properties(site, basin),
        provenance={},
    )
    sd.provenance = hub.snapshot(SITE_DATASETS)
    return sd


def build_context(hub: DataHub, site: Site, basin: Basin, settings: FieldSettings,
                  scenario: Scenario = Scenario(), rule_pack_ids: list[str] | None = None,
                  site_data: SiteData | None = None, crop_ids: list[str] | None = None) -> FieldContext:
    sd = site_data or load_site_data(hub, site, basin)
    crops = load_crops()
    econ = load_economics(basin.id)
    ids = crop_ids or basin_crops(basin.id)
    climate = apply_scenario(sd.climate, scenario, sd.deltas)
    et0 = sd.et0 if scenario.is_baseline else et0_from_climate(climate, site.lat, site.elevation_m)
    first, last = hub.history
    table = build_crop_year_table(
        climate, et0, basin, crops, econ, ids, sd.soil_props.get("taw_mm_per_m", 150.0),
        range(first, last + 1), sd.soil_moisture if scenario.is_baseline else None,
        heat_ref_tmax=sd.climate["tmax"],
    )
    packs = [load_rule_pack(p) for p in (rule_pack_ids if rule_pack_ids is not None else basin.rule_packs)]
    ctx = FieldContext(basin, site, crops, econ, ids, table, packs, settings, float(sd.terrain.get("slope_deg", 0.5)))
    ctx.provenance = sd.provenance
    if table.dropped_years:
        cp = ctx.provenance.get("climate_daily")
        if cp is not None:
            msg = bi(
                f"Sezonunda verinin %5'inden fazlası eksik olduğu için stres testinden çıkarılan yıllar: {table.dropped_years}",
                f"Years dropped from the stress test because more than 5% of in-season data is missing: {table.dropped_years}",
            )
            if msg not in cp.warnings:
                cp.warnings.append(msg)
    return ctx
