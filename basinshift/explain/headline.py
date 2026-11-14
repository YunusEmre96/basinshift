"""Planlar sayfasının en üstündeki tek cümlelik özet.

Jürinin "sonuç ne?" sorusuna 10 saniyede cevap: mevcut planın kural durumu ve
önerilen planın ona göre su, destek ve kötü dönem geliri farkı. Metin yalnızca
hesaplanmış değerlerden şablonla üretilir.
"""
from __future__ import annotations

from .fmt import area_factor, money, water

STATUS = {
    "tr": {"green": "kurallara uygun", "yellow": "sarı kart riski taşıyor", "red": "kırmızı kart riski taşıyor"},
    "en": {"green": "complies with the rules", "yellow": "risks a yellow card", "red": "risks a red card"},
}


def headline_numbers(current, best) -> dict:
    """Mevcut plana göre farklar (dekar başına, yıllık). Pozitif d_water = daha AZ su."""
    c, b = current.metrics, best.metrics
    return {
        "water_saved": float(c["water_mean"] - b["water_mean"]),
        "water_saved_pct": float((c["water_mean"] - b["water_mean"]) / c["water_mean"] * 100) if c["water_mean"] > 0 else 0.0,
        "support_gain": float(b["support_mean"] - c["support_mean"]),
        "bad_income_gain": float(b["cvar5"] - c["cvar5"]),
        "margin_gain": float(b["mean_margin"] - c["mean_margin"]),
    }


def headline(current, best, best_title: str, sym: str, irrigated: bool, lang: str = "tr", unit: str = "da") -> str:
    """Örn.: 'Mevcut planınız kırmızı kart riski taşıyor. Denge planı kurallara uygun: yılda 400 m³/da
    daha az su (%41), +973 ₺/da destek, kötü dönemde +1.600 ₺/da.'"""
    if current is None or best is None:
        return ""
    tr = lang == "tr"
    n = headline_numbers(current, best)
    cs, bs = current.detail["status"], best.detail["status"]
    first = (f"Mevcut planınız {STATUS['tr'][cs]}." if tr else f"Your current plan {STATUS['en'][cs]}.")
    parts = []
    if irrigated and abs(n["water_saved"]) >= 1:
        w = water(abs(n["water_saved"]), unit, lang)
        pct = abs(n["water_saved_pct"])
        if tr:
            parts.append(f"yılda {w} {'daha az' if n['water_saved'] > 0 else 'daha fazla'} su (%{pct:.0f})")
        else:
            parts.append(f"{w} {'less' if n['water_saved'] > 0 else 'more'} water per year ({pct:.0f}%)")

    def signed(v: float) -> str:
        return ("+" if v >= 0 else "−") + money(abs(v), sym, unit, lang)

    if abs(n["support_gain"]) >= 1:
        parts.append(f"{signed(n['support_gain'])} " + ("destek" if tr else "support"))
    parts.append((f"kötü dönemde {signed(n['bad_income_gain'])}" if tr else f"{signed(n['bad_income_gain'])} in bad periods"))
    second = (f"{best_title} planı {STATUS['tr'][bs]}: " if tr else f"The {best_title} plan {STATUS['en'][bs]}: ") + ", ".join(parts) + "."
    return first + " " + second


__all__ = ["headline", "headline_numbers", "area_factor"]
