"""Uzun dönem eğilim testi: Mann-Kendall + Sen eğimi.

Brifteki "istatistiksel yaklaşım" önerisine karşılık: 40+ yıllık sıcaklık
ve yağış serilerinde anlamlı bir eğilim var mı? Parametrik olmayan, iklim
bilimlerinde standart test. (Bağlı değer düzeltmesi basitleştirilmiştir.)
"""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt

import numpy as np
import pandas as pd


@dataclass
class Trend:
    name: str
    unit: str
    slope_per_decade: float
    p_value: float
    n_years: int
    first_mean: float     # ilk 10 yıl ortalaması
    last_mean: float      # son 10 yıl ortalaması

    @property
    def significant(self) -> bool:
        return self.p_value < 0.05

    @property
    def direction(self) -> str:
        return "up" if self.slope_per_decade > 0 else "down"


def mann_kendall(x: np.ndarray) -> tuple[float, float]:
    """(Sen eğimi birim/yıl, iki yönlü p değeri)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return 0.0, 1.0
    s = 0.0
    for k in range(n - 1):
        s += np.sign(x[k + 1:] - x[k]).sum()
    _, counts = np.unique(x, return_counts=True)
    var_s = (n * (n - 1) * (2 * n + 5) - (counts * (counts - 1) * (2 * counts + 5)).sum()) / 18
    if s > 0:
        z = (s - 1) / sqrt(var_s)
    elif s < 0:
        z = (s + 1) / sqrt(var_s)
    else:
        z = 0.0
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
    i, j = np.triu_indices(n, k=1)
    slope = float(np.median((x[j] - x[i]) / (j - i)))
    return slope, float(p)


def climate_trends(climate: pd.DataFrame, et0: pd.Series, ag_year_start_month: int = 10) -> list[Trend]:
    c = climate.copy()
    c["et0"] = et0
    years = c.index.year
    complete = c.groupby(years).size()
    full = complete[complete >= 360].index
    c = c[np.isin(years, full)]
    y = c.index.year
    summer = c[c.index.month.isin([6, 7, 8])] if ag_year_start_month != 4 else c[c.index.month.isin([12, 1, 2])]
    series = {
        ("Yıllık ortalama sıcaklık", "°C"): c["tmean"].groupby(y).mean(),
        ("Yaz en yüksek sıcaklık ort.", "°C"): summer["tmax"].groupby(summer.index.year).mean(),
        ("Yıllık yağış", "mm"): c["precip"].groupby(y).sum(),
        ("32 °C üstü gün sayısı", "gün"): (c["tmax"] > 32).groupby(y).sum(),
        ("Yıllık ET0", "mm"): c["et0"].groupby(y).sum(),
    }
    out = []
    for (name, unit), s in series.items():
        slope, p = mann_kendall(s.to_numpy())
        out.append(Trend(name, unit, slope * 10, p, len(s), float(s.iloc[:10].mean()), float(s.iloc[-10:].mean())))
    return out
