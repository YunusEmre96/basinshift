"""Pareto cephesi: hiçbir göstergede başka bir plandan geri kalmayan planlar."""
from __future__ import annotations

import numpy as np


def pareto_mask(obj: np.ndarray) -> np.ndarray:
    """obj: (P, K), tüm sütunlar "büyük daha iyi". Dönen: (P,) bool.

    Plan i, başka bir j her göstergede ≥ ve en az birinde > ise elenir.
    Birinci göstergeye göre sıralayıp aday cepheye karşı vektörel kontrol
    yapılır: O(P · |cephe|).
    """
    obj = np.asarray(obj, dtype=float)
    p = obj.shape[0]
    order = np.lexsort(obj.T[::-1])[::-1]   # önce 1. sütun, eşitlikte sonrakiler (azalan)
    front: list[int] = []
    front_vals = np.empty((0, obj.shape[1]))
    for i in order:
        v = obj[i]
        if len(front):
            dominated = np.all(front_vals >= v, axis=1) & np.any(front_vals > v, axis=1)
            if dominated.any():
                continue
            same = np.all(front_vals == v, axis=1)
            if same.any():
                continue
        front.append(i)
        front_vals = np.vstack([front_vals, v])
    mask = np.zeros(p, dtype=bool)
    mask[front] = True
    return mask
