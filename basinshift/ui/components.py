"""Görsel bileşenler: kart rozeti, tarla şeridi, plan sütunu, grafikler.

Tasarım dili:
    zemin   #F3F4EF  kireçli bozkır toprağı      mürekkep #1F2A24 liken
    su      #1C5D7A  derin akifer                gelir    #C9971C buğday okrası
    kart    #2E7D4F yeşil · #E3B505 sarı · #B3392F kırmızı (mevzuattaki sarı/kırmızı kart)
    yazı    Barlow (gövde) + Barlow Semi Condensed (başlıklar)
"""
from __future__ import annotations

import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..explain.confidence import confidence, label as conf_label
from ..explain.fmt import merged_year, money, num, water
from ..knowledge.tables import Crop
from .i18n import t

INK, MUTED, GROUND, PANEL = "#1F2A24", "#6B7A70", "#F3F4EF", "#E4E8E1"
WATER, INCOME = "#1C5D7A", "#C9971C"
STATUS_COLOR = {"green": "#2E7D4F", "yellow": "#E3B505", "red": "#B3392F"}
CONF_COLOR = {"high": "#2E7D4F", "medium": "#C9971C", "low": "#B3392F"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, select, textarea {
  font-family: 'Barlow', 'Segoe UI', system-ui, sans-serif;
}
h1, h2, h3, h4 { font-family: 'Barlow Semi Condensed', 'Barlow', system-ui, sans-serif; letter-spacing: -0.01em; color: #1F2A24; }
h1 { font-weight: 700; }
h2, h3 { font-weight: 600; }
.block-container { padding-top: 1.6rem; max-width: 1380px; }
.bs-tagline { color: #4A5750; font-size: 1.05rem; max-width: 70ch; margin: -0.4rem 0 1.2rem 0; line-height: 1.45; }
.bs-banner { border-left: 4px solid #E3B505; background: #FBF6DF; padding: 0.55rem 0.9rem; margin: 0.2rem 0 1rem 0; color: #3A3A2A; font-size: 0.95rem; }
.bs-disclaimer { color: #6B7A70; font-size: 0.85rem; border-top: 1px solid #D5DBD2; padding-top: 0.6rem; margin-top: 2rem; }

/* Sarı / kırmızı kart rozeti — mevzuattaki kart cezası */
.bs-status { display: inline-flex; align-items: center; gap: 0.45rem; font-weight: 600; font-size: 0.92rem; }
.bs-status .card { width: 13px; height: 18px; border-radius: 2px; transform: rotate(-9deg); box-shadow: 1px 1px 0 rgba(31,42,36,0.35); }
.bs-status.green .card { background: #2E7D4F; transform: none; border-radius: 50%; width: 12px; height: 12px; box-shadow: none; }
.bs-status.yellow .card { background: #E3B505; }
.bs-status.red .card { background: #B3392F; }
.bs-status.red { color: #8E2A22; }

/* Tarla şeridi — 4 yıl, ürün renkli bloklar */
.bs-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 3px; margin: 0.5rem 0 0.8rem 0; }
.bs-strip-wrap { container-type: inline-size; }
@container (max-width: 330px) { .bs-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.bs-tile { padding: 0.45rem 0.4rem 0.4rem 0.45rem; min-height: 3.4rem; border-radius: 3px; font-size: 0.86rem; line-height: 1.15; position: relative; min-width: 0; overflow-wrap: break-word; }
.bs-tile .yr { font-size: 0.72rem; opacity: 0.8; display: block; margin-bottom: 0.15rem; }
.bs-tile.viol { outline: 2px solid #B3392F; outline-offset: -2px; }
.bs-col-head { font-family: 'Barlow Semi Condensed', sans-serif; font-size: 1.35rem; font-weight: 700; margin: 0; color: #1F2A24; }
.bs-col-sub { color: #6B7A70; font-size: 0.88rem; margin: 0 0 0.35rem 0; min-height: 2.2em; }
.bs-col-current .bs-col-head { color: #4A5750; }

/* Gösterge satırları */
.bs-metric { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px dotted #C9D0C6; padding: 0.28rem 0; font-size: 0.93rem; }
.bs-metric .k { color: #4A5750; }
.bs-metric .v { font-weight: 600; font-variant-numeric: tabular-nums; text-align: right; }
.bs-metric .v.water { color: #1C5D7A; }
.bs-metric .v.income { color: #7A5A0C; }
.bs-metric .v.neg { color: #B3392F; }
.bs-conf { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-left: 0.35rem; vertical-align: middle; }
.bs-bar { height: 6px; background: #D5DBD2; border-radius: 3px; overflow: hidden; margin: 0.12rem 0 0.35rem 0; }
.bs-bar > span { display: block; height: 100%; background: #2E7D4F; }
.bs-soil-k { font-size: 0.84rem; color: #4A5750; display: flex; justify-content: space-between; }

.bs-big { font-family: 'Barlow Semi Condensed', sans-serif; font-size: 2.3rem; font-weight: 700; line-height: 1.05; color: #1F2A24; }
.bs-big.water { color: #1C5D7A; }
.bs-big-label { color: #4A5750; font-size: 0.92rem; margin-bottom: 0.8rem; }
.bs-headline { font-family: 'Barlow Semi Condensed', sans-serif; font-size: 1.45rem; font-weight: 600; line-height: 1.3;
  padding: 0.7rem 1rem; margin: 0.2rem 0 1rem 0; border-left: 6px solid #2E7D4F; background: #EAF1EA; color: #1F2A24; }
.bs-headline.yellow { border-left-color: #E3B505; background: #FBF6DF; }
.bs-headline.red { border-left-color: #B3392F; background: #F7E9E7; }
.bs-realcount { font-size: 0.9rem; color: #4A5750; margin: 0.6rem 0 0.2rem 0; }
.bs-fact { padding: 0.35rem 0 0.35rem 0.8rem; border-left: 3px solid #1C5D7A; margin: 0.25rem 0; color: #2E3A33; }
@media (max-width: 760px) { .bs-strip { grid-template-columns: repeat(2, 1fr); } .bs-big { font-size: 1.8rem; } }
</style>
"""


# Sunum modu: projektörde arka sıradan okunabilsin diye her şeyi ~%22 büyütür
# (1920×1080 projektör; Streamlit ölçüleri rem tabanlı olduğu için kök yazı boyutu yeter).
PRESENT_CSS = """
<style>
html { font-size: 19.5px !important; }
.block-container { max-width: 1760px; padding-top: 1.2rem; }
.bs-metric { font-size: 1.02rem; }
.bs-tile { font-size: 0.95rem; }
.bs-col-sub, .bs-soil-k, .bs-big-label, .bs-disclaimer { font-size: 0.95rem; }
[data-testid="stCaptionContainer"] { font-size: 0.95rem; }
</style>
"""


def presenting() -> bool:
    try:
        return bool(st.session_state.get("present", False))
    except Exception:  # noqa: BLE001 — Streamlit oturumu dışında (testler)
        return False


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    if presenting():
        st.markdown(PRESENT_CSS, unsafe_allow_html=True)


def _text_on(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return INK if lum > 0.55 else "#FFFFFF"


def status_html(status: str, lang: str) -> str:
    return (f'<span class="bs-status {status}"><span class="card"></span>'
            f'{html.escape(t("status_" + status, lang))}</span>')


def strip_html(parts, years: list[int], crops: dict[str, Crop], lang: str, viol_positions=()) -> str:
    tiles = []
    for i, y in enumerate(years):
        if len(parts) == 1:
            c = crops[parts[0][0][i]]
            bg, fg = c.color, _text_on(c.color)
            label = html.escape(c.name(lang)).replace("/", "/\u200b")
        else:
            # Karışım: baskın ürünün rengi + paylar (aynı ürün birleştirilir)
            m = merged_year(parts, i)
            c = crops[m[0][0]]
            bg, fg = c.color, _text_on(c.color)
            if len(m) == 1:
                label = html.escape(c.name(lang))
            else:
                label = "<br>".join(f"%{s * 100:.0f} {html.escape(crops[cid].name(lang))}" if lang == "tr"
                                    else f"{s * 100:.0f}% {html.escape(crops[cid].name(lang))}" for cid, s in m)
        cls = "bs-tile viol" if i in viol_positions else "bs-tile"
        tiles.append(f'<div class="{cls}" style="background:{bg};color:{fg}"><span class="yr">{y}</span>{label}</div>')
    return f'<div class="bs-strip-wrap"><div class="bs-strip">{"".join(tiles)}</div></div>'


def metric_row(key: str, value: str, cls: str = "", conf: tuple[str, str] | None = None) -> str:
    dot = ""
    if conf:
        dot = (f'<span class="bs-conf" style="background:{CONF_COLOR[conf[0]]}" '
               f'title="{html.escape(conf[1])}"></span>')
    return f'<div class="bs-metric"><span class="k">{html.escape(key)}</span><span class="v {cls}">{value}{dot}</span></div>'


def soil_bars(soil: dict, lang: str) -> str:
    out = []
    for k in ("nitrogen", "organic_matter", "erosion", "pest_cycle"):
        v = max(0.0, min(100.0, soil[k]))
        out.append(f'<div class="bs-soil-k"><span>{html.escape(t(k, lang))}</span><span>{v:.0f}</span></div>'
                   f'<div class="bs-bar"><span style="width:{v:.0f}%"></span></div>')
    return "".join(out)


def option_column(option, title: str, subtitle: str, ctx, lang: str, unit: str, synthetic: bool,
                  current_key: bool = False) -> None:
    det = option.detail
    m = option.metrics
    sym = ctx.basin.currency_symbol
    years = ctx.settings.plan_years
    viol = [i for i, v in enumerate(det.get("legal_viol", [])) if v] if not option.is_mix else []
    wrap = "bs-col-current" if current_key else ""
    st.markdown(
        f'<div class="{wrap}"><p class="bs-col-head">{html.escape(title)}</p>'
        f'<p class="bs-col-sub">{html.escape(subtitle)}</p></div>'
        + status_html(det["status"], lang)
        + strip_html(option.parts, years, ctx.crops, lang, viol),
        unsafe_allow_html=True,
    )
    rows = [
        metric_row(t("mean_income", lang), money(m["mean_margin"], sym, unit, lang),
                   "income" if m["mean_margin"] >= 0 else "neg", confidence("income", synthetic, lang)),
        metric_row(t("bad_income", lang), money(m["cvar5"], sym, unit, lang),
                   "income" if m["cvar5"] >= 0 else "neg", confidence("risk", synthetic, lang)),
    ]
    if ctx.settings.irrigated:
        rows.append(metric_row(t("water_use", lang), water(m["water_mean"], unit, lang), "water",
                               confidence("water", synthetic, lang)))
    rows += [
        metric_row(t("support", lang), money(m["support_mean"], sym, unit, lang), "",
                   confidence("support", synthetic, lang)),
        metric_row(t("loss_prob", lang), f"%{m['loss_prob'] * 100:.0f}" if lang == "tr" else f"{m['loss_prob'] * 100:.0f}%"),
        metric_row(t("forage", lang), f"{num(det['soil']['forage'], lang)} kg/da"),
    ]
    st.markdown("".join(rows), unsafe_allow_html=True)
    st.markdown(
        f'<div class="bs-soil-k" style="margin-top:0.6rem"><b>{html.escape(t("soil_health", lang))}</b>'
        f'<b>{det["soil"]["soil"]:.0f}/100</b></div>' + soil_bars(det["soil"], lang),
        unsafe_allow_html=True,
    )


def why_panel(expl: dict[str, list[str]], lang: str) -> None:
    for key, title in (("why", "why_why"), ("evidence", "why_evidence"), ("benefits", "why_benefits"),
                       ("gaps", "why_gaps"), ("local_risks", "why_local")):
        if expl.get(key):
            st.markdown(f"**{t(title, lang)}**")
            st.markdown("\n".join(f"- {line}" for line in expl[key]))


def confidence_legend(lang: str, synthetic: bool) -> str:
    items = [(lvl, conf_label(lvl, lang)) for lvl in ("high", "medium", "low")]
    dots = " ".join(f'<span class="bs-conf" style="background:{CONF_COLOR[l]}"></span> {html.escape(n)}' for l, n in items)
    return f'<div style="color:{MUTED};font-size:0.82rem;margin-top:0.4rem">{dots}</div>'


# ---------------------------------------------------------------------------
# Grafikler
# ---------------------------------------------------------------------------
def _layout(fig: go.Figure, height: int = 360, **kw) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Barlow, 'Segoe UI', system-ui, sans-serif", color=INK, size=17 if presenting() else 13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        **kw,
    )
    fig.update_xaxes(gridcolor="#D5DBD2", zeroline=False)
    fig.update_yaxes(gridcolor="#D5DBD2", zerolinecolor="#AEB8AC")
    return fig


def month_names(lang: str) -> list[str]:
    return (["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"] if lang == "tr"
            else ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])


def risk_heatmap(risk: pd.DataFrame, bare: pd.Series | None, lang: str) -> go.Figure:
    rows = ["frost_days", "hard_frost", "heat_days", "extreme_heat", "heavy_rain"]
    z = [risk[r].to_numpy() for r in rows]
    labels = [t(r, lang) for r in rows]
    text = [[f"{v:.1f}" for v in row] for row in z]
    zs = [row / max(row.max(), 1e-6) for row in z]
    z.append(risk["dry_month_prob"].to_numpy() * 100)
    zs.append(risk["dry_month_prob"].to_numpy())
    labels.append(t("dry_month_prob", lang) + " (%)")
    text.append([f"{v:.0f}" for v in z[-1]])
    if bare is not None:
        zs.append(bare.fillna(0).to_numpy())
        labels.append(t("bare_soil", lang) + " (%)")
        text.append([f"{v * 100:.0f}" for v in bare.fillna(0).to_numpy()])
    fig = go.Figure(go.Heatmap(
        z=zs, x=month_names(lang), y=labels, text=text, texttemplate="%{text}", showscale=False,
        colorscale=[[0, "#F3F4EF"], [0.5, "#C7D3C2"], [1, "#2F5A44"]], hoverinfo="skip",
        xgap=2, ygap=2,
    ))
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, 60 + 38 * len(labels))


def water_month_chart(risk: pd.DataFrame, lang: str) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=month_names(lang), y=risk["precip_mm"], name=("Yağış (mm)" if lang == "tr" else "Rain (mm)"),
                marker_color="#7FA7B8")
    fig.add_scatter(x=month_names(lang), y=risk["et0_mm"], name="ET0 (mm)", mode="lines+markers",
                    line=dict(color=INCOME, width=3))
    return _layout(fig, 300)


def income_box(options: dict, crops, ctx, lang: str, unit: str, order: list[tuple[str, str]]) -> go.Figure:
    from ..explain.fmt import area_factor

    fig = go.Figure()
    f = area_factor(unit)
    for key, label in order:
        if key not in options:
            continue
        totals = options[key].detail["sim"]["margin"].sum(axis=1) * f
        color = MUTED if key == "current" else {"profit": INCOME, "aquifer": WATER, "balance": "#2E7D4F"}[key]
        fig.add_box(y=totals, name=label, boxpoints="all", jitter=0.4, pointpos=0, marker=dict(size=4, color=color),
                    line=dict(color=color), fillcolor="rgba(0,0,0,0.03)")
    fig.update_yaxes(title=f"{ctx.basin.currency_symbol}/{unit}")
    return _layout(fig, 380, showlegend=False)


def pareto_chart(res, options: dict, labels: dict[str, str], ctx, unit: str, lang: str) -> go.Figure:
    from ..explain.fmt import area_factor

    f = area_factor(unit)
    feas = res.feasible
    sample = feas.sample(min(len(feas), 4000), random_state=1) if len(feas) > 4000 else feas
    fig = go.Figure()
    x_col = "water_mean" if ctx.settings.irrigated else "cvar5"
    x_title = (f"{t('water_use', lang)} (m³/{unit})" if ctx.settings.irrigated else f"{t('bad_income', lang)} ({ctx.basin.currency_symbol}/{unit})")
    fig.add_scatter(x=sample[x_col] * f, y=sample["mean_margin"] * f, mode="markers",
                    marker=dict(size=4, color="#AEB8AC", opacity=0.5), name=("Uygun planlar" if lang == "tr" else "Feasible plans"),
                    hoverinfo="skip")
    p = res.pareto
    fig.add_scatter(x=p[x_col] * f, y=p["mean_margin"] * f, mode="markers",
                    marker=dict(size=7, color=p["soil"], colorscale="Greens", showscale=True,
                                colorbar=dict(title=t("soil_health", lang), thickness=10)),
                    name="Pareto", text=[" → ".join(ctx.crops[c].name(lang) for c in pl) for pl in p["plan"]],
                    hovertemplate="%{text}<extra></extra>")
    for key, opt in options.items():
        m = opt.metrics
        xv = (m["water_mean"] if ctx.settings.irrigated else m["cvar5"]) * f
        fig.add_scatter(x=[xv], y=[m["mean_margin"] * f], mode="markers+text", text=[labels.get(key, key)],
                        textposition="top center", marker=dict(size=14, symbol="diamond",
                                                               color=MUTED if key == "current" else INK),
                        showlegend=False)
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title=f"{t('mean_income', lang)} ({ctx.basin.currency_symbol}/{unit})")
    return _layout(fig, 460)


def calendar_chart(cal: pd.DataFrame, crops, risk: pd.DataFrame, lang: str) -> go.Figure:
    fig = go.Figure()
    for _, r in cal.iterrows():
        if r["start"] is None or pd.isna(r["start"]):
            continue
        c = crops[r["crop"]]
        fig.add_trace(go.Scatter(x=[r["start"], r["end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color=c.color, width=16), showlegend=False,
                                 hovertemplate=f"{c.name(lang)} {r['year']}<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["mid_start"], r["mid_end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color="#B3392F", width=4), showlegend=False,
                                 hovertemplate=("Sıcak stresine hassas" if lang == "tr" else "Heat-sensitive") + "<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["frost_start"], r["frost_end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color="#5B8DB8", width=4, dash="dot"), showlegend=False,
                                 hovertemplate=("Dona hassas" if lang == "tr" else "Frost-sensitive") + "<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, 70 + 42 * max(1, cal["crop"].nunique()))


def band_chart(details: list[tuple[str, dict, str]], key: str, years: list[int], factor: float, ytitle: str) -> go.Figure:
    fig = go.Figure()
    for name, det, color in details:
        arr = det["sim"][key] * factor                       # (W, N)
        p10, p50, p90 = (np.percentile(arr, q, axis=0) for q in (10, 50, 90))
        rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        fig.add_scatter(x=years + years[::-1], y=list(p90) + list(p10[::-1]), fill="toself", mode="lines",
                        fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.18)", line=dict(width=0),
                        hoverinfo="skip", showlegend=False)
        fig.add_scatter(x=years, y=p50, mode="lines+markers", name=name, line=dict(color=color, width=3))
    fig.update_xaxes(tickmode="array", tickvals=years)
    fig.update_yaxes(title=ytitle)
    return _layout(fig, 320)
