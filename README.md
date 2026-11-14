# BasinShift

**NASA Space Apps Challenge 2026 · Field Shift: Adapting Farms with NASA Data**

Çiftçinin 4 yıllık ekim nöbeti planını son 40+ yılın gerçek havası ve 2040'ların
iklimiyle **stres testine** sokan, kurallara ve çiftçinin koşullarına uygun en iyi
planları **otomatik bulan**, her öneriyi **gerekçesiyle açıklayan** ve aynı ekranda
bu kararın **havzanın suyuna ve ürün fiyatlarına** etkisini gösteren karar destek aracı.

> **Demo modu:** NASA verisi bağlanana kadar uygulama gerçek şemayla aynı,
> fiziksel olarak tutarlı **sentetik** veriyle çalışır ve bunu her ekranda açıkça
> söyler. Gerçek veriye geçiş tek bir ayardır → [docs/DATA_SWAP.md](docs/DATA_SWAP.md)

## Hızlı başlangıç

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Tarayıcıda açılan sayfada **"Örnek tarlayı yükle: Mehmet Amca, Çumra"** düğmesine basın.

Gerçek NASA POWER iklim verisiyle (anahtar gerekmez):

```bash
python scripts/fetch_data.py --basin konya --datasets climate_daily
BASINSHIFT_DATA_CLIMATE_DAILY=nasa streamlit run app.py
```

Testler: `python -m pytest -q` (46 test; FAO-56 Örnek 18 doğrulaması dahil).

## Sayfalar

| Sayfa | Ne gösterir |
|---|---|
| **Tarla** | Geçmiş ürünler, düşünülen plan, su/ekipman/sözleşme/alıcı/yem koşulları, öncelikler, kural paketleri, uydudan ürün geçmişi doğrulaması |
| **İklim geçmişi** | Risk takvimi (don, sıcak, şiddetli yağış, kurak ay, çıplak toprak), aylık yağış/ET0, Mann-Kendall eğilim testi, NDVI ve SMAP serileri, uydu–iklim verisi yağış karşılaştırması |
| **Planlar** | Mevcut plan + Kâr / Akifer / Denge kartları, sarı/kırmızı kart, toprak alt skorları, yem, güven etiketleri, "Neden bu plan?" (5 başlık), 40 yıllık gelir dağılımı, ürün takvimi, örtü bitkisi ödünleşimi, Pareto görünümü |
| **İki gelecek** | Alışkanlıkla ekim ile BasinShift planının 2027–2030 gelir ve su aralıkları |
| **Havza** | GRACE su deposu, obruk bilgileri, bugünkü / koordinasyonsuz / koordineli senaryolar, koordinasyonsuzluğun bedeli, suyun gölge fiyatı, örümcek ağı fiyat döngüsü |
| **Karne** | Banka/sigorta/kooperatif için tek sayfalık PDF Risk ve Su Karnesi |
| **Yöntem ve veriler** | Veri seti–ürün–çözünürlük–kullanılan kaynak tablosu, varsayımlar ve güven düzeyleri, sözlük |

Kenar çubuğu: dil (TR/EN), havza (Konya, Central Valley, Pencap, Murray-Darling),
konum (pilot noktalar veya koordinat), alan birimi (da/ha), **Ya şöyle olursa?**
(sıcaklık, yağış, CMIP6 2040'lar), veri kaynakları durumu.

## Belgeler

* [docs/DATA_SWAP.md](docs/DATA_SWAP.md) — sentetikten gerçek NASA verisine geçiş, dosya biçimleri, yeni API bağlama
* [docs/METHODS.md](docs/METHODS.md) — tüm formüller, katsayılar ve varsayımlar
* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — kod yapısı ve tasarım ilkeleri
* [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) — 3 dakikalık jüri demosu
* [docs/PROJECT_PAGE_EN.md](docs/PROJECT_PAGE_EN.md) — İngilizce proje sayfası taslağı

## Varsayımları güncellemek (kod bilmeden)

| Ne | Nerede |
|---|---|
| Ürün katsayıları, sezonlar, eşikler, yerel riskler | `tables/crops.csv` |
| Fiyat, verim, maliyet, ekim tarihi (havza bazında) | `tables/basin_economics.csv` |
| Önceki ürün etkileri | `tables/rotation_effects.csv` |
| Kurallar ve destek tutarları | `tables/rules/*.yaml` |
| Havza modeli çiftlik tipleri | `tables/farm_types.csv` |
| Pilot noktalar | `tables/basins.yaml` |

## Teyit edilmesi gerekenler (sunumdan önce)

* Konya su kısıtı ilçe listesi ve 2026 destek tutarları (şu an yerel haberlerden; `tr_konya_water_2026.yaml`)
* Silajlık mısırın kısıt kapsamında olup olmadığı
* 2026 ürün fiyatları ve maliyetleri (`basin_economics.csv`)
* Rotasyon etkisi katsayıları ve hastalık ara verme süreleri (yerel ziraat mühendisi)

## Lisans ve kaynaklar

NASA verileri NASA'nın açık veri politikasıyla kullanılır. Yöntemler: FAO
Irrigation and Drainage Paper 56 (Allen vd., 1998) ve 33 (Doorenbos & Kassam, 1979).
Tam kaynak listesi: docs/METHODS.md ve proje planı.
