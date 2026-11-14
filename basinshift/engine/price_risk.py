"""Borsa / fiyat riski: planın gelirini hava ile birlikte FİYAT dalgalanmasına karşı da sınar.

Ana stres testi 2026 sabit fiyatlarıyla yapılır (yalnızca hava belirsizliği). Bu modül aynı
41 geçmiş dönemi, her ürün için yıllık fiyat çarpanlarıyla K kez yeniden oynatır:

    çarpan[k, yıl, ürün] ~ LogNormal(ortalama 1, CV = tables/price_risk.csv → price_cv) × (1 + şok)
    kâr' = kâr + verim × fiyat × (çarpan − 1)

Aynı takvim yılı her dönemde aynı fiyat çarpanını alır (dönemler örtüştüğü için tutarlı).
Ürünler arası fiyat ilişkisi yok sayılır (varsayım). Tohum sabit: sonuçlar tekrarlanabilir.
Çıktılar: ortalama kâr, kötü dönem geliri (her fiyat senaryosunda CVaR %5, senaryoların ortalaması),
zarar eden yıl olasılığı.
"""
from __future__ import annotations

import numpy as np

from ..knowledge.tables import load_price_risk
from .metrics import cvar

DEFAULT_CV = 0.20
N_DRAWS = 200
SEED = 2026


def price_cv(basin_id: str, crop_ids: list[str]) -> dict[str, float]:
    df = load_price_risk()
    sub = df[df["basin"] == basin_id].set_index("crop_id") if not df.empty else None
    out = {}
    for c in crop_ids:
        if sub is not None and c in sub.index:
            out[c] = float(sub.loc[c, "price_cv"])
        else:
            out[c] = 0.0 if c == "fallow" else DEFAULT_CV
    return out


def _parts(option) -> list[tuple[dict, float]]:
    d = option.detail
    if option.is_mix:
        return list(zip(d["parts"], d["shares"]))
    return [(d, 1.0)]


def price_multipliers(ctx, cv: dict[str, float], shock: dict[str, float] | None = None,
                      n_draws: int = N_DRAWS, seed: int = SEED) -> np.ndarray:
    """(K, Y, C) çarpan dizisi — ctx.table.years × ctx.crop_ids."""
    rng = np.random.default_rng(seed)
    y, c = len(ctx.table.years), len(ctx.crop_ids)
    sig = np.array([np.sqrt(np.log(1 + cv.get(cid, DEFAULT_CV) ** 2)) for cid in ctx.crop_ids])
    z = rng.standard_normal((n_draws, y, c))
    mult = np.exp(sig * z - sig ** 2 / 2)
    if shock:
        mult = mult * np.array([1 + shock.get(cid, 0.0) for cid in ctx.crop_ids])
    return mult


def option_price_risk(option, ctx, mult: np.ndarray) -> dict[str, float]:
    win = ctx.windows()                                     # (W, N) yıl indeksleri
    total = None
    for det, share in _parts(option):
        idx = ctx.idx(det["plan"])                          # (N,)
        m = det["sim"]["margin"]                            # (W, N)
        rev = det["sim"]["yield"] * ctx.price[idx][None, :]  # (W, N)
        k_mult = mult[:, win, idx[None, :]]                 # (K, W, N)
        adj = m[None] + rev[None] * (k_mult - 1)
        total = adj * share if total is None else total + adj * share
    window_mean = total.mean(axis=2)                        # (K, W)
    # Kötü dönem geliri her fiyat senaryosunda ana stres testiyle AYNI tanımla (41 dönemin en kötü %5'i)
    # hesaplanır, sonra senaryoların ortalaması alınır → sıfır oynaklıkta ana sonuçla birebir aynı.
    return {
        "mean_margin": float(total.mean()),
        "cvar5": float(cvar(window_mean, 0.05, axis=1).mean()),
        "loss_prob": float((total < 0).mean()),
        "p10_window": float(np.percentile(window_mean.reshape(-1), 10)),
    }


def weather_only(option) -> dict[str, float]:
    m = option.metrics
    return {"mean_margin": float(m["mean_margin"]), "cvar5": float(m["cvar5"]), "loss_prob": float(m["loss_prob"])}
