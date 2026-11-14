# Teyit günlüğü (14 Kasım 2026)

Sunumda söylenen her rakamın nereden geldiği. Üç etiket: **KAYNAKLI** (yayımlanmış kaynakta birebir var),
**TÜRETİLMİŞ** (kaynaklı rakamdan hesapla çıkarıldı), **VARSAYIM** (kaynak bulunamadı; değer tahmindir).
Jüri sorarsa etiketi olduğu gibi söyleyin.

## 1. Münavebe kuralı — `tables/rules/tr_konya_water_2026.yaml`

| Konu | Durum | Dayanak |
|---|---|---|
| Sulu arazide mısır (dane/silaj), patates, şeker pancarı, domates, havuç: 4 üretim yılında art arda gelmemek şartıyla en fazla 2 kez | KAYNAKLI | Destekleme tebliği haberleri (Ülke TV, Bigpara; 1 Ocak 2026'da yürürlük); Tarım ve Orman Bakanlığı "Tarımsal Üretim Planlaması" belgesi |
| Silajlık mısır kapsamda | KAYNAKLI | Tebliğ metni "mısır (dane/silaj)" diyor. Kural dosyasında kapsamda bırakıldı |
| Başlangıç: 2024 üretim yılı ÇKS kaydındaki son ürün | KAYNAKLI | Bakanlık belgesi |
| Konya'da 19 ilçe (Türkiye: 11 il, 52 ilçe) | KAYNAKLI | Konya İl Müdürlüğü açıklaması (tarimdanhaber.com). Liste: Akören, Akşehir, Altınekin, Cihanbeyli, Çumra, Derbent, Doğanhisar, Emirgazi, Ereğli, Güneysınır, Halkapınar, Kadınhanı, Karapınar, Karatay, Kulu, Meram, Sarayönü, Selçuklu, Tuzlukçu |
| İlk yıl sarı kart (uyarı), ikinci yıl kırmızı kart ve tüm desteklerden mahrumiyet | KAYNAKLI | Aynı açıklama |
| Sarı kart yılında o yılın desteğinin sıfır olması | **YORUM** | Destek "planlı üretime ve münavebeye uygun üretene" ödeniyor; haber sarı kartı "uyarı" diye anlatıyor. İl Müdürlüğü'ne sorun |
| Dane mısır ve patatese su kısıtlı havzalarda destek yok | KAYNAKLI | 2026 Yılı Destekleme Birim Fiyatları dipnotu (BÜGEM) |

**Dikkat:** Bazı haberlerde bir ziraat odası başkanı kuralı "aynı parsele 4 yıl aynı ürün ekilemez" diye
anlatıyor. Tebliğ ifadesi bu değil; biz tebliğ ifadesini kodladık. Proje planı, haberlerde Halkapınar / Hadim /
Hüyük farkı olduğunu not etmişti; elimizdeki listede Halkapınar var, Hadim ve Hüyük yok.

## 2. Destek tutarları (TL/da)

Eylül 2026 kararıyla destek katsayı değeri 310 → 367 TL/da oldu (Alomaliye, Bloomberg HT, Dünya; 8 Eylül 2026).
Kılavuz ve proje planındaki "806 + 434" rakamı eski katsayıya aittir.

| Ürün | Temel + planlı üretim | Su kısıtı desteği | Durum |
|---|---|---|---|
| Buğday, arpa | 954 | 514 | 954 KAYNAKLI; 514 TÜRETİLMİŞ (eski 434 ÷ 310 = 1,4 katsayı × 367) |
| Nohut, mercimek | 734 | 294 | 734 KAYNAKLI; 294 TÜRETİLMİŞ (kaynaklı katsayı 0,8 × 367; eski tutar 248) |
| Aspir | 734 | 294 | 734 KAYNAKLI; 294 TÜRETİLMİŞ |
| Yağlık ayçiçeği | 1.101 | 440 | 1.101 KAYNAKLI; 440 TÜRETİLMİŞ (toplam ~1.300 TL haberinden 1,2 katsayı) |
| Fiğ | 734 | 294 | 734 VARSAYIM (yem bitkisi); 294 TÜRETİLMİŞ |
| Silajlık mısır | 477 | — | VARSAYIM |
| Şeker pancarı | 367 | — | VARSAYIM |
| Yonca | 367 | — | VARSAYIM |
| Dane mısır, patates | 0 | — | KAYNAKLI |

Eylül zammının su kısıtı desteğine de yansıdığı **varsayıldı**. Resmi tablo: tarimorman.gov.tr → BÜGEM →
"2026 Yılı Destekleme Birim Fiyatları" (PDF'i tarayıcıda açıp satır satır karşılaştırın; 10 dakikalık iş).

## 3. Fiyatlar — `tables/basin_economics.csv`

| Ürün | Fiyat (TL/kg) | Durum | Kaynak |
|---|---|---|---|
| Buğday | 16,50 | KAYNAKLI | TMO 2026, 2. grup ekmeklik/makarnalık 16.500 TL/ton (2 Haziran 2026) |
| Arpa | 12,75 | KAYNAKLI | TMO 2026, 12.750 TL/ton |
| Şeker pancarı | 3,72 | KAYNAKLI | TÜRKŞEKER 2026-27, 3.720 TL/ton, kota tamamlama primi dahil (13 Ekim 2026). Konya Şeker fiyatı farklı olabilir |
| Ayçiçeği | 34,00 | KAYNAKLI (aralığın alt ucu) | 2026 ön alım: Karadenizbirlik 34.000, Trakya Birlik 37.000 TL/ton (%44 yağ) |
| Dane mısır | 11,00 | VARSAYIM | TMO 2026'da mısır alım fiyatı açıklamadı |
| Nohut, mercimek, aspir, fiğ, patates, silaj, yonca | tabloda | VARSAYIM | Konya Ticaret Borsası bülteniyle güncellenmeli |
| Bütün değişken maliyetler ve verimler | tabloda | VARSAYIM | TÜİK / ziraat odası maliyet cetveliyle güncellenmeli |

Fiyatların bir kısmı güncel, maliyetler varsayım olduğu için **mutlak kâr rakamları düşük güvenlidir** (ekranda kırmızı
nokta). Planlar arasındaki su ve kural farkları fiyattan bağımsızdır.

## 4. Akla yatkınlık kontrolleri (otomatik test olarak da var)

| Kontrol | Beklenen | Modelde |
|---|---|---|
| Pancar sulaması, yağmurlama, Çumra | 700–1.000 m³/da | Sentetik veriyle ~1.000 m³/da; test aralığı 650–1.150 |
| Damla sulama tasarrufu | %23–26 (FAO Konya rehberi: pancar %25,5, mısır %23,5) | %16,7 (yalnızca randıman farkı: 0,75 → 0,90). Model tasarrufu **olduğundan az** gösteriyor; temkinli tarafta |
| Taranan plan sayısı | Belgelerle aynı | 20.736 (12⁴) |

## 5. Hâlâ sizin yapmanız gerekenler

- [ ] BÜGEM birim fiyat PDF'i ile bölüm 2 tablosunu karşılaştırın; farkları `tr_konya_water_2026.yaml`'a yazın.
- [ ] Sarı kart yılında destek kesiliyor mu? (İl Müdürlüğü ya da bir ziraat odası; tek telefon.)
- [ ] Konya Ticaret Borsası'ndan nohut, mercimek, mısır fiyatı.
- [ ] Bir ziraat mühendisine `tables/rotation_effects.csv` ve `crops.csv → min_gap_years` sütununu 10 dakika gösterin.
- [ ] Obruk sayıları (739 / 702 / 126 / 32), 244 mm ve 30 m rakamları haber kaynaklıdır; slaytta kaynak yazın.


## Ek: Veri durumu ve kod denetimi (14 Kasım 2026, son tur)

| Konu | Durum | Dayanak |
|---|---|---|
| Kenar çubuğu önceki sürümde "8 / 8 gerçek" gösteriyordu | **DÜZELTİLDİ** | `data/external/` altındaki SMAP ve NDVI dosyaları `export_synthetic` çıktısıyla birebir (r = 0,99); dosyanın klasörde olması "gerçek" sayılıyordu. Artık köken `KAYNAK.yaml`'dan okunuyor → 4 / 8 |
| PDF karnedeki sentetik veri uyarısı kaldırılmıştı | **DÜZELTİLDİ** | `report/scorecard.py` uyarıları geri geldi |
| POWER yağışı (Çumra ≈ 539 mm) istasyon normalinin (~320–330 mm) çok üstünde | **DÜZELTİLDİ** | IMERG aylık oran düzeltmesi (`engine/pipeline.py`) |
| `tables/commodity_trade.csv` içinde kaynaksız sanal su ve dünya fiyatı sütunları | **KALDIRILDI** | Yalnızca kaynaklı ticaret bilgisi + kaynak sütunu; su değerleri modelden |
| Un ihracatında dünya birinciliği; 2025'te 2.344.528 t | KAYNAKLI | Un sanayicileri açıklamaları (Ekonomi Gazetesi, Yeni Asır, Ekim 2026) |
| Mısır tüketimi ~12 Mt, üretim ~8,5 Mt, 2024 ithalatı ~4,4 Mt | KAYNAKLI | Türkiye Tarım Birliği / TÜİK (Ekonomim, 2025) |
| Ayçiçeğinde yeterlilik 2024/25'te %63 | KAYNAKLI | TÜİK denge tabloları (Ekonomi Gazetesi, 2026) |
| Buğdayda tam sulama varsayımı mutlak su değerini yükseltir | **SINIRLAMA** | METHODS.md §2; sıralamayı değiştirmez |
