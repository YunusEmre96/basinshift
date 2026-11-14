"""Güven etiketleri: her sonucun ne kadar güvenilir olduğu (yüksek / orta / düşük).

Güven iki şeye bağlıdır:
    1. Yöntemin kabul görmüşlüğü (ör. FAO-56 su hesabı → yüksek; fiyat tahmini → düşük)
    2. Verinin kaynağı (sentetik demo verisi → her şey "düşük")
"""
from __future__ import annotations

HIGH, MEDIUM, LOW = "high", "medium", "low"
ORDER = [LOW, MEDIUM, HIGH]

METHOD_CONFIDENCE = {
    "water": (HIGH, "FAO-56 günlük su dengesi; dünyada standart yöntem",
              "FAO-56 daily water balance; the global standard method"),
    "yield": (MEDIUM, "FAO-33 verim tepkisi + literatür rotasyon katsayıları (varsayım)",
              "FAO-33 yield response + literature rotation coefficients (assumption)"),
    "risk": (MEDIUM, "Geçmiş 40+ yılın gerçek dizileri; gelecek geçmişe benzemeyebilir",
             "Real 40+ year historical sequences; the future may differ"),
    "income": (LOW, "Fiyat ve maliyetler 2026 varsayımı; piyasa dalgalanır",
               "Prices and costs are 2026 assumptions; markets fluctuate"),
    "soil": (MEDIUM, "Plan içeriğinden kural tabanlı puan; uydudan ölçülmez",
             "Rule-based score from plan content; not measured by satellite"),
    "support": (MEDIUM, "Kural ve destek tutarları resmi metinle teyit edilmeli",
                "Rules and support amounts must be verified with official text"),
    "basin": (LOW, "Temsili çiftlik tipleri ve varsayımsal fiyat esnekliği",
              "Representative farm types and assumed price elasticities"),
}

LABELS = {
    "tr": {HIGH: "Yüksek güven", MEDIUM: "Orta güven", LOW: "Düşük güven"},
    "en": {HIGH: "High confidence", MEDIUM: "Medium confidence", LOW: "Low confidence"},
}


def confidence(metric: str, synthetic: bool, lang: str = "tr") -> tuple[str, str]:
    level, why_tr, why_en = METHOD_CONFIDENCE[metric]
    why = why_tr if lang == "tr" else why_en
    if synthetic:
        level = LOW
        why = ("SENTETİK demo verisi — " if lang == "tr" else "SYNTHETIC demo data — ") + why
    return level, why


def label(level: str, lang: str) -> str:
    return LABELS[lang][level]
