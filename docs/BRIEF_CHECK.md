# NASA brifi karşılama kontrolü (proje planı bölüm 2.7 → uygulama)

14 Kasım 2026'da uygulamanın her sayfası çalıştırılarak kontrol edildi. **Var** = ekranda görülüyor.
**Kısmen** = bir bölümü var, eksik yan yazıldı. **Bilerek yapılmadı** = kapsam dışı; sunumda sorulursa
söylenecek cümle yanında.

| NASA beklentisi | Durum | Uygulamada nerede / not |
|---|---|---|
| NASA yer gözlemleri + yerel veri | Kısmen | POWER, SMAP, HLS, MODIS, GPM IMERG, GRACE, NEX-GDDP-CMIP6, SRTM + SoilGrids için veri yolu hazır. Hangisinin gerçek, hangisinin sentetik olduğu kenar çubuğunda "N / 8 veri seti gerçek" diye yazar. **ECOSTRESS yok** (aşağıya bakın) |
| Mevcut rotasyon dahil en az 3 strateji | Var | Planlar: Mevcut plan + Kâr + Akifer + Denge, dört sütun |
| Neden / kanıt / fayda / bilgi boşluğu / yerel risk | Var | Her kartta "Neden bu plan?" (beş başlık), TR ve EN |
| Su kullanımı | Var | Sulama suyu m³/da (FAO-56) |
| Azot, organik madde, erozyon, zararlı döngüsü | Var | Toprak sağlığı alt skorları (dört çubuk) |
| Yem değeri | Var | Yem göstergesi (kg KM/da), yem alt sınırı ve yem önceliği |
| Pazar uygunluğu | Var | Sözleşme / alıcı yok / istenmeyen ürün kısıtları; Havza sayfasında fiyat tepkisi |
| Don, sıcak stresi, aşırı yağış, çıplak tarla | Var | İklim geçmişi: risk takvimi; Planlar: ürün takviminde hassas dönemler |
| Değişen koşullara dayanıklılık | Var | 41 dönemlik stres testi + 2040'lar (CMIP6 değişim katsayıları) |
| Yağış/sıcaklık senaryo kaydırıcıları | Var | Kenar çubuğu "Ya şöyle olursa?" (yağış −%40…+%20, sıcaklık −1…+4 °C) |
| Uzun dönem su eğilimleri | Var | Havza: GRACE su deposu serisi ve eğilim çizgisi |
| Belirsizlik ve yerel uzmanlık | Kısmen | Gelir dağılımı (kutu grafiği), güven noktaları, "yerel olarak incelenmesi gereken riskler". **Fiyat aralığıyla hassasiyet gösterimi yok**; fiyat belirsizliği yalnızca "Bilgi boşlukları"nda yazıyor |
| Terimleri açıklamak | Var | Yöntem ve veriler: sözlük (TR/EN) |
| Uydu ve yer ölçümü farkı | Kısmen | Açıklama + POWER ile IMERG yağış karşılaştırması var. **MGM istasyon verisi yok** (opsiyoneldi) |
| Verileri ortak ızgarada uyumlaştırmak | Kısmen | Ortak zaman adımı ve nokta çıkarımı var; ortak **ızgara** (raster) yok. Dürüst cümle: "Tarla noktası için her veriyi kendi hücresinden çekip günlük/aylık ortak adıma getiriyoruz" |
| SI veya istatistiksel yaklaşımlar | Var | Mann-Kendall eğilim testi + Sen eğimi. Karar yolunda dil modeli yok |
| Tarla düzeyi zafiyet haritası | Bilerek yapılmadı | Opsiyoneldi. Cümle: "Tarla içi harita HLS 30 m ile yol haritamızda; bugün tarlayı tek nokta olarak ele alıyoruz" |
| Çiftçinin kendi kısıtları | Var | Tarla: su, ekipman, sözleşme, alıcı, istenmeyen ürün, yem |
| Anlaşılırlık | Var | Planlar'ın üstünde tek cümlelik özet, üç kart, renkli rozet, sözlük, sunum modu |
| Çiftçinin yargısının yerini almamak | Var | Her sayfanın altındaki kalıcı not ve PDF karnedeki not |

## Planla uygulama arasındaki farklar (sunumda yanlış söylenmesin)

| Planda yazan | Gerçek durum | Ne yapılacak |
|---|---|---|
| "ECOSTRESS ile doğruladık" (plan 16, 20.3) | ECOSTRESS uygulamada **kullanılmıyor** | Bu cümleyi kurmayın. Doğrulama cümlesi: "ET0 hesabını FAO-56 kitabındaki örnekle doğruladık (3,88 / 3,9 mm/gün)" |
| "28 bin plan" / 8⁴ = 4.096 | Taranan plan 20.736 | "20 binden fazla plan" deyin |
| PuLP | SciPy `linprog` (HiGHS) | Sorulursa: aynı çözücü, farklı arayüz |
| Folium harita, haritaya tıklayarak tarla seçimi | Yok; pilot nokta menüsü ya da koordinat girişi | Demoda pilot noktaları kullanın |
| LLM ile açıklama, Telegram botu, Prithvi | Yok | Yol haritası |
| Tuzluluk uyarısı | Yok | Söylemeyin |
| "806 + 434 TL" buğday desteği | Eylül 2026'da 954 + 514 (514 türetilmiş) | Güncel rakamı kullanın (docs/VERIFICATION_LOG.md) |
| AFAD obruk noktaları haritası | Nokta verisi açık değil; harita yok, sayılar metin olarak var | Obruk **fotoğrafı** slaytta; harita vaat etmeyin |

## Bilinen sınırlar için karar (METHODS bölüm 10)

| Sınır | Karar | Sunumda |
|---|---|---|
| Yılda tek ana ürün | Düzeltilmeyecek | "Pencap'taki çeltik–buğday çift ürünü yol haritasında" |
| Yonca yıl yıl modelleniyor | Düzeltilmeyecek; öneri kartlarına girmiyor | Sorulursa söylenir |
| Fiyat oynaklığı stres testinde yok | Düzeltilmeyecek | "Stres testi hava riskini ölçer; fiyat riski havza katmanında" |
| Tarla içi farklılık yok | Düzeltilmeyecek | "İklim 0,5°, toprak tek değer; HLS 30 m yol haritasında" |
