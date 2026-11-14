"""Toprak sağlığı alt skorları ve yem değeri (plan bazında, vektörel).

Toprak sağlığı uydudan ÖLÇÜLMEZ; planın içeriğinden kural tabanlı puanlanır.
Her alt skor 0–100; katsayılar varsayımdır ve arayüzde öyle etiketlenir.

    azot bağlama      100 · min(1, baklagil yılı / 2)
    organik madde     100 · ortalama(ürün organik madde katkısı) + örtü bitkisi bonusu
    erozyon/çıplak    100 · (1 − ortalama çıplak ay / 12), eğim > 2° ise ceza büyür
    zararlı döngüsü   100 − 25 · (ara verme ihlali) − 10 · (aynı aile art arda)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..data.basins import Basin
from ..knowledge.tables import Crop, Economics
from .calendar import covered_months

COVER_CROP = {
    "water_mm": 60.0,            # örtü bitkisinin sonraki ürüne kalan sudan tükettiği (varsayım)
    "cost_share_of_wheat": 0.12,  # tohum + ekim maliyeti, buğday maliyetinin oranı (varsayım)
    "om_bonus": 15.0,
    "bare_month_reduction": 3,
}
SUBSCORES = ("nitrogen", "organic_matter", "erosion", "pest_cycle")


@dataclass
class CropAttrArrays:
    n_fix: np.ndarray
    om: np.ndarray
    bare_months: np.ndarray
    forage: np.ndarray
    cover_ok: np.ndarray   # hasadı yaz ortasından önce olan ürünler (örtü bitkisine yer var)


def crop_attr_arrays(crop_ids: list[str], crops: dict[str, Crop], econ: dict[str, Economics],
                     basin: Basin) -> CropAttrArrays:
    from .calendar import season_for

    n = len(crop_ids)
    n_fix, om, bare, forage, cover_ok = (np.zeros(n) for _ in range(5))
    for i, cid in enumerate(crop_ids):
        c = crops[cid]
        n_fix[i] = 1.0 if c.n_fixing else 0.0
        om[i] = c.om_score
        bare[i] = 12 - covered_months(c, econ[cid], basin).sum()
        forage[i] = c.forage_kg_dm_da
        if not c.is_fallow and c.residue_cover_months < 12:
            s = season_for(c, econ[cid], basin, 2010)
            # hasat ile bir sonraki ana ürün arasında ≥ 90 gün boşluk kalıyorsa
            harvest_doy = s.end.timetuple().tm_yday
            cover_ok[i] = 1.0 if (harvest_doy < 225 if not basin.is_southern else harvest_doy > 290 or harvest_doy < 40) else 0.0
    return CropAttrArrays(n_fix, om, bare, forage, cover_ok)


def soil_scores(plans: np.ndarray, attrs: CropAttrArrays, gap_viol: np.ndarray, family_viol: np.ndarray,
                slope_deg: float, cover: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """(P,) dizileri: dört alt skor, genel skor, yem (kg KM/da/yıl)."""
    legume_years = attrs.n_fix[plans].sum(axis=1)
    nitrogen = 100 * np.minimum(1.0, legume_years / 2)
    om = 100 * attrs.om[plans].mean(axis=1)
    bare = attrs.bare_months[plans].astype(float)
    if cover is not None:
        om = om + COVER_CROP["om_bonus"] * cover.mean(axis=1)
        bare = np.maximum(0, bare - COVER_CROP["bare_month_reduction"] * cover)
    erosion = 100 * (1 - bare.mean(axis=1) / 12)
    slope_factor = 1 + max(0.0, slope_deg - 2.0) * 0.15
    erosion = 100 - (100 - erosion) * slope_factor
    pest = 100 - 25 * gap_viol.sum(axis=1) - 10 * family_viol.sum(axis=1)
    out = {
        "nitrogen": np.clip(nitrogen, 0, 100),
        "organic_matter": np.clip(om, 0, 100),
        "erosion": np.clip(erosion, 0, 100),
        "pest_cycle": np.clip(pest, 0, 100),
    }
    out["soil"] = np.mean([out[k] for k in SUBSCORES], axis=0)
    out["forage"] = attrs.forage[plans].mean(axis=1)
    out["bare_months"] = bare.mean(axis=1)
    return out
