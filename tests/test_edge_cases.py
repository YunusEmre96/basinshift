"""Uç durumlar ve yarışma günü eklenen parçalar (özet cümle, iki dilli notlar, veri kontrolü)."""
import sys
from pathlib import Path

import numpy as np
import pytest

from basinshift.data.basins import custom_site, load_basins
from basinshift.engine.field import FieldSettings
from basinshift.engine.pipeline import build_context
from basinshift.engine.scenarios import Scenario
from basinshift.explain.fmt import area_factor
from basinshift.explain.headline import headline, headline_numbers
from basinshift.explain.why import explain
from basinshift.optimizer.search import Constraints, NoFeasiblePlan, search
from basinshift.textutil import bi, loc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
MEHMET = ["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"]
TR_ONLY = set("çğışöüÇĞİŞÖÜ")


@pytest.fixture(scope="module")
def cumra_search(cumra_ctx):
    return search(cumra_ctx, current_plan=MEHMET)


def test_scanned_plan_count_matches_docs(cumra_search):
    # 13 ürün; çok yıllık yonca öneri dışında → 12^4. Belgelerdeki sayı bununla aynı olmalı.
    assert cumra_search.n_total == 12 ** 4 == 20736


def test_mehmet_story_holds(cumra_search):
    cur, bal = cumra_search.options["current"], cumra_search.options["balance"]
    assert cur.detail["status"] == "red" and cur.metrics["support_mean"] == 0
    for key in ("profit", "aquifer", "balance"):
        assert cumra_search.options[key].detail["status"] == "green"
    assert bal.metrics["water_mean"] < cur.metrics["water_mean"]
    assert cumra_search.options["aquifer"].metrics["water_mean"] <= bal.metrics["water_mean"]


def test_irrigation_water_is_plausible(cumra_ctx):
    # Literatür: Konya'da yağmurlamayla pancar için brüt ~700–1.000 m³/da (biraz pay bırakıldı)
    det = cumra_ctx.detail(["sugar_beet", "wheat", "chickpea", "barley"])
    beet = float(det["sim"]["water_m3"][:, 0].mean())
    assert 650 <= beet <= 1150, beet


def test_drip_saving_close_to_fao_konya_guide(hub, konya):
    # FAO Konya damla sulama rehberi: pancarda %25,5, dane mısırda %23,5 tasarruf.
    # Modelde tasarruf randıman oranından gelir (0,75 → 0,90 = %16,7); aynı yönde ve aynı mertebede olmalı.
    def water(method):
        st = FieldSettings(True, method, True, None, konya.water_cost_per_m3, ["wheat", "barley"], 2027)
        ctx = build_context(hub, konya.site("cumra"), konya, st)
        return ctx.detail(["sugar_beet", "wheat", "maize_grain", "wheat"])["summary"]["water_mean"]
    saving = 1 - water("drip") / water("sprinkler")
    assert 0.12 <= saving <= 0.30, saving


def test_extreme_scenario_runs_and_hurts(hub, konya, cumra_search):
    st = FieldSettings(True, "sprinkler", True, None, konya.water_cost_per_m3, ["sugar_beet", "maize_grain"], 2027)
    ctx = build_context(hub, konya.site("cumra"), konya, st, Scenario(4.0, -40.0, None))
    res = search(ctx, current_plan=MEHMET)
    assert set(res.options) == {"profit", "aquifer", "balance", "current"}
    for o in res.options.values():
        assert all(np.isfinite(v) for v in o.metrics.values() if isinstance(v, float))
    assert res.options["current"].metrics["water_mean"] > cumra_search.options["current"].metrics["water_mean"]


def test_impossible_constraints_raise_clear_error(cumra_ctx):
    cons = Constraints(excluded={"wheat", "barley", "chickpea", "lentil", "safflower", "vetch", "sunflower", "fallow"},
                       min_forage=1000.0)
    with pytest.raises(NoFeasiblePlan):
        search(cumra_ctx, cons, current_plan=MEHMET)


def test_custom_coordinate_and_all_basins(hub):
    for bid, basin in load_basins().items():
        ref = basin.sites[0]
        site = custom_site(basin, ref.lat + 0.2, ref.lon - 0.2, irrigated=ref.irrigated,
                           irrigation_method=ref.irrigation_method, water_restricted=ref.water_restricted)
        st = FieldSettings(ref.irrigated, ref.irrigation_method if ref.irrigated else "none", ref.water_restricted,
                           None, basin.water_cost_per_m3, [], 2027)
        res = search(build_context(hub, site, basin, st))
        assert {"profit", "aquifer", "balance"} <= set(res.options), bid


def test_english_explanations_have_no_turkish_leaks(cumra_ctx, cumra_search):
    cur = cumra_search.options["current"]
    allowed = ("Türkiye", "Çumra", "Karapınar", "₺")   # yer adları
    for key in ("profit", "aquifer", "balance", "current"):
        ex = explain(cumra_search.options[key], cur, cumra_ctx, cumra_ctx.provenance, "en", "ha")
        assert all(ex[k] for k in ("why", "evidence", "benefits", "gaps", "local_risks"))
        for line in sum(ex.values(), []):
            for a in allowed:
                line = line.replace(a, "")
            assert not (set(line) & TR_ONLY), line


def test_headline_numbers_and_text(cumra_search):
    cur, bal = cumra_search.options["current"], cumra_search.options["balance"]
    n = headline_numbers(cur, bal)
    assert n["water_saved"] == pytest.approx(cur.metrics["water_mean"] - bal.metrics["water_mean"])
    assert n["support_gain"] > 0 and n["water_saved"] > 0
    tr = headline(cur, bal, "Denge", "₺", True, "tr", "da")
    en = headline(cur, bal, "Balance", "₺", True, "en", "da")
    assert "kırmızı kart" in tr and "daha az su" in tr and "destek" in tr
    assert "red card" in en and "less water" in en and not (set(en.replace("₺", "")) & TR_ONLY)
    assert area_factor("ha") == 10 * area_factor("da")
    assert "m³/ha" in headline(cur, bal, "Denge", "₺", True, "tr", "ha")


def test_bilingual_messages():
    s = bi("Türkçe not", "English note")
    assert loc(s, "tr") == "Türkçe not" and loc(s, "en") == "English note"
    assert loc("düz metin", "tr") == "düz metin"
    assert loc("SENTETİK — gerçek ürün: NASA POWER (Agroclimatology, günlük)", "en") == \
        "SYNTHETIC — real product: NASA POWER (Agroclimatology, daily)"
    assert loc(None, "en") == ""


def test_provenance_messages_follow_language(cumra_ctx):
    cp = cumra_ctx.provenance["climate_daily"]
    assert "SYNTHETIC" in cp.product_text("en") and "SENTETİK" in cp.product_text("tr")
    for m in cp.messages("en"):
        assert not (set(m) & TR_ONLY), m


def test_data_checks_catch_unit_errors(hub, konya):
    import setup_real_data as s
    df = hub.climate_daily(konya.site("cumra"), konya)
    errs, warns, stats = s.check_climate(df, "konya")
    assert not errs and 250 <= stats["yıllık yağış (mm)"] <= 450
    bad = df.copy()
    bad["rs"] = bad["rs"] * 10            # MJ yerine yanlış birim
    assert s.check_climate(bad, "konya")[0]
    wet = df.copy()
    wet["precip"] = wet["precip"] * 2     # Konya için fazla yağış → uyarı
    assert s.check_climate(wet, "konya")[1]
    sm = hub.soil_moisture(konya.site("cumra"), konya)
    assert not s.check_soil_moisture(sm)[0]
    assert s.check_soil_moisture(sm * 100)[0]      # % cinsinden gelmiş veri yakalanır
    nd = hub.ndvi(konya.site("cumra"), konya)
    assert not s.check_ndvi(nd)[0]


def test_setup_script_edits_only_requested_sources(tmp_path):
    import re
    import setup_real_data as s
    cfg = tmp_path / "config.yaml"
    raw = (Path(__file__).resolve().parent.parent / "config.yaml").read_text(encoding="utf-8")
    cfg.write_text(re.sub(r"(\bclimate_daily:\s*)\S+", r"\g<1>synthetic", raw), encoding="utf-8")
    before = cfg.read_text(encoding="utf-8")
    assert s.set_config_sources(cfg, ["climate_daily"]) == ["climate_daily"]
    after = cfg.read_text(encoding="utf-8")
    assert "climate_daily: nasa" in after and "soil_moisture: null" in after
    assert len(before.splitlines()) == len(after.splitlines())
    assert s.set_config_sources(cfg, ["climate_daily"]) == []     # ikinci kez değişiklik yok


def test_no_credentials_in_repo():
    root = Path(__file__).resolve().parent.parent
    for name in ("config.yaml", ".env.example"):
        text = (root / name).read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("#") or "=" not in line and ":" not in line:
                continue
            for key in ("EARTHDATA_TOKEN", "EARTHDATA_PASSWORD", "EARTHDATA_USERNAME"):
                if line.strip().startswith(key):
                    assert line.split("=", 1)[1].strip() == "", f"{name}: {key} dolu olmamalı"
    assert ".env" in (root / ".gitignore").read_text(encoding="utf-8").split()
