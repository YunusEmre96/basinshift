"""Dosya sağlayıcısı: data/external/ altındaki CSV'leri okur.

Yarışmada NASA veri dosyası paylaşırsa ya da veriyi bir web arayüzünden
(POWER Data Access Viewer, AppEEARS, GES DISC, PO.DAAC) elle indirirseniz
bu yol kullanılır. Kod değişikliği gerekmez.

Dosya arama sırası (her veri seti için):
    data/external/<veriseti>/<nokta_id>.csv
    data/external/<veriseti>/<havza_id>.csv          (water_storage için)
    data/external/<veriseti>.csv                     (site_id sütunu ile filtrelenir)

Ham NASA biçimleri de kabul edilir:
    * POWER CSV (başlık bloğu -BEGIN HEADER- ... -END HEADER- atlanır;
      YEAR/MO/DY, YEAR/DOY veya YYYYMMDD tarih sütunları; T2M_MAX vb. adlar)
    * AppEEARS nokta CSV'si (SMAP/HLS/MODIS sütun adları)
Sütun adları ALIASES sözlüğüyle şemaya eşlenir.
"""
from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

from .base import DataProvider, NotAvailable

ALIASES = {
    # NASA POWER
    "T2M_MAX": "tmax", "T2M_MIN": "tmin", "T2M": "tmean", "RH2M": "rh", "WS2M": "wind2m",
    "ALLSKY_SFC_SW_DWN": "rs", "PRECTOTCORR": "precip", "PRECTOT": "precip",
    # AppEEARS SMAP
    "SPL4SMGP_008_Geophysical_Data_sm_surface": "sm_surface",
    "SPL4SMGP_008_Geophysical_Data_sm_rootzone": "sm_rootzone",
    # AppEEARS MODIS
    "MOD13Q1_061__250m_16_days_NDVI": "ndvi",
    # GPM IMERG (GES DISC zaman serisi / POWER API)
    "precipitation": "precip", "precipitationCal": "precip", "GPM_3IMERGDF_07_precipitation": "precip",
    "IMERG_PRECTOT": "precip",
    # GRACE
    "lwe_thickness": "tws_anomaly_cm", "tws": "tws_anomaly_cm",
    # Genel
    "Date": "date", "DATE": "date", "time": "date",
}
FILL_VALUES = (-999, -999.0, -9999, -9999.0)

#: data/external içindeki her dosyanın GERÇEK kökeni bu dosyada yazılır.
#: Dosyanın klasörde durması, gerçek NASA verisi olduğu anlamına gelmez.
MANIFEST_NAME = "KAYNAK.yaml"
ORIGINS = ("nasa", "external", "synthetic", "assumed", "unknown")


@lru_cache(maxsize=8)
def _load_manifest(path_str: str, mtime: float) -> dict:
    with open(path_str, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def file_origin(root: Path, dataset: str, stem: str) -> dict:
    """(origin, note_tr, note_en, product) — KAYNAK.yaml'da yoksa origin='unknown'."""
    path = root / MANIFEST_NAME
    entry: dict = {}
    if path.exists():
        man = _load_manifest(str(path), path.stat().st_mtime)
        ds = man.get(dataset) or {}
        entry = dict(ds.get("default") or {})
        entry.update((ds.get("files") or {}).get(stem) or {})
    origin = str(entry.get("origin", "unknown"))
    if origin not in ORIGINS:
        origin = "unknown"
    return {"origin": origin, "note_tr": entry.get("note_tr", ""), "note_en": entry.get("note_en", ""),
            "product": entry.get("product", "")}


def _read_any_csv(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "-END HEADER-" in text:
        text = text.split("-END HEADER-", 1)[1].lstrip("\r\n")
    return pd.read_csv(io.StringIO(text))


def normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: ALIASES.get(c.strip(), c.strip()) for c in df.columns})
    if "date" not in df.columns:
        if {"YEAR", "MO", "DY"} <= set(df.columns):
            df["date"] = pd.to_datetime(dict(year=df["YEAR"], month=df["MO"], day=df["DY"]))
        elif {"YEAR", "DOY"} <= set(df.columns):
            df["date"] = pd.to_datetime(df["YEAR"].astype(int).astype(str) + df["DOY"].astype(int).astype(str).str.zfill(3), format="%Y%j")
        elif "YYYYMMDD" in df.columns:
            df["date"] = pd.to_datetime(df["YYYYMMDD"].astype(str), format="%Y%m%d")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    df = df.replace(list(FILL_VALUES), pd.NA)
    if "tmean" not in df.columns and {"tmax", "tmin"} <= set(df.columns):
        df["tmean"] = (pd.to_numeric(df["tmax"]) + pd.to_numeric(df["tmin"])) / 2
    return df


class FilesProvider(DataProvider):
    source = "files"
    label_tr = "Yerel dosya (data/external)"
    label_en = "Local file (data/external)"

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        self.root = Path(cfg["data"]["files_dir"])
        #: son okunan dosyanın kökeni (DataHub provenance'a yazar)
        self.last_origin: dict = {}

    def _find(self, dataset: str, keys: list[str]) -> Path:
        for k in keys:
            p = self.root / dataset / f"{k}.csv"
            if p.exists():
                self.last_origin = file_origin(self.root, dataset, k)
                return p
        p = self.root / f"{dataset}.csv"
        if p.exists():
            self.last_origin = file_origin(self.root, dataset, dataset)
            return p
        raise NotAvailable(
            f"'{dataset}' için dosya yok. Beklenen: {self.root / dataset / (keys[0] + '.csv')} "
            f"veya {self.root / (dataset + '.csv')}"
        )

    def _table(self, dataset: str, keys: list[str], site_id: str | None = None) -> pd.DataFrame:
        df = normalize_frame(_read_any_csv(self._find(dataset, keys)))
        if site_id is not None and "site_id" in df.columns:
            df = df[df["site_id"].astype(str) == site_id].drop(columns=["site_id"])
        return df

    @staticmethod
    def _clip(df, start, end):
        return df.loc[pd.Timestamp(start): pd.Timestamp(end)]

    def climate_daily(self, site, basin, start, end):
        return self._clip(self._table("climate_daily", [site.id, site.cache_key], site.id), start, end)

    def soil_moisture(self, site, basin, start, end):
        return self._clip(self._table("soil_moisture", [site.id, site.cache_key], site.id), start, end)

    def ndvi(self, site, basin, start, end):
        df = self._table("ndvi", [site.id, site.cache_key], site.id)
        if "source" not in df.columns:
            df["source"] = "HLS"
        return self._clip(df, start, end)

    def precip_satellite(self, site, basin, start, end):
        return self._clip(self._table("precip_satellite", [site.id, site.cache_key], site.id), start, end)

    def water_storage(self, basin):
        return self._table("water_storage", [basin.id])

    def climate_deltas(self, site, basin):
        df = _read_any_csv(self._find("climate_deltas", [site.id, basin.id]))
        return df

    def _dict(self, dataset: str, site) -> dict:
        df = _read_any_csv(self._find(dataset, [site.id, site.cache_key]))
        if "site_id" in df.columns:
            df = df[df["site_id"].astype(str) == site.id]
        if df.empty:
            raise NotAvailable(f"{dataset}: {site.id} için satır yok")
        return {k: v for k, v in df.iloc[0].to_dict().items() if k != "site_id"}

    def terrain(self, site, basin):
        return self._dict("terrain", site)

    def soil_properties(self, site, basin):
        return self._dict("soil_properties", site)
