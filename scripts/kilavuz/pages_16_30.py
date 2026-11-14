"""
BasinShift Kılavuzu: Sayfa 16 - 30
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

IMG_DIR = r"c:\Users\yunus\Desktop\spaceapps\pdf_extracted_images"
MEVCUT_DIR = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler"

IMG_RISK = os.path.join(IMG_DIR, "page_18_1_X95.png")
IMG_PARETO = os.path.join(IMG_DIR, "page_18_2_X96.png")
IMG_TARLA_1 = os.path.join(MEVCUT_DIR, "01_tarla_girisi_ve_yapilandirma.png")
IMG_TARLA_2 = os.path.join(MEVCUT_DIR, "02_tarla_veri_kaynaklari_paneli.png")
IMG_IKLIM_1 = os.path.join(MEVCUT_DIR, "03_iklim_gecmisi_ve_risk_analizi.png")


def render_pages_16_30(pdf):
    # =========================================================================
    # SAYFA 16: BÖLÜM 04 - 4.5 UYDU VE İKLİM VERİSİ: ÇÖZÜNÜRLÜK PİRAMİDİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.5 Uydu Çözünürlük Piramidi")
    pdf.section_title("4.5 Uydu ve İklim Verisi Kavramları: Çözünürlük Piramidi")
    pdf.body(
        "Tek bir tarla meteoroloji istasyonu sadece birkaç yüz metrelik mikro alanı temsil eder ve sensör kalibrasyonu bozulabilir. "
        "Buna karşılık NASA uydu filosu, Dünya'yı farklı mekansal ve zamansal çözünürlüklerde sürekli tarar. BasinShift, "
        "çözünürlük piramidini doğru basamaklarda birleştirir:"
    )
    pdf.bullet("30 Metre (Parsel Ölçeği):", "SRTM v3 Sayısal Yükseklik Modeli (parsel eğimi ve yüzey akışı) ve Harmonized Landsat-Sentinel (HLS) 30m NDVI.")
    pdf.bullet("250 Metre (Toprak Katmanları):", "ISRIC SoilGrids toprak profili (kil, kum, silt, organik madde, hacim ağırlığı, TAW su kapasitesi).")
    pdf.bullet("10 Kilometre (Yağış ve Nem):", "NASA GPM IMERG 0.1° x 0.1° radar yağışı ve NASA SMAP 9-36 km kök bölgesi toprak nemi.")
    pdf.bullet("50 Kilometre (Atmosferik İklim):", "NASA POWER Agroclimatology 0.5° x 0.625° günlük güneş radyasyonu, nem, sıcaklık ve rüzgar serileri.")
    pdf.bullet("300 Kilometre (Akifer Kütlesi):", "NASA/DLR GRACE ve GRACE-FO Tellus Mascon yeraltı suyu gravitasyonel anomali ölçümü.")
    
    pdf.callout(
        "NEDEN UYDU VERİSİ YEREL İSTASYONDAN DAHA GÜVENİLİRDİR?",
        "İklim, bölge ölçeğinde homojen bir yapı gösterir; 30 km yarıçapında güneş radyasyonu ve sıcaklık rejimleri birbirine çok yakındır. "
        "Yerel meteoroloji istasyonları ise genellikle binaların, ağaçların gölgesinde kalabilir veya bakım eksikliğinden hatalı ölçebilir. "
        "NASA POWER uydusu 44 yıllık kesintisiz, boşluksuz ve homojen veri sağlar.",
        "info"
    )

    # =========================================================================
    # SAYFA 17: BÖLÜM 04 - 4.5 UYDULARIN TEKNİK ROLLERİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.5 Uyduların Teknik Rolleri")
    pdf.section_title("NASA Uydularının Sistemdeki Spesifik Görevleri")
    pdf.body(
        "BasinShift motorunda her NASA uydusunun matematikteki yeri kesin olarak tanımlanmıştır:"
    )
    
    headers = ["Uydu / Sensör", "Mekansal Çözünürlük", "Zaman Aralığı", "Modeldeki Matematiksel Rolü"]
    rows = [
        ["NASA POWER", "0,5° x 0,625° (~50 km)", "1981–2025 (Günlük)", "FAO-56 Penman-Monteith ET0, don/sıcaklık stres günleri, kayan pencere stres testi."],
        ["NASA GPM IMERG", "0,1° x 0,1° (~10 km)", "2000–2025 (Günlük/Aylık)", "Toprak su bütçesinde efektif yağış (P_eff) girdisi ve aşırı sağanak yüzey akışı denetimi."],
        ["NASA SMAP", "9 km / 36 km", "2015–2025 (Günlük)", "Simülasyonun ekim anındaki kök bölgesi başlangıç nemi ve kış çıkışı toprak su rezervi."],
        ["NASA SRTM v3", "30 m (1 arc-sec)", "Statik Küresel DEM", "Parsel topoğrafik eğimi; eğimli arazilerde suyun yüzey akışıyla kaçma fraksiyonu."],
        ["NASA/USGS HLS", "30 m (Harmonized)", "2013–2025 (5 Günlük)", "Bitki örtüsü yeşillenme takvimi, geçmiş Kc eğrilerinin fenolojiyle doğrulanması."],
        ["NASA GRACE / FO", "1° Mascon (~100-300 km)", "2002–2024 (Aylık)", "Havza yeraltı suyu su deposu değişimi; -1,3 cm/yıl akifer tükeniş trendi."],
        ["NEX-GDDP-CMIP6", "0,25° x 0,25° (~25 km)", "2030–2050 (Projeksiyon)", "2040 iklim senaryoları (SSP2-4.5 ve SSP5-8.5) stres testi simülasyonları."]
    ]
    pdf.table(headers, rows, [32, 38, 38, 70], ["L", "L", "L", "L"])
    
    pdf.body(
        "Bu uyduların birleşimi; tarlanın mikro topoğrafyasından (SRTM) atmosferik iklimine (POWER) ve derin akiferine (GRACE) kadar "
        "tam ölçekli bir dijital ikiz yaratmaktadır."
    )

    # =========================================================================
    # SAYFA 18: BÖLÜM 04 - 4.6 RİSK VE KARAR: CVAR VE PARETO SINIRI
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.6 Risk ve Çok Boyutlu Karar")
    pdf.section_title("4.6 Risk ve Karar: Kötü Dönem Geliri (CVaR) ve Pareto Sınırı")
    pdf.body(
        "Tarımsal karar vermede yalnızca ortalama getiriye bakmak ölümcül bir hatadır. Bir plan ortalama bir yılda yüksek kâr getirebilir "
        "ancak 4 yılda bir gelen şiddetli kuraklıkta çiftçiyi iflasa sürükleyebilir. BasinShift, finans mühendisliğinden uyarlanan iki metrik kullanır:"
    )
    pdf.bullet("Kötü Dönem Geliri (CVaR - Conditional Value at Risk):", "Bir planın 44 yıllık geçmişteki en kötü %5'lik döneminde (yani "
               "en yıkıcı 2 kuraklık penceresinde) elde ettiği ortalama yıllık brüt kârdır. Çiftçinin iflas etmeme garantisidir.")
    pdf.bullet("3 Boyutlu Pareto Etkinlik Sınırı:", "Kârı maksimize eden, su tüketimini minimize eden ve kuraklık riskini düşüren "
               "en üstün planlar kümesidir. Başka bir plana göre hem daha az kazandıran hem daha çok su harcayan tüm zayıf planlar elenir.")
               
    if os.path.exists(IMG_RISK):
        pdf.figure(IMG_RISK, "Risk Dağılımı (CVaR): Alışılmış Planın Sol Kuyruk Çöküşü vs Denge Kartının Güvenli Getirisi", max_h=35, max_w=145)
    if os.path.exists(IMG_PARETO):
        pdf.figure(IMG_PARETO, "Çok Kriterli Pareto Etkinlik Sınırı: Kâr, Su Tüketimi ve Risk Dengesi", max_h=35, max_w=145)

    # =========================================================================
    # SAYFA 19: BÖLÜM 04 - 4.6 KOORDİNASYON VE GÖLGE FİYAT
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.6 Koordinasyon ve Gölge Fiyat")
    pdf.section_title("Ortak Kaynak, Koordinasyon ve Suyun Gölge Fiyatı")
    pdf.body(
        "Akifer, havzadaki 100.000 çiftçinin ortak kullandığı devasa bir yeraltı su havuzudur. Çiftçiler arasında koordinasyon "
        "olmadığında ortaya çıkan ekonomik kayıplar iki temel kavramla ölçülür:"
    )
    pdf.bullet("Koordinasyonsuzluğun Maliyeti (Price of Anarchy):", "Her çiftçi sadece geçen yılın piyasa fiyatına bakarak tek başına "
               "aşırı su isteyen mısır ve pancar ektiğinde, koordineli ve dengeli bir plana kıyasla havza dekarda yılda ortalama 929 ₺ kazanç "
               "ve 149 m³ su kaybetmektedir. Bu, plansızlığın ve koordinasyonsuzluğun havzaya kestiği somut faturadır.")
               
    pdf.bullet("Suyun Gölge Fiyatı (Shadow Price of Water):", "Doğrusal programlama (LP) modelinde su kısıtına 1 m³ ilave su eklendiğinde "
               "havzanın toplam ekonomik kârının ne kadar artacağını gösteren marjinal değerdir. Konya havzasında bu değer 8,39 ₺/m³'tür. "
               "Yani modern damla sulama veya ürün değişimi ile kurtarılan her 1 metreküp su, bölge ekonomisine net 8,39 ₺ kazandırmaktadır.")
               
    pdf.callout(
        "YATIRIM KARARLARINDA GÖLGE FİYATIN KULLANIMI",
        "Bir sulama kooperatifi veya DSİ kanalı kapalı borulu sisteme çevirmek istediğinde yatırım maliyetini suyun gölge fiyatıyla kıyaslar. "
        "Eğer 1 m³ su tasarrufunun yatırım maliyeti 8,39 ₺'nin altındaysa o proje kamu yararına ve ekonomiye doğrudan kârlıdır.",
        "verified"
    )

    # =========================================================================
    # SAYFA 20: BÖLÜM 05 - ÇÖZÜM: İLKE 1 VE İLKE 2
    # =========================================================================
    pdf.add_exact_page("Bölüm 05 · Çözüm: İlke 1 ve 2")
    pdf.chapter_title(
        "05",
        "Çözüm: BasinShift'in Dört Fikri",
        "Kavramlar yerine oturduktan sonra BasinShift'in sunduğu çözüm dört sarsılmaz bilimsel ilkeye dayanır."
    )
    
    pdf.section_title("İlke 1 · Planı 40 Yılın Gerçek Havasıyla Sına")
    pdf.body(
        "Mevcut tarım danışmanlığı araçları 'varsayımsal ortalama bir yıl' için tavsiye verir. Oysa Konya'da ortalama bir yıl yoktur; "
        "bir yıl aşırı kurak, ertesi yıl donlu, üçüncü yıl ise aşırı yağışlı geçer. BasinShift, çiftçinin aklındaki 4 yıllık planı "
        "1981–2025 arasındaki 44 yıllık gerçek meteorolojik koşullarda kayan pencerelerle (1982–1985, 1983–1986, ..., 2022–2025 olmak üzere "
        "tam 41 bağımsız dönemde) sınar. Plan, geçmişin en zorlu kuraklıklarında batmışsa elenir."
    )
    
    pdf.section_title("İlke 2 · Kurallara ve Çiftçi Kısıtlarına Uyan En İyilerini Bul")
    pdf.body(
        "12 ürünün 4 yıllık kombinasyonu olan 20.736 olası plan arasından önce çiftçinin tarlaya özel kısıtları (su kotası, kuyu debisi, "
        "makine parkuru, yem ihtiyacı, sözleşmeli ekim kotası) ve 2026 Tarımsal Destekleme Kararnamesi kuralları (su kısıtı ve rotasyon "
        "yasakları) filtrelenir. Sarı veya kırmızı kart alan tüm planlar çöpe atılır. Kalan binlerce geçerli plan arasından Pareto Sınırı "
        "çizilerek çiftçiye üç net alternatif sunulur: Denge, Kâr ve Akifer."
    )

    # =========================================================================
    # SAYFA 21: BÖLÜM 05 - ÇÖZÜM: İLKE 3 VE İLKE 4
    # =========================================================================
    pdf.add_exact_page("Bölüm 05 · Çözüm: İlke 3 ve 4")
    pdf.section_title("İlke 3 · Nedenini ve Gerekçesini Şeffafça Açıkla")
    pdf.body(
        "Çiftçiye 'Git şunu ek' demek ikna edici değildir. Çiftçi neden o ürünün seçildiğini, bir önceki yılın toprağa etkisini, "
        "hangi ayda ne kadar su harcayacağını ve ne kadar devlet desteği alacağını bilmek ister. BasinShift, kara kutu bir yapay zekâ "
        "modeli (halüsinasyon riski olan LLM'ler) kullanmaz. Tüm açıklamalar, FAO-56 su dengesi ve resmi destek katsayılarından doğrudan "
        "türetilen deterministik agronomik şablonlarla üretilir. Verilen hiçbir rakam uydurma olamaz."
    )
    
    pdf.section_title("İlke 4 · Tarladan Havzaya ve Küresel Pazara Bağla")
    pdf.body(
        "Tek bir tarla kendi başına sürdürülebilir görünse bile, havzadaki 100.000 çiftçi aynı anda aşırı su çekerse akifer çöker; ya da herkes "
        "aynı ürünü ekerse ürün arz fazlasından tarlada kalır ve fiyatlar taban yapar. BasinShift, tarladaki her kararı havza hidrolojisiyle "
        "(GRACE su kütlesi kaybı ve obruk riski) ve küresel emtia dengesiyle (CBOT/Euronext fiyatları ve sanal su ihracatı) ilişkilendirir."
    )
    
    pdf.callout(
        "DÖRT İLKENİN SENTEZİ",
        "BasinShift; çiftçiye güvenli gelir, toprağa organik canlılık, akifere sürdürülebilir su ve devlete gıda arz güvenliği "
        "sağlayan bütüncül bir ekosistem inşa etmektedir.",
        "verified"
    )

    # =========================================================================
    # SAYFA 22: BÖLÜM 06 - VERİLER: NE, NEREDEN, NEREDE? (8/8 TABLO)
    # =========================================================================
    pdf.add_exact_page("Bölüm 06 · Veriler: Ne, Nereden, Nerede?")
    pdf.chapter_title(
        "06",
        "Veriler: Ne, Nereden, Nerede?",
        "Jürinin ve bilim insanlarının ilk sorusu: 'Hangi NASA verisini nereden çektiniz, nasıl işlediniz?'. Cevabın tamamı bu tablodur."
    )
    
    headers = ["Veri Seti Kodu", "Uydu / Görev / Sağlayıcı", "Çözünürlük & Kapsam", "Hesapta Nerede Kullanılıyor?", "Erişim Metodu & Doğrulama"]
    rows = [
        ["climate_daily", "NASA POWER (Agroclimatology API)", "0,5° x 0,625°; 1981–2025 (44 Yıl)", "FAO-56 ET0, günlük su dengesi, don/sıcaklık stresi, risk takvimi", "[OK] Canlı REST API / NetCDF"],
        ["precipitation", "NASA GPM IMERG v07 (GPM_3IMERGM)", "0,1° x 0,1°; Aylık & Günlük", "Yağış doğrulaması, kuraklık indeksleri, efektif yağış hesabı", "[OK] GES DISC API / HDF5"],
        ["groundwater", "NASA/DLR GRACE & GRACE-FO Tellus", "1° Mascon (JPL / CSR); 2002–2024", "Havza yeraltı suyu kütle anomalisi, akifer düşüş eğilimi (-1,3 cm/yıl)", "[OK] PO.DAAC / NetCDF"],
        ["soil_moisture", "NASA SMAP L3/L4 Radyometre", "9 km / 36 km; 2015–2025", "Kök bölgesi toprak nemi, su dengesi başlangıç koşulları", "[OK] NSIDC DAAC (Doğrulandı)"],
        ["terrain_elev", "NASA SRTM v3 (Shuttle Radar Topo)", "30 m (1 arc-sec); Küresel", "Parsel eğimi, yüzey akışı katsayısı, erozyon riski", "[OK] USGS EarthExplorer / GeoTIFF"],
        ["vegetation_ndvi", "NASA/USGS HLS (Landsat-Sentinel)", "30 m; 5 Günlük Sıklık", "Bitki örtüsü dinamikleri, geçmiş fenoloji doğrulama, Kc eğrisi", "[OK] LP DAAC AppEEARS"],
        ["climate_proj", "NASA NEX-GDDP-CMIP6", "0,25° x 0,25°; 2030–2050 (SSP2/5)", "'İki Gelecek' ve '2040 İklim Senaryoları' stres testi", "[OK] Center for Climate Simulation"],
        ["soil_profile", "ISRIC SoilGrids 250m (Global Soil)", "250 m; 6 Derinlik Katmanı (0-200 cm)", "Toprak bünyesi (kil, kum), TAW, RAW, tarla kapasitesi ve solma noktası", "[OK] ISRIC WCS / REST API"]
    ]
    pdf.table(headers, rows, [28, 42, 32, 44, 32], ["L", "L", "L", "L", "L"])
    
    pdf.body(
        "Yukarıdaki 8 veri setinin tamamı projenin `data/konya/` dizininde doğrulanmış netcdf ve csv dosyaları olarak mevcuttur."
    )

    # =========================================================================
    # SAYFA 23: BÖLÜM 06 - SENTETİK VERİ DÖNEMİ BİTTİ & QA/QC
    # =========================================================================
    pdf.add_exact_page("Bölüm 06 · Canlı Doğrulama ve QA/QC")
    pdf.section_title("Sentetik Veri Dönemi Bitti: %100 Canlı Doğrulama")
    pdf.body(
        "Projenin ilk geliştirme aşamasında kullanılan geçici sentetik veriler tamamen devre dışı bırakılmıştır. "
        "Artık uygulamanın 'Yöntem ve Veriler' sekmesindeki doğrulama tablosunda her bir veri kaynağı için yeşil onay etiketi "
        "görüntülenmektedir. Jüri veya kullanıcı dilerse `veri_indir.bat` ile verileri yeniden resmi NASA sunucularından çekebilir."
    )
    
    pdf.section_title("Veri Kalitesi ve QA/QC Filtreleme Protokolü")
    pdf.body(
        "Ham uydu verilerinde sensör kalibrasyonu veya bulut örtüsü nedeniyle yaşanabilecek anomalilere karşı katı bir QA/QC filtresi uygulanır:"
    )
    pdf.bullet("Eksik Gün Tamamlama (Gap-Filling):", "NASA POWER günlük serisinde herhangi bir yılda eksik gün oranı %5'in altındaysa "
               "yakındaki komşu günlerin lineer interpolasyonu ile tamamlanır; eksik gün %5'i aşıyorsa o yıl hesaptan tamamen çıkartılır.")
    pdf.bullet("Rüzgar Hızı Yükseklik Düzeltmesi:", "Farklı sensörlerin 10 metrede ölçtüğü rüzgar hızları, FAO-56 logaritmik rüzgar profili "
               "denklemiyle [u2 = u10 * 4.87 / ln(67.8 * 10 - 5.42)] standart 2 metre yüksekliğine dönüştürülür.")
    pdf.bullet("Yağış Kalibrasyonu:", "GPM IMERG uydu yağış verileri, yerel meteoroloji istasyonu doğrulamalarıyla çarpraz kontrol edilir; "
               "aşırı yağış anomalileri yüzey akış katsayısıyla filtrelenir.")

    # =========================================================================
    # SAYFA 24: BÖLÜM 07 - HESAP NASIL YAPILIYOR? (ADIM 1 - 4)
    # =========================================================================
    pdf.add_exact_page("Bölüm 07 · Hesap Adımları 1 - 4")
    pdf.chapter_title(
        "07",
        "Hesap Nasıl Yapılıyor?",
        "Ham NASA uydusundan tarladaki karar kartına giden yol: 11 adımlı matematiksel modelleme hattı."
    )
    
    pdf.section_title("Model Boru Hattı: Adım 1'den 4'e")
    pdf.bullet("Adım 1 · Coğrafi Konum ve Parsel Toprak Profili:", "Parselin koordinatları alınır. SoilGrids 250m veri tabanından "
               "6 katmanlı toprak analizi (kil, kum, silt, organik karbon) ve SRTM'den 30m eğim çekilir. Toprağın TAW ve RAW su kapasitesi "
               "parsel bazında milimetrik olarak hesaplanır.")
               
    pdf.bullet("Adım 2 · Günlük FAO-56 Penman-Monteith ET0:", "NASA POWER'dan 1981–2025 arasındaki 16.000+ gün için sıcaklık, radyasyon, "
               "bağıl nem ve rüzgar çekilerek her bir günün referans buharlaşması (ET0, mm/gün) Penman-Monteith eşitliğiyle fiziksel olarak hesaplanır.")
               
    pdf.bullet("Adım 3 · Günlük Toprak Su Dengesi Simülasyonu:", "Her ürün için fenolojik büyüme takvimine göre günlük Kc katsayısı belirlenir. "
               "Topraktaki su bütçesi gün gün işletilir: Giriş = Yağış + Sulama; Çıkış = ETc + Derine Sızma + Yüzey Akışı. RAW'ın altına inilen "
               "günler 'su stresi' olarak kaydedilir.")
               
    pdf.bullet("Adım 4 · 12 Ürün x 44 Yıl Ürün-Yıl Matrisi:", "Konya havzasındaki 12 ürün, 1982–2025 arasındaki 44 hasat yılının her birinde "
               "tek tek ekilmiş gibi simüle edilir (12 x 44 = 528 durum). Her durum için verim, gereken sulama suyu, iklim stresi kaybı, "
               "maliyet ve brüt gelir tek bir ana matriste toplanır. Bu matris hesaplamayı 0,2 saniyeye indirir.")

    # =========================================================================
    # SAYFA 25: BÖLÜM 07 - HESAP NASIL YAPILIYOR? (ADIM 5 - 7)
    # =========================================================================
    pdf.add_exact_page("Bölüm 07 · Hesap Adımları 5 - 7")
    pdf.section_title("Model Boru Hattı: Adım 5'ten 7'ye")
    pdf.bullet("Adım 5 · 4 Yıllık Rotasyon Penceresi Stres Testi:", "12 ürünün tüm 4 yıllık kombinasyonları (12^4 = 20.736 plan), "
               "tarihteki 41 adet 4 yıllık pencerede (1982-1985, 1983-1986, ..., 2022-2025) geriye dönük oynatılır. Her plan için 41 farklı "
               "4 yıllık ekonomik ve hidrolojik sonuç üretilir. Böylece planın ortalama performansı ve kurak yıllardaki çöküş riski belirlenir.")
               
    pdf.bullet("Adım 6 · Yasal ve Çiftçi Kısıt Süzgeci:", "20.736 plan içinden; kuyu debisini aşan, çiftçinin 'ekmem' dediği ürünleri içeren, "
               "yem ihtiyacını karşılamayan ve Eylül 2026 su kısıtı kurallarını ihlal eden (sarı veya kırmızı kart alan) tüm planlar otomatik olarak elenir.")
               
    pdf.bullet("Adım 7 · 3 Boyutlu Pareto Optimizasyonu:", "Kural süzgecinden geçen geçerli planlar 3 boyutlu uzayda sıralanır:\n"
               "1) Ortalama Yıllık Brüt Kâr (Maksimum Kazanç)\n"
               "2) Yıllık Çekilen Sulama Suyu (Minimum Su Harcaması)\n"
               "3) Kötü Dönem Geliri CVaR (Maksimum Kuraklık Dayanıklılığı)\n"
               "Baskın olmayan (non-dominated) optimal çözümler kümesi Pareto Sınırı olarak çıkarılır.")

    # =========================================================================
    # SAYFA 26: BÖLÜM 07 - HESAP NASIL YAPILIYOR? (ADIM 8 - 11)
    # =========================================================================
    pdf.add_exact_page("Bölüm 07 · Hesap Adımları 8 - 11")
    pdf.section_title("Model Boru Hattı: Adım 8'den 11'e")
    pdf.bullet("Adım 8 · Üç Stratejik Kartın Belirlenmesi:", "Pareto sınırındaki yüzlerce plan arasından çiftçiye üç net kart sunulur:\n"
               "• Denge Kartı: Kâr / Risk oranını (Sharpe oranı) maksimize eden en dengeli plan.\n"
               "• Kâr Kartı: Kural ihlali yapmadan en yüksek parayı kazandıran plan.\n"
               "• Akifer Kartı: En az su harcayan ve yeraltı suyunu koruyan sürdürülebilir plan.")
               
    pdf.bullet("Adım 9 · Deterministik Gerekçe ve Neden Açıklaması:", "Seçilen kartlar için doğal dilde şablon motoru çalışır. 'Neden bu plan?' sorusuna; "
               "kurtarılan su miktarı, ön bitkinin azot katkısı, kazanılan devlet desteği ve kuraklık dayanıklılığı rakamlarla tek tek yazılır.")
               
    pdf.bullet("Adım 10 · Çıktıların Üretilmesi ve Raporlama:", "Streamlit UI ekranları dinamik olarak güncellenir; karşılaştırma tabloları, interaktif "
               "Plotly saçılım grafikleri çizilir ve tek tıklamayla resmi 'Risk ve Su Karnesi' PDF belgesi oluşturulur.")
               
    pdf.bullet("Adım 11 · Havza Ölçeği Entegrasyonu (LP & Nash Dengesi):", "Tarladaki kararlar havza geneline ölçeklenir. GRACE yeraltı suyu kaybı, "
               "havza koordinasyon kazancı (Price of Anarchy), suyun gölge fiyatı (Shadow Price) ve küresel emtia paritesi raporlanır.")

    # =========================================================================
    # SAYFA 27: BÖLÜM 08 - ARAYÜZ TURU: GENEL VE KENAR ÇUBUĞU
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · Arayüz Turu: Kenar Çubuğu")
    pdf.chapter_title(
        "08",
        "Arayüz Turu: Her Ekran, Her Grafik",
        "Resmi NASA Space Apps 2026 koyu tasarım temasıyla güncellenen arayüzün tüm bileşenleri ve görsel rehberi."
    )
    
    pdf.section_title("8.1 Kenar Çubuğu (Sidebar): Genel Kontroller")
    pdf.body(
        "Kenar çubuğu, uygulamanın hangi sayfasına gidilirse gidilsin sol tarafta sabit kalan kontrol merkezidir:"
    )
    pdf.bullet("Resmi NASA Space Apps 2026 Logosu:", "En üstte yer alır; organizasyon kimliğini doğrular.")
    pdf.bullet("Havza Seçimi:", "Konya Kapalı Havzası (Türkiye), Pencap (Hindistan), California Central Valley (ABD).")
    pdf.bullet("Dil Seçimi (TR / EN):", "Tek tıkla tüm arayüz, tablolar, grafikler ve terimler Türkçe veya İngilizceye döner.")
    pdf.bullet("Birim Seçimi (da / ha):", "Türkiye için dekar (da), uluslararası kullanıcılar için hektar (ha) bazlı hesaplama.")
    pdf.bullet("İklim Değişimi Simülatörü ('Ya şöyle olursa?'):", "2040 SSP2-4.5 (Orta İklim) ve SSP5-8.5 (Aşırı Kuraklık) senaryoları.")

    # =========================================================================
    # SAYFA 28: BÖLÜM 08 - 8.2 TARLA SAYFASI: ÜST KISIM
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.2 Tarla Sayfası (Üst Kısım)")
    pdf.section_title("8.2 Tarla Sayfası: Coğrafi Konum ve Toprak Profili")
    pdf.body(
        "Tarla sayfası, analizin başladığı ilk ekrandır. Çiftçi veya danışman tarlanın temel parametrelerini burada belirler:"
    )
    pdf.bullet("Hazır Demo Yükleme Butonu ('Örnek tarlayı yükle: Mehmet Amca, Çumra'):", "Tek tıkla Çumra havzasındaki gerçek bir parselin "
               "koordinatını, tınlı-killi toprak yapısını, 80m derin kuyu bilgisini ve alışılagelmiş 4 yıllık mısır-pancar ekim planını yükler.")
    pdf.bullet("Harita ve Koordinat Seçimi:", "Kullanıcı harita üzerinden parselini işaretleyebilir; enlem ve boylam otomatik okunur.")
    
    if os.path.exists(IMG_TARLA_1):
        pdf.figure(IMG_TARLA_1, "Tarla Sayfası Üst Kısım: Mehmet Amca Örneği, Koordinat ve Toprak Yapısı", max_h=58, max_w=165)

    # =========================================================================
    # SAYFA 29: BÖLÜM 08 - 8.2 TARLA SAYFASI: ALT KISIM
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.2 Tarla Sayfası (Alt Kısım)")
    pdf.section_title("8.2 Tarla Sayfası: Sulama Altyapısı ve Mevcut Plan")
    pdf.body(
        "Tarla sayfasının orta ve alt bölümünde sulama koşulları ve mevcut alışkanlıklar tanımlanır:"
    )
    pdf.bullet("Statik Su Seviyesi (m):", "Kuyudaki suyun derinliğidir; elektrik maliyeti bu derinliğe göre dinamik hesaplanır.")
    pdf.bullet("Sulama Yöntemi:", "Damla (%90), Yağmurlama (%75), Salma (%50) seçenekleri; randıman katsayısını belirler.")
    pdf.bullet("Mevcut 4 Yıllık Plan:", "Çiftçinin son 4 yılda ektiği veya ekmeyi düşündüğü ürün sıralaması (ör. Mısır-Pancar-Mısır-Pancar).")
    
    if os.path.exists(IMG_TARLA_2):
        pdf.figure(IMG_TARLA_2, "Tarla Sayfası Alt Kısım: Sulama Altyapısı, Kuyu Debisi ve Veri Kaynakları Paneli", max_h=58, max_w=165)

    # =========================================================================
    # SAYFA 30: BÖLÜM 08 - 8.3 İKLİM GEÇMİŞİ: TRENDLER VE RİSK TAKVİMİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 08 · 8.3 İklim Geçmişi")
    pdf.section_title("8.3 İklim Geçmişi: 44 Yıllık NASA Karnesi ve Risk Takvimi")
    pdf.body(
        "İklim Geçmişi sayfası, NASA POWER Agroclimatology ve GPM IMERG verilerinden üretilen 1981–2025 tarihsel iklim analizidir:"
    )
    pdf.bullet("Yıllık Yağış ve Sıcaklık Anomalisi Grafiği:", "Son 44 yılın yağış dalgalanmalarını, kurak geçen yılları (ör. 2007, 2014, 2021) "
               "ve uzun dönemli ısınma trendini (+1.4°C artış) gösterir.")
    pdf.bullet("Aylık İklim Stres Takvimi (Heatmap):", "12 ay boyunca don riski günleri, aşırı sıcak gün sayısı (>35°C) ve hasat dönemi "
               "istenmeyen aşırı yağış frekansını matris formatında sergiler. Çiftçi hangi ayda bitkisinin ne tür risk altında olduğunu anlar.")

    if os.path.exists(IMG_IKLIM_1):
        pdf.figure(IMG_IKLIM_1, "İklim Geçmişi Sayfası: 44 Yıllık Yağış/Sıcaklık Grafiği ve Aylık İklim Stres Takvimi (Heatmap)", max_h=58, max_w=165)
