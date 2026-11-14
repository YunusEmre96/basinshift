"""Gerçek NASA verisini indirir, birim/ölçek kontrolünden geçirir ve başarılı
olan veri setleri için config.yaml'daki kaynağı ``nasa`` yapar.

Tek komut (Windows'ta ``veri_indir.bat``):

    python scripts/setup_real_data.py                      # anahtar gerektirmeyenler: POWER + SoilGrids
    python scripts/setup_real_data.py --earthdata          # + SMAP, HLS/MODIS, SRTM, GRACE (Earthdata gerekir)
    python scripts/setup_real_data.py --datasets climate_deltas   # yalnızca CMIP6
    python scripts/setup_real_data.py --basins konya       # yalnızca Konya (kaynak DEĞİŞTİRİLMEZ, aşağıya bakın)

Kurallar:
    * Bir veri seti ancak DÖRT havzanın bütün pilot noktalarında indirilip kontrolden
      geçerse config.yaml'da ``nasa`` yapılır. Böylece demoda havza değiştirince turuncu
      "sentetiğe düşüldü" uyarısı çıkmaz. Kısmi başarı önbellekte kalır, kaynak sentetik kalır.
    * İndirilen her şey data/cache/nasa/ altına yazılır; sonrasında internet gerekmez.
    * Earthdata kimliği yalnızca ortam değişkeninden ya da git'e girmeyen ``.env`` dosyasından
      okunur (EARTHDATA_TOKEN ya da EARTHDATA_USERNAME / EARTHDATA_PASSWORD).
    * Rapor: data/veri_raporu.txt (gerçek veri ile sentetiğin yan yana karşılaştırması dahil).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

NO_KEY = ("climate_daily", "soil_properties")
EARTHDATA = ("soil_moisture", "ndvi", "terrain", "water_storage")
BASIN_LEVEL = ("water_storage",)


def load_dotenv(path: Path) -> None:
    """Çok küçük .env okuyucu (ek paket gerektirmez). Var olan ortam değişkenini ezmez."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------------------------------------------------------------------------
# Birim ve ölçek kontrolleri
# ---------------------------------------------------------------------------
def check_climate(df, basin_id: str) -> tuple[list[str], list[str], dict]:
    """(hatalar, uyarılar, özet). Hata = veri kullanılmamalı; uyarı = göz atın."""
    errs, warns = [], []
    yearly = df["precip"].resample("YS").sum(min_count=300)
    p = float(yearly.mean())
    tmean = float(df["tmean"].mean())
    stats = {"yıllık yağış (mm)": p, "ort. sıcaklık (°C)": tmean,
             "en yüksek Tmax (°C)": float(df["tmax"].max()), "en düşük Tmin (°C)": float(df["tmin"].min()),
             "ort. radyasyon (MJ/m²/gün)": float(df["rs"].mean()), "ort. rüzgâr (m/s)": float(df["wind2m"].mean())}
    if not 20 <= p <= 4000:
        errs.append(f"yıllık yağış {p:.0f} mm akla yatkın değil (birim hatası olabilir)")
    if basin_id == "konya" and not 250 <= p <= 450:
        warns.append(f"Konya için yıllık yağış {p:.0f} mm; beklenen 250–450 mm")
    if not 3 <= stats["ort. radyasyon (MJ/m²/gün)"] <= 32:
        errs.append(f"radyasyon ortalaması {stats['ort. radyasyon (MJ/m²/gün)']:.1f} MJ/m²/gün aralık dışı (kWh ile karışmış olabilir)")
    if df["tmax"].lt(df["tmin"] - 0.5).mean() > 0.01:
        errs.append("günlerin %1'inden fazlasında Tmax < Tmin")
    for col in ("tmax", "tmin", "precip"):
        miss = float(df[col].isna().mean())
        if miss > 0.05:
            errs.append(f"{col}: verinin %{miss * 100:.1f}'i eksik")
        elif miss > 0.005:
            warns.append(f"{col}: verinin %{miss * 100:.1f}'i eksik")
    span = (df.index.max() - df.index.min()).days / 365.25
    if span < 30:
        errs.append(f"seri yalnızca {span:.0f} yıl; stres testi için en az 30 yıl gerekir")
    return errs, warns, stats


def check_soil_moisture(df) -> tuple[list[str], list[str], dict]:
    errs, warns = [], []
    hi = float(df[["sm_surface", "sm_rootzone"]].max().max())
    lo = float(df[["sm_surface", "sm_rootzone"]].min().min())
    if hi > 0.6 or lo < 0:
        errs.append(f"SMAP değerleri {lo:.2f}–{hi:.2f}; beklenen 0–0,5 m³/m³")
    elif hi > 0.5:
        warns.append(f"SMAP en yüksek {hi:.2f} m³/m³ (0,5 üstü nadirdir)")
    return errs, warns, {"en düşük": lo, "en yüksek": hi, "ortalama kök bölgesi": float(df["sm_rootzone"].mean())}


def check_ndvi(df) -> tuple[list[str], list[str], dict]:
    errs, warns = [], []
    lo, hi = float(df["ndvi"].min()), float(df["ndvi"].max())
    if lo < -1 or hi > 1:
        errs.append(f"NDVI {lo:.2f}–{hi:.2f}; −1 ile 1 arasında olmalı (ölçek faktörü uygulanmamış olabilir)")
    if hi < 0.3:
        warns.append(f"en yüksek NDVI {hi:.2f}; tarım alanı için düşük (nokta tarla dışında olabilir)")
    n_hls = int((df["source"] == "HLS").sum())
    if n_hls < 50:
        warns.append(f"yalnızca {n_hls} bulutsuz HLS gözlemi var")
    return errs, warns, {"en düşük": lo, "en yüksek": hi, "HLS gözlem": n_hls, "MODIS gözlem": int((df["source"] == "MODIS").sum())}


def check_generic(data) -> tuple[list[str], list[str], dict]:
    if isinstance(data, dict):
        return [], [], {k: v for k, v in data.items()}
    return [], [], {"satır": len(data)}


CHECKS = {"climate_daily": check_climate, "soil_moisture": lambda d, b: check_soil_moisture(d),
          "ndvi": lambda d, b: check_ndvi(d)}


def run_check(ds: str, data, basin_id: str):
    fn = CHECKS.get(ds)
    return fn(data, basin_id) if fn else check_generic(data)


def fmt_stats(stats: dict) -> str:
    return "; ".join(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in stats.items())


# ---------------------------------------------------------------------------
def set_config_sources(config_path: Path, datasets: list[str], source: str = "nasa") -> list[str]:
    """config.yaml içinde yalnızca ilgili satırları değiştirir (yorumlar korunur)."""
    text = config_path.read_text(encoding="utf-8")
    changed = []
    for ds in datasets:
        pat = re.compile(rf"^(\s+{re.escape(ds)}:\s*)(\S+)", re.MULTILINE)
        m = pat.search(text)
        if m and m.group(2) != source:
            text = pat.sub(lambda mm: mm.group(1) + source, text, count=1)
            changed.append(ds)
    if changed:
        config_path.write_text(text, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--basins", default="all", help="virgülle ayrılmış havza kimlikleri ya da 'all'")
    ap.add_argument("--datasets", default=None, help="virgülle ayrılmış veri setleri (varsayılan: anahtarsız olanlar)")
    ap.add_argument("--earthdata", action="store_true", help="Earthdata gerektiren veri setlerini de indir")
    ap.add_argument("--no-switch", action="store_true", help="config.yaml'a dokunma, yalnızca indir ve kontrol et")
    args = ap.parse_args(argv)

    load_dotenv(ROOT / ".env")
    os.environ["BASINSHIFT_DATA"] = "nasa"
    for k in [k for k in os.environ if k.startswith("BASINSHIFT_DATA_")]:
        del os.environ[k]

    from basinshift.config import DEFAULT_CONFIG_PATH, load_config
    from basinshift.data.basins import load_basins
    from basinshift.data.hub import DataHub
    from basinshift.textutil import loc

    cfg = load_config()
    cfg["data"]["fallback_to_synthetic"] = False
    hub = DataHub(cfg)
    os.environ["BASINSHIFT_DATA"] = "synthetic"
    syn = DataHub(load_config())
    all_basins = load_basins()
    basin_ids = list(all_basins) if args.basins == "all" else [b.strip() for b in args.basins.split(",")]
    if args.datasets:
        wanted = [d.strip() for d in args.datasets.split(",")]
    else:
        wanted = list(NO_KEY) + (list(EARTHDATA) if args.earthdata else [])
    if any(d in EARTHDATA for d in wanted) and not (os.environ.get("EARTHDATA_TOKEN") or
                                                    (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"))):
        print("UYARI: Earthdata kimliği bulunamadı (.env ya da ortam değişkeni). AppEEARS/GRACE indirmeleri başarısız olacak.")

    lines: list[str] = [f"BasinShift veri raporu — {time.strftime('%Y-%m-%d %H:%M')}", ""]
    ok_all: dict[str, bool] = {}

    def say(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    for ds in wanted:
        say(f"=== {ds} ===")
        ok_all[ds] = True
        for bid in basin_ids:
            basin = all_basins[bid]
            targets = [None] if ds in BASIN_LEVEL else list(basin.sites)
            for site in targets:
                label = f"{basin.name_tr}" + (f" / {site.name}" if site else "")
                t0 = time.time()
                try:
                    data = getattr(hub, ds)(basin) if site is None else getattr(hub, ds)(site, basin)
                    if data is None:
                        key = [k for k in hub.records if k[0] == ds][-1]
                        raise RuntimeError("; ".join(loc(w, "tr") for w in hub.records[key].warnings) or "veri yok")
                    errs, warns, stats = run_check(ds, data, bid)
                    mark = "HATA " if errs else ("UYARI" if warns else "TAMAM")
                    say(f"  [{mark}] {label} ({time.time() - t0:.0f} sn) — {fmt_stats(stats)}")
                    for e in errs:
                        say(f"          HATA: {e}")
                    for w in warns:
                        say(f"          uyarı: {w}")
                    if ds == "climate_daily" and site is not None:
                        s = syn.climate_daily(site, basin)
                        _, _, sstats = check_climate(s, bid)
                        say(f"          sentetik karşılaştırma — {fmt_stats(sstats)}")
                    if errs:
                        ok_all[ds] = False
                except Exception as exc:  # noqa: BLE001 — bir nokta başarısız olsa da diğerlerine devam
                    ok_all[ds] = False
                    say(f"  [BAŞARISIZ] {label}: {type(exc).__name__}: {str(exc)[:400]}")
        say("")

    partial = set(basin_ids) != set(all_basins)
    good = [d for d, ok in ok_all.items() if ok]
    bad = [d for d, ok in ok_all.items() if not ok]
    if args.no_switch or partial:
        say("config.yaml DEĞİŞTİRİLMEDİ (" + ("--no-switch" if args.no_switch else "yalnızca bazı havzalar indirildi") + ").")
    else:
        changed = set_config_sources(Path(DEFAULT_CONFIG_PATH), good)
        if good:
            say("config.yaml → kaynağı 'nasa' olan veri setleri: " + ", ".join(good)
                + (f" (yeni değişen: {', '.join(changed)})" if changed else " (zaten ayarlıydı)"))
    if bad:
        say("Sentetik kalanlar (indirilemedi ya da kontrolden geçmedi): " + ", ".join(bad))
        say("Yedek yol: veriyi web arayüzünden CSV indirip data/external/ altına koyun (docs/DATA_SWAP.md, bölüm 5).")
    report = ROOT / "data" / "veri_raporu.txt"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    say(f"Rapor: {report}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
