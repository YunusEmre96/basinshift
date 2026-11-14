"""Sentetik veriyi data/external/ biçiminde CSV olarak dışa aktarır.

İki amaçla kullanılır:
    1. 'files' kaynağının beklediği dosya biçimini görmek (şablon)
    2. Gerçek NASA dosyası geldiğinde aynı adla üzerine yazmak

    python scripts/export_synthetic.py --basin konya --out data/external_example
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os  # noqa: E402

os.environ["BASINSHIFT_DATA"] = "synthetic"

from basinshift.data.basins import load_basins  # noqa: E402
from basinshift.data.hub import DataHub  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--basin", default="konya")
    ap.add_argument("--out", default="data/external_example")
    args = ap.parse_args()
    out = Path(args.out)
    hub = DataHub()
    basin = load_basins()[args.basin]
    for site in basin.sites:
        for ds in ("climate_daily", "soil_moisture", "ndvi", "precip_satellite"):
            df = getattr(hub, ds)(site, basin)
            p = out / ds / f"{site.id}.csv"
            p.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(p, index_label="date", float_format="%.4f")
        deltas = hub.climate_deltas(site, basin)
        p = out / "climate_deltas" / f"{site.id}.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        deltas.to_csv(p, index=False, float_format="%.4f")
        for ds in ("terrain", "soil_properties"):
            p = out / ds / f"{site.id}.csv"
            p.parent.mkdir(parents=True, exist_ok=True)
            row = getattr(hub, ds)(site, basin)
            p.write_text(",".join(row) + "\n" + ",".join(f"{v}" for v in row.values()) + "\n", encoding="utf-8")
    ws = hub.water_storage(basin)
    p = out / "water_storage" / f"{basin.id}.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    ws.to_csv(p, index_label="date", float_format="%.3f")
    print(f"Şablon dosyalar yazıldı: {out.resolve()}")
    print(json.dumps({"not": "Bu dosyalar SENTETİKTİR; yalnızca biçim örneğidir."}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
