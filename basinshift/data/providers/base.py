"""Tüm veri sağlayıcılarının uyduğu ortak arayüz.

Yeni bir kaynak eklemek (ör. TKGM, MGM, yarışmada paylaşılan bir API) için
bu sınıftan türetip ilgili metodları yazmak ve hub.py'deki kayıt sözlüğüne
eklemek yeterlidir. Dönen veri ``schema.py``'deki sözleşmeye uymalıdır;
DataHub her sonucu ``schema.validate`` ile doğrular.
"""
from __future__ import annotations

from abc import ABC
from datetime import date

import pandas as pd

from ..basins import Basin, Site


class NotAvailable(RuntimeError):
    """Bu sağlayıcı bu veri setini sağlayamıyor (ör. kimlik bilgisi yok)."""


class DataProvider(ABC):
    #: config.yaml'daki kaynak adı: "synthetic" | "nasa" | "files"
    source: str = "base"
    #: Kullanıcıya gösterilecek kısa etiket
    label_tr: str = ""
    label_en: str = ""

    def __init__(self, cfg: dict):
        self.cfg = cfg

    # Her metod ilgili veri seti için şemaya uygun veri döner.
    def climate_daily(self, site: Site, basin: Basin, start: date, end: date) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: climate_daily desteklenmiyor")

    def soil_moisture(self, site: Site, basin: Basin, start: date, end: date) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: soil_moisture desteklenmiyor")

    def ndvi(self, site: Site, basin: Basin, start: date, end: date) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: ndvi desteklenmiyor")

    def precip_satellite(self, site: Site, basin: Basin, start: date, end: date) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: precip_satellite desteklenmiyor")

    def water_storage(self, basin: Basin) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: water_storage desteklenmiyor")

    def climate_deltas(self, site: Site, basin: Basin) -> pd.DataFrame:
        raise NotAvailable(f"{self.source}: climate_deltas desteklenmiyor")

    def terrain(self, site: Site, basin: Basin) -> dict:
        raise NotAvailable(f"{self.source}: terrain desteklenmiyor")

    def soil_properties(self, site: Site, basin: Basin) -> dict:
        raise NotAvailable(f"{self.source}: soil_properties desteklenmiyor")
