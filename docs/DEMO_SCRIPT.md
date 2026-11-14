# 3 dakikalık demo akışı

Planın 20. bölümündeki pitch akışının uygulamadaki karşılığı. Demo öncesi:
`streamlit run app.py` açık, tarayıcı tam ekran, dil Türkçe. İnternet çökerse
diye ekran kaydı (60 sn) hazır olsun.

| Süre | Ekran | Ne söylenir / ne yapılır |
|---|---|---|
| 0:00–0:25 | **Havza** sayfası (GRACE grafiği + obruk bilgileri) | "Konya'da 739 obruk. 2025'te 244 mm yağış. Yeraltı suyu 30 metre düştü. Bu grafik NASA'nın GRACE uydusundan: havzanın suyu her yıl azalıyor. Aynı kriz Kaliforniya'da, Pencap'ta, Avustralya'da." Kenar çubuğunda havza menüsünü açıp dört havzayı gösterin, Konya'da bırakın. |
| 0:25–0:40 | **Tarla** | "Örnek tarlayı yükle"ye basın. "Mehmet Amca, Çumra, 120 dekar. 2025'te pancar, 2026'da mısır ekti; aynısını sürdürmek istiyor." Uydudan doğrulama tablosunu gösterin: "Beyanını uydu da doğruluyor." |
| 0:40–1:30 | **Planlar** | Üstte kırmızı kart: "Mevcut planı 2027'de kırmızı kart alıyor; destek tamamen kesiliyor." Dört sütun: "BasinShift 28 bin planı son 40 yılın havasıyla sınadı. Kâr, Akifer, Denge. Her biri kurala uygun." Bir kartın **Neden bu plan?** bölümünü açın: gerekçe, kanıt, fayda, bilgi boşlukları, yerel riskler. Kutu grafiği: "Mevcut plan kötü yıllarda çöküyor; bu plan dar ve yüksek." |
| 1:30–1:45 | Kenar çubuğu: **Ya şöyle olursa?** | Jüriye dönün: "Yağış %20 azalırsa?" Kaydırıcıyı −20'ye çekin; kartlar güncellenir. Ya da "2040'lar · yüksek emisyon" seçin. |
| 1:45–2:05 | **İki gelecek** | "Aynı tarla, iki farklı 2027–2030." Büyük rakamlar: 4 yılda su farkı, korunan destek, kâr farkı. |
| 2:05–2:25 | **Havza** (aşağı kaydırın) | "Bir çiftçi için doğru olan, bin çiftçi yapınca obruk olabilir." Üç senaryo çubukları, koordinasyonsuzluğun bedeli, suyun gölge fiyatı: "Konya'da 1 m³ ek suyun havzaya değeri bu kadar; damla sulama yatırımının değeri buradan okunur." Örümcek ağı grafiği: "Herkes geçen yılın fiyatına bakınca fiyatlar böyle dalgalanıyor." |
| 2:25–2:40 | **Karne** | PDF'i indirin; basılı örneği jüri masasına bırakın. "Çiftçiye ücretsiz; kooperatif, şeker fabrikası, banka ve sigorta öder." |
| 2:40–3:00 | **Yöntem ve veriler** | "Hangi veri hangi ölçekte, ne varsayıyoruz — hepsi burada. GRACE'i tarla için kullanmıyoruz; OpenET Türkiye'yi kapsamadığı için FAO-56 kullandık." Kapanış: "Bankalara stres testi yapılıyor. Artık tarlalara da." |

## Sık sorulan sorular için ekranlar

* "Bu veri gerçek mi?" → Kenar çubuğu **Veri kaynakları** (her veri setinin kaynağı) ve **Yöntem ve veriler** tablosu.
* "Katsayılar nereden?" → `tables/` klasörü ve docs/METHODS.md; güven noktaları (yeşil/okra/kırmızı).
* "Başka ülkede çalışır mı?" → Havza menüsünden Pencap'a geçin; kural paketi değişir, motor aynı.
* "AB'de?" → Tarla sayfasında kural paketlerine "AB GAEC 7" ekleyin.
