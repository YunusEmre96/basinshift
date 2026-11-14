import numpy as np

from basinshift.basin.model import run_basin
from basinshift.explain.why import explain
from basinshift.optimizer.pareto import pareto_mask
from basinshift.optimizer.search import Constraints, search
from basinshift.report.scorecard import build_scorecard_pdf

CURRENT = ["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"]


def test_pareto_mask():
    obj = np.array([[1, 1], [2, 0], [0, 2], [0.5, 0.5], [2, 0]])
    m = pareto_mask(obj)
    assert m[0] and m[2] and not m[3]          # (0.5, 0.5) elenir
    assert m[1] ^ m[4]                          # aynı (2, 0) noktası yalnızca bir kez tutulur


def test_search_returns_compliant_cards(cumra_ctx):
    res = search(cumra_ctx, Constraints(), current_plan=CURRENT)
    assert set(res.options) == {"profit", "aquifer", "balance", "current"}
    for k in ("profit", "aquifer", "balance"):
        assert res.options[k].detail["status"] == "green"
    assert res.options["current"].detail["status"] == "red"
    assert res.options["aquifer"].metrics["water_mean"] <= res.options["profit"].metrics["water_mean"]
    assert res.options["profit"].metrics["mean_margin"] >= res.options["aquifer"].metrics["mean_margin"]
    assert res.n_total == (len(cumra_ctx.crop_ids) - len(res.excluded_crops)) ** 4


def test_constraints_exclude_crops(cumra_ctx):
    res = search(cumra_ctx, Constraints(contracts=set(), no_buyer={"chickpea"}), current_plan=CURRENT)
    for opt in res.options.values():
        if opt.key == "current":
            continue
        for plan, _ in opt.parts:
            assert "sugar_beet" not in plan and "chickpea" not in plan
    assert res.excluded_crops["sugar_beet"] == "contract"


def test_explanation_has_five_sections(cumra_ctx, hub):
    res = search(cumra_ctx, Constraints(), current_plan=CURRENT)
    e = explain(res.options["balance"], res.options["current"], cumra_ctx, cumra_ctx.provenance, "tr")
    for k in ("why", "evidence", "benefits", "gaps", "local_risks"):
        assert e[k], k
    assert any("SENTETİK" in g for g in e["gaps"])
    e_en = explain(res.options["profit"], res.options["current"], cumra_ctx, cumra_ctx.provenance, "en")
    assert e_en["why"][0].startswith("Suggested")


def test_basin_model(hub, konya):
    r = run_basin(hub, konya)
    assert r.lp_status == "optimal"
    assert r.shadow_price_water > 0
    assert r.metrics.loc["coordinated", "water"] <= r.water_budget_m3 * 1.0001
    np.testing.assert_allclose(r.coordinated.sum(axis=1), [ft.area_da for ft in r.farm_types], rtol=1e-6)
    assert np.isfinite(r.metrics["income"]).all()


def test_scorecard_pdf(cumra_ctx, hub):
    res = search(cumra_ctx, Constraints(), current_plan=CURRENT)
    opt = res.options["balance"]
    e = explain(opt, res.options["current"], cumra_ctx, cumra_ctx.provenance, "tr")
    pdf = build_scorecard_pdf(opt, res.options["current"], cumra_ctx, e, cumra_ctx.provenance, "tr", "da",
                              farmer="Mehmet Amca", field_area=120, title="Denge")
    assert pdf[:4] == b"%PDF" and len(pdf) > 10_000


def test_perennials_not_suggested(cumra_ctx):
    res = search(cumra_ctx, Constraints(), current_plan=CURRENT)
    assert res.excluded_crops.get("alfalfa") == "perennial"
    for k in ("profit", "aquifer", "balance"):
        for plan, _ in res.options[k].parts:
            assert "alfalfa" not in plan


def test_cooperative_sharing_is_budget_neutral(hub, konya):
    from basinshift.basin.model import cooperative_sharing, run_basin
    res = run_basin(hub, konya)
    tt = cooperative_sharing(res)
    assert abs(tt["transfer"].sum()) < 1e-6 * max(1.0, tt["income_coordinated"].abs().sum())
    # paylaşım sonrası toplam = koordineli toplam
    assert abs(tt["income_after"].sum() - tt["income_coordinated"].sum()) < 1e-3 * abs(tt["income_coordinated"].sum())
    # her üye aynı dekar başı ek kazancı alır; fazla pozitifse kimse kendi başına durumdan kötü değil
    assert np.allclose(tt["gain_per_da"], tt["gain_per_da"].iloc[0])
    if tt.attrs["surplus"] > 0:
        assert (tt["income_after"] >= tt["income_uncoordinated"] - 1e-6).all()
