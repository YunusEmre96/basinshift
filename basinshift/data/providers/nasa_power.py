"""NASA POWER günlük nokta API istemcisi (anahtar/giriş gerektirmez).

Belgeler: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
Topluluk: AG (Agroclimatology) — radyasyon MJ/m²/gün olarak döner.

Not: POWER'da güneş radyasyonu (ALLSKY_SFC_SW_DWN) Temmuz 1983'ten itibaren
vardır; daha önceki günler NaN kalır ve ET0 hesabında Hargreaves ile
tamamlanır (engine/et0.py). Bu durum provenance notuna yazılır.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from .http import FetchError, get_json

PARAM_MAP = {
    "T2M_MAX": "tmax",
    "T2M_MIN": "tmin",
    "T2M": "tmean",
    "RH2M": "rh",
    "WS2M": "wind2m",
    "ALLSKY_SFC_SW_DWN": "rs",
    "PRECTOTCORR": "precip",
}
FILL_VALUE = -999.0


def parse_power_json(payload: dict) -> pd.DataFrame:
    """POWER JSON yanıtını şemaya uygun DataFrame'e çevirir."""
    try:
        params = payload["properties"]["parameter"]
    except (KeyError, TypeError) as exc:
        msg = payload.get("messages") or payload.get("errors") or payload
        raise FetchError(f"Beklenmeyen POWER yanıtı: {str(msg)[:300]}") from exc
    frames = {}
    for power_name, col in PARAM_MAP.items():
        if power_name not in params:
            continue
        series = pd.Series(params[power_name], dtype=float)
        series.index = pd.to_datetime(series.index, format="%Y%m%d")
        frames[col] = series.replace(FILL_VALUE, np.nan)
    if not frames:
        raise FetchError("POWER yanıtında beklenen parametrelerin hiçbiri yok")
    df = pd.DataFrame(frames).sort_index()
    df.index.name = "date"
    if "tmean" not in df and {"tmax", "tmin"} <= set(df):
        df["tmean"] = (df["tmax"] + df["tmin"]) / 2
    for col in ("tmax", "tmin", "tmean", "rh", "wind2m"):
        if col in df:
            # Kısa boşlukları (≤3 gün) doğrusal doldur; uzun boşluklar NaN kalır.
            # Yağış enterpolasyonla UYDURULMAZ: eksik gün NaN kalır ve DataHub
            # eksiklik oranını uyarı olarak kaydeder.
            df[col] = df[col].interpolate(limit=3, limit_area="inside")
    return df


def fetch_power_daily(lat: float, lon: float, start: date, end: date, cfg: dict,
                      session=None) -> pd.DataFrame:
    """Uzun aralıkları 10 yıllık parçalar halinde indirir."""
    power_cfg = cfg.get("nasa", {}).get("power", {})
    base = power_cfg.get("base_url", "https://power.larc.nasa.gov/api/temporal/daily/point")
    chunks = []
    y = start.year
    while y <= end.year:
        c_start = max(start, date(y, 1, 1))
        c_end = min(end, date(y + 9, 12, 31))
        params = {
            "parameters": ",".join(PARAM_MAP),
            "community": power_cfg.get("community", "AG"),
            "longitude": round(lon, 4),
            "latitude": round(lat, 4),
            "start": c_start.strftime("%Y%m%d"),
            "end": c_end.strftime("%Y%m%d"),
            "format": "JSON",
        }
        payload = get_json(base, params, timeout=power_cfg.get("timeout_s", 60),
                           retries=power_cfg.get("max_retries", 3), session=session)
        chunks.append(parse_power_json(payload))
        y += 10
    df = pd.concat(chunks).sort_index()
    return df[~df.index.duplicated()]
