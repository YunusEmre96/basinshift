"""Veri sözleşmesi (şema).

Hangi kaynaktan gelirse gelsin (sentetik, NASA API, dosya) her veri seti
bu şemaya dönüştürülür. Hesap çekirdeği YALNIZCA bu şemayı bilir; bu yüzden
veri kaynağını değiştirmek hesapları etkilemez.

Tablo veri setleri tarih indeksli ``pd.DataFrame`` döner; ``terrain`` ve
``soil_properties`` sözlük döner.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import math

import numpy as np
import pandas as pd


class SchemaError(ValueError):
    """Veri şemaya uymuyor."""


@dataclass(frozen=True)
class Column:
    name: str
    unit: str
    lo: float | None = None
    hi: float | None = None
    required: bool = True


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    kind: str                  # "table" | "dict"
    product: str               # Gerçek NASA ürünü
    resolution: str
    use_scale_tr: str          # Hangi ölçekte kullanılmalı
    use_scale_en: str
    columns: tuple[Column, ...] = field(default_factory=tuple)
    freq: str | None = None    # "D" günlük, "MS" aylık vb.


SPECS: dict[str, DatasetSpec] = {
    "climate_daily": DatasetSpec(
        "climate_daily", "table", "NASA POWER (Agroclimatology, günlük)", "0.5° × 0.625°",
        "Bölge ölçeği iklim; tarla için yeterli homojenlikte",
        "Regional-scale climate; homogeneous enough for a field",
        (
            Column("tmax", "°C", -60, 60),
            Column("tmin", "°C", -70, 50),
            Column("tmean", "°C", -60, 55),
            Column("rh", "%", 0, 100),
            Column("wind2m", "m/s", 0, 40),
            Column("rs", "MJ/m²/gün", 0, 45),
            Column("precip", "mm/gün", 0, 600),
        ),
        "D",
    ),
    "soil_moisture": DatasetSpec(
        "soil_moisture", "table", "SMAP L4 (SPL4SMGP)", "9 km, 3 saatlik (günlüğe toplanır)",
        "Ekim zamanı başlangıç nemi ve nem anomalisi",
        "Initial moisture at planting and moisture anomaly",
        (Column("sm_surface", "m³/m³", 0, 1), Column("sm_rootzone", "m³/m³", 0, 1)),
        "D",
    ),
    "ndvi": DatasetSpec(
        "ndvi", "table", "HLS (Landsat+Sentinel-2) 30 m / MODIS MOD13Q1 250 m", "30 m / 250 m",
        "Tarla: ürün geçmişi ve çıplak toprak dönemleri (HLS); bölge eğilimi (MODIS)",
        "Field: crop history and bare-soil periods (HLS); regional trend (MODIS)",
        (Column("ndvi", "-", -1, 1), Column("source", "-", required=True)),
        None,
    ),
    "precip_satellite": DatasetSpec(
        "precip_satellite", "table", "GPM IMERG Final (günlük)", "0.1°",
        "Yağış için ikinci kaynak; uydu–yer karşılaştırması",
        "Second precipitation source; satellite vs ground comparison",
        (Column("precip", "mm/gün", 0, 1000),),
        "D",
    ),
    "water_storage": DatasetSpec(
        "water_storage", "table", "GRACE / GRACE-FO Mascon (JPL/CSR)", "~300 km, aylık",
        "YALNIZCA havza ölçeği; tarla/ilçe yorumu yapılmaz",
        "Basin scale ONLY; never interpreted per field or district",
        (Column("tws_anomaly_cm", "cm", -200, 200), Column("uncertainty_cm", "cm", 0, 100, required=False)),
        "MS",
    ),
    "climate_deltas": DatasetSpec(
        "climate_deltas", "table", "NEX-GDDP-CMIP6 (2041–2060 vs 1995–2014)", "0.25°, günlük → aylık değişim",
        "Gelecek iklim senaryosu (değişim katsayısı yöntemi)",
        "Future climate scenario (delta-change method)",
        (
            Column("month", "-", 1, 12),
            Column("scenario", "-"),
            Column("dtmax", "°C", -10, 15),
            Column("dtmin", "°C", -10, 15),
            Column("precip_ratio", "-", 0, 5),
        ),
        None,
    ),
    "terrain": DatasetSpec(
        "terrain", "dict", "SRTM GL1 (NASA)", "30 m",
        "Eğim → su erozyonu riski", "Slope → water erosion risk",
        (Column("elevation_m", "m", -500, 9000), Column("slope_deg", "°", 0, 90)),
    ),
    "soil_properties": DatasetSpec(
        "soil_properties", "dict", "SoilGrids (ISRIC) / yerel toprak etüdü", "250 m",
        "Toprağın tutabildiği kullanılabilir su (TAW)", "Total available water (TAW)",
        (
            Column("taw_mm_per_m", "mm/m", 30, 300),
            Column("clay_pct", "%", 0, 100, required=False),
            Column("sand_pct", "%", 0, 100, required=False),
            Column("soc_g_kg", "g/kg", 0, 600, required=False),
            Column("ph", "-", 2, 12, required=False),
        ),
    ),
}


def validate(dataset: str, data):
    """Veriyi şemaya göre doğrular ve normalize eder. Hata durumunda
    ``SchemaError`` fırlatır; sessizce düzeltmez (yalnızca sıralama ve tip)."""
    spec = SPECS.get(dataset)
    if spec is None:
        raise SchemaError(f"Bilinmeyen veri seti: {dataset}")

    if spec.kind == "dict":
        if not isinstance(data, dict):
            raise SchemaError(f"{dataset}: sözlük bekleniyordu, {type(data).__name__} geldi")
        out = dict(data)
        for col in spec.columns:
            if col.name not in out or out[col.name] is None:
                if col.required:
                    raise SchemaError(f"{dataset}: zorunlu alan eksik: {col.name}")
                continue
            val = float(out[col.name])
            if math.isnan(val):
                if col.required:
                    raise SchemaError(f"{dataset}: zorunlu alan boş (NaN): {col.name}")
                out.pop(col.name)
                continue
            if (col.lo is not None and val < col.lo) or (col.hi is not None and val > col.hi):
                raise SchemaError(f"{dataset}.{col.name}={val} aralık dışı [{col.lo}, {col.hi}]")
            out[col.name] = val
        return out

    if not isinstance(data, pd.DataFrame):
        raise SchemaError(f"{dataset}: DataFrame bekleniyordu, {type(data).__name__} geldi")
    df = data.copy()
    if dataset != "climate_deltas":
        if not isinstance(df.index, pd.DatetimeIndex):
            raise SchemaError(f"{dataset}: indeks DatetimeIndex olmalı")
        if "source" in df.columns:
            key = pd.MultiIndex.from_arrays([df.index, df["source"]])
            df = df[~key.duplicated(keep="first")].sort_index()
        else:
            df = df[~df.index.duplicated(keep="first")].sort_index()
    missing = [c.name for c in spec.columns if c.required and c.name not in df.columns]
    if missing:
        raise SchemaError(f"{dataset}: eksik sütun(lar): {missing}")
    for col in spec.columns:
        if col.name not in df.columns or col.name in ("source", "scenario"):
            continue
        df[col.name] = pd.to_numeric(df[col.name], errors="coerce")
        vals = df[col.name].dropna()
        if len(vals) and col.lo is not None and (vals < col.lo).any():
            raise SchemaError(f"{dataset}.{col.name}: {col.lo} altında değer var (min={vals.min():.3g})")
        if len(vals) and col.hi is not None and (vals > col.hi).any():
            raise SchemaError(f"{dataset}.{col.name}: {col.hi} üstünde değer var (max={vals.max():.3g})")
    if len(df) == 0:
        raise SchemaError(f"{dataset}: boş tablo")
    for col in spec.columns:
        if col.required and col.name in df.columns and col.name not in ("source", "scenario") \
                and df[col.name].isna().all():
            raise SchemaError(f"{dataset}: zorunlu sütun tamamen boş: {col.name}")
    keep = [c.name for c in spec.columns if c.name in df.columns]
    if dataset == "climate_deltas":
        return df[keep].reset_index(drop=True)
    return df[keep]


def completeness(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns or len(df) == 0:
        return 0.0
    return float(np.isfinite(df[column].to_numpy(dtype=float)).mean())
