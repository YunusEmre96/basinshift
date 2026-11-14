"""Görsel bileşenler — NASA Space Apps 2026 marka rehberine dayalı karanlık tema.

Renkler (Space Apps Brand Guidelines, 25 Haziran 2026):
    Deep Blue     #07173F   zemin tonları (daha koyu türevleri: #040B1E, #0A1A3D)
    Electric Blue #0042A6   gradyan başlangıcı (sol üst → sağ alt, 45°)
    Neon Blue     #0960E1   ikincil vurgu
    Blue Yonder   #2E96F5   su, bağlantı, seçili durum
    Neon Yellow   #EAFE07   YALNIZCA vurgu (60-30-10 kuralı): birincil düğme, önemli rakam
    Rocket Red    #E43700   kırmızı kart, kayıp
    Martian Red   #8E1100   koyu kırmızı zemin
Yazı: Fira Sans Black (başlık) · Overpass (gövde) · Fira Code (kod). Çevrimdışıyken Inter /
Segoe UI devreye girer. Renk tek başına anlam taşımaz: her durum rengi bir metin ya da
simgeyle birlikte verilir (marka rehberi erişilebilirlik kuralı).
"""
from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from ..explain.confidence import confidence, label as conf_label
from ..explain.fmt import merged_year, money, num, water
from ..knowledge.tables import Crop
from .i18n import t

ASSETS = Path(__file__).resolve().parent / "assets"

# Marka renkleri
DEEP, ELECTRIC, NEON_BLUE, YONDER = "#07173F", "#0042A6", "#0960E1", "#2E96F5"
NEON_YELLOW, ROCKET, MARTIAN = "#EAFE07", "#E43700", "#8E1100"
GROUND, PANEL, PANEL_2 = "#040B1E", "#0A1A3D", "#0E2250"
INK, MUTED, FAINT = "#F4F7FC", "#9AAACB", "#5E6F93"
GREEN = "#2BD67B"
WATER, INCOME = YONDER, NEON_YELLOW
STATUS_COLOR = {"green": GREEN, "yellow": "#FFC83D", "red": ROCKET}
CONF_COLOR = {"high": GREEN, "medium": "#FFC83D", "low": ROCKET}
#: Kart (strateji) renkleri — her kartın üst şeridi ve grafiklerdeki rengi
STRATEGY_COLOR = {"current": "#8A97B4", "profit": NEON_YELLOW, "aquifer": YONDER, "balance": GREEN}
STRATEGY_ICON = {"current": "◎", "profit": "▲", "aquifer": "◆", "balance": "⬢"}
FONT_BODY = "Overpass, Inter, 'Segoe UI', -apple-system, Roboto, sans-serif"
FONT_HEAD = "'Fira Sans', 'Inter Display', Inter, 'Segoe UI', sans-serif"


@lru_cache(maxsize=8)
def asset_b64(rel: str) -> str:
    p = ASSETS / rel
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


# ---------------------------------------------------------------------------
# Plotly şablonu: bütün grafikler aynı dili konuşsun
# ---------------------------------------------------------------------------
def _register_template() -> None:
    if "basinshift" in pio.templates:
        return
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=INK, size=13),
        colorway=[YONDER, NEON_YELLOW, GREEN, "#FF8A5B", "#B892FF", "#5DE0E6", "#FFC83D", "#8A97B4"],
        hoverlabel=dict(bgcolor=PANEL_2, bordercolor=YONDER, font=dict(family=FONT_BODY, color=INK, size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)",
                    font=dict(color=MUTED, size=12)),
        xaxis=dict(automargin=True, gridcolor="rgba(154,170,203,0.10)", zeroline=False, linecolor="rgba(154,170,203,0.25)",
                   tickfont=dict(color=MUTED), title=dict(font=dict(color=MUTED, size=12))),
        yaxis=dict(automargin=True, gridcolor="rgba(154,170,203,0.10)", zerolinecolor="rgba(154,170,203,0.28)",
                   linecolor="rgba(154,170,203,0.25)", tickfont=dict(color=MUTED),
                   title=dict(font=dict(color=MUTED, size=12))),
        margin=dict(l=10, r=10, t=36, b=10), bargap=0.28,
    )
    pio.templates["basinshift"] = tpl


_register_template()


def _css() -> str:
    orbit = asset_b64("patterns/hero_orbits.png")
    waves = asset_b64("patterns/waves_light.png")
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Fira+Sans:wght@600;700;800;900&family=Overpass:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&display=swap');

:root {{
  --bs-ground: {GROUND}; --bs-panel: {PANEL}; --bs-panel2: {PANEL_2}; --bs-deep: {DEEP};
  --bs-electric: {ELECTRIC}; --bs-yonder: {YONDER}; --bs-yellow: {NEON_YELLOW}; --bs-red: {ROCKET};
  --bs-green: {GREEN}; --bs-ink: {INK}; --bs-muted: {MUTED}; --bs-faint: {FAINT};
  --bs-line: rgba(46,150,245,0.16); --bs-line-strong: rgba(46,150,245,0.34);
  --bs-radius: 14px; --bs-head: {FONT_HEAD}; --bs-body: {FONT_BODY};
}}
.stApp {{
  background:
    radial-gradient(1200px 600px at 100% -10%, rgba(0,66,166,0.28), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(9,96,225,0.14), transparent 60%),
    var(--bs-ground) !important;
}}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button, [data-baseweb] {{
  font-family: var(--bs-body);
}}
h1, h2, h3, h4, h5 {{ font-family: var(--bs-head) !important; color: var(--bs-ink) !important; letter-spacing: -0.005em; }}
h1 {{ font-weight: 900 !important; }}
h2 {{ font-weight: 800 !important; font-size: 1.6rem !important; }}
h3 {{ font-weight: 700 !important; font-size: 1.18rem !important; }}
code, pre {{ font-family: 'Fira Code', 'DejaVu Sans Mono', monospace !important; }}
.block-container {{ padding-top: 1.0rem; max-width: 1440px; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}
.stDeployButton, [data-testid="stDeployButton"], #MainMenu {{ display: none !important; }}

/* ---------- Üst gezinme ---------- */
[data-testid="stTopNavLink"], [data-testid="stNavLink"] {{ border-radius: 999px !important; }}
[data-testid="stTopNavLink"] span, [data-testid="stNavLink"] span {{ font-weight: 700; letter-spacing: 0.01em; }}

/* ---------- Kenar çubuğu ---------- */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #06102A 0%, #040B1E 100%) !important;
  border-right: 1px solid var(--bs-line) !important;
}}
[data-testid="stSidebar"] [data-testid="stImage"] img {{ max-width: 210px; margin: 0.2rem 0 0.2rem 0; }}
.bs-side-brand {{ display:flex; flex-direction:column; gap:0.1rem; margin:0.1rem 0 1rem 0; }}
.bs-side-brand .n {{ font-family: var(--bs-head); font-weight: 900; font-size: 1.5rem; letter-spacing: 0.06em; color: var(--bs-ink); }}
.bs-side-brand .s {{ font-size: 0.74rem; color: var(--bs-muted); letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; }}
.bs-side-label {{ font-size: 0.72rem; color: var(--bs-faint); letter-spacing: 0.14em; text-transform: uppercase;
  font-weight: 800; margin: 1.1rem 0 0.35rem 0; border-top: 1px solid var(--bs-line); padding-top: 0.9rem; }}

/* ---------- Form öğeleri ---------- */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stNumberInput input, .stTextInput input {{
  background-color: rgba(10,26,61,0.85) !important; border: 1px solid var(--bs-line) !important; border-radius: 10px !important;
}}
div[data-baseweb="select"] > div:hover {{ border-color: var(--bs-line-strong) !important; }}
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {{ background-color: {PANEL_2} !important; }}
span[data-baseweb="tag"] {{ background: rgba(46,150,245,0.18) !important; border: 1px solid rgba(46,150,245,0.45) !important;
  color: var(--bs-ink) !important; border-radius: 999px !important; }}
[data-testid="stSlider"] [role="slider"] {{ box-shadow: 0 0 0 4px rgba(46,150,245,0.22) !important; }}
[data-testid="stExpander"] {{ background: rgba(10,26,61,0.55) !important; border: 1px solid var(--bs-line) !important;
  border-radius: 12px !important; }}
[data-testid="stExpander"] summary p {{ font-weight: 700; }}

/* ---------- Düğmeler ---------- */
.stButton > button, .stDownloadButton > button {{ font-weight: 800 !important; border-radius: 999px !important;
  padding: 0.5rem 1.15rem !important; transition: all .18s ease !important; letter-spacing: 0.01em; }}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
  background: var(--bs-yellow) !important; color: #06102A !important; border: 1px solid var(--bs-yellow) !important; }}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {{
  box-shadow: 0 0 0 4px rgba(234,254,7,0.18), 0 8px 24px rgba(234,254,7,0.18) !important; transform: translateY(-1px); }}
.stButton > button[kind="secondary"] {{ background: rgba(10,26,61,0.8) !important; color: var(--bs-ink) !important;
  border: 1px solid var(--bs-line-strong) !important; }}
.stButton > button[kind="secondary"]:hover {{ border-color: var(--bs-yonder) !important; background: rgba(46,150,245,0.12) !important; }}

/* ---------- Kahraman alanı (yalnızca Tarla sayfası) ---------- */
.bs-hero {{
  position: relative; overflow: hidden; border-radius: 20px; padding: 1.7rem 2rem 1.6rem 2rem; margin: 0.2rem 0 1.2rem 0;
  background: linear-gradient(135deg, {ELECTRIC} 0%, #062A72 38%, {DEEP} 100%);
  border: 1px solid rgba(46,150,245,0.35); box-shadow: 0 24px 60px rgba(0,0,0,0.45);
}}
.bs-hero::before {{ content:""; position:absolute; right:-140px; top:-170px; width:620px; height:620px; opacity:0.55;
  background: url(data:image/png;base64,{orbit}) center/contain no-repeat; pointer-events:none; }}
.bs-hero .kicker {{ display:inline-flex; gap:0.5rem; align-items:center; font-size:0.74rem; font-weight:800; letter-spacing:0.16em;
  text-transform:uppercase; color: var(--bs-yellow); background: rgba(4,11,30,0.45); border:1px solid rgba(234,254,7,0.35);
  padding: 0.28rem 0.8rem; border-radius:999px; }}
.bs-hero h1 {{ font-size: 3.0rem !important; line-height: 1.02; margin: 0.7rem 0 0.4rem 0 !important; letter-spacing: 0.01em; }}
.bs-hero p {{ color: #D6E3FF; font-size: 1.1rem; max-width: 64ch; line-height: 1.5; margin: 0; position: relative; }}
.bs-hero .steps {{ display:flex; flex-wrap:wrap; gap:0.5rem; margin-top: 1.1rem; position: relative; }}
.bs-hero .steps span {{ font-size: 0.82rem; color: var(--bs-ink); background: rgba(4,11,30,0.42); border: 1px solid rgba(255,255,255,0.14);
  padding: 0.3rem 0.75rem; border-radius: 999px; font-weight: 600; }}
.bs-hero .steps b {{ color: var(--bs-yellow); margin-right: 0.35rem; }}

/* ---------- Sayfa girişi ---------- */
.bs-intro {{ display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin: 0.2rem 0 1.0rem 0;
  padding-bottom: 0.9rem; border-bottom: 1px solid var(--bs-line); }}
.bs-intro .l .step {{ font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--bs-yonder); font-weight: 800; }}
.bs-intro .l h2 {{ margin: 0.15rem 0 0.25rem 0 !important; font-size: 2.0rem !important; font-weight: 900 !important; }}
.bs-intro .l p {{ margin: 0; color: var(--bs-muted); max-width: 80ch; line-height: 1.45; }}
.bs-intro .r {{ display:flex; gap:0.45rem; flex-wrap:wrap; justify-content:flex-end; }}

/* ---------- Bölüm başlığı ---------- */
.bs-sec {{ margin: 1.5rem 0 0.55rem 0; }}
.bs-sec .t {{ font-family: var(--bs-head); font-weight: 800; font-size: 1.22rem; color: var(--bs-ink); display:flex; align-items:center; gap:0.55rem; }}
.bs-sec .t::before {{ content:""; width: 4px; height: 1.05em; border-radius: 4px; background: linear-gradient(180deg, var(--bs-yonder), var(--bs-electric)); }}
.bs-sec .h {{ color: var(--bs-muted); font-size: 0.9rem; margin: 0.15rem 0 0 0.95rem; line-height: 1.4; }}

/* ---------- Çipler ---------- */
.bs-chip {{ display:inline-flex; align-items:center; gap:0.4rem; font-size: 0.78rem; font-weight: 700; padding: 0.22rem 0.65rem;
  border-radius: 999px; border: 1px solid var(--bs-line-strong); color: var(--bs-ink); background: rgba(46,150,245,0.10); white-space: nowrap; }}
.bs-chip i {{ width: 7px; height: 7px; border-radius: 50%; display:inline-block; font-style: normal; }}
.bs-chip.real {{ border-color: rgba(43,214,123,0.5); background: rgba(43,214,123,0.10); }} .bs-chip.real i {{ background: var(--bs-green); }}
.bs-chip.synthetic {{ border-color: rgba(255,200,61,0.55); background: rgba(255,200,61,0.10); }} .bs-chip.synthetic i {{ background: #FFC83D; }}
.bs-chip.default, .bs-chip.unverified {{ border-color: rgba(154,170,203,0.5); background: rgba(154,170,203,0.10); }}
.bs-chip.default i, .bs-chip.unverified i {{ background: var(--bs-muted); }}
.bs-chip.missing {{ border-color: rgba(228,55,0,0.55); background: rgba(228,55,0,0.12); }} .bs-chip.missing i {{ background: var(--bs-red); }}
.bs-chip.yellow {{ color: #06102A; background: var(--bs-yellow); border-color: var(--bs-yellow); }}
.bs-chip.v-green {{ border-color: rgba(43,214,123,0.55); background: rgba(43,214,123,0.12); }} .bs-chip.v-green i {{ background: var(--bs-green); }}
.bs-chip.v-yellow {{ border-color: rgba(255,200,61,0.6); background: rgba(255,200,61,0.12); }} .bs-chip.v-yellow i {{ background: #FFC83D; }}
.bs-chip.v-red {{ border-color: rgba(228,55,0,0.6); background: rgba(228,55,0,0.14); }} .bs-chip.v-red i {{ background: var(--bs-red); }}

/* ---------- Veri durumu (kenar çubuğu) ---------- */
.bs-data {{ background: rgba(10,26,61,0.7); border:1px solid var(--bs-line); border-radius: 12px; padding: 0.7rem 0.8rem; }}
.bs-data .bar {{ display:flex; height: 8px; border-radius: 6px; overflow:hidden; margin: 0.45rem 0 0.5rem 0; background: rgba(255,255,255,0.06); }}
.bs-data .bar span {{ display:block; height:100%; }}
.bs-data .row {{ display:flex; justify-content:space-between; font-size: 0.8rem; color: var(--bs-muted); margin: 0.12rem 0; }}
.bs-data .row b {{ color: var(--bs-ink); }}
.bs-data .ttl {{ font-weight: 800; font-size: 0.86rem; color: var(--bs-ink); }}
.bs-ds {{ border-top: 1px dashed var(--bs-line); padding: 0.45rem 0 0.35rem 0; }}
.bs-ds .nm {{ font-size: 0.86rem; font-weight: 700; color: var(--bs-ink); display:flex; justify-content:space-between; gap:0.4rem; align-items:center; }}
.bs-ds .nt {{ font-size: 0.76rem; color: var(--bs-muted); line-height: 1.35; margin-top: 0.15rem; }}

/* ---------- KPI kutuları ---------- */
.bs-kpis {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.8rem; margin: 0.6rem 0 1.0rem 0; }}
.bs-kpi {{ position: relative; background: linear-gradient(160deg, rgba(14,34,80,0.95), rgba(10,26,61,0.85));
  border: 1px solid var(--bs-line); border-radius: var(--bs-radius); padding: 0.95rem 1.1rem 0.9rem 1.1rem; overflow:hidden; }}
.bs-kpi::after {{ content:""; position:absolute; left:0; top:0; bottom:0; width: 4px; background: var(--tone, var(--bs-yonder)); }}
.bs-kpi .lb {{ font-size: 0.76rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--bs-muted); font-weight: 800; }}
.bs-kpi .v {{ font-family: var(--bs-head); font-weight: 900; font-size: 2.05rem; line-height: 1.1; margin-top: 0.3rem;
  color: var(--tone, var(--bs-ink)); font-variant-numeric: tabular-nums; }}
.bs-kpi .s {{ font-size: 0.84rem; color: var(--bs-muted); margin-top: 0.25rem; line-height: 1.35; }}

/* ---------- Özet cümlesi ---------- */
.bs-headline {{ display:flex; gap: 0.9rem; align-items:flex-start; font-family: var(--bs-head); font-size: 1.32rem; font-weight: 700;
  line-height: 1.38; padding: 1.0rem 1.2rem; margin: 0.2rem 0 0.4rem 0; border-radius: var(--bs-radius); color: var(--bs-ink);
  background: linear-gradient(120deg, rgba(43,214,123,0.14), rgba(10,26,61,0.85) 55%); border: 1px solid rgba(43,214,123,0.35); }}
.bs-headline .ic {{ flex: 0 0 auto; width: 2.3rem; height: 2.3rem; border-radius: 50%; display:grid; place-items:center;
  font-size: 1.15rem; font-weight: 900; color: #06102A; background: var(--bs-green); }}
.bs-headline.yellow {{ background: linear-gradient(120deg, rgba(255,200,61,0.16), rgba(10,26,61,0.85) 55%); border-color: rgba(255,200,61,0.45); }}
.bs-headline.yellow .ic {{ background: #FFC83D; }}
.bs-headline.red {{ background: linear-gradient(120deg, rgba(228,55,0,0.22), rgba(10,26,61,0.85) 55%); border-color: rgba(228,55,0,0.5); }}
.bs-headline.red .ic {{ background: var(--bs-red); color: #fff; }}

/* ---------- Bilgi kutusu ---------- */
.bs-callout {{ border-radius: 12px; padding: 0.75rem 1rem; margin: 0.4rem 0 0.8rem 0; font-size: 0.93rem; line-height: 1.45;
  border: 1px solid var(--bs-line); background: rgba(10,26,61,0.65); color: #DCE6FA; }}
.bs-callout b {{ color: var(--bs-ink); }}
.bs-callout.warn {{ border-color: rgba(255,200,61,0.45); background: rgba(255,200,61,0.08); }}
.bs-callout.bad {{ border-color: rgba(228,55,0,0.5); background: rgba(228,55,0,0.10); }}
.bs-callout.good {{ border-color: rgba(43,214,123,0.45); background: rgba(43,214,123,0.08); }}

/* ---------- Strateji kartları (st.container key=bs-card-*) ---------- */
[class*="st-key-bs-card-"] {{ background: linear-gradient(180deg, rgba(14,34,80,0.92) 0%, rgba(8,20,48,0.92) 100%);
  border: 1px solid var(--bs-line) !important; border-radius: 18px !important; padding: 1.05rem 1.0rem 0.8rem 1.0rem !important;
  box-shadow: 0 16px 40px rgba(0,0,0,0.35); position: relative; overflow: hidden; }}
[class*="st-key-bs-card-"]::before {{ content:""; position:absolute; left:0; right:0; top:0; height: 4px; background: var(--card, var(--bs-yonder)); }}
.st-key-bs-card-current {{ --card: {STRATEGY_COLOR['current']}; }}
.st-key-bs-card-profit {{ --card: {STRATEGY_COLOR['profit']}; }}
.st-key-bs-card-aquifer {{ --card: {STRATEGY_COLOR['aquifer']}; }}
.st-key-bs-card-balance {{ --card: {STRATEGY_COLOR['balance']}; box-shadow: 0 0 0 1px rgba(43,214,123,0.25), 0 16px 40px rgba(0,0,0,0.35); }}
[class*="st-key-bs-panel"] {{ background: rgba(10,26,61,0.62); border: 1px solid var(--bs-line) !important; border-radius: 16px !important;
  padding: 0.9rem 1.05rem 0.6rem 1.05rem !important; }}
.bs-card-h {{ display:flex; align-items:center; gap: 0.6rem; }}
.bs-card-h .ic {{ width: 2.1rem; height: 2.1rem; border-radius: 10px; display:grid; place-items:center; font-weight: 900; font-size: 1.05rem;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); }}
.bs-card-h .tt {{ font-family: var(--bs-head); font-weight: 900; font-size: 1.32rem; color: var(--bs-ink); line-height: 1.1; }}
.bs-card-sub {{ color: var(--bs-muted); font-size: 0.84rem; margin: 0.35rem 0 0.55rem 0; min-height: 2.5em; line-height: 1.35; }}
.bs-badge-best {{ font-size: 0.66rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; color: #06102A;
  background: var(--bs-green); border-radius: 999px; padding: 0.12rem 0.5rem; margin-left: auto; }}

/* ---------- Kural rozeti ---------- */
.bs-status {{ display:inline-flex; align-items:center; gap: 0.45rem; font-weight: 800; font-size: 0.86rem; padding: 0.22rem 0.7rem 0.22rem 0.55rem;
  border-radius: 999px; border: 1px solid; }}
.bs-status .card {{ width: 11px; height: 15px; border-radius: 2px; transform: rotate(-9deg); }}
.bs-status.green {{ color: {GREEN}; border-color: rgba(43,214,123,0.5); background: rgba(43,214,123,0.10); }}
.bs-status.green .card {{ background: {GREEN}; transform:none; width: 9px; height: 9px; border-radius: 50%; }}
.bs-status.yellow {{ color: #FFC83D; border-color: rgba(255,200,61,0.55); background: rgba(255,200,61,0.10); }}
.bs-status.yellow .card {{ background: #FFC83D; }}
.bs-status.red {{ color: #FF7A4D; border-color: rgba(228,55,0,0.6); background: rgba(228,55,0,0.12); }}
.bs-status.red .card {{ background: {ROCKET}; }}

/* ---------- 4 yıllık şerit ---------- */
.bs-strip {{ display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 4px; margin: 0.6rem 0 0.75rem 0; }}
.bs-strip-wrap {{ container-type: inline-size; }}
@container (max-width: 300px) {{ .bs-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.bs-tile {{ padding: 0.45rem 0.45rem; min-height: 3.6rem; border-radius: 9px; font-size: 0.82rem; font-weight: 800; line-height: 1.18;
  position: relative; min-width: 0; overflow-wrap: break-word; box-shadow: inset 0 -2px 0 rgba(0,0,0,0.18); }}
.bs-tile .yr {{ font-size: 0.68rem; opacity: 0.82; display:block; margin-bottom: 0.18rem; font-weight: 800; letter-spacing: 0.04em; }}
.bs-tile.viol {{ outline: 2px solid {ROCKET}; outline-offset: 2px; }}
.bs-tile.viol::after {{ content:"!"; position:absolute; right:5px; top:3px; width:15px; height:15px; border-radius:50%; background:{ROCKET};
  color:#fff; font-size:0.7rem; display:grid; place-items:center; font-weight:900; }}

/* ---------- Gösterge satırları ---------- */
.bs-metric {{ display:flex; justify-content:space-between; align-items:baseline; border-bottom: 1px solid rgba(154,170,203,0.12);
  padding: 0.32rem 0; font-size: 0.9rem; gap: 0.5rem; }}
.bs-metric .k {{ color: var(--bs-muted); }}
.bs-metric .v {{ font-weight: 800; font-variant-numeric: tabular-nums; text-align:right; color: var(--bs-ink); white-space: nowrap; }}
.bs-metric .v.water {{ color: {YONDER}; }} .bs-metric .v.income {{ color: {NEON_YELLOW}; }} .bs-metric .v.neg {{ color: #FF7A4D; }}
.bs-metric.hero .v {{ font-size: 1.12rem; }}
.bs-conf {{ display:inline-block; width: 7px; height: 7px; border-radius: 50%; margin-left: 0.4rem; vertical-align: middle; }}
.bs-soil {{ margin-top: 0.7rem; padding-top: 0.55rem; border-top: 1px solid rgba(154,170,203,0.14); }}
.bs-soil-k {{ font-size: 0.8rem; color: var(--bs-muted); display:flex; justify-content:space-between; font-weight: 600; margin-top: 0.15rem; }}
.bs-soil-k.ttl {{ color: var(--bs-ink); font-weight: 800; font-size: 0.86rem; }}
.bs-bar {{ height: 6px; background: rgba(255,255,255,0.08); border-radius: 6px; overflow:hidden; margin: 0.18rem 0 0.35rem 0; }}
.bs-bar > span {{ display:block; height:100%; border-radius: 6px; background: linear-gradient(90deg, {NEON_BLUE}, {GREEN}); }}

/* ---------- Büyük rakam ---------- */
.bs-big {{ font-family: var(--bs-head); font-size: 2.3rem; font-weight: 900; line-height: 1.05; color: var(--bs-ink); }}
.bs-big.water {{ color: {YONDER}; }}
.bs-big-label {{ color: var(--bs-muted); font-size: 0.9rem; margin-bottom: 0.8rem; }}

/* ---------- Tablolar ---------- */
.bs-table-wrap {{ border: 1px solid var(--bs-line); border-radius: 14px; overflow: auto; background: rgba(10,26,61,0.55); margin: 0.3rem 0 0.8rem 0; }}
table.bs-table {{ width: 100%; border-collapse: collapse; font-size: 0.86rem; }}
table.bs-table thead th {{ position: sticky; top: 0; background: {PANEL_2}; color: var(--bs-muted); text-align: left; font-weight: 800;
  font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--bs-line-strong); }}
table.bs-table td {{ padding: 0.55rem 0.75rem; border-bottom: 1px solid rgba(154,170,203,0.10); color: #E3EBFA; vertical-align: top; line-height: 1.38; }}
table.bs-table tr:last-child td {{ border-bottom: none; }}
table.bs-table tbody tr:hover td {{ background: rgba(46,150,245,0.07); }}
table.bs-table td.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 700; }}
table.bs-table th.num {{ text-align: right; }}
table.bs-table td.small {{ color: var(--bs-muted); font-size: 0.8rem; }}

/* ---------- Diğer ---------- */
.bs-fact {{ display:flex; gap: 0.7rem; padding: 0.6rem 0.8rem; border-radius: 12px; margin: 0.35rem 0; color: #DCE6FA; line-height: 1.4;
  background: rgba(10,26,61,0.6); border: 1px solid var(--bs-line); font-size: 0.92rem; }}
.bs-fact::before {{ content:"●"; color: {ROCKET}; font-size: 0.7rem; margin-top: 0.25rem; }}
.bs-legend {{ color: var(--bs-muted); font-size: 0.8rem; margin: 0.3rem 0 0.2rem 0; display:flex; gap: 1rem; flex-wrap: wrap; }}
.bs-disclaimer {{ color: var(--bs-muted); font-size: 0.82rem; border-top: 1px solid var(--bs-line); padding-top: 0.9rem; margin-top: 2.2rem;
  display:flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }}
.bs-disclaimer .r {{ color: var(--bs-faint); }}
.bs-scenario {{ display:inline-flex; gap: 0.5rem; align-items:center; font-size: 0.86rem; font-weight: 700; color: #06102A;
  background: var(--bs-yellow); border-radius: 999px; padding: 0.25rem 0.8rem; margin: 0 0 0.6rem 0; }}
[data-testid="stCaptionContainer"] {{ color: var(--bs-muted) !important; }}
@media (max-width: 760px) {{ .bs-hero h1 {{ font-size: 2.1rem !important; }} .bs-intro {{ flex-direction: column; align-items: flex-start; }} }}
.bs-waves {{ position: relative; }}
.bs-waves::before {{ content:""; position:absolute; inset:0; opacity: 0.05; background: url(data:image/png;base64,{waves}) center/cover; pointer-events:none; }}
</style>
"""


# Sunum modu: projektörde arka sıradan okunabilsin diye her şey ~%20 büyür
PRESENT_CSS = """
<style>
html { font-size: 19px !important; }
.block-container { max-width: 1780px; }
.bs-kpi .v { font-size: 2.4rem; }
.bs-headline { font-size: 1.5rem; }
</style>
"""


def presenting() -> bool:
    try:
        return bool(st.session_state.get("present", False))
    except Exception:  # noqa: BLE001 — Streamlit oturumu dışında (testler)
        return False


def inject_css() -> None:
    st.markdown(_css(), unsafe_allow_html=True)
    if presenting():
        st.markdown(PRESENT_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Küçük yapı taşları
# ---------------------------------------------------------------------------
def esc(x) -> str:
    return html.escape(str(x))


def hero(kicker: str, title: str, text: str, steps: list[str]) -> None:
    st_html = "".join(f"<span><b>{i + 1}</b>{esc(s)}</span>" for i, s in enumerate(steps))
    st.markdown(f'<div class="bs-hero"><span class="kicker">🛰 {esc(kicker)}</span><h1>{esc(title)}</h1>'
                f'<p>{esc(text)}</p><div class="steps">{st_html}</div></div>', unsafe_allow_html=True)


def page_intro(step: str, title: str, text: str, chips: list[tuple[str, str]] | None = None) -> None:
    ch = "".join(f'<span class="bs-chip {cls}"><i></i>{esc(lbl)}</span>' for lbl, cls in (chips or []))
    st.markdown(f'<div class="bs-intro"><div class="l"><div class="step">{esc(step)}</div><h2>{esc(title)}</h2>'
                f'<p>{esc(text)}</p></div><div class="r">{ch}</div></div>', unsafe_allow_html=True)


def section(title: str, help_text: str = "") -> None:
    h = f'<div class="h">{esc(help_text)}</div>' if help_text else ""
    st.markdown(f'<div class="bs-sec"><div class="t">{esc(title)}</div>{h}</div>', unsafe_allow_html=True)


def callout(text_html: str, tone: str = "") -> None:
    """text_html güvenli (kendi ürettiğimiz) HTML olmalı."""
    st.markdown(f'<div class="bs-callout {tone}">{text_html}</div>', unsafe_allow_html=True)


def kpi_grid(items: list[dict]) -> None:
    """items: {label, value, sub, tone} — tone bir CSS rengi."""
    cells = []
    for it in items:
        tone = it.get("tone") or INK
        cells.append(f'<div class="bs-kpi" style="--tone:{tone}"><div class="lb">{esc(it["label"])}</div>'
                     f'<div class="v">{esc(it["value"])}</div><div class="s">{esc(it.get("sub", ""))}</div></div>')
    st.markdown(f'<div class="bs-kpis">{"".join(cells)}</div>', unsafe_allow_html=True)


def html_table(df: pd.DataFrame, num_cols: tuple[str, ...] = (), small_cols: tuple[str, ...] = (),
               max_height: int | None = None, html_cols: tuple[str, ...] = ()) -> None:
    """Temaya uyan HTML tablo (st.dataframe yerine; okunaklı, projektör dostu)."""
    head = "".join(f'<th class="{"num" if c in num_cols else ""}">{esc(c)}</th>' for c in df.columns)
    body = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            cls = "num" if c in num_cols else ("small" if c in small_cols else "")
            cell = v if c in html_cols else esc("" if (isinstance(v, float) and np.isnan(v)) else v)
            tds.append(f'<td class="{cls}">{cell}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    style = f' style="max-height:{max_height}px"' if max_height else ""
    st.markdown(f'<div class="bs-table-wrap"{style}><table class="bs-table"><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(body)}</tbody></table></div>', unsafe_allow_html=True)


STATUS_LABEL = {
    "tr": {"real": "Gerçek", "synthetic": "Sentetik", "default": "Varsayım", "unverified": "Doğrulanmamış", "missing": "Yok"},
    "en": {"real": "Real", "synthetic": "Synthetic", "default": "Assumed", "unverified": "Unverified", "missing": "Missing"},
}
STATUS_BAR = {"real": GREEN, "synthetic": "#FFC83D", "default": MUTED, "unverified": FAINT, "missing": ROCKET}


def data_chip(status: str, lang: str) -> str:
    return f'<span class="bs-chip {status}"><i></i>{esc(STATUS_LABEL[lang][status])}</span>'


def data_status_panel(prov: dict, lang: str, names: dict[str, str]) -> str:
    """Kenar çubuğundaki dürüst veri özeti: kaç veri seti gerçek, kaçı yer tutucu."""
    counts: dict[str, int] = {}
    for p in prov.values():
        counts[p.status] = counts.get(p.status, 0) + 1
    total = max(1, len(prov))
    bar = "".join(f'<span style="width:{counts.get(s, 0) / total * 100:.1f}%;background:{STATUS_BAR[s]}"></span>'
                  for s in ("real", "synthetic", "default", "unverified", "missing"))
    rows = "".join(f'<div class="row"><span>{data_chip(s, lang)}</span><b>{counts[s]}</b></div>'
                   for s in ("real", "synthetic", "default", "unverified", "missing") if counts.get(s))
    ttl = (f"{counts.get('real', 0)} / {total} veri seti gerçek" if lang == "tr"
           else f"{counts.get('real', 0)} / {total} datasets real")
    return f'<div class="bs-data"><div class="ttl">{esc(ttl)}</div><div class="bar">{bar}</div>{rows}</div>'


def dataset_rows(prov: dict, lang: str, names: dict[str, str]) -> str:
    out = []
    for ds, p in prov.items():
        msgs = p.messages(lang, 2)
        note = esc(" ".join(m[:180] for m in msgs)) if msgs else esc(p.label(lang))
        out.append(f'<div class="bs-ds"><div class="nm"><span>{esc(names.get(ds, ds))}</span>{data_chip(p.status, lang)}</div>'
                   f'<div class="nt">{esc(p.label(lang))}{" · " + note if msgs else ""}</div></div>')
    return "".join(out)


def _text_on(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#06102A" if lum > 0.55 else "#FFFFFF"


def status_html(status: str, lang: str) -> str:
    return (f'<span class="bs-status {status}"><span class="card"></span>'
            f'{esc(t("status_" + status, lang))}</span>')


def strip_html(parts, years: list[int], crops: dict[str, Crop], lang: str, viol_positions=()) -> str:
    tiles = []
    for i, y in enumerate(years):
        if len(parts) == 1:
            c = crops[parts[0][0][i]]
            bg, fg = c.color, _text_on(c.color)
            label = esc(c.name(lang)).replace("/", "/​")
        else:
            m = merged_year(parts, i)
            c = crops[m[0][0]]
            bg, fg = c.color, _text_on(c.color)
            if len(m) == 1:
                label = esc(c.name(lang))
            else:
                label = "<br>".join(f"%{s * 100:.0f} {esc(crops[cid].name(lang))}" if lang == "tr"
                                    else f"{s * 100:.0f}% {esc(crops[cid].name(lang))}" for cid, s in m)
        cls = "bs-tile viol" if i in viol_positions else "bs-tile"
        tiles.append(f'<div class="{cls}" style="background:{bg};color:{fg}"><span class="yr">{y}</span>{label}</div>')
    return f'<div class="bs-strip-wrap"><div class="bs-strip">{"".join(tiles)}</div></div>'


def metric_row(key: str, value: str, cls: str = "", conf: tuple[str, str] | None = None, hero_row: bool = False) -> str:
    dot = ""
    if conf:
        dot = (f'<span class="bs-conf" style="background:{CONF_COLOR[conf[0]]}" '
               f'title="{esc(conf[1])}"></span>')
    return (f'<div class="bs-metric{" hero" if hero_row else ""}"><span class="k">{esc(key)}</span>'
            f'<span class="v {cls}">{value}{dot}</span></div>')


def soil_bars(soil: dict, lang: str) -> str:
    out = []
    for k in ("nitrogen", "organic_matter", "erosion", "pest_cycle"):
        v = max(0.0, min(100.0, soil[k]))
        out.append(f'<div class="bs-soil-k"><span>{esc(t(k, lang))}</span><span>{v:.0f}</span></div>'
                   f'<div class="bs-bar"><span style="width:{v:.0f}%"></span></div>')
    return "".join(out)


def card_header(key: str, title: str, subtitle: str, best: bool = False, lang: str = "tr") -> str:
    color = STRATEGY_COLOR.get(key, YONDER)
    badge = f'<span class="bs-badge-best">{"Önerilen" if lang == "tr" else "Suggested"}</span>' if best else ""
    return (f'<div class="bs-card-h"><span class="ic" style="color:{color}">{STRATEGY_ICON.get(key, "●")}</span>'
            f'<span class="tt">{esc(title)}</span>{badge}</div><div class="bs-card-sub">{esc(subtitle)}</div>')


def option_column(option, title: str, subtitle: str, ctx, lang: str, unit: str, synthetic: bool,
                  current_key: bool = False, key: str | None = None, best: bool = False) -> None:
    det = option.detail
    m = option.metrics
    sym = ctx.basin.currency_symbol
    years = ctx.settings.plan_years
    viol = [i for i, v in enumerate(det.get("legal_viol", [])) if v] if not option.is_mix else []
    k = key or ("current" if current_key else option.key)
    st.markdown(card_header(k, title, subtitle, best, lang) + status_html(det["status"], lang)
                + strip_html(option.parts, years, ctx.crops, lang, viol), unsafe_allow_html=True)
    rows = [
        metric_row(t("mean_income", lang), money(m["mean_margin"], sym, unit, lang),
                   "income" if m["mean_margin"] >= 0 else "neg", confidence("income", synthetic, lang), hero_row=True),
        metric_row(t("bad_income", lang), money(m["cvar5"], sym, unit, lang),
                   "income" if m["cvar5"] >= 0 else "neg", confidence("risk", synthetic, lang)),
    ]
    if ctx.settings.irrigated:
        rows.append(metric_row(t("water_use", lang), water(m["water_mean"], unit, lang), "water",
                               confidence("water", synthetic, lang), hero_row=True))
    rows += [
        metric_row(t("support", lang), money(m["support_mean"], sym, unit, lang), "",
                   confidence("support", synthetic, lang)),
        metric_row(t("loss_prob", lang), f"%{m['loss_prob'] * 100:.0f}" if lang == "tr" else f"{m['loss_prob'] * 100:.0f}%"),
        metric_row(t("forage", lang), f"{num(det['soil']['forage'], lang)} kg/da"),
    ]
    st.markdown("".join(rows), unsafe_allow_html=True)
    st.markdown(
        f'<div class="bs-soil"><div class="bs-soil-k ttl"><span>{esc(t("soil_health", lang))}</span>'
        f'<span>{det["soil"]["soil"]:.0f}/100</span></div>' + soil_bars(det["soil"], lang) + "</div>",
        unsafe_allow_html=True,
    )


def why_panel(expl: dict[str, list[str]], lang: str) -> None:
    icons = {"why": "🎯", "evidence": "🛰", "benefits": "✅", "gaps": "❓", "local_risks": "📍"}
    for key, title in (("why", "why_why"), ("evidence", "why_evidence"), ("benefits", "why_benefits"),
                       ("gaps", "why_gaps"), ("local_risks", "why_local")):
        if expl.get(key):
            st.markdown(f"**{icons[key]} {t(title, lang)}**")
            st.markdown("\n".join(f"- {line}" for line in expl[key]))


def confidence_legend(lang: str, synthetic: bool) -> str:
    items = [(lvl, conf_label(lvl, lang)) for lvl in ("high", "medium", "low")]
    dots = "".join(f'<span><span class="bs-conf" style="background:{CONF_COLOR[l]};margin:0 0.35rem 0 0"></span>{esc(n)}</span>'
                   for l, n in items)
    note = ("Noktaların üzerine gelince güvenin nedeni görünür." if lang == "tr"
            else "Hover a dot to see why.")
    return f'<div class="bs-legend">{dots}<span>· {esc(note)}</span></div>'


# ---------------------------------------------------------------------------
# Grafikler
# ---------------------------------------------------------------------------
def chart(fig: go.Figure, **kw) -> None:
    """st.plotly_chart, Streamlit teması yerine BasinShift şablonuyla (koyu zemin, marka renkleri)."""
    kw.setdefault("config", {"displayModeBar": False})
    kw.setdefault("width", "stretch")
    st.plotly_chart(fig, theme=None, **kw)


def _layout(fig: go.Figure, height: int = 360, **kw) -> go.Figure:
    fig.update_layout(template="basinshift", height=height,
                      font=dict(size=16 if presenting() else 13), **kw)
    return fig


def month_names(lang: str) -> list[str]:
    return (["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"] if lang == "tr"
            else ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])


def risk_heatmap(risk: pd.DataFrame, bare: pd.Series | None, lang: str) -> go.Figure:
    rows = ["frost_days", "hard_frost", "heat_days", "extreme_heat", "heavy_rain"]
    z = [risk[r].to_numpy() for r in rows]
    labels = [t(r, lang) for r in rows]
    text = [[f"{v:.1f}" if v else "·" for v in row] for row in z]
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
        textfont=dict(color=INK, size=12),
        colorscale=[[0, "#0A1A3D"], [0.3, ELECTRIC], [0.65, YONDER], [1, NEON_YELLOW]], hoverinfo="skip",
        xgap=3, ygap=3,
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False, side="top")
    return _layout(fig, 70 + 40 * len(labels))


def water_month_chart(risk: pd.DataFrame, lang: str) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=month_names(lang), y=risk["precip_mm"], name=("Yağış (mm)" if lang == "tr" else "Rain (mm)"),
                marker=dict(color=YONDER, line=dict(width=0)), opacity=0.9)
    fig.add_scatter(x=month_names(lang), y=risk["et0_mm"], name="ET₀ (mm)", mode="lines+markers",
                    line=dict(color=NEON_YELLOW, width=3, shape="spline"), marker=dict(size=7))
    fig.update_yaxes(title="mm")
    return _layout(fig, 300)


def income_box(options: dict, crops, ctx, lang: str, unit: str, order: list[tuple[str, str]]) -> go.Figure:
    from ..explain.fmt import area_factor

    fig = go.Figure()
    f = area_factor(unit)
    for key, label in order:
        if key not in options:
            continue
        totals = options[key].detail["sim"]["margin"].sum(axis=1) * f
        color = STRATEGY_COLOR.get(key, YONDER)
        rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        fig.add_trace(go.Violin(y=totals, name=label, box_visible=True, meanline_visible=True, points="all",
                                pointpos=0, jitter=0.35, line_color=color, marker=dict(size=4, color=color, opacity=0.7),
                                fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.16)", spanmode="hard",
                                hovertemplate="%{y:,.0f}<extra>" + label + "</extra>"))
    fig.add_hline(y=0, line_color="rgba(228,55,0,0.6)", line_dash="dot")
    fig.update_yaxes(title=f"{ctx.basin.currency_symbol}/{unit} · 4 yıl" if lang == "tr" else f"{ctx.basin.currency_symbol}/{unit} · 4 years")
    return _layout(fig, 400, showlegend=False)


def pareto_chart(res, options: dict, labels: dict[str, str], ctx, unit: str, lang: str) -> go.Figure:
    from ..explain.fmt import area_factor

    f = area_factor(unit)
    feas = res.feasible
    sample = feas.sample(min(len(feas), 4000), random_state=1) if len(feas) > 4000 else feas
    fig = go.Figure()
    x_col = "water_mean" if ctx.settings.irrigated else "cvar5"
    x_title = (f"{t('water_use', lang)} (m³/{unit})" if ctx.settings.irrigated else f"{t('bad_income', lang)} ({ctx.basin.currency_symbol}/{unit})")
    fig.add_scatter(x=sample[x_col] * f, y=sample["mean_margin"] * f, mode="markers",
                    marker=dict(size=4, color="rgba(154,170,203,0.28)"),
                    name=("Kurala uygun planlar" if lang == "tr" else "Feasible plans"), hoverinfo="skip")
    p = res.pareto
    fig.add_scatter(x=p[x_col] * f, y=p["mean_margin"] * f, mode="markers",
                    marker=dict(size=8, color=p["soil"], line=dict(width=0.5, color=GROUND),
                                colorscale=[[0, ELECTRIC], [0.5, GREEN], [1, NEON_YELLOW]], showscale=True,
                                colorbar=dict(title=dict(text=t("soil_health", lang), font=dict(color=MUTED)),
                                              tickfont=dict(color=MUTED), thickness=10, outlinewidth=0)),
                    name="Pareto", text=[" → ".join(ctx.crops[c].name(lang) for c in pl) for pl in p["plan"]],
                    hovertemplate="%{text}<extra></extra>")
    for key, opt in options.items():
        m = opt.metrics
        xv = (m["water_mean"] if ctx.settings.irrigated else m["cvar5"]) * f
        fig.add_scatter(x=[xv], y=[m["mean_margin"] * f], mode="markers+text", text=[labels.get(key, key)],
                        textposition="top center", textfont=dict(color=INK, size=13),
                        marker=dict(size=16, symbol="diamond", color=STRATEGY_COLOR.get(key, INK),
                                    line=dict(width=2, color=GROUND)), showlegend=False)
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title=f"{t('mean_income', lang)} ({ctx.basin.currency_symbol}/{unit})")
    return _layout(fig, 480)


def calendar_chart(cal: pd.DataFrame, crops, risk: pd.DataFrame, lang: str) -> go.Figure:
    fig = go.Figure()
    for _, r in cal.iterrows():
        if r["start"] is None or pd.isna(r["start"]):
            continue
        c = crops[r["crop"]]
        fig.add_trace(go.Scatter(x=[r["start"], r["end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color=c.color, width=18), showlegend=False,
                                 hovertemplate=f"{c.name(lang)} {r['year']}<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["mid_start"], r["mid_end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color=ROCKET, width=5), showlegend=False,
                                 hovertemplate=("Sıcak stresine hassas" if lang == "tr" else "Heat-sensitive") + "<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["frost_start"], r["frost_end"]], y=[c.name(lang)] * 2, mode="lines",
                                 line=dict(color=INK, width=4, dash="dot"), showlegend=False,
                                 hovertemplate=("Dona hassas" if lang == "tr" else "Frost-sensitive") + "<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticksuffix="   ")
    starts = pd.to_datetime(cal["start"].dropna())
    ends = pd.to_datetime(cal["end"].dropna())
    if len(starts) and len(ends):
        months = ("Oca Şub Mar Nis May Haz Tem Ağu Eyl Eki Kas Ara" if lang == "tr"
                  else "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec").split()
        ticks = pd.date_range(starts.min().to_period("M").to_timestamp(), ends.max() + pd.offsets.MonthBegin(1), freq="6MS")
        fig.update_xaxes(tickmode="array", tickvals=list(ticks),
                         ticktext=[f"{months[d.month - 1]} {d.year}" for d in ticks])
    return _layout(fig, 110 + 52 * max(1, cal["crop"].nunique()))


def band_chart(details: list[tuple[str, dict, str]], key: str, years: list[int], factor: float, ytitle: str) -> go.Figure:
    fig = go.Figure()
    for name, det, color in details:
        arr = det["sim"][key] * factor                       # (W, N)
        p10, p50, p90 = (np.percentile(arr, q, axis=0) for q in (10, 50, 90))
        rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        fig.add_scatter(x=years + years[::-1], y=list(p90) + list(p10[::-1]), fill="toself", mode="lines",
                        fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.18)", line=dict(width=0),
                        hoverinfo="skip", showlegend=False)
        fig.add_scatter(x=years, y=p50, mode="lines+markers", name=name, line=dict(color=color, width=3, shape="spline"),
                        marker=dict(size=9, line=dict(width=2, color=GROUND)))
    fig.update_xaxes(tickmode="array", tickvals=years)
    fig.update_yaxes(title=ytitle)
    return _layout(fig, 330)


def bar_compare(labels: list[str], values: list[float], colors: list[str], ytitle: str, lang: str = "tr",
                hline: float | None = None, hline_text: str = "") -> go.Figure:
    fig = go.Figure(go.Bar(x=labels, y=values, marker=dict(color=colors, line=dict(width=0)),
                           text=[num(v, lang) for v in values], textposition="outside",
                           textfont=dict(color=INK, size=13), cliponaxis=False))
    if hline is not None:
        fig.add_hline(y=hline, line_dash="dash", line_color=YONDER, annotation_text=hline_text,
                      annotation_position="top left", annotation_font_color=YONDER,
                      annotation_bgcolor="rgba(7,23,63,0.85)")
    fig.update_yaxes(title=ytitle)
    return _layout(fig, 320)
