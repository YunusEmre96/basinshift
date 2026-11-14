"""BasinShift — NASA verisiyle ekim nöbeti stres testi ve havza karar destek aracı.

Katmanlar:
    data       -> değiştirilebilir veri sağlayıcıları (sentetik / NASA / dosya)
    knowledge  -> ürün, ekonomi, kural tabloları
    engine     -> FAO-56 su, FAO-33 verim, toprak, risk, stres testi
    optimizer  -> plan tarama, Pareto, kartlar
    explain    -> "Neden bu plan?", güven etiketleri, sözlük
    basin      -> havza LP, örümcek ağı fiyat simülasyonu, gölge fiyat
    report     -> Risk & Su Karnesi (PDF)
    ui         -> Streamlit arayüzü
"""

__version__ = "1.0.0"
