"""Ürün uygunluk taraması: "Başka bölgelerin ürünleri bu tarlada olur mu?"

Seçili tarlada ürün tablosundaki BÜTÜN ürünler (havzanın plan listesinde olmayanlar dahil:
pamuk, çeltik, domates, kanola…) aynı gerçek iklim serisiyle sınanır. Yalnızca agronomi
değerlendirilir; fiyat, pazar ve destek bilinmediği için kâr hesaplanmaz.

Yöntem
------
1. Isı yeterliliği (yalnızca havzada ekilmeyen ürünler için; yerel ürünler zaten yetişiyor):
   büyüme derece-günü GDD = Σ max(0, (Tmax+Tmin)/2 − Ttaban). Ekimden itibaren ürünün
   olgunluk ihtiyacı (tables/crop_suitability.csv → gdd_req) kaç günde birikir?
   Bu süre, ürünün sığabileceği pencereyle karşılaştırılır:
       yazlık ürün (referans bölgede ekim Mart–Temmuz): ekimden Ağustos sonrası ilk ağır dona (Tmin < −2 °C)
       kışlık ürün (ekim Ağustos–Şubat): ekimden ertesi 20 Temmuz'a (yaz sıcağı/hasat)
   ısı payı = pencere / gereken gün (ortanca, bütün yıllar).
2. Ekim tarihi: yerel üründe havzanın kendi tarihi; diğerlerinde referans bölgenin tarihi
   (yarımküre farkı 6 ay) ve −30…+30 günlük kaydırmalar denenir, en iyi sonuç seçilir.
3. Su dengesi ve iklim stresi: water.build_crop_year_table (FAO-56 + FAO-33 + sıcak/don/yağış).
   Yerel olmayan üründe gelişim dönemleri "gereken gün"e ölçeklenir.
   → sulu verim oranı (yalnızca iklim stresi), kuru verim oranı (su eksikliği × stres),
     net sulama ihtiyacı (mm = m³/da).
4. Hasat öncesi don: sezonun son 30 gününde Tmin < −2 °C olan gün (hassas dönem donuna eklenir).

Karar (eşikler varsayımdır):
   kırmızı  ısı payı < 1,0 (pencerede olgunlaşamıyor), ya da kötü yılda (p10) verim oranı < 0,60,
            ya da don ≥ 5 gün (ortanca)
   sarı     ısı payı < 1,1 (sınırda), ya da ortanca verim oranı < 0,85, ya da don ≥ 2 gün,
            ya da sulama referans bölgeden %25'ten fazla
   yeşil    diğerleri
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

import numpy as np
import pandas as pd

from ..data.basins import Basin
from ..knowledge.tables import Crop, Economics, load_crop_suitability, load_crops, load_economics
from .calendar import stage_lengths
from .water import build_crop_year_table

OFFSETS = (-30, -15, 0, 15, 30)
MAX_SEASON_DAYS = 330
HARD_FROST_C = -2.0
WINTER_DEADLINE = (7, 20)        # kışlık ürün en geç 20 Temmuz'da hasat
RED_HEAT, YELLOW_HEAT = 1.0, 1.1
RED_P10_YIELD, YELLOW_MED_YIELD = 0.60, 0.85
RED_FROST, YELLOW_FROST = 5, 2
WATER_RATIO_YELLOW = 1.25


@dataclass
class Suitability:
    crop_id: str
    native: bool                 # havzanın plan listesinde mi
    home_site: str
    plant_md: tuple[int, int]    # (ay, gün)
    season_days: int
    home_season_days: int
    days_needed: float           # olgunluk için gereken gün (yerel üründe sezon uzunluğu)
    window_days: float           # sığabileceği pencere
    heat_margin: float           # pencere / gereken (yerel üründe nan)
    yield_med: float             # sulu (tam su) verim oranı, ortanca
    yield_p10: float             # kötü yıl (p10)
    rainfed_med: float           # kuru tarım verim oranı, ortanca
    heat_days: float
    frost_days: float            # hassas dönem + hasat öncesi don (ortanca)
    water_mm: float              # net sulama ihtiyacı, ortanca (mm = m³/da)
    home_water_mm: float
    verdict: str                 # green | yellow | red
    reasons: list[str]           # gerekçe kodları

    @property
    def matures(self) -> bool:
        return self.native or (np.isfinite(self.heat_margin) and self.heat_margin >= RED_HEAT)


def _shift_md(month: int, day: int, offset_days: int, months: int = 0) -> tuple[int, int]:
    d = date(2001, month, min(day, 28)) + timedelta(days=offset_days)
    m = (d.month - 1 + months) % 12 + 1
    return m, d.day


def _season_len(crop: Crop, econ: Economics) -> int:
    return int(sum(stage_lengths(crop, econ)))


def _years(clim: pd.DataFrame) -> list[int]:
    return list(range(clim.index[0].year + 1, clim.index[-1].year))


def _is_summer(md: tuple[int, int], southern: bool) -> bool:
    m = (md[0] + 6 - 1) % 12 + 1 if southern else md[0]
    return 3 <= m <= 7


def heat_check(clim: pd.DataFrame, basin: Basin, md: tuple[int, int], gdd_req: float, tbase: float,
               years: list[int], summer: bool | None = None) -> tuple[float, float]:
    """(gereken gün, pencere gün) — ortanca. Olgunlaşamayan yıl MAX_SEASON_DAYS+1 sayılır.
    summer: ürün tipi (yazlık/kışlık); verilmezse ekim ayından çıkarılır."""
    tmean = ((clim["tmax"] + clim["tmin"]) / 2).astype(float)
    tmin = clim["tmin"].astype(float)
    if summer is None:
        summer = _is_summer(md, basin.is_southern)
    need, win = [], []
    for y in years:
        start = pd.Timestamp(basin.planting_date(y, *md))
        seg = tmean.loc[start:start + pd.Timedelta(days=MAX_SEASON_DAYS)]
        if len(seg) < 200:
            continue
        cum = np.cumsum(np.clip(seg.to_numpy() - tbase, 0, None))
        hit = np.flatnonzero(cum >= gdd_req)
        need.append(float(hit[0] + 1) if hit.size else float(MAX_SEASON_DAYS + 1))
        if summer:
            mid = pd.Timestamp(start.year, 2 if basin.is_southern else 8, 1)
            if mid < start:
                mid = start + pd.Timedelta(days=60)
            frost = tmin.loc[mid:mid + pd.Timedelta(days=200)]
            hard = frost[frost < HARD_FROST_C]
            end = hard.index[0] if len(hard) else mid + pd.Timedelta(days=200)
        else:
            m, d = WINTER_DEADLINE
            if basin.is_southern:
                m = (m + 6 - 1) % 12 + 1
            end = pd.Timestamp(start.year, m, d)
            while end <= start + pd.Timedelta(days=60):
                end = pd.Timestamp(end.year + 1, m, d)
        win.append(float((end - start).days))
    if not need:
        return float("nan"), float("nan")
    return float(np.median(need)), float(np.median(win))


def evaluate_crop(crop_id: str, clim: pd.DataFrame, et0: pd.Series, basin: Basin, taw_mm_per_m: float,
                  home: dict, irrigated: bool) -> Suitability | None:
    """home: {"clim", "et0", "basin", "econ", "taw"} — ürünün referans bölgesi."""
    crop = load_crops()[crop_id]
    if crop.is_fallow or crop.residue_cover_months >= 12:
        return None
    meta = load_crop_suitability().loc[crop_id]
    tbase, gdd_req = float(meta["tbase_c"]), float(meta["gdd_req"])
    target_econ = load_economics(basin.id)
    native = crop_id in target_econ
    h_econ: Economics = home["econ"][crop_id]
    h_len = _season_len(crop, h_econ)

    if native:
        candidates = [(target_econ[crop_id].plant_month, target_econ[crop_id].plant_day)]
    else:
        hemi = 6 if basin.is_southern != home["basin"].is_southern else 0
        candidates = [_shift_md(h_econ.plant_month, h_econ.plant_day, o, hemi) for o in OFFSETS]

    yrs = _years(clim)
    tmin = clim["tmin"].astype(float)
    best = None
    for md in candidates:
        if native:
            econ_c = target_econ[crop_id]
            need = float(_season_len(crop, econ_c))
            window, margin = need, float("nan")
        else:
            need, window = heat_check(clim, basin, md, gdd_req, tbase, yrs,
                                      summer=_is_summer((h_econ.plant_month, h_econ.plant_day), home["basin"].is_southern))
            if not np.isfinite(need):
                continue
            margin = window / need
            scale = h_econ.season_scale * float(np.clip(need / h_len, 0.6, MAX_SEASON_DAYS / h_len))
            econ_c = replace(h_econ, plant_month=md[0], plant_day=md[1], season_scale=scale)
        season = _season_len(crop, econ_c)
        try:
            tbl = build_crop_year_table(clim, et0, basin, {crop_id: crop}, {crop_id: econ_c}, [crop_id],
                                        taw_mm_per_m, range(yrs[0], yrs[-1] + 1), None,
                                        heat_ref_tmax=clim["tmax"])
        except ValueError:
            continue
        stress = tbl.stress_mult[0]
        ratio = np.divide(tbl.eta_rf[0], tbl.etc[0], out=np.ones_like(tbl.etc[0]), where=tbl.etc[0] > 0)
        rainfed = np.clip(1 - crop.ky * (1 - ratio), 0, 1) * stress
        late = []
        for y in tbl.years:
            end = pd.Timestamp(basin.planting_date(int(y), *md)) + pd.Timedelta(days=season - 1)
            late.append(float((tmin.loc[end - pd.Timedelta(days=29):end] < HARD_FROST_C).sum()))
        frost = float(np.median(tbl.frost_days[0] + np.array(late)))
        yv = stress if irrigated else rainfed
        cand = dict(md=md, season=season, need=need, window=window, margin=margin, stress=stress,
                    rainfed=rainfed, frost=frost, heat=float(np.median(tbl.heat_days[0])),
                    water=float(np.median(tbl.ir_net[0])))
        heat_pen = 0.0 if native else max(0.0, YELLOW_HEAT - margin)
        score = float(np.median(yv)) - 2.0 * heat_pen - 0.05 * frost
        if best is None or score > best[0] + 1e-9 or (abs(score - best[0]) < 1e-9 and cand["water"] < best[1]["water"]):
            best = (score, cand)
    if best is None:
        return None
    c = best[1]
    try:
        yrs_h = _years(home["clim"])
        htbl = build_crop_year_table(home["clim"], home["et0"], home["basin"], {crop_id: crop}, {crop_id: h_econ},
                                     [crop_id], home["taw"], range(yrs_h[0], yrs_h[-1] + 1), None,
                                     heat_ref_tmax=home["clim"]["tmax"])
        home_water = float(np.median(htbl.ir_net[0]))
    except ValueError:
        home_water = float("nan")

    yv = c["stress"] if irrigated else c["rainfed"]
    y_med, y_p10 = float(np.median(yv)), float(np.percentile(yv, 10))
    reasons = []
    if not native:
        if c["margin"] < RED_HEAT:
            reasons.append("heat_short")
        elif c["margin"] < YELLOW_HEAT:
            reasons.append("heat_tight")
    if "heat_short" not in reasons:
        if y_p10 < RED_P10_YIELD:
            reasons.append("bad_years")
        elif y_med < YELLOW_MED_YIELD:
            reasons.append("stress")
        if c["frost"] >= RED_FROST:
            reasons.append("frost_high")
        elif c["frost"] >= YELLOW_FROST:
            reasons.append("frost")
        if irrigated and np.isfinite(home_water) and home_water > 0 and c["water"] > WATER_RATIO_YELLOW * home_water:
            reasons.append("water_more")
    if any(r in ("heat_short", "bad_years", "frost_high") for r in reasons):
        verdict = "red"
    elif reasons:
        verdict = "yellow"
    else:
        verdict = "green"
    return Suitability(
        crop_id=crop_id, native=native, home_site=str(meta["home_site"]), plant_md=c["md"],
        season_days=int(c["season"]), home_season_days=int(h_len), days_needed=float(c["need"]),
        window_days=float(c["window"]), heat_margin=float(c["margin"]),
        yield_med=y_med, yield_p10=y_p10, rainfed_med=float(np.median(c["rainfed"])),
        heat_days=c["heat"], frost_days=c["frost"], water_mm=c["water"], home_water_mm=home_water,
        verdict=verdict, reasons=reasons,
    )


def screen_crops(site_clim: pd.DataFrame, site_et0: pd.Series, basin: Basin, taw_mm_per_m: float,
                 homes: dict[str, dict], irrigated: bool) -> list[Suitability]:
    """homes: home_site → {"clim", "et0", "basin", "econ", "taw"}."""
    meta = load_crop_suitability()
    out = []
    for cid in meta.index:
        h = homes.get(str(meta.loc[cid, "home_site"]))
        if h is None or cid not in h["econ"]:
            continue
        r = evaluate_crop(cid, site_clim, site_et0, basin, taw_mm_per_m, h, irrigated)
        if r is not None:
            out.append(r)
    order = {"green": 0, "yellow": 1, "red": 2}
    out.sort(key=lambda s: (order[s.verdict], not s.native, -s.yield_med))
    return out


def home_sites() -> list[tuple[str, str]]:
    """(havza, konum) — referans bölgeler."""
    meta = load_crop_suitability()
    return sorted({(str(r["home_basin"]), str(r["home_site"])) for _, r in meta.iterrows()})
