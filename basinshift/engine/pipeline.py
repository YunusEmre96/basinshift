"""Uçtan uca kurulum: veri → senaryo → ET0 → ürün-yıl tablosu → FieldContext.

Arayüz ve testler bu tek giriş noktasını kullanır.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
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


#: Yağış düzeltmesi: POWER (MERRA-2 tabanlı) yağışı yarı kurak iç bölgelerde fazla verebilir
#: (Çumra: POWER ~540 mm/yıl, IMERG ~330 mm/yıl, Konya istasyon normali ~320–330 mm).
#: Gerçek IMERG verisi varsa her takvim ayı için IMERG/POWER oranı (örtüşen yıllar) hesaplanır
#: ve bütün POWER serisine uygulanır ("aylık oran yöntemi"). Günlük dizilim korunur.
PRECIP_RATIO_CLIP = (0.3, 1.5)
MIN_OVERLAP_YEARS = 10


def imerg_monthly_ratio(power_p: pd.Series, imerg_p: pd.Series) -> pd.Series | None:
    """Takvim ayı → IMERG/POWER toplam yağış oranı. Yetersiz örtüşmede None."""
    both = pd.concat([power_p.astype(float), imerg_p.astype(float)], axis=1, keys=["power", "imerg"], sort=True).dropna()
    if both.empty:
        return None
    monthly = both.resample("MS").agg(["sum", "count"])
    full = monthly[("power", "count")] >= 25
    monthly = monthly[full]
    if monthly.index.year.nunique() < MIN_OVERLAP_YEARS:
        return None
    s_p = monthly[("power", "sum")].groupby(monthly.index.month).sum()
    s_i = monthly[("imerg", "sum")].groupby(monthly.index.month).sum()
    ratio = (s_i / s_p.replace(0, np.nan)).fillna(1.0).clip(*PRECIP_RATIO_CLIP)
    return ratio.reindex(range(1, 13)).fillna(1.0)


def correct_precip(climate: pd.DataFrame, ratio: pd.Series) -> pd.DataFrame:
    out = climate.copy()
    out["precip"] = out["precip"] * ratio.reindex(out.index.month).to_numpy()
    return out


SITE_DATASETS = ["climate_daily", "soil_moisture", "ndvi", "precip_satellite", "climate_deltas",
                 "terrain", "soil_properties"]


@dataclass
class SiteData:
    climate: pd.DataFrame
    et0: pd.Series
    #: düzeltme öncesi POWER yağışı (karşılaştırma grafikleri için); düzeltme yoksa None
    precip_raw: pd.Series | None
    soil_moisture: pd.DataFrame | None
    ndvi: pd.DataFrame | None
    precip_sat: pd.DataFrame | None
    deltas: pd.DataFrame | None
    terrain: dict
    soil_props: dict
    #: BU NOKTANIN veri setlerinin kaynak kaydı (paylaşılan hub'ın "son kayıt"ı değil)
    provenance: dict[str, Provenance]
    #: uygulanan IMERG/POWER aylık oranları (düzeltme yapılmadıysa None)
    precip_ratio: pd.Series | None = None


def load_site_data(hub: DataHub, site: Site, basin: Basin) -> SiteData:
    climate = hub.climate_daily(site, basin)
    precip_sat = hub.precip_satellite(site, basin)
    sd = SiteData(
        climate=climate,
        et0=et0_from_climate(climate, site.lat, site.elevation_m),
        precip_raw=None,
        soil_moisture=hub.soil_moisture(site, basin),
        ndvi=hub.ndvi(site, basin),
        precip_sat=precip_sat,
        deltas=hub.climate_deltas(site, basin),
        terrain=hub.terrain(site, basin),
        soil_props=hub.soil_properties(site, basin),
        provenance={},
    )
    sd.provenance = hub.snapshot(SITE_DATASETS)
    mode = str(hub.cfg["data"].get("precip_correction", "imerg_monthly") or "none")
    cp, pp = sd.provenance.get("climate_daily"), sd.provenance.get("precip_satellite")
    # Yalnızca iki gerçek seri varsa düzelt (sentetik/yer tutucu veriyle asla)
    if (mode == "imerg_monthly" and precip_sat is not None and cp is not None and pp is not None
            and cp.is_real and pp.is_real):
        ratio = imerg_monthly_ratio(climate["precip"], precip_sat["precip"])
        if ratio is not None:
            before = float(climate["precip"].resample("YS").sum(min_count=330).mean())
            sd.precip_raw = climate["precip"].copy()
            sd.climate = correct_precip(climate, ratio)
            after = float(sd.climate["precip"].resample("YS").sum(min_count=330).mean())
            cp.notes.append(bi(
                f"Yağış GPM IMERG ile aylık oran yöntemiyle düzeltildi: yıllık ortalama {before:.0f} → {after:.0f} mm "
                f"(ay oranları {ratio.min():.2f}–{ratio.max():.2f}).",
                f"Precipitation bias-corrected with GPM IMERG (monthly ratio method): annual mean {before:.0f} → {after:.0f} mm "
                f"(monthly ratios {ratio.min():.2f}–{ratio.max():.2f}).",
            ))
            sd.precip_ratio = ratio
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
    # Gerçek iklimle sentetik toprak nemi karıştırılmaz: SMAP yer tutucuysa başlangıç nemi
    # gerçek yağıştan (son 90 gün göstergesi) tahmin edilir. Tamamen sentetik demo modunda kullanılır.
    smp, cp = sd.provenance.get("soil_moisture"), sd.provenance.get("climate_daily")
    sm_ok = smp is None or smp.is_real or (cp is not None and cp.is_synthetic)
    table = build_crop_year_table(
        climate, et0, basin, crops, econ, ids, sd.soil_props.get("taw_mm_per_m", 150.0),
        range(first, last + 1), sd.soil_moisture if (scenario.is_baseline and sm_ok) else None,
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
