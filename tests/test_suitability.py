"""Ürün uygunluk taraması (başka bölgelerin ürünleri bu tarlada olur mu?)."""
import numpy as np
import pandas as pd
import pytest

from basinshift.data.basins import load_basins
from basinshift.engine.pipeline import load_site_data
from basinshift.engine.scenarios import Scenario, apply_scenario
from basinshift.engine.suitability import heat_check, home_sites, screen_crops
from basinshift.knowledge.tables import load_crop_suitability, load_crops, load_economics


@pytest.fixture(scope="module")
def homes(hub):
    bs = load_basins()
    out = {}
    for bid, sid in home_sites():
        sd = load_site_data(hub, bs[bid].site(sid), bs[bid])
        out[sid] = {"clim": sd.climate, "et0": sd.et0, "basin": bs[bid], "econ": load_economics(bid),
                    "taw": float(sd.soil_props.get("taw_mm_per_m", 150.0))}
    return out


def test_table_is_complete():
    meta = load_crop_suitability()
    crops = load_crops()
    bs = load_basins()
    for cid, r in meta.iterrows():
        assert cid in crops
        assert float(r["gdd_req"]) >= 0
        assert cid in load_economics(r["home_basin"]), cid          # referans bölgede ekiliyor olmalı
        bs[r["home_basin"]].site(r["home_site"])                      # referans konum var


def test_heat_check_constant_climate():
    idx = pd.date_range("2000-01-01", "2004-12-31", freq="D")
    clim = pd.DataFrame({"tmax": 25.0, "tmin": 15.0}, index=idx)      # Tort 20 °C
    konya = load_basins()["konya"]
    need, win = heat_check(clim, konya, (5, 1), gdd_req=1000, tbase=10, years=[2001, 2002, 2003], summer=True)
    assert need == pytest.approx(100, abs=1)                          # 1000 / (20-10)
    assert win > need                                                 # don yok → pencere geniş


def test_screen_konya(hub, konya, homes):
    sd = load_site_data(hub, konya.site("cumra"), konya)
    res = screen_crops(sd.climate, sd.et0, konya, 150.0, homes, irrigated=True)
    by = {r.crop_id: r for r in res}
    for cid in load_economics("konya"):
        if cid in by:
            assert by[cid].native
    assert "cotton" in by and not by["cotton"].native
    assert by["cotton"].verdict != "green"                            # Konya pamuk için soğuk
    assert by["wheat"].verdict == "green"
    for r in res:
        assert 0 <= r.yield_p10 <= r.yield_med <= 1.0001
        assert r.verdict in ("green", "yellow", "red")


def test_warming_helps_heat_limited_crop(hub, konya, homes):
    sd = load_site_data(hub, konya.site("cumra"), konya)
    base = {r.crop_id: r for r in screen_crops(sd.climate, sd.et0, konya, 150.0, homes, True)}
    warm_clim = apply_scenario(sd.climate, Scenario(d_temp_c=3.0), sd.deltas)
    warm = {r.crop_id: r for r in screen_crops(warm_clim, sd.et0, konya, 150.0, homes, True)}
    assert warm["cotton"].heat_margin > base["cotton"].heat_margin
