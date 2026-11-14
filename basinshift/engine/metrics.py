"""Risk ölçüleri."""
from __future__ import annotations

import math

import numpy as np


def cvar(values: np.ndarray, alpha: float = 0.05, axis: int = -1) -> np.ndarray:
    """Koşullu Riske Maruz Değer (alt kuyruk): en kötü %alpha değerlerin ortalaması.

    Gelir için "işler kötü giderse ortalama ne kazanırım?" sorusunun cevabı.
    """
    v = np.moveaxis(np.asarray(values, dtype=float), axis, -1)
    n = v.shape[-1]
    k = max(1, math.ceil(alpha * n))
    part = np.partition(v, k - 1, axis=-1)[..., :k]
    return part.mean(axis=-1)


def percentile(values: np.ndarray, q: float, axis: int = -1) -> np.ndarray:
    return np.percentile(values, q, axis=axis)
