"""Sentetik veri sağlayıcısı (DEMO).

Gerçek NASA veri setleriyle BİREBİR AYNI şemada, fiziksel olarak tutarlı ama
UYDURMA veri üretir. Amaç: NASA verisi bağlanmadan önce tüm hesapları ve
arayüzü çalıştırmak. Arayüz bu kaynak kullanıldığında açıkça "SENTETİK"
uyarısı gösterir; sonuçlar gerçek dünya iddiası olarak sunulmamalıdır.

Üretim deterministiktir (aynı nokta → aynı veri), böylece demo tekrarlanabilir.
"""
from __future__ import annotations

import zlib
from datetime import date
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.signal import lfilter

from ...engine.solar import clear_sky_radiation, extraterrestrial_radiation
from ..basins import Basin, Site
from .base import DataProvider

SYN_START = date(1981, 1, 1)
SYN_END = date(2026, 6, 30)
MID_MONTH_DOY = np.array([15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349])


def _interp_monthly(values, doy: np.ndarray) -> np.ndarray:
    """Ay ortası değerlerinden günlük (periyodik) doğrusal interpolasyon."""
    vals = np.asarray(values, dtype=float)
    x = np.concatenate([MID_MONTH_DOY - 365, MID_MONTH_DOY, MID_MONTH_DOY + 365])
    y = np.concatenate([vals, vals, vals])
    return np.interp(doy, x, y)


def _ag_year_label(dates: pd.DatetimeIndex, start_month: int) -> np.ndarray:
    return np.where(dates.month >= start_month, dates.year + 1, dates.year)


@lru_cache(maxsize=32)
def _climate_full(site: Site, basin: Basin) -> pd.DataFrame:
    p = basin.synthetic
    rng = np.random.default_rng(site.seed)
    dates = pd.date_range(SYN_START, SYN_END, freq="D")
    n = len(dates)
    doy = dates.dayofyear.values
    month = dates.month.values - 1
    yearfrac = dates.year.values + doy / 365.25

    # --- Yağış: Markov zinciri + gama dağılımı, yıl çarpanı ve kurak yıllar ---
    ag_label = _ag_year_label(dates, basin.ag_year_start_month)
    labels = np.unique(ag_label)
    dry = {int(k): float(v) for k, v in (p.get("dry_years") or {}).items()}
    mult_by_label = {lab: float(np.exp(rng.normal(0, 0.18))) * dry.get(int(lab), 1.0) for lab in labels}
    mult = np.array([mult_by_label[lab] for lab in ag_label])

    pm = np.asarray(p["precip"], float) * site.precip_factor
    wd = np.maximum(np.asarray(p["wet_days"], float), 0.2)
    dim = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    p_wet = np.clip(wd[month] / dim[month] * np.sqrt(mult), 0.005, 0.9)
    mean_amt = (pm[month] / wd[month]) * np.sqrt(mult)
    u = rng.random(n)
    wet = np.zeros(n, dtype=bool)
    for i in range(n):
        pw = p_wet[i]
        if i and wet[i - 1]:
            pw = min(0.95, pw + 0.3 * (1 - pw))
        else:
            pw = pw * 0.85
        wet[i] = u[i] < pw
    shape = 0.75
    amounts = rng.gamma(shape, mean_amt / shape)
    precip = np.where(wet, amounts, 0.0)

    # --- Sıcaklık: klimatoloji + ısınma eğilimi + yıl anomalisi + AR(1) ---
    t_clim = _interp_monthly(p["tmean"], doy)
    trend = p.get("warming_per_year", 0.03) * (yearfrac - 2003)
    year_anom_map = {y: rng.normal(0, 0.5) for y in np.unique(dates.year)}
    year_anom = np.array([year_anom_map[y] for y in dates.year])
    ar = lfilter([1.0], [1.0, -0.75], rng.normal(0, 2.5 * np.sqrt(1 - 0.75**2), n))
    dry_heat = np.where((mult < 0.75) & np.isin(month, [5, 6, 7, 8]), 0.8, 0.0)
    tmean = t_clim + trend + year_anom + ar + dry_heat - np.where(wet, 1.0, 0.0)
    dtr = _interp_monthly(p["dtr"], doy) * np.where(wet, 0.65, 1.05) + rng.normal(0, 1.0, n)
    dtr = np.clip(dtr, 2.0, 25.0)
    tmax = tmean + dtr / 2
    tmin = tmean - dtr / 2

    # --- Nem, rüzgâr, radyasyon ---
    rh = _interp_monthly(p["rh"], doy) + np.where(wet, 12.0, -2.0) + rng.normal(0, 5, n)
    rh = np.clip(rh, 8, 100)
    wind = np.clip(p.get("wind", 2.0) * np.exp(rng.normal(0, 0.3, n)), 0.3, 12)
    ra = extraterrestrial_radiation(site.lat, doy)
    rso = clear_sky_radiation(ra, site.elevation_m)
    rs = rso * np.where(wet, rng.uniform(0.35, 0.65, n), rng.uniform(0.85, 1.0, n))

    return pd.DataFrame(
        {
            "tmax": tmax, "tmin": tmin, "tmean": (tmax + tmin) / 2, "rh": rh,
            "wind2m": wind, "rs": rs, "precip": precip,
        },
        index=pd.DatetimeIndex(dates, name="date"),
    )


def _slice(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    return df.loc[pd.Timestamp(start): pd.Timestamp(end)]


class SyntheticProvider(DataProvider):
    source = "synthetic"
    label_tr = "Sentetik (demo)"
    label_en = "Synthetic (demo)"

    def climate_daily(self, site, basin, start, end):
        return _slice(_climate_full(site, basin), start, end)

    def soil_moisture(self, site, basin, start, end):
        from ...engine.et0 import et0_from_climate

        clim = _climate_full(site, basin).loc["2015-03-31":]
        et0 = et0_from_climate(clim, site.lat, site.elevation_m).to_numpy()
        prec = clim["precip"].to_numpy()
        taw_r, taw_s = 150.0, 25.0
        s_r, s_s = taw_r * 0.5, taw_s * 0.5
        rz, sf = np.empty(len(clim)), np.empty(len(clim))
        for i in range(len(clim)):
            s_s = min(taw_s, s_s + prec[i])
            s_s = max(0.0, s_s - et0[i] * 0.8 * s_s / taw_s)
            s_r = min(taw_r, s_r + prec[i] * 0.8)
            s_r = max(0.0, s_r - et0[i] * 0.45 * s_r / taw_r)
            rz[i], sf[i] = s_r / taw_r, s_s / taw_s
        rng = np.random.default_rng(site.seed + 7)
        df = pd.DataFrame(
            {
                "sm_surface": np.clip(0.05 + 0.30 * sf + rng.normal(0, 0.01, len(sf)), 0.02, 0.5),
                "sm_rootzone": np.clip(0.12 + 0.20 * rz + rng.normal(0, 0.004, len(rz)), 0.05, 0.5),
            },
            index=clim.index,
        )
        return _slice(df, start, end)

    def ndvi(self, site, basin, start, end):
        from ...engine.calendar import season_for
        from ...knowledge.tables import load_crops, load_economics

        crops, econ = load_crops(), load_economics(basin.id)
        rng = np.random.default_rng(site.seed + 11)
        dates = pd.date_range("2000-01-01", SYN_END, freq="D")
        truth = np.full(len(dates), 0.16)
        spring = np.isin(dates.month, [3, 4, 5])
        truth[spring] += 0.05  # kendiliğinden çıkan ot
        hist = dict(site.synthetic_history) or {2020: "wheat", 2021: "fallow"}
        years_known = sorted(hist)
        peaks = {"cereal": 0.72, "legume": 0.62, "fallow": 0.0}
        for hy in range(2000, SYN_END.year + 1):
            crop_id = hist.get(hy) or hist[years_known[(hy - years_known[0]) % len(years_known)]]
            if crop_id not in econ or crops[crop_id].is_fallow:
                continue
            crop = crops[crop_id]
            s = season_for(crop, econ[crop_id], basin, hy)
            idx0 = (pd.Timestamp(s.start) - dates[0]).days
            if idx0 < 0 or idx0 >= len(dates):
                continue
            kc = s.kc
            green = np.clip((kc - kc.min()) / max(kc.max() - kc.min(), 1e-6), 0, 1)
            green[s.stage == 3] *= np.linspace(1, 0.3, (s.stage == 3).sum())
            peak = peaks.get(crop.family, 0.82 if site.irrigated else 0.65)
            seg = 0.16 + (peak - 0.16) * green
            idx1 = min(len(dates), idx0 + len(seg))
            truth[idx0:idx1] = np.maximum(truth[idx0:idx1], seg[: idx1 - idx0])

        truth_s = pd.Series(truth, index=dates)
        # HLS: 2013-04 sonrası ~3 günde bir, %30 bulut kaybı
        hls_dates = pd.date_range("2013-04-11", SYN_END, freq="3D")
        hls_dates = hls_dates[rng.random(len(hls_dates)) > 0.3]
        hls = truth_s.reindex(hls_dates).to_numpy() + rng.normal(0, 0.035, len(hls_dates))
        # MODIS: 16 günlük kompozit, karma piksel (çevreyle karışır)
        mod_dates = pd.date_range("2000-02-18", SYN_END, freq="16D")
        mod = 0.55 * truth_s.reindex(mod_dates).to_numpy() + 0.45 * 0.32 + rng.normal(0, 0.02, len(mod_dates))
        df = pd.concat([
            pd.DataFrame({"ndvi": np.clip(hls, -0.1, 0.95), "source": "HLS"}, index=hls_dates),
            pd.DataFrame({"ndvi": np.clip(mod, -0.1, 0.95), "source": "MODIS"}, index=mod_dates),
        ]).sort_index()
        df.index.name = "date"
        return _slice(df, start, end)

    def precip_satellite(self, site, basin, start, end):
        clim = _climate_full(site, basin).loc["2000-06-01":]
        rng = np.random.default_rng(site.seed + 13)
        p = clim["precip"].to_numpy()
        sat = np.where(p > 0, p * np.exp(rng.normal(0, 0.35, len(p))), 0.0)
        false_alarm = (p == 0) & (rng.random(len(p)) < 0.03)
        sat = sat + np.where(false_alarm, rng.uniform(0.3, 2.0, len(p)), 0.0)
        missed = (p > 0) & (p < 2) & (rng.random(len(p)) < 0.4)
        sat = np.where(missed, 0.0, sat)
        return _slice(pd.DataFrame({"precip": sat}, index=clim.index), start, end)

    def water_storage(self, basin):
        p = basin.synthetic
        rng = np.random.default_rng(zlib.crc32(basin.id.encode()))
        months = pd.date_range("2002-04-01", "2025-12-01", freq="MS")
        t = months.year + (months.month - 1) / 12
        peak = 9 if basin.is_southern else 4
        seasonal = p.get("grace_seasonal_cm", 3.0) * np.cos(2 * np.pi * (months.month - peak) / 12)
        trend = p.get("grace_trend_cm_per_year", -1.0) * (t - 2010)
        dry = {int(k): float(v) for k, v in (p.get("dry_years") or {}).items()}
        shock = np.zeros(len(months))
        level = 0.0
        for i, m in enumerate(months):
            if m.month == 1:
                level = 0.6 * level + (-6.0 * (1 - dry[m.year]) if m.year in dry else 0.0)
            shock[i] = level
        noise = lfilter([1.0], [1.0, -0.6], rng.normal(0, 0.8, len(months)))
        df = pd.DataFrame(
            {"tws_anomaly_cm": trend + seasonal + shock + noise, "uncertainty_cm": 1.5},
            index=pd.DatetimeIndex(months, name="date"),
        )
        gap = (df.index >= "2017-07-01") & (df.index <= "2018-05-01")  # gerçek GRACE→GRACE-FO boşluğu
        return df[~gap]

    def climate_deltas(self, site, basin):
        ratios = basin.synthetic.get("cmip6_precip_ratio", [0.93, 0.88])
        rows = []
        for scen, base_dt, extra, pr in (("ssp245", 1.5, 0.6, ratios[0]), ("ssp585", 2.1, 0.9, ratios[1])):
            for m in range(1, 13):
                summer_m = (m + 6 - 1) % 12 + 1 if basin.is_southern else m
                summerness = max(0.0, np.cos(2 * np.pi * (summer_m - 7) / 12))
                dt = base_dt + extra * summerness
                rows.append({
                    "month": m, "scenario": scen, "dtmax": dt + 0.2, "dtmin": dt - 0.1,
                    "precip_ratio": pr - 0.06 * summerness if pr < 1 else pr + 0.04 * summerness,
                })
        return pd.DataFrame(rows)

    def terrain(self, site, basin):
        rng = np.random.default_rng(site.seed + 17)
        return {"elevation_m": site.elevation_m,
                "slope_deg": float(basin.synthetic.get("slope_deg", 0.8) * rng.uniform(0.7, 1.3))}

    def soil_properties(self, site, basin):
        s = basin.synthetic.get("soil", {})
        return {
            "taw_mm_per_m": float(s.get("taw_mm_per_m", 150)),
            "clay_pct": float(s.get("clay_pct", 32)),
            "sand_pct": float(s.get("sand_pct", 28)),
            "soc_g_kg": float(s.get("soc_g_kg", 10)),
            "ph": float(s.get("ph", 7.8)),
        }
