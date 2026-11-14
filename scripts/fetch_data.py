"""Gerçek veriyi indirip önbelleğe yazar (demo öncesi, internet varken çalıştırın).

Örnekler:
    # Konya'nın tüm pilot noktaları için NASA POWER iklim verisi (anahtar gerekmez)
    python scripts/fetch_data.py --basin konya --datasets climate_daily

    # Tüm veri setleri (Earthdata gerektirenler için önce ortam değişkenleri):
    #   export EARTHDATA_USERNAME=... EARTHDATA_PASSWORD=...   (ya da EARTHDATA_TOKEN)
    python scripts/fetch_data.py --basin konya --datasets all

    # Tek bir nokta
    python scripts/fetch_data.py --basin konya --site cumra --datasets climate_daily,soil_moisture

İndirilen veri data/cache/nasa/ altına yazılır; uygulama BASINSHIFT_DATA=nasa ile
açıldığında internet olmasa bile bu önbellekten okur. Bir veri seti başarısız
olursa hata mesajı yazdırılır ve diğerleriyle devam edilir.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from basinshift.config import DATASETS, load_config  # noqa: E402
from basinshift.data.basins import load_basins  # noqa: E402
from basinshift.data.hub import DataHub  # noqa: E402

SITE_DATASETS = ("climate_daily", "soil_moisture", "ndvi", "precip_satellite", "climate_deltas", "terrain", "soil_properties")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--basin", default="konya")
    ap.add_argument("--site", default=None, help="tek nokta (varsayılan: havzadaki tüm noktalar)")
    ap.add_argument("--datasets", default="climate_daily", help="virgülle ayrılmış liste ya da 'all'")
    ap.add_argument("--source", default="nasa", choices=["nasa", "files"])
    args = ap.parse_args()

    os.environ["BASINSHIFT_DATA"] = args.source
    cfg = load_config()
    cfg["data"]["fallback_to_synthetic"] = False
    hub = DataHub(cfg)
    basin = load_basins()[args.basin]
    sites = [basin.site(args.site)] if args.site else list(basin.sites)
    wanted = DATASETS if args.datasets == "all" else tuple(d.strip() for d in args.datasets.split(","))

    ok = True
    for ds in wanted:
        targets = sites if ds in SITE_DATASETS else [None]
        for site in targets:
            label = f"{ds} · {site.name if site else basin.name_tr}"
            try:
                if site is None:
                    data = getattr(hub, ds)(basin)
                elif ds == "climate_daily":
                    data = hub.climate_daily(site, basin)
                else:
                    data = getattr(hub, ds)(site, basin)
                if data is None:
                    raise RuntimeError("; ".join(hub.provenance[ds].warnings) or "veri yok")
                size = len(data) if hasattr(data, "__len__") else 1
                print(f"✓ {label}: {size} kayıt (önbellek: {cfg['data']['cache']['dir']})")
                for note in hub.provenance[ds].notes:
                    print(f"    not: {note}")
            except Exception as exc:  # noqa: BLE001
                ok = False
                print(f"✗ {label}: {exc}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
