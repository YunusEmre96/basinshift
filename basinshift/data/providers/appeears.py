"""NASA AppEEARS nokta örnekleme istemcisi (Earthdata hesabı gerekir).

AppEEARS, SMAP, HLS, MODIS ve SRTM gibi ürünleri tek bir API üzerinden
nokta bazında CSV olarak verir. Akış: giriş → görev oluştur → bekle →
paket dosyalarını listele → CSV indir.

Belgeler: https://appeears.earthdatacloud.nasa.gov/api/

Kimlik bilgileri YALNIZCA ortam değişkenlerinden okunur:
    EARTHDATA_TOKEN                 (varsa doğrudan kullanılır)
    EARTHDATA_USERNAME / EARTHDATA_PASSWORD

UYARI: Bu istemci API belgelerine göre yazılmıştır; geliştirme ortamında
canlı ağ erişimi olmadığından gerçek servisle uçtan uca test EDİLMEMİŞTİR.
İlk kullanımda scripts/download_appeears.py ile küçük bir tarih aralığında
deneyin. Sorun çıkarsa AppEEARS web arayüzünden CSV indirip ``files``
kaynağını kullanmak her zaman çalışan yedek yoldur (docs/DATA_SWAP.md).
"""
from __future__ import annotations

import io
import os
import time
from datetime import date

import numpy as np
import pandas as pd
import requests

from .base import NotAvailable
from .http import USER_AGENT, FetchError

# Ürün ve katman adları (AppEEARS ürün listesine göre; sürümler değişebilir)
PRODUCTS = {
    "smap": ("SPL4SMGP.008", ["Geophysical_Data_sm_surface", "Geophysical_Data_sm_rootzone"]),
    "hls_l30": ("HLSL30.020", ["B04", "B05", "Fmask"]),
    "hls_s30": ("HLSS30.020", ["B04", "B8A", "Fmask"]),
    "modis_ndvi": ("MOD13Q1.061", ["_250m_16_days_NDVI"]),
    "srtm": ("SRTMGL1_NC.003", ["SRTMGL1_DEM"]),
}


class AppEEARSClient:
    def __init__(self, cfg: dict):
        a = cfg.get("nasa", {}).get("appeears", {})
        self.base = a.get("base_url", "https://appeears.earthdatacloud.nasa.gov/api").rstrip("/")
        self.poll = a.get("poll_interval_s", 20)
        self.max_wait = a.get("max_wait_s", 1800)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._token: str | None = None

    # -- kimlik doğrulama ---------------------------------------------------
    def token(self) -> str:
        if self._token:
            return self._token
        tok = os.environ.get("EARTHDATA_TOKEN")
        if tok:
            self._token = tok
            return tok
        user, pwd = os.environ.get("EARTHDATA_USERNAME"), os.environ.get("EARTHDATA_PASSWORD")
        if not (user and pwd):
            raise NotAvailable(
                "AppEEARS için EARTHDATA_TOKEN veya EARTHDATA_USERNAME/EARTHDATA_PASSWORD "
                "ortam değişkenleri gerekli (https://urs.earthdata.nasa.gov)."
            )
        resp = self.session.post(f"{self.base}/login", auth=(user, pwd), timeout=60)
        if resp.status_code >= 400:
            raise FetchError(f"AppEEARS girişi başarısız: HTTP {resp.status_code}")
        self._token = resp.json()["token"]
        return self._token

    def _h(self) -> dict:
        return {"Authorization": f"Bearer {self.token()}"}

    # -- görev ----------------------------------------------------------------
    def point_task(self, name: str, coords: list[tuple[str, float, float]], start: date, end: date,
                   layers: list[tuple[str, str]]) -> pd.DataFrame:
        """coords: [(nokta_id, enlem, boylam), ...]"""
        body = {
            "task_type": "point",
            "task_name": name[:60],
            "params": {
                "dates": [{"startDate": start.strftime("%m-%d-%Y"), "endDate": end.strftime("%m-%d-%Y")}],
                "layers": [{"product": p, "layer": lyr} for p, lyr in layers],
                "coordinates": [
                    {"latitude": la, "longitude": lo, "id": pid, "category": "basinshift"}
                    for pid, la, lo in coords
                ],
            },
        }
        resp = self.session.post(f"{self.base}/task", json=body, headers=self._h(), timeout=60)
        if resp.status_code >= 400:
            raise FetchError(f"AppEEARS görev oluşturulamadı: HTTP {resp.status_code} {resp.text[:300]}")
        task_id = resp.json()["task_id"]
        waited = 0
        while True:
            st = self.session.get(f"{self.base}/task/{task_id}", headers=self._h(), timeout=60).json()
            status = st.get("status")
            if status == "done":
                break
            if status in ("error", "expired"):
                raise FetchError(f"AppEEARS görevi başarısız: {st}")
            if waited >= self.max_wait:
                raise FetchError(f"AppEEARS görevi {self.max_wait} sn içinde bitmedi (id={task_id})")
            time.sleep(self.poll)
            waited += self.poll
        bundle = self.session.get(f"{self.base}/bundle/{task_id}", headers=self._h(), timeout=60).json()
        frames = []
        for f in bundle.get("files", []):
            if f.get("file_name", "").endswith(".csv") and "results" in f["file_name"]:
                r = self.session.get(f"{self.base}/bundle/{task_id}/{f['file_id']}",
                                     headers=self._h(), timeout=300, allow_redirects=True)
                r.raise_for_status()
                frames.append(pd.read_csv(io.StringIO(r.text)))
        if not frames:
            raise FetchError("AppEEARS paketinde sonuç CSV'si bulunamadı")
        return pd.concat(frames, ignore_index=True)


def _col(df: pd.DataFrame, product: str, layer: str) -> str:
    """AppEEARS CSV sütun adı: '<ÜRÜN_SÜRÜM>_<katman>' (nokta yerine alt çizgi)."""
    key = f"{product.replace('.', '_')}_{layer}"
    for c in df.columns:
        if c == key or c.endswith(layer) and product.split(".")[0] in c:
            return c
    raise FetchError(f"AppEEARS CSV'sinde sütun yok: {key}")


def _maybe_scale(x: pd.Series, expected_max: float) -> pd.Series:
    """Ölçek faktörü uygulanmamışsa (ör. HLS 0–10000) uygular."""
    x = pd.to_numeric(x, errors="coerce")
    if x.dropna().abs().quantile(0.95) > expected_max * 5:
        return x * 0.0001
    return x


def smap_from_appeears(df: pd.DataFrame) -> pd.DataFrame:
    prod, (ls, lr) = PRODUCTS["smap"][0], PRODUCTS["smap"][1]
    out = pd.DataFrame({
        "date": pd.to_datetime(df["Date"]),
        "sm_surface": pd.to_numeric(df[_col(df, prod, ls)], errors="coerce"),
        "sm_rootzone": pd.to_numeric(df[_col(df, prod, lr)], errors="coerce"),
    })
    out = out[(out["sm_surface"] >= 0) & (out["sm_rootzone"] >= 0)]  # dolgu değerleri (-9999) atılır
    return out.groupby(out["date"].dt.normalize()).mean(numeric_only=True).rename_axis("date")


def hls_ndvi_from_appeears(df: pd.DataFrame, product_key: str) -> pd.DataFrame:
    prod, layers = PRODUCTS[product_key]
    red = _maybe_scale(df[_col(df, prod, layers[0])], 1.0)
    nir = _maybe_scale(df[_col(df, prod, layers[1])], 1.0)
    fmask = pd.to_numeric(df[_col(df, prod, "Fmask")], errors="coerce").fillna(255).astype(int)
    # Fmask bitleri: 1=bulut, 2=bulut çevresi, 3=gölge (HLS v2 kullanıcı kılavuzu)
    clear = ((fmask & 0b1110) == 0)
    ndvi = (nir - red) / (nir + red)
    out = pd.DataFrame({"date": pd.to_datetime(df["Date"]), "ndvi": ndvi, "source": "HLS"})[clear.values]
    out = out[np.isfinite(out["ndvi"]) & out["ndvi"].between(-1, 1)]
    return out.set_index("date")


def modis_ndvi_from_appeears(df: pd.DataFrame) -> pd.DataFrame:
    prod, layers = PRODUCTS["modis_ndvi"]
    ndvi = pd.to_numeric(df[_col(df, prod, layers[0])], errors="coerce")
    if ndvi.dropna().abs().max() > 1.5:
        ndvi = ndvi * 0.0001
    out = pd.DataFrame({"date": pd.to_datetime(df["Date"]), "ndvi": ndvi, "source": "MODIS"})
    out = out[out["ndvi"].between(-0.2, 1)]
    return out.set_index("date")
