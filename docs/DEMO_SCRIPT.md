# 3 dakikalık demo akışı

Demo öncesi: `calistir.bat` açık, tarayıcı tam ekran (F11), dil Türkçe, kenar çubuğunda **Sunum modu** açık.
İnternet çökerse diye 60 saniyelik ekran kaydı hazır. Rakamları **ekrandan okuyun**. Teslim halindeki (gerçek POWER + IMERG düzeltmesi) Mehmet Amca rakamları: Denge planı yılda
574 m³/da daha az su (%58), +1.248 ₺/da destek, kötü dönemde +2.075 ₺/da. Köşeli parantezdeki yerler ekrandaki sayıdır.

| Süre | Ekran | Ne söylenir / ne yapılır |
|---|---|---|
| 0:00–0:25 | **Havza** (GRACE grafiği + obruk bilgileri) | "Konya'da 739 obruk kayıtlı. 2025'te 244 mm yağış. Yeraltı suyu 30 metre düştü. Bu grafik havzanın toplam su deposu. Aynı kriz Kaliforniya'da, Pencap'ta, Avustralya'da." Havza menüsünü açıp dört havzayı gösterin, Konya'da bırakın. |
| 0:25–0:40 | **Tarla** | Aşağı kaydırıp uydudan doğrulama tablosunu gösterin: "Gerçek HLS verisi bağlandığında çiftçinin beyanını uydu kontrol edecek; şu an NDVI sentetik, ekranda da öyle yazıyor." Yukarı çıkıp **"Örnek tarlayı yükle"** düğmesine basın: "Mehmet Amca, Çumra, 120 dekar. 2025'te pancar, 2026'da mısır ekti; aynısını sürdürmek istiyor." Uygulama kendiliğinden Planlar'a geçer. |
| 0:40–1:30 | **Planlar** | En üstteki özet cümleyi okuyun: "Mevcut planı kırmızı kart riski taşıyor. Denge planı yılda [ ] m³ daha az su, [ ] ₺ destek." Dört sütun: "BasinShift 20 binden fazla planı son 40 yılın havasıyla sınadı. Kâr, Akifer, Denge. Üçü de kurala uygun." Bir kartın **Neden bu plan?** bölümünü açın. Kutu grafiği: "Mevcut plan kötü yıllarda çöküyor; bu plan dar ve yüksek." |
| 1:30–1:45 | Kenar çubuğu: **Ya şöyle olursa?** | Jüriye dönün: "Yağış %20 azalırsa?" Kaydırıcıyı −20'ye çekin; özet cümle ve kartlar güncellenir. |
| 1:45–2:05 | **İki gelecek** | "Aynı tarla, iki farklı 2027–2030." Üç büyük rakam: su farkı, destek farkı, kâr farkı. |
| 2:05–2:25 | **Havza** (aşağı kaydırın) | "Bir çiftçi için doğru olan, bin çiftçi yapınca obruk olabilir." Üç senaryo çubuğu, koordinasyonsuzluğun bedeli, suyun gölge fiyatı. "Çiftlik tipleri temsilidir; mekanizmayı gösteriyoruz." |
| 2:25–2:40 | **Karne** | PDF'i indirin; basılı örneği jüri masasına bırakın. "Çiftçiye ücretsiz; kooperatif, şeker fabrikası, banka ve sigorta öder." |
| 2:40–3:00 | **Yöntem ve veriler** | "Hangi veri gerçek, hangisi değil, ne varsayıyoruz: hepsi burada. GRACE'i tarla için kullanmıyoruz; OpenET Türkiye'yi kapsamadığı için FAO-56 kullandık." Kapanış: "Bankalara stres testi yapılıyor. Artık tarlalara da." |

## Demodan önce 2 dakikalık kontrol

1. Kenar çubuğunda "N / 8 veri seti gerçek" kaç yazıyor? Teslim halinde **4 / 8** (POWER, IMERG, GRACE, CMIP6). Sunumda aynı sayıyı söyleyin; "8/8" demeyin.
2. Örnek tarlayı yükleyin; özet cümledeki üç rakamı bir kâğıda yazın.
3. Yağışı −20 yapın; kartların değiştiğini görün; sıfıra geri alın.
4. Karne PDF'ini indirip açın.
5. İnterneti kapatıp sayfayı yenileyin: harita altlığı boş kalabilir, hesaplar çalışmalı.

## Sık sorulan sorular için ekranlar

* "Bu veri gerçek mi?" → Kenar çubuğu **Veri kaynakları** ve **Yöntem ve veriler** tablosu.
* "Katsayılar nereden?" → `tables/` klasörü, docs/METHODS.md; güven noktaları (yeşil/okra/kırmızı).
* "Başka ülkede çalışır mı?" → Havza menüsünden Pencap'a geçin; kural paketi değişir, motor aynı.
* "AB'de?" → Tarla sayfasında kural paketlerine "AB GAEC 7" ekleyin.
* Diğer sorular: docs/QA_PREP.md.
