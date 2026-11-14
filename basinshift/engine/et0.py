"""FAO-56 Penman-Monteith referans buharlaşma-terleme (ET0).

Kaynak: Allen, Pereira, Raes & Smith (1998), FAO Irrigation and Drainage Paper 56,
Bölüm 2-3, Denklem 6 ve yardımcı denklemler. Doğrulama: tests/test_et0.py,
FAO-56 Örnek 18 (Uccle, 6 Temmuz) -> ET0 ≈ 3.9 mm/gün.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .solar import clear_sky_radiation, extraterrestrial_radiation, hargreaves_radiation

SIGMA = 4.903e-9  # Stefan-Boltzmann, MJ K-4 m-2 gün-1


def sat_vapour_pressure(t: np.ndarray) -> np.ndarray:
    """e°(T), kPa — Denklem 11."""
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def penman_monteith(
    tmax, tmin, rs, wind2m, lat_deg: float, elevation_m: float, doy,
    rh_mean=None, ea=None, albedo: float = 0.23,
) -> np.ndarray:
    """Günlük ET0 (mm/gün). Tüm girdiler aynı uzunlukta dizi veya skaler.

    Gerçek buhar basıncı için ``ea`` (kPa) verilebilir; verilmezse ``rh_mean``
    (%) ile Denklem 19 kullanılır (NASA POWER RH2M günlük ortalama verir).
    """
    tmax = np.asarray(tmax, dtype=float)
    tmin = np.asarray(tmin, dtype=float)
    rs = np.asarray(rs, dtype=float)
    u2 = np.asarray(wind2m, dtype=float)
    doy = np.asarray(doy, dtype=float)

    tmean = (tmax + tmin) / 2
    p = 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26          # Denk. 7
    gamma = 0.665e-3 * p                                              # Denk. 8
    es = (sat_vapour_pressure(tmax) + sat_vapour_pressure(tmin)) / 2  # Denk. 12
    if ea is None:
        if rh_mean is None:
            raise ValueError("ea veya rh_mean verilmeli")
        ea = np.asarray(rh_mean, dtype=float) / 100 * es              # Denk. 19
    ea = np.asarray(ea, dtype=float)
    delta = 4098 * sat_vapour_pressure(tmean) / (tmean + 237.3) ** 2  # Denk. 13

    ra = extraterrestrial_radiation(lat_deg, doy)
    rso = clear_sky_radiation(ra, elevation_m)
    rns = (1 - albedo) * rs                                           # Denk. 38
    rs_rso = np.clip(np.divide(rs, rso, out=np.ones_like(rs), where=rso > 0), 0.3, 1.0)
    rnl = SIGMA * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (
        0.34 - 0.14 * np.sqrt(np.maximum(ea, 0))
    ) * (1.35 * rs_rso - 0.35)                                        # Denk. 39
    rn = rns - rnl
    g = 0.0  # günlük adımda toprak ısı akısı ihmal edilir (Denk. 42)

    num = 0.408 * delta * (rn - g) + gamma * (900 / (tmean + 273)) * u2 * (es - ea)
    den = delta + gamma * (1 + 0.34 * u2)
    return np.maximum(num / den, 0.0)


def et0_from_climate(climate: pd.DataFrame, lat_deg: float, elevation_m: float) -> pd.Series:
    """Şemaya uygun günlük iklim tablosundan ET0 serisi üretir.

    Radyasyonu eksik günlerde (ör. NASA POWER'da 1984 öncesi) Hargreaves
    radyasyon tahmini kullanılır.
    """
    doy = climate.index.dayofyear.values
    rs = climate["rs"].to_numpy(dtype=float).copy()
    missing = np.isnan(rs)
    if missing.any():
        ra = extraterrestrial_radiation(lat_deg, doy)
        rs[missing] = hargreaves_radiation(
            climate["tmax"].to_numpy()[missing], climate["tmin"].to_numpy()[missing], ra[missing]
        )
    wind = climate["wind2m"].fillna(2.0).to_numpy(dtype=float)
    rh = climate["rh"].fillna(climate["rh"].mean() if climate["rh"].notna().any() else 55.0)
    et0 = penman_monteith(
        climate["tmax"].to_numpy(), climate["tmin"].to_numpy(), rs, wind,
        lat_deg, elevation_m, doy, rh_mean=rh.to_numpy(),
    )
    return pd.Series(et0, index=climate.index, name="et0")
