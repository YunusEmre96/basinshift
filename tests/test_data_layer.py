import json
from pathlib import Path

import pandas as pd
import pytest

from basinshift.config import load_config
from basinshift.data.hub import DataHub
from basinshift.data.providers.files import FilesProvider, normalize_frame
from basinshift.data.providers.nasa_power import parse_power_json
from basinshift.data.schema import SchemaError, validate

FIX = Path(__file__).parent / "fixtures"


def test_synthetic_matches_schema_and_is_deterministic(hub, konya):
    site = konya.site("cumra")
    a = hub.climate_daily(site, konya)
    b = DataHub().climate_daily(site, konya)
    assert list(a.columns) == ["tmax", "tmin", "tmean", "rh", "wind2m", "rs", "precip"]
    pd.testing.assert_frame_equal(a, b)
    assert (a["tmax"] >= a["tmin"]).all()
    annual = a["precip"].groupby(a.index.year).sum().mean()
    assert 250 < annual < 450   # Konya ~330 mm


def test_all_datasets_have_provenance(hub, konya):
    site = konya.site("cumra")
    hub.climate_daily(site, konya)
    hub.soil_moisture(site, konya)
    hub.ndvi(site, konya)
    hub.water_storage(konya)
    hub.climate_deltas(site, konya)
    for ds in ("climate_daily", "soil_moisture", "ndvi", "water_storage", "climate_deltas"):
        p = hub.provenance[ds]
        assert p.actual == "synthetic" and p.is_synthetic


def test_power_json_parser():
    payload = json.loads((FIX / "power_sample.json").read_text())
    df = parse_power_json(payload)
    df = validate("climate_daily", df)
    assert len(df) == 5
    assert df["rs"].isna().sum() == 1          # -999 dolgu değeri NaN olur
    assert abs(df.loc["2024-01-01", "tmax"] - 6.2) < 1e-9


def test_power_csv_via_files_provider():
    from basinshift.data.providers.files import _read_any_csv
    df = normalize_frame(_read_any_csv(FIX / "power_sample.csv"))
    df = validate("climate_daily", df)
    assert len(df) == 3 and df.index[0] == pd.Timestamp("2024-01-01")


def test_files_provider_reads_external(tmp_path, monkeypatch, konya):
    ext = tmp_path / "climate_daily"
    ext.mkdir(parents=True)
    (ext / "cumra.csv").write_text((FIX / "power_sample.csv").read_text(encoding="utf-8"), encoding="utf-8")
    cfg = load_config()
    cfg["data"]["files_dir"] = str(tmp_path)
    p = FilesProvider(cfg)
    df = p.climate_daily(konya.site("cumra"), konya, pd.Timestamp("2024-01-01").date(), pd.Timestamp("2024-12-31").date())
    assert len(df) == 3


def test_fallback_to_synthetic_with_warning(monkeypatch, konya, tmp_path):
    monkeypatch.setenv("BASINSHIFT_DATA_CLIMATE_DAILY", "files")
    cfg = load_config()
    cfg["data"]["files_dir"] = str(tmp_path)      # boş klasör → dosya yok
    hub = DataHub(cfg)
    df = hub.climate_daily(konya.site("cumra"), konya)
    p = hub.provenance["climate_daily"]
    assert p.requested == "files" and p.actual == "synthetic" and p.fell_back
    assert p.warnings and len(df) > 1000


def test_no_fallback_raises(monkeypatch, konya, tmp_path):
    monkeypatch.setenv("BASINSHIFT_DATA_CLIMATE_DAILY", "files")
    cfg = load_config()
    cfg["data"]["files_dir"] = str(tmp_path)
    cfg["data"]["fallback_to_synthetic"] = False
    with pytest.raises(RuntimeError):
        DataHub(cfg).climate_daily(konya.site("cumra"), konya)


def test_schema_rejects_bad_values():
    idx = pd.date_range("2020-01-01", periods=3)
    df = pd.DataFrame({"tmax": [10, 10, 10], "tmin": [0, 0, 0], "tmean": 5, "rh": [50, 50, 150],
                       "wind2m": 2, "rs": 10, "precip": 0}, index=idx)
    with pytest.raises(SchemaError):
        validate("climate_daily", df)
    with pytest.raises(SchemaError):
        validate("climate_daily", df.drop(columns=["precip"]))


def test_env_override(monkeypatch):
    monkeypatch.setenv("BASINSHIFT_DATA", "files")
    cfg = load_config()
    assert all(v == "files" for v in cfg["data"]["sources"].values())


def test_soilgrids_units(monkeypatch, konya):
    """SoilGrids d_factor bir kez uygulanmalı: kil 250 (g/kg×10 değil, ham) → %25."""
    from basinshift.data.providers import nasa as nasa_mod

    def layer(name, vals):
        return {"name": name, "unit_measure": {"d_factor": 10},
                "depths": [{"label": d, "values": {"mean": v}} for d, v in vals.items()]}
    depths = ("0-5cm", "5-15cm", "15-30cm", "30-60cm")
    payload = {"properties": {"layers": [
        layer("clay", dict.fromkeys(depths, 250)), layer("sand", dict.fromkeys(depths, 300)),
        layer("soc", dict.fromkeys(depths, 120)), layer("phh2o", dict.fromkeys(depths, 78)),
    ]}}

    class Resp:
        status_code = 200
        def json(self):
            return payload

    import requests
    monkeypatch.setattr(requests, "get", lambda *a, **k: Resp())
    out = nasa_mod.NasaProvider(load_config()).soil_properties(konya.site("cumra"), konya)
    assert abs(out["clay_pct"] - 25) < 1e-9 and abs(out["sand_pct"] - 30) < 1e-9
    assert abs(out["soc_g_kg"] - 12) < 1e-9 and abs(out["ph"] - 7.8) < 1e-9
    assert out["taw_mm_per_m"] == 160.0     # tın


def test_power_parser_does_not_invent_rain():
    import numpy as np
    payload = json.loads((FIX / "power_sample.json").read_text())
    payload["properties"]["parameter"]["PRECTOTCORR"]["20240103"] = -999.0
    df = parse_power_json(payload)
    assert np.isnan(df.loc["2024-01-03", "precip"])


def test_site_data_provenance_is_per_site(konya):
    from basinshift.engine.pipeline import load_site_data
    hub = DataHub()
    a = load_site_data(hub, konya.site("cumra"), konya)
    b = load_site_data(hub, konya.site("cihanbeyli"), konya)
    assert a.provenance["climate_daily"].key.startswith("konya_cumra")
    assert b.provenance["climate_daily"].key.startswith("konya_cihanbeyli")
    assert a.provenance["climate_daily"] is not b.provenance["climate_daily"]


def test_corrupt_cache_is_deleted_and_live_source_retried(tmp_path, monkeypatch, konya):
    from basinshift.data.providers.nasa import NasaProvider
    monkeypatch.setenv("BASINSHIFT_DATA_TERRAIN", "nasa")
    cfg = load_config()
    cfg["data"]["cache"]["dir"] = str(tmp_path)
    hub = DataHub(cfg)
    site = konya.site("cumra")
    path = hub._cache_path("nasa", "terrain", site.cache_key)
    path.parent.mkdir(parents=True)
    path.write_text("{bozuk json", encoding="utf-8")
    monkeypatch.setattr(NasaProvider, "terrain", lambda self, s, b: {"elevation_m": 1010.0, "slope_deg": 0.7})
    out = hub.terrain(site, konya)
    p = hub.provenance["terrain"]
    assert out["slope_deg"] == 0.7 and p.actual == "nasa" and not p.from_cache
    assert path.exists()   # yeniden yazıldı


def test_default_values_are_labelled(monkeypatch, konya, tmp_path):
    monkeypatch.setenv("BASINSHIFT_DATA_SOIL_PROPERTIES", "files")
    cfg = load_config()
    cfg["data"]["files_dir"] = str(tmp_path)
    cfg["data"]["fallback_to_synthetic"] = False
    hub = DataHub(cfg)
    out = hub.soil_properties(konya.site("cumra"), konya)
    p = hub.provenance["soil_properties"]
    assert out == {"taw_mm_per_m": 150.0}
    assert p.is_default and not p.is_real and not p.is_synthetic


def test_dict_schema_rejects_nan():
    with pytest.raises(SchemaError):
        validate("soil_properties", {"taw_mm_per_m": float("nan")})
