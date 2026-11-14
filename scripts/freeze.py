"""Kod dondurma: testleri çalıştırır, sürümü etiketler ve çevrimdışı çalışan bir zip üretir.

    python scripts/freeze.py                 # etiket: final-YYYYMMDD-HHMM
    python scripts/freeze.py --tag v1.0

Zip (dist/BasinShift_<etiket>.zip) data/cache klasörünü de içerir; böylece sunum
bilgisayarında internet olmadan gerçek veriyle açılır. .venv, .git ve .env zip'e GİRMEZ.
USB'ye kopyalamak size kalır.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", ".pytest_cache", "dist"}
SKIP_FILES = {".env"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=time.strftime("final-%Y%m%d-%H%M"))
    ap.add_argument("--skip-tests", action="store_true")
    args = ap.parse_args()

    if not args.skip_tests:
        print("Testler çalışıyor…")
        if subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=ROOT) != 0:
            print("Testler geçmedi; dondurma İPTAL. (Yine de almak için: --skip-tests)")
            return 1

    secrets = [p for p in ROOT.rglob("*") if p.is_file() and p.name == ".env"]
    if secrets:
        print("Not: .env dosyası var; zip'e ve git'e alınmıyor.")

    if (ROOT / ".git").exists():
        subprocess.call(["git", "add", "-A"], cwd=ROOT)
        subprocess.call(["git", "commit", "-q", "-m", f"Dondurma: {args.tag}"], cwd=ROOT)
        subprocess.call(["git", "tag", "-f", args.tag], cwd=ROOT)

    out = ROOT / "dist" / f"BasinShift_{args.tag}.zip"
    out.parent.mkdir(exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob("*")):
            rel = p.relative_to(ROOT)
            if not p.is_file() or any(part in SKIP_DIRS for part in rel.parts) or p.name in SKIP_FILES:
                continue
            z.write(p, Path("basinshift") / rel)
            n += 1
    cache = sum(1 for _ in (ROOT / "data" / "cache").rglob("*.csv.gz")) + sum(1 for _ in (ROOT / "data" / "cache").rglob("*.json"))
    print(f"Yedek hazır: {out}  ({n} dosya, {out.stat().st_size / 1e6:.1f} MB; önbellekte {cache} veri dosyası)")
    if cache == 0:
        print("UYARI: data/cache boş — zip yalnızca sentetik veriyle açılır. Önce veri_indir.bat çalıştırın.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
