import numpy as np
import pandas as pd

from basinshift.engine.crop_detect import detect_groups
from basinshift.engine.field import FieldSettings
from basinshift.engine.metrics import cvar
from basinshift.engine.pipeline import build_context
from basinshift.engine.risk import monthly_climate_risk
from basinshift.engine.scenarios import Scenario, apply_scenario
from basinshift.engine.trends import mann_kendall


def test_cvar():
    v = np.arange(100, dtype=float)
    assert cvar(v, 0.05) == np.mean(np.arange(5))


def test_mann_kendall_detects_trend():
    rng = np.random.default_rng(0)
    slope, p = mann_kendall(np.arange(40) * 0.05 + rng.normal(0, 0.2, 40))
    assert p < 0.01 and 0.03 < slope < 0.07
    _, p2 = mann_kendall(rng.normal(0, 1, 40))
    assert p2 > 0.05


def test_crop_year_table_is_physical(cumra_ctx):
    t = cumra_ctx.table
    assert len(t.years) >= 35
    assert (t.ir_net >= 0).all() and (t.eta_rf <= t.etc + 1e-9).all()
    beet, wheat, chick = (t.index(c) for c in ("sugar_beet", "wheat", "chickpea"))
    # pancar buğdaydan, buğday nohuttan fazla su ister
    assert t.ir_net[beet].mean() > t.ir_net[wheat].mean() > t.ir_net[chick].mean()


def test_water_cap_reduces_water_and_yield(hub, konya):
    base = FieldSettings(True, "sprinkler", True, None, 2.5, ["wheat", "chickpea"], 2027)
    capped = FieldSettings(True, "sprinkler", True, 300.0, 2.5, ["wheat", "chickpea"], 2027)
    plan = ["sugar_beet", "wheat", "chickpea", "barley"]
    d0 = build_context(hub, konya.site("cumra"), konya, base).detail(plan)
    d1 = build_context(hub, konya.site("cumra"), konya, capped).detail(plan)
    assert d1["summary"]["water_mean"] < d0["summary"]["water_mean"]
    assert d1["summary"]["yield_ratio"] < d0["summary"]["yield_ratio"]
    assert d1["summary"]["water_p90"] <= 300.0 + 1e-6


def test_drier_scenario_needs_more_water(hub, konya):
    st = FieldSettings(True, "sprinkler", True, None, 2.5, ["wheat", "chickpea"], 2027)
    plan = ["sugar_beet", "wheat", "chickpea", "barley"]
    a = build_context(hub, konya.site("cumra"), konya, st).detail(plan)
    b = build_context(hub, konya.site("cumra"), konya, st, Scenario(2.0, -20.0)).detail(plan)
    assert b["summary"]["water_mean"] > a["summary"]["water_mean"]


def test_cmip6_scenario_applies_deltas(hub, konya):
    site = konya.site("cumra")
    clim = hub.climate_daily(site, konya)
    d = hub.climate_deltas(site, konya)
    out = apply_scenario(clim, Scenario(cmip6="ssp585"), d)
    assert out["tmax"].mean() > clim["tmax"].mean() + 1.5
    assert out["precip"].sum() < clim["precip"].sum()


def test_fallow_stores_water_for_rainfed_wheat(hub, konya):
    st = FieldSettings(False, "none", True, None, 2.5, ["wheat", "barley"], 2027)
    ctx = build_context(hub, konya.site("cihanbeyli"), konya, st)
    after_fallow = ctx.detail(["fallow", "wheat", "fallow", "wheat"])["sim"]["yield_ratio"][:, 1].mean()
    after_barley = ctx.detail(["barley", "wheat", "barley", "wheat"])["sim"]["yield_ratio"][:, 1].mean()
    assert after_fallow > after_barley


def test_soil_scores(cumra_ctx):
    legumes = cumra_ctx.detail(["chickpea", "wheat", "lentil", "barley"])["soil"]
    beet_maize = cumra_ctx.detail(["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"])["soil"]
    assert legumes["nitrogen"] == 100 and beet_maize["nitrogen"] == 0
    assert legumes["soil"] > beet_maize["soil"]
    assert beet_maize["pest_cycle"] < 100


def test_risk_calendar_shape(hub, konya):
    site = konya.site("cumra")
    clim = hub.climate_daily(site, konya)
    from basinshift.engine.et0 import et0_from_climate
    r = monthly_climate_risk(clim, et0_from_climate(clim, site.lat, site.elevation_m))
    assert list(r.index) == list(range(1, 13))
    assert r.loc[1, "frost_days"] > r.loc[7, "frost_days"]
    assert r.loc[7, "heat_days"] > r.loc[1, "heat_days"]


def test_satellite_crop_groups_match_truth(hub, konya):
    site = konya.site("cihanbeyli")
    det = detect_groups(hub.ndvi(site, konya), [2020, 2021, 2022])
    assert [det[y]["group"] for y in (2020, 2021, 2022)] == ["fallow", "winter", "fallow"]


def test_warming_increases_heat_stress(hub, konya):
    st = FieldSettings(True, "sprinkler", True, None, 2.5, ["wheat", "chickpea"], 2027)
    base = build_context(hub, konya.site("cumra"), konya, st).table
    warm = build_context(hub, konya.site("cumra"), konya, st, Scenario(3.0, 0.0)).table
    i = base.index("maize_grain")
    assert warm.heat_days[i].mean() > base.heat_days[i].mean() * 1.5
    assert warm.stress_mult[i].mean() < base.stress_mult[i].mean()


def test_years_with_data_gaps_are_dropped(hub, konya):
    import numpy as np
    from basinshift.engine.et0 import et0_from_climate
    from basinshift.engine.water import build_crop_year_table
    from basinshift.knowledge.tables import basin_crops, load_crops, load_economics
    site = konya.site("cumra")
    clim = hub.climate_daily(site, konya).copy()
    clim.loc["2010-04-01":"2010-06-30", "precip"] = np.nan     # 2010 yaz ürünleri sezonunda büyük boşluk
    et0 = et0_from_climate(clim, site.lat, site.elevation_m)
    t = build_crop_year_table(clim, et0, konya, load_crops(), load_economics("konya"), basin_crops("konya"),
                              150.0, range(1982, 2026))
    assert 2010 in t.dropped_years and 2010 not in t.years
