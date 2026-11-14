"""Ürün takvimi ve FAO-56 bitki katsayısı (Kc) eğrisi.

FAO-56 Bölüm 6: dört gelişim dönemi (başlangıç, gelişme, orta, son) ve
doğrusal geçişlerle günlük Kc eğrisi.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from ..data.basins import Basin
from ..knowledge.tables import Crop, Economics


@dataclass(frozen=True)
class Season:
    crop_id: str
    harvest_year: int
    start: date
    end: date            # dahil
    kc: np.ndarray       # günlük Kc
    stage: np.ndarray    # 0=ini 1=dev 2=mid 3=late

    @property
    def days(self) -> int:
        return len(self.kc)


def stage_lengths(crop: Crop, econ: Economics | None = None) -> tuple[int, int, int, int]:
    """Dönem uzunlukları (gün). Havzaya özgü ``season_scale`` uygulanır
    (ör. Pencap'ta buğday Konya'dan çok daha kısa sürede hasat edilir)."""
    k = econ.season_scale if econ is not None else 1.0
    return tuple(max(1, int(round(x * k))) for x in (crop.l_ini, crop.l_dev, crop.l_mid, crop.l_late))


def kc_curve(crop: Crop, econ: Economics | None = None) -> tuple[np.ndarray, np.ndarray]:
    """FAO-56 Şekil 34 tipi Kc eğrisi ve dönem etiketleri."""
    if crop.is_fallow or crop.season_days == 0:
        return np.zeros(0), np.zeros(0, dtype=int)
    l_ini, l_dev, l_mid, l_late = stage_lengths(crop, econ)
    ini = np.full(l_ini, crop.kc_ini)
    dev = np.linspace(crop.kc_ini, crop.kc_mid, l_dev + 2)[1:-1]
    mid = np.full(l_mid, crop.kc_mid)
    late = np.linspace(crop.kc_mid, crop.kc_end, l_late + 1)[1:]
    kc = np.concatenate([ini, dev, mid, late])
    stage = np.concatenate([
        np.zeros(l_ini, int), np.ones(l_dev, int), np.full(l_mid, 2), np.full(l_late, 3),
    ])
    return kc, stage


def season_for(crop: Crop, econ: Economics, basin: Basin, harvest_year: int) -> Season | None:
    """Belirli hasat yılı için ürün sezonu. Nadas için None."""
    if crop.is_fallow:
        return None
    start = basin.planting_date(harvest_year, econ.plant_month, econ.plant_day)
    kc, stage = kc_curve(crop, econ)
    end = start + timedelta(days=len(kc) - 1)
    return Season(crop.id, harvest_year, start, end, kc, stage)


def covered_months(crop: Crop, econ: Economics, basin: Basin) -> np.ndarray:
    """Takvim ayı bazında (1..12) toprağın örtülü olduğu aylar (bool[12]).

    Bitki gelişme+orta dönemindeyken ya da hasat sonrası anız/artık örtüsü
    sürerken örtülü sayılır. Yonca (residue_cover_months=12) yıl boyu örtülü.
    """
    cov = np.zeros(12, dtype=bool)
    if crop.is_fallow:
        return cov
    if crop.residue_cover_months >= 12:
        cov[:] = True
        return cov
    ref_year = 2010
    s = season_for(crop, econ, basin, ref_year)
    covered_from = s.start + timedelta(days=stage_lengths(crop, econ)[0] // 2)
    covered_to = s.end + timedelta(days=30 * crop.residue_cover_months)
    d = covered_from
    while d <= covered_to:
        cov[d.month - 1] = True
        d += timedelta(days=15)
    return cov
