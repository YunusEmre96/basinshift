"""Borsa / fiyat riski modülü."""
import numpy as np

from basinshift.engine.price_risk import option_price_risk, price_cv, price_multipliers, weather_only
from basinshift.knowledge.tables import load_price_risk
from basinshift.optimizer.search import search


def test_price_table_covers_konya_crops(konya):
    from basinshift.knowledge.tables import basin_crops
    df = load_price_risk()
    have = set(df[df["basin"] == "konya"]["crop_id"])
    assert set(basin_crops("konya")) <= have
    assert (df["price_cv"] >= 0).all()


def test_multipliers_have_unit_mean(cumra_ctx):
    cv = price_cv("konya", cumra_ctx.crop_ids)
    m = price_multipliers(cumra_ctx, cv, n_draws=2000)
    assert abs(m.mean() - 1) < 0.02
    m2 = price_multipliers(cumra_ctx, cv, n_draws=2000)
    assert np.array_equal(m, m2)                                  # tohum sabit


def test_zero_volatility_reproduces_weather_only(cumra_ctx):
    res = search(cumra_ctx, current_plan=["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"])
    zero = {c: 0.0 for c in cumra_ctx.crop_ids}
    m = price_multipliers(cumra_ctx, zero, n_draws=3)
    for opt in res.options.values():
        p, w = option_price_risk(opt, cumra_ctx, m), weather_only(opt)
        assert abs(p["mean_margin"] - w["mean_margin"]) < 1e-6 * max(1, abs(w["mean_margin"]))
        assert abs(p["cvar5"] - w["cvar5"]) < 1e-6 * max(1, abs(w["cvar5"]))


def test_price_risk_lowers_bad_period_income_and_shock_hits_crop(cumra_ctx):
    res = search(cumra_ctx, current_plan=["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"])
    cv = price_cv("konya", cumra_ctx.crop_ids)
    base = price_multipliers(cumra_ctx, cv)
    for opt in res.options.values():
        assert option_price_risk(opt, cumra_ctx, base)["cvar5"] <= weather_only(opt)["cvar5"] + 1e-6
    opt = res.options["current"]                                   # pancar + mısır
    shocked = price_multipliers(cumra_ctx, cv, {"maize_grain": -0.3})
    assert option_price_risk(opt, cumra_ctx, shocked)["mean_margin"] < option_price_risk(opt, cumra_ctx, base)["mean_margin"]
