"""DataHub: veri setlerini yapılandırmaya göre doğru sağlayıcıdan alır.

Sorumlulukları:
    * veri seti → kaynak yönlendirmesi (config.yaml / ortam değişkeni)
    * canlı (nasa) kaynak için disk önbelleği (demo internetsiz çalışsın diye)
    * şema doğrulaması (schema.validate)
    * hata durumunda açık uyarı + (ayarlıysa) sentetik veriye geri düşme
    * provenance: her veri setinin, HER NOKTA İÇİN gerçekte nereden geldiğinin kaydı
      (arayüzdeki rozetler, "Neden bu plan?" kanıt satırları, güven etiketleri ve
      PDF karnedeki uyarı bu kayıttan beslenir)

Dürüstlük kuralları:
    * Sentetik ya da varsayılan değer asla gerçek veri gibi etiketlenmez.
    * Bilinen veri hataları (ağ, kimlik, şema) uyarıyla geri düşer; beklenmeyen
      hatalar (yazılım hatası olabilir) ayrıca günlüğe tam iz kaydıyla yazılır ve
      uyarı metninde öyle belirtilir.
    * Bozuk önbellek dosyası silinir ve canlı kaynak yeniden denenir.
    * ``files`` kaynağı önbelleğe alınmaz (dosyalar zaten yerel; eski kopya okunmasın).
"""
from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from ..config import load_config, source_for
from ..textutil import bi, loc
from .basins import Basin, Site
from .providers.base import DataProvider, NotAvailable
from .providers.files import FilesProvider
from .providers.http import FetchError
from .providers.nasa import NasaProvider
from .providers.synthetic import SyntheticProvider
from .schema import SPECS, SchemaError, completeness, validate

log = logging.getLogger("basinshift.data")

PROVIDERS: dict[str, type[DataProvider]] = {
    "synthetic": SyntheticProvider,
    "nasa": NasaProvider,
    "files": FilesProvider,
}
CACHED_SOURCES = {"nasa"}
EXPECTED_ERRORS = (NotAvailable, FetchError, SchemaError, requests.RequestException, OSError, ValueError, ImportError)
DEFAULT, MISSING, UNVERIFIED = "default", "missing", "unverified"


@dataclass
class Provenance:
    dataset: str
    requested: str
    key: str = ""
    actual: str = ""          # synthetic | nasa | files | default | missing
    label_tr: str = ""
    label_en: str = ""
    product: str = ""
    resolution: str = ""
    from_cache: bool = False
    origin: str = ""          # files kaynağı için KAYNAK.yaml kökeni (nasa | external | synthetic | assumed | unknown)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_synthetic(self) -> bool:
        return self.actual == "synthetic"

    @property
    def is_real(self) -> bool:
        return self.actual in ("nasa", "files")

    @property
    def is_nasa(self) -> bool:
        """Gerçekten NASA kaynaklı mı (canlı API ya da kökeni 'nasa' olan dosya)?"""
        return self.actual == "nasa" or (self.actual == "files" and self.origin == "nasa")

    @property
    def is_default(self) -> bool:
        return self.actual in (DEFAULT, MISSING)

    @property
    def is_unverified(self) -> bool:
        return self.actual == UNVERIFIED

    @property
    def status(self) -> str:
        """Arayüz rozeti: real | synthetic | default | unverified | missing."""
        if self.is_real:
            return "real"
        if self.is_synthetic:
            return "synthetic"
        if self.actual == MISSING:
            return "missing"
        if self.is_unverified:
            return "unverified"
        return "default"

    @property
    def fell_back(self) -> bool:
        return self.actual != self.requested

    def label(self, lang: str) -> str:
        return self.label_tr if lang == "tr" else self.label_en

    def product_text(self, lang: str) -> str:
        return loc(self.product, lang)

    def resolution_text(self, lang: str) -> str:
        return loc(self.resolution, lang)

    def messages(self, lang: str, last: int | None = None) -> list[str]:
        """Notlar + uyarılar, istenen dilde (arayüz ve PDF bunu kullanır)."""
        out = [loc(m, lang) for m in (self.notes + self.warnings)]
        return out[-last:] if last else out

    def warning_texts(self, lang: str, last: int | None = None) -> list[str]:
        out = [loc(m, lang) for m in self.warnings]
        return out[-last:] if last else out


def any_synthetic(prov: dict[str, Provenance]) -> bool:
    return any(p.is_synthetic for p in prov.values())


def any_not_real(prov: dict[str, Provenance]) -> bool:
    return any(not p.is_real for p in prov.values())


class DataHub:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or load_config()
        self._providers: dict[str, DataProvider] = {}
        #: veri seti → SON alınan kayıt (geriye dönük uyumluluk / kenar çubuğu)
        self.provenance: dict[str, Provenance] = {}
        #: (veri seti, anahtar) → kayıt — nokta bazında doğru kayıt için bunu kullanın
        self.records: dict[tuple[str, str], Provenance] = {}
        dcfg = self.cfg["data"]
        self.cache_enabled = bool(dcfg.get("cache", {}).get("enabled", True))
        self.cache_dir = Path(dcfg.get("cache", {}).get("dir", "data/cache"))
        self.fallback = bool(dcfg.get("fallback_to_synthetic", True))
        self.history = (int(dcfg.get("history_start_year", 1982)), int(dcfg.get("history_end_year", 2025)))

    # ---------------------------------------------------------------------
    def provider(self, source: str) -> DataProvider:
        if source not in self._providers:
            self._providers[source] = PROVIDERS[source](self.cfg)
        return self._providers[source]

    def _cache_path(self, source: str, dataset: str, key: str) -> Path:
        h = hashlib.sha1(key.encode()).hexdigest()[:12]
        ext = "json" if SPECS[dataset].kind == "dict" else "csv.gz"
        return self.cache_dir / source / dataset / f"{h}.{ext}"

    def _read_cache(self, path: Path, dataset: str):
        """Önbellek yoksa None. Bozuksa dosyayı siler ve None döner (canlı kaynak denensin)."""
        if not path.exists():
            return None
        try:
            if SPECS[dataset].kind == "dict":
                return json.loads(path.read_text(encoding="utf-8"))
            df = pd.read_csv(path, index_col=0 if dataset != "climate_deltas" else None,
                             parse_dates=dataset != "climate_deltas")
            if dataset != "climate_deltas":
                df.index.name = "date"
            return validate(dataset, df)
        except Exception:  # noqa: BLE001 — bozuk dosya: sil ve canlı kaynağa git
            log.warning("Bozuk önbellek dosyası siliniyor: %s", path, exc_info=True)
            path.unlink(missing_ok=True)
            return None

    def _write_cache(self, path: Path, dataset: str, data) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if SPECS[dataset].kind == "dict":
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        else:
            data.to_csv(path, index=dataset != "climate_deltas")

    def _store(self, prov: Provenance) -> None:
        self.provenance[prov.dataset] = prov
        self.records[(prov.dataset, prov.key)] = prov

    def _fetch(self, dataset: str, key: str, call):
        """Ortak akış: kaynak seç → önbellek → çağır → doğrula → gerekirse geri düş."""
        requested = source_for(self.cfg, dataset)
        spec = SPECS[dataset]
        prov = Provenance(dataset, requested, key=key, product=spec.product, resolution=spec.resolution)
        attempts = [requested] + (["synthetic"] if self.fallback and requested != "synthetic" else [])
        last_error: Exception | None = None
        for source in attempts:
            p = self.provider(source)
            prov.from_cache = False
            use_cache = self.cache_enabled and source in CACHED_SOURCES
            cache_path = self._cache_path(source, dataset, key)
            try:
                data = self._read_cache(cache_path, dataset) if use_cache else None
                if data is not None:
                    prov.from_cache = True
                else:
                    data = validate(dataset, call(p))
                    if use_cache:
                        self._write_cache(cache_path, dataset, data)
                prov.actual = source
                prov.label_tr, prov.label_en = p.label_tr, p.label_en
                if source == "synthetic":
                    prov.product = f"SENTETİK — gerçek ürün: {spec.product}"
                if source == "files":
                    self._apply_file_origin(prov, getattr(p, "last_origin", {}) or {}, spec)
                self._store(prov)
                return data
            except EXPECTED_ERRORS as exc:
                last_error = exc
                prov.warnings.append(f"{source}: {type(exc).__name__}: {exc}")
            except Exception as exc:  # noqa: BLE001 — demo çökmesin ama gizlenmesin
                last_error = exc
                log.exception("Beklenmeyen hata: %s / %s", dataset, source)
                prov.warnings.append(
                    bi(f"{source}: BEKLENMEYEN HATA (yazılım hatası olabilir; günlüğe bakın) — {type(exc).__name__}: {exc}",
                       f"{source}: UNEXPECTED ERROR (possibly a software bug; see the log) — {type(exc).__name__}: {exc}")
                )
        prov.actual = MISSING
        prov.label_tr, prov.label_en = "Veri alınamadı", "Data unavailable"
        self._store(prov)
        raise RuntimeError(f"{dataset} hiçbir kaynaktan alınamadı: {last_error}")

    @staticmethod
    def _apply_file_origin(prov: Provenance, origin: dict, spec) -> None:
        """Yerel dosyanın KAYNAK.yaml'daki kökenine göre kaydı düzeltir.

        Dosyanın klasörde durması gerçek veri olduğu anlamına gelmez: sentetik yer tutucu
        ya da elle girilmiş değer öyle etiketlenir; kökeni yazılmamış dosya "doğrulanmamış" sayılır.
        """
        o = origin.get("origin", "unknown")
        prov.origin = o
        note = bi(origin.get("note_tr", ""), origin.get("note_en", "")) if origin.get("note_tr") else ""
        if origin.get("product"):
            prov.product = origin["product"]
        if o == "nasa":
            prov.label_tr, prov.label_en = "NASA verisi (yerel dosya)", "NASA data (local file)"
        elif o == "external":
            prov.label_tr, prov.label_en = "Açık veri (yerel dosya, NASA dışı)", "Open data (local file, non-NASA)"
        elif o == "synthetic":
            prov.actual = "synthetic"
            prov.label_tr, prov.label_en = "Sentetik yer tutucu (dosya)", "Synthetic placeholder (file)"
            prov.product = f"SENTETİK — gerçek ürün: {spec.product}"
        elif o == "assumed":
            prov.actual = DEFAULT
            prov.label_tr, prov.label_en = "Varsayım / elle girilmiş değer", "Assumed / hand-entered value"
        else:
            prov.actual = UNVERIFIED
            prov.label_tr, prov.label_en = "Yerel dosya (kökeni belirtilmemiş)", "Local file (origin not declared)"
            prov.warnings.append(bi("Bu dosyanın kökeni data/external/KAYNAK.yaml'da yazılı değil; gerçek veri sayılmadı.",
                                    "This file's origin is not declared in data/external/KAYNAK.yaml; not counted as real data."))
        if note:
            prov.notes.append(note)

    def _optional(self, dataset, key, call):
        """Ana hesap için zorunlu olmayan veri setleri: alınamazsa None (kayıt 'missing')."""
        try:
            return self._fetch(dataset, key, call)
        except RuntimeError:
            return None

    def _defaulted(self, dataset: str, key: str, value: dict) -> dict:
        prov = self.records.get((dataset, key))
        if prov is not None:
            prov.actual = DEFAULT
            prov.label_tr, prov.label_en = "Varsayılan değer (veri alınamadı)", "Default value (data unavailable)"
            prov.notes.append(bi(f"Kullanılan varsayılan: {value}", f"Default used: {value}"))
            self._store(prov)
        return value

    # --- Genel arayüz ------------------------------------------------------
    def climate_range(self, basin: Basin) -> tuple[date, date]:
        first, last = self.history
        start = date(basin.ag_year_start(first).year, 1, 1)
        end = min(date.today(), date(last + 1, 6, 30))
        return start, end

    def climate_daily(self, site: Site, basin: Basin) -> pd.DataFrame:
        start, end = self.climate_range(basin)
        df = self._fetch("climate_daily", f"{site.cache_key}|{start}|{end}",
                         lambda p: p.climate_daily(site, basin, start, end))
        prov = self.provenance["climate_daily"]
        rs_cov = completeness(df, "rs")
        if rs_cov < 0.999:
            prov.notes.append(bi(
                f"Güneş radyasyonu verisinin %{(1 - rs_cov) * 100:.1f}'i eksik (POWER'da Tem 1983 öncesi yok); "
                "bu günlerde Hargreaves radyasyon tahmini kullanıldı.",
                f"{(1 - rs_cov) * 100:.1f}% of solar radiation is missing (POWER has none before Jul 1983); "
                "the Hargreaves radiation estimate was used on those days.",
            ))
        for col in ("tmax", "tmin", "precip"):
            cov = completeness(df, col)
            if cov < 0.98:
                prov.warnings.append(bi(f"{col} verisinin %{(1 - cov) * 100:.1f}'i eksik",
                                        f"{(1 - cov) * 100:.1f}% of {col} is missing"))
        return df

    def soil_moisture(self, site: Site, basin: Basin) -> pd.DataFrame | None:
        start, end = date(2015, 3, 31), self.climate_range(basin)[1]
        return self._optional("soil_moisture", f"{site.cache_key}|{end}",
                              lambda p: p.soil_moisture(site, basin, start, end))

    def ndvi(self, site: Site, basin: Basin) -> pd.DataFrame | None:
        start, end = date(2000, 2, 18), self.climate_range(basin)[1]
        return self._optional("ndvi", f"{site.cache_key}|{end}", lambda p: p.ndvi(site, basin, start, end))

    def precip_satellite(self, site: Site, basin: Basin) -> pd.DataFrame | None:
        start, end = date(2000, 6, 1), self.climate_range(basin)[1]
        return self._optional("precip_satellite", f"{site.cache_key}|{end}",
                              lambda p: p.precip_satellite(site, basin, start, end))

    def water_storage(self, basin: Basin) -> pd.DataFrame | None:
        return self._optional("water_storage", basin.id, lambda p: p.water_storage(basin))

    def climate_deltas(self, site: Site, basin: Basin) -> pd.DataFrame | None:
        return self._optional("climate_deltas", site.cache_key, lambda p: p.climate_deltas(site, basin))

    def terrain(self, site: Site, basin: Basin) -> dict:
        r = self._optional("terrain", site.cache_key, lambda p: p.terrain(site, basin))
        return r or self._defaulted("terrain", site.cache_key, {"elevation_m": site.elevation_m, "slope_deg": 0.5})

    def soil_properties(self, site: Site, basin: Basin) -> dict:
        r = self._optional("soil_properties", site.cache_key, lambda p: p.soil_properties(site, basin))
        return r or self._defaulted("soil_properties", site.cache_key, {"taw_mm_per_m": 150.0})

    def snapshot(self, datasets: list[str]) -> dict[str, Provenance]:
        """Son alınan kayıtların kopyası (bir noktanın verisi yüklendikten hemen sonra çağrılır)."""
        return {ds: copy.deepcopy(self.provenance[ds]) for ds in datasets if ds in self.provenance}

    def any_synthetic(self) -> bool:
        return any_synthetic(self.provenance)
