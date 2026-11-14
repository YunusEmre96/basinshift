# Sunum paketi: pitch, video, gönderim

## 1. Üç dakikalık pitch metni

Köşeli parantezdeki sayıları demodan hemen önce ekrandan okuyup yazın.

**0:00 Problem.** "Konya Kapalı Havzası'nda 739 obruk kayıtlı. 2025'te yağış 244 milimetreydi. Yeraltı suyu 1980'lerden
beri yaklaşık 30 metre düştü. Aynı kriz Kaliforniya'da, Pencap'ta, Avustralya'da var. Çiftçi ise önümüzdeki dört yılı
hâlâ alışkanlıkla ve geçen yılın fiyatıyla planlıyor."

**0:25 Tarla.** "Mehmet Amca Çumra'da 120 dekar sulu arazi işliyor. 2025'te pancar, 2026'da mısır ekti; 2027'de yine
pancar düşünüyor. 2026'da yürürlüğe giren kurala göre bu plan kırmızı kart riski taşıyor: mısır, patates ve pancar dört
yılda en fazla iki kez ekilebiliyor ve art arda gelemiyor."

**0:40 Planlar.** "BasinShift 20 binden fazla dört yıllık planı son 40 yılın gerçek havasıyla tek tek sınadı ve kurala
uyanlardan üçünü seçti: Kâr, Akifer, Denge. Denge planı yılda dekar başına [ ] metreküp daha az su istiyor, [ ] lira
destek getiriyor ve kötü dönemde [ ] lira daha fazla kazandırıyor. Her kart nedenini, kanıtını, bilgi boşluğunu ve
yerelde kontrol edilmesi gereken riski yazıyor."

**1:30 Senaryo.** "Yağış yüzde yirmi azalırsa?" (kaydırıcı) "Kartlar yeniden hesaplandı. Hangi planın dayanıklı
kaldığını görüyorsunuz."

**1:45 İki gelecek.** "Aynı tarla, iki farklı 2027–2030: alışkanlıkla ekim ve BasinShift planı."

**2:05 Havza.** "Bir çiftçi için doğru olan, bin çiftçi yapınca obruk olabilir. Herkes geçen yılın fiyatına bakarsa
fiyatlar dalgalanır, su yine yetmez. Koordineli planla aradaki fark dekar başına [ ] lira ve [ ] metreküp. Bir metreküp
suyun havzaya değeri [ ] lira. Çiftlik tipleri temsilidir; mekanizmayı gösteriyoruz."

**2:25 İş modeli.** "Çiftçiye ücretsiz. Kooperatif, şeker fabrikası, banka ve sigorta öder. Donanım yok, veri açık."

**2:40 Dürüstlük ve kapanış.** "Sekiz veri setinden [ ] tanesi bugün gerçek NASA verisi; kalanı ekranda sentetik diye
işaretli. Fiyatların bir kısmı ve bütün maliyetler varsayım. Araç karar vermez, kararı aydınlatır. Bankalara stres
testi yapılıyor. Artık tarlalara da."

## 2. İki dakikalık video (İngilizce altyazı: `docs/VIDEO_SUBTITLES_EN.srt`)

Ekran kaydı: Windows'ta **Win + Alt + R** (Xbox Game Bar) ya da OBS. Uygulama tam ekran, Sunum modu açık, dil **English**
(global jüri için) ya da Türkçe + altyazı.

| Zaman | Ekran | Anlatım |
|---|---|---|
| 0:00–0:15 | Havza: GRACE grafiği | Problem |
| 0:15–0:30 | Havza menüsü: dört havza | Küresel |
| 0:30–0:45 | Tarla → örnek tarlayı yükle | Mehmet Amca |
| 0:45–1:15 | Planlar: özet, dört sütun, Neden bu plan? | Stres testi ve kartlar |
| 1:15–1:30 | Kaydırıcı −20 | Senaryo |
| 1:30–1:45 | Havza alt kısım | Koordinasyon, gölge fiyat |
| 1:45–2:00 | Karne PDF + Yöntem ve veriler | Dürüstlük ve kapanış |

Altyazı dosyasındaki köşeli parantezleri kayıttan önce doldurun. 60 saniyelik yedek demo kaydı: aynı akışın 0:30–1:30
arası, anlatımsız.

## 3. Slaytlar (en fazla 6)

1. Obruk fotoğrafı + dört rakam (kaynak dipnotuyla).
2. Tek cümle: "4 yıllık ekim planınızı 40 yılın havasıyla sınayın."
3. Canlı demo (slayt değil, uygulama).
4. Havza: koordinasyonsuzluğun bedeli + gölge fiyat (ekran görüntüsü).
5. Dürüstlük slaydı: veri seti × çözünürlük × gerçek/sentetik × ne için kullanılmaz (Yöntem tablosunun ekran görüntüsü).
6. İş modeli + yol haritası + kapanış cümlesi.

## 4. Gönderim kontrol listesi (son saat 15 Kasım 23:59; hedef 21:30)

- [ ] `veri_indir.bat` raporu okundu; kenar çubuğundaki "N / 8" sayısı not edildi.
- [ ] `yedek_al.bat` çalıştı; `dist/` altındaki zip USB'ye kopyalandı ve **başka bir bilgisayarda** açılıp denendi.
- [ ] Proje sayfası İngilizce; `docs/PROJECT_PAGE_EN.md` içindeki bütün köşeli parantezler dolduruldu.
- [ ] "Use of AI" bölümü etkinliğin kurallarına göre yazıldı.
- [ ] References alanında bütün veri, yöntem ve kütüphaneler var.
- [ ] Video 2 dakikayı aşmıyor, İngilizce altyazılı, bağlantısı herkese açık.
- [ ] Depo bağlantısı açık; depoda `.env`, token, şifre yok (`test.bat` içindeki test de kontrol ediyor).
- [ ] Sunum 3 kez kronometreyle prova edildi; `docs/QA_PREP.md` ile soru provası yapıldı.
- [ ] Mehmet Amca karnesinin PDF'i basıldı.
- [ ] Etkinlik kuralı: "ürünün kodu etkinlik sırasında yazılmalı". Etkinlikten önce hazırlanan kısımları yerel
      organizatöre sorun ve proje sayfasında açıkça belirtin.
