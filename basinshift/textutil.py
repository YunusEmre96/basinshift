"""İki dilli kısa metinler için yardımcılar.

Veri katmanı ve hesap çekirdeği arayüz dilini bilmez; ürettikleri not ve
uyarıları ``bi(tr, en)`` ile iki dilde tek bir dizgeye koyar. Arayüz, PDF ve
açıklama metinleri gösterirken ``loc(metin, dil)`` ile doğru dili seçer.
``bi`` kullanılmamış (yalnızca Türkçe) eski metinler olduğu gibi döner.
"""
from __future__ import annotations

SEP = "␟"   # görünmez olmayan ama metinde geçmeyen ayırıcı (␟)

#: Şema ve sağlayıcı etiketlerindeki Türkçe parçaların İngilizce karşılıkları
EN_FRAGMENTS = (
    ("SENTETİK — gerçek ürün:", "SYNTHETIC — real product:"),
    ("Agroclimatology, günlük", "Agroclimatology, daily"),
    ("3 saatlik (günlüğe toplanır)", "3-hourly (aggregated to daily)"),
    ("günlük → aylık değişim", "daily → monthly change"),
    ("yerel toprak etüdü", "local soil survey"),
    ("(günlük)", "(daily)"),
    ("aylık", "monthly"),
    ("SMAP+yağış göstergesi", "SMAP + rainfall proxy"),
    ("yağış göstergesi", "rainfall proxy"),
)


def bi(tr: str, en: str) -> str:
    return f"{tr}{SEP}{en}"


def loc(text, lang: str = "tr") -> str:
    """İki dilli dizgeden istenen dili seçer; İngilizcede bilinen Türkçe parçaları çevirir."""
    if text is None:
        return ""
    s = str(text)
    if SEP in s:
        tr, en = s.split(SEP, 1)
        s = tr if lang == "tr" else en
    if lang != "tr":
        for a, b in EN_FRAGMENTS:
            s = s.replace(a, b)
    return s
