"""Güneş geometrisi ve radyasyon (FAO-56, Bölüm 3, Denklem 21-39).

Hem ET0 hesabında hem de sentetik veri üretiminde ve eksik radyasyon
verisinin (NASA POWER'da 1984 öncesi) Hargreaves ile tamamlanmasında kullanılır.
"""
from __future__ import annotations

import numpy as np

GSC = 0.0820  # Güneş sabiti, MJ m-2 dk-1


def extraterrestrial_radiation(lat_deg: float, doy: np.ndarray) -> np.ndarray:
    """Atmosfer dışı radyasyon Ra (MJ m-2 gün-1), FAO-56 Denklem 21."""
    doy = np.asarray(doy, dtype=float)
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi / 365 * doy)
    delta = 0.409 * np.sin(2 * np.pi / 365 * doy - 1.39)
    ws_arg = np.clip(-np.tan(phi) * np.tan(delta), -1.0, 1.0)
    ws = np.arccos(ws_arg)
    ra = (24 * 60 / np.pi) * GSC * dr * (
        ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws)
    )
    return np.maximum(ra, 0.0)


def clear_sky_radiation(ra: np.ndarray, elevation_m: float) -> np.ndarray:
    """Açık gök radyasyonu Rso, FAO-56 Denklem 37."""
    return (0.75 + 2e-5 * elevation_m) * ra


def hargreaves_radiation(tmax: np.ndarray, tmin: np.ndarray, ra: np.ndarray, krs: float = 0.16) -> np.ndarray:
    """Sıcaklıktan güneş radyasyonu tahmini (Hargreaves), FAO-56 Denklem 50.

    krs: iç kesimler için ~0.16, kıyı için ~0.19.
    """
    dtr = np.maximum(np.asarray(tmax) - np.asarray(tmin), 0.0)
    return krs * np.sqrt(dtr) * ra
