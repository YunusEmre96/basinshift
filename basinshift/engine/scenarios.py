"""İklim senaryoları: kaydırıcılar ve CMIP6 değişim katsayısı (delta) yöntemi.

Değişim katsayısı yöntemi: gözlenen (veya POWER) günlük serinin her ayına,
iklim modellerinin 2041–2060 ile 1995–2014 arasındaki aylık farkı eklenir
(sıcaklık) veya oranla çarpılır (yağış). Basit, şeffaf ve yaygın bir
"downscaling" yöntemidir; günlük değişkenlik yapısını korur, değiştirmez.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Scenario:
    d_temp_c: float = 0.0        # tüm yıla eklenen sıcaklık farkı
    precip_pct: float = 0.0      # yağışta yüzde değişim (-30 → %30 azalma)
    cmip6: str | None = None     # None | "ssp245" | "ssp585"

    @property
    def is_baseline(self) -> bool:
        return self.d_temp_c == 0 and self.precip_pct == 0 and self.cmip6 is None

    def key(self) -> str:
        return f"dt{self.d_temp_c:+.1f}_dp{self.precip_pct:+.0f}_{self.cmip6 or 'hist'}"


def apply_scenario(climate: pd.DataFrame, scenario: Scenario, deltas: pd.DataFrame | None) -> pd.DataFrame:
    if scenario.is_baseline:
        return climate
    out = climate.copy()
    if scenario.cmip6:
        if deltas is None or deltas.empty:
            raise ValueError("CMIP6 senaryosu için climate_deltas verisi yok")
        d = deltas[deltas["scenario"] == scenario.cmip6].set_index("month")
        if d.empty:
            raise ValueError(f"climate_deltas içinde senaryo yok: {scenario.cmip6}")
        months = out.index.month
        out["tmax"] = out["tmax"] + d["dtmax"].reindex(months).to_numpy()
        out["tmin"] = out["tmin"] + d["dtmin"].reindex(months).to_numpy()
        out["precip"] = out["precip"] * d["precip_ratio"].reindex(months).to_numpy()
    if scenario.d_temp_c:
        out["tmax"] = out["tmax"] + scenario.d_temp_c
        out["tmin"] = out["tmin"] + scenario.d_temp_c
    if scenario.precip_pct:
        out["precip"] = out["precip"] * (1 + scenario.precip_pct / 100)
    out["tmean"] = (out["tmax"] + out["tmin"]) / 2
    # Isınan havada bağıl nem bir miktar düşer (sabit mutlak nem varsayımı, kaba)
    dt_total = (out["tmean"] - climate["tmean"]).to_numpy()
    out["rh"] = np.clip(climate["rh"].to_numpy() * np.exp(-0.06 * dt_total), 5, 100)
    return out
