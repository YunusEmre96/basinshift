# BasinShift

**NASA Space Apps Challenge 2026 · Field Shift: Adapting Farms with NASA Data**

Çiftçinin 4 yıllık ekim nöbeti planını son 40+ yılın gerçek havası ve 2040'ların
iklimiyle **stres testine** sokan, kurallara ve çiftçinin koşullarına uygun en iyi
planları **otomatik bulan**, her öneriyi **gerekçesiyle açıklayan** ve aynı ekranda
bu kararın **havzanın suyuna ve ürün fiyatlarına** etkisini gösteren karar destek aracı.

> **Veri durumu (teslim):** 8 veri setinden 4'ü gerçek NASA verisi — POWER (iklim),
> GPM IMERG (yağış düzeltmesi), GRACE/GRACE-FO (havza su deposu), NEX-GDDP-CMIP6 (2040'lar).
> SMAP ve HLS/MODIS sentetik yer tutucudur (hesaba girmez / yalnızca grafik), SRTM eğimi
> ve Çumra toprağı elle girilmiştir. Her dosyanın kökeni `data/external/KAYNAK.yaml`'da
> beyan edilir; uygulama ve PDF karne bunu her ekranda yazar → [docs/DATA_SWAP.md](docs/DATA_SWAP.md)

## Hızlı başlangıç (Windows)

Klasördeki dosyalara çift tıklayın (Python 3.11+ kurulu olmalı):

| Dosya | Ne yapar |
|---|---|
| `kur.bat` | Sanal ortamı kurar, paketleri yükler, testleri çalıştırır (bir kez; internet gerekir) |
| `calistir.bat` | Uygulamayı açar → http://localhost:8501 |
| `veri_indir.bat` | Gerçek NASA verisini indirir, birim kontrolünden geçirir, başarılı veri setleri için `config.yaml`'ı günceller |
| `test.bat` | Testleri çalıştırır |
| `yedek_al.bat` | Testler + sürüm etiketi + `data/cache` dahil çevrimdışı zip (`dist/`) |
| `nasa_ek_paketler.bat` | GRACE ve CMIP6 için ek paketler |

Tarayıcıda **"Örnek tarlayı yükle: Mehmet Amca, Çumra"** düğmesine basın; uygulama doğrudan Planlar sayfasına geçer.
Projektörde kenar çubuğundan **Sunum modu**nu açın.

Linux / macOS:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python scripts/setup_real_data.py        # gerçek NASA verisi (POWER + SoilGrids; anahtar gerekmez)
```

Testler: `python -m pytest -q` (68 test; FAO-56 Örnek 18 doğrulaması, uç durumlar ve veri birim kontrolleri dahil).

## Yayına alma (Streamlit Community Cloud)

1. share.streamlit.io → **Create app** → bu depo, dal `main`, ana dosya `app.py`.
2. **Advanced settings → Python 3.12** (varsayılan 3.14 bazı paketlerle uyumsuz olabilir).
3. Secrets gerekmez. Veri (`data/external`, `data/cache`) depoda olduğu için uygulama gerçek veriyle açılır.
4. 12 saat ziyaret almayan uygulama uyur; sunumdan önce linki bir kez açın.

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
* [docs/PROJECT_PAGE_EN.md](docs/PROJECT_PAGE_EN.md) — İngilizce proje sayfası (gönderim formu için)
* [docs/BRIEF_CHECK.md](docs/BRIEF_CHECK.md) — NASA brifi karşılama tablosunun uygulamayla satır satır kontrolü
* [docs/VERIFICATION_LOG.md](docs/VERIFICATION_LOG.md) — hangi rakam hangi kaynaktan teyit edildi, ne varsayım kaldı
* [docs/QA_PREP.md](docs/QA_PREP.md) — jürinin zor soruları ve cevaplar
* [docs/SUNUM_PAKETI.md](docs/SUNUM_PAKETI.md) — pitch metni, video akışı, gönderim kontrol listesi

## Varsayımları güncellemek (kod bilmeden)

| Ne | Nerede |
|---|---|
| Ürün katsayıları, sezonlar, eşikler, yerel riskler | `tables/crops.csv` |
| Fiyat, verim, maliyet, ekim tarihi (havza bazında) | `tables/basin_economics.csv` |
| Önceki ürün etkileri | `tables/rotation_effects.csv` |
| Kurallar ve destek tutarları | `tables/rules/*.yaml` |
| Havza modeli çiftlik tipleri | `tables/farm_types.csv` |
| Pilot noktalar | `tables/basins.yaml` |

## Teyit durumu (14 Kasım 2026)

Ayrıntı ve kaynaklar: [docs/VERIFICATION_LOG.md](docs/VERIFICATION_LOG.md).

* **Teyit edildi:** münavebe kuralı (4 üretim yılında en fazla 2, art arda değil; silajlık mısır kapsamda), 19 Konya ilçesi,
  buğday/arpa/nohut/mercimek/aspir/ayçiçeği temel+planlı destek tutarları (Eylül 2026 güncellemesi), TMO buğday-arpa ve
  TÜRKŞEKER pancar alım fiyatları.
* **Hâlâ varsayım:** su kısıtı desteğinin bir kısmı (katsayıdan türetildi), fiğ/silaj/pancar/yonca destekleri, mısır ve
  baklagil fiyatları, bütün maliyetler, rotasyon etkisi katsayıları ve ara verme süreleri (yerel ziraat mühendisi).

## Lisans ve kaynaklar

NASA verileri NASA'nın açık veri politikasıyla kullanılır. Yöntemler: FAO
Irrigation and Drainage Paper 56 (Allen vd., 1998) ve 33 (Doorenbos & Kassam, 1979).
Tam kaynak listesi: docs/METHODS.md ve proje planı.
