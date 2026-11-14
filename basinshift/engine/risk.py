"""Risk takvimi: 12 aylık iklim riskleri + planın ürün takvimiyle üst üste gösterim.

Her ay için (geçmiş yılların ortalaması):
    frost_days      Tmin < 0 °C olan gün sayısı
    hard_frost      Tmin < −5 °C
    heat_days       Tmax > 32 °C
    extreme_heat    Tmax > 35 °C
    heavy_rain      günlük yağış > 20 mm olan gün sayısı
    dry_month_prob  o ayın yağışının klimatolojinin %30'unun altında kaldığı yılların oranı
    precip_mm       ortalama aylık yağış
    et0_mm          ortalama aylık ET0
Çıplak toprak: HLS (yoksa MODIS) NDVI < 0.25 olan gözlemlerin aylık oranı.
"""
from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from ..data.basins import Basin
from ..knowledge.tables import Crop, Economics
from .calendar import season_for, stage_lengths

MONTHS = list(range(1, 13))
BARE_NDVI = 0.25


def monthly_climate_risk(climate: pd.DataFrame, et0: pd.Series) -> pd.DataFrame:
    c = climate.copy()
    c["et0"] = et0
    c["y"], c["m"] = c.index.year, c.index.month
    g = c.groupby(["y", "m"])
    per = pd.DataFrame({
        "frost_days": g["tmin"].apply(lambda s: (s < 0).sum()),
        "hard_frost": g["tmin"].apply(lambda s: (s < -5).sum()),
        "heat_days": g["tmax"].apply(lambda s: (s > 32).sum()),
        "extreme_heat": g["tmax"].apply(lambda s: (s > 35).sum()),
        "heavy_rain": g["precip"].apply(lambda s: (s > 20).sum()),
        "precip_mm": g["precip"].sum(),
        "et0_mm": g["et0"].sum(),
        "n": g["tmax"].size(),
    })
    per = per[per["n"] >= 25]
    clim_p = per.groupby(level="m")["precip_mm"].transform("mean")
    per["dry"] = (per["precip_mm"] < 0.3 * clim_p).astype(float)
    out = per.groupby(level="m").mean()
    out["dry_month_prob"] = out.pop("dry")
    return out.drop(columns="n").reindex(MONTHS)


def bare_soil_by_month(ndvi: pd.DataFrame | None) -> pd.Series | None:
    if ndvi is None or ndvi.empty:
        return None
    src = ndvi[ndvi["source"] == "HLS"]
    if len(src) < 50:
        src = ndvi
    recent = src.loc[src.index >= src.index.max() - pd.Timedelta(days=365 * 5)]
    return (recent["ndvi"] < BARE_NDVI).groupby(recent.index.month).mean().reindex(MONTHS)


def plan_calendar(plan: list[str], plan_years: list[int], crops: dict[str, Crop],
                  econ: dict[str, Economics], basin: Basin) -> pd.DataFrame:
    """Plan için günlük değil aylık şerit: hangi ayda hangi ürün, hangi dönemde.

    Sütunlar: year, crop, start, end, mid_start, mid_end, frost_start, frost_end
    """
    rows = []
    for y, cid in zip(plan_years, plan):
        crop = crops[cid]
        if crop.is_fallow:
            rows.append({"year": y, "crop": cid, "start": None, "end": None})
            continue
        s = season_for(crop, econ[cid], basin, y)
        l_ini, l_dev, l_mid, _ = stage_lengths(crop, econ[cid])
        mid_start = s.start + timedelta(days=l_ini + l_dev)
        mid_end = mid_start + timedelta(days=l_mid)
        if crop.frost_stage == "mid":
            fs, fe = mid_start, mid_start + timedelta(days=30)
        else:
            fs, fe = s.start, s.start + timedelta(days=l_ini + l_dev // 2)
        rows.append({"year": y, "crop": cid, "start": s.start, "end": s.end,
                     "mid_start": mid_start, "mid_end": mid_end, "frost_start": fs, "frost_end": fe})
    return pd.DataFrame(rows)


def plan_exposure(table, plan: list[str]) -> dict[str, float]:
    """Planın ürünlerinin hassas dönemlerinde ortalama stres günleri (geçmiş yıllar)."""
    heat = frost = wet = 0.0
    for cid in plan:
        i = table.index(cid)
        heat += table.heat_days[i].mean()
        frost += table.frost_days[i].mean()
        wet += table.wet_harvest_days[i].mean()
    n = max(len(plan), 1)
    return {"heat_days": heat / n, "frost_days": frost / n, "wet_harvest_days": wet / n}
