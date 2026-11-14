"""Canlı NASA (ve açık bilim) API'leri sağlayıcısı.

| Veri seti         | Kaynak                                   | Kimlik       | Test durumu                 |
|-------------------|------------------------------------------|--------------|-----------------------------|
| climate_daily     | NASA POWER günlük nokta API              | gerekmez     | ayrıştırıcı birim testli    |
| soil_moisture     | AppEEARS → SMAP L4 (SPL4SMGP)            | Earthdata    | canlı test edilmedi         |
| ndvi              | AppEEARS → HLS L30/S30 + MODIS MOD13Q1   | Earthdata    | canlı test edilmedi         |
| terrain           | AppEEARS → SRTM GL1 (5 nokta → eğim)     | Earthdata    | canlı test edilmedi         |
| water_storage     | CMR/PO.DAAC → GRACE(-FO) JPL Mascon      | Earthdata    | canlı test edilmedi         |
| climate_deltas    | NCCS THREDDS → NEX-GDDP-CMIP6            | gerekmez     | canlı test edilmedi         |
| soil_properties   | ISRIC SoilGrids REST                     | gerekmez     | canlı test edilmedi         |
| precip_satellite  | GPM IMERG → ``files`` kaynağı ile        | —            | bkz. docs/DATA_SWAP.md      |

"Canlı test edilmedi": geliştirme ortamında internet erişimi yoktu; kod resmi
API belgelerine göre yazıldı. Her biri hata verirse DataHub bunu arayüzde
açıkça gösterir ve (ayarlıysa) sentetik veriye geri düşer.
"""
from __future__ import annotations

import io
import math
import os
from datetime import date

import numpy as np
import pandas as pd

from .appeears import (
    PRODUCTS, AppEEARSClient, hls_ndvi_from_appeears, modis_ndvi_from_appeears, smap_from_appeears,
)
from .base import DataProvider, NotAvailable
from .http import FetchError, get_json, get_text
from .nasa_power import fetch_power_daily


class NasaProvider(DataProvider):
    source = "nasa"
    label_tr = "NASA (canlı API)"
    label_en = "NASA (live API)"

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        self._appeears: AppEEARSClient | None = None

    @property
    def appeears(self) -> AppEEARSClient:
        if self._appeears is None:
            self._appeears = AppEEARSClient(self.cfg)
        return self._appeears

    # --- NASA POWER --------------------------------------------------------
    def climate_daily(self, site, basin, start, end):
        return fetch_power_daily(site.lat, site.lon, start, end, self.cfg)

    # --- AppEEARS ----------------------------------------------------------
    def soil_moisture(self, site, basin, start, end):
        start = max(start, date(2015, 3, 31))
        prod, layers = PRODUCTS["smap"]
        raw = self.appeears.point_task(f"bs_smap_{site.id}", [(site.id, site.lat, site.lon)],
                                       start, end, [(prod, lyr) for lyr in layers])
        return smap_from_appeears(raw)

    def ndvi(self, site, basin, start, end):
        frames = []
        coords = [(site.id, site.lat, site.lon)]
        for key in ("hls_l30", "hls_s30"):
            prod, layers = PRODUCTS[key]
            s = max(start, date(2013, 4, 11) if key == "hls_l30" else date(2015, 11, 28))
            raw = self.appeears.point_task(f"bs_{key}_{site.id}", coords, s, end,
                                           [(prod, lyr) for lyr in layers])
            frames.append(hls_ndvi_from_appeears(raw, key))
        prod, layers = PRODUCTS["modis_ndvi"]
        raw = self.appeears.point_task(f"bs_modis_{site.id}", coords, max(start, date(2000, 2, 18)), end,
                                       [(prod, layers[0])])
        frames.append(modis_ndvi_from_appeears(raw))
        df = pd.concat(frames).sort_index()
        df.index.name = "date"
        return df

    def terrain(self, site, basin):
        """SRTM 30 m: merkez + 4 komşu nokta (≈30 m) → eğim (merkezi fark)."""
        d_lat = 30 / 111_320
        d_lon = 30 / (111_320 * max(math.cos(math.radians(site.lat)), 0.1))
        coords = [
            ("c", site.lat, site.lon), ("n", site.lat + d_lat, site.lon), ("s", site.lat - d_lat, site.lon),
            ("e", site.lat, site.lon + d_lon), ("w", site.lat, site.lon - d_lon),
        ]
        prod, layers = PRODUCTS["srtm"]
        raw = self.appeears.point_task(f"bs_srtm_{site.id}", coords, date(2000, 2, 11), date(2000, 2, 21),
                                       [(prod, layers[0])])
        col = next(c for c in raw.columns if c.endswith(layers[0]))
        z = raw.groupby("ID")[col].mean()
        dzdx = (z["e"] - z["w"]) / 60.0
        dzdy = (z["n"] - z["s"]) / 60.0
        slope = math.degrees(math.atan(math.hypot(dzdx, dzdy)))
        return {"elevation_m": float(z["c"]), "slope_deg": slope}

    # --- GRACE / GRACE-FO (PO.DAAC) ---------------------------------------
    def water_storage(self, basin):
        try:
            import xarray as xr  # noqa: F401
        except ImportError as exc:
            raise NotAvailable("GRACE dosyasını okumak için: pip install -r requirements-nasa.txt") from exc
        token = os.environ.get("EARTHDATA_TOKEN")
        if not token:
            raise NotAvailable("GRACE (PO.DAAC) indirmesi için EARTHDATA_TOKEN gerekli")
        cmr = self.cfg.get("nasa", {}).get("cmr", {}).get("base_url", "https://cmr.earthdata.nasa.gov/search")
        res = get_json(f"{cmr}/granules.json", {
            "short_name": "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4",
            "sort_key": "-start_date", "page_size": 1,
        })
        entries = res.get("feed", {}).get("entry", [])
        if not entries:
            raise FetchError("CMR'de GRACE mascon granülü bulunamadı (ürün adı değişmiş olabilir)")
        url = next((lk["href"] for lk in entries[0].get("links", [])
                    if lk.get("href", "").endswith(".nc") and lk["href"].startswith("https")), None)
        if url is None:
            raise FetchError("GRACE granülünde HTTPS .nc bağlantısı yok")
        import requests
        import xarray as xr

        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=600)
        r.raise_for_status()
        ds = xr.open_dataset(io.BytesIO(r.content))
        lon_min, lat_min, lon_max, lat_max = basin.grace_bbox
        lon_min, lon_max = lon_min % 360, lon_max % 360
        sub = ds["lwe_thickness"].sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
        w = np.cos(np.deg2rad(sub["lat"]))
        series = sub.weighted(w).mean(("lat", "lon")).to_series()
        series.index = pd.to_datetime(series.index).to_period("M").to_timestamp()
        out = pd.DataFrame({"tws_anomaly_cm": series.groupby(level=0).mean()})
        out.index.name = "date"
        return out

    # --- NEX-GDDP-CMIP6 (NCCS THREDDS NCSS) -------------------------------
    def climate_deltas(self, site, basin):
        c = self.cfg.get("nasa", {}).get("cmip6", {})
        base_url = c.get("ncss_base", "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6")
        template = c.get("filename", "{var}_day_{model}_{scenario}_{member}_{grid}_{year}{suffix}.nc")
        models = c.get("models") or {}
        if not models:
            raise NotAvailable("config.yaml -> nasa.cmip6.models boş")
        step = int(c.get("year_step", 2))
        b0, b1 = c.get("baseline", [1995, 2014])
        f0, f1 = c.get("future", [2041, 2060])
        lon = site.lon % 360

        def monthly(model, spec, scenario, years, var):
            vals = []
            for yr in range(years[0], years[1] + 1, step):
                fname = template.format(var=var, model=model, scenario=scenario, year=yr, **spec)
                url = f"{base_url}/{model}/{scenario}/{spec['member']}/{var}/{fname}"
                txt = get_text(url, {
                    "var": var, "latitude": site.lat, "longitude": lon,
                    "time_start": f"{yr}-01-01T00:00:00Z", "time_end": f"{yr}-12-31T23:59:59Z",
                    "accept": "csv",
                }, timeout=120)
                df = pd.read_csv(io.StringIO(txt))
                vcol = next(col for col in df.columns if col.split("[")[0] == var)
                s = pd.Series(df[vcol].to_numpy(float), index=pd.to_datetime(df["time"]))
                vals.append(s)
            s = pd.concat(vals)
            if var in ("tasmax", "tasmin"):
                s = s - 273.15
            else:
                s = s * 86400.0
            return s.groupby(s.index.month).mean()

        rows = []
        for scen in c.get("scenarios", ["ssp245", "ssp585"]):
            per_model = []
            for model, spec in models.items():
                hist = {v: monthly(model, spec, "historical", (b0, b1), v) for v in ("tasmax", "tasmin", "pr")}
                fut = {v: monthly(model, spec, scen, (f0, f1), v) for v in ("tasmax", "tasmin", "pr")}
                per_model.append(pd.DataFrame({
                    "dtmax": fut["tasmax"] - hist["tasmax"],
                    "dtmin": fut["tasmin"] - hist["tasmin"],
                    "precip_ratio": (fut["pr"] / hist["pr"].clip(lower=0.05)).clip(0.2, 3.0),
                }))
            ens = sum(per_model) / len(per_model)
            for m, r in ens.iterrows():
                rows.append({"month": int(m), "scenario": scen, **r.to_dict()})
        return pd.DataFrame(rows)

    # --- SoilGrids (ISRIC, açık REST) -------------------------------------
    def soil_properties(self, site, basin):
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        params = [("lon", site.lon), ("lat", site.lat), ("value", "mean")]
        params += [("property", p) for p in ("clay", "sand", "soc", "phh2o")]
        params += [("depth", d) for d in ("0-5cm", "5-15cm", "15-30cm", "30-60cm")]
        import requests

        resp = requests.get(url, params=params, timeout=60)
        if resp.status_code >= 400:
            raise FetchError(f"SoilGrids HTTP {resp.status_code}")
        layers = resp.json()["properties"]["layers"]
        thick = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15, "30-60cm": 30}
        vals = {}
        for layer in layers:
            d_factor = layer.get("unit_measure", {}).get("d_factor", 10) or 10
            num = den = 0.0
            for dpt in layer["depths"]:
                v = dpt["values"].get("mean")
                if v is None:
                    continue
                num += v / d_factor * thick[dpt["label"]]
                den += thick[dpt["label"]]
            if den:
                vals[layer["name"]] = num / den
        # d_factor zaten uygulandı: kil/kum g/kg ÷ 10 → %, soc dg/kg ÷ 10 → g/kg, pH×10 ÷ 10
        if "clay" not in vals or "sand" not in vals:
            raise NotAvailable("SoilGrids bu nokta için kil/kum değeri döndürmedi (su yüzeyi/yerleşim olabilir)")
        clay, sand = vals["clay"], vals["sand"]
        out = {"taw_mm_per_m": taw_from_texture(clay, sand), "clay_pct": clay, "sand_pct": sand}
        if "soc" in vals:
            out["soc_g_kg"] = vals["soc"]
        if "phh2o" in vals:
            out["ph"] = vals["phh2o"]
        return out

    def precip_satellite(self, site, basin, start, end):
        raise NotAvailable(
            "GPM IMERG için canlı istemci yok. GES DISC'ten (GPM_3IMERGDF) nokta zaman serisini CSV "
            "olarak indirip data/external/precip_satellite/ altına koyun ve bu veri setinin kaynağını "
            "'files' yapın (docs/DATA_SWAP.md)."
        )


def taw_from_texture(clay_pct: float, sand_pct: float) -> float:
    """Basit doku sınıfı → kullanılabilir su (mm/m). FAO-56 Tablo 19 aralık ortaları."""
    silt = max(0.0, 100 - clay_pct - sand_pct)
    if sand_pct >= 85:
        return 70.0          # kum
    if sand_pct >= 70:
        return 90.0          # tınlı kum
    if clay_pct >= 40:
        return 150.0         # kil
    if clay_pct >= 27:
        return 170.0 if silt >= 30 else 155.0   # killi tın
    if silt >= 50:
        return 190.0         # siltli tın
    if sand_pct >= 52:
        return 120.0         # kumlu tın
    return 160.0             # tın
