"""BasinShift — Streamlit giriş noktası.

Çalıştırma:
    pip install -r requirements.txt
    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from basinshift.config import load_config
from basinshift.ui import components as ui
from basinshift.ui import pages, state
from basinshift.ui.i18n import t

st.set_page_config(page_title="BasinShift", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

cfg = load_config()
state.init_state(cfg)
state.persist_widgets()
ui.inject_css()
pages.sidebar()
lang = st.session_state["lang"]

PAGES = [
    ("field", "page_field", "🌾", pages.page_field),
    ("status", "page_status", "🌦️", pages.page_status),
    ("plans", "page_plans", "📊", pages.page_plans),
    ("futures", "page_futures", "🔮", pages.page_futures),
    ("basin", "page_basin", "🗺️", pages.page_basin),
    ("report", "page_report", "📄", pages.page_report),
    ("method", "page_method", "🔬", pages.page_method),
]


def _wrap(fn, key):
    def run():
        pages.header(show_tagline=(key == "field"))
        # Veri kaynaklarının durumu (sentetik/geri düşme) için önce ana veriyi yükle
        state.site_data()
        pages.banners()
        fn()
        pages.footer()
    return run


page_objs = {
    key: st.Page(_wrap(fn, key), title=t(title_key, lang), icon=icon, url_path=key, default=(key == "field"))
    for key, title_key, icon, fn in PAGES
}
state.register_pages(page_objs)
nav_pages = list(page_objs.values())
try:
    nav = st.navigation(nav_pages, position="top")
except TypeError:  # eski Streamlit sürümleri
    nav = st.navigation(nav_pages)

# Bir düğme "şu sayfaya geç" dediyse (ör. örnek tarla yüklendi → Planlar) önce oraya git
_target = st.session_state.pop("_goto", None)
if _target in page_objs:
    try:
        st.switch_page(page_objs[_target])
    except Exception:  # noqa: BLE001 — geçiş desteklenmiyorsa bulunduğu sayfada kalır
        pass
nav.run()
