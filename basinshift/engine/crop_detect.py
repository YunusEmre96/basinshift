"""'Geçmişini uydudan doğrula': NDVI zaman serisinden yıllık ürün tipi tahmini.

Basit, açıklanabilir eşik kuralı (makine öğrenmesi değil):
    Her hasat yılı için ilkbahar (Nis–May) ve yaz sonu (15 Tem–Ağu) NDVI tepe değerine bakılır
    (kışlık tahıllar Temmuz ortasına kadar hasat edildiği için yaz penceresi geç başlar).
        ilkbahar tepe ≥ 0.45 ve yaz tepe < 0.45  → kışlık/erken ürün (buğday, arpa, baklagil…)
        yaz tepe ≥ 0.45                          → yazlık ürün (pancar, mısır, ayçiçeği, patates…)
        ikisi de < 0.35                          → nadas / çıplak
        aksi halde                               → belirsiz
Güney yarımkürede mevsimler 6 ay kaydırılır.

Yalnızca ürün GRUBUNU (kışlık/yazlık/nadas) ayırt eder; tür ayrımı için
NASA–IBM Prithvi gibi bir model gerekir (yol haritası).
"""
from __future__ import annotations

import pandas as pd

from ..knowledge.tables import Crop

WINTER, SUMMER, FALLOW, UNKNOWN = "winter", "summer", "fallow", "unknown"


def crop_group(crop: Crop, plant_month: int, southern: bool = False) -> str:
    if crop.is_fallow:
        return FALLOW
    if crop.residue_cover_months >= 12:
        return SUMMER          # yonca: yazın da yeşil
    m = (plant_month + 6 - 1) % 12 + 1 if southern else plant_month
    return WINTER if m in (9, 10, 11, 12, 1, 2, 3) else SUMMER


def detect_groups(ndvi: pd.DataFrame, years: list[int], southern: bool = False) -> dict[int, dict]:
    src = ndvi[ndvi["source"] == "HLS"] if (ndvi["source"] == "HLS").sum() > 50 else ndvi
    out = {}
    for y in years:
        if southern:
            spring = src.loc[f"{y-1}-09-01":f"{y-1}-10-31", "ndvi"]
            summer = src.loc[f"{y}-01-15":f"{y}-02-28", "ndvi"]
        else:
            spring = src.loc[f"{y}-04-01":f"{y}-05-31", "ndvi"]
            summer = src.loc[f"{y}-07-15":f"{y}-08-31", "ndvi"]
        if len(spring) < 3 or len(summer) < 3:
            out[y] = {"group": UNKNOWN, "spring_peak": None, "summer_peak": None, "n_obs": len(spring) + len(summer)}
            continue
        sp, su = float(spring.quantile(0.9)), float(summer.quantile(0.9))
        if sp < 0.35 and su < 0.35:
            g = FALLOW
        elif su >= 0.45:
            g = SUMMER
        elif sp >= 0.45:
            g = WINTER
        else:
            g = UNKNOWN
        out[y] = {"group": g, "spring_peak": sp, "summer_peak": su, "n_obs": len(spring) + len(summer)}
    return out
