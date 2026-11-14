"""Arayüz durumu ve önbellekli hesaplar.

Streamlit her etkileşimde betiği baştan çalıştırır; ağır hesaplar
(veri, ürün-yıl tablosu, 20 bin planın taranması, havza LP'si) burada
parametreleriyle önbelleğe alınır.
"""
from __future__ import annotations

import streamlit as st

from ..basin.model import run_basin
from ..data.basins import Basin, Site, custom_site, load_basins
from ..data.hub import DataHub
from ..engine.field import FieldSettings
from ..engine.pipeline import build_context, load_site_data
from ..engine.scenarios import Scenario
from ..knowledge.tables import basin_crops, load_crops
from ..optimizer.search import Constraints, search

PLAN_START = 2027
HORIZON = 4

#: app.py'nin kaydettiği sayfa nesneleri (sayfalar arası geçiş düğmeleri için)
_PAGES: dict = {}


def register_pages(pages: dict) -> None:
    _PAGES.clear()
    _PAGES.update(pages)


def page(key: str):
    return _PAGES.get(key)


def goto(key: str) -> None:
    """Bir sonraki çalıştırmada verilen sayfaya geç (geri çağırma içinden güvenle çağrılır)."""
    st.session_state["_goto"] = key


@st.cache_resource(show_spinner=False)
def get_hub() -> DataHub:
    return DataHub()


def basins() -> dict[str, Basin]:
    return load_basins()


def current_basin() -> Basin:
    bid = st.session_state.get("basin_id", "konya")
    bs = basins()
    return bs.get(bid) or list(bs.values())[0]


def current_site() -> Site:
    b = current_basin()
    ss = st.session_state
    if ss.get("site_id") == "custom":
        return custom_site(b, float(ss["lat"]), float(ss["lon"]), irrigated=ss["irrigated"],
                           irrigation_method=ss["method"], water_restricted=ss["restricted"])
    return b.site(ss["site_id"])


def _site_key(site: Site) -> tuple:
    return (site.basin_id, site.id, site.lat, site.lon, site.elevation_m)


def _site_from_key(key: tuple) -> Site:
    basin_id, site_id, lat, lon, elev = key
    b = basins()[basin_id]
    if site_id.startswith("custom_"):
        return custom_site(b, lat, lon, elev)
    return b.site(site_id)


@st.cache_resource(show_spinner="Veri yükleniyor… / Loading data…")
def _site_data(site_key: tuple):
    site = _site_from_key(site_key)
    return load_site_data(get_hub(), site, basins()[site.basin_id])


def site_data():
    return _site_data(_site_key(current_site()))


def settings() -> FieldSettings:
    ss = st.session_state
    b = current_basin()
    cap = float(ss["cap_val"]) if (ss["irrigated"] and not ss["cap_unlimited"]) else None
    return FieldSettings(
        irrigated=bool(ss["irrigated"]),
        irrigation_method=ss["method"] if ss["irrigated"] else "none",
        water_restricted=bool(ss["restricted"]),
        farmer_water_cap_m3=cap,
        water_cost_per_m3=b.water_cost_per_m3,
        history=list(ss["history"]),
        plan_start_year=PLAN_START,
        horizon=HORIZON,
        cover_crop=bool(ss["cover"]),
    )


def scenario() -> Scenario:
    ss = st.session_state
    return Scenario(float(ss["d_temp"]), float(ss["d_precip"]), ss["cmip6"] or None)


def _settings_key(s: FieldSettings) -> tuple:
    return (s.irrigated, s.irrigation_method, s.water_restricted, s.farmer_water_cap_m3, s.water_cost_per_m3,
            tuple(s.history), s.plan_start_year, s.horizon, s.cover_crop)


def _settings_from_key(k: tuple) -> FieldSettings:
    return FieldSettings(k[0], k[1], k[2], k[3], k[4], list(k[5]), k[6], k[7], k[8])


@st.cache_resource(show_spinner=False, max_entries=24)
def _context(site_key: tuple, settings_key: tuple, scen: tuple, packs: tuple):
    site = _site_from_key(site_key)
    b = basins()[site.basin_id]
    return build_context(get_hub(), site, b, _settings_from_key(settings_key), Scenario(*scen),
                         list(packs), site_data=_site_data(site_key))


def context(scen: Scenario | None = None, cover: bool | None = None):
    s = settings()
    if cover is not None:
        s.cover_crop = cover
    sc = scen or scenario()
    return _context(_site_key(current_site()), _settings_key(s), (sc.d_temp_c, sc.precip_pct, sc.cmip6),
                    tuple(st.session_state["packs"]))


def constraints() -> Constraints:
    ss = st.session_state
    b = current_basin()
    crops = load_crops()
    ids = basin_crops(b.id)
    tags = {crops[c].equipment for c in ids if crops[c].equipment}
    contract_crops = {c for c in ids if crops[c].contract_required}
    return Constraints(
        available_equipment=set(ss["equipment"]) if set(ss["equipment"]) != tags else None,
        contracts=set(ss["contracts"]) if contract_crops else None,
        no_buyer=set(ss["no_buyer"]),
        excluded=set(ss["excluded"]),
        min_forage=float(ss["min_forage"]),
        respect_breaks=bool(ss["breaks"]),
    )


def weights() -> dict[str, float]:
    ss = st.session_state
    return {k: float(ss[f"w_{k}"]) for k in ("income", "risk", "water", "soil", "forage")}


@st.cache_resource(show_spinner=False, max_entries=24)
def _search(site_key, settings_key, scen, packs, cons_key, weights_key, current_plan):
    ctx = _context(site_key, settings_key, scen, packs)
    eq, ct, nb, ex, mf, rb = cons_key
    cons = Constraints(set(eq) if eq is not None else None, set(ct) if ct is not None else None,
                       set(nb), set(ex), mf, rb)
    return search(ctx, cons, dict(weights_key), list(current_plan))


def search_result(scen: Scenario | None = None):
    s = settings()
    sc = scen or scenario()
    c = constraints()
    cons_key = (
        tuple(sorted(c.available_equipment)) if c.available_equipment is not None else None,
        tuple(sorted(c.contracts)) if c.contracts is not None else None,
        tuple(sorted(c.no_buyer)), tuple(sorted(c.excluded)), c.min_forage, c.respect_breaks,
    )
    return _search(_site_key(current_site()), _settings_key(s), (sc.d_temp_c, sc.precip_pct, sc.cmip6),
                   tuple(st.session_state["packs"]), cons_key, tuple(sorted(weights().items())),
                   tuple(st.session_state["current_plan"]))


@st.cache_resource(show_spinner=False, max_entries=12)
def _basin(basin_id: str, scen: tuple, fraction: float):
    return run_basin(get_hub(), basins()[basin_id], Scenario(*scen), fraction, plan_start_year=PLAN_START)


def basin_result(fraction: float):
    sc = scenario()
    return _basin(st.session_state["basin_id"], (sc.d_temp_c, sc.precip_pct, sc.cmip6), round(fraction, 2))


# ---------------------------------------------------------------------------
# Varsayılanlar
# ---------------------------------------------------------------------------
def default_history(site: Site, ids: list[str]) -> list[str]:
    hist = dict(site.synthetic_history)
    out = [hist.get(PLAN_START - 2), hist.get(PLAN_START - 1)]
    fallback = "wheat" if "wheat" in ids else ids[0]
    return [h if h in ids else fallback for h in out]


def reset_field_defaults() -> None:
    """Havza/konum değişince ürün listesine bağlı alanları sıfırlar."""
    ss = st.session_state
    b = current_basin()
    site = b.sites[0] if ss.get("site_id") == "custom" else b.site(ss["site_id"])
    crops = load_crops()
    ids = basin_crops(b.id)
    hist = default_history(site, ids)
    ss["history"] = hist
    ss["current_plan"] = [hist[0], hist[1], hist[0], hist[1]]
    ss["irrigated"] = site.irrigated
    ss["method"] = site.irrigation_method if site.irrigated else "sprinkler"
    ss["restricted"] = site.water_restricted
    ss["equipment"] = sorted({crops[c].equipment for c in ids if crops[c].equipment})
    ss["contracts"] = sorted(c for c in ids if crops[c].contract_required)
    ss["no_buyer"] = []
    ss["excluded"] = []
    ss["packs"] = list(b.rule_packs)
    sync_plan_widgets()


def sync_plan_widgets() -> None:
    """Model listelerini (history, current_plan) seçim kutusu anahtarlarına yazar."""
    ss = st.session_state
    for i, c in enumerate(ss["history"]):
        ss[f"hist_{i}"] = c
    for i, c in enumerate(ss["current_plan"]):
        ss[f"plan_{i}"] = c


def init_state(cfg: dict) -> None:
    ss = st.session_state
    app = cfg.get("app", {})
    if not ss.get("lang"):
        ss["lang"] = app.get("default_language", "tr")
    if not ss.get("basin_id"):
        ss["basin_id"] = app.get("default_basin", "konya")
    if not ss.get("unit"):
        ss["unit"] = app.get("area_unit", "da")
    bs = basins()
    if not ss.get("site_id") and ss.get("basin_id") in bs:
        ss["site_id"] = bs[ss["basin_id"]].sites[0].id
    if ss.get("_init"):
        return
    b = bs[ss["basin_id"]]
    ss["lat"], ss["lon"] = b.sites[0].lat, b.sites[0].lon
    ss["cap_unlimited"] = True
    ss["cap_val"] = 600.0
    ss["min_forage"] = 0.0
    ss["cover"] = False
    ss["breaks"] = True
    for k, v in {"income": 3.0, "risk": 3.0, "water": 3.0, "soil": 2.0, "forage": 0.0}.items():
        ss[f"w_{k}"] = v
    ss["d_temp"], ss["d_precip"], ss["cmip6"] = 0.0, 0.0, ""
    ss["present"] = False
    ss["farmer_name"] = ""
    reset_field_defaults()
    ss["_init"] = True


PERSISTENT_WIDGETS = (
    "lang", "basin_id", "site_id", "unit", "present", "lat", "lon", "d_temp", "d_precip", "cmip6",
    "hist_0", "hist_1", "plan_0", "plan_1", "plan_2", "plan_3",
    "irrigated", "method", "restricted", "cap_unlimited", "cap_val",
    "equipment", "contracts", "no_buyer", "excluded", "min_forage",
    "w_income", "w_risk", "w_water", "w_soil", "w_forage", "cover", "breaks", "packs",
    "farmer_name", "field_area",
)


def persist_widgets() -> None:
    """Sayfalar arası geçişte Tarla sayfasının ayarlarını korur.

    Streamlit, bir çalıştırmada ekrana çizilmeyen kontrollerin değerlerini oturumdan
    siler. Her çalıştırmanın başında değeri kendine yeniden atamak, değeri kontrolden
    bağımsız bir oturum değeri yapar ve silinmesini engeller (Streamlit'in önerdiği yöntem).
    """
    ss = st.session_state
    for k in PERSISTENT_WIDGETS:
        if k in ss:
            ss[k] = ss[k]


def load_demo() -> None:
    """Mehmet Amca, Çumra: pancar 2025, mısır 2026, aynısını sürdürmeyi düşünüyor."""
    ss = st.session_state
    ss["basin_id"] = "konya"
    ss["site_id"] = "cumra"
    reset_field_defaults()
    ss["history"] = ["sugar_beet", "maize_grain"]
    ss["current_plan"] = ["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"]
    ss["irrigated"], ss["method"], ss["restricted"] = True, "sprinkler", True
    ss["cap_unlimited"] = True
    ss["min_forage"] = 0.0
    ss["d_temp"], ss["d_precip"], ss["cmip6"] = 0.0, 0.0, ""
    ss["unit"] = "da"
    ss["farmer_name"] = "Mehmet Amca"
    ss["field_area"] = 120.0
    sync_plan_widgets()
    ss["demo_loaded"] = True
    goto("plans")          # demo akışı: doğrudan Planlar sayfası
