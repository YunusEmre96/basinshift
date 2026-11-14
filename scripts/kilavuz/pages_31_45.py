"""
BasinShift Kılavuzu: Sayfa 31 - 45
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

MEVCUT_DIR = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler"
IMG_04 = os.path.join(MEVCUT_DIR, "04_ekim_planlari_karsilastirma.png")
IMG_05 = os.path.join(MEVCUT_DIR, "05_ekim_planlari_neden_aciklamalari.png")
IMG_06 = os.path.join(MEVCUT_DIR, "06_ekim_planlari_pareto_analizi.png")
IMG_07 = os.path.join(MEVCUT_DIR, "07_iki_gelecek_dengeli_senaryo.png")
IMG_10 = os.path.join(MEVCUT_DIR, "10_havza_gorunumu_ve_anarsi_maliyeti.png")
IMG_11 = os.path.join(MEVCUT_DIR, "11_ciftci_karnesi_denge_raporu.png")
IMG_13 = os.path.join(MEVCUT_DIR, "13_yontem_ve_veri_kaynaklari.png")


def render_pages_31_45(pdf):
    # =========================================================================
    # SAYFA 31: BÖLÜM 08 - 8.3 İKLİM GEÇMİŞİ: NDVI VE TOPRAK SU AÇIĞI
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.3 NDVI ve Toprak Su Açığı")
    pdf.section_title("8.3 İklim Geçmişi: HLS/MODIS NDVI ve Toprak Su Dengesi")
    pdf.body(
        "İklim Geçmişi sayfasının alt panelinde, uydu tabanlı bitki örtüsü yeşillenme endeksi (NDVI) ve toprak su açığı yer alır:"
    )
    pdf.bullet("Harmonized Landsat-Sentinel (HLS) 30m NDVI Zaman Serisi:", "Parselin geçmiş yıllardaki bitki gelişim eğrisini "
               "5 günlük aralıklarla takip eder. Bitkinin ne zaman kardeşlendiği, ne zaman başak bağladığı ve ne zaman sarardığı "
               "uydu spektral yansımasıyla doğrulanır.")
    pdf.bullet("Kümülâtif Toprak Su Açığı (Deficit) Eğrisi:", "Yıl boyunca yağışın yetersiz kaldığı ve sulamanın zorunlu olduğu "
               "kritik fenolojik pencereleri gösterir. Çumra parselinde su açığının Haziran-Ağustos döneminde tepe yaptığı net şekilde görülür.")
    pdf.bullet("Tarihsel Kuraklık Yılları Karşılaştırması:", "1994, 2007, 2014 ve 2021 büyük Konya kuraklıklarının tarlaya etkisi kıyaslanır.")

    # =========================================================================
    # SAYFA 32: BÖLÜM 08 - 8.4 PLANLAR: CEVABI GÖRMEK VE KARTLAR
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.4 Planlar: Karar Kartları")
    pdf.section_title("8.4 Planlar: Cevabı Görmek ve Karar Kartları")
    pdf.body(
        "Planlar sayfası, BasinShift'in en can alıcı sonuç ekranıdır. Çiftçinin mevcut alışkanlığı ile sistemin önerdiği "
        "üç stratejik kart yan yana listelenir:"
    )
    pdf.bullet("Mevcut Planınız (Alışkanlık):", "Kırmızı kart uyarısıyla gösterilir. Yıllık su tüketimi 700+ m³/da, 2026 desteği 0 ₺/da, "
               "kurak yılda batma riski çok yüksektir.")
    pdf.bullet("Denge Kartı (Önerilen - En Yüksek Sharpe Oranı):", "Örnek: Fiğ -> Ekmeklik Buğday -> Nohut -> Yağlık Ayçiçeği. "
               "Yıllık su tüketimi ~340 m³/da'ya iner, devlet desteği 1.468–1.541 ₺/da'ya çıkar, kurak yılda bile garanti nakit akışı sağlar.")
    pdf.bullet("Kâr Kartı (Maksimum Kazanç):", "Yasal kural sınırları dahilinde en yüksek ortalama brüt geliri üreten plan.")
    pdf.bullet("Akifer Kartı (Maksimum Su Tasarrufu):", "Suyu minimum tüketen (nadas, aspir, nohut ağırlıklı) ve kuyu seviyesini koruyan plan.")

    if os.path.exists(IMG_04):
        pdf.figure(IMG_04, "Planlar Sayfası: Mevcut Alışkanlık vs Denge, Kâr ve Akifer Stratejik Karar Kartları", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 33: BÖLÜM 08 - 8.4 PLANLAR: KARTLARIN DERİN ANALİZİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.4 Planlar: Kartların Derin Analizi")
    pdf.section_title("Karar Kartlarının Sayısal Karşılaştırması (Çumra Parseli)")
    pdf.body(
        "Mehmet Amca'nın Çumra parseli için 44 yıllık NASA iklim simülasyonu sonuçlarının özet tablosu:"
    )
    
    headers = ["Stratejik Kart", "4 Yıllık Rotasyon Sırası", "Yıllık Su (m³/da)", "Ort. Kâr (₺/da/yıl)", "Kötü Dönem CVaR", "2026 Destek Durumu"]
    rows = [
        ["Mevcut Planınız", "Mısır - Pancar - Mısır - Pancar", "720 m³", "4.850 ₺", "1.200 ₺ (İflas Riski)", "KIRMIZI KART (0 ₺ Destek)"],
        ["Denge Kartı (Önerilen)", "Fiğ - Buğday - Nohut - Ayçiçeği", "340 m³ (-%53)", "6.420 ₺ (+%32)", "4.150 ₺ (Çok Güvenli)", "1.468–1.541 ₺/da TAM HİBE"],
        ["Kâr Kartı", "Buğday - Pancar - Nohut - Ayçiçeği", "480 m³ (-%33)", "7.150 ₺ (+%47)", "3.600 ₺ (Orta Risk)", "Yasal Sınırda Destekli"],
        ["Akifer Kartı", "Nadas - Buğday - Nohut - Aspir", "180 m³ (-%75)", "4.200 ₺ (-%13)", "3.850 ₺ (Sıfır Risk)", "1.028–1.468 ₺/da Destekli"]
    ]
    pdf.table(headers, rows, [32, 45, 26, 26, 26, 23], ["L", "L", "C", "C", "C", "L"])
    
    pdf.callout(
        "DENGE KARTININ SIRRI: HEM YÜKSEK KÂR HEM DÜŞÜK SU",
        "Çiftçiler genellikle 'daha az su tüketirsem daha az kazanırım' yanılgısına düşer. Oysa Denge Kartı, "
        "kırmızı kart cezasından kurtulup 1.468 ₺ buğday ve 1.541 ₺ ayçiçeği su kısıtı hibelerini aldığı ve kuyu elektrik faturasını "
        "yarıya indirdiği için hem mevcut plandan %32 daha fazla net kâr bırakmakta hem de kuyudan %53 daha az su çekmektedir!",
        "verified"
    )

    # =========================================================================
    # SAYFA 34: BÖLÜM 08 - 8.4 PLANLAR: NEDEN BU PLAN? GEREKÇELERİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.4 Neden Bu Plan? Gerekçeleri")
    pdf.section_title("Deterministik Neden Açıklamaları ve Yıllık Akış")
    pdf.body(
        "Her kartın altında yer alan 'Neden bu plan?' butonu tıklandığında, sistemin agronomik gerekçelendirme motoru çalışır:"
    )
    pdf.bullet("1. Yıl (Fiğ):", "Toprağa kökleriyle organik azot depolar. Yaz sıcağında toprak çıplak kalmaz, kök nematod döngüsü kırılır.")
    pdf.bullet("2. Yıl (Ekmeklik Buğday):", "Önceki yılın fiğ azotundan faydalanarak gübre maliyetini düşürür; 1.468 ₺/da devlet desteği alır.")
    pdf.bullet("3. Yıl (Nohut):", "Sıfır ek sulama ihtiyacıyla kurak yaz aylarında kuyuya nefes aldırır; yüksek piyasa fiyatıyla nakit getirir.")
    pdf.bullet("4. Yıl (Yağlık Ayçiçeği):", "Derin kökleriyle taban suyunu kullanır; 1.541 ₺/da rekor destekle döngüyü taçlandırır.")

    if os.path.exists(IMG_05):
        pdf.figure(IMG_05, "Planlar Sayfası Alt Kısım: Yıllık Su Tüketimi Dağılımı ve Deterministik Neden Açıklamaları", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 35: BÖLÜM 08 - 8.4 PLANLAR: MÜHENDİS GÖRÜNÜMÜ VE PARETO
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.4 Mühendis Görünümü ve Pareto")
    pdf.section_title("Mühendis Görünümü ve 20.736 Planın Pareto Saçılımı")
    pdf.body(
        "Sayfanın altındaki 'Mühendis Görünümünü Aç' kutusu işaretlendiğinde, taranan 20.736 planın tamamını içeren interaktif "
        "Plotly saçılım grafiği devreye girer. Ziraat mühendisleri ve araştırmacılar tüm geçerli planları filtreleyebilir:"
    )
    pdf.bullet("X Ekseni:", "Yıllık ortalama çekilen sulama suyu (m³/da/yıl).")
    pdf.bullet("Y Ekseni:", "Yıllık ortalama brüt kâr (₺/da/yıl).")
    pdf.bullet("Renk Skalası:", "Kötü dönem geliri (CVaR - dayanıklılık). Kırmızı noktalar kuraklıkta batanları, sarı/yeşil noktalar güvenlileri gösterir.")
    pdf.bullet("Optimal Pareto Eğrisi:", "Grafiğin sol-üst kenarını oluşturan en verimli planlar hattıdır.")

    if os.path.exists(IMG_06):
        pdf.figure(IMG_06, "20.736 Planın Çok Boyutlu Pareto Saçılım Grafiği (Mühendis Görünümü)", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 36: BÖLÜM 08 - 8.5 İKİ GELECEK: 2027–2030 DİNAMİK SİMÜLASYON
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.5 İki Gelecek")
    pdf.chapter_title(
        "8.5",
        "İki Gelecek: Aynı Tarla, İki Farklı 2027–2030",
        "Alışılagelmiş ekim tercihleri ile BasinShift planının 4 yıllık dinamik simülasyonu ve kuyu seviyesi projeksiyonu."
    )
    
    pdf.section_title("Zaman Makinesi: Alışkanlık vs Bilimsel Dönüşüm")
    pdf.body(
        "İki Gelecek ekranı, çiftçiye önündeki 4 yılı yan yana karşılaştırır. Solda alışılmış ekim (kırmızı kartlı mısır-pancar), "
        "sağda ise önerilen BasinShift Denge planı simüle edilir. 4 yılın sonunda üç büyük sayı özetlenir:"
    )
    pdf.bullet("4 Yılda Su Farkı (−1.600 m³/da):", "Kuyudan tam 1.600 ton daha az su çekilir; akiferin tükenmesi yavaşlatılır.")
    pdf.bullet("4 Yılda Destek Farkı (+4.108 ₺/da):", "Kırmızı kart cezasından kurtulup yasal destekler cebe girer.")
    pdf.bullet("Kuyu Statik Su Seviyesi Farkı:", "Alışılmış planda kuyu her yıl 1 metre daha derine inerken, Denge planında durulur.")

    if os.path.exists(IMG_07):
        pdf.figure(IMG_07, "İki Gelecek Ekranı: Alışılmış Plan vs BasinShift Planının 2027–2030 Karşılaştırması", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 37: BÖLÜM 08 - 8.6 HAVZA: GRACE VE 739 OBRUK
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.6 Havza: GRACE ve Obruklar")
    pdf.chapter_title(
        "8.6",
        "Havza: Bin Çiftçi Aynı Şeyi Yaparsa",
        "Tek tarlanın sınırlarını aşarak Konya Kapalı Havzası'nın tamamına bakan makro hidrolojik göstergeler."
    )
    
    pdf.section_title("NASA GRACE Mascon Akifer Erimesi ve 739 Obruk")
    pdf.body(
        "Havza sayfası, havzanın yeraltı suyu bilançosunu gözler önüne serer:"
    )
    pdf.bullet("NASA GRACE / GRACE-FO Yeraltı Suyu Anomalisi:", "2002–2024 yılları arasında akifer kütlesindeki erimeyi belgeler. "
               "Uzun vadeli eğilim yılda −1,3 cm eşdeğer su kalınlığı kaybıdır.")
    pdf.bullet("739 Obruk Yoğunluk Haritası:", "Aşırı su çekilen Çumra, Karapınar ve Karatay bölgelerinde yoğunlaşan obrukların "
               "jeolojik dağılımını gösterir; plansız su tüketiminin fiziksel çöküşünü kanıtlar.")

    if os.path.exists(IMG_10):
        pdf.figure(IMG_10, "Havza Görünümü: GRACE Akifer Kütle Kaybı, 739 Obruk ve Koordinasyonsuzluk Bedeli", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 38: BÖLÜM 08 - 8.6 HAVZA: ANARŞİ MALİYETİ VE GÖLGE FİYAT
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.6 Havza: Anarşi Maliyeti")
    pdf.section_title("İki Anahtar Sayı: Koordinasyonsuzluk Bedeli ve Gölge Fiyat")
    pdf.body(
        "Havza sayfasının altındaki analitik paneller, karar vericilere yönelik iki devasa ekonomik gösterge sunar:"
    )
    
    pdf.callout(
        "KOORDİNASYONSUZLUĞUN HAVZAYA MALİYETİ (PRICE OF ANARCHY)",
        "Her çiftçi geçen yılın yüksek fiyatına aldanarak tek başına mısır ve pancar ektiğinde; havza genelinde koordineli "
        "bir ürün desenine kıyasla dekar başına yılda 929 ₺ kazanç ve 149 m³ su kaybolmaktadır. "
        "BasinShift havza planlaması ile bu kaynak israfı tamamen önlenebilmektedir.",
        "danger"
    )
    
    pdf.callout(
        "SUYUN GÖLGE FİYATI: 8,39 ₺ / m³",
        "Su bütçesine eklenecek veya tasarruf edilecek her 1 m³ suyun havza ekonomisine net marjinal katkısı 8,39 ₺'dir. "
        "Sulama kooperatifleri ve DSİ için kapalı borulu sistem yatırımlarının geri dönüş fizibilitesi bu sayı üzerinden hesaplanır.",
        "verified"
    )

    # =========================================================================
    # SAYFA 39: BÖLÜM 08 - 8.7 KARNE: TEK SAYFALIK RİSK VE SU KARNESİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.7 Karne: Risk ve Su Karnesi")
    pdf.section_title("8.7 Karne: Tek Sayfalık Resmi Risk ve Su Karnesi")
    pdf.body(
        "Karne sayfası, çiftçinin cebine ve dosyasına girecek resmi çıktıdır. İstenilen plan seçilip (Denge, Kâr, Akifer veya Mevcut), "
        "çiftçi/işletme adı ve tarla alanı girildikten sonra 'Karneyi İndir (PDF)' butonuna basıldığında yüksek çözünürlüklü A4 belge üretilir:"
    )
    pdf.bullet("Kurumsal Kullanım:", "Ziraat Bankası tarımsal kredi faiz indirimi, TARSİM kuraklık sigortası aktüeryal primi veya "
               "şeker fabrikası sözleşmeli ekim kotası için resmi referans belgesidir.")
    pdf.bullet("İçerik:", "Parsel bilgileri, 4 yıllık ürün deseni, su tüketim karnesi, CVaR risk skoru ve Eylül 2026 destek onay mührü.")

    if os.path.exists(IMG_11):
        pdf.figure(IMG_11, "Karne Sayfası: Tek Sayfalık Çiftçi Risk ve Su Karnesi Önizleme Ekranı", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 40: BÖLÜM 08 - 8.8 YÖNTEM VE VERİLER
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.8 Yöntem ve Veriler")
    pdf.section_title("8.8 Yöntem ve Veriler: Canlı Doğrulama ve Sözlük")
    pdf.body(
        "Yöntem ve Veriler sayfası, sistemin bilimsel dürüstlük ve şeffaflık merkezidir:"
    )
    pdf.bullet("8/8 Gerçek Veri Doğrulama Tablosu:", "Sistemdeki tüm NASA ve küresel veri setlerinin canlı durumunu sergiler. "
               "Her satırda yeşil onay rozeti yer alır.")
    pdf.bullet("Model Varsayımları ve Formül Detayları:", "FAO-56 Penman-Monteith, Stewart verim denklemleri ve toprak parametrelerinin "
               "matematiksel açıklamalarını barındırır.")
    pdf.bullet("İki Dilli (TR / EN) Terimler Sözlüğü:", "Uygulamadaki tüm teknik kavramların açıklamalarını içerir.")

    if os.path.exists(IMG_13):
        pdf.figure(IMG_13, "Yöntem ve Veriler Sayfası: Canlı 8/8 Veri Seti Doğrulama Tablosu ve Sözlük", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 41: BÖLÜM 09 - SENARYO A: MEHMET AMCA ÇUMRA
    # =========================================================================
    pdf.add_exact_page("Bölüm 09 · Senaryo A: Mehmet Amca Çumra")
    pdf.chapter_title(
        "09",
        "Adım Adım Kullanım: 3 Senaryo",
        "Uygulamayı ilk kez açan birinin izleyebileceği üç gerçekçi kullanım senaryosu."
    )
    
    pdf.section_title("Senaryo A · Çumra'da Mısır-Pancar Eken Mehmet Amca")
    pdf.body(
        "Mehmet Amca, Çumra havzasında 100 dekarlık sulu arazisinde yıllardır iki yıl dane mısır, iki yıl şeker pancarı ekmektedir. "
        "Kuyu derinliği 80 metreye inmiş, elektrik faturaları katlanmış ve Eylül 2026 kararnamesiyle mısırına su kısıtı desteği sıfırlanmıştır."
    )
    pdf.bullet("Adım 1:", "Uygulama açılır, Tarla sayfasında 'Örnek tarlayı yükle: Mehmet Amca, Çumra' sarı butonuna tıklanır. Tüm veriler yüklenir.")
    pdf.bullet("Adım 2:", "Doğrudan 'Planlar' sayfasına geçilir. Mevcut planının üzerinde büyük kırmızı 'Kırmızı Kart (ÇKS Destek İhlali)' uyarısını görür.")
    pdf.bullet("Adım 3:", "Hemen yanındaki yeşil 'Denge Kartı'na bakar: 1. Yıl Fiğ, 2. Yıl Buğday, 3. Yıl Nohut, 4. Yıl Ayçiçeği. 4 yılda kuyusundan "
               "1.600 ton daha az su çekeceğini ve tam 4.108 ₺/da devlet desteği kazanacağını hesaplar.")
    pdf.bullet("Adım 4:", "'Karne' sayfasına geçer, resmi Risk ve Su Karnesini PDF olarak indirir ve bankaya düşük faizli sulama kredisi için başvurur.")

    # =========================================================================
    # SAYFA 42: BÖLÜM 09 - SENARYO B: KARAPINAR ÇİFTÇİSİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 09 · Senaryo B: Karapınar Çiftçisi")
    pdf.section_title("Senaryo B · Kendi Tarlasını Giren Karapınar Çiftçisi")
    pdf.body(
        "Karapınar'da obruk riski yüksek bölgede kumlu-tınlı toprağı olan bir üretici, kendi parsel koordinatını girer (37.71° K, 33.55° D). "
        "Toprak analizi SoilGrids'ten otomatik çekilir; kuyu debisinin düşük olduğunu (15 m³/saat) belirtir."
    )
    pdf.bullet("Adım 1:", "Kendi koordinatını girip kuyu debisini ve salma sulamadan damla sulamaya geçiş opsiyonunu işaretler.")
    pdf.bullet("Adım 2:", "'İklim Geçmişi'nde bölgenin Temmuz ayında ortalama 14 gün >35°C sıcaklık stresine maruz kaldığını görür.")
    pdf.bullet("Adım 3:", "Planlar sayfasında sistem ona sıcağa ve kireçli toprağa çok dayanıklı olan Aspir ve Nohut ağırlıklı Akifer Kartını önerir. "
               "Sıfır kuyu riskiyle net gelirini garanti altına alır.")
    pdf.bullet("Adım 4:", "Düşük su tüketimli planla kuyu pompaj masrafını %70 azaltır ve erozyon riskini sıfırlar.")

    # =========================================================================
    # SAYFA 43: BÖLÜM 09 - SENARYO C: 2040 İKLİM DEĞİŞİMİ PROJEKSİYONU
    # =========================================================================
    pdf.add_exact_page("Bölüm 09 · Senaryo C: 2040 İklim Projeksiyonu")
    pdf.section_title("Senaryo C · 'Ya İklim Değişirse?': 2040 Projeksiyonu")
    pdf.body(
        "Tarım Kredi Kooperatifi uzmanı, sol kenar çubuğundan 'Ya şöyle olursa?' ayarını açar ve iklimi 'NASA CMIP6 SSP5-8.5 (Aşırı Kuraklık)' "
        "moduna alır (+2.5°C sıcaklık artışı, %20 yağış azalışı). Sistem saniyeler içinde 20.736 planı 2040 ikliminde yeniden sınar:"
    )
    pdf.bullet("Mevcut Planın Çöküşü:", "Şeker pancarı ve mısır aşırı sıcaklıktan dolayı tepe döllenmesini yapamaz, verim %40 düşer ve zarar eder.")
    pdf.bullet("Denge Planının Direnci:", "Ayçiçeği ve arpa derin kökleri ve kuraklık toleransıyla ayakta kalır, çiftçiyi iflastan korur.")
    pdf.bullet("Jüriye Sunum:", "İklim değişikliği altında tarımsal uyumun (Field Shift) somut kanıtı olarak sunulur.")

    # =========================================================================
    # SAYFA 44: BÖLÜM 10 - KODUN YAPISI VE KATMANLAR
    # =========================================================================
    pdf.add_exact_page("Bölüm 10 · Kodun Yapısı ve Katmanlar")
    pdf.chapter_title(
        "10",
        "Kodun Yapısı ve Mimarisi",
        "Kodu okumadan veya geliştirmeden önce bilinmesi gereken modüler yazılım mimarisi ve katmanlar."
    )
    
    pdf.section_title("Modüler Klasör Mimarisi")
    pdf.body(
        "BasinShift, kurumsal yazılım standartlarına uygun olarak katmanlı bir mimaride geliştirilmiştir:"
    )
    
    headers = ["Klasör / Dosya Yolu", "Katman", "Sorumluluk ve İçerik"]
    rows = [
        ["app.py", "Giriş Noktası", "Streamlit uygulamasını başlatır, 7 sayfalık sekmeleri ve kenar çubuğunu kurar."],
        ["basinshift/core/water.py", "Çekirdek Motor", "FAO-56 Penman-Monteith ET0, TAW, RAW, günlük toprak su dengesi diferansiyel denklemleri."],
        ["basinshift/core/yield_model.py", "Çekirdek Motor", "FAO Stewart Ky verim azalışı, sıcaklık/don iklim stres cezaları, maliyet ve brüt kâr."],
        ["basinshift/core/rotation.py", "Çekirdek Motor", "20.736 planın üretimi, ön bitki matrisi, 4 yıllık kayan pencere stres testi."],
        ["basinshift/core/pareto.py", "Optimizasyon", "3 Boyutlu Pareto etkinlik sınırı, baskınlık filtreleri, Sharpe oranı seçimi."],
        ["basinshift/knowledge/tables.py", "Bilgi Tabanı", "crops.yaml, rules.yaml, September 2026 destek katsayıları ve commodity_trade.csv yükleyicisi."],
        ["basinshift/ui/pages.py", "Arayüz Katmanı", "7 sayfanın görsel bileşenleri, Plotly grafikleri, metrik kartları ve Space Apps teması."],
        ["basinshift/ui/state.py", "Durum Yönetimi", "PERSISTENT_WIDGETS mekanizması, sayfa geçişlerinde veri kaybını önleyen oturum yöneticisi."],
        ["data/konya/...", "Veri Deposu", "NASA POWER, GPM, GRACE, SMAP, SRTM, CMIP6 ve SoilGrids NetCDF / CSV dosyaları."]
    ]
    pdf.table(headers, rows, [45, 30, 103], ["L", "L", "L"])

    # =========================================================================
    # SAYFA 45: BÖLÜM 10 - UI STATE VE BİR TIKLAMADA NE OLUYOR?
    # =========================================================================
    pdf.add_exact_page("Bölüm 10 · UI State Yönetimi")
    pdf.section_title("UI State Yönetimi ve Bir Tıklamada Ne Oluyor?")
    pdf.body(
        "Streamlit mimarisinde her kullanıcı etkileşiminde script baştan sona yeniden çalıştırılır. "
        "BasinShift'in performansını ve kararlılığını garanti altına alan iki hayati mekanizma vardır:"
    )
    pdf.bullet("PERSISTENT_WIDGETS Mekanizması (`basinshift/ui/state.py`):", "Sayfalar arasında gezinirken (ör. Tarla'dan Planlar'a geçerken) "
               "Streamlit'in bileşen state'lerini unutup `KeyError` vermesini engelleyen kalıcı oturum koruyucusu. `lang`, `basin_id`, "
               "`site_id`, `unit` gibi anahtar değişkenler asla kaybolmaz.")
               
    pdf.bullet("@st.cache_data ile Anlık Yanıt Süresi:", "Ham NASA verileri diskten bir kez okunur ve bellekte önbelleklenir. "
               "Kullanıcı parametre değiştirdiğinde 20.736 planın taranması ve Pareto optimizasyonu yalnızca 0,2 saniyede tamamlanır.")
               
    pdf.bullet("Deterministik Mimari:", "Aynı girdi parametreleri her zaman aynı kesin sonuçları üretir; hiçbir rassal sapma veya "
               "halüsinasyon barındırmaz.")
