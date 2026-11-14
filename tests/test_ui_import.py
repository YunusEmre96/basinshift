"""Arayüz modülleri sözdizimi/içe aktarma hatası olmadan yüklenmeli (Streamlit açılmadan yakalanır)."""
import importlib
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_all_python_files_compile():
    for f in list((ROOT / "basinshift").rglob("*.py")) + [ROOT / "app.py"]:
        py_compile.compile(str(f), doraise=True)


def test_ui_modules_import():
    for m in ("basinshift.ui.components", "basinshift.ui.pages", "basinshift.ui.state", "basinshift.ui.i18n"):
        importlib.import_module(m)


def test_i18n_keys_used_in_pages_exist():
    import re
    from basinshift.ui.i18n import STRINGS
    src = (ROOT / "basinshift" / "ui" / "pages.py").read_text(encoding="utf-8")
    keys = set(re.findall(r'\bt\("([a-z0-9_]+)"', src))
    missing = sorted(k for k in keys if k not in STRINGS and not k.endswith("_"))   # "_" ile biten: dinamik önek
    assert not missing, missing
