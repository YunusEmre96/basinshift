"""Önceki ürün etkisi matrisleri (rotation_effects.csv'den).

Öncelik sırası: ürün→ürün > ürün→aile > aile→ürün > aile→aile > 1.0
"""
from __future__ import annotations

import numpy as np

from ..knowledge.tables import Crop, load_rotation_effects


def rotation_matrices(crop_ids: list[str], crops: dict[str, Crop]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(verim çarpanı, azot maliyet tasarrufu oranı, güven) — her biri (C+1, C).

    Son satır (indeks C) "önceki ürün bilinmiyor" durumudur → nötr.
    """
    df = load_rotation_effects()
    n = len(crop_ids)
    mult = np.ones((n + 1, n))
    ncred = np.zeros((n + 1, n))
    conf = np.full((n + 1, n), "", dtype=object)
    rank = np.full((n + 1, n), -1)

    def keys(cid):
        return {cid: 3, f"family:{crops[cid].family}": 1}

    for r in df.to_dict("records"):
        prev, curr = str(r["prev"]).strip(), str(r["curr"]).strip()
        for i, pid in enumerate(crop_ids):
            pk = keys(pid)
            if prev not in pk:
                continue
            for j, cid in enumerate(crop_ids):
                ck = keys(cid)
                if curr not in ck:
                    continue
                score = pk[prev] + ck[curr]   # ürün-ürün=6, ürün-aile=4, aile-ürün=4, aile-aile=2
                if score > rank[i, j]:
                    rank[i, j] = score
                    mult[i, j] = float(r["yield_multiplier"])
                    ncred[i, j] = float(r["n_credit_cost_share"])
                    conf[i, j] = r["confidence"]
    return mult, ncred, conf
