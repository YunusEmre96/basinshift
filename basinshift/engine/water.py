"""Ürün-yıl tablosu: her ürünün her hasat yılındaki su dengesi ve iklim stresi.

Bu tablo bir kez hesaplanır; binlerce planın stres testi bu tablodan
vektörel olarak okunur.

Yöntem — FAO-56 günlük kök bölgesi su dengesi (Bölüm 8, tek katsayılı Kc):
    Kapasite   TAW = toprak kullanılabilir suyu (mm/m) × kök derinliği
    Başlangıç  S0  = TAW × ıslaklık oranı
               ıslaklık: SMAP kök bölgesi nemi (2015+) varsa ondan; yoksa
               ekim öncesi 90 günlük yağışın klimatolojiye oranından
    Günlük     S ← min(TAW, S + P − yüzey akışı)
               ETc = Kc · ET0
               Kuru tarım: Ks = 1 (S ≥ RAW sınırı) ya da S / sınır;  ETa = Ks · ETc
               Tam sulu:   S RAW sınırının altına düşünce TAW'a kadar sulanır
    Çıktılar   ETc toplamı, kuru tarım ETa'sı, tam sulama için net su (IRnet),
               ürünün kullandığı yağış.
    Sınırlı su altında ETa, kuru tarım ETa'sı ile ETc arasında uygulanan
    suyla doğrusal kabul edilir (field.py).

İklim stresi çarpanı (varsayım katsayıları):
    sıcak stresi  : hassas dönemde (orta) Tmax > max(ürün eşiği, o günün yerel 90. yüzdeliği)
                    olan her gün −%1.5 (yerel çeşitler bölgenin olağan sıcağına uyumlu
                    kabul edilir; stres OLAĞANDIŞI sıcakta sayılır)
    don           : hassas dönemde Tmin < eşik olan her gün          −%3
    aşırı yağış   : hasat döneminde (son) günlük yağış > 25 mm       −%2
    toplam kayıp en fazla %50
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd

from ..data.basins import Basin
from ..knowledge.tables import Crop, Economics
from .calendar import season_for

IRRIGATION_EFFICIENCY = {"drip": 0.90, "sprinkler": 0.75, "surface": 0.60, "none": 1.0}
DEPLETION_FRACTION = {"potato": 0.35, "tomato": 0.40, "rice": 0.20}   # FAO-56 Tablo 22; diğerleri 0.5
HEAT_PENALTY_PER_DAY = 0.015
FROST_PENALTY_PER_DAY = 0.03
WET_HARVEST_PENALTY_PER_DAY = 0.02
MAX_STRESS_LOSS = 0.5
FALLOW_STORAGE_EFFICIENCY = 0.20
HEAVY_RAIN_MM = 25.0
RUNOFF_THRESHOLD_MM = 25.0
RUNOFF_FRACTION = 0.3


@dataclass
class CropYearTable:
    crop_ids: list[str]
    years: np.ndarray              # (Y,) hasat yılları
    etc: np.ndarray                # (C, Y) mm — ürün su ihtiyacı
    eta_rf: np.ndarray             # (C, Y) mm — sulamasız gerçekleşen ET
    ir_net: np.ndarray             # (C, Y) mm — tam sulama için net su
    rain_used: np.ndarray          # (C, Y) mm — ürünün kullandığı yağış (etkili yağış)
    s0: np.ndarray                 # (C, Y) mm — ekimde kök bölgesindeki su
    taw: np.ndarray                # (C,) mm — kök bölgesi kapasitesi
    stress_mult: np.ndarray        # (C, Y) 0..1
    heat_days: np.ndarray          # (C, Y)
    frost_days: np.ndarray         # (C, Y)
    wet_harvest_days: np.ndarray   # (C, Y)
    season_precip: np.ndarray      # (C, Y) mm
    fallow_store: np.ndarray       # (Y,) mm — o yıl nadas olursa sonraki ürüne kalan su
    ag_year_precip: np.ndarray     # (Y,) mm
    wetness_source: str            # "SMAP" | "yağış göstergesi" | "SMAP+yağış göstergesi"
    dropped_years: list[int]       # sezonunda verinin >%5'i eksik olduğu için çıkarılan yıllar

    def index(self, crop_id: str) -> int:
        return self.crop_ids.index(crop_id)


def _bucket(p: np.ndarray, etc_d: np.ndarray, taw: float, s0: float, dep: float) -> tuple[float, float, float]:
    """Tek sezon için (kuru tarım ETa, tam sulama IRnet, kullanılan yağış)."""
    thr = (1 - dep) * taw
    runoff = np.maximum(p - RUNOFF_THRESHOLD_MM, 0) * RUNOFF_FRACTION
    infil = p - runoff
    # Kuru tarım
    s = s0
    eta = 0.0
    for i in range(len(p)):
        s = min(taw, s + infil[i])
        ks = 1.0 if s >= thr else (s / thr if thr > 0 else 0.0)
        e = ks * etc_d[i]
        s = max(0.0, s - e)
        eta += e
    # Tam sulama (RAW sınırında TAW'a kadar doldur)
    s = s0
    irr = 0.0
    drain = 0.0
    for i in range(len(p)):
        s += infil[i]
        if s > taw:
            drain += s - taw
            s = taw
        s -= etc_d[i]
        if s < thr:
            irr += taw - s
            s = taw
    rain_used = float(infil.sum() - drain - max(0.0, s - s0))
    return float(eta), float(irr), max(0.0, rain_used)


def build_crop_year_table(
    climate: pd.DataFrame,
    et0: pd.Series,
    basin: Basin,
    crops: dict[str, Crop],
    econ: dict[str, Economics],
    crop_ids: list[str],
    taw_mm_per_m: float,
    years: range,
    soil_moisture: pd.DataFrame | None = None,
    heat_ref_tmax: pd.Series | None = None,
) -> CropYearTable:
    """heat_ref_tmax: sıcak stresi referansı için TEMEL (senaryosuz) Tmax serisi.
    Verilmezse ``climate`` kullanılır. Senaryo çalışırken temel seri verilmelidir;
    aksi halde ısınma, "olağandışı sıcak" eşiğini de kaydırıp etkisini gizler."""
    dates = climate.index
    t0 = dates[0]
    # Eksik gün maskesi: yağış, Tmax veya ET0 olmayan günler (kısa boşluklar dışında)
    missing = (climate["precip"].isna() | climate["tmax"].isna() | et0.reindex(dates).isna()).to_numpy()
    p_arr = np.nan_to_num(climate["precip"].to_numpy(float), nan=0.0)
    tmax_arr = climate["tmax"].to_numpy(float)
    tmin_arr = climate["tmin"].to_numpy(float)
    et0_arr = np.nan_to_num(et0.reindex(dates).to_numpy(float), nan=0.0)
    data_end = dates[-1]
    # Gün-yıl bazında yerel Tmax 90. yüzdeliği (±15 gün pencere)
    tmax_s = (heat_ref_tmax.reindex(dates) if heat_ref_tmax is not None else pd.Series(tmax_arr, index=dates))
    doy_p90 = tmax_s.groupby(dates.dayofyear).quantile(0.9).reindex(range(1, 367)).interpolate()
    doy_p90 = pd.Series(np.convolve(np.r_[doy_p90.values[-15:], doy_p90.values, doy_p90.values[:15]],
                                    np.ones(31) / 31, mode="valid"), index=range(1, 367))
    heat_ref = doy_p90.reindex(dates.dayofyear).to_numpy()

    p90 = pd.Series(p_arr, index=dates).rolling(90, min_periods=60).sum()
    clim_p90 = p90.groupby(p90.index.dayofyear).transform("mean")
    proxy = np.nan_to_num(((p90 / clim_p90.replace(0, np.nan)).clip(0.1, 2.0) * 0.5).to_numpy(), nan=0.5)
    smap_rel = None
    if soil_moisture is not None and len(soil_moisture) > 365:
        rz = soil_moisture["sm_rootzone"].astype(float)
        lo, hi = rz.quantile(0.05), rz.quantile(0.95)
        if hi > lo:
            smap_rel = ((rz - lo) / (hi - lo)).clip(0, 1).reindex(dates)
    used_smap = used_proxy = False

    valid_years, dropped = [], []
    for y in years:
        ok = True
        gap = False
        for c in crop_ids:
            if crops[c].is_fallow:
                continue
            s = season_for(crops[c], econ[c], basin, y)
            if pd.Timestamp(s.start) - timedelta(days=95) < t0 or pd.Timestamp(s.end) > data_end:
                ok = False
                break
            i0 = (pd.Timestamp(s.start) - t0).days
            if missing[i0:i0 + s.days].mean() > 0.05:
                gap = True
        if ok and not gap:
            valid_years.append(y)
        elif ok and gap:
            dropped.append(int(y))
    if len(valid_years) < 8:
        raise ValueError(f"Stres testi için yeterli yıl yok ({len(valid_years)}); veri aralığını kontrol edin")
    yrs = np.array(valid_years)
    n_c, n_y = len(crop_ids), len(yrs)
    shape = (n_c, n_y)
    etc, eta_rf, ir_net, rain_used, s0 = (np.zeros(shape) for _ in range(5))
    stress = np.ones(shape)
    heat, frost, wet, sp = (np.zeros(shape) for _ in range(4))
    taw = np.zeros(n_c)

    for ci, cid in enumerate(crop_ids):
        crop = crops[cid]
        if crop.is_fallow:
            continue
        taw[ci] = taw_mm_per_m * crop.root_depth_m
        dep = DEPLETION_FRACTION.get(cid, 0.5)
        for yi, y in enumerate(yrs):
            s = season_for(crop, econ[cid], basin, int(y))
            i0 = (pd.Timestamp(s.start) - t0).days
            sl = slice(i0, i0 + s.days)
            etc_d = s.kc * et0_arr[sl]
            p = p_arr[sl]
            w = None
            if smap_rel is not None:
                v = smap_rel.iloc[i0]
                if not np.isnan(v):
                    w = float(v)
                    used_smap = True
            if w is None:
                w = float(min(proxy[i0], 1.0))
                used_proxy = True
            s0[ci, yi] = taw[ci] * w
            etc[ci, yi] = float(etc_d.sum())
            eta_rf[ci, yi], ir_net[ci, yi], rain_used[ci, yi] = _bucket(p, etc_d, taw[ci], s0[ci, yi], dep)
            sp[ci, yi] = float(p.sum())

            st = s.stage
            mid = st == 2
            thr = np.maximum(crop.heat_thr_c, heat_ref[sl][mid])
            heat[ci, yi] = float((tmax_arr[sl][mid] > thr).sum())
            if crop.frost_stage == "mid":
                fz = np.zeros_like(st, dtype=bool)
                fz[np.flatnonzero(mid)[:30]] = True
            else:
                dev_idx = np.flatnonzero(st == 1)
                fz = st == 0
                fz[dev_idx[: len(dev_idx) // 2]] = True
            frost[ci, yi] = float((tmin_arr[sl][fz] < crop.frost_thr_c).sum())
            wet[ci, yi] = float((p[st == 3] > HEAVY_RAIN_MM).sum())
            loss = (heat[ci, yi] * HEAT_PENALTY_PER_DAY + frost[ci, yi] * FROST_PENALTY_PER_DAY
                    + wet[ci, yi] * WET_HARVEST_PENALTY_PER_DAY)
            stress[ci, yi] = 1.0 - min(loss, MAX_STRESS_LOSS)

    ag = np.where(dates.month >= basin.ag_year_start_month, dates.year + 1, dates.year)
    ag_p = pd.Series(p_arr, index=ag).groupby(level=0).sum()
    ag_year_precip = np.array([ag_p.get(int(y), np.nan) for y in yrs])
    fallow_store = FALLOW_STORAGE_EFFICIENCY * np.nan_to_num(ag_year_precip, nan=0.0)

    src = "SMAP+yağış göstergesi" if used_smap and used_proxy else ("SMAP" if used_smap else "yağış göstergesi")
    return CropYearTable(
        crop_ids=list(crop_ids), years=yrs, etc=etc, eta_rf=eta_rf, ir_net=ir_net, rain_used=rain_used,
        s0=s0, taw=taw, stress_mult=stress, heat_days=heat, frost_days=frost, wet_harvest_days=wet,
        season_precip=sp, fallow_store=fallow_store, ag_year_precip=ag_year_precip, wetness_source=src,
        dropped_years=dropped,
    )
