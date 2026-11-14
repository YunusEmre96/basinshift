"""Görsel bileşenler: NASA Space Apps Challenge 2026 Tasarım Sistemi (Stealth Navy).

Tasarım dili (NASA Space Apps Brand Guide 2026 - Stealth Navy Theme):
    zemin       #060B14  Stealth Navy Ground (mat gece laciverti zemin)
    panel       #0D1524  Navy Card Surface (mat gece laciverti kartlar)
    vurgu/link  #0042A6  Electric Blue / #2E96F5 Blue Yonder
    öne çıkan   #EAFE07  Neon Yellow (PMS Neon 387 - %10 kuralı, buton/rozet/metrik)
    uyarı/ceza  #E43700  Rocket Red (PMS Bright Red C - kırmızı kart/alarm)
    metin       #FFFFFF  White (ana) / #8C9BAE Slate Gray (ikincil)
    yazı        Fira Sans (başlıklar, 700-900) + Overpass (gövde/metrik) + Fira Code (kod/veri)
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

INK, MUTED, GROUND, PANEL = "#FFFFFF", "#8C9BAE", "#060B14", "#0D1524"
WATER, INCOME = "#2E96F5", "#EAFE07"
STATUS_COLOR = {"green": "#00D26A", "yellow": "#FFD600", "red": "#E43700"}
CONF_COLOR = {"high": "#00D26A", "medium": "#FFD600", "low": "#E43700"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Fira+Sans:wght@700;800;900&family=Overpass:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

html, body, .stApp, .stMarkdown, .stText, p, label, .bs-tagline, .bs-disclaimer, .bs-metric {
  font-family: 'Overpass', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Explicit Material Symbols icon styling for Streamlit expanders & buttons */
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
[data-testid*="IconMaterial"],
[data-testid*="stIcon"],
[data-testid*="stExpanderToggleIcon"],
[data-testid="stExpanderToggleIcon"] *,
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {
  font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 1.25rem !important;
  line-height: 1 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  display: inline-block !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  font-feature-settings: 'liga' 1 !important;
  -webkit-font-feature-settings: 'liga' 1 !important;
  -webkit-font-smoothing: antialiased !important;
}

/* Hide Streamlit Deploy button and toolbar branding */
.stDeployButton, [data-testid="stDeployButton"], #MainMenu, header[data-testid="stHeader"] .stDeployButton {
  display: none !important;
}

div[data-baseweb="select"] {
  font-size: 0.88rem !important;
}
div[data-baseweb="select"] > div {
  background-color: #0D1524 !important;
  border: 1px solid rgba(46, 150, 245, 0.18) !important;
  border-radius: 6px !important;
}
div[data-baseweb="select"] > div:hover {
  border-color: rgba(46, 150, 245, 0.55) !important;
}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
  background-color: #0D1524 !important;
  border: 1px solid rgba(46, 150, 245, 0.25) !important;
}
[data-testid="stExpander"] {
  background-color: #0D1524 !important;
  border: 1px solid rgba(46, 150, 245, 0.15) !important;
  border-radius: 8px !important;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: #FFFFFF !important;
  letter-spacing: -0.01em;
}
h1 { font-weight: 900 !important; letter-spacing: 0.02em !important; }
h2, h3 { font-weight: 700 !important; }
code, pre { font-family: 'Fira Code', monospace !important; }

.block-container { padding-top: 1.2rem; max-width: 1400px; }

/* NASA Space Apps Hero Header & Rozet - Stealth Navy */
.bs-hero-banner {
  background: linear-gradient(135deg, rgba(14, 23, 38, 0.95) 0%, rgba(6, 11, 20, 0.98) 100%),
              radial-gradient(ellipse at 85% 15%, rgba(46, 150, 245, 0.16) 0%, transparent 60%);
  border: 1px solid rgba(46, 150, 245, 0.22);
  border-radius: 12px;
  padding: 1.4rem 1.8rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}
.bs-hero-banner::after {
  content: "";
  position: absolute;
  top: -30%;
  right: -5%;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(46, 150, 245, 0.12) 0%, rgba(234, 254, 7, 0.02) 50%, transparent 75%);
  border-radius: 50%;
  pointer-events: none;
}
.bs-badge-spaceapps {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(46, 150, 245, 0.14);
  border: 1px solid rgba(46, 150, 245, 0.38);
  border-radius: 20px;
  padding: 0.28rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #EAFE07;
  margin-bottom: 0.7rem;
}
.bs-hero-title {
  font-family: 'Fira Sans', sans-serif !important;
  font-weight: 900 !important;
  font-size: 2.2rem !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  color: #FFFFFF !important;
  margin: 0 0 0.4rem 0 !important;
}
.bs-tagline {
  color: #A0B2C6;
  font-size: 1.05rem;
  max-width: 75ch;
  margin: 0.2rem 0 0.4rem 0;
  line-height: 1.5;
  font-weight: 400;
}

/* Alt sayfa başlığı */
.bs-sub-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.8rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px solid rgba(46, 150, 245, 0.15);
}
.bs-sub-title {
  font-family: 'Fira Sans', sans-serif;
  font-weight: 900;
  font-size: 1.45rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #FFFFFF;
}
.bs-sub-badge {
  background: rgba(46, 150, 245, 0.14);
  border: 1px solid rgba(46, 150, 245, 0.38);
  color: #EAFE07;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Kenar Çubuğu */
[data-testid="stSidebar"] {
  background: #04070D !important;
  border-right: 1px solid rgba(46, 150, 245, 0.12) !important;
}
.bs-sidebar-title {
  font-family: 'Fira Sans', sans-serif;
  font-weight: 900;
  font-size: 1.35rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #FFFFFF;
  margin-top: 0.4rem;
}
.bs-sidebar-sub {
  font-family: 'Overpass', sans-serif;
  font-size: 0.76rem;
  color: #EAFE07;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
}

.bs-banner {
  border-left: 4px solid #EAFE07;
  background: rgba(234, 254, 7, 0.12);
  padding: 0.6rem 1rem;
  margin: 0.3rem 0 1rem 0;
  color: #E8EEF5;
  font-size: 0.95rem;
  border-radius: 4px;
}
.bs-disclaimer {
  color: #8C9BAE;
  font-size: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  padding-top: 0.8rem;
  margin-top: 2rem;
}

/* Butonlar: Neon Yellow birincil buton */
.stButton > button {
  font-family: 'Overpass', sans-serif !important;
  font-weight: 700 !important;
  border-radius: 6px !important;
  transition: all 0.2s ease-in-out !important;
}
.stButton > button[kind="primary"] {
  background-color: #EAFE07 !important;
  color: #060B14 !important;
  border: 1px solid #EAFE07 !important;
  font-weight: 800 !important;
}
.stButton > button[kind="primary"]:hover {
  background-color: #F5FF55 !important;
  box-shadow: 0 0 15px rgba(234, 254, 7, 0.5) !important;
  color: #050B14 !important;
}
.stButton > button[kind="secondary"] {
  background-color: #0D1524 !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(46, 150, 245, 0.22) !important;
}
.stButton > button[kind="secondary"]:hover {
  background-color: #132036 !important;
  border-color: #2E96F5 !important;
}

/* Sarı / kırmızı kart rozeti — mevzuattaki kart cezası */
.bs-status {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-weight: 700;
  font-size: 0.92rem;
  font-family: 'Overpass', sans-serif;
}
.bs-status .card {
  width: 13px;
  height: 18px;
  border-radius: 2px;
  transform: rotate(-9deg);
  box-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.bs-status.green .card {
  background: #00D26A;
  transform: none;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  box-shadow: 0 0 8px rgba(0, 210, 106, 0.7);
}
.bs-status.yellow .card {
  background: #FFD600;
  box-shadow: 0 0 8px rgba(255, 214, 0, 0.6);
}
.bs-status.red .card {
  background: #E43700;
  box-shadow: 0 0 8px rgba(228, 55, 0, 0.7);
}
.bs-status.green { color: #00E676; }
.bs-status.yellow { color: #FFEA00; }
.bs-status.red { color: #FF5252; }

/* Tarla şeridi — 4 yıl, ürün renkli bloklar */
.bs-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 5px;
  margin: 0.5rem 0 0.8rem 0;
}
.bs-strip-wrap { container-type: inline-size; }
@container (max-width: 330px) { .bs-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.bs-tile {
  padding: 0.5rem 0.45rem;
  min-height: 3.5rem;
  border-radius: 6px;
  font-size: 0.86rem;
  font-weight: 700;
  line-height: 1.2;
  position: relative;
  min-width: 0;
  overflow-wrap: break-word;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.bs-tile .yr {
  font-size: 0.72rem;
  opacity: 0.85;
  display: block;
  margin-bottom: 0.15rem;
  font-weight: 800;
}
.bs-tile.viol {
  outline: 3px solid #E43700;
  outline-offset: -2px;
  box-shadow: 0 0 10px rgba(228, 55, 0, 0.7);
}
.bs-col-head {
  font-family: 'Fira Sans', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  margin: 0;
  color: #FFFFFF;
  letter-spacing: 0.02em;
}
.bs-col-sub {
  color: #8C9BAE;
  font-size: 0.88rem;
  margin: 0 0 0.35rem 0;
  min-height: 2.2em;
  line-height: 1.3;
}
.bs-col-current .bs-col-head { color: #B0C4DE; }

/* Gösterge satırları */
.bs-metric {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px dotted rgba(255, 255, 255, 0.18);
  padding: 0.3rem 0;
  font-size: 0.93rem;
}
.bs-metric .k { color: #8C9BAE; font-weight: 500; }
.bs-metric .v { font-weight: 700; font-variant-numeric: tabular-nums; text-align: right; color: #FFFFFF; }
.bs-metric .v.water { color: #2E96F5; }
.bs-metric .v.income { color: #EAFE07; }
.bs-metric .v.neg { color: #FF5252; }
.bs-conf { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 0.35rem; vertical-align: middle; }
.bs-bar { height: 7px; background: rgba(255, 255, 255, 0.12); border-radius: 4px; overflow: hidden; margin: 0.14rem 0 0.38rem 0; }
.bs-bar > span { display: block; height: 100%; background: linear-gradient(90deg, #0052FF 0%, #00D26A 100%); border-radius: 4px; }
.bs-soil-k { font-size: 0.85rem; color: #8C9BAE; display: flex; justify-content: space-between; font-weight: 600; }

.bs-big { font-family: 'Fira Sans', sans-serif; font-size: 2.3rem; font-weight: 900; line-height: 1.05; color: #FFFFFF; }
.bs-big.water { color: #2E96F5; }
.bs-big-label { color: #8C9BAE; font-size: 0.92rem; margin-bottom: 0.8rem; }
.bs-headline {
  font-family: 'Fira Sans', sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
  padding: 0.8rem 1.1rem;
  margin: 0.3rem 0 1rem 0;
  border-left: 5px solid #00D26A;
  background: rgba(13, 21, 36, 0.88);
  border: 1px solid rgba(46, 150, 245, 0.12);
  border-left: 5px solid #00D26A;
  border-radius: 6px;
  color: #FFFFFF;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.bs-headline.yellow { border-left-color: #FFD600; background: rgba(36, 30, 10, 0.7); }
.bs-headline.red { border-left-color: #E43700; background: rgba(40, 12, 12, 0.7); }
.bs-realcount { font-size: 0.9rem; color: #8C9BAE; margin: 0.6rem 0 0.2rem 0; font-weight: 600; }
.bs-fact { padding: 0.4rem 0 0.4rem 0.85rem; border-left: 3px solid #2E96F5; margin: 0.3rem 0; color: #D8E2ED; }
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
    return "#060B14" if lum > 0.55 else "#FFFFFF"


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
        font=dict(family="Overpass, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                  color=INK, size=17 if presenting() else 13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=INK)),
        **kw,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zeroline=False,
                     tickfont=dict(color=MUTED), title_font=dict(color=INK))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.18)",
                     tickfont=dict(color=MUTED), title_font=dict(color=INK))
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
        colorscale=[[0, "#060B14"], [0.35, "#0042A6"], [0.7, "#2E96F5"], [1, "#EAFE07"]], hoverinfo="skip",
        xgap=2, ygap=2,
    ))
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, 60 + 38 * len(labels))


def water_month_chart(risk: pd.DataFrame, lang: str) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=month_names(lang), y=risk["precip_mm"], name=("Yağış (mm)" if lang == "tr" else "Rain (mm)"),
                marker_color="#2E96F5")
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
        color = MUTED if key == "current" else {"profit": INCOME, "aquifer": WATER, "balance": "#00D26A"}[key]
        fig.add_box(y=totals, name=label, boxpoints="all", jitter=0.4, pointpos=0, marker=dict(size=4, color=color),
                    line=dict(color=color), fillcolor="rgba(255,255,255,0.04)")
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
                    marker=dict(size=4, color="rgba(140, 155, 174, 0.45)", opacity=0.5), name=("Uygun planlar" if lang == "tr" else "Feasible plans"),
                    hoverinfo="skip")
    p = res.pareto
    fig.add_scatter(x=p[x_col] * f, y=p["mean_margin"] * f, mode="markers",
                    marker=dict(size=7, color=p["soil"], colorscale=[[0, "#0042A6"], [0.5, "#00D26A"], [1, "#EAFE07"]], showscale=True,
                                colorbar=dict(title=dict(text=t("soil_health", lang), font=dict(color=INK)),
                                              tickfont=dict(color=MUTED), thickness=10)),
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
                                 line=dict(color="#E43700", width=4), showlegend=False,
                                 hovertemplate=("Sıcak stresine hassas" if lang == "tr" else "Heat-sensitive") + "<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["frost_start"], r["frost_end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color="#2E96F5", width=4, dash="dot"), showlegend=False,
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
