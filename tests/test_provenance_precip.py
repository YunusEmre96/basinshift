"""Veri dürüstlüğü (KAYNAK.yaml) ve IMERG yağış düzeltmesi testleri."""
import numpy as np
import pandas as pd
import yaml

from basinshift.data.hub import DataHub, Provenance
from basinshift.data.providers.files import file_origin
from basinshift.engine.pipeline import MIN_OVERLAP_YEARS, PRECIP_RATIO_CLIP, correct_precip, imerg_monthly_ratio


class _Spec:
    product = "SMAP L4"


def _prov(**kw) -> Provenance:
    p = Provenance.__new__(Provenance)
    p.actual, p.origin, p.product = "files", "unknown", ""
    p.label_tr = p.label_en = ""
    p.warnings, p.notes = [], []
    for k, v in kw.items():
        setattr(p, k, v)
    return p


def test_manifest_file_overrides_default(tmp_path):
    (tmp_path / "KAYNAK.yaml").write_text(yaml.safe_dump({
        "soil_properties": {"default": {"origin": "assumed"},
                            "files": {"karapinar": {"origin": "external", "note_tr": "SoilGrids"}}}}), encoding="utf-8")
    assert file_origin(tmp_path, "soil_properties", "cumra")["origin"] == "assumed"
    o = file_origin(tmp_path, "soil_properties", "karapinar")
    assert o["origin"] == "external" and o["note_tr"] == "SoilGrids"


def test_manifest_missing_is_unknown(tmp_path):
    assert file_origin(tmp_path, "ndvi", "cumra")["origin"] == "unknown"
    (tmp_path / "KAYNAK.yaml").write_text("ndvi: {default: {origin: banana}}", encoding="utf-8")
    assert file_origin(tmp_path, "ndvi", "cumra")["origin"] == "unknown"


def test_file_origin_labels_status():
    """Klasörde duran dosya kökeni yazılmadıkça 'gerçek' sayılmaz."""
    cases = {"nasa": "real", "external": "real", "synthetic": "synthetic", "assumed": "default", "unknown": "unverified"}
    for origin, status in cases.items():
        p = _prov()
        DataHub._apply_file_origin(p, {"origin": origin}, _Spec)
        assert p.status == status, origin
    p = _prov(); DataHub._apply_file_origin(p, {"origin": "nasa"}, _Spec)
    assert p.is_nasa
    p = _prov(); DataHub._apply_file_origin(p, {"origin": "external"}, _Spec)
    assert not p.is_nasa


def _daily(years, value):
    idx = pd.date_range(f"{years[0]}-01-01", f"{years[1]}-12-31", freq="D")
    return pd.Series(value, index=idx, dtype=float)


def test_imerg_ratio_and_correction():
    power = _daily((2001, 2015), 2.0)
    imerg = _daily((2001, 2015), 1.2)
    ratio = imerg_monthly_ratio(power, imerg)
    assert ratio is not None and len(ratio) == 12
    assert np.allclose(ratio.values, 0.6)
    clim = pd.DataFrame({"precip": _daily((1990, 2015), 2.0)})
    out = correct_precip(clim, ratio)
    assert np.allclose(out["precip"].values, 1.2)
    assert np.allclose(clim["precip"].values, 2.0)  # girdi değişmez


def test_imerg_ratio_needs_overlap_and_is_clipped():
    few = MIN_OVERLAP_YEARS - 2
    assert imerg_monthly_ratio(_daily((2001, 2001 + few), 2.0), _daily((2001, 2001 + few), 1.0)) is None
    r = imerg_monthly_ratio(_daily((2001, 2015), 1.0), _daily((2001, 2015), 5.0))
    assert np.allclose(r.values, PRECIP_RATIO_CLIP[1])
