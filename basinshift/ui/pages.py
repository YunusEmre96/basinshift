"""Streamlit sayfaları."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..config import ROOT
from ..data.hub import any_synthetic
from ..data.schema import SPECS
from ..engine.crop_detect import crop_group, detect_groups
from ..engine.risk import bare_soil_by_month, monthly_climate_risk, plan_calendar
from ..engine.trends import climate_trends
from ..explain.confidence import METHOD_CONFIDENCE, label as conf_label
from ..explain.fmt import area_factor, money, num, option_text, water
from ..explain.headline import headline
from ..explain.why import explain
from ..knowledge.rules import check_plan, list_rule_packs, load_rule_pack
from ..knowledge.tables import basin_crops, load_crops, load_economics, load_glossary
from ..optimizer.search import NoFeasiblePlan, PlanOption
from ..textutil import loc
from . import components as ui
from . import state
from .i18n import t

CARD_ORDER = ("current", "profit", "aquifer", "balance")


def L() -> str:
    return st.session_state["lang"]


def card_title(key: str, irrigated: bool) -> tuple[str, str]:
    lang = L()
    k = "aquifer_rainfed" if key == "aquifer" and not irrigated else key
    return t(f"card_{k}", lang), t(f"card_{k}_sub", lang)


def crop_label(cid: str) -> str:
    return load_crops()[cid].name(L())


def site_prov() -> dict:
    """Seçili noktanın veri kaynak kaydı (oturumlar arası paylaşılan 'son kayıt' değil)."""
    return state.site_data().provenance


def all_prov() -> dict:
    """Nokta veri setleri + havza ölçeğindeki GRACE kaydı (kenar çubuğu ve yöntem tablosu için)."""
    prov = dict(site_prov())
    hub = state.get_hub()
    b = state.current_basin()
    if ("water_storage", b.id) not in hub.records:
        try:
            hub.water_storage(b)
        except Exception:  # noqa: BLE001 — havza verisi alınamazsa kayıt 'missing' olarak kalır
            pass
    wp = hub.records.get(("water_storage", b.id))
    if wp is not None:
        prov["water_storage"] = wp
    return prov


def src_tag(ds: str) -> str:
    p = site_prov().get(ds)
    if p is None or p.is_real:
        return ""
    return " · " + ("sentetik" if L() == "tr" else "synthetic") if p.is_synthetic else " · " + p.label(L())


# ---------------------------------------------------------------------------
# Kenar çubuğu
# ---------------------------------------------------------------------------
def _on_basin_change():
    ss = st.session_state
    b = state.basins()[ss["basin_id"]]
    ss["site_id"] = b.sites[0].id
    ss["lat"], ss["lon"] = b.sites[0].lat, b.sites[0].lon
    state.reset_field_defaults()


def _on_site_change():
    ss = st.session_state
    if ss["site_id"] != "custom":
        site = state.current_basin().site(ss["site_id"])
        ss["lat"], ss["lon"] = site.lat, site.lon
        state.reset_field_defaults()


def sidebar() -> None:
    ss = st.session_state
    with st.sidebar:
        st.markdown(f"## {t('app_title', L())}")
        st.radio(t("language", L()), ["tr", "en"], key="lang", horizontal=True,
                 format_func=lambda x: "Türkçe" if x == "tr" else "English")
        lang = L()
        bs = state.basins()
        st.selectbox(t("basin", lang), list(bs), key="basin_id", on_change=_on_basin_change,
                     format_func=lambda b: bs[b].name(lang))
        b = state.current_basin()
        site_opts = [s.id for s in b.sites] + ["custom"]
        st.selectbox(t("field_location", lang), site_opts, key="site_id", on_change=_on_site_change,
                     format_func=lambda s: t("custom_point", lang) if s == "custom" else b.site(s).name)
        if ss["site_id"] == "custom":
            c1, c2 = st.columns(2)
            c1.number_input(t("latitude", lang), -90.0, 90.0, key="lat", format="%.3f", step=0.01)
            c2.number_input(t("longitude", lang), -180.0, 180.0, key="lon", format="%.3f", step=0.01)
        st.radio(t("area_unit", lang), ["da", "ha"], key="unit", horizontal=True)
        st.toggle(t("present_mode", lang), key="present", help=t("present_mode_help", lang))

        st.markdown(f"#### {t('scenario', lang)}")
        st.slider(t("d_temp", lang), -1.0, 4.0, step=0.5, key="d_temp")
        st.slider(t("d_precip", lang), -40.0, 20.0, step=5.0, key="d_precip")
        st.selectbox(t("cmip6", lang), ["", "ssp245", "ssp585"], key="cmip6",
                     format_func=lambda x: t("cmip6_none", lang) if not x else t(f"cmip6_{x}", lang))

        prov = all_prov()
        n_real = sum(1 for p in prov.values() if p.is_real)
        st.markdown(f'<div class="bs-realcount">{t("real_count", lang, n=n_real, total=len(prov))}</div>',
                    unsafe_allow_html=True)
        with st.expander(t("data_sources", lang)):
            for ds, p in prov.items():
                mark = "🟢" if p.is_real and not p.fell_back else ("🟡" if p.is_synthetic and not p.fell_back else "🟠")
                st.markdown(f"{mark} **{t('ds_' + ds, lang)}** · {p.label(lang)}"
                            + ((" · önbellek" if lang == "tr" else " · cached") if p.from_cache else ""))
                for w in p.warning_texts(lang, 2):
                    st.caption(w[:220])


def header(show_tagline: bool = True) -> None:
    lang = L()
    if show_tagline:
        st.markdown(f"# {t('app_title', lang)}")
        st.markdown(f'<p class="bs-tagline">{t("app_tagline", lang)}</p>', unsafe_allow_html=True)
    sc = state.scenario()
    if not sc.is_baseline:
        parts = []
        if sc.cmip6:
            parts.append(t(f"cmip6_{sc.cmip6}", lang))
        if sc.d_temp_c:
            parts.append(f"{sc.d_temp_c:+.1f} °C")
        if sc.precip_pct:
            parts.append(f"{sc.precip_pct:+.0f}% " + ("yağış" if lang == "tr" else "rain"))
        st.info(t("scenario_active", lang, txt=", ".join(parts)))


def banners() -> None:
    lang = L()
    prov = site_prov()
    if any_synthetic(prov):
        st.markdown(f'<div class="bs-banner">{t("synthetic_banner", lang)}</div>', unsafe_allow_html=True)
    for ds, p in prov.items():
        if p.requested != "synthetic" and p.is_synthetic:
            st.warning(t("fallback_warning", lang, dataset=t("ds_" + ds, lang), requested=p.requested))
        elif p.is_default:
            st.warning(t("default_warning", lang, dataset=t("ds_" + ds, lang), label=p.label(lang)))


def footer() -> None:
    st.markdown(f'<div class="bs-disclaimer">{t("disclaimer", L())}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tarla
# ---------------------------------------------------------------------------
def page_field() -> None:
    lang = L()
    ss = st.session_state
    b = state.current_basin()
    crops = load_crops()
    ids = basin_crops(b.id)

    b1, b2, _ = st.columns([2, 1.2, 3])
    b1.button(t("demo_button", lang), on_click=state.load_demo, type="primary")
    if b2.button(t("go_plans", lang) + " →"):
        target = state.page("plans")
        if target is not None:
            st.switch_page(target)
    if ss.pop("demo_loaded", False):
        st.success(t("demo_loaded", lang))

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(f"### {t('history', lang)}")
        hc = st.columns(2)
        for i, y in enumerate((state.PLAN_START - 2, state.PLAN_START - 1)):
            hc[i].selectbox(str(y), ids, key=f"hist_{i}", format_func=crop_label)
        ss["history"] = [ss["hist_0"], ss["hist_1"]]

        st.markdown(f"### {t('current_plan', lang)}")
        pc = st.columns(4)
        for i, y in enumerate(range(state.PLAN_START, state.PLAN_START + state.HORIZON)):
            pc[i].selectbox(str(y), ids, key=f"plan_{i}", format_func=crop_label)
        ss["current_plan"] = [ss[f"plan_{i}"] for i in range(state.HORIZON)]

        st.markdown(f"### {t('water_setup', lang)}")
        w1, w2, w3 = st.columns(3)
        w1.toggle(t("irrigated", lang), key="irrigated")
        if ss["irrigated"]:
            w2.selectbox(t("irrigation_method", lang), ["drip", "sprinkler", "surface"], key="method",
                         format_func=lambda m: t(f"irr_{m}", lang))
        w3.toggle(t("water_restricted", lang), key="restricted")
        if ss["irrigated"]:
            c1, c2 = st.columns([1, 2])
            c1.checkbox(t("water_unlimited", lang), key="cap_unlimited")
            if not ss["cap_unlimited"]:
                c2.slider(t("water_cap", lang), 100.0, 1500.0, step=25.0, key="cap_val")

        st.markdown(f"### {t('constraints', lang)}")
        tags = sorted({crops[c].equipment for c in ids if crops[c].equipment})
        if tags:
            st.multiselect(t("equipment", lang), tags, key="equipment", format_func=_equipment_label)
        contract_crops = [c for c in ids if crops[c].contract_required]
        if contract_crops:
            st.multiselect(t("contracts", lang), contract_crops, key="contracts", format_func=crop_label)
        st.multiselect(t("no_buyer", lang), [c for c in ids if c != "fallow"], key="no_buyer", format_func=crop_label)
        st.multiselect(t("excluded", lang), ids, key="excluded", format_func=crop_label)
        st.slider(t("min_forage", lang), 0.0, 1000.0, step=25.0, key="min_forage")

    with right:
        st.markdown(f"### {t('priorities', lang)}")
        for k in ("income", "risk", "water", "soil", "forage"):
            st.slider(t(f"prio_{k}", lang), 0.0, 5.0, step=0.5, key=f"w_{k}")
        st.markdown(f"### {t('options', lang)}")
        st.toggle(t("cover_crop", lang), key="cover")
        st.toggle(t("respect_breaks", lang), key="breaks")
        st.multiselect(t("rule_packs", lang), list_rule_packs(), key="packs",
                       format_func=lambda p: load_rule_pack(p).name(lang))
        _location_map(b)

    st.markdown(f"### {t('verify_history', lang)}")
    st.caption(t("verify_explain", lang))
    _verify_history()


def _equipment_label(tag: str) -> str:
    names = {
        "pancar_sokum": ("Pancar sökme makinesi", "Beet harvester"),
        "patates_sokum": ("Patates sökme makinesi", "Potato harvester"),
        "baklagil_hasat": ("Baklagil hasat tablası", "Pulse harvesting header"),
        "silaj_makinesi": ("Silaj makinesi", "Forage harvester"),
        "ot_bicme": ("Ot biçme-balyalama", "Hay mower/baler"),
        "pamuk_hasat": ("Pamuk hasat makinesi", "Cotton picker"),
        "celtik": ("Çeltik ekipmanı", "Rice equipment"),
        "domates_hasat": ("Domates hasat makinesi", "Tomato harvester"),
    }
    tr, en = names.get(tag, (tag, tag))
    return tr if L() == "tr" else en


def _location_map(b) -> None:
    site = state.current_site()
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=[s.lat for s in b.sites], lon=[s.lon for s in b.sites], text=[s.name for s in b.sites],
        mode="markers+text", textposition="top right", marker=dict(size=10, color=ui.MUTED), hoverinfo="text",
    ))
    fig.add_trace(go.Scattermap(lat=[site.lat], lon=[site.lon], mode="markers",
                                marker=dict(size=16, color=ui.WATER), hoverinfo="skip"))
    fig.update_layout(map=dict(style="open-street-map", center=dict(lat=b.map_center[0], lon=b.map_center[1]),
                               zoom=b.map_zoom - 0.5),
                      height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _verify_history() -> None:
    lang = L()
    b = state.current_basin()
    sd = state.site_data()
    nd = sd.ndvi
    if nd is None or nd.empty:
        st.caption("NDVI —")
        return
    crops, econ = load_crops(), load_economics(b.id)
    years = [state.PLAN_START - 2, state.PLAN_START - 1]
    det = detect_groups(nd, years, b.is_southern)
    rows = []
    for y, declared in zip(years, st.session_state["history"]):
        exp = crop_group(crops[declared], econ[declared].plant_month, b.is_southern)
        got = det[y]["group"]
        rows.append({
            ("Yıl" if lang == "tr" else "Year"): y,
            t("declared", lang): f"{crops[declared].name(lang)} ({t('group_' + exp, lang)})",
            t("detected", lang): t("group_" + got, lang),
            "": ("✅ " + t("match", lang)) if got == exp else ("⚠️ " + t("mismatch", lang) if got != "unknown" else "—"),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    del sd


# ---------------------------------------------------------------------------
# İklim geçmişi
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False, max_entries=16)
def _status_data(site_key: tuple):
    sd = state._site_data(site_key)
    risk = monthly_climate_risk(sd.climate, sd.et0)
    basin = state.basins()[site_key[0]]
    trends = climate_trends(sd.climate, sd.et0, basin.ag_year_start_month)
    return risk, trends


def page_status() -> None:
    lang = L()
    b = state.current_basin()
    site = state.current_site()
    sd = state.site_data()
    risk, trends = _status_data(state._site_key(site))
    nd = sd.ndvi
    bare = bare_soil_by_month(nd)

    st.markdown(f"### {t('risk_calendar', lang)}")
    st.caption(t("risk_calendar_help", lang))
    st.plotly_chart(ui.risk_heatmap(risk, bare, lang), width="stretch", config={"displayModeBar": False})

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"### {t('water_month', lang)}")
        st.plotly_chart(ui.water_month_chart(risk, lang), width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown(f"### {t('trends', lang)}")
        rows = []
        for tr in trends:
            name = tr.name if lang == "tr" else {
                "Yıllık ortalama sıcaklık": "Annual mean temperature", "Yaz en yüksek sıcaklık ort.": "Summer mean max temperature",
                "Yıllık yağış": "Annual precipitation", "32 °C üstü gün sayısı": "Days above 32 °C", "Yıllık ET0": "Annual ET0",
            }.get(tr.name, tr.name)
            rows.append({
                ("Gösterge" if lang == "tr" else "Indicator"): name,
                ("10 yılda değişim" if lang == "tr" else "Change per decade"): f"{tr.slope_per_decade:+.2f} {tr.unit}",
                ("İlk 10 yıl → son 10 yıl" if lang == "tr" else "First → last 10 yrs"): f"{num(tr.first_mean, lang, 1)} → {num(tr.last_mean, lang, 1)}",
                "p": f"{tr.p_value:.3f}",
                "": t("trend_sig", lang) if tr.significant else t("trend_nonsig", lang),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    c3, c4 = st.columns(2, gap="large")
    with c3:
        st.markdown(f"### {t('ndvi_series', lang)}")
        if nd is not None and not nd.empty:
            recent = nd.loc[nd.index >= nd.index.max() - pd.Timedelta(days=365 * 6)]
            fig = go.Figure()
            for src, color in (("MODIS", "#AEB8AC"), ("HLS", "#2E7D4F")):
                s = recent[recent["source"] == src]
                fig.add_scatter(x=s.index, y=s["ndvi"], mode="markers" if src == "HLS" else "lines",
                                name=f"{src} ({'30 m' if src == 'HLS' else '250 m'}){src_tag('ndvi')}",
                                marker=dict(size=4, color=color), line=dict(color=color))
            st.plotly_chart(ui._layout(fig, 300), width="stretch", config={"displayModeBar": False})
    with c4:
        st.markdown(f"### {t('soil_moisture_series', lang)}")
        sm = sd.soil_moisture
        if sm is not None and not sm.empty:
            fig = go.Figure()
            fig.add_scatter(x=sm.index, y=sm["sm_rootzone"], mode="lines", name="0–100 cm" + src_tag("soil_moisture"),
                            line=dict(color=ui.WATER))
            fig.add_scatter(x=sm.index, y=sm["sm_surface"], mode="lines", name="0–5 cm",
                            line=dict(color="#7FA7B8", width=1))
            fig.update_yaxes(title="m³/m³")
            st.plotly_chart(ui._layout(fig, 300), width="stretch", config={"displayModeBar": False})

    st.markdown(f"### {t('sat_vs_ground', lang)}")
    sat = sd.precip_sat
    if sat is not None and not sat.empty:
        m_power = sd.climate["precip"].resample("MS").sum()
        m_sat = sat["precip"].resample("MS").sum()
        both = pd.concat([m_power.rename("power"), m_sat.rename("imerg")], axis=1).dropna().iloc[-72:]
        fig = go.Figure()
        fig.add_bar(x=both.index, y=both["power"], name="NASA POWER (0.5°)" + src_tag("climate_daily"), marker_color="#AEB8AC")
        fig.add_scatter(x=both.index, y=both["imerg"], name="GPM IMERG (0.1°)" + src_tag("precip_satellite"),
                        mode="lines", line=dict(color=ui.WATER))
        fig.update_yaxes(title="mm/ay" if lang == "tr" else "mm/month")
        st.plotly_chart(ui._layout(fig, 300), width="stretch", config={"displayModeBar": False})
        g = load_glossary()["satellite_vs_ground"][lang]
        st.caption(g["text"])
    else:
        p = site_prov().get("precip_satellite")
        st.caption(p.warning_texts(lang, 1)[0] if p and p.warnings else "—")


# ---------------------------------------------------------------------------
# Planlar
# ---------------------------------------------------------------------------
def _get_result():
    with st.spinner(t("computing", L())):
        try:
            ctx = state.context()
        except ValueError as exc:   # ör. yetersiz veri yılı
            st.error(t("data_error", L(), msg=str(exc)))
            return None, None
        try:
            return ctx, state.search_result()
        except NoFeasiblePlan as exc:
            st.error(t("no_plan", L()) + (f"  ({exc})" if L() == "tr" else ""))
            return ctx, None


def page_plans() -> None:
    lang = L()
    unit = st.session_state["unit"]
    ctx, res = _get_result()
    if res is None:
        return
    syn = any_synthetic(ctx.provenance)
    crops = ctx.crops
    cur = res.options.get("current")
    if st.session_state.pop("demo_loaded", False):
        st.success(t("demo_loaded", lang))

    best = res.options.get("balance")
    if cur is not None and best is not None:
        txt = headline(cur, best, card_title("balance", ctx.settings.irrigated)[0], ctx.basin.currency_symbol,
                       ctx.settings.irrigated, lang, unit)
        cls = cur.detail["status"]
        st.markdown(f'<div class="bs-headline {cls}">{txt}</div>', unsafe_allow_html=True)

    if cur is not None:
        chk = check_plan(list(cur.parts[0][0]), ctx.settings.plan_years, ctx.settings.history, ctx.crop_ids,
                         crops, ctx.packs, ctx.settings.irrigated, ctx.settings.water_restricted)
        if chk.legal:
            with st.container(border=True):
                st.markdown(ui.status_html(chk.status, lang) + f" &nbsp; **{t('card_current', lang)}**",
                            unsafe_allow_html=True)
                by_year: dict[int, list[str]] = {}
                for v in chk.legal:
                    rule_txt = v.text(lang).split(": ", 1)[-1]
                    by_year.setdefault(v.year, [])
                    if rule_txt not in by_year[v.year]:
                        by_year[v.year].append(rule_txt)
                plan = list(cur.parts[0][0])
                st.markdown("\n".join(
                    f"- **{y} · {crops[plan[ctx.settings.plan_years.index(y)]].name(lang)}** — " + " ".join(rules)
                    for y, rules in sorted(by_year.items())))

    cols = st.columns(4, gap="medium")
    for col, key in zip(cols, CARD_ORDER):
        opt = res.options.get(key)
        if opt is None:
            continue
        with col:
            title, sub = card_title(key, ctx.settings.irrigated)
            if opt.is_mix:
                sub = f"{sub} · {t('mix_note', lang)}"
            ui.option_column(opt, title, sub, ctx, lang, unit, syn, current_key=key == "current")
            with st.expander(t("why_title", lang)):
                ui.why_panel(explain(opt, cur, ctx, ctx.provenance, lang, unit), lang)
    st.markdown(ui.confidence_legend(lang, syn), unsafe_allow_html=True)

    if res.excluded_crops:
        st.caption(t("excluded_crops", lang) + ": " + ", ".join(
            f"{crops[c].name(lang)} ({t('why_' + why, lang)})" for c, why in res.excluded_crops.items()))

    st.markdown(f"### {t('income_spread', lang)}")
    st.caption(t("income_spread_help", lang))
    order = [(k, card_title(k, ctx.settings.irrigated)[0]) for k in CARD_ORDER]
    st.plotly_chart(ui.income_box(res.options, crops, ctx, lang, unit, order), width="stretch",
                    config={"displayModeBar": False})

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown(f"### {t('calendar_strip', lang)}")
        pick = st.selectbox(" ", [k for k in CARD_ORDER if k in res.options],
                            format_func=lambda k: card_title(k, ctx.settings.irrigated)[0], key="cal_pick",
                            label_visibility="collapsed")
        opt = res.options[pick]
        cal = plan_calendar(list(opt.main_plan), ctx.settings.plan_years, crops, ctx.econ, ctx.basin)
        st.plotly_chart(ui.calendar_chart(cal, crops, None, lang), width="stretch", config={"displayModeBar": False})
        st.caption(("Kalın şerit: sezon · kırmızı: sıcak stresine hassas dönem · mavi noktalı: dona hassas dönem"
                    if lang == "tr" else "Thick bar: season · red: heat-sensitive stage · blue dotted: frost-sensitive stage"))
        adv = check_plan(list(opt.main_plan), ctx.settings.plan_years, ctx.settings.history, ctx.crop_ids, crops,
                         ctx.packs, ctx.settings.irrigated, ctx.settings.water_restricted).advisory
        if adv:
            st.markdown(f"**{t('advisories', lang)}**")
            st.markdown("\n".join(f"- {v.text(lang)}" for v in adv))
    with c2:
        st.markdown(f"### {t('cover_tradeoff', lang)}")
        st.caption(t("cover_tradeoff_help", lang))
        _cover_tradeoff(res.options["balance"], unit)

    with st.expander(t("pareto_title", lang)):
        st.caption(t("pareto_help", lang, n=res.n_total, f=len(res.feasible), p=len(res.pareto)))
        labels = {k: card_title(k, ctx.settings.irrigated)[0] for k in res.options}
        st.plotly_chart(ui.pareto_chart(res, res.options, labels, ctx, unit, lang), width="stretch")
        f = area_factor(unit)
        top = res.pareto.sort_values("score", ascending=False).head(25)
        st.dataframe(pd.DataFrame({
            "Plan": [" → ".join(crops[c].name(lang) for c in p) for p in top["plan"]],
            t("mean_income", lang): (top["mean_margin"] * f).round(0),
            t("bad_income", lang): (top["cvar5"] * f).round(0),
            t("water_use", lang): (top["water_mean"] * f).round(0),
            t("soil_health", lang): top["soil"].round(0),
            t("forage", lang): top["forage"].round(0),
        }), hide_index=True, width="stretch")


def _cover_tradeoff(opt: PlanOption, unit: str) -> None:
    lang = L()
    plan = list(opt.main_plan)
    base_ctx = state.context(cover=False)
    cov_ctx = state.context(cover=True)
    a, c = base_ctx.detail(plan), cov_ctx.detail(plan)
    if not cov_ctx.cover_mask(cov_ctx.idx(plan)[None, :]).any():
        st.caption("Bu planda örtü bitkisine uygun boşluk yok." if lang == "tr" else "No suitable gap for a cover crop in this plan.")
        return
    sym = base_ctx.basin.currency_symbol
    rows = [
        (t("mean_income", lang), money(a["summary"]["mean_margin"], sym, unit, lang), money(c["summary"]["mean_margin"], sym, unit, lang)),
        (t("soil_health", lang), f"{a['soil']['soil']:.0f}", f"{c['soil']['soil']:.0f}"),
        (t("erosion", lang), f"{a['soil']['erosion']:.0f}", f"{c['soil']['erosion']:.0f}"),
    ]
    if base_ctx.settings.irrigated:
        rows.insert(1, (t("water_use", lang), water(a["summary"]["water_mean"], unit, lang), water(c["summary"]["water_mean"], unit, lang)))
    else:
        rows.insert(1, (t("bad_income", lang), money(a["summary"]["cvar5"], sym, unit, lang), money(c["summary"]["cvar5"], sym, unit, lang)))
    st.dataframe(pd.DataFrame(rows, columns=["", "Örtüsüz" if lang == "tr" else "Without", "Örtülü" if lang == "tr" else "With"]),
                 hide_index=True, width="stretch")


# ---------------------------------------------------------------------------
# İki gelecek
# ---------------------------------------------------------------------------
def page_futures() -> None:
    lang = L()
    unit = st.session_state["unit"]
    ctx, res = _get_result()
    if res is None or "current" not in res.options:
        return
    st.markdown(f"## {t('futures_title', lang)}")
    pick = st.radio(t("futures_pick", lang), ["balance", "profit", "aquifer"], horizontal=True,
                    format_func=lambda k: card_title(k, ctx.settings.irrigated)[0], key="fut_pick")
    cur, new = res.options["current"], res.options[pick]
    years = ctx.settings.plan_years
    f = area_factor(unit)
    sym = ctx.basin.currency_symbol

    c1, c2 = st.columns(2, gap="large")
    for col, opt, title in ((c1, cur, t("future_habit", lang)), (c2, new, t("future_basinshift", lang))):
        with col:
            st.markdown(f"### {title}")
            st.markdown(ui.status_html(opt.detail["status"], lang)
                        + ui.strip_html(opt.parts, years, ctx.crops, lang,
                                        [i for i, v in enumerate(opt.detail.get("legal_viol", [])) if v] if not opt.is_mix else []),
                        unsafe_allow_html=True)

    d_water = (new.metrics["water_total"] - cur.metrics["water_total"]) * f
    d_sup = (new.detail["sim"]["support"].sum(axis=1).mean() - cur.detail["sim"]["support"].sum(axis=1).mean()) * f
    d_inc = (new.metrics["mean_margin"] - cur.metrics["mean_margin"]) * 4 * f
    k1, k2, k3 = st.columns(3)
    if ctx.settings.irrigated:
        k1.markdown(f'<div class="bs-big water">{d_water:+,.0f} m³/{unit}</div><div class="bs-big-label">{t("water_saved_4y", lang)}</div>'.replace(",", "." if lang == "tr" else ","),
                    unsafe_allow_html=True)
    k2.markdown(f'<div class="bs-big">{d_sup:+,.0f} {sym}/{unit}</div><div class="bs-big-label">{t("support_kept", lang)}</div>'.replace(",", "." if lang == "tr" else ","),
                unsafe_allow_html=True)
    k3.markdown(f'<div class="bs-big">{d_inc:+,.0f} {sym}/{unit}</div><div class="bs-big-label">{("4 yılda ortalama kâr farkı" if lang == "tr" else "Average margin difference over 4 years")}</div>'.replace(",", "." if lang == "tr" else ","),
                unsafe_allow_html=True)

    dets = [(t("future_habit", lang), cur.detail, ui.MUTED), (t("future_basinshift", lang), new.detail, "#2E7D4F")]
    st.markdown(f"### {t('income_band', lang)}")
    st.plotly_chart(ui.band_chart(dets, "margin", years, f, f"{sym}/{unit}"), width="stretch", config={"displayModeBar": False})
    if ctx.settings.irrigated:
        st.markdown(f"### {t('water_band', lang)}")
        dets_w = [(n, d, c if c != "#2E7D4F" else ui.WATER) for n, d, c in dets]
        st.plotly_chart(ui.band_chart(dets_w, "water_m3", years, f, f"m³/{unit}"), width="stretch", config={"displayModeBar": False})
    st.caption(t("futures_scenario", lang))


# ---------------------------------------------------------------------------
# Havza
# ---------------------------------------------------------------------------
def page_basin() -> None:
    lang = L()
    unit = st.session_state["unit"]
    b = state.current_basin()
    hub = state.get_hub()
    f = area_factor(unit)
    st.markdown(f"## {t('basin_title', lang)}")

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown(f"### {t('grace_title', lang)}")
        ws = hub.water_storage(b)
        wp = hub.records.get(("water_storage", b.id))
        if wp is not None and not wp.is_real:
            st.caption(("Kaynak: " if lang == "tr" else "Source: ") + wp.label(lang)
                       + (" — " + wp.warning_texts(lang, 1)[0][:200] if wp.warnings else ""))
        if ws is not None and not ws.empty:
            full = ws.reindex(pd.date_range(ws.index.min(), ws.index.max(), freq="MS"))
            fig = go.Figure()
            fig.add_scatter(x=full.index, y=full["tws_anomaly_cm"], mode="lines", line=dict(color=ui.WATER, width=2),
                            name="TWS", connectgaps=False)
            x = (ws.index - ws.index[0]).days / 365.25
            k, c0 = np.polyfit(x, ws["tws_anomaly_cm"], 1)
            fig.add_scatter(x=ws.index, y=c0 + k * x, mode="lines", line=dict(color=ui.INK, dash="dash", width=1),
                            name=(f"Eğilim {k:+.1f} cm/yıl" if lang == "tr" else f"Trend {k:+.1f} cm/yr"))
            fig.update_yaxes(title="cm")
            st.plotly_chart(ui._layout(fig, 320), width="stretch", config={"displayModeBar": False})
            st.caption(t("grace_note", lang))
    with c2:
        st.markdown(f"### {t('sinkholes', lang) if b.id == 'konya' else b.name(lang)}")
        for fact in b.facts(lang):
            st.markdown(f'<div class="bs-fact">{fact}</div>', unsafe_allow_html=True)
        sink = Path(hub.cfg["data"]["files_dir"]) / "sinkholes.csv"
        if b.id == "konya":
            if sink.exists():
                df = pd.read_csv(sink)
                fig = go.Figure(go.Scattermap(lat=df["lat"], lon=df["lon"], mode="markers",
                                              marker=dict(size=6, color=df.get("year", 0), colorscale="Reds")))
                fig.update_layout(map=dict(style="open-street-map", center=dict(lat=b.map_center[0], lon=b.map_center[1]), zoom=7),
                                  height=280, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption(t("sinkholes_missing", lang))

    frac = st.slider(t("sust_fraction", lang), 0.4, 1.0, value=float(b.sustainable_water_fraction), step=0.05, key="sust_frac")
    with st.spinner(t("computing", lang)):
        r = state.basin_result(frac)
    st.caption(t("basin_synthetic", lang))

    sym = r.currency_symbol
    m = r.metrics
    labels = {"current": t("scen_current", lang), "uncoordinated": t("scen_uncoord", lang), "coordinated": t("scen_coord", lang)}
    colors = {"current": ui.MUTED, "uncoordinated": "#B3392F", "coordinated": "#2E7D4F"}
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown(f"### {t('income_per_area', lang)}")
        fig = go.Figure(go.Bar(x=[labels[i] for i in m.index], y=m["income_per_da"] * f,
                               marker_color=[colors[i] for i in m.index]))
        fig.update_yaxes(title=f"{sym}/{unit}/{'yıl' if lang == 'tr' else 'yr'}")
        st.plotly_chart(ui._layout(fig, 300), width="stretch", config={"displayModeBar": False})
    with g2:
        st.markdown(f"### {t('water_per_area', lang)}")
        fig = go.Figure(go.Bar(x=[labels[i] for i in m.index], y=m["water_per_da"] * f,
                               marker_color=[colors[i] for i in m.index]))
        total_area = sum(ft.area_da for ft in r.farm_types)
        fig.add_hline(y=r.water_budget_m3 / total_area * f, line_dash="dash", line_color=ui.WATER,
                      annotation_text=("Sürdürülebilir bütçe" if lang == "tr" else "Sustainable budget"))
        fig.update_yaxes(title=f"m³/{unit}/{'yıl' if lang == 'tr' else 'yr'}")
        st.plotly_chart(ui._layout(fig, 300), width="stretch", config={"displayModeBar": False})

    total_area = sum(ft.area_da for ft in r.farm_types)
    k1, k2 = st.columns(2, gap="large")
    with k1:
        st.markdown(f"### {t('poa', lang)}")
        inc = money(r.price_of_anarchy_income / total_area, sym, unit, lang)
        wat = water(r.price_of_anarchy_water / total_area, unit, lang)
        st.markdown(t("poa_text", lang, inc=inc, wat=wat))
    with k2:
        st.markdown(f"### {t('shadow', lang)}")
        if np.isfinite(r.shadow_price_water):
            st.markdown(f'<div class="bs-big water">{num(r.shadow_price_water, lang, 2)} {sym}/m³</div>', unsafe_allow_html=True)
            st.markdown(t("shadow_text", lang, v=f"{num(r.shadow_price_water, lang, 2)} {sym}"))
        for n in r.notes:
            st.warning(loc(n, lang))

    h1, h2 = st.columns(2, gap="large")
    with h1:
        st.markdown(f"### {t('cobweb_title', lang)}")
        crops = load_crops()
        pp = r.price_path
        movers = pp.std().sort_values(ascending=False).head(4).index
        fig = go.Figure()
        for c in movers:
            fig.add_scatter(x=pp.index, y=pp[c] * 100, mode="lines+markers", name=crops[c].name(lang),
                            line=dict(color=crops[c].color, width=2))
        fig.add_hline(y=100, line_color=ui.MUTED, line_dash="dot")
        fig.update_yaxes(title=("Fiyat endeksi (bugün = 100)" if lang == "tr" else "Price index (today = 100)"))
        st.plotly_chart(ui._layout(fig, 320), width="stretch", config={"displayModeBar": False})
    with h2:
        st.markdown(f"### {t('budget_curve', lang)}")
        bc = r.budget_curve
        if not bc.empty:
            fig = go.Figure(go.Scatter(x=bc["fraction"] * 100, y=bc["shadow_price"], mode="lines+markers",
                                       line=dict(color=ui.WATER, width=3)))
            fig.update_xaxes(title=("Su bütçesi (bugünkü çekimin %)" if lang == "tr" else "Water budget (% of today)"))
            fig.update_yaxes(title=f"{sym}/m³")
            st.plotly_chart(ui._layout(fig, 320), width="stretch", config={"displayModeBar": False})

    st.markdown(f"### {t('pattern_title', lang)}")
    crops = load_crops()
    fig = go.Figure()
    scen_rows = [(t("scen_current", lang), r.current), (t("scen_uncoord", lang), r.uncoordinated_last),
                 (t("scen_coord", lang), r.coordinated)]
    for j, cid in enumerate(r.crop_ids):
        vals = [x[:, j].sum() / max(x.sum(), 1) * 100 for _, x in scen_rows]
        if max(vals) < 0.5:
            continue
        fig.add_bar(y=[n for n, _ in scen_rows], x=vals, name=crops[cid].name(lang), orientation="h",
                    marker_color=crops[cid].color)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="%")
    st.plotly_chart(ui._layout(fig, 280), width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Karne
# ---------------------------------------------------------------------------
def page_report() -> None:
    from ..report.scorecard import build_scorecard_pdf

    lang = L()
    unit = st.session_state["unit"]
    ctx, res = _get_result()
    if res is None:
        return
    st.markdown(f"## {t('report_title', lang)}")
    st.caption(t("report_help", lang))
    keys = [k for k in ("balance", "profit", "aquifer", "current") if k in res.options]
    pick = st.radio(t("report_pick", lang), keys, horizontal=True,
                    format_func=lambda k: card_title(k, ctx.settings.irrigated)[0], key="rep_pick")
    c1, c2 = st.columns(2)
    st.session_state.setdefault("farmer_name", "")
    st.session_state.setdefault("field_area", 120.0 if unit == "da" else 12.0)
    name = c1.text_input(t("farmer_name", lang), key="farmer_name", max_chars=60)
    area = c2.number_input(t("field_area", lang) + f" ({unit})", 1.0, 100000.0, step=1.0, key="field_area")
    opt = res.options[pick]
    expl = explain(opt, res.options.get("current"), ctx, ctx.provenance, lang, unit)
    pdf = build_scorecard_pdf(opt, res.options.get("current"), ctx, expl, ctx.provenance, lang, unit,
                              farmer=name, field_area=area, title=card_title(pick, ctx.settings.irrigated)[0])
    st.download_button(t("download_pdf", lang), pdf, file_name=f"basinshift_karne_{ctx.site.id}_{pick}.pdf",
                       mime="application/pdf", type="primary")
    ui.option_column(opt, card_title(pick, ctx.settings.irrigated)[0], option_text(opt.parts, ctx.crops, lang),
                     ctx, lang, unit, any_synthetic(ctx.provenance))


# ---------------------------------------------------------------------------
# Yöntem ve veriler
# ---------------------------------------------------------------------------
def page_method() -> None:
    lang = L()
    hub = state.get_hub()
    st.markdown(f"## {t('method_title', lang)}")
    prov = all_prov()
    rows = []
    for ds, spec in SPECS.items():
        p = prov.get(ds)
        rows.append({
            t("col_dataset", lang): t("ds_" + ds, lang),
            t("col_product", lang): loc(spec.product, lang),
            t("col_resolution", lang): loc(spec.resolution, lang),
            t("col_source", lang): (p.label(lang) + (" (cache)" if p.from_cache else "")) if p else "—",
            t("col_scale", lang): spec.use_scale_tr if lang == "tr" else spec.use_scale_en,
            t("col_notes", lang): " ".join(p.messages(lang, 2)) if p else "",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    st.markdown(f"### {t('assumptions', lang)}")
    names = {
        "water": ("Su ihtiyacı", "Water need"), "yield": ("Verim", "Yield"), "risk": ("Risk (kötü dönem)", "Risk (bad periods)"),
        "income": ("Gelir", "Income"), "soil": ("Toprak sağlığı", "Soil health"), "support": ("Destek ve kurallar", "Support and rules"),
        "basin": ("Havza modeli", "Basin model"),
    }
    st.dataframe(pd.DataFrame([
        {("Sonuç" if lang == "tr" else "Result"): names[k][0 if lang == "tr" else 1],
         ("Güven" if lang == "tr" else "Confidence"): conf_label(v[0], lang),
         ("Neden" if lang == "tr" else "Why"): v[1] if lang == "tr" else v[2]}
        for k, v in METHOD_CONFIDENCE.items()
    ]), hide_index=True, width="stretch")
    st.markdown(
        "- " + ("Sıcak stresi: hassas dönemde Tmax ürün eşiğini ve yerel 90. yüzdeliği aşınca günde −%1,5; don −%3; hasatta >25 mm yağış −%2; toplam en fazla −%50."
                if lang == "tr" else "Heat stress: −1.5%/day when Tmax exceeds both the crop threshold and the local 90th percentile in the sensitive stage; frost −3%; >25 mm rain at harvest −2%; capped at −50%.")
        + "\n- " + ("Nadas yılı yağışının %20'si sonraki ürüne kalır; örtü bitkisi sonraki ürünün suyundan 60 mm alır."
                    if lang == "tr" else "20% of fallow-year rain carries over; a cover crop takes 60 mm from the next crop's water.")
        + "\n- " + ("Sulama randımanı: damla 0,90 · yağmurlama 0,75 · salma 0,60."
                    if lang == "tr" else "Irrigation efficiency: drip 0.90 · sprinkler 0.75 · surface 0.60.")
        + "\n- " + ("Ürün katsayıları, fiyatlar ve rotasyon etkileri tables/ klasöründedir; kod bilmeden güncellenebilir."
                    if lang == "tr" else "Crop coefficients, prices and rotation effects live in tables/ and can be edited without code.")
    )

    st.markdown(f"### {t('not_used', lang)}")
    st.markdown(
        "- **OpenET**: " + ("Türkiye'yi kapsamıyor (ABD ve Brezilya pilotu)." if lang == "tr" else "Does not cover Türkiye (US and Brazil pilot).")
        + "\n- **GRACE " + ("tarla ölçeğinde" if lang == "tr" else "at field scale") + "**: " + ("~300 km çözünürlük; yalnızca havza bağlamı." if lang == "tr" else "~300 km resolution; basin context only.")
        + "\n- **GEDI**: " + ("Orman biyokütlesi için; tek yıllık tarla ürünlerinde katkısı düşük." if lang == "tr" else "Built for forest biomass; little value for annual field crops.")
        + "\n- **" + ("Karbon sertifikası" if lang == "tr" else "Carbon certificate") + "**: " + ("Toprak karbonu değişimi 1–3 yılda uydudan doğrulanamaz." if lang == "tr" else "Soil carbon change cannot be verified from space in 1–3 years.")
    )

    st.markdown(f"### {t('glossary', lang)}")
    for _, entry in load_glossary().items():
        e = entry[lang]
        with st.expander(e["term"]):
            st.write(e["text"])

    st.markdown(f"### {t('how_switch', lang)}")
    st.code(("veri_indir.bat        # Windows: gerçek NASA verisini indirir, kontrol eder, config.yaml'ı günceller\n"
             "python scripts/setup_real_data.py   # aynı işin komut satırı hali\n# ayrıntı: docs/DATA_SWAP.md") if lang == "tr" else
            ("veri_indir.bat        # Windows: downloads real NASA data, checks it, updates config.yaml\n"
             "python scripts/setup_real_data.py   # the same from the command line\n# details: docs/DATA_SWAP.md"),
            language="bash")
    readme = ROOT / "docs" / "DATA_SWAP.md"
    if lang == "tr" and readme.exists():
        with st.expander("docs/DATA_SWAP.md"):
            st.markdown(readme.read_text(encoding="utf-8"))
