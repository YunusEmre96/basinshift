"""
BasinShift Kılavuzu - Kısım 3: Bölüm 8, 9, 10, 11
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

MEVCUT_DIR = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler"
IMG_01 = os.path.join(MEVCUT_DIR, "01_tarla_girisi_ve_yapilandirma.png")
IMG_03 = os.path.join(MEVCUT_DIR, "03_iklim_gecmisi_ve_risk_analizi.png")
IMG_04 = os.path.join(MEVCUT_DIR, "04_ekim_planlari_karsilastirma.png")
IMG_05 = os.path.join(MEVCUT_DIR, "05_ekim_planlari_neden_aciklamalari.png")
IMG_06 = os.path.join(MEVCUT_DIR, "06_ekim_planlari_pareto_analizi.png")
IMG_07 = os.path.join(MEVCUT_DIR, "07_iki_gelecek_dengeli_senaryo.png")
IMG_10 = os.path.join(MEVCUT_DIR, "10_havza_gorunumu_ve_anarsi_maliyeti.png")
IMG_11 = os.path.join(MEVCUT_DIR, "11_ciftci_karnesi_denge_raporu.png")
IMG_13 = os.path.join(MEVCUT_DIR, "13_yontem_ve_veri_kaynaklari.png")


def build_chapter_08(pdf):
    pdf.chapter_header(
        "08",
        "Arayüz Turu: Her Ekran, Her Grafik",
        "Resmi NASA Space Apps 2026 koyu tasarım temasıyla güncellenen arayüzün tüm bileşenleri ve kullanım rehberi."
    )
    
    # 8.1 Kenar Çubuğu
    pdf.section_header("8.1 Kenar Çubuğu (Sidebar): Genel Yapılandırma")
    pdf.body_p(
        "Kenar çubuğu, uygulamanın hangi sayfasına gidilirse gidilsin sol tarafta sabit kalan kontrol merkezidir:"
    )
    pdf.bullet("Resmi NASA Space Apps 2026 Logosu:", "En üstte yer alır; organizasyon kimliğini doğrular.")
    pdf.bullet("Havza Seçimi:", "Konya Kapalı Havzası (Türkiye), Pencap (Hindistan), California Central Valley (ABD).")
    pdf.bullet("Dil Seçimi (TR / EN):", "Tek tıkla tüm arayüz, tablolar, grafikler ve terimler Türkçe veya İngilizceye döner.")
    pdf.bullet("Birim Seçimi (da / ha):", "Türkiye için dekar (da), uluslararası kullanıcılar için hektar (ha) bazlı hesaplama.")
    pdf.bullet("İklim Değişimi Simülatörü ('Ya şöyle olursa?'):", "2040 SSP2-4.5 (Orta İklim) ve SSP5-8.5 (Aşırı Kuraklık) senaryoları.")
    
    # 8.2 Tarla Sayfası
    pdf.section_header("8.2 Tarla Sayfası: Soruyu Sormak ve Yapılandırma")
    pdf.body_p(
        "Tarla sayfası, analizin başladığı ilk ekrandır. Çiftçi veya danışman tarlanın temel parametrelerini burada belirler:"
    )
    pdf.bullet("Hazır Demo Yükleme Butonu ('Örnek tarlayı yükle: Mehmet Amca, Çumra'):", "Tek tıkla Çumra havzasındaki gerçek bir parselin "
               "koordinatını, tınlı-killi toprak yapısını, 80m derin kuyu bilgisini ve alışılagelmiş 4 yıllık mısır-pancar ekim planını yükler.")
    pdf.bullet("Parsel ve Sulama Parametreleri:", "Tarla büyüklüğü (da), statik su seviyesi (m), sulama altyapısı (Damla %90, Yağmurlama %75, Salma %50), "
               "kuyu pompa debisi ve çiftlik tipi (Aile işletmesi, ticari tarım, hayvancılık odaklı vb.).")
    pdf.bullet("Mevcut 4 Yıllık Plan:", "Çiftçinin son yıllarda uyguladığı geleneksel sıralama (ör. Dane Mısır -> Şeker Pancarı -> Dane Mısır -> Şeker Pancarı).")

    if os.path.exists(IMG_01):
        pdf.figure(IMG_01, "Tarla Sayfası: Koordinat, Toprak Tipi, Kuyu Derinliği ve Mevcut Ekim Alışkanlığı Girişi", max_h=62, max_w=165)

    # 8.3 İklim Geçmişi
    pdf.section_header("8.3 İklim Geçmişi: Tarlanın 44 Yıllık NASA Karnesi")
    pdf.body_p(
        "İklim Geçmişi sayfası, NASA POWER Agroclimatology ve GPM IMERG verilerinden üretilen 1981–2025 tarihsel iklim analizidir:"
    )
    pdf.bullet("Yıllık Yağış ve Sıcaklık Anomalisi Grafiği:", "Son 44 yılın yağış dalgalanmalarını, kurak geçen yılları (ör. 2007, 2014, 2021) "
               "ve uzun dönemli ısınma trendini (+1.4°C artış) gösterir.")
    pdf.bullet("Aylık İklim Stres Takvimi (Heatmap):", "12 ay boyunca don riski günleri, aşırı sıcak gün sayısı (>35°C) ve hasat dönemi "
               "istenmeyen aşırı yağış frekansını matris formatında sergiler. Çiftçi hangi ayda bitkisinin ne tür risk altında olduğunu anlar.")

    if os.path.exists(IMG_03):
        pdf.figure(IMG_03, "İklim Geçmişi Sayfası: 44 Yıllık Sıcaklık/Yağış Trendi ve Aylık İklim Stresi Risk Takvimi", max_h=58, max_w=165)

    # 8.4 Planlar
    pdf.section_header("8.4 Planlar: Cevabı Görmek, Stratejik Kartlar ve Pareto Analizi")
    pdf.body_p(
        "Planlar sayfası, BasinShift'in kalbidir. 20.736 olası plan taranır; kural dışı olanlar elendikten sonra çiftçinin önüne "
        "mevcut planı ile üç öneri kartı yan yana konur:"
    )
    pdf.bullet("Mevcut Planınız (Alışkanlık):", "Kırmızı kart uyarısıyla gösterilir. Yıllık su tüketimi 700+ m³/da, 2026 desteği 0 ₺/da, "
               "kurak yılda batma riski çok yüksektir.")
    pdf.bullet("Denge Kartı (Önerilen - En Yüksek Sharpe Oranı):", "Örnek: Fiğ -> Ekmeklik Buğday -> Nohut -> Yağlık Ayçiçeği. "
               "Yıllık su tüketimi ~340 m³/da'ya iner, devlet desteği 1.468–1.541 ₺/da'ya çıkar, kurak yılda bile garanti nakit akışı sağlar.")
    pdf.bullet("Kâr Kartı (Maksimum Kazanç):", "Yasal kural sınırları dahilinde en yüksek ortalama brüt geliri üreten plan.")
    pdf.bullet("Akifer Kartı (Maksimum Su Tasarrufu):", "Suyu minimum tüketen (nadas, aspir, nohut ağırlıklı) ve kuyu seviyesini koruyan plan.")

    if os.path.exists(IMG_04):
        pdf.figure(IMG_04, "Planlar Sayfası: Mevcut Alışkanlık vs Denge, Kâr ve Akifer Stratejik Karar Kartları", max_h=55, max_w=165)
        
    pdf.body_p(
        "Sayfanın alt kısmında 'Neden bu plan?' gerekçeleri ve 20.736 planın tamamını gösteren interaktif Plotly Pareto Saçılım Grafiği yer alır. "
        "Mühendis görünümü açıldığında tüm geçerli planlar filtrelenebilir ve sıralanabilir."
    )

    if os.path.exists(IMG_05):
        pdf.figure(IMG_05, "Deterministik Neden Açıklamaları: Ön Bitki Katkısı, Su Tasarrufu ve Yasal Destek Analizi", max_h=55, max_w=165)
    if os.path.exists(IMG_06):
        pdf.figure(IMG_06, "3 Boyutlu Pareto Etkinlik Sınırı: Kâr, Su Tüketimi ve CVaR Riski Dağılımı", max_h=55, max_w=165)

    # 8.5 İki Gelecek
    pdf.section_header("8.5 İki Gelecek: 2027–2030 Karşılaştırmalı Dinamik Simülasyon")
    pdf.body_p(
        "İki Gelecek sayfası, çiftçiye geleceğini gösteren bir zaman makinesidir. Solda alışılagelmiş ekim tercihi (kırmızı kartlı mısır-pancar), "
        "sağda ise BasinShift Denge planı simüle edilir. 4 yılın sonunda üç çarpıcı fark özetlenir:"
    )
    pdf.bullet("4 Yılda Su Farkı:", "−1.600 m³/da su tasarrufu (Kuyudan 1.600 ton daha az su çekilir).")
    pdf.bullet("4 Yılda Destek Farkı:", "+4.108 ₺/da ilave devlet desteği (Kırmızı karttan kurtulup yasal su kısıtı hibelerini almak).")
    pdf.bullet("Kuyu Statik Seviyesi:", "Alışılmış planda kuyu 4 metre daha derine düşerken, Denge planında düşüş durur.")

    if os.path.exists(IMG_07):
        pdf.figure(IMG_07, "İki Gelecek Sayfası: Alışılmış Plan vs BasinShift Planının 2027–2030 Dinamik Karşılaştırması", max_h=55, max_w=165)

    # 8.6 Havza
    pdf.section_header("8.6 Havza: GRACE Yeraltı Suyu, 739 Obruk ve Anarşi Maliyeti")
    pdf.body_p(
        "Havza sayfası, tek bir tarlanın sınırlarını aşarak Konya Kapalı Havzası'nın tamamına bakar:"
    )
    pdf.bullet("NASA GRACE / GRACE-FO Mascon Grafiği:", "2002–2024 yılları arasında havzanın yeraltı su kütlesindeki net erimeyi sergiler. "
               "Eğilim yılda −1,3 cm eşdeğer su kalınlığı kaybıdır.")
    pdf.bullet("739 Obruk Haritası:", "Havzadaki obrukların yoğunluk dağılımını gösterir; aşırı su çekiminin fiziksel çöküşünü belgeler.")
    pdf.bullet("Koordinasyonsuzluğun Maliyeti (Price of Anarchy):", "Herkes tek başına mısır ekerse havza dekara yılda 929 ₺ gelir ve "
               "149 m³ su kaybeder. Koordineli ekim deseni bu israfı önler.")
    pdf.bullet("Suyun Gölge Fiyatı (Shadow Price):", "8,39 ₺/m³; havzada tasarruf edilen her metreküp suyun sisteme net ekonomik katkısıdır.")

    if os.path.exists(IMG_10):
        pdf.figure(IMG_10, "Havza Görünümü: GRACE Akifer Kütle Kaybı, 739 Obruk ve Koordinasyonsuzluk Maliyeti", max_h=55, max_w=165)

    # 8.7 Karne ve Yöntem Sayfaları
    pdf.section_header("8.7 Karne ve Yöntem Sayfaları")
    pdf.body_p(
        "Karne sayfası, çiftçinin bankaya (kredi için), sigortaya (TARSİM için) veya kooperatife sunabileceği resmi tek sayfalık "
        "'Risk ve Su Karnesi' üretir. İstenilen plan seçilip 'Karneyi İndir (PDF)' butonuna basıldığında yüksek çözünürlüklü belge indirilir."
    )
    pdf.body_p(
        "Yöntem ve Veriler sayfası ise bilimsel şeffaflık panelidir: 8/8 gerçek NASA verisinin canlı bağlantı durumunu, veri indirme "
        "komutlarını, model varsayımlarını ve iki dilli (Türkçe/İngilizce) terimler sözlüğünü içerir."
    )

    if os.path.exists(IMG_11):
        pdf.figure(IMG_11, "Karne Sayfası: Resmi Tek Sayfalık Çiftçi Risk ve Su Karnesi Önizleme Ekranı", max_h=55, max_w=165)
    if os.path.exists(IMG_13):
        pdf.figure(IMG_13, "Yöntem ve Veriler Sayfası: 8/8 Gerçek NASA Verisi Doğrulama Tablosu ve Sözlük", max_h=55, max_w=165)


def build_chapter_09(pdf):
    pdf.chapter_header(
        "09",
        "Adım Adım Kullanım: 3 Senaryo",
        "Uygulamayı ilk kez açan birinin izleyebileceği üç gerçekçi kullanım senaryosu."
    )
    
    pdf.section_header("Senaryo A · Çumra'da Mısır-Pancar Eken Mehmet Amca")
    pdf.body_p(
        "Mehmet Amca, Çumra havzasında 100 dekarlık sulu arazisinde yıllardır alışkanlıkla iki yıl dane mısır, iki yıl şeker pancarı ekmektedir. "
        "Kuyu derinliği 80 metreye inmiş, elektrik faturaları katlanmış ve Eylül 2026 kararnamesiyle mısırına su kısıtı desteği sıfırlanmıştır."
    )
    pdf.bullet("Adım 1:", "Uygulama açılır, Tarla sayfasında 'Örnek tarlayı yükle: Mehmet Amca, Çumra' sarı butonuna tıklanır. Tüm veriler yüklenir.")
    pdf.bullet("Adım 2:", "Doğrudan 'Planlar' sayfasına geçilir. Mevcut planının üzerinde büyük kırmızı 'Kırmızı Kart (ÇKS Destek İhlali)' uyarısını görür.")
    pdf.bullet("Adım 3:", "Hemen yanındaki yeşil 'Denge Kartı'na bakar: 1. Yıl Fiğ, 2. Yıl Buğday, 3. Yıl Nohut, 4. Yıl Ayçiçeği. 4 yılda kuyusundan "
               "1.600 ton daha az su çekeceğini ve tam 4.108 ₺/da devlet desteği kazanacağını hesaplar.")
    pdf.bullet("Adım 4:", "'Karne' sayfasına geçer, 'Mehmet Yılmaz - Çumra Parsel 104' yazarak resmi Risk ve Su Karnesini PDF olarak indirir ve "
               "Ziraat Bankası'na düşük faizli sulama kredisi için başvurur.")
               
    pdf.section_header("Senaryo B · Kendi Tarlasını Giren Karapınar Çiftçisi")
    pdf.body_p(
        "Karapınar'da obruk riski yüksek bölgede kumlu-tınlı toprağı olan bir üretici, kendi parsel koordinatını girer (37.71° K, 33.55° D). "
        "Toprak analizi SoilGrids'ten otomatik çekilir; kuyu debisinin düşük olduğunu (15 m³/saat) belirtir."
    )
    pdf.bullet("Adım 1:", "Kendi koordinatını girip kuyu debisini ve salma sulamadan damla sulamaya geçiş opsiyonunu işaretler.")
    pdf.bullet("Adım 2:", "'İklim Geçmişi'nde bölgenin Temmuz ayında ortalama 14 gün >35°C sıcaklık stresine maruz kaldığını görür.")
    pdf.bullet("Adım 3:", "Planlar sayfasında sistem ona sıcağa ve kireçli toprağa çok dayanıklı olan Aspir ve Nohut ağırlıklı Akifer Kartını önerir. "
               "Sıfır kuyu riskiyle net gelirini garanti altına alır.")

    pdf.section_header("Senaryo C · 'Ya İklim Değişirse?': 2040 Projeksiyonu")
    pdf.body_p(
        "Tarım Kredi Kooperatifi uzmanı, sol kenar çubuğundan 'Ya şöyle olursa?' ayarını açar ve iklimi 'NASA CMIP6 SSP5-8.5 (Aşırı Kuraklık)' "
        "moduna alır (+2.5°C sıcaklık artışı, %20 yağış azalışı). Sistem saniyeler içinde 20.736 planı 2040 ikliminde yeniden sınar; "
        "şeker pancarının kuraklık stresinden dolayı zarar ettiğini, ayçiçeği ve arpa rotasyonunun ise dimdik ayakta kaldığını jüriye gösterir."
    )


def build_chapter_10(pdf):
    pdf.chapter_header(
        "10",
        "Kodun Yapısı ve Mimarisi",
        "Kodu okumadan veya katkı vermeden önce bilinmesi gereken modüler yazılım mimarisi ve test güvencesi."
    )
    
    pdf.section_header("Modüler Klasör Mimarisi")
    pdf.body_p(
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
        ["data/konya/...", "Veri Deposu", "NASA POWER, GPM, GRACE, SMAP, SRTM, CMIP6 ve SoilGrids NetCDF / CSV dosyaları."],
        ["tests/test_*.py", "Kalite Güvencesi", "63 adet tam kapsamlı otomatik birim ve entegrasyon testi (Pytest)."]
    ]
    pdf.table(headers, rows, [45, 30, 103], ["L", "L", "L"])
    
    pdf.section_header("63 Adet Otomatik Pytest Birim Testi")
    pdf.body_p(
        "Projenin güvenilirliği, 63 adet bağımsız test senaryosu ile teminat altındadır. Testler çekirdek motorun (FAO-56, Ky, kurallar, "
        "Pareto, 2026 destek katsayıları, küresel emtia tabloları) hatasız çalıştığını doğrular. Komut satırından `.venv\\Scripts\\python.exe -m pytest -q` "
        "çalıştırıldığında 63 testin tamamı saniyeler içinde yeşil geçer (63 passed)."
    )


def build_chapter_11(pdf):
    pdf.chapter_header(
        "11",
        "Kurulum, Çalıştırma ve Gerçek Veri İndirme",
        "Sıfır bir bilgisayardan çalışan uygulamaya ve canlı NASA verisi boru hattına adım adım geçiş rehberi."
    )
    
    pdf.section_header("Sistem Gereksinimleri ve Hızlı Kurulum")
    pdf.body_p(
        "Gerekenler: Python 3.11 veya üstü, Git, internet bağlantısı (yalnızca ilk kurulum ve canlı veri indirme için)."
    )
    
    pdf.callout(
        "KONSOL KURULUM KOMUTLARI (WINDOWS POWERSHELL / BASH)",
        "# 1. Proje dizinine gidin\n"
        "cd c:\\Users\\yunus\\Desktop\\spaceapps\\basinshift\n\n"
        "# 2. Sanal ortamı oluşturun ve aktif edin\n"
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate   # Linux/macOS: source .venv/bin/activate\n\n"
        "# 3. Bağımlılıkları yükleyin\n"
        "pip install -r requirements.txt\n\n"
        "# 4. Uygulamayı başlatın\n"
        "streamlit run app.py",
        "info"
    )
    
    pdf.section_header("Canlı NASA ve Global Verileri İndirme Boru Hattı")
    pdf.body_p(
        "Proje dizininde yer alan `veri_indir.bat` veya `scripts/setup_real_data.py` betiği, tüm veri setlerini doğrudan resmi kaynaklardan "
        "çekip `data/konya/` klasörüne yerleştirir:"
    )
    pdf.bullet("NASA POWER API:", "1981–2025 günlük iklim verilerini REST endpoint'inden çeker, QA/QC kontrolünden geçirir.")
    pdf.bullet("NASA GPM & GRACE:", "Aylık yağış ve yeraltı suyu anomali NetCDF dosyalarını indirip doğrular.")
    pdf.bullet("ISRIC SoilGrids & SRTM:", "Parsel bazlı toprak katmanları ve 30m yükseklik modelini çeker.")
