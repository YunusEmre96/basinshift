# Jürinin zor soruları (prova kâğıdı)

Kural: cevap en fazla üç cümle. Bilmediğinizi bilmiyorum diye söyleyin, sonra ekranda nereye bakılacağını gösterin.
Proje planı bölüm 21 ve kılavuz bölüm 12 temel alındı; uygulamanın bugünkü haline göre düzeltildi.

## Veri

**Bu veri gerçek mi?**
Kenar çubuğunda "N / 8 veri seti gerçek veriden" yazıyor ve her veri setinin kaynağı açılır listede. Sentetik kalanlar
sarı şeritle ve PDF karnede uyarıyla işaretli. (Sunumdan önce bu sayıya bakın ve aynısını söyleyin.)

**0,5° iklim verisi bir tarla için kaba değil mi?**
İklim bölge ölçeğinde değişir; 50 km içinde sıcaklık ve yağış rejimi benzerdir. Tarlada fark yaratan toprak ve yönetimdir;
onlar kullanıcı girdisinden ve SoilGrids'ten gelir. Her verinin ölçeği "Yöntem ve veriler" tablosunda yazar.

**GRACE'i neden tarla hesabında kullanmadınız?**
Çözünürlüğü yaklaşık 300 km; tek tarla için anlamsız. Yalnızca "havzanın suyu azalıyor mu?" sorusunda kullanıyoruz.

**ECOSTRESS, OpenET?**
OpenET Türkiye'yi kapsamıyor. ECOSTRESS'i kullanmadık; su ihtiyacını POWER ve FAO-56 ile hesaplıyoruz ve ET0'ı kitaptaki
örnekle doğruladık (3,88'e karşı 3,9 mm/gün).

## Yöntem

**Sonuçların doğru olduğunu nereden biliyorsunuz?**
ET0 FAO-56 Örnek 18 ile doğrulandı; pancar sulaması literatürdeki 700–1.000 m³/da aralığında çıkıyor; 62 otomatik test var.
Verim tarafı yerel kayıtlarla henüz doğrulanmadı; yol haritasının ilk adımı bu.

**Katsayılar nereden?**
Kc ve Ky FAO-56 ve FAO-33 tablolarından. Önceki ürün etkisi ve iklim stresi oranları literatür ortalaması, "varsayım"
etiketli ve `tables/` klasöründe açık.

**Damla sulama tasarrufunuz FAO'nun Konya rehberindeki %23–26'dan düşük, neden?**
Biz yalnızca randıman farkını sayıyoruz (0,75'ten 0,90'a, yaklaşık %17). Rehberdeki ek tasarruf programlı sulamadan geliyor;
modelimiz tasarrufu olduğundan az gösteriyor, yani temkinli tarafta.

**Fiyatları nereden biliyorsunuz?**
Buğday, arpa, pancar ve ayçiçeği 2026 açıklanan alım fiyatları; diğerleri ve bütün maliyetler varsayım. Bu yüzden gelirin
güven etiketi kırmızı. Planlar arasındaki su ve kural farkı fiyattan bağımsız.

**Yapay zekâ nerede?**
Karar yolunda yok, bilerek. Her rakamın hangi formülden geldiğini gösterebiliyoruz. Geliştirme sırasında yapay zekâ
asistanı kullandık ve bunu proje sayfasında beyan ettik.

**Geçmiş hava geleceği temsil eder mi?**
Tek başına etmez; aynı test CMIP6 2040'lar değişim katsayılarıyla ve kaydırıcılarla da çalışıyor. Geçmişin değeri,
gerçekten yaşanmış kurak dizileri içermesi.

**Toprak sağlığını uydudan mı ölçüyorsunuz?**
Hayır. Planın içeriğinden dört alt skor hesaplıyoruz; uydu yalnızca tarlanın hangi aylarda çıplak kaldığını gösteriyor.

## Kural ve destek

**Kural doğru mu? Değişirse?**
Kural tebliğ ifadesiyle aynı: 4 üretim yılında en fazla iki kez, art arda değil, silaj dahil. Destek tutarlarının bir kısmı
katsayıdan türetildi ve öyle etiketli. Kural bir YAML dosyası; değişiklik kod gerektirmez.

**Sarı kartta destek kesiliyor mu?**
Kırmızı kartta tüm destek kesiliyor, bu kaynaklı. Sarı kart yılında desteği sıfır saymak bizim yorumumuz; teyit etmedik.

**Neden 4 yıl?**
Kural 4 yıllık pencereye dayanıyor.

## Havza

**Havzadaki çiftlikler gerçek mi?**
Hayır, beş temsili tip; ekranda öyle yazıyor. Rakamlar yönü ve büyüklük mertebesini gösterir.

**Koordineli planı kim uygulayacak?**
Plan emir değil, pusula. Kamu destek tasarımında, kooperatif üyeleri arasında ürün paylaşımında kullanır; suyun gölge
fiyatı tasarruf yatırımının önceliğini gösterir.

## Ürün, İş Modeli ve Hedef Kitle

**Hedef kitleniz tam olarak kim? Çiftçi için bu arayüz fazla karmaşık değil mi?**
Projenin müşterisi ve karar vericisi B2B/B2G: Tarım Kredi Kooperatifleri, Şeker Fabrikaları (Konya Şeker/TÜRKŞEKER sözleşmeli tarım ekipleri), Ziraat Odaları, TARSİM ve Tarım Bankacılığıdır. Çiftçi tek başına kullandığında ise sistem "3 Tıkla Karar" mantığıyla çalışır: 1. Tarlayı seç, 2. Kırmızı kart cezasından kaçıran 3 hazır planı (Kâr, Akifer, Denge) gör, 3. Tek sayfalık PDF karneni al. Pareto cephesi, CMIP6 iklim deltalari ve cobweb fiyat dinamikleri çiftçiyi boğmamak için "Mühendis Görünümü" açılır penceresinde tutulur.

**Projeyle ihracat/ithalat ve dünya piyasaları entegre mi? Buğday, mısır, un ticareti için ne söylüyor?**
Evet. "Havza" sayfasındaki Küresel Ticaret ve Emtia tablosunda her ürün için TMO/yerel borsa fiyatı ile CBOT/Euronext dünya gösterge fiyatı, ulusal ticaret dengesi ve sanal su ayak izi kıyaslanır. Örneğin; Türkiye dünyanın #1 un ihracatçısıdır, ancak kuraklıkta buğday ithal eder; mısırda yılda ~2.5 milyon ton ithalat açığı vardır ama mısır ton başına 1.280 m³ yeraltı suyu tüketir; ayçiçeğinde %60 ham yağ ithalat bağımlılığı vardır. Model, mısır yerine ayçiçeği ve kışlık buğday rotasyonunu teşvik ederek hem akiferi korur hem de Türkiye'nin döviz faturasını ve un sanayisinin yerli hammadde güvencesini destekler.

**Uygulama sadece "şunu ek buna bak" diyen mekanik bir rotasyon aracı mı, yoksa tavsiye ve stratejik karar destek sistemi mi?**
Kör bir tavsiye sistemi değil, çok kriterli bir karar pusulasıdır. 20.736 olası 4 yıllık kombinasyonu tarar; mevzuat kuralı (kırmızı kart), 40 yıllık NASA iklim verisi, yeraltı suyu çekimi, kötü dönem geliri (CVaR %5), toprak sağlığı ve küresel emtia dengesini bir araya getirir. Kullanıcıya tek bir emir dayatmaz; "Kâr", "Akifer (Su Koruma)" ve "Denge" alternatifleri sunar; her kartın neden önerildiğini, kanıtını, bilgi boşluğunu ve yerel riskini şeffafça açıklar.

**Bunu yapan uygulamalar yok mu?**
Sezon içi takip yapan çok uygulama var. Çok yıllık planı kurala, iklim riskine ve havza suyuna göre birlikte değerlendiren
bir örnek bulamadık. "İlk" demiyoruz.

**Kim para ödeyecek?**
Çiftçi ücretsiz kullanır. Kooperatif, şeker fabrikası, banka ve sigorta lisans öder. Henüz hiçbiriyle görüşmedik
(görüştüyseniz bu cümleyi değiştirin).

**Araç çiftçinin yerine mi karar veriyor?**
Hayır. Mevcut plan her zaman karşılaştırmada, her önerinin bilgi boşlukları ve yerel riskleri yazılı, her sayfanın altında
"kararın sahibi çiftçi ve yerel ziraat mühendisidir" notu var.

**Başka ülkede çalışır mı?**
Havza menüsünden Pencap'ı seçin; kural paketi ve para birimi değişir, motor aynı kalır. Diğer üç havzanın ekonomi ve
kural tabloları temsilidir.

## Söylenmeyecekler

"İlk", "sıfır risk", "ECOSTRESS ile doğruladık", "28 bin plan", "görüştük" (görüşmediyseniz), "2.500+ çökme yapısı".
